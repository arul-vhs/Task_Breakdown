import logging
import concurrent.futures
from typing import Optional
from app.providers.base_provider import BaseProvider
from app.providers.gemini_provider import GeminiProvider
from app.providers.openai_provider import OpenAIProvider
from app.core.logger import update_log_context

logger = logging.getLogger("goalpilot.providers.failover_provider")

# Global thread pool for enforcing generation timeouts
executor = concurrent.futures.ThreadPoolExecutor(max_workers=10)

class FailoverProvider(BaseProvider):
    MAX_PROVIDER_RETRY = 1
    TIMEOUT_SECONDS = 90

    def __init__(self, gemini_api_key: Optional[str] = None, openai_api_key: Optional[str] = None):
        self.providers = []
        
        # Initialize Gemini Provider
        try:
            gemini = GeminiProvider(api_key=gemini_api_key)
            self.providers.append(("Gemini", gemini))
        except Exception as e:
            logger.warning(f"Could not initialize GeminiProvider: {e}")
            
        # Initialize OpenAI Provider
        try:
            openai = OpenAIProvider(api_key=openai_api_key)
            self.providers.append(("OpenAI", openai))
        except Exception as e:
            logger.warning(f"Could not initialize OpenAIProvider: {e}")

    def generate(
        self,
        prompt: str,
        system_instruction: Optional[str] = None,
        json_mode: bool = False
    ) -> str:
        if not self.providers:
            raise RuntimeError("No LLM providers are configured or available.")

        last_error = None
        for name, provider in self.providers:
            # Try execution with retries
            for attempt in range(self.MAX_PROVIDER_RETRY + 1):
                update_log_context({
                    "event": "llm_generation_attempt",
                    "provider": name,
                    "attempt": attempt + 1
                })
                logger.info(f"LLM generation attempt {attempt + 1} with {name}")
                
                try:
                    # Execute provider with a timeout safeguard
                    future = executor.submit(
                        provider.generate, 
                        prompt, 
                        system_instruction=system_instruction, 
                        json_mode=json_mode
                    )
                    result = future.result(timeout=self.TIMEOUT_SECONDS)
                    
                    update_log_context({
                        "event": "llm_generation_success",
                        "provider": name
                    })
                    logger.info(f"LLM generation succeeded with {name}")
                    return result
                    
                except concurrent.futures.TimeoutError as e:
                    last_error = RuntimeError(f"Request to {name} timed out after {self.TIMEOUT_SECONDS}s")
                    update_log_context({
                        "event": "llm_generation_timeout",
                        "provider": name,
                        "attempt": attempt + 1
                    })
                    logger.error(f"Generation timed out with {name} on attempt {attempt + 1}")
                    
                except (Exception, ImportError) as e:
                    last_error = e
                    update_log_context({
                        "event": "llm_generation_failed",
                        "provider": name,
                        "attempt": attempt + 1,
                        "error": str(e)
                    })
                    logger.error(f"Generation failed with {name} on attempt {attempt + 1}: {e}")
            
            # Switch provider
            update_log_context({"event": "llm_provider_switch", "from": name})
            logger.warning(f"Failing over from provider {name} due to repeated errors/timeouts.")

        raise RuntimeError(f"All LLM providers in the chain failed. Last error: {last_error}")
