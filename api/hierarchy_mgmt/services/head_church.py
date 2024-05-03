from ...check import User
from fastapi import HTTPException, status  # type: ignore
from sqlalchemy import text  # type: ignore
from sqlalchemy.orm import Session  # type: ignore

from ...authentication.models.auth import UserAccess
from ...hierarchy_mgmt.models.head_church import HeadChurchUpdateIn
from ...common.utils import (
    check_if_new_code_exist,
    check_if_new_name_exist,
    set_user_access,
)


class HeadChurchService:
    """
    Head Church Services
    - Get Head Church by Code
    - Update Head Church by Code
    """

    async def get_head_church_by_code(
        self,
        code: str,
        db: Session,
        current_user: User,
        current_user_access: UserAccess,
    ):
        try:
            # set user access
            set_user_access(
                current_user_access,
                headchurch_code=current_user.HeadChurch_Code,
                role_code=["ADM", "SAD"],
                level_code=["CHU"],
                module_code=["HRCH"],
                submodule_code=["HEAD"],
                access_type=["VW", "ED"],
            )
            # fetch data from db
            head_church = db.execute(
                text("SELECT * FROM tblCLHeadChurch WHERE Code = :Code;"),
                dict(Code=code),
            ).first()
            # check if data exists
            if not head_church:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Head Church with code: {code.upper()} not found",
                )
            return head_church
        except Exception as err:
            db.rollback()
            raise err

    async def update_head_church_by_code(
        self,
        code: str,
        head_church: HeadChurchUpdateIn,
        db: Session,
        current_user: User,
        current_user_access: UserAccess,
    ):
        try:
            # set user access
            set_user_access(
                current_user_access,
                headchurch_code=code,
                role_code=["ADM", "SAD"],
                submodule_code=["PROV", "HEAD"],
                access_type=["ED"],
            )
            # check if code exists
            old_head_church = await self.get_head_church_by_code(
                code, db, current_user, current_user_access
            )
            # check if new Code or Name already exists
            check_if_new_code_exist(head_church.Code, "tblCLHeadChurch", db)
            check_if_new_name_exist(head_church.Name, "tblCLHeadChurch", db)
            # update the data
            db.execute(
                text(
                    """
                    UPDATE tblCLHeadChurch
                    SET
                        Code = :Code,
                        Name = :Name,
                        Alt_Name = :Alt_Name,
                        Address = :Address,
                        Founding_Date = :Founding_Date,
                        About = :About,
                        Mission = :Mission,
                        Vision = :Vision,
                        Motto = :Motto,
                        Contact_No = :Contact_No,
                        Contact_No2 = :Contact_No2,
                        Contact_Email = :Contact_Email,
                        Contact_Email2 = :Contact_Email2,
                        Town_Code = :Town_Code,
                        State_Code = :State_Code,
                        Region_Code = :Region_Code,
                        Country_Code = :Country_Code,
                        Is_Active = :Is_Active,
                        Modified_By = :Modified_By                        
                    WHERE Code = :Code2;
                    """
                ),
                dict(
                    Code=(
                        head_church.Code if head_church.Code else old_head_church.Code
                    ),
                    Name=(
                        head_church.Name if head_church.Name else old_head_church.Name
                    ),
                    Alt_Name=(
                        head_church.Alt_Name
                        if head_church.Alt_Name
                        else old_head_church.Alt_Name
                    ),
                    Address=(
                        head_church.Address
                        if head_church.Address
                        else old_head_church.Address
                    ),
                    Founding_Date=(
                        head_church.Founding_Date
                        if head_church.Founding_Date
                        else old_head_church.Founding_Date
                    ),  # type: ignore
                    About=(
                        head_church.About
                        if head_church.About
                        else old_head_church.About
                    ),
                    Mission=(
                        head_church.Mission
                        if head_church.Mission
                        else old_head_church.Mission
                    ),
                    Vision=(
                        head_church.Vision
                        if head_church.Vision
                        else old_head_church.Vision
                    ),
                    Motto=(
                        head_church.Motto
                        if head_church.Motto
                        else old_head_church.Motto
                    ),
                    Contact_No=(
                        head_church.Contact_No
                        if head_church.Contact_No
                        else old_head_church.Contact_No
                    ),
                    Contact_No2=(
                        head_church.Contact_No2
                        if head_church.Contact_No2
                        else old_head_church.Contact_No2
                    ),
                    Contact_Email=(
                        head_church.Contact_Email
                        if head_church.Contact_Email
                        else old_head_church.Contact_Email
                    ),
                    Contact_Email2=(
                        head_church.Contact_Email2
                        if head_church.Contact_Email2
                        else old_head_church.Contact_Email2
                    ),
                    Town_Code=(
                        head_church.Town_Code
                        if head_church.Town_Code
                        else old_head_church.Town_Code
                    ),
                    State_Code=(
                        head_church.State_Code
                        if head_church.State_Code
                        else old_head_church.State_Code
                    ),
                    Region_Code=(
                        head_church.Region_Code
                        if head_church.Region_Code
                        else old_head_church.Region_Code
                    ),
                    Country_Code=(
                        head_church.Country_Code
                        if head_church.Country_Code
                        else old_head_church.Country_Code
                    ),
                    Is_Active=(
                        head_church.Is_Active
                        if head_church.Is_Active
                        else old_head_church.Is_Active
                    ),
                    Modified_By=current_user.Usercode,
                    Code2=code,
                ),
            )
            db.commit()
            # fetch the updated data
            h_code = head_church.Code if head_church.Code else old_head_church.Code
            updated_data = await self.get_head_church_by_code(
                h_code, db, current_user, current_user_access
            )
            return updated_data
        except Exception as err:
            db.rollback()
            raise err
