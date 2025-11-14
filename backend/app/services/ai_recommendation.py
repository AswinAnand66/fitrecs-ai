from typing import List, Optional
from langchain.llms import OpenAI
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from langchain.output_parsers import PydanticOutputParser
from pydantic import BaseModel, Field
from datetime import datetime, timedelta
import json

class ContextualRecommendation(BaseModel):
    item_ids: List[int] = Field(description="List of item IDs to recommend")
    explanation: str = Field(description="Natural language explanation of the recommendations")

class AIRecommendationService:
    def __init__(self, api_key: str, model_name: str = "gpt-4"):
        self.llm = OpenAI(openai_api_key=api_key, model_name=model_name)
        self.parser = PydanticOutputParser(pydantic_object=ContextualRecommendation)

        self.recommendation_prompt = PromptTemplate(
            template="""
            Given a user's fitness context, suggest relevant content items and explain why.

            User Context:
            - Recent Activities: {recent_activities}
            - Liked Items: {liked_items}
            - Completed Items: {completed_items}
            - Goals: {goals}
            - Fitness Level: {fitness_level}

            Available Items:
            {available_items}

            Generate personalized recommendations by analyzing patterns, goals, and preferences.
            Ensure recommendations are diverse yet relevant to the user's journey.

            {format_instructions}
            """,
            input_variables=[
                "recent_activities",
                "liked_items",
                "completed_items",
                "goals",
                "fitness_level",
                "available_items"
            ],
            partial_variables={
                "format_instructions": self.parser.get_format_instructions()
            }
        )

        self.explanation_prompt = PromptTemplate(
            template="""
            Explain why this fitness content item would be relevant for the user.

            User Context:
            - Recent Activities: {recent_activities}
            - Goals: {goals}
            - Fitness Level: {fitness_level}

            Item Details:
            {item_details}

            Generate a concise, personalized explanation (2-3 sentences) of why this item is recommended.
            Focus on the user's goals, preferences, and fitness journey.
            """,
            input_variables=[
                "recent_activities",
                "goals",
                "fitness_level",
                "item_details"
            ]
        )

        self.chain = LLMChain(llm=self.llm, prompt=self.recommendation_prompt)
        self.explanation_chain = LLMChain(llm=self.llm, prompt=self.explanation_prompt)

    async def get_contextual_recommendations(
        self,
        recent_activities: List[dict],
        liked_items: List[dict],
        completed_items: List[dict],
        goals: List[str],
        fitness_level: str,
        available_items: List[dict],
        limit: int = 5
    ) -> ContextualRecommendation:
        # Format activities for better context
        recent_activities_str = self._format_activities(recent_activities)
        liked_items_str = self._format_items(liked_items, "liked")
        completed_items_str = self._format_items(completed_items, "completed")
        available_items_str = json.dumps(
            [{"id": item["id"], "title": item["title"], "type": item["type"]} 
             for item in available_items],
            indent=2
        )

        # Get recommendations from LLM
        result = await self.chain.arun(
            recent_activities=recent_activities_str,
            liked_items=liked_items_str,
            completed_items=completed_items_str,
            goals=", ".join(goals),
            fitness_level=fitness_level,
            available_items=available_items_str
        )

        # Parse the LLM output
        recommendations = self.parser.parse(result)
        
        # Limit the number of recommendations
        recommendations.item_ids = recommendations.item_ids[:limit]
        
        return recommendations

    async def explain_recommendation(
        self,
        item: dict,
        recent_activities: List[dict],
        goals: List[str],
        fitness_level: str
    ) -> str:
        recent_activities_str = self._format_activities(recent_activities)
        item_details = json.dumps(item, indent=2)

        explanation = await self.explanation_chain.arun(
            recent_activities=recent_activities_str,
            goals=", ".join(goals),
            fitness_level=fitness_level,
            item_details=item_details
        )

        return explanation.strip()

    def _format_activities(self, activities: List[dict]) -> str:
        if not activities:
            return "No recent activities"

        formatted = []
        for activity in activities:
            date = datetime.fromisoformat(activity["created_at"])
            days_ago = (datetime.now() - date).days
            time_str = f"{days_ago} days ago" if days_ago > 0 else "today"
            formatted.append(
                f"{activity['interaction_type']} {activity['item']['type']} "
                f"'{activity['item']['title']}' ({time_str})"
            )

        return "\n".join(formatted)

    def _format_items(self, items: List[dict], action: str) -> str:
        if not items:
            return f"No {action} items"

        return "\n".join([
            f"- {item['type']}: {item['title']}"
            for item in items
        ])