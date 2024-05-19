from datetime import datetime
from ...common.utils import custom_title_case, get_phonenumber
from pydantic import BaseModel, Field, validator, EmailStr  # type: ignore
from typing import Optional, Union


class MemberBase(BaseModel):
    First_Name: str = Field(examples=["John"], max_length=255)
    Middle_Name: Optional[str] = Field(default=None, examples=["Janet"], max_length=255)
    Last_Name: str = Field(examples=["Doe"], max_length=255)
    Title: Optional[str] = Field(default=None, examples=["Dr"], max_length=100)
    Title2: Optional[str] = Field(default=None, examples=["Mrs"], max_length=100)
    Family_Name: str = Field(examples=["Doe"], max_length=255)
    Is_FamilyHead: Optional[bool] = Field(default=False)
    Home_Address: str = Field(
        examples=["This is the address of the Member"], max_length=500
    )
    Date_of_Birth: str = Field(examples=["2000-12-31"])
    Gender: str = Field(examples=["Male"], max_length=1)
    Marital_Status: str = Field(examples=["Single"], max_length=3)
    Employ_Status: str = Field(examples=["EMPD"], max_length=3)
    Occupation: Optional[str] = Field(default=None, examples=["Doctor"], max_length=100)
    Office_Address: Optional[str] = Field(
        default=None, examples=["This is the address of the Office"], max_length=500
    )
    State_of_Origin: str = Field(examples=["Lagos"], max_length=3)
    Personal_Contact_No: Optional[str] = Field(
        default=None, examples=["+2348012345678"], max_length=25
    )
    Contact_No: str = Field(examples=["+2348012345678"], max_length=25)
    Contact_No2: Optional[str] = Field(
        default=None, examples=["+2348012345678"], max_length=25
    )
    Personal_Email: Optional[EmailStr] = Field(
        default=None, examples=["john.doe@example.com"], max_length=255
    )
    Contact_Email: EmailStr = Field(examples=["john.doe@example.com"], max_length=255)
    Contact_Email2: Optional[EmailStr] = Field(
        default=None, examples=["john.doe@example.com"], max_length=255
    )
    Is_User: Optional[bool] = Field(default=False)
    Town_Code: str = Field(max_length=4)
    State_Code: str = Field(max_length=4)
    Region_Code: str = Field(max_length=4)
    Country_Code: str = Field(max_length=4)
    Type: str = Field(examples=["MBR"], max_length=3)
    Is_Clergy: Optional[bool] = Field(default=False)
    HeadChurch_Code: str = Field(examples=["TEST"], max_length=4)
    Is_Active: Optional[bool] = Field(default=True)
    Created_Date: Optional[datetime] = None
    Created_By: Optional[str] = None
    Modified_Date: Optional[datetime] = None
    Modified_By: Optional[str] = None

    @validator(
        "First_Name",
        "Middle_Name",
        "Last_Name",
        "Home_Address",
        "Office_Address",
        "Title",
        "Title2",
        "Family_Name",
        "Occupation",
    )
    def title_case_strings(cls, v):
        return custom_title_case(v) if v else None

    @validator("Personal_Contact_No", "Contact_No", "Contact_No2")
    def get_phone_numbers(cls, v):
        return get_phonenumber(v) if v else None


class MemberChurch(BaseModel):
    Church_Code: str
    Join_Date: datetime
    Join_Type: str
    Join_Note: Optional[str] = None
    Exit_Date: Optional[datetime] = None
    Exit_Type: Optional[str] = None
    Exit_Note: Optional[str] = None
    Is_Active_M: Optional[bool] = Field(default=True)
    HeadChurch_Code: Optional[str] = Field(examples=["TEST"], max_length=4)


class Member(MemberChurch, MemberBase):
    pass


class MemberResponse(BaseModel):
    status_code: int
    message: str
    data: Union[list[Member], Member, None] = None
