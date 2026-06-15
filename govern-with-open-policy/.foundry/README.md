# Foundry Deployment Instructions

## Overview

This directory contains configurations for deploying the retail AI agents to Microsoft Azure AI Foundry.

## Files

- `agent-metadata.yaml` - Agent deployment specifications for all 4 agents
- `Dockerfile.template` - Template for building agent containers with OPA sidecar

## Deployment Process

### Prerequisites

1. Azure subscription with AI Foundry project created
2. Azure CLI installed and authenticated
3. Docker installed for building images
4. Azure Container Registry (ACR) configured

### Step 1: Configure Environment

Edit `.env` file with your Foundry details:

```bash
FOUNDRY_PROJECT_ENDPOINT=https://your-project.api.azureml.ms
FOUNDRY_SUBSCRIPTION_ID=your-subscription-id
FOUNDRY_RESOURCE_GROUP=your-resource-group
FOUNDRY_PROJECT_NAME=your-project-name
MODEL_NAME=gpt-4o
MODEL_DEPLOYMENT_NAME=gpt-4o
```

### Step 2: Build Container Images

Each agent needs to be containerized with OPA sidecar:

```bash
# Example for customer service agent
docker build -t retail-customer-service-agent:latest \
  --build-arg AGENT_TYPE=customer_service \
  -f .foundry/Dockerfile.template .

# Repeat for other agents
```

### Step 3: Push to Azure Container Registry

```bash
# Tag for ACR
docker tag retail-customer-service-agent:latest \
  yourregistry.azurecr.io/retail-customer-service-agent:latest

# Push to ACR
docker push yourregistry.azurecr.io/retail-customer-service-agent:latest
```

### Step 4: Deploy to Foundry

Use Azure AI Foundry CLI or SDK to deploy agents:

```bash
# Using Foundry CLI (if available)
az ml online-deployment create \
  --file .foundry/agent-metadata.yaml \
  --resource-group your-resource-group \
  --workspace-name your-project-name
```

Or use the provided deployment notebook:
```bash
jupyter notebook notebooks/06-foundry-deployment.ipynb
```

### Step 5: Test Deployment

```python
from azure.ai.projects import AIProjectClient
from azure.identity import DefaultAzureCredential

# Connect to Foundry project
client = AIProjectClient.from_connection_string(
    credential=DefaultAzureCredential(),
    conn_str=os.environ["FOUNDRY_PROJECT_ENDPOINT"]
)

# Invoke agent
response = client.agents.invoke(
    agent_name="customer-service-agent",
    message="Check customer PII for CUST-12345"
)
print(response)
```

## OPA Sidecar Pattern

Each agent container includes an OPA sidecar for local policy evaluation:

```
┌─────────────────────────────────┐
│  Agent Container                │
│                                 │
│  ┌───────────────────────────┐ │
│  │  Agent Code (Python)      │ │
│  │  Port: 8000               │ │
│  └────────┬──────────────────┘ │
│           │ localhost         │
│  ┌────────▼──────────────────┐ │
│  │  OPA Sidecar              │ │
│  │  Port: 8181               │ │
│  │  Policies: /policies      │ │
│  └───────────────────────────┘ │
│                                 │
└─────────────────────────────────┘
```

Benefits:
- Low latency policy evaluation (local)
- No external OPA server dependency
- Policy bundled with agent image
- Consistent policy version with code

## Policy Updates

To update policies in deployed agents:

1. Update Rego files in `src/policies/`
2. Rebuild container images
3. Push updated images to ACR
4. Redeploy agents with new image tags

## Monitoring

Once deployed, monitor via:
- Azure Monitor for container metrics
- Application Insights for agent telemetry
- Policy audit logs (forwarded to Log Analytics)
- Foundry agent dashboard

## Troubleshooting

### Agent Not Starting

Check container logs:
```bash
az containerapp logs show \
  --name customer-service-agent \
  --resource-group your-resource-group
```

### Policy Evaluation Failures

1. Verify OPA sidecar is running: `curl http://localhost:8181/health`
2. Check policy files are mounted: `/policies/authorization.rego`, `/policies/behavior.rego`
3. Test policies locally before deployment

### Connection Issues

- Verify Foundry endpoint in environment variables
- Check managed identity permissions
- Ensure network security group allows traffic

## Additional Resources

- [Microsoft Foundry Documentation](https://learn.microsoft.com/azure/ai-studio/)
- [Azure Container Apps](https://learn.microsoft.com/azure/container-apps/)
- [OPA in Production](https://www.openpolicyagent.org/docs/latest/deployments/)
