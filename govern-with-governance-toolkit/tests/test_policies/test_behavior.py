"""Tests for AGT-B behavior rules."""
import pytest

from src.agents.inventory import InventoryAgent
from src.agents.order_processing import OrderProcessingAgent
from src.agents.returns import ReturnsAgent
from src.models import AgentRole


class TestRateLimit:
    def test_rate_limit_blocks_after_100_actions(self):
        agent = InventoryAgent(role=AgentRole.WAREHOUSE_MANAGER)
        # Pre-fill recent_actions with 101 entries
        agent._recent_actions = [{"action": "read"}] * 101
        result = agent.invoke_tool(
            "check_stock", {"product_id": "SKU-100", "location": "STORE-NYC"}
        )
        assert result["ok"] is False
        assert result["denied_by"] == "AGT-B"
        assert "rate" in result["reason"].lower()


class TestLargeTransfer:
    def test_manager_allowed_large_transfer(self):
        agent = InventoryAgent(role=AgentRole.WAREHOUSE_MANAGER)
        result = agent.invoke_tool(
            "transfer_inventory",
            {"product_id": "SKU-100", "from_location": "WAREHOUSE-EAST",
             "to_location": "STORE-NYC", "quantity": 600},
        )
        assert result["ok"] is True

    def test_warehouse_staff_blocked_very_large_transfer(self):
        agent = InventoryAgent(role=AgentRole.WAREHOUSE_STAFF)
        result = agent.invoke_tool(
            "transfer_inventory",
            {"product_id": "SKU-100", "from_location": "WAREHOUSE-EAST",
             "to_location": "STORE-NYC", "quantity": 600},
        )
        assert result["ok"] is False
        assert result["denied_by"] in ("AGT-A", "AGT-B")


class TestPricingRules:
    def test_below_cost_blocked(self):
        # SKU-300: price=89.99, cost=25.0 => 75% discount => new_price=22.50 < cost
        agent = OrderProcessingAgent(role=AgentRole.STORE_MANAGER)
        result = agent.invoke_tool(
            "apply_discount", {"product_id": "SKU-300", "discount_percent": 75.0}
        )
        assert result["ok"] is False
        assert result["denied_by"] == "AGT-B"
        assert "cost" in result["reason"].lower()

    def test_below_map_blocked(self):
        # SKU-100: price=199.99, MAP=149.99 => 30% off => 139.99 < MAP
        agent = OrderProcessingAgent(role=AgentRole.STORE_MANAGER)
        result = agent.invoke_tool(
            "apply_discount", {"product_id": "SKU-100", "discount_percent": 30.0}
        )
        assert result["ok"] is False
        assert result["denied_by"] == "AGT-B"

    def test_valid_discount_allowed(self):
        # SKU-300: price=89.99, 10% off => 80.99, cost=25, MAP=59.99 => all good
        agent = OrderProcessingAgent(role=AgentRole.STORE_MANAGER)
        result = agent.invoke_tool(
            "apply_discount", {"product_id": "SKU-300", "discount_percent": 10.0}
        )
        assert result["ok"] is True


class TestRefundRules:
    def test_late_refund_blocked(self):
        # ORD-002: 45 days since purchase
        agent = ReturnsAgent(role=AgentRole.STORE_MANAGER)
        result = agent.invoke_tool(
            "process_refund", {"order_id": "ORD-002", "amount": 89.99}
        )
        assert result["ok"] is False
        assert result["denied_by"] == "AGT-B"
        assert "30" in result["reason"] or "day" in result["reason"].lower()

    def test_no_receipt_high_refund_blocked(self):
        # ORD-002: no receipt, amount=89.99 > 50 => blocked
        agent = ReturnsAgent(role=AgentRole.ADMIN)
        # Temporarily patch days_since_purchase to avoid the 30-day rule
        from src import mock_data
        orig = mock_data.ORDERS["ORD-002"].days_since_purchase
        mock_data.ORDERS["ORD-002"].days_since_purchase = 5
        try:
            result = agent.invoke_tool(
                "process_refund", {"order_id": "ORD-002", "amount": 89.99}
            )
            assert result["ok"] is False
            assert result["denied_by"] == "AGT-B"
        finally:
            mock_data.ORDERS["ORD-002"].days_since_purchase = orig

    def test_valid_refund_allowed(self):
        # ORD-001: 5 days, has receipt, amount=30 < 349.98
        agent = ReturnsAgent(role=AgentRole.STORE_MANAGER)
        result = agent.invoke_tool(
            "process_refund", {"order_id": "ORD-001", "amount": 30.0}
        )
        assert result["ok"] is True
