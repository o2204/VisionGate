from typing import Annotated

from fastapi import APIRouter, Depends, Form, HTTPException, Request, status
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import EmailStr
from zxcvbn import zxcvbn

from src.clients.db.redis import add_jti_to_blacklist
from src.core.container import (
    AdminServiceDep,
    UserServiceDep,
    AdminDep,
    get_admin_token,
)

from src.core.config import settings
from src.core.container import templates
from src.schemas.admin_schema import AdminCreate, AdminMessage


admin_router = APIRouter(
    prefix="/admin",
    tags=["Admin"]
)


# Admin Login (No auth required)
@admin_router.post("/login") 
async def login_admin(
    request_form: Annotated[OAuth2PasswordRequestForm, Depends()],
    service: AdminServiceDep,
):
    token = await service.admin_login(
        request_form.username,
        request_form.password
    )

    return {
        "access_token": token,
        "token_type": "bearer"
    }


@admin_router.get("/reset-password-form")
async def reset_password_form(request: Request, token: str):

    return templates.TemplateResponse(
        "password/reset.html",
        {
            "request": request,
            "reset_password": f"http://{settings.APP_DOMAIN}{admin_router.prefix}/reset-password?token={token}",
            "token": token
        }
    )


@admin_router.post("/reset-password")
async def reset_admin_password(
    request: Request,
    token: Annotated[str, Form()],
    password: Annotated[str, Form()],
    confirm_password: Annotated[str, Form()],
    service: AdminServiceDep
):
    errors = []

    if password != confirm_password:
        errors.append("Passwords do not match.")

    result = zxcvbn(password)
    if result["score"] < 3:
        errors.append("Password is too weak. Please choose a stronger password.")

    if len(password) < 8:
        errors.append("Password must be at least 8 characters long.")

    if errors:
        return templates.TemplateResponse(
            "password/reset.html",
            {
                "request": request,
                "token": token,
                "errors": errors
            }
        )

    result = await service.reset_admin_password(token, password)

    # expired
    if result == "expired":
        return templates.TemplateResponse(
            "password/expired.html",
            {
                "request": request,
                "message": "This reset link expired after 24 hours."
            }
        )

    # not found
    if result == "not_found":
        return templates.TemplateResponse(
            "password/reset_failed.html",
            {
                "request": request
            }
        )

    # success
    return templates.TemplateResponse(
        "password/reset_success.html",
        {
            "request": request
        }
    )

## Forgot Password - Send Reset Link
@admin_router.get("/forgot-password")
async def forgot_password(
    email: EmailStr,
    service: AdminServiceDep,
):
    await service.send_password_reset_link(email, admin_router.prefix)
    return {"detail": "Password reset link sent if the email exists in our system"}

# Create Admin (Superuser only)
@admin_router.post("/create-admin")
async def create_admin(
    data: AdminCreate,
    admin: AdminDep,
    service: AdminServiceDep
):
    if not admin.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, 
            detail="Not allowed"
        )

    await service.create_admin(data)

    return {
        "message": "Admin created successfully. Check email to make password."
    }      


@admin_router.delete("/delete/{admin_id}")
async def delete_admin(
    admin_id: str,
    current_admin: AdminDep,
    service: AdminServiceDep
):
    if not current_admin.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only superadmin allowed to deleted admin"
        )
    
    await service.delete_admin(admin_id, current_admin)
    return {"message": f"Admin {current_admin.name} is deleted successfully"}


@admin_router.get("/logout")
async def logout_admin(
    token_data: Annotated[dict, Depends(get_admin_token)]
):
    await add_jti_to_blacklist(token_data["jti"]) 
    
    return {
        "detail": "Successful Log Out"
    }


# Admin Dashboard
@admin_router.get("/dashboard")
async def admin_dashboard(admin: AdminDep):
    return {
        "message": f"Welcome {admin.name} to the admin dashboard!"
    }

# Total Users Count
@admin_router.get("/users-count")
async def get_users_count(
    user_service: UserServiceDep
):
    count = await user_service.get_users_count()
    return {"total_users": count}


# Verified Users Count
@admin_router.get("/verified-users-count")
async def get_verified_users_count(
    user_service: UserServiceDep
):
    count = await user_service.get_verified_users_count()
    return {"verified_users": count}
@admin_router.get("/users")
async def get_all_users(
    admin: AdminDep,
    user_service: UserServiceDep
):
    users = await user_service.get_all_users()
    return users


@admin_router.delete("/users/{user_id}")
async def delete_user(
    user_id: str,
    admin: AdminDep,
    user_service: UserServiceDep
):
    from uuid import UUID
    await user_service.delete_user(UUID(user_id))
    return {"message": "User deleted successfully"}


@admin_router.delete("/users/all")
async def delete_all_users(
    admin: AdminDep,
    user_service: UserServiceDep
):
    await user_service.delete_all_users()
    return {"message": "All users deleted successfully"}
