"""Inventory agent — stock check, transfers, adjustments."""

from __future__ import annotations

from .. import mock_data
from ..models import ActionType, AgentRole
from ..policy import tool
from .base import BaseAgent


class InventoryAgent(BaseAgent):
    """Warehouse AI agent for inventory operations."""

    AGENT_TYPE = "inventory"
    DEFAULT_ROLE = AgentRole.WAREHOUSE_STAFF

    # ------------------------------------------------------------------
    @tool("Check current stock quantity for a product at a given location.")
    def check_stock(self, product_id: str, location: str) -> dict:
        self.enforce(
            ActionType.READ,
            resource={"type": "inventory", "product_id": product_id, "location": location},
        )
        item = mock_data.get_inventory(product_id, location)
        return {
            "product_id": item.product_id,
            "location": item.location,
            "quantity": item.quantity,
        }

    # ------------------------------------------------------------------
    @tool("Transfer units of a product from one location to another.")
    def transfer_inventory(
        self,
        product_id: str,
        from_location: str,
        to_location: str,
        quantity: int,
    ) -> dict:
        src = mock_data.get_inventory(product_id, from_location)
        if src.quantity < quantity:
            raise LookupError(
                f"Insufficient stock at {from_location}: have {src.quantity}, need {quantity}"
            )

        # OPA-A checks role-based transfer permission; OPA-B enforces large-transfer rule.
        self.enforce(
            ActionType.TRANSFER,
            resource={
                "type": "inventory",
                "product_id": product_id,
                "location": from_location,
                "to_location": to_location,
                "quantity": quantity,
            },
        )

        src.quantity -= quantity
        dst_key = (product_id, to_location)
        if dst_key in mock_data.INVENTORY:
            mock_data.INVENTORY[dst_key].quantity += quantity
        else:
            from ..models import InventoryItem

            mock_data.INVENTORY[dst_key] = InventoryItem(
                product_id=product_id, location=to_location, quantity=quantity
            )
        return {
            "product_id": product_id,
            "from": from_location,
            "to": to_location,
            "quantity": quantity,
            "remaining_at_source": src.quantity,
        }

    # ------------------------------------------------------------------
    @tool(
        "Adjust on-hand inventory quantity for a product at a location "
        "(e.g. after a stock count). Positive or negative delta."
    )
    def adjust_inventory(self, product_id: str, location: str, delta: int, reason: str) -> dict:
        item = mock_data.get_inventory(product_id, location)
        new_qty = item.quantity + delta

        self.enforce(
            ActionType.ADJUST_INVENTORY,
            resource={
                "type": "inventory",
                "product_id": product_id,
                "location": location,
                "delta": delta,
                "new_quantity": new_qty,
            },
            context={"reason": reason},
        )

        item.quantity = max(0, new_qty)
        return {
            "product_id": product_id,
            "location": location,
            "delta": delta,
            "new_quantity": item.quantity,
            "reason": reason,
        }
