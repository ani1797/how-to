# Microsoft Agent Framework — Walkthrough Course

A bite-sized, notebook-based intro course on **Microsoft Agent Framework** for Python.
All examples use Insurance and Banking use cases to keep things relatable.

## Notebooks

| # | Notebook | What you'll learn |
|---|---------|-------------------|
| 01 | Hello Agent | Create your first agent, streaming vs non-streaming |
| 02 | Function Tools | Give agents callable tools (insurance quoting) |
| 03 | Structured Output | Parse free-text into typed Pydantic models (claims) |
| 04 | Multi-Turn Conversations | Session-based memory (banking chatbot) |
| 05 | Agent as Tool | Compose agents — specialist sub-agents (underwriting) |
| 06 | Middleware | Compliance logging, PII guard, timing (banking) |
| 07 | Workflows Intro | Executors, edges, pipelines (loan processing) |
| 08 | Multi-Agent Orchestration | Sequential & concurrent patterns (claims, quotes) |
| 09 | MCP with Agent Framework | Wrap MCP calls as tools for grounded responses |
| 10 | Hosting Microsoft Agent on API | Learn about deploying a model to a FastAPI for quick inferences (Non Foundry Deployments) |

## Setup

```bash
# 1. Clone and enter the repo
cd microsoft-agents-framework-walkthrough

# 2. Copy the env template and fill in your deployment name
cp .env.example .env

# 3. Install dependencies with uv (prerelease flag needed for RC packages)
uv sync

# 4. Login to Azure (used for authentication — no API keys needed)
az login

# 5. Open any notebook and run it
```

## Prerequisites

- Python 3.10+
- [uv](https://docs.astral.sh/uv/) installed
- Azure CLI (`az`) installed and logged in
- An Azure AI Foundry project with a deployed model (e.g. `gpt-4o`)
