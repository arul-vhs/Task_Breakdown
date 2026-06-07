import streamlit as st
import datetime
from services.gemini_service import generate_coaching_dashboard_with_gemini, chat_with_coach_agent
from agents.goal_agent import render_sidebar_api_key
from agents.progress_agent import calculate_metrics

def initialize_coach_state():
    """
    Initializes session state variables for the AI Coach Agent.
    """
    if "coach_outputs" not in st.session_state:
        st.session_state.coach_outputs = None
    if "coach_chat_history" not in st.session_state:
        st.session_state.coach_chat_history = []

def render_coach_agent():
    """
    Renders the AI Coach Agent workspace.
    """
    initialize_coach_state()

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

    # Extract all inputs from st.session_state
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

    # Calculate current progress metrics using progress_agent's function
    progress_metrics = calculate_metrics()
    weekly_reflections = st.session_state.get("weekly_reflections", []) or []

    # Get resolved API key
    api_key = render_sidebar_api_key()

    # Sidebar navigation
    st.sidebar.html("<h3 style='margin-bottom: 20px;'>Navigation</h3>")
    if st.sidebar.button("👤 View Persona Profile", key="coach_nav_profile", use_container_width=True):
        st.session_state.app_phase = "profiling"
        st.rerun()
    if st.sidebar.button("📊 Back to Progress Center", key="coach_nav_prog", use_container_width=True):
        st.session_state.app_phase = "progress_tracking"
        st.rerun()
    if st.sidebar.button("🔄 Adaptive Replanning", key="coach_nav_replan", use_container_width=True):
        st.session_state.app_phase = "replanning"
        st.rerun()
    st.sidebar.html("<hr style='border-color: rgba(255,255,255,0.1); margin: 15px 0;'>")

    # CSS Styling
    st.html(
        """
        <style>
        .coach-header {
            text-align: center;
            padding: 30px 20px;
            max-width: 800px;
            margin: 0 auto;
        }
        
        .tab-content-card {
            background: linear-gradient(135deg, rgba(30, 41, 59, 0.35) 0%, rgba(15, 23, 42, 0.55) 100%);
            border: 1px solid rgba(255, 255, 255, 0.06);
            border-radius: 16px;
            padding: 28px;
            margin-bottom: 25px;
            box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.2);
            backdrop-filter: blur(8px);
        }

        .chat-container {
            background: rgba(15, 23, 42, 0.45);
            border: 1px solid rgba(255, 255, 255, 0.08);
            border-radius: 16px;
            padding: 20px;
            margin-top: 30px;
            margin-bottom: 30px;
        }

        .chat-bubble-coach {
            background: rgba(99, 102, 241, 0.1);
            border: 1px solid rgba(99, 102, 241, 0.25);
            color: #cbd5e1;
            padding: 12px 18px;
            border-radius: 14px 14px 14px 0px;
            margin-bottom: 15px;
            line-height: 1.5;
            font-size: 0.95rem;
            max-width: 85%;
        }

        .chat-bubble-user {
            background: rgba(30, 41, 59, 0.6);
            border: 1px solid rgba(255, 255, 255, 0.1);
            color: #cbd5e1;
            padding: 12px 18px;
            border-radius: 14px 14px 0px 14px;
            margin-bottom: 15px;
            line-height: 1.5;
            font-size: 0.95rem;
            max-width: 85%;
            margin-left: auto;
        }

        .prompt-pill {
            background-color: #1e293b !important;
            border: 1px solid rgba(255, 255, 255, 0.08) !important;
            color: #818cf8 !important;
            font-size: 0.85rem !important;
            font-weight: 600 !important;
            border-radius: 20px !important;
            padding: 6px 14px !important;
            margin-right: 8px !important;
            margin-bottom: 10px !important;
            display: inline-block !important;
            cursor: pointer !important;
            transition: all 0.2s ease !important;
        }

        .prompt-pill:hover {
            background-color: #334155 !important;
            border-color: rgba(99, 102, 241, 0.3) !important;
            transform: translateY(-1px);
        }
        
        .motivation-box {
            background: linear-gradient(135deg, rgba(245, 158, 11, 0.1) 0%, rgba(236, 72, 153, 0.1) 100%);
            border: 1.5px solid rgba(245, 158, 11, 0.25);
            border-radius: 12px;
            padding: 20px;
            text-align: center;
            margin-top: 15px;
        }
        </style>
        """
    )

    # 1. HEADER SECTION
    st.html(
        """
        <div class='coach-header'>
            <span class='badge' style='background: rgba(99, 102, 241, 0.1); color: #818cf8; border: 1px solid rgba(99, 102, 241, 0.3); padding: 6px 14px; border-radius: 20px; font-size: 0.85rem; font-weight: 700; letter-spacing: 1.5px;'>PHASE 7: DYNAMIC AI COACHING AGENT</span>
            <h1 style='font-size: 2.8rem; font-weight: 800; margin-top: 15px; margin-bottom: 10px; background: linear-gradient(to right, #f8fafc, #94a3b8); -webkit-background-clip: text; -webkit-text-fill-color: transparent;'>AI Execution Coach</h1>
            <p style='color: #94a3b8; font-size: 1.15rem;'>Get custom briefings, risk profiles, habit motivations, and chat interactively with your personal execution strategist.</p>
        </div>
        """
    )

    if not api_key:
        st.warning("Please configure your Gemini API Key in the sidebar to activate the AI Coach.")
        return

    # Trigger Generation if cached outputs do not exist
    if not st.session_state.coach_outputs:
        st.html(
            """
            <div style='background: rgba(30, 41, 59, 0.25); border: 1px solid rgba(255, 255, 255, 0.05); border-radius: 12px; padding: 30px; text-align: center; max-width: 600px; margin: 20px auto;'>
                <h4 style='color: #cbd5e1; font-weight: 700; margin-bottom: 12px;'>Analyze Execution Context</h4>
                <p style='color: #94a3b8; font-size: 0.9rem; margin-bottom: 20px;'>Your coach needs to run an audit of your goal context, blueprint, schedules, and active progress telemetry to formulate briefings.</p>
            </div>
            """
        )
        col1, col2, col3 = st.columns([1, 1.2, 1])
        with col2:
            if st.button("Generate Coaching Briefings 🧠", use_container_width=True, type="primary"):
                with st.spinner("AI Coach is analyzing progress metrics, schedules, and consistency vectors..."):
                    try:
                        brief_data = generate_coaching_dashboard_with_gemini(
                            profile_data,
                            goal_context,
                            selected_strategy,
                            readiness_results,
                            roadmap_dag_data,
                            schedule_data,
                            progress_metrics,
                            weekly_reflections,
                            api_key
                        )
                        st.session_state.coach_outputs = brief_data
                        st.rerun()
                    except Exception as e:
                        st.error(f"Coaching Briefing Generation Failed: {str(e)}")
        return

    # Cache load
    outputs = st.session_state.coach_outputs

    # Create Tabs for Coaching Categories
    tab_briefing, tab_summary, tab_risks, tab_connectors = st.tabs([
        "🎯 Daily Briefing & Actions",
        "📊 Weekly Summary & Analytics",
        "🚨 Risk & Motivation",
        "🔌 Agent Connectors"
    ])

    # ==================== TAB 1: BRIEFING & ACTIONS ====================
    with tab_briefing:
        st.html(
            """
            <div class='tab-content-card' style='border-top: 4px solid #6366f1;'>
                <h3 style='margin: 0 0 15px 0; color: #818cf8; font-weight: 700;'>⚡ Today's Execution Briefing</h3>
            </div>
            """
        )
        st.markdown(outputs.get("daily_briefing", ""))
        
        st.html(
            """
            <div class='tab-content-card' style='border-top: 4px solid #10b981; margin-top: 25px;'>
                <h3 style='margin: 0 0 15px 0; color: #10b981; font-weight: 700;'>📋 Recommended Next Actions</h3>
            </div>
            """
        )
        st.markdown(outputs.get("recommended_actions", ""))

    # ==================== TAB 2: SUMMARY & PROGRESS ====================
    with tab_summary:
        st.html(
            """
            <div class='tab-content-card' style='border-top: 4px solid #a855f7;'>
                <h3 style='margin: 0 0 15px 0; color: #c084fc; font-weight: 700;'>📅 Weekly Sprint Summary</h3>
            </div>
            """
        )
        st.markdown(outputs.get("weekly_summary", ""))

        st.html(
            """
            <div class='tab-content-card' style='border-top: 4px solid #818cf8; margin-top: 25px;'>
                <h3 style='margin: 0 0 15px 0; color: #818cf8; font-weight: 700;'>📊 Telemetric Progress Analysis</h3>
            </div>
            """
        )
        st.markdown(outputs.get("progress_analysis", ""))

    # ==================== TAB 3: RISK & MOTIVATION ====================
    with tab_risks:
        st.html(
            """
            <div class='tab-content-card' style='border-top: 4px solid #f87171;'>
                <h3 style='margin: 0 0 15px 0; color: #f87171; font-weight: 700;'>🚨 Bottlenecks & Risk Assessment</h3>
            </div>
            """
        )
        st.markdown(outputs.get("risk_assessment", ""))

        st.html(
            f"""
            <div class='motivation-box'>
                <div style='font-size: 1.8rem; margin-bottom: 8px;'>🎯</div>
                <h4 style='margin: 0 0 8px 0; color: #fbbf24; font-weight: bold;'>Execution Motivation Boost</h4>
                <div style='color: #cbd5e1; font-size: 1.02rem; line-height: 1.5; font-style: italic;'>
                    "{outputs.get("motivation_message", "Focus on your goals and take consistency steps daily.")}"
                </div>
            </div>
            """
        )

    # ==================== TAB 4: AGENT CONNECTORS ====================
    with tab_connectors:
        st.html(
            """
            <div class='tab-content-card' style='border-top: 4px solid #cbd5e1;'>
                <h3 style='margin: 0 0 8px 0; color: #cbd5e1; font-weight: 700;'>🔌 Downstream Agents Interfacing</h3>
                <p style='color: #94a3b8; font-size: 0.88rem; margin: 0 0 20px 0;'>Payloads structured precisely for ingestion by the Adaptive Replanning and Memory agents.</p>
            </div>
            """
        )
        
        col_c1, col_c2 = st.columns(2)
        with col_c1:
            st.html("<h5 style='color: #a855f7; font-weight: bold; margin-bottom: 10px;'>Adaptive Replanning Agent Payload</h5>")
            st.json(outputs.get("adaptive_replanning_payload", {}))
        with col_c2:
            st.html("<h5 style='color: #10b981; font-weight: bold; margin-bottom: 10px;'>Memory Agent Payload</h5>")
            st.json(outputs.get("memory_payload", {}))

    # Force recalculate button
    st.markdown("<div style='height: 15px;'></div>", unsafe_allow_html=True)
    if st.button("🔄 Regenerate Coach Briefings", key="btn_regen_briefing", type="secondary"):
        st.session_state.coach_outputs = None
        st.rerun()

    # ==================== INTERACTIVE COACH CHAT ====================
    st.html("<hr style='border-color: rgba(255,255,255,0.08); margin: 35px 0;'>")
    st.html(
        """
        <div style='margin-bottom: 15px;'>
            <h3 style='color: #818cf8; font-weight: 800; font-size: 1.8rem; margin: 0;'>🧠 Coach Chat Consultation</h3>
            <p style='color: #94a3b8; font-size: 0.95rem; margin: 3px 0 0 0;'>Consult your coach on deadlines, bottlenecks, strategy execution, or routine optimization.</p>
        </div>
        """
    )

    # Chat history rendering container
    chat_container_div = st.container()
    with chat_container_div:
        if not st.session_state.coach_chat_history:
            st.html(
                """
                <div style='color: #64748b; font-style: italic; text-align: center; padding: 30px;'>
                    No dialogue started yet. Choose a template query below or write your own question to start the consultation.
                </div>
                """
            )
        else:
            for msg in st.session_state.coach_chat_history:
                bubble_class = "chat-bubble-user" if msg["role"] == "user" else "chat-bubble-coach"
                prefix = "👤 **You**" if msg["role"] == "user" else "🧠 **Coach**"
                st.html(
                    f"""
                    <div class='{bubble_class}'>
                        <div style='font-size: 0.78rem; opacity: 0.7; margin-bottom: 4px; font-weight: bold;'>{prefix}</div>
                        <div style='margin: 0;'>{msg['content']}</div>
                    </div>
                    """
                )

    # Suggested Prompts Row
    st.html("<span style='font-size: 0.8rem; font-weight: 700; color: #64748b; text-transform: uppercase; margin-bottom: 10px; display: block;'>Recommended Queries</span>")
    
    col_q1, col_q2, col_q3, col_q4 = st.columns(4)
    suggested_prompts = [
        "What should I do today?",
        "Why am I behind?",
        "Can I finish on time?",
        "What should I focus on next?"
    ]
    col_list = [col_q1, col_q2, col_q3, col_q4]

    # Helper function to submit chat message
    def submit_chat_message(prompt_text):
        if not prompt_text.strip():
            return
        
        # Append User Message
        st.session_state.coach_chat_history.append({"role": "user", "content": prompt_text})
        
        # Execute API call with a spinner
        with st.spinner("AI Execution Coach is thinking..."):
            try:
                coach_response = chat_with_coach_agent(
                    profile_data,
                    goal_context,
                    selected_strategy,
                    readiness_results,
                    roadmap_dag_data,
                    schedule_data,
                    progress_metrics,
                    weekly_reflections,
                    st.session_state.coach_chat_history,
                    api_key
                )
                # Append Coach Message
                st.session_state.coach_chat_history.append({"role": "coach", "content": coach_response})
            except Exception as e:
                st.session_state.coach_chat_history.append({"role": "coach", "content": f"⚠️ Coaching connection failed: {str(e)}"})
        st.rerun()

    for idx, prompt in enumerate(suggested_prompts):
        with col_list[idx]:
            if st.button(prompt, key=f"btn_sug_prompt_{idx}", use_container_width=True, type="secondary"):
                submit_chat_message(prompt)

    # Chat Input Box
    user_query = st.chat_input("Ask your coach a custom question...")
    if user_query:
        submit_chat_message(user_query)

    # Bottom Actions / clear history
    if st.session_state.coach_chat_history:
        if st.button("🧹 Clear Chat History", type="secondary"):
            st.session_state.coach_chat_history = []
            st.rerun()
