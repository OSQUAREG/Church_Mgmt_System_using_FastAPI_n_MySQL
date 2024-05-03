from typing import Annotated

from fastapi import APIRouter, status, Depends  # type: ignore
from sqlalchemy.orm import Session  # type: ignore

from ...authentication.models.auth import User
from ...common.database import get_db
from ...common.dependencies import get_current_user, get_current_user_access
from ...hierarchy_mgmt.services.level1 import Level1Service
from ...hierarchy_mgmt.models.level1 import (
    Level1Base,
    Level1Response,
    Level1Update,
)


level1_router = APIRouter(prefix=f"/cl1", tags=["Level 1 Church Operations"])

"""
#### Church Routes
- Create New Level 1 Church
- Approved Level 1 Church by Code
- Get All Level 1 Churches
- Get Level 1 Church by Code
- Update Level 1 Church by Code
- Activate Level 1 Church by code
- Deactivate Level 1 Church by Code
"""


# Create New Church
@level1_router.post(
    "/create",
    status_code=status.HTTP_201_CREATED,
    name="Create New Level 1 Church",
    response_model=Level1Response,
)
async def create_new_level1_church(
    church: Level1Base,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
    current_user_access: Annotated[User, Depends(get_current_user_access)],
):
    new_church = await Level1Service().create_new_level1_church(
        church, db, current_user, current_user_access
    )
    # set response body
    response = dict(
        data=new_church,
        status_code=status.HTTP_201_CREATED,
        message=f"Successfully created Church: '{new_church.Name}', with code: '{new_church.Code}'",
    )
    return response


# Approve church by code
@level1_router.patch(
    "/{code}/approve",
    status_code=status.HTTP_200_OK,
    name="Approve Level 1 Church by Code",
    response_model=Level1Response,
)
async def approve_church_by_code(
    code: str,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
    current_user_access: Annotated[User, Depends(get_current_user_access)],
):
    approved_church = await Level1Service().approve_level1_church_by_code(
        code, db, current_user, current_user_access
    )
    # set response body
    response = dict(
        data=approved_church,
        status_code=status.HTTP_200_OK,
        message=f"Successfully approved Church: '{approved_church.Name}' with code: '{approved_church.Code}'",
    )
    return response


# Get All Churchs
@level1_router.get(
    "/",
    status_code=status.HTTP_200_OK,
    name="Get All Level 1 Churches",
    response_model=Level1Response,
)
async def get_all_level1_churches(
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
    current_user_access: Annotated[User, Depends(get_current_user_access)],
):
    churchs = await Level1Service().get_all_level1_churches(
        db, current_user, current_user_access
    )
    # set response body
    response = dict(
        data=churchs,
        status_code=status.HTTP_200_OK,
        message=f"Successfully retrieved all {len(churchs)} Churchs",
    )
    return response


@level1_router.get(
    "/{code}",
    status_code=status.HTTP_200_OK,
    name="Get Level 1 Church by Code",
    response_model=Level1Response,
)
async def get_church_by_code(
    code: str,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
    current_user_access: Annotated[User, Depends(get_current_user_access)],
):
    church = await Level1Service().get_church_by_code(
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
@level1_router.put(
    "/{code}/update",
    status_code=status.HTTP_200_OK,
    name="Update Level 1 Church by Code",
    response_model=Level1Response,
)
async def update_church_by_code(
    code: str,
    church: Level1Update,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
    current_user_access: Annotated[User, Depends(get_current_user_access)],
):
    updated_church = await Level1Service().update_level1_church_by_code(
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
@level1_router.patch(
    "/{code}/activate",
    status_code=status.HTTP_200_OK,
    name="Activate Level 1 Church by Code",
    response_model=Level1Response,
)
async def activate_church_by_code(
    code: str,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
    current_user_access: Annotated[User, Depends(get_current_user_access)],
):
    activated_church = await Level1Service().activate_church_by_code(
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
@level1_router.patch(
    "/{code}/deactivate",
    status_code=status.HTTP_200_OK,
    name="Deactivate Church by Code",
    response_model=Level1Response,
)
async def deactivate_church_by_code(
    code: str,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
    current_user_access: Annotated[User, Depends(get_current_user_access)],
):
    deactivated_church = await Level1Service().deactivate_church_by_code(
        code, db, current_user, current_user_access
    )
    # set response body
    response = dict(
        data=deactivated_church,
        status_code=status.HTTP_200_OK,
        message=f"Successfully deactivated Church: '{deactivated_church.Name}' with code: '{deactivated_church.Code}'",
    )
    return response
