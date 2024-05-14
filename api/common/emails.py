from typing import List
from datetime import datetime, timedelta, timezone

from starlette.responses import JSONResponse  # type: ignore
from fastapi_mail import FastMail, MessageSchema, ConnectionConfig, MessageType  # type: ignore
from pydantic import EmailStr, BaseModel  # type: ignore
from jose import jwt  # type: ignore

from .. import app
from ..authentication.models.auth import User
from .config import settings


class EmailSchema(BaseModel):
    email: List[EmailStr]


MAIL_SECRET_KEY = settings.mail_secret_key
ALGORITHM = settings.algorithm
MAIL_TOKEN_EXPIRE_HOURS = settings.mail_token_expire_hours

conf = ConnectionConfig(
    MAIL_USERNAME=settings.mail_username,
    MAIL_PASSWORD=settings.mail_password,
    MAIL_FROM=settings.mail_from,
    MAIL_PORT=int(settings.mail_port),
    MAIL_SERVER=settings.mail_server,
    MAIL_FROM_NAME=settings.mail_from_name,
    MAIL_STARTTLS=True,
    MAIL_SSL_TLS=False,
    USE_CREDENTIALS=True,
    VALIDATE_CERTS=True,
)


async def send_email(email: EmailSchema, user: User):
    expires_delta = datetime.now(timezone.utc) + timedelta(
        hours=MAIL_TOKEN_EXPIRE_HOURS
    )
    token_data = {"username": user.Usercode, "exp": expires_delta}
    token = jwt.encode(token_data, key=MAIL_SECRET_KEY, algorithm=ALGORITHM)
    template = f"""
        Hello, welcome to ChMS!

        Please confirm your email address by clicking on the link below.

        {app.url_path_for("auth.confirm_email", token=token, email=email.email)}
        """
    message = MessageSchema(
        subject="Welcome to ChurchMan Church Management System",
        recipients=email.email,
        body=template,
        subtype=MessageType.html,
    )
    fm = FastMail(conf)
    await fm.send_message(message)
    return JSONResponse(status_code=200, content={"message": "Email sent successfully"})
