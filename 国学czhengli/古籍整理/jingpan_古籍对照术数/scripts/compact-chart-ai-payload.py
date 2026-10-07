#!/usr/bin/env python3
"""Print compact payload for Doubao / local testing. Usage:
  python3 scripts/compact-chart-ai-payload.py path/to/raw.json
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'server'))

# Import without starting server
import importlib.util

spec = importlib.util.spec_from_file_location(
    'chart_ai_proxy',
    ROOT / 'server' / 'chart_ai_proxy.py',
)
mod = importlib.util.module_from_spec(spec)
assert spec.loader
# Provide __file__ for ENV path
sys.modules['chart_ai_proxy'] = mod
spec.loader.exec_module(mod)

raw_path = Path(sys.argv[1]) if len(sys.argv) > 1 else None
if not raw_path or not raw_path.is_file():
    print('usage: compact-chart-ai-payload.py <raw.json>', file=sys.stderr)
    sys.exit(1)

raw = json.loads(raw_path.read_text(encoding='utf-8'))
compact = mod.compact_holographic_payload(raw)
print(json.dumps(compact, ensure_ascii=False, indent=2))
print('---', file=sys.stderr)
print(f'chars={len(json.dumps(compact, ensure_ascii=False))}', file=sys.stderr)
print(f'decades={len(compact.get("decades") or [])} palaces={len(compact.get("palaces") or [])}', file=sys.stderr)
