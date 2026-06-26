from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.models.booking import Booking
from app.models.expert import Expert
from app.schemas.booking import BookingCreate, BookingRead
from app.routes.auth import get_current_user

router = APIRouter()

@router.post("/create", response_model=BookingRead)
def create_booking(booking_create: BookingCreate, current_user=Depends(get_current_user), db: Session = Depends(get_db)):
    expert = db.query(Expert).get(booking_create.expert_id)
    if not expert:
        raise HTTPException(status_code=404, detail="Expert not found")
    booking = Booking(
        user_id=current_user.id,
        expert_id=booking_create.expert_id,
        slot=booking_create.slot,
        status="confirmed",
    )
    db.add(booking)
    db.commit()
    db.refresh(booking)
    return booking

@router.get("/list", response_model=list[BookingRead])
def list_bookings(current_user=Depends(get_current_user), db: Session = Depends(get_db)):
    return db.query(Booking).filter(Booking.user_id == current_user.id).all()

@router.post("/cancel/{booking_id}", response_model=BookingRead)
def cancel_booking(booking_id: int, current_user=Depends(get_current_user), db: Session = Depends(get_db)):
    booking = db.query(Booking).get(booking_id)
    if not booking or booking.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Booking not found")
    booking.status = "cancelled"
    db.commit()
    db.refresh(booking)
    return booking
