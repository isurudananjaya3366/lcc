"""
Manufacturing cost calculation and stock services for LankaCommerce Cloud.

Provides two service classes:
- CostCalculationService: Calculates manufacturing costs from BOM
- ManufacturingStockService: Checks raw material availability for production

Cost Components:
    Material Cost + Wastage + Labor + Overhead = Total Manufacturing Cost
    Unit Cost = Total Cost / yield_quantity
"""

import math
from decimal import Decimal


class CostCalculationService:
    """
    Service for calculating manufacturing costs from a Bill of Materials.

    Cost breakdown:
    - Material cost: Sum of (raw_material.cost_price × quantity)
    - Wastage cost: Additional material needed due to manufacturing loss
    - Labor cost: Configurable labor cost per production run
    - Overhead cost: Fixed or percentage-based overhead allocation
    - Total cost: Material + Wastage + Labor + Overhead
    - Unit cost: Total cost / yield_quantity
    """

    def __init__(self, bom, labor_cost=None, overhead_cost=None, overhead_percent=None):
        """
        Initialize with a BillOfMaterials instance.

        Args:
            bom: BillOfMaterials instance.
            labor_cost: Decimal labor cost per production run (optional).
            overhead_cost: Decimal fixed overhead per production run (optional).
            overhead_percent: Decimal overhead as percentage of material cost (optional).
        """
        self.bom = bom
        self._labor_cost = Decimal(str(labor_cost)) if labor_cost is not None else Decimal("0.00")
        self._overhead_cost = Decimal(str(overhead_cost)) if overhead_cost is not None else None
        self._overhead_percent = Decimal(str(overhead_percent)) if overhead_percent is not None else None

    def calculate_material_cost(self):
        """
        Calculate total raw material cost for one production run.

        Returns:
            Decimal: Sum of (raw_material.cost_price × quantity) for all BOM items.
        """
        total = Decimal("0.00")
        items = self.bom.items.select_related("raw_material").all()

        for item in items:
            cost_price = Decimal("0.00")
            if hasattr(item.raw_material, "cost_price") and item.raw_material.cost_price:
                cost_price = Decimal(str(item.raw_material.cost_price))

            item_cost = item.quantity * cost_price
            total += item_cost

        return total

    def calculate_with_wastage(self):
        """
        Calculate material cost including wastage allowances.

        For each BOM item, the effective quantity is:
            quantity × (1 + wastage_percent / 100)

        Returns:
            Decimal: Total material cost with wastage included.
        """
        total = Decimal("0.00")
        items = self.bom.items.select_related("raw_material").all()

        for item in items:
            cost_price = Decimal("0.00")
            if hasattr(item.raw_material, "cost_price") and item.raw_material.cost_price:
                cost_price = Decimal(str(item.raw_material.cost_price))

            wastage_multiplier = Decimal("1") + (item.wastage_percent / Decimal("100"))
            effective_qty = item.quantity * wastage_multiplier
            item_cost = effective_qty * cost_price
            total += item_cost

        return total

    def calculate_labor_cost(self):
        """
        Get the labor cost for one production run.

        Returns:
            Decimal: Labor cost per production run.
        """
        return self._labor_cost

    def calculate_overhead(self):
        """
        Calculate overhead cost for one production run.

        If a fixed overhead_cost is set, returns that directly.
        If overhead_percent is set, calculates as percentage of material cost.
        Otherwise returns Decimal('0.00').

        Returns:
            Decimal: Overhead cost allocation.
        """
        if self._overhead_cost is not None:
            return self._overhead_cost

        if self._overhead_percent is not None:
            material_cost = self.calculate_with_wastage()
            return (material_cost * self._overhead_percent / Decimal("100")).quantize(
                Decimal("0.01")
            )

        return Decimal("0.00")

    def calculate_total_cost(self):
        """
        Calculate total manufacturing cost per production run.

        Total = Material (with wastage) + Labor + Overhead

        Returns:
            Decimal: Total manufacturing cost.
        """
        material = self.calculate_with_wastage()
        labor = self.calculate_labor_cost()
        overhead = self.calculate_overhead()
        return material + labor + overhead

    def calculate_unit_cost(self):
        """
        Calculate manufacturing cost per output unit.

        Unit Cost = Total Cost / yield_quantity

        Returns:
            Decimal: Cost per unit produced, rounded to 2 decimal places.
        """
        total = self.calculate_total_cost()
        yield_qty = self.bom.yield_quantity or 1
        return (total / Decimal(str(yield_qty))).quantize(Decimal("0.01"))

    def suggest_selling_price(self, margin_percent=30):
        """
        Suggest a selling price based on unit cost and target margin.

        Price = Unit Cost × (1 + margin_percent / 100)

        Args:
            margin_percent: Target profit margin percentage (default: 30%).

        Returns:
            dict: Contains 'unit_cost', 'selling_price', and 'margin_percent'.
        """
        unit_cost = self.calculate_unit_cost()
        margin = Decimal(str(margin_percent))
        selling_price = (unit_cost * (Decimal("1") + margin / Decimal("100"))).quantize(
            Decimal("0.01")
        )

        return {
            "unit_cost": unit_cost,
            "selling_price": selling_price,
            "margin_percent": margin,
        }


class ManufacturingStockService:
    """
    Service for checking raw material availability for manufacturing.

    Determines how many batches of a composite product can be manufactured
    based on current raw material stock levels.
    """

    def __init__(self, bom):
        """
        Initialize with a BillOfMaterials instance.

        Args:
            bom: BillOfMaterials instance.
        """
        self.bom = bom

    def check_raw_materials(self):
        """
        Check availability of all raw materials for one production run.

        Returns:
            list[dict]: Status of each raw material with keys:
                - 'item': BOMItem instance
                - 'required': Decimal quantity needed (with wastage)
                - 'available': Current stock quantity
                - 'sufficient': bool whether enough stock exists
                - 'substitute_available': bool if substitute has stock
        """
        results = []
        items = self.bom.items.select_related("raw_material", "substitute").all()

        for item in items:
            wastage_multiplier = Decimal("1") + (item.wastage_percent / Decimal("100"))
            required = item.quantity * wastage_multiplier

            available = Decimal("0")
            if hasattr(item.raw_material, "stock_quantity"):
                available = Decimal(str(item.raw_material.stock_quantity))

            sufficient = available >= required

            substitute_available = False
            if not sufficient and item.substitute_id:
                sub_stock = Decimal("0")
                if hasattr(item.substitute, "stock_quantity"):
                    sub_stock = Decimal(str(item.substitute.stock_quantity))
                substitute_available = sub_stock >= required

            results.append({
                "item": item,
                "required": required,
                "available": available,
                "sufficient": sufficient,
                "substitute_available": substitute_available,
            })

        return results

    def get_producible_quantity(self):
        """
        Calculate maximum number of finished units that can be produced.

        Considers all BOM items, their wastage, and available stock to
        determine the bottleneck and maximum output.

        Returns:
            int: Maximum number of finished units producible.
        """
        items = self.bom.items.select_related("raw_material").all()
        if not items.exists():
            return 0

        yield_qty = self.bom.yield_quantity or 1
        min_batches = None

        for item in items:
            wastage_multiplier = Decimal("1") + (item.wastage_percent / Decimal("100"))
            required_per_batch = item.quantity * wastage_multiplier

            available = Decimal("0")
            if hasattr(item.raw_material, "stock_quantity"):
                available = Decimal(str(item.raw_material.stock_quantity))

            if required_per_batch <= 0:
                continue

            possible_batches = int(available / required_per_batch)

            if min_batches is None:
                min_batches = possible_batches
            else:
                min_batches = min(min_batches, possible_batches)

        if min_batches is None:
            return 0

        return min_batches * yield_qty
