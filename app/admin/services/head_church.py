from sqlalchemy import text  # type: ignore
from sqlalchemy.orm import Session  # type: ignore

from ...authentication.models.auth import User
from ...hierarchy_mgmt.services.head_church import HeadChurchService
from ...hierarchy_mgmt.models.head_church import HeadChurch
from ...common.utils import (
    check_if_new_name_exist,
    check_if_new_code_exist,
    custom_title_case,
)

head_church_services = HeadChurchService()


class HeadChurchAdminService:
    """
    Head Church Admin Services
    - Create Head Church
    - Get All Head Churches
    - Activate Head Church by Code
    - Deactivate Head Church by Code
    """

    def create_head_church(
        self, head_church: HeadChurch, db: Session, current_user: User
    ):
        try:
            # check if new Code or Name already exists
            check_if_new_code_exist(head_church.Code, "tblCLHeadChurch", db)
            check_if_new_name_exist(head_church.Name, "tblCLHeadChurch", db)
            # insert new head church
            db.execute(
                text(
                    """
                    INSERT INTO tblCLHeadChurch
                        (Code, Name, Alt_Name, Address, Founding_Date, About, Mission, Vision, Motto, Contact_No, Contact_No2, Contact_Email, Contact_Email2, Town_Code, State_Code, Region_Code, Country_Code, Is_Active, Created_By, Modified_By)
                    VALUES
                        (:Code, :Name, :Alt_Name, :Address, :Founding_Date, :About, :Mission, :Vision, :Motto, :Contact_No, :Contact_No2, :Contact_Email, :Contact_Email2, :Town_Code, :State_Code, :Region_Code, :Country_Code, :Is_Active, :Created_By, :Modified_By);
                    """
                ),
                dict(
                    Code=head_church.Code,
                    Name=head_church.Name,
                    Alt_Name=head_church.Alt_Name,
                    Address=head_church.Address,
                    Founding_Date=head_church.Founding_Date,
                    About=head_church.About,
                    Mission=head_church.Mission,
                    Vision=head_church.Vision,
                    Motto=head_church.Motto,
                    Contact_No=head_church.Contact_No,
                    Contact_No2=head_church.Contact_No2,
                    Contact_Email=head_church.Contact_Email,
                    Contact_Email2=head_church.Contact_Email2,
                    Town_Code=head_church.Town_Code,
                    State_Code=head_church.State_Code,
                    Region_Code=head_church.Region_Code,
                    Country_Code=head_church.Country_Code,
                    Is_Active=head_church.Is_Active,
                    Created_By=current_user.Usercode,
                    Modified_By=current_user.Usercode,
                ),
            )
            db.commit()
            new_head_church = db.execute(
                text("SELECT * FROM tblCLHeadChurch WHERE Id = LAST_INSERT_ID();")
            ).one()
            return new_head_church
        except Exception as err:
            db.rollback()
            raise err

    def get_all_head_churches(self, db: Session):
        try:
            head_churches = db.execute(
                text("SELECT * FROM tblCLHeadChurch ORDER BY Id;"),
            ).all()
            return head_churches
        except Exception as err:
            db.rollback()
            raise err

    def activate_head_church_by_code(self, code: str, db: Session, current_user: User):
        try:

            # check if it exists
            head_church_services.get_head_church_by_code(code, db)
            # update the data
            db.execute(
                text(
                    "UPDATE tblCLHeadChurch SET Is_Active = :Is_Active, Modified_By = :Modified_By WHERE Code = :Code;"
                ),
                dict(Is_Active=1, Modified_By=current_user.Usercode, Code=code),
            )
            # commit changes to db
            db.commit()
            return head_church_services.get_head_church_by_code(code, db)
        except Exception as err:
            db.rollback()
            raise err

    def deactivate_head_church_by_code(
        self, code: str, db: Session, current_user: User
    ):
        try:
            # check if it exists
            head_church_services.get_head_church_by_code(code, db)
            # update the data
            db.execute(
                text(
                    "UPDATE tblCLHeadChurch SET Is_Active = :Is_Active, Modified_By = :Modified_By WHERE Code = :Code;"
                ),
                dict(Is_Active=0, Modified_By=current_user.Usercode, Code=code),
            )
            # commit changes to db
            db.commit()
            return head_church_services.get_head_church_by_code(code, db)
        except Exception as err:
            db.rollback()
            raise err
