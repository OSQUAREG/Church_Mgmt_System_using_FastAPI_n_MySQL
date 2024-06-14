# from typing import Annotated, Optional

# from ..services.member_branch import MemberBranchServices, get_member_branch_services
# from fastapi import APIRouter, status, Depends, Path  # type: ignore

# from ...membership_mgmt.services import get_member_services, MemberServices
# from ...membership_mgmt.models.members import (
#     MemberBranchExitIn,
#     MemberBranchJoinIn,
#     MemberIn,
#     MemberResponse,
#     MemberUpdate,
#     MemberBranchResponse,
#     MemberBranchUpdate,
# )

# member_church_router = APIRouter(
#     prefix="/member_church", tags=["Member Church Sub-Module Operations"]
# )
# """
# ### Member Church Routes
# - Get Member's All Church
# - Get Member's Church by Code
# """


# member_church_adm_router = APIRouter(
#     prefix="/admin/member_church",
#     tags=["Member Church Sub-Module Operations - Admin only"],
# )
# """
# ### Member Church Admin Routes
# - Exit Member From All Churches
# - Exit Memeber From Church
# - Join Member To Church

# """


# # Get Current Member-Branch
# @member_church_router.get(
#     "/{member_code}/branch",
#     status_code=status.HTTP_200_OK,
#     name="Get Member Current Branch",
#     response_model=MemberBranchResponse,
# )
# async def get_member_current_branch(
#     member_code: str,
#     member_branch_services: Annotated[
#         MemberBranchServices, Depends(get_member_branch_services)
#     ],
# ):
#     member_church = await member_branch_services.get_member_branches(
#         member_code, is_active=True
#     )
#     # set response body
#     response = dict(
#         data=member_church,
#         status_code=status.HTTP_200_OK,
#         message=f"Successfully retrieved '{member_church.Member_Code}' Member's Current Branch'",
#     )
#     return response


# # Get Specific Member-Branch by Code
# @member_church_router.get(
#     "/{member_code}/branch/{branch_code}",
#     status_code=status.HTTP_200_OK,
#     name="Get Specific Member-Branch by Code",
#     response_model=MemberBranchResponse,
# )
# async def get_member_branch_by_code(
#     member_code: str,
#     branch_code: str,
#     member_branch_services: Annotated[
#         MemberBranchServices, Depends(get_member_branch_services)
#     ],
#     is_active: Optional[bool] = None,
# ):
#     member_branches = await member_branch_services.get_member_branches(
#         member_code, branch_code, is_active=is_active
#     )
#     # mc_code = [member_branch.Member_Code for member_branch in member_branches]
#     # member_code = ", ".join(mc_code)[0:18]
#     # set response body
#     response = dict(
#         data=member_branches,
#         status_code=status.HTTP_200_OK,
#         message=f"Successfully retrieved {len(member_branches)}"
#         + (
#             (" current" if is_active == 1 else " previous")
#             if is_active is not None
#             else ""
#         )
#         + f" Member-Branch '{branch_code.upper()}'"
#         + f" records for Member: '{member_code.upper()}'",
#     )
#     return response


# # Get All Member-Branches by Member Code
# @member_church_router.get(
#     "/{member_code}/branches",
#     status_code=status.HTTP_200_OK,
#     name="Get All Member-Branches by Member Code",
#     response_model=MemberBranchResponse,
# )
# async def get_member_all_branches(
#     member_code: str,
#     member_branch_services: Annotated[MemberBranchServices, Depends(get_member_branch_services)],
#     is_active: Optional[bool] = None,
# ):
#     member_branches = await member_branch_services.get_member_branches(
#         member_code, is_active=is_active
#     )
#     # set response body
#     response = dict(
#         data=member_branches,
#         status_code=status.HTTP_200_OK,
#         message=f"Successfully retrieved {len(member_branches)}"
#         + (
#             (" current" if is_active == 1 else " previous")
#             if is_active is not None
#             else ""
#         )
#         + (
#             " Member-Branch records"
#             if {len(member_branches) > 1}
#             else " Member-Branch records"
#         )
#         + f" for Member: '{member_code.upper()}'",
#     )
#     return response


# # Exit Member From Church
# @member_church_adm_router.patch(
#     "/{member_code}/exit",
#     status_code=status.HTTP_200_OK,
#     name="Exit Member From Church",
#     response_model=MemberResponse,
# )
# async def exit_member_from_church(
#     member_code: Annotated[str, Path(..., description="code of member to be exited")],
#     member_exit: MemberBranchExitIn,
#     member_branch_services: Annotated[MemberBranchServices, Depends(get_member_branch_services)],
# ):
#     exited_member = await member_branch_services.exit_member_from_church(
#         member_code, member_exit
#     )
#     # set response body
#     response = dict(
#         data=exited_member,
#         status_code=status.HTTP_200_OK,
#         message=f"Successfully exited Member: '{exited_member.Title} {exited_member.Title2} {exited_member.First_Name} {exited_member.Last_Name} ({exited_member.Code})' from '{member_exit.Church_Code}' Church",
#     )
#     return response


# # Exit Member From All Churches
# @member_church_adm_router.patch(
#     "/{member_code}/exit_all",
#     status_code=status.HTTP_200_OK,
#     name="Exit Member From All Churches",
#     response_model=MemberResponse,
# )
# async def exit_member_from_all_branches(
#     member_code: str,
#     member_branch_services: Annotated[MemberBranchServices, Depends(get_member_branch_services)],
# ):
#     exited_member = await member_branch_services.exit_member_from_all_branches(member_code)
#     # set response body
#     response = dict(
#         data=exited_member,
#         status_code=status.HTTP_200_OK,
#         message=f"Successfully exited Member: '{exited_member.Title} {exited_member.Title2} {exited_member.First_Name} {exited_member.Last_Name} ({exited_member.Code})' from all Churches",
#     )
#     return response


# # Join Member To Church
# @member_church_adm_router.patch(
#     "/{member_code}/join",
#     status_code=status.HTTP_200_OK,
#     name="Join Member To Church",
#     response_model=MemberResponse,
# )
# async def join_member_to_church(
#     member_code: Annotated[
#         str, Path(..., description="code of the member to be joined")
#     ],
#     member_join: MemberBranchJoinIn,
#     member_branch_services: Annotated[MemberBranchServices, Depends(get_member_branch_services)],
# ):
#     joined_member = await member_branch_services.join_member_to_church(
#         member_code, member_join
#     )
#     # set response body
#     response = dict(
#         data=joined_member,
#         status_code=status.HTTP_200_OK,
#         message=f"Successfully joined Member: '{joined_member.Title} {joined_member.Title2} {joined_member.First_Name} {joined_member.Last_Name} ({joined_member.Code})' to '{joined_member.Branch_Code}' Church",
#     )
#     return response
