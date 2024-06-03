from datetime import datetime
from typing import Annotated, Optional

from fastapi import HTTPException, status, Depends  # type: ignore
from sqlalchemy import text  # type: ignore
from sqlalchemy.orm import Session  # type: ignore

from ...hierarchy_mgmt.services.church import ChurchServices, get_church_services
from ...authentication.models.auth import User, UserAccess
from ...common.database import get_db
from ...common.utils import get_level, set_user_access
from ...common.dependencies import (
    get_current_user,
    get_current_user_access,
    set_db_current_user,
)

church_recursive_cte = """
                WITH RECURSIVE ChurchHierarchy AS (
                    -- Base case: Select the initial lead church and its direct churches
                    SELECT 
                        L.Code AS `Lead`, 
                        L.Name AS Lead_Name, 
                        L.Level_Code AS Lead_Level, 
                        CL.Church_Code AS Church, 
                        C.Name AS Church_Name, 
                        C.Level_Code AS Church_Level, 
                        1 AS LevelNo
                    FROM tblChurches L
                        JOIN tblChurchLeads CL ON CL.LeadChurch_Code = L.Code
                        JOIN tblChurches C ON C.Code = CL.Church_Code
                    WHERE L.Code = :Church_Code AND L.HeadChurch_Code = :HeadChurch_Code
                    
                    UNION ALL
                    
                    -- Recursive case: Select the next level of churches
                    SELECT 
                        CH.Lead, 
                        CH.Lead_Name, 
                        CH.Lead_Level, 
                        CL.Church_Code AS Church, 
                        C.Name AS Church_Name, 
                        C.Level_Code AS Church_Level, 
                        CH.LevelNo + 1 AS LevelNo
                    FROM ChurchHierarchy CH
                        JOIN tblChurchLeads CL ON CL.LeadChurch_Code = CH.Church
                        JOIN tblChurches C ON C.Code = CL.Church_Code
                    WHERE CH.LevelNo < 10
                )
                """


class ChurchLeadsServices:
    """
    #### Church Leads Service methods
    - Get Church Leads by Code
    - Unmap Church Leads by Code
    - Map Church Leads by Coded
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

    async def get_church_leads_by_church_code(
        self, church_code: str, is_active: Optional[bool] = None
    ):
        try:
            # fetch church data
            church = await self.church_services.get_church_by_id_code(church_code)
            # check if church is active/approved
            if not church.Is_Active and church.Status != "APR":
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Church: {church.Name} is not active/approved.",
                )
            set_user_access(
                self.current_user_access,
                headchurch_code=self.current_user.HeadChurch_Code,
                module_code=["ALLM", "HRCH"],
                access_type=["VW"],
            )
            church_leads = (
                self.db.execute(
                    text(
                        """
                    SELECT Church_Code, Level_Code, LeadChurch_Code, LeadChurch_Level, Is_Active, Start_Date, End_Date, HeadChurch_Code, Created_Date, Created_By, Modified_Date, Modified_By, `Status`, Status_By, Status_Date
                    FROM tblChurchLeads 
                    WHERE Church_Code = :Church_Code AND HeadChurch_Code = :HeadChurch_Code
                    ORDER BY Start_Date DESC;
                    """
                    ),
                    dict(
                        Church_Code=church_code,
                        HeadChurch_Code=self.current_user.HeadChurch_Code,
                    ),
                ).all()
                if is_active is None
                else self.db.execute(
                    text(
                        """
                    SELECT Church_Code, Level_Code, LeadChurch_Code, LeadChurch_Level, Is_Active, Start_Date, End_Date, HeadChurch_Code, Created_Date, Created_By, Modified_Date, Modified_By, `Status`, Status_By, Status_Date
                    FROM tblChurchLeads 
                    WHERE Church_Code = :Church_Code AND HeadChurch_Code = :HeadChurch_Code 
                        AND A.Is_Active = :Is_Active
                    ORDER BY Start_Date DESC;
                    """
                    ),
                    dict(
                        Church_Code=church_code,
                        HeadChurch_Code=self.current_user.HeadChurch_Code,
                        Is_Active=is_active,
                    ),
                ).all()
            )
            return church_leads
        except Exception as err:
            raise err

    async def unmap_church_leads_by_church_code(self, church_code: str):
        try:
            # fetch church data
            church = await self.church_services.get_church_by_id_code(church_code)
            # check if church is active/approved
            if not church.Is_Active and church.Status != "APR":
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Church: {church.Name} is not active/approved.",
                )
            # get church level no
            level = get_level(
                church.Level_Code, self.current_user.HeadChurch_Code, self.db
            )
            # set user access
            set_user_access(
                self.current_user_access,
                headchurch_code=self.current_user.HeadChurch_Code,
                role_code=["ADM", "SAD"],
                # level_code=["CHU"],
                level_no=level.Level_No - 1,
                module_code=["ALLM", "HRCH"],
                # submodule_code=["HEAD", "CL1"],
                access_type=["ED", "VW"],
            )
            # ummap church from any active church lead
            self.db.execute(
                text(
                    """
                    UPDATE tblChurchLeads 
                    SET End_Date = :End_Date, Is_Active = :Is_Active, Modified_By = :Modified_By, Status = :Status, Status_By = :Status_By, Status_Date = :Status_Date 
                    WHERE Church_Code = :Church_Code AND End_Date IS NULL;
                    """
                ),
                dict(
                    End_Date=datetime.now(),
                    Is_Active=0,
                    Modified_By=self.current_user.Usercode,
                    Status="INA",
                    Status_By=self.current_user.Usercode,
                    Status_Date=datetime.now(),
                    Church_Code=church_code,
                ),
            )
            self.db.commit()
            return await self.get_church_leads_by_church_code(church_code)
        except Exception as err:
            self.db.rollback()
            raise err

    async def map_church_lead_by_code(self, church_code: str, lead_code: str):
        try:
            # fetch church data
            church = await self.church_services.get_church_by_id_code(church_code)
            # fetch lead church data
            lead_church = await self.church_services.get_church_by_id_code(lead_code)
            # fetch church leads
            church_leads = await self.get_church_leads_by_church_code(church_code)
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
                    church_lead.LeadChurch_Code == lead_church.Code
                    and church_lead.Is_Active
                    and church_lead.Status == "APR"
                ):
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail=f"Church: '{church.Name}' is currently mapped to selected Lead Church: '{lead_church.Name}'.",
                    )
            # get church level no
            level = get_level(
                church.Level_Code, self.current_user.HeadChurch_Code, self.db
            )
            # set user access
            set_user_access(
                self.current_user_access,
                headchurch_code=self.current_user.HeadChurch_Code,
                role_code=["ADM", "SAD"],
                # level_code=["CHU"],
                level_no=level.Level_No - 1,
                module_code=["ALLM", "HRCH"],
                # submodule_code=["HEAD", "CL1"],
                access_type=["ED"],
            )
            # unmap any current church leads
            await self.unmap_church_leads_by_church_code(
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
            new_church_lead = self.db.execute(
                text("SELECT * FROM tblChurchLeads WHERE Id = LAST_INSERT_ID();")
            ).first()
            return new_church_lead
        except Exception as err:
            self.db.rollback()
            raise err

    async def approve_church_lead_by_code(self, church_code: str, lead_code: str):
        try:
            # fetch church data
            church = await self.church_services.get_church_by_id_code(church_code)
            # fetch lead church data
            lead_church = await self.church_services.get_church_by_id_code(lead_code)
            # fetch church leads
            church_leads = await self.get_church_leads_by_church_code(church_code)
            # check if church lead is active or already approved
            for church_lead in church_leads:
                if (
                    church_lead.LeadChurch_Code == lead_church.Code
                    and church_lead.Is_Active
                    and church_lead.Status == "APR"
                ):
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail=f"Church Lead mapping is already approved.",
                    )
                elif (
                    church_lead.LeadChurch_Code == lead_church.Code
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
            level = get_level(
                church.Level_Code, self.current_user.HeadChurch_Code, self.db
            )
            # set user access
            set_user_access(
                self.current_user_access,
                headchurch_code=self.current_user.HeadChurch_Code,
                role_code=["ADM", "SAD"],
                # level_code=["CHU"],
                level_no=level.Level_No - 1,
                module_code=["ALLM", "HRCH"],
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
            return await self.get_church_leads_by_church_code(church.Code)
        except Exception as err:
            self.db.rollback()
            raise err

    async def get_all_churches_by_lead_code(
        self, lead_code: str, is_active: Optional[bool] = None
    ):
        try:
            set_user_access(
                self.current_user_access,
                headchurch_code=self.current_user.HeadChurch_Code,
                module_code=["ALLM", "HRCH"],
                access_type=["VW"],
            )
            lead_church = await self.church_services.get_church_by_id_code(lead_code)
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

    async def get_branches_by_church_lead(
        self, church_code: str, status_code: Optional[str] = None
    ):
        """Get Branches by Church: accessible to all logged in user member."""
        try:
            level = get_level(church_code, self.current_user.HeadChurch_Code, self.db)
            if level.Level_No == 8:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="This church is a branch and does not have any branches.",
                )
            # set user access
            set_user_access(
                self.current_user_access,
                headchurch_code=self.current_user.HeadChurch_Code,
                module_code=["ALLM", "HRCH"],
                access_type=["VW"],
            )
            # fetch churches by level
            branches = (
                self.db.execute(
                    text(
                        f"""
                        {church_recursive_cte}
                        SELECT * FROM tblChurches 
                        WHERE HeadChurch_Code = :HeadChurch_Code 
                            AND `Code` IN (
                                SELECT Church FROM ChurchHierarchy
                                WHERE Church_Level = 'BRN'
                            )
                        ORDER BY `Code`;
                        """
                    ),
                    dict(
                        HeadChurch_Code=self.current_user.HeadChurch_Code,
                        Church_Code=church_code.upper(),
                    ),
                ).all()
                if status_code is None
                else self.db.execute(
                    text(
                        f"""
                        {church_recursive_cte}
                        SELECT * FROM tblChurches 
                        WHERE HeadChurch_Code = :HeadChurch_Code 
                            AND `Code` IN (
                                SELECT Church FROM ChurchHierarchy
                                WHERE Church_Level = 'BRN' 
                            )
                            AND Status = :Status 
                        ORDER BY `Code`;
                        """
                    ),
                    dict(
                        HeadChurch_Code=self.current_user.HeadChurch_Code,
                        Church_Code=church_code.upper(),
                        Status=status_code,
                    ),
                ).all()
            )
            return branches
        except Exception as err:
            self.db.rollback()
            raise err


def get_church_lead_services(
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
    current_user_access: Annotated[UserAccess, Depends(get_current_user_access)],
    church_services: Annotated[ChurchServices, Depends(get_church_services)],
    db_current_user: Annotated[str, Depends(set_db_current_user)],
):
    return ChurchLeadsServices(db, current_user, current_user_access, church_services)
