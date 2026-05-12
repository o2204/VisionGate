from zxcvbn import zxcvbn
from typing import Annotated

from fastapi import APIRouter, Depends, Form,  Request
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import EmailStr

from src.schemas.user_schema import UserCreate 
from src.core.container import UserServiceDep, get_user_token
from src.schemas.user_schema import UserRead
from src.clients.db.redis import add_jti_to_blacklist
from src.core.config import settings

from src.core.container import templates

user_router = APIRouter(prefix="/user", tags=["Users"])


@user_router.post("/signup", response_model=UserRead)
async def create_user(
    user: UserCreate,
    user_service: UserServiceDep
):
    return await user_service._add_user(
        data=user.model_dump(),
        router_prefix=user_router.prefix
    )


### Login the user 
@user_router.post("/login")
async def login_user(
    request_form: Annotated[OAuth2PasswordRequestForm, Depends()],
    service: UserServiceDep,
):
    token = await service.login(
        request_form.username, 
        request_form.password
    )

    return {
        "access_token": token,
        "token_type": "bearer"
    }


### Verify User Email
@user_router.get("/verify")
async def verify_user_email(token: str, request: Request, service: UserServiceDep):

    is_success = await service.verify_email(token)

    return templates.TemplateResponse(
            request=request,
            name="verify_email_success.html" if is_success else "verify_email_failed.html"
        )


## Forgot Password - Send Reset Link
@user_router.get("/forgot-password")
async def forgot_password(
    email: EmailStr,
    service: UserServiceDep,
):
    await service.send_password_reset_link(email, user_router.prefix)
    return {"detail": "Password reset link sent if the email exists in our system"}


### Password Reset Form
@user_router.get("/reset-password-form")
async def get_reset_password_form(request: Request, token: str):

    return templates.TemplateResponse(
        request=request,
        name="password/reset.html",
        context={
            "request": request,
            "reset_password": f"http://{settings.APP_DOMAIN}{user_router.prefix}/reset-password?token={token}",
            "token": token
        }
    )
    

### Email Password Reset Link
@user_router.post("/reset-password")
async def reset_password(
    request: Request,
    token: Annotated[str, Form()], 
    password: Annotated[str, Form()],
    confirm_password: Annotated[str, Form()], 
    service: UserServiceDep
):
    errors = []

    # Match check for password and confirm password
    if password != confirm_password:
        errors.append("Passwords do not match.")
    # zxcvbn password strength check
    result = zxcvbn(password)
    if result["score"] < 3:
        errors.append("Password is too weak. Please choose a stronger password.")
    if len(password) < 8:
        errors.append("Password must be at least 8 characters long.")
    if errors:
        return templates.TemplateResponse(
            request=request,
            name="password/reset.html",
            context={
                "request": request,
                "reset_password": f"http://{settings.APP_DOMAIN}{user_router.prefix}/reset-password?token={token}",
                "token": token,
                "errors": errors
            }
        )
    is_success = await service.reset_password(token, password)

    return templates.TemplateResponse(
        request=request,
        name="password/reset_success.html" if is_success else "password/reset_failed.html"
    )


### Logout the user 
@user_router.get("/logout")
async def logout_user(
    token_data: Annotated[dict, Depends(get_user_token)],
):
    await add_jti_to_blacklist(token_data["jti"]) 

    return {
        "detail": "Successful Log Out"
    }