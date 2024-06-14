# from datetime import datetime
# from typing import Annotated, Optional

# from .members import MemberServices, get_member_services
# from fastapi import Depends, HTTPException, status  # type: ignore
# from pydantic import ValidationError  # type: ignore
# from sqlalchemy import text  # type: ignore
# from sqlalchemy.exc import SQLAlchemyError  # type: ignore
# from sqlalchemy.orm import Session  # type: ignore

# # from sqlalchemy.ext.asyncio import AsyncSession  # type: ignore

# from ...authentication.models.auth import User, UserAccess
# from ...hierarchy_mgmt.services import get_church_services, ChurchServices
# from ...membership_mgmt.models.members import (
#     MemberBranchExitIn,
#     MemberBranchJoinIn,
#     MemberIn,
#     MemberUpdate,
# )
# from ...common.database import get_db
# from ...common.utils import (
#     check_duplicate_entry,
#     validate_code_type,
#     get_level,
#     set_user_access,
# )
# from ...common.dependencies import (
#     get_current_user,
#     get_current_user_access,
#     set_db_current_user,
# )
# from ...hierarchy_mgmt.services.church_leads import church_recursive_cte


# class MemberBranchServices:
#     """
#     ### Member Service methods
#     - Create New Member
#     - Get All Members
#     - Get Member by Code
#     - Get Current User Member
#     - Get Members by Church
#     - Get Members by Level
#     - Update Member by Code
#     - Update Current User Member
#     - Activate Member by Code
#     - Deactivate Member by Code

#     """

#     def __init__(
#         self,
#         db: Session,
#         current_user: User,
#         current_user_access: UserAccess,
#         church_services: ChurchServices,
#         member_services: MemberServices,
#     ):
#         self.db = db
#         self.current_user = current_user
#         self.current_user_access = current_user_access
#         self.church_services = church_services
#         self.member_services = member_services

#     async def get_member_branches(
#         self,
#         member_code: str,
#         branch_code: Optional[str] = None,
#         is_active: Optional[bool] = None,
#     ):
#         """Get Member Branches: accessible to only church admins in the same/higher level/church."""
#         try:
#             member = await self.member_services.get_member_by_code(member_code)
#             level = get_level("BRN", self.current_user.HeadChurch_Code, self.db)

#             # set user access
#             set_user_access(
#                 self.current_user_access,
#                 headchurch_code=self.current_user.HeadChurch_Code,
#                 church_code=member.Branch_Code,
#                 level_no=level.Level_No - 1,
#                 role_code=["ADM", "SAD"],
#                 module_code=["ALLM", "MBSH"],
#                 submodule_code=["ALLS", "MBRS"],
#                 access_type=["ED", "VW", "CR"],
#             )
#             # fetch member churches
#             if is_active is not None:
#                 if is_active == 1:
#                     if branch_code:
#                         msg = "returns current specific member-branch or none if branch is not the current"
#                     else:
#                         msg = "returns current member-branch"
#                 else:
#                     if branch_code:
#                         msg = "returns previous specific member-branches"
#                     else:
#                         msg = "returns previous member-branches"
#             else:
#                 if branch_code:
#                     msg = "returns all specific member-branches"
#                 else:
#                     msg = "returns all member-branches"

#             print(f"msg: {msg}")

#             if is_active is not None:
#                 if branch_code:
#                     member_branches = self.db.execute(
#                         text(
#                             """
#                         SELECT
#                             MC.*, M.First_Name, M.Middle_Name, M.Last_Name, C.Name AS Branch_Name
#                         FROM tblMemberBranch MC
#                             LEFT JOIN tblMember M ON M.Code = MC.Member_Code
#                             LEFT JOIN tblChurches C ON C.Code = MC.Branch_Code
#                         WHERE MC.Member_Code = :Member_Code AND MC.HeadChurch_Code = :HeadChurch_Code
#                             AND MC.Is_Active = :Is_Active AND MC.Branch_Code = :Branch_Code
#                         ORDER BY MC.Join_Date;
#                         """
#                         ),
#                         dict(
#                             Member_Code=member_code,
#                             HeadChurch_Code=self.current_user.HeadChurch_Code,
#                             Is_Active=is_active,
#                             Branch_Code=branch_code,
#                         ),
#                     ).all()
#                 else:
#                     member_branches = self.db.execute(
#                         text(
#                             """
#                         SELECT
#                             MC.*, M.First_Name, M.Middle_Name, M.Last_Name, C.Name AS Branch_Name
#                         FROM tblMemberBranch MC
#                             LEFT JOIN tblMember M ON M.Code = MC.Member_Code
#                             LEFT JOIN tblChurches C ON C.Code = MC.Branch_Code
#                         WHERE MC.Member_Code = :Member_Code AND MC.HeadChurch_Code = :HeadChurch_Code
#                             AND MC.Is_Active = :Is_Active
#                         ORDER BY MC.Join_Date;
#                         """
#                         ),
#                         dict(
#                             Member_Code=member_code,
#                             HeadChurch_Code=self.current_user.HeadChurch_Code,
#                             Is_Active=is_active,
#                         ),
#                     ).all()
#             else:
#                 if branch_code:
#                     member_branches = self.db.execute(
#                         text(
#                             """
#                             SELECT
#                                 MC.*, M.First_Name, M.Middle_Name, M.Last_Name, C.Name AS Branch_Name
#                             FROM tblMemberBranch MC
#                                 LEFT JOIN tblMember M ON M.Code = MC.Member_Code
#                                 LEFT JOIN tblChurches C ON C.Code = MC.Branch_Code
#                             WHERE MC.Member_Code = :Member_Code AND MC.HeadChurch_Code = :HeadChurch_Code
#                                 AND MC.Branch_Code = :Branch_Code
#                             ORDER BY MC.Join_Date;
#                             """
#                         ),
#                         dict(
#                             Member_Code=member_code,
#                             HeadChurch_Code=self.current_user.HeadChurch_Code,
#                             Branch_Code=branch_code,
#                         ),
#                     ).all()
#                 else:
#                     member_branches = self.db.execute(
#                         text(
#                             """
#                         SELECT
#                             MC.*, M.First_Name, M.Middle_Name, M.Last_Name, C.Name AS Branch_Name
#                         FROM tblMemberBranch MC
#                             LEFT JOIN tblMember M ON M.Code = MC.Member_Code
#                             LEFT JOIN tblChurches C ON C.Code = MC.Branch_Code
#                         WHERE MC.Member_Code = :Member_Code AND MC.HeadChurch_Code = :HeadChurch_Code
#                         ORDER BY MC.Join_Date;
#                         """
#                         ),
#                         dict(
#                             Member_Code=member_code,
#                             HeadChurch_Code=self.current_user.HeadChurch_Code,
#                         ),
#                     ).all()
#             if not member_branches:
#                 raise HTTPException(
#                     status_code=status.HTTP_404_NOT_FOUND,
#                     detail=(
#                         "No"
#                         + (
#                             (" current" if is_active == 1 else " previous")
#                             if is_active is not None
#                             else ""
#                         )
#                         + f" Member-Branch"
#                         + (" " if branch_code is None else f" '{branch_code.upper()}'")
#                         + f" records found for member: '{member_code.upper()}'."
#                     ),
#                 )
#             return member_branches
#         except Exception as err:
#             raise err

#     async def exit_member_from_church(
#         self, member_code, member_exit: MemberBranchExitIn
#     ):
#         """Exit Member From Church: accessible to only church admins in the same/higher level/church."""
#         try:
#             # validate member and church
#             member = await self.member_services.get_member_by_code(member_code)
#             await self.church_services.get_church_by_id_code(member_exit.Branch_Code)
#             await self.get_member_branches(member.Code, member_exit.Branch_Code, True)
#             level = get_level(
#                 member_exit.Branch_Code, self.current_user.HeadChurch_Code, self.db
#             )
#             # set user access
#             set_user_access(
#                 self.current_user_access,
#                 headchurch_code=self.current_user.HeadChurch_Code,
#                 church_code=member_exit.Branch_Code,
#                 level_no=level.Level_No - 1,
#                 role_code=["ADM", "SAD"],
#                 module_code=["ALLM", "MBSH"],
#                 submodule_code=["ALLS", "MBRS"],
#                 access_type=["ED"],
#             )
#             # exit member from church
#             self.db.execute(
#                 text(
#                     """
#                     UPDATE tblMemberBranch
#                     SET Exit_Date = :Exit_Date, Exit_Note = :Exit_Note, Exit_Code = :Exit_Code, Is_Active = :Is_Active, Modified_By = :Modified_By
#                     WHERE Member_Code = :Member_Code AND Branch_Code = :Branch_Code
#                         AND HeadChurch_Code = :HeadChurch_Code AND Is_Active = :Is_Active2;
#                     """
#                 ),
#                 dict(
#                     Exit_Date=(
#                         member_exit.Exit_Date
#                         if member_exit.Exit_Date
#                         else datetime.now()
#                     ),
#                     Exit_Note=member_exit.Exit_Note,
#                     Exit_Code=member_exit.Exit_Code,
#                     Modified_By=self.current_user.Usercode,
#                     Member_Code=member.Code,
#                     Branch_Code=member_exit.Branch_Code,
#                     HeadChurch_Code=self.current_user.HeadChurch_Code,
#                     Is_Active=0,
#                     Is_Active2=1,
#                 ),
#             )
#             self.db.commit()
#             return await self.get_member_branches(
#                 member_exit.Member_Code, member_exit.Branch_Code, True
#             )
#         except Exception as err:
#             self.db.rollback()
#             raise err

#     async def exit_member_from_all_branches(self, member_code: str):
#         """Exit Member From All Churches: accessible to only church admins in higher level/church."""
#         try:
#             # validate member
#             await self.member_services.get_member_by_code(member_code)
#             # set user access
#             set_user_access(
#                 self.current_user_access,
#                 headchurch_code=self.current_user.HeadChurch_Code,
#                 level_no=1,
#                 role_code=["ADM", "SAD"],
#                 module_code=["ALLM", "MBSH"],
#                 submodule_code=["ALLS", "MBRS"],
#                 access_type=["ED"],
#             )
#             # exit member from all churches
#             self.db.execute(
#                 text(
#                     """
#                     UPDATE tblMemberBranch
#                     SET Exit_Date = :Exit_Date, Exit_Note = :Exit_Note, Exit_Code = :Exit_Code, Is_Active = :Is_Active, Modified_By = :Modified_By
#                     WHERE Member_Code = :Member_Code AND HeadChurch_Code = :HeadChurch_Code AND Is_Active = :Is_Active2;
#                     """
#                 ),
#                 dict(
#                     Exit_Date=datetime.now(),
#                     Exit_Note="Member exited from all churches",
#                     Exit_Code="OTH",
#                     Modified_By=self.current_user.Usercode,
#                     Member_Code=member_code,
#                     HeadChurch_Code=self.current_user.HeadChurch_Code,
#                     Is_Active=0,
#                     Is_Active2=1,
#                 ),
#             )
#             self.db.commit()
#             member = await self.member_services.get_member_by_code(member_code)
#             return member
#         except Exception as err:
#             self.db.rollback()
#             raise err

#     async def join_member_to_church(self, member_code, member_join: MemberBranchJoinIn):
#         """Join Member To Church: accessible to only church admins in the same/higher level/church."""
#         try:
#             level = get_level(
#                 member_join.Branch_Code, self.current_user.HeadChurch_Code, self.db
#             )
#             # set user access
#             set_user_access(
#                 self.current_user_access,
#                 headchurch_code=self.current_user.HeadChurch_Code,
#                 church_code=member_join.Branch_Code,
#                 level_no=level.Level_No - 1,
#                 role_code=["ADM", "SAD"],
#                 module_code=["ALLM", "MBSH"],
#                 submodule_code=["ALLS", "MBRS"],
#                 access_type=["ED"],
#             )
#             # validate member and church
#             member = await self.member_services.get_member_by_code(member_code)
#             await self.church_services.get_church_by_id_code(member_join.Branch_Code)
#             member_branch = await self.get_member_branches(
#                 member_code, member.Branch_Code, is_active=True
#             )
#             # checks if member is already a member of a church
#             if member_branch:
#                 raise HTTPException(
#                     status_code=status.HTTP_400_BAD_REQUEST,
#                     detail="Member is already a member of a church",
#                 )
#             # check and exit member from possible member church
#             await self.exit_member_from_all_branches(member.Code)
#             # join member to church
#             self.db.execute(
#                 text(
#                     """
#                     INSERT INTO tblMemberBranch
#                     (Member_Code, Branch_Code, Level_Code, HeadChurch_Code, Join_Date, Join_Code, Join_Note, Is_Active, Created_By)
#                     VALUES
#                     (:Member_Code, :Branch_Code, :Level_Code, :HeadChurch_Code, :Join_Date, :Join_Code, :Join_Note, :Is_Active, :Created_By);
#                     """
#                 ),
#                 dict(
#                     Member_Code=member.Code,
#                     Branch_Code=member_join.Branch_Code,
#                     HeadChurch_Code=self.current_user.HeadChurch_Code,
#                     Join_Date=(
#                         member_join.Join_Date
#                         if member_join.Join_Date
#                         else datetime.now()
#                     ),
#                     Join_Code=member_join.Join_Code,
#                     Join_Note=member_join.Join_Note,
#                     Is_Active=1,
#                     Created_By=self.current_user.Usercode,
#                 ),
#             )
#             self.db.commit()
#             return await self.get_member_branches(
#                 member.Code, member_join.Branch_Code, True
#             )
#         except Exception as err:
#             self.db.rollback()
#             raise err

#     async def make_member_clergy(self, member_code):
#         pass


# def get_member_branch_services(
#     db: Annotated[Session, Depends(get_db)],
#     current_user: Annotated[User, Depends(get_current_user)],
#     current_user_access: Annotated[UserAccess, Depends(get_current_user_access)],
#     church_services: Annotated[ChurchServices, Depends(get_church_services)],
#     member_services: Annotated[MemberServices, Depends(get_member_services)],
#     db_current_user: Annotated[str, Depends(set_db_current_user)],
# ):
#     return MemberBranchServices(
#         db, current_user, current_user_access, church_services, member_services
#     )
