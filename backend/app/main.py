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
    allow_origins=[
        "http://localhost:5173",
        "http://localhost:5174",
        "http://localhost:3000",
        "http://localhost:3001",
        "http://localhost:4000",
        "http://localhost:8080",
        "http://localhost:5180",
        "http://127.0.0.1:5173",
        "http://127.0.0.1:5174",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:3001",
        "http://127.0.0.1:4000",
        "http://127.0.0.1:8080",
        "http://127.0.0.1:5180",
    ],
    allow_origin_regex=r"^http://(localhost|127\.0\.0\.1)(:\d+)?$",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
def startup_event():
    from migrate_schema import run_migration
    run_migration()
    base.Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        seed(db)
        initialize_vector_store(db)
    finally:
        db.close()

app.include_router(auth.router, prefix="/auth", tags=["auth"])
app.include_router(experts.router, prefix="/experts", tags=["experts"])
app.include_router(bookings.router, prefix="/bookings", tags=["bookings"])
app.include_router(agents.router, prefix="/agents", tags=["agents"])
app.include_router(documents.router, prefix="/documents", tags=["documents"])
app.include_router(admin.router, prefix="/admin", tags=["admin"])
