from sqlalchemy import Column, Integer, String, ForeignKey
from db.database import Base

class Subscription(Base):
    __tablename__ = "subscriptions"

    id = Column(Integer, primary_key=True, index=True)

    user_id = Column(Integer, ForeignKey("users.id"))
    plan_id = Column(Integer, ForeignKey("plans.id"))

    stripe_customer_id = Column(String(255)) 
    stripe_subscription_id = Column(String(255)) 

    plan = Column(String(50), default="PRO") 