import asyncio
from concurrent.futures import Future
import threading

def run_async_task(coro, queue, callback):
    """
    Runs a coroutine in a background thread and puts the result in a queue.
    This is for non-blocking async tasks where the UI should remain responsive.
    """
    def task_wrapper():
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            result = loop.run_until_complete(coro)
            queue.put((callback, (result,)))
        finally:
            loop.close()

    thread = threading.Thread(target=task_wrapper)
    thread.daemon = True
    thread.start()

def run_async_and_wait(coro, loop):
    """
    Executes a coroutine on a running asyncio event loop from a synchronous context
    and waits for its result.
    This is for blocking tasks where the UI should wait for the result.
    """
    future = asyncio.run_coroutine_threadsafe(coro, loop)
    return future.result()
