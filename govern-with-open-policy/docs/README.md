# Documentation Index

This directory contains comprehensive documentation for the Retail AI Agent Policy Workshop.

## Quick Navigation

### Getting Started

- **[QUICKSTART.md](QUICKSTART.md)** - Get up and running in 5 minutes
  - Prerequisites
  - Installation steps
  - Running your first demo

### Core Concepts

- **[AI_AGENT_PATTERN.md](AI_AGENT_PATTERN.md)** - AI Agent + Tool Use Pattern
  - Architecture of policy-enforced AI agents
  - How OPA-A and OPA-B work with tool execution
  - Step-by-step examples with diagrams
  - Implementation guide and best practices

### Comparison & Alternatives

- **[OPA_VS_AGENT_GOVERNANCE.md](OPA_VS_AGENT_GOVERNANCE.md)** - ⭐ OPA vs. Agent Governance Toolkit
  - Detailed feature comparison
  - Architecture differences
  - When to use each approach
  - Hybrid approaches
  - Code examples for both patterns

### Technical Deep Dive

- **[ARCHITECTURE.md](ARCHITECTURE.md)** - System Architecture
  - Component overview
  - Policy layers (OPA-A and OPA-B)
  - Middleware pattern details
  - Integration with Microsoft Agent Framework
  - Deployment architecture

### Maintenance

- **[CLEANUP_SUMMARY.md](CLEANUP_SUMMARY.md)** - Recent Changes
  - Repository streamlining details
  - What was removed and why
  - Current project structure
  - Migration notes

---

## Documentation Structure

```
docs/
├── README.md                    # This file - documentation index
├── QUICKSTART.md                # 5-minute setup guide
├── AI_AGENT_PATTERN.md          # Core pattern explanation
├── OPA_VS_AGENT_GOVERNANCE.md   # Comparison document
├── ARCHITECTURE.md              # Technical deep dive
└── CLEANUP_SUMMARY.md           # Change log
```

---

## Workshop Learning Path

**Recommended reading order:**

1. **Start Here** → [QUICKSTART.md](QUICKSTART.md)
   - Get OPA and dependencies running
   - Run your first demo

2. **Understand the Pattern** → [AI_AGENT_PATTERN.md](AI_AGENT_PATTERN.md)
   - Learn how AI agents use tools
   - Understand policy enforcement flow
   - See concrete examples

3. **Compare Approaches** → [OPA_VS_AGENT_GOVERNANCE.md](OPA_VS_AGENT_GOVERNANCE.md)
   - Understand when to use OPA
   - Learn about alternatives
   - Make informed decisions

4. **Deep Technical Dive** → [ARCHITECTURE.md](ARCHITECTURE.md)
   - System internals
   - Middleware implementation
   - Production considerations

5. **Reference** → [CLEANUP_SUMMARY.md](CLEANUP_SUMMARY.md)
   - Recent changes
   - Project structure
   - Development notes

---

## Related Materials

### Code Examples
- `../scripts/demo_ai_agent.py` - Main demonstration
- `../src/agents/ai_customer_service.py` - Example AI agent implementation
- `../src/common/policy_middleware.py` - Policy enforcement middleware

### Interactive Learning
- `../notebooks/01-setup-and-intro.ipynb` - Workshop introduction
- `../notebooks/02-opa-authorization.ipynb` - OPA-A hands-on
- `../notebooks/03-opa-behavior.ipynb` - OPA-B hands-on
- `../notebooks/05-policy-violations.ipynb` - Debugging guide
- `../notebooks/06-foundry-deployment.ipynb` - Production deployment

### Policies
- `../src/policies/authorization.rego` - OPA-A authorization policies
- `../src/policies/behavior.rego` - OPA-B behavior constraints

---

## Contributing to Documentation

When updating documentation:

1. **Maintain consistency** - Follow existing structure and style
2. **Update cross-references** - Check for links that need updating
3. **Test examples** - Ensure code examples actually work
4. **Keep it workshop-focused** - Remember this is for teaching

### Documentation Standards

- Use clear, concise language
- Include code examples where helpful
- Provide diagrams for complex concepts
- Link to related documents
- Keep workshop participants in mind

---

## Quick Reference

| Need to... | See Document |
|------------|--------------|
| Get started quickly | [QUICKSTART.md](QUICKSTART.md) |
| Understand AI agent pattern | [AI_AGENT_PATTERN.md](AI_AGENT_PATTERN.md) |
| Compare with alternatives | [OPA_VS_AGENT_GOVERNANCE.md](OPA_VS_AGENT_GOVERNANCE.md) |
| Understand system design | [ARCHITECTURE.md](ARCHITECTURE.md) |
| See recent changes | [CLEANUP_SUMMARY.md](CLEANUP_SUMMARY.md) |
| Deploy to production | [QUICKSTART.md](QUICKSTART.md) + Notebook 06 |

---

For the main project README, see [`../README.md`](../README.md)
