import { HEXAGRAM_TRIGRAMS } from '@/utils/yijingTrigrams';

/** 三钱：阳面=3，阴面=2 */
export type CoinFace = 2 | 3;

export type YaoKind = 'oldYin' | 'youngYang' | 'youngYin' | 'oldYang';

export interface YaoLine {
  /** 自下而上 0=初爻 … 5=上爻 */
  position: number;
  sum: 6 | 7 | 8 | 9;
  kind: YaoKind;
  /** 1 阳 0 阴 */
  yang: 0 | 1;
  changing: boolean;
  coins: [CoinFace, CoinFace, CoinFace];
  label: string;
}

const KIND_BY_SUM: Record<6 | 7 | 8 | 9, { kind: YaoKind; yang: 0 | 1; changing: boolean; label: string }> = {
  6: { kind: 'oldYin', yang: 0, changing: true, label: '老陰' },
  7: { kind: 'youngYang', yang: 1, changing: false, label: '少陽' },
  8: { kind: 'youngYin', yang: 0, changing: false, label: '少陰' },
  9: { kind: 'oldYang', yang: 1, changing: true, label: '老陽' },
};

const TRIGRAM_BITS: Record<string, number> = {
  天: 0b111,
  澤: 0b110,
  火: 0b101,
  雷: 0b100,
  風: 0b011,
  水: 0b010,
  山: 0b001,
  地: 0b000,
};

/** bits0–2 下卦，bits3–5 上卦 → 文王序卦号 */
const BITS_TO_INDEX: Record<number, number> = (() => {
  const out: Record<number, number> = {};
  for (const [idx, v] of Object.entries(HEXAGRAM_TRIGRAMS)) {
    const bits = ((TRIGRAM_BITS[v.upper] ?? 0) << 3) | (TRIGRAM_BITS[v.lower] ?? 0);
    out[bits] = Number(idx);
  }
  return out;
})();

export function tossCoin(): CoinFace {
  return Math.random() < 0.5 ? 3 : 2;
}

export function tossThreeCoins(): [CoinFace, CoinFace, CoinFace] {
  return [tossCoin(), tossCoin(), tossCoin()];
}

/** 一次成卦：六爻各擲三錢（算法同傳統，僅合併為一次） */
export function castFullHexagram(): YaoLine[] {
  return Array.from({ length: 6 }, (_, i) => coinsToYao(tossThreeCoins(), i));
}

/** 六爻結果對應的六枚展示面（陽3 / 陰2，自初至上） */
export function linesToDisplayFaces(lines: YaoLine[]): CoinFace[] {
  return lines.map((l) => (l.yang ? 3 : 2));
}

/** 一次成卦：隨機搖筒時長 + 逐枚隨機間隔出幣（順序仍為初→上） */
export interface SixPourSchedule {
  /** 各幣開始灑出延遲（秒） */
  delaysSec: number[];
  /** 先搖筒時長（秒） */
  shakeSec: number;
  /** 單幣落地動畫（秒） */
  pourSec: number;
  /** 整段動畫總等待（毫秒） */
  totalMs: number;
}

function mulberry32(seed: number): () => number {
  let t = seed >>> 0 || 1;
  return () => {
    t += 0x6d2b79f5;
    let r = Math.imul(t ^ (t >>> 15), 1 | t);
    r ^= r + Math.imul(r ^ (r >>> 7), 61 | r);
    return ((r ^ (r >>> 14)) >>> 0) / 4294967296;
  };
}

export function createSixPourSchedule(seed: number): SixPourSchedule {
  const rnd = mulberry32(seed * 9973 + 17);
  const pourSec = 0.85;
  // 多搖幾下：約 1.1～2.0 秒
  const shakeSec = 1.1 + rnd() * 0.9;
  const delaysSec: number[] = [];
  let t = shakeSec;
  for (let i = 0; i < 6; i += 1) {
    delaysSec.push(Number(t.toFixed(3)));
    // 出幣間隔隨機 0.2～0.75 秒，不全等距
    t += 0.2 + rnd() * 0.55;
  }
  const lastStart = delaysSec[5] ?? shakeSec;
  const totalMs = Math.ceil((lastStart + pourSec + 0.35) * 1000);
  return { delaysSec, shakeSec: Number(shakeSec.toFixed(3)), pourSec, totalMs };
}

export function coinsToYao(coins: [CoinFace, CoinFace, CoinFace], position: number): YaoLine {
  const sum = (coins[0] + coins[1] + coins[2]) as 6 | 7 | 8 | 9;
  const meta = KIND_BY_SUM[sum];
  return {
    position,
    sum,
    coins,
    ...meta,
  };
}

export function linesToBits(lines: YaoLine[]): number {
  let bits = 0;
  for (let i = 0; i < 6; i += 1) {
    if (lines[i]?.yang) bits |= 1 << i;
  }
  return bits;
}

export function changedBits(lines: YaoLine[]): number {
  let bits = 0;
  for (let i = 0; i < 6; i += 1) {
    const line = lines[i];
    if (!line) continue;
    const yang = line.changing ? (line.yang ? 0 : 1) : line.yang;
    if (yang) bits |= 1 << i;
  }
  return bits;
}

export function bitsToIndex(bits: number): number {
  return BITS_TO_INDEX[bits & 0b111111] ?? 0;
}

export interface CastResult {
  lines: YaoLine[];
  primaryIndex: number;
  relatingIndex: number | null;
  changingPositions: number[];
}

export function finishCast(lines: YaoLine[]): CastResult {
  const primaryIndex = bitsToIndex(linesToBits(lines));
  const changingPositions = lines.filter((l) => l.changing).map((l) => l.position);
  const relatingIndex = changingPositions.length ? bitsToIndex(changedBits(lines)) : null;
  return { lines, primaryIndex, relatingIndex, changingPositions };
}

/** 是否像一次「摇一摇」：短时加速度峰值 */
export function isShakeGesture(acc: { x: number; y: number; z: number }, threshold = 18): boolean {
  return Math.hypot(acc.x, acc.y, acc.z) > threshold;
}
