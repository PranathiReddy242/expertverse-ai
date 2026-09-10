"""
Automated Verification Suite for ExpertVerse AI Chatbot Accuracy & Domain Matching
Validates:
1. Exact Intent & Domain Classification across Medicine, Software, AI/ML, Cybersecurity, UI/UX, and Niche topics.
2. Authentic Domain Roadmaps (Clinical milestones for doctors, design systems for UI/UX, CTF for cyber).
3. Strict Domain Gating in Expert Recommendations (Zero cross-domain leakage).
4. Truthful No-Expert Handling when an unrepresented niche is queried.
5. Negative Matching Enforcement (Doctor query never recommends engineers).
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.db.session import SessionLocal
from app.models.user import User
from app.routes.agents import chat
from app.schemas.chat import ChatRequest
from app.services.intent_service import extract_user_intent
from app.services.agents import match_experts

def run_chat_accuracy_tests():
    print("=================================================================")
    print("   EXPERTVERSE AI — CHATBOT ACCURACY & DOMAIN MATCHING SUITE     ")
    print("=================================================================\n")
    passed = 0
    total = 0

    db = SessionLocal()
    test_user = db.query(User).first()

    # -------------------------------------------------------------
    # TEST 1: Medicine & Healthcare Domain Accuracy
    # -------------------------------------------------------------
    total += 1
    print(f"[TEST {total}] Medicine & Healthcare Query Intent & Expert Matching...")
    med_queries = [
        "I want to become a doctor.",
        "How can I become an MBBS doctor?",
        "I want to prepare for NEET."
    ]
    for q in med_queries:
        intent = extract_user_intent(q)
        print(f"       Query: '{q}'")
        print(f"         Detected Domain: {intent['domain_display']}")
        assert intent["domain"] == "medicine", f"Expected medicine domain, got {intent['domain']}"
        assert intent["intent"] == "career_guidance", f"Expected career_guidance, got {intent['intent']}"

        matches = match_experts(db, q)
        matched_names = [e["name"] for e in matches]
        print(f"         Matched Experts: {matched_names}")
        assert len(matches) > 0, "Expected at least 1 medical mentor matched"
        assert "Dr. Aakash Mukherjee" in matched_names, "Dr. Aakash Mukherjee must be recommended!"
        # Negative check: ZERO engineers
        for m in matches:
            title_lower = m["title"].lower()
            assert not any(k in title_lower for k in ["software", "cloud", "full-stack", "developer"]), \
                f"Engineering expert '{m['name']}' illegally leaked to medicine query!"

    # Test full chat response for doctor query
    resp_med = chat(ChatRequest(message="I want to become a doctor."), current_user=test_user, db=db)
    assert "Medicine" in resp_med.message or "Clinical" in resp_med.message or "NEET" in resp_med.message
    assert "Phase" in resp_med.message
    # Roadmap check
    p1 = resp_med.roadmap.get("phase_1", {}).get("milestones", "")
    p3 = resp_med.roadmap.get("phase_3", {}).get("milestones", "")
    print(f"         Roadmap Phase 1: {p1}")
    print(f"         Roadmap Phase 3: {p3}")
    assert any(k in p1.lower() for k in ["pre-medical", "entrance", "science", "biology"]), \
        f"Roadmap Phase 1 missing medical context: {p1}"
    assert any(k in p3.lower() for k in ["clinical", "hospital", "rotations", "clerkships"]), \
        f"Roadmap Phase 3 missing clinical context: {p3}"
    assert not any(k in str(resp_med.roadmap).lower() for k in ["open-source repository", "idiomatic code", "pull request"]), \
        "Coding terms found in medical roadmap!"

    print("  ==> [PASSED] Medicine queries accurately classified with clinical roadmap & medical experts.\n")
    passed += 1

    # -------------------------------------------------------------
    # TEST 2: Software Engineering & Web Development
    # -------------------------------------------------------------
    total += 1
    print(f"[TEST {total}] Software Engineering Query Intent & Expert Matching...")
    sw_q = "I want to become a software engineer."
    intent_sw = extract_user_intent(sw_q)
    print(f"       Query: '{sw_q}'")
    print(f"         Detected Domain: {intent_sw['domain_display']}")
    assert intent_sw["domain"] == "software_engineering"

    matches_sw = match_experts(db, sw_q)
    sw_names = [e["name"] for e in matches_sw]
    print(f"         Matched Experts: {sw_names}")
    assert "Sarah Jenkins" in sw_names, "Sarah Jenkins must be matched for software engineering!"
    assert "Dr. Aakash Mukherjee" not in sw_names, "Doctor must NOT be matched for software engineering!"

    print("  ==> [PASSED] Software queries match software architects without doctor leakage.\n")
    passed += 1

    # -------------------------------------------------------------
    # TEST 3: UI/UX & Product Design
    # -------------------------------------------------------------
    total += 1
    print(f"[TEST {total}] UI/UX & Product Design Intent & Expert Matching...")
    design_q = "I want to learn UI/UX design and Figma."
    intent_design = extract_user_intent(design_q)
    print(f"       Query: '{design_q}'")
    print(f"         Detected Domain: {intent_design['domain_display']}")
    assert intent_design["domain"] == "ui_ux_design"

    matches_design = match_experts(db, design_q)
    design_names = [e["name"] for e in matches_design]
    print(f"         Matched Experts: {design_names}")
    assert "Ananya Iyer" in design_names, "Ananya Iyer must be matched for UI/UX design!"
    assert "Dr. Aakash Mukherjee" not in design_names, "Doctor must NOT be matched for UI/UX design!"
    assert "Sarah Jenkins" not in design_names, "Software engineer must NOT be matched for UI/UX design!"

    resp_design = chat(ChatRequest(message=design_q), current_user=test_user, db=db)
    assert "UI/UX" in resp_design.message or "Design" in resp_design.message
    p_design = resp_design.roadmap.get("phase_1", {}).get("milestones", "")
    assert "design" in p_design.lower() or "figma" in p_design.lower()

    print("  ==> [PASSED] UI/UX queries match product design leads without engineer leakage.\n")
    passed += 1

    # -------------------------------------------------------------
    # TEST 4: Cybersecurity & Ethical Hacking
    # -------------------------------------------------------------
    total += 1
    print(f"[TEST {total}] Cybersecurity & Ethical Hacking Intent & Expert Matching...")
    cyber_q = "I want to become a cybersecurity professional and learn ethical hacking."
    intent_cyber = extract_user_intent(cyber_q)
    print(f"       Query: '{cyber_q}'")
    print(f"         Detected Domain: {intent_cyber['domain_display']}")
    assert intent_cyber["domain"] == "cybersecurity"

    matches_cyber = match_experts(db, cyber_q)
    cyber_names = [e["name"] for e in matches_cyber]
    print(f"         Matched Experts: {cyber_names}")
    assert "Vikramaditya Rao" in cyber_names, "Vikramaditya Rao must be matched for Cybersecurity!"
    assert "Dr. Aakash Mukherjee" not in cyber_names, "Doctor must NOT be matched for Cybersecurity!"
    assert "Ananya Iyer" not in cyber_names, "Designer must NOT be matched for Cybersecurity!"

    print("  ==> [PASSED] Cybersecurity queries match penetration testing specialists.\n")
    passed += 1

    # -------------------------------------------------------------
    # TEST 5: AI & Machine Learning
    # -------------------------------------------------------------
    total += 1
    print(f"[TEST {total}] Artificial Intelligence & Machine Learning Intent & Expert Matching...")
    ai_q = "I want to build deep neural network models with PyTorch."
    intent_ai = extract_user_intent(ai_q)
    print(f"       Query: '{ai_q}'")
    print(f"         Detected Domain: {intent_ai['domain_display']}")
    assert intent_ai["domain"] == "ai_ml_data"

    matches_ai = match_experts(db, ai_q)
    ai_names = [e["name"] for e in matches_ai]
    print(f"         Matched Experts: {ai_names}")
    assert "Arjun Singh" in ai_names, "Arjun Singh must be matched for AI/ML!"
    assert "Dr. Aakash Mukherjee" not in ai_names, "Doctor must NOT be matched for AI/ML!"

    print("  ==> [PASSED] AI/ML queries match GenAI/ML architect.\n")
    passed += 1

    # -------------------------------------------------------------
    # TEST 6: Unrepresented / Niche Domain (Zero Fabrication & Clear Notice)
    # -------------------------------------------------------------
    total += 1
    print(f"[TEST {total}] Unrepresented Niche Domain Handling (Zero Fabrication + Transparent Notice)...")
    niche_q = "I want to study marine biology."
    intent_niche = extract_user_intent(niche_q)
    print(f"       Query: '{niche_q}'")
    print(f"         Detected Domain: {intent_niche['domain_display']}")
    assert intent_niche["domain"] == "other"

    matches_niche = match_experts(db, niche_q)
    print(f"         Matched Experts Count: {len(matches_niche)}")
    assert len(matches_niche) == 0, f"Expected ZERO experts for marine biology, got {len(matches_niche)}"

    resp_niche = chat(ChatRequest(message=niche_q), current_user=test_user, db=db)
    assert len(resp_niche.recommended_experts) == 0, "Must return 0 recommended experts for unrepresented domain"
    assert "there are currently no verified" in resp_niche.message.lower(), \
        "Response must transparently inform user that no mentor is currently available in this field!"
    assert not any(k in resp_niche.message for k in ["Dr. Aakash Mukherjee", "Sarah Jenkins", "Arjun Singh"]), \
        "Unrelated experts must NEVER be mentioned in text when 0 mentors match!"

    print("  ==> [PASSED] Unrepresented niches return 0 experts and transparently notify the user without fabrication.\n")
    passed += 1

    db.close()

    # -------------------------------------------------------------
    # SUMMARY
    # -------------------------------------------------------------
    print("=================================================================")
    print(f"   CHAT ACCURACY VERIFICATION COMPLETE: {passed}/{total} TESTS PASSED (100%)")
    print("=================================================================")

if __name__ == "__main__":
    run_chat_accuracy_tests()
