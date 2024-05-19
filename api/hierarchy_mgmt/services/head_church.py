from datetime import datetime
from typing import Annotated

from fastapi import HTTPException, status, Depends  # type: ignore
from sqlalchemy import text  # type: ignore
from sqlalchemy.orm import Session  # type: ignore

from ...authentication.models.auth import User, UserAccess
from ...hierarchy_mgmt.models.head_church import HeadChurch, HeadChurchUpdateIn
from ...common.database import get_db
from ...common.dependencies import (
    get_current_user,
    get_current_user_access,
    set_db_current_user,
)
from ...common.utils import (
    check_if_new_code_exist,
    check_if_new_name_exist,
    set_user_access,
)


class HeadChurchServices:
    """
    Head Church Services
    - Create Head Church
    - Get Head Church by Code
    - Update Head Church by Code
    - Activate Head Church by Code
    - Deactivate Head Church by Code
    """

    def __init__(
        self,
        db: Session,
        current_user: User,
        current_user_access: UserAccess,
    ):
        self.db = db
        self.current_user = current_user
        self.current_user_access = current_user_access

    async def create_head_church(self, head_church: HeadChurch):
        try:
            # check if new Code or Name already exists
            check_if_new_code_exist(head_church.Code, "tblCLHeadChurch", self.db)
            check_if_new_name_exist(head_church.Name, "tblCLHeadChurch", self.db)
            # insert new head church
            self.db.execute(
                text(
                    """
                    INSERT INTO tblCLHeadChurch
                        (Code, Name, Alt_Name, Address, Founding_Date, About, Mission, Vision, Motto, Contact_No, Contact_No2, Contact_Email, Contact_Email2, Town_Code, State_Code, Region_Code, Country_Code, Created_By)
                    VALUES
                        (:Code, :Name, :Alt_Name, :Address, :Founding_Date, :About, :Mission, :Vision, :Motto, :Contact_No, :Contact_No2, :Contact_Email, :Contact_Email2, :Town_Code, :State_Code, :Region_Code, :Country_Code, :Created_By);
                    """
                ),
                dict(
                    Code=head_church.Code,
                    Name=head_church.Name,
                    Alt_Name=head_church.Alt_Name,
                    Address=head_church.Address,
                    Founding_Date=head_church.Founding_Date,
                    About=head_church.About,
                    Mission=head_church.Mission,
                    Vision=head_church.Vision,
                    Motto=head_church.Motto,
                    Contact_No=head_church.Contact_No,
                    Contact_No2=head_church.Contact_No2,
                    Contact_Email=head_church.Contact_Email,
                    Contact_Email2=head_church.Contact_Email2,
                    Town_Code=head_church.Town_Code,
                    State_Code=head_church.State_Code,
                    Region_Code=head_church.Region_Code,
                    Country_Code=head_church.Country_Code,
                    Created_By=head_church.Code + "_ADMIN",
                ),
            )
            self.db.commit()
            new_head_church = self.db.execute(
                text("SELECT * FROM tblCLHeadChurch WHERE Id = LAST_INSERT_ID();")
            ).first()
            return new_head_church
        except Exception as err:
            self.db.rollback()
            raise err

    async def get_head_church_by_code(self, code: str):
        try:
            # set user access
            set_user_access(
                self.current_user_access,
                headchurch_code=self.current_user.HeadChurch_Code,
                role_code=["ADM", "SAD"],
                level_code=["CHU"],
                module_code=["HRCH"],
                submodule_code=["HEAD"],
                access_type=["VW", "ED"],
            )
            # fetch data from self.db
            head_church = self.db.execute(
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
            self.db.rollback()
            raise err

    async def update_head_church_by_code(
        self, code: str, head_church: HeadChurchUpdateIn
    ):
        try:
            # set user access
            set_user_access(
                self.current_user_access,
                headchurch_code=self.current_user.HeadChurch_Code,
                role_code=["ADM", "SAD"],
                level_code=["CHU"],
                module_code=["HRCH"],
                submodule_code=["HEAD"],
                access_type=["ED"],
            )
            # check if code exists
            old_head_church = await self.get_head_church_by_code(code)
            # check if new Code or Name already exists
            if head_church.Code:
                check_if_new_code_exist(head_church.Code, "tblCLHeadChurch", self.db)
            if head_church.Name:
                check_if_new_name_exist(head_church.Name, "tblCLHeadChurch", self.db)

            # update the data
            self.db.execute(
                text(
                    """
                    UPDATE tblCLHeadChurch
                    SET
                        Code = :Code, Name = :Name, Alt_Name = :Alt_Name, Address = :Address, Founding_Date = :Founding_Date, About = :About, Mission = :Mission, Vision = :Vision, Motto = :Motto, Contact_No = :Contact_No, Contact_No2 = :Contact_No2, Contact_Email = :Contact_Email, Contact_Email2 = :Contact_Email2, Town_Code = :Town_Code, State_Code = :State_Code, Region_Code = :Region_Code, Country_Code = :Country_Code, Modified_By = :Modified_By                        
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
                    Modified_By=self.current_user.Usercode,
                    Code2=code,
                ),
            )
            self.db.commit()
            # fetch the updated data
            h_code = head_church.Code if head_church.Code else old_head_church.Code
            updated_data = await self.get_head_church_by_code(h_code)
            return updated_data
        except Exception as err:
            self.db.rollback()
            raise err

    async def activate_head_church_by_code(self, code: str):
        try:
            # set user access
            set_user_access(
                self.current_user_access,
                headchurch_code="ALL",
                role_code=["SAD"],
                level_code=["CHU"],
                module_code=["HRCH"],
                submodule_code=["HEAD"],
                access_type=["ED"],
            )
            # check if it exists
            await self.get_head_church_by_code(code)
            # update head church data
            self.db.execute(
                text(
                    """
                    UPDATE tblCLHeadChurch 
                    SET Is_Active = :Is_Active, Modified_By = :Modified_By 
                    WHERE Code = :Code;
                    """
                ),
                dict(
                    Is_Active=1,
                    Modified_By=self.current_user.Usercode,
                    Code=code,
                ),
            )
            self.db.commit()
            # update it in tblChurches
            self.db.execute(
                text(
                    """
                    UPDATE tblChurches 
                    SET Is_Active = :Is_Active, Modified_By = :Modified_By, Status = :Status, Status_By = :Status_By, Status_Date = :Status_Date 
                    WHERE Code = :Code;
                    """
                ),
                dict(
                    Is_Active=1,
                    Modified_By=self.current_user.Usercode,
                    Status="ACT",
                    Status_By=self.current_user.Usercode,
                    Status_Date=datetime.now(),
                    Code=code,
                ),
            )
            self.db.commit()
            return await self.get_head_church_by_code(code)
        except Exception as err:
            self.db.rollback()
            raise err

    async def deactivate_head_church_by_code(self, code: str):
        try:
            # set user access
            set_user_access(
                self.current_user_access,
                headchurch_code="ALL",
                role_code=["SAD"],
                level_code=["CHU"],
                module_code=["HRCH"],
                submodule_code=["HEAD"],
                access_type=["ED"],
            )
            # check if it exists
            await self.get_head_church_by_code(code)
            # update head church data
            self.db.execute(
                text(
                    """
                    UPDATE tblCLHeadChurch 
                    SET Is_Active = :Is_Active, Modified_By = :Modified_By 
                    WHERE Code = :Code;
                    """
                ),
                dict(
                    Is_Active=0,
                    Modified_By=self.current_user.Usercode,
                    Code=code,
                ),
            )
            self.db.commit()
            # update it in tblChurches
            self.db.execute(
                text(
                    """
                    UPDATE tblChurches 
                    SET Is_Active = :Is_Active, Modified_By = :Modified_By, Status = :Status, Status_By = :Status_By, Status_Date = :Status_Date 
                    WHERE Code = :Code;
                    """
                ),
                dict(
                    Is_Active=0,
                    Modified_By=self.current_user.Usercode,
                    Status="INA",
                    Status_By=self.current_user.Usercode,
                    Status_Date=datetime.now(),
                    Code=code,
                ),
            )
            self.db.commit()
            return await self.get_head_church_by_code(code)
        except Exception as err:
            self.db.rollback()
            raise err


def get_head_church_services(
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
    current_user_access: Annotated[User, Depends(get_current_user_access)],
    db_current_user: Annotated[str, Depends(set_db_current_user)],
):
    return HeadChurchServices(db, current_user, current_user_access)
