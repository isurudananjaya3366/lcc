"""
Credit & Loyalty signals.

Auto-creates CreditSettings for new tenants.
"""

import logging

from django.db import ProgrammingError
from django.db.models.signals import post_save
from django.dispatch import receiver

logger = logging.getLogger(__name__)


@receiver(post_save, sender="tenants.Tenant")
def create_credit_settings_for_tenant(sender, instance, created, **kwargs):
    """Auto-create CreditSettings when a new tenant is created."""
    if created:
        try:
            from apps.credit.models.credit_settings import CreditSettings

            CreditSettings.objects.get_or_create(tenant=instance)
        except ProgrammingError:
            # Table may not exist yet during initial schema creation
            logger.debug(
                "credit_settings table not ready for tenant %s; "
                "will be created on first access.",
                instance.schema_name,
            )
