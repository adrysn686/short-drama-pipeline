"""SQLAlchemy engine/session setup. Tables are defined in db/migrations/001_init.sql
rather than ORM models, since the schema is applied directly to Postgres on
container init — this module is just the connection layer for the routers."""
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from .config import get_settings

settings = get_settings()

engine = create_engine(settings.database_url, pool_pre_ping=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
