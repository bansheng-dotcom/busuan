"""Locate the bundled Laoshifu engine runtime and run its scripts.

The MCP server never re-implements 排盘/起卦. It shells out to the same
authoritative engines that ship with the Skill, so tool output and Skill
output can never drift apart.
"""
from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ENV_ROOT = "LAOSHIFU_ENGINE_ROOT"
ENV_NODE = "LAOSHIFU_NODE"

_THIS = Path(__file__).resolve()

CHART_SCRIPT = "scripts/chart_bazi_ziwei.py"
FUSION_SCRIPT = "scripts/liuyao_qimen_fusion.py"
DIAGRAM_SCRIPT = "scripts/diagram_render.py"
PILLARS_SCRIPT = "scripts/resolve-pillars.cjs"
ENGINE_ENTRY = "engine/calculator/dist/run-chart.js"
QIMEN_DATA = "references/qimen/jiuxing.json"

_REQUIRED = (
    CHART_SCRIPT,
    FUSION_SCRIPT,
    DIAGRAM_SCRIPT,
    PILLARS_SCRIPT,
    ENGINE_ENTRY,
    QIMEN_DATA,
)


class EngineError(RuntimeError):
    """Raised when the bundled runtime is missing or a script fails."""


def _is_engine_root(path: Path) -> bool:
    return all((path / rel).is_file() for rel in _REQUIRED)


def engine_root() -> Path:
    """Resolve the engine root: env override, packaged runtime, then repo dev tree."""
    candidates: list[Path] = []
    override = os.environ.get(ENV_ROOT)
    if override:
        candidates.append(Path(override).expanduser())
    candidates.append(_THIS.parent / "_runtime")
    # <repo>/channels/modelscope-mcp/laoshifu_mcp/runtime.py -> <repo>
    candidates.append(_THIS.parents[3] if len(_THIS.parents) > 3 else _THIS.parent)
    for candidate in candidates:
        resolved = candidate.resolve()
        if _is_engine_root(resolved):
            return resolved
    tried = ", ".join(str(c) for c in candidates)
    raise EngineError(
        "找不到老师傅排盘引擎。请设置 " + ENV_ROOT + f" 指向包含 {CHART_SCRIPT} 的目录。已尝试: {tried}"
    )


def node_binary() -> str:
    configured = os.environ.get(ENV_NODE)
    if configured and Path(configured).exists():
        return configured
    for name in ("node", "nodejs"):
        found = shutil.which(name)
        if found:
            return found
    for candidate in (
        "/usr/local/bin/node",
        "/usr/bin/node",
        "/opt/node/bin/node",
    ):
        if Path(candidate).exists():
            return candidate
    raise EngineError("找不到 Node.js 运行时；请安装 Node.js 或设置 " + ENV_NODE)


def _run(argv: list[str], cwd: Path, timeout: int) -> str:
    env = dict(os.environ)
    env.setdefault("PYTHONUTF8", "1")
    env.setdefault("PYTHONIOENCODING", "utf-8")
    env.setdefault("LC_ALL", "C.UTF-8")
    try:
        proc = subprocess.run(
            argv,
            cwd=str(cwd),
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=timeout,
            env=env,
        )
    except subprocess.TimeoutExpired as exc:
        raise EngineError(f"排盘引擎超时（{timeout}s）") from exc
    if proc.returncode != 0:
        detail = (proc.stderr or proc.stdout or "").strip().splitlines()
        tail = " / ".join(detail[-3:]) if detail else f"退出码 {proc.returncode}"
        raise EngineError(f"排盘引擎执行失败：{tail}")
    return proc.stdout


def _read_json(path: Path) -> dict:
    if not path.is_file():
        raise EngineError(f"排盘引擎未生成结果文件：{path.name}")
    try:
        payload = json.loads(path.read_text(encoding="utf-8-sig"))
    except json.JSONDecodeError as exc:
        raise EngineError(f"结果文件不是合法 JSON：{path.name}") from exc
    if not isinstance(payload, dict) or not payload:
        raise EngineError(f"结果文件为空：{path.name}")
    return payload


def bazi_ziwei_chart(
    *,
    year: int,
    month: int,
    day: int,
    hour: int,
    minute: int,
    gender: str,
    calendar: str,
    is_leap_month: bool,
    time_zone: int,
    current_year: int,
) -> dict:
    root = engine_root()
    with tempfile.TemporaryDirectory(prefix="laoshifu-chart-") as work:
        out = Path(work) / "chart.json"
        argv = [
            sys.executable,
            str(root / CHART_SCRIPT),
            f"--year={year}",
            f"--month={month}",
            f"--day={day}",
            f"--hour={hour}",
            f"--minute={minute}",
            f"--gender={gender}",
            f"--calendar={calendar}",
            f"--isLeapMonth={'true' if is_leap_month else 'false'}",
            f"--timeZone={time_zone}",
            f"--currentYear={current_year}",
            f"--output={out}",
        ]
        _run(argv, root, timeout=90)
        return _read_json(out)


def liuyao_qimen_fusion(
    *,
    question: str,
    category: str,
    method: str,
    numbers: list[int] | None,
    year: int,
    month: int,
    day: int,
    hour: int,
    minute: int,
    time_zone: int,
) -> dict:
    root = engine_root()
    with tempfile.TemporaryDirectory(prefix="laoshifu-event-") as work:
        out = Path(work) / "fusion.json"
        argv = [
            sys.executable,
            str(root / FUSION_SCRIPT),
            f"--question={question}",
            f"--category={category}",
            f"--method={method}",
            f"--year={year}",
            f"--month={month}",
            f"--day={day}",
            f"--hour={hour}",
            f"--minute={minute}",
            f"--timeZone={time_zone}",
            f"--output={out}",
        ]
        if method == "numbers":
            argv.append("--numbers=" + ",".join(str(n) for n in (numbers or [])))
        _run(argv, root, timeout=90)
        return _read_json(out)


def hexagram_diagram(fusion: dict) -> dict:
    """Render the standard six-line diagram PNG plus its per-line text fallback."""
    root = engine_root()
    with tempfile.TemporaryDirectory(prefix="laoshifu-diagram-") as work:
        work_path = Path(work)
        fusion_path = work_path / "fusion.json"
        fusion_path.write_text(json.dumps(fusion, ensure_ascii=False), encoding="utf-8")
        out = work_path / "diagram-output"
        argv = [
            sys.executable,
            str(root / DIAGRAM_SCRIPT),
            f"--fusion={fusion_path}",
            f"--out={out}",
        ]
        _run(argv, root, timeout=90)
        png = out / "diagram.png"
        if not png.is_file():
            raise EngineError("卦图渲染未生成 PNG")
        fallback = out / "fallback.txt"
        manifest = out / "manifest.json"
        return {
            "image": png.read_bytes(),
            "fallback_text": fallback.read_text(encoding="utf-8").strip() if fallback.is_file() else "",
            "manifest": json.loads(manifest.read_text(encoding="utf-8")) if manifest.is_file() else {},
        }


def resolve_pillars(*, pillars: str, start_year: int, end_year: int) -> dict:
    root = engine_root()
    with tempfile.TemporaryDirectory(prefix="laoshifu-pillars-") as work:
        out = Path(work) / "candidates.json"
        argv = [
            node_binary(),
            str(root / PILLARS_SCRIPT),
            f"--pillars={pillars}",
            f"--startYear={start_year}",
            f"--endYear={end_year}",
            f"--output={out}",
        ]
        _run(argv, root, timeout=90)
        return _read_json(out)
