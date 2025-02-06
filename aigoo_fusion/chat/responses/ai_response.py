from typing import List, Optional
from pydantic import BaseModel, ConfigDict

from aigoo_fusion.chat.messages.tool_call import ToolCall


class AIResponse(BaseModel):
    """AIResponse Class"""
    model_config = ConfigDict(extra='forbid')
    content: Optional[str] = None
    tool_calls: Optional[List[ToolCall]] = None