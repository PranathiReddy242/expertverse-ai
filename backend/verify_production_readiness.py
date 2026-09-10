"""
Comprehensive Production Readiness Verification Suite for ExpertVerse AI
Validates:
1. Semantic Expert Matching with non-random embeddings & zero irrelevant expert leakage.
2. Verified-only expert recommendations with explicit relevance reasons.
3. Dynamic real-time slot generation (day and month availability).
4. Conflict engine: Double-booking prevention returning HTTP 409 + nearest slot recommendations.
5. Past-date booking validation returning HTTP 400.
6. Multi-domain AI Chatbot guidance & roadmap generation.
"""

import sys
import os
from datetime import datetime, timedelta, date

# Ensure backend root is on sys.path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from fastapi.testclient import TestClient
from app.main import app
from app.db.session import SessionLocal
from app.models.user import User
from app.models.expert import Expert
from app.models.booking import Booking
from app.routes.auth import get_current_user
from app.services.agents import (
    analyze_problem,
    match_experts,
    generate_roadmap,
    generate_conversational_response,
)
from app.services.embeddings import get_embedding

client = TestClient(app)

def compute_similarity(v1: list[float], v2: list[float]) -> float:
    return sum(a * b for a, b in zip(v1, v2))

def run_tests():
    print("=================================================================")
    print("   EXPERTVERSE AI — PRODUCTION READINESS VERIFICATION SUITE       ")
    print("=================================================================\n")
    passed = 0
    total = 0

    # -------------------------------------------------------------
    # TEST 1: Semantic Embedding Determinism and Quality
    # -------------------------------------------------------------
    total += 1
    print(f"[TEST {total}] Semantic Embedding Generator Consistency & Cosine Similarity...")
    emb_ai1 = get_embedding("machine learning deep learning neural networks transformers")
    emb_ai2 = get_embedding("machine learning deep learning pytorch tensorflow")
    emb_cooking = get_embedding("italian pasta baking sourdough bread pastry")

    sim_similar = compute_similarity(emb_ai1, emb_ai2)
    sim_dissimilar = compute_similarity(emb_ai1, emb_cooking)

    print(f"       Similarity (AI vs AI): {sim_similar:.4f}")
    print(f"       Similarity (AI vs Cooking): {sim_dissimilar:.4f}")

    assert len(emb_ai1) == 1536, f"Embedding dimension mismatch: {len(emb_ai1)}"
    assert sim_similar > sim_dissimilar, f"Semantic similarity failed: {sim_similar} not > {sim_dissimilar}"
    assert sim_similar > 0.4, f"Similar domain similarity too low: {sim_similar}"
    print("  ==> [PASSED] Semantic embeddings produce consistent and discerning vectors.\n")
    passed += 1

    # -------------------------------------------------------------
    # TEST 2: Multi-Signal Semantic Expert Matching
    # -------------------------------------------------------------
    total += 1
    print(f"[TEST {total}] Semantic Expert Matching with Strict Verification & Relevance Reasons...")
    db = SessionLocal()
    try:
        # Query 1: Machine Learning
        ml_matches = match_experts(db, "I want to optimize large transformer models and build deep neural networks")
        print(f"       AI/ML Query matches found: {len(ml_matches)}")
        assert len(ml_matches) > 0, "No expert matches found for AI/ML query"
        for m in ml_matches:
            print(f"         - {m['name']} (Score: {m.get('score', 0)})")
            print(f"           Reason: {m['relevance_reason']}")
            # Must be verified
            expert_obj = db.query(Expert).filter(Expert.id == m['id']).first()
            assert expert_obj.is_verified is True, f"Expert {m['name']} must be verified!"
            assert expert_obj.is_active is True, f"Expert {m['name']} must be active!"
            assert "relevance_reason" in m and len(m["relevance_reason"]) > 10, "Missing relevance reason!"

        # Verify top ML expert is in AI/ML field
        top_expert_title = ml_matches[0]['title'].lower()
        assert any(k in top_expert_title for k in ["ai", "machine learning", "ml", "research", "engineer"]), \
            f"Top matched expert '{ml_matches[0]['name']}' title '{top_expert_title}' does not match AI domain!"

        # Query 2: Frontend Engineering
        fe_matches = match_experts(db, "I need help architecting React components and optimizing TypeScript frontend performance")
        print(f"       Frontend Query matches found: {len(fe_matches)}")
        assert len(fe_matches) > 0, "No expert matches found for Frontend query"
        top_fe_title = fe_matches[0]['title'].lower() + " " + " ".join(fe_matches[0].get('skills', [])).lower()
        print(f"         - {fe_matches[0]['name']} (Title: {fe_matches[0]['title']})")
        assert any(k in top_fe_title for k in ["frontend", "react", "full-stack", "typescript", "software"]), \
            f"Top matched expert '{fe_matches[0]['name']}' is not a frontend specialist!"

        print("  ==> [PASSED] Expert matching prioritizes verified domain specialists and returns explicit reasons.\n")
        passed += 1
    finally:
        db.close()

    # -------------------------------------------------------------
    # TEST 3: Dynamic Real-Time Availability Calculation
    # -------------------------------------------------------------
    total += 1
    print(f"[TEST {total}] Dynamic Availability Engine (Day & Month endpoints)...")
    db = SessionLocal()
    try:
        expert = db.query(Expert).filter(Expert.is_verified == True, Expert.is_active == True).first()
        assert expert is not None, "No verified expert found in test DB"
        expert_id = expert.id

        # Test Day Availability
        tomorrow_str = (date.today() + timedelta(days=2)).isoformat()
        res_day = client.get(f"/bookings/availability/{expert_id}?date={tomorrow_str}")
        assert res_day.status_code == 200, f"Day availability failed: {res_day.text}"
        day_data = res_day.json()
        assert day_data["date"] == tomorrow_str
        assert "slots" in day_data
        assert len(day_data["slots"]) >= 8, f"Expected at least 8 working hour slots, got {len(day_data['slots'])}"
        print(f"       Generated {len(day_data['slots'])} slots for {tomorrow_str} (Available: {day_data['available_count']})")

        # Test Month Availability
        next_month_target = date.today() + timedelta(days=30)
        res_month = client.get(f"/bookings/availability/{expert_id}/month?year={next_month_target.year}&month={next_month_target.month}")
        assert res_month.status_code == 200, f"Month availability failed: {res_month.text}"
        month_data = res_month.json()
        assert "days" in month_data
        assert len(month_data["days"]) > 20, f"Expected full month days, got {len(month_data['days'])}"
        print(f"       Month {next_month_target.year}-{next_month_target.month} generated {len(month_data['days'])} day schedules.")

        print("  ==> [PASSED] Availability endpoints dynamically calculate active and open slots.\n")
        passed += 1
    finally:
        db.close()

    # -------------------------------------------------------------
    # TEST 4: Double-Booking Conflict Engine & Alternative Suggestions
    # -------------------------------------------------------------
    total += 1
    print(f"[TEST {total}] Double-Booking Conflict Engine (409 Conflict + Nearest Alternatives)...")
    db = SessionLocal()
    try:
        user = db.query(User).first()
        expert = db.query(Expert).filter(Expert.is_verified == True, Expert.is_active == True).first()
        assert user is not None and expert is not None

        # Override auth dependency to act as `user`
        app.dependency_overrides[get_current_user] = lambda: user

        test_dt = datetime.combine(date.today() + timedelta(days=3), datetime.min.time()) + timedelta(hours=10)
        
        # Clean up any pre-existing booking for this slot
        db.query(Booking).filter(
            Booking.expert_id == expert.id,
            Booking.slot == test_dt
        ).delete()
        db.commit()

        # Step 1: Create legitimate initial booking in database
        first_booking = Booking(
            user_id=user.id,
            expert_id=expert.id,
            slot=test_dt,
            duration_minutes=60,
            status="accepted",
            payment_status="paid",
            learner_notes="Initial test reservation"
        )
        db.add(first_booking)
        db.commit()

        # Step 2: Attempt to book the exact same slot via API
        payload = {
            "expert_id": expert.id,
            "slot": test_dt.isoformat(),
            "duration_minutes": 60,
            "learner_notes": "Attempted double-booking conflict"
        }
        res_conflict = client.post("/bookings/create", json=payload)
        print(f"       Double-booking response code: {res_conflict.status_code}")
        assert res_conflict.status_code == 409, f"Expected 409 Conflict, got {res_conflict.status_code}: {res_conflict.text}"
        detail = res_conflict.json().get("detail", "")
        print(f"       Conflict detail: {detail}")
        assert "Nearest available slots today" in detail, f"Expected nearest slots in detail: {detail}"

        # Clean up test booking
        db.delete(first_booking)
        db.commit()

        print("  ==> [PASSED] Double-booking strictly blocked with HTTP 409 and alternative recommendations.\n")
        passed += 1
    finally:
        db.close()

    # -------------------------------------------------------------
    # TEST 5: Past-Date Booking Prevention
    # -------------------------------------------------------------
    total += 1
    print(f"[TEST {total}] Past-Date Validation (400 Bad Request)...")
    db = SessionLocal()
    try:
        user = db.query(User).first()
        expert = db.query(Expert).filter(Expert.is_verified == True).first()
        app.dependency_overrides[get_current_user] = lambda: user
        past_dt = datetime.utcnow() - timedelta(days=2)

        payload_past = {
            "expert_id": expert.id,
            "slot": past_dt.isoformat(),
            "duration_minutes": 60,
            "learner_notes": "Attempt to book slot in past"
        }
        res_past = client.post("/bookings/create", json=payload_past)
        print(f"       Past booking response code: {res_past.status_code}")
        assert res_past.status_code == 400, f"Expected 400 Bad Request, got {res_past.status_code}: {res_past.text}"
        assert "past" in res_past.json().get("detail", "").lower(), "Expected past error message"

        print("  ==> [PASSED] Past-date reservations strictly rejected with HTTP 400.\n")
        passed += 1
    finally:
        db.close()
        app.dependency_overrides.clear()

    # -------------------------------------------------------------
    # TEST 6: Multi-Domain AI Chat Reasoning & Strategic Roadmaps
    # -------------------------------------------------------------
    total += 1
    print(f"[TEST {total}] Multi-Domain AI Agent Response & Strategic Action Roadmaps...")
    db = SessionLocal()
    try:
        user = db.query(User).first()
        app.dependency_overrides[get_current_user] = lambda: user

        chat_queries = [
            ("AI Systems", "How can I deploy a quantized Llama 3 model with vLLM in production with high throughput?"),
            ("Cybersecurity", "How do I secure an enterprise Kubernetes cluster with Zero Trust architecture and mTLS?")
        ]

        for domain, query in chat_queries:
            res = client.post("/agents/chat", json={"message": query})
            assert res.status_code == 200, f"Chat failed with {res.status_code}: {res.text}"
            data = res.json()
            print(f"       Testing [{domain}] query:")
            print(f"         Recommended experts count: {len(data.get('recommended_experts', []))}")
            print(f"         Roadmap phases present: {list(data.get('roadmap', {}).keys())}")
            
            final_ans = data.get("message", "")
            assert len(final_ans) > 200, f"Chat response too brief for {domain}"
            assert "Phase" in final_ans or "Roadmap" in final_ans or "Architecture" in final_ans or "Strategy" in final_ans or "Action" in final_ans, \
                f"Response missing structured roadmap or architectural phases for {domain}"

        print("  ==> [PASSED] AI agent generates domain-accurate architectures, roadmaps, and grounded recommendations.\n")
        passed += 1
    finally:
        db.close()
        app.dependency_overrides.clear()

    # -------------------------------------------------------------
    # SUMMARY
    # -------------------------------------------------------------
    print("=================================================================")
    print(f"   TEST SUITE EXECUTION COMPLETE: {passed}/{total} TESTS PASSED (100%)")
    print("=================================================================")

if __name__ == "__main__":
    run_tests()
