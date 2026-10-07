import type { BuiltChart } from '@/utils/chart';
import type { ChartPalace, ChartStar, ExcerptItem, MatchedPattern, PalaceReading } from '@/types';
import { collectChartBookQuotes, resolveVernacular } from '@/utils/bookVernacular';

const BRANCHES = ['子', '丑', '寅', '卯', '辰', '巳', '午', '未', '申', '酉', '戌', '亥'] as const;

/** 星曜带庙旺、四化，便于模型写细 */
export interface ChartAiStar {
  name: string;
  /** 庙/旺/得/利/平/不/陷 等，空则省略 */
  brightness?: string;
  /** 禄/权/科/忌 等，空则省略 */
  mutagen?: string;
}

export interface ChartAiTimelineEvent {
  year: number;
  event: string;
}

export interface ChartAiDecade {
  /** 如 5-14 */
  range: string;
  start: number;
  end: number;
  /** 该大限落在的宫位主题名（别名优先） */
  themePalace: string;
  stars: ChartAiStar[];
}

export interface ChartAiSanFangCorner {
  palace: string;
  stars: ChartAiStar[];
}

export interface ChartAiNearTermYear {
  year: number;
  /** 约合虚岁，便于对照大限 */
  age: number;
  isCurrent: boolean;
  decadeRange: string;
  /** 该年虚岁所落大限宫 */
  themePalace: string;
  /** 大限宫本命星（摘要） */
  stars: ChartAiStar[];
  /** 流年干支，如 丙午 */
  yearlyGanZhi?: string;
  /** 流年命宫 */
  yearlyMingPalace?: string;
  /** 流年四化：禄权科忌 → 星 + 本命落宫 */
  yearlyMutagen?: Partial<
    Record<'禄' | '权' | '科' | '忌', { star: string; palace: string }>
  >;
  /** 流曜落宫（流魁/流羊等） */
  yearlyFlow?: Array<{ name: string; palace: string }>;
}

export interface ChartAiNearTerm {
  fromYear: number;
  toYear: number;
  currentYear: number;
  years: ChartAiNearTermYear[];
}

export interface ChartAiPayload {
  meta: {
    solarDate?: string;
    gender?: string;
    lunarDate?: string;
    fiveElementsClass?: string;
    soul?: string;
    body?: string;
  };
  /** 命宫三方四正：本宫、对宫、两合宫 */
  sanFangMing: {
    self: ChartAiSanFangCorner;
    opposite: ChartAiSanFangCorner;
    triA: ChartAiSanFangCorner;
    triB: ChartAiSanFangCorner;
  } | null;
  palaces: Array<{
    name: string;
    aliasName: string;
    heavenlyStem?: string;
    earthlyBranch?: string;
    isBodyPalace?: boolean;
    emptyMajor?: boolean;
    stars: ChartAiStar[];
  }>;
  /** 按年龄排序的各大限段 */
  decades: ChartAiDecade[];
  /** 当前年前后各约 5 年 */
  nearTerm: ChartAiNearTerm | null;
  patterns: Array<{
    name: string;
    condition: string;
    /** 仅作素材；模型须改写成白话，不得原文照抄 */
    text: string;
  }>;
  excerpts: Array<{
    chapterTitle: string;
    chapterId?: string;
    text: string;
  }>;
  /** 只传白话译文，不传古文原句 */
  palaceReadings: Array<{
    palace: string;
    vernacular: string;
    source?: string;
  }>;
  /** 卷一已錄入摘句：古文 + 白話，供 AI 與命盤解讀共用 */
  bookQuotes: Array<{
    bookId: string;
    source: string;
    palace?: string;
    classic: string;
    vernacular: string;
  }>;
  /** 全息验盘用：过往大事（可选） */
  timeline?: ChartAiTimelineEvent[];
  /** 全息时空锚点年 */
  anchorYear?: number;
}

function formatStar(s: ChartStar): ChartAiStar {
  const out: ChartAiStar = { name: s.name };
  if (s.brightness?.trim()) out.brightness = s.brightness.trim();
  if (s.mutagen?.trim()) out.mutagen = s.mutagen.trim();
  return out;
}

function palaceStars(p: ChartPalace): ChartAiStar[] {
  return [...p.majorStars, ...p.minorStars, ...p.adjectiveStars].map(formatStar);
}

function findByBranch(palaces: ChartPalace[], branch: string): ChartPalace | undefined {
  return palaces.find((p) => p.earthlyBranch === branch);
}

function nextBranch(branch: string, step: number): string {
  const i = BRANCHES.indexOf(branch as (typeof BRANCHES)[number]);
  if (i < 0) return branch;
  return BRANCHES[(i + step + 12) % 12];
}

function cornerOf(palace: ChartPalace | undefined): ChartAiSanFangCorner {
  if (!palace) return { palace: '', stars: [] };
  return {
    palace: palace.aliasName || palace.name,
    stars: palaceStars(palace),
  };
}

function buildSanFangMing(palaces: ChartPalace[]): ChartAiPayload['sanFangMing'] {
  const ming = palaces.find((p) => p.name === '命宫' || p.name === '命宮');
  if (!ming) return null;
  return {
    self: cornerOf(ming),
    opposite: cornerOf(findByBranch(palaces, nextBranch(ming.earthlyBranch, 6))),
    triA: cornerOf(findByBranch(palaces, nextBranch(ming.earthlyBranch, 4))),
    triB: cornerOf(findByBranch(palaces, nextBranch(ming.earthlyBranch, 8))),
  };
}

function buildDecades(palaces: ChartPalace[]): ChartAiDecade[] {
  return palaces
    .filter((p) => p.decadal?.range)
    .map((p) => {
      const [start, end] = p.decadal!.range;
      return {
        range: `${start}-${end}`,
        start,
        end,
        themePalace: p.aliasName || p.name,
        stars: palaceStars(p),
      };
    })
    .sort((a, b) => a.start - b.start);
}

function parseBirthYear(solarDate: string): number | null {
  const m = /^(\d{4})/.exec((solarDate || '').trim());
  if (!m) return null;
  const y = Number(m[1]);
  return Number.isFinite(y) ? y : null;
}

const MUTAGEN_KEYS = ['禄', '权', '科', '忌'] as const;

function palaceLabel(p: { name: string; aliasName?: string } | undefined): string {
  if (!p) return '';
  return (p as { aliasName?: string }).aliasName || p.name;
}

function findNatalPalaceForStar(
  palaces: ChartPalace[],
  starName: string,
): ChartPalace | undefined {
  return palaces.find((p) =>
    [...p.majorStars, ...p.minorStars, ...p.adjectiveStars].some((s) => s.name === starName),
  );
}

/** 当前公历年前后各 5 年：大限叠宫 + 真实流年四化/流曜 */
function buildNearTerm(
  chart: BuiltChart,
  palaces: ChartPalace[],
  decades: ChartAiDecade[],
): ChartAiNearTerm | null {
  const birthYear = parseBirthYear(chart.solarDate);
  if (!birthYear) return null;
  const currentYear = new Date().getFullYear();
  const fromYear = currentYear - 5;
  const toYear = currentYear + 5;
  const years: ChartAiNearTermYear[] = [];

  for (let year = fromYear; year <= toYear; year += 1) {
    const age = year - birthYear + 1;
    const hit =
      decades.find((d) => age >= d.start && age <= d.end) ||
      decades.find((d) => age >= d.start && age <= d.end + 1);

    const row: ChartAiNearTermYear = {
      year,
      age,
      isCurrent: year === currentYear,
      decadeRange: hit?.range || '',
      themePalace: hit?.themePalace || '',
      stars: hit ? hit.stars.slice(0, 10) : [],
    };

    try {
      const h = chart.astrolabe.horoscope(`${year}-06-15`);
      const yearly = h.yearly as {
        heavenlyStem?: string;
        earthlyBranch?: string;
        index?: number;
        mutagen?: string[];
        stars?: Array<Array<{ name: string; type?: string; scope?: string }>>;
      } | null;
      if (yearly) {
        const stem = String(yearly.heavenlyStem || '');
        const branch = String(yearly.earthlyBranch || '');
        if (stem || branch) row.yearlyGanZhi = `${stem}${branch}`;
        const yIdx = typeof yearly.index === 'number' ? yearly.index : -1;
        if (yIdx >= 0 && yIdx < palaces.length) {
          row.yearlyMingPalace = palaceLabel(palaces[yIdx]);
        }

        const mutagenStars = Array.isArray(yearly.mutagen) ? yearly.mutagen : [];
        if (mutagenStars.length) {
          const mutagen: NonNullable<ChartAiNearTermYear['yearlyMutagen']> = {};
          mutagenStars.slice(0, 4).forEach((starName, i) => {
            const key = MUTAGEN_KEYS[i];
            if (!key || !starName) return;
            const seat = findNatalPalaceForStar(palaces, starName);
            mutagen[key] = { star: starName, palace: palaceLabel(seat) };
          });
          row.yearlyMutagen = mutagen;
        }

        const flow: Array<{ name: string; palace: string }> = [];
        const cells = Array.isArray(yearly.stars) ? yearly.stars : [];
        cells.forEach((cell, idx) => {
          if (!Array.isArray(cell) || idx >= palaces.length) return;
          const palace = palaceLabel(palaces[idx]);
          cell.forEach((s) => {
            const name = String(s?.name || '').trim();
            if (!name.startsWith('流') && name !== '年解') return;
            flow.push({ name, palace });
          });
        });
        if (flow.length) row.yearlyFlow = flow.slice(0, 14);
      }
    } catch {
      // horoscope 失败时仍保留大限叠宫信息
    }

    years.push(row);
  }

  return { fromYear, toYear, currentYear, years };
}

export function buildChartAiPayload(input: {
  chart: BuiltChart;
  palaces: ChartPalace[];
  patterns: MatchedPattern[];
  excerpts: ExcerptItem[];
  readings: PalaceReading[];
}): ChartAiPayload {
  const { chart, patterns, excerpts, readings } = input;
  // AI 解盘以本命盘为准；流年材料走 nearTerm，避免把流曜混进本命宫
  const basePalaces = chart.palaces;
  const decades = buildDecades(basePalaces);

  return {
    meta: {
      solarDate: chart.solarDate,
      gender: chart.gender,
      lunarDate: chart.lunarDate,
      fiveElementsClass: chart.fiveElementsClass,
      soul: chart.soul,
      body: chart.body,
    },
    sanFangMing: buildSanFangMing(basePalaces),
    palaces: basePalaces.map((p) => ({
      name: p.name,
      aliasName: p.aliasName,
      heavenlyStem: p.heavenlyStem,
      earthlyBranch: p.earthlyBranch,
      isBodyPalace: p.isBodyPalace,
      emptyMajor: (p.majorStars?.length ?? 0) === 0,
      stars: palaceStars(p),
    })),
    decades,
    nearTerm: buildNearTerm(chart, basePalaces, decades),
    patterns: patterns.map((p) => ({
      name: p.name,
      condition: p.condition,
      text: p.originalText,
    })),
    excerpts: excerpts.map((e) => ({
      chapterTitle: e.chapterTitle,
      chapterId: e.chapterId,
      text: e.text,
    })),
    palaceReadings: readings.flatMap((r) =>
      r.quotes
        .map((q) => ({
          palace: r.aliasName,
          vernacular: resolveVernacular(q.classic, (q.vernacular || '').trim()),
          source: q.cite.title,
        }))
        .filter((q) => q.vernacular.length > 0),
    ),
    bookQuotes: collectChartBookQuotes(basePalaces),
    anchorYear: new Date().getFullYear(),
  };
}

export function hasChartAiMaterial(payload: ChartAiPayload): boolean {
  return (
    payload.patterns.length > 0 ||
    payload.excerpts.length > 0 ||
    payload.palaceReadings.length > 0 ||
    payload.bookQuotes.length > 0
  );
}
