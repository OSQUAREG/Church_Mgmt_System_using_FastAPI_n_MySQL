from pydantic import BaseModel, Field  # type: ignore
from pydantic_extra_types.phone_numbers import PhoneNumber  # type: ignore
from typing import Optional, Union


class Hierarchy(BaseModel):
    Level_Code: Optional[str] = None
    Level_No: Optional[int] = None
    Head_Code: Optional[str] = None
    Church_Level: Optional[str] = None
    ChurchLevel_Code: Optional[str] = None
    Is_Active: Optional[bool] = True


class HierarchyResponse(BaseModel):
    status_code: int
    message: str
    data: Union[list[Hierarchy], Hierarchy, None] = None


class HierarchyUpdate(BaseModel):
    Church_Level: Optional[str] = None
    ChurchLevel_Code: Optional[str] = None
    Is_Active: Optional[bool] = True
