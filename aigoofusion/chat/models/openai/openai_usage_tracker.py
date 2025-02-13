from contextlib import contextmanager
from contextvars import ContextVar
import functools

from aigoofusion.chat.models.openai.openai_usage import OpenAIUsage

# Thread-safe storage for token usage per request
OPENAI_USAGE_TRACKER_VAR = ContextVar("OPENAI_USAGE_TRACKER", default=OpenAIUsage())


@contextmanager
def openai_usage_tracker():
    """OpenAI usage tracker.

    Use this to track token usage on openai.

    Example:
    ```python
    with openai_usage_tracker() as usage:
            result = llm.generate(messages)
            ...
            print(usage)
    ```

    Yields:
            OpenAIUsage: OpenAI usage accumulation.
    """
    usage_tracker = OpenAIUsage()
    OPENAI_USAGE_TRACKER_VAR.set(usage_tracker)  # Store usage_tracker it in the context
    try:
        yield usage_tracker  # Expose tracker to the context
    finally:
        print("")


def track_openai_usage(func):
    """Decorator to wrap `__call_openai` calls on `OpenAIModel`."""

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        response = func(*args, **kwargs)
        model = args[1][
            "model"
        ]  # args is tuple[OpenAIModel, params] and params contain `model`
        if response.usage:
            usage = response.usage
            usage_tracker = OPENAI_USAGE_TRACKER_VAR.get()
            usage_tracker.update(model=model, usage=usage)
        return response

    return wrapper
