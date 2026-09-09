from __future__ import annotations

import time
from uuid import uuid4

import httpx

BASE_URL = "http://127.0.0.1:8002"
HEADERS = {"x-api-key": "change-me"}


def wait_for_api(timeout_seconds: int = 90) -> None:
    deadline = time.time() + timeout_seconds
    last_error: Exception | None = None
    while time.time() < deadline:
        try:
            response = httpx.get(f"{BASE_URL}/health", timeout=2.0)
            if response.status_code == 200 and response.json().get("database") == "ok":
                return
        except Exception as exc:
            last_error = exc
        time.sleep(1)
    raise RuntimeError(f"API did not become ready: {last_error}")


def main() -> None:
    wait_for_api()

    unauthorized = httpx.post(
        f"{BASE_URL}/v1/jobs",
        headers={"Idempotency-Key": "unauthorized-smoke"},
        json={"payload": {"task": "enrich"}},
        timeout=5.0,
    )
    assert unauthorized.status_code in {401, 403}, unauthorized.text

    idempotency_key = f"smoke-{uuid4()}"
    headers = {**HEADERS, "Idempotency-Key": idempotency_key}
    payload = {"payload": {"customer_id": 42, "task": "enrich"}}

    first = httpx.post(f"{BASE_URL}/v1/jobs", headers=headers, json=payload, timeout=5.0)
    first.raise_for_status()
    first_body = first.json()
    job_id = first_body["id"]

    duplicate = httpx.post(f"{BASE_URL}/v1/jobs", headers=headers, json=payload, timeout=5.0)
    duplicate.raise_for_status()
    assert duplicate.json()["id"] == job_id

    deadline = time.time() + 45
    final = None
    while time.time() < deadline:
        status = httpx.get(f"{BASE_URL}/v1/jobs/{job_id}", headers=HEADERS, timeout=5.0)
        status.raise_for_status()
        final = status.json()
        if final["status"] in {"completed", "failed"}:
            break
        time.sleep(1)

    assert final is not None
    assert final["status"] == "completed", final
    assert final["result"]["accepted"] is True
    assert final["result"]["echo"] == payload["payload"]
    print(f"Docker smoke test completed job {job_id} through API -> Redis/Celery -> worker -> upstream -> PostgreSQL")


if __name__ == "__main__":
    main()
