# -*- coding: utf-8 -*-
"""排盘结果 -> 自包含 HTML 可视化（水墨·古籍风，无外部依赖）"""
import datetime
from bazi import _shensha

_CSS = """
* { box-sizing: border-box; margin: 0; padding: 0; }
body { font-family: 'Noto Serif SC','STSong','SimSun',serif; background:#f6f1e6; color:#2b2723; padding:28px; line-height:1.6; }
.wrap { max-width: 760px; margin: 0 auto; }
h1 { font-size: 26px; letter-spacing: 4px; color:#8c2f1f; border-bottom: 2px solid #8c2f1f; padding-bottom: 10px; margin-bottom: 6px; }
.sub { color:#7a7266; font-size: 14px; margin-bottom: 20px; }
.card { background:#fffdf6; border:1px solid #e3d9c4; border-radius:8px; padding:18px 20px; margin-bottom:16px; box-shadow:0 1px 4px rgba(0,0,0,.05); }
.card h2 { font-size: 16px; color:#8c2f1f; margin-bottom: 10px; letter-spacing: 2px; }
table { width:100%; border-collapse: collapse; }
th, td { padding: 8px 6px; text-align:center; font-size: 15px; border-bottom: 1px solid #eee6d4; }
th { color:#8c2f1f; font-weight:600; background:#f3ecda; }
.pillar { font-size: 22px; letter-spacing: 2px; }
.small { font-size: 12px; color:#8a8172; }
.grid { display:grid; grid-template-columns: repeat(3, 1fr); gap: 10px; }
.palace { border:1px solid #e3d9c4; border-radius:8px; padding:10px 8px; background:#fbf8ef; min-height:96px; }
.palace.ming { border:2px solid #8c2f1f; background:#f7ead8; }
.palace .name { color:#8c2f1f; font-weight:700; font-size:15px; margin-bottom:4px; }
.palace .gz { font-size:13px; color:#5a5247; margin-bottom:4px; }
.palace .stars { font-size:13px; color:#2b2723; }
.palace .fu { font-size:11px; color:#7a7266; margin-top:3px; }
.palace .dx { font-size:11px; color:#8c2f1f; margin-top:3px; }
.tag { display:inline-block; background:#8c2f1f; color:#fff; font-size:11px; padding:0 5px; border-radius:3px; margin-right:3px; }
.warn { color:#8c2f1f; font-size:13px; }
"""


def _esc(s):
    return str(s).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def save(path, title, body):
    html = f"""<!DOCTYPE html>
<html lang="zh"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{_esc(title)}</title><style>{_CSS}</style></head>
<body><div class="wrap">
<h1>{_esc(title)}</h1>
{body}
<div class="sub">本盘由 scripts/cast.py 确定性排盘生成，仅供传统文化研习与娱乐参考。</div>
</div></body></html>"""
    with open(path, "w", encoding="utf-8") as f:
        f.write(html)
    print(f"[已生成] {path}")


def bazi_html(b, gender, path):
    """八字 -> HTML"""
    lunar = b.getLunar()
    solar = lunar.getSolar()
    cols = [("年柱", b.getYear(), b.getYearShiShenGan(), b.getYearWuXing(), b.getYearNaYin()),
            ("月柱", b.getMonth(), b.getMonthShiShenGan(), b.getMonthWuXing(), b.getMonthNaYin()),
            ("日柱", b.getDay(), b.getDayShiShenGan(), b.getDayWuXing(), b.getDayNaYin()),
            ("时柱", b.getTime(), b.getTimeShiShenGan(), b.getTimeWuXing(), b.getTimeNaYin())]
    rows = "".join(
        f"<tr><th>{n}</th><td class='pillar'>{gz}</td><td>{ss}</td><td>{wx}</td><td class='small'>{ny}</td></tr>"
        for n, gz, ss, wx, ny in cols)
    ss = _shensha(b)
    ss_html = "　".join(f"{n}（{m}）" for n, m in ss) if ss else "—"
    sub = f"公历 {solar.toYmdHms()}　农历 {lunar.toString()}　{'男' if gender else '女'}"
    body = f"""
<div class="sub">{_esc(sub)}</div>
<div class="card"><h2>四柱</h2><table>
<tr><th></th><th>干支</th><th>十神</th><th>五行</th><th>纳音</th></tr>{rows}</table></div>
<div class="card"><h2>日主</h2>
<p>日主 <b>{b.getDayGan()}{b.getDayZhi()}</b>　长生 {b.getDayDiShi()}　旬空 {b.getDayXunKong()}　命宫 {b.getMingGong()}　胎元 {b.getTaiYuan()}</p></div>
<div class="card"><h2>神煞</h2><p>{_esc(ss_html)}</p></div>"""
    save(path, f"八字命盘 · {b.getYear()}", body)


def zhiwei_html(r, path):
    """紫微斗数 -> HTML"""
    cells = []
    for p in r["十二宫"]:
        mains = " ".join(f"{n}({b}{s})" if s else f"{n}({b})" for n, b, s in p["主星"]) or "—"
        fus = " ".join(p["辅星"]) or "—"
        dx = f"{p['大限'][0]}-{p['大限'][1]}岁" if p["大限"] else "—"
        tag = '<span class="tag">命</span>' if p["命"] else ('<span class="tag">身</span>' if p["身"] else "")
        cls = "palace ming" if p["命"] or p["身"] else "palace"
        cells.append(
            f"<div class='{cls}'><div class='name'>{tag}{p['宫']}</div>"
            f"<div class='gz'>{p['干']}{p['支']}</div><div class='stars'>{_esc(mains)}</div>"
            f"<div class='fu'>{_esc(fus)}</div><div class='dx'>{dx}</div></div>")
    body = f"""
<div class="sub">{_esc(r['农历'])}　四柱 {_esc(r['四柱'])}</div>
<div class="card"><h2>命宫身宫</h2>
<p>命宫 <b>{r['命宫']}</b>　身宫 <b>{r['身宫']}</b>　五行局 <b>{r['五行局']}</b>　紫微在{r['紫微']}　天府在{r['天府']}</p>
<p>四化：{_esc(r['四化'])}</p></div>
<div class="card"><h2>十二宫</h2><div class="grid">{''.join(cells)}</div></div>"""
    save(path, f"紫微斗数命盘 · {r['四柱']}", body)
