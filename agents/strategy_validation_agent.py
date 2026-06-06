import streamlit as st
import datetime
from services.gemini_service import (
    generate_validation_questions_with_gemini,
    evaluate_strategy_readiness_with_gemini
)
from agents.goal_agent import render_sidebar_api_key

def initialize_validation_state():
    """
    Initializes session state variables for strategy validation.
    """
    if "validation_questions_data" not in st.session_state:
        st.session_state.validation_questions_data = None
    if "validation_answers" not in st.session_state:
        st.session_state.validation_answers = {}
    if "validation_q_step" not in st.session_state:
        st.session_state.validation_q_step = 1
    if "strategy_validation" not in st.session_state:
        st.session_state.strategy_validation = None

def render_strategy_validation_agent():
    """
    Renders the Strategy Validation Agent UI and logic.
    """
    initialize_validation_state()
    
    # Assert inputs exist
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

    goal_context = st.session_state.goal_context
    profile_data = st.session_state.profile_data
    strategy = st.session_state.selected_strategy_data
    api_key = render_sidebar_api_key()

    # Sidebar navigation option
    st.sidebar.html("<h3 style='margin-bottom: 20px;'>Navigation</h3>")
    if st.sidebar.button("👤 View Persona Profile", key="val_nav_profile", use_container_width=True):
        st.session_state.app_phase = "profiling"
        st.rerun()
    if st.sidebar.button("⚡ Back to Strategy Selection", key="val_nav_strat", use_container_width=True):
        st.session_state.app_phase = "strategy_generation"
        st.rerun()
    st.sidebar.html("<hr style='border-color: rgba(255,255,255,0.1); margin: 15px 0;'>")

    # CSS Injection
    st.html(
        """
        <style>
        .readiness-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }
        .readiness-card {
            background: rgba(30, 41, 59, 0.45);
            border: 1px solid rgba(255, 255, 255, 0.08);
            border-radius: 16px;
            padding: 20px;
            text-align: center;
            box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.25);
            backdrop-filter: blur(8px);
            transition: all 0.3s ease;
        }
        .readiness-card:hover {
            transform: translateY(-2px);
            border-color: rgba(255,255,255,0.15);
        }
        .readiness-score-value {
            font-size: 2.8rem;
            font-weight: 800;
            margin-bottom: 5px;
            line-height: 1;
        }
        .readiness-score-label {
            font-size: 0.82rem;
            color: #94a3b8;
            text-transform: uppercase;
            letter-spacing: 1.2px;
            font-weight: 700;
        }
        .readiness-bar-bg {
            background: #0f172a;
            border-radius: 6px;
            height: 8px;
            width: 100%;
            margin-top: 15px;
            overflow: hidden;
            border: 1px solid rgba(255,255,255,0.05);
        }
        .readiness-bar-fill {
            height: 100%;
            border-radius: 6px;
        }
        
        .feedback-grid {
            display: grid;
            grid-template-columns: repeat(2, 1fr);
            gap: 20px;
            margin-bottom: 30px;
        }
        @media (max-width: 768px) {
            .feedback-grid {
                grid-template-columns: 1fr;
            }
        }
        .feedback-box {
            background: rgba(30, 41, 59, 0.35);
            border: 1px solid rgba(255, 255, 255, 0.06);
            border-radius: 16px;
            padding: 25px;
            box-shadow: 0 4px 20px rgba(0, 0, 0, 0.15);
            backdrop-filter: blur(6px);
        }
        .feedback-box-title {
            font-size: 1.1rem;
            font-weight: 700;
            margin-bottom: 15px;
            display: flex;
            align-items: center;
        }
        .feedback-box-list {
            list-style-type: none;
            padding-left: 0;
            margin: 0;
        }
        .feedback-box-list li {
            font-size: 0.9rem;
            color: #cbd5e1;
            margin-bottom: 8px;
            position: relative;
            padding-left: 20px;
            line-height: 1.45;
        }
        .feedback-box-list li::before {
            position: absolute;
            left: 0;
            font-weight: 800;
        }
        
        .box-strengths { border-top: 4px solid #10b981; }
        .box-strengths .feedback-box-title { color: #10b981; }
        .box-strengths li::before { content: "✓"; color: #10b981; }
        
        .box-weaknesses { border-top: 4px solid #f59e0b; }
        .box-weaknesses .feedback-box-title { color: #f59e0b; }
        .box-weaknesses li::before { content: "⚠"; color: #f59e0b; }
        
        .box-risks { border-top: 4px solid #ef4444; }
        .box-risks .feedback-box-title { color: #ef4444; }
        .box-risks li::before { content: "🚨"; color: #ef4444; }
        
        .box-recommendations { border-top: 4px solid #3b82f6; }
        .box-recommendations .feedback-box-title { color: #3b82f6; }
        .box-recommendations li::before { content: "💡"; color: #3b82f6; }
        
        .gap-container {
            background: rgba(15, 23, 42, 0.4);
            border: 1px solid rgba(255, 255, 255, 0.04);
            border-radius: 12px;
            padding: 15px 20px;
            margin-bottom: 20px;
        }
        .gap-label {
            font-size: 0.75rem;
            text-transform: uppercase;
            letter-spacing: 1px;
            color: #64748b;
            font-weight: 700;
            margin-bottom: 4px;
        }
        .gap-list {
            margin: 0;
            padding-left: 15px;
            color: #cbd5e1;
            font-size: 0.88rem;
        }
        .gap-list li {
            margin-bottom: 4px;
        }
        </style>
        """
    )

    # 1. GENERATE VALIDATION QUESTIONS
    if not st.session_state.validation_questions_data:
        st.html(
            f"""
            <div style='max-width: 800px; margin: 0 auto; padding: 20px 0;'>
                <span class='badge' style='background: rgba(99, 102, 241, 0.1); color: #818cf8; border: 1px solid rgba(99, 102, 241, 0.3); padding: 6px 14px; border-radius: 20px; font-size: 0.85rem; font-weight: 700; letter-spacing: 1.5px;'>PHASE 3.5: STRATEGY VALIDATION</span>
                <h1 style='font-size: 2.8rem; font-weight: 800; margin-top: 15px; margin-bottom: 10px; background: linear-gradient(to right, #f8fafc, #94a3b8); -webkit-background-clip: text; -webkit-text-fill-color: transparent;'>Validate your path</h1>
                <p style='color: #94a3b8; font-size: 1.15rem; margin-bottom: 30px;'>The Strategy Validation Agent runs a mock execution audit. We will locate hidden resource, knowledge, skill, and schedule gaps, and custom-generate 3 follow-up questions to calculate your launch readiness.</p>
            </div>
            """
        )
        
        if not api_key:
            st.warning("Please configure your Gemini API Key in the sidebar before proceeding.")

        col1, col2, col3 = st.columns([1, 1.2, 1])
        with col2:
            if st.button("Start Validation Audit ⚡", use_container_width=True, type="primary", disabled=not api_key):
                with st.spinner("Analyzing execution gaps and generating questions..."):
                    try:
                        questions_data = generate_validation_questions_with_gemini(profile_data, goal_context, strategy, api_key)
                        st.session_state.validation_questions_data = questions_data
                        st.session_state.validation_q_step = 1
                        st.session_state.validation_answers = {}
                        st.rerun()
                    except Exception as e:
                        st.error(f"Validation analysis failed: {str(e)}")

    # 2. RUN QUESTIONNAIRE WIZARD (If questions exist but results don't)
    elif st.session_state.validation_questions_data and not st.session_state.strategy_validation:
        questions_data = st.session_state.validation_questions_data
        analysis = questions_data.get("analysis", {})
        questions = questions_data.get("validation_questions", [])
        q_step = st.session_state.validation_q_step
        total_q = len(questions)
        q_pct = int((q_step / total_q) * 100)

        st.html(
            f"""
            <div style='margin-bottom: 30px; margin-top: 10px;'>
                <span style='font-size: 0.9rem; text-transform: uppercase; letter-spacing: 1.5px; opacity: 0.7; color: #818cf8;'>Execution Auditor Gaps Analyzed</span>
                <h2 style='font-size: 2.2rem; font-weight: 800; color: #f8fafc; margin-top: 10px; margin-bottom: 5px;'>Initial Gaps & Validation</h2>
                <p style='color: #94a3b8; font-size: 1rem;'>Gemini has identified potential friction points. Answer the validation questionnaire to grade your readiness scores.</p>
            </div>
            """
        )

        # 3 Column Layout for initial gaps analyzed
        col_g1, col_g2, col_g3 = st.columns([1, 1, 1], gap="medium")
        
        with col_g1:
            skills_html = "".join([f"<li>{s}</li>" for s in analysis.get("missing_skills", [])])
            st.html(
                f"""
                <div class='gap-container' style='border-top: 3px solid #10b981; height: 100%;'>
                    <div class='gap-label'>Missing Skills / Knowledge</div>
                    <ul class='gap-list'>{skills_html}</ul>
                </div>
                """
            )
            
        with col_g2:
            res_html = "".join([f"<li>{r}</li>" for r in analysis.get("missing_resources", [])])
            st.html(
                f"""
                <div class='gap-container' style='border-top: 3px solid #f59e0b; height: 100%;'>
                    <div class='gap-label'>Missing Resources / Tools</div>
                    <ul class='gap-list'>{res_html}</ul>
                </div>
                """
            )
            
        with col_g3:
            time_html = "".join([f"<li>{t}</li>" for t in analysis.get("time_constraints", [])])
            st.html(
                f"""
                <div class='gap-container' style='border-top: 3px solid #ef4444; height: 100%;'>
                    <div class='gap-label'>Time & Obstacles Risks</div>
                    <ul class='gap-list'>{time_html}</ul>
                </div>
                """
            )

        st.markdown("<div style='height: 30px;'></div>", unsafe_allow_html=True)

        # Render step question
        active_question = questions[q_step - 1]
        st.html(
            f"""
            <div style='display: flex; justify-content: space-between; align-items: center; margin-bottom: 15px;'>
                <span style='font-size: 0.9rem; text-transform: uppercase; letter-spacing: 1.5px; opacity: 0.7;'>Validation Wizard: Step {q_step} of {total_q}</span>
                <span class='badge' style='background: linear-gradient(135deg, #a855f7, #ec4899); color: white; padding: 4px 10px; border-radius: 20px; font-size: 0.8rem; font-weight: bold;'>{q_pct}%</span>
            </div>
            <div class='question-card' style='border-left: 4px solid #a855f7;'>
                <h3 style='font-weight: 700; margin-bottom: 5px; color: #f8fafc;'>❓ Question {q_step}</h3>
                <p style='color: #cbd5e1; font-size: 1.1rem; margin-bottom: 20px; font-weight: 500;'>{active_question}</p>
            </div>
            """
        )

        saved_ans = st.session_state.validation_answers.get(q_step - 1, "")
        ans_input = st.text_area(
            "Your Answer",
            value=saved_ans,
            placeholder="State your answer, tools, or schedule adjustments...",
            height=100,
            label_visibility="collapsed"
        )
        st.session_state.validation_answers[q_step - 1] = ans_input

        st.progress(q_step / total_q)

        # Nav
        st.markdown("<div style='height: 25px;'></div>", unsafe_allow_html=True)
        col_nav1, col_nav2 = st.columns([1, 1])
        
        with col_nav1:
            if q_step > 1:
                if st.button("← Previous Question", key="val_q_back", use_container_width=True, type="secondary"):
                    st.session_state.validation_q_step -= 1
                    st.rerun()
                    
        with col_nav2:
            if q_step < total_q:
                if st.button("Next Question →", key="val_q_next", use_container_width=True, type="primary"):
                    if not ans_input.strip():
                        st.error("Please answer the validation question before moving forward.")
                    else:
                        st.session_state.validation_q_step += 1
                        st.rerun()
            else:
                if st.button("Calculate Readiness Scores 🎉", key="val_q_calc", use_container_width=True, type="primary"):
                    if not ans_input.strip():
                        st.error("Please answer the final validation question before submitting.")
                    else:
                        # Compile QA list
                        compiled_qa = []
                        for i, q_text in enumerate(questions):
                            compiled_qa.append({
                                "question": q_text,
                                "answer": st.session_state.validation_answers.get(i, "")
                            })
                            
                        with st.spinner("Gemini is auditing answers and calculating readiness metrics..."):
                            try:
                                eval_data = evaluate_strategy_readiness_with_gemini(
                                    profile_data,
                                    goal_context,
                                    strategy,
                                    compiled_qa,
                                    api_key
                                )
                                
                                # Save in state as strategy_validation
                                st.session_state.strategy_validation = {
                                    "scores": {
                                        "skill_readiness": eval_data.get("skill_readiness_score", 50),
                                        "resource_readiness": eval_data.get("resource_readiness_score", 50),
                                        "time_readiness": eval_data.get("time_readiness_score", 50),
                                        "overall_readiness": eval_data.get("overall_readiness_score", 50)
                                    },
                                    "feedback": {
                                        "strengths": eval_data.get("strengths", []),
                                        "weaknesses": eval_data.get("weaknesses", []),
                                        "potential_risks": eval_data.get("potential_risks", []),
                                        "recommendations": eval_data.get("recommendations", [])
                                    },
                                    "answers": compiled_qa,
                                    "timestamp": datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S")
                                }
                                st.rerun()
                            except Exception as e:
                                st.error(f"Readiness evaluation failed: {str(e)}")

    # 3. DISPLAY FINAL VALIDATION DASHBOARD
    else:
        v_data = st.session_state.strategy_validation
        scores = v_data.get("scores", {})
        feedback = v_data.get("feedback", {})
        
        st.html(
            f"""
            <div style='text-align: center; margin-bottom: 40px; margin-top: 10px;'>
                <span class='badge' style='background: linear-gradient(135deg, #10b981, #059669); color: white; padding: 6px 14px; border-radius: 20px; font-size: 0.85rem; font-weight: 700; letter-spacing: 1px;'>VALIDATION AUDIT SECURED</span>
                <h1 class='results-header' style='font-size: 2.8rem; font-weight: 800; margin-top: 15px; margin-bottom: 10px; background: linear-gradient(to right, #f8fafc, #94a3b8); -webkit-background-clip: text; -webkit-text-fill-color: transparent;'>Launch Readiness Dashboard</h1>
                <p style='color: #94a3b8; font-size: 1.15rem; max-width: 600px; margin: 0 auto;'>The Strategy Validation Agent has finalized your execution readiness assessment. Address the weaknesses below before kick-off.</p>
            </div>
            """
        )

        # 4 Column Grid for Scores
        score_keys = [
            ("Skill Readiness", scores.get("skill_readiness", 50), "#10b981"),
            ("Resource Readiness", scores.get("resource_readiness", 50), "#f59e0b"),
            ("Time Readiness", scores.get("time_readiness", 50), "#ef4444"),
            ("Overall Readiness", scores.get("overall_readiness", 50), "#6366f1")
        ]

        st.markdown("<div class='readiness-grid'>", unsafe_allow_html=True)
        cols_score = st.columns(4, gap="medium")
        for idx, (label, val, color) in enumerate(score_keys):
            # Dynamic bar fill width
            with cols_score[idx]:
                st.html(
                    f"""
                    <div class='readiness-card'>
                        <div class='readiness-score-label'>{label}</div>
                        <div class='readiness-score-value' style='color: {color};'>{val}%</div>
                        <div class='readiness-bar-bg'>
                            <div class='readiness-bar-fill' style='width: {val}%; background-color: {color};'></div>
                        </div>
                    </div>
                    """
                )
        st.markdown("</div>", unsafe_allow_html=True)

        st.markdown("<div style='height: 20px;'></div>", unsafe_allow_html=True)

        # 2x2 Grid for Strengths, Weaknesses, Risks, Recommendations
        col_f1, col_f2 = st.columns([1, 1], gap="large")
        
        with col_f1:
            str_html = "".join([f"<li>{s}</li>" for s in feedback.get("strengths", [])])
            st.html(
                f"""
                <div class='feedback-box box-strengths'>
                    <div class='feedback-box-title'>💪 Execution Strengths</div>
                    <ul class='feedback-box-list'>{str_html}</ul>
                </div>
                """
            )
            
            st.markdown("<div style='height: 20px;'></div>", unsafe_allow_html=True)
            
            risk_html = "".join([f"<li>{r}</li>" for r in feedback.get("potential_risks", [])])
            st.html(
                f"""
                <div class='feedback-box box-risks'>
                    <div class='feedback-box-title'>🚨 Vulnerability & Risks</div>
                    <ul class='feedback-box-list'>{risk_html}</ul>
                </div>
                """
            )
            
        with col_f2:
            weak_html = "".join([f"<li>{w}</li>" for w in feedback.get("weaknesses", [])])
            st.html(
                f"""
                <div class='feedback-box box-weaknesses'>
                    <div class='feedback-box-title'>⚠️ Preparation Gaps (Weaknesses)</div>
                    <ul class='feedback-box-list'>{weak_html}</ul>
                </div>
                """
            )
            
            st.markdown("<div style='height: 20px;'></div>", unsafe_allow_html=True)
            
            rec_html = "".join([f"<li>{rc}</li>" for rc in feedback.get("recommendations", [])])
            st.html(
                f"""
                <div class='feedback-box box-recommendations'>
                    <div class='feedback-box-title'>💡 Dynamic Recommendations</div>
                    <ul class='feedback-box-list'>{rec_html}</ul>
                </div>
                """
            )

        st.markdown("<div style='height: 40px;'></div>", unsafe_allow_html=True)

        # Action Panel
        col_act1, col_act2, col_act3 = st.columns([1, 1.5, 1])
        with col_act2:
            if st.button("Proceed to Execution Blueprint 🚀", key="proceed_execution_blueprint", use_container_width=True, type="primary"):
                st.session_state.app_phase = "execution_blueprint"
                st.rerun()
                
            if st.button("🔄 Reset Validation", key="reset_validation", use_container_width=True, type="secondary"):
                st.session_state.validation_questions_data = None
                st.session_state.validation_answers = {}
                st.session_state.validation_q_step = 1
                st.session_state.strategy_validation = None
                st.rerun()
