from typing import List, Optional

from sqlalchemy import or_
from sqlalchemy.orm import Session

from app.models.event import Event
from app.models.event_staff import EventStaff
from app.models.event_task import EventTask
from app.models.user import User

from app.schemas.event_task import ( EventTaskCreate, EventTaskUpdate)

from app.core.exceptions import (bad_request, forbidden,not_found)


def get_event_or_404(db: Session, event_id: int):
    event = db.query(Event).filter(Event.id == event_id).first()

    if not event:
        raise not_found("Không tìm thấy sự kiện")

    return event


def get_task_or_404(db: Session, task_id: int):
    task = db.query(EventTask).filter(EventTask.id == task_id).first()

    if not task:
        raise not_found("Không tìm thấy công việc")

    return task


def check_event_member(db: Session, event_id: int, user_id: int):
    get_event_or_404(db=db, event_id=event_id)

    staff = (
        db.query(EventStaff)
        .filter(EventStaff.event_id == event_id, EventStaff.user_id == user_id)
        .first()
    )

    if not staff:
        raise forbidden("Bạn không phải thành viên của sự kiện")

    return staff


def check_task_permission(db: Session, task: EventTask, user_id: int):
    staff = check_event_member(db=db, event_id=task.event_id, user_id=user_id)

    return staff


def validate_assignee(db: Session, event_id: int, assignee_id: Optional[int]):
    if assignee_id is None:
        return

    user = db.query(User).filter(User.id == assignee_id).first()

    if not user:
        raise not_found("Người được giao không tồn tại")

    staff = (
        db.query(EventStaff)
        .filter(EventStaff.event_id == event_id, EventStaff.user_id == assignee_id)
        .first()
    )

    if not staff:
        raise bad_request("Không thể giao việc cho người ngoài sự kiện")


def create_task(
    db: Session, event_id: int, task_in: EventTaskCreate, current_user_id: int
):
    staff = check_event_member(db=db, event_id=event_id, user_id=current_user_id)

    validate_assignee(db=db, event_id=event_id, assignee_id=task_in.assignee_id)

    task = EventTask(
        event_id=event_id,
        title=task_in.title,
        description=task_in.description,
        priority=task_in.priority,
        due_date=task_in.due_date,
        assignee_id=task_in.assignee_id,
    )

    db.add(task)
    db.commit()
    db.refresh(task)

    return task


def get_tasks(
    db: Session,
    event_id: int,
    current_user_id: int,
    status_filter=None,
    priority_filter=None,
    assignee_id: Optional[int] = None,
    search: Optional[str] = None,
    limit: int = 10,
    offset: int = 0,
    sort_by: str = "created_at",
    sort_order: str = "desc",
) -> List[EventTask]:

    check_event_member(db=db, event_id=event_id, user_id=current_user_id)

    query = db.query(EventTask).filter(EventTask.event_id == event_id)

    if status_filter is not None:
        query = query.filter(EventTask.status == status_filter)

    if priority_filter is not None:
        query = query.filter(EventTask.priority == priority_filter)

    if assignee_id is not None:
        query = query.filter(EventTask.assignee_id == assignee_id)

    if search:
        query = query.filter(
            or_(
                EventTask.title.ilike(f"%{search}%"),
                EventTask.description.ilike(f"%{search}%"),
            )
        )

    if sort_by == "due_date":
        sort_column = EventTask.due_date

    elif sort_by == "priority":
        sort_column = EventTask.priority

    else:
        sort_column = EventTask.created_at

    if sort_order.lower() == "asc":
        query = query.order_by(sort_column.asc())
    else:
        query = query.order_by(sort_column.desc())

    return query.offset(offset).limit(limit).all()


def get_task(db: Session, task_id: int, current_user_id: int):
    task = get_task_or_404(db=db, task_id=task_id)

    check_task_permission(db=db, task=task, user_id=current_user_id)

    return task


def update_task(
    db: Session, task_id: int, task_in: EventTaskUpdate, current_user_id: int
):
    task = get_task_or_404(db=db, task_id=task_id)

    staff = check_task_permission(db=db, task=task, user_id=current_user_id)

    update_data = task_in.model_dump(exclude_unset=True)

    if "assignee_id" in update_data:

        validate_assignee(
            db=db, event_id=task.event_id, assignee_id=update_data["assignee_id"]
        )

    if staff.role.value != "OWNER":

        allowed_fields = {"status", "description", "priority", "due_date"}

        for key in update_data:

            if key not in allowed_fields:
                raise forbidden("Bạn không có quyền cập nhật trường này")

    for key, value in update_data.items():
        setattr(task, key, value)

    db.commit()
    db.refresh(task)

    return task


def delete_task(db: Session, task_id: int, current_user_id: int):
    task = get_task_or_404(db=db, task_id=task_id)

    staff = check_task_permission(db=db, task=task, user_id=current_user_id)

    if staff.role.value != "OWNER":
        raise forbidden("Chỉ OWNER mới có quyền xóa công việc")

    db.delete(task)
    db.commit()
