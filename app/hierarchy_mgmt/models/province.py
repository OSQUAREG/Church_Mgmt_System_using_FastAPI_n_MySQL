from typing import Optional, Union

from pydantic import BaseModel  # type: ignore

from .head_church import HeadChurchBase, HeadChurchUpdate, CodeModel, ApproveModel


class ProvinceBase(HeadChurchBase):
    HeadChurch_Code: str


class Province(ApproveModel, ProvinceBase, CodeModel):
    pass


class ProvinceResponse(BaseModel):
    status_code: int
    message: str
    data: Union[list[Province], Province, None] = None


class ProvinceUpdate(HeadChurchUpdate):
    HeadChurch_Code: Optional[str] = None
