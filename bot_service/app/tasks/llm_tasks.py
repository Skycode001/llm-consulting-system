import logging
import httpx
from celery import shared_task

from app.core.config import settings
from app.services.openrouter_client import call_openrouter

logger = logging.getLogger(__name__)


@shared_task(bind=True, max_retries=3)
def llm_request(self, tg_chat_id: int, prompt: str) -> dict:
    logger.info(f"Processing LLM request for chat {tg_chat_id}")
    
    try:
        response = call_openrouter(prompt)
        
        if response.get("success"):
            logger.info(f"LLM request successful for chat {tg_chat_id}")
            
            # Отправляем ответ в Telegram
            try:
                bot_token = settings.TELEGRAM_BOT_TOKEN
                answer_text = response.get("content", "")
                
                logger.info(f"Attempting to send to Telegram chat {tg_chat_id}")
                logger.info(f"Bot token: {bot_token[:10]}...")
                
                url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
                payload = {
                    "chat_id": tg_chat_id,
                    "text": answer_text,
                    "parse_mode": "HTML"
                }
                
                with httpx.Client(timeout=30.0) as client:
                    resp = client.post(url, json=payload)
                
                logger.info(f"Telegram response status: {resp.status_code}")
                logger.info(f"Telegram response body: {resp.text[:200]}")
                
                if resp.status_code == 200:
                    logger.info(f"Response sent to Telegram chat {tg_chat_id}")
                    return {
                        "success": True,
                        "chat_id": tg_chat_id,
                        "response": answer_text,
                        "sent": True
                    }
                else:
                    logger.error(f"Failed to send to Telegram: {resp.status_code} - {resp.text}")
                    return {
                        "success": False,
                        "chat_id": tg_chat_id,
                        "error": f"Failed to send to Telegram: {resp.status_code}",
                        "response": answer_text
                    }
                    
            except Exception as e:
                logger.exception(f"Failed to send Telegram message for chat {tg_chat_id}")
                return {
                    "success": False,
                    "chat_id": tg_chat_id,
                    "error": f"Telegram send error: {str(e)}",
                    "response": response.get("content", "")
                }
        else:
            error_msg = response.get('error', 'Unknown error')
            logger.error(f"LLM request failed for chat {tg_chat_id}: {error_msg}")
            
            try:
                bot_token = settings.TELEGRAM_BOT_TOKEN
                url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
                payload = {
                    "chat_id": tg_chat_id,
                    "text": f"❌ Извините, произошла ошибка: {error_msg}",
                    "parse_mode": "HTML"
                }
                with httpx.Client(timeout=30.0) as client:
                    client.post(url, json=payload)
            except Exception:
                pass
                
            return {
                "success": False,
                "chat_id": tg_chat_id,
                "error": error_msg
            }
            
    except Exception as e:
        logger.exception(f"Unexpected error in LLM task for chat {tg_chat_id}")
        
        try:
            bot_token = settings.TELEGRAM_BOT_TOKEN
            url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
            payload = {
                "chat_id": tg_chat_id,
                "text": f"❌ Внутренняя ошибка сервера: {str(e)}",
                "parse_mode": "HTML"
            }
            with httpx.Client(timeout=30.0) as client:
                client.post(url, json=payload)
        except Exception:
            pass
            
        return {
            "success": False,
            "chat_id": tg_chat_id,
            "error": str(e)
        }