from typing import Annotated

from fastapi import APIRouter, status, Depends  # type: ignore
from sqlalchemy.orm import Session  # type: ignore

from ...authentication.models.auth import User
from ...common.database import get_db
from ...common.dependencies import get_current_user
from ...hierarchy_mgmt.services.area import AreaService
from ...hierarchy_mgmt.models.area import Area, AreaResponse, AreaUpdate

area_router = APIRouter(prefix="/area", tags=["Area Operations"])

"""
#### Area Routes
- Create New Area
- Get All Areas
- Get Area by Code
- Update Area by Code
- Activate Area by Code
- Deactivate Area by Code
"""


# Create New Area
@area_router.post(
    "/create",
    status_code=status.HTTP_201_CREATED,
    name="Create New Area",
    response_model=AreaResponse,
)
async def create_new_area(
    area: Area,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
):
    new_area = AreaService().create_new_area(area, db, current_user)
    # set response body
    response = dict(
        data=new_area,
        status_code=status.HTTP_201_CREATED,
        message=f"Successfully created new Area: {new_area.Name} with code: {new_area.Code}",
    )
    return response


# Get All Areas
@area_router.get(
    "/",
    status_code=status.HTTP_200_OK,
    name="Get All Areas",
    response_model=AreaResponse,
)
async def get_all_areas(
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
):
    areas = AreaService().get_all_areas(db)
    # set response body
    response = dict(
        data=areas,
        status_code=status.HTTP_200_OK,
        message=f"Successfully retrieved all {len(areas)} areas",
    )
    return response


# Get Area by Code
@area_router.get(
    "/{code}",
    status_code=status.HTTP_200_OK,
    name="Get Area by Code",
    response_model=AreaResponse,
)
async def get_area_by_code(
    code: str,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
):
    area = AreaService().get_area_by_code(code, db)
    # set response body
    response = dict(
        data=area,
        status_code=status.HTTP_200_OK,
        message=f"Successfully retrieved area: {area.Name} with code: {area.Code}",
    )
    return response


# Update Area by Code
@area_router.put(
    "/{code}/update",
    status_code=status.HTTP_200_OK,
    name="Update Area by Code",
    response_model=AreaResponse,
)
async def update_area_by_code(
    code: str,
    area: AreaUpdate,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
):
    updated_area = AreaService().update_area_by_code(code, area, db, current_user)
    # set response body
    response = dict(
        data=updated_area,
        status_code=status.HTTP_200_OK,
        message=f"Successfully updated area: {updated_area.Name} with code: {updated_area.Code}",
    )
    return response


# Activate Area by Code
@area_router.patch(
    "/{code}/activate",
    status_code=status.HTTP_200_OK,
    name="Activate Area by Code",
    response_model=AreaResponse,
)
async def activate_area_by_code(
    code: str,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
):
    activated_area = AreaService().activate_area_by_code(code, db, current_user)
    # set response body
    response = dict(
        data=activated_area,
        status_code=status.HTTP_200_OK,
        message=f"Successfully activated area: {activated_area.Name} with code: {activated_area.Code}",
    )
    return response


# Deactivate Area by Code
@area_router.patch(
    "/{code}/deactivate",
    status_code=status.HTTP_200_OK,
    name="Deactivate Area by Code",
    response_model=AreaResponse,
)
async def deactivate_area_by_code(
    code: str,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
):
    deactivated_area = AreaService().deactivate_area_by_code(code, db, current_user)
    # set response body
    response = dict(
        data=deactivated_area,
        status_code=status.HTTP_200_OK,
        message=f"Successfully deactivated area: {deactivated_area.Name} with code: {deactivated_area.Code}",
    )
    return response
