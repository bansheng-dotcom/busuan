# -*- coding: utf-8 -*-
"""
国学典籍 txt → PDF 批量转换
- 宋体(SimSun) 正文 + 黑体(SimHei) 标题 + 楷体(KaiTi) 卷首
- A4, 页码, 标题页
"""
import os, re, sys, glob
from fpdf import FPDF
from fpdf.enums import XPos, YPos

FONT_SUN = "C:/Windows/Fonts/simsun.ttc"
FONT_HEI = "C:/Windows/Fonts/simhei.ttf"
FONT_KAI = "C:/Windows/Fonts/simkai.ttf"

BASE = r"D:\daimajieti1\国学"
OUTDIR = os.path.join(BASE, "PDF")
os.makedirs(OUTDIR, exist_ok=True)

# 标题类行(黑体), 用于目录/卷首等
HEADER_RE = re.compile(
    r"^(提要|目录|目錄|序|卷首|卷末|卷[一二三四五六七八九十百零]+"
    r"|[第卷]?[一二三四五六七八九十百零]+[卷篇部]?之?[一二三四五六七八九十]*$|"
    r"欽定四庫全書|御製|提要|臣等謹案)$"
)

class BookPDF(FPDF):
    def __init__(self, title):
        super().__init__("P", "mm", "A4")
        self.title = title
        self.add_font("Sun", "", FONT_SUN)
        self.add_font("Hei", "", FONT_HEI)
        self.add_font("Kai", "", FONT_KAI)
        self.set_auto_page_break(True, margin=18)
        self.set_margins(20, 22, 20)
        self._made_title = False

    def header(self):
        if not self._made_title:
            return
        self.set_font("Sun", "", 9)
        self.set_text_color(120, 120, 120)
        self.cell(0, 8, self.title, align="C", new_x=XPos.LMARGIN, new_y=YPos.NEXT)

    def footer(self):
        self.set_y(-15)
        self.set_font("Sun", "", 9)
        self.set_text_color(120, 120, 120)
        self.cell(0, 10, str(self.page_no()), align="C", new_x=XPos.LMARGIN, new_y=YPos.NEXT)

    def title_page(self):
        self._made_title = False
        self.add_page()
        self.ln(70)
        self.set_font("Hei", "", 28)
        self.set_text_color(0, 0, 0)
        self.multi_cell(0, 16, self.title, align="C", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        self.ln(12)
        self.set_font("Kai", "", 13)
        self.cell(0, 10, "国学典籍 · PDF 整理本", align="C", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        self._made_title = True

    def render(self, paragraphs):
        self.title_page()
        self.add_page()
        self.set_text_color(0, 0, 0)
        for p in paragraphs:
            p = p.rstrip()
            if not p.strip():
                continue
            s = p.strip()
            # 标题行
            if HEADER_RE.match(s) and len(s) <= 20:
                self.ln(4)
                self.set_font("Hei", "", 13)
                self.multi_cell(0, 9, s, align="C", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
                self.ln(2)
                self.set_font("Sun", "", 11.5)
                continue
            # 正文
            self.set_font("Sun", "", 11.5)
            self.multi_cell(0, 7.2, p, align="L", new_x=XPos.LMARGIN, new_y=YPos.NEXT)


def clean_kanripo(raw):
    """清理 Kanripo mandoku 格式, 返回 (title, text)"""
    title = None
    out = []
    for line in raw.split("\n"):
        if line.startswith("#+TITLE:"):
            title = line.split("#+TITLE:", 1)[1].strip()
            continue
        if line.startswith("#"):
            continue
        line = line.replace("\u00b6", "\n")  # ¶ -> 换行
        out.append(line)
    text = "\n".join(out)
    text = re.sub(r"<pb:[^>]*>", "", text)   # 去页码标记
    text = re.sub(r"<[^>]+>", "", text)      # 去其余标签
    text = text.replace("(占卜之屬/)", "(占卜之屬)").replace("/)", ")")
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n[ \t]*\n+", "\n", text)
    text = re.sub(r"\n{2,}", "\n", text)
    return title, text


def convert_kanripo_dir(d):
    files = sorted(glob.glob(os.path.join(d, "*.txt")))
    if not files:
        return None
    raw = ""
    for f in files:
        try:
            raw += open(f, encoding="utf-8").read() + "\n"
        except Exception:
            pass
    title, text = clean_kanripo(raw)
    if title is None:
        # 从目录名取
        bn = os.path.basename(d)
        m = re.match(r"^[A-Za-z0-9]+_(.+)$", bn)
        title = m.group(1) if m else bn
    return title, text.split("\n")


def convert_txt(f, title=None):
    raw = open(f, encoding="utf-8").read()
    if title is None:
        title = os.path.splitext(os.path.basename(f))[0]
    text = raw
    text = re.sub(r"\r\n", "\n", text)
    return title, text.split("\n")


def save_pdf(title, paragraphs, outpath):
    pdf = BookPDF(title)
    pdf.render(paragraphs)
    pdf.output(outpath)
    return os.path.getsize(outpath)


def main():
    total = 0
    # 1. 四库全书术数类 46 部
    kan = os.path.join(BASE, "四库全书-子部术数")
    dirs = sorted(os.listdir(kan))
    for d in dirs:
        dp = os.path.join(kan, d)
        if not os.path.isdir(dp):
            continue
        r = convert_kanripo_dir(dp)
        if not r:
            continue
        title, paras = r
        safe = re.sub(r'[\\/:*?"<>|]', "_", title)
        outpath = os.path.join(OUTDIR, f"[术数] {safe}.pdf")
        try:
            sz = save_pdf(title, paras, outpath)
            print(f"[OK] {title} -> {os.path.basename(outpath)} ({sz//1024}KB)")
            total += 1
        except Exception as e:
            print(f"[失败] {title}: {str(e)[:80]}")
        sys.stdout.flush()

    # 2. 其他术数(梅花易数/小六壬)
    other = os.path.join(BASE, "其他术数")
    for f in sorted(glob.glob(os.path.join(other, "*.txt"))):
        title, paras = convert_txt(f)
        safe = re.sub(r'[\\/:*?"<>|]', "_", title)
        outpath = os.path.join(OUTDIR, f"[其他] {safe}.pdf")
        try:
            sz = save_pdf(title, paras, outpath)
            print(f"[OK] {title} -> {os.path.basename(outpath)} ({sz//1024}KB)")
            total += 1
        except Exception as e:
            print(f"[失败] {title}: {str(e)[:80]}")
        sys.stdout.flush()

    print("======================")
    print(f"完成: {total} 本 PDF -> {OUTDIR}")


if __name__ == "__main__":
    main()
