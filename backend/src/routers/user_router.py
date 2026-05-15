from fastapi import HTTPException
from zxcvbn import zxcvbn
from typing import Annotated

import os
import shutil
import uuid
from fastapi import APIRouter, Depends, Form, Request, File, UploadFile
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import EmailStr

from src.core.container import UserServiceDep, get_user_token, FaceServiceDep, get_alert_service
from src.service.alert_service import AlertService
from src.schemas.user_schema import UserRead, UserCreate
from src.clients.db.redis import add_jti_to_blacklist
from src.core.config import settings
import httpx

from src.core.container import templates

user_router = APIRouter(prefix="/user", tags=["Users"])


@user_router.post("/signup")
async def create_user(
    user: UserCreate,
    user_service: UserServiceDep
):
    new_user = await user_service._add_user(
        data=user.model_dump(),
        router_prefix=user_router.prefix
    )
    
    # Generate token so user can enroll face immediately
    token = user_service.auth.generate_token(new_user)
    
    return {
        "user": new_user,
        "access_token": token,
        "token_type": "bearer"
    }


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


@user_router.post("/google-auth")
async def google_auth(
    token_id: Annotated[str, Form()],
    service: UserServiceDep,
):
    """
    Verify Google ID Token and login/signup user
    """
    # 1. Verify token with Google
    async with httpx.AsyncClient() as client:
        response = await client.get(f"https://oauth2.googleapis.com/tokeninfo?id_token={token_id}")
        
    if response.status_code != 200:
        raise HTTPException(status_code=401, detail="Invalid Google Token")
        
    google_data = response.json()
    email = google_data.get("email")
    name = google_data.get("name", email.split('@')[0])
    
    if not email:
        raise HTTPException(status_code=400, detail="Email not provided by Google")

    # 2. Check if user exists, if not create
    user = await service._get_by_email(email)
    if not user:
        # Create a new user with a random password since it's social login
        user_data = {
            "email": email,
            "name": name,
            "password": str(uuid.uuid4()), # Placeholder
            "is_verified": True
        }
        user = await service._add_user(user_data, router_prefix=user_router.prefix)
    
    # 3. Generate Local Token
    access_token = service.auth.generate_token(user)
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": user
    }


### Verify User Email
@user_router.get("/verify-email")
async def verify_email(token: str, request: Request, service: UserServiceDep):

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


@user_router.post("/enroll-face")
async def enroll_face(
    service: UserServiceDep,
    face_service: FaceServiceDep,
    token_data: Annotated[dict, Depends(get_user_token)],
    file: UploadFile = File(...)
):
    user_id = token_data["id"]
    
    # Create directory if not exists
    upload_dir = "src/media/users"
    os.makedirs(upload_dir, exist_ok=True)
    
    file_path = os.path.join(upload_dir, f"{user_id}.jpg")
    
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    # Generate Embedding
    embedding = face_service.generate_embedding(file_path)
    if not embedding:
        raise HTTPException(status_code=400, detail="Could not detect face in image")
        
    user = await service._get(user_id)
    user.image_path = file_path
    user.face_embedding = embedding
    await service._update(user)
    
    return {"detail": "Face enrolled successfully", "image_path": file_path}


@user_router.post("/face-login")
async def face_login(
    email: Annotated[str, Form()],
    file: UploadFile,
    service: UserServiceDep,
    face_service: FaceServiceDep,
    alert_service: Annotated[AlertService, Depends(get_alert_service)],
):
    user = await service._get_by_email(email)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
        
    if not user.face_embedding:
        raise HTTPException(status_code=400, detail="User has no face enrolled")

    # Save temporary capture for processing
    temp_dir = "src/media/temp"
    os.makedirs(temp_dir, exist_ok=True)
    temp_path = os.path.join(temp_dir, f"login_{user.id}_{uuid.uuid4()}.jpg")
    
    # We need to read the file contents multiple times or seek(0)
    contents = await file.read()
    with open(temp_path, "wb") as buffer:
        buffer.write(contents)
    
    # 1. Similarity Check (Standard)
    similarity = face_service.verify_similarity(user.face_embedding, temp_path)
    
    # 2. AI Model Check (VisionGateModel) - if similarity is borderline or for extra security
    # Here we can also check liveness if we had a dedicated liveness model
    # For now, we'll use similarity threshold of 0.85
    
    is_allowed = similarity >= 0.85
    
    if is_allowed:
        # Success: Clear any temporary files and return token
        if os.path.exists(temp_path):
            os.remove(temp_path)
            
        token = service.auth.generate_token(user)
        return {
            "access_token": token,
            "token_type": "bearer",
            "similarity": similarity,
            "user_name": user.name,
            "message": f"Hello {user.name}"
        }
    else:
        # Failure: Log alert and send email
        # We need the file for the alert, so we create a new UploadFile from contents
        from io import BytesIO
        alert_file = UploadFile(filename=file.filename, file=BytesIO(contents))
        
        await alert_service.create_alert(
            user_email=email,
            message=f"Unauthorized face login attempt for account: {email}. Similarity: {similarity:.2f}",
            image=alert_file,
            status="UNAUTHORIZED_ACCESS"
        )
        
        # Trigger intruder alert email
        await alert_service.notification.send_intruder_alert(email, user.name)
        
        if os.path.exists(temp_path):
            os.remove(temp_path)
            
        raise HTTPException(
            status_code=401, 
            detail=f"Face verification failed. Security alert sent. Similarity: {similarity:.2f}"
        )