<template>
  <teleport to="body">
    <div
      v-show="open"
      class="orbital-mask"
      aria-hidden="true"
      @click="handleClose"
    />
    <div class="orbital-root" :class="{ open, dragging }" :style="rootStyle">
      <button
        v-for="(item, i) in items"
        :key="item.path"
        type="button"
        class="orbital-child"
        :class="{ active: isActive(item.path), shown: open }"
        :style="childStyle(i)"
        :title="display(item.label, false)"
        :aria-label="display(item.label, false)"
        :tabindex="open ? 0 : -1"
        @click.stop="handleNav(item.path)"
      >
        {{ display(item.tag, false) }}
      </button>

      <button
        type="button"
        class="orbital-main"
        :aria-expanded="open"
        :aria-label="display(open ? '收起菜單' : '打開導航菜單', false)"
        @pointerdown="onDown"
        @pointermove="onMove"
        @pointerup="onUp"
        @pointercancel="onUp"
        @click="onClick"
      >
        {{ display(open ? '合' : '盤', false) }}
      </button>
    </div>
  </teleport>
</template>

<script lang="ts">
import { computed, defineComponent, onMounted, onUnmounted, ref } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import { useDisplayText } from '@/composables/useDisplayText';
import { flattenOrbitalNav, isNavChildActive } from '@/data/siteNav';

const SIZE = 44;
const CHILD = 36;
const RADIUS = 78;
const POS_KEY = 'zw-orbital-nav-pos';
/** 展开后子球不贴边：半径 + 半个子弹 + 边距 */
const RING_CLEAR = RADIUS + CHILD / 2 + 12;

export default defineComponent({
  name: 'OrbitalNavFab',
  setup() {
    const route = useRoute();
    const router = useRouter();
    const { display } = useDisplayText();
    const items = flattenOrbitalNav();
    const n = items.length;

    const open = ref(false);
    const left = ref(0);
    const top = ref(0);
    const placed = ref(false);
    const dragging = ref(false);
    const moved = ref(false);
    let origin = { x: 0, y: 0, left: 0, top: 0 };

    const rootStyle = computed(() =>
      placed.value
        ? { left: `${left.value}px`, top: `${top.value}px`, right: 'auto', bottom: 'auto' }
        : undefined,
    );

    /** 拖动：只防出屏，可贴边 */
    const clampLoose = (l: number, t: number) => {
      const maxL = Math.max(8, window.innerWidth - SIZE - 8);
      const maxT = Math.max(72, window.innerHeight - SIZE - 8);
      return {
        left: Math.min(maxL, Math.max(8, l)),
        top: Math.min(maxT, Math.max(72, t)),
      };
    };

    /** 初始化 / 展开：保证整圈在视口内 */
    const clampRing = (l: number, t: number) => {
      const pad = Math.max(8, RING_CLEAR - SIZE / 2);
      const maxL = Math.max(pad, window.innerWidth - SIZE - pad);
      const maxT = Math.max(Math.max(72, pad), window.innerHeight - SIZE - pad);
      return {
        left: Math.min(maxL, Math.max(pad, l)),
        top: Math.min(maxT, Math.max(Math.max(72, pad), t)),
      };
    };

    const placeDefault = () => {
      const pad = Math.max(8, RING_CLEAR - SIZE / 2);
      try {
        const raw = sessionStorage.getItem(POS_KEY);
        if (raw) {
          const saved = JSON.parse(raw) as { left?: number; top?: number };
          if (typeof saved.left === 'number' && typeof saved.top === 'number') {
            // 恢复拖动位置：不强制整圈可见
            const next = clampLoose(saved.left, saved.top);
            left.value = next.left;
            top.value = next.top;
            placed.value = true;
            return;
          }
        }
      } catch {
        /* ignore */
      }
      // 首次默认：右下内侧，整圈可展
      const next = clampRing(
        window.innerWidth - SIZE - pad,
        window.innerHeight - SIZE - pad,
      );
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

    /** 展开前夹到整圈可见（不限制拖动过程） */
    const ensureRingVisible = () => {
      const next = clampRing(left.value, top.value);
      left.value = next.left;
      top.value = next.top;
    };

    /** 起始角略偏上，减轻正下方与「頂」抢位 */
    const childStyle = (i: number) => {
      const start = -Math.PI / 2 - Math.PI / n;
      const theta = start + (i * 2 * Math.PI) / n;
      const tx = Math.cos(theta) * RADIUS;
      const ty = Math.sin(theta) * RADIUS;
      return {
        '--tx': `${tx}px`,
        '--ty': `${ty}px`,
        transitionDelay: open.value ? `${i * 30}ms` : `${(n - 1 - i) * 18}ms`,
        width: `${CHILD}px`,
        height: `${CHILD}px`,
        marginLeft: `${-CHILD / 2}px`,
        marginTop: `${-CHILD / 2}px`,
      };
    };

    const isActive = (path: string) => isNavChildActive(path, route.path);

    const handleClose = () => {
      open.value = false;
    };

    const handleNav = (path: string) => {
      open.value = false;
      if (isNavChildActive(path, route.path) && path === route.path) return;
      void router.push(path);
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
      if (!moved.value && (Math.abs(dx) > 4 || Math.abs(dy) > 4)) {
        moved.value = true;
        open.value = false;
      }
      if (!moved.value) return;
      const next = clampLoose(origin.left + dx, origin.top + dy);
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
      if (!open.value) ensureRingVisible();
      open.value = !open.value;
    };

    const onResize = () => {
      if (!placed.value) return;
      const next = clampLoose(left.value, top.value);
      left.value = next.left;
      top.value = next.top;
    };

    onMounted(() => {
      placeDefault();
      window.addEventListener('resize', onResize, { passive: true });
    });

    onUnmounted(() => {
      window.removeEventListener('resize', onResize);
    });

    return {
      display,
      items,
      open,
      dragging,
      rootStyle,
      childStyle,
      isActive,
      handleClose,
      handleNav,
      onDown,
      onMove,
      onUp,
      onClick,
    };
  },
});
</script>

<style scoped>
.orbital-mask {
  position: fixed;
  inset: 0;
  z-index: 80;
  background: color-mix(in srgb, var(--zw-ink) 18%, transparent);
}

.orbital-root {
  position: fixed;
  /* JS 定位后覆盖；未 ready 时也先偏内侧，避免首帧贴边 */
  right: calc(16px + 78px);
  bottom: calc(24px + env(safe-area-inset-bottom) + 78px);
  z-index: 90;
  width: 44px;
  height: 44px;
  touch-action: none;
}

.orbital-main {
  position: relative;
  z-index: 2;
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
  user-select: none;
  box-shadow: 0 4px 12px rgba(44, 36, 22, 0.16);
  transition: transform 0.25s ease, background 0.2s ease, color 0.2s ease;
}

.orbital-root.open .orbital-main {
  color: #b42318;
  border-color: color-mix(in srgb, #b42318 55%, var(--zw-gold));
  transform: rotate(90deg);
}

.orbital-root.dragging .orbital-main {
  cursor: grabbing;
  transform: scale(1.06);
  box-shadow: 0 8px 20px rgba(44, 36, 22, 0.22);
}

.orbital-main:hover,
.orbital-main:focus-visible {
  color: var(--zw-ink);
  background: var(--zw-paper);
}

.orbital-child {
  position: absolute;
  left: 50%;
  top: 50%;
  z-index: 1;
  border-radius: 50%;
  border: 1px solid var(--zw-gold);
  background: color-mix(in srgb, var(--zw-paper) 90%, var(--zw-gold));
  color: var(--zw-ink);
  font-family: inherit;
  font-size: 12px;
  letter-spacing: 0.08em;
  cursor: pointer;
  user-select: none;
  box-shadow: 0 3px 10px rgba(44, 36, 22, 0.14);
  opacity: 0;
  pointer-events: none;
  transform: translate(0, 0) scale(0.4) rotate(-90deg);
  transition:
    transform 0.4s cubic-bezier(0.22, 1.2, 0.36, 1),
    opacity 0.32s ease;
}

.orbital-child.shown {
  opacity: 1;
  pointer-events: auto;
  transform: translate(var(--tx), var(--ty)) scale(1) rotate(0deg);
}

.orbital-child.active {
  color: #b42318;
  border-color: #b42318;
  background: color-mix(in srgb, #b42318 10%, var(--zw-paper));
}

.orbital-child:hover,
.orbital-child:focus-visible {
  border-color: var(--zw-primary);
  color: var(--zw-primary);
}
</style>
