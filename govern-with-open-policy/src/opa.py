"""Tiny OPA REST client. One method: `evaluate(policy_path, input_data)`."""

import logging
from typing import Any, Dict, Optional
from urllib.parse import urljoin

import requests
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)


class PolicyDecision(BaseModel):
    """Result returned from OPA."""

    allow: bool
    reason: Optional[str] = None
    raw: Dict[str, Any] = Field(default_factory=dict)


class OPAError(RuntimeError):
    """Raised when OPA itself cannot be reached / errors out."""


class OPAClient:
    """Minimal client for the OPA HTTP Data API."""

    def __init__(self, base_url: str = "http://localhost:8181") -> None:
        self.base_url = base_url.rstrip("/")

    # ------------------------------------------------------------------
    def health_check(self) -> bool:
        try:
            r = requests.get(urljoin(self.base_url + "/", "health"), timeout=5)
            return r.status_code == 200
        except requests.RequestException as exc:
            logger.warning("OPA health check failed: %s", exc)
            return False

    # ------------------------------------------------------------------
    def evaluate(self, policy_path: str, input_data: Dict[str, Any]) -> PolicyDecision:
        """Evaluate a policy.

        Args:
            policy_path: e.g. ``"retail/authorization"`` (we always read
                ``allow`` and ``reason`` from the package).
            input_data: ``input`` document for OPA.
        """
        url = f"{self.base_url}/v1/data/{policy_path.strip('/')}"
        try:
            r = requests.post(url, json={"input": input_data}, timeout=10)
            r.raise_for_status()
        except requests.RequestException as exc:
            raise OPAError(f"OPA request failed: {exc}") from exc

        result = r.json().get("result", {})

        if isinstance(result, bool):
            return PolicyDecision(allow=result, raw={"allow": result})
        if isinstance(result, dict):
            return PolicyDecision(
                allow=bool(result.get("allow", False)),
                reason=result.get("reason"),
                raw=result,
            )
        return PolicyDecision(allow=False, reason=f"Unexpected OPA result: {result!r}")
