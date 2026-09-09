from typing import Any
from pydantic import AnyHttpUrl, BaseModel


class JobCreate(BaseModel):
    payload: dict[str, Any]
    callback_url: AnyHttpUrl | None = None


class JobResponse(BaseModel):
    id: str
    status: str
    idempotency_key: str
    result: dict[str, Any] | None = None
    error: str | None = None
