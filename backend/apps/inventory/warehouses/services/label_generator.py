"""
Label and QR-code generator for storage location barcodes.

Generates printable barcode labels (Code 128) and QR codes in PNG/PDF
formats, including bulk PDF output for Avery-style label sheets.
"""

import json
import logging
from io import BytesIO

logger = logging.getLogger(__name__)

# Label size templates in pixels (at 72 DPI ≈ points)
LABEL_SIZES = {
    "2x1": (144, 72),
    "4x2": (288, 144),
    "4x6": (288, 432),
}

# Avery template layout specs (all dimensions in points, 72 pt = 1 inch)
TEMPLATE_SPECS = {
    "avery_5160": {
        "width": 189,       # 2 5/8″
        "height": 72,       # 1″
        "cols": 3,
        "rows": 10,
        "labels_per_page": 30,
        "margin_left": 14,
        "margin_top": 756,  # start near top (letter = 792pt)
        "gutter_x": 9,
        "gutter_y": 0,
    },
    "avery_5163": {
        "width": 288,       # 4″
        "height": 144,      # 2″
        "cols": 2,
        "rows": 5,
        "labels_per_page": 10,
        "margin_left": 12,
        "margin_top": 756,
        "gutter_x": 18,
        "gutter_y": 0,
    },
}


class LabelGenerator:
    """Generate printable barcode / QR-code labels for storage locations."""

    # ── single-label generation ───────────────────────────────────────

    def generate_label(self, location, label_size="4x2", fmt="png"):
        """
        Generate a barcode label image for *location*.

        Returns a ``PIL.Image`` (for png/jpg) or ``bytes`` (for pdf).
        """
        from PIL import Image, ImageDraw, ImageFont

        width, height = LABEL_SIZES.get(label_size, LABEL_SIZES["4x2"])
        label = Image.new("RGB", (width, height), color="white")
        draw = ImageDraw.Draw(label)

        try:
            font = ImageFont.load_default()
        except Exception:
            font = None

        # Header: warehouse name
        draw.text((10, 5), str(location.warehouse.name), fill="black", font=font)

        # Location code prominently
        draw.text(
            (10, 20),
            f"Location: {location.code}",
            fill="black",
            font=font,
        )

        # Barcode image (Code 128) via python-barcode if available
        barcode_img = self._generate_barcode_image(location.barcode)
        if barcode_img:
            barcode_resized = barcode_img.resize((width - 20, max(height - 60, 20)))
            label.paste(barcode_resized, (10, 40))

        # Human-readable barcode text at bottom
        draw.text((10, height - 15), str(location.barcode or ""), fill="black", font=font)

        if fmt == "pdf":
            return self._image_to_pdf_bytes(label)
        return label

    # ── QR code ───────────────────────────────────────────────────────

    def generate_qr_code(self, location):
        """
        Generate a QR code image encoding location metadata as JSON.

        Returns a ``PIL.Image`` or None if qrcode is not installed.
        """
        try:
            import qrcode
        except ImportError:
            logger.warning("qrcode package not installed – skipping QR generation")
            return None

        qr_data = {
            "type": "location",
            "location_id": str(location.id),
            "code": location.code,
            "warehouse_code": location.warehouse.code,
            "barcode": location.barcode or "",
            "path": location.location_path,
        }

        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_M,
            box_size=10,
            border=4,
        )
        qr.add_data(json.dumps(qr_data))
        qr.make(fit=True)
        return qr.make_image(fill_color="black", back_color="white")

    def generate_combined_label(self, location, label_size="4x6"):
        """Label with both a Code 128 barcode **and** a QR code side-by-side."""
        from PIL import Image, ImageDraw, ImageFont

        width, height = LABEL_SIZES.get(label_size, LABEL_SIZES["4x6"])
        label = Image.new("RGB", (width, height), color="white")
        draw = ImageDraw.Draw(label)

        try:
            font = ImageFont.load_default()
        except Exception:
            font = None

        draw.text((10, 5), str(location.warehouse.name), fill="black", font=font)
        draw.text((10, 20), f"Location: {location.code}", fill="black", font=font)

        barcode_img = self._generate_barcode_image(location.barcode)
        if barcode_img:
            bw = width - 120
            bh = max(height - 60, 20)
            label.paste(barcode_img.resize((bw, bh)), (10, 40))

        qr_img = self.generate_qr_code(location)
        if qr_img:
            qr_size = min(100, height - 40)
            label.paste(qr_img.resize((qr_size, qr_size)), (width - qr_size - 10, 40))

        draw.text((10, height - 15), str(location.barcode or ""), fill="black", font=font)
        return label

    # ── bulk PDF ──────────────────────────────────────────────────────

    def bulk_generate_labels(self, locations, template="avery_5163", output_file=None):
        """
        Generate a multi-page PDF with barcode labels laid out on Avery sheets.

        Returns PDF ``bytes`` (or writes to *output_file* if given).
        """
        try:
            from reportlab.lib.pagesizes import letter
            from reportlab.lib.utils import ImageReader
            from reportlab.pdfgen import canvas
        except ImportError:
            logger.error("reportlab is required for bulk PDF generation")
            raise

        specs = TEMPLATE_SPECS.get(template, TEMPLATE_SPECS["avery_5163"])

        pdf_buffer = BytesIO()
        c = canvas.Canvas(pdf_buffer, pagesize=letter)

        col = 0
        row = 0

        for location in locations:
            x = specs["margin_left"] + col * (specs["width"] + specs["gutter_x"])
            y = specs["margin_top"] - row * (specs["height"] + specs["gutter_y"])

            # Draw label content
            img = self.generate_label(location, label_size="4x2")
            img_buf = BytesIO()
            img.save(img_buf, format="PNG")
            img_buf.seek(0)
            c.drawImage(
                ImageReader(img_buf),
                x,
                y - specs["height"],
                width=specs["width"],
                height=specs["height"],
            )

            col += 1
            if col >= specs["cols"]:
                col = 0
                row += 1
            if row >= specs["rows"]:
                c.showPage()
                col = 0
                row = 0

        c.save()
        pdf_buffer.seek(0)
        pdf_bytes = pdf_buffer.getvalue()

        if output_file:
            with open(output_file, "wb") as f:
                f.write(pdf_bytes)
            return output_file

        return pdf_bytes

    # ── private helpers ───────────────────────────────────────────────

    @staticmethod
    def _generate_barcode_image(barcode_value):
        """Return a PIL Image of a Code 128 barcode, or None."""
        if not barcode_value:
            return None
        try:
            import barcode as barcode_lib
            from barcode.writer import ImageWriter

            code128 = barcode_lib.get_barcode_class("code128")
            bc = code128(str(barcode_value), writer=ImageWriter())
            buf = BytesIO()
            bc.write(buf)
            buf.seek(0)
            from PIL import Image

            return Image.open(buf).copy()
        except ImportError:
            logger.warning("python-barcode not installed – skipping barcode image")
            return None
        except Exception:
            logger.exception("Failed to generate barcode image for %s", barcode_value)
            return None

    @staticmethod
    def _image_to_pdf_bytes(image):
        """Convert a PIL Image to a single-page PDF as bytes."""
        buf = BytesIO()
        image.save(buf, format="PDF")
        buf.seek(0)
        return buf.getvalue()
