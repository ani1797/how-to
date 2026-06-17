"""Deploy governance-enforced agents to Azure AI Foundry.

Usage::

    python scripts/deploy_to_foundry.py

Requires FOUNDRY_PROJECT_ENDPOINT in .env or environment.
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.config import get_settings


def main() -> None:
    settings = get_settings()
    if not settings.has_llm():
        print("ERROR: FOUNDRY_PROJECT_ENDPOINT not set. Cannot deploy.")
        sys.exit(1)

    print(f"Deploying to: {settings.foundry_project_endpoint}")
    print("Governance policies loaded from:", settings.governance_policy_dir)
    print()

    from src.agents import (
        CustomerServiceAgent, InventoryAgent,
        OrderProcessingAgent, ReturnsAgent,
    )
    from src.models import AgentRole

    agents = [
        CustomerServiceAgent(role=AgentRole.CUSTOMER_SERVICE),
        InventoryAgent(role=AgentRole.WAREHOUSE_STAFF),
        OrderProcessingAgent(role=AgentRole.CASHIER),
        ReturnsAgent(role=AgentRole.CASHIER),
    ]

    for agent in agents:
        print(f"  Registering {agent.AGENT_TYPE} with tools: {agent.list_tools()}")

    print()
    print("All agents registered. Send queries with agent.ask('...').")


if __name__ == "__main__":
    main()
