# AGT Policy Files

This directory contains the two YAML governance policy files used by the workshop.

## authorization.yaml (AGT-A)

Role-based access control (RBAC) rules that run **before** every tool call:

- Cashiers blocked from PII access, tier updates, inventory transfers/adjustments
- Cashiers capped at $500 orders, 10% discounts, $100 refunds
- Warehouse staff blocked from transferring more than 100 units without a manager

## behavior.yaml (AGT-B)

Runtime behaviour constraints evaluated **after** AGT-A passes:

- Rate limiting (max 100 actions per window)
- Large transfers (>500 units) require manager role
- Pricing cannot drop below cost or below MAP without approval
- Refunds rejected after 30 days or without receipt (if >$50)

## Key Differences from OPA/Rego

| OPA (Rego)                       | AGT (YAML)                             |
|----------------------------------|----------------------------------------|
| `.rego` files compiled server-side | `.yaml` files evaluated in-process     |
| Requires Docker/OPA server       | `pip install agent-governance-toolkit` |
| Datalog-like policy language     | Simple Python-like expressions         |
| Remote HTTP call per decision    | In-memory evaluation (<1 ms)           |
