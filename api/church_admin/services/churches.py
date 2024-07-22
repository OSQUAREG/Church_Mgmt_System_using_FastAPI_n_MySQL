from datetime import datetime
from typing import Annotated, Optional

from fastapi import HTTPException, status, Depends  # type: ignore
from sqlalchemy import text  # type: ignore
from sqlalchemy.orm import Session  # type: ignore

from ...authentication.models.auth import User, UserAccess
from ...church_admin.models.churches import ChurchBase, ChurchUpdate
from ...common.database import get_db
from ...common.utils import (
    check_duplicate_entry,
    check_if_new_code_name_exist,
    get_level,
    set_user_access,
)
from ...common.dependencies import (
    get_current_user,
    get_current_user_access,
    set_db_current_user,
)


class ChurchServices:
    """
    #### Church Service methods
    - Create New Church
    - Approve Church by Code
    - Get All Churches
    - Get Churches by Level
    - Get Church by Code
    - Update Church by Code
    - Activate Church by code
    - Deactivate Church by Code
    """

    def __init__(
        self,
        db: Session,
        current_user: User,
        current_user_access: UserAccess,
    ):
        self.db = db
        self.current_user = current_user
        self.current_user_access = current_user_access

    async def create_new_church(self, level_code: str, church: ChurchBase):
        try:
            # check and get church level no
            level_no = get_level(level_code, self.current_user.Head_Code, self.db)
            # set user access
            set_user_access(
                self.current_user_access,
                head_code=self.current_user.Head_Code,
                role_code=["ADM", "SAD"],
                # level_code=["CHU"],
                level_no=level_no.Level_No - 1,
                module_code=["ALLM", "HRCH"],
                # submodule_code=["HEAD", "CL1"],
                access_type=["CR"],
            )
            # checks if Name already exist
            check_if_new_code_name_exist(
                new_code_name=church.Name,
                table_name="tblChurches",
                schema_name="generic",
                db=self.db,
                action="create",
                head_code=self.current_user.Head_Code,
            )
            # cheeck duplicate entry
            check_duplicate_entry(
                self.db,
                self.current_user.Head_Code,
                "tblChurches",
                "Contact_No",
                church.Contact_No,
                "Level_Code",
                level_code,
            )
            check_duplicate_entry(
                self.db,
                self.current_user.Head_Code,
                "tblChurches",
                "Contact_Email",
                church.Contact_Email,
                "Level_Code",
                level_code,
            )
            # insert new church
            self.db.execute(
                text(
                    """
                    INSERT INTO tblChurches
                        (Name, Alt_Name, Address, Founding_Date, About, Mission, Vision, Motto, Contact_No, Contact_No2, Contact_Email, Contact_Email2, Town_Code, State_Code, Region_Code, Country_Code, Level_Code, Head_Code, Created_By)
                    VALUES
                        (:Name, :Alt_Name, :Address, :Founding_Date, :About, :Mission, :Vision, :Motto, :Contact_No, :Contact_No2, :Contact_Email, :Contact_Email2, :Town_Code, :State_Code, :Region_Code, :Country_Code, :Level_Code, :Head_Code, :Created_By);
                    """
                ),
                dict(
                    Name=church.Name,
                    Alt_Name=church.Alt_Name,
                    Address=church.Address,
                    Founding_Date=church.Founding_Date,
                    About=church.About,
                    Mission=church.Mission,
                    Vision=church.Vision,
                    Motto=church.Motto,
                    Contact_No=church.Contact_No,
                    Contact_No2=church.Contact_No2,
                    Contact_Email=church.Contact_Email,
                    Contact_Email2=church.Contact_Email2,
                    Town_Code=church.Town_Code,
                    State_Code=church.State_Code,
                    Region_Code=church.Region_Code,
                    Country_Code=church.Country_Code,
                    Is_Active=1,
                    Level_Code=level_code.upper(),
                    Head_Code=self.current_user.Head_Code,
                    Created_By=self.current_user.Usercode,
                ),
            )
            self.db.commit()
            new_church = self.db.execute(
                text("SELECT * FROM tblChurches WHERE Id = LAST_INSERT_ID();")
            ).first()
            return new_church
        except Exception as err:
            self.db.rollback()
            raise err

    async def approve_church_by_code(self, id_code: str):
        try:
            # fetch church data
            church = await self.get_church_by_id_code(id_code)
            # check if church is active
            if not church.Is_Active:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Church must be active before it can be approved.",
                )
            if church.Status == "APR":
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Church is already approved!",
                )
            # get church level no
            level_no = get_level(
                church.Level_Code, self.current_user.Head_Code, self.db
            )
            # set user access
            set_user_access(
                self.current_user_access,
                head_code=self.current_user.Head_Code,
                role_code=["ADM", "SAD"],
                level_no=level_no.Level_No - 1,
                module_code=["ALLM", "HRCH"],
                access_type=["AR"],
            )
            # update church
            self.db.execute(
                text(
                    """
                    UPDATE tblChurches 
                    SET Status = :Status, Status_By = :Status_By, Status_Date = :Status_Date 
                    WHERE Id = :Id AND Is_Active = :Is_Active 
                        AND (Status = :Old_Status1 OR Status = :Old_Status2);
                    """
                ),
                dict(
                    Status="APR",
                    Status_By=self.current_user.Usercode,
                    Status_Date=datetime.now(),
                    Id=church.Id,
                    Is_Active=1,
                    Old_Status1="AWT",
                    Old_Status2="ACT",
                ),
            )
            self.db.commit()
            return await self.get_church_by_id_code(id_code)
        except Exception as err:
            self.db.rollback()
            raise err

    async def get_all_churches(self, status_code: Optional[str] = None):
        try:
            # set user access
            set_user_access(
                self.current_user_access,
                head_code=self.current_user.Head_Code,
                module_code=["ALLM", "HRCH"],
                access_type=["VW"],
            )
            # fetch all churches
            churches = (
                self.db.execute(
                    text(
                        """
                        SELECT * FROM tblChurches 
                        WHERE Head_Code = :Head_Code 
                        ORDER BY Code, Level_Code;
                        """
                    ),
                    dict(Head_Code=self.current_user.Head_Code),
                ).all()
                if status_code is None
                else self.db.execute(
                    text(
                        """
                        SELECT * FROM tblChurches 
                        WHERE Head_Code = :Head_Code AND Status = :Status 
                        ORDER BY Code;
                        """
                    ),
                    dict(
                        Head_Code=self.current_user.Head_Code,
                        Status=status_code,
                    ),
                ).all()
            )
            return churches
        except Exception as err:
            self.db.rollback()
            raise err

    async def get_churches_by_level(
        self, level_code: str, status_code: Optional[str] = None
    ):
        try:
            # set user access
            set_user_access(
                self.current_user_access,
                head_code=self.current_user.Head_Code,
                module_code=["ALLM", "HRCH"],
                access_type=["VW"],
            )
            # fetch churches by level
            churches = (
                self.db.execute(
                    text(
                        "SELECT * FROM tblChurches WHERE Head_Code = :Head_Code AND Level_Code = :Level_Code ORDER BY Code;"
                    ),
                    dict(
                        Head_Code=self.current_user.Head_Code,
                        Level_Code=level_code,
                    ),
                ).all()
                if status_code is None
                else self.db.execute(
                    text(
                        """
                        SELECT * FROM tblChurches 
                        WHERE Head_Code = :Head_Code AND Level_Code = :Level_Code 
                            AND Status = :Status ORDER BY Code;
                        """
                    ),
                    dict(
                        Head_Code=self.current_user.Head_Code,
                        Level_Code=level_code,
                        Status=status_code,
                    ),
                ).all()
            )
            return churches
        except Exception as err:
            self.db.rollback()
            raise err

    async def get_church_by_id_code(self, id_code: str):
        try:
            # set user access
            set_user_access(
                self.current_user_access,
                head_code=self.current_user.Head_Code,
                module_code=["ALLM", "HRCH"],
                access_type=["VW", "ED", "AR"],
            )
            # fetch church
            church = self.db.execute(
                text(
                    "SELECT * FROM tblChurches WHERE Head_Code = :Head_Code AND (Code = :Code or Id = :Id);"
                ),
                dict(
                    Head_Code=self.current_user.Head_Code,
                    Code=id_code,
                    Id=id_code,
                ),
            ).first()
            # check if church exists
            if church is None:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Church with code: '{id_code.upper()}' not found in Head Church: {self.current_user.Head_Code}",
                )
            return church
        except Exception as err:
            self.db.rollback()
            raise err

    async def update_church_by_code(self, code: str, church: ChurchUpdate):
        try:
            # fetch church data
            old_church = await self.get_church_by_id_code(code)
            # check if church is active
            if not church.Is_Active:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Church must be active before it can be updated.",
                )
            # get church level no
            level_no = get_level(
                old_church.Level_Code, self.current_user.Head_Code, self.db
            )
            # set user access
            set_user_access(
                self.current_user_access,
                head_code=self.current_user.Head_Code,
                role_code=["ADM", "SAD"],
                church_code=old_church.Code,
                level_no=level_no.Level_No,
                module_code=["ALLM", "HRCH"],
                access_type=["ED"],
            )
            # check if new Name already exist
            if church.Name is not None and church.Name != old_church.Name:
                check_if_new_code_name_exist(
                    church.Name,
                    self.current_user.Head_Code,
                    "tblChurches",
                    self.db,
                    "update",
                    old_church.Name,
                )
            # cheeck duplicate entry
            check_duplicate_entry(
                self.db,
                self.current_user.Head_Code,
                "tblChurches",
                "Contact_No",
                church.Contact_No,
                "Level_Code",
                old_church.Level_Code,
            )
            check_duplicate_entry(
                self.db,
                self.current_user.Head_Code,
                "tblChurches",
                "Contact_Email",
                church.Contact_Email,
                "Level_Code",
                old_church.Level_Code,
            )
            # update church data
            self.db.execute(
                text(
                    """
                    UPDATE tblChurches
                    SET
                        Name = :Name, Alt_Name = :Alt_Name, Address = :Address, Founding_Date = :Founding_Date, About = :About, Mission = :Mission, Vision = :Vision, Motto = :Motto, Contact_No = :Contact_No, Contact_No2 = :Contact_No2, Contact_Email = :Contact_Email, Contact_Email2 = :Contact_Email2, Town_Code = :Town_Code, State_Code = :State_Code, Region_Code = :Region_Code, Country_Code = :Country_Code, Head_Code = :Head_Code,Modified_By = :Modified_By
                    WHERE
                        Code = :Code;
                    """
                ),
                dict(
                    Name=church.Name if church.Name else old_church.Name,
                    Alt_Name=(
                        church.Alt_Name if church.Alt_Name else old_church.Alt_Name
                    ),
                    Address=(church.Address if church.Address else old_church.Address),
                    Founding_Date=(
                        church.Founding_Date
                        if church.Founding_Date
                        else old_church.Founding_Date
                    ),  # type: ignore
                    About=church.About if church.About else old_church.About,
                    Mission=(church.Mission if church.Mission else old_church.Mission),
                    Vision=church.Vision if church.Vision else old_church.Vision,
                    Motto=church.Motto if church.Motto else old_church.Motto,
                    Contact_No=(
                        church.Contact_No
                        if church.Contact_No
                        else old_church.Contact_No
                    ),
                    Contact_No2=(
                        church.Contact_No2
                        if church.Contact_No2
                        else old_church.Contact_No2
                    ),
                    Contact_Email=(
                        church.Contact_Email
                        if church.Contact_Email
                        else old_church.Contact_Email
                    ),
                    Contact_Email2=(
                        church.Contact_Email2
                        if church.Contact_Email2
                        else old_church.Contact_Email2
                    ),
                    Town_Code=(
                        church.Town_Code if church.Town_Code else old_church.Town_Code
                    ),
                    State_Code=(
                        church.State_Code
                        if church.State_Code
                        else old_church.State_Code
                    ),
                    Region_Code=(
                        church.Region_Code
                        if church.Region_Code
                        else old_church.Region_Code
                    ),
                    Country_Code=(
                        church.Country_Code
                        if church.Country_Code
                        else old_church.Country_Code
                    ),
                    Head_Code=self.current_user.Head_Code,
                    Modified_By=self.current_user.Usercode,
                    Code=code,
                ),
            )
            self.db.commit()
            return await self.get_church_by_id_code(code)
        except Exception as err:
            self.db.rollback()
            raise err

    async def activate_church_by_code(self, code: str):
        try:
            # fetch church data
            church = await self.get_church_by_id_code(code)
            # check if church is active
            if church.Is_Active:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Church is already active.",
                )
            # get church level no
            level_no = get_level(
                church.Level_Code, self.current_user.Head_Code, self.db
            )
            # set user access
            set_user_access(
                self.current_user_access,
                head_code=self.current_user.Head_Code,
                role_code=["ADM", "SAD"],
                level_no=level_no.Level_No - 1,
                module_code=["ALLM", "HRCH"],
                access_type=["ED"],
            )
            # activate church
            self.db.execute(
                text(
                    "UPDATE tblChurches SET Is_Active = :Is_Active, Status = :Status, Status_By = :Status_By, Status_Date = :Status_Date, Modified_By = :Modified_By WHERE Code = :Code;"
                ),
                dict(
                    Is_Active=1,
                    Status="ACT",
                    Status_By=self.current_user.Usercode,
                    Status_Date=datetime.now(),
                    Modified_By=self.current_user.Usercode,
                    Code=code,
                ),
            )
            self.db.commit()
            return await self.get_church_by_id_code(code)
        except Exception as err:
            self.db.rollback()
            raise err

    async def deactivate_church_by_code(self, code: str):
        try:
            # fetch church data
            church = await self.get_church_by_id_code(code)
            # check if church is active
            if not church.Is_Active:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Church is already inactive.",
                )
            # get church level no
            level_no = get_level(
                church.Level_Code, self.current_user.Head_Code, self.db
            )
            # set user access
            set_user_access(
                self.current_user_access,
                head_code=self.current_user.Head_Code,
                role_code=["ADM", "SAD"],
                level_no=level_no.Level_No - 1,
                module_code=["ALLM", "HRCH"],
                access_type=["ED"],
            )
            # deactivate church
            self.db.execute(
                text(
                    "UPDATE tblChurches SET Is_Active = :Is_Active, Status = :Status, Status_By = :Status_By, Status_Date = :Status_Date, Modified_By = :Modified_By WHERE Code = :Code;"
                ),
                dict(
                    Is_Active=0,
                    Status="INA",
                    Status_By=self.current_user.Usercode,
                    Status_Date=datetime.now(),
                    Modified_By=self.current_user.Usercode,
                    Code=code,
                ),
            )
            self.db.commit()
            # deactivate all active church lead mapping
            self.db.execute(
                text(
                    """
                    UPDATE tblChurchLeads 
                    SET End_Date = :End_Date, Is_Active = :Is_Active, Modified_By = :Modified_By, Status = :Status, Status_By = :Status_By, Status_Date = :Status_Date 
                    WHERE Church_Code = :Church_Code AND End_Date IS NULL;
                    """
                ),
                dict(
                    End_Date=datetime.now(),
                    Is_Active=0,
                    Status="INA",
                    Status_By=self.current_user.Usercode,
                    Status_Date=datetime.now(),
                    Modified_By=self.current_user.Usercode,
                    Church_Code=code.upper(),
                ),
            )
            self.db.commit()
            return await self.get_church_by_id_code(code)
        except Exception as err:
            self.db.rollback()
            raise err

    @staticmethod
    async def test_query(db: Session):
        try:
            db.execute(
                text(
                    """
                    SELECT 'Good' AS `Check`, H.Level_No, UR.Level_Code  FROM ChMS_generic.tblHierarchy H
                    LEFT JOIN ChMS_testdb.tblUserRole UR  ON UR.Level_Code = H.Code
                    """
                )
            )
        except Exception as err:
            db.rollback()
            raise err


def get_church_services(
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
    current_user_access: Annotated[UserAccess, Depends(get_current_user_access)],
    db_current_user: Annotated[str, Depends(set_db_current_user)],
):
    return ChurchServices(db, current_user, current_user_access)
