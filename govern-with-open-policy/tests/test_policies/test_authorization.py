"""Tests for OPA-A (authorization) policies — exercised via a live OPA server.

Requires `docker-compose up -d` so OPA is reachable on localhost:8181.
"""

from __future__ import annotations

import pytest

from src.opa import OPAClient


@pytest.fixture(scope="module")
def opa() -> OPAClient:
    client = OPAClient()
    if not client.health_check():
        pytest.skip("OPA server not running on http://localhost:8181")
    return client


def _evaluate(
    opa: OPAClient,
    agent_role: str,
    action: str,
    resource: dict,
    location: str = "STORE-NYC",
    context: dict | None = None,
) -> bool:
    decision = opa.evaluate(
        "retail/authorization",
        {
            "agent": {
                "agent_id": "test",
                "agent_type": "test",
                "role": agent_role,
                "location": location,
                "trust_level": 3,
            },
            "action": action,
            "resource": resource,
            "context": context or {},
        },
    )
    return decision.allow


# ---------------------------------------------------------------------------
# Customer Service
# ---------------------------------------------------------------------------


def test_pii_allowed_with_consent(opa):
    assert _evaluate(
        opa, "customer_service", "access_pii", {"type": "customer_pii", "consent_given": True}
    )


def test_pii_denied_without_consent(opa):
    assert not _evaluate(
        opa, "customer_service", "access_pii", {"type": "customer_pii", "consent_given": False}
    )


def test_pii_denied_for_cashier(opa):
    assert not _evaluate(
        opa, "cashier", "access_pii", {"type": "customer_pii", "consent_given": True}
    )


# ---------------------------------------------------------------------------
# Inventory
# ---------------------------------------------------------------------------


def test_warehouse_staff_can_read_inventory(opa):
    assert _evaluate(opa, "warehouse_staff", "read", {"type": "inventory", "product_id": "SKU-100"})


def test_warehouse_staff_transfer_own_location(opa):
    assert _evaluate(
        opa,
        "warehouse_staff",
        "transfer",
        {"type": "inventory", "location": "STORE-NYC", "quantity": 10},
        location="STORE-NYC",
    )


def test_warehouse_staff_transfer_other_location_denied(opa):
    assert not _evaluate(
        opa,
        "warehouse_staff",
        "transfer",
        {"type": "inventory", "location": "STORE-NYC", "quantity": 10},
        location="WAREHOUSE-EAST",
    )


# ---------------------------------------------------------------------------
# Order Processing
# ---------------------------------------------------------------------------


def test_cashier_order_within_limit(opa):
    assert _evaluate(opa, "cashier", "process_order", {"type": "transaction", "amount": 450.0})


def test_cashier_order_exceeds_limit(opa):
    assert not _evaluate(opa, "cashier", "process_order", {"type": "transaction", "amount": 750.0})


def test_cashier_discount_within_cap(opa):
    assert _evaluate(
        opa,
        "cashier",
        "apply_discount",
        {"type": "price", "original_price": 100.0, "new_price": 92.0},
    )


def test_cashier_discount_over_cap(opa):
    assert not _evaluate(
        opa,
        "cashier",
        "apply_discount",
        {"type": "price", "original_price": 100.0, "new_price": 80.0},
    )


# ---------------------------------------------------------------------------
# Refunds
# ---------------------------------------------------------------------------


def test_cashier_refund_within_limit(opa):
    assert _evaluate(
        opa,
        "cashier",
        "process_refund",
        {"type": "refund", "amount": 50.0, "days_since_purchase": 10, "has_receipt": True},
    )


def test_cashier_refund_exceeds_limit(opa):
    assert not _evaluate(
        opa,
        "cashier",
        "process_refund",
        {"type": "refund", "amount": 250.0, "days_since_purchase": 10, "has_receipt": True},
    )


# ---------------------------------------------------------------------------
# Admin
# ---------------------------------------------------------------------------


def test_admin_can_do_anything(opa):
    assert _evaluate(opa, "admin", "anything", {"type": "anything"})
