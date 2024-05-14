from typing import Annotated

from fastapi import APIRouter, status, Depends, Form  # type: ignore
from sqlalchemy.orm import Session  # type: ignore

from ...common.database import get_db
from ...common.dependencies import get_current_user, get_current_user_access
from ...authentication.models.auth import User, UserAccess
from ...hierarchy_mgmt.services.hierarchy import HierarchyService
from ...hierarchy_mgmt.models.hierarchy import HierarchyResponse, HierarchyUpdate

hierarchy_router = APIRouter(prefix="/hierarchy", tags=["Hierarchy Operations"])

"""
Hierarchy Routes
- Get All Hierarchies
- Get Hierarchy by Code
- Activate Hierarchy by Code
- Deactivate Hierarchy by Code
- Update Hierarchy by Code

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
    current_user_access: Annotated[UserAccess, Depends(get_current_user_access)],
):
    hierarchies = await HierarchyService().get_all_hierarchies(
        db, current_user, current_user_access
    )
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
    current_user_access: Annotated[UserAccess, Depends(get_current_user_access)],
):
    hierarchy = await HierarchyService().get_hierarchy_by_code(
        code, db, current_user, current_user_access
    )
    # set response body
    response = dict(
        data=hierarchy,
        status_code=status.HTTP_200_OK,
        message=f"Successsfully retrieved {hierarchy.Level_Code} Hierarchy: '{hierarchy.Church_Level}', with code: '{hierarchy.ChurchLevel_Code}'",
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
    current_user_access: Annotated[UserAccess, Depends(get_current_user_access)],
):
    activated_hierarchy = await HierarchyService().activate_hierarchy_by_code(
        code, db, current_user, current_user_access
    )
    print(activated_hierarchy)
    # set response body
    response = dict(
        data=activated_hierarchy,
        status_code=status.HTTP_200_OK,
        message=f"Successsfully activated {activated_hierarchy.Level_Code} Hierarchy: '{activated_hierarchy.Church_Level}', with code: '{activated_hierarchy.ChurchLevel_Code}'",
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
    current_user_access: Annotated[UserAccess, Depends(get_current_user_access)],
):
    deactivated_hierarchy = await HierarchyService().deactivate_hierarchy_by_code(
        code, db, current_user, current_user_access
    )
    # set response body
    response = dict(
        data=deactivated_hierarchy,
        status_code=status.HTTP_200_OK,
        message=f"Successsfully deactivated {deactivated_hierarchy.Level_Code} Hierarchy: '{deactivated_hierarchy.Church_Level}', with code: '{deactivated_hierarchy.ChurchLevel_Code}'",
    )
    return response


# Update Hierarchy by Code
@hierarchy_router.put(
    "/{code}/update",
    status_code=status.HTTP_200_OK,
    name="Update Hierarchy by Code",
    response_model=HierarchyResponse,
)
async def update_hierarchy_by_code(
    code: str,
    hierarchy: HierarchyUpdate,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
    current_user_access: Annotated[UserAccess, Depends(get_current_user_access)],
):
    updated_hierarchy = await HierarchyService().update_hierarchy_by_code(
        code, hierarchy, db, current_user, current_user_access
    )
    # set response body
    response = dict(
        data=updated_hierarchy,
        status_code=status.HTTP_200_OK,
        message=f"Successsfully updated {updated_hierarchy.Level_Code} Hierarchy: '{updated_hierarchy.Church_Level}', with code: '{updated_hierarchy.ChurchLevel_Code}'",
    )
    return response
