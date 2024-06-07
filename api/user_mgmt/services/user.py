from typing import Annotated
from secrets import token_hex

from ...authentication.services.auth import AuthService
from fastapi import Depends  # type: ignore
from sqlalchemy import text  # type: ignore
from sqlalchemy.orm import Session  # type: ignore

from ...common.database import get_db
from ...authentication.models.auth import User, UserAccess
from ...common.utils import get_level, set_user_access
from ...membership_mgmt.services.members import MemberServices, get_member_services
from ...common.dependencies import (
    get_current_user,
    get_current_user_access,
    set_db_current_user,
)


class UserServices:
    def __init__(
        self,
        db: Session,
        current_user: User,
        current_user_access: UserAccess,
        member_services: MemberServices,
    ):
        self.db = db
        self.current_user = current_user
        self.current_user_access = current_user_access
        self.member_services = member_services

    async def create_user_from_member(self, member_code: str):
        """Create User From Member: accessible to only church admins of same/higher level/church."""
        try:
            # fetch user member data
            user = await self.member_services.get_member_by_code(member_code)
            level = get_level(
                user.Church_Code, self.current_user.HeadChurch_Code, self.db
            )
            new_password = token_hex(10)
            # password_hash = AuthService().get_password_hash(new_password)
            # set user access
            set_user_access(
                self.current_user_access,
                headchurch_code=self.current_user.HeadChurch_Code,
                church_code=user.Church_Code,
                level_no=level.Level_No - 1,
                role_code=["ADM", "SAD"],
                module_code=["MBSH"],
                submodule_code=["MBRS"],
                access_type=["ED", "CR"],
            )
            # promote a member to user in tblMember
            self.db.execute(
                text(
                    """
                    Update tblMember
                    SET Is_User = :Is_User
                    WHERE `Code` = :Usercode AND Is_Active = :Is_Active
                        AND HeadChurch_Code = :HeadChurch_Code
                    """
                ),
                dict(
                    Is_User=1,
                    Usercode=member_code,
                    Is_Active=1,
                    HeadChurch_Code=self.current_user.HeadChurch_Code,
                ),
            )
            self.db.commit()
            # insert new user into tblUser
            self.db.execute(
                text(
                    """
                    INSERT INTO tblUser
                        (Usercode, Email, Password, HeadChurch_Code)
                    VALUES
                        (:Usercode, :Email, :Password, :HeadChurch_Code)
                    """
                ),
                dict(
                    Usercode=user.Code,
                    Email=user.Personal_Email,
                    Password=AuthService().get_password_hash(new_password),
                    HeadChurch_Code=user.HeadChurch_Code,
                ),
            )
            self.db.commit()
            return await self.get_user_details(user.Code)
        except Exception as err:
            self.db.rollback()
            raise err

    async def get_user_details(self, usercode: str):
        """Get User Details: accessible to only church admins of same/higher level/church."""
        try:
            user = await self.member_services.get_member_by_code(usercode)
            level = get_level(
                user.Church_Code, self.current_user.HeadChurch_Code, self.db
            )
            # set user access
            set_user_access(
                self.current_user_access,
                headchurch_code=self.current_user.HeadChurch_Code,
                church_code=user.Church_Code,
                level_no=level.Level_No - 1,
                role_code=["ADM", "SAD"],
                module_code=["MBSH"],
                submodule_code=["MBRS"],
                access_type=["ED", "CR"],
            )
            # fetch user details
            user_details = self.db.execute(
                text(
                    """
                    SELECT U.*, M.First_Name, M.Last_Name, M.Title, M.Title2 FROM tblUser U
                    LEFT JOIN tblMember M ON M.Code = U.Usercode
                    WHERE Usercode = :Usercode
                    """
                ),
                dict(Usercode=user.Code),
            )
            return user_details
        except Exception as err:
            raise err


def get_user_services(
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
    current_user_access: Annotated[UserAccess, Depends(get_current_user_access)],
    member_services: Annotated[MemberServices, Depends(get_member_services)],
    db_current_user: Annotated[str, Depends(set_db_current_user)],
):
    return UserServices(db, current_user, current_user_access, member_services)
