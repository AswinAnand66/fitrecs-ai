from typing import List, Optional, Any
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.security import get_current_active_user
from app.db.session import get_db
from app.db.models import User, Item, Interaction
from app.schemas.item import ItemWithSimilarity
from app.services.recommender import recommender
from app.services.indexer import indexer_service

router = APIRouter()

@router.get("/content/{item_id}", response_model=List[ItemWithSimilarity])
def get_content_based_recommendations(
    *,
    db: Session = Depends(get_db),
    item_id: int,
    topn: int = settings.DEFAULT_TOP_K,
    current_user: User = Depends(get_current_active_user)
) -> Any:
    """
    Get content-based recommendations similar to the given item.
    """
    item = db.query(Item).filter(Item.id == item_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
        
    similar_items = indexer_service.find_similar(item_id, k=topn)
    
    # Fetch full items with similarity scores
    recommendations = []
    for similar_id, similarity in similar_items:
        similar_item = db.query(Item).filter(Item.id == similar_id).first()
        if similar_item:
            item_dict = ItemWithSimilarity.from_orm(similar_item).dict()
            item_dict["similarity_score"] = similarity
            recommendations.append(item_dict)
            
    return recommendations

@router.get("/collaborative/{user_id}", response_model=List[ItemWithSimilarity])
def get_collaborative_recommendations(
    *,
    db: Session = Depends(get_db),
    user_id: int,
    topn: int = settings.DEFAULT_TOP_K,
    current_user: User = Depends(get_current_active_user)
) -> Any:
    """
    Get collaborative filtering recommendations for a user.
    """
    # Get user's viewed items
    viewed_items = set(
        inter.item_id 
        for inter in db.query(Interaction)
        .filter(Interaction.user_id == user_id)
        .all()
    )
    
    # Get recommendations
    recommended_items = recommender.get_user_recommendations(
        user_id,
        n_items=topn,
        viewed_items=list(viewed_items)
    )
    
    # Fetch full items with scores
    recommendations = []
    for item_id, score in recommended_items:
        item = db.query(Item).filter(Item.id == item_id).first()
        if item:
            item_dict = ItemWithSimilarity.from_orm(item).dict()
            item_dict["similarity_score"] = score
            recommendations.append(item_dict)
            
    return recommendations

@router.get("/hybrid/{user_id}", response_model=List[ItemWithSimilarity])
def get_hybrid_recommendations(
    *,
    db: Session = Depends(get_db),
    user_id: int,
    item_id: Optional[int] = None,
    topn: int = settings.DEFAULT_TOP_K,
    alpha: float = settings.HYBRID_ALPHA,
    current_user: User = Depends(get_current_active_user)
) -> Any:
    """
    Get hybrid recommendations combining collaborative and content-based filtering.
    """
    # Validate item if provided
    if item_id:
        item = db.query(Item).filter(Item.id == item_id).first()
        if not item:
            raise HTTPException(status_code=404, detail="Item not found")
            
    # Get user's viewed items
    viewed_items = set(
        inter.item_id 
        for inter in db.query(Interaction)
        .filter(Interaction.user_id == user_id)
        .all()
    )
    
    # Get hybrid recommendations
    recommended_items = recommender.get_hybrid_recommendations(
        user_id,
        item_id=item_id,
        n_items=topn,
        alpha=alpha,
        viewed_items=list(viewed_items)
    )
    
    # Fetch full items with scores
    recommendations = []
    for item_id, score in recommended_items:
        item = db.query(Item).filter(Item.id == item_id).first()
        if item:
            item_dict = ItemWithSimilarity.from_orm(item).dict()
            item_dict["similarity_score"] = score
            recommendations.append(item_dict)
            
    return recommendations