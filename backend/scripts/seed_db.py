import os
import sys
from pathlib import Path

# Add the project root to PYTHONPATH
root_dir = Path(__file__).resolve().parent.parent
sys.path.append(str(root_dir))

from app.db.init_db import init_db
from app.db.session import SessionLocal

def seed_db():
    """Seed the database with initial data."""
    db = SessionLocal()
    try:
        init_db(db)
        print("Database seeded successfully!")
    except Exception as e:
        print(f"Error seeding database: {e}", file=sys.stderr)
        sys.exit(1)
    finally:
        db.close()

if __name__ == "__main__":
    seed_db()