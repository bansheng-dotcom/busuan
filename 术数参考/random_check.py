# -*- coding: utf-8 -*-
"""卜算技能随机检验：12 个排盘术随机 fuzz（无崩溃 + 关键字段齐全），多线程并行。

用法:
  python random_check.py [N] [workers]
"""
import subprocess
import random
import sys
from concurrent.futures import ThreadPoolExecutor

CAST = r"D:\卜算\.claude\skills\卜算\scripts\cast.py"
PY = r"D:\anaconda3\python.exe"
N = int(sys.argv[1]) if len(sys.argv) > 1 else 15
WORKERS = int(sys.argv[2]) if len(sys.argv) > 2 else 6

random.seed(20261009)


def run(args, timeout=60):
    try:
        r = subprocess.run([PY, CAST, *[str(a) for a in args]],
                           capture_output=True, text=True, encoding="utf-8",
                           errors="replace", timeout=timeout)
        return r.returncode, r.stdout, r.stderr
    except subprocess.TimeoutExpired:
        return "TIMEOUT", "", "超时"
    except Exception as e:  # noqa
        return "ERR", "", str(e)


def rdt():
    y = random.randint(1900, 2100)
    m = random.randint(1, 12)
    d = random.randint(1, 28)
    h = random.randint(0, 23)
    mi = random.randint(0, 59)
    return f"{y}-{m:02d}-{d:02d} {h:02d}:{mi:02d}"


def rparts():
    t = rdt().split(" ")
    y, m, d = map(int, t[0].split("-"))
    h, mi = map(int, t[1].split(":"))
    return y, m, d, h, mi, random.randint(0, 59), random.choice([0, 1])


def gen_methods():
    return [
        ("小六壬",   lambda: (["xiaoliuren", "--time", rdt()], "落宫")),
        ("梅花·时间", lambda: (["meihua-time", "--time", rdt()], "本卦")),
        ("梅花·数字", lambda: (["meihua-num", random.randint(1, 999), random.randint(1, 999)], "本卦")),
        ("六爻纳甲", lambda: (["liuyao", "--time", rdt()], "初爻")),
        ("大六壬",   lambda: (["liuren", "--time", rdt()], "四课")),
        ("金口诀",   lambda: (["jinkoujue", random.choice("子丑寅卯辰巳午未申酉戌亥"), "--time", rdt()], "月将")),
        ("奇门遁甲", lambda: (["qimen", "--time", rdt()], "八门")),
        ("太乙神数", lambda: (["taiyi", "--time", rdt()], "太乙神数")),
        ("八字命理", lambda: (["bazi", *[str(x) for x in rparts()]], "四柱")),
        ("紫微斗数", lambda: (lambda p: (["zhiwei", p[0], p[1], p[2], p[3], p[6]], "命宫"))(rparts())),
        ("七政四余", lambda: (["qizheng", "--time", rdt()], "七政四余星盘")),
        ("风水堪舆", lambda: (["fengshui", random.randint(1940, 2010),
                              random.choice(["坐北朝南", "坐南朝北", "坐东朝西", "坐西朝东"]),
                              random.choice(["男", "女"])], "命卦")),
        ("择日",     lambda: (["zeri", random.choice(["婚嫁", "开业", "动土", "出行", "搬家"]),
                              "--time", rdt()], "择日")),
    ]


def check_one(pair):
    args, marker = pair
    code, out, err = run(args)
    ok = (code == 0 and marker in out)
    return args, code, ok, (err or out).strip()[:100]


def main():
    print(f"卜算技能随机检验（每术 {N} 例，seed=20261009，{WORKERS} 线程并行）", flush=True)
    print(f"{'术法':<10} {'通过':>6} {'失败':>6} {'通过率':>8}", flush=True)
    print("-" * 50, flush=True)
    total_fail = 0
    for name, gen in gen_methods():
        pairs = [gen() for _ in range(N)]
        ok = fail = 0
        samples = []
        with ThreadPoolExecutor(max_workers=WORKERS) as ex:
            for args, code, o, msg in ex.map(check_one, pairs):
                if o:
                    ok += 1
                else:
                    fail += 1
                    total_fail += 1
                    if len(samples) < 2:
                        samples.append((args, code, msg))
        print(f"{name:<10} {ok:>6} {fail:>6} {ok / N * 100:>7.0f}%", flush=True)
        for args, code, msg in samples:
            print(f"    例 code={code}: {' '.join(str(a)[:20] for a in args[:4])}… {msg[:60]}", flush=True)
    print("-" * 50, flush=True)
    print(f"合计 13 术 × {N} 例，失败 {total_fail} 例", flush=True)


if __name__ == "__main__":
    main()
