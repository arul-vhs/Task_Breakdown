import streamlit as st
from services.gemini_service import generate_strategies_with_gemini
from agents.goal_agent import render_sidebar_api_key
from utils.persona_engine import generate_persona

def initialize_strategy_state():
    """
    Initializes session state variables for strategy generation.
    """
    if "strategies_data" not in st.session_state:
        st.session_state.strategies_data = None
    if "selected_strategy_key" not in st.session_state:
        st.session_state.selected_strategy_key = None
    if "selected_strategy_data" not in st.session_state:
        st.session_state.selected_strategy_data = None

def render_strategy_agent():
    """
    Renders the Strategy Generator Agent UI and logic.
    """
    initialize_strategy_state()
    
    # Check if goal context exists
    if "goal_context" not in st.session_state or not st.session_state.goal_context:
        st.html(
            """
            <div style='text-align: center; padding: 40px;'>
                <h3 style='color: #f87171;'>⚠️ No Goal Context Found</h3>
                <p style='color: #94a3b8;'>Please complete the Goal Intake phase first before generating strategies.</p>
            </div>
            """
        )
        if st.button("Go to Goal Intake 🎯", type="primary"):
            st.session_state.app_phase = "goal_intake"
            st.rerun()
        return

    goal_context = st.session_state.goal_context
    profile_data = st.session_state.profile_data
    persona = generate_persona(profile_data) if profile_data else {
        "name": "Consistent Explorer",
        "strength": "High curiosity & adaptability",
        "challenge": "Maintaining habit consistency",
        "strategy": "Micro-habits planning"
    }
    
    # Sidebar navigation option
    st.sidebar.html("<h3 style='margin-bottom: 20px;'>Navigation</h3>")
    if st.sidebar.button("👤 View Persona Profile", key="nav_view_profile", use_container_width=True):
        st.session_state.app_phase = "profiling"
        st.rerun()
    if st.sidebar.button("🎯 Back to Goal Intake", key="nav_back_goal", use_container_width=True):
        st.session_state.app_phase = "goal_intake"
        st.rerun()
    st.sidebar.html("<hr style='border-color: rgba(255,255,255,0.1); margin: 15px 0;'>")

    # Resolve API Key
    api_key = render_sidebar_api_key()

    # Premium CSS injection specifically for strategy cards
    st.html(
        """
        <style>
        .strategy-card {
            background: rgba(30, 41, 59, 0.45);
            border: 1px solid rgba(255, 255, 255, 0.08);
            border-radius: 16px;
            padding: 25px;
            box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.3);
            backdrop-filter: blur(8px);
            height: 480px;
            display: flex;
            flex-direction: column;
            justify-content: space-between;
            transition: all 0.3s ease;
            position: relative;
            overflow: hidden;
            margin-bottom: 15px;
        }
        
        .strategy-card:hover {
            transform: translateY(-5px);
            border: 1px solid rgba(255, 255, 255, 0.18);
        }
        
        .strategy-card-recommended {
            border: 2px solid #6366f1 !important;
            background: rgba(99, 102, 241, 0.06);
        }
        
        .strategy-card-selected {
            border: 2px solid #10b981 !important;
            background: rgba(16, 185, 129, 0.06);
        }
        
        .badge-recommended {
            background: linear-gradient(135deg, #6366f1, #a855f7);
            color: white;
            padding: 4px 12px;
            border-radius: 20px;
            font-size: 0.72rem;
            font-weight: 700;
            text-transform: uppercase;
            letter-spacing: 1px;
            display: inline-block;
            margin-bottom: 12px;
        }
        
        .badge-selected {
            background: linear-gradient(135deg, #10b981, #059669);
            color: white;
            padding: 4px 12px;
            border-radius: 20px;
            font-size: 0.72rem;
            font-weight: 700;
            text-transform: uppercase;
            letter-spacing: 1px;
            display: inline-block;
            margin-bottom: 12px;
        }
        
        .badge-normal {
            background: rgba(255, 255, 255, 0.08);
            color: #cbd5e1;
            padding: 4px 12px;
            border-radius: 20px;
            font-size: 0.72rem;
            font-weight: 700;
            text-transform: uppercase;
            letter-spacing: 1px;
            display: inline-block;
            margin-bottom: 12px;
            border: 1px solid rgba(255, 255, 255, 0.1);
        }
        
        .glow-mvp {
            box-shadow: 0 0 25px rgba(16, 185, 129, 0.08);
        }
        .glow-growth {
            box-shadow: 0 0 25px rgba(168, 85, 247, 0.08);
        }
        .glow-scale {
            box-shadow: 0 0 25px rgba(236, 72, 153, 0.08);
        }
        
        .strategy-title {
            font-size: 1.35rem;
            font-weight: 800;
            margin-top: 0;
            margin-bottom: 8px;
            color: #f8fafc;
        }
        
        .strategy-desc {
            color: #94a3b8;
            font-size: 0.88rem;
            line-height: 1.45;
            margin-bottom: 15px;
            height: 70px;
            overflow: hidden;
            text-overflow: ellipsis;
        }
        
        .strategy-meta {
            background-color: rgba(15, 23, 42, 0.35);
            border-radius: 10px;
            padding: 10px 14px;
            margin-bottom: 15px;
            font-size: 0.85rem;
            border: 1px solid rgba(255, 255, 255, 0.04);
        }
        
        .strategy-meta-item {
            display: flex;
            justify-content: space-between;
            margin-bottom: 5px;
        }
        
        .strategy-meta-item:last-child {
            margin-bottom: 0;
        }
        
        .strategy-meta-label {
            color: #64748b;
            font-weight: 500;
        }
        
        .strategy-meta-value {
            color: #f8fafc;
            font-weight: 600;
        }
        
        .strategy-list-title {
            font-size: 0.72rem;
            text-transform: uppercase;
            letter-spacing: 1.2px;
            color: #475569;
            font-weight: 700;
            margin-bottom: 6px;
        }
        
        .strategy-list {
            margin: 0 0 10px 0;
            padding-left: 0;
            list-style-type: none;
            overflow-y: auto;
            height: 140px;
        }
        
        .strategy-list li {
            font-size: 0.85rem;
            color: #cbd5e1;
            margin-bottom: 5px;
            position: relative;
            padding-left: 20px;
            line-height: 1.35;
        }
        
        .strategy-list-pro li::before {
            content: "✓";
            position: absolute;
            left: 0;
            color: #10b981;
            font-weight: 800;
        }
        
        .strategy-list-con li::before {
            content: "✗";
            position: absolute;
            left: 0;
            color: #f87171;
            font-weight: 800;
        }
        </style>
        """
    )

    # 1. INITIAL START PAGE (No strategies loaded yet)
    if not st.session_state.strategies_data:
        st.html(
            f"""
            <div style='max-width: 800px; margin: 0 auto; padding: 20px 0;'>
                <span class='badge' style='background: rgba(99, 102, 241, 0.1); color: #818cf8; border: 1px solid rgba(99, 102, 241, 0.3); padding: 6px 14px; border-radius: 20px; font-size: 0.85rem; font-weight: 700; letter-spacing: 1.5px;'>PHASE 3: STRATEGY GENERATOR</span>
                <h1 style='font-size: 2.8rem; font-weight: 800; margin-top: 15px; margin-bottom: 10px; background: linear-gradient(to right, #f8fafc, #94a3b8); -webkit-background-clip: text; -webkit-text-fill-color: transparent;'>Design your execution strategy</h1>
                <p style='color: #94a3b8; font-size: 1.15rem; margin-bottom: 30px;'>Your coach will evaluate your goal context, schedule, and execution archetype to build exactly 3 personalized execution options: Fast MVP, Balanced Growth, and Ambitious Scale.</p>
            </div>
            """
        )
        
        # Display small context overview
        st.html(
            f"""
            <div class='question-card' style='border-left: 4px solid #6366f1; max-width: 800px; margin: 0 auto 30px auto;'>
                <h4 style='margin: 0 0 10px 0; color: #f8fafc;'>Goal Context Ingested</h4>
                <p style='margin: 0; color: #94a3b8; font-size: 0.95rem;'><b>Goal:</b> "{goal_context['goal']}"</p>
                <p style='margin: 5px 0 0 0; color: #94a3b8; font-size: 0.95rem;'><b>Archetype:</b> {persona['name']} ({profile_data.get('experience_level')} • {profile_data.get('hours_per_week')} hrs/week)</p>
            </div>
            """
        )

        if not api_key:
            st.warning("Please configure your Gemini API Key in the sidebar before proceeding.")

        col1, col2, col3 = st.columns([1, 1.2, 1])
        with col2:
            if st.button("Generate Execution Strategies ⚡", use_container_width=True, type="primary", disabled=not api_key):
                with st.spinner("Gemini is formulating three highly customized execution strategies..."):
                    try:
                        result = generate_strategies_with_gemini(goal_context, profile_data, persona, api_key)
                        
                        # Store in state
                        st.session_state.strategies_data = result
                        
                        # Set default selected strategy to recommended one
                        rec_key = result.get("recommended_strategy_key", "balanced_growth")
                        st.session_state.selected_strategy_key = rec_key
                        
                        # Find and set selected strategy data
                        for s in result.get("strategies", []):
                            if s.get("key") == rec_key:
                                st.session_state.selected_strategy_data = s
                                break
                                
                        st.rerun()
                    except Exception as e:
                        st.error(f"Failed to generate strategies: {str(e)}")

    # 2. DISPLAY STRATEGIES & REVIEWS
    else:
        result = st.session_state.strategies_data
        strategies = result.get("strategies", [])
        recommended_key = result.get("recommended_strategy_key")
        rec_explanation = result.get("recommendation_explanation", "")
        
        st.html(
            f"""
            <div style='margin-bottom: 30px; margin-top: 10px;'>
                <span style='font-size: 0.9rem; text-transform: uppercase; letter-spacing: 1.5px; opacity: 0.7; color: #818cf8;'>Strategies Compiled</span>
                <h2 style='font-size: 2.2rem; font-weight: 800; color: #f8fafc; margin-top: 10px; margin-bottom: 5px;'>Pick Your Execution Strategy</h2>
                <p style='color: #94a3b8; font-size: 1rem;'>Review the personalized paths below and choose the one that matches your timeline and effort goals.</p>
            </div>
            """
        )
        
        # 3 Column Layout for strategies
        col_mvp, col_growth, col_scale = st.columns([1, 1, 1], gap="medium")
        
        # Render cards
        for s in strategies:
            key = s.get("key")
            name = s.get("name")
            desc = s.get("description")
            pros = s.get("pros", [])
            cons = s.get("cons", [])
            duration = s.get("estimated_duration")
            effort = s.get("effort_level")
            
            # Identify card attributes
            is_recommended = (key == recommended_key)
            is_selected = (key == st.session_state.selected_strategy_key)
            
            # Card styling selector classes
            card_class = "strategy-card"
            if is_selected:
                card_class += " strategy-card-selected"
            elif is_recommended:
                card_class += " strategy-card-recommended"
                
            glow_class = "glow-growth"
            theme_color = "#a855f7"
            if key == "fast_mvp":
                glow_class = "glow-mvp"
                theme_color = "#10b981"
            elif key == "ambitious_scale":
                glow_class = "glow-scale"
                theme_color = "#ec4899"
                
            badge_html = ""
            if is_selected:
                badge_html = "<span class='badge-selected'>Selected ✅</span>"
            elif is_recommended:
                badge_html = "<span class='badge-recommended'>Recommended ⭐</span>"
            else:
                badge_html = "<span class='badge-normal'>Option</span>"
                
            pros_html = "".join([f"<li>{p}</li>" for p in pros])
            cons_html = "".join([f"<li>{c}</li>" for c in cons])
            
            # Find which column to render in
            col_target = col_growth
            if key == "fast_mvp":
                col_target = col_mvp
            elif key == "ambitious_scale":
                col_target = col_scale
                
            with col_target:
                st.html(
                    f"""
                    <div class='{card_class} {glow_class}'>
                        <div>
                            {badge_html}
                            <h3 class='strategy-title' style='border-bottom: 2px solid {theme_color}33; padding-bottom: 8px;'>{name}</h3>
                            <p class='strategy-desc'>{desc}</p>
                            
                            <div class='strategy-meta'>
                                <div class='strategy-meta-item'>
                                    <span class='strategy-meta-label'>Estimated Duration</span>
                                    <span class='strategy-meta-value' style='color: {theme_color};'>{duration}</span>
                                </div>
                                <div class='strategy-meta-item'>
                                    <span class='strategy-meta-label'>Effort Intensity</span>
                                    <span class='strategy-meta-value'>{effort}</span>
                                </div>
                            </div>
                        </div>
                        
                        <div>
                            <div class='strategy-list-title'>Pros & Trade-offs</div>
                            <ul class='strategy-list strategy-list-pro' style='height: 70px; margin-bottom: 5px;'>
                                {pros_html}
                            </ul>
                            <ul class='strategy-list strategy-list-con' style='height: 70px;'>
                                {cons_html}
                            </ul>
                        </div>
                    </div>
                    """
                )
                
                # Selection Button
                if is_selected:
                    st.button("✓ Active Selection", key=f"sel_{key}", use_container_width=True, disabled=True)
                else:
                    if st.button(f"Select {name}", key=f"sel_{key}", use_container_width=True, type="secondary"):
                        st.session_state.selected_strategy_key = key
                        st.session_state.selected_strategy_data = s
                        st.rerun()

        # Spacer
        st.markdown("<div style='height: 30px;'></div>", unsafe_allow_html=True)

        # 3. RECOMMENDATION ANALYSIS SECTION
        rec_name = "N/A"
        for s in strategies:
            if s.get("key") == recommended_key:
                rec_name = s.get("name")
                break
                
        st.html(
            f"""
            <div class='persona-card glow-beginner' style='border-top: 5px solid #6366f1; max-width: 900px; margin: 0 auto 30px auto;'>
                <div style='display: flex; justify-content: space-between; align-items: center; margin-bottom: 15px;'>
                    <div class='persona-badge' style='background: rgba(99,102,241,0.1); color: #818cf8; border: 1px solid rgba(99,102,241,0.3);'>Coach Recommendation Analysis</div>
                    <span style='font-size: 0.95rem; font-weight: 700; color: #818cf8;'>Recommended Option: {rec_name}</span>
                </div>
                
                <h3 style='color: #f8fafc; font-size: 1.3rem; font-weight: 700; margin-top: 0; margin-bottom: 12px;'>Why this strategy is recommended:</h3>
                <p style='color: #cbd5e1; font-size: 1rem; line-height: 1.6; margin-bottom: 0;'>
                    {rec_explanation}
                </p>
            </div>
            """
        )
        
        # Action Control Panel
        col_ctl1, col_ctl2, col_ctl3 = st.columns([1, 1.5, 1])
        with col_ctl2:
            if st.button("Proceed to Strategy Validation 🚀", use_container_width=True, type="primary"):
                # Complete Phase
                # Proceed to Strategy Validation Agent
                st.session_state.app_phase = "strategy_validation"
                st.rerun()
                
            if st.button("🔄 Regenerate Strategies", use_container_width=True, type="secondary"):
                # Clear and regenerate
                st.session_state.strategies_data = None
                st.session_state.selected_strategy_key = None
                st.session_state.selected_strategy_data = None
                st.rerun()
