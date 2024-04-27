from typing import Annotated

from fastapi import APIRouter, status, Depends  # type: ignore
from sqlalchemy.orm import Session  # type: ignore

from ...authentication.models.auth import User
from ...common.database import get_db
from ...common.dependencies import get_current_user
from ...hierarchy_mgmt.services.province import ProvinceService
from ...hierarchy_mgmt.models.province import (
    ProvinceBase,
    ProvinceResponse,
    ProvinceUpdate,
)


province_router = APIRouter(prefix="/province", tags=["Province Operations"])

"""
#### Province Routes
- Create New Province
- Get All Provinces
- Get Province by Code
- Update Province by Code
- Activate Province by code
- Deactivate Province by Code
- Approved Province by Code
"""


# Create New Province
@province_router.post(
    "/create",
    status_code=status.HTTP_201_CREATED,
    name="Create New Province",
    response_model=ProvinceResponse,
    # dependencies=[Depends(JWTBearer())],
)
async def create_province(
    province: ProvinceBase,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
):
    new_province = ProvinceService().create_new_province(province, db, current_user)
    # set response body
    response = dict(
        data=new_province,
        status_code=status.HTTP_201_CREATED,
        message=f"Successfully created Province: '{new_province.Name}', with code: '{new_province.Code}'",
    )
    return response


# Get All Provinces
@province_router.get(
    "/",
    status_code=status.HTTP_200_OK,
    name="Get All Provinces",
    response_model=ProvinceResponse,
)
async def get_provinces(
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
):
    provinces = ProvinceService().get_all_provinces(db, current_user)
    # set response body
    response = dict(
        data=provinces,
        status_code=status.HTTP_200_OK,
        message=f"Successfully retrieved all {len(provinces)} Provinces",
    )
    return response


@province_router.get(
    "/{code}",
    status_code=status.HTTP_200_OK,
    name="Get Province by Code",
    response_model=ProvinceResponse,
)
async def get_province_by_code(
    code: str,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
):
    province = ProvinceService().get_province_by_code(code, db, current_user)
    # set response body
    response = dict(
        data=province,
        status_code=status.HTTP_200_OK,
        message=f"Successfully retrieved Province: '{province.Name}' with code: '{province.Code}'",
    )
    return response


# update province by code
@province_router.put(
    "/{code}/update",
    status_code=status.HTTP_200_OK,
    name="Update Province by Code",
    response_model=ProvinceResponse,
)
async def update_province_by_code(
    code: str,
    province: ProvinceUpdate,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
):
    updated_province = ProvinceService().update_province_by_code(
        code, province, db, current_user
    )
    # set response body
    response = dict(
        data=updated_province,
        status_code=status.HTTP_200_OK,
        message=f"Successfully updated Province: '{updated_province.Name}' with code: '{updated_province.Code}'",
    )
    return response


# Activate province by code
@province_router.patch(
    "/{code}/activate",
    status_code=status.HTTP_200_OK,
    name="Activate Province by Code",
    response_model=ProvinceResponse,
)
async def activate_province_by_code(
    code: str,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
):
    activated_province = ProvinceService().activate_province_by_code(
        code, db, current_user
    )
    # set response body
    response = dict(
        data=activated_province,
        status_code=status.HTTP_200_OK,
        message=f"Successfully activated Province: '{activated_province.Name}' with code: '{activated_province.Code}'",
    )
    return response


# deactivate province by code
@province_router.patch(
    "/{code}/deactivate",
    status_code=status.HTTP_200_OK,
    name="Deactivate Province by Code",
    response_model=ProvinceResponse,
)
async def deactivate_province_by_code(
    code: str,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
):
    deactivated_province = ProvinceService().deactivate_province_by_code(
        code, db, current_user
    )
    # set response body
    response = dict(
        data=deactivated_province,
        status_code=status.HTTP_200_OK,
        message=f"Successfully deactivated Province: '{deactivated_province.Name}' with code: '{deactivated_province.Code}'",
    )
    return response


# Approve province by code
@province_router.patch(
    "/{code}/approve",
    status_code=status.HTTP_200_OK,
    name="Approve Province by Code",
    response_model=ProvinceResponse,
)
async def approve_province_by_code(
    code: str,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
):
    approved_province = ProvinceService().approve_province_by_code(
        code, db, current_user
    )
    # set response body
    response = dict(
        data=approved_province,
        status_code=status.HTTP_200_OK,
        message=f"Successfully approved Province: '{approved_province.Name}' with code: '{approved_province.Code}'",
    )
    return response
