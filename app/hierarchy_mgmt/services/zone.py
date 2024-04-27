from fastapi import HTTPException, status  # type: ignore
from sqlalchemy import text  # type: ignore
from sqlalchemy.orm import Session  # type: ignore

from ...authentication.models.auth import User
from ...hierarchy_mgmt.models.zone import ZoneBase, ZoneUpdate
from ...common.utils import check_if_new_name_exist


class ZoneService:
    """
    #### Zone Services
    - Create New Zone
    - Get All Zones
    - Get Zone by Code
    - Update Zone by Code
    - Activate Zone by Code
    - Deactivate Zone by Code
    """

    def create_new_zone(self, zone: ZoneBase, db: Session, current_user: User):
        try:
            # checks if Name already exist
            check_if_new_name_exist(zone.Name, "tblCLZone", db)
            # insert new zone
            db.execute(
                text(
                    """
                    INSERT INTO tblCLZone
                        (Name, Alt_Name, Address, Founding_Date, About, Mission, Vision, Motto, Contact_No, Contact_No2, Contact_Email, Contact_Email2, Town_Code, State_Code, Region_Code, Country_Code, Is_Active, Province_Code, HeadChurch_Code, Created_By, Modified_By)
                    VALUES
                        (:Name, :Alt_Name, :Address, :Founding_Date, :About, :Mission, :Vision, :Motto, :Contact_No, :Contact_No2, :Contact_Email, :Contact_Email2, :Town_Code, :State_Code, :Region_Code, :Country_Code, :Is_Active, :Province_Code, :HeadChurch_Code, :Created_By, :Modified_By);
                    """
                ),
                dict(
                    Name=zone.Name,
                    Alt_Name=zone.Alt_Name,
                    Address=zone.Address,
                    Founding_Date=zone.Founding_Date,
                    About=zone.About,
                    Mission=zone.Mission,
                    Vision=zone.Vision,
                    Motto=zone.Motto,
                    Contact_No=zone.Contact_No,
                    Contact_No2=zone.Contact_No2,
                    Contact_Email=zone.Contact_Email,
                    Contact_Email2=zone.Contact_Email2,
                    Town_Code=zone.Town_Code,
                    State_Code=zone.State_Code,
                    Region_Code=zone.Region_Code,
                    Country_Code=zone.Country_Code,
                    Is_Active=zone.Is_Active,
                    Province_Code=zone.Province_Code,
                    HeadChurch_Code=zone.HeadChurch_Code,
                    Created_By=current_user.Usercode,
                    Modified_By=current_user.Usercode,
                ),
            )
            db.commit()
            new_zone = db.execute(
                text("SELECT * FROM tblCLZone WHERE Id = LAST_INSERT_ID();")
            ).one()
            return new_zone
        except Exception as err:
            db.rollback()
            raise err

    def get_all_zones(self, db: Session, current_user: User):
        try:
            zones = db.execute(
                text(
                    "SELECT * FROM tblCLZone WHERE HeadChurch_Code = :HeadChurch_Code ORDER BY Id;"
                ),
                dict(HeadChurch_Code=current_user.HeadChurch_Code),
            ).all()
            return zones
        except Exception as err:
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail=f"MySQL Error: {err}"
            )

    def get_zone_by_code(self, code: str, db: Session, current_user: User):
        try:
            zone = db.execute(
                text(
                    "SELECT * FROM tblCLZone WHERE HeadChurch_Code = :HeadChurch_Code AND Code = :Code;"
                ),
                dict(HeadChurch_Code=current_user.HeadChurch_Code, Code=code),
            ).first()
            if zone is None:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND, detail="Zone not found"
                )
            return zone
        except Exception as err:
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail=f"MySQL Error: {err}"
            )

    def update_zone_by_code(
        self, code: str, zone: ZoneUpdate, db: Session, current_user: User
    ):
        try:
            old_zone = self.get_zone_by_code(code, db, current_user)
            # checks if new Name already exists
            if zone.Name is not None and zone.Name != old_zone.Name:
                check_if_new_name_exist(zone.Name, "tblCLZone", db)
            # update zone
            db.execute(
                text(
                    """
                    UPDATE tblCLZone
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
                        Province_Code = :Province_Code,
                        HeadChurch_Code = :HeadChurch_Code,
                        Is_Active = :Is_Active,
                        Modified_By = :Modified_By
                    WHERE
                        Code = :Code2;
                    """
                ),
                dict(
                    Code=zone.Code if zone.Code else old_zone.Code,
                    Name=zone.Name if zone.Name else old_zone.Name,
                    Alt_Name=zone.Alt_Name if zone.Alt_Name else old_zone.Alt_Name,
                    Address=zone.Address if zone.Address else old_zone.Address,
                    Founding_Date=(
                        zone.Founding_Date
                        if zone.Founding_Date
                        else old_zone.Founding_Date
                    ),  # type: ignore
                    About=zone.About if zone.About else old_zone.About,
                    Mission=zone.Mission if zone.Mission else old_zone.Mission,
                    Vision=zone.Vision if zone.Vision else old_zone.Vision,
                    Motto=zone.Motto if zone.Motto else old_zone.Motto,
                    Contact_No=(
                        zone.Contact_No if zone.Contact_No else old_zone.Contact_No
                    ),
                    Contact_No2=(
                        zone.Contact_No2 if zone.Contact_No2 else old_zone.Contact_No2
                    ),
                    Contact_Email=(
                        zone.Contact_Email
                        if zone.Contact_Email
                        else old_zone.Contact_Email
                    ),
                    Contact_Email2=(
                        zone.Contact_Email2
                        if zone.Contact_Email2
                        else old_zone.Contact_Email2
                    ),
                    Town_Code=zone.Town_Code if zone.Town_Code else old_zone.Town_Code,
                    State_Code=(
                        zone.State_Code if zone.State_Code else old_zone.State_Code
                    ),
                    Region_Code=(
                        zone.Region_Code if zone.Region_Code else old_zone.Region_Code
                    ),
                    Country_Code=(
                        zone.Country_Code
                        if zone.Country_Code
                        else old_zone.Country_Code
                    ),
                    Province_Code=(
                        zone.Province_Code
                        if zone.Province_Code
                        else old_zone.Province_Code
                    ),
                    HeadChurch_Code=current_user.HeadChurch_Code,
                    Is_Active=zone.Is_Active if zone.Is_Active else old_zone.Is_Active,
                    Modified_By=current_user.Usercode,
                    Code2=code,
                ),
            )
            db.commit()
            z_code = zone.Code if zone.Code else old_zone.Code
            return self.get_zone_by_code(z_code, db, current_user)
        except Exception as err:
            db.rollback()
            raise err

    def activate_zone_by_code(self, code: str, db: Session, current_user: User):
        try:
            zone = self.get_zone_by_code(code, db, current_user)
            if zone is None:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND, detail="Zone not found"
                )
            db.execute(
                text(
                    "UPDATE tblCLZone SET Is_Active = :Is_Active, Modified_By = :Modified_By WHERE Code = :Code;"
                ),
                dict(Is_Active=1, Code=code, Modified_By=current_user.Usercode),
            )
            db.commit()
            return self.get_zone_by_code(code, db, current_user)
        except Exception as err:
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail=f"MySQL Error: {err}"
            )

    def deactivate_zone_by_code(self, code: str, db: Session, current_user: User):
        try:
            zone = self.get_zone_by_code(code, db)
            if zone is None:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND, detail="Zone not found"
                )
            db.execute(
                text(
                    "UPDATE tblCLZone SET Is_Active = :Is_Active, Modified_By = :Modified_By WHERE Code = :Code;"
                ),
                dict(Is_Active=0, Code=code, Modified_By=current_user.Usercode),
            )
            db.commit()
            return self.get_zone_by_code(code, db)
        except Exception as err:
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail=f"MySQL Error: {err}"
            )

    # def delete_zone_by_code(self, code: str, db: Session):
    #     try:
    #         zone = self.get_zone_by_code(code, db)
    #         db.execute(
    #             text("DELETE FROM tblCLZone WHERE Code = :Code;"), dict(Code=code)
    #         )
    #         db.commit()
    #     except Exception as err:
    #         db.rollback()
    #         raise HTTPException(
    #             status_code=status.HTTP_400_BAD_REQUEST, detail=f"MySQL Error: {err}"
    #         )
