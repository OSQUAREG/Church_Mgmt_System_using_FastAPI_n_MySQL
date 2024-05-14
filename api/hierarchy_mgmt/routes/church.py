from typing import Annotated

from fastapi import APIRouter, status, Depends, Form  # type: ignore
from sqlalchemy.orm import Session  # type: ignore

from ...authentication.models.auth import User
from ...common.database import get_db
from ...common.dependencies import get_current_user, get_current_user_access
from ...hierarchy_mgmt.services import ChurchServices
from ...hierarchy_mgmt.models.church import ChurchBase, ChurchResponse, ChurchUpdate


church_router = APIRouter(prefix=f"/church", tags=["Church Operations"])

"""
#### Church Routes
- Create New Church
- Approved Church by Code
- Get All Churches
- Get Churches by Level
- Get Church by Code
- Update Church by Code
- Activate Church by Code
- Deactivate Church by Code
"""


# Create New Church
@church_router.post(
    "/create",
    status_code=status.HTTP_201_CREATED,
    name="Create New Church",
    response_model=ChurchResponse,
)
async def create_new_church(
    level_code: str,
    church: ChurchBase,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
    current_user_access: Annotated[User, Depends(get_current_user_access)],
):
    new_church = await ChurchServices().create_new_church(
        level_code, church, db, current_user, current_user_access
    )
    # set response body
    response = dict(
        data=new_church,
        status_code=status.HTTP_201_CREATED,
        message=f"Successfully created Church: '{new_church.Name}', with code: '{new_church.Code}'",
    )
    return response


# Approve church by code
@church_router.patch(
    "/{code}/approve",
    status_code=status.HTTP_200_OK,
    name="Approve Church by Code",
    response_model=ChurchResponse,
)
async def approve_church_by_code(
    code: str,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
    current_user_access: Annotated[User, Depends(get_current_user_access)],
):
    approved_church = await ChurchServices().approve_church_by_code(
        code, db, current_user, current_user_access
    )
    # set response body
    response = dict(
        data=approved_church,
        status_code=status.HTTP_200_OK,
        message=f"Successfully approved Church: '{approved_church.Name}' with code: '{approved_church.Code}'",
    )
    return response


# Get All Churches
@church_router.get(
    "/",
    status_code=status.HTTP_200_OK,
    name="Get All Churches",
    response_model=ChurchResponse,
)
async def get_all_churches(
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
    current_user_access: Annotated[User, Depends(get_current_user_access)],
):
    churches = await ChurchServices().get_all_churches(
        db, current_user, current_user_access
    )
    # set response body
    response = dict(
        data=churches,
        status_code=status.HTTP_200_OK,
        message=f"Successfully retrieved all {len(churches)} Churches",
    )
    return response


# Get Churches by Level
@church_router.get(
    "/level/{level_code}",
    status_code=status.HTTP_200_OK,
    name="Get Churches by Level",
    response_model=ChurchResponse,
)
async def get_churches_by_level(
    level_code: str,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
    current_user_access: Annotated[User, Depends(get_current_user_access)],
):
    churches = await ChurchServices().get_churches_by_level(
        level_code, db, current_user, current_user_access
    )
    # set response body
    response = dict(
        data=churches,
        status_code=status.HTTP_200_OK,
        message=f"Successfully retrieved all {len(churches)} Churches in level: '{level_code.upper()}'",
    )
    return response


@church_router.get(
    "/{code}",
    status_code=status.HTTP_200_OK,
    name="Get Church by Code",
    response_model=ChurchResponse,
)
async def get_church_by_code(
    code: str,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
    current_user_access: Annotated[User, Depends(get_current_user_access)],
):
    church = await ChurchServices().get_church_by_code(
        code, db, current_user, current_user_access
    )
    # set response body
    response = dict(
        data=church,
        status_code=status.HTTP_200_OK,
        message=f"Successfully retrieved Church: '{church.Name}' with code: '{church.Code}'",
    )
    return response


# update church by code
@church_router.put(
    "/{code}/update",
    status_code=status.HTTP_200_OK,
    name="Update Church by Code",
    response_model=ChurchResponse,
)
async def update_church_by_code(
    code: str,
    church: ChurchUpdate,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
    current_user_access: Annotated[User, Depends(get_current_user_access)],
):
    updated_church = await ChurchServices().update_church_by_code(
        code, church, db, current_user, current_user_access
    )
    # set response body
    response = dict(
        data=updated_church,
        status_code=status.HTTP_200_OK,
        message=f"Successfully updated Church: '{updated_church.Name}' with code: '{updated_church.Code}'",
    )
    return response


# Activate church by code
@church_router.patch(
    "/{code}/activate",
    status_code=status.HTTP_200_OK,
    name="Activate Church by Code",
    response_model=ChurchResponse,
)
async def activate_church_by_code(
    code: str,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
    current_user_access: Annotated[User, Depends(get_current_user_access)],
):
    activated_church = await ChurchServices().activate_church_by_code(
        code, db, current_user, current_user_access
    )
    # set response body
    response = dict(
        data=activated_church,
        status_code=status.HTTP_200_OK,
        message=f"Successfully activated Church: '{activated_church.Name}' with code: '{activated_church.Code}'",
    )
    return response


# deactivate church by code
@church_router.patch(
    "/{code}/deactivate",
    status_code=status.HTTP_200_OK,
    name="Deactivate Church by Code",
    response_model=ChurchResponse,
)
async def deactivate_church_by_code(
    code: str,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
    current_user_access: Annotated[User, Depends(get_current_user_access)],
):
    deactivated_church = await ChurchServices().deactivate_church_by_code(
        code, db, current_user, current_user_access
    )
    # set response body
    response = dict(
        data=deactivated_church,
        status_code=status.HTTP_200_OK,
        message=f"Successfully deactivated Church: '{deactivated_church.Name}' with code: '{deactivated_church.Code}'",
    )
    return response
