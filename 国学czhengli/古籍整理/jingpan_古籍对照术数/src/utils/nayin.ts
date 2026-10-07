/** 六十花甲子纳音。歌辞据卷二，检索键按通行六十甲子（甲戌、己亥、桑柘）。 */
import { Solar } from 'lunar-typescript';
import { astro } from 'iztro';

export interface NayinPair {
  first: string;
  second: string;
  name: string;
  wuxing: '金' | '木' | '水' | '火' | '土';
}

export const NAYIN_PAIRS: NayinPair[] = [
  { first: '甲子', second: '乙丑', name: '海中金', wuxing: '金' },
  { first: '丙寅', second: '丁卯', name: '爐中火', wuxing: '火' },
  { first: '戊辰', second: '己巳', name: '大林木', wuxing: '木' },
  { first: '庚午', second: '辛未', name: '路旁土', wuxing: '土' },
  { first: '壬申', second: '癸酉', name: '劍峰金', wuxing: '金' },
  { first: '甲戌', second: '乙亥', name: '山頭火', wuxing: '火' },
  { first: '丙子', second: '丁丑', name: '澗下水', wuxing: '水' },
  { first: '戊寅', second: '己卯', name: '城頭土', wuxing: '土' },
  { first: '庚辰', second: '辛巳', name: '白蠟金', wuxing: '金' },
  { first: '壬午', second: '癸未', name: '楊柳木', wuxing: '木' },
  { first: '甲申', second: '乙酉', name: '泉中水', wuxing: '水' },
  { first: '丙戌', second: '丁亥', name: '屋上土', wuxing: '土' },
  { first: '戊子', second: '己丑', name: '霹靂火', wuxing: '火' },
  { first: '庚寅', second: '辛卯', name: '松柏木', wuxing: '木' },
  { first: '壬辰', second: '癸巳', name: '長流水', wuxing: '水' },
  { first: '甲午', second: '乙未', name: '沙中金', wuxing: '金' },
  { first: '丙申', second: '丁酉', name: '山下火', wuxing: '火' },
  { first: '戊戌', second: '己亥', name: '平地木', wuxing: '木' },
  { first: '庚子', second: '辛丑', name: '壁上土', wuxing: '土' },
  { first: '壬寅', second: '癸卯', name: '金箔金', wuxing: '金' },
  { first: '甲辰', second: '乙巳', name: '覆燈火', wuxing: '火' },
  { first: '丙午', second: '丁未', name: '天河水', wuxing: '水' },
  { first: '戊申', second: '己酉', name: '大驛土', wuxing: '土' },
  { first: '庚戌', second: '辛亥', name: '釵釧金', wuxing: '金' },
  { first: '壬子', second: '癸丑', name: '桑柘木', wuxing: '木' },
  { first: '甲寅', second: '乙卯', name: '大溪水', wuxing: '水' },
  { first: '丙辰', second: '丁巳', name: '沙中土', wuxing: '土' },
  { first: '戊午', second: '己未', name: '天上火', wuxing: '火' },
  { first: '庚申', second: '辛酉', name: '石榴木', wuxing: '木' },
  { first: '壬戌', second: '癸亥', name: '大海水', wuxing: '水' },
];

export interface PillarNayin {
  label: string;
  ganZhi: string;
  name: string;
  wuxing: string;
}

export interface NayinLookup {
  pillars: PillarNayin[];
  soul: PillarNayin | null;
  fiveElementsClass: string;
}

export function nayinOf(ganZhi: string): NayinPair | null {
  const key = ganZhi.replace(/\s/g, '');
  return NAYIN_PAIRS.find((p) => p.first === key || p.second === key) ?? null;
}

export function timeIndexToHour(timeIndex: number): number {
  if (timeIndex <= 0) return 0;
  if (timeIndex >= 12) return 23;
  return timeIndex * 2 - 1;
}

function pillar(label: string, ganZhi: string): PillarNayin {
  const hit = nayinOf(ganZhi);
  return {
    label,
    ganZhi,
    name: hit?.name ?? '',
    wuxing: hit?.wuxing ?? '',
  };
}

export function toIztroDate(iso: string): string {
  const [y, m, d] = iso.split('-').map(Number);
  return `${y}-${m}-${d}`;
}

export function lookupBirthNayin(iso: string, timeIndex: number): NayinLookup {
  const [y, m, d] = iso.split('-').map(Number);
  const hour = timeIndexToHour(timeIndex);
  const lunar = Solar.fromYmdHms(y, m, d, hour, 0, 0).getLunar();
  const pillars = [
    pillar('年柱', lunar.getYearInGanZhi()),
    pillar('月柱', lunar.getMonthInGanZhi()),
    pillar('日柱', lunar.getDayInGanZhi()),
    pillar('時柱', lunar.getTimeInGanZhi()),
  ];
  const astrolabe = astro.bySolar(toIztroDate(iso), timeIndex, '男', true, 'zh-TW');
  const soulPalace = astrolabe.palaces.find((p) => p.name === '命宫' || p.name === '命宮');
  const soulGz = soulPalace ? `${soulPalace.heavenlyStem}${soulPalace.earthlyBranch}` : '';
  return {
    pillars,
    soul: soulGz ? pillar('命宮', soulGz) : null,
    fiveElementsClass: String(astrolabe.fiveElementsClass ?? ''),
  };
}

