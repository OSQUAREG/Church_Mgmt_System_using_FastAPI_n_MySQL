from typing import Annotated

from fastapi import APIRouter, status, Depends, Path  # type: ignore
from sqlalchemy.orm import Session  # type: ignore

from ...common.database import get_db
from ..services.church_heads import (
    HeadChurchServices,
    get_head_church_services,
)
from ..models.church_heads import (
    HeadChurchCreate,
    HeadChurchResponse,
    HeadChurchUpdateIn,
)
from ...swagger_doc import tags

head_chu_router = APIRouter(
    prefix="/head_church",
    tags=[f"{tags['head_church']['module']}: {tags['head_church']['submodule']}"],
)

"""
Head Church Routes
- Create New Head Church
- Get Head Church by Code
- Update Head Church by Code
"""

head_chu_adm_router = APIRouter(
    prefix="/admin/head_church",
    tags=[
        f"{tags['head_church']['module']}: {tags['head_church']['submodule']}: Super Admin only",
    ],
)

"""
Head Church Admin Routes
- Activate Head Church by Code
- Deactivate Head Church by Code
"""


# Create New Head Church
@head_chu_router.post(
    "/create",
    status_code=status.HTTP_201_CREATED,
    name="Create New Head Church",
    summary="Create New Head Church",
    description="## Create New Head Church",
    response_model=HeadChurchResponse,
)
async def create_new_head_church(
    head_church: HeadChurchCreate,
    db: Annotated[Session, Depends(get_db)],
):
    new_head_church = await HeadChurchServices.create_head_church(db, head_church)
    # set response body
    response = dict(
        data=new_head_church,
        status_code=status.HTTP_201_CREATED,
        message=f"Successsfully created new Head Church: {new_head_church.Name} with code: {new_head_church.Code}. \n Please send an email to 'osquaregtech@gmail.com' to activate the Head Church.",
    )
    return response


# Get Head Church by Code
@head_chu_router.get(
    "/{code}",
    status_code=status.HTTP_200_OK,
    name="Get Head Church",
    summary="Get Head Church by Code",
    description="## Retrieve Head Church by Code",
    response_model=HeadChurchResponse,
)
async def get_head_church_by_code(
    code: Annotated[
        str, Path(..., description="code of the head church to be retrieved")
    ],
    head_church_services: Annotated[
        HeadChurchServices, Depends(get_head_church_services)
    ],
):
    head_church = await head_church_services.get_head_church_by_code(code)
    # set response body
    response = dict(
        data=head_church,
        status_code=status.HTTP_200_OK,
        message=f"Successsfully retrieved Head Church: '{head_church.Name}' with code: '{code}'",
    )
    return response


# Update Head Church by Code
@head_chu_router.put(
    "/update/{code}",
    status_code=status.HTTP_200_OK,
    name="Update Head Church",
    summary="Update Head Church by Code",
    description="## Update Head Church by Code",
    response_model=HeadChurchResponse,
)
async def update_head_church_by_code(
    code: Annotated[
        str, Path(..., description="code of the head church to be updated")
    ],
    head_church: HeadChurchUpdateIn,
    head_church_services: Annotated[
        HeadChurchServices, Depends(get_head_church_services)
    ],
):
    updated_head_church = await head_church_services.update_head_church_by_code(
        code, head_church
    )
    # set response body
    response = dict(
        data=updated_head_church,
        status_code=status.HTTP_200_OK,
        message=f"Successsfully updated Head Church: '{updated_head_church.Name}' with code: '{code.upper()}'",
    )
    return response


# Activate Head Church by Code
@head_chu_adm_router.patch(
    "/{code}/activate",
    status_code=status.HTTP_200_OK,
    name="Activate Head Church",
    summary="Activate Head Church by Code",
    description="## Activate Head Church by Code",
    response_model=HeadChurchResponse,
)
async def activate_head_church_by_code(
    code: Annotated[
        str, Path(..., description="code of the head church to be activated")
    ],
    head_church_services: Annotated[
        HeadChurchServices, Depends(get_head_church_services)
    ],
):
    activated_head_church = await head_church_services.activate_head_church_by_code(
        code
    )
    # set response body
    response = dict(
        data=activated_head_church,
        status_code=status.HTTP_200_OK,
        message=f"Successsfully activated Head Church: '{activated_head_church.Name}' with code: '{code.upper()}'",
    )
    return response


# Deactivate Head Church by Code
@head_chu_adm_router.patch(
    "/{code}/deactivate",
    status_code=status.HTTP_200_OK,
    name="Deactivate Head Church",
    summary="Deactivate Head Church by Code",
    description="## Deactivate Head Church by Code",
    response_model=HeadChurchResponse,
)
async def deactivate_head_church_by_code(
    code: Annotated[
        str, Path(..., description="code of the head church to be deactivated")
    ],
    head_church_services: Annotated[
        HeadChurchServices, Depends(get_head_church_services)
    ],
):
    deactivated_head_church = await head_church_services.deactivate_head_church_by_code(
        code
    )
    # set response body
    response = dict(
        data=deactivated_head_church,
        status_code=status.HTTP_200_OK,
        message=f"Successsfully deactivated Head Church: '{deactivated_head_church.Name}' with code: '{code.upper()}'",
    )
    return response
