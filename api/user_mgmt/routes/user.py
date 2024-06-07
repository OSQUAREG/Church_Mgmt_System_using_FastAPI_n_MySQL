from typing import Annotated

from ..services.user import UserServices, get_user_services
from ..models.user import UserResponse
from fastapi import APIRouter, status, Depends  # type: ignore

user_route = APIRouter(prefix="/user", tags=["Users Operations"])


@user_route.post(
    "/member/{member_code}",
    status_code=status.HTTP_201_CREATED,
    name="Create User From Member",
    response_model=UserResponse,
)
async def create_user_from_member(
    member_code: str,
    user_services: Annotated[UserServices, Depends(get_user_services)],
):
    new_user = await user_services.create_user_from_member(member_code)
    # set response body
    response = dict(
        data=new_user,
        status_code=status.HTTP_200_OK,
        message=f"Successfully created member as a user: '{new_user.First_Name} {new_user.Last_Name} ({new_user.Code})'",
    )
    return response
