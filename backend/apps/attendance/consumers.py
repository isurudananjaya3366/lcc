"""WebSocket consumers for real-time attendance dashboard updates."""

import json
import logging

logger = logging.getLogger(__name__)


try:
    from channels.generic.websocket import AsyncJsonWebsocketConsumer
except ImportError:
    # channels not installed – provide a no-op base so the module is importable
    class AsyncJsonWebsocketConsumer:  # type: ignore[no-redef]
        """Fallback stub when django-channels is not installed."""
        async def connect(self): ...  # noqa: E704
        async def disconnect(self, code): ...  # noqa: E704
        async def receive_json(self, content, **kwargs): ...  # noqa: E704
        async def send_json(self, content, close=False): ...  # noqa: E704


class AttendanceDashboardConsumer(AsyncJsonWebsocketConsumer):
    """
    WebSocket consumer that streams live attendance dashboard updates.

    Groups:
        attendance_dashboard — broadcasts check-in / check-out events to
        all connected dashboard clients.
    """

    GROUP_NAME = "attendance_dashboard"

    async def connect(self):
        await self.channel_layer.group_add(self.GROUP_NAME, self.channel_name)
        await self.accept()
        logger.info("Dashboard WS connected: %s", self.channel_name)

    async def disconnect(self, code):
        await self.channel_layer.group_discard(self.GROUP_NAME, self.channel_name)
        logger.info("Dashboard WS disconnected: %s (code=%s)", self.channel_name, code)

    async def receive_json(self, content, **kwargs):
        """Handle messages from the client (e.g. subscription filters)."""
        msg_type = content.get("type")
        if msg_type == "ping":
            await self.send_json({"type": "pong"})

    # ── Group message handlers ──────────────────────────────

    async def attendance_event(self, event):
        """Broadcast an attendance event (check-in / check-out) to the client."""
        await self.send_json({
            "type": "attendance_event",
            "data": event.get("data", {}),
        })

    async def dashboard_refresh(self, event):
        """Signal a full dashboard data refresh."""
        await self.send_json({
            "type": "dashboard_refresh",
            "data": event.get("data", {}),
        })


class EmployeeAttendanceConsumer(AsyncJsonWebsocketConsumer):
    """
    Per-employee WebSocket consumer for individual attendance status updates.

    The employee UUID is taken from the URL route (``/ws/attendance/<employee_id>/``).
    """

    async def connect(self):
        self.employee_id = self.scope["url_route"]["kwargs"]["employee_id"]
        self.group_name = f"attendance_employee_{self.employee_id}"

        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.accept()

    async def disconnect(self, code):
        await self.channel_layer.group_discard(self.group_name, self.channel_name)

    async def attendance_update(self, event):
        """Push an attendance status update to the employee's client."""
        await self.send_json({
            "type": "attendance_update",
            "data": event.get("data", {}),
        })
