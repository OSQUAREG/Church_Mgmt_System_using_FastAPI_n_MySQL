from datetime import datetime, date, time
from typing import Optional, Union

from pydantic import BaseModel, EmailStr, Field, FilePath, DirectoryPath  # type: ignore
from pydantic_extra_types.phone_numbers import PhoneNumber  # type: ignore

from .head_church import HeadChurch
from ...common.utils import get_phonenumber


class Branch(HeadChurch):
    Area_Code: str
    Zone_Code: str
    Province_Code: str
    HeadChurch_Code: str


class BranchResponse(BaseModel):
    status_code: int
    message: str
    data: Union[list[Branch], Branch, None] = None


class BranchUpdate(HeadChurch):
    Area_Code: Optional[str] = None
    Zone_Code: Optional[str] = None
    Province_Code: Optional[str] = None
    HeadChurch_Code: Optional[str] = None
