import asyncio
from concurrent.futures import Future

def run_async_from_sync(coro, loop):
    """
    Executes a coroutine on a running asyncio event loop from a synchronous context
    and waits for its result.

    This is a safe way to call async code from a sync UI thread without closing
    the main event loop.

    Args:
        coro: The coroutine to execute.
        loop: The asyncio event loop on which to run the coroutine.

    Returns:
        The result of the coroutine.
    """
    future = asyncio.run_coroutine_threadsafe(coro, loop)
    return future.result()
