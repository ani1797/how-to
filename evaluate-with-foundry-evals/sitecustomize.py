"""Reasoning-model compatibility shim for azure-ai-evaluation.

Reasoning judge models (gpt-5.x, o-series) reject the `max_tokens` parameter
(they require `max_completion_tokens`) and only allow the default temperature.
azure-ai-evaluation's built-in evaluators still send `max_tokens`, so this shim
rewrites outgoing chat-completion parameters on the OpenAI client.

Placed on `sitecustomize.py`, Python auto-imports it at interpreter startup —
including the worker processes azure-ai-evaluation spawns to run evaluators.
It is a no-op for classic models (gpt-4o, gpt-4.1), so it is always safe.
"""
try:
    import openai.resources.chat.completions as _c

    def _wrap(orig):
        def create(self, *args, **kwargs):
            if "max_tokens" in kwargs:
                kwargs["max_completion_tokens"] = kwargs.pop("max_tokens")
            if kwargs.get("temperature") not in (None, 1):
                kwargs.pop("temperature", None)
            return orig(self, *args, **kwargs)

        return create

    if not getattr(_c.Completions.create, "_foundry_shim", False):
        _c.Completions.create = _wrap(_c.Completions.create)
        _c.Completions.create._foundry_shim = True
        _c.AsyncCompletions.create = _wrap(_c.AsyncCompletions.create)
        _c.AsyncCompletions.create._foundry_shim = True
except Exception:
    pass
