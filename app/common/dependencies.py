from typing import Annotated

from fastapi import Depends, HTTPException, status  # type: ignore
from fastapi.security import OAuth2PasswordBearer  # type: ignore
from sqlalchemy.orm import Session  # type: ignore

from .database import get_db
from ..authentication.services.auth import AuthService, auth_credentials_exception

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")


# Get Current User
async def get_current_user(
    token: Annotated[str, Depends(oauth2_scheme)],
    db: Session = Depends(get_db),
):
    # verify access token to get token data (username)
    token_data = AuthService().verify_access_token(token)
    # get user from db
    current_user = AuthService().get_user(token_data.username, db)  # type: ignore
    # checks if user exist
    if current_user is None:
        raise auth_credentials_exception
    # checks if user is active
    if not current_user.Is_Active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user",
        )
    return current_user


async def get_current_user_access(
    token: Annotated[str, Depends(oauth2_scheme)],
    db: Session = Depends(get_db),
):
    # verify access token to get token data (church_level)
    token_data = AuthService().re_verify_access_token(token)
    current_user = AuthService().get_user_access(token_data.username, token_data.church_level, db)  # type: ignore
    # checks if user exist
    if current_user is None:
        raise auth_credentials_exception
    return current_user
