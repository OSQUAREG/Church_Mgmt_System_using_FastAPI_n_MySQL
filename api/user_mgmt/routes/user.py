from tkinter.tix import Form
from typing import Annotated

from fastapi import APIRouter, status, HTTPException, Depends, Path, Query, Header  # type: ignore
from jose import jwt  # type: ignore

from ..services.user import UserServices, get_user_services
from ..models.user import UserResponse
from ...common.config import settings
from ...swagger_doc import tags

JWT_SECRET_KEY = settings.jwt_secret_key
ALGORITHM = settings.algorithm
ACCESS_TOKEN_EXPIRE_MINUTES = settings.access_token_expire_minutes

user_route = APIRouter(
    prefix="/users", tags=[f"{tags['users']['module']}: {tags['users']['submodule']}"]
)

user_adm_route = APIRouter(
    prefix="/admin/users",
    tags=[f"{tags['users']['module']}: {tags['users']['submodule']}: Admin only"],
)


@user_adm_route.post(
    "/{member_code}/create",
    status_code=status.HTTP_201_CREATED,
    name="Create User From Member",
    summary="Create User From Member Details",
    description="## Create User From Member Details",
    response_model=UserResponse,
)
async def create_user_from_member(
    member_code: Annotated[
        str, Path(..., description="Code of the member to be created as a user")
    ],
    role_code: Annotated[
        str,
        Form(),
        Query(..., description="Code of the role to be assigned to the new user"),
    ],
    level_code: Annotated[
        str,
        Form(),
        Query(..., description="Code of the level to be assigned to the new user"),
    ],
    user_services: Annotated[UserServices, Depends(get_user_services)],
):
    new_user = await user_services.create_user_from_member(
        member_code, role_code, level_code
    )
    # set response body
    response = dict(
        data=new_user,
        status_code=status.HTTP_201_CREATED,
        message=f"Successfully created member as a user: '{new_user.First_Name} {new_user.Last_Name} ({new_user.Usercode})'",
    )
    return response


# Get User Details by User Code
@user_route.get(
    "/{user_code}",
    status_code=status.HTTP_200_OK,
    name="Get User",
    summary="Get User Details By Usercode",
    description="## Retrieve User Details By Usercode",
    response_model=UserResponse,
)
async def get_user_details_by_usercode(
    user_code: Annotated[
        str, Path(..., description="Code of the user to be retrieved")
    ],
    user_services: Annotated[UserServices, Depends(get_user_services)],
    authorization: Annotated[str, Header(..., description="Bearer token")],
):
    # Decode token to extract level_code
    level_code = await user_services.get_church_level_from_token(authorization)
    # token = authorization.split("Bearer ")[-1]
    # payload = jwt.decode(token, key=JWT_SECRET_KEY, algorithms=ALGORITHM)
    # level_code = payload.get("church_level")

    # if not level_code:
    #     raise HTTPException(status_code=400, detail="Level code not found in token")

    user = await user_services.get_user_details(user_code, level_code)
    # set response body
    response = dict(
        data=user,
        status_code=status.HTTP_200_OK,
        message=f"Successfully retrieved user: '{user.First_Name} {user.Last_Name} ({user.Usercode})'",
    )
    return response


# Get Users Details
@user_route.get(
    "/",
    status_code=status.HTTP_200_OK,
    name="Get Users",
    summary="Get Users Details",
    description="## Retrieve Users Details",
    response_model=UserResponse,
)
async def get_users_details(
    user_services: Annotated[UserServices, Depends(get_user_services)],
    authorization: Annotated[str, Header(..., description="Bearer token")],
):
    # Decode token to extract level_code
    token = authorization.split("Bearer ")[-1]
    payload = jwt.decode(token, key=JWT_SECRET_KEY, algorithms=ALGORITHM)
    level_code = payload.get("church_level")

    if not level_code:
        raise HTTPException(status_code=400, detail="Level code not found in token")

    users = await user_services.get_users_details(level_code)
    # set response body
    response = dict(
        data=users,
        status_code=status.HTTP_200_OK,
        message=f"Successfully retrieved {len(users)} users at {level_code.upper()} Level",
    )
    return response


# endpoints = [
#     {
#         "router_name": "Authentication (AUTH): Authentication Sub-Module (AUTH)",
#         "name": "Authenticate User",
#         "submodule": {
#             "module_name": "Authentication",
#             "module_code": "AUTH",
#             "submodule_name": "Authentication",
#             "submodule_code": "AUTH",
#         },
#         "description": "User Login Route - Authenticate User",
#         "methods": ["POST"],
#     },
#     {
#         "router_name": "Authentication (AUTH): Authentication Sub-Module (AUTH)",
#         "name": "Re-Authenticate User",
#         "submodule": {
#             "module_name": "Authentication",
#             "module_code": "AUTH",
#             "submodule_name": "Authentication",
#             "submodule_code": "AUTH",
#         },
#         "description": "Re-Authenticate User by Selecting Church Level",
#         "methods": ["POST"],
#     },
#     {
#         "router_name": "Authentication (AUTH): Authentication Sub-Module (AUTH)",
#         "name": "Get Current User",
#         "submodule": {
#             "module_name": "Authentication",
#             "module_code": "AUTH",
#             "submodule_name": "Authentication",
#             "submodule_code": "AUTH",
#         },
#         "description": "Get Current Active User",
#         "methods": ["GET"],
#     },
#     {
#         "router_name": "Authentication (AUTH): Authentication Sub-Module (AUTH)",
#         "name": "Get Current User Access",
#         "submodule": {
#             "module_name": "Authentication",
#             "module_code": "AUTH",
#             "submodule_name": "Authentication",
#             "submodule_code": "AUTH",
#         },
#         "description": "Get Current Active User Access",
#         "methods": ["GET"],
#     },
#     {
#         "router_name": "Authentication (AUTH): Authentication Sub-Module (AUTH)",
#         "name": "Get Current User Levels",
#         "submodule": {
#             "module_name": "Authentication",
#             "module_code": "AUTH",
#             "submodule_name": "Authentication",
#             "submodule_code": "AUTH",
#         },
#         "description": "Get Current Active User Levels",
#         "methods": ["GET"],
#     },
#     {
#         "router_name": "Church Administration (CHAD): Hierarchy Sub-Module (HIER)",
#         "name": "Get Hierarchies",
#         "submodule": {
#             "module_name": "Church Administration",
#             "module_code": "CHAD",
#             "submodule_name": "Hierarchy",
#             "submodule_code": "HIER",
#         },
#         "description": "Retrieve All Hierarchies",
#         "methods": ["GET"],
#     },
#     {
#         "router_name": "Church Administration (CHAD): Hierarchy Sub-Module (HIER)",
#         "name": "Get Hierarchy",
#         "submodule": {
#             "module_name": "Church Administration",
#             "module_code": "CHAD",
#             "submodule_name": "Hierarchy",
#             "submodule_code": "HIER",
#         },
#         "description": "Retrieve Hierarchy by Code",
#         "methods": ["GET"],
#     },
#     {
#         "router_name": "Church Administration (CHAD): Hierarchy Sub-Module (HIER)",
#         "name": "Activate Hierarchy",
#         "submodule": {
#             "module_name": "Church Administration",
#             "module_code": "CHAD",
#             "submodule_name": "Hierarchy",
#             "submodule_code": "HIER",
#         },
#         "description": "Activate Hierarchy by Code",
#         "methods": ["PATCH"],
#     },
#     {
#         "router_name": "Church Administration (CHAD): Hierarchy Sub-Module (HIER)",
#         "name": "Deactivate Hierarchy",
#         "submodule": {
#             "module_name": "Church Administration",
#             "module_code": "CHAD",
#             "submodule_name": "Hierarchy",
#             "submodule_code": "HIER",
#         },
#         "description": "Deactivate Hierarchy by Code",
#         "methods": ["PATCH"],
#     },
#     {
#         "router_name": "Church Administration (CHAD): Hierarchy Sub-Module (HIER)",
#         "name": "Update Hierarchy",
#         "submodule": {
#             "module_name": "Church Administration",
#             "module_code": "CHAD",
#             "submodule_name": "Hierarchy",
#             "submodule_code": "HIER",
#         },
#         "description": "Update Hierarchy by Code",
#         "methods": ["PUT"],
#     },
#     {
#         "router_name": "Church Administration (CHAD): Head Church Sub-Module (HEAD)",
#         "name": "Create New Head Church",
#         "submodule": {
#             "module_name": "Church Administration",
#             "module_code": "CHAD",
#             "submodule_name": "Head Church",
#             "submodule_code": "HEAD",
#         },
#         "description": "Create New Head Church",
#         "methods": ["POST"],
#     },
#     {
#         "router_name": "Church Administration (CHAD): Head Church Sub-Module (HEAD)",
#         "name": "Get Head Church",
#         "submodule": {
#             "module_name": "Church Administration",
#             "module_code": "CHAD",
#             "submodule_name": "Head Church",
#             "submodule_code": "HEAD",
#         },
#         "description": "Retrieve Head Church by Code",
#         "methods": ["GET"],
#     },
#     {
#         "router_name": "Church Administration (CHAD): Head Church Sub-Module (HEAD)",
#         "name": "Update Head Church",
#         "submodule": {
#             "module_name": "Church Administration",
#             "module_code": "CHAD",
#             "submodule_name": "Head Church",
#             "submodule_code": "HEAD",
#         },
#         "description": "Update Head Church by Code",
#         "methods": ["PUT"],
#     },
#     {
#         "router_name": "Church Administration (CHAD): Head Church Sub-Module (HEAD): Super Admin only",
#         "name": "Activate Head Church",
#         "submodule": {
#             "module_name": "Church Administration",
#             "module_code": "CHAD",
#             "submodule_name": "Head Church",
#             "submodule_code": "HEAD",
#         },
#         "description": "Activate Head Church by Code",
#         "methods": ["PATCH"],
#     },
#     {
#         "router_name": "Church Administration (CHAD): Head Church Sub-Module (HEAD): Super Admin only",
#         "name": "Deactivate Head Church",
#         "submodule": {
#             "module_name": "Church Administration",
#             "module_code": "CHAD",
#             "submodule_name": "Head Church",
#             "submodule_code": "HEAD",
#         },
#         "description": "Deactivate Head Church by Code",
#         "methods": ["PATCH"],
#     },
#     {
#         "router_name": "Church Administration (CHAD): Churches Sub-Module (CHUR)",
#         "name": "Create New Church",
#         "submodule": {
#             "module_name": "Church Administration",
#             "module_code": "CHAD",
#             "submodule_name": "Churches",
#             "submodule_code": "CHUR",
#         },
#         "description": "Create New Church",
#         "methods": ["POST"],
#     },
#     {
#         "router_name": "Church Administration (CHAD): Churches Sub-Module (CHUR)",
#         "name": "Approve Church",
#         "submodule": {
#             "module_name": "Church Administration",
#             "module_code": "CHAD",
#             "submodule_name": "Churches",
#             "submodule_code": "CHUR",
#         },
#         "description": "Approve Church by Id or Code",
#         "methods": ["PATCH"],
#     },
#     {
#         "router_name": "Church Administration (CHAD): Churches Sub-Module (CHUR)",
#         "name": "Get All Churches",
#         "submodule": {
#             "module_name": "Church Administration",
#             "module_code": "CHAD",
#             "submodule_name": "Churches",
#             "submodule_code": "CHUR",
#         },
#         "description": "Retrieve All Churches",
#         "methods": ["GET"],
#     },
#     {
#         "router_name": "Church Administration (CHAD): Churches Sub-Module (CHUR)",
#         "name": "Get Churches by Level",
#         "submodule": {
#             "module_name": "Church Administration",
#             "module_code": "CHAD",
#             "submodule_name": "Churches",
#             "submodule_code": "CHUR",
#         },
#         "description": "Retrieve Churches by Hierarchical Church Level",
#         "methods": ["GET"],
#     },
#     {
#         "router_name": "Church Administration (CHAD): Churches Sub-Module (CHUR)",
#         "name": "Get Church",
#         "submodule": {
#             "module_name": "Church Administration",
#             "module_code": "CHAD",
#             "submodule_name": "Churches",
#             "submodule_code": "CHUR",
#         },
#         "description": "Retrieve Church by Id or Code",
#         "methods": ["GET"],
#     },
#     {
#         "router_name": "Church Administration (CHAD): Churches Sub-Module (CHUR)",
#         "name": "Update Church",
#         "submodule": {
#             "module_name": "Church Administration",
#             "module_code": "CHAD",
#             "submodule_name": "Churches",
#             "submodule_code": "CHUR",
#         },
#         "description": "Update Church by Code",
#         "methods": ["PUT"],
#     },
#     {
#         "router_name": "Church Administration (CHAD): Churches Sub-Module (CHUR): Admin only",
#         "name": "Activate Church",
#         "submodule": {
#             "module_name": "Church Administration",
#             "module_code": "CHAD",
#             "submodule_name": "Churches",
#             "submodule_code": "CHUR",
#         },
#         "description": "Activate Church by Code",
#         "methods": ["PATCH"],
#     },
#     {
#         "router_name": "Church Administration (CHAD): Churches Sub-Module (CHUR): Admin only",
#         "name": "Deactivate Church",
#         "submodule": {
#             "module_name": "Church Administration",
#             "module_code": "CHAD",
#             "submodule_name": "Churches",
#             "submodule_code": "CHUR",
#         },
#         "description": "Deactivate Church by Code",
#         "methods": ["PATCH"],
#     },
#     {
#         "router_name": "Church Administration (CHAD): Church Leads Sub-Module (LEAD)",
#         "name": "Get Church Lead",
#         "submodule": {
#             "module_name": "Church Administration",
#             "module_code": "CHAD",
#             "submodule_name": "Church Leads",
#             "submodule_code": "LEAD",
#         },
#         "description": "Retrieve Church Lead by Code",
#         "methods": ["GET"],
#     },
#     {
#         "router_name": "Church Administration (CHAD): Church Leads Sub-Module (LEAD)",
#         "name": "Approve Church Lead",
#         "submodule": {
#             "module_name": "Church Administration",
#             "module_code": "CHAD",
#             "submodule_name": "Church Leads",
#             "submodule_code": "LEAD",
#         },
#         "description": "Approve Church Lead by Code",
#         "methods": ["PATCH"],
#     },
#     {
#         "router_name": "Church Administration (CHAD): Church Leads Sub-Module (LEAD)",
#         "name": "Get Churches by Lead",
#         "submodule": {
#             "module_name": "Church Administration",
#             "module_code": "CHAD",
#             "submodule_name": "Church Leads",
#             "submodule_code": "LEAD",
#         },
#         "description": "Retrieve Churches by Leads Code",
#         "methods": ["GET"],
#     },
#     {
#         "router_name": "Church Administration (CHAD): Church Leads Sub-Module (LEAD)",
#         "name": "Get Branches by Church Lead",
#         "submodule": {
#             "module_name": "Church Administration",
#             "module_code": "CHAD",
#             "submodule_name": "Church Leads",
#             "submodule_code": "LEAD",
#         },
#         "description": "Retrieve Branches by Church Lead Code",
#         "methods": ["GET"],
#     },
#     {
#         "router_name": "Church Administration (CHAD): Church Leads Sub-Module (LEAD)",
#         "name": "Get Church Lead Hierarchy",
#         "submodule": {
#             "module_name": "Church Administration",
#             "module_code": "CHAD",
#             "submodule_name": "Church Leads",
#             "submodule_code": "LEAD",
#         },
#         "description": "Retrieve Church Lead Hierarchy by Church Code",
#         "methods": ["GET"],
#     },
#     {
#         "router_name": "Church Administration (CHAD): Church Leads Sub-Module (LEAD): Admin only",
#         "name": "Unmap Church Lead",
#         "submodule": {
#             "module_name": "Church Administration",
#             "module_code": "CHAD",
#             "submodule_name": "Church Leads",
#             "submodule_code": "LEAD",
#         },
#         "description": "Unmap Church Leads by Church code",
#         "methods": ["PATCH"],
#     },
#     {
#         "router_name": "Church Administration (CHAD): Church Leads Sub-Module (LEAD): Admin only",
#         "name": "Map Church Lead",
#         "submodule": {
#             "module_name": "Church Administration",
#             "module_code": "CHAD",
#             "submodule_name": "Church Leads",
#             "submodule_code": "LEAD",
#         },
#         "description": "Map Church Leads",
#         "methods": ["POST"],
#     },
#     {
#         "router_name": "Membership Management (MBSM): Members Sub-Module (MBRS)",
#         "name": "Get All Members",
#         "submodule": {
#             "module_name": "Membership Management",
#             "module_code": "MBSM",
#             "submodule_name": "Members",
#             "submodule_code": "MBRS",
#         },
#         "description": "Retrieve All Members",
#         "methods": ["GET"],
#     },
#     {
#         "router_name": "Membership Management (MBSM): Members Sub-Module (MBRS)",
#         "name": "Get Current User Member",
#         "submodule": {
#             "module_name": "Membership Management",
#             "module_code": "MBSM",
#             "submodule_name": "Members",
#             "submodule_code": "MBRS",
#         },
#         "description": "Get Current User Member",
#         "methods": ["GET"],
#     },
#     {
#         "router_name": "Membership Management (MBSM): Members Sub-Module (MBRS)",
#         "name": "Get Member",
#         "submodule": {
#             "module_name": "Membership Management",
#             "module_code": "MBSM",
#             "submodule_name": "Members",
#             "submodule_code": "MBRS",
#         },
#         "description": "Retrieve Member by Code or Id",
#         "methods": ["GET"],
#     },
#     {
#         "router_name": "Membership Management (MBSM): Members Sub-Module (MBRS)",
#         "name": "Get Members by Church",
#         "submodule": {
#             "module_name": "Membership Management",
#             "module_code": "MBSM",
#             "submodule_name": "Members",
#             "submodule_code": "MBRS",
#         },
#         "description": "Retrieve Members by Church Code",
#         "methods": ["GET"],
#     },
#     {
#         "router_name": "Membership Management (MBSM): Members Sub-Module (MBRS)",
#         "name": "Update Current User Member",
#         "submodule": {
#             "module_name": "Membership Management",
#             "module_code": "MBSM",
#             "submodule_name": "Members",
#             "submodule_code": "MBRS",
#         },
#         "description": "Update Current User Member",
#         "methods": ["PUT"],
#     },
#     {
#         "router_name": "Membership Management (MBSM): Members Sub-Module (MBRS)",
#         "name": "Update Member",
#         "submodule": {
#             "module_name": "Membership Management",
#             "module_code": "MBSM",
#             "submodule_name": "Members",
#             "submodule_code": "MBRS",
#         },
#         "description": "Update Member by Code or Id",
#         "methods": ["PUT"],
#     },
#     {
#         "router_name": "Membership Management (MBSM): Members Sub-Module (MBRS): Admin only",
#         "name": "Create New Member",
#         "submodule": {
#             "module_name": "Membership Management",
#             "module_code": "MBSM",
#             "submodule_name": "Members",
#             "submodule_code": "MBRS",
#         },
#         "description": "Create New Member",
#         "methods": ["POST"],
#     },
#     {
#         "router_name": "Membership Management (MBSM): Members Sub-Module (MBRS): Admin only",
#         "name": "Deactivate Member",
#         "submodule": {
#             "module_name": "Membership Management",
#             "module_code": "MBSM",
#             "submodule_name": "Members",
#             "submodule_code": "MBRS",
#         },
#         "description": "Deactivate Member by Code",
#         "methods": ["PATCH"],
#     },
#     {
#         "router_name": "Membership Management (MBSM): Members Sub-Module (MBRS): Admin only",
#         "name": "Activate Member",
#         "submodule": {
#             "module_name": "Membership Management",
#             "module_code": "MBSM",
#             "submodule_name": "Members",
#             "submodule_code": "MBRS",
#         },
#         "description": "Activate Member by Code",
#         "methods": ["PATCH"],
#     },
#     {
#         "router_name": "Membership Management (MBSM): Members Sub-Module (MBRS): Admin only",
#         "name": "Promote Member to Clergy",
#         "submodule": {
#             "module_name": "Membership Management",
#             "module_code": "MBSM",
#             "submodule_name": "Members",
#             "submodule_code": "MBRS",
#         },
#         "description": "Promote Member to Clergy",
#         "methods": ["PATCH"],
#     },
#     {
#         "router_name": "Membership Management (MBSM): Members Sub-Module (MBRS): Admin only",
#         "name": "Demote Member from Clergy",
#         "submodule": {
#             "module_name": "Membership Management",
#             "module_code": "MBSM",
#             "submodule_name": "Members",
#             "submodule_code": "MBRS",
#         },
#         "description": "Demote Member from Clergy",
#         "methods": ["PATCH"],
#     },
#     {
#         "router_name": "Membership Management (MBSM): Member Branch Sub-Module (MBRN)",
#         "name": "Get Member Current Branch",
#         "submodule": {
#             "module_name": "Membership Management",
#             "module_code": "MBSM",
#             "submodule_name": "Member Branch",
#             "submodule_code": "MBRN",
#         },
#         "description": "Retrieve Member Current Branch",
#         "methods": ["GET"],
#     },
#     {
#         "router_name": "Membership Management (MBSM): Member Branch Sub-Module (MBRN)",
#         "name": "Get Specific Member-Branch",
#         "submodule": {
#             "module_name": "Membership Management",
#             "module_code": "MBSM",
#             "submodule_name": "Member Branch",
#             "submodule_code": "MBRN",
#         },
#         "description": "Retrieve Specific Member-Branch by Code",
#         "methods": ["GET"],
#     },
#     {
#         "router_name": "Membership Management (MBSM): Member Branch Sub-Module (MBRN)",
#         "name": "Get All Member-Branches by Member",
#         "submodule": {
#             "module_name": "Membership Management",
#             "module_code": "MBSM",
#             "submodule_name": "Member Branch",
#             "submodule_code": "MBRN",
#         },
#         "description": "Retrieve All Member-Branches by Member Code",
#         "methods": ["GET"],
#     },
#     {
#         "router_name": "Membership Management (MBSM): Member Branch Sub-Module (MBRN)",
#         "name": "Get Member Church Hierarchy",
#         "submodule": {
#             "module_name": "Membership Management",
#             "module_code": "MBSM",
#             "submodule_name": "Member Branch",
#             "submodule_code": "MBRN",
#         },
#         "description": "Retrieve Member Church Hierarchy by Member Code",
#         "methods": ["GET"],
#     },
#     {
#         "router_name": "Membership Management (MBSM): Member Branch Sub-Module (MBRN): Admin only",
#         "name": "Exit Member From Church",
#         "submodule": {
#             "module_name": "Membership Management",
#             "module_code": "MBSM",
#             "submodule_name": "Member Branch",
#             "submodule_code": "MBRN",
#         },
#         "description": "Exit Member From Church by Member Code",
#         "methods": ["PATCH"],
#     },
# ]
