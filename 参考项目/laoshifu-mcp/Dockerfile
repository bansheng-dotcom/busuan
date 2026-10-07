# 自托管镜像：用于不走魔搭托管、想自己跑一份 Hosted MCP 的场景。
# 需要 Python 3.11+ 与 Node.js 18+，两者都在镜像内固化为确定版本。
FROM python:3.11-slim

ENV PYTHONUNBUFFERED=1 \
    PYTHONUTF8=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    LAOSHIFU_MCP_TRANSPORT=streamable-http \
    LAOSHIFU_PORT=8000

RUN apt-get update \
    && apt-get install -y --no-install-recommends nodejs npm ca-certificates \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY pyproject.toml MANIFEST.in README.md LICENSE NOTICE ./
COPY laoshifu_mcp ./laoshifu_mcp

RUN python -m pip install --no-cache-dir .

RUN node --version && python -c "from laoshifu_mcp import runtime; print('engine root:', runtime.engine_root())"

EXPOSE 8000
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD python -c "import os,socket; s=socket.create_connection(('127.0.0.1', int(os.environ.get('LAOSHIFU_PORT','8000'))), 3); s.close()"

CMD ["laoshifu-mcp"]
