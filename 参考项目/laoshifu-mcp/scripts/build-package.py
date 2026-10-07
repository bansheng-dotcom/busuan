#!/usr/bin/env python3
"""Build the wheel/sdist and refuse to hand over an incomplete package.

Checks that the bundled runtime is present and clean, builds the distributions,
then re-opens the wheel to confirm the engines really travelled with it.
"""
from __future__ import annotations

import hashlib
import json
import shutil
import subprocess
import sys
import tomllib
import zipfile
from datetime import datetime, timezone
from pathlib import Path

PACKAGE_ROOT = Path(__file__).resolve().parents[1]
DIST = PACKAGE_ROOT / "dist"
BUNDLE = PACKAGE_ROOT / "laoshifu_mcp" / "_runtime"

MUST_BE_IN_WHEEL = (
    "laoshifu_mcp/server.py",
    "laoshifu_mcp/runtime.py",
    "laoshifu_mcp/_runtime/scripts/chart_bazi_ziwei.py",
    "laoshifu_mcp/_runtime/scripts/liuyao_qimen_fusion.py",
    "laoshifu_mcp/_runtime/scripts/diagram_render.py",
    "laoshifu_mcp/_runtime/scripts/resolve-pillars.cjs",
    "laoshifu_mcp/_runtime/scripts/diagram-assets/glyphs.json",
    "laoshifu_mcp/_runtime/engine/calculator/dist/run-chart.js",
    "laoshifu_mcp/_runtime/references/qimen/jiuxing.json",
)

MUST_NOT_BE_IN_WHEEL = (
    "laoshifu_mcp/_runtime/SKILL.md",
    "laoshifu_mcp/_runtime/VOICE-SAMPLES.md",
)

# A standalone repository keeps the runtime committed, so ModelScope can build
# straight from GitHub without the parent Skill checkout.
MUST_BE_IN_REPO = (
    "laoshifu_mcp/_runtime/engine/calculator/dist/run-chart.js",
    "laoshifu_mcp/_runtime/scripts/node_modules/mingyu-core/dist/index.js",
    "laoshifu_mcp/_runtime/references/qimen/jiuxing.json",
)

# Root-anchored on purpose: vendored npm packages have their own dist/ and
# build/ directories and those are exactly the files the engines import.
REPO_IGNORE = """\
/.venv/
/build/
/dist/
/*.egg-info/
__pycache__/
*.pyc
*.pyo
.pytest_cache/
"""

# Only the top-level build artefacts are dropped: vendored npm packages legitimately
# contain directories called build/ or dist/ of their own.
REPO_TOP_EXCLUDE = {".venv", "build", "dist", "laoshifu_mcp.egg-info"}
REPO_ANY_EXCLUDE = {"__pycache__", ".pytest_cache", ".git"}


def run(argv: list[str]) -> None:
    proc = subprocess.run(argv, cwd=PACKAGE_ROOT, text=True, capture_output=True)
    if proc.returncode:
        sys.stderr.write(proc.stdout + proc.stderr)
        raise SystemExit(f"[STOP] 命令失败：{' '.join(argv)}")


def make_repo(target: Path) -> int:
    """Emit a self-contained, git-ready tree with the runtime committed."""
    if target.exists():
        shutil.rmtree(target)
    target.mkdir(parents=True)
    for item in sorted(PACKAGE_ROOT.rglob("*")):
        rel = item.relative_to(PACKAGE_ROOT)
        if rel.parts[0] in REPO_TOP_EXCLUDE or set(rel.parts) & REPO_ANY_EXCLUDE:
            continue
        if item.is_dir():
            continue
        if item.suffix in {".pyc", ".pyo"}:
            continue
        if rel.name == ".gitignore":
            continue
        dst = target / rel
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(item, dst)
    (target / ".gitignore").write_text(REPO_IGNORE, encoding="utf-8")
    missing = [rel for rel in MUST_BE_IN_REPO if not (target / rel).is_file()]
    if missing:
        raise SystemExit("[STOP] 独立仓库树缺少引擎文件：" + ", ".join(missing))
    return sum(1 for p in target.rglob("*") if p.is_file())


def main() -> int:
    if not BUNDLE.is_dir():
        raise SystemExit("[STOP] 缺少 _runtime，先运行 python scripts/sync-runtime.py --force")
    run([sys.executable, str(PACKAGE_ROOT / "scripts" / "sync-runtime.py"), "--check"])
    run([sys.executable, str(PACKAGE_ROOT / "scripts" / "verify-bundle.py")])

    if DIST.exists():
        shutil.rmtree(DIST)
    run([sys.executable, "-m", "build", "--outdir", str(DIST)])

    wheels = sorted(DIST.glob("*.whl"))
    if len(wheels) != 1:
        raise SystemExit(f"[STOP] 期望 1 个 wheel，实际 {len(wheels)} 个")
    wheel = wheels[0]

    with zipfile.ZipFile(wheel) as archive:
        names = set(archive.namelist())
        missing = [name for name in MUST_BE_IN_WHEEL if name not in names]
        if missing:
            raise SystemExit("[STOP] wheel 缺少运行时文件：" + ", ".join(missing))
        leaked = [name for name in MUST_NOT_BE_IN_WHEEL if name in names]
        if leaked:
            raise SystemExit("[STOP] wheel 混入会谈断法资料：" + ", ".join(leaked))
        runtime_files = sum(1 for name in names if "_runtime/" in name)

    archives = [
        {
            "name": path.name,
            "bytes": path.stat().st_size,
            "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
        }
        for path in sorted(DIST.iterdir())
        if path.is_file()
    ]
    repo_dir = DIST / "laoshifu-mcp-repo"

    # The repo tree has to exist before the manifest is written, but dist/ is
    # excluded from the copy, so build it first and record it as a directory.
    repo_files = make_repo(repo_dir)
    repo_bytes = sum(p.stat().st_size for p in repo_dir.rglob("*") if p.is_file())

    manifest = {
        "builtAt": datetime.now(timezone.utc).astimezone().isoformat(),
        "version": tomllib.loads(
            (PACKAGE_ROOT / "pyproject.toml").read_text(encoding="utf-8")
        )["project"]["version"],
        "runtimeFiles": runtime_files,
        "archives": archives,
        "standaloneRepo": {
            "path": str(repo_dir),
            "files": repo_files,
            "bytes": repo_bytes,
        },
        "published": False,
    }
    (DIST / "manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print(
        f"[OK] {wheel.name} 含 {runtime_files} 个运行时文件，"
        f"{wheel.stat().st_size / 1048576:.2f} MB，未发布。"
    )
    print(
        f"     独立仓库树 {repo_files} 个文件 / {repo_bytes / 1048576:.1f} MB -> {repo_dir}"
    )
    print("     产物目录：" + str(DIST))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
