import requests
from typing import List, Dict, Any, Optional
from loguru import logger
from backend.app.config.settings import settings

class TavilySearchTool:
    @staticmethod
    def search_web(query: str, max_results: int = 4) -> Dict[str, Any]:
        api_key = settings.TAVILY_API_KEY
        if not api_key or "your_" in api_key:
            return {"error": "Tavily API key not configured."}
        try:
            url = "https://api.tavily.com/search"
            headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
            payload = {"query": query, "max_results": max_results, "include_answer": True}
            res = requests.post(url, headers=headers, json=payload, timeout=15)
            if res.status_code == 200:
                data = res.json()
                results = [
                    {"title": r.get("title"), "url": r.get("url"), "content": r.get("content")}
                    for r in data.get("results", [])
                ]
                return {"success": True, "answer": data.get("answer"), "results": results}
            else:
                return {"success": False, "error": f"Tavily returned {res.status_code}: {res.text}"}
        except Exception as e:
            logger.error(f"Tavily search failed: {e}")
            return {"success": False, "error": str(e)}
