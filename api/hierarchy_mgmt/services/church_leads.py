from datetime import datetime
from typing import Annotated, Optional

from fastapi import HTTPException, status, Depends  # type: ignore
from sqlalchemy import text  # type: ignore
from sqlalchemy.orm import Session  # type: ignore

from ...hierarchy_mgmt.services.church import ChurchServices, get_church_services
from ...authentication.models.auth import User, UserAccess
from ...common.database import get_db
from ...common.dependencies import (
    get_current_user,
    get_current_user_access,
    set_db_current_user,
)
from ...common.utils import get_level_no, set_user_access


class ChurchLeadsServices:
    """
    #### Church Leads Service methods
    - Get Church Leads by Code
    - Unmap Church Leads by Code
    - Map Church Leads by Code
    - Get Churches by Lead Code
    """

    def __init__(
        self,
        db: Session,
        current_user: User,
        current_user_access: UserAccess,
        church_services: Annotated[ChurchServices, Depends(get_church_services)],
    ):
        self.db = db
        self.current_user = current_user
        self.current_user_access = current_user_access
        self.church_services = church_services

    async def get_church_leads_by_code(
        self, code: str, is_active: Optional[bool] = None
    ):
        try:
            # fetch church data
            church = await self.church_services.get_church_by_code(code)
            # check if church is active/approved
            if not church.Is_Active and church.Status != "APR":
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Church: {church.Name} is not active/approved.",
                )
            set_user_access(
                self.current_user_access,
                headchurch_code=self.current_user.HeadChurch_Code,
                # role_code=["ADM", "SAD"],
                # level_code=["CHU", "CL1"],
                module_code=["HRCH"],
                # submodule_code=["HEAD", "CL1"],
                access_type=["VW"],
            )
            church_leads = (
                self.db.execute(
                    text(
                        """
                    SELECT Church_Code, Level_Code, LeadChurch_Code, LeadChurch_Level, Is_Active, Start_Date, End_Date, HeadChurch_Code, Created_Date, Created_By, Modified_Date, Modified_By, `Status`, Status_By, Status_Date
                    FROM tblChurchLeads 
                    WHERE Code = :Code AND HeadChurch_Code = :HeadChurch_Code
                    ORDER BY Start_Date DESC;
                    """
                    ),
                    dict(Code=code, HeadChurch_Code=self.current_user.HeadChurch_Code),
                ).all()
                if is_active is None
                else self.db.execute(
                    text(
                        """
                    SELECT Church_Code, Level_Code, LeadChurch_Code, LeadChurch_Level, Is_Active, Start_Date, End_Date, HeadChurch_Code, Created_Date, Created_By, Modified_Date, Modified_By, `Status`, Status_By, Status_Date
                    FROM tblChurchLeads 
                    WHERE Code = :Code AND HeadChurch_Code = :HeadChurch_Code AND A.Is_Active = :Is_Active
                    ORDER BY Start_Date DESC;
                    """
                    ),
                    dict(
                        Code=code,
                        HeadChurch_Code=self.current_user.HeadChurch_Code,
                        Is_Active=is_active,
                    ),
                ).all()
            )
            return church_leads
        except Exception as err:
            raise err

    async def unmap_church_leads_by_code(self, church_code: str):
        try:
            # fetch church data
            church = await self.church_services.get_church_by_code(church_code)
            # check if church is active/approved
            if not church.Is_Active and church.Status != "APR":
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Church: {church.Name} is not active/approved.",
                )
            # get church level no
            level_no = get_level_no(
                church.Level_Code, self.current_user.HeadChurch_Code, self.db
            )
            # set user access
            set_user_access(
                self.current_user_access,
                headchurch_code=self.current_user.HeadChurch_Code,
                role_code=["ADM", "SAD"],
                # level_code=["CHU"],
                level_no=level_no - 1,
                module_code=["HRCH"],
                # submodule_code=["HEAD", "CL1"],
                access_type=["ED", "VW"],
            )
            # ummap church from any active church lead
            self.db.execute(
                text(
                    """
                    UPDATE tblChurches 
                    SET End_Date = :End_Date, Is_Active = :Is_Active, Modified_By = :Modified_By, Status = :Status, Status_By = :Status_By, Status_Date = :Status_Date 
                    WHERE Code = :Code AND End_Date IS NULL;
                    """
                ),
                dict(
                    End_Date=datetime.now(),
                    Is_Active=0,
                    Modified_By=self.current_user.Usercode,
                    Status="INA",
                    Status_By=self.current_user.Usercode,
                    Status_Date=datetime.now(),
                    Code=church_code,
                ),
            )
            self.db.commit()
            return await self.get_church_leads_by_code(church_code)
        except Exception as err:
            self.db.rollback()
            raise err

    async def map_church_lead_by_code(self, church_code: str, lead_church_code: str):
        try:
            # fetch church data
            church = await self.church_services.get_church_by_code(church_code)
            # fetch lead church data
            lead_church = await self.church_services.get_church_by_code(
                lead_church_code
            )
            # fetch church leads
            church_leads = await self.get_church_leads_by_code(church_code)
            # check if church is active/approved
            if not church.Is_Active and church.Status != "APR":
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Church: '{church.Name}' is not active/approved.",
                )
            # check if lead church is active/approved
            if not lead_church.Is_Active and lead_church.Status != "APR":
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Selected Lead Church: '{lead_church.Name}' is not active/approved.",
                )
            # check if church is already mapped to lead church
            for church_lead in church_leads:
                if (
                    church_lead.ChurchLevel_Code == lead_church.Code
                    and church_lead.Is_Active
                    and church_lead.Status == "APR"
                ):
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail=f"Church: '{church.Name}' is currently mapped to selected Lead Church: '{lead_church.Name}'.",
                    )
            # get church level no
            level_no = get_level_no(
                church.Level_Code, self.current_user.HeadChurch_Code, self.db
            )
            # set user access
            set_user_access(
                self.current_user_access,
                headchurch_code=self.current_user.HeadChurch_Code,
                role_code=["ADM", "SAD"],
                # level_code=["CHU"],
                level_no=level_no - 1,
                module_code=["HRCH"],
                # submodule_code=["HEAD", "CL1"],
                access_type=["ED"],
            )
            # unmap any current church leads
            await self.unmap_church_leads_by_code(
                church_code,
            )
            # assign church leads
            self.db.execute(
                text(
                    """
                    INSERT INTO tblChurchLeads
                        (Church_Code, Level_Code, LeadChurch_Code, LeadChurch_Level, Start_Date, HeadChurch_Code, Created_By)
                    VALUES 
                        (:Church_Code, :Level_Code, :LeadChurch_Code, :LeadChurch_Level, :Start_Date, :HeadChurch_Code, :Created_By);
                    """
                ),
                dict(
                    Church_Code=church.Code,
                    Level_Code=church.Level_Code,
                    LeadChurch_Code=lead_church.Code,
                    LeadChurch_Level=lead_church.Level_Code,
                    Start_Date=datetime.now(),
                    HeadChurch_Code=self.current_user.HeadChurch_Code,
                    Created_By=self.current_user.Usercode,
                ),
            )
            self.db.commit()
            new_church_lead = await self.db.execute(
                text("SELECT * FROM tblChurchLeads WHERE Id = LAST_INSERT_ID();")
            ).first()
            return new_church_lead
        except Exception as err:
            self.db.rollback()
            raise err

    async def approve_church_lead_by_code(self, church_code: str, leadchurch_code: str):
        try:
            # fetch church data
            church = await self.church_services.get_church_by_code(church_code)
            # fetch lead church data
            lead_church = await self.church_services.get_church_by_code(leadchurch_code)
            # fetch church leads
            church_leads = await self.get_church_leads_by_code(church_code)
            # check if church lead is active or already approved
            for church_lead in church_leads:
                if (
                    church_lead.ChurchLevel_Code == lead_church.Code
                    and church_lead.Is_Active
                    and church_lead.Status == "APR"
                ):
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail=f"Church Lead mapping is already approved.",
                    )
                elif (
                    church_lead.ChurchLevel_Code == lead_church.Code
                    and church_lead.Is_Active
                    and church_lead.Status != "APR"
                ):
                    break
            else:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Church Lead mapping is not active.",
                )
            # get church level no
            level_no = get_level_no(
                church.Level_Code, self.current_user.HeadChurch_Code, self.db
            )
            # set user access
            set_user_access(
                self.current_user_access,
                headchurch_code=self.current_user.HeadChurch_Code,
                role_code=["ADM", "SAD"],
                # level_code=["CHU"],
                level_no=level_no - 1,
                module_code=["HRCH"],
                # submodule_code=["HEAD", "CL1"],
                access_type=["ED"],
            )
            # approve church leads
            self.db.execute(
                text(
                    """
                    UPDATE tblChurchLeads
                    SET Status = :Status, Status_Date = :Status_Date, Status_By = :Status_By, Modified_By = :Modified_By
                    WHERE Church_Code = :Church_Code 
                    AND LeadChurch_Code = :LeadChurch_Code
                    AND HeadChurch_Code = :HeadChurch_Code
                    AND Is_Active = :Is_Active;
                    """
                ),
                dict(
                    Status="APR",
                    Status_Date=datetime.now(),
                    Status_By=self.current_user.Usercode,
                    Modified_By=self.current_user.Usercode,
                    Church_Code=church.Code,
                    LeadChurch_Code=lead_church.Code,
                    HeadChurch_Code=self.current_user.HeadChurch_Code,
                    Is_Active=1,
                ),
            )
            self.db.commit()
            return await self.get_church_leads_by_code(church.Code)
        except Exception as err:
            self.db.rollback()
            raise err

    async def get_all_churches_by_lead_code(
        self, leadchurch_code: str, is_active: Optional[bool] = None
    ):
        try:
            set_user_access(
                self.current_user_access,
                headchurch_code=self.current_user.HeadChurch_Code,
                # role_code=["ADM", "SAD"],
                # level_code=["CHU"],
                module_code=["HRCH"],
                # submodule_code=["HEAD", "CL1"],
                access_type=["VW"],
            )
            lead_church = await self.church_services.get_church_by_code(leadchurch_code)
            churches = (
                self.db.execute(
                    text(
                        """
                    SELECT LeadChurch_Code, B.* FROM tblChurchLeads A
                    LEFT JOIN tblChurches B ON B.Code = A.Church_Code
                    WHERE LeadChurch_Code = :LeadChurch_Code
                        AND HeadChurch_Code = :HeadChurch_Code;
                    """
                    ),
                    dict(
                        LeadChurch_Code=lead_church.Code,
                        HeadChurch_Code=self.current_user.HeadChurch_Code,
                    ),
                ).all()
                if is_active is None
                else self.db.execute(
                    text(
                        """
                    SELECT LeadChurch_Code, B.* FROM tblChurchLeads A
                    LEFT JOIN tblChurches B ON B.Code = A.Church_Code
                    WHERE LeadChurch_Code = :LeadChurch_Code
                        AND HeadChurch_Code = :HeadChurch_Code AND Is_Active = :Is_Active;
                    """
                    ),
                    dict(
                        LeadChurch_Code=lead_church.Code,
                        HeadChurch_Code=self.current_user.HeadChurch_Code,
                        Is_Active=is_active,
                    ),
                ).all()
            )
            return churches
        except Exception as err:
            raise err


def get_church_lead_services(
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
    current_user_access: Annotated[UserAccess, Depends(get_current_user_access)],
    church_services: Annotated[ChurchServices, Depends(get_church_services)],
    db_current_user: Annotated[str, Depends(set_db_current_user)],
):
    return ChurchLeadsServices(db, current_user, current_user_access, church_services)
