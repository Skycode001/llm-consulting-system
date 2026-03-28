# LLM Consulting System — Двухсервисная система с JWT аутентификацией, Telegram-ботом и асинхронной обработкой LLM-запросов

Распределённая система, состоящая из двух логически и технически независимых сервисов. Архитектура построена по принципу разделения ответственности: Auth Service отвечает исключительно за аутентификацию и выпуск JWT-токенов, Bot Service — за предоставление функциональности LLM-консультаций через Telegram-бота с использованием асинхронной очереди задач.

## 🏗️ Архитектура проекта
```
llm-consulting-system/
├── auth_service/ # Сервис аутентификации (FastAPI)
│ ├── app/
│ │ ├── main.py # Точка входа FastAPI, lifespan, health check
│ │ ├── core/
│ │ │ ├── config.py # Настройки через pydantic-settings
│ │ │ ├── security.py # JWT создание/проверка, хеширование паролей
│ │ │ └── exceptions.py # Кастомные HTTP исключения (409, 401, 404, 403)
│ │ ├── db/
│ │ │ ├── base.py # SQLAlchemy DeclarativeBase
│ │ │ ├── session.py # Асинхронный engine и sessionmaker
│ │ │ └── models.py # ORM-модель User
│ │ ├── schemas/
│ │ │ ├── auth.py # RegisterRequest, TokenResponse
│ │ │ └── user.py # UserPublic (без password_hash)
│ │ ├── repositories/
│ │ │ └── users.py # Репозиторий: get_by_id, get_by_email, create
│ │ ├── usecases/
│ │ │ └── auth.py # Бизнес-логика: register, login, get_current_user
│ │ └── api/
│ │ ├── deps.py # Зависимости: get_db, get_current_user
│ │ ├── routes_auth.py # Эндпоинты /auth/register, /auth/login, /auth/me
│ │ └── router.py # Сборка роутеров
│ ├── tests/ # Модульные и интеграционные тесты
│ ├── pyproject.toml # Зависимости (uv)
│ └── .env # Переменные окружения
│
├── bot_service/ # Сервис Telegram-бота (aiogram + Celery)
│ ├── app/
│ │ ├── main.py # FastAPI для health checks
│ │ ├── core/
│ │ │ ├── config.py # Настройки: Telegram, JWT, Redis, RabbitMQ, OpenRouter
│ │ │ └── jwt.py # Только проверка JWT (не создаёт токены)
│ │ ├── infra/
│ │ │ ├── redis.py # Redis клиент (сохранение JWT по tg_user_id)
│ │ │ └── celery_app.py # Celery приложение с RabbitMQ брокером
│ │ ├── tasks/
│ │ │ └── llm_tasks.py # Celery задача: вызов OpenRouter и отправка ответа
│ │ ├── services/
│ │ │ └── openrouter_client.py # Клиент для OpenRouter API
│ │ ├── bot/
│ │ │ ├── dispatcher.py # Создание Bot и Dispatcher
│ │ │ └── handlers.py # Обработчики: /start, /token, /status, текстовые сообщения
│ │ └── api/
│ │ └── health.py # Health check эндпоинты
│ ├── tests/ # Тесты: JWT, handlers, OpenRouter, Redis, Celery
│ ├── run_bot.py # Точка входа для запуска polling
│ ├── celery_worker.py # Точка входа для Celery worker
│ ├── pyproject.toml # Зависимости (uv)
│ └── .env # Переменные окружения
│
├── docker-compose.yml # Оркестрация всех сервисов
└── .gitignore # Игнорируемые файлы
```