from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional

from aigoofusion.chat.models.model_provider import ModelProvider
from aigoofusion.chat.responses.ai_response import AIResponse


class BaseAIModel(ABC):
    """BaseAIModel Abstract"""

    def __init__(self):
        """Model provider."""
        self.provider: ModelProvider

    @abstractmethod
    def generate(
        self,
        messages: List[Dict[str, Any]],
        tools: Optional[List[Dict[str, Any]]] = None,
        **kwargs,
    ) -> AIResponse:
        pass

    @abstractmethod
    def generate_stream(
        self,
        messages: List[Dict[str, Any]],
        tools: Optional[List[Dict[str, Any]]] = None,
        **kwargs,
    ) -> Any:
        pass
