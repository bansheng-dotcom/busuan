<template>
  <teleport to="body">
    <button
      v-show="visible"
      type="button"
      class="back-to-top"
      :class="{ dragging }"
      :style="btnStyle"
      :aria-label="display('回到頂部', false)"
      @pointerdown="onDown"
      @pointermove="onMove"
      @pointerup="onUp"
      @pointercancel="onUp"
      @click="onClick"
    >
      {{ display('頂', false) }}
    </button>
  </teleport>
</template>

<script lang="ts">
import { computed, defineComponent, onMounted, onUnmounted, ref, watch } from 'vue';
import { useRoute } from 'vue-router';
import { useDisplayText } from '@/composables/useDisplayText';

const SIZE = 44;
const THRESHOLD = 240;
const POS_KEY = 'zw-to-top-pos';

function isScrollBox(el: Element): el is HTMLElement {
  if (!(el instanceof HTMLElement)) return false;
  if (el.scrollHeight <= el.clientHeight + 1) return false;
  const oy = getComputedStyle(el).overflowY;
  return oy === 'auto' || oy === 'scroll' || oy === 'overlay';
}

function maxPageScroll(): number {
  let max = window.scrollY || document.documentElement.scrollTop || 0;
  document.querySelectorAll('.reader, [data-scroll-root]').forEach((el) => {
    if (el instanceof HTMLElement) max = Math.max(max, el.scrollTop);
  });
  return max;
}

export default defineComponent({
  name: 'BackToTop',
  setup() {
    const route = useRoute();
    const { display } = useDisplayText();
    const visible = ref(false);
    const left = ref(0);
    const top = ref(0);
    const placed = ref(false);
    const dragging = ref(false);
    const moved = ref(false);
    let origin = { x: 0, y: 0, left: 0, top: 0 };
    let raf = 0;

    const btnStyle = computed(() =>
      placed.value
        ? { left: `${left.value}px`, top: `${top.value}px`, right: 'auto', bottom: 'auto' }
        : undefined,
    );

    const clamp = (l: number, t: number) => {
      const maxL = Math.max(8, window.innerWidth - SIZE - 8);
      const maxT = Math.max(8, window.innerHeight - SIZE - 8);
      return {
        left: Math.min(maxL, Math.max(8, l)),
        top: Math.min(maxT, Math.max(72, t)),
      };
    };

    const placeDefault = () => {
      try {
        const raw = sessionStorage.getItem(POS_KEY);
        if (raw) {
          const saved = JSON.parse(raw) as { left?: number; top?: number };
          if (typeof saved.left === 'number' && typeof saved.top === 'number') {
            const next = clamp(saved.left, saved.top);
            left.value = next.left;
            top.value = next.top;
            placed.value = true;
            return;
          }
        }
      } catch {
        /* ignore */
      }
      const next = clamp(window.innerWidth - SIZE - 16, window.innerHeight - SIZE - 24);
      left.value = next.left;
      top.value = next.top;
      placed.value = true;
    };

    const savePos = () => {
      try {
        sessionStorage.setItem(POS_KEY, JSON.stringify({ left: left.value, top: top.value }));
      } catch {
        /* ignore */
      }
    };

    const syncVisible = () => {
      visible.value = maxPageScroll() > THRESHOLD;
      if (visible.value && !placed.value) placeDefault();
    };

    const scheduleSync = (e?: Event) => {
      if (e?.target instanceof HTMLElement && e.target !== document.documentElement && e.target !== document.body) {
        if (e.target.scrollTop > THRESHOLD) {
          visible.value = true;
          if (!placed.value) placeDefault();
          return;
        }
      }
      if (raf) return;
      raf = window.requestAnimationFrame(() => {
        raf = 0;
        syncVisible();
      });
    };

    const scrollAllToTop = () => {
      window.scrollTo({ top: 0, behavior: 'smooth' });
      document.querySelectorAll('.reader, [data-scroll-root]').forEach((el) => {
        if (!(el instanceof HTMLElement) || el.scrollTop <= 0) return;
        el.scrollTo({ top: 0, behavior: 'smooth' });
      });
      // 兜底：页面内其他可滚动容器
      document.querySelectorAll('main *').forEach((el) => {
        if (!(el instanceof HTMLElement) || el.scrollTop <= 0 || !isScrollBox(el)) return;
        el.scrollTo({ top: 0, behavior: 'smooth' });
      });
    };

    const onDown = (e: PointerEvent) => {
      if (e.button !== 0) return;
      e.preventDefault();
      if (!placed.value) placeDefault();
      dragging.value = true;
      moved.value = false;
      origin = { x: e.clientX, y: e.clientY, left: left.value, top: top.value };
      (e.currentTarget as HTMLElement).setPointerCapture?.(e.pointerId);
    };

    const onMove = (e: PointerEvent) => {
      if (!dragging.value) return;
      const dx = e.clientX - origin.x;
      const dy = e.clientY - origin.y;
      if (Math.abs(dx) > 4 || Math.abs(dy) > 4) moved.value = true;
      const next = clamp(origin.left + dx, origin.top + dy);
      left.value = next.left;
      top.value = next.top;
    };

    const onUp = (e: PointerEvent) => {
      if (!dragging.value) return;
      dragging.value = false;
      try {
        (e.currentTarget as HTMLElement)?.releasePointerCapture?.(e.pointerId);
      } catch {
        /* ignore */
      }
      if (moved.value) savePos();
    };

    const onClick = () => {
      if (moved.value) return;
      scrollAllToTop();
    };

    const onResize = () => {
      if (!placed.value) return;
      const next = clamp(left.value, top.value);
      left.value = next.left;
      top.value = next.top;
    };

    watch(
      () => route.fullPath,
      () => {
        window.setTimeout(syncVisible, 80);
      },
    );

    onMounted(() => {
      placeDefault();
      syncVisible();
      window.addEventListener('scroll', scheduleSync, { passive: true });
      document.addEventListener('scroll', scheduleSync, { passive: true, capture: true });
      window.addEventListener('resize', onResize, { passive: true });
    });

    onUnmounted(() => {
      if (raf) window.cancelAnimationFrame(raf);
      window.removeEventListener('scroll', scheduleSync);
      document.removeEventListener('scroll', scheduleSync, true);
      window.removeEventListener('resize', onResize);
    });

    return {
      display,
      visible,
      dragging,
      btnStyle,
      onDown,
      onMove,
      onUp,
      onClick,
    };
  },
});
</script>

<style scoped>
.back-to-top {
  position: fixed;
  right: 16px;
  bottom: calc(24px + env(safe-area-inset-bottom));
  z-index: 70;
  width: 44px;
  height: 44px;
  border-radius: 50%;
  border: 1px solid var(--zw-gold);
  background: color-mix(in srgb, var(--zw-paper) 88%, var(--zw-gold));
  color: var(--zw-primary);
  font-family: inherit;
  font-size: 14px;
  letter-spacing: 0.12em;
  cursor: grab;
  touch-action: none;
  user-select: none;
  box-shadow: 0 4px 12px rgba(44, 36, 22, 0.16);
}
.back-to-top.dragging {
  cursor: grabbing;
  transform: scale(1.06);
  box-shadow: 0 8px 20px rgba(44, 36, 22, 0.22);
}
.back-to-top:hover,
.back-to-top:focus-visible {
  color: var(--zw-ink);
  background: var(--zw-paper);
}
</style>
