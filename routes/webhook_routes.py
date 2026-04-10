from fastapi import APIRouter, Request, Depends
from sqlalchemy.orm import Session
import stripe
import os

from db.database import get_db
from modules.user import User
from modules.subscription import Subscription
from modules.payment import Payment
from modules.notification import Notification

router = APIRouter()

stripe.api_key = os.getenv("STRIPE_SECRET_KEY")

endpoint_secret = "whsec_35054410ee845a08f83810486b03108e2a834472a4795d8070ee05aef7df417b"


@router.post("/webhook")
async def stripe_webhook(request: Request, db: Session = Depends(get_db)):
    payload = await request.body()
    sig_header = request.headers.get("stripe-signature")

    try:
        event = stripe.Webhook.construct_event(payload, sig_header, endpoint_secret)
    except Exception:
        return {"error": "Webhook error"}

    event_type = event["type"]
    print("Webhook received:", event_type)

    # =========================
    # ✅ CHECKOUT FLOW
    # =========================
    if event_type == "checkout.session.completed":

        session = event["data"]["object"]

        metadata = getattr(session, "metadata", {}) or {}
        user_id = metadata["user_id"] if "user_id" in metadata else None

        customer_email = getattr(
            getattr(session, "customer_details", None),
            "email",
            None
        )

        stripe_sub_id = getattr(session, "subscription", None)
        stripe_cust_id = getattr(session, "customer", None)

        user = None

        # 🔹 Find user
        if user_id:
            user = db.query(User).filter(User.id == int(user_id)).first()

        if not user and customer_email:
            user = db.query(User).filter(User.email == customer_email).first()

        if not user:
            print("User not found ❌")
            return {"status": "ignored"}

        # 🔥 SAVE CUSTOMER ID (IMPORTANT)
        if stripe_cust_id:
            user.stripe_customer_id = stripe_cust_id
            db.commit()

        # 🔹 Save subscription
        existing_sub = db.query(Subscription).filter(
            Subscription.user_id == user.id
        ).first()

        if existing_sub:
            existing_sub.stripe_customer_id = stripe_cust_id
            existing_sub.stripe_subscription_id = stripe_sub_id
            existing_sub.plan = "PRO"
        else:
            db.add(Subscription(
                user_id=user.id,
                stripe_customer_id=stripe_cust_id,
                stripe_subscription_id=stripe_sub_id,
                plan="PRO"
            ))

        db.commit()
        print("SUBSCRIPTION SAVED ✅")

    # =========================
    # ✅ PAYMENT FLOW (FINAL FIX)
    # =========================
    if event_type == "invoice.payment_succeeded":

        invoice = event["data"]["object"]

        customer_id = getattr(invoice, "customer", None)
        payment_intent_id = getattr(invoice, "payment_intent", None)

        user = None

        # 🔹 TRY 1 → customer_id
        if customer_id:
            user = db.query(User).filter(
                User.stripe_customer_id == customer_id
            ).first()

        # 🔹 TRY 2 → fallback using metadata
        if not user and customer_id:
            sessions = stripe.checkout.Session.list(
                customer=customer_id,
                limit=1
            )

            if sessions.data:
                session = sessions.data[0]
                metadata = getattr(session, "metadata", {}) or {}
                user_id = metadata.get("user_id")

                if user_id:
                    user = db.query(User).filter(User.id == int(user_id)).first()

        if not user:
            print("User still not found ❌")
            return {"status": "ignored"}

        # 🔹 Save payment
        existing_payment = db.query(Payment).filter(
            Payment.stripe_payment_id == payment_intent_id
        ).first()

        if not existing_payment:
            db.add(Payment(
                user_id=user.id,
                stripe_payment_id=payment_intent_id,
                amount=(getattr(invoice, "amount_paid", 0) or 0) / 100,
                currency=getattr(invoice, "currency", "inr"),
                payment_status=getattr(invoice, "status", "paid")
            ))

        # 🔹 Notification
        db.add(Notification(
            user_id=user.id,
            title="Payment Success",
            message="Payment successful. You are now PRO user"
        ))

        db.commit()
        print("PAYMENT SAVED ✅")

    return {"status": "success"}