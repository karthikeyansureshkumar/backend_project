from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import func

from db.database import SessionLocal
from utils.security import admin_required

from modules.user import User
from modules.project import Project
from modules.payment import Payment
from modules.subscription import Subscription
from modules.notification import Notification

router = APIRouter(prefix="/admin")


# ✅ ADMIN DASHBOARD (UPGRADED ANALYTICS)
@router.get("/dashboard")
def admin_dashboard(admin=Depends(admin_required)):
    db = SessionLocal()

    total_users = db.query(User).count()

    active_users = db.query(User).filter(
        User.is_active == True
    ).count()

    total_projects = db.query(Project).count()

    total_subscriptions = db.query(Subscription).count()

    pro_users = db.query(Subscription).filter(
        Subscription.plan == "PRO"
    ).count()

    total_payments = db.query(Payment).count()

    total_revenue = db.query(
        func.sum(Payment.amount)
    ).scalar() or 0

    result = {
        "total_users": total_users,
        "active_users": active_users,
        "total_projects": total_projects,
        "total_subscriptions": total_subscriptions,
        "pro_users": pro_users,
        "total_payments": total_payments,
        "total_revenue": total_revenue
    }

    db.close()
    return result


# ✅ GET ALL PAYMENTS
@router.get("/payments")
def get_all_payments(admin=Depends(admin_required)):
    db = SessionLocal()

    payments = db.query(Payment).all()

    result = [
        {
            "id": p.id,
            "user_id": p.user_id,
            "amount": p.amount,
            "currency": p.currency,
            "status": p.payment_status
        }
        for p in payments
    ]

    db.close()
    return result


# ✅ GET ALL SUBSCRIPTIONS
@router.get("/subscriptions")
def get_all_subscriptions(admin=Depends(admin_required)):
    db = SessionLocal()

    subs = db.query(Subscription).all()

    result = [
        {
            "user_id": s.user_id,
            "plan": s.plan,
            "status": getattr(s, "status", "active")
        }
        for s in subs
    ]

    db.close()
    return result


# ✅ SEND NOTIFICATION
@router.post("/notify/{user_id}")
def send_notification(user_id: int, admin=Depends(admin_required)):
    db = SessionLocal()

    notif = Notification(
        user_id=user_id,
        message="Admin message"
    )

    db.add(notif)
    db.commit()

    db.close()
    return {"message": "Notification sent"}


# ✅ TOGGLE USER ACTIVE/INACTIVE
@router.put("/users/{user_id}/toggle")
def toggle_user(user_id: int, admin=Depends(admin_required)):
    db = SessionLocal()

    user = db.query(User).filter(User.id == user_id).first()

    if not user:
        db.close()
        raise HTTPException(status_code=404, detail="User not found")

    user.is_active = not user.is_active
    db.commit()

    result = {
        "message": "User status updated",
        "is_active": user.is_active
    }

    db.close()
    return result