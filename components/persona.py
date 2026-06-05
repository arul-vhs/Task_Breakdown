import streamlit as st
from utils.persona_engine import generate_persona

def render_results_page():
    """
    Renders the professional profile summary dashboard and AI execution persona card.
    """
    # Retrieve user input and generate persona
    profile = st.session_state.profile_data
    persona = generate_persona(profile)
    
    # Header Section
    st.html(
        """
        <div style='text-align: center; margin-bottom: 40px; margin-top: 10px;'>
            <span class='badge' style='background: linear-gradient(135deg, #10b981, #059669); color: white; padding: 6px 14px; border-radius: 20px; font-size: 0.85rem; font-weight: 700; letter-spacing: 1px;'>PROFILING COMPLETE</span>
            <h1 class='results-header' style='font-size: 2.8rem; font-weight: 800; margin-top: 15px; margin-bottom: 10px; background: linear-gradient(to right, #f8fafc, #94a3b8); -webkit-background-clip: text; -webkit-text-fill-color: transparent;'>Your Execution Blueprint</h1>
            <p style='color: #94a3b8; font-size: 1.15rem; max-width: 600px; margin: 0 auto;'>Based on your working style and motivation drivers, we have constructed your goal execution archetype.</p>
        </div>
        """
    )
    
    # Grid Layout: Left Column = Profile Summary, Right Column = Persona Card
    col1, col2 = st.columns([1, 1.2], gap="large")
    
    with col1:
        st.html(
            f"""
            <div class='results-card'>
                <div style='display: flex; align-items: center; margin-bottom: 25px;'>
                    <span style='font-size: 1.5rem; margin-right: 10px;'>📋</span>
                    <h3 style='margin: 0; font-size: 1.3rem; font-weight: 700; color: #f8fafc;'>Profile Summary</h3>
                </div>
                
                <div class='summary-row'>
                    <div class='summary-label'>User Type</div>
                    <div class='summary-value'>{profile.get('user_type', 'N/A')}</div>
                </div>
                
                <div class='summary-row'>
                    <div class='summary-label'>Experience Level</div>
                    <div class='summary-value-badge exp-{profile.get('experience_level', 'Beginner').lower()}'>{profile.get('experience_level', 'N/A')}</div>
                </div>
                
                <div class='summary-row'>
                    <div class='summary-label'>Weekly Dedication</div>
                    <div class='summary-value' style='font-weight: 700; color: #818cf8;'>{profile.get('hours_per_week', 0)} Hours</div>
                </div>
                
                <div class='summary-row'>
                    <div class='summary-label'>Work Style</div>
                    <div class='summary-value'>{profile.get('work_style', 'N/A')}</div>
                </div>
                
                <div class='summary-row'>
                    <div class='summary-label'>Motivation Style</div>
                    <div class='summary-value'>{profile.get('motivation_style', 'N/A')}</div>
                </div>
                
                <div class='summary-row' style='border-bottom: none;'>
                    <div class='summary-label'>Biggest Challenge</div>
                    <div class='summary-value' style='color: #f87171; font-weight: 500;'>⚠️ {profile.get('biggest_challenge', 'N/A')}</div>
                </div>
            </div>
            """
        )
        
    with col2:
        # Determine theme color based on experience level
        experience = profile.get('experience_level', 'Beginner')
        if experience == "Beginner":
            theme_color = "#6366f1"  # Indigo
            glow_class = "glow-beginner"
        elif experience == "Intermediate":
            theme_color = "#a855f7"  # Purple
            glow_class = "glow-intermediate"
        else:
            theme_color = "#ec4899"  # Pink/Rose
            glow_class = "glow-advanced"
            
        st.html(
            f"""
            <div class='persona-card {glow_class}' style='border-top: 5px solid {theme_color};'>
                <div style='display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px;'>
                    <div class='persona-badge' style='background: {theme_color}18; color: {theme_color}; border: 1px solid {theme_color}33;'>AI Execution Persona</div>
                    <span style='font-size: 1.8rem;'>🧠</span>
                </div>
                
                <h2 class='persona-name' style='font-size: 2.2rem; font-weight: 800; color: #f8fafc; margin-bottom: 25px; margin-top: 0;'>{persona['name']}</h2>
                
                <div style='margin-bottom: 20px;'>
                    <div class='section-label'>🔥 Core Strength</div>
                    <div class='section-text'>{persona['strength']}</div>
                </div>
                
                <div style='margin-bottom: 25px;'>
                    <div class='section-label'>⚠️ Primary Challenge</div>
                    <div class='section-text'>{persona['challenge']}</div>
                </div>
                
                <div class='strategy-box' style='border-left: 3px solid {theme_color}; background-color: #0f172a; padding: 15px 20px; border-radius: 0 10px 10px 0;'>
                    <div class='section-label' style='color: {theme_color}; font-weight: 700; font-size: 0.8rem; text-transform: uppercase; letter-spacing: 1px; margin-bottom: 5px;'>💡 Recommended Strategy</div>
                    <div class='strategy-text' style='color: #f8fafc; font-size: 1.05rem; font-weight: 500;'>{persona['strategy']}</div>
                </div>
            </div>
            """
        )
        
    # Spacer
    st.markdown("<div style='height: 40px;'></div>", unsafe_allow_html=True)
    
    # Extra Value: Let the user know what to do next
    st.html(
        """
        <div class='instruction-container' style='background-color: #1e293b; border: 1px solid #334155; padding: 25px; border-radius: 12px; margin-bottom: 30px; text-align: center;'>
            <h4 style='margin: 0 0 10px 0; font-weight: 700; color: #f8fafc;'>Your Archetype is Secured</h4>
            <p style='margin: 0; color: #94a3b8; font-size: 0.95rem;'>Now, let's feed your execution coach a specific goal. We will customize your strategy, skills list, and risk plan based on your persona.</p>
        </div>
        """
    )
    
    # Control Row: Back to Wizard Button & Proceed Button
    col_reset, col_space, col_proceed = st.columns([1, 0.5, 1.5])
    with col_reset:
        if st.button("🔄 Restart Profiling", use_container_width=True):
            st.session_state.onboarding_started = False
            st.session_state.completed = False
            st.session_state.current_step = 1
            st.session_state.profile_data = {}
            st.rerun()
            
    with col_proceed:
        if st.button("Proceed to Goal Intake 🚀", use_container_width=True, type="primary"):
            st.session_state.app_phase = "goal_intake"
            st.rerun()
