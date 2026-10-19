#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Decode 2009-era GB2312 MIME (.eml) forum posts into readable UTF-8 text.
Handles: base64 + quoted-printable transfer-encodings, gb2312/gbk/utf-8 charsets,
rfc2047 encoded-headers (From/Subject/Date)."""
import os, glob, email, re
from email.header import decode_header, make_header

SRC = r"C:\Users\13364\WorkBuddy\2026-07-10-17-28-23\materials\【个人成长-俩姓婚姻】精品分享：【至尊泡妞不能让女人看到的泡妞秘籍】"
OUT = r"C:\Users\13364\WorkBuddy\2026-07-10-17-28-23\materials\decoded_eml"
os.makedirs(OUT, exist_ok=True)

def dec(s):
    if s is None:
        return ""
    try:
        return str(make_header(decode_header(s)))
    except Exception:
        return s

def to_text(part):
    # get_payload(decode=True) reverses transfer-encoding -> bytes
    raw = part.get_payload(decode=True)
    if raw is None:
        return ""
    cset = part.get_content_charset() or "gb2312"
    for enc in (cset, "gbk", "gb18030", "utf-8", "latin-1"):
        try:
            return raw.decode(enc)
        except Exception:
            continue
    return raw.decode("utf-8", "replace")

files = sorted(glob.glob(os.path.join(SRC, "*.eml")))
print(f"Found {len(files)} .eml files")
ok, fail = 0, 0
for f in files:
    try:
        with open(f, "rb") as fh:
            msg = email.message_from_binary_file(fh)
        subject = dec(msg.get("Subject", ""))
        frm = dec(msg.get("From", ""))
        date = dec(msg.get("Date", ""))
        texts = []
        if msg.is_multipart():
            for p in msg.walk():
                if p.is_multipart():
                    continue
                ct = p.get_content_type()
                if ct in ("text/plain", "text/html"):
                    texts.append((ct, to_text(p)))
        else:
            texts.append((msg.get_content_type(), to_text(msg)))
        body = ""
        for ct, t in texts:
            if ct == "text/plain":
                body = t
                break
        if not body:
            for ct, t in texts:
                body = t
                break
        if body and "<html" in body.lower():
            body = re.sub(r"<style[\s\S]*?</style>", "", body, flags=re.I)
            body = re.sub(r"<[^>]+>", "", body)
            body = re.sub(r"&nbsp;", " ", body)
            body = re.sub(r"\n{3,}", "\n\n", body)
        base = os.path.splitext(os.path.basename(f))[0]
        outp = os.path.join(OUT, base + ".txt")
        with open(outp, "w", encoding="utf-8") as w:
            w.write(f"主题: {subject}\n")
            w.write(f"发件人: {frm}\n")
            w.write(f"日期: {date}\n")
            w.write("=" * 60 + "\n\n")
            w.write(body.strip() + "\n")
        ok += 1
        print(f"[OK] {os.path.basename(f)} -> {len(body)} chars")
    except Exception as e:
        fail += 1
        print(f"[FAIL] {os.path.basename(f)}: {e}")
print(f"\nDone. ok={ok} fail={fail}")
