import textwrap

def get_goal_analysis_prompt(goal_text: str, persona: dict) -> str:
    """
    Constructs a highly structured prompt to analyze a goal in the context of a user's persona.
    Instructs the model to output a JSON object containing the category, difficulty, duration,
    required skills, persona-customized risks, and 5 dynamic questions.
    
    Parameters:
    - goal_text (str): The goal inputted by the user.
    - persona (dict): The user's profiling persona containing 'name', 'strength', 'challenge', 'strategy'.
    
    Returns:
    - str: The fully formatted prompt.
    """
    persona_name = persona.get("name", "Consistent Explorer")
    persona_strength = persona.get("strength", "High curiosity & adaptability")
    persona_challenge = persona.get("challenge", "Maintaining habit consistency")
    persona_strategy = persona.get("strategy", "Micro-habits planning")

    return textwrap.dedent(
        f"""
        Analyze the following user goal in the context of their AI Execution Persona.
        
        User Goal: "{goal_text}"
        
        User Persona Profile:
        - Persona Archetype: {persona_name}
        - Core Strength: {persona_strength}
        - Execution Challenge: {persona_challenge}
        - Recommended Planning Style: {persona_strategy}
        
        You must perform a detailed analysis and generate 5 dynamic, goal-specific questions to gather further context.
        Customize the "risks" and the "dynamic_questions" to align with their persona (e.g. if they struggle with consistency or burnout, ask how they will manage their energy).
        
        Format your response as a single, valid JSON object. Do not include markdown code block wrappers (like ```json), do not include any explanatory text outside the JSON. Return only the raw JSON.
        
        JSON Schema structure required:
        {{
            "category": "String - The industry or category of the goal (e.g. Software Development, Fitness, Language Learning, Business)",
            "difficulty": "String - Assess the difficulty level relative to their goal complexity (Beginner, Intermediate, or Advanced)",
            "estimated_duration": "String - Realistic timeline to achieve this goal (e.g., '6 weeks', '3 months')",
            "required_skills": [
                "List of 3 to 5 critical skills/tools they need to learn or apply"
            ],
            "risks": [
                "List of 3 to 5 key risks or obstacles. Customize at least half of these to target the user's personal execution challenge: {persona_challenge}"
            ],
            "dynamic_questions": [
                "Generate exactly 5 deep, goal-specific questions that will help structure a roadmap. Do not use generic questions. Ensure the questions target details like their current status, technical preferences, availability, and how they will handle their personal challenge: {persona_challenge}"
            ]
        }}
        """
    )


def get_strategy_generation_prompt(goal_context: dict, profile_data: dict, persona: dict) -> str:
    """
    Constructs a highly structured prompt to generate exactly three execution strategies
    (Fast MVP, Balanced Growth, Ambitious Scale) and a personalized recommendation.
    
    Parameters:
    - goal_context (dict): Compiled goal context containing 'goal', 'category', 'difficulty', 'estimated_duration', 'required_skills', 'risks', 'qa_context'.
    - profile_data (dict): User's profile choices.
    - persona (dict): User's execution archetype details.
    
    Returns:
    - str: The fully formatted prompt.
    """
    goal = goal_context.get("goal", "")
    category = goal_context.get("category", "")
    difficulty = goal_context.get("difficulty", "")
    est_duration = goal_context.get("estimated_duration", "")
    required_skills = ", ".join(goal_context.get("required_skills", []))
    risks = "; ".join(goal_context.get("risks", []))
    
    # Format QA Context
    qa_list = []
    for idx, qa in enumerate(goal_context.get("qa_context", [])):
        q = qa.get("question", "")
        a = qa.get("answer", "")
        qa_list.append(f"Q{idx+1}: {q}\nA{idx+1}: {a}")
    qa_formatted = "\n\n".join(qa_list)
    
    # Profile
    user_type = profile_data.get("user_type", "Learner")
    experience_level = profile_data.get("experience_level", "Beginner")
    hours_per_week = profile_data.get("hours_per_week", 10)
    work_style = profile_data.get("work_style", "Balanced Progress")
    motivation_style = profile_data.get("motivation_style", "Progress")
    biggest_challenge = profile_data.get("biggest_challenge", "Inconsistent")
    
    # Persona
    persona_name = persona.get("name", "Consistent Explorer")
    persona_strength = persona.get("strength", "")
    persona_challenge = persona.get("challenge", "")
    persona_strategy = persona.get("strategy", "")
    
    return textwrap.dedent(
        f"""
        You are a world-class startup mentor and execution coach. Your goal is to generate exactly three personalized execution strategies for a user's goal based on their profile, persona, and answers to context questions.
        
        === USER GOAL DETAILS ===
        - Goal: "{goal}"
        - Category: {category}
        - Difficulty: {difficulty}
        - Base Estimated Duration: {est_duration}
        - Required Skills: {required_skills}
        - Goal Risks: {risks}
        
        === USER PROFILE & PERSONA ===
        - User Type: {user_type}
        - Experience Level: {experience_level}
        - Available Time: {hours_per_week} hours/week
        - Preference Work Style: {work_style}
        - Motivation Style: {motivation_style}
        - Biggest Execution Challenge: {biggest_challenge}
        - Persona Archetype: {persona_name}
        - Persona Core Strength: {persona_strength}
        - Persona Execution Challenge: {persona_challenge}
        - Persona Recommended Style: {persona_strategy}
        
        === CONTEXT QUESTIONS & ANSWERS ===
        {qa_formatted}
        
        === TASK ===
        Generate exactly three tailored execution strategies with the keys "fast_mvp", "balanced_growth", and "ambitious_scale".
        
        For each strategy, provide:
        - name: The name of the strategy (e.g. "Fast MVP", "Balanced Growth", "Ambitious Scale" or a highly creative variant personalized for their goal).
        - description: A concise description of how they would execute this goal under this path.
        - pros: At least 2 bullet points highlighting the advantages (e.g. alignment with their strengths, quick validation, low cost).
        - cons: At least 2 bullet points highlighting the trade-offs (e.g. limited scope, higher workload, longer time, risk of perfectionism).
        - estimated_duration: A realistic timeline (e.g. "4 weeks", "3 months", "6 months") tailored to this strategy.
        - effort_level: The intensity of execution ("Low", "Medium", "High").
        
        Recommend exactly one of the three strategies (by setting recommended_strategy_key to either "fast_mvp", "balanced_growth", or "ambitious_scale").
        
        Provide a detailed recommended_explanation explaining why that specific strategy was chosen. You MUST explicitly evaluate and base this recommendation on the following 5 criteria:
        1. Experience: How the strategy fits their {experience_level} level.
        2. Hours per week: How the strategy maps to their availability of {hours_per_week} hours/week.
        3. Budget: Inferred budget constraints (or direct answers from Q&A if present). If no budget was explicitly mentioned, make a logical assumption based on their profile and state it.
        4. Team size: Inferred team size (assume solo unless they specified teammates).
        5. Goal complexity: How it structures progress relative to the goal's overall complexity.
        
        Format your response as a single, valid JSON object. Do not include markdown code block wrappers (like ```json), do not include any explanatory text outside the JSON. Return only the raw JSON.
        
        JSON Schema structure required:
        {{
            "strategies": [
                {{
                    "key": "fast_mvp",
                    "name": "String",
                    "description": "String",
                    "pros": ["String", "String"],
                    "cons": ["String", "String"],
                    "estimated_duration": "String",
                    "effort_level": "String"
                }},
                {{
                    "key": "balanced_growth",
                    "name": "String",
                    "description": "String",
                    "pros": ["String", "String"],
                    "cons": ["String", "String"],
                    "estimated_duration": "String",
                    "effort_level": "String"
                }},
                {{
                    "key": "ambitious_scale",
                    "name": "String",
                    "description": "String",
                    "pros": ["String", "String"],
                    "cons": ["String", "String"],
                    "estimated_duration": "String",
                    "effort_level": "String"
                }}
            ],
            "recommended_strategy_key": "String - must be one of: fast_mvp, balanced_growth, ambitious_scale",
            "recommendation_explanation": "String - detailed explanation addressing all 5 criteria: Experience, Hours per week, Budget, Team size, and Goal complexity."
        }}
        """
    )


def get_strategy_validation_questions_prompt(profile_data: dict, goal_context: dict, strategy: dict) -> str:
    """
    Constructs a prompt to perform gap analysis and generate exactly 3 validation questions.
    """
    # Get user profile details
    user_type = profile_data.get("user_type", "Learner")
    experience_level = profile_data.get("experience_level", "Beginner")
    hours_per_week = profile_data.get("hours_per_week", 10)
    work_style = profile_data.get("work_style", "Balanced Progress")
    biggest_challenge = profile_data.get("biggest_challenge", "Inconsistent")

    # Get goal details
    goal = goal_context.get("goal", "")
    category = goal_context.get("category", "")
    difficulty = goal_context.get("difficulty", "")
    required_skills = ", ".join(goal_context.get("required_skills", []))
    risks = "; ".join(goal_context.get("risks", []))

    # Get strategy details
    strategy_name = strategy.get("name", "Balanced Growth")
    strategy_desc = strategy.get("description", "")
    strategy_duration = strategy.get("estimated_duration", "")
    strategy_effort = strategy.get("effort_level", "")

    return textwrap.dedent(
        f"""
        You are a meticulous project planner and execution auditor. Your task is to perform an initial gap analysis of a user's selected execution strategy for their goal, and generate exactly 3 dynamic follow-up validation questions to test their preparation and readiness.

        === USER GOAL DETAILS ===
        - Goal: "{goal}"
        - Category: {category}
        - Difficulty: {difficulty}
        - Required Skills: {required_skills}
        - Key Risks: {risks}

        === USER PROFILE ===
        - User Type: {user_type}
        - Experience Level: {experience_level}
        - Available Time: {hours_per_week} hours/week
        - Work Style Preference: {work_style}
        - Main Obstacle: {biggest_challenge}

        === SELECTED STRATEGY ===
        - Strategy Option: {strategy_name}
        - Description: {strategy_desc}
        - Estimated Duration: {strategy_duration}
        - Effort Level: {strategy_effort}

        === ANALYSIS CRITERIA ===
        Analyze potential gaps in the following areas:
        1. Missing Skills: What skills might they be missing to execute this specific strategy?
        2. Missing Resources: What materials, software, hardware, or access do they need?
        3. Missing Knowledge: What domain expertise or validation steps are missing?
        4. Time Constraints: Is their availability ({hours_per_week} hrs/week) sufficient for the strategy's timeline ({strategy_duration}) and effort ({strategy_effort})?
        5. Risks: What execution obstacles could lead to their main failure mode ({biggest_challenge})?

        Generate exactly 3 follow-up validation questions. Ensure the questions adapt to the Goal Type, Strategy, and User Profile. Avoid generic questions; make them deep, conversational, and highly specific to the gaps you identify (e.g. asking about tools, specific learning resources, scheduling conflicts, or contingency plans).

        Format your response as a single, valid JSON object. Do not include markdown code block wrappers (like ```json), do not include any explanatory text outside the JSON. Return only the raw JSON.

        JSON Schema structure required:
        {{
            "analysis": {{
                "missing_skills": ["List of potential skill gaps"],
                "missing_resources": ["List of potential resource/tool gaps"],
                "missing_knowledge": ["List of potential domain knowledge/validation gaps"],
                "time_constraints": ["Evaluation of timeline and schedule challenges"],
                "risks": ["Custom strategy execution risks"]
            }},
            "validation_questions": [
                "Question 1 (focused on skills/knowledge/validation gaps)",
                "Question 2 (focused on resource requirements/tool access)",
                "Question 3 (focused on time management/contingency plan for their biggest obstacle: {biggest_challenge})"
            ]
        }}
        """
    )


def get_strategy_readiness_evaluation_prompt(profile_data: dict, goal_context: dict, strategy: dict, qa_list: list) -> str:
    """
    Constructs a prompt to grade responses to validation questions and return quantitative scores and qualitative summaries.
    """
    # Get user profile details
    user_type = profile_data.get("user_type", "Learner")
    experience_level = profile_data.get("experience_level", "Beginner")
    hours_per_week = profile_data.get("hours_per_week", 10)
    work_style = profile_data.get("work_style", "Balanced Progress")
    biggest_challenge = profile_data.get("biggest_challenge", "Inconsistent")

    # Get goal details
    goal = goal_context.get("goal", "")
    category = goal_context.get("category", "")
    difficulty = goal_context.get("difficulty", "")

    # Get strategy details
    strategy_name = strategy.get("name", "Balanced Growth")
    strategy_desc = strategy.get("description", "")
    strategy_duration = strategy.get("estimated_duration", "")
    strategy_effort = strategy.get("effort_level", "")

    # Format Validation Q&As
    qa_formatted_list = []
    for idx, qa in enumerate(qa_list):
        q = qa.get("question", "")
        a = qa.get("answer", "")
        qa_formatted_list.append(f"Validation Question {idx+1}: {q}\nUser Answer {idx+1}: {a}")
    qa_formatted = "\n\n".join(qa_formatted_list)

    return textwrap.dedent(
        f"""
        You are a veteran execution coach and strategy validator. The user has provided answers to 3 follow-up validation questions regarding their chosen strategy. You must evaluate their answers, calculate quantitative readiness scores, and generate detailed qualitative insights.

        === USER PROFILE & GOAL ===
        - Goal: "{goal}" ({category} • {difficulty} level)
        - Profile: {user_type} • {experience_level} Experience • {hours_per_week} hours/week • Biggest Challenge: {biggest_challenge}
        - Chosen Strategy: {strategy_name} ({strategy_desc} • Timeline: {strategy_duration} • Effort: {strategy_effort})

        === VALIDATION Q&A RESPONSES ===
        {qa_formatted}

        === EVALUATION CRITERIA ===
        Evaluate their answers to assess:
        1. Skill Readiness: How prepared are they skill-wise? Do they know how to address skill gaps? (Score: 0 to 100)
        2. Resource Readiness: Do they have or know how to get all tools, templates, systems, or environments needed? (Score: 0 to 100)
        3. Time Readiness: Is their schedule realistic? Do they have a solid plan to allocate {hours_per_week} hours/week around obstacles? (Score: 0 to 100)
        4. Overall Readiness: The weighted average score reflecting their overall execution safety and preparation. (Score: 0 to 100)

        Generate clear bullet-pointed lists for:
        - strengths: Areas where the user is highly prepared or has solid plans.
        - weaknesses: Remaining preparation vulnerabilities, resource shortages, or skill deficits.
        - potential_risks: Threat vectors that could detail their execution (especially relating to consistency/overwhelm/loss of motivation).
        - recommendations: Actionable, immediate steps they should take to improve their readiness before launching.

        Format your response as a single, valid JSON object. Do not include markdown code block wrappers (like ```json), do not include any explanatory text outside the JSON. Return only the raw JSON.

        JSON Schema structure required:
        {{
            "skill_readiness_score": Integer (0 to 100),
            "resource_readiness_score": Integer (0 to 100),
            "time_readiness_score": Integer (0 to 100),
            "overall_readiness_score": Integer (0 to 100),
            "strengths": ["Strength bullet point 1", "Strength bullet point 2"],
            "weaknesses": ["Weakness bullet point 1", "Weakness bullet point 2"],
            "potential_risks": ["Risk bullet point 1", "Risk bullet point 2"],
            "recommendations": ["Recommendation bullet point 1", "Recommendation bullet point 2"]
        }}
        """
    )


def get_execution_blueprint_prompt(profile_data: dict, goal_context: dict, strategy: dict, validation_results: dict, refinement_choice: str) -> str:
    """
    Constructs a highly structured prompt to generate a personalized 3-7 phase execution roadmap
    incorporating a specific refinement adjustment choice.
    """
    # Get profile details
    user_type = profile_data.get("user_type", "Learner")
    experience_level = profile_data.get("experience_level", "Beginner")
    hours_per_week = profile_data.get("hours_per_week", 10)
    work_style = profile_data.get("work_style", "Balanced Progress")
    biggest_challenge = profile_data.get("biggest_challenge", "Inconsistent")

    # Get goal details
    goal = goal_context.get("goal", "")
    category = goal_context.get("category", "")
    difficulty = goal_context.get("difficulty", "")
    required_skills = ", ".join(goal_context.get("required_skills", []))

    # Get strategy details
    strategy_name = strategy.get("name", "Balanced Growth")
    strategy_desc = strategy.get("description", "")
    strategy_duration = strategy.get("estimated_duration", "")

    # Format Validation Scores and Findings
    scores = validation_results.get("scores", {})
    feedback = validation_results.get("feedback", {})
    v_strengths = "; ".join(feedback.get("strengths", []))
    v_weaknesses = "; ".join(feedback.get("weaknesses", []))
    v_risks = "; ".join(feedback.get("potential_risks", []))
    v_recs = "; ".join(feedback.get("recommendations", []))

    return textwrap.dedent(
        f"""
        You are a veteran Chief Product Officer and execution coach. Your goal is to generate a comprehensive, highly personalized step-by-step execution roadmap (consisting of exactly 3 to 7 phases) for the user's goal based on their profile, chosen strategy, validation audit, and a selected refinement style.

        === USER PROFILE & ARCHETYPE ===
        - Goal: "{goal}" ({category} • {difficulty} level)
        - Archetype: {user_type} ({experience_level} level)
        - Available time: {hours_per_week} hours/week
        - Work Preference: {work_style}
        - Main obstacle challenge: {biggest_challenge}

        === SELECTED STRATEGY ===
        - Strategy Option: {strategy_name}
        - Description: {strategy_desc}
        - Total Estimated Duration: {strategy_duration}

        === STRATEGY VALIDATION RESULTS ===
        - Readiness Scores:
          * Skill Readiness: {scores.get("skill_readiness")}%
          * Resource Readiness: {scores.get("resource_readiness")}%
          * Time Readiness: {scores.get("time_readiness")}%
          * Overall Readiness: {scores.get("overall_readiness")}%
        - Audit Findings:
          * Key Strengths: {v_strengths}
          * Highlighted Weaknesses: {v_weaknesses}
          * Critical Risks: {v_risks}
          * Coach Recommendations: {v_recs}

        === ROADMAP REFINEMENT STYLE ===
        Apply this custom constraint: **{refinement_choice}**

        How to structure the phases based on this constraint:
        - "Default": Provide a balanced, standard execution timeline aligning with the selected strategy.
        - "Faster Completion": Focus on launch speed. Compress timelines by 20-30%, recommend parallel tasks, and defer non-essential features/learning.
        - "Lower Workload": Adjust for lower stress. Divide phases into smaller milestone increments, stretch timelines, and suggest micro-tasks fitting into small sessions.
        - "Lower Risk": Prioritize execution safety. Build in explicit validation checkpoints, testing buffers, and fallback plans to mitigate the challenge: {biggest_challenge}.
        - "Higher Learning": Prioritize skill acquisition. Dedicate Phase 1/2 to spikes, research, tutorials, and prototype testing to build the required skills: {required_skills}.
        - "Maximum Growth": Scale up the objectives. Expand the blueprint to include launch prep, user feedback loops, metrics tracking, or production-grade architecture setups.

        === OUTPUT FORMAT ===
        Generate exactly 3 to 7 phases.
        For each phase, provide:
        - phase_number: Integer (1 to total phases)
        - name: Concise, premium name (e.g. "Phase 1: Foundation & Spikes", "Phase 2: Core Architecture Build", etc.)
        - objective: Clear focus and list of top deliverables for this phase
        - milestone: The concrete result/outcome that marks the end of this phase
        - success_criteria: A checklist or verifiable metric indicating the phase is successfully completed
        - duration: Estimated duration (e.g. "Weeks 1-2" or "Days 1-7")
        - dependencies: List of string names or numbers of preceding phases (e.g. [] for Phase 1, or ["Phase 1"] for Phase 2)

        Format your response as a single, valid JSON object. Do not include markdown code block wrappers (like ```json), do not include any explanatory text outside the JSON. Return only the raw JSON.

        JSON Schema structure required:
        {{
            "blueprint_name": "String - e.g. 'Consistent Launch Roadmap'",
            "summary": "String - brief high-level overview of the roadmap adjusted for the refinement style",
            "phases": [
                {{
                    "phase_number": Integer,
                    "name": "String",
                    "objective": "String",
                    "milestone": "String",
                    "success_criteria": "String",
                    "duration": "String",
                    "dependencies": ["String"]
                }}
            ]
        }}
        """
    )


def get_task_breakdown_prompt(profile_data: dict, goal_context: dict, strategy: dict, validation_results: dict, blueprint: dict, depth: str) -> str:
    """
    Constructs a highly structured prompt to generate a detailed list of tasks and subtasks
    for each phase of the execution blueprint, customized to the user's archetype and requested depth.
    """
    # Profile
    user_type = profile_data.get("user_type", "Learner")
    experience_level = profile_data.get("experience_level", "Beginner")
    hours_per_week = profile_data.get("hours_per_week", 10)
    work_style = profile_data.get("work_style", "Balanced Progress")
    biggest_challenge = profile_data.get("biggest_challenge", "Inconsistent")

    # Goal
    goal = goal_context.get("goal", "")
    category = goal_context.get("category", "")
    difficulty = goal_context.get("difficulty", "")
    required_skills = ", ".join(goal_context.get("required_skills", []))

    # Strategy & Validation
    strategy_name = strategy.get("name", "Balanced Growth")
    scores = validation_results.get("scores", {})
    overall_readiness = scores.get("overall_readiness", 50)

    # Format Blueprint Phases
    phases_formatted_list = []
    for phase in blueprint.get("phases", []):
        num = phase.get("phase_number", 1)
        name = phase.get("name", "")
        objective = phase.get("objective", "")
        milestone = phase.get("milestone", "")
        duration = phase.get("duration", "")
        phases_formatted_list.append(
            f"Phase {num}: {name}\n- Duration: {duration}\n- Objective: {objective}\n- Target Milestone: {milestone}"
        )
    phases_formatted = "\n\n".join(phases_formatted_list)

    return textwrap.dedent(
        f"""
        You are an elite agile project manager and execution scrum master. Your task is to breakdown the execution blueprint phases into a highly actionable backlog of tasks and subtasks.

        === USER PROFILE & COACHING CONTEXT ===
        - Goal: "{goal}" ({category} • {difficulty} difficulty)
        - User Archetype: {user_type} ({experience_level} level)
        - Available hours: {hours_per_week} hours/week
        - Preference style: {work_style}
        - Main challenge obstacle: {biggest_challenge}
        - Strategy Choice: {strategy_name}
        - Audit Overall Readiness Score: {overall_readiness}%

        === EXECUTION BLUEPRINT PHASES ===
        {phases_formatted}

        === TASK BREAKDOWN GRANULARITY SPECIFICATION ===
        You must structure tasks matching this depth request: **{depth}**

        Rules for depth levels:
        - "Basic": Generate exactly 2-3 high-level tasks per phase. Subtasks should contain 1-2 items outlining general directions.
        - "Detailed": Generate exactly 3-5 tasks per phase. Subtasks should contain 3-4 items outlining concrete deliverables, setups, or actions.
        - "Very Detailed": Generate exactly 5-8 highly granular tasks per phase. Subtasks should contain 4-6 items detailing exact coding steps, CLI commands, specific files to modify, learning tutorials to watch, or tests to run.

        === USER PERSONALIZATION CONSTRAINTS ===
        - Experience Level ({experience_level}):
          * Beginner: Provide more "Learning" and "Setup" tasks, with detailed descriptions of tools and simple step-by-step guidance.
          * Advanced: Focus on performance, security, architecture design, and automation tasks. Keep descriptions succinct but structurally advanced.
        - Weekly Availability ({hours_per_week} hrs/week):
          * Ensure estimated hours per task do not exceed user availability for the phase duration. Break large tasks into small chunks (e.g. 1-4 hours each).
        - Work Style ({work_style}):
          * Quick Wins: Structure tasks with lower estimated hours (1-2 hours) to allow rapid completions.
          * Deep Focus: Structure tasks into larger, cohesive deep work sessions (3-6 hours).

        === OUTPUT JSON SCHEMA ===
        For each blueprint phase, generate a list of tasks.
        Each task must contain:
        - task_id: Unique string identifier format "T[PhaseNumber]_[TaskNumber]" (e.g., "T1_1", "T1_2", "T2_1").
        - name: Concise, actionable task name.
        - description: Clear explanation of what needs to be done.
        - subtasks: List of string checklist items (complying with the depth level rules).
        - priority: "High", "Medium", or "Low".
        - difficulty: "Beginner", "Intermediate", or "Advanced".
        - estimated_hours: Integer hours required (e.g., 2, 4).
        - dependencies: List of string task_ids that must be completed first (e.g., ["T1_1"]).
        - task_type: "Setup", "Learning", "Research", "Coding", "Testing", or "Validation".

        Format your response as a single, valid JSON object. Do not include markdown code block wrappers (like ```json), do not include any explanatory text outside the JSON. Return only the raw JSON.

        Required JSON structure:
        {{
            "blueprint_id": "String",
            "depth": "String - Basic/Detailed/Very Detailed",
            "tasks_by_phase": [
                {{
                    "phase_number": Integer,
                    "phase_name": "String",
                    "tasks": [
                        {{
                            "task_id": "String",
                            "name": "String",
                            "description": "String",
                            "subtasks": ["String"],
                            "priority": "String",
                            "difficulty": "String",
                            "estimated_hours": Integer,
                            "dependencies": ["String"],
                            "task_type": "String",
                            "subtasks": ["String"]
                        }}
                    ]
                }}
            ]
        }}
        """
    )


def get_roadmap_dag_prompt(profile_data: dict, goal_context: dict, strategy: dict, validation_results: dict, refinement_choice: str, depth: str) -> str:
    """
    Constructs a prompt to generate a single cohesive JSON payload containing phases, tasks, subtasks,
    dependencies, and estimations, optimized by refinement style and checkpoint depth.
    """
    # Profile
    user_type = profile_data.get("user_type", "Learner")
    experience_level = profile_data.get("experience_level", "Beginner")
    hours_per_week = profile_data.get("hours_per_week", 10)
    work_style = profile_data.get("work_style", "Balanced Progress")
    biggest_challenge = profile_data.get("biggest_challenge", "Inconsistent")

    # Goal
    goal = goal_context.get("goal", "")
    category = goal_context.get("category", "")
    difficulty = goal_context.get("difficulty", "")
    required_skills = ", ".join(goal_context.get("required_skills", []))

    # Strategy & Validation
    strategy_name = strategy.get("name", "Balanced Growth")
    strategy_desc = strategy.get("description", "")
    strategy_duration = strategy.get("estimated_duration", "")
    scores = validation_results.get("scores", {})
    v_feedback = validation_results.get("feedback", {})
    v_strengths = "; ".join(v_feedback.get("strengths", []))
    v_weaknesses = "; ".join(v_feedback.get("weaknesses", []))
    v_risks = "; ".join(v_feedback.get("potential_risks", []))
    v_recs = "; ".join(v_feedback.get("recommendations", []))

    return textwrap.dedent(
        f"""
        You are a master product manager, software architect, and execution coach. Your goal is to generate a single unified Execution Roadmap and Task dependency schema (consisting of exactly 3 to 7 phases) for the user's goal based on their profile, chosen strategy, validation audit, and optimization preferences.

        === USER PROFILE & COACHING CONTEXT ===
        - Goal: "{goal}" ({category} • {difficulty} difficulty)
        - User Archetype: {user_type} ({experience_level} level)
        - Available hours: {hours_per_week} hours/week
        - Work Preference style: {work_style}
        - Main obstacle challenge: {biggest_challenge}
        - Strategy Choice: {strategy_name} ({strategy_desc} • Timeline: {strategy_duration})

        === AUDIT VALIDATION RESULTS ===
        - Readiness: Skill {scores.get("skill_readiness")}% • Resource {scores.get("resource_readiness")}% • Time {scores.get("time_readiness")}% • Overall {scores.get("overall_readiness")}%
        - Strengths: {v_strengths}
        - Weaknesses: {v_weaknesses}
        - Critical Risks: {v_risks}
        - Coach Recommendations: {v_recs}

        === ROADMAP REFINEMENT STYLE (CONSTRAINTS) ===
        Apply this custom constraint: **{refinement_choice}**
        - "Default": Balanced standard roadmap.
        - "Faster Completion": Compress timelines by 20-30%, recommend parallel tasks, defer non-essential items.
        - "Lower Workload": Stretch timelines, break into smaller milestones, schedule micro-tasks fitting smaller sessions.
        - "Lower Risk": Add explicit testing buffers, fallback plans, and strict validation checkpoints.
        - "Higher Learning": Dedicate early phases to spikes, tutorials, documentation, and prototyping.
        - "Maximum Growth": Scale up objectives to include launch prep, marketing setups, metrics tracking, or production architecture.

        === TASK BREAKDOWN GRANULARITY ===
        Structure task listings matching this depth: **{depth}**
        - "Basic": 2-3 high-level tasks per phase. Subtasks contain 1-2 general directions.
        - "Detailed": 3-5 tasks per phase. Subtasks contain 3-4 concrete steps.
        - "Very Detailed": 5-8 highly granular tasks per phase. Subtasks contain 4-6 specific steps detailing commands, files, or specific tutorial goals.
        Personalize task difficulty for the user's {experience_level} level and {hours_per_week} hours/week availability.

        === TASK DEPENDENCIES & DAG (DIRECTED ACYCLIC GRAPH) ===
        Assign dependencies carefully:
        - Each task must have a unique ID: "T[PhaseNumber]_[TaskNumber]" (e.g., "T1_1", "T1_2", "T2_1").
        - List dependencies as task IDs that must be completed *before* starting this task.
        - Ensure there are NO circular dependencies.

        === OUTPUT FORMAT ===
        Return exactly 3 to 7 phases.
        For each phase, provide:
        - phase_number: Integer (1 to total phases)
        - name: Phase name (e.g. "Phase 1: Setup & Spike")
        - duration: Estimated duration (e.g. "Weeks 1-2")
        - objective: High-level focus of the phase
        - milestone: The concrete result/outcome marking the end of the phase
        - success_criteria: Verification check indicating phase completion
        - tasks: List of tasks in this phase.

        Format your response as a single, valid JSON object. Do not include markdown code block wrappers (like ```json), do not include any explanatory text outside the JSON. Return only the raw JSON.

        Required JSON structure:
        {{
            "roadmap_name": "String",
            "summary": "String",
            "phases": [
                {{
                    "phase_number": Integer,
                    "name": "String",
                    "duration": "String",
                    "objective": "String",
                    "milestone": "String",
                    "success_criteria": "String",
                    "tasks": [
                        {{
                            "task_id": "String",
                            "name": "String",
                            "description": "String",
                            "priority": "String - High/Medium/Low",
                            "difficulty": "String - Beginner/Intermediate/Advanced",
                            "estimated_hours": Integer,
                            "dependencies": ["String"],
                            "task_type": "String",
                            "subtasks": ["String"]
                        }}
                    ]
                }}
            ]
        }}
        """
    )


def get_scheduling_prompt(profile_data: dict, goal_context: dict, selected_strategy: dict, roadmap_dag_data: dict) -> str:
    """
    Constructs a highly structured prompt to generate a personalized weekly and daily schedule
    along with buffer time allocation, confidence score, and rescheduling suggestions.
    """
    # Profile
    user_type = profile_data.get("user_type", "Learner")
    experience_level = profile_data.get("experience_level", "Beginner")
    hours_per_week = profile_data.get("hours_per_week", 10)
    work_style = profile_data.get("work_style", "Balanced Progress")
    motivation_style = profile_data.get("motivation_style", "Progress")
    biggest_challenge = profile_data.get("biggest_challenge", "Inconsistent")

    # Goal
    goal = goal_context.get("goal", "")
    category = goal_context.get("category", "")
    difficulty = goal_context.get("difficulty", "")

    # Strategy
    strategy_name = selected_strategy.get("name", "Balanced Growth")
    strategy_desc = selected_strategy.get("description", "")
    strategy_duration = selected_strategy.get("estimated_duration", "")

    # Format Roadmap Phases and Tasks for context
    roadmap_formatted_list = []
    for phase in roadmap_dag_data.get("phases", []):
        p_num = phase.get("phase_number", 1)
        p_name = phase.get("name", "")
        p_duration = phase.get("duration", "")
        tasks = []
        for task in phase.get("tasks", []):
            tasks.append(
                f"  - {task.get('task_id')}: {task.get('name')} (Est: {task.get('estimated_hours')} hrs, Priority: {task.get('priority')})"
            )
        tasks_str = "\n".join(tasks)
        roadmap_formatted_list.append(
            f"Phase {p_num}: {p_name} ({p_duration})\n{tasks_str}"
        )
    roadmap_formatted = "\n\n".join(roadmap_formatted_list)

    return textwrap.dedent(
        f"""
        You are an elite productivity strategist and dynamic scheduling agent. Your goal is to convert an execution roadmap and task dependency list into a highly structured, realistic weekly and daily schedule.

        === USER PROFILE & COACHING CONTEXT ===
        - Goal: "{goal}" ({category} • {difficulty} difficulty)
        - User Archetype: {user_type} ({experience_level} level)
        - Available hours: {hours_per_week} hours/week
        - Work Preference style: {work_style}
        - Main obstacle challenge: {biggest_challenge}
        - Strategy Choice: {strategy_name} ({strategy_desc} • Timeline: {strategy_duration})

        === EXECUTION ROADMAP & TASKS ===
        {roadmap_formatted}

        === SCHEDULING CONSTRAINTS & PERSONALIZATION RULES ===
        1. **Hours Per Week Limit**: You must NOT allocate more than {hours_per_week} hours of work in a single week. 
        2. **Work Style ({work_style})**:
           - "Quick Wins": Distribute tasks in short daily blocks (1-2 hours) to maintain dopamine loops.
           - "Deep Focus": Consolidate hours into larger chunks (3-5 hours) on fewer days (e.g. 2-3 deep days per week).
           - "Balanced Progress": Smoothly distribute hours across the week (e.g. 1.5-2 hours every day).
        3. **Experience Level ({experience_level})**:
           - Beginner: Build in at least 15-20% extra buffer time for learning curves and obstacles.
           - Advanced: Streamline the scheduling with tight, efficient blocks.
        4. **Dependencies**: Ensure task order strictly respects the dependencies specified in the roadmap (e.g., don't schedule a task before its dependencies are complete).

        === OUTPUT FORMAT ===
        Generate a complete Weekly Schedule, Daily Task Allocation, and Schedule Analysis.
        
        The `weekly_schedule` should map tasks to each week (Week 1, Week 2, etc.) up to the estimated duration of the strategy.
        The `daily_schedule` should detail how tasks are scheduled day-by-day (e.g., Monday through Sunday for active days). Include realistic time slots (e.g. "09:00 AM - 11:00 AM") that respect the selected work style.
        The `schedule_analysis` must include:
        - `confidence_score` (Integer 0-100) representing how likely the user is to maintain this schedule given their profile and challenge ({biggest_challenge}).
        - `goal_completion_forecast` (String) predicting the final completion date or duration.
        - `buffer_time_allocation` (String) explaining where buffers were built in (e.g., "1.5 hours of weekly buffer added on Friday").
        - `deadline_feasibility_analysis` (String) evaluation of timeline feasibility.
        - `rescheduling_suggestions` (Array) of exactly 3 actionable rescheduling recommendations if they fall behind.

        Format your response as a single, valid JSON object. Do not include markdown code block wrappers (like ```json), do not include any explanatory text outside the JSON. Return only the raw JSON.

        Required JSON structure:
        {{
            "weekly_schedule": [
                {{
                    "week_number": Integer,
                    "focus": "String - major theme/milestone for this week",
                    "allocated_hours": Float,
                    "tasks": [
                        {{
                            "task_id": "String",
                            "name": "String",
                            "allocated_hours": Float
                        }}
                    ]
                }}
            ],
            "daily_schedule": [
                {{
                    "week_number": Integer,
                    "day_number": Integer,
                    "day_name": "String - e.g., Monday, Tuesday",
                    "total_hours": Float,
                    "time_blocks": [
                        {{
                            "task_id": "String",
                            "name": "String",
                            "time_slot": "String - e.g. 09:00 AM - 11:00 AM",
                            "duration_hours": Float,
                            "type": "String - Setup/Coding/Learning/etc."
                        }}
                    ]
                }}
            ],
            "schedule_analysis": {{
                "confidence_score": Integer,
                "goal_completion_forecast": "String",
                "buffer_time_allocation": "String",
                "deadline_feasibility_analysis": "String",
                "rescheduling_suggestions": [
                    {{
                        "id": "String - unique short ID, e.g. 'buffer_boost'",
                        "title": "String",
                        "description": "String",
                        "impact": "String"
                    }}
                ]
            }}
        }}
        """
    )


def get_weekly_reflection_prompt(profile_data: dict, goal_context: dict, progress_summary: dict) -> str:
    """
    Constructs a prompt to generate a personalized weekly progress reflection and coaching guidance.
    """
    user_type = profile_data.get("user_type", "Learner")
    experience_level = profile_data.get("experience_level", "Beginner")
    hours_per_week = profile_data.get("hours_per_week", 10)
    work_style = profile_data.get("work_style", "Balanced Progress")
    biggest_challenge = profile_data.get("biggest_challenge", "Inconsistent")

    goal = goal_context.get("goal", "")
    category = goal_context.get("category", "")
    difficulty = goal_context.get("difficulty", "")

    # Progress details
    health_score = progress_summary.get("health_score", 100)
    completion_rate = progress_summary.get("completion_rate", 0)
    streak_count = progress_summary.get("streak_count", 0)
    overdue_count = progress_summary.get("overdue_count", 0)
    total_hours_spent = progress_summary.get("total_hours_spent", 0.0)
    completed_tasks_count = progress_summary.get("completed_tasks_count", 0)
    total_tasks_count = progress_summary.get("total_tasks_count", 0)
    overdue_tasks = ", ".join(progress_summary.get("overdue_tasks_names", [])) or "None"

    return textwrap.dedent(
        f"""
        You are an elite, highly empathetic AI execution coach. Your goal is to analyze the user's progress for their goal, evaluate their performance metrics, identify bottlenecks (especially relative to their biggest execution challenge), and provide custom coaching feedback.

        === USER PROFILE & COACHING CONTEXT ===
        - Goal: "{goal}" ({category} • {difficulty} difficulty)
        - User Archetype: {user_type} ({experience_level} level)
        - Scheduled availability: {hours_per_week} hours/week
        - Work style: {work_style}
        - Main obstacle/challenge: {biggest_challenge}

        === CURRENT PROGRESS METRICS ===
        - Execution Health Score: {health_score}/100
        - Overall Goal Completion: {completion_rate}% ({completed_tasks_count}/{total_tasks_count} tasks completed)
        - Cumulative Hours Spent: {total_hours_spent} hours
        - Active Streak: {streak_count} days
        - Overdue Tasks Count: {overdue_count}
        - Overdue Tasks list: {overdue_tasks}

        === TASK ===
        Generate a thoughtful execution reflection. Your response must address:
        1. **Bottleneck Diagnostics**: If they have overdue tasks, identify the likely cause based on their profile challenge ({biggest_challenge}) and suggest how to resolve it. If no tasks are overdue, congratulate them on their consistency.
        2. **Streak & Momentum**: Review their streak of {streak_count} days and describe how to keep the momentum high.
        3. **Tactical Strategy Adjustments**: Provide 2-3 specific, actionable tweaks to their weekly routines, buffers, or task handling.
        4. **Encouragement**: A high-impact coaching statement.

        Format your response as a single, valid JSON object. Do not include markdown code block wrappers (like ```json), do not include any explanatory text outside the JSON. Return only the raw JSON.

        Required JSON structure:
        {{
            "reflection": "String - detailed coaching feedback formatted in clean markdown paragraphs",
            "suggested_adjustments": [
                "Specific, concrete adjustments mapping to their performance and work style"
            ],
            "encouragement_quote": "String - a short, high-impact motivational quote to close the session"
        }}
        """
    )


def get_coaching_briefing_prompt(
    profile_data: dict,
    goal_context: dict,
    selected_strategy: dict,
    readiness_results: dict,
    roadmap_dag_data: dict,
    schedule_data: dict,
    progress_metrics: dict,
    weekly_reflections: list
) -> str:
    """
    Constructs a highly structured prompt to generate a cohesive coaching briefing JSON object.
    """
    # Profile
    user_type = profile_data.get("user_type", "Learner")
    experience_level = profile_data.get("experience_level", "Beginner")
    hours_per_week = profile_data.get("hours_per_week", 10)
    work_style = profile_data.get("work_style", "Balanced Progress")
    motivation_style = profile_data.get("motivation_style", "Progress")
    biggest_challenge = profile_data.get("biggest_challenge", "Inconsistent")

    # Goal
    goal = goal_context.get("goal", "")
    category = goal_context.get("category", "")
    difficulty = goal_context.get("difficulty", "")

    # Strategy
    strategy_name = selected_strategy.get("name", "Balanced Growth")
    strategy_desc = selected_strategy.get("description", "")
    strategy_duration = selected_strategy.get("estimated_duration", "")

    # Validation
    v_scores = readiness_results.get("scores", {})
    overall_readiness = v_scores.get("overall_readiness", 50)

    # Schedule
    weekly_sched = schedule_data.get("weekly_schedule", [])
    schedule_analysis = schedule_data.get("schedule_analysis", {})
    confidence_score = schedule_analysis.get("confidence_score", 80)
    forecast = schedule_analysis.get("goal_completion_forecast", "")

    # Progress Telemetry
    health_score = progress_metrics.get("health_score", 100)
    completion_rate = progress_metrics.get("overall_completion_pct", 0)
    streak_count = progress_metrics.get("streak_count", 0)
    overdue_count = progress_metrics.get("overdue_tasks_count", 0)
    total_hours_spent = progress_metrics.get("total_hours_spent", 0.0)
    completed_tasks = progress_metrics.get("completed_tasks", 0)
    total_tasks = progress_metrics.get("total_tasks", 0)
    overdue_tasks = ", ".join(progress_metrics.get("overdue_tasks_names", [])) or "None"

    # Reflections
    reflection_logs = ""
    for idx, ref in enumerate(weekly_reflections[:3]):
        timestamp = ref.get("timestamp", "N/A")
        text = ref.get("reflection", "")
        encouragement = ref.get("encouragement_quote", "")
        reflection_logs += f"[{timestamp}] Reflection:\n{text}\nEncouragement Quote: {encouragement}\n\n"

    return textwrap.dedent(
        f"""
        You are the ultimate AI Execution Coach for Agent OnboardX. Your mission is to analyze all telemetry, goal context, schedules, and progress details of a user to produce a highly personalized coaching brief and prepare state payloads for downstream agents.

        === USER PROFILE & ARCHETYPE ===
        - User Type: {user_type}
        - Experience Level: {experience_level}
        - Availability: {hours_per_week} hours/week
        - Preference Work Style: {work_style}
        - Motivation Driver: {motivation_style}
        - Main obstacle: {biggest_challenge}

        === GOAL & STRATEGY ===
        - Goal: "{goal}" ({category} • {difficulty} level)
        - Strategy Chosen: {strategy_name} ({strategy_desc})
        - Strategy Target Duration: {strategy_duration}
        - Strategy Readiness Audit Score: {overall_readiness}%

        === EXECUTION SCHEDULE ===
        - Total weeks scheduled: {len(weekly_sched)} weeks
        - Confidence Score of Scheduler: {confidence_score}%
        - Scheduler Timeline Forecast: {forecast}

        === PROGRESS & TELEMETRY ===
        - Current Execution Health: {health_score}/100
        - Overall Goal Completion: {completion_rate}% ({completed_tasks}/{total_tasks} tasks done)
        - Cumulative Hours Logged: {total_hours_spent} hours
        - Active Streak: {streak_count} days
        - Overdue Tasks Count: {overdue_count}
        - Overdue Tasks list: {overdue_tasks}

        === PAST COACH REFLECTIONS ===
        {reflection_logs or "No past reflection logs found."}

        === INSTRUCTIONS ===
        You must perform a detailed analysis and generate a comprehensive JSON briefing. Every field should be customized to the user's specific context.

        Required JSON Fields:
        1. "daily_briefing": A concise, high-impact markdown paragraph outlining today's execution context. Focus on their current active week/sprint, task status, streak, and what they need to keep in mind today.
        2. "weekly_summary": A high-level markdown overview of the current week's sprint theme, focus, and total task workload.
        3. "progress_analysis": A markdown assessment of their speed, velocity, execution consistency, streak patterns, and hours logged vs initial estimates. Be analytical yet encouraging.
        4. "risk_assessment": A markdown assessment of potential or active execution failures. Address any overdue tasks (e.g. {overdue_tasks}), energy drain risks, potential delay causes, or friction points related to their biggest obstacle ({biggest_challenge}).
        5. "motivation_message": A highly personalized message tailored to their motivation style ({motivation_style}). Push them to execute today by linking their actions to their core driver.
        6. "recommended_actions": A bulleted markdown list of 3-5 concrete, prioritized next action steps. Be extremely tactical and specific (e.g., specific tasks from their backlog to focus on).
        7. "adaptive_replanning_payload": A structured JSON object for the Adaptive Replanning Agent:
           - "risk_level": "low", "medium", or "high"
           - "velocity_status": "on_track", "behind", or "ahead"
           - "at_risk_tasks": Array of task IDs (e.g., T1_1) that are overdue or delayed
           - "critical_delay_reason": A short string explaining why they are behind (or "None" if on track)
           - "recommended_timeline_adjustment": "none", "extend_1_week", "reduce_daily_load", or "reallocate_hours"
        8. "memory_payload": A structured JSON object for the Memory Agent:
           - "key_learnings": Array of 2-3 key insights about the user's habit/work patterns
           - "user_strengths_noted": Array of strengths observed during this session
           - "sentiment_reflection": A short description of the user's morale or execution sentiment
           - "session_summary": A summary of progress made in this session

        Format your response as a single, valid JSON object. Do not include markdown code block wrappers (like ```json), do not include any explanatory text outside the JSON. Return only the raw JSON.
        """
    )


def get_coaching_chat_prompt(
    profile_data: dict,
    goal_context: dict,
    selected_strategy: dict,
    readiness_results: dict,
    roadmap_dag_data: dict,
    schedule_data: dict,
    progress_metrics: dict,
    weekly_reflections: list,
    chat_history: list
) -> str:
    """
    Constructs the prompt for the conversational coaching agent chat.
    """
    user_type = profile_data.get("user_type", "Learner")
    experience_level = profile_data.get("experience_level", "Beginner")
    hours_per_week = profile_data.get("hours_per_week", 10)
    work_style = profile_data.get("work_style", "Balanced Progress")
    motivation_style = profile_data.get("motivation_style", "Progress")
    biggest_challenge = profile_data.get("biggest_challenge", "Inconsistent")

    goal = goal_context.get("goal", "")
    category = goal_context.get("category", "")
    difficulty = goal_context.get("difficulty", "")

    strategy_name = selected_strategy.get("name", "Balanced Growth")
    strategy_duration = selected_strategy.get("estimated_duration", "")

    health_score = progress_metrics.get("health_score", 100)
    completion_rate = progress_metrics.get("overall_completion_pct", 0)
    streak_count = progress_metrics.get("streak_count", 0)
    overdue_count = progress_metrics.get("overdue_tasks_count", 0)
    completed_tasks = progress_metrics.get("completed_tasks", 0)
    total_tasks = progress_metrics.get("total_tasks", 0)
    overdue_tasks = ", ".join(progress_metrics.get("overdue_tasks_names", [])) or "None"

    # Format history
    history_formatted = ""
    for msg in chat_history[-10:]:
        role = "User" if msg["role"] == "user" else "Coach"
        history_formatted += f"{role}: {msg['content']}\n"

    return textwrap.dedent(
        f"""
        You are the AI Execution Coach for Agent OnboardX. You are having a conversation with the user to help them execute their goals, debug their bottlenecks, and optimize their schedule.

        === USER CONTEXT ===
        - User Profile: {user_type} | {experience_level} level | {hours_per_week} hrs/week availability | {work_style} style | Main challenge: {biggest_challenge}
        - Goal: "{goal}" ({category} • {difficulty} level)
        - Selected Strategy: {strategy_name} (Timeline: {strategy_duration})
        - Telemetry: Health {health_score}/100 | Completed: {completion_rate}% ({completed_tasks}/{total_tasks} tasks done) | Streak: {streak_count} days | Overdue: {overdue_count} tasks ({overdue_tasks})

        === CONVERSATION HISTORY ===
        {history_formatted}

        === COACHING STYLE RULES ===
        1. **Empathetic & Data-Driven**: Always refer to their actual telemetry (streaks, completion rate, overdue tasks) when answering their planning questions.
        2. **Action-Oriented**: Focus responses on what they can do next. Suggest concrete steps.
        3. **Archetype-Aware**: If they are a Beginner, explain things simply. If they are Advanced, dive straight into optimizations. Address their main challenge ({biggest_challenge}) when they are falling behind.
        4. **Tone**: Direct, encouraging, friendly, and expert. Keep responses concise and formatted in clean markdown (paragraphs, bold text, bullet points). Do not make up tasks that do not exist in their backlog, refer only to the actual tasks if needed.

        Answer the user's latest query now.
        """
    )


def get_adaptive_replanning_prompt(
    profile_data: dict,
    goal_context: dict,
    selected_strategy: dict,
    readiness_results: dict,
    roadmap_dag_data: dict,
    schedule_data: dict,
    progress_metrics: dict,
    coach_insights: dict,
    new_hours_per_week: float,
    replanning_mode: str
) -> str:
    """
    Constructs a detailed prompt to invoke the Gemma 4 31B model for adaptive replanning.
    """
    user_type = profile_data.get("user_type", "Learner")
    experience_level = profile_data.get("experience_level", "Beginner")
    original_hours = profile_data.get("hours_per_week", 10)
    work_style = profile_data.get("work_style", "Balanced Progress")
    biggest_challenge = profile_data.get("biggest_challenge", "Inconsistent")

    goal = goal_context.get("goal", "")
    category = goal_context.get("category", "")
    difficulty = goal_context.get("difficulty", "")

    strategy_name = selected_strategy.get("name", "Balanced Growth")
    strategy_duration = selected_strategy.get("estimated_duration", "")

    # Progress Telemetry
    health_score = progress_metrics.get("health_score", 100)
    completion_rate = progress_metrics.get("overall_completion_pct", 0)
    streak_count = progress_metrics.get("streak_count", 0)
    overdue_count = progress_metrics.get("overdue_tasks_count", 0)
    total_hours_spent = progress_metrics.get("total_hours_spent", 0.0)
    completed_tasks_count = progress_metrics.get("completed_tasks", 0)
    total_tasks_count = progress_metrics.get("total_tasks", 0)
    overdue_tasks = ", ".join(progress_metrics.get("overdue_tasks_names", [])) or "None"

    # Coach Insights
    coach_briefing = coach_insights.get("daily_briefing", "") if coach_insights else ""
    coach_risks = coach_insights.get("risk_assessment", "") if coach_insights else ""
    coach_actions = coach_insights.get("recommended_actions", "") if coach_insights else ""

    # Current roadmap and task list details
    phases = roadmap_dag_data.get("phases", [])
    current_schedule_weekly = schedule_data.get("weekly_schedule", [])

    # Format the current tasks status (complete vs incomplete)
    tasks_status_list = []
    for phase in phases:
        p_num = phase.get("phase_number", 1)
        for task in phase.get("tasks", []):
            t_id = task.get("task_id")
            t_name = task.get("name")
            t_hours = task.get("estimated_hours", 2)
            t_deps = ", ".join(task.get("dependencies", [])) or "None"
            
            # Determine complete status
            # Task is complete if all its subtask checkmarks are marked True in session_state.task_completions
            subtasks = task.get("subtasks", [])
            sub_keys = [f"{t_id}_{i}" for i in range(len(subtasks))]
            is_completed = progress_metrics.get("task_statuses", {}).get(t_id) == "Completed"
            
            status_str = "Completed" if is_completed else "Incomplete"
            tasks_status_list.append(
                f"- [{t_id}] {t_name} (Phase {p_num} • {t_hours} hrs • Deps: {t_deps}) - Status: {status_str}"
            )
    tasks_status_formatted = "\n".join(tasks_status_list)

    return textwrap.dedent(
        f"""
        You are the Adaptive Replanning Agent for Agent OnboardX. Your job is to analyze execution telemetry, detect delays or changes in constraints, and compute an optimized schedule update matching the user's selected replanning mode.

        === USER PROFILE & COACHING CONTEXT ===
        - Goal: "{goal}" ({category} • {difficulty} difficulty)
        - User Archetype: {user_type} ({experience_level} level)
        - Original Hours Available: {original_hours} hours/week
        - Modified Hours Available Constraint: {new_hours_per_week} hours/week
        - Work Style Preference: {work_style}
        - Main obstacle/challenge: {biggest_challenge}
        - Strategy Chosen: {strategy_name} (Base timeline: {strategy_duration})

        === CURRENT PROGRESS TELEMETRY ===
        - Goal Completion: {completion_rate}% ({completed_tasks_count}/{total_tasks_count} tasks completed)
        - Active Streak: {streak_count} days
        - Execution Health Score: {health_score}/100
        - Cumulative Hours Logged: {total_hours_spent} hours
        - Overdue Tasks: {overdue_tasks} ({overdue_count} tasks delayed)

        === ACTIVE BACKLOG STATUS ===
        {tasks_status_formatted}

        === AI COACH FINDINGS ===
        - Daily Briefing Summary: {coach_briefing}
        - Risk Assessment Summary: {coach_risks}
        - Recommended Tweak Actions: {coach_actions}

        === REPLANNING CRITERIA & MODE ===
        Selected Replanning Mode: **{replanning_mode}**

        How to restructure the timeline and schedule based on the mode:
        1. **Catch Up**:
           - Keep the final target date identical.
           - Compress the remaining schedule.
           - You may allow weeks to slightly exceed the availability constraint of {new_hours_per_week} hours if necessary.
           - Suggest parallelizing tasks that do not have strict sequential dependencies.
        2. **Balanced**:
           - Standard rescheduling.
           - Distribute all remaining incomplete tasks evenly across subsequent weeks.
           - Strictly respect the availability constraint of {new_hours_per_week} hours per week.
           - Push out target dates proportionally if the remaining work exceeds availability.
        3. **Low Stress**:
           - Focus on execution safety and preventing burnout.
           - Extend the timeline by 20-50% to build in larger weekly buffers.
           - Cap weekly allocations well below {new_hours_per_week} hours (e.g. 70-80% of constraint).
           - Distribute tasks into small daily blocks with rest buffers.
        4. **Aggressive**:
           - Target early completion.
           - Compress the remaining sprint schedule into the minimum possible weeks.
           - Maximize weekly allocations up to {new_hours_per_week} hours.
           - Pull forward milestones and parallelize tasks where possible.

        === TASK ===
        Generate a replanned execution model.
        1. Grade the overall `roadmap_health_score` (0-100) reflecting how safe/delinquent the plan is.
        2. Grade the `completion_probability` (0-100) that the user will achieve this goal on the new timeline given their metrics.
        3. Formulate a detailed weekly sprint plan (`replanned_weekly_schedule`) containing only the remaining **Incomplete** tasks. Note: Completed tasks should NOT be scheduled in the new weeks. Start the schedule at Week 1 for the remaining sprint duration.
        4. Formulate the hourly daily task slots (`replanned_daily_schedule`) for the active workdays of those weeks, respecting the selected mode constraints.
        5. Detail the risk analysis explaining detected bottlenecks and recommended timeline adjustments.
        6. Package a downstream JSON payload (`memory_payload`) containing key learnings, adjustments made, user sentiment, and a summary.

        Format your response as a single, valid JSON object. Do not include markdown code block wrappers (like ```json), do not include any explanatory text outside the JSON. Return only the raw JSON.

        Required JSON structure:
        {{
            "roadmap_health_score": Integer (0 to 100),
            "completion_probability": Integer (0 to 100),
            "goal_completion_forecast": "String - e.g. 'Completed in 3 weeks, adjusted from 2 weeks'",
            "risk_analysis": "String - detailed breakdown of bottlenecks, availability slips, and plan risks",
            "recommended_adjustments": [
                "Action adjustment 1",
                "Action adjustment 2"
            ],
            "replanned_weekly_schedule": [
                {{
                    "week_number": Integer,
                    "focus": "String sprint theme",
                    "allocated_hours": Float,
                    "tasks": [
                        {{
                            "task_id": "String",
                            "name": "String",
                            "allocated_hours": Float
                        }}
                    ]
                }}
            ],
            "replanned_daily_schedule": [
                {{
                    "week_number": Integer,
                    "day_number": Integer,
                    "day_name": "String",
                    "total_hours": Float,
                    "time_blocks": [
                        {{
                            "task_id": "String",
                            "name": "String",
                            "time_slot": "String - e.g. 09:00 AM - 11:00 AM",
                            "duration_hours": Float,
                            "type": "String"
                        }}
                    ]
                }}
            ],
            "memory_payload": {{
                "key_learnings": ["String insights about user's consistency/timeline slips"],
                "user_strengths_noted": ["String strengths"],
                "adjustments_made": "String summary of adjustments made",
                "sentiment_reflection": "String - user confidence/burnout morale metrics",
                "session_summary": "String summary of this replanning event"
            }}
        }}
        """
    )







