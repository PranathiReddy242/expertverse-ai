from datetime import datetime
from typing import Any
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.db.session import get_db
from app.models.booking import Booking
from app.models.expert import Expert
from app.models.user import User
from app.models.document import Document
from app.models.expert_verification import ExpertVerification
from app.schemas.expert import ExpertReviewAction
from app.schemas.document import DocumentReview
from app.routes.auth import get_current_user
from app.services.llm_service import llm_service

router = APIRouter()


def require_admin(current_user: User = Depends(get_current_user)):
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required",
        )
    return current_user


class AdminAIChatRequest(BaseModel):
    query: str


@router.get("/summary")
def admin_summary(
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    total_users = db.query(User).count()
    total_experts = db.query(Expert).count()
    pending_experts = db.query(Expert).filter(Expert.is_verified == False, Expert.verification_status != "rejected").count()
    approved_experts = db.query(Expert).filter(Expert.is_verified == True).count()
    rejected_experts = db.query(Expert).filter(Expert.verification_status == "rejected").count()
    total_bookings = db.query(Booking).count()
    pending_bookings = db.query(Booking).filter(Booking.status == "pending").count()
    completed_bookings = db.query(Booking).filter(Booking.status == "completed").count()
    paid_bookings = db.query(Booking).filter(Booking.payment_status == "paid").count()
    total_revenue = db.query(func.sum(Booking.amount)).filter(Booking.payment_status == "paid").scalar() or 0.0
    pending_documents = db.query(Document).filter(Document.status == "pending").count()

    return {
        "users": total_users,
        "experts": total_experts,
        "pending_experts": pending_experts,
        "approved_experts": approved_experts,
        "rejected_experts": rejected_experts,
        "bookings": total_bookings,
        "pending_bookings": pending_bookings,
        "completed_bookings": completed_bookings,
        "paid_bookings": paid_bookings,
        "total_revenue": round(float(total_revenue), 2),
        "pending_documents": pending_documents,
    }


@router.get("/users")
def list_users(
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    users = db.query(User).order_by(User.id.asc()).all()

    return [
        {
            "id": user.id,
            "name": user.name,
            "email": user.email,
            "is_learner": user.is_learner,
            "is_expert": user.is_expert,
            "is_admin": user.is_admin,
            "created_at": user.created_at,
        }
        for user in users
    ]


@router.get("/experts")
def list_experts(
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    experts = db.query(Expert).order_by(Expert.id.asc()).all()

    return [
        {
            "id": expert.id,
            "user_id": expert.user_id,
            "name": expert.user.name if expert.user else "Expert",
            "email": expert.user.email if expert.user else None,
            "title": expert.title,
            "company": expert.company,
            "experience_years": expert.experience_years,
            "hourly_rate": expert.hourly_rate,
            "rating": expert.rating,
            "is_verified": expert.is_verified,
            "verification_status": expert.verification_status or ("approved" if expert.is_verified else "pending"),
            "rejection_reason": expert.rejection_reason,
            "reviewed_at": expert.reviewed_at,
            "is_active": expert.is_active,
        }
        for expert in experts
    ]


@router.get("/pending-verifications")
def get_pending_verifications(
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    pending_experts = (
        db.query(Expert)
        .filter(Expert.is_verified == False)
        .order_by(Expert.id.desc())
        .all()
    )

    results = []
    for exp in pending_experts:
        verification = db.query(ExpertVerification).filter(ExpertVerification.user_id == exp.user_id).first()
        docs = db.query(Document).filter(Document.expert_id == exp.id).all()
        results.append({
            "expert_id": exp.id,
            "user_id": exp.user_id,
            "name": exp.user.name if exp.user else "Applicant",
            "email": exp.user.email if exp.user else None,
            "title": exp.title,
            "company": exp.company,
            "experience_years": exp.experience_years,
            "hourly_rate": exp.hourly_rate,
            "bio": exp.bio,
            "skills": exp.skills,
            "verification_status": exp.verification_status or "pending",
            "rejection_reason": exp.rejection_reason,
            "certificate_url": verification.certificate_url if verification else None,
            "resume_url": verification.resume_url if verification else None,
            "linkedin_url": exp.linkedin_url or (verification.linkedin_url if verification else None),
            "submitted_at": verification.created_at if verification else None,
            "documents": [
                {
                    "id": d.id,
                    "title": d.title or d.file_url or f"Doc #{d.id}",
                    "file_type": d.file_type,
                    "status": d.status,
                    "created_at": d.created_at,
                }
                for d in docs
            ],
        })

    return results


@router.post("/experts/{expert_id}/approve")
def approve_expert(
    expert_id: int,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    expert = db.get(Expert, expert_id)
    if not expert:
        raise HTTPException(status_code=404, detail="Expert not found")

    expert.is_verified = True
    expert.verification_status = "approved"
    expert.is_active = True
    expert.rejection_reason = None
    expert.reviewed_at = datetime.utcnow()

    # Also update ExpertVerification record if exists
    verification = db.query(ExpertVerification).filter(ExpertVerification.user_id == expert.user_id).first()
    if verification:
        verification.status = "approved"

    # Auto-approve supporting credential documents
    docs = db.query(Document).filter(Document.expert_id == expert.id).all()
    for d in docs:
        if d.status == "pending":
            d.status = "approved"
            d.reviewed_at = datetime.utcnow()

    db.commit()
    db.refresh(expert)

    return {
        "status": "success",
        "message": f"Expert {expert.title} (ID: {expert.id}) approved successfully. Profile is now publicly active and bookable.",
        "expert_id": expert.id,
        "is_verified": expert.is_verified,
        "verification_status": expert.verification_status,
    }


@router.post("/experts/{expert_id}/reject")
def reject_expert(
    expert_id: int,
    action: ExpertReviewAction,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    expert = db.get(Expert, expert_id)
    if not expert:
        raise HTTPException(status_code=404, detail="Expert not found")

    reason = action.reason or "Application did not meet our verification criteria."
    expert.is_verified = False
    expert.verification_status = "rejected"
    expert.is_active = False
    expert.rejection_reason = reason
    expert.reviewed_at = datetime.utcnow()

    verification = db.query(ExpertVerification).filter(ExpertVerification.user_id == expert.user_id).first()
    if verification:
        verification.status = "rejected"

    db.commit()
    db.refresh(expert)

    return {
        "status": "success",
        "message": f"Expert application {expert.id} rejected.",
        "expert_id": expert.id,
        "is_verified": expert.is_verified,
        "verification_status": expert.verification_status,
        "rejection_reason": expert.rejection_reason,
    }


@router.post("/documents/{document_id}/review")
def review_document(
    document_id: int,
    review: DocumentReview,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    doc = db.get(Document, document_id)
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")

    doc.status = review.status.lower()
    doc.review_notes = review.review_notes
    doc.reviewed_at = datetime.utcnow()

    db.commit()
    db.refresh(doc)

    return {
        "status": "success",
        "document_id": doc.id,
        "document_status": doc.status,
        "review_notes": doc.review_notes,
    }


@router.get("/bookings")
def list_bookings(
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    bookings = db.query(Booking).order_by(Booking.id.desc()).all()

    return [
        {
            "id": booking.id,
            "user_id": booking.user_id,
            "learner": booking.user.name if booking.user else None,
            "expert_id": booking.expert_id,
            "expert": booking.expert.title if booking.expert else None,
            "slot": booking.slot,
            "status": booking.status,
            "payment_status": booking.payment_status,
            "amount": booking.amount,
            "created_at": booking.created_at,
        }
        for booking in bookings
    ]


@router.post("/ai-assistant")
def admin_ai_assistant(
    request: AdminAIChatRequest,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    """
    Administrative AI Assistant that queries live database metrics
    and generates a truthful, actionable platform report without fabricating statistics.
    """
    total_users = db.query(User).count()
    total_experts = db.query(Expert).count()
    approved_experts = db.query(Expert).filter(Expert.is_verified == True).count()
    pending_experts = db.query(Expert).filter(Expert.is_verified == False, Expert.verification_status != "rejected").count()
    rejected_experts = db.query(Expert).filter(Expert.verification_status == "rejected").count()
    total_bookings = db.query(Booking).count()
    pending_bookings = db.query(Booking).filter(Booking.status == "pending").count()
    paid_bookings = db.query(Booking).filter(Booking.payment_status == "paid").count()
    total_revenue = db.query(func.sum(Booking.amount)).filter(Booking.payment_status == "paid").scalar() or 0.0

    recent_experts = db.query(Expert).order_by(Expert.id.desc()).limit(3).all()
    recent_expert_titles = [f"{e.title} (Status: {e.verification_status or ('approved' if e.is_verified else 'pending')})" for e in recent_experts]

    prompt = f"""You are the ExpertVerse AI Platform Administrator Assistant.
Live Application Data:
- Total Registered Users: {total_users}
- Total Experts: {total_experts} (Approved: {approved_experts}, Pending Review: {pending_experts}, Rejected: {rejected_experts})
- Bookings: {total_bookings} total (Pending: {pending_bookings}, Paid: {paid_bookings})
- Total Confirmed Revenue: ${total_revenue:.2f}
- Recent Expert Profiles: {", ".join(recent_expert_titles) or "None"}

Admin Query:
"{request.query}"

Provide a concise, direct, and completely accurate response based strictly on the above live data. Never fabricate metrics. Outline any action items required by the administrator."""

    response = llm_service.generate_text(prompt)
    if not response or len(response.strip()) < 30:
        # High quality local fallback based on live counts
        response = (
            f"**ExpertVerse Platform Executive Summary**:\n\n"
            f"• **Users**: {total_users} registered users ({approved_experts} verified active experts, {pending_experts} pending reviews).\n"
            f"• **Verification Queue**: There are currently **{pending_experts}** expert applications awaiting your review.\n"
            f"• **Operations**: {total_bookings} bookings on record ({paid_bookings} paid, {pending_bookings} pending).\n"
            f"• **Revenue**: ${total_revenue:.2f} total processed.\n\n"
            f"**Recommended Action**: Review the {pending_experts} pending expert application(s) in the Action Required queue to maintain quality governance."
        )

    return {
        "query": request.query,
        "answer": response,
        "metrics_snapshot": {
            "total_users": total_users,
            "approved_experts": approved_experts,
            "pending_experts": pending_experts,
            "rejected_experts": rejected_experts,
            "total_bookings": total_bookings,
            "total_revenue": total_revenue,
        }
    }
