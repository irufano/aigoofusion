from typing import List
from pydantic import BaseModel, ConfigDict, Field

from aigoofusion.chat.messages.message import Message
from aigoofusion.chat.responses.ai_response import AIResponse


class ChatResponse(BaseModel):
    """ChatResponse Class"""

    model_config = ConfigDict(extra="forbid")
    result: AIResponse
    messages: List[Message] = Field(default_factory=list)
