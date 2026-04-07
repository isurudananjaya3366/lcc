"""
Attributes integration tests — production-level database tests.

Tests model CRUD operations, API endpoints, tenant isolation, and business
logic using a real PostgreSQL database with tenant schema isolation.

Run with:
    DJANGO_SETTINGS_MODULE=config.settings.test_pg pytest tests/attributes/test_integration.py

All tests in this module require @pytest.mark.django_db.

NOTE ON MANAGERS:
    The attribute models define custom managers (GroupManager, AttributeManager,
    OptionManager) that do NOT extend AliveManager.  This means ``objects``
    returns ALL records regardless of ``is_active`` / ``is_deleted``.
    Soft-delete / deactivation filtering is only available via the explicit
    queryset helpers (e.g. ``objects.active()``, ``objects.filterable()``).
    Use ``all_with_deleted`` when you need the unfiltered base Manager.
"""

import uuid
from decimal import Decimal

import pytest
from django.core.exceptions import ValidationError
from django.db import IntegrityError

pytestmark = pytest.mark.django_db


# ═══════════════════════════════════════════════════════════════════════
# 1. AttributeGroup — CRUD Operations
# ═══════════════════════════════════════════════════════════════════════


class TestAttributeGroupCRUD:
    """Test AttributeGroup model CRUD with real database."""

    def test_create_attribute_group(self, tenant_context):
        from apps.attributes.models import AttributeGroup

        group = AttributeGroup.objects.create(
            name="Test Group",
            description="A test group",
            display_order=5,
        )
        assert group.pk is not None
        assert isinstance(group.pk, uuid.UUID)
        assert group.name == "Test Group"
        assert group.slug == "test-group"
        assert group.description == "A test group"
        assert group.display_order == 5
        assert group.is_active is True
        assert group.is_deleted is False

    def test_auto_slug_generation(self, tenant_context):
        from apps.attributes.models import AttributeGroup

        group = AttributeGroup.objects.create(name="Technical Specifications")
        assert group.slug == "technical-specifications"

    def test_slug_not_overwritten_on_update(self, attribute_group):
        original_slug = attribute_group.slug
        attribute_group.name = "Updated Group Name"
        attribute_group.save()
        attribute_group.refresh_from_db()
        assert attribute_group.slug == original_slug

    def test_read_attribute_group(self, attribute_group):
        from apps.attributes.models import AttributeGroup

        fetched = AttributeGroup.objects.get(pk=attribute_group.pk)
        assert fetched.name == attribute_group.name
        assert fetched.slug == attribute_group.slug

    def test_update_attribute_group(self, attribute_group):
        attribute_group.description = "Updated description"
        attribute_group.save()
        attribute_group.refresh_from_db()
        assert attribute_group.description == "Updated description"

    def test_soft_delete_method(self, attribute_group):
        """Test BaseModel.soft_delete() sets is_deleted and deleted_on."""
        attribute_group.soft_delete()
        attribute_group.refresh_from_db()
        assert attribute_group.is_deleted is True
        assert attribute_group.deleted_on is not None
        # all_with_deleted always finds the record
        from apps.attributes.models import AttributeGroup

        assert AttributeGroup.all_with_deleted.filter(pk=attribute_group.pk).exists()

    def test_soft_delete_via_delete_override(self, attribute_group):
        """Calling .delete() triggers soft-delete, not hard delete."""
        from apps.attributes.models import AttributeGroup

        pk = attribute_group.pk
        attribute_group.delete()
        # Record still exists (soft-deleted)
        obj = AttributeGroup.all_with_deleted.get(pk=pk)
        assert obj.is_deleted is True

    def test_restore_after_soft_delete(self, attribute_group):
        """Test BaseModel.restore() undoes a soft-delete."""
        attribute_group.soft_delete()
        attribute_group.restore()
        attribute_group.refresh_from_db()
        assert attribute_group.is_deleted is False
        assert attribute_group.deleted_on is None

    def test_hard_delete(self, attribute_group):
        """Test BaseModel.hard_delete() permanently removes the record."""
        from apps.attributes.models import AttributeGroup

        pk = attribute_group.pk
        attribute_group.hard_delete()
        assert not AttributeGroup.all_with_deleted.filter(pk=pk).exists()

    def test_deactivation_filtered_by_active_queryset(self, attribute_group):
        """Deactivated groups are excluded by objects.active()."""
        from apps.attributes.models import AttributeGroup

        attribute_group.is_active = False
        attribute_group.save()
        assert not AttributeGroup.objects.active().filter(pk=attribute_group.pk).exists()

    def test_str_representation(self, attribute_group):
        assert str(attribute_group) == "Technical Specifications"

    def test_ordering(self, attribute_group, attribute_group_2):
        from apps.attributes.models import AttributeGroup

        groups = list(AttributeGroup.objects.all().values_list("name", flat=True))
        assert groups.index("Technical Specifications") < groups.index("Dimensions")

    def test_uuid_primary_key(self, attribute_group):
        assert isinstance(attribute_group.pk, uuid.UUID)

    def test_timestamps_auto_populated(self, attribute_group):
        assert attribute_group.created_on is not None
        assert attribute_group.updated_on is not None


# ═══════════════════════════════════════════════════════════════════════
# 2. AttributeGroup — QuerySet Methods
# ═══════════════════════════════════════════════════════════════════════


class TestAttributeGroupQuerySet:
    """Test AttributeGroup custom QuerySet methods."""

    def test_active_queryset(self, attribute_group, tenant_context):
        from apps.attributes.models import AttributeGroup

        inactive = AttributeGroup.objects.create(
            name="Inactive Group", is_active=False,
        )
        active_groups = AttributeGroup.objects.active()
        assert attribute_group in active_groups
        assert inactive not in active_groups

    def test_with_attributes_queryset(self, attribute_group, text_attribute):
        from apps.attributes.models import AttributeGroup

        groups = AttributeGroup.objects.with_attributes()
        group = groups.get(pk=attribute_group.pk)
        # Verify the prefetched attributes are correct
        assert text_attribute in group.attributes.all()


# ═══════════════════════════════════════════════════════════════════════
# 3. Attribute — CRUD Operations
# ═══════════════════════════════════════════════════════════════════════


class TestAttributeCRUD:
    """Test Attribute model CRUD with real database."""

    def test_create_text_attribute(self, text_attribute):
        assert text_attribute.pk is not None
        assert text_attribute.name == "Brand"
        assert text_attribute.slug == "brand"
        assert text_attribute.attribute_type == "text"
        assert text_attribute.is_required is True
        assert text_attribute.is_filterable is True
        assert text_attribute.is_searchable is True

    def test_create_number_attribute(self, number_attribute):
        assert number_attribute.attribute_type == "number"
        assert number_attribute.unit == "kg"
        assert number_attribute.min_value == Decimal("0")
        assert number_attribute.max_value == Decimal("1000")

    def test_create_select_attribute(self, select_attribute):
        assert select_attribute.attribute_type == "select"
        assert select_attribute.slug == "color"

    def test_auto_slug_generation(self, tenant_context):
        from apps.attributes.models import Attribute

        attr = Attribute.objects.create(
            name="Screen Size",
            attribute_type="number",
            unit="inches",
        )
        assert attr.slug == "screen-size"

    def test_group_fk_relationship(self, text_attribute, attribute_group):
        assert text_attribute.group == attribute_group
        assert text_attribute in attribute_group.attributes.all()

    def test_group_set_null_on_delete(self, text_attribute, attribute_group):
        """Deleting the group via hard_delete sets FK to NULL."""
        from apps.attributes.models import AttributeGroup

        group_pk = attribute_group.pk
        AttributeGroup.all_with_deleted.filter(pk=group_pk).delete()
        text_attribute.refresh_from_db()
        assert text_attribute.group is None

    def test_categories_m2m(self, text_attribute, category):
        text_attribute.categories.add(category)
        assert category in text_attribute.categories.all()
        assert text_attribute in category.attributes.all()

    def test_clean_validates_min_max(self, tenant_context):
        from apps.attributes.models import Attribute

        attr = Attribute(
            name="Bad Range",
            attribute_type="number",
            min_value=Decimal("100"),
            max_value=Decimal("10"),
        )
        with pytest.raises(ValidationError):
            attr.clean()

    def test_clean_passes_valid_range(self, tenant_context):
        from apps.attributes.models import Attribute

        attr = Attribute(
            name="Good Range",
            attribute_type="number",
            min_value=Decimal("10"),
            max_value=Decimal("100"),
        )
        attr.clean()  # Should not raise

    def test_soft_delete(self, text_attribute):
        """soft_delete() marks the record and sets deleted_on."""
        text_attribute.soft_delete()
        text_attribute.refresh_from_db()
        assert text_attribute.is_deleted is True
        assert text_attribute.deleted_on is not None

        from apps.attributes.models import Attribute

        assert Attribute.all_with_deleted.filter(pk=text_attribute.pk).exists()

    def test_str_representation(self, text_attribute):
        assert str(text_attribute) == "Brand"

    def test_update_attribute(self, text_attribute):
        text_attribute.is_filterable = False
        text_attribute.save()
        text_attribute.refresh_from_db()
        assert text_attribute.is_filterable is False


# ═══════════════════════════════════════════════════════════════════════
# 4. Attribute — QuerySet Methods
# ═══════════════════════════════════════════════════════════════════════


class TestAttributeQuerySet:
    """Test Attribute custom QuerySet methods."""

    def test_filterable(self, text_attribute, tenant_context):
        from apps.attributes.models import Attribute

        filterable = Attribute.objects.filterable()
        assert text_attribute in filterable

    def test_searchable(self, text_attribute, tenant_context):
        from apps.attributes.models import Attribute

        searchable = Attribute.objects.searchable()
        assert text_attribute in searchable

    def test_by_type(self, text_attribute, number_attribute, tenant_context):
        from apps.attributes.models import Attribute

        text_attrs = Attribute.objects.by_type("text")
        assert text_attribute in text_attrs
        assert number_attribute not in text_attrs

    def test_for_category(self, text_attribute, category, tenant_context):
        from apps.attributes.models import Attribute

        text_attribute.categories.add(category)
        attrs = Attribute.objects.for_category(category)
        assert text_attribute in attrs


# ═══════════════════════════════════════════════════════════════════════
# 5. AttributeOption — CRUD Operations
# ═══════════════════════════════════════════════════════════════════════


class TestAttributeOptionCRUD:
    """Test AttributeOption model CRUD with real database."""

    def test_create_option(self, attribute_options):
        red = attribute_options[0]
        assert red.pk is not None
        assert red.value == "red"
        assert red.label == "Red"
        assert red.color_code == "#FF0000"
        assert red.is_default is True

    def test_option_fk_relationship(self, attribute_options, select_attribute):
        for opt in attribute_options:
            assert opt.attribute == select_attribute
        assert select_attribute.options.count() == 3

    def test_cascade_delete(self, select_attribute, attribute_options):
        """Hard-deleting the parent Attribute cascades to its options."""
        from apps.attributes.models import Attribute, AttributeOption

        option_pks = [o.pk for o in attribute_options]
        Attribute.all_with_deleted.filter(pk=select_attribute.pk).delete()
        for pk in option_pks:
            assert not AttributeOption.all_with_deleted.filter(pk=pk).exists()

    def test_unique_together_value(self, select_attribute, attribute_options):
        """The (attribute, value) pair must be unique."""
        from apps.attributes.models import AttributeOption

        with pytest.raises(IntegrityError):
            AttributeOption.objects.create(
                attribute=select_attribute,
                value="red",  # Already exists
                label="Another Red",
            )

    def test_single_default_enforcement(self, select_attribute, attribute_options):
        """Setting a new default clears the previous one."""
        from apps.attributes.models import AttributeOption

        blue = attribute_options[1]
        blue.is_default = True
        blue.save()
        # Refresh red (was the default)
        red = attribute_options[0]
        red.refresh_from_db()
        assert blue.is_default is True
        assert red.is_default is False

    def test_str_representation(self, attribute_options):
        red = attribute_options[0]
        assert str(red) == "Red"

    def test_ordering(self, attribute_options):
        from apps.attributes.models import AttributeOption

        opts = list(
            AttributeOption.objects.filter(
                attribute=attribute_options[0].attribute,
            ).values_list("label", flat=True)
        )
        assert opts == ["Red", "Blue", "Green"]


# ═══════════════════════════════════════════════════════════════════════
# 6. AttributeOption — QuerySet Methods
# ═══════════════════════════════════════════════════════════════════════


class TestAttributeOptionQuerySet:
    """Test AttributeOption custom QuerySet methods."""

    def test_for_attribute(self, select_attribute, attribute_options):
        from apps.attributes.models import AttributeOption

        opts = AttributeOption.objects.for_attribute(select_attribute)
        assert opts.count() == 3

    def test_defaults(self, select_attribute, attribute_options):
        from apps.attributes.models import AttributeOption

        defaults = AttributeOption.objects.defaults()
        assert defaults.filter(attribute=select_attribute).count() == 1

    def test_with_images(self, select_attribute, attribute_options, tenant_context):
        from apps.attributes.models import AttributeOption

        # None of the fixtures have images
        with_images = AttributeOption.objects.with_images()
        assert with_images.count() == 0


# ═══════════════════════════════════════════════════════════════════════
# 7. API Endpoint Tests — AttributeGroup
# ═══════════════════════════════════════════════════════════════════════


class TestAttributeGroupAPI:
    """Test AttributeGroup API endpoints with real HTTP requests.

    List endpoints return paginated responses from StandardPagination:
        { "count": N, "next": ..., "previous": ..., "results": [...] }
    """

    def test_list_groups(self, auth_api_client, attribute_group):
        response = auth_api_client.get("/api/v1/attribute-groups/")
        assert response.status_code == 200
        assert response.data["count"] >= 1
        assert len(response.data["results"]) >= 1

    def test_create_group(self, auth_api_client, tenant_context):
        data = {
            "name": "New Group",
            "description": "A brand new group",
            "display_order": 10,
        }
        response = auth_api_client.post("/api/v1/attribute-groups/", data)
        assert response.status_code == 201
        assert response.data["name"] == "New Group"
        assert response.data["slug"] == "new-group"
        assert response.data["attribute_count"] == 0

    def test_retrieve_group(self, auth_api_client, attribute_group):
        response = auth_api_client.get(
            f"/api/v1/attribute-groups/{attribute_group.pk}/"
        )
        assert response.status_code == 200
        assert response.data["name"] == attribute_group.name

    def test_update_group(self, auth_api_client, attribute_group):
        data = {"name": "Updated Name", "description": "Updated"}
        response = auth_api_client.patch(
            f"/api/v1/attribute-groups/{attribute_group.pk}/",
            data,
        )
        assert response.status_code == 200
        assert response.data["name"] == "Updated Name"

    def test_delete_group(self, auth_api_client, attribute_group):
        response = auth_api_client.delete(
            f"/api/v1/attribute-groups/{attribute_group.pk}/"
        )
        # BaseModel.delete() triggers soft_delete(); DRF returns 204
        assert response.status_code == 204

    def test_unauthenticated_rejected(self, tenant_context):
        from rest_framework.test import APIClient

        client = APIClient()
        client.defaults["HTTP_HOST"] = "testserver"
        response = client.get("/api/v1/attribute-groups/")
        assert response.status_code in (401, 403, 404)

    def test_search_groups(self, auth_api_client, attribute_group):
        response = auth_api_client.get(
            "/api/v1/attribute-groups/?search=Technical"
        )
        assert response.status_code == 200
        results = response.data["results"]
        assert any(g["name"] == "Technical Specifications" for g in results)

    def test_ordering(self, auth_api_client, attribute_group, attribute_group_2):
        response = auth_api_client.get(
            "/api/v1/attribute-groups/?ordering=display_order"
        )
        assert response.status_code == 200
        names = [g["name"] for g in response.data["results"]]
        assert names.index("Technical Specifications") < names.index("Dimensions")


# ═══════════════════════════════════════════════════════════════════════
# 8. API Endpoint Tests — Attribute
# ═══════════════════════════════════════════════════════════════════════


class TestAttributeAPI:
    """Test Attribute API endpoints with real HTTP requests."""

    def test_list_attributes(self, auth_api_client, text_attribute):
        response = auth_api_client.get("/api/v1/attributes/")
        assert response.status_code == 200
        results = response.data["results"]
        assert len(results) >= 1
        # List serializer (AttributeListSerializer) exposes option_count
        first = results[0]
        assert "option_count" in first

    def test_create_attribute(self, auth_api_client, attribute_group, tenant_context):
        data = {
            "name": "Resolution",
            "attribute_type": "text",
            "group": str(attribute_group.pk),
            "is_required": False,
        }
        response = auth_api_client.post("/api/v1/attributes/", data)
        assert response.status_code == 201
        assert response.data["name"] == "Resolution"
        assert response.data["slug"] == "resolution"

    def test_create_number_requires_unit(self, auth_api_client, tenant_context):
        data = {
            "name": "Weight",
            "attribute_type": "number",
            "unit": "",
        }
        response = auth_api_client.post("/api/v1/attributes/", data)
        assert response.status_code == 400

    def test_create_number_with_unit_succeeds(self, auth_api_client, tenant_context):
        data = {
            "name": "Height",
            "attribute_type": "number",
            "unit": "cm",
        }
        response = auth_api_client.post("/api/v1/attributes/", data)
        assert response.status_code == 201

    def test_retrieve_detail(self, auth_api_client, text_attribute):
        response = auth_api_client.get(
            f"/api/v1/attributes/{text_attribute.pk}/"
        )
        assert response.status_code == 200
        # Detail serializer (AttributeDetailSerializer) nests group + options
        assert "options" in response.data
        assert "group" in response.data
        assert response.data["name"] == "Brand"

    def test_update_attribute(self, auth_api_client, text_attribute):
        data = {"is_filterable": False}
        response = auth_api_client.patch(
            f"/api/v1/attributes/{text_attribute.pk}/", data
        )
        assert response.status_code == 200

    def test_delete_attribute(self, auth_api_client, text_attribute):
        response = auth_api_client.delete(
            f"/api/v1/attributes/{text_attribute.pk}/"
        )
        assert response.status_code == 204

    def test_filter_by_type(self, auth_api_client, text_attribute, number_attribute):
        response = auth_api_client.get("/api/v1/attributes/?attribute_type=text")
        assert response.status_code == 200
        names = [a["name"] for a in response.data["results"]]
        assert "Brand" in names
        assert "Weight" not in names

    def test_filter_by_filterable(self, auth_api_client, text_attribute):
        response = auth_api_client.get("/api/v1/attributes/?is_filterable=true")
        assert response.status_code == 200
        assert all(a["is_filterable"] for a in response.data["results"])

    def test_search_by_name(self, auth_api_client, text_attribute):
        response = auth_api_client.get("/api/v1/attributes/?search=Brand")
        assert response.status_code == 200
        results = response.data["results"]
        assert any(a["name"] == "Brand" for a in results)

    def test_by_category_action(
        self, auth_api_client, text_attribute, category, tenant_context
    ):
        text_attribute.categories.add(category)
        response = auth_api_client.get(
            f"/api/v1/attributes/by-category/?category_id={category.pk}"
        )
        assert response.status_code == 200
        # by-category is a custom action — returns unpaginated list
        names = [a["name"] for a in response.data]
        assert "Brand" in names

    def test_by_category_inherits_parent(
        self,
        auth_api_client,
        text_attribute,
        category,
        child_category,
        tenant_context,
    ):
        text_attribute.categories.add(category)
        # Query for child category — view walks up to parent via .parent
        response = auth_api_client.get(
            f"/api/v1/attributes/by-category/?category_id={child_category.pk}"
        )
        assert response.status_code == 200
        names = [a["name"] for a in response.data]
        assert "Brand" in names

    def test_by_category_without_id_returns_400(self, auth_api_client, tenant_context):
        response = auth_api_client.get("/api/v1/attributes/by-category/")
        assert response.status_code == 400

    def test_filterable_action(self, auth_api_client, text_attribute, tenant_context):
        # filterable is a custom action — returns unpaginated list
        response = auth_api_client.get("/api/v1/attributes/filterable/")
        assert response.status_code == 200
        names = [a["name"] for a in response.data]
        assert "Brand" in names

    def test_unauthenticated_rejected(self, tenant_context):
        from rest_framework.test import APIClient

        client = APIClient()
        client.defaults["HTTP_HOST"] = "testserver"
        response = client.get("/api/v1/attributes/")
        assert response.status_code in (401, 403, 404)


# ═══════════════════════════════════════════════════════════════════════
# 9. API Endpoint Tests — AttributeOption
# ═══════════════════════════════════════════════════════════════════════


class TestAttributeOptionAPI:
    """Test AttributeOption API endpoints with real HTTP requests."""

    def test_list_options(self, auth_api_client, attribute_options):
        response = auth_api_client.get("/api/v1/attribute-options/")
        assert response.status_code == 200
        assert response.data["count"] >= 3
        assert len(response.data["results"]) >= 3

    def test_create_option(self, auth_api_client, select_attribute, tenant_context):
        data = {
            "attribute": str(select_attribute.pk),
            "value": "yellow",
            "label": "Yellow",
            "color_code": "#FFFF00",
            "display_order": 4,
        }
        response = auth_api_client.post("/api/v1/attribute-options/", data)
        assert response.status_code == 201
        assert response.data["label"] == "Yellow"

    def test_retrieve_option(self, auth_api_client, attribute_options):
        opt = attribute_options[0]
        response = auth_api_client.get(f"/api/v1/attribute-options/{opt.pk}/")
        assert response.status_code == 200
        assert response.data["label"] == "Red"
        assert response.data["attribute_name"] == "Color"

    def test_update_option(self, auth_api_client, attribute_options):
        opt = attribute_options[0]
        data = {"label": "Crimson Red"}
        response = auth_api_client.patch(
            f"/api/v1/attribute-options/{opt.pk}/", data
        )
        assert response.status_code == 200
        assert response.data["label"] == "Crimson Red"

    def test_delete_option(self, auth_api_client, attribute_options):
        opt = attribute_options[2]  # Delete green
        response = auth_api_client.delete(
            f"/api/v1/attribute-options/{opt.pk}/"
        )
        assert response.status_code == 204

    def test_filter_by_attribute(
        self, auth_api_client, select_attribute, attribute_options
    ):
        response = auth_api_client.get(
            f"/api/v1/attribute-options/?attribute={select_attribute.pk}"
        )
        assert response.status_code == 200
        assert response.data["count"] == 3

    def test_filter_by_default(self, auth_api_client, attribute_options):
        response = auth_api_client.get(
            "/api/v1/attribute-options/?is_default=true"
        )
        assert response.status_code == 200
        assert all(o["is_default"] for o in response.data["results"])

    def test_unauthenticated_rejected(self, tenant_context):
        from rest_framework.test import APIClient

        client = APIClient()
        client.defaults["HTTP_HOST"] = "testserver"
        response = client.get("/api/v1/attribute-options/")
        assert response.status_code in (401, 403, 404)


# ═══════════════════════════════════════════════════════════════════════
# 10. Integration — Cross-Model Relationships
# ═══════════════════════════════════════════════════════════════════════


class TestCrossModelIntegration:
    """Test relationships between attribute models."""

    def test_group_has_attributes(
        self, attribute_group, text_attribute, number_attribute
    ):
        assert attribute_group.attributes.count() == 2

    def test_attribute_has_options(self, select_attribute, attribute_options):
        assert select_attribute.options.count() == 3

    def test_category_attribute_relationship(self, text_attribute, category):
        text_attribute.categories.add(category)
        assert text_attribute.categories.count() == 1
        assert category.attributes.count() == 1

    def test_delete_group_nullifies_attributes(
        self, attribute_group, text_attribute
    ):
        from apps.attributes.models import AttributeGroup

        AttributeGroup.all_with_deleted.filter(pk=attribute_group.pk).delete()
        text_attribute.refresh_from_db()
        assert text_attribute.group is None

    def test_delete_attribute_cascades_options(
        self, select_attribute, attribute_options
    ):
        from apps.attributes.models import Attribute, AttributeOption

        option_pks = [o.pk for o in attribute_options]
        Attribute.all_with_deleted.filter(pk=select_attribute.pk).delete()
        for pk in option_pks:
            assert not AttributeOption.all_with_deleted.filter(pk=pk).exists()

    def test_api_detail_includes_nested_data(
        self, auth_api_client, select_attribute, attribute_options
    ):
        response = auth_api_client.get(
            f"/api/v1/attributes/{select_attribute.pk}/"
        )
        assert response.status_code == 200
        assert len(response.data["options"]) == 3
        assert response.data["group"] is not None
