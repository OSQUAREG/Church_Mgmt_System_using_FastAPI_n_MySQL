from datetime import date, datetime
from typing import List, Optional, Union

from pydantic import BaseModel, Field, validator, EmailStr  # type: ignore
from ...common.utils import custom_title_case, get_phonenumber


class MemberCode(BaseModel):
    Code: Optional[str] = Field(default=None)


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
    Date_of_Birth: date = Field(examples=["2000-12-31"])
    Gender: str = Field(examples=["M"], max_length=1)
    Marital_Status: str = Field(examples=["SIG"], max_length=4)
    Employ_Status: str = Field(examples=["EMPD"], max_length=4)
    Occupation: Optional[str] = Field(default=None, examples=["Doctor"], max_length=100)
    Office_Address: Optional[str] = Field(
        default=None, examples=["This is the address of the Office"], max_length=500
    )
    State_of_Origin: str = Field(examples=["EDO"], max_length=4)
    Country_of_Origin: str = Field(examples=["NIG"], max_length=4)
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
    Town_Code: str = Field(examples=["BEN"], max_length=4)
    State_Code: str = Field(examples=["EDO"], max_length=4)
    Region_Code: str = Field(examples=["SOUT"], max_length=4)
    Country_Code: str = Field(examples=["NIG"], max_length=4)
    Type: str = Field(examples=["MBR"], max_length=3)
    Is_Clergy: Optional[bool] = Field(default=False)

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


class MemberBranchJoinIn(BaseModel):
    Branch_Code: str
    Join_Date: datetime
    Join_Code: str
    Join_Note: Optional[str] = None


class MemberBranchExitIn(BaseModel):
    Branch_Code: str
    Exit_Date: datetime
    Exit_Code: str
    Exit_Note: Optional[str] = None


class MemberIn(MemberBranchJoinIn, MemberBase):
    pass


class Member(MemberBase, MemberCode):
    Branch_Code: Optional[str] = None
    Join_Date: Optional[datetime] = None
    Join_Code: Optional[str] = None
    Join_Note: Optional[str] = None
    Exit_Date: Optional[datetime] = None
    Exit_Code: Optional[str] = None
    Exit_Note: Optional[str] = None
    Is_User: Optional[bool] = False
    Clergy_Code: Optional[str] = None
    Is_Active: Optional[bool] = True
    HeadChurch_Code: Optional[str] = Field(examples=["TEST"], max_length=4)
    Created_Date: Optional[datetime] = None
    Created_By: Optional[str] = None
    Modified_Date: Optional[datetime] = None
    Modified_By: Optional[str] = None
    Id: Optional[int] = None


class MemberResponse(BaseModel):
    status_code: int
    message: str
    data: Union[list[Member], Member, None] = None


class MemberBranchOut(BaseModel):
    Id: int
    Member_Code: str
    Title: str
    Title2: str
    First_Name: str
    Middle_Name: str
    Last_Name: str
    Branch_Code: str
    Branch_Name: str
    Join_Date: datetime
    Join_Code: str
    Join_Note: Optional[str] = None
    Exit_Date: Optional[datetime] = None
    Exit_Code: Optional[str] = None
    Exit_Note: Optional[str] = None
    HeadChurch_Code: Optional[str] = None
    Is_Active: Optional[bool] = Field(default=True)
    Created_Date: Optional[datetime] = None
    Created_By: Optional[str] = None
    Modified_Date: Optional[datetime] = None
    Modified_By: Optional[str] = None


class MemberBranchResponse(BaseModel):
    status_code: int
    message: str
    data: Union[list[MemberBranchOut], MemberBranchOut, None] = None


class MemberUpdate(BaseModel):
    First_Name: Optional[str] = Field(default=None, examples=["John"], max_length=255)
    Middle_Name: Optional[str] = Field(default=None, examples=["Janet"], max_length=255)
    Last_Name: Optional[str] = Field(default=None, examples=["Doe"], max_length=255)
    Title: Optional[str] = Field(default=None, examples=["Dr"], max_length=100)
    Title2: Optional[str] = Field(default=None, examples=["Mrs"], max_length=100)
    Family_Name: Optional[str] = Field(default=None, examples=["Doe"], max_length=255)
    Is_FamilyHead: Optional[bool] = Field(default=False)
    Home_Address: Optional[str] = Field(
        default=None, examples=["This is the address of the Member"], max_length=500
    )
    Date_of_Birth: Optional[date] = Field(default=None, examples=["2000-12-31"])
    Gender: Optional[str] = Field(default=None, examples=["M"], max_length=1)
    Marital_Status: Optional[str] = Field(default=None, examples=["MRD"], max_length=3)
    Employ_Status: Optional[str] = Field(default=None, examples=["EMPD"], max_length=4)
    Occupation: Optional[str] = Field(
        default=None, examples=["Professor"], max_length=100
    )
    Office_Address: Optional[str] = Field(
        default=None, examples=["This is the address of the Office"], max_length=500
    )
    State_of_Origin: Optional[str] = Field(default=None, examples=["EDO"], max_length=4)
    Country_of_Origin: Optional[str] = Field(
        default=None, examples=["NIG"], max_length=4
    )
    Personal_Contact_No: Optional[str] = Field(
        default=None, examples=["+2348012345678"], max_length=25
    )
    Contact_No: Optional[str] = Field(
        default=None, examples=["+2348012345678"], max_length=25
    )
    Contact_No2: Optional[str] = Field(
        default=None, examples=["+2348012345678"], max_length=25
    )
    Personal_Email: Optional[EmailStr] = Field(
        default=None, examples=["john.doe@example.com"], max_length=255
    )
    Contact_Email: Optional[EmailStr] = Field(
        default=None, examples=["john.doe@example.com"], max_length=255
    )
    Contact_Email2: Optional[EmailStr] = Field(
        default=None, examples=["john.doe@example.com"], max_length=255
    )
    Town_Code: Optional[str] = Field(default=None, examples=["BEN"], max_length=4)
    State_Code: Optional[str] = Field(default=None, examples=["EDO"], max_length=4)
    Region_Code: Optional[str] = Field(default=None, examples=["SOUT"], max_length=4)
    Country_Code: Optional[str] = Field(default=None, examples=["NIG"], max_length=4)
    Type: Optional[str] = Field(default=None, examples=["MBR"], max_length=3)
    Is_Clergy: Optional[bool] = Field(default=False)

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


class MemberChurchHierarchy(BaseModel):
    Member_Code: str
    LeadCode_1: str
    LeadName_1: str
    LeadLevel_1: str
    LeadCode_2: Optional[str] = None
    LeadName_2: Optional[str] = None
    LeadLevel_2: Optional[str] = None
    LeadCode_3: Optional[str] = None
    LeadName_3: Optional[str] = None
    LeadLevel_3: Optional[str] = None
    LeadCode_4: Optional[str] = None
    LeadName_4: Optional[str] = None
    LeadLevel_4: Optional[str] = None
    LeadCode_5: Optional[str] = None
    LeadName_5: Optional[str] = None
    LeadLevel_5: Optional[str] = None
    LeadCode_6: Optional[str] = None
    LeadName_6: Optional[str] = None
    LeadLevel_6: Optional[str] = None
    LeadCode_7: Optional[str] = None
    LeadName_7: Optional[str] = None
    LeadLevel_7: Optional[str] = None
    LeadCode_8: Optional[str] = None
    LeadName_8: Optional[str] = None
    LeadLevel_8: Optional[str] = None
    LeadCode_9: Optional[str] = None
    LeadName_9: Optional[str] = None
    LeadLevel_9: Optional[str] = None
    LeadCode_10: Optional[str] = None
    LeadName_10: Optional[str] = None
    LeadLevel_10: Optional[str] = None


class MemberChurchHierarchyResponse(BaseModel):
    status_code: int
    message: str
    data: Union[List[MemberChurchHierarchy], MemberChurchHierarchy, None] = None


class MemberBranchUpdate(BaseModel):
    Join_Date: Optional[datetime] = None
    Join_Code: Optional[str] = None
    Join_Note: Optional[str] = None
    Exit_Date: Optional[datetime] = None
    Exit_Code: Optional[str] = None
    Exit_Note: Optional[str] = None
    # Is_Active: Optional[bool] = True
