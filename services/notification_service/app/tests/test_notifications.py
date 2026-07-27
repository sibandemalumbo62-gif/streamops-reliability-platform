import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from uuid import uuid4

from app.main import app
from app.db.base import Base
from app.db.session import get_db


SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)


@pytest.fixture
def setup_database():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy", "service": "notification-service"}


def test_create_notification(setup_database):
    notification_data = {
        "user_id": str(uuid4()),
        "notification_type": "EMAIL",
        "channel": "TRANSACTIONAL",
        "title": "Test Notification",
        "body": "This is a test notification"
    }
    response = client.post("/notifications/", json=notification_data)
    assert response.status_code == 201
    data = response.json()
    assert data["title"] == notification_data["title"]
    assert "id" in data


def test_get_user_notifications(setup_database):
    user_id = str(uuid4())
    
    # Create a notification first
    notification_data = {
        "user_id": user_id,
        "notification_type": "IN_APP",
        "channel": "MARKETING",
        "title": "Test",
        "body": "Test body"
    }
    client.post("/notifications/", json=notification_data)
    
    # Get user notifications
    response = client.get(f"/notifications/user/{user_id}")
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 1


def test_mark_as_read(setup_database):
    user_id = str(uuid4())
    
    # Create a notification first
    notification_data = {
        "user_id": user_id,
        "notification_type": "IN_APP",
        "channel": "MARKETING",
        "title": "Test",
        "body": "Test body"
    }
    create_response = client.post("/notifications/", json=notification_data)
    notification_id = str(create_response.json()["id"])
    
    # Mark as read
    response = client.post(f"/notifications/{notification_id}/read")
    assert response.status_code == 200


def test_create_template(setup_database):
    template_data = {
        "name": "welcome_email",
        "notification_type": "EMAIL",
        "channel": "TRANSACTIONAL",
        "subject_template": "Welcome to StreamOps",
        "body_template": "Hello {{username}}, welcome to StreamOps!",
        "variables": "username"
    }
    response = client.post("/templates/", json=template_data)
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == template_data["name"]
