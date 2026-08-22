from fastapi import APIRouter, Depends, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional

from app.db.database import get_db
from app.models.user import User
from app.schemas.event import (
    EventCreate,
    EventUpdate,
    EventResponse,
    EventDetailResponse,
    EventStaffCreate,
    EventStaffResponse,
)
from app.services import event_service as event_service
from app.dependencies.auth import get_current_active_user

router = APIRouter(prefix="/events", tags=["events"])


@router.post("", response_model=EventResponse, status_code=status.HTTP_201_CREATED)
def create_event(
    event_in: EventCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    return event_service.create_event(
        db=db, event_in=event_in, current_user_id=current_user.id
    )


@router.get("", response_model=List[EventResponse])
def list_events(
    search: Optional[str] = Query(None, description="Tìm kiếm theo tên sự kiện"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    return event_service.get_events(
        db=db, current_user_id=current_user.id, search=search
    )


@router.get("/{event_id}", response_model=EventDetailResponse)
def get_event(
    event_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    return event_service.get_event_by_id(
        db=db, event_id=event_id, current_user_id=current_user.id
    )


@router.put("/{event_id}", response_model=EventDetailResponse)
def update_event(
    event_id: int,
    event_in: EventUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    return event_service.update_event(
        db=db, event_id=event_id, event_in=event_in, current_user_id=current_user.id
    )


@router.patch("/{event_id}", response_model=EventDetailResponse)
def patch_event(
    event_id: int,
    event_in: EventUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    return event_service.update_event(
        db=db, event_id=event_id, event_in=event_in, current_user_id=current_user.id
    )


@router.delete("/{event_id}", status_code=status.HTTP_200_OK)
def delete_event(
    event_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    message = event_service.delete_event(
        db=db, event_id=event_id, current_user_id=current_user.id
    )
    return {"message": message}


@router.post("/{event_id}/members", response_model=EventStaffResponse, status_code=status.HTTP_201_CREATED)
def add_member(
    event_id: int,
    member_in: EventStaffCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    return event_service.add_member(
        db=db, event_id=event_id, member_in=member_in, current_user_id=current_user.id
    )


@router.delete("/{event_id}/members/{user_id}", status_code=status.HTTP_200_OK)
def remove_member(
    event_id: int,
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    message = event_service.remove_member(
        db=db, event_id=event_id, target_user_id=user_id, current_user_id=current_user.id
    )
    return {"message": message}


@router.get("/{event_id}/members", response_model=List[EventStaffResponse])
def get_members(
    event_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    return event_service.get_event_members(
        db=db, event_id=event_id, current_user_id=current_user.id
    )

