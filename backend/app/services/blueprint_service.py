import uuid
import json
from typing import Dict, Any, List, Optional
from app.repositories.user_repository import UserRepository
from app.repositories.goal_repository import GoalRepository
from app.repositories.strategy_repository import StrategyRepository
from app.providers.base_provider import BaseProvider
from app.utils.prompts import (
    get_execution_blueprint_prompt,
    get_task_breakdown_prompt
)

class BlueprintService:
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

    def generate_roadmap_and_tasks(
        self,
        goal_id: uuid.UUID,
        user_id: uuid.UUID,
        refinement_choice: str = "Standard",
        depth: str = "Detailed"
    ) -> Dict[str, Any]:
        """
        Creates roadmap phases blueprint, runs task breakdown decomposition,
        and saves execution plan, tasks, and task dependencies.
        """
        profile = self.user_repository.get_profile(user_id)
        if not profile:
            raise ValueError("Profile not found.")
            
        profile_data = {
            "role": profile.role,
            "work_style": profile.work_style,
            "weekly_hours_available": float(profile.weekly_hours_available),
            "biggest_challenge": profile.biggest_challenge
        }

        goal = self.goal_repository.get_by_id(goal_id, user_id)
        ctx = self.goal_repository.get_context(goal_id)
        goal_context_dict = {
            "goal": goal.title,
            "category": ctx.category if ctx else None,
            "difficulty": ctx.difficulty if ctx else None
        }

        selected_strat = self.strategy_repository.get_selected(goal_id)
        strat_dict = {
            "strategy_key": selected_strat.strategy_key,
            "title": selected_strat.title,
            "description": selected_strat.description
        }

        readiness = self.strategy_repository.get_readiness_analysis(goal_id)
        readiness_results = {
            "overall_readiness_score": readiness.overall_readiness_score if readiness else 100,
            "dimension_scores": readiness.dimension_scores if readiness else {},
            "identified_gaps": readiness.identified_gaps if readiness else [],
            "remediation_steps": readiness.remediation_steps if readiness else []
        }

        # 1. Generate Execution Blueprint Phases
        blueprint_prompt = get_execution_blueprint_prompt(
            profile_data, goal_context_dict, strat_dict, readiness_results, refinement_choice
        )
        raw_blueprint = self.provider.generate(prompt=blueprint_prompt, json_mode=True)
        blueprint = json.loads(raw_blueprint)

        blueprint_data = {
            "blueprint_refinement": refinement_choice,
            "phases": blueprint.get("phases", []),
            "total_phases": len(blueprint.get("phases", []))
        }

        # 2. Decompose into Specific Tasks & Dependencies (DAG)
        task_prompt = get_task_breakdown_prompt(
            profile_data, goal_context_dict, strat_dict, readiness_results, blueprint_data, depth
        )
        raw_tasks = self.provider.generate(prompt=task_prompt, json_mode=True)
        task_res = json.loads(raw_tasks)

        raw_phases = task_res.get("tasks_by_phase", [])
        tasks_list = []
        dependencies = []

        for phase in raw_phases:
            p_num = phase.get("phase_number", 1)
            p_name = phase.get("phase_name", "Phase")
            for t in phase.get("tasks", []):
                task_item = {
                    "phase_number": p_num,
                    "phase_name": p_name,
                    "task_id_alias": t.get("task_id"),
                    "name": t.get("name"),
                    "title": t.get("name"),
                    "description": t.get("description", ""),
                    "allocated_hours": float(t.get("estimated_hours", 1.0))
                }
                tasks_list.append(task_item)
                
                for dep_id in t.get("dependencies", []):
                    dependencies.append({
                        "task_id_alias": t.get("task_id"),
                        "depends_on_alias": dep_id
                    })

        # Save ExecutionPlan, Tasks, and Dependencies to Database
        self.goal_repository.save_execution_plan_and_tasks(
            goal_id=goal_id,
            refinement_choice=refinement_choice,
            total_phases=blueprint_data["total_phases"],
            tasks_list=tasks_list,
            dependencies=dependencies,
            roadmap_json=task_res
        )

        self.goal_repository.update_status(goal_id, "planning", user_id)
        
        # Log event tracking
        self.goal_repository.log_goal_event(
            goal_id=goal_id,
            event_type="blueprint_and_tasks_generated",
            payload={"blueprint": blueprint_data, "tasks_count": len(tasks_list)}
        )

        return {
            "execution_plan": blueprint_data,
            "tasks": tasks_list,
            "dependencies": dependencies
        }
