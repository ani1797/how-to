"""Workshop agents (customer service, inventory, order processing, returns)."""

from .base import BaseAgent
from .customer_service import CustomerServiceAgent
from .inventory import InventoryAgent
from .order_processing import OrderProcessingAgent
from .returns import ReturnsAgent

__all__ = [
    "BaseAgent",
    "CustomerServiceAgent",
    "InventoryAgent",
    "OrderProcessingAgent",
    "ReturnsAgent",
]
