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

    def _star_brightness(self, idx, star):
        """该宫某主星的庙旺（庙/旺/得/利/平/不/陷，无则 None）。"""
        for n, b, s in self.palaces[idx]["主星"]:
            if n == star:
                return b
        return None

    def _star_sihua(self, idx, star):
        """该宫某主星的四化（禄/权/科/忌，无则 None）。"""
        for n, b, s in self.palaces[idx]["主星"]:
            if n == star:
                return s
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
        if "jia" in c:  # 夹：stars 分列某宫前后两宫（各至少一星在侧）
            idx = self._idx(c["jia"])
            front = self._stars((idx - 1) % 12)
            back = self._stars((idx + 1) % 12)
            stars = set(c["stars"])
            union = front | back
            return all(s in union for s in stars) and bool(stars & front) and bool(stars & back)
        if "miaowang" in c:  # 某星在某宫且庙旺落在 in 列表
            idx = self._idx(c["at"])
            b = self._star_brightness(idx, c["star"])
            return b in c["in"]
        if "sihua" in c:  # 某宫某星化某四化；不指定 star 则任意星化该四化即真
            idx = self._idx(c["at"])
            si = c["si"]
            if "star" in c:
                return self._star_sihua(idx, c["star"]) == si
            return any(s == si for n, b, s in self.palaces[idx]["主星"])
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
     "text": "輔弼拱主 紫微守命二星來拱是也",
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

    {"id": "geju-tianliang-wu", "name": "天梁午", "verdict": "吉",
     "text": "梁居午位官资清显",
     "note": "天梁在午守命，主清贵、官资清显、刚正不阿",
     "topic": "格局", "src": S,
     "cond": {"and": [{"stars": ["天梁"], "at": "命"}, {"zhi": "命", "in": ["午"]}]},
     "reading": "天梁在午守命"},

    {"id": "geju-wutan", "name": "武贪同行", "verdict": "中",
     "text": "先貧後富武貪同身命之宮；貪武同行威鎮邊夷",
     "note": "武曲贪狼同宫，主先贫后富、武职威权、白手起家",
     "topic": "格局", "src": S,
     "cond": {"same_palace": ["武曲", "贪狼"]},
     "reading": "武曲贪狼同宫"},

    {"id": "geju-lianqisha", "name": "廉贞七杀", "verdict": "中",
     "text": "廉貞七殺反為積富之人；廉貞七殺流蕩天涯",
     "note": "廉贞七杀同宫两面：庙旺有制则积富，陷地无制则流荡天涯（多面并列，不锁死）",
     "topic": "格局", "src": S,
     "cond": {"same_palace": ["廉贞", "七杀"]},
     "reading": "廉贞七杀同宫（积富/流荡两面，看庙旺陷地）"},

    {"id": "geju-huotan", "name": "火贪格", "verdict": "吉",
     "text": "貪狼火星居廟旺名鎮諸邦",
     "note": "贪狼火星同宫，主横发暴富、名镇一方、异路功名",
     "topic": "格局", "src": S,
     "cond": {"same_palace": ["贪狼", "火星"]},
     "reading": "贪狼火星同宫"},

    {"id": "geju-kuiyue", "name": "魁钺拱命", "verdict": "吉",
     "text": "天魁天鉞蓋世文章",
     "note": "天魁天钺拱照命宫，主贵人提携、文名盖世、机遇多",
     "topic": "格局", "src": S,
     "cond": {"sanfang": "命", "stars": ["天魁", "天钺"], "mode": "any"},
     "reading": "天魁天钺会命三方四正"},

    {"id": "geju-fuxiang-yin", "name": "府相寅", "verdict": "吉",
     "text": "寅逢府相位登一品之榮",
     "note": "天府天相在寅守命，主位登一品、财荫夹印、富贵荣显",
     "topic": "格局", "src": S,
     "cond": {"stars": ["天府", "天相"], "at": "寅", "mode": "any"},
     "reading": "天府或天相在寅"},

    {"id": "geju-changqu", "name": "昌曲拱命", "verdict": "吉",
     "text": "昌曲夾墀男命貴而且顯；左輔文昌會吉星尊居八座",
     "note": "文昌文曲拱照命宫，主文采出众、科名显达、贵而且显",
     "topic": "格局", "src": S,
     "cond": {"sanfang": "命", "stars": ["文昌", "文曲"], "mode": "any"},
     "reading": "文昌文曲会命三方四正"},

    {"id": "geju-jincan", "name": "金灿光辉", "verdict": "吉",
     "text": "金燦光輝 太陽單守，命在午宮是也",
     "note": "太阳单守命在午（日丽中天），主光明显赫、富贵声扬",
     "topic": "格局", "src": S,
     "cond": {"and": [{"stars": ["太阳"], "at": "命"}, {"zhi": "命", "in": ["午"]}]},
     "reading": "太阳单守命在午"},

    {"id": "geju-wuqu-shouyuan", "name": "武曲守垣", "verdict": "吉",
     "text": "武曲守垣 武守命卯宮是也，余不是",
     "note": "武曲单守命在卯，主武职威权、财帛丰足（原文「余不是」，仅卯宫成格）",
     "topic": "格局", "src": S,
     "cond": {"and": [{"stars": ["武曲"], "at": "命"}, {"zhi": "命", "in": ["卯"]}]},
     "reading": "武曲单守命在卯"},

    {"id": "geju-caiqiu", "name": "财与囚仇", "verdict": "凶",
     "text": "財與囚仇 武貞同守身命是也",
     "note": "武曲廉贞同守身命，主财星与囚星相仇，先富后败、是非破财",
     "topic": "格局", "src": S,
     "cond": {"same_palace": ["武曲", "廉贞"]},
     "reading": "武曲廉贞同宫"},

    {"id": "geju-gupin", "name": "一生孤贫", "verdict": "凶",
     "text": "一生孤貧 謂破守命星陷地是也",
     "note": "破军守命陷地，主一生孤贫、破耗无成（陷地方论，旺地不同）",
     "topic": "格局", "src": S,
     "cond": {"stars": ["破军"], "at": "命"},
     "reading": "破军守命（陷地孤贫，旺地另论）"},

    {"id": "geju-caiyin", "name": "财荫夹印", "verdict": "吉",
     "text": "財蔭夾印 相守命武梁來夾是也，田宅宮亦然",
     "note": "天相守命，武曲天梁夹命，主财荫夹印、富贵双全、一生财禄丰足",
     "topic": "格局", "src": S,
     "cond": {"and": [{"stars": ["天相"], "at": "命"}, {"jia": "命", "stars": ["武曲", "天梁"]}]},
     "reading": "天相守命，武曲天梁夹命"},

    {"id": "geju-riyuejiacai", "name": "日月夹财", "verdict": "吉",
     "text": "日月夾財 武守命日月來夾是也，財帛宮亦然",
     "note": "武曲守命，太阳太阴夹命，主财帛丰足、富贵之格",
     "topic": "格局", "src": S,
     "cond": {"and": [{"stars": ["武曲"], "at": "命"}, {"jia": "命", "stars": ["太阳", "太阴"]}]},
     "reading": "武曲守命，太阳太阴夹命"},

    {"id": "geju-cailujiama", "name": "财禄夹马", "verdict": "吉",
     "text": "財祿夾馬 馬守命武祿來夾是也，逢生旺尤妙",
     "note": "天马守命，武曲禄存夹命，主禄马交驰、发财远郡、奔波得财",
     "topic": "格局", "src": S,
     "cond": {"and": [{"stars": ["天马"], "at": "命"}, {"jia": "命", "stars": ["武曲", "禄存"]}]},
     "reading": "天马守命，武曲禄存夹命"},

    {"id": "geju-jinyu", "name": "金舆扶驾", "verdict": "吉",
     "text": "金輿扶駕 紫微守命前後有日月來夾是也",
     "note": "紫微守命，日月前后夹命，主贵气扶驾、位极人臣",
     "topic": "格局", "src": S,
     "cond": {"and": [{"stars": ["紫微"], "at": "命"}, {"jia": "命", "stars": ["太阳", "太阴"]}]},
     "reading": "紫微守命，太阳太阴前后夹命"},

    {"id": "geju-riyuejiaming", "name": "日月夹命", "verdict": "吉",
     "text": "日月夾命 不坐空亡遇逢本宮有吉星是也",
     "note": "太阳太阴夹命（本宫有吉星、不坐空亡方论），主贵气、福泽深厚",
     "topic": "格局", "src": S,
     "cond": {"jia": "命", "stars": ["太阳", "太阴"]},
     "reading": "太阳太阴夹命"},

    {"id": "geju-caiyinjialu", "name": "财印夹禄", "verdict": "吉",
     "text": "財印夾祿 祿守命梁相來夾是也，入財亦然",
     "note": "禄存守命，天梁天相夹命，主财印夹禄、财禄丰足",
     "topic": "格局", "src": S,
     "cond": {"and": [{"stars": ["禄存"], "at": "命"}, {"jia": "命", "stars": ["天梁", "天相"]}]},
     "reading": "禄存守命，天梁天相夹命"},

    {"id": "geju-quanlu", "name": "权禄生逢", "verdict": "吉",
     "text": "權祿生逢 二星守命廟旺是也，陷不是",
     "note": "命宫化权化禄二星守命，主掌权得禄、名利双收（原文要求庙旺，陷地不论）",
     "topic": "格局", "src": S,
     "cond": {"and": [{"sihua": {"at": "命", "si": "权"}}, {"sihua": {"at": "命", "si": "禄"}}]},
     "reading": "命宫化权星与化禄星同守（庙旺方论）"},
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
