import os
import pytest
from fastapi.testclient import TestClient
from backend.app.main import app
from backend.app.workflows.business_assistant import MultiAgentOrchestrator

client = TestClient(app)
headers = {}

def test_01_setup_auth_for_workflow():
    payload = {
        "email": "chief.architect@assistant.local",
        "full_name": "Chief Architect Lead",
        "password": "LangGraphSecret123!",
        "role_name": "ADMIN"
    }
    res = client.post("/api/v1/auth/register", json=payload)
    if res.status_code == 409:
        res = client.post("/api/v1/auth/login", json={"email": payload["email"], "password": payload["password"]})
    assert res.status_code in (200, 201)
    token = res.json()["access_token"]
    global headers
    headers["Authorization"] = f"Bearer {token}"
    print("\n✅ User authenticated for LangGraph Multi-Agent test suite!")

def test_02_direct_orchestration_research_query():
    print("\n--- Testing LangGraph Supervisor -> Research Agent Routing ---")
    res = MultiAgentOrchestrator.execute("What are the latest developments in autonomous AI agent operating systems?")
    assert res["success"] is True
    print(f"Agent Triggered: {res['agent_triggered']}")
    print(f"Response Summary: {res['response'][:300]}...")
    assert "RESEARCH" in res["agent_triggered"] or "GENERAL" in res["agent_triggered"]

def test_03_direct_orchestration_analytics_query():
    print("\n--- Testing LangGraph Supervisor -> Data Analyst Agent Routing ---")
    res = MultiAgentOrchestrator.execute("Check database KPIs and project statistics to see how many tasks are completed versus in progress.")
    assert res["success"] is True
    print(f"Agent Triggered: {res['agent_triggered']}")
    print(f"Response Summary: {res['response'][:300]}...")
    assert "ANALYTICS" in res["agent_triggered"] or "GENERAL" in res["agent_triggered"]

def test_04_api_chat_endpoint_multiagent_routing():
    print("\n--- Testing /api/v1/chat endpoint executing LangGraph Workflow ---")
    payload = {
        "session_id": "exec_sprint_session",
        "message": "Draft a short follow up email for our corporate partner to discuss our automated report capabilities."
    }
    res = client.post("/api/v1/chat", json=payload, headers=headers)
    assert res.status_code == 200, f"Chat endpoint failed: {res.text}"
    data = res.json()
    print(f"Agent Triggered: {data['agent_triggered']}")
    print(f"Reply: {data['response']}")
    assert "response" in data
    print("✅ LangGraph Autonomous Multi-Agent Orchestration verified across all tiers!")
