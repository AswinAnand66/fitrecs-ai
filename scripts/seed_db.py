import os
import sys
import pandas as pd
import json
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import random
from datetime import datetime, timedelta

# Add the backend directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "backend"))

from app.core.config import settings
from app.db.base import Base
from app.db.models import User, Item, Interaction, InteractionType, ItemType, DifficultyLevel
from app.core.security import get_password_hash
from app.services.embeddings import embedding_service
from app.services.indexer import indexer_service
from app.services.recommender import recommender

def create_test_users(db):
    """Create test users"""
    users = [
        {
            "email": "admin@example.com",
            "username": "admin",
            "password": "admin123",
            "role": "admin"
        },
        {
            "email": "user@example.com",
            "username": "testuser",
            "password": "test123",
            "role": "user"
        }
    ]
    
    created_users = []
    for user_data in users:
        user = User(
            email=user_data["email"],
            username=user_data["username"],
            hashed_password=get_password_hash(user_data["password"]),
            role=user_data["role"]
        )
        db.add(user)
        created_users.append(user)
        
    db.commit()
    return created_users

def load_items(db, csv_path):
    """Load items from CSV file"""
    df = pd.read_csv(csv_path)
    items = []
    
    for _, row in df.iterrows():
        # Parse tags from string if needed
        tags = row["tags"]
        if isinstance(tags, str):
            tags = json.loads(tags)
            
        item = Item(
            title=row["title"],
            type=ItemType[row["type"].upper()],
            description=row["description"],
            tags=tags,
            duration=row["duration"],
            difficulty=DifficultyLevel[row["difficulty"].upper()],
            media_url=row["media_url"] if pd.notnull(row["media_url"]) else None
        )
        db.add(item)
        items.append(item)
        
    db.commit()
    return items

def generate_interactions(db, users, items):
    """Generate synthetic interactions"""
    interactions = []
    
    # Each user interacts with some items
    for user in users:
        # Randomly select items to interact with
        n_interactions = random.randint(3, len(items))
        selected_items = random.sample(items, n_interactions)
        
        for item in selected_items:
            # Random interaction type with weights
            interaction_type = random.choices(
                list(InteractionType),
                weights=[0.5, 0.3, 0.2]  # VIEW more common than LIKE or COMPLETE
            )[0]
            
            interaction = Interaction(
                user_id=user.id,
                item_id=item.id,
                interaction_type=interaction_type,
                created_at=datetime.utcnow() - timedelta(
                    days=random.randint(0, 30)
                )
            )
            db.add(interaction)
            interactions.append(interaction)
            
    db.commit()
    return interactions

def main():
    # Create database engine
    engine = create_engine(settings.DATABASE_URL)
    Base.metadata.create_all(engine)
    
    # Create session
    Session = sessionmaker(bind=engine)
    db = Session()
    
    try:
        print("Creating test users...")
        users = create_test_users(db)
        
        print("Loading items from CSV...")
        items = load_items(db, os.path.join("data", "sample_fitness_items.csv"))
        
        print("Generating synthetic interactions...")
        interactions = generate_interactions(db, users, items)
        
        print("Computing embeddings and building FAISS index...")
        indexer_service.rebuild_index(items)
        
        print("Training collaborative filtering model...")
        recommender.fit_collaborative(interactions)
        
        print("Seed completed successfully!")
        
    except Exception as e:
        print(f"Error during seeding: {e}")
        db.rollback()
        raise
    finally:
        db.close()

if __name__ == "__main__":
    main()