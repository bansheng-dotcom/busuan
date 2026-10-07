# -*- coding: utf-8 -*-
"""道藏·术数占卜类专书下载 + 转 PDF（筛掉炼丹/科仪，只留术数）"""
import os, re, sys, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from download_shushu import download_book, save_pdf, norm, existing_titles, OUTDIR

BASE = r"D:\daimajieti1\国学"
TXTDIR = os.path.join(BASE, "道藏术数")
os.makedirs(TXTDIR, exist_ok=True)
os.makedirs(OUTDIR, exist_ok=True)

# 道藏中的术数/占卜/星命/堪舆/式占 专书 (书名, 编号)
BOOKS = [
    ("黄帝龙首经", "210498"),          # 六壬式占
    ("黄帝金匮玉衡经", "210497"),      # 占卜
    ("黄帝授三子玄女经", "210496"),    # 奇门/太乙
    ("黄帝宅经", "210495"),            # 阳宅堪舆
    ("灵台经", "210490"),              # 星命占卜
    ("秤星灵台秘要经", "210492"),      # 星命
    ("通占大象历星经", "210493"),      # 占星
    ("黄帝太乙八门入式秘诀", "210186"),# 太乙
    ("黄帝太乙八门入式诀", "210187"),  # 太乙
    ("黄帝太乙八门逆顺生死诀", "210188"),# 太乙
    ("太上六壬明鉴符阴经", "210935"),  # 六壬符法
    ("秘藏通玄变化六阴洞微遁甲真经", "210969"),# 遁甲
    ("黄庭遁甲缘身经", "210976"),      # 遁甲
    ("儒门崇理折衷堪舆完孝录", "211177"),# 堪舆
    ("邓天君玄灵八门报应内旨", "210157"),# 八门
    ("洞玄灵宝道士受三洞经箓法箓择日历", "210080"),# 择日
    ("洞真太上八素真经占候入定妙诀", "210099"),# 占候
    ("素问入式运气论奥", "209899"),    # 五运六气
]

def main():
    ex = existing_titles()
    done = 0
    for name, bid in BOOKS:
        url = f"https://lfglib.cn/text/daolib/{bid}.html"
        safe = re.sub(r'[\\/:*?"<>|]', "_", name)
        txtpath = os.path.join(TXTDIR, safe + ".txt")
        pdfpath = os.path.join(OUTDIR, f"[道藏] {safe}.pdf")
        if norm(name) in ex:
            print(f"[跳过-已有] {name}")
            continue
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
    print(f"道藏术数完成: {done} 本")

if __name__ == "__main__":
    main()
