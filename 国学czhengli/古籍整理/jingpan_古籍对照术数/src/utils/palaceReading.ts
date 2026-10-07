import type { ChartPalace, ChartStar, PalaceReading, ReadingQuote } from '@/types';
import {
  FAWEI_PALACE_QUOTES,
  FAWEI_LINES,
  MING_VERSES,
  PALACE_STAR_QUOTES,
  SHIXIAN_VERSES,
  SIHUA_QUOTES,
  STAR_OPENINGS,
  toReadingQuote,
  wikiSection,
  type QuoteRecord,
} from '@/data/readingQuotes';

const BRANCHES = ['寅', '卯', '辰', '巳', '午', '未', '申', '酉', '戌', '亥', '子', '丑'];
const SHA_NAMES = ['擎羊', '陀羅', '陀罗', '火星', '鈴星', '铃星', '地劫', '天空', '七殺', '七杀', '破軍', '破军'];

export const PALACE_KEYS = [
  'ming',
  'xiongdi',
  'qizi',
  'zinv',
  'caibo',
  'jie',
  'qianyi',
  'jiaoyou',
  'guanlu',
  'tianzhai',
  'fude',
  'fumu',
] as const;

export type PalaceKey = (typeof PALACE_KEYS)[number];

const PALACE_NAME_TO_KEY: Record<string, PalaceKey> = {
  命宫: 'ming',
  命宮: 'ming',
  兄弟: 'xiongdi',
  夫妻: 'qizi',
  妻妾: 'qizi',
  子女: 'zinv',
  財帛: 'caibo',
  财帛: 'caibo',
  疾厄: 'jie',
  遷移: 'qianyi',
  迁移: 'qianyi',
  交友: 'jiaoyou',
  奴僕: 'jiaoyou',
  奴仆: 'jiaoyou',
  僕役: 'jiaoyou',
  仆役: 'jiaoyou',
  官祿: 'guanlu',
  官禄: 'guanlu',
  事業: 'guanlu',
  事业: 'guanlu',
  田宅: 'tianzhai',
  福德: 'fude',
  父母: 'fumu',
};

export function palaceKeyOf(name: string): PalaceKey | '' {
  if (PALACE_NAME_TO_KEY[name]) return PALACE_NAME_TO_KEY[name];
  const hit = Object.keys(PALACE_NAME_TO_KEY).find((k) => name.includes(k));
  return hit ? PALACE_NAME_TO_KEY[hit] : '';
}

function nextBranch(branch: string, delta: number): string {
  const i = BRANCHES.indexOf(branch);
  if (i < 0) return branch;
  return BRANCHES[(i + delta + 12) % 12];
}

function allStars(palace: ChartPalace): ChartStar[] {
  return [...palace.majorStars, ...palace.minorStars, ...palace.adjectiveStars];
}

function starNames(palace: ChartPalace): string[] {
  return allStars(palace).map((s) => s.name);
}

function hasSha(palace: ChartPalace): boolean {
  return starNames(palace).some((n) => SHA_NAMES.some((s) => n.includes(s)));
}

function starMatch(recordStars: string[] | undefined, names: string[]): boolean {
  if (!recordStars?.length) return true;
  return recordStars.some((rs) => names.some((n) => n === rs || n.includes(rs) || rs.includes(n)));
}

function findByBranch(palaces: ChartPalace[], branch: string): ChartPalace | undefined {
  return palaces.find((p) => p.earthlyBranch === branch);
}

function palaceLabel(p: ChartPalace | undefined): string {
  if (!p) return '—';
  return `${p.aliasName || p.name}（${p.heavenlyStem}${p.earthlyBranch}）`;
}

function formatStar(star: ChartStar): string {
  const bits = [star.name];
  if (star.brightness) bits.push(star.brightness);
  if (star.mutagen) bits.push(star.mutagen);
  return bits.join('');
}

function mutagensOf(palace: ChartPalace): string[] {
  return allStars(palace)
    .map((s) => s.mutagen)
    .filter(Boolean);
}

function pushUnique(list: ReadingQuote[], quote: ReadingQuote) {
  if (list.some((q) => q.classic === quote.classic)) return;
  list.push(quote);
}

function pickRecords(records: QuoteRecord[], palace: ChartPalace, key: PalaceKey): QuoteRecord[] {
  const names = starNames(palace);
  const sha = hasSha(palace);
  return records.filter((r) => {
    if (r.palaces?.length && !r.palaces.includes(key)) return false;
    if (r.stars?.length && !starMatch(r.stars, names)) return false;
    if (r.needSha && !sha) return false;
    if (r.branches?.length && !r.branches.includes(palace.earthlyBranch)) return false;
    return true;
  });
}

export function orderPalaces(palaces: ChartPalace[]): ChartPalace[] {
  const ming = palaces.find((p) => palaceKeyOf(p.name) === 'ming');
  if (!ming) return palaces;
  const ordered: ChartPalace[] = [];
  let branch = ming.earthlyBranch;
  for (let i = 0; i < 12; i += 1) {
    const hit = findByBranch(palaces, branch);
    if (hit) ordered.push(hit);
    branch = nextBranch(branch, -1);
  }
  return ordered.length ? ordered : palaces;
}

export function buildPalaceReadings(palaces: ChartPalace[]): PalaceReading[] {
  const ordered = orderPalaces(palaces);
  return ordered.map((palace) => {
    const key = palaceKeyOf(palace.name) || palaceKeyOf(palace.aliasName);
    const opposite = findByBranch(palaces, nextBranch(palace.earthlyBranch, 6));
    const triA = findByBranch(palaces, nextBranch(palace.earthlyBranch, 4));
    const triB = findByBranch(palaces, nextBranch(palace.earthlyBranch, 8));
    const quotes: ReadingQuote[] = [];

    if (key) {
      pickRecords(PALACE_STAR_QUOTES, palace, key).forEach((r) => pushUnique(quotes, toReadingQuote(r)));
      pickRecords(FAWEI_PALACE_QUOTES, palace, key).forEach((r) => pushUnique(quotes, toReadingQuote(r)));
      if (key === 'ming') {
        pickRecords(MING_VERSES, palace, key).forEach((r) => pushUnique(quotes, toReadingQuote(r)));
        pickRecords(SHIXIAN_VERSES, palace, key).forEach((r) => pushUnique(quotes, toReadingQuote(r)));
      }
    }

    // 發微論文句：有星曜/宮位條件的才選入
    FAWEI_LINES.filter((r) => {
      if (r.palaces?.length && key && !r.palaces.includes(key)) return false;
      if (r.stars?.length && !starMatch(r.stars, starNames(palace))) return false;
      if (r.needSha && !hasSha(palace)) return false;
      if (!r.stars?.length && !r.palaces?.length && !r.needSha) return false;
      return true;
    }).forEach((r) => {
      if (quotes.length >= 8) return;
      pushUnique(quotes, toReadingQuote(r));
    });

    const majors = palace.majorStars.map((s) => s.name);
    const minors = palace.minorStars.map((s) => s.name);
    STAR_OPENINGS.filter((r) => starMatch(r.stars, majors.length ? majors : minors)).forEach((r) => {
      if (quotes.filter((q) => q.classic === toReadingQuote(r).classic).length) return;
      if (quotes.length >= 6) return;
      pushUnique(quotes, toReadingQuote(r));
    });

    mutagensOf(palace).forEach((m) => {
      SIHUA_QUOTES.filter((r) => r.mutagen?.includes(m)).forEach((r) => pushUnique(quotes, toReadingQuote(r)));
    });

    const sanFangMutagens = [palace, opposite, triA, triB].flatMap((p) => (p ? mutagensOf(p) : []));
    sanFangMutagens.forEach((m) => {
      if (quotes.length >= 8) return;
      SIHUA_QUOTES.filter((r) => r.mutagen?.includes(m)).forEach((r) => pushUnique(quotes, toReadingQuote(r)));
    });

    if (palace.isBodyPalace && hasSha(palace)) {
      pushUnique(quotes, {
        classic: '身遇殺星不但貧而且賤。',
        vernacular: '身宮若遇殺星，古書說不但貧而且賤。',
        cite: {
          title: '斗數發微論',
          url: wikiSection('斗數發微論'),
          bookId: 'dou-shu-fawei-lun',
        },
      });
    }

    const keQuanXian = allStars(palace).some(
      (s) => (s.mutagen === '科' || s.mutagen === '权' || s.mutagen === '權') && (s.brightness.includes('陷') || s.brightness.includes('不')),
    );
    if (keQuanXian) {
      pushUnique(quotes, {
        classic: '科權陷於凶鄉功名蹭蹬。',
        vernacular: '化科、化權若落在凶陷之地，古書說功名蹭蹬。',
        cite: {
          title: '斗數發微論',
          url: wikiSection('斗數發微論'),
          bookId: 'dou-shu-fawei-lun',
        },
      });
    }

    const mutagenLine = allStars(palace)
      .filter((s) => s.mutagen)
      .map((s) => `${s.name}化${s.mutagen}`)
      .join('　');

    return {
      name: palace.name,
      aliasName: palace.aliasName || palace.name,
      heavenlyStem: palace.heavenlyStem,
      earthlyBranch: palace.earthlyBranch,
      isBodyPalace: palace.isBodyPalace,
      starLine: [...palace.majorStars, ...palace.minorStars].map(formatStar).join('　') || '無主輔星',
      mutagenLine,
      sanFang: {
        self: palaceLabel(palace),
        opposite: palaceLabel(opposite),
        triA: palaceLabel(triA),
        triB: palaceLabel(triB),
      },
      quotes: quotes.slice(0, 8),
    };
  });
}
