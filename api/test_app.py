from fastapi import FastAPI, Request, APIRouter, Depends, HTTPException
from fastapi.responses import JSONResponse
from fastapi_jwt_auth import AuthJWT
from fastapi_jwt_auth.exceptions import AuthJWTException
from routers import users, items
from pydantic import BaseModel

app = FastAPI()

router = APIRouter()

app.include_router(router, tags=["users"])
app.include_router(router, tags=["items"])


class Settings(BaseModel):
    authjwt_secret_key: str = "secret"


@AuthJWT.load_config
def get_config():
    return Settings()


@app.exception_handler(AuthJWTException)
def authjwt_exception_handler(request: Request, exc: AuthJWTException):
    return JSONResponse(status_code=exc.status_code, content={"detail": exc.message})


# User.py
class User(BaseModel):
    username: str
    password: str


@router.post("/login")
def login(user: User, Authorize: AuthJWT = Depends()):
    if user.username != "test" or user.password != "test":
        raise HTTPException(status_code=401, detail="Bad username or password")

    access_token = Authorize.create_access_token(subject=user.username)
    return {"access_token": access_token}


# item.py
@router.get("/items")
def items(Authorize: AuthJWT = Depends()):
    Authorize.jwt_required()

    items = ["item1", "item2", "item3"]

    return {"items": items}
