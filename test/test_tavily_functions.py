#!/usr/bin/env python3
"""
Multi-Agent Business Assistant — Tavily AI Search Testing Suite
Tests live internet research capabilities (search, extraction, and AI synthesized answers) using Tavily API.
"""

import os
import sys
from dotenv import load_dotenv
from tavily import TavilyClient

# Load variables from .env file located in the project root
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ENV_PATH = os.path.join(BASE_DIR, ".env")
load_dotenv(ENV_PATH)

def print_header(title):
    print("\n" + "="*70)
    print(f" 🔍 {title}")
    print("="*70)

def test_tavily():
    api_key = os.getenv("TAVILY_API_KEY")
    if not api_key or api_key == "replace-with-your-key":
        print("❌ Error: Valid TAVILY_API_KEY not found in environment or .env file.")
        sys.exit(1)
    
    print_header("STEP 1: Initializing Tavily AI Research Client")
    client = TavilyClient(api_key=api_key)
    print("✅ Client initialized successfully with API key from .env!")

    print_header("STEP 2: Testing Live Web Research Query ('latest AI news')")
    query = "latest AI news and LLM breakthroughs 2026"
    print(f"📡 Executing search query: '{query}' with AI answer generation enabled...")
    
    response = client.search(
        query=query,
        search_depth="advanced",
        max_results=3,
        include_answer=True
    )

    print("\n💡 AI SYNTHESIZED ANSWER:")
    print("-" * 70)
    print(response.get("answer", "(No summary answer returned)"))
    print("-" * 70)

    print("\n🔗 TOP SEARCH RESULTS (Citations & Sources):")
    for i, res in enumerate(response.get("results", []), 1):
        title = res.get("title", "(No Title)")
        url = res.get("url", "")
        content = res.get("content", "")[:180] + "..."
        score = res.get("score", 0.0)
        print(f"\n [{i}] {title} (Relevance Score: {score:.2f})")
        print(f"     URL: {url}")
        print(f"     SNIPPET: {content}")

    print_header("STEP 3: Testing Q&A Context Extraction for Agents")
    qa_query = "What is LangGraph and how does it help build multi-agent AI systems?"
    print(f"🤖 Querying Tavily Context Engine: '{qa_query}'...")
    context = client.get_search_context(query=qa_query, max_results=2)
    print(f"📄 Retrieved clean AI Research Context: {len(context)} characters of structured text loaded.")
    print("✅ Context extraction verified!")

    print_header("🎉 TAVILY API FULLY VERIFIED! READY FOR RESEARCH AGENT (#2) 🎉")

if __name__ == "__main__":
    test_tavily()
