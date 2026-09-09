import json
from contextlib import asynccontextmanager
from fastapi import Depends, FastAPI, Header, HTTPException
from sqlalchemy import text

from app.config import get_settings
from app.db import SessionLocal, init_db
from app.rate_limit import rate_limit, redis_client
from app.schemas import JobCreate, JobResponse
from app.security import require_api_key
from app.service import create_or_get_job, get_job
from app.tasks import process_job

settings = get_settings()


@asynccontextmanager
async def lifespan(_app: FastAPI):
    init_db()
    yield


app = FastAPI(title=settings.app_name, version="0.1.0", lifespan=lifespan)


@app.get("/health")
def health():
    with SessionLocal() as session:
        session.execute(text("SELECT 1"))
    redis_ok = True
    try:
        redis_ok = bool(redis_client.ping())
    except Exception:
        redis_ok = False
    return {"status": "ok", "database": "ok", "redis": "ok" if redis_ok else "degraded"}


@app.post("/demo/upstream")
def demo_upstream(payload: dict):
    return {"accepted": True, "echo": payload}


@app.post("/v1/jobs", response_model=JobResponse, dependencies=[Depends(require_api_key)])
def create_job(
    payload: JobCreate,
    idempotency_key: str = Header(alias="Idempotency-Key", min_length=8, max_length=120),
):
    rate_limit("api")
    job, created = create_or_get_job(idempotency_key, payload.payload, str(payload.callback_url) if payload.callback_url else None)
    if created:
        process_job.delay(job.id)
    result = json.loads(job.response_json) if job.response_json else None
    return JobResponse(id=job.id, status=job.status, idempotency_key=job.idempotency_key, result=result, error=job.error)


@app.get("/v1/jobs/{job_id}", response_model=JobResponse, dependencies=[Depends(require_api_key)])
def job_status(job_id: str):
    job = get_job(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    return JobResponse(
        id=job.id,
        status=job.status,
        idempotency_key=job.idempotency_key,
        result=json.loads(job.response_json) if job.response_json else None,
        error=job.error,
    )
