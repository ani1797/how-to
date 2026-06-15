# Resilience & Disaster Recovery

> How to build reliable, fault-tolerant document processing pipelines with Azure Document Intelligence.

---

## Service Availability

| Feature | Details |
|---|---|
| **SLA** | 99.9% uptime for Standard (S0) tier |
| **Regions** | 30+ Azure regions worldwide |
| **Availability Zones** | Supported in most regions for zone-redundant deployment |

---

## Built-in Resilience

Azure Document Intelligence provides several built-in resilience features:

1. **Automatic retries**: The Azure SDK includes built-in retry policies for transient failures.
2. **Zone redundancy**: Resources deployed in regions with Availability Zones are automatically distributed.
3. **Load balancing**: The service automatically distributes requests across healthy instances.

---

## Cross-Region Redundancy with the Copy Model API

For **custom models**, you can replicate models to a secondary region using the **Copy Model** API. This enables failover if your primary region becomes unavailable.

### Architecture

```
┌─────────────────┐         Copy API          ┌─────────────────┐
│  Primary Region  │ ──────────────────────►  │ Secondary Region │
│  (East US)       │                           │  (West US 2)     │
│                  │                           │                  │
│  Custom Models   │                           │  Custom Models   │
│  Classifiers     │                           │  Classifiers     │
└────────┬────────┘                           └────────┬────────┘
         │                                              │
         │  Normal traffic                    Failover traffic
         ▼                                              ▼
    ┌──────────┐                                ┌──────────┐
    │ Your App │ ──── if primary fails ────►   │ Your App │
    └──────────┘                                └──────────┘
```

### Copy Model Example

```python
from azure.ai.documentintelligence import DocumentIntelligenceAdministrationClient
from azure.core.credentials import AzureKeyCredential

# Source (primary region)
source_client = DocumentIntelligenceAdministrationClient(
    endpoint="https://primary-eastus.cognitiveservices.azure.com/",
    credential=AzureKeyCredential(primary_key)
)

# Target (secondary region)
target_client = DocumentIntelligenceAdministrationClient(
    endpoint="https://secondary-westus2.cognitiveservices.azure.com/",
    credential=AzureKeyCredential(secondary_key)
)

# Step 1: Get copy authorization from target
auth = target_client.authorize_model_copy(
    authorize_copy_request={
        "modelId": "my-insurance-claim-model",
        "description": "DR copy from East US"
    }
)

# Step 2: Copy from source to target
poller = source_client.begin_copy_model_to(
    model_id="my-insurance-claim-model",
    copy_to_request=auth
)
copied_model = poller.result()
print(f"Model copied to secondary region: {copied_model.model_id}")
```

> **Note**: Prebuilt models are available in all regions automatically — only custom models need to be copied.

---

## Client-Side Retry Strategy

The Azure SDK provides configurable retry policies. For production insurance workloads, configure retries appropriate to your SLA requirements.

```python
from azure.ai.documentintelligence import DocumentIntelligenceClient
from azure.core.credentials import AzureKeyCredential

# Configure custom retry policy
client = DocumentIntelligenceClient(
    endpoint=endpoint,
    credential=AzureKeyCredential(key),
    retry_total=5,           # Max retries (default: 3)
    retry_backoff_factor=1,  # Backoff multiplier (default: 0.8)
    retry_backoff_max=60,    # Max backoff in seconds (default: 120)
)
```

### Retry Logic Summary

| Error | Action |
|---|---|
| **429 Too Many Requests** | Retry with exponential backoff (respect `Retry-After` header) |
| **500 Internal Server Error** | Retry up to 3 times with backoff |
| **502/503 Service Unavailable** | Retry with backoff; check Azure Status page if persistent |
| **408 Request Timeout** | Retry immediately, then with backoff |
| **Network errors** | Retry with backoff |
| **400 Bad Request** | Do not retry — fix the request |
| **401/403 Auth errors** | Do not retry — fix credentials |

---

## Multi-Region Failover Pattern

For insurance companies requiring high availability:

```python
import os
from azure.core.exceptions import HttpResponseError, ServiceRequestError

# Primary and secondary endpoints
ENDPOINTS = [
    {
        "endpoint": os.environ["PRIMARY_ENDPOINT"],
        "key": os.environ["PRIMARY_KEY"],
    },
    {
        "endpoint": os.environ["SECONDARY_ENDPOINT"],
        "key": os.environ["SECONDARY_KEY"],
    },
]

def analyze_with_failover(model_id, document_url):
    """Try primary region first, fail over to secondary."""
    for i, config in enumerate(ENDPOINTS):
        region = "primary" if i == 0 else "secondary"
        try:
            client = DocumentIntelligenceClient(
                endpoint=config["endpoint"],
                credential=AzureKeyCredential(config["key"])
            )
            poller = client.begin_analyze_document(
                model_id,
                {"urlSource": document_url}
            )
            result = poller.result()
            if i > 0:
                print(f"⚠️ Succeeded on {region} region (failover)")
            return result
        except (HttpResponseError, ServiceRequestError) as e:
            print(f"❌ {region} region failed: {e}")
            if i == len(ENDPOINTS) - 1:
                raise  # All regions failed
    
    raise RuntimeError("All regions exhausted")
```

---

## APIM as a Resiliency Control Plane

Azure API Management (APIM) can sit in front of Document Intelligence resources and enforce resilient behavior consistently for all callers.

### Why APIM Helps

1. **Centralized failover**: Route traffic to primary or secondary backend without changing application code.
2. **Gateway retries**: Apply retry and timeout policies at the gateway.
3. **Rate protection**: Throttle spikes before they hit Document Intelligence quotas.
4. **Circuit breaking**: Temporarily stop sending traffic to unhealthy backends.
5. **Operational control**: Use revisions/versions to roll out policy changes safely.

### High-Resiliency Flow Diagram

- [docs/diagrams/arch-high-resiliency-apim.mmd](docs/diagrams/arch-high-resiliency-apim.mmd)
- [docs/diagrams/arch-high-resiliency-apim.png](docs/diagrams/arch-high-resiliency-apim.png) (PNG fallback)

### Example APIM Policy Pattern (Conceptual)

```xml
<policies>
    <inbound>
        <base />
        <set-backend-service backend-id="docintel-primary" />
        <retry condition="@(context.Response != null && (context.Response.StatusCode == 429 || context.Response.StatusCode >= 500))"
                     count="3"
                     interval="2"
                     delta="2"
                     max-interval="15" />
        <rate-limit-by-key calls="100" renewal-period="60" counter-key="@(context.Subscription.Id)" />
    </inbound>
    <backend>
        <base />
    </backend>
    <outbound>
        <base />
    </outbound>
    <on-error>
        <base />
    </on-error>
</policies>
```

> Use APIM backend pools and health-aware routing to fail over from primary to secondary region at the gateway layer.

---

## High Throughput with Messaging

For bursty or very high-volume workloads (for example, claims ingestion), decouple ingestion from processing by introducing messaging.

### Recommended Pattern

1. **Ingest quickly**: API writes document metadata and blob location to a queue or stream.
2. **Scale processors horizontally**: Worker services pull messages and call Document Intelligence asynchronously.
3. **Control backpressure**: Queue depth absorbs spikes while workers scale out.
4. **Handle failures safely**: Use dead-letter queues for poison messages and replay workflows.
5. **Preserve ordering where needed**: Use sessions/partition keys for per-claim ordering.

### Messaging Options

| Service | Best For | Notes |
|---|---|---|
| **Azure Service Bus** | Command-style work queues, guaranteed delivery, DLQ | Good for transactional workflows and per-item retries |
| **Azure Event Hubs** | Very high event ingestion throughput | Best for streaming telemetry/events, then fan-out to processors |
| **Azure Storage Queue** | Cost-efficient simple queueing | Good for simpler pipelines with basic requirements |

### High-Throughput Flow Diagram

- [docs/diagrams/arch-high-throughput-messaging.mmd](docs/diagrams/arch-high-throughput-messaging.mmd)
- [docs/diagrams/arch-high-throughput-messaging.png](docs/diagrams/arch-high-throughput-messaging.png) (PNG fallback)

### Worker Processing Considerations

- Use idempotency keys (for example, `claim_id + document_hash`) to avoid duplicate processing.
- Tune concurrency per worker based on TPS quota and observed 429 rates.
- Send failed jobs to DLQ after max retry attempts and alert operations.
- Persist analysis outputs to durable storage (Blob/DB) for replay and auditing.

---

## Monitoring & Alerting

Set up proactive monitoring to detect issues before they impact operations:

### Key Metrics to Monitor

| Metric | Alert Threshold | Description |
|---|---|---|
| **Error Rate** | > 5% of requests | API returning 4xx/5xx |
| **Latency (P95)** | > 30 seconds | Slow analysis times |
| **429 Rate** | > 1% of requests | Hitting TPS limits |
| **Availability** | < 99.9% | Service degradation |

### Azure Monitor Alert (CLI)

```bash
# Create an alert for high error rate
az monitor metrics alert create \
  --name "DocIntel-HighErrorRate" \
  --resource-group "my-rg" \
  --scopes "/subscriptions/{sub}/resourceGroups/{rg}/providers/Microsoft.CognitiveServices/accounts/{name}" \
  --condition "avg ClientErrors > 5" \
  --window-size 5m \
  --evaluation-frequency 1m \
  --action "/subscriptions/{sub}/resourceGroups/{rg}/providers/microsoft.insights/actionGroups/{ag}"
```

---

## Quota Planning

| Quota | Default | How to Increase |
|---|---|---|
| Analyze TPS | 15 (S0), 1 (F0) | Azure Support ticket |
| Custom models per resource | 500 | Azure Support ticket |
| Max document size | 500 MB (S0) | Cannot increase |
| Max pages per document | 2,000 (S0) | Cannot increase |

For insurance companies processing thousands of claims daily, request a TPS increase **before** going to production.

---

## Disaster Recovery Checklist

- [ ] Deploy Document Intelligence resources in **two regions**
- [ ] Copy custom models to secondary region on a schedule (e.g., after each training)
- [ ] Implement **client-side failover** logic in your application
- [ ] Add **APIM gateway failover/rate-limit policies** in front of Document Intelligence
- [ ] Add a **messaging buffer** (Service Bus/Event Hubs/Queue) for burst handling
- [ ] Configure **Azure Monitor alerts** for error rates and latency
- [ ] Test failover regularly (quarterly DR drills)
- [ ] Document the failover runbook for operations team
- [ ] Request **TPS increases** in both regions

---

## References

- [Document Intelligence Service Limits](https://learn.microsoft.com/en-us/azure/ai-services/document-intelligence/service-limits)
- [Copy Models Across Resources](https://learn.microsoft.com/en-us/azure/ai-services/document-intelligence/disaster-recovery)
- [Azure Cognitive Services High Availability](https://learn.microsoft.com/en-us/azure/ai-services/cognitive-services-virtual-networks)
- [Azure Monitor for Cognitive Services](https://learn.microsoft.com/en-us/azure/ai-services/document-intelligence/how-to-guides/monitor-document-intelligence)
- [APIM Policy Reference](https://learn.microsoft.com/en-us/azure/api-management/api-management-policies)
- [APIM Backend Pools and Load Balancing](https://learn.microsoft.com/en-us/azure/api-management/backends)
- [Azure Service Bus Overview](https://learn.microsoft.com/en-us/azure/service-bus-messaging/service-bus-messaging-overview)
- [Azure Event Hubs Overview](https://learn.microsoft.com/en-us/azure/event-hubs/event-hubs-about)
