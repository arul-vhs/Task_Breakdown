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
