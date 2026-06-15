#!/usr/bin/env python3
"""Quick environment sanity check for the workshop.

Run:
    python scripts/verify_workshop.py
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))


def main() -> int:
    print("Workshop verification")
    print("=" * 40)
    ok = True

    # 1. Imports
    try:
        from src.agents import (  # noqa: F401
            CustomerServiceAgent,
            InventoryAgent,
            OrderProcessingAgent,
            ReturnsAgent,
        )
        from src.opa import OPAClient  # noqa: F401
        from src.policy import PolicyEnforcer  # noqa: F401

        print("[OK] imports")
    except Exception as exc:  # noqa: BLE001
        print(f"[FAIL] imports: {exc}")
        ok = False

    # 2. Policy files
    pol_dir = Path(__file__).resolve().parents[1] / "src" / "policies"
    for name in ("authorization.rego", "behavior.rego"):
        if (pol_dir / name).exists():
            print(f"[OK] {name}")
        else:
            print(f"[FAIL] missing {name}")
            ok = False

    # 3. OPA reachable (warning only)
    try:
        from src.opa import OPAClient as _C

        if _C().health_check():
            print("[OK] OPA server reachable")
        else:
            print("[WARN] OPA not reachable — start with: docker-compose up -d")
    except Exception as exc:  # noqa: BLE001
        print(f"[WARN] OPA check failed: {exc}")

    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
