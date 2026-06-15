# Quick Start Guide

Welcome to the Retail AI Agent Policy Workshop! This guide will get you up and running in 5 minutes.

## Prerequisites Check

Before you begin, ensure you have:
- ✅ Python 3.11 or higher
- ✅ Docker and Docker Compose
- ✅ uv package manager (install: `curl -LsSf https://astral.sh/uv/install.sh | sh`)

## Step-by-Step Setup

### 1. Install Dependencies (2 minutes)

```bash
# From the project root directory
uv sync --extra all
```

This installs all required packages including:
- Azure AI Projects SDK
- OPA client libraries
- Jupyter notebooks
- Testing tools

### 2. Start OPA Server (30 seconds)

```bash
# Start OPA in the background
docker-compose up -d

# Verify it's running
curl http://localhost:8181/health
# Should return: {}
```

The OPA server loads policies from `src/policies/` automatically.

### 3. Configure Environment (30 seconds)

```bash
# Copy the template
cp .env.template .env

# For local testing only, no changes needed!
# .env already configured with:
# - OPA_URL=http://localhost:8181
# - USE_MOCK_DATA=true
# - ENABLE_POLICY_AUDIT=true
```

For Foundry deployment, edit `.env` with your Azure credentials.

### 4. Run Your First Demo (1 minute)

```bash
# Activate the virtual environment
source .venv/bin/activate

# Option 1: AI Agent Demo (RECOMMENDED - shows the main pattern)
python scripts/demo_ai_agent.py

# Option 2: Pattern Demo (simpler, good for learning OPA basics)
python scripts/demo_customer_service.py
```

**AI Agent Demo** shows:
- \u2705 LLM-powered agent selecting tools
- \u2705 OPA-A authorization before tool execution
- \u2705 OPA-B behavior checks after execution
- \u274c Policy denials when rules not met

**Pattern Demo** shows:
- \u2705 Policy enforcement mechanics
- \u2705 Simpler code without AI complexity
- \u2705 Good for understanding OPA concepts

### 5. Explore with Jupyter (1 minute)

```bash
# Start Jupyter
jupyter notebook notebooks/

# Open: 01-setup-and-intro.ipynb
# Click: Run All
```

## Verify Everything Works

Run the test suite:

```bash
pytest tests/test_policies/test_authorization.py -v
```

Expected output:
```
tests/test_policies/test_authorization.py::TestAuthorizationPolicies::test_pii_access_with_consent PASSED
tests/test_policies/test_authorization.py::TestAuthorizationPolicies::test_pii_access_without_consent PASSED
...
```

All tests should PASS ✅

## What's Next?

### Learn the Concepts

1. Read [README.md](README.md) for comprehensive overview
2. Review [ARCHITECTURE.md](ARCHITECTURE.md) for system design
3. Check [.copilot-instructions.md](.copilot-instructions.md) for development guide

### Explore the Code

**Agents** (in `src/agents/`):
- `customer_service.py` - PII protection demo
- `inventory_management.py` - RBAC demo
- `order_processing.py` - Transaction limits demo
- `returns_refund.py` - Refund policy demo

**Policies** (in `src/policies/`):
- `authorization.rego` - OPA-A (Who can do what?)
- `behavior.rego` - OPA-B (Should we constrain this?)

### Try More Demos

```bash
# Inventory management with role-based access
python scripts/demo_inventory.py

# Order processing with pricing policies
python scripts/demo_order_processing.py

# Policy violation scenarios
python scripts/demo_policy_enforcement.py
```

### Interactive Notebooks

Notebooks in `notebooks/`:
1. `01-setup-and-intro.ipynb` - Start here!
2. `02-opa-authorization.ipynb` - OPA-A deep dive
3. `03-opa-behavior.ipynb` - OPA-B constraints
4. `04-agent-workflows.ipynb` - Multi-agent scenarios
5. `05-policy-violations.ipynb` - Debugging policies

## Troubleshooting

### OPA Not Running

```bash
# Check Docker container
docker ps | grep opa

# View logs
docker-compose logs opa

# Restart if needed
docker-compose restart opa
```

### Import Errors

```bash
# Ensure virtual environment is activated
source .venv/bin/activate

# Reinstall if needed
uv sync --extra all
```

### Port Already in Use

If port 8181 is occupied:

```bash
# Stop OPA
docker-compose down

# Change port in docker-compose.yml:
ports:
  - "8182:8181"  # Use 8182 instead

# Update .env:
OPA_URL=http://localhost:8182

# Restart
docker-compose up -d
```

### Audit Logs Not Writing

```bash
# Create logs directory
mkdir -p logs

# Verify permissions
chmod 755 logs

# Check .env setting
ENABLE_POLICY_AUDIT=true
```

## Workshop Flow

For the complete workshop experience:

1. **Setup** (this guide) - 5 minutes ✅
2. **Introduction** - Read README.md concepts
3. **Hands-on Labs** - Run all demo scripts
4. **Deep Dive** - Complete Jupyter notebooks
5. **Advanced** - Modify policies and add features
6. **Deployment** - Deploy to Azure AI Foundry (optional)

## Getting Help

### Check Audit Logs

```bash
# View policy decisions
tail -f logs/policy-audit.jsonl

# Find denied actions
grep '"allow": false' logs/policy-audit.jsonl
```

### Test Policies Directly

```bash
# Test authorization policy
echo '{"agent": {"role": "cashier"}, "action": "read", "resource": {"type": "inventory"}}' | \
  opa eval -d src/policies/authorization.rego -I "data.retail.authorization.allow"
```

### Use Copilot

Ask questions in VS Code Copilot Chat:
- "Explain how OPA-A works in this project"
- "Show me examples of adding a new policy"
- "How do I test my agent?"

The `.copilot-instructions.md` file provides context.

## Success Criteria

You're ready to proceed when:

- ✅ `uv sync` completes without errors
- ✅ OPA health check returns `{}`
- ✅ `python scripts/demo_customer_service.py` runs successfully
- ✅ Tests pass: `pytest tests/test_policies/`
- ✅ Jupyter notebooks open and run

## Next Steps

Congratulations! You're now ready to:

1. Experiment with different agent roles
2. Modify policies in `src/policies/`
3. Create your own retail scenarios
4. Deploy agents to Azure AI Foundry

Start with: `python scripts/demo_customer_service.py`

Happy learning! 🚀

---

**Need Help?**
- Review [README.md](README.md) for detailed documentation
- Check [ARCHITECTURE.md](ARCHITECTURE.md) for system design
- Consult `.copilot-instructions.md` for development patterns
