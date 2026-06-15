# Security, Privacy & Compliance

> How Azure Document Intelligence protects sensitive insurance data.

---

## Encryption

| Layer | Protection |
|---|---|
| **In transit** | TLS 1.2+ (TLS 1.3 negotiated by default) for all API calls |
| **At rest** | AES-256 encryption for any persisted data |
| **Customer-managed keys** | Supported via Azure Key Vault for additional control |

All communication with the Document Intelligence API uses HTTPS. No data is ever sent in plaintext.

---

## Data Handling

### Temporary Storage

- Documents submitted via URL or file upload are **processed in memory** and **temporarily cached** for up to **24 hours** for result retrieval.
- After 24 hours, analysis results are **automatically deleted**.
- You can delete results immediately using the **Delete Analyze Result** API for sensitive documents.

### No Data Used for Training

- **Your documents are never used to train Microsoft models.**
- Data submitted to the API is not shared with other customers.
- For custom model training, your training data resides in **your own Azure Blob Storage** — Microsoft accesses it only during the training operation.

### Custom Model Training Data

- Training data is stored in **your Azure Blob Storage account**.
- You control access, encryption, and lifecycle of training data.
- The service accesses training data via SAS token during training only.

---

## Authentication

### API Key Authentication

- Two keys provided per resource (for key rotation without downtime).
- Rotate keys regularly using the Azure Portal or CLI.
- Store keys in **Azure Key Vault**, never in source code.

### Microsoft Entra ID (Recommended for Production)

- Use `DefaultAzureCredential` from `azure-identity` for token-based auth.
- Supports managed identities — no secrets in code.
- Role: **Cognitive Services User** grants analyze permissions.
- Role: **Cognitive Services Contributor** grants model management.

```python
# Recommended: Entra ID with managed identity
from azure.identity import DefaultAzureCredential
from azure.ai.documentintelligence import DocumentIntelligenceClient

client = DocumentIntelligenceClient(
    endpoint=os.environ["DOCUMENTINTELLIGENCE_ENDPOINT"],
    credential=DefaultAzureCredential()
)
```

---

## Network Security

| Feature | Description |
|---|---|
| **Private Endpoints** | Access the service entirely over your Azure Virtual Network |
| **VNet Service Endpoints** | Restrict access to specific subnets |
| **IP Firewall** | Allow/deny access from specific IP ranges |
| **Disable Public Access** | Turn off all public internet access |

For insurance companies handling PHI/PII, **private endpoints are strongly recommended** to ensure documents never traverse the public internet.

---

## Compliance Certifications

Azure Document Intelligence inherits Azure Cognitive Services compliance certifications:

| Certification | Relevance for Insurance |
|---|---|
| **HIPAA BAA** | Required for processing health insurance claims and medical documents |
| **SOC 1, SOC 2, SOC 3** | Audit controls for financial and operational processes |
| **ISO 27001** | Information security management standard |
| **ISO 27017** | Cloud security controls |
| **ISO 27018** | Protection of personal data in the cloud |
| **PCI DSS** | Credit card data on invoices/receipts |
| **FedRAMP** | US government cloud requirements |
| **CSA STAR** | Cloud Security Alliance certification |

> Full list: [Azure Compliance Offerings](https://learn.microsoft.com/en-us/azure/compliance/offerings/)

### HIPAA Considerations for Insurance

- Azure offers a **Business Associate Agreement (BAA)** for HIPAA-covered entities.
- Document Intelligence is included in the BAA.
- You must still implement appropriate access controls, audit logging, and data handling procedures on your side.

---

## Audit & Monitoring

| Tool | Purpose |
|---|---|
| **Azure Monitor** | Track API calls, latency, error rates |
| **Diagnostic Logs** | Detailed per-request logging |
| **Azure Policy** | Enforce organizational standards (e.g., require private endpoints) |
| **Activity Log** | Track management operations (resource creation, key rotation) |

### Enable Diagnostic Logging

```bash
# Enable diagnostic logs for your Document Intelligence resource
az monitor diagnostic-settings create \
  --name "doc-intel-logs" \
  --resource "/subscriptions/{sub-id}/resourceGroups/{rg}/providers/Microsoft.CognitiveServices/accounts/{name}" \
  --workspace "/subscriptions/{sub-id}/resourceGroups/{rg}/providers/Microsoft.OperationalInsights/workspaces/{workspace-name}" \
  --logs '[{"category":"Audit","enabled":true},{"category":"RequestResponse","enabled":true}]'
```

---

## Insurance-Specific Recommendations

1. **Use Private Endpoints**: Keep all document traffic within your VNet.
2. **Enable Diagnostic Logging**: Required for HIPAA audit trail.
3. **Managed Identity**: Eliminate API keys in production — use `DefaultAzureCredential`.
4. **Delete Results Promptly**: Call Delete Analyze Result API after processing sensitive claims.
5. **Key Vault for Secrets**: Store any API keys or connection strings in Azure Key Vault.
6. **Restrict Network Access**: Use IP firewall + private endpoints to limit access.
7. **Tag Resources**: Apply tags for cost tracking and compliance grouping.

---

## References

- [Document Intelligence Security](https://learn.microsoft.com/en-us/azure/ai-services/document-intelligence/authentication/managed-identities)
- [Azure Cognitive Services Virtual Networks](https://learn.microsoft.com/en-us/azure/ai-services/cognitive-services-virtual-networks)
- [Azure Compliance Documentation](https://learn.microsoft.com/en-us/azure/compliance/)
- [HIPAA on Azure](https://learn.microsoft.com/en-us/azure/compliance/offerings/offering-hipaa-us)
