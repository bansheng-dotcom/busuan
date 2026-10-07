import { Solar } from 'lunar-typescript';

export interface AlmanacDay {
  iso: string;
  solarText: string;
  week: string;
  lunarText: string;
  shengxiao: string;
  yearGanZhi: string;
  monthGanZhi: string;
  dayGanZhi: string;
  timeGanZhi: string;
  nayin: string;
  yi: string[];
  ji: string[];
  chong: string;
  sha: string;
  pengZu: string;
  tianShen: string;
  xiu: string;
  jieQi: string;
  festivals: string[];
  taiShen: string;
  isToday: boolean;
}

function pad(n: number): string {
  return String(n).padStart(2, '0');
}

export function toIsoDate(date: Date): string {
  return `${date.getFullYear()}-${pad(date.getMonth() + 1)}-${pad(date.getDate())}`;
}

export function shiftIsoDate(iso: string, days: number): string {
  const [y, m, d] = iso.split('-').map(Number);
  const next = new Date(y, m - 1, d + days);
  return toIsoDate(next);
}

export function loadAlmanacDay(iso: string, now = new Date()): AlmanacDay {
  const [year, month, day] = iso.split('-').map(Number);
  const todayIso = toIsoDate(now);
  const hour = iso === todayIso ? now.getHours() : 12;
  const minute = iso === todayIso ? now.getMinutes() : 0;
  const solar = Solar.fromYmdHms(year, month, day, hour, minute, 0);
  const lunar = solar.getLunar();
  const jie = lunar.getJieQi();
  const festivals = [...lunar.getFestivals(), ...lunar.getOtherFestivals(), ...solar.getFestivals()];
  return {
    iso,
    solarText: `${solar.getYear()}年${solar.getMonth()}月${solar.getDay()}日`,
    week: `星期${solar.getWeekInChinese()}`,
    lunarText: `農曆${lunar.getYearInChinese()}年${lunar.getMonthInChinese()}月${lunar.getDayInChinese()}`,
    shengxiao: lunar.getYearShengXiao(),
    yearGanZhi: lunar.getYearInGanZhi(),
    monthGanZhi: lunar.getMonthInGanZhi(),
    dayGanZhi: lunar.getDayInGanZhi(),
    timeGanZhi: lunar.getTimeInGanZhi(),
    nayin: lunar.getDayNaYin(),
    yi: lunar.getDayYi(),
    ji: lunar.getDayJi(),
    chong: lunar.getDayChongDesc(),
    sha: lunar.getDaySha(),
    pengZu: `${lunar.getPengZuGan()} ${lunar.getPengZuZhi()}`,
    tianShen: lunar.getDayTianShen(),
    xiu: `${lunar.getXiu()}${lunar.getZheng()}${lunar.getAnimal()}`,
    jieQi: jie || '',
    festivals,
    taiShen: lunar.getDayPositionTai(),
    isToday: iso === todayIso,
  };
}
