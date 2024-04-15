from datetime import datetime, date, time

from pydantic import BaseModel, Field  # type: ignore
from pydantic_extra_types.phone_numbers import PhoneNumber  # type: ignore
from typing import Optional, Union

# from phonenumbers import parse, is_valid_number


class Hierarchy(BaseModel):
    Code: str = Field(examples=["CHU"], max_length=3)
    Hierarchy: str = Field(examples=["Church"], max_length=255)
    Alt_Name: Optional[str] = Field(
        default=None, examples=["Head Church"], max_length=255
    )
    Rank_No: int = Field(examples=[1])
    Is_Active: Optional[bool] = True


class HierarchyResponse(BaseModel):
    status_code: int
    message: str
    data: Union[list[Hierarchy], Hierarchy, None] = None
