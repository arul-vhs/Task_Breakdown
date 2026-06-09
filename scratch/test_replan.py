import sys
import os
import json

# Add backend directory to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../backend")))

from fastapi.testclient import TestClient
import app.main
from app.security.jwt import create_access_token

client = TestClient(app.main.app)

goal_id = "36e0068f-8048-45fa-8435-282e06234c1d"
user_id = "d2a6eafc-1463-4cef-893c-b3518668663c"

# 1. Create a JWT access token for this user
token = create_access_token(subject=user_id)
headers = {"Authorization": f"Bearer {token}"}

# 2. Trigger replanning preview
print("\n--- Generating Replan Preview ---")
payload = {
    "goal_id": goal_id,
    "new_hours_per_week": 12.0,
    "replanning_mode": "Balanced"
}
resp = client.post("/api/v1/replan/preview", json=payload, headers=headers)
print("Response Status Code:", resp.status_code)
print("Response JSON:")
print(json.dumps(resp.json(), indent=2))
