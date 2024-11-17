from functools import wraps
from typing import Any, Callable, Coroutine, Union

from textual.containers import Container


def interface(
    name: str, activate: Union[bool, Callable[[], bool]] = True
) -> Callable[[Callable[[Container], Coroutine]], Callable[[Container], Coroutine]]:
    """
    Decorator to mark and name interface functions with runtime activation check.

    Args:
        name: The name to assign to the interface
        activate: Boolean or callable that returns whether interface should be active
    """

    def decorator(
        func: Callable[[Container], Coroutine]
    ) -> Callable[[Container], Coroutine]:
        @wraps(func)
        async def wrapper(container: Container) -> Any:
            return await func(container)

        wrapper._NAME = name
        wrapper._IS_INTERFACE = True
        if isinstance(activate, bool):
            wrapper._ACTIVATE = lambda: activate
        else:
            wrapper._ACTIVATE = activate
        return wrapper

    return decorator
