"""
QuoteHistory model for tracking quote lifecycle events.

Task 48: Audit trail for quote status changes and modifications.
"""

from django.conf import settings
from django.db import models


class QuoteHistory(models.Model):
    """Tracks changes and events in a quote's lifecycle."""

    CREATED = "CREATED"
    UPDATED = "UPDATED"
    SENT = "SENT"
    ACCEPTED = "ACCEPTED"
    REJECTED = "REJECTED"
    EXPIRED = "EXPIRED"
    CONVERTED = "CONVERTED"
    REVISION_CREATED = "REVISION_CREATED"
    STATUS_CHANGED = "STATUS_CHANGED"

    EVENT_TYPE_CHOICES = [
        (CREATED, "Quote Created"),
        (UPDATED, "Quote Updated"),
        (SENT, "Sent to Customer"),
        (ACCEPTED, "Customer Accepted"),
        (REJECTED, "Customer Rejected"),
        (EXPIRED, "Quote Expired"),
        (CONVERTED, "Converted to Order"),
        (REVISION_CREATED, "Revision Created"),
        (STATUS_CHANGED, "Status Changed"),
    ]

    quote = models.ForeignKey(
        "quotes.Quote",
        on_delete=models.CASCADE,
        related_name="history",
    )
    event_type = models.CharField(
        max_length=50,
        choices=EVENT_TYPE_CHOICES,
        db_index=True,
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    timestamp = models.DateTimeField(auto_now_add=True, db_index=True)
    old_values = models.JSONField(null=True, blank=True)
    new_values = models.JSONField(null=True, blank=True)
    notes = models.TextField(blank=True)

    class Meta:
        db_table = "quotes_quotehistory"
        ordering = ["-timestamp"]
        verbose_name = "Quote History"
        verbose_name_plural = "Quote Histories"
        indexes = [
            models.Index(
                fields=["quote", "-timestamp"],
                name="idx_qh_quote_timestamp",
            ),
            models.Index(
                fields=["event_type", "-timestamp"],
                name="idx_qh_event_timestamp",
            ),
        ]

    def __str__(self):
        return (
            f"{self.quote.quote_number} - "
            f"{self.get_event_type_display()} - "
            f"{self.timestamp}"
        )

    def get_changes_summary(self):
        """Return a human-readable summary of changes."""
        if not self.old_values or not self.new_values:
            return self.get_event_type_display()
        changes = []
        for key in self.new_values:
            old_val = self.old_values.get(key)
            new_val = self.new_values.get(key)
            if old_val != new_val:
                changes.append(f"{key}: {old_val} → {new_val}")
        return "; ".join(changes) if changes else self.get_event_type_display()
