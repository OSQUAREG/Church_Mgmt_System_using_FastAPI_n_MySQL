from fastapi import APIRouter  # type: ignore

user_route = APIRouter(prefix="/user", tags=["Users Operations"])
