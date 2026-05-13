from datetime import datetime
import os
import shutil
import uuid
from typing import List
from fastapi import UploadFile, BackgroundTasks
from sqlalchemy import select, desc
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.alert_model import AlertModel
from src.models.user_model import UserModel
from src.service.notification_service import NotificationService

class AlertService:
    def __init__(self, db: AsyncSession, tasks: BackgroundTasks):
        self.db = db
        self.notification = NotificationService(tasks)

    async def create_alert(
        self, 
        user_email: str, 
        message: str, 
        image: UploadFile = None,
        status: str = "UNAUTHORIZED_ACCESS"
    ):
        # Find user if exists
        result = await self.db.execute(select(UserModel).where(UserModel.email == user_email))
        user = result.scalar_one_or_none()

        captured_image_path = None
        if image:
            # Save intruder image
            upload_dir = "src/media/alerts"
            os.makedirs(upload_dir, exist_ok=True)
            file_name = f"{uuid.uuid4()}.jpg"
            captured_image_path = os.path.join(upload_dir, file_name)
            
            with open(captured_image_path, "wb") as buffer:
                shutil.copyfileobj(image.file, buffer)

        # Create alert
        alert = AlertModel(
            user_id=user.id if user else None,
            user_email=user_email,
            user_name=user.name if user else "Unknown User",
            message=message,
            captured_image=captured_image_path,
            status=status,
            intruder_detected=True
        )

        self.db.add(alert)
        await self.db.commit()
        await self.db.refresh(alert)

        # Send Email Notification
        if user:
            # Send email with alert details
            # We can expand notification_service to handle this
            email_message = f"SECURITY ALERT: {message}\nTime: {alert.created_at.strftime('%Y-%m-%d %H:%M:%S')}\nLocation: Main Access Point"
            await self.notification.tasks.add_task(
                self.notification.fastmail.send_mail,
                self.notification.MessageSchema(
                    subject="VisionGate Security Alert!",
                    recipients=[user_email],
                    body=email_message,
                    subtype="plain"
                )
            )

        return alert

    async def get_alerts_by_user(self, email: str) -> List[AlertModel]:
        result = await self.db.execute(
            select(AlertModel)
            .where(AlertModel.user_email == email)
            .order_by(desc(AlertModel.created_at))
        )
        return result.scalars().all()