from fastapi import HTTPException, status  # type: ignore
from sqlalchemy import text  # type: ignore
from sqlalchemy.orm import Session  # type: ignore

from ...authentication.models.auth import User


class HierarchyService:
    """
    Hierarchy Services
    - Get All Hierarchies
    - Get Hierarchy by Code
    - Activate Hierarchy by Code
    - Deactivate Hierarchy by Code
    """

    def get_all_hierarchies(self, db: Session, current_user: User):
        try:
            hierarchies = db.execute(
                text(
                    """
                    SELECT 
                        Head_Code, Level_Code, Hierarchy, Alt_Name, Rank_No, HC.Is_Active FROM ChMS_testdb1.tblHeadChurchLevels HC
                    LEFT JOIN ChMS_testdb1.dfHierarchy H ON H.Code = HC.Level_Code
                    WHERE Head_Code = :Head_Code
                    ORDER BY Rank_No;
                    """
                ),
                dict(Head_Code=current_user.HeadChurch_Code),
            ).all()
            return hierarchies
        except Exception as err:
            db.rollback()
            raise err

    def get_hierarchy_by_code(self, code: str, db: Session, current_user: User):
        try:
            hierarchy = db.execute(
                text(
                    """
                    SELECT 
                        Head_Code, Level_Code, Hierarchy, Alt_Name, Rank_No, HC.Is_Active FROM ChMS_testdb1.tblHeadChurchLevels HC
                    LEFT JOIN ChMS_testdb1.dfHierarchy H ON H.Code = HC.Level_Code
                    WHERE Head_Code = :Head_Code AND Level_Code = :Level_Code;
                    """
                ),
                dict(Head_Code=current_user.HeadChurch_Code, Level_Code=code),
            ).first()
            if not hierarchy:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Hierarchy with code: {code.upper()} not found",
                )
            return hierarchy
        except Exception as err:
            db.rollback()
            raise err

    def activate_hierarchy_by_code(self, code: str, db: Session, current_user: User):
        try:
            hierarchy = self.get_hierarchy_by_code(code, db, current_user)
            if current_user.HeadChurch_Code != hierarchy.Head_Code:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Operation not allowed.",
                )
            db.execute(
                text(
                    f"""
                    UPDATE tblHeadChurchLevels 
                    SET Is_Active = :Is_Active, Modified_By = :Modified_By 
                    WHERE Head_Code = :Head_Code AND Level_Code = ;Level_Code;
                    """
                ),
                dict(
                    Is_Active=1,
                    Modified_By=current_user.Usercode,
                    Head_Code=current_user.HeadChurch_Code,
                    Level_Code=code,
                ),
            )
            db.commit()
            return self.get_hierarchy_by_code(code, db, current_user)
        except Exception as err:
            db.rollback()
            raise err

    def deactivate_hierarchy_by_code(self, code: str, db: Session, current_user: User):
        try:
            hierarchy = self.get_hierarchy_by_code(code, db, current_user)
            if current_user.HeadChurch_Code != hierarchy.Head_Code:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Operation not allowed.",
                )
            db.execute(
                text(
                    f"""
                    UPDATE tblHeadChurchLevels 
                    SET Is_Active = :Is_Active, Modified_By = :Modified_By 
                    WHERE Head_Code = :Head_Code AND Level_Code = ;Level_Code;
                    """
                ),
                dict(
                    Is_Active=0,
                    Modified_By=current_user.Usercode,
                    Head_Code=current_user.HeadChurch_Code,
                    Level_Code=code,
                ),
            )
            db.commit()
            return self.get_hierarchy_by_code(code, db, current_user)
        except Exception as err:
            db.rollback()
            raise err
