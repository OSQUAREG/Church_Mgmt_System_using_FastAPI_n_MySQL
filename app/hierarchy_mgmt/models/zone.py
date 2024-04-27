from datetime import datetime, date, time
from typing import Optional, Union

from pydantic import BaseModel  # type: ignore
from pydantic_extra_types.phone_numbers import PhoneNumber  # type: ignore

from .head_church import HeadChurchBase, HeadChurchUpdate, CodeModel, ApproveModel
from ...common.utils import get_phonenumber


class ZoneBase(HeadChurchBase):
    Province_Code: str
    HeadChurch_Code: str


class Zone(ApproveModel, ZoneBase, CodeModel):
    pass


class ZoneResponse(BaseModel):
    status_code: int
    message: str
    data: Union[list[Zone], Zone, None] = None


class ZoneUpdate(HeadChurchUpdate):
    Province_Code: Optional[str] = None
    HeadChurch_Code: Optional[str] = None
