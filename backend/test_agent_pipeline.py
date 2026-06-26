import sys
from sqlalchemy.orm import Session
sys.path.insert(0, '.')

from app.db.session import SessionLocal
from app.models.user import User
from app.models.expert import Expert
from app.models.document import Document
from app.services.vector_store import initialize_vector_store, query_expert_documents
from app.services.agents import analyze_problem, match_experts, generate_roadmap
from app.routes.auth import get_password_hash


def setup_data(db: Session):
    db.query(Document).delete()
    db.query(Expert).delete()
    db.query(User).delete()
    db.commit()

    user = User(name='Test User', email='test@example.com', password_hash=get_password_hash('password'), role='user')
    db.add(user)
    db.commit()
    db.refresh(user)

    expert = Expert(user_id=user.id, title='AI Strategy Expert', company='ExpertVerse', experience_years=8, bio='AI strategy and product planning.', hourly_rate=180.0, rating=4.9)
    db.add(expert)
    db.commit()
    db.refresh(expert)

    doc = Document(expert_id=expert.id, file_type='text', text='This expert helps build AI product roadmaps, strategy, and execution plans.')
    db.add(doc)
    db.commit()
    db.refresh(doc)
    return user, expert


def main():
    db = SessionLocal()
    try:
        user, expert = setup_data(db)
        initialize_vector_store(db)

        query = 'I need help planning an AI product roadmap and finding an expert.'
        print('query_expert_documents:', query_expert_documents(query, top_k=3))
        print('analyze_problem:', analyze_problem(db, query))
        print('match_experts:', match_experts(db, query))
        print('generate_roadmap:', generate_roadmap(db, query))
    finally:
        db.close()


if __name__ == '__main__':
    main()
