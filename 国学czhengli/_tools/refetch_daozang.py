# -*- coding: utf-8 -*-
"""从始知阁重新下载道藏术数 18 本完整全文并重生成 PDF"""
import urllib.request, json, urllib.parse, os, re, sys, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from convert_pdf import OUTDIR, save_pdf

BASE = r"D:\daimajieti1\国学"
TXTDIR = os.path.join(BASE, "道藏术数")
os.makedirs(TXTDIR, exist_ok=True)
os.makedirs(OUTDIR, exist_ok=True)

# (书名, 始知阁目录)
BOOKS = [
    ("黄帝龙首经", "道藏/正统道藏洞真部/众术类"),
    ("黄帝金匮玉衡经", "道藏/正统道藏洞真部/众术类"),
    ("黄帝授三子玄女经", "道藏/正统道藏洞真部/众术类"),
    ("黄帝宅经", "道藏/正统道藏洞真部/众术类"),
    ("灵台经", "道藏/正统道藏洞真部/众术类"),
    ("秤星灵台秘要经", "道藏/正统道藏洞真部/众术类"),
    ("通占大象历星经", "道藏/正统道藏洞真部/众术类"),
    ("黄帝太乙八门入式秘诀", "道藏/正统道藏洞玄部/众术类"),
    ("黄帝太乙八门入式诀", "道藏/正统道藏洞玄部/众术类"),
    ("黄帝太乙八门逆顺生死诀", "道藏/正统道藏洞玄部/众术类"),
    ("太上六壬明鉴符阴经", "道藏/正统道藏洞神部/方法类"),
    ("秘藏通玄变化六阴洞微遁甲真经", "道藏/正统道藏洞神部/方法类"),
    ("黄庭遁甲缘身经", "道藏/正统道藏洞神部/方法类"),
    ("邓天君玄灵八门报应内旨", "道藏/正统道藏正一部"),
    ("洞玄灵宝道士受三洞经箓法箓择日历", "道藏/正统道藏正一部"),
    ("洞真太上八素真经占候入定妙诀", "道藏/正统道藏正一部"),
    ("素问入式运气论奥", "道藏/正统道藏太玄部"),
    ("儒门崇理折衷堪舆完孝录", "道藏/正统道藏续道藏"),
]

def gh(url):
    req = urllib.request.Request(url, headers={"User-Agent": "curl", "Accept": "application/vnd.github+json"})
    return json.load(urllib.request.urlopen(req, timeout=30))

def list_dir(path):
    c = gh("https://api.github.com/repos/garychowcmu/daizhigev20/contents/" + urllib.parse.quote(path))
    return {x["name"]: x["path"] for x in c if x["type"] == "file" and x["name"].endswith(".txt")}

def raw_dl(repo_path):
    url = "https://raw.githubusercontent.com/garychowcmu/daizhigev20/master/" + urllib.parse.quote(repo_path)
    req = urllib.request.Request(url, headers={"User-Agent": "curl"})
    for a in range(5):
        try:
            return urllib.request.urlopen(req, timeout=120).read().decode("utf-8", "ignore")
        except Exception:
            time.sleep(2 + a * 2)
    raise RuntimeError("download fail: " + repo_path)

def main():
    cache = {}
    done = 0
    for title, d in BOOKS:
        try:
            if d not in cache:
                cache[d] = list_dir(d)
            files = cache[d]
            fname = title + ".txt"
            if fname not in files:
                print(f"[缺] {title} 不在 {d}")
                continue
            repo_path = files[fname]
            data = raw_dl(repo_path)
            open(os.path.join(TXTDIR, fname), "w", encoding="utf-8").write(data)
            sz = save_pdf(title, data.split("\n"), os.path.join(OUTDIR, f"[道藏] {title}.pdf"))
            done += 1
            print(f"[OK] {title} ({len(data)}字, {sz//1024}KB)")
        except Exception as e:
            print(f"[失败] {title}: {str(e)[:80]}")
        sys.stdout.flush()
        time.sleep(0.1)
    print("======================")
    print(f"道藏重下载完成: {done} 本")

if __name__ == "__main__":
    main()
