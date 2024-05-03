from fastapi import HTTPException, status  # type: ignore
from sqlalchemy import text  # type: ignore
from sqlalchemy.orm import Session  # type: ignore

from ...authentication.models.auth import User
from ...hierarchy_mgmt.models.branch import Branch, BranchUpdate


class BranchService:
    """
    #### Branch Services
    - Create New Branch
    - Get All Branches
    - Get Branch by Code
    - Update Branch by Code
    - Activate Branch by Code
    - Deactivate Branch by Code
    """

    def create_new_branch(self, branch: Branch, db: Session, current_user: User):
        try:
            db.execute(
                text(
                    """
                    INSERT INTO tblCLBranch
                        (Name, Alt_Name, Address, Founding_Date, About, Mission, Vision, Motto, Contact_No, Contact_No2, Contact_Email, Contact_Email2, Town_Code, State_Code, Region_Code, Country_Code, Is_Active, Area_Code, Zone_Code, Province_Code, HeadChurch_Code, Created_By, Modified_By)
                    VALUES
                        (:Name, :Alt_Name, :Address, :Founding_Date, :About, :Mission, :Vision, :Motto, :Contact_No, :Contact_No2, :Contact_Email, :Contact_Email2, :Town_Code, :State_Code, :Region_Code, :Country_Code, :Is_Active, :Area_Code :Zone_Code, :Province_Code, :HeadChurch_Code, :Created_By, :Modified_By);
                    """
                ),
                dict(
                    Name=branch.Name,
                    Alt_Name=branch.Alt_Name,
                    Address=branch.Address,
                    Founding_Date=branch.Founding_Date,
                    About=branch.About,
                    Mission=branch.Mission,
                    Vision=branch.Vision,
                    Motto=branch.Motto,
                    Contact_No=branch.Contact_No,
                    Contact_No2=branch.Contact_No2,
                    Contact_Email=branch.Contact_Email,
                    Contact_Email2=branch.Contact_Email2,
                    Town_Code=branch.Town_Code,
                    State_Code=branch.State_Code,
                    Region_Code=branch.Region_Code,
                    Country_Code=branch.Country_Code,
                    Is_Active=branch.Is_Active,
                    Area_Code=branch.Area_Code,
                    Zone_Code=branch.Zone_Code,
                    Province_Code=branch.Province_Code,
                    HeadChurch_Code=branch.HeadChurch_Code,
                    Created_By=current_user.Usercode,
                    Modified_By=current_user.Usercode,
                ),
            )
            db.commit()
            new_branch = db.execute(
                text("SELECT * FROM tblCLBranch WHERE Id = LAST_INSERT_ID();")
            )
            return new_branch
        except Exception as err:
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail=f"MySQL Error: {err}"
            )
