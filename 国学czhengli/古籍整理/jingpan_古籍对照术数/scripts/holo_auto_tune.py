#!/usr/bin/env python3
"""Call holographic API with a fixture, score with local guards, print issues."""
from __future__ import annotations

import json
import re
import sys
import urllib.error
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'server'))
import chart_ai_proxy as cap  # noqa: E402

FIXTURE = ROOT / 'server' / 'fixtures' / 'holo-sample-1996.json'
OUT = ROOT / 'server' / 'fixtures' / 'holo-last-response.json'
API = 'http://127.0.0.1:8787/api/chart-ai-holographic'


HARD_ISSUE_NAMES = {
    'style',
    'evidence',
    'invented_flow',
    'json_leak',
    'clinical',
    'child_romance',
    'ming_contradiction',
    'star_palace',
    'pattern_name',
    'wenqu_lie',
    'decade_jump',
    'decade_horizon',
    'adult_grown_up',
    'decade_spam',
}


def score(content: str, compact: dict, allowed_flow: set[str]) -> list[str]:
    issues: list[str] = []
    checks = [
        ('style', lambda: cap.violates_holographic_style(content)),
        ('evidence', lambda: cap.holographic_evidence_thin(content)),
        ('invented_flow', lambda: cap.holographic_invented_flow(content, allowed_flow)),
        ('json_leak', lambda: cap.holographic_json_leak(content)),
        ('clinical', lambda: cap.holographic_clinical_terms(content)),
        ('child_romance', lambda: cap.holographic_child_romance_tone(content, compact)),
        ('ming_contradiction', lambda: cap.holographic_ming_contradiction(content, compact)),
        ('star_palace', lambda: cap.holographic_star_palace_mismatch(content, compact)),
        ('pattern_name', lambda: cap.holographic_pattern_name_mismatch(content, compact)),
        ('wenqu_lie', lambda: cap.holographic_wenqu_location_lie(content, compact)),
        ('decade_jump', lambda: cap.holographic_decade_jump(content, compact)),
        ('decade_horizon', lambda: cap.holographic_near_horizon_overflow(content, compact)),
        ('adult_grown_up', lambda: cap.holographic_adult_grown_up_tone(content, compact)),
        ('decade_spam', lambda: cap.holographic_decade_year_spam(content)),
    ]
    for name, fn in checks:
        try:
            if fn():
                issues.append(name)
        except Exception as exc:  # noqa: BLE001
            issues.append(f'{name}:ERR:{exc}')
    # soft quality heuristics (not hard reject)
    if '长大后' in content and (compact.get('meta') or {}).get('lifeStage') == 'adult':
        if 'adult_grown_up' not in issues:
            issues.append('adult_grown_up_soft')
    if '事业宫紫微天府' in content or '官禄宫紫微天府' in content:
        issues.append('wrong_tianfu_in_career')
    if '府相朝垣' in content and '武曲天府' in content:
        if not re.search(
            r'(?:禁止|勿称|勿稱|并非|並非|不是|以为|以為|便是「|不算|不可称|不能称).{0,24}府相朝垣|'
            r'府相朝垣.{0,24}(?:其实|其實|而非|必须|必須|才算|才是)',
            content,
        ):
            issues.append('wrong_fuxiang_pattern')
    if '文星朝命' in content:
        ming_names = []
        for p in compact.get('palaces') or []:
            if isinstance(p, dict) and (p.get('isMing') or p.get('palace') in ('命宫', '命宮')):
                ming_names = [str(s.get('name') or '') for s in (p.get('stars') or []) if isinstance(s, dict)]
                break
        if '文昌' not in ming_names and not re.search(
            r'(?:禁止|勿称|勿稱|并非|並非|不是|以为|以為|便是「).{0,20}文星朝命|'
            r'文星朝命.{0,20}(?:其实|其實|而非)',
            content,
        ):
            issues.append('wrong_wenxing_pattern')
    if '投资需谨慎' in content or '忌投机' in content:
        issues.append('invest_advice_soft')
    # 时空章首 280 字内出现虚岁/大限年龄锚点即可（允许先写公历年）
    temporal = content.split('## 时空战略', 1)[-1][:280] if '## 时空战略' in content else ''
    if temporal and not re.search(r'虚岁|虛歲|\d{1,2}\s*[-–—～~]\s*\d{1,2}', temporal):
        issues.append('temporal_age_anchor_soft')
    return issues


def split_issues(issues: list[str]) -> tuple[list[str], list[str]]:
    hard: list[str] = []
    soft: list[str] = []
    for item in issues:
        base = item.split(':', 1)[0]
        if base in HARD_ISSUE_NAMES:
            hard.append(item)
        else:
            soft.append(item)
    return hard, soft


def main() -> int:
    if not FIXTURE.is_file():
        print('MISSING_FIXTURE', FIXTURE)
        return 2
    payload = json.loads(FIXTURE.read_text(encoding='utf-8'))
    compact = cap.compact_holographic_payload(payload)
    allowed = cap.collect_allowed_flow_stars(compact)
    body = json.dumps(payload, ensure_ascii=False).encode('utf-8')
    req = urllib.request.Request(
        API,
        data=body,
        headers={'Content-Type': 'application/json'},
        method='POST',
    )
    try:
        with urllib.request.urlopen(req, timeout=300) as resp:
            data = json.loads(resp.read().decode('utf-8'))
            status = resp.status
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode('utf-8', errors='replace')
        try:
            data = json.loads(detail)
        except json.JSONDecodeError:
            data = {'error': detail}
        status = exc.code
        OUT.write_text(json.dumps({'status': status, **data}, ensure_ascii=False, indent=2), encoding='utf-8')
        print(f'STATUS={status}')
        print('ERROR=', data.get('error', data))
        return 1

    content = str(data.get('content') or '')
    OUT.write_text(
        json.dumps({'status': status, 'content': content, 'ageGuide': compact.get('ageGuide')}, ensure_ascii=False, indent=2),
        encoding='utf-8',
    )
    issues = score(content, compact, allowed)
    hard, soft = split_issues(issues)
    print(f'STATUS={status}')
    print(f'LEN={len(content)}')
    print(f'AGE_GUIDE={json.dumps(compact.get("ageGuide"), ensure_ascii=False)}')
    print(f'HARD={hard or ["none"]}')
    print(f'SOFT={soft or ["none"]}')
    # print first/last headings for quick glance
    for line in content.splitlines():
        if line.startswith('##') or line.startswith('**🔴') or line.startswith('**🟡') or line.startswith('**🟢'):
            print('H:', line[:120])
    # 仅硬门槛失败才非 0；软质量只作提示
    return 0 if not hard else 3


if __name__ == '__main__':
    raise SystemExit(main())
