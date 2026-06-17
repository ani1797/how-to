"""Validate that governance policies are working correctly post-deploy.

Runs a quick smoke test of each agent through the key allow/deny scenarios.
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.agents import (
    CustomerServiceAgent, InventoryAgent,
    OrderProcessingAgent, ReturnsAgent,
)
from src.models import AgentRole

PASS = "PASS"
FAIL = "FAIL"


def check(label: str, result: dict, expect_ok: bool) -> bool:
    ok = result.get("ok", True) is not False
    passed = ok == expect_ok
    status = PASS if passed else FAIL
    print(f"  [{status}] {label}")
    if not passed:
        print(f"         expected ok={expect_ok}, got: {result}")
    return passed


def main() -> None:
    print("=== Governance Validation ===\n")
    results = []

    cs_cs = CustomerServiceAgent(role=AgentRole.CUSTOMER_SERVICE)
    cs_cashier = CustomerServiceAgent(role=AgentRole.CASHIER)

    results.append(check("PII w/ consent allowed",
        cs_cs.invoke_tool("access_customer_pii", {"customer_id": "CUST-001"}), True))
    results.append(check("PII w/o consent denied",
        cs_cs.invoke_tool("access_customer_pii", {"customer_id": "CUST-002"}), False))
    results.append(check("Cashier PII denied",
        cs_cashier.invoke_tool("access_customer_pii", {"customer_id": "CUST-001"}), False))

    op_cashier = OrderProcessingAgent(role=AgentRole.CASHIER)
    results.append(check("Cashier $100 order allowed",
        op_cashier.invoke_tool("process_order", {"customer_id": "CUST-001", "amount": 100.0}), True))
    results.append(check("Cashier $600 order denied",
        op_cashier.invoke_tool("process_order", {"customer_id": "CUST-001", "amount": 600.0}), False))

    ret_mgr = ReturnsAgent(role=AgentRole.STORE_MANAGER)
    results.append(check("Late refund denied (AGT-B)",
        ret_mgr.invoke_tool("process_refund", {"order_id": "ORD-002", "amount": 89.99}), False))

    passed = sum(results)
    total = len(results)
    print(f"\n{passed}/{total} checks passed.")
    sys.exit(0 if passed == total else 1)


if __name__ == "__main__":
    main()
