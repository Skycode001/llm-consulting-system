from unittest.mock import patch

from app.tasks.llm_tasks import llm_request


class TestCeleryTask:
    """Тесты для Celery задач"""
    
    def test_llm_request_success(self):
        """Тест успешного выполнения LLM задачи"""
        with patch("app.tasks.llm_tasks.call_openrouter") as mock_call:
            mock_call.return_value = {
                "success": True,
                "content": "Тестовый ответ от LLM"
            }
            
            result = llm_request(12345, "Тестовый вопрос")
            
            assert result["success"] is True
            assert result["chat_id"] == 12345
            assert result["response"] == "Тестовый ответ от LLM"
    
    def test_llm_request_failure(self):
        """Тест неудачного выполнения LLM задачи"""
        with patch("app.tasks.llm_tasks.call_openrouter") as mock_call:
            mock_call.return_value = {
                "success": False,
                "error": "OpenRouter API error"
            }
            
            result = llm_request(12345, "Тестовый вопрос")
            
            assert result["success"] is False
            assert result["chat_id"] == 12345
            assert result["error"] == "OpenRouter API error"
    
    def test_llm_request_exception(self):
        """Тест обработки исключения в LLM задаче"""
        with patch("app.tasks.llm_tasks.call_openrouter") as mock_call:
            mock_call.side_effect = Exception("Unexpected error")
            
            result = llm_request(12345, "Тестовый вопрос")
            
            assert result["success"] is False
            assert result["chat_id"] == 12345
            assert "Unexpected error" in result["error"]
    
    def test_llm_request_retry_on_failure(self):
        """Тест повторной попытки при ошибке"""
        with patch("app.tasks.llm_tasks.call_openrouter") as mock_call:
            mock_call.return_value = {
                "success": False,
                "error": "Temporary error"
            }
            
            result = llm_request(12345, "Тестовый вопрос")
            
            assert result["success"] is False
            assert result["chat_id"] == 12345
            assert result["error"] == "Temporary error"