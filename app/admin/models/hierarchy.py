# from datetime import datetime, date, time

# from pydantic import BaseModel, Field  # type: ignore
# from pydantic_extra_types.phone_numbers import PhoneNumber  # type: ignore
# from typing import Optional, Union


# class Hierarchy(BaseModel):
#     Code: str = Field(examples=["TST"], max_length=3)
#     Hierarchy: str = Field(examples=["Test Church"], max_length=255)
#     Alt_Name: Optional[str] = Field(
#         default=None, examples=["Test Head Church"], max_length=255
#     )
#     Rank_No: int = Field(examples=[1])
#     Is_Active: Optional[bool] = True


# class HierarchyResponse(BaseModel):
#     status_code: int
#     message: str
#     data: Union[list[Hierarchy], Hierarchy, None] = None


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
