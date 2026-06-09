import sys
import os
import json

# Add backend directory to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../backend")))

from fastapi.testclient import TestClient
import app.main
from app.security.jwt import create_access_token
from app.database.session import SessionLocal
import app.database.base
from app.models.task import Task

client = TestClient(app.main.app)

goal_id = "36e0068f-8048-45fa-8435-282e06234c1d"
user_id = "d2a6eafc-1463-4cef-893c-b3518668663c"

# 1. Create a JWT access token for this user
token = create_access_token(subject=user_id)
headers = {"Authorization": f"Bearer {token}"}

# 2. Get task stats before toggle
db = SessionLocal()
try:
    tasks = db.query(Task).filter(Task.goal_id == goal_id).all()
    print(f"Goal ID: {goal_id}")
    print(f"Row count in tasks table for this goal: {len(tasks)}")
    
    # Print some example tasks
    print("\nExample task records:")
    for t in tasks[:3]:
        print(f"  - ID: {t.id} | Alias: {t.task_id_alias} | Name: '{t.name}' | Completed: {t.is_completed}")
finally:
    db.close()

# 3. Trigger toggle: set to completed
print("\n--- Toggling 'Equipment & Environment Setup' to True ---")
payload = {
    "goal_id": goal_id,
    "task_alias": "Equipment & Environment Setup",
    "is_completed": True,
    "time_spent": 1.5
}
update_resp = client.post("/api/v1/progress/update", json=payload, headers=headers)
print("Response Status Code:", update_resp.status_code)
print("Response JSON:")
print(json.dumps(update_resp.json(), indent=2))

# 4. Toggle back to False to preserve original state
print("\n--- Toggling 'Equipment & Environment Setup' back to False ---")
payload["is_completed"] = False
cleanup_resp = client.post("/api/v1/progress/update", json=payload, headers=headers)
print("Cleanup Status Code:", cleanup_resp.status_code)
