from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routes import auth, experts, bookings, agents, documents, admin
from app.db.session import engine, SessionLocal
from app.models import base
from app.services.seed import seed
from app.services.vector_store import initialize_vector_store

app = FastAPI(
    title="ExpertVerse AI",
    version="0.1.0",
    description="AI-powered expertise marketplace with expert matching, booking, and planning.",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_origin_regex=r"^https://.*\.vercel\.app$",
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
def startup_event():
    try:
        from migrate_schema import run_migration
        run_migration()
        base.Base.metadata.create_all(bind=engine)
        db = SessionLocal()
        try:
            from app.models.user import User
            user_count = db.query(User).count()
            if user_count == 0:
                seed(db)
            initialize_vector_store(db)
        finally:
            db.close()
    except Exception as e:
        print(f"Startup initialization note: {e}")

app.include_router(auth.router, prefix="/auth", tags=["auth"])
app.include_router(experts.router, prefix="/experts", tags=["experts"])
app.include_router(bookings.router, prefix="/bookings", tags=["bookings"])
app.include_router(agents.router, prefix="/agents", tags=["agents"])
app.include_router(documents.router, prefix="/documents", tags=["documents"])
app.include_router(admin.router, prefix="/admin", tags=["admin"])
