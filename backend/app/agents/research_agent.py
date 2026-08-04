from typing import List, Dict, Any, Optional
from loguru import logger
from backend.app.tools.tavily_tool import TavilySearchTool
from backend.app.llm.client import llm_client

class ResearchAgent:
    def run(self, query: str, history: Optional[List[Dict[str, Any]]] = None) -> str:
        logger.info(f"🔍 RESEARCH AGENT analyzing request: '{query}'")
        
        # Build conversational context
        context_str = ""
        if history:
            last_msgs = history[-3:]
            context_str = "Recent Conversation Context:\n" + "\n".join([f"- {m.get('role', 'user')}: {m.get('content', '')}" for m in last_msgs]) + "\n\n"

        # Stage 1: Search Query Optimization & Polyglot Intent Parsing
        opt_prompt = [
            {
                "role": "system",
                "content": (
                    "You are an Expert Search Query Optimizer and Multilingual Business Linguist for an AI Executive Assistant.\n"
                    "Your mission is to inspect the user's instruction and convert it into the SINGLE MOST EFFECTIVE search engine keyword string.\n"
                    "Critical Optimization Rules:\n"
                    "1. Strip out command meta-words (e.g., 'search in web', 'look up on google', 'find me information about', 'search for').\n"
                    "2. Recognize mixed French/English/Business terminology:\n"
                    "   - 'formation' in a business or software context means 'Training Courses, Educational Certifications, Bootcamp, Tutorials'. Do NOT interpret 'formation' as physical geology or code structure!\n"
                    "   - 'stage' means 'Internship'.\n"
                    "   - 'concours' means 'Competitive Examination'.\n"
                    "3. Target the user's true educational or competitive objective (e.g., if input is 'search in web formation for python', your output must be something like: 'best Python training courses certifications online bootcamps 2026').\n"
                    "Respond ONLY with the cleaned, optimized search engine keyword query string, nothing else."
                )
            },
            {"role": "user", "content": f"{context_str}User Instruction: {query}"}
        ]
        
        opt_res = llm_client.complete(messages=opt_prompt, temperature=0.1)
        optimized_query = opt_res.get("content", "").strip()
        if not optimized_query or len(optimized_query) < 3:
            optimized_query = query.replace("search in web", "").replace("search for", "").strip()
            
        logger.info(f"⚡ RESEARCH AGENT OPTIMIZED SEARCH QUERY: '{optimized_query}' (derived from raw: '{query}')")
        
        # Stage 2: Live Search Execution via Tavily API
        search_results = TavilySearchTool.search_web(query=optimized_query)
        if not search_results.get("success"):
            return f"[Research Agent] Web search encountered an issue: {search_results.get('error')}"
        
        results_str = "\n".join([f"- **{r['title']}**: {r['content']} ([Link]({r['url']}))" for r in search_results.get("results", [])])
        
        # Stage 3: Executive Synthesis & Formatting
        synth_prompt = [
            {
                "role": "system",
                "content": (
                    "You are the specialized Senior Corporate Research Agent. Your goal is to deliver an empowering, highly practical executive briefing responding directly to what the user truly desires.\n"
                    "Guidelines:\n"
                    "- Structure your answer cleanly with Markdown headings, bullet points, and high-value recommendations.\n"
                    "- If comparing products, courses, or services, format a clean Markdown comparison table with columns like Name, Focus Area, Level, and Link/Source.\n"
                    "- Include hyperlinked citations directly from the search results.\n"
                    "- Speak directly to the user in a polished, professional tone."
                )
            },
            {"role": "user", "content": f"{context_str}Original User Request: {query}\nOptimized Search Executed: {optimized_query}\n\nLive Web Search Findings:\n{results_str}\n\nSynthesize these findings into an actionable executive briefing."}
        ]
        res = llm_client.complete(messages=synth_prompt)
        reply = res.get("content", "Research synthesis completed.")
        
        badge = f"\n\n🔍 *Web intelligence gathered via Tavily (Optimized Query: `{optimized_query}`)*"
        return reply + badge if badge not in reply else reply

research_agent = ResearchAgent()
