"""
ReceiptBuilder — builds complete receipt data from a POS cart.

Tasks 23-32: Header, transaction info, items, variant display,
totals, tax breakdown, payments, footer, and QR code.
"""

import logging
from decimal import Decimal

from django.utils import timezone

from apps.pos.receipts.services.exceptions import (
    CartValidationError,
    DataBuildError,
    ReceiptBuildError,
    TemplateMissingError,
)

logger = logging.getLogger(__name__)


class ReceiptBuilder:
    """
    Transforms a completed POSCart into a structured receipt-data dict
    suitable for JSON storage, thermal printing, PDF, and email.
    """

    CURRENCY_SYMBOL = "Rs."

    def __init__(self, cart, template=None):
        self.cart = cart
        self.template = template or self._get_default_template()
        self._receipt_number = None  # cached after first generation

    # ── PUBLIC API ────────────────────────────────────────────

    def build(self):
        """
        Build complete receipt data.

        Returns:
            dict: Full receipt data structure.
        """
        try:
            self.validate_cart()
            payments_data = self.build_payments()
            return {
                "schema_version": "1.0",
                "generated_at": timezone.now().isoformat(),
                "header": self.build_header(),
                "transaction": self.build_transaction_info(),
                "items": self.build_items(),
                "totals": self.build_totals(),
                "payments": payments_data["payments"],
                "payments_info": payments_data,
                "footer": self.build_footer(),
                "qr_code": self.build_qr_code(),
            }
        except (CartValidationError, TemplateMissingError):
            raise
        except Exception as exc:
            logger.exception("Unexpected error building receipt: %s", exc)
            raise ReceiptBuildError(f"Failed to build receipt: {exc}") from exc

    def validate_cart(self):
        if self.cart.status != "completed":
            raise CartValidationError(
                f"Cart must be completed (current: {self.cart.status})"
            )
        if not self.cart.items.exists():
            raise CartValidationError("Cart has no items")
        if self.cart.grand_total is None or self.cart.grand_total <= 0:
            raise CartValidationError("Cart total not calculated")

    # ── Task 24: build_header ─────────────────────────────────

    def build_header(self):
        header = {
            "business_name": self._get_business_name(),
        }

        # Address lines
        address = self._format_address()
        header.update(address)

        # Contact
        contact = self._get_contact_info()
        header.update(contact)

        # Tax registration
        tax_reg = self._get_tax_registration()
        header.update(tax_reg)

        # Custom header lines from template
        custom = self._get_custom_header_lines()
        if custom:
            header["custom_lines"] = custom

        return header

    # ── Task 25: build_transaction_info ───────────────────────

    def build_transaction_info(self):
        local_dt = self._get_local_datetime()

        data = {
            "receipt_number": self._get_or_generate_receipt_number(),
            "date": local_dt.strftime("%Y-%m-%d"),
            "date_display": local_dt.strftime("%d/%m/%Y"),
            "time": local_dt.strftime("%H:%M:%S"),
            "time_display": local_dt.strftime("%I:%M %p").lstrip("0"),
            "datetime_local": local_dt.strftime("%Y-%m-%d %H:%M:%S"),
            "cashier_name": self._get_cashier_name(),
            "cashier_id": self._get_cashier_id(),
            "terminal_id": self._get_terminal_id(),
            "terminal_name": self._get_terminal_name(),
        }

        ref = self._get_cart_reference()
        if ref:
            data["order_number"] = ref

        return data

    # ── Tasks 26-27: build_items + variant display ────────────

    def build_items(self):
        cart_items = self.cart.items.select_related(
            "product", "variant"
        ).order_by("line_number", "created_on")

        if not cart_items.exists():
            raise DataBuildError("Cart has no items")

        return [
            self._build_item_data(ci, idx)
            for idx, ci in enumerate(cart_items, start=1)
        ]

    # ── Tasks 28-29: build_totals + tax breakdown ─────────────

    def build_totals(self):
        subtotal = self.cart.subtotal or Decimal("0.00")
        discount_total = self.cart.discount_total or Decimal("0.00")
        tax_total = self.cart.tax_total or Decimal("0.00")
        grand_total = self.cart.grand_total or Decimal("0.00")

        data = {
            "subtotal": float(subtotal),
            "subtotal_display": self._fmt(subtotal),
            "discount_total": float(discount_total),
            "discount_display": self._fmt(discount_total),
            "tax_total": float(tax_total),
            "tax_display": self._fmt(tax_total),
            "grand_total": float(grand_total),
            "grand_total_display": self._fmt(grand_total),
            "tax_breakdown": self._build_tax_breakdown(),
        }

        # Task 28: Additional totals fields
        taxable_amount = subtotal - discount_total
        data["taxable_amount"] = float(taxable_amount)
        data["taxable_amount_display"] = self._fmt(taxable_amount)

        if subtotal > 0:
            data["discount_percent"] = float(
                (discount_total / subtotal * Decimal("100")).quantize(Decimal("0.01"))
            )
        else:
            data["discount_percent"] = 0.0

        if taxable_amount > 0:
            data["tax_rate"] = float(
                (tax_total / taxable_amount * Decimal("100")).quantize(Decimal("0.01"))
            )
        else:
            data["tax_rate"] = 0.0

        if discount_total > 0:
            data["amount_saved"] = float(discount_total)
            data["amount_saved_display"] = self._fmt(discount_total)

        # Tax-exempt amount
        exempt = self._calculate_tax_exempt_amount()
        if exempt > 0:
            data["tax_exempt_amount"] = float(exempt)
            data["tax_exempt_display"] = self._fmt(exempt)

        return data

    # ── Task 30: build_payments ───────────────────────────────

    def build_payments(self):
        payments_qs = self.cart.payments.filter(
            status="completed"
        ).order_by("created_on")

        if not payments_qs.exists():
            # Fallback: include pending if no completed
            payments_qs = self.cart.payments.all().order_by("created_on")

        payments_list = [self._build_payment_entry(p) for p in payments_qs]

        total_paid = sum(p["amount"] for p in payments_list)
        grand_total_f = float(self.cart.grand_total or 0)
        change_due = max(total_paid - grand_total_f, 0.0)

        result = {
            "payments": payments_list,
            "total_paid": total_paid,
            "total_paid_display": self._fmt(Decimal(str(total_paid))),
            "amount_due": max(grand_total_f - total_paid, 0.0),
            "change_due": change_due,
        }
        if change_due > 0:
            result["change_due_display"] = self._fmt(Decimal(str(change_due)))

        return result

    # ── Task 31: build_footer ─────────────────────────────────

    def build_footer(self):
        footer: dict = {}

        # Thank-you message
        thank_you = self._tpl("footer_line_1") or "Thank you for your purchase!"
        footer["thank_you_message"] = thank_you

        # Custom footer lines
        lines = []
        for attr in ("footer_line_1", "footer_line_2", "footer_line_3"):
            val = self._tpl(attr)
            if val:
                lines.append(val)
        if lines:
            footer["custom_lines"] = lines

        # Return policy
        if self._tpl("show_return_policy"):
            policy = self._tpl("return_policy_text")
            if policy:
                footer["return_policy"] = policy
                heading = self._tpl("return_policy_heading")
                if heading:
                    footer["return_policy_heading"] = heading

        # Website
        website = self._tpl("show_website")
        if website:
            footer["website"] = website

        # Social media placeholders (read from template when available)
        social = self._tpl("social_media")
        if social:
            footer["social_media"] = social

        footer["footer_note"] = "This is a computer-generated receipt"
        footer["footer_lines"] = lines if lines else [footer["thank_you_message"]]
        return footer

    # ── Task 32: build_qr_code ────────────────────────────────

    def build_qr_code(self):
        receipt_number = self._get_or_generate_receipt_number()
        qr_data = {
            "data": receipt_number,
            "format": "TEXT",
            "error_correction": "M",
            "size": self._tpl("qr_code_size") or "medium",
            "display_text": receipt_number,
            "metadata": {
                "receipt_number": receipt_number,
                "generated_at": timezone.now().isoformat(),
            },
        }
        return qr_data

    # ══════════════════════════════════════════════════════════
    # PRIVATE HELPERS
    # ══════════════════════════════════════════════════════════

    def _get_default_template(self):
        from apps.pos.receipts.models import ReceiptTemplate

        tpl = ReceiptTemplate.objects.filter(
            is_active=True, is_default=True
        ).first()
        if not tpl:
            tpl = ReceiptTemplate.objects.filter(is_active=True).first()
        return tpl

    def _tpl(self, field_name, default=None):
        """Safe template field access."""
        if self.template and hasattr(self.template, field_name):
            val = getattr(self.template, field_name, None)
            if val is not None and val != "":
                return val
        return default

    # ── header helpers ────────────────────────────────────────

    def _get_business_name(self):
        override = self._tpl("business_name_override")
        if override:
            return override
        session = getattr(self.cart, "session", None)
        if session:
            terminal = getattr(session, "terminal", None)
            if terminal and hasattr(terminal, "name"):
                pass  # terminal name != business name
        return "Business"

    def _format_address(self):
        """Extract address from session/terminal tenant settings."""
        session = getattr(self.cart, "session", None)
        if session:
            terminal = getattr(session, "terminal", None)
            if terminal:
                return {
                    "address_line_1": getattr(terminal, "address_line_1", "") or "",
                    "address_line_2": getattr(terminal, "address_line_2", "") or "",
                    "address_line_3": getattr(terminal, "city", "") or "",
                }
        return {
            "address_line_1": "",
            "address_line_2": "",
            "address_line_3": "",
        }

    def _get_contact_info(self):
        """Extract contact info from session/terminal."""
        session = getattr(self.cart, "session", None)
        if session:
            terminal = getattr(session, "terminal", None)
            if terminal:
                return {
                    "phone": getattr(terminal, "phone", "") or "",
                    "email": getattr(terminal, "email", "") or "",
                    "website": getattr(terminal, "website", "") or "",
                }
        return {}

    def _get_tax_registration(self):
        """Extract tax registration numbers from session/terminal."""
        session = getattr(self.cart, "session", None)
        if session:
            terminal = getattr(session, "terminal", None)
            if terminal:
                info = {}
                vat = getattr(terminal, "vat_number", None)
                tin = getattr(terminal, "tin_number", None)
                if vat:
                    info["vat_number"] = vat
                if tin:
                    info["tin_number"] = tin
                return info
        return {}

    def _get_custom_header_lines(self):
        lines = []
        for attr in ("header_line_1", "header_line_2", "header_line_3"):
            val = self._tpl(attr)
            if val:
                lines.append(val)
        return lines

    # ── transaction helpers ───────────────────────────────────

    def _get_local_datetime(self):
        import zoneinfo

        utc_now = timezone.now()
        try:
            lk_tz = zoneinfo.ZoneInfo("Asia/Colombo")
            return utc_now.astimezone(lk_tz)
        except Exception:
            return utc_now

    def _get_or_generate_receipt_number(self):
        if self._receipt_number:
            return self._receipt_number
        from apps.pos.receipts.services.number_generator import ReceiptNumberGenerator

        gen = ReceiptNumberGenerator()
        self._receipt_number = gen.generate()
        return self._receipt_number

    def _get_cashier_name(self):
        user = getattr(self.cart, "created_by", None)
        if user:
            return self._format_user_name(user)
        return "Cashier"

    def _get_cashier_id(self):
        user = getattr(self.cart, "created_by", None)
        if user:
            if hasattr(user, "employee_code") and user.employee_code:
                return user.employee_code
            return str(user.pk)[:8]
        return "N/A"

    def _get_terminal_id(self):
        session = getattr(self.cart, "session", None)
        if session:
            terminal = getattr(session, "terminal", None)
            if terminal and hasattr(terminal, "terminal_code"):
                return terminal.terminal_code
        return "POS-01"

    def _get_terminal_name(self):
        session = getattr(self.cart, "session", None)
        if session:
            terminal = getattr(session, "terminal", None)
            if terminal:
                return getattr(terminal, "name", None)
        return None

    def _get_cart_reference(self):
        return getattr(self.cart, "reference_number", None)

    @staticmethod
    def _format_user_name(user):
        if hasattr(user, "get_full_name"):
            full = user.get_full_name()
            if full and full.strip():
                return full.strip()
        if getattr(user, "first_name", ""):
            last = getattr(user, "last_name", "")
            return f"{user.first_name} {last}".strip()
        return getattr(user, "email", "Cashier")

    # ── item helpers ──────────────────────────────────────────

    def _build_item_data(self, cart_item, line_number):
        product = cart_item.product
        variant = getattr(cart_item, "variant", None)

        unit_price = cart_item.unit_price or Decimal("0.00")
        discount_amount = cart_item.discount_amount or Decimal("0.00")
        line_total = cart_item.line_total or Decimal("0.00")
        tax_rate = cart_item.tax_rate or Decimal("0.00")
        tax_amount = cart_item.tax_amount or Decimal("0.00")
        quantity = cart_item.quantity or Decimal("1.000")

        data = {
            "line_number": line_number,
            "sku": self._get_item_sku(product, variant),
            "name": self._truncate(product.name, 30),
            "variant_display": self._get_variant_display(variant),
            "quantity": float(quantity),
            "quantity_display": self._format_quantity(quantity),
            "unit_price": float(unit_price),
            "unit_price_display": self._fmt(unit_price),
            "discount": float(discount_amount),
            "discount_display": self._fmt(discount_amount) if discount_amount > 0 else None,
            "line_total": float(line_total),
            "line_total_display": self._fmt(line_total),
            "tax_rate": float(tax_rate),
            "tax_amount": float(tax_amount),
            "is_free": unit_price == 0,
            "is_promotional": bool(
                getattr(cart_item, "is_promotional", False)
                or getattr(cart_item, "promotion_id", None)
            ),
        }
        if discount_amount > 0 and unit_price > 0:
            data["discount_percent"] = float(
                (discount_amount / (unit_price * quantity) * Decimal("100")).quantize(
                    Decimal("0.01")
                )
            )
        return data

    @staticmethod
    def _get_item_sku(product, variant=None):
        if variant and getattr(variant, "sku", None):
            return variant.sku
        if getattr(product, "sku", None):
            return product.sku
        return str(product.pk)[:8]

    @staticmethod
    def _get_variant_display(variant):
        if not variant:
            return None
        if hasattr(variant, "display_name") and variant.display_name:
            return variant.display_name
        return getattr(variant, "name", None)

    # ── totals / tax helpers ──────────────────────────────────

    def _build_tax_breakdown(self):
        tax_groups: dict[Decimal, dict] = {}

        for item in self.cart.items.all():
            rate = item.tax_rate or Decimal("0.00")
            if rate not in tax_groups:
                tax_groups[rate] = {"taxable": Decimal("0.00"), "tax": Decimal("0.00")}
            tax_groups[rate]["taxable"] += item.line_total or Decimal("0.00")
            tax_groups[rate]["tax"] += item.tax_amount or Decimal("0.00")

        breakdown = []
        for rate in sorted(tax_groups.keys(), reverse=True):
            info = tax_groups[rate]
            if rate == Decimal("15.00"):
                name = "VAT"
            elif rate == Decimal("0.00"):
                name = "Tax Exempt"
            else:
                name = f"Tax ({rate}%)"

            breakdown.append(
                {
                    "tax_name": name,
                    "tax_rate": float(rate),
                    "tax_rate_display": f"{rate}%",
                    "taxable_amount": float(info["taxable"]),
                    "taxable_amount_display": self._fmt(info["taxable"]),
                    "tax_amount": float(info["tax"]),
                    "tax_amount_display": self._fmt(info["tax"]),
                }
            )
        return breakdown

    def _verify_tax_breakdown(self, breakdown):
        """Verify tax breakdown sums match cart totals (Task 29)."""
        total_tax = sum(Decimal(str(item["tax_amount"])) for item in breakdown)
        cart_tax = self.cart.tax_total or Decimal("0.00")
        if abs(total_tax - cart_tax) > Decimal("0.02"):
            logger.warning(
                "Tax breakdown mismatch: breakdown=%s, cart=%s",
                total_tax,
                cart_tax,
            )
        return abs(total_tax - cart_tax) <= Decimal("0.02")

    def _calculate_tax_exempt_amount(self):
        total = Decimal("0.00")
        for item in self.cart.items.all():
            if not getattr(item, "is_taxable", True):
                total += item.line_total or Decimal("0.00")
        return total

    # ── payment helpers ───────────────────────────────────────

    def _build_payment_entry(self, payment):
        method = getattr(payment, "method", "UNKNOWN")
        amount = payment.amount or Decimal("0.00")
        change = Decimal("0.00")

        if method == "cash":
            tendered = getattr(payment, "amount_tendered", None)
            change_val = getattr(payment, "change_due", None)
            if change_val and change_val > 0:
                change = change_val
            elif tendered and tendered > amount:
                change = tendered - amount

        entry = {
            "method": method,
            "method_display": self._format_payment_method(payment),
            "amount": float(amount),
            "amount_display": self._fmt(amount),
            "reference": getattr(payment, "reference_number", None) or None,
            "change": float(change),
        }
        if change > 0:
            entry["change_display"] = self._fmt(change)
        return entry

    @staticmethod
    def _format_payment_method(payment):
        method = getattr(payment, "method", "")
        mapping = {
            "cash": "Cash",
            "card": "Card",
            "bank_transfer": "Bank Transfer",
            "mobile_frimi": "FriMi",
            "mobile_genie": "Dialog Genie",
            "store_credit": "Store Credit",
            "payhere": "PayHere",
        }
        return mapping.get(method, method.replace("_", " ").title())

    # ── formatting helpers ────────────────────────────────────

    def _fmt(self, amount):
        """Format Decimal as Sri Lankan Rupee string."""
        if amount is None:
            return f"{self.CURRENCY_SYMBOL} 0.00"
        return f"{self.CURRENCY_SYMBOL} {Decimal(str(amount)):,.2f}"

    @staticmethod
    def _format_quantity(quantity):
        d = Decimal(str(quantity))
        if d == d.to_integral_value():
            return str(int(d))
        return f"{d:.3f}".rstrip("0").rstrip(".")

    @staticmethod
    def _truncate(text, max_length=40):
        if not text or len(text) <= max_length:
            return text
        return text[: max_length - 3] + "..."
