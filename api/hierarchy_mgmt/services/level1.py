from datetime import datetime
from fastapi import HTTPException, status  # type: ignore
from sqlalchemy import text  # type: ignore
from sqlalchemy.orm import Session  # type: ignore

from ...authentication.models.auth import User, UserAccess
from ..models.level1 import Level1Base, Level1Update
from ...common.utils import check_if_new_name_exist, custom_title_case, set_user_access


class Level1Service:
    """
    #### Level 1 Church Service methods
    - Create New Level 1 Church
    - Approve Level 1 Church by Code
    - Get All Level 1 Churches
    - Get Level 1 Church by Code
    - Update Level 1 Church by Code
    - Activate Level 1 Church by code
    - Deactivate Level 1 Church by Code
    """

    async def create_new_level1_church(
        self,
        church: Level1Base,
        db: Session,
        current_user: User,
        current_user_access: UserAccess,
    ):
        try:
            # set user access
            set_user_access(
                current_user_access,
                headchurch_code=current_user.HeadChurch_Code,
                role_code=["ADM", "SAD"],
                level_code=["CHU", "CL1"],
                module_code=["HRCH"],
                submodule_code=["HEAD", "CL1"],
                access_type=["CR"],
            )
            # checks if Name already exist
            check_if_new_name_exist(church.Name, "tblChurchLevel1", db)
            # insert new church
            db.execute(
                text(
                    """
                    INSERT INTO tblChurchLevel1
                        (Name, Alt_Name, Address, Founding_Date, About, Mission, Vision, Motto, Contact_No, Contact_No2, Contact_Email, Contact_Email2, Town_Code, State_Code, Region_Code, Country_Code, Is_Active, HeadChurch_Code, Created_By, Modified_By)
                    VALUES
                        (:Name, :Alt_Name, :Address, :Founding_Date, :About, :Mission, :Vision, :Motto, :Contact_No, :Contact_No2, :Contact_Email, :Contact_Email2, :Town_Code, :State_Code, :Region_Code, :Country_Code, :Is_Active, :HeadChurch_Code, :Created_By, :Modified_By);
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
                    Is_Active=church.Is_Active,
                    HeadChurch_Code=current_user.HeadChurch_Code,
                    Created_By=current_user.Usercode,
                    Modified_By=current_user.Usercode,
                ),
            )
            db.commit()
            new_church = db.execute(
                text("SELECT * FROM tblChurchLevel1 WHERE Id = LAST_INSERT_ID();")
            ).one()
            return new_church
        except Exception as err:
            db.rollback()
            raise err

    async def approve_level1_church_by_code(
        self,
        code: str,
        db: Session,
        current_user: User,
        current_user_access: UserAccess,
    ):
        try:
            set_user_access(
                current_user_access,
                headchurch_code=current_user.HeadChurch_Code,
                role_code=["ADM", "SAD"],
                level_code=["CHU", "CL1"],
                module_code=["HRCH"],
                submodule_code=["HEAD", "CL1"],
                access_type=["AR"],
            )
            church = await self.get_church_by_code(
                code, db, current_user, current_user_access
            )
            if not church.Is_Active:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="church must be active before it can be approved.",
                )
            db.execute(
                text(
                    "UPDATE tblCLchurch SET Is_Approved = :Is_Approved, Approved_By = :Approved_By, Approved_Date = :Approved_Date WHERE Code = :Code AND Is_Active :Is_Active;"
                ),
                dict(
                    Is_Approved=1,
                    Approved_By=current_user.Usercode,
                    Approved_Date=datetime.now(),
                    Code=code,
                    Is_Active=1,
                ),
            )
            db.commit()
            return await self.get_church_by_code(
                code, db, current_user, current_user_access
            )
        except Exception as err:
            db.rollback()
            raise err

    async def get_all_level1_churches(
        self, db: Session, current_user: User, current_user_access: UserAccess
    ):
        try:
            # set user access
            set_user_access(
                current_user_access,
                headchurch_code=current_user.HeadChurch_Code,
                role_code=["ADM", "SAD"],
                level_code=["CHU", "CL1"],
                module_code=["HRCH"],
                submodule_code=["HEAD", "CL1"],
                access_type=["VW"],
            )
            # fetch all churches
            churches = db.execute(
                text(
                    "SELECT * FROM tblChurchLevel1 WHERE HeadChurch_Code = :HeadChurch_Code ORDER BY Code;"
                ),
                dict(HeadChurch_Code=current_user.HeadChurch_Code),
            ).all()
            return churches
        except Exception as err:
            db.rollback()
            raise err

    async def get_church_by_code(
        self,
        code: str,
        db: Session,
        current_user: User,
        current_user_access: UserAccess,
    ):
        try:
            # set user access
            set_user_access(
                current_user_access,
                headchurch_code=current_user.HeadChurch_Code,
                role_code=["ADM", "SAD"],
                level_code=["CL1"],
                module_code=["HRCH"],
                submodule_code=["HEAD", "CL1"],
                access_type=["VW", "ED", "AR"],
            )
            # fetch church
            church = db.execute(
                text(
                    "SELECT * FROM tblChurchLevel1 WHERE HeadChurch_Code = :HeadChurch_Code AND Code = :Code;"
                ),
                dict(HeadChurch_Code=current_user.HeadChurch_Code, Code=code),
            ).first()
            # check if church exists
            if church is None:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"church with code: '{code.upper()}' not found in Head Church: {current_user.HeadChurch_Code}",
                )
            return church
        except Exception as err:
            db.rollback()
            raise err

    async def update_level1_church_by_code(
        self,
        code: str,
        church: Level1Update,
        db: Session,
        current_user: User,
        current_user_access: UserAccess,
    ):
        try:
            # set user access
            set_user_access(
                current_user_access,
                headchurch_code=current_user.HeadChurch_Code,
                role_code=["ADM", "SAD"],
                level_code=["CHU", "CL1"],
                module_code=["HRCH"],
                submodule_code=["HEAD", "CL1"],
                access_type=["ED"],
            )
            # fetch old church data
            old_church = await self.get_church_by_code(
                code, db, current_user, current_user_access
            )
            # check if new Name already exist
            if church.Name is not None and church.Name != old_church.Name:
                check_if_new_name_exist(church.Name, "tblChurchLevel1", db)
            # update church data
            db.execute(
                text(
                    """
                    UPDATE tblChurchLevel1
                    SET
                        Name = :Name,
                        Alt_Name = :Alt_Name,
                        Address = :Address,
                        Founding_Date = :Founding_Date,
                        About = :About,
                        Mission = :Mission,
                        Vision = :Vision,
                        Motto = :Motto,
                        Contact_No = :Contact_No,
                        Contact_No2 = :Contact_No2,
                        Contact_Email = :Contact_Email,
                        Contact_Email2 = :Contact_Email2,
                        Town_Code = :Town_Code,
                        State_Code = :State_Code,
                        Region_Code = :Region_Code,
                        Country_Code = :Country_Code,
                        Is_Active = :Is_Active,
                        HeadChurch_Code = :HeadChurch_Code,
                        Modified_By = :Modified_By
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
                    ),
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
                    Is_Active=(
                        church.Is_Active if church.Is_Active else old_church.Is_Active
                    ),
                    HeadChurch_Code=current_user.HeadChurch_Code,
                    Modified_By=current_user.Usercode,
                    Code=code,
                ),
            )
            db.commit()
            return await self.get_church_by_code(
                code, db, current_user, current_user_access
            )
        except Exception as err:
            db.rollback()
            raise err

    async def activate_church_by_code(
        self,
        code: str,
        db: Session,
        current_user: User,
        current_user_access: UserAccess,
    ):
        try:
            # set user access
            set_user_access(
                current_user_access,
                headchurch_code=current_user.HeadChurch_Code,
                role_code=["ADM", "SAD"],
                level_code=["CL1"],
                module_code=["HRCH"],
                submodule_code=["HEAD", "CL1"],
                access_type=["ED"],
            )
            await self.get_church_by_code(code, db, current_user, current_user_access)
            db.execute(
                text(
                    "UPDATE tblCLchurch SET Is_Active = :Is_Active, Modified_By = :Modified_By WHERE Code = :Code AND HeadChurch_Code = :HeadChurch_Code;"
                ),
                dict(
                    Is_Active=1,
                    Code=code,
                    HeadChurch_Code=current_user.HeadChurch_Code,
                    Modified_By=current_user.Usercode,
                ),
            )
            db.commit()
            return await self.get_church_by_code(
                code, db, current_user, current_user_access
            )
        except Exception as err:
            db.rollback()
            raise err

    async def deactivate_church_by_code(
        self,
        code: str,
        db: Session,
        current_user: User,
        current_user_access: UserAccess,
    ):
        try:
            # set user access
            set_user_access(
                current_user_access,
                headchurch_code=current_user.HeadChurch_Code,
                role_code=["ADM", "SAD"],
                level_code=["CHU", "CL1"],
                module_code=["HRCH"],
                submodule_code=["HEAD", "CL1"],
                access_type=["ED"],
            )
            await self.get_church_by_code(code, db, current_user, current_user_access)
            db.execute(
                text(
                    "UPDATE tblCLchurch SET Is_Active = :Is_Active, Is_Approved = :Is_Approved, Approved_By = :Approved_By, Approved_Date = :Approved_Date, Modified_By = :Modified_By WHERE Code = :Code;"
                ),
                dict(
                    Is_Active=0,
                    Is_Approved=0,
                    Approved_By=None,
                    Approved_Date=None,
                    Modified_By=current_user.Usercode,
                    Code=code,
                ),
            )
            db.commit()
            return await self.get_church_by_code(
                code, db, current_user, current_user_access
            )
        except Exception as err:
            db.rollback()
            raise err
