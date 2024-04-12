from pydantic import BaseModel
from typing import Optional


class Country(BaseModel):
    Code: str
    Country: str
    Is_Active: Optional[bool] = True


class Region(BaseModel):
    Code: str
    Region: str
    Country_Code: str
    Is_Active: Optional[bool] = True


class State(BaseModel):
    Code: str
    State: str
    Region_Code: str
    Country_Code: str
    Is_Active: Optional[bool] = True


class Town(BaseModel):
    Code: str
    Town: str
    State_Code: str
    Region_Code: str
    Country_Code: str
    Is_Active: Optional[bool] = True
