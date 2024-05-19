from typing import Annotated, Optional

from fastapi import APIRouter, status, Depends, Form  # type: ignore

from ...hierarchy_mgmt.services import (
    ChurchServices,
    ChurchLeadsServices,
    get_church_services,
    get_church_lead_services,
)
from ...hierarchy_mgmt.models.church_leads import ChurchLeadsResponse


churchleads_router = APIRouter(
    prefix=f"/church_leads", tags=["Church Leads Operations"]
)

"""
#### Church Leads Routes
- Get Church Leads by Code
- Unmap Church Leads by Code
- Map Church Leads by Code
- Get Churches by Lead Code
"""


# Get church lead by code
@churchleads_router.get(
    "/{code}",
    status_code=status.HTTP_200_OK,
    name="Get Church Lead",
    response_model=ChurchLeadsResponse,
)
async def get_church_leads_by_code(
    code: str,
    church_lead_services: Annotated[
        ChurchLeadsServices, Depends(get_church_lead_services)
    ],
    is_active: Optional[bool] = None,
):
    church_lead = await church_lead_services.get_church_leads_by_code(code, is_active)
    # set response body
    response = dict(
        data=church_lead,
        status_code=status.HTTP_200_OK,
        message=f"Successfully retrieved Church Lead: '{church_lead.Name}' with code: '{church_lead.Code}'",
    )
    return response


# Unmap church leads by code
@churchleads_router.patch(
    "/{code}/unmap",
    status_code=status.HTTP_200_OK,
    name="Unmap Church Lead",
    response_model=ChurchLeadsResponse,
)
async def unmap_church_lead_by_code(
    code: str,
    church_services: Annotated[ChurchServices, Depends(get_church_services)],
    church_lead_services: Annotated[
        ChurchLeadsServices, Depends(get_church_lead_services)
    ],
):
    church = await church_services.get_church_by_code(code)
    unmap_church_lead = await church_lead_services.unmap_church_leads_by_code(code)
    # set response body
    response = dict(
        data=unmap_church_lead,
        status_code=status.HTTP_200_OK,
        details=f"Successfully unmaped all Church Leads from Church: '{church.Name}' with code: '{church.Code}'",
    )
    return response


# Map church lead by code
@churchleads_router.post(
    "/{code}/map/{lead_code}",
    status_code=status.HTTP_200_OK,
    name="Map Church Lead",
    response_model=ChurchLeadsResponse,
)
async def map_church_lead_by_code(
    code: Annotated[str, Form],
    lead_code: Annotated[str, Form],
    church_services: Annotated[ChurchServices, Depends(get_church_services)],
    church_lead_services: Annotated[
        ChurchLeadsServices, Depends(get_church_lead_services)
    ],
):
    church = await church_services.get_church_by_code(code)
    mapped_church_lead = await church_lead_services.map_church_lead_by_code(
        code, lead_code
    )
    # set response body
    response = dict(
        data=mapped_church_lead,
        status_code=status.HTTP_200_OK,
        details=f"Successfully mapped all Church Leads from Church: '{church.Name}' with code: '{church.Code}'",
    )
    return response


# Approve church lead by code
@churchleads_router.patch(
    "/{code}/approve",
    status_code=status.HTTP_200_OK,
    name="Approve Church Lead by Code",
    response_model=ChurchLeadsResponse,
)
async def approve_church_lead_by_code(
    code: Annotated[str, Form],
    lead_code: Annotated[str, Form],
    church_lead_services: Annotated[
        ChurchLeadsServices, Depends(get_church_lead_services)
    ],
):
    approved_church_lead = await church_lead_services.approve_church_lead_by_code(
        code, lead_code
    )
    # set response body
    response = dict(
        data=approved_church_lead,
        status_code=status.HTTP_200_OK,
        details=f"Successfully approved the Church Leads for Church: '{approved_church_lead.Name}' with code: '{approved_church_lead.Code}'",
    )
    return response


# Get all churches by lead code
@churchleads_router.get(
    "/{code}/all",
    status_code=status.HTTP_200_OK,
    name="Get All Churches by Leads Code",
    response_model=ChurchLeadsResponse,
)
async def get_all_churches_by_lead_code(
    code: str,
    church_services: Annotated[ChurchServices, Depends(get_church_services)],
    church_lead_services: Annotated[
        ChurchLeadsServices, Depends(get_church_lead_services)
    ],
    is_active: Optional[bool] = None,
):
    lead_church = await church_services.get_church_by_code(code)
    churches = await church_lead_services.get_all_churches_by_lead_code(code, is_active)
    # set response body
    response = dict(
        data=churches,
        status_code=status.HTTP_200_OK,
        message=f"Successfully retrieved all {len(churches)} churches under the Lead Church: '{lead_church.Name}' with code: '{lead_church.Code}'",
    )
    return response
