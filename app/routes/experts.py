from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, Query, Header
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.expert import Expert
from app.models.user import User
from app.models.expert_verification import ExpertVerification
from app.schemas.expert import ExpertCreate, ExpertRead, ExpertVerificationSubmit
from app.routes.auth import get_current_user
from app.core.config import settings
from jose import jwt, JWTError

router = APIRouter(tags=["Experts"])


def _optional_current_user(authorization: str | None = Header(None), db: Session = Depends(get_db)) -> User | None:
    if not authorization or not authorization.startswith("Bearer "):
        return None
    token = authorization.split(" ")[1]
    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=["HS256"])
        user_id = payload.get("user_id")
        if user_id:
            return db.query(User).filter(User.id == user_id).first()
    except JWTError:
        pass
    return None


@router.post("/become-expert")
def become_expert(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if current_user.is_expert:
        return {
            "message": "You are already an expert.",
            "is_expert": True,
        }

    current_user.is_expert = True
    db.commit()
    db.refresh(current_user)

    return {
        "message": "Expert mode enabled successfully.",
        "is_expert": True,
    }


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
        skills=expert_create.skills,
        profile_image=expert_create.profile_image,
        linkedin_url=expert_create.linkedin_url,
        github_url=expert_create.github_url,
        website_url=expert_create.website_url,
        hourly_rate=expert_create.hourly_rate,
        is_verified=False,
        verification_status="pending",
        is_active=True,
    )

    db.add(expert)
    db.commit()
    db.refresh(expert)

    return expert


@router.get("/list", response_model=list[ExpertRead])
def list_experts(
    q: str | None = Query(None),
    all_statuses: bool = Query(False),
    db: Session = Depends(get_db),
    optional_user: User | None = Depends(_optional_current_user),
):
    query = db.query(Expert)

    # Only admins can view unverified/rejected experts in the full listing
    is_admin = isinstance(optional_user, User) and optional_user.is_admin
    if not all_statuses or not is_admin:
        query = query.filter(Expert.is_verified == True, Expert.is_active == True)

    if q and isinstance(q, str) and q.strip():
        search = f"%{q.strip()}%"
        query = query.filter(
            Expert.title.ilike(search)
            | Expert.company.ilike(search)
            | Expert.bio.ilike(search)
            | Expert.skills.ilike(search)
        )

    return query.order_by(Expert.rating.desc(), Expert.experience_years.desc()).all()


@router.get("/details/{expert_id}", response_model=ExpertRead)
def expert_details(
    expert_id: int,
    db: Session = Depends(get_db),
    optional_user: User | None = Depends(_optional_current_user),
):
    expert = db.get(Expert, expert_id)

    if not expert:
        raise HTTPException(
            status_code=404,
            detail="Expert not found."
        )

    # If expert is not verified, only admin or the expert themselves can view it
    if not expert.is_verified:
        is_owner = isinstance(optional_user, User) and optional_user.id == expert.user_id
        is_admin = isinstance(optional_user, User) and optional_user.is_admin
        if not is_owner and not is_admin:
            raise HTTPException(
                status_code=403,
                detail="Expert application is pending verification and is not publicly accessible."
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
    expert.skills = expert_create.skills
    expert.profile_image = expert_create.profile_image
    expert.linkedin_url = expert_create.linkedin_url
    expert.github_url = expert_create.github_url
    expert.website_url = expert_create.website_url
    expert.hourly_rate = expert_create.hourly_rate

    db.commit()
    db.refresh(expert)

    return expert


@router.post("/submit-verification")
def submit_verification(
    payload: ExpertVerificationSubmit,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    expert = db.query(Expert).filter(Expert.user_id == current_user.id).first()
    if not expert:
        expert = Expert(
            user_id=current_user.id,
            title="Expert Contributor",
            company="Independent",
            experience_years=payload.experience_years or 1,
            hourly_rate=100.0,
            is_verified=False,
            verification_status="pending",
            is_active=True,
        )
        db.add(expert)
        db.commit()
        db.refresh(expert)

    verification = db.query(ExpertVerification).filter(ExpertVerification.user_id == current_user.id).first()
    if not verification:
        verification = ExpertVerification(
            user_id=current_user.id,
            certificate_url=payload.certificate_url,
            resume_url=payload.resume_url,
            linkedin_url=payload.linkedin_url or expert.linkedin_url,
            experience_years=payload.experience_years or expert.experience_years,
            status="pending",
        )
        db.add(verification)
    else:
        verification.certificate_url = payload.certificate_url or verification.certificate_url
        verification.resume_url = payload.resume_url or verification.resume_url
        verification.linkedin_url = payload.linkedin_url or verification.linkedin_url
        verification.experience_years = payload.experience_years or verification.experience_years
        verification.status = "pending"

    expert.verification_status = "pending"
    expert.is_verified = False
    expert.rejection_reason = None
    db.commit()
    db.refresh(expert)
    db.refresh(verification)

    return {
        "status": "success",
        "message": "Verification application submitted successfully. It is currently under administrative review.",
        "verification_id": verification.id,
        "expert_id": expert.id,
        "verification_status": "pending",
    }


@router.get("/my-verification")
def get_my_verification(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    expert = db.query(Expert).filter(Expert.user_id == current_user.id).first()
    if not expert:
        raise HTTPException(status_code=404, detail="Expert profile not found.")

    verification = db.query(ExpertVerification).filter(ExpertVerification.user_id == current_user.id).first()
    return {
        "expert_id": expert.id,
        "is_verified": expert.is_verified,
        "verification_status": expert.verification_status,
        "rejection_reason": expert.rejection_reason,
        "reviewed_at": expert.reviewed_at,
        "is_active": expert.is_active,
        "verification_details": {
            "certificate_url": verification.certificate_url if verification else None,
            "resume_url": verification.resume_url if verification else None,
            "linkedin_url": verification.linkedin_url if verification else None,
            "experience_years": verification.experience_years if verification else expert.experience_years,
            "submitted_at": verification.created_at if verification else None,
        } if verification else None,
    }