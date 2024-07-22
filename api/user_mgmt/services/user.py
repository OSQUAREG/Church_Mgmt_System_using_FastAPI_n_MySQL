from typing import Annotated, Optional
from secrets import token_hex

from fastapi import Depends, HTTPException, status  # type: ignore
from sqlalchemy import text  # type: ignore
from sqlalchemy.orm import Session  # type: ignore
from jose import jwt  # type: ignore

from ...authentication.models.auth import User, UserAccess
from ...authentication.services.auth import AuthService
from ...membership_mgmt.services.members import MemberServices, get_member_services
from ...user_mgmt.models.user import UserDetails, UserRoles, UserSubModules
from ...common.utils import (
    check_level_code,
    check_role_code,
    get_level,
    set_user_access,
)
from ...common.config import settings
from ...common.database import get_db
from ...common.dependencies import (
    get_current_user,
    get_current_user_access,
    set_db_current_user,
)

JWT_SECRET_KEY = settings.jwt_secret_key
ALGORITHM = settings.algorithm
ACCESS_TOKEN_EXPIRE_MINUTES = settings.access_token_expire_minutes


class UserServices:
    """
    User Service methods
    - Create User From Member
    - Get User Details by Usercode
    - Get Users Details
    - Assign User Role Access
    - Assign User Role Sub-Modules
    - Remove User Role Sub-Modules
    - Deactivate User
    """

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

    async def create_user_from_member(
        self, member_code: str, role_code: str, level_code: str
    ):
        """Create User From Member: accessible to only church admins of same/higher level/church."""
        try:
            # fetch user member data
            user = await self.member_services.get_member_by_code_id(member_code)
            # check if member has a branch
            if user.Branch_Code is None:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Member does not have a branch. User must be a member of a branch first.",
                )
            # check if member has personal email
            if user.Personal_Email is None:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Member has no personal email address. Please update User's Member detail.",
                )
            # check if member is active
            if user.Is_Active == 0:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Member is inactive.",
                )
            level = get_level(level_code, self.current_user.HeadChurch_Code, self.db)
            # set user access
            set_user_access(
                self.current_user_access,
                headchurch_code=self.current_user.HeadChurch_Code,
                church_code=user.Branch_Code,
                level_no=level.Level_No,
                role_code=["ADM", "SAD"],
                # module_code=["MBSH"],
                # submodule_code=["MBRS"],
                access_type=["ED", "CR"],
            )
            # check role code and level code
            check_role_code(role_code, self.db)
            check_level_code(level_code, self.db, self.current_user.HeadChurch_Code)
            # generate new password hash
            new_password = token_hex(10)
            print(new_password)
            password_hash = AuthService().get_password_hash(new_password)
            # update is_user to create user
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
            # insert new user
            self.db.execute(
                text(
                    """
                    INSERT INTO tblUser
                        (Usercode, Email, Password, Is_Member, Church_Code, HeadChurch_Code)
                    VALUES
                        (:Usercode, :Email, :Password, :HeadChurch_Code)
                    """
                ),
                dict(
                    Usercode=user.Code,
                    Email=user.Personal_Email,
                    Password=password_hash,
                    Is_Member=1,
                    Branch_Code=user.Branch_Code,
                    HeadChurch_Code=user.HeadChurch_Code,
                ),
            )
            self.db.commit()
            # assign user role
            self.db.execute(
                text(
                    """
                    INSERT INTO tblUserRole
                        (Usercode, Role_Code, Level_Code, HeadChurch_Code)
                    VALUES
                        (:Usercode, :Role_Code, :Level_Code, :HeadChurch_Code)
                    """
                ),
                dict(
                    Usercode=user.Code,
                    Role_Code=role_code.upper(),
                    Level_Code=level_code.upper(),
                    HeadChurch_Code=user.HeadChurch_Code,
                ),
            )
            self.db.commit()
            return await self.get_user_details(user.Code, level_code)
        except Exception as err:
            self.db.rollback()
            raise err

    async def get_user(self, usercode: str):
        """Get User: accessible to only church admins of same/higher level/church."""
        try:
            user = self.db.execute(
                text(
                    """
                    SELECT * FROM tblUser
                    WHERE Usercode = :Usercode
                    """
                ),
                dict(Usercode=usercode),
            ).first()
            return user
        except Exception as err:
            raise err

    async def get_user_submodules(
        self, level_code: str, usercode: Optional[str] = None
    ):
        try:
            if usercode:
                user = await self.get_user(usercode)
                user_submodules = (
                    self.db.execute(
                        text(
                            """
                            SELECT B.Submodule_Code, C.SubModule AS Submodule_Name, B.Module_Code, D.Module AS Module_Name, HL.Level_Code, HL.ChurchLevel_Code, HL.Church_Level, B.Access_Type,  A.Is_Active, A.Status
                            FROM tblUserRole U
                            INNER JOIN tblUserRoleSubModule A ON A.UserRole_Code = U.Code
                            LEFT JOIN dfSubModuleAccess B ON B.Code = A.SubModuleAccess_Code
                            LEFT JOIN dfSubModules C ON C.Code = B.SubModule_Code
                            LEFT JOIN dfModules D ON D.Code = B.Module_Code
                            LEFT JOIN tblHeadChurchLevels HL ON HL.Level_Code = U.Level_Code
                            WHERE U.Usercode = :Usercode AND U.Level_Code = :Level_Code
                                AND HL.Head_Code = :Head_Code AND HL.Is_Active = :Is_Active
                            """
                        ),
                        dict(
                            Usercode=user.Usercode,
                            Level_Code=level_code,
                            Head_Code=user.HeadChurch_Code,
                            Is_Active=1,
                        ),
                    ).all()
                    if level_code != "CHU"
                    else self.db.execute(
                        text(
                            """
                            SELECT B.Submodule_Code, C.SubModule AS Submodule_Name, B.Module_Code, D.Module AS Module_Name, HL.Level_Code, HL.ChurchLevel_Code, HL.Church_Level, B.Access_Type,  A.Is_Active, A.Status
                            FROM tblUserRole U
                            INNER JOIN tblUserRoleSubModule A ON A.UserRole_Code = U.Code
                            LEFT JOIN dfSubModuleAccess B ON B.Code = A.SubModuleAccess_Code
                            LEFT JOIN dfSubModules C ON C.Code = B.SubModule_Code
                            LEFT JOIN dfModules D ON D.Code = B.Module_Code
                            LEFT JOIN tblHeadChurchLevels HL ON HL.Level_Code = U.Level_Code
                            WHERE U.Usercode = :Usercode
                                AND HL.Head_Code = :Head_Code AND HL.Is_Active = :Is_Active
                            """
                        ),
                        dict(
                            Usercode=user.Usercode,
                            Head_Code=user.HeadChurch_Code,
                            Is_Active=1,
                        ),
                    ).all()
                )
            else:
                user_submodules = (
                    self.db.execute(
                        text(
                            """
                            SELECT B.Submodule_Code, C.SubModule AS Submodule_Name, B.Module_Code, D.Module AS Module_Name, HL.Level_Code, HL.ChurchLevel_Code, HL.Church_Level, B.Access_Type,  A.Is_Active, A.Status
                            FROM tblUserRole U
                            INNER JOIN tblUserRoleSubModule A ON A.UserRole_Code = U.Code
                            LEFT JOIN dfSubModuleAccess B ON B.Code = A.SubModuleAccess_Code
                            LEFT JOIN dfSubModules C ON C.Code = B.SubModule_Code
                            LEFT JOIN dfModules D ON D.Code = B.Module_Code
                            LEFT JOIN tblHeadChurchLevels HL ON HL.Level_Code = U.Level_Code
                            WHERE U.Level_Code = :Level_Code
                                AND HL.Head_Code = :Head_Code AND HL.Is_Active = :Is_Active
                            """
                        ),
                        dict(
                            Level_Code=level_code,
                            Head_Code=self.current_user.HeadChurch_Code,
                            Is_Active=1,
                        ),
                    ).all()
                    if level_code != "CHU"
                    else self.db.execute(
                        text(
                            """
                            SELECT B.Submodule_Code, C.SubModule AS Submodule_Name, B.Module_Code, D.Module AS Module_Name, HL.Level_Code, HL.ChurchLevel_Code, HL.Church_Level, B.Access_Type,  A.Is_Active, A.Status
                            FROM tblUserRole U
                            INNER JOIN tblUserRoleSubModule A ON A.UserRole_Code = U.Code
                            LEFT JOIN dfSubModuleAccess B ON B.Code = A.SubModuleAccess_Code
                            LEFT JOIN dfSubModules C ON C.Code = B.SubModule_Code
                            LEFT JOIN dfModules D ON D.Code = B.Module_Code
                            LEFT JOIN tblHeadChurchLevels HL ON HL.Level_Code = U.Level_Code
                            WHERE HL.Head_Code = :Head_Code AND HL.Is_Active = :Is_Active
                            """
                        ),
                        dict(
                            Head_Code=self.current_user.HeadChurch_Code,
                            Is_Active=1,
                        ),
                    ).all()
                )
            return user_submodules
        except Exception as err:
            raise err

    @staticmethod
    async def get_church_level_from_token(auth):
        token = auth.split("Bearer ")[-1]
        payload = jwt.decode(token, key=JWT_SECRET_KEY, algorithms=ALGORITHM)
        level_code = payload.get("church_level")

        if not level_code:
            raise HTTPException(status_code=400, detail="Level code not found in token")
        return level_code

    async def get_user_roles(self, level_code: str, usercode: Optional[str] = None):
        try:
            if usercode:
                user = await self.get_user(usercode)
                user_roles = (
                    self.db.execute(
                        text(
                            """
                            SELECT UR.Role_Code, R.Role AS Role_Name, HL.Level_Code, HL.ChurchLevel_Code, HL.Church_Level,  UR.Is_Active, UR.Status
                            FROM tblUserRole UR
                            LEFT JOIN dfRole R ON R.Code = UR.Role_Code
                            LEFT JOIN tblHeadChurchLevels HL ON HL.Level_Code = UR.Level_Code
                            WHERE UR.Usercode = :Usercode AND UR.Level_Code = :Level_Code
                                AND HL.Head_Code = :Head_Code AND HL.Is_Active = :Is_Active
                            """
                        ),
                        dict(
                            Usercode=user.Usercode,
                            Level_Code=level_code,
                            Head_Code=self.current_user.HeadChurch_Code,
                            Is_Active=1,
                        ),
                    ).all()
                    if level_code != "CHU"
                    else self.db.execute(
                        text(
                            """
                            SELECT UR.Role_Code, R.Role AS Role_Name, HL.Level_Code, HL.ChurchLevel_Code, HL.Church_Level,  UR.Is_Active, UR.Status
                            FROM tblUserRole UR
                            LEFT JOIN dfRole R ON R.Code = UR.Role_Code
                            LEFT JOIN tblHeadChurchLevels HL ON HL.Level_Code = UR.Level_Code
                            WHERE UR.Usercode = :Usercode
                                AND HL.Head_Code = :Head_Code AND HL.Is_Active = :Is_Active
                            """
                        ),
                        dict(
                            Usercode=user.Usercode,
                            Head_Code=self.current_user.HeadChurch_Code,
                            Is_Active=1,
                        ),
                    ).all()
                )
            else:
                user_roles = (
                    self.db.execute(
                        text(
                            """
                            SELECT UR.Role_Code, R.Role AS Role_Name, HL.Level_Code, HL.ChurchLevel_Code, HL.Church_Level,  UR.Is_Active, UR.Status
                            FROM tblUserRole UR
                            LEFT JOIN dfRole R ON R.Code = UR.Role_Code
                            LEFT JOIN tblHeadChurchLevels HL ON HL.Level_Code = UR.Level_Code
                            WHERE UR.Level_Code = :Level_Code
                                AND HL.Head_Code = :Head_Code AND HL.Is_Active = :Is_Active
                            """
                        ),
                        dict(
                            Level_Code=level_code,
                            Head_Code=self.current_user.HeadChurch_Code,
                            Is_Active=1,
                        ),
                    ).all()
                    if level_code != "CHU"
                    else self.db.execute(
                        text(
                            """
                            SELECT UR.Role_Code, R.Role AS Role_Name, HL.Level_Code, HL.ChurchLevel_Code, HL.Church_Level,  UR.Is_Active, UR.Status
                            FROM tblUserRole UR
                            LEFT JOIN dfRole R ON R.Code = UR.Role_Code
                            LEFT JOIN tblHeadChurchLevels HL ON HL.Level_Code = UR.Level_Code
                            WHERE HL.Head_Code = :Head_Code AND HL.Is_Active = :Is_Active
                            """
                        ),
                        dict(
                            Head_Code=self.current_user.HeadChurch_Code,
                            Is_Active=1,
                        ),
                    ).all()
                )
            return user_roles
        except Exception as err:
            raise err

    async def get_user_details(self, usercode: str, level_code: str):
        """Get User Details: accessible to only church admins of same/higher level/church."""
        try:
            # fetch user
            user = await self.get_user(usercode)
            # set user access
            set_user_access(
                self.current_user_access,
                headchurch_code=self.current_user.HeadChurch_Code,
                role_code=["ADM", "SAD"],
                # module_code=["MBSH"],
                # submodule_code=["MBRS"],
                access_type=["ED", "CR"],
            )

            # fetch user details
            user_details_row = self.db.execute(
                text(
                    """
                    SELECT U.*, UR.Role_Code, UR.Level_Code, M.First_Name, M.Last_Name, M.Title, M.Title2, MB.Branch_Code, C.Name AS Branch_Name, UR.Status, UR.Status_By, UR.Status_Date
                    FROM tblUser U
                    LEFT JOIN tblUserRole UR ON UR.Usercode = U.Usercode
                    LEFT JOIN tblMember M ON M.Code = U.Usercode
                    LEFT JOIN tblMemberBranch MB ON MB.Member_Code = U.Usercode
                    LEFT JOIN tblChurches C ON C.Code = MB.Branch_Code
                    WHERE U.Usercode = :Usercode
                    """
                ),
                dict(Usercode=user.Usercode),
            ).first()
            # check if user exists
            if user_details_row is None:
                raise Exception("User not found")
            # convert row to dict
            user_details_dict = user_details_row._asdict()
            user_details = UserDetails(**user_details_dict)

            # fetch user roles
            user_roles_rows = await self.get_user_roles(level_code, user.Usercode)
            if len(user_roles_rows) == 0:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"User Role not found for this Level: {level_code}",
                )
            # iterate and convert rows to dict
            user_roles = [UserRoles(**row._asdict()) for row in user_roles_rows]
            # set user roles attribute
            user_details.Roles = user_roles

            # fetch user submodules
            user_submodules_rows = await self.get_user_submodules(
                level_code, user.Usercode
            )
            # iterate and convert rows to dict
            user_submodules = [
                UserSubModules(**row._asdict()) for row in user_submodules_rows
            ]
            # set user submodules attribute
            user_details.SubModules = user_submodules

            return user_details
        except Exception as err:
            raise err

    async def get_users_details(self, level_code: str):
        """Get User Details: accessible to only church admins of same/higher level/church."""
        try:
            # set user access
            set_user_access(
                self.current_user_access,
                headchurch_code=self.current_user.HeadChurch_Code,
                role_code=["ADM", "SAD"],
                # module_code=["MBSH"],
                # submodule_code=["MBRS"],
                access_type=["ED", "CR"],
            )

            # fetch user details
            users_details_row = self.db.execute(
                text(
                    """
                    SELECT U.*, UR.Role_Code, UR.Level_Code, M.First_Name, M.Last_Name, M.Title, M.Title2, MB.Branch_Code, C.Name AS Branch_Name, UR.Status, UR.Status_By, UR.Status_Date
                    FROM tblUser U
                    LEFT JOIN tblUserRole UR ON UR.Usercode = U.Usercode
                    LEFT JOIN tblMember M ON M.Code = U.Usercode
                    LEFT JOIN tblMemberBranch MB ON MB.Member_Code = U.Usercode
                    LEFT JOIN tblChurches C ON C.Code = MB.Branch_Code
                    WHERE UR.Level_Code = :Level_Code
                    """
                ),
                dict(Level_Code=level_code),
            ).all()
            # check if user exists
            if users_details_row is None:
                raise Exception("User not found")

            users_details_list = []
            for row in users_details_row:
                # convert row to dict
                user_details_dict = row._asdict()
                user_details = UserDetails(**user_details_dict)

                # fetch user roles
                user_roles_rows = await self.get_user_roles(level_code)
                if len(user_roles_rows) == 0:
                    raise HTTPException(
                        status_code=status.HTTP_404_NOT_FOUND,
                        detail=f"User Role not found for this Level: {level_code}",
                    )
                # iterate and convert rows to dict
                user_roles = [UserRoles(**row._asdict()) for row in user_roles_rows]
                # set user roles attribute
                user_details.Roles = user_roles

                # fetch user submodules
                user_submodules_rows = await self.get_user_submodules(level_code)
                # iterate and convert rows to dict
                user_submodules = [
                    UserSubModules(**row._asdict()) for row in user_submodules_rows
                ]
                # set user submodules attribute
                user_details.SubModules = user_submodules

                users_details_list.append(user_details)

            return users_details_list
        except Exception as err:
            raise err

    async def assign_user_role(self, usercode: str, role_code: str, level_code: str):
        """Assign User Role: accessible to only church admins of same/higher level/church."""
        try:
            user = await self.get_user(usercode)
            # set user access
            set_user_access(
                self.current_user_access,
                headchurch_code=self.current_user.HeadChurch_Code,
                role_code=["ADM", "SAD"],
                module_code=["USRL"],
                submodule_code=["USER"],
                access_type=["ED"],
            )

            # assign user role
            self.db.execute(
                text(
                    """
                    INSERT INTO tblUserRole 
                        (Usercode, Role_Code, Level_Code, HeadChurch_Code)
                    VALUES 
                        (:Usercode, :Role_Code, :Level_Code, :HeadChurch_Code)
                    """
                ),
                dict(
                    Usercode=usercode,
                    Role_Code=role_code,
                    Level_Code=level_code,
                    HeadChurch_Code=user.HeadChurch_Code,
                ),
            )
            self.db.commit()
            return await self.get_user_details(usercode, level_code)
        except Exception as err:
            self.db.rollback()
            raise err


def get_user_services(
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
    current_user_access: Annotated[UserAccess, Depends(get_current_user_access)],
    member_services: Annotated[MemberServices, Depends(get_member_services)],
    db_current_user: Annotated[str, Depends(set_db_current_user)],
):
    return UserServices(db, current_user, current_user_access, member_services)
