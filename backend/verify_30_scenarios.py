"""
ExpertVerse AI - 30-Scenario Complete System Verification Suite
Tests all 30 core functional, security, RBAC, lifecycle, AI, and payment scenarios.
"""

import sys
import time
from datetime import datetime, timedelta

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

from fastapi.testclient import TestClient
from app.main import app
from app.db.session import SessionLocal
from app.models.user import User
from app.models.expert import Expert
from app.models.document import Document
from app.models.booking import Booking

results = []

def run_test(scenario_num: int, name: str, test_func, client):
    start = time.time()
    try:
        test_func(client)
        duration = (time.time() - start) * 1000
        print(f"  \033[92m[PASS]\033[0m Scenario {scenario_num:02d}: {name} ({duration:.1f}ms)")
        results.append({"num": scenario_num, "name": name, "passed": True, "error": None})
    except Exception as e:
        duration = (time.time() - start) * 1000
        print(f"  \033[91m[FAIL]\033[0m Scenario {scenario_num:02d}: {name} - Error: {e} ({duration:.1f}ms)")
        results.append({"num": scenario_num, "name": name, "passed": False, "error": str(e)})

print("=" * 80)
print("EXPERTVERSE AI — 30-SCENARIO AUTOMATED VERIFICATION SUITE")
print("=" * 80)

# Global test state
state = {}

with TestClient(app) as client:
    # --- SCENARIO 1: Learner User Registration ---
    def test_01(c):
        email = f"learner_test_{int(time.time()*1000)}@example.com"
        state["learner_email"] = email
        state["learner_password"] = "password123"
        resp = c.post("/auth/register", json={
            "name": "Test Learner",
            "email": email,
            "password": state["learner_password"],
            "role": "user"
        })
        assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
        data = resp.json()
        assert data["is_learner"] is True
        assert data["is_expert"] is False
        assert data["email"] == email

    run_test(1, "Learner Registration (Default Learner Role)", test_01, client)

    # --- SCENARIO 2: Expert Applicant Registration ---
    def test_02(c):
        email = f"expert_applicant_{int(time.time()*1000)}@example.com"
        state["expert_applicant_email"] = email
        state["expert_applicant_password"] = "password123"
        resp = c.post("/auth/register", json={
            "name": "Applicant Expert",
            "email": email,
            "password": state["expert_applicant_password"],
            "role": "expert"
        })
        assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
        data = resp.json()
        assert data["is_expert"] is True
        state["expert_applicant_user_id"] = data["id"]

    run_test(2, "Expert Applicant Registration (Expert Flag Set)", test_02, client)

    # --- SCENARIO 3: Duplicate Email Registration Prevention ---
    def test_03(c):
        resp = c.post("/auth/register", json={
            "name": "Duplicate User",
            "email": state["learner_email"],
            "password": "password123",
            "role": "user"
        })
        assert resp.status_code == 400, f"Expected 400, got {resp.status_code}"
        assert "already registered" in resp.json().get("detail", "").lower()

    run_test(3, "Duplicate Email Prevention (400 Conflict Rejection)", test_03, client)

    # --- SCENARIO 4: Password Length Validation (< 6 chars) ---
    def test_04(c):
        resp = c.post("/auth/register", json={
            "name": "Weak Pass User",
            "email": f"weak_{int(time.time()*1000)}@example.com",
            "password": "123",
            "role": "user"
        })
        assert resp.status_code == 422, f"Expected 422, got {resp.status_code}"

    run_test(4, "Password Validation Enforcement (< 6 Characters Rejected)", test_04, client)

    # --- SCENARIO 5: User Login with Valid Credentials ---
    def test_05(c):
        resp = c.post("/auth/login", data={
            "username": state["learner_email"],
            "password": state["learner_password"]
        })
        assert resp.status_code == 200, f"Expected 200, got {resp.status_code}"
        data = resp.json()
        assert "access_token" in data
        assert data["token_type"].lower() == "bearer"
        state["learner_token"] = data["access_token"]

    run_test(5, "User Login with Valid Credentials (JWT Token Generation)", test_05, client)

    # --- SCENARIO 6: User Login with Invalid Password ---
    def test_06(c):
        resp = c.post("/auth/login", data={
            "username": state["learner_email"],
            "password": "WrongPassword999!"
        })
        assert resp.status_code == 401, f"Expected 401, got {resp.status_code}"

    run_test(6, "Authentication Security (Invalid Password Returns 401)", test_06, client)

    # --- SCENARIO 7: Authenticated Profile Retrieval ---
    def test_07(c):
        resp = c.get("/auth/profile", headers={"Authorization": f"Bearer {state['learner_token']}"})
        assert resp.status_code == 200, f"Expected 200, got {resp.status_code}"
        data = resp.json()
        assert data["email"] == state["learner_email"]
        assert data["is_learner"] is True

    run_test(7, "Authenticated Profile Endpoint (/auth/profile with Role Context)", test_07, client)

    # --- SCENARIO 8: RBAC - Learner Denied Admin Privileges ---
    def test_08(c):
        resp = c.get("/admin/summary", headers={"Authorization": f"Bearer {state['learner_token']}"})
        assert resp.status_code == 403, f"Expected 403, got {resp.status_code}"
        assert "admin" in resp.json().get("detail", "").lower()

    run_test(8, "RBAC Server-Side Enforcement (Learner Blocked from Admin APIs)", test_08, client)

    # --- SCENARIO 9: Admin Authentication & Privileged Access ---
    def test_09(c):
        login_resp = c.post("/auth/login", data={
            "username": "grace@example.com",
            "password": "password123"
        })
        assert login_resp.status_code == 200, f"Admin login failed: {login_resp.text}"
        state["admin_token"] = login_resp.json()["access_token"]
        
        summary_resp = c.get("/admin/summary", headers={"Authorization": f"Bearer {state['admin_token']}"})
        assert summary_resp.status_code == 200
        summary = summary_resp.json()
        assert "users" in summary
        assert "experts" in summary
        assert "approved_experts" in summary

    run_test(9, "Admin Authentication & Dashboard Metrics Summary Access", test_09, client)

    # --- SCENARIO 10: Expert Verification Credential Submission ---
    def test_10(c):
        # Login as expert applicant
        login_resp = c.post("/auth/login", data={
            "username": state["expert_applicant_email"],
            "password": state["expert_applicant_password"]
        })
        assert login_resp.status_code == 200
        state["expert_applicant_token"] = login_resp.json()["access_token"]

        submit_resp = c.post(
            "/experts/submit-verification",
            json={
                "certificate_url": "https://credentials.example.com/cert/12345",
                "resume_url": "https://linkedin.com/in/applicant",
                "linkedin_url": "https://linkedin.com/in/applicant",
                "experience_years": 8,
                "notes": "Experienced Systems Architect with Cloud certifications."
            },
            headers={"Authorization": f"Bearer {state['expert_applicant_token']}"}
        )
        assert submit_resp.status_code == 200, f"Expected 200, got {submit_resp.status_code}: {submit_resp.text}"
        data = submit_resp.json()
        assert data["verification_status"] == "pending"
        state["applicant_expert_id"] = data["expert_id"]

    run_test(10, "Expert Credential Submission (Transitions to Pending State)", test_10, client)

    # --- SCENARIO 11: Public Directory Filtering (Only Verified Experts Visible) ---
    def test_11(c):
        resp = c.get("/experts/list")
        assert resp.status_code == 200
        experts = resp.json()
        # Ensure our pending applicant is NOT in the public list
        applicant_ids = [e["id"] for e in experts if e["id"] == state["applicant_expert_id"]]
        assert len(applicant_ids) == 0, "Unverified expert must NOT appear in public directory"
        # Ensure all returned experts are verified
        for exp in experts:
            assert exp["is_verified"] is True

    run_test(11, "Public Directory Filtering (Unverified Experts Hidden)", test_11, client)

    # --- SCENARIO 12: Verified Expert Listing Verification ---
    def test_12(c):
        resp = c.get("/experts/list")
        assert resp.status_code == 200
        experts = resp.json()
        names = [e.get("user", {}).get("name") for e in experts]
        assert any("Arjun" in str(n) for n in names), f"Arjun Singh not in verified listings: {names}"

    run_test(12, "Verified Seed Experts Present in Public Listing", test_12, client)

    # --- SCENARIO 13: Expert Search & Filtering ---
    def test_13(c):
        resp = c.get("/experts/list?q=Strategy")
        assert resp.status_code == 200
        matches = resp.json()
        assert len(matches) >= 1
        assert any("Strategy" in (e.get("title") or "") for e in matches)

    run_test(13, "Expert Search Query Filter (Matches Title & Domain)", test_13, client)

    # --- SCENARIO 14: Restricting Public Access to Unverified Expert Details ---
    def test_14(c):
        resp = c.get(f"/experts/details/{state['applicant_expert_id']}")
        assert resp.status_code in [403, 404], f"Expected 403 or 404, got {resp.status_code}"

    run_test(14, "Public Protection (Unverified Expert Details Blocked)", test_14, client)

    # --- SCENARIO 15: Admin Action-Required Queue Retrieval ---
    def test_15(c):
        resp = c.get("/admin/pending-verifications", headers={"Authorization": f"Bearer {state['admin_token']}"})
        assert resp.status_code == 200
        pending_list = resp.json()
        assert isinstance(pending_list, list)
        pending_ids = [pe["expert_id"] for pe in pending_list]
        assert state["applicant_expert_id"] in pending_ids, "Pending applicant must appear in Admin Queue"

    run_test(15, "Admin Verification Queue (/admin/pending-verifications)", test_15, client)

    # --- SCENARIO 16: Admin Approves Expert Application ---
    def test_16(c):
        resp = c.post(
            f"/admin/experts/{state['applicant_expert_id']}/approve",
            headers={"Authorization": f"Bearer {state['admin_token']}"}
        )
        assert resp.status_code == 200, f"Expected 200, got {resp.status_code}"
        data = resp.json()
        assert data["is_verified"] is True
        assert data["verification_status"] == "approved"

    run_test(16, "Admin Expert Approval Workflow (Status Transitions to Approved)", test_16, client)

    # --- SCENARIO 17: Post-Approval Public Visibility Verification ---
    def test_17(c):
        resp = c.get("/experts/list")
        assert resp.status_code == 200
        experts = resp.json()
        approved_ids = [e["id"] for e in experts]
        assert state["applicant_expert_id"] in approved_ids, "Approved expert must now be visible publicly"

    run_test(17, "Immediate Public Visibility Following Admin Approval", test_17, client)

    # --- SCENARIO 18: Admin Rejects Expert with Mandatory Reason ---
    def test_18(c):
        email = f"reject_applicant_{int(time.time()*1000)}@example.com"
        reg = c.post("/auth/register", json={
            "name": "Reject Candidate",
            "email": email,
            "password": "password123",
            "role": "expert"
        })
        token = c.post("/auth/login", data={"username": email, "password": "password123"}).json()["access_token"]
        sub = c.post("/experts/submit-verification", json={"notes": "No certs"}, headers={"Authorization": f"Bearer {token}"})
        exp_id = sub.json()["expert_id"]
        state["rejected_exp_id"] = exp_id
        state["rejected_token"] = token

        reason = "Insufficient professional certification for requested tier."
        rej_resp = c.post(
            f"/admin/experts/{exp_id}/reject",
            json={"reason": reason},
            headers={"Authorization": f"Bearer {state['admin_token']}"}
        )
        assert rej_resp.status_code == 200
        assert rej_resp.json()["verification_status"] == "rejected"
        assert rej_resp.json()["rejection_reason"] == reason

    run_test(18, "Admin Expert Rejection with Mandatory Audit Reason", test_18, client)

    # --- SCENARIO 19: Unverified / Rejected Expert Booking Prevention ---
    def test_19(c):
        future_slot = (datetime.now() + timedelta(days=2)).isoformat()
        resp = c.post(
            "/bookings/create",
            json={"expert_id": state["rejected_exp_id"], "slot": future_slot},
            headers={"Authorization": f"Bearer {state['learner_token']}"}
        )
        assert resp.status_code == 400, f"Expected 400, got {resp.status_code}: {resp.text}"
        detail = resp.json().get("detail", "").lower()
        assert any(k in detail for k in ["not verified", "pending verification", "rejected", "cannot accept bookings"]), f"Unexpected detail: {detail}"

    run_test(19, "Booking Prevention for Unverified/Rejected Experts", test_19, client)

    # --- SCENARIO 20: Rejected Applicant Rejection Transparency ---
    def test_20(c):
        resp = c.get("/experts/my-verification", headers={"Authorization": f"Bearer {state['rejected_token']}"})
        assert resp.status_code == 200
        data = resp.json()
        assert data["verification_status"] == "rejected"
        assert "Insufficient professional certification" in data["rejection_reason"]

    run_test(20, "Applicant Rejection Reason Transparency via Verification API", test_20, client)

    # --- SCENARIO 21: Document Upload & Metadata Ingestion ---
    def test_21(c):
        resp = c.post(
            "/documents/upload-file",
            data={"expert_id": state["applicant_expert_id"]},
            files={"file": ("architecture_spec.txt", b"Microservices patterns and high-availability database replication.", "text/plain")},
            headers={"Authorization": f"Bearer {state['expert_applicant_token']}"}
        )
        assert resp.status_code == 200
        doc_data = resp.json()
        assert "id" in doc_data
        state["test_doc_id"] = doc_data["id"]

    run_test(21, "Expert Document Upload & Metadata Ingestion", test_21, client)

    # --- SCENARIO 22: Document Review Lifecycle - Admin Approval ---
    def test_22(c):
        resp = c.post(
            f"/admin/documents/{state['test_doc_id']}/review",
            json={"status": "approved", "review_notes": "Approved for inclusion in RAG index."},
            headers={"Authorization": f"Bearer {state['admin_token']}"}
        )
        assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
        assert resp.json().get("document_status") == "approved"

    run_test(22, "Document Lifecycle - Admin Review Approval", test_22, client)

    # --- SCENARIO 23: Document Review Lifecycle - Admin Rejection with Notes ---
    def test_23(c):
        up = c.post(
            "/documents/upload-file",
            data={"expert_id": state["applicant_expert_id"]},
            files={"file": ("invalid_doc.txt", b"Incomplete draft notes.", "text/plain")},
            headers={"Authorization": f"Bearer {state['expert_applicant_token']}"}
        )
        doc_id = up.json()["id"]
        rej = c.post(
            f"/admin/documents/{doc_id}/review",
            json={"status": "rejected", "review_notes": "Document contains unverified material."},
            headers={"Authorization": f"Bearer {state['admin_token']}"}
        )
        assert rej.status_code == 200, f"Expected 200, got {rej.status_code}: {rej.text}"
        assert rej.json().get("document_status") == "rejected"
        assert "unverified material" in rej.json().get("review_notes", "")

    run_test(23, "Document Lifecycle - Admin Rejection with Notes", test_23, client)

    # --- SCENARIO 24: Vector Search & Semantic Knowledge Retrieval ---
    def test_24(c):
        resp = c.post(
            "/documents/search",
            json={"query": "machine learning architecture", "k": 3}
        )
        assert resp.status_code == 200
        data = resp.json()
        assert "results" in data
        assert len(data["results"]) >= 1

    run_test(24, "Vector Search (FAISS Cosine Similarity Retrieval)", test_24, client)

    # --- SCENARIO 25: RAG Document-Grounded Q&A ---
    def test_25(c):
        resp = c.post(
            "/documents/rag-chat",
            json={"query": "What are best practices for high availability systems?"}
        )
        assert resp.status_code == 200
        data = resp.json()
        assert "answer" in data
        assert len(data["answer"]) > 20
        assert "sources" in data

    run_test(25, "RAG Document-Grounded Q&A Synthesis with Sources", test_25, client)

    # --- SCENARIO 26: Conversational AI Agent with Domain Intent Recognition ---
    def test_26(c):
        resp = c.post(
            "/agents/chat",
            json={"message": "I need architectural guidance for scaling an enterprise backend system."},
            headers={"Authorization": f"Bearer {state['learner_token']}"}
        )
        assert resp.status_code == 200
        data = resp.json()
        assert "message" in data
        assert len(data["message"]) > 30
        assert "recommended_experts" in data

    run_test(26, "Conversational AI Agent (Intent Recognition & Expert Recommendation)", test_26, client)

    # --- SCENARIO 27: Booking Creation for Verified Expert ---
    def test_27(c):
        # Look up a verified expert from DB
        db = SessionLocal()
        verified_expert = db.query(Expert).filter(Expert.is_verified == True).first()
        db.close()
        assert verified_expert is not None, "At least one verified expert must exist"

        slot = (datetime.now() + timedelta(days=3)).replace(microsecond=0).isoformat()
        resp = c.post(
            "/bookings/create",
            json={"expert_id": verified_expert.id, "slot": slot},
            headers={"Authorization": f"Bearer {state['learner_token']}"}
        )
        assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
        booking = resp.json()
        assert booking["status"] == "pending"
        assert booking["payment_status"] == "unpaid"
        state["booking_id"] = booking["id"]

    run_test(27, "Booking Creation for Verified Expert (Pending State)", test_27, client)

    # --- SCENARIO 28: Dual Payment Architecture - Razorpay Order Creation ---
    def test_28(c):
        resp = c.post(
            f"/bookings/{state['booking_id']}/payment/create-order",
            headers={"Authorization": f"Bearer {state['learner_token']}"}
        )
        assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
        order = resp.json()
        assert "order_id" in order
        assert "amount" in order
        assert order["currency"] == "INR"
        assert "key_id" in order

    run_test(28, "Dual Payment - Razorpay Order Generation (/payment/create-order)", test_28, client)

    # --- SCENARIO 29: Dual Payment Architecture - Academic Demo Instant Confirmation ---
    def test_29(c):
        resp = c.post(
            f"/bookings/{state['booking_id']}/payment/demo-confirm",
            headers={"Authorization": f"Bearer {state['learner_token']}"}
        )
        assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
        data = resp.json()
        assert data["status"] == "confirmed"
        assert data["payment_status"] == "paid"

    run_test(29, "Dual Payment - Academic Demo Mode Instant Confirmation", test_29, client)

    # --- SCENARIO 30: Truthful Admin AI Assistant Platform Analytics ---
    def test_30(c):
        resp = c.post(
            "/admin/ai-assistant",
            json={"query": "How many total users and verified experts are currently on the platform?"},
            headers={"Authorization": f"Bearer {state['admin_token']}"}
        )
        assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
        data = resp.json()
        assert "answer" in data
        assert "metrics_snapshot" in data
        assert data["metrics_snapshot"]["total_users"] > 0
        assert data["metrics_snapshot"]["approved_experts"] > 0

    run_test(30, "Truthful Admin AI Assistant (Live SQL Metric Analysis)", test_30, client)

print("=" * 80)
passed_count = sum(1 for r in results if r["passed"])
failed_count = sum(1 for r in results if not r["passed"])
print(f"VERIFICATION RESULTS: {passed_count}/{len(results)} SCENARIOS PASSED")
if failed_count == 0:
    print("\033[92m[SUCCESS] ALL 30/30 END-TO-END SCENARIOS VERIFIED SUCCESSFULLY!\033[0m")
else:
    print(f"\033[91m[FAILURE] {failed_count} SCENARIO(S) FAILED.\033[0m")
print("=" * 80)

if failed_count > 0:
    sys.exit(1)
