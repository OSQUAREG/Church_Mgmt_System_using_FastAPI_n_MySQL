from datetime import datetime
from typing import Optional, Union

from pydantic import BaseModel  # type: ignore
from .church import ChurchStatus


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
