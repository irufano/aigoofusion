import math
import os
import re
from typing import Dict, List

from aigoofusion.chat.models.bedrock.bedrock_pricing_list import BEDROCK_PRICING
from aigoofusion.chat.models.model_pricing import ModelPricing


class BedrockUsage:
    """
    BedrockUsage class.

    Count bedrock token usage.

    Usage in `BedrockModel`, `bedrock_usage_tracker` and `track_bedrock_usage`
    """

    def __init__(self):
        self.total_request: int = 0
        self.output_tokens: int = 0
        self.input_tokens: int = 0
        self.total_tokens: int = 0
        self.total_cost: float = 0.0
        self.raw_usages: List[Dict[str, int]] = []
        self.pricing: Dict[str, Dict[str, ModelPricing]] = self._load_pricing() or {}

    def __repr__(self) -> str:
        rounded_up = math.ceil(self.total_cost * 1000000) / 1000000
        return (
            f"Total Tokens: {self.total_tokens}\n"
            f"\tInput Tokens: {self.input_tokens}\n"
            f"\tOutput Tokens: {self.output_tokens}\n"
            f"Total Requests: {self.total_request}\n"
            f"Total Cost (USD): ${rounded_up:.6f}"
        )

    def _load_pricing(self) -> Dict[str, Dict[str, ModelPricing]]:
        """
        Load bedrock pricing from dictionary.
        """
        # Price per 1K tokens for different models (USD)
        # https://aws.amazon.com/bedrock/pricing/
        # https://aws.amazon.com/bedrock/pricing/
        # https://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/Concepts.RegionsAndAvailabilityZones.html
        pricing_data = BEDROCK_PRICING
        return {
            model: {
                region: ModelPricing(
                    token_input=pricing["input"],
                    token_output=pricing["output"],
                )
                for region, pricing in regions.items()
            }
            for model, regions in pricing_data.items()
        }

    def update(self, model: str, usage: Dict[str, int]) -> None:
        """
        Update usage statistics and calculate price.

        Args:
            model: Model name
            usage: Dictionary containing token counts
        """

        def has_cross_region_inference_id(s):
            return bool(re.match(r"^.{2}\.", s))

        ONE_K = 1000
        AWS_REGION = os.getenv("BEDROCK_AWS_REGION") or ""
        MODEL = model[3:] if has_cross_region_inference_id(model) else model

        self.raw_usages.append(usage)
        usage_dict = vars(usage) if hasattr(usage, "__dict__") else usage
        self.total_request += 1
        self.input_tokens += usage_dict.get("inputTokens", 0)
        self.output_tokens += usage_dict.get("outputTokens", 0)
        self.total_tokens = self.input_tokens + self.output_tokens

        # Calculate price
        if MODEL in self.pricing:
            price_info = self.pricing[MODEL][AWS_REGION]
            input_price = (self.input_tokens / ONE_K) * price_info.token_input
            output_price = (self.output_tokens / ONE_K) * price_info.token_output
            self.total_cost = input_price + output_price
        pass

    def reset(self):
        """
        Reset usage statistics and calculate price.
        """
        self.total_request = 0
        self.input_tokens = 0
        self.output_tokens = 0
        self.total_tokens = 0
        self.total_cost = 0.0
        self.raw_usages = []
