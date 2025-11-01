import asyncio
import threading
from typing import Coroutine, Callable

def run_async_task(coro: Coroutine, callback: Callable, scheduler: Callable):
    """
    Runs an async coroutine in a new background thread and uses a scheduler
    to pass the result to a callback on the main thread.

    Args:
        coro: The coroutine to run.
        callback: The function to call with the result of the coroutine.
        scheduler: A function from the main thread's event loop that can schedule
                   a function to be called later (e.g., `root.after`).
    """
    def thread_target():
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            result = loop.run_until_complete(coro)
            # Use the scheduler to safely call the callback on the main thread
            scheduler(0, lambda: callback(result))
        finally:
            loop.close()

    threading.Thread(target=thread_target).start()
