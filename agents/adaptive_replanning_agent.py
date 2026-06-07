import streamlit as st
import datetime
from services.replanning_service import generate_replanning_analysis
from agents.goal_agent import render_sidebar_api_key
from agents.progress_agent import calculate_metrics
from components.replanning_preview import render_schedule_comparison
from components.impact_analysis import render_schedule_impact_analysis

def initialize_replanning_state():
    """
    Initializes session state variables for the Adaptive Replanning Agent.
    """
    if "replanned_schedule_preview" not in st.session_state:
        st.session_state["replanned_schedule_preview"] = None
    if "replanning_mode" not in st.session_state:
        st.session_state.replanning_mode = "Balanced"
    if "replanning_hours" not in st.session_state:
        hours = 10.0
        if "profile_data" in st.session_state and "hours_per_week" in st.session_state.profile_data:
            hours = float(st.session_state.profile_data["hours_per_week"])
        st.session_state.replanning_hours = hours
    if "roadmap_health" not in st.session_state:
        st.session_state["roadmap_health"] = None
    if "completion_forecast" not in st.session_state:
        st.session_state["completion_forecast"] = None
    if "impact_analysis" not in st.session_state:
        st.session_state["impact_analysis"] = None

def apply_replanned_schedule(preview, roadmap_dag_data):
    """
    Executes the schedule re-execution workflow:
    1. Copies the preview to active schedule
    2. Increments the version number
    3. Saves history
    4. Recalculates due dates, deadlines, and forecasts
    5. Clears preview and refreshes AI Coach
    """
    # 1. Copy preview to active_schedule
    st.session_state["active_schedule"] = {
        "weekly_schedule": preview.get("replanned_weekly_schedule", []),
        "daily_schedule": preview.get("replanned_daily_schedule", []),
        "schedule_analysis": {
            "confidence_score": preview.get("completion_probability", 80),
            "goal_completion_forecast": preview.get("goal_completion_forecast", "Adjusted"),
            "buffer_time_allocation": f"Adjusted under {st.session_state.replanning_mode} mode.",
            "deadline_feasibility_analysis": preview.get("risk_analysis", ""),
            "rescheduling_suggestions": [
                {
                    "id": f"replan_sug_{i}",
                    "title": f"Adjustment Option {i+1}",
                    "description": adj,
                    "impact": "High"
                }
                for i, adj in enumerate(preview.get("recommended_adjustments", []))
            ]
        }
    }
    
    # Sync legacy keys
    st.session_state.weekly_schedule = st.session_state["active_schedule"]["weekly_schedule"]
    st.session_state.daily_schedule = st.session_state["active_schedule"]["daily_schedule"]
    st.session_state.schedule_analysis = st.session_state["active_schedule"]["schedule_analysis"]
    
    # 2. Increment schedule version
    st.session_state["current_schedule_version"] += 1
    new_version = st.session_state["current_schedule_version"]
    
    # 3. Store history
    st.session_state["schedule_versions"].append({
        "version": new_version,
        "name": f"{st.session_state.replanning_mode} Replan",
        "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M"),
        "schedule": st.session_state["active_schedule"]
    })
    
    # 4. Recalculate task due dates based on new week mapping
    start_date = datetime.date.today()
    task_weeks = {}
    for week in st.session_state.weekly_schedule:
        w_num = week.get("week_number", 1)
        for t in week.get("tasks", []):
            t_id = t.get("task_id")
            if t_id:
                task_weeks[t_id] = w_num
                
    if "roadmap_dag_data" in st.session_state and st.session_state.roadmap_dag_data:
        for phase in st.session_state.roadmap_dag_data.get("phases", []):
            for task in phase.get("tasks", []):
                t_id = task.get("task_id")
                if t_id and t_id in task_weeks:
                    w_num = task_weeks[t_id]
                    due_date = start_date + datetime.timedelta(weeks=int(w_num))
                    st.session_state.task_due_dates[t_id] = due_date.strftime("%Y-%m-%d")

    # Update capacity capacity limit in profile
    st.session_state.profile_data["hours_per_week"] = st.session_state.replanning_hours
    
    # Update active metrics
    st.session_state["roadmap_health"] = preview.get("roadmap_health_score", 80)
    st.session_state["completion_forecast"] = preview.get("goal_completion_forecast", "Adjusted")
    st.session_state["impact_analysis"] = preview.get("risk_analysis", "")
    
    # Save log into reflections
    new_log = {
        "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M"),
        "reflection": f"Roadmap replanned to version {new_version} under objective **{st.session_state.replanning_mode}** with capacity **{st.session_state.replanning_hours}h/week**. Reason: {preview.get('risk_analysis')}",
        "suggested_adjustments": preview.get("recommended_adjustments", []),
        "encouragement_quote": "Your roadmap has been successfully adjusted and you are now back on track."
    }
    if "weekly_reflections" not in st.session_state:
        st.session_state.weekly_reflections = []
    st.session_state.weekly_reflections.insert(0, new_log)
    
    # 5. Clear preview outputs and coach dashboard cache to trigger a refresh
    st.session_state["replanned_schedule_preview"] = None
    st.session_state.coach_outputs = None

def render_adaptive_replanning_agent():
    """
    Renders the Adaptive Replanning Agent workspace.
    """
    initialize_replanning_state()

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

    if "selected_strategy_data" not in st.session_state or not st.session_state.selected_strategy_data:
        st.html(
            """
            <div style='text-align: center; padding: 40px;'>
                <h3 style='color: #f87171;'>⚠️ No Strategy Selected</h3>
                <p style='color: #94a3b8;'>Please select an execution strategy first.</p>
            </div>
            """
        )
        if st.button("Go to Strategy Selection ⚡"):
            st.session_state.app_phase = "strategy_generation"
            st.rerun()
        return

    if "strategy_validation" not in st.session_state or not st.session_state.strategy_validation:
        st.html(
            """
            <div style='text-align: center; padding: 40px;'>
                <h3 style='color: #f87171;'>⚠️ Missing Strategy Validation</h3>
                <p style='color: #94a3b8;'>Please complete the Strategy Validation audit first.</p>
            </div>
            """
        )
        if st.button("Go to Strategy Validation 📋"):
            st.session_state.app_phase = "strategy_validation"
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

    # Check if a schedule exists using active_schedule as single source of truth
    has_schedule = False
    if "active_schedule" in st.session_state and st.session_state["active_schedule"]:
        has_schedule = True
    elif "weekly_schedule" in st.session_state and st.session_state.weekly_schedule:
        has_schedule = True
        
    if not has_schedule:
        st.html(
            """
            <div style='text-align: center; padding: 40px;'>
                <h3 style='color: #f87171;'>⚠️ Missing Schedule</h3>
                <p style='color: #94a3b8;'>Please generate your weekly execution calendar first.</p>
            </div>
            """
        )
        if st.button("Go to Coaching Scheduler 📅"):
            st.session_state.app_phase = "scheduling"
            st.rerun()
        return

    # Extract active states
    profile_data = st.session_state.profile_data
    goal_context = st.session_state.goal_context
    selected_strategy = st.session_state.selected_strategy_data
    readiness_results = st.session_state.strategy_validation
    roadmap_dag_data = st.session_state.roadmap_dag_data
    
    if "active_schedule" in st.session_state and st.session_state["active_schedule"]:
        schedule_data = st.session_state["active_schedule"]
    else:
        schedule_data = {
            "weekly_schedule": st.session_state.get("weekly_schedule", []) or [],
            "daily_schedule": st.session_state.get("daily_schedule", []) or [],
            "schedule_analysis": st.session_state.get("schedule_analysis", {}) or {}
        }

    # Calculate metrics & load reflections/coach insights
    progress_metrics = calculate_metrics()
    coach_insights = st.session_state.get("coach_outputs", {}) or {}
    api_key = render_sidebar_api_key()

    # Sidebar navigation
    st.sidebar.html("<h3 style='margin-bottom: 20px;'>Navigation</h3>")
    if st.sidebar.button("👤 View Persona Profile", key="replan_nav_profile", use_container_width=True):
        st.session_state.app_phase = "profiling"
        st.rerun()
    if st.sidebar.button("📊 Back to Progress Center", key="replan_nav_prog", use_container_width=True):
        st.session_state.app_phase = "progress_tracking"
        st.rerun()
    if st.sidebar.button("🧠 Back to AI Coach", key="replan_nav_coach", use_container_width=True):
        st.session_state.app_phase = "coaching"
        st.rerun()
    st.sidebar.html("<hr style='border-color: rgba(255,255,255,0.1); margin: 15px 0;'>")

    # CSS Injection
    st.html(
        """
        <style>
        .replan-header {
            text-align: center;
            padding: 30px 20px;
            max-width: 800px;
            margin: 0 auto;
        }

        .replan-card {
            background: linear-gradient(135deg, rgba(30, 41, 59, 0.4) 0%, rgba(15, 23, 42, 0.6) 100%);
            border: 1px solid rgba(255, 255, 255, 0.06);
            border-radius: 16px;
            padding: 25px;
            margin-bottom: 25px;
            box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.25);
            backdrop-filter: blur(8px);
        }

        .metric-glow {
            transition: transform 0.2s ease, border-color 0.2s ease;
        }
        .metric-glow:hover {
            transform: translateY(-2px);
            border-color: rgba(99, 102, 241, 0.25);
        }

        .replan-adjust-pill {
            background: rgba(251, 191, 36, 0.08);
            border: 1px solid rgba(251, 191, 36, 0.25);
            color: #fbbf24;
            padding: 10px 15px;
            border-radius: 10px;
            margin-bottom: 10px;
            font-size: 0.92rem;
            line-height: 1.4;
        }
        
        .overdue-list-item {
            color: #f87171;
            font-size: 0.9rem;
            margin-bottom: 5px;
            list-style-type: square;
        }

        .version-badge {
            background: rgba(99, 102, 241, 0.15);
            color: #818cf8;
            border: 1px solid rgba(99, 102, 241, 0.25);
            padding: 2px 8px;
            border-radius: 6px;
            font-size: 0.75rem;
            font-weight: bold;
        }
        .version-badge-active {
            background: rgba(16, 185, 129, 0.15) !important;
            color: #34d399 !important;
            border-color: rgba(16, 185, 129, 0.25) !important;
        }
        </style>
        """
    )

    # 1. HEADER
    st.html(
        """
        <div class='replan-header'>
            <span class='badge' style='background: rgba(245, 158, 11, 0.1); color: #fbbf24; border: 1px solid rgba(245, 158, 11, 0.3); padding: 6px 14px; border-radius: 20px; font-size: 0.85rem; font-weight: 700; letter-spacing: 1.5px;'>PHASE 8: ADAPTIVE REPLANNING AGENT</span>
            <h1 style='font-size: 2.8rem; font-weight: 800; margin-top: 15px; margin-bottom: 10px; background: linear-gradient(to right, #f8fafc, #94a3b8); -webkit-background-clip: text; -webkit-text-fill-color: transparent;'>Dynamic Roadmaps & Replanning</h1>
            <p style='color: #94a3b8; font-size: 1.15rem;'>Recalculate your calendar to resolve delays, adjust availability constraints, and align execution with your energy limits.</p>
        </div>
        """
    )

    if not api_key:
        st.warning("Please configure your Gemini API Key in the sidebar to activate the Adaptive Replanning Agent.")
        return

    # 2. TELEMETRY AUDIT FRAME
    st.html("<h4 style='color: #cbd5e1; font-weight: 700; margin-bottom: 15px;'>🔍 Execution Delays & Telemetry Audit</h4>")
    
    col_t1, col_t2 = st.columns([1, 1.2], gap="large")
    
    with col_t1:
        st.html(
            f"""
            <div class='replan-card' style='height: 100%; border-left: 4px solid #f87171;'>
                <h5 style='margin: 0 0 10px 0; color: #f87171; font-weight: bold;'>Detected Planning Gaps</h5>
                <p style='color: #cbd5e1; font-size: 0.88rem; line-height: 1.4; margin-bottom: 15px;'>
                    The agent has performed a telemetry check. We detected active scheduling gaps and overdue items:
                </p>
                <div style='font-size: 0.95rem; color: #cbd5e1; margin-bottom: 8px;'>⚠️ Overdue Tasks Count: <b>{progress_metrics.get("overdue_tasks_count", 0)}</b></div>
                <div style='font-size: 0.95rem; color: #cbd5e1; margin-bottom: 15px;'>🔥 Current Streak: <b>{progress_metrics.get("streak_count", 0)} days</b></div>
            </div>
            """
        )
        
    with col_t2:
        overdue_names = progress_metrics.get("overdue_tasks_names", [])
        if overdue_names:
            overdue_items_html = "".join([f"<li class='overdue-list-item'>{name}</li>" for name in overdue_names])
            st.html(
                f"""
                <div class='replan-card' style='height: 100%;'>
                    <h5 style='margin: 0 0 10px 0; color: #cbd5e1; font-weight: bold;'>Active Bottleneck Checklist</h5>
                    <ul style='padding-left: 20px; margin: 0;'>
                        {overdue_items_html}
                    </ul>
                </div>
                """
            )
        else:
            st.html(
                """
                <div class='replan-card' style='height: 100%; display: flex; align-items: center; justify-content: center; border-left: 4px solid #10b981;'>
                    <div style='text-align: center;'>
                        <span style='font-size: 1.8rem; color: #10b981;'>✅</span>
                        <h6 style='margin: 5px 0 0 0; color: #10b981; font-weight: bold;'>No Overdue Tasks</h6>
                        <p style='color: #94a3b8; font-size: 0.78rem; margin: 3px 0 0 0;'>You are fully on track! You can still use replanning to adjust hours or mode preferences.</p>
                    </div>
                </div>
                """
            )

    # 3. CONTROL PANEL
    st.html("<div style='height: 15px;'></div>")
    st.html("<h4 style='color: #cbd5e1; font-weight: 700; margin-bottom: 15px;'>⚙️ Adjust Constraints & Replanning Mode</h4>")
    
    col_c1, col_c2 = st.columns([1, 1.2], gap="large")
    
    with col_c1:
        modes = ["Balanced", "Catch Up", "Low Stress", "Aggressive"]
        current_idx = modes.index(st.session_state.replanning_mode) if st.session_state.replanning_mode in modes else 0
        
        sel_mode = st.selectbox(
            "Select Replanning Objective Mode",
            options=modes,
            index=current_idx,
            help="Choose how the agent should reschedule remaining incomplete tasks."
        )
        if sel_mode != st.session_state.replanning_mode:
            st.session_state.replanning_mode = sel_mode
            
    with col_c2:
        new_hours = st.slider(
            "Adjust Weekly Hour Availability Limit",
            min_value=1.0,
            max_value=40.0,
            step=1.0,
            value=st.session_state.replanning_hours,
            help="Define your new weekly dedication limits. This adjusts allocations dynamically."
        )
        if new_hours != st.session_state.replanning_hours:
            st.session_state.replanning_hours = new_hours

    st.markdown("<div style='height: 10px;'></div>", unsafe_allow_html=True)
    
    col_btn1, col_btn2, col_btn3 = st.columns([1, 1.2, 1])
    with col_btn2:
        if st.button("Generate Replanned Schedule Preview ⚡", use_container_width=True, type="primary"):
            with st.spinner("AI Replanning Agent is recalculating dependencies, timelines, and daily calendars..."):
                try:
                    res = generate_replanning_analysis(
                        profile_data,
                        goal_context,
                        selected_strategy,
                        readiness_results,
                        roadmap_dag_data,
                        schedule_data,
                        progress_metrics,
                        coach_insights,
                        st.session_state.replanning_hours,
                        st.session_state.replanning_mode,
                        api_key
                    )
                    st.session_state["replanned_schedule_preview"] = res
                    st.rerun()
                except Exception as e:
                    st.error(f"Schedule Replanning Failed: {str(e)}")

    # 4. DASHBOARD DETAILS & PREVIEW
    preview = st.session_state["replanned_schedule_preview"]
    if preview:
        st.html("<hr style='border-color: rgba(255,255,255,0.08); margin: 35px 0;'>")
        st.html("<h3 style='color: #fbbf24; font-weight: 800; font-size: 1.8rem; margin-bottom: 20px;'>📊 Replanning Forecast Dashboard</h3>")
        
        # Diagnostic row
        col_r1, col_r2, col_r3 = st.columns(3)
        
        with col_r1:
            # Roadmap Health Card
            h_score = preview.get("roadmap_health_score", 80)
            h_color = "#10b981"
            if h_score < 50:
                h_color = "#f87171"
            elif h_score < 75:
                h_color = "#fbbf24"
            st.html(
                f"""
                <div class='replan-card metric-glow' style='text-align: center; height: 100%;'>
                    <span style='font-size: 0.8rem; text-transform: uppercase; font-weight: 700; color: #64748b; letter-spacing: 1px;'>Roadmap Health Card</span>
                    <div style='font-size: 2.8rem; font-weight: 800; color: {h_color}; margin: 8px 0;'>{h_score}%</div>
                    <p style='font-size: 0.78rem; color: #94a3b8; margin: 0;'>Workload capacity safety & delay buffer margins.</p>
                </div>
                """
            )
            
        with col_r2:
            # Completion Probability Card
            prob = preview.get("completion_probability", 80)
            p_color = "#10b981"
            if prob < 50:
                p_color = "#f87171"
            elif prob < 75:
                p_color = "#fbbf24"
            st.html(
                f"""
                <div class='replan-card metric-glow' style='text-align: center; height: 100%;'>
                    <span style='font-size: 0.8rem; text-transform: uppercase; font-weight: 700; color: #64748b; letter-spacing: 1px;'>Completion Probability Card</span>
                    <div style='font-size: 2.8rem; font-weight: 800; color: {p_color}; margin: 8px 0;'>{prob}%</div>
                    <p style='font-size: 0.78rem; color: #94a3b8; margin: 0;'>Feasibility of target date matching availability.</p>
                </div>
                """
            )
            
        with col_r3:
            # Forecast Completion Date Card
            forecast = preview.get("goal_completion_forecast", "Adjusted")
            st.html(
                f"""
                <div class='replan-card metric-glow' style='text-align: center; height: 100%;'>
                    <span style='font-size: 0.8rem; text-transform: uppercase; font-weight: 700; color: #64748b; letter-spacing: 1px;'>Forecast Completion Date Card</span>
                    <div style='font-size: 1.1rem; font-weight: 800; color: #818cf8; margin: 24px 0;'>{forecast}</div>
                    <p style='font-size: 0.78rem; color: #94a3b8; margin: 0;'>Adjusted timeline forecast date calculated.</p>
                </div>
                """
            )

        # Risk details and suggested adjustments
        col_det1, col_det2 = st.columns([1.2, 1], gap="large")
        with col_det1:
            st.html("<h5 style='color: #818cf8; font-weight: bold; margin-bottom: 10px;'>🔍 Risk Analysis & Delay Drivers</h5>")
            st.html(
                f"""
                <div class='replan-card'>
                    <div style='color: #cbd5e1; font-size: 0.95rem; line-height: 1.5;'>{preview.get("risk_analysis", "")}</div>
                </div>
                """
            )
        with col_det2:
            st.html("<h5 style='color: #fbbf24; font-weight: bold; margin-bottom: 10px;'>💡 Recommended Adjustments</h5>")
            adjusts = preview.get("recommended_adjustments", [])
            for item in adjusts:
                st.html(f"<div class='replan-adjust-pill'>⚡ {item}</div>")

        # 4a. Schedule Impact Analysis Card
        st.html("<div style='height: 15px;'></div>")
        st.html("<h4 style='color: #cbd5e1; font-weight: 700; margin-bottom: 10px;'>📊 Schedule Impact Analysis Card</h4>")
        render_schedule_impact_analysis(
            old_weekly=schedule_data.get("weekly_schedule", []),
            new_weekly=preview.get("replanned_weekly_schedule", []),
            old_capacity=float(profile_data.get("hours_per_week", 10.0)),
            new_capacity=st.session_state.replanning_hours,
            old_probability=int(schedule_data.get("schedule_analysis", {}).get("confidence_score", 80)),
            new_probability=int(preview.get("completion_probability", 80)),
            old_health=float(progress_metrics.get("health_score", 100)),
            new_health=float(preview.get("roadmap_health_score", 80))
        )

        # 4b. Schedule Comparison View (Old vs New Schedule)
        st.html("<div style='height: 15px;'></div>")
        render_schedule_comparison(
            old_weekly=schedule_data.get("weekly_schedule", []),
            new_weekly=preview.get("replanned_weekly_schedule", [])
        )

        # Integrations payload preview
        with st.expander("🔌 Preview Memory Agent Replanning Payload", expanded=False):
            st.json(preview.get("memory_payload", {}))

        # 5. USER APPROVAL WORKFLOW
        st.html("<div style='height: 25px;'></div>")
        col_act1, col_act2, col_act3 = st.columns([1, 1.8, 1])
        
        with col_act2:
            if st.button("Apply Replanned Schedule ⚡", key="btn_apply_replan", use_container_width=True, type="primary"):
                try:
                    apply_replanned_schedule(preview, roadmap_dag_data)
                    st.success("Replanning successfully applied! Active schedule and capacity constraints have been updated.")
                    st.balloons()
                    
                    # Redirect to the scheduler page as requested
                    st.session_state.app_phase = "scheduling"
                    st.rerun()
                except Exception as ex:
                    st.error(f"Applying adjustments failed: {str(ex)}")

    # 6. SCHEDULE VERSION HISTORY CARD
    st.html("<hr style='border-color: rgba(255,255,255,0.08); margin: 35px 0;'>")
    st.html("<h3 style='color: #cbd5e1; font-weight: 700; margin-bottom: 15px;'>📜 Schedule Version History Card</h3>")
    
    versions = st.session_state.get("schedule_versions", [])
    current_ver = st.session_state.get("current_schedule_version", 1)
    
    if not versions:
        st.info("No schedule versions logged yet. Version history will update once a schedule is generated or replanned.")
    else:
        for ver in versions:
            ver_num = ver.get("version", 1)
            ver_name = ver.get("name", "Original Schedule")
            timestamp = ver.get("timestamp", "N/A")
            
            # Active badge
            is_active = (ver_num == current_ver)
            badge_class = "version-badge-active" if is_active else ""
            badge_label = "Active Version" if is_active else "Archived Version"
            
            st.html(
                f"""
                <div style='background: rgba(30, 41, 59, 0.2); border: 1px solid rgba(255, 255, 255, 0.05); border-radius: 10px; padding: 15px; margin-bottom: 12px; display: flex; justify-content: space-between; align-items: center;'>
                    <div>
                        <b style='color: #f8fafc; font-size: 1rem;'>Version {ver_num}: {ver_name}</b>
                        <div style='color: #64748b; font-size: 0.82rem; margin-top: 4px;'>Logged: {timestamp}</div>
                    </div>
                    <span class='version-badge {badge_class}'>{badge_label}</span>
                </div>
                """
            )
