from typing import List

import httpx


class Ollama:
    def __init__(self, url: str = "http://localhost:11434") -> None:
        self.url = url

    @property
    def models(self):
        response = httpx.get(f"{self.url}/api/tags")
        return list(map(lambda model: model.get("name"), response.json().get("models")))

    def completion(self, message: str, model: str = "mistral:latest"):
        response = httpx.post(
            f"{self.url}/api/generate",
            json={"model": model, "prompt": message, "stream": False},
            timeout=240,
        )
        return response.json().get("response")

    def chat(self, messages: List, model: str = "mistral:latest"):
        response = httpx.post(
            f"{self.url}/api/chat",
            json={"model": model, "messages": messages, "stream": False},
            timeout=240,
        )
        return response

    def embedding(self, text: str, model: str = "mistral:latest"):
        response = httpx.post(
            f"{self.url}/api/embeddings",
            json={"model": model, "prompt": text},
            timeout=240,
        )
        return response.json().get("embedding")
