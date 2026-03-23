import logging

from aiogram import Router, types
from aiogram.filters import Command

from app.core.jwt import JWTExpiredError, JWTValidationError, decode_and_validate
from app.infra.redis import get_token, save_token
from app.tasks.llm_tasks import llm_request

logger = logging.getLogger(__name__)

router = Router()


@router.message(Command("start"))
async def cmd_start(message: types.Message):
    """
    Обработчик команды /start
    """
    await message.answer(
        "🤖 <b>LLM Консультант</b>\n\n"
        "Этот бот предоставляет доступ к большой языковой модели.\n\n"
        "Чтобы начать работу, необходимо:\n"
        "1. Зарегистрироваться в Auth Service через Swagger\n"
        "2. Получить JWT токен (через /login)\n"
        "3. Отправить токен командой: <code>/token &lt;JWT&gt;</code>\n\n"
        "После успешной авторизации просто отправляйте сообщения - бот ответит на них."
    )


@router.message(Command("token"))
async def cmd_token(message: types.Message):
    """
    Обработчик команды /token - сохранение JWT токена пользователя
    """
    args = message.text.split(maxsplit=1)
    
    if len(args) < 2:
        await message.answer(
            "❌ <b>Ошибка:</b> Не указан токен\n\n"
            "Использование: <code>/token &lt;JWT_TOKEN&gt;</code>\n\n"
            "Получите токен в Auth Service через POST /api/auth/login"
        )
        return
    
    jwt_token = args[1].strip()
    
    try:
        payload = decode_and_validate(jwt_token)
        user_id = payload.get("sub")
        role = payload.get("role", "user")
        
        await save_token(message.from_user.id, jwt_token)
        
        await message.answer(
            f"✅ <b>Токен сохранён</b>\n\n"
            f"👤 <b>Пользователь:</b> {user_id}\n"
            f"🔑 <b>Роль:</b> {role}\n\n"
            f"Теперь вы можете отправлять сообщения для получения ответов от LLM."
        )
        
        logger.info(
            f"Token saved for user {message.from_user.id} "
            f"(tg_id: {user_id}, role: {role})"
        )
        
    except JWTExpiredError:
        await message.answer(
            "❌ <b>Ошибка:</b> Токен истёк\n\n"
            "Пожалуйста, получите новый токен в Auth Service через POST /api/auth/login"
        )
    except JWTValidationError as e:
        await message.answer(
            f"❌ <b>Ошибка валидации токена:</b>\n\n"
            f"{str(e)}\n\n"
            "Пожалуйста, проверьте правильность токена и попробуйте снова."
        )
    except Exception:
        logger.exception("Unexpected error in /token handler")
        await message.answer(
            "❌ <b>Внутренняя ошибка сервера</b>\n\n"
            "Пожалуйста, попробуйте позже."
        )


@router.message(Command("help"))
async def cmd_help(message: types.Message):
    """
    Обработчик команды /help
    """
    await message.answer(
        "🆘 <b>Помощь</b>\n\n"
        "📌 <b>Доступные команды:</b>\n"
        "/start - Начало работы\n"
        "/token &lt;JWT&gt; - Сохранить токен авторизации\n"
        "/status - Проверить статус авторизации\n"
        "/help - Показать это сообщение\n\n"
        "📌 <b>Как получить токен:</b>\n"
        "1. Откройте Auth Service Swagger: http://localhost:8000/docs\n"
        "2. Зарегистрируйтесь через POST /api/auth/register\n"
        "3. Войдите через POST /api/auth/login\n"
        "4. Скопируйте полученный access_token\n\n"
        "📌 <b>Отправка сообщений:</b>\n"
        "Просто напишите текст, и бот отправит запрос к LLM.\n"
        "Ответ придёт через несколько секунд."
    )


@router.message(Command("status"))
async def cmd_status(message: types.Message):
    """
    Обработчик команды /status - проверка статуса авторизации
    """
    jwt_token = await get_token(message.from_user.id)
    
    if not jwt_token:
        await message.answer(
            "❌ <b>Не авторизован</b>\n\n"
            "У вас нет сохранённого токена.\n"
            "Отправьте токен командой: <code>/token &lt;JWT&gt;</code>"
        )
        return
    
    try:
        payload = decode_and_validate(jwt_token)
        user_id = payload.get("sub")
        role = payload.get("role", "user")
        
        await message.answer(
            f"✅ <b>Авторизация активна</b>\n\n"
            f"👤 <b>ID пользователя:</b> {user_id}\n"
            f"🔑 <b>Роль:</b> {role}\n"
            f"📅 <b>Токен действителен</b>"
        )
        
    except JWTExpiredError:
        await message.answer(
            "⚠️ <b>Токен истёк</b>\n\n"
            "Пожалуйста, получите новый токен в Auth Service\n"
            "и отправьте его командой: <code>/token &lt;JWT&gt;</code>"
        )
    except JWTValidationError as e:
        await message.answer(
            f"⚠️ <b>Токен невалиден</b>\n\n"
            f"{str(e)}\n\n"
            "Пожалуйста, получите новый токен и отправьте его "
            "командой: <code>/token &lt;JWT&gt;</code>"
        )


@router.message()
async def handle_message(message: types.Message):
    """
    Обработчик текстовых сообщений - отправка запроса к LLM
    """
    jwt_token = await get_token(message.from_user.id)
    
    if not jwt_token:
        await message.answer(
            "🔒 <b>Доступ запрещён</b>\n\n"
            "У вас нет сохранённого токена авторизации.\n\n"
            "Получите токен в Auth Service через Swagger:\n"
            "1. http://localhost:8000/docs\n"
            "2. POST /api/auth/register\n"
            "3. POST /api/auth/login\n"
            "4. Отправьте токен командой: <code>/token &lt;JWT&gt;</code>"
        )
        return
    
    try:
        payload = decode_and_validate(jwt_token)
        user_id = payload.get("sub")
        role = payload.get("role", "user")
        
        logger.info(
            f"Processing message from user {message.from_user.id} "
            f"(auth: {user_id}, role: {role})"
        )
        
        await message.answer(
            "🔄 <b>Запрос принят</b>\n\n"
            "Обрабатываю ваш вопрос... Ответ придёт следующим сообщением."
        )
        
        llm_request.delay(message.chat.id, message.text)
        
    except JWTExpiredError:
        await message.answer(
            "⚠️ <b>Токен истёк</b>\n\n"
            "Ваш токен авторизации истёк.\n"
            "Пожалуйста, получите новый токен в Auth Service\n"
            "и отправьте его командой: <code>/token &lt;JWT&gt;</code>"
        )
    except JWTValidationError as e:
        await message.answer(
            f"⚠️ <b>Токен невалиден</b>\n\n"
            f"{str(e)}\n\n"
            "Пожалуйста, получите новый токен в Auth Service\n"
            "и отправьте его командой: <code>/token &lt;JWT&gt;</code>"
        )
    except Exception:
        logger.exception("Unexpected error in message handler")
        await message.answer(
            "❌ <b>Внутренняя ошибка сервера</b>\n\n"
            "Пожалуйста, попробуйте позже."
        )