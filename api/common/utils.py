from typing import Optional

from fastapi import HTTPException, status  # type: ignore
from phonenumbers import format_number, PhoneNumberFormat, parse  # type: ignore
from sqlalchemy import text  # type: ignore
from sqlalchemy.orm import Session  # type: ignore

from ..authentication.models.auth import UserAccess


def get_phonenumber(number_str: str):
    phonenumber = format_number(parse(number_str), PhoneNumberFormat.E164)
    return phonenumber


def check_if_new_code_name_exist(
    new_code_name: str,
    table_name: str,
    db: Session,
    action: str,
    existing_code_name: Optional[str] = None,
    headchurch_code: Optional[str] = None,
):
    if action == "create":
        code_name_check = (
            db.execute(
                text(
                    f"""
                    SELECT * FROM {table_name} 
                    WHERE (
                        upper(Code) = upper(:Code)
                        OR lower(Name) = lower(:Name)
                        );
                    """
                ),
                dict(Code=new_code_name, Name=new_code_name),
            ).first()
            if headchurch_code is None
            else db.execute(
                text(
                    f"""
                    SELECT * FROM {table_name} 
                    WHERE HeadChurch_Code = :HeadChurch_Code AND (
                        upper(Code) = upper(:Code)
                        OR lower(Name) = lower(:Name)
                    );
                    """
                ),
                dict(
                    Code=new_code_name,
                    Name=new_code_name,
                    HeadChurch_Code=headchurch_code,
                ),
            ).first()
        )
        if code_name_check:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Code/Name: '{new_code_name.upper()}' already exists.",
            )
    elif action == "update":
        if new_code_name != existing_code_name:
            code_name_check = (
                db.execute(
                    text(
                        f"""
                        SELECT * FROM {table_name} 
                        WHERE (
                            upper(Code) = upper(:Code)
                            OR lower(Name) = lower(:Name)
                            );
                        """
                    ),
                    dict(Code=new_code_name, Name=new_code_name),
                ).first()
                if headchurch_code is None
                else db.execute(
                    text(
                        f"""
                        SELECT * FROM {table_name} 
                        WHERE HeadChurch_Code = :HeadChurch_Code AND (
                            upper(Code) = upper(:Code)
                            OR lower(Name) = lower(:Name)
                        );
                        """
                    ),
                    dict(
                        Code=new_code_name,
                        Name=new_code_name,
                        HeadChurch_Code=headchurch_code,
                    ),
                ).first()
            )
            if code_name_check:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail=f"Code/Name: '{new_code_name.upper()}' already exists.",
                )
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid action selected: '{action}'",
        )
    return False


def check_duplicate_entry(
    db: Session,
    headchurch_code: str,
    table_name: str,
    column_name: str,
    column_value,
    column_old_value: str | None = None,
    column_name2: str | None = None,
    column_value2: str | None = None,
    column_old_value2: str | None = None,
    column_name3: str | None = None,
    column_value3: str | None = None,
    column_old_value3: str | None = None,
):
    if column_old_value and column_value == column_old_value:
        return False
    if column_old_value2 and column_value2 == column_old_value2:
        return False
    if column_old_value3 and column_value3 == column_old_value3:
        return False

    query = f"""
    SELECT * FROM {table_name} 
    WHERE HeadChurch_Code = :Headchurch_Code AND (
        {column_name} = :column_value
    """

    params = {"Headchurch_Code": headchurch_code, "column_value": column_value}

    if column_name2 and column_value2:
        query += f" AND {column_name2} = :column_value2"
        params["column_value2"] = column_value2

    if column_name3 and column_value3:
        query += f" AND {column_name3} = :column_value3"
        params["column_value3"] = column_value3

    query += ");"

    duplicate_check = db.execute(text(query), params).first()

    if duplicate_check:
        error_detail = f"Duplicate Error: {column_name}: '{column_value}'"
        if column_name2 and column_value2:
            error_detail += f" plus {column_name2}: '{column_value2}'"
        if column_name3 and column_value3:
            error_detail += f" and {column_name3}: '{column_value3}'"
        error_detail += " already exists."

        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=error_detail,
        )
    return False


def custom_title_case(s):
    words = s.split()
    for i, word in enumerate(words):
        if len(word) > 1 and word.isupper():
            # Skip words with two consecutive capital letters
            continue
        else:
            words[i] = word.capitalize()
    return " ".join(words)


def set_user_access(
    current_user_access: UserAccess,
    headchurch_code: str | None = None,
    church_code: str | None = None,
    access_type: list | None = None,
    level_code: list | None = None,
    level_no: int | None = None,
    role_code: list | None = None,
    module_code: list | None = None,
    submodule_code: list | None = None,
):
    for user_access in current_user_access:
        if (
            (headchurch_code is None or user_access.HeadChurch_Code == headchurch_code)
            # and (church_code is None or user_access.Church_Code == church_code)
            and (access_type is None or user_access.Access_Type in access_type)
            and (
                (church_code is None or user_access.Church_Code == church_code)
                or (level_code is None or user_access.Level_Code in level_code)
                or (level_no is None or user_access.Level_No <= level_no)
            )
            and (role_code is None or user_access.Role_Code in role_code)
            and (module_code is None or user_access.Module_Code in module_code)
            and (submodule_code is None or user_access.SubModule_Code in submodule_code)
        ):
            # print("user access granted")
            break
    else:
        # print("user access not granted")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access Denied: You are NOT ALLOWED to perform this action",
        )


def get_level(code: str, head_code: str, db: Session):
    """code: can be Level_Code or ChurchLevel_Code or Church_Code."""
    level_no = db.execute(
        text(
            """
            SELECT DISTINCT B.Level_No, A.Level_Code, A.ChurchLevel_Code FROM tblHeadChurchLevels  A
            LEFT JOIN dfHierarchy B ON B.Code = A.Level_Code
            LEFT JOIN tblChurches C ON C.Level_Code = A.Level_Code
            WHERE Head_Code = :Head_Code AND A.Is_Active = :Is_Active
            AND (A.Level_Code = :Code OR A.ChurchLevel_Code = :Code OR C.Code = :Code);
            """
        ),
        dict(Code=code, Head_Code=head_code, Is_Active=1),
    ).first()
    if level_no is None:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Church Level is not active",
        )
    return level_no


def validate_code_type(code: str | None, category: str, db: Session):
    if not code:
        return None
    code_type = db.execute(
        text(
            """
            SELECT Code, Name FROM dfCodeTable 
            WHERE Code = :Code AND Category = :Category AND Is_Active = :Active;
            """
        ),
        dict(Code=code, Category=category, Active=1),
    ).first()
    # check if code is valid
    if code_type is None:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"{code.upper()} is an invalid {category} code",
        )
    return True
