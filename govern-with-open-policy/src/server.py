"""HTTP server wrapper for Foundry / Container Apps deployment.

Endpoints:
    GET  /health                       -> {"status": "healthy"}
    GET  /tools                        -> {"tools": [...]}
    POST /invoke   {"message": str}    -> {"response": ..., "tool_calls": [...]}
    POST /tool     {"name": str, "arguments": {...}}
                                       -> direct tool call (bypasses LLM)

The agent type is selected via the AGENT_TYPE env var. Valid values:
    customer_service | inventory | order_processing | returns
"""

from __future__ import annotations

import json
import logging
import os
import sys
from http.server import BaseHTTPRequestHandler, HTTPServer
from typing import Any, Dict

from .agents import (
    BaseAgent,
    CustomerServiceAgent,
    InventoryAgent,
    OrderProcessingAgent,
    ReturnsAgent,
)

logging.basicConfig(
    level=os.environ.get("LOG_LEVEL", "INFO"),
    format="%(asctime)s %(levelname)s %(name)s %(message)s",
)
logger = logging.getLogger("agent-server")


AGENT_REGISTRY = {
    "customer_service": (CustomerServiceAgent, "foundry-cs-001"),
    "inventory": (InventoryAgent, "foundry-inv-001"),
    "order_processing": (OrderProcessingAgent, "foundry-ord-001"),
    "returns": (ReturnsAgent, "foundry-ret-001"),
}


def create_agent(agent_type: str) -> BaseAgent:
    if agent_type not in AGENT_REGISTRY:
        raise ValueError(f"Unknown AGENT_TYPE={agent_type!r}; valid: {list(AGENT_REGISTRY)}")
    cls, agent_id = AGENT_REGISTRY[agent_type]
    return cls(agent_id=agent_id)


class _Handler(BaseHTTPRequestHandler):
    agent: BaseAgent = None  # set in run_server

    def log_message(self, fmt: str, *args: Any) -> None:  # noqa: D401
        logger.info(fmt, *args)

    # ---- helpers ----
    def _send_json(self, status: int, payload: Dict[str, Any]) -> None:
        body = json.dumps(payload).encode()
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _read_json(self) -> Dict[str, Any]:
        length = int(self.headers.get("Content-Length", "0"))
        if length == 0:
            return {}
        return json.loads(self.rfile.read(length).decode())

    # ---- routes ----
    def do_GET(self) -> None:  # noqa: N802
        if self.path == "/health":
            self._send_json(200, {"status": "healthy", "agent": self.agent.AGENT_TYPE})
        elif self.path == "/tools":
            self._send_json(200, {"tools": self.agent.list_tools()})
        else:
            self._send_json(404, {"error": "not found"})

    def do_POST(self) -> None:  # noqa: N802
        try:
            body = self._read_json()
            if self.path == "/invoke":
                message = body.get("message", "")
                self._send_json(200, self.agent.ask(message))
            elif self.path == "/tool":
                name = body["name"]
                args = body.get("arguments", {})
                self._send_json(200, self.agent.invoke_tool(name, args))
            else:
                self._send_json(404, {"error": "not found"})
        except Exception as exc:  # noqa: BLE001
            logger.exception("Request failed")
            self._send_json(500, {"error": str(exc)})


def run_server(port: int = 8000) -> None:
    agent_type = os.environ.get("AGENT_TYPE", "customer_service")
    agent = create_agent(agent_type)
    _Handler.agent = agent

    logger.info("Starting %s agent on :%d (id=%s)", agent_type, port, agent.agent_id)
    logger.info("Tools: %s", ", ".join(agent.list_tools()))

    httpd = HTTPServer(("", port), _Handler)
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        logger.info("Shutting down")
        httpd.shutdown()


if __name__ == "__main__":
    run_server(int(os.environ.get("PORT", "8000")))
