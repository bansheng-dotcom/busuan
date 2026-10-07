/** 倪海厦版六壬时课：大安→留连→速喜→赤口→小吉→空亡，顺时针。 */

export interface LiurenPalace {
  key: string;
  name: string;
  luck: '吉' | '凶';
  summary: string;
}

export const LIUREN_PALACES: LiurenPalace[] = [
  {
    key: 'daan',
    name: '大安',
    luck: '吉',
    summary: '平安吉祥，諸事順利，約一週左右可見結果。',
  },
  {
    key: 'liulian',
    name: '留連',
    luck: '凶',
    summary: '事情停滯不前，此行不利，需謹慎行事。',
  },
  {
    key: 'suxi',
    name: '速喜',
    luck: '吉',
    summary: '立竿見影，馬上看到結果，適合找尋失物。',
  },
  {
    key: 'chikou',
    name: '赤口',
    luck: '凶',
    summary: '有第三者介入，小人竊財，是非多因人為因素。',
  },
  {
    key: 'xiaoji',
    name: '小吉',
    luck: '吉',
    summary: '吉祥順利，但需等待，約兩週左右可見結果。',
  },
  {
    key: 'kongwang',
    name: '空亡',
    luck: '凶',
    summary: '事情難成，可以斷念，建議放棄或另尋他法。',
  },
];

/** 時辰地支，子=1 … 亥=12 */
export const LIUREN_HOURS = [
  { value: 1, label: '子時 23:00–00:59' },
  { value: 2, label: '丑時 01:00–02:59' },
  { value: 3, label: '寅時 03:00–04:59' },
  { value: 4, label: '卯時 05:00–06:59' },
  { value: 5, label: '辰時 07:00–08:59' },
  { value: 6, label: '巳時 09:00–10:59' },
  { value: 7, label: '午時 11:00–12:59' },
  { value: 8, label: '未時 13:00–14:59' },
  { value: 9, label: '申時 15:00–16:59' },
  { value: 10, label: '酉時 17:00–18:59' },
  { value: 11, label: '戌時 19:00–20:59' },
  { value: 12, label: '亥時 21:00–22:59' },
] as const;

export interface LiurenInput {
  /** 農曆月 1–12 */
  month: number;
  /** 農曆日 1–30 */
  day: number;
  /** 時辰 1子–12亥 */
  hour: number;
}

export interface LiurenResult {
  index: number;
  palace: LiurenPalace;
  monthIndex: number;
  dayIndex: number;
  hourIndex: number;
}

/** 從起點走 n 步（含本宮為第 1 步） */
export function walkSteps(startIndex: number, steps: number): number {
  const n = LIUREN_PALACES.length;
  const move = Math.max(1, Math.floor(steps)) - 1;
  return (startIndex + move) % n;
}

/**
 * 月、日、時均從當宮起算（含本宮）。
 * 例：農曆四月五日戌時 → 空亡。
 */
export function castLiuren(input: LiurenInput): LiurenResult {
  const month = Math.min(12, Math.max(1, Math.floor(input.month)));
  const day = Math.min(30, Math.max(1, Math.floor(input.day)));
  const hour = Math.min(12, Math.max(1, Math.floor(input.hour)));

  const monthIndex = walkSteps(0, month);
  const dayIndex = walkSteps(monthIndex, day);
  const hourIndex = walkSteps(dayIndex, hour);

  return {
    index: hourIndex,
    palace: LIUREN_PALACES[hourIndex],
    monthIndex,
    dayIndex,
    hourIndex,
  };
}

/** 鐘錶時刻 → 六壬時辰序（子=1…亥=12） */
export function clockToLiurenHour(hour: number, minute = 0): number {
  const total = hour + minute / 60;
  if (total >= 23 || total < 1) return 1;
  return Math.floor((total + 1) / 2) + 1;
}
