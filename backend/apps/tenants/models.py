"""
LankaCommerce Cloud - Tenant and Domain Models.

Defines the Tenant and Domain models for multi-tenant SaaS operations.

The Tenant model represents an organization (business) in the platform.
Each tenant maps to a dedicated PostgreSQL schema where all tenant-specific
business data (products, sales, inventory, etc.) is stored in isolation.

The Domain model maps hostnames and subdomains to tenants. django-tenants
uses this mapping to resolve the current tenant from the incoming request
hostname via TenantMainMiddleware, which then sets the PostgreSQL
search_path to the tenant's schema.

The Tenant model extends django-tenants' TenantMixin, which provides the
schema_name field and schema lifecycle management (auto-create on save,
optional auto-drop on delete).

Key fields:
    - schema_name: PostgreSQL schema name (from TenantMixin, e.g. 'tenant_acme')
    - name: Human-readable business name
    - slug: URL-safe identifier used in subdomains and schema naming
    - paid_until: Subscription expiry date for billing lifecycle
    - on_trial: Whether the tenant is currently on a trial period
    - status: Lifecycle state (active, suspended, archived)
    - settings: Per-tenant JSON configuration
    - created_on / updated_on: Audit timestamps

Related models (defined in this same module):
    - Domain: Maps hostnames/subdomains to tenants (see 02_Tasks-49-52)

Settings references:
    - TENANT_MODEL = "tenants.Tenant" (in config/settings/database.py)
    - TENANT_SCHEMA_PREFIX = "tenant_" (in config/settings/database.py)
    - AUTO_CREATE_SCHEMA = True (schema created on Tenant.save())
    - AUTO_DROP_SCHEMA = False (schema NOT dropped on Tenant.delete())
"""

from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator
from django.db import models
from django.utils import timezone
from django_tenants.models import DomainMixin, TenantMixin

from apps.tenants.managers import DomainManager, SubscriptionManager, TenantManager


# ════════════════════════════════════════════════════════════════════════
# CONSTANTS
# ════════════════════════════════════════════════════════════════════════

# Tenant lifecycle statuses
TENANT_STATUS_ACTIVE = "active"
TENANT_STATUS_SUSPENDED = "suspended"
TENANT_STATUS_ARCHIVED = "archived"

TENANT_STATUS_CHOICES = [
    (TENANT_STATUS_ACTIVE, "Active"),
    (TENANT_STATUS_SUSPENDED, "Suspended"),
    (TENANT_STATUS_ARCHIVED, "Archived"),
]

# Schema name reserved words that cannot be used as tenant slugs
RESERVED_SCHEMA_NAMES = frozenset({
    "public",
    "pg_catalog",
    "information_schema",
    "pg_toast",
})

# Slug validation regex: lowercase letters, digits, and hyphens.
# Must start with a letter or digit. No consecutive hyphens.
SLUG_REGEX = r"^[a-z0-9](?:[a-z0-9]|-(?=[a-z0-9]))*$"

# Default per-tenant settings structure
DEFAULT_TENANT_SETTINGS = {
    "currency": "LKR",
    "timezone": "Asia/Colombo",
    "date_format": "YYYY-MM-DD",
    "language": "en",
}

# Business type choices for tenant classification
BUSINESS_TYPE_SOLE_PROPRIETOR = "sole_proprietor"
BUSINESS_TYPE_PARTNERSHIP = "partnership"
BUSINESS_TYPE_PVT_LTD = "pvt_ltd"
BUSINESS_TYPE_PLC = "plc"
BUSINESS_TYPE_COOPERATIVE = "cooperative"
BUSINESS_TYPE_NGO = "ngo"
BUSINESS_TYPE_OTHER = "other"

BUSINESS_TYPE_CHOICES = [
    (BUSINESS_TYPE_SOLE_PROPRIETOR, "Sole Proprietor"),
    (BUSINESS_TYPE_PARTNERSHIP, "Partnership"),
    (BUSINESS_TYPE_PVT_LTD, "Private Limited Company"),
    (BUSINESS_TYPE_PLC, "Public Limited Company"),
    (BUSINESS_TYPE_COOPERATIVE, "Cooperative Society"),
    (BUSINESS_TYPE_NGO, "Non-Governmental Organization"),
    (BUSINESS_TYPE_OTHER, "Other"),
]

# Industry classification choices
INDUSTRY_RETAIL = "retail"
INDUSTRY_WHOLESALE = "wholesale"
INDUSTRY_MANUFACTURING = "manufacturing"
INDUSTRY_SERVICES = "services"
INDUSTRY_FOOD_BEVERAGE = "food_beverage"
INDUSTRY_HEALTHCARE = "healthcare"
INDUSTRY_EDUCATION = "education"
INDUSTRY_TECHNOLOGY = "technology"
INDUSTRY_AGRICULTURE = "agriculture"
INDUSTRY_CONSTRUCTION = "construction"
INDUSTRY_HOSPITALITY = "hospitality"
INDUSTRY_AUTOMOTIVE = "automotive"
INDUSTRY_OTHER = "other"

INDUSTRY_CHOICES = [
    (INDUSTRY_RETAIL, "Retail"),
    (INDUSTRY_WHOLESALE, "Wholesale"),
    (INDUSTRY_MANUFACTURING, "Manufacturing"),
    (INDUSTRY_SERVICES, "Professional Services"),
    (INDUSTRY_FOOD_BEVERAGE, "Food & Beverage"),
    (INDUSTRY_HEALTHCARE, "Healthcare"),
    (INDUSTRY_EDUCATION, "Education"),
    (INDUSTRY_TECHNOLOGY, "Technology"),
    (INDUSTRY_AGRICULTURE, "Agriculture"),
    (INDUSTRY_CONSTRUCTION, "Construction"),
    (INDUSTRY_HOSPITALITY, "Hospitality & Tourism"),
    (INDUSTRY_AUTOMOTIVE, "Automotive"),
    (INDUSTRY_OTHER, "Other"),
]

# Sri Lanka province choices (all 9 provinces)
PROVINCE_WESTERN = "western"
PROVINCE_CENTRAL = "central"
PROVINCE_SOUTHERN = "southern"
PROVINCE_NORTHERN = "northern"
PROVINCE_EASTERN = "eastern"
PROVINCE_NORTH_WESTERN = "north_western"
PROVINCE_NORTH_CENTRAL = "north_central"
PROVINCE_UVA = "uva"
PROVINCE_SABARAGAMUWA = "sabaragamuwa"

PROVINCE_CHOICES = [
    (PROVINCE_WESTERN, "Western Province"),
    (PROVINCE_CENTRAL, "Central Province"),
    (PROVINCE_SOUTHERN, "Southern Province"),
    (PROVINCE_NORTHERN, "Northern Province"),
    (PROVINCE_EASTERN, "Eastern Province"),
    (PROVINCE_NORTH_WESTERN, "North Western Province"),
    (PROVINCE_NORTH_CENTRAL, "North Central Province"),
    (PROVINCE_UVA, "Uva Province"),
    (PROVINCE_SABARAGAMUWA, "Sabaragamuwa Province"),
]

# Language choices for tenant locale preferences
LANGUAGE_EN = "en"
LANGUAGE_SI = "si"
LANGUAGE_TA = "ta"

LANGUAGE_CHOICES = [
    (LANGUAGE_EN, "English"),
    (LANGUAGE_SI, "Sinhala (සිංහල)"),
    (LANGUAGE_TA, "Tamil (தமிழ்)"),
]

# Timezone choices relevant to Sri Lanka
TIMEZONE_COLOMBO = "Asia/Colombo"

TIMEZONE_CHOICES = [
    (TIMEZONE_COLOMBO, "Asia/Colombo (IST +05:30)"),
]

# Color validator for hex color codes (e.g. #FF5733)
HEX_COLOR_REGEX = r"^#([A-Fa-f0-9]{6}|[A-Fa-f0-9]{3})$"


# ════════════════════════════════════════════════════════════════════════
# VALIDATORS
# ════════════════════════════════════════════════════════════════════════

slug_validator = RegexValidator(
    regex=SLUG_REGEX,
    message=(
        "Slug must contain only lowercase letters, digits, and hyphens. "
        "Must start with a letter or digit. No consecutive hyphens."
    ),
)

# Sri Lanka Business Registration Number validator.
# Formats: PV 12345, PB 12345, GA 12345, or numeric-only (e.g. 123456).
brn_validator = RegexValidator(
    regex=r"^(PV|PB|GA)\s?\d{4,6}$|^\d{4,9}$",
    message=(
        "Business registration number must be in a valid Sri Lanka format: "
        "PV/PB/GA followed by 4-6 digits, or a numeric registration number."
    ),
)

# Sri Lanka phone number validator.
# Accepts +94 XX XXX XXXX or 0XX XXX XXXX formats (with optional spaces/hyphens).
phone_validator = RegexValidator(
    regex=r"^(\+94|0)[\s-]?\d{2}[\s-]?\d{3}[\s-]?\d{4}$",
    message=(
        "Phone number must be in Sri Lanka format: "
        "+94 XX XXX XXXX or 0XX XXX XXXX."
    ),
)

# Sri Lanka postal code validator.
# Sri Lanka postal codes are 5-digit numbers (e.g. 10100 for Colombo Fort).
postal_code_validator = RegexValidator(
    regex=r"^\d{5}$",
    message="Postal code must be a 5-digit Sri Lanka postal code (e.g. 10100).",
)

# Hex color code validator for branding fields.
hex_color_validator = RegexValidator(
    regex=HEX_COLOR_REGEX,
    message="Color must be a valid hex color code (e.g. #FF5733 or #F53).",
)


def tenant_logo_upload_path(instance, filename):
    """
    Generate tenant-specific logo storage path.

    Storage convention: tenants/<schema_name>/branding/<filename>
    Each tenant's logo is stored in a partitioned directory to prevent
    collisions and enable per-tenant file management.
    """
    return f"tenants/{instance.schema_name}/branding/{filename}"


# ════════════════════════════════════════════════════════════════════════
# TENANT MODEL
# ════════════════════════════════════════════════════════════════════════

class Tenant(TenantMixin):
    """
    Represents a tenant (business organization) in LankaCommerce Cloud.

    Each Tenant instance corresponds to a PostgreSQL schema that isolates
    all business data (products, sales, inventory, customers, etc.) from
    other tenants. The public tenant (schema_name='public') hosts shared
    platform data.

    TenantMixin provides:
        - schema_name (CharField, max_length=63, unique): The PostgreSQL
          schema name. Set to 'public' for the shared/public tenant, or
          'tenant_<slug>' for business tenants.
        - auto_create_schema (bool): When True, saving a new instance
          creates the schema and runs TENANT_APPS migrations.
        - auto_drop_schema (bool): When True, deleting the instance drops
          the schema. MUST remain False in production.

    LankaCommerce adds:
        - name: Human-readable business name
        - slug: URL-safe identifier for subdomains and schema naming
        - business_type / industry: Business classification
        - business_registration_number: Sri Lanka BRN
        - contact_name / contact_email / contact_phone: Primary contact
        - address_line_1 / address_line_2: Street address
        - city / district / province / postal_code: Sri Lanka location
        - logo / primary_color / secondary_color: Branding
        - language / timezone: Locale preferences
        - paid_until: Subscription expiry for billing lifecycle
        - on_trial: Trial period flag
        - status: Lifecycle state management
        - onboarding_step / onboarding_completed: Onboarding progress
        - schema_version: Schema migration version tracking
        - settings: Per-tenant JSON configuration
        - created_on / updated_on: Audit timestamps
    """

    # ── Core Identity ───────────────────────────────────────────────
    name = models.CharField(
        max_length=255,
        help_text="Human-readable business name (e.g. 'Acme Trading Pvt Ltd').",
    )

    slug = models.SlugField(
        max_length=63,
        unique=True,
        validators=[slug_validator],
        help_text=(
            "URL-safe tenant identifier used in subdomains and schema naming. "
            "Lowercase letters, digits, and hyphens only. "
            "Example: 'acme-trading' -> schema 'tenant_acme_trading', "
            "subdomain 'acme-trading.lankacommerce.lk'."
        ),
    )

    # ── Business Information ────────────────────────────────────────
    business_type = models.CharField(
        max_length=30,
        choices=BUSINESS_TYPE_CHOICES,
        default=BUSINESS_TYPE_OTHER,
        blank=True,
        help_text=(
            "Legal structure of the business. Used during onboarding "
            "and for compliance reporting. Sri Lanka business types: "
            "Sole Proprietor, Partnership, Pvt Ltd, PLC, Cooperative, NGO."
        ),
    )

    industry = models.CharField(
        max_length=30,
        choices=INDUSTRY_CHOICES,
        default=INDUSTRY_OTHER,
        blank=True,
        help_text=(
            "Industry classification for the tenant. Used for analytics, "
            "reporting, and industry-specific feature recommendations. "
            "Standardized categories covering major Sri Lankan industries."
        ),
    )

    business_registration_number = models.CharField(
        max_length=20,
        blank=True,
        default="",
        validators=[brn_validator],
        help_text=(
            "Sri Lanka Business Registration Number. "
            "Formats: PV 12345 (Private), PB 12345 (Public), "
            "GA 12345 (Guarantee), or numeric (e.g. 123456). "
            "Used for invoicing and regulatory compliance."
        ),
    )

    # ── Primary Contact ─────────────────────────────────────────────
    contact_name = models.CharField(
        max_length=255,
        blank=True,
        default="",
        help_text=(
            "Full name of the primary contact person for this tenant. "
            "Used for account communications and support."
        ),
    )

    contact_email = models.EmailField(
        blank=True,
        default="",
        help_text=(
            "Primary contact email address for the tenant. "
            "Used for billing notifications, system alerts, and support."
        ),
    )

    contact_phone = models.CharField(
        max_length=20,
        blank=True,
        default="",
        validators=[phone_validator],
        help_text=(
            "Primary contact phone number in Sri Lanka format: "
            "+94 XX XXX XXXX or 0XX XXX XXXX. "
            "Used for urgent notifications and account verification."
        ),
    )

    # ── Address ─────────────────────────────────────────────────────
    address_line_1 = models.CharField(
        max_length=255,
        blank=True,
        default="",
        help_text=(
            "Primary address line (street name, building number). "
            "Used for billing documents, invoices, and legal correspondence."
        ),
    )

    address_line_2 = models.CharField(
        max_length=255,
        blank=True,
        default="",
        help_text=(
            "Secondary address line (suite, floor, area). "
            "Optional additional address detail."
        ),
    )

    city = models.CharField(
        max_length=100,
        blank=True,
        default="",
        help_text=(
            "City or town name. Used for regional reporting "
            "and delivery logistics."
        ),
    )

    district = models.CharField(
        max_length=100,
        blank=True,
        default="",
        help_text=(
            "Administrative district (e.g. Colombo, Gampaha, Kandy). "
            "Sri Lanka has 25 districts. Used for regional reporting."
        ),
    )

    province = models.CharField(
        max_length=30,
        blank=True,
        default="",
        choices=PROVINCE_CHOICES,
        help_text=(
            "Sri Lanka province. One of the 9 provinces: "
            "Western, Central, Southern, Northern, Eastern, "
            "North Western, North Central, Uva, Sabaragamuwa."
        ),
    )

    postal_code = models.CharField(
        max_length=10,
        blank=True,
        default="",
        validators=[postal_code_validator],
        help_text=(
            "Sri Lanka postal code (5 digits, e.g. 10100 for Colombo Fort). "
            "Used for delivery routing and regional classification."
        ),
    )

    # ── Branding ────────────────────────────────────────────────────
    logo = models.ImageField(
        upload_to=tenant_logo_upload_path,
        blank=True,
        null=True,
        help_text=(
            "Tenant logo image. Stored at tenants/<schema_name>/branding/. "
            "Used in tenant dashboard, invoices, and webstore header. "
            "Recommended size: 200x200px, max 2MB."
        ),
    )

    primary_color = models.CharField(
        max_length=7,
        blank=True,
        default="#1a73e8",
        validators=[hex_color_validator],
        help_text=(
            "Primary brand color in hex format (e.g. #1a73e8). "
            "Applied to tenant dashboard theme and webstore accents."
        ),
    )

    secondary_color = models.CharField(
        max_length=7,
        blank=True,
        default="#ffffff",
        validators=[hex_color_validator],
        help_text=(
            "Secondary brand color in hex format (e.g. #ffffff). "
            "Applied to backgrounds and secondary UI elements."
        ),
    )

    # ── Locale Preferences ──────────────────────────────────────────
    language = models.CharField(
        max_length=5,
        choices=LANGUAGE_CHOICES,
        default=LANGUAGE_EN,
        help_text=(
            "Default UI language for this tenant. "
            "Supported: English (en), Sinhala (si), Tamil (ta)."
        ),
    )

    timezone = models.CharField(
        max_length=50,
        choices=TIMEZONE_CHOICES,
        default=TIMEZONE_COLOMBO,
        help_text=(
            "Tenant timezone for date/time display and reporting. "
            "Default: Asia/Colombo (IST +05:30)."
        ),
    )

    paid_until = models.DateField(
        null=True,
        blank=True,
        help_text=(
            "Subscription expiry date. Null for the public tenant or "
            "tenants with unlimited access. After this date, the tenant "
            "may be suspended or moved to a limited plan."
        ),
    )

    on_trial = models.BooleanField(
        default=True,
        help_text=(
            "Whether this tenant is currently on a trial period. "
            "Trial tenants may have feature restrictions."
        ),
    )

    # ── Lifecycle Status ────────────────────────────────────────────
    status = models.CharField(
        max_length=20,
        choices=TENANT_STATUS_CHOICES,
        default=TENANT_STATUS_ACTIVE,
        db_index=True,
        help_text=(
            "Tenant lifecycle state. "
            "'active': fully operational. "
            "'suspended': temporarily disabled (e.g. payment overdue). "
            "'archived': permanently deactivated, data retained for compliance."
        ),
    )

    # ── Onboarding Progress ─────────────────────────────────────────
    onboarding_step = models.PositiveSmallIntegerField(
        default=0,
        help_text=(
            "Current onboarding step the tenant has reached. "
            "0 = not started. Each step represents a setup milestone "
            "(e.g. 1=profile, 2=products, 3=payment, 4=launch). "
            "Used by the frontend to resume onboarding where the tenant left off."
        ),
    )

    onboarding_completed = models.BooleanField(
        default=False,
        help_text=(
            "Whether the tenant has completed the onboarding workflow. "
            "Set to True when all onboarding steps have been finished. "
            "Tenants that have not completed onboarding may see a setup wizard."
        ),
    )

    # ── Schema Metadata ─────────────────────────────────────────────
    schema_version = models.CharField(
        max_length=50,
        default="1.0.0",
        help_text=(
            "Tracks the current schema migration version for this tenant. "
            "Used to determine whether the tenant's schema needs migration "
            "updates. Follows semantic versioning (e.g. '1.0.0', '1.1.0')."
        ),
    )

    # ── Per-Tenant Settings ─────────────────────────────────────────
    settings = models.JSONField(
        default=dict,
        blank=True,
        help_text=(
            "Per-tenant configuration stored as JSON. "
            "Expected keys: currency, timezone, date_format, language. "
            "Defaults are applied at the application layer if keys are missing."
        ),
    )

    # ── Timestamps ──────────────────────────────────────────────────
    created_on = models.DateTimeField(
        auto_now_add=True,
        help_text="When this tenant was created.",
    )

    updated_on = models.DateTimeField(
        auto_now=True,
        help_text="When this tenant was last updated.",
    )

    # ── Schema Lifecycle (from TenantMixin) ─────────────────────────
    # auto_create_schema is inherited from TenantMixin.
    # Default is True (set in database.py as AUTO_CREATE_SCHEMA).
    # When True, saving a new Tenant creates the PostgreSQL schema
    # and runs all TENANT_APPS migrations in it.
    auto_create_schema = True

    # ── Manager ─────────────────────────────────────────────────────
    objects = TenantManager()

    class Meta:
        verbose_name = "Tenant"
        verbose_name_plural = "Tenants"
        ordering = ["name"]
        indexes = [
            models.Index(
                fields=["status", "created_on"],
                name="idx_tenant_status_created",
            ),
            models.Index(
                fields=["onboarding_completed"],
                name="idx_tenant_onboarding",
            ),
        ]

    def __str__(self):
        return self.name

    def clean(self):
        """
        Validate tenant fields before saving.

        Ensures:
            1. Slug is not a reserved PostgreSQL schema name (except
               the public tenant, which is allowed to use 'public')
            2. Schema name follows the tenant_<slug> convention
            3. Schema name does not exceed PostgreSQL's 63-char limit
        """
        super().clean()

        # The public tenant (schema_name='public') is exempt from
        # reserved-name validation because it is a required system tenant.
        is_public_tenant = self.schema_name == "public"

        # Validate slug is not a reserved name (skip for public tenant)
        if (
            self.slug
            and self.slug.lower() in RESERVED_SCHEMA_NAMES
            and not is_public_tenant
        ):
            raise ValidationError({
                "slug": f"'{self.slug}' is a reserved name and cannot be used as a tenant slug.",
            })

        # If schema_name is not yet set and slug is available, generate it
        # (public tenant already has schema_name='public', so this is skipped)
        if self.slug and not self.schema_name:
            prefix = getattr(settings, "TENANT_SCHEMA_PREFIX", "tenant_")
            self.schema_name = f"{prefix}{self.slug.replace('-', '_')}"

        # Validate schema_name length (PostgreSQL limit: 63 characters)
        if self.schema_name and len(self.schema_name) > 63:
            raise ValidationError({
                "slug": (
                    f"Generated schema name '{self.schema_name}' exceeds "
                    "PostgreSQL's 63-character limit. Use a shorter slug."
                ),
            })

    def save(self, *args, **kwargs):
        """
        Save the tenant, auto-generating schema_name from slug if needed.

        The public tenant (schema_name='public') skips schema name generation.
        Business tenants get schema_name = tenant_<slug> with hyphens
        converted to underscores for PostgreSQL compatibility.
        """
        # Auto-generate schema_name from slug for non-public tenants
        if self.slug and not self.schema_name:
            prefix = getattr(settings, "TENANT_SCHEMA_PREFIX", "tenant_")
            self.schema_name = f"{prefix}{self.slug.replace('-', '_')}"

        self.full_clean()
        super().save(*args, **kwargs)

    @property
    def is_active(self):
        """Return True if the tenant is in active status."""
        return self.status == TENANT_STATUS_ACTIVE

    @property
    def is_suspended(self):
        """Return True if the tenant is suspended."""
        return self.status == TENANT_STATUS_SUSPENDED

    @property
    def is_archived(self):
        """Return True if the tenant is archived."""
        return self.status == TENANT_STATUS_ARCHIVED

    @property
    def is_paid(self):
        """Return True if the tenant's subscription has not expired."""
        if self.paid_until is None:
            return True  # No expiry date means unlimited access
        return self.paid_until >= timezone.now().date()

    @property
    def is_public(self):
        """Return True if this is the public (shared) tenant."""
        return self.schema_name == "public"

    @property
    def is_onboarded(self):
        """Return True if the tenant has completed onboarding."""
        return self.onboarding_completed

    @property
    def needs_onboarding(self):
        """Return True if the tenant still needs to complete onboarding."""
        return not self.onboarding_completed

    @property
    def has_brn(self):
        """Return True if the tenant has a business registration number."""
        return bool(self.business_registration_number)

    @property
    def has_contact(self):
        """Return True if the tenant has primary contact info set."""
        return bool(self.contact_name and self.contact_email)

    @property
    def has_address(self):
        """Return True if the tenant has a minimal address (line 1 and city)."""
        return bool(self.address_line_1 and self.city)

    @property
    def full_address(self):
        """Return formatted multi-line address string."""
        parts = [
            p for p in [
                self.address_line_1,
                self.address_line_2,
                self.city,
                self.district,
                self.get_province_display() if self.province else "",
                self.postal_code,
            ] if p
        ]
        return ", ".join(parts)

    @property
    def has_branding(self):
        """Return True if the tenant has custom branding (logo or colors)."""
        return bool(self.logo) or self.primary_color != "#1a73e8"

    @property
    def logo_url(self):
        """Return the URL of the tenant logo, or None if not set."""
        if self.logo:
            return self.logo.url
        return None

    def get_setting(self, key, default=None):
        """
        Retrieve a per-tenant setting value.

        Falls back to DEFAULT_TENANT_SETTINGS if the key is not set,
        then to the provided default.
        """
        if self.settings and key in self.settings:
            return self.settings[key]
        return DEFAULT_TENANT_SETTINGS.get(key, default)


# ════════════════════════════════════════════════════════════════════════
# DOMAIN MODEL
# ════════════════════════════════════════════════════════════════════════

class Domain(DomainMixin):
    """
    Maps hostnames and subdomains to tenants for request routing.

    django-tenants uses the Domain model to resolve which tenant a request
    belongs to. When a request arrives, TenantMainMiddleware looks up the
    Host header in the Domain table and activates the corresponding
    tenant's PostgreSQL schema.

    DomainMixin provides:
        - domain (CharField, max_length=253, unique): The hostname or
          subdomain that maps to a tenant. Must not include port numbers
          or 'www' prefix. Examples: 'acme.lankacommerce.lk', 'localhost'.
        - tenant (ForeignKey to TENANT_MODEL, related_name='domains'):
          The tenant this domain belongs to. Each domain belongs to
          exactly one tenant, but a tenant can have multiple domains.
        - is_primary (BooleanField, default=True): Whether this is the
          primary domain for the tenant. Only one domain per tenant
          should be marked as primary. The primary domain is used for
          generating canonical URLs and redirects.

    LankaCommerce adds:
        - domain_type: Platform (system-assigned) vs custom domain
        - is_verified / verified_at: Custom domain verification tracking
        - ssl_status / ssl_expires_at: SSL certificate monitoring
        - metadata: Additional domain configuration (JSONField)
        - created_on / updated_on: Audit timestamps

    Domain routing examples:
        - Public tenant:   domain='localhost'              -> schema: public
        - Public tenant:   domain='lankacommerce.lk'       -> schema: public
        - Business tenant:  domain='acme.lankacommerce.lk'  -> schema: tenant_acme
        - Business tenant:  domain='acme.localhost'          -> schema: tenant_acme

    Settings references:
        - TENANT_DOMAIN_MODEL = "tenants.Domain" (in config/settings/database.py)
        - BASE_TENANT_DOMAIN configured per environment (.env.docker)
    """

    # Domain type constants
    DOMAIN_TYPE_PLATFORM = "platform"
    DOMAIN_TYPE_CUSTOM = "custom"

    DOMAIN_TYPE_CHOICES = [
        (DOMAIN_TYPE_PLATFORM, "Platform Domain"),
        (DOMAIN_TYPE_CUSTOM, "Custom Domain"),
    ]

    # SSL status constants
    SSL_STATUS_NONE = "none"
    SSL_STATUS_PENDING = "pending"
    SSL_STATUS_ACTIVE = "active"
    SSL_STATUS_EXPIRED = "expired"
    SSL_STATUS_FAILED = "failed"

    SSL_STATUS_CHOICES = [
        (SSL_STATUS_NONE, "No SSL"),
        (SSL_STATUS_PENDING, "Pending"),
        (SSL_STATUS_ACTIVE, "Active"),
        (SSL_STATUS_EXPIRED, "Expired"),
        (SSL_STATUS_FAILED, "Failed"),
    ]

    # ── Domain Type ─────────────────────────────────────────────────
    domain_type = models.CharField(
        max_length=20,
        choices=DOMAIN_TYPE_CHOICES,
        default=DOMAIN_TYPE_PLATFORM,
        help_text=(
            "Type of domain. 'platform' domains are system-assigned "
            "subdomains (e.g. acme.lankacommerce.lk). 'custom' domains "
            "are user-provided and require DNS verification."
        ),
    )

    # ── Verification ────────────────────────────────────────────────
    is_verified = models.BooleanField(
        default=False,
        help_text=(
            "Whether this domain has been verified via DNS. "
            "Platform domains are auto-verified. Custom domains "
            "require TXT record verification."
        ),
    )

    verified_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Timestamp when the domain was last successfully verified.",
    )

    # ── SSL Tracking ────────────────────────────────────────────────
    ssl_status = models.CharField(
        max_length=20,
        choices=SSL_STATUS_CHOICES,
        default=SSL_STATUS_NONE,
        help_text=(
            "Current SSL certificate status. "
            "'none': no SSL configured. 'pending': provisioning in progress. "
            "'active': valid certificate. 'expired': certificate expired. "
            "'failed': provisioning failed."
        ),
    )

    ssl_expires_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text=(
            "SSL certificate expiry date. Used for monitoring and "
            "automated renewal. Null when no certificate is provisioned."
        ),
    )

    # ── Metadata ────────────────────────────────────────────────────
    metadata = models.JSONField(
        default=dict,
        blank=True,
        help_text=(
            "Additional domain metadata (DNS records, verification tokens, "
            "CDN configuration, etc.). Structured as a JSON object."
        ),
    )

    # ── Timestamps ──────────────────────────────────────────────────
    created_on = models.DateTimeField(
        auto_now_add=True,
        help_text="When this domain record was created.",
    )

    updated_on = models.DateTimeField(
        auto_now=True,
        help_text="When this domain record was last updated.",
    )

    # ── Manager ─────────────────────────────────────────────────────
    objects = DomainManager()

    class Meta:
        verbose_name = "Domain"
        verbose_name_plural = "Domains"
        ordering = ["domain"]
        indexes = [
            models.Index(
                fields=["domain_type", "is_verified"],
                name="idx_domain_type_verified",
            ),
            models.Index(
                fields=["ssl_status"],
                name="idx_domain_ssl_status",
            ),
        ]

    def __str__(self):
        return self.domain

    @property
    def is_platform_domain(self):
        """Return True if this is a system-assigned platform domain."""
        return self.domain_type == self.DOMAIN_TYPE_PLATFORM

    @property
    def is_custom_domain(self):
        """Return True if this is a user-provided custom domain."""
        return self.domain_type == self.DOMAIN_TYPE_CUSTOM

    @property
    def needs_verification(self):
        """Return True if this custom domain needs DNS verification."""
        return self.is_custom_domain and not self.is_verified

    @property
    def has_ssl(self):
        """Return True if domain has an active SSL certificate."""
        return self.ssl_status == self.SSL_STATUS_ACTIVE


# ═══════════════════════════════════════════════════════════════════════
# TENANT SETTINGS MODEL
# ═══════════════════════════════════════════════════════════════════════


def default_notification_settings():
    """Return default notification settings for a new tenant."""
    return {
        "email_on_order": True,
        "email_on_payment": True,
        "sms_enabled": False,
        "low_stock_alert": True,
    }


def default_feature_settings():
    """Return default feature toggle flags for a new tenant."""
    return {
        "webstore_enabled": True,
        "pos_enabled": True,
        "multi_location": False,
        "advanced_reports": False,
    }


def default_integration_settings():
    """Return default integration configuration for a new tenant."""
    return {
        "payment_gateway": None,
        "accounting_software": None,
        "shipping_provider": None,
    }


class TenantSettings(models.Model):
    """
    Per-tenant configuration settings.

    Each tenant has exactly one TenantSettings record, created automatically
    via a post_save signal when a new Tenant is created. This model stores
    branding preferences, document numbering prefixes, default tax rates,
    footer texts, and JSON-based feature/notification/integration settings
    that apply across the tenant's ERP modules.

    Relationship:
        - OneToOneField to Tenant (related_name='tenant_settings')
        - Auto-created on Tenant creation via signal (see signals.py)

    Fields:
        - tenant: OneToOne FK to Tenant
        - theme_color: Hex color for tenant branding (#1E40AF default)
        - invoice_prefix: Prefix for invoice numbers (default: INV)
        - order_prefix: Prefix for order numbers (default: ORD)
        - tax_rate: Default tax rate as decimal (default: 0.00)
        - invoice_footer: Footer text for invoices (default: blank)
        - receipt_footer: Footer text for receipts (default: Thank you...)
        - notification_settings: JSON notification preferences
        - feature_settings: JSON feature toggle flags
        - integration_settings: JSON third-party integration config
        - created_on / updated_on: Audit timestamps
    """

    # ── Relationship ────────────────────────────────────────────────
    tenant = models.OneToOneField(
        "tenants.Tenant",
        on_delete=models.CASCADE,
        related_name="tenant_settings",
        help_text="The tenant this settings record belongs to.",
    )

    # ── Branding ────────────────────────────────────────────────────
    theme_color = models.CharField(
        max_length=7,
        default="#1E40AF",
        validators=[hex_color_validator],
        help_text=(
            "Primary brand color for the tenant's UI theme. "
            "Must be a valid hex color code (e.g. #1E40AF). "
            "Applied to headers, buttons, and accent elements."
        ),
    )

    # ── Document Prefixes ───────────────────────────────────────────
    invoice_prefix = models.CharField(
        max_length=10,
        default="INV",
        help_text=(
            "Prefix for invoice numbers. Combined with a sequential "
            "number to generate invoice IDs (e.g. INV-0001, INV-0002)."
        ),
    )

    order_prefix = models.CharField(
        max_length=10,
        default="ORD",
        help_text=(
            "Prefix for order numbers. Combined with a sequential "
            "number to generate order IDs (e.g. ORD-0001, ORD-0002)."
        ),
    )

    # ── Tax Configuration ───────────────────────────────────────────
    tax_rate = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=0,
        help_text=(
            "Default tax rate as a percentage (e.g. 8.00 for 8%). "
            "Applied to new products and invoices when no specific "
            "tax rate is configured. Sri Lanka standard VAT is "
            "typically set per business requirements."
        ),
    )

    # ── Footer Text Fields ──────────────────────────────────────────
    invoice_footer = models.TextField(
        default="",
        blank=True,
        help_text=(
            "Footer text printed on invoices. Supports plain text. "
            "Commonly used for payment terms, bank details, or legal "
            "disclaimers. Leave blank for no footer."
        ),
    )

    receipt_footer = models.TextField(
        default="Thank you for your purchase!",
        blank=True,
        help_text=(
            "Footer text printed on receipts. Supports plain text. "
            "Commonly used for thank-you messages, return policies, "
            "or promotional messages."
        ),
    )

    # ── JSON Settings Fields ────────────────────────────────────────
    notification_settings = models.JSONField(
        default=default_notification_settings,
        blank=True,
        help_text=(
            "Notification preferences for the tenant. Controls email, "
            "SMS, and alert notifications. Expected keys: "
            "email_on_order (bool), email_on_payment (bool), "
            "sms_enabled (bool), low_stock_alert (bool)."
        ),
    )

    feature_settings = models.JSONField(
        default=default_feature_settings,
        blank=True,
        help_text=(
            "Feature toggle flags for the tenant. Controls which "
            "modules and capabilities are enabled. Expected keys: "
            "webstore_enabled (bool), pos_enabled (bool), "
            "multi_location (bool), advanced_reports (bool)."
        ),
    )

    integration_settings = models.JSONField(
        default=default_integration_settings,
        blank=True,
        help_text=(
            "Integration configuration for the tenant. Stores "
            "third-party service settings. Expected keys: "
            "payment_gateway (str|null), accounting_software (str|null), "
            "shipping_provider (str|null)."
        ),
    )

    # ── Timestamps ──────────────────────────────────────────────────
    created_on = models.DateTimeField(
        auto_now_add=True,
        help_text="When this settings record was created.",
    )

    updated_on = models.DateTimeField(
        auto_now=True,
        help_text="When this settings record was last updated.",
    )

    class Meta:
        verbose_name = "Tenant Settings"
        verbose_name_plural = "Tenant Settings"

    def __str__(self):
        return f"Settings for {self.tenant.name}"


# ═══════════════════════════════════════════════════════════════════════
# TENANT SUBSCRIPTION MODEL
# ═══════════════════════════════════════════════════════════════════════


# Subscription status constants
SUBSCRIPTION_STATUS_TRIAL = "trial"
SUBSCRIPTION_STATUS_ACTIVE = "active"
SUBSCRIPTION_STATUS_EXPIRED = "expired"
SUBSCRIPTION_STATUS_CANCELLED = "cancelled"
SUBSCRIPTION_STATUS_SUSPENDED = "suspended"

SUBSCRIPTION_STATUS_CHOICES = [
    (SUBSCRIPTION_STATUS_TRIAL, "Trial"),
    (SUBSCRIPTION_STATUS_ACTIVE, "Active"),
    (SUBSCRIPTION_STATUS_EXPIRED, "Expired"),
    (SUBSCRIPTION_STATUS_CANCELLED, "Cancelled"),
    (SUBSCRIPTION_STATUS_SUSPENDED, "Suspended"),
]

# Billing cycle constants
BILLING_CYCLE_MONTHLY = "monthly"
BILLING_CYCLE_ANNUAL = "annual"

BILLING_CYCLE_CHOICES = [
    (BILLING_CYCLE_MONTHLY, "Monthly"),
    (BILLING_CYCLE_ANNUAL, "Annual"),
]


class TenantSubscription(models.Model):
    """
    Tracks tenant subscription state, billing cycle, and payment info.

    Each tenant can have multiple subscription records over time (e.g.
    when they upgrade, downgrade, or renew). The most recent active
    subscription determines the tenant's current plan and capabilities.

    All monetary amounts are stored in LKR (Sri Lankan Rupee, ₨).

    Relationships:
        - ForeignKey to Tenant (related_name='subscriptions')
        - ForeignKey to SubscriptionPlan in platform app
          (related_name='tenant_subscriptions')

    Lifecycle Statuses:
        - trial: Active trial period (free access)
        - active: Paid subscription, currently active
        - expired: Subscription period ended, not renewed
        - cancelled: User-initiated cancellation
        - suspended: Admin-initiated suspension

    Status Transitions:
        trial -> active (payment received)
        trial -> expired (trial period ended without payment)
        active -> expired (billing period ended)
        active -> cancelled (user cancels)
        active -> suspended (admin suspends)
        expired -> active (payment received, renewal)
        cancelled -> active (re-subscription)
        suspended -> active (admin reinstates)

    Fields:
        - tenant: FK to Tenant
        - plan: FK to SubscriptionPlan (nullable for legacy)
        - status: Current subscription lifecycle state
        - billing_cycle: Monthly or annual billing
        - started_at: When the subscription was activated
        - expires_at: When the current billing period ends
        - trial_ends_at: When the trial period ends
        - next_billing_date: Next scheduled billing date
        - amount: Current billing amount in LKR (₨)
        - payment_method: Payment method (card/bank_transfer/mobile)
        - is_auto_renew: Whether subscription auto-renews
        - created_on / updated_on: Audit timestamps
    """

    # ── Relationships ───────────────────────────────────────────────
    tenant = models.ForeignKey(
        "tenants.Tenant",
        on_delete=models.CASCADE,
        related_name="subscriptions",
        help_text="The tenant this subscription belongs to.",
    )

    plan = models.ForeignKey(
        "platform.SubscriptionPlan",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="tenant_subscriptions",
        help_text=(
            "The subscription plan this subscription is based on. "
            "Null for legacy or migrated subscriptions."
        ),
    )

    # ── Status ──────────────────────────────────────────────────────
    status = models.CharField(
        max_length=20,
        choices=SUBSCRIPTION_STATUS_CHOICES,
        default=SUBSCRIPTION_STATUS_TRIAL,
        db_index=True,
        help_text=(
            "Current subscription lifecycle state. "
            "'trial': free trial period. 'active': paid and current. "
            "'expired': billing period ended. 'cancelled': user cancelled. "
            "'suspended': admin suspended."
        ),
    )

    # ── Billing Cycle ───────────────────────────────────────────────
    billing_cycle = models.CharField(
        max_length=20,
        choices=BILLING_CYCLE_CHOICES,
        default=BILLING_CYCLE_MONTHLY,
        help_text=(
            "Billing frequency. 'monthly': billed every month. "
            "'annual': billed yearly with approximately 17%% discount."
        ),
    )

    # ── Date Fields ─────────────────────────────────────────────────
    started_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text=(
            "When this subscription was activated. Set when status "
            "transitions to 'active' or 'trial'. Null for subscriptions "
            "that haven't started yet."
        ),
    )

    expires_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text=(
            "When the current billing period ends. Computed from "
            "started_at + billing_cycle duration. Used for expiration "
            "checks and renewal scheduling."
        ),
    )

    trial_ends_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text=(
            "When the trial period ends. Calculated from started_at + "
            "trial_days (from SubscriptionPlan, default 14 days). "
            "Null if subscription was never on trial."
        ),
    )

    next_billing_date = models.DateTimeField(
        null=True,
        blank=True,
        help_text=(
            "Next scheduled billing date. Updated after each "
            "successful payment. Used for recurring charge scheduling."
        ),
    )

    # ── Billing ─────────────────────────────────────────────────────
    amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        help_text=(
            "Current billing amount in LKR (₨). Derived from the "
            "subscription plan's monthly or annual price. May differ "
            "from plan price if discounts or promotions are applied."
        ),
    )

    payment_method = models.CharField(
        max_length=30,
        default="",
        blank=True,
        help_text=(
            "Payment method used for this subscription. "
            "Common values: 'card', 'bank_transfer', 'mobile_payment'. "
            "Empty if no payment method has been set."
        ),
    )

    is_auto_renew = models.BooleanField(
        default=True,
        help_text=(
            "Whether the subscription auto-renews at the end of "
            "each billing cycle. If False, the subscription expires "
            "and the tenant must manually renew."
        ),
    )

    # ── Timestamps ──────────────────────────────────────────────────
    created_on = models.DateTimeField(
        auto_now_add=True,
        help_text="When this subscription record was created.",
    )

    updated_on = models.DateTimeField(
        auto_now=True,
        help_text="When this subscription record was last updated.",
    )

    # ── Manager ─────────────────────────────────────────────────────
    objects = SubscriptionManager()

    class Meta:
        verbose_name = "Tenant Subscription"
        verbose_name_plural = "Tenant Subscriptions"
        ordering = ["-created_on"]
        indexes = [
            models.Index(
                fields=["tenant", "status"],
                name="idx_subscription_tenant_status",
            ),
            models.Index(
                fields=["expires_at"],
                name="idx_subscription_expires_at",
            ),
        ]

    def __str__(self):
        plan_name = self.plan.name if self.plan else "No Plan"
        return f"{self.tenant.name} - {plan_name} ({self.get_status_display()})"

    @property
    def is_active(self):
        """Return True if subscription is currently active."""
        return self.status == SUBSCRIPTION_STATUS_ACTIVE

    @property
    def is_trial(self):
        """Return True if subscription is in trial period."""
        return self.status == SUBSCRIPTION_STATUS_TRIAL

    @property
    def is_active_or_trial(self):
        """Return True if subscription is active or in trial."""
        return self.status in (
            SUBSCRIPTION_STATUS_ACTIVE,
            SUBSCRIPTION_STATUS_TRIAL,
        )

    @property
    def is_expired(self):
        """Return True if subscription has expired."""
        return self.status == SUBSCRIPTION_STATUS_EXPIRED

    @property
    def is_cancelled(self):
        """Return True if subscription was cancelled."""
        return self.status == SUBSCRIPTION_STATUS_CANCELLED

    @property
    def is_suspended(self):
        """Return True if subscription was suspended by admin."""
        return self.status == SUBSCRIPTION_STATUS_SUSPENDED
