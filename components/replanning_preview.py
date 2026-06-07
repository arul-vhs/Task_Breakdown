import streamlit as st

def render_schedule_comparison(old_weekly: list, new_weekly: list):
    """
    Renders a side-by-side comparison of the Old Schedule vs the New Schedule.
    """
    st.markdown("<h4 style='color: #cbd5e1; font-weight: 700; margin-top: 15px; margin-bottom: 15px;'>📅 Weekly Schedule Comparison (Old vs. New)</h4>", unsafe_allow_html=True)
    
    # Clean fallback checks
    old_list = old_weekly or []
    new_list = new_weekly or []
    
    if not old_list and not new_list:
        st.info("No schedules available for comparison.")
        return

    max_weeks = max(len(old_list), len(new_list))
    
    # Styled CSS for comparison blocks
    st.html(
        """
        <style>
        .compare-week-header {
            font-size: 1.1rem;
            font-weight: 700;
            color: #fbbf24;
            margin-bottom: 12px;
            border-bottom: 1px solid rgba(255, 255, 255, 0.08);
            padding-bottom: 6px;
            margin-top: 15px;
        }
        .compare-box {
            background: rgba(30, 41, 59, 0.25);
            border: 1px solid rgba(255, 255, 255, 0.05);
            border-radius: 12px;
            padding: 18px;
            height: 100%;
            min-height: 140px;
        }
        .compare-box-title {
            font-size: 0.85rem;
            font-weight: 700;
            color: #94a3b8;
            margin-bottom: 8px;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }
        .compare-task-item {
            font-size: 0.88rem;
            color: #cbd5e1;
            padding: 6px 0;
            border-bottom: 1px solid rgba(255, 255, 255, 0.03);
        }
        .compare-task-item:last-child {
            border-bottom: none;
        }
        </style>
        """
    )
    
    for i in range(max_weeks):
        week_num = i + 1
        
        # Get week data from old schedule
        old_week = next((w for w in old_list if w.get("week_number") == week_num), None)
        # Get week data from new schedule
        new_week = next((w for w in new_list if w.get("week_number") == week_num), None)
        
        # Determine focus themes
        old_focus = old_week.get("focus", "Active theme") if old_week else "N/A"
        new_focus = new_week.get("focus", "Active theme") if new_week else "N/A"
        
        st.markdown(f"<div class='compare-week-header'>Sprint Week {week_num}</div>", unsafe_allow_html=True)
        col1, col2 = st.columns(2)
        
        with col1:
            if old_week:
                tasks = old_week.get("tasks", [])
                allocated = old_week.get("allocated_hours", 0.0)
                tasks_html = ""
                for t in tasks:
                    tasks_html += f"<div class='compare-task-item'>🔹 [{t.get('task_id')}] {t.get('name')} <span style='color: #818cf8; font-weight: 600;'>({t.get('allocated_hours')}h)</span></div>"
                if not tasks:
                    tasks_html = "<div style='color: #64748b; font-style: italic; font-size: 0.85rem;'>No tasks scheduled.</div>"
                
                st.html(
                    f"""
                    <div class='compare-box' style='border-left: 4px solid #64748b;'>
                        <div class='compare-box-title'>Old Schedule (Focus: {old_focus})</div>
                        <div style='font-size: 0.78rem; color: #a855f7; font-weight: bold; margin-bottom: 8px;'>Capacity: {allocated} hrs</div>
                        {tasks_html}
                    </div>
                    """
                )
            else:
                st.html(
                    """
                    <div class='compare-box' style='border-left: 4px solid #64748b; opacity: 0.5;'>
                        <div class='compare-box-title'>Old Schedule</div>
                        <div style='color: #64748b; font-style: italic; font-size: 0.85rem; padding: 10px 0;'>No tasks scheduled.</div>
                    </div>
                    """
                )
                
        with col2:
            if new_week:
                tasks = new_week.get("tasks", [])
                allocated = new_week.get("allocated_hours", 0.0)
                tasks_html = ""
                for t in tasks:
                    tasks_html += f"<div class='compare-task-item'>🔸 [{t.get('task_id')}] {t.get('name')} <span style='color: #34d399; font-weight: 600;'>({t.get('allocated_hours')}h)</span></div>"
                if not tasks:
                    tasks_html = "<div style='color: #64748b; font-style: italic; font-size: 0.85rem;'>No tasks scheduled.</div>"
                
                st.html(
                    f"""
                    <div class='compare-box' style='border-left: 4px solid #10b981; background: rgba(16, 185, 129, 0.03);'>
                        <div class='compare-box-title' style='color: #34d399;'>New Schedule Preview (Focus: {new_focus})</div>
                        <div style='font-size: 0.78rem; color: #34d399; font-weight: bold; margin-bottom: 8px;'>Capacity: {allocated} hrs</div>
                        {tasks_html}
                    </div>
                    """
                )
            else:
                st.html(
                    """
                    <div class='compare-box' style='border-left: 4px solid #ef4444; opacity: 0.5;'>
                        <div class='compare-box-title'>New Schedule Preview</div>
                        <div style='color: #64748b; font-style: italic; font-size: 0.85rem; padding: 10px 0;'>No tasks scheduled.</div>
                    </div>
                    """
                )
        st.markdown("<div style='height: 10px;'></div>", unsafe_allow_html=True)
