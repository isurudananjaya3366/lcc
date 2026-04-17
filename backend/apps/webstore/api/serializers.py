"""
Store API serializers for the LankaCommerce webstore.

Adapts internal Product/Category models to the JSON shapes
expected by the Next.js frontend store pages.
"""

from rest_framework import serializers

from apps.products.models import Category, Product, ProductImage, ProductVariant
from apps.products.models.variant_option import VariantOptionValue  # noqa: F401


class StoreProductImageSerializer(serializers.ModelSerializer):
    url = serializers.SerializerMethodField()
    order = serializers.IntegerField(source="display_order")

    class Meta:
        model = ProductImage
        fields = ["id", "url", "alt_text", "is_primary", "order"]

    def get_url(self, obj):
        request = self.context.get("request")
        if obj.image:
            url = obj.image.url
            if request:
                return request.build_absolute_uri(url)
            return url
        return ""


class StoreProductVariantSerializer(serializers.ModelSerializer):
    price = serializers.SerializerMethodField()
    in_stock = serializers.BooleanField(source="is_active")
    attributes = serializers.SerializerMethodField()

    class Meta:
        model = ProductVariant
        fields = ["id", "name", "sku", "price", "in_stock", "attributes"]

    def get_price(self, obj):
        try:
            return float(obj.product.selling_price) if obj.product.selling_price else 0.0
        except Exception:
            return 0.0

    def get_attributes(self, obj):
        attrs = {}
        for ov in obj.option_values.select_related("option_type").all():
            attrs[ov.option_type.name] = ov.value
        return attrs


class StoreCategorySerializer(serializers.ModelSerializer):
    parent_id = serializers.SerializerMethodField()

    class Meta:
        model = Category
        fields = ["id", "name", "slug", "is_active", "parent_id"]

    def get_parent_id(self, obj):
        if obj.parent_id:
            return str(obj.parent_id)
        return None


class StoreProductSerializer(serializers.ModelSerializer):
    id = serializers.CharField()
    price = serializers.SerializerMethodField()
    sale_price = serializers.SerializerMethodField()
    in_stock = serializers.SerializerMethodField()
    stock_quantity = serializers.SerializerMethodField()
    images = StoreProductImageSerializer(many=True, read_only=True)
    variants = serializers.SerializerMethodField()
    rating = serializers.FloatField(default=0.0, read_only=True)
    review_count = serializers.IntegerField(default=0, read_only=True)
    currency = serializers.SerializerMethodField()
    category = serializers.SerializerMethodField()
    created_at = serializers.DateTimeField(source="created_on", read_only=True)
    updated_at = serializers.DateTimeField(source="updated_on", read_only=True)

    class Meta:
        model = Product
        fields = [
            "id",
            "name",
            "slug",
            "sku",
            "description",
            "short_description",
            "price",
            "sale_price",
            "currency",
            "in_stock",
            "stock_quantity",
            "category",
            "images",
            "variants",
            "rating",
            "review_count",
            "created_at",
            "updated_at",
        ]

    def get_price(self, obj):
        return float(obj.selling_price) if obj.selling_price else 0.0

    def get_sale_price(self, obj):
        if obj.mrp and obj.mrp > obj.selling_price:
            return float(obj.selling_price)
        return None

    def get_in_stock(self, obj):
        return obj.status == "active"

    def get_stock_quantity(self, obj):
        # Inventory tracked in inventory app; return placeholder
        return 99

    def get_currency(self, obj):
        return "LKR"

    def get_variants(self, obj):
        variants = obj.variants.filter(is_active=True).prefetch_related(
            "option_values__option_type"
        )
        return StoreProductVariantSerializer(
            variants, many=True, context=self.context
        ).data

    def get_category(self, obj):
        if obj.category:
            return {
                "id": str(obj.category.id),
                "name": obj.category.name,
                "slug": obj.category.slug,
            }
        return None
