import uuid
import json
from typing import Dict, Any, List, Optional
from app.repositories.user_repository import UserRepository
from app.repositories.goal_repository import GoalRepository
from app.repositories.strategy_repository import StrategyRepository
from app.providers.base_provider import BaseProvider
from app.utils.prompts import get_strategy_generation_prompt

class StrategyService:
    def __init__(
        self,
        user_repository: UserRepository,
        goal_repository: GoalRepository,
        strategy_repository: StrategyRepository,
        provider: BaseProvider
    ):
        self.user_repository = user_repository
        self.goal_repository = goal_repository
        self.strategy_repository = strategy_repository
        self.provider = provider

    def generate_strategies(self, goal_id: uuid.UUID, user_id: uuid.UUID) -> Dict[str, Any]:
        """
        Invokes LLM provider to construct Fast MVP, Balanced Growth, Ambitious Scale.
        """
        # Load user profile
        profile = self.user_repository.get_profile(user_id)
        if not profile:
            raise ValueError("Profile not found.")
            
        profile_data = {
            "role": profile.role,
            "work_style": profile.work_style,
            "weekly_hours_available": float(profile.weekly_hours_available),
            "biggest_challenge": profile.biggest_challenge
        }
        
        # Simple fallback persona description
        persona = {
            "name": f"Consistent {profile.role or 'Explorer'}",
            "strength": "Adaptability",
            "challenge": profile.biggest_challenge or "Time Management",
            "strategy": "Micro-habits planning"
        }
        
        # Load context
        ctx = self.goal_repository.get_context(goal_id)
        if not ctx:
            raise ValueError("Goal context not initialized.")
            
        goal = self.goal_repository.get_by_id(goal_id, user_id)
        if not goal:
            raise ValueError("Goal not found.")

        goal_context_dict = {
            "goal": goal.title,
            "category": ctx.category,
            "difficulty": ctx.difficulty,
            "estimated_duration": ctx.estimated_duration,
            "required_skills": ctx.required_skills,
            "risks": ctx.risks,
            "qa_context": ctx.qa_context
        }

        # Build prompt using exactly the original logic
        prompt = get_strategy_generation_prompt(goal_context_dict, profile_data, persona)
        
        raw_response = self.provider.generate(prompt=prompt, json_mode=True)
        
        # 2. Print and inspect raw LLM response
        print(f"[StrategyService] Raw LLM Response:\n{raw_response}")
        
        # 6. Reuse the JSON cleaning utility from GeminiProvider if available
        if hasattr(self.provider, "_clean_json"):
            cleaned_response = self.provider._clean_json(raw_response)
        else:
            cleaned_response = raw_response.strip()
            
        try:
            strat_res = json.loads(cleaned_response)
        except json.JSONDecodeError as e:
            raise ValueError(f"Failed to parse strategies JSON payload: {e}")
            
        # 9. Show parsed JSON
        print(f"[StrategyService] Parsed JSON:\n{json.dumps(strat_res, indent=2)}")
        
        strategies_raw = strat_res.get("strategies", [])
        recommended_key = strat_res.get("recommended_strategy_key", "balanced_growth")
        
        strategies_list = []
        for s in strategies_raw:
            strategy_key = s.get("strategy_key") or s.get("key")
            title = s.get("name") or s.get("title")
            description = s.get("description")
            
            # 7. Validation: key, title, description are required
            if not strategy_key:
                raise ValueError("Validation failed: 'strategy_key' is required for each strategy option.")
            if not title:
                raise ValueError(f"Validation failed: 'title' (or 'name') is required for strategy '{strategy_key}'.")
            if not description:
                raise ValueError(f"Validation failed: 'description' is required for strategy '{strategy_key}'.")
                
            # 5. Normalize LLM output into repository schema
            normalized_strat = {
                "strategy_key": strategy_key,
                "title": title,
                "description": description,
                "pros": s.get("pros", []),
                "cons": s.get("cons", []),
                "is_recommended": (strategy_key == recommended_key),
                "is_selected": False,
                "estimated_duration": s.get("estimated_duration", ""),
                "effort_level": s.get("effort_level", "")
            }
            strategies_list.append(normalized_strat)
            
        # 3. Print parsed/normalized strategies_list before saving
        print(f"[StrategyService] Normalized strategies list:\n{json.dumps(strategies_list, indent=2)}")
        
        # Save strategies to DB
        self.strategy_repository.save_strategies(goal_id, strategies_list)
        self.goal_repository.update_status(goal_id, "strat_selection", user_id)
        
        # Log event tracking
        self.goal_repository.log_goal_event(
            goal_id=goal_id,
            event_type="strategies_generated",
            payload={"strategies": strategies_list, "recommended": recommended_key}
        )
        
        return {
            "strategies": strategies_list,
            "recommended_strategy_key": recommended_key,
            "recommendation_explanation": strat_res.get("recommendation_explanation", "")
        }

    def select_strategy(self, goal_id: uuid.UUID, strategy_key: str, user_id: uuid.UUID) -> Dict[str, Any]:
        """
        Deselects previous strategies and makes key strategy active.
        """
        selected = self.strategy_repository.select_strategy(goal_id, strategy_key)
        if not selected:
            raise ValueError("Invalid strategy choice.")
            
        # Log event tracking
        self.goal_repository.log_goal_event(
            goal_id=goal_id,
            event_type="strategy_selected",
            payload={"strategy_key": strategy_key}
        )
        
        return {"status": "selected", "strategy": selected}
