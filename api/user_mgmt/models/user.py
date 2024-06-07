from datetime import datetime
from typing import List, Optional, Union
from pydantic import BaseModel, EmailStr, SecretStr, Field  # type: ignore


class UserDetails(BaseModel):
    First_Name: Optional[str] = None
    Last_Name: Optional[str] = None
    Title: Optional[str] = None
    Title2: Optional[str] = None
    Usercode: str
    Email: Optional[EmailStr] = None
    HeadChurch_Code: Optional[str] = None
    Is_Active: Optional[bool] = False
    is_Verified: Optional[bool] = False
    Created_By: Optional[str] = None
    Created_Date: Optional[datetime] = None
    Modified_By: Optional[str] = None
    Modified_Date: Optional[datetime] = None


class UserResponse(BaseModel):
    status_code: int
    message: str
    data: Union[List[UserDetails], UserDetails, None] = None
