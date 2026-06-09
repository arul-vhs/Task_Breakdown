import google.generativeai as genai
import json
import logging
from typing import Optional
from app.providers.base_provider import BaseProvider
from app.core.config import settings

logger = logging.getLogger("app.providers.gemini_provider")

class GeminiProvider(BaseProvider):
    def __init__(self, api_key: Optional[str] = None, model_name: Optional[str] = None):
        key = api_key or settings.GEMINI_API_KEY
        if not key:
            raise ValueError("GEMINI_API_KEY is not set or is empty.")
        genai.configure(api_key=key)
        
        self.model_name = model_name or settings.GEMINI_MODEL or "models/gemma-4-31b-it"
        if not self.model_name:
            raise ValueError("GEMINI_MODEL is not set or is empty.")
            
        try:
            # Validate model name using get_model
            genai.get_model(self.model_name)
        except Exception as e:
            raise ValueError(f"Invalid Gemini model '{self.model_name}': {e}")
            
        print(f"[GeminiProvider] Selected model: {self.model_name}")
        print(f"[GeminiProvider] API key loaded: {bool(key)}")

    def _clean_json(self, text: str) -> str:
        text_stripped = text.strip()
        
        # If it is already valid JSON, don't touch it
        try:
            json.loads(text_stripped)
            return text_stripped
        except json.JSONDecodeError:
            pass

        # 1. Try finding ```json or ```JSON
        lower_text = text_stripped.lower()
        start_marker = "```json"
        if start_marker in lower_text:
            start_idx = lower_text.find(start_marker) + len(start_marker)
            end_idx = text_stripped.find("```", start_idx)
            candidate = text_stripped[start_idx:end_idx].strip() if end_idx != -1 else text_stripped[start_idx:].strip()
            try:
                json.loads(candidate)
                return candidate
            except json.JSONDecodeError:
                pass

        # Try general ```
        if "```" in text_stripped:
            start_idx = text_stripped.find("```") + 3
            end_idx = text_stripped.find("```", start_idx)
            candidate = text_stripped[start_idx:end_idx].strip() if end_idx != -1 else text_stripped[start_idx:].strip()
            try:
                json.loads(candidate)
                return candidate
            except json.JSONDecodeError:
                pass

        # 2. Try to find the first '{' and the last '}'
        start_brace = text_stripped.find("{")
        end_brace = text_stripped.rfind("}")
        if start_brace != -1 and end_brace != -1 and end_brace > start_brace:
            candidate = text_stripped[start_brace:end_brace + 1].strip()
            try:
                json.loads(candidate)
                return candidate
            except json.JSONDecodeError:
                pass

        # 3. Try to find the first '[' and the last ']'
        start_bracket = text_stripped.find("[")
        end_bracket = text_stripped.rfind("]")
        if start_bracket != -1 and end_bracket != -1 and end_bracket > start_bracket:
            candidate = text_stripped[start_bracket:end_bracket + 1].strip()
            try:
                json.loads(candidate)
                return candidate
            except json.JSONDecodeError:
                pass

        # 4. Try to find the last '{' and matching/last '}' (searching backwards)
        braces_indices = [i for i, char in enumerate(text_stripped) if char == '{']
        for start_idx in reversed(braces_indices):
            if end_brace > start_idx:
                candidate = text_stripped[start_idx:end_brace + 1].strip()
                try:
                    json.loads(candidate)
                    return candidate
                except json.JSONDecodeError:
                    pass

        # 5. Try the same for brackets
        brackets_indices = [i for i, char in enumerate(text_stripped) if char == '[']
        for start_idx in reversed(brackets_indices):
            if end_bracket > start_idx:
                candidate = text_stripped[start_idx:end_bracket + 1].strip()
                try:
                    json.loads(candidate)
                    return candidate
                except json.JSONDecodeError:
                    pass

        # Return the original stripped text if all extraction attempts fail
        return text_stripped

    def generate(
        self,
        prompt: str,
        system_instruction: Optional[str] = None,
        json_mode: bool = False
    ) -> str:
        print(f"[GeminiProvider] Generating content using model: {self.model_name}")
        
        # Load model with system instruction if provided
        model = genai.GenerativeModel(
            model_name=self.model_name,
            system_instruction=system_instruction
        )
        
        generation_config = {}
        if json_mode:
            generation_config["response_mime_type"] = "application/json"
            
        response = model.generate_content(
            prompt,
            generation_config=generation_config
        )
        
        print(f"[GeminiProvider] Raw Gemini response: {response}")
        try:
            print(f"[GeminiProvider] response.text: {response.text}")
        except Exception as e:
            print(f"[GeminiProvider] response.text retrieval failed: {e}")
            
        if not response or not hasattr(response, "text") or not response.text:
            if response and response.candidates and len(response.candidates) > 0:
                candidate = response.candidates[0]
                if hasattr(candidate, "finish_reason") and str(candidate.finish_reason) != "FinishReason.STOP":
                    raise ValueError(f"Gemini model returned a response with no text candidate. Finish reason: {candidate.finish_reason}")
            raise ValueError("Gemini model returned an empty or invalid response object.")
            
        text = response.text.strip()
        if not text:
            raise ValueError("Gemini model returned an empty text response.")
            
        cleaned_text = text
        if json_mode:
            cleaned_text = self._clean_json(text)
            try:
                # Attempt to parse to validate JSON structure
                json.loads(cleaned_text)
            except json.JSONDecodeError as e:
                # Log raw response and raise descriptive exception
                logger.error(f"Failed to parse JSON from Gemini. Raw response:\n{text}")
                print(f"[GeminiProvider] JSON validation failed. Raw response was:\n{text}")
                raise ValueError(f"Gemini response was not valid JSON: {e}")
                
        return cleaned_text

