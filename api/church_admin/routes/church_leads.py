from typing import Annotated, Optional

from fastapi import APIRouter, status, Depends, Query, Path  # type: ignore

from ...church_admin.services import (
    ChurchServices,
    ChurchLeadsServices,
    get_church_services,
    get_church_lead_services,
)
from ...church_admin.models.church_leads import (
    ChurchLeadHierarchyResponse,
    ChurchLeadsResponse,
)
from ..models.churches import ChurchResponse
from ...swagger_doc import tags

churchleads_router = APIRouter(
    prefix=f"/church_leads",
    tags=[f"{tags['church_leads']['module']}: {tags['church_leads']['submodule']}"],
)
"""
#### Church Leads Routes
- Get Church Leads by Code
- Get Churches by Lead Code
- Approve Church Lead by Code
"""

churchleads_adm_router = APIRouter(
    prefix=f"/admin/church_leads",
    tags=[
        f"{tags['church_leads']['module']}: {tags['church_leads']['submodule']}: Admin only"
    ],
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
    summary="Get Church Lead by Code",
    description="## Retrieve Church Lead by Code",
    response_model=ChurchLeadsResponse,
)
async def get_church_leads_by_church_code(
    church_code: Annotated[str, Path(..., description="code of the church mapped")],
    church_lead_services: Annotated[
        ChurchLeadsServices, Depends(get_church_lead_services)
    ],
    status_code: Optional[str] = Query(
        default=None,
        description="(Optional) status of the branches to retrieve: ACT-active, INA-inactive, AWT-awaiting, APR-approved, REJ-rejected",
    ),
):
    church_lead = await church_lead_services.get_church_leads_by_church_code(
        church_code, status_code
    )
    # set response body
    response = dict(
        data=church_lead,
        status_code=status.HTTP_200_OK,
        message=(
            f"Successfully retrieved {len(church_lead)} "
            + ("Church Leads" if len(church_lead) > 1 else "Church Lead")
            + f" for the Church: '{church_code.upper()}'"
            + ("" if status_code is None else f", with Status: '{status_code.upper()}'")
        ),
    )
    return response


# Approve church lead by code
@churchleads_router.patch(
    "/{church_code}/{lead_code}/approve",
    status_code=status.HTTP_200_OK,
    name="Approve Church Lead",
    summary="Approve Church Lead by Code",
    description="## Approve Church Lead by Code",
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
        message=f"Successfully approved the Church Lead: '{approved_church_lead.LeadChurch_Name} ({approved_church_lead.LeadChurch_Code}) for the Church: '{approved_church_lead.Church_Name} ({approved_church_lead.Church_Code})'",
    )
    return response


# Get churches by lead code
@churchleads_router.get(
    "/{lead_code}/churches",
    status_code=status.HTTP_200_OK,
    name="Get Churches by Lead",
    summary="Get Churches by Leads Code",
    description="## Retrieve Churches by Leads Code",
    response_model=ChurchResponse,
)
async def get_all_churches_by_lead_code(
    lead_code: Annotated[str, Path(..., description="code of the lead church")],
    church_services: Annotated[ChurchServices, Depends(get_church_services)],
    church_lead_services: Annotated[
        ChurchLeadsServices, Depends(get_church_lead_services)
    ],
    status_code: Optional[str] = Query(
        default=None,
        description="(Optional) status of the branches to retrieve: ACT-active, INA-inactive, AWT-awaiting, APR-approved, REJ-rejected.",
    ),
    level_code: Optional[str] = Query(
        default=None,
        description="(Optional) church hierarchical level to retrieve.",
    ),
):
    lead_church = await church_services.get_church_by_id_code(lead_code)
    churches = await church_lead_services.get_all_churches_by_lead_code(
        lead_code, status_code, level_code
    )
    # set response body
    response = dict(
        data=churches,
        status_code=status.HTTP_200_OK,
        message=(
            f"Successfully retrieved {len(churches)} "
            + ("Churches" if len(churches) > 1 else "Church")
            + f" under the Lead Church: '{lead_church.Name} ({lead_church.Code})'"
            + ("" if status_code is None else f", with Status: '{status_code.upper()}'")
            + (
                ""
                if level_code is None
                else f", with Church Level: '{level_code.upper()}'"
            )
        ),
    )
    return response


# Get Branches by Church Lead
@churchleads_router.get(
    "/{church_code}/branches",
    status_code=status.HTTP_200_OK,
    name="Get Branches by Church Lead",
    summary="Get Branches by Church Lead Code",
    description="## Retrieve Branches by Church Lead Code",
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
        message=(
            f"Successfully retrieved {len(branches)} "
            + ("Branches" if len(branches) > 1 else "Branch")
            + f" under the Lead Church: '{church_code.upper()}'"
            + ("" if status_code is None else f", with Status: '{status_code.upper()}'")
        ),
    )
    return response


# Unmap church leads by code
@churchleads_adm_router.patch(
    "/{church_code}/unmap",
    status_code=status.HTTP_200_OK,
    name="Unmap Church Lead",
    summary="Unmap Church Lead by Church Code",
    description="## Unmap Church Leads by Church code",
    response_model=ChurchLeadsResponse,
)
async def unmap_church_leads_by_church(
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
    "/{church_code}/map/{lead_code}",
    status_code=status.HTTP_200_OK,
    name="Map Church Lead",
    summary="Map Church Lead",
    description="## Map Church Leads",
    response_model=ChurchLeadsResponse,
)
async def map_church_to_lead_by_code(
    church_code: Annotated[
        str, Path(..., description="code of the church to be mapped")
    ],
    lead_code: Annotated[
        str, Path(..., description="code of the church lead to map to")
    ],
    church_lead_services: Annotated[
        ChurchLeadsServices, Depends(get_church_lead_services)
    ],
):
    mapped = await church_lead_services.map_church_lead_by_code(church_code, lead_code)
    # set response body
    response = dict(
        data=mapped,
        status_code=status.HTTP_200_OK,
        message=f"Successfully mapped Church: '{mapped.Church_Code}' to Lead Church: '{mapped.LeadChurch_Code}",
    )
    return response


# Get Church Lead Hierarchy
@churchleads_router.get(
    "/{church_code}/hierarchy",
    status_code=status.HTTP_200_OK,
    name="Get Church Lead Hierarchy",
    summary="Get Church Lead Hierarchy by Church Code",
    description="## Retrieve Church Lead Hierarchy by Church Code",
    response_model=ChurchLeadHierarchyResponse,
)
async def get_church_lead_hierarchy_by_church_code(
    church_code,
    church_lead_services: Annotated[
        ChurchLeadsServices, Depends(get_church_lead_services)
    ],
):
    hierarchy = await church_lead_services.get_church_lead_hierarchy_by_church_code(
        church_code
    )
    # set response body
    response = dict(
        data=hierarchy,
        status_code=status.HTTP_200_OK,
        message=f"Successfully retrieved the Church Lead Hierarchy for the Church: '{hierarchy.Church_Name} ({hierarchy.Church_Code})'",
    )
    return response
