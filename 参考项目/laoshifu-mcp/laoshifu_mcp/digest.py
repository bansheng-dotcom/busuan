"""Bound tool output size without dropping the parts a reading actually needs.

The raw 排盘/起卦 JSON is kept intact by the engines; these helpers only remove
duplicated blocks so a tool result stays inside a sane context budget.
"""
from __future__ import annotations

import copy
from typing import Any

MAX_JSON_CHARS = 60_000

# chart.json repeats the same birth data and four pillars across bazi/ziwei.
_CHART_DUPLICATE_KEYS = {
    "bazi": ("birthInfo", "siZhu", "dayun"),
    "ziwei": ("birthInfo", "siZhu"),
}


def chart_summary(chart: dict) -> dict:
    """Core chart: 四柱、八字 enrichment、紫微十二宫、大运、流年、证据摘要."""
    summary = copy.deepcopy(chart)
    for section, keys in _CHART_DUPLICATE_KEYS.items():
        block = summary.get(section)
        if isinstance(block, dict):
            for key in keys:
                block.pop(key, None)
    meta = summary.get("meta")
    if isinstance(meta, dict) and isinstance(meta.get("input"), dict):
        # The top-level input already carries calendar/gender/timeZone.
        meta.pop("normalizedSolarInput", None)
    return summary


def chart_payload(chart: dict, detail: str) -> dict:
    return chart if detail == "full" else chart_summary(chart)


def fusion_payload(fusion: dict, detail: str) -> dict:
    """Drop only the deprecated legacy diagram blob; keep both method verdicts."""
    if detail == "full":
        return fusion
    payload = copy.deepcopy(fusion)
    payload.pop("diagram", None)
    return payload


def clamp_text(text: str, limit: int = MAX_JSON_CHARS) -> str:
    if len(text) <= limit:
        return text
    return text[:limit] + "\n…（结果过长已截断，可用 detail=full 或分段索取）"


def as_text(payload: Any) -> str:
    import json

    # Compact separators keep a full chart inside a sane context budget; the
    # payload is already grouped by section, so no indentation is needed.
    return clamp_text(json.dumps(payload, ensure_ascii=False, separators=(",", ":")))
