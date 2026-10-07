export const TIME_INDEX_LABELS = [
  '早子時 23:00–00:59',
  '丑時 01:00–02:59',
  '寅時 03:00–04:59',
  '卯時 05:00–06:59',
  '辰時 07:00–08:59',
  '巳時 09:00–10:59',
  '午時 11:00–12:59',
  '未時 13:00–14:59',
  '申時 15:00–16:59',
  '酉時 17:00–18:59',
  '戌時 19:00–20:59',
  '亥時 21:00–22:59',
  '晚子時 23:00–23:59',
];

/** 均时差（分钟），Spencer 近似。 */
export function equationOfTimeMinutes(date: Date): number {
  const start = Date.UTC(date.getFullYear(), 0, 0);
  const day = (Date.UTC(date.getFullYear(), date.getMonth(), date.getDate()) - start) / 86400000;
  const b = (2 * Math.PI * (day - 81)) / 365;
  return 9.87 * Math.sin(2 * b) - 7.53 * Math.cos(b) - 1.5 * Math.sin(b);
}

export function applyTrueSolarTime(date: Date, longitude: number): Date {
  const eot = equationOfTimeMinutes(date);
  const lngCorr = (longitude - 120) * 4;
  return new Date(date.getTime() + (eot + lngCorr) * 60 * 1000);
}

/** iztro 时辰序号 0 早子 … 12 晚子 */
export function clockToTimeIndex(hour: number, minute: number): number {
  const total = hour + minute / 60;
  if (total >= 23) return 12;
  if (total < 1) return 0;
  return Math.floor((total + 1) / 2);
}

/** 时辰 → 代表性钟表时刻（取该时辰区间起点，便于双向联动） */
export function timeIndexToClock(timeIndex: number): string {
  const idx = Math.min(12, Math.max(0, Math.floor(timeIndex)));
  // 与 clockToTimeIndex 对齐：0=00:00–00:59，1=01:00–02:59 … 12=23:00–23:59
  const hour = idx === 0 ? 0 : idx === 12 ? 23 : idx * 2 - 1;
  return `${String(hour).padStart(2, '0')}:00`;
}

export interface TrueSolarResult {
  dateStr: string;
  timeIndex: number;
  trueClock: string;
  offsetMinutes: number;
}

export function computeTrueSolar(
  solarDate: string,
  hour: number,
  minute: number,
  longitude: number,
): TrueSolarResult {
  const [y, m, d] = solarDate.split('-').map(Number);
  const local = new Date(y, m - 1, d, hour, minute, 0);
  const trueDate = applyTrueSolarTime(local, longitude);
  const offsetMinutes = Math.round((trueDate.getTime() - local.getTime()) / 60000);
  const yy = trueDate.getFullYear();
  const mm = String(trueDate.getMonth() + 1).padStart(2, '0');
  const dd = String(trueDate.getDate()).padStart(2, '0');
  const hh = String(trueDate.getHours()).padStart(2, '0');
  const mi = String(trueDate.getMinutes()).padStart(2, '0');
  return {
    dateStr: `${yy}-${Number(mm)}-${Number(dd)}`,
    timeIndex: clockToTimeIndex(trueDate.getHours(), trueDate.getMinutes()),
    trueClock: `${hh}:${mi}`,
    offsetMinutes,
  };
}
