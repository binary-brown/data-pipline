from functools import wraps
import asyncio
from typer import Typer


class AsyncTyper(Typer):
    def async_command(app, *args, **kwargs):
        def decorator(func):
            
            @wraps(func)
            def wrapper(*args, **kwargs):
                return asyncio.run(func(*args, **kwargs))

            app.command(*args, **kwargs)(wrapper)

            return wrapper

        return decorator
