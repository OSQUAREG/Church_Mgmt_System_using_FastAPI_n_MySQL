from datetime import datetime

from fastapi import HTTPException, status  # type: ignore
from sqlalchemy import text  # type: ignore
from sqlalchemy.orm import Session  # type: ignore

from ...authentication.models.auth import User, UserAccess
from ...hierarchy_mgmt.models.church import ChurchBase, ChurchUpdate
from ...common.utils import check_if_new_name_exist, get_level_no, set_user_access


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

    async def create_new_church(
        self,
        level_code: str,
        church: ChurchBase,
        db: Session,
        current_user: User,
        current_user_access: UserAccess,
    ):
        try:
            # check and get church level no
            level_no = get_level_no(level_code, current_user.HeadChurch_Code, db)
            # set user access
            set_user_access(
                current_user_access,
                headchurch_code=current_user.HeadChurch_Code,
                role_code=["ADM", "SAD"],
                # level_code=["CHU"],
                level_no=level_no - 1,
                module_code=["HRCH"],
                # submodule_code=["HEAD", "CL1"],
                access_type=["CR"],
            )
            # checks if Name already exist
            check_if_new_name_exist(
                church.Name, current_user.HeadChurch_Code, "tblChurches", db
            )
            # insert new church
            db.execute(
                text(
                    """
                    INSERT INTO tblChurches
                        (Name, Alt_Name, Address, Founding_Date, About, Mission, Vision, Motto, Contact_No, Contact_No2, Contact_Email, Contact_Email2, Town_Code, State_Code, Region_Code, Country_Code, Is_Active, Level_Code, HeadChurch_Code, Created_By, Modified_By)
                    VALUES
                        (:Name, :Alt_Name, :Address, :Founding_Date, :About, :Mission, :Vision, :Motto, :Contact_No, :Contact_No2, :Contact_Email, :Contact_Email2, :Town_Code, :State_Code, :Region_Code, :Country_Code, :Is_Active, :Level_Code, :HeadChurch_Code, :Created_By, :Modified_By);
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
                    Level_Code=level_code.upper(),
                    HeadChurch_Code=current_user.HeadChurch_Code,
                    Created_By=current_user.Usercode,
                    Modified_By=current_user.Usercode,
                ),
            )
            db.commit()
            new_church = db.execute(
                text("SELECT * FROM tblChurches WHERE Id = LAST_INSERT_ID();")
            ).one()
            return new_church
        except Exception as err:
            db.rollback()
            raise err

    async def approve_church_by_code(
        self,
        code: str,
        db: Session,
        current_user: User,
        current_user_access: UserAccess,
    ):
        try:
            # fetch church data
            church = await self.get_church_by_code(
                code, db, current_user, current_user_access
            )
            # check if church is active
            if not church.Is_Active:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="church must be active before it can be approved.",
                )
            # get church level no
            level_no = get_level_no(church.Level_Code, current_user.HeadChurch_Code, db)
            # set user access
            set_user_access(
                current_user_access,
                headchurch_code=current_user.HeadChurch_Code,
                role_code=["ADM", "SAD"],
                # level_code=["CHU"],
                level_no=level_no - 1,
                module_code=["HRCH"],
                # submodule_code=["HEAD", "CL1"],
                access_type=["AR"],
            )
            # update church
            db.execute(
                text(
                    """
                    UPDATE tblChurches 
                    SET Status = :Status, Status_By = :Status_By, Status_Date = :Status_Date WHERE Code = :Code AND Is_Active :Is_Active;
                    """
                ),
                dict(
                    Status="APR",
                    Status_By=current_user.Usercode,
                    Status_Date=datetime.now(),
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

    async def get_all_churches(
        self, db: Session, current_user: User, current_user_access: UserAccess
    ):
        try:
            # set user access
            set_user_access(
                current_user_access,
                headchurch_code=current_user.HeadChurch_Code,
                # role_code=["ADM", "SAD"],
                # level_code=["CHU", "CL1"],
                module_code=["HRCH"],
                # submodule_code=["HEAD", "CL1"],
                access_type=["VW"],
            )
            # fetch all churches
            churches = db.execute(
                text(
                    "SELECT * FROM tblChurches WHERE HeadChurch_Code = :HeadChurch_Code ORDER BY Code;"
                ),
                dict(HeadChurch_Code=current_user.HeadChurch_Code),
            ).all()
            return churches
        except Exception as err:
            db.rollback()
            raise err

    async def get_churches_by_level(
        self,
        level_code: str,
        db: Session,
        current_user: User,
        current_user_access: UserAccess,
    ):
        try:
            # set user access
            set_user_access(
                current_user_access,
                headchurch_code=current_user.HeadChurch_Code,
                # role_code=["ADM", "SAD"],
                # level_code=["CHU", "CL1"],
                module_code=["HRCH"],
                # submodule_code=["HEAD", "CL1"],
                access_type=["VW"],
            )
            # fetch churches by level
            churches = db.execute(
                text(
                    "SELECT * FROM tblChurches WHERE HeadChurch_Code = :HeadChurch_Code AND Level_Code = :Level_Code ORDER BY Code;"
                ),
                dict(
                    HeadChurch_Code=current_user.HeadChurch_Code, Level_Code=level_code
                ),
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
                # role_code=["ADM", "SAD"],
                # level_code=["CHU", "CL1"],
                module_code=["HRCH"],
                # submodule_code=["HEAD", "CL1"],
                access_type=["VW", "ED", "AR"],
            )
            # fetch church
            church = db.execute(
                text(
                    "SELECT * FROM tblChurches WHERE HeadChurch_Code = :HeadChurch_Code AND Code = :Code;"
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

    async def update_church_by_code(
        self,
        code: str,
        church: ChurchUpdate,
        db: Session,
        current_user: User,
        current_user_access: UserAccess,
    ):
        try:
            # fetch church data
            old_church = await self.get_church_by_code(
                code, db, current_user, current_user_access
            )
            # check if church is active
            if not church.Is_Active:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Church must be active before it can be updated.",
                )
            # get church level no
            level_no = get_level_no(
                old_church.Level_Code, current_user.HeadChurch_Code, db
            )
            # set user access
            set_user_access(
                current_user_access,
                headchurch_code=current_user.HeadChurch_Code,
                role_code=["ADM", "SAD"],
                church_code=old_church.Code,
                # level_code=["CHU"],
                level_no=level_no,
                module_code=["HRCH"],
                # submodule_code=["HEAD", "CL1"],
                access_type=["ED"],
            )
            # check if new Name already exist
            if church.Name is not None and church.Name != old_church.Name:
                check_if_new_name_exist(
                    church.Name, current_user.HeadChurch_Code, "tblChurches", db
                )
            # update church data
            db.execute(
                text(
                    """
                    UPDATE tblChurches
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
            # fetch church data
            church = await self.get_church_by_code(
                code, db, current_user, current_user_access
            )
            # check if church is active
            if church.Is_Active:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Church is already active.",
                )
            # get church level no
            level_no = get_level_no(church.Level_Code, current_user.HeadChurch_Code, db)
            # set user access
            set_user_access(
                current_user_access,
                headchurch_code=current_user.HeadChurch_Code,
                role_code=["ADM", "SAD"],
                # level_code=["CHU"],
                level_no=level_no - 1,
                module_code=["HRCH"],
                # submodule_code=["HEAD", "CL1"],
                access_type=["ED"],
            )
            # activate church
            db.execute(
                text(
                    "UPDATE tblChurches SET Is_Active = :Is_Active, Status = :Status, Status_By = :Status_By, Status_Date = :Status_Date, Modified_By = :Modified_By WHERE Code = :Code;"
                ),
                dict(
                    Is_Active=1,
                    Status="ACT",
                    Status_By=current_user.Usercode,
                    Status_Date=datetime.now(),
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

    async def deactivate_church_by_code(
        self,
        code: str,
        db: Session,
        current_user: User,
        current_user_access: UserAccess,
    ):
        try:
            # fetch church data
            church = await self.get_church_by_code(
                code, db, current_user, current_user_access
            )
            # check if church is active
            if church.Is_Active:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Church is already active.",
                )
            # get church level no
            level_no = get_level_no(church.Level_Code, current_user.HeadChurch_Code, db)
            # set user access
            set_user_access(
                current_user_access,
                headchurch_code=current_user.HeadChurch_Code,
                role_code=["ADM", "SAD"],
                # level_code=["CHU"],
                level_no=level_no - 1,
                module_code=["HRCH"],
                # submodule_code=["HEAD", "CL1"],
                access_type=["ED"],
            )
            # deactivate church
            db.execute(
                text(
                    "UPDATE tblChurches SET Is_Active = :Is_Active, Status = :Status, Status_By = :Status_By, Status_Date = :Status_Date, Modified_By = :Modified_By WHERE Code = :Code;"
                ),
                dict(
                    Is_Active=0,
                    Status="INA",
                    Status_By=current_user.Usercode,
                    Status_Date=datetime.now(),
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
