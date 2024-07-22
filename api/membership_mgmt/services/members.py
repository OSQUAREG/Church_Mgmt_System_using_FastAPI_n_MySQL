from datetime import datetime
from typing import Annotated, Optional

from fastapi import Depends, HTTPException, status  # type: ignore
from sqlalchemy import text  # type: ignore
from sqlalchemy.orm import Session  # type: ignore

from ...authentication.models.auth import User, UserAccess
from ...church_admin.services.church_leads import church_recursive_cte
from ...church_admin.services import get_church_services, ChurchServices
from ...membership_mgmt.models.members import (
    MemberBranchExitIn,
    MemberBranchJoinIn,
    MemberBranchUpdate,
    MemberIn,
    MemberUpdate,
)
from ...common.database import get_db
from ...common.utils import (
    check_duplicate_entry,
    validate_code_type,
    get_level,
    set_user_access,
)
from ...common.dependencies import (
    get_current_user,
    get_current_user_access,
    set_db_current_user,
)


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

    - Get Member Current Branch
    - Get Member-Branch by Code
    - Get Member All Branches
    - Get Member Church Hierarchy by Member Code
    - Exit Member From All Churches
    - Exit Memeber From Church
    - Join Member To Church
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
            # get level
            level = get_level(
                new_member.Branch_Code, self.current_user.Head_Code, self.db
            )
            # set user access
            set_user_access(
                self.current_user_access,
                head_code=self.current_user.Head_Code,
                church_code=new_member.Branch_Code,
                level_no=level.Level_No - 1,
                role_code=["ADM", "SAD"],
                module_code=["ALLM", "MBSH"],
                submodule_code=["ALLS", "MBRS"],
                access_type=["CR"],
            )
            # check gender, member type, marital status, employment status, join reason codes
            validate_code_type(new_member.Gender, "Gender", self.db)
            validate_code_type(new_member.Marital_Status, "Marital Status", self.db)
            validate_code_type(new_member.Employ_Status, "Employment Status", self.db)
            validate_code_type(new_member.Type, "Member Type", self.db)
            validate_code_type(new_member.Join_Code, "Exit/Join Reason", self.db)
            # check duplicate entry
            check_duplicate_entry(
                self.db,
                self.current_user.Head_Code,
                "tblMember",
                "Personal_Contact_No",
                new_member.Personal_Contact_No,
            )
            check_duplicate_entry(
                self.db,
                self.current_user.Head_Code,
                "tblMember",
                "Personal_Email",
                new_member.Personal_Email,
            )
            # insert new member
            self.db.execute(
                text(
                    """
                    INSERT INTO tblMember
                        (First_Name, Middle_Name, Last_Name, Title, Title2, Family_Name, Is_FamilyHead, Home_Address, Date_of_Birth, Gender, Marital_Status, Employ_Status, Occupation, Office_Address, State_of_Origin, Country_of_Origin, Personal_Contact_No, Contact_No, Contact_No2, Personal_Email, Contact_Email, Contact_Email2, Town_Code, State_Code, Region_Code, Country_Code, `Type`, Is_Clergy, Head_Code, Created_By)
                    VALUES
                        (:First_Name, :Middle_Name, :Last_Name, :Title, :Title2, :Family_Name, :Is_FamilyHead, :Home_Address, :Date_of_Birth, :Gender, :Marital_Status, :Employ_Status, :Occupation, :Office_Address, :State_of_Origin, :Country_of_Origin, :Personal_Contact_No, :Contact_No, :Contact_No2, :Personal_Email, :Contact_Email, :Contact_Email2, :Town_Code, :State_Code, :Region_Code, :Country_Code, :Type, :Is_Clergy, :Head_Code, :Created_By);
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
                    Head_Code=self.current_user.Head_Code,
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
                    (Member_Code, Branch_Code, Join_Date, Join_Code, Join_Note, Head_Code, Created_By)
                VALUES
                    (:Member_Code, :Branch_Code, :Join_Date, :Join_Code, :Join_Note, :Head_Code, :Created_By);
                """
                ),
                dict(
                    Member_Code=new_code.Code,
                    Branch_Code=new_member.Branch_Code,
                    Join_Date=new_member.Join_Date,
                    Join_Code=new_member.Join_Code,
                    Join_Note=new_member.Join_Note,
                    Head_Code=self.current_user.Head_Code,
                    Created_By=self.current_user.Usercode,
                ),
            )
            self.db.commit()
            return await self.get_member_by_code_id(new_code.Code)
        except Exception as err:
            self.db.rollback()
            raise err

    async def get_all_members(self, is_active: Optional[bool] = None):
        """Get All Members: accessible to only head church admins and super-admins."""
        try:
            # set user access
            set_user_access(
                self.current_user_access,
                head_code=self.current_user.Head_Code,
                level_code=["CHU"],
                role_code=["ADM", "SAD"],
                module_code=["ALLM", "MBSH"],
                submodule_code=["ALLS", "MBRS"],
                access_type=["VW"],
            )
            members = (
                self.db.execute(
                    text(
                        """
                        SELECT M.* , MC.Branch_Code, MC.Join_Date, MC.Join_Code, MC.Join_Note FROM tblMember M
                        LEFT JOIN tblMemberBranch MC ON MC.Member_Code = M.Code
                        WHERE M.Head_Code = :Head_Code
                        ORDER BY `Code`;
                        """
                    ),
                    dict(Head_Code=self.current_user.Head_Code),
                ).all()
                if is_active is None
                else self.db.execute(
                    text(
                        """
                        SELECT M.* , MC.Branch_Code, MC.Join_Date, MC.Join_Code, MC.Join_Note FROM tblMember M
                        LEFT JOIN tblMemberBranch MC ON MC.Member_Code = M.Code
                        WHERE M.Head_Code = :Head_Code AND M.Is_Active = :Is_Active AND MC.Is_Active = :Is_Active
                        ORDER BY `Code`;
                        """
                    ),
                    dict(
                        Head_Code=self.current_user.Head_Code,
                        Is_Active=is_active,
                    ),
                ).all()
            )
            return members
        except Exception as err:
            raise err

    async def get_member_by_code_id(self, member_code_id: str):
        """Get Member By Code: accessible to church admins and executives of same/higher level/church."""
        try:
            # fetch member data
            member = self.db.execute(
                text(
                    """
                    SELECT M.* , MC.Branch_Code, MC.Join_Date, MC.Join_Code, MC.Join_Note, MC.Exit_Date, MC.Exit_Code, MC.Exit_Note
                    FROM tblMember M
                    LEFT JOIN tblMemberBranch MC ON MC.Member_Code = M.Code AND MC.Is_Active = :Is_Active
                    WHERE (M.Code = :Code or M.Id = :Id) AND M.Head_Code = :Head_Code
                    """
                ),
                dict(
                    Code=member_code_id,
                    Id=member_code_id,
                    Head_Code=self.current_user.Head_Code,
                    Is_Active=1,
                ),
            ).first()
            # # get level
            # level = get_level(
            #     member.Branch_Code, self.current_user.Head_Code, self.db
            # ) if member.Branch_Code is not None else 0
            # set user access
            set_user_access(
                self.current_user_access,
                head_code=self.current_user.Head_Code,
                # church_code=member.Branch_Code,
                # level_no=level.Level_No - 1,
                role_code=["ADM", "SAD", "EXC"],
                module_code=["ALLM", "MBSH"],
                submodule_code=["ALLS", "MBRS"],
                access_type=["VW", "ED", "CR"],
            )
            # check if member exists
            if member is None:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Member not found or inactive",
                )
            return member
        except Exception as err:
            raise err

    async def get_current_user_member(self):
        """Get Current User Member: accessible to only the current logged in member."""
        try:
            member = self.db.execute(
                text(
                    """
                    SELECT M.* , MC.Branch_Code, MC.Join_Date, MC.Join_Code, MC.Join_Note 
                    FROM tblMember M
                    LEFT JOIN tblMemberBranch MC ON MC.Member_Code = M.Code
                    WHERE `Code` = :Code AND M.Head_Code = :Head_Code AND M.Is_Active = :Is_Active AND MC.Is_Active = :Is_Active;
                    """
                ),
                dict(
                    Code=self.current_user.Usercode,
                    Head_Code=self.current_user.Head_Code,
                    Is_Active=1,
                ),
            ).first()
            if member is None:
                return None
                # else:
                #     raise HTTPException(
                #         status_code=status.HTTP_404_NOT_FOUND,
                #         detail="Member not found or inactive",
                #     )
            return member
        except Exception as err:
            raise err

    async def get_members_by_church(self, church_code: str):
        """Get Members By Church: accessible to only church admins and executives of same/higher level/church"""
        try:
            level = get_level(church_code, self.current_user.Head_Code, self.db)
            # set user access
            set_user_access(
                self.current_user_access,
                head_code=self.current_user.Head_Code,
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
                        SELECT M.* , MC.Branch_Code, MC.Join_Date, MC.Join_Code, MC.Join_Note 
                        FROM tblMember M
                            LEFT JOIN tblMemberBranch MC ON MC.Member_Code = M.Code
                        WHERE M.Head_Code = :Head_Code 
                            AND M.Is_Active = :Is_Active AND MC.Is_Active = :Is_Active
                            AND MC.Branch_Code = :Church_Code;
                        """
                    ),
                    dict(
                        Church_Code=church_code.upper(),
                        Head_Code=self.current_user.Head_Code,
                        Is_Active=1,
                    ),
                ).all()
                if level.Level_No == 8  # if church is a branch
                else self.db.execute(
                    text(
                        f"""
                        {church_recursive_cte}
                        SELECT M.* , MC.Branch_Code, MC.Join_Date, MC.Join_Code, MC.Join_Note FROM tblMember M
                            LEFT JOIN tblMemberBranch MC ON MC.Member_Code = M.Code
                        WHERE M.Head_Code = :Head_Code 
                            AND M.Is_Active = :Is_Active AND MC.Is_Active = :Is_Active
                            AND MC.Branch_Code IN (
                                SELECT Church FROM ChurchHierarchy
                                WHERE Church_Level = 'BRN'
                            );
                        """
                    ),
                    dict(
                        Church_Code=church_code.upper(),
                        Head_Code=self.current_user.Head_Code,
                        Is_Active=1,
                    ),
                ).all()
            )
            return members
        except Exception as err:
            raise err

    async def update_member_by_code_id(self, member_code_id: str, member: MemberUpdate):
        """Update Member By Code: accessible to only the admins and executives of same/higher level/church."""
        try:
            # fetch member data
            old_member = await self.get_member_by_code_id(member_code_id)
            # get church level
            level_no = get_level(
                old_member.Branch_Code, self.current_user.Head_Code, self.db
            )
            # set user access
            set_user_access(
                self.current_user_access,
                head_code=self.current_user.Head_Code,
                church_code=old_member.Branch_Code,
                level_no=level_no.Level_No - 1,
                role_code=["ADM", "SAD", "EXC"],
                module_code=["ALLM", "MBSH"],
                submodule_code=["ALLS", "MBRS"],
                access_type=["ED"],
            )
            # check gender, member type, marital status, employment status, join reason codes
            validate_code_type(member.Gender, "Gender", self.db)
            validate_code_type(member.Marital_Status, "Marital Status", self.db)
            validate_code_type(member.Employ_Status, "Employment Status", self.db)
            validate_code_type(member.Type, "Member Type", self.db)
            # check duplicate entry
            check_duplicate_entry(
                self.db,
                self.current_user.Head_Code,
                "tblMember",
                "Personal_Contact_No",
                member.Personal_Contact_No,
                old_member.Personal_Contact_No,
            )
            check_duplicate_entry(
                self.db,
                self.current_user.Head_Code,
                "tblMember",
                "Personal_Email",
                member.Personal_Email,
                old_member.Personal_Email,
            )
            # update member
            self.db.execute(
                text(
                    """
                    UPDATE tblMember 
                    SET 
                        First_Name = :First_Name, Last_Name = :Last_Name, Middle_Name = :Middle_Name, Title = :Title, Title2 = :Title2, Family_Name = :Family_Name, Is_FamilyHead = :Is_FamilyHead, Home_Address = :Home_Address, Date_of_Birth = :Date_of_Birth, Gender = :Gender, Marital_Status = :Marital_Status, Employ_Status = :Employ_Status, Occupation = :Occupation, Office_Address = :Office_Address, State_of_Origin = :State_of_Origin, Personal_Contact_No = :Personal_Contact_No, Contact_No = :Contact_No, Contact_No2 = :Contact_No2, Personal_Email = :Personal_Email, Contact_Email = :Contact_Email, Contact_Email2 = :Contact_Email2, Town_Code = :Town_Code, State_Code = :State_Code, Region_Code = :Region_Code, Country_Code = :Country_Code, `Type` = :Type, Is_Clergy = :Is_Clergy, Modified_By = :Modified_By
                    WHERE (`Code` = :Code OR Id = :Id) AND Head_Code = :Head_Code;
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
                        if member.Is_FamilyHead is not None
                        else old_member.Is_FamilyHead
                    ),  # type: ignore
                    Home_Address=(
                        member.Home_Address
                        if member.Home_Address
                        else old_member.Home_Address
                    ),
                    Date_of_Birth=(
                        member.Date_of_Birth
                        if member.Date_of_Birth
                        else old_member.Date_of_Birth
                    ),  # type: ignore
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
                        member.Is_Clergy
                        if member.Is_Clergy is not None
                        else old_member.Is_Clergy
                    ),
                    Modified_By=self.current_user.Usercode,
                    Head_Code=self.current_user.Head_Code,
                    Code=member_code_id,
                    Id=member_code_id,
                ),
            )
            self.db.commit()
            return await self.get_member_by_code_id(member_code_id)
        except Exception as err:
            self.db.rollback()
            raise err

    async def update_current_user_member(self, member: MemberUpdate):
        """Update Current User Member: accessible to only the current logged in member."""
        try:
            member_code = self.current_user.Usercode
            # fetch member data
            old_member = await self.get_member_by_code_id(member_code)
            if not old_member:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Current user not a church member.",
                )
            # check gender, member type, marital status, employment status, join reason codes
            validate_code_type(member.Gender, "Gender", self.db)
            validate_code_type(member.Marital_Status, "Marital Status", self.db)
            validate_code_type(member.Employ_Status, "Employment Status", self.db)
            validate_code_type(member.Type, "Member Type", self.db)
            # check duplicate entry
            check_duplicate_entry(
                self.db,
                self.current_user.Head_Code,
                "tblMember",
                "Personal_Contact_No",
                member.Personal_Contact_No,
                old_member.Personal_Contact_No,
            )
            check_duplicate_entry(
                self.db,
                self.current_user.Head_Code,
                "tblMember",
                "Personal_Email",
                member.Personal_Email,
                old_member.Personal_Email,
            )
            # update member
            self.db.execute(
                text(
                    """
                    UPDATE tblMember 
                    SET First_Name = :First_Name, Last_Name = :Last_Name, Middle_Name = :Middle_Name, Title = :Title, Title2 = :Title2, Family_Name = :Family_Name, Is_FamilyHead = :Is_FamilyHead, Home_Address = :Home_Address, Date_of_Birth = :Date_of_Birth, Gender = :Gender, Marital_Status = :Marital_Status, Employ_Status = :Employ_Status, Occupation = :Occupation, Office_Address = :Office_Address, State_of_Origin = :State_of_Origin, Personal_Contact_No = :Personal_Contact_No, Contact_No = :Contact_No, Contact_No2 = :Contact_No2, Personal_Email = :Personal_Email, Contact_Email = :Contact_Email, Contact_Email2 = :Contact_Email2, Town_Code = :Town_Code, State_Code = :State_Code, Region_Code = :Region_Code, Country_Code = :Country_Code, Modified_By = :Modified_By
                    WHERE `Code` = :Code AND Head_Code = :Head_Code;
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
                        if member.Is_FamilyHead is not None
                        else old_member.Is_FamilyHead
                    ),  # type: ignore
                    Home_Address=(
                        member.Home_Address
                        if member.Home_Address
                        else old_member.Home_Address
                    ),
                    Date_of_Birth=(
                        member.Date_of_Birth
                        if member.Date_of_Birth
                        else old_member.Date_of_Birth
                    ),  # type: ignore
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
                    Modified_By=self.current_user.Usercode,
                    Head_Code=self.current_user.Head_Code,
                    Code=member_code,
                ),
            )
            self.db.commit()
            return await self.get_current_user_member()
        except Exception as err:
            self.db.rollback()
            raise err

    async def deactivate_member_by_code(self, member_code):
        """Deactivate Member by Code: accessible to only church admins in the same/higher level/church."""
        try:
            member = await self.get_member_by_code_id(member_code)
            level = get_level("BRN", self.current_user.Head_Code, self.db)
            # set user access
            set_user_access(
                self.current_user_access,
                head_code=self.current_user.Head_Code,
                church_code=member.Branch_Code,
                level_no=level.Level_No - 1,
                role_code=["ADM", "SAD"],
                module_code=["ALLM", "MBSH"],
                submodule_code=["ALLS", "MBRS"],
                access_type=["ED"],
            )
            # checks if member is inactive
            if member.Is_Active != 1:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Member is already deactivated",
                )
            # deactivate member
            self.db.execute(
                text(
                    """
                    UPDATE tblMember
                    SET Is_Active = :Is_Active
                    WHERE `Code` = :Code AND Head_Code = :Head_Code AND Is_Active = :Is_Active2;
                    """
                ),
                dict(
                    Is_Active=0,
                    Code=member.Code,
                    Head_Code=self.current_user.Head_Code,
                    Is_Active2=1,
                ),
            )
            self.db.commit()
            # deactivate member church
            await self.exit_member_from_all_branches(member.Code)
            return await self.get_member_by_code_id(member.Code)
        except Exception as err:
            self.db.rollback()
            raise err

    async def activate_member_by_code(
        self, member_code, member_church: MemberBranchJoinIn
    ):
        """Activate Member by Code: accessible to only church admins in the same/higher level/church."""
        try:
            member = await self.get_member_by_code_id(member_code)
            level = get_level(member.Branch_Code, self.current_user.Head_Code, self.db)
            # set user access
            set_user_access(
                self.current_user_access,
                head_code=self.current_user.Head_Code,
                church_code=member.Branch_Code,
                level_no=level.Level_No - 1,
                role_code=["ADM", "SAD"],
                module_code=["ALLM", "MBSH"],
                submodule_code=["ALLS", "MBRS"],
                access_type=["ED"],
            )
            # check join type
            if member_church.Join_Code:
                validate_code_type(member_church.Join_Code, "Exit/Join Reason", self.db)
            # check if member is active
            if member.Is_Active == 1:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Member is already activated.",
                )
            # activate member
            self.db.execute(
                text(
                    """
                    UPDATE tblMember
                    SET Is_Active = :Is_Active
                    WHERE `Code` = :Code AND Head_Code = :Head_Code AND Is_Active = :Is_Active2;
                    """
                ),
                dict(
                    Is_Active=1,
                    Code=member.Code,
                    Head_Code=self.current_user.Head_Code,
                    Is_Active2=0,
                ),
            )
            self.db.commit()
            # insert new member church
            self.db.execute(
                text(
                    """
                    INSERT INTO tblMemberBranch
                    (Member_Code, Branch_Code, Join_Date, Join_Note, Join_Code, Head_Code)
                    VALUES
                    (:Member_Code, :Branch_Code, :Join_Date, :Join_Note, :Join_Code, :Head_Code);
                    """
                ),
                dict(
                    Member_Code=member.Code,
                    Branch_Code=member_church.Branch_Code,
                    Join_Date=member_church.Join_Date,
                    Join_Note=member_church.Join_Note,
                    Join_Code=member_church.Join_Code,
                    Head_Code=self.current_user.Head_Code,
                ),
            )
            self.db.commit()
            return await self.get_member_by_code_id(member.Code)
        except Exception as err:
            self.db.rollback()
            raise err

    async def promote_member_to_clergy(self, member_code_id):
        try:
            member = await self.get_member_by_code_id(member_code_id)
            # set user access
            set_user_access(
                self.current_user_access,
                head_code=self.current_user.Head_Code,
                level_no=0,
                role_code=["ADM", "SAD"],
                module_code=["ALLM", "MBSH"],
                submodule_code=["ALLS", "MBRS"],
                access_type=["ED"],
            )
            # check if member is active
            if member.Is_Active != 1:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Member is deactivated",
                )
            # promote member
            self.db.execute(
                text(
                    """
                    UPDATE tblMember
                    SET Is_Clergy = :Is_Clergy
                    WHERE `Code` = :Code AND Head_Code = :Head_Code 
                        AND Is_Active = :Is_Active AND Is_Clergy = :Is_Clergy2;
                    """
                ),
                dict(
                    Is_Clergy=1,
                    Code=member.Code,
                    Head_Code=self.current_user.Head_Code,
                    Is_Active=1,
                    Is_Clergy2=0,
                ),
            )
            self.db.commit()
            return await self.get_member_by_code_id(member.Code)
        except Exception as err:
            self.db.rollback()
            raise err

    async def demote_member_from_clergy(self, member_code_id):
        try:
            member = await self.get_member_by_code_id(member_code_id)
            # set user access
            set_user_access(
                self.current_user_access,
                head_code=self.current_user.Head_Code,
                level_no=0,
                role_code=["ADM", "SAD"],
                module_code=["ALLM", "MBSH"],
                submodule_code=["ALLS", "MBRS"],
                access_type=["ED"],
            )
            # demote member
            self.db.execute(
                text(
                    """
                    UPDATE tblMember
                    SET Is_Clergy = :Is_Clergy
                    WHERE `Code` = :Code AND Head_Code = :Head_Code 
                        AND Is_Active = :Is_Active AND Is_Clergy = :Is_Clergy2;
                    """
                ),
                dict(
                    Is_Clergy=0,
                    Code=member.Code,
                    Head_Code=self.current_user.Head_Code,
                    Is_Active=1,
                    Is_Clergy2=1,
                ),
            )
            self.db.commit()
            return await self.get_member_by_code_id(member.Code)
        except Exception as err:
            self.db.rollback()
            raise err

    async def get_member_branches(
        self,
        member_code: str,
        branch_code: Optional[str] = None,
        is_active: Optional[bool] = None,
    ):
        """Get Member Branches: accessible to only church admins in the same/higher level/church."""
        try:
            member = await self.get_member_by_code_id(member_code)
            level = get_level("BRN", self.current_user.Head_Code, self.db)

            # set user access
            set_user_access(
                self.current_user_access,
                head_code=self.current_user.Head_Code,
                church_code=member.Branch_Code,
                level_no=level.Level_No - 1,
                role_code=["ADM", "SAD"],
                module_code=["ALLM", "MBSH"],
                submodule_code=["ALLS", "MBRS"],
                access_type=["ED", "VW", "CR"],
            )
            # fetch member churches
            if is_active is not None:
                if is_active == 1:
                    if branch_code:
                        msg = "returns current specific member-branch or none if branch is not the current"
                    else:
                        msg = "returns current member-branch"
                else:
                    if branch_code:
                        msg = "returns previous specific member-branches"
                    else:
                        msg = "returns previous member-branches"
            else:
                if branch_code:
                    msg = "returns all specific member-branches"
                else:
                    msg = "returns all member-branches"

            print(f"msg: {msg}")

            if is_active is not None:
                if branch_code:
                    member_branches = self.db.execute(
                        text(
                            """
                            SELECT
                                MC.*, M.Title, M.Title2, M.First_Name, M.Middle_Name, M.Last_Name, C.Name AS Branch_Name
                            FROM tblMemberBranch MC
                                LEFT JOIN tblMember M ON M.Code = MC.Member_Code
                                LEFT JOIN tblChurches C ON C.Code = MC.Branch_Code
                            WHERE MC.Member_Code = :Member_Code AND MC.Head_Code = :Head_Code
                                AND MC.Branch_Code = :Branch_Code AND MC.Is_Active = :Is_Active
                            ORDER BY MC.Join_Date;
                            """
                        ),
                        dict(
                            Member_Code=member_code,
                            Head_Code=self.current_user.Head_Code,
                            Is_Active=is_active,
                            Branch_Code=branch_code,
                        ),
                    ).all()
                else:
                    member_branches = self.db.execute(
                        text(
                            """
                        SELECT
                            MC.*, M.Title, M.Title2, M.First_Name, M.Middle_Name, M.Last_Name, C.Name AS Branch_Name
                        FROM tblMemberBranch MC
                            LEFT JOIN tblMember M ON M.Code = MC.Member_Code
                            LEFT JOIN tblChurches C ON C.Code = MC.Branch_Code
                        WHERE MC.Member_Code = :Member_Code AND MC.Head_Code = :Head_Code
                            AND MC.Is_Active = :Is_Active
                        ORDER BY MC.Join_Date;
                        """
                        ),
                        dict(
                            Member_Code=member_code,
                            Head_Code=self.current_user.Head_Code,
                            Is_Active=is_active,
                        ),
                    ).all()
            else:
                if branch_code:
                    member_branches = self.db.execute(
                        text(
                            """
                            SELECT
                                MC.*, M.Title, M.Title2, M.First_Name, M.Middle_Name, M.Last_Name, C.Name AS Branch_Name
                            FROM tblMemberBranch MC
                                LEFT JOIN tblMember M ON M.Code = MC.Member_Code
                                LEFT JOIN tblChurches C ON C.Code = MC.Branch_Code
                            WHERE MC.Member_Code = :Member_Code AND MC.Head_Code = :Head_Code
                                AND MC.Branch_Code = :Branch_Code
                            ORDER BY MC.Join_Date;
                            """
                        ),
                        dict(
                            Member_Code=member_code,
                            Head_Code=self.current_user.Head_Code,
                            Branch_Code=branch_code,
                        ),
                    ).all()
                else:
                    member_branches = self.db.execute(
                        text(
                            """
                        SELECT
                            MC.*, M.Title, M.Title2, M.First_Name, M.Middle_Name, M.Last_Name, C.Name AS Branch_Name
                        FROM tblMemberBranch MC
                            LEFT JOIN tblMember M ON M.Code = MC.Member_Code
                            LEFT JOIN tblChurches C ON C.Code = MC.Branch_Code
                        WHERE MC.Member_Code = :Member_Code AND MC.Head_Code = :Head_Code
                        ORDER BY MC.Join_Date;
                        """
                        ),
                        dict(
                            Member_Code=member_code,
                            Head_Code=self.current_user.Head_Code,
                        ),
                    ).all()
            # if not member_branches:
            #     raise HTTPException(
            #         status_code=status.HTTP_404_NOT_FOUND,
            #         detail=(
            #             "No"
            #             + (
            #                 (" current" if is_active == 1 else " previous")
            #                 if is_active is not None
            #                 else ""
            #             )
            #             + f" Member-Branch"
            #             + (" " if branch_code is None else f" '{branch_code.upper()}'")
            #             + f" records found for member: '{member_code.upper()}'."
            #         ),
            #     )
            return member_branches
        except Exception as err:
            raise err

    async def get_member_branch_by_id(self, member_branch_id):
        try:
            member_branch = self.db.execute(
                text(
                    """
                    SELECT
                        MC.*, M.Title, M.Title2, M.First_Name, M.Middle_Name, M.Last_Name, C.Name AS Branch_Name
                    FROM tblMemberBranch MC
                        LEFT JOIN tblMember M ON M.Code = MC.Member_Code
                        LEFT JOIN tblChurches C ON C.Code = MC.Branch_Code
                    WHERE MC.Id = :Id;
                    """
                ),
                dict(Id=member_branch_id),
            ).first()
            return member_branch
        except Exception as err:
            raise err

    async def exit_member_from_branch(
        self, member_code, member_exit: MemberBranchExitIn
    ):
        """Exit Member From Church: accessible to only church admins in the same/higher level/church."""
        try:
            level = get_level(
                member_exit.Branch_Code, self.current_user.Head_Code, self.db
            )
            # set user access
            set_user_access(
                self.current_user_access,
                head_code=self.current_user.Head_Code,
                church_code=member_exit.Branch_Code,
                level_no=level.Level_No - 1,
                role_code=["ADM", "SAD"],
                module_code=["ALLM", "MBSH"],
                submodule_code=["ALLS", "MBRS"],
                access_type=["ED"],
            )
            # validate member and church
            member = await self.get_member_by_code_id(member_code)
            await self.church_services.get_church_by_id_code(member_exit.Branch_Code)
            await self.get_member_branches(member.Code, member_exit.Branch_Code, True)
            # check if member is already a member of the same branch
            if member.Branch_Code != member_exit.Branch_Code:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Member is not a member of the selected branch",
                )
            member_branch = await self.get_member_branches(member_code, is_active=True)
            # checks if member is already a member of a church
            if not member_branch:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Member is not a member of any branch.",
                )
            # exit member from church
            self.db.execute(
                text(
                    """
                    UPDATE tblMemberBranch
                    SET Exit_Date = :Exit_Date, Exit_Note = :Exit_Note, Exit_Code = :Exit_Code, Is_Active = :Is_Active, Modified_By = :Modified_By
                    WHERE Member_Code = :Member_Code AND Branch_Code = :Branch_Code
                        AND Head_Code = :Head_Code AND Is_Active = :Is_Active2;
                    """
                ),
                dict(
                    Exit_Date=(
                        member_exit.Exit_Date
                        if member_exit.Exit_Date
                        else datetime.now()
                    ),
                    Exit_Note=member_exit.Exit_Note,
                    Exit_Code=member_exit.Exit_Code,
                    Modified_By=self.current_user.Usercode,
                    Member_Code=member.Code,
                    Branch_Code=member_exit.Branch_Code,
                    Head_Code=self.current_user.Head_Code,
                    Is_Active=0,
                    Is_Active2=1,
                ),
            )
            self.db.commit()
            return await self.get_member_branches(member.Code, member_exit.Branch_Code)
        except Exception as err:
            self.db.rollback()
            raise err

    async def exit_member_from_all_branches(self, member_code: str):
        """Exit Member From All Churches: accessible to only church admins in higher level/church."""
        try:
            # validate member
            member = await self.get_member_by_code_id(member_code)
            # set user access
            set_user_access(
                self.current_user_access,
                head_code=self.current_user.Head_Code,
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
                    SET Exit_Date = :Exit_Date, Exit_Note = :Exit_Note, Exit_Code = :Exit_Code, Is_Active = :Is_Active, Modified_By = :Modified_By
                    WHERE Member_Code = :Member_Code AND Head_Code = :Head_Code AND Is_Active = :Is_Active2;
                    """
                ),
                dict(
                    Exit_Date=datetime.now(),
                    Exit_Note="Member exited from all churches",
                    Exit_Code="OTH",
                    Modified_By=self.current_user.Usercode,
                    Member_Code=member_code,
                    Head_Code=self.current_user.Head_Code,
                    Is_Active=0,
                    Is_Active2=1,
                ),
            )
            self.db.commit()
            return await self.get_member_branches(member.Code, member.Branch_Code)
            return member
        except Exception as err:
            self.db.rollback()
            raise err

    async def join_member_to_branch(self, member_code, member_join: MemberBranchJoinIn):
        """Join Member To Church: accessible to only church admins in the same/higher level/church."""
        try:
            level = get_level(
                member_join.Branch_Code, self.current_user.Head_Code, self.db
            )
            # set user access
            set_user_access(
                self.current_user_access,
                head_code=self.current_user.Head_Code,
                church_code=member_join.Branch_Code,
                level_no=level.Level_No - 1,
                role_code=["ADM", "SAD"],
                module_code=["ALLM", "MBSH"],
                submodule_code=["ALLS", "MBRS"],
                access_type=["ED"],
            )
            # validate member and church
            member = await self.get_member_by_code_id(member_code)
            await self.church_services.get_church_by_id_code(member_join.Branch_Code)
            # check if member is already a member of the same branch
            if member.Branch_Code == member_join.Branch_Code:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Member is already a member of the same branch",
                )
            member_branch = await self.get_member_branches(member_code, is_active=True)
            # checks if member is already a member of a church
            if member_branch:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Member is already a member of a branch. Please exit member from all branches first.",
                )
            # # check and exit member from possible member church
            # await self.exit_member_from_all_branches(member.Code)
            # join member to church
            self.db.execute(
                text(
                    """
                    INSERT INTO tblMemberBranch
                    (Member_Code, Branch_Code, Head_Code, Join_Date, Join_Code, Join_Note, Is_Active, Created_By)
                    VALUES
                    (:Member_Code, :Branch_Code, :Head_Code, :Join_Date, :Join_Code, :Join_Note, :Is_Active, :Created_By);
                    """
                ),
                dict(
                    Member_Code=member.Code,
                    Branch_Code=member_join.Branch_Code,
                    Head_Code=self.current_user.Head_Code,
                    Join_Date=(
                        member_join.Join_Date
                        if member_join.Join_Date
                        else datetime.now()
                    ),
                    Join_Code=member_join.Join_Code,
                    Join_Note=member_join.Join_Note,
                    Is_Active=1,
                    Created_By=self.current_user.Usercode,
                ),
            )
            self.db.commit()
            return await self.get_member_branches(
                member.Code, member_join.Branch_Code, True
            )
        except Exception as err:
            self.db.rollback()
            raise err

    async def update_member_branch_reason(
        self, member_branch_id: int, member_branch: MemberBranchUpdate
    ):
        try:
            memb_brn = await self.get_member_branch_by_id(member_branch_id)
            level = get_level(
                memb_brn.Branch_Code, self.current_user.Head_Code, self.db
            )
            branch = await self.church_services.get_church_by_id_code(
                memb_brn.Branch_Code
            )
            # set user access
            set_user_access(
                self.current_user_access,
                head_code=self.current_user.Head_Code,
                church_code=branch.Code,
                level_no=level.Level_No - 1,
                role_code=["ADM", "SAD", "EXC"],
                module_code=["ALLM", "MBSH"],
                submodule_code=["ALLS", "MBRS"],
                access_type=["ED"],
            )
            if memb_brn.Is_Active == 1:
                self.db.execute(
                    text(
                        """
                        UPDATE tblMemberBranch
                        SET Join_Date = :Join_Date, Join_Code = :Join_Code, Join_Note = :Join_Note, Modified_By = :Modified_By
                        WHERE Id = :Id;
                        """
                    ),
                    dict(
                        Join_Date=member_branch.Join_Date,
                        Join_Code=member_branch.Join_Code,
                        Join_Note=member_branch.Join_Note,
                        Modified_By=self.current_user.Usercode,
                        Id=member_branch_id,
                    ),
                )
                self.db.commit()
            else:
                self.db.execute(
                    text(
                        """
                        UPDATE tblMemberBranch
                        SET Join_Code = :Join_Code, Join_Note = :Join_Note, Exit_Date = :Exit_Date, Exit_Note = :Exit_Note, Exit_Code = :Exit_Code, Modified_By = :Modified_By
                        WHERE Id = :Id;
                        """
                    ),
                    dict(
                        Join_Code=member_branch.Join_Code,
                        Join_Note=member_branch.Join_Note,
                        Exit_Date=member_branch.Exit_Date,
                        Exit_Note=member_branch.Exit_Note,
                        Exit_Code=member_branch.Exit_Code,
                        Modified_By=self.current_user.Usercode,
                        Id=member_branch_id,
                    ),
                )
                self.db.commit()
            return await self.get_member_branch_by_id(member_branch_id)
        except Exception as err:
            self.db.rollback()
            raise err

    async def get_member_church_hierarchy_by_member_code(self, member_code: str):
        try:
            member = await self.get_member_by_code_id(member_code)
            # fetch data
            mc_hierarchy = self.db.execute(
                text(
                    """
                    SELECT * FROM vwMemberChurchHierarchy
                    WHERE Member_Code = :Member_Code
                    """
                ),
                dict(Member_Code=member.Code),
            ).first()
            if not mc_hierarchy:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Member's church hierarchy not found",
                )
            return mc_hierarchy
        except Exception as err:
            raise err


def get_member_services(
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
    current_user_access: Annotated[UserAccess, Depends(get_current_user_access)],
    church_services: Annotated[ChurchServices, Depends(get_church_services)],
    db_current_user: Annotated[str, Depends(set_db_current_user)],
):
    return MemberServices(db, current_user, current_user_access, church_services)
