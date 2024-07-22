from datetime import datetime
from typing import Annotated, Optional

from fastapi import HTTPException, status, Depends  # type: ignore
from sqlalchemy import text  # type: ignore
from sqlalchemy.orm import Session  # type: ignore

from ...church_admin.services.churches import ChurchServices, get_church_services
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
                    -- Anchor/Base case: Select the initial lead church and its direct churches
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
                    WHERE L.Code = :Church_Code AND L.Head_Code = :Head_Code
                    
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
        self, church_code: str, status_code: Optional[str] = None
    ):
        try:
            # fetch church data
            church = await self.church_services.get_church_by_id_code(church_code)
            # check if church is active/approved
            if not church.Is_Active and church.Status != "APR":
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Church: '{church.Name} ({church.Code})' is not active or approved.",
                )
            set_user_access(
                self.current_user_access,
                head_code=self.current_user.Head_Code,
                module_code=["ALLM", "HRCH"],
                access_type=["VW"],
            )
            church_leads = (
                self.db.execute(
                    text(
                        """
                    SELECT CL.*, C.Name AS Church_Name, L.Name AS LeadChurch_Name
                    FROM tblChurchLeads CL
                    LEFT JOIN tblChurches C ON C.Code = CL.Church_Code
                    LEFT JOIN tblChurches L ON L.Code = CL.LeadChurch_Code
                    WHERE Church_Code = :Church_Code AND CL.Head_Code = :Head_Code
                    ORDER BY Start_Date DESC;
                    """
                    ),
                    dict(
                        Church_Code=church_code,
                        Head_Code=self.current_user.Head_Code,
                    ),
                ).all()
                if status_code is None
                else self.db.execute(
                    text(
                        """
                    SELECT CL.*, C.Name AS Church_Name, L.Name AS LeadChurch_Name
                    FROM tblChurchLeads CL
                    LEFT JOIN tblChurches C ON C.Code = CL.Church_Code
                    LEFT JOIN tblChurches L ON L.Code = CL.LeadChurch_Code
                    WHERE Church_Code = :Church_Code AND CL.Head_Code = :Head_Code 
                        AND CL.Status = :Status 
                    ORDER BY Start_Date DESC;
                    """
                    ),
                    dict(
                        Church_Code=church_code,
                        Head_Code=self.current_user.Head_Code,
                        Status=status_code,
                    ),
                ).all()
            )
            return church_leads
        except Exception as err:
            raise err

    async def get_current_church_lead_by_code(self, church_code: str):
        """Get Church Lead by Code (by Both Church and Lead Church Code)"""
        try:
            # fetch and check church and lead church data
            church = await self.church_services.get_church_by_id_code(church_code)
            # lead_church = await self.church_services.get_church_by_id_code(lead_code)
            # check if church is active/approved
            if not church.Is_Active and church.Status != "APR":
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Church: '{church.Name} ({church.Code})' is not active or approved.",
                )
            set_user_access(
                self.current_user_access,
                head_code=self.current_user.Head_Code,
                module_code=["ALLM", "HRCH"],
                access_type=["VW"],
            )
            church_lead = self.db.execute(
                text(
                    """
                    SELECT CL.*, C.Name AS Church_Name, L.Name AS LeadChurch_Name
                    FROM tblChurchLeads CL
                    LEFT JOIN tblChurches C ON C.Code = CL.Church_Code
                    LEFT JOIN tblChurches L ON L.Code = CL.LeadChurch_Code
                    WHERE CL.Head_Code = :Head_Code AND CL.Status = :Status
                        AND Church_Code = :Church_Code
                    ORDER BY Start_Date DESC;
                    """
                ),
                dict(
                    Head_Code=self.current_user.Head_Code,
                    Status="APR",
                    Church_Code=church.Code,
                    # LeadChurch_Code=lead_church.Code,
                ),
            ).first()
            if not church_lead:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Church: '{church.Name} ({church.Code})' does not have a current Lead Church.",
                )
            return church_lead
        except Exception as err:
            raise err

    async def get_all_churches_by_lead_code(
        self,
        lead_code: str,
        status_code: Optional[str] = None,
        level_code: Optional[str] = None,
    ):
        try:
            set_user_access(
                self.current_user_access,
                head_code=self.current_user.Head_Code,
                module_code=["ALLM", "HRCH"],
                access_type=["VW"],
            )
            lead_church = await self.church_services.get_church_by_id_code(lead_code)
            churches = (
                # fetch all with no status and level filter
                self.db.execute(
                    text(
                        """
                        SELECT LeadChurch_Code, B.* FROM tblChurchLeads A
                        LEFT JOIN tblChurches B ON B.Code = A.Church_Code
                        WHERE LeadChurch_Code = :LeadChurch_Code
                            AND A.Head_Code = :Head_Code;
                        """
                    ),
                    dict(
                        LeadChurch_Code=lead_church.Code,
                        Head_Code=self.current_user.Head_Code,
                    ),
                ).all()
                if status_code is None and level_code is None
                else (
                    # fetch all with status filter
                    self.db.execute(
                        text(
                            """
                        SELECT LeadChurch_Code, B.* FROM tblChurchLeads A
                        LEFT JOIN tblChurches B ON B.Code = A.Church_Code
                        WHERE LeadChurch_Code = :LeadChurch_Code
                            AND A.Head_Code = :Head_Code 
                            AND B.Status = :Status;
                        """
                        ),
                        dict(
                            LeadChurch_Code=lead_church.Code,
                            Head_Code=self.current_user.Head_Code,
                            Status=status_code,
                        ),
                    ).all()
                    if level_code is None
                    # fetch all with church level filter
                    else self.db.execute(
                        text(
                            """
                        SELECT LeadChurch_Code, B.* FROM tblChurchLeads A
                        LEFT JOIN tblChurches B ON B.Code = A.Church_Code
                        WHERE LeadChurch_Code = :LeadChurch_Code
                            AND A.Head_Code = :Head_Code 
                            AND B.Level_Code = :Level_Code;
                        """
                        ),
                        dict(
                            LeadChurch_Code=lead_church.Code,
                            Head_Code=self.current_user.Head_Code,
                            Level_Code=level_code,
                        ),
                    ).all()
                )
            )
            return churches
        except Exception as err:
            raise err

    async def get_branches_by_church_lead(
        self, church_code: str, status_code: Optional[str] = None
    ):
        """Get Branches by Church: accessible to all logged in user member."""
        try:
            level = get_level(church_code, self.current_user.Head_Code, self.db)
            if level.Level_No == 8:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="This church is a branch and does not have any branches.",
                )
            # set user access
            set_user_access(
                self.current_user_access,
                head_code=self.current_user.Head_Code,
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
                        WHERE Head_Code = :Head_Code 
                            AND `Code` IN (
                                SELECT Church FROM ChurchHierarchy
                                WHERE Church_Level = 'BRN'
                            )
                        ORDER BY `Code`;
                        """
                    ),
                    dict(
                        Head_Code=self.current_user.Head_Code,
                        Church_Code=church_code.upper(),
                    ),
                ).all()
                if status_code is None
                else self.db.execute(
                    text(
                        f"""
                        {church_recursive_cte}
                        SELECT * FROM tblChurches 
                        WHERE Head_Code = :Head_Code 
                            AND `Code` IN (
                                SELECT Church FROM ChurchHierarchy
                                WHERE Church_Level = 'BRN' 
                            )
                            AND Status = :Status 
                        ORDER BY `Code`;
                        """
                    ),
                    dict(
                        Head_Code=self.current_user.Head_Code,
                        Church_Code=church_code.upper(),
                        Status=status_code,
                    ),
                ).all()
            )
            return branches
        except Exception as err:
            self.db.rollback()
            raise err

    async def unmap_church_leads_by_church_code(self, church_code: str):
        try:
            # fetch church data
            church = await self.church_services.get_church_by_id_code(church_code)
            # check if church is active/approved
            if not church.Is_Active and church.Status != "APR":
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Church: '{church.Name} ({church.Code})' is not active or approved.",
                )
            # get church level no
            level = get_level(
                church.Level_Code, self.current_user.Head_Code, self.db
            )
            # set user access
            set_user_access(
                self.current_user_access,
                head_code=self.current_user.Head_Code,
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
            print(church.Code)
            # check if church is active/approved
            if not church.Is_Active and church.Status != "APR":
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Church: '{church.Name} ({church.Code})' is not active and approved.",
                )
            # check if lead church is active/approved
            if not lead_church.Is_Active and lead_church.Status != "APR":
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Selected Lead Church: '{lead_church.Name} ({lead_church.Code})' is not active and approved.",
                )
            # check if church is already mapped to lead church
            for church_lead in church_leads:
                if church_lead.LeadChurch_Code == lead_church.Code and (
                    church_lead.Is_Active or church_lead.Status == "APR"
                ):
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail=f"Church: '{church.Name} ({church.Code})' is currently mapped to Lead Church: '{lead_church.Name} ({lead_church.Code})'.",
                    )
            # check if church is already mapped to same lead church
            for church_lead in church_leads:
                if church_lead.LeadChurch_Code == lead_church.Code and (
                    church_lead.Is_Active or church_lead.Status == "APR"
                ):
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail=f"Church: '{church.Name} ({church.Code})' is currently mapped to Lead Church: '{lead_church.Name} ({lead_church.Code})'.",
                    )
            # get church level no
            level = get_level(
                church.Level_Code, self.current_user.Head_Code, self.db
            )
            # set user access
            set_user_access(
                self.current_user_access,
                head_code=self.current_user.Head_Code,
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
                        (Church_Code, Level_Code, LeadChurch_Code, LeadChurch_Level, Start_Date, Head_Code, Created_By)
                    VALUES 
                        (:Church_Code, :Level_Code, :LeadChurch_Code, :LeadChurch_Level, :Start_Date, :Head_Code, :Created_By);
                    """
                ),
                dict(
                    Church_Code=church.Code,
                    Level_Code=church.Level_Code,
                    LeadChurch_Code=lead_church.Code,
                    LeadChurch_Level=lead_church.Level_Code,
                    Start_Date=datetime.now(),
                    Head_Code=self.current_user.Head_Code,
                    Created_By=self.current_user.Usercode,
                ),
            )
            self.db.commit()
            new_church_lead = self.db.execute(
                text(
                    """
                    SELECT CL.*, C.Name AS Church_Name, L.Name AS LeadChurch_Name
                    FROM tblChurchLeads CL
                    LEFT JOIN tblChurches C ON C.Code = CL.Church_Code
                    LEFT JOIN tblChurches L ON L.Code = CL.LeadChurch_Code
                    WHERE CL.Id = LAST_INSERT_ID();
                    """
                )
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
                    detail=f"This Church Lead mapping is no longer active.",
                )
            # get church level no
            level = get_level(
                church.Level_Code, self.current_user.Head_Code, self.db
            )
            # set user access
            set_user_access(
                self.current_user_access,
                head_code=self.current_user.Head_Code,
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
                    AND Head_Code = :Head_Code
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
                    Head_Code=self.current_user.Head_Code,
                    Is_Active=1,
                ),
            )
            self.db.commit()
            return await self.get_current_church_lead_by_code(church.Code)
        except Exception as err:
            self.db.rollback()
            raise err

    async def get_church_lead_hierarchy_by_church_code(self, church_code: str):
        try:
            # fetch church data
            church = await self.church_services.get_church_by_id_code(church_code)
            # fetch church leads hierarchy
            church_leads_hierarchy = self.db.execute(
                text(
                    """
                    SELECT * FROM vwChurchLeadHierarchy 
                    WHERE Church_Code = :Church_Code;
                    """
                ),
                dict(Church_Code=church.Code),
            ).first()
            if not church_leads_hierarchy:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Church: '{church.Name} ({church.Code})' not found in any Church Hierarchy.",
                )
            return church_leads_hierarchy
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
