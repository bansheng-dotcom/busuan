import { Lunar, LunarYear, Solar } from 'lunar-typescript';

export type CalendarType = 'solar' | 'lunar';

/** 农历月：正数为正月份，负数为闰月（与 lunar-typescript 一致） */
export interface LunarYmd {
  year: number;
  month: number;
  day: number;
}

export interface LunarMonthOption {
  /** 传给 Lunar.fromYmd 的月份（闰月为负） */
  value: number;
  label: string;
  dayCount: number;
}

const MONTH_CN = ['正', '二', '三', '四', '五', '六', '七', '八', '九', '十', '冬', '腊'];
const DAY_CN = [
  '初一', '初二', '初三', '初四', '初五', '初六', '初七', '初八', '初九', '初十',
  '十一', '十二', '十三', '十四', '十五', '十六', '十七', '十八', '十九', '二十',
  '廿一', '廿二', '廿三', '廿四', '廿五', '廿六', '廿七', '廿八', '廿九', '三十',
];

export function parseSolarYmd(solarDate: string): { y: number; m: number; d: number } | null {
  const parts = solarDate.split(/[-/]/).map(Number);
  if (parts.length < 3 || parts.some((n) => !n || Number.isNaN(n))) return null;
  return { y: parts[0], m: parts[1], d: parts[2] };
}

export type SolarDateFormat = 'loose' | 'padded';

export function formatSolarYmd(y: number, m: number, d: number, format: SolarDateFormat = 'loose'): string {
  if (format === 'padded') {
    return `${y}-${String(m).padStart(2, '0')}-${String(d).padStart(2, '0')}`;
  }
  return `${y}-${m}-${d}`;
}

export function monthLabel(month: number): string {
  const leap = month < 0;
  const abs = Math.abs(month);
  const base = MONTH_CN[abs - 1] ?? String(abs);
  return leap ? `閏${base}月` : `${base}月`;
}

export function dayLabel(day: number): string {
  return DAY_CN[day - 1] ?? String(day);
}

export function solarToLunar(solarDate: string): LunarYmd | null {
  const p = parseSolarYmd(solarDate);
  if (!p) return null;
  try {
    const lunar = Solar.fromYmd(p.y, p.m, p.d).getLunar();
    return { year: lunar.getYear(), month: lunar.getMonth(), day: lunar.getDay() };
  } catch {
    return null;
  }
}

export function lunarToSolar(lunar: LunarYmd, format: SolarDateFormat = 'loose'): string | null {
  try {
    const solar = Lunar.fromYmd(lunar.year, lunar.month, lunar.day).getSolar();
    return formatSolarYmd(solar.getYear(), solar.getMonth(), solar.getDay(), format);
  } catch {
    return null;
  }
}

export function listLunarMonths(year: number): LunarMonthOption[] {
  const ly = LunarYear.fromYear(year);
  return ly.getMonthsInYear().map((m) => ({
    value: m.getMonth(),
    label: monthLabel(m.getMonth()),
    dayCount: m.getDayCount(),
  }));
}

export function lunarDayCount(year: number, month: number): number {
  const hit = listLunarMonths(year).find((m) => m.value === month);
  return hit?.dayCount ?? 30;
}

export function formatLunarText(lunar: LunarYmd): string {
  try {
    const l = Lunar.fromYmd(lunar.year, lunar.month, lunar.day);
    return `${l.getYearInChinese()}年${l.getMonthInChinese()}月${l.getDayInChinese()}`;
  } catch {
    return `${lunar.year}年${monthLabel(lunar.month)}${dayLabel(lunar.day)}`;
  }
}

export function formatLunarTextFromSolar(solarDate: string): string {
  const lunar = solarToLunar(solarDate);
  if (!lunar) return '';
  return formatLunarText(lunar);
}

export function clampLunarDay(year: number, month: number, day: number): number {
  const max = lunarDayCount(year, month);
  return Math.min(Math.max(1, day), max);
}
