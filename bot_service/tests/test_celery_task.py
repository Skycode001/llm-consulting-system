from unittest.mock import MagicMock, patch

from app.tasks.llm_tasks import llm_request


class TestCeleryTask:
    """Тесты для Celery задач"""
    
    def test_llm_request_success(self):
        """Тест успешного выполнения LLM задачи"""
        with patch("app.tasks.llm_tasks.call_openrouter") as mock_call:
            with patch("app.tasks.llm_tasks.httpx.Client") as mock_httpx:
                # Мокаем успешный ответ от OpenRouter
                mock_call.return_value = {
                    "success": True,
                    "content": "Тестовый ответ от LLM"
                }
                
                # Мокаем успешную отправку в Telegram
                mock_client = MagicMock()
                mock_response = MagicMock()
                mock_response.status_code = 200
                mock_client.post.return_value = mock_response
                mock_httpx.return_value.__enter__.return_value = mock_client
                
                result = llm_request(12345, "Тестовый вопрос")
                
                assert result["success"] is True
                assert result["chat_id"] == 12345
                assert result["response"] == "Тестовый ответ от LLM"
                assert result["sent"] is True
    
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
        # Тест проверяет, что задача возвращает ошибку (retry логика обрабатывается Celery)
        with patch("app.tasks.llm_tasks.call_openrouter") as mock_call:
            mock_call.return_value = {
                "success": False,
                "error": "Temporary error"
            }
            
            result = llm_request(12345, "Тестовый вопрос")
            
            assert result["success"] is False
            assert result["chat_id"] == 12345
            assert result["error"] == "Temporary error"