from abc import ABC, abstractmethod
from typing import Optional

class BaseProvider(ABC):
    @abstractmethod
    def generate(
        self,
        prompt: str,
        system_instruction: Optional[str] = None,
        json_mode: bool = False
    ) -> str:
        """
        Generates text using the model.
        
        Args:
            prompt (str): Prompt to send to the provider model.
            system_instruction (Optional[str]): System instructions/context instructions.
            json_mode (bool): If True, requests JSON output from the model.
            
        Returns:
            str: Generated content response from the provider.
        """
        pass
