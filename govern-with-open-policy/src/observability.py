"""OpenTelemetry tracing helper for the workshop.

Microsoft Agent Framework already auto-instruments chat clients and agents.
This module just wires the OTLP exporter so traces show up in the Foundry
Toolkit trace viewer (or any other OTLP-compatible collector).

Usage::

    from src.observability import configure_tracing
    configure_tracing()                 # honours ENABLE_TRACING / OTEL endpoint

    from src.agents import CustomerServiceAgent
    agent = CustomerServiceAgent(agent_id="demo")
    agent.ask("...")                   # spans now emitted to OTLP

In VS Code, run command ``ai-mlstudio.tracing.open`` (Foundry Toolkit) first
to launch the local collector on ``localhost:4317``.
"""

from __future__ import annotations

import logging
import os
from typing import Optional

from .config import get_settings

logger = logging.getLogger(__name__)

_configured = False


def configure_tracing(force: bool = False, endpoint: Optional[str] = None) -> bool:
    """Configure OpenTelemetry providers for MAF auto-instrumentation.

    Returns True if tracing was configured, False if skipped (already done or
    ``ENABLE_TRACING`` is unset).
    """
    global _configured

    if _configured and not force:
        return False

    settings = get_settings()
    if not settings.enable_tracing and not force:
        logger.debug("Tracing disabled (ENABLE_TRACING=false); skipping setup")
        return False

    otlp_endpoint = endpoint or settings.otel_exporter_otlp_endpoint
    os.environ.setdefault("OTEL_EXPORTER_OTLP_ENDPOINT", otlp_endpoint)

    try:
        from agent_framework.observability import configure_otel_providers
    except ImportError as exc:  # pragma: no cover
        logger.warning("agent-framework not installed; tracing disabled: %s", exc)
        return False

    configure_otel_providers(enable_sensitive_data=True)
    _configured = True
    logger.info("OpenTelemetry tracing configured -> %s", otlp_endpoint)
    return True


__all__ = ["configure_tracing"]
