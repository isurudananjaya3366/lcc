"""
Product search serializers for POS.

Provides request/response serialization for product search,
barcode scanning, and quick-button features.
"""

from rest_framework import serializers

from apps.pos.search.models import QuickButton, QuickButtonGroup, SearchHistory


class ProductSearchRequestSerializer(serializers.Serializer):
    """Validates incoming search requests."""

    query = serializers.CharField(max_length=200)
    category = serializers.UUIDField(required=False, allow_null=True)
    limit = serializers.IntegerField(
        required=False, default=20, min_value=1, max_value=100
    )


class ProductSearchResultSerializer(serializers.Serializer):
    """Represents a single product search result."""

    id = serializers.UUIDField(read_only=True)
    name = serializers.CharField(read_only=True)
    sku = serializers.CharField(read_only=True)
    barcode = serializers.CharField(read_only=True)
    selling_price = serializers.DecimalField(
        max_digits=10, decimal_places=2, read_only=True
    )
    cost_price = serializers.DecimalField(
        max_digits=10, decimal_places=2, read_only=True, allow_null=True
    )
    category = serializers.CharField(
        read_only=True, allow_null=True, default=None
    )
    brand = serializers.CharField(
        read_only=True, allow_null=True, default=None
    )
    tax_class = serializers.CharField(
        read_only=True, allow_null=True, default=None
    )
    product_type = serializers.CharField(read_only=True, default="")
    variant_id = serializers.UUIDField(
        read_only=True, allow_null=True, default=None
    )
    variant_sku = serializers.CharField(
        read_only=True, allow_null=True, default=None
    )
    variant_barcode = serializers.CharField(
        read_only=True, allow_null=True, default=None
    )
    variant_name = serializers.CharField(
        read_only=True, allow_null=True, default=None
    )
    search_method = serializers.CharField(read_only=True)
    is_pos_visible = serializers.BooleanField(read_only=True, default=True)

    # Stock availability
    stock_quantity = serializers.DecimalField(
        max_digits=12, decimal_places=3, read_only=True, default=None, allow_null=True
    )
    is_in_stock = serializers.BooleanField(read_only=True, default=None, allow_null=True)
    low_stock_warning = serializers.BooleanField(read_only=True, default=None, allow_null=True)
    can_sell = serializers.BooleanField(read_only=True, default=None, allow_null=True)


class BarcodeScanRequestSerializer(serializers.Serializer):
    """Validates barcode scan input."""

    barcode = serializers.CharField(max_length=100)


class QuickButtonSerializer(serializers.ModelSerializer):
    """Serializer for quick-action buttons."""

    product_name = serializers.CharField(
        source="product.name", read_only=True
    )
    product_sku = serializers.CharField(
        source="product.sku", read_only=True
    )

    class Meta:
        model = QuickButton
        fields = [
            "id",
            "group",
            "product",
            "product_name",
            "product_sku",
            "label",
            "image",
            "color",
            "row",
            "column",
            "quick_quantity",
            "is_active",
        ]
        read_only_fields = ["id"]


class QuickButtonGroupSerializer(serializers.ModelSerializer):
    """Serializer for quick-button groups with nested buttons."""

    buttons = serializers.SerializerMethodField()

    class Meta:
        model = QuickButtonGroup
        fields = [
            "id",
            "name",
            "code",
            "icon",
            "color",
            "description",
            "display_order",
            "rows",
            "columns",
            "is_default",
            "is_active",
            "buttons",
        ]
        read_only_fields = ["id"]

    def get_buttons(self, obj):
        buttons = (
            obj.buttons.filter(is_active=True, is_deleted=False)
            .select_related("product")
            .order_by("row", "column")
        )
        return QuickButtonSerializer(buttons, many=True).data


class SearchHistorySerializer(serializers.ModelSerializer):
    """Read-only serializer for search history."""

    class Meta:
        model = SearchHistory
        fields = [
            "id",
            "query",
            "result_count",
            "search_method",
            "timestamp",
        ]
        read_only_fields = fields
