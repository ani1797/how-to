# Evaluate with Foundry Evals — Walkthrough Course

A bite-sized, notebook-based course on **evaluating GenAI apps on Azure AI Foundry**
using the [`azure-ai-evaluation`](https://pypi.org/project/azure-ai-evaluation/) SDK.
It closes with a documented pattern for **automated evaluation in CI** using the
[GenAI Evaluation GitHub Action](https://github.com/marketplace/actions/generative-ai-evaluation-action).

All examples use Insurance and Banking use cases to keep things relatable.

## Notebooks

| # | Notebook | What you'll learn |
|---|----------|-------------------|
| 00 | Setup & Basics | What evaluation is, the data schema, your first `evaluate()` run |
| 01 | NLP / Local Evaluators | Deterministic, free metrics — F1, BLEU, ROUGE, METEOR, GLEU |
| 02 | AI-Assisted Quality | LLM-judged metrics — relevance, coherence, fluency, groundedness, `QAEvaluator` |
| 03 | Risk & Safety | Foundry-backed safety — content safety, protected material, indirect attack |
| 04 | Custom Evaluators | Code-based and Prompty prompt-based evaluators |
| 05 | Evaluating a Target | Score a live app with `target=` and `column_mapping` |
| 06 | Cloud & Foundry Evaluation | Log runs to Foundry, view in the portal, remote runs |
| 07 | CI Automated Evaluation | Gate PRs with the GenAI Evaluation GitHub Action (docs-only) |

## Setup

```bash
# 1. Enter the workshop
cd evaluate-with-foundry-evals

# 2. Copy the env template and fill in your Foundry + judge model details
cp .env.example .env

# 3. Install dependencies with uv
uv sync

# 4. Login to Azure (Entra ID auth — no keys needed for local evaluators)
az login

# 5. Open any notebook and run it
```

## Prerequisites

- Python 3.10+
- [uv](https://docs.astral.sh/uv/) installed
- Azure CLI (`az`) installed and logged in
- An Azure AI Foundry project (for cloud logging + risk/safety evaluators)
- An Azure OpenAI chat deployment to act as the **judge model**

### Judge model & reasoning-model compatibility

AI-assisted evaluators need a chat deployment set as `AZURE_OPENAI_DEPLOYMENT` in
your `.env`. Both classic (`gpt-4o`, `gpt-4.1`) and **reasoning** models
(`gpt-5.x`, o-series) work:

- Reasoning models reject `max_tokens` (they require `max_completion_tokens`) and
  only allow the default temperature.
- `azure-ai-evaluation`'s built-in evaluators still send `max_tokens`, so the
  workshop ships [`sitecustomize.py`](./sitecustomize.py) — a tiny shim that rewrites
  those parameters. The notebooks' setup cell copies it into your venv's
  site-packages automatically so it also loads in the evaluator worker processes.
  It is a no-op for classic models, so nothing to configure.

> `openai` is pinned to `<2` because openai 2.x regressed Entra ID
> token-provider auth used by the judge model.

### What each evaluator kind needs

| Kind | Needs | Notebooks |
|------|-------|-----------|
| NLP / local | nothing (deterministic) | 01 |
| AI-assisted quality | a judge `model_config` | 02, 04, 05 |
| Risk & safety | an `azure_ai_project` (Foundry) | 03, 06 |

## CI: automated evaluation

Notebook 07 walks through running evaluation in GitHub Actions. The reference files
live in [`ci-example/`](./ci-example/):

- [`evaluate.yml`](./ci-example/evaluate.yml) — the workflow (OIDC login + `microsoft/genai-evals`)
- [`evaluate-config.json`](./ci-example/evaluate-config.json) — evaluators + judge model config
- [`eval-input.jsonl`](./ci-example/eval-input.jsonl) — the test dataset

> These files sit **outside** `.github/workflows/` on purpose, so nothing runs
> automatically in this repo. Copy them into your own repository to wire up CI, and
> gate on `paths:` / small datasets to control judge-model cost.
