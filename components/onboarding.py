import streamlit as st

# Define onboarding wizard steps configuration
STEPS = {
    1: {
        "title": "User Type",
        "question": "Which best describes you?",
        "key": "user_type",
        "options": ["Student", "Professional", "Founder", "Developer", "Creator", "Learner"],
        "type": "radio",
        "icon": "👤"
    },
    2: {
        "title": "Experience Level",
        "question": "What is your goal execution experience level?",
        "key": "experience_level",
        "options": ["Beginner", "Intermediate", "Advanced"],
        "type": "radio",
        "icon": "⚡"
    },
    3: {
        "title": "Available Time",
        "question": "How many hours can you realistically dedicate each week?",
        "key": "hours_per_week",
        "min_value": 1,
        "max_value": 40,
        "default": 10,
        "type": "slider",
        "icon": "⏳"
    },
    4: {
        "title": "Work Style",
        "question": "How do you prefer to work?",
        "key": "work_style",
        "options": ["Quick Wins", "Balanced Progress", "Deep Focus"],
        "type": "radio",
        "icon": "⚙️"
    },
    5: {
        "title": "Motivation Style",
        "question": "What motivates you the most?",
        "key": "motivation_style",
        "options": ["Achievements", "Progress", "Learning", "Money", "Impact"],
        "type": "radio",
        "icon": "🎯"
    },
    6: {
        "title": "Biggest Challenge",
        "question": "What usually prevents you from completing goals?",
        "key": "biggest_challenge",
        "options": ["Lack of Time", "Overwhelmed", "Lose Motivation", "Don't Know Where To Start", "Inconsistent"],
        "type": "radio",
        "icon": "⚠️"
    }
}

def render_sidebar_progress():
    """
    Renders step-by-step progress list in the sidebar.
    Shows checked, active, and upcoming steps with appropriate styling.
    """
    st.sidebar.html("<h3 style='margin-bottom: 20px;'>Onboarding Progress</h3>")
    
    current = st.session_state.current_step
    
    for step_num, step_info in STEPS.items():
        title = step_info["title"]
        icon = step_info["icon"]
        
        if step_num < current:
            # Completed step
            st.sidebar.html(
                f"<div class='sidebar-step completed-step'>✅ {icon} <b>{title}</b></div>"
            )
        elif step_num == current:
            # Active step
            st.sidebar.html(
                f"<div class='sidebar-step active-step'>👉 {icon} <b>{title}</b></div>"
            )
        else:
            # Upcoming step
            st.sidebar.html(
                f"<div class='sidebar-step upcoming-step'>⚪ {icon} <span style='opacity: 0.6;'>{title}</span></div>"
            )
            
    # Calculate percentage
    total_steps = len(STEPS)
    pct = int((current / total_steps) * 100)
    
    st.sidebar.html("<hr style='border-color: rgba(255,255,255,0.1); margin: 15px 0;'>")
    st.sidebar.html(f"<p style='font-size: 0.9rem; margin-bottom: 5px;'>Profile Completion: <b>{pct}%</b></p>")
    st.sidebar.progress(current / total_steps)

def render_onboarding_wizard():
    """
    Renders the active question and navigation buttons in the main panel.
    """
    current = st.session_state.current_step
    step = STEPS[current]
    
    # Progress indicator at the top of the main panel
    total_steps = len(STEPS)
    pct = int((current / total_steps) * 100)
    
    st.html(
        f"""
        <div style='display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px;'>
            <span style='font-size: 0.9rem; text-transform: uppercase; letter-spacing: 1.5px; opacity: 0.7;'>Step {current} of {total_steps}</span>
            <span class='badge' style='background: linear-gradient(135deg, #6366f1, #a855f7); color: white; padding: 4px 10px; border-radius: 20px; font-size: 0.8rem; font-weight: bold;'>{pct}% Complete</span>
        </div>
        """
    )
    
    # Card wrapper for the question
    st.html(
        f"""
        <div class='question-card'>
            <h2 style='font-weight: 700; margin-bottom: 5px; color: #f8fafc;'>{step['icon']} {step['title']}</h2>
            <p style='color: #94a3b8; font-size: 1.1rem; margin-bottom: 25px;'>{step['question']}</p>
        </div>
        """
    )
    
    # Render component inputs and preserve session state values
    key = step["key"]
    saved_val = st.session_state.profile_data.get(key)
    
    # Render actual Streamlit elements centered or wrapped
    with st.container():
        st.write("")  # spacing
        if step["type"] == "radio":
            options = step["options"]
            index = 0
            if saved_val in options:
                index = options.index(saved_val)
            
            # Use custom streamlit radio selection
            val = st.radio(
                label=step["question"],
                options=options,
                index=index,
                label_visibility="collapsed"
            )
            st.session_state.profile_data[key] = val
            
        elif step["type"] == "slider":
            val = st.slider(
                label=step["question"],
                min_value=step["min_value"],
                max_value=step["max_value"],
                value=saved_val if saved_val is not None else step["default"],
                step=1,
                label_visibility="collapsed"
            )
            st.session_state.profile_data[key] = val
            st.html(
                f"""
                <div style='text-align: center; margin-top: 10px;'>
                    <span style='font-size: 2.2rem; font-weight: 800; color: #818cf8;'>{val}</span>
                    <span style='font-size: 1rem; color: #94a3b8;'>hours per week</span>
                </div>
                """
            )
            
    # Spacer
    st.markdown("<div style='height: 40px;'></div>", unsafe_allow_html=True)
    
    # Navigation Buttons
    col1, col2 = st.columns([1, 1])
    
    with col1:
        if current > 1:
            if st.button("← Back", use_container_width=True, type="secondary"):
                st.session_state.current_step -= 1
                st.rerun()
                
    with col2:
        if current < total_steps:
            if st.button("Next →", use_container_width=True, type="primary"):
                st.session_state.current_step += 1
                st.rerun()
        else:
            if st.button("Generate Execution Profile 🎉", use_container_width=True, type="primary"):
                st.session_state.completed = True
                st.rerun()
