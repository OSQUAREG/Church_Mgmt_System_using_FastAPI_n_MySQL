from datetime import datetime
from typing import Optional, Union

from pydantic import BaseModel  # type: ignore

from .church import ChurchStatus


class ChurchLeadsBase(BaseModel):
    Church_Code: str
    Level_Code: str
    LeadChurch_Code: str
    LeadChurch_Level: str
    Is_Active: bool
    Start_Date: datetime
    End_Date: Optional[datetime] = None


class ChurchLeads(ChurchStatus, ChurchLeadsBase):
    HeadChurch_Code: str
    Created_Date: Optional[datetime] = None
    Created_By: Optional[str] = None
    Modified_Date: Optional[datetime] = None
    Modified_By: Optional[str] = None


class ChurchLeadsResponse(BaseModel):
    status_code: int
    message: str
    data: Union[list[ChurchLeads], ChurchLeads, None] = None
