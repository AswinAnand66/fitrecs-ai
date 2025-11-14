"""Database initialization."""
from sqlalchemy.orm import Session

from .base import Base
from .session import engine
from . import models

def init_db() -> None:
    """Create database tables."""
    Base.metadata.create_all(bind=engine)