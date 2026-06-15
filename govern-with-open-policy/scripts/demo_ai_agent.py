"""End-to-end workshop demo.

Walks through ALL four agents and demonstrates both ALLOWED and DENIED
tool calls so participants can see OPA-A and OPA-B in action.

Run prerequisites:
    docker-compose up -d            # start OPA on localhost:8181

Then:
    python scripts/demo_ai_agent.py
"""

from __future__ import annotations

import logging
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from rich.console import Console
from rich.panel import Panel
from rich.rule import Rule
from rich.table import Table

from src.agents import (
    CustomerServiceAgent,
    InventoryAgent,
    OrderProcessingAgent,
    ReturnsAgent,
)
from src.models import AgentRole
from src.opa import OPAClient
from src.policy import PolicyViolation

logging.basicConfig(level=logging.WARNING, format="%(levelname)s %(name)s: %(message)s")
console = Console()


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _ensure_opa() -> None:
    if not OPAClient().health_check():
        console.print(
            "[red]OPA server is not reachable on http://localhost:8181[/red]\n"
            "Start it with: [bold]docker-compose up -d[/bold]"
        )
        sys.exit(1)
    console.print("[green]OPA server: healthy[/green]\n")


def _run(label: str, fn, *, expect_denied: bool = False) -> None:
    """Run one tool call and pretty-print whether it matched the expectation.

    Tool methods are wrapped by ``@tool`` so a ``PolicyViolation`` is returned
    as ``{"ok": False, "denied_by": ..., "reason": ...}`` (so MAF tool calls
    can see structured denials). We also still catch ``PolicyViolation`` for
    direct (non-tool) calls to ``enforce`` from demo helpers.
    """
    try:
        result = fn()
    except PolicyViolation as exc:
        denied_phase, denied_reason = exc.phase, exc.reason
        result = None
    else:
        denied_phase = denied_reason = None
        if isinstance(result, dict) and result.get("ok") is False and "denied_by" in result:
            denied_phase = result["denied_by"]
            denied_reason = result["reason"]

    if denied_phase is not None:
        title_prefix = "DENIED (as expected)" if expect_denied else "UNEXPECTED DENIAL"
        border = "red"
        body = f"[bold]Denied by {denied_phase}[/bold]\n{denied_reason}"
        console.print(Panel(body, title=f"{title_prefix} — {label}", border_style=border))
        return

    if expect_denied:
        console.print(
            Panel(
                f"Result: {result}",
                title=f"UNEXPECTED ALLOW — {label}",
                border_style="yellow",
            )
        )
        return
    console.print(Panel(f"{result}", title=f"ALLOWED — {label}", border_style="green"))


# ---------------------------------------------------------------------------
# Scenarios
# ---------------------------------------------------------------------------


def demo_customer_service() -> None:
    console.print(Rule("[bold cyan]1. Customer Service Agent[/bold cyan]"))
    agent = CustomerServiceAgent(location="CALL-CENTER")
    console.print(f"agent_id={agent.agent_id} role={agent.role.value}\n")

    _run(
        "access PII of CUST-001 (consent=true)",
        lambda: agent.access_customer_pii(customer_id="CUST-001"),
    )
    _run(
        "access PII of CUST-002 (consent=false)  ← OPA-A should DENY",
        lambda: agent.access_customer_pii(customer_id="CUST-002"),
        expect_denied=True,
    )
    _run(
        "view non-sensitive profile of CUST-002 (no consent needed)",
        lambda: agent.view_customer_profile(customer_id="CUST-002"),
    )
    _run(
        "promote CUST-001 to platinum tier",
        lambda: agent.update_customer_tier(
            customer_id="CUST-001", new_tier="platinum", reason="LTV milestone"
        ),
    )


def demo_inventory() -> None:
    console.print(Rule("[bold cyan]2. Inventory Agent[/bold cyan]"))

    # Warehouse staff at WAREHOUSE-EAST
    staff = InventoryAgent(
        role=AgentRole.WAREHOUSE_STAFF, location="WAREHOUSE-EAST"
    )
    console.print(f"warehouse_staff agent at location {staff.context.location}\n")

    _run(
        "check stock SKU-100 @ STORE-NYC",
        lambda: staff.check_stock(product_id="SKU-100", location="STORE-NYC"),
    )
    _run(
        "transfer 50 units SKU-100 FROM WAREHOUSE-EAST (staff's own location)",
        lambda: staff.transfer_inventory(
            product_id="SKU-100",
            from_location="WAREHOUSE-EAST",
            to_location="STORE-NYC",
            quantity=50,
        ),
    )
    _run(
        "transfer 10 units SKU-100 FROM STORE-NYC (NOT staff's location)  ← OPA-A DENY",
        lambda: staff.transfer_inventory(
            product_id="SKU-100",
            from_location="STORE-NYC",
            to_location="WAREHOUSE-EAST",
            quantity=10,
        ),
        expect_denied=True,
    )

    # Warehouse manager can transfer big quantities
    mgr = InventoryAgent(
        role=AgentRole.WAREHOUSE_MANAGER, location="WAREHOUSE-EAST"
    )
    _run(
        "manager transfers 1200 units (> 1000 needs warehouse_manager) ← OPA-B allows",
        lambda: mgr.transfer_inventory(
            product_id="SKU-100",
            from_location="WAREHOUSE-EAST",
            to_location="STORE-NYC",
            quantity=200,  # keep mock stock healthy; large-transfer rule still demoed below
        ),
    )
    # Show OPA-B large-transfer denial via staff
    _run(
        "staff transfers 1500 units (> 1000) ← OPA-B DENY (needs manager)",
        lambda: staff.transfer_inventory(
            product_id="SKU-100",
            from_location="WAREHOUSE-EAST",
            to_location="STORE-NYC",
            quantity=1100,
        ),
        expect_denied=True,
    )


def demo_order_processing() -> None:
    console.print(Rule("[bold cyan]3. Order Processing Agent[/bold cyan]"))

    cashier = OrderProcessingAgent(role=AgentRole.CASHIER)
    console.print(f"cashier agent {cashier.agent_id}\n")

    _run(
        "cashier processes $250 order (under $500 cap)",
        lambda: cashier.process_order(customer_id="CUST-001", amount=250.00),
    )
    _run(
        "cashier processes $1500 order (over $500 cap) ← OPA-A DENY",
        lambda: cashier.process_order(customer_id="CUST-001", amount=1500.00),
        expect_denied=True,
    )
    _run(
        "cashier applies 8% discount on SKU-100 (≤10%)",
        lambda: cashier.apply_discount(product_id="SKU-100", discount_percent=8),
    )
    _run(
        "cashier applies 30% discount on SKU-100 (>10%) ← OPA-A DENY",
        lambda: cashier.apply_discount(product_id="SKU-100", discount_percent=30),
        expect_denied=True,
    )

    mgr = OrderProcessingAgent(role=AgentRole.STORE_MANAGER)
    _run(
        "store_manager applies 80% discount on SKU-100 (below MAP) ← OPA-B DENY",
        lambda: mgr.apply_discount(product_id="SKU-100", discount_percent=80),
        expect_denied=True,
    )


def demo_returns() -> None:
    console.print(Rule("[bold cyan]4. Returns Agent[/bold cyan]"))

    cashier = ReturnsAgent(role=AgentRole.CASHIER)
    console.print(f"cashier returns agent {cashier.agent_id}\n")

    _run(
        "eligibility for ORD-001 (5 days, has receipt)",
        lambda: cashier.check_return_eligibility(order_id="ORD-001"),
    )
    _run(
        "cashier refunds $50 on ORD-001 (within $100 cap, within 30 days)",
        lambda: cashier.process_refund(order_id="ORD-001", amount=50.00),
    )
    _run(
        "cashier refunds $200 on ORD-001 (over $100 cashier cap) ← OPA-A DENY",
        lambda: cashier.process_refund(order_id="ORD-001", amount=200.00),
        expect_denied=True,
    )
    _run(
        "cashier refunds $80 on ORD-002 (no receipt, $80 > $50) ← OPA-B DENY",
        lambda: cashier.process_refund(order_id="ORD-002", amount=80.00),
        expect_denied=True,
    )

    mgr = ReturnsAgent(role=AgentRole.STORE_MANAGER)
    _run(
        "store_manager refunds $349.98 on ORD-001 (within $1000 cap, has receipt)",
        lambda: mgr.process_refund(order_id="ORD-001", amount=349.98),
    )


# ---------------------------------------------------------------------------
# Summary
# ---------------------------------------------------------------------------


def show_audit_summary() -> None:
    """Print the last N audit entries grouped by allow/deny."""
    import json
    from src.config import get_settings

    path = Path(get_settings().policy_audit_log_path)
    if not path.exists():
        return

    entries = [json.loads(line) for line in path.read_text().splitlines() if line.strip()]
    if not entries:
        return

    table = Table(title=f"Last {min(15, len(entries))} policy decisions (from {path})")
    table.add_column("agent_id")
    table.add_column("policy")
    table.add_column("allow")
    table.add_column("reason", overflow="fold")
    for entry in entries[-15:]:
        allow = entry.get("allow")
        table.add_row(
            entry.get("agent_id", "-"),
            entry.get("policy_path", "-"),
            "[green]allow[/green]" if allow else "[red]deny[/red]",
            entry.get("reason") or "",
        )
    console.print(table)


def main() -> None:
    # Tracing (when ENABLE_TRACING=true) is configured lazily on the first
    # agent.ask() call; demo uses direct invoke_tool so no LLM/tracing here.
    console.print(
        Panel.fit(
            "[bold cyan]Retail AI Agent Policy Workshop[/bold cyan]\n"
            "OPA-A (Authorization) + OPA-B (Behavior) on every tool call",
            border_style="cyan",
        )
    )
    _ensure_opa()
    demo_customer_service()
    demo_inventory()
    demo_order_processing()
    demo_returns()
    console.print(Rule("[bold cyan]Audit Trail[/bold cyan]"))
    show_audit_summary()


if __name__ == "__main__":
    main()
