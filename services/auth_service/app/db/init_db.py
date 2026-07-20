from services.auth_service.app.db.base import Base
from services.auth_service.app.db.session import engine

# Import models so SQLAlchemy knows them
from services.auth_service.app.models.user import User
from . import integrity_models

def init_db():
    Base.metadata.create_all(bind=engine)


if __name__ == "__main__":
    init_db()