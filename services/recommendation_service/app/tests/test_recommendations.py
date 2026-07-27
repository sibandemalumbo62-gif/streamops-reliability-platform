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
    assert response.json() == {"status": "healthy", "service": "recommendation-service"}


def test_create_user_preferences(setup_database):
    preference_data = {
        "user_id": str(uuid4()),
        "preferred_genres": ["Action", "Sci-Fi"],
        "preferred_languages": ["English"],
        "favorite_directors": ["Christopher Nolan"]
    }
    response = client.post("/preferences/", json=preference_data)
    assert response.status_code == 201
    data = response.json()
    assert data["user_id"] == preference_data["user_id"]
    assert "id" in data


def test_get_recommendations(setup_database):
    user_id = str(uuid4())
    
    # Create preferences first
    preference_data = {
        "user_id": user_id,
        "preferred_genres": ["Sci-Fi"],
        "preferred_languages": ["English"]
    }
    client.post("/preferences/", json=preference_data)
    
    # Get recommendations
    response = client.get(f"/recommendations/{user_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["user_id"] == user_id
    assert "recommendations" in data


def test_add_watch_history(setup_database):
    history_data = {
        "user_id": str(uuid4()),
        "content_id": str(uuid4()),
        "content_type": "MOVIE",
        "genre": "Action",
        "watch_duration": 3600,
        "total_duration": 7200,
        "user_rating": 5
    }
    response = client.post("/recommendations/watch-history", json=history_data)
    assert response.status_code == 200
    data = response.json()
    assert data["user_id"] == history_data["user_id"]
    assert data["completion_percentage"] == 50.0
