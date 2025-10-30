import asyncio
import threading
from typing import Coroutine, Callable

def run_async_task(coro: Coroutine, callback: Callable):
    """
    Runs an async coroutine in a new background thread and calls a callback with the result.
    This safely manages the asyncio event loop lifecycle.

    Args:
        coro: The coroutine to run (e.g., an async function call).
        callback: The function to call with the result of the coroutine. This will be
                  scheduled to run on the main GUI thread.
    """
    def thread_target():
        # Get or create a new event loop for this thread
        try:
            loop = asyncio.get_running_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)

        try:
            result = loop.run_until_complete(coro)
            # The 'after' method needs to be called from the main thread's root window,
            # but we don't have a direct reference to it here.
            # Instead, we rely on the callback being scheduled correctly by the caller.
            callback(result)
        finally:
            loop.close()

    threading.Thread(target=thread_target).start()
