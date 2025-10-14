import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import numpy as np
from datetime import datetime

from ..core.config import settings
from ..db.base import Base
from ..db.models import User, Item, Interaction, ItemType, DifficultyLevel, InteractionType
from ..services.recommender import RecommenderService
from ..services.embeddings import EmbeddingService
from ..services.indexer import IndexerService

# Test data
TEST_ITEMS = [
    {
        "title": "Test Workout 1",
        "type": ItemType.WORKOUT,
        "description": "Test workout description",
        "tags": ["test", "workout"],
        "duration": 30,
        "difficulty": DifficultyLevel.INTERMEDIATE
    },
    {
        "title": "Test Article 1",
        "type": ItemType.ARTICLE,
        "description": "Test article description",
        "tags": ["test", "article"],
        "duration": 15,
        "difficulty": DifficultyLevel.BEGINNER
    }
]

@pytest.fixture
def db_session():
    """Create a test database session"""
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    
    yield session
    
    session.close()
    Base.metadata.drop_all(engine)

@pytest.fixture
def test_items(db_session):
    """Create test items in the database"""
    items = []
    for item_data in TEST_ITEMS:
        item = Item(**item_data)
        db_session.add(item)
        items.append(item)
    db_session.commit()
    return items

@pytest.fixture
def test_user(db_session):
    """Create a test user"""
    user = User(
        email="test@example.com",
        username="testuser",
        hashed_password="dummyhash"
    )
    db_session.add(user)
    db_session.commit()
    return user

@pytest.fixture
def test_interactions(db_session, test_user, test_items):
    """Create test interactions"""
    interactions = []
    for item in test_items:
        interaction = Interaction(
            user_id=test_user.id,
            item_id=item.id,
            interaction_type=InteractionType.VIEW,
            created_at=datetime.utcnow()
        )
        db_session.add(interaction)
        interactions.append(interaction)
    db_session.commit()
    return interactions

def test_content_based_recommendations(test_items):
    """Test content-based recommendations using FAISS"""
    indexer = IndexerService()
    
    # Initialize index with test items
    indexer.rebuild_index(test_items)
    
    # Get recommendations for first item
    similar_items = indexer.find_similar(test_items[0].id, k=1)
    
    assert len(similar_items) == 1
    assert similar_items[0][0] == test_items[1].id  # Should return the other item
    assert 0 <= similar_items[0][1] <= 1  # Similarity score should be normalized

def test_collaborative_recommendations(test_interactions):
    """Test collaborative filtering recommendations"""
    recommender = RecommenderService()
    
    # Train the model
    recommender.fit_collaborative(test_interactions)
    
    # Get recommendations for the test user
    user_id = test_interactions[0].user_id
    recommendations = recommender.get_user_recommendations(
        user_id,
        n_items=1
    )
    
    assert len(recommendations) == 1
    assert isinstance(recommendations[0][0], int)  # Item ID
    assert isinstance(recommendations[0][1], float)  # Score

def test_hybrid_recommendations(test_items, test_interactions):
    """Test hybrid recommendations"""
    recommender = RecommenderService()
    
    # Initialize content-based components
    recommender.create_faiss_index()
    for item in test_items:
        embedding = recommender.compute_item_embedding(item)
        recommender.add_item_to_index(item, embedding)
    
    # Train collaborative model
    recommender.fit_collaborative(test_interactions)
    
    # Get hybrid recommendations
    user_id = test_interactions[0].user_id
    item_id = test_items[0].id
    
    recommendations = recommender.get_hybrid_recommendations(
        user_id,
        item_id=item_id,
        n_items=1,
        alpha=0.5  # Equal weight to CF and content-based
    )
    
    assert len(recommendations) == 1
    assert isinstance(recommendations[0][0], int)  # Item ID
    assert isinstance(recommendations[0][1], float)  # Score
    assert 0 <= recommendations[0][1] <= 1  # Score should be normalized