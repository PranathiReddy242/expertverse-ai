import requests
import sys

BASE_URL = "http://127.0.0.1:8000"

def test_payment_and_upi():
    # 1. Register or login learner
    auth_data = {
        "email": "upilearner@expertverse.ai",
        "password": "LearnerPassword123!",
        "name": "UPI Test Learner"
    }
    r = requests.post(f"{BASE_URL}/auth/register", json=auth_data)
    if r.status_code not in (200, 400):
        print(f"Register failed: {r.status_code} {r.text}")
        sys.exit(1)

    r = requests.post(f"{BASE_URL}/auth/login", data={"username": auth_data["email"], "password": auth_data["password"]})
    assert r.status_code == 200, f"Login failed: {r.text}"
    token = r.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # 2. Fetch experts
    r = requests.get(f"{BASE_URL}/experts/list")
    assert r.status_code == 200
    experts = r.json()
    assert len(experts) > 0
    expert = experts[0]
    print(f"[OK] Selected expert: {expert['user']['name']} (Rate: INR {expert['hourly_rate']})")

    # 3. Create a booking
    slot_time = "2026-09-22T11:00:00"
    r = requests.post(f"{BASE_URL}/bookings/create", json={"expert_id": expert["id"], "slot": slot_time}, headers=headers)
    assert r.status_code == 200, f"Booking create failed: {r.text}"
    booking = r.json()
    booking_id = booking["id"]
    print(f"[OK] Created booking #{booking_id} with amount INR {booking['amount']}")

    # 4. Create payment order (Razorpay + Direct UPI metadata)
    r = requests.post(f"{BASE_URL}/bookings/{booking_id}/payment/create-order", headers=headers)
    assert r.status_code == 200, f"Create order failed: {r.text}"
    order = r.json()
    print(f"[OK] Payment order created successfully:")
    print(f"     Order ID: {order['order_id']}")
    print(f"     Merchant UPI ID: {order.get('merchant_upi_id')}")
    print(f"     Merchant Payment URL: {order.get('merchant_payment_url')}")
    print(f"     UPI Link: {order.get('upi_link')}")
    print(f"     QR Code URL: {order.get('qr_code_url')}")
    assert "pranathitarigonda@razorpay" in order.get("merchant_upi_id", ""), "Merchant UPI ID mismatch"
    assert "razorpay.me/@pranathitarigonda" in order.get("merchant_payment_url", ""), "Merchant payment URL mismatch"
    assert "qrserver.com" in order["qr_code_url"], "QR code URL missing"

    # 5. Test Direct UPI payment confirmation
    utr_number = "423819284729"
    r = requests.post(f"{BASE_URL}/bookings/{booking_id}/payment/upi-confirm", json={"utr_number": utr_number}, headers=headers)
    assert r.status_code == 200, f"UPI confirm failed: {r.text}"
    confirm_data = r.json()
    print(f"[OK] UPI payment confirmed:")
    print(f"     Status: {confirm_data['status']}")
    print(f"     Meeting Link: {confirm_data.get('meeting_link')}")
    assert confirm_data["status"] == "paid"
    assert "meet.jit.si" in confirm_data.get("meeting_link", "")

    # 6. Verify booking list reflects paid
    r = requests.get(f"{BASE_URL}/bookings/list", headers=headers)
    assert r.status_code == 200
    my_bookings = r.json()
    matched = next((b for b in my_bookings if b["id"] == booking_id), None)
    assert matched is not None
    assert matched["payment_status"] == "paid"
    assert matched["status"] == "confirmed"
    print(f"[OK] Booking #{booking_id} verified as PAID and CONFIRMED in database.")

    print("\nALL PAYMENT AND UPI INTEGRATION TESTS PASSED SUCCESSFULLY!")

if __name__ == "__main__":
    test_payment_and_upi()
