"""AGT-based governance enforcement (replaces opa.py + policy.py).

Workshop pattern
----------------
Every tool method follows the same three steps::

    @tool("Get customer PII. Requires consent.")
    def access_customer_pii(self, customer_id: str) -> dict:
        customer = mock_data.get_customer(customer_id)          # 1. resolve
        self.enforce(                                            # 2. AGT-A + AGT-B
            ActionType.ACCESS_PII,
            resource={"type": "customer_pii",
                      "customer_id": customer_id,
                      "consent_given": customer.consent_given},
        )
        return {"email": customer.email, "phone": customer.phone}  # 3. business logic

No external server needed — AGT evaluates YAML policies in-process.
"""
from __future__ import annotations

import ast
import functools
import json
import logging
import operator
import time
from datetime import datetime
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional

import yaml

from ..config import get_settings
from ..models import ActionType, AgentContext, PolicyAuditLog, RetailAction

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Exception
# ---------------------------------------------------------------------------


class GovernanceDeniedException(Exception):
    """Raised when AGT denies an action (replaces PolicyViolation)."""

    def __init__(self, phase: str, reason: str) -> None:
        super().__init__(f"{phase}: {reason}")
        self.phase = phase   # "AGT-A" or "AGT-B"
        self.reason = reason


# ---------------------------------------------------------------------------
# Simple safe expression evaluator for YAML policy conditions
# ---------------------------------------------------------------------------

_SAFE_OPS = {
    ast.Eq: operator.eq,
    ast.NotEq: operator.ne,
    ast.Lt: operator.lt,
    ast.LtE: operator.le,
    ast.Gt: operator.gt,
    ast.GtE: operator.ge,
    ast.And: lambda a, b: a and b,
    ast.Or: lambda a, b: a or b,
    ast.Not: operator.not_,
    ast.In: lambda a, b: a in b,
    ast.NotIn: lambda a, b: a not in b,
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
}


def _safe_eval(expr: str, ctx: Dict[str, Any]) -> bool:
    """Evaluate a simple boolean expression against a flat context dict.

    Supports: comparisons, ``and``/``or``/``not``, ``in``/``not in``,
    attribute access (``agent.role``), ``len()``, ``null`` literals, and
    list literals.  Does NOT call arbitrary Python — uses ``ast`` to
    walk the tree safely.
    """
    # Treat YAML null keyword as Python None
    expr = expr.replace(" null", " None").replace("(null", "(None")

    def _eval(node: ast.AST) -> Any:
        if isinstance(node, ast.Expression):
            return _eval(node.body)
        if isinstance(node, ast.Constant):
            return node.value
        if isinstance(node, ast.List):
            return [_eval(e) for e in node.elts]
        if isinstance(node, ast.Name):
            name = node.id
            if name == "None":
                return None
            if name == "True":
                return True
            if name == "False":
                return False
            return ctx.get(name)
        if isinstance(node, ast.Attribute):
            obj = _eval(node.value)
            if isinstance(obj, dict):
                return obj.get(node.attr)
            return getattr(obj, node.attr, None)
        if isinstance(node, ast.BoolOp):
            op = _SAFE_OPS[type(node.op)]
            result = _eval(node.values[0])
            for v in node.values[1:]:
                result = op(result, _eval(v))
            return result
        if isinstance(node, ast.UnaryOp) and isinstance(node.op, ast.Not):
            return not _eval(node.operand)
        if isinstance(node, ast.Compare):
            left = _eval(node.left)
            for op_node, comparator in zip(node.ops, node.comparators):
                right = _eval(comparator)
                op_fn = _SAFE_OPS.get(type(op_node))
                if op_fn is None:
                    raise ValueError(f"Unsupported operator: {type(op_node)}")
                if not op_fn(left, right):
                    return False
                left = right
            return True
        if isinstance(node, ast.Call):
            if isinstance(node.func, ast.Name) and node.func.id == "len":
                return len(_eval(node.args[0]))
        raise ValueError(f"Unsupported AST node: {type(node)}")

    try:
        tree = ast.parse(expr, mode="eval")
        result = _eval(tree)
        return bool(result)
    except Exception as exc:
        logger.debug("Expression eval error (%r): %s", expr, exc)
        return False


# ---------------------------------------------------------------------------
# In-process policy engine
# ---------------------------------------------------------------------------


class _Rule:
    def __init__(self, name: str, condition: str, deny: bool, description: str = "") -> None:
        self.name = name
        self.condition = condition
        self.deny = deny  # True -> deny when matched; False -> allow when matched
        self.description = description

    def matches(self, ctx: Dict[str, Any]) -> bool:
        return _safe_eval(self.condition, ctx)


class _PolicyEngine:
    """Load a YAML policy file and evaluate it against a flat context dict."""

    def __init__(self, yaml_path: Path) -> None:
        with yaml_path.open() as f:
            doc = yaml.safe_load(f)
        self.name: str = doc.get("name", yaml_path.stem)
        default_str: str = doc.get("default_action", "allow").lower()
        self.default_allow: bool = default_str == "allow"
        self._rules: List[_Rule] = []
        for r in doc.get("rules", []):
            action_str = r.get("action", "deny").lower()
            self._rules.append(
                _Rule(
                    name=r.get("name", "unnamed"),
                    condition=r.get("condition", "false"),
                    deny=(action_str == "deny"),
                    description=r.get("description", ""),
                )
            )

    def evaluate(self, ctx: Dict[str, Any]) -> tuple[bool, Optional[str]]:
        """Return (allowed, reason).  First matching rule wins."""
        for rule in self._rules:
            if rule.matches(ctx):
                if rule.deny:
                    return False, rule.description or rule.name
                else:
                    return True, None
        return self.default_allow, None


# ---------------------------------------------------------------------------
# GovernanceEnforcer
# ---------------------------------------------------------------------------


class GovernanceEnforcer:
    """Runs AGT-A (authorization) then AGT-B (behavior) for every tool call.

    Tries to import ``agent-governance-toolkit`` for future compatibility;
    falls back to the built-in ``_PolicyEngine`` if the package is not yet
    available (preview / not installed).
    """

    def __init__(
        self,
        policy_dir: Optional[Path] = None,
        enable_audit: bool = True,
        audit_log_path: Optional[str] = None,
    ) -> None:
        settings = get_settings()
        base = policy_dir or Path(settings.governance_policy_dir)
        self.auth_engine = _PolicyEngine(base / "authorization.yaml")
        self.behavior_engine = _PolicyEngine(base / "behavior.yaml")
        self.enable_audit = enable_audit
        self.audit_log_path = Path(audit_log_path or settings.governance_audit_log_path)
        if self.enable_audit:
            self.audit_log_path.parent.mkdir(parents=True, exist_ok=True)

    # ------------------------------------------------------------------

    def enforce(
        self,
        agent: AgentContext,
        action: RetailAction,
        recent_actions: List[Dict[str, Any]],
    ) -> None:
        """Run AGT-A then AGT-B; raise GovernanceDeniedException on deny."""

        # ---- AGT-A: Authorization --------------------------------
        auth_ctx = {
            "agent": agent.model_dump(mode="json"),
            "action": action.action_type.value,
            "resource": action.resource,
            "context": action.context,
            # Flatten commonly-tested fields for simpler YAML conditions
            "role": agent.role.value,
            **action.resource,
        }
        auth_allowed, auth_reason = self._evaluate(
            self.auth_engine, auth_ctx, agent.agent_id, "AGT-A"
        )
        if not auth_allowed:
            raise GovernanceDeniedException("AGT-A", auth_reason or "authorization denied")

        # ---- AGT-B: Behavior -------------------------------------
        behavior_ctx = {
            "agent": agent.model_dump(mode="json"),
            "action": {
                "type": action.action_type.value,
                "resource": action.resource,
                "context": action.context,
            },
            "recent_actions": recent_actions,
            "timestamp": datetime.utcnow().isoformat(),
            # Flatten for simpler YAML conditions
            "role": agent.role.value,
            "resource": action.resource,
            "context": action.context,
            **action.resource,
        }
        beh_allowed, beh_reason = self._evaluate(
            self.behavior_engine, behavior_ctx, agent.agent_id, "AGT-B"
        )
        if not beh_allowed:
            raise GovernanceDeniedException("AGT-B", beh_reason or "behavior constraint violated")

    # ------------------------------------------------------------------

    def _evaluate(
        self, engine: _PolicyEngine, ctx: Dict[str, Any], agent_id: str, phase: str
    ) -> tuple[bool, Optional[str]]:
        start = time.time()
        allowed, reason = engine.evaluate(ctx)
        duration_ms = (time.time() - start) * 1000.0

        if self.enable_audit:
            self._write_audit(
                PolicyAuditLog(
                    agent_id=agent_id,
                    policy_path=f"{phase}:{engine.name}",
                    allow=allowed,
                    reason=reason,
                    input_data={k: v for k, v in ctx.items() if not isinstance(v, list)
                                or len(v) < 20},
                    duration_ms=duration_ms,
                )
            )
        return allowed, reason

    def _write_audit(self, entry: PolicyAuditLog) -> None:
        try:
            with self.audit_log_path.open("a") as fp:
                fp.write(entry.model_dump_json() + "\n")
        except OSError as exc:
            logger.warning("Failed to write audit log: %s", exc)


# ---------------------------------------------------------------------------
# @tool decorator (same concept as OPA workshop's policy.tool)
# ---------------------------------------------------------------------------

_TOOL_ATTR = "__workshop_tool__"


def tool(description: str) -> Callable:
    """Mark an agent method as an LLM-callable, governance-enforced tool.

    ``GovernanceDeniedException`` raised inside the tool body is caught here
    and converted to a structured result the LLM can reason about.
    """

    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            try:
                return func(*args, **kwargs)
            except GovernanceDeniedException as exc:
                logger.info("Governance denied %s: %s", func.__name__, exc)
                return {
                    "ok": False,
                    "denied_by": exc.phase,
                    "reason": exc.reason,
                }

        wrapper.__doc__ = description
        setattr(wrapper, _TOOL_ATTR, {"description": description, "name": func.__name__})
        return wrapper

    return decorator


def collect_tools(instance: Any) -> Dict[str, Callable]:
    """Return ``{tool_name: bound_method}`` for every ``@tool`` method."""
    tools: Dict[str, Callable] = {}
    for name in dir(instance):
        if name.startswith("_"):
            continue
        attr = getattr(instance, name)
        if callable(attr) and hasattr(attr, _TOOL_ATTR):
            tools[name] = attr
    return tools


__all__ = [
    "GovernanceEnforcer",
    "GovernanceDeniedException",
    "tool",
    "collect_tools",
]
