"""BaseAgent: Microsoft Agent Framework agent with OPA-enforced tool calls.

Workshop participants only need to read three things:

1. ``BaseAgent.enforce(...)`` — single call that runs OPA-A then OPA-B.
2. ``BaseAgent.invoke_tool(...)`` — direct tool dispatch (used by tests/demos).
3. ``BaseAgent.ask(...)`` — Microsoft Agent Framework ``Agent.run()`` loop
   that the LLM uses to call the same policy-enforced tool methods.

The agent is built once per instance: tools are plain Python methods marked
with the workshop ``@tool`` decorator. MAF auto-derives the LLM tool schema
from each method's type hints and docstring, so we don't hand-roll any JSON.
"""

from __future__ import annotations

import asyncio
import logging
from datetime import datetime
from typing import Any, Dict, List, Optional

from ..config import get_settings
from ..models import ActionType, AgentContext, AgentRole, RetailAction
from ..opa import OPAClient
from ..policy import PolicyEnforcer, PolicyViolation, collect_tools

logger = logging.getLogger(__name__)


class BaseAgent:
    """Base class for all workshop agents (built on Microsoft Agent Framework)."""

    #: Agents override these two class attributes.
    AGENT_TYPE: str = "base"
    DEFAULT_ROLE: AgentRole = AgentRole.ADMIN

    #: Class-level counter so each instance gets a stable, predictable id
    #: (e.g. ``customer_service-001``). Tests/notebooks that need a fixed id
    #: can still set ``agent.context.agent_id`` after construction.
    _instance_counter: int = 0

    @classmethod
    def _make_agent_id(cls) -> str:
        cls._instance_counter += 1
        return f"{cls.AGENT_TYPE}-{cls._instance_counter:03d}"

    # ------------------------------------------------------------------
    def __init__(
        self,
        role: Optional[AgentRole] = None,
        location: Optional[str] = None,
        trust_level: int = 3,
        enforcer: Optional[PolicyEnforcer] = None,
    ) -> None:
        self.settings = get_settings()
        self.context = AgentContext(
            agent_id=self._make_agent_id(),
            agent_type=self.AGENT_TYPE,
            role=role or self.DEFAULT_ROLE,
            location=location,
            trust_level=trust_level,
        )
        self.enforcer = enforcer or PolicyEnforcer(
            opa_client=OPAClient(base_url=self.settings.opa_url),
            enable_audit=self.settings.enable_policy_audit,
            audit_log_path=self.settings.policy_audit_log_path,
        )
        self._recent_actions: List[Dict[str, Any]] = []
        self._max_recent = 100
        self._tools = collect_tools(self)
        self._maf_agent = None  # lazily built when ask() is called

    # ------------------------------------------------------------------
    @property
    def agent_id(self) -> str:
        return self.context.agent_id

    @property
    def role(self) -> AgentRole:
        return self.context.role

    # ------------------------------------------------------------------
    # Policy enforcement (called from each @tool method body)
    # ------------------------------------------------------------------
    def enforce(
        self,
        action_type: ActionType,
        resource: Optional[Dict[str, Any]] = None,
        context: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Run OPA-A then OPA-B for an action; raise PolicyViolation on deny."""
        action = RetailAction(
            action_type=action_type,
            resource=resource or {},
            context=context or {},
        )
        self.enforcer.enforce(self.context, action, self._recent_actions)

        # Track for OPA-B rate-limit checks
        self._recent_actions.append(
            {
                "timestamp_ns": int(datetime.utcnow().timestamp() * 1e9),
                "action": action_type.value,
                "resource": action.resource,
            }
        )
        if len(self._recent_actions) > self._max_recent:
            self._recent_actions = self._recent_actions[-self._max_recent :]

    # ------------------------------------------------------------------
    # Direct tool invocation (used by demos + tests)
    # ------------------------------------------------------------------
    def list_tools(self) -> List[str]:
        return sorted(self._tools.keys())

    def invoke_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Run a tool directly, normalising the result into ``{"ok": ...}`` form.

        The ``@tool`` decorator already converts ``PolicyViolation`` into a
        denial dict, so this method only has to wrap successful results.
        """
        if tool_name not in self._tools:
            raise ValueError(f"Unknown tool: {tool_name}")
        try:
            result = self._tools[tool_name](**arguments)
        except LookupError as exc:
            return {"ok": False, "error": str(exc)}

        if isinstance(result, dict) and result.get("ok") is False:
            return result
        return {"ok": True, "result": result}

    # ------------------------------------------------------------------
    # Microsoft Agent Framework loop
    # ------------------------------------------------------------------
    def ask(self, user_query: str) -> Dict[str, Any]:
        """Process a natural-language query via MAF ``Agent.run()``.

        Falls back to a "tool-less" string response if no LLM is configured,
        so the workshop stays runnable without Azure credentials.
        """
        if not self.settings.has_llm():
            return self._fallback_ask(user_query)

        # Tracing + MAF agent build + agent.run must all share one asyncio
        # context, otherwise MAF's observability ContextVar token can't be
        # reset cleanly (ValueError: token was created in a different Context).
        async def _run() -> str:
            from ..observability import configure_tracing

            configure_tracing()
            agent = self._build_maf_agent()
            return str(await agent.run(user_query))

        # If we're already inside a running event loop (e.g. Jupyter), spawn
        # a dedicated thread with its own loop so asyncio.run() + the underlying
        # HTTP client (anyio/httpx) see a clean async context.
        try:
            asyncio.get_running_loop()
            in_loop = True
        except RuntimeError:
            in_loop = False

        if in_loop:
            import concurrent.futures

            with concurrent.futures.ThreadPoolExecutor(max_workers=1) as pool:
                response = pool.submit(lambda: asyncio.run(_run())).result()
        else:
            response = asyncio.run(_run())

        return {
            "response": response,
            "agent_id": self.agent_id,
        }

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------
    def _system_prompt(self) -> str:
        return (
            f"You are the {self.AGENT_TYPE} agent for a retail company.\n"
            f"Your role: {self.role.value}. Agent id: {self.agent_id}.\n"
            "All tools are policy-enforced (OPA-A authorization + OPA-B behavior).\n"
            "When a tool returns ok=false, briefly explain to the user what the "
            "policy denied and why."
        )

    def _fallback_ask(self, user_query: str) -> Dict[str, Any]:
        """No-LLM mode: just list available tools so demos still produce output."""
        return {
            "response": (
                f"[no-LLM fallback] {self.AGENT_TYPE} agent received: {user_query!r}. "
                f"Available tools: {', '.join(self.list_tools())}"
            ),
            "agent_id": self.agent_id,
        }

    def _build_maf_agent(self):
        """Build (once) a MAF ``Agent`` configured with our policy-enforced tools.

        Sends chat requests to the Foundry account's Azure OpenAI data-plane
        host (derived from the project endpoint). Authentication is always
        Entra ID via ``DefaultAzureCredential`` — ``az login`` locally,
        Managed Identity in production. No API key needed.
        """
        if self._maf_agent is not None:
            return self._maf_agent

        # Imported lazily so basic tests / demos work without MAF installed.
        from agent_framework import Agent
        from agent_framework.openai import OpenAIChatClient
        from azure.identity import DefaultAzureCredential

        chat_client = OpenAIChatClient(
            model=self.settings.model_deployment_name,
            azure_endpoint=self.settings.chat_endpoint(),
            api_version=self.settings.model_api_version,
            credential=DefaultAzureCredential(),
        )

        self._maf_agent = Agent(
            client=chat_client,
            instructions=self._system_prompt(),
            name=f"{self.AGENT_TYPE}-agent",
            tools=list(self._tools.values()),
        )
        return self._maf_agent
