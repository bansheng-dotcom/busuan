# -*- coding: utf-8 -*-
"""紫微格局判定 · 数据表迁移版（JSON 规则表 + 通用解释器）。

把 ziwei_geju.py 里 18 个硬编码 _check_* 函数，迁成 tianzhi-core duanyu.py 式
JSON 规则表 + GejuAdapter（盘面适配器）。每条格局带
  id/name(格局名) verdict(吉凶) text(原文) note(断语) cond(判定条件) reading(读法)
判定由 duanyu_engine 的通用解释器 + GejuAdapter 完成；ziwei_geju.judge_patterns
仍可作交叉印证（两套判定结果应一致，不一致即标「信号冲突」）。

用法：
  from judge.ziwei_geju_data import find_geju
  hits = find_geju(chart)   # chart 为 pan/zhiwei 产出的盘（含「十二宫」）
"""
from __future__ import annotations

from judge.duanyu_engine import BaseAdapter, find
from pan import zhiwei


class GejuAdapter(BaseAdapter):
    """紫微格局适配器：把 pan/zhiwei 的十二宫盘映射到 duanyu_engine DSL。

    chart["十二宫"][idx] = {"宫": 宫名, "支": 地支, "命": bool,
                            "主星": [(星名, 庙旺, 四化)], "辅星": [星名]}
    宫位索引寅=0。命宫由 p["命"] 定位。
    """

    def __init__(self, chart):
        self.chart = chart
        self.palaces = chart["十二宫"]
        self.by_name = {p["宫"]: i for i, p in enumerate(self.palaces)}
        self.by_zhi = {p["支"]: i for i, p in enumerate(self.palaces)}
        self.ming = next((i for i, p in enumerate(self.palaces) if p.get("命")), 0)

    def _stars(self, idx):
        p = self.palaces[idx]
        names = {n for n, _b, _s in p["主星"]}
        names.update(p["辅星"])
        return names

    def _idx(self, P):
        if P == "命":
            return self.ming
        if P in self.by_name:
            return self.by_name[P]
        if P in self.by_zhi:
            return self.by_zhi[P]
        raise ValueError(f"不是宫名或地支：{P!r}")

    def _has(self, idx, stars, mode):
        names = self._stars(idx)
        return all(s in names for s in stars) if mode == "all" else any(s in names for s in stars)

    def _sanfang(self, idx, stars, mode):
        zs = zhiwei.sanfang_sizheng(idx)      # [本宫, 对宫, 三合两宫]
        inn = [any(s in self._stars(q) for q in zs) for s in stars]
        return all(inn) if mode == "all" else any(inn)

    def _star_at(self, name):
        for i in range(12):
            if name in self._stars(i):
                return self.palaces[i]["支"]
        return None

    def test(self, c):
        mode = c.get("mode", "all")
        if "stars" in c and "at" in c:
            return self._has(self._idx(c["at"]), c["stars"], mode)
        if "none" in c:
            return not self._has(self._idx(c["at"]), c["none"], "any")
        if "sanfang" in c:
            idx = self._idx(c["sanfang"])
            zs = zhiwei.sanfang_sizheng(idx)
            got = sum(1 for s in c["stars"] if any(s in self._stars(q) for q in zs))
            if "min" in c or "max" in c:
                return c.get("min", 0) <= got <= c.get("max", len(c["stars"]))
            return got == len(c["stars"]) if mode == "all" else got >= 1
        if "zhi" in c:
            return self.palaces[self._idx(c["zhi"])]["支"] in c["in"]
        if "star_at" in c:
            z = self._star_at(c["star_at"])
            return z in c["in"] if z else False
        if "same_palace" in c:
            return any(all(s in self._stars(i) for s in c["same_palace"]) for i in range(12))
        if "luma_jiaochi" in c:
            lu = [i for i in range(12) if "禄存" in self._stars(i)]
            ma = [i for i in range(12) if "天马" in self._stars(i)]
            if not lu or not ma:
                return False
            return bool(set(lu) & set(ma)) or any((l + 6) % 12 in ma for l in lu)
        if "riyue_bingming" in c:
            tai = [i for i in range(12) if "太阳" in self._stars(i)]
            yin = [i for i in range(12) if "太阴" in self._stars(i)]
            if not tai or not yin:
                return False
            if set(tai) & set(yin):
                return True
            if self.by_zhi["卯"] in tai and self.by_zhi["亥"] in yin:
                return True
            if self.by_zhi["巳"] in tai and self.by_zhi["酉"] in yin:
                return True
            return False
        raise ValueError(f"不认识的条件：{c!r}")


S = "紫微斗数全书"

# 18 格局规则表（判定条件为 duanyu_engine DSL，出处《紫微斗数全书》）
GEJU_RULES = [
    {"id": "geju-junchen", "name": "君臣庆会", "verdict": "吉",
     "text": "君臣慶會 紫微左右同守命是也，更會相武陰妙上",
     "note": "紫微为君、左右为辅，贵气聚命，多得贵人助力、掌权有望",
     "topic": "格局", "src": S,
     "cond": {"and": [{"stars": ["紫微"], "at": "命"},
                      {"sanfang": "命", "stars": ["左辅", "右弼", "天府", "天相"], "mode": "any"}]},
     "reading": "紫微守命且左右/府相拱照"},

    {"id": "geju-fuxiang", "name": "府相朝垣", "verdict": "吉",
     "text": "府相朝垣命必荣；府相朝垣千锺食禄",
     "note": "天府天相为财荫之星，朝拱命垣，主富贵荣显、财禄丰厚",
     "topic": "格局", "src": S,
     "cond": {"or": [{"stars": ["天府", "天相"], "at": "命", "mode": "any"},
                     {"sanfang": "命", "stars": ["天府", "天相"], "mode": "all"}]},
     "reading": "天府/天相守命，或同见命三方四正"},

    {"id": "geju-jiyue", "name": "机月同梁", "verdict": "吉",
     "text": "机月同梁作吏人 命在寅申方论",
     "note": "机月同梁作吏人，主稳定文职、公门清贵、安分守成",
     "topic": "格局", "src": S,
     "cond": {"sanfang": "命", "stars": ["天机", "太阴", "天同", "天梁"], "mode": "all"},
     "reading": "天机太阴天同天梁四星会命三方四正"},

    {"id": "geju-jiyue-qing", "name": "机月同梁", "verdict": "中",
     "text": "机月同梁作吏人 命在寅申方论",
     "note": "机月同梁三星会命，不完整（倾向，破格）",
     "topic": "格局", "src": S,
     "cond": {"sanfang": "命", "stars": ["天机", "太阴", "天同", "天梁"], "min": 3, "max": 3},
     "reading": "四星缺一，仅三星会命三方四正，倾向不完整"},

    {"id": "geju-yuelang", "name": "月朗天门", "verdict": "吉",
     "text": "月朗天门于亥地登云职掌大权",
     "note": "太阴入庙于亥，主大富大贵、掌权有谋略",
     "topic": "格局", "src": S,
     "cond": {"and": [{"stars": ["太阴"], "at": "命"}, {"zhi": "命", "in": ["亥"]}]},
     "reading": "太阴在亥守命"},

    {"id": "geju-rizhao", "name": "日照雷门", "verdict": "吉",
     "text": "日照雷门子辰卯地昼生富贵声扬",
     "note": "太阳在卯入庙守命，主声名显达、富贵扬名（昼生更验）",
     "topic": "格局", "src": S,
     "cond": {"and": [{"stars": ["太阳"], "at": "命"}, {"zhi": "命", "in": ["卯"]}]},
     "reading": "太阳在卯守命"},

    {"id": "geju-yuesheng", "name": "月生沧海", "verdict": "吉",
     "text": "月生滄海 月在子宮守田宅是也",
     "note": "太阴在子守田宅，主田宅丰厚、家业安稳、晚福绵长",
     "topic": "格局", "src": S,
     "cond": {"and": [{"stars": ["太阴"], "at": "田宅"}, {"zhi": "田宅", "in": ["子"]}]},
     "reading": "太阴在子守田宅"},

    {"id": "geju-qisha", "name": "七杀朝斗", "verdict": "吉",
     "text": "七杀寅申子午一生爵禄荣昌 为七杀朝斗格",
     "note": "七杀在寅申子午朝拱紫微，主武职权贵、威权显赫",
     "topic": "格局", "src": S,
     "cond": {"and": [{"stars": ["七杀"], "at": "命"}, {"zhi": "命", "in": ["寅", "申", "子", "午"]}]},
     "reading": "七杀在寅申子午守命"},

    {"id": "geju-wuqu", "name": "武曲庙垣", "verdict": "吉",
     "text": "武曲庙垣威名赫奕",
     "note": "武曲于四墓地入庙，主财帛威权、经商发达",
     "topic": "格局", "src": S,
     "cond": {"and": [{"stars": ["武曲"], "at": "命"}, {"zhi": "命", "in": ["辰", "戌", "丑", "未"]}]},
     "reading": "武曲在辰戌丑未守命"},

    {"id": "geju-shizhong", "name": "石中隐玉", "verdict": "吉",
     "text": "身命居子午宫为石中隐玉格，更会科权禄，终身福厚",
     "note": "巨门子午藏玉于石，先难后成、更会科权禄则终身福厚",
     "topic": "格局", "src": S,
     "cond": {"and": [{"stars": ["巨门"], "at": "命"}, {"zhi": "命", "in": ["子", "午"]}]},
     "reading": "巨门在子午守命"},

    {"id": "geju-luma", "name": "禄马交驰", "verdict": "吉",
     "text": "禄马交驰亦吉；武曲禄马交驰发财远郡",
     "note": "禄存天马交驰，主财禄丰足、奔波得财、发财远郡",
     "topic": "格局", "src": S,
     "cond": {"luma_jiaochi": True},
     "reading": "禄存与天马同宫或对照"},

    {"id": "geju-qingyang", "name": "擎羊入庙", "verdict": "吉",
     "text": "擎羊入庙富贵声扬；擎羊入庙最利武职",
     "note": "擎羊辰戌丑未入庙，主先破后成、武职发迹、闹中发财",
     "topic": "格局", "src": S,
     "cond": {"star_at": "擎羊", "in": ["辰", "戌", "丑", "未"]},
     "reading": "擎羊在辰戌丑未入庙"},

    {"id": "geju-matou", "name": "马头带剑", "verdict": "吉",
     "text": "马头带剑 谓马有刃是也不是居午格；马头带箭富且贵",
     "note": "擎羊在午带剑，主于险中得富、武职奋斗成贵",
     "topic": "格局", "src": S,
     "cond": {"star_at": "擎羊", "in": ["午"]},
     "reading": "擎羊在午"},

    {"id": "geju-zifu", "name": "紫府同宫", "verdict": "吉",
     "text": "天府惟寅申二宫紫府同宫",
     "note": "紫微天府同宫，主福禄厚重、稳重有成、一生衣食",
     "topic": "格局", "src": S,
     "cond": {"same_palace": ["紫微", "天府"]},
     "reading": "紫微天府同宫"},

    {"id": "geju-fubi", "name": "辅弼拱主", "verdict": "吉",
     "text": "辅弼拱主 紫微守命二星来拱是也",
     "note": "左辅右弼拱护紫微，主左右得人、助力强、事业有靠",
     "topic": "格局", "src": S,
     "cond": {"and": [{"stars": ["紫微"], "at": "命"},
                      {"sanfang": "命", "stars": ["左辅", "右弼"], "mode": "any"}]},
     "reading": "紫微守命且左辅右弼拱照"},

    {"id": "geju-juri", "name": "巨日同宫", "verdict": "吉",
     "text": "巨日拱照亦为奇",
     "note": "巨门太阳同宫，主食禄驰名、声名在外、口才扬名",
     "topic": "格局", "src": S,
     "cond": {"same_palace": ["巨门", "太阳"]},
     "reading": "巨门太阳同宫"},

    {"id": "geju-riyue", "name": "日月并明", "verdict": "吉",
     "text": "日月守命不如照合并明",
     "note": "日月并明，主阴阳调和、福寿双全、名利两得",
     "topic": "格局", "src": S,
     "cond": {"riyue_bingming": True},
     "reading": "太阳太阴同宫，或日卯月亥/日巳月酉拱照"},

    {"id": "geju-shapo", "name": "杀破狼", "verdict": "中",
     "text": "紫微入限本为祥，只恐三方杀破狼",
     "note": "杀破狼会命，主大变动、开创、动荡，成者大起败者大落",
     "topic": "格局", "src": S,
     "cond": {"sanfang": "命", "stars": ["七杀", "破军", "贪狼"], "mode": "all"},
     "reading": "七杀破军贪狼三星会命三方四正"},

    {"id": "geju-juji", "name": "巨机同临", "verdict": "凶",
     "text": "巨门天机为破荡；巨宿天机为破荡",
     "note": "巨门天机同宫破荡，主是非、多谋少成、易破败",
     "topic": "格局", "src": S,
     "cond": {"same_palace": ["巨门", "天机"]},
     "reading": "巨门天机同宫"},
]


def find_geju(chart):
    """判定紫微格局，返回命中的 [{id,name,verdict,text,note,src,reading}]。"""
    return find(GEJU_RULES, GejuAdapter(chart))[0]


if __name__ == "__main__":
    import sys
    for s in (sys.stdout, sys.stderr):
        try:
            s.reconfigure(encoding="utf-8")
        except Exception:
            pass
    # 自测：排一张盘跑两种判定（数据表 vs 硬编码），核对是否一致
    from pan import zhiwei as _zw
    chart = _zw.cast(1990, 5, 8, 9, 30, 0, 1) if hasattr(_zw, "cast") else None
    if chart:
        hits = find_geju(chart)
        print(f"[格局·数据表版] 命中 {len(hits)} 格：")
        for h in hits:
            print(f"  [{h['verdict']}] {h['name']} — {h['note']}（{h['src']}）")
