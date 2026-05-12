from pydantic import BaseModel


class GateResponse(BaseModel):

    success: bool
    message: str
    gate_status: str