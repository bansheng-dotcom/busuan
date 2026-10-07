<template>
  <div class="sheet-time">
    <SheetField :text="displayText" :placeholder="placeholder" @click="handleOpen" />
    <BottomSheet
      v-model="open"
      :title="title"
      show-toolbar
      :cancel-text="cancelText"
      :confirm-text="confirmText"
      @cancel="open = false"
      @confirm="handleConfirm"
    >
      <div ref="wheelsRef" class="wheels">
        <div class="indicator" aria-hidden="true" />
        <div class="fade fade-top" aria-hidden="true" />
        <div class="fade fade-bottom" aria-hidden="true" />
        <div class="wheel-row">
          <div ref="hourWheelRef" class="wheel">
            <div class="spacer" aria-hidden="true" />
            <button
              v-for="h in 24"
              :key="h - 1"
              type="button"
              class="item"
              :class="{ active: draft.h === h - 1 }"
              :data-value="h - 1"
              @click="pickHour(h - 1)"
            >
              {{ pad2(h - 1) }}{{ hourUnit }}
            </button>
            <div class="spacer" aria-hidden="true" />
          </div>
          <div ref="minuteWheelRef" class="wheel">
            <div class="spacer" aria-hidden="true" />
            <button
              v-for="m in minutes"
              :key="m"
              type="button"
              class="item"
              :class="{ active: draft.m === m }"
              :data-value="m"
              @click="pickMinute(m)"
            >
              {{ pad2(m) }}{{ minuteUnit }}
            </button>
            <div class="spacer" aria-hidden="true" />
          </div>
        </div>
      </div>
    </BottomSheet>
  </div>
</template>

<script lang="ts">
import { computed, defineComponent, nextTick, onBeforeUnmount, reactive, ref, watch } from 'vue';
import BottomSheet from './BottomSheet.vue';
import SheetField from './SheetField.vue';
import { bindWheelSnap, scrollAllPickerWheels, scrollPickerItemToCenter, snapWheelToNearest } from './scrollPicker';

const pad2 = (n: number) => String(n).padStart(2, '0');

const nowParts = () => {
  const now = new Date();
  return { h: now.getHours(), m: now.getMinutes() };
};

export default defineComponent({
  name: 'SheetTimePicker',
  components: { BottomSheet, SheetField },
  props: {
    modelValue: { type: String, default: '' },
    title: { type: String, default: '' },
    placeholder: { type: String, default: '請選擇時刻' },
    minuteStep: { type: Number, default: 1 },
    hourUnit: { type: String, default: '時' },
    minuteUnit: { type: String, default: '分' },
    cancelText: { type: String, default: '取消' },
    confirmText: { type: String, default: '確定' },
  },
  emits: {
    'update:modelValue': (_v: string) => true,
    change: (_v: string) => true,
  },
  setup(props, { emit }) {
    const open = ref(false);
    const wheelsRef = ref<HTMLElement | null>(null);
    const hourWheelRef = ref<HTMLElement | null>(null);
    const minuteWheelRef = ref<HTMLElement | null>(null);
    const now = nowParts();
    const draft = reactive({ h: now.h, m: now.m });
    const cleanups: Array<() => void> = [];

    const minutes = computed(() => {
      const step = Math.max(1, props.minuteStep);
      const list: number[] = [];
      for (let m = 0; m < 60; m += step) list.push(m);
      return list;
    });

    const parse = (val: string) => {
      if (!val) return nowParts();
      const [h, m] = val.split(':').map(Number);
      return {
        h: Number.isFinite(h) ? h : nowParts().h,
        m: Number.isFinite(m) ? m : nowParts().m,
      };
    };

    const displayText = computed(() => {
      if (!props.modelValue) return '';
      const { h, m } = parse(props.modelValue);
      return `${pad2(h)}:${pad2(m)}`;
    });

    const unbindSnaps = () => {
      while (cleanups.length) cleanups.pop()?.();
    };

    const bindSnaps = () => {
      unbindSnaps();
      const pairs: Array<[HTMLElement | null, (n: number) => void]> = [
        [hourWheelRef.value, (n) => { draft.h = n; }],
        [minuteWheelRef.value, (n) => { draft.m = n; }],
      ];
      for (const [wheel, setVal] of pairs) {
        if (!wheel) continue;
        cleanups.push(
          bindWheelSnap(wheel, (item) => {
            const n = Number(item.dataset.value);
            if (!Number.isNaN(n)) setVal(n);
          }),
        );
      }
    };

    const scrollActiveIntoView = async () => {
      await nextTick();
      const run = () => scrollAllPickerWheels(wheelsRef.value);
      requestAnimationFrame(() => {
        run();
        window.setTimeout(() => {
          run();
          bindSnaps();
        }, 320);
      });
    };

    watch(open, (v) => {
      if (v) void scrollActiveIntoView();
      else unbindSnaps();
    });

    onBeforeUnmount(unbindSnaps);

    const scrollToValue = (wheel: HTMLElement | null, value: number) => {
      if (!wheel) return;
      const item = wheel.querySelector(`.item[data-value="${value}"]`) as HTMLElement | null;
      if (item) scrollPickerItemToCenter(wheel, item);
    };

    const pickHour = (h: number) => {
      draft.h = h;
      scrollToValue(hourWheelRef.value, h);
    };
    const pickMinute = (m: number) => {
      draft.m = m;
      scrollToValue(minuteWheelRef.value, m);
    };

    const handleOpen = () => {
      const parsed = parse(props.modelValue);
      draft.h = parsed.h;
      // 对齐到步进
      const step = Math.max(1, props.minuteStep);
      draft.m = Math.round(parsed.m / step) * step % 60;
      open.value = true;
    };

    const handleConfirm = () => {
      const applySnap = (wheel: HTMLElement | null, setVal: (n: number) => void) => {
        if (!wheel) return;
        const item = snapWheelToNearest(wheel);
        if (!item) return;
        const n = Number(item.dataset.value);
        if (!Number.isNaN(n)) setVal(n);
      };
      applySnap(hourWheelRef.value, (n) => { draft.h = n; });
      applySnap(minuteWheelRef.value, (n) => { draft.m = n; });
      const val = `${pad2(draft.h)}:${pad2(draft.m)}`;
      emit('update:modelValue', val);
      emit('change', val);
      open.value = false;
    };

    return {
      open,
      wheelsRef,
      hourWheelRef,
      minuteWheelRef,
      draft,
      minutes,
      pad2,
      displayText,
      pickHour,
      pickMinute,
      handleOpen,
      handleConfirm,
    };
  },
});
</script>

<style scoped>
.sheet-time {
  width: 100%;
}
.wheels {
  position: relative;
  height: 264px;
  flex-shrink: 0;
  overflow: hidden;
  background: var(--zw-paper);
}
.indicator {
  position: absolute;
  left: 12px;
  right: 12px;
  top: 50%;
  height: 44px;
  margin-top: -22px;
  border-radius: 8px;
  background: color-mix(in srgb, var(--zw-gold) 22%, var(--zw-paper));
  box-shadow: inset 0 0 0 1px color-mix(in srgb, var(--zw-gold) 40%, transparent);
  pointer-events: none;
  z-index: 1;
}
.fade {
  position: absolute;
  left: 0;
  right: 0;
  height: 100px;
  z-index: 3;
  pointer-events: none;
}
.fade-top {
  top: 0;
  background: linear-gradient(to bottom, var(--zw-paper) 0%, var(--zw-paper) 45%, transparent 100%);
}
.fade-bottom {
  bottom: 0;
  background: linear-gradient(to top, var(--zw-paper) 0%, var(--zw-paper) 45%, transparent 100%);
}
.wheel-row {
  position: relative;
  z-index: 2;
  display: flex;
  height: 100%;
}
.wheel {
  position: relative;
  flex: 1;
  min-width: 0;
  height: 100%;
  overflow-x: hidden;
  overflow-y: auto;
  -webkit-overflow-scrolling: touch;
  overscroll-behavior: contain;
  scroll-snap-type: y mandatory;
  scroll-padding-block: 110px;
  scrollbar-width: none;
  -ms-overflow-style: none;
}
.wheel::-webkit-scrollbar {
  display: none;
  width: 0;
  height: 0;
}
.spacer {
  height: 110px;
  flex-shrink: 0;
  pointer-events: none;
  scroll-snap-align: none;
}
.item {
  display: block;
  position: relative;
  z-index: 1;
  box-sizing: border-box;
  width: 100%;
  height: 44px;
  min-height: 44px;
  flex-shrink: 0;
  margin: 0;
  border: 0;
  background: transparent;
  padding: 0 4px;
  font-family: inherit;
  font-size: 17px;
  letter-spacing: 0.06em;
  color: var(--zw-muted);
  text-align: center;
  line-height: 44px;
  overflow: hidden;
  white-space: nowrap;
  scroll-snap-align: center;
  scroll-snap-stop: always;
}
.item.active {
  color: var(--zw-primary);
  font-weight: 700;
}
</style>
