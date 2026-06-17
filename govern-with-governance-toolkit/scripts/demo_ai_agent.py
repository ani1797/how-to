"""Demo: run all 4 agents through allowed and denied scenarios.

Run from repo root::

    python scripts/demo_ai_agent.py

No Azure credentials needed — the demo uses tool calls directly via
``invoke_tool`` (no LLM required).
"""
from __future__ import annotations

import sys
from pathlib import Path

# Allow running from repo root without installing the package
sys.path.insert(0, str(Path(__file__).parent.parent))

try:
    from rich.console import Console
    from rich.table import Table
    from rich import box
    RICH = True
except ImportError:
    RICH = False

from src.agents.customer_service import CustomerServiceAgent
from src.agents.inventory import InventoryAgent
from src.agents.order_processing import OrderProcessingAgent
from src.agents.returns import ReturnsAgent
from src.models import AgentRole

console = Console() if RICH else None


def header(text: str) -> None:
    if console:
        console.rule(f"[bold cyan]{text}[/]")
    else:
        print(f"\n{'='*60}\n{text}\n{'='*60}")


def show(label: str, result: dict) -> None:
    ok = result.get("ok", True)
    status = "[green]ALLOWED[/]" if ok is not False else "[red]DENIED[/]"
    if console:
        console.print(f"  {status}  {label}")
        if ok is False:
            console.print(f"         denied_by={result.get('denied_by')}  reason={result.get('reason')}")
    else:
        tag = "ALLOWED" if ok is not False else "DENIED"
        print(f"  [{tag}]  {label}")
        if ok is False:
            print(f"         denied_by={result.get('denied_by')}  reason={result.get('reason')}")


def main() -> None:
    header("Retail AI Agent Governance Demo — Agent Governance Toolkit (AGT)")

    # -- CustomerService --------------------------------------------------
    header("CustomerService Agent")
    cs_cs = CustomerServiceAgent(role=AgentRole.CUSTOMER_SERVICE)
    cs_cashier = CustomerServiceAgent(role=AgentRole.CASHIER)

    show("CS agent: PII for CUST-001 (consent=True)",
         cs_cs.invoke_tool("access_customer_pii", {"customer_id": "CUST-001"}))
    show("CS agent: PII for CUST-002 (consent=False)",
         cs_cs.invoke_tool("access_customer_pii", {"customer_id": "CUST-002"}))
    show("Cashier: PII for CUST-001 [blocked by AGT-A]",
         cs_cashier.invoke_tool("access_customer_pii", {"customer_id": "CUST-001"}))
    show("CS agent: view profile CUST-003",
         cs_cs.invoke_tool("view_customer_profile", {"customer_id": "CUST-003"}))
    show("CS agent: update tier CUST-001 -> platinum",
         cs_cs.invoke_tool("update_customer_tier",
                           {"customer_id": "CUST-001", "new_tier": "platinum",
                            "reason": "loyalty reward"}))
    show("Cashier: update tier [blocked by AGT-A]",
         cs_cashier.invoke_tool("update_customer_tier",
                                {"customer_id": "CUST-001", "new_tier": "silver",
                                 "reason": "test"}))
    show("CS agent: inquiry (shipping)",
         cs_cs.invoke_tool("handle_customer_inquiry",
                           {"customer_id": "CUST-001", "inquiry_type": "shipping"}))

    # -- Inventory --------------------------------------------------------
    header("Inventory Agent")
    inv_staff = InventoryAgent(role=AgentRole.WAREHOUSE_STAFF)
    inv_mgr = InventoryAgent(role=AgentRole.WAREHOUSE_MANAGER)

    show("Staff: check stock SKU-100 NYC",
         inv_staff.invoke_tool("check_stock",
                               {"product_id": "SKU-100", "location": "STORE-NYC"}))
    show("Staff: transfer 50 units [allowed by AGT-A]",
         inv_staff.invoke_tool("transfer_inventory",
                               {"product_id": "SKU-100", "from_location": "WAREHOUSE-EAST",
                                "to_location": "STORE-NYC", "quantity": 50}))
    show("Staff: transfer 101 units [blocked by AGT-A]",
         inv_staff.invoke_tool("transfer_inventory",
                               {"product_id": "SKU-100", "from_location": "WAREHOUSE-EAST",
                                "to_location": "STORE-NYC", "quantity": 101}))
    show("Manager: transfer 600 units [AGT-A ok; AGT-B ok for manager]",
         inv_mgr.invoke_tool("transfer_inventory",
                             {"product_id": "SKU-100", "from_location": "WAREHOUSE-EAST",
                              "to_location": "STORE-NYC", "quantity": 600}))
    show("Staff: adjust -5 units",
         inv_staff.invoke_tool("adjust_inventory",
                               {"product_id": "SKU-100", "location": "STORE-NYC",
                                "delta": -5, "reason": "shrinkage"}))

    # -- OrderProcessing --------------------------------------------------
    header("Order Processing Agent")
    op_cashier = OrderProcessingAgent(role=AgentRole.CASHIER)
    op_mgr = OrderProcessingAgent(role=AgentRole.STORE_MANAGER)

    show("Cashier: process $100 order [allowed]",
         op_cashier.invoke_tool("process_order",
                                {"customer_id": "CUST-001", "amount": 100.0}))
    show("Cashier: process $600 order [blocked by AGT-A]",
         op_cashier.invoke_tool("process_order",
                                {"customer_id": "CUST-001", "amount": 600.0}))
    show("Cashier: 5% discount SKU-300 [allowed]",
         op_cashier.invoke_tool("apply_discount",
                                {"product_id": "SKU-300", "discount_percent": 5.0}))
    show("Cashier: 15% discount SKU-100 [blocked by AGT-A]",
         op_cashier.invoke_tool("apply_discount",
                                {"product_id": "SKU-100", "discount_percent": 15.0}))
    show("Manager: 30% discount SKU-100 [blocked by AGT-B — below MAP]",
         op_mgr.invoke_tool("apply_discount",
                            {"product_id": "SKU-100", "discount_percent": 30.0}))
    show("Cashier: lookup ORD-001",
         op_cashier.invoke_tool("lookup_order", {"order_id": "ORD-001"}))

    # -- Returns ----------------------------------------------------------
    header("Returns Agent")
    ret_cashier = ReturnsAgent(role=AgentRole.CASHIER)
    ret_mgr = ReturnsAgent(role=AgentRole.STORE_MANAGER)

    show("Check eligibility ORD-001 (5 days, receipt)",
         ret_cashier.invoke_tool("check_return_eligibility", {"order_id": "ORD-001"}))
    show("Check eligibility ORD-002 (45 days, no receipt)",
         ret_cashier.invoke_tool("check_return_eligibility", {"order_id": "ORD-002"}))
    show("Cashier: refund $50 ORD-001 [allowed]",
         ret_cashier.invoke_tool("process_refund",
                                 {"order_id": "ORD-001", "amount": 50.0}))
    show("Cashier: refund $150 ORD-001 [blocked by AGT-A — over $100]",
         ret_cashier.invoke_tool("process_refund",
                                 {"order_id": "ORD-001", "amount": 150.0}))
    show("Manager: refund ORD-002 (45 days) [blocked by AGT-B — over 30 days]",
         ret_mgr.invoke_tool("process_refund",
                             {"order_id": "ORD-002", "amount": 89.99}))

    header("Demo complete — check logs/governance-audit.jsonl for the full audit trail")


if __name__ == "__main__":
    main()
