from typing import Annotated

from fastapi.security import OAuth2PasswordBearer  # type: ignore
from fastapi import Depends, HTTPException, status  # type: ignore
from jose import JWTError, jwt  # type: ignore

from .models.auth import TokenData, User
from .config.config import get_mysql_cursor, close_mysql_cursor, conn
from .utils.auth import get_user, secret_key, algorithm


# OAuth2 Scope
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/token")


# Get into DB
def get_db():
    mydb, cursor = get_mysql_cursor()
    try:
        yield {"mydb": mydb, "cursor": cursor}
    except conn.Error as err:
        raise HTTPException(status_code=500, detail=f"MySQL Error: {err}")
    finally:
        close_mysql_cursor(mydb, cursor)


# Get Current User
async def get_current_user(token: Annotated[str, Depends(oauth2_scheme)]):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, key=secret_key, algorithms=algorithm)  # type: ignore
        username: str = payload.get("sub")  # type: ignore
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except JWTError:
        raise credentials_exception
    user = get_user(token_data.username)  # type: ignore
    if user is None:
        raise credentials_exception
    return user


# Get Current Active User
async def get_current_active_user(
    current_user: Annotated[User, Depends(get_current_user)]
):
    if not current_user.Is_Active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user",
        )
    return current_user
