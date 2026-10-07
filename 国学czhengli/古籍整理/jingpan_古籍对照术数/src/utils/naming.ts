/** 纳音起名：日柱纳音定本气 → 生扶喜用 → 精选字库组名。不作吉凶断语。 */
import nameCharsJson from '@/data/nameChars.json';
import { lookupBirthNayin, type PillarNayin } from '@/utils/nayin';

export type Wuxing = '金' | '木' | '水' | '火' | '土';

export interface NameChar {
  char: string;
  wuxing: Wuxing;
  note: string;
  source: string;
}

export const NAME_CHARS = nameCharsJson as NameChar[];

export const RULE_TEXT =
  '以日柱納音為本氣，主取生本氣之五行，次取同本氣；不取克本氣。納音歌訣見卷二；用字表為研習輔助，非《紫微斗數全書》原文。不作吉凶斷語。';

const SHENG_ME: Record<Wuxing, Wuxing> = {
  木: '水',
  火: '木',
  土: '火',
  金: '土',
  水: '金',
};

const KE_ME: Record<Wuxing, Wuxing> = {
  木: '金',
  火: '水',
  土: '木',
  金: '火',
  水: '土',
};

export function isWuxing(v: string): v is Wuxing {
  return v === '金' || v === '木' || v === '水' || v === '火' || v === '土';
}

/** 生本气之五行（主喜用） */
export function shengOf(ben: Wuxing): Wuxing {
  return SHENG_ME[ben];
}

/** 克本气之五行（忌用） */
export function keOf(ben: Wuxing): Wuxing {
  return KE_ME[ben];
}

export function preferredWuxing(ben: Wuxing): {
  primary: Wuxing;
  secondary: Wuxing;
  avoid: Wuxing;
} {
  return {
    primary: shengOf(ben),
    secondary: ben,
    avoid: keOf(ben),
  };
}

export interface NamingInput {
  iso: string;
  timeIndex: number;
  surname?: string;
}

export interface NamingAnalysis {
  pillars: PillarNayin[];
  dayNayin: { ganZhi: string; name: string; wuxing: Wuxing };
  preferred: { primary: Wuxing; secondary: Wuxing; avoid: Wuxing };
  ruleText: string;
}

export function analyzeBirth(input: NamingInput): NamingAnalysis | null {
  if (!input.iso) return null;
  const lookup = lookupBirthNayin(input.iso, input.timeIndex);
  const day = lookup.pillars.find((p) => p.label === '日柱');
  if (!day || !day.wuxing || !isWuxing(day.wuxing)) return null;
  return {
    pillars: lookup.pillars,
    dayNayin: {
      ganZhi: day.ganZhi,
      name: day.name,
      wuxing: day.wuxing,
    },
    preferred: preferredWuxing(day.wuxing),
    ruleText: RULE_TEXT,
  };
}

export function charsForPreferred(primary: Wuxing, secondary: Wuxing): NameChar[] {
  return NAME_CHARS.filter((c) => c.wuxing === primary || c.wuxing === secondary);
}

/** 可复现的伪随机（换一批用 seed） */
function mulberry32(seed: number): () => number {
  let t = seed >>> 0;
  return () => {
    t += 0x6d2b79f5;
    let r = Math.imul(t ^ (t >>> 15), 1 | t);
    r ^= r + Math.imul(r ^ (r >>> 7), 61 | r);
    return ((r ^ (r >>> 14)) >>> 0) / 4294967296;
  };
}

function shuffleCopy<T>(arr: T[], rand: () => number): T[] {
  const a = arr.slice();
  for (let i = a.length - 1; i > 0; i -= 1) {
    const j = Math.floor(rand() * (i + 1));
    [a[i], a[j]] = [a[j], a[i]];
  }
  return a;
}

export interface NameSuggestion {
  full: string;
  given: string;
  chars: NameChar[];
}

export function buildRecommendations(opts: {
  surname: string;
  primary: Wuxing;
  secondary: Wuxing;
  seed?: number;
  countSingle?: number;
  countDouble?: number;
}): { single: NameSuggestion[]; double: NameSuggestion[] } {
  const countSingle = opts.countSingle ?? 6;
  const countDouble = opts.countDouble ?? 6;
  const rand = mulberry32(opts.seed ?? 1);
  const surname = (opts.surname || '').trim();

  const primaryPool = shuffleCopy(
    NAME_CHARS.filter((c) => c.wuxing === opts.primary),
    rand,
  );
  const secondaryPool = shuffleCopy(
    NAME_CHARS.filter((c) => c.wuxing === opts.secondary),
    rand,
  );
  const mixed = shuffleCopy([...primaryPool, ...secondaryPool], rand);

  const single: NameSuggestion[] = [];
  for (let i = 0; i < countSingle && i < mixed.length; i += 1) {
    const ch = mixed[i];
    single.push({
      full: `${surname}${ch.char}`,
      given: ch.char,
      chars: [ch],
    });
  }

  const double: NameSuggestion[] = [];
  const usedPairs = new Set<string>();
  let guard = 0;
  while (double.length < countDouble && guard < 200) {
    guard += 1;
    const a =
      primaryPool[Math.floor(rand() * primaryPool.length)] ??
      mixed[Math.floor(rand() * mixed.length)];
    const useSecondary = rand() > 0.45;
    const poolB = useSecondary && secondaryPool.length ? secondaryPool : primaryPool;
    const b = poolB[Math.floor(rand() * poolB.length)];
    if (!a || !b || a.char === b.char) continue;
    const key = `${a.char}${b.char}`;
    if (usedPairs.has(key)) continue;
    usedPairs.add(key);
    const given = `${a.char}${b.char}`;
    double.push({
      full: `${surname}${given}`,
      given,
      chars: [a, b],
    });
  }

  return { single, double };
}
