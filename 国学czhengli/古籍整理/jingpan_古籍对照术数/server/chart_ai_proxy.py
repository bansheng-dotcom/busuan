#!/usr/bin/env python3
"""Thin proxy: POST /api/chart-ai-holographic → Cloudflare Workers AI (OpenAI-compatible)."""
from __future__ import annotations

import json
import os
import re
import sys
from datetime import date
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib import error, request

ROOT = Path(__file__).resolve().parent
ENV_FILE = ROOT / '.env'

# 仅拦「行动性」断语。勿含「大吉/大凶/吉凶」——模型常在解读提示写「不作大吉大凶」，会误杀并触发二次请求。
FORBIDDEN = re.compile(r'開運方法|改命|招財術|破財免|宜嫁娶|宜出行|命運好壞|必主大富|必主橫財')

DISCLAIMER_SPAN = re.compile(
    r'[^。！？\n]{0,30}(不[作做编編致提供]|禁止|勿|無|没有|並非|并非|僅供|仅供)[^。！？\n]{0,48}'
    r'(大吉|大凶|吉凶|開運|改命|宜忌|禍福|祸福|断语|斷語)[^。！？\n]{0,24}[。！？]?'
)

# 输出侧：仍像旧稿（引古文 / 逐宫）则判失败
DIVINATION_FORBIDDEN = re.compile(
    r'開運方法|改命|招財術|破財免|必主大富|必主橫財|必成無疑|必死|保證獲利|一定發財'
)

DIVINATION_NEED_OVERVIEW = re.compile(r'##\s*总览|##\s*總覽')

LIUREN_SYSTEM_PROMPT = """你是「经盘」六壬课解读助手。根据 JSON 用现代白话写一段简短解读。

规则：
1. 只用 JSON（kind、question、cast）里的信息，不编造未给出的落宫。
2. 全文白话。可写倾向（顺/滞、宜缓/宜动），禁止开运改命、绝对断语（必成/必死）、医疗法律投资指令。
3. 有 question：必须对着所问事项回答；无 question：写整体倾向，并说明用户未填写具体问题。
4. cast.luck / summary 是课式自带标签与摘要，可吸收进叙事，但不要夸大成铁口直断。

固定 Markdown 结构（标题一字不差）：
## 总览
## 对所问事项
（无问题时本节写整体倾向，首句说明未提问）
## 注意点
## 说明
（仅供参考，不作唯一决策依据）"""

YAOGUA_SYSTEM_PROMPT = """你是「经盘」三钱摇卦解读助手。根据 JSON 用现代白话写一段简短解读。

规则：
1. 只用 JSON（kind、question、cast）里的信息；不编造未给出的卦名或动爻。
2. 全文白话。可结合本卦/之卦 overview 与动爻写倾向，禁止开运改命、绝对断语、医疗法律投资指令。
3. 有 question：必须对着所问事项回答；无 question：写整体倾向，并说明用户未填写具体问题。
4. overview 是站内易经节选白话，消化进叙事，不要大段照抄。

固定 Markdown 结构（标题一字不差）：
## 总览
## 对所问事项
（无问题时本节写整体倾向，首句说明未提问）
## 注意点
## 说明
（仅供参考，不作唯一决策依据）"""

# ---------------------------------------------------------------------------
# 全息诊断（独立路由 /api/chart-ai-holographic）
# ---------------------------------------------------------------------------

HOLOGRAPHIC_SYSTEM_PROMPT = """你是「经盘」的紫微斗数全息诊断助手：冷酷、理性、手术刀式精准。只根据用户 JSON 解盘，禁止重排盘、改星、臆造未给出的星曜。

流派口径（固定声明，勿改口）：站内 iztro 三合安星 + 生年四化。首版不做宫干飞星链、不做八字交叉。

年龄锚点（优先读 JSON.ageGuide；与 meta.virtualAge / lifeStage 一致）：
- ageGuide.virtualAge / lifeStage / currentDecade.{range,palace,start,end} 为当前虚岁与当前大限。
- ageGuide.nearYearMaxAge / nearYearMaxYear：🟡3～5年可写到的虚岁与公历年上限（通常=当前大限终点）。禁止写「虚岁N」或流年公历年超过该上限却仍挂在当前大限下。
- ageGuide.nearYearsStayInDecade=true 时：🔴与🟡全部仍在当前大限，大限年龄段只能抄 currentDecade.range。
- ageGuide.writing 为阶段写作指令，必须遵守。

数据边界（必须遵守，违反即失败）：
- mutagens / palaces[*].stars 才是本命星与生年四化落宫；同一主星只能落在 JSON 标明的那一宫，禁止把七杀/贪狼/天府等写成同时在命宫又在事业宫。写「X宫紫微天府」时两颗星都必须真在该宫。
- 生年四化落点以 mutagens 为准：写「X化忌」只能写在 mutagens.忌.palace，禁止把「疾厄宫天机化忌」说成「命宫廉贞化忌」。
- nearTerm.years[*].decadePalace / decadeStars：该年虚岁落入的大限宫叠宫提示。
- nearTerm.years[*].yearlyGanZhi / yearlyMingPalace / yearlyMutagen / yearlyFlow：真实流年材料。写 1 年战术时优先引用；禁止编造 JSON 没有的流曜名或四化落点。
- 若某年缺少 yearlyFlow，该年禁止写流魁/流曲等具体流曜名。
- 疾厄、羊陀、空劫等落宫必须与 palaces 一致。
- [依据: …] 只能写给人看的宫名/星名/年份，例如「[依据: 2026流年命宫迁移·破军]」「[依据: 生年忌天机在疾厄]」。绝对禁止写出 JSON 字段路径（如 nearTerm.years[6]、yearlyMutagen.忌、decades[0].palace、ageGuide）。

硬约束：
1. 直接从「## 验盘校准」起笔；禁止复述本提示、注意事项、格式说明。
2. 解盘顺序强制：象（命宫三方四正 sanFangMing）→ 数（mutagens 生年四化）→ 时（decades / nearTerm）。禁止单宫乱断。
3. 每个关键结论必须可反追问，格式如 [依据: 财帛宫武曲化禄]；禁止空洞巴纳姆套话。
4. 空宫（emptyMajor=true）须借对宫主星并注明「借对宫」。
5. 禁止开运改命术、就医处方、具体买卖/投资指令；疾厄只写易累部位与作息/压力倾向（用脑过度、筋骨紧、睡眠不稳、视力疲劳等）。禁止确诊病名与病理标签（如神经衰弱、抑郁症、癌症、残废、昏盲、心血管疾病等）及手术断言。理财只写「易耗散/宜守成」类盘面倾向，禁止「忌投机/投资需谨慎/严控开支」等操作指令。
6. 材料不足处写「从本盘不易具体推到」，勿硬编年份事件。
7. 须对照 meta.gender 写他/她；勿默认男命语气。
8. 年龄口径：严格按 ageGuide（及 meta.virtualAge / lifeStage）。
   - child：六维财富/事业/婚恋必须用「长大后倾向：…」起句；婚恋固定「长大后感情模式倾向：…」，禁止感情生活丰富/烂桃花/花花公子/异性缘极好等现时恋爱词；时空战略只写学业、家庭、身心作息、兴趣、环境/出行。
   - youth：可写升学与早期职业探索，勿写婚恋定局；勿滥用「长大后」。
   - adult：六维写现况倾向，禁止出现「长大后」「长大后倾向」。
9. 大限对齐：🔴/🟡 每段可写一句「虚岁N · 大限R · 宫P」。🟡只写**一段**（虚岁跨度一句总览，可点 2～3 个流年忌点），禁止拆成多个🟡逐年各写一段；年限不得超过 nearYearMaxAge / nearYearMaxYear。🟢当前大限只写一段总述（本限主题+1～2依据），禁止把虚岁25、26…34逐年各写一行。🟢/大限段落的宫位与星曜必须抄 decades / ageGuide.currentDecade，禁止把命宫主星写成「大限宫武曲天府同宫」这类挪移。
10. 禁止自相矛盾（极常见失败项，务必自检）：
   - 命宫已有武曲/天府/文曲/文昌/辅弼等时，**绝对禁止**写「命宫无吉星/无吉曜」。短板只写迁移对宫煞曜夹制、四化忌耗等。
   - 称「文武格」当且仅当文曲与武曲同在身命；称「文星朝命」须文昌在命。二者不可混用。
   - 禁止同段既写「命宫有文曲」又写「文曲不在命宫」。
   - 「化囚」是廉贞星性，不是生年四化，勿与 mutagens 混淆。十四主星落宫须与 palaces 一致。
11. 若 JSON.guardNotes 非空：视为本盘硬提醒，全文必须遵守，不可反着写。
12. [依据] 与正文禁止出现 JSON 字段名（如 palaces、mutagens、ageGuide、nearTerm、guardNotes、decades）。

写作流程：
A. 验盘校准：若 JSON.timeline 有 1～2 条大事，尽量用 decades / nearTerm 对验；对不上写「与本盘材料不易吻合，建议复核时辰」，但继续全文。若无 timeline 或为空：本节只写一句「未提供大事年表，本节跳过」。
B. 命格X光：先据 sanFangMing + 命宫星定成格/破格；底层驱动力（名/利/情/权）；致命短板须能在 palaces/mutagens 对上号，禁止自相矛盾。格局名必须与落星一致：武曲天府同宫勿称「府相朝垣」（府相须天府+天**同宫**；三方另宫见天相也不算）；文昌不在命宫勿称「文星朝命」；文曲武曲在命可称「文武格」。优先采用 JSON.patterns 已给出的格局名。
C. 四化焦点：严格按 mutagens 写化禄/化忌/权/科落宫各一句；理财只写盘面倾向，禁止「宜投资/把握时机」等行动指令。
D. 六维深度：财富、事业、婚恋、六亲、疾厄、福德。每维：一句结论 + [依据: …] + 一句「白话对照：…」。child 按第8条；adult 禁止「长大后」。
E. 时空战略：🔴约1年；🟡一段 3～5年总览（≤nearYearMaxAge/Year）；🟢当前大限一段总述（勿逐年罗列虚岁）。
F. 易误判点：用读者能懂的话纠正常见误读（须与 mutagens/palaces 一致）；禁止复述系统指令原文（如「绝对禁止写…」），改写成「有人以为…，其实…」。纠正「文星朝命」时勿否定命宫已有的文曲。
G. 专家结语：一句直断 + 免责「以上为盘面逻辑推演，仅供参考，不作唯一决策依据」。

固定 Markdown 结构（标题一字不差）：
## 验盘校准
## 命格X光
## 四化焦点
## 六维深度
## 时空战略
## 易误判点
## 专家结语"""

HOLOGRAPHIC_RETRY_HINT = (
    '上一稿不合格。请重写全息诊断：第一行必须是「## 验盘校准」；'
    '必须含「## 命格X光」「## 四化焦点」「## 六维深度」「## 时空战略」「## 易误判点」「## 专家结语」；'
    '六维每块须有 [依据: …] 与白话对照；[依据] 禁止 JSON 字段名与 ageGuide；'
    '流曜只能引用该年 yearlyFlow；生年忌只写在 mutagens.忌 的宫；'
    '禁止神经衰弱等病名；命宫有武曲/天府/文曲/文昌时禁止写「命宫无吉星」；'
    '称文武格时可写文曲武曲在命，但禁止同段又写「文曲不在命宫」；'
    '必须遵守 ageGuide 与 guardNotes；时空每段首句「虚岁N · 大限R · 宫P」，R 抄 currentDecade.range；'
    '🟡只写一段总览，不得超过 nearYearMaxAge/nearYearMaxYear；'
    'nearYearsStayInDecade=true 时禁止写下一限年龄段；'
    'lifeStage=child 时六维用「长大后倾向」；lifeStage=adult 禁止「长大后」；'
    '🟢当前大限只写一段总述，禁止虚岁逐年罗列；'
    '十四主星落宫必须与 palaces 一致，禁止同一主星写进两个宫；大限宫星须抄 decades，勿把命宫星挪到大限宫；'
    '武曲天府勿称府相朝垣（三方另宫天相也不算府相）；文昌不在命勿称文星朝命；文曲武曲在命可称文武格；'
    '禁止 JSON 字段名泄漏到正文或依据；禁止昏盲等病名与投资操作指令；禁止重排盘。'
)

HOLO_NEED_CALIBRATION = re.compile(r'##\s*验盘校准|##\s*驗盤校準')
HOLO_NEED_KERNEL = re.compile(r'##\s*命格X光|##\s*命格ｘ光', re.IGNORECASE)
HOLO_NEED_MUTAGEN = re.compile(r'##\s*四化焦点|##\s*四化焦點')
HOLO_NEED_MATRIX = re.compile(r'##\s*六维深度|##\s*六維深度')
HOLO_NEED_TEMPORAL = re.compile(r'##\s*时空战略|##\s*時空戰略')
HOLO_NEED_PITFALL = re.compile(r'##\s*易误判点|##\s*易誤判點')
HOLO_NEED_ENDING = re.compile(r'##\s*专家结语|##\s*專家結語')
HOLO_EVIDENCE = re.compile(r'\[依据[:：]|\[依據[:：]')
# 依据里泄漏 JSON 路径
HOLO_JSON_LEAK = re.compile(
    r'nearTerm|yearlyMutagen|yearlyFlow|yearlyMingPalace|yearlyGanZhi|ageGuide|'
    r'years\s*\[\s*\d+\s*\]|decades\s*\[\s*\d+\s*\]|palaces\s*\[\s*\d+\s*\]|'
    r'mutagens\.(?:禄|權|权|科|忌)|dataLimits|emptyMajor|currentDecade|nearYearsStayInDecade|'
    r'nearYearMaxAge|nearYearMaxYear'
)
# 确诊病名 / 过硬病理标签
HOLO_CLINICAL = re.compile(
    r'神经衰弱|憂鬱症|抑郁症|焦慮症|焦虑症|精神分裂|自閉|自闭|癌症|腫瘤|肿瘤|'
    r'殘疾|残疾|白血病|心臟病|心脏病发作|中風|中风偏瘫|偏头痛|偏頭痛|'
    r'昏盲|失明|心血管疾病|冠心病|脑溢血|腦溢血'
)
# child 盘不应写成正在谈恋爱
HOLO_CHILD_ROMANCE = re.compile(
    r'感情生活丰富|感情经历丰富|烂桃花|爛桃花|花花公子|桃花劫|见异思迁|見異思遷|'
    r'情场|情場得意|因情破财|因情破財|容易遇到喜欢的人|'
    r'异性缘极好|異性緣極好|感情波折|因情生事|因情误事|因情誤事'
)
# 「命宫无吉星」与「文星朝命 / 文昌文曲值命」类正文自相矛盾（他宫文昌不算）
HOLO_MING_NO_JI = re.compile(
    r'命宫无吉星|命宮無吉星|命宫無吉星|命宫无吉曜|命宮無吉曜|'
    r'命宫虽无吉|命宮雖無吉|命宫卻无吉|命宫却无吉|命宮卻無吉'
)
HOLO_MING_WEN_CLAIM = re.compile(
    r'文星朝命|文星朝斗|文昌文曲值命|文曲文昌值命|文武格|'
    r'命宫[^。\n]{0,28}(?:文昌|文曲)|(?:文昌|文曲)[^。\n]{0,12}(?:值命|同宫|同宮)'
)
HOLO_BAIHUA = re.compile(r'白话对照|白話對照')
HOLO_DECADE_AGE_RANGE = re.compile(r'(\d{1,2})\s*[-–—～~]\s*(\d{1,2})\s*岁')
HOLO_XU_SUI = re.compile(r'虚岁\s*(\d{1,2})')
HOLO_XU_SUI_SPAN = re.compile(r'虚岁\s*(\d{1,2})\s*[-–—～~至到]\s*(\d{1,2})')
HOLO_YEAR_TOKEN = re.compile(r'(?<!\d)(20\d{2})(?!\d)')
# 本盘 JSON 通常不含流曜/流年四化；正文出现则视为臆造
HOLO_GROWN_UP = re.compile(r'长大后|長大後')
HOLO_INVENTED_FLOW = re.compile(
    r'流[魁鉞钺昌曲羊陀祿禄權权科忌]|流年四化|大限四化|运[祿禄權权科忌]|運[祿禄權权科忌]'
)

def compact_holographic_payload(body: dict) -> dict:
    """全息：保留宫名/星名/四化；标空宫；附 timeline。"""
    meta_in = body.get('meta') if isinstance(body.get('meta'), dict) else {}
    meta = {
        k: meta_in[k]
        for k in ('solarDate', 'gender', 'lunarDate', 'fiveElementsClass', 'soul', 'body')
        if meta_in.get(k)
    }
    if not meta.get('fiveElementsClass') and body.get('fiveElementsClass'):
        meta['fiveElementsClass'] = body['fiveElementsClass']

    mutagen_map: dict[str, dict] = {}
    palaces_out: list[dict] = []
    for item in (body.get('palaces') or [])[:12]:
        if not isinstance(item, dict):
            continue
        name = str(item.get('aliasName') or item.get('name') or '').strip()
        raw_name = str(item.get('name') or '').strip()
        stars = normalize_stars(item.get('stars'), 16)
        empty_major = bool(item.get('emptyMajor')) if 'emptyMajor' in item else len(stars) == 0
        row = {
            'palace': name or raw_name,
            'branch': str(item.get('earthlyBranch') or ''),
            'stem': str(item.get('heavenlyStem') or ''),
            'isBody': bool(item.get('isBodyPalace')),
            'isMing': raw_name in ('命宫', '命宮') or name in ('命宫', '命宮'),
            'emptyMajor': empty_major,
            'stars': stars,
        }
        palaces_out.append(row)
        for star in stars:
            m = str(star.get('mutagen') or '').strip()
            if not m:
                continue
            key = m.replace('祿', '禄').replace('權', '权')
            mutagen_map[key] = {
                'star': star.get('name'),
                'palace': row['palace'],
                'branch': row['branch'],
                'brightness': star.get('brightness'),
            }

    san_raw = body.get('sanFangMing')
    san_fang = None
    if isinstance(san_raw, dict):
        def corner_keep(raw: object) -> dict:
            if not isinstance(raw, dict):
                return {'palace': '', 'stars': []}
            return {
                'palace': str(raw.get('palace') or ''),
                'stars': normalize_stars(raw.get('stars'), 14),
            }

        san_fang = {
            'self': corner_keep(san_raw.get('self')),
            'opposite': corner_keep(san_raw.get('opposite')),
            'triA': corner_keep(san_raw.get('triA')),
            'triB': corner_keep(san_raw.get('triB')),
        }

    decades = []
    for item in (body.get('decades') or [])[:12]:
        if not isinstance(item, dict):
            continue
        start = item.get('start')
        if isinstance(start, int) and start > 85:
            continue
        if len(decades) >= 8:
            break
        decades.append(
            {
                'range': item.get('range', ''),
                'start': item.get('start'),
                'end': item.get('end'),
                'palace': str(item.get('themePalace') or item.get('palace') or ''),
                'stars': normalize_stars(item.get('stars'), 12),
            }
        )

    near_raw = body.get('nearTerm') if isinstance(body.get('nearTerm'), dict) else None
    near_term = None
    allowed_flow_stars: set[str] = set()
    has_yearly_mutagen = False
    if near_raw:
        years_out = []
        for item in (near_raw.get('years') or [])[:11]:
            if not isinstance(item, dict):
                continue
            year_row: dict = {
                'year': item.get('year'),
                'age': item.get('age'),
                'isCurrent': bool(item.get('isCurrent')),
                'decadeRange': item.get('decadeRange', ''),
                'decadePalace': str(item.get('themePalace') or item.get('palace') or ''),
                'decadeStars': normalize_stars(item.get('stars'), 8),
            }
            gan = str(item.get('yearlyGanZhi') or '').strip()
            if gan:
                year_row['yearlyGanZhi'] = gan
            ming = str(item.get('yearlyMingPalace') or '').strip()
            if ming:
                year_row['yearlyMingPalace'] = ming
            ym = item.get('yearlyMutagen')
            if isinstance(ym, dict) and ym:
                cleaned_m: dict = {}
                for key in ('禄', '權', '权', '科', '忌', '祿'):
                    cell = ym.get(key)
                    if not isinstance(cell, dict) or not cell.get('star'):
                        continue
                    norm_key = (
                        '禄'
                        if key in ('禄', '祿')
                        else '权'
                        if key in ('权', '權')
                        else key
                    )
                    cleaned_m[norm_key] = {
                        'star': str(cell.get('star')),
                        'palace': str(cell.get('palace') or ''),
                    }
                if cleaned_m:
                    year_row['yearlyMutagen'] = cleaned_m
                    has_yearly_mutagen = True
            flow_raw = item.get('yearlyFlow')
            if isinstance(flow_raw, list) and flow_raw:
                flow_out = []
                for fr in flow_raw[:14]:
                    if not isinstance(fr, dict) or not fr.get('name'):
                        continue
                    fname = str(fr['name']).strip()
                    flow_out.append({'name': fname, 'palace': str(fr.get('palace') or '')})
                    allowed_flow_stars.add(fname)
                if flow_out:
                    year_row['yearlyFlow'] = flow_out
            years_out.append(year_row)
        near_term = {
            'fromYear': near_raw.get('fromYear'),
            'toYear': near_raw.get('toYear'),
            'currentYear': near_raw.get('currentYear'),
            'years': years_out,
        }

    patterns_out: list[dict] = []
    ming_star_names: set[str] = set()
    palace_star_map: dict[str, set[str]] = {}
    for row in palaces_out:
        pname = str(row.get('palace') or '')
        names = {str(s.get('name') or '') for s in (row.get('stars') or []) if isinstance(s, dict)}
        palace_star_map[pname] = names
        if row.get('isMing') or pname in ('命宫', '命宮'):
            ming_star_names |= names
        # alias 事业 <-> 官禄
        if pname in ('事业', '事業', '官禄', '官祿'):
            palace_star_map.setdefault('官禄宫', set()).update(names)
            palace_star_map.setdefault('事业宫', set()).update(names)

    for item in (body.get('patterns') or [])[:8]:
        if not isinstance(item, dict) or not item.get('name'):
            continue
        name = str(item.get('name'))
        cond = str(item.get('condition') or '')
        # 文昌不在命宫时，勿把「文星朝命格」喂给模型
        if ('文星朝命' in name or '文昌文曲值命' in cond) and '文昌' not in ming_star_names:
            continue
        patterns_out.append(
            {
                'name': name,
                'condition': trim_text(cond, 80),
            }
        )

    book_quotes: list[dict] = []
    for item in (body.get('bookQuotes') or [])[:24]:
        if not isinstance(item, dict):
            continue
        vern = clean_vernacular(str(item.get('vernacular') or ''))
        if len(vern) < 6:
            continue
        # 去掉病理标签，避免模型照抄「昏盲」等
        if HOLO_CLINICAL.search(vern):
            vern = HOLO_CLINICAL.sub('压力倾向', vern)
        palace = str(item.get('palace') or '')
        # 「官禄遇紫府」类：天府不在官禄/事业时不喂，防写成事业宫紫微天府
        if ('紫府' in vern or '紫微天府' in vern) and palace in (
            '事业',
            '官禄',
            '官祿',
            '事业宫',
            '官禄宫',
        ):
            career_stars = palace_star_map.get('官禄宫') or palace_star_map.get('事业宫') or set()
            if '天府' not in career_stars:
                continue
        book_quotes.append(
            {
                'source': str(item.get('source') or ''),
                'palace': palace,
                'vernacular': trim_text(vern, 100),
            }
        )

    timeline_out: list[dict] = []
    for item in (body.get('timeline') or [])[:2]:
        if not isinstance(item, dict):
            continue
        try:
            year = int(item.get('year'))
        except (TypeError, ValueError):
            continue
        event = trim_text(str(item.get('event') or '').strip(), 80)
        if not event:
            continue
        timeline_out.append({'year': year, 'event': event})

    try:
        anchor = int(body.get('anchorYear') or date.today().year)
    except (TypeError, ValueError):
        anchor = date.today().year

    virtual_age = None
    solar = str(meta.get('solarDate') or '')
    m_year = re.match(r'^(\d{4})', solar)
    if m_year:
        try:
            birth_year = int(m_year.group(1))
            virtual_age = anchor - birth_year + 1
        except ValueError:
            virtual_age = None
    if isinstance(virtual_age, int) and virtual_age < 16:
        life_stage = 'child'
    elif isinstance(virtual_age, int) and virtual_age < 22:
        life_stage = 'youth'
    else:
        life_stage = 'adult'

    if virtual_age is not None:
        meta = {**meta, 'virtualAge': virtual_age, 'lifeStage': life_stage}

    age_guide = build_holographic_age_guide(
        virtual_age=virtual_age,
        life_stage=life_stage,
        decades=decades,
        near_term=near_term,
    )
    guard_notes = build_holographic_guard_notes(
        palaces_out,
        patterns_out,
        mutagen_map,
        decades=decades,
        virtual_age=virtual_age,
    )

    return {
        'meta': meta,
        'ageGuide': age_guide,
        'guardNotes': guard_notes or None,
        'mutagens': mutagen_map or None,
        'sanFangMing': san_fang,
        'palaces': palaces_out,
        'decades': decades,
        'nearTerm': near_term,
        'patterns': patterns_out,
        'bookQuotes': book_quotes,
        'timeline': timeline_out or None,
        'anchorYear': anchor,
        'methodNote': 'iztro三合安星+生年四化；流年取自nearTerm.yearly*；年龄口径见ageGuide',
        'dataLimits': {
            'natalMutagensOnly': True,
            'nearTermHasDecadeOverlay': True,
            'hasFlowStars': bool(allowed_flow_stars),
            'hasYearlyMutagens': has_yearly_mutagen,
            'allowedFlowStars': sorted(allowed_flow_stars) if allowed_flow_stars else [],
            'lifeStage': life_stage,
        },
    }


def build_holographic_guard_notes(
    palaces: list,
    patterns: list,
    mutagens: dict,
    decades: list | None = None,
    virtual_age: int | None = None,
) -> list[str]:
    """按本盘星曜生成短护栏，压常见自相矛盾。"""
    notes: list[str] = []
    ming_names: list[str] = []
    for item in palaces or []:
        if not isinstance(item, dict):
            continue
        if item.get('isMing') or str(item.get('palace') or '') in ('命宫', '命宮'):
            ming_names = [
                str(s.get('name') or '')
                for s in (item.get('stars') or [])
                if isinstance(s, dict) and s.get('name')
            ]
            break
    ming_set = set(ming_names)
    auspicious = {'武曲', '天府', '文曲', '文昌', '紫微', '天相', '左辅', '右弼', '天魁', '天钺', '禄存'}
    hit = sorted(ming_set & auspicious)
    if hit:
        notes.append(
            f'命宫有{"、".join(hit)}，禁止写「命宫无吉星/无吉曜」；短板只写对宫煞曜或四化忌耗。'
        )
    if '文曲' in ming_set and '武曲' in ming_set:
        notes.append('命宫文曲+武曲，可称「文武格」；禁止写「文曲不在命宫」。')
    if '文昌' not in ming_set:
        notes.append('文昌不在命宫，禁止称「文星朝命」；提及该错称时只能否定，不可改口说昌曲俱在命。')
    if '天府' in ming_set and '武曲' in ming_set and '天相' not in ming_set:
        notes.append(
            '命宫武曲天府同宫，勿称「府相朝垣」。府相朝垣须天府与天相同宫；'
            '三方四正另宫见天相也不算府相朝垣。'
        )
    for pat in patterns or []:
        if not isinstance(pat, dict):
            continue
        name = str(pat.get('name') or '').strip()
        cond = str(pat.get('condition') or '').strip()
        if name:
            notes.append(f'本盘已匹配格局「{name}」' + (f'（{cond}）' if cond else '') + '，优先采用此名。')
    ji = mutagens.get('忌') if isinstance(mutagens, dict) else None
    if isinstance(ji, dict) and ji.get('star') and ji.get('palace'):
        notes.append(f'生年忌为{ji["star"]}在{ji["palace"]}，写化忌只落此宫。')
    _append_decade_guard(notes, decades or [], virtual_age)
    return notes[:8]


def _append_decade_guard(notes: list[str], decades: list, virtual_age: int | None) -> None:
    if not isinstance(virtual_age, int):
        return
    for item in decades or []:
        if not isinstance(item, dict):
            continue
        try:
            start = int(item['start']) if item.get('start') is not None else None
            end = int(item['end']) if item.get('end') is not None else None
        except (TypeError, ValueError):
            continue
        if start is None or end is None or not (start <= virtual_age <= end):
            continue
        palace = str(item.get('palace') or '').strip()
        stars = [
            str(s.get('name') or '')
            for s in (item.get('stars') or [])
            if isinstance(s, dict) and s.get('name')
        ]
        if palace and stars:
            notes.append(
                f'当前大限在{palace}，大限星为{"、".join(stars[:6])}；'
                f'写🟢/大限时禁止把命宫主星写成「{palace}某某同宫」。'
            )
        elif palace:
            notes.append(f'当前大限在{palace}；写大限星须与 decades 一致，勿挪移命宫星。')
        break


def build_holographic_age_guide(
    virtual_age: int | None,
    life_stage: str,
    decades: list,
    near_term: dict | None,
) -> dict:
    """给模型的显式年龄/大限锚点，减少童盘成人写、大限跳段。"""
    current: dict = {'range': '', 'palace': '', 'start': None, 'end': None}
    if isinstance(virtual_age, int):
        for item in decades or []:
            if not isinstance(item, dict):
                continue
            start, end = item.get('start'), item.get('end')
            try:
                start_i = int(start) if start is not None else None
                end_i = int(end) if end is not None else None
            except (TypeError, ValueError):
                continue
            if isinstance(start_i, int) and isinstance(end_i, int) and start_i <= virtual_age <= end_i:
                current = {
                    'range': _normalize_decade_range(item.get('range') or f'{start_i}-{end_i}'),
                    'palace': str(item.get('palace') or ''),
                    'start': start_i,
                    'end': end_i,
                }
                break
        if not current.get('range'):
            years = (near_term or {}).get('years') or []
            for item in years:
                if not isinstance(item, dict):
                    continue
                if item.get('isCurrent') or item.get('age') == virtual_age:
                    current = {
                        'range': _normalize_decade_range(item.get('decadeRange')),
                        'palace': str(item.get('decadePalace') or ''),
                        'start': None,
                        'end': None,
                    }
                    nums = re.findall(r'\d+', str(item.get('decadeRange') or ''))
                    if len(nums) >= 2:
                        current['start'] = int(nums[0])
                        current['end'] = int(nums[1])
                    break

    decade_end = current.get('end')
    try:
        decade_end = int(decade_end) if decade_end is not None else None
    except (TypeError, ValueError):
        decade_end = None

    near_ages: list[int] = []
    near_ranges: set[str] = set()
    year_by_age: dict[int, int] = {}
    for item in (near_term or {}).get('years') or []:
        if not isinstance(item, dict):
            continue
        try:
            ya = int(item['age']) if item.get('age') is not None else None
        except (TypeError, ValueError, KeyError):
            ya = None
        try:
            yy = int(item['year']) if item.get('year') is not None else None
        except (TypeError, ValueError, KeyError):
            yy = None
        if not isinstance(virtual_age, int) or not isinstance(ya, int):
            continue
        if virtual_age <= ya <= virtual_age + 5:
            near_ages.append(ya)
            nr = _normalize_decade_range(item.get('decadeRange'))
            if nr:
                near_ranges.add(nr)
            if isinstance(yy, int):
                year_by_age[ya] = yy

    # 黄段上限：当前大限终点与「当前虚岁+5」取较小；只保留仍在本限内的近中期
    horizon = virtual_age + 5 if isinstance(virtual_age, int) else None
    near_year_max_age = None
    if isinstance(decade_end, int) and isinstance(virtual_age, int):
        near_year_max_age = min(decade_end, horizon) if isinstance(horizon, int) else decade_end
    elif isinstance(horizon, int):
        near_year_max_age = horizon

    ages_in_cap = [
        a
        for a in near_ages
        if not isinstance(near_year_max_age, int) or a <= near_year_max_age
    ]
    cur_range = str(current.get('range') or '')
    stay = True
    if cur_range and ages_in_cap:
        age_to_range = {}
        for it in (near_term or {}).get('years') or []:
            if not isinstance(it, dict):
                continue
            try:
                a = int(it.get('age'))
            except (TypeError, ValueError):
                continue
            nr = _normalize_decade_range(it.get('decadeRange'))
            if nr:
                age_to_range[a] = nr
        for a in ages_in_cap:
            nr = age_to_range.get(a)
            if nr and nr != cur_range:
                stay = False
                break
    elif cur_range and near_ranges:
        stay = near_ranges <= {cur_range}
    elif not cur_range:
        stay = False

    near_year_max_year = None
    if isinstance(near_year_max_age, int):
        if near_year_max_age in year_by_age:
            near_year_max_year = year_by_age[near_year_max_age]
        elif isinstance(virtual_age, int) and virtual_age in year_by_age:
            near_year_max_year = year_by_age[virtual_age] + (near_year_max_age - virtual_age)

    if life_stage == 'child':
        writing = (
            '童盘：六维财富/事业/婚恋用「长大后倾向」；'
            '婚恋写「长大后感情模式倾向」；'
            '时空只写学业、家庭、身心作息、兴趣、出行；'
            '疾厄只写部位与作息压力，禁病名。'
        )
    elif life_stage == 'youth':
        writing = '青年：可写升学与早期职业探索；勿写婚恋定局；大限抄 nearTerm/currentDecade。'
    else:
        writing = (
            '成人：六维写现况倾向，禁止「长大后」「长大后倾向」；'
            '🟢当前大限只写一段总述，禁止虚岁逐年罗列。'
        )

    if isinstance(near_year_max_age, int):
        writing += (
            f' 🟡3～5年虚岁上限{near_year_max_age}'
            + (f'（公历至{near_year_max_year}）' if near_year_max_year else '')
            + '，禁止把下一限虚岁/年份仍挂在当前大限下。'
        )

    return {
        'virtualAge': virtual_age,
        'lifeStage': life_stage,
        'currentDecade': current,
        'nearYearAges': ages_in_cap,
        'nearYearMaxAge': near_year_max_age,
        'nearYearMaxYear': near_year_max_year,
        'nearYearsStayInDecade': stay,
        'writing': writing,
    }


def extract_holographic_body(text: str) -> str:
    raw = (text or '').strip()
    if not raw:
        return raw
    raw = re.sub(
        r'</?redacted_thinking>.*?(?:</think>|$)',
        '',
        raw,
        flags=re.DOTALL | re.IGNORECASE,
    )
    m = re.search(r'^##\s*验盘校准|^##\s*驗盤校準', raw, re.MULTILINE)
    if m and m.start() > 0:
        raw = raw[m.start():]
    return raw.strip()


def violates_holographic_style(text: str) -> bool:
    raw = text or ''
    checks = (
        HOLO_NEED_CALIBRATION,
        HOLO_NEED_KERNEL,
        HOLO_NEED_MUTAGEN,
        HOLO_NEED_MATRIX,
        HOLO_NEED_TEMPORAL,
        HOLO_NEED_PITFALL,
        HOLO_NEED_ENDING,
    )
    return any(not pat.search(raw) for pat in checks)


def holographic_evidence_thin(text: str) -> bool:
    """依据括号不足且白话对照也很少时才判薄。"""
    raw = text or ''
    ev = len(HOLO_EVIDENCE.findall(raw))
    bv = len(HOLO_BAIHUA.findall(raw))
    return ev < 3 and bv < 5


def holographic_invented_flow(text: str, allowed: set[str] | None = None) -> bool:
    """正文出现的流曜名若不在 allowed（来自 nearTerm.yearlyFlow）则视为臆造。"""
    raw = text or ''
    allow = allowed or set()
    for match in re.finditer(r'流[魁鉞钺昌曲羊陀祿禄喜鸾鸞馬马]', raw):
        if match.group(0) not in allow:
            return True
    if re.search(r'大限四化', raw):
        return True
    return False


def holographic_json_leak(text: str) -> bool:
    """依据或正文泄漏 JSON 字段路径。"""
    return bool(HOLO_JSON_LEAK.search(text or ''))


def holographic_clinical_terms(text: str) -> bool:
    return bool(HOLO_CLINICAL.search(text or ''))


def holographic_child_romance_tone(text: str, compact: dict) -> bool:
    meta = compact.get('meta') if isinstance(compact.get('meta'), dict) else {}
    stage = str(meta.get('lifeStage') or '')
    if stage != 'child':
        limits = compact.get('dataLimits') if isinstance(compact.get('dataLimits'), dict) else {}
        if str(limits.get('lifeStage') or '') != 'child':
            return False
    return bool(HOLO_CHILD_ROMANCE.search(text or ''))


def _ming_palace_has_wen_stars(compact: dict) -> bool:
    for item in compact.get('palaces') or []:
        if not isinstance(item, dict):
            continue
        name = str(item.get('palace') or '')
        if not (item.get('isMing') or name in ('命宫', '命宮')):
                continue
        for star in item.get('stars') or []:
            if not isinstance(star, dict):
                continue
            sn = str(star.get('name') or '')
            if '文昌' in sn or '文曲' in sn:
                return True
        return False
    san = compact.get('sanFangMing') if isinstance(compact.get('sanFangMing'), dict) else {}
    self_corner = san.get('self') if isinstance(san.get('self'), dict) else {}
    for star in self_corner.get('stars') or []:
        if not isinstance(star, dict):
            continue
        sn = str(star.get('name') or '')
        if '文昌' in sn or '文曲' in sn:
            return True
    return False


def holographic_ming_contradiction(text: str, compact: dict | None = None) -> bool:
    """正文肯定地写「命宫无吉星」：命宫已有吉曜/文星朝命类表述时判矛盾。否定句不触发。"""
    raw = text or ''
    affirmed_no_ji = False
    for match in HOLO_MING_NO_JI.finditer(raw):
        prefix = raw[max(0, match.start() - 28) : match.start()]
        suffix = raw[match.end() : match.end() + 28]
        if any(
            tip in prefix
            for tip in (
                '不可断为',
                '不可斷為',
                '不可写',
                '不可寫',
                '不可再写',
                '不可再寫',
                '勿写',
                '勿寫',
                '勿断',
                '勿斷',
                '禁止写',
                '禁止寫',
                '绝对禁止',
                '絕對禁止',
                '禁止',
                '不是',
                '并非',
                '並非',
                '不能说',
                '不能說',
                '纠正',
                '糾正',
                '以为',
                '以為',
                '误为',
                '誤為',
                '即为「',
                '即為「',
                '便是「',
                '所谓',
                '所謂',
            )
        ):
            continue
        # 「…命宫无吉星，其实命宫吉星云集」纠偏后半句
        if any(tip in suffix for tip in ('其实', '其實', '但实际', '但實際', '而是', '并非', '並非')):
            continue
        affirmed_no_ji = True
        break
    if not affirmed_no_ji:
        return False

    ming_names: set[str] = set()
    if isinstance(compact, dict):
        for item in compact.get('palaces') or []:
            if not isinstance(item, dict):
                continue
            if item.get('isMing') or str(item.get('palace') or '') in ('命宫', '命宮'):
                for star in item.get('stars') or []:
                    if isinstance(star, dict) and star.get('name'):
                        ming_names.add(str(star['name']))
                break
    auspicious = {
        '武曲',
        '天府',
        '文曲',
        '文昌',
        '紫微',
        '天相',
        '左辅',
        '右弼',
        '天魁',
        '天钺',
        '禄存',
        '天梁',
        '天同',
    }
    if ming_names & auspicious:
        return True
    return bool(HOLO_MING_WEN_CLAIM.search(raw))


# 十四主星（简繁）→ 规范名
HOLO_STAR_CANON = {
    '紫微': '紫微',
    '天机': '天机',
    '天機': '天机',
    '太阳': '太阳',
    '太陽': '太阳',
    '武曲': '武曲',
    '天同': '天同',
    '廉贞': '廉贞',
    '廉貞': '廉贞',
    '天府': '天府',
    '太阴': '太阴',
    '太陰': '太阴',
    '贪狼': '贪狼',
    '貪狼': '贪狼',
    '巨门': '巨门',
    '巨門': '巨门',
    '天相': '天相',
    '天梁': '天梁',
    '七杀': '七杀',
    '七殺': '七杀',
    '破军': '破军',
    '破軍': '破军',
}
# 宫名别称 → 规范名（含省略「宫」的写法，便于断句与校验）
HOLO_PALACE_CANON = {
    '命宫': '命宫',
    '命宮': '命宫',
    '兄弟宫': '兄弟宫',
    '兄弟宮': '兄弟宫',
    '兄弟': '兄弟宫',
    '夫妻宫': '夫妻宫',
    '夫妻宮': '夫妻宫',
    '夫妻': '夫妻宫',
    '子女宫': '子女宫',
    '子女宮': '子女宫',
    '子女': '子女宫',
    '财帛宫': '财帛宫',
    '財帛宮': '财帛宫',
    '财帛': '财帛宫',
    '財帛': '财帛宫',
    '疾厄宫': '疾厄宫',
    '疾厄宮': '疾厄宫',
    '疾厄': '疾厄宫',
    '迁移宫': '迁移宫',
    '遷移宮': '迁移宫',
    '迁移': '迁移宫',
    '遷移': '迁移宫',
    '交友宫': '交友宫',
    '交友宮': '交友宫',
    '交友': '交友宫',
    '仆役宫': '交友宫',
    '奴仆宫': '交友宫',
    '奴僕宮': '交友宫',
    '官禄宫': '官禄宫',
    '官祿宮': '官禄宫',
    '官禄': '官禄宫',
    '官祿': '官禄宫',
    '事业宫': '官禄宫',
    '事業宮': '官禄宫',
    '事业': '官禄宫',
    '事業': '官禄宫',
    '田宅宫': '田宅宫',
    '田宅宮': '田宅宫',
    '田宅': '田宅宫',
    '福德宫': '福德宫',
    '福德宮': '福德宫',
    '福德': '福德宫',
    '父母宫': '父母宫',
    '父母宮': '父母宫',
    '父母': '父母宫',
}
_HOLO_STAR_ALT = '|'.join(sorted(HOLO_STAR_CANON.keys(), key=len, reverse=True))
_HOLO_PALACE_ALT = '|'.join(sorted(HOLO_PALACE_CANON.keys(), key=len, reverse=True))
# 排除「流年命宫 / 大限命宫」等叠宫说法，避免误绑本命落宫
HOLO_PALACE_CLAIM = re.compile(
    rf'(?<!流年)(?<!大限)(?<!限)({_HOLO_PALACE_ALT})'
)
HOLO_STAR_AT_PALACE = re.compile(
    rf'({_HOLO_STAR_ALT})(?:化[禄权科忌祿權])?(?:坐守|同宫|同宮|坐|守|落|在|入)({_HOLO_PALACE_ALT})'
)


def _build_natal_star_palaces(compact: dict) -> dict[str, set[str]]:
    """主星 → 本命落宫集合（规范宫名）。"""
    out: dict[str, set[str]] = {}
    for item in compact.get('palaces') or []:
        if not isinstance(item, dict):
            continue
        raw_palace = str(item.get('palace') or '')
        palace = HOLO_PALACE_CANON.get(raw_palace, '')
        if not palace:
            for alias, canon in HOLO_PALACE_CANON.items():
                if alias in raw_palace or raw_palace in alias:
                    palace = canon
                    break
        if not palace:
            continue
        for star in item.get('stars') or []:
            if not isinstance(star, dict):
                continue
            sn = str(star.get('name') or '')
            canon = HOLO_STAR_CANON.get(sn)
            if not canon:
                for alias, c in HOLO_STAR_CANON.items():
                    if alias in sn:
                        canon = c
                        break
            if not canon:
                continue
            out.setdefault(canon, set()).add(palace)
    return out


def _extract_star_palace_claims(text: str) -> list[tuple[str, str]]:
    """从正文抽出 (主星, 宫) 显式落宫断言。"""
    raw = text or ''
    claims: list[tuple[str, str]] = []
    seen: set[tuple[str, str]] = set()

    def _add(star: str, palace: str) -> None:
        key = (star, palace)
        if key in seen:
            return
        seen.add(key)
        claims.append(key)

    for match in HOLO_STAR_AT_PALACE.finditer(raw):
        star = HOLO_STAR_CANON.get(match.group(1))
        palace = HOLO_PALACE_CANON.get(match.group(2))
        if not (star and palace):
            continue
        # 「廉贞化忌入疾厄」属飞化/入宫修辞，不是本命落宫
        if re.search(r'化[禄权科忌祿權]入', match.group(0)):
            continue
        ctx = raw[max(0, match.start() - 12) : match.start()]
        if any(t in ctx for t in ('流年', '大限', '流曜', '流禄', '流曲', '流羊', '流陀')):
            continue
        _add(star, palace)

    for match in HOLO_PALACE_CLAIM.finditer(raw):
        palace = HOLO_PALACE_CANON.get(match.group(1))
        if not palace:
            continue
        start = match.start()
        # 跳过流年/大限叠宫前缀（lookbehind 已处理常见情况；再挡「流年命宫在迁移」类）
        prefix = raw[max(0, start - 8) : start]
        if any(prefix.endswith(t) for t in ('流年', '大限', '限', '流曜')):
            continue
        if any(t in prefix for t in ('流年', '大限')):
            continue
        window = raw[start : start + 42]
        # 仅当本句前段就是「空宫借对宫」时跳过，避免长窗口误伤后文
        head = window[:28]
        if re.search(r'(?:空宫|空宮).{0,6}借|(?:借对宫|借對宮)', head):
            continue
        # 截到下一宫名或句读，减少串宫
        cut = len(window)
        for m2 in HOLO_PALACE_CLAIM.finditer(window[len(match.group(1)) :]):
            cut = len(match.group(1)) + m2.start()
            break
        for ch in ('。', '！', '？', '\n', '；', ';'):
            idx = window.find(ch)
            if 0 <= idx < cut:
                cut = idx
        # 「命宫…，但大限贪狼」勿把大限星绑到命宫
        for tip in (
            '，但',
            '，且',
            '大限',
            '流年',
            '白话对照',
            '白話對照',
            '现况倾向',
            '現況傾向',
            '及生年',
            '以及',
            '夹制',
            '夾制',
            '夹命',
            '夾命',
            '三方',
            '四正',
            '会照',
            '會照',
            '会吉',
            '會吉',
            '汇聚',
            '匯聚',
        ):
            idx = window.find(tip)
            if 0 <= idx < cut:
                cut = idx
        chunk = window[:cut]
        # 宫名本身不算星；只取宫名后紧邻片段，且不得跨到下一宫干（财帛/福德…）
        body = chunk[len(match.group(1)) :][:12]
        # 若片段内又冒出其它宫干，截断到该宫干前，避免「命宫武曲…，财帛廉贞」串绑
        for alias in sorted(HOLO_PALACE_CANON.keys(), key=len, reverse=True):
            if alias == match.group(1):
                continue
            idx = body.find(alias)
            if idx > 0:
                body = body[:idx]
                break
        for alias, star in HOLO_STAR_CANON.items():
            if alias not in body:
                continue
            # 否定落宫：命宫见天相不算 / 命宫无文昌 / 并非文昌在命
            pos = body.find(alias)
            neg = body[max(0, pos - 4) : pos + len(alias) + 6]
            if re.search(
                rf'(?:无|没有|并非|不是|未见|不见|非){re.escape(alias)}|'
                rf'见{re.escape(alias)}.{{0,6}}不算|'
                rf'{re.escape(alias)}.{{0,4}}(?:不算|并非|不是)',
                neg,
            ):
                continue
            _add(star, palace)
    return claims




def holographic_pattern_name_mismatch(text: str, compact: dict) -> bool:
    """常见错格名：武曲天府称府相朝垣；文昌不在命称文星朝命。否定句不触发。"""
    raw = text or ''
    ming_names: set[str] = set()
    for item in compact.get('palaces') or []:
        if not isinstance(item, dict):
            continue
        if item.get('isMing') or str(item.get('palace') or '') in ('命宫', '命宮'):
            for star in item.get('stars') or []:
                if isinstance(star, dict) and star.get('name'):
                    ming_names.add(str(star['name']))
            break

    def _affirmative(name: str) -> bool:
        for match in re.finditer(re.escape(name), raw):
            prefix = raw[max(0, match.start() - 24) : match.start()]
            suffix = raw[match.end() : match.end() + 28]
            if any(
                tip in prefix
                for tip in (
                    '并非',
                    '並非',
                    '不是',
                    '勿称',
                    '勿稱',
                    '不可',
                    '不能',
                    '禁止',
                    '不算',
                    '非「',
                    '非『',
                    '纠正',
                    '糾正',
                    '以为',
                    '以為',
                    '误为',
                    '誤為',
                    '便是「',
                    '所谓',
                    '所謂',
                )
            ):
                continue
            # 「…文星朝命，其实…」纠偏后半句
            if any(tip in suffix for tip in ('其实', '其實', '但实际', '但實際', '而非', '并不是', '並不是', '也不算', '才是')):
                continue
            # 「府相朝垣必须天府与天相同宫」定义句不算认格
            if any(tip in suffix[:14] for tip in ('必须', '必須', '须', '須', '才是', '才算', '才叫')):
                continue
            return True
        return False

    if _affirmative('府相朝垣') and ('武曲' in ming_names and '天府' in ming_names) and '天相' not in ming_names:
        return True
    if _affirmative('文星朝命') or _affirmative('文星朝斗'):
        if '文昌' not in ming_names:
            return True
    return False


def holographic_wenqu_location_lie(text: str, compact: dict) -> bool:
    """命宫确有文曲时，禁止正文写「文曲不在命宫」。"""
    ming_has_wenqu = False
    for item in compact.get('palaces') or []:
        if not isinstance(item, dict):
            continue
        if not (item.get('isMing') or str(item.get('palace') or '') in ('命宫', '命宮')):
            continue
        for star in item.get('stars') or []:
            if isinstance(star, dict) and str(star.get('name') or '') in ('文曲',):
                ming_has_wenqu = True
                break
        break
    if not ming_has_wenqu:
        return False
    # 勿用过宽窗口，避免「命宫虽有文曲，但若文昌不在命宫」误伤
    return bool(
        re.search(
            r'文曲(?:星)?不在命|因文曲不在命|文曲其实不在命|文曲並非在命|文曲并非在命',
            text or '',
        )
    )

def holographic_star_palace_mismatch(text: str, compact: dict) -> bool:
    """同一主星写进两宫，或落宫与 palaces JSON 不符。"""
    claims = _extract_star_palace_claims(text)
    if not claims:
        return False

    by_star: dict[str, set[str]] = {}
    for star, palace in claims:
        by_star.setdefault(star, set()).add(palace)
    for palaces in by_star.values():
        if len(palaces) >= 2:
            return True

    natal = _build_natal_star_palaces(compact)
    if not natal:
        return False
    for star, palace in claims:
        actual = natal.get(star)
        if not actual:
            continue
        if palace not in actual:
            return True
    return False


def _normalize_decade_range(raw: object) -> str:
    s = str(raw or '').strip()
    if not s:
        return ''
    s = s.replace('～', '-').replace('—', '-').replace('–', '-').replace('~', '-')
    nums = re.findall(r'\d+', s)
    if len(nums) >= 2:
        return f'{int(nums[0])}-{int(nums[1])}'
    return s


def holographic_decade_jump(text: str, compact: dict) -> bool:
    """时空战略里写的「N-M岁大限」须覆盖近中期虚岁，禁止跳到下一大限。"""
    meta = compact.get('meta') if isinstance(compact.get('meta'), dict) else {}
    guide = compact.get('ageGuide') if isinstance(compact.get('ageGuide'), dict) else {}
    age = guide.get('virtualAge', meta.get('virtualAge'))
    try:
        age = int(age) if age is not None else None
    except (TypeError, ValueError):
        age = None
    if not isinstance(age, int):
        return False

    valid: set[str] = set()
    cur = guide.get('currentDecade') if isinstance(guide.get('currentDecade'), dict) else {}
    cur_range = _normalize_decade_range(cur.get('range'))
    if cur_range:
        valid.add(cur_range)
    near = compact.get('nearTerm') if isinstance(compact.get('nearTerm'), dict) else {}
    max_age = guide.get('nearYearMaxAge')
    try:
        max_age = int(max_age) if max_age is not None else age + 6
    except (TypeError, ValueError):
        max_age = age + 6
    for item in near.get('years') or []:
        if not isinstance(item, dict):
            continue
        ya = item.get('age')
        try:
            ya = int(ya) if ya is not None else None
        except (TypeError, ValueError):
            ya = None
        if isinstance(ya, int) and age <= ya <= max_age:
            nr = _normalize_decade_range(item.get('decadeRange'))
            if nr:
                valid.add(nr)
    if not valid:
        for item in compact.get('decades') or []:
            if not isinstance(item, dict):
                continue
            start, end = item.get('start'), item.get('end')
            try:
                start = int(start) if start is not None else None
                end = int(end) if end is not None else None
            except (TypeError, ValueError):
                continue
            if isinstance(start, int) and isinstance(end, int) and start <= max_age and end >= age:
                valid.add(_normalize_decade_range(item.get('range') or f'{start}-{end}'))
    if not valid:
        return False

    m = HOLO_NEED_TEMPORAL.search(text or '')
    if not m:
        return False
    section = (text or '')[m.start() :]
    nxt = re.search(r'\n##\s+', section[4:])
    if nxt:
        section = section[: nxt.start() + 4]

    for match in HOLO_DECADE_AGE_RANGE.finditer(section):
        claimed = f'{int(match.group(1))}-{int(match.group(2))}'
        if claimed not in valid:
            return True
    return False


def _holo_red_yellow_blocks(temporal_section: str) -> str:
    parts: list[str] = []
    for mark in ('🔴', '🟡'):
        m = re.search(
            rf'{mark}.*?(?=(?:🔴|🟡|🟢|\n##\s+|$))',
            temporal_section,
            flags=re.DOTALL,
        )
        if m:
            parts.append(m.group(0))
    return '\n'.join(parts)


def holographic_adult_grown_up_tone(text: str, compact: dict) -> bool:
    """成人盘不应写「长大后」。"""
    meta = compact.get('meta') if isinstance(compact.get('meta'), dict) else {}
    guide = compact.get('ageGuide') if isinstance(compact.get('ageGuide'), dict) else {}
    stage = str(guide.get('lifeStage') or meta.get('lifeStage') or '')
    if stage != 'adult':
        limits = compact.get('dataLimits') if isinstance(compact.get('dataLimits'), dict) else {}
        if str(limits.get('lifeStage') or '') != 'adult':
            return False
    return bool(HOLO_GROWN_UP.search(text or ''))


def _holo_green_block(temporal_section: str) -> str:
    m = re.search(r'🟢.*?(?=(?:\n##\s+|$))', temporal_section, flags=re.DOTALL)
    return m.group(0) if m else ''


def holographic_decade_year_spam(text: str) -> bool:
    """🟢 段虚岁罗列过多（应一段总述）。"""
    m = HOLO_NEED_TEMPORAL.search(text or '')
    if not m:
        return False
    section = (text or '')[m.start() :]
    nxt = re.search(r'\n##\s+', section[4:])
    if nxt:
        section = section[: nxt.start() + 4]
    green = _holo_green_block(section)
    if not green:
        return False
    return len(HOLO_XU_SUI.findall(green)) >= 5


def holographic_near_horizon_overflow(text: str, compact: dict) -> bool:
    """🔴/🟡 中虚岁或公历年超过 ageGuide.nearYearMax*（跨出当前大限终点）。"""
    guide = compact.get('ageGuide') if isinstance(compact.get('ageGuide'), dict) else {}
    max_age = guide.get('nearYearMaxAge')
    max_year = guide.get('nearYearMaxYear')
    try:
        max_age = int(max_age) if max_age is not None else None
    except (TypeError, ValueError):
        max_age = None
    try:
        max_year = int(max_year) if max_year is not None else None
    except (TypeError, ValueError):
        max_year = None
    if max_age is None and max_year is None:
        return False

    m = HOLO_NEED_TEMPORAL.search(text or '')
    if not m:
        return False
    section = (text or '')[m.start() :]
    nxt = re.search(r'\n##\s+', section[4:])
    if nxt:
        section = section[: nxt.start() + 4]
    block = _holo_red_yellow_blocks(section) or section

    if isinstance(max_age, int):
        for match in HOLO_XU_SUI_SPAN.finditer(block):
            if int(match.group(2)) > max_age:
                return True
        for match in HOLO_XU_SUI.finditer(block):
            if int(match.group(1)) > max_age:
                return True
    if isinstance(max_year, int):
        for match in HOLO_YEAR_TOKEN.finditer(block):
            if int(match.group(1)) > max_year:
                return True
    return False


def collect_allowed_flow_stars(compact: dict) -> set[str]:
    limits = compact.get('dataLimits') if isinstance(compact.get('dataLimits'), dict) else {}
    raw = limits.get('allowedFlowStars') or []
    return {str(x) for x in raw if x}

def sanitize_holographic_content(text: str) -> str:
    raw = extract_holographic_body(text)
    raw = re.sub(r'\n{3,}', '\n\n', raw)
    # 操作指令软清洗 → 盘面倾向表述
    replacements = (
        (r'忌投机', '宜守成'),
        (r'不宜投机', '宜守成'),
        (r'投资需谨慎', '财运宜守成'),
        (r'投资要谨慎', '财运宜守成'),
        (r'严控开支', '开支易偏紧'),
        (r'勿盲目投资', '不宜冒进求财'),
        (r'不要投机', '宜守成'),
        # 病理标签 → 部位/压力倾向
        (r'心血管疾病', '心血管负担偏重'),
        (r'心脏病发作', '心脏负荷偏重'),
        (r'心臟病', '心脏易累'),
        (r'冠心病', '心脏易累'),
        (r'偏头痛', '头部紧绷易累'),
        (r'偏頭痛', '头部紧绷易累'),
        (r'神经衰弱', '用脑过度易疲'),
        (r'抑郁症|憂鬱症', '情绪低落倾向'),
        (r'焦虑症|焦慮症', '精神紧绷倾向'),
        (r'脑溢血|腦溢血', '头部压力偏大'),
        (r'中风偏瘫', '行动迟缓倾向'),
    )
    for pat, rep in replacements:
        raw = re.sub(pat, rep, raw)
    if raw and not re.search(r'[。！？…]"?$', raw):
        raw = raw + '。'
    if HOLO_NEED_ENDING.search(raw) and not re.search(r'仅供参考|僅供參考', raw):
        raw = raw.rstrip() + '\n以上为盘面逻辑推演，仅供参考，不作唯一决策依据。'
    return raw.strip()


def _ming_has_auspicious(compact: dict) -> bool:
    auspicious = {
        '武曲', '天府', '文曲', '文昌', '紫微', '天相', '左辅', '右弼',
        '天魁', '天钺', '禄存', '天梁', '天同',
    }
    for item in compact.get('palaces') or []:
        if not isinstance(item, dict):
            continue
        if not (item.get('isMing') or str(item.get('palace') or '') in ('命宫', '命宮')):
            continue
        for star in item.get('stars') or []:
            if isinstance(star, dict) and str(star.get('name') or '') in auspicious:
                return True
        return False
    return False


def repair_holographic_content(text: str, compact: dict) -> str:
    """终稿修补：命宫已有吉曜时，去掉肯定性的「命宫无吉星」笔误（保留易误判纠偏句）。"""
    raw = text or ''
    if not _ming_has_auspicious(compact):
        return raw
    # 只改「易误判点」之前的正文，避免改掉「有人以为…无吉星，其实…」
    split = re.split(r'(\n##\s*易误判点|\n##\s*易誤判點)', raw, maxsplit=1)
    head = split[0]
    tail = ''.join(split[1:]) if len(split) > 1 else ''

    def _fix_no_ji(match: re.Match[str]) -> str:
        prefix = head[max(0, match.start() - 20) : match.start()]
        if any(t in prefix for t in ('以为', '以為', '并非', '並非', '不是', '禁止', '不可', '勿')):
            return match.group(0)
        return '命宫吉星已具，短板在对宫煞曜或四化忌耗'

    head2 = HOLO_MING_NO_JI.sub(_fix_no_ji, head)
    # 常见错写：大限宫误挂命宫主星
    head2 = re.sub(
        r'福德宫(?:坐拥|坐守|见|見)?武曲[、，,]?天府[、，,]?文曲',
        '福德宫贪狼、文昌、天马',
        head2,
    )
    return (head2 + tail).strip()


def load_env() -> None:
    if not ENV_FILE.is_file():
        return
    for line in ENV_FILE.read_text(encoding='utf-8').splitlines():
        line = line.strip()
        if not line or line.startswith('#') or '=' not in line:
            continue
        key, val = line.split('=', 1)
        key = key.strip()
        val = val.strip()
        if (val.startswith('"') and val.endswith('"')) or (val.startswith("'") and val.endswith("'")):
            val = val[1:-1]
        os.environ.setdefault(key, val)


def resolve_origin(req_origin: str) -> str:
    allowed = os.environ.get('ALLOWED_ORIGIN', '*')
    if allowed == '*':
        return '*'
    items = [s.strip() for s in allowed.split(',') if s.strip()]
    if req_origin and req_origin in items:
        return req_origin
    return items[0] if items else '*'


def trim_text(text: str, limit: int) -> str:
    text = (text or '').strip()
    if len(text) <= limit:
        return text
    return text[:limit] + '…'


def clean_vernacular(text: str) -> str:
    return re.sub(r'\s{2,}', ' ', (text or '').strip()).strip(' ，,。;；')


def normalize_stars(raw: object, limit: int = 14) -> list:
    """接受 string[] 或 {name,brightness,mutagen}[]，统一成紧凑对象列表。"""
    if not isinstance(raw, list):
        return []
    out: list = []
    for item in raw[:limit]:
        if isinstance(item, dict) and item.get('name'):
            row: dict = {'name': str(item['name'])}
            b = str(item.get('brightness') or '').strip()
            m = str(item.get('mutagen') or '').strip()
            if b:
                row['brightness'] = b
            if m:
                row['mutagen'] = m
            out.append(row)
        elif item:
            out.append({'name': str(item)})
    return out


def has_material(body: dict) -> bool:
    def count(key: str) -> int:
        val = body.get(key)
        return len(val) if isinstance(val, list) else 0

    return count('excerpts') + count('patterns') + count('palaceReadings') + count('bookQuotes') > 0


def violates_rules(text: str) -> bool:
    cleaned = DISCLAIMER_SPAN.sub('', text or '')
    return bool(FORBIDDEN.search(cleaned))


def chart_ai_max_tokens() -> int:
    try:
        return max(3200, min(5200, int(os.environ.get('CF_CHART_AI_MAX_TOKENS', '5200'))))
    except ValueError:
        return 5200


ENDING_DISCLAIMER = '以上内容依据本盘材料推估吉凶倾向，仅供参考，不作唯一决策依据。'


def compact_divination_payload(body: dict) -> dict:
    kind = str(body.get('kind') or '').strip()
    question = trim_text(str(body.get('question') or '').strip(), 120)
    cast_in = body.get('cast') if isinstance(body.get('cast'), dict) else {}

    if kind == 'liuren':
        return {
            'kind': 'liuren',
            'question': question or None,
            'cast': {
                'month': cast_in.get('month'),
                'day': cast_in.get('day'),
                'hour': cast_in.get('hour'),
                'palaceName': cast_in.get('palaceName', ''),
                'luck': cast_in.get('luck', ''),
                'summary': trim_text(str(cast_in.get('summary') or ''), 120),
            },
        }

    if kind == 'yaogua':
        def gua(raw: object) -> dict | None:
            if not isinstance(raw, dict):
                return None
            return {
                'index': raw.get('index'),
                'name': raw.get('name', ''),
                'overview': trim_text(str(raw.get('overview') or ''), 220) or None,
            }

        lines_out = []
        for item in (cast_in.get('lines') or [])[:6]:
            if not isinstance(item, dict):
                continue
            lines_out.append(
                {
                    'position': item.get('position'),
                    'label': item.get('label', ''),
                    'changing': bool(item.get('changing')),
                }
            )
        changing = cast_in.get('changingPositions') or []
        if not isinstance(changing, list):
            changing = []
        changing_out = []
        for x in changing[:6]:
            try:
                changing_out.append(int(x))
            except (TypeError, ValueError):
                continue
        return {
            'kind': 'yaogua',
            'question': question or None,
            'cast': {
                'primary': gua(cast_in.get('primary')),
                'relating': gua(cast_in.get('relating')),
                'changingPositions': changing_out,
                'lines': lines_out,
            },
        }

    raise ValueError('kind 须为 liuren 或 yaogua')


def has_divination_material(body: dict) -> bool:
    kind = str(body.get('kind') or '').strip()
    cast = body.get('cast') if isinstance(body.get('cast'), dict) else {}
    if kind == 'liuren':
        return bool(cast.get('palaceName') and cast.get('summary'))
    if kind == 'yaogua':
        primary = cast.get('primary') if isinstance(cast.get('primary'), dict) else {}
        return bool(primary.get('name') or primary.get('index'))
    return False


def violates_divination_rules(text: str) -> bool:
    cleaned = DISCLAIMER_SPAN.sub('', text or '')
    return bool(DIVINATION_FORBIDDEN.search(cleaned))


def violates_divination_style(text: str) -> bool:
    return not DIVINATION_NEED_OVERVIEW.search(text or '')


def call_model(
    payload: dict,
    *,
    system_prompt: str = HOLOGRAPHIC_SYSTEM_PROMPT,
    max_tokens: int = 3600,
    retry: bool = False,
    retry_hint: str = HOLOGRAPHIC_RETRY_HINT,
) -> str:
    account_id = os.environ.get('CF_ACCOUNT_ID', '')
    token = os.environ.get('CF_API_TOKEN', '')
    model = os.environ.get('CF_AI_MODEL', '@cf/zai-org/glm-4.7-flash')
    base = os.environ.get(
        'CF_AI_BASE_URL',
        f'https://api.cloudflare.com/client/v4/accounts/{account_id}/ai/v1' if account_id else '',
    )
    if not account_id or not token or not base:
        raise RuntimeError('Server missing CF_ACCOUNT_ID / CF_API_TOKEN configuration')

    user_json = json.dumps(payload, ensure_ascii=False, separators=(',', ':'))
    messages: list[dict[str, str]] = [
        {'role': 'system', 'content': system_prompt},
        {'role': 'user', 'content': user_json},
    ]
    if retry:
        messages.extend(
            [
                {'role': 'assistant', 'content': '好的。'},
                {'role': 'user', 'content': retry_hint},
            ]
        )

    req_body = json.dumps(
        {
            'model': model,
            'messages': messages,
            'temperature': 0.25 if retry else 0.3,
            'max_tokens': max_tokens,
            'reasoning_effort': 'low',
            'chat_template_kwargs': {'enable_thinking': False},
        },
        ensure_ascii=False,
        separators=(',', ':'),
    ).encode('utf-8')

    req = request.Request(
        f'{base.rstrip("/")}/chat/completions',
        data=req_body,
        headers={
            'Authorization': f'Bearer {token}',
            'Content-Type': 'application/json',
        },
        method='POST',
    )

    try:
        upstream_timeout = int(os.environ.get('CF_AI_TIMEOUT', '180'))
        with request.urlopen(req, timeout=max(60, upstream_timeout)) as resp:
            data = json.loads(resp.read().decode('utf-8'))
    except error.HTTPError as exc:
        detail = exc.read().decode('utf-8', errors='replace')
        try:
            parsed = json.loads(detail)
            msg = parsed.get('errors', [{}])[0].get('message') or parsed.get('error', {}).get('message')
        except json.JSONDecodeError:
            msg = detail or exc.reason
        raise RuntimeError(f'Cloudflare AI error: {msg}') from exc
    except error.URLError as exc:
        reason = str(getattr(exc, 'reason', exc))
        if 'timed out' in reason.lower() or 'timeout' in reason.lower():
            raise RuntimeError('模型回應逾時，請稍後重試。') from exc
        raise RuntimeError(f'Upstream error: {reason}') from exc

    message = ((data.get('choices') or [{}])[0].get('message') or {})
    content = message.get('content')
    if content is None:
        content = ''
    content = str(content).strip()
    if not content:
        raise RuntimeError('Empty model response (content is null; try again)')
    return content


class Handler(BaseHTTPRequestHandler):
    def log_message(self, fmt: str, *args) -> None:
        sys.stderr.write('%s - %s\n' % (self.address_string(), fmt % args))

    def _cors_origin(self) -> str:
        return resolve_origin(self.headers.get('Origin', ''))

    def _send_json(self, status: int, body: dict) -> None:
        payload = json.dumps(body, ensure_ascii=False).encode('utf-8')
        origin = self._cors_origin()
        self.send_response(status)
        self.send_header('Content-Type', 'application/json; charset=utf-8')
        self.send_header('Access-Control-Allow-Origin', origin)
        self.send_header('Access-Control-Allow-Methods', 'POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
        self.wfile.write(payload)

    def _api_path(self) -> str:
        return self.path.split('?', 1)[0]

    def do_OPTIONS(self) -> None:  # noqa: N802
        if self._api_path() not in (
            '/api/chart-ai-holographic',
            '/api/divination-ai',
        ):
            self.send_error(404)
            return
        self._send_json(204, {})

    def do_GET(self) -> None:  # noqa: N802
        if self._api_path() == '/health':
            self._send_json(
                200,
                {
                    'ok': True,
                    'holographic': 'holographic-v1',
                    'divination': 'divination-ai-v1',
                },
            )
            return
        self.send_error(404)

    def _handle_holographic_ai(self, payload: dict) -> None:
        if not has_material(payload):
            self._send_json(400, {'error': '本盤材料不足，無法生成全息診斷。'})
            return
        try:
            compact = compact_holographic_payload(payload)
            allowed_flow = collect_allowed_flow_stars(compact)
            max_tok = chart_ai_max_tokens()
            content = extract_holographic_body(
                        call_model(
                            compact,
                    system_prompt=HOLOGRAPHIC_SYSTEM_PROMPT,
                            max_tokens=max_tok,
                    retry_hint=HOLOGRAPHIC_RETRY_HINT,
                )
            )
            content = repair_holographic_content(sanitize_holographic_content(content), compact)

            def _holo_soft_fail(body: str) -> str | None:
                if violates_holographic_style(body):
                    return 'style'
                if holographic_evidence_thin(body):
                    return 'evidence'
                if holographic_invented_flow(body, allowed_flow):
                    return 'invented_flow'
                if holographic_json_leak(body):
                    return 'json_leak'
                if holographic_clinical_terms(body):
                    return 'clinical'
                if holographic_child_romance_tone(body, compact):
                    return 'child_romance'
                if holographic_ming_contradiction(body, compact):
                    return 'ming_contradiction'
                if holographic_star_palace_mismatch(body, compact):
                    return 'star_palace'
                if holographic_pattern_name_mismatch(body, compact):
                    return 'pattern_name'
                if holographic_wenqu_location_lie(body, compact):
                    return 'wenqu_lie'
                if holographic_decade_jump(body, compact):
                    return 'decade_jump'
                if holographic_near_horizon_overflow(body, compact):
                    return 'decade_horizon'
                if holographic_adult_grown_up_tone(body, compact):
                    return 'adult_grown_up'
                if holographic_decade_year_spam(body):
                    return 'decade_spam'
                return None

            soft = _holo_soft_fail(content)
            if soft:
                sys.stderr.write(f'chart-ai-holo: {soft}, retry once\n')
                reason_map = {
                    'style': '章节结构不全或标题不符。',
                    'evidence': '六维缺少[依据]或白话对照。',
                    'invented_flow': '出现了 JSON 未提供的流曜名。',
                    'json_leak': '依据或正文泄漏了 JSON 字段名（palaces/mutagens/ageGuide 等）。',
                    'clinical': '出现了禁止的病理病名。',
                    'child_romance': '童盘误用成人恋爱口吻。',
                    'ming_contradiction': '命宫已有吉曜却写「命宫无吉星」。',
                    'star_palace': '主星落宫与 palaces 不符；大限宫星须抄 decades，禁止把命宫武曲天府写成福德同宫。',
                    'pattern_name': '错用格局名：武曲天府勿称府相朝垣（三方见天相也不算）；文昌不在命勿称文星朝命。',
                    'wenqu_lie': '命宫有文曲却写文曲不在命宫。',
                    'decade_jump': '大限年龄段错位。',
                    'decade_horizon': '近中期超出 nearYearMaxAge/Year。',
                    'adult_grown_up': '成人盘出现「长大后」。',
                    'decade_spam': '🟢大限逐年罗列过细。',
                }
                for attempt in (1, 2):
                    reason = reason_map.get(soft, soft)
                    content = repair_holographic_content(
                        sanitize_holographic_content(
                            extract_holographic_body(
                                call_model(
                                    compact,
                                    system_prompt=HOLOGRAPHIC_SYSTEM_PROMPT,
                                    max_tokens=max_tok,
                                    retry=True,
                                    retry_hint=HOLOGRAPHIC_RETRY_HINT
                                    + f' 本次失败原因：{reason}（第{attempt}次重试）',
                                )
                            )
                        ),
                        compact,
                    )
                    soft = _holo_soft_fail(content)
                    if not soft:
                        break
                    sys.stderr.write(f'chart-ai-holo: {soft}, retry {attempt + 1}\n')
                else:
                    soft = _holo_soft_fail(content)
            if violates_rules(content):
                sys.stderr.write('chart-ai-holo: forbidden hit, reject\n')
                self._send_json(502, {'error': 'AI 輸出含不宜表述，已拒絕返回，請稍後重試。'})
                return
            soft = _holo_soft_fail(content)
            if soft:
                try:
                    debug_path = Path(__file__).resolve().parent / 'holo-reject-debug.txt'
                    debug_path.write_text(
                        f'soft={soft}\n\n{content}',
                        encoding='utf-8',
                    )
                except OSError:
                    pass
            if soft == 'style':
                sys.stderr.write('chart-ai-holo: style bad, reject\n')
                self._send_json(
                    502,
                    {'error': 'AI 輸出格式不符（需驗盤、命格、四化、六維、時空戰略等章節），請稍後重試。'},
                )
                return
            if soft == 'json_leak':
                sys.stderr.write('chart-ai-holo: json path leak, reject\n')
                self._send_json(502, {'error': 'AI 輸出含內部字段名，已拒絕返回，請稍後重試。'})
                return
            if soft == 'invented_flow':
                sys.stderr.write('chart-ai-holo: invented flow stars, reject\n')
                self._send_json(502, {'error': 'AI 輸出含未提供的流年/流曜材料，已拒絕返回，請稍後重試。'})
                return
            if soft == 'clinical':
                sys.stderr.write('chart-ai-holo: clinical terms, reject\n')
                self._send_json(502, {'error': 'AI 輸出含不宜之病理斷語，已拒絕返回，請稍後重試。'})
                return
            if soft == 'child_romance':
                sys.stderr.write('chart-ai-holo: child romance tone, reject\n')
                self._send_json(502, {'error': 'AI 輸出與年齡階段不符，已拒絕返回，請稍後重試。'})
                return
            if soft == 'ming_contradiction':
                sys.stderr.write('chart-ai-holo: ming luck contradiction, reject\n')
                self._send_json(502, {'error': 'AI 輸出自相矛盾（吉星與無吉），已拒絕返回，請稍後重試。'})
                return
            if soft == 'star_palace':
                sys.stderr.write('chart-ai-holo: star palace mismatch, reject\n')
                self._send_json(502, {'error': 'AI 輸出主星落宮矛盾或與盤面不符，已拒絕返回，請稍後重試。'})
                return
            if soft == 'pattern_name':
                sys.stderr.write('chart-ai-holo: pattern name mismatch, reject\n')
                self._send_json(502, {'error': 'AI 輸出格局名稱與落星不符，已拒絕返回，請稍後重試。'})
                return
            if soft == 'wenqu_lie':
                sys.stderr.write('chart-ai-holo: wenqu location lie, reject\n')
                self._send_json(502, {'error': 'AI 輸出文曲落宮自相矛盾，已拒絕返回，請稍後重試。'})
                return
            if soft == 'decade_jump':
                sys.stderr.write('chart-ai-holo: decade jump, reject\n')
                self._send_json(502, {'error': 'AI 輸出大限年齡段錯位，已拒絕返回，請稍後重試。'})
                return
            if soft == 'decade_horizon':
                sys.stderr.write('chart-ai-holo: near horizon overflow, reject\n')
                self._send_json(502, {'error': 'AI 輸出近中期超出當前大限終點，已拒絕返回，請稍後重試。'})
                return
            if soft == 'adult_grown_up':
                sys.stderr.write('chart-ai-holo: adult grown-up tone, reject\n')
                self._send_json(502, {'error': 'AI 輸出誤用「長大後」（成人盤應寫現況），已拒絕返回，請稍後重試。'})
                return
            if soft == 'decade_spam':
                sys.stderr.write('chart-ai-holo: decade year spam, reject\n')
                self._send_json(502, {'error': 'AI 輸出當前大限羅列過細，已拒絕返回，請稍後重試。'})
                return
            if soft == 'evidence':
                sys.stderr.write('chart-ai-holo: evidence still thin, reject\n')
                self._send_json(502, {'error': 'AI 輸出依據不足，請稍後重試。'})
                return
            self._send_json(200, {'content': content})
        except Exception as exc:  # noqa: BLE001
            msg = str(exc)
            if 'timed out' in msg.lower() or 'timeout' in msg.lower():
                msg = '模型回應逾時，請稍後重試。'
            self._send_json(502, {'error': msg})

    def _handle_divination_ai(self, payload: dict) -> None:
        if not has_divination_material(payload):
            self._send_json(400, {'error': '課式／卦象材料不足，無法生成 AI 解讀。'})
            return
        try:
            compact = compact_divination_payload(payload)
            kind = compact.get('kind')
            prompt = LIUREN_SYSTEM_PROMPT if kind == 'liuren' else YAOGUA_SYSTEM_PROMPT
            content = call_model(compact, system_prompt=prompt, max_tokens=1600)
            if violates_divination_rules(content):
                sys.stderr.write('divination-ai: forbidden hit, reject\n')
                self._send_json(502, {'error': 'AI 輸出含不宜表述，已拒絕返回，請稍後重試。'})
                return
            if violates_divination_style(content):
                sys.stderr.write('divination-ai: style bad, reject\n')
                self._send_json(502, {'error': 'AI 輸出格式不符（需含總覽），請稍後重試。'})
                return
            self._send_json(200, {'content': content})
        except ValueError as exc:
            self._send_json(400, {'error': str(exc)})
        except Exception as exc:  # noqa: BLE001
            msg = str(exc)
            if 'timed out' in msg.lower() or 'timeout' in msg.lower():
                msg = '模型回應逾時，請稍後重試。'
            self._send_json(502, {'error': msg})

    def do_POST(self) -> None:  # noqa: N802
        path = self._api_path()
        if path not in (
            '/api/chart-ai-holographic',
            '/api/divination-ai',
        ):
            self.send_error(404)
            return

        length = int(self.headers.get('Content-Length', '0') or 0)
        raw = self.rfile.read(length).decode('utf-8') if length else '{}'
        try:
            payload = json.loads(raw or '{}')
        except json.JSONDecodeError:
            self._send_json(400, {'error': 'Invalid JSON body'})
            return

        if path == '/api/divination-ai':
            self._handle_divination_ai(payload)
            return
        self._handle_holographic_ai(payload)


def main() -> None:
    load_env()
    host = os.environ.get('LISTEN_HOST', '127.0.0.1')
    port = int(os.environ.get('PORT', '8787'))
    server = ThreadingHTTPServer((host, port), Handler)
    print(f'chart-ai-proxy listening on {host}:{port}', flush=True)
    server.serve_forever()


if __name__ == '__main__':
    main()
