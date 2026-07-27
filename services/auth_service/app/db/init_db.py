from app.db.base import Base
from app.db.session import engine

# Import models so SQLAlchemy knows them
from app.models.user import User


def init_db():
    Base.metadata.create_all(bind=engine)


if __name__ == "__main__":
    init_db()