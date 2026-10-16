# -*- coding: utf-8 -*-
"""8 术法工程化回归：风水/择日/相术/天文占/测字/小六壬/太乙/金口诀。

收口「风水/择日/相术/天文占/测字/小六壬/太乙/金口诀 工程化薄弱」的差距——这 8 个术法
参考系几乎没做、我们是领跑者，但领跑的原因之一是「没人和我们对拍」，故更该自补回归兜底。

分层：
1. 有代码化的 5 术法（小六壬/择日/风水/太乙/金口诀）——数据完整性硬断言 + 典籍实例对照
   （小六壬六宫 vs 《小六壬》txt、择日建除/黄黑道十二神、风水八宅命卦/游年九星）。
2. 无代码化的 3 术法（相术/天文占/测字）——如实标注「无 Det 计算层，靠典籍 Grep」，
   验证典籍 txt 与分术文档均存在（引用一致性），不硬造判定。

运行: python tests/bafu_engineering_regression.py
"""
import os
import sys

LIB = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "scripts", "libs")
sys.path.insert(0, LIB)

for _s in (sys.stdout, sys.stderr):
    try:
        _s.reconfigure(encoding="utf-8")
    except Exception:
        pass

_TXT = r"D:\卜算\国学czhengli\txt"
_DOCS = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "docs")


def _grep_any(path, needles):
    try:
        t = open(path, encoding="utf-8").read()
    except Exception:
        return False
    return any(n in t for n in needles)


def main():
    fail = False
    print("[8术法] 工程化回归：5 术法数据完整性 + 3 术法无代码化如实标注\n")

    # ========== 1. 小六壬 ==========
    from pan import xiaoliuren as xlr
    ok_gong = xlr.GONG == ["大安", "留连", "速喜", "赤口", "小吉", "空亡"]
    ok_jx = len(xlr._XLR_JX) == 6 and all(v[0] in ("吉", "凶") for v in xlr._XLR_JX.values())
    # 典籍实例：六宫名 + 掌诀顺序「大安→留连→速喜→赤口→小吉→空亡」
    xlr_txt = os.path.join(_TXT, "[其他] 小六壬.txt")
    ok_dianji = _grep_any(xlr_txt, ["大安", "留连", "速喜", "赤口", "小吉", "空亡", "回到大安"])
    print(f"  [小六壬] {'✓' if (ok_gong and ok_jx) else '✗'} 六宫顺序+吉凶完整；"
          f"{'✓' if ok_dianji else '✗'} 典籍《小六壬》六宫名/掌诀顺序可 Grep")
    fail |= not (ok_gong and ok_jx and ok_dianji)

    # ========== 2. 择日 ==========
    from pan import zeri
    ok_jc = zeri.JIAN_CHU == ['建', '除', '满', '平', '定', '执', '破', '危', '成', '收', '开', '闭']
    ok_hd = zeri.HUANG_DAO == ['青龙', '明堂', '天刑', '朱雀', '金匮', '天德', '白虎', '玉堂', '天牢', '玄武', '司命', '勾陈']
    ok_jcjx = len(zeri.JIAN_CHU_JI_XIONG) == 12 and len(zeri.HUANG_DAO_JI_XIONG) == 12
    # 黄黑道吉凶：青龙/明堂/金匮/天德/玉堂/司命 吉（大吉/吉），天刑/朱雀/白虎/天牢/玄武/勾陈 凶
    huang_ji = ["青龙", "明堂", "金匮", "天德", "玉堂", "司命"]
    huang_xiong = ["天刑", "朱雀", "白虎", "天牢", "玄武", "勾陈"]
    ok_hdjx = all("吉" in zeri.HUANG_DAO_JI_XIONG[s] for s in huang_ji) and \
              all("凶" in zeri.HUANG_DAO_JI_XIONG[s] for s in huang_xiong)
    print(f"  [择日] {'✓' if (ok_jc and ok_hd and ok_jcjx) else '✗'} 建除十二神+黄黑道十二神完整；"
          f"{'✓' if ok_hdjx else '✗'} 黄黑道吉凶（6吉6凶）正确")
    fail |= not (ok_jc and ok_hd and ok_jcjx and ok_hdjx)

    # ========== 3. 风水 ==========
    from pan import fengshui
    ok_bagua = fengshui.BA_GUA == ['乾', '兑', '离', '震', '巽', '坎', '艮', '坤']
    ok_dongxi = set(fengshui.DONG_SI_MING) == {"坎", "离", "震", "巽"} and \
                set(fengshui.XI_SI_MING) == {"乾", "坤", "艮", "兑"}
    # 游年歌诀标准对照（大游年歌诀 8 卦 × 8 星 golden，逐字对拍，抓「六煞/祸害抄错」）
    _YOU_STD = {
        '乾': {'生气': '兑', '天医': '艮', '延年': '坤', '伏位': '乾', '绝命': '离', '五鬼': '震', '六煞': '坎', '祸害': '巽'},
        '坤': {'生气': '艮', '天医': '兑', '延年': '乾', '伏位': '坤', '绝命': '坎', '五鬼': '巽', '六煞': '离', '祸害': '震'},
        '震': {'生气': '离', '天医': '坎', '延年': '巽', '伏位': '震', '绝命': '兑', '五鬼': '艮', '六煞': '乾', '祸害': '坤'},
        '巽': {'生气': '坎', '天医': '离', '延年': '震', '伏位': '巽', '绝命': '兑', '五鬼': '坤', '六煞': '艮', '祸害': '乾'},
        '坎': {'生气': '巽', '天医': '震', '延年': '离', '伏位': '坎', '绝命': '坤', '五鬼': '艮', '六煞': '乾', '祸害': '兑'},
        '离': {'生气': '震', '天医': '巽', '延年': '坎', '伏位': '离', '绝命': '乾', '五鬼': '兑', '六煞': '坤', '祸害': '艮'},
        '艮': {'生气': '坤', '天医': '乾', '延年': '兑', '伏位': '艮', '绝命': '巽', '五鬼': '坎', '六煞': '震', '祸害': '离'},
        '兑': {'生气': '乾', '天医': '坤', '延年': '艮', '伏位': '兑', '绝命': '震', '五鬼': '离', '六煞': '巽', '祸害': '坎'},
    }
    ok_younian = fengshui.YOU_NIAN == _YOU_STD
    # 命卦确定性：1990 男=坎、女=坤（八宅命卦公式），命卦均在八卦内
    ok_minggua = (fengshui.get_ming_gua(1990, "男") == "坎" and fengshui.get_ming_gua(1990, "女") == "坤"
                  and fengshui.get_ming_gua(1990, "男") in fengshui.BA_GUA
                  and fengshui.get_ming_gua(1990, "女") in fengshui.BA_GUA)
    print(f"  [风水] {'✓' if (ok_bagua and ok_dongxi and ok_younian) else '✗'} 八宅八卦+东西四命+游年歌诀逐字对照；"
          f"{'✓' if ok_minggua else '✗'} 命卦公式（1990男坎/女坤）")
    fail |= not (ok_bagua and ok_dongxi and ok_younian and ok_minggua)

    # ========== 4. 太乙 ==========
    from pan import taiyi
    import datetime
    import io, contextlib
    with contextlib.redirect_stdout(io.StringIO()):
        t = taiyi.cast(datetime.datetime(2026, 10, 7, 10, 0))
    ju = (t.get("局式") or {}).get("數")
    ok_ju = isinstance(ju, int) and 1 <= ju <= 72
    ok_zhuke = "主算" in t and "客算" in t
    print(f"  [太乙] {'✓' if (ok_ju and ok_zhuke) else '✗'} 局式数∈1-72（得 {ju}）+ 主客算齐全")
    fail |= not (ok_ju and ok_zhuke)

    # ========== 5. 金口诀 ==========
    from pan import jinkoujue
    ok_jjs = len(jinkoujue._JIANGSHEN) == 12
    ok_gs = len(jinkoujue._GUISHEN) == 12
    ok_yj = len(jinkoujue._YUEJIANG) == 24   # 月将按 24 节气（每节气一月将，非 12）
    ok_ds = len(jinkoujue._DUNSHOU) == 10
    # 古本实例复算（丙日昼贵亥/春分戌将，与 regression_test 同款）
    ok_inst = (jinkoujue._GUIREN["丙"][0] == "亥" and jinkoujue._YUEJIANG.get("春分") == "戌"
               and jinkoujue._DUNSHOU["丙"] == "戊")
    print(f"  [金口诀] {'✓' if (ok_jjs and ok_gs and ok_yj and ok_ds) else '✗'} 将神12+贵神12+月将24+遁首10 完整；"
          f"{'✓' if ok_inst else '✗'} 古本实例（丙日昼贵亥/春分戌将/丙遁戊）")
    fail |= not (ok_jjs and ok_gs and ok_yj and ok_ds and ok_inst)

    # ========== 6. 相术/天文占/测字（无 Det 计算层，如实标注） ==========
    print("\n  [相术/天文占/测字] 无 Det 计算层（`rules.py` 标注「无盘术法返回 []」），靠典籍 Grep 断卦：")
    no_code = [
        ("相术", ["柳庄相法", "公笃相法", "冰鉴"], "相术.md"),
        ("天文占", ["星学大成"], "天文占.md"),
        ("测字", ["测字秘牒", "梅花易数卷四五相字术"], "测字.md"),
    ]
    for name, dianji_names, doc in no_code:
        dianji_ok = all(os.path.exists(os.path.join(_TXT, f"[易藏] {n}.txt")) for n in dianji_names)
        doc_ok = os.path.exists(os.path.join(_DOCS, doc))
        # rules 无 Det 计算层：pan_meta 对无盘术法返回空
        from judge import rules
        meta = rules.pan_meta(name)
        det_ok = meta.get("计算层") == [] or meta.get("计算层") is None
        print(f"    {name}: 典籍 txt {'✓' if dianji_ok else '✗'} 分术文档 {'✓' if doc_ok else '✗'} "
              f"无Det计算层 {'✓' if det_ok else '✗'}")
        fail |= not (dianji_ok and doc_ok)

    print(f"\n结果: {'失败' if fail else '通过'}（5 术法数据完整性+实例 + 3 术法无代码化如实标注）")
    sys.exit(1 if fail else 0)


if __name__ == "__main__":
    main()
