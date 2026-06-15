"""Workshop configuration loaded from environment / .env file."""

from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings.

    The workshop targets **Microsoft Foundry** via the Microsoft Agent
    Framework. A single Foundry project endpoint is all that's needed —
    auth is always Entra ID via ``DefaultAzureCredential`` (``az login``
    locally, Managed Identity in production).
    """

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    # OPA server
    opa_url: str = Field(default="http://localhost:8181")

    # Microsoft Foundry project (consumed as-is by MAF's FoundryChatClient).
    foundry_project_endpoint: str = Field(default="")
    model_deployment_name: str = Field(default="gpt-4o")
    # MAF's OpenAIChatClient targets the new /openai/v1/ surface, which only
    # accepts api_version=preview or =latest (not dated previews).
    model_api_version: str = Field(default="preview")

    # Audit log
    enable_policy_audit: bool = Field(default=True)
    policy_audit_log_path: str = Field(default="./logs/policy-audit.jsonl")

    # Tracing (OpenTelemetry / Foundry Toolkit trace viewer)
    enable_tracing: bool = Field(default=False)
    otel_exporter_otlp_endpoint: str = Field(default="http://localhost:4317")

    def has_llm(self) -> bool:
        return bool(self.foundry_project_endpoint)

    def chat_endpoint(self) -> str:
        """Return a base URL suitable for MAF's ``OpenAIChatClient``.

        The Foundry project endpoint (``<account>.services.ai.azure.com/...``)
        is the right value for ``AIProjectClient`` / ``FoundryChatClient``,
        but ``OpenAIChatClient`` is a generic OpenAI-compatible client and
        expects the Azure OpenAI **data-plane** base URL
        (``<account>.openai.azure.com``). Same account, different host —
        rewrite the project URL to the data-plane URL so MAF can call
        ``/openai/v1/chat/completions`` directly.
        """
        ep = (self.foundry_project_endpoint or "").rstrip("/")
        if not ep:
            return ""
        for marker in (".services.ai.azure.com", ".cognitiveservices.azure.com"):
            if marker in ep:
                account = ep.split(marker, 1)[0]  # "https://<account>"
                return f"{account}.openai.azure.com"
        return ep


@lru_cache
def get_settings() -> Settings:
    return Settings()
