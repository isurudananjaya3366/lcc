"""
Thread-local middleware for tracking the current request user.

Used by pricing signals to record ``changed_by`` on PriceHistory
without passing the user through every model save call.
"""

import threading

_thread_locals = threading.local()


def get_current_user():
    """Return the user set by CurrentUserMiddleware, or None."""
    return getattr(_thread_locals, "user", None)


class CurrentUserMiddleware:
    """
    Store ``request.user`` in thread-local storage so that model-layer
    code (signals) can access it without an explicit argument.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        _thread_locals.user = getattr(request, "user", None)
        response = self.get_response(request)
        # Clean up after request
        _thread_locals.user = None
        return response
