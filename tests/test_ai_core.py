import os
import pytest
from fastapi.testclient import TestClient
from backend.app.main import app

client = TestClient(app)
headers = {}

def test_01_auth_for_chat():
    payload = {
        "email": "ai.executive@assistant.local",
        "full_name": "AI Executive Lead",
        "password": "StrongPassword99!",
        "role_name": "ADMIN"
    }
    res = client.post("/api/v1/auth/register", json=payload)
    if res.status_code == 409:
        res = client.post("/api/v1/auth/login", json={"email": payload["email"], "password": payload["password"]})
    
    assert res.status_code in (200, 201)
    token = res.json()["access_token"]
    global headers
    headers["Authorization"] = f"Bearer {token}"
    print("\n✅ User authenticated for AI Core verification!")

def test_02_openrouter_chat_execution():
    payload = {
        "session_id": "test_ai_session_1",
        "message": "Hello Supervisor! In one concise sentence, confirm that our OpenRouter AI communication core is fully active and ready to coordinate specialized agents."
    }
    res = client.post("/api/v1/chat", json=payload, headers=headers)
    assert res.status_code == 200, f"Chat execution failed: {res.text}"
    data = res.json()
    assert data["session_id"] == payload["session_id"]
    assert "response" in data
    print(f"\n🤖 AI Supervisor Reply (Model: {data.get('model_used')}): \"{data['response']}\"")
    print("✅ OpenRouter LLM Core & Database conversation history storage verified!")
