# libs/ 目录说明

排盘引擎，分两层：**自写方法** + **第三方引擎**（均已通读，MIT 许可）。

## 结构

```
libs/
├── gua.py          # 八卦/六十四卦常量 + 体用生克（梅花、六爻共用）
├── meihua.py       # 梅花易数（时间/数字起卦，自写）
├── xiaoliuren.py   # 小六壬（月日时掌诀，自写）
├── liuyao.py       # 六爻纳甲（铜钱摇卦，自写）
├── bazi.py         # 八字（依赖 lunar_python）
├── liuren.py       # 大六壬（包装 engines/taiyi/kinliuren.py）
├── qimen.py        # 奇门遁甲（包装 engines/qimen）
├── taiyi.py        # 太乙神数（包装 engines/taiyi/kintaiyi.py）
├── sxtwl.py        # 历法垫片：用 lunar_python 替代需 C++ 编译的寿星历(sxtwl)
└── engines/        # 第三方开源排盘引擎（原样保留，见下）
    ├── qimen/      # kentang2017/kinqimen（奇门）
    └── taiyi/      # kentang2017/kintaiyi（太乙）+ 其内置 kinliuren（六壬）
```

## 第三方引擎来源

| 目录 | 来源仓库 | 许可 |
|------|---------|------|
| `engines/qimen/` | [kentang2017/kinliuren](https://github.com/kentang2017/kinliuren) `src/kinqimen/` | MIT |
| `engines/taiyi/` | [kentang2017/kintaiyi](https://github.com/kentang2017/kintaiyi) `src/kintaiyi/`（已剔除 7 个未被引用的 GUI/AI 文件） | MIT |

六壬只有一份实现（`engines/taiyi/kinliuren.py`），`liuren.py` 与太乙内部共用，避免重复。

## 为什么需要 sxtwl.py 垫片

第三方引擎依赖 `sxtwl`（寿星天文历，C++ 扩展，本机无预编译轮子）。`sxtwl.py` 用纯 Python 的 `lunar_python` 实现等价的 `fromSolar / JD2DD / toJD / Time` 接口，从而无需编译。

## 依赖

```bash
pip install lunar_python ephem cn2an bidict drawsvg
```

- `lunar_python`：八字 + 干支 + 节气（垫片底层）
- `ephem` / `drawsvg`：太乙天文计算 / SVG 渲染
- `cn2an` / `bidict`：太乙中文数字转换 / 双向字典
