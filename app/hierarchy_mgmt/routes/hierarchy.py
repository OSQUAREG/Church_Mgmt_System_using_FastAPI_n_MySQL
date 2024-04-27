from typing import Annotated

from fastapi import APIRouter, status, Depends  # type: ignore
from sqlalchemy import text  # type: ignore
from sqlalchemy.orm import Session  # type: ignore

from ...common.database import get_db
from ...common.dependencies import get_current_user
from ...authentication.models.auth import User
from ...hierarchy_mgmt.services.hierarchy import HierarchyService
from ...hierarchy_mgmt.models.hierarchy import HierarchyResponse

hierarchy_router = APIRouter(prefix="/hierarchy", tags=["Hierarchy Operations"])

"""
Hierarchy Routes
- Get All Hierarchies
- Get Hierarchy by Code
- Activate Hierarchy by Code
- Deactivate Hierarchy by Code
"""


# Get All Hierarchies
@hierarchy_router.get(
    "/",
    status_code=status.HTTP_200_OK,
    name="Get All Hierarchies",
    response_model=HierarchyResponse,
)
async def get_all_hierarchies(
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
):
    hierarchies = HierarchyService().get_all_hierarchies(db, current_user)
    # set response body
    response = dict(
        data=hierarchies,
        status_code=status.HTTP_200_OK,
        message=f"Successsfully retrieved {len(hierarchies)} Hierarchies",
    )
    return response


# Get Hierarchy by Code
@hierarchy_router.get(
    "/{code}",
    status_code=status.HTTP_200_OK,
    name="Get Hierarchy by Code",
    response_model=HierarchyResponse,
)
async def get_hierarchy_by_code(
    code: str,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
):
    hierarchy = HierarchyService().get_hierarchy_by_code(code, db, current_user)
    # set response body
    response = dict(
        data=hierarchy,
        status_code=status.HTTP_200_OK,
        message=f"Successsfully retrieved Hierarchy: '{hierarchy.Hierarchy}', with code: '{hierarchy.Code.upper()}'",
    )
    return response


# Activate Hierarchy by Code
@hierarchy_router.patch(
    "/{code}/activate",
    status_code=status.HTTP_200_OK,
    name="Activate Hierarchy by Code",
    response_model=HierarchyResponse,
)
async def activate_hierarchy_by_code(
    code: str,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
):
    activated_hierarchy = HierarchyService().activate_hierarchy_by_code(
        code, db, current_user
    )
    # set response body
    response = dict(
        data=activated_hierarchy,
        status_code=status.HTTP_200_OK,
        message=f"Successsfully activated Hierarchy: '{activated_hierarchy.Hierarchy}', with code: '{activated_hierarchy.Code.upper()}'",
    )
    return response


# Deactivate Hierarchy by Code
@hierarchy_router.patch(
    "/{code}/deactivate",
    status_code=status.HTTP_200_OK,
    name="Deactivate Hierarchy by Code",
    response_model=HierarchyResponse,
)
async def deactivate_hierarchy_by_code(
    code: str,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
):
    deactivated_hierarchy = HierarchyService().deactivate_hierarchy_by_code(
        code, db, current_user
    )
    # set response body
    response = dict(
        data=deactivated_hierarchy,
        status_code=status.HTTP_200_OK,
        message=f"Successsfully deactivated Hierarchy: '{deactivated_hierarchy.Hierarchy}', with code: '{deactivated_hierarchy.Code.upper()}'",
    )
    return response
