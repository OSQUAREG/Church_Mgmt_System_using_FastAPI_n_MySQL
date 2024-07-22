from datetime import datetime
from typing import Optional, Union

from pydantic import BaseModel  # type: ignore
from .churches import ChurchStatus


class ChurchLeadsBase(BaseModel):
    Id: int
    Church_Code: str
    Church_Name: str
    Level_Code: str
    LeadChurch_Code: str
    LeadChurch_Name: str
    LeadChurch_Level: str
    Start_Date: datetime
    End_Date: Optional[datetime] = None
    Is_Active: bool
    HeadChurch_Code: str
    Created_Date: Optional[datetime] = None
    Created_By: Optional[str] = None
    Modified_Date: Optional[datetime] = None
    Modified_By: Optional[str] = None


class ChurchLeads(ChurchStatus, ChurchLeadsBase):
    pass


class ChurchLeadsResponse(BaseModel):
    status_code: int
    message: str
    data: Union[list[ChurchLeads], ChurchLeads, None] = None


class ChurchLeadHierarchy(BaseModel):
    Church_Code: str
    Church_Name: str
    Church_Level: str
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


class ChurchLeadHierarchyResponse(BaseModel):
    status_code: int
    message: str
    data: Union[list[ChurchLeadHierarchy], ChurchLeadHierarchy, None] = None
