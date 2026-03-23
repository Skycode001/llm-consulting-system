import respx
from httpx import Response

from app.core.config import settings
from app.services.openrouter_client import call_openrouter


class TestOpenRouterClient:
    """Тесты для OpenRouter клиента"""
    
    @respx.mock
    def test_call_openrouter_success(self):
        """Тест успешного вызова OpenRouter"""
        mock_response = {
            "choices": [
                {
                    "message": {
                        "content": "Это ответ от тестовой LLM"
                    }
                }
            ]
        }
        
        url = f"{settings.OPENROUTER_BASE_URL}/chat/completions"
        respx.post(url).mock(return_value=Response(200, json=mock_response))
        
        result = call_openrouter("Привет, как дела?")
        
        assert result["success"] is True
        assert result["content"] == "Это ответ от тестовой LLM"
    
    @respx.mock
    def test_call_openrouter_with_custom_model(self):
        """Тест вызова OpenRouter с кастомной моделью"""
        mock_response = {
            "choices": [
                {
                    "message": {
                        "content": "Ответ от кастомной модели"
                    }
                }
            ]
        }
        
        url = f"{settings.OPENROUTER_BASE_URL}/chat/completions"
        respx.post(url).mock(return_value=Response(200, json=mock_response))
        
        result = call_openrouter("Тест", model="gpt-4o")
        
        assert result["success"] is True
        assert result["content"] == "Ответ от кастомной модели"
    
    @respx.mock
    def test_call_openrouter_empty_response(self):
        """Тест вызова OpenRouter с пустым ответом"""
        mock_response = {"choices": []}
        
        url = f"{settings.OPENROUTER_BASE_URL}/chat/completions"
        respx.post(url).mock(return_value=Response(200, json=mock_response))
        
        result = call_openrouter("Привет")
        
        assert result["success"] is False
        assert "Empty response" in result["error"]
    
    @respx.mock
    def test_call_openrouter_api_error(self):
        """Тест вызова OpenRouter с ошибкой API"""
        url = f"{settings.OPENROUTER_BASE_URL}/chat/completions"
        respx.post(url).mock(return_value=Response(500, json={"error": "Internal server error"}))
        
        result = call_openrouter("Привет")
        
        assert result["success"] is False
        assert "500" in result["error"]
    
    @respx.mock
    def test_call_openrouter_timeout(self):
        """Тест вызова OpenRouter с таймаутом"""
        url = f"{settings.OPENROUTER_BASE_URL}/chat/completions"
        respx.post(url).mock(side_effect=TimeoutError())
        
        result = call_openrouter("Привет")
        
        assert result["success"] is False
        assert "timeout" in result["error"].lower()
    
    @respx.mock
    def test_call_openrouter_network_error(self):
        """Тест вызова OpenRouter с сетевой ошибкой"""
        url = f"{settings.OPENROUTER_BASE_URL}/chat/completions"
        respx.post(url).mock(side_effect=Exception("Network error"))
        
        result = call_openrouter("Привет")
        
        assert result["success"] is False
        assert "Network error" in result["error"]
    
    def test_call_openrouter_with_real_prompt_format(self):
        """Тест проверки формата промпта"""
        with respx.mock:
            url = f"{settings.OPENROUTER_BASE_URL}/chat/completions"
            respx.post(url).mock(return_value=Response(
                200, 
                json={
                    "choices": [{"message": {"content": "Ответ"}}]
                }
            ))
            
            result = call_openrouter("Тестовый вопрос")
            
            assert result["success"] is True
            assert len(respx.calls) == 1
            request_json = respx.calls[0].request.json()
            assert request_json["messages"][0]["role"] == "user"
            assert request_json["messages"][0]["content"] == "Тестовый вопрос"