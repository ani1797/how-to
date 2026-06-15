# AI Agent Tool Use with OPA Policy Enforcement

## Core Workshop Lesson

**"Policy Enforcement for Business Logic on AI Agents and their Tool Use"**

This workshop demonstrates how to enforce authorization and behavior policies on AI agents' tool execution, ensuring that business logic is governed by robust policy rules.

---

## 🎯 What You'll Learn

1. **AI Agents with Tools**: How LLM-powered agents use tools (business functions)
2. **OPA-A Authorization**: Policy enforcement **before** tool execution
3. **OPA-B Behavior**: Policy enforcement **after** tool execution  
4. **Audit Trail**: Complete logging of all policy decisions
5. **Production Patterns**: Real-world patterns for policy-governed AI systems

---

## 🏗️ Architecture: Policy-Enforced AI Agent Tools

```
┌─────────────────────────────────────────────────────────────┐
│ 1. User Query                                                │
│    "What's customer Jane Doe's email address?"               │
└────────────────────┬────────────────────────────────────────┘
                     │
┌────────────────────▼────────────────────────────────────────┐
│ 2. AI Agent (LLM)                                           │
│    • Analyzes natural language query                        │
│    • Decides which tool to call                             │
│    • Selects: access_customer_pii(customer_id="C001")       │
└────────────────────┬────────────────────────────────────────┘
                     │
┌────────────────────▼────────────────────────────────────────┐
│ 3. OPA-A Policy Check (BEFORE tool execution)              │
│    Authorization Layer                                      │
│    ✓ Is this agent role allowed to use this tool?          │
│    ✓ Does customer consent exist for PII access?           │
│    ✓ Are resource access conditions met?                   │
│    Result: AUTHORIZED or DENIED                             │
└────────────────────┬────────────────────────────────────────┘
                     │
┌────────────────────▼────────────────────────────────────────┐
│ 4. Execute Tool (Business Logic)                           │
│    • Query database for customer PII                        │
│    • Retrieve: {email, phone, address}                      │
│    • Return structured data                                 │
└────────────────────┬────────────────────────────────────────┘
                     │
┌────────────────────▼────────────────────────────────────────┐
│ 5. OPA-B Policy Check (AFTER tool execution)               │
│    Behavior Constraints Layer                               │
│    ✓ Rate limit: Is agent within action limits?            │
│    ✓ Audit: Log this action for compliance                 │
│    ✓ Patterns: Check for anomalous behavior                │
│    Result: ALLOWED or CONSTRAINED                           │
└────────────────────┬────────────────────────────────────────┘
                     │
┌────────────────────▼────────────────────────────────────────┐
│ 6. AI Agent Response                                        │
│    • LLM generates natural language response                │
│    • "Jane Doe's email is jane.doe@example.com..."         │
│    • Includes policy decision metadata                      │
└─────────────────────────────────────────────────────────────┘
```

---

## 🔑 Key Concepts

### AI Agent Tools

Tools are **business functions** that AI agents can call:

- `access_customer_pii` - Retrieve sensitive customer data
- `update_inventory_count` - Modify inventory levels
- `apply_discount` - Apply pricing discounts
- `process_refund` - Issue customer refunds

**Each tool execution is policy-enforced.**

### OPA-A: Authorization Policies

Answer: **"Can this agent use this tool?"**

```rego
# Example: PII access requires customer consent
allow if {
    input.action == "access_pii"
    input.agent.role == "customer_service"
    input.resource.consent_given == true  # ← Policy rule
}
```

**Enforcement Point**: Before tool execution

**Use Cases**:
- Role-based access control (RBAC)
- Resource-level permissions
- Consent management
- Tier-based authorization

### OPA-B: Behavior Policies

Answer: **"Should this agent's tool use be constrained?"**

```rego
# Example: Rate limiting
deny contains msg if {
    count(input.recent_actions) > 100
    msg := "Rate limit exceeded: max 100 actions per minute"
}
```

**Enforcement Point**: After tool execution

**Use Cases**:
- Rate limiting
- Anomaly detection
- Audit logging
- Workflow enforcement

---

## 📝 Example: Customer Service AI Agent

### Scenario: User Asks for Customer Email

**User Query**: "What is customer Jane Doe's email address?"

**Step 1: AI Agent Analyzes Query**
```python
# AI determines this requires the access_customer_pii tool
tool_call = {
    "tool": "access_customer_pii",
    "parameters": {
        "customer_id": "CUST-001",
        "purpose": "customer_support"
    }
}
```

**Step 2: OPA-A Authorization Check**
```json
{
  "input": {
    "agent": {
      "role": "customer_service",
      "trust_level": 3
    },
    "action": "access_pii",
    "resource": {
      "customer_id": "CUST-001",
      "consent_given": true  // ✓ Consent exists
    }
  }
}
```

**OPA Decision**: ✅ **AUTHORIZED**

**Step 3: Execute Tool**
```python
pii_data = database.get_customer_pii("CUST-001")
# Returns: {email: "jane.doe@example.com", phone: "+1-555-0123"}
```

**Step 4: OPA-B Behavior Check**
```json
{
  "input": {
    "recent_actions": [...],  // 45 actions in last minute
    "action": "access_pii"
  }
}
```

**OPA Decision**: ✅ **ALLOWED** (under rate limit)

**Step 5: AI Response**
```
The email address for customer Jane Doe (CUST-001) is jane.doe@example.com.
Her phone number is +1-555-0123. Is there anything else I can help you with?
```

**Audit Log Entry**:
```json
{
  "timestamp": "2026-05-26T10:30:15Z",
  "agent_id": "ai-cs-001",
  "tool": "access_customer_pii",
  "authorization": "allowed",
  "behavior_check": "passed"
}
```

---

## 🚫 Policy Denial Example

**User Query**: "What is John Smith's email?"

**Step 1**: AI selects `access_customer_pii` tool

**Step 2**: OPA-A Check
```json
{
  "resource": {
    "customer_id": "CUST-002",
    "consent_given": false  // ❌ No consent
  }
}
```

**OPA Decision**: ❌ **DENIED**

```
Policy Violation: Authorization denied
Reason: Customer has not given PII consent
Tool execution prevented
```

**AI Response**: "I'm sorry, but I cannot access that customer's email address because they have not provided consent for PII access. I can help you with other non-sensitive information."

---

## 🛠️ Implementation

### Define AI Agent with Tools

```python
from src.agents.ai_base_agent import AIRetailAgent
from src.common.models import RetailAction, ActionType

class AICustomerServiceAgent(AIRetailAgent):
    def access_customer_pii(self, customer_id, user_query):
        # Create action for policy check
        action = RetailAction(
            action_type=ActionType.ACCESS_PII,
            resource={
                "type": "customer_pii",
                "customer_id": customer_id,
                "consent_given": True  # Retrieved from DB
            }
        )
        
        # Execute with policy enforcement
        # This automatically does OPA-A + OPA-B checks
        result = self.execute_ai_action(
            action=action,
            user_query=user_query,
            context_data={"customer_data": {...}}
        )
        
        return result
```

### Tool Definitions for LLM

```python
tools = [
    {
        "type": "function",
        "function": {
            "name": "access_customer_pii",
            "description": "Access sensitive customer PII. Requires consent.",
            "parameters": {
                "type": "object",
                "properties": {
                    "customer_id": {"type": "string"},
                    "purpose": {"type": "string"}
                }
            }
        }
    }
]
```

### OPA Policy Rules

**Authorization (OPA-A)** - `src/policies/authorization.rego`:
```rego
package retail.authorization

default allow = false

# Customer service can access PII with consent
allow if {
    input.action == "access_pii"
    input.agent.role == "customer_service"
    input.resource.consent_given == true
}
```

**Behavior (OPA-B)** - `src/policies/behavior.rego`:
```rego
package retail.behavior

default allow = true

# Deny if rate limit exceeded
deny contains msg if {
    count(input.recent_actions) > 100
    msg := "Rate limit: max 100 actions/minute"
}

allow if { count(deny) == 0 }
```

---

## 🚀 Quick Start

### 1. Install Dependencies

```bash
# Install uv package manager
pip install uv

# Install project dependencies
uv sync --all-extras
```

### 2. Start OPA Server

```bash
docker-compose up -d
```

### 3. Configure Environment

```bash
cp .env.template .env

# Edit .env with your Azure OpenAI credentials
AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com/
AZURE_OPENAI_API_KEY=your-key-here
MODEL_DEPLOYMENT_NAME=gpt-4o
```

### 4. Run AI Agent Demo

```bash
python scripts/demo_ai_agent.py
```

This will show:
- ✅ Successful tool use with policy authorization
- ❌ Policy denial when consent missing
- 📊 Tool definitions and capabilities
- 📝 Audit trail examples

---

## 📚 Workshop Materials

### Demo Scripts

- `scripts/demo_ai_agent.py` - **Main AI agent demo** (start here!)
- `scripts/demo_customer_service.py` - Customer service scenarios
- `scripts/demo_inventory.py` - Inventory management
- `scripts/demo_order_processing.py` - Order processing & pricing
- `scripts/demo_policy_enforcement.py` - Policy violation examples

### Jupyter Notebooks

1. **01-setup-and-intro.ipynb** - Workshop intro and OPA basics
2. **02-opa-authorization.ipynb** - OPA-A authorization patterns
3. **03-opa-behavior.ipynb** - OPA-B behavior constraints
4. **04-agent-workflows.ipynb** - Multi-agent scenarios
5. **05-policy-violations.ipynb** - Debugging and audit logs
6. **06-foundry-deployment.ipynb** - Deploy to Azure AI Foundry

### Policy Files

- `src/policies/authorization.rego` - OPA-A authorization rules
- `src/policies/behavior.rego` - OPA-B behavior constraints

---

## 🎓 Learning Path

### Beginner

1. Run `python scripts/demo_ai_agent.py` to see the pattern
2. Read `src/agents/ai_customer_service.py` - see tool definitions
3. Review `src/policies/authorization.rego` - understand rules
4. Check `logs/policy-audit.jsonl` - view audit trail

### Intermediate

1. Open `notebooks/01-setup-and-intro.ipynb` in Jupyter
2. Work through notebooks 02-05 sequentially
3. Modify policies in `src/policies/*.rego`
4. Test policy changes with `opa eval` command

### Advanced

1. Create your own AI agent with custom tools
2. Write new OPA policies for your domain
3. Deploy to Azure AI Foundry with notebook 06
4. Integrate with production systems

---

## 🔍 Key Files

| File | Purpose |
|------|---------|
| `src/agents/ai_base_agent.py` | Base AI agent with policy enforcement |
| `src/agents/ai_customer_service.py` | **Example AI agent with tools** |
| `src/common/policy_middleware.py` | Policy enforcement middleware |
| `src/policies/authorization.rego` | OPA-A authorization rules |
| `src/policies/behavior.rego` | OPA-B behavior rules |
| `scripts/demo_ai_agent.py` | **Main demo script** |

---

## 🐛 Debugging

### View Policy Decisions

```bash
# Watch audit log in real-time
tail -f logs/policy-audit.jsonl | jq .
```

### Test Policies Directly

```bash
# Test authorization policy
echo '{
  "input": {
    "agent": {"role": "customer_service"},
    "action": "access_pii",
    "resource": {"consent_given": true}
  }
}' | opa eval -d src/policies/authorization.rego 'data.retail.authorization.allow'
```

### Common Issues

**Q: "Connection error" when calling LLM**
- A: Configure `AZURE_OPENAI_ENDPOINT` in `.env` or run in mock mode

**Q: "Policy violation" when it should allow**
- A: Check `logs/policy-audit.jsonl` for denial reason
- A: Test policy with `opa eval` to see decision

**Q: "OPA server not running"**
- A: Run `docker-compose up -d` to start OPA

---

## 🌟 Production Deployment

Deploy AI agents with policy enforcement to Azure AI Foundry:

1. Build Docker containers with OPA sidecar
2. Configure agent metadata in `.foundry/agent-metadata.yaml`
3. Deploy using `notebooks/06-foundry-deployment.ipynb`
4. Monitor with Application Insights + audit logs

See `.foundry/README.md` for detailed instructions.

---

## 📖 Additional Resources

- [Open Policy Agent Docs](https://www.openpolicyagent.org/docs/latest/)
- [Azure OpenAI Service](https://learn.microsoft.com/azure/ai-services/openai/)
- [Azure AI Foundry](https://learn.microsoft.com/azure/ai-studio/)
- [OPA Policy Testing](https://www.openpolicyagent.org/docs/latest/policy-testing/)

---

## 🤝 Contributing

This is a workshop project for learning policy enforcement patterns. Feel free to:

- Add new agent types with different tools
- Create additional policy rules for your domain
- Share your workshop experiences
- Report issues or suggest improvements

---

## 📜 License

MIT License - See LICENSE file for details

---

## ✨ Summary

**Workshop Lesson**: Policy Enforcement for Business Logic on AI Agents and their Tool Use

**Pattern**:
1. AI Agent analyzes user query
2. AI Agent selects appropriate tool
3. **OPA-A checks authorization** before tool execution
4. Tool executes business logic
5. **OPA-B checks behavior** after execution
6. AI Agent generates natural language response
7. **All decisions audited** for compliance

**Result**: Secure, governed, auditable AI agent systems that respect business policies.
