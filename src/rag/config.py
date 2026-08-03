"""Safe runtime configuration for the RAG layer."""

from __future__ import annotations

import importlib.util
import os
from dataclasses import dataclass
from pathlib import Path

from src.ingestion.io import get_repo_root


@dataclass(frozen=True)
class RagConfig:
    provider: str
    api_key_present: bool
    base_url: str | None
    model: str
    openai_available: bool
    dotenv_loaded: bool

    @property
    def real_llm_available(self) -> bool:
        return self.api_key_present and self.openai_available and self.provider != "mock"


def _load_dotenv_if_available() -> bool:
    dotenv_path = get_repo_root() / ".env"
    if not dotenv_path.exists():
        return False
    if importlib.util.find_spec("dotenv") is None:
        return False
    from dotenv import load_dotenv

    load_dotenv(dotenv_path=Path(dotenv_path), override=False)
    return True


def load_config() -> RagConfig:
    dotenv_loaded = _load_dotenv_if_available()
    provider = os.getenv("LLM_PROVIDER", "mock").strip() or "mock"
    api_key_present = bool((os.getenv("LLM_API_KEY") or "").strip())
    base_url = (os.getenv("LLM_BASE_URL") or "").strip() or None
    model = os.getenv("LLM_MODEL", "mock-supportlens").strip() or "mock-supportlens"
    openai_available = importlib.util.find_spec("openai") is not None
    return RagConfig(
        provider=provider,
        api_key_present=api_key_present,
        base_url=base_url,
        model=model,
        openai_available=openai_available,
        dotenv_loaded=dotenv_loaded,
    )