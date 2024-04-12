from pydantic import BaseModel
from typing import Optional


class Member(BaseModel):
    First_Name: str
    Middle_Name: Optional[str]
    Last_Name: str
    Title: Optional[str]
    Title2: Optional[str]
    Family_Name: str
    Home_Address: str
    Date_of_Birth: str
    Gender: str
    Marital_Status: str
    Employ_Status: str
    Occupation: str
    Office_Address: Optional[str]
    State_of_Origin: str
    Personal_Contact_No: Optional[str]
    Contact_No: str
    Contact_No2: Optional[str]
    Personal_Email: Optional[str]
    Contact_Email: str
    Contact_Email2: Optional[str]
    Is_User: Optional[bool]
    # Passowrd: Optional[str]
    Town_Code: str
    State_Code: str
    Region_Code: str
    Country_Code: str
    Type: str
    Is_Clergy: Optional[bool]
    HeadChurch_Code: str
    Is_Active: Optional[bool]
