from typing import Annotated
from fastapi import Depends, HTTPException, status  # type: ignore
from fastapi.security import OAuth2PasswordBearer  # type: ignore
from sqlalchemy import text  # type: ignore
from sqlalchemy.orm import Session  # type: ignore

from ...common.database import get_db

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")


class UserService:
    pass
