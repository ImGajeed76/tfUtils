from functools import wraps
from typing import Callable


def interface(name: str, activate: bool = True) -> Callable:
    """Decorator to mark and name interface functions."""

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            return func(*args, **kwargs)

        if activate:
            wrapper._NAME = name
            wrapper._IS_INTERFACE = True
        return wrapper

    return decorator
