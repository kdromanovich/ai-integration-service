import time
from fastapi import HTTPException
from redis import Redis
from app.config import get_settings

settings = get_settings()
redis_client = Redis.from_url(settings.redis_url, decode_responses=True)


def rate_limit(identity: str) -> None:
    bucket = int(time.time() // 60)
    key = f"ratelimit:{identity}:{bucket}"
    try:
        current = redis_client.incr(key)
        if current == 1:
            redis_client.expire(key, 70)
        if current > settings.rate_limit_per_minute:
            raise HTTPException(status_code=429, detail="Rate limit exceeded")
    except HTTPException:
        raise
    except Exception:
        # Fail open if Redis is unavailable; production systems may choose a stricter policy.
        return
