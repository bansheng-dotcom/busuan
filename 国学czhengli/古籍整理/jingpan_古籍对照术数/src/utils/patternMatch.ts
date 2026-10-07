import type { BuiltChart } from '@/utils/chart';
import type { MatchedPattern } from '@/types';
import patternDict from '@/data/patternDict.json';

interface PalaceLite {
  name: string;
  earthlyBranch: string;
  isBodyPalace: boolean;
  stars: string[];
  brightness: Record<string, string>;
}

function normalizeName(name: string): string {
  return name.replace(/化/g, '');
}

function allStars(p: {
  majorStars: { name: string; brightness: string }[];
  minorStars: { name: string; brightness: string }[];
  adjectiveStars: { name: string; brightness: string }[];
}): { names: string[]; brightness: Record<string, string> } {
  const list = [...p.majorStars, ...p.minorStars, ...p.adjectiveStars];
  const brightness: Record<string, string> = {};
  const names = list.map((s) => {
    brightness[s.name] = s.brightness;
    return s.name;
  });
  return { names, brightness };
}

function has(p: PalaceLite | undefined, ...names: string[]): boolean {
  if (!p) return false;
  return names.every((n) => p.stars.some((s) => s === n || s.includes(n)));
}

function hasAny(p: PalaceLite | undefined, names: string[]): boolean {
  if (!p) return false;
  return names.some((n) => p.stars.some((s) => s === n || s.includes(n)));
}

function findByName(palaces: PalaceLite[], name: string): PalaceLite | undefined {
  return palaces.find((p) => p.name === name || p.name.includes(name.replace('宫', '').replace('宮', '')));
}

function findByBranch(palaces: PalaceLite[], branch: string): PalaceLite | undefined {
  return palaces.find((p) => p.earthlyBranch === branch);
}

function neighbors(palaces: PalaceLite[], target: PalaceLite): [PalaceLite | undefined, PalaceLite | undefined] {
  const order = ['寅', '卯', '辰', '巳', '午', '未', '申', '酉', '戌', '亥', '子', '丑'];
  const i = order.indexOf(target.earthlyBranch);
  if (i < 0) return [undefined, undefined];
  const prev = findByBranch(palaces, order[(i + 11) % 12]);
  const next = findByBranch(palaces, order[(i + 1) % 12]);
  return [prev, next];
}

function isClamped(palaces: PalaceLite[], target: PalaceLite, a: string, b: string): boolean {
  const [l, r] = neighbors(palaces, target);
  return (has(l, a) && has(r, b)) || (has(l, b) && has(r, a));
}

function sanFang(palaces: PalaceLite[], ming: PalaceLite): PalaceLite[] {
  const order = ['寅', '卯', '辰', '巳', '午', '未', '申', '酉', '戌', '亥', '子', '丑'];
  const i = order.indexOf(ming.earthlyBranch);
  const branches = [order[i], order[(i + 4) % 12], order[(i + 8) % 12], order[(i + 6) % 12]];
  return branches.map((b) => findByBranch(palaces, b)).filter(Boolean) as PalaceLite[];
}

function brightnessOk(p: PalaceLite, star: string): boolean {
  const b = p.brightness[star] || '';
  return b.includes('庙') || b.includes('廟') || b.includes('旺');
}

function isXian(p: PalaceLite, star: string): boolean {
  const b = p.brightness[star] || '';
  return b.includes('陷') || b.includes('不');
}

const FOUR_SHA = ['擎羊', '陀羅', '陀罗', '火星', '鈴星', '铃星'];

/**
 * 格局判定严格对照卷一《定富局》《定贵局》《定贫贱局》及格局诗诀原文条件。
 * 命中则只返回古本歌诀/定义原文，不附加白话。
 */
export function matchPatterns(chart: BuiltChart): MatchedPattern[] {
  const palaces: PalaceLite[] = chart.palaces.map((p) => {
    const { names, brightness } = allStars(p);
    return {
      name: p.name,
      earthlyBranch: p.earthlyBranch,
      isBodyPalace: p.isBodyPalace,
      stars: names,
      brightness,
    };
  });

  const ming = palaces.find((p) => p.name === '命宫' || p.name === '命宮');
  const shen = palaces.find((p) => p.isBodyPalace);
  const cai = findByName(palaces, '财') || findByName(palaces, '財');
  const tian = findByName(palaces, '田');
  const guan = findByName(palaces, '官') || findByName(palaces, '事业') || findByName(palaces, '事業');
  if (!ming) return [];

  const hits: string[] = [];
  const sf = sanFang(palaces, ming);

  if (['子', '午'].includes(ming.earthlyBranch) && has(ming, '祿存', '禄存')) hits.push('對面朝斗格');
  if (has(ming, '化祿', '化禄') && has(ming, '化權', '化权')) hits.push('科權祿主格');
  if (sf.some((p) => has(p, '左輔', '左辅')) && sf.some((p) => has(p, '右弼'))) hits.push('左右朝垣格');
  if ((has(ming, '文曲') && has(ming, '武曲')) || (has(shen, '文曲') && has(shen, '武曲'))) {
    hits.push('文武格');
  }
  if (has(ming, '文昌') || has(ming, '文曲')) hits.push('文星朝命格');
  if (['子', '午'].includes(ming.earthlyBranch) && has(ming, '巨門', '巨门')) hits.push('石中隱玉格');
  if (
    (has(ming, '貪狼', '贪狼') && has(ming, '火星')) ||
    sf.some((p) => has(p, '貪狼', '贪狼') && has(p, '火星'))
  ) {
    hits.push('火貴格');
    if (has(ming, '貪狼', '贪狼') && has(ming, '火星') && brightnessOk(ming, '貪狼')) {
      hits.push('貪火相逢');
    }
  }

  if (['寅', '申', '子', '午'].includes(ming.earthlyBranch) && has(ming, '七殺', '七杀')) {
    const around = sf.some(
      (p) =>
        hasAny(p, ['天魁', '天鉞', '天钺', '左輔', '左辅', '右弼', '文昌']),
    );
    if (around) hits.push('七殺朝斗格');
  }

  if (cai && isClamped(palaces, cai, '太陽', '太陰')) hits.push('日月夾財格');
  if (ming && isClamped(palaces, ming, '太陽', '太陰')) hits.push('日月夾命');
  if (has(ming, '天相') && isClamped(palaces, ming, '武曲', '天梁')) hits.push('財蔭夾印');
  if (has(ming, '天馬', '天马') && isClamped(palaces, ming, '武曲', '祿存')) hits.push('財祿夾馬');
  if (shen && (shen.name.includes('田') || tian?.isBodyPalace) && tian) {
    if (sf.concat(tian).some((p) => has(p, '天梁')) && sf.concat(tian).some((p) => has(p, '天相'))) {
      hits.push('蔭印拱身');
    }
  }
  if (tian && has(tian, '太陽') && has(tian, '太陰')) hits.push('日月照璧');
  if (ming.earthlyBranch === '午' && has(ming, '太陽') && ming.stars.filter((s) => ['紫微', '天機', '太陽', '武曲', '天同', '廉貞', '天府', '太陰', '貪狼', '巨門', '天相', '天梁', '七殺', '破軍'].includes(normalizeName(s)) || ['紫微', '天機', '太陽', '武曲', '天同', '廉貞', '天府', '太陰', '貪狼', '巨門', '天相', '天梁', '七殺', '破軍'].some((n) => s.includes(n))).length <= 1) {
    hits.push('金燦光輝');
  }
  if (ming.earthlyBranch === '卯' && has(ming, '太陽')) hits.push('日出扶桑');
  if (guan?.earthlyBranch === '卯' && has(guan, '太陽')) hits.push('日出扶桑');
  if (ming.earthlyBranch === '亥' && has(ming, '太陰')) hits.push('月落亥宮');
  if (tian?.earthlyBranch === '子' && has(tian, '太陰')) hits.push('月生滄海');
  if (has(ming, '紫微') && isClamped(palaces, ming, '左輔', '右弼')) hits.push('輔弼拱主');
  if (has(ming, '紫微') && has(ming, '左輔', '左辅') && has(ming, '右弼')) hits.push('君臣慶會');
  if (has(ming, '祿存', '禄存') && isClamped(palaces, ming, '天梁', '天相')) hits.push('財印夾祿');
  if (has(ming, '天馬', '天马') && has(ming, '祿存', '禄存') && has(ming, '天相')) hits.push('祿馬佩印');
  if (has(ming, '天魁') || has(ming, '天鉞', '天钺')) hits.push('坐貴向貴');
  if (has(ming, '天馬', '天马') && has(ming, '擎羊') && ming.earthlyBranch !== '午') hits.push('馬頭帶劍');
  if ((has(ming, '天刑') && has(ming, '廉貞')) || (has(shen, '天刑') && has(shen, '廉貞'))) {
    hits.push('刑囚夾印');
  }
  if (ming.earthlyBranch === '卯' && has(ming, '武曲')) hits.push('武曲守垣');
  if (has(ming, '化權', '化权') && has(ming, '化祿', '化禄') && brightnessOk(ming, '化祿')) {
    hits.push('權祿生逢');
  }
  if (['辰', '戌', '戍', '丑', '未'].includes(ming.earthlyBranch) && has(ming, '擎羊')) {
    hits.push('羊刃入廟');
  }
  if (has(ming, '紫微') && isClamped(palaces, ming, '太陽', '太陰')) hits.push('金輿扶駕');

  if (has(ming, '廉貞') && ming.stars.some((s) => s.includes('空'))) hits.push('生不逢時');
  if (has(ming, '祿存', '禄存') && hasAny(ming, ['天空', '地劫'])) hits.push('祿逢兩殺');
  if (has(ming, '天馬', '天马') && hasAny(ming, ['天空', '地劫'])) hits.push('馬落空亡');
  const sun = palaces.find((p) => has(p, '太陽'));
  const moon = palaces.find((p) => has(p, '太陰'));
  if (sun && moon && ['卯', '辰', '巳', '午'].includes(moon.earthlyBranch) && hasAny(ming, ['巨門', '巨门'])) {
    hits.push('日月藏輝');
  }
  if ((has(ming, '武曲') && has(ming, '廉貞')) || (has(shen, '武曲') && has(shen, '廉貞'))) {
    hits.push('財與囚仇');
  }
  if (has(ming, '破軍', '破军') && isXian(ming, '破軍')) hits.push('一生孤貧');
  if (FOUR_SHA.filter((s) => has(ming, s)).length >= 2 && ming.stars.some((s) => isXian(ming, s))) {
    hits.push('君子在野');
  }
  if (has(ming, '祿存', '禄存') && has(ming, '化祿', '化禄') && hasAny(ming, ['天空', '地劫'])) {
    hits.push('兩重華蓋');
  }

  const unique = [...new Set(hits)];
  const dict = patternDict as Record<string, { condition: string; originalText: string; category: string }>;
  return unique
    .map((name) => {
      const item = dict[name];
      if (!item) return null;
      return {
        name,
        condition: item.condition,
        originalText: item.originalText,
        category: item.category,
      };
    })
    .filter((x): x is MatchedPattern => x !== null);
}
