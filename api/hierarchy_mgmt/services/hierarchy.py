from typing import Annotated, Optional

from ...common.dependencies import (
    get_current_user,
    get_current_user_access,
    set_db_current_user,
)

from ...common.database import get_db
from fastapi import HTTPException, status, Depends  # type: ignore
from sqlalchemy import text  # type: ignore
from sqlalchemy.orm import Session  # type: ignore

from ...common.utils import set_user_access
from ...hierarchy_mgmt.models.hierarchy import HierarchyUpdate
from ...authentication.models.auth import User, UserAccess


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
                headchurch_code=self.current_user.HeadChurch_Code,
                module_code=["HRCH"],
                access_type=["VW"],
            )

            hierarchies = (
                self.db.execute(
                    text(
                        """
                    SELECT Head_Code, Level_Code, Church_Level, ChurchLevel_Code, Level_No, A.Is_Active 
                    FROM tblHeadChurchLevels A
                    LEFT JOIN dfHierarchy B ON B.Code = A.Level_Code
                    WHERE Head_Code = :Head_Code;
                    """
                    ),
                    dict(Head_Code=self.current_user.HeadChurch_Code),
                ).all()
                if is_active is None
                else self.db.execute(
                    text(
                        """
                    SELECT Head_Code, Level_Code, Church_Level, ChurchLevel_Code, Level_No, A.Is_Active 
                    FROM tblHeadChurchLevels A
                    LEFT JOIN dfHierarchy B ON B.Code = A.Level_Code
                    WHERE Head_Code = :Head_Code AND A.Is_Active = :Is_Active;
                    """
                    ),
                    dict(
                        Head_Code=self.current_user.HeadChurch_Code, Is_Active=is_active
                    ),
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
                headchurch_code=self.current_user.HeadChurch_Code,
                role_code=["ADM", "SAD"],
                level_code=["CHU"],
                module_code=["HRCH"],
                submodule_code=["HEAD", "HIER"],
                access_type=["VW", "ED"],
            )
            # fetch data from self.db
            hierarchy = self.db.execute(
                text(
                    """
                    SELECT Head_Code, Level_Code, Church_Level, ChurchLevel_Code, Level_No, A.Is_Active 
                    FROM tblHeadChurchLevels A
                    LEFT JOIN dfHierarchy B ON B.Code = A.Level_Code
                    WHERE Head_Code = :Head_Code AND (ChurchLevel_Code = :ChurchLevel_Code OR Level_Code = :Level_Code);
                    """
                ),
                dict(
                    Head_Code=self.current_user.HeadChurch_Code,
                    ChurchLevel_Code=code,
                    Level_Code=code,
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
                headchurch_code=self.current_user.HeadChurch_Code,
                role_code=["ADM", "SAD"],
                level_code=["CHU"],
                module_code=["HRCH"],
                submodule_code=["HEAD", "HIER"],
                access_type=["ED"],
            )
            # fetch data from self.db
            hierarchy = await self.get_hierarchy_by_code(code)
            print(hierarchy)
            if self.current_user.HeadChurch_Code != hierarchy.Head_Code:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Operation not allowed.",
                )
            self.db.execute(
                text(
                    """
                    UPDATE tblHeadChurchLevels
                    SET Is_Active = :Is_Active, Modified_By = :Modified_By
                    WHERE Head_Code = :Head_Code AND ChurchLevel_Code IS NOT NULL 
                        AND (Level_Code = :Level_Code OR ChurchLevel_Code = :ChurchLevel_Code);
                    """
                ),
                dict(
                    Is_Active=1,
                    Modified_By=self.current_user.Usercode,
                    Head_Code=self.current_user.HeadChurch_Code,
                    Level_Code=hierarchy.Level_Code,
                    ChurchLevel_Code=code,
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
                headchurch_code=self.current_user.HeadChurch_Code,
                role_code=["ADM", "SAD"],
                level_code=["CHU"],
                module_code=["HRCH"],
                submodule_code=["HEAD", "HIER"],
                access_type=["ED"],
            )
            # fetch data from self.db
            hierarchy = await self.get_hierarchy_by_code(code)
            if self.current_user.HeadChurch_Code != hierarchy.Head_Code:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Operation not allowed.",
                )
            self.db.execute(
                text(
                    """
                    UPDATE tblHeadChurchLevels 
                    SET Is_Active = :Is_Active, Modified_By = :Modified_By 
                    WHERE Head_Code = :Head_Code AND ChurchLevel_Code IS NOT NULL 
                        AND (Level_Code = :Level_Code OR ChurchLevel_Code = :ChurchLevel_Code);
                    """
                ),
                dict(
                    Is_Active=0,
                    Modified_By=self.current_user.Usercode,
                    Head_Code=self.current_user.HeadChurch_Code,
                    Level_Code=code,
                    ChurchLevel_Code=code,
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
                headchurch_code=self.current_user.HeadChurch_Code,
                role_code=["ADM", "SAD"],
                level_code=["CHU"],
                module_code=["HRCH"],
                submodule_code=["HEAD", "HIER"],
                access_type=["ED"],
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
            if self.current_user.HeadChurch_Code != old_hierarchy.Head_Code:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Operation not allowed.",
                )
            # updates hierarchy
            self.db.execute(
                text(
                    """
                    UPDATE tblHeadChurchLevels 
                    SET Church_Level = :Church_Level, ChurchLevel_Code = :ChurchLevel_Code, Is_Active = :Is_Active, Modified_By = :Modified_By 
                    WHERE Head_Code = :Head_Code AND (ChurchLevel_Code = :OldChurchLevel_Code OR Level_Code = :Level_Code);
                    """
                ),
                dict(
                    Church_Level=(
                        hierarchy.Church_Level
                        if hierarchy.Church_Level
                        else old_hierarchy.Church_Level
                    ),
                    ChurchLevel_Code=(
                        hierarchy.ChurchLevel_Code
                        if hierarchy.ChurchLevel_Code
                        else old_hierarchy.ChurchLevel_Code
                    ),
                    Is_Active=(
                        hierarchy.Is_Active
                        if hierarchy.Is_Active
                        else old_hierarchy.Is_Active
                    ),
                    Modified_By=self.current_user.Usercode,
                    Head_Code=self.current_user.HeadChurch_Code,
                    OldChurchLevel_Code=code,
                    Level_Code=code,
                ),
            )
            self.db.commit()
            h_code = (
                hierarchy.ChurchLevel_Code
                if hierarchy.ChurchLevel_Code
                else old_hierarchy.ChurchLevel_Code
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
