# Resources & Further Reading

> Curated links to documentation, SDKs, samples, and learning resources for Azure Document Intelligence.

---

## Repository Guides (This Project)

| Guide | Focus |
|---|---|
| [Performance, Scalability & Observability](performance-scalability-observability.md) | Production operations: performance, scale, resiliency, security, monitoring |
| [Security, Privacy & Compliance](security-privacy-compliance.md) | Encryption, identity, networking controls, compliance posture |
| [Resilience & Disaster Recovery](resilience-and-dr.md) | Retry strategy, failover, cross-region custom model copy |
| [Data Residency](data-residency.md) | Region placement, residency guarantees, regulatory considerations |

---

## Official Documentation

| Resource | Link |
|---|---|
| **Product Overview** | [Azure Document Intelligence](https://azure.microsoft.com/en-us/products/ai-services/ai-document-intelligence/) |
| **Documentation Hub** | [Document Intelligence Docs](https://learn.microsoft.com/en-us/azure/ai-services/document-intelligence/) |
| **What's New** | [Release Notes](https://learn.microsoft.com/en-us/azure/ai-services/document-intelligence/whats-new) |
| **Pricing** | [Document Intelligence Pricing](https://azure.microsoft.com/en-us/pricing/details/ai-document-intelligence/) |
| **Service Limits** | [Quotas & Limits](https://learn.microsoft.com/en-us/azure/ai-services/document-intelligence/service-limits) |

---

## SDK & API Reference

### Python SDK (v4.0 — Current)

| Resource | Link |
|---|---|
| **PyPI Package** | [azure-ai-documentintelligence](https://pypi.org/project/azure-ai-documentintelligence/) |
| **SDK Reference** | [Python SDK Docs](https://learn.microsoft.com/en-us/python/api/azure-ai-documentintelligence/) |
| **GitHub Source** | [azure-sdk-for-python — documentintelligence](https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/documentintelligence/azure-ai-documentintelligence) |
| **SDK Samples** | [Python Samples](https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/documentintelligence/azure-ai-documentintelligence/samples) |
| **Changelog** | [CHANGELOG.md](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/documentintelligence/azure-ai-documentintelligence/CHANGELOG.md) |

### Other Language SDKs

| Language | Package | Documentation |
|---|---|---|
| **.NET** | [Azure.AI.DocumentIntelligence](https://www.nuget.org/packages/Azure.AI.DocumentIntelligence) | [.NET Docs](https://learn.microsoft.com/en-us/dotnet/api/azure.ai.documentintelligence) |
| **Java** | [azure-ai-documentintelligence](https://central.sonatype.com/artifact/com.azure/azure-ai-documentintelligence) | [Java Docs](https://learn.microsoft.com/en-us/java/api/com.azure.ai.documentintelligence) |
| **JavaScript** | [@azure-rest/ai-document-intelligence](https://www.npmjs.com/package/@azure-rest/ai-document-intelligence) | [JS Docs](https://learn.microsoft.com/en-us/javascript/api/@azure-rest/ai-document-intelligence) |
| **REST API** | — | [REST API Reference](https://learn.microsoft.com/en-us/rest/api/aiservices/document-intelligence) |

---

## Document Intelligence Studio

The web-based interactive tool for exploring models and building custom models:

| Resource | Link |
|---|---|
| **Studio** | [Document Intelligence Studio](https://documentintelligence.ai.azure.com/) |
| **Studio Guide** | [How to Use Studio](https://learn.microsoft.com/en-us/azure/ai-services/document-intelligence/studio-overview) |

Use Studio to:
- Test prebuilt models with your own documents
- Label training data for custom models
- Build and test custom models visually
- Explore model schemas and field definitions

---

## Prebuilt Model Documentation

| Model | Documentation | Insurance Use Case |
|---|---|---|
| **Read** | [Read Model](https://learn.microsoft.com/en-us/azure/ai-services/document-intelligence/prebuilt/read) | OCR for scanned claim letters |
| **Layout** | [Layout Model](https://learn.microsoft.com/en-us/azure/ai-services/document-intelligence/prebuilt/layout) | Policy schedules with tables |
| **Invoice** | [Invoice Model](https://learn.microsoft.com/en-us/azure/ai-services/document-intelligence/prebuilt/invoice) | Vendor invoices, repair bills |
| **Receipt** | [Receipt Model](https://learn.microsoft.com/en-us/azure/ai-services/document-intelligence/prebuilt/receipt) | Expense receipts for claims |
| **ID Document** | [ID Model](https://learn.microsoft.com/en-us/azure/ai-services/document-intelligence/prebuilt/id-document) | KYC identity verification |
| **Health Insurance Card** | [Insurance Card Model](https://learn.microsoft.com/en-us/azure/ai-services/document-intelligence/prebuilt/health-insurance-card) | Member onboarding |
| **Contract** | [Contract Model](https://learn.microsoft.com/en-us/azure/ai-services/document-intelligence/prebuilt/contract) | Policy contracts review |
| **US Tax Forms** | [Tax Forms](https://learn.microsoft.com/en-us/azure/ai-services/document-intelligence/prebuilt/tax-document) | W-2, 1040, 1099 processing |

---

## Custom Models & Classifiers

| Topic | Link |
|---|---|
| **Custom Model Overview** | [Build a Custom Model](https://learn.microsoft.com/en-us/azure/ai-services/document-intelligence/train/custom-model) |
| **Custom Neural Model** | [Neural Model](https://learn.microsoft.com/en-us/azure/ai-services/document-intelligence/train/custom-neural) |
| **Custom Template Model** | [Template Model](https://learn.microsoft.com/en-us/azure/ai-services/document-intelligence/train/custom-template) |
| **Custom Classifier** | [Document Classifier](https://learn.microsoft.com/en-us/azure/ai-services/document-intelligence/train/custom-classifier) |
| **Composed Models** | [Composed Model](https://learn.microsoft.com/en-us/azure/ai-services/document-intelligence/train/composed-models) |
| **Labeling Training Data** | [Label Your Data](https://learn.microsoft.com/en-us/azure/ai-services/document-intelligence/train/custom-labels) |

---

## Quickstarts & Tutorials

| Resource | Link |
|---|---|
| **Python Quickstart** | [Quickstart: Python SDK](https://learn.microsoft.com/en-us/azure/ai-services/document-intelligence/quickstarts/get-started-sdks-rest-api) |
| **Studio Quickstart** | [Quickstart: Studio](https://learn.microsoft.com/en-us/azure/ai-services/document-intelligence/quickstarts/try-document-intelligence-studio) |
| **REST API Quickstart** | [Quickstart: REST API](https://learn.microsoft.com/en-us/azure/ai-services/document-intelligence/quickstarts/get-started-sdks-rest-api?pivots=programming-language-rest-api) |

---

## GitHub Samples & Repositories

| Repository | Description |
|---|---|
| [azure-sdk-for-python — samples](https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/documentintelligence/azure-ai-documentintelligence/samples) | Official Python SDK samples |
| [cognitive-services-REST-api-samples](https://github.com/Azure-Samples/cognitive-services-REST-api-samples) | REST API samples with sample documents |
| [azure-docs-sdk-python](https://github.com/MicrosoftDocs/azure-docs-sdk-python) | Python SDK documentation source |
| [document-intelligence-code-samples](https://github.com/Azure-Samples/document-intelligence-code-samples) | Additional code samples |

---

## Microsoft Learn Training

| Module | Link |
|---|---|
| **Introduction to Azure AI Document Intelligence** | [MS Learn](https://learn.microsoft.com/en-us/training/modules/analyze-receipts-form-recognizer/) |
| **Build a Form Processing App** | [MS Learn](https://learn.microsoft.com/en-us/training/modules/work-form-recognizer/) |
| **AI-102 Certification Path** | [AI Engineer Learning Path](https://learn.microsoft.com/en-us/training/paths/prepare-for-ai-engineering/) |

---

## Security & Compliance

| Topic | Link |
|---|---|
| **Data Privacy & Security** | [Data Privacy](https://learn.microsoft.com/en-us/legal/cognitive-services/document-intelligence/data-privacy-security) |
| **Virtual Networks** | [Configure VNets](https://learn.microsoft.com/en-us/azure/ai-services/cognitive-services-virtual-networks) |
| **Managed Identities** | [Authentication Guide](https://learn.microsoft.com/en-us/azure/ai-services/document-intelligence/authentication/managed-identities) |
| **Disaster Recovery** | [Copy Models Across Regions](https://learn.microsoft.com/en-us/azure/ai-services/document-intelligence/disaster-recovery) |
| **Azure Compliance** | [Compliance Offerings](https://learn.microsoft.com/en-us/azure/compliance/offerings/) |

---

## Community & Support

| Channel | Link |
|---|---|
| **Stack Overflow** | [Tag: azure-form-recognizer](https://stackoverflow.com/questions/tagged/azure-form-recognizer) |
| **Microsoft Q&A** | [Document Intelligence Q&A](https://learn.microsoft.com/en-us/answers/tags/440/azure-form-recognizer) |
| **Azure Updates** | [Azure Updates](https://azure.microsoft.com/en-us/updates/) |
| **Azure Support** | [Create Support Ticket](https://portal.azure.com/#blade/Microsoft_Azure_Support/HelpAndSupportBlade) |
