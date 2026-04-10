from fastapi import APIRouter, Depends, HTTPException, Query
from services.stripe_service import create_checkout_session
import stripe
import os

from db.database import SessionLocal
from modules.subscription import Subscription
from modules.payment import Payment
from modules.notification import Notification
from utils.security import get_current_user

router = APIRouter()

stripe.api_key = os.getenv("STRIPE_SECRET_KEY")


@router.get("/subscribe")
def subscribe(current_user=Depends(get_current_user)):
    url = create_checkout_session(user_id=current_user.id)
    return {"checkout_url": url}


@router.get("/payment-success")
def payment_success(session_id: str = Query(...)):
    try:
        session = stripe.checkout.Session.retrieve(session_id)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

    metadata = session.metadata
    user_id = None

    if metadata:
        try:
            user_id = int(metadata.get("user_id"))
        except Exception:
            pass

    if not user_id:
        customer_email = getattr(
            getattr(session, "customer_details", None),
            "email",
            None
        )

        if customer_email:
            db = SessionLocal()
            user = db.query(Subscription).filter(Subscription.user_id != None).first()
            db.close()
            if user:
                user_id = user.user_id

    if not user_id:
        raise HTTPException(status_code=400, detail="Invalid user")

    db = SessionLocal()

    try:
        existing = db.query(Subscription).filter(
            Subscription.user_id == user_id
        ).first()

        if existing:
            existing.stripe_customer_id = session.customer or ""
            existing.stripe_subscription_id = session.subscription or ""
            existing.plan = "PRO"
        else:
            new_subscription = Subscription(
                user_id=user_id,
                stripe_customer_id=session.customer or "",
                stripe_subscription_id=session.subscription or "",
                plan="PRO"
            )
            db.add(new_subscription)

        if session.payment_intent:
            try:
                payment_intent = stripe.PaymentIntent.retrieve(session.payment_intent)

                existing_payment = db.query(Payment).filter(
                    Payment.stripe_payment_id == payment_intent.id
                ).first()

                if not existing_payment:
                    payment = Payment(
                        user_id=user_id,
                        stripe_payment_id=payment_intent.id,
                        amount=payment_intent.amount / 100,
                        currency=payment_intent.currency,
                        payment_status=payment_intent.status
                    )
                    db.add(payment)
            except Exception as e:
                print("Payment save error:", e)

        notification = Notification(
            user_id=user_id,
            message=" Payment successful! You are now PRO user."
        )
        db.add(notification)

        db.commit()

    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

    finally:
        db.close()

    return {
        "message": "Payment successful",
        "customer_id": session.customer,
        "subscription_id": session.subscription
    }


@router.get("/payment-cancel")
def payment_cancel():
    return {"message": "Payment cancelled"}