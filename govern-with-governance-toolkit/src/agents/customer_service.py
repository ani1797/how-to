"""Customer Service agent — PII access, profile lookup, tier update, inquiry."""
from __future__ import annotations

from typing import Optional

from .. import mock_data
from ..models import ActionType, AgentRole, CustomerTier
from ..governance.enforcer import tool
from .base import BaseAgent


class CustomerServiceAgent(BaseAgent):
    """Customer-facing AI agent backed by governance-enforced tools."""

    AGENT_TYPE = "customer_service"
    DEFAULT_ROLE = AgentRole.CUSTOMER_SERVICE

    @tool("Return PII (email, phone) for a customer. Requires customer consent.")
    def access_customer_pii(self, customer_id: str) -> dict:
        customer = mock_data.get_customer(customer_id)
        self.enforce(
            ActionType.ACCESS_PII,
            resource={
                "type": "customer_pii",
                "customer_id": customer_id,
                "consent_given": customer.consent_given,
            },
            context={"purpose": "customer_support"},
        )
        return {
            "customer_id": customer.customer_id,
            "name": customer.name,
            "email": customer.email,
            "phone": customer.phone,
        }

    @tool("View a customer's non-sensitive profile (name + loyalty tier).")
    def view_customer_profile(self, customer_id: str) -> dict:
        customer = mock_data.get_customer(customer_id)
        self.enforce(
            ActionType.READ,
            resource={"type": "customer_profile", "customer_id": customer_id},
        )
        return {
            "customer_id": customer.customer_id,
            "name": customer.name,
            "tier": customer.tier.value,
        }

    @tool("Promote/demote a customer to a new loyalty tier. Requires a reason.")
    def update_customer_tier(self, customer_id: str, new_tier: str, reason: str) -> dict:
        new_tier_enum = CustomerTier(new_tier)
        customer = mock_data.get_customer(customer_id)
        old_tier = customer.tier

        self.enforce(
            ActionType.UPDATE,
            resource={
                "type": "customer_tier",
                "customer_id": customer_id,
                "old_tier": old_tier.value,
                "new_tier": new_tier_enum.value,
            },
            context={"reason": reason},
        )

        customer.tier = new_tier_enum
        return {
            "customer_id": customer_id,
            "old_tier": old_tier.value,
            "new_tier": new_tier_enum.value,
            "reason": reason,
        }

    @tool("Answer a generic customer inquiry (shipping, returns, hours, etc.).")
    def handle_customer_inquiry(self, customer_id: str, inquiry_type: str) -> dict:
        self.enforce(
            ActionType.QUERY,
            resource={
                "type": "customer_inquiry",
                "customer_id": customer_id,
                "inquiry_type": inquiry_type,
            },
        )
        kb = {
            "shipping": "Free shipping on orders over $50; 2-5 business days.",
            "returns": "Returns accepted within 30 days with receipt.",
            "hours": "Stores open 9am-9pm Mon-Sat, 10am-6pm Sun.",
        }
        return {
            "customer_id": customer_id,
            "inquiry_type": inquiry_type,
            "answer": kb.get(inquiry_type, "Please rephrase your question."),
        }
