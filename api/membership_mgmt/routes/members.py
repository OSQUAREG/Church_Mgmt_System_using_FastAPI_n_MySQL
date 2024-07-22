from typing import Annotated, Optional

from fastapi import APIRouter, status, Depends, Path  # type: ignore

from ...membership_mgmt.services import get_member_services, MemberServices
from ...membership_mgmt.models.members import (
    MemberBranchExitIn,
    MemberBranchJoinIn,
    MemberChurchHierarchyResponse,
    MemberIn,
    MemberResponse,
    MemberUpdate,
    MemberBranchResponse,
    MemberBranchUpdate,
)
from ...swagger_doc import tags

members_router = APIRouter(
    prefix="/members",
    tags=[f"{tags['members']['module']}: {tags['members']['submodule']}"],
)

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
    prefix="/admin/members",
    tags=[f"{tags['members']['module']}: {tags['members']['submodule']}: Admin only"],
)
"""
### Member Routes
- Create New Member
- Activate Member by Code
- Deactivate Member by Code
- Promote Member to Clergy
- Demote Member from Clergy
"""


member_branch_router = APIRouter(
    prefix="/member_branch",
    tags=[f"{tags['member_branch']['module']}: {tags['member_branch']['submodule']}"],
)
"""
### Member Branch Routes
- Get Member Current Branch
- Get Member-Branch by Code
- Get Member All Branches
- Get Member Church Hierarchy by Member Code
"""


member_branch_adm_router = APIRouter(
    prefix="/admin/member_branch",
    tags=[
        f"{tags['member_branch']['module']}: {tags['member_branch']['submodule']}: Admin only"
    ],
)
"""
### Member Branch Admin Routes
- Exit Member From All Churches
- Exit Memeber From Church
- Join Member To Church
"""


# Create New Member
@members_adm_router.post(
    "/create",
    status_code=status.HTTP_201_CREATED,
    name="Create New Member",
    summary="Create New Member",
    description="## Create New Member",
    response_model=MemberResponse,
)
async def create_new_member(
    member: MemberIn,
    member_services: Annotated[MemberServices, Depends(get_member_services)],
):
    new_member = await member_services.create_new_member(member)
    # set response body
    response = dict(
        data=new_member,
        status_code=status.HTTP_201_CREATED,
        message=(
            f"Successfully created new member: '{new_member.Title} {new_member.Title2} {new_member.First_Name} {new_member.Last_Name} ({new_member.Code})"
            + f" / (Clergy Code: {new_member.Clergy_Code})'"
            if new_member.Clergy_Code
            else "'"
        ),
    )
    return response


# Deactivate Member by Code
@members_adm_router.patch(
    "/{member_code}/deactivate",
    name="Deactivate Member",
    summary="Deactivate Member by Code",
    description="## Deactivate Member by Code",
    response_model=MemberResponse,
)
async def deactivate_member(
    member_code: Annotated[
        str, Path(..., description="code of the member to be deactivated")
    ],
    member_services: Annotated[MemberServices, Depends(get_member_services)],
):
    deactivated_member = await member_services.deactivate_member_by_code(member_code)
    # set response body
    response = dict(
        data=deactivated_member,
        status_code=status.HTTP_200_OK,
        message=f"Successfully deactivated Member: '{deactivated_member.Title} {deactivated_member.Title2} {deactivated_member.First_Name} {deactivated_member.Last_Name} ({deactivated_member.Code})'",
    )
    return response


# Activate Member by Code
@members_adm_router.patch(
    "/{member_code}/activate",
    name="Activate Member",
    summary="Activate Member by Code",
    description="## Activate Member by Code",
    response_model=MemberResponse,
)
async def activate_member(
    member_code: Annotated[
        str, Path(..., description="code of the member to be activated")
    ],
    member_branch: MemberBranchJoinIn,
    member_services: Annotated[MemberServices, Depends(get_member_services)],
):
    activated_member = await member_services.activate_member_by_code(
        member_code, member_branch
    )
    # set response body
    response = dict(
        data=activated_member,
        status_code=status.HTTP_200_OK,
        message=f"Successfully activated Member: '{activated_member.Title} {activated_member.Title2} {activated_member.First_Name} ({activated_member.Code})' in the church: '{activated_member.Branch_Code}'",
    )
    return response


@members_adm_router.patch(
    "/{member_code_id}/promote_to_clergy",
    status_code=status.HTTP_200_OK,
    name="Promote Member to Clergy",
    summary="Promote Member to Clergy",
    description="## Promote Member to Clergy",
    response_model=MemberResponse,
)
async def promote_member_to_clergy(
    member_code_id: Annotated[
        str, Path(..., description="code of the member to be promoted to clergy")
    ],
    member_services: Annotated[MemberServices, Depends(get_member_services)],
):
    promoted_member = await member_services.promote_member_to_clergy(member_code_id)
    # set response body
    response = dict(
        data=promoted_member,
        status_code=status.HTTP_200_OK,
        message=f"Successfully promoted Member: '{promoted_member.Title} {promoted_member.Title2} {promoted_member.First_Name} {promoted_member.Last_Name} ({promoted_member.Code})' to Clergy ({promoted_member.Clergy_Code})",
    )
    return response


@members_adm_router.patch(
    "/{member_code_id}/demote_from_clergy",
    status_code=status.HTTP_200_OK,
    name="Demote Member from Clergy",
    summary="Demote Member from Clergy",
    description="## Demote Member from Clergy",
    response_model=MemberResponse,
)
async def demote_member_from_clergy(
    member_code_id: Annotated[
        str, Path(..., description="code of the member to be demoted from clergy")
    ],
    member_services: Annotated[MemberServices, Depends(get_member_services)],
):
    demoted_member = await member_services.demote_member_from_clergy(member_code_id)
    # set response body
    response = dict(
        data=demoted_member,
        status_code=status.HTTP_200_OK,
        message=f"Successfully demoted Member: '{demoted_member.Title} {demoted_member.Title2} {demoted_member.First_Name} {demoted_member.Last_Name} ({demoted_member.Code})' from Clergy",
    )
    return response


# Get All Members
@members_router.get(
    "/",
    name="Get All Members",
    summary="Get All Members",
    description="## Retrieve All Members",
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
        message=f"Successfully retrived {len(members)} Members",
    )
    return response


# Get Current User Member
@members_router.get(
    "/current",
    name="Get Current User Member",
    summary="Get Current User Member",
    description="## Get Current User Member",
    response_model=MemberResponse,
)
async def get_current_user_member(
    member_services: Annotated[MemberServices, Depends(get_member_services)],
):
    member = await member_services.get_current_user_member()
    # set response body
    response = dict(
        data=member,
        status_code=status.HTTP_200_OK if member else status.HTTP_204_NO_CONTENT,
        message=(
            f"Successfully retrieved Member: '{member.Title} {member.Title2} {member.First_Name} {member.Last_Name} ({member.Code})'"
            if member
            else "Current User not a church member"
        ),
    )
    return response


# Get Member by Code
@members_router.get(
    "/{member_code_id}",
    name="Get Member",
    summary="Get Member by Code or Id",
    description="## Retrieve Member by Code or Id",
    response_model=MemberResponse,
)
async def get_member_by_code_id(
    member_code_id: str,
    member_services: Annotated[MemberServices, Depends(get_member_services)],
):
    member = await member_services.get_member_by_code_id(member_code_id)
    # set response body
    response = dict(
        data=member,
        status_code=status.HTTP_200_OK,
        message=(
            f"Successfully created new member: '{member.Title} {member.Title2} {member.First_Name} {member.Last_Name} ({member.Code})"
            + (
                f" / (Clergy Code: {member.Clergy_Code})'"
                if member.Clergy_Code
                else "'"
            )
        ),
    )
    return response


# Get Members by Church Code
@members_router.get(
    "/church/{church_code}",
    name="Get Members by Church",
    summary="Get Members by Church Code",
    description="## Retrieve Members by Church Code",
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


# Update Current User Member
@members_router.put(
    "/current/update",
    name="Update Current User Member",
    summary="Update Current User Member",
    description="## Update Current User Member",
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
        status_code=(
            status.HTTP_200_OK if updated_member else status.HTTP_204_NO_CONTENT
        ),
        message=(
            f"Successfully updated Member: '{updated_member.Title} {updated_member.Title2} {updated_member.First_Name} ({updated_member.Code})'"
            if updated_member
            else "Current User not a church member"
        ),
    )
    return response


# Update Member by Code or Id
@members_router.put(
    "/{code}/update",
    name="Update Member",
    summary="Update Member by Code or Id",
    description="## Update Member by Code or Id",
    response_model=MemberResponse,
)
async def update_member_by_code(
    member_code: str,
    member: MemberUpdate,
    member_services: Annotated[MemberServices, Depends(get_member_services)],
):
    updated_member = await member_services.update_member_by_code_id(member_code, member)
    # set response body
    response = dict(
        data=updated_member,
        status_code=status.HTTP_200_OK,
        message=f"Successfully updated Member: '{updated_member.Title} {updated_member.Title2} {updated_member.First_Name} {updated_member.Last_Name} ({updated_member.Code})'",
    )
    return response


# Get Current Member-Branch
@member_branch_router.get(
    "/{member_code}/branch",
    status_code=status.HTTP_200_OK,
    name="Get Member Current Branch",
    summary="Get Member Current Branch",
    description="## Retrieve Member Current Branch",
    response_model=MemberBranchResponse,
)
async def get_member_current_branch(
    member_code: str,
    member_services: Annotated[MemberServices, Depends(get_member_services)],
):
    member_branch = await member_services.get_member_branches(
        member_code, is_active=True
    )
    # set response body
    response = dict(
        data=member_branch,
        status_code=status.HTTP_200_OK,
        message=f"Successfully retrieved '{member_code.upper()}' Member's Current Branch'",
    )
    return response


# Get Specific Member-Branch by Code
@member_branch_router.get(
    "/{member_code}/branch/{branch_code}",
    status_code=status.HTTP_200_OK,
    name="Get Specific Member-Branch",
    summary="Get Specific Member-Branch by Code",
    description="## Retrieve Specific Member-Branch by Code",
    response_model=MemberBranchResponse,
)
async def get_member_branch_by_code(
    member_code: str,
    branch_code: str,
    member_services: Annotated[MemberServices, Depends(get_member_services)],
    is_active: Optional[bool] = None,
):
    member_branches = await member_services.get_member_branches(
        member_code, branch_code, is_active=is_active
    )
    # set response body
    response = dict(
        data=member_branches,
        status_code=status.HTTP_200_OK,
        message=f"Successfully retrieved {len(member_branches)}"
        + (
            (" current" if is_active == 1 else " previous")
            if is_active is not None
            else ""
        )
        + f" Member-Branch '{branch_code.upper()}'"
        + f" records for Member: '{member_code.upper()}'",
    )
    return response


# Get All Member-Branches by Member Code
@member_branch_router.get(
    "/{member_code}/branches",
    status_code=status.HTTP_200_OK,
    name="Get All Member-Branches by Member",
    summary="Get All Member-Branches by Member Code",
    description="## Retrieve All Member-Branches by Member Code",
    response_model=MemberBranchResponse,
)
async def get_member_all_branches(
    member_code: str,
    member_services: Annotated[MemberServices, Depends(get_member_services)],
    is_active: Optional[bool] = None,
):
    member_branches = await member_services.get_member_branches(
        member_code, is_active=is_active
    )
    # set response body
    response = dict(
        data=member_branches,
        status_code=status.HTTP_200_OK,
        message=f"Successfully retrieved {len(member_branches)}"
        + (
            (" current" if is_active == 1 else " previous")
            if is_active is not None
            else ""
        )
        + (
            " Member-Branch records"
            if {len(member_branches) > 1}
            else " Member-Branch records"
        )
        + f" for Member: '{member_code.upper()}'",
    )
    return response


# Get Member Church Hierarchy
@member_branch_router.get(
    "/{member_code}/hierarchy",
    status_code=status.HTTP_200_OK,
    name="Get Member Church Hierarchy",
    summary="Get Member Church Hierarchy by Member Code",
    description="## Retrieve Member Church Hierarchy by Member Code",
    response_model=MemberChurchHierarchyResponse,
)
async def get_member_church_hierarchy_by_member_code(
    member_code: Annotated[str, Path(..., description="code of member")],
    member_services: Annotated[MemberServices, Depends(get_member_services)],
):
    mc_hierarchy = await member_services.get_member_church_hierarchy_by_member_code(
        member_code
    )
    # set response body
    response = dict(
        data=mc_hierarchy,
        status_code=status.HTTP_200_OK,
        message=f"Successfully retrieved the Member's Church Hierarchy for Member: '{mc_hierarchy.Member_Code}'",
    )
    return response


# Exit Member From Church
@member_branch_adm_router.patch(
    "/{member_code}/exit",
    status_code=status.HTTP_200_OK,
    name="Exit Member From Church",
    summary="Exit Member From Church by Member Code",
    description="## Exit Member From Church by Member Code",
    response_model=MemberBranchResponse,
)
async def exit_member_from_branch(
    member_code: Annotated[str, Path(..., description="code of member to be exited")],
    member_exit: MemberBranchExitIn,
    member_services: Annotated[MemberServices, Depends(get_member_services)],
):
    exited_member = await member_services.exit_member_from_branch(
        member_code, member_exit
    )
    for member in exited_member:
        # set response body
        response = dict(
            data=exited_member,
            status_code=status.HTTP_200_OK,
            message=f"Successfully exited Member: '{member.Title} {member.Title2} {member.First_Name} {member.Last_Name} ({member.Member_Code})' from Branch: '{member_exit.Branch_Code.upper()}'",
        )
        return response


# Exit Member From All Churches
@member_branch_adm_router.patch(
    "/{member_code}/exit_all",
    status_code=status.HTTP_200_OK,
    name="Exit Member From All Churches",
    summary="Exit Member From All Churches",
    description="## Exit Member From All Churches",
    response_model=MemberBranchResponse,
)
async def exit_member_from_all_branches(
    member_code: str,
    member_services: Annotated[MemberServices, Depends(get_member_services)],
):
    exited_member = await member_services.exit_member_from_all_branches(member_code)
    for member in exited_member:
        # set response body
        response = dict(
            data=exited_member,
            status_code=status.HTTP_200_OK,
            message=f"Successfully exited Member: '{member.Title} {member.Title2} {member.First_Name} {member.Last_Name} ({member.Member_Code})' from all Branches",
        )
        return response


# Join Member To Church
@member_branch_adm_router.patch(
    "/{member_code}/join",
    status_code=status.HTTP_200_OK,
    name="Join Member To Church",
    summary="Join Member To Church by Member Code",
    description="## Join Member To Church by Member Code",
    response_model=MemberBranchResponse,
)
async def join_member_to_branch(
    member_code: Annotated[
        str, Path(..., description="code of the member to be joined")
    ],
    member_join: MemberBranchJoinIn,
    member_services: Annotated[MemberServices, Depends(get_member_services)],
):
    joined_member = await member_services.join_member_to_branch(
        member_code, member_join
    )
    for member in joined_member:
        # set response body
        response = dict(
            data=joined_member,
            status_code=status.HTTP_200_OK,
            message=f"Successfully joined Member: '{member.Title} {member.Title2} {member.First_Name} {member.Last_Name} ({member.Member_Code})' to Branch: '{member.Branch_Name} ({member.Branch_Code})'",
        )
        return response


# Update Member-Branch Reason
@member_branch_adm_router.put(
    "/{member_branch_id}/update_reason",
    status_code=status.HTTP_200_OK,
    name="Update Member-Branch Reason",
    summary="Get All Member-Branches by Member Code",
    description="## Update Member-Branch Reason Member-Branches by Member Code",
    response_model=MemberBranchResponse,
)
async def update_member_branch_reason(
    member_branch_id: int,
    member_branch: MemberBranchUpdate,
    member_services: Annotated[MemberServices, Depends(get_member_services)],
):
    updated_member = await member_services.update_member_branch_reason(
        member_branch_id, member_branch
    )
    # set response body
    response = dict(
        data=updated_member,
        status_code=status.HTTP_200_OK,
        message=f"Successfully updated Member-Branch for: '{updated_member.Title} {updated_member.Title2} {updated_member.First_Name} {updated_member.Last_Name} ({updated_member.Member_Code})' to Branch: '{updated_member.Branch_Name} ({updated_member.Branch_Code})'",
    )
    return response
