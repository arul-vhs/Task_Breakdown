import os
import json
import streamlit as st
import google.generativeai as genai
from dotenv import load_dotenv
from utils.prompts import (
    get_goal_analysis_prompt,
    get_strategy_generation_prompt,
    get_strategy_validation_questions_prompt,
    get_strategy_readiness_evaluation_prompt,
    get_execution_blueprint_prompt,
    get_task_breakdown_prompt,
    get_roadmap_dag_prompt,
    get_scheduling_prompt,
    get_weekly_reflection_prompt
)

# Load environment variables on startup
load_dotenv()

def get_api_key(custom_key: str = None) -> str:
    """
    Resolves the Gemini API key from custom input, Streamlit secrets, or .env.
    """
    if custom_key:
        return custom_key
    
    # Try .env / OS environment
    api_key = os.getenv("GEMINI_API_KEY")
    if api_key:
        return api_key
        
    # Try Streamlit Secrets
    try:
        if "GEMINI_API_KEY" in st.secrets:
            return st.secrets["GEMINI_API_KEY"]
    except Exception:
        pass
        
    return ""

def extract_json_from_text(text: str) -> dict:
    """
    Robustly extracts and parses a JSON object from a text string that may contain
    additional conversational prefaces or markdown code block markers.
    """
    clean_text = text.strip()
    
    # 1. Try to load directly (best case scenario)
    try:
        return json.loads(clean_text)
    except json.JSONDecodeError:
        pass
        
    # 2. Try to extract content inside ```json ... ``` code blocks
    if "```json" in clean_text:
        try:
            parts = clean_text.split("```json")
            json_str = parts[1].split("```")[0].strip()
            return json.loads(json_str)
        except Exception:
            pass
            
    # 3. Try to extract content inside general ``` ... ``` code blocks
    if "```" in clean_text:
        try:
            parts = clean_text.split("```")
            json_str = parts[1].strip()
            if json_str.startswith("json"):
                json_str = json_str[4:].strip()
            return json.loads(json_str)
        except Exception:
            pass

    # 4. Fallback: Search for the first '{' and the last '}'
    start_idx = clean_text.find("{")
    end_idx = clean_text.rfind("}")
    
    if start_idx != -1 and end_idx != -1 and end_idx > start_idx:
        json_str = clean_text[start_idx:end_idx + 1]
        try:
            return json.loads(json_str)
        except json.JSONDecodeError as je:
            raise ValueError(f"Extracted a JSON-like block but failed to parse: {str(je)}\nBlock: {json_str}")
            
    raise ValueError(f"No parseable JSON structure starting with '{{' and ending with '}}' found in response.\nRaw response: {text}")

def analyze_goal_with_gemini(goal_text: str, persona: dict, api_key: str) -> dict:
    """
    Calls the Gemini API using the provided key to analyze the goal and generate
    5 dynamic context-gathering questions. Enforces JSON output using generation_config.
    
    Parameters:
    - goal_text (str): Goal text.
    - persona (dict): Persona profile.
    - api_key (str): Resolved API Key.
    
    Returns:
    - dict: Parsed analysis results.
    """
    if not api_key:
        raise ValueError("Gemini API Key is missing. Please provide a key in your .env or sidebar.")
        
    # Configure generative AI library
    genai.configure(api_key=api_key)
    
    # Build prompt
    prompt = get_goal_analysis_prompt(goal_text, persona)
    
    try:
        # Load gemma-4-31b-it as requested
        model = genai.GenerativeModel("models/gemma-4-31b-it")
        
        # Enforce JSON output mode in Gemini API
        response = model.generate_content(
            prompt,
            generation_config={"response_mime_type": "application/json"}
        )
        
        # Parse the JSON response robustly
        result = extract_json_from_text(response.text)
        return result
        
    except Exception as e:
        raise Exception(f"Goal Analysis Failed: {str(e)}")


def generate_strategies_with_gemini(goal_context: dict, profile_data: dict, persona: dict, api_key: str) -> dict:
    """
    Calls the Gemini API to generate exactly 3 execution strategies and a personalized recommendation.
    Enforces JSON output.
    
    Parameters:
    - goal_context (dict): Compiled goal context.
    - profile_data (dict): User's profile choices.
    - persona (dict): User's execution archetype details.
    - api_key (str): Resolved API Key.
    
    Returns:
    - dict: Parsed strategy generation results containing 'strategies', 'recommended_strategy_key', and 'recommendation_explanation'.
    """
    if not api_key:
        raise ValueError("Gemini API Key is missing. Please provide a key in your .env or sidebar.")
        
    # Configure generative AI library
    genai.configure(api_key=api_key)
    
    # Build prompt
    prompt = get_strategy_generation_prompt(goal_context, profile_data, persona)
    
    try:
        # Load gemma-4-31b-it as requested
        model = genai.GenerativeModel("models/gemma-4-31b-it")
        
        # Enforce JSON output mode in Gemini API
        response = model.generate_content(
            prompt,
            generation_config={"response_mime_type": "application/json"}
        )
        
        # Parse the JSON response robustly
        result = extract_json_from_text(response.text)
        return result
        
    except Exception as e:
        try:
            # Fallback to gemini-1.5-flash
            model = genai.GenerativeModel("gemini-1.5-flash")
            response = model.generate_content(
                prompt,
                generation_config={"response_mime_type": "application/json"}
            )
            result = extract_json_from_text(response.text)
            return result
        except Exception as fallback_e:
            raise Exception(f"Strategy Generation Failed. Primary (gemma-4-31b-it) error: {str(e)}. Fallback (gemini-1.5-flash) error: {str(fallback_e)}")


def generate_validation_questions_with_gemini(profile_data: dict, goal_context: dict, strategy: dict, api_key: str) -> dict:
    """
    Calls Gemini to perform a gap analysis and generate 3 dynamic validation questions.
    """
    if not api_key:
        raise ValueError("Gemini API Key is missing. Please provide a key.")
        
    genai.configure(api_key=api_key)
    prompt = get_strategy_validation_questions_prompt(profile_data, goal_context, strategy)
    
    try:
        model = genai.GenerativeModel("models/gemma-4-31b-it")
        response = model.generate_content(
            prompt,
            generation_config={"response_mime_type": "application/json"}
        )
        result = extract_json_from_text(response.text)
        return result
    except Exception as e:
        try:
            model = genai.GenerativeModel("gemini-1.5-flash")
            response = model.generate_content(
                prompt,
                generation_config={"response_mime_type": "application/json"}
            )
            result = extract_json_from_text(response.text)
            return result
        except Exception as fallback_e:
            raise Exception(f"Validation Questions Generation Failed. Primary error: {str(e)}. Fallback error: {str(fallback_e)}")


def evaluate_strategy_readiness_with_gemini(profile_data: dict, goal_context: dict, strategy: dict, qa_list: list, api_key: str) -> dict:
    """
    Calls Gemini to grade user answers to validation questions and returns readiness scores and lists of feedback.
    """
    if not api_key:
        raise ValueError("Gemini API Key is missing. Please provide a key.")
        
    genai.configure(api_key=api_key)
    prompt = get_strategy_readiness_evaluation_prompt(profile_data, goal_context, strategy, qa_list)
    
    try:
        model = genai.GenerativeModel("models/gemma-4-31b-it")
        response = model.generate_content(
            prompt,
            generation_config={"response_mime_type": "application/json"}
        )
        result = extract_json_from_text(response.text)
        return result
    except Exception as e:
        try:
            model = genai.GenerativeModel("gemini-1.5-flash")
            response = model.generate_content(
                prompt,
                generation_config={"response_mime_type": "application/json"}
            )
            result = extract_json_from_text(response.text)
            return result
        except Exception as fallback_e:
            raise Exception(f"Readiness Evaluation Failed. Primary error: {str(e)}. Fallback error: {str(fallback_e)}")


def generate_execution_blueprint_with_gemini(profile_data: dict, goal_context: dict, strategy: dict, validation_results: dict, refinement_choice: str, api_key: str) -> dict:
    """
    Calls Gemini to generate a personalized step-by-step 3-7 phase execution roadmap.
    """
    if not api_key:
        raise ValueError("Gemini API Key is missing. Please provide a key.")
        
    genai.configure(api_key=api_key)
    prompt = get_execution_blueprint_prompt(profile_data, goal_context, strategy, validation_results, refinement_choice)
    
    try:
        model = genai.GenerativeModel("models/gemma-4-31b-it")
        response = model.generate_content(
            prompt,
            generation_config={"response_mime_type": "application/json"}
        )
        result = extract_json_from_text(response.text)
        return result
    except Exception as e:
        try:
            model = genai.GenerativeModel("gemini-1.5-flash")
            response = model.generate_content(
                prompt,
                generation_config={"response_mime_type": "application/json"}
            )
            result = extract_json_from_text(response.text)
            return result
        except Exception as fallback_e:
            raise Exception(f"Execution Blueprint Generation Failed. Primary error: {str(e)}. Fallback error: {str(fallback_e)}")


def generate_task_breakdown_with_gemini(profile_data: dict, goal_context: dict, strategy: dict, validation_results: dict, blueprint: dict, depth: str, api_key: str) -> dict:
    """
    Calls Gemini to generate a personalized actionable checklist breakdown of tasks/subtasks.
    """
    if not api_key:
        raise ValueError("Gemini API Key is missing. Please provide a key.")
        
    genai.configure(api_key=api_key)
    prompt = get_task_breakdown_prompt(profile_data, goal_context, strategy, validation_results, blueprint, depth)
    
    try:
        model = genai.GenerativeModel("models/gemma-4-31b-it")
        response = model.generate_content(
            prompt,
            generation_config={"response_mime_type": "application/json"}
        )
        result = extract_json_from_text(response.text)
        return result
    except Exception as e:
        try:
            model = genai.GenerativeModel("gemini-1.5-flash")
            response = model.generate_content(
                prompt,
                generation_config={"response_mime_type": "application/json"}
            )
            result = extract_json_from_text(response.text)
            return result
        except Exception as fallback_e:
            raise Exception(f"Task Breakdown Generation Failed. Primary error: {str(e)}. Fallback error: {str(fallback_e)}")


def generate_roadmap_dag_with_gemini(profile_data: dict, goal_context: dict, strategy: dict, validation_results: dict, refinement_choice: str, depth: str, api_key: str) -> dict:
    """
    Calls Gemini to generate a unified execution roadmap containing phases, tasks, subtasks, dependencies, and estimations.
    """
    if not api_key:
        raise ValueError("Gemini API Key is missing. Please provide a key.")
        
    genai.configure(api_key=api_key)
    prompt = get_roadmap_dag_prompt(profile_data, goal_context, strategy, validation_results, refinement_choice, depth)
    
    try:
        model = genai.GenerativeModel("models/gemma-4-31b-it")
        response = model.generate_content(
            prompt,
            generation_config={"response_mime_type": "application/json"}
        )
        result = extract_json_from_text(response.text)
        return result
    except Exception as e:
        try:
            model = genai.GenerativeModel("gemini-1.5-flash")
            response = model.generate_content(
                prompt,
                generation_config={"response_mime_type": "application/json"}
            )
            result = extract_json_from_text(response.text)
            return result
        except Exception as fallback_e:
            raise Exception(f"Roadmap & DAG Generation Failed. Primary error: {str(e)}. Fallback error: {str(fallback_e)}")


def generate_schedule_with_gemini(profile_data: dict, goal_context: dict, selected_strategy: dict, roadmap_dag_data: dict, api_key: str) -> dict:
    """
    Calls Gemini to generate a weekly and daily schedule.
    """
    if not api_key:
        raise ValueError("Gemini API Key is missing. Please provide a key.")
        
    genai.configure(api_key=api_key)
    prompt = get_scheduling_prompt(profile_data, goal_context, selected_strategy, roadmap_dag_data)
    
    try:
        model = genai.GenerativeModel("models/gemma-4-31b-it")
        response = model.generate_content(
            prompt,
            generation_config={"response_mime_type": "application/json"}
        )
        result = extract_json_from_text(response.text)
        return result
    except Exception as e:
        try:
            model = genai.GenerativeModel("gemini-1.5-flash")
            response = model.generate_content(
                prompt,
                generation_config={"response_mime_type": "application/json"}
            )
            result = extract_json_from_text(response.text)
            return result
        except Exception as fallback_e:
            raise Exception(f"Scheduling Generation Failed. Primary error: {str(e)}. Fallback error: {str(fallback_e)}")


def generate_weekly_reflection_with_gemini(profile_data: dict, goal_context: dict, progress_summary: dict, api_key: str) -> dict:
    """
    Calls Gemini to generate a weekly coaching reflection based on execution progress.
    """
    if not api_key:
        raise ValueError("Gemini API Key is missing. Please provide a key.")
        
    genai.configure(api_key=api_key)
    prompt = get_weekly_reflection_prompt(profile_data, goal_context, progress_summary)
    
    try:
        model = genai.GenerativeModel("models/gemma-4-31b-it")
        response = model.generate_content(
            prompt,
            generation_config={"response_mime_type": "application/json"}
        )
        result = extract_json_from_text(response.text)
        return result
    except Exception as e:
        try:
            model = genai.GenerativeModel("gemini-1.5-flash")
            response = model.generate_content(
                prompt,
                generation_config={"response_mime_type": "application/json"}
            )
            result = extract_json_from_text(response.text)
            return result
        except Exception as fallback_e:
            raise Exception(f"Weekly Reflection Generation Failed. Primary error: {str(e)}. Fallback error: {str(fallback_e)}")
