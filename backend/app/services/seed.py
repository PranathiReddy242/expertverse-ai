from sqlalchemy.orm import Session
from app.models.user import User
from app.models.expert import Expert
from app.routes.auth import get_password_hash
from app.services.vector_store import add_documents_to_expert

DEFAULT_USERS = [
    {"name": "Grace Lee", "email": "grace@example.com", "password": "password123", "role": "user"},
    {"name": "Arjun Singh", "email": "arjun@example.com", "password": "password123", "role": "expert"},
]

DEFAULT_EXPERTS = [
    {
        "user_email": "arjun@example.com",
        "title": "AI Strategy Expert",
        "company": "ExpertVerse",
        "experience_years": 8,
        "bio": "Helps teams go from concept to market with AI product strategy.",
        "hourly_rate": 185.0,
        "rating": 4.9,
        "documents": [
            {"text": "Expert in AI product strategy, fundraising guidance, roadmap planning, and GTM execution.", "file_type": "text"},
            {"text": "Supports users with technical product planning, hiring strategy, and KPI alignment.", "file_type": "text"},
        ],
    },
]


def seed(db: Session):
    if db.query(User).count() == 0:
        for user_data in DEFAULT_USERS:
            user = User(
                name=user_data["name"],
                email=user_data["email"],
                password_hash=get_password_hash(user_data["password"]),
                role=user_data["role"],
            )
            db.add(user)
        db.commit()

    if db.query(Expert).count() == 0:
        expert_user = db.query(User).filter(User.email == "arjun@example.com").first()
        if expert_user:
            expert_data = DEFAULT_EXPERTS[0]
            expert = Expert(
                user_id=expert_user.id,
                title=expert_data["title"],
                company=expert_data["company"],
                experience_years=expert_data["experience_years"],
                bio=expert_data["bio"],
                hourly_rate=expert_data["hourly_rate"],
                rating=expert_data["rating"],
            )
            db.add(expert)
            db.commit()
            db.refresh(expert)
            try:
                add_documents_to_expert(expert.id, expert_data["documents"])
            except Exception:
                # If embeddings or vector store are not configured, skip without failing startup
                pass
