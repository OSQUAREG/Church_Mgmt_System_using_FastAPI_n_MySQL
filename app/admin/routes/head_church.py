from typing import Annotated

from fastapi import APIRouter, status, Depends  # type: ignore
from sqlalchemy.orm import Session  # type: ignore

from ...common.database import get_db
from ...common.dependencies import get_current_user
from ...authentication.models.auth import User
from ...admin.services.head_church import HeadChurchAdminService
from ...hierarchy_mgmt.models.head_church import HeadChurch, HeadChurchResponse

adm_head_chu_router = APIRouter(
    prefix="/admin/head_church",
    tags=["Head Church Operations - Admin only"],
)


"""
Head Church Admin Routes
- Create New Head Church
- Get All Head Churches
- Activate Head Church by Code
- Deactivate Head Church by Code
"""


# Create New Head Church
@adm_head_chu_router.post(
    "/create",
    status_code=status.HTTP_201_CREATED,
    name="Create New Head Church",
    response_model=HeadChurchResponse,
)
async def create_new_head_church(
    head_church: HeadChurch,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
):
    new_head_church = HeadChurchAdminService().create_head_church(
        head_church, db, current_user
    )
    # set response body
    response = dict(
        data=new_head_church,
        status_code=status.HTTP_201_CREATED,
        message=f"Successsfully created new Head Church: {new_head_church.Name} with code: {new_head_church.Code}",
    )
    return response


# Get All Head Churches
@adm_head_chu_router.get(
    "/",
    status_code=status.HTTP_200_OK,
    name="Get All Head Churches",
    response_model=HeadChurchResponse,
)
async def get_all_head_churches(
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
):
    head_churches = HeadChurchAdminService().get_all_head_churches(db)
    # set response body
    response = dict(
        data=head_churches,
        status_code=status.HTTP_200_OK,
        message=f"Successsfully retrieved {len(head_churches)} Head Churches",
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
):
    activated_head_church = HeadChurchAdminService().activate_head_church_by_code(
        code, db, current_user
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
):
    deactivated_head_church = HeadChurchAdminService().deactivate_head_church_by_code(
        code, db, current_user
    )
    # set response body
    response = dict(
        data=deactivated_head_church,
        status_code=status.HTTP_200_OK,
        message=f"Successsfully deactivated Head Church: '{deactivated_head_church.Name}' with code: '{code.upper()}'",
    )
    return response
