import pytest
from fastapi.testclient import TestClient

def test_goal_creation_and_context(client: TestClient):
    # 1. Register and login to retrieve auth headers
    signup_data = {
        "email": "goals_user@example.com",
        "password": "securepassword123"
    }
    client.post("/api/v1/auth/signup", json=signup_data)
    
    login_data = {
        "username": "goals_user@example.com",
        "password": "securepassword123"
    }
    login_resp = client.post("/api/v1/auth/login", data=login_data)
    token = login_resp.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # 2. Create Goal test
    goal_data = {
        "title": "Master FastAPI Development in 30 Days",
        "description": "Learn routing, dependencies injection, database relations, and authentication workflows."
    }
    response = client.post("/api/v1/auth/profile", json={
        "role": "Working Professional",
        "work_style": "Pomodoro",
        "weekly_hours_available": 15.0,
        "biggest_challenge": "Lack of time",
        "full_name": "Developer John"
    }, headers=headers)
    assert response.status_code == 200

    goal_resp = client.post("/api/v1/goals/", json=goal_data, headers=headers)
    assert goal_resp.status_code == 201
    goal_json = goal_resp.json()
    assert goal_json["title"] == goal_data["title"]
    assert "id" in goal_json
    goal_id = goal_json["id"]

    # 3. Retrieve Goal details
    get_resp = client.get(f"/api/v1/goals/{goal_id}", headers=headers)
    assert get_resp.status_code == 200
    assert get_resp.json()["title"] == goal_data["title"]
