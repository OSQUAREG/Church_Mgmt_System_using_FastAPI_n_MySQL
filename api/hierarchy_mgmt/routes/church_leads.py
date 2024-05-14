from typing import Annotated

from fastapi import APIRouter, status, Depends, Form  # type: ignore
from sqlalchemy.orm import Session  # type: ignore

from ...authentication.models.auth import User
from ...common.database import get_db
from ...common.dependencies import get_current_user, get_current_user_access
from ...hierarchy_mgmt.services import ChurchServices, ChurchLeadsServices
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
async def get_church_lead_by_code(
    code: str,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
    current_user_access: Annotated[User, Depends(get_current_user_access)],
):
    church_lead = await ChurchLeadsServices().get_church_leads_by_code(
        code, db, current_user, current_user_access
    )
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
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
    current_user_access: Annotated[User, Depends(get_current_user_access)],
):
    church = await ChurchServices().get_church_by_code(
        code, db, current_user, current_user_access
    )
    unmap_church_lead = await ChurchLeadsServices().unmap_church_leads_by_code(
        code, db, current_user, current_user_access
    )
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
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
    current_user_access: Annotated[User, Depends(get_current_user_access)],
):
    church = await ChurchServices().get_church_by_code(
        code, db, current_user, current_user_access
    )
    mapped_church_lead = await ChurchLeadsServices().map_church_lead_by_code(
        code, lead_code, db, current_user, current_user_access
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
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
    current_user_access: Annotated[User, Depends(get_current_user_access)],
):
    approved_church_lead = await ChurchLeadsServices().approve_church_lead_by_code(
        code, lead_code, db, current_user, current_user_access
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
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
    current_user_access: Annotated[User, Depends(get_current_user_access)],
):
    lead_church = await ChurchServices().get_church_by_code(
        code, db, current_user, current_user_access
    )
    churches = await ChurchLeadsServices().get_all_churches_by_lead_code(
        code, db, current_user, current_user_access
    )
    # set response body
    response = dict(
        data=churches,
        status_code=status.HTTP_200_OK,
        message=f"Successfully retrieved all {len(churches)} churches under the Lead Church: '{lead_church.Name}' with code: '{lead_church.Code}'",
    )
    return response
