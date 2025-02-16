from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional

from aigoofusion.chat.messages.message import Message
# from aigoofusion.chat.tools.function_parser import FunctionParser


class ModelFormatter(ABC):
    """ModelFormatter.

    Register all derivated intances from this class to:
        - `MessageTemp` class at `aigoofusion/chat/messages/message_temp.py`
        - `Tool` class at `aigoofusion/chat/tools/tool.py`

    Args:
        ABC (_type_): _description_
    """

    @abstractmethod
    def format_message(self, message: Message) -> dict:
        pass

    @abstractmethod
    def format_tool_function(
        self, func_metadata: Dict, type_mapping: dict[Any, str]
    ) -> dict:
        pass

    @abstractmethod
    def format_tool_message(
        self,
        messages: List[Message],
        id: str,
        tool_call_id: str,
        name: str,
        result: str,
        request_call_id: Optional[str] = None,
    ) -> List[Message]:
        pass
