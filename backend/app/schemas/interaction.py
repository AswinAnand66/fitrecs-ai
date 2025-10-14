from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from ..db.models import InteractionType

class InteractionBase(BaseModel):
    item_id: int
    interaction_type: InteractionType

class InteractionCreate(InteractionBase):
    pass

class Interaction(InteractionBase):
    id: int
    user_id: int
    created_at: datetime
    
    class Config:
        orm_mode = True