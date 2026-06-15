"""Policy enforcement: ties agent tool calls to OPA-A and OPA-B.

Workshop pattern
----------------
Every tool method follows three steps that are easy to point at in a demo::

    @tool("Get customer PII. Requires consent.")
    def access_customer_pii(self, customer_id: str) -> dict:
        customer = mock_data.get_customer(customer_id)              # 1. resolve
        self.enforce(                                                # 2. OPA-A + OPA-B
            ActionType.ACCESS_PII,
            resource={"type": "customer_pii",
                      "customer_id": customer_id,
                      "consent_given": customer.consent_given},
        )
        return {"email": customer.email, "phone": customer.phone}    # 3. business logic
"""

from __future__ import annotations

import functools
import json
import logging
import time
from datetime import datetime
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional

from .config import get_settings
from .models import ActionType, AgentContext, PolicyAuditLog, RetailAction
from .opa import OPAClient, OPAError, PolicyDecision

logger = logging.getLogger(__name__)


class PolicyViolation(Exception):
    """Raised when OPA denies an action."""

    def __init__(self, phase: str, reason: str) -> None:
        super().__init__(f"{phase}: {reason}")
        self.phase = phase  # "OPA-A" or "OPA-B"
        self.reason = reason


# ---------------------------------------------------------------------------
# PolicyEnforcer
# ---------------------------------------------------------------------------


class PolicyEnforcer:
    """Runs OPA-A and OPA-B against a `RetailAction` and writes an audit log."""

    AUTHORIZATION_POLICY = "retail/authorization"
    BEHAVIOR_POLICY = "retail/behavior"

    def __init__(
        self,
        opa_client: Optional[OPAClient] = None,
        enable_audit: bool = True,
        audit_log_path: Optional[str] = None,
    ) -> None:
        settings = get_settings()
        self.opa = opa_client or OPAClient(base_url=settings.opa_url)
        self.enable_audit = enable_audit
        self.audit_log_path = Path(audit_log_path or settings.policy_audit_log_path)
        if self.enable_audit:
            self.audit_log_path.parent.mkdir(parents=True, exist_ok=True)

    # ------------------------------------------------------------------
    def enforce(
        self,
        agent: AgentContext,
        action: RetailAction,
        recent_actions: List[Dict[str, Any]],
    ) -> Dict[str, PolicyDecision]:
        """Run OPA-A (authorization) then OPA-B (behavior). Raise on deny."""

        # ---- OPA-A: Authorization ---------------------------------
        auth_input = {
            "agent": agent.model_dump(mode="json"),
            "action": action.action_type.value,
            "resource": action.resource,
            "context": action.context,
        }
        auth = self._evaluate(self.AUTHORIZATION_POLICY, auth_input, agent.agent_id)
        if not auth.allow:
            raise PolicyViolation("OPA-A", auth.reason or "authorization denied")

        # ---- OPA-B: Behavior --------------------------------------
        behavior_input = {
            "agent": agent.model_dump(mode="json"),
            "action": {
                "type": action.action_type.value,
                "resource": action.resource,
                "context": action.context,
            },
            "recent_actions": recent_actions,
            "timestamp": datetime.utcnow().isoformat(),
        }
        behavior = self._evaluate(self.BEHAVIOR_POLICY, behavior_input, agent.agent_id)
        if not behavior.allow:
            raise PolicyViolation("OPA-B", behavior.reason or "behavior constraint violated")

        return {"authorization": auth, "behavior": behavior}

    # ------------------------------------------------------------------
    def _evaluate(
        self, policy_path: str, input_data: Dict[str, Any], agent_id: str
    ) -> PolicyDecision:
        start = time.time()
        try:
            decision = self.opa.evaluate(policy_path, input_data)
        except OPAError as exc:
            # Fail closed but log
            decision = PolicyDecision(allow=False, reason=str(exc))
        duration_ms = (time.time() - start) * 1000.0

        if self.enable_audit:
            self._write_audit(
                PolicyAuditLog(
                    agent_id=agent_id,
                    policy_path=policy_path,
                    allow=decision.allow,
                    reason=decision.reason,
                    input_data=input_data,
                    duration_ms=duration_ms,
                )
            )
        return decision

    def _write_audit(self, entry: PolicyAuditLog) -> None:
        try:
            with self.audit_log_path.open("a") as fp:
                fp.write(entry.model_dump_json() + "\n")
        except OSError as exc:  # pragma: no cover
            logger.warning("Failed to write audit log: %s", exc)


# ---------------------------------------------------------------------------
# @tool decorator
#
# Microsoft Agent Framework auto-infers tool schemas from type hints + the
# function docstring. We use a tiny wrapper here so that:
#   1. The description shows up as the docstring (and thus as the tool's
#      description in the LLM tool spec).
#   2. ``PolicyViolation`` raised inside the tool body is converted to a
#      structured result the model can reason about (instead of crashing
#      the agent loop).
# ---------------------------------------------------------------------------

_TOOL_ATTR = "__workshop_tool__"


def tool(description: str) -> Callable:
    """Mark an agent method as an LLM-callable, policy-enforced tool.

    The decorated method body is responsible for calling ``self.enforce(...)``
    so workshop participants can see exactly where policy enforcement happens.
    """

    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            try:
                return func(*args, **kwargs)
            except PolicyViolation as exc:
                # Convert to structured output so the LLM sees the denial
                # and can explain it to the user, rather than blowing up
                # the tool-call loop.
                logger.info("Policy denied %s: %s", func.__name__, exc)
                return {
                    "ok": False,
                    "denied_by": exc.phase,
                    "reason": exc.reason,
                }

        # Ensure the description ends up as the docstring so MAF picks it up.
        wrapper.__doc__ = description
        setattr(wrapper, _TOOL_ATTR, {"description": description, "name": func.__name__})
        return wrapper

    return decorator


def collect_tools(instance: Any) -> Dict[str, Callable]:
    """Return ``{tool_name: bound_method}`` for every `@tool` method on ``instance``."""
    tools: Dict[str, Callable] = {}
    for name in dir(instance):
        if name.startswith("_"):
            continue
        attr = getattr(instance, name)
        if callable(attr) and hasattr(attr, _TOOL_ATTR):
            tools[name] = attr
    return tools


__all__ = [
    "PolicyEnforcer",
    "PolicyViolation",
    "tool",
    "collect_tools",
]
