import asyncio


def run_async(coro):
    loop = asyncio.get_event_loop()
    f = asyncio.run_coroutine_threadsafe(coro, loop)
    return f
