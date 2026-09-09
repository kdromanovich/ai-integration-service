# AI Integration Service

[![CI](https://github.com/kdromanovich/ai-integration-service/actions/workflows/ci.yml/badge.svg)](https://github.com/kdromanovich/ai-integration-service/actions/workflows/ci.yml)

Reference-backend интеграций на **Python, FastAPI, PostgreSQL, Redis и Celery**.

Сервис принимает задачи через API, защищается API-ключом, использует `Idempotency-Key`, сохраняет состояние в PostgreSQL, отправляет задачу worker-у через Redis/Celery, повторяет временно неудачные запросы с exponential backoff и позволяет получать статус выполнения.

## Что демонстрирует

- FastAPI и REST API;
- PostgreSQL / SQLAlchemy;
- Redis;
- Celery workers;
- реальные очереди и фоновые задачи;
- retries и обработку ошибок;
- idempotency;
- webhook callback;
- Docker Compose;
- unit-тесты и end-to-end smoke test в CI.

## End-to-end проверка

GitHub Actions поднимает полный Docker Compose stack: FastAPI, PostgreSQL, Redis и настоящий Celery worker. Smoke-тест проверяет авторизацию, создаёт задачу, повторно отправляет тот же `Idempotency-Key`, затем ждёт, пока worker получит задачу через Redis/Celery, вызовет demo upstream и сохранит результат в PostgreSQL.

По умолчанию `UPSTREAM_API_URL` направлен на встроенный demo endpoint, поэтому весь сценарий можно запустить локально без стороннего сервиса.

## Статус проекта

Это portfolio/reference implementation, а не заявление о deployed customer production system. Для реального internet-facing production потребуются миграции, tracing, управление секретами, TLS и дополнительные ограничения для callbacks/rate limiting.
