import asyncio
import functools
from pysnmp.hlapi.v1arch.asyncio import *

def ensure_loop():
    try:
        loop = asyncio.get_event_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
    return loop

def create_transport(host: str, port: int, timeout: float = 1.0):
    """
    Await the async factory to build UdpTransportTarget once,
    using our shared loop.
    """
    loop = ensure_loop()
    coro = UdpTransportTarget.create((host, port), timeout=timeout)
    return loop.run_until_complete(coro)

def _sync_coro(coro):
    """
    Run the given coroutine to completion on the shared loop,
    scheduling if needed.
    """
    loop = ensure_loop()
    if loop.is_running():
        fut = asyncio.ensure_future(coro)
        return loop.run_until_complete(fut)
    return loop.run_until_complete(coro)

def _sync_agen(agen):
    """
    Consume an async-generator into a list synchronously.
    """
    async def _collector():
        items = []
        async for item in agen:
            items.append(item)
        return items

    return _sync_coro(_collector())

def make_sync(fn):
    """Turn any pysnmp async‐HLAPI fn into a sync wrapper."""
    @functools.wraps(fn)
    def wrapper(*args, **kwargs):
        return _sync_coro(fn(*args, **kwargs))
    return wrapper

get_cmd_sync = make_sync(get_cmd)
next_cmd_sync = make_sync(next_cmd)
set_cmd_sync = make_sync(set_cmd)
bulk_cmd_sync = make_sync(bulk_cmd)

def walk_cmd_sync(*args, **kwargs):
    """Sync wrapper for walk_cmd (async generator)."""
    return _sync_agen(walk_cmd(*args, **kwargs))

def bulk_walk_cmd_sync(*args, **kwargs):
    """Sync wrapper for bulk_walk_cmd (async generator)."""
    return _sync_agen(bulk_walk_cmd(*args, **kwargs))
