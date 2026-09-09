import json
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from app.db import SessionLocal
from app.models import Job


def create_or_get_job(idempotency_key: str, payload: dict, callback_url: str | None) -> tuple[Job, bool]:
    with SessionLocal() as session:
        existing = session.scalar(select(Job).where(Job.idempotency_key == idempotency_key))
        if existing:
            session.expunge(existing)
            return existing, False
        job = Job(idempotency_key=idempotency_key, request_json=json.dumps(payload), callback_url=callback_url)
        session.add(job)
        try:
            session.commit()
        except IntegrityError:
            session.rollback()
            existing = session.scalar(select(Job).where(Job.idempotency_key == idempotency_key))
            if not existing:
                raise
            session.expunge(existing)
            return existing, False
        session.refresh(job)
        session.expunge(job)
        return job, True


def get_job(job_id: str) -> Job | None:
    with SessionLocal() as session:
        job = session.get(Job, job_id)
        if job:
            session.expunge(job)
        return job
