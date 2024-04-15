from fastapi import APIRouter, HTTPException, status, Response

from ...common.config import conn, get_mysql_cursor, close_mysql_cursor
from ..models.church import HeadChurch

# router = APIRouter(prefix="/church", tags=["Church Operations"])
chu_router = APIRouter(prefix="/head_church", tags=["Head Church Operations"])


# Get Head Church by Code
@chu_router.get(
    "/{code}",
    status_code=status.HTTP_200_OK,
    name="Get Head Church by Code",
    response_model=HeadChurch,
    response_description="Successsfully retrieved Head Church with code: {code}",
)
async def get_head_church_by_code(code: str):
    try:
        mydb, cursor = get_mysql_cursor()
        cursor.execute("SELECT * FROM tblHeadChurch WHERE Code = %s;", (code,))
        data = cursor.fetchone()
        if data is None:
            raise HTTPException(
                status_code=404, detail=f"Head Church with code: {code} not found"
            )
        return data
    except conn.Error as err:
        raise HTTPException(status_code=500, detail=f"MySQL Error: {err}")
    finally:
        close_mysql_cursor(mydb, cursor)


# Update Head Church by Code
@chu_router.patch(
    "/{code}",
    status_code=status.HTTP_200_OK,
    name="Update Head Church by Code",
    response_model=HeadChurch,
    response_description="Successsfully updated Head Church with code: {code}",
)
async def update_head_church_by_code(code: str, head_church: HeadChurch):
    try:
        mydb, cursor = get_mysql_cursor()
        cursor.execute(
            """
            UPDATE tblHeadChurch
            SET
                Name = %s,
                Alt_Name = %s,
                Address = %s,
                Founding_Date = %s,
                About = %s,
                Mission = %s,
                Vision = %s,
                Motto = %s,
                Contact_No = %s,
                Contact_No2 = %s,
                Contact_Email = %s,
                Contact_Email2 = %s,
                Town_Code = %s,
                State_Code = %s,
                Region_Code = %s,
                Country_Code = %s,
                Is_Active = %s
                Modified_By = %s
            WHERE Code = %s;
            """,
            (
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
                code,
            ),
        )
        mydb.commit()
        # fetch the last updated data
        cursor.execute("SELECT * FROM tblHeadChurch WHERE Code = %s;", (code,))
        updated_data = cursor.fetchone()
        return updated_data
    except conn.Error as err:
        raise HTTPException(status_code=500, detail=f"MySQL Error: {err}")
    finally:
        close_mysql_cursor(mydb, cursor)
