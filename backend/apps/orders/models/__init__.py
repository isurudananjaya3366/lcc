"""
Orders models package.
"""

from apps.orders.models.order import Order
from apps.orders.models.order_item import OrderLineItem
from apps.orders.models.history import OrderHistory
from apps.orders.models.settings import OrderSettings
from apps.orders.models.fulfillment import Fulfillment
from apps.orders.models.fulfillment_item import FulfillmentLineItem
from apps.orders.models.order_return import OrderReturn, ReturnLineItem
from apps.orders.services.order_number_generator import OrderSequence

# Legacy alias
OrderItem = OrderLineItem

__all__ = [
    "Fulfillment",
    "FulfillmentLineItem",
    "Order",
    "OrderHistory",
    "OrderItem",
    "OrderLineItem",
    "OrderReturn",
    "OrderSequence",
    "OrderSettings",
    "ReturnLineItem",
]
