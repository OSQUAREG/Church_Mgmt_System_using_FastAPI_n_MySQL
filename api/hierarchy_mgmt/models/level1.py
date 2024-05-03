from typing import Optional, Union

from pydantic import BaseModel  # type: ignore

from .head_church import HeadChurchBase, HeadChurchUpdate, CodeModel, ApproveModel


class Level1Base(HeadChurchBase):
    HeadChurch_Code: str


class Level1(ApproveModel, Level1Base, CodeModel):
    pass


class Level1Response(BaseModel):
    status_code: int
    message: str
    data: Union[list[Level1], Level1, None] = None


class Level1Update(HeadChurchUpdate):
    HeadChurch_Code: Optional[str] = None
