import json
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, ConfigDict

from aigoo_fusion.chat.messages.role import Role
from aigoo_fusion.chat.messages.tool_call import ToolCall


class Message(BaseModel):
	"""Message class for input to the LLM models."""
	model_config = ConfigDict(extra='forbid')

	role: Role
	content: Optional[str] = None
	tool_calls: Optional[List[ToolCall]] = None # For Message with `assistant` role
	tool_call_id: Optional[str] = None # For Message with `tool` role
	name: Optional[str] = None

	def to_dict(self) -> dict:
		message_dict: Dict[str, Any] = {
			"role": self.role.value
		}

		if self.content is not None:
			message_dict["content"] = self.content

		if self.tool_calls:
			message_dict["tool_calls"] = [
				{
					"id": tool_call.tool_call_id,
					"type": "function",
					"function": {
						"name": tool_call.name,
						"arguments": json.dumps(tool_call.arguments),
					},
				}
				for tool_call in self.tool_calls
			]

		if self.tool_call_id:
			message_dict["tool_call_id"] = self.tool_call_id

		if self.name:
			message_dict["name"] = self.name

		return message_dict
