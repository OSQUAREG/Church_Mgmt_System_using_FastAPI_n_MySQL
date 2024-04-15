from typing import Annotated

from fastapi import APIRouter, HTTPException, status, Depends

from ..models.hierarchy import Hierarchy, HierarchyResponse
from ...authentication.models.auth import User
from ...common.dependencies import get_current_active_user, get_db

adm_hie_router = APIRouter(
    prefix="/admin/hierarchy", tags=["Hierarchy Operations - Admin only"]
)


# Create New Hierarchy
@adm_hie_router.post(
    "/create",
    status_code=status.HTTP_201_CREATED,
    name="Create New Hierarchy",
    response_model=HierarchyResponse,
    response_description="Successsfully created new Hierarchy",
)
async def create_hierarchy(
    hierarchy: Hierarchy, conn: Annotated[dict, Depends(get_db)]
):
    # get cursor and mydb from the get_db depemdency
    cursor = conn["cursor"]
    mydb = conn["mydb"]
    # insert new data into db
    cursor.execute(
        """
        INSERT INTO dfHierarchy 
        (Code, Hierarchy, Alt_Name, Rank_No, Is_Active, Created_By, Modified_By)
        VALUES (%s, %s, %s, %s, %s, %s, %s);
        """,
        (
            hierarchy.Code,
            hierarchy.Hierarchy,
            hierarchy.Alt_Name,
            hierarchy.Rank_No,
            hierarchy.Is_Active,
            "tester",
            "tester",
        ),
    )
    # commit changes to db
    mydb.commit()
    # fetch the last inserted data from db
    cursor.execute("SELECT * FROM dfHierarchy WHERE Id = LAST_INSERT_ID();")
    new_data = cursor.fetchone()
    # set response body
    response = dict(
        data=new_data,
        status_code=status.HTTP_201_CREATED,
        message="Successsfully created new Hierarchy",
    )
    return new_data


# Get All Hierarchies
@adm_hie_router.get(
    "/",
    status_code=status.HTTP_200_OK,
    name="Get All Hierarchies",
    response_model=HierarchyResponse,
    response_description="Successsfully retrieved all Hierarchies",
)
async def get_hierarchy(
    conn: Annotated[dict, Depends(get_db)],
    # current_user: Annotated[User, Depends(get_current_active_user)],
):
    # get cursor from the get_db depemdency
    cursor = conn["cursor"]
    # fetch data from db
    cursor.execute("SELECT * FROM dfHierarchy ORDER BY Id ASC;")
    data = cursor.fetchall()
    # set response body
    response = dict(
        data=data,
        status_code=status.HTTP_200_OK,
        message=f"Successsfully retrieved a total of {len(data)} Hierarchies",
    )
    return response


# Get Hierarchy by Code
@adm_hie_router.get(
    "/{code}",
    status_code=status.HTTP_200_OK,
    name="Get Hierarchy by Code",
    response_model=HierarchyResponse,
    response_description="Successsfully retrieved Hierarchy by Code",
)
async def get_hierarchy_by_code(code: str, conn: Annotated[dict, Depends(get_db)]):
    # get cursor from the get_db depemdency
    cursor = conn["cursor"]
    # fetch data from db
    cursor.execute("SELECT * FROM dfHierarchy WHERE Code = %s;", (code,))
    data = cursor.fetchone()
    # checks if data exists
    if data is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Hierarchy with code: {code} not found",
        )
    # set response body
    response = dict(
        data=data,
        status_code=status.HTTP_200_OK,
        message=f"Successsfully retrieved Hierarchy: {data['Hierarchy']}, with code: {code.upper()}",
    )
    return response


# Update Hierarchy by Code
@adm_hie_router.patch(
    "/update/{code}",
    status_code=status.HTTP_200_OK,
    name="Update Hierarchy by Code",
    response_model=Hierarchy,
    response_description="Successsfully updated Hierarchy by Code",
)
async def update_hierarchy_by_code(
    code: str, hierarchy: Hierarchy, conn: Annotated[dict, Depends(get_db)]
):
    # get cursor and mydb from the get_db depemdency
    cursor = conn["cursor"]
    mydb = conn["mydb"]
    # fetch data from db to check if it exists
    cursor.execute("SELECT * FROM dfHierarchy WHERE Code = %s;", (code,))
    data = cursor.fetchone()
    if data is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Hierarchy with code: {code} not found",
        )
    # update the data
    cursor.execute(
        """
        UPDATE dfHierarchy
        SET Hierarchy = %s, Alt_Name = %s, Rank_No = %s, Is_Active = %s, Modified_By = %s
        WHERE Code = %s;
        """,
        (
            hierarchy.Hierarchy,
            hierarchy.Alt_Name,
            hierarchy.Rank_No,
            hierarchy.Is_Active,
            "tester1",
            code,
        ),
    )
    # commit changes to db
    mydb.commit()
    # fetch the updated data
    cursor.execute("SELECT * FROM dfHierarchy WHERE Code = %s;", (code,))
    updated_data = cursor.fetchone()
    # set response body
    response = dict(
        data=updated_data,
        status_code=status.HTTP_200_OK,
        message=f"Successsfully updated Hierarchy: {updated_data['Hierarchy']}, with code: {code.upper()}",
    )
    return response


# Delete Hierarchy by Code
@adm_hie_router.delete(
    "/delete/{code}",
    status_code=status.HTTP_204_NO_CONTENT,
    name="Delete Hierarchy by Code",
    response_description="Successsfully deleted Hierarchy by Code",
)
async def delete_hierarchy_by_code(code: str, conn: Annotated[dict, Depends(get_db)]):
    # get cursor and mydb from the get_db depemdency
    cursor = conn["cursor"]
    mydb = conn["mydb"]
    # fetch data from db to check if it exists
    cursor.execute("SELECT * FROM dfHierarchy WHERE Code = %s;", (code,))
    data = cursor.fetchone()
    if data is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Hierarchy with code: {code} not found",
        )
    # delete the data
    cursor.execute("DELETE FROM dfHierarchy WHERE Code = %s;", (code,))
    # commit changes to db
    mydb.commit()
    return
