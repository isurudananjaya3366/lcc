"""
DRF Serializers for the products app.

Provides serializers for categories, brands, tax classes,
units of measure, and products with different strategies:
- List serializers: Lightweight for list views
- Detail serializers: Complete info with nested relations
- Create/Update serializers: Validation and business logic
- Tree serializers: Recursive nested structures (categories)
"""

from django.db import transaction
from django.utils.text import slugify
from rest_framework import serializers

from apps.products.models import (
    BillOfMaterials,
    BOMItem,
    Brand,
    BundleItem,
    Category,
    Product,
    ProductBundle,
    ProductOptionConfig,
    ProductVariant,
    ProductVariantOption,
    TaxClass,
    UnitOfMeasure,
    VariantOptionType,
    VariantOptionValue,
)
from apps.products.constants import PRODUCT_TYPES, PRODUCT_STATUS


class CategoryListSerializer(serializers.ModelSerializer):
    """
    Lightweight serializer for category list views.

    Minimal fields optimised for large result sets.
    """

    class Meta:
        model = Category
        fields = [
            "id",
            "name",
            "slug",
            "icon",
            "parent",
            "is_active",
            "display_order",
            "level",
        ]
        read_only_fields = ["id"]


class CategorySerializer(serializers.ModelSerializer):
    """
    Base serializer for Category with common fields.

    Includes parent name for context and children count.
    """

    parent_name = serializers.CharField(
        source="parent.name", read_only=True, default=None
    )
    children_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = Category
        fields = [
            "id",
            "name",
            "slug",
            "parent",
            "parent_name",
            "description",
            "image",
            "icon",
            "is_active",
            "display_order",
            "children_count",
            "created_on",
            "updated_on",
        ]
        read_only_fields = ["id", "created_on", "updated_on"]


class CategoryDetailSerializer(CategorySerializer):
    """
    Detailed serializer including SEO fields and tree info.

    Used for single-category retrieval (GET /categories/{id}/).
    """

    is_root = serializers.BooleanField(read_only=True)
    is_leaf = serializers.BooleanField(read_only=True)
    descendants_count = serializers.IntegerField(read_only=True)
    full_path = serializers.SerializerMethodField()
    children = CategoryListSerializer(many=True, read_only=True, source="get_children")

    class Meta(CategorySerializer.Meta):
        fields = CategorySerializer.Meta.fields + [
            "seo_title",
            "seo_description",
            "seo_keywords",
            "is_root",
            "is_leaf",
            "descendants_count",
            "full_path",
            "children",
        ]

    def get_full_path(self, obj) -> str:
        """Return breadcrumb path string."""
        return obj.get_full_path()


class CategoryTreeSerializer(serializers.ModelSerializer):
    """
    Recursive serializer for the full category tree.

    Each node carries its nested children down to leaf level.
    Used by the ``/categories/tree/`` endpoint.
    """

    children = serializers.SerializerMethodField()

    class Meta:
        model = Category
        fields = [
            "id",
            "name",
            "slug",
            "icon",
            "is_active",
            "display_order",
            "level",
            "children",
        ]

    def get_children(self, obj) -> list:
        """Recursively serialize active children."""
        children_qs = obj.get_children().filter(is_active=True)
        return CategoryTreeSerializer(children_qs, many=True).data


class CategoryCreateUpdateSerializer(serializers.ModelSerializer):
    """
    Serializer for creating and updating categories.

    Handles slug auto-generation and parent validation.
    """

    class Meta:
        model = Category
        fields = [
            "name",
            "slug",
            "parent",
            "description",
            "image",
            "icon",
            "is_active",
            "display_order",
            "seo_title",
            "seo_description",
            "seo_keywords",
        ]
        extra_kwargs = {
            "slug": {"required": False, "allow_blank": True},
        }

    # ── Validation ──────────────────────────────────────────────────

    def validate_parent(self, value):
        """Prevent a category from being set as its own parent."""
        if value and self.instance and value.pk == self.instance.pk:
            raise serializers.ValidationError(
                "A category cannot be its own parent."
            )
        # Prevent moving a category under one of its descendants
        if (
            value
            and self.instance
            and self.instance.is_ancestor_of(value)
        ):
            raise serializers.ValidationError(
                "Cannot move a category under its own descendant."
            )
        return value

    def validate_name(self, value):
        """Ensure name is not empty after stripping."""
        stripped = value.strip()
        if not stripped:
            raise serializers.ValidationError("Category name cannot be blank.")
        return stripped

    # ── Slug auto-generation ────────────────────────────────────────

    def _generate_unique_slug(self, name):
        """Generate a unique slug within the tenant schema."""
        base_slug = slugify(name)
        if not base_slug:
            base_slug = "category"
        slug = base_slug
        counter = 1
        qs = Category.objects.all()
        if self.instance:
            qs = qs.exclude(pk=self.instance.pk)
        while qs.filter(slug=slug).exists():
            counter += 1
            slug = f"{base_slug}-{counter}"
        return slug

    def create(self, validated_data):
        """Create category, auto-generating slug when missing."""
        if not validated_data.get("slug"):
            validated_data["slug"] = self._generate_unique_slug(
                validated_data["name"]
            )
        return super().create(validated_data)

    def update(self, instance, validated_data):
        """Update category, regenerating slug if name changed and slug blank."""
        if not validated_data.get("slug") and "name" in validated_data:
            if validated_data["name"] != instance.name:
                validated_data["slug"] = self._generate_unique_slug(
                    validated_data["name"]
                )
        return super().update(instance, validated_data)


# ════════════════════════════════════════════════════════════════════════
# Brand Serializer
# ════════════════════════════════════════════════════════════════════════


class BrandSerializer(serializers.ModelSerializer):
    """
    Serializer for Brand model.

    Used for list, detail, create, and update operations.
    """

    class Meta:
        model = Brand
        fields = [
            "id",
            "name",
            "slug",
            "logo",
            "description",
            "website",
            "is_active",
        ]
        read_only_fields = ["id", "slug"]


# ════════════════════════════════════════════════════════════════════════
# TaxClass Serializer
# ════════════════════════════════════════════════════════════════════════


class TaxClassSerializer(serializers.ModelSerializer):
    """
    Serializer for TaxClass model.

    Used for list, detail, create, and update operations.
    """

    class Meta:
        model = TaxClass
        fields = [
            "id",
            "name",
            "rate",
            "description",
            "is_default",
            "is_active",
        ]
        read_only_fields = ["id"]


# ════════════════════════════════════════════════════════════════════════
# UnitOfMeasure Serializer
# ════════════════════════════════════════════════════════════════════════


class UnitOfMeasureSerializer(serializers.ModelSerializer):
    """
    Serializer for UnitOfMeasure model.

    Used for list, detail, create, and update operations.
    """

    class Meta:
        model = UnitOfMeasure
        fields = [
            "id",
            "name",
            "symbol",
            "description",
            "conversion_factor",
            "is_base_unit",
            "is_active",
        ]
        read_only_fields = ["id"]


# ════════════════════════════════════════════════════════════════════════
# Product Serializers
# ════════════════════════════════════════════════════════════════════════


class ProductListSerializer(serializers.ModelSerializer):
    """
    Lightweight serializer for product list views.

    Includes source-based fields for category/brand names and
    display values for choices fields.
    """

    category_name = serializers.CharField(
        source="category.name", read_only=True
    )
    brand_name = serializers.CharField(
        source="brand.name", read_only=True, allow_null=True
    )
    product_type_display = serializers.CharField(
        source="get_product_type_display", read_only=True
    )
    status_display = serializers.CharField(
        source="get_status_display", read_only=True
    )

    class Meta:
        model = Product
        fields = [
            "id",
            "name",
            "slug",
            "sku",
            "barcode",
            "category",
            "category_name",
            "brand",
            "brand_name",
            "product_type",
            "product_type_display",
            "status",
            "status_display",
            "cost_price",
            "selling_price",
            "is_webstore_visible",
            "is_pos_visible",
            "featured",
            "created_on",
            "updated_on",
        ]
        read_only_fields = ["id", "slug", "created_on", "updated_on"]


class ProductDetailSerializer(serializers.ModelSerializer):
    """
    Detailed serializer for single product retrieval.

    Includes nested related objects and all product fields.
    """

    category = CategorySerializer(read_only=True)
    brand = BrandSerializer(read_only=True, allow_null=True)
    tax_class = TaxClassSerializer(read_only=True, allow_null=True)
    unit_of_measure = UnitOfMeasureSerializer(read_only=True, allow_null=True)
    product_type_display = serializers.CharField(
        source="get_product_type_display", read_only=True
    )
    status_display = serializers.CharField(
        source="get_status_display", read_only=True
    )

    class Meta:
        model = Product
        fields = [
            "id",
            "name",
            "slug",
            "sku",
            "barcode",
            "description",
            "short_description",
            "category",
            "brand",
            "product_type",
            "product_type_display",
            "status",
            "status_display",
            "is_webstore_visible",
            "is_pos_visible",
            "featured",
            "tax_class",
            "unit_of_measure",
            "cost_price",
            "selling_price",
            "mrp",
            "wholesale_price",
            "weight",
            "length",
            "width",
            "height",
            "seo_title",
            "seo_description",
            "created_on",
            "updated_on",
        ]
        read_only_fields = ["id", "slug", "created_on", "updated_on"]


class ProductCreateSerializer(serializers.ModelSerializer):
    """
    Serializer for creating and updating products.

    Handles SKU auto-generation, slug generation, and uniqueness validation.
    """

    class Meta:
        model = Product
        fields = [
            "name",
            "slug",
            "sku",
            "barcode",
            "description",
            "short_description",
            "category",
            "brand",
            "product_type",
            "status",
            "is_webstore_visible",
            "is_pos_visible",
            "featured",
            "tax_class",
            "unit_of_measure",
            "cost_price",
            "selling_price",
            "mrp",
            "wholesale_price",
            "weight",
            "length",
            "width",
            "height",
            "seo_title",
            "seo_description",
        ]
        extra_kwargs = {
            "sku": {"required": False, "allow_blank": True},
            "slug": {"required": False, "allow_blank": True},
            "brand": {"required": False, "allow_null": True},
            "barcode": {
                "required": False,
                "allow_blank": True,
                "allow_null": True,
            },
        }

    # ── Validation ──────────────────────────────────────────────────

    def validate_sku(self, value):
        """Ensure SKU is unique (exclude current instance on update)."""
        if not value:
            return value
        qs = Product.objects.filter(sku=value)
        if self.instance:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise serializers.ValidationError(
                "A product with this SKU already exists."
            )
        return value

    def validate_barcode(self, value):
        """Ensure barcode is unique (exclude current instance on update)."""
        if not value:
            return value
        qs = Product.objects.filter(barcode=value)
        if self.instance:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise serializers.ValidationError(
                "A product with this barcode already exists."
            )
        return value

    # ── SKU Generation ──────────────────────────────────────────────

    def _generate_sku(self, category):
        """
        Auto-generate a unique SKU based on category.

        Format: PRD-{CATEGORY_CODE}-{NUMBER:05d}
        where CATEGORY_CODE is the first 4 chars of the category slug
        uppercased, and NUMBER is an auto-incrementing counter.
        """
        category_code = category.slug[:4].upper() if category.slug else "GNRL"
        prefix = f"PRD-{category_code}-"
        last_product = (
            Product.objects.filter(sku__startswith=prefix)
            .order_by("-sku")
            .first()
        )
        if last_product:
            try:
                last_number = int(last_product.sku.split("-")[-1])
                next_number = last_number + 1
            except (ValueError, IndexError):
                next_number = 1
        else:
            next_number = 1
        return f"{prefix}{next_number:05d}"

    # ── Slug Generation ─────────────────────────────────────────────

    def _generate_unique_slug(self, name):
        """Generate a unique slug for the product."""
        base_slug = slugify(name)
        if not base_slug:
            base_slug = "product"
        slug = base_slug
        counter = 1
        qs = Product.objects.all()
        if self.instance:
            qs = qs.exclude(pk=self.instance.pk)
        while qs.filter(slug=slug).exists():
            counter += 1
            slug = f"{base_slug}-{counter}"
        return slug

    # ── Create / Update ─────────────────────────────────────────────

    @transaction.atomic
    def create(self, validated_data):
        """Create product with auto-generated SKU and slug if blank."""
        if not validated_data.get("sku"):
            validated_data["sku"] = self._generate_sku(
                validated_data["category"]
            )
        if not validated_data.get("slug"):
            validated_data["slug"] = self._generate_unique_slug(
                validated_data["name"]
            )
        return super().create(validated_data)

    def update(self, instance, validated_data):
        """Update product, regenerating slug if name changed and slug blank."""
        if not validated_data.get("slug") and "name" in validated_data:
            if validated_data["name"] != instance.name:
                validated_data["slug"] = self._generate_unique_slug(
                    validated_data["name"]
                )
        return super().update(instance, validated_data)


# ════════════════════════════════════════════════════════════════════════
# Variant Option Type Serializer
# ════════════════════════════════════════════════════════════════════════


class VariantOptionTypeSerializer(serializers.ModelSerializer):
    """
    Serializer for VariantOptionType model.

    Includes computed ``value_count`` field showing number of values
    defined for the option type.
    """

    value_count = serializers.SerializerMethodField()

    class Meta:
        model = VariantOptionType
        fields = [
            "id",
            "name",
            "slug",
            "display_order",
            "is_color_swatch",
            "is_image_swatch",
            "is_active",
            "value_count",
            "created_on",
            "updated_on",
        ]
        read_only_fields = ["id", "slug", "created_on", "updated_on"]

    def get_value_count(self, obj) -> int:
        """Return number of option values for this type."""
        return obj.values.count()


# ════════════════════════════════════════════════════════════════════════
# Variant Option Value Serializer
# ════════════════════════════════════════════════════════════════════════


class VariantOptionValueSerializer(serializers.ModelSerializer):
    """
    Serializer for VariantOptionValue with swatch handling.

    Includes the parent option type name and a swatch preview
    for frontend rendering.
    """

    option_type_name = serializers.CharField(
        source="option_type.name", read_only=True
    )
    swatch_preview = serializers.SerializerMethodField()

    class Meta:
        model = VariantOptionValue
        fields = [
            "id",
            "option_type",
            "option_type_name",
            "value",
            "label",
            "color_code",
            "image",
            "display_order",
            "is_active",
            "swatch_preview",
            "created_on",
            "updated_on",
        ]
        read_only_fields = ["id", "created_on", "updated_on"]

    def get_swatch_preview(self, obj) -> dict | None:
        """Return swatch representation for frontend rendering."""
        if obj.image:
            try:
                return {"type": "image", "url": obj.image.url}
            except ValueError:
                pass
        if obj.color_code:
            return {"type": "color", "value": obj.color_code}
        return None


# ════════════════════════════════════════════════════════════════════════
# Product Variant Option Serializer (through model)
# ════════════════════════════════════════════════════════════════════════


class ProductVariantOptionSerializer(serializers.ModelSerializer):
    """
    Serializer for the ProductVariantOption through model.

    Read operations include a nested ``VariantOptionValueSerializer``;
    write operations accept ``option_value_id`` as a primary key.
    """

    option_value = VariantOptionValueSerializer(read_only=True)
    option_value_id = serializers.PrimaryKeyRelatedField(
        queryset=VariantOptionValue.objects.all(),
        source="option_value",
        write_only=True,
    )

    class Meta:
        model = ProductVariantOption
        fields = [
            "id",
            "option_value",
            "option_value_id",
            "display_order",
        ]
        read_only_fields = ["id"]


# ════════════════════════════════════════════════════════════════════════
# Product Variant Serializers
# ════════════════════════════════════════════════════════════════════════


class ProductVariantListSerializer(serializers.ModelSerializer):
    """
    Lightweight serializer for variant list views.

    Minimal fields optimised for large result sets.
    """

    product_name = serializers.CharField(
        source="product.name", read_only=True
    )
    option_summary = serializers.SerializerMethodField()

    class Meta:
        model = ProductVariant
        fields = [
            "id",
            "product",
            "product_name",
            "sku",
            "name",
            "option_summary",
            "sort_order",
            "is_active",
            "created_on",
        ]
        read_only_fields = ["id", "created_on"]

    def get_option_summary(self, obj) -> dict:
        """Return option type → value mapping."""
        return obj.get_option_display()


class ProductVariantDetailSerializer(serializers.ModelSerializer):
    """
    Detailed serializer for single variant retrieval.

    Includes full nested options and override fields.
    """

    product_name = serializers.CharField(
        source="product.name", read_only=True
    )
    options = ProductVariantOptionSerializer(
        source="variant_options", many=True, read_only=True
    )
    option_summary = serializers.SerializerMethodField()

    class Meta:
        model = ProductVariant
        fields = [
            "id",
            "product",
            "product_name",
            "sku",
            "barcode",
            "name",
            "options",
            "option_summary",
            "weight_override",
            "length_override",
            "width_override",
            "height_override",
            "sort_order",
            "is_active",
            "created_on",
            "updated_on",
        ]
        read_only_fields = ["id", "created_on", "updated_on"]

    def get_option_summary(self, obj) -> dict:
        """Return option type → value mapping."""
        return obj.get_option_display()


class ProductVariantCreateSerializer(serializers.ModelSerializer):
    """
    Serializer for creating and updating product variants.

    Accepts ``option_value_ids`` as a list of VariantOptionValue PKs
    for linking via the through model on create.  Options cannot be
    changed on update.
    """

    option_value_ids = serializers.PrimaryKeyRelatedField(
        queryset=VariantOptionValue.objects.all(),
        many=True,
        write_only=True,
        required=False,
    )

    class Meta:
        model = ProductVariant
        fields = [
            "product",
            "sku",
            "barcode",
            "name",
            "option_value_ids",
            "weight_override",
            "length_override",
            "width_override",
            "height_override",
            "sort_order",
        ]

    # ── Validation ──────────────────────────────────────────────────

    def validate_sku(self, value):
        """Ensure SKU uniqueness (exclude self on update)."""
        qs = ProductVariant.objects.filter(sku=value)
        if self.instance:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise serializers.ValidationError(
                "A variant with this SKU already exists."
            )
        return value

    def validate(self, data):
        """Validate option combination uniqueness for new variants."""
        option_values = data.get("option_value_ids", [])
        product = data.get("product") or (
            self.instance.product if self.instance else None
        )

        if option_values and product and not self.instance:
            option_ids = {ov.pk for ov in option_values}
            for variant in ProductVariant.objects.for_product(product):
                existing_ids = set(
                    variant.option_values.values_list("id", flat=True)
                )
                if existing_ids == option_ids:
                    raise serializers.ValidationError(
                        "A variant with this option combination already "
                        "exists for this product."
                    )
        return data

    # ── Create / Update ─────────────────────────────────────────────

    @transaction.atomic
    def create(self, validated_data):
        """Create variant and link option values via through model."""
        option_values = validated_data.pop("option_value_ids", [])
        variant = ProductVariant.objects.create(**validated_data)

        for idx, ov in enumerate(option_values):
            ProductVariantOption.objects.create(
                variant=variant,
                option_value=ov,
                display_order=idx,
            )

        if not variant.name and option_values:
            variant.generate_name_from_options()

        return variant

    def update(self, instance, validated_data):
        """Update variant — option values cannot be changed."""
        validated_data.pop("option_value_ids", None)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance


class BulkVariantCreateSerializer(serializers.Serializer):
    """
    Serializer for bulk variant generation via VariantGenerator.

    Accepts ``product_id`` and uses the configured option types
    and their values to generate all combinations.
    """

    product_id = serializers.UUIDField(
        help_text="UUID of the product to generate variants for."
    )

    def validate_product_id(self, value):
        """Ensure product exists and is of type VARIABLE."""
        try:
            product = Product.objects.get(pk=value)
        except Product.DoesNotExist:
            raise serializers.ValidationError("Product not found.")
        if product.product_type != PRODUCT_TYPES.VARIABLE:
            raise serializers.ValidationError(
                "Variants can only be generated for VARIABLE products."
            )
        return value


# ════════════════════════════════════════════════════════════════════════
# Product Option Config Serializer
# ════════════════════════════════════════════════════════════════════════


class ProductOptionConfigSerializer(serializers.ModelSerializer):
    """
    Serializer for ProductOptionConfig.

    Links a product to its applicable option types.
    """

    option_type_name = serializers.CharField(
        source="option_type.name", read_only=True
    )

    class Meta:
        model = ProductOptionConfig
        fields = [
            "id",
            "product",
            "option_type",
            "option_type_name",
            "display_order",
            "is_active",
            "created_on",
            "updated_on",
        ]
        read_only_fields = ["id", "created_on", "updated_on"]


# ════════════════════════════════════════════════════════════════════════
# Bundle Serializers (SP05)
# ════════════════════════════════════════════════════════════════════════


class BundleItemSerializer(serializers.ModelSerializer):
    """
    Serializer for BundleItem model.

    Provides product/variant names for display and validates
    that variant belongs to the specified product.
    """

    product_name = serializers.CharField(source="product.name", read_only=True)
    variant_name = serializers.CharField(
        source="variant.name", read_only=True, allow_null=True, default=None
    )

    class Meta:
        model = BundleItem
        fields = [
            "id",
            "bundle",
            "product",
            "product_name",
            "variant",
            "variant_name",
            "quantity",
            "is_optional",
            "sort_order",
            "is_active",
            "created_on",
            "updated_on",
        ]
        read_only_fields = ["id", "created_on", "updated_on"]

    def validate(self, attrs):
        variant = attrs.get("variant")
        product = attrs.get("product")
        if variant and product and variant.product_id != product.id:
            raise serializers.ValidationError(
                {"variant": "Variant does not belong to the specified product."}
            )
        return attrs


class ProductBundleSerializer(serializers.ModelSerializer):
    """
    Base serializer for ProductBundle model.

    Includes calculated fields for price, stock, and savings.
    """

    calculated_price = serializers.SerializerMethodField()
    available_stock = serializers.SerializerMethodField()
    savings = serializers.SerializerMethodField()

    class Meta:
        model = ProductBundle
        fields = [
            "id",
            "product",
            "bundle_type",
            "fixed_price",
            "discount_type",
            "discount_value",
            "is_active",
            "calculated_price",
            "available_stock",
            "savings",
            "created_on",
            "updated_on",
        ]
        read_only_fields = ["id", "created_on", "updated_on"]

    def get_calculated_price(self, obj):
        from apps.products.services import BundlePricingService

        try:
            service = BundlePricingService(obj)
            return str(service.get_bundle_price())
        except Exception:
            return None

    def get_available_stock(self, obj):
        from apps.products.services import BundleStockService

        try:
            service = BundleStockService(obj)
            return service.get_available_stock()
        except Exception:
            return None

    def get_savings(self, obj):
        from apps.products.services import BundlePricingService

        try:
            service = BundlePricingService(obj)
            return str(service.get_savings())
        except Exception:
            return None


class BundleDetailSerializer(ProductBundleSerializer):
    """
    Detailed serializer for ProductBundle with nested items.

    Used for retrieve operations with full bundle component details.
    """

    items = BundleItemSerializer(many=True, read_only=True)
    component_count = serializers.SerializerMethodField()

    class Meta(ProductBundleSerializer.Meta):
        fields = ProductBundleSerializer.Meta.fields + [
            "items",
            "component_count",
        ]

    def get_component_count(self, obj):
        return obj.items.count()


# ════════════════════════════════════════════════════════════════════════
# BOM Serializers (SP05)
# ════════════════════════════════════════════════════════════════════════


class BOMItemSerializer(serializers.ModelSerializer):
    """
    Serializer for BOMItem (Bill of Materials component).

    Includes raw material name, effective quantity with wastage,
    unit price, and calculated item cost.
    """

    raw_material_name = serializers.CharField(
        source="raw_material.name", read_only=True
    )
    effective_quantity = serializers.SerializerMethodField()
    unit_price = serializers.SerializerMethodField()
    item_cost = serializers.SerializerMethodField()

    class Meta:
        model = BOMItem
        fields = [
            "id",
            "bom",
            "raw_material",
            "raw_material_name",
            "quantity",
            "unit",
            "wastage_percent",
            "is_critical",
            "substitute",
            "sort_order",
            "effective_quantity",
            "unit_price",
            "item_cost",
            "is_active",
            "created_on",
            "updated_on",
        ]
        read_only_fields = ["id", "created_on", "updated_on"]

    def get_effective_quantity(self, obj):
        return str(obj.get_effective_quantity())

    def get_unit_price(self, obj):
        if hasattr(obj.raw_material, "cost_price") and obj.raw_material.cost_price:
            return str(obj.raw_material.cost_price)
        return "0.00"

    def get_item_cost(self, obj):
        from decimal import Decimal

        cost_price = Decimal("0.00")
        if hasattr(obj.raw_material, "cost_price") and obj.raw_material.cost_price:
            cost_price = Decimal(str(obj.raw_material.cost_price))
        return str(obj.get_effective_quantity() * cost_price)


class BillOfMaterialsSerializer(serializers.ModelSerializer):
    """
    Base serializer for BillOfMaterials.

    Includes computed cost fields for manufacturing decisions.
    """

    total_cost = serializers.SerializerMethodField()
    unit_cost = serializers.SerializerMethodField()

    class Meta:
        model = BillOfMaterials
        fields = [
            "id",
            "product",
            "version",
            "is_active",
            "notes",
            "yield_quantity",
            "total_cost",
            "unit_cost",
            "created_on",
            "updated_on",
        ]
        read_only_fields = ["id", "created_on", "updated_on"]

    def get_total_cost(self, obj):
        from apps.products.services import CostCalculationService

        try:
            service = CostCalculationService(obj)
            return str(service.calculate_total_cost())
        except Exception:
            return None

    def get_unit_cost(self, obj):
        from apps.products.services import CostCalculationService

        try:
            service = CostCalculationService(obj)
            return str(service.calculate_unit_cost())
        except Exception:
            return None


class BOMDetailSerializer(BillOfMaterialsSerializer):
    """
    Detailed BOM serializer with nested items.

    Used for retrieve operations with full BOM component details.
    """

    items = BOMItemSerializer(many=True, read_only=True)
    component_count = serializers.SerializerMethodField()

    class Meta(BillOfMaterialsSerializer.Meta):
        fields = BillOfMaterialsSerializer.Meta.fields + [
            "items",
            "component_count",
        ]

    def get_component_count(self, obj):
        return obj.items.count()
