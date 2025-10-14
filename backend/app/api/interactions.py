from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session

from ..core.security import get_current_active_user
from ..db.session import get_db
from ..db.models import User, Item, Interaction, InteractionType
from ..schemas.interaction import InteractionCreate, Interaction as InteractionSchema
from ..services.recommender import recommender

router = APIRouter()

@router.post("/", response_model=InteractionSchema)
def create_interaction(
    *,
    db: Session = Depends(get_db),
    interaction_in: InteractionCreate,
    current_user: User = Depends(get_current_active_user)
) -> Any:
    """
    Record a user interaction (view/like/complete) with an item.
    """
    # Verify item exists
    item = db.query(Item).filter(Item.id == interaction_in.item_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
        
    # Create interaction
    interaction = Interaction(
        user_id=current_user.id,
        item_id=interaction_in.item_id,
        interaction_type=interaction_in.interaction_type
    )
    
    db.add(interaction)
    db.commit()
    db.refresh(interaction)
    
    # Background task to update recommender models could be added here
    return interaction

@router.get("/me", response_model=List[InteractionSchema])
def list_my_interactions(
    *,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> Any:
    """
    List all interactions for the current user.
    """
    interactions = (
        db.query(Interaction)
        .filter(Interaction.user_id == current_user.id)
        .order_by(Interaction.created_at.desc())
        .all()
    )
    return interactions

@router.post("/retrain")
def retrain_recommender(
    *,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> Any:
    """
    Retrain the collaborative filtering model with latest interactions.
    Admin only.
    """
    if current_user.role != "admin":
        raise HTTPException(
            status_code=403,
            detail="Only admin users can trigger retraining"
        )
        
    # Get all interactions
    interactions = db.query(Interaction).all()
    
    # Retrain collaborative model
    recommender.fit_collaborative(interactions)
    
    return {"message": "Recommender model retrained successfully"}