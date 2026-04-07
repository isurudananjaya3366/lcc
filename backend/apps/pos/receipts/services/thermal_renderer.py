"""
Thermal receipt renderer — builds complete ESC/POS output from receipt data.

Tasks 43-48: QR code, layout formatters (80mm/58mm), separator lines,
cash drawer, and the ThermalPrintRenderer orchestrator.
"""

import logging

from apps.pos.receipts.services import escpos_constants as ESC
from apps.pos.receipts.services.thermal_printer import ThermalPrinterService

logger = logging.getLogger(__name__)


class LayoutFormatter:
    """
    Formats text columns for a given line width.
    Used by both 80mm (48 chars) and 58mm (32 chars) layouts.
    """

    def __init__(self, chars_per_line: int):
        self.width = chars_per_line

    def left_right(self, left: str, right: str) -> str:
        """Two-column: text left, value right."""
        gap = self.width - len(left) - len(right)
        if gap < 1:
            left = left[: self.width - len(right) - 1]
            gap = 1
        return left + " " * gap + right

    def three_columns(self, col1: str, col2: str, col3: str,
                      widths: tuple[int, int, int] | None = None) -> str:
        """Three-column layout for item lines."""
        if widths is None:
            w1 = self.width // 2
            w3 = max(10, self.width // 4)
            w2 = self.width - w1 - w3
        else:
            w1, w2, w3 = widths

        c1 = col1[:w1].ljust(w1)
        c2 = col2[:w2].rjust(w2)
        c3 = col3[:w3].rjust(w3)
        return c1 + c2 + c3

    def center(self, text: str) -> str:
        return text[:self.width].center(self.width)

    def separator(self, char="-") -> str:
        return char * self.width

    def double_separator(self) -> str:
        return "=" * self.width

    def dotted_separator(self) -> str:
        return "." * self.width

    def blank_line(self) -> str:
        return ""

    def wrap_text(self, text: str) -> list[str]:
        """Word-wrap text to fit line width."""
        words = text.split()
        lines: list[str] = []
        current = ""
        for word in words:
            # Handle words longer than line width — hard break
            while len(word) > self.width:
                if current:
                    lines.append(current)
                    current = ""
                lines.append(word[: self.width])
                word = word[self.width :]
            if not word:
                continue
            if current and len(current) + 1 + len(word) > self.width:
                lines.append(current)
                current = word
            else:
                current = f"{current} {word}".strip() if current else word
        if current:
            lines.append(current)
        return lines


class Layout80mm(LayoutFormatter):
    """80mm paper layout — 48 characters per line (Font A)."""

    def __init__(self):
        super().__init__(ESC.CHARS_PER_LINE_80MM)


class Layout58mm(LayoutFormatter):
    """58mm paper layout — 32 characters per line (Font A)."""

    def __init__(self):
        super().__init__(ESC.CHARS_PER_LINE_58MM)


class ThermalPrintRenderer:
    """
    Renders full receipt from receipt_data dict to ESC/POS bytes.

    Orchestrates the ThermalPrinterService and LayoutFormatter
    to produce a complete printable thermal receipt.

    Usage::

        renderer = ThermalPrintRenderer(receipt_data, paper_width=80)
        raw_bytes = renderer.render()
    """

    def __init__(self, receipt_data: dict, paper_width: int = 80,
                 open_drawer: bool = False, auto_cut: bool = True):
        self.data = receipt_data
        self.paper_width = paper_width
        self.open_drawer = open_drawer
        self.auto_cut = auto_cut
        self.printer = ThermalPrinterService(paper_width=paper_width)
        self.layout = Layout80mm() if paper_width == 80 else Layout58mm()

    def render(self) -> bytes:
        """Build complete receipt bytes."""
        self.printer.initialize()

        if self.open_drawer:
            self._open_cash_drawer()

        self._render_header()
        self._print_separator()
        self._render_transaction()
        self._print_separator()
        self._render_items()
        self._print_separator()
        self._render_totals()
        self._print_double_separator()
        self._render_payments()
        self._print_separator()
        self._render_footer()
        self._render_qr_code()

        if self.auto_cut:
            self.printer.cut()

        return self.printer.get_buffer()

    # ── Section renderers ─────────────────────────────────

    def _render_header(self):
        header = self.data.get("header", {})
        name = header.get("business_name", "")
        if name:
            self.printer.text(name, bold=True, double_height=True,
                              align="center")

        # Custom lines
        for line in header.get("custom_lines", []):
            self.printer.text(line, align="center")

        self.printer.feed(1)

    def _render_transaction(self):
        txn = self.data.get("transaction", {})
        p = self.printer

        receipt_num = txn.get("receipt_number", "")
        if receipt_num:
            p.text(self.layout.left_right("Receipt #:", receipt_num))

        date_disp = txn.get("date_display", "")
        time_disp = txn.get("time_display", "")
        if date_disp:
            p.text(self.layout.left_right("Date:", date_disp))
        if time_disp:
            p.text(self.layout.left_right("Time:", time_disp))

        cashier = txn.get("cashier_name", "")
        if cashier:
            p.text(self.layout.left_right("Cashier:", cashier))

        terminal = txn.get("terminal_name") or txn.get("terminal_id", "")
        if terminal:
            p.text(self.layout.left_right("Terminal:", terminal))

        order = txn.get("order_number", "")
        if order:
            p.text(self.layout.left_right("Order #:", order))

    def _render_items(self):
        items = self.data.get("items", [])
        p = self.printer

        # Item header
        p.text(self.layout.three_columns("Item", "Qty", "Total"),
               bold=True)
        p.text(self.layout.separator("-"))

        for item in items:
            name = item.get("name", "")
            qty_disp = item.get("quantity_display", "1")
            total_disp = item.get("line_total_display", "0.00")

            p.text(self.layout.three_columns(name, qty_disp, total_disp))

            # Variant info
            variant = item.get("variant_display")
            if variant:
                p.text(f"  {variant}")

            # Discount
            discount_disp = item.get("discount_display")
            if discount_disp:
                p.text(self.layout.left_right("  Discount:", f"-{discount_disp}"))

    def _render_totals(self):
        totals = self.data.get("totals", {})
        p = self.printer

        sub = totals.get("subtotal_display", "")
        if sub:
            p.text(self.layout.left_right("Subtotal:", sub))

        disc = totals.get("discount_display", "")
        discount_val = totals.get("discount_total", 0)
        if disc and discount_val and str(discount_val) not in ("0", "0.00", "Rs. 0.00"):
            p.text(self.layout.left_right("Discount:", f"-{disc}"))

        # Tax breakdown
        for tax in totals.get("tax_breakdown", []):
            name = tax.get("tax_name", "Tax")
            rate = tax.get("tax_rate_display", "")
            amt = tax.get("tax_amount_display", "")
            label = f"{name} ({rate})" if rate else name
            p.text(self.layout.left_right(label, amt))

        # Grand total
        grand = totals.get("grand_total_display", "")
        if grand:
            p.text("")
            p.text(
                self.layout.left_right("TOTAL:", grand),
                bold=True, double_height=True,
            )

    def _render_payments(self):
        pay_section = self.data.get("payments", {})
        if isinstance(pay_section, list):
            payments = pay_section
            change_disp = None
        else:
            payments = pay_section.get("payments", [])
            change_disp = pay_section.get("change_due_display")
        p = self.printer

        for pay in payments:
            method = pay.get("method_display", pay.get("method", ""))
            amount = pay.get("amount_display", "")
            p.text(self.layout.left_right(method, amount))

            ref = pay.get("reference")
            if ref:
                p.text(f"  Ref: {ref}")

        if change_disp:
            p.text(self.layout.left_right("Change:", change_disp), bold=True)

    def _render_footer(self):
        footer = self.data.get("footer", {})
        p = self.printer

        p.feed(1)
        for line in footer.get("custom_lines", []):
            p.text(line, align="center")

        policy = footer.get("return_policy")
        if policy:
            p.feed(1)
            for wrapped in self.layout.wrap_text(policy):
                p.text(wrapped, align="center")

        note = footer.get("footer_note")
        if note:
            p.feed(1)
            p.text(note, align="center")

        p.feed(1)

    # ── Task 43: QR code ─────────────────────────────────

    def _render_qr_code(self):
        qr = self.data.get("qr_code", {})
        qr_data = qr.get("data")
        if not qr_data:
            return

        p = self.printer
        p.align_center()

        # Set QR model 2
        p.write(ESC.QR_MODEL_2)

        # Size
        size_map = {"small": 4, "medium": 6, "large": 8}
        module_size = size_map.get(qr.get("size", "medium"), 6)
        p.write(ESC.qr_size_cmd(module_size))

        # Error correction
        ec_map = {"L": ESC.QR_ERR_L, "M": ESC.QR_ERR_M,
                  "Q": ESC.QR_ERR_Q, "H": ESC.QR_ERR_H}
        p.write(ec_map.get(qr.get("error_correction", "M"), ESC.QR_ERR_M))

        # Store and print
        p.write(ESC.qr_store_data(qr_data))
        p.write(ESC.QR_PRINT)

        display_text = qr.get("display_text")
        if display_text:
            p.feed(1)
            p.text(display_text, align="center")

        p.align_left()

    # ── Task 46: Separator helpers ────────────────────────

    def _print_separator(self, char="-"):
        self.printer.text(self.layout.separator(char))

    def _print_double_separator(self):
        self.printer.text(self.layout.double_separator())

    def _print_dotted_separator(self):
        self.printer.text(self.layout.dotted_separator())

    # ── Task 47: Cash drawer ─────────────────────────────

    def _open_cash_drawer(self, pin=2):
        if pin == 5:
            self.printer.write(ESC.CASH_DRAWER_PIN5)
        else:
            self.printer.write(ESC.CASH_DRAWER_PIN2)
