# from fastapi import HTTPException, status  # type: ignore
# from sqlalchemy import text  # type: ignore
# from sqlalchemy.orm import Session  # type: ignore

# from ...authentication.models.auth import User
# from ...admin.models.hierarchy import Hierarchy, HierarchyUpdate
# from ...hierarchy_mgmt.services.hierarchy import HierarchyService


# hierarchy_service = HierarchyService()


# class HierarchyAdminService:
#     """
#     Hierarchy Admin Services
#     - Create New Hierarchy
#     - Update Hierarchy by Code
#     - Activate Hierarchy by Code
#     - Deactivate Hierarchy by Code
#     - Delete Hierarchy by Code
#     """

#     def create_new_hierarchy(
#         self, hierarchy: Hierarchy, db: Session, current_user: User
#     ):
#         try:
#             # insert new data into db
#             db.execute(
#                 text(
#                     """
#                     INSERT INTO dfHierarchy 
#                     (Code, Hierarchy, Alt_Name, Rank_No, Is_Active, Created_By, Modified_By)
#                     VALUES (:Code, :Hierarchy, :Alt_Name, :Rank_No, :Is_Active, :Created_By, :Modified_By);
#                     """
#                 ),
#                 dict(
#                     Code=hierarchy.Code,
#                     Hierarchy=hierarchy.Hierarchy,
#                     Alt_Name=hierarchy.Alt_Name,
#                     Rank_No=hierarchy.Rank_No,
#                     Is_Active=hierarchy.Is_Active,
#                     Created_By=current_user.Usercode,
#                     Modified_By=current_user.Usercode,
#                 ),
#             )
#             # commit changes to db
#             db.commit()
#             # fetch the last inserted data from db
#             new_hierarchy = db.execute(
#                 text("SELECT * FROM dfHierarchy WHERE Id = LAST_INSERT_ID();")
#             ).one()
#             return new_hierarchy
#         except Exception as err:
#             db.rollback()
#             raise HTTPException(
#                 status_code=status.HTTP_400_BAD_REQUEST, detail=f"MySQL Error: {err}"
#             )

#     def update_hierarchy_by_code(
#         self, code: str, hierarchy: HierarchyUpdate, db: Session, current_user: User
#     ):
#         try:
#             # check if it exists
#             old_hierarchy = hierarchy_service.get_hierarchy_by_code(code, db)
#             # update the data
#             db.execute(
#                 text(
#                     "UPDATE dfHierarchy SET Code = :Code, Hierarchy = :Hierarchy, Alt_Name = :Alt_Name, Rank_No = :Rank_No, Is_Active = :Is_Active, Modified_By = :Modified_By WHERE Code = :Code2;"
#                 ),
#                 dict(
#                     Code=(hierarchy.Code if hierarchy.Code else old_hierarchy.Code),
#                     Hierarchy=(
#                         hierarchy.Hierarchy
#                         if hierarchy.Hierarchy
#                         else old_hierarchy.Hierarchy
#                     ),
#                     Alt_Name=(
#                         hierarchy.Alt_Name
#                         if hierarchy.Alt_Name
#                         else old_hierarchy.Alt_Name
#                     ),
#                     Rank_No=(
#                         hierarchy.Rank_No
#                         if hierarchy.Rank_No
#                         else old_hierarchy.Rank_No
#                     ),
#                     Is_Active=(
#                         hierarchy.Is_Active
#                         if hierarchy.Is_Active
#                         else old_hierarchy.Is_Active
#                     ),
#                     Modified_By=current_user.Usercode,
#                     Code2=code,
#                 ),
#             )
#             # commit changes to db
#             db.commit()
#             # fetch updated data
#             h_code = hierarchy.Code if hierarchy.Code else old_hierarchy.Code
#             updated_data = hierarchy_service.get_hierarchy_by_code(h_code, db)
#             return updated_data
#         except Exception as err:
#             db.rollback()
#             raise err

#     def activate_hierarchy_by_code(self, code: str, db: Session, current_user: User):
#         try:
#             db.execute(
#                 text(
#                     "UPDATE dfHierarchy SET Is_Active = :Is_Active, Modified_By = :Modified_By WHERE Code = :Code;"
#                 ),
#                 dict(
#                     Is_Active=1,
#                     Modified_By=current_user.Usercode,
#                     Code=code,
#                 ),
#             )
#             db.commit()
#             return hierarchy_service.get_hierarchy_by_code(code, db)
#         except Exception as err:
#             db.rollback()
#             raise err

#     def deactivate_hierarchy_by_code(self, code: str, db: Session, current_user: User):
#         try:
#             db.execute(
#                 text(
#                     "UPDATE dfHierarchy SET Is_Active = :Is_Active, Modified_By = :Modified_By WHERE Code = :Code;"
#                 ),
#                 dict(
#                     Is_Active=0,
#                     Modified_By=current_user.Usercode,
#                     Code=code,
#                 ),
#             )
#             db.commit()
#             return hierarchy_service.get_hierarchy_by_code(code, db)
#         except Exception as err:
#             db.rollback()
#             raise err

#     def delete_hierarchy_by_code(self, code: str, db: Session):
#         try:
#             # check if it exists
#             hierarchy_to_delete = hierarchy_service.get_hierarchy_by_code(code, db)
#             # delete the data
#             db.execute(
#                 text("DELETE FROM dfHierarchy WHERE Code = :Code;"),
#                 dict(Code=code),
#             )
#             # commit changes to db
#             db.commit()
#         except Exception as err:
#             db.rollback()
#             raise err
