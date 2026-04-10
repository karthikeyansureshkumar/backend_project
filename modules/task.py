from sqlalchemy import Column, Integer, String, ForeignKey
from db.database import Base

class Task(Base):   
    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(100))
    description = Column(String(255))
    status = Column(String(50), default="pending")

    project_id = Column(Integer, ForeignKey("projects.id"))