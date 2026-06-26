from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.schemas.chat import ChatRequest, ChatResponse
from app.schemas.chat_history import ChatHistoryRead
from app.models.chat_history import ChatHistory
from app.db.session import get_db
from app.routes.auth import get_current_user
from app.services.agents import analyze_problem, match_experts, generate_roadmap, save_chat_history, save_action_plan

router = APIRouter()

@router.post("/analyze", response_model=dict)
def analyze(request: ChatRequest, current_user=Depends(get_current_user), db: Session = Depends(get_db)):
    return analyze_problem(db, request.message)

@router.post("/match", response_model=list[dict])
def match(request: ChatRequest, current_user=Depends(get_current_user), db: Session = Depends(get_db)):
    return match_experts(db, request.message)

@router.post("/roadmap", response_model=dict)
def roadmap(request: ChatRequest, current_user=Depends(get_current_user), db: Session = Depends(get_db)):
    return generate_roadmap(db, request.message)

@router.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest, current_user=Depends(get_current_user), db: Session = Depends(get_db)):
    analysis = analyze_problem(db, request.message)
    experts = match_experts(db, request.message)
    plan = generate_roadmap(db, request.message)
    save_chat_history(db, current_user.id, request.message, analysis.get("analysis_text", ""))
    save_action_plan(db, current_user.id, str(plan))
    return ChatResponse(
        message="Here is your plan and recommendation.",
        recommended_experts=experts[:5],
        roadmap=plan,
    )


@router.get("/history", response_model=list[ChatHistoryRead])
def get_history(current_user=Depends(get_current_user), db: Session = Depends(get_db)):
    records = db.query(ChatHistory).filter(ChatHistory.user_id == current_user.id).order_by(ChatHistory.created_at.desc()).all()
    return records
