import requests
import json

BASE_URL = "http://localhost:8000"

print("=" * 60)
print("TESTING AUTH FLOW")
print("=" * 60)

import time

TEST_EMAIL = f"test_{int(time.time())}@example.com"
TEST_PASS = "testpass123"

# Step 1: Register
print("\n1. Registering user...")
try:
    resp = requests.post(f"{BASE_URL}/auth/register", json={
        "name": "Test User",
        "email": TEST_EMAIL,
        "password": TEST_PASS
    })
    print(f"Status: {resp.status_code}")
    if resp.status_code in [200, 400]:  # 400 = already exists
        print(f"Response: {resp.json()}")
except Exception as e:
    print(f"Error: {e}")
    print("ERROR: Backend is not running! Start it with:")
    print("  python -m uvicorn app.main:app --reload")
    exit(1)

# Step 2: Login
print("\n2. Logging in...")
try:
    resp = requests.post(f"{BASE_URL}/auth/login", data={
        "username": TEST_EMAIL,
        "password": TEST_PASS
    })
    print(f"Status: {resp.status_code}")
    result = resp.json()
    print(f"Response: {result}")
    
    if resp.status_code != 200:
        print("ERROR: Login failed!")
        exit(1)
    
    token = result.get("access_token")
    print(f"Token: {token[:20]}... (truncated)")
    
except Exception as e:
    print(f"Error: {e}")
    exit(1)

# Step 3: Chat with token
print("\n3. Making chat request with token...")
try:
    headers = {"Authorization": f"Bearer {token}"}
    resp = requests.post(f"{BASE_URL}/agents/chat", 
        json={"message": "I want to learn Python"}, 
        headers=headers)
    print(f"Status: {resp.status_code}")
    result = resp.json()
    print(f"Response: {json.dumps(result, indent=2)[:500]}...")
    
    if resp.status_code == 401:
        print("\nERROR: 401 Unauthorized!")
        print("The token is being rejected by the backend.")
        print("This means the JWT verification is failing.")
        
except Exception as e:
    print(f"Error: {e}")

print("\n" + "=" * 60)
