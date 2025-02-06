from typing import List
from pydantic import BaseModel, ConfigDict, Field

from aigoo_fusion.chat.messages.message import Message
from aigoo_fusion.chat.responses.ai_response import AIResponse


class ChatResponse(BaseModel):
    """ChatResponse Class"""
    model_config = ConfigDict(extra='forbid')
    result: AIResponse 
    process: List[Message] = Field(default_factory=list)
