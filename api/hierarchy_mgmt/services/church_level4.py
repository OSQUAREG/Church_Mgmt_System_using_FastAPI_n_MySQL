from datetime import datetime
from fastapi import HTTPException, status  # type: ignore
from sqlalchemy import text  # type: ignore
from sqlalchemy.orm import Session  # type: ignore

from ...authentication.models.auth import User, UserAccess
from ..models.church_level4 import ProvinceBase, ProvinceUpdate
from ...common.utils import check_if_new_name_exist, custom_title_case, set_user_access


class ProvinceService:
    """
    #### Province Service methods
    - Create New Province
    - Get All Provinces
    - Get Province by Code
    - Update Province by Code
    - Activate Province by code
    - Deactivate Province by Code
    - Approve Province by Code
    """

    def create_new_province(
        self,
        province: ProvinceBase,
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
                level_code=["PRV"],
                module_code=["HRCH"],
                submodule_code=["HEAD", "CL4"],
                access_type=["CR"],
            )
            # checks if Name already exist
            check_if_new_name_exist(province.Name, "tblCLProvince", db)
            # insert new province
            db.execute(
                text(
                    """
                    INSERT INTO tblCLProvince
                        (Name, Alt_Name, Address, Founding_Date, About, Mission, Vision, Motto, Contact_No, Contact_No2, Contact_Email, Contact_Email2, Town_Code, State_Code, Region_Code, Country_Code, Is_Active, HeadChurch_Code, Created_By, Modified_By)
                    VALUES
                        (:Name, :Alt_Name, :Address, :Founding_Date, :About, :Mission, :Vision, :Motto, :Contact_No, :Contact_No2, :Contact_Email, :Contact_Email2, :Town_Code, :State_Code, :Region_Code, :Country_Code, :Is_Active, :HeadChurch_Code, :Created_By, :Modified_By);
                    """
                ),
                dict(
                    Name=province.Name,
                    Alt_Name=province.Alt_Name,
                    Address=province.Address,
                    Founding_Date=province.Founding_Date,
                    About=province.About,
                    Mission=province.Mission,
                    Vision=province.Vision,
                    Motto=province.Motto,
                    Contact_No=province.Contact_No,
                    Contact_No2=province.Contact_No2,
                    Contact_Email=province.Contact_Email,
                    Contact_Email2=province.Contact_Email2,
                    Town_Code=province.Town_Code,
                    State_Code=province.State_Code,
                    Region_Code=province.Region_Code,
                    Country_Code=province.Country_Code,
                    Is_Active=province.Is_Active,
                    HeadChurch_Code=current_user.HeadChurch_Code,
                    Created_By=current_user.Usercode,
                    Modified_By=current_user.Usercode,
                ),
            )
            db.commit()
            new_province = db.execute(
                text("SELECT * FROM tblCLProvince WHERE Id = LAST_INSERT_ID();")
            ).one()
            return new_province
        except Exception as err:
            db.rollback()
            raise err

    def get_all_provinces(self, db: Session, current_user: User):
        try:
            provinces = db.execute(
                text(
                    "SELECT * FROM tblCLProvince WHERE HeadChurch_Code = :HeadChurch_Code ORDER BY Id;"
                ),
                dict(HeadChurch_Code=current_user.HeadChurch_Code),
            ).all()
            return provinces
        except Exception as err:
            db.rollback()
            raise err

    def get_province_by_code(self, code: str, db: Session, current_user: User):
        try:
            province = db.execute(
                text(
                    "SELECT * FROM tblCLProvince WHERE HeadChurch_Code = :HeadChurch_Code AND Code = :Code;"
                ),
                dict(HeadChurch_Code=current_user.HeadChurch_Code, Code=code),
            ).first()
            if province is None:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Province with code: '{code.upper()}' not found in Head Church: {current_user.HeadChurch_Code}",
                )
            return province
        except Exception as err:
            db.rollback()
            raise err

    def update_province_by_code(
        self, code: str, province: ProvinceUpdate, db: Session, current_user: User
    ):
        try:
            # fetch old province data
            old_province = self.get_province_by_code(code, db, current_user)
            # check if new Name already exist
            if province.Name is not None and province.Name != old_province.Name:
                check_if_new_name_exist(province.Name, "tblCLProvince", db)
            # update province data
            db.execute(
                text(
                    """
                    UPDATE tblCLProvince
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
                    Name=province.Name if province.Name else old_province.Name,
                    Alt_Name=(
                        province.Alt_Name
                        if province.Alt_Name
                        else old_province.Alt_Name
                    ),
                    Address=(
                        province.Address if province.Address else old_province.Address
                    ),
                    Founding_Date=(
                        province.Founding_Date
                        if province.Founding_Date
                        else old_province.Founding_Date
                    ),  # type: ignore
                    About=province.About if province.About else old_province.About,
                    Mission=(
                        province.Mission if province.Mission else old_province.Mission
                    ),
                    Vision=province.Vision if province.Vision else old_province.Vision,
                    Motto=province.Motto if province.Motto else old_province.Motto,
                    Contact_No=(
                        province.Contact_No
                        if province.Contact_No
                        else old_province.Contact_No
                    ),
                    Contact_No2=(
                        province.Contact_No2
                        if province.Contact_No2
                        else old_province.Contact_No2
                    ),
                    Contact_Email=(
                        province.Contact_Email
                        if province.Contact_Email
                        else old_province.Contact_Email
                    ),
                    Contact_Email2=(
                        province.Contact_Email2
                        if province.Contact_Email2
                        else old_province.Contact_Email2
                    ),
                    Town_Code=(
                        province.Town_Code
                        if province.Town_Code
                        else old_province.Town_Code
                    ),
                    State_Code=(
                        province.State_Code
                        if province.State_Code
                        else old_province.State_Code
                    ),
                    Region_Code=(
                        province.Region_Code
                        if province.Region_Code
                        else old_province.Region_Code
                    ),
                    Country_Code=(
                        province.Country_Code
                        if province.Country_Code
                        else old_province.Country_Code
                    ),
                    Is_Active=(
                        province.Is_Active
                        if province.Is_Active
                        else old_province.Is_Active
                    ),  # type: ignore
                    HeadChurch_Code=current_user.HeadChurch_Code,
                    Modified_By=current_user.Usercode,
                    Code=code,
                ),
            )
            db.commit()
            return self.get_province_by_code(code, db, current_user)
        except Exception as err:
            db.rollback()
            raise err

    def activate_province_by_code(self, code: str, db: Session, current_user: User):
        try:
            self.get_province_by_code(code, db, current_user)
            db.execute(
                text(
                    "UPDATE tblCLProvince SET Is_Active = :Is_Active, Modified_By = :Modified_By WHERE Code = :Code AND HeadChurch_Code = :HeadChurch_Code;"
                ),
                dict(
                    Is_Active=1,
                    Code=code,
                    HeadChurch_Code=current_user.HeadChurch_Code,
                    Modified_By=current_user.Usercode,
                ),
            )
            db.commit()
            return self.get_province_by_code(code, db, current_user)
        except Exception as err:
            db.rollback()
            raise err

    def deactivate_province_by_code(self, code: str, db: Session, current_user: User):
        try:
            self.get_province_by_code(code, db, current_user)
            db.execute(
                text(
                    "UPDATE tblCLProvince SET Is_Active = :Is_Active, Is_Approved = :Is_Approved, Approved_By = :Approved_By, Approved_Date = :Approved_Date, Modified_By = :Modified_By WHERE Code = :Code;"
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
            return self.get_province_by_code(code, db, current_user)
        except Exception as err:
            db.rollback()
            raise err

    def approve_province_by_code(self, code: str, db: Session, current_user: User):
        try:
            province = self.get_province_by_code(code, db, current_user)
            if not province.Is_Active:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Province must be active before it can be approved.",
                )
            db.execute(
                text(
                    "UPDATE tblCLProvince SET Is_Approved = :Is_Approved, Approved_By = :Approved_By, Approved_Date = :Approved_Date WHERE Code = :Code;"
                ),
                dict(
                    Is_Approved=1,
                    Approved_By=current_user.Usercode,
                    Approved_Date=datetime.now(),
                    Code=code,
                ),
            )
            db.commit()
            return self.get_province_by_code(code, db, current_user)
        except Exception as err:
            db.rollback()
            raise err
