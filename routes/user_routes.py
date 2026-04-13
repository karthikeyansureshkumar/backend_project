from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
import random   

from db.database import get_db
from modules.user import User

from modules.subscription import Subscription
from modules.plan import Plan

from utils.security import (
    hash_password,
    verify_password,
    create_access_token,
    get_current_user,
    admin_required
)

router = APIRouter()


class UserCreate(BaseModel):
    email: str
    password: str


@router.post("/register")
def register(user: UserCreate, db: Session = Depends(get_db)):

    existing_user = db.query(User).filter(User.email == user.email).first()

    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")

    otp = str(random.randint(100000, 999999))

    new_user = User(
        email=user.email,
        hashed_password=hash_password(user.password),
        role="user",
        otp_code=otp,
        otp_verified=False
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    free_plan = db.query(Plan).filter(Plan.name == "free").first()

    if not free_plan:
        raise HTTPException(status_code=500, detail="Free plan not found")

    subscription = Subscription(
        user_id=new_user.id,
        plan_id=free_plan.id,
        plan="FREE"
    )

    db.add(subscription)
    db.commit()

    print("OTP:", otp)

    return {"msg": "User created. Verify OTP"}


@router.post("/verify-otp")
def verify_otp(email: str, otp: str, db: Session = Depends(get_db)):

    user = db.query(User).filter(User.email == email).first()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    if user.otp_code != otp:
        raise HTTPException(status_code=400, detail="Invalid OTP")

    user.otp_verified = True
    user.otp_code = None

    db.commit()

    return {"msg": "OTP verified successfully"}


@router.post("/login")
def login(user: UserCreate, db: Session = Depends(get_db)):

    db_user = db.query(User).filter(User.email == user.email).first()

    if not db_user:
        raise HTTPException(status_code=400, detail="User not found")

    if not verify_password(user.password, db_user.hashed_password):
        raise HTTPException(status_code=400, detail="Invalid password")

    if not db_user.otp_verified:
        raise HTTPException(status_code=403, detail="Verify OTP first")

    if not db_user.is_active:
        raise HTTPException(
            status_code=403,
            detail="User is deactivated by admin"
        )

    token = create_access_token({"user_id": db_user.id})

    return {
        "access_token": token,
        "token_type": "bearer"
    }


@router.get("/profile")
def profile(current_user: User = Depends(get_current_user)):
    return {
        "email": current_user.email,
        "id": current_user.id,
        "role": current_user.role,
        "is_active": current_user.is_active
    }


@router.get("/admin/test")
def admin_test(user: User = Depends(admin_required)):
    return {"msg": "Admin access granted"}