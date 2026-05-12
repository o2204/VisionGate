from fastapi import APIRouter

from src.service.gate_service import GateService


gate_router = APIRouter(
    prefix="/gate",
    tags=["Gate Control"]
)


@gate_router.post("/open")
async def open_gate():

    service = GateService()
    return await service.open_gate()


@gate_router.post("/lock")
async def lock_gate():

    service = GateService()

    return await service.lock_gate()