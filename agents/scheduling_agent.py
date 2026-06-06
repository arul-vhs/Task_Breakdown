import streamlit as st
import datetime
from services.gemini_service import generate_schedule_with_gemini
from agents.goal_agent import render_sidebar_api_key

def initialize_scheduling_state():
    """
    Initializes session state variables for the Scheduling Agent.
    """
    if "weekly_schedule" not in st.session_state:
        st.session_state.weekly_schedule = None
    if "daily_schedule" not in st.session_state:
        st.session_state.daily_schedule = None
    if "schedule_analysis" not in st.session_state:
        st.session_state.schedule_analysis = None
    if "applied_suggestion" not in st.session_state:
        st.session_state.applied_suggestion = None
    if "original_weekly_schedule" not in st.session_state:
        st.session_state.original_weekly_schedule = None
    if "original_daily_schedule" not in st.session_state:
        st.session_state.original_daily_schedule = None
    if "original_schedule_analysis" not in st.session_state:
        st.session_state.original_schedule_analysis = None

def apply_rescheduling_suggestion(suggestion_id: str):
    """
    Simulates the impact of a rescheduling suggestion in session state.
    """
    if not st.session_state.schedule_analysis:
        return

    # Back up original if not already done
    if st.session_state.original_weekly_schedule is None:
        st.session_state.original_weekly_schedule = list(st.session_state.weekly_schedule)
        st.session_state.original_daily_schedule = list(st.session_state.daily_schedule)
        st.session_state.original_schedule_analysis = dict(st.session_state.schedule_analysis)

    suggestions = st.session_state.original_schedule_analysis.get("rescheduling_suggestions", [])
    selected_sug = next((s for s in suggestions if s["id"] == suggestion_id), None)
    
    if not selected_sug:
        return

    st.session_state.applied_suggestion = selected_sug

    # Simulate changes based on suggestion type
    if "extend" in suggestion_id.lower() or "timeline" in suggestion_id.lower():
        # Extend timeline: reduce allocated hours slightly, add an extra week representation
        new_weekly = []
        for week in st.session_state.original_weekly_schedule:
            week_copy = dict(week)
            week_copy["allocated_hours"] = max(1.0, week_copy["allocated_hours"] * 0.8)
            new_weekly.append(week_copy)
        
        # Add simulated Week N+1
        last_week_num = len(new_weekly) + 1
        new_weekly.append({
            "week_number": last_week_num,
            "focus": "Buffer & Final Integration",
            "allocated_hours": 3.0,
            "tasks": []
        })
        st.session_state.weekly_schedule = new_weekly

        # Increase Confidence Score
        analysis_copy = dict(st.session_state.original_schedule_analysis)
        analysis_copy["confidence_score"] = min(100, analysis_copy.get("confidence_score", 80) + 12)
        analysis_copy["goal_completion_forecast"] = f"Extended by 1 week ({selected_sug['impact']})"
        st.session_state.schedule_analysis = analysis_copy

    elif "buffer" in suggestion_id.lower() or "boost" in suggestion_id.lower():
        # Add buffers: shift tasks slightly, reduce daily hours, boost confidence
        analysis_copy = dict(st.session_state.original_schedule_analysis)
        analysis_copy["confidence_score"] = min(100, analysis_copy.get("confidence_score", 80) + 8)
        analysis_copy["buffer_time_allocation"] = "Boosted: Enforced 20% dedicated buffer time in all active days."
        st.session_state.schedule_analysis = analysis_copy

    elif "weekend" in suggestion_id.lower() or "load" in suggestion_id.lower() or "parallel" in suggestion_id.lower():
        # Distribute to weekends / parallelize
        analysis_copy = dict(st.session_state.original_schedule_analysis)
        analysis_copy["confidence_score"] = min(100, analysis_copy.get("confidence_score", 80) + 5)
        analysis_copy["deadline_feasibility_analysis"] = "Optimized: Work distributed onto weekends to lower weekday strain."
        st.session_state.schedule_analysis = analysis_copy

def reset_schedule():
    """
    Resets the schedule to the original generated version.
    """
    if st.session_state.original_weekly_schedule is not None:
        st.session_state.weekly_schedule = st.session_state.original_weekly_schedule
        st.session_state.daily_schedule = st.session_state.original_daily_schedule
        st.session_state.schedule_analysis = st.session_state.original_schedule_analysis
        st.session_state.applied_suggestion = None
        st.session_state.original_weekly_schedule = None
        st.session_state.original_daily_schedule = None
        st.session_state.original_schedule_analysis = None

def render_scheduling_agent():
    """
    Renders the Scheduling Agent workspace.
    """
    initialize_scheduling_state()

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
    strategy = st.session_state.selected_strategy_data
    roadmap = st.session_state.roadmap_dag_data
    api_key = render_sidebar_api_key()

    # Sidebar back-navigation controls
    st.sidebar.html("<h3 style='margin-bottom: 20px;'>Navigation</h3>")
    if st.sidebar.button("👤 View Persona Profile", key="sched_nav_profile", use_container_width=True):
        st.session_state.app_phase = "profiling"
        st.rerun()
    if st.sidebar.button("🗺️ Back to Roadmap DAG", key="sched_nav_dag", use_container_width=True):
        st.session_state.app_phase = "execution_blueprint"
        st.rerun()
    st.sidebar.html("<hr style='border-color: rgba(255,255,255,0.1); margin: 15px 0;'>")

    # Custom Premium CSS injection for Calendar and Timelines
    st.html(
        """
        <style>
        .scheduler-header {
            text-align: center;
            padding: 30px 20px;
            max-width: 800px;
            margin: 0 auto;
        }
        .section-header {
            color: #818cf8;
            font-weight: 700;
            margin-top: 25px;
            margin-bottom: 15px;
            font-size: 1.3rem;
            text-transform: uppercase;
            letter-spacing: 1.5px;
            border-bottom: 1.5px solid rgba(129, 140, 248, 0.2);
            padding-bottom: 6px;
        }
        /* Custom timeline and calendar views */
        .week-card {
            background: rgba(30, 41, 59, 0.35);
            border: 1px solid rgba(255, 255, 255, 0.06);
            border-radius: 12px;
            padding: 20px;
            margin-bottom: 15px;
            transition: all 0.2s ease;
        }
        .week-card:hover {
            border-color: rgba(99, 102, 241, 0.25);
            background: rgba(30, 41, 59, 0.45);
        }
        .time-block {
            background: linear-gradient(135deg, rgba(30, 41, 59, 0.6) 0%, rgba(15, 23, 42, 0.8) 100%);
            border-left: 4px solid #6366f1;
            border-radius: 8px;
            padding: 12px 16px;
            margin-bottom: 10px;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        .time-block-learning {
            border-left-color: #a855f7 !important;
        }
        .time-block-setup {
            border-left-color: #cbd5e1 !important;
        }
        .time-block-coding {
            border-left-color: #10b981 !important;
        }
        .time-slot-badge {
            background: rgba(99, 102, 241, 0.15);
            color: #818cf8;
            border: 1px solid rgba(99, 102, 241, 0.25);
            padding: 3px 8px;
            border-radius: 6px;
            font-size: 0.78rem;
            font-weight: 600;
        }
        .suggest-card {
            background: rgba(30, 41, 59, 0.4);
            border: 1px solid rgba(255, 255, 255, 0.08);
            border-radius: 12px;
            padding: 18px;
            margin-bottom: 15px;
            height: 100%;
            display: flex;
            flex-direction: column;
            justify-content: space-between;
        }
        .suggest-title {
            color: #fbbf24;
            font-weight: 700;
            font-size: 1rem;
            margin-bottom: 8px;
        }
        .suggest-desc {
            font-size: 0.88rem;
            color: #94a3b8;
            line-height: 1.4;
            margin-bottom: 12px;
            flex-grow: 1;
        }
        .suggest-impact {
            font-size: 0.8rem;
            color: #34d399;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 0.5px;
            margin-bottom: 12px;
        }
        .gauge-container {
            text-align: center;
            background: rgba(15, 23, 42, 0.4);
            border: 1px solid rgba(255, 255, 255, 0.05);
            border-radius: 16px;
            padding: 25px;
            height: 100%;
        }
        .gauge-value {
            font-size: 3rem;
            font-weight: 800;
            margin: 10px 0;
            background: linear-gradient(135deg, #10b981 0%, #059669 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }
        .gauge-value-medium {
            background: linear-gradient(135deg, #fbbf24 0%, #d97706 100%) !important;
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }
        .gauge-value-low {
            background: linear-gradient(135deg, #f87171 0%, #dc2626 100%) !important;
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }
        .sim-banner {
            background: rgba(251, 191, 36, 0.1);
            border: 1px solid rgba(251, 191, 36, 0.25);
            border-radius: 8px;
            padding: 12px 18px;
            margin-bottom: 25px;
            color: #fbbf24;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        </style>
        """
    )

    # 1. INITIAL GENERATION STATE
    if not st.session_state.weekly_schedule:
        st.html(
            """
            <div class='scheduler-header'>
                <span class='badge' style='background: rgba(99, 102, 241, 0.1); color: #818cf8; border: 1px solid rgba(99, 102, 241, 0.3); padding: 6px 14px; border-radius: 20px; font-size: 0.85rem; font-weight: 700; letter-spacing: 1.5px;'>PHASE 5: COACHING SCHEDULER</span>
                <h1 style='font-size: 2.8rem; font-weight: 800; margin-top: 15px; margin-bottom: 10px; background: linear-gradient(to right, #f8fafc, #94a3b8); -webkit-background-clip: text; -webkit-text-fill-color: transparent;'>Optimize Your Weekly Calendar</h1>
                <p style='color: #94a3b8; font-size: 1.15rem;'>We will translate your tasks breakdown into structured time allocations, creating custom-tailored daily schedules mapping precisely to your availability limit.</p>
            </div>
            """
        )

        if not api_key:
            st.warning("Please configure your Gemini API Key in the sidebar before proceeding.")

        col1, col2, col3 = st.columns([1, 1.2, 1])
        with col2:
            if st.button("Generate Workspace Schedule 📅", use_container_width=True, type="primary", disabled=not api_key):
                with st.spinner("Gemini is designing daily allocations and calculating project timelines..."):
                    try:
                        res = generate_schedule_with_gemini(
                            profile_data,
                            goal_context,
                            strategy,
                            roadmap,
                            api_key
                        )
                        st.session_state.weekly_schedule = res.get("weekly_schedule", [])
                        st.session_state.daily_schedule = res.get("daily_schedule", [])
                        st.session_state.schedule_analysis = res.get("schedule_analysis", {})
                        st.rerun()
                    except Exception as e:
                        st.error(f"Scheduling generation failed: {str(e)}")

    # 2. RUNNING SCHEDULER WORKSPACE
    else:
        weekly = st.session_state.weekly_schedule
        daily = st.session_state.daily_schedule
        analysis = st.session_state.schedule_analysis

        # Simulation Banner if suggestion is applied
        if st.session_state.applied_suggestion:
            st.html(
                f"""
                <div class='sim-banner'>
                    <div>
                        <b>💡 Simulating Rescheduling Suggestion:</b> {st.session_state.applied_suggestion['title']}
                    </div>
                </div>
                """
            )
            col_res_btn = st.columns([1, 4, 1])
            with col_res_btn[0]:
                if st.button("Reset Schedule 🔄", key="reset_sim_schedule", type="secondary"):
                    reset_schedule()
                    st.rerun()

        # Dashboard Top row: Analytics Cards
        st.html("<div class='section-header'>📊 Schedule Feasibility & Diagnostics</div>")
        col_gauge, col_meta = st.columns([1, 2], gap="medium")

        with col_gauge:
            score = analysis.get("confidence_score", 80)
            score_class = "gauge-value"
            if score < 50:
                score_class = "gauge-value-low"
            elif score < 75:
                score_class = "gauge-value-medium"

            st.html(
                f"""
                <div class='gauge-container'>
                    <span style='font-size: 0.8rem; text-transform: uppercase; font-weight: 700; color: #64748b; letter-spacing: 1px;'>Confidence Score</span>
                    <div class='{score_class}'>{score}%</div>
                    <p style='font-size: 0.85rem; color: #94a3b8; line-height: 1.3;'>Measures scheduling safety against your challenge: <b>{profile_data.get("biggest_challenge")}</b></p>
                </div>
                """
            )

        with col_meta:
            st.html(
                f"""
                <div style='background: rgba(30, 41, 59, 0.25); border: 1px solid rgba(255, 255, 255, 0.05); border-radius: 16px; padding: 25px; height: 100%;'>
                    <div style='margin-bottom: 12px;'>
                        <span style='color: #818cf8; font-size: 0.75rem; text-transform: uppercase; font-weight: 700; letter-spacing: 1px;'>Goal Forecast</span>
                        <p style='color: #f8fafc; font-size: 1.05rem; margin: 3px 0 0 0; font-weight: 600;'>{analysis.get("goal_completion_forecast")}</p>
                    </div>
                    <div style='margin-bottom: 12px;'>
                        <span style='color: #10b981; font-size: 0.75rem; text-transform: uppercase; font-weight: 700; letter-spacing: 1px;'>Buffer Time Allocation</span>
                        <p style='color: #cbd5e1; font-size: 0.9rem; margin: 3px 0 0 0;'>{analysis.get("buffer_time_allocation")}</p>
                    </div>
                    <div>
                        <span style='color: #fbbf24; font-size: 0.75rem; text-transform: uppercase; font-weight: 700; letter-spacing: 1px;'>Feasibility Audit</span>
                        <p style='color: #cbd5e1; font-size: 0.9rem; margin: 3px 0 0 0;'>{analysis.get("deadline_feasibility_analysis")}</p>
                    </div>
                </div>
                """
            )

        # Tabbed Scheduler View: Weekly vs Daily Planner
        st.html("<div class='section-header' style='margin-top: 35px;'>📅 Execution Timelines</div>")
        tab_week, tab_day, tab_export = st.tabs(["📋 Weekly Planner", "📆 Daily Calendar", "🔌 Agent Integrations"])

        with tab_week:
            st.html("<p style='color: #94a3b8; font-size: 0.95rem; margin-bottom: 20px;'>Weekly sprint themes, task workloads, and available hour budgets.</p>")
            for week in weekly:
                week_num = week.get("week_number")
                focus = week.get("focus")
                allocated = week.get("allocated_hours", 0.0)
                tasks = week.get("tasks", [])

                task_list_items = ""
                for t in tasks:
                    task_list_items += f"""
                    <div style='display: flex; justify-content: space-between; font-size: 0.9rem; color: #cbd5e1; padding: 6px 0; border-bottom: 1px solid rgba(255,255,255,0.03);'>
                        <span>🔹 [{t.get('task_id')}] {t.get('name')}</span>
                        <span style='font-weight: 600; color: #818cf8;'>🕒 {t.get('allocated_hours')} hrs</span>
                    </div>
                    """
                
                if not tasks:
                    task_list_items = "<p style='font-size: 0.85rem; color: #64748b; font-style: italic;'>No tasks allocated.</p>"

                st.html(
                    f"""
                    <div class='week-card'>
                        <div style='display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px;'>
                            <h4 style='margin: 0; color: #f8fafc; font-weight: 700;'>Week {week_num}: {focus}</h4>
                            <span class='time-slot-badge' style='background: rgba(16, 185, 129, 0.15); color: #34d399; border-color: rgba(16, 185, 129, 0.25);'>Workload: {allocated} / {profile_data.get("hours_per_week")} hrs</span>
                        </div>
                        <div style='background: rgba(15,23,42,0.25); border-radius: 8px; padding: 12px 15px; border: 1px solid rgba(255,255,255,0.03);'>
                            {task_list_items}
                        </div>
                    </div>
                    """
                )

        with tab_day:
            st.html("<p style='color: #94a3b8; font-size: 0.95rem; margin-bottom: 20px;'>Daily hour-by-hour task allocations matching your <b>{profile_data.get('work_style')}</b> focus slots.</p>")
            
            # Group daily items by Week
            unique_weeks = sorted(list(set(d.get("week_number", 1) for d in daily)))
            
            if not unique_weeks:
                st.info("No daily task allocations found.")
            else:
                sel_week_num = st.selectbox("Select Week Filter", options=unique_weeks, format_func=lambda w: f"Week {w}")
                
                week_daily_data = [d for d in daily if d.get("week_number") == sel_week_num]
                
                for day_data in week_daily_data:
                    day_num = day_data.get("day_number")
                    day_name = day_data.get("day_name", "Active Day")
                    total_h = day_data.get("total_hours", 0.0)
                    time_blocks = day_data.get("time_blocks", [])

                    blocks_html = ""
                    for block in time_blocks:
                        b_type = block.get("type", "Coding").lower()
                        type_class = ""
                        if "learn" in b_type:
                            type_class = "time-block-learning"
                        elif "setup" in b_type or "research" in b_type:
                            type_class = "time-block-setup"
                        elif "code" in b_type:
                            type_class = "time-block-coding"

                        blocks_html += f"""
                        <div class='time-block {type_class}'>
                            <div>
                                <span style='font-size: 0.78rem; text-transform: uppercase; letter-spacing: 0.5px; opacity: 0.6; display: block;'>{block.get('type','Work')}</span>
                                <b style='color: #f8fafc; font-size: 0.95rem;'>[{block.get('task_id')}] {block.get('name')}</b>
                            </div>
                            <div style='text-align: right;'>
                                <span class='time-slot-badge'>{block.get('time_slot')}</span>
                                <span style='display: block; font-size: 0.78rem; color: #94a3b8; margin-top: 4px;'>🕒 {block.get('duration_hours')} hrs</span>
                            </div>
                        </div>
                        """

                    if not time_blocks:
                        blocks_html = "<div style='color: #64748b; font-style: italic; padding: 10px 0;'>Rest Day / Buffer Buffer</div>"

                    st.html(
                        f"""
                        <div style='margin-bottom: 25px; border-left: 2px solid rgba(255,255,255,0.06); padding-left: 15px;'>
                            <div style='display: flex; gap: 15px; align-items: center; margin-bottom: 12px;'>
                                <h5 style='margin: 0; color: #818cf8; font-weight: 700; font-size: 1.05rem;'>{day_name} (Day {day_num})</h5>
                                <span style='font-size: 0.85rem; color: #94a3b8;'>Total Hours: <b>{total_h} hrs</b></span>
                            </div>
                            {blocks_html}
                        </div>
                        """
                    )

        with tab_export:
            st.html("<p style='color: #94a3b8; font-size: 0.95rem; margin-bottom: 20px;'>Outputs structured for consumption by other coaching subagents.</p>")
            
            # Package state payload
            coach_payload = {
                "user_experience": profile_data.get("experience_level"),
                "allocated_weekly_hours": profile_data.get("hours_per_week"),
                "scheduled_weeks": len(weekly),
                "total_scheduled_hours": sum(w.get("allocated_hours", 0) for w in weekly),
                "confidence_score": analysis.get("confidence_score"),
                "forecast": analysis.get("goal_completion_forecast"),
                "buffer_strategy": analysis.get("buffer_time_allocation")
            }

            st.json(coach_payload)
            st.html(
                """
                <div style='background-color: rgba(16, 185, 129, 0.05); border: 1px solid rgba(16, 185, 129, 0.2); border-radius: 8px; padding: 15px; margin-top: 15px;'>
                    <p style='color: #34d399; font-size: 0.85rem; margin: 0;'>🚀 <b>Subagent Integration Ready</b>: These variables are persisted in <code>st.session_state</code> and will be read automatically by the <b>AI Coach Agent</b> and the <b>Progress Tracking Agent</b>.</p>
                </div>
                """
            )

        # Dynamic Rescheduling Panel
        st.html("<div class='section-header' style='margin-top: 35px;'>⚙️ Automatic Rescheduling Suggestions</div>")
        st.html("<p style='color: #94a3b8; font-size: 0.95rem; margin-bottom: 20px;'>Apply optimized scheduler adjustments to compensate for delays, consistency blocks, or workload changes.</p>")

        suggestions = analysis.get("rescheduling_suggestions", [])
        if not suggestions:
            st.info("No suggestions available.")
        else:
            col_s1, col_s2, col_s3 = st.columns(3, gap="medium")
            col_list_s = [col_s1, col_s2, col_s3]
            
            for idx, sug in enumerate(suggestions):
                with col_list_s[idx % 3]:
                    sug_id = sug.get("id", f"sug_{idx}")
                    sug_title = sug.get("title")
                    sug_desc = sug.get("description")
                    sug_impact = sug.get("impact")

                    # Highlight applied suggestion
                    border_style = ""
                    btn_label = "Apply Suggestion ⚡"
                    is_disabled = False
                    if st.session_state.applied_suggestion and st.session_state.applied_suggestion["id"] == sug_id:
                        border_style = "border-color: #fbbf24; background: rgba(251, 191, 36, 0.05);"
                        btn_label = "Applied ✅"
                        is_disabled = True

                    st.html(
                        f"""
                        <div class='suggest-card' style='{border_style}'>
                            <div>
                                <div class='suggest-title'>{sug_title}</div>
                                <div class='suggest-desc'>{sug_desc}</div>
                                <div class='suggest-impact'>Impact: {sug_impact}</div>
                            </div>
                        </div>
                        """
                    )
                    if st.button(btn_label, key=f"btn_{sug_id}", use_container_width=True, type="secondary", disabled=is_disabled):
                        apply_rescheduling_suggestion(sug_id)
                        st.rerun()

        # Workspace Navigation Controls
        st.markdown("<div style='height: 45px;'></div>", unsafe_allow_html=True)
        col_act1, col_act2, col_act3 = st.columns([1, 1.8, 1])
        
        with col_act2:
            if st.button("Complete Scheduling & View Progress Dashboard 🎉", key="complete_scheduler_onboarding", use_container_width=True, type="primary"):
                st.balloons()
                
                # Double-check serialization details before transitioning
                st.session_state.app_phase = "progress_tracking"
                st.rerun()

            st.markdown("<div style='height: 10px;'></div>", unsafe_allow_html=True)
            if st.button("🔄 Regenerate Full Schedule", key="re_trigger_schedule_gen", use_container_width=True, type="secondary"):
                st.session_state.weekly_schedule = None
                st.session_state.daily_schedule = None
                st.session_state.schedule_analysis = None
                st.session_state.applied_suggestion = None
                st.session_state.original_weekly_schedule = None
                st.session_state.original_daily_schedule = None
                st.session_state.original_schedule_analysis = None
                st.rerun()
