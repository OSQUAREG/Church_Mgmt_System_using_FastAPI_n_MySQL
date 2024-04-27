from typing import List, Optional, Union

from pydantic import BaseModel, EmailStr, SecretStr  # type: ignore


class User(BaseModel):
    Usercode: str
    Email: Optional[EmailStr] = None
    HeadChurch_Code: str
    Is_Active: Optional[bool] = False


# class UserPassword(BaseModel):
#     password: SecretStr

#     def __init__(self, **data):
#         super().__init__(**data)
#         if self.password:
#             self.password = self.password.get_secret_value()


# class UserIn(User, UserPassword):
#     pass


class UserAccess(BaseModel):
    Usercode: str
    Email: Optional[EmailStr] = None
    Role_Code: str
    Level_Code: str
    Church_Code: str
    HeadChurch_Code: str
    Module_Code: str
    SubModule_Code: str
    Access_Type: str


# class UserAccessIn(UserAccess, UserPassword):
#     pass


class TokenData(BaseModel):
    username: Union[str, None] = None


class TokenResponse(BaseModel):
    status_code: int
    message: str
    access_token: str
    token_type: str
    user: Union[list[User], User, None] = None


class TokenAccessData(BaseModel):
    username: Union[str, None] = None
    church_level: Union[str, None] = None


class TokenAccessResponse(BaseModel):
    status_code: int
    message: str
    access_token: str
    token_type: str
    user_access: Union[list[UserAccess], UserAccess, None] = None
