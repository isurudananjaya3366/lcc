"""
Quote Sequence Model

Tracks yearly quote number sequences for auto-generation.
"""

from django.db import models


class QuoteSequence(models.Model):
    """
    Tracks the last used sequence number for each year.
    Used by QuoteNumberGenerator for atomic sequence generation.
    """

    year = models.IntegerField(unique=True, help_text="Year for this sequence")
    last_number = models.IntegerField(
        default=0, help_text="Last used sequence number"
    )

    class Meta:
        db_table = "quote_sequences"
        verbose_name = "Quote Sequence"
        verbose_name_plural = "Quote Sequences"

    def __str__(self):
        return f"QuoteSequence({self.year}: {self.last_number})"
