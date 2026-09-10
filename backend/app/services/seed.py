from datetime import datetime, timedelta
from sqlalchemy.orm import Session

from app.models.user import User
from app.models.expert import Expert
from app.models.document import Document
from app.models.booking import Booking
from app.models.expert_verification import ExpertVerification
from app.routes.auth import get_password_hash
from app.services.vector_store import add_documents_to_expert


SEED_USERS = [
    {
        "name": "Grace Lee",
        "email": "grace@example.com",
        "password": "password123",
        "is_learner": True,
        "is_expert": False,
        "is_admin": True,
    },
    {
        "name": "Arjun Singh",
        "email": "arjun@example.com",
        "password": "password123",
        "is_learner": True,
        "is_expert": True,
        "is_admin": False,
    },
    {
        "name": "Sarah Jenkins",
        "email": "sarah@example.com",
        "password": "password123",
        "is_learner": True,
        "is_expert": True,
        "is_admin": False,
    },
    {
        "name": "Dr. Priya Sharma",
        "email": "priya@example.com",
        "password": "password123",
        "is_learner": True,
        "is_expert": True,
        "is_admin": False,
    },
    {
        "name": "Alex Rivera",
        "email": "alex@example.com",
        "password": "password123",
        "is_learner": True,
        "is_expert": True,
        "is_admin": False,
    },
    {
        "name": "Rohan Verma",
        "email": "rohan@example.com",
        "password": "password123",
        "is_learner": True,
        "is_expert": False,
        "is_admin": False,
    },
    {
        "name": "Dr. Aakash Mukherjee",
        "email": "aakash.med@example.com",
        "password": "password123",
        "is_learner": True,
        "is_expert": True,
        "is_admin": False,
    },
    {
        "name": "Ananya Iyer",
        "email": "ananya.design@example.com",
        "password": "password123",
        "is_learner": True,
        "is_expert": True,
        "is_admin": False,
    },
    {
        "name": "Vikramaditya Rao",
        "email": "vikram.sec@example.com",
        "password": "password123",
        "is_learner": True,
        "is_expert": True,
        "is_admin": False,
    },
]

SEED_EXPERTS = [
    {
        "user_email": "arjun@example.com",
        "title": "AI Strategy & GenAI Architect",
        "company": "MetaLabs AI",
        "experience_years": 8,
        "bio": "Specializes in enterprise LLM architectures, RAG pipelines, and ethical AI deployment. Passionate about empowering founders and engineers.",
        "skills": "LLMs, RAG, PyTorch, LangChain, Ethical AI, Vector Databases",
        "hourly_rate": 1500.0,
        "rating": 4.9,
        "total_reviews": 24,
        "total_sessions": 48,
        "is_verified": True,
        "verification_status": "approved",
        "is_active": True,
        "documents": [
            {
                "title": "Enterprise RAG Architecture Guide",
                "text": "Comprehensive architectural guide on building low-latency retrieval augmented generation with FAISS, metadata filtering, and hallucination guardrails.",
                "file_type": "pdf",
                "category": "architecture",
            },
            {
                "title": "Ethical AI Governance Checklist",
                "text": "Standard framework for model bias auditing, demographic parity testing, and compliance with data privacy regulations (GDPR and EU AI Act).",
                "file_type": "text",
                "category": "ethics",
            },
        ],
    },
    {
        "user_email": "sarah@example.com",
        "title": "Principal Full-Stack & Cloud Architect",
        "company": "ScaleCloud Systems",
        "experience_years": 10,
        "bio": "Helps engineers transition to senior full-stack roles, system design mastery, and distributed microservices architectures.",
        "skills": "React, TypeScript, FastAPI, Kubernetes, AWS, System Design",
        "hourly_rate": 1600.0,
        "rating": 4.8,
        "total_reviews": 19,
        "total_sessions": 36,
        "is_verified": True,
        "verification_status": "approved",
        "is_active": True,
        "documents": [
            {
                "title": "Microservices Resiliency Blueprint",
                "text": "Pattern catalog for distributed circuit breakers, rate limiting, and zero-downtime deployment pipelines on cloud infrastructure.",
                "file_type": "pdf",
                "category": "systems",
            },
        ],
    },
    {
        "user_email": "priya@example.com",
        "title": "Senior Data Science & MLOps Engineer",
        "company": "DataPulse Health",
        "experience_years": 6,
        "bio": "Focused on predictive modeling in healthcare and production MLOps. Awaiting administrative review.",
        "skills": "Python, SQL, MLflow, Docker, Healthcare NLP",
        "hourly_rate": 1200.0,
        "rating": 4.7,
        "total_reviews": 0,
        "total_sessions": 0,
        "is_verified": False,
        "verification_status": "pending",
        "is_active": True,
        "documents": [
            {
                "title": "Clinical NLP Benchmark Paper",
                "text": "Research paper outlining privacy-preserving transformer models on anonymized electronic health record datasets.",
                "file_type": "pdf",
                "category": "research",
            },
        ],
    },
    {
        "user_email": "alex@example.com",
        "title": "Junior Python Developer",
        "company": "Self-Employed",
        "experience_years": 1,
        "bio": "Junior developer eager to mentor beginners. Application reviewed and currently declined.",
        "skills": "Python, Django, SQLite",
        "hourly_rate": 500.0,
        "rating": 4.0,
        "total_reviews": 0,
        "total_sessions": 0,
        "is_verified": False,
        "verification_status": "rejected",
        "rejection_reason": "Insufficient verified enterprise experience (minimum 3 years required for expert tier).",
        "is_active": False,
        "documents": [],
    },
    {
        "user_email": "aakash.med@example.com",
        "title": "Clinical Director & Medical Career Mentor",
        "company": "Apex Institute of Medical Sciences",
        "experience_years": 12,
        "bio": "Senior physician and medical educator advising students on medical school admissions, NEET preparation, MBBS curriculum mastery, clinical rotations, and specialty healthcare careers.",
        "skills": "Medicine, MBBS, NEET, Clinical Medicine, Medical Education, Healthcare Careers, Pre-Med, Surgery",
        "hourly_rate": 1800.0,
        "rating": 4.95,
        "total_reviews": 32,
        "total_sessions": 64,
        "is_verified": True,
        "verification_status": "approved",
        "is_active": True,
        "documents": [
            {
                "title": "Medical Career & MBBS Comprehensive Roadmap",
                "text": "Detailed medical education guide covering pre-med preparation, entrance strategy, preclinical anatomy/physiology, clinical clerkships, and residency selection.",
                "file_type": "pdf",
                "category": "career",
            }
        ],
    },
    {
        "user_email": "ananya.design@example.com",
        "title": "Principal UI/UX & Product Design Lead",
        "company": "DesignCraft Studios",
        "experience_years": 9,
        "bio": "Product design leader with 9+ years guiding designers on Figma systems, user research, wireframing, portfolio presentation, and design reviews.",
        "skills": "UI/UX, Product Design, Figma, User Research, Wireframing, Design Systems, Usability Testing, Interaction Design",
        "hourly_rate": 1400.0,
        "rating": 4.9,
        "total_reviews": 21,
        "total_sessions": 42,
        "is_verified": True,
        "verification_status": "approved",
        "is_active": True,
        "documents": [
            {
                "title": "Product Design Portfolio Playbook",
                "text": "Practical handbook on framing design case studies, demonstrating iterative user research, typography hierarchy, and presenting wireframes to stakeholders.",
                "file_type": "pdf",
                "category": "design",
            }
        ],
    },
    {
        "user_email": "vikram.sec@example.com",
        "title": "Lead Cybersecurity & Penetration Testing Specialist",
        "company": "CyberShield Defense",
        "experience_years": 11,
        "bio": "Offensive security and information assurance expert mentoring professionals on ethical hacking, network defense, penetration testing, and zero trust security.",
        "skills": "Cybersecurity, Ethical Hacking, Penetration Testing, Zero Trust, Network Security, CISSP, OSCP, Threat Modeling",
        "hourly_rate": 1700.0,
        "rating": 4.88,
        "total_reviews": 18,
        "total_sessions": 35,
        "is_verified": True,
        "verification_status": "approved",
        "is_active": True,
        "documents": [
            {
                "title": "Ethical Hacking & Network Defense Blueprint",
                "text": "Practical offensive security manual detailing vulnerability scanning, penetration testing methodology, threat modeling, and defense-in-depth principles.",
                "file_type": "pdf",
                "category": "security",
            }
        ],
    },
]


def seed(db: Session):
    # 1. Upsert Users
    for user_data in SEED_USERS:
        existing = db.query(User).filter(User.email == user_data["email"]).first()
        if not existing:
            user = User(
                name=user_data["name"],
                email=user_data["email"],
                password_hash=get_password_hash(user_data["password"]),
                is_learner=user_data["is_learner"],
                is_expert=user_data["is_expert"],
                is_admin=user_data["is_admin"],
            )
            db.add(user)
        else:
            # Sync roles
            existing.is_learner = user_data["is_learner"]
            existing.is_expert = user_data["is_expert"]
            existing.is_admin = user_data["is_admin"]
            existing.name = user_data["name"]

    db.commit()

    # 2. Upsert Experts
    for exp_data in SEED_EXPERTS:
        user = db.query(User).filter(User.email == exp_data["user_email"]).first()
        if not user:
            continue

        expert = db.query(Expert).filter(Expert.user_id == user.id).first()
        if not expert:
            expert = Expert(
                user_id=user.id,
                title=exp_data["title"],
                company=exp_data["company"],
                experience_years=exp_data["experience_years"],
                bio=exp_data["bio"],
                skills=exp_data.get("skills"),
                hourly_rate=exp_data["hourly_rate"],
                rating=exp_data["rating"],
                total_reviews=exp_data.get("total_reviews", 0),
                total_sessions=exp_data.get("total_sessions", 0),
                is_verified=exp_data["is_verified"],
                verification_status=exp_data["verification_status"],
                rejection_reason=exp_data.get("rejection_reason"),
                is_active=exp_data["is_active"],
            )
            db.add(expert)
            db.commit()
            db.refresh(expert)
        else:
            expert.title = exp_data["title"]
            expert.company = exp_data["company"]
            expert.experience_years = exp_data["experience_years"]
            expert.bio = exp_data["bio"]
            expert.skills = exp_data.get("skills")
            expert.hourly_rate = exp_data["hourly_rate"]
            expert.rating = exp_data["rating"]
            expert.is_verified = exp_data["is_verified"]
            expert.verification_status = exp_data["verification_status"]
            expert.rejection_reason = exp_data.get("rejection_reason")
            expert.is_active = exp_data["is_active"]
            db.commit()

        # Seed verification entry
        verification = db.query(ExpertVerification).filter(ExpertVerification.user_id == user.id).first()
        if not verification:
            verification = ExpertVerification(
                user_id=user.id,
                certificate_url=f"https://credentials.example.com/{user.id}/cert.pdf",
                resume_url=f"https://credentials.example.com/{user.id}/resume.pdf",
                linkedin_url=f"https://linkedin.com/in/{user.name.lower().replace(' ', '')}",
                experience_years=exp_data["experience_years"],
                status=exp_data["verification_status"],
            )
            db.add(verification)
            db.commit()

        # Seed documents & index in FAISS
        for doc_item in exp_data.get("documents", []):
            existing_doc = (
                db.query(Document)
                .filter(Document.expert_id == expert.id, Document.title == doc_item["title"])
                .first()
            )
            if not existing_doc:
                new_doc = Document(
                    expert_id=expert.id,
                    title=doc_item["title"],
                    text=doc_item["text"],
                    file_type=doc_item["file_type"],
                    category=doc_item.get("category", "general"),
                    status="approved" if exp_data["is_verified"] else "pending",
                )
                db.add(new_doc)
                db.commit()
                try:
                    add_documents_to_expert(expert.id, [doc_item])
                except Exception:
                    pass

    # 3. Seed Sample Booking for Learner Rohan Verma
    rohan = db.query(User).filter(User.email == "rohan@example.com").first()
    arjun_exp = (
        db.query(Expert)
        .join(User, Expert.user_id == User.id)
        .filter(User.email == "arjun@example.com")
        .first()
    )

    if rohan and arjun_exp:
        existing_booking = (
            db.query(Booking)
            .filter(Booking.user_id == rohan.id, Booking.expert_id == arjun_exp.id)
            .first()
        )
        if not existing_booking:
            booking = Booking(
                user_id=rohan.id,
                expert_id=arjun_exp.id,
                slot=datetime.utcnow() + timedelta(days=3),
                duration_minutes=60,
                status="confirmed",
                payment_status="paid",
                amount=arjun_exp.hourly_rate,
                meeting_link=f"https://meet.jit.si/expertverse-demo-{rohan.id}-{arjun_exp.id}",
                learner_notes="Looking forward to reviewing our enterprise AI roadmap and RAG architecture.",
            )
            db.add(booking)
            db.commit()