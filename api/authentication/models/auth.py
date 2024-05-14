from typing import List, Optional, Union

from pydantic import BaseModel, EmailStr, SecretStr  # type: ignore


class TokenData(BaseModel):
    username: Union[str, None] = None


class TokenLevelData(BaseModel):
    username: Union[str, None] = None
    church_level: Union[str, None] = None


class User(BaseModel):
    Usercode: str
    Email: Optional[EmailStr] = None
    HeadChurch_Code: str
    Is_Active: Optional[bool] = False
    Title: Optional[str] = None
    Titl2: Optional[str] = None
    First_Name: Optional[str] = None
    Last_Name: Optional[str] = None


class TokenResponse(BaseModel):
    status_code: int
    message: str
    access_token: str
    token_type: str
    user: Union[list[User], User, None] = None


class UserLevel(BaseModel):
    Usercode: str
    Email: Optional[EmailStr] = None
    Level_Code: str
    ChurchLevel_Code: Optional[str] = None
    HeadChurch_Code: str


class TokenLevelResponse(BaseModel):
    status_code: int
    message: str
    access_token: str
    token_type: str
    user_access: Union[list[UserLevel], UserLevel, None] = None


class UserAccess(BaseModel):
    Usercode: str
    Email: Optional[EmailStr] = None
    Level_Code: str
    Level_No: int
    Role_Code: str
    Church_Code: Optional[str] = None
    ChurchLevel_Code: Optional[str] = None
    Church_Level: Optional[str] = None
    HeadChurch_Code: str
    Module_Code: str
    SubModule_Code: str
    Access_Type: str
    Title: Optional[str] = None
    Titl2: Optional[str] = None
    First_Name: Optional[str] = None
    Last_Name: Optional[str] = None


class TokenAccessResponse(BaseModel):
    status_code: int
    message: str
    access_token: str
    token_type: str
    user_access: Union[list[UserAccess], UserAccess, None] = None


class UserLevels(BaseModel):
    Level_Code: str
    ChurchLevel_Code: Optional[str] = None
    Church_Level: Optional[str] = None


# class UserPassword(BaseModel):
#     password: SecretStr

#     def __init__(self, **data):
#         super().__init__(**data)
#         if self.password:
#             self.password = self.password.get_secret_value()


# class UserIn(User, UserPassword):
#     pass
