# how-to

> Self-contained, bite-sized workshops built for builders tackling the big problems.

Each workshop is independent — pick the one that solves your problem today. No prerequisites between them.

---

## 🤖 Agents

Workshops on building, governing, and operating AI agents.

### [Build with Microsoft Agent Framework](./build-with-microsoft-agent-framework/)
A notebook-based walkthrough of **Microsoft Agent Framework (MAF)** for Python. Covers the full lifecycle — streaming agents, function tools, multi-agent orchestration, middleware, MCP integration, and API hosting. Insurance and banking use cases throughout.
→ [Go to workshop](./build-with-microsoft-agent-framework/README.md)

### [Govern with Open Policy Agent](./govern-with-open-policy/)
A practical workshop on applying **Open Policy Agent (OPA)** to AI agent systems. Enforce policy at inference time, gate tool use, validate structured outputs, and integrate governance into agentic pipelines. Includes a full Docker-based test environment.
→ [Go to workshop](./govern-with-open-policy/README.md)

---

## ☁️ Azure AI

Workshops on Azure AI services — hands-on, scenario-driven.

### [Extract with Document Intelligence](./extract-with-document-intelligence/)
A bite-sized intro to **Azure Document Intelligence** (formerly Form Recognizer). Each notebook covers one extraction feature against a real insurance scenario — claims, invoices, IDs, health cards — ready to run in minutes.
→ [Go to workshop](./extract-with-document-intelligence/README.md)

---

## 📊 Data & ML

Workshops on data engineering, ML experiment tracking, and Databricks platform patterns.

### [Query with SQL AI](./query-with-sql-ai/)
A CLI tool and workshop demonstrating **natural language → SQL** using LLMs. Supports multiple backends (OpenAI + Ollama), jinja2 prompt templates, and a schema-aware query pipeline. Good foundation for building NL interfaces on top of databases.
→ [Go to workshop](./query-with-sql-ai/)

### [Track with MLflow](./track-with-mlflow/)
End-to-end **MLflow experiment tracking** pipeline with ingest, transform, train, and runtime stages. Includes Jenkins CI/CD config and multi-environment setup (nonprod/prod). A repeatable pattern for reproducible ML.
→ [Go to workshop](./track-with-mlflow/)

### [Manage with Unity Catalog](./manage-with-unity-catalog/)
A CLI tool for managing **Databricks Unity Catalog** — schema creation, query collection, and catalog expansion for data teams. Includes a devcontainer and research notebooks.
→ [Go to workshop](./manage-with-unity-catalog/)

### [Deploy with Databricks](./deploy-with-databricks/)
A production-ready **Databricks Asset Bundle** setup with full CI/CD (validate, deploy, release workflows), ML experiment configs, and schema definitions. Repeatable pattern for deploying models and experiments on Databricks.
→ [Go to workshop](./deploy-with-databricks/)

---

## 🧪 Testing & Integration

Workshops on integration testing patterns and messaging infrastructure.

### [Test with RabbitMQ](./test-with-rabbitmq/)
A Spring Boot workshop demonstrating **integration testing with Apache AMQP/QPID**. Uses an embedded in-memory QPID broker to run full message-passing tests without external infrastructure. A repeatable pattern for testing any RabbitMQ-based service reliably in CI.
→ [Go to workshop](./test-with-rabbitmq/)

---

## 🏗️ Platform

Workshops on infrastructure, deployment, and operations.

### [Deploy with Kubernetes](./deploy-with-kubernetes/)
A hands-on introduction to **Kubernetes** fundamentals. Covers pods, deployments, services, ingress, and environment configuration using a real Node.js app. Good foundation before moving to production-grade orchestration.
→ [Go to workshop](./deploy-with-kubernetes/README.md)

---

## Principles

- **Self-contained** — each workshop has its own dependencies, setup, and scope.
- **Bite-sized** — focused learning outcomes, no filler.
- **Builder-first** — every workshop solves a real problem, not a toy example.
- **Opinionated** — modern tooling (`uv`, Docker, Azure AI Foundry) so you learn production patterns from day one.

---

## Adding a Workshop

Add a top-level directory using the pattern `verb-with-<technology>` (e.g. `orchestrate-with-temporal`, `observe-with-langfuse`). Each workshop must include:

- `README.md` — overview, learning outcomes, setup
- `pyproject.toml` or equivalent — isolated dependencies
- Working examples that run end to end

Place it under the right category in this README.

---

## Common Prerequisites

- Python 3.10+ · [uv](https://docs.astral.sh/uv/) installed
- [Docker](https://docs.docker.com/get-docker/) — for container-based workshops
- Azure CLI (`az`) — for Azure AI Foundry workshops
