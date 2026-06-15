# OPA Policy Documentation
# This directory contains Rego policies for retail agent governance

## Policy Organization

### authorization.rego (OPA-A)
Role-based access control (RBAC) policies that answer: "Can this agent perform this action?"

Key policies:
- PII access control (customer_service, compliance_officer only)
- Inventory access control (read/write permissions by role)
- Pricing authorization (tiered discount limits by role)
- Transaction limits (amount thresholds by role)
- Refund authorization (amount and timeframe constraints)

### behavior.rego (OPA-B)
Behavioral constraint policies that answer: "Should this agent's behavior be constrained?"

Key constraints:
- Rate limiting (max 100 actions per minute)
- Bulk data access controls (>10K records requires approval)
- Pricing constraints (>20% change requires approval)
- Inventory transfer limits (>1000 units requires manager)
- Transaction velocity checks (unusual patterns)
- Refund constraints (without receipt limited to $50)

## Testing Policies

Use the OPA CLI to test policies:

```bash
# Test authorization policy
opa eval -d src/policies/authorization.rego -i test_input.json "data.retail.authorization.allow"

# Test behavior policy
opa eval -d src/policies/behavior.rego -i test_input.json "data.retail.behavior.allow"
```

## Loading Policies

Policies are automatically loaded into OPA server via docker-compose volume mount:
- Source: `./src/policies`
- Mount: `/policies` in container

OPA server watches for changes and reloads policies automatically.
