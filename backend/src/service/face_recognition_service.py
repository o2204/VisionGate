import os
import pickle
from uuid import uuid4

import face_recognition

from fastapi import (
    UploadFile,
    HTTPException,
    BackgroundTasks
)

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.user_model import UserModel
from src.models.history_model import HistoryModel
from src.service.base_service import BaseService
from src.service.alert_service import AlertService
from src.service.notification_service import NotificationService
from src.core.utils.tts_service import speak_access
from src.service.gate_service import GateService


class FaceRecognitionService(BaseService):
    def __init__(
        self,
        session: AsyncSession,
        tasks: BackgroundTasks
    ):

        super().__init__(
            HistoryModel,
            session
        )

        notification = NotificationService(
            tasks
        )

        self.alert_service = AlertService(
            session,
            notification
        )

    async def recognize_face(
        self,
        file: UploadFile
    ):

        os.makedirs(
            "captures",
            exist_ok=True
        )

        captured_image_path = (
            f"captures/"
            f"{uuid4()}_{file.filename}"
        )

        with open(
            captured_image_path,
            "wb"
        ) as buffer:

            buffer.write(
                await file.read()
            )

        image = face_recognition.load_image_file(
            captured_image_path
        )

        face_locations = (
            face_recognition.face_locations(
                image
            )
        )

        if not face_locations:

            raise HTTPException(
                status_code=400,
                detail="No face detected"
            )

        face_encodings = (
            face_recognition.face_encodings(
                image,
                face_locations
            )
        )

        unknown_encoding = (
            face_encodings[0]
        )

        result = await self.session.execute(
            select(UserModel)
        )

        users = result.scalars().all()

        for user in users:

            if not user.face_embedding:
                continue

            stored_embedding = pickle.loads(
                bytes.fromhex(
                    user.face_embedding
                )
            )

            matches = (
                face_recognition.compare_faces(
                    [stored_embedding],
                    unknown_encoding
                )
            )

            distance = (
                face_recognition.face_distance(
                    [stored_embedding],
                    unknown_encoding
                )[0]
            )

            confidence = round(
                (1 - distance) * 100,
                2
            )

        if matches[0]:
            # Open Gate
            gate_service = GateService()

            await gate_service.open_gate()

            # Speak Welcome
            speak_access(
                user.name,
                allowed=True
            )

            # Save History
            history = HistoryModel(
                user_id=user.id,
                person_name=user.name,
                dataset_image=user.image_path,
                captured_image=captured_image_path,
                confidence=confidence,
                is_real=True,
                is_allowed=True,
                status="Access Granted"
            )

            await self._add(history)

            return {
                "message": "Access Granted",
                "user": user.name,
                "confidence": confidence
            }

        speak_access(
            "Unknown",
            allowed=False
        )

        history = HistoryModel(
            user_id=users[0].id if users else None,
            person_name="Unknown",
            dataset_image=None,
            captured_image=captured_image_path,
            confidence=0,
            is_real=False,
            is_allowed=False,
            status="Access Denied"
        )

        await self._add(history)

        for user in users:

            if user.email:

                await self.alert_service.create_intruder_alert(
                    user_email=user.email,
                    user_name=user.name
                )

        raise HTTPException(
            status_code=401,
            detail="Face not recognized"
        )