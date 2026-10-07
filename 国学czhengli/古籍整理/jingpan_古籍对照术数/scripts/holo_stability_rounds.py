#!/usr/bin/env python3
"""Run holo_auto_tune N times; always continue on failure; print summary."""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
N = int(sys.argv[1]) if len(sys.argv) > 1 else 3


def main() -> int:
    results: list[str] = []
    for i in range(1, N + 1):
        print(f'===== ROUND {i}/{N} =====', flush=True)
        proc = subprocess.run(
            [sys.executable, str(ROOT / 'scripts' / 'holo_auto_tune.py')],
            cwd=str(ROOT),
        )
        tag = 'PASS' if proc.returncode == 0 else f'FAIL({proc.returncode})'
        results.append(tag)
        print(f'ROUND {i}: {tag}', flush=True)
    print('SUMMARY', results, flush=True)
    ok = sum(1 for r in results if r == 'PASS')
    print(f'PASS_RATE {ok}/{N}', flush=True)
    return 0 if ok == N else 1


if __name__ == '__main__':
    raise SystemExit(main())
