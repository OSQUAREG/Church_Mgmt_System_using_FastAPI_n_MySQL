import os
from datetime import datetime, timedelta, timezone
from typing import Union

from dotenv import load_dotenv
from fastapi import HTTPException, status  # type: ignore
from passlib.context import CryptContext  # type: ignore
from jose import jwt  # type: ignore

from ..models.auth import UserIn
from ..config.config import get_mysql_cursor, close_mysql_cursor, conn


load_dotenv()


secret_key = os.getenv("SECRET_KEY")
algorithm = os.getenv("ALGORITHM")
access_token_expire_minutes = os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES")


# Password Context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


# Verify Password
def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


# Get Hash Password
def get_password_hash(password):
    return pwd_context.hash(password)


# Get User from DB
def get_user(username: str):
    try:
        mydb, cursor = get_mysql_cursor()
        cursor.execute(
            "SELECT * FROM tblUser WHERE Usercode = %s;",
            (username,),
        )
        user = cursor.fetchone()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found",
            )
        return UserIn(**user)
    except conn.Error as err:
        raise HTTPException(status_code=500, detail=f"MySQL Error: {err}")
    finally:
        close_mysql_cursor(mydb, cursor)


# Authenticate User
def authenticate_user(username: str, password: str):
    user = get_user(username)
    if not user:
        return False
    if not verify_password(password, user.Password):
        return False
    return user


# Create Access Token
def create_access_token(data: dict, expires_delta: Union[timedelta, None] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, key=secret_key, algorithm=algorithm)  # type: ignore
    return encoded_jwt
