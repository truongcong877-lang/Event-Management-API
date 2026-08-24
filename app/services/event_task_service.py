from typing import List, Optional
from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.event import Event
from app.models.event_staff import EventStaff
from app.models.event_task import EventTask
from app.models.user import User
from app.schemas.event_task import EventTaskCreate, EventTaskUpdate


def _get_task_or_404(db: Session, task_id: int) -> EventTask:
    task = db.query(EventTask).filter(EventTask.id == task_id).first()

    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Không tìm thấy công việc"
        )

    return task


def _get_event_or_404(db: Session, event_id: int) -> Event:
    event = db.query(Event).filter(Event.id == event_id).first()

    if not event:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Không tìm thấy sự kiệm"
        )

    return event


def _check_event_member(db: Session, event_id: int, user_id: int) -> EventStaff:
    _get_event_or_404(db, event_id)

    staff = (
        db.query(EventStaff)
        .filter(EventStaff.event_id == event_id, EventStaff.user_id == user_id)
        .first()
    )

    if not staff:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Bạn không phải thành viên của sự kiện",
        )

    return staff


def _check_task_permission(db: Session, task: EventTask, user_id: int) -> EventStaff:
    staff = _check_event_member(db=db, event_id=task.event_id, user_id=user_id)

    return staff


def _validate_assignee(db: Session, event_id: int, assignee_id: Optional[int]):
    if assignee_id is None:
        return

    user = db.query(User).filter(User.id == assignee_id).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Người được giao không tồn tại",
        )

    staff = (
        db.query(EventStaff)
        .filter(EventStaff.event_id == event_id, EventStaff.user_id == assignee_id)
        .first()
    )

    if not staff:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Không thể giao việc cho người ngoài sự kiện",
        )


def create_task(
    db: Session, event_id: int, task_in: EventTaskCreate, current_user_id: int
) -> EventTask:
    _check_event_member(db=db, event_id=event_id, user_id=current_user_id)

    _validate_assignee(db=db, event_id=event_id, assignee_id=task_in.assignee_id)

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


def get_task(
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
    _check_event_member(db=db, event_id=event_id, user_id=current_user_id)

    query = db.query(EventTask).filter(EventTask.event_id == event_id)

    if status_filter is not None:
        query = query.filter(EventTask.status == status_filter)

    if priority_filter is not None:
        query = query.filter(EventTask.priority == priority_filter)

    if assignee_id is not None:
        query = query.filter(EventTask.assignee_id == assignee_id)

    if search:
        query = query.filter(EventTask.title.ilike(f"%(search)%"))

    if sort_by == "due_date":
        sort_column = EventTask.due_date
    else:
        sort_column = EventTask.created_at

    if sort_order.lower() == "asc":
        query = query.order_by(sort_column.asc())
    else:
        query = query.order_by(sort_column.desc())

    return query.offset(offset).limit(limit).all()


def get_task(db: Session, task_id: int, current_user_id: int) -> EventTask:
    task = _get_task_or_404(db=db, task_id=task_id)

    _check_task_permission(
        db=db,
        task=task,
        user_id=current_user_id,
    )

    return task


def update_task(
    db: Session, task_id: int, task_in: EventTaskUpdate, current_user_id: int
) -> EventTask:
    task = _get_task_or_404(db=db, task_id=task_id)

    staff = _check_task_permission(db=db, task=task, user_id=current_user_id)

    update_data = task_in.model_dump(exclude_unset=True)

    if "assignee_id" in update_data:
        _validate_assignee(
            db=db, event_id=task.event_id, assignee_id=update_data["assignee_id"]
        )

    if staff.role.value != "OWNER":
        allowed_fields = {"status", "description", "priority"}

        for key in update_data:
            if key not in allowed_fields:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Bạn không có quyền cập nhật trường này",
                )

    for key, value in update_data.items():
        setattr(task, key, value)

    db.commit()
    db.refresh(task)

    return task


def delete_task(db: Session, task_id: int, current_user_id: int) -> None:
    task = _get_task_or_404(db=db, task_id=task_id)

    staff = _check_task_permission(db=db, task=task, user_id=current_user_id)

    if staff.role.value != "OWNER":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Chỉ OWNER mới có quyền xóa công việc",
        )

    db.delete(task)
    db.commit()
