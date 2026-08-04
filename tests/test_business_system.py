import os
import pytest
from datetime import datetime, timedelta
from fastapi.testclient import TestClient
from backend.app.main import app

client = TestClient(app)
headers = {}

def test_01_setup_auth():
    payload = {
        "email": "manager@assistant.local",
        "full_name": "Project Manager",
        "password": "SecurePassword123!",
        "role_name": "MANAGER"
    }
    response = client.post("/api/v1/auth/register", json=payload)
    if response.status_code == 409:
        response = client.post("/api/v1/auth/login", json={"email": payload["email"], "password": payload["password"]})
    
    assert response.status_code in (200, 201), f"Auth failed: {response.text}"
    token = response.json()["access_token"]
    global headers
    headers["Authorization"] = f"Bearer {token}"
    print("\n✅ Auth initialized for Business System Test Suite!")

def test_02_create_and_get_project():
    payload = {
        "name": "Q3 Strategic AI Expansion",
        "description": "Integrating multi-agent productivity workflows across corporate divisions.",
        "status": "ACTIVE"
    }
    res = client.post("/api/v1/projects", json=payload, headers=headers)
    assert res.status_code == 201, f"Create project failed: {res.text}"
    data = res.json()
    assert data["name"] == payload["name"]
    project_id = data["id"]
    os.environ["TEST_PROJECT_ID"] = str(project_id)
    
    list_res = client.get("/api/v1/projects", headers=headers)
    assert list_res.status_code == 200
    assert any(p["id"] == project_id for p in list_res.json())
    print(f"✅ Created & Verified Project: '{payload['name']}' (ID: {project_id})")

def test_03_create_task_under_project():
    project_id = int(os.environ.get("TEST_PROJECT_ID"))
    payload = {
        "title": "Configure OpenRouter Supervisor pipeline",
        "description": "Set up LangGraph conditional edges and tools.",
        "status": "IN_PROGRESS",
        "priority": "HIGH",
        "project_id": project_id
    }
    res = client.post("/api/v1/tasks", json=payload, headers=headers)
    assert res.status_code == 201, f"Create task failed: {res.text}"
    data = res.json()
    assert data["title"] == payload["title"]
    assert data["project_id"] == project_id
    os.environ["TEST_TASK_ID"] = str(data["id"])
    print(f"✅ Created Task linked to Project ID {project_id} (Task ID: {data['id']})")

def test_04_schedule_meeting():
    now = datetime.now()
    payload = {
        "title": "Weekly Multi-Agent Architecture Review",
        "description": "Review sprint progress on local RAG and email agent functions.",
        "start_time": (now + timedelta(hours=2)).isoformat(),
        "end_time": (now + timedelta(hours=3)).isoformat(),
        "location_or_link": "https://meet.google.com/test-ai-room"
    }
    res = client.post("/api/v1/meetings", json=payload, headers=headers)
    assert res.status_code == 201, f"Create meeting failed: {res.text}"
    data = res.json()
    assert data["title"] == payload["title"]
    os.environ["TEST_MEETING_ID"] = str(data["id"])
    print(f"✅ Scheduled Meeting: '{payload['title']}'")

def test_05_record_file_upload():
    project_id = int(os.environ.get("TEST_PROJECT_ID"))
    payload = {
        "filename": "financial_report_2026.pdf",
        "file_type": "PDF",
        "file_path": "/uploads/financial_report_2026.pdf",
        "extracted_text": "Net income increased by 24% following automated email triage.",
        "project_id": project_id
    }
    res = client.post("/api/v1/files", json=payload, headers=headers)
    assert res.status_code == 201, f"Upload file record failed: {res.text}"
    data = res.json()
    assert data["filename"] == payload["filename"]
    print(f"✅ Registered Uploaded File Record with OCR Text for RAG indexing!")
