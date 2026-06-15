# Sample Documents

The notebooks in this quickstart use publicly available sample documents hosted on GitHub. No local files are required to get started — each notebook references URLs directly.

## Public Sample Document URLs

The following URLs are used throughout the notebooks:

| Document Type | URL | Used In |
|---|---|---|
| Sample Layout PDF | [sample-layout.pdf](https://raw.githubusercontent.com/Azure-Samples/cognitive-services-REST-api-samples/master/curl/form-recognizer/sample-layout.pdf) | Notebook 02 |
| Sample Invoice | [sample-invoice.pdf](https://raw.githubusercontent.com/Azure-Samples/cognitive-services-REST-api-samples/master/curl/form-recognizer/sample-invoice.pdf) | Notebook 03 |
| Contoso Receipt | [contoso-receipt.png](https://raw.githubusercontent.com/Azure/azure-sdk-for-python/main/sdk/documentintelligence/azure-ai-documentintelligence/samples/sample_forms/receipt/contoso-receipt.png) | Notebook 04 |
| Sample ID Document | [license.jpg](https://raw.githubusercontent.com/Azure-Samples/cognitive-services-REST-api-samples/master/curl/form-recognizer/DriverLicense.png) | Notebook 05 |
| Health Insurance Card | [insurance.jpg](https://raw.githubusercontent.com/Azure-Samples/cognitive-services-REST-api-samples/master/curl/form-recognizer/insurance.jpg) | Notebook 06 |

## Using Your Own Documents

To use your own insurance documents:

1. Place your files in this directory (PDF, JPEG, PNG, BMP, TIFF, or HEIF)
2. Update the file path in the notebook cell:

```python
# Instead of URL:
# poller = client.begin_analyze_document("prebuilt-invoice", AnalyzeDocumentRequest(url_source=url))

# Use local file:
with open("sample-documents/your-file.pdf", "rb") as f:
    poller = client.begin_analyze_document("prebuilt-invoice", body=f)
```

## File Size Limits

| Tier | Max File Size | Max Pages |
|---|---|---|
| Free (F0) | 4 MB | 2 pages |
| Standard (S0) | 500 MB | 2,000 pages |

## Supported Formats

- **PDF** — including scanned PDFs
- **Images** — JPEG/JPG, PNG, BMP, TIFF, HEIF
- **Microsoft Office** — DOCX, PPTX, XLSX (Read and Layout models only)
