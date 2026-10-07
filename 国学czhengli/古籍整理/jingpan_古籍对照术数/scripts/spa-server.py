#!/usr/bin/env python3
"""静態站點服務：真實檔案優先，其餘回退 index.html（配合 Vue history 模式）。"""
from __future__ import annotations

import os
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from urllib import error, request

ROOT = os.environ.get("JINGPAN_ROOT", "/var/www/jingpan")
HOST = os.environ.get("JINGPAN_HOST", "0.0.0.0")
PORT = int(os.environ.get("JINGPAN_PORT", "80"))
AI_UPSTREAM_BASE = os.environ.get("JINGPAN_AI_UPSTREAM_BASE", "http://127.0.0.1:8787").rstrip("/")
# 兼容旧环境变量
CHART_AI_UPSTREAM = os.environ.get(
    "JINGPAN_CHART_AI_UPSTREAM", f"{AI_UPSTREAM_BASE}/api/chart-ai-holographic"
)
AI_API_PATHS = frozenset({"/api/chart-ai-holographic", "/api/divination-ai"})


class SpaHandler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=ROOT, **kwargs)

    def end_headers(self) -> None:
        # HTML 入口不缓存，避免刷新仍用旧壳；带 hash 的 /assets/ 可长期缓存
        path = self.path.split("?", 1)[0].split("#", 1)[0]
        name = os.path.basename(path) or "index.html"
        ext = os.path.splitext(name)[1].lower()
        if ext in {".html", ".htm"} or name in {"index.html", "index.htm"}:
            self.send_header("Cache-Control", "no-store, no-cache, must-revalidate, max-age=0")
            self.send_header("Pragma", "no-cache")
        elif path.startswith("/assets/"):
            self.send_header("Cache-Control", "public, max-age=31536000, immutable")
        super().end_headers()

    def _api_path(self) -> str:
        return self.path.split("?", 1)[0]

    def _upstream_url(self) -> str:
        path = self._api_path()
        if path == "/api/chart-ai-holographic" and "JINGPAN_CHART_AI_UPSTREAM" in os.environ:
            return CHART_AI_UPSTREAM
        return f"{AI_UPSTREAM_BASE}{path}"

    def _proxy_ai(self) -> None:
        length = int(self.headers.get("Content-Length", "0") or 0)
        body = self.rfile.read(length) if length else b""
        headers = {"Content-Type": self.headers.get("Content-Type", "application/json")}
        req = request.Request(self._upstream_url(), data=body, headers=headers, method=self.command)
        try:
            with request.urlopen(req, timeout=300) as upstream:
                payload = upstream.read()
                self.send_response(upstream.status)
                for key, val in upstream.headers.items():
                    if key.lower() in {"content-type", "access-control-allow-origin"}:
                        self.send_header(key, val)
                self.end_headers()
                self.wfile.write(payload)
        except error.HTTPError as exc:
            payload = exc.read()
            self.send_response(exc.code)
            self.send_header("Content-Type", exc.headers.get("Content-Type", "application/json"))
            self.end_headers()
            self.wfile.write(payload)
        except Exception as exc:  # noqa: BLE001
            detail = str(exc)
            if 'timed out' in detail.lower():
                detail = '模型回應逾時，請稍後重試。'
            msg = json_error(detail)
            self.send_response(502)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.end_headers()
            self.wfile.write(msg)

    def _rewrite_to_index_if_needed(self) -> None:
        raw = self.path.split("?", 1)[0].split("#", 1)[0]
        local = self.translate_path(raw)
        if os.path.isdir(local):
            for name in ("index.html", "index.htm"):
                if os.path.isfile(os.path.join(local, name)):
                    return
            self.path = "/index.html"
        elif not os.path.isfile(local):
            self.path = "/index.html"

    def do_OPTIONS(self):  # noqa: N802
        if self._api_path() in AI_API_PATHS:
            return self._proxy_ai()
        self.send_error(404)

    def do_POST(self):  # noqa: N802
        if self._api_path() in AI_API_PATHS:
            return self._proxy_ai()
        self.send_error(405)

    def do_GET(self):  # noqa: N802
        self._rewrite_to_index_if_needed()
        return SimpleHTTPRequestHandler.do_GET(self)

    def do_HEAD(self):  # noqa: N802
        self._rewrite_to_index_if_needed()
        return SimpleHTTPRequestHandler.do_HEAD(self)

    def log_message(self, fmt: str, *args) -> None:
        sys_stderr = __import__("sys").stderr
        sys_stderr.write("%s - %s\n" % (self.address_string(), fmt % args))


def json_error(message: str) -> bytes:
    import json

    return json.dumps({"error": message}, ensure_ascii=False).encode("utf-8")


def main() -> None:
    os.makedirs(ROOT, exist_ok=True)
    server = ThreadingHTTPServer((HOST, PORT), SpaHandler)
    print(f"jingpan spa server on http://{HOST}:{PORT} root={ROOT}", flush=True)
    server.serve_forever()


if __name__ == "__main__":
    main()
