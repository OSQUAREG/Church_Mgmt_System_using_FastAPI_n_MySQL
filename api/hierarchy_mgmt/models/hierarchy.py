from datetime import datetime
from typing import Optional, Union

from pydantic import BaseModel, validator  # type: ignore

from ...common.utils import custom_title_case


class Hierarchy(BaseModel):
    Level_Code: Optional[str] = None
    Level_No: Optional[int] = None
    Head_Code: Optional[str] = None
    Church_Level: Optional[str] = None
    ChurchLevel_Code: Optional[str] = None
    Is_Active: Optional[bool] = True
    Created_By: Optional[str] = None
    Created_Date: Optional[datetime] = None
    Modified_By: Optional[str] = None
    Modified_Date: Optional[datetime] = None


class HierarchyResponse(BaseModel):
    status_code: int
    message: str
    data: Union[list[Hierarchy], Hierarchy, None] = None


class HierarchyUpdate(BaseModel):
    Church_Level: Optional[str] = None
    ChurchLevel_Code: Optional[str] = None
    Is_Active: Optional[bool] = True

    @validator("Church_Level")
    def title_case_strings(cls, v):
        return custom_title_case(v) if v else None

    @validator("ChurchLevel_Code")
    def upper_case_strings(cls, v):
        return v.upper() if v else None
