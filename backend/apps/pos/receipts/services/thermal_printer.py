"""
Thermal printer service — ESC/POS byte-stream builder.

Tasks 35, 37-42: Buffer management, text formatting, alignment,
line spacing, paper cutting, logo printing, and barcode generation.
"""

import logging
import struct
from io import BytesIO

from apps.pos.receipts.services import escpos_constants as ESC

logger = logging.getLogger(__name__)


class ThermalPrinterService:
    """
    Builds an ESC/POS byte buffer for thermal receipt printers.

    Usage::

        svc = ThermalPrinterService(paper_width=80)
        svc.initialize()
        svc.text("Hello World", bold=True, align="center")
        svc.feed(2)
        svc.cut()
        raw = svc.get_buffer()
    """

    PAPER_CONFIGS = {
        80: {
            "chars_per_line": ESC.CHARS_PER_LINE_80MM,
            "chars_font_b": ESC.CHARS_PER_LINE_80MM_FONT_B,
            "dots_per_line": 576,
        },
        58: {
            "chars_per_line": ESC.CHARS_PER_LINE_58MM,
            "chars_font_b": ESC.CHARS_PER_LINE_58MM_FONT_B,
            "dots_per_line": 384,
        },
    }

    def __init__(self, paper_width=80):
        if paper_width not in self.PAPER_CONFIGS:
            raise ValueError(f"Unsupported paper width: {paper_width}mm")
        self._buffer = BytesIO()
        self.paper_width = paper_width
        self._config = self.PAPER_CONFIGS[paper_width]
        self.chars_per_line = self._config["chars_per_line"]

    # ── Buffer management ─────────────────────────────────

    def write(self, data: bytes):
        self._buffer.write(data)
        return self

    def get_buffer(self) -> bytes:
        return self._buffer.getvalue()

    def reset_buffer(self):
        self._buffer = BytesIO()
        return self

    # ── Task 35: Initialization ───────────────────────────

    def initialize(self):
        self.write(ESC.INIT)
        self.write(ESC.CHARSET_WPC1252)
        return self

    # ── Task 37: Text formatting ──────────────────────────

    def text(self, content: str, bold=False, underline=False,
             double_height=False, double_width=False,
             font="A", align=None):
        if align:
            self.align(align)

        # Font
        self.write(ESC.FONT_A if font == "A" else ESC.FONT_B)

        # Size
        if double_height and double_width:
            self.write(ESC.TEXT_DOUBLE_SIZE)
        elif double_height:
            self.write(ESC.TEXT_DOUBLE_HEIGHT)
        elif double_width:
            self.write(ESC.TEXT_DOUBLE_WIDTH)
        else:
            self.write(ESC.TEXT_NORMAL)

        if bold:
            self.write(ESC.BOLD_ON)
        if underline:
            self.write(ESC.UNDERLINE_ON)

        self.write(content.encode("cp1252", errors="replace"))
        self.write(ESC.LINE_FEED)

        # Reset formatting
        if bold:
            self.write(ESC.BOLD_OFF)
        if underline:
            self.write(ESC.UNDERLINE_OFF)
        self.write(ESC.TEXT_NORMAL)

        return self

    def text_line(self, content: str, **kwargs):
        """Write text truncated/padded to line width."""
        return self.text(content[:self.chars_per_line], **kwargs)

    # ── Task 38: Alignment ────────────────────────────────

    def align(self, alignment: str):
        mapping = {
            "left": ESC.ALIGN_LEFT,
            "center": ESC.ALIGN_CENTER,
            "right": ESC.ALIGN_RIGHT,
        }
        cmd = mapping.get(alignment.lower(), ESC.ALIGN_LEFT)
        self.write(cmd)
        return self

    def align_left(self):
        return self.align("left")

    def align_center(self):
        return self.align("center")

    def align_right(self):
        return self.align("right")

    # ── Task 39: Line spacing ─────────────────────────────

    def line_spacing(self, mode="default", value=None):
        if value is not None:
            self.write(ESC.LINE_SPACING_SET + bytes([value]))
        elif mode == "tight":
            self.write(ESC.LINE_SPACING_TIGHT)
        elif mode == "wide":
            self.write(ESC.LINE_SPACING_WIDE)
        else:
            self.write(ESC.LINE_SPACING_DEFAULT)
        return self

    def feed(self, lines=1):
        self.write(ESC.FEED_LINES + bytes([lines]))
        return self

    # ── Task 40: Paper cutting ────────────────────────────

    def cut(self, mode="partial", feed_before=3):
        if feed_before:
            self.feed(feed_before)
        if mode == "full":
            self.write(ESC.CUT_FULL)
        else:
            self.write(ESC.CUT_PARTIAL)
        return self

    # ── Task 41: Logo (raster image) ─────────────────────

    def logo(self, image_data: bytes, width: int):
        """
        Print a raster bit-image.

        Args:
            image_data: 1-bit-per-pixel packed bytes (MSB first).
            width: pixel width (must be ≤ dots_per_line).
        """
        max_dots = self._config["dots_per_line"]
        if width > max_dots:
            width = max_dots

        byte_width = (width + 7) // 8
        height = len(image_data) // byte_width if byte_width else 0
        if height == 0:
            return self

        self.align_center()
        # GS v 0 — raster bit-image: mode 0 (normal)
        self.write(ESC.RASTER_BIT_IMAGE + b"\x00")
        self.write(struct.pack("<HH", byte_width, height))
        self.write(image_data[:byte_width * height])
        self.align_left()
        return self

    def logo_from_pil(self, pil_image, max_width=None):
        """Convert a PIL Image to 1-bit raster and print."""
        try:
            max_w = max_width or self._config["dots_per_line"]
            if pil_image.width > max_w:
                ratio = max_w / pil_image.width
                new_h = int(pil_image.height * ratio)
                pil_image = pil_image.resize((max_w, new_h))

            mono = pil_image.convert("1")
            pixels = mono.tobytes()
            self.logo(pixels, mono.width)
        except Exception:
            logger.warning("Failed to print logo image", exc_info=True)
        return self

    # ── Task 42: Barcode printing ─────────────────────────

    BARCODE_TYPES = {
        "UPC-A": ESC.BARCODE_UPC_A,
        "UPC-E": ESC.BARCODE_UPC_E,
        "EAN13": ESC.BARCODE_EAN13,
        "EAN8": ESC.BARCODE_EAN8,
        "CODE39": ESC.BARCODE_CODE39,
        "CODE128": ESC.BARCODE_CODE128,
        "ITF": ESC.BARCODE_ITF,
    }

    def barcode(self, data: str, barcode_type="CODE128",
                height=80, width=3, text_position="below"):
        # Height
        self.write(ESC.BARCODE_HEIGHT + bytes([min(height, 255)]))
        # Width (module size 1-6)
        self.write(ESC.BARCODE_WIDTH + bytes([max(1, min(width, 6))]))
        # HRI text position
        pos_map = {
            "none": ESC.BARCODE_TEXT_NONE,
            "above": ESC.BARCODE_TEXT_ABOVE,
            "below": ESC.BARCODE_TEXT_BELOW,
            "both": ESC.BARCODE_TEXT_BOTH,
        }
        self.write(pos_map.get(text_position, ESC.BARCODE_TEXT_BELOW))

        # Print barcode
        cmd = self.BARCODE_TYPES.get(barcode_type.upper(), ESC.BARCODE_CODE128)
        encoded = data.encode("ascii", errors="replace")
        self.write(cmd + bytes([len(encoded)]) + encoded)
        return self

    # ── Utility ───────────────────────────────────────────

    def raw(self, data: bytes):
        """Write raw bytes."""
        self.write(data)
        return self

    def newline(self):
        self.write(ESC.LINE_FEED)
        return self

    def finalize(self) -> bytes:
        """Finalize buffer: reset printer state and return bytes."""
        self.write(ESC.TEXT_NORMAL)
        self.write(ESC.ALIGN_LEFT)
        self.write(ESC.BOLD_OFF)
        self.write(ESC.UNDERLINE_OFF)
        self.feed(3)
        return self.get_buffer()

    def print_bold(self, content: str, **kwargs):
        """Convenience: print text in bold."""
        return self.text(content, bold=True, **kwargs)

    def print_underline(self, content: str, **kwargs):
        """Convenience: print text with underline."""
        return self.text(content, underline=True, **kwargs)

    def set_bold(self, enabled: bool = True):
        """Toggle bold mode."""
        self.write(ESC.BOLD_ON if enabled else ESC.BOLD_OFF)
        return self

    def set_underline(self, mode: int = 1):
        """Set underline mode (0=off, 1=single, 2=double)."""
        if mode == 2:
            self.write(ESC.UNDERLINE_DOUBLE)
        elif mode == 1:
            self.write(ESC.UNDERLINE_ON)
        else:
            self.write(ESC.UNDERLINE_OFF)
        return self
