# =====================================================================
# OPA-A: AUTHORIZATION POLICY
#
# Question answered: "Can this agent perform this action on this resource?"
# Pattern: role-based access control (RBAC) + resource-attribute checks.
#
# Input contract (built in src/policy.py PolicyEnforcer.enforce):
#   input.agent.role               e.g. "customer_service"
#   input.agent.agent_id, ...
#   input.action                   e.g. "access_pii"
#   input.resource.type            e.g. "customer_pii"
#   input.resource.<attrs...>      action-specific attributes
#   input.context.<attrs...>       optional extra context
#
# Output:
#   allow  : bool   -- fail-closed default false
#   reason : string -- only set when not allowed (helps debugging)
# =====================================================================

package retail.authorization

import future.keywords.if
import future.keywords.in

default allow := false

# ---------------------------------------------------------------------
# Admin override (useful for tests; do NOT use in production)
# ---------------------------------------------------------------------
allow if {
    input.agent.role == "admin"
}

# ---------------------------------------------------------------------
# Customer Service tools
# ---------------------------------------------------------------------

# PII access requires customer-service role AND customer consent.
allow if {
    input.action == "access_pii"
    input.resource.type == "customer_pii"
    input.agent.role == "customer_service"
    input.resource.consent_given == true
}

# Reading a basic profile is allowed for all customer-facing roles.
allow if {
    input.action == "read"
    input.resource.type == "customer_profile"
    input.agent.role in ["customer_service", "cashier", "store_manager"]
}

# Only customer_service or store_manager can change a customer's loyalty tier.
allow if {
    input.action == "update"
    input.resource.type == "customer_tier"
    input.agent.role in ["customer_service", "store_manager"]
}

# Anyone customer-facing can handle a generic inquiry.
allow if {
    input.action == "query"
    input.resource.type == "customer_inquiry"
    input.agent.role in ["customer_service", "cashier", "store_manager"]
}

# ---------------------------------------------------------------------
# Inventory tools
# ---------------------------------------------------------------------

# Reading inventory: all warehouse + store roles.
allow if {
    input.action == "read"
    input.resource.type == "inventory"
    input.agent.role in [
        "warehouse_staff", "warehouse_manager",
        "store_manager", "cashier",
    ]
}

# Warehouse staff can only transfer FROM their own location.
allow if {
    input.action == "transfer"
    input.resource.type == "inventory"
    input.agent.role == "warehouse_staff"
    input.agent.location == input.resource.location
}

# Warehouse managers can transfer between any locations.
allow if {
    input.action == "transfer"
    input.resource.type == "inventory"
    input.agent.role == "warehouse_manager"
}

# Adjustments (write) require warehouse_manager or store_manager.
allow if {
    input.action == "adjust_inventory"
    input.resource.type == "inventory"
    input.agent.role in ["warehouse_manager", "store_manager"]
}

# ---------------------------------------------------------------------
# Order Processing tools
# ---------------------------------------------------------------------

# Cashiers can process orders up to $500.
allow if {
    input.action == "process_order"
    input.resource.type == "transaction"
    input.agent.role == "cashier"
    input.resource.amount <= 500
}

# Store managers can process orders up to $5,000.
allow if {
    input.action == "process_order"
    input.resource.type == "transaction"
    input.agent.role == "store_manager"
    input.resource.amount <= 5000
}

# Regional managers can process anything (still subject to OPA-B).
allow if {
    input.action == "process_order"
    input.resource.type == "transaction"
    input.agent.role == "regional_manager"
}

# Cashiers may apply discounts up to 10%.
allow if {
    input.action == "apply_discount"
    input.resource.type == "price"
    input.agent.role == "cashier"
    discount_pct <= 10
}

# Store managers may apply discounts up to 25%.
allow if {
    input.action == "apply_discount"
    input.resource.type == "price"
    input.agent.role == "store_manager"
    discount_pct <= 25
}

# Reading an order is allowed for customer_service, cashier and managers.
allow if {
    input.action == "read"
    input.resource.type == "order"
    input.agent.role in ["customer_service", "cashier", "store_manager"]
}

# ---------------------------------------------------------------------
# Returns / Refunds tools
# ---------------------------------------------------------------------

# Cashier: refunds up to $100, only within 30 days.
allow if {
    input.action == "process_refund"
    input.resource.type == "refund"
    input.agent.role == "cashier"
    input.resource.amount <= 100
    input.resource.days_since_purchase <= 30
}

# Store manager: refunds up to $1,000 with a receipt.
allow if {
    input.action == "process_refund"
    input.resource.type == "refund"
    input.agent.role == "store_manager"
    input.resource.amount <= 1000
    input.resource.has_receipt == true
}

# ---------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------

discount_pct := pct if {
    orig := input.resource.original_price
    new := input.resource.new_price
    orig > 0
    pct := ((orig - new) / orig) * 100
}

# ---------------------------------------------------------------------
# Human-readable denial reason (best-effort)
# ---------------------------------------------------------------------
reason := msg if {
    not allow
    input.action == "access_pii"
    input.resource.consent_given == false
    msg := "PII access denied: customer has not given consent"
} else := msg if {
    not allow
    input.action == "access_pii"
    msg := sprintf("PII access denied: role '%v' is not authorized to access PII", [input.agent.role])
} else := msg if {
    not allow
    input.action == "process_order"
    msg := sprintf("Order denied: amount $%.2f exceeds limit for role '%v'", [input.resource.amount, input.agent.role])
} else := msg if {
    not allow
    input.action == "apply_discount"
    msg := sprintf("Discount denied: %.1f%% exceeds limit for role '%v'", [discount_pct, input.agent.role])
} else := msg if {
    not allow
    input.action == "process_refund"
    msg := sprintf("Refund denied: $%.2f for role '%v' (days=%v, receipt=%v)",
                   [input.resource.amount, input.agent.role,
                    input.resource.days_since_purchase, input.resource.has_receipt])
} else := msg if {
    not allow
    input.action == "transfer"
    msg := sprintf("Inventory transfer denied for role '%v' at location '%v'",
                   [input.agent.role, input.agent.location])
} else := msg if {
    not allow
    msg := sprintf("Action '%v' on resource '%v' denied for role '%v'",
                   [input.action, input.resource.type, input.agent.role])
}
