# OPA Policy Enforcement vs. Agent Governance Toolkit

## Overview

This document compares two approaches to policy enforcement in AI agent applications:

1. **OPA (Open Policy Agent) with Microsoft Agent Framework Middlewares** (this workshop)
2. **Azure AI Agent Governance Toolkit**

Both solutions provide governance and policy enforcement for AI agents, but with different architectural approaches and capabilities.

---

## Quick Comparison

| Aspect | OPA + Agent Framework | Agent Governance Toolkit |
|--------|----------------------|--------------------------|
| **Architecture** | Middleware-based, external policy engine | Integrated policy framework |
| **Policy Language** | Rego (declarative) | Python/Configuration-based |
| **Enforcement Point** | Agent tool execution layer | Agent invocation layer |
| **Deployment Model** | Sidecar/external service | SDK/library integration |
| **Policy Updates** | Hot-reload, no code changes | May require deployment |
| **Authorization Focus** | OPA-A: Role-based, resource-level | Built-in RBAC and permissions |
| **Behavior Constraints** | OPA-B: Rate limiting, workflows | Built-in guardrails and controls |
| **Audit Trail** | Custom logging to JSONL | Integrated telemetry |
| **Multi-Agent Support** | Policy-per-agent or shared | Centralized governance |
| **Learning Curve** | Moderate (Rego + middleware) | Low (Python-native) |
| **Flexibility** | High (custom policies) | Moderate (predefined patterns) |
| **Production Readiness** | Enterprise-grade (OPA) | Azure-native integration |

---

## Architectural Comparison

### OPA + Microsoft Agent Framework (This Workshop)

```
┌─────────────────────────────────────────┐
│         User / Application              │
└───────────────┬─────────────────────────┘
                │
┌───────────────▼─────────────────────────┐
│         AI Agent (LLM)                  │
│  - Natural language understanding       │
│  - Tool selection via function calling  │
└───────────────┬─────────────────────────┘
                │
┌───────────────▼─────────────────────────┐
│   Microsoft Agent Framework Middleware  │
│   - PolicyEnforcementMiddleware         │
│   - Pre-execution: OPA-A check          │
│   - Post-execution: OPA-B check         │
│   - Audit logging                       │
└───────────┬───────────┬─────────────────┘
            │           │
            │   ┌───────▼─────────┐
            │   │  OPA Server     │
            │   │  (External)     │
            │   │  - Rego policies│
            │   │  - Declarative  │
            │   │  - Hot-reload   │
            │   └─────────────────┘
            │
┌───────────▼─────────────────────────────┐
│      Business Logic / Tools             │
│  - access_pii(), update_inventory()     │
│  - Actual operations after auth         │
└─────────────────────────────────────────┘
```

**Key Characteristics:**
- **External Policy Engine**: OPA runs as separate service (sidecar pattern)
- **Declarative Policies**: Rego language for complex authorization logic
- **Middleware Pattern**: Transparent enforcement without modifying business logic
- **Tool-Level Enforcement**: Policies evaluated at every tool execution
- **Flexible Policy Logic**: Full control over authorization and behavior rules

### Agent Governance Toolkit

```
┌─────────────────────────────────────────┐
│         User / Application              │
└───────────────┬─────────────────────────┘
                │
┌───────────────▼─────────────────────────┐
│   Agent Governance SDK / Framework      │
│   ┌─────────────────────────────────┐   │
│   │  Policy Engine (Integrated)     │   │
│   │  - RBAC enforcement             │   │
│   │  - Content filtering            │   │
│   │  - Rate limiting                │   │
│   │  - Prompt injection detection   │   │
│   └─────────────────────────────────┘   │
│   ┌─────────────────────────────────┐   │
│   │  AI Agent                       │   │
│   │  - LLM invocation               │   │
│   │  - Tool execution               │   │
│   │  - Governed by framework        │   │
│   └─────────────────────────────────┘   │
│   ┌─────────────────────────────────┐   │
│   │  Telemetry & Monitoring         │   │
│   │  - Azure Monitor integration    │   │
│   │  - Built-in audit logs          │   │
│   └─────────────────────────────────┘   │
└─────────────────────────────────────────┘
```

**Key Characteristics:**
- **Integrated Framework**: Policy engine built into agent SDK
- **Python-Native**: Configuration and policies in Python
- **Azure Integration**: First-class support for Azure services
- **Agent-Level Enforcement**: Policies applied at agent invocation
- **Pre-built Guardrails**: Common patterns included out-of-box

---

## Feature Comparison

### 1. Authorization (OPA-A vs. RBAC)

#### OPA Approach (OPA-A)
```rego
# Fine-grained, custom authorization logic
package retail.authorization

default allow = false

# Customer service can access PII with consent
allow if {
    input.agent.role == "customer_service"
    input.action == "access_pii"
    input.resource.consent_given == true
}

# Store managers can access without consent
allow if {
    input.agent.role == "store_manager"
    input.action == "access_pii"
}

# Tiered discount limits
allow if {
    input.action == "apply_discount"
    discount_within_tier_limit(
        input.agent.role,
        input.resource.discount_percent
    )
}
```

**Advantages:**
- Extremely flexible policy logic
- Complex conditions with business rules
- Easy to version and test policies
- No code changes for policy updates

#### Agent Governance Toolkit Approach
```python
# RBAC configuration
from azure.ai.governance import AgentPolicy, Role

policy = AgentPolicy(
    roles=[
        Role(
            name="customer_service",
            permissions=[
                "read:customer_pii",
                "update:customer_profile"
            ]
        ),
        Role(
            name="store_manager",
            permissions=["*:customer_pii"]  # Full access
        )
    ],
    content_filters=["pii", "financial"],
    rate_limits={"max_requests_per_minute": 100}
)
```

**Advantages:**
- Familiar RBAC patterns
- Python-native (no new language)
- Built-in content safety filters
- Azure-integrated authentication

### 2. Behavior Constraints (OPA-B vs. Guardrails)

#### OPA Approach (OPA-B)
```rego
package retail.behavior

default allow = true

# Rate limiting
deny contains msg if {
    count(input.recent_actions) > 100
    msg := "Rate limit exceeded: max 100 actions per minute"
}

# Bulk access constraints
deny contains msg if {
    input.action == "bulk_access_pii"
    count(input.resource.customer_ids) > 50
    not input.agent.role == "compliance_officer"
    msg := "Bulk PII access limited to 50 customers without compliance approval"
}

# Workflow enforcement
deny contains msg if {
    input.action == "issue_refund"
    input.resource.amount > 500
    not has_manager_approval(input.resource.transaction_id)
    msg := "Refunds over $500 require manager approval"
}
```

#### Agent Governance Toolkit Approach
```python
from azure.ai.governance import Guardrails, RateLimit, WorkflowPolicy

guardrails = Guardrails(
    rate_limit=RateLimit(
        max_requests=100,
        time_window="1m"
    ),
    content_policies=[
        ContentPolicy(
            name="bulk_pii_limit",
            max_records=50,
            requires_approval=True
        )
    ],
    workflow_policies=[
        WorkflowPolicy(
            action="issue_refund",
            threshold=500,
            requires_approval_from=["store_manager"]
        )
    ]
)
```

### 3. Audit and Compliance

#### OPA Approach
```python
# Custom audit logging
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
- Written to custom JSONL log
- Full control over audit format
- Can integrate with any SIEM

#### Agent Governance Toolkit Approach
```python
# Azure Monitor integration
from azure.monitor import AuditLogger

# Automatic telemetry
# - All agent invocations
# - Policy decisions
# - Performance metrics
# Sent to Azure Monitor / Application Insights
```
- Native Azure Monitor integration
- Structured telemetry format
- Built-in dashboards and alerts

---

## When to Use Each Approach

### Use OPA + Microsoft Agent Framework When:

✅ **You need maximum policy flexibility**
- Complex business rules requiring custom logic
- Policies that evolve frequently and independently
- Fine-grained authorization at tool/operation level

✅ **You want policy-as-code separation**
- Policy updates without agent redeployment
- Version control and testing for policies separately
- Multiple teams managing policies vs. agent code

✅ **You're building multi-cloud or hybrid systems**
- OPA is cloud-agnostic and widely adopted
- Can enforce policies across different runtimes
- Consistent governance across platforms

✅ **You have or want to build OPA expertise**
- Organization already uses OPA for other services
- Rego skills exist or can be developed
- Value of declarative policy language outweighs learning curve

### Use Agent Governance Toolkit When:

✅ **You want Azure-native integration**
- Leveraging Azure AI services extensively
- Need built-in Azure Monitor telemetry
- Want seamless Entra ID integration

✅ **You prefer Python-native governance**
- Team is Python-focused, prefer no new languages
- Want policies defined alongside agent code
- Configuration-over-code approach is sufficient

✅ **You need quick time-to-value**
- Pre-built governance patterns cover your needs
- Want out-of-box content safety and rate limiting
- Don't need highly custom authorization logic

✅ **You're using Azure AI Foundry**
- Native integration with Foundry platform
- Built-in support for agent deployment
- Centralized governance dashboard

---

## Hybrid Approach

Both approaches can be combined:

```python
# Use Agent Governance Toolkit for basic controls
from azure.ai.governance import Guardrails

guardrails = Guardrails(
    rate_limit=RateLimit(max_requests=100, time_window="1m"),
    content_filters=["pii", "financial"]
)

# Add OPA for complex authorization
from src.common.policy_middleware import PolicyEnforcementMiddleware

middleware = PolicyEnforcementMiddleware(
    opa_url="http://localhost:8181"
)

# Apply both layers
agent = MyAgent(
    guardrails=guardrails,        # Azure-native controls
    policy_middleware=middleware   # Custom OPA policies
)
```

**Benefits:**
- Azure-native telemetry and monitoring
- Custom authorization logic where needed
- Best of both worlds

---

## Conclusion

| Criteria | Recommendation |
|----------|----------------|
| **Maximum flexibility** | OPA + Agent Framework |
| **Azure-first strategy** | Agent Governance Toolkit |
| **Complex business rules** | OPA + Agent Framework |
| **Quick implementation** | Agent Governance Toolkit |
| **Multi-cloud/hybrid** | OPA + Agent Framework |
| **Python-only teams** | Agent Governance Toolkit |
| **Custom audit requirements** | OPA + Agent Framework |
| **Built-in dashboards** | Agent Governance Toolkit |

**This Workshop Focus**: We demonstrate the **OPA + Microsoft Agent Framework** approach because it provides:
1. Deep understanding of policy enforcement mechanics
2. Maximum flexibility for custom business rules  
3. Separation of concerns between policies and code
4. Skills transferable across different platforms
5. Fine-grained control at the tool execution layer

The patterns learned here can be applied with either approach, or combined for comprehensive governance.

---

## Further Reading

- [Open Policy Agent Documentation](https://www.openpolicyagent.org/docs/latest/)
- [Microsoft Agent Framework](https://learn.microsoft.com/azure/ai-services/agents/)
- [Azure AI Foundry Agent Governance](https://learn.microsoft.com/azure/ai-services/foundry/governance)
- [Rego Policy Language](https://www.openpolicyagent.org/docs/latest/policy-language/)
