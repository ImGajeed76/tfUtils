from functools import wraps


def interface(name: str, activate: bool = True):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            return func(*args, **kwargs)

        if activate:
            wrapper._NAME = name
            wrapper._IS_INTERFACE = True
        return wrapper

    return decorator