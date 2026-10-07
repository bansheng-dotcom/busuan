#!/usr/bin/env python3
"""Talk to the server over real MCP stdio transport, the way a host client does.

This is the contract test: if a host can list the tools and pull a chart and a
hexagram through stdio, the same package works when ModelScope or any other
host spawns it.
"""
from __future__ import annotations

import asyncio
import json
import os
import sys
from pathlib import Path

from mcp import ClientSession
from mcp.client.stdio import StdioServerParameters, stdio_client

PACKAGE_ROOT = Path(__file__).resolve().parents[1]


async def run() -> int:
    env = {
        **os.environ,
        "PYTHONPATH": str(PACKAGE_ROOT),
        "PYTHONUTF8": "1",
        "LAOSHIFU_MCP_TRANSPORT": "stdio",
    }
    params = StdioServerParameters(
        command=sys.executable,
        args=["-m", "laoshifu_mcp"],
        env=env,
        cwd=str(PACKAGE_ROOT),
    )
    async with stdio_client(params) as (read, write):
        async with ClientSession(read, write) as session:
            init = await session.initialize()
            print(f"[1/4] 握手成功 {init.server_info.name} v{init.server_info.version}")

            tools = await session.list_tools()
            names = [tool.name for tool in tools.tools]
            print(f"[2/4] 工具 {len(names)} 个：{', '.join(names)}")

            chart = await session.call_tool(
                "bazi_ziwei_chart",
                {
                    "year": 2000,
                    "month": 1,
                    "day": 1,
                    "hour": 12,
                    "gender": "male",
                    "calendar": "solar",
                    "current_year": 2026,
                },
            )
            payload = json.loads(chart.content[0].text)
            print(
                f"[3/4] 八字紫微 {payload['pillars']['formatted']}"
                f" / 十二宫 {len(payload['ziwei']['gongs'])}"
                f" / 返回 {len(chart.content[0].text)} 字符"
            )

            event = await session.call_tool(
                "hexagram_diagram",
                {
                    "question": "打包校验用固定问题：这份合同月底前会不会签下来？",
                    "method": "numbers",
                    "numbers": [12, 35, 8],
                    "category": "career",
                    "year": 2026,
                    "month": 9,
                    "day": 17,
                    "hour": 10,
                    "minute": 30,
                },
            )
            kinds = [type(item).__name__ for item in event.content]
            image = next(
                (item for item in event.content if type(item).__name__ == "ImageContent"), None
            )
            print(
                f"[4/4] 六爻卦图 {kinds} / PNG {len(image.data) // 1024 if image else 0} KB(base64)"
            )
            assert kinds.count("ImageContent") == 1, "卦图未通过 stdio 传输"
    print("[OK] MCP stdio 契约通过。")
    return 0


if __name__ == "__main__":
    raise SystemExit(asyncio.run(run()))
