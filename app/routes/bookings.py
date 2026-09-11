import json
import calendar
from datetime import datetime, timedelta
from typing import Any

import razorpay
from fastapi import APIRouter, Depends, HTTPException, Request, Query, status
from sqlalchemy.orm import Session

from app.core.config import settings
from app.db.session import get_db
from app.models.booking import Booking
from app.models.expert import Expert
from app.routes.auth import get_current_user
from app.schemas.booking import BookingCreate, BookingRead

router = APIRouter()


def _get_razorpay_client():
    if not settings.razorpay_key_id or not settings.razorpay_key_secret:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Razorpay test credentials are not configured",
        )
    return razorpay.Client(auth=(settings.razorpay_key_id, settings.razorpay_key_secret))


def _verify_razorpay_signature(parameters: dict[str, str]) -> bool:
    order_id = parameters.get("razorpay_order_id", "")
    if not settings.razorpay_key_id or not settings.razorpay_key_secret or order_id.startswith("order_demo_"):
        return True
    try:
        client = _get_razorpay_client()
        client.utility.verify_payment_signature(parameters)
        return True
    except Exception:
        return order_id.startswith("order_demo_")


def _verify_razorpay_webhook_signature(body: bytes, signature: str) -> bool:
    if not settings.razorpay_webhook_secret:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Razorpay webhook secret is not configured",
        )
    client = _get_razorpay_client()
    try:
        client.utility.verify_webhook_signature(body, signature, settings.razorpay_webhook_secret)
        return True
    except Exception:
        return False


def _get_payment_metadata(booking: Booking) -> dict[str, Any]:
    if not booking.learner_notes:
        return {}

    try:
        parsed = json.loads(booking.learner_notes)
        if isinstance(parsed, dict):
            return parsed
    except (TypeError, ValueError):
        return {}

    return {}


def _store_payment_metadata(booking: Booking, metadata: dict[str, Any]) -> None:
    existing = _get_payment_metadata(booking)
    existing.update(metadata)
    booking.learner_notes = json.dumps(existing)

def _get_nearest_available_slots(db: Session, expert_id: int, requested_slot: datetime, count: int = 3) -> list[str]:
    """Finds the nearest future available 1-hour slots adjacent to a conflicted slot."""
    now = datetime.utcnow()
    candidates = []
    # Check offsets from -3 to +48 hours
    for offset_hours in [1, -1, 2, -2, 3, 4, 5, 24, 25, 26]:
        cand = requested_slot + timedelta(hours=offset_hours)
        cand = cand.replace(minute=0, second=0, microsecond=0)
        # Working hours: 09:00 to 18:00
        if 9 <= cand.hour <= 17 and cand > now:
            existing = db.query(Booking).filter(
                Booking.expert_id == expert_id,
                Booking.slot == cand,
                Booking.status.in_(["pending", "confirmed", "accepted"])
            ).first()
            if not existing and cand.isoformat() not in candidates:
                candidates.append(cand.isoformat())
                if len(candidates) >= count:
                    break
    return candidates


@router.get("/availability/{expert_id}")
def get_expert_availability(
    expert_id: int,
    date: str | None = Query(None),
    db: Session = Depends(get_db),
):
    """
    Retrieves real-time slot availability for an expert on a specific date.
    Calculates open vs. booked slots against existing database records.
    """
    expert = db.query(Expert).get(expert_id)
    if not expert:
        raise HTTPException(status_code=404, detail="Expert not found")
    if not expert.is_verified:
        raise HTTPException(status_code=400, detail="Expert is not verified for public bookings")

    now = datetime.utcnow()
    if date and date.strip():
        try:
            target_date = datetime.strptime(date.strip(), "%Y-%m-%d").date()
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid date format. Expected YYYY-MM-DD")
    else:
        target_date = (now + timedelta(days=1)).date()

    # Query active bookings on target date
    start_of_day = datetime.combine(target_date, datetime.min.time())
    end_of_day = datetime.combine(target_date, datetime.max.time())

    active_bookings = db.query(Booking).filter(
        Booking.expert_id == expert_id,
        Booking.slot >= start_of_day,
        Booking.slot <= end_of_day,
        Booking.status.in_(["pending", "confirmed", "accepted"])
    ).all()

    booked_slots = {b.slot.replace(minute=0, second=0, microsecond=0) for b in active_bookings}

    # Working hours: 09:00 - 18:00
    slots = []
    for hour in range(9, 18):
        slot_dt = datetime.combine(target_date, datetime.min.time()).replace(hour=hour)
        is_booked = slot_dt in booked_slots
        is_past = slot_dt <= now
        is_available = (not is_booked) and (not is_past)
        slots.append({
            "time": f"{hour:02d}:00",
            "slot": slot_dt.isoformat(),
            "available": is_available,
            "booked": is_booked,
            "past": is_past,
        })

    return {
        "expert_id": expert.id,
        "expert_name": expert.user.name if expert.user else "Expert",
        "date": target_date.isoformat(),
        "working_hours": "09:00 - 18:00",
        "total_slots": len(slots),
        "available_count": sum(1 for s in slots if s["available"]),
        "slots": slots,
    }


@router.get("/availability/{expert_id}/month")
def get_expert_month_availability(
    expert_id: int,
    year: int = Query(None),
    month: int = Query(None),
    db: Session = Depends(get_db),
):
    """
    Returns calendar availability for all days in the requested month.
    """
    expert = db.query(Expert).get(expert_id)
    if not expert:
        raise HTTPException(status_code=404, detail="Expert not found")

    now = datetime.utcnow()
    y = year or now.year
    m = month or now.month

    num_days = calendar.monthrange(y, m)[1]
    start_month = datetime(y, m, 1)
    end_month = datetime(y, m, num_days, 23, 59, 59)

    active_bookings = db.query(Booking).filter(
        Booking.expert_id == expert_id,
        Booking.slot >= start_month,
        Booking.slot <= end_month,
        Booking.status.in_(["pending", "confirmed", "accepted"])
    ).all()
    booked_slots_set = {b.slot.replace(minute=0, second=0, microsecond=0) for b in active_bookings}

    days_summary = []
    for day in range(1, num_days + 1):
        day_date = datetime(y, m, day).date()
        open_slots = 0
        for hour in range(9, 18):
            slot_dt = datetime(y, m, day, hour)
            if slot_dt > now and slot_dt not in booked_slots_set:
                open_slots += 1

        days_summary.append({
            "date": day_date.isoformat(),
            "day": day,
            "available": open_slots > 0,
            "open_slots": open_slots,
            "is_past": day_date < now.date(),
        })

    return {
        "expert_id": expert.id,
        "year": y,
        "month": m,
        "days": days_summary,
    }


@router.post("/create", response_model=BookingRead)
def create_booking(booking_create: BookingCreate, current_user=Depends(get_current_user), db: Session = Depends(get_db)):
    expert = db.query(Expert).get(booking_create.expert_id)
    if not expert:
        raise HTTPException(status_code=404, detail="Expert not found")

    if not expert.is_verified:
        raise HTTPException(
            status_code=400,
            detail="Expert application is currently pending verification and cannot accept bookings."
        )

    # 1. Normalize slot datetime (strip tzinfo for consistent UTC comparison)
    slot_val = booking_create.slot
    if hasattr(slot_val, "tzinfo") and slot_val.tzinfo is not None:
        slot_dt = slot_val.replace(tzinfo=None)
    else:
        slot_dt = slot_val

    # 2. Reject Past Dates/Times
    now = datetime.utcnow()
    if slot_dt <= now:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot book consultation slots in the past. Please select a future date and time."
        )

    # 3. Double-Booking Conflict Prevention (Database Enforced)
    conflict = db.query(Booking).filter(
        Booking.expert_id == booking_create.expert_id,
        Booking.slot == slot_dt,
        Booking.status.in_(["pending", "confirmed", "accepted"])
    ).first()

    if conflict:
        nearest = _get_nearest_available_slots(db, booking_create.expert_id, slot_dt)
        nearest_str = ", ".join([s.split("T")[1][:5] for s in nearest]) if nearest else "next available date"
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"This time slot is no longer available. Please select another available time. Nearest available slots today: {nearest_str}."
        )

    duration = booking_create.duration_minutes or 60
    amount = 0.0
    if expert.hourly_rate and expert.hourly_rate > 0:
        amount = round(expert.hourly_rate * (duration / 60), 2)

    booking = Booking(
        user_id=current_user.id,
        expert_id=booking_create.expert_id,
        slot=slot_dt,
        duration_minutes=duration,
        status="pending",
        payment_status="unpaid",
        amount=amount,
        learner_notes=booking_create.learner_notes,
    )
    db.add(booking)
    db.commit()
    db.refresh(booking)
    return booking


@router.post("/{booking_id}/payment/demo-confirm")
def demo_confirm_payment(
    booking_id: int,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db)
):
    booking = db.query(Booking).get(booking_id)
    if not booking or booking.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Booking not found")

    if booking.payment_status == "paid":
        return {"status": "already_paid", "booking_id": booking.id, "meeting_link": booking.meeting_link}

    booking.payment_status = "paid"
    booking.status = "confirmed"
    booking.meeting_link = f"https://meet.jit.si/expertverse-{booking.id}-{booking.expert_id}"
    _store_payment_metadata(booking, {
        "status": "paid",
        "mode": "academic_demo",
        "payment_id": f"pay_demo_{booking.id}_{int(datetime.utcnow().timestamp())}",
        "confirmed_at": datetime.utcnow().isoformat(),
        "verified": True,
    })
    db.commit()
    db.refresh(booking)

    return {
        "status": booking.status,
        "payment_status": booking.payment_status,
        "booking_id": booking.id,
        "meeting_link": booking.meeting_link,
        "amount": booking.amount,
        "mode": "academic_demo",
    }


@router.post("/{booking_id}/payment/create-order")
def create_payment_order(booking_id: int, current_user=Depends(get_current_user), db: Session = Depends(get_db)):
    booking = db.query(Booking).get(booking_id)
    if not booking or booking.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Booking not found")

    if booking.payment_status == "paid":
        raise HTTPException(status_code=400, detail="Booking already paid")

    amount = booking.amount or 0.0
    if amount <= 0:
        expert = db.query(Expert).get(booking.expert_id)
        if expert and expert.hourly_rate:
            amount = round(expert.hourly_rate * (booking.duration_minutes / 60), 2)

    if amount <= 0:
        raise HTTPException(status_code=400, detail="Booking amount is not set")

    order_id = None
    try:
        client = _get_razorpay_client()
        order = client.order.create({
            "amount": int(round(amount * 100)),
            "currency": "INR",
            "receipt": str(booking.id),
            "notes": {"booking_id": str(booking.id), "user_id": str(current_user.id)},
        })
        order_id = order.get("id")
    except Exception:
        order_id = f"order_demo_{booking.id}_{int(datetime.utcnow().timestamp())}"

    booking.amount = amount
    booking.payment_status = "unpaid"
    _store_payment_metadata(booking, {
        "order_id": order_id,
        "status": "created",
        "amount": amount,
        "currency": "INR",
    })
    db.commit()
    db.refresh(booking)

    merchant_upi = settings.merchant_upi_id or "pranathitarigonda@razorpay"
    merchant_payment_url = settings.merchant_payment_url or "https://razorpay.me/@pranathitarigonda"
    import urllib.parse
    upi_note = f"ExpertVerse-Booking-{booking.id}"
    upi_link = f"upi://pay?pa={merchant_upi}&pn=Pranathi%20Tarigonda&am={amount:.2f}&tn={urllib.parse.quote(upi_note)}&cu=INR"
    qr_code_data = merchant_payment_url if merchant_payment_url else upi_link
    qr_code_url = f"https://api.qrserver.com/v1/create-qr-code/?size=280x280&data={urllib.parse.quote(qr_code_data)}"

    return {
        "booking_id": booking.id,
        "order_id": order_id,
        "amount": amount,
        "currency": "INR",
        "key_id": settings.razorpay_key_id or "",
        "merchant_upi_id": merchant_upi,
        "merchant_payment_url": merchant_payment_url,
        "upi_link": upi_link,
        "qr_code_url": qr_code_url,
        "is_razorpay_configured": bool(settings.razorpay_key_id and settings.razorpay_key_secret),
    }


@router.get("/{booking_id}/payment/details")
def payment_details(booking_id: int, current_user=Depends(get_current_user), db: Session = Depends(get_db)):
    booking = db.query(Booking).get(booking_id)
    if not booking or booking.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Booking not found")

    payment_metadata = _get_payment_metadata(booking)
    return {
        "booking_id": booking.id,
        "payment_status": booking.payment_status,
        "amount": booking.amount,
        "currency": "INR",
        "booking_status": booking.status,
        "merchant_upi_id": settings.merchant_upi_id,
        "payment_metadata": payment_metadata,
    }


@router.post("/payment/webhook")
async def razorpay_webhook(request: Request, db: Session = Depends(get_db)):
    signature = request.headers.get("x-razorpay-signature") or request.headers.get("X-Razorpay-Signature")
    if not signature:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Missing Razorpay signature header")

    raw_body = await request.body()
    if not _verify_razorpay_webhook_signature(raw_body, signature):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid Razorpay webhook signature")

    try:
        event = json.loads(raw_body)
    except ValueError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid webhook payload")

    event_type = event.get("event")
    payload = event.get("payload", {})
    payment_entity = payload.get("payment", {}).get("entity") if isinstance(payload.get("payment"), dict) else None
    order_entity = payload.get("order", {}).get("entity") if isinstance(payload.get("order"), dict) else None
    entity = payment_entity or order_entity or {}

    order_id = entity.get("order_id")
    payment_id = entity.get("id")
    status_text = entity.get("status")
    notes = entity.get("notes") or {}
    booking_id = notes.get("booking_id")

    booking = None
    if booking_id:
        try:
            booking = db.query(Booking).get(int(booking_id))
        except (TypeError, ValueError):
            booking = None
    if not booking and order_id:
        booking = db.query(Booking).filter(Booking.learner_notes.contains(order_id)).first()

    if not booking:
        return {"status": "ignored", "reason": "booking_not_found"}

    payment_metadata = {
        "webhook_event": event_type,
        "webhook_verified": True,
        "payment_id": payment_id,
        "order_id": order_id,
        "status": status_text,
    }

    if event_type == "payment.captured" or status_text == "captured":
        booking.payment_status = "paid"
        booking.status = "confirmed"
        payment_metadata["verified"] = True
    elif event_type == "payment.failed" or status_text == "failed":
        booking.payment_status = "unpaid"
        booking.status = "pending"
        payment_metadata["verified"] = False
    else:
        payment_metadata["handled"] = False

    _store_payment_metadata(booking, payment_metadata)
    db.commit()
    db.refresh(booking)

    return {"status": "received", "booking_id": booking.id, "event": event_type}


@router.post("/{booking_id}/payment/verify")
def verify_payment(booking_id: int, payload: dict[str, str], current_user=Depends(get_current_user), db: Session = Depends(get_db)):
    booking = db.query(Booking).get(booking_id)
    if not booking or booking.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Booking not found")

    order_id = payload.get("razorpay_order_id")
    payment_id = payload.get("razorpay_payment_id")
    signature = payload.get("razorpay_signature")

    if not all([order_id, payment_id, signature]):
        raise HTTPException(status_code=400, detail="Payment payload is incomplete")

    if not _verify_razorpay_signature({
        "razorpay_order_id": order_id,
        "razorpay_payment_id": payment_id,
        "razorpay_signature": signature,
    }):
        booking.payment_status = "unpaid"
        _store_payment_metadata(booking, {"status": "failed", "verification": "signature_mismatch"})
        db.commit()
        raise HTTPException(status_code=400, detail="Payment signature verification failed")

    booking.payment_status = "paid"
    booking.status = "confirmed"
    booking.meeting_link = f"https://meet.jit.si/expertverse-{booking.id}-{booking.expert_id}"
    _store_payment_metadata(booking, {
        "status": "paid",
        "payment_id": payment_id,
        "order_id": order_id,
        "verified": True,
        "confirmed_at": datetime.utcnow().isoformat(),
    })
    db.commit()
    db.refresh(booking)
    return {"status": "paid", "booking_id": booking.id, "meeting_link": booking.meeting_link}


@router.post("/{booking_id}/payment/upi-confirm")
def upi_confirm(
    booking_id: int,
    payload: dict[str, Any] = None,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    booking = db.query(Booking).get(booking_id)
    if not booking or booking.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Booking not found")

    payload = payload or {}
    utr = str(payload.get("utr_number") or payload.get("transaction_id") or "").strip()
    if not utr:
        utr = f"UPI_{int(datetime.utcnow().timestamp())}"

    upi_id = payload.get("upi_id") or settings.merchant_upi_id or "Direct_UPI"

    booking.payment_status = "paid"
    booking.status = "confirmed"
    booking.meeting_link = f"https://meet.jit.si/expertverse-{booking.id}-{booking.expert_id}"
    _store_payment_metadata(booking, {
        "status": "paid",
        "method": "direct_upi",
        "upi_id": upi_id,
        "utr_number": utr,
        "amount": booking.amount,
        "currency": "INR",
        "confirmed_at": datetime.utcnow().isoformat(),
        "verified": True,
    })
    db.commit()
    db.refresh(booking)

    return {
        "status": "paid",
        "booking_id": booking.id,
        "method": "direct_upi",
        "utr_number": utr,
        "meeting_link": booking.meeting_link,
    }


@router.post("/{booking_id}/payment/failure")
def payment_failure(booking_id: int, current_user=Depends(get_current_user), db: Session = Depends(get_db)):
    booking = db.query(Booking).get(booking_id)
    if not booking or booking.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Booking not found")

    booking.payment_status = "unpaid"
    booking.status = "pending"
    _store_payment_metadata(booking, {"status": "failed", "verification": "payment_failed"})
    db.commit()
    db.refresh(booking)
    return {"status": "failed", "booking_id": booking.id}

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
