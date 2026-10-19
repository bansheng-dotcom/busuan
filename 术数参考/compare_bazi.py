# -*- coding: utf-8 -*-
"""八字四柱对照：本技能 cast.py bazi vs dglijin bazi_pan.py（N 随机样本）。"""
import subprocess, random, re, sys, json, os

CAST = r"D:\卜算\.claude\skills\卜算\scripts\cast.py"
DGLJ = r"D:\术数参考\chinese-metaphysics-skills\bazi-pan-skill\scripts\bazi_pan.py"
PY = r"D:\anaconda3\python.exe"
N = int(sys.argv[1]) if len(sys.argv) > 1 else 20
ENV = {**os.environ, "PYTHONIOENCODING": "utf-8"}

random.seed(20261009)


def skill_bazi(y, m, d, h, sex):
    r = subprocess.run([PY, CAST, "bazi", str(y), str(m), str(d), str(h), "0", "0",
                        "1" if sex == "男" else "0"],
                       capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=60, env=ENV)
    g = re.search(r"四柱:\s*(\S+)\s+(\S+)\s+(\S+)\s+(\S+)", r.stdout)
    return list(g.groups()) if g else None


def dglj_bazi(y, m, d, h, sex):
    r = subprocess.run([PY, DGLJ, "--date", f"{y}-{m:02d}-{d:02d}", "--hour", str(h),
                        "--gender", sex, "--json"],
                       capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=60, env=ENV)
    try:
        j = json.loads(r.stdout)
        s = j["四柱"]
        return [s["年柱"], s["月柱"], s["日柱"], s["时柱"]]
    except Exception:
        return None


def main():
    print(f"八字四柱对照（{N} 随机样本，seed=20261009）\n")
    cols = ["年柱", "月柱", "日柱", "时柱"]
    agree = [0, 0, 0, 0]
    diffs = []
    for _ in range(N):
        y = random.randint(1950, 2020)
        m = random.randint(1, 12)
        d = random.randint(1, 28)
        h = random.randint(0, 23)
        sex = random.choice(["男", "女"])
        a = skill_bazi(y, m, d, h, sex)
        b = dglj_bazi(y, m, d, h, sex)
        if not a or not b:
            continue
        for i in range(4):
            if a[i] == b[i]:
                agree[i] += 1
            else:
                if len(diffs) < 6:
                    diffs.append((f"{y}-{m:02d}-{d:02d} {h:02d}时 {sex}", a, b))
    print(f"{'柱':<4} {'一致':>5} {'/ 有效':>6} {'一致率':>7}")
    for i in range(4):
        print(f"{cols[i]:<4} {agree[i]:>5} {N:>6} {agree[i]/N*100:>6.0f}%")
    print("\n差异样例（本技能 vs dglijin）:")
    for dt, a, b in diffs:
        print(f"  {dt}: {' '.join(a)} vs {' '.join(b)}")


if __name__ == "__main__":
    main()
