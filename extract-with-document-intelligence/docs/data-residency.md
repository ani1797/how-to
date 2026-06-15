# Data Residency

> Where your insurance documents are processed and stored when using Azure Document Intelligence.

---

## Core Principle

**Your data stays in the Azure region where you deploy the resource.**

When you create a Document Intelligence resource in a specific Azure region (e.g., East US), all document processing happens within that region's data center. Documents are not transferred to other regions unless you explicitly copy models or data.

---

## Data Flow

```
                    Your Region (e.g., East US)
┌──────────────────────────────────────────────────────────┐
│                                                          │
│  Your App ──► Document Intelligence API ──► Processing   │
│                                                          │
│  Documents processed in memory within this region.       │
│  Results cached ≤24 hours, then auto-deleted.            │
│                                                          │
│  Custom model training data: Your Azure Blob Storage     │
│  (in the same or any region you choose).                 │
│                                                          │
└──────────────────────────────────────────────────────────┘
```

---

## What Stays Where

| Data | Location | Retention |
|---|---|---|
| **Submitted documents** | Processed in-region | Not persisted beyond analysis |
| **Analysis results** | Stored in-region | Auto-deleted after 24 hours |
| **Custom model definitions** | Stored in-region | Until you delete the model |
| **Custom model training data** | Your Azure Blob Storage | You control retention |
| **API keys** | Stored in-region | Until you regenerate |
| **Diagnostic logs** | Your configured Log Analytics workspace | You control retention |

---

## What Microsoft Does NOT Do

- ❌ Does **not** move your documents across regions
- ❌ Does **not** store your documents permanently
- ❌ Does **not** use your documents to train Microsoft's models
- ❌ Does **not** share your data with other customers
- ❌ Does **not** retain analysis results beyond 24 hours

---

## Available Regions

Azure Document Intelligence is available in 30+ regions globally. Select a region based on:

1. **Regulatory requirements** — Where your data must reside (e.g., US, EU, specific country)
2. **Latency** — Closest region to your users/applications
3. **Feature availability** — Some features may launch in select regions first

### Commonly Used Regions for Insurance

| Region | Use Case |
|---|---|
| **East US / East US 2** | US-based insurance companies |
| **West US 2 / West US 3** | Secondary US region for DR |
| **West Europe** | EU-based operations, Schrems II compliant |
| **North Europe** | EU secondary region |
| **UK South** | UK insurance market |
| **Canada Central** | Canadian operations, data sovereignty |
| **Australia East** | APAC insurance operations |
| **Japan East** | Japanese market requirements |
| **Southeast Asia** | APAC hub |

> Full region list: [Azure Products by Region](https://azure.microsoft.com/en-us/explore/global-infrastructure/products-by-region/)

---

## Regulatory Considerations for Insurance

### United States

- HIPAA: Azure offers BAA; data processed in US regions stays in the US
- State insurance regulations: No specific cloud data residency requirements at federal level, but some states may have data localization preferences
- SOC 2 Type II compliance provides audit assurance

### European Union

- GDPR: Deploy in EU regions (West Europe, North Europe, France Central, Germany West Central) to keep data within the EU
- Schrems II: Microsoft provides EU Data Boundary commitments for applicable services
- DORA (Digital Operational Resilience Act): Relevant for insurance companies operating under EU financial regulations

### United Kingdom

- UK GDPR (post-Brexit): Deploy in UK South or UK West
- PRA/FCA: Financial regulators may have specific cloud outsourcing expectations

### Canada

- PIPEDA: Deploy in Canada Central or Canada East
- Provincial regulations (e.g., Quebec's Law 25) may require additional data handling considerations

### Australia

- Privacy Act 1988: Deploy in Australia East or Australia Southeast

---

## Cross-Region Data Movement

Data only moves between regions when **you explicitly initiate** one of these operations:

| Operation | What Moves | Your Control |
|---|---|---|
| **Copy Model API** | Model definition (not training data) | You initiate, you choose target region |
| **Custom model training** | Service reads from your Blob Storage | Blob Storage region is your choice |
| **Application failover** | Your app sends documents to a new region | You control failover logic |

---

## Recommendations for Insurance Companies

1. **Choose regions that match your regulatory requirements.**
   - US insurer processing health claims → East US or West US 2
   - EU insurer → West Europe or North Europe

2. **Deploy primary and secondary resources in paired regions.**
   - East US ↔ West US 2 (Azure paired regions for DR)
   - West Europe ↔ North Europe

3. **Keep training data in the same region as your resource** to minimize cross-region data transfer and simplify compliance documentation.

4. **Document your data flow** for compliance audits — this guide + your architecture diagram should be part of your compliance package.

5. **Use Azure Policy** to enforce resource creation in approved regions only:
   ```bash
   # Restrict Cognitive Services to specific regions
   az policy assignment create \
     --name "restrict-doc-intel-regions" \
     --policy "/providers/Microsoft.Authorization/policyDefinitions/e56962a6-4747-49cd-b67b-bf8b01975c4c" \
     --params '{"listOfAllowedLocations": {"value": ["eastus", "westus2"]}}'
   ```

6. **Enable diagnostic logging** to a Log Analytics workspace in the same region for compliance audit trails.

---

## References

- [Azure Data Residency](https://azure.microsoft.com/en-us/explore/global-infrastructure/data-residency/)
- [Azure Products by Region](https://azure.microsoft.com/en-us/explore/global-infrastructure/products-by-region/)
- [Microsoft EU Data Boundary](https://learn.microsoft.com/en-us/privacy/eudb/eu-data-boundary-learn)
- [Azure Compliance Offerings](https://learn.microsoft.com/en-us/azure/compliance/offerings/)
- [Document Intelligence Data Privacy](https://learn.microsoft.com/en-us/legal/cognitive-services/document-intelligence/data-privacy-security)
