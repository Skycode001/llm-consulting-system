import logging
from typing import Any, Dict, Optional

import httpx

from app.core.config import settings

logger = logging.getLogger(__name__)


def call_openrouter(prompt: str, model: Optional[str] = None) -> Dict[str, Any]:
    """
    Вызов OpenRouter API для получения ответа от LLM
    
    Args:
        prompt: текст запроса пользователя
        model: модель для использования (если не указана, берется из настроек)
        
    Returns:
        dict с полями:
            - success: bool
            - content: str (если success=True)
            - error: str (если success=False)
    """
    model = model or settings.OPENROUTER_MODEL
    
    headers = {
        "Authorization": f"Bearer {settings.OPENROUTER_API_KEY}",
        "Content-Type": "application/json",
        "HTTP-Referer": settings.OPENROUTER_SITE_URL,
        "X-Title": settings.OPENROUTER_APP_NAME,
    }
    
    payload = {
        "model": model,
        "messages": [
            {
                "role": "user",
                "content": prompt
            }
        ],
        "max_tokens": 1000,
        "temperature": 0.7,
    }
    
    try:
        with httpx.Client(timeout=60.0) as client:
            response = client.post(
                f"{settings.OPENROUTER_BASE_URL}/chat/completions",
                headers=headers,
                json=payload
            )
            
            if response.status_code == 200:
                data = response.json()
                content = data.get("choices", [{}])[0].get("message", {}).get("content", "")
                
                if content:
                    return {
                        "success": True,
                        "content": content
                    }
                else:
                    return {
                        "success": False,
                        "error": "Empty response from OpenRouter"
                    }
            else:
                logger.error(f"OpenRouter API error: {response.status_code} - {response.text}")
                return {
                    "success": False,
                    "error": f"OpenRouter API returned {response.status_code}"
                }
                
    except httpx.TimeoutException:
        logger.error("OpenRouter API timeout")
        return {
            "success": False,
            "error": "Request timeout"
        }
    except httpx.RequestError as e:
        logger.error(f"OpenRouter request error: {e}")
        return {
            "success": False,
            "error": f"Network error: {str(e)}"
        }
    except Exception as e:
        logger.exception("Unexpected error in OpenRouter client")
        return {
            "success": False,
            "error": f"Internal error: {str(e)}"
        }