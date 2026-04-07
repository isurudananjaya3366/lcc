"""
Warehouse & StorageLocation model unit tests (Tasks 79-80).

All tests are database-free — they use ``__new__`` or MagicMock
so no tenant database context is required.
"""

import uuid
from datetime import time
from decimal import Decimal
from unittest.mock import MagicMock, patch, PropertyMock

import pytest
from django.db import models

from apps.inventory.warehouses.models import (
    Warehouse,
    StorageLocation,
    WarehouseZone,
    TransferRoute,
    WarehouseCapacity,
    DefaultWarehouseConfig,
    POSWarehouseMapping,
    BarcodeScan,
)
from apps.inventory.warehouses.constants import (
    SRI_LANKA_DISTRICTS,
    LOCATION_DEPTH_MAP,
    LOCATION_PARENT_RULES,
    WAREHOUSE_STATUS_CHOICES,
    WAREHOUSE_TYPE_CHOICES,
)


# ═══════════════════════════════════════════════════════════════════
# Helpers
# ═══════════════════════════════════════════════════════════════════


def _make_warehouse(**kwargs):
    """Instantiate a Warehouse via ``__new__`` without DB."""
    obj = Warehouse.__new__(Warehouse)
    from django.db.models.base import ModelState

    obj._state = ModelState()
    defaults = {
        "id": uuid.uuid4(),
        "name": "Main Warehouse",
        "code": "WH-CMB-01",
        "warehouse_type": "MAIN",
        "status": "active",
        "address_line_1": "123 Galle Road",
        "address_line_2": "",
        "city": "Colombo",
        "district": "Colombo",
        "postal_code": "00100",
        "phone": "+94112345678",
        "email": "wh@example.com",
        "manager_name": "John",
        "is_default": False,
        "is_24_hours": False,
        "opens_at": time(8, 0),
        "closes_at": time(20, 0),
        "breaks_start": None,
        "breaks_end": None,
        "latitude": Decimal("6.9271"),
        "longitude": Decimal("79.8612"),
        "is_deleted": False,
        "created_on": None,
        "updated_on": None,
    }
    defaults.update(kwargs)
    for k, v in defaults.items():
        setattr(obj, k, v)
    return obj


def _make_location(**kwargs):
    """Instantiate a StorageLocation via ``__new__`` without DB."""
    obj = StorageLocation.__new__(StorageLocation)
    from django.db.models.base import ModelState

    obj._state = ModelState()
    defaults = {
        "id": uuid.uuid4(),
        "name": "Zone A",
        "code": "WH-CMB-01-ZA",
        "location_type": "zone",
        "barcode": "LOC-T001-WH001-LOC001-7",
        "description": "",
        "max_weight": Decimal("1000.00"),
        "max_volume": Decimal("500.00"),
        "max_items": 100,
        "is_active": True,
        "is_pickable": False,
        "is_receivable": True,
        "utilization_status": "empty",
        "last_activity_at": None,
        "created_on": None,
        "updated_on": None,
    }
    defaults.update(kwargs)
    for k, v in defaults.items():
        setattr(obj, k, v)
    # FK caches
    if "warehouse" not in kwargs:
        obj._state.fields_cache["warehouse"] = _make_warehouse()
    if "parent" not in kwargs:
        obj._state.fields_cache["parent"] = None
    if "zone" not in kwargs:
        obj._state.fields_cache["zone"] = None
    return obj


# ═══════════════════════════════════════════════════════════════════
# Task 79: Warehouse model tests
# ═══════════════════════════════════════════════════════════════════


class TestWarehouseModel:
    """Unit tests for the Warehouse model."""

    def test_meta_db_table(self):
        assert Warehouse._meta.db_table == "inventory_warehouses"

    def test_meta_ordering(self):
        assert Warehouse._meta.ordering == ["name"]

    def test_warehouse_type_choices(self):
        field = Warehouse._meta.get_field("warehouse_type")
        type_values = [c[0] for c in field.choices]
        for wt, _ in WAREHOUSE_TYPE_CHOICES:
            assert wt in type_values

    def test_status_choices(self):
        field = Warehouse._meta.get_field("status")
        status_values = [c[0] for c in field.choices]
        for s, _ in WAREHOUSE_STATUS_CHOICES:
            assert s in status_values

    def test_district_choices(self):
        field = Warehouse._meta.get_field("district")
        district_values = [c[0] for c in field.choices]
        for d, _ in SRI_LANKA_DISTRICTS:
            assert d in district_values

    def test_str_representation(self):
        wh = _make_warehouse(code="WH-CMB-01", name="Main Warehouse")
        assert str(wh) == "Main Warehouse (WH-CMB-01)"

    def test_is_default_field(self):
        field = Warehouse._meta.get_field("is_default")
        assert field.default is False

    def test_code_max_length(self):
        field = Warehouse._meta.get_field("code")
        assert field.max_length == 50

    def test_name_max_length(self):
        field = Warehouse._meta.get_field("name")
        assert field.max_length == 200

    def test_latitude_field(self):
        field = Warehouse._meta.get_field("latitude")
        assert isinstance(field, models.DecimalField)

    def test_longitude_field(self):
        field = Warehouse._meta.get_field("longitude")
        assert isinstance(field, models.DecimalField)

    def test_opens_at_field(self):
        field = Warehouse._meta.get_field("opens_at")
        assert isinstance(field, models.TimeField)

    def test_closes_at_field(self):
        field = Warehouse._meta.get_field("closes_at")
        assert isinstance(field, models.TimeField)

    def test_is_open_at_within_hours(self):
        wh = _make_warehouse(
            opens_at=time(8, 0), closes_at=time(20, 0),
            is_24_hours=False, breaks_start=None, breaks_end=None,
        )
        assert wh.is_open_at(time(12, 0)) is True

    def test_is_open_at_before_opening(self):
        wh = _make_warehouse(
            opens_at=time(8, 0), closes_at=time(20, 0),
            is_24_hours=False, breaks_start=None, breaks_end=None,
        )
        assert wh.is_open_at(time(7, 0)) is False

    def test_is_open_at_after_closing(self):
        wh = _make_warehouse(
            opens_at=time(8, 0), closes_at=time(20, 0),
            is_24_hours=False, breaks_start=None, breaks_end=None,
        )
        assert wh.is_open_at(time(21, 0)) is False

    def test_is_open_at_no_hours_set(self):
        wh = _make_warehouse(
            opens_at=None, closes_at=None,
            is_24_hours=False, breaks_start=None, breaks_end=None,
        )
        assert wh.is_open_at(time(12, 0)) is True

    def test_phone_field(self):
        field = Warehouse._meta.get_field("phone")
        assert field.max_length == 20

    def test_email_field(self):
        field = Warehouse._meta.get_field("email")
        assert isinstance(field, models.EmailField)

    def test_indexes_exist(self):
        index_names = [idx.name for idx in Warehouse._meta.indexes]
        assert len(index_names) >= 1

    def test_manager_is_available(self):
        assert hasattr(Warehouse, "objects")

    def test_all_with_deleted_manager(self):
        assert hasattr(Warehouse, "all_with_deleted")


# ═══════════════════════════════════════════════════════════════════
# Task 80: StorageLocation model tests
# ═══════════════════════════════════════════════════════════════════


class TestStorageLocationModel:
    """Unit tests for the StorageLocation model."""

    def test_meta_db_table(self):
        assert StorageLocation._meta.db_table == "inventory_storage_locations"

    def test_meta_ordering(self):
        assert StorageLocation._meta.ordering == ["warehouse", "code"]

    def test_location_type_choices(self):
        field = StorageLocation._meta.get_field("location_type")
        assert len(field.choices) >= 5  # ZONE, AISLE, RACK, SHELF, BIN

    def test_str_representation(self):
        loc = _make_location(code="WH-CMB-01-ZA", name="Zone A")
        assert str(loc) == "WH-CMB-01-ZA (Zone A)"

    def test_depth_root_is_zero(self):
        loc = _make_location()
        loc._state.fields_cache["parent"] = None
        assert loc.depth == 0

    def test_depth_with_parent(self):
        parent = _make_location(location_type="zone")
        parent._state.fields_cache["parent"] = None
        child = _make_location(location_type="aisle")
        child._state.fields_cache["parent"] = parent
        assert child.depth == 1

    def test_depth_three_levels(self):
        grandparent = _make_location(location_type="zone")
        grandparent._state.fields_cache["parent"] = None
        parent = _make_location(location_type="aisle")
        parent._state.fields_cache["parent"] = grandparent
        child = _make_location(location_type="rack")
        child._state.fields_cache["parent"] = parent
        assert child.depth == 2

    def test_level_name(self):
        expected_names = {0: "Zone", 1: "Aisle", 2: "Rack", 3: "Shelf", 4: "Bin"}
        for loc_type, depth_val in LOCATION_DEPTH_MAP.items():
            loc = _make_location(location_type=loc_type)
            assert loc.level_name == expected_names[depth_val]

    def test_location_path_root(self):
        loc = _make_location(code="ZA", name="Zone A")
        loc._state.fields_cache["parent"] = None
        loc.pk = loc.id  # needed by location_path's seen set
        loc.parent_id = None
        assert "Zone A" in loc.location_path

    def test_is_active_default(self):
        field = StorageLocation._meta.get_field("is_active")
        assert field.default is True

    def test_is_pickable_default(self):
        field = StorageLocation._meta.get_field("is_pickable")
        assert field.default is True

    def test_is_receivable_default(self):
        field = StorageLocation._meta.get_field("is_receivable")
        assert field.default is True

    def test_barcode_field_blank(self):
        field = StorageLocation._meta.get_field("barcode")
        assert field.blank is True

    def test_max_weight_decimal(self):
        field = StorageLocation._meta.get_field("max_weight")
        assert isinstance(field, models.DecimalField)

    def test_max_volume_decimal(self):
        field = StorageLocation._meta.get_field("max_volume")
        assert isinstance(field, models.DecimalField)

    def test_max_items_positive(self):
        field = StorageLocation._meta.get_field("max_items")
        assert isinstance(field, models.PositiveIntegerField)

    def test_parent_self_referential(self):
        field = StorageLocation._meta.get_field("parent")
        assert field.related_model is StorageLocation

    def test_zone_fk(self):
        field = StorageLocation._meta.get_field("zone")
        assert field.related_model is WarehouseZone

    def test_utilization_status_field(self):
        field = StorageLocation._meta.get_field("utilization_status")
        assert field.max_length >= 5

    def test_last_activity_at_nullable(self):
        field = StorageLocation._meta.get_field("last_activity_at")
        assert field.null is True

    def test_location_parent_rules_defined(self):
        assert "aisle" in LOCATION_PARENT_RULES
        assert "rack" in LOCATION_PARENT_RULES
        assert "shelf" in LOCATION_PARENT_RULES
        assert "bin" in LOCATION_PARENT_RULES

    def test_parent_rules_hierarchy(self):
        assert LOCATION_PARENT_RULES["aisle"] == "zone"
        assert LOCATION_PARENT_RULES["rack"] == "aisle"
        assert LOCATION_PARENT_RULES["shelf"] == "rack"
        assert LOCATION_PARENT_RULES["bin"] == "shelf"

    def test_unique_constraint_on_warehouse_code(self):
        constraints = StorageLocation._meta.constraints
        codes = [c.name for c in constraints]
        assert any("warehouse" in c and "code" in c for c in codes)

    def test_indexes_exist(self):
        assert len(StorageLocation._meta.indexes) >= 1

    def test_manager_available(self):
        assert hasattr(StorageLocation, "objects")


# ═══════════════════════════════════════════════════════════════════
# Group D model meta tests
# ═══════════════════════════════════════════════════════════════════


class TestWarehouseZoneModel:
    """Unit tests for WarehouseZone."""

    def test_meta_db_table(self):
        assert WarehouseZone._meta.db_table == "inventory_warehouse_zones"

    def test_purpose_choices(self):
        field = WarehouseZone._meta.get_field("purpose")
        assert len(field.choices) >= 5

    def test_code_max_length(self):
        field = WarehouseZone._meta.get_field("code")
        assert field.max_length == 20

    def test_unique_constraint(self):
        names = [c.name for c in WarehouseZone._meta.constraints]
        assert any("zone" in n and "warehouse" in n and "code" in n for n in names)


class TestTransferRouteModel:
    """Unit tests for TransferRoute."""

    def test_meta_db_table(self):
        assert TransferRoute._meta.db_table == "inventory_transfer_routes"

    def test_transit_days_field(self):
        field = TransferRoute._meta.get_field("transit_days")
        assert isinstance(field, models.PositiveIntegerField)

    def test_estimated_cost_field(self):
        field = TransferRoute._meta.get_field("estimated_cost")
        assert isinstance(field, models.DecimalField)

    def test_unique_constraint(self):
        names = [c.name for c in TransferRoute._meta.constraints]
        assert len(names) >= 1

    def test_calculate_transfer_cost(self):
        route = TransferRoute.__new__(TransferRoute)
        from django.db.models.base import ModelState
        route._state = ModelState()
        route.estimated_cost = Decimal("100.00")
        route.cost_per_kg = Decimal("2.00")
        route.cost_per_m3 = Decimal("10.00")
        route.minimum_cost = Decimal("50.00")
        cost = route.calculate_transfer_cost(weight_kg=10, volume_m3=5)
        # base = max(100, 50) = 100; weight=20, volume=50; max(20,50)=50; total=150
        assert cost == Decimal("150.00")

    def test_calculate_transfer_cost_minimum(self):
        route = TransferRoute.__new__(TransferRoute)
        from django.db.models.base import ModelState
        route._state = ModelState()
        route.estimated_cost = Decimal("0")
        route.cost_per_kg = Decimal("0.01")
        route.cost_per_m3 = Decimal("0.01")
        route.minimum_cost = Decimal("50.00")
        cost = route.calculate_transfer_cost(weight_kg=1, volume_m3=1)
        # base = max(0, 50) = 50; weight=0.01, volume=0.01; max=0.01; total=50.01
        assert cost == Decimal("50.01")


class TestWarehouseCapacityModel:
    """Unit tests for WarehouseCapacity."""

    def test_meta_db_table(self):
        assert WarehouseCapacity._meta.db_table == "inventory_warehouse_capacities"

    def test_utilization_percentage_property(self):
        cap = WarehouseCapacity.__new__(WarehouseCapacity)
        from django.db.models.base import ModelState
        cap._state = ModelState()
        cap.max_item_capacity = 100
        cap.current_item_count = 75
        assert cap.utilization_percentage == 75.0

    def test_utilization_percentage_zero_capacity(self):
        cap = WarehouseCapacity.__new__(WarehouseCapacity)
        from django.db.models.base import ModelState
        cap._state = ModelState()
        cap.max_item_capacity = 0
        cap.current_item_count = 0
        assert cap.utilization_percentage == 0.0

    def test_alert_level_green(self):
        cap = WarehouseCapacity.__new__(WarehouseCapacity)
        from django.db.models.base import ModelState
        cap._state = ModelState()
        cap.max_item_capacity = 100
        cap.current_item_count = 50
        assert cap.alert_level == "green"

    def test_alert_level_red(self):
        cap = WarehouseCapacity.__new__(WarehouseCapacity)
        from django.db.models.base import ModelState
        cap._state = ModelState()
        cap.max_item_capacity = 100
        cap.current_item_count = 95
        assert cap.alert_level == "red"


class TestDefaultWarehouseConfigModel:
    """Unit tests for DefaultWarehouseConfig."""

    def test_meta_db_table(self):
        assert DefaultWarehouseConfig._meta.db_table == "inventory_default_warehouse_configs"

    def test_scope_field(self):
        field = DefaultWarehouseConfig._meta.get_field("scope")
        assert field.max_length >= 10


class TestPOSWarehouseMappingModel:
    """Unit tests for POSWarehouseMapping."""

    def test_meta_db_table(self):
        assert POSWarehouseMapping._meta.db_table == "inventory_pos_warehouse_mappings"

    def test_terminal_id_unique(self):
        field = POSWarehouseMapping._meta.get_field("terminal_id")
        assert field.unique is True


class TestBarcodeScanModel:
    """Unit tests for BarcodeScan."""

    def test_meta_db_table(self):
        assert BarcodeScan._meta.db_table == "inventory_barcode_scans"

    def test_meta_ordering(self):
        assert BarcodeScan._meta.ordering == ["-created_on"]

    def test_scan_type_choices(self):
        field = BarcodeScan._meta.get_field("scan_type")
        assert len(field.choices) >= 4

    def test_success_default(self):
        field = BarcodeScan._meta.get_field("success")
        assert field.default is True

    def test_context_data_json(self):
        field = BarcodeScan._meta.get_field("context_data")
        assert isinstance(field, models.JSONField)
