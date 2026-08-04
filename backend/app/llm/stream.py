from typing import List, Dict, Any, Generator
from openai import OpenAI
from loguru import logger
from backend.app.config.settings import settings

def stream_chat_completion(messages: List[Dict[str, Any]], model: str = None) -> Generator[str, None, None]:
    client = OpenAI(
        base_url=settings.OPENROUTER_BASE_URL,
        api_key=settings.OPENROUTER_API_KEY
    )
    target_model = model or settings.OPENROUTER_DEFAULT_MODEL
    
    try:
        response = client.chat.completions.create(
            model=target_model,
            messages=messages,
            temperature=0.7,
            stream=True
        )
        for chunk in response:
            delta = chunk.choices[0].delta
            if getattr(delta, "content", None):
                yield delta.content
    except Exception as e:
        logger.error(f"Error during streaming completion: {e}")
        yield f"\n[Streaming error: {str(e)}]"
