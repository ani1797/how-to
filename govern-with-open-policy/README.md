# Retail AI Agent Policy Workshop

## Policy Enforcement for AI Agents with Microsoft Agent Framework & OPA

This workshop demonstrates how to enforce **OPA-A (Authorization)** and **OPA-B (Behavior)** policies on AI agent tool execution using Microsoft Agent Framework Middlewares. Learn how to build secure, policy-governed AI agents with robust authorization and behavior controls.

> **Comparison**: See [docs/OPA_VS_AGENT_GOVERNANCE.md](docs/OPA_VS_AGENT_GOVERNANCE.md) for detailed comparison with Azure AI Agent Governance Toolkit

---

## 🎯 Workshop Overview

**Core Concept**: AI agents powered by LLMs use tools to perform business operations. Every tool execution must be policy-enforced:

1. **OPA-A (Authorization)**: Can this agent use this tool? *(checked before execution)*
2. **OPA-B (Behavior)**: Should this usage be constrained? *(checked after execution)*
3. **Audit Trail**: Every decision is logged for compliance

**What You'll Learn**:
- Build AI agents that select and execute tools with policy enforcement
- Implement authorization rules using Open Policy Agent (OPA) and Rego
- Apply behavior constraints (rate limiting, workflow enforcement)
- Integrate policy middleware with Microsoft Agent Framework
- Compare OPA approach with Agent Governance Toolkit
- Deploy to Azure AI Foundry

---

## 🚀 Quick Start

### 1. Prerequisites

- Python 3.11+
- Docker (for OPA server)
- Azure OpenAI endpoint (optional - works in mock mode without)

### 2. Installation

```bash
# Install uv package manager
pip install uv

# Install dependencies
uv sync --all-extras

# Copy environment template
cp .env.template .env
```

### 3. Start OPA Server

```bash
docker-compose up -d

# Verify OPA is running
curl http://localhost:8181/health
```

### 4. Run AI Agent Demo

```bash
python scripts/demo_ai_agent.py
```

This demonstrates:
- ✅ AI agent selecting tools based on user queries
- ✅ OPA-A authorization before tool execution  
- ✅ OPA-B behavior checks after execution
- ✅ Policy denials when rules not met
- ✅ Complete audit trail in `logs/policy-audit.jsonl`

---

## � Documentation & Workshop Flow

| Step | Document | Purpose |
|------|----------|---------|
| 1 | **[docs/QUICKSTART.md](docs/QUICKSTART.md)** | Get system running in 5 minutes |
| 2 | **[docs/AI_AGENT_PATTERN.md](docs/AI_AGENT_PATTERN.md)** | Understand AI agent + tool use pattern |
| 3 | Run `demo_ai_agent.py` | See pattern in action |
| 4 | **[docs/OPA_VS_AGENT_GOVERNANCE.md](docs/OPA_VS_AGENT_GOVERNANCE.md)** | **Compare OPA vs. Agent Governance Toolkit** |
| 5 | Work through Notebooks 01-05 | Hands-on exercises |
| 6 | **[docs/ARCHITECTURE.md](docs/ARCHITECTURE.md)** | Deep technical dive |
## 🏗️ Architecture

```
┌─────────────────────────────────────┐
│         User Query                  │
│  "What's customer C001's email?"    │
└─────────────┬───────────────────────┘
              │
┌─────────────▼───────────────────────┐
│       AI Agent (LLM)                │
│  • Analyzes query                   │
│  • Selects tool via function call   │
│  • Tool: access_customer_pii()      │
└─────────────┬───────────────────────┘
              │
┌─────────────▼───────────────────────┐
│  Policy Enforcement Middleware      │
│  ┌────────────────────────────────┐ │
│  │ OPA-A (Authorization)          │ │
│  │ ✓ Role: customer_service?      │ │
│  │ ✓ Customer consent given?      │ │
│  │ Result: AUTHORIZED             │ │
│  └────────────────────────────────┘ │
└─────────────┬───────────────────────┘
              │
┌─────────────▼───────────────────────┐
│       Execute Tool                  │
│  • Retrieve PII from database       │
│  • Returns: {email, phone...}       │
└─────────────┬───────────────────────┘
              │
┌─────────────▼───────────────────────┐
│  Policy Enforcement Middleware      │
│  ┌────────────────────────────────┐ │
│  │ OPA-B (Behavior)               │ │
│  │ ✓ Rate limit: 45/min < 100?   │ │
│  │ ✓ Audit log written            │ │
│  │ Result: OK                     │ │
│  └────────────────────────────────┘ │
└─────────────┬───────────────────────┘
              │
┌─────────────▼───────────────────────┐
│    AI Agent Response                │
│  "The email for customer C001       │
│   is jane@example.com..."           │
└─────────────────────────────────────┘
```

### Policy Layers

**OPA-A (Authorization)** - `src/policies/authorization.rego`  
Answers: *"Can this agent perform this action?"*
- Role-based access control (RBAC)
- Resource-level permissions
- Consent verification
- Tiered authorization

**OPA-B (Behavior)** - `src/policies/behavior.rego`  
Answers: *"Should this agent's behavior be constrained?"*
- Rate limiting (100 actions/min)
- Bulk access controls
- Workflow enforcement (approval requirements)
- Anomaly detection

---

## � AI Agent Implementation

### Components

**AI Agent Base** - `src/agents/ai_base_agent.py`
- LLM-powered with Azure OpenAI integration
- Function calling for tool selection
- Automatic policy enforcement via middleware
- Natural language interaction

**Example: AI Customer Service Agent** - `src/agents/ai_customer_service.py`

4 policy-enforced tools:
1. `access_customer_pii` - Access PII with consent verification
2. `view_customer_profile` - View basic customer data
3. `update_customer_tier` - Update loyalty tier with authorization
4. `handle_customer_inquiry` - General support queries

Every tool execution flows through middleware for OPA-A and OPA-B checks.

### Tool Execution Pattern

```python
# User asks: "What's Jane's email?"
# ↓
# AI Agent analyzes query and selects tool
# ↓
action = RetailAction(
    action_type=ActionType.ACCESS_PII,
    resource={"customer_id": "C001", "consent_given": True},
    context={"purpose": "customer_support"}
)
# ↓
# Middleware enforces OPA-A (authorization)
# ↓
# Tool executes business logic
# ↓
# Middleware enforces OPA-B (behavior)
# ↓
# Result returned to AI agent for natural language response
```

---

## 📦 Project Structure

```
agent-policy-opa/
├── src/
│   ├── agents/                    # AI Agent implementations
│   │   ├── ai_base_agent.py       # ⭐ AI agent base class
│   │   ├── ai_customer_service.py # ⭐ Example AI agent with tools
│   │   └── agent_server.py        # HTTP server for Foundry deployment
│   ├── policies/                  # OPA Rego policies
│   │   ├── authorization.rego     # OPA-A policies
│   │   ├── behavior.rego          # OPA-B policies
│   │   └── README.md
│   ├── opa_client/                # OPA integration
│   │   └── client.py              # OPA REST API client
│   └── common/                    # Shared utilities
│       ├── models.py              # Pydantic models
│       ├── config.py              # Settings
│       └── policy_middleware.py   # ⭐ Policy enforcement middleware
├── tests/                         # Test suite
│   └── test_policies/             # Policy tests
├── notebooks/                     # Workshop notebooks (01-06)
│   ├── 01-setup-and-intro.ipynb
│   ├── 02-opa-authorization.ipynb
│   ├── 03-opa-behavior.ipynb
│   ├── 05-policy-violations.ipynb
│   └── 06-foundry-deployment.ipynb
├── scripts/                       # Demo scripts
│   ├── demo_ai_agent.py           # ⭐ MAIN DEMO
│   ├── deploy_to_foundry.py       # Deployment automation
│   └── validate_deployment.py     # Validation checks
├── .foundry/                      # Foundry deployment configs
├── docker-compose.yml             # OPA server setup
├── OPA_VS_AGENT_GOVERNANCE.md     # ⭐ Comparison document
└── README.md                      # This file
```

---

## �📚 Workshop Materials

### Notebooks (Recommended Order)

1. **01-setup-and-intro.ipynb** - Workshop introduction and setup verification
2. **02-opa-authorization.ipynb** - Deep dive into OPA-A authorization patterns
3. **03-opa-behavior.ipynb** - Deep dive into OPA-B behavior constraints
4. **05-policy-violations.ipynb** - Debugging policy denials and audit logs
5. **06-foundry-deployment.ipynb** - Deploy to Azure AI Foundry

### Demo Scripts

- **`scripts/demo_ai_agent.py`** - Main demonstration of AI agent with policy-enforced tools
- `scripts/deploy_to_foundry.py` - Automated deployment to Foundry
- `scripts/validate_deployment.py` - Validate deployment readiness

---

## 📊 Policy Examples

### OPA-A: Authorization

```rego
# src/policies/authorization.rego
package retail.authorization

default allow = false

# Customer service can access PII with consent
allow if {
    input.agent.role == "customer_service"
    input.action == "access_pii"
    input.resource.consent_given == true
}

# Store managers can access PII without consent
allow if {
    input.agent.role == "store_manager"
    input.action == "access_pii"
}
```

### OPA-B: Behavior Constraints

```rego
# src/policies/behavior.rego
package retail.behavior

default allow = true

# Rate limiting
deny contains msg if {
    count(input.recent_actions) > 100
    msg := "Rate limit exceeded: max 100 actions per minute"
}

# Bulk PII access requires compliance role
deny contains msg if {
    input.action == "bulk_access_pii"
    count(input.resource.customer_ids) > 50
    not input.agent.role == "compliance_officer"
    msg := "Bulk PII access >50 customers requires compliance_officer role"
}
```

---

## 🧪 Testing

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src --cov-report=html

# Test specific components
pytest tests/test_policies/        # Policy tests
pytest -v tests/test_policies/test_authorization.py

# Check OPA policy syntax
opa check src/policies/authorization.rego
opa check src/policies/behavior.rego
```

---

## 🌐 Deployment to Azure AI Foundry

### Prerequisites

- Azure AI Foundry project
- Model deployed (e.g., gpt-4o)
- Azure Container Registry
- Azure CLI authenticated

### Quick Deploy

```bash
# 1. Configure .env
FOUNDRY_PROJECT_ENDPOINT=https://your-project.api.azureml.ms
MODEL_NAME=gpt-4o
MODEL_DEPLOYMENT_NAME=gpt-4o

# 2. Deploy (see notebook 06 for details)
python scripts/deploy_to_foundry.py

# 3. Validate
python scripts/validate_deployment.py
```

Detailed steps in `notebooks/06-foundry-deployment.ipynb` and `.foundry/README.md`.

---

## 🔍 Debugging & Audit Logs

All policy decisions are logged to `logs/policy-audit.jsonl`:

```json
{
  "timestamp": "2026-05-26T10:30:45Z",
  "agent_id": "cs-agent-001",
  "action": "access_pii",
  "decision": {
    "allow": false,
    "reason": "Customer consent not given"
  },
  "context": {
    "customer_id": "C001",
    "agent_role": "cashier"
  }
}
```

View audit logs:
```python
import json

with open('logs/policy-audit.jsonl') as f:
    for line in f:
        entry = json.loads(line)
        if not entry['decision']['allow']:
            print(f"DENIED: {entry['agent_id']} - {entry['decision']['reason']}")
```

---

## 🆚 OPA vs. Agent Governance Toolkit

| Feature | OPA + Middleware | Agent Governance Toolkit |
|---------|------------------|--------------------------|
| **Policy Language** | Rego (declarative) | Python/Config |
| **Enforcement Point** | Tool execution layer | Agent invocation layer |
| **Flexibility** | High (custom logic) | Moderate (patterns) |
| **Azure Integration** | Manual | Native |
| **Learning Curve** | Moderate (Rego) | Low (Python) |

👉 See **[docs/OPA_VS_AGENT_GOVERNANCE.md](docs/OPA_VS_AGENT_GOVERNANCE.md)** for comprehensive comparison

---

## 🤝 Contributing

This is a workshop project for educational purposes. For improvements:

1. Test policy changes: `opa check src/policies/*.rego`
2. Run test suite: `pytest`
3. Update documentation as needed
4. Maintain separation: policies vs. business logic

---

## 📖 Additional Resources

- [Open Policy Agent Documentation](https://www.openpolicyagent.org/docs/latest/)
- [Rego Policy Language](https://www.openpolicyagent.org/docs/latest/policy-language/)
- [Microsoft Agent Framework](https://learn.microsoft.com/azure/ai-services/agents/)
- [Azure AI Foundry](https://learn.microsoft.com/azure/ai-services/foundry/)

---

## � Support

For workshop questions or issues:
- Check `logs/policy-audit.jsonl` for policy denials
- Review OPA server logs: `docker-compose logs opa`
- See `notebooks/05-policy-violations.ipynb` for debugging guide
- Refer to [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) for system details

---

**Workshop Focus**: This project demonstrates the **OPA + Microsoft Agent Framework Middleware** pattern for policy-governed AI agents. The approach provides maximum flexibility for custom business rules while maintaining clean separation between policies and code.

For alternative approaches, see the comparison with Agent Governance Toolkit in [docs/OPA_VS_AGENT_GOVERNANCE.md](docs/OPA_VS_AGENT_GOVERNANCE.md).
