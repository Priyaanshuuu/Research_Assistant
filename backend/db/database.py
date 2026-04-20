from sqlalchemy import create_engine , event
from sqlalchemy.orm import sessionmaker , DeclarativeBase
from typing import Generator 
from loguru import logger

from core.config import settings

engine = create_engine(
    settings.DATABASE_URL,
    pool_pre_ping = True,
    pool_size = 10,
    max_overflow = 20,
)

class Base(DeclarativeBase):
    pass

SessionLocal = sessionmaker(autocommit = False, autoflush = False , bind = engine)

def get_db() -> Generator:
    """FastAPi dependency - yields a SQLAlchmy session and always closes it"""
    db = SessionLocal()
    try:
        yield db
    except Exception as exc:
        logger.error("DB session error: {}"  , exc)
        db.rollback()
        raise
    finally: 
        db.close()
