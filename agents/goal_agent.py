import streamlit as st
import datetime
from services.gemini_service import get_api_key, analyze_goal_with_gemini

def initialize_goal_state():
    """
    Ensures all goal intake session state variables are initialized.
    """
    if "goal_submitted" not in st.session_state:
        st.session_state.goal_submitted = False
    if "goal_analysis" not in st.session_state:
        st.session_state.goal_analysis = {}
    if "goal_questions" not in st.session_state:
        st.session_state.goal_questions = []
    if "goal_answers" not in st.session_state:
        st.session_state.goal_answers = {}
    if "goal_q_step" not in st.session_state:
        st.session_state.goal_q_step = 1
    if "goal_context" not in st.session_state:
        st.session_state.goal_context = None
    if "goal_text" not in st.session_state:
        st.session_state.goal_text = ""
    if "custom_api_key" not in st.session_state:
        st.session_state.custom_api_key = ""

def render_sidebar_api_key():
    """
    Renders an API key input in the sidebar if not resolved from system .env / secrets.
    """
    initialize_goal_state()
    resolved_key = get_api_key()
    
    if not resolved_key:
        st.sidebar.html(
            """
            <div style='background-color: rgba(245, 158, 11, 0.08); border: 1px solid rgba(245, 158, 11, 0.2); padding: 15px; border-radius: 10px; margin-bottom: 20px;'>
                <p style='color: #fbbf24; font-size: 0.85rem; margin: 0 0 10px 0;'>⚠️ <b>Missing Gemini API Key</b></p>
                <p style='color: #94a3b8; font-size: 0.75rem; margin: 0;'>To use the Goal Intake module, please enter your Gemini API key below. This will be stored temporarily in your session state.</p>
            </div>
            """
        )
        custom_key = st.sidebar.text_input(
            "Gemini API Key",
            type="password",
            value=st.session_state.custom_api_key,
            placeholder="AIzaSy...",
            help="Your API key is safe and only used for requests during this session."
        )
        if custom_key != st.session_state.custom_api_key:
            st.session_state.custom_api_key = custom_key
            st.rerun()
            
        return custom_key
        
    return resolved_key

def render_goal_intake_module():
    """
    Renders the Goal Intake Agent module flow.
    """
    # Resolve API Key
    api_key = render_sidebar_api_key()
    
    # Check if profiling persona exists
    persona = st.session_state.profile_data
    if not persona:
        # Fallback persona if they bypassed the profiling onboarding
        persona = {
            "name": "Consistent Explorer",
            "strength": "High curiosity & adaptability",
            "challenge": "Maintaining long-term habit consistency",
            "strategy": "Micro-habits planning (15-minute daily sessions)"
        }
    
    # 1. GOAL INPUT STEP
    if not st.session_state.goal_submitted:
        st.html(
            """
            <div style='max-width: 800px; margin: 0 auto; padding: 20px 0;'>
                <span class='badge' style='background: rgba(99, 102, 241, 0.1); color: #818cf8; border: 1px solid rgba(99, 102, 241, 0.3); padding: 6px 14px; border-radius: 20px; font-size: 0.85rem; font-weight: 700; letter-spacing: 1.5px;'>PHASE 2: GOAL INTAKE</span>
                <h1 style='font-size: 2.8rem; font-weight: 800; margin-top: 15px; margin-bottom: 10px; background: linear-gradient(to right, #f8fafc, #94a3b8); -webkit-background-clip: text; -webkit-text-fill-color: transparent;'>What do you want to accomplish?</h1>
                <p style='color: #94a3b8; font-size: 1.15rem; margin-bottom: 30px;'>Tell your Goal Intake Agent what goal you want to tackle. We will analyze it and ask you a few targeted questions to structure your plan.</p>
            </div>
            """
        )
        
        # User input area
        goal_input = st.text_area(
            "Enter your goal",
            placeholder="e.g. Build a SaaS micro-startup in 30 days, Run my first half-marathon, Learn conversational Spanish for my upcoming trip...",
            height=120,
            label_visibility="collapsed"
        )
        
        st.markdown("<div style='height: 10px;'></div>", unsafe_allow_html=True)
        
        # Alert if key is missing
        if not api_key:
            st.warning("Please configure your Gemini API Key in the sidebar before proceeding.")
            
        col1, col2, col3 = st.columns([1, 1.2, 1])
        with col2:
            if st.button("Analyze Goal ⚡", use_container_width=True, type="primary", disabled=not api_key):
                if not goal_input.strip():
                    st.error("Please enter a valid goal before proceeding.")
                else:
                    # Execute Gemini API call with loading spinner
                    with st.spinner("Gemini API is analyzing your goal and customizing context questions..."):
                        try:
                            # Invoke Gemini
                            analysis = analyze_goal_with_gemini(goal_input, persona, api_key)
                            
                            # Save to session state
                            st.session_state.goal_analysis = {
                                "category": analysis.get("category", "General"),
                                "difficulty": analysis.get("difficulty", "Intermediate"),
                                "estimated_duration": analysis.get("estimated_duration", "Flexible"),
                                "required_skills": analysis.get("required_skills", []),
                                "risks": analysis.get("risks", [])
                            }
                            st.session_state.goal_questions = analysis.get("dynamic_questions", [])
                            st.session_state.goal_text = goal_input
                            st.session_state.goal_submitted = True
                            st.session_state.goal_q_step = 1
                            st.session_state.goal_answers = {}
                            st.rerun()
                        except Exception as e:
                            st.error(f"Goal Analysis Failed: {str(e)}")
                            
    # 2. INTERACTIVE QUESTIONS STEP
    elif st.session_state.goal_submitted and not st.session_state.goal_context:
        # Display Goal Ingestion Summary Cards
        analysis = st.session_state.goal_analysis
        questions = st.session_state.goal_questions
        q_step = st.session_state.goal_q_step
        
        st.html(
            f"""
            <div style='margin-bottom: 30px; margin-top: 10px;'>
                <span style='font-size: 0.9rem; text-transform: uppercase; letter-spacing: 1.5px; opacity: 0.7; color: #818cf8;'>Goal Analysis Complete</span>
                <h2 style='font-size: 2.2rem; font-weight: 800; color: #f8fafc; margin-top: 10px; margin-bottom: 5px;'>Goal: "{st.session_state.goal_text}"</h2>
                <p style='color: #94a3b8; font-size: 1rem;'>Gemini has evaluated your objective. Review the blueprint below and answer the 5 dynamic questions to build your strategy context.</p>
            </div>
            """
        )
        
        # 3-Column Grid for Goal Ingestion Summary Cards
        col_c, col_d, col_e = st.columns([1, 1, 1], gap="medium")
        
        with col_c:
            st.html(
                f"""
                <div class='results-card' style='border-top: 4px solid #6366f1;'>
                    <div style='display: flex; align-items: center; margin-bottom: 15px;'>
                        <span style='font-size: 1.2rem; margin-right: 8px;'>🎯</span>
                        <h4 style='margin: 0; font-weight: 700; color: #f8fafc; font-size: 1.1rem;'>Overview</h4>
                    </div>
                    <div class='summary-row'>
                        <div class='summary-label'>Category</div>
                        <div class='summary-value'>{analysis.get('category')}</div>
                    </div>
                    <div class='summary-row'>
                        <div class='summary-label'>Difficulty</div>
                        <div class='summary-value-badge exp-{analysis.get('difficulty','Intermediate').lower()}'>{analysis.get('difficulty')}</div>
                    </div>
                    <div class='summary-row' style='border-bottom: none;'>
                        <div class='summary-label'>Estimated Time</div>
                        <div class='summary-value' style='color: #818cf8;'>{analysis.get('estimated_duration')}</div>
                    </div>
                </div>
                """
            )
            
        with col_d:
            skills_html = "".join([f"<li style='margin-bottom: 8px; color: #cbd5e1; font-size: 0.92rem;'>🛠️ {s}</li>" for s in analysis.get('required_skills', [])])
            st.html(
                f"""
                <div class='results-card' style='border-top: 4px solid #a855f7;'>
                    <div style='display: flex; align-items: center; margin-bottom: 15px;'>
                        <span style='font-size: 1.2rem; margin-right: 8px;'>🧠</span>
                        <h4 style='margin: 0; font-weight: 700; color: #f8fafc; font-size: 1.1rem;'>Required Skills</h4>
                    </div>
                    <ul style='list-style-type: none; padding-left: 0; margin: 0;'>
                        {skills_html}
                    </ul>
                </div>
                """
            )
            
        with col_e:
            risks_html = "".join([f"<li style='margin-bottom: 8px; color: #cbd5e1; font-size: 0.92rem;'>⚠️ {r}</li>" for r in analysis.get('risks', [])])
            st.html(
                f"""
                <div class='results-card' style='border-top: 4px solid #f87171;'>
                    <div style='display: flex; align-items: center; margin-bottom: 15px;'>
                        <span style='font-size: 1.2rem; margin-right: 8px;'>🚨</span>
                        <h4 style='margin: 0; font-weight: 700; color: #f8fafc; font-size: 1.1rem;'>Persona Risks</h4>
                    </div>
                    <ul style='list-style-type: none; padding-left: 0; margin: 0;'>
                        {risks_html}
                    </ul>
                </div>
                """
            )
            
        # Spacer
        st.markdown("<div style='height: 40px;'></div>", unsafe_allow_html=True)
        
        # Questionnaire wizard
        total_q = len(questions)
        q_pct = int((q_step / total_q) * 100)
        
        st.html(
            f"""
            <div style='display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px;'>
                <span style='font-size: 0.9rem; text-transform: uppercase; letter-spacing: 1.5px; opacity: 0.7;'>Context Questionnaire: Question {q_step} of {total_q}</span>
                <span class='badge' style='background: linear-gradient(135deg, #a855f7, #ec4899); color: white; padding: 4px 10px; border-radius: 20px; font-size: 0.8rem; font-weight: bold;'>{q_pct}% Complete</span>
            </div>
            <div class='question-card' style='border-left: 4px solid #a855f7;'>
                <h3 style='font-weight: 700; margin-bottom: 5px; color: #f8fafc;'>❓ Question {q_step}</h3>
                <p style='color: #cbd5e1; font-size: 1.1rem; margin-bottom: 20px; font-weight: 500;'>{questions[q_step - 1]}</p>
            </div>
            """
        )
        
        # User answer input
        saved_ans = st.session_state.goal_answers.get(q_step - 1, "")
        ans_input = st.text_area(
            "Your Answer",
            value=saved_ans,
            placeholder="Type your response here...",
            height=100,
            label_visibility="collapsed"
        )
        st.session_state.goal_answers[q_step - 1] = ans_input
        
        # Questionnaire Progress Bar
        st.html(f"<p style='font-size: 0.85rem; color: #94a3b8; margin-top: 15px; margin-bottom: 5px;'>Questionnaire progress: {q_pct}%</p>")
        st.progress(q_step / total_q)
        
        # Navigation
        st.markdown("<div style='height: 30px;'></div>", unsafe_allow_html=True)
        col_nav1, col_nav2 = st.columns([1, 1])
        
        with col_nav1:
            if q_step > 1:
                if st.button("← Back", key="q_back", use_container_width=True, type="secondary"):
                    st.session_state.goal_q_step -= 1
                    st.rerun()
                    
        with col_nav2:
            if q_step < total_q:
                if st.button("Next Question →", key="q_next", use_container_width=True, type="primary"):
                    if not ans_input.strip():
                        st.error("Please provide an answer before going to the next question.")
                    else:
                        st.session_state.goal_q_step += 1
                        st.rerun()
            else:
                if st.button("Finalize Goal Blueprint 🎉", key="q_finalize", use_container_width=True, type="primary"):
                    if not ans_input.strip():
                        st.error("Please answer the final question before finalizing.")
                    else:
                        # Compile Goal Context
                        compiled_qa = []
                        for i, q_text in enumerate(questions):
                            compiled_qa.append({
                                "question": q_text,
                                "answer": st.session_state.goal_answers.get(i, "")
                            })
                            
                        st.session_state.goal_context = {
                            "goal": st.session_state.goal_text,
                            "category": analysis.get("category"),
                            "difficulty": analysis.get("difficulty"),
                            "estimated_duration": analysis.get("estimated_duration"),
                            "required_skills": analysis.get("required_skills"),
                            "risks": analysis.get("risks"),
                            "qa_context": compiled_qa,
                            "timestamp": datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S")
                        }
                        st.rerun()
                        
    # 3. COMPILED CONTEXT DISPLAY STEP
    else:
        ctx = st.session_state.goal_context
        
        st.html(
            """
            <div style='text-align: center; margin-bottom: 40px; margin-top: 10px;'>
                <span class='badge' style='background: linear-gradient(135deg, #10b981, #059669); color: white; padding: 6px 14px; border-radius: 20px; font-size: 0.85rem; font-weight: 700; letter-spacing: 1px;'>GOAL CONTEXT SECURED</span>
                <h1 class='results-header' style='font-size: 2.8rem; font-weight: 800; margin-top: 15px; margin-bottom: 10px; background: linear-gradient(to right, #f8fafc, #94a3b8); -webkit-background-clip: text; -webkit-text-fill-color: transparent;'>Ready for Strategy Execution</h1>
                <p style='color: #94a3b8; font-size: 1.15rem; max-width: 600px; margin: 0 auto;'>The Goal Intake Agent has compiled a comprehensive context payload. This will form the foundation for the Strategy Generator Agent.</p>
            </div>
            """
        )
        
        # Display Final Goal Context Summary Card
        qa_html = ""
        for i, item in enumerate(ctx.get("qa_context", [])):
            qa_html += f"""
            <div style='margin-bottom: 18px; border-bottom: 1px solid rgba(255,255,255,0.05); padding-bottom: 12px;'>
                <p style='color: #818cf8; font-weight: 600; margin: 0 0 5px 0; font-size: 0.95rem;'>Q{i+1}: {item["question"]}</p>
                <p style='color: #f8fafc; margin: 0; font-size: 0.92rem; font-style: italic; line-height: 1.4;'>"{item["answer"]}"</p>
            </div>
            """
            
        skills_pills = "".join([f"<span style='background-color: rgba(168, 85, 247, 0.15); color: #c084fc; border: 1px solid rgba(168, 85, 247, 0.3); padding: 4px 10px; border-radius: 12px; font-size: 0.82rem; margin-right: 8px; margin-bottom: 8px; display: inline-block;'>{s}</span>" for s in ctx.get('required_skills', [])])
        risks_bullets = "".join([f"<li style='margin-bottom: 5px; color: #cbd5e1; font-size: 0.9rem;'>⚠️ {r}</li>" for r in ctx.get('risks', [])])
        
        st.html(
            f"""
            <div class='persona-card glow-intermediate' style='border-top: 5px solid #a855f7; padding: 35px; max-width: 900px; margin: 0 auto 30px auto;'>
                <div style='display: flex; justify-content: space-between; align-items: center; margin-bottom: 25px;'>
                    <div class='persona-badge' style='background: rgba(168,85,247,0.1); color: #c084fc; border: 1px solid rgba(168,85,247,0.3);'>Compiled Goal Context</div>
                    <span style='font-size: 0.85rem; color: #64748b;'>{ctx.get('timestamp')}</span>
                </div>
                
                <h2 style='font-size: 1.8rem; font-weight: 800; color: #f8fafc; margin-top: 0; margin-bottom: 10px;'>"{ctx.get('goal')}"</h2>
                <div style='display: flex; gap: 20px; align-items: center; margin-bottom: 25px;'>
                    <span class='summary-value-badge exp-intermediate'>{ctx.get('category')}</span>
                    <span class='summary-value-badge exp-advanced'>{ctx.get('difficulty')} Level</span>
                    <span style='color: #94a3b8; font-size: 0.9rem;'>Duration: <b>{ctx.get('estimated_duration')}</b></span>
                </div>
                
                <div style='margin-bottom: 25px;'>
                    <div class='section-label'>Skills Roadmap Target</div>
                    <div style='margin-top: 8px;'>{skills_pills}</div>
                </div>
                
                <div style='margin-bottom: 25px;'>
                    <div class='section-label'>Analyzed Impediments & Risks</div>
                    <ul style='list-style-type: none; padding-left: 0; margin: 8px 0 0 0;'>
                        {risks_bullets}
                    </ul>
                </div>
                
                <div>
                    <div class='section-label' style='margin-bottom: 15px;'>Detailed Goal Context (Q&A)</div>
                    <div style='background-color: rgba(15, 23, 42, 0.4); border: 1px solid rgba(255, 255, 255, 0.05); border-radius: 10px; padding: 20px;'>
                        {qa_html}
                    </div>
                </div>
            </div>
            """
        )
        
        # Actions Row
        col_res1, col_res2, col_res3 = st.columns([1, 1.2, 1])
        with col_res2:
            if st.button("🔄 Reset Goal Context", use_container_width=True):
                st.session_state.goal_submitted = False
                st.session_state.goal_analysis = {}
                st.session_state.goal_questions = []
                st.session_state.goal_answers = {}
                st.session_state.goal_q_step = 1
                st.session_state.goal_context = None
                st.session_state.goal_text = ""
                st.rerun()
