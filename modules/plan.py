from sqlalchemy import Column, Integer, String
from db.database import Base

class Plan(Base):
    __tablename__ = "plans"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(20), unique=True)   
    project_limit = Column(Integer)
    price = Column(Integer)