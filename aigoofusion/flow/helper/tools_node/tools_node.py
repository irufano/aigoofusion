from typing import Any, List

from aigoofusion.chat.messages.message import Message
from aigoofusion.chat.messages.role import Role
from aigoofusion.chat.tools.tool_registry import ToolRegistry


def tools_node(messages: List[Message], registry: ToolRegistry):
	new_messages = messages
	last_message = new_messages[-1]
	if last_message.tool_calls:
		for tool_call in last_message.tool_calls:
			result = registry.execute_tool(
				name=tool_call.name,
				arguments=tool_call.arguments
			)
			new_messages.append(
				Message(
					role=Role.TOOL, 
					content=str(result), 
					tool_call_id=tool_call.tool_call_id, 
					name=tool_call.name)
			)
	return new_messages
