from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.alert_model import AlertModel
from src.service.notification_service import NotificationService


class AlertService:
    def __init__(
        self,
        session: AsyncSession,
        notification: NotificationService
    ):
        self.session = session
        self.notification = notification

    async def create_intruder_alert(
        self,
        user_email: str,
        user_name: str
    ):

        alert = AlertModel(
            user_email=user_email,
            message="Unauthorized access attempt detected",
            intruder_detected=True
        )

        self.session.add(alert)
        await self.session.commit()

        # Send email
        await self.notification.send_intruder_alert(
            email=user_email,
            user_name=user_name
        )

        return alert
    
    async def get_alerts(self):
        result = await self.session.execute(
            select(AlertModel)
        )

        return result.scalars().all()

    async def delete_alert(
        self,
        alert_id
    ):

        alert = await self._get(alert_id)

        if not alert:
            return None

        await self._delete(alert)

        return {
            "message": "Alert deleted successfully"
        }