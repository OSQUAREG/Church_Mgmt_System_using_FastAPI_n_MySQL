from ..authentication.models.auth import UserAccess
from fastapi import HTTPException, status  # type: ignore
from phonenumbers import format_number, PhoneNumberFormat, parse  # type: ignore
from sqlalchemy import text  # type: ignore
from sqlalchemy.orm import Session  # type: ignore


def get_phonenumber(number_str: str):
    phonenumber = format_number(parse(number_str), PhoneNumberFormat.E164)
    return phonenumber


def check_if_new_code_exist(code: str, table_name: str, db: Session):
    code_check = db.execute(
        text(f"SELECT * FROM {table_name} WHERE Code = :Code;"),
        dict(Code=code),
    ).first()
    if code_check and code_check.Code != code:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Code: '{code}' already exists",
        )
    return True


def check_if_new_name_exist(name: str, table_name: str, db: Session):
    name_check = db.execute(
        text(f"SELECT * FROM {table_name} WHERE Name = :Name;"),
        dict(Name=name),
    ).first()
    db_name = custom_title_case(name_check.Name) if name_check else None
    check_name = custom_title_case(name)
    if name_check and (db_name != check_name):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Name: '{name}' already exists",
        )
    return True


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
    role_code: list | None = None,
    module_code: list | None = None,
    submodule_code: list | None = None,
):
    for user_access in current_user_access:
        if (
            (headchurch_code is None or user_access.HeadChurch_Code == headchurch_code)
            and (church_code is None or user_access.Church_Code == church_code)
            and (access_type is None or user_access.Access_Type in access_type)
            and (level_code is None or user_access.Level_Code in level_code)
            and (role_code is None or user_access.Role_Code in role_code)
            and (module_code is None or user_access.Module_Code in module_code)
            and (submodule_code is None or user_access.SubModule_Code in submodule_code)
        ):
            print("user access granted")
            break
    else:
        print("user access not granted")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are NOT ALLOWED to perform this action",
        )
