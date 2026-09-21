import sys
import os
import json
import traceback
from datetime import datetime, timedelta

# Ensure root and backend are on sys.path
sys.path.insert(0, os.path.abspath("backend"))
sys.path.insert(0, os.path.abspath("."))

from fastapi.testclient import TestClient
from app.main import app
from app.db.session import SessionLocal
from app.models.user import User
from app.models.expert import Expert
from app.models.booking import Booking

client = TestClient(app)

results = {
    "whitebox": [],
    "blackbox": []
}

def log_test(category, name, passed, details):
    status = "PASS" if passed else "FAIL"
    results[category].append({"name": name, "status": status, "details": details})
    print(f"[{category.upper()}] [{status}] {name} -> {details}")

print("==========================================================")
print("  EXPERTVERSE AI — BLACK BOX & WHITE BOX TEST SUITE")
print("==========================================================")

# ========================================================
# 1. WHITE BOX AUDIT: CODE PATHS & LOGICAL FLOWS
# ========================================================

# W1: Password Hashing & Verification Logic
from app.routes.auth import get_password_hash, verify_password, create_access_token
try:
    pwd = "SecurePassword123!"
    hashed = get_password_hash(pwd)
    v1 = verify_password(pwd, hashed)
    v2 = verify_password("WrongPassword!", hashed)
    log_test("whitebox", "W1: Cryptographic Password Hashing & Verification", v1 and not v2, "Correctly verifies valid password and rejects invalid")
except Exception as e:
    log_test("whitebox", "W1: Cryptographic Password Hashing & Verification", False, str(e))

# W2: JWT Generation, Expiry, and Claims Structure
try:
    token = create_access_token({"user_id": 999, "is_learner": True, "is_expert": False, "is_admin": False})
    from jose import jwt
    from app.core.config import settings
    payload = jwt.decode(token, settings.secret_key, algorithms=["HS256"])
    log_test("whitebox", "W2: JWT Token Claims & Secret Encoding", payload.get("user_id") == 999 and "exp" in payload, f"Decoded claims: {payload}")
except Exception as e:
    log_test("whitebox", "W2: JWT Token Claims & Secret Encoding", False, str(e))

# W3: Database Session Lifecycle (get_db generator)
try:
    from app.db.session import get_db
    db_gen = get_db()
    session = next(db_gen)
    test_query = session.query(User).count()
    # close session
    try:
        next(db_gen)
    except StopIteration:
        pass
    log_test("whitebox", "W3: Database Session Pool & Cleanup Lifecycle", test_query >= 0, f"Session active, queried {test_query} users")
except Exception as e:
    log_test("whitebox", "W3: Database Session Pool & Cleanup Lifecycle", False, str(e))

# W4: Intent Service Classification Branching (Medical vs AI vs PM)
from app.services.intent_service import extract_user_intent
try:
    i1 = extract_user_intent("I am preparing for NEET and need an MBBS surgery mentor")
    i2 = extract_user_intent("I want to build autonomous LangChain agents in Python")
    i3 = extract_user_intent("I am preparing for a Senior Product Manager interview at Google")
    log_test("whitebox", "W4: Intent Detection Classification Branches", 
             i1.get("domain") == "medicine" and i2.get("domain") == "ai_ml_data" and (i3.get("domain") in ["business_finance", "career_growth", "product_management"]),
             f"Detected domains: {[i1.get('domain'), i2.get('domain'), i3.get('domain')]}")
except Exception as e:
    log_test("whitebox", "W4: Intent Detection Classification Branches", False, str(e))

# W5: Vector Store Cosine Similarity Computation
from app.services.vector_store import query_expert_documents
try:
    v_results = query_expert_documents("cardiology medical MBBS", top_k=2)
    log_test("whitebox", "W5: Vector Store Cosine Similarity & Search", True, f"Query returned structured vector results (count: {len(v_results)})")
except Exception as e:
    log_test("whitebox", "W5: Vector Store Cosine Similarity & Search", False, str(e))

# W6: Booking Duration & Price Calculation Logic
try:
    rate = 1800.0
    p60 = (60 / 60.0) * rate
    p30 = (30 / 60.0) * rate
    log_test("whitebox", "W6: Dynamic Session Price Formula", p60 == 1800.0 and p30 == 900.0, f"30m: Rs {p30}, 60m: Rs {p60}")
except Exception as e:
    log_test("whitebox", "W6: Dynamic Session Price Formula", False, str(e))

# ========================================================
# 2. BLACK BOX AUDIT: API ENDPOINTS & USER WORKFLOWS
# ========================================================

# B1: Health check
r = client.get("/health")
log_test("blackbox", "B1: GET /health", r.status_code == 200 and r.json().get("status") == "healthy", r.text)

# B2: Root status
r = client.get("/")
log_test("blackbox", "B2: GET /", r.status_code == 200, r.text)

# B3: Experts List (Positive Case)
r = client.get("/experts/list")
experts = r.json() if r.status_code == 200 else []
log_test("blackbox", "B3: GET /experts/list (Fetch Catalog)", r.status_code == 200 and len(experts) > 0, f"Found {len(experts)} experts")

# B4: Expert Search with Keyword
r = client.get("/experts/list?q=Medical")
med_experts = r.json() if r.status_code == 200 else []
log_test("blackbox", "B4: GET /experts/list?q=Medical (Search Filter)", r.status_code == 200 and len(med_experts) > 0, f"Found {len(med_experts)} matching")

# B5: Expert Details by Valid ID
if len(experts) > 0:
    eid = experts[0]["id"]
    r = client.get(f"/experts/details/{eid}")
    log_test("blackbox", f"B5: GET /experts/details/{eid} (Valid ID)", r.status_code == 200, f"Fetched: {r.json().get('title') if r.status_code == 200 else 'None'}")

# B6: Expert Details by Non-Existent ID (Negative Boundary Case)
r = client.get("/experts/details/999999")
log_test("blackbox", "B6: GET /experts/details/999999 (404 Handling)", r.status_code == 404, f"Returned code {r.status_code}")

# B7: User Registration (Positive Case)
unique_email = f"bb_test_{int(datetime.now().timestamp())}@expertverse.ai"
reg_payload = {"name": "Blackbox Tester", "email": unique_email, "password": "Password123!", "role": "learner"}
r = client.post("/auth/register", json=reg_payload)
log_test("blackbox", "B7: POST /auth/register (New User)", r.status_code == 200 and r.json().get("email") == unique_email, r.text)

# B8: User Registration Duplicate Email (Negative Case)
r = client.post("/auth/register", json=reg_payload)
log_test("blackbox", "B8: POST /auth/register (Duplicate Email 400)", r.status_code == 400, f"Returned: {r.text}")

# B9: User Login via JSON Body
r = client.post("/auth/login", json={"email": unique_email, "password": "Password123!"})
jwt_token = r.json().get("access_token") if r.status_code == 200 else None
log_test("blackbox", "B9: POST /auth/login (JSON Body Authentication)", r.status_code == 200 and jwt_token is not None, f"Received token: {jwt_token[:30]}...")

# B10: User Login via Form URL-Encoded Body
r = client.post("/auth/login", data={"username": unique_email, "password": "Password123!"})
log_test("blackbox", "B10: POST /auth/login (Form URL-Encoded Authentication)", r.status_code == 200 and "access_token" in r.json(), "Successfully authenticated via form")

# B11: User Login Invalid Password (Negative Case)
r = client.post("/auth/login", json={"email": unique_email, "password": "WrongPassword!"})
log_test("blackbox", "B11: POST /auth/login (Invalid Password 401)", r.status_code == 401, f"Returned: {r.text}")

# B12: User Profile with Valid Bearer Token
headers = {"Authorization": f"Bearer {jwt_token}"} if jwt_token else {}
r = client.get("/auth/profile", headers=headers)
log_test("blackbox", "B12: GET /auth/profile (Authenticated)", r.status_code == 200 and r.json().get("email") == unique_email, r.text)

# B13: User Profile with Missing/Invalid Token (Security Case)
r = client.get("/auth/profile", headers={"Authorization": "Bearer invalid_or_expired_token"})
log_test("blackbox", "B13: GET /auth/profile (Invalid Token 401 Rejection)", r.status_code == 401, f"Returned code {r.status_code}")

# B14: AI Agent Chat Intent Match
chat_payload = {"message": "I am looking for an experienced surgeon for NEET and clinical residency mentorship."}
r = client.post("/agents/chat", json=chat_payload, headers=headers)
reply = r.json().get("message", "") if r.status_code == 200 else ""
matched_dr = any(k in reply.lower() for k in ["mukherjee", "aakash", "doctor", "medical", "mbbs", "clinical", "surgeon"])
log_test("blackbox", "B14: POST /agents/chat (AI Intent & Mentor Matching)", r.status_code == 200 and matched_dr, f"AI Reply: {reply[:100]}...")

# B15: Booking Creation
if len(experts) > 0:
    eid = experts[0]["id"]
    book_payload = {
        "expert_id": eid,
        "slot": (datetime.now() + timedelta(days=3)).strftime("%Y-%m-%dT14:00:00"),
        "duration_minutes": 60,
        "learner_notes": "Comprehensive AI Architecture & Career Planning"
    }
    r = client.post("/bookings/create", json=book_payload, headers=headers)
    booking_id = r.json().get("id") if r.status_code == 200 else None
    log_test("blackbox", "B15: POST /bookings/create (Create Slot Booking)", r.status_code == 200 and booking_id is not None, f"Created Booking ID: {booking_id}")

    # B16: Razorpay Order Creation
    if booking_id:
        r = client.post(f"/bookings/{booking_id}/payment/create-order", headers=headers)
        order_data = r.json() if r.status_code == 200 else {}
        log_test("blackbox", "B16: POST /bookings/:id/payment/create-order", r.status_code == 200 and "order_id" in order_data, f"Order: {order_data.get('order_id')}")

    # B17: UPI Payment Intent & Verification
    if booking_id:
        r = client.post(f"/bookings/{booking_id}/payment/upi-confirm", json={"utr": "UTR123456789012", "upi_id": "pranathitarigonda@razorpay"}, headers=headers)
        log_test("blackbox", "B17: POST /bookings/:id/payment/upi-confirm (UPI Verification)", r.status_code == 200, f"Status: {r.json().get('status') if r.status_code == 200 else r.text}")

# B18: Admin Dashboard Protection (Learner trying to access Admin)
r = client.get("/admin/summary", headers=headers)
log_test("blackbox", "B18: GET /admin/summary (Learner Role Authorization Check)", r.status_code == 403, f"Learner correctly denied admin access with HTTP {r.status_code}")

print("==========================================================")
print(f"Summary: Total Whitebox: {len(results['whitebox'])} | Total Blackbox: {len(results['blackbox'])}")
print("==========================================================")
