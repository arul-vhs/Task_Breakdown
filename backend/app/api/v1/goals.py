from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
from app.database.session import get_db
from app.repositories import goal_repo
from app.models.models import User, Goal, Task, Strategy
from app.api.deps import get_current_user
from app.langgraph.workflow import (
    goal_discovery_node,
    strategy_node,
    readiness_node,
    planning_node,
    task_generation_node,
    scheduling_node,
    execution_node,
    coaching_node
)
from app.services.progress_engine import progress_engine
from app.services.ai_orchestrator import ai_orchestrator
import uuid
import datetime

router = APIRouter()

# ==========================================
# Schema Definitions
# ==========================================
class GoalCreate(BaseModel):
    title: str = Field(..., max_length=500)

class GoalResponse(BaseModel):
    id: uuid.UUID
    title: str
    status: str
    created_at: datetime.datetime

    class Config:
        from_attributes = True

class GoalDetailsResponse(GoalResponse):
    category: Optional[str] = None
    difficulty: Optional[str] = None
    estimated_duration: Optional[str] = None
    required_skills: List[str] = []
    risks: List[str] = []
    qa_context: List[Dict[str, Any]] = []

class AnswerInput(BaseModel):
    question: str
    answer: str

class IngestionAnswers(BaseModel):
    answers: List[AnswerInput]

class StrategySelect(BaseModel):
    strategy_key: str

class BlueprintApproval(BaseModel):
    approved: bool
    refinement_choice: str = "Standard" # Minimalist, Standard, Comprehensive

class TaskToggleInput(BaseModel):
    is_completed: bool
    time_spent: float = 0.0

class ChatInput(BaseModel):
    message: str

class ReplanInput(BaseModel):
    replanning_mode: str = "Balanced" # Balanced, Catch Up, Low Stress, Aggressive
    new_hours_per_week: float

# ==========================================
# Goal Lifecycle Endpoints
# ==========================================

@router.get("/", response_model=List[GoalResponse])
def read_goals(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Retrieves all goals owned by the authenticated user.
    """
    return goal_repo.get_goals(db, current_user.id)

@router.post("/", response_model=Dict[str, Any], status_code=status.HTTP_201_CREATED)
def start_goal_lifecycle(
    data: GoalCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Initializes a new Goal. Triggers the LangGraph Goal Discovery Node to analyze 
    the target goal and generate dynamic context-gathering questions.
    """
    # 1. Create Draft Goal
    goal = goal_repo.create_goal(db, data.title, current_user.id)
    
    # 2. Invoke LangGraph Goal Discovery node
    # Build state
    state = {
        "user_id": str(current_user.id),
        "goal_id": str(goal.id),
        "goal_title": goal.title,
        "profile": {},
        "goal_context": None,
        "strategies": [],
        "selected_strategy_key": None,
        "readiness": None,
        "execution_plan": None,
        "tasks": [],
        "dependencies": [],
        "active_schedule": None,
        "progress": {},
        "reflections": [],
        "coach_insights": None,
        "replanning_history": [],
        "replanned_preview": None
    }
    
    # Run discovery node
    # Passes db context in custom config parameter
    config = {"configurable": {"db": db}}
    node_out = goal_discovery_node(state, config)
    
    return {
        "goal_id": str(goal.id),
        "status": "drafting",
        "category": node_out["goal_context"]["category"],
        "difficulty": node_out["goal_context"]["difficulty"],
        "estimated_duration": node_out["goal_context"]["estimated_duration"],
        "required_skills": node_out["goal_context"]["required_skills"],
        "risks": node_out["goal_context"]["risks"],
        "questions": node_out["goal_context"]["dynamic_questions"]
    }

@router.get("/{goal_id}", response_model=GoalDetailsResponse)
def read_goal_details(
    goal_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Retrieves detailed context metadata for a specific goal.
    """
    goal = goal_repo.get_goal(db, goal_id, current_user.id)
    if not goal:
        raise HTTPException(status_code=404, detail="Goal not found.")
        
    ctx = goal.goal_context
    return {
        "id": str(goal.id),
        "title": goal.title,
        "status": goal.status,
        "created_at": goal.created_at,
        "category": ctx.category if ctx else None,
        "difficulty": ctx.difficulty if ctx else None,
        "estimated_duration": ctx.estimated_duration if ctx else None,
        "required_skills": ctx.required_skills if ctx else [],
        "risks": ctx.risks if ctx else [],
        "qa_context": ctx.qa_context if ctx else []
    }

@router.post("/{goal_id}/answers")
def submit_answers(
    goal_id: uuid.UUID,
    data: IngestionAnswers,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Submits answers to context questions. Triggers the Strategy Generation Node.
    """
    goal = goal_repo.get_goal(db, goal_id, current_user.id)
    if not goal:
        raise HTTPException(status_code=404, detail="Goal not found.")
        
    ctx = goal.goal_context
    if not ctx:
        raise HTTPException(status_code=400, detail="Goal context not initialized.")
        
    # Format Q&A Context
    compiled_qa = []
    for item in data.answers:
        compiled_qa.append({
            "question": item.question,
            "answer": item.answer
        })
    ctx.qa_context = compiled_qa
    db.commit()
    
    # Run LangGraph Strategy Node
    state = {
        "user_id": str(current_user.id),
        "goal_id": str(goal.id),
        "goal_title": goal.title,
        "profile": {
            "role": current_user.profile.role,
            "work_style": current_user.profile.work_style,
            "weekly_hours_available": float(current_user.profile.weekly_hours_available),
            "biggest_challenge": current_user.profile.biggest_challenge
        },
        "goal_context": None,
        "strategies": [],
        "selected_strategy_key": None
    }
    
    config = {"configurable": {"db": db}}
    node_out = strategy_node(state, config)
    
    return {
        "status": "strat_selection",
        "strategies": node_out["strategies"]
    }

@router.get("/{goal_id}/strategies")
def get_goal_strategies(
    goal_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Retrieves the 3 generated strategy options.
    """
    goal = goal_repo.get_goal(db, goal_id, current_user.id)
    if not goal:
        raise HTTPException(status_code=404, detail="Goal not found.")
        
    strategies = goal.strategies
    return strategies

@router.post("/{goal_id}/select-strategy")
def select_goal_strategy(
    goal_id: uuid.UUID,
    data: StrategySelect,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Selects the strategy (Checkpoint 1). Triggers the Readiness Analysis Node, 
    Planning Node, and Task Generation Node.
    """
    goal = goal_repo.get_goal(db, goal_id, current_user.id)
    if not goal:
        raise HTTPException(status_code=404, detail="Goal not found.")
        
    # Mark selection
    selected_strat = goal_repo.select_strategy(db, goal_id, data.strategy_key)
    if not selected_strat:
        raise HTTPException(status_code=400, detail="Invalid strategy key selection.")
        
    # Setup state for readiness assessment
    profile_data = {
        "role": current_user.profile.role,
        "work_style": current_user.profile.work_style,
        "weekly_hours_available": float(current_user.profile.weekly_hours_available),
        "biggest_challenge": current_user.profile.biggest_challenge
    }
    
    # We will simulate the validation QAs for execution routing 
    # Or fetch if user answered validation questions in client
    # For now, evaluate baseline readiness
    state = {
        "user_id": str(current_user.id),
        "goal_id": str(goal.id),
        "goal_title": goal.title,
        "profile": profile_data,
        "readiness": {"qa_list": []},
        "execution_plan": {"blueprint_refinement": "Standard"},
        "tasks": [],
        "dependencies": []
    }
    
    config = {"configurable": {"db": db}}
    
    # 1. Run Readiness Evaluation
    readiness_out = readiness_node(state, config)
    state["readiness"] = readiness_out["readiness"]
    
    # 2. Run Planning node
    planning_out = planning_node(state, config)
    state["execution_plan"] = planning_out["execution_plan"]
    
    # 3. Run Task Generation
    task_out = task_generation_node(state, config)
    
    return {
        "status": "planning",
        "readiness": state["readiness"],
        "execution_plan": state["execution_plan"],
        "tasks": task_out["tasks"],
        "dependencies": task_out["dependencies"]
    }

@router.get("/{goal_id}/readiness")
def get_goal_readiness(
    goal_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Retrieves the readiness analysis results for a specific goal.
    """
    goal = goal_repo.get_goal(db, goal_id, current_user.id)
    if not goal:
        raise HTTPException(status_code=404, detail="Goal not found.")
    
    readiness = goal.readiness_analysis
    if not readiness:
        return {
            "overall_readiness_score": 100,
            "dimension_scores": {},
            "identified_gaps": [],
            "remediation_steps": []
        }
        
    return {
        "overall_readiness_score": readiness.overall_readiness_score,
        "dimension_scores": readiness.dimension_scores,
        "identified_gaps": readiness.identified_gaps,
        "remediation_steps": readiness.remediation_steps
    }

@router.post("/{goal_id}/approve-blueprint")
def approve_goal_blueprint(
    goal_id: uuid.UUID,
    data: BlueprintApproval,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    User approves the plan (Checkpoint 2). Triggers the Python-only Scheduling Node.
    """
    goal = goal_repo.get_goal(db, goal_id, current_user.id)
    if not goal:
        raise HTTPException(status_code=404, detail="Goal not found.")
        
    if not data.approved:
        # User rejects, let them generate a new plan (Planning engine re-routes)
        goal_repo.update_goal_status(db, goal_id, "readiness_check", current_user.id)
        return {"status": "readiness_check", "detail": "Re-run strategy adjustments."}
        
    # Load tasks and dependencies
    db_tasks = goal_repo.get_tasks(db, goal_id)
    tasks_list = [
        {
            "phase_number": t.phase_number,
            "phase_name": t.phase_name,
            "task_id_alias": t.task_id_alias,
            "name": t.name,
            "allocated_hours": float(t.allocated_hours)
        } for t in db_tasks
    ]
    
    db_deps = db.query(goal_repo.TaskDependency).filter(goal_repo.TaskDependency.goal_id == goal_id).all()
    deps_list = [{"task_id_alias": d.task_id_alias, "depends_on_alias": d.depends_on_alias} for d in db_deps]
    
    profile_data = {
        "role": current_user.profile.role,
        "work_style": current_user.profile.work_style,
        "weekly_hours_available": float(current_user.profile.weekly_hours_available),
        "biggest_challenge": current_user.profile.biggest_challenge
    }
    
    # Run deterministic scheduling service
    state = {
        "user_id": str(current_user.id),
        "goal_id": str(goal.id),
        "goal_title": goal.title,
        "profile": profile_data,
        "tasks": tasks_list,
        "dependencies": deps_list,
        "active_schedule": None
    }
    
    config = {"configurable": {"db": db}}
    sched_out = scheduling_node(state, config)
    
    # Also trigger baseline Coaching Engine run
    state["active_schedule"] = sched_out["active_schedule"]
    state["progress"] = {
        "total_tasks_count": len(tasks_list),
        "completed_tasks_count": 0,
        "completion_percentage": 0.0,
        "health_score": 100,
        "overdue_tasks_count": 0,
        "streak_count": 0,
        "time_spent_total": 0.0,
        "allocated_hours_total": sum(t["allocated_hours"] for t in tasks_list)
    }
    coaching_node(state, config)
    
    return {
        "status": "active",
        "schedule": sched_out["active_schedule"]
    }

# ==========================================
# Execution Tracker Endpoints
# ==========================================

@router.get("/{goal_id}/tasks")
def read_goal_tasks(
    goal_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Gets the task board checklist for the goal.
    """
    goal = goal_repo.get_goal(db, goal_id, current_user.id)
    if not goal:
        raise HTTPException(status_code=404, detail="Goal not found.")
    return goal_repo.get_tasks(db, goal_id)

@router.get("/{goal_id}/dependencies")
def read_goal_dependencies(
    goal_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Retrieves task dependency links for a goal.
    """
    goal = goal_repo.get_goal(db, goal_id, current_user.id)
    if not goal:
        raise HTTPException(status_code=404, detail="Goal not found.")
    
    deps = db.query(goal_repo.TaskDependency).filter(goal_repo.TaskDependency.goal_id == goal_id).all()
    return [{"task_id_alias": d.task_id_alias, "depends_on_alias": d.depends_on_alias} for d in deps]

@router.post("/{goal_id}/tasks/{task_alias}/toggle")
def toggle_task(
    goal_id: uuid.UUID,
    task_alias: str,
    data: TaskToggleInput,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Toggles task execution check state, recalculates streak indices locally.
    """
    goal = goal_repo.get_goal(db, goal_id, current_user.id)
    if not goal:
        raise HTTPException(status_code=404, detail="Goal not found.")
        
    task = goal_repo.update_task_completion(
        db=db,
        goal_id=goal_id,
        task_id_alias=task_alias,
        is_completed=data.is_completed,
        time_spent=data.time_spent,
        user_id=current_user.id
    )
    
    # Recalculate metrics
    metrics = progress_engine.calculate_goal_metrics(db, goal_id, str(current_user.id))
    return {
        "task_id_alias": task_alias,
        "is_completed": task.is_completed,
        "time_spent": float(task.time_spent),
        "metrics": metrics
    }

@router.get("/{goal_id}/progress")
def read_progress_metrics(
    goal_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Returns telemetry aggregates.
    """
    goal = goal_repo.get_goal(db, goal_id, current_user.id)
    if not goal:
        raise HTTPException(status_code=404, detail="Goal not found.")
    return progress_engine.calculate_goal_metrics(db, goal_id, str(current_user.id))

# ==========================================
# AI Coach Center Endpoints
# ==========================================

@router.get("/{goal_id}/coaching")
def read_coaching_dashboard(
    goal_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Retrieves the coaching guidance briefs and risks indices.
    """
    goal = goal_repo.get_goal(db, goal_id, current_user.id)
    if not goal:
        raise HTTPException(status_code=404, detail="Goal not found.")
    return goal.coach_insight

@router.post("/{goal_id}/coaching/chat")
def chat_with_coach(
    goal_id: uuid.UUID,
    data: ChatInput,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Conversational feedback loop directly connected to Gemini.
    """
    goal = goal_repo.get_goal(db, goal_id, current_user.id)
    if not goal:
        raise HTTPException(status_code=404, detail="Goal not found.")
        
    profile_data = {
        "role": current_user.profile.role,
        "work_style": current_user.profile.work_style,
        "weekly_hours_available": float(current_user.profile.weekly_hours_available),
        "biggest_challenge": current_user.profile.biggest_challenge
    }
    
    ctx = goal.goal_context
    goal_context_dict = {"goal": goal.title, "category": ctx.category, "difficulty": ctx.difficulty}
    selected_strat = goal_repo.get_selected_strategy(db, goal_id)
    strat_dict = {"strategy_key": selected_strat.strategy_key, "title": selected_strat.title} if selected_strat else {}
    
    # Calculate progress metrics
    progress = progress_engine.calculate_goal_metrics(db, goal_id, str(current_user.id))
    
    # Format schedules
    sched = goal.schedule
    schedule_data = {"weekly_schedule": sched.weekly_schedule, "daily_schedule": sched.daily_schedule} if sched else {}
    
    reflections = [{"reflection": r.reflection, "quote": r.encouragement_quote} for r in goal.reflections]
    
    # Call Gemini Conversational agent
    chat_history = []  # Can load from state if desired, here run one-shot conversation
    chat_history.append({"role": "user", "content": data.message})
    
    reply = ai_orchestrator.chat_with_coach(
        profile=profile_data,
        goal_context=goal_context_dict,
        selected_strategy=strat_dict,
        readiness_results=goal.readiness_analysis.__dict__ if goal.readiness_analysis else {},
        roadmap_dag_data={"phases": goal.execution_plan.total_phases if goal.execution_plan else 0},
        schedule_data=schedule_data,
        progress_metrics=progress,
        weekly_reflections=reflections,
        chat_history=chat_history
    )
    
    return {"reply": reply}

# ==========================================
# Adaptive Replanning Endpoints
# ==========================================

@router.post("/{goal_id}/replan")
def preview_schedule_replan(
    goal_id: uuid.UUID,
    data: ReplanInput,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Triggers adaptive replanning preview. Returns forecast adjustments.
    """
    goal = goal_repo.get_goal(db, goal_id, current_user.id)
    if not goal:
        raise HTTPException(status_code=404, detail="Goal not found.")
        
    profile_data = {
        "role": current_user.profile.role,
        "work_style": current_user.profile.work_style,
        "weekly_hours_available": float(current_user.profile.weekly_hours_available),
        "biggest_challenge": current_user.profile.biggest_challenge
    }
    
    ctx = goal.goal_context
    goal_context_dict = {"goal": goal.title, "category": ctx.category, "difficulty": ctx.difficulty}
    selected_strat = goal_repo.get_selected_strategy(db, goal_id)
    strat_dict = {"strategy_key": selected_strat.strategy_key, "title": selected_strat.title} if selected_strat else {}
    
    progress = progress_engine.calculate_goal_metrics(db, goal_id, str(current_user.id))
    sched = goal.schedule
    schedule_data = {"weekly_schedule": sched.weekly_schedule, "daily_schedule": sched.daily_schedule} if sched else {}
    
    coach = goal.coach_insight
    coach_dict = {"risk_level": coach.risk_level, "coaching_summary": coach.coaching_summary} if coach else {}
    
    # Request replanning preview calculations from Gemini
    replanned_res = ai_orchestrator.generate_replanned_preview(
        profile=profile_data,
        goal_context=goal_context_dict,
        selected_strategy=strat_dict,
        readiness_results=goal.readiness_analysis.__dict__ if goal.readiness_analysis else {},
        roadmap_dag_data={"phases": goal.execution_plan.total_phases if goal.execution_plan else 0},
        schedule_data=schedule_data,
        progress_metrics=progress,
        coach_insights=coach_dict,
        new_hours_per_week=data.new_hours_per_week,
        replanning_mode=data.replanning_mode
    )
    
    # Temporary cache of preview in Redis or memory session is standard
    # For now, return preview mapping directly to user
    return {
        "replanning_mode": data.replanning_mode,
        "new_hours_per_week": data.new_hours_per_week,
        "roadmap_health_score": replanned_res.get("roadmap_health_score", 80),
        "completion_probability": replanned_res.get("completion_probability", 80),
        "goal_completion_forecast": replanned_res.get("goal_completion_forecast", "Adjusted timeline"),
        "risk_analysis": replanned_res.get("risk_analysis", ""),
        "recommended_adjustments": replanned_res.get("recommended_adjustments", []),
        "replanned_weekly_schedule": replanned_res.get("replanned_weekly_schedule", [])
    }

@router.post("/{goal_id}/apply-replan")
def apply_schedule_replan(
    goal_id: uuid.UUID,
    data: ReplanInput, # Resends target preview parameters to apply
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Applies the previewed reschedule (Checkpoint 3). Invokes scheduler service and bumps version.
    """
    goal = goal_repo.get_goal(db, goal_id, current_user.id)
    if not goal:
        raise HTTPException(status_code=404, detail="Goal not found.")
        
    # Update profile hour availability constraint
    current_user.profile.weekly_hours_available = data.new_hours_per_week
    
    # Reload tasks and recalculate deterministic schedule in Python using new hours limit
    db_tasks = goal_repo.get_tasks(db, goal_id)
    tasks_list = [
        {
            "phase_number": t.phase_number,
            "phase_name": t.phase_name,
            "task_id_alias": t.task_id_alias,
            "name": t.name,
            "allocated_hours": float(t.allocated_hours)
        } for t in db_tasks
    ]
    
    db_deps = db.query(goal_repo.TaskDependency).filter(goal_repo.TaskDependency.goal_id == goal_id).all()
    deps_list = [{"task_id_alias": d.task_id_alias, "depends_on_alias": d.depends_on_alias} for d in db_deps]
    
    profile_data = {
        "role": current_user.profile.role,
        "work_style": current_user.profile.work_style,
        "weekly_hours_available": float(data.new_hours_per_week),
        "biggest_challenge": current_user.profile.biggest_challenge
    }
    
    # Re-schedule in Python
    sched_res = scheduler_engine.calculate_schedule(tasks_list, deps_list, profile_data)
    analysis = sched_res["schedule_analysis"]
    
    # Update Active Schedule
    goal_repo.save_active_schedule(
        db=db,
        goal_id=goal_id,
        confidence=analysis["confidence_score"],
        forecast=analysis["goal_completion_forecast"],
        buffer_desc=analysis["buffer_time_allocation"],
        feasibility=analysis["deadline_feasibility_analysis"],
        weekly_schedule=sched_res["weekly_schedule"],
        daily_schedule=sched_res["daily_schedule"]
    )
    
    # Increment Version
    version_count = db.query(goal_repo.ScheduleVersion).filter(goal_repo.ScheduleVersion.goal_id == goal_id).count()
    new_ver = version_count + 1
    
    goal_repo.create_schedule_version(
        db=db,
        goal_id=goal_id,
        version=new_ver,
        name=f"{data.replanning_mode} Replan",
        weekly=sched_res["weekly_schedule"],
        daily=sched_res["daily_schedule"],
        reason=f"Rescheduled under mode {data.replanning_mode} with capacity {data.new_hours_per_week}h/week"
    )
    
    # Save Reflection entry
    goal_repo.save_reflection(
        db=db,
        goal_id=goal_id,
        reflection=f"Rescheduled goal timeline to version {new_ver}.",
        adjustments=[f"Set availability limit to {data.new_hours_per_week}h/week."],
        quote="Progress is adjustment. Stay focused."
    )
    
    # Log Replanning History
    goal_repo.save_replanning_history(
        db=db,
        goal_id=goal_id,
        mode=data.replanning_mode,
        hours=data.new_hours_per_week,
        risks=analysis["deadline_feasibility_analysis"],
        adjustments=[f"Adjusted weekly hours to {data.new_hours_per_week}"]
    )
    
    # Refresh Coaching Insights
    state = {
        "user_id": str(current_user.id),
        "goal_id": str(goal.id),
        "goal_title": goal.title,
        "profile": profile_data,
        "tasks": tasks_list,
        "dependencies": deps_list,
        "active_schedule": sched_res,
        "progress": progress_engine.calculate_goal_metrics(db, goal_id, str(current_user.id)),
        "reflections": [{"reflection": r.reflection} for r in goal.reflections]
    }
    coaching_node(state, {"configurable": {"db": db}})
    
    return {
        "status": "applied",
        "current_version": new_ver,
        "schedule": sched_res
    }

@router.get("/{goal_id}/schedule")
def read_goal_schedule(
    goal_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Retrieves the active weekly and daily calendar schedule for the goal.
    """
    goal = goal_repo.get_goal(db, goal_id, current_user.id)
    if not goal:
        raise HTTPException(status_code=404, detail="Goal not found.")
    
    sched = goal.schedule
    if not sched:
        return {"weekly_schedule": [], "daily_schedule": [], "schedule_analysis": {}}
        
    return {
        "weekly_schedule": sched.weekly_schedule,
        "daily_schedule": sched.daily_schedule,
        "schedule_analysis": {
            "confidence_score": sched.confidence_score,
            "goal_completion_forecast": sched.goal_completion_forecast,
            "buffer_time_allocation": sched.buffer_time_allocation,
            "deadline_feasibility_analysis": sched.feasibility_audit
        }
    }
