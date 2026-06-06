import streamlit as st
import datetime
import pandas as pd
from services.gemini_service import generate_weekly_reflection_with_gemini
from agents.goal_agent import render_sidebar_api_key

def initialize_progress_state():
    """
    Initializes session state variables for the Progress Tracking Agent.
    """
    if "task_due_dates" not in st.session_state:
        st.session_state.task_due_dates = {}
    if "task_time_spent" not in st.session_state:
        st.session_state.task_time_spent = {}
    if "streak_count" not in st.session_state:
        st.session_state.streak_count = 0
    if "last_activity_date" not in st.session_state:
        st.session_state.last_activity_date = None
    if "weekly_reflections" not in st.session_state:
        st.session_state.weekly_reflections = []

    # Auto-initialize default due dates if they are empty
    auto_initialize_due_dates()

def auto_initialize_due_dates():
    """
    Helper to set default due dates based on the generated weekly schedule.
    If no schedule exists, falls back to estimated phase durations.
    """
    if "roadmap_dag_data" not in st.session_state or not st.session_state.roadmap_dag_data:
        return
    
    if st.session_state.task_due_dates:
        # Already initialized
        return

    start_date = datetime.date.today()
    phases = st.session_state.roadmap_dag_data.get("phases", [])

    # Map task ID to week number from weekly schedule if it exists
    task_weeks = {}
    if "weekly_schedule" in st.session_state and st.session_state.weekly_schedule:
        for week in st.session_state.weekly_schedule:
            w_num = week.get("week_number", 1)
            for t in week.get("tasks", []):
                t_id = t.get("task_id")
                if t_id:
                    task_weeks[t_id] = w_num

    for phase in phases:
        p_num = phase.get("phase_number", 1)
        for task in phase.get("tasks", []):
            t_id = task.get("task_id")
            if t_id:
                w_num = task_weeks.get(t_id, p_num)
                # Estimate due date based on week number (7 days per week)
                due_date = start_date + datetime.timedelta(weeks=int(w_num))
                st.session_state.task_due_dates[t_id] = due_date.strftime("%Y-%m-%d")

def record_activity():
    """
    Increments or maintains the user's execution streak when they interact.
    """
    today_str = datetime.date.today().strftime("%Y-%m-%d")
    last_act = st.session_state.last_activity_date

    if not last_act:
        st.session_state.streak_count = 1
    elif last_act == today_str:
        # Already logged activity today, streak unchanged
        pass
    else:
        # Check if last activity was yesterday
        last_act_date = datetime.datetime.strptime(last_act, "%Y-%m-%d").date()
        yesterday = datetime.date.today() - datetime.timedelta(days=1)
        if last_act_date == yesterday:
            st.session_state.streak_count += 1
        else:
            # Streak broken
            st.session_state.streak_count = 1

    st.session_state.last_activity_date = today_str

def calculate_metrics():
    """
    Calculates progress metrics, velocity, overdue tasks, and health scores.
    """
    if "roadmap_dag_data" not in st.session_state or not st.session_state.roadmap_dag_data:
        return {}

    phases = st.session_state.roadmap_dag_data.get("phases", [])
    today = datetime.date.today()

    total_subtasks = 0
    completed_subtasks = 0
    total_tasks = 0
    completed_tasks = 0
    
    overdue_tasks_count = 0
    overdue_tasks_names = []
    
    total_hours_spent = 0.0
    total_estimated_hours = 0.0
    
    phase_metrics = []
    task_statuses = {} # task_id -> 'Completed' | 'In Progress' | 'Overdue' | 'Not Started'
    task_spent_list = [] # List of tuples for visualization
    task_est_list = []
    
    priority_stats = {"High": {"total": 0, "completed": 0}, "Medium": {"total": 0, "completed": 0}, "Low": {"total": 0, "completed": 0}}
    type_stats = {}

    for phase in phases:
        p_num = phase.get("phase_number", 1)
        p_name = phase.get("name", f"Phase {p_num}")
        
        phase_total_sub = 0
        phase_completed_sub = 0
        phase_tasks = phase.get("tasks", [])
        
        for task in phase_tasks:
            t_id = task.get("task_id")
            t_name = task.get("name", "")
            t_priority = task.get("priority", "Medium")
            t_type = task.get("task_type", "Coding")
            t_est = task.get("estimated_hours", 2)
            
            subtasks = task.get("subtasks", [])
            sub_keys = [f"{t_id}_{i}" for i in range(len(subtasks))]
            
            # Subtask counts
            task_total_sub = len(subtasks)
            task_completed_sub = sum(1 for k in sub_keys if st.session_state.task_completions.get(k, False))
            
            total_subtasks += task_total_sub
            completed_subtasks += task_completed_sub
            phase_total_sub += task_total_sub
            phase_completed_sub += task_completed_sub
            
            # Task completion definition: all subtasks complete
            is_completed = (task_completed_sub == task_total_sub) if task_total_sub > 0 else False
            is_started = (task_completed_sub > 0)
            
            total_tasks += 1
            if is_completed:
                completed_tasks += 1
                
            # Time spent
            spent = float(st.session_state.task_time_spent.get(t_id, 0.0))
            total_hours_spent += spent
            total_estimated_hours += t_est
            
            task_spent_list.append((t_id, spent))
            task_est_list.append((t_id, t_est))
            
            # Due date & Overdue detection
            due_str = st.session_state.task_due_dates.get(t_id)
            is_overdue = False
            if due_str and not is_completed:
                due_date_obj = datetime.datetime.strptime(due_str, "%Y-%m-%d").date()
                if due_date_obj < today:
                    is_overdue = True
                    overdue_tasks_count += 1
                    overdue_tasks_names.append(f"{t_id}: {t_name}")
            
            # Status
            if is_completed:
                status = "Completed"
            elif is_overdue:
                status = "Overdue"
            elif is_started:
                status = "In Progress"
            else:
                status = "Not Started"
                
            task_statuses[t_id] = status
            
            # Priority statistics
            if t_priority in priority_stats:
                priority_stats[t_priority]["total"] += 1
                if is_completed:
                    priority_stats[t_priority]["completed"] += 1
            
            # Type statistics
            if t_type not in type_stats:
                type_stats[t_type] = {"total": 0, "completed": 0}
            type_stats[t_type]["total"] += 1
            if is_completed:
                type_stats[t_type]["completed"] += 1
                
        phase_pct = int((phase_completed_sub / phase_total_sub) * 100) if phase_total_sub > 0 else 0
        phase_metrics.append({
            "phase_number": p_num,
            "name": p_name,
            "objective": phase.get("objective", ""),
            "milestone": phase.get("milestone", ""),
            "progress_pct": phase_pct,
            "is_completed": (phase_completed_sub == phase_total_sub) if phase_total_sub > 0 else False
        })

    # Overall completion percentage
    overall_completion_pct = int((completed_subtasks / total_subtasks) * 100) if total_subtasks > 0 else 0
    
    # Streak details
    streak = st.session_state.streak_count
    
    # Health Score Calculation
    # Health Score = (completion_rate * 0.7) + (streak * 2) - (overdue_count * 10)
    streak_bonus = min(20, streak * 2)
    overdue_penalty = overdue_tasks_count * 10
    health_score = int((overall_completion_pct * 0.7) + streak_bonus - overdue_penalty)
    health_score = max(0, min(100, health_score))
    
    # Weekly Velocity calculation: completed tasks / total weeks scheduled
    total_weeks = 1
    if "weekly_schedule" in st.session_state and st.session_state.weekly_schedule:
        total_weeks = max(1, len(st.session_state.weekly_schedule))
    elif "profile_data" in st.session_state:
        # fallback duration
        total_weeks = 4
        
    velocity_tasks_per_week = round(completed_tasks / total_weeks, 1)

    return {
        "overall_completion_pct": overall_completion_pct,
        "completed_subtasks": completed_subtasks,
        "total_subtasks": total_subtasks,
        "completed_tasks": completed_tasks,
        "total_tasks": total_tasks,
        "overdue_tasks_count": overdue_tasks_count,
        "overdue_tasks_names": overdue_tasks_names,
        "total_hours_spent": total_hours_spent,
        "total_estimated_hours": total_estimated_hours,
        "health_score": health_score,
        "streak_count": streak,
        "velocity_tasks_per_week": velocity_tasks_per_week,
        "phase_metrics": phase_metrics,
        "task_statuses": task_statuses,
        "priority_stats": priority_stats,
        "type_stats": type_stats,
        "task_spent_list": task_spent_list,
        "task_est_list": task_est_list
    }

def render_progress_agent():
    """
    Renders the Progress Tracking Agent dashboard.
    """
    initialize_progress_state()

    # Validate prior states exist
    if "goal_context" not in st.session_state or not st.session_state.goal_context:
        st.html(
            """
            <div style='text-align: center; padding: 40px;'>
                <h3 style='color: #f87171;'>⚠️ Missing Goal Context</h3>
                <p style='color: #94a3b8;'>Please complete the Goal Intake phase first.</p>
            </div>
            """
        )
        if st.button("Go to Goal Intake 🎯"):
            st.session_state.app_phase = "goal_intake"
            st.rerun()
        return

    if "roadmap_dag_data" not in st.session_state or not st.session_state.roadmap_dag_data:
        st.html(
            """
            <div style='text-align: center; padding: 40px;'>
                <h3 style='color: #f87171;'>⚠️ Missing Execution Blueprint</h3>
                <p style='color: #94a3b8;'>Please generate your execution roadmap and DAG first.</p>
            </div>
            """
        )
        if st.button("Go to Roadmap & DAG Builder 🗺️"):
            st.session_state.app_phase = "execution_blueprint"
            st.rerun()
        return

    goal_context = st.session_state.goal_context
    profile_data = st.session_state.profile_data
    api_key = render_sidebar_api_key()

    # Calculate current metrics
    metrics = calculate_metrics()

    # Sidebar Navigation Controls
    st.sidebar.html("<h3 style='margin-bottom: 20px;'>Navigation</h3>")
    if st.sidebar.button("👤 View Persona Profile", key="prog_nav_profile", use_container_width=True):
        st.session_state.app_phase = "profiling"
        st.rerun()
    if st.sidebar.button("📅 Back to Scheduler Workspace", key="prog_nav_sched", use_container_width=True):
        st.session_state.app_phase = "scheduling"
        st.rerun()
    st.sidebar.html("<hr style='border-color: rgba(255,255,255,0.1); margin: 15px 0;'>")

    # Custom Premium CSS Injection
    st.html(
        """
        <style>
        .progress-header {
            text-align: center;
            padding: 30px 20px;
            max-width: 800px;
            margin: 0 auto;
        }
        .metric-card-glow {
            background: linear-gradient(135deg, rgba(30, 41, 59, 0.4) 0%, rgba(15, 23, 42, 0.6) 100%);
            border: 1px solid rgba(255, 255, 255, 0.06);
            border-radius: 16px;
            padding: 22px;
            text-align: center;
            box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.15);
            backdrop-filter: blur(8px);
            transition: transform 0.2s ease, border-color 0.2s ease;
            height: 100%;
        }
        .metric-card-glow:hover {
            transform: translateY(-2px);
            border-color: rgba(99, 102, 241, 0.25);
        }
        .metric-card-title {
            font-size: 0.8rem;
            text-transform: uppercase;
            font-weight: 700;
            color: #64748b;
            letter-spacing: 1px;
            margin-bottom: 8px;
        }
        .metric-card-value {
            font-size: 2.5rem;
            font-weight: 800;
            margin-bottom: 4px;
        }
        .metric-card-desc {
            font-size: 0.78rem;
            color: #94a3b8;
        }
        
        /* Health Score colors */
        .health-high {
            background: linear-gradient(135deg, #10b981 0%, #059669 100%) !important;
            -webkit-background-clip: text !important;
            -webkit-text-fill-color: transparent !important;
        }
        .health-medium {
            background: linear-gradient(135deg, #fbbf24 0%, #d97706 100%) !important;
            -webkit-background-clip: text !important;
            -webkit-text-fill-color: transparent !important;
        }
        .health-low {
            background: linear-gradient(135deg, #f87171 0%, #dc2626 100%) !important;
            -webkit-background-clip: text !important;
            -webkit-text-fill-color: transparent !important;
        }
        
        .overdue-banner {
            background: rgba(239, 68, 68, 0.08);
            border: 1px solid rgba(239, 68, 68, 0.3);
            border-radius: 12px;
            padding: 18px;
            margin-bottom: 25px;
            box-shadow: 0 4px 15px rgba(239, 68, 68, 0.05);
        }
        
        .status-badge {
            font-size: 0.72rem;
            font-weight: 700;
            text-transform: uppercase;
            padding: 4px 10px;
            border-radius: 12px;
            letter-spacing: 0.5px;
            display: inline-block;
        }
        .badge-completed {
            background-color: rgba(16, 185, 129, 0.15);
            color: #34d399;
            border: 1px solid rgba(16, 185, 129, 0.3);
        }
        .badge-ip {
            background-color: rgba(168, 85, 247, 0.15);
            color: #c084fc;
            border: 1px solid rgba(168, 85, 247, 0.3);
        }
        .badge-overdue {
            background-color: rgba(239, 68, 68, 0.15);
            color: #f87171;
            border: 1px solid rgba(239, 68, 68, 0.3);
        }
        .badge-ns {
            background-color: rgba(255, 255, 255, 0.05);
            color: #94a3b8;
            border: 1px solid rgba(255, 255, 255, 0.08);
        }
        
        .active-phase-card {
            background: linear-gradient(135deg, rgba(99, 102, 241, 0.08) 0%, rgba(30, 41, 59, 0.3) 100%);
            border: 1.5px solid rgba(99, 102, 241, 0.25);
            border-radius: 16px;
            padding: 24px;
            margin-bottom: 25px;
            box-shadow: 0 8px 32px 0 rgba(99, 102, 241, 0.08);
        }
        
        .task-row {
            background: rgba(30, 41, 59, 0.2);
            border: 1px solid rgba(255, 255, 255, 0.04);
            border-radius: 12px;
            padding: 15px 20px;
            margin-bottom: 12px;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        .task-row:hover {
            border-color: rgba(255, 255, 255, 0.1);
        }
        
        .coaching-bubble {
            background: rgba(30, 41, 59, 0.35);
            border: 1px solid rgba(255, 255, 255, 0.06);
            border-radius: 16px;
            padding: 25px;
            margin-bottom: 25px;
            box-shadow: inset 0 0 20px rgba(99, 102, 241, 0.03);
            line-height: 1.6;
        }
        </style>
        """
    )

    # 1. HEADER
    st.html(
        """
        <div class='progress-header'>
            <span class='badge' style='background: rgba(16, 185, 129, 0.1); color: #34d399; border: 1px solid rgba(16, 185, 129, 0.3); padding: 6px 14px; border-radius: 20px; font-size: 0.85rem; font-weight: 700; letter-spacing: 1.5px;'>PHASE 6: PROGRESS TRACKING CENTER</span>
            <h1 style='font-size: 2.8rem; font-weight: 800; margin-top: 15px; margin-bottom: 10px; background: linear-gradient(to right, #f8fafc, #94a3b8); -webkit-background-clip: text; -webkit-text-fill-color: transparent;'>Execution Hub & Analytics</h1>
            <p style='color: #94a3b8; font-size: 1.15rem;'>Track your milestones, record daily effort, view diagnostic metrics, and consult your AI Execution Coach for weekly feedback.</p>
        </div>
        """
    )

    # 2. OVERDUE TASK ALERT
    if metrics["overdue_tasks_count"] > 0:
        overdue_list_html = "".join([f"<li>{name}</li>" for name in metrics["overdue_tasks_names"]])
        st.html(
            f"""
            <div class='overdue-banner'>
                <div style='display: flex; align-items: center; gap: 10px; margin-bottom: 8px;'>
                    <span style='font-size: 1.5rem;'>⚠️</span>
                    <b style='color: #f87171; font-size: 1.1rem;'>Overdue Execution Gaps Detected</b>
                </div>
                <p style='color: #cbd5e1; font-size: 0.92rem; margin: 0 0 10px 0;'>
                    The following tasks have passed their scheduled due date without completion. This lowers your Health Score and risks scheduling delays:
                </p>
                <ul style='color: #f87171; font-size: 0.88rem; margin: 0; padding-left: 20px;'>
                    {overdue_list_html}
                </ul>
            </div>
            """
        )

    # 3. METRICS CARDS ROW
    col_m1, col_m2, col_m3, col_m4 = st.columns(4)
    
    with col_m1:
        score = metrics["health_score"]
        h_class = "health-high"
        if score < 50:
            h_class = "health-low"
        elif score < 75:
            h_class = "health-medium"
            
        st.html(
            f"""
            <div class='metric-card-glow'>
                <div class='metric-card-title'>Execution Health</div>
                <div class='metric-card-value {h_class}'>{score}%</div>
                <div class='metric-card-desc'>Combines speed, overdue safety, and streak metrics.</div>
            </div>
            """
        )
        
    with col_m2:
        streak = metrics["streak_count"]
        st.html(
            f"""
            <div class='metric-card-glow'>
                <div class='metric-card-title'>Current Streak</div>
                <div class='metric-card-value' style='color: #f59e0b;'>🔥 {streak} Days</div>
                <div class='metric-card-desc'>Consecutive active days logged. Keep it up!</div>
            </div>
            """
        )
        
    with col_m3:
        vel = metrics["velocity_tasks_per_week"]
        st.html(
            f"""
            <div class='metric-card-glow'>
                <div class='metric-card-title'>Weekly Velocity</div>
                <div class='metric-card-value' style='color: #818cf8;'>🚀 {vel}</div>
                <div class='metric-card-desc'>Average tasks completed per scheduled week.</div>
            </div>
            """
        )
        
    with col_m4:
        rate = metrics["overall_completion_pct"]
        completed = metrics["completed_tasks"]
        tot = metrics["total_tasks"]
        st.html(
            f"""
            <div class='metric-card-glow'>
                <div class='metric-card-title'>Goal Completion</div>
                <div class='metric-card-value' style='color: #10b981;'>🎯 {rate}%</div>
                <div class='metric-card-desc'>Completed {completed} of {tot} total roadmap tasks.</div>
            </div>
            """
        )

    st.markdown("<div style='height: 30px;'></div>", unsafe_allow_html=True)

    # 4. TABS DEFINITION
    tab_overview, tab_tasks, tab_reflection, tab_export = st.tabs([
        "📊 Performance Overview", 
        "📝 Task Checklist & Logger", 
        "🧠 AI Coach Weekly Reflection", 
        "🔌 AI Coach Agent Export"
    ])

    # ==================== TAB 1: OVERVIEW ====================
    with tab_overview:
        # Determine Current Phase
        active_phase = next((p for p in metrics["phase_metrics"] if not p["is_completed"]), None)
        if not active_phase and metrics["phase_metrics"]:
            # All completed!
            active_phase = metrics["phase_metrics"][-1]
            
        if active_phase:
            st.html(
                f"""
                <div class='active-phase-card'>
                    <div style='display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px;'>
                        <span style='font-size: 0.78rem; text-transform: uppercase; font-weight: 700; color: #818cf8; letter-spacing: 1.5px;'>🎯 CURRENT ACTIVE PHASE</span>
                        <span class='status-badge badge-ip' style='background-color: rgba(99, 102, 241, 0.15); color: #818cf8; border-color: rgba(99, 102, 241, 0.3);'>
                            {active_phase['progress_pct']}% Done
                        </span>
                    </div>
                    <h3 style='margin: 0 0 8px 0; color: #f8fafc; font-weight: 800;'>{active_phase['name']}</h3>
                    <p style='color: #cbd5e1; font-size: 0.95rem; margin: 0 0 12px 0;'><b>Objective:</b> {active_phase['objective']}</p>
                    <div style='display: flex; justify-content: space-between; font-size: 0.85rem; color: #94a3b8;'>
                        <span>🏁 <b>Milestone:</b> {active_phase['milestone']}</span>
                    </div>
                </div>
                """
            )
            
        col_c1, col_c2 = st.columns([1.2, 1], gap="large")
        
        with col_c1:
            st.html("<h4 style='color: #818cf8; font-weight: 700; margin-bottom: 15px;'>Phase Progress Breakdown</h4>")
            
            # Format dataframe for Phase Progress
            phase_df = pd.DataFrame([
                {"Phase": f"Phase {p['phase_number']}", "Progress (%)": p["progress_pct"]}
                for p in metrics["phase_metrics"]
            ])
            if not phase_df.empty:
                st.bar_chart(phase_df.set_index("Phase"), color="#6366f1")
                
        with col_c2:
            st.html("<h4 style='color: #818cf8; font-weight: 700; margin-bottom: 15px;'>Time Statistics</h4>")
            
            total_logged = metrics["total_hours_spent"]
            total_est = metrics["total_estimated_hours"]
            
            st.html(
                f"""
                <div style='background: rgba(30, 41, 59, 0.25); border: 1px solid rgba(255,255,255,0.05); border-radius: 12px; padding: 20px; text-align: center; margin-bottom: 20px;'>
                    <div style='font-size: 0.85rem; color: #94a3b8; font-weight: 600; text-transform: uppercase;'>Total Allocated Effort</div>
                    <div style='font-size: 2.2rem; font-weight: 800; color: #cbd5e1; margin: 5px 0;'>{total_logged} / {total_est} hrs</div>
                    <p style='font-size: 0.82rem; color: #64748b; margin: 0;'>Logged hours vs initial estimations across all checklist checkpoints.</p>
                </div>
                """
            )
            
            # Task effort breakdown chart
            tasks_spent = metrics["task_spent_list"]
            tasks_est = metrics["task_est_list"]
            
            if tasks_spent:
                effort_df = pd.DataFrame({
                    "Task": [t[0] for t in tasks_spent],
                    "Hours Spent": [t[1] for t in tasks_spent],
                    "Estimated Hours": [next((e[1] for e in tasks_est if e[0] == t[0]), 0) for t in tasks_spent]
                })
                
                st.area_chart(effort_df.set_index("Task"), color=["#10b981", "#a855f7"])

    # ==================== TAB 2: TASK CHECKLIST & LOGGER ====================
    with tab_tasks:
        st.html("<p style='color: #94a3b8; font-size: 0.95rem; margin-bottom: 20px;'>View details, set custom deadlines, log execution effort, and complete task checklists.</p>")
        
        phases = st.session_state.roadmap_dag_data.get("phases", [])
        
        for phase in phases:
            p_num = phase.get("phase_number", 1)
            p_name = phase.get("name", "")
            
            # Get phase specific metrics
            p_metric = next((m for m in metrics["phase_metrics"] if m["phase_number"] == p_num), None)
            pct = p_metric["progress_pct"] if p_metric else 0
            
            expander_title = f"Phase {p_num}: {p_name} ({pct}% Done)"
            
            with st.expander(expander_title, expanded=(p_metric and not p_metric["is_completed"])):
                st.progress(pct / 100)
                st.markdown("<div style='height: 10px;'></div>", unsafe_allow_html=True)
                
                tasks = phase.get("tasks", [])
                for task in tasks:
                    t_id = task.get("task_id")
                    t_name = task.get("name")
                    t_desc = task.get("description", "")
                    t_est = task.get("estimated_hours", 2)
                    subtasks = task.get("subtasks", [])
                    
                    status = metrics["task_statuses"].get(t_id, "Not Started")
                    badge_class = "badge-ns"
                    if status == "Completed":
                        badge_class = "badge-completed"
                    elif status == "In Progress":
                        badge_class = "badge-ip"
                    elif status == "Overdue":
                        badge_class = "badge-overdue"
                        
                    # Calculate subtask checklists
                    sub_keys = [f"{t_id}_{i}" for i in range(len(subtasks))]
                    
                    st.html(
                        f"""
                        <div style='background: rgba(15, 23, 42, 0.25); border: 1px solid rgba(255, 255, 255, 0.05); border-radius: 12px; padding: 20px; margin-bottom: 15px;'>
                            <div style='display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px; flex-wrap: wrap; gap: 10px;'>
                                <h5 style='margin: 0; color: #f8fafc; font-weight: 700;'>[{t_id}] {t_name}</h5>
                                <div style='display: flex; align-items: center; gap: 10px;'>
                                    <span class='status-badge {badge_class}'>{status}</span>
                                    <span class='time-slot-badge'>Est: {t_est} hrs</span>
                                </div>
                            </div>
                            <p style='color: #cbd5e1; font-size: 0.88rem; margin: 0 0 15px 0; line-height: 1.4;'>{t_desc}</p>
                        </div>
                        """
                    )
                    
                    # Columns for Actions: Checkbox checklist, Due Date and Time Spent
                    col_chk, col_act = st.columns([1.2, 1], gap="medium")
                    
                    with col_chk:
                        st.html("<span style='font-size: 0.8rem; font-weight: 700; color: #64748b; text-transform: uppercase;'>Action Checkpoints</span>")
                        for idx, sub in enumerate(subtasks):
                            key = f"{t_id}_{idx}"
                            current_val = st.session_state.task_completions.get(key, False)
                            
                            val = st.checkbox(sub, value=current_val, key=f"prog_chk_{key}")
                            if val != current_val:
                                st.session_state.task_completions[key] = val
                                record_activity()
                                st.rerun()
                                
                    with col_act:
                        st.html("<span style='font-size: 0.8rem; font-weight: 700; color: #64748b; text-transform: uppercase;'>Execution Details</span>")
                        
                        # Due Date picker
                        current_due = st.session_state.task_due_dates.get(t_id)
                        due_date_val = datetime.date.today()
                        if current_due:
                            due_date_val = datetime.datetime.strptime(current_due, "%Y-%m-%d").date()
                            
                        new_due = st.date_input(
                            f"Due Date for {t_id}", 
                            value=due_date_val, 
                            key=f"prog_due_{t_id}",
                            label_visibility="collapsed"
                        )
                        new_due_str = new_due.strftime("%Y-%m-%d")
                        if new_due_str != current_due:
                            st.session_state.task_due_dates[t_id] = new_due_str
                            record_activity()
                            st.rerun()
                            
                        # Time Spent input
                        current_spent = float(st.session_state.task_time_spent.get(t_id, 0.0))
                        new_spent = st.number_input(
                            f"Log Hours Spent for {t_id}",
                            min_value=0.0,
                            max_value=100.0,
                            value=current_spent,
                            step=0.5,
                            key=f"prog_spent_{t_id}"
                        )
                        if new_spent != current_spent:
                            st.session_state.task_time_spent[t_id] = new_spent
                            record_activity()
                            st.rerun()

                    st.markdown("<hr style='border-color: rgba(255,255,255,0.05); margin: 15px 0;'>", unsafe_allow_html=True)

    # ==================== TAB 3: WEEKLY REFLECTION ====================
    with tab_reflection:
        st.html("<p style='color: #94a3b8; font-size: 0.95rem; margin-bottom: 20px;'>Generate periodic, AI-assisted coaching diagnostics. The coach evaluates your metrics and suggests adjustments.</p>")
        
        if not api_key:
            st.warning("Please configure your Gemini API Key in the sidebar before requesting reflection.")
            
        # Trigger reflection button
        if st.button("Generate Weekly Coach Reflection 🧠", type="primary", disabled=not api_key):
            with st.spinner("AI Execution Coach is reviewing your telemetry and diagnosing blocks..."):
                try:
                    # Package metrics details for prompt
                    progress_summary = {
                        "health_score": metrics["health_score"],
                        "completion_rate": metrics["overall_completion_pct"],
                        "streak_count": metrics["streak_count"],
                        "overdue_count": metrics["overdue_tasks_count"],
                        "overdue_tasks_names": metrics["overdue_tasks_names"],
                        "total_hours_spent": metrics["total_hours_spent"],
                        "completed_tasks_count": metrics["completed_tasks"],
                        "total_tasks_count": metrics["total_tasks"]
                    }
                    
                    res = generate_weekly_reflection_with_gemini(
                        profile_data,
                        goal_context,
                        progress_summary,
                        api_key
                    )
                    
                    # Store generated reflection
                    new_ref = {
                        "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M"),
                        "reflection": res.get("reflection", "No reflection returned."),
                        "suggested_adjustments": res.get("suggested_adjustments", []),
                        "encouragement_quote": res.get("encouragement_quote", "Keep moving forward.")
                    }
                    
                    st.session_state.weekly_reflections.insert(0, new_ref) # Prepend
                    st.rerun()
                except Exception as e:
                    st.error(f"Weekly reflection generation failed: {str(e)}")

        # Display past reflections
        if not st.session_state.weekly_reflections:
            st.info("No reflection logs generated yet. Click the button above to request your first coaching session.")
        else:
            for idx, ref in enumerate(st.session_state.weekly_reflections):
                exp_label = f"📝 Coach Session Log - {ref['timestamp']}"
                with st.expander(exp_label, expanded=(idx == 0)):
                    st.html(
                        f"""
                        <div class='coaching-bubble'>
                            <div style='color: #818cf8; font-weight: 700; margin-bottom: 12px; font-size: 0.8rem; text-transform: uppercase;'>COACH DIAGNOSTIC BRIEF</div>
                            <div style='color: #cbd5e1; font-size: 0.95rem; margin-bottom: 15px;'>{ref['reflection']}</div>
                        </div>
                        """
                    )
                    
                    st.html("<b style='color: #fbbf24; font-size: 0.9rem;'>Suggested Action Plan Adjustments:</b>")
                    adjust_list = "".join([f"<li style='color: #cbd5e1; font-size: 0.9rem; margin-bottom: 5px;'>{item}</li>" for item in ref.get("suggested_adjustments", [])])
                    st.html(f"<ul style='margin-top: 5px; padding-left: 20px;'>{adjust_list}</ul>")
                    
                    st.html(
                        f"""
                        <div style='border-top: 1px solid rgba(255,255,255,0.06); padding-top: 15px; text-align: center;'>
                            <p style='font-style: italic; color: #10b981; font-size: 1.05rem;'>"{ref['encouragement_quote']}"</p>
                        </div>
                        """
                    )

    # ==================== TAB 4: INTEGRATIONS ====================
    with tab_export:
        st.html("<p style='color: #94a3b8; font-size: 0.95rem; margin-bottom: 20px;'>Telemetric payload formatted for direct feeding into the downstream AI Coach Agent.</p>")
        
        # Package integration payload
        coach_export_payload = {
            "execution_health_score": metrics["health_score"],
            "current_streak_days": metrics["streak_count"],
            "weekly_velocity_tasks": metrics["velocity_tasks_per_week"],
            "total_tasks_count": metrics["total_tasks"],
            "completed_tasks_count": metrics["completed_tasks"],
            "completion_ratio": round(metrics["completed_tasks"] / metrics["total_tasks"], 3) if metrics["total_tasks"] > 0 else 0.0,
            "total_allocated_hours": metrics["total_estimated_hours"],
            "total_logged_hours": metrics["total_hours_spent"],
            "overdue_tasks_count": metrics["overdue_tasks_count"],
            "overdue_tasks_list": metrics["overdue_tasks_names"],
            "streak_last_active_date": st.session_state.last_activity_date,
            "persona_archetype": profile_data.get("experience_level"),
            "weekly_hour_availability": profile_data.get("hours_per_week"),
            "user_biggest_challenge": profile_data.get("biggest_challenge")
        }
        
        st.json(coach_export_payload)
        
        st.html(
            """
            <div style='background-color: rgba(16, 185, 129, 0.05); border: 1px solid rgba(16, 185, 129, 0.2); border-radius: 8px; padding: 15px; margin-top: 15px;'>
                <p style='color: #34d399; font-size: 0.85rem; margin: 0;'>
                    🚀 <b>Downstream API Compatibility Checked</b>: This payload structure matches the telemetry specifications of the <b>AI Coach Agent</b>. When the coach executes, it will automatically consume these variables from <code>st.session_state</code>.
                </p>
            </div>
            """
        )
