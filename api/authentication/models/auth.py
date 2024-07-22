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
    Head_Code: str
    Is_Member: Optional[bool] = False
    Is_Active: Optional[bool] = False
    Title: Optional[str] = None
    Titl2: Optional[str] = None
    First_Name: Optional[str] = None
    Last_Name: Optional[str] = None
    Head_Name: Optional[str] = None


class TokenResponse(BaseModel):
    status_code: int
    message: str
    access_token: str
    token_type: str
    user: Union[list[User], User, None] = None


class UserLevel(BaseModel):
    Usercode: str
    Email: Optional[EmailStr] = None
    Level_Code: Optional[str] = None
    Level_Name: Optional[str] = None
    Church_Code: Optional[str] = None
    Church_Name: Optional[str] = None
    Head_Code: str
    Title: Optional[str] = None
    Titl2: Optional[str] = None
    First_Name: Optional[str] = None
    Last_Name: Optional[str] = None


class TokenLevelResponse(BaseModel):
    status_code: int
    message: str
    access_token: str
    token_type: str
    user_access: Union[list[UserLevel], UserLevel, None] = None


class UserAccess(BaseModel):
    Usercode: str
    Email: Optional[EmailStr] = None
    Is_Member: Optional[bool] = False
    Role_Code: str
    Hierarchy_Code: str
    Level_No: int
    Level_Code: Optional[str] = None
    Level_Name: Optional[str] = None
    Church_Code: Optional[str] = None
    Group_Code: Optional[str] = None
    Head_Code: str
    Module_Code: str
    SubModule_Code: str
    Access_Type: str
    Title: Optional[str] = None
    Titl2: Optional[str] = None
    First_Name: Optional[str] = None
    Last_Name: Optional[str] = None


# class TokenAccessResponse(BaseModel):
#     status_code: int
#     message: str
#     access_token: str
#     token_type: str
#     user_access: Union[list[UserAccess], UserAccess, None] = None


class UserLevels(BaseModel):
    Level_Code: str
    Level_Name: Optional[str] = None


# class UserPassword(BaseModel):
#     password: SecretStr

#     def __init__(self, **data):
#         super().__init__(**data)
#         if self.password:
#             self.password = self.password.get_secret_value()


# class UserIn(User, UserPassword):
#     pass
