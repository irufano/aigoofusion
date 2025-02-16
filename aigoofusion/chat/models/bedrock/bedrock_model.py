import os
from typing import Any, Dict, List

import boto3

from aigoofusion.chat.messages.tool_call import ToolCall
from aigoofusion.chat.models.base_ai_model import BaseAIModel
from aigoofusion.chat.models.bedrock.bedrock_config import (
    BedrockConfig,
)
from aigoofusion.chat.models.bedrock.bedrock_usage_tracker import track_bedrock_usage
from aigoofusion.chat.models.model_provider import ModelProvider
from aigoofusion.chat.responses.ai_response import AIResponse
from aigoofusion.exception.aigoo_exception import AIGooException


class BedrockModel(BaseAIModel):
    def __init__(self, model: str, config: BedrockConfig):
        if not os.getenv("AWS_ACCESS_KEY_ID"):
            raise AIGooException(
                "Please provide `AWS_ACCESS_KEY_ID` on your environment!"
            )
        if not os.getenv("AWS_SECRET_ACCESS_KEY"):
            raise AIGooException(
                "Please provide `AWS_SECRET_ACCESS_KEY` on your environment!"
            )
        if not os.getenv("BEDROCK_AWS_REGION"):
            raise AIGooException(
                "Please provide `BEDROCK_AWS_REGION` on your environment!"
            )

        self.provider = ModelProvider.BEDROCK
        self.model_name = model
        self.config = config
        self.client = boto3.client(
            "bedrock-runtime",
            aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
            aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
            region_name=os.getenv("BEDROCK_AWS_REGION"),
        )

    @track_bedrock_usage
    def __call_bedrock(self, params: dict[str, Any]):
        try:
            response = self.client.converse(**params)
            return response
        except Exception as e:
            raise e

    def generate(
        self,
        messages: List[Dict[str, Any]],
        tools: List[Dict[str, Any]] | None = None,
        **kwargs,
    ) -> AIResponse:
        try:
            _system = [msg for msg in messages if msg["role"] == "system"][0]["content"]
            _messages = [msg for msg in messages if msg["role"] != "system"]

            inferences = {
                "temperature": self.config.temperature,
                "maxTokens": self.config.max_tokens,
                "stopSequences": self.config.stopSequences,
                "topP": self.config.top_p,
            }
            # Remove None values
            inference_config = {
                key: value for key, value in inferences.items() if value is not None
            }

            additionals = {
                "top_k": self.config.top_k,
                **kwargs,
            }
            # Remove None values
            additional_config = {
                key: value for key, value in additionals.items() if value is not None
            }

            params = {
                "modelId": self.model_name,
                "messages": _messages,
                "system": _system,
                "inferenceConfig": inference_config,
                "additionalModelRequestFields": additional_config,
            }

            if tools:
                """
                ToolConfig
                {
                    "tools": [
                        {
                            "toolSpec": {
                                "name": "top_song",
                                "description": "Get the most popular song played on a radio station.",
                                "inputSchema": {
                                    "json": {
                                        "type": "object",
                                        "properties": {
                                            "sign": {
                                                "type": "string",
                                                "description": "The call sign for the radio station for which you want the most popular song. Example calls signs are WZPZ and WKRP."
                                            }
                                        },
                                        "required": [
                                            "sign"
                                        ]
                                    }
                                }
                            }
                        }
                    ]
                }
                """
                params["toolConfig"] = {"tools": [{"toolSpec": tool} for tool in tools]}

            response = self.__call_bedrock(params)

            output_message = response["output"]["message"]
            stop_reason = response["stopReason"]
            tool_calls = None
            content = None

            if stop_reason == "tool_use":
                tool_requests = response["output"]["message"]["content"]
                tool_callings = []
                for tool_request in tool_requests:
                    if "toolUse" in tool_request:
                        tool = tool_request["toolUse"]
                        tool_callings.append(
                            ToolCall(
                                request_call_id=response["ResponseMetadata"][
                                    "RequestId"
                                ],
                                tool_call_id=tool["toolUseId"],
                                name=tool["name"],
                                arguments=tool["input"],
                            )
                        )
                tool_calls = tool_callings
            else:
                content = output_message["content"][0]["text"]

            return AIResponse(
                content=content,
                tool_calls=tool_calls,
            )
        except Exception as e:
            raise AIGooException(e)

    def generate_stream(
        self,
        messages: List[Dict[str, Any]],
        tools: List[Dict[str, Any]] | None = None,
        **kwargs,
    ) -> Any:
        try:
            _system = [msg for msg in messages if msg["role"] == "system"][0]["content"]
            _messages = [msg for msg in messages if msg["role"] != "system"]

            inferences = {
                "temperature": self.config.temperature,
                "maxTokens": self.config.max_tokens,
                "stopSequences": self.config.stopSequences,
                "topP": self.config.top_p,
            }
            # Remove None values
            inference_config = {
                key: value for key, value in inferences.items() if value is not None
            }

            additionals = {
                "top_k": self.config.top_k,
                **kwargs,
            }
            # Remove None values
            additional_config = {
                key: value for key, value in additionals.items() if value is not None
            }

            params = {
                "modelId": self.model_name,
                "messages": _messages,
                "system": _system,
                "inferenceConfig": inference_config,
                "additionalModelRequestFields": additional_config,
            }

            if tools:
                params["toolConfig"] = {"tools": [{"toolSpec": tool} for tool in tools]}

            return self.client.converse_stream(**params)

        except Exception as e:
            raise AIGooException(e)
