"""Constants for the Payslip Generation app.

Defines payslip status choices for lifecycle tracking
from draft through generation, distribution, and download.
"""

from django.db import models


class PayslipStatus(models.TextChoices):
    """Status choices tracking the payslip document lifecycle.

    Flow: DRAFT → GENERATED → SENT → VIEWED → DOWNLOADED
    """

    DRAFT = "DRAFT", "Draft"
    GENERATED = "GENERATED", "Generated"
    SENT = "SENT", "Sent"
    VIEWED = "VIEWED", "Viewed"
    DOWNLOADED = "DOWNLOADED", "Downloaded"
