"""
Variant generation service for creating product variant combinations.

Provides the ``VariantGenerator`` class which computes the Cartesian
product of configured option values and bulk-creates ``ProductVariant``
instances with auto-generated SKUs and names.
"""

import itertools
import logging
import time
from typing import List, Optional, Tuple

from django.core.exceptions import ValidationError
from django.db import transaction

from apps.products.constants import PRODUCT_TYPES
from apps.products.models.product_variant import (
    ProductOptionConfig,
    ProductVariant,
    ProductVariantOption,
)
from apps.products.models.variant_option import VariantOptionValue
from apps.products.services.config import (
    DEFAULT_SKU_PATTERN,
    SKU_MAX_RETRY,
    SKU_SEPARATOR,
    format_option_value_for_sku,
)

logger = logging.getLogger(__name__)


class VariantGenerator:
    """
    Service for generating product variants from option combinations.

    Uses Cartesian product of configured option values to create all
    possible variant combinations with auto-generated SKUs.

    Usage::

        generator = VariantGenerator(product)
        is_valid, error = generator.validate_combinations()
        if is_valid:
            variants = generator.generate_variants()
    """

    def __init__(self, product):
        """
        Initialise with a parent product.

        Args:
            product: A ``Product`` instance (should be VARIABLE type).
        """
        self.product = product

    # ── Validation ──────────────────────────────────────────────────

    def validate_combinations(self) -> Tuple[bool, Optional[str]]:
        """
        Validate that the product can have variants generated.

        Checks:
        1. Product type is VARIABLE.
        2. Product has at least one ``ProductOptionConfig``.
        3. Each configured option type has at least one active value.
        4. At least one option type has 2+ active values.

        Returns:
            Tuple of ``(True, None)`` on success or
            ``(False, error_message)`` on failure.
        """
        if self.product.product_type != PRODUCT_TYPES.VARIABLE:
            return (
                False,
                "Product must be VARIABLE type to have variants",
            )

        configs = (
            ProductOptionConfig.objects.filter(product=self.product)
            .select_related("option_type")
            .order_by("display_order")
        )

        if not configs.exists():
            return (False, "Product has no option configurations")

        for config in configs:
            values_count = config.option_type.values.filter(
                is_active=True
            ).count()
            if values_count == 0:
                return (
                    False,
                    f"Option type '{config.option_type.name}' "
                    f"has no values defined",
                )

        has_multiple = any(
            config.option_type.values.filter(is_active=True).count() >= 2
            for config in configs
        )
        if not has_multiple:
            return (
                False,
                "Need at least one option type with 2+ values",
            )

        return (True, None)

    # ── Combination Generation ──────────────────────────────────────

    def get_combinations(self) -> List[List[VariantOptionValue]]:
        """
        Compute the Cartesian product of all configured option values.

        Returns:
            List of lists — each inner list is one variant's option
            values (one value per option type), ordered by the option
            type's ``display_order``.
        """
        configs = (
            ProductOptionConfig.objects.filter(product=self.product)
            .select_related("option_type")
            .order_by("display_order")
        )

        option_groups: list[list[VariantOptionValue]] = []
        for config in configs:
            values = list(
                config.option_type.values.filter(is_active=True).order_by(
                    "display_order", "value"
                )
            )
            if values:
                option_groups.append(values)

        if not option_groups:
            return []

        combinations = list(itertools.product(*option_groups))
        return [list(combo) for combo in combinations]

    # ── SKU Generation ──────────────────────────────────────────────

    def generate_sku(
        self, option_values: List[VariantOptionValue],
        pattern: str = DEFAULT_SKU_PATTERN,
    ) -> str:
        """
        Generate a unique SKU for a variant combination.

        Uses ``pattern`` (defaults to ``DEFAULT_SKU_PATTERN``) to
        format the SKU.  The pattern is expected to contain
        ``{product_sku}`` and ``{options}`` placeholders.

        Args:
            option_values: Ordered list of option values for one
                variant combination.
            pattern: SKU pattern string with ``{product_sku}`` and
                ``{options}`` placeholders.

        Returns:
            A unique SKU string.
        """
        option_codes = [
            format_option_value_for_sku(ov.value) for ov in option_values
        ]
        options_str = SKU_SEPARATOR.join(option_codes)
        base_sku = pattern.format(
            product_sku=self.product.sku,
            options=options_str,
        )
        return self.get_unique_sku(base_sku)

    def check_sku_unique(self, sku: str) -> bool:
        """Return True if no existing variant uses this SKU."""
        return not ProductVariant.objects.filter(sku=sku).exists()

    def get_unique_sku(self, base_sku: str) -> str:
        """
        Return a guaranteed-unique SKU.

        If ``base_sku`` is already taken, appends ``-2``, ``-3``, etc.
        up to ``SKU_MAX_RETRY``.

        Raises:
            ValueError: If all counter attempts are exhausted.
        """
        if self.check_sku_unique(base_sku):
            return base_sku

        for counter in range(2, SKU_MAX_RETRY + 2):
            candidate = f"{base_sku}{SKU_SEPARATOR}{counter}"
            if self.check_sku_unique(candidate):
                return candidate

        raise ValueError(
            f"Cannot generate unique SKU for base: {base_sku}"
        )

    # ── Variant Creation ────────────────────────────────────────────

    def generate_variants(self) -> List[ProductVariant]:
        """
        Validate, compute combinations, and create all variants.

        Returns:
            List of created ``ProductVariant`` instances.

        Raises:
            ValidationError: If validation fails.
        """
        is_valid, error = self.validate_combinations()
        if not is_valid:
            raise ValidationError(error)

        combinations = self.get_combinations()
        if not combinations:
            return []

        return self.bulk_create_variants(combinations)

    def bulk_create_variants(
        self, combinations: List[List[VariantOptionValue]]
    ) -> List[ProductVariant]:
        """
        Bulk-create variants and their option links in a transaction.

        Args:
            combinations: Output from ``get_combinations()``.

        Returns:
            List of created ``ProductVariant`` instances.
        """
        start_time = time.time()

        with transaction.atomic():
            # Prepare variant objects
            variants_to_create: list[ProductVariant] = []
            combo_map: list[list[VariantOptionValue]] = []

            for idx, combination in enumerate(combinations):
                sku = self.generate_sku(combination)
                variant = ProductVariant(
                    product=self.product,
                    sku=sku,
                    sort_order=idx * 10,
                )
                variants_to_create.append(variant)
                combo_map.append(combination)

            # Bulk create variants
            created_variants = ProductVariant.objects.bulk_create(
                variants_to_create, batch_size=500
            )

            # Bulk create M2M through-model links
            option_links: list[ProductVariantOption] = []
            for variant, combination in zip(
                created_variants, combo_map
            ):
                for opt_idx, option_value in enumerate(combination):
                    option_links.append(
                        ProductVariantOption(
                            variant=variant,
                            option_value=option_value,
                            display_order=opt_idx * 10,
                        )
                    )

            ProductVariantOption.objects.bulk_create(
                option_links, batch_size=500
            )

            # Generate names from options
            for variant in created_variants:
                variant.generate_name_from_options()

        elapsed = time.time() - start_time
        logger.info(
            "Created %d variants for product '%s' in %.2fs",
            len(created_variants),
            self.product.name,
            elapsed,
        )

        return created_variants
