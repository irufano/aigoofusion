from typing import Any, Callable, Dict

from aigoofusion.chat.models.model_formatter import ModelFormatter
from aigoofusion.chat.models.bedrock.bedrock_formatter import BedrockFormatter
from aigoofusion.chat.models.model_provider import ModelProvider
from aigoofusion.chat.models.openai.openai_formatter import OpenAIFormatter
from aigoofusion.chat.tools.function_parser import FunctionParser
from aigoofusion.chat.tools.function_type_mapping import FUNCTION_TYPE_MAPPING
from aigoofusion.exception.aigoo_exception import AIGooException


class Tool:
    """
    Decorator class for creating tool definitions.
    """

    # Register formatter
    _formatters: Dict[ModelProvider, ModelFormatter] = {
        ModelProvider.OPENAI: OpenAIFormatter(),
        ModelProvider.BEDROCK: BedrockFormatter(),
    }

    def __init__(self, strict: bool = True):
        self.strict = strict

    def __call__(self, func: Callable) -> Callable:
        func._is_tool = True  # type: ignore # Mark the function as a tool
        func._tool_strict = self.strict  # type: ignore # Store strict setting. to check: getattr(func, '_tool_strict', True)
        return func

    @staticmethod
    def _get_tool_definition(func: Callable, provider: ModelProvider) -> Dict[str, Any]:
        formatter = Tool._formatters.get(provider)
        if not formatter:
            raise AIGooException(f"Unsupported model provider: {provider}")

        metadata = FunctionParser.get_function_metadata(func)
        return formatter.format_tool_function(metadata, FUNCTION_TYPE_MAPPING)
