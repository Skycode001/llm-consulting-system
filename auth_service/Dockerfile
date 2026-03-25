FROM python:3.11-slim

WORKDIR /app

COPY pyproject.toml .

# Устанавливаем зависимости с фиксированной версией bcrypt
RUN pip install --no-cache-dir \
    fastapi \
    uvicorn[standard] \
    sqlalchemy \
    aiosqlite \
    pydantic[email] \
    pydantic-settings \
    python-jose[cryptography] \
    passlib[bcrypt] \
    python-multipart \
    bcrypt==4.0.1 \
    email-validator

COPY . .

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]