#!/usr/bin/env python
"""
End-to-end test for ExpertVerse AI core functionality.
Tests: registration, login, expert listing, document search, and agents.
"""

import requests
import json
from typing import Dict, Any

BASE_URL = "http://localhost:8000"
HEADERS = {"Content-Type": "application/json"}
TOKEN = None


def test_register_user(email: str, name: str = "Test User", password: str = "testpass123"):
    """Test user registration."""
    global TOKEN
    print(f"\n[TEST] Registering user: {email}")
    payload = {"name": name, "email": email, "password": password, "role": "user"}
    resp = requests.post(f"{BASE_URL}/auth/register", json=payload, headers=HEADERS)
    print(f"Status: {resp.status_code}")
    if resp.status_code == 200:
        print(f"✓ Registered successfully: {resp.json()}")
        return True
    else:
        print(f"✗ Failed: {resp.text}")
        return False


def test_login_user(email: str, password: str = "testpass123"):
    """Test user login and token retrieval."""
    global TOKEN
    print(f"\n[TEST] Logging in user: {email}")
    data = f"username={email}&password={password}"
    resp = requests.post(
        f"{BASE_URL}/auth/login",
        data=data,
        headers={"Content-Type": "application/x-www-form-urlencoded"}
    )
    print(f"Status: {resp.status_code}")
    if resp.status_code == 200:
        TOKEN = resp.json().get("access_token")
        print(f"✓ Logged in successfully. Token: {TOKEN[:20]}...")
        return True
    else:
        print(f"✗ Failed: {resp.text}")
        return False


def test_list_experts():
    """Test expert listing."""
    print(f"\n[TEST] Listing all experts")
    resp = requests.get(f"{BASE_URL}/experts/list", headers=HEADERS)
    print(f"Status: {resp.status_code}")
    if resp.status_code == 200:
        experts = resp.json()
        print(f"✓ Found {len(experts)} expert(s)")
        for expert in experts:
            print(f"  - {expert.get('title')} (ID: {expert.get('id')}, Rating: {expert.get('rating')})")
        return experts
    else:
        print(f"✗ Failed: {resp.text}")
        return []


def test_expert_details(expert_id: int):
    """Test expert detail retrieval."""
    print(f"\n[TEST] Getting expert details: {expert_id}")
    resp = requests.get(f"{BASE_URL}/experts/details/{expert_id}", headers=HEADERS)
    print(f"Status: {resp.status_code}")
    if resp.status_code == 200:
        expert = resp.json()
        print(f"✓ Got expert details: {expert.get('title')}")
        return expert
    else:
        print(f"✗ Failed: {resp.text}")
        return None


def test_chat_agent(message: str):
    """Test the chat agent endpoint (requires authentication)."""
    global TOKEN
    print(f"\n[TEST] Sending chat message to agent")
    if not TOKEN:
        print("✗ No token available. Please login first.")
        return None
    
    headers = {**HEADERS, "Authorization": f"Bearer {TOKEN}"}
    payload = {"message": message}
    resp = requests.post(f"{BASE_URL}/agents/chat", json=payload, headers=headers)
    print(f"Status: {resp.status_code}")
    if resp.status_code == 200:
        result = resp.json()
        print(f"✓ Chat response received")
        print(f"  Message: {result.get('message')}")
        print(f"  Experts: {[e.get('title') for e in result.get('recommended_experts', [])]}")
        return result
    else:
        print(f"✗ Failed: {resp.text}")
        return None


def test_create_booking(expert_id: int = 1):
    """Test booking creation."""
    global TOKEN
    print(f"\n[TEST] Creating booking with expert {expert_id}")
    if not TOKEN:
        print("✗ No token available. Please login first.")
        return None
    
    from datetime import datetime, timedelta
    slot = (datetime.utcnow() + timedelta(days=7)).isoformat() + "Z"
    
    headers = {**HEADERS, "Authorization": f"Bearer {TOKEN}"}
    payload = {"expert_id": expert_id, "slot": slot}
    resp = requests.post(f"{BASE_URL}/bookings/create", json=payload, headers=headers)
    print(f"Status: {resp.status_code}")
    if resp.status_code == 200:
        result = resp.json()
        print(f"✓ Booking created")
        print(f"  Booking ID: {result.get('id')}")
        print(f"  Status: {result.get('status')}")
        print(f"  Slot: {result.get('slot')}")
        return result
    else:
        print(f"✗ Failed: {resp.text}")
        return None


def test_list_bookings():
    """Test listing user's bookings."""
    global TOKEN
    print(f"\n[TEST] Listing bookings")
    if not TOKEN:
        print("✗ No token available. Please login first.")
        return None
    
    headers = {**HEADERS, "Authorization": f"Bearer {TOKEN}"}
    resp = requests.get(f"{BASE_URL}/bookings/list", headers=headers)
    print(f"Status: {resp.status_code}")
    if resp.status_code == 200:
        bookings = resp.json()
        print(f"✓ Found {len(bookings)} booking(s)")
        for booking in bookings:
            print(f"  - Booking {booking.get('id')}: Expert {booking.get('expert_id')} at {booking.get('slot')} ({booking.get('status')})")
        return bookings
    else:
        print(f"✗ Failed: {resp.text}")
        return None


def test_analyze_agent(message: str):
    """Test the analyze agent endpoint."""
    global TOKEN
    print(f"\n[TEST] Analyzing problem via agent")
    if not TOKEN:
        print("✗ No token available. Please login first.")
        return None
    
    headers = {**HEADERS, "Authorization": f"Bearer {TOKEN}"}
    payload = {"message": message}
    resp = requests.post(f"{BASE_URL}/agents/analyze", json=payload, headers=headers)
    print(f"Status: {resp.status_code}")
    if resp.status_code == 200:
        result = resp.json()
        print(f"✓ Analysis received")
        print(f"  Domain: {result.get('domain')}")
        print(f"  Goal: {result.get('goal')}")
        print(f"  Analysis: {result.get('analysis_text')[:100]}...")
        return result
    else:
        print(f"✗ Failed: {resp.text}")
        return None


def main():
    print("=" * 60)
    print("ExpertVerse AI - End-to-End Test Suite")
    print("=" * 60)
    
    test_email = "test_e2e@example.com"
    
    # 1. Register
    test_register_user(test_email)
    
    # 2. Login
    if not test_login_user(test_email):
        print("\n✗ Login failed. Stopping tests.")
        return
    
    # 3. List experts
    experts = test_list_experts()
    
    # 4. Get expert details
    if experts:
        test_expert_details(experts[0].get("id"))
    
    # 5. Test analyze agent
    test_analyze_agent("I want to transition into AI and data science")
    
    # 6. Test chat agent
    test_chat_agent("I'm interested in learning about AI product strategy")
    
    # 7. Test bookings
    booking = test_create_booking(expert_id=1)
    if booking:
        test_list_bookings()
    
    print("\n" + "=" * 60)
    print("Test suite completed!")
    print("=" * 60)


if __name__ == "__main__":
    main()
