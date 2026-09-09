from __future__ import annotations
import json
import httpx
from app.celery_app import celery
from app.config import get_settings
from app.db import SessionLocal
from app.models import Job

settings = get_settings()


def backoff_seconds(retry_number: int) -> int:
    return min(2 ** max(retry_number, 1), 60)


def _callback(url: str | None, body: dict):
    if not url:
        return
    try:
        httpx.post(url, json=body, timeout=5.0)
    except Exception:
        # Callback delivery is best-effort in this reference implementation.
        pass


@celery.task(bind=True, max_retries=5, name="process_integration_job")
def process_job(self, job_id: str):
    with SessionLocal() as session:
        job = session.get(Job, job_id)
        if not job:
            return {"status": "missing"}
        job.status = "processing"
        session.commit()
        payload = json.loads(job.request_json)
        callback_url = job.callback_url

    try:
        with httpx.Client(timeout=settings.request_timeout_seconds) as client:
            response = client.post(settings.upstream_api_url, json=payload)
            response.raise_for_status()
            result = response.json()
    except Exception as exc:
        if self.request.retries >= self.max_retries:
            with SessionLocal() as session:
                job = session.get(Job, job_id)
                if job:
                    job.status = "failed"
                    job.error = str(exc)[:2000]
                    session.commit()
            _callback(callback_url, {"job_id": job_id, "status": "failed", "error": str(exc)})
            raise
        raise self.retry(exc=exc, countdown=backoff_seconds(self.request.retries + 1))

    with SessionLocal() as session:
        job = session.get(Job, job_id)
        if job:
            job.status = "completed"
            job.response_json = json.dumps(result)
            job.error = None
            session.commit()
    _callback(callback_url, {"job_id": job_id, "status": "completed", "result": result})
    return {"status": "completed", "result": result}
