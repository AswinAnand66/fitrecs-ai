"""Service layer initialization."""
from .embeddings import embedding_service
from .indexer import indexer_service
from .recommender import recommender
from .fitness_coach import FitnessCoachService
from .ai_recommendation import ai_recommender

__all__ = [
    "embedding_service",
    "indexer_service",
    "recommender",
    "FitnessCoachService",
    "ai_recommender"
]