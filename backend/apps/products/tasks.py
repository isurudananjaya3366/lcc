"""
Products app Celery tasks.

Re-exports tasks from sub-modules so Celery autodiscover finds them.
"""

from apps.products.media.tasks import process_image_variants  # noqa: F401
from apps.products.pricing.tasks import update_scheduled_prices  # noqa: F401
