# Retail AI Agent Governance Workshop

**Runtime Policy Enforcement for AI Agents with Agent Governance Toolkit (AGT)**

This workshop teaches you how to add runtime governance to AI agents using Microsoft's
[Agent Governance Toolkit (AGT)](https://github.com/microsoft/agent-governance-toolkit).
No Docker, no external server — everything runs in-process with a single pip install.

---

## What You'll Learn

- **AGT-A Authorization**: role-based access control (RBAC) before every tool call
- **AGT-B Behavior**: runtime safety constraints (rate limiting, pricing floors, refund windows)
- How to write YAML governance policies instead of Rego/OPA
- How to integrate governance with Microsoft Agent Framework and Azure AI Foundry

---

## Architecture

```
User / LLM
    │
    ▼
BaseAgent.invoke_tool() / ask()
    │
    ├── AGT-A: authorization.yaml  ← RBAC rules (role + action + resource)
    │       Allow / Deny
    │
    ├── AGT-B: behavior.yaml       ← Safety rules (rate limit, pricing, refunds)
    │       Allow / Deny
    │
    └── Tool method executes  →  Returns result or {"ok": false, "denied_by": ...}
```

Policies are evaluated **in-process** — no HTTP call, no server.
Each evaluation is logged to `logs/governance-audit.jsonl`.

---

## Quick Start

```bash
# 1. Install
pip install agent-governance-toolkit[full] pydantic pydantic-settings pyyaml rich

# 2. (Optional) Configure Azure Foundry for LLM-powered demos
cp .env.template .env
# Edit .env with your FOUNDRY_PROJECT_ENDPOINT

# 3. Run the demo (no Azure needed)
python scripts/demo_ai_agent.py

# 4. Run the tests
pytest tests/ -v

# 5. Verify policies with AGT CLI
agt lint-policy src/policies/
agt verify
```

---

## Agents & Tools (same as govern-with-open-policy)

| Agent | Tools |
|-------|-------|
| CustomerService | `access_customer_pii`, `view_customer_profile`, `update_customer_tier`, `handle_customer_inquiry` |
| Inventory | `check_stock`, `transfer_inventory`, `adjust_inventory` |
| OrderProcessing | `process_order`, `apply_discount`, `lookup_order` |
| Returns | `check_return_eligibility`, `process_refund` |

---

## RBAC Roles

`cashier` · `customer_service` · `warehouse_staff` · `warehouse_manager` · `store_manager` · `regional_manager` · `admin`

---

## Policy Examples

### AGT-A Authorization (src/policies/authorization.yaml)

```yaml
apiVersion: governance.toolkit/v1
name: retail-authorization
default_action: allow
rules:
  - name: block-cashier-pii
    condition: "role == 'cashier' and action == 'access_pii'"
    action: deny
    description: "Cashiers cannot access customer PII"

  - name: require-consent-for-pii
    condition: "action == 'access_pii' and consent_given == False"
    action: deny
    description: "PII access requires customer consent"
```

### AGT-B Behavior (src/policies/behavior.yaml)

```yaml
apiVersion: governance.toolkit/v1
name: retail-behavior
default_action: allow
rules:
  - name: block-below-cost-price
    condition: "new_price < cost and action == 'apply_discount'"
    action: deny
    description: "Price cannot be set below cost"

  - name: block-late-refund
    condition: "days_since_purchase > 30 and action == 'process_refund'"
    action: deny
    description: "Refunds not accepted after 30 days"
```

---

## AGT vs OPA Comparison

| Feature | OPA (govern-with-open-policy) | AGT (this workshop) |
|---------|-------------------------------|---------------------|
| Policy language | Rego (Datalog-like) | YAML + expressions |
| Runtime | External OPA server (Docker) | In-process library |
| Install | `docker pull openpolicyagent/opa` | `pip install agent-governance-toolkit[full]` |
| Latency per decision | ~5–15 ms (HTTP round-trip) | < 1 ms (in-memory) |
| Audit log | JSON lines via OPA | JSON lines via AGT |
| CLI tools | `opa eval`, `opa test` | `agt doctor`, `agt lint-policy`, `agt verify` |
| Standalone workshop | ❌ Requires Docker | ✅ pip only |

---

## Notebooks

| # | Notebook | Topic |
|---|----------|-------|
| 01 | setup-and-intro | Install, verify, AGT-A vs AGT-B concepts |
| 02 | agt-authorization | Deep dive: RBAC, consent, role caps |
| 03 | agt-behavior | Deep dive: rate limit, pricing, refunds |
| 04 | natural-language-agents | LLM-powered agents via Microsoft Agent Framework |
| 05 | policy-violations | Debugging: audit log, `agt lint-policy`, `agt verify` |
| 06 | foundry-deployment | Deploy to Azure AI Foundry |

---

## Links

- [Agent Governance Toolkit](https://github.com/microsoft/agent-governance-toolkit)
- [Microsoft Agent Framework](https://github.com/microsoft/agent-framework)
- [Azure AI Foundry](https://ai.azure.com)
- [govern-with-open-policy](../govern-with-open-policy/) — the OPA-based version of this workshop
