"""
LankaCommerce Cloud - Tenant Manager and QuerySets.

Provides custom manager and queryset helpers for the Tenant, Domain,
and TenantSubscription models, enabling efficient filtering by
lifecycle status, billing state, onboarding progress, subscription
expiry, domain type, verification, and SSL status.

Usage (Tenant):
    Tenant.objects.active()           -> Active tenants only
    Tenant.objects.suspended()        -> Suspended tenants only
    Tenant.objects.archived()         -> Archived tenants only
    Tenant.objects.on_trial()         -> Tenants currently on trial
    Tenant.objects.paid()             -> Tenants with valid subscription
    Tenant.objects.expired()          -> Tenants with expired subscription
    Tenant.objects.needs_onboarding() -> Tenants not yet onboarded
    Tenant.objects.onboarded()        -> Tenants that completed onboarding
    Tenant.objects.business()         -> Non-public tenants only

Usage (Domain):
    Domain.objects.platform()         -> Platform (system) domains
    Domain.objects.custom()           -> Custom (user-provided) domains
    Domain.objects.verified()         -> Verified domains
    Domain.objects.unverified()       -> Unverified domains
    Domain.objects.active_domains()   -> Verified + SSL active domains
    Domain.objects.needs_verification() -> Custom domains needing DNS verification
    Domain.objects.ssl_active()       -> Domains with active SSL
    Domain.objects.ssl_expiring_soon()-> SSL certificates expiring within 30 days
    Domain.objects.primary()          -> Primary domains only

Usage (TenantSubscription):
    TenantSubscription.objects.active()           -> Active subscriptions
    TenantSubscription.objects.trial()            -> Trial subscriptions
    TenantSubscription.objects.active_or_trial()  -> Active or trial
    TenantSubscription.objects.expired()          -> Expired subscriptions
    TenantSubscription.objects.cancelled()        -> Cancelled subscriptions
    TenantSubscription.objects.suspended()        -> Suspended subscriptions
    TenantSubscription.objects.auto_renew()       -> Auto-renew enabled
    TenantSubscription.objects.expiring_soon()    -> Expiring within 30 days
    TenantSubscription.objects.for_tenant(tenant) -> Subscriptions for tenant
"""

from datetime import timedelta

from django.db import models
from django.utils import timezone


class TenantQuerySet(models.QuerySet):
    """
    Custom queryset for Tenant model with chainable filter helpers.

    All methods return querysets, so they can be chained together:
        Tenant.objects.active().paid().onboarded()
    """

    # ── Lifecycle Status Filters ────────────────────────────────────

    def active(self):
        """Return only tenants with active status."""
        return self.filter(status="active")

    def suspended(self):
        """Return only tenants with suspended status."""
        return self.filter(status="suspended")

    def archived(self):
        """Return only tenants with archived status."""
        return self.filter(status="archived")

    def not_archived(self):
        """Return tenants that are not archived (active or suspended)."""
        return self.exclude(status="archived")

    # ── Billing Status Filters ──────────────────────────────────────

    def on_trial(self):
        """Return tenants currently on a trial period."""
        return self.filter(on_trial=True)

    def not_on_trial(self):
        """Return tenants that are not on trial."""
        return self.filter(on_trial=False)

    def paid(self):
        """
        Return tenants with a valid (non-expired) subscription.

        Includes tenants with no expiry date (paid_until=None),
        which indicates unlimited access.
        """
        return self.filter(
            models.Q(paid_until__isnull=True)
            | models.Q(paid_until__gte=timezone.now().date())
        )

    def expired(self):
        """
        Return tenants whose subscription has expired.

        Only includes tenants that have a paid_until date set
        and that date is in the past.
        """
        return self.filter(
            paid_until__isnull=False,
            paid_until__lt=timezone.now().date(),
        )

    # ── Onboarding Filters ──────────────────────────────────────────

    def onboarded(self):
        """Return tenants that have completed the onboarding workflow."""
        return self.filter(onboarding_completed=True)

    def needs_onboarding(self):
        """Return tenants that have not completed onboarding."""
        return self.filter(onboarding_completed=False)

    # ── Tenant Type Filters ─────────────────────────────────────────

    def business(self):
        """
        Return only business tenants (excludes the public tenant).

        The public tenant has schema_name='public' and hosts shared
        platform data. Business tenants have schema_name starting
        with the tenant prefix (e.g. 'tenant_acme').
        """
        return self.exclude(schema_name="public")

    def public_only(self):
        """Return only the public tenant."""
        return self.filter(schema_name="public")


class TenantManager(models.Manager):
    """
    Custom manager for the Tenant model.

    Exposes all TenantQuerySet methods at the manager level so they
    can be called directly as Tenant.objects.active() etc.

    The default queryset returns all tenants (no implicit filtering).
    """

    def get_queryset(self):
        """Return the custom TenantQuerySet."""
        return TenantQuerySet(self.model, using=self._db)

    def active(self):
        """Shortcut: return active tenants."""
        return self.get_queryset().active()

    def suspended(self):
        """Shortcut: return suspended tenants."""
        return self.get_queryset().suspended()

    def archived(self):
        """Shortcut: return archived tenants."""
        return self.get_queryset().archived()

    def not_archived(self):
        """Shortcut: return non-archived tenants."""
        return self.get_queryset().not_archived()

    def on_trial(self):
        """Shortcut: return trial tenants."""
        return self.get_queryset().on_trial()

    def not_on_trial(self):
        """Shortcut: return non-trial tenants."""
        return self.get_queryset().not_on_trial()

    def paid(self):
        """Shortcut: return tenants with valid subscription."""
        return self.get_queryset().paid()

    def expired(self):
        """Shortcut: return tenants with expired subscription."""
        return self.get_queryset().expired()

    def onboarded(self):
        """Shortcut: return onboarded tenants."""
        return self.get_queryset().onboarded()

    def needs_onboarding(self):
        """Shortcut: return tenants needing onboarding."""
        return self.get_queryset().needs_onboarding()

    def business(self):
        """Shortcut: return business tenants (excludes public)."""
        return self.get_queryset().business()

    def public_only(self):
        """Shortcut: return public tenant only."""
        return self.get_queryset().public_only()


# ════════════════════════════════════════════════════════════════════════
# DOMAIN QUERYSET & MANAGER
# ════════════════════════════════════════════════════════════════════════


class DomainQuerySet(models.QuerySet):
    """
    Custom queryset for Domain model with chainable filter helpers.

    All methods return querysets, so they can be chained together:
        Domain.objects.custom().verified().ssl_active()
    """

    # ── Domain Type Filters ─────────────────────────────────────────

    def platform(self):
        """Return only platform (system-assigned) domains."""
        return self.filter(domain_type="platform")

    def custom(self):
        """Return only custom (user-provided) domains."""
        return self.filter(domain_type="custom")

    # ── Verification Filters ────────────────────────────────────────

    def verified(self):
        """Return only verified domains."""
        return self.filter(is_verified=True)

    def unverified(self):
        """Return only unverified domains."""
        return self.filter(is_verified=False)

    def needs_verification(self):
        """Return custom domains that are not yet verified."""
        return self.filter(domain_type="custom", is_verified=False)

    # ── SSL Filters ─────────────────────────────────────────────────

    def ssl_active(self):
        """Return domains with active SSL certificates."""
        return self.filter(ssl_status="active")

    def ssl_expiring_soon(self, days=30):
        """Return domains with SSL certificates expiring within given days."""
        threshold = timezone.now() + timedelta(days=days)
        return self.filter(
            ssl_status="active",
            ssl_expires_at__isnull=False,
            ssl_expires_at__lte=threshold,
        )

    def ssl_expired(self):
        """Return domains with expired SSL certificates."""
        return self.filter(ssl_status="expired")

    def ssl_pending(self):
        """Return domains with pending SSL certificate provisioning."""
        return self.filter(ssl_status="pending")

    # ── Composite Filters ───────────────────────────────────────────

    def active_domains(self):
        """Return verified domains with active SSL (fully operational)."""
        return self.filter(is_verified=True, ssl_status="active")

    def primary(self):
        """Return primary domains only."""
        return self.filter(is_primary=True)

    def for_tenant(self, tenant):
        """Return domains belonging to a specific tenant."""
        return self.filter(tenant=tenant)


class DomainManager(models.Manager):
    """
    Custom manager for Domain model.

    Exposes DomainQuerySet methods at the manager level for convenience:
        Domain.objects.platform()          -> Platform domains
        Domain.objects.custom()            -> Custom domains
        Domain.objects.verified()          -> Verified domains
        Domain.objects.active_domains()    -> Verified + SSL active
        Domain.objects.needs_verification()-> Custom needing DNS check
    """

    def get_queryset(self):
        """Return DomainQuerySet for all manager operations."""
        return DomainQuerySet(self.model, using=self._db)

    # ── Domain Type Shortcuts ───────────────────────────────────────

    def platform(self):
        """Shortcut: return platform domains."""
        return self.get_queryset().platform()

    def custom(self):
        """Shortcut: return custom domains."""
        return self.get_queryset().custom()

    # ── Verification Shortcuts ──────────────────────────────────────

    def verified(self):
        """Shortcut: return verified domains."""
        return self.get_queryset().verified()

    def unverified(self):
        """Shortcut: return unverified domains."""
        return self.get_queryset().unverified()

    def needs_verification(self):
        """Shortcut: return custom domains needing verification."""
        return self.get_queryset().needs_verification()

    # ── SSL Shortcuts ───────────────────────────────────────────────

    def ssl_active(self):
        """Shortcut: return domains with active SSL."""
        return self.get_queryset().ssl_active()

    def ssl_expiring_soon(self, days=30):
        """Shortcut: return domains with SSL expiring soon."""
        return self.get_queryset().ssl_expiring_soon(days=days)

    def ssl_expired(self):
        """Shortcut: return domains with expired SSL."""
        return self.get_queryset().ssl_expired()

    def ssl_pending(self):
        """Shortcut: return domains with pending SSL."""
        return self.get_queryset().ssl_pending()

    # ── Composite Shortcuts ─────────────────────────────────────────

    def active_domains(self):
        """Shortcut: return verified + SSL active domains."""
        return self.get_queryset().active_domains()

    def primary(self):
        """Shortcut: return primary domains only."""
        return self.get_queryset().primary()

    def for_tenant(self, tenant):
        """Shortcut: return domains for a specific tenant."""
        return self.get_queryset().for_tenant(tenant)


# ═══════════════════════════════════════════════════════════════════════
# SUBSCRIPTION QUERYSET & MANAGER
# ═══════════════════════════════════════════════════════════════════════


class SubscriptionQuerySet(models.QuerySet):
    """
    Custom queryset for TenantSubscription model with chainable filters.

    All methods return querysets, so they can be chained:
        TenantSubscription.objects.active().auto_renew()
    """

    # ── Status Filters ──────────────────────────────────────────────

    def active(self):
        """Return subscriptions with active status."""
        return self.filter(status="active")

    def trial(self):
        """Return subscriptions in trial period."""
        return self.filter(status="trial")

    def active_or_trial(self):
        """Return subscriptions that are active or in trial."""
        return self.filter(status__in=["active", "trial"])

    def expired(self):
        """Return expired subscriptions."""
        return self.filter(status="expired")

    def cancelled(self):
        """Return cancelled subscriptions."""
        return self.filter(status="cancelled")

    def suspended(self):
        """Return suspended subscriptions."""
        return self.filter(status="suspended")

    # ── Billing Filters ─────────────────────────────────────────────

    def monthly(self):
        """Return subscriptions with monthly billing cycle."""
        return self.filter(billing_cycle="monthly")

    def annual(self):
        """Return subscriptions with annual billing cycle."""
        return self.filter(billing_cycle="annual")

    def auto_renew(self):
        """Return subscriptions with auto-renewal enabled."""
        return self.filter(is_auto_renew=True)

    def no_auto_renew(self):
        """Return subscriptions with auto-renewal disabled."""
        return self.filter(is_auto_renew=False)

    # ── Date-Based Filters ──────────────────────────────────────────

    def expiring_soon(self, days=30):
        """Return subscriptions expiring within given days."""
        threshold = timezone.now() + timedelta(days=days)
        return self.filter(
            status__in=["active", "trial"],
            expires_at__isnull=False,
            expires_at__lte=threshold,
        )

    def trial_ending_soon(self, days=7):
        """Return trial subscriptions ending within given days."""
        threshold = timezone.now() + timedelta(days=days)
        return self.filter(
            status="trial",
            trial_ends_at__isnull=False,
            trial_ends_at__lte=threshold,
        )

    def billing_due(self, days=7):
        """Return subscriptions with billing due within given days."""
        threshold = timezone.now() + timedelta(days=days)
        return self.filter(
            status="active",
            next_billing_date__isnull=False,
            next_billing_date__lte=threshold,
        )

    # ── Tenant Filters ──────────────────────────────────────────────

    def for_tenant(self, tenant):
        """Return subscriptions for a specific tenant."""
        return self.filter(tenant=tenant)

    def current_for_tenant(self, tenant):
        """Return the most recent active/trial subscription for a tenant."""
        return self.filter(
            tenant=tenant,
            status__in=["active", "trial"],
        ).order_by("-created_on")


class SubscriptionManager(models.Manager):
    """
    Custom manager for TenantSubscription model.

    Exposes SubscriptionQuerySet methods at the manager level so they
    can be called directly as TenantSubscription.objects.active(), etc.
    """

    def get_queryset(self):
        """Return SubscriptionQuerySet instead of default QuerySet."""
        return SubscriptionQuerySet(self.model, using=self._db)

    # ── Status Shortcuts ────────────────────────────────────────────

    def active(self):
        """Shortcut: return active subscriptions."""
        return self.get_queryset().active()

    def trial(self):
        """Shortcut: return trial subscriptions."""
        return self.get_queryset().trial()

    def active_or_trial(self):
        """Shortcut: return active or trial subscriptions."""
        return self.get_queryset().active_or_trial()

    def expired(self):
        """Shortcut: return expired subscriptions."""
        return self.get_queryset().expired()

    def cancelled(self):
        """Shortcut: return cancelled subscriptions."""
        return self.get_queryset().cancelled()

    def suspended(self):
        """Shortcut: return suspended subscriptions."""
        return self.get_queryset().suspended()

    # ── Billing Shortcuts ───────────────────────────────────────────

    def monthly(self):
        """Shortcut: return monthly subscriptions."""
        return self.get_queryset().monthly()

    def annual(self):
        """Shortcut: return annual subscriptions."""
        return self.get_queryset().annual()

    def auto_renew(self):
        """Shortcut: return auto-renew subscriptions."""
        return self.get_queryset().auto_renew()

    def no_auto_renew(self):
        """Shortcut: return non-auto-renew subscriptions."""
        return self.get_queryset().no_auto_renew()

    # ── Date-Based Shortcuts ────────────────────────────────────────

    def expiring_soon(self, days=30):
        """Shortcut: return subscriptions expiring soon."""
        return self.get_queryset().expiring_soon(days=days)

    def trial_ending_soon(self, days=7):
        """Shortcut: return trials ending soon."""
        return self.get_queryset().trial_ending_soon(days=days)

    def billing_due(self, days=7):
        """Shortcut: return subscriptions with billing due."""
        return self.get_queryset().billing_due(days=days)

    # ── Tenant Shortcuts ────────────────────────────────────────────

    def for_tenant(self, tenant):
        """Shortcut: return subscriptions for a tenant."""
        return self.get_queryset().for_tenant(tenant)

    def current_for_tenant(self, tenant):
        """Shortcut: return current subscription for a tenant."""
        return self.get_queryset().current_for_tenant(tenant)
