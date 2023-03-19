import asyncio

def async_caller(func, *rest):
    if callable(func):
        loop = asyncio.get_event_loop()
        result = loop.run_until_complete(func(*rest))
        loop.close()
        return result
    return None