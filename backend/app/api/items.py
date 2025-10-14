from typing import List, Any, Optional
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, BackgroundTasks
from sqlalchemy.orm import Session
import pandas as pd
import json

from ..core.security import get_current_active_user
from ..db.session import get_db
from ..db.models import User, Item, ItemType, DifficultyLevel
from ..schemas.item import ItemCreate, Item as ItemSchema, ItemWithSimilarity
from ..services.embeddings import embedding_service
from ..services.indexer import indexer_service
from ..services.recommender import recommender

router = APIRouter()

@router.get("/", response_model=List[ItemSchema])
def list_items(
    *,
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_active_user)
) -> Any:
    """
    Retrieve items with pagination.
    """
    items = db.query(Item).offset(skip).limit(limit).all()
    return items

@router.get("/search", response_model=List[ItemSchema])
def search_items(
    *,
    db: Session = Depends(get_db),
    q: str,
    current_user: User = Depends(get_current_active_user)
) -> Any:
    """
    Search items by title or description.
    """
    items = db.query(Item).filter(
        (Item.title.ilike(f"%{q}%")) | 
        (Item.description.ilike(f"%{q}%"))
    ).all()
    return items

@router.get("/{item_id}", response_model=ItemSchema)
def get_item(
    *,
    db: Session = Depends(get_db),
    item_id: int,
    current_user: User = Depends(get_current_active_user)
) -> Any:
    """
    Get item by ID.
    """
    item = db.query(Item).filter(Item.id == item_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    return item

def process_upload(db: Session, items_data: List[dict]) -> None:
    """Background task to process uploaded items"""
    new_items = []
    for item_data in items_data:
        item = Item(
            title=item_data["title"],
            type=ItemType[item_data["type"].upper()],
            description=item_data.get("description"),
            tags=item_data["tags"],
            duration=item_data["duration"],
            difficulty=DifficultyLevel[item_data["difficulty"].upper()],
            media_url=item_data.get("media_url")
        )
        db.add(item)
        new_items.append(item)
    
    db.commit()
    
    # Compute embeddings and update index
    indexer_service.add_items(new_items)
    indexer_service.save_index()

@router.post("/upload")
async def upload_items(
    *,
    db: Session = Depends(get_db),
    file: UploadFile = File(...),
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_active_user)
) -> Any:
    """
    Upload items from CSV file.
    """
    if not file.filename.endswith('.csv'):
        raise HTTPException(
            status_code=400,
            detail="Only CSV files are supported"
        )
        
    # Read CSV
    df = pd.read_csv(file.file)
    required_columns = ["title", "type", "tags", "duration", "difficulty"]
    
    if not all(col in df.columns for col in required_columns):
        raise HTTPException(
            status_code=400,
            detail=f"CSV must contain columns: {', '.join(required_columns)}"
        )
        
    # Convert DataFrame to list of dicts
    items_data = []
    for _, row in df.iterrows():
        item_dict = row.to_dict()
        # Convert tags string to list if needed
        if isinstance(item_dict["tags"], str):
            item_dict["tags"] = json.loads(item_dict["tags"])
        items_data.append(item_dict)
        
    # Process in background
    background_tasks.add_task(process_upload, db, items_data)
    
    return {"message": "Upload processing started", "items_count": len(items_data)}

@router.post("/rebuild-index")
def rebuild_index(
    *,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> Any:
    """
    Rebuild the FAISS index for all items.
    """
    if current_user.role != "admin":
        raise HTTPException(
            status_code=403,
            detail="Only admin users can rebuild the index"
        )
        
    items = db.query(Item).all()
    indexer_service.rebuild_index(items)
    
    return {"message": "Index rebuilt successfully", "items_count": len(items)}