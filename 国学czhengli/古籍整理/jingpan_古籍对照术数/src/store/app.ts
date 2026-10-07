import { defineStore } from 'pinia';
import { computed, ref, watch } from 'vue';
import { ElMessage } from 'element-plus';
import type { ScriptMode, ThemeMode } from '@/types';

/** 舊版會寫入 localStorage；刷新需回到默認，故僅內存保存 */
const LEGACY_STORAGE_KEY = 'zw-site-prefs';
const FONT_MIN = 14;
const FONT_MAX = 28;
const DEFAULT_THEME: ThemeMode = 'xuanpaper';
const DEFAULT_SCRIPT: ScriptMode = 'hans';
const DEFAULT_FONT = 18;

export const useAppStore = defineStore('app', () => {
  try {
    localStorage.removeItem(LEGACY_STORAGE_KEY);
  } catch {
    /* ignore */
  }

  const theme = ref<ThemeMode>(DEFAULT_THEME);
  const script = ref<ScriptMode>(DEFAULT_SCRIPT);
  const fontSize = ref(DEFAULT_FONT);

  const isDark = computed(() => theme.value === 'nightsky');
  const iztroLang = computed(() => (script.value === 'hans' ? 'zh-CN' : 'zh-TW'));

  function applyDom() {
    const root = document.documentElement;
    root.classList.toggle('dark', isDark.value);
    root.classList.toggle('theme-nightsky', isDark.value);
    root.classList.toggle('theme-xuanpaper', !isDark.value);
    root.style.setProperty('--zw-font-size', `${fontSize.value}px`);
    root.lang = script.value === 'hans' ? 'zh-Hans' : 'zh-Hant';
  }

  function setTheme(next: ThemeMode) {
    theme.value = next;
  }

  function toggleTheme() {
    theme.value = isDark.value ? 'xuanpaper' : 'nightsky';
  }

  function setScript(next: ScriptMode) {
    script.value = next;
  }

  function toggleScript() {
    script.value = script.value === 'hans' ? 'hant' : 'hans';
  }

  /**
   * 字号极限提示：手机端触碰易触发 ElMessage 的 hover 暂停计时，导致永不关闭。
   * 因此 duration=0 由我们定时强制 close，且未关闭前不重复弹出。
   */
  const FONT_TOAST_MS = 800;
  let fontLimitToastOpen = false;
  let fontLimitToastTimer: ReturnType<typeof setTimeout> | null = null;

  function showFontLimitToast(hans: string, hant: string) {
    if (fontLimitToastOpen) return;
    fontLimitToastOpen = true;
    const instance = ElMessage({
      type: 'info',
      message: script.value === 'hans' ? hans : hant,
      duration: 0,
      onClose: () => {
        fontLimitToastOpen = false;
        if (fontLimitToastTimer != null) {
          clearTimeout(fontLimitToastTimer);
          fontLimitToastTimer = null;
        }
      },
    });
    fontLimitToastTimer = setTimeout(() => {
      instance.close();
    }, FONT_TOAST_MS);
  }

  function bumpFont(delta: number) {
    const next = fontSize.value + delta * 2;
    if (delta > 0 && fontSize.value >= FONT_MAX) {
      showFontLimitToast('已是最大字号', '已是最大字號');
      return;
    }
    if (delta < 0 && fontSize.value <= FONT_MIN) {
      showFontLimitToast('已是最小字号', '已是最小字號');
      return;
    }
    fontSize.value = Math.min(FONT_MAX, Math.max(FONT_MIN, next));
    if (delta > 0 && fontSize.value >= FONT_MAX) {
      showFontLimitToast('已调至最大字号', '已調至最大字號');
    } else if (delta < 0 && fontSize.value <= FONT_MIN) {
      showFontLimitToast('已调至最小字号', '已調至最小字號');
    }
  }

  watch([theme, script, fontSize], () => {
    applyDom();
  });

  applyDom();

  return {
    theme,
    script,
    fontSize,
    isDark,
    iztroLang,
    setTheme,
    toggleTheme,
    setScript,
    toggleScript,
    bumpFont,
  };
});
