"""
SearchHistory model — tracks POS product search queries for analytics
and autocomplete/suggestions.
"""

from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _

from apps.pos.constants import SEARCH_METHOD_CHOICES, SEARCH_METHOD_COMBINED


class SearchHistory(models.Model):
    """Records each product search performed at a POS terminal."""

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="pos_search_history",
        verbose_name=_("User"),
    )
    terminal = models.ForeignKey(
        "pos.POSTerminal",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="search_history",
        verbose_name=_("Terminal"),
    )
    query = models.CharField(
        max_length=200,
        verbose_name=_("Search Query"),
    )
    result_count = models.IntegerField(
        default=0,
        verbose_name=_("Result Count"),
    )
    selected_product = models.ForeignKey(
        "products.Product",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="+",
        verbose_name=_("Selected Product"),
    )
    search_method = models.CharField(
        max_length=20,
        choices=SEARCH_METHOD_CHOICES,
        default=SEARCH_METHOD_COMBINED,
        verbose_name=_("Search Method"),
    )
    timestamp = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_("Timestamp"),
    )

    class Meta:
        db_table = "pos_search_history"
        ordering = ["-timestamp"]
        verbose_name = _("Search History")
        verbose_name_plural = _("Search History")
        indexes = [
            models.Index(
                fields=["terminal", "-timestamp"],
                name="pos_sh_terminal_ts",
            ),
            models.Index(
                fields=["user", "-timestamp"],
                name="pos_sh_user_ts",
            ),
        ]

    def __str__(self):
        return f"{self.query} ({self.search_method})"
