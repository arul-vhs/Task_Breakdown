import uuid
import json
from typing import Dict, Any, Optional, List
from app.repositories.user_repository import UserRepository
from app.repositories.goal_repository import GoalRepository
from app.providers.base_provider import BaseProvider
from app.utils.prompts import get_goal_analysis_prompt

class GoalService:
    def __init__(
        self,
        user_repository: UserRepository,
        goal_repository: GoalRepository,
        provider: BaseProvider
    ):
        self.user_repository = user_repository
        self.goal_repository = goal_repository
        self.provider = provider

    def analyze_goal_and_initialize_context(self, goal_id: uuid.UUID, user_id: uuid.UUID) -> Dict[str, Any]:
        """
        Extracts goal description, generates dynamic context questions using Gemini,
        and saves context into database.
        """
        # Load user profile
        profile = self.user_repository.get_profile(user_id)
        if not profile:
            raise ValueError("User onboarding profile not found.")
            
        profile_data = {
            "role": profile.role,
            "work_style": profile.work_style,
            "hours_per_week": float(profile.weekly_hours_available),
            "biggest_challenge": profile.biggest_challenge
        }
        
        goal = self.goal_repository.get_by_id(goal_id, user_id)
        if not goal:
            raise ValueError("Goal not found.")

        # Build prompt using the existing exact prompts logic
        prompt = get_goal_analysis_prompt(goal.title, profile_data)
        
        # Call provider with JSON response requested
        try:
            raw_response = self.provider.generate(prompt=prompt, json_mode=True)
            analysis = json.loads(raw_response)
        except (ValueError, json.JSONDecodeError) as e:
            raise ValueError(f"Failed to analyze goal: AI provider returned invalid or empty response. Details: {e}")
        
        questions = analysis.get("dynamic_questions", [])
        qa_context = [{"question": q, "answer": ""} for q in questions]
        
        # Persist Goal Context using GoalRepository
        self.goal_repository.save_context(
            goal_id=goal_id,
            category=analysis.get("category", "General"),
            difficulty=analysis.get("difficulty", "Intermediate"),
            estimated_duration=analysis.get("estimated_duration", "Flexible"),
            required_skills=analysis.get("required_skills", []),
            risks=analysis.get("risks", []),
            qa_context=qa_context,
            context_json=analysis
        )
        
        # Log event tracking (Event Sourcing)
        self.goal_repository.log_goal_event(
            goal_id=goal_id,
            event_type="goal_intake_initialized",
            payload=analysis
        )
        
        self.goal_repository.update_status(goal_id, "drafting", user_id)
        
        return {
            "goal_id": str(goal_id),
            "status": "drafting",
            "category": analysis.get("category"),
            "difficulty": analysis.get("difficulty"),
            "estimated_duration": analysis.get("estimated_duration"),
            "required_skills": analysis.get("required_skills"),
            "risks": analysis.get("risks"),
            "questions": questions
        }

    def submit_ingestion_answers(self, goal_id: uuid.UUID, user_id: uuid.UUID, answers: List[Dict[str, str]]) -> Dict[str, Any]:
        """
        Submits context onboarding answers. Updates context and logs event.
        """
        ctx = self.goal_repository.get_context(goal_id)
        if not ctx:
            raise ValueError("Goal context not initialized.")
            
        compiled_qa = []
        for item in answers:
            compiled_qa.append({
                "question": item["question"],
                "answer": item["answer"]
            })
            
        ctx.qa_context = compiled_qa
        self.goal_repository.db.commit()
        
        # Log event
        self.goal_repository.log_goal_event(
            goal_id=goal_id,
            event_type="goal_context_answers_submitted",
            payload={"answers": compiled_qa}
        )
        
        return {"status": "context_updated"}
