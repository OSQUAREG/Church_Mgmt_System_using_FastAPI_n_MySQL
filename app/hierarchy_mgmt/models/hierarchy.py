from pydantic import BaseModel, Field  # type: ignore
from pydantic_extra_types.phone_numbers import PhoneNumber  # type: ignore
from typing import Optional, Union


class Hierarchy(BaseModel):
    Level_Code: Optional[str] = None
    Hierarchy: Optional[str] = None
    Alt_Name: Optional[str] = None
    Rank_No: Optional[int] = None
    Is_Active: Optional[bool] = True
    Head_Code: Optional[str] = None

    # class Config:
    #     schema_extra = {"hidden": True}


class HierarchyResponse(BaseModel):
    status_code: int
    message: str
    data: Union[list[Hierarchy], Hierarchy, None] = None


# class HierarchyUpdate(BaseModel):
#     Code: Optional[str] = Field(default=None, examples=["TST"], max_length=3)
#     Hierarchy: Optional[str] = Field(
#         default=None, examples=["Test Church1"], max_length=255
#     )
#     Alt_Name: Optional[str] = Field(
#         default=None, examples=["Test Head Church1"], max_length=255
#     )
#     Rank_No: Optional[int] = Field(default=None, examples=[1])
#     Is_Active: Optional[bool] = None
