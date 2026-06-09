import sys
import os
import json
import random

# Add backend directory to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../backend")))

from fastapi.testclient import TestClient
from app.main import app
from app.database.session import SessionLocal
from app.models.strategy import Strategy

client = TestClient(app)

rand_id = random.randint(1000, 9999)
email = f"strategy_test_{rand_id}@example.com"
password = "securepassword123"

print(f"Testing with user: {email}")

# 1. Sign up / Login
signup_resp = client.post("/api/v1/auth/signup", json={"email": email, "password": password})
login_resp = client.post("/api/v1/auth/login", data={"username": email, "password": password})
token = login_resp.json()["access_token"]
headers = {"Authorization": f"Bearer {token}"}

# 2. Update profile
client.post("/api/v1/auth/profile", json={
    "role": "Founder",
    "work_style": "Deep Work",
    "weekly_hours_available": 20.0,
    "biggest_challenge": "Burnout & Overwhelm",
    "full_name": "Founder Bob"
}, headers=headers)

# 3. Create Goal
goal_resp = client.post("/api/v1/goals/", json={
    "title": "Build and Launch a SaaS MVP in 30 Days",
    "description": "Develop a micro-service backend, simple landing page, and integrate payment gateway."
}, headers=headers)
goal_id = goal_resp.json()["id"]
print(f"Goal created with ID: {goal_id}")

# 4. Analyze goal (generates context questions)
print("\n--- Running Goal Intake/Analysis ---")
analyze_resp = client.post(f"/api/v1/goals/{goal_id}/analyze", headers=headers)
print("Analyze Status:", analyze_resp.status_code)
questions = analyze_resp.json()["questions"]
print(f"Intake questions generated: {len(questions)}")

# 5. Submit context Q&A answers
print("\n--- Submitting Context Answers ---")
answers = [{"question": q, "answer": f"Mock answer for question: {q[:30]}..."} for q in questions]
context_resp = client.post(f"/api/v1/goals/{goal_id}/context", json={"answers": answers}, headers=headers)
print("Submit Context Status:", context_resp.status_code)

# 6. Generate Strategies
print("\n--- Generating Strategies (Triggering Normalization & Persistence) ---")
gen_resp = client.post("/api/v1/strategies/generate", json={"goal_id": goal_id}, headers=headers)
print("Generate Strategies Status:", gen_resp.status_code)

if gen_resp.status_code == 200:
    res_data = gen_resp.json()
    print("\nStrategies Generation Response Payload:")
    print(json.dumps(res_data, indent=2))
    
    # 7. Check Database to confirm strategies were actually saved
    db = SessionLocal()
    try:
        saved_strats = db.query(Strategy).filter(Strategy.goal_id == goal_id).all()
        print(f"\nSuccessfully verified in database: Found {len(saved_strats)} saved strategies.")
        for s in saved_strats:
            print(f"  - Key: {s.strategy_key} | Title: {s.title} | Recommended: {s.is_recommended}")
    finally:
        db.close()
else:
    print("Error:", gen_resp.json())
