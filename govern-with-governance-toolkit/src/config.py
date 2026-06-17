"""Workshop configuration loaded from environment / .env file."""
from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings.

    The workshop targets **Microsoft Foundry** via the Microsoft Agent
    Framework. A single Foundry project endpoint is all that is needed —
    auth is always Entra ID via ``DefaultAzureCredential`` (``az login``
    locally, Managed Identity in production).
    """

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    # Microsoft Foundry project
    foundry_project_endpoint: str = Field(default="")
    model_deployment_name: str = Field(default="gpt-4o")
    model_api_version: str = Field(default="preview")

    # Governance (AGT)
    governance_audit_log_path: str = Field(default="./logs/governance-audit.jsonl")
    governance_policy_dir: str = Field(default="./src/policies")
    enable_policy_audit: bool = Field(default=True)

    # Tracing (OpenTelemetry / Foundry Toolkit trace viewer)
    enable_tracing: bool = Field(default=False)
    otel_exporter_otlp_endpoint: str = Field(default="http://localhost:4317")

    def has_llm(self) -> bool:
        return bool(self.foundry_project_endpoint)

    def chat_endpoint(self) -> str:
        """Return a base URL suitable for MAF's ``OpenAIChatClient``."""
        ep = (self.foundry_project_endpoint or "").rstrip("/")
        if not ep:
            return ""
        for marker in (".services.ai.azure.com", ".cognitiveservices.azure.com"):
            if marker in ep:
                account = ep.split(marker, 1)[0]
                return f"{account}.openai.azure.com"
        return ep


@lru_cache
def get_settings() -> Settings:
    return Settings()
