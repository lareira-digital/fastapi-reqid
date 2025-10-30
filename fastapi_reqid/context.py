"""
Context management utilities for request ID propagation.

Uses Python's contextvars to provide thread-safe, async-compatible
access to the current request ID throughout the application.
"""

from contextvars import ContextVar, Token
from typing import Optional

# Global context variable to store the current request ID
request_id_context: ContextVar[Optional[str]] = ContextVar("request_id", default=None)


def get_request_id() -> Optional[str]:
    """
    Get the current request ID from context.

    Returns:
        The current request ID, or None if not set

    Example:
        ```python
        from middleware import get_request_id

        def some_function():
            request_id = get_request_id()
            print(f"Processing request: {request_id}")
        ```
    """
    return request_id_context.get()


def set_request_id(request_id: str) -> Token:
    """
    Set the request ID in the current context.

    Args:
        request_id: The request ID to set

    Returns:
        A token that can be used to reset the context

    Example:
        ```python
        from middleware import set_request_id, request_id_context

        token = set_request_id("my-custom-id")
        try:
            # Do work with this request ID
            pass
        finally:
            request_id_context.reset(token)
        ```
    """
    return request_id_context.set(request_id)
