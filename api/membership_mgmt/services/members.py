from typing import Annotated

from ...common.utils import check_code_list, get_level_no, set_user_access
from fastapi import Depends  # type: ignore
from sqlalchemy import text  # type: ignore
from sqlalchemy.orm import Session  # type: ignore

from ...authentication.models.auth import User, UserAccess
from ...membership_mgmt.models.members import Member
from ...hierarchy_mgmt.services import get_church_services, ChurchServices
from ...common.database import get_db
from ...common.dependencies import get_current_user, get_current_user_access


class MemberServices:
    """
    ### Member Service methods
    - Create New Member
    - Get All Members
    - Get Member by Code
    - Get Members by Church Code
    - Update Member by Code
    - Activate Member by code
    - Deactivate Member by Code
    """

    def __init__(
        self,
        db: Session,
        current_user: User,
        current_user_access: UserAccess,
        church_services: Annotated[ChurchServices, Depends(get_church_services)],
    ):
        self.db = db
        self.current_user = current_user
        self.current_user_access = current_user_access
        self.church_services = church_services

    async def create_new_member(self, member: Member, church_code: str):
        try:
            # fetch church data
            await self.church_services.get_church_by_code(church_code)
            # fetch and check gender, member type, marital status, employment status
            check_code_list(member.Gender, "Gender", self.db)
            check_code_list(member.Marital_Status, "Marital Status", self.db)
            check_code_list(member.Employ_Status, "Employment Status", self.db)
            check_code_list(member.Type, "Member Type", self.db)

            # set user access
            set_user_access(
                self.current_user_access,
                headchurch_code=self.current_user.HeadChurch_Code,
                church_code=church_code,
                role_code=["ADM", "SAD"],
                module_code=["MBSH"],
                submodule_code=["MBRS"],
                access_type=["CR"],
            )
            # insert new member
            self.db.execute(
                text(
                    """
                    INSERT INTO tblMember
                        (First_Name, Middle_Name, Last_Name, Title, Title2, Family_Name, Is_FamilyHead, Home_Address, Date_of_Birth, Gender, Marital_Status, Employ_Status, Occupation, Office_Address, State_of_Origin, Personal_Contact_No, Contact_No, Contact_No2, Personal_Email, Contact_Email, Contact_Email2, Is_User, Town_Code, State_Code, Region_Code, Country_Code, `Type`, Is_Clergy, HeadChurch_Code, Is_Active)
                    VALUES
                        (:First_Name, :Middle_Name, :Last_Name, :Title, :Title2, :Family_Name, :Is_FamilyHead, :Home_Address, :Date_od Birth, :Gender, :Marital Status, :Employ_Status, :Occupation, :Office_Address, :State_of_Origin, :Personal_Contact_No, :Contact_No, :Contact_No2, :Personal_Email, :Contact_Email, :Contact_Email2, :Is_User, :Town_Code, :State_Code, :Region_Code, :Country_Code, :Type, :Is_Clergy, :HeadChurch_Code, :Is_Active);
                    """
                ),
                dict(
                    First_Name=member.First_Name,
                    Middle_Name=member.Middle_Name,
                    Last_Name=member.Last_Name,
                    Title=member.Title,
                    Title2=member.Title2,
                    Family_Name=member.Family_Name,
                    Is_FamilyHead=member.Is_FamilyHead,
                    Home_Address=member.Home_Address,
                    Date_of_Birth=member.Date_of_Birth,
                    Gender=member.Gender,
                    Marital_Status=member.Marital_Status,
                    Employ_Status=member.Employ_Status,
                    Occupation=member.Occupation,
                    Office_Address=member.Office_Address,
                    State_of_Origin=member.State_of_Origin,
                    Personal_Contact_No=member.Personal_Contact_No,
                    Contact_No=member.Contact_No,
                    Contact_No2=member.Contact_No2,
                    Personal_Email=member.Personal_Email,
                    Contact_Email=member.Contact_Email,
                    Contact_Email2=member.Contact_Email2,
                    Is_User=member.Is_User,
                    Town_Code=member.Town_Code,
                    State_Code=member.State_Code,
                    Region_Code=member.Region_Code,
                    Country_Code=member.Country_Code,
                    Type=member.Type,
                    Is_Clergy=member.Is_Clergy,
                    HeadChurch_Code=member.HeadChurch_Code,
                    Is_Active=member.Is_Active,
                ),
            )
            self.db.commit()
            # fetch new code
            new_code = await self.db.execute(
                text("SELECT Code FROM tblMember WHERE Id = LAST_INSERT_ID();")
            ).first()

            # inserts new member church
            self.db.execute(
                text(
                    """
                INSERT INTO tblMemberChurch
                    (Member_Code, Church_Code, Join_Date, Join_Type, Join_Note)
                VALUES
                    (:Member_Code, :Church_Code, :Join_Date, :Join_Type, :Join_Note);
                """
                ),
                dict(
                    Member_Code=new_code.Code,
                    Church_Code=church_code.upper(),
                    Join_Date=member.Join_Date,
                    Join_Type=member.Join_Type,
                    Join_Note=member.Join_Note,
                    HeadChurch_Code=member.HeadChurch_Code,
                ),
            )
            self.db.commit()
            # fetch new member
            new_member = self.db.execute(text)
            return new_member
        except Exception as err:
            self.db.rollback()
            raise err

    async def get_all_members(self):
        try:
            # set user access
            set_user_access(
                self.current_user_access,
                headchurch_code=self.current_user.HeadChurch_Code,
                # church_code=self.current_user_access.Church_Code,
                role_code=["ADM", "SAD"],
                module_code=["MBSH"],
                submodule_code=["MBRS"],
                access_type=["VW"],
            )
            members = await self.db.execute(
                text(
                    "SELECT * FROM tblMember WHERE HeadChurch_Code = :HeadChurch_Code;"
                ),
                dict(HeadChurch_Code=self.current_user.HeadChurch_Code),
            ).all()
            return members
        except Exception as err:
            raise err

    async def get_member_by_code(self, member_code: str):
        try:
            # fetch member data
            member = await self.db.execute(
                text(
                    "SELECT * FROM tblMember WHERE Code = :Code AND HeadChurch_Code = :HeadChurch_Code;"
                ),
                dict(
                    Code=member_code, HeadChurch_Code=self.current_user.HeadChurch_Code
                ),
            ).first()
            level_no = get_level_no(
                member.Church_Code, self.current_user.HeadChurch_Code, self.db
            )
            # set user access
            set_user_access(
                self.current_user_access,
                headchurch_code=self.current_user.HeadChurch_Code,
                # church_code=self.current_user_access.Church_Code,
                # role_code=["ADM", "SAD"],
                module_code=["MBSH"],
                submodule_code=["MBRS"],
                access_type=["VW", "ED", "CR"],
            )
            member = await self.db.execute(
                text(
                    """
                    SELECT M.* , MC.Church_Code, MC.Join_Date, MC.Join_Type, MC.Join_Note  FROM tblMember M
                    LEFT JOIN tblMemberChurch MC ON MC.Member_Code = M.Code
                    WHERE `Code` = :Code AND MC.Church_Code = :Church_Code AND HeadChurches_Code = :HeadChurch_Code AND M.Is_Active = :Is_Active_M AND MC.Is_Active = :Is_Active_MC;
                    """
                ),
                dict(
                    Code=member_code,
                    HeadChurch_Code=self.current_user.HeadChurch_Code,
                    Is_Active_M=1,
                    Is_Active_MC=1,
                ),
            ).first()
            return member
        except Exception as err:
            raise err

    # async def get_members_by_church_code(self, church_code: str):
    #     try:
    #         # set user access
    #         set_user_access(
    #             self.current_user_access,
    #             headchurch_code=self.current_user.HeadChurch_Code,
    #             # church_code=self.current_user_access.Church_Code,
    #             # role_code=["ADM", "SAD"],
    #             module_code=["MBSH"],
    #             submodule_code=["MBRS"],
    #             access_type=["VW", "ED"],
    #         )
