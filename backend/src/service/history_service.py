from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.history_model import HistoryModel
from src.schemas.history_schema import HistoryCreate
from src.core.utils.tts_service import speak_access
from src.service.base_service import BaseService


class HistoryService(BaseService):

    def __init__(self, session: AsyncSession):
        super().__init__(
            model=HistoryModel,
            session=session
        )

    async def create_history(
        self,
        data: HistoryCreate
    ):

        # TTS
        speak_access(
            name=data.person_name or "Unknown",
            allowed=data.is_allowed
        )

        # Create history object
        history = HistoryModel(
            user_id=data.user_id,
            person_name=data.person_name,
            dataset_image=data.dataset_image,
            captured_image=data.captured_image,
            confidence=data.confidence,
            is_real=data.is_real,
            is_allowed=data.is_allowed,
            status=data.status
        )

        # Save using BaseService
        history = await self._add(history)

        # Intruder alert
        if not data.is_real or not data.is_allowed:
            await self.send_intruder_alert(history)

        return history

    async def get_histories(self):

        result = await self.session.execute(
            select(HistoryModel)
            .order_by(HistoryModel.created_at.desc())
        )

        return result.scalars().all()

    async def get_denied_histories(self):

        result = await self.session.execute(
            select(HistoryModel)
            .where(HistoryModel.is_allowed.is_(False))
            .order_by(HistoryModel.created_at.desc())
        )

        return result.scalars().all()

    async def send_intruder_alert(
        self,
        history: HistoryModel
    ):

        print("WARNING: Intruder detected")

        print(
            "Captured image:",
            history.captured_image
        )