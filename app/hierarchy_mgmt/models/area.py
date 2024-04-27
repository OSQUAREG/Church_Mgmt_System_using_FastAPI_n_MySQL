from datetime import datetime, date, time
from typing import Optional, Union

from pydantic import BaseModel, EmailStr, Field, FilePath, DirectoryPath  # type: ignore
from pydantic_extra_types.phone_numbers import PhoneNumber  # type: ignore

from .head_church import HeadChurch, HeadChurchUpdate
from ...common.utils import get_phonenumber


class AreaIn(HeadChurch):
    Zone_Code: str
    Province_Code: str
    HeadChurch_Code: str


class Area(AreaIn):
    Code: str = Field(examples=["TEST"], max_length=18)


class AreaResponse(BaseModel):
    status_code: int
    message: str
    data: Union[list[Area], Area, None] = None


class AreaUpdate(HeadChurchUpdate):
    Zone_Code: Optional[str] = None
    Province_Code: Optional[str] = None
    HeadChurch_Code: Optional[str] = None
