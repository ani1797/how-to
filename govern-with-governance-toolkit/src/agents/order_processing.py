"""Order Processing agent — process orders, apply discounts, look up orders."""
from __future__ import annotations

from .. import mock_data
from ..models import ActionType, AgentRole, Order
from ..governance.enforcer import tool
from .base import BaseAgent


class OrderProcessingAgent(BaseAgent):
    """AI agent that creates and reviews retail orders."""

    AGENT_TYPE = "order_processing"
    DEFAULT_ROLE = AgentRole.CASHIER

    @tool(
        "Process a new order for a customer. Amount is the total in dollars. "
        "AGT-A enforces per-role transaction-amount caps."
    )
    def process_order(self, customer_id: str, amount: float) -> dict:
        mock_data.get_customer(customer_id)

        self.enforce(
            ActionType.PROCESS_ORDER,
            resource={
                "type": "transaction",
                "customer_id": customer_id,
                "amount": amount,
                "has_approval": False,
            },
        )

        order_id = f"ORD-{len(mock_data.ORDERS) + 1:03d}"
        mock_data.ORDERS[order_id] = Order(
            order_id=order_id,
            customer_id=customer_id,
            amount=amount,
            days_since_purchase=0,
            has_receipt=True,
        )
        return {
            "order_id": order_id,
            "customer_id": customer_id,
            "amount": amount,
            "status": "confirmed",
        }

    @tool(
        "Apply a percent discount to a product. AGT-A caps the discount per role; "
        "AGT-B prevents selling below cost or below MAP."
    )
    def apply_discount(self, product_id: str, discount_percent: float) -> dict:
        product = mock_data.get_product(product_id)
        new_price = round(product.price * (1 - discount_percent / 100.0), 2)

        self.enforce(
            ActionType.APPLY_DISCOUNT,
            resource={
                "type": "price",
                "product_id": product_id,
                "original_price": product.price,
                "new_price": new_price,
                "cost": product.cost,
                "minimum_advertised_price": product.minimum_advertised_price,
            },
            context={"manager_approved": False, "special_promotion": False},
        )
        return {
            "product_id": product_id,
            "original_price": product.price,
            "discount_percent": discount_percent,
            "new_price": new_price,
        }

    @tool("Look up an existing order by id.")
    def lookup_order(self, order_id: str) -> dict:
        self.enforce(
            ActionType.READ,
            resource={"type": "order", "order_id": order_id},
        )
        order = mock_data.get_order(order_id)
        return order.model_dump()
