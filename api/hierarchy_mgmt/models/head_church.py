from datetime import date, datetime
from typing import Optional, Union

from pydantic import (
    BaseModel,
    EmailStr,
    Field,
    validator,
)  # type: ignore
from pydantic_extra_types.phone_numbers import PhoneNumber  # type: ignore

from ...common.utils import get_phonenumber, custom_title_case


class HeadChurchCode(BaseModel):
    Code: str = Field(examples=["TEST"], max_length=4)

    @validator("Code")
    def uppercase_code(cls, v):
        return v.upper() if v else None


class HeadChurchBase(BaseModel):
    Name: str = Field(examples=["Test Church"], max_length=255)
    Alt_Name: Optional[str] = Field(
        default=None, examples=["Test Church Alternate Name"], max_length=255
    )
    Address: str = Field(examples=["This is the address of the Church"], max_length=255)
    Founding_Date: Optional[date] = Field(default=None, examples=["2000-12-31"])
    About: Optional[str] = Field(default=None, examples=["This is about the Church"])
    Mission: Optional[str] = Field(
        default=None, examples=["This is the mission of the Church"], max_length=1000
    )
    Vision: Optional[str] = Field(
        default=None, examples=["This is the vision of the Church"], max_length=1000
    )
    Motto: Optional[str] = Field(
        default=None, examples=["This is the moto of the Church"], max_length=255
    )
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

    @validator("Name", "Alt_Name", "Address")
    def title_case_strings(cls, v):
        return custom_title_case(v) if v else None

    @validator("About", "Mission", "Vision", "Motto")
    def capitalize_strings(cls, v):
        return v.capitalize() if v else None

    @validator("Contact_No", "Contact_No2")
    def get_phone_numbers(cls, v):
        return get_phonenumber(v) if v else None


class HeadChurch(HeadChurchBase, HeadChurchCode):
    pass


class HeadChurchResponse(BaseModel):
    status_code: int
    message: str
    data: Union[list[HeadChurch], HeadChurch, None] = None


class HeadChurchUpdate(BaseModel):
    Name: str = Field(default=None, examples=["Test Church"], max_length=255)
    Alt_Name: Optional[str] = Field(
        default=None, examples=["Test Church Alternate Name"], max_length=255
    )
    Address: str = Field(
        default=None, examples=["This is the address of the Church"], max_length=255
    )
    Founding_Date: Optional[date] = Field(default=None, examples=["2000-12-31"])
    About: Optional[str] = Field(default=None, examples=["This is about the Church"])
    Mission: Optional[str] = Field(
        default=None, examples=["This is the mission of the Church"], max_length=1000
    )
    Vision: Optional[str] = Field(
        default=None, examples=["This is the vision of the Church"], max_length=1000
    )
    Motto: Optional[str] = Field(
        default=None, examples=["This is the motto of the Church"], max_length=255
    )
    Contact_No: PhoneNumber = Field(
        default=None, examples=["+2348012345678"], max_length=25
    )
    Contact_No2: Optional[PhoneNumber] = Field(
        default=None, examples=["+2348012345678"], max_length=25
    )
    Contact_Email: EmailStr = Field(default=None, max_length=255)
    Contact_Email2: Optional[EmailStr] = Field(default=None, max_length=255)
    Town_Code: str = Field(default=None, max_length=4)
    State_Code: str = Field(default=None, max_length=4)
    Region_Code: str = Field(default=None, max_length=4)
    Country_Code: str = Field(default=None, max_length=4)
    Is_Active: Optional[bool] = None

    @validator("Name", "Alt_Name", "Address")
    def title_case_strings(cls, v):
        return custom_title_case(v) if v else None

    @validator("About", "Mission", "Vision", "Motto")
    def capitalize_strings(cls, v):
        return v.capitalize() if v else None

    @validator("Contact_No", "Contact_No2")
    def get_phone_numbers(cls, v):
        return get_phonenumber(v) if v else None


class HeadChurchCodeIn(BaseModel):
    Code: str = Field(default=None, examples=["TEST"], max_length=4)

    @validator("Code")
    def uppercase_string(cls, v):
        return v.upper() if v else None


class HeadChurchUpdateIn(HeadChurchUpdate, HeadChurchCodeIn):
    pass


class CodeModel(BaseModel):
    Code: str = Field(default=None, examples=["TEST-AAA-000000000"], max_length=18)

    @validator("Code")
    def uppercase_code(cls, v):
        return v.upper() if v else None


class ApproveModel(BaseModel):
    Is_Approved: Optional[bool] = None
    Approved_By: Optional[str] = None
    Approved_Date: Optional[datetime] = None
