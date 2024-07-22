from typing import Annotated, Optional


from fastapi import HTTPException, status, Depends  # type: ignore
from sqlalchemy import text  # type: ignore
from sqlalchemy.orm import Session  # type: ignore

from ...church_admin.models.hierarchy import HierarchyUpdate
from ...authentication.models.auth import User, UserAccess
from ...common.config import settings
from ...common.database import get_db
from ...common.utils import set_user_access
from ...common.dependencies import (
    get_current_user,
    get_current_user_access,
    set_db_current_user,
)

db_schema_headchu = settings.db_schema_headchu
db_schema_generic = settings.db_schema_generic


class HierarchyService:
    """
    Hierarchy Services
    - Get All Hierarchies
    - Get Hierarchy by Code
    - Activate Hierarchy by Code
    - Deactivate Hierarchy by Code
    - Update Hierarchy by Code
    """

    def __init__(
        self, db: Session, current_user: User, current_user_access: UserAccess
    ):
        self.db = db
        self.current_user = current_user
        self.current_user_access = current_user_access

    async def get_all_hierarchies(self, is_active: Optional[bool] = None):
        try:
            # set user access
            set_user_access(
                self.current_user_access,
                head_code=self.current_user.Head_Code,
                module_code=["ALLM", "HCHM"],
                access_type=["RD"],
            )

            hierarchies = (
                self.db.execute(
                    text(
                        f"""
                        SELECT A.*, A.Code AS Level_Code, B.Level_No
                        FROM {db_schema_headchu}.tblChurchLevels A
                        LEFT JOIN {db_schema_generic}.tblHierarchy B ON B.Code = A.Hierarchy_Code
                        WHERE Head_Code = :Head_Code;
                        """
                    ),
                    dict(Head_Code=self.current_user.Head_Code),
                ).all()
                if is_active is None
                else self.db.execute(
                    text(
                        f"""
                        SELECT A.*, A.Code AS Level_Code, B.Level_No 
                        FROM {db_schema_headchu}.tblChurchLevels A
                        LEFT JOIN {db_schema_generic}.tblHierarchy B ON B.Code = A.Hierarchy_Code
                        WHERE Head_Code = :Head_Code AND A.Is_Active = :Is_Active;
                        """
                    ),
                    dict(Head_Code=self.current_user.Head_Code, Is_Active=is_active),
                ).all()
            )
            return hierarchies
        except Exception as err:
            self.db.rollback()
            raise err

    async def get_hierarchy_by_code(self, code: str):
        try:
            # set user access
            set_user_access(
                self.current_user_access,
                head_code=self.current_user.Head_Code,
                role_code=["ADM", "SAD"],
                level_code=["CHU"],
                module_code=["ALLM", "HCHM"],
                submodule_code=["ALLS", "HEAD", "HCHL"],
                access_type=["RD", "UP"],
            )
            # fetch data from self.db
            hierarchy = self.db.execute(
                text(
                    f"""
                    SELECT A.*, A.Code AS Level_Code, B.Level_No
                    FROM {db_schema_headchu}.tblChurchLevels A
                    LEFT JOIN {db_schema_generic}.tblHierarchy B ON B.Code = A.Hierarchy_Code
                    WHERE Head_Code = :Head_Code AND (A.Code = :Code OR Hierarchy_Code = :Hierarchy_Code);
                    """
                ),
                dict(
                    Head_Code=self.current_user.Head_Code,
                    Code=code,
                    Level_Code=code,
                    Hierarchy_Code=code,
                ),
            ).first()
            if not hierarchy:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Hierarchy with code: {code.upper()} not found",
                )
            return hierarchy
        except Exception as err:
            self.db.rollback()
            raise err

    async def activate_hierarchy_by_code(self, code: str):
        try:
            # set user access
            set_user_access(
                self.current_user_access,
                head_code=self.current_user.Head_Code,
                role_code=["ADM", "SAD"],
                level_code=["CHU"],
                module_code=["ALLM", "HCHM"],
                submodule_code=["ALLS", "HEAD", "HCHL"],
                access_type=["UP"],
            )
            # fetch data from db
            hierarchy = await self.get_hierarchy_by_code(code)
            # print(hierarchy)
            if self.current_user.Head_Code != hierarchy.Head_Code:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Access Denied: Operation not allowed.",
                )
            if hierarchy.Is_Active == 1:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Church Hierarchy: '{hierarchy.Level_Name} ({hierarchy.Level_Code})' is already active.",
                )
            self.db.execute(
                text(
                    f"""
                    UPDATE {db_schema_headchu}.tblChurchLevels
                    SET Is_Active = :Is_Active, Modified_By = :Modified_By
                    WHERE Head_Code = :Head_Code AND Is_Active = :Is_Active2 
                        AND Code = :Code;
                    """
                ),
                dict(
                    Is_Active=1,
                    Modified_By=self.current_user.Usercode,
                    Head_Code=self.current_user.Head_Code,
                    Is_Active2=0,
                    Code=hierarchy.Level_Code,
                ),
            )
            self.db.commit()
            return await self.get_hierarchy_by_code(code)
        except Exception as err:
            self.db.rollback()
            raise err

    async def deactivate_hierarchy_by_code(self, code: str):
        try:
            # set user access
            set_user_access(
                self.current_user_access,
                head_code=self.current_user.Head_Code,
                role_code=["ADM", "SAD"],
                level_code=["CHU"],
                module_code=["ALLM", "HCHM"],
                submodule_code=["ALLS", "HEAD", "HCHL"],
                access_type=["UP"],
            )
            # fetch data from self.db
            hierarchy = await self.get_hierarchy_by_code(code)
            if self.current_user.Head_Code != hierarchy.Head_Code:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Operation not allowed.",
                )
            if hierarchy.Is_Active == 0:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Church Hierarchy: '{hierarchy.Level_Name} ({hierarchy.Level_Code})' is already inactive.",
                )
            self.db.execute(
                text(
                    f"""
                    UPDATE {db_schema_headchu}.tblChurchLevels 
                    SET Is_Active = :Is_Active, Modified_By = :Modified_By 
                    WHERE Head_Code = :Head_Code AND Is_Active = :Is_Active2 
                        AND Code = :Code;
                    """
                ),
                dict(
                    Is_Active=0,
                    Modified_By=self.current_user.Usercode,
                    Head_Code=self.current_user.Head_Code,
                    Is_Active2=1,
                    Code=hierarchy.Level_Code,
                ),
            )
            self.db.commit()
            return await self.get_hierarchy_by_code(code)
        except Exception as err:
            self.db.rollback()
            raise err

    async def update_hierarchy_by_code(self, code: str, hierarchy: HierarchyUpdate):
        try:
            # set user access
            set_user_access(
                self.current_user_access,
                head_code=self.current_user.Head_Code,
                role_code=["ADM", "SAD"],
                level_code=["CHU"],
                module_code=["ALLM", "HCHM"],
                submodule_code=["ALLS", "HEAD", "HCHL"],
                access_type=["UP"],
            )
            # fetch data from self.db
            old_hierarchy = await self.get_hierarchy_by_code(code)
            # checks if hierarchy exist
            if not old_hierarchy:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Hierarchy with code: {code.upper()} not found",
                )
            # checks if user is allowed to update
            if self.current_user.Head_Code != old_hierarchy.Head_Code:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Operation not allowed.",
                )
            # updates hierarchy
            self.db.execute(
                text(
                    f"""
                    UPDATE {db_schema_headchu}.tblChurchLevels
                    SET Level_Name = :Level_Name, Code = :Code, Is_Active = :Is_Active, Modified_By = :Modified_By
                    WHERE Head_Code = :Head_Code AND (Code = :OldCode OR Hierarchy_Code = :Hierarchy_Code);
                    """
                ),
                dict(
                    Level_Name=(
                        hierarchy.Level_Name
                        if hierarchy.Level_Name
                        else old_hierarchy.Level_Name
                    ),
                    Code=(
                        hierarchy.Level_Code
                        if hierarchy.Level_Code
                        else old_hierarchy.Code
                    ),
                    Is_Active=(
                        hierarchy.Is_Active
                        if hierarchy.Is_Active
                        else old_hierarchy.Is_Active
                    ),
                    Modified_By=self.current_user.Usercode,
                    Head_Code=self.current_user.Head_Code,
                    OldCode=code,
                    Hierarchy_Code=code,
                ),
            )
            self.db.commit()
            h_code = (
                hierarchy.Level_Code
                if hierarchy.Level_Code
                else old_hierarchy.Hierarchy_Code
            )
            return await self.get_hierarchy_by_code(h_code)
        except Exception as err:
            self.db.rollback()
            raise err


def get_hierarchy_services(
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
    current_user_access: Annotated[User, Depends(get_current_user_access)],
    db_current_user: Annotated[str, Depends(set_db_current_user)],
):
    return HierarchyService(db, current_user, current_user_access)
