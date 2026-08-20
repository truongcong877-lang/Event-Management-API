from sqlalchemy import Column, Integer, ForeignKey, Enum, DateTime
from sqlalchemy.orm import relationship
from app.db.database import Base
import enum

class StaffRole(str, enum.Enum):
    OWNER = "OWNER"
    MEMBER = "MEMBER"

class EventStaff(Base):
    __tablename__ = "event_staff"

    event_id = Column(Integer, ForeignKey("events.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    role = Column(Enum(StaffRole), nullable=False)
    joined_at = Column(DateTime, nullable=False)

    event = relationship("Event", back_populates="staff_members")
    user = relationship("User", back_populates="staff_memberships")