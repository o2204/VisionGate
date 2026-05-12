from src.clients.hardware.gate_client import GateClient


class GateService:

    async def open_gate(self):

        GateClient.open_gate()

        return {
            "success": True,
            "message": "Gate opened successfully",
            "gate_status": "OPEN"
        }

    async def lock_gate(self):

        GateClient.lock_gate()

        return {
            "success": True,
            "message": "Gate locked successfully",
            "gate_status": "LOCKED"
        }