from typing import Optional, Union

from pydantic import BaseModel, validator  # type: ignore

from .head_church import HeadChurchBase, HeadChurchUpdate, ChurchCode, ChurchStatus


class ChurchBase(HeadChurchBase):
    Level_Code: str
    HeadChurch_Code: str

    @validator("Level_Code")
    def capitalize_strings(cls, v):
        return v.capitalize() if v else None


class Church(ChurchStatus, ChurchBase, ChurchCode):
    pass


class ChurchResponse(BaseModel):
    status_code: int
    message: str
    data: Union[list[Church], Church, None] = None


class ChurchUpdate(HeadChurchUpdate):
    Level_Code: Optional[str] = None
    HeadChurch_Code: Optional[str] = None

    @validator("Level_Code")
    def capitalize_strings(cls, v):
        return v.capitalize() if v else None
