from fastapi import Header, HTTPException
from app.config import get_settings


async def require_api_key(x_api_key: str | None = Header(default=None)):
    if x_api_key != get_settings().api_key:
        raise HTTPException(status_code=401, detail="Invalid API key")
    return x_api_key
