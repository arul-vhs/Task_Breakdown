import os
import json
import streamlit as st

CACHE_FILE = ".state_cache.json"

PERSISTENT_KEYS = [
    "app_phase",
    "onboarding_started",
    "current_step",
    "profile_data",
    "completed",
    "goal_submitted",
    "goal_analysis",
    "goal_questions",
    "goal_answers",
    "goal_q_step",
    "goal_context",
    "custom_api_key",
    "selected_strategy_data",
    "selected_strategy_index",
    "strategy_validation",
    "roadmap_dag_data",
    "blueprint_refinement",
    "task_depth",
    "task_completions",
    "task_due_dates",
    "task_time_spent",
    "streak_count",
    "last_activity_date",
    "weekly_reflections"
]

def load_state_from_cache():
    """
    Loads session state from the local JSON cache file if it exists,
    but only if we haven't already initialized state in the current session.
    """
    if "state_loaded" not in st.session_state:
        st.session_state.state_loaded = True
        if os.path.exists(CACHE_FILE):
            try:
                with open(CACHE_FILE, "r") as f:
                    cached_data = json.load(f)
                for key in PERSISTENT_KEYS:
                    if key in cached_data:
                        st.session_state[key] = cached_data[key]
            except Exception:
                pass

def save_state_to_cache():
    """
    Saves the current session state values to the local JSON cache file.
    """
    cache_data = {}
    for key in PERSISTENT_KEYS:
        if key in st.session_state:
            cache_data[key] = st.session_state[key]
    
    if cache_data:
        try:
            with open(CACHE_FILE, "w") as f:
                json.dump(cache_data, f, indent=4)
        except Exception:
            pass

def clear_state_cache():
    """
    Clears the local JSON cache file and resets the relevant session state.
    """
    if os.path.exists(CACHE_FILE):
        try:
            os.remove(CACHE_FILE)
        except Exception:
            pass
            
    for key in PERSISTENT_KEYS:
        if key in st.session_state:
            del st.session_state[key]
            
    if "state_loaded" in st.session_state:
        del st.session_state["state_loaded"]
