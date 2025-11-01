import asyncio
import threading
from typing import Coroutine, Callable
from queue import Queue

def run_async_task(coro: Coroutine, queue: Queue, callback: Callable):
    """
    Runs a coroutine in a background thread and puts the callback and result
    onto a queue for the main thread to process.

    Args:
        coro: The coroutine to run.
        queue: The queue to put the result on.
        callback: The function to be called with the result.
    """
    def thread_target():
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            result = loop.run_until_complete(coro)
            # Put the callback and its arguments onto the queue
            queue.put((callback, (result,)))
        except Exception as e:
            # It's good practice to handle potential exceptions in the async task
            print(f"Error in background task: {e}")
            # Optionally put the error on the queue for the UI to handle
            # queue.put((error_callback, (e,)))
        finally:
            loop.close()

    threading.Thread(target=thread_target).start()
