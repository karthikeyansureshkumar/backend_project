from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey
from datetime import datetime
from db.database import Base

class Payment(Base):
    __tablename__= "payments"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    stripe_payment_id = Column(String(255))
    amount = Column(Float)
    currency = Column(String(10))
    payment_status = Column(String(50))
    created_at = Column(DateTime, default=datetime.utcnow)