import type { ChartPalace, ReadingQuote } from '@/types';
import bookToc from '@/data/bookToc.json';
import bookVernacularByChapter from '@/data/bookVernacularByChapter.json';
import {
  FAWEI_PALACE_QUOTES,
  FAWEI_LINES,
  MING_VERSES,
  PALACE_STAR_QUOTES,
  SHIXIAN_VERSES,
  SIHUA_QUOTES,
  STAR_OPENINGS,
  type QuoteRecord,
} from '@/data/readingQuotes';
import { buildPalaceReadings, orderPalaces, palaceKeyOf } from '@/utils/palaceReading';
import type { PalaceKey } from '@/utils/palaceReading';

export interface BookVernacularEntry {
  bookId: string;
  source: string;
  classic: string;
  vernacular: string;
  palace?: string;
}

export interface AnnotatedSentence {
  text: string;
  vernacular?: string;
  source?: string;
}

type ChapterVernacularMap = Record<string, Array<{ classic: string; vernacular: string }>>;

const CHAPTER_MAP = bookVernacularByChapter as ChapterVernacularMap;

const CHAPTER_TITLES = Object.fromEntries(
  (bookToc as Array<{ id: string; title: string }>).map((item) => [item.id, item.title]),
);

function chapterSourceTitle(chapterId: string): string {
  return CHAPTER_TITLES[chapterId] || chapterId;
}

const ALL_QUOTES: QuoteRecord[] = [
  ...SIHUA_QUOTES,
  ...STAR_OPENINGS,
  ...PALACE_STAR_QUOTES,
  ...FAWEI_PALACE_QUOTES,
  ...FAWEI_LINES,
  ...MING_VERSES,
  ...SHIXIAN_VERSES,
];

function normalizeMatch(text: string): string {
  return (text || '')
    .replace(/\s+/g, '')
    .replace(/[，,。．.！!？?；;：:「」『』""''（）()【】\[\]、·…—\-]/g, '')
    .replace(/兇/g, '凶')
    .replace(/殺/g, '杀')
    .trim();
}

function toEntry(record: QuoteRecord, palace?: string): BookVernacularEntry {
  return {
    bookId: record.bookId || '',
    source: record.sourceTitle,
    classic: record.classic,
    vernacular: record.vernacular,
    palace,
  };
}

type IndexedQuote = BookVernacularEntry & { norm: string };

const CHAPTER_VERNACULAR_IDS = new Set(
  Object.keys(CHAPTER_MAP).filter((id) => (CHAPTER_MAP[id]?.length ?? 0) > 0),
);

const indexedQuotesCache = new Map<string, IndexedQuote[]>();
let allEntriesCache: BookVernacularEntry[] | null = null;
let allChapterIndexedCache: IndexedQuote[] | null = null;

function allChapterIndexedQuotes(): IndexedQuote[] {
  if (allChapterIndexedCache) return allChapterIndexedCache;
  const indexed: IndexedQuote[] = [];
  for (const chapterId of Object.keys(CHAPTER_MAP)) {
    for (const row of CHAPTER_MAP[chapterId] || []) {
      const norm = normalizeMatch(row.classic);
      if (norm.length < 2) continue;
      indexed.push({
        bookId: chapterId,
        source: chapterSourceTitle(chapterId),
        classic: row.classic,
        vernacular: row.vernacular,
        norm,
      });
    }
  }
  indexed.sort((a, b) => b.norm.length - a.norm.length);
  allChapterIndexedCache = indexed;
  return indexed;
}

/** 依古文在卷一全量白話索引中查找（模糊匹配） */
export function lookupChapterEntry(classic: string): BookVernacularEntry | undefined {
  const hit = lookupInQuotes(classic, allChapterIndexedQuotes());
  if (!hit) return undefined;
  return {
    bookId: hit.bookId,
    source: hit.source,
    classic: hit.classic,
    vernacular: hit.vernacular,
  };
}

/** 优先卷一章节今译，找不到再用 fallback */
export function resolveVernacular(classic: string, fallback = ''): string {
  return lookupChapterEntry(classic)?.vernacular?.trim() || fallback.trim();
}

/** 命盘解读 / AI：把摘句白话升级为卷一最新今译 */
export function upgradeQuoteVernacular(quote: ReadingQuote): ReadingQuote {
  const hit = lookupChapterEntry(quote.classic);
  if (!hit) return quote;
  return {
    ...quote,
    classic: hit.classic,
    vernacular: hit.vernacular,
    cite: {
      ...quote.cite,
      bookId: hit.bookId || quote.cite.bookId,
      title: hit.source || quote.cite.title,
    },
  };
}

function mergeWithChapter(entry: BookVernacularEntry): BookVernacularEntry {
  const hit = lookupChapterEntry(entry.classic);
  if (!hit) return entry;
  return {
    ...entry,
    bookId: hit.bookId || entry.bookId,
    source: hit.source || entry.source,
    classic: hit.classic,
    vernacular: hit.vernacular,
  };
}

function chapterEntries(chapterId: string): BookVernacularEntry[] {
  const rows = CHAPTER_MAP[chapterId];
  if (!rows?.length) return [];
  return rows.map((row) => ({
    bookId: chapterId,
    source: chapterId,
    classic: row.classic,
    vernacular: row.vernacular,
  }));
}

function indexedQuotesForChapter(chapterId: string): IndexedQuote[] {
  if (!chapterId) return [];
  const cached = indexedQuotesCache.get(chapterId);
  if (cached) return cached;

  const fromChapter = chapterEntries(chapterId);
  const base = fromChapter.length
    ? fromChapter
    : allBookVernacularEntries().filter((q) => q.bookId && q.bookId === chapterId);

  const indexed = base
    .map((entry) => ({ ...entry, norm: normalizeMatch(entry.classic) }))
    .filter((entry) => entry.norm.length >= 2)
    .sort((a, b) => b.norm.length - a.norm.length);

  indexedQuotesCache.set(chapterId, indexed);
  return indexed;
}

/** 全站已錄入的卷一白話索引（章節全量優先，再併摘句） */
export function allBookVernacularEntries(): BookVernacularEntry[] {
  if (allEntriesCache) return allEntriesCache;

  const seen = new Set<string>();
  const out: BookVernacularEntry[] = [];

  const push = (entry: BookVernacularEntry) => {
    const key = `${entry.bookId}|${normalizeMatch(entry.classic)}`;
    if (!entry.classic || seen.has(key)) return;
    seen.add(key);
    out.push(entry);
  };

  for (const chapterId of Object.keys(CHAPTER_MAP)) {
    for (const entry of chapterEntries(chapterId)) push(entry);
  }

  const sorted = [...ALL_QUOTES].sort((a, b) => b.classic.length - a.classic.length);
  for (const record of sorted) {
    push(toEntry(record));
  }
  allEntriesCache = out;
  return out;
}

/** 章節 id 有白話數據才顯示開關 */
export function chapterHasVernacular(chapterId: string): boolean {
  return Boolean(chapterId) && CHAPTER_VERNACULAR_IDS.has(chapterId);
}

function lookupInQuotes(text: string, quotes: IndexedQuote[]): IndexedQuote | undefined {
  const norm = normalizeMatch(text);
  if (!norm) return undefined;
  let best: IndexedQuote | undefined;
  let bestLen = 0;
  for (const q of quotes) {
    const qc = q.norm;
    if (norm === qc || norm.includes(qc) || qc.includes(norm)) {
      if (qc.length > bestLen) {
        best = q;
        bestLen = qc.length;
      }
    }
  }
  return best;
}

/** 把一段古文拆句，並挂上已錄白話（若有） */
export function annotateClassicText(text: string, chapterId: string): AnnotatedSentence[] {
  const raw = (text || '').trim();
  if (!raw) return [];
  const quotes = indexedQuotesForChapter(chapterId);
  if (!quotes.length) return [{ text: raw }];

  const parts = raw
    .split(/(?<=[。！？；])/)
    .map((s) => s.trim())
    .filter(Boolean);

  if (parts.length <= 1) {
    const hit = lookupInQuotes(raw, quotes);
    return [{ text: raw, vernacular: hit?.vernacular, source: hit?.source }];
  }

  return parts.map((sentence) => {
    const hit = lookupInQuotes(sentence, quotes);
    const punct = /[。！？；]$/.test(sentence);
    return {
      text: punct ? sentence : `${sentence}。`,
      vernacular: hit?.vernacular,
      source: hit?.source,
    };
  });
}

/** 命盤 AI / 解讀共用：依星曜宮位收集卷一白話摘句（优先卷一全量今译） */
export function collectChartBookQuotes(palaces: ChartPalace[]): BookVernacularEntry[] {
  const readings = buildPalaceReadings(palaces);
  const seen = new Set<string>();
  const out: BookVernacularEntry[] = [];

  const push = (entry: BookVernacularEntry) => {
    const merged = mergeWithChapter(entry);
    const key = `${merged.bookId}|${normalizeMatch(merged.classic)}`;
    if (!merged.classic || !merged.vernacular?.trim() || seen.has(key)) return;
    seen.add(key);
    out.push(merged);
  };

  for (const reading of readings) {
    for (const q of reading.quotes) {
      push({
        bookId: q.cite.bookId || '',
        source: q.cite.title,
        classic: q.classic,
        vernacular: q.vernacular,
        palace: reading.aliasName,
      });
    }
  }

  // 卷一全量今译中，按本宫星曜再补若干条（覆盖旧摘句库未收录的条目）
  const PALACE_HINTS: Partial<Record<PalaceKey, RegExp>> = {
    ming: /命[宫宮]|身命|在命|守命|居命/,
    xiongdi: /兄弟/,
    qizi: /夫妻|妻妾|夫婦|夫妇/,
    zinv: /子女|子息|男女/,
    caibo: /財帛|财帛/,
    jie: /疾厄/,
    qianyi: /遷移|迁移/,
    jiaoyou: /奴僕|奴仆|僕役|仆役|交友/,
    guanlu: /官祿|官禄|事業|事业/,
    tianzhai: /田宅/,
    fude: /福德/,
    fumu: /父母/,
  };

  const starInText = (starName: string, text: string) => {
    const compact = text.replace(/\s/g, '');
    if (compact.includes(starName)) return true;
    return normalizeMatch(text).includes(normalizeMatch(starName));
  };

  for (const palace of orderPalaces(palaces)) {
    const key = palaceKeyOf(palace.name) || palaceKeyOf(palace.aliasName);
    const hint = key ? PALACE_HINTS[key] : undefined;
    if (!hint) continue;

    const names = [
      ...palace.majorStars,
      ...palace.minorStars,
      ...palace.adjectiveStars,
    ].map((s) => s.name);
    if (!names.length) continue;

    let added = 0;
    for (const row of allChapterIndexedQuotes()) {
      if (added >= 2 || out.length >= 56) break;
      if (!hint.test(row.classic)) continue;
      if (!names.some((name) => starInText(name, row.classic))) continue;
      push({
        bookId: row.bookId,
        source: row.source,
        classic: row.classic,
        vernacular: row.vernacular,
        palace: palace.aliasName || palace.name,
      });
      added += 1;
    }
  }

  const mutagens = new Set<string>();
  for (const p of palaces) {
    for (const s of [...p.majorStars, ...p.minorStars, ...p.adjectiveStars]) {
      if (s.mutagen) mutagens.add(s.mutagen);
    }
  }
  for (const record of SIHUA_QUOTES) {
    if (!record.mutagen?.some((m) => mutagens.has(m))) continue;
    push(toEntry(record));
  }

  return out;
}
