from typing import List
from pydantic import BaseModel
from app.schemas.item import Item

class ExplanationResponse(BaseModel):
    explanation: str

class ContextualRecommendationResponse(BaseModel):
    items: List[Item]
    explanation: str