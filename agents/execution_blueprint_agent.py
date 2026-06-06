import streamlit as st
import datetime
import streamlit.components.v1 as components
from services.gemini_service import generate_roadmap_dag_with_gemini
from agents.goal_agent import render_sidebar_api_key
from utils.state_persistence import clear_state_cache

def initialize_roadmap_dag_state():
    """
    Initializes session state variables for the unified Roadmap & Task DAG.
    """
    if "roadmap_dag_data" not in st.session_state:
        st.session_state.roadmap_dag_data = None
    if "blueprint_refinement" not in st.session_state:
        st.session_state.blueprint_refinement = "Default"
    if "task_depth" not in st.session_state:
        st.session_state.task_depth = "Detailed"
    if "task_completions" not in st.session_state:
        st.session_state.task_completions = {}

def render_execution_blueprint_agent():
    """
    Renders the unified Roadmap & Task DAG Builder workspace.
    """
    initialize_roadmap_dag_state()

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

    goal_context = st.session_state.goal_context
    profile_data = st.session_state.profile_data
    strategy = st.session_state.selected_strategy_data
    validation_results = st.session_state.strategy_validation
    api_key = render_sidebar_api_key()

    # Sidebar back-navigation controls
    st.sidebar.html("<h3 style='margin-bottom: 20px;'>Navigation</h3>")
    if st.sidebar.button("👤 View Persona Profile", key="blue_nav_profile", use_container_width=True):
        st.session_state.app_phase = "profiling"
        st.rerun()
    if st.sidebar.button("📋 Back to Validation Audit", key="blue_nav_audit", use_container_width=True):
        st.session_state.app_phase = "strategy_validation"
        st.rerun()
    st.sidebar.html("<hr style='border-color: rgba(255,255,255,0.1); margin: 15px 0;'>")

    # CSS styling injection
    st.html(
        """
        <style>
        .task-header-badge {
            background: rgba(255, 255, 255, 0.05);
            color: #94a3b8;
            border: 1px solid rgba(255, 255, 255, 0.08);
            padding: 2px 8px;
            border-radius: 8px;
            font-size: 0.72rem;
            font-weight: 600;
            margin-left: 8px;
            display: inline-block;
        }
        .task-header-badge-high {
            background: rgba(239, 68, 68, 0.12) !important;
            color: #f87171 !important;
            border: 1px solid rgba(239, 68, 68, 0.25) !important;
        }
        .task-header-badge-medium {
            background: rgba(245, 158, 11, 0.12) !important;
            color: #fbbf24 !important;
            border: 1px solid rgba(245, 158, 11, 0.25) !important;
        }
        .task-header-badge-low {
            background: rgba(16, 185, 129, 0.12) !important;
            color: #34d399 !important;
            border: 1px solid rgba(16, 185, 129, 0.25) !important;
        }
        .task-meta-label {
            font-size: 0.75rem;
            text-transform: uppercase;
            letter-spacing: 1.2px;
            color: #64748b;
            font-weight: 700;
            margin-top: 15px;
            margin-bottom: 5px;
        }
        .task-dep-tag {
            background: rgba(168, 85, 247, 0.12);
            color: #c084fc;
            border: 1px solid rgba(168, 85, 247, 0.25);
            padding: 2px 6px;
            border-radius: 6px;
            font-size: 0.75rem;
            margin-right: 5px;
            display: inline-block;
        }
        div[data-testid="stVerticalBlockBorderWrapper"]:has(.dag-marker) {
            background: rgba(15, 23, 42, 0.3) !important;
            border: 1px solid rgba(255, 255, 255, 0.05) !important;
            border-radius: 16px !important;
            padding: 20px !important;
        }
        .legend-dot {
            height: 10px;
            width: 10px;
            border-radius: 50%;
            display: inline-block;
            margin-right: 6px;
        }
        </style>
        """
    )

    # 1. INITIAL ROADMAP GENERATION
    if not st.session_state.roadmap_dag_data:
        st.html(
            f"""
            <div style='max-width: 800px; margin: 0 auto; padding: 20px 0; text-align: center;'>
                <span class='badge' style='background: rgba(99, 102, 241, 0.1); color: #818cf8; border: 1px solid rgba(99, 102, 241, 0.3); padding: 6px 14px; border-radius: 20px; font-size: 0.85rem; font-weight: 700; letter-spacing: 1.5px;'>PHASE 4: ROADMAP & TASK DAG BUILDER</span>
                <h1 style='font-size: 2.8rem; font-weight: 800; margin-top: 15px; margin-bottom: 10px; background: linear-gradient(to right, #f8fafc, #94a3b8); -webkit-background-clip: text; -webkit-text-fill-color: transparent;'>Build Your Dynamic Execution Graph</h1>
                <p style='color: #94a3b8; font-size: 1.15rem;'>We are merging your milestones timeline with a detailed task backlog, plotting it as an interactive Directed Acyclic Graph (DAG) for tracking.</p>
            </div>
            """
        )
        
        if not api_key:
            st.warning("Please configure your Gemini API Key in the sidebar before proceeding.")

        col1, col2, col3 = st.columns([1, 1.2, 1])
        with col2:
            if st.button("Generate Roadmap & DAG ⚡", use_container_width=True, type="primary", disabled=not api_key):
                with st.spinner("Gemini is formulating your roadmap phases, tasks, and dependencies graph..."):
                    try:
                        roadmap = generate_roadmap_dag_with_gemini(
                            profile_data,
                            goal_context,
                            strategy,
                            validation_results,
                            st.session_state.blueprint_refinement,
                            st.session_state.task_depth,
                            api_key
                        )
                        st.session_state.roadmap_dag_data = roadmap
                        st.rerun()
                    except Exception as e:
                        st.error(f"Failed to generate roadmap: {str(e)}")

    # 2. RENDER WORKSPACE
    else:
        roadmap = st.session_state.roadmap_dag_data
        phases = roadmap.get("phases", [])
        summary = roadmap.get("summary", "")
        roadmap_name = roadmap.get("roadmap_name", "Unified Execution Plan")

        # Pre-populate checkpoint completion statuses if not present
        for phase in phases:
            for task in phase.get("tasks", []):
                task_id = task.get("task_id")
                for idx, _ in enumerate(task.get("subtasks", [])):
                    key = f"{task_id}_{idx}"
                    if key not in st.session_state.task_completions:
                        st.session_state.task_completions[key] = False

        # Calculate Checklist Completions Progress
        total_subtasks = 0
        completed_subtasks = 0
        for phase in phases:
            for task in phase.get("tasks", []):
                task_id = task.get("task_id")
                for idx, _ in enumerate(task.get("subtasks", [])):
                    total_subtasks += 1
                    if st.session_state.task_completions.get(f"{task_id}_{idx}", False):
                        completed_subtasks += 1

        progress_pct = int((completed_subtasks / total_subtasks) * 100) if total_subtasks > 0 else 0

        # Workspace Title
        st.html(
            f"""
            <div style='margin-bottom: 25px; margin-top: 10px;'>
                <span style='font-size: 0.9rem; text-transform: uppercase; letter-spacing: 1.5px; opacity: 0.7; color: #818cf8;'>Unified Coaching Workspace</span>
                <h2 style='font-size: 2.2rem; font-weight: 800; color: #f8fafc; margin-top: 10px; margin-bottom: 5px;'>Roadmap & Task DAG: {roadmap_name}</h2>
                <p style='color: #94a3b8; font-size: 1.05rem;'>Track your milestones in the timeline and check off tasks. The DAG updates dynamically based on checkmarks.</p>
            </div>
            """
        )

        # Progress bar
        st.html(
            f"""
            <div class='gap-container' style='border-left: 4px solid #10b981; margin-bottom: 20px;'>
                <div style='display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;'>
                    <span style='font-size: 0.85rem; text-transform: uppercase; letter-spacing: 1px; color: #10b981; font-weight: 700;'>Milestones Checklist Progress</span>
                    <span style='font-size: 0.95rem; font-weight: 700; color: #f8fafc;'>{progress_pct}% Complete ({completed_subtasks}/{total_subtasks} steps checked)</span>
                </div>
            </div>
            """
        )
        st.progress(completed_subtasks / total_subtasks if total_subtasks > 0 else 0)
        st.markdown("<div style='height: 15px;'></div>", unsafe_allow_html=True)

        # 3. REFINEMENT & CONFIG PANEL
        st.html(
            """
            <div class='refinement-panel' style='padding: 20px 25px; margin-bottom: 30px;'>
                <h5 style='margin: 0 0 15px 0; color: #f8fafc;'>⚙️ Configure Roadmap & Granularity</h5>
            </div>
            """
        )
        
        col_c1, col_c2, col_c3 = st.columns([1, 1, 1])
        refinement_options = [
            "Default", "Faster Completion", "Lower Workload", "Lower Risk", "Higher Learning", "Maximum Growth"
        ]
        depth_options = ["Basic", "Detailed", "Very Detailed"]
        
        with col_c1:
            ref_idx = refinement_options.index(st.session_state.blueprint_refinement) if st.session_state.blueprint_refinement in refinement_options else 0
            sel_ref = st.selectbox("Roadmap Focus Constraints", options=refinement_options, index=ref_idx)
        with col_c2:
            dep_idx = depth_options.index(st.session_state.task_depth) if st.session_state.task_depth in depth_options else 1
            sel_dep = st.selectbox("Checklist Granularity Depth", options=depth_options, index=dep_idx)
        with col_c3:
            st.markdown("<div style='height: 28px;'></div>", unsafe_allow_html=True)
            if st.button("Regenerate Roadmap & DAG ⚡", use_container_width=True, type="primary", disabled=not api_key):
                with st.spinner("Gemini is recalculating phases, checkpoints, and dependencies..."):
                    try:
                        new_roadmap = generate_roadmap_dag_with_gemini(
                            profile_data,
                            goal_context,
                            strategy,
                            validation_results,
                            sel_ref,
                            sel_dep,
                            api_key
                        )
                        st.session_state.roadmap_dag_data = new_roadmap
                        st.session_state.blueprint_refinement = sel_ref
                        st.session_state.task_depth = sel_dep
                        # Reset completions
                        st.session_state.task_completions = {}
                        st.rerun()
                    except Exception as e:
                        st.error(f"Regeneration failed: {str(e)}")

        st.markdown("<div style='height: 25px;'></div>", unsafe_allow_html=True)

        # 4. TWO-COLUMN WORKSPACE
        col_dag, col_list = st.columns([1.1, 1.2], gap="large")

        # Left Column: Task DAG
        with col_dag:
            st.html("<h4>🎨 Task Dependency DAG Graph</h4>")
            
            # Dynamic Mermaid DAG Construction
            mermaid_lines = ["graph TD"]
            # Class definitions
            mermaid_lines.append("classDef default fill:#111827,stroke:#374151,stroke-width:1.5px,color:#9ca3af;")
            mermaid_lines.append("classDef complete fill:#064e3b,stroke:#10b981,stroke-width:2.5px,color:#ecfdf5;")
            mermaid_lines.append("classDef ip fill:#4c1d95,stroke:#a855f7,stroke-width:2.5px,color:#f5f3ff;")

            # Build set of valid task IDs first
            valid_task_ids = set()
            for phase in phases:
                for task in phase.get("tasks", []):
                    t_id = task.get("task_id")
                    if t_id:
                        valid_task_ids.add(t_id.replace(" ", "").strip())

            # Nodes mapping inside subgraphs
            for phase in phases:
                p_num = phase.get("phase_number")
                p_title = phase.get("name", f"Phase {p_num}")
                # Clean title for subgraph name
                clean_p_title = p_title.replace('"', '').replace("'", "").replace("&", "and").replace("[", "").replace("]", "").replace("(", "").replace(")", "").replace(":", "-")
                
                mermaid_lines.append(f"subgraph Phase_{p_num} [\"{clean_p_title}\"]")
                
                for task in phase.get("tasks", []):
                    raw_t_id = task.get("task_id", "")
                    t_id = raw_t_id.replace(" ", "").strip() if raw_t_id else ""
                    if not t_id:
                        continue
                    t_name = task.get("name", "")
                    clean_t_name = t_name.replace('"', "'").replace("&", "and").replace("[", "(").replace("]", ")")
                    
                    if len(clean_t_name) > 28:
                        clean_t_name = clean_t_name[:25] + "..."

                    # Determine status style
                    sub_keys = [f"{raw_t_id}_{i}" for i in range(len(task.get("subtasks", [])))]
                    task_completed = all(st.session_state.task_completions.get(k, False) for k in sub_keys) if sub_keys else False
                    task_started = any(st.session_state.task_completions.get(k, False) for k in sub_keys) if sub_keys else False
                    
                    style_class = ""
                    if task_completed:
                        style_class = ":::complete"
                    elif task_started:
                        style_class = ":::ip"

                    mermaid_lines.append(f"    {t_id}[\"{t_id}: {clean_t_name}\"]{style_class}")
                
                mermaid_lines.append("end")

            # Edges mapping
            for phase in phases:
                for task in phase.get("tasks", []):
                    raw_t_id = task.get("task_id", "")
                    t_id = raw_t_id.replace(" ", "").strip() if raw_t_id else ""
                    if not t_id:
                        continue
                    for dep in task.get("dependencies", []):
                        if isinstance(dep, str):
                            parts = dep.replace(";", ",").split(",")
                            for part in parts:
                                clean_dep = part.replace(" ", "").strip()
                                if clean_dep in valid_task_ids and clean_dep != t_id:
                                    mermaid_lines.append(f"  {clean_dep} --> {t_id}")

            mermaid_string = "\n".join(mermaid_lines)
            print("--- DEBUG MERMAID ---")
            print(mermaid_string)
            print("--- END DEBUG ---")
            
            # Display Diagram inside a styled container
            with st.container(border=True):
                st.html(
                    """
                    <div class='dag-marker'></div>
                    <div style='margin-bottom: 15px; font-size: 0.82rem; color: #94a3b8; display: flex; gap: 15px;'>
                        <div><span class='legend-dot' style='background: #111827; border: 1.5px solid #374151;'></span>Not Started</div>
                        <div><span class='legend-dot' style='background: #4c1d95; border: 1.5px solid #a855f7;'></span>In Progress</div>
                        <div><span class='legend-dot' style='background: #064e3b; border: 1.5px solid #10b981;'></span>Completed</div>
                    </div>
                    """
                )
                # HTML template to load Mermaid from CDN and render it inside the iframe
                mermaid_html = f"""
                <!DOCTYPE html>
                <html>
                <head>
                    <style>
                        body {{
                            background-color: transparent !important;
                            margin: 0;
                            padding: 0;
                            display: flex;
                            justify-content: center;
                            font-family: 'Outfit', 'Inter', sans-serif;
                            color: #cbd5e1;
                            overflow-x: auto;
                        }}
                        #mermaid-container {{
                            width: 100%;
                            display: flex;
                            justify-content: center;
                        }}
                    </style>
                    <script src="https://cdn.jsdelivr.net/npm/mermaid@9.4.3/dist/mermaid.min.js"></script>
                    <script>
                        mermaid.initialize({{
                            startOnLoad: true,
                            theme: 'dark',
                            securityLevel: 'loose',
                            themeVariables: {{
                                background: '#0b0f19',
                                primaryColor: '#111827',
                                primaryTextColor: '#9ca3af',
                                lineColor: '#374151'
                            }}
                        }});
                    </script>
                </head>
                <body>
                    <div id="mermaid-container">
                        <div class="mermaid">
{mermaid_string}
                        </div>
                    </div>
                </body>
                </html>
                """
                components.html(mermaid_html, height=520, scrolling=True)

        # Right Column: Roadmap Timeline & Checklists
        with col_list:
            st.html("<h4>📅 Milestones & Action Checklists</h4>")
            
            for phase in phases:
                p_num = phase.get("phase_number")
                p_name = phase.get("name")
                p_duration = phase.get("duration", "")
                p_objective = phase.get("objective", "")
                p_milestone = phase.get("milestone", "")
                p_criteria = phase.get("success_criteria", "")
                tasks = phase.get("tasks", [])

                st.markdown(
                    f"""
                    <div style='margin-top: 25px; margin-bottom: 15px;'>
                        <h4 style='color: #818cf8; margin-bottom: 2px; font-weight: 800;'>Phase {p_num}: {p_name}</h4>
                        <span style='color: #64748b; font-size: 0.85rem;'><b>Duration:</b> {p_duration} • <b>Milestone:</b> 🏁 {p_milestone}</span>
                    </div>
                    """,
                    unsafe_allow_html=True
                )

                if not tasks:
                    st.info("No tasks found.")
                    continue

                for task in tasks:
                    t_id = task.get("task_id")
                    t_name = task.get("name")
                    t_desc = task.get("description", "")
                    priority = task.get("priority", "Medium")
                    difficulty = task.get("difficulty", "Intermediate")
                    hours = task.get("estimated_hours", 2)
                    deps = task.get("dependencies", [])
                    t_type = task.get("task_type", "Coding")
                    subtasks = task.get("subtasks", [])

                    # Completion status
                    sub_keys = [f"{t_id}_{i}" for i in range(len(subtasks))]
                    task_completed = all(st.session_state.task_completions.get(k, False) for k in sub_keys) if sub_keys else False

                    p_badge_class = "task-header-badge-medium"
                    if priority.lower() == "high":
                        p_badge_class = "task-header-badge-high"
                    elif priority.lower() == "low":
                        p_badge_class = "task-header-badge-low"

                    status_icon = "🟢" if task_completed else "🟡"
                    exp_label = f"{status_icon} [{t_id}] {t_name} (🕒 {hours}h | {priority} Priority)"

                    with st.expander(exp_label, expanded=False):
                        st.html(
                            f"""
                            <p style='color: #cbd5e1; font-size: 0.92rem; line-height: 1.4; margin: 0 0 12px 0;'>{t_desc}</p>
                            <div style='font-size: 0.85rem; margin-bottom: 12px; display: flex; gap: 15px;'>
                                <div><span style='color: #64748b;'>Level:</span> <span class='task-header-badge'>{difficulty}</span></div>
                                <div><span style='color: #64748b;'>Type:</span> <span class='task-header-badge'>{t_type}</span></div>
                                <div><span style='color: #64748b;'>Priority:</span> <span class='task-header-badge {p_badge_class}'>{priority}</span></div>
                            </div>
                            """
                        )

                        if deps:
                            dep_badges = "".join([f"<span class='task-dep-tag'>{d}</span>" for d in deps])
                            st.html(
                                f"""
                                <div style='margin-bottom: 15px;'>
                                    <span style='color: #64748b; font-size: 0.8rem; text-transform: uppercase; font-weight: 700;'>Depends On:</span>
                                    <div style='margin-top: 4px;'>{dep_badges}</div>
                                </div>
                                """
                            )

                        # Checkboxes
                        if subtasks:
                            st.html("<div class='task-meta-label' style='margin-top: 10px; margin-bottom: 8px;'>Action Steps</div>")
                            for idx, sub in enumerate(subtasks):
                                key = f"{t_id}_{idx}"
                                val = st.checkbox(sub, value=st.session_state.task_completions[key], key=f"chk_{key}")
                                if val != st.session_state.task_completions[key]:
                                    st.session_state.task_completions[key] = val
                                    st.rerun()

        # Spacer
        st.markdown("<div style='height: 45px;'></div>", unsafe_allow_html=True)

        # 5. CONTROL PANEL
        col_act1, col_act2, col_act3 = st.columns([1, 1.8, 1])
        with col_act2:
            if st.button("Proceed to Scheduling Workspace 📅", key="complete_dag_journey", use_container_width=True, type="primary"):
                st.session_state.app_phase = "scheduling"
                st.rerun()
                
            st.markdown("<div style='height: 10px;'></div>", unsafe_allow_html=True)
            
            col_reset1, col_reset2 = st.columns([1, 1])
            with col_reset1:
                if st.button("🔄 Reset Checklist Progress", key="reset_checklist_only", use_container_width=True, type="secondary"):
                    st.session_state.task_completions = {k: False for k in st.session_state.task_completions}
                    st.rerun()
            with col_reset2:
                if st.button("🚨 Clear All Data & Reset", key="hard_reset_all", use_container_width=True, type="secondary"):
                    clear_state_cache()
                    st.rerun()
