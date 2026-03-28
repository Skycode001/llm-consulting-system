# LLM Consulting System — Двухсервисная система с JWT аутентификацией, Telegram-ботом и асинхронной обработкой LLM-запросов

Распределённая система, состоящая из двух логически и технически независимых сервисов. Архитектура построена по принципу разделения ответственности: Auth Service отвечает исключительно за аутентификацию и выпуск JWT-токенов, Bot Service — за предоставление функциональности LLM-консультаций через Telegram-бота с использованием асинхронной очереди задач.

## 🏗️ Архитектура проекта
```
llm-consulting-system/
├── docker-compose.yml # Оркестрация всех сервисов
├── Makefile # Утилиты для сборки и запуска
├── .gitignore # Игнорируемые файлы
├── llm-consulting-system.code-workspace 
│
├── auth_service/ # Сервис аутентификации (FastAPI)
│ ├── Dockerfile # Сборка образа Auth Service
│ ├── pyproject.toml # Зависимости (uv)
│ ├── pytest.ini # Настройки тестирования
│ ├── .env # Переменные окружения
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
│ └── tests/
│ ├── test_security.py # Модульные тесты JWT и хеширования
│ └── test_auth_integration.py # Интеграционные тесты API
│
├── bot_service/ # Сервис Telegram-бота (aiogram + Celery)
│ ├── Dockerfile # Сборка образа Bot Service (FastAPI)
│ ├── Dockerfile.celery # Сборка образа Celery worker
│ ├── Dockerfile.polling # Сборка образа для polling Telegram бота
│ ├── pyproject.toml # Зависимости (uv)
│ ├── pytest.ini # Настройки тестирования
│ ├── .env # Переменные окружения
│ ├── run_bot.py # Точка входа для запуска polling
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
│ └── tests/
│ ├── conftest.py # Фикстуры для тестов (mock_redis, mock_celery)
│ ├── test_jwt.py # Тесты JWT валидации
│ ├── test_handlers.py # Тесты обработчиков Telegram
│ ├── test_openrouter.py # Тесты OpenRouter клиента (respx)
│ ├── test_redis.py # Тесты Redis операций (fakeredis)
│ ├── test_celery_task.py # Тесты Celery задач
│ └── test_health.py # Тесты health check эндпоинтов
```


## 🔧 Технологии

| Компонент | Технология | Назначение |
|-----------|------------|------------|
| **Auth Service** | FastAPI, SQLAlchemy, SQLite | Регистрация, логин, выпуск JWT |
| **Bot Service** | aiogram | Telegram-бот |
| **Очередь задач** | Celery + RabbitMQ | Асинхронная обработка LLM-запросов |
| **Кэш/Хранилище** | Redis | Хранение JWT, привязанных к tg_user_id |
| **LLM** | OpenRouter API | Доступ к языковым моделям |
| **Контейнеризация** | Docker, Docker Compose | Запуск всех сервисов |
| **Управление зависимостями** | uv | Быстрая установка пакетов |

## 🎯 Ключевые архитектурные решения

### 1. Разделение ответственности
- **Auth Service** — только управление пользователями и выпуск JWT
- **Bot Service** — только проверка JWT и работа с Telegram
- Bot Service **не знает** о пользователях, паролях и механизмах регистрации
- Bot Service доверяет только корректно подписанному и не истёкшему JWT

### 2. JWT как единственный механизм авторизации
- Токен создаётся **только** в Auth Service
- Bot Service **только проверяет** подпись и срок действия
- JWT содержит поля: `sub` (id пользователя), `role`, `iat`, `exp`

### 3. Асинхронная обработка LLM-запросов
- Запросы к LLM **не выполняются** напрямую в хэндлерах Telegram
- Bot Service публикует задачу в RabbitMQ
- Celery worker забирает задачу, вызывает OpenRouter, отправляет ответ в Telegram

### 4. Полноценное использование RabbitMQ и Redis
- **RabbitMQ** — брокер задач Celery
- **Redis** — хранилище JWT, привязанных к Telegram user_id
- Оба сервиса реально участвуют в обработке (не «для галочки»)

## ⚙️ Установка и запуск

### Проверка доступа к Telegram API (важно для корректной работы)
```bash
curl -I https://api.telegram.org
```

### 1. Клонирование репозитория
```bash
git clone https://github.com/Skycode001/llm-consulting-system.git
cd llm-consulting-system
```
### 2. Настройка переменных окружения
Auth Service (auth_service/.env):
```bash
APP_NAME=auth-service
ENV=local
JWT_SECRET=change_me_super_secret_key_2026
JWT_ALG=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60
SQLITE_PATH=./auth.db
```

Bot Service (bot_service/.env):
```bash
APP_NAME=bot-service
ENV=local
TELEGRAM_BOT_TOKEN=ВАШ_ТОКЕН_ОТ_BOTFATHER
JWT_SECRET=change_me_super_secret_key_2026
JWT_ALG=HS256
REDIS_URL=redis://redis:6379/0
RABBITMQ_URL=amqp://guest:guest@rabbitmq:5672//
OPENROUTER_API_KEY=ВАШ_КЛЮЧ_OPENROUTER
OPENROUTER_BASE_URL=https://openrouter.ai/api/v1
OPENROUTER_MODEL=deepseek/deepseek-chat-v3.1:free #(или другая модель)
OPENROUTER_SITE_URL=https://example.com
OPENROUTER_APP_NAME=bot-service
```

### 3. Установка зависимостей (локально, для разработки)
Auth Service
```bash
cd auth_service
uv venv
source .venv/bin/activate
uv pip install -r <(uv pip compile pyproject.toml)
```

Bot Service
```bash
cd ../bot_service
uv venv
source .venv/bin/activate
uv pip install -r <(uv pip compile pyproject.toml)
```

### 4. Запуск через Docker (рекомендуется)
```bash
docker-compose up -d --build
docker-compose ps
```
Все 6 контейнеров должны быть в статусе Up:
- llm-redis
- llm-rabbitmq
- llm-auth
- llm-bot
- llm-celery
- llm-bot-polling

🐳 Основные команды Docker

| Команда | Описание |
|---------|----------|
| `docker-compose up -d --build` | Собрать образы и запустить все контейнеры в фоновом режиме |
| `docker-compose up -d` | Запустить контейнеры без пересборки |
| `docker-compose down` | Остановить и удалить все контейнеры |
| `docker-compose down -v` | Остановить контейнеры и удалить volumes (очистить данные Redis/RabbitMQ) |
| `docker-compose ps` | Показать статус всех контейнеров |
| `docker-compose logs -f` | Показать логи всех контейнеров в реальном времени |
| `docker-compose logs <service>` | Показать логи конкретного сервиса (например, `bot-polling`) |
| `docker images` | Список всех Docker образов |
| `docker system prune -a --volumes` | Удалить все неиспользуемые образы, контейнеры и volumes (полная очистка) |
| `docker rmi <image>` | Удалить конкретный образ |

### 5. Запуск тестов
Auth Service
```bash
cd auth_service
source .venv/bin/activate
pytest tests/ -v
```

Bot Service
```bash
cd bot_service
source .venv/bin/activate
pytest tests/ -v
```

### 6. Доступ к сервисам
| Сервис | URL |
|--------|-----|
| Auth Service Swagger | http://localhost:8000/docs |
| Bot Service Health | http://localhost:8001/health |
| RabbitMQ Management | http://localhost:15672 (guest/guest) |

## 🚀 Демонстрация работы

### 1. Auth Service Swagger

![Auth Service Swagger](Screenshots/Auth_service.png)

![Auth Service Swagger](Screenshots/Swagger_registration1_1.png)

![Auth Service Swagger](Screenshots/Swagger_registration1_2.png)

Логика: 
- /api/auth/register - регистрация логина и пароля
- /api/auth/login - получения токена
- Authorize - авторизация полученного токена
- /api/auth/me - информация по токену
- /health - проверка состояния

### 2. Bot Service Swagger

![Bot Service Swagger](Screenshots/Bot_service.png)

Логика:
- /health - проверка состояния
- /health/redis - проверка состояния Redis
- /health/rabbitmq - проверка состояния Rabbitmq

### 3. Telegram - работа с ботом

![Telehram](Screenshots/Bot_review.png)

Вопрос к боту 1:

![Telegram](Screenshots/Bot_question_1_2.png)

Логи Celery на вопрос 1:
```bash 
docker-compose logs -f celery-worker
```

![Telegram](Screenshots/Bot_question_1_1.png)

Вопрос к боту 2:

![Telegram](Screenshots/Bot_question_2_1.png)

Логи Celery на вопрос 2:
```bash 
docker-compose logs -f celery-worker
```

![Telegram](Screenshots/Bot_question_2_2.png)


### 4. RabbitMQ Managment

![RabbitMQ Managment](Screenshots/RabbitMQ_1.png)

![RabbitMQ Managment](Screenshots/RabbitMQ_2.png)

### 5. Тестирование auth_serice и bot_service
Auth Service
```bash
cd auth_service && source .venv/bin/activate && pytest tests/ -v
```

![Auth Tests](Screenshots/Auth_tests.png)

Bot Service
```bash
cd bot_service && source .venv/bin/activate && pytest tests/ -v
```

![Bot Tests](Screenshots/Bot_tests.png)

### 6. Docker

![Docker](Screenshots/Docker1.png)

![Docker](Screenshots/Docker2.png)

## 🔧 API Endpoints

### Auth Service

| Метод | Эндпоинт | Описание | Доступ |
|-------|----------|----------|--------|
| `POST` | `/api/auth/register` | Регистрация пользователя | Публичный |
| `POST` | `/api/auth/login` | Вход, получение JWT | Публичный |
| `GET` | `/api/auth/me` | Профиль текущего пользователя | Требует JWT |
| `GET` | `/health` | Проверка работоспособности | Публичный |

### Bot Service

| Метод | Эндпоинт | Описание | Доступ |
|-------|----------|----------|--------|
| `GET` | `/health` | Проверка работоспособности | Публичный |
| `GET` | `/health/redis` | Статус Redis | Публичный |
| `GET` | `/health/rabbitmq` | Статус RabbitMQ | Публичный |

### Telegram-бот

| Команда | Описание |
|---------|----------|
| `/start` | Приветственное сообщение, инструкция |
| `/token <JWT>` | Сохранение JWT токена в Redis |
| `/status` | Проверка статуса авторизации |
| `/help` | Справка по командам |

![Bot Help](Screenshots/Bot_help.png)

## 🔧 Форматирование и линтинг

# Auth Service
```bash
cd auth_service
ruff check .
ruff format .
```

# Bot Service
```bash
cd bot_service
ruff check .
ruff format .
```

## 🔧 Переменные окружения

### Auth Service

| Переменная | Описание | Пример |
|------------|----------|--------|
| `APP_NAME` | Название приложения | `auth-service` |
| `ENV` | Окружение | `local` |
| `JWT_SECRET` | Секретный ключ для JWT | `change_me_super_secret_key_2026` |
| `JWT_ALG` | Алгоритм JWT | `HS256` |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | Время жизни токена | `60` |
| `SQLITE_PATH` | Путь к БД | `./auth.db` |

### Bot Service

| Переменная | Описание | Пример |
|------------|----------|--------|
| `APP_NAME` | Название приложения | `bot-service` |
| `ENV` | Окружение | `local` |
| `TELEGRAM_BOT_TOKEN` | Токен от @BotFather | `1234567890:ABCdefGHIjkl...` |
| `JWT_SECRET` | Секретный ключ (должен совпадать с Auth) | `change_me_super_secret_key_2026` |
| `JWT_ALG` | Алгоритм JWT | `HS256` |
| `REDIS_URL` | URL Redis | `redis://redis:6379/0` |
| `RABBITMQ_URL` | URL RabbitMQ | `amqp://guest:guest@rabbitmq:5672//` |
| `OPENROUTER_API_KEY` | API ключ OpenRouter | `sk-or-v1-...` |
| `OPENROUTER_MODEL` | Модель LLM | `deepseek/deepseek-chat-v3.1:free` |