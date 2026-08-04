from loguru import logger
from backend.app.tools.database_tool import DatabaseAnalyticsTool
from backend.app.tools.qdrant_tool import rag_tool
from backend.app.llm.client import llm_client

class DataAnalystAgent:
    def run(self, query: str) -> str:
        logger.info(f"📊 DATA ANALYST AGENT querying business analytics: '{query}'")
        stats = DatabaseAnalyticsTool.get_project_statistics()
        rag_hits = rag_tool.search_similar(query=query, limit=2)
        rag_str = "\n".join([f"- Doc ID {r['doc_id']} ({r['title']}): {r['text']}" for r in rag_hits])
        
        prompt = [
            {"role": "system", "content": "You are the Chief Data Analyst & Business Intelligence Agent. Connect quantitative relational database statistics with qualitative RAG corporate document memories."},
            {"role": "user", "content": f"Query: {query}\n\nDatabase KPIs:\n{stats}\n\nRelevant RAG Document Excerpts:\n{rag_str}\n\nSynthesize a definitive business intelligence report."}
        ]
        res = llm_client.complete(messages=prompt)
        return res.get("content", "Analytics briefing ready.")

data_analyst_agent = DataAnalystAgent()
