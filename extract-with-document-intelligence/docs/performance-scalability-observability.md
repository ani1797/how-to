# Performance, Scalability, Resiliency, Security, and Observability

> Production-focused guidance for running Azure Document Intelligence workloads in insurance and regulated environments.

---

## Scope

This guide covers the five operational categories most teams need before production:

1. Performance
2. Scalability
3. Resiliency
4. Security
5. Monitoring and observability

The recommendations apply to Azure AI Document Intelligence v4.0 workloads using either prebuilt or custom models.

---

## 1) Performance

### Performance Objectives

Define explicit service-level indicators before tuning:

| Indicator | Typical Target | Why it matters |
|---|---|---|
| End-to-end latency (P95) | <= 30 seconds for single documents | User-facing responsiveness |
| Throughput | Match peak claims ingestion rate with buffer | Operational stability |
| Extraction quality | Field-level confidence threshold per document class | Downstream automation quality |
| Failure rate | < 1% non-retriable failures | Predictability and support load |

### Levers that affect performance

| Lever | Impact | Recommendation |
|---|---|---|
| Document quality (scan clarity, skew, DPI) | High | Pre-normalize scans and reject unreadable inputs early |
| Page count and file size | High | Split large files where business process allows |
| Model choice | Medium/High | Use prebuilt models when possible; reserve custom for domain-specific fields |
| Add-on capabilities | Medium | Enable only capabilities that are required per workflow |
| Region proximity | Medium | Place resource close to callers and storage |

### Practical tuning guidance

1. Keep request payloads small and focused.
2. Batch ingestion at the application layer, but submit analysis requests at a rate below sustained quota.
3. Use asynchronous pollers correctly and avoid aggressive polling loops.
4. Route low-confidence outputs to human review instead of retrying unchanged documents.

---

## 2) Scalability

### Known service constraints to plan around

Use official limits as hard boundaries in design:

| Constraint area | Planning note |
|---|---|
| Transactions per second (TPS) quota | Start with default quota and request increase before launch |
| Maximum pages per document | Enforce input policy in your ingestion layer |
| Maximum document size | Validate size before submitting |
| Custom model count limits | Track model lifecycle and retire unused versions |

Reference: Azure Document Intelligence service limits documentation.

### Scaling patterns

#### Pattern A: Queue-based fan-out

Use a message queue (for example Azure Service Bus) between document intake and analysis workers.

Benefits:
- Smooths burst traffic
- Supports back-pressure
- Enables controlled concurrency

#### Pattern B: Worker autoscaling

Scale worker count based on queue depth and request latency.

Benefits:
- Efficient cost/performance balance
- Better handling of intraday spikes

#### Pattern C: Segmented workloads

Separate traffic by workload type (for example claims, invoices, identity docs) with independent worker pools and thresholds.

Benefits:
- Prevents one document class from starving another
- Enables model-specific tuning

### Capacity planning checklist

- Forecast peak documents per minute and average pages per document.
- Convert peak load into expected analysis calls per second.
- Set worker concurrency so aggregate call rate stays below sustainable quota.
- Load test with production-like documents, not synthetic placeholders only.
- File support requests for quota increase before cutover.

---

## 3) Resiliency

### Failure modes and mitigations

| Failure mode | Mitigation |
|---|---|
| Transient 5xx errors | Exponential backoff retries with jitter |
| 429 throttling | Respect Retry-After and reduce caller concurrency |
| Regional outage | Secondary-region failover for critical flows |
| Downstream outage (database/workflow) | Durable queue and dead-letter processing |
| Poison documents | Validation, quarantine workflow, and manual remediation |

### Retry policy baseline

- Retry only transient classes (429, 408, 5xx, network timeouts).
- Do not retry non-transient errors (400, 401, 403) without correction.
- Use capped exponential backoff with jitter.
- Maintain request correlation IDs for replay and support analysis.

### Business continuity pattern

1. Deploy primary and secondary Document Intelligence resources in approved regions.
2. Replicate custom models with Copy Model API.
3. Keep failover routing in application configuration.
4. Perform periodic failover drills and capture recovery time objective and recovery point objective evidence.

---

## 4) Security

### Identity and access

| Control | Recommendation |
|---|---|
| Authentication | Prefer Microsoft Entra ID with managed identity in production |
| Authorization | Apply least-privilege RBAC roles (for example Cognitive Services User) |
| Secrets | Store keys in Azure Key Vault; rotate regularly |
| Access reviews | Run periodic role assignment reviews |

### Network and data protection

| Control | Recommendation |
|---|---|
| Encryption in transit | TLS 1.2+ only |
| Encryption at rest | Azure-managed encryption, optionally customer-managed keys |
| Network isolation | Private endpoint and restricted public access |
| Data lifecycle | Delete analyze results early for sensitive classes |
| Data residency | Deploy only in approved jurisdictions |

### Regulated workload controls

1. Use separate environments for development, test, and production.
2. Enforce region allowlists with Azure Policy.
3. Capture audit logs to Log Analytics with defined retention.
4. Apply documented data classification for each document stream.

---

## 5) Monitoring and observability

### Signals to collect

Collect telemetry across application, platform, and business layers:

| Layer | Signal | Example metric |
|---|---|---|
| Platform | Service health and API metrics | Availability, request count, error count, throttling |
| Application | Workflow telemetry | Queue lag, worker concurrency, retry attempts |
| Quality | Extraction outcomes | Confidence distributions, human-review rate |
| Business | Process outcomes | Claims turnaround time, straight-through processing rate |

### Recommended alert set

| Alert | Suggested trigger |
|---|---|
| Error spike | 5xx or client error rate above baseline for 5-10 minutes |
| Throttling | 429 count above baseline |
| Latency regression | P95 latency over SLO threshold |
| Queue backlog | Queue age/depth above operational threshold |
| Failover event | Any routing to secondary region |

### Logging practices

1. Emit one correlation ID per incoming document and propagate through all components.
2. Log model ID, document class, page count, and processing duration.
3. Avoid logging raw sensitive document content.
4. Record confidence and human-review decisions for model governance.

### Dashboard starter widgets

- Requests per minute
- P50/P95/P99 analysis latency
- Error rate by status code
- 429 throttling trend
- Queue depth and oldest message age
- Human-review volume and percentage
- Confidence histogram by field and document class

---

## Implementation roadmap

### Phase 1: Baseline readiness

- Define SLOs for latency, throughput, and failure rate.
- Enable diagnostics and central log collection.
- Implement retry with backoff and idempotent processing.

### Phase 2: Scale readiness

- Introduce queue-based decoupling and autoscaled workers.
- Run load tests with representative documents.
- Request quota increases as needed.

### Phase 3: Resilience and compliance hardening

- Configure secondary region and failover runbook.
- Enforce private networking and policy guardrails.
- Add quality monitoring and drift indicators.

---

## Cross-reference in this repository

- Security and compliance details: see security-privacy-compliance.md
- Disaster recovery details: see resilience-and-dr.md
- Data residency details: see data-residency.md
- Official documentation links: see resources.md

---

## References

- Azure Document Intelligence overview: https://learn.microsoft.com/en-us/azure/ai-services/document-intelligence/
- Service limits: https://learn.microsoft.com/en-us/azure/ai-services/document-intelligence/service-limits
- Monitor Document Intelligence: https://learn.microsoft.com/en-us/azure/ai-services/document-intelligence/how-to-guides/monitor-document-intelligence
- Data privacy and security: https://learn.microsoft.com/en-us/legal/cognitive-services/document-intelligence/data-privacy-security
- Disaster recovery and model copy: https://learn.microsoft.com/en-us/azure/ai-services/document-intelligence/disaster-recovery
