"""Returns & Refunds agent — eligibility check + refund processing."""
from __future__ import annotations

from .. import mock_data
from ..models import ActionType, AgentRole
from ..governance.enforcer import tool
from .base import BaseAgent


class ReturnsAgent(BaseAgent):
    """AI agent that evaluates and processes refund requests."""

    AGENT_TYPE = "returns"
    DEFAULT_ROLE = AgentRole.CASHIER

    @tool("Check whether an order qualifies for a refund without processing it.")
    def check_return_eligibility(self, order_id: str) -> dict:
        order = mock_data.get_order(order_id)
        self.enforce(
            ActionType.READ,
            resource={"type": "order", "order_id": order_id},
        )
        reasons = []
        if order.days_since_purchase > 30:
            reasons.append("outside 30-day return window")
        if not order.has_receipt and order.amount > 50:
            reasons.append("refund > $50 requires a receipt")
        return {
            "order_id": order_id,
            "amount": order.amount,
            "days_since_purchase": order.days_since_purchase,
            "has_receipt": order.has_receipt,
            "eligible": len(reasons) == 0,
            "issues": reasons,
        }

    @tool(
        "Process a refund for an order. AGT-A enforces per-role refund caps; "
        "AGT-B blocks no-receipt refunds above $50."
    )
    def process_refund(self, order_id: str, amount: float) -> dict:
        order = mock_data.get_order(order_id)
        if amount > order.amount:
            raise LookupError(f"Refund {amount} exceeds order total {order.amount}")

        self.enforce(
            ActionType.PROCESS_REFUND,
            resource={
                "type": "refund",
                "order_id": order_id,
                "amount": amount,
                "days_since_purchase": order.days_since_purchase,
                "has_receipt": order.has_receipt,
            },
        )
        return {
            "order_id": order_id,
            "refund_amount": amount,
            "status": "refunded",
            "processed_by": self.agent_id,
        }
