"""
Django-filter FilterSets for products app.

Provides advanced filtering capabilities for Product model
including price range, category, brand, and status filters.
"""

import django_filters

from apps.products.models import Product


class ProductFilter(django_filters.FilterSet):
    """
    Advanced filtering for Product model.

    Supports filtering by:
    - category: UUID of the category
    - brand: UUID of the brand
    - product_type: Product type choice
    - status: Product status choice
    - is_webstore_visible: Boolean
    - is_pos_visible: Boolean
    - featured: Boolean
    - min_price / max_price: Selling price range
    """

    category = django_filters.UUIDFilter(field_name="category__id")
    brand = django_filters.UUIDFilter(field_name="brand__id")
    product_type = django_filters.ChoiceFilter(
        choices=Product._meta.get_field("product_type").choices
    )
    status = django_filters.ChoiceFilter(
        choices=Product._meta.get_field("status").choices
    )
    is_webstore_visible = django_filters.BooleanFilter()
    is_pos_visible = django_filters.BooleanFilter()
    featured = django_filters.BooleanFilter()
    min_price = django_filters.NumberFilter(
        field_name="selling_price", lookup_expr="gte"
    )
    max_price = django_filters.NumberFilter(
        field_name="selling_price", lookup_expr="lte"
    )

    class Meta:
        model = Product
        fields = [
            "category",
            "brand",
            "product_type",
            "status",
            "is_webstore_visible",
            "is_pos_visible",
            "featured",
        ]
