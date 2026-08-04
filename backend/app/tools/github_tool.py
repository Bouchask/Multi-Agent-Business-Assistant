import requests
from typing import Dict, Any, List
from loguru import logger
from backend.app.config.settings import settings

class GitHubTool:
    @staticmethod
    def list_repositories(limit: int = 5) -> Dict[str, Any]:
        token = settings.GITHUB_PERSONAL_ACCESS_TOKEN
        if not token or "github_pat_" not in token:
            return {"success": False, "error": "GitHub token not configured properly."}
        try:
            url = f"https://api.github.com/user/repos?per_page={limit}&sort=updated"
            headers = {"Authorization": f"Bearer {token}", "Accept": "application/vnd.github.v3+json"}
            res = requests.get(url, headers=headers, timeout=15)
            if res.status_code == 200:
                repos = [
                    {"name": r["name"], "full_name": r["full_name"], "private": r["private"], "html_url": r["html_url"], "description": r["description"]}
                    for r in res.json()
                ]
                return {"success": True, "repositories": repos}
            else:
                return {"success": False, "error": f"GitHub returned {res.status_code}: {res.text}"}
        except Exception as e:
            logger.error(f"GitHub API check failed: {e}")
            return {"success": False, "error": str(e)}
