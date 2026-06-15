# Copilot Instructions: Retail AI Agent Policy Workshop

## Project Overview

This is a **workshop project** demonstrating **OPA-A (Authorization) and OPA-B (Behavior)** policy enforcement in AI agentic workflows using **Microsoft Agent Framework Middlewares**. The project also provides comparison with **Azure AI Agent Governance Toolkit**.

**Tech Stack:**
- **Python 3.11+** with uv package manager
- **Open Policy Agent (OPA)** for policy evaluation
- **Microsoft Agent Framework SDK** for agent runtime
- **AI Agents** with LLM-powered tool selection
- **Rego policies** for authorization and behavior constraints

## Core Concepts

### OPA-A (Authorization Policies)
Answer: **"Can this agent perform this action?"**

- Role-based access control (RBAC)
- Resource-level permissions
- Located in: `src/policies/authorization.rego`
- Examples: PII access, inventory RBAC, pricing tiers, transaction limits

### OPA-B (Behavior Policies)
Answer: **"Should this agent's behavior be constrained?"**

- Rate limiting and throttling
- Workflow enforcement
- Anomaly detection
- Located in: `src/policies/behavior.rego`
- Examples: Max actions/min, bulk access controls, approval workflows

## Project Structure (Streamlined)

```
src/
├── agents/                       # AI Agent implementations
│   ├── ai_base_agent.py         # ⭐ AI agent base class (LLM-powered)
│   ├── ai_customer_service.py   # ⭐ Example AI agent with 4 tools
│   └── agent_server.py          # HTTP server for Foundry deployment
├── policies/                     # OPA Rego policies
│   ├── authorization.rego       # OPA-A: RBAC policies
│   └── behavior.rego            # OPA-B: Constraint policies
├── opa_client/                   # OPA REST API integration
│   └── client.py                # OPAClient class
└── common/                       # Shared utilities
    ├── models.py                # Pydantic models (AgentContext, RetailAction, etc.)
    ├── config.py                # Settings management
    └── policy_middleware.py     # ⭐ PolicyEnforcementMiddleware
```

## Key Classes and Patterns

### AI Agent Development

**All AI agents inherit from `AIRetailAgent`:**

```python
from src.agents.ai_base_agent import AIRetailAgent
from src.common.models import AgentRole, RetailAction, ActionType

class MyAIAgent(AIRetailAgent):
    def __init__(self, agent_id: str, role: AgentRole):
        super().__init__(
            agent_id=agent_id,
            agent_type="my_ai_agent",
            role=role,
            model_name="gpt-4o"  # or from config
        )
    
    def tool_example(self, param: str) -> dict:
        """Example tool that gets policy-enforced.
        
        This docstring is visible to the LLM for tool selection.
        """
        # Create action for policy check
        action = RetailAction(
            action_type=ActionType.READ,
            resource={"type": "resource_type", "param": param},
            context={"purpose": "example"}
        )
        
        # Execute with automatic policy enforcement
        result = self.execute_ai_action(action)
        
        # Business logic here
        return {"status": "success", "data": result}
```

### Tool Execution Flow

```
User Query → AI Agent (LLM) → Tool Selection → 
OPA-A (Authorization) → Tool Execution → 
OPA-B (Behavior) → Response
```

Every tool execution is automatically policy-enforced through the middleware pattern.

### Policy Middleware Usage

The `PolicyEnforcementMiddleware` is automatically created by `AIRetailAgent`. It provides:

- `enforce_authorization()` - OPA-A checks
- `enforce_behavior()` - OPA-B checks  
- `enforce_combined()` - Both OPA-A and OPA-B

AI agents call `self.execute_ai_action(action)` which automatically runs policy checks.

### Common Models

Import from `src.common.models`:

- `AgentRole` - Enum of agent roles (CASHIER, STORE_MANAGER, etc.)
- `AgentContext` - Agent identity and context for policy evaluation
- `RetailAction` - Action to be performed (action_type, resource, context)
- `ActionType` - Enum of action types (READ, WRITE, UPDATE, ACCESS_PII, etc.)
- `Customer`, `Product`, `Transaction`, `InventoryItem` - Domain models

## Writing Rego Policies

### OPA-A (Authorization) Pattern

```rego
package retail.authorization

default allow = false

# Rule: customer_service can access PII with consent
allow if {
    input.action == "access_pii"
    input.agent.role == "customer_service"
    input.resource.consent_given == true
}
```

### OPA-B (Behavior) Pattern

```rego
package retail.behavior

default allow = true  # Behavior policies are constraints, not primary auth

deny contains msg if {
    count(input.recent_actions) > 100
    msg := "Rate limit exceeded: max 100 actions per minute"
}

allow if { count(deny) == 0 }
```

## Common Development Tasks

### Adding a New AI Agent

1. Create new file in `src/agents/`
2. Inherit from `AIRetailAgent`
3. Define role in constructor
4. Implement tool methods (each method becomes a tool for the LLM)
5. Create `RetailAction` for each tool operation
6. Use `execute_ai_action()` for policy enforcement
7. Add docstrings (visible to LLM for tool selection)

### Adding a New Policy

1. Edit `src/policies/authorization.rego` (OPA-A) or `behavior.rego` (OPA-B)
2. Follow existing patterns
3. Test with `opa eval` command or unit tests
4. OPA server auto-reloads policies from volume mount

### Testing Policies

```bash
# Syntax check
opa check src/policies/authorization.rego

# Test with input
echo '{"agent": {"role": "cashier"}, "action": "read"}' | \
  opa eval -d src/policies/authorization.rego -I "data.retail.authorization.allow"
```

### Testing AI Agents

Use pytest:

```python
from src.agents.ai_customer_service import AICustomerServiceAgent
from src.common.models import AgentRole, Customer

def test_ai_agent_pii_access():
    agent = AICustomerServiceAgent(agent_id="test-001")
    customer = Customer(customer_id="C001", consent_given=True, ...)
    
    # Should succeed
    result = agent.access_customer_pii("C001", customer)
    assert result is not None
```

## Environment Configuration

Settings in `.env` (see `.env.template`):

- `OPA_URL` - OPA server endpoint (default: http://localhost:8181)
- `USE_MOCK_DATA` - Use mock data for offline testing
- `ENABLE_POLICY_AUDIT` - Enable audit logging to `logs/policy-audit.jsonl`
- `FOUNDRY_PROJECT_ENDPOINT` - Azure AI Foundry endpoint (optional)

## OPA Server Management

```bash
# Start OPA
docker-compose up -d opa

# Check health
curl http://localhost:8181/health

# View logs
docker-compose logs -f opa

# Restart (to reload policies)
docker-compose restart opa
```

## Debugging Tips

### Policy Denials

1. Check audit log: `logs/policy-audit.jsonl`
2. Look for `"allow": false` with reason
3. Verify input data matches policy expectations
4. Test policy directly with OPA CLI

### Agent Errors

1. Ensure OPA server is running (`docker-compose ps`)
2. Check agent role matches policy requirements
3. Verify `AgentContext` is properly initialized
4. Check `_recent_actions` tracking for behavior policies

### Import Errors

- Activate virtual environment: `source .venv/bin/activate`
- Ensure in project root directory
- Run `uv sync` to install dependencies

## Code Style Guidelines

- Use `black` for formatting: `black src/`
- Use `ruff` for linting: `ruff check src/`
- Type hints required for function signatures
- Docstrings required for public methods
- Follow existing patterns in `base_agent.py`

## Workshop Context

This is a **teaching project** focused on:

- Demonstrating OPA policy enforcement patterns with Microsoft Agent Framework Middlewares
- Comparing OPA approach with Azure AI Agent Governance Toolkit
- Showing real-world AI agent tool use patterns
- Providing hands-on examples for workshop participants
- Integrating with Microsoft Foundry for production deployment

When suggesting changes:
- Keep code simple and educational
- Add comments explaining policy concepts
- Provide clear examples in docstrings
- Consider workshop participant learning curve
- Focus on AI agents (not pattern demo agents)

## Comparison with Agent Governance Toolkit

See **`OPA_VS_AGENT_GOVERNANCE.md`** for comprehensive comparison:

- **OPA + Middleware**: Maximum flexibility, declarative Rego policies, tool-level enforcement
- **Agent Governance Toolkit**: Azure-native, Python-based, agent-level enforcement
- **When to use each**: Different scenarios and trade-offs
- **Hybrid approach**: Can combine both strategies

This workshop demonstrates the OPA approach to provide:
- Deep understanding of policy enforcement mechanics
- Maximum flexibility for custom business rules
- Separation of concerns between policies and code
- Skills transferable across platforms

## Microsoft Foundry Integration

The project can be deployed to Azure AI Foundry:

- Agent configurations in `.foundry/agent-metadata.yaml`
- Docker containers with OPA sidecar pattern
- Model selection from Foundry project
- See `notebooks/06-foundry-deployment.ipynb` for details

## Useful Commands

```bash
# Install dependencies
uv sync --extra all

# Run tests
pytest

# Start OPA
docker-compose up -d

# Format code
black src/ tests/

# Type check
mypy src/

# Run main demo (AI agent)
python scripts/demo_ai_agent.py

# Start Jupyter
jupyter notebook notebooks/
```

## Workshop Materials

### Demo Scripts
- **`scripts/demo_ai_agent.py`** - ⭐ Main demo (AI agent with tools)
- `scripts/deploy_to_foundry.py` - Deployment automation
- `scripts/validate_deployment.py` - Validation utilities

### Notebooks (5 total, in sequence)
1. `notebooks/01-setup-and-intro.ipynb` - Setup and introduction
2. `notebooks/02-opa-authorization.ipynb` - OPA-A deep dive
3. `notebooks/03-opa-behavior.ipynb` - OPA-B deep dive
4. `notebooks/05-policy-violations.ipynb` - Debugging and audit logs
5. `notebooks/06-foundry-deployment.ipynb` - Production deployment

### Documentation
- `README.md` - Main workshop guide (root level)
- `docs/README.md` - Documentation index
- `docs/QUICKSTART.md` - 5-minute getting started
- `docs/AI_AGENT_PATTERN.md` - Core AI agent + tool pattern
- **`docs/OPA_VS_AGENT_GOVERNANCE.md`** - ⭐ Comparison with Agent Governance Toolkit
- `docs/ARCHITECTURE.md` - Technical deep dive
- `docs/CLEANUP_SUMMARY.md` - Recent streamlining changes

## Policy Audit Logs

All policy decisions logged to `logs/policy-audit.jsonl`:

```python
import json

# Read audit entries
with open('logs/policy-audit.jsonl') as f:
    for line in f:
        entry = json.loads(line)
        if not entry['decision']['allow']:
            print(f"DENIED: {entry['agent_id']} - {entry['decision']['reason']}")
```

## Key Files to Reference

- `src/agents/ai_base_agent.py` - AI agent base implementation pattern
- `src/agents/ai_customer_service.py` - Example AI agent with 4 tools
- `src/common/policy_middleware.py` - Policy enforcement logic
- `src/policies/authorization.rego` - OPA-A reference policies
- `src/policies/behavior.rego` - OPA-B reference policies
- `README.md` - Main workshop guide
- `docs/README.md` - Documentation index
- `docs/OPA_VS_AGENT_GOVERNANCE.md` - Comparison document
- `docs/AI_AGENT_PATTERN.md` - Core pattern guide
- `docs/ARCHITECTURE.md` - System architecture

## When Modifying Code

1. **AI Agents**: Follow `AIRetailAgent` pattern, use `RetailAction` for all tool operations
2. **Policies**: Test with `opa eval` before committing
3. **Models**: Update Pydantic models in `common/models.py` with proper validation
4. **Tests**: Add tests for new features in `tests/` directory
5. **Docs**: Update README.md and relevant notebook if changing public API

## Remember

- **OPA-A** = Authorization (Can do?)
- **OPA-B** = Behavior (Should constrain?)
- All AI agents automatically get policy enforcement via `AIRetailAgent`
- Policy decisions are audited automatically when `ENABLE_POLICY_AUDIT=true`
- OPA policies auto-reload from `src/policies/` volume mount
- Workshop focuses on **AI agents with tool use**, not pattern demo agents

---

For more details, see README.md, AI_AGENT_PATTERN.md, and OPA_VS_AGENT_GOVERNANCE.md.
