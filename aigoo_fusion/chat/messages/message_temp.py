from typing import Any, Dict, List, Optional

from aigoo_fusion.chat.messages.message import Message
from aigoo_fusion.chat.messages.role import Role
from aigoo_fusion.chat.messages.tool_call import ToolCall


class MessageTemp:
	"""MessageTemp class. History only per request, not saved to memory."""
	def __init__(self):
		self.messages: List[Message] = []

	def add_system_message(self, content: str) -> None:
		self.messages.insert(0, Message(role=Role.SYSTEM, content=content))

	def add_user_message(self, content: str) -> None:
		self.messages.append(Message(role=Role.USER, content=content))

	def add_assistant_message(
		self, content: Optional[str] = None, tool_calls: Optional[List[ToolCall]] = None
	) -> None:
		self.messages.append(
			Message(role=Role.ASSISTANT, content=content, tool_calls=tool_calls)
		)

	def add_tool_message(self, tool_call_id: str, name: str, content: str) -> None:
		self.messages.append(
			Message(
				role=Role.TOOL, content=content, tool_call_id=tool_call_id, name=name
			)
		)

	def get_messages(self) -> List[Dict[str, Any]]:
		return [msg.to_dict() for msg in self.messages]

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

