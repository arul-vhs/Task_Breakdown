def generate_persona(profile_data: dict) -> dict:
    """
    Generates an AI Execution Persona based on rule-based logic
    using experience level, available hours, and other profile indicators.
    
    Parameters:
    - profile_data (dict): Dictionary containing keys:
        - 'experience_level': 'Beginner', 'Intermediate', 'Advanced'
        - 'hours_per_week': int (1-40)
        - 'user_type': 'Student', 'Professional', etc.
        - 'work_style': 'Quick Wins', 'Balanced Progress', 'Deep Focus'
        - 'motivation_style': 'Achievements', 'Progress', etc.
        - 'biggest_challenge': 'Lack of Time', 'Overwhelmed', etc.
        
    Returns:
    - dict: Generated persona details:
        - 'name': str
        - 'strength': str
        - 'challenge': str
        - 'strategy': str
    """
    experience = profile_data.get("experience_level", "Beginner")
    hours = profile_data.get("hours_per_week", 10)
    
    # 9-Quadrant Mapping based on Experience and Dedicated Hours
    if experience == "Beginner":
        if hours < 10:
            return {
                "name": "Consistent Explorer",
                "strength": "High curiosity, adaptability, and openness to learning.",
                "challenge": "Maintaining long-term habit consistency under constrained timelines.",
                "strategy": "Micro-habits planning (15-minute daily sessions, low-friction tracking, and clear checklists)."
            }
        elif hours < 20:
            return {
                "name": "Habit Builder",
                "strength": "Strong willingness to commit time and build structured skills.",
                "challenge": "Taking on too many goals at once, leading to scattered focus.",
                "strategy": "Agile task boarding (visualizing a Kanban board with max 3 tasks active per day)."
            }
        else:
            return {
                "name": "Ambitious Starter",
                "strength": "Immense energy, high enthusiasm, and ample available execution time.",
                "challenge": "Rapid burnout due to lack of structured pathing and clear milestones.",
                "strategy": "Structured milestone roadmaps (weekly checkpoints, guided learnings, and rest rules)."
            }
            
    elif experience == "Intermediate":
        if hours < 10:
            return {
                "name": "Strategic Optimizer",
                "strength": "Capable execution skills paired with efficient task navigation.",
                "challenge": "High context-switching costs and extremely restricted time pockets.",
                "strategy": "High-impact prioritization (80/20 rule: pick exactly one high-value win per week)."
            }
        elif hours < 20:
            return {
                "name": "Focused Builder",
                "strength": "Good execution discipline, solid core skills, and steady work output.",
                "challenge": "Over-planning features or getting stuck in validation/looping.",
                "strategy": "Time-blocked planning (2-hour deep work focus blocks with distraction-blocking apps)."
            }
        else:
            return {
                "name": "Sustained Producer",
                "strength": "Highly consistent output, robust skillset, and large capacity.",
                "challenge": "Allocating effort to low-leverage tasks because of high availability.",
                "strategy": "Weekly sprint planning (strict definition of done, weekly review and retro sessions)."
            }
            
    else:  # Advanced
        if hours < 10:
            return {
                "name": "Precision Architect",
                "strength": "Expert-level strategic clarity and process optimization capability.",
                "challenge": "Struggling to make momentum on large-scale projects in short sessions.",
                "strategy": "Leveraged execution (focusing solely on high-leverage decisions, automation, or delegation)."
            }
        elif hours < 20:
            return {
                "name": "Systems Designer",
                "strength": "Advanced workflow creation and systems-level thinking.",
                "challenge": "Perfectionism and over-engineering solutions before releasing them.",
                "strategy": "MVP-first approach (set strict limits for Minimum Viable Progress, release early and iterate)."
            }
        else:
            return {
                "name": "Execution Strategist",
                "strength": "Exceptional drive, high output capacity, and deep strategic vision.",
                "challenge": "Prone to severe stress, overwork, and absolute resistance to delegation.",
                "strategy": "OKRs & mandatory rest buffers (set top-level objectives, enforce 15% downtime buffer weekly)."
            }
