export interface YijingExcerptBlock {
  type: 'heading' | 'prose' | 'image';
  text?: string;
}

const HEAD_OK =
  /为什么|為何|卦象|序卦|真義|真义|之道|象曰|象辞|象辭|自然界|此卦|外悦|外險|外险|外健|外明|外止|外順|外顺|人間道|人间道|天道|卦形|卦體|卦体|故次|謂之|故稱|故称|以卦体|以卦體/;

const LIST_ITEM =
  /^([一二三四五六七八九十]+[、．.]|[①②③④⑤⑥⑦⑧⑨⑩]|[1-9]\.|含义：|來源：|来源：)/;

const BAD_CONTEXT =
  /阳宅|陽宅|测官运|卜生育|卜婚姻|值年卦|先天卦|后天卦|官带加身|连升三级|女孩子拿到|婚后居此位|案例：|占卜$/;

function normalize(text: string): string {
  return text.replace(/\s+/g, ' ').trim();
}

function shortName(name: string): string {
  return name
    .replace(/为[天地水火山泽雷风]$/, '')
    .replace(/為[天地水火山澤雷風]$/, '');
}

function trimExcerpt(text: string, max = 220): string {
  const t = normalize(text);
  if (t.length <= max) return t;
  const cut = t.slice(0, max);
  const m = cut.match(/^[\s\S]*[。！？；]/);
  return `${m && m[0].length > 60 ? m[0] : cut}……`;
}

/** 合併相鄰短散文（原文常被斷行） */
function mergedProse(blocks: YijingExcerptBlock[]): { text: string; startIdx: number }[] {
  const out: { text: string; startIdx: number }[] = [];
  let buf = '';
  let start = -1;
  const flush = () => {
    if (buf.length >= 40) out.push({ text: buf, startIdx: start });
    buf = '';
    start = -1;
  };
  blocks.forEach((b, idx) => {
    if (b.type !== 'prose' || !b.text) {
      flush();
      return;
    }
    const t = normalize(b.text);
    if (!t || LIST_ITEM.test(t) || BAD_CONTEXT.test(t)) {
      flush();
      return;
    }
    if (!buf) {
      buf = t;
      start = idx;
    } else if (buf.length < 160 && !/[。！？]$/.test(buf) && t.length < 100) {
      buf = `${buf}${t}`;
    } else {
      flush();
      buf = t;
      start = idx;
    }
  });
  flush();
  return out;
}

/**
 * 自站內易經條目 blocks 摘一段「卦體／名義」講解原文，不另行編寫斷語。
 */
export function excerptHexagramOverview(
  blocks: YijingExcerptBlock[] | undefined,
  name: string,
): string | null {
  if (!blocks?.length) return null;
  const sn = shortName(name);

  const scored = mergedProse(blocks)
    .map(({ text, startIdx }) => {
      let s = 0;
      if (sn && text.includes(sn) && startIdx < 22) s += 5;
      if (
        /卦象|序卦|外卦|内卦|內卦|此卦|象曰|象辞|謂之|故稱|故称|所以叫|象征|自然界|卦形|以卦体|以卦體|故次|外.{0,3}(健|顺|順|险|險|明|止|动|動|悦|悅)|内.{0,3}(健|顺|順|险|險|明|止|动|動|悦|悅)|柔静|地性|天行健|天地定位/.test(
          text,
        )
      ) {
        s += 8;
      }
      if (text.length >= 70 && text.length <= 400) s += 3;
      if (startIdx <= 6) s += 3;
      else if (startIdx <= 15) s += 1;
      if (/案例|有人来找你|联合起来你听|赤眉|卜得知/.test(text)) s -= 6;
      return { s, text, startIdx };
    })
    .sort((a, b) => b.s - a.s || a.startIdx - b.startIdx);

  if (scored[0] && scored[0].s >= 6) return trimExcerpt(scored[0].text);

  for (let i = 0; i < blocks.length; i += 1) {
    const b = blocks[i];
    if (b.type !== 'heading' || !b.text || BAD_CONTEXT.test(b.text)) continue;
    if (!HEAD_OK.test(b.text)) continue;
    const parts: string[] = [];
    const ht = normalize(b.text).replace(/[：:]$/, '');
    if (ht.length >= 4 && ht.length <= 36) parts.push(ht);
    for (let j = i + 1; j < blocks.length && parts.join('').length < 210; j += 1) {
      const n = blocks[j];
      if (n.type === 'heading') break;
      if (n.type !== 'prose' || !n.text) continue;
      const pt = normalize(n.text);
      if (LIST_ITEM.test(pt) || BAD_CONTEXT.test(pt)) continue;
      parts.push(pt);
      if (parts.join('').length >= 90) break;
    }
    const joined = normalize(parts.join(''));
    if (joined.length >= 50) return trimExcerpt(joined);
  }

  if (scored[0]) return trimExcerpt(scored[0].text);
  return null;
}
