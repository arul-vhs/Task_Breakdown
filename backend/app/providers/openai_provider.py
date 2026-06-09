from typing import Optional
from app.providers.base_provider import BaseProvider
from app.core.config import settings

class OpenAIProvider(BaseProvider):
    def __init__(self, api_key: Optional[str] = None, model_name: Optional[str] = None):
        self.api_key = api_key or settings.OPENAI_API_KEY
        self.model_name = model_name or "gpt-4o"
        self._client = None

    @property
    def client(self):
        if self._client is None:
            try:
                from openai import OpenAI
            except ImportError:
                raise ImportError(
                    "openai package is not installed. Please run 'pip install openai' to use the OpenAIProvider."
                )
            self._client = OpenAI(api_key=self.api_key)
        return self._client

    def generate(
        self,
        prompt: str,
        system_instruction: Optional[str] = None,
        json_mode: bool = False
    ) -> str:
        messages = []
        if system_instruction:
            messages.append({"role": "system", "content": system_instruction})
        messages.append({"role": "user", "content": prompt})

        response_format = {"type": "text"}
        if json_mode:
            # For JSON mode, OpenAI models generally require the prompt to contain 'json'
            # We enforce JSON response format
            response_format = {"type": "json_object"}

        response = self.client.chat.completions.create(
            model=self.model_name,
            messages=messages,
            response_format=response_format
        )
        return response.choices[0].message.content
