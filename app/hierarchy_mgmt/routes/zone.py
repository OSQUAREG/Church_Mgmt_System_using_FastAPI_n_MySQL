from typing import Annotated

from fastapi import APIRouter, status, Depends  # type: ignore
from sqlalchemy.orm import Session  # type: ignore

from ...authentication.models.auth import User
from ...common.database import get_db
from ...common.dependencies import get_current_user
from ...hierarchy_mgmt.services.zone import ZoneService
from ...hierarchy_mgmt.models.zone import Zone, ZoneResponse, ZoneUpdate

zone_router = APIRouter(prefix="/zone", tags=["Zone Operations"])

"""
#### Zone Routes
- Create New Zone
- Get All Zones
- Get Zone by Code
- Update Zone by Code
- Activate Zone by Code
- Deactivate Zone by Code
"""


# Create New Zone
@zone_router.post(
    "/create",
    status_code=status.HTTP_201_CREATED,
    name="Create New Zone",
    response_model=ZoneResponse,
)
async def create_new_zone(
    zone: Zone,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
):
    new_zone = ZoneService().create_new_province(zone, db, current_user)
    # set response body
    response = dict(
        data=new_zone,
        status_code=status.HTTP_201_CREATED,
        message=f"Successfully created new Zone: {new_zone.Name} with code: {new_zone.Code}",
    )
    return response


# Get All Zones
@zone_router.get(
    "/",
    status_code=status.HTTP_200_OK,
    name="Get All Zones",
    response_model=ZoneResponse,
)
async def get_all_zones(
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
):
    zones = ZoneService().get_all_zones(db)
    # set response body
    response = dict(
        data=zones,
        status_code=status.HTTP_200_OK,
        message=f"Successfully retrieved all {len(zones)} Zones",
    )
    return response


# Get Zone by Code
@zone_router.get(
    "/{code}",
    status_code=status.HTTP_200_OK,
    name="Get Zone by Code",
    response_model=ZoneResponse,
)
async def get_zone_by_code(
    zone_code: str,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
):
    zone = ZoneService().get_zone_by_code(zone_code, db)
    # set response body
    response = dict(
        data=zone,
        status_code=status.HTTP_200_OK,
        message=f"Successfully retrieved Zone: {zone.Name} with code: {zone.Code}",
    )
    return response


# Update Zone by Code
@zone_router.put(
    "/{code}/update",
    status_code=status.HTTP_200_OK,
    name="Update Zone by Code",
    response_model=ZoneResponse,
)
async def update_zone_by_code(
    code: str,
    zone: ZoneUpdate,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
):
    zone = ZoneService().update_zone_by_code(code, zone, db, current_user)
    # set response body
    response = dict(
        data=zone,
        status_code=status.HTTP_200_OK,
        message=f"Successfully updated Zone: {zone.Name} with code: {zone.Code}",
    )
    return response


# Activate Zone by Code
@zone_router.patch(
    "/{code}/activate",
    status_code=status.HTTP_200_OK,
    name="Activate Zone by Code",
    response_model=ZoneResponse,
)
async def activate_zone_by_code(
    code: str,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
):
    zone = ZoneService().activate_zone_by_code(code, db, current_user)
    # set response body
    response = dict(
        data=zone,
        status_code=status.HTTP_200_OK,
        message=f"Successfully activated Zone: {zone.Name} with code: {zone.Code}",
    )
    return response


# Deactivate Zone by Code
@zone_router.patch(
    "/{code}/deactivate",
    status_code=status.HTTP_200_OK,
    name="Deactivate Zone by Code",
    response_model=ZoneResponse,
)
async def deactivate_zone_by_code(
    code: str,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
):
    zone = ZoneService().deactivate_zone_by_code(code, db, current_user)
    # set response body
    response = dict(
        data=zone,
        status_code=status.HTTP_200_OK,
        message=f"Successfully deactivated Zone: {zone.Name} with code: {zone.Code}",
    )
    return response
