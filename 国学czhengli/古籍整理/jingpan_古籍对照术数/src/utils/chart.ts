import { astro } from 'iztro';
import type { ChartPalace, ChartStar } from '@/types';

export type AstrolabeInstance = ReturnType<typeof astro.bySolar>;

export interface BuildChartInput {
  solarDate: string;
  timeIndex: number;
  gender: '男' | '女';
  language: 'zh-CN' | 'zh-TW';
}

export interface HoroscopeView {
  decadalRange: string;
  yearly: string;
  yearlyIndex: number;
  mutagen: string[];
}

export interface BuiltChart {
  astrolabe: AstrolabeInstance;
  palaces: ChartPalace[];
  fiveElementsClass: string;
  lunarDate: string;
  chineseDate: string;
  soul: string;
  body: string;
  gender: string;
  solarDate: string;
}

const PALACE_ALIAS: Record<string, string> = {
  仆役: '交友',
  僕役: '交友',
  交友: '交友',
  官禄: '事业',
  官祿: '事业',
  事业: '事业',
  事業: '事业',
};

function mapStar(star: {
  name: string;
  type: string;
  brightness?: string;
  mutagen?: string;
  scope?: string;
}): ChartStar {
  return {
    name: star.name,
    type: star.type,
    brightness: star.brightness ?? '',
    mutagen: star.mutagen ?? '',
    scope: star.scope ?? 'origin',
  };
}

export function buildChart(input: BuildChartInput): BuiltChart {
  const astrolabe = astro.bySolar(
    input.solarDate,
    input.timeIndex,
    input.gender,
    true,
    input.language,
  );

  const palaces: ChartPalace[] = astrolabe.palaces.map((p) => ({
    name: p.name,
    aliasName: PALACE_ALIAS[p.name] ?? p.name,
    heavenlyStem: p.heavenlyStem,
    earthlyBranch: p.earthlyBranch,
    isBodyPalace: Boolean(p.isBodyPalace),
    isOriginalPalace: p.name === '命宫' || p.name === '命宮',
    majorStars: (p.majorStars ?? []).map(mapStar),
    minorStars: (p.minorStars ?? []).map(mapStar),
    adjectiveStars: (p.adjectiveStars ?? []).map(mapStar),
    decadal: p.decadal
      ? {
          range: p.decadal.range as [number, number],
          heavenlyStem: p.decadal.heavenlyStem,
          earthlyBranch: p.decadal.earthlyBranch,
        }
      : undefined,
  }));

  const soulPalace = astrolabe.palaces.find((p) => p.name === '命宫' || p.name === '命宮');
  const bodyPalace = astrolabe.palaces.find((p) => p.isBodyPalace);

  return {
    astrolabe,
    palaces,
    fiveElementsClass: String(astrolabe.fiveElementsClass ?? ''),
    lunarDate: String(astrolabe.lunarDate ?? ''),
    chineseDate: String(astrolabe.chineseDate ?? ''),
    soul: soulPalace ? `${soulPalace.heavenlyStem}${soulPalace.earthlyBranch}` : '',
    body: bodyPalace ? `${bodyPalace.heavenlyStem}${bodyPalace.earthlyBranch}` : '',
    gender: String(astrolabe.gender ?? ''),
    solarDate: String(astrolabe.solarDate ?? ''),
  };
}

export function getHoroscope(astrolabe: AstrolabeInstance, targetDate: string): HoroscopeView {
  const h = astrolabe.horoscope(targetDate);
  const decadal = h.decadal;
  const yearly = h.yearly;
  const decadalPalace = astrolabe.palaces.find(
    (p) => p.earthlyBranch === decadal?.earthlyBranch,
  );
  const range = decadalPalace?.decadal?.range;
  return {
    decadalRange: range
      ? `${decadal?.heavenlyStem ?? ''}${decadal?.earthlyBranch ?? ''} ${range[0]}–${range[1]}歲`
      : `${decadal?.heavenlyStem ?? ''}${decadal?.earthlyBranch ?? ''}`,
    yearly: yearly ? `${yearly.heavenlyStem}${yearly.earthlyBranch}` : '',
    yearlyIndex: yearly?.index ?? -1,
    mutagen: yearly?.mutagen ?? [],
  };
}

/** 将大限、流年流曜叠到盘面（运/流），并标出当前大限宫、流年宫。 */
export function palacesWithHoroscope(
  astrolabe: AstrolabeInstance,
  palaces: ChartPalace[],
  targetDate: string,
): ChartPalace[] {
  const h = astrolabe.horoscope(targetDate);
  const decadalBranch = h.decadal?.earthlyBranch ?? '';
  const yearlyBranch = h.yearly?.earthlyBranch ?? '';
  return palaces.map((palace, index) => {
    const flow = [
      ...((h.decadal?.stars?.[index] ?? []) as { name: string; type: string; scope?: string }[]),
      ...((h.yearly?.stars?.[index] ?? []) as { name: string; type: string; scope?: string }[]),
    ].map(mapStar);
    return {
      ...palace,
      adjectiveStars: [...palace.adjectiveStars, ...flow],
      isDecadalLimit: Boolean(decadalBranch) && palace.earthlyBranch === decadalBranch,
      isYearlyLimit: Boolean(yearlyBranch) && palace.earthlyBranch === yearlyBranch,
    };
  });
}

/** 十二地支盘面坐标：巳午未申 / 辰 中 酉 / 卯 中 戌 / 寅丑子亥 */
export const BRANCH_GRID: Record<string, { col: number; row: number }> = {
  巳: { col: 1, row: 1 },
  午: { col: 2, row: 1 },
  未: { col: 3, row: 1 },
  申: { col: 4, row: 1 },
  辰: { col: 1, row: 2 },
  酉: { col: 4, row: 2 },
  卯: { col: 1, row: 3 },
  戌: { col: 4, row: 3 },
  寅: { col: 1, row: 4 },
  丑: { col: 2, row: 4 },
  子: { col: 3, row: 4 },
  亥: { col: 4, row: 4 },
};

export const BRIGHTNESS_CLASS: Record<string, string> = {
  庙: 'is-miao',
  廟: 'is-miao',
  旺: 'is-wang',
  得: 'is-de',
  利: 'is-li',
  平: 'is-ping',
  不: 'is-bu',
  陷: 'is-xian',
};

export const MUTAGEN_CLASS: Record<string, string> = {
  禄: 'muta-lu',
  祿: 'muta-lu',
  权: 'muta-quan',
  權: 'muta-quan',
  科: 'muta-ke',
  忌: 'muta-ji',
};
