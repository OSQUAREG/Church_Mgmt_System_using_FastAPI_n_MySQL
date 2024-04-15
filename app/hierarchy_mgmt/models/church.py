from datetime import datetime, date, time
from typing import Optional, Union

from pydantic import BaseModel, EmailStr, Field, FilePath, DirectoryPath  # type: ignore
from pydantic_extra_types.phone_numbers import PhoneNumber  # type: ignore

from ...common.utils import get_phonenumber


class HeadChurch(BaseModel):
    Code: str = Field(examples=["CNAC"], max_length=4)
    Name: str = Field(
        examples=["Church of Nigeria (Anglican Communion)"], max_length=255
    )
    Alt_Name: Optional[str] = None
    Address: str = Field(max_length=255)
    Founding_Date: Optional[date] = Field(examples=["2000-12-31"])
    About: Optional[str] = None
    Mission: Optional[str] = Field(default=None, max_length=1000)
    Vision: Optional[str] = Field(default=None, max_length=1000)
    Motto: Optional[str] = Field(default=None, max_length=255)
    Contact_No: PhoneNumber = Field(examples=["+2348012345678"], max_length=25)
    Contact_No2: Optional[PhoneNumber] = Field(
        default=None, examples=["+2348012345678"], max_length=25
    )
    Contact_Email: EmailStr = Field(max_length=255)
    Contact_Email2: Optional[EmailStr] = Field(default=None, max_length=255)
    Town_Code: str = Field(max_length=4)
    State_Code: str = Field(max_length=4)
    Region_Code: str = Field(max_length=4)
    Country_Code: str = Field(max_length=4)
    Is_Active: Optional[bool] = True

    def __init__(self, **data):
        super().__init__(**data)
        if self.Contact_No:
            self.Contact_No = get_phonenumber(self.Contact_No)
        if self.Contact_No2:
            self.Contact_No2 = get_phonenumber(self.Contact_No2)


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
