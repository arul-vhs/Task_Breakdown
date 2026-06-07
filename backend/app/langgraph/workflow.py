import uuid
import datetime
from typing import Dict, Any, List
from langgraph.graph import StateGraph, END
from langgraph.checkpoint.base import BaseCheckpointSaver
from app.langgraph.state import GoalState
from app.services.ai_orchestrator import ai_orchestrator
from app.services.scheduler_engine import scheduler_engine
from app.services.progress_engine import progress_engine
from app.repositories import goal_repo, user_repo
from app.models.models import Task
from sqlalchemy import and_
from sqlalchemy.orm import Session
from langchain_core.runnables import RunnableConfig

# ==========================================
# 1. Workflow Node Implementations
# ==========================================

def goal_discovery_node(state: GoalState, config: RunnableConfig) -> Dict[str, Any]:
    """
    Goal Discovery Node: Performs initial classification, difficulty, and risk discovery.
    """
    db: Session = config["configurable"]["db"]
    user_id = uuid.UUID(state["user_id"])
    goal_id = uuid.UUID(state["goal_id"])
    
    # Load profile
    profile_db = user_repo.get_profile(db, user_id)
    profile_data = {
        "role": profile_db.role,
        "work_style": profile_db.work_style,
        "hours_per_week": float(profile_db.weekly_hours_available),
        "biggest_challenge": profile_db.biggest_challenge
    }
    
    # Query Gemini for goal intelligence analysis
    analysis = ai_orchestrator.analyze_goal(state["goal_title"], profile_data)
    questions = analysis.get("dynamic_questions", [])
    qa_context = [{"question": q, "answer": ""} for q in questions]
    
    # Save goal context to DB
    goal_repo.save_goal_context(
        db=db,
        goal_id=goal_id,
        category=analysis.get("category", "General"),
        difficulty=analysis.get("difficulty", "Intermediate"),
        estimated_duration=analysis.get("estimated_duration", "Flexible"),
        required_skills=analysis.get("required_skills", []),
        risks=analysis.get("risks", []),
        qa_context=qa_context
    )
    
    goal_repo.update_goal_status(db, goal_id, "drafting", user_id)
    
    return {
        "profile": profile_data,
        "goal_context": {
            "category": analysis.get("category"),
            "difficulty": analysis.get("difficulty"),
            "estimated_duration": analysis.get("estimated_duration"),
            "required_skills": analysis.get("required_skills", []),
            "risks": analysis.get("risks", []),
            "dynamic_questions": questions
        }
    }

def goal_intel_node(state: GoalState, config: RunnableConfig) -> Dict[str, Any]:
    """
    Goal Intelligence Node: Keeps track of context ingestion.
    """
    # Simply passes context answers through or refreshes
    return {}

def strategy_node(state: GoalState, config: RunnableConfig) -> Dict[str, Any]:
    """
    Strategy Node: Generates 3 execution strategies and personal recommendation.
    """
    db: Session = config["configurable"]["db"]
    user_id = uuid.UUID(state["user_id"])
    goal_id = uuid.UUID(state["goal_id"])
    
    # Load context
    ctx_db = db.query(goal_repo.GoalContext).filter(goal_repo.GoalContext.goal_id == goal_id).first()
    goal_context_dict = {
        "goal": state["goal_title"],
        "category": ctx_db.category,
        "difficulty": ctx_db.difficulty,
        "estimated_duration": ctx_db.estimated_duration,
        "required_skills": ctx_db.required_skills,
        "risks": ctx_db.risks,
        "qa_context": ctx_db.qa_context
    }
    
    # Generate strategies using Gemini
    strat_res = ai_orchestrator.generate_strategies(goal_context_dict, state["profile"])
    
    strategies_list = strat_res.get("strategies", [])
    recommended_key = strat_res.get("recommended_strategy_key")
    
    # Tag recommended key
    for s in strategies_list:
        strategy_key = s.get("strategy_key") or s.get("key")
        s["strategy_key"] = strategy_key
        s["is_recommended"] = (strategy_key == recommended_key)
        
    # Save strategies in DB
    goal_repo.save_strategies(db, goal_id, strategies_list)
    goal_repo.update_goal_status(db, goal_id, "strat_selection", user_id)
    
    return {
        "strategies": strategies_list
    }

def readiness_node(state: GoalState, config: RunnableConfig) -> Dict[str, Any]:
    """
    Readiness Node: Evaluates user gaps and readiness based on validation questionnaires.
    """
    db: Session = config["configurable"]["db"]
    user_id = uuid.UUID(state["user_id"])
    goal_id = uuid.UUID(state["goal_id"])
    
    selected_strat = goal_repo.get_selected_strategy(db, goal_id)
    strat_dict = {
        "strategy_key": selected_strat.strategy_key,
        "title": selected_strat.title,
        "description": selected_strat.description
    }
    
    ctx_db = db.query(goal_repo.GoalContext).filter(goal_repo.GoalContext.goal_id == goal_id).first()
    goal_context_dict = {
        "goal": state["goal_title"],
        "category": ctx_db.category,
        "difficulty": ctx_db.difficulty,
        "qa_context": ctx_db.qa_context
    }
    
    # Evaluate readiness with Gemini
    # Note: validation qas are generated and answered by user
    # For node execution, read user's strategy_validation context
    validation_qas = state.get("readiness", {}).get("qa_list", [])
    
    readiness_res = ai_orchestrator.evaluate_readiness(
        profile=state["profile"],
        goal_context=goal_context_dict,
        selected_strategy=strat_dict,
        qa_list=validation_qas
    )
    
    score = readiness_res.get("overall_readiness_score", 80)
    dim_scores = readiness_res.get("dimension_scores", {"skills": 80, "resources": 80, "time": 80})
    gaps = readiness_res.get("identified_gaps", [])
    steps = readiness_res.get("remediation_steps", [])
    
    # Save readiness analysis
    goal_repo.save_readiness_analysis(db, goal_id, score, dim_scores, gaps, steps)
    goal_repo.update_goal_status(db, goal_id, "readiness_check", user_id)
    
    return {
        "readiness": {
            "overall_readiness_score": score,
            "dimension_scores": dim_scores,
            "identified_gaps": gaps,
            "remediation_steps": steps
        }
    }

def planning_node(state: GoalState, config: RunnableConfig) -> Dict[str, Any]:
    """
    Planning Node: Formulates execution blueprint phases.
    """
    db: Session = config["configurable"]["db"]
    goal_id = uuid.UUID(state["goal_id"])
    
    selected_strat = goal_repo.get_selected_strategy(db, goal_id)
    strat_dict = {
        "strategy_key": selected_strat.strategy_key,
        "title": selected_strat.title,
        "description": selected_strat.description
    }
    
    ctx_db = db.query(goal_repo.GoalContext).filter(goal_repo.GoalContext.goal_id == goal_id).first()
    goal_context_dict = {
        "goal": state["goal_title"],
        "category": ctx_db.category,
        "difficulty": ctx_db.difficulty
    }
    
    refinement = state.get("execution_plan", {}).get("blueprint_refinement", "Standard")
    readiness_results = state.get("readiness", {})
    
    # Generate execution blueprint phases via Gemini
    blueprint = ai_orchestrator.generate_blueprint(
        profile=state["profile"],
        goal_context=goal_context_dict,
        selected_strategy=strat_dict,
        readiness_results=readiness_results,
        refinement_choice=refinement
    )
    
    return {
        "execution_plan": {
            "blueprint_refinement": refinement,
            "phases": blueprint.get("phases", []),
            "total_phases": len(blueprint.get("phases", []))
        }
    }

def task_generation_node(state: GoalState, config: RunnableConfig) -> Dict[str, Any]:
    """
    Task Generation Node: Generates specific tasks checklist and sequencing dependencies (DAG).
    """
    db: Session = config["configurable"]["db"]
    user_id = uuid.UUID(state["user_id"])
    goal_id = uuid.UUID(state["goal_id"])
    
    selected_strat = goal_repo.get_selected_strategy(db, goal_id)
    strat_dict = {
        "strategy_key": selected_strat.strategy_key,
        "title": selected_strat.title,
        "description": selected_strat.description
    }
    
    ctx_db = db.query(goal_repo.GoalContext).filter(goal_repo.GoalContext.goal_id == goal_id).first()
    goal_context_dict = {
        "goal": state["goal_title"],
        "category": ctx_db.category,
        "difficulty": ctx_db.difficulty
    }
    
    readiness_results = state.get("readiness", {})
    blueprint = state["execution_plan"]
    
    # Generate tasks and dependencies using Gemini
    task_res = ai_orchestrator.generate_task_breakdown(
        profile=state["profile"],
        goal_context=goal_context_dict,
        selected_strategy=strat_dict,
        readiness_results=readiness_results,
        blueprint=blueprint,
        depth="Detailed"
    )
    
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
                "description": t.get("description", ""),
                "allocated_hours": float(t.get("estimated_hours", 1.0))
            }
            tasks_list.append(task_item)
            
            for dep_id in t.get("dependencies", []):
                dependencies.append({
                    "task_id_alias": t.get("task_id"),
                    "depends_on_alias": dep_id
                })
    
    # Save plan, tasks, and dependencies to DB
    goal_repo.save_execution_plan_and_tasks(
        db=db,
        goal_id=goal_id,
        refinement_choice=blueprint["blueprint_refinement"],
        total_phases=blueprint["total_phases"],
        tasks_list=tasks_list,
        dependencies=dependencies
    )
    
    goal_repo.update_goal_status(db, goal_id, "planning", user_id)
    
    return {
        "tasks": tasks_list,
        "dependencies": dependencies
    }

def scheduling_node(state: GoalState, config: RunnableConfig) -> Dict[str, Any]:
    """
    Scheduling Node: Computes deterministic calendar schedules locally (Python-only capacity mapping).
    """
    db: Session = config["configurable"]["db"]
    user_id = uuid.UUID(state["user_id"])
    goal_id = uuid.UUID(state["goal_id"])
    
    # Perform deterministic local schedule calculation
    sched_res = scheduler_engine.calculate_schedule(
        tasks=state["tasks"],
        dependencies=state["dependencies"],
        profile=state["profile"]
    )
    
    analysis = sched_res["schedule_analysis"]
    
    # Save active schedule to DB
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
    
    # Create Schedule Version 1
    goal_repo.create_schedule_version(
        db=db,
        goal_id=goal_id,
        version=1,
        name="Original Schedule",
        weekly=sched_res["weekly_schedule"],
        daily=sched_res["daily_schedule"]
    )
    
    # Recalculate tasks due dates based on daily calendar
    task_due_dates = {}
    for day in sched_res["daily_schedule"]:
        w_num = day["week_number"]
        # Calculate date (starts today, offset by week number)
        target_date = datetime.date.today() + datetime.timedelta(weeks=int(w_num)-1)
        for block in day["time_blocks"]:
            t_alias = block["task_id"]
            task_due_dates[t_alias] = target_date
            
    # Apply to db
    for t_alias, due in task_due_dates.items():
        db_task = db.query(Task).filter(and_(Task.goal_id == goal_id, Task.task_id_alias == t_alias)).first()
        if db_task:
            db_task.due_date = due
            
    db.commit()
    goal_repo.update_goal_status(db, goal_id, "active", user_id)
    
    return {
        "active_schedule": sched_res
    }

def execution_node(state: GoalState, config: RunnableConfig) -> Dict[str, Any]:
    """
    Execution Node: Tracks task metrics and computes streaks locally in Python.
    """
    db: Session = config["configurable"]["db"]
    user_id = state["user_id"]
    goal_id = state["goal_id"]
    
    metrics = progress_engine.calculate_goal_metrics(db, goal_id, user_id)
    return {
        "progress": metrics
    }

def coaching_node(state: GoalState, config: RunnableConfig) -> Dict[str, Any]:
    """
    Coaching Node: Generates daily guidance and identifies scheduling risk factors.
    """
    db: Session = config["configurable"]["db"]
    goal_id = uuid.UUID(state["goal_id"])
    
    selected_strat = goal_repo.get_selected_strategy(db, goal_id)
    strat_dict = {
        "strategy_key": selected_strat.strategy_key,
        "title": selected_strat.title,
        "description": selected_strat.description
    }
    
    ctx_db = db.query(goal_repo.GoalContext).filter(goal_repo.GoalContext.goal_id == goal_id).first()
    goal_context_dict = {
        "goal": state["goal_title"],
        "category": ctx_db.category,
        "difficulty": ctx_db.difficulty
    }
    
    readiness = state.get("readiness", {})
    roadmap = {"phases": state.get("execution_plan", {}).get("phases", [])}
    schedule = state["active_schedule"]
    progress = state["progress"]
    reflections = state.get("reflections", [])
    
    # Request coaching brief via Gemini
    coach_res = ai_orchestrator.generate_coaching_insights(
        profile=state["profile"],
        goal_context=goal_context_dict,
        selected_strategy=strat_dict,
        readiness_results=readiness,
        roadmap_dag_data=roadmap,
        schedule_data=schedule,
        progress_metrics=progress,
        weekly_reflections=reflections
    )
    
    # Save Coach Insights to DB
    goal_repo.save_coach_insights(
        db=db,
        goal_id=goal_id,
        risk_level=coach_res.get("risk_level", "Low"),
        critical_risks=coach_res.get("critical_risks", []),
        action_items=coach_res.get("action_items", []),
        coaching_summary=coach_res.get("coaching_summary", "Guidance complete.")
    )
    
    return {
        "coach_insights": coach_res
    }

def adaptive_replanning_node(state: GoalState, config: RunnableConfig) -> Dict[str, Any]:
    """
    Adaptive Replanning Node: Re-calculates and forecasts goal recovery schedules.
    """
    # Pauses for Checkpoint 3 (User approves replan schedule)
    return {}


# ==========================================
# 2. StateGraph Mapping & Compilation
# ==========================================

def create_workflow() -> StateGraph:
    workflow = StateGraph(GoalState)
    
    # Add Nodes
    workflow.add_node("goal_discovery", goal_discovery_node)
    workflow.add_node("goal_intel", goal_intel_node)
    workflow.add_node("strategy", strategy_node)
    workflow.add_node("readiness", readiness_node)
    workflow.add_node("planning", planning_node)
    workflow.add_node("task_generation", task_generation_node)
    workflow.add_node("scheduling", scheduling_node)
    workflow.add_node("execution", execution_node)
    workflow.add_node("coaching", coaching_node)
    workflow.add_node("adaptive_replanning", adaptive_replanning_node)
    
    # Set Entry Point
    workflow.set_entry_point("goal_discovery")
    
    # Define Core Transitions
    workflow.add_edge("goal_discovery", "goal_intel")
    workflow.add_edge("goal_intel", "strategy")
    
    # Interrupt before readiness for Checkpoint 1 (Strategy selection)
    workflow.add_edge("strategy", "readiness")
    
    workflow.add_edge("readiness", "planning")
    workflow.add_edge("planning", "task_generation")
    
    # Interrupt before scheduling for Checkpoint 2 (Plan approval)
    workflow.add_edge("task_generation", "scheduling")
    
    workflow.add_edge("scheduling", "execution")
    workflow.add_edge("execution", "coaching")
    workflow.add_edge("coaching", "adaptive_replanning")
    workflow.add_edge("adaptive_replanning", END)
    
    return workflow

# Compile workflow graph
# Note: In production, configure with checking adapters
workflow_app = create_workflow().compile()
