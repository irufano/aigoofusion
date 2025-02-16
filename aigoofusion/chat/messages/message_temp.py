from typing import Any, Dict, List, Optional

from aigoofusion.chat.messages.message import Message
from aigoofusion.chat.messages.role import Role
from aigoofusion.chat.messages.tool_call import ToolCall
from aigoofusion.chat.models.bedrock.bedrock_formatter import BedrockFormatter
from aigoofusion.chat.models.model_provider import ModelProvider
from aigoofusion.chat.models.openai.openai_formatter import OpenAIFormatter
from aigoofusion.chat.models.model_formatter import ModelFormatter
from aigoofusion.exception.aigoo_exception import AIGooException


class MessageTemp:
    """MessageTemp class. History only per request, not saved to memory."""

    # Register formatter
    _formatters: Dict[ModelProvider, ModelFormatter] = {
        ModelProvider.OPENAI: OpenAIFormatter(),
        ModelProvider.BEDROCK: BedrockFormatter(),
    }

    def __init__(self):
        self.messages: List[Message] = []

    def add_system_message(self, content: str) -> None:
        self.messages.insert(0, Message(role=Role.SYSTEM, content=content))

    def add_user_message(self, id: str, content: str) -> None:
        self.messages.append(Message(id=id, role=Role.USER, content=content))

    def add_assistant_message(
        self,
        id: str,
        content: Optional[str] = None,
        tool_calls: Optional[List[ToolCall]] = None,
    ) -> None:
        # Update request call id by parent
        if tool_calls:
            for tool_call in tool_calls:
                tool_call.request_call_id = id

        self.messages.append(
            Message(id=id, role=Role.ASSISTANT, content=content, tool_calls=tool_calls)
        )

    def add_tool_message(
        self,
        id: str,
        tool_call_id: str,
        name: str,
        result: str,
        provider: ModelProvider,
        request_call_id: Optional[str] = None,
    ) -> None:
        formatter = self._formatters.get(provider)
        if not formatter:
            raise AIGooException(f"Unsupported model provider: {provider}")

        formatter.format_tool_message(
            messages=self.messages,
            id=id,
            tool_call_id=tool_call_id,
            name=name,
            request_call_id=request_call_id,
            result=result,
        )

    def get_messages(self, provider: ModelProvider) -> List[Dict[str, Any]]:
        formatter = self._formatters.get(provider)
        if not formatter:
            raise AIGooException(f"Unsupported model provider: {provider}")
        return [formatter.format_message(msg) for msg in self.messages]

    def get_instance_messages(self) -> List[Message]:
        # return [msg for msg in self.messages if msg.role != Role.SYSTEM]
        return self.messages

    def clear(self) -> None:
        system_message = next(
            (msg for msg in self.messages if msg.role == Role.SYSTEM), None
        )
        self.messages.clear()
        if system_message:
            self.messages.append(system_message)
