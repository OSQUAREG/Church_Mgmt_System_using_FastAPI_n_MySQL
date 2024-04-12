import datetime
from pydantic import BaseModel, EmailStr
from typing import Optional, Union


class Hierarchy(BaseModel):
    Code: str
    Hierarchy: str
    Alt_Name: Optional[str] = None
    Rank_No: int
    Is_Active: Optional[bool]


class HierarchyResponse(BaseModel):
    status_code: int
    message: str
    data: Union[list[Hierarchy], Hierarchy, None] = None


class HeadChurch(BaseModel):
    Code: str
    Name: str
    Alt_Name: Optional[str] = None
    Address: str
    Founding_Date: Optional[datetime.date] = None
    About: Optional[str] = None
    Mission: Optional[str] = None
    Vision: Optional[str] = None
    Motto: Optional[str] = None
    Contact_No: str
    Contact_No2: Optional[str] = None
    Contact_Email: str
    Contact_Email2: Optional[str] = None
    Town_Code: str
    State_Code: str
    Region_Code: str
    Country_Code: str
    Is_Active: Optional[bool] = True


class HeadChurchResponse(BaseModel):
    status_code: int
    message: str
    data: Union[list[HeadChurch], HeadChurch, None] = None


class Province(HeadChurch):
    HeadChurch_Code: str


class ProvinceResponse(BaseModel):
    status_code: int
    message: str
    data: Union[list[Province], Province, None] = None


class Zone(HeadChurch):
    Province_Code: str
    HeadChurch_Code: str


class ZoneResponse(BaseModel):
    status_code: int
    message: str
    data: Union[list[Zone], Zone, None] = None


class Area(HeadChurch):
    Zone_Code: str
    Province_Code: str
    HeadChurch_Code: str


class AreaResponse(BaseModel):
    status_code: int
    message: str
    data: Union[list[Area], Area, None] = None


class Branch(HeadChurch):
    Area_Code: str
    Zone_Code: str
    Province_Code: str
    HeadChurch_Code: str


class BranchResponse(BaseModel):
    status_code: int
    message: str
    data: Union[list[Branch], Branch, None] = None
