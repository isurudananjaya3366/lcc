"""
ESC/POS command constants for thermal receipt printers.

Task 36: Standard ESC/POS byte sequences for text formatting,
alignment, graphics, cash drawer, and paper control.
"""

# ── Printer initialization ────────────────────────────────

ESC = b"\x1b"
GS = b"\x1d"
FS = b"\x1c"
DLE = b"\x10"

INIT = ESC + b"\x40"  # Initialize printer
RESET = ESC + b"\x40"

# ── Text formatting ───────────────────────────────────────

BOLD_ON = ESC + b"\x45\x01"
BOLD_OFF = ESC + b"\x45\x00"
UNDERLINE_ON = ESC + b"\x2d\x01"
UNDERLINE_OFF = ESC + b"\x2d\x00"
UNDERLINE_DOUBLE = ESC + b"\x2d\x02"
INVERSE_ON = GS + b"\x42\x01"
INVERSE_OFF = GS + b"\x42\x00"

# Font selection
FONT_A = ESC + b"\x4d\x00"  # Standard 12x24
FONT_B = ESC + b"\x4d\x01"  # Condensed 9x17

# Text size
TEXT_NORMAL = GS + b"\x21\x00"
TEXT_DOUBLE_HEIGHT = GS + b"\x21\x01"
TEXT_DOUBLE_WIDTH = GS + b"\x21\x10"
TEXT_DOUBLE_SIZE = GS + b"\x21\x11"  # Double height + width
TEXT_TRIPLE_HEIGHT = GS + b"\x21\x02"
TEXT_QUADRUPLE = GS + b"\x21\x33"

# ── Alignment ─────────────────────────────────────────────

ALIGN_LEFT = ESC + b"\x61\x00"
ALIGN_CENTER = ESC + b"\x61\x01"
ALIGN_RIGHT = ESC + b"\x61\x02"

# ── Line spacing ──────────────────────────────────────────

LINE_SPACING_DEFAULT = ESC + b"\x32"  # ~4.23mm
LINE_SPACING_SET = ESC + b"\x33"  # + n byte (n/180 inch)
LINE_SPACING_TIGHT = ESC + b"\x33\x10"  # 16/180
LINE_SPACING_NORMAL = ESC + b"\x33\x1e"  # 30/180
LINE_SPACING_WIDE = ESC + b"\x33\x3c"  # 60/180

# Feed
LINE_FEED = b"\x0a"
FEED_LINES = ESC + b"\x64"  # + n byte

# ── Paper cutting ─────────────────────────────────────────

CUT_FULL = GS + b"\x56\x00"
CUT_PARTIAL = GS + b"\x56\x01"
CUT_FULL_FEED = GS + b"\x56\x41\x00"   # Feed then cut
CUT_PARTIAL_FEED = GS + b"\x56\x42\x00"  # Feed then partial cut

# ── Barcode ───────────────────────────────────────────────

BARCODE_HEIGHT = GS + b"\x68"  # + n byte (height in dots)
BARCODE_WIDTH = GS + b"\x77"  # + n byte (1-6)
BARCODE_TEXT_NONE = GS + b"\x48\x00"
BARCODE_TEXT_ABOVE = GS + b"\x48\x01"
BARCODE_TEXT_BELOW = GS + b"\x48\x02"
BARCODE_TEXT_BOTH = GS + b"\x48\x03"

# Barcode types
BARCODE_UPC_A = GS + b"\x6b\x00"
BARCODE_UPC_E = GS + b"\x6b\x01"
BARCODE_EAN13 = GS + b"\x6b\x02"
BARCODE_EAN8 = GS + b"\x6b\x03"
BARCODE_CODE39 = GS + b"\x6b\x04"
BARCODE_CODE128 = GS + b"\x6b\x49"
BARCODE_ITF = GS + b"\x6b\x05"

# ── QR Code ───────────────────────────────────────────────

QR_MODEL_1 = GS + b"\x28\x6b\x04\x00\x31\x41\x31\x00"
QR_MODEL_2 = GS + b"\x28\x6b\x04\x00\x31\x41\x32\x00"
QR_ERR_L = GS + b"\x28\x6b\x03\x00\x31\x45\x30"
QR_ERR_M = GS + b"\x28\x6b\x03\x00\x31\x45\x31"
QR_ERR_Q = GS + b"\x28\x6b\x03\x00\x31\x45\x32"
QR_ERR_H = GS + b"\x28\x6b\x03\x00\x31\x45\x33"

def qr_size_cmd(size=6):
    """QR module size (1-16, default 6)."""
    return GS + b"\x28\x6b\x03\x00\x31\x43" + bytes([size])


def qr_store_data(data: str):
    """Store QR code data in printer buffer."""
    encoded = data.encode("utf-8")
    length = len(encoded) + 3
    pl = length % 256
    ph = length // 256
    return GS + b"\x28\x6b" + bytes([pl, ph]) + b"\x31\x50\x30" + encoded


QR_PRINT = GS + b"\x28\x6b\x03\x00\x31\x51\x30"

# ── Cash drawer ───────────────────────────────────────────

CASH_DRAWER_PIN2 = ESC + b"\x70\x00\x19\x78"  # Pin 2, 25ms on, 120ms off
CASH_DRAWER_PIN5 = ESC + b"\x70\x01\x19\x78"  # Pin 5, 25ms on, 120ms off

# ── Raster graphics ──────────────────────────────────────

RASTER_BIT_IMAGE = GS + b"\x76\x30"

# ── Character set ─────────────────────────────────────────

CHARSET_PC437 = ESC + b"\x74\x00"  # USA
CHARSET_PC850 = ESC + b"\x74\x02"  # Multilingual
CHARSET_WPC1252 = ESC + b"\x74\x10"  # Windows Latin-1
CHARSET_UTF8 = ESC + b"\x74\x30"

# ── Paper width constants ─────────────────────────────────

CHARS_PER_LINE_80MM = 48  # Standard 80mm, Font A
CHARS_PER_LINE_58MM = 32  # Standard 58mm, Font A
CHARS_PER_LINE_80MM_FONT_B = 64
CHARS_PER_LINE_58MM_FONT_B = 42

# ── Status commands ───────────────────────────────────────

STATUS_ONLINE = DLE + b"\x04\x01"
STATUS_OFFLINE = DLE + b"\x04\x02"
STATUS_ERROR = DLE + b"\x04\x03"
STATUS_PAPER = DLE + b"\x04\x04"
