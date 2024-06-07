from datetime import date, datetime
from typing import Optional, Union

from pydantic import BaseModel, EmailStr, Field, validator  # type: ignore
from pydantic_extra_types.phone_numbers import PhoneNumber  # type: ignore

from ...common.utils import get_phonenumber, custom_title_case


class HeadChurchCode(BaseModel):
    Code: str = Field(examples=["TEST"], max_length=4)

    @validator("Code")
    def upper_case_strings(cls, v):
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
    Contact_Email: EmailStr = Field(examples=["john.doe@example.com"], max_length=255)
    Contact_Email2: Optional[EmailStr] = Field(
        default=None, examples=["john.doe2@example.com"], max_length=255
    )
    Town_Code: str = Field(examples=["BEN"], max_length=4)
    State_Code: str = Field(examples=["EDO"], max_length=4)
    Region_Code: str = Field(examples=["SOUT"], max_length=4)
    Country_Code: str = Field(examples=["NIG"], max_length=4)

    @validator("Name", "Alt_Name", "Address")
    def title_case_strings(cls, v):
        return custom_title_case(v) if v else None

    @validator("About", "Mission", "Vision", "Motto")
    def capitalize_strings(cls, v):
        return v.capitalize() if v else None

    @validator("Contact_No", "Contact_No2")
    def get_phone_numbers(cls, v):
        return get_phonenumber(v) if v else None


class HeadChurchCreate(HeadChurchBase, HeadChurchCode):
    pass


class HeadChurch(HeadChurchBase, HeadChurchCode):
    Is_Active: Optional[bool] = True
    Created_Date: Optional[datetime] = None
    Created_By: Optional[str] = None
    Modified_Date: Optional[datetime] = None
    Modified_By: Optional[str] = None
    Id: Optional[int] = None


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
    Contact_Email: EmailStr = Field(
        default=None, examples=["john.doe@example.com"], max_length=255
    )
    Contact_Email2: Optional[EmailStr] = Field(
        default=None, examples=["john.doe2@example.com"], max_length=255
    )
    Town_Code: str = Field(default=None, examples=["BEN"], max_length=4)
    State_Code: str = Field(default=None, examples=["EDO"], max_length=4)
    Region_Code: str = Field(default=None, examples=["SOUT"], max_length=4)
    Country_Code: str = Field(default=None, examples=["NIG"], max_length=4)

    @validator("Name", "Alt_Name", "Address")
    def title_case_strings(cls, v):
        return custom_title_case(v) if v else None

    @validator("About", "Mission", "Vision", "Motto")
    def capitalize_strings(cls, v):
        return v.capitalize() if v else None

    @validator("Contact_No", "Contact_No2")
    def get_phone_numbers(cls, v):
        return get_phonenumber(v) if v else None


class HeadChurchCodeUpdate(BaseModel):
    Code: str = Field(default=None, examples=["TEST"], max_length=4)

    @validator("Code")
    def upper_case_strings(cls, v):
        return v.upper() if v else None


class HeadChurchUpdateIn(HeadChurchUpdate, HeadChurchCodeUpdate):
    pass
