# AI Integration Service

Backend интеграций на **Python, FastAPI, PostgreSQL, Redis и Celery**.

Сервис принимает задачи через API, защищается API-ключом, использует `Idempotency-Key`, сохраняет состояние в PostgreSQL, отправляет задачу worker-у через Redis/Celery, повторяет временно неудачные запросы с exponential backoff и позволяет получать статус выполнения.

## Что демонстрирует

- FastAPI и REST API;
- PostgreSQL / SQLAlchemy;
- Redis;
- Celery workers;
- очереди и фоновые задачи;
- retries и обработку ошибок;
- idempotency;
- webhook callback;
- Docker Compose;
- тесты и CI.

По умолчанию `UPSTREAM_API_URL` направлен на встроенный demo endpoint, поэтому весь сценарий можно запустить локально без стороннего сервиса.
