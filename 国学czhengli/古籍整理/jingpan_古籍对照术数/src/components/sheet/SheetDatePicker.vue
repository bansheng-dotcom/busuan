<template>
  <div class="sheet-date">
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
          <div ref="yearWheelRef" class="wheel">
            <div class="spacer" aria-hidden="true" />
            <button
              v-for="y in years"
              :key="y"
              type="button"
              class="item"
              :class="{ active: draft.y === y }"
              :data-value="y"
              @click="pickYear(y)"
            >
              {{ y }}{{ yearUnit }}
            </button>
            <div class="spacer" aria-hidden="true" />
          </div>
          <div ref="monthWheelRef" class="wheel">
            <div class="spacer" aria-hidden="true" />
            <button
              v-for="m in 12"
              :key="m"
              type="button"
              class="item"
              :class="{ active: draft.m === m }"
              :data-value="m"
              @click="pickMonth(m)"
            >
              {{ m }}{{ monthUnit }}
            </button>
            <div class="spacer" aria-hidden="true" />
          </div>
          <div ref="dayWheelRef" class="wheel">
            <div class="spacer" aria-hidden="true" />
            <button
              v-for="d in daysInMonth"
              :key="d"
              type="button"
              class="item"
              :class="{ active: draft.d === d }"
              :data-value="d"
              @click="pickDay(d)"
            >
              {{ d }}{{ dayUnit }}
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

const todayParts = () => {
  const now = new Date();
  return { y: now.getFullYear(), m: now.getMonth() + 1, d: now.getDate() };
};

export default defineComponent({
  name: 'SheetDatePicker',
  components: { BottomSheet, SheetField },
  props: {
    modelValue: { type: String, default: '' },
    title: { type: String, default: '' },
    placeholder: { type: String, default: '請選擇日期' },
    format: { type: String, default: 'loose' },
    minYear: { type: Number, default: 1900 },
    maxYear: { type: Number, default: () => new Date().getFullYear() },
    yearUnit: { type: String, default: '年' },
    monthUnit: { type: String, default: '月' },
    dayUnit: { type: String, default: '日' },
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
    const yearWheelRef = ref<HTMLElement | null>(null);
    const monthWheelRef = ref<HTMLElement | null>(null);
    const dayWheelRef = ref<HTMLElement | null>(null);
    const today = todayParts();
    const draft = reactive({ y: today.y, m: today.m, d: today.d });
    const cleanups: Array<() => void> = [];

    const parse = (val: string) => {
      const parts = val.split(/[-/]/).map(Number);
      if (parts.length < 3 || parts.some((n) => Number.isNaN(n))) return todayParts();
      return { y: parts[0], m: parts[1], d: parts[2] };
    };

    const formatValue = (y: number, m: number, d: number) => {
      if (props.format === 'padded') return `${y}-${pad2(m)}-${pad2(d)}`;
      return `${y}-${m}-${d}`;
    };

    const displayText = computed(() => {
      if (!props.modelValue) return '';
      const { y, m, d } = parse(props.modelValue);
      return `${y}${props.yearUnit}${m}${props.monthUnit}${d}${props.dayUnit}`;
    });

    const years = computed(() => {
      const list: number[] = [];
      for (let y = props.maxYear; y >= props.minYear; y -= 1) list.push(y);
      return list;
    });

    const daysInMonth = computed(() => {
      const count = new Date(draft.y, draft.m, 0).getDate();
      return Array.from({ length: count }, (_, i) => i + 1);
    });

    watch(daysInMonth, (days) => {
      if (draft.d > days.length) draft.d = days.length;
    });

    const unbindSnaps = () => {
      while (cleanups.length) cleanups.pop()?.();
    };

    const bindSnaps = () => {
      unbindSnaps();
      const pairs: Array<[HTMLElement | null, (n: number) => void]> = [
        [yearWheelRef.value, (n) => { draft.y = n; }],
        [monthWheelRef.value, (n) => { draft.m = n; }],
        [dayWheelRef.value, (n) => { draft.d = n; }],
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

    watch(
      () => [draft.y, draft.m] as const,
      async () => {
        if (!open.value) return;
        await nextTick();
        // 日列重建后重新绑定吸附
        bindSnaps();
        scrollAllPickerWheels(wheelsRef.value);
      },
    );

    onBeforeUnmount(unbindSnaps);

    const scrollToValue = (wheel: HTMLElement | null, value: number) => {
      if (!wheel) return;
      const item = wheel.querySelector(`.item[data-value="${value}"]`) as HTMLElement | null;
      if (item) scrollPickerItemToCenter(wheel, item);
    };

    const pickYear = (y: number) => {
      draft.y = y;
      scrollToValue(yearWheelRef.value, y);
    };
    const pickMonth = (m: number) => {
      draft.m = m;
      scrollToValue(monthWheelRef.value, m);
    };
    const pickDay = (d: number) => {
      draft.d = d;
      scrollToValue(dayWheelRef.value, d);
    };

    const handleOpen = () => {
      const parsed = parse(props.modelValue || '');
      draft.y = Math.min(Math.max(parsed.y, props.minYear), props.maxYear);
      draft.m = parsed.m;
      draft.d = parsed.d;
      open.value = true;
    };

    const handleConfirm = () => {
      // 确认前强制吸附到整格，避免停在两格之间
      const applySnap = (wheel: HTMLElement | null, setVal: (n: number) => void) => {
        if (!wheel) return;
        const item = snapWheelToNearest(wheel);
        if (!item) return;
        const n = Number(item.dataset.value);
        if (!Number.isNaN(n)) setVal(n);
      };
      applySnap(yearWheelRef.value, (n) => { draft.y = n; });
      applySnap(monthWheelRef.value, (n) => { draft.m = n; });
      applySnap(dayWheelRef.value, (n) => { draft.d = n; });
      const val = formatValue(draft.y, draft.m, draft.d);
      emit('update:modelValue', val);
      emit('change', val);
      open.value = false;
    };

    return {
      open,
      wheelsRef,
      yearWheelRef,
      monthWheelRef,
      dayWheelRef,
      draft,
      years,
      daysInMonth,
      displayText,
      pickYear,
      pickMonth,
      pickDay,
      handleOpen,
      handleConfirm,
    };
  },
});
</script>

<style scoped>
.sheet-date {
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
