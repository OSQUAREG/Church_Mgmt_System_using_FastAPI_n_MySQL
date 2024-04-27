# from typing import Annotated

# from fastapi import APIRouter, status, Depends  # type: ignore
# from sqlalchemy import text  # type: ignore
# from sqlalchemy.orm import Session  # type: ignore

# from ...common.database import get_db
# from ...common.dependencies import get_current_user
# from ...authentication.models.auth import User
# from ...admin.services.hierarchy import HierarchyService
# from ...admin.models.hierarchy import (
#     Hierarchy,
#     HierarchyUpdate,
#     HierarchyResponse,
# )

# adm_hie_router = APIRouter(
#     prefix="/admin/hierarchy", tags=["Hierarchy Operations - Admin only"]
# )

# """
# Hierarchy Admin Routes
# - Create New Hierarchy
# - Get All Hierarchies
# - Get Hierarchy by Code
# - Update Hierarchy by Code
# - Activate Hierarchy by Code
# - Deactivate Hierarchy by Code
# - Delete Hierarchy by Code
# """


# # Create New Hierarchy
# @adm_hie_router.post(
#     "/create",
#     status_code=status.HTTP_201_CREATED,
#     name="Create New Hierarchy",
#     response_model=HierarchyResponse,
# )
# async def create_new_hierarchy(
#     hierarchy: Hierarchy,
#     db: Annotated[Session, Depends(get_db)],
#     current_user: Annotated[User, Depends(get_current_user)],
# ):
#     new_hierarchy = HierarchyService().create_new_hierarchy(hierarchy, db, current_user)
#     # set response body
#     response = dict(
#         data=new_hierarchy,
#         status_code=status.HTTP_201_CREATED,
#         message=f"Successsfully created new Hierarchy: {new_hierarchy.Hierarchy} with code: {new_hierarchy.Code}",
#     )
#     return response


# # Get All Hierarchies
# @adm_hie_router.get(
#     "/",
#     status_code=status.HTTP_200_OK,
#     name="Get All Hierarchies",
#     response_model=HierarchyResponse,
# )
# async def get_all_hierarchy(
#     db: Annotated[Session, Depends(get_db)],
#     current_user: Annotated[User, Depends(get_current_user)],
# ):
#     hierarchies = HierarchyService().get_all_hierarchies(db)
#     # set response body
#     response = dict(
#         data=hierarchies,
#         status_code=status.HTTP_200_OK,
#         message=f"Successsfully retrieved all {len(hierarchies)} Hierarchies",
#     )
#     return response


# # Get Hierarchy by Code
# @adm_hie_router.get(
#     "/{code}",
#     status_code=status.HTTP_200_OK,
#     name="Get Hierarchy by Code",
#     response_model=HierarchyResponse,
# )
# async def get_hierarchy_by_code(
#     code: str,
#     db: Annotated[Session, Depends(get_db)],
#     current_user: Annotated[User, Depends(get_current_user)],
# ):
#     hierarchy = HierarchyService().get_hierarchy_by_code(code, db)
#     # set response body
#     response = dict(
#         data=hierarchy,
#         status_code=status.HTTP_200_OK,
#         message=f"Successsfully retrieved Hierarchy: {hierarchy.Hierarchy}, with code: {hierarchy.Code.upper()}",
#     )
#     return response


# # Update Hierarchy by Code
# @adm_hie_router.put(
#     "/{code}/update",
#     status_code=status.HTTP_200_OK,
#     name="Update Hierarchy by Code",
#     response_model=HierarchyResponse,
# )
# async def update_hierarchy_by_code(
#     code: str,
#     hierarchy: HierarchyUpdate,
#     db: Annotated[Session, Depends(get_db)],
#     current_user: Annotated[User, Depends(get_current_user)],
# ):
#     updated_hierarchy = HierarchyService().update_hierarchy_by_code(
#         code, hierarchy, db, current_user
#     )
#     # set response body
#     response = dict(
#         data=updated_hierarchy,
#         status_code=status.HTTP_200_OK,
#         message=f"Successsfully updated Hierarchy: {updated_hierarchy.Hierarchy}, with code: {updated_hierarchy.Code.upper()}",
#     )
#     return response


# # Activate Hierarchy by Code
# @adm_hie_router.patch(
#     "/{code}/activate",
#     status_code=status.HTTP_200_OK,
#     name="Activate Hierarchy by Code",
#     response_model=HierarchyResponse,
# )
# async def activate_hierarchy_by_code(
#     code: str,
#     db: Annotated[Session, Depends(get_db)],
#     current_user: Annotated[User, Depends(get_current_user)],
# ):
#     activated_hierarchy = HierarchyService().activate_hierarchy_by_code(
#         code, db, current_user
#     )
#     # set response body
#     response = dict(
#         data=activated_hierarchy,
#         status_code=status.HTTP_200_OK,
#         message=f"Successsfully activated Hierarchy: {activated_hierarchy.Hierarchy}, with code: {activated_hierarchy.Code.upper()}",
#     )
#     return response


# # Deactivate Hierarchy by Code
# @adm_hie_router.patch(
#     "/{code}/deactivate",
#     status_code=status.HTTP_200_OK,
#     name="Deactivate Hierarchy by Code",
#     response_model=HierarchyResponse,
# )
# async def deactivate_hierarchy_by_code(
#     code: str,
#     db: Annotated[Session, Depends(get_db)],
#     current_user: Annotated[User, Depends(get_current_user)],
# ):
#     deactivated_hierarchy = HierarchyService().deactivate_hierarchy_by_code(
#         code, db, current_user
#     )
#     # set response body
#     response = dict(
#         data=deactivated_hierarchy,
#         status_code=status.HTTP_200_OK,
#         message=f"Successsfully deactivated Hierarchy: {deactivated_hierarchy.Hierarchy}, with code: {deactivated_hierarchy.Code.upper()}",
#     )
#     return response


# # Delete Hierarchy by Code
# @adm_hie_router.delete(
#     "/{code}/delete",
#     status_code=status.HTTP_204_NO_CONTENT,
#     name="Delete Hierarchy by Code",
# )
# async def delete_hierarchy_by_code(
#     code: str,
#     db: Annotated[Session, Depends(get_db)],
#     current_user: Annotated[User, Depends(get_current_user)],
# ):
#     HierarchyService().delete_hierarchy_by_code(code, db)
#     return
