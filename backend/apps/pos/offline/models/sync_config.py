"""
Offline Sync Configuration model.

Stores tenant-specific settings that control how POS terminals
synchronise data when transitioning between online and offline modes.
Covers sync frequency, cache TTLs, retry policies, and conflict
resolution strategies.
"""

from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models

from apps.core.models import BaseModel
from apps.pos.offline.constants import (
    CONFLICT_RESOLUTION_CHOICES,
    CONFLICT_RESOLUTION_SERVER_WINS,
    DEFAULT_AUTO_SYNC_INTERVAL,
    DEFAULT_CACHE_TTL_CATEGORIES,
    DEFAULT_CACHE_TTL_CUSTOMERS,
    DEFAULT_CACHE_TTL_PRICES,
    DEFAULT_CACHE_TTL_PRODUCTS,
    DEFAULT_CACHE_TTL_SETTINGS,
    DEFAULT_CONFLICT_ARCHIVE_DAYS,
    DEFAULT_CONFLICT_RESOLUTION_TIMEOUT_HOURS,
    DEFAULT_MAX_OFFLINE_TRANSACTIONS,
    DEFAULT_MAX_RETRY_ATTEMPTS,
    DEFAULT_RETRY_BACKOFF_MINUTES,
    DEFAULT_SYNC_BATCH_SIZE,
)


class OfflineSyncConfig(BaseModel):
    """
    Tenant-level configuration for POS offline synchronisation.

    Each tenant may have one active configuration that governs sync
    frequency, cache lifetimes, retry behaviour, and conflict
    resolution policies across all POS terminals.
    """

    # ── Basic Info ────────────────────────────────────────────────────────
    config_name = models.CharField(
        max_length=100,
        help_text="Human-readable name for this configuration.",
    )
    description = models.TextField(
        blank=True,
        default="",
        help_text="Optional description of this configuration.",
    )

    # ── Sync Frequency Settings ───────────────────────────────────────────
    auto_sync_interval = models.PositiveIntegerField(
        default=DEFAULT_AUTO_SYNC_INTERVAL,
        validators=[MinValueValidator(5), MaxValueValidator(1440)],
        help_text="Automatic sync interval in minutes (5-1440).",
    )
    sync_on_startup = models.BooleanField(
        default=True,
        help_text="Trigger a sync when the POS application starts.",
    )
    sync_after_transaction = models.BooleanField(
        default=False,
        help_text="Trigger a sync after each completed transaction.",
    )
    max_offline_transactions = models.PositiveIntegerField(
        default=DEFAULT_MAX_OFFLINE_TRANSACTIONS,
        validators=[MinValueValidator(10), MaxValueValidator(1000)],
        help_text="Maximum queued offline transactions before forcing sync (10-1000).",
    )

    # ── Cache TTL Settings (minutes) ──────────────────────────────────────
    cache_ttl_products = models.PositiveIntegerField(
        default=DEFAULT_CACHE_TTL_PRODUCTS,
        help_text="Cache TTL for products in minutes.",
    )
    cache_ttl_prices = models.PositiveIntegerField(
        default=DEFAULT_CACHE_TTL_PRICES,
        help_text="Cache TTL for prices in minutes.",
    )
    cache_ttl_customers = models.PositiveIntegerField(
        default=DEFAULT_CACHE_TTL_CUSTOMERS,
        help_text="Cache TTL for customers in minutes.",
    )
    cache_ttl_categories = models.PositiveIntegerField(
        default=DEFAULT_CACHE_TTL_CATEGORIES,
        help_text="Cache TTL for categories in minutes.",
    )
    cache_ttl_settings = models.PositiveIntegerField(
        default=DEFAULT_CACHE_TTL_SETTINGS,
        help_text="Cache TTL for POS settings in minutes.",
    )

    # ── Retry / Batch Settings ────────────────────────────────────────────
    sync_batch_size = models.PositiveIntegerField(
        default=DEFAULT_SYNC_BATCH_SIZE,
        validators=[MinValueValidator(10), MaxValueValidator(500)],
        help_text="Number of records per sync batch (10-500).",
    )
    max_retry_attempts = models.PositiveIntegerField(
        default=DEFAULT_MAX_RETRY_ATTEMPTS,
        validators=[MinValueValidator(1), MaxValueValidator(10)],
        help_text="Maximum retry attempts for a failed sync (1-10).",
    )
    retry_backoff_minutes = models.PositiveIntegerField(
        default=DEFAULT_RETRY_BACKOFF_MINUTES,
        validators=[MinValueValidator(1), MaxValueValidator(60)],
        help_text="Base backoff delay between retries in minutes (1-60).",
    )
    retry_exponential = models.BooleanField(
        default=True,
        help_text="Use exponential backoff for retries.",
    )
    low_bandwidth_mode = models.BooleanField(
        default=False,
        help_text="Reduce batch sizes and skip non-critical data on slow connections.",
    )

    # ── Scheduled Sync ────────────────────────────────────────────────────
    scheduled_sync_enabled = models.BooleanField(
        default=False,
        help_text="Enable scheduled sync at specific times.",
    )
    scheduled_sync_times = models.JSONField(
        default=list,
        blank=True,
        help_text='List of scheduled sync times, e.g. ["06:00","12:00","18:00"].',
    )
    sync_during_business_hours_only = models.BooleanField(
        default=False,
        help_text="Restrict automatic syncs to business hours only.",
    )

    # ── Conflict Resolution Settings ──────────────────────────────────────
    default_conflict_resolution = models.CharField(
        max_length=20,
        choices=CONFLICT_RESOLUTION_CHOICES,
        default=CONFLICT_RESOLUTION_SERVER_WINS,
        help_text="Default conflict resolution strategy.",
    )
    product_conflict_resolution = models.CharField(
        max_length=20,
        choices=CONFLICT_RESOLUTION_CHOICES,
        default=CONFLICT_RESOLUTION_SERVER_WINS,
        help_text="Conflict resolution for product data.",
    )
    customer_conflict_resolution = models.CharField(
        max_length=20,
        choices=CONFLICT_RESOLUTION_CHOICES,
        default=CONFLICT_RESOLUTION_SERVER_WINS,
        help_text="Conflict resolution for customer data.",
    )
    price_conflict_resolution = models.CharField(
        max_length=20,
        choices=CONFLICT_RESOLUTION_CHOICES,
        default=CONFLICT_RESOLUTION_SERVER_WINS,
        help_text="Conflict resolution for price data.",
    )
    transaction_conflict_resolution = models.CharField(
        max_length=20,
        choices=CONFLICT_RESOLUTION_CHOICES,
        default=CONFLICT_RESOLUTION_SERVER_WINS,
        help_text="Conflict resolution for transaction data.",
    )
    allow_auto_merge = models.BooleanField(
        default=False,
        help_text="Allow automatic merging of non-conflicting fields.",
    )
    merge_rules = models.JSONField(
        default=dict,
        blank=True,
        help_text="Entity-specific merge rules as JSON.",
    )

    # ── Notification / Approval ───────────────────────────────────────────
    notify_on_conflict = models.BooleanField(
        default=True,
        help_text="Send notification when a sync conflict is detected.",
    )
    conflict_notification_emails = models.JSONField(
        default=list,
        blank=True,
        help_text="Email addresses to notify on conflicts.",
    )
    require_supervisor_approval = models.BooleanField(
        default=False,
        help_text="Require supervisor approval before resolving conflicts.",
    )
    conflict_resolution_timeout_hours = models.PositiveIntegerField(
        default=DEFAULT_CONFLICT_RESOLUTION_TIMEOUT_HOURS,
        help_text="Hours before unresolved conflicts auto-resolve.",
    )

    # ── Data Preservation ─────────────────────────────────────────────────
    preserve_client_data = models.BooleanField(
        default=True,
        help_text="Keep client-side data copy on conflict.",
    )
    preserve_server_data = models.BooleanField(
        default=True,
        help_text="Keep server-side data copy on conflict.",
    )
    conflict_archive_days = models.PositiveIntegerField(
        default=DEFAULT_CONFLICT_ARCHIVE_DAYS,
        help_text="Days to retain archived conflict records.",
    )
    prioritize_latest_timestamp = models.BooleanField(
        default=True,
        help_text="Prefer the record with the most recent timestamp.",
    )

    class Meta(BaseModel.Meta):
        db_table = "pos_offline_sync_config"
        verbose_name = "Offline Sync Configuration"
        verbose_name_plural = "Offline Sync Configurations"

    def __str__(self):
        return f"{self.config_name} (active={self.is_active})"
