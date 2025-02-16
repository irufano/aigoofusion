import json
import os
import openai
from typing import Any, Dict, List, Optional

from aigoofusion.chat.messages.tool_call import ToolCall
from aigoofusion.chat.models.base_ai_model import BaseAIModel
from aigoofusion.chat.models.model_provider import ModelProvider
from aigoofusion.chat.models.openai.openai_config import OpenAIConfig
from aigoofusion.chat.models.openai.openai_usage import OpenAIUsage
from aigoofusion.chat.models.openai.openai_usage_tracker import track_openai_usage
from aigoofusion.chat.responses.ai_response import AIResponse
from aigoofusion.exception.aigoo_exception import AIGooException


class OpenAIModel(BaseAIModel):
    """
    OpenAIModel class.

    Example:
    ```python
    # Configuration
    config = OpenAIConfig(
            temperature=0.7
    )
    llm = OpenAIModel(model="gpt-4o-mini", config=config)
    ...
    ```

    """

    def __init__(self, model: str, config: OpenAIConfig):
        if not os.getenv("OPENAI_API_KEY"):
            raise AIGooException("Please provide `OPENAI_API_KEY` on your environment!")
        self.provider = ModelProvider.OPENAI
        self.model_name = model
        self.config = config
        self.client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        self.usage_callback = OpenAIUsage()

    @track_openai_usage
    def __call_openai(self, params: dict[str, Any]):
        try:
            response = self.client.chat.completions.create(**params)
            return response
        except Exception as e:
            raise e

    def generate(
        self,
        messages: List[Dict[str, Any]],
        tools: Optional[List[Dict[str, Any]]] = None,
        **kwargs,
    ) -> AIResponse:
        """
        Generate messages.

        Args:
                messages (List[Dict[str, Any]]): _description_
                tools (Optional[List[Dict[str, Any]]], optional): _description_. Defaults to None.

        Raises:
                AIGooChatException: _description_

        Returns:
                AIResponse: _description_
        """
        try:
            params = {
                "model": self.model_name,
                "messages": messages,
                "temperature": self.config.temperature,
                "max_tokens": self.config.max_tokens,
                "top_p": self.config.top_p,
                "frequency_penalty": self.config.frequency_penalty,
                "presence_penalty": self.config.presence_penalty,
                "stream": False,
                **kwargs,
            }

            if tools:
                params["tools"] = [
                    {"type": "function", "function": tool} for tool in tools
                ]
                params["tool_choice"] = "auto"
            print("\nREQUEST:")
            print(json.dumps(params))

            response = self.__call_openai(params)
            print("\nRESPONSE:")
            print(response)

            message = response.choices[0].message
            tool_calls = None
            content = None
            # print(f"usage openai: {response.usage.model_dump()}")
            # token_usage = self.usage_callback.update(self.model_name, response.usage)

            if hasattr(message, "tool_calls") and message.tool_calls:
                tool_calls = [
                    ToolCall(
                        request_call_id=response.id,
                        tool_call_id=tool_call.id,
                        name=tool_call.function.name,
                        arguments=json.loads(tool_call.function.arguments),
                    )
                    for tool_call in message.tool_calls
                ]
            else:
                content = message.content

            return AIResponse(
                content=content,
                tool_calls=tool_calls,
            )

        except Exception as e:
            raise AIGooException(e)

    def generate_stream(
        self,
        messages: List[Dict[str, Any]],
        tools: Optional[List[Dict[str, Any]]] = None,
        **kwargs,
    ) -> Any:
        """
        Generate messages with streaming.

        Note:
                When using stream=True, the response does not include total usage information (usage field with prompt_tokens, completion_tokens, and total_tokens).

                Why?

                \t- In streaming mode, tokens are sent incrementally, so the API doesnt return a single final response that includes token usage.
                \t- If you need token usage, you must track tokens manually or make a separate non-streaming request.

        Args:
                messages (List[Dict[str, Any]]): _description_
                tools (Optional[List[Dict[str, Any]]], optional): _description_. Defaults to None.

        Raises:
                AIGooChatException: _description_

        Returns:
                Any: _description_
        """
        try:
            params = {
                "model": self.model_name,
                "messages": messages,
                "temperature": self.config.temperature,
                "max_tokens": self.config.max_tokens,
                "stream": True,
                **kwargs,
            }

            if tools:
                params["tools"] = [
                    {"type": "function", "function": tool} for tool in tools
                ]
                params["tool_choice"] = "auto"

            return self.client.chat.completions.create(**params)

        except Exception as e:
            raise AIGooException(e)
