<template>
  <teleport to="body">
    <transition name="sheet-fade">
      <div
        v-if="modelValue"
        class="mask"
        @click="handleMask"
        @touchmove.prevent
      />
    </transition>
    <transition name="sheet-slide">
      <div
        v-if="modelValue"
        class="sheet"
        role="dialog"
        aria-modal="true"
        :aria-label="title || undefined"
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
        <header v-if="title || showToolbar" class="toolbar">
          <button v-if="showToolbar" type="button" class="tool-btn" @click="handleCancel">
            {{ cancelText }}
          </button>
          <strong class="title">{{ title }}</strong>
          <button
            v-if="showToolbar"
            type="button"
            class="tool-btn confirm"
            @click="handleConfirm"
          >
            {{ confirmText }}
          </button>
        </header>
        <div class="body">
          <slot />
        </div>
        <button v-if="showCancelFooter" type="button" class="cancel-footer" @click="handleCancel">
          {{ cancelText }}
        </button>
      </div>
    </transition>
  </teleport>
</template>

<script lang="ts">
import { computed, defineComponent, onUnmounted, ref, watch } from 'vue';

const CLOSE_DRAG_PX = 72;

/** 可在弹层内滚动的区域，触摸不拦截 */
const SCROLLABLE_SEL = '.wheel, .option-list, .col, .sheet-scroll';

export default defineComponent({
  name: 'BottomSheet',
  props: {
    modelValue: { type: Boolean, default: false },
    title: { type: String, default: '' },
    showToolbar: { type: Boolean, default: false },
    showCancelFooter: { type: Boolean, default: false },
    closeOnClickMask: { type: Boolean, default: true },
    cancelText: { type: String, default: '取消' },
    confirmText: { type: String, default: '確定' },
  },
  emits: {
    'update:modelValue': (_v: boolean) => true,
    confirm: () => true,
    cancel: () => true,
  },
  setup(props, { emit }) {
    const dragY = ref(0);
    const dragging = ref(false);
    let startY = 0;
    let activePointerId: number | null = null;
    let lockedScrollY = 0;
    let pageLocked = false;
    let touchMoveHandler: ((e: TouchEvent) => void) | null = null;
    let wheelHandler: ((e: WheelEvent) => void) | null = null;

    const isInsideScrollable = (target: EventTarget | null) => {
      if (!(target instanceof Element)) return false;
      return Boolean(target.closest(SCROLLABLE_SEL));
    };

    const lockPage = (lock: boolean) => {
      const html = document.documentElement;
      const body = document.body;

      if (lock) {
        if (pageLocked) return;
        pageLocked = true;
        lockedScrollY = window.scrollY || html.scrollTop || 0;
        html.classList.add('sheet-open');
        body.classList.add('sheet-open');
        body.style.position = 'fixed';
        body.style.top = `-${lockedScrollY}px`;
        body.style.left = '0';
        body.style.right = '0';
        body.style.width = '100%';
        body.style.overflow = 'hidden';
        html.style.overflow = 'hidden';
        html.style.overscrollBehaviorY = 'none';
        body.style.overscrollBehaviorY = 'none';

        touchMoveHandler = (e: TouchEvent) => {
          // 仅允许弹层内滚轮/列表滚动；其余手势全部拦住，避免底层页面跟滚
          if (isInsideScrollable(e.target)) return;
          e.preventDefault();
        };
        wheelHandler = (e: WheelEvent) => {
          if (isInsideScrollable(e.target)) return;
          e.preventDefault();
        };
        document.addEventListener('touchmove', touchMoveHandler, { passive: false });
        document.addEventListener('wheel', wheelHandler, { passive: false });
        return;
      }

      if (!pageLocked) return;
      pageLocked = false;

      if (touchMoveHandler) {
        document.removeEventListener('touchmove', touchMoveHandler);
        touchMoveHandler = null;
      }
      if (wheelHandler) {
        document.removeEventListener('wheel', wheelHandler);
        wheelHandler = null;
      }

      html.classList.remove('sheet-open');
      body.classList.remove('sheet-open');
      body.style.position = '';
      body.style.top = '';
      body.style.left = '';
      body.style.right = '';
      body.style.width = '';
      body.style.overflow = '';
      html.style.overflow = '';
      html.style.overscrollBehaviorY = '';
      body.style.overscrollBehaviorY = '';
      window.scrollTo(0, lockedScrollY);
    };

    const resetDrag = () => {
      dragging.value = false;
      dragY.value = 0;
      startY = 0;
      activePointerId = null;
    };

    watch(
      () => props.modelValue,
      (open) => {
        lockPage(open);
        if (!open) resetDrag();
      },
      { immediate: true },
    );

    onUnmounted(() => lockPage(false));

    const close = () => emit('update:modelValue', false);
    const handleMask = () => {
      if (!props.closeOnClickMask) return;
      emit('cancel');
      close();
    };
    const handleCancel = () => {
      emit('cancel');
      close();
    };
    const handleConfirm = () => {
      emit('confirm');
    };

    const sheetStyle = computed(() => {
      if (dragY.value <= 0) return undefined;
      return {
        transform: `translateY(${dragY.value}px)`,
        transition: dragging.value ? 'none' : 'transform 0.22s ease',
      };
    });

    const onDragStart = (e: PointerEvent) => {
      if (e.button !== 0) return;
      dragging.value = true;
      startY = e.clientY;
      activePointerId = e.pointerId;
      (e.currentTarget as HTMLElement).setPointerCapture(e.pointerId);
    };

    const onDragMove = (e: PointerEvent) => {
      if (!dragging.value || e.pointerId !== activePointerId) return;
      e.preventDefault();
      dragY.value = Math.max(0, e.clientY - startY);
    };

    const onDragEnd = (e: PointerEvent) => {
      if (!dragging.value || e.pointerId !== activePointerId) return;
      try {
        (e.currentTarget as HTMLElement).releasePointerCapture(e.pointerId);
      } catch {
        /* ignore */
      }
      dragging.value = false;
      if (dragY.value >= CLOSE_DRAG_PX) {
        resetDrag();
        emit('cancel');
        close();
        return;
      }
      dragY.value = 0;
      activePointerId = null;
    };

    return {
      sheetStyle,
      handleMask,
      handleCancel,
      handleConfirm,
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
  z-index: 1000;
  background: rgba(20, 14, 30, 0.48);
  touch-action: none;
}
.sheet {
  position: fixed;
  left: 0;
  right: 0;
  bottom: 0;
  z-index: 1001;
  max-height: min(88vh, 640px);
  display: flex;
  flex-direction: column;
  border-radius: 16px 16px 0 0;
  background: var(--zw-paper);
  border-top: 1px solid var(--zw-gold);
  box-shadow: 0 -12px 40px rgba(0, 0, 0, 0.22);
  padding-bottom: env(safe-area-inset-bottom);
  touch-action: manipulation;
}
.drag-zone {
  flex-shrink: 0;
  touch-action: none;
  cursor: grab;
  padding: 10px 0 6px;
  margin: 0;
}
.drag-zone:active {
  cursor: grabbing;
}
.handle {
  width: 36px;
  height: 4px;
  margin: 0 auto;
  border-radius: 999px;
  background: color-mix(in srgb, var(--zw-gold) 70%, transparent);
}
.toolbar {
  display: grid;
  grid-template-columns: 88px 1fr 88px;
  align-items: center;
  gap: 4px;
  padding: 2px 4px 8px;
  border-bottom: 1px solid var(--zw-line);
  flex-shrink: 0;
}
.title {
  text-align: center;
  font-size: 15px;
  letter-spacing: 0.16em;
  font-weight: 600;
  color: var(--zw-ink);
}
.tool-btn {
  border: 0;
  background: transparent;
  color: var(--zw-muted);
  font-family: inherit;
  font-size: 15px;
  letter-spacing: 0.08em;
  min-height: 44px;
  width: 100%;
  padding: 12px 10px;
  display: inline-flex;
  align-items: center;
  justify-content: flex-start;
  box-sizing: border-box;
}
.tool-btn.confirm {
  color: var(--zw-primary);
  font-weight: 600;
  justify-content: flex-end;
}
.body {
  flex: 1;
  min-height: 0;
  /* 禁止整层 body 滚动，避免裁切日期/时间滚轮导致对不齐 */
  overflow: hidden;
  display: flex;
  flex-direction: column;
  overscroll-behavior: contain;
  touch-action: pan-y;
}
.cancel-footer {
  flex-shrink: 0;
  margin: 8px 12px 12px;
  border: 1px solid var(--zw-line);
  border-radius: 10px;
  background: color-mix(in srgb, var(--zw-bg) 50%, var(--zw-paper));
  color: var(--zw-ink);
  font-family: inherit;
  font-size: 15px;
  letter-spacing: 0.12em;
  padding: 12px;
}
.sheet-fade-enter-active,
.sheet-fade-leave-active {
  transition: opacity 0.22s ease;
}
.sheet-fade-enter-from,
.sheet-fade-leave-to {
  opacity: 0;
}
.sheet-slide-enter-active,
.sheet-slide-leave-active {
  transition: transform 0.28s ease;
}
.sheet-slide-enter-from,
.sheet-slide-leave-to {
  transform: translateY(100%);
}
</style>
