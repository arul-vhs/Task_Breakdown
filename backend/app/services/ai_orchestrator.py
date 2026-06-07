import os
import json
import google.generativeai as genai
from jose import JWTError
from app.config import settings
from app.utils.prompts import (
    get_goal_analysis_prompt,
    get_strategy_generation_prompt,
    get_strategy_validation_questions_prompt,
    get_strategy_readiness_evaluation_prompt,
    get_execution_blueprint_prompt,
    get_task_breakdown_prompt,
    get_weekly_reflection_prompt,
    get_coaching_briefing_prompt,
    get_coaching_chat_prompt,
    get_adaptive_replanning_prompt
)

class AIOrchestrator:
    def __init__(self):
        # Resolve Gemini key from settings
        api_key = settings.GEMINI_API_KEY
        if api_key:
            genai.configure(api_key=api_key)
        self.model_name = settings.GEMINI_MODEL if settings.GEMINI_MODEL else "models/gemma-4-31b-it"

    def _get_model(self) -> genai.GenerativeModel:
        return genai.GenerativeModel(self.model_name)

    def _extract_json(self, text: str) -> dict:
        """
        Robustly extracts and parses a JSON object from raw LLM text responses.
        """
        clean_text = text.strip()
        try:
            return json.loads(clean_text)
        except json.JSONDecodeError:
            pass
            
        if "```json" in clean_text:
            try:
                parts = clean_text.split("```json")
                json_str = parts[1].split("```")[0].strip()
                return json.loads(json_str)
            except Exception:
                pass
                
        if "```" in clean_text:
            try:
                parts = clean_text.split("```")
                json_str = parts[1].strip()
                if json_str.startswith("json"):
                    json_str = json_str[4:].strip()
                return json.loads(json_str)
            except Exception:
                pass

        start_idx = clean_text.find("{")
        end_idx = clean_text.rfind("}")
        if start_idx != -1 and end_idx != -1 and end_idx > start_idx:
            json_str = clean_text[start_idx:end_idx + 1]
            try:
                return json.loads(json_str)
            except json.JSONDecodeError as je:
                raise ValueError(f"Extracted JSON block but failed to parse: {str(je)}")
                
        raise ValueError(f"No parseable JSON structure found in response.\nRaw: {text}")

    def analyze_goal(self, goal_title: str, profile: dict) -> dict:
        prompt = get_goal_analysis_prompt(goal_title, profile)
        model = self._get_model()
        response = model.generate_content(
            prompt,
            generation_config={"response_mime_type": "application/json"}
        )
        return self._extract_json(response.text)

    def generate_strategies(self, goal_context: dict, profile: dict) -> dict:
        prompt = get_strategy_generation_prompt(goal_context, profile, profile)
        model = self._get_model()
        response = model.generate_content(
            prompt,
            generation_config={"response_mime_type": "application/json"}
        )
        return self._extract_json(response.text)

    def generate_validation_questions(self, profile: dict, goal_context: dict, selected_strategy: dict) -> dict:
        prompt = get_strategy_validation_questions_prompt(profile, goal_context, selected_strategy)
        model = self._get_model()
        response = model.generate_content(
            prompt,
            generation_config={"response_mime_type": "application/json"}
        )
        return self._extract_json(response.text)

    def evaluate_readiness(self, profile: dict, goal_context: dict, selected_strategy: dict, qa_list: list) -> dict:
        prompt = get_strategy_readiness_evaluation_prompt(profile, goal_context, selected_strategy, qa_list)
        model = self._get_model()
        response = model.generate_content(
            prompt,
            generation_config={"response_mime_type": "application/json"}
        )
        return self._extract_json(response.text)

    def generate_blueprint(self, profile: dict, goal_context: dict, selected_strategy: dict, readiness_results: dict, refinement_choice: str) -> dict:
        prompt = get_execution_blueprint_prompt(profile, goal_context, selected_strategy, readiness_results, refinement_choice)
        model = self._get_model()
        response = model.generate_content(
            prompt,
            generation_config={"response_mime_type": "application/json"}
        )
        return self._extract_json(response.text)

    def generate_task_breakdown(self, profile: dict, goal_context: dict, selected_strategy: dict, readiness_results: dict, blueprint: dict, depth: str) -> dict:
        prompt = get_task_breakdown_prompt(profile, goal_context, selected_strategy, readiness_results, blueprint, depth)
        model = self._get_model()
        response = model.generate_content(
            prompt,
            generation_config={"response_mime_type": "application/json"}
        )
        return self._extract_json(response.text)

    def generate_weekly_reflection(self, profile: dict, goal_context: dict, progress_summary: dict) -> dict:
        prompt = get_weekly_reflection_prompt(profile, goal_context, progress_summary)
        model = self._get_model()
        response = model.generate_content(
            prompt,
            generation_config={"response_mime_type": "application/json"}
        )
        return self._extract_json(response.text)

    def generate_coaching_insights(self, profile: dict, goal_context: dict, selected_strategy: dict, readiness_results: dict, roadmap_dag_data: dict, schedule_data: dict, progress_metrics: dict, weekly_reflections: list) -> dict:
        prompt = get_coaching_briefing_prompt(profile, goal_context, selected_strategy, readiness_results, roadmap_dag_data, schedule_data, progress_metrics, weekly_reflections)
        model = self._get_model()
        response = model.generate_content(
            prompt,
            generation_config={"response_mime_type": "application/json"}
        )
        return self._extract_json(response.text)

    def chat_with_coach(self, profile: dict, goal_context: dict, selected_strategy: dict, readiness_results: dict, roadmap_dag_data: dict, schedule_data: dict, progress_metrics: dict, weekly_reflections: list, chat_history: list) -> str:
        prompt = get_coaching_chat_prompt(profile, goal_context, selected_strategy, readiness_results, roadmap_dag_data, schedule_data, progress_metrics, weekly_reflections, chat_history)
        model = self._get_model()
        response = model.generate_content(prompt)
        return response.text

    def generate_replanned_preview(self, profile: dict, goal_context: dict, selected_strategy: dict, readiness_results: dict, roadmap_dag_data: dict, schedule_data: dict, progress_metrics: dict, coach_insights: dict, new_hours_per_week: float, replanning_mode: str) -> dict:
        prompt = get_adaptive_replanning_prompt(profile, goal_context, selected_strategy, readiness_results, roadmap_dag_data, schedule_data, progress_metrics, coach_insights, new_hours_per_week, replanning_mode)
        model = self._get_model()
        response = model.generate_content(
            prompt,
            generation_config={"response_mime_type": "application/json"}
        )
        return self._extract_json(response.text)

ai_orchestrator = AIOrchestrator()
