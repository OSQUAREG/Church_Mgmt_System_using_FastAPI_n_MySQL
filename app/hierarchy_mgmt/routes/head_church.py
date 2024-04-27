from typing import Annotated

from fastapi import APIRouter, status, Depends  # type: ignore
from sqlalchemy.orm import Session  # type: ignore

from ...authentication.models.auth import User
from ...common.database import get_db
from ...common.dependencies import get_current_user, get_current_user_access
from ...hierarchy_mgmt.services.head_church import HeadChurchService
from ...hierarchy_mgmt.models.head_church import HeadChurchResponse, HeadChurchUpdateIn

head_chu_router = APIRouter(prefix="/head_church", tags=["Head Church Operations"])


"""
Head Church Routes
- Get Head Church by Code
- Update Head Church by Code
"""


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
):
    head_church = HeadChurchService().get_head_church_by_code(code, db)
    # set response body
    response = dict(
        data=head_church,
        status_code=status.HTTP_200_OK,
        message=f"Successsfully retrieved Head Church: {head_church.Name} with code: {code}",
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
    current_user: Annotated[User, Depends(get_current_user_access)],
):
    updated_head_church = HeadChurchService().update_head_church_by_code(
        code, head_church, db, current_user, current_user.church_level
    )
    # set response body
    response = dict(
        data=updated_head_church,
        status_code=status.HTTP_200_OK,
        message=f"Successsfully updated Head Church: '{updated_head_church.Name}' with code: '{code.upper()}'",
    )
    return response
