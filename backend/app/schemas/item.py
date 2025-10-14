from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
from ..db.models import ItemType, DifficultyLevel

class ItemBase(BaseModel):
    title: str
    type: ItemType
    description: Optional[str] = None
    tags: List[str]
    duration: int
    difficulty: DifficultyLevel
    media_url: Optional[str] = None

class ItemCreate(ItemBase):
    pass

class Item(ItemBase):
    id: int
    created_at: datetime
    
    class Config:
        orm_mode = True

class ItemWithSimilarity(Item):
    similarity_score: Optional[float] = None