import os
import json
import streamlit as st
import google.generativeai as genai
from services.gemini_service import get_api_key, extract_json_from_text
from utils.prompts import get_adaptive_replanning_prompt

def generate_replanning_analysis(
    profile_data: dict,
    goal_context: dict,
    selected_strategy: dict,
    readiness_results: dict,
    roadmap_dag_data: dict,
    schedule_data: dict,
    progress_metrics: dict,
    coach_insights: dict,
    new_hours_per_week: float,
    replanning_mode: str,
    api_key: str
) -> dict:
    """
    Calls the Gemini API using the Gemma 4 31B model to calculate a new schedule.
    Saves and returns the structured JSON output.
    """
    if not api_key:
        raise ValueError("Gemini API Key is missing. Please configure it in the sidebar.")
        
    genai.configure(api_key=api_key)
    prompt = get_adaptive_replanning_prompt(
        profile_data,
        goal_context,
        selected_strategy,
        readiness_results,
        roadmap_dag_data,
        schedule_data,
        progress_metrics,
        coach_insights,
        new_hours_per_week,
        replanning_mode
    )
    
    try:
        model = genai.GenerativeModel("models/gemma-4-31b-it")
        response = model.generate_content(
            prompt,
            generation_config={"response_mime_type": "application/json"}
        )
        result = extract_json_from_text(response.text)
        return result
    except Exception as e:
        raise Exception(f"Replanning Analysis Generation Failed: {str(e)}")
