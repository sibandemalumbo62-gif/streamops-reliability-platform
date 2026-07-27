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
    assert response.json() == {"status": "healthy", "service": "playback-service"}


def test_start_playback(setup_database):
    session_data = {
        "user_id": str(uuid4()),
        "content_id": str(uuid4()),
        "quality": "AUTO",
        "device_type": "WEB"
    }
    response = client.post("/playback/start", json=session_data)
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ACTIVE"
    assert "session_id" in data


def test_pause_playback(setup_database):
    # First start a session
    session_data = {
        "user_id": str(uuid4()),
        "content_id": str(uuid4()),
        "quality": "AUTO"
    }
    start_response = client.post("/playback/start", json=session_data)
    session_id = start_response.json()["session_id"]
    
    # Pause the session
    response = client.post(f"/playback/{session_id}/pause")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "PAUSED"


def test_stop_playback(setup_database):
    # First start a session
    session_data = {
        "user_id": str(uuid4()),
        "content_id": str(uuid4()),
        "quality": "AUTO"
    }
    start_response = client.post("/playback/start", json=session_data)
    session_id = start_response.json()["session_id"]
    
    # Stop the session
    response = client.post(f"/playback/{session_id}/stop")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "STOPPED"
