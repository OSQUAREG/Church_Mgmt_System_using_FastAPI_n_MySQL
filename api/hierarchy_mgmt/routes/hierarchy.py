from typing import Annotated, Optional

from fastapi import APIRouter, status, Depends, Path  # type: ignore

from ...hierarchy_mgmt.models.hierarchy import HierarchyResponse, HierarchyUpdate
from ...hierarchy_mgmt.services.hierarchy import (
    HierarchyService,
    get_hierarchy_services,
)

hierarchy_router = APIRouter(
    prefix="/admin/hierarchy", tags=["Hierarchy Sub-Module Operations"]
)

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
    hierarchy_services: Annotated[HierarchyService, Depends(get_hierarchy_services)],
    is_active: Optional[bool] = None,
):
    hierarchies = await hierarchy_services.get_all_hierarchies(is_active)
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
    code: Annotated[
        str, Path(..., description="Code of the hierarchy to be retrieved")
    ],
    hierarchy_services: Annotated[HierarchyService, Depends(get_hierarchy_services)],
):
    hierarchy = await hierarchy_services.get_hierarchy_by_code(code)
    # set response body
    response = dict(
        data=hierarchy,
        status_code=status.HTTP_200_OK,
        message=f"Successsfully retrieved {hierarchy.Level_Code} Hierarchy: '{hierarchy.Church_Level} ({hierarchy.ChurchLevel_Code})'",
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
    code: Annotated[
        str, Path(..., description="Code of the hierarchy to be activated")
    ],
    hierarchy_services: Annotated[HierarchyService, Depends(get_hierarchy_services)],
):
    activated_hierarchy = await hierarchy_services.activate_hierarchy_by_code(code)
    print(activated_hierarchy)
    # set response body
    response = dict(
        data=activated_hierarchy,
        status_code=status.HTTP_200_OK,
        message=f"Successsfully activated {activated_hierarchy.Level_Code} Hierarchy: '{activated_hierarchy.Church_Level} ({activated_hierarchy.ChurchLevel_Code})'",
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
    code: Annotated[
        str, Path(..., description="Code of the hierarchy to be deactivated")
    ],
    hierarchy_services: Annotated[HierarchyService, Depends(get_hierarchy_services)],
):
    deactivated_hierarchy = await hierarchy_services.deactivate_hierarchy_by_code(code)
    # set response body
    response = dict(
        data=deactivated_hierarchy,
        status_code=status.HTTP_200_OK,
        message=f"Successsfully deactivated {deactivated_hierarchy.Level_Code} Hierarchy: '{deactivated_hierarchy.Church_Level} ({deactivated_hierarchy.ChurchLevel_Code})'",
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
    code: Annotated[str, Path(..., description="Code of the hierarchy to be updated")],
    hierarchy: HierarchyUpdate,
    hierarchy_services: Annotated[HierarchyService, Depends(get_hierarchy_services)],
):
    updated_hierarchy = await hierarchy_services.update_hierarchy_by_code(
        code, hierarchy
    )
    # set response body
    response = dict(
        data=updated_hierarchy,
        status_code=status.HTTP_200_OK,
        message=f"Successsfully updated {updated_hierarchy.Level_Code} Hierarchy: '{updated_hierarchy.Church_Level} ({updated_hierarchy.ChurchLevel_Code})'",
    )
    return response
