# =====================================================================
# OPA-B: BEHAVIOR POLICY
#
# Question answered: "Even though this action is authorized, should we
# constrain it based on runtime behavior?"
#
# Examples enforced here:
#   - Rate limiting (max actions per minute)
#   - Block selling below cost / below MAP
#   - Block large transfers without warehouse manager
#   - Block no-receipt refunds above $50
#
# Input contract:
#   input.agent.role
#   input.action.type, input.action.resource, input.action.context
#   input.recent_actions[]  -- {"timestamp_ns", "action", "resource"}
#   input.timestamp
#
# Default: allow=true (behavior policies are CONSTRAINTS, not primary auth).
# =====================================================================

package retail.behavior

import future.keywords.if
import future.keywords.in
import future.keywords.contains

default allow := false

# Allow only when no deny rules fired.
allow if {
    count(deny) == 0
}

# ---------------------------------------------------------------------
# Rate limit: <= 30 actions per 60s window (small for easy demo)
# ---------------------------------------------------------------------
RATE_LIMIT := 30

WINDOW_NS := 60000000000  # 60s in nanoseconds

recent_window_count := n if {
    threshold := time.now_ns() - WINDOW_NS
    n := count([a |
        a := input.recent_actions[_]
        a.timestamp_ns > threshold
    ])
}

deny contains msg if {
    recent_window_count > RATE_LIMIT
    msg := sprintf("Rate limit exceeded: %v actions in last 60s (limit %v)",
                   [recent_window_count, RATE_LIMIT])
}

# ---------------------------------------------------------------------
# Pricing constraints (apply_discount)
# ---------------------------------------------------------------------
deny contains msg if {
    input.action.type == "apply_discount"
    input.action.resource.new_price < input.action.resource.cost
    msg := sprintf("Price $%.2f is below cost $%.2f",
                   [input.action.resource.new_price, input.action.resource.cost])
}

deny contains msg if {
    input.action.type == "apply_discount"
    map_price := input.action.resource.minimum_advertised_price
    map_price != null
    input.action.resource.new_price < map_price
    not input.action.context.special_promotion
    msg := sprintf("Price $%.2f is below MAP $%.2f (no special promotion flag)",
                   [input.action.resource.new_price, map_price])
}

# ---------------------------------------------------------------------
# Inventory transfer constraints
# ---------------------------------------------------------------------
deny contains msg if {
    input.action.type == "transfer"
    input.action.resource.quantity > 1000
    input.agent.role != "warehouse_manager"
    msg := sprintf("Transfer of %v units requires warehouse_manager (role=%v)",
                   [input.action.resource.quantity, input.agent.role])
}

# ---------------------------------------------------------------------
# Refund constraints
# ---------------------------------------------------------------------
deny contains msg if {
    input.action.type == "process_refund"
    input.action.resource.has_receipt == false
    input.action.resource.amount > 50
    msg := "Refunds over $50 require a receipt"
}

# ---------------------------------------------------------------------
# Inventory adjustment: large write-downs require a reason
# ---------------------------------------------------------------------
deny contains msg if {
    input.action.type == "adjust_inventory"
    abs_int(input.action.resource.delta) > 100
    not input.action.context.reason
    msg := sprintf("Adjustment of %v units requires a reason",
                   [abs_int(input.action.resource.delta)])
}

abs_int(x) := x if x >= 0
abs_int(x) := -x if x < 0

# ---------------------------------------------------------------------
# Human-readable reason (single concatenated string)
# ---------------------------------------------------------------------
reason := msg if {
    count(deny) > 0
    msg := concat("; ", [m | m := deny[_]])
}
