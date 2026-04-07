"""
Base Middleware.

Provides :class:`BaseMiddleware`, an abstract base class that all
LankaCommerce middleware should inherit from.  It follows the Django
middleware protocol while exposing user-friendly ``process_request``
and ``process_response`` hooks.
"""

from __future__ import annotations

import abc
import logging
from typing import Any

from django.http import HttpRequest, HttpResponse

logger = logging.getLogger(__name__)


class BaseMiddleware(abc.ABC):
    """
    Abstract base middleware for LankaCommerce Cloud.

    Subclasses **must** implement at least one of:

    * :meth:`process_request` — called before the view.
    * :meth:`process_response` — called after the view.

    A subclass may also override :meth:`process_exception` to intercept
    unhandled exceptions.

    Usage::

        class MyMiddleware(BaseMiddleware):
            def process_request(self, request):
                request.my_flag = True
                return None  # continue chain

            def process_response(self, request, response):
                response["X-My-Header"] = "1"
                return response
    """

    def __init__(self, get_response: Any) -> None:
        self.get_response = get_response

    def __call__(self, request: HttpRequest) -> HttpResponse:
        # Pre-processing
        short_circuit = self.process_request(request)
        if short_circuit is not None:
            return short_circuit

        # Delegate to next middleware / view
        try:
            response = self.get_response(request)
        except Exception as exc:
            handled = self.process_exception(request, exc)
            if handled is not None:
                return handled
            raise

        # Post-processing
        response = self.process_response(request, response)
        return response

    # ------------------------------------------------------------------
    # Hooks — subclasses override these
    # ------------------------------------------------------------------

    def process_request(self, request: HttpRequest) -> HttpResponse | None:
        """
        Called before the view.

        Return ``None`` to continue the chain, or return an
        ``HttpResponse`` to short-circuit.
        """
        return None

    def process_response(
        self, request: HttpRequest, response: HttpResponse
    ) -> HttpResponse:
        """
        Called after the view.

        Must return the (possibly modified) ``response``.
        """
        return response

    def process_exception(
        self, request: HttpRequest, exception: Exception
    ) -> HttpResponse | None:
        """
        Called when the view (or a later middleware) raises an exception.

        Return ``None`` to let the exception propagate, or return an
        ``HttpResponse`` to handle it.
        """
        return None
