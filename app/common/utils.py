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
