from typing import List, Optional
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.dependencies.auth import get_current_active_user
from app.models.event_task import TaskStatus, TaskPriority
from app.models.user import User
from app.schemas.event_task import EventTaskCreate, EventTaskUpdate, EventTaskResponse
from app.services import event_task_service

router = APIRouter(tags=["event-tasks"])


@router.post(
    "/events/{event_id}/event-tasks",
    response_model=EventTaskResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_event_task(
    event_id: int,
    task_in: EventTaskCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    return event_task_service.create_task(
        db=db,
        event_id=event_id,
        task_in=task_in,
        current_user_id=current_user.id,
    )


@router.get(
    "/events/{event_id}/event-tasks",
    response_model=List[EventTaskResponse],
)
def get_event_tasks(
    event_id: int,
    status_filter: Optional[TaskStatus] = Query(
        None,
        alias="status",
    ),
    priority_filter: Optional[TaskPriority] = Query(None, alias="priority"),
    assignee_id: Optional[int] = None,
    search: Optional[str] = None,
    limit: int = Query(10, ge=1, le=100),
    offset: int = Query(0, ge=0),
    sort_by: str = Query("created_at"),
    sort_order: str = Query("desc"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    return event_task_service.get_tasks(
        db=db,
        event_id=event_id,
        current_user_id=current_user.id,
        status_filter=status_filter,
        priority_filter=priority_filter,
        assignee_id=assignee_id,
        search=search,
        limit=limit,
        offset=offset,
        sort_by=sort_by,
        sort_order=sort_order,
    )


@router.get("/event-tasks/{task_id}", response_model=EventTaskResponse)
def get_event_task(
    task_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    return event_task_service.get_task(
        db=db, task_id=task_id, current_user_id=current_user.id
    )


@router.patch("/event-tasks/{task_id}", response_model=EventTaskResponse)
def update_event_task(
    task_id: int,
    task_in: EventTaskUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    return event_task_service.update_task(
        db=db,
        task_id=task_id,
        task_in=task_in,
        current_user_id=current_user.id,
    )


@router.delete("/event-tasks/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_event_task(
    task_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    event_task_service.delete_task(
        db=db, task_id=task_id, current_user_id=current_user.id
    )
