from fastapi import APIRouter, HTTPException, status, Response
from ..config.config import conn, get_mysql_cursor, close_mysql_cursor
from ..models.hierarchy import Hierarchy, HeadChurch

router = APIRouter(prefix="/church", tags=["Church Operations"])
chu_router = APIRouter(prefix="/head_church", tags=["Head Church Operations"])


# Create New Head Church
@chu_router.post(
    "/create",
    status_code=status.HTTP_201_CREATED,
    name="Create New Head Church",
    response_model=HeadChurch,
    response_description="Successsfully created new Head Church",
)
async def create_new_head_church(head_church: HeadChurch):
    try:
        mydb, cursor = get_mysql_cursor()
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
    except conn.Error as err:
        raise HTTPException(status_code=500, detail=f"MySQL Error: {err}")
    finally:
        close_mysql_cursor(mydb, cursor)


# Get All Head Churches
@chu_router.get(
    "/",
    status_code=status.HTTP_200_OK,
    name="Get All Head Churches",
    response_model=list[HeadChurch],
    response_description="Successsfully retrieved all Head Churches",
)
async def get_head_church():
    try:
        mydb, cursor = get_mysql_cursor()
        cursor.execute("SELECT * FROM tblHeadChurch;")
        data = cursor.fetchall()
        return data
    except conn.Error as err:
        raise HTTPException(status_code=500, detail=f"MySQL Error: {err}")
    finally:
        close_mysql_cursor(mydb, cursor)


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
@chu_router.put(
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
