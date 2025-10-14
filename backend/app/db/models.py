from sqlalchemy import Column, Integer, String, Float, ForeignKey, Enum, DateTime, JSON
from sqlalchemy.orm import relationship
from datetime import datetime
import enum

from .base import Base

class UserRole(str, enum.Enum):
    ADMIN = "admin"
    USER = "user"

class ItemType(str, enum.Enum):
    ARTICLE = "article"
    WORKOUT = "workout"
    VIDEO = "video"

class InteractionType(str, enum.Enum):
    VIEW = "view"
    LIKE = "like"
    COMPLETE = "complete"

class DifficultyLevel(str, enum.Enum):
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    username = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    role = Column(Enum(UserRole), default=UserRole.USER)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    interactions = relationship("Interaction", back_populates="user")

class Item(Base):
    __tablename__ = "items"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True, nullable=False)
    type = Column(Enum(ItemType), nullable=False)
    description = Column(String)
    tags = Column(JSON)  # Store as JSON array
    duration = Column(Integer)  # in minutes
    difficulty = Column(Enum(DifficultyLevel))
    media_url = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    interactions = relationship("Interaction", back_populates="item")
    embedding_index = relationship("EmbeddingIndex", back_populates="item", uselist=False)

class Interaction(Base):
    __tablename__ = "interactions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    item_id = Column(Integer, ForeignKey("items.id"), nullable=False)
    interaction_type = Column(Enum(InteractionType), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    user = relationship("User", back_populates="interactions")
    item = relationship("Item", back_populates="interactions")

class EmbeddingIndex(Base):
    __tablename__ = "embedding_index"

    id = Column(Integer, primary_key=True, index=True)
    item_id = Column(Integer, ForeignKey("items.id"), unique=True, nullable=False)
    faiss_id = Column(Integer, unique=True, nullable=False)  # Position in FAISS index
    embedding = Column(JSON, nullable=True)  # Optional: store raw embedding if needed
    
    item = relationship("Item", back_populates="embedding_index")