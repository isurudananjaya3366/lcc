"""
Task 80: Thermal Printer Tests.

Tests for ESC/POS constants, ThermalPrinterService, layout formatters,
ThermalPrintRenderer, and print connectivity.
"""

import pytest

from apps.pos.receipts.services.escpos_constants import (
    ALIGN_CENTER,
    ALIGN_LEFT,
    ALIGN_RIGHT,
    BOLD_OFF,
    BOLD_ON,
    CHARS_PER_LINE_58MM,
    CHARS_PER_LINE_80MM,
    CUT_FULL,
    CUT_PARTIAL,
    INIT,
    UNDERLINE_OFF,
    UNDERLINE_ON,
)
from apps.pos.receipts.services.thermal_printer import ThermalPrinterService
from apps.pos.receipts.services.thermal_renderer import (
    Layout58mm,
    Layout80mm,
    ThermalPrintRenderer,
)


# ── ESC/POS Constants ─────────────────────────────────────────


class TestESCPOSConstants:
    """Verify ESC/POS byte constants."""

    def test_init_command(self):
        assert INIT == b"\x1b\x40"

    def test_bold_commands(self):
        assert BOLD_ON == b"\x1b\x45\x01"
        assert BOLD_OFF == b"\x1b\x45\x00"

    def test_underline_commands(self):
        assert UNDERLINE_ON == b"\x1b\x2d\x01"
        assert UNDERLINE_OFF == b"\x1b\x2d\x00"

    def test_alignment_commands(self):
        assert ALIGN_LEFT == b"\x1b\x61\x00"
        assert ALIGN_CENTER == b"\x1b\x61\x01"
        assert ALIGN_RIGHT == b"\x1b\x61\x02"

    def test_cut_commands(self):
        assert CUT_FULL == b"\x1d\x56\x00"
        assert CUT_PARTIAL == b"\x1d\x56\x01"

    def test_paper_width_constants(self):
        assert CHARS_PER_LINE_80MM == 48
        assert CHARS_PER_LINE_58MM == 32


# ── ThermalPrinterService ─────────────────────────────────────


class TestThermalPrinterService:
    """Test low-level thermal printer command generation."""

    def test_initialize(self):
        printer = ThermalPrinterService()
        printer.initialize()
        data = printer.get_buffer()
        assert INIT in data

    def test_text_output(self):
        printer = ThermalPrinterService()
        printer.initialize()
        printer.text("Hello World")
        data = printer.get_buffer()
        assert b"Hello World" in data

    def test_bold_text(self):
        printer = ThermalPrinterService()
        printer.initialize()
        printer.text("Bold Text", bold=True)
        data = printer.get_buffer()
        assert BOLD_ON in data
        assert b"Bold Text" in data
        assert BOLD_OFF in data

    def test_underline_text(self):
        printer = ThermalPrinterService()
        printer.initialize()
        printer.text("Underlined", underline=True)
        data = printer.get_buffer()
        assert UNDERLINE_ON in data
        assert b"Underlined" in data

    def test_alignment(self):
        printer = ThermalPrinterService()
        printer.initialize()
        printer.align("center")
        data = printer.get_buffer()
        assert ALIGN_CENTER in data

    def test_align_left(self):
        printer = ThermalPrinterService()
        printer.initialize()
        printer.align_left()
        data = printer.get_buffer()
        assert ALIGN_LEFT in data

    def test_align_right(self):
        printer = ThermalPrinterService()
        printer.initialize()
        printer.align_right()
        data = printer.get_buffer()
        assert ALIGN_RIGHT in data

    def test_feed(self):
        printer = ThermalPrinterService()
        printer.initialize()
        printer.feed(3)
        data = printer.get_buffer()
        # Feed generates line feed bytes
        assert len(data) > len(INIT)

    def test_cut_full(self):
        printer = ThermalPrinterService()
        printer.initialize()
        printer.cut(mode="full")
        data = printer.get_buffer()
        assert CUT_FULL in data

    def test_cut_partial(self):
        printer = ThermalPrinterService()
        printer.initialize()
        printer.cut(mode="partial")
        data = printer.get_buffer()
        assert CUT_PARTIAL in data

    def test_get_buffer_returns_bytes(self):
        printer = ThermalPrinterService()
        printer.initialize()
        printer.text("Test")
        data = printer.get_buffer()
        assert isinstance(data, bytes)

    def test_barcode(self):
        printer = ThermalPrinterService()
        printer.initialize()
        printer.barcode("8901234567890", barcode_type="EAN13")
        data = printer.get_buffer()
        assert b"8901234567890" in data


# ── Layout Formatters ─────────────────────────────────────────


class TestLayout80mm:
    """Test 80mm layout formatting (48 chars per line)."""

    def test_width(self):
        layout = Layout80mm()
        assert layout.width == 48

    def test_left_right(self):
        layout = Layout80mm()
        result = layout.left_right("Item Name", "Rs. 150.00")
        assert len(result) == 48
        assert result.startswith("Item Name")
        assert result.endswith("Rs. 150.00")

    def test_center(self):
        layout = Layout80mm()
        result = layout.center("Header")
        assert len(result) == 48
        # "Header" is centered in 48-char line
        assert "Header" in result

    def test_separator(self):
        layout = Layout80mm()
        result = layout.separator()
        assert len(result) == 48

    def test_double_separator(self):
        layout = Layout80mm()
        result = layout.double_separator()
        assert len(result) == 48
        assert "=" in result

    def test_three_columns(self):
        layout = Layout80mm()
        result = layout.three_columns("Name", "Qty", "Total")
        assert len(result) == 48
        assert "Name" in result
        assert "Total" in result

    def test_wrap_text(self):
        layout = Layout80mm()
        long_text = "A" * 100
        lines = layout.wrap_text(long_text)
        assert len(lines) >= 2
        for line in lines:
            assert len(line) <= 48


class TestLayout58mm:
    """Test 58mm layout formatting (32 chars per line)."""

    def test_width(self):
        layout = Layout58mm()
        assert layout.width == 32

    def test_left_right(self):
        layout = Layout58mm()
        result = layout.left_right("Item", "Rs. 150.00")
        assert len(result) == 32
        assert result.startswith("Item")
        assert result.endswith("Rs. 150.00")

    def test_center(self):
        layout = Layout58mm()
        result = layout.center("Header")
        assert len(result) == 32

    def test_separator(self):
        layout = Layout58mm()
        result = layout.separator()
        assert len(result) == 32

    def test_long_name_truncation(self):
        layout = Layout58mm()
        # Name too long for 32 chars with price
        result = layout.left_right("A Very Long Product Name Here", "Rs. 150.00")
        assert len(result) == 32


# ── ThermalPrintRenderer ──────────────────────────────────────


class TestThermalPrintRenderer:
    """Test the high-level receipt renderer."""

    def test_render_returns_bytes(self, sample_receipt_data):
        renderer = ThermalPrintRenderer(
            receipt_data=sample_receipt_data, paper_width=80
        )
        result = renderer.render()
        assert isinstance(result, bytes)

    def test_render_contains_init(self, sample_receipt_data):
        renderer = ThermalPrintRenderer(
            receipt_data=sample_receipt_data, paper_width=80
        )
        result = renderer.render()
        assert INIT in result

    def test_render_contains_item_names(self, sample_receipt_data):
        renderer = ThermalPrintRenderer(
            receipt_data=sample_receipt_data, paper_width=80
        )
        result = renderer.render()
        assert b"Coca Cola 330ml" in result

    def test_render_contains_totals(self, sample_receipt_data):
        renderer = ThermalPrintRenderer(
            receipt_data=sample_receipt_data, paper_width=80
        )
        result = renderer.render()
        assert b"500.00" in result

    def test_render_58mm(self, sample_receipt_data):
        renderer = ThermalPrintRenderer(
            receipt_data=sample_receipt_data, paper_width=58
        )
        result = renderer.render()
        assert isinstance(result, bytes)
        assert len(result) > 0

    def test_render_with_cash_drawer(self, sample_receipt_data):
        renderer = ThermalPrintRenderer(
            receipt_data=sample_receipt_data,
            paper_width=80,
            open_drawer=True,
        )
        result = renderer.render()
        assert isinstance(result, bytes)

    def test_render_with_auto_cut(self, sample_receipt_data):
        renderer = ThermalPrintRenderer(
            receipt_data=sample_receipt_data,
            paper_width=80,
            auto_cut=True,
        )
        result = renderer.render()
        # Cut command should be present
        assert CUT_FULL in result or CUT_PARTIAL in result

    def test_render_empty_items(self, sample_receipt_data):
        """Renderer handles empty items gracefully."""
        sample_receipt_data["items"] = []
        renderer = ThermalPrintRenderer(
            receipt_data=sample_receipt_data, paper_width=80
        )
        result = renderer.render()
        assert isinstance(result, bytes)

    def test_render_missing_sections(self):
        """Renderer handles minimal data."""
        minimal_data = {
            "header": {"business_name": "Test"},
            "items": [],
            "totals": {"grand_total": "Rs. 0.00"},
            "payments": [],
        }
        renderer = ThermalPrintRenderer(
            receipt_data=minimal_data, paper_width=80
        )
        result = renderer.render()
        assert isinstance(result, bytes)


# ── Print Connectivity ────────────────────────────────────────


class TestPrintConnectivity:
    """Test printer connection classes."""

    def test_network_printer_init(self):
        from apps.pos.receipts.services.print_connectivity import (
            NetworkPrinter,
        )

        printer = NetworkPrinter(host="192.168.1.100", port=9100)
        assert printer.host == "192.168.1.100"
        assert printer.port == 9100

    def test_usb_printer_stub_raises(self):
        from apps.pos.receipts.services.print_connectivity import (
            PrinterConnectionError,
            USBPrinterStub,
        )

        printer = USBPrinterStub()
        with pytest.raises(PrinterConnectionError):
            printer.send(b"test")


# ── Print Queue ───────────────────────────────────────────────


class TestPrintQueue:
    """Test print queue management."""

    def test_enqueue_job(self):
        from apps.pos.receipts.services.print_queue import (
            PrintJob,
            PrintQueue,
        )

        queue = PrintQueue()
        job = PrintJob(
            receipt_id="test-id",
            data=b"test data",
            printer_host="192.168.1.100",
        )
        job_id = queue.enqueue(job)
        assert isinstance(job_id, str)
        assert job.status == "pending"

    def test_dequeue_returns_highest_priority(self):
        from apps.pos.receipts.services.print_queue import (
            PrintJob,
            PrintPriority,
            PrintQueue,
        )

        queue = PrintQueue()
        queue.enqueue(PrintJob(
            receipt_id="low",
            data=b"low",
            priority=PrintPriority.LOW,
            printer_host="192.168.1.100",
        ))
        queue.enqueue(PrintJob(
            receipt_id="high",
            data=b"high",
            priority=PrintPriority.HIGH,
            printer_host="192.168.1.100",
        ))
        job = queue.dequeue()
        assert job is not None
        assert job.receipt_id == "high"

    def test_cancel_job(self):
        from apps.pos.receipts.services.print_queue import (
            PrintJob,
            PrintQueue,
        )

        queue = PrintQueue()
        job = PrintJob(
            receipt_id="cancel-me",
            data=b"data",
            printer_host="192.168.1.100",
        )
        queue.enqueue(job)
        result = queue.cancel(job.job_id)
        assert result is True
        assert job.status == "cancelled"

    def test_get_job(self):
        from apps.pos.receipts.services.print_queue import (
            PrintJob,
            PrintQueue,
        )

        queue = PrintQueue()
        job = PrintJob(
            receipt_id="findme",
            data=b"data",
            printer_host="192.168.1.100",
        )
        queue.enqueue(job)
        found = queue.get_job(job.job_id)
        assert found is not None
        assert found.receipt_id == "findme"
