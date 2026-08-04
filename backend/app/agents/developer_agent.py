from loguru import logger
from backend.app.tools.github_tool import GitHubTool
from backend.app.llm.client import llm_client

class DeveloperAgent:
    def run(self, instruction: str) -> str:
        logger.info(f"💻 DEVELOPER AGENT analyzing repository request: '{instruction}'")
        repos_data = GitHubTool.list_repositories(limit=5)
        if not repos_data.get("success"):
            return f"[Developer Agent] GitHub inspection noted: {repos_data.get('error')}"
        
        repos_str = "\n".join([f"- {r['full_name']} (Private: {r['private']}): {r['description'] or 'No description'}" for r in repos_data.get("repositories", [])])
        prompt = [
            {"role": "system", "content": "You are the Technical Lead Developer Agent. Summarize repository status and codebase architecture insights."},
            {"role": "user", "content": f"Request: {instruction}\n\nRepositories Found:\n{repos_str}\n\nProvide technical insights for executive engineering alignment."}
        ]
        res = llm_client.complete(messages=prompt)
        return res.get("content", "Developer analysis completed.")

developer_agent = DeveloperAgent()
