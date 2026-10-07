#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
卜算ima 检索 —— 本地精确检索（默认） + ima 知识库检索（兜底）

两种模式：
  1) 本地精确检索（推荐）：对典籍 txt 建「字级倒排索引」，按字精确匹配原文，
     效果等同 Grep（任意连续子串都能命中），支持繁简自动转换 + 正则。
     找不到时自动 fallback 到 ima 知识库语义检索。
  2) ima 知识库检索：调腾讯 ima OpenAPI search_knowledge 接口（全文检索）。

本地配置（优先级从高到低）：
  1. 命令行参数 --txt / --clientid / --apikey / --kb
  2. 环境变量  IMA_TXT_DIR / IMA_CLIENT_ID / IMA_API_KEY / IMA_KB_ID
  3. scripts/ima_config.json（见 ima_config.example.json）

用法：
  python scripts/search.py "妻财" --txt D:\\daimajieti1\\国学czhengli\\txt
  python scripts/search.py "妻财" --local --txt <典籍目录>          # 本地精确
  python scripts/search.py "妻.{0,4}应" --local --regex --txt <目录>  # 正则模式
  python scripts/search.py "妻财"                                   # 走 ima API
  python scripts/search.py --list-kb                                 # 列知识库

可选依赖（增强繁简召回，不装也能用）：pip install opencc-python-reimplemented
"""

import argparse
import hashlib
import json
import os
import pickle
import re
import sys
import urllib.error
import urllib.request

# ---------- ima OpenAPI ----------
BASE_URL = "https://ima.qq.com/openapi/wiki/v1"
CONFIG_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "ima_config.json")

# ---------- 本地索引 ----------
INDEX_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".index")

# ---------- 繁简转换（可选） ----------
try:
    from opencc import OpenCC
    _cc_s2t = OpenCC("s2t")
    _cc_t2s = OpenCC("t2s")
    _HAS_OPENCC = True
except Exception:  # noqa: BLE001
    _HAS_OPENCC = False


def _load_config():
    cfg = {}
    if os.path.exists(CONFIG_PATH):
        try:
            with open(CONFIG_PATH, "r", encoding="utf-8") as f:
                cfg = json.load(f)
        except Exception:
            pass
    return cfg


def _get_cred(cfg_key, env_key, cli_val, cfg):
    if cli_val:
        return cli_val
    env = os.environ.get(env_key)
    if env:
        return env
    return cfg.get(cfg_key, "")


def _headers(client_id, api_key):
    return {
        "Content-Type": "application/json",
        "ima-openapi-clientid": client_id,
        "ima-openapi-apikey": api_key,
    }


def _post(path, body, client_id, api_key):
    url = BASE_URL + path
    data = json.dumps(body, ensure_ascii=False).encode("utf-8")
    req = urllib.request.Request(url, data=data, headers=_headers(client_id, api_key), method="POST")
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        raw = e.read().decode("utf-8", errors="replace")
        return {"code": e.code, "msg": "HTTP %s: %s" % (e.code, raw[:300])}
    except Exception as e:  # noqa: BLE001
        return {"code": -1, "msg": str(e)}


def _clean(text):
    if not text:
        return ""
    text = re.sub(r"<[^>]+>", "", text)
    text = (text.replace("&lt;", "<").replace("&gt;", ">")
                .replace("&amp;", "&").replace("&quot;", '"').replace("&#39;", "'"))
    return text.strip()


def search_knowledge_base(query="", cursor="", limit=20, client_id="", api_key=""):
    body = {"query": query, "cursor": cursor, "limit": int(limit)}
    return _post("/search_knowledge_base", body, client_id, api_key)


def search_knowledge(query, kb_id, cursor="", client_id="", api_key=""):
    body = {"query": query, "cursor": cursor, "knowledge_base_id": kb_id}
    return _post("/search_knowledge", body, client_id, api_key)


def ima_search(query, kb_id, client_id="", api_key="", limit=20):
    res = search_knowledge(query, kb_id, "", client_id, api_key)
    if not isinstance(res, dict):
        return {"error": "响应异常"}
    if res.get("code") not in (0, None, "0"):
        return {"error": res.get("msg", "请求失败")}
    out = []
    for item in res.get("info_list", [])[:int(limit)]:
        out.append({
            "title": item.get("title", ""),
            "media_id": item.get("media_id", ""),
            "highlight": _clean(item.get("highlight_content", "")),
        })
    return out


# ---------- 本地精确检索 ----------
def _variants(keyword):
    """生成关键词的繁简变体，用于同时匹配简体/繁体原文"""
    vs = {keyword}
    if _HAS_OPENCC:
        try:
            vs.add(_cc_s2t.convert(keyword))
            vs.add(_cc_t2s.convert(keyword))
        except Exception:  # noqa: BLE001
            pass
    return [v for v in vs if v and v != keyword] + [keyword]


def _iter_txt(txt_dir):
    """遍历 txt 目录，产出 (文件路径, 文件名)"""
    root = os.path.abspath(txt_dir)
    for dirpath, _dirs, files in os.walk(root):
        for fn in sorted(files):
            if fn.lower().endswith(".txt"):
                fp = os.path.join(dirpath, fn)
                rel = os.path.relpath(fp, root)
                yield fp, rel


def build_index(txt_dir):
    """扫描典籍目录，建字级倒排索引：{字: [文件ID...]}"""
    files = []
    index = {}
    for fp, rel in _iter_txt(txt_dir):
        fid = len(files)
        files.append(rel)
        try:
            with open(fp, "r", encoding="utf-8", errors="ignore") as f:
                text = f.read()
        except Exception:
            continue
        for ch in set(text):  # 文件级：记录「字 → 出现该字的文件」
            index.setdefault(ch, []).append(fid)
    return {"txt_dir": os.path.abspath(txt_dir), "files": files, "index": index}


def load_index(txt_dir):
    """加载缓存索引，不存在则构建"""
    os.makedirs(INDEX_DIR, exist_ok=True)
    key = hashlib.md5(os.path.abspath(txt_dir).encode("utf-8")).hexdigest()[:12]
    idx_file = os.path.join(INDEX_DIR, "idx_%s.pkl" % key)
    if os.path.exists(idx_file):
        try:
            with open(idx_file, "rb") as f:
                return pickle.load(f)
        except Exception:  # noqa: BLE001
            pass
    print("[建索引] 首次扫描 %s ..." % txt_dir, file=sys.stderr)
    data = build_index(txt_dir)
    with open(idx_file, "wb") as f:
        pickle.dump(data, f)
    print("[建索引] 完成：%d 个文件，%d 个字符索引" % (len(data["files"]), len(data["index"])), file=sys.stderr)
    return data


def local_search(keyword, txt_dir, use_regex=False, limit=20):
    """本地精确检索，返回 [{title, highlight}]"""
    data = load_index(txt_dir)
    files = data["files"]
    index = data["index"]
    root = data["txt_dir"]
    results = []
    seen = set()

    if use_regex:
        try:
            pat = re.compile(keyword)
        except re.error as e:
            return {"error": "正则错误：%s" % e}
        for fp, rel in _iter_txt(root):
            try:
                with open(fp, "r", encoding="utf-8", errors="ignore") as f:
                    text = f.read()
            except Exception:
                continue
            for m in pat.finditer(text):
                ctx = text[max(0, m.start() - 30): m.end() + 30].replace("\n", " ")
                if ctx not in seen:
                    seen.add(ctx)
                    results.append({"title": rel, "highlight": ctx})
                    if len(results) >= limit:
                        return results
        return results

    # 精确短语匹配（含繁简变体）
    variants = _variants(keyword)
    candidate_fids = set()
    for kw in variants:
        if not kw:
            continue
        fids = set(range(len(files)))
        for ch in set(kw):
            fids &= set(index.get(ch, []))
            if not fids:
                break
        candidate_fids |= fids

    for fid in sorted(candidate_fids):
        rel = files[fid]
        fp = os.path.join(root, rel)
        try:
            with open(fp, "r", encoding="utf-8", errors="ignore") as f:
                text = f.read()
        except Exception:
            continue
        for kw in variants:
            if not kw:
                continue
            start = 0
            while True:
                pos = text.find(kw, start)
                if pos == -1:
                    break
                ctx = text[max(0, pos - 30): pos + len(kw) + 30].replace("\n", " ")
                key = (rel, ctx)
                if key not in seen:
                    seen.add(key)
                    results.append({"title": rel, "highlight": ctx})
                start = pos + 1
                if len(results) >= limit:
                    return results
    return results


# ---------- 输出 ----------
def _print_hits(hits):
    if isinstance(hits, dict) and "error" in hits:
        print("[检索失败] %s" % hits["error"], file=sys.stderr)
        return
    if not hits:
        print("[无结果] 未找到匹配。古文建议用繁体、短词；本地模式可用 --regex 试正则。")
        return
    for i, h in enumerate(hits, 1):
        print("── %d. %s ──" % (i, h["title"]))
        if h.get("highlight"):
            print(h["highlight"])
        print()


def main():
    for _s in (sys.stdout, sys.stderr):
        try:
            _s.reconfigure(encoding="utf-8")
        except Exception:  # noqa: BLE001
            pass

    p = argparse.ArgumentParser(description="卜算ima 检索（本地精确 + ima 兜底）")
    p.add_argument("query", nargs="?", default="", help="检索关键词")
    p.add_argument("--local", action="store_true", help="本地精确检索（字级索引，等同 Grep）")
    p.add_argument("--regex", action="store_true", help="按正则匹配（隐含 --local）")
    p.add_argument("--txt", default="", help="典籍 txt 目录（缺省用 IMA_TXT_DIR）")
    p.add_argument("--kb", default="", help="ima 知识库 ID（缺省用 IMA_KB_ID）")
    p.add_argument("--clientid", default="", help="ima Client ID")
    p.add_argument("--apikey", default="", help="ima API Key")
    p.add_argument("--limit", type=int, default=20, help="返回条数（默认 20）")
    p.add_argument("--list-kb", action="store_true", help="列出 ima 知识库（找 kb id）")
    args = p.parse_args()

    cfg = _load_config()
    client_id = _get_cred("client_id", "IMA_CLIENT_ID", args.clientid, cfg)
    api_key = _get_cred("api_key", "IMA_API_KEY", args.apikey, cfg)
    kb_id = _get_cred("kb_id", "IMA_KB_ID", args.kb, cfg)
    txt_dir = _get_cred("txt_dir", "IMA_TXT_DIR", args.txt, cfg)

    if args.list_kb:
        if not client_id or not api_key:
            print("缺少 ima 凭证：请配置 IMA_CLIENT_ID / IMA_API_KEY", file=sys.stderr)
            print("凭证获取：https://ima.qq.com/agent-interface", file=sys.stderr)
            sys.exit(1)
        res = search_knowledge_base("", "", 20, client_id, api_key)
        infos = res.get("info_list", []) if isinstance(res, dict) else []
        print("可用知识库：")
        for it in infos:
            print("  - %s  (id=%s)" % (it.get("name"), it.get("id")))
        if not infos:
            print("  [无] " + str(res.get("msg", "")))
        return

    if not args.query:
        p.print_help()
        sys.exit(1)

    use_local = args.local or args.regex

    if use_local:
        if not txt_dir or not os.path.isdir(txt_dir):
            print("缺少典籍目录：请用 --txt 指定，或设 IMA_TXT_DIR / ima_config.json 的 txt_dir", file=sys.stderr)
            sys.exit(1)
        hits = local_search(args.query, txt_dir, use_regex=args.regex, limit=args.limit)
        if isinstance(hits, dict) and "error" in hits:
            _print_hits(hits)
            sys.exit(1)
        if not hits and client_id and api_key and kb_id:
            print("[本地无精确匹配，转 ima 知识库语义检索 ...]", file=sys.stderr)
            print()
            hits = ima_search(args.query, kb_id, client_id, api_key, args.limit)
        _print_hits(hits)
        return

    # 默认走 ima API
    if not client_id or not api_key:
        print("缺少 ima 凭证：请配置 IMA_CLIENT_ID / IMA_API_KEY，或用 --local 走本地检索", file=sys.stderr)
        print("凭证获取：https://ima.qq.com/agent-interface", file=sys.stderr)
        sys.exit(1)
    if not kb_id:
        print("缺少知识库 ID：请配置 IMA_KB_ID，或用 --kb 指定", file=sys.stderr)
        sys.exit(1)
    _print_hits(ima_search(args.query, kb_id, client_id, api_key, args.limit))


if __name__ == "__main__":
    main()
