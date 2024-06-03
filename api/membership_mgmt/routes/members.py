from typing import Annotated, Optional

from fastapi import APIRouter, status, Depends, Path  # type: ignore

from ...membership_mgmt.services import get_member_services, MemberServices
from ...membership_mgmt.models.members import (
    MemberIn,
    MemberResponse,
    MemberUpdate,
    MemberBranchExit,
    MemberBranchJoin,
    MemberBranchResponse,
    MemberBranchUpdate,
)

members_router = APIRouter(prefix="/members", tags=["Members Sub-Module Operations"])
"""
### Member Routes
- Get All Members
- Get Member by Code
- Get Current User Member
- Get Members by Church Code
- Get Members by Level Code
- Update Member by Code
- Update Current User Member
"""

members_adm_router = APIRouter(
    prefix="/admin/members", tags=["Members Sub-Module Operations - Admin only"]
)
"""
### Member Routes
- Create New Member
- Activate Member by Code
- Deactivate Member by Code
"""


member_church_router = APIRouter(
    prefix="/member_church", tags=["Member Church Sub-Module Operations"]
)
"""
### Member Church Routes
- Get Member's All Church
- Get Member's Church by Code
"""


member_church_adm_router = APIRouter(
    prefix="/admin/member_church",
    tags=["Member Church Sub-Module Operations - Admin only"],
)
"""
### Member Church Admin Routes
- Exit Member From All Churches
- Exit Memeber From Church
- Join Member To Church
"""


# Create New Member
@members_adm_router.post(
    "/{branch_code}/create",
    status_code=status.HTTP_201_CREATED,
    name="Create New Member",
    response_model=MemberResponse,
)
async def create_new_member(
    member: MemberIn,
    branch_code: Annotated[str, Path(..., description="code of the church branch")],
    member_services: Annotated[MemberServices, Depends(get_member_services)],
):
    new_member = await member_services.create_new_member(member, branch_code)
    # set response body
    response = dict(
        data=new_member,
        status_code=status.HTTP_201_CREATED,
        message=f"Successfully created new Member: '{new_member.First_Name}', with code: '{new_member.Member_Code}'",
    )
    return response


# Deactivate Member by Code
@members_adm_router.patch(
    "/{member_code}/deactivate",
    name="Deactivate Member by Code",
    response_model=MemberResponse,
)
async def deactivate_member(
    member_code: Annotated[
        str, Path(..., description="code of the member to be deactivated")
    ],
    member_church: MemberBranchExit,
    member_services: Annotated[MemberServices, Depends(get_member_services)],
):
    deactivated_member = await member_services.deactivate_member_by_code(
        member_code, member_church
    )
    # set response body
    response = dict(
        data=deactivated_member,
        status_code=status.HTTP_200_OK,
        message=f"Successfully deactivated Member: '{deactivated_member.First_Name}' with code: '{deactivated_member.Member_Code}'",
    )
    return response


# Activate Member by Code
@members_adm_router.patch(
    "/{member_code}/activate",
    name="Activate Member by Code",
    response_model=MemberResponse,
)
async def activate_member(
    member_code: Annotated[
        str, Path(..., description="code of the member to be activated")
    ],
    member_church: MemberBranchUpdate,
    member_services: Annotated[MemberServices, Depends(get_member_services)],
):
    activated_member = await member_services.activate_member_by_code(
        member_code, member_church
    )
    # set response body
    response = dict(
        data=activated_member,
        status_code=status.HTTP_200_OK,
        message=f"Successfully activated Member: '{activated_member.First_Name}' with code: '{activated_member.Member_Code}'",
    )
    return response


# Get All Members
@members_router.get(
    "/",
    name="Get All Members",
    response_model=MemberResponse,
)
async def get_all_members(
    member_services: Annotated[MemberServices, Depends(get_member_services)],
):
    members = await member_services.get_all_members()
    # set response body
    response = dict(
        data=members,
        status_code=status.HTTP_200_OK,
        message=f"Successfully fetched {len(members)} Members",
    )
    return response


# Get Member by Code
@members_router.get(
    "/{code}",
    name="Get Member by Code",
    response_model=MemberResponse,
)
async def get_member_by_code(
    code: str,
    member_services: Annotated[MemberServices, Depends(get_member_services)],
):
    member = await member_services.get_member_by_code(code)
    # set response body
    response = dict(
        data=member,
        status_code=status.HTTP_200_OK,
        message=f"Successfully fetched Member: '{member.First_Name}' with code: '{member.Member_Code}'",
    )
    return response


# Get Current User Member
@members_router.get(
    "/current",
    name="Get Current User Member",
    response_model=MemberResponse,
)
async def get_current_user_member(
    member_services: Annotated[MemberServices, Depends(get_member_services)],
):
    member = await member_services.get_current_user_member()
    # set response body
    response = dict(
        data=member,
        status_code=status.HTTP_200_OK,
        message=f"Successfully retrieved Member: '{member.First_Name}' with code: '{member.Member_Code}'",
    )
    return response


# Get Members by Church Code
@members_router.get(
    "/church/{church_code}",
    name="Get Members by Church Code",
    response_model=MemberResponse,
)
async def get_members_by_church(
    church_code: str,
    member_services: Annotated[MemberServices, Depends(get_member_services)],
):
    members = await member_services.get_members_by_church(church_code)
    # set response body
    response = dict(
        data=members,
        status_code=status.HTTP_200_OK,
        message=f"Successfully retrieved {len(members)} Members",
    )
    return response


# Get Members by Level Code
@members_router.get(
    "/level/{level_code}",
    name="Get Members by Level Code",
    response_model=MemberResponse,
)
async def get_members_by_level(
    level_code: str,
    member_services: Annotated[MemberServices, Depends(get_member_services)],
):
    members = await member_services.get_members_by_level(level_code)
    # set response body
    response = dict(
        data=members,
        status_code=status.HTTP_200_OK,
        message=f"Successfully retrieved {len(members)} Members",
    )
    return response


# Update Member by Code
@members_router.put(
    "/{code}/update",
    name="Update Member by Code",
    response_model=MemberResponse,
)
async def update_member_by_code(
    member_code: str,
    member: MemberUpdate,
    member_services: Annotated[MemberServices, Depends(get_member_services)],
):
    updated_member = await member_services.update_member_by_code(member_code, member)
    # set response body
    response = dict(
        data=updated_member,
        status_code=status.HTTP_200_OK,
        message=f"Successfully updated Member: '{updated_member.First_Name}' with code: '{updated_member.Member_Code}'",
    )
    return response


# Update Current User Member
@members_router.put(
    "/current/update",
    name="Update Current User Member",
    response_model=MemberResponse,
)
async def update_current_user_member(
    member: MemberUpdate,
    member_services: Annotated[MemberServices, Depends(get_member_services)],
):
    updated_member = await member_services.update_current_user_member(member)
    # set response body
    response = dict(
        data=updated_member,
        status_code=status.HTTP_200_OK,
        message=f"Successfully updated Member: '{updated_member.First_Name}' with code: '{updated_member.Member_Code}'",
    )
    return response


# Get Member Church by Code
@member_church_router.get(
    "/{member_code}/church/{church_code}",
    status_code=status.HTTP_200_OK,
    name="Get Member Church by Code",
    response_model=MemberBranchResponse,
)
async def get_member_church_by_code(
    member_code: str,
    church_code: str,
    member_services: Annotated[MemberServices, Depends(get_member_services)],
    is_active: Optional[bool] = None,
):
    member_church = await member_services.get_member_church_by_member_code(
        member_code, church_code, is_active
    )
    # set response body
    response = dict(
        data=member_church,
        status_code=status.HTTP_200_OK,
        message=f"Successfully retrieved '{member_church.Member_Code}' Member's Church'",
    )
    return response


# Get Member's All Churches
@member_church_router.get(
    "/{member_code}/churches",
    status_code=status.HTTP_200_OK,
    name="Get Member's All Churches",
    response_model=MemberBranchResponse,
)
async def get_member_all_churches(
    member_code: str,
    member_services: Annotated[MemberServices, Depends(get_member_services)],
    is_active: Optional[bool] = None,
):
    member_churches = await member_services.get_member_all_churches_by_code(
        member_code, is_active
    )
    # set response body
    response = dict(
        data=member_churches,
        status_code=status.HTTP_200_OK,
        message=f"Successfully retrieved '{len(member_churches)}' Member's All Churches",
    )
    return response


# Exit Member From Church
@member_church_adm_router.patch(
    "/church/{member_code}/exit",
    status_code=status.HTTP_200_OK,
    name="Exit Member From Church",
    response_model=MemberResponse,
)
async def exit_member_from_church(
    member_code: Annotated[str, Path(..., description="code of member to be exited")],
    member_exit: MemberBranchExit,
    member_services: Annotated[MemberServices, Depends(get_member_services)],
):
    exited_member = await member_services.exit_member_from_church(
        member_code, member_exit
    )
    # set response body
    response = dict(
        data=exited_member,
        status_code=status.HTTP_200_OK,
        message=f"Successfully exited Member: '{exited_member.Member_Code}' - '{exited_member.First_Name}' from '{member_exit.Church_Code}' Church",
    )
    return response


# Exit Member From All Churches
@member_church_adm_router.patch(
    "/church/exit_all",
    status_code=status.HTTP_200_OK,
    name="Exit Member From All Churches",
    response_model=MemberResponse,
)
async def exit_member_from_all_churches(
    member_code: str,
    member_services: Annotated[MemberServices, Depends(get_member_services)],
):
    exited_member = await member_services.exit_member_from_all_churches(member_code)
    # set response body
    response = dict(
        data=exited_member,
        status_code=status.HTTP_200_OK,
        message=f"Successfully exited Member: '{exited_member.Member_Code}' - '{exited_member.First_Name}' from all Churches",
    )
    return response


# Join Member To Church
@member_church_adm_router.patch(
    "/church/{member_code}/join",
    status_code=status.HTTP_200_OK,
    name="Join Member To Church",
    response_model=MemberResponse,
)
async def join_member_to_church(
    member_code: Annotated[
        str, Path(..., description="code of the member to be joined")
    ],
    member_join: MemberBranchJoin,
    member_services: Annotated[MemberServices, Depends(get_member_services)],
):
    joined_member = await member_services.join_member_to_church(
        member_code, member_join
    )
    # set response body
    response = dict(
        data=joined_member,
        status_code=status.HTTP_200_OK,
        message=f"Successfully joined Member: '{joined_member.Member_Code}' - '{joined_member.First_Name}' to '{member_join.Church_Code}' Church",
    )
    return response
