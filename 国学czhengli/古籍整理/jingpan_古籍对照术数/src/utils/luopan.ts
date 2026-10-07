/** 风水地盘：子在正北，顺时针。阴阳为三合地盘常例，仅供对照。 */

export type YinYang = 'yang' | 'yin';
export type Yao = 0 | 1;

export interface Mountain {
  name: string;
  gua: string;
  dir: string;
  deg: number;
  yinYang: YinYang;
}

export interface Trigram {
  name: string;
  yaos: [Yao, Yao, Yao];
  deg: number;
  luoshu: number;
}

const YANG_MOUNTAINS = new Set(['壬', '子', '癸', '寅', '甲', '乙', '辰', '午', '坤', '申', '庚', '戌']);

export const MOUNTAINS: Mountain[] = [
  { name: '子', gua: '坎', dir: '正北', deg: 0 },
  { name: '癸', gua: '坎', dir: '北偏東', deg: 15 },
  { name: '丑', gua: '艮', dir: '東北偏北', deg: 30 },
  { name: '艮', gua: '艮', dir: '東北', deg: 45 },
  { name: '寅', gua: '艮', dir: '東北偏東', deg: 60 },
  { name: '甲', gua: '震', dir: '東偏北', deg: 75 },
  { name: '卯', gua: '震', dir: '正東', deg: 90 },
  { name: '乙', gua: '震', dir: '東偏南', deg: 105 },
  { name: '辰', gua: '巽', dir: '東南偏東', deg: 120 },
  { name: '巽', gua: '巽', dir: '東南', deg: 135 },
  { name: '巳', gua: '巽', dir: '東南偏南', deg: 150 },
  { name: '丙', gua: '離', dir: '南偏東', deg: 165 },
  { name: '午', gua: '離', dir: '正南', deg: 180 },
  { name: '丁', gua: '離', dir: '南偏西', deg: 195 },
  { name: '未', gua: '坤', dir: '西南偏南', deg: 210 },
  { name: '坤', gua: '坤', dir: '西南', deg: 225 },
  { name: '申', gua: '坤', dir: '西南偏西', deg: 240 },
  { name: '庚', gua: '兌', dir: '西偏南', deg: 255 },
  { name: '酉', gua: '兌', dir: '正西', deg: 270 },
  { name: '辛', gua: '兌', dir: '西偏北', deg: 285 },
  { name: '戌', gua: '乾', dir: '西北偏西', deg: 300 },
  { name: '乾', gua: '乾', dir: '西北', deg: 315 },
  { name: '亥', gua: '乾', dir: '西北偏北', deg: 330 },
  { name: '壬', gua: '坎', dir: '北偏西', deg: 345 },
].map((item) => ({
  ...item,
  yinYang: YANG_MOUNTAINS.has(item.name) ? 'yang' : 'yin',
}));

/** 爻序自下而上：1 阳 0 阴。洛书配后天方位。 */
export const HOU_TIAN: Trigram[] = [
  { name: '坎', yaos: [0, 1, 0], deg: 0, luoshu: 1 },
  { name: '艮', yaos: [0, 0, 1], deg: 45, luoshu: 8 },
  { name: '震', yaos: [1, 0, 0], deg: 90, luoshu: 3 },
  { name: '巽', yaos: [0, 1, 1], deg: 135, luoshu: 4 },
  { name: '離', yaos: [1, 0, 1], deg: 180, luoshu: 9 },
  { name: '坤', yaos: [0, 0, 0], deg: 225, luoshu: 2 },
  { name: '兌', yaos: [1, 1, 0], deg: 270, luoshu: 7 },
  { name: '乾', yaos: [1, 1, 1], deg: 315, luoshu: 6 },
];

/** 先天方位：乾南坤北离东坎西。 */
export const XIAN_TIAN: Trigram[] = [
  { name: '坤', yaos: [0, 0, 0], deg: 0, luoshu: 0 },
  { name: '震', yaos: [1, 0, 0], deg: 45, luoshu: 0 },
  { name: '離', yaos: [1, 0, 1], deg: 90, luoshu: 0 },
  { name: '兌', yaos: [1, 1, 0], deg: 135, luoshu: 0 },
  { name: '乾', yaos: [1, 1, 1], deg: 180, luoshu: 0 },
  { name: '巽', yaos: [0, 1, 1], deg: 225, luoshu: 0 },
  { name: '坎', yaos: [0, 1, 0], deg: 270, luoshu: 0 },
  { name: '艮', yaos: [0, 0, 1], deg: 315, luoshu: 0 },
];

export const LUOSHU_HAN = ['', '一', '二', '三', '四', '五', '六', '七', '八', '九'] as const;

export function normalizeDeg(deg: number): number {
  return ((deg % 360) + 360) % 360;
}

/** 將方位角映到 (−180, 180]，便於顯示「偏差 ±N°」 */
export function signedDeg(deg: number): number {
  const n = normalizeDeg(deg);
  return n > 180 ? n - 360 : n;
}

export function lerpHeading(from: number, to: number, t: number): number {
  const diff = ((to - from + 540) % 360) - 180;
  return normalizeDeg(from + diff * t);
}

export function mountainAt(heading: number): Mountain {
  const idx = Math.round(normalizeDeg(heading) / 15) % MOUNTAINS.length;
  return MOUNTAINS[idx];
}

function guaAt(heading: number, ring: Trigram[]): Trigram {
  const idx = Math.round(normalizeDeg(heading) / 45) % ring.length;
  return ring[idx];
}

export function houTianAt(heading: number): Trigram {
  return guaAt(heading, HOU_TIAN);
}

export function xianTianAt(heading: number): Trigram {
  return guaAt(heading, XIAN_TIAN);
}

export function yaoDrawn(yaos: Trigram['yaos']): Yao[] {
  return [...yaos].reverse();
}
