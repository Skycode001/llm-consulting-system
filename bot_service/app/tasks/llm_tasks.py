import logging

from celery import shared_task

from app.services.openrouter_client import call_openrouter

logger = logging.getLogger(__name__)


@shared_task(bind=True, max_retries=3)
def llm_request(self, tg_chat_id: int, prompt: str) -> dict:
    """
    Celery задача для выполнения запроса к LLM через OpenRouter
    
    Args:
        tg_chat_id: ID чата в Telegram для отправки ответа
        prompt: текст запроса пользователя
        
    Returns:
        dict с результатом или ошибкой
    """
    logger.info(f"Processing LLM request for chat {tg_chat_id}")
    
    try:
        response = call_openrouter(prompt)
        
        if response.get("success"):
            logger.info(f"LLM request successful for chat {tg_chat_id}")
            return {
                "success": True,
                "chat_id": tg_chat_id,
                "response": response.get("content", "")
            }
        else:
            logger.error(f"LLM request failed for chat {tg_chat_id}: {response.get('error')}")
            return {
                "success": False,
                "chat_id": tg_chat_id,
                "error": response.get("error", "Unknown error")
            }
            
    except Exception as e:
        logger.exception(f"Unexpected error in LLM task for chat {tg_chat_id}")
        return {
            "success": False,
            "chat_id": tg_chat_id,
            "error": str(e)
        }