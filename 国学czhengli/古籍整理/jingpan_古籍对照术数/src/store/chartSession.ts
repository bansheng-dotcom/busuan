import { defineStore } from 'pinia';
import type { ChartFormValue } from '@/views/chart/components/ChartForm.vue';

/** 僅內存：硬刷新清空；站內往返靠 keep-alive / Pinia 保留 */
export interface ChartSessionSnapshot {
  form: ChartFormValue;
  targetDate: string;
  trueSolarNote: string;
}

const LEGACY_STORAGE_KEY = 'zw-chart-session';

export const useChartSessionStore = defineStore('chartSession', () => {
  // 清除舊版 sessionStorage，避免刷新後仍還原命盤
  try {
    sessionStorage.removeItem(LEGACY_STORAGE_KEY);
  } catch {
    /* ignore */
  }

  let snapshot: ChartSessionSnapshot | null = null;
  let scrollY = 0;
  let fromChart = false;

  function saveSnapshot(next: ChartSessionSnapshot) {
    snapshot = {
      form: { ...next.form },
      targetDate: next.targetDate,
      trueSolarNote: next.trueSolarNote,
    };
  }

  function saveScroll() {
    scrollY = window.scrollY;
  }

  function markFromChart() {
    fromChart = true;
    saveScroll();
  }

  function clearFromChart() {
    fromChart = false;
  }

  function clearSnapshot() {
    snapshot = null;
    scrollY = 0;
  }

  function getSnapshot() {
    return snapshot;
  }

  function getScrollY() {
    return scrollY;
  }

  function isFromChart() {
    return fromChart;
  }

  return {
    saveSnapshot,
    saveScroll,
    markFromChart,
    clearFromChart,
    clearSnapshot,
    getSnapshot,
    getScrollY,
    isFromChart,
  };
});
