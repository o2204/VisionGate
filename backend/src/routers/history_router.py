from fastapi import APIRouter

from src.core.container import HistoryServiceDep
from src.schemas.history_schema import HistoryCreate, HistoryRead


history_router = APIRouter(
    prefix="/history",
    tags=["History"]
)


@history_router.post("/", response_model=HistoryRead)
async def create_history(
    data: HistoryCreate,
    service: HistoryServiceDep
):
    return await service.create_history(data)


@history_router.get("/", response_model=list[HistoryRead])
async def get_histories(
    service: HistoryServiceDep
):
    return await service.get_histories()


@history_router.get("/denied", response_model=list[HistoryRead])
async def get_denied_histories(
    service: HistoryServiceDep
):
    return await service.get_denied_histories()