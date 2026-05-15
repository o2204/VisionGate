from datetime import timedelta
from uuid import UUID

from fastapi import BackgroundTasks, HTTPException, status 
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.user_model import UserModel
from src.core.utils.utils import decode_url_safe_token, generate_url_safe_token
from src.core.config import settings
from src.service.notification_service import NotificationService

from src.service.base_service import BaseService
from src.service.auth_service import AuthService


class UserService(BaseService):
    def __init__(self, model: UserModel, session: AsyncSession, auth_service: AuthService, tasks: BackgroundTasks):
        self.session = session
        self.model = model
        self.auth = auth_service
        self.notification_service = NotificationService(tasks)
    
    async def _add_user(self, data: dict, router_prefix: str) -> UserModel:

        exiting_user = await self._get_by_email(data["email"])
        if exiting_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email May be registered before"
            )
        
        user = self.model(
            email=data["email"],
            name=data["name"],
            password_hash=self.auth.hash_password(data["password"]),
        )

        # Add user to the database and get refreshed data
        user = await self._add(user)
        # Generate the token with user ID
        token = generate_url_safe_token({
            "id": str(user.id)
        })

        # Send registration email with the token
        await self.notification_service.send_email_with_template(
            recipients=[user.email],
            subject="Welcome to Our Service! Please Verify Your Email",
            context={
                "username": user.name,
                "verification_url": f"http://{settings.APP_DOMAIN}{router_prefix}/verify-email?token={token}"
            },
            template_name="verify_email.html"
        )
        return user
    
    async def verify_email(self, token: str) -> bool:
        token_data = decode_url_safe_token(token)
        if not token_data:
            return False
        
        user = await self._get(UUID(token_data["id"]))
        if not user:
            return False
        
        user.is_verified = True
        await self._update(user)
        return True
    
    async def _get_by_email(self, email: str) -> UserModel | None:
        return await self.session.scalar(
            select(self.model).where(self.model.email == email)
        )
    
    async def login(self, email: str, password: str) -> str: 
        user = await self._get_by_email(email)

        if not user:
            raise HTTPException(status_code=404 ,detail="user not found.")
        
        self.auth.validate_credentials(user, password)

        if not user.is_verified:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Please verify your email before logging in."
            )
        
        if not user.image_path:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Face enrollment required. Please complete your profile."
            )

        return self.auth.generate_token(user)
    
    async def send_password_reset_link(self, email, router_prefix):
        user = await self._get_by_email(email)

        if not user:
            return # Don't reveal if the email exists or not

        token = generate_url_safe_token({"id": str(user.id)}, salt="password-reset")

        await self.notification_service.send_email_with_template(
            recipients=[user.email],
            subject="VisionGate Password Reset Request",
            context={
                "username": user.name,
                "reset_url": f"http://{settings.APP_DOMAIN}{router_prefix}/reset-password-form?token={token}"
            },
            template_name="mail_password_reset.html"
        )
    
    async def reset_password(self, token: str, new_password: str) -> bool:
        token_data = decode_url_safe_token(
            token,
            salt="password-reset",
            expiry=timedelta(hours=24)
        )

        if not token_data:
            raise HTTPException(
                status_code=400,
                detail="Invalid or expired token"
            )

        user = await self._get(UUID(token_data["id"]))

        if not user:
            raise HTTPException(
                status_code=404,
                detail="User not found"
            )
        
        if len(new_password) < 8:
            raise HTTPException(
                status_code=400,
                detail="Password must be at least 8 characters long"
            )
        
        user.password_hash = self.auth.hash_password(new_password)
        await self._update(user)
        return True
    
    async def get_users_count(self) -> int:
        result = await self.session.scalar(
            select(func.count()).select_from(self.model)
        )
        return result or 0
    
    async def get_verified_users_count(self) -> int:
        result = await self.session.scalar(
            select(func.count()).select_from(self.model).where(self.model.is_verified.is_(True)) 
        )
        return result or 0

    async def update_face_image(self, user_id: UUID, image_path: str):
        user = await self._get(user_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        user.image_path = image_path
        await self._update(user)
        return user
    async def get_all_users(self) -> list[UserModel]:
        result = await self.session.scalars(select(self.model))
        return result.all()

    async def delete_user(self, user_id: UUID):
        user = await self._get(user_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        await self.session.delete(user)
        await self.session.commit()

    async def delete_all_users(self):
        from sqlalchemy import delete
        await self.session.execute(delete(self.model))
        await self.session.commit()
