from sqlalchemy.orm import Session
from sqlalchemy import and_, func
from app.models.models import (
    Goal, GoalContext, Strategy, ReadinessAnalysis, ExecutionPlan,
    Task, TaskDependency, Schedule, ScheduleVersion, ProgressLog,
    Reflection, CoachInsight, ReplanningHistory
)
import uuid
import datetime

# 1. Goal CRUD
def get_goals(db: Session, user_id: uuid.UUID) -> list[Goal]:
    return db.query(Goal).filter(Goal.user_id == user_id).all()

def get_goal(db: Session, goal_id: uuid.UUID, user_id: uuid.UUID) -> Goal:
    return db.query(Goal).filter(and_(Goal.id == goal_id, Goal.user_id == user_id)).first()

def create_goal(db: Session, title: str, user_id: uuid.UUID) -> Goal:
    goal = Goal(user_id=user_id, title=title, status="drafting")
    db.add(goal)
    db.commit()
    db.refresh(goal)
    return goal

def update_goal_status(db: Session, goal_id: uuid.UUID, status: str, user_id: uuid.UUID) -> Goal:
    goal = get_goal(db, goal_id, user_id)
    if goal:
        goal.status = status
        db.commit()
        db.refresh(goal)
    return goal

# 2. Goal Context
def save_goal_context(
    db: Session,
    goal_id: uuid.UUID,
    category: str,
    difficulty: str,
    estimated_duration: str,
    required_skills: list,
    risks: list,
    qa_context: list
) -> GoalContext:
    ctx = db.query(GoalContext).filter(GoalContext.goal_id == goal_id).first()
    if ctx:
        ctx.category = category
        ctx.difficulty = difficulty
        ctx.estimated_duration = estimated_duration
        ctx.required_skills = required_skills
        ctx.risks = risks
        ctx.qa_context = qa_context
    else:
        ctx = GoalContext(
            goal_id=goal_id,
            category=category,
            difficulty=difficulty,
            estimated_duration=estimated_duration,
            required_skills=required_skills,
            risks=risks,
            qa_context=qa_context
        )
        db.add(ctx)
    db.commit()
    db.refresh(ctx)
    return ctx

# 3. Strategy
def save_strategies(db: Session, goal_id: uuid.UUID, strategies_list: list[dict]) -> list[Strategy]:
    # Delete old ones
    db.query(Strategy).filter(Strategy.goal_id == goal_id).delete()
    
    db_strategies = []
    for item in strategies_list:
        strat = Strategy(
            goal_id=goal_id,
            strategy_key=item["strategy_key"],
            title=item["title"],
            description=item["description"],
            pros=item.get("pros", []),
            cons=item.get("cons", []),
            is_recommended=item.get("is_recommended", False),
            is_selected=False
        )
        db.add(strat)
        db_strategies.append(strat)
    db.commit()
    return db_strategies

def select_strategy(db: Session, goal_id: uuid.UUID, strategy_key: str) -> Strategy:
    # Deselect all
    db.query(Strategy).filter(Strategy.goal_id == goal_id).update({Strategy.is_selected: False})
    
    # Select target
    target = db.query(Strategy).filter(and_(Strategy.goal_id == goal_id, Strategy.strategy_key == strategy_key)).first()
    if target:
        target.is_selected = True
        db.commit()
        db.refresh(target)
    return target

def get_selected_strategy(db: Session, goal_id: uuid.UUID) -> Strategy:
    return db.query(Strategy).filter(and_(Strategy.goal_id == goal_id, Strategy.is_selected == True)).first()

# 4. Readiness Analysis
def save_readiness_analysis(
    db: Session,
    goal_id: uuid.UUID,
    overall_score: int,
    dimension_scores: dict,
    identified_gaps: list,
    remediation_steps: list
) -> ReadinessAnalysis:
    analysis = db.query(ReadinessAnalysis).filter(ReadinessAnalysis.goal_id == goal_id).first()
    if analysis:
        analysis.overall_readiness_score = overall_score
        analysis.dimension_scores = dimension_scores
        analysis.identified_gaps = identified_gaps
        analysis.remediation_steps = remediation_steps
    else:
        analysis = ReadinessAnalysis(
            goal_id=goal_id,
            overall_readiness_score=overall_score,
            dimension_scores=dimension_scores,
            identified_gaps=identified_gaps,
            remediation_steps=remediation_steps
        )
        db.add(analysis)
    db.commit()
    db.refresh(analysis)
    return analysis

# 5. Execution Blueprint & Tasks mapping
def save_execution_plan_and_tasks(
    db: Session,
    goal_id: uuid.UUID,
    refinement_choice: str,
    total_phases: int,
    tasks_list: list[dict],
    dependencies: list[dict]
):
    # Update plan meta
    plan = db.query(ExecutionPlan).filter(ExecutionPlan.goal_id == goal_id).first()
    if plan:
        plan.blueprint_refinement = refinement_choice
        plan.total_phases = total_phases
    else:
        plan = ExecutionPlan(
            goal_id=goal_id,
            blueprint_refinement=refinement_choice,
            total_phases=total_phases
        )
        db.add(plan)
    
    # Cascade clean existing tasks & dependencies
    db.query(TaskDependency).filter(TaskDependency.goal_id == goal_id).delete()
    db.query(Task).filter(Task.goal_id == goal_id).delete()
    
    # Save Tasks
    db_tasks = {}
    for item in tasks_list:
        task = Task(
            goal_id=goal_id,
            phase_number=item["phase_number"],
            phase_name=item["phase_name"],
            task_id_alias=item["task_id_alias"],
            name=item["name"],
            description=item.get("description", ""),
            allocated_hours=item.get("allocated_hours", 1.0),
            is_completed=False,
            time_spent=0.0
        )
        db.add(task)
        db_tasks[task.task_id_alias] = task
        
    # Commit tasks to generate UUIDs if necessary or index mapping
    db.commit()
    
    # Save Dependencies
    for dep in dependencies:
        db_dep = TaskDependency(
            goal_id=goal_id,
            task_id_alias=dep["task_id_alias"],
            depends_on_alias=dep["depends_on_alias"]
        )
        db.add(db_dep)
        
    db.commit()
    return plan

def get_tasks(db: Session, goal_id: uuid.UUID) -> list[Task]:
    return db.query(Task).filter(Task.goal_id == goal_id).order_by(Task.phase_number, Task.task_id_alias).all()

def update_task_completion(
    db: Session,
    goal_id: uuid.UUID,
    task_id_alias: str,
    is_completed: bool,
    time_spent: float,
    user_id: uuid.UUID
) -> Task:
    task = db.query(Task).filter(and_(Task.goal_id == goal_id, Task.task_id_alias == task_id_alias)).first()
    if task:
        orig_completed = task.is_completed
        task.is_completed = is_completed
        task.updated_at = datetime.datetime.now()
        
        if is_completed:
            task.completed_at = datetime.datetime.now()
            action = "completed"
        else:
            task.completed_at = None
            action = "uncompleted"
            
        time_delta = time_spent - float(task.time_spent)
        task.time_spent = time_spent
        
        # Log progress changes
        progress_log = ProgressLog(
            user_id=user_id,
            goal_id=goal_id,
            task_id=task.id,
            action=action,
            time_delta=time_delta,
            logged_date=datetime.date.today()
        )
        db.add(progress_log)
        db.commit()
        db.refresh(task)
    return task

# 6. Schedules
def save_active_schedule(
    db: Session,
    goal_id: uuid.UUID,
    confidence: int,
    forecast: str,
    buffer_desc: str,
    feasibility: str,
    weekly_schedule: list,
    daily_schedule: list
) -> Schedule:
    sched = db.query(Schedule).filter(Schedule.goal_id == goal_id).first()
    if sched:
        sched.confidence_score = confidence
        sched.goal_completion_forecast = forecast
        sched.buffer_time_allocation = buffer_desc
        sched.feasibility_audit = feasibility
        sched.weekly_schedule = weekly_schedule
        sched.daily_schedule = daily_schedule
    else:
        sched = Schedule(
            goal_id=goal_id,
            confidence_score=confidence,
            goal_completion_forecast=forecast,
            buffer_time_allocation=buffer_desc,
            feasibility_audit=feasibility,
            weekly_schedule=weekly_schedule,
            daily_schedule=daily_schedule
        )
        db.add(sched)
    db.commit()
    db.refresh(sched)
    return sched

def get_active_schedule(db: Session, goal_id: uuid.UUID) -> Schedule:
    return db.query(Schedule).filter(Schedule.goal_id == goal_id).first()

def create_schedule_version(
    db: Session,
    goal_id: uuid.UUID,
    version: int,
    name: str,
    weekly: list,
    daily: list,
    reason: str = None
) -> ScheduleVersion:
    sv = ScheduleVersion(
        goal_id=goal_id,
        version_number=version,
        name=name,
        weekly_schedule=weekly,
        daily_schedule=daily,
        replan_reason=reason
    )
    db.add(sv)
    db.commit()
    db.refresh(sv)
    return sv

# 7. Progress Logs and Metrics
def get_streak_count(db: Session, user_id: uuid.UUID) -> int:
    logs = db.query(ProgressLog.logged_date).filter(
        and_(ProgressLog.user_id == user_id, ProgressLog.action == "completed")
    ).distinct().order_by(ProgressLog.logged_date.desc()).all()
    
    if not logs:
        return 0
        
    dates = [row[0] for row in logs]
    today = datetime.date.today()
    yesterday = today - datetime.timedelta(days=1)
    
    # Check if user did something today or yesterday to continue streak
    if dates[0] not in (today, yesterday):
        return 0
        
    streak = 1
    current_date = dates[0]
    for next_date in dates[1:]:
        if current_date - next_date == datetime.timedelta(days=1):
            streak += 1
            current_date = next_date
        else:
            break
    return streak

# 8. Reflections
def save_reflection(db: Session, goal_id: uuid.UUID, reflection: str, adjustments: list, quote: str = None) -> Reflection:
    ref = Reflection(goal_id=goal_id, reflection=reflection, suggested_adjustments=adjustments, encouragement_quote=quote)
    db.add(ref)
    db.commit()
    db.refresh(ref)
    return ref

def get_reflections(db: Session, goal_id: uuid.UUID) -> list[Reflection]:
    return db.query(Reflection).filter(Reflection.goal_id == goal_id).order_by(Reflection.created_at.desc()).all()

# 9. Coach Insights
def save_coach_insights(
    db: Session,
    goal_id: uuid.UUID,
    risk_level: str,
    critical_risks: list,
    action_items: list,
    coaching_summary: str
) -> CoachInsight:
    insight = db.query(CoachInsight).filter(CoachInsight.goal_id == goal_id).first()
    if insight:
        insight.risk_level = risk_level
        insight.critical_risks = critical_risks
        insight.action_items = action_items
        insight.coaching_summary = coaching_summary
    else:
        insight = CoachInsight(
            goal_id=goal_id,
            risk_level=risk_level,
            critical_risks=critical_risks,
            action_items=action_items,
            coaching_summary=coaching_summary
        )
        db.add(insight)
    db.commit()
    db.refresh(insight)
    return insight

def get_coach_insights(db: Session, goal_id: uuid.UUID) -> CoachInsight:
    return db.query(CoachInsight).filter(CoachInsight.goal_id == goal_id).first()

# 10. Replanning History
def save_replanning_history(
    db: Session,
    goal_id: uuid.UUID,
    mode: str,
    hours: float,
    risks: str,
    adjustments: list
) -> ReplanningHistory:
    rep = ReplanningHistory(
        goal_id=goal_id,
        replanning_mode=mode,
        new_hours_per_week=hours,
        risk_analysis=risks,
        recommended_adjustments=adjustments
    )
    db.add(rep)
    db.commit()
    db.refresh(rep)
    return rep
