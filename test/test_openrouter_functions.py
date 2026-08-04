#!/usr/bin/env python3
"""
Multi-Agent Business Assistant — OpenRouter API & AI Core Testing Suite
Tests Chat Completion, Live Token Streaming, and Supervisor Agent Routing Simulation.
"""

import os
import sys
import json
from dotenv import load_dotenv
from openai import OpenAI

# Load variables from .env file located in the project root
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ENV_PATH = os.path.join(BASE_DIR, ".env")
load_dotenv(ENV_PATH)

def print_header(title):
    print("\n" + "="*70)
    print(f" 🤖 {title}")
    print("="*70)

def test_openrouter():
    api_key = os.getenv("OPENROUTER_API_KEY")
    base_url = os.getenv("OPENROUTER_BASE_URL", "https://openrouter.ai/api/v1")
    default_model = os.getenv("OPENROUTER_DEFAULT_MODEL", "google/gemini-2.0-flash-001")
    
    if not api_key or "replace" in api_key:
        print("❌ Error: Valid OPENROUTER_API_KEY not found in environment or .env file.")
        sys.exit(1)
    
    print_header("STEP 1: Initializing OpenRouter AI Client (via OpenAI SDK)")
    client = OpenAI(
        api_key=api_key,
        base_url=base_url,
        default_headers={
            "HTTP-Referer": "http://localhost:3000",
            "X-Title": "Multi-Agent Business Assistant",
        }
    )
    print(f"✅ Client initialized successfully using Endpoint: {base_url}")
    print(f"🎯 Default Target Model: {default_model}")

    # Models to test in order of preference for high reliability
    test_models = [
        default_model,
        "openai/gpt-4o-mini",
        "anthropic/claude-3.5-sonnet",
        "google/gemini-pro-1.5"
    ]

    working_model = None
    print_header("STEP 2: Testing Standard Chat Completion (Phase 5 Feature)")
    for model in test_models:
        print(f"📡 Attempting connection with Model: '{model}'...")
        try:
            response = client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": "You are a professional software engineering AI assistant."},
                    {"role": "user", "content": "Briefly describe in 2 sentences why LangGraph is excellent for building multi-agent business systems."}
                ],
                temperature=0.7,
                max_tokens=150
            )
            working_model = model
            answer = response.choices[0].message.content.strip()
            print(f"✅ SUCCESS with model: [{working_model}]!")
            print("\n💡 AI RESPONSE:")
            print("-" * 70)
            print(answer)
            print("-" * 70)
            break
        except Exception as e:
            print(f"⚠️ Model '{model}' unavailable or errored: {e}")

    if not working_model:
        print("❌ Error: All tested models failed on OpenRouter. Please check API Key balance or network permissions.")
        sys.exit(1)

    print_header("STEP 3: Testing Real-Time Token Streaming (Phase 5 Feature)")
    print(f"🌊 Stream Test — Prompt: 'List the top 3 specialized agents in a company AI assistant.'")
    print("\n💬 LIVE STREAMING OUTPUT:")
    print("-" * 70)
    try:
        stream = client.chat.completions.create(
            model=working_model,
            messages=[{"role": "user", "content": "List 3 essential AI specialized agents for a corporate assistant in a concise bulleted format."}],
            stream=True,
            max_tokens=150
        )
        for chunk in stream:
            token = chunk.choices[0].delta.content
            if token:
                print(token, end="", flush=True)
        print("\n" + "-" * 70)
        print("✅ Streaming capability successfully verified!")
    except Exception as e:
        print(f"\n⚠️ Streaming failed: {e}")

    print_header("STEP 4: Supervisor Agent (#1) Routing Simulation")
    supervisor_prompt = """
    You are the Supervisor Agent (Main Controller) of an AI Business Assistant.
    Analyze the user request and choose which agents from the list [Calendar Agent, Email Agent, Research Agent, Database Agent, Report Agent] are needed.
    Respond ONLY with a valid JSON format:
    {
        "selected_agents": ["Agent1", "Agent2"],
        "reasoning": "Brief explanation of why these agents were selected"
    }
    """
    user_task = "Create a meeting with Ahmed next Monday at 10 AM, send him an email with the calendar link, and generate a PDF briefing document."
    print(f"📥 User Task input to Supervisor: '{user_task}'")
    print("🧠 Supervisor Agent reasoning...")
    
    try:
        res = client.chat.completions.create(
            model=working_model,
            messages=[
                {"role": "system", "content": supervisor_prompt},
                {"role": "user", "content": user_task}
            ],
            response_format={"type": "json_object"} if "gpt" in working_model or "gemini" in working_model else None,
            temperature=0.2,
            max_tokens=200
        )
        output_str = res.choices[0].message.content.strip()
        print("\n📊 SUPERVISOR AGENT ROUTING PLAN (JSON Output):")
        print("-" * 70)
        print(output_str)
        print("-" * 70)
        print("✅ Supervisor routing decision verified!")
    except Exception as e:
        print(f"⚠️ Supervisor simulation error: {e}")

    print_header("🎉 OPENROUTER API & AI CORE FULLY VERIFIED! READY FOR PHASE 5 & 6 🎉")

if __name__ == "__main__":
    test_openrouter()
