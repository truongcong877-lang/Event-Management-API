from sqlalchemy import Column, Integer, String, Text, DateTime, Enum, ForeignKey
from sqlalchemy.orm import relationship
from app.db.database import Base
import enum

class TaskStatus(str, enum.Enum):
    TODO = "TODO"
    IN_PROGRESS = "IN_PROGRESS"
    DONE = "DONE"

class TaskPriority(str, enum.Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"

class EventTask(Base):
    __tablename__ = "event_tasks"

    id = Column(Integer, primary_key=True)
    event_id = Column(Integer, ForeignKey("events.id"), nullable=False)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    assignee_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    status = Column(Enum(TaskStatus), nullable=False)
    priority = Column(Enum(TaskPriority), nullable=False)
    due_date = Column(DateTime, nullable=True)
    created_at = Column(DateTime, nullable=False)

    event = relationship("Event", back_populates="tasks")
    assignee = relationship("User", back_populates="assigned_tasks")