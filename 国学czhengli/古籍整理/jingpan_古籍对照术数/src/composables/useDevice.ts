import { onMounted, onUnmounted, ref, computed } from 'vue';

/** 768px 以下视为 H5；以上为 PC。 */
const MOBILE_MQ = '(max-width: 767.98px)';

export function useDevice() {
  const isMobile = ref(false);
  let mql: MediaQueryList | null = null;

  const sync = () => {
    isMobile.value = Boolean(mql?.matches);
  };

  onMounted(() => {
    mql = window.matchMedia(MOBILE_MQ);
    sync();
    mql.addEventListener('change', sync);
  });

  onUnmounted(() => {
    mql?.removeEventListener('change', sync);
  });

  const isPc = computed(() => !isMobile.value);
  const deviceClass = computed(() => (isMobile.value ? 'is-h5' : 'is-pc'));

  return { isMobile, isPc, deviceClass };
}
