"""
Route finder service for inter-warehouse transfers.

Provides direct route lookup and multi-hop routing using BFS (Dijkstra-like)
with configurable optimisation metric (transit days or cost).
"""

import heapq
import logging

from django.core.cache import cache

logger = logging.getLogger(__name__)


class RouteFinder:
    """Find routes between warehouses, including multi-hop paths."""

    CACHE_TIMEOUT = 1800  # 30 minutes

    # ── direct lookup ─────────────────────────────────────────────────

    def find_route(self, source, destination):
        """
        Return the best active TransferRoute from *source* → *destination*,
        preferring routes marked ``is_preferred``.  Returns None if none exist.
        """
        from apps.inventory.warehouses.models import TransferRoute

        cache_key = f"route_{source.pk}_{destination.pk}"
        route = cache.get(cache_key)
        if route is not None:
            return route if route != "__none__" else None

        route = (
            TransferRoute.objects.filter(
                source_warehouse=source,
                destination_warehouse=destination,
                is_active=True,
            )
            .order_by("-is_preferred", "transit_days")
            .first()
        )
        cache.set(cache_key, route or "__none__", self.CACHE_TIMEOUT)
        return route

    def get_all_routes(self, warehouse):
        """Return all active outgoing routes for *warehouse*."""
        from apps.inventory.warehouses.models import TransferRoute

        return list(
            TransferRoute.objects.filter(
                source_warehouse=warehouse,
                is_active=True,
            )
            .select_related("destination_warehouse")
            .order_by("-is_preferred", "transit_days")
        )

    # ── multi-hop routing ─────────────────────────────────────────────

    def find_multi_hop_route(self, source, destination, max_hops=3, metric="transit_days"):
        """
        Find a path *source* → *destination* through intermediate warehouses.

        Uses Dijkstra with the given *metric* (``transit_days`` or ``estimated_cost``).
        Returns a list of ``TransferRoute`` segments, or ``[]`` if no path.
        """
        cache_key = f"multi_route_{source.pk}_{destination.pk}_{max_hops}_{metric}"
        cached = cache.get(cache_key)
        if cached is not None:
            return cached if cached != "__empty__" else []

        # Check direct route first
        direct = self.find_route(source, destination)
        if direct:
            result = [direct]
            cache.set(cache_key, result, self.CACHE_TIMEOUT)
            return result

        from apps.inventory.warehouses.models import TransferRoute

        routes = TransferRoute.objects.filter(is_active=True).select_related(
            "source_warehouse", "destination_warehouse"
        )

        # Build adjacency: src_id → [(cost, route_obj)]
        graph = {}
        for r in routes:
            cost = float(getattr(r, metric, r.transit_days))
            graph.setdefault(r.source_warehouse_id, []).append(
                (cost, r.destination_warehouse_id, r)
            )

        # Dijkstra
        src_id = source.pk
        dst_id = destination.pk

        # (total_cost, hops, current_node, path_of_routes)
        heap = [(0, 0, src_id, [])]
        visited = set()

        while heap:
            total_cost, hops, node, path = heapq.heappop(heap)
            if node == dst_id:
                cache.set(cache_key, path, self.CACHE_TIMEOUT)
                return path
            if node in visited:
                continue
            visited.add(node)
            if hops > max_hops:
                continue
            for edge_cost, neighbor, route_obj in graph.get(node, []):
                if neighbor not in visited:
                    heapq.heappush(
                        heap,
                        (total_cost + edge_cost, hops + 1, neighbor, path + [route_obj]),
                    )

        cache.set(cache_key, "__empty__", self.CACHE_TIMEOUT)
        return []

    def calculate_route_totals(self, route_segments):
        """
        Sum transit_days and estimated_cost across a list of route segments.
        """
        from decimal import Decimal

        total_days = sum(r.transit_days for r in route_segments)
        total_cost = sum(
            (r.estimated_cost for r in route_segments), Decimal("0")
        )
        return {"transit_days": total_days, "estimated_cost": total_cost}
