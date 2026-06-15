# how-to-agents

> Self-contained, bite-sized workshops on all things agents — built for builders tackling the big problems.

This monorepo houses hands-on learning workshops that cover different tools, frameworks, and paradigms in the world of building intelligent agents. Each workshop is independent and can be taken on its own — no need to do them in order.

---

## Workshops

### 🤖 [Build with Microsoft Agent Framework](./build-with-microsoft-agent-framework/)

A notebook-based walkthrough course on the **Microsoft Agent Framework (MAF)** for Python.

Covers the full agent development lifecycle: from your first streaming agent to multi-agent orchestration, middleware, MCP integration, and production-style API hosting. All examples use insurance and banking use cases to keep things grounded.

**Best for:** Developers new to MAF who want a structured, hands-on path from zero to production-ready agent patterns.

→ [Go to workshop](./build-with-microsoft-agent-framework/README.md)

---

### 🔐 [Govern with Open Policy Agent](./govern-with-open-policy/)

A practical workshop on applying **Open Policy Agent (OPA)** to AI agent systems.

Explores how to enforce policy at inference time, gate tool use, validate structured outputs, and integrate governance into agentic pipelines. Includes real-world examples and a full Docker-based test environment.

**Best for:** Engineers and platform teams who need to understand how to build trustworthy, auditable, and compliant agent systems.

→ [Go to workshop](./govern-with-open-policy/README.md)

---

## Principles

- **Self-contained** — each workshop runs independently with its own dependencies and setup.
- **Bite-sized** — focused scope, clear learning outcomes, no fluff.
- **Builder-first** — every workshop solves a real problem, not a toy example.
- **Opinionated** — uses modern tooling (`uv`, Docker, Azure AI Foundry) so you're learning production patterns from day one.

---

## Contributing a Workshop

New workshops should be added as top-level directories following the naming pattern `verb-with-<technology>` (e.g. `orchestrate-with-temporal`, `observe-with-langfuse`). Each workshop must include:

- `README.md` — overview, learning outcomes, setup instructions
- `pyproject.toml` (or equivalent) — isolated dependencies
- Working examples that run end to end

---

## Prerequisites (shared across workshops)

- Python 3.10+
- [uv](https://docs.astral.sh/uv/) installed
- [Docker](https://docs.docker.com/get-docker/) (for workshops that use containers)
- Azure CLI (`az`) — for workshops using Azure AI Foundry
