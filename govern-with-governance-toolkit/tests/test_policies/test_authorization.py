"""Tests for AGT-A authorization rules."""
import pytest

from src.agents.customer_service import CustomerServiceAgent
from src.agents.inventory import InventoryAgent
from src.agents.order_processing import OrderProcessingAgent
from src.agents.returns import ReturnsAgent
from src.models import AgentRole


# ---------------------------------------------------------------------------
# CustomerService
# ---------------------------------------------------------------------------

class TestPIIAccess:
    def test_customer_service_can_access_consented_pii(self):
        agent = CustomerServiceAgent(role=AgentRole.CUSTOMER_SERVICE)
        result = agent.invoke_tool("access_customer_pii", {"customer_id": "CUST-001"})
        assert result["ok"] is True
        assert "email" in result["result"]

    def test_cashier_blocked_from_pii(self):
        agent = CustomerServiceAgent(role=AgentRole.CASHIER)
        result = agent.invoke_tool("access_customer_pii", {"customer_id": "CUST-001"})
        assert result["ok"] is False
        assert result["denied_by"] == "AGT-A"
        assert "cashier" in result["reason"].lower()

    def test_pii_blocked_without_consent(self):
        agent = CustomerServiceAgent(role=AgentRole.CUSTOMER_SERVICE)
        result = agent.invoke_tool("access_customer_pii", {"customer_id": "CUST-002"})
        assert result["ok"] is False
        assert result["denied_by"] == "AGT-A"
        assert "consent" in result["reason"].lower()

    def test_admin_can_access_pii(self):
        agent = CustomerServiceAgent(role=AgentRole.ADMIN)
        result = agent.invoke_tool("access_customer_pii", {"customer_id": "CUST-001"})
        assert result["ok"] is True


class TestTierUpdate:
    def test_cashier_blocked_from_update(self):
        agent = CustomerServiceAgent(role=AgentRole.CASHIER)
        result = agent.invoke_tool(
            "update_customer_tier",
            {"customer_id": "CUST-001", "new_tier": "platinum", "reason": "test"},
        )
        assert result["ok"] is False
        assert result["denied_by"] == "AGT-A"

    def test_customer_service_can_update(self):
        agent = CustomerServiceAgent(role=AgentRole.CUSTOMER_SERVICE)
        result = agent.invoke_tool(
            "update_customer_tier",
            {"customer_id": "CUST-001", "new_tier": "silver", "reason": "test"},
        )
        assert result["ok"] is True


# ---------------------------------------------------------------------------
# Inventory
# ---------------------------------------------------------------------------

class TestInventoryTransfer:
    def test_cashier_blocked_from_transfer(self):
        agent = InventoryAgent(role=AgentRole.CASHIER)
        result = agent.invoke_tool(
            "transfer_inventory",
            {"product_id": "SKU-100", "from_location": "WAREHOUSE-EAST",
             "to_location": "STORE-NYC", "quantity": 5},
        )
        assert result["ok"] is False
        assert result["denied_by"] == "AGT-A"

    def test_warehouse_staff_blocked_over_100_units(self):
        agent = InventoryAgent(role=AgentRole.WAREHOUSE_STAFF)
        result = agent.invoke_tool(
            "transfer_inventory",
            {"product_id": "SKU-100", "from_location": "WAREHOUSE-EAST",
             "to_location": "STORE-NYC", "quantity": 101},
        )
        assert result["ok"] is False
        assert result["denied_by"] == "AGT-A"

    def test_warehouse_staff_allowed_under_100_units(self):
        agent = InventoryAgent(role=AgentRole.WAREHOUSE_STAFF)
        result = agent.invoke_tool(
            "transfer_inventory",
            {"product_id": "SKU-100", "from_location": "WAREHOUSE-EAST",
             "to_location": "STORE-NYC", "quantity": 50},
        )
        assert result["ok"] is True

    def test_cashier_blocked_from_adjust(self):
        agent = InventoryAgent(role=AgentRole.CASHIER)
        result = agent.invoke_tool(
            "adjust_inventory",
            {"product_id": "SKU-100", "location": "STORE-NYC",
             "delta": -5, "reason": "shrinkage"},
        )
        assert result["ok"] is False
        assert result["denied_by"] == "AGT-A"


# ---------------------------------------------------------------------------
# OrderProcessing
# ---------------------------------------------------------------------------

class TestOrderProcessing:
    def test_cashier_blocked_high_value_order(self):
        agent = OrderProcessingAgent(role=AgentRole.CASHIER)
        result = agent.invoke_tool(
            "process_order", {"customer_id": "CUST-001", "amount": 600.0}
        )
        assert result["ok"] is False
        assert result["denied_by"] == "AGT-A"

    def test_cashier_allowed_low_value_order(self):
        agent = OrderProcessingAgent(role=AgentRole.CASHIER)
        result = agent.invoke_tool(
            "process_order", {"customer_id": "CUST-001", "amount": 100.0}
        )
        assert result["ok"] is True

    def test_cashier_blocked_high_discount(self):
        agent = OrderProcessingAgent(role=AgentRole.CASHIER)
        result = agent.invoke_tool(
            "apply_discount", {"product_id": "SKU-100", "discount_percent": 15.0}
        )
        assert result["ok"] is False
        assert result["denied_by"] == "AGT-A"

    def test_cashier_allowed_low_discount(self):
        agent = OrderProcessingAgent(role=AgentRole.CASHIER)
        result = agent.invoke_tool(
            "apply_discount", {"product_id": "SKU-300", "discount_percent": 5.0}
        )
        assert result["ok"] is True


# ---------------------------------------------------------------------------
# Returns
# ---------------------------------------------------------------------------

class TestReturns:
    def test_cashier_blocked_high_refund(self):
        agent = ReturnsAgent(role=AgentRole.CASHIER)
        result = agent.invoke_tool(
            "process_refund", {"order_id": "ORD-001", "amount": 150.0}
        )
        assert result["ok"] is False
        assert result["denied_by"] == "AGT-A"

    def test_cashier_allowed_low_refund(self):
        agent = ReturnsAgent(role=AgentRole.CASHIER)
        result = agent.invoke_tool(
            "process_refund", {"order_id": "ORD-001", "amount": 50.0}
        )
        assert result["ok"] is True
