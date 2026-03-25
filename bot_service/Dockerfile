FROM python:3.11-slim

WORKDIR /app

COPY pyproject.toml .

RUN pip install --no-cache-dir fastapi uvicorn[standard] aiogram celery redis httpx pydantic-settings python-jose[cryptography] pytest pytest-asyncio pytest-mock fakeredis respx email-validator

COPY . .

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8001"]