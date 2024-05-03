from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session

from .config import settings

host = settings.host
port = settings.port
user = settings.user
password = settings.password
database = settings.database

SQLALCHEMY_DATABASE_URL = (
    f"mysql+mysqlconnector://{user}:{str(password)}@{host}:{port}/{database}"
)

engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db() -> Session:
    db = SessionLocal()
    print("Database connection was successful!")
    try:
        yield db
    finally:
        db.close()
        print("Database connection closed.")
