# -*- coding: utf-8 -*-
"""从始知阁(garychowcmu/daizhigev20)重新下载完整全文并重生成 PDF
替换 lfglib.cn 的预览版"""
import urllib.request, json, urllib.parse, os, re, sys, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from convert_pdf import OUTDIR, save_pdf

BASE = r"D:\daimajieti1\国学"
TXTDIR = os.path.join(BASE, "易藏术数")
os.makedirs(TXTDIR, exist_ok=True)
os.makedirs(OUTDIR, exist_ok=True)

def gh(url):
    req = urllib.request.Request(url, headers={"User-Agent": "curl", "Accept": "application/vnd.github+json"})
    return json.load(urllib.request.urlopen(req, timeout=30))

def list_dir(path):
    c = gh("https://api.github.com/repos/garychowcmu/daizhigev20/contents/" + urllib.parse.quote(path))
    return [(x["name"], x["path"]) for x in c if x["type"] == "file" and x["name"].endswith(".txt")]

def raw_dl(repo_path):
    url = "https://raw.githubusercontent.com/garychowcmu/daizhigev20/master/" + urllib.parse.quote(repo_path)
    req = urllib.request.Request(url, headers={"User-Agent": "curl"})
    for a in range(5):
        try:
            return urllib.request.urlopen(req, timeout=120).read().decode("utf-8", "ignore")
        except Exception:
            time.sleep(2 + a * 2)
    raise RuntimeError("download fail: " + repo_path)

def is_full(text):
    return "流芳阁" not in text and "祝您学习" not in text

def main():
    files = list_dir("易藏/术数") + list_dir("易藏/易经")
    print("始知阁易藏文件总数:", len(files))
    done = 0
    for name, path in files:
        title = name[:-4]
        txtpath = os.path.join(TXTDIR, name)
        pdfpath = os.path.join(OUTDIR, f"[易藏] {title}.pdf")
        # 跳过已完成的完整全文
        if os.path.exists(txtpath):
            try:
                old = open(txtpath, encoding="utf-8").read()
                if is_full(old) and os.path.exists(pdfpath) and os.path.getsize(pdfpath) > 1000:
                    print(f"[跳过] {title}")
                    continue
            except Exception:
                pass
        try:
            data = raw_dl(path)
            open(txtpath, "w", encoding="utf-8").write(data)
            paras = data.split("\n")
            sz = save_pdf(title, paras, pdfpath)
            done += 1
            print(f"[OK] {title} ({len(data)}字, {sz//1024}KB)")
        except Exception as e:
            print(f"[失败] {title}: {str(e)[:80]}")
        sys.stdout.flush()
        time.sleep(0.1)
    print("======================")
    print(f"重下载完成: {done} 本")

if __name__ == "__main__":
    main()
