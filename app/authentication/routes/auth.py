from datetime import timedelta
from typing import Annotated

from fastapi import APIRouter, HTTPException, status, Depends  # type: ignore
from fastapi.security import OAuth2PasswordRequestForm  # type: ignore

from ..models.auth import TokenResponse, User
from ...common.dependencies import get_current_active_user
from ...common.utils import (
    authenticate_user,
    create_access_token,
    access_token_expire_minutes,
)

auth_router = APIRouter(prefix="/auth", tags=["Authentication Operations"])


@auth_router.post(
    "/token",
    status_code=status.HTTP_201_CREATED,
    name="Login User",
    response_model=TokenResponse,
    response_description="Successsfully logged in",
)
async def login(form_data: Annotated[OAuth2PasswordRequestForm, Depends()]):
    user = authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Oops! Incorrect username or password",
        )
    access_token_expires = timedelta(minutes=int(access_token_expire_minutes))  # type: ignore
    access_token = create_access_token(
        data={"sub": user.Usercode},
        expires_delta=access_token_expires,
    )
    # # set response body
    response = dict(
        status_code=status.HTTP_200_OK,
        message="Successsfully logged in",
        access_token=access_token,
        token_type="bearer",
    )
    return response


@auth_router.get(
    "/users/me",
    status_code=status.HTTP_200_OK,
    name="Get Current Active User",
    response_model=User,
    response_description="Successsfully retrieved current active user",
)
async def read_users_me(
    current_user: Annotated[User, Depends(get_current_active_user)]
):
    return current_user
