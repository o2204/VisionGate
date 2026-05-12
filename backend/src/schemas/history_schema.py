from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


class HistoryCreate(BaseModel):
    user_id: UUID
    person_name: str | None = None
    dataset_image: str | None = None
    captured_image: str
    confidence: float | None = None
    is_real: bool = True
    is_allowed: bool = False
    status: str


class HistoryRead(BaseModel):
    id: UUID
    person_name: str | None
    dataset_image: str | None
    captured_image: str
    confidence: float | None
    is_real: bool
    is_allowed: bool
    status: str
    created_at: datetime

    class Config:
        from_attributes = True