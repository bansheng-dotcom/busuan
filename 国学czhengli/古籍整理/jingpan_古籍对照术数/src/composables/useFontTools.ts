import { computed } from 'vue';
import { useRoute } from 'vue-router';

/** 顶栏字号 ± / 复制：仅古籍阅读与词典正文页生效（--zw-font-size 有实际作用） */
export function useFontTools() {
  const route = useRoute();
  const showFontTools = computed(() => route.meta.fontTools === true);
  return { showFontTools };
}
