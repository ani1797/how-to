"""Architecture documentation for the workshop."""

# Retail AI Agent Policy Workshop - Architecture

## System Architecture

### Overview

The workshop demonstrates a **policy-enforced multi-agent system** for retail operations using the **OPA (Open Policy Agent)** framework. The architecture separates **business logic** (agents) from **policy logic** (OPA), enabling centralized governance and flexible policy updates without code changes.

```
┌────────────────────────────────────────────────────────────────┐
│                      Application Layer                          │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐         │
│  │   Jupyter    │  │  CLI Scripts │  │  Foundry     │         │
│  │  Notebooks   │  │   (Demo)     │  │  Deployment  │         │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘         │
│         │                 │                  │                  │
└─────────┼─────────────────┼──────────────────┼──────────────────┘
          │                 │                  │
┌─────────▼─────────────────▼──────────────────▼──────────────────┐
│                        Agent Layer                               │
│  ┌────────────────┐ ┌────────────────┐ ┌────────────────┐      │
│  │   Customer     │ │    Inventory   │ │     Order      │  ... │
│  │   Service      │ │   Management   │ │   Processing   │      │
│  │                │ │                │ │                │      │
│  │ • PII access   │ │ • Stock query  │ │ • Pricing      │      │
│  │ • Tier update  │ │ • Transfers    │ │ • Discounts    │      │
│  │ • Inquiries    │ │ • Reorders     │ │ • Tx limits    │      │
│  └────────┬───────┘ └────────┬───────┘ └────────┬───────┘      │
│           │                  │                  │               │
│           └──────────────────┴──────────────────┘               │
│                              │                                  │
└──────────────────────────────┼──────────────────────────────────┘
                               │
┌──────────────────────────────▼──────────────────────────────────┐
│                  Policy Enforcement Layer                        │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │          PolicyEnforcementMiddleware                      │  │
│  │                                                            │  │
│  │  • enforce_authorization()    ← OPA-A checks             │  │
│  │  • enforce_behavior()         ← OPA-B checks             │  │
│  │  • enforce_combined()         ← Both checks              │  │
│  │  • Audit logging             ← All decisions logged      │  │
│  └──────────────────────┬───────────────────────────────────┘  │
│                         │                                       │
└─────────────────────────┼───────────────────────────────────────┘
                          │
┌─────────────────────────▼───────────────────────────────────────┐
│                      OPA Client Layer                            │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │                   OPAClient                               │  │
│  │                                                            │  │
│  │  • evaluate_policy()          ← POST to OPA              │  │
│  │  • health_check()             ← OPA availability         │  │
│  │  • update_policy()            ← Dynamic policy updates   │  │
│  │  • REST API integration       ← HTTP requests           │  │
│  └──────────────────────┬───────────────────────────────────┘  │
└─────────────────────────┼───────────────────────────────────────┘
                          │
                    HTTP (JSON)
                          │
┌─────────────────────────▼───────────────────────────────────────┐
│                   Open Policy Agent (OPA)                        │
│                   Docker Container: Port 8181                    │
│  ┌────────────────────────────┬────────────────────────────┐   │
│  │    OPA-A (Authorization)   │   OPA-B (Behavior)         │   │
│  │  retail/authorization      │   retail/behavior          │   │
│  │                             │                            │   │
│  │  • RBAC rules              │   • Rate limiting          │   │
│  │  • Resource permissions    │   • Workflow constraints   │   │
│  │  • Role-based access       │   • Anomaly detection      │   │
│  │  • Tiered authorization    │   • Volume limits          │   │
│  │                             │                            │   │
│  │  Rego Policy Files:        │   Rego Policy Files:       │   │
│  │  authorization.rego        │   behavior.rego            │   │
│  └────────────────────────────┴────────────────────────────┘   │
│                                                                  │
│  Policy Volume Mount: /policies ← ./src/policies (auto-reload) │
└──────────────────────────────────────────────────────────────────┘
```

## Component Details

### 1. Agent Layer

The workshop includes TWO types of agents:

#### A. **AI Agents** (Main Workshop Focus)

**Base Class**: `AIRetailAgent` (in `ai_base_agent.py`)
- **LLM-powered** using Azure OpenAI
- Demonstrates **tool use** with policy enforcement
- Tools = business functions (access_pii, update_inventory, etc.)
- Policy enforcement at tool execution layer
- Implements `execute_ai_action()` with automatic policy checks
- Generates natural language responses

**Example**: `AICustomerServiceAgent` (in `ai_customer_service.py`)
- Uses OpenAI function calling for tool selection
- Each tool wrapped with OPA-A (authorization) and OPA-B (behavior) checks
- Tools: `access_customer_pii`, `view_customer_profile`, `update_customer_tier`, `handle_customer_inquiry`

**Key Pattern**:
```
User Query → AI analyzes → Selects tool → OPA-A check → Execute tool → OPA-B check → Response
```

#### B. **Pattern Demo Agents** (Learning Support)

**Base Class**: `BaseRetailAgent` (in `base_agent.py`)
- Simpler agents without AI complexity
- Good for understanding policy mechanics
- Direct business logic execution (no LLM)
- Same policy enforcement patterns

**Concrete Agents:**
1. **CustomerServiceAgent** - PII access patterns
2. **InventoryManagementAgent** - RBAC patterns
3. **OrderProcessingAgent** - Transaction limit patterns
4. **ReturnsRefundAgent** - Approval workflow patterns

**Both agent types:**
- Use the same `PolicyEnforcementMiddleware`
- Enforce identical OPA policies
- Track actions for behavior analysis
- Generate audit logs
- Define specific capabilities
- Use `RetailAction` for all operations
- Automatically enforce policies via middleware

### 2. Policy Enforcement Layer

**PolicyEnforcementMiddleware**

Responsibilities:
- Evaluate actions against OPA policies
- Track policy decisions for audit
- Handle policy violations gracefully
- Support both OPA-A and OPA-B checks

Policy Types:
- **OPA-A (Authorization)**: "Can this agent do this?"
  - Role-based access control
  - Resource-level permissions
  - Identity-based decisions
  
- **OPA-B (Behavior)**: "Should we constrain this?"
  - Rate limiting
  - Volume controls
  - Workflow enforcement
  - Anomaly detection

### 3. OPA Client Layer

**OPAClient**

Features:
- REST API integration with OPA server
- Health check monitoring
- Policy evaluation with timeout handling
- Error handling and retry logic
- Response parsing to `PolicyDecision` objects

Communication:
- Protocol: HTTP/REST
- Format: JSON
- Endpoint: `/v1/data/{policy_path}`
- Input: `{"input": {...}}`
- Output: `{"result": {"allow": bool, "reason": str}}`

### 4. OPA Server

**Open Policy Agent Container**

Configuration:
- Port: 8181
- Volume: `./src/policies:/policies:ro` (read-only mount)
- Auto-reload: Policies reload on file changes
- Health: `/health` endpoint
- Data API: `/v1/data/*`

Policy Structure:
```
/policies/
├── authorization.rego  # OPA-A: RBAC policies
└── behavior.rego       # OPA-B: Constraint policies
```

## Data Flow

### Policy Evaluation Flow

```
1. Agent receives request
   └─→ Create RetailAction(action_type, resource, context)

2. Agent calls execute_action(action)
   └─→ PolicyEnforcementMiddleware.enforce_combined()

3. Middleware evaluates OPA-A (Authorization)
   └─→ OPAClient.evaluate_policy("retail/authorization/allow", input_data)
       └─→ HTTP POST to OPA server
           └─→ OPA evaluates authorization.rego
               ├─→ allow = true  → Continue
               └─→ allow = false → PolicyViolationError

4. Middleware evaluates OPA-B (Behavior)
   └─→ OPAClient.evaluate_policy("retail/behavior/validate", input_data)
       └─→ HTTP POST to OPA server
           └─→ OPA evaluates behavior.rego
               ├─→ allow = true  → Continue
               └─→ allow = false → PolicyViolationError

5. Both checks pass
   └─→ Agent._execute_action_impl(action)  # Business logic
       └─→ Track action in recent_actions
           └─→ Return result

6. Log policy decision to audit log
   └─→ logs/policy-audit.jsonl
```

### Audit Trail

Every policy evaluation creates an audit entry:

```json
{
  "timestamp": "2026-05-26T10:30:00.123Z",
  "agent_id": "cs-agent-001",
  "action": "retail/authorization/allow",
  "policy_path": "retail/authorization/allow",
  "decision": {
    "allow": true,
    "reason": null,
    "metadata": {}
  },
  "input_data": {
    "agent": {"role": "customer_service", ...},
    "action": "access_pii",
    "resource": {...}
  },
  "duration_ms": 12.5
}
```

## Policy Architecture

### OPA-A: Authorization Policies

**Package:** `retail.authorization`

**Strategy:** Fail-closed (default deny)

**Policy Structure:**
```rego
default allow = false

allow if {
    # Condition 1: Role matches
    # Condition 2: Resource requirements met
    # Condition 3: Context validates
}

reason := "explanation" if { not allow }
```

**Key Policies:**
- PII access requires role + consent
- Inventory write requires manager role
- Pricing updates tiered by role (10%/15%/25%/50%)
- Transaction limits by role ($500/$5K/$50K)
- Refund authorization by amount and role

### OPA-B: Behavior Policies

**Package:** `retail.behavior`

**Strategy:** Fail-open with constraints (default allow)

**Policy Structure:**
```rego
default allow = true

deny contains msg if {
    # Constraint violated
    msg := "Explanation of violation"
}

allow if { count(deny) == 0 }
```

**Key Constraints:**
- Rate limiting (100 actions/minute)
- Bulk access (>10K records requires approval)
- Large transfers (>1000 units requires manager)
- Price constraints (>20% change requires approval)
- Transaction velocity checks

## Deployment Architecture

### Local Development

```
┌────────────────────────────────────┐
│  Developer Workstation             │
│                                    │
│  ┌──────────────────────────────┐ │
│  │  VS Code / Jupyter          │ │
│  │  Python 3.11+ with uv       │ │
│  └───────────┬──────────────────┘ │
│              │                    │
│  ┌───────────▼──────────────────┐ │
│  │  Agent Code (src/)          │ │
│  │  • Runs locally             │ │
│  │  • Mock data enabled        │ │
│  └───────────┬──────────────────┘ │
│              │                    │
└──────────────┼────────────────────┘
               │
    Docker Bridge Network
               │
┌──────────────▼────────────────────┐
│  Docker Container                 │
│  ┌────────────────────────────┐  │
│  │  OPA Server                │  │
│  │  Port: 8181                │  │
│  │  Volume: ./src/policies    │  │
│  └────────────────────────────┘  │
└───────────────────────────────────┘
```

### Microsoft Foundry Deployment

```
┌────────────────────────────────────────────────────────────┐
│  Azure AI Foundry                                          │
│                                                            │
│  ┌──────────────────────────────────────────────────────┐ │
│  │  Hosted Agent Deployments                            │ │
│  │                                                        │ │
│  │  ┌───────────────┐  ┌───────────────┐               │ │
│  │  │  Agent Pod 1  │  │  Agent Pod 2  │   ...         │ │
│  │  │               │  │               │               │ │
│  │  │  ┌─────────┐  │  │  ┌─────────┐  │               │ │
│  │  │  │ Agent   │  │  │  │ Agent   │  │               │ │
│  │  │  │ Code    │  │  │  │ Code    │  │               │ │
│  │  │  └────┬────┘  │  │  └────┬────┘  │               │ │
│  │  │       │       │  │       │       │               │ │
│  │  │  ┌────▼────┐  │  │  ┌────▼────┐  │               │ │
│  │  │  │  OPA    │  │  │  │  OPA    │  │               │ │
│  │  │  │ Sidecar │  │  │  │ Sidecar │  │               │ │
│  │  │  └─────────┘  │  │  └─────────┘  │               │ │
│  │  └───────────────┘  └───────────────┘               │ │
│  │                                                        │ │
│  └──────────────────────────────────────────────────────┘ │
│                                                            │
│  ┌──────────────────────────────────────────────────────┐ │
│  │  Azure OpenAI / Foundry Model                        │ │
│  │  (gpt-4o, gpt-4o-mini, etc.)                         │ │
│  └──────────────────────────────────────────────────────┘ │
│                                                            │
└────────────────────────────────────────────────────────────┘
```

**OPA Sidecar Pattern:**
- Each agent container includes OPA sidecar
- Policies bundled in container image
- Local policy evaluation (low latency)
- Shared policy updates via CI/CD

## Security Considerations

### Policy Security

1. **Fail-Closed Authorization**: OPA-A defaults to deny
2. **Policy Version Control**: All policies in Git
3. **Audit Logging**: All decisions logged for compliance
4. **Role Separation**: Agents have minimal required permissions

### Data Security

1. **PII Protection**: Explicit consent checks in policies
2. **Data Minimization**: Agents only access needed data
3. **Audit Trail**: Complete history of data access
4. **Secure Communication**: HTTPS for Foundry deployments

### Operational Security

1. **Policy Testing**: Automated tests for all policies
2. **Change Management**: Policy updates reviewed and tested
3. **Monitoring**: Policy decision metrics and alerts
4. **Incident Response**: Audit logs for forensics

## Performance Characteristics

### Latency

- Policy evaluation: 5-20ms (local OPA)
- Network round-trip: +2-5ms (OPA server)
- Total overhead: 10-30ms per action

### Scalability

- OPA is stateless (horizontally scalable)
- Agents are independent (parallel execution)
- Policy caching possible (partial evaluation)

### Throughput

- OPA: 10,000+ evaluations/sec per instance
- Agent throughput: Limited by business logic, not policies

## Extension Points

### Adding New Agents

1. Extend `BaseRetailAgent`
2. Define role and capabilities
3. Implement `_execute_action_impl()`
4. No policy changes needed (uses existing rules)

### Adding New Policies

1. Edit `authorization.rego` or `behavior.rego`
2. Add policy rules following existing patterns
3. OPA auto-reloads (volume mount)
4. Test with `opa eval`

### Custom Policy Packages

Create new Rego packages:
- `retail.compliance` - Regulatory checks
- `retail.fraud` - Fraud detection
- `retail.scheduling` - Workflow orchestration

Update middleware to evaluate additional packages.

## Monitoring and Observability

### Metrics

- Policy evaluation latency
- Policy decision distribution (allow/deny)
- Agent action rates
- Policy violation rates

### Logs

- Audit logs: `logs/policy-audit.jsonl`
- OPA logs: Docker container logs
- Agent logs: Application logs

### Alerting

- High violation rates
- Policy evaluation failures
- OPA server downtime
- Unusual agent behavior patterns

---

For implementation details, see source code in `src/` directory.
For usage examples, see Jupyter notebooks in `notebooks/`.
