from typing import List, Dict, Any, Optional
from openai import OpenAI
from loguru import logger
from backend.app.config.settings import settings

class LLMManager:
    def __init__(self):
        self.api_key = settings.OPENROUTER_API_KEY
        self.base_url = settings.OPENROUTER_BASE_URL
        self.default_model = settings.OPENROUTER_DEFAULT_MODEL
        self.fast_model = settings.OPENROUTER_FAST_MODEL
        
        self.client = OpenAI(
            base_url=self.base_url,
            api_key=self.api_key
        )

    def complete(
        self,
        messages: List[Dict[str, Any]],
        model: Optional[str] = None,
        temperature: float = 0.7,
        tools: Optional[List[Dict[str, Any]]] = None
    ) -> Dict[str, Any]:
        target_model = model or self.default_model
        try:
            kwargs = {
                "model": target_model,
                "messages": messages,
                "temperature": temperature,
            }
            if tools:
                kwargs["tools"] = tools

            logger.debug(f"Calling OpenRouter LLM ({target_model}) with {len(messages)} messages...")
            response = self.client.chat.completions.create(**kwargs)
            message = response.choices[0].message
            return {
                "success": True,
                "model_used": target_model,
                "content": message.content or "",
                "tool_calls": getattr(message, "tool_calls", None),
                "raw_response": response
            }
        except Exception as e:
            logger.warning(f"Error calling {target_model}: {e}. Attempting fallback to {self.fast_model}...")
            try:
                kwargs["model"] = self.fast_model
                response = self.client.chat.completions.create(**kwargs)
                message = response.choices[0].message
                return {
                    "success": True,
                    "model_used": self.fast_model,
                    "content": message.content or "",
                    "tool_calls": getattr(message, "tool_calls", None),
                    "fallback_triggered": True
                }
            except Exception as e2:
                logger.error(f"Complete LLM execution failed on both models: {e2}")
                return {"success": False, "error": str(e2), "content": "I apologize, but my AI reasoning engine experienced a temporary timeout."}

llm_client = LLMManager()
