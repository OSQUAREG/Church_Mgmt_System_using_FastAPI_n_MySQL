from typing import Annotated, Optional

from fastapi import APIRouter, status, Depends, Query, Path  # type: ignore

from ...hierarchy_mgmt.services import (
    ChurchServices,
    ChurchLeadsServices,
    get_church_services,
    get_church_lead_services,
)
from ...hierarchy_mgmt.models.church_leads import ChurchLeadsResponse
from ...hierarchy_mgmt.models.church import ChurchResponse


churchleads_router = APIRouter(
    prefix=f"/church_leads", tags=["Church Leads Sub-Module Operations"]
)
"""
#### Church Leads Routes
- Get Church Leads by Code
- Get Churches by Lead Code
- Approve Church Lead by Code
"""

churchleads_adm_router = APIRouter(
    prefix=f"/admin/church_leads",
    tags=["Church Leads Sub-Module Operations - Admin only"],
)
"""
#### Church Leads Routes
- Unmap Church Leads by Code
- Map Church Leads by Code
"""


# Get church lead by code
@churchleads_router.get(
    "/{church_code}",
    status_code=status.HTTP_200_OK,
    name="Get Church Lead",
    response_model=ChurchLeadsResponse,
)
async def get_church_leads_by_church_code(
    church_code: Annotated[str, Path(..., description="code of the church mapped")],
    church_lead_services: Annotated[
        ChurchLeadsServices, Depends(get_church_lead_services)
    ],
    is_active: Optional[bool] = None,
):
    church_lead = await church_lead_services.get_church_leads_by_church_code(
        church_code, is_active
    )
    # set response body
    response = dict(
        data=church_lead,
        status_code=status.HTTP_200_OK,
        message=f"Successfully retrieved Church Lead: '{church_lead.Name}' with code: '{church_lead.Code}'",
    )
    return response


# Approve church lead by code
@churchleads_router.patch(
    "/{church_code}/{lead_code}/approve",
    status_code=status.HTTP_200_OK,
    name="Approve Church Lead by Code",
    response_model=ChurchLeadsResponse,
)
async def approve_church_lead_by_code(
    church_code: Annotated[str, Path(..., description="code of the church mapped")],
    lead_code: Annotated[str, Path(..., description="code of the lead church")],
    church_lead_services: Annotated[
        ChurchLeadsServices, Depends(get_church_lead_services)
    ],
):
    approved_church_lead = await church_lead_services.approve_church_lead_by_code(
        church_code, lead_code
    )
    # set response body
    response = dict(
        data=approved_church_lead,
        status_code=status.HTTP_200_OK,
        message=f"Successfully approved the Church Leads for Church: '{approved_church_lead.Name}' with code: '{approved_church_lead.Code}'",
    )
    return response


# Get all churches by lead code
@churchleads_router.get(
    "/{lead_code}/churches",
    status_code=status.HTTP_200_OK,
    name="Get All Churches by Leads Code",
    response_model=ChurchLeadsResponse,
)
async def get_all_churches_by_lead_code(
    lead_code: Annotated[str, Path(..., description="code of the lead church")],
    church_services: Annotated[ChurchServices, Depends(get_church_services)],
    church_lead_services: Annotated[
        ChurchLeadsServices, Depends(get_church_lead_services)
    ],
    is_active: Optional[bool] = None,
):
    lead_church = await church_services.get_church_by_id_code(lead_code)
    churches = await church_lead_services.get_all_churches_by_lead_code(
        lead_code, is_active
    )
    # set response body
    response = dict(
        data=churches,
        status_code=status.HTTP_200_OK,
        message=f"Successfully retrieved all {len(churches)} churches under the Lead Church: '{lead_church.Name}' with code: '{lead_church.Code}'",
    )
    return response


# Get Branches by Church Lead
@churchleads_router.get(
    "/{church_code}/branches",
    status_code=status.HTTP_200_OK,
    name="Get Branches by Church",
    response_model=ChurchResponse,
)
async def get_branches_by_church(
    church_code: Annotated[
        str, Path(..., description="code of the church to retrieve branches")
    ],
    church_lead_services: Annotated[
        ChurchLeadsServices, Depends(get_church_lead_services)
    ],
    status_code: Optional[str] = Query(
        default=None,
        description="(Optional) status of the branches to retrieve: ACT-active, INA-inactive, AWT-awaiting, APR-approved, REJ-rejected",
    ),
):
    branches = await church_lead_services.get_branches_by_church_lead(
        church_code, status_code
    )
    # set response body
    response = dict(
        data=branches,
        status_code=status.HTTP_200_OK,
        message=f"Successfully retrieved all {len(branches)} Branches in church: '{church_code.upper()}'",
    )
    return response


# Unmap church leads by code
@churchleads_adm_router.patch(
    "/{church_code}/unmap",
    status_code=status.HTTP_200_OK,
    name="Unmap Church Lead",
    response_model=ChurchLeadsResponse,
)
async def unmap_church_leads_by_church_code(
    church_code: Annotated[
        str, Path(..., description="code of the church to be unmaped")
    ],
    church_services: Annotated[ChurchServices, Depends(get_church_services)],
    church_lead_services: Annotated[
        ChurchLeadsServices, Depends(get_church_lead_services)
    ],
):
    church = await church_services.get_church_by_id_code(church_code)
    unmap_church_lead = await church_lead_services.unmap_church_leads_by_church_code(
        church_code
    )
    # set response body
    response = dict(
        data=unmap_church_lead,
        status_code=status.HTTP_200_OK,
        message=f"Successfully unmaped all Church Leads from Church: '{church.Name}' with code: '{church.Code}'",
    )
    return response


# Map church lead by code
@churchleads_adm_router.post(
    "/{church_code}/map/{leadchurch_code}",
    status_code=status.HTTP_200_OK,
    name="Map Church Lead",
    response_model=ChurchLeadsResponse,
)
async def map_church_lead_by_code(
    church_code: Annotated[
        str, Path(..., description="code of the church to be mapped")
    ],
    lead_code: Annotated[
        str, Path(..., description="code of the church lead to map to")
    ],
    church_services: Annotated[ChurchServices, Depends(get_church_services)],
    church_lead_services: Annotated[
        ChurchLeadsServices, Depends(get_church_lead_services)
    ],
):
    church = await church_services.get_church_by_id_code(church_code)
    mapped_church_lead = await church_lead_services.map_church_lead_by_code(
        church_code, lead_code
    )
    # set response body
    response = dict(
        data=mapped_church_lead,
        status_code=status.HTTP_200_OK,
        message=f"Successfully mapped all Church Leads from Church: '{church.Name}' with code: '{church.Code}'",
    )
    return response
