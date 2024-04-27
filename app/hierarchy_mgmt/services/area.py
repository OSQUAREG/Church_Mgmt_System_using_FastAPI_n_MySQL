from fastapi import HTTPException, status  # type: ignore
from sqlalchemy import text  # type: ignore
from sqlalchemy.orm import Session  # type: ignore

from ...authentication.models.auth import User
from ...hierarchy_mgmt.models.area import AreaIn, AreaUpdate


class AreaService:
    """
    #### Area Services
    - Create New Area
    - Get All Areas
    - Get Area by Code
    - Update Area by Code
    - Activate Area by Code
    - Deactivate Area by Code
    """

    def create_new_area(self, area: AreaIn, db: Session, current_user: User):
        try:
            db.execute(
                text(
                    """
                    INSERT INTO tblCLArea
                        (Name, Alt_Name, Address, Founding_Date, About, Mission, Vision, Motto, Contact_No, Contact_No2, Contact_Email, Contact_Email2, Town_Code, State_Code, Region_Code, Country_Code, Is_Active, Zone_Code, Province_Code, HeadChurch_Code, Created_By, Modified_By)
                    VALUES
                        (:Name, :Alt_Name, :Address, :Founding_Date, :About, :Mission, :Vision, :Motto, :Contact_No, :Contact_No2, :Contact_Email, :Contact_Email2, :Town_Code, :State_Code, :Region_Code, :Country_Code, :Is_Active, :Zone_Code, :Province_Code, :HeadChurch_Code, :Created_By, :Modified_By);
                    """
                ),
                dict(
                    Name=area.Name,
                    Alt_Name=area.Alt_Name,
                    Address=area.Address,
                    Founding_Date=area.Founding_Date,
                    About=area.About,
                    Mission=area.Mission,
                    Vision=area.Vision,
                    Motto=area.Motto,
                    Contact_No=area.Contact_No,
                    Contact_No2=area.Contact_No2,
                    Contact_Email=area.Contact_Email,
                    Contact_Email2=area.Contact_Email2,
                    Town_Code=area.Town_Code,
                    State_Code=area.State_Code,
                    Region_Code=area.Region_Code,
                    Country_Code=area.Country_Code,
                    Is_Active=area.Is_Active,
                    Zone_Code=area.Zone_Code,
                    Province_Code=area.Province_Code,
                    HeadChurch_Code=area.HeadChurch_Code,
                    Created_By=current_user.Usercode,
                    Modified_By=current_user.Usercode,
                ),
            )
            db.commit()
            new_area = db.execute(
                text("SELECT * FROM tblCLArea WHERE Id = LAST_INSERT_ID();")
            ).one()
            return new_area
        except Exception as err:
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail=f"MySQL Error: {err}"
            )

    def get_all_areas(self, db: Session):
        try:
            areas = db.execute(text("SELECT * FROM tblCLArea;")).all()
            return areas
        except Exception as err:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail=f"MySQL Error: {err}"
            )

    def get_area_by_code(self, code: str, db: Session):
        try:
            area = db.execute(
                text("SELECT * FROM tblCLArea WHERE Code = :Code;"), dict(Code=code)
            ).one()
            return area
        except Exception as err:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail=f"MySQL Error: {err}"
            )

    def update_area_by_code(
        self, code: str, area: AreaUpdate, db: Session, current_user: User
    ):
        try:
            old_area = self.get_area_by_code(code, db)
            db.execute(
                text(
                    """
                    UPDATE tblCLArea
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
                        Zone_Code = :Zone_Code,
                        Province_Code = :Province_Code,
                        HeadChurch_Code = :HeadChurch_Code,
                        Modified_By = :Modified_By
                    WHERE
                        Code = :Code2;
                    """
                ),
                dict(
                    Code=area.Code if area.Code else old_area.Code,
                    Name=area.Name if area.Name else old_area.Name,
                    Alt_Name=area.Alt_Name if area.Alt_Name else old_area.Alt_Name,
                    Address=area.Address if area.Address else old_area.Address,
                    Founding_Date=(
                        area.Founding_Date
                        if area.Founding_Date
                        else old_area.Founding_Date
                    ),  # type: ignore
                    About=area.About if area.About else old_area.About,
                    Mission=area.Mission if area.Mission else old_area.Mission,
                    Vision=area.Vision if area.Vision else old_area.Vision,
                    Motto=area.Motto if area.Motto else old_area.Motto,
                    Contact_No=(
                        area.Contact_No if area.Contact_No else old_area.Contact_No
                    ),
                    Contact_No2=(
                        area.Contact_No2 if area.Contact_No2 else old_area.Contact_No2
                    ),
                    Contact_Email=(
                        area.Contact_Email
                        if area.Contact_Email
                        else old_area.Contact_Email
                    ),
                    Contact_Email2=(
                        area.Contact_Email2
                        if area.Contact_Email2
                        else old_area.Contact_Email2
                    ),
                    Town_Code=area.Town_Code if area.Town_Code else old_area.Town_Code,
                    State_Code=(
                        area.State_Code if area.State_Code else old_area.State_Code
                    ),
                    Region_Code=(
                        area.Region_Code if area.Region_Code else old_area.Region_Code
                    ),
                    Country_Code=(
                        area.Country_Code
                        if area.Country_Code
                        else old_area.Country_Code
                    ),
                    Zone_Code=area.Zone_Code if area.Zone_Code else old_area.Zone_Code,
                    Province_Code=(
                        area.Province_Code
                        if area.Province_Code
                        else old_area.Province_Code
                    ),
                    HeadChurch_Code=(
                        area.HeadChurch_Code
                        if area.HeadChurch_Code
                        else old_area.HeadChurch_Code
                    ),
                    Modified_By=current_user.Usercode,
                ),
            )
            db.commit()
            a_code = area.Code if area.Code else old_area.Code
            new_area = self.get_area_by_code(a_code, db)
            return new_area
        except Exception as err:
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail=f"MySQL Error: {err}"
            )

    def activate_area_by_code(self, code: str, db: Session, current_user: User):
        try:
            area = self.get_area_by_code(code, db)
            if area is None:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND, detail="Area not found"
                )
            db.execute(
                text(
                    "UPDATE tblCLArea SET Is_Active = :Is_Active, Modified_By = :Modified_By WHERE Code = :Code"
                ),
                dict(Is_Active=1, Modified_By=current_user.Usercode, Code=code),
            )
            db.commit()
            return area
        except Exception as err:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail=f"MySQL Error: {err}"
            )

    def deactivate_area_by_code(self, code: str, db: Session, current_user: User):
        try:
            area = self.get_area_by_code(code, db)
            if area is None:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND, detail="Area not found"
                )
            db.execute(
                text(
                    "UPDATE tblCLArea SET Is_Active = :Is_Active, Modified_By = :Modified_By WHERE Code = :Code"
                ),
                dict(Is_Active=0, Modified_By=current_user.Usercode, Code=code),
            )
            db.commit()
            return area
        except Exception as err:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail=f"MySQL Error: {err}"
            )
