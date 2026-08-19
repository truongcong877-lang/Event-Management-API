from sqlalchemy import Column, Integer, String, Text, ForeignKey, DateTime, Enum
from sqlalchemy.orm import relationship
from datetime import datetime
import enum
from app.db.database import Base


class StaffRole(str, enum.Enum):
    MEMBER = "MEMBER"
    ADMIN = "ADMIN"


class TaskStatus(str, enum.Enum):
    TODO = "TODO"
    IN_PROGRESS = "IN_PROGRESS"
    DONE = "DONE"


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, autoincrement=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    full_name = Column(String(255), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    events = relationship("Event", back_populates="owner")
    staff_memberships = relationship("EventStaff", back_populates="user")
    assigned_tasks = relationship("EventTask", back_populates="assignee")


class Event(Base):
    __tablename__ = "events"

    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    # Thêm ondelete="CASCADE": Xóa User sẽ xóa luôn Event tương ứng trong CSDL
    owner_id = Column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    created_at = Column(DateTime, default=datetime.utcnow)

    owner = relationship("User", back_populates="events")
    # Thêm cascade="all, delete-orphan": Khi xóa Event qua SQLAlchemy, toàn bộ Staff và Task liên quan sẽ tự bị xóa
    staffs = relationship(
        "EventStaff", back_populates="event", cascade="all, delete-orphan"
    )
    tasks = relationship(
        "EventTask", back_populates="event", cascade="all, delete-orphan"
    )


class EventStaff(Base):
    __tablename__ = "event_staffs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    event_id = Column(
        Integer, ForeignKey("events.id", ondelete="CASCADE"), nullable=False
    )
    user_id = Column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    role = Column(Enum(StaffRole), default=StaffRole.MEMBER, nullable=False)

    event = relationship("Event", back_populates="staffs")
    user = relationship("User", back_populates="staff_memberships")


class EventTask(Base):
    __tablename__ = "event_tasks"

    id = Column(Integer, primary_key=True, autoincrement=True)
    event_id = Column(
        Integer, ForeignKey("events.id", ondelete="CASCADE"), nullable=False
    )
    # Thêm ondelete="SET NULL": Nếu User được phân công bị xóa, cột assigned_to sẽ tự về NULL thay vì lỗi CSDL
    assigned_to = Column(
        Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )
    title = Column(String(255), nullable=False)
    status = Column(Enum(TaskStatus), default=TaskStatus.TODO, nullable=False)
    deadline = Column(DateTime, nullable=True)

    event = relationship("Event", back_populates="tasks")
    assignee = relationship("User", back_populates="assigned_tasks")
