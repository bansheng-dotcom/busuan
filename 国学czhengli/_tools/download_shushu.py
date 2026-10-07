# -*- coding: utf-8 -*-
"""
易藏·术数类专书批量下载 + 转 PDF
- 从 lfglib.cn/yilist 解析全部术数书
- 去重(跳过已有四库本/其他术数)
- 逐书抓取全文(txt) 并转 PDF
"""
import os, re, sys, time, html, urllib.request, urllib.error
import zhconv
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from convert_pdf import BookPDF, OUTDIR, save_pdf, clean_kanripo

BASE = r"D:\daimajieti1\国学"
TXTDIR = os.path.join(BASE, "易藏术数")
os.makedirs(TXTDIR, exist_ok=True)
os.makedirs(OUTDIR, exist_ok=True)

UA = {"User-Agent": "Mozilla/5.0"}
YILIST = "https://lfglib.cn/yilist"

def fetch(url, tries=3):
    for a in range(tries):
        try:
            req = urllib.request.Request(url, headers=UA)
            return urllib.request.urlopen(req, timeout=40).read().decode("utf-8", "ignore")
        except Exception:
            time.sleep(1.5)
    raise RuntimeError("fetch fail: " + url)

def parse_yilist():
    h = fetch(YILIST)
    rows = re.findall(r'<tr class="row-\d+ (?:odd|even)">(.*?)</tr>', h, flags=re.S)
    books = []
    for r in rows:
        def cell(n):
            m = re.search(r'<td class="column-%d">(.*?)</td>' % n, r, flags=re.S)
            return html.unescape(re.sub(r"<[^>]+>", "", m.group(1))).strip() if m else ""
        u = re.search(r"href='(https://lfglib\.cn/text/yilib/\d+\.html)'", r)
        name = cell(1).strip("《》").strip()
        cat = cell(2)
        if name and u:
            books.append((name, u.group(1), cat))
    return books

def existing_titles():
    s = set()
    kan = os.path.join(BASE, "四库全书-子部术数")
    for d in os.listdir(kan):
        m = re.match(r"^[A-Za-z0-9]+_(.+?)(?:-[^_]*)?$", d)
        if m:
            s.add(norm(m.group(1)))
    for f in os.listdir(os.path.join(BASE, "其他术数")):
        s.add(norm(os.path.splitext(f)[0]))
    return s

def norm(t):
    t = t.replace(" ", "").replace("　", "")
    try:
        t = zhconv.convert(t, "zh-cn")
    except Exception:
        pass
    return t

def max_page(h):
    ms = re.findall(r'\.html/(\d+)', h)
    if not ms:
        return 1
    return max(int(x) for x in ms)

def extract_main(h):
    arts = re.findall(r"<article.*?</article>", h, flags=re.S)
    best = ""
    for a in arts:
        t = re.sub(r"<[^>]+>", "", a)
        t = html.unescape(t)
        if "卦" in t or "易" in t or "占" in t:
            if len(t) > len(best):
                best = t
    if not best:
        best = html.unescape(re.sub(r"<[^>]+>", "", h))
    best = re.sub(r"流芳阁|易藏|TXT全文下载|书籍类目[^\n]*|书籍内容[:：]?", "", best)
    return best

def download_book(url):
    h = fetch(url)
    np = max_page(h)
    parts = [extract_main(h)]
    for i in range(2, np + 1):
        h = fetch(f"{url}/{i}")
        parts.append(extract_main(h))
        time.sleep(0.2)
    full = "\n".join(parts)
    full = re.sub(r"[ \t\r]+", " ", full)
    full = re.sub(r"\n\s*\n+", "\n", full)
    full = re.sub(r"分页阅读[：:][\s\d下一页上一页]*", "", full)
    full = re.sub(r"以上为书籍的全部内容[，,]?祝您阅读愉快。", "", full)
    return full.split("\n")

def main():
    cat = sys.argv[1] if len(sys.argv) > 1 else "术数"
    books = [(n, u) for n, u, c in parse_yilist() if c == cat]
    print(f"{cat}类书:", len(books))
    ex = existing_titles()
    print("已有(去重后):", len(ex))
    todo = [(n, u) for n, u in books if norm(n) not in ex]
    print("待下载:", len(todo))
    done = 0
    for name, url in todo:
        safe = re.sub(r'[\\/:*?"<>|]', "_", name)
        txtpath = os.path.join(TXTDIR, safe + ".txt")
        pdfpath = os.path.join(OUTDIR, f"[易藏] {safe}.pdf")
        try:
            if not (os.path.exists(pdfpath) and os.path.getsize(pdfpath) > 1000):
                paras = download_book(url)
                open(txtpath, "w", encoding="utf-8").write("\n".join(paras))
                sz = save_pdf(name, paras, pdfpath)
                done += 1
                print(f"[OK] {name} ({sz//1024}KB)")
            else:
                print(f"[跳过] {name}")
        except Exception as e:
            print(f"[失败] {name}: {str(e)[:80]}")
        sys.stdout.flush()
        time.sleep(0.2)
    print("======================")
    print(f"本次完成: {done} 本")

if __name__ == "__main__":
    main()
