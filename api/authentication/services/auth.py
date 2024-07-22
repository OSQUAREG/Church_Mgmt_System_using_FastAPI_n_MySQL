from datetime import datetime, timedelta, timezone

from fastapi import HTTPException, status  # type: ignore
from passlib.context import CryptContext  # type: ignore
from jose import JWTError, jwt  # type: ignore
from sqlalchemy.orm import Session  # type: ignore
from sqlalchemy import text  # type: ignore

from ...common.config import settings
from ...authentication.models.auth import TokenLevelData, TokenData, User

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

JWT_SECRET_KEY = settings.jwt_secret_key
ALGORITHM = settings.algorithm
ACCESS_TOKEN_EXPIRE_MINUTES = settings.access_token_expire_minutes
db_schema_headchu = settings.db_schema_headchu
db_schema_generic = settings.db_schema_generic


auth_credentials_exception = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Could not validate credentials",
    headers={"WWW-Authenticate": "Bearer"},
)


class AuthService:
    """
    Authentication Services
    - Get Hash Password
    - Verify Password
    - Get User
    - Create Access Token
    - Verify Access Token
    - Authenticate User
    - Get User Level
    - Re-Authenticate User Access
    - Re-verify Access Token
    - Get User Access
    """

    # Hash Password
    def get_password_hash(self, plain_password: str) -> str:
        return pwd_context.hash(plain_password)

    # Verify Password
    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        return pwd_context.verify(plain_password, hashed_password)

    # Get User
    def get_user(self, username: str, db: Session):
        try:
            user = db.execute(
                text(
                    f"""
                    SELECT A.Usercode, A.Password, A.Email, A.Head_Code, A.Is_Active, B.Title, B.Title2, B.First_Name, B.Last_Name, A.Is_Member, C.Name AS Head_Name
                    FROM {db_schema_headchu}.tblUsers A
                    LEFT JOIN {db_schema_headchu}.tblMembers B ON B.Code = A.Usercode
                    LEFT JOIN {db_schema_generic}.tblChurchHeads C ON C.Code = A.Head_Code
                    WHERE A.Usercode = :Usercode;
                    """
                ),
                dict(
                    Usercode=username,
                ),
            ).first()
            if not user:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="User not found",
                )
            # print("user fetched")
            return user
        except Exception as err:
            msg = "User not found" + str(err)
            print(msg)
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=msg)

    # Create Access Token
    def create_access_token(self, data: dict):
        payload = data.copy()
        expires_delta = datetime.now(timezone.utc) + timedelta(
            minutes=ACCESS_TOKEN_EXPIRE_MINUTES
        )
        payload.update({"exp": expires_delta})
        token = jwt.encode(payload, key=JWT_SECRET_KEY, algorithm=ALGORITHM)
        # print("access token created")
        return token

    # Verify Access Token
    def verify_access_token(self, token: str):
        try:
            payload = jwt.decode(token, key=JWT_SECRET_KEY, algorithms=ALGORITHM)  # type: ignore
            username: str = payload.get("usercode")  # type: ignore
            if username is None:
                raise auth_credentials_exception
            token_data = TokenData(username=username)
            # print("access token verified")
            return token_data
        except JWTError as err:
            # print(err)
            # print("access token not verified")
            raise auth_credentials_exception
        except AssertionError as err:
            # print(err)
            # print("access token not verified")
            raise auth_credentials_exception

    def authenticate_user(self, username: str, password: str, db: Session):
        try:
            user = self.get_user(username, db)
            if not self.verify_password(password, user.Password):
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Oops! Incorrect username or password",
                )
            return user
        except HTTPException as err:
            raise err
        except Exception as err:
            msg = "Failed to authenticate user. Error: " + str(err)
            print(msg)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=msg
            )

    # Get User Access
    def get_user_level(self, username: str, level_code: str, db: Session):
        try:
            user_level = db.execute(
                text(
                    f"""
                    SELECT DISTINCT A.Usercode, Password, Email, A.Level_Code, C.Level_Name, A.Church_Code, E.Name AS Church_Name, A.Head_Code, D.Title, D.Title2, D.First_Name, D.Last_Name
                    FROM {db_schema_headchu}.tblUserRole A
                    LEFT JOIN {db_schema_headchu}.tblUsers B ON B.Usercode = A.Usercode
                    LEFT JOIN {db_schema_headchu}.tblChurchLevels C ON C.Code = A.Level_Code
                    LEFT JOIN {db_schema_headchu}.tblMembers D ON D.Code = A.Usercode
                    LEFT JOIN {db_schema_headchu}.tblChurches E ON E.Code = A.Church_Code
                    WHERE A.Is_Active = :Is_Active AND B.Is_Active = :Is_Active AND A.Status = :Status
                        AND A.Usercode = :Usercode AND A.Level_Code = :Level_Code;
                    """
                ),
                dict(
                    Usercode=username,
                    Level_Code=level_code,
                    Is_Active=1,
                    Status="APR",
                ),
            ).first()
            if not user_level:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="User's Church Level not found or approved",
                )
            # print("user level fetched")
            return user_level
        except Exception as err:
            print(err)
            print("user level not fetched")
            raise err

    def get_user_levels(self, username: str, db: Session):
        try:
            user_levels = db.execute(
                text(
                    f"""
                    SELECT A.Level_Code, B.Level_Name
                    FROM {db_schema_headchu}.tblUserRole A
                    LEFT JOIN {db_schema_headchu}.tblChurchLevels B ON B.Code = A.Level_Code AND B.Head_Code = A.Head_Code
                    WHERE A.Is_Active = :Is_Active AND B.Is_Active = :Is_Active AND A.Status = :Status
                    AND Usercode = :Usercode;
                    """
                ),
                dict(Usercode=username, Is_Active=1, Status="APR"),
            ).all()
            if not user_levels:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="You don't have access to any Church Levels.",
                )
            # print("user levels fetched")
            return user_levels
        except Exception as err:
            db.rollback()
            # print(err)
            # print("user levels not fetched")
            raise err

    # Re-Authenticate User Access
    def re_authenticate_user_access(
        self,
        church_level: str,
        current_user: User,
        db: Session,
    ):
        try:
            # checks if church is selected
            if church_level is None:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail=f"Oops! Please re-login and select a valid Church Level",
                )
            # fetch user church level list from db
            user_church_level_list = self.get_user_levels(current_user.Usercode, db)
            # check if user has access to church level
            if user_church_level_list is None:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Oops! No access to any Church Levels",
                )
            # finds and validates selected church level
            for user_church_level in user_church_level_list:
                if (
                    user_church_level.Level_Code == church_level
                    or user_church_level.Code == church_level
                ):
                    break
            else:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Oops! Please select your accessible Church Level.",
                )
            # get user access data from db
            user_access = self.get_user_level(current_user.Usercode, church_level, db)
            # print("user re-authenticated")
            return user_access
        except Exception as err:
            db.rollback()
            # print(err)
            # print("user not re-authenticated")
            raise err

    # Re-Verify Access Token
    def re_verify_access_token(self, token: str):
        try:
            payload = jwt.decode(token, key=JWT_SECRET_KEY, algorithms=ALGORITHM)  # type: ignore
            username: str = payload.get("usercode")  # type: ignore
            church_level: str = payload.get("church_level")  # type: ignore
            if username is None:
                raise auth_credentials_exception
            token_data = TokenLevelData(
                username=username,
                church_level=church_level,
            )
            # print("user re-verified")
            return token_data
        except JWTError as e:
            # print(e)
            # print("user not re-verified")
            raise auth_credentials_exception
        except AssertionError as e:
            # print(e)
            # print("user not re-verified")
            raise auth_credentials_exception

    def get_user_access(self, username: str, level_code: str, db: Session):
        try:
            user_access = db.execute(
                text(
                    f"""
                    SELECT A.Usercode, D.Password, D.Email, A.Role_Code, E.Hierarchy_Code, A.Level_Code, F.Level_No, E.Level_Name, A.Church_Code, A.Group_Code, C.Module_Code, C.SubModule_Code, C.Access_Type, A.Head_Code, G.First_Name, G.Last_Name, G.Title, G.Title2, D.Is_Member
                    FROM {db_schema_headchu}.tblUserRole A
                    LEFT JOIN {db_schema_headchu}.tblRoleSubModules B ON B.Role_Code = A.Role_Code
                    LEFT JOIN {db_schema_generic}.tblSubModuleAccess C ON C.Code = B.SubModuleAccess_Code
                    LEFT JOIN {db_schema_headchu}.tblUsers D ON D.Usercode = A.Usercode
                    LEFT JOIN {db_schema_headchu}.tblChurchLevels E ON E.Code = A.Level_Code
                    LEFT JOIN {db_schema_generic}.tblHierarchy F ON F.Code = E.Hierarchy_Code
                    LEFT JOIN {db_schema_headchu}.tblMembers G ON G.Code = A.Usercode
                    WHERE A.Is_Active = :Is_Active AND B.Is_Active = :Is_Active AND C.Is_Active = :Is_Active 
                        AND A.Status = :Status AND B.Status = :Status
                        AND A.Usercode = :Usercode AND A.Level_Code = :Level_Code;
                    """
                ),
                dict(
                    Usercode=username,
                    Level_Code=level_code,
                    Is_Active=1,
                    Status="APR",
                ),
            ).all()
            if not user_access:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="User access denied. Select a valid Church Level.",
                )
            # print("user access fetched")
            return user_access
        except Exception as err:
            db.rollback()
            # print(err)
            # print("user access not fetched")
            raise err
