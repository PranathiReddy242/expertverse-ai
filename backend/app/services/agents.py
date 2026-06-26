from datetime import datetime
from typing import Any

from sqlalchemy.orm import Session

from app.models.expert import Expert
from app.models.chat_history import ChatHistory
from app.models.action_plan import ActionPlan
from app.models.booking import Booking

from app.services.embeddings import get_text_response
from app.services.vector_store import query_expert_documents


def analyze_problem(db: Session, user_input: str) -> dict[str, Any]:

    prompt = f"""
Analyze the user's request.

Return a concise structured response containing:

Domain:
Subdomain:
Goal:
Urgency:
Estimated Duration:

User request:
{user_input}

Do not use markdown.
"""

    raw = get_text_response(prompt)

    cleaned = raw.replace("**", "")

    return {
        "analysis_text": cleaned
    }


def match_experts(db: Session, user_input: str) -> list[dict[str, Any]]:

    experts = (
        db.query(Expert)
        .order_by(
            Expert.rating.desc(),
            Expert.experience_years.desc()
        )
        .all()
    )

    document_result = query_expert_documents(
        user_input,
        top_k=5
    )

    expert_order = []

    if isinstance(document_result, dict) and document_result.get("metadatas"):

        for metadata in document_result["metadatas"][0]:

            expert_id = metadata.get("expert_id")

            if expert_id and expert_id not in expert_order:
                expert_order.append(expert_id)

    ordered = []
    seen = set()

    for expert_id in expert_order:

        expert = next(
            (e for e in experts if e.id == expert_id),
            None
        )

        if expert and expert.id not in seen:
            ordered.append(expert)
            seen.add(expert.id)

    for expert in experts:

        if expert.id not in seen and len(ordered) < 5:
            ordered.append(expert)
            seen.add(expert.id)

    return [
        {
            "id": expert.id,
            "name": expert.user.name if expert.user else "Expert",
            "title": expert.title,
            "experience_years": expert.experience_years,
            "rating": expert.rating,
        }
        for expert in ordered[:5]
    ]


def generate_roadmap(db: Session, user_input: str) -> dict[str, Any]:

    prompt = f"""
Create a roadmap for:

{user_input}

Return EXACTLY in this format:

Phase 1
Milestones: ...
Tasks: ...
Next Steps: ...

Phase 2
Milestones: ...
Tasks: ...
Next Steps: ...

Phase 3
Milestones: ...
Tasks: ...
Next Steps: ...

Phase 4
Milestones: ...
Tasks: ...
Next Steps: ...

Do not use markdown.
Keep answers concise.
"""

    raw = get_text_response(prompt)

    raw = (
        raw.replace("**", "")
           .replace("#", "")
           .replace("\t", "")
    )

    phases = {}

    for i in range(1, 5):
        phase_name = f"Phase {i}"

        if phase_name in raw:
            start = raw.find(phase_name)

            if i < 4 and f"Phase {i+1}" in raw:
                end = raw.find(f"Phase {i+1}")
                section = raw[start:end]
            else:
                section = raw[start:]

            milestones = ""
            tasks = ""
            next_steps = ""

            if "Milestones:" in section and "Tasks:" in section:
                milestones = section.split("Milestones:")[1].split("Tasks:")[0].strip()

            if "Tasks:" in section and "Next Steps:" in section:
                tasks = section.split("Tasks:")[1].split("Next Steps:")[0].strip()

            if "Next Steps:" in section:
                next_steps = section.split("Next Steps:")[1].strip()

            phases[f"phase_{i}"] = {
                "milestones": milestones,
                "tasks": tasks,
                "next_steps": next_steps
            }

    phases["generated_at"] = datetime.utcnow().isoformat() + "Z"

    return phases

def save_chat_history(
    db: Session,
    user_id: int,
    message: str,
    response_text: str
) -> ChatHistory:

    chat = ChatHistory(
        user_id=user_id,
        message=message,
        response=response_text
    )

    db.add(chat)
    db.commit()
    db.refresh(chat)

    return chat


def save_action_plan(
    db: Session,
    user_id: int,
    plan_json: str
) -> ActionPlan:

    plan = ActionPlan(
        user_id=user_id,
        plan_json=plan_json
    )

    db.add(plan)
    db.commit()
    db.refresh(plan)

    return plan


def create_booking_record(
    db: Session,
    user_id: int,
    expert_id: int,
    slot: datetime
) -> Booking:

    booking = Booking(
        user_id=user_id,
        expert_id=expert_id,
        slot=slot,
        status="confirmed"
    )

    db.add(booking)
    db.commit()
    db.refresh(booking)

    return booking