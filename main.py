import streamlit as st
import textwrap
from components.onboarding import render_onboarding_wizard, render_sidebar_progress
from components.persona import render_results_page
from agents.goal_agent import render_goal_intake_module

# Set page configuration
st.set_page_config(
    page_title="Agent OnboardX - AI Execution Coach",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom premium CSS injection
st.html(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700;800&family=Inter:wght@300;400;500;600;700&display=swap');
    
    /* Enforce modern geometric font family */
    html, body, [class*="css"], .stMarkdown, p, h1, h2, h3, h4, h5, h6, label, div, span, button, input {
        font-family: 'Outfit', 'Inter', sans-serif !important;
    }
    
    /* Main container styling */
    .stApp {
        background-color: #0b0f19;
        color: #f8fafc;
    }
    
    /* Header sidebar logo styling */
    .sidebar .sidebar-content {
        background-color: #0f172a;
    }
    
    /* Landing page styles */
    .hero-container {
        text-align: center;
        padding: 80px 20px;
        max-width: 800px;
        margin: 0 auto;
    }
    
    .hero-title {
        font-size: 4rem;
        font-weight: 800;
        margin-bottom: 15px;
        background: linear-gradient(135deg, #e0e7ff 0%, #a5b4fc 50%, #6366f1 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        letter-spacing: -1px;
    }
    
    .hero-subtitle {
        font-size: 1.8rem;
        font-weight: 600;
        color: #818cf8;
        margin-bottom: 25px;
        letter-spacing: -0.5px;
    }
    
    .hero-text {
        font-size: 1.2rem;
        color: #94a3b8;
        margin-bottom: 40px;
        line-height: 1.6;
    }
    
    /* Custom Card Containers */
    .question-card {
        background: rgba(30, 41, 59, 0.45);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 16px;
        padding: 30px;
        box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.3);
        backdrop-filter: blur(8px);
        margin-bottom: 25px;
    }
    
    .results-card {
        background: rgba(30, 41, 59, 0.4);
        border: 1px solid rgba(255, 255, 255, 0.06);
        border-radius: 16px;
        padding: 30px;
        box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.25);
        backdrop-filter: blur(8px);
        height: 100%;
    }
    
    .persona-card {
        background: linear-gradient(135deg, rgba(15, 23, 42, 0.85) 0%, rgba(30, 41, 59, 0.55) 100%);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 16px;
        padding: 35px;
        box-shadow: 0 12px 40px 0 rgba(0, 0, 0, 0.4);
        backdrop-filter: blur(10px);
        height: 100%;
        position: relative;
        overflow: hidden;
    }
    
    /* Persona Card Glow effects */
    .glow-beginner {
        box-shadow: 0 0 30px rgba(99, 102, 241, 0.15), inset 0 0 20px rgba(99, 102, 241, 0.05);
    }
    .glow-intermediate {
        box-shadow: 0 0 30px rgba(168, 85, 247, 0.15), inset 0 0 20px rgba(168, 85, 247, 0.05);
    }
    .glow-advanced {
        box-shadow: 0 0 30px rgba(236, 72, 153, 0.15), inset 0 0 20px rgba(236, 72, 153, 0.05);
    }
    
    /* Styling Buttons */
    div.stButton > button {
        border-radius: 10px !important;
        font-weight: 600 !important;
        padding: 10px 24px !important;
        font-size: 1rem !important;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
        height: 48px !important;
    }
    
    div.stButton > button[kind="primary"] {
        background: linear-gradient(135deg, #6366f1, #a855f7) !important;
        border: none !important;
        color: white !important;
        box-shadow: 0 4px 15px rgba(99, 102, 241, 0.3) !important;
    }
    
    div.stButton > button[kind="primary"]:hover {
        background: linear-gradient(135deg, #4f46e5, #9333ea) !important;
        box-shadow: 0 6px 20px rgba(99, 102, 241, 0.45) !important;
        transform: translateY(-2px);
    }
    
    div.stButton > button[kind="secondary"] {
        background-color: #1e293b !important;
        border: 1px solid rgba(255, 255, 255, 0.12) !important;
        color: #f8fafc !important;
    }
    
    div.stButton > button[kind="secondary"]:hover {
        border: 1px solid rgba(255, 255, 255, 0.3) !important;
        background-color: #334155 !important;
        transform: translateY(-1px);
    }
    
    /* Sidebar Step-by-Step progress styles */
    .sidebar-step {
        padding: 12px 16px;
        border-radius: 10px;
        margin-bottom: 10px;
        font-size: 0.92rem;
        transition: all 0.2s ease;
    }
    
    .completed-step {
        background-color: rgba(16, 185, 129, 0.06);
        border: 1px solid rgba(16, 185, 129, 0.15);
        color: #10b981;
    }
    
    .active-step {
        background-color: rgba(99, 102, 241, 0.12);
        border: 1px solid rgba(99, 102, 241, 0.35);
        color: #818cf8;
        font-weight: 600;
        box-shadow: 0 4px 12px rgba(99, 102, 241, 0.1);
    }
    
    .upcoming-step {
        background-color: transparent;
        border: 1px solid transparent;
        color: #94a3b8;
    }
    
    /* Profile Summary Card specific styling */
    .summary-row {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 15px 0;
        border-bottom: 1px solid rgba(255, 255, 255, 0.06);
    }
    
    .summary-label {
        font-size: 0.95rem;
        color: #94a3b8;
        font-weight: 500;
    }
    
    .summary-value {
        font-size: 0.95rem;
        color: #f8fafc;
        font-weight: 600;
    }
    
    .summary-value-badge {
        font-size: 0.8rem;
        font-weight: 700;
        text-transform: uppercase;
        padding: 4px 10px;
        border-radius: 12px;
        letter-spacing: 0.5px;
    }
    
    .exp-beginner {
        background-color: rgba(99, 102, 241, 0.15);
        color: #818cf8;
        border: 1px solid rgba(99, 102, 241, 0.3);
    }
    
    .exp-intermediate {
        background-color: rgba(168, 85, 247, 0.15);
        color: #c084fc;
        border: 1px solid rgba(168, 85, 247, 0.3);
    }
    
    .exp-advanced {
        background-color: rgba(236, 72, 153, 0.15);
        color: #f472b6;
        border: 1px solid rgba(236, 72, 153, 0.3);
    }
    
    /* Persona Card details styling */
    .persona-badge {
        font-size: 0.72rem;
        font-weight: 700;
        text-transform: uppercase;
        padding: 4px 12px;
        border-radius: 20px;
        display: inline-block;
        letter-spacing: 1px;
    }
    
    .persona-name {
        font-size: 2.2rem;
        font-weight: 800;
        letter-spacing: -0.5px;
        margin-top: 15px;
    }
    
    .section-label {
        font-size: 0.8rem;
        text-transform: uppercase;
        letter-spacing: 1.2px;
        color: #64748b;
        font-weight: 700;
        margin-bottom: 5px;
    }
    
    .section-text {
        font-size: 1.02rem;
        color: #cbd5e1;
        line-height: 1.5;
        font-weight: 400;
    }
    
    /* Clean overrides for streamlit inputs */
    .stRadio > label {
        display: none !important;
    }
    
    /* Make active radio choice look premium */
    div[data-testid="stMarkdownContainer"] > p {
        margin-bottom: 0px;
    }
    
    /* Style radio selections */
    div[data-testid="stRadio"] > div {
        gap: 10px;
    }
    
    div[data-testid="stRadio"] label {
        background-color: #1e293b;
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 10px;
        padding: 12px 18px !important;
        color: #cbd5e1 !important;
        font-size: 1rem !important;
        font-weight: 500 !important;
        transition: all 0.2s ease;
        cursor: pointer;
        width: 100%;
    }
    
    div[data-testid="stRadio"] label:hover {
        background-color: #334155;
        border: 1px solid rgba(99, 102, 241, 0.3);
    }
    
    div[data-testid="stRadio"] label[data-checked="true"] {
        background: rgba(99, 102, 241, 0.1) !important;
        border: 1.5px solid #6366f1 !important;
        color: #818cf8 !important;
        font-weight: 600 !important;
    }
    
    /* Hide native radio circle to make list items feel like clean list buttons */
    div[data-testid="stRadio"] label div[role="radiogroup"] {
        display: none !important;
    }
    
    /* Slider visual tuning */
    div[data-testid="stSlider"] [data-testid="stSliderTrack"] {
        background-color: #1e293b;
    }
    
    div[data-testid="stSlider"] [aria-valuenow] {
        background-color: #6366f1;
    }
    
    </style>
    """
)

# Initialize Session State Variables
if "app_phase" not in st.session_state:
    st.session_state.app_phase = "profiling"
if "onboarding_started" not in st.session_state:
    st.session_state.onboarding_started = False
if "current_step" not in st.session_state:
    st.session_state.current_step = 1
if "profile_data" not in st.session_state:
    st.session_state.profile_data = {}
if "completed" not in st.session_state:
    st.session_state.completed = False

# Sidebar Branding Header
st.sidebar.html(
    """
    <div style='text-align: center; padding: 10px 0; margin-bottom: 20px;'>
        <h2 style='margin: 0; font-weight: 800; font-size: 1.6rem; letter-spacing: -0.5px;'>🎯 Agent OnboardX</h2>
        <p style='color: #6366f1; margin: 0; font-size: 0.8rem; font-weight: 600; text-transform: uppercase; letter-spacing: 1px;'>AI Execution Coach</p>
    </div>
    <hr style='margin-top: 0; margin-bottom: 20px; border-color: rgba(255, 255, 255, 0.1);'>
    """
)

# App Routing Logic
if st.session_state.app_phase == "profiling":
    if not st.session_state.onboarding_started:
        # 1. LANDING PAGE
        st.sidebar.html("<p style='opacity: 0.5; font-style: italic; font-size: 0.9rem;'>Start profiling to see onboarding progress here.</p>")
        
        st.html(
            textwrap.dedent(
                """
                <div class='hero-container'>
                    <div style='margin-bottom: 25px;'>
                        <span class='badge' style='background: rgba(99, 102, 241, 0.1); color: #818cf8; border: 1px solid rgba(99, 102, 241, 0.3); padding: 6px 14px; border-radius: 20px; font-size: 0.85rem; font-weight: 700; letter-spacing: 1.5px;'>WELCOME TO AGENT ONBOARDX</span>
                    </div>
                    <h1 class='hero-title'>Agent OnboardX</h1>
                    <h2 class='hero-subtitle'>Your Personal AI Execution Coach</h2>
                    <p class='hero-text'>
                        Unlock your absolute execution potential. Before we can generate a personalized habit, 
                        planning, and target roadmap, let's understand exactly how you operate, what motivates you, 
                        and the barriers that get in your way.
                    </p>
                </div>
                """
            )
        )
        
        # Start Button Centered
        col1, col2, col3 = st.columns([1, 1.2, 1])
        with col2:
            if st.button("Start Profiling ⚡", use_container_width=True, type="primary"):
                st.session_state.onboarding_started = True
                st.rerun()

    elif not st.session_state.completed:
        # 2. ONBOARDING WIZARD
        render_sidebar_progress()
        render_onboarding_wizard()

    else:
        # 3. RESULTS PAGE
        # Sidebar Complete State
        st.sidebar.html(
            """
            <div class='sidebar-step completed-step' style='text-align: center; margin-bottom: 20px; font-weight: bold;'>
                🎉 Blueprint Generated
            </div>
            <hr style='border-color: rgba(255,255,255,0.1); margin: 15px 0;'>
            <p style='font-size: 0.85rem; color: #64748b; text-align: center;'>Your results have been processed and are locked in session state.</p>
            """
        )
        
        render_results_page()

elif st.session_state.app_phase == "goal_intake":
    # Sidebar back to Profiling option
    st.sidebar.html("<h3 style='margin-bottom: 20px;'>Navigation</h3>")
    if st.sidebar.button("👤 View Persona Profile", use_container_width=True):
        st.session_state.app_phase = "profiling"
        st.rerun()
    st.sidebar.html("<hr style='border-color: rgba(255,255,255,0.1); margin: 15px 0;'>")
    
    render_goal_intake_module()
