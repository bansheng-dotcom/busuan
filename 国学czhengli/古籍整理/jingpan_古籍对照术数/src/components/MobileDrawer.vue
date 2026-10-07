<template>
  <teleport to="body">
    <transition name="drawer-fade">
      <div v-if="modelValue" class="mask" @click="handleClose" />
    </transition>
    <transition name="drawer-slide">
      <aside
        v-if="modelValue"
        ref="sheetRef"
        class="sheet"
        role="dialog"
        aria-modal="true"
        :style="sheetStyle"
      >
        <div
          class="drag-zone"
          @pointerdown="onDragStart"
          @pointermove="onDragMove"
          @pointerup="onDragEnd"
          @pointercancel="onDragEnd"
        >
          <div class="handle" aria-hidden="true" />
        </div>
        <header class="sheet-head">
          <img src="/assets/decor/yin-yang.svg" alt="" class="yin" width="28" height="28" />
          <strong>{{ display('快捷入口', false) }}</strong>
          <button type="button" class="close" @click="handleClose">{{ display('關閉', false) }}</button>
        </header>

        <div class="sheet-body">
          <div v-for="group in groups" :key="group.key" class="group">
            <h3 v-if="group.title" class="group-title">{{ display(group.title, false) }}</h3>
            <nav class="grid">
              <router-link
                v-for="item in group.items"
                :key="item.path"
                :to="item.path"
                class="cell"
                @click="handleClose"
              >
                <span class="tag">{{ display(item.tag || '', false) }}</span>
                <b>{{ display(item.label, false) }}</b>
                <em>{{ display(item.desc || '', false) }}</em>
              </router-link>
            </nav>
          </div>
        </div>

      </aside>
    </transition>
  </teleport>
</template>

<script lang="ts">
import { computed, defineComponent, ref, watch } from 'vue';
import { useDisplayText } from '@/composables/useDisplayText';
import { SITE_NAV, type NavChild } from '@/data/siteNav';

interface DrawerGroup {
  key: string;
  title: string;
  items: NavChild[];
}

const CLOSE_DRAG_PX = 72;

export default defineComponent({
  name: 'MobileDrawer',
  props: {
    modelValue: { type: Boolean, default: false },
  },
  emits: {
    'update:modelValue': (_v: boolean) => true,
  },
  setup(props, { emit }) {
    const { display } = useDisplayText();
    const sheetRef = ref<HTMLElement | null>(null);
    const dragY = ref(0);
    const dragging = ref(false);
    let startY = 0;
    let activePointerId: number | null = null;

    const groups = computed(() => {
      const list: DrawerGroup[] = [];
      for (const item of SITE_NAV) {
        if (item.children?.length) {
          list.push({
            key: item.key,
            title: item.label,
            items: item.children,
          });
          continue;
        }
        if (!item.path) continue;
        const lone: NavChild = {
          path: item.path,
          label: item.label,
          tag: item.tag,
          desc: item.desc,
        };
        // 關於等獨立入口：自帶分組標題，避免貼在「工具」格網裡像同一欄
        if (item.key === 'about') {
          list.push({ key: item.key, title: item.label, items: [lone] });
          continue;
        }
        const last = list[list.length - 1];
        if (last && !last.title) {
          last.items.push(lone);
        } else {
          list.push({ key: item.key, title: '', items: [lone] });
        }
      }
      return list;
    });

    const handleClose = () => emit('update:modelValue', false);

    const sheetStyle = computed(() => {
      if (dragY.value <= 0) return undefined;
      return {
        transform: `translateY(${dragY.value}px)`,
        transition: dragging.value ? 'none' : 'transform 0.22s ease',
      };
    });

    const resetDrag = () => {
      dragging.value = false;
      dragY.value = 0;
      startY = 0;
      activePointerId = null;
    };

    const onDragStart = (e: PointerEvent) => {
      if (e.button !== 0) return;
      dragging.value = true;
      startY = e.clientY;
      activePointerId = e.pointerId;
      (e.currentTarget as HTMLElement).setPointerCapture(e.pointerId);
    };

    const onDragMove = (e: PointerEvent) => {
      if (!dragging.value || e.pointerId !== activePointerId) return;
      dragY.value = Math.max(0, e.clientY - startY);
    };

    const onDragEnd = (e: PointerEvent) => {
      if (!dragging.value || e.pointerId !== activePointerId) return;
      (e.currentTarget as HTMLElement).releasePointerCapture(e.pointerId);
      dragging.value = false;

      if (dragY.value >= CLOSE_DRAG_PX) {
        resetDrag();
        handleClose();
        return;
      }

      dragY.value = 0;
      activePointerId = null;
    };

    watch(
      () => props.modelValue,
      (open) => {
        if (!open) resetDrag();
      },
    );

    return {
      display,
      groups,
      sheetRef,
      sheetStyle,
      handleClose,
      onDragStart,
      onDragMove,
      onDragEnd,
    };
  },
});
</script>

<style scoped>
.mask {
  position: fixed;
  inset: 0;
  z-index: 80;
  background: rgba(20, 14, 30, 0.48);
}
.sheet {
  position: fixed;
  left: 0;
  right: 0;
  bottom: 0;
  z-index: 90;
  display: flex;
  flex-direction: column;
  max-height: min(78vh, 640px);
  padding: 10px 0 calc(14px + env(safe-area-inset-bottom));
  border-radius: 18px 18px 0 0;
  background: var(--zw-paper);
  border-top: 1px solid var(--zw-gold);
  box-shadow: 0 -12px 40px rgba(0, 0, 0, 0.22);
  overflow: hidden;
}
.handle {
  width: 42px;
  height: 4px;
  margin: 0 auto;
  border-radius: 999px;
  background: color-mix(in srgb, var(--zw-gold) 70%, transparent);
}
.drag-zone {
  touch-action: none;
  cursor: grab;
  flex: none;
  padding: 10px 16px 14px;
  margin: -6px 0 0;
}
.drag-zone:active {
  cursor: grabbing;
}
.sheet-head {
  display: flex;
  align-items: center;
  gap: 10px;
  flex: none;
  margin: 0 16px 12px;
}
.sheet-body {
  flex: 1;
  min-height: 0;
  overflow: auto;
  padding: 0 16px 12px;
  -webkit-overflow-scrolling: touch;
}
.sheet-head strong {
  letter-spacing: 0.22em;
}
.yin {
  border-radius: 50%;
}
.close {
  margin-left: auto;
  border: 0;
  background: transparent;
  color: var(--zw-muted);
  font-family: inherit;
  letter-spacing: 0.12em;
}
.group + .group {
  margin-top: 14px;
}
.group-title {
  margin: 0 0 8px;
  font-size: 12px;
  letter-spacing: 0.22em;
  color: var(--zw-muted);
  font-weight: 600;
}
.grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 10px;
}
.cell {
  display: flex;
  flex-direction: column;
  gap: 4px;
  padding: 14px 12px;
  border: 1px solid var(--zw-line);
  border-radius: 12px;
  text-decoration: none;
  color: var(--zw-ink);
  background: color-mix(in srgb, var(--zw-bg) 55%, var(--zw-paper));
}
.tag {
  width: 28px;
  height: 28px;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  border-radius: 50%;
  border: 1px solid var(--zw-gold);
  color: var(--zw-gold);
  font-size: 13px;
}
.cell b {
  font-size: 18px;
  letter-spacing: 0.18em;
}
.cell em {
  font-style: normal;
  font-size: 11px;
  line-height: 1.45;
  color: var(--zw-muted);
  letter-spacing: 0.06em;
}
.drawer-fade-enter-active,
.drawer-fade-leave-active {
  transition: opacity 0.22s ease;
}
.drawer-fade-enter-from,
.drawer-fade-leave-to {
  opacity: 0;
}
.drawer-slide-enter-active,
.drawer-slide-leave-active {
  transition: transform 0.28s ease;
}
.drawer-slide-enter-from,
.drawer-slide-leave-to {
  transform: translateY(100%);
}
</style>
