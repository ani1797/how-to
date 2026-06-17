"""In-memory mock data for the workshop.

The numbers/IDs are intentionally small so participants can refer to them
during demos. Order/refund records are mutated by the agent tools so they
demonstrate write paths end-to-end.
"""
from __future__ import annotations

from typing import Dict, List

from .models import Customer, CustomerTier, InventoryItem, Order, Product

CUSTOMERS: Dict[str, Customer] = {
    "CUST-001": Customer(
        customer_id="CUST-001",
        name="Jane Doe",
        email="jane.doe@example.com",
        phone="+1-555-0101",
        tier=CustomerTier.GOLD,
        consent_given=True,
    ),
    "CUST-002": Customer(
        customer_id="CUST-002",
        name="John Smith",
        email="john.smith@example.com",
        phone="+1-555-0102",
        tier=CustomerTier.SILVER,
        consent_given=False,
    ),
    "CUST-003": Customer(
        customer_id="CUST-003",
        name="Aisha Khan",
        email="aisha.khan@example.com",
        phone="+1-555-0103",
        tier=CustomerTier.PLATINUM,
        consent_given=True,
    ),
}

PRODUCTS: Dict[str, Product] = {
    "SKU-100": Product(
        product_id="SKU-100",
        name="Wireless Headphones",
        cost=50.0,
        price=199.99,
        minimum_advertised_price=149.99,
    ),
    "SKU-200": Product(
        product_id="SKU-200",
        name="Smart Watch",
        cost=120.0,
        price=399.99,
        minimum_advertised_price=299.99,
    ),
    "SKU-300": Product(
        product_id="SKU-300",
        name="Bluetooth Speaker",
        cost=25.0,
        price=89.99,
        minimum_advertised_price=59.99,
    ),
}

INVENTORY: Dict[tuple, InventoryItem] = {
    ("SKU-100", "STORE-NYC"): InventoryItem(
        product_id="SKU-100", location="STORE-NYC", quantity=42
    ),
    ("SKU-100", "WAREHOUSE-EAST"): InventoryItem(
        product_id="SKU-100", location="WAREHOUSE-EAST", quantity=1500
    ),
    ("SKU-200", "STORE-NYC"): InventoryItem(product_id="SKU-200", location="STORE-NYC", quantity=8),
    ("SKU-300", "STORE-NYC"): InventoryItem(
        product_id="SKU-300", location="STORE-NYC", quantity=120
    ),
}

ORDERS: Dict[str, Order] = {
    "ORD-001": Order(
        order_id="ORD-001",
        customer_id="CUST-001",
        amount=349.98,
        days_since_purchase=5,
        has_receipt=True,
    ),
    "ORD-002": Order(
        order_id="ORD-002",
        customer_id="CUST-002",
        amount=89.99,
        days_since_purchase=45,
        has_receipt=False,
    ),
    "ORD-003": Order(
        order_id="ORD-003",
        customer_id="CUST-003",
        amount=1299.50,
        days_since_purchase=10,
        has_receipt=True,
    ),
}


def get_customer(customer_id: str) -> Customer:
    if customer_id not in CUSTOMERS:
        raise LookupError(f"Customer {customer_id} not found")
    return CUSTOMERS[customer_id]


def get_product(product_id: str) -> Product:
    if product_id not in PRODUCTS:
        raise LookupError(f"Product {product_id} not found")
    return PRODUCTS[product_id]


def get_inventory(product_id: str, location: str) -> InventoryItem:
    key = (product_id, location)
    if key not in INVENTORY:
        raise LookupError(f"No inventory for {product_id} at {location}")
    return INVENTORY[key]


def get_order(order_id: str) -> Order:
    if order_id not in ORDERS:
        raise LookupError(f"Order {order_id} not found")
    return ORDERS[order_id]


def list_inventory(product_id: str) -> List[InventoryItem]:
    return [item for (pid, _), item in INVENTORY.items() if pid == product_id]
