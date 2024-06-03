from typing import Annotated, Optional

from fastapi import APIRouter, status, Depends, Query, Path  # type: ignore

from ...hierarchy_mgmt.services import ChurchServices, get_church_services
from ...hierarchy_mgmt.models.church import ChurchBase, ChurchResponse, ChurchUpdate


church_router = APIRouter(prefix=f"/church", tags=["Churches Sub-Module Operations"])
"""
#### Church Routes
- Approved Church by Code
- Get All Churches
- Get Branches by Church
- Get Churches by Level
- Get Church by Code
- Update Church by Code
"""

church_adm_router = APIRouter(
    prefix=f"/admin/church", tags=["Churches Sub-Module Operations - Admin only"]
)
"""
#### Church Routes
- Create New Church
- Activate Church by Code
- Deactivate Church by Code
"""


# Create New Church
@church_router.post(
    "/create/{level_code}",
    status_code=status.HTTP_201_CREATED,
    name="Create New Church",
    response_model=ChurchResponse,
)
async def create_new_church(
    level_code: Annotated[
        str, Path(..., description="hierarchical level of the new church")
    ],
    church: ChurchBase,
    church_services: Annotated[ChurchServices, Depends(get_church_services)],
):
    new_church = await church_services.create_new_church(level_code, church)
    # set response body
    response = dict(
        data=new_church,
        status_code=status.HTTP_201_CREATED,
        message=f"Successfully created Church: '{new_church.Name}', with code: '{new_church.Code}'",
    )
    return response


# Activate church by code
@church_adm_router.patch(
    "/{code}/activate",
    status_code=status.HTTP_200_OK,
    name="Activate Church by Code",
    response_model=ChurchResponse,
)
async def activate_church_by_code(
    code: Annotated[str, Path(..., description="code of the church to be activated")],
    church_services: Annotated[ChurchServices, Depends(get_church_services)],
):
    activated_church = await church_services.activate_church_by_code(code)
    # set response body
    response = dict(
        data=activated_church,
        status_code=status.HTTP_200_OK,
        message=f"Successfully activated Church: '{activated_church.Name}' with code: '{activated_church.Code}'",
    )
    return response


# deactivate church by code
@church_adm_router.patch(
    "/{code}/deactivate",
    status_code=status.HTTP_200_OK,
    name="Deactivate Church by Code",
    response_model=ChurchResponse,
)
async def deactivate_church_by_code(
    code: Annotated[str, Path(..., description="code of the church to be deactivated")],
    church_services: Annotated[ChurchServices, Depends(get_church_services)],
):
    deactivated_church = await church_services.deactivate_church_by_code(code)
    # set response body
    response = dict(
        data=deactivated_church,
        status_code=status.HTTP_200_OK,
        message=f"Successfully deactivated Church: '{deactivated_church.Name}' with code: '{deactivated_church.Code}'",
    )
    return response


# Approve church by code
@church_router.patch(
    "/{id_code}/approve",
    status_code=status.HTTP_200_OK,
    name="Approve Church by Id or Code",
    response_model=ChurchResponse,
)
async def approve_church_by_code(
    id_code: Annotated[str, Path(..., description="code of the church to be approved")],
    church_services: Annotated[ChurchServices, Depends(get_church_services)],
):
    approved_church = await church_services.approve_church_by_code(id_code)
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
    church_services: Annotated[ChurchServices, Depends(get_church_services)],
    status_code: Optional[str] = Query(
        default=None,
        description="(Optional) status of the churches to retrieve: ACT-active, INA-inactive, AWT-awaiting, APR-approved, REJ-rejected",
    ),
):
    churches = await church_services.get_all_churches(status_code)
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
    church_services: Annotated[ChurchServices, Depends(get_church_services)],
    status_code: Optional[str] = Query(
        default=None,
        description="(Optional) status of the churches to retrieve: ACT-active, INA-inactive, AWT-awaiting, APR-approved, REJ-rejected",
    ),
):
    churches = await church_services.get_churches_by_level(level_code, status_code)
    # set response body
    response = dict(
        data=churches,
        status_code=status.HTTP_200_OK,
        message=f"Successfully retrieved all {len(churches)} Churches in level: '{level_code.upper()}'",
    )
    return response


@church_router.get(
    "/{id_code}",
    status_code=status.HTTP_200_OK,
    name="Get Church by Id or Code",
    response_model=ChurchResponse,
)
async def get_church_by_id_code(
    id_code: str,
    church_services: Annotated[ChurchServices, Depends(get_church_services)],
):
    church = await church_services.get_church_by_id_code(id_code)
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
    church_services: Annotated[ChurchServices, Depends(get_church_services)],
):
    updated_church = await church_services.update_church_by_code(code, church)
    # set response body
    response = dict(
        data=updated_church,
        status_code=status.HTTP_200_OK,
        message=f"Successfully updated Church: '{updated_church.Name}' with code: '{updated_church.Code}'",
    )
    return response
