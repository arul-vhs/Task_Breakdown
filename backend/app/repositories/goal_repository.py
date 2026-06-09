import uuid
from typing import List, Optional, Dict, Any
from sqlalchemy import and_
from sqlalchemy.orm import Session
from app.models.goal import Goal, GoalContext
from app.models.task import Task, TaskDependency, ExecutionPlan
from app.models.event_store import GoalEvent, TaskEvent

class GoalRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_user(self, user_id: uuid.UUID) -> List[Goal]:
        """Supports fetching multiple goals per user."""
        return self.db.query(Goal).filter(Goal.user_id == user_id).all()

    def get_by_id(self, goal_id: uuid.UUID, user_id: uuid.UUID) -> Optional[Goal]:
        return self.db.query(Goal).filter(and_(Goal.id == goal_id, Goal.user_id == user_id)).first()

    def create(self, title: str, user_id: uuid.UUID, description: Optional[str] = None) -> Goal:
        goal = Goal(user_id=user_id, title=title, description=description, status="draft")
        self.db.add(goal)
        self.db.commit()
        self.db.refresh(goal)
        return goal

    def update_status(self, goal_id: uuid.UUID, status: str, user_id: uuid.UUID) -> Optional[Goal]:
        goal = self.get_by_id(goal_id, user_id)
        if goal:
            goal.status = status
            self.db.commit()
            self.db.refresh(goal)
        return goal

    def save_context(
        self,
        goal_id: uuid.UUID,
        category: str,
        difficulty: str,
        estimated_duration: str,
        required_skills: List[str],
        risks: List[str],
        qa_context: List[Dict[str, Any]],
        context_json: Optional[Dict[str, Any]] = None
    ) -> GoalContext:
        ctx = self.db.query(GoalContext).filter(GoalContext.goal_id == goal_id).first()
        if ctx:
            ctx.category = category
            ctx.difficulty = difficulty
            ctx.estimated_duration = estimated_duration
            ctx.required_skills = required_skills
            ctx.risks = risks
            ctx.qa_context = qa_context
            if context_json is not None:
                ctx.context_json = context_json
        else:
            ctx = GoalContext(
                goal_id=goal_id,
                category=category,
                difficulty=difficulty,
                estimated_duration=estimated_duration,
                required_skills=required_skills,
                risks=risks,
                qa_context=qa_context,
                context_json=context_json
            )
            self.db.add(ctx)
        self.db.commit()
        self.db.refresh(ctx)
        return ctx

    def get_context(self, goal_id: uuid.UUID) -> Optional[GoalContext]:
        return self.db.query(GoalContext).filter(GoalContext.goal_id == goal_id).first()

    def save_execution_plan_and_tasks(
        self,
        goal_id: uuid.UUID,
        refinement_choice: str,
        total_phases: int,
        tasks_list: List[Dict[str, Any]],
        dependencies: List[Dict[str, Any]],
        roadmap_json: Optional[Dict[str, Any]] = None
    ) -> ExecutionPlan:
        # Update plan metadata
        plan = self.db.query(ExecutionPlan).filter(ExecutionPlan.goal_id == goal_id).first()
        if plan:
            plan.blueprint_refinement = refinement_choice
            plan.total_phases = total_phases
            if roadmap_json is not None:
                plan.roadmap_json = roadmap_json
        else:
            plan = ExecutionPlan(
                goal_id=goal_id,
                blueprint_refinement=refinement_choice,
                total_phases=total_phases,
                roadmap_json=roadmap_json
            )
            self.db.add(plan)
        
        # Cascading deletion of existing tasks and dependency definitions
        self.db.query(TaskDependency).filter(TaskDependency.goal_id == goal_id).delete()
        self.db.query(Task).filter(Task.goal_id == goal_id).delete()
        
        # Save Tasks
        for item in tasks_list:
            task = Task(
                goal_id=goal_id,
                phase_number=item["phase_number"],
                phase_name=item["phase_name"],
                task_id_alias=item["task_id_alias"],
                name=item["name"],
                title=item.get("title", item["name"]),
                description=item.get("description", ""),
                allocated_hours=item.get("allocated_hours", 1.0),
                estimated_hours=item.get("estimated_hours", item.get("allocated_hours", 1.0)),
                is_completed=False,
                status="pending",
                time_spent=0.0
            )
            self.db.add(task)
            
        self.db.commit()
        
        # Save Dependencies
        for dep in dependencies:
            db_dep = TaskDependency(
                goal_id=goal_id,
                task_id_alias=dep["task_id_alias"],
                depends_on_alias=dep["depends_on_alias"]
            )
            self.db.add(db_dep)
            
        self.db.commit()
        return plan

    def get_tasks(self, goal_id: uuid.UUID) -> List[Task]:
        return self.db.query(Task).filter(Task.goal_id == goal_id).order_by(Task.phase_number, Task.task_id_alias).all()

    def get_task_dependencies(self, goal_id: uuid.UUID) -> List[TaskDependency]:
        return self.db.query(TaskDependency).filter(TaskDependency.goal_id == goal_id).all()

    def log_goal_event(self, goal_id: uuid.UUID, event_type: str, payload: Dict[str, Any], version: int = 1) -> GoalEvent:
        event = GoalEvent(
            goal_id=goal_id,
            event_type=event_type,
            event_payload=payload,
            version=version
        )
        self.db.add(event)
        self.db.commit()
        self.db.refresh(event)
        return event

    def log_task_event(self, goal_id: uuid.UUID, task_id: Optional[uuid.UUID], event_type: str, payload: Dict[str, Any]) -> TaskEvent:
        event = TaskEvent(
            goal_id=goal_id,
            task_id=task_id,
            event_type=event_type,
            event_payload=payload
        )
        self.db.add(event)
        self.db.commit()
        self.db.refresh(event)
        return event
