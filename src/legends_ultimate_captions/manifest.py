"""Manifest helpers for caption policy decisions."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from .policy import PolicyResult, decisions_as_dicts


def build_policy_manifest(result: PolicyResult, source: str | None = None) -> dict[str, Any]:
    return {
        "schema": "legends_ultimate_captions.policy_manifest.v1",
        "created_utc": datetime.now(timezone.utc).isoformat(),
        "source": source,
        "normalized_text": result.text,
        "caption_text": result.caption_text(uppercase=True),
        "decisions": decisions_as_dicts(result.decisions),
    }

