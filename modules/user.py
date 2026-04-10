from sqlalchemy import Column, Integer, String, Boolean
from db.database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(100), unique=True, index=True)
    hashed_password = Column(String(200))

    role = Column(String(20), default="user")   
    is_active = Column(Boolean, default=True)

    otp_code = Column(String(6), nullable=True)
    otp_verified = Column(Boolean, default=False)

    
    stripe_customer_id = Column(String(255), nullable=True)