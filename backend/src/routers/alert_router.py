from typing import Annotated, List
from fastapi import APIRouter, Depends, UploadFile, File, Form, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession

from src.clients.db.database import get_db
from src.service.alert_service import AlertService
from src.schemas.user_schema import UserRead # Using standard schemas where possible

alert_router = APIRouter(prefix="/alerts", tags=["Alerts"])

@alert_router.post("/")
async def create_security_alert(
    background_tasks: BackgroundTasks,
    email: Annotated[str, Form()],
    message: Annotated[str, Form()],
    status: Annotated[str, Form()] = "UNAUTHORIZED_ACCESS",
    image: UploadFile = File(None),
    db: AsyncSession = Depends(get_db)
):
    service = AlertService(db, background_tasks)
    alert = await service.create_alert(
        user_email=email,
        message=message,
        image=image,
        status=status
    )
    return alert

@alert_router.get("/{email}")
async def get_alerts(
    email: str,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db)
):
    service = AlertService(db, background_tasks)
    alerts = await service.get_alerts_by_user(email)
    return alerts