"""Bounded process-local memoization. Never persist prompts or model output to disk."""
from collections import OrderedDict
from copy import deepcopy
from functools import wraps
from threading import RLock
from time import monotonic


def memoized(maxsize=64, ttl=900):
    """Return independent values; serialize misses to avoid duplicate inference work."""
    def decorate(fn):
        cache = OrderedDict()
        lock = RLock()

        @wraps(fn)
        def wrapped(*args):
            with lock:
                now = monotonic()
                if args in cache:
                    expires, value = cache[args]
                    if expires > now:
                        cache.move_to_end(args)
                        return deepcopy(value)
                    del cache[args]
                value = fn(*args)  # Exceptions are never cached.
                cache[args] = (monotonic() + ttl, deepcopy(value))
                while len(cache) > maxsize:
                    cache.popitem(last=False)
                return deepcopy(value)

        def clear():
            with lock:
                cache.clear()

        wrapped.cache_clear = clear
        return wrapped
    return decorate
