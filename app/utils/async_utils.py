import asyncio
import threading

def run_async_task(coro, loop, queue, callback):
    """
    Executes a coroutine in a background thread on the main application's event loop,
    and queues a callback to be executed on the main UI thread upon completion.

    This is the standard, non-blocking way to run async tasks from the UI in this application.

    Args:
        coro: The coroutine to execute.
        loop: The main asyncio event loop of the application.
        queue: The thread-safe queue for UI updates.
        callback: The function to call on the main thread with the result of the coroutine.
    """
    def task_wrapper():
        # This function runs in a separate thread.
        # It submits the coroutine to the main event loop and waits for the result.
        future = asyncio.run_coroutine_threadsafe(coro, loop)
        try:
            result = future.result()
            # Once the result is ready, put it and the callback into the thread-safe queue.
            queue.put((callback, (result,)))
        except Exception as e:
            # If the async task raises an exception, queue it for the callback to handle.
            queue.put((callback, (e,)))

    # Start the background thread to manage the async task.
    thread = threading.Thread(target=task_wrapper)
    thread.daemon = True
    thread.start()
