from datetime import datetime
from typing import Annotated, Optional

from fastapi import Depends, HTTPException, status  # type: ignore
from sqlalchemy import text  # type: ignore
from sqlalchemy.orm import Session  # type: ignore

from ...authentication.models.auth import User, UserAccess
from ...hierarchy_mgmt.services import get_church_services, ChurchServices
from ...membership_mgmt.models.members import (
    MemberBranchExitIn,
    MemberBranchJoinIn,
    MemberIn,
    MemberUpdate,
)
from ...common.database import get_db
from ...common.utils import validate_code_type, get_level, set_user_access
from ...common.dependencies import (
    get_current_user,
    get_current_user_access,
    set_db_current_user,
)
from ...hierarchy_mgmt.services.church_leads import church_recursive_cte


class MemberServices:
    """
    ### Member Service methods
    - Create New Member
    - Get All Members
    - Get Member by Code
    - Get Current User Member
    - Get Members by Church
    - Get Members by Level
    - Update Member by Code
    - Update Current User Member
    - Activate Member by Code
    - Deactivate Member by Code
    """

    def __init__(
        self,
        db: Session,
        current_user: User,
        current_user_access: UserAccess,
        church_services: ChurchServices,
    ):
        self.db = db
        self.current_user = current_user
        self.current_user_access = current_user_access
        self.church_services = church_services

    async def create_new_member(self, new_member: MemberIn):
        """Create New Member: accessible to only church admins."""
        try:
            # fetch and check if church is a branch
            church = await self.church_services.get_church_by_id_code(
                new_member.Branch_Code
            )
            if church.Level_Code != "BRN":
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Only Branches can have members. Select a valid Branch.",
                )
            # check gender, member type, marital status, employment status, join reason codes
            validate_code_type(new_member.Gender, "Gender", self.db)
            validate_code_type(new_member.Marital_Status, "Marital Status", self.db)
            validate_code_type(new_member.Employ_Status, "Employment Status", self.db)
            validate_code_type(new_member.Type, "Member Type", self.db)
            validate_code_type(new_member.Join_Reason, "Exit/Join Reason", self.db)
            # get level
            level = get_level(
                new_member.Branch_Code, self.current_user.HeadChurch_Code, self.db
            )

            # set user access
            set_user_access(
                self.current_user_access,
                headchurch_code=self.current_user.HeadChurch_Code,
                church_code=new_member.Branch_Code,
                level_no=level.Level_No - 1,
                role_code=["ADM", "SAD"],
                module_code=["ALLM", "MBSH"],
                submodule_code=["ALLS", "MBRS"],
                access_type=["CR"],
            )
            # insert new member
            self.db.execute(
                text(
                    """
                    INSERT INTO tblMember
                        (First_Name, Middle_Name, Last_Name, Title, Title2, Family_Name, Is_FamilyHead, Home_Address, Date_of_Birth, Gender, Marital_Status, Employ_Status, Occupation, Office_Address, State_of_Origin, Country_of_Origin, Personal_Contact_No, Contact_No, Contact_No2, Personal_Email, Contact_Email, Contact_Email2, Town_Code, State_Code, Region_Code, Country_Code, `Type`, Is_Clergy, HeadChurch_Code, Created_By)
                    VALUES
                        (:First_Name, :Middle_Name, :Last_Name, :Title, :Title2, :Family_Name, :Is_FamilyHead, :Home_Address, :Date_of_Birth, :Gender, :Marital_Status, :Employ_Status, :Occupation, :Office_Address, :State_of_Origin, :Country_of_Origin, :Personal_Contact_No, :Contact_No, :Contact_No2, :Personal_Email, :Contact_Email, :Contact_Email2, :Town_Code, :State_Code, :Region_Code, :Country_Code, :Type, :Is_Clergy, :HeadChurch_Code, :Created_By);
                    """
                ),
                dict(
                    First_Name=new_member.First_Name,
                    Middle_Name=new_member.Middle_Name,
                    Last_Name=new_member.Last_Name,
                    Title=new_member.Title,
                    Title2=new_member.Title2,
                    Family_Name=new_member.Family_Name,
                    Is_FamilyHead=new_member.Is_FamilyHead,
                    Home_Address=new_member.Home_Address,
                    Date_of_Birth=new_member.Date_of_Birth,
                    Gender=new_member.Gender,
                    Marital_Status=new_member.Marital_Status,
                    Employ_Status=new_member.Employ_Status,
                    Occupation=new_member.Occupation,
                    Office_Address=new_member.Office_Address,
                    State_of_Origin=new_member.State_of_Origin,
                    Country_of_Origin=new_member.Country_of_Origin,
                    Personal_Contact_No=new_member.Personal_Contact_No,
                    Contact_No=new_member.Contact_No,
                    Contact_No2=new_member.Contact_No2,
                    Personal_Email=new_member.Personal_Email,
                    Contact_Email=new_member.Contact_Email,
                    Contact_Email2=new_member.Contact_Email2,
                    Town_Code=new_member.Town_Code,
                    State_Code=new_member.State_Code,
                    Region_Code=new_member.Region_Code,
                    Country_Code=new_member.Country_Code,
                    Type=new_member.Type,
                    Is_Clergy=new_member.Is_Clergy,
                    HeadChurch_Code=self.current_user.HeadChurch_Code,
                    Created_By=self.current_user.Usercode,
                ),
            )
            self.db.commit()
            # fetch new code
            new_code = self.db.execute(
                text("SELECT Code FROM tblMember WHERE Id = LAST_INSERT_ID();")
            ).first()

            # inserts new member church
            self.db.execute(
                text(
                    """
                INSERT INTO tblMemberBranch
                    (Member_Code, Branch_Code, Join_Date, Join_Reason, Join_Note, HeadChurch_Code, Created_By)
                VALUES
                    (:Member_Code, :Branch_Code, :Join_Date, :Join_Reason, :Join_Note, :HeadChurch_Code, :Created_By);
                """
                ),
                dict(
                    Member_Code=new_code.Code,
                    Branch_Code=new_member.Branch_Code,
                    Join_Date=new_member.Join_Date,
                    Join_Reason=new_member.Join_Reason,
                    Join_Note=new_member.Join_Note,
                    HeadChurch_Code=self.current_user.HeadChurch_Code,
                    Created_By=self.current_user.Usercode,
                ),
            )
            self.db.commit()
            return await self.get_member_by_code(new_code.Code)
        except Exception as err:
            self.db.rollback()
            raise err

    async def get_all_members(self, is_active: Optional[bool] = None):
        """Get All Members: accessible to only head church admins and super-admins."""
        try:
            # set user access
            set_user_access(
                self.current_user_access,
                headchurch_code=self.current_user.HeadChurch_Code,
                level_code=["CHU"],
                role_code=["ADM", "SAD"],
                module_code=["ALLM", "MBSH"],
                submodule_code=["ALLS", "MBRS"],
                access_type=["VW"],
            )
            members = (
                await self.db.execute(
                    text(
                        """
                        SELECT M.* , MC.Branch_Code, MC.Join_Date, MC.Join_Reason, MC.Join_Note FROM tblMember M
                        LEFT JOIN tblMemberBranch MC ON MC.Member_Code = M.Code
                        WHERE HeadChurch_Code = :HeadChurch_Code
                        ORDER BY `Code`;
                        """
                    ),
                    dict(HeadChurch_Code=self.current_user.HeadChurch_Code),
                ).all()
                if is_active is None
                else await self.db.execute(
                    text(
                        """
                        SELECT M.* , MC.Branch_Code, MC.Join_Date, MC.Join_Reason, MC.Join_Note FROM tblMember M
                        LEFT JOIN tblMemberBranch MC ON MC.Member_Code = M.Code
                        WHERE HeadChurch_Code = :HeadChurch_Code AND M.Is_Active = :Is_Active AND MC.Is_Active = :Is_Active
                        ORDER BY `Code`;
                        """
                    ),
                    dict(
                        HeadChurch_Code=self.current_user.HeadChurch_Code,
                        Is_Active=is_active,
                    ),
                ).all()
            )
            return members
        except Exception as err:
            raise err

    async def get_member_by_code(self, member_code: str):
        """Get Member By Code: accessible to church admins and executives of same/higher level/church"""
        try:
            # fetch member data
            member = self.db.execute(
                text(
                    """
                    SELECT M.* , MC.Branch_Code, MC.Join_Date, MC.Join_Reason, MC.Join_Note, MC.Exit_Date, MC.Exit_Reason, MC.Exit_Note
                    FROM tblMember M
                    LEFT JOIN tblMemberBranch MC ON MC.Member_Code = M.Code
                    WHERE M.Code = :Code AND M.HeadChurch_Code = :HeadChurch_Code 
                        AND M.Is_Active = :Is_Active AND MC.Is_Active = :Is_Active;
                    """
                ),
                dict(
                    Code=member_code,
                    HeadChurch_Code=self.current_user.HeadChurch_Code,
                    Is_Active=1,
                ),
            ).first()
            # get level
            level_no = get_level(
                member.Branch_Code, self.current_user.HeadChurch_Code, self.db
            )
            # set user access
            set_user_access(
                self.current_user_access,
                headchurch_code=self.current_user.HeadChurch_Code,
                church_code=member.Branch_Code,
                level_no=level_no.Level_No - 1,
                role_code=["ADM", "SAD", "EXC"],
                module_code=["ALLM", "MBSH"],
                submodule_code=["ALLS", "MBRS"],
                access_type=["VW", "ED", "CR"],
            )
            # check if member exists
            if member is None:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND, detail="Member not found"
                )
            return member
        except Exception as err:
            raise err

    async def get_current_user_member(self):
        """Get Current User Member: accessible to only the current logged in member."""
        try:
            member = await self.db.execute(
                text(
                    """
                    SELECT M.* , MC.Branch_Code, MC.Join_Date, MC.Join_Reason, MC.Join_Note FROM tblMember M
                    LEFT JOIN tblMemberBranch MC ON MC.Member_Code = M.Code
                    WHERE `Code` = :Code AND HeadChurch_Code = :HeadChurch_Code AND M.Is_Active = :Is_Active AND MC.Is_Active = :Is_Active;
                    """
                ),
                dict(
                    Code=self.current_user.Usercode,
                    HeadChurch_Code=self.current_user.HeadChurch_Code,
                    Is_Active=1,
                ),
            ).first()
            return member
        except Exception as err:
            raise err

    async def get_members_by_church(self, church_code: str):
        """Get Members By Church Code: accessible to only church admins and executives of same/higher level/church"""
        try:
            level = get_level(church_code, self.current_user.HeadChurch_Code, self.db)
            # set user access
            set_user_access(
                self.current_user_access,
                headchurch_code=self.current_user.HeadChurch_Code,
                church_code=church_code,
                level_no=level.Level_No - 1,
                role_code=["ADM", "SAD", "EXC"],
                module_code=["ALLM", "MBSH"],
                submodule_code=["ALLS", "MBRS"],
                access_type=["VW", "ED"],
            )
            # fetch members
            members = (
                self.db.execute(
                    text(
                        """
                        SELECT M.* , MC.Branch_Code, MC.Join_Date, MC.Join_Reason, MC.Join_Note 
                        FROM tblMember M
                            LEFT JOIN tblMemberBranch MC ON MC.Member_Code = M.Code
                        WHERE HeadChurch_Code = :HeadChurch_Code 
                            AND M.Is_Active = :Is_Active AND MC.Is_Active = :Is_Active
                            AND MC.Branch_Code = :Church_Code;
                        """
                    ),
                    dict(
                        Church_Code=church_code.upper(),
                        HeadChurch_Code=self.current_user.HeadChurch_Code,
                        Is_Active=1,
                    ),
                ).all()
                if level.Level_No == 8  # if church is a branch
                else self.db.execute(
                    text(
                        f"""
                        {church_recursive_cte}
                        SELECT M.* , MC.Branch_Code, MC.Join_Date, MC.Join_Reason, MC.Join_Note FROM tblMember M
                            LEFT JOIN tblMemberBranch MC ON MC.Member_Code = M.Code
                        WHERE HeadChurch_Code = :HeadChurch_Code 
                            AND M.Is_Active = :Is_Active AND MC.Is_Active = :Is_Active
                            AND MC.Branch_Code IN (
                                SELECT Church FROM ChurchHierarchy
                                WHERE Church_Level = 'BRN'
                            );
                        """
                    ),
                    dict(
                        Church_Code=church_code.upper(),
                        HeadChurch_Code=self.current_user.HeadChurch_Code,
                        Is_Active=1,
                    ),
                ).all()
            )
            return members
        except Exception as err:
            raise err

    async def get_members_by_level(self, level_code: str):
        """Get Members By Level Code: accessible to only church admins and executives of same/higher level/church"""
        try:
            level_no = get_level(level_code, self.current_user.HeadChurch_Code, self.db)
            # set user access
            set_user_access(
                self.current_user_access,
                headchurch_code=self.current_user.HeadChurch_Code,
                level_no=level_no.Level_No - 1,
                # role_code=["ADM", "SAD"],
                module_code=["ALLM", "MBSH"],
                submodule_code=["ALLS", "MBRS"],
                access_type=["VW", "ED"],
            )
            # fetch members
            members = await self.db.execute(
                text(
                    """
                    SELECT M.* , MC.Branch_Code, MC.Join_Date, MC.Join_Reason, MC.Join_Note FROM tblMember M
                    LEFT JOIN tblMemberBranch MC ON MC.Member_Code = M.Code
                    WHERE HeadChurch_Code = :HeadChurch_Code 
                        AND M.Is_Active = :Is_Active AND MC.Is_Active = :Is_Active
                        AND MC.Level_Code = :Level_Code;
                    """
                ),
                dict(
                    Level_Code=level_code.upper(),
                    HeadChurch_Code=self.current_user.HeadChurch_Code,
                    Is_Active=1,
                ),
            ).all()
            return members
        except Exception as err:
            raise err

    async def update_member_by_code(self, member_code: str, member: MemberUpdate):
        """Update Member By Code: accessible to only the admins and executives of same/higher level/church."""
        try:
            # fetch member data
            old_member = await self.get_member_by_code(member_code)
            # get church level
            level_no = get_level(
                member.Branch_Code, self.current_user.HeadChurch_Code, self.db
            )
            # set user access
            set_user_access(
                self.current_user_access,
                headchurch_code=self.current_user.HeadChurch_Code,
                church_code=member.Branch_Code,
                level_no=level_no.Level_No - 1,
                role_code=["ADM", "SAD", "EXC"],
                module_code=["ALLM", "MBSH"],
                submodule_code=["ALLS", "MBRS"],
                access_type=["ED"],
            )
            # update member
            await self.db.execute(
                text(
                    """
                    UPDATE tblMember 
                    SET First_Name = :First_Name, Last_Name = :Last_Name, Middle_Name = :Middle_Name, Title = :Title, Title2 = :Title2, Family_Name = :Family_Name, Is_FamilyHead = :Is_FamilyHead, Home_Address = :Home_Address, Date_of_Birth = :Date_of_Birth, Gender = :Gender, Marital_Status = :Marital_Status, Employ_Status = :Employ_Status, Occupation = :Occupation, Office_Address = :Office_Address, State_of_Origin = :State_of_Origin, Personal_Contact_No = :Personal_Contact_No, Contact_No = :Contact_No, Contact_No2 = :Contact_No2, Personal_Email = :Personal_Email, Contact_Email = :Contact_Email, Contact_Email2 = :Contact_Email2, Is_User = :Is_User, Town_Code = :Town_Code, State_Code = :State_Code, Region_Code = :Region_Code, Country_Code = :Country_Code, `Type` = :Type, Is_Clergy = :Is_Clergy, Modified_By = :Modified_By
                    WHERE `Code` = :Code AND HeadChurch_Code = :HeadChurch_Code;
                    """
                ),
                dict(
                    First_Name=(
                        member.First_Name
                        if member.First_Name
                        else old_member.First_Name
                    ),
                    Last_Name=(
                        member.Last_Name if member.Last_Name else old_member.Last_Name
                    ),
                    Middle_Name=(
                        member.Middle_Name
                        if member.Middle_Name
                        else old_member.Middle_Name
                    ),
                    Title=member.Title if member.Title else old_member.Title,
                    Title2=member.Title2 if member.Title2 else old_member.Title2,
                    Family_Name=(
                        member.Family_Name
                        if member.Family_Name
                        else old_member.Family_Name
                    ),
                    Is_FamilyHead=(
                        member.Is_FamilyHead
                        if member.Is_FamilyHead
                        else old_member.Is_FamilyHead
                    ),
                    Home_Address=(
                        member.Home_Address
                        if member.Home_Address
                        else old_member.Home_Address
                    ),
                    Date_of_Birth=(
                        member.Date_of_Birth
                        if member.Date_of_Birth
                        else old_member.Date_of_Birth
                    ),
                    Gender=member.Gender if member.Gender else old_member.Gender,
                    Marital_Status=(
                        member.Marital_Status
                        if member.Marital_Status
                        else old_member.Marital_Status
                    ),
                    Employ_Status=(
                        member.Employ_Status
                        if member.Employ_Status
                        else old_member.Employ_Status
                    ),
                    Occupation=(
                        member.Occupation
                        if member.Occupation
                        else old_member.Occupation
                    ),
                    Office_Address=(
                        member.Office_Address
                        if member.Office_Address
                        else old_member.Office_Address
                    ),
                    State_of_Origin=(
                        member.State_of_Origin
                        if member.State_of_Origin
                        else old_member.State_of_Origin
                    ),
                    Personal_Contact_No=(
                        member.Personal_Contact_No
                        if member.Personal_Contact_No
                        else old_member.Personal_Contact_No
                    ),
                    Contact_No=(
                        member.Contact_No
                        if member.Contact_No
                        else old_member.Contact_No
                    ),
                    Contact_No2=(
                        member.Contact_No2
                        if member.Contact_No2
                        else old_member.Contact_No2
                    ),
                    Personal_Email=(
                        member.Personal_Email
                        if member.Personal_Email
                        else old_member.Personal_Email
                    ),
                    Contact_Email=(
                        member.Contact_Email
                        if member.Contact_Email
                        else old_member.Contact_Email
                    ),
                    Contact_Email2=(
                        member.Contact_Email2
                        if member.Contact_Email2
                        else old_member.Contact_Email2
                    ),
                    Is_User=member.Is_User if member.Is_User else old_member.Is_User,
                    Town_Code=(
                        member.Town_Code if member.Town_Code else old_member.Town_Code
                    ),
                    State_Code=(
                        member.State_Code
                        if member.State_Code
                        else old_member.State_Code
                    ),
                    Region_Code=(
                        member.Region_Code
                        if member.Region_Code
                        else old_member.Region_Code
                    ),
                    Country_Code=(
                        member.Country_Code
                        if member.Country_Code
                        else old_member.Country_Code
                    ),
                    Type=member.Type if member.Type else old_member.Type,
                    Is_Clergy=(
                        member.Is_Clergy if member.Is_Clergy else old_member.Is_Clergy
                    ),
                    Modified_By=self.current_user.Code,
                    HeadChurch_Code=self.current_user.HeadChurch_Code,
                    Code=member_code,
                ),
            )
            self.db.commit()
            return await self.get_member_by_code(member_code)
        except Exception as err:
            self.db.rollback()
            raise err

    async def update_current_user_member(self, member: MemberUpdate):
        """Update Current User Member: accessible to only the current logged in member."""
        try:
            member_code = self.current_user.Usercode
            # fetch member data
            old_member = await self.get_member_by_code(member_code)
            # update member
            await self.db.execute(
                text(
                    """
                    UPDATE tblMember 
                    SET First_Name = :First_Name, Last_Name = :Last_Name, Middle_Name = :Middle_Name, Title = :Title, Title2 = :Title2, Family_Name = :Family_Name, Is_FamilyHead = :Is_FamilyHead, Home_Address = :Home_Address, Date_of_Birth = :Date_of_Birth, Gender = :Gender, Marital_Status = :Marital_Status, Employ_Status = :Employ_Status, Occupation = :Occupation, Office_Address = :Office_Address, State_of_Origin = :State_of_Origin, Personal_Contact_No = :Personal_Contact_No, Contact_No = :Contact_No, Contact_No2 = :Contact_No2, Personal_Email = :Personal_Email, Contact_Email = :Contact_Email, Contact_Email2 = :Contact_Email2, Is_User = :Is_User, Town_Code = :Town_Code, State_Code = :State_Code, Region_Code = :Region_Code, Country_Code = :Country_Code, `Type` = :Type, Is_Clergy = :Is_Clergy, Modified_By = :Modified_By
                    WHERE `Code` = :Code AND HeadChurch_Code = :HeadChurch_Code;
                    """
                ),
                dict(
                    First_Name=(
                        member.First_Name
                        if member.First_Name
                        else old_member.First_Name
                    ),
                    Last_Name=(
                        member.Last_Name if member.Last_Name else old_member.Last_Name
                    ),
                    Middle_Name=(
                        member.Middle_Name
                        if member.Middle_Name
                        else old_member.Middle_Name
                    ),
                    Title=member.Title if member.Title else old_member.Title,
                    Title2=member.Title2 if member.Title2 else old_member.Title2,
                    Family_Name=(
                        member.Family_Name
                        if member.Family_Name
                        else old_member.Family_Name
                    ),
                    Is_FamilyHead=(
                        member.Is_FamilyHead
                        if member.Is_FamilyHead
                        else old_member.Is_FamilyHead
                    ),
                    Home_Address=(
                        member.Home_Address
                        if member.Home_Address
                        else old_member.Home_Address
                    ),
                    Date_of_Birth=(
                        member.Date_of_Birth
                        if member.Date_of_Birth
                        else old_member.Date_of_Birth
                    ),
                    Gender=member.Gender if member.Gender else old_member.Gender,
                    Marital_Status=(
                        member.Marital_Status
                        if member.Marital_Status
                        else old_member.Marital_Status
                    ),
                    Employ_Status=(
                        member.Employ_Status
                        if member.Employ_Status
                        else old_member.Employ_Status
                    ),
                    Occupation=(
                        member.Occupation
                        if member.Occupation
                        else old_member.Occupation
                    ),
                    Office_Address=(
                        member.Office_Address
                        if member.Office_Address
                        else old_member.Office_Address
                    ),
                    State_of_Origin=(
                        member.State_of_Origin
                        if member.State_of_Origin
                        else old_member.State_of_Origin
                    ),
                    Personal_Contact_No=(
                        member.Personal_Contact_No
                        if member.Personal_Contact_No
                        else old_member.Personal_Contact_No
                    ),
                    Contact_No=(
                        member.Contact_No
                        if member.Contact_No
                        else old_member.Contact_No
                    ),
                    Contact_No2=(
                        member.Contact_No2
                        if member.Contact_No2
                        else old_member.Contact_No2
                    ),
                    Personal_Email=(
                        member.Personal_Email
                        if member.Personal_Email
                        else old_member.Personal_Email
                    ),
                    Contact_Email=(
                        member.Contact_Email
                        if member.Contact_Email
                        else old_member.Contact_Email
                    ),
                    Contact_Email2=(
                        member.Contact_Email2
                        if member.Contact_Email2
                        else old_member.Contact_Email2
                    ),
                    Is_User=member.Is_User if member.Is_User else old_member.Is_User,
                    Town_Code=(
                        member.Town_Code if member.Town_Code else old_member.Town_Code
                    ),
                    State_Code=(
                        member.State_Code
                        if member.State_Code
                        else old_member.State_Code
                    ),
                    Region_Code=(
                        member.Region_Code
                        if member.Region_Code
                        else old_member.Region_Code
                    ),
                    Country_Code=(
                        member.Country_Code
                        if member.Country_Code
                        else old_member.Country_Code
                    ),
                    Type=member.Type if member.Type else old_member.Type,
                    Is_Clergy=(
                        member.Is_Clergy if member.Is_Clergy else old_member.Is_Clergy
                    ),
                    Modified_By=self.current_user.Code,
                    HeadChurch_Code=self.current_user.HeadChurch_Code,
                    Code=member_code,
                ),
            )
            self.db.commit()
            return await self.get_current_user_member()
        except Exception as err:
            self.db.rollback()
            raise err

    async def deactivate_member_by_code(
        self, member_code, member_church: MemberBranchExitIn
    ):
        """Deactivate Member by Code: accessible to only church admins in the same/higher level/church."""
        try:
            member = await self.get_member_by_code(member_code)
            level = get_level("BRN", self.current_user.HeadChurch_Code, self.db)
            # check exit type
            if member_church.Exit_Reason:
                validate_code_type(
                    member_church.Exit_Reason, "Exit/Join Reason", self.db
                )
            # set user access
            set_user_access(
                self.current_user_access,
                headchurch_code=self.current_user.HeadChurch_Code,
                church_code=member.Branch_Code,
                level_no=level.Level_No - 1,
                role_code=["ADM", "SAD"],
                module_code=["ALLM", "MBSH"],
                submodule_code=["ALLS", "MBRS"],
                access_type=["ED"],
            )
            # deactivate member
            self.db.execute(
                text(
                    """
                    UPDATE tblMember
                    SET Is_Active = :Is_Active
                    WHERE `Code` = :Code AND HeadChurch_Code = :HeadChurch_Code AND Is_Active = :Is_Active2;
                    """
                ),
                dict(
                    Is_Active=0,
                    Code=member.Code,
                    HeadChurch_Code=self.current_user.HeadChurch_Code,
                    Is_Active2=1,
                ),
            )
            self.db.commit()
            # deactivate member church
            await self.exit_member_from_all_churches(member.Code)
            # self.db.execute(
            #     text(
            #         """
            #         UPDATE tblMemberBranch
            #         SET Is_Active = :Is_Active, Exit_Date = :Exit_Date, Exit_Note = :Exit_Note, Exit_Reason = :Exit_Reason
            #         WHERE Member_Code = :Member_Code AND Is_Active = :Is_Active2 AND HeadChurch_Code = :HeadChurch_Code;
            #         """
            #     ),
            #     dict(
            #         Is_Active=0,
            #         Exit_Date=(
            #             member_church.Exit_Date
            #             if member_church.Exit_Date
            #             else datetime.now()
            #         ),
            #         Exit_Note=(
            #             member_church.Exit_Note
            #             if member_church.Exit_Note
            #             else "Deactivated"
            #         ),
            #         Exit_Reason=(
            #             member_church.Exit_Reason
            #             if member_church.Exit_Reason
            #             else "OTH"
            #         ),
            #         Member_Code=member.Code,
            #         Is_Active2=1,
            #         HeadChurch_Code=self.current_user.HeadChurch_Code,
            #     ),
            # )
            # self.db.commit()
            return await self.get_member_by_code(member.Code)
        except Exception as err:
            self.db.rollback()
            raise err

    async def activate_member_by_code(
        self, member_code, member_church: MemberBranchJoinIn
    ):
        """Activate Member by Code: accessible to only church admins in the same/higher level/church."""
        try:
            member = await self.get_member_by_code(member_code)
            level = get_level(
                member.Branch_Code, self.current_user.HeadChurch_Code, self.db
            )
            # check exit type
            if member_church.Join_Reason:
                validate_code_type(
                    member_church.Join_Reason, "Exit/Join Reason", self.db
                )
            # set user access
            set_user_access(
                self.current_user_access,
                headchurch_code=self.current_user.HeadChurch_Code,
                church_code=member.Branch_Code,
                level_no=level.Level_No - 1,
                role_code=["ADM", "SAD"],
                module_code=["ALLM", "MBSH"],
                submodule_code=["ALLS", "MBRS"],
                access_type=["ED"],
            )
            # activate member
            self.db.execute(
                text(
                    """
                    UPDATE tblMember
                    SET Is_Active = :Is_Active
                    WHERE `Code` = :Code AND HeadChurch_Code = :HeadChurch_Code AND Is_Active = :Is_Active2;
                    """
                ),
                dict(
                    Is_Active=1,
                    Code=member.Member_Code,
                    HeadChurch_Code=self.current_user.HeadChurch_Code,
                    Is_Active2=0,
                ),
            )
            self.db.commit()
            # insert new member church
            self.db.execute(
                text(
                    """
                    INSERT INTO tblMemberBranch
                    (Member_Code, Branch_Code, Join_Date, Join_Note, Join_Reason, HeadChurch_Code)
                    VALUES
                    (:Member_Code, :Branch_Code, :Join_Date, :Join_Note, :Join_Reason, :HeadChurch_Code);
                    """
                ),
                dict(
                    Member_Code=member.Code,
                    Branch_Code=member_church.Branch_Code,
                    Join_Date=member_church.Join_Date,
                    Join_Note=member_church.Join_Note,
                    Join_Reason=member_church.Join_Reason,
                    HeadChurch_Code=self.current_user.HeadChurch_Code,
                ),
            )
            self.db.commit()
            return await self.get_member_by_code(member.Code)
        except Exception as err:
            self.db.rollback()
            raise err

    async def get_member_all_churches_by_code(
        self, member_code: str, is_active: Optional[bool] = None
    ):
        """Get Member All Churches: accessible to only church admins in the same/higher level/church."""
        try:
            member = await self.get_member_by_code(member_code)
            level = get_level(
                member.Branch_Code, self.current_user.HeadChurch_Code, self.db
            )
            # set user access
            set_user_access(
                self.current_user_access,
                headchurch_code=self.current_user.HeadChurch_Code,
                church_code=member.Branch_Code,
                level_no=level.Level_No - 1,
                role_code=["ADM", "SAD"],
                module_code=["ALLM", "MBSH"],
                submodule_code=["ALLS", "MBRS"],
                access_type=["ED", "VW", "CR"],
            )
            # fetch member churches
            member_churches = (
                self.db.execute(
                    text(
                        """
                        SELECT MC.Member_Code, M.First_Name, M.Middle_Name, M.Last_Name, MC.Branch_Code, C.Name AS Church_Name, C.Level_Code, MC.Join_Date, MC.Join_Reason, MC.Join_Note, MC.Is_Active, MC.Exit_Date, MC.Exit_Note, MC.Exit_Reason, MC.HeadChurch_Code
                        FROM tblMemberBranch MC
                        LEFT JOIN tblMember M ON M.Code = MC.Member_Code
                        LEFT JOIN tblChurches C ON C.Code = MC.Branch_Code
                        WHERE MC.Member_Code = :Member_Code AND MC.HeadChurch_Code = :HeadChurch_Code;
                        ORDER BY MC.Join_Date;
                        """
                    ),
                    dict(
                        Member_Code=member_code,
                        HeadChurch_Code=self.current_user.HeadChurch_Code,
                    ),
                ).all()
                if is_active is None
                else self.db.execute(
                    text(
                        """
                        SELECT MC.Member_Code, M.First_Name, M.Middle_Name, M.Last_Name, MC.Branch_Code, C.Name, C.Level_Code, MC.Join_Date, MC.Join_Reason, MC.Join_Note, MC.Is_Active, MC.Exit_Date, MC.Exit_Note, MC.Exit_Reason, MC.HeadChurch_Code
                        FROM tblMemberBranch MC
                        LEFT JOIN tblMember M ON M.Code = MC.Member_Code
                        LEFT JOIN tblChurches C ON C.Code = MC.Branch_Code
                        WHERE MC.Member_Code = :Member_Code AND MC.HeadChurch_Code = :HeadChurch_Code AND MC.Is_Active = :Is_Active;
                        ORDER BY MC.Join_Date;
                        """
                    ),
                    dict(
                        Member_Code=member_code,
                        HeadChurch_Code=self.current_user.HeadChurch_Code,
                        Is_Active=is_active,
                    ),
                ).all()
            )
            return member_churches
        except Exception as err:
            raise err

    async def get_member_church_by_member_code(
        self, member_code: str, church_code: str, is_active: Optional[bool] = None
    ):
        """Get Member Church by Code: accessible to only church admins in the same/higher level/church."""
        try:
            await self.get_member_by_code(member_code)
            await self.church_services.get_church_by_code(church_code)
            level = get_level(church_code, self.current_user.HeadChurch_Code, self.db)
            # set user access
            set_user_access(
                self.current_user_access,
                headchurch_code=self.current_user.HeadChurch_Code,
                church_code=church_code,
                level_no=level.Level_No - 1,
                role_code=["ADM", "SAD"],
                module_code=["ALLM", "MBSH"],
                submodule_code=["ALLS", "MBRS"],
                access_type=["ED", "VW", "CR"],
            )
            # fetch member church
            member_church = (
                self.db.execute(
                    text(
                        """
                        SELECT MC.Member_Code, M.First_Name, M.Middle_Name, M.Last_Name, MC.Branch_Code, C.Name AS Church_Name, C.Level_Code, MC.Join_Date, MC.Join_Reason, MC.Join_Note, MC.Is_Active, MC.Exit_Date, MC.Exit_Note, MC.Exit_Reason, MC.HeadChurch_Code
                        FROM tblMemberBranch MC
                        LEFT JOIN tblMember M ON M.Code = MC.Member_Code
                        LEFT JOIN tblChurches C ON C.Code = MC.Branch_Code
                        WHERE MC.Member_Code = :Member_Code AND MC.Branch_Code = :Branch_Code AND MC.HeadChurch_Code = :HeadChurch_Code;
                        ORDER BY MC.Join_Date;
                        """
                    ),
                    dict(
                        Member_Code=member_code,
                        Branch_Code=church_code,
                        HeadChurch_Code=self.current_user.HeadChurch_Code,
                    ),
                ).first()
                if is_active is None
                else self.db.execute(
                    text(
                        """
                        SELECT MC.Member_Code, M.First_Name, M.Middle_Name, M.Last_Name, MC.Branch_Code, C.Name, C.Level_Code, MC.Join_Date, MC.Join_Reason, MC.Join_Note, MC.Is_Active, MC.Exit_Date, MC.Exit_Note, MC.Exit_Reason, MC.HeadChurch_Code
                        FROM tblMemberBranch MC
                        LEFT JOIN tblMember M ON M.Code = MC.Member_Code
                        LEFT JOIN tblChurches C ON C.Code = MC.Branch_Code
                        WHERE MC.Member_Code = :Member_Code AND MC.Branch_Code = :Church_Code AND MC.HeadChurch_Code = :HeadChurch_Code AND MC.Is_Active = :Is_Active;
                        ORDER BY MC.Join_Date;
                        """
                    ),
                    dict(
                        Member_Code=member_code,
                        Church_Code=church_code,
                        HeadChurch_Code=self.current_user.HeadChurch_Code,
                        Is_Active=is_active,
                    ),
                ).first()
            )
            # if len(member_church) == 0:
            #     raise HTTPException(
            #         status_code=status.HTTP_404_NOT_FOUND,
            #         detail="Member not found in Church Selected",
            #     )
            return member_church
        except Exception as err:
            raise err

    async def exit_member_from_church(
        self, member_code, member_exit: MemberBranchExitIn
    ):
        """Exit Member From Church: accessible to only church admins in the same/higher level/church."""
        try:
            # validate member and church
            member = await self.get_member_by_code(member_code)
            await self.church_services.get_church_by_code(member_exit.Branch_Code)
            await self.get_member_church_by_member_code(
                member.Code,
                member_exit.Branch_Code,
                is_active=True,
            )
            level = get_level(
                member_exit.Branch_Code, self.current_user.HeadChurch_Code, self.db
            )
            # set user access
            set_user_access(
                self.current_user_access,
                headchurch_code=self.current_user.HeadChurch_Code,
                church_code=member_exit.Branch_Code,
                level_no=level.Level_No - 1,
                role_code=["ADM", "SAD"],
                module_code=["ALLM", "MBSH"],
                submodule_code=["ALLS", "MBRS"],
                access_type=["ED"],
            )
            # exit member from church
            self.db.execute(
                text(
                    """
                    UPDATE tblMemberBranch
                    SET Exit_Date = :Exit_Date, Exit_Note = :Exit_Note, Exit_Reason = :Exit_Reason, Is_Active = :Is_Active, Modified_By = :Modified_By
                    WHERE Member_Code = :Member_Code AND Branch_Code = :Branch_Code 
                        AND HeadChurch_Code = :HeadChurch_Code AND Is_Active = :Is_Active2;
                    """
                ),
                dict(
                    Exit_Date=(
                        member_exit.Exit_Date
                        if member_exit.Exit_Date
                        else datetime.now()
                    ),
                    Exit_Note=member_exit.Exit_Note,
                    Exit_Reason=member_exit.Exit_Reason,
                    Modified_By=self.current_user.Usercode,
                    Member_Code=member.Code,
                    Branch_Code=member_exit.Branch_Code,
                    HeadChurch_Code=self.current_user.HeadChurch_Code,
                    Is_Active=0,
                    Is_Active2=1,
                ),
            )
            self.db.commit()
            member = await self.get_member_church_by_member_code(
                member_exit.Member_Code, member_exit.Branch_Code
            )
            return member
        except Exception as err:
            self.db.rollback()
            raise err

    async def exit_member_from_all_churches(self, member_code: str):
        """Exit Member From All Churches: accessible to only church admins in higher level/church."""
        try:
            # validate member
            await self.get_member_by_code(member_code)
            # set user access
            set_user_access(
                self.current_user_access,
                headchurch_code=self.current_user.HeadChurch_Code,
                level_no=1,
                role_code=["ADM", "SAD"],
                module_code=["ALLM", "MBSH"],
                submodule_code=["ALLS", "MBRS"],
                access_type=["ED"],
            )
            # exit member from all churches
            self.db.execute(
                text(
                    """
                    UPDATE tblMemberBranch
                    SET Exit_Date = :Exit_Date, Exit_Note = :Exit_Note, Exit_Reason = :Exit_Reason, Is_Active = :Is_Active, Modified_By = :Modified_By
                    WHERE Member_Code = :Member_Code AND HeadChurch_Code = :HeadChurch_Code AND Is_Active = :Is_Active2;
                    """
                ),
                dict(
                    Exit_Date=datetime.now(),
                    Exit_Note="Member exited from all churches",
                    Exit_Reason="OTH",
                    Modified_By=self.current_user.Usercode,
                    Member_Code=member_code,
                    HeadChurch_Code=self.current_user.HeadChurch_Code,
                    Is_Active=0,
                    Is_Active2=1,
                ),
            )
            self.db.commit()
            member = await self.get_member_by_code(member_code)
            return member
        except Exception as err:
            self.db.rollback()
            raise err

    async def join_member_to_church(self, member_code, member_join: MemberBranchJoinIn):
        """Join Member To Church: accessible to only church admins in the same/higher level/church."""
        try:
            # validate member and church
            member = await self.get_member_by_code(member_code)
            await self.church_services.get_church_by_code(member_join.Branch_Code)
            member_church = await self.get_member_all_churches_by_code(
                member_code, is_active=True
            )
            level = get_level(
                member_join.Branch_Code, self.current_user.HeadChurch_Code, self.db
            )
            # set user access
            set_user_access(
                self.current_user_access,
                headchurch_code=self.current_user.HeadChurch_Code,
                church_code=member_join.Branch_Code,
                level_no=level.Level_No - 1,
                role_code=["ADM", "SAD"],
                module_code=["ALLM", "MBSH"],
                submodule_code=["ALLS", "MBRS"],
                access_type=["ED"],
            )
            # checks if member is already a member of a church
            if member_church:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Member is already a member of a church",
                )
            # check and exit member from possible member church
            await self.exit_member_from_all_churches(member.Code)
            # join member to church
            self.db.execute(
                text(
                    """
                    INSERT INTO tblMemberBranch
                    (Member_Code, Branch_Code, Level_Code, HeadChurch_Code, Join_Date, Join_Reason, Join_Note, Is_Active, Created_By)
                    VALUES
                    (:Member_Code, :Branch_Code, :Level_Code, :HeadChurch_Code, :Join_Date, :Join_Reason, :Join_Note, :Is_Active, :Created_By);
                    """
                ),
                dict(
                    Member_Code=member.Code,
                    Branch_Code=member_join.Branch_Code,
                    HeadChurch_Code=self.current_user.HeadChurch_Code,
                    Join_Date=(
                        member_join.Join_Date
                        if member_join.Join_Date
                        else datetime.now()
                    ),
                    Join_Reason=member_join.Join_Reason,
                    Join_Note=member_join.Join_Note,
                    Is_Active=1,
                    Created_By=self.current_user.Usercode,
                ),
            )
            self.db.commit()
            member_church = await self.get_member_church_by_member_code(
                member.Code, member_join.Branch_Code, is_active=True
            )
            return member_church
        except Exception as err:
            self.db.rollback()
            raise err


def get_member_services(
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
    current_user_access: Annotated[UserAccess, Depends(get_current_user_access)],
    church_services: Annotated[ChurchServices, Depends(get_church_services)],
    db_current_user: Annotated[str, Depends(set_db_current_user)],
):
    return MemberServices(db, current_user, current_user_access, church_services)
