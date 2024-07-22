from typing import Annotated, Optional

from fastapi import APIRouter, status, Depends, Query, Path  # type: ignore

from ...church_admin.services import ChurchServices, get_church_services
from ...church_admin.models.churches import ChurchBase, ChurchResponse, ChurchUpdate
from ...swagger_doc import tags

church_router = APIRouter(
    prefix=f"/church",
    tags=[f"{tags['churches']['module']}: {tags['churches']['submodule']}"],
)
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
    prefix=f"/admin/church",
    tags=[f"{tags['churches']['module']}: {tags['churches']['submodule']}: Admin only"],
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
    summary="Create New Church",
    description="## Create New Church",
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
        message=f"Successfully created Church: '{new_church.Name} ({new_church.Code})'",
    )
    return response


# Activate church by code
@church_adm_router.patch(
    "/{code}/activate",
    status_code=status.HTTP_200_OK,
    name="Activate Church",
    summary="Activate Church by Code",
    description="## Activate Church by Code",
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
        message=f"Successfully activated Church: '{activated_church.Name} ({activated_church.Code})'",
    )
    return response


# deactivate church by code
@church_adm_router.patch(
    "/{code}/deactivate",
    status_code=status.HTTP_200_OK,
    name="Deactivate Church",
    summary="Deactivate Church by Code",
    description="## Deactivate Church by Code",
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
        message=f"Successfully deactivated Church: '{deactivated_church.Name} ({deactivated_church.Code})'",
    )
    return response


# Approve church by code
@church_router.patch(
    "/{id_code}/approve",
    status_code=status.HTTP_200_OK,
    name="Approve Church",
    summary="Approve Church by Id or Code",
    description="## Approve Church by Id or Code",
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
        message=f"Successfully approved Church: '{approved_church.Name} ({approved_church.Code})'",
    )
    return response


# Get All Churches
@church_router.get(
    "/",
    status_code=status.HTTP_200_OK,
    name="Get All Churches",
    summary="Get All Churches",
    description="## Retrieve All Churches",
    response_model=ChurchResponse,
)
async def get_all_churches(
    church_services: Annotated[ChurchServices, Depends(get_church_services)],
    status_code: Optional[str] = Query(
        default=None,
        description="(Optional) status of the churches to retrieve: ACT-active, INA-inactive, PND-pending, APR-approved, REJ-rejected",
    ),
):
    churches = await church_services.get_all_churches(status_code)
    # set response body
    response = dict(
        data=churches,
        status_code=status.HTTP_200_OK,
        message=(
            f"Successfully retrieved {len(churches)} "
            + ("Churches" if len(churches) > 1 else "Church")
            + ("" if status_code is None else f", with Status: '{status_code.upper()}'")
        ),
    )
    return response


# Get Churches by Level
@church_router.get(
    "/level/{level_code}",
    status_code=status.HTTP_200_OK,
    name="Get Churches by Level",
    summary="Get Churches by Church Level",
    description="## Retrieve Churches by Hierarchical Church Level",
    response_model=ChurchResponse,
)
async def get_churches_by_level(
    level_code: str,
    church_services: Annotated[ChurchServices, Depends(get_church_services)],
    status_code: Optional[str] = Query(
        default=None,
        description="(Optional) status of the churches to retrieve: ACT-active, INA-inactive, PND-pending, APR-approved, REJ-rejected",
    ),
):
    churches = await church_services.get_churches_by_level(level_code, status_code)
    # set response body
    response = dict(
        data=churches,
        status_code=status.HTTP_200_OK,
        message=(
            f"Successfully retrieved {len(churches)} "
            + ("Churches" if len(churches) > 1 else "Church")
            + f" in level: '{level_code.upper()}'"
            + ("" if status_code is None else f", with Status: '{status_code.upper()}'")
        ),
    )
    return response


@church_router.get(
    "/{id_code}",
    status_code=status.HTTP_200_OK,
    name="Get Church",
    summary="Get Church by Id or Code",
    description="## Retrieve Church by Id or Code",
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
        message=f"Successfully retrieved Church: '{church.Name} ({church.Code})'",
    )
    return response


# update church by code
@church_router.put(
    "/{code}/update",
    status_code=status.HTTP_200_OK,
    name="Update Church",
    summary="Update Church by Code",
    description="## Update Church by Code",
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
        message=f"Successfully updated Church: '{updated_church.Name} ({updated_church.Code})'",
    )
    return response
