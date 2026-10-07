/**
 * 把卷二底本里的十二宫 ASCII 盘图还原成结构化数据。
 * 五行局日期按原图上下两行逐字对读（国学典籍网与维基文库卷二同一套图），
 * 不补字、不改宫位、不把 OCR 碎字改写成通顺句。
 */

const BRANCHES = ['巳', '午', '未', '申', '辰', '酉', '卯', '戌', '寅', '丑', '子', '亥'];
const WUXING_TITLES = ['水二局', '木三局', '金四局', '土五局', '火六局'];

export function isSep(line) {
  const t = line.replace(/\\/g, '').trim();
  return /^[-+]{6,}/.test(t) || /^[-+|.]{8,}$/.test(t.replace(/\s/g, ''));
}

export function isPipe(line) {
  return line.includes('|');
}

export function cells(line) {
  const raw = line.replace(/\\/g, '');
  const parts = raw.split('|').map((s) => s.replace(/\s+/g, ' ').trim());
  if (parts.length && parts[0] === '') parts.shift();
  if (parts.length && parts[parts.length - 1] === '') parts.pop();
  return parts;
}

/** 原图上下两行逐字对读：巳宫「初初」+「八九」→「初八、初九」。 */
export function zipPair(top, bot) {
  const a = (top || '').replace(/\s/g, '');
  const b = (bot || '').replace(/\s/g, '');
  if (!a && !b) return '';
  if (!b) return a;
  if (!a) return b;
  const n = Math.max(a.length, b.length);
  const out = [];
  for (let i = 0; i < n; i++) out.push(`${a[i] || ''}${b[i] || ''}`);
  return out.filter(Boolean).join('、');
}

function nonemptyRows(contentLines) {
  return contentLines
    .map(cells)
    .filter((row) => row.some((c) => (c || '').replace(/\s/g, '')));
}

function columnVals(rows, colIdx, fromEnd = false, stripSpace = true) {
  return rows
    .map((row) => {
      const i = fromEnd ? row.length - 1 : colIdx;
      const raw = row[i] || '';
      return stripSpace ? raw.replace(/\s/g, '') : raw.trim();
    })
    .filter(Boolean);
}

function combineColumn(vals, zip) {
  if (!vals.length) return '';
  if (zip && vals.length >= 2) return zipPair(vals[0], vals[1]);
  return vals.join('\n');
}

function detectTitle(buf) {
  const t = buf.join('\n');
  for (const name of WUXING_TITLES) {
    if (t.includes(name)) return name;
  }
  if (t.includes('安天府图') || t.includes('安天府圖')) return '安天府图';
  if (t.includes('禄权科忌图') || t.includes('祿權科忌圖')) return '禄权科忌图';
  if (t.includes('殇使祸福') || t.includes('殤使禍福')) return '殇使祸福紧慢图';
  if (t.includes('庙') && t.includes('落陷') && t.includes('旺')) return '十二宫庙旺落陷图';
  return '';
}

function sepLabel(line) {
  return line
    .replace(/\\/g, '')
    .replace(/[-+]+/g, ' ')
    .replace(/\s+/g, ' ')
    .trim();
}

function collectAbove(lines, idx) {
  const out = [];
  for (let i = idx - 1; i >= 0; i--) {
    const L = lines[i];
    if (isSep(L)) break;
    if (!isPipe(L)) break;
    out.unshift(L);
  }
  return out;
}

function middleTexts(contentLines) {
  const out = [];
  for (const line of contentLines) {
    const p = cells(line);
    if (p.length < 3) continue;
    const mid = p.slice(1, -1).join('').replace(/\s+/g, '').trim();
    if (mid) out.push(mid);
  }
  return out;
}

function assignFour(palaces, contentLines, branches, zip) {
  const rows = nonemptyRows(contentLines);
  if (!rows.length) return;
  for (let c = 0; c < branches.length; c++) {
    const vals = rows
      .map((row) => {
        const raw = row[c] || '';
        return zip ? raw.replace(/\s/g, '') : raw.trim();
      })
      .filter(Boolean);
    const text = combineColumn(vals, zip);
    if (text) palaces[branches[c]] = text;
  }
}

function parsePalaceChart(buf) {
  const title = detectTitle(buf);
  const palaces = {};
  const notes = [];
  const zip = WUXING_TITLES.includes(title);

  for (let i = 0; i < buf.length; i++) {
    const line = buf[i];
    if (!isPipe(line)) {
      const label = sepLabel(line);
      if (label && label !== title && !WUXING_TITLES.includes(label)) notes.push(label);
      continue;
    }
    const cs = cells(line);
    const above = collectAbove(buf, i);

    if (/巳/.test(cs[0] || '') && /午/.test(cs[1] || '') && /未/.test(cs[2] || '') && /申/.test(cs[3] || '')) {
      assignFour(palaces, above, ['巳', '午', '未', '申'], zip);
      continue;
    }
    if (/寅/.test(cs[0] || '') && /丑/.test(cs[1] || '') && /子/.test(cs[2] || '') && /亥/.test(cs[3] || '')) {
      assignFour(palaces, above, ['寅', '丑', '子', '亥'], zip);
      continue;
    }
    if (cs.length >= 2 && /^辰$/.test(cs[0] || '') && /酉/.test(cs[cs.length - 1] || '')) {
      const block = [...above, line];
      for (const m of middleTexts(block)) {
        if (m !== title) notes.push(m);
      }
      const rows = nonemptyRows(above);
      palaces.辰 = combineColumn(columnVals(rows, 0, false, zip), zip);
      palaces.酉 = combineColumn(columnVals(rows, 0, true, zip), zip);
      continue;
    }
    if (cs.length >= 2 && /^卯$/.test(cs[0] || '') && /戌/.test(cs[cs.length - 1] || '')) {
      const block = [...above, line];
      for (const m of middleTexts(block)) {
        if (m !== title) notes.push(m);
      }
      const rows = nonemptyRows(above);
      palaces.卯 = combineColumn(columnVals(rows, 0, false, zip), zip);
      palaces.戌 = combineColumn(columnVals(rows, 0, true, zip), zip);
      continue;
    }
  }

  const note = [...new Set(notes.map((n) => n.replace(/[-+|]/g, '').trim()).filter(Boolean))].join('\n');
  return { type: 'palace-chart', title, note, palaces };
}

function isMiaowangHeader(cs) {
  const joined = cs.join('');
  return /庙/.test(joined) && /落陷/.test(joined) && !BRANCHES.some((b) => cs[0] === b);
}

function parseMiaowangTable(buf) {
  const headers = ['宮', '廟', '旺', '得地', '利益', '平和', '不得地', '落陷'];
  const rows = [];
  let acc = null;
  for (const line of buf) {
    if (!isPipe(line) || isSep(line)) {
      if (acc && acc.branch) {
        rows.push(headers.map((_, i) => acc.cols[i] || ''));
        acc = null;
      }
      continue;
    }
    const cs = cells(line);
    if (isMiaowangHeader(cs)) continue;
    const branch = BRANCHES.find((b) => cs[0] === b);
    if (!acc) acc = { branch: '', cols: Array.from({ length: 8 }, () => '') };
    if (branch) acc.branch = branch;
    const data = branch ? [branch, ...cs.slice(1)] : cs[0] === '' ? ['', ...cs.slice(1)] : cs;
    for (let i = 0; i < 8; i++) {
      const piece = (data[i] || '').replace(/\s/g, '');
      if (!piece) continue;
      if (i === 0 && acc.cols[0]) continue;
      acc.cols[i] += piece;
    }
  }
  if (acc && acc.branch) rows.push(headers.map((_, i) => acc.cols[i] || ''));
  return {
    type: 'table',
    title: '十二宫庙旺落陷图',
    headers,
    rows: rows.filter((r) => r[0]),
  };
}

export function isChartStart(line, next) {
  const t = line.trim();
  if (isSep(t) && next && (isPipe(next) || isSep(next))) return true;
  if (isPipe(t) && /庙/.test(t) && /落陷/.test(t)) return true;
  return false;
}

export function isJunkLine(line) {
  const t = line.replace(/\\/g, '').trim();
  if (!t) return true;
  if (isSep(t)) return true;
  if (isPipe(t) && !t.replace(/[|+\-\s]/g, '')) return true;
  return false;
}

/**
 * 标题落在盘图内部时，回溯到本张图的顶部分隔线（不吃上一张图的亥宫行）。
 */
function sepGroupStart(lines, idx) {
  let start = idx;
  while (start > 0 && isSep(lines[start - 1])) start--;
  return start;
}

export function findAsciiChartStart(src, titleIdx) {
  const head = src.slice(0, titleIdx);
  const lines = head.split('\n');
  const titlePreview = src.slice(titleIdx, titleIdx + 120);
  const isTableHead = /庙/.test(titlePreview) && /落陷/.test(titlePreview);

  let startLine = -1;
  if (isTableHead) {
    for (let j = lines.length - 1; j >= 0; j--) {
      if (isSep(lines[j])) {
        startLine = sepGroupStart(lines, j);
        break;
      }
    }
  } else {
    let i = lines.length - 1;
    let seenTop = false;
    while (i >= 0) {
      const L = lines[i];
      if (isPipe(L)) {
        const cs = cells(L);
        if (
          cs.length >= 4 &&
          /巳/.test(cs[0] || '') &&
          /午/.test(cs[1] || '') &&
          /未/.test(cs[2] || '') &&
          /申/.test(cs[3] || '')
        ) {
          seenTop = true;
        }
      }
      if (seenTop && isSep(L)) {
        startLine = sepGroupStart(lines, i);
        break;
      }
      i--;
    }
  }
  if (startLine < 0) return titleIdx;
  let offset = 0;
  for (let k = 0; k < startLine; k++) offset += lines[k].length + 1;
  return offset;
}

export function toBlocksWithCharts(text, toHant, extras) {
  const lines = text.split('\n').map((l) => l.trimEnd()).filter((l) => l.trim());
  const blocks = [];
  let chartBuf = [];
  let inChart = false;

  const flushChart = () => {
    if (!chartBuf.length) return;
    const blob = chartBuf.join('');
    const title = detectTitle(chartBuf);
    if (title === '十二宫庙旺落陷图' || (blob.includes('落陷') && blob.includes('得地'))) {
      const table = parseMiaowangTable(chartBuf);
      table.title = toHant(table.title);
      table.headers = table.headers.map(toHant);
      table.rows = table.rows.map((r) => r.map(toHant));
      if (table.rows.length) blocks.push(table);
    } else {
      const chart = parsePalaceChart(chartBuf);
      chart.title = toHant(chart.title || title);
      chart.note = toHant(chart.note);
      const nextPalaces = {};
      for (const [k, v] of Object.entries(chart.palaces)) nextPalaces[k] = toHant(v);
      chart.palaces = nextPalaces;
      if (Object.keys(chart.palaces).length) blocks.push(chart);
    }
    chartBuf = [];
  };

  for (let i = 0; i < lines.length; i++) {
    const line = lines[i];
    const next = lines[i + 1];
    if (!inChart && isChartStart(line, next)) {
      inChart = true;
      chartBuf = [line];
      continue;
    }
    if (inChart) {
      chartBuf.push(line);
      const endSep = isSep(line);
      const hasHai = chartBuf.some((L) => /亥/.test(L) && isPipe(L));
      if (endSep && hasHai && !(next && isPipe(next))) {
        inChart = false;
        flushChart();
      }
      continue;
    }
    if (isJunkLine(line)) continue;
    extras(line, blocks);
  }
  if (inChart) flushChart();
  return blocks;
}

export { WUXING_TITLES, BRANCHES };
