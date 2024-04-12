from typing import Optional, Union

from pydantic import BaseModel, EmailStr  # type: ignore


class User(BaseModel):
    Usercode: str
    Email: Optional[EmailStr] = None
    HeadChurch_Code: str
    Is_Active: Optional[bool] = False


class UserReponse(BaseModel):
    status_code: int
    message: str
    data: Union[list[User], User, None] = None


class UserIn(User):
    Password: str


class UserLogin(BaseModel):
    username: str
    password: str


class TokenResponse(BaseModel):
    status_code: int
    message: str
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: Union[str, None] = None
