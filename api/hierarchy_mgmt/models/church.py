from datetime import datetime
from typing import Optional, Union

from pydantic import BaseModel, validator, Field  # type: ignore
from .head_church import HeadChurchBase, HeadChurchUpdate


class ChurchCode(BaseModel):
    Id: int
    Code: Optional[str] = Field(
        default=None, examples=["TEST-AAA-000000000"], max_length=18
    )

    @validator("Code")
    def upper_case_strings(cls, v):
        return v.upper() if v else None


class ChurchBase(HeadChurchBase):
    pass


class ChurchStatus(BaseModel):
    Status: Optional[str] = None
    Status_Date: Optional[datetime] = None
    Status_By: Optional[str] = None


class Church(ChurchStatus, ChurchBase, ChurchCode):
    Level_Code: str
    HeadChurch_Code: str
    Is_Active: Optional[bool] = True
    Created_Date: Optional[datetime] = None
    Created_By: Optional[str] = None
    Modified_Date: Optional[datetime] = None
    Modified_By: Optional[str] = None
    Id: Optional[int] = None


class ChurchResponse(BaseModel):
    status_code: int
    message: str
    data: Union[list[Church], Church, None] = None


class ChurchUpdate(HeadChurchUpdate):
    pass
