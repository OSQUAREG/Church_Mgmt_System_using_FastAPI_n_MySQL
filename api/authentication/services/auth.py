from datetime import datetime, timedelta, timezone


from ...check import User
from fastapi import HTTPException, status  # type: ignore
from passlib.context import CryptContext  # type: ignore
from jose import JWTError, jwt  # type: ignore
from sqlalchemy.orm import Session  # type: ignore
from sqlalchemy import text  # type: ignore

from ...common.config import settings
from ...authentication.models.auth import TokenLevelData, TokenData

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

JWT_SECRET_KEY = settings.jwt_secret_key
ALGORITHM = settings.algorithm
ACCESS_TOKEN_EXPIRE_MINUTES = settings.access_token_expire_minutes


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

    def get_user(self, username: str, db: Session):
        try:
            user = db.execute(
                text("SELECT * FROM tblUser WHERE Usercode = :Usercode;"),
                dict(Usercode=username),
            ).first()
            if not user:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="User not found",
                )
            print("user fetched")
            return user
        except Exception as err:
            db.rollback()
            print(err)
            print("user not fetched")
            raise err

    # Create Access Token
    def create_access_token(self, data: dict):
        payload = data.copy()
        expires_delta = datetime.now(timezone.utc) + timedelta(
            minutes=ACCESS_TOKEN_EXPIRE_MINUTES
        )
        payload.update({"exp": expires_delta})
        token = jwt.encode(payload, key=JWT_SECRET_KEY, algorithm=ALGORITHM)
        print("access token created")
        return token

    # Verify Access Token
    def verify_access_token(self, token: str):
        try:
            payload = jwt.decode(token, key=JWT_SECRET_KEY, algorithms=ALGORITHM)  # type: ignore
            username: str = payload.get("usercode")  # type: ignore
            if username is None:
                raise auth_credentials_exception
            token_data = TokenData(username=username)
            print("access token verified")
            return token_data
        except JWTError as err:
            print(err)
            print("access token not verified")
            raise auth_credentials_exception
        except AssertionError as err:
            print(err)
            print("access token not verified")
            raise auth_credentials_exception

    # Authenticate User
    def authenticate_user(
        self,
        username: str,
        password: str,
        db: Session,
    ):
        try:
            # get user from db
            user = self.get_user(username, db)
            # verify user password
            user_check = self.verify_password(password, user.Password)
            if user_check is False:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Oops! Incorrect username or password",
                )
            print("user authenticated")
            return user
        except Exception as err:
            db.rollback()
            print(err)
            print("user not authenticated")
            raise err

    # Get User Access
    def get_user_level(self, username: str, church_level: str, db: Session):
        try:
            user_access = db.execute(
                text(
                    """
                    SELECT DISTINCT A.Usercode, Password, Email, A.Level_Code, C.ChurchLevel_Code, A.HeadChurch_Code
                    FROM tblUserRole A
                    LEFT JOIN tblUser B ON B.Usercode = A.Usercode
                    LEFT JOIN tblHeadChurchLevels C ON C.Level_Code = A.Level_Code AND C.Head_Code = A.HeadChurch_Code
                    WHERE A.Is_Active=1 AND B.Is_Active=1
                        AND A.Usercode = :Usercode AND (A.Level_Code = :Level_Code OR C.ChurchLevel_Code = :ChurchLevel_Code);
                    """
                ),
                dict(
                    Usercode=username,
                    Level_Code=church_level,
                    ChurchLevel_Code=church_level,
                ),
            ).first()
            if not user_access:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="User not found",
                )
            print("user level fetched")
            return user_access
        except Exception as err:
            db.rollback()
            print(err)
            print("user level not fetched")
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
                    detail=f"Oops! Please select a valid Church Level",
                )
            # fetch user church level list from db
            user_church_level_list = db.execute(
                text(
                    """
                    SELECT A.Level_Code, B.ChurchLevel_Code
                    FROM tblUserRole A
                    LEFT JOIN tblHeadChurchLevels B ON B.Level_Code = A.Level_Code AND B.Head_Code = A.HeadChurch_Code
                    WHERE A.Is_Active=1 AND B.Is_Active
                    """
                ),
                dict(Usercode=current_user.Usercode),
            ).all()
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
                    or user_church_level.ChurchLevel_Code == church_level
                ):
                    break
            else:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Oops! Please select your accessible Church Level.",
                )
            # get user access data from db
            user_access = self.get_user_level(current_user.Usercode, church_level, db)
            print("user re-authenticated")
            return user_access
        except Exception as err:
            db.rollback()
            print(err)
            print("user not re-authenticated")
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
            print("user re-verified")
            return token_data
        except JWTError as e:
            print(e)
            print("user not re-verified")
            raise auth_credentials_exception
        except AssertionError as e:
            print(e)
            print("user not re-verified")
            raise auth_credentials_exception

    def get_user_access(self, username: str, church_level: str, db: Session):
        try:
            user_access = db.execute(
                text(
                    """
                    SELECT A.Usercode, Password, Email, Role_Code, A.Level_Code, ChurchLevel_Code, Church_Level, Church_Code, A.HeadChurch_Code, Module_Code, SubModule_Code, Access_Type
                    FROM tblUserRole A
                    LEFT JOIN tblUserRoleSubModule B ON B.UserRole_Code = A.Code
                    LEFT JOIN dfSubModuleAccess C ON C.Code = B.SubModuleAccess_Code
                    LEFT JOIN tblUser D ON D.Usercode = A.Usercode
                    LEFT JOIN tblHeadChurchLevels E ON E.Level_Code = A.Level_Code
                    WHERE A.Is_Active=1 AND B.Is_Active=1 AND C.Is_Active=1
                        AND A.Usercode = :Usercode AND (A.Level_Code = :Level_Code OR E.ChurchLevel_Code = :ChurchLevel_Code);
                    """
                ),
                dict(
                    Usercode=username,
                    Level_Code=church_level,
                    ChurchLevel_Code=church_level,
                ),
            ).all()
            if not user_access:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="User access denied. Select a valid Church Level.",
                )
            print("user access fetched")
            return user_access
        except Exception as err:
            db.rollback()
            print(err)
            print("user access not fetched")
            raise err
