from http.client import HTTPException
from typing import Annotated

from fastapi import APIRouter, status, Depends  # type: ignore
from sqlalchemy.orm import Session  # type: ignore

from ...authentication.models.auth import User, UserAccess
from ...common.database import get_db
from ...common.dependencies import get_current_user, get_current_user_access
from ...hierarchy_mgmt.services.head_church import HeadChurchServices
from ...hierarchy_mgmt.models.head_church import (
    HeadChurchBase,
    HeadChurchResponse,
    HeadChurchUpdateIn,
)

head_chu_router = APIRouter(prefix="/head_church", tags=["Head Church Operations"])

"""
Head Church Routes
- Create New Head Church
- Get Head Church by Code
- Update Head Church by Code
"""

adm_head_chu_router = APIRouter(
    prefix="/admin/head_church",
    tags=["Head Church Operations - Super Admin only"],
)

"""
Head Church Admin Routes
- Activate Head Church by Code
- Deactivate Head Church by Code
"""


# Create New Head Church
@head_chu_router.post(
    "/create",
    status_code=status.HTTP_201_CREATED,
    name="Create New Head Church",
    response_model=HeadChurchResponse,
)
async def create_new_head_church(
    head_church: HeadChurchBase,
    db: Annotated[Session, Depends(get_db)],
):
    new_head_church = await HeadChurchServices().create_head_church(head_church, db)
    # set response body
    response = dict(
        data=new_head_church,
        status_code=status.HTTP_201_CREATED,
        message=f"Successsfully created new Head Church: {new_head_church.Name} with code: {new_head_church.Code}. \n Please send an email to osquaregtech@gmail.com to activate the Head Church.",
    )
    return response


# Get Head Church by Code
@head_chu_router.get(
    "/{code}",
    status_code=status.HTTP_200_OK,
    name="Get Head Church by Code",
    response_model=HeadChurchResponse,
)
async def get_head_church_by_code(
    code: str,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
    current_user_access: Annotated[UserAccess, Depends(get_current_user_access)],
):
    head_church = await HeadChurchServices().get_head_church_by_code(
        code, db, current_user, current_user_access
    )
    # set response body
    response = dict(
        data=head_church,
        status_code=status.HTTP_200_OK,
        message=f"Successsfully retrieved Head Church: '{head_church.Name}' with code: '{code}'",
    )
    return response


# Update Head Church by Code
@head_chu_router.put(
    "/update/{code}",
    status_code=status.HTTP_200_OK,
    name="Update Head Church by Code",
    response_model=HeadChurchResponse,
)
async def update_head_church_by_code(
    code: str,
    head_church: HeadChurchUpdateIn,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
    current_user_access: Annotated[UserAccess, Depends(get_current_user_access)],
):
    updated_head_church = await HeadChurchServices().update_head_church_by_code(
        code, head_church, db, current_user, current_user_access
    )
    # set response body
    response = dict(
        data=updated_head_church,
        status_code=status.HTTP_200_OK,
        message=f"Successsfully updated Head Church: '{updated_head_church.Name}' with code: '{code.upper()}'",
    )
    return response


# Activate Head Church by Code
@adm_head_chu_router.patch(
    "/{code}/activate",
    status_code=status.HTTP_200_OK,
    name="Activate Head Church by Code",
    response_model=HeadChurchResponse,
)
async def activate_head_church_by_code(
    code: str,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
    current_user_access: Annotated[UserAccess, Depends(get_current_user_access)],
):
    activated_head_church = await HeadChurchServices().activate_head_church_by_code(
        code, db, current_user, current_user_access
    )
    # set response body
    response = dict(
        data=activated_head_church,
        status_code=status.HTTP_200_OK,
        message=f"Successsfully activated Head Church: '{activated_head_church.Name}' with code: '{code.upper()}'",
    )
    return response


# Deactivate Head Church by Code
@adm_head_chu_router.patch(
    "/{code}/deactivate",
    status_code=status.HTTP_200_OK,
    name="Deactivate Head Church by Code",
    response_model=HeadChurchResponse,
)
async def deactivate_head_church_by_code(
    code: str,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
    current_user_access: Annotated[UserAccess, Depends(get_current_user_access)],
):
    deactivated_head_church = await HeadChurchServices().deactivate_head_church_by_code(
        code, db, current_user, current_user_access
    )
    # set response body
    response = dict(
        data=deactivated_head_church,
        status_code=status.HTTP_200_OK,
        message=f"Successsfully deactivated Head Church: '{deactivated_head_church.Name}' with code: '{code.upper()}'",
    )
    return response


# # Get All Head Churches
# @adm_head_chu_router.get(
#     "/",
#     status_code=status.HTTP_200_OK,
#     name="Get All Head Churches",
#     response_model=HeadChurchResponse,
# )
# async def get_all_head_churches(
#     db: Annotated[Session, Depends(get_db)],
#     current_user: Annotated[User, Depends(get_current_user)],
# ):
#     head_churches = HeadChurchAdminService().get_all_head_churches(db)
#     # set response body
#     response = dict(
#         data=head_churches,
#         status_code=status.HTTP_200_OK,
#         message=f"Successsfully retrieved {len(head_churches)} Head Churches",
#     )
#     return response
