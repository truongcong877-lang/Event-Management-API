from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from typing import Optional, List

from app.models.event_staff import EventStaff, StaffRole
from app.models.event import Event
from app.models.user import User
from app.schemas.event import EventCreate, EventUpdate, EventStaffCreate


def _get_event_or_404(db: Session, event_id: int) -> Event:
    event = db.query(Event).filter(Event.id == event_id).first()
    if not event:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Không tìm thấy sự kiện"
        )
    return event


def _check_owner_permission(
    db: Session, event_id: int, current_user_id: int
) -> EventStaff:
    # Đảm bảo sự kiện phải tồn tại trước khi kiểm tra quyền
    _get_event_or_404(db, event_id)

    staff = (
        db.query(EventStaff)
        .filter(
            EventStaff.event_id == event_id,
            EventStaff.user_id == current_user_id,
            EventStaff.role == StaffRole.OWNER,
        )
        .first()
    )

    if not staff:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Bạn không có quyền thực hiện thao tác này",
        )
    return staff


def create_event(db: Session, event_in: EventCreate, current_user_id: int) -> Event:
    new_event = Event(
        name=event_in.name,
        description=event_in.description,
        owner_id=current_user_id,
    )
    db.add(new_event)
    db.flush()  # sinh new_event.id

    owner_staff = EventStaff(
        event_id=new_event.id, user_id=current_user_id, role=StaffRole.OWNER
    )

    db.add(owner_staff)
    db.commit()
    db.refresh(new_event)
    return new_event


def get_events(
    db: Session, current_user_id: int, search: Optional[str] = None
) -> List[Event]:
    query = (
        db.query(Event)
        .join(EventStaff, Event.id == EventStaff.event_id)
        .filter(EventStaff.user_id == current_user_id)
    )

    if search:
        query = query.filter(Event.name.ilike(f"%{search}%"))

    return query.all()


def get_event_by_id(db: Session, event_id: int, current_user_id: int) -> Event:
    event = _get_event_or_404(db, event_id)

    event_staff = (
        db.query(EventStaff)
        .filter(EventStaff.event_id == event_id, EventStaff.user_id == current_user_id)
        .first()
    )

    if not event_staff:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Bạn không có quyền truy cập sự kiện này",
        )

    event.role = event_staff.role
    return event


def update_event(
    db: Session, event_id: int, event_in: EventUpdate, current_user_id: int
) -> Event:
    _check_owner_permission(db, event_id, current_user_id)
    event = _get_event_or_404(db, event_id)

    update_dict = event_in.model_dump(exclude_unset=True)
    for key, value in update_dict.items():
        setattr(event, key, value)

    db.commit()
    db.refresh(event)
    event.role = StaffRole.OWNER
    return event


def delete_event(db: Session, event_id: int, current_user_id: int) -> str:
    _check_owner_permission(db, event_id, current_user_id)
    event = _get_event_or_404(db, event_id)

    event_name = event.name
    db.delete(event)
    db.commit()

    return f"Đã xoá thành công sự kiện {event_name}"


def add_member(
    db: Session, event_id: int, member_in: EventStaffCreate, current_user_id: int
) -> EventStaff:
    # 1. Chỉ owner mới được thêm member
    _check_owner_permission(db, event_id, current_user_id)

    # 2. Kiểm tra user được thêm có tồn tại trong hệ thống không
    target_user = db.query(User).filter(User.id == member_in.user_id).first()
    if not target_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Người dùng không tồn tại"
        )

    # 3. Kiểm tra user đã là member/owner trong sự kiện chưa (không cho thêm trùng)
    existing_staff = (
        db.query(EventStaff)
        .filter(
            EventStaff.event_id == event_id, EventStaff.user_id == member_in.user_id
        )
        .first()
    )
    if existing_staff:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Người dùng đã là thành viên trong sự kiện này",
        )

    new_staff = EventStaff(
        event_id=event_id, user_id=member_in.user_id, role=member_in.role
    )
    db.add(new_staff)
    db.commit()
    db.refresh(new_staff)
    return new_staff


def remove_member(
    db: Session, event_id: int, target_user_id: int, current_user_id: int
) -> str:
    # 1. Chỉ owner mới được xóa member
    _check_owner_permission(db, event_id, current_user_id)

    # 2. Kiểm tra thành viên có thuộc sự kiện không
    target_staff = (
        db.query(EventStaff)
        .filter(EventStaff.event_id == event_id, EventStaff.user_id == target_user_id)
        .first()
    )
    if not target_staff:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Thành viên không thuộc sự kiện này",
        )

    # 3. Không được xóa owner cuối cùng
    if target_staff.role == StaffRole.OWNER:
        owner_count = (
            db.query(EventStaff)
            .filter(EventStaff.event_id == event_id, EventStaff.role == StaffRole.OWNER)
            .count()
        )
        if owner_count <= 1:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Không thể xóa owner cuối cùng của sự kiện",
            )

    db.delete(target_staff)
    db.commit()
    return "Xóa thành viên thành công"


def get_event_members(
    db: Session, event_id: int, current_user_id: int
) -> List[EventStaff]:
    _get_event_or_404(db, event_id)

    # Kiểm tra người dùng hiện tại có là thành viên/owner sự kiện không
    current_staff = (
        db.query(EventStaff)
        .filter(EventStaff.event_id == event_id, EventStaff.user_id == current_user_id)
        .first()
    )
    if not current_staff:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Bạn không có quyền xem danh sách thành viên của sự kiện này",
        )

    members = db.query(EventStaff).filter(EventStaff.event_id == event_id).all()
    return members
