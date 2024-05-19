from datetime import datetime
from typing import Optional, Union

from pydantic import BaseModel, validator  # type: ignore

from .head_church import HeadChurchBase, HeadChurchUpdate, ChurchCode, ChurchStatus


class ChurchBase(HeadChurchBase):
    Level_Code: str
    HeadChurch_Code: str

    @validator("Level_Code")
    def upper_case_strings(cls, v):
        return v.upper() if v else None


class Church(ChurchStatus, ChurchBase, ChurchCode):
    Is_Active: Optional[bool] = True
    Created_Date: Optional[datetime] = None
    Created_By: Optional[str] = None
    Modified_Date: Optional[datetime] = None
    Modified_By: Optional[str] = None


class ChurchResponse(BaseModel):
    status_code: int
    message: str
    data: Union[list[Church], Church, None] = None


class ChurchUpdate(HeadChurchUpdate):
    Level_Code: Optional[str] = None
    HeadChurch_Code: Optional[str] = None

    @validator("Level_Code")
    def upper_case_strings(cls, v):
        return v.upper() if v else None
