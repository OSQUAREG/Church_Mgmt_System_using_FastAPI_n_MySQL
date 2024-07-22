from typing import Annotated

from fastapi import APIRouter, status, Depends, Path  # type: ignore
from fastapi.security import OAuth2PasswordRequestForm  # type: ignore
from sqlalchemy.orm import Session  # type: ignore

from ...common.database import get_db
from ...common.dependencies import (
    get_current_user,
    get_current_user_access,
    get_route_code,
)
from ...authentication.services.auth import AuthService
from ...authentication.models.auth import (
    TokenLevelResponse,
    TokenResponse,
    User,
    UserAccess,
    UserLevels,
)
from ...swagger_doc import tags

auth_router = APIRouter(
    prefix="/auth", tags=[f"{tags['auth']['module']}: {tags['auth']['submodule']}"]
)

"""
#### Authentication Routes
- Authenticate User
- Re-Authenticate With Church Level
- Get Current User
- Get Current User Access
- Get Current User Levels
"""


# User Login Route
@auth_router.post(
    "/login",
    status_code=status.HTTP_201_CREATED,
    name="Authenticate User",
    summary="Login User",
    description="## User Login Route - Authenticate User",
    response_model=TokenResponse,
)
async def login(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    db: Session = Depends(get_db),
):
    # db = db[0]  # use this when connecting with specified dbs in database.py
    # authenticate user
    user = AuthService().authenticate_user(
        form_data.username,
        form_data.password,
        db,
    )
    # create access token
    access_token = AuthService().create_access_token(
        data={
            "usercode": user.Usercode,
        }
    )
    # set response body
    response = dict(
        status_code=status.HTTP_200_OK,
        message="Successsfully logged in",
        access_token=access_token,
        token_type="bearer",
        user=user,
    )
    return response


# User Select Church Level/Re-authenticate
@auth_router.post(
    "/select_level/{level_code}",
    status_code=status.HTTP_201_CREATED,
    name="Re-Authenticate User",
    summary="Re-Authenticate User With Church Level",
    description="## Re-Authenticate User by Selecting Church Level",
    response_model=TokenLevelResponse,
)
async def select_level(
    level_code: Annotated[
        str, Path(..., description="hierarchy level code of the church to access")
    ],
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
):
    # db = db[0]  # use this when connecting with specified dbs in database.py
    # authenticate user
    user_access = AuthService().re_authenticate_user_access(
        level_code, current_user, db
    )
    # create access token
    access_token = AuthService().create_access_token(
        data={
            "usercode": user_access.Usercode,
            "church_level": user_access.Level_Code,
        }
    )
    # set response body
    response = dict(
        status_code=status.HTTP_200_OK,
        message=f"Successsfully logged in and selected {user_access.Level_Code} Church Level",
        access_token=access_token,
        token_type="bearer",
        user_access=user_access,
    )
    return response


@auth_router.get(
    "/users/me",
    status_code=status.HTTP_200_OK,
    name="Get Current User",
    summary="Get Current Active User",
    description="## Get Current Active User",
    response_model=User,
)
async def read_users_me(
    current_user: Annotated[User, Depends(get_current_user)],
    route_code: Annotated[str, Depends(get_route_code)],
):
    print(route_code)
    return current_user


@auth_router.get(
    "/user_access/me",
    status_code=status.HTTP_200_OK,
    name="Get Current User Access",
    summary="Get Current Active User Access",
    description="## Get Current Active User Access",
    response_model=list[UserAccess],
)
async def read_users_access_me(
    current_user: Annotated[User, Depends(get_current_user_access)],
    route_code: Annotated[str, Depends(get_route_code)],
):
    print(route_code)
    return current_user


@auth_router.get(
    "/user_levels/me",
    status_code=status.HTTP_200_OK,
    name="Get Current User Levels",
    summary="Get Current Active User Levels",
    description="## Get Current Active User Levels",
    response_model=list[UserLevels],
)
async def get_user_levels_me(
    current_user: Annotated[User, Depends(get_current_user)],
    route_code: Annotated[str, Depends(get_route_code)],
    db: Session = Depends(get_db),
):
    print(route_code)
    user_levels = AuthService().get_user_levels(current_user.Usercode, db)
    return user_levels
