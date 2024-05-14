from datetime import datetime

from fastapi import HTTPException, status  # type: ignore
from sqlalchemy import text  # type: ignore
from sqlalchemy.orm import Session  # type: ignore

from ...hierarchy_mgmt.services.church import ChurchServices
from ...authentication.models.auth import User, UserAccess
from ...common.utils import get_level_no, set_user_access


class ChurchLeadsServices:
    """
    #### Church Leads Service methods
    - Get Church Leads by Code
    - Unmap Church Leads by Code
    - Map Church Leads by Code
    - Get Churches by Lead Code
    """

    async def get_church_leads_by_code(
        self,
        code: str,
        db: Session,
        current_user: User,
        current_user_access: UserAccess,
    ):
        try:
            # fetch church data
            church = await ChurchServices().get_church_by_code(
                code, db, current_user, current_user_access
            )
            # check if church is active/approved
            if not church.Is_Active and church.Status != "APR":
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Church: {church.Name} is not active/approved.",
                )
            set_user_access(
                current_user_access,
                headchurch_code=current_user.HeadChurch_Code,
                # role_code=["ADM", "SAD"],
                # level_code=["CHU", "CL1"],
                module_code=["HRCH"],
                # submodule_code=["HEAD", "CL1"],
                access_type=["VW"],
            )
            church_leads = db.execute(
                text(
                    """
                    SELECT Church_Code, Level_Code, LeadChurch_Code, LeadChurch_Level, Is_Active, Start_Date, End_Date, HeadChurch_Code, Created_Date, Created_By, Modified_Date, Modified_By, `Status`, Status_By, Status_Date
                    FROM tblChurchLeads 
                    WHERE Code = :Code AND HeadChurch_Code = :HeadChurch_Code
                    ORDER BY Start_Date DESC;
                    """
                ),
                dict(Code=code, HeadChurch_Code=current_user.HeadChurch_Code),
            ).all()
            return church_leads
        except Exception as err:
            raise err

    async def unmap_church_leads_by_code(
        self,
        church_code: str,
        db: Session,
        current_user: User,
        current_user_access: UserAccess,
    ):
        try:
            # fetch church data
            church = await ChurchServices().get_church_by_code(
                church_code, db, current_user, current_user_access
            )
            # check if church is active/approved
            if not church.Is_Active and church.Status != "APR":
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Church: {church.Name} is not active/approved.",
                )
            # get church level no
            level_no = get_level_no(church.Level_Code, current_user.HeadChurch_Code, db)
            # set user access
            set_user_access(
                current_user_access,
                headchurch_code=current_user.HeadChurch_Code,
                role_code=["ADM", "SAD"],
                # level_code=["CHU"],
                level_no=level_no - 1,
                module_code=["HRCH"],
                # submodule_code=["HEAD", "CL1"],
                access_type=["ED", "VW"],
            )
            # ummap church from any active church lead
            db.execute(
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
                    Modified_By=current_user.Usercode,
                    Status="INA",
                    Status_By=current_user.Usercode,
                    Status_Date=datetime.now(),
                    Code=church_code,
                ),
            )
            db.commit()
            return await self.get_church_leads_by_code(
                church_code, db, current_user, current_user_access
            )
        except Exception as err:
            db.rollback()
            raise err

    async def map_church_lead_by_code(
        self,
        church_code: str,
        lead_church_code: str,
        db: Session,
        current_user: User,
        current_user_access: UserAccess,
    ):
        try:
            # fetch church data
            church = await ChurchServices().get_church_by_code(
                church_code, db, current_user, current_user_access
            )
            # fetch lead church data
            lead_church = await ChurchServices().get_church_by_code(
                lead_church_code, db, current_user, current_user_access
            )
            # fetch church leads
            church_leads = await self.get_church_leads_by_code(
                church_code, db, current_user, current_user_access
            )
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
            level_no = get_level_no(church.Level_Code, current_user.HeadChurch_Code, db)
            # set user access
            set_user_access(
                current_user_access,
                headchurch_code=current_user.HeadChurch_Code,
                role_code=["ADM", "SAD"],
                # level_code=["CHU"],
                level_no=level_no - 1,
                module_code=["HRCH"],
                # submodule_code=["HEAD", "CL1"],
                access_type=["ED"],
            )
            # unmap any current church leads
            await self.unmap_church_leads_by_code(
                church_code, db, current_user, current_user_access
            )
            # assign church leads
            db.execute(
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
                    HeadChurch_Code=current_user.HeadChurch_Code,
                    Created_By=current_user.Usercode,
                ),
            )
            db.commit()
            return await self.get_church_leads_by_code(
                church_code, db, current_user, current_user_access
            )
        except Exception as err:
            db.rollback()
            raise err

    async def approve_church_lead_by_code(
        self,
        church_code: str,
        leadchurch_code: str,
        db: Session,
        current_user: User,
        current_user_access: UserAccess,
    ):
        try:
            # fetch church data
            church = await ChurchServices().get_church_by_code(
                church_code, db, current_user, current_user_access
            )
            # fetch lead church data
            lead_church = await ChurchServices().get_church_by_code(
                leadchurch_code, db, current_user, current_user_access
            )
            # fetch church leads
            church_leads = await self.get_church_leads_by_code(
                church_code, db, current_user, current_user_access
            )
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
            level_no = get_level_no(church.Level_Code, current_user.HeadChurch_Code, db)
            # set user access
            set_user_access(
                current_user_access,
                headchurch_code=current_user.HeadChurch_Code,
                role_code=["ADM", "SAD"],
                # level_code=["CHU"],
                level_no=level_no - 1,
                module_code=["HRCH"],
                # submodule_code=["HEAD", "CL1"],
                access_type=["ED"],
            )
            # approve church leads
            db.execute(
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
                    Status_By=current_user.Usercode,
                    Modified_By=current_user.Usercode,
                    Church_Code=church.Code,
                    LeadChurch_Code=lead_church.Code,
                    HeadChurch_Code=current_user.HeadChurch_Code,
                    Is_Active=1,
                ),
            )
            db.commit()
            return await self.get_church_leads_by_code(
                church.Code, db, current_user, current_user_access
            )
        except Exception as err:
            db.rollback()
            raise err

    async def get_all_churches_by_lead_code(
        self,
        leadchurch_code: str,
        db: Session,
        current_user: User,
        current_user_access: UserAccess,
    ):
        try:
            set_user_access(
                current_user_access,
                headchurch_code=current_user.HeadChurch_Code,
                # role_code=["ADM", "SAD"],
                # level_code=["CHU"],
                module_code=["HRCH"],
                # submodule_code=["HEAD", "CL1"],
                access_type=["VW"],
            )
            lead_church = await ChurchServices().get_church_by_code(
                leadchurch_code, db, current_user, current_user_access
            )
            churches = db.execute(
                text(
                    """
                    SELECT LeadChurch_Code, B.*
                    FROM tblChurchLeads A
                    LEFT JOIN tblChurches B ON B.Code = A.Church_Code
                    WHERE LeadChurch_Code = :LeadChurch_Code
                        AND HeadChurch_Code = :HeadChurch_Code;
                    """
                ),
                dict(
                    LeadChurch_Code=lead_church.Code,
                    HeadChurch_Code=current_user.HeadChurch_Code,
                ),
            )
            return churches
        except Exception as err:
            raise err
