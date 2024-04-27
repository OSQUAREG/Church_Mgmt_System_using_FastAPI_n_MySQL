from datetime import datetime, timedelta, timezone


from ...check import User
from fastapi import HTTPException, status  # type: ignore
from passlib.context import CryptContext  # type: ignore
from jose import JWTError, jwt  # type: ignore
from sqlalchemy.orm import Session  # type: ignore
from sqlalchemy import text  # type: ignore

from ...common.config import settings
from ...authentication.models.auth import TokenAccessData, TokenData, UserAccess

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
            return user
        except Exception as err:
            db.rollback()
            raise err

    # Create Access Token
    def create_access_token(self, data: dict):
        payload = data.copy()
        expires_delta = datetime.now(timezone.utc) + timedelta(
            minutes=ACCESS_TOKEN_EXPIRE_MINUTES
        )
        payload.update({"exp": expires_delta})
        token = jwt.encode(payload, key=JWT_SECRET_KEY, algorithm=ALGORITHM)
        return token

    # Verify Access Token
    def verify_access_token(self, token: str):
        try:
            payload = jwt.decode(token, key=JWT_SECRET_KEY, algorithms=ALGORITHM)  # type: ignore
            username: str = payload.get("usercode")  # type: ignore
            if username is None:
                raise auth_credentials_exception
            token_data = TokenData(username=username)
            return token_data
        except JWTError as e:
            print(e)
            raise auth_credentials_exception
        except AssertionError as e:
            print(e)
            raise auth_credentials_exception

    # Authenticate User
    def authenticate_user(
        self,
        username: str,
        password: str,
        db: Session,
    ):
        # get user from db
        user = self.get_user(username, db)
        # verify user password
        user_check = self.verify_password(password, user.Password)
        if user_check is False:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Oops! Incorrect username or password",
            )
        return user

    # Get User Access
    def get_user_access(self, username: str, church_level: str, db: Session):
        try:
            user_access = db.execute(
                text(
                    """
                    SELECT B.Usercode, D.Password, A.Level_Code, Email, Role_Code, Church_Code, A.HeadChurch_Code, Module_Code, SubModule_Code, Access_Type
                    FROM tblUserRoleSubModule A
                    LEFT JOIN tblUserRole B ON B.Code = A.UserRole_Code
                    LEFT JOIN dfSubModuleAccess C ON C.Code = A.SubModuleAccess_Code
                    LEFT JOIN tblUser D ON D.Usercode = B.Usercode
                    WHERE A.Is_Active=1 AND B.Is_Active=1 AND C.Is_Active=1
                        AND B.Usercode = :Usercode AND Level_Code = :Level_Code
                    """
                ),
                dict(Usercode=username, Level_Code=church_level),
            ).first()
            if not user_access:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="User not found",
                )
            return user_access
        except Exception as err:
            db.rollback()
            raise err

    # Re-Authenticate User Access
    def re_authenticate_user_access(
        self,
        church_level: str,
        current_user: User,
        db: Session,
    ):
        # checks if church is selected
        if church_level is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=f"Oops! Please select a church level",
            )
        # fetch user church level list from db
        user_church_level_list = db.execute(
            text(
                """
                SELECT A.Level_Code
                FROM tblUserRoleSubModule A
                LEFT JOIN tblUserRole B ON B.Code = A.UserRole_Code
                WHERE A.Is_Active=1 AND B.Is_Active=1
                    AND B.Usercode = :Usercode;
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
            print(user_church_level.Level_Code)
            print(church_level)
            if user_church_level.Level_Code == church_level:
                break
        else:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Oops! You are NOT allowed to access this User Church Level.",
            )
        # get user access data from db
        user_access = self.get_user_access(current_user.Usercode, church_level, db)
        return user_access

    # Re-Verify Access Token
    def re_verify_access_token(self, token: str):
        try:
            payload = jwt.decode(token, key=JWT_SECRET_KEY, algorithms=ALGORITHM)  # type: ignore
            username: str = payload.get("usercode")  # type: ignore
            church_level: str = payload.get("church_level")  # type: ignore
            if username is None:
                raise auth_credentials_exception
            token_data = TokenAccessData(
                username=username,
                church_level=church_level,
            )
            print(token_data)
            return token_data
        except JWTError as e:
            print(e)
            raise auth_credentials_exception
        except AssertionError as e:
            print(e)
            raise auth_credentials_exception
