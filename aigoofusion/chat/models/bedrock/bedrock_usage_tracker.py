from contextlib import contextmanager
from contextvars import ContextVar
import functools

from aigoofusion.chat.models.bedrock.bedrock_usage import BedrockUsage

# Thread-safe storage for token usage per request
BEDROCK_USAGE_TRACKER_VAR = ContextVar("BEDROCK_USAGE_TRACKER", default=BedrockUsage())


@contextmanager
def bedrock_usage_tracker():
    """Bedrock usage tracker.

    Use this to track token usage on bedrock.

    Example:
    ```python
    with bedrock_usage_tracker() as usage:
            result = chat.generate(messages)
            ...
            print(usage)
    ```

    Yields:
            BedrockUsage: Bedrock usage accumulation.
    """
    usage_tracker = BedrockUsage()
    BEDROCK_USAGE_TRACKER_VAR.set(
        usage_tracker
    )  # Store usage_tracker it in the context
    try:
        yield usage_tracker  # Expose tracker to the context
    finally:
        print("")


def track_bedrock_usage(func):
    """Decorator to wrap `__call_bedrock` calls on `BedrockModel`."""

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        response = func(*args, **kwargs)
        model = args[1][
            "modelId"
        ]  # args is tuple[BedrockModel, params] and params contain `modelId`
        if response["usage"]:
            usage = response["usage"]
            usage_tracker = BEDROCK_USAGE_TRACKER_VAR.get()
            usage_tracker.update(model=model, usage=usage)
        return response

    return wrapper
