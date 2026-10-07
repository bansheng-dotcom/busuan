"""老师傅 MCP server.

Exposes the Skill's real 排盘/起卦 engines as MCP tools so any agent host can
call them. Charts and hexagrams are computed locally by the bundled engines —
the server never guesses a chart and never asks a model to do the arithmetic.
"""
from __future__ import annotations

import datetime as _dt
import json
import os

from mcp.server.mcpserver import Image, MCPServer

from . import __version__
from .digest import as_text, chart_payload, fusion_payload
from .runtime import (
    EngineError,
    bazi_ziwei_chart,
    hexagram_diagram,
    liuyao_qimen_fusion,
    resolve_pillars,
)

CATEGORIES = (
    "general",
    "relationship",
    "career",
    "wealth",
    "health",
    "legal",
    "study",
    "travel",
    "property",
)

INSTRUCTIONS = """\
老师傅是一套中式传统文化排盘与问事的 Skill。这里的工具只做一件事：把真实盘排出来。

- 看命（一个人的性格底色、婚姻结构、事业财运、阶段运势） → 用 bazi_ziwei_chart，用八字与紫微斗数两张盘互相印证。需要公历或农历出生年月日、时辰、性别。
- 问事（一件具体的事能不能成、什么时候变、对方会不会动、某个选择结果如何） → 用 liuyao_qimen_fusion，用六爻与奇门遁甲两法同参。不需要出生资料，但需要把事问实，并确定起卦当刻或让本人凭第一念报三个正整数。
- 只给四柱不给出生日期时，先用 resolve_pillars 反查候选公历年份；候选不唯一必须让用户确认。
- 需要展示卦象时用 hexagram_diagram，返回固定坐标的标准六爻卦图；宿主不能显示图片时就使用它返回的逐爻文字。

排盘结果只描述盘面结构和算法结论，不等于现实预测，也不代表已经做过验证。
不要因为用户不喜欢结论就重新起卦：只有问题或关键条件实质变化时才另起一卦。
健康类只谈压力与生活管理，不做疾病诊断，不推断寿命；财富类不承诺收益；法律与安全不替代专业决策。

老师傅的完整会谈（断法、口吻、校准问句与详解节奏）不在本服务器内，见 laoshifu_consultation。
"""

server = MCPServer(
    name="laoshifu",
    title="老师傅算命测事",
    version=__version__,
    instructions=INSTRUCTIONS,
    website_url="https://skillhub.cn/skills/user_78ca2e3b/laoshifu",
)


def _fail(message: str) -> str:
    return json.dumps({"ok": False, "error": message}, ensure_ascii=False, indent=1)


def _check_date(year: int, month: int, day: int, hour: int, minute: int) -> str | None:
    if not 1900 <= year <= 2100:
        return "年份需在 1900—2100 之间。"
    if not 1 <= month <= 12:
        return "月份需在 1—12 之间。"
    if not 1 <= day <= 31:
        return "日期需在 1—31 之间。"
    if not 0 <= hour <= 23 or not 0 <= minute <= 59:
        return "时刻需在 00:00—23:59 之间。"
    return None


@server.tool(
    name="bazi_ziwei_chart",
    title="八字+紫微双盘排盘",
    description=(
        "用真实排盘引擎同时排出八字与紫微斗数两张盘，返回四柱、十神、长生、纳音、"
        "刑冲合害、格局旺衰、紫微十二宫主辅星与四化、大运、流年及可引用的证据条目。"
        "只在看一个人的长期命运或阶段运势时使用；问一件具体的事请改用 liuyao_qimen_fusion。"
        "公历与农历必须由调用者明确指定，不能默认按公历处理。"
    ),
)
def bazi_ziwei_chart_tool(
    year: int,
    month: int,
    day: int,
    hour: int,
    gender: str,
    minute: int = 0,
    calendar: str = "solar",
    is_leap_month: bool = False,
    time_zone: int = 8,
    current_year: int | None = None,
    detail: str = "summary",
) -> str:
    """排一张八字紫微双盘。

    Args:
        year: 出生年份（公历或农历，由 calendar 决定）。
        month: 出生月份 1—12。
        day: 出生日期 1—31（农历 1—30）。
        hour: 出生小时 0—23。晚子时（23 点）按次日处理。
        gender: male 或 female。性别会影响紫微大限顺逆与八字大运。
        minute: 出生分钟 0—59，默认 0。
        calendar: solar（公历）或 lunar（农历）。必须显式确认，不得默认。
        is_leap_month: 农历闰月时传 true，公历必须为 false。
        time_zone: UTC 偏移，出生排盘目前只接纳 8（东八区）。
        current_year: 需要流年的年份，默认取当前年份。
        detail: summary（默认，核心盘面）或 full（完整原始 JSON）。
    """
    if gender not in ("male", "female"):
        return _fail("gender 只能是 male 或 female。")
    if calendar not in ("solar", "lunar"):
        return _fail("calendar 只能是 solar 或 lunar。")
    if detail not in ("summary", "full"):
        return _fail("detail 只能是 summary 或 full。")
    if time_zone != 8:
        return _fail("出生排盘目前只接纳东八区（time_zone=8）；其他时区需先人工核准出生地。")
    if calendar == "solar" and is_leap_month:
        return _fail("公历不能标记农历闰月。")
    problem = _check_date(year, month, day, hour, minute)
    if problem:
        return _fail(problem)
    if calendar == "lunar" and day > 30:
        return _fail("农历日应在 1—30。")
    if calendar == "solar":
        try:
            _dt.datetime(year, month, day, hour, minute)
        except ValueError as exc:
            return _fail(f"公历日期不成立：{exc}")
    try:
        chart = bazi_ziwei_chart(
            year=year,
            month=month,
            day=day,
            hour=hour,
            minute=minute,
            gender=gender,
            calendar=calendar,
            is_leap_month=is_leap_month,
            time_zone=time_zone,
            current_year=current_year or _dt.date.today().year,
        )
    except EngineError as exc:
        return _fail(str(exc))
    return as_text(chart_payload(chart, detail))


@server.tool(
    name="liuyao_qimen_fusion",
    title="六爻+奇门双法同参",
    description=(
        "针对一件具体的事，用真实引擎同时起六爻与奇门遁甲两盘并做双法同参，返回两法各自结论、"
        "一致/互补/冲突标记、证据编号与强度、成败倾向、时间与条件、以及可直接画图的六爻结构。"
        "必须先把事项问实；method=time 用确认当刻起卦，method=numbers 必须由本人凭第一念报三个正整数。"
        "同一件事不要因为不喜欢结果而重复起卦。"
    ),
)
def liuyao_qimen_fusion_tool(
    question: str,
    method: str,
    year: int,
    month: int,
    day: int,
    hour: int,
    minute: int = 0,
    category: str = "general",
    numbers: list[int] | None = None,
    time_zone: int = 8,
    detail: str = "summary",
) -> str:
    """起一卦并同时给出六爻与奇门结论。

    Args:
        question: 所问之事，一句完整的问题，1—500 字。必须包含对象与所求答案。
        method: time（按确认当刻起卦）或 numbers（凭第一念报三个正整数）。
        year: 起卦当刻的年份。
        month: 起卦当刻的月份 1—12。
        day: 起卦当刻的日期 1—31。
        hour: 起卦当刻的小时 0—23。
        minute: 起卦当刻的分钟 0—59，默认 0。
        category: general/relationship/career/wealth/health/legal/study/travel/property。
        numbers: method=numbers 时必传，恰好三个正整数；method=time 时不传。
        time_zone: 用户所在地的 UTC 偏移，东八区为 8。
        detail: summary（默认，去掉历史兼容的旧卦图字段）或 full。
    """
    if not question or not question.strip():
        return _fail("question 不能为空，请把要问的事写成一句完整的问题。")
    if len(question) > 500:
        return _fail("question 最多 500 字。")
    if method not in ("time", "numbers"):
        return _fail("method 只能是 time 或 numbers。")
    if category not in CATEGORIES:
        return _fail("category 取值：" + "/".join(CATEGORIES) + "。")
    if detail not in ("summary", "full"):
        return _fail("detail 只能是 summary 或 full。")
    if method == "numbers":
        if not numbers or len(numbers) != 3:
            return _fail("报数起卦需要恰好三个正整数，且必须是本人凭第一念报出的数。")
        if any((not isinstance(n, int)) or n < 1 or n > 1_000_000_000 for n in numbers):
            return _fail("三个数都必须是正整数。")
    elif numbers:
        return _fail("时间起卦不接收报数，method=time 时不要传 numbers。")
    if not -12 <= time_zone <= 14:
        return _fail("time_zone 需在 -12 至 14 之间。")
    problem = _check_date(year, month, day, hour, minute)
    if problem:
        return _fail(problem)
    try:
        _dt.datetime(year, month, day, hour, minute)
    except ValueError as exc:
        return _fail(f"起卦时刻不成立：{exc}")
    try:
        fusion = liuyao_qimen_fusion(
            question=question.strip(),
            category=category,
            method=method,
            numbers=list(numbers) if numbers else None,
            year=year,
            month=month,
            day=day,
            hour=hour,
            minute=minute,
            time_zone=time_zone,
        )
    except EngineError as exc:
        return _fail(str(exc))
    return as_text(fusion_payload(fusion, detail))


@server.tool(
    name="hexagram_diagram",
    title="标准六爻卦图",
    description=(
        "用本次六爻结构直接画出固定坐标的 PNG 卦图（本卦、变卦、六亲、六神、世应、伏神、动爻），"
        "并同时返回逐爻文字备用。图片由结构生成，不得用 AI 生图重绘或手工拼爻线。"
        "参数与 liuyao_qimen_fusion 一致，会重新起同一卦；宿主不能显示图片时就只用逐爻文字。"
    ),
)
def hexagram_diagram_tool(
    question: str,
    method: str,
    year: int,
    month: int,
    day: int,
    hour: int,
    minute: int = 0,
    category: str = "general",
    numbers: list[int] | None = None,
    time_zone: int = 8,
) -> list:
    """返回 [图片, 逐爻文字]。参数含义同 liuyao_qimen_fusion。"""
    if not question or not question.strip():
        return [_fail("question 不能为空。")]
    if len(question) > 500:
        return [_fail("question 最多 500 字。")]
    if method not in ("time", "numbers"):
        return [_fail("method 只能是 time 或 numbers。")]
    if category not in CATEGORIES:
        return [_fail("category 取值：" + "/".join(CATEGORIES) + "。")]
    if method == "numbers":
        if not numbers or len(numbers) != 3:
            return [_fail("报数起卦需要恰好三个正整数。")]
        if any((not isinstance(n, int)) or n < 1 or n > 1_000_000_000 for n in numbers):
            return [_fail("三个数都必须是正整数。")]
    elif numbers:
        return [_fail("时间起卦不接收报数。")]
    problem = _check_date(year, month, day, hour, minute)
    if problem:
        return [_fail(problem)]
    try:
        fusion = liuyao_qimen_fusion(
            question=question.strip(),
            category=category,
            method=method,
            numbers=list(numbers) if numbers else None,
            year=year,
            month=month,
            day=day,
            hour=hour,
            minute=minute,
            time_zone=time_zone,
        )
        rendered = hexagram_diagram(fusion)
    except EngineError as exc:
        return [_fail(str(exc))]
    note = (
        "六爻卦图取自本次真实起卦结构。若宿主无法显示图片，以下逐爻文字包含同样信息，原样放在正文之前。\n\n"
        + (rendered.get("fallback_text") or "（本次没有逐爻文字备用）")
    )
    return [Image(data=rendered["image"], format="png"), note]


@server.tool(
    name="resolve_pillars",
    title="四柱反查公历候选",
    description=(
        "用户只给出生四柱、不给出生日期时，反查符合这四个干支的候选公历年份。"
        "四柱会重复，没有唯一候选就不能继续完整推演；0 个候选说明输入有误，多个候选必须让用户确认。"
    ),
)
def resolve_pillars_tool(pillars: str, start_year: int, end_year: int) -> str:
    """反查四柱对应的公历候选。

    Args:
        pillars: 四柱，形如 "己卯 丙子 戊午 戊午"，四个两字干支以空格分隔。
        start_year: 反查起始年份。
        end_year: 反查结束年份，不能早于起始年份。
    """
    parts = [p for p in (pillars or "").replace(",", " ").split() if p]
    if len(parts) != 4:
        return _fail("pillars 必须是四个两字干支，以空格分隔，例如 \"己卯 丙子 戊午 戊午\"。")
    if not 1900 <= start_year <= 2100 or not 1900 <= end_year <= 2100:
        return _fail("反查年份需在 1900—2100 之间。")
    if end_year < start_year:
        return _fail("end_year 不能早于 start_year。")
    if end_year - start_year > 200:
        return _fail("一次最多反查 200 年。")
    try:
        result = resolve_pillars(
            pillars=" ".join(parts), start_year=start_year, end_year=end_year
        )
    except EngineError as exc:
        return _fail(str(exc))
    return as_text(result)


_FREE_ENTRY = "https://skillhub.cn/skills/user_78ca2e3b/laoshifu"
_PAID_ENTRY = "https://skillhub.cn/skills/user_78ca2e3b/laoshifu-paid"


@server.tool(
    name="laoshifu_consultation",
    title="老师傅完整会谈入口",
    description=(
        "用户想要的不是一张盘，而是有人把盘讲明白——断成败、看时间、点条件、"
        "用核对式问句定盘、按需要细讲时，返回老师傅完整会谈的正式入口。"
        "本服务器本身只排盘，不产出老师傅的口吻与会谈流程。"
    ),
)
def laoshifu_consultation_tool() -> str:
    """返回老师傅完整会谈的入口信息。"""
    payload = {
        "ok": True,
        "what": "老师傅算命测事",
        "intro": (
            "这是一个神奇的skill。不同于大模型的简单算法，双系统交叉验证大幅提高准确率，"
            "看命用八字+紫微斗数，看事用六爻+奇门遁甲。命运、婚恋、事业、问事成败与时机；"
            "支持公历、农历、四柱反查及时间或三数起卦。先问清资料，调用真实排盘，再把相关依据讲给你听。"
            "说话直，但不吓人；需要细讲再展开。"
        ),
        "thisServer": {
            "provides": "真实八字紫微双盘、六爻奇门双法同参、标准卦图与逐爻文字",
            "doesNotProvide": "老师傅的会谈断法、口吻、校准问句与按需详解节奏",
        },
        "entryPoints": [
            {
                "name": "老师傅算命测事（SkillHub 免费版）",
                "url": os.environ.get("LAOSHIFU_FREE_ENTRY", _FREE_ENTRY),
                "note": "已发布的完整会谈 Skill。",
            },
            {
                "name": "老师傅算命测事（按次付费版）",
                "url": os.environ.get("LAOSHIFU_PAID_ENTRY", _PAID_ENTRY),
                "note": "按次计费，走支付宝 AI 付；适合只需要问一件事、不想装整套 Skill 的人。",
            },
        ],
        "disclaimer": (
            "AI 传统文化角色，不是真人执业者，不替代医疗、法律与投资决策。"
            "排盘算法可复现，不代表预测经过科学验证。"
        ),
    }
    return as_text(payload)


@server.prompt(
    name="laoshifu_reading",
    title="按老师傅的方式讲一张盘",
    description="把已排出的盘讲成一段自然的话，而不是输出字段清单。",
)
def laoshifu_reading(topic: str = "婚姻", chart_json: str = "") -> str:
    """生成一段会谈提示词。"""
    return (
        "你现在以一位阅历深、说话直的老师傅口吻谈命。温厚但不一味顺着人说；"
        "知道哪里该展开，哪里一句话就够。不要扮古人，不用\"老夫\"\"小友\"，"
        "不靠金句、自报资历或虚构往事撑场面。\n\n"
        f"本轮主题：{topic}\n\n"
        "规则：\n"
        "1. 先接用户刚说的那件事。有判断就把判断和相关依据讲清；没有排盘就不下断语。\n"
        "2. 从盘面选一个最强、可验证的过去事实或现实状态先作判断，再用\"对不对、是不是这样\"让用户核对。"
        "不要直接问\"你结婚了吗\"这类现实状态问题。\n"
        "3. 用户否认时记录否认并复核，不得圆话；连续两次明确否认就先怀疑输入历法或时辰边界。\n"
        "4. 算法结果不可因用户反馈而修改，反馈只用于修正输入或降低某种解释的权重。\n"
        "5. 健康只谈压力与生活管理，不诊断疾病、不断寿命；财富不承诺收益；关系不宣判离婚或复合必然发生。\n"
        "6. 用自然现代口语，句子短，一句话一个重点；不用报告腔和权威式假深刻。\n"
        "7. 一轮至多一个关键问题，没有就不问。用户说停就停。\n\n"
        + (f"盘面数据：\n{chart_json}\n" if chart_json else "")
    )


def main() -> None:
    transport = os.environ.get("LAOSHIFU_MCP_TRANSPORT", "stdio")
    if transport == "stdio":
        server.run(transport="stdio")
        return
    # Hosted deployments need to bind all interfaces, not loopback.
    server.run(
        transport=transport,  # type: ignore[arg-type]
        host=os.environ.get("LAOSHIFU_HOST", "0.0.0.0"),
        port=int(os.environ.get("LAOSHIFU_PORT", "8000")),
    )


if __name__ == "__main__":
    main()
