from sqlalchemy import inspect
from app.main import app, health_check, start
from app.db.database import engine, SessionLocal
from app.models import User, Event, EventStaff, EventTask, UserRole, StaffRole, TaskStatus, TaskPriority
from app.schemas import UserResponse, EventResponse, EventStaffResponse, EventTaskResponse
from app.core.exceptions import NotFoundException, BadRequestException, ForbiddenException, UnauthorizedException, create_error_response

def test_health_check():
    res = health_check()
    assert res["status"] == 200
    assert "Dịch vụ đang hoạt động bình thường" in res["message"]
    print("[OK] test_health_check passed")

def test_root_endpoint():
    res = start()
    assert "message" in res
    print("[OK] test_root_endpoint passed")

def test_database_tables_created():
    inspector = inspect(engine)
    tables = inspector.get_table_names()
    assert "users" in tables, "Table 'users' missing"
    assert "events" in tables, "Table 'events' missing"
    assert "event_staff" in tables, "Table 'event_staff' missing"
    assert "event_tasks" in tables, "Table 'event_tasks' missing"
    print("[OK] test_database_tables_created passed: tables=", tables)

def test_custom_exception_handling():
    exc = NotFoundException("Sự kiện không tồn tại")
    assert exc.status_code == 404
    assert exc.message == "Sự kiện không tồn tại"

    response = create_error_response(exc.status_code, exc.message, exc.details)
    assert response.status_code == 404
    print("[OK] test_custom_exception_handling passed")

def test_models_and_schemas():
    db = SessionLocal()
    try:
        # Clean test user if exists
        test_user = db.query(User).filter(User.email == "test_user@example.com").first()
        if test_user:
            db.delete(test_user)
            db.commit()

        user = User(
            email="test_user@example.com",
            password_hash="secret_hash",
            full_name="Test User",
            role=UserRole.USER,
        )
        db.add(user)
        db.commit()
        db.refresh(user)

        assert user.id is not None
        user_schema = UserResponse.model_validate(user)
        assert user_schema.email == "test_user@example.com"
        assert user_schema.full_name == "Test User"

        # Create Event
        event = Event(name="Tech Conf 2026", description="Annual event", owner_id=user.id)
        db.add(event)
        db.commit()
        db.refresh(event)

        assert event.id is not None
        event_schema = EventResponse.model_validate(event)
        assert event_schema.name == "Tech Conf 2026"

        # Create EventStaff
        staff = EventStaff(event_id=event.id, user_id=user.id, role=StaffRole.OWNER)
        db.add(staff)
        db.commit()
        db.refresh(staff)

        assert staff.id is not None
        staff_schema = EventStaffResponse.model_validate(staff)
        assert staff_schema.role == StaffRole.OWNER

        # Create EventTask
        task = EventTask(
            event_id=event.id,
            title="Setup stage",
            assignee_id=user.id,
            status=TaskStatus.TODO,
            priority=TaskPriority.HIGH
        )
        db.add(task)
        db.commit()
        db.refresh(task)

        assert task.id is not None
        task_schema = EventTaskResponse.model_validate(task)
        assert task_schema.title == "Setup stage"

        # Cleanup
        db.delete(user) # cascade deletes event, staff, task
        db.commit()

        print("[OK] test_models_and_schemas passed")

    finally:
        db.close()

if __name__ == "__main__":
    print("=== RUNNING VERIFICATION SUITE ===")
    test_health_check()
    test_root_endpoint()
    test_database_tables_created()
    test_custom_exception_handling()
    test_models_and_schemas()
    print("=== ALL VERIFICATION TESTS PASSED SUCCESSFULLY! ===")
