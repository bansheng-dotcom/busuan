import { computed } from 'vue';
import { storeToRefs } from 'pinia';
import { useAppStore } from '@/store/app';
import { convertScript } from '@/utils/convert';
import { annotateRareChars } from '@/utils/rareChars';

export function useDisplayText() {
  const store = useAppStore();
  const { script } = storeToRefs(store);

  const display = (text: string, annotate = true) => {
    const converted = convertScript(text, script.value);
    return annotate ? annotateRareChars(converted) : converted;
  };

  const t = computed(() => display);

  return { display, t, script };
}
