import os
from pathlib import Path

from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

from ..config import DATABASE_URL

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db() -> None:
    print("Initializing database...")
    db_dir = Path("./data")
    if not os.path.exists(db_dir):
        os.makedirs(db_dir)

    Base.metadata.create_all(bind=engine)
    print("Database initialized.")
