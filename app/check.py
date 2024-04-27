from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel

app = FastAPI()


# Fake user model
class User(BaseModel):
    username: str
    password: str
    extra_requirement: str


# Fake user database
USERS = {
    "user1": {"password": "pass1", "extra_requirement": "extra1"},
    "user2": {"password": "pass2", "extra_requirement": "extra2"},
}

# OAuth2 with password flow
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/token")


# Authenticate user
def authenticate_user(username: str, password: str, extra_requirement: str):
    user_data = USERS.get(username)
    if (
        user_data
        and user_data["password"] == password
        and user_data["extra_requirement"] == extra_requirement
    ):
        return User(
            username=username, password=password, extra_requirement=extra_requirement
        )
    else:
        return None


# Token endpoint with extra requirement validation
@app.post("/token")
def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    extra_requirement: str = Depends(oauth2_scheme),
):
    user = authenticate_user(form_data.username, form_data.password, extra_requirement)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username, password, or extra requirement",
            headers={"WWW-Authenticate": "Bearer"},
        )
    # Here you would generate and return the access token
    # For simplicity, let's just return a dummy token
    return {"access_token": "dummy_token", "token_type": "bearer"}


# Protected endpoint that requires authentication
@app.get("/protected")
def protected_route(token: str = Depends(oauth2_scheme)):
    # Here you would implement logic for protected route
    return {"message": "This route is protected and requires authentication"}
