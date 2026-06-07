import streamlit as st

def get_risk_label(health_score: float) -> str:
    if health_score < 50:
        return "High"
    elif health_score < 75:
        return "Medium"
    else:
        return "Low"

def render_schedule_impact_analysis(
    old_weekly: list,
    new_weekly: list,
    old_capacity: float,
    new_capacity: float,
    old_probability: int,
    new_probability: int,
    old_health: float,
    new_health: float
):
    """
    Renders a premium visual card summarizing the schedule impact indicators.
    """
    st.markdown("<h4 style='color: #cbd5e1; font-weight: 700; margin-top: 15px; margin-bottom: 15px;'>⚖️ Schedule Impact Analysis</h4>", unsafe_allow_html=True)
    
    # Calculate Week shift
    old_weeks = len(old_weekly or [])
    new_weeks = len(new_weekly or [])
    delta_weeks = new_weeks - old_weeks
    
    if delta_weeks > 0:
        weeks_impact = f"Timeline extended by {delta_weeks} week{'s' if delta_weeks > 1 else ''}"
    elif delta_weeks < 0:
        weeks_impact = f"Timeline compressed by {abs(delta_weeks)} week{'s' if abs(delta_weeks) > 1 else ''}"
    else:
        weeks_impact = "Timeline duration maintained (on track)"
        
    # Capacity impact
    capacity_impact = f"Weekly capacity limit adjusted from {old_capacity}h to {new_capacity}h"
    
    # Risk shift
    old_risk = get_risk_label(old_health)
    new_risk = get_risk_label(new_health)
    if old_risk != new_risk:
        risk_impact = f"Risk level adjusted from {old_risk} to {new_risk}"
    else:
        risk_impact = f"Risk level maintained as {new_risk}"
        
    # Probability shift
    prob_impact = f"Completion probability changed from {old_probability}% to {new_probability}%"
    
    # Renders checkmarks with CSS styling
    st.html(
        f"""
        <style>
        .impact-container {{
            background: linear-gradient(135deg, rgba(16, 185, 129, 0.04) 0%, rgba(99, 102, 241, 0.04) 100%);
            border: 1px solid rgba(16, 185, 129, 0.15);
            border-radius: 12px;
            padding: 20px;
            margin-bottom: 25px;
        }}
        .impact-item {{
            display: flex;
            align-items: center;
            gap: 10px;
            font-size: 0.95rem;
            color: #cbd5e1;
            margin-bottom: 12px;
        }}
        .impact-item:last-child {{
            margin-bottom: 0;
        }}
        .impact-check {{
            color: #10b981;
            font-weight: 800;
            font-size: 1.15rem;
        }}
        </style>
        <div class='impact-container'>
            <div class='impact-item'>
                <span class='impact-check'>✓</span>
                <span>{weeks_impact}</span>
            </div>
            <div class='impact-item'>
                <span class='impact-check'>✓</span>
                <span>{capacity_impact}</span>
            </div>
            <div class='impact-item'>
                <span class='impact-check'>✓</span>
                <span>{risk_impact}</span>
            </div>
            <div class='impact-item'>
                <span class='impact-check'>✓</span>
                <span>{prob_impact}</span>
            </div>
        </div>
        """
    )
