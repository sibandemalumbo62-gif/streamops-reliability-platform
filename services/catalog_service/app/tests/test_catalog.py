import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

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
    assert response.json() == {"status": "healthy", "service": "catalog-service"}


def test_create_content(setup_database):
    content_data = {
        "title": "Test Movie",
        "description": "A test movie",
        "content_type": "MOVIE",
        "genre": ["Action", "Drama"],
        "duration": 120,
        "release_year": 2024,
        "rating": 8.5,
        "language": "English"
    }
    response = client.post("/catalog/", json=content_data)
    assert response.status_code == 201
    data = response.json()
    assert data["title"] == content_data["title"]
    assert "id" in data


def test_get_all_content(setup_database):
    # Create some content first
    content_data = {
        "title": "Test Movie",
        "description": "A test movie",
        "content_type": "MOVIE",
        "genre": ["Action"],
        "duration": 120
    }
    client.post("/catalog/", json=content_data)
    
    response = client.get("/catalog/")
    assert response.status_code == 200
    data = response.json()
    assert data["count"] >= 1


def test_search_content(setup_database):
    # Create content first
    content_data = {
        "title": "The Matrix",
        "description": "A sci-fi movie",
        "content_type": "MOVIE",
        "genre": ["Sci-Fi"],
        "duration": 136
    }
    client.post("/catalog/", json=content_data)
    
    response = client.get("/search?q=Matrix")
    assert response.status_code == 200
    data = response.json()
    assert data["count"] >= 1
