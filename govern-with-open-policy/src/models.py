"""Domain models shared across agents, policies, and the OPA client."""

from datetime import datetime
from enum import Enum
from typing import Any, Dict, Optional

from pydantic import BaseModel, Field

# ---------------------------------------------------------------------------
# Enums
# ---------------------------------------------------------------------------


class AgentRole(str, Enum):
    """RBAC roles used by OPA-A policies."""

    CASHIER = "cashier"
    CUSTOMER_SERVICE = "customer_service"
    WAREHOUSE_STAFF = "warehouse_staff"
    WAREHOUSE_MANAGER = "warehouse_manager"
    STORE_MANAGER = "store_manager"
    REGIONAL_MANAGER = "regional_manager"
    ADMIN = "admin"


class CustomerTier(str, Enum):
    REGULAR = "regular"
    SILVER = "silver"
    GOLD = "gold"
    PLATINUM = "platinum"


class ActionType(str, Enum):
    """Action verbs used by policies."""

    READ = "read"
    UPDATE = "update"
    QUERY = "query"
    ACCESS_PII = "access_pii"
    TRANSFER = "transfer"
    ADJUST_INVENTORY = "adjust_inventory"
    PROCESS_ORDER = "process_order"
    APPLY_DISCOUNT = "apply_discount"
    PROCESS_REFUND = "process_refund"


# ---------------------------------------------------------------------------
# Domain entities (mock data)
# ---------------------------------------------------------------------------


class Customer(BaseModel):
    customer_id: str
    name: str
    email: str
    phone: Optional[str] = None
    tier: CustomerTier = CustomerTier.REGULAR
    consent_given: bool = False


class Product(BaseModel):
    product_id: str
    name: str
    cost: float = Field(ge=0)
    price: float = Field(ge=0)
    minimum_advertised_price: Optional[float] = None


class InventoryItem(BaseModel):
    product_id: str
    location: str
    quantity: int = Field(ge=0)


class Order(BaseModel):
    order_id: str
    customer_id: str
    amount: float = Field(ge=0)
    days_since_purchase: int = 0
    has_receipt: bool = True


# ---------------------------------------------------------------------------
# Policy I/O
# ---------------------------------------------------------------------------


class AgentContext(BaseModel):
    """Identity passed to OPA on every call."""

    agent_id: str
    agent_type: str
    role: AgentRole
    location: Optional[str] = None
    trust_level: int = Field(default=3, ge=1, le=5)


class RetailAction(BaseModel):
    """Single action being evaluated by OPA."""

    action_type: ActionType
    resource: Dict[str, Any] = Field(default_factory=dict)
    context: Dict[str, Any] = Field(default_factory=dict)


class PolicyAuditLog(BaseModel):
    """One audit record per policy evaluation."""

    timestamp: datetime = Field(default_factory=datetime.utcnow)
    agent_id: str
    policy_path: str
    allow: bool
    reason: Optional[str] = None
    input_data: Dict[str, Any] = Field(default_factory=dict)
    duration_ms: float = 0.0
