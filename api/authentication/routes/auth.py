from typing import Annotated

from fastapi import APIRouter, status, Depends  # type: ignore
from fastapi.security import OAuth2PasswordRequestForm  # type: ignore
from sqlalchemy.orm import Session  # type: ignore

from ..models.auth import (
    TokenLevelResponse,
    TokenResponse,
    User,
    UserAccess,
    UserLevels,
)
from ...common.dependencies import get_current_user, get_current_user_access
from ...authentication.services.auth import AuthService
from ...common.database import get_db

auth_router = APIRouter(prefix="/auth", tags=["Authentication Operations"])

"""
#### Authentication Routes
- Login User
- Select Church Level/Re-authenticate
- Get Current User
- Get Current User Levels
"""


# User Login Route
@auth_router.post(
    "/login",
    status_code=status.HTTP_201_CREATED,
    name="Login User",
    response_model=TokenResponse,
)
async def login(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    db: Session = Depends(get_db),
):
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
    "/select_level/{church_level}",
    status_code=status.HTTP_201_CREATED,
    name="Select Church Level/Re-authenticate",
    response_model=TokenLevelResponse,
)
async def select_level(
    church_level: str,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
):

    # authenticate user
    user_access = AuthService().re_authenticate_user_access(
        church_level, current_user, db
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
        message=f"Successsfully logged in and selected {user_access.ChurchLevel_Code if user_access.ChurchLevel_Code else user_access.Level_Code} Church Level",
        access_token=access_token,
        token_type="bearer",
        user_access=user_access,
    )
    return response


@auth_router.get(
    "/users/me",
    status_code=status.HTTP_200_OK,
    name="Get Current Active User",
    response_model=list[UserAccess],
)
async def read_users_me(
    current_user: Annotated[User, Depends(get_current_user_access)],
):
    return current_user


@auth_router.get(
    "/user_levels/me",
    status_code=status.HTTP_200_OK,
    name="Get Current Active User Levels",
    response_model=list[UserLevels],
)
async def get_user_levels(
    current_user: Annotated[User, Depends(get_current_user)],
    db: Session = Depends(get_db),
):
    user_levels = AuthService().get_user_levels(current_user.Usercode, db)
    return user_levels
