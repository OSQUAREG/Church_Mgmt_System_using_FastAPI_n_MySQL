from typing import Annotated

from fastapi import APIRouter, HTTPException, status, Response, Depends

from ...common.config import conn, get_mysql_cursor, close_mysql_cursor
from ...hierarchy_mgmt.models.church import HeadChurch, HeadChurchResponse
from ...common.dependencies import get_db

# router = APIRouter(prefix="/church", tags=["Church Operations"])
adm_chu_router = APIRouter(
    prefix="/admin/head_church",
    tags=["Head Church Operations - Admin only"],
)


# Create New Head Church
@adm_chu_router.post(
    "/create",
    status_code=status.HTTP_201_CREATED,
    name="Create New Head Church",
    response_model=HeadChurch,
    response_description="Successsfully created new Head Church",
)
async def create_new_head_church(
    head_church: HeadChurch, conn: Annotated[dict, Depends(get_db)]
):
    mydb, cursor = conn["mydb"], conn["cursor"]
    cursor.execute(
        """
        INSERT INTO tblHeadChurch
        (Code, Name, Alt_Name, Address, Founding_Date, About, Mission, Vision, Motto, Contact_No, Contact_No2, Contact_Email, Contact_Email2, Town_Code, State_Code, Region_Code, Country_Code, Is_Active, Created_By, Modified_By)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """,
        (
            head_church.Code,
            head_church.Name,
            head_church.Alt_Name,
            head_church.Address,
            head_church.Founding_Date,
            head_church.About,
            head_church.Mission,
            head_church.Vision,
            head_church.Motto,
            head_church.Contact_No,
            head_church.Contact_No2,
            head_church.Contact_Email,
            head_church.Contact_Email2,
            head_church.Town_Code,
            head_church.State_Code,
            head_church.Region_Code,
            head_church.Country_Code,
            head_church.Is_Active,
            "root",
            "root",
        ),
    )
    mydb.commit()
    # fetch the last inserted data
    cursor.execute("SELECT * FROM tblHeadChurch WHERE Id = LAST_INSERT_ID();")
    new_data = cursor.fetchone()
    return new_data


# Get All Head Churches
@adm_chu_router.get(
    "/",
    status_code=status.HTTP_200_OK,
    name="Get All Head Churches",
    response_model=HeadChurchResponse,
    response_description="Successsfully retrieved all Head Churches",
)
async def get_head_church(conn: Annotated[dict, Depends(get_db)]):
    # get cursor from the get_db depemdency
    cursor = conn["cursor"]
    # fetch data from db
    cursor.execute("SELECT * FROM tblHeadChurch ORDER BY Id ASC;")
    data = cursor.fetchall()
    # set response body
    response = dict(
        data=data,
        status_code=status.HTTP_200_OK,
        message=f"Successsfully retrieved a total of {len(data)} Head Churches",
    )
    return response
