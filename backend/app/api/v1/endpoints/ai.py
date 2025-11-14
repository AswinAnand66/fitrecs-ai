from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.config import settings
from app.api.deps import get_current_user, get_db
from app.services.ai_recommendation import AIRecommendationService
from app.services.fitness_coach import FitnessCoachService
from app.models.user import User
from app.models.item import Item
from app.models.interaction import Interaction
from app.crud.interaction import interaction as interaction_crud
from app.crud.item import item as item_crud
from app.schemas.ai import ContextualRecommendationResponse, ExplanationResponse
from app.schemas.chat import ChatRequest, ChatResponse

router = APIRouter()
ai_service = AIRecommendationService(settings.OPENAI_API_KEY)
fitness_coach = FitnessCoachService(settings.OPENAI_API_KEY)

@router.get("/recommendations/contextual", response_model=ContextualRecommendationResponse)
async def get_contextual_recommendations(
    limit: int = 5,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get AI-powered contextual recommendations based on user history and preferences.
    """
    try:
        # Get user's recent activity (last 30 days)
        recent_interactions = await interaction_crud.get_user_recent_interactions(
            db, user.id, days=30
        )

        # Get liked and completed items
        liked_items = await interaction_crud.get_user_interactions_by_type(
            db, user.id, "like"
        )
        completed_items = await interaction_crud.get_user_interactions_by_type(
            db, user.id, "complete"
        )

        # Get available items (excluding those the user has interacted with)
        user_item_ids = {i.item_id for i in recent_interactions}
        available_items = await item_crud.get_multi(
            db, skip_ids=list(user_item_ids)
        )

        # Get AI recommendations
        recommendations = await ai_service.get_contextual_recommendations(
            recent_activities=[
                {
                    "interaction_type": i.interaction_type,
                    "item": {
                        "id": i.item.id,
                        "title": i.item.title,
                        "type": i.item.type,
                    },
                    "created_at": i.created_at.isoformat(),
                }
                for i in recent_interactions
            ],
            liked_items=[
                {
                    "id": i.item.id,
                    "title": i.item.title,
                    "type": i.item.type,
                }
                for i in liked_items
            ],
            completed_items=[
                {
                    "id": i.item.id,
                    "title": i.item.title,
                    "type": i.item.type,
                }
                for i in completed_items
            ],
            goals=user.preferences.get("goals", []),
            fitness_level=user.preferences.get("fitness_level", "beginner"),
            available_items=[
                {
                    "id": item.id,
                    "title": item.title,
                    "type": item.type,
                    "description": item.description,
                    "difficulty": item.difficulty,
                }
                for item in available_items
            ],
            limit=limit
        )

        # Fetch recommended items from database
        recommended_items = await item_crud.get_multi_by_ids(
            db, recommendations.item_ids
        )

        return ContextualRecommendationResponse(
            items=recommended_items,
            explanation=recommendations.explanation
        )

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error generating recommendations: {str(e)}"
        )

@router.get("/explain/{item_id}", response_model=ExplanationResponse)
async def explain_recommendation(
    item_id: int,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get an AI-generated explanation for why an item was recommended.
    """
    try:
        # Get the item
        item = await item_crud.get(db, id=item_id)
        if not item:
            raise HTTPException(status_code=404, detail="Item not found")

        # Get user's recent activity
        recent_interactions = await interaction_crud.get_user_recent_interactions(
            db, user.id, days=30
        )

        # Generate explanation
        explanation = await ai_service.explain_recommendation(
            item={
                "id": item.id,
                "title": item.title,
                "type": item.type,
                "description": item.description,
                "difficulty": item.difficulty,
                "tags": item.tags,
            },
            recent_activities=[
                {
                    "interaction_type": i.interaction_type,
                    "item": {
                        "id": i.item.id,
                        "title": i.item.title,
                        "type": i.item.type,
                    },
                    "created_at": i.created_at.isoformat(),
                }
                for i in recent_interactions
            ],
            goals=user.preferences.get("goals", []),
            fitness_level=user.preferences.get("fitness_level", "beginner")
        )

        return ExplanationResponse(explanation=explanation)

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error generating explanation: {str(e)}"
        )

@router.post("/chat", response_model=ChatResponse)
async def chat_with_fitness_coach(
    request: ChatRequest,
    user: User = Depends(get_current_user)
):
    """
    Chat with the AI fitness coach.
    """
    try:
        response = await fitness_coach.get_response(
            request.message,
            request.context
        )
        return ChatResponse(response=response)
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error getting response: {str(e)}"
        )