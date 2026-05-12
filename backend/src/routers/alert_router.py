from uuid import UUID

from fastapi import APIRouter

from src.core.container import AlertServiceDep


alert_router = APIRouter(
    prefix="/alerts",
    tags=["Alerts"]
)


@alert_router.get("/")
async def get_alerts(
    service: AlertServiceDep
):

    return await service.get_alerts()


@alert_router.delete("/{alert_id}")
async def delete_alert(
    alert_id: UUID,
    service: AlertServiceDep
):

    return await service.delete_alert(
        alert_id
    )