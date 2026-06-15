"""End-to-end behaviour evals for the policy-enforced agents.

These tests drive each agent's tool methods directly (no LLM) against the
**live** OPA server. They double as both functional tests AND policy evals:
every assertion confirms that OPA-A or OPA-B produces the expected decision.

Run with::

    docker-compose up -d opa
    pytest tests/test_agents -v
"""

from __future__ import annotations

import pytest
import requests

from src.agents import (
    CustomerServiceAgent,
    InventoryAgent,
    OrderProcessingAgent,
    ReturnsAgent,
)
from src.config import get_settings
from src.models import AgentRole


# ---------------------------------------------------------------------------
# Shared fixture: skip the whole suite if OPA isn't reachable
# ---------------------------------------------------------------------------


@pytest.fixture(scope="module", autouse=True)
def opa_health_check() -> None:
    settings = get_settings()
    try:
        r = requests.get(f"{settings.opa_url}/health", timeout=2)
        r.raise_for_status()
    except Exception as exc:  # noqa: BLE001
        pytest.skip(f"OPA not reachable at {settings.opa_url}: {exc}")


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _allowed(result: dict) -> dict:
    """Assert the @tool call was allowed by policy and return its payload."""
    assert result.get("ok") is True, f"expected ok=True, got {result}"
    return result["result"]


def _denied(result: dict, *, by: str | None = None) -> dict:
    """Assert the @tool call was denied; optionally check which phase."""
    assert result.get("ok") is False, f"expected ok=False, got {result}"
    assert "denied_by" in result, f"missing denied_by in {result}"
    if by is not None:
        assert result["denied_by"] == by, (
            f"expected denied_by={by!r}, got {result['denied_by']!r}"
        )
    return result


# ---------------------------------------------------------------------------
# Customer Service: PII access requires consent
# ---------------------------------------------------------------------------


class TestCustomerServiceAgent:
    def setup_method(self) -> None:
        self.agent = CustomerServiceAgent()

    def test_pii_allowed_with_consent(self) -> None:
        payload = _allowed(
            self.agent.invoke_tool(
                "access_customer_pii", {"customer_id": "CUST-001"}
            )
        )
        assert "email" in payload and "@" in payload["email"]

    def test_pii_denied_without_consent(self) -> None:
        _denied(
            self.agent.invoke_tool(
                "access_customer_pii", {"customer_id": "CUST-002"}
            ),
            by="OPA-A",
        )

    def test_profile_view_does_not_need_consent(self) -> None:
        payload = _allowed(
            self.agent.invoke_tool(
                "view_customer_profile", {"customer_id": "CUST-002"}
            )
        )
        assert "name" in payload

    def test_tier_update_requires_privileged_role(self) -> None:
        # A cashier should NOT be able to promote customers.
        cashier = CustomerServiceAgent(
            role=AgentRole.CASHIER
        )
        _denied(
            cashier.invoke_tool(
                "update_customer_tier",
                {
                    "customer_id": "CUST-001",
                    "new_tier": "platinum",
                    "reason": "loyalty milestone",
                },
            ),
            by="OPA-A",
        )

        # Manager-role agent is allowed
        mgr = CustomerServiceAgent(
            role=AgentRole.STORE_MANAGER
        )
        _allowed(
            mgr.invoke_tool(
                "update_customer_tier",
                {
                    "customer_id": "CUST-001",
                    "new_tier": "platinum",
                    "reason": "loyalty milestone",
                },
            )
        )


# ---------------------------------------------------------------------------
# Inventory: location-bound + bulk-transfer behaviour rules
# ---------------------------------------------------------------------------


class TestInventoryAgent:
    def test_transfer_from_assigned_location_allowed(self) -> None:
        staff = InventoryAgent(
            role=AgentRole.WAREHOUSE_STAFF,
            location="WAREHOUSE-EAST",
        )
        _allowed(
            staff.invoke_tool(
                "transfer_inventory",
                {
                    "product_id": "SKU-100",
                    "from_location": "WAREHOUSE-EAST",
                    "to_location": "STORE-NYC",
                    "quantity": 10,
                },
            )
        )

    def test_transfer_from_other_location_denied(self) -> None:
        staff = InventoryAgent(
            role=AgentRole.WAREHOUSE_STAFF,
            location="WAREHOUSE-EAST",
        )
        _denied(
            staff.invoke_tool(
                "transfer_inventory",
                {
                    "product_id": "SKU-100",
                    "from_location": "STORE-NYC",
                    "to_location": "WAREHOUSE-EAST",
                    "quantity": 5,
                },
            ),
            by="OPA-A",
        )

    def test_large_transfer_requires_manager(self) -> None:
        # Staff transferring 1100 units → OPA-B should deny (>1000 threshold).
        staff = InventoryAgent(
            role=AgentRole.WAREHOUSE_STAFF,
            location="WAREHOUSE-EAST",
        )
        _denied(
            staff.invoke_tool(
                "transfer_inventory",
                {
                    "product_id": "SKU-100",
                    "from_location": "WAREHOUSE-EAST",
                    "to_location": "STORE-NYC",
                    "quantity": 1100,
                },
            ),
            by="OPA-B",
        )

        # Manager doing the same large transfer → allowed.
        mgr = InventoryAgent(
            role=AgentRole.WAREHOUSE_MANAGER,
            location="WAREHOUSE-EAST",
        )
        _allowed(
            mgr.invoke_tool(
                "transfer_inventory",
                {
                    "product_id": "SKU-100",
                    "from_location": "WAREHOUSE-EAST",
                    "to_location": "STORE-NYC",
                    "quantity": 1100,
                },
            )
        )


# ---------------------------------------------------------------------------
# Order processing: amount cap + discount cap
# ---------------------------------------------------------------------------


class TestOrderProcessingAgent:
    def setup_method(self) -> None:
        self.cashier = OrderProcessingAgent(
            role=AgentRole.CASHIER
        )
        self.manager = OrderProcessingAgent(
            role=AgentRole.STORE_MANAGER
        )

    def test_small_order_allowed_for_cashier(self) -> None:
        _allowed(
            self.cashier.invoke_tool(
                "process_order", {"customer_id": "CUST-001", "amount": 250.0}
            )
        )

    def test_large_order_denied_for_cashier(self) -> None:
        _denied(
            self.cashier.invoke_tool(
                "process_order", {"customer_id": "CUST-001", "amount": 1500.0}
            ),
            by="OPA-A",
        )

    def test_large_order_allowed_for_manager(self) -> None:
        _allowed(
            self.manager.invoke_tool(
                "process_order", {"customer_id": "CUST-001", "amount": 1500.0}
            )
        )

    def test_small_discount_allowed_for_cashier(self) -> None:
        _allowed(
            self.cashier.invoke_tool(
                "apply_discount", {"product_id": "SKU-100", "discount_percent": 8.0}
            )
        )

    def test_large_discount_denied_for_cashier(self) -> None:
        _denied(
            self.cashier.invoke_tool(
                "apply_discount", {"product_id": "SKU-100", "discount_percent": 30.0}
            ),
            by="OPA-A",
        )


# ---------------------------------------------------------------------------
# Returns: cap + receipt + days-since-purchase behaviour
# ---------------------------------------------------------------------------


class TestReturnsAgent:
    def setup_method(self) -> None:
        self.cashier = ReturnsAgent(
            role=AgentRole.CASHIER
        )
        self.manager = ReturnsAgent(
            role=AgentRole.STORE_MANAGER
        )

    def test_small_refund_with_receipt_allowed_for_cashier(self) -> None:
        _allowed(
            self.cashier.invoke_tool(
                "process_refund", {"order_id": "ORD-001", "amount": 50.0}
            )
        )

    def test_refund_over_cashier_cap_denied(self) -> None:
        _denied(
            self.cashier.invoke_tool(
                "process_refund", {"order_id": "ORD-001", "amount": 200.0}
            ),
            by="OPA-A",
        )

    def test_no_receipt_large_refund_denied(self) -> None:
        # ORD-002: no receipt, 45 days old → cashier refund $80 should deny.
        _denied(
            self.cashier.invoke_tool(
                "process_refund", {"order_id": "ORD-002", "amount": 80.0}
            ),
            by="OPA-A",
        )

    def test_manager_can_refund_full_order(self) -> None:
        _allowed(
            self.manager.invoke_tool(
                "process_refund", {"order_id": "ORD-001", "amount": 349.98}
            )
        )
