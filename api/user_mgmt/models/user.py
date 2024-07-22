from datetime import datetime
from typing import List, Optional, Union
from pydantic import BaseModel, EmailStr, SecretStr, Field  # type: ignore


class UserSubModules(BaseModel):
    Module_Code: str
    Module_Name: str
    Submodule_Code: str
    Submodule_Name: str
    Access_Type: str
    Level_Code: str
    ChurchLevel_Code: str
    Church_Level: str
    Is_Active: bool
    Status: str


class UserRoles(BaseModel):
    Role_Code: str
    Role_Name: str
    Level_Code: str
    ChurchLevel_Code: str
    Church_Level: str
    Is_Active: bool
    Status: str


class UserDetails(BaseModel):
    Id: Optional[int] = None
    Usercode: str
    Email: Optional[EmailStr] = None
    Roles: Union[List[UserRoles], UserRoles, None] = None
    Level_Code: Optional[str] = None
    SubModules: Union[List[UserSubModules], UserSubModules, None] = None
    First_Name: Optional[str] = None
    Last_Name: Optional[str] = None
    Title: Optional[str] = None
    Title2: Optional[str] = None
    Is_Member: Optional[bool] = False
    Branch_Code: Optional[str] = None
    Branch_Name: Optional[str] = None
    HeadChurch_Code: Optional[str] = None
    Is_Active: Optional[bool] = False
    is_Verified: Optional[bool] = False
    Password_Reset: Optional[bool] = False
    Created_By: Optional[str] = None
    Created_Date: Optional[datetime] = None
    Modified_By: Optional[str] = None
    Modified_Date: Optional[datetime] = None
    Status: Optional[str] = None
    Status_By: Optional[str] = None
    Status_Date: Optional[datetime] = None


class UserResponse(BaseModel):
    status_code: int
    message: str
    data: Union[List[UserDetails], UserDetails, None] = None
