from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.expert import Expert
from app.models.user import User
from app.schemas.expert import ExpertCreate, ExpertRead
from app.routes.auth import get_current_user

router = APIRouter(prefix="/experts", tags=["Experts"])


@router.post("/create", response_model=ExpertRead)
def create_expert(
    expert_create: ExpertCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if not current_user.is_expert:
        raise HTTPException(
            status_code=403,
            detail="Enable expert mode before creating an expert profile."
        )

    existing = (
        db.query(Expert)
        .filter(Expert.user_id == current_user.id)
        .first()
    )

    if existing:
        raise HTTPException(
            status_code=400,
            detail="Expert profile already exists."
        )

    expert = Expert(
        user_id=current_user.id,
        title=expert_create.title,
        company=expert_create.company,
        experience_years=expert_create.experience_years,
        bio=expert_create.bio,
        hourly_rate=expert_create.hourly_rate,
    )

    db.add(expert)
    db.commit()
    db.refresh(expert)

    return expert


@router.get("/list", response_model=list[ExpertRead])
def list_experts(
    q: str | None = Query(None),
    db: Session =Depends(get_db),
):

    query = db.query(Expert)

    if q:
        search = f"%{q}%"

        query = query.filter(
            Expert.title.ilike(search)
            | Expert.company.ilike(search)
            | Expert.bio.ilike(search)
        )

    return query.all()


@router.get("/details/{expert_id}", response_model=ExpertRead)
def expert_details(
    expert_id: int,
    db: Session = Depends(get_db),
):

    expert = db.get(Expert, expert_id)

    if not expert:
        raise HTTPException(
            status_code=404,
            detail="Expert not found."
        )

    return expert


@router.get("/me", response_model=ExpertRead)
def my_profile(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):

    expert = (
        db.query(Expert)
        .filter(Expert.user_id == current_user.id)
        .first()
    )

    if not expert:
        raise HTTPException(
            status_code=404,
            detail="Expert profile not found."
        )

    return expert


@router.put("/update", response_model=ExpertRead)
def update_profile(
    expert_create: ExpertCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):

    expert = (
        db.query(Expert)
        .filter(Expert.user_id == current_user.id)
        .first()
    )

    if not expert:
        raise HTTPException(
            status_code=404,
            detail="Expert profile not found."
        )

    expert.title = expert_create.title
    expert.company = expert_create.company
    expert.experience_years = expert_create.experience_years
    expert.bio = expert_create.bio
    expert.hourly_rate = expert_create.hourly_rate

    db.commit()
    db.refresh(expert)

    return expert