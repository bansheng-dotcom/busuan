<template>
  <div class="sheet-lunar-date">
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
              :class="{ active: draft.year === y }"
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
              v-for="m in monthOptions"
              :key="m.value"
              type="button"
              class="item"
              :class="{ active: draft.month === m.value }"
              :data-value="m.value"
              @click="pickMonth(m.value)"
            >
              {{ m.label }}
            </button>
            <div class="spacer" aria-hidden="true" />
          </div>
          <div ref="dayWheelRef" class="wheel">
            <div class="spacer" aria-hidden="true" />
            <button
              v-for="d in dayOptions"
              :key="d"
              type="button"
              class="item"
              :class="{ active: draft.day === d }"
              :data-value="d"
              @click="pickDay(d)"
            >
              {{ dayLabel(d) }}
            </button>
            <div class="spacer" aria-hidden="true" />
          </div>
        </div>
      </div>
    </BottomSheet>
  </div>
</template>

<script lang="ts">
import { computed, defineComponent, nextTick, onBeforeUnmount, reactive, ref, watch, type PropType } from 'vue';
import BottomSheet from './BottomSheet.vue';
import SheetField from './SheetField.vue';
import { bindWheelSnap, scrollAllPickerWheels, scrollPickerItemToCenter, snapWheelToNearest } from './scrollPicker';
import {
  clampLunarDay,
  dayLabel,
  formatLunarText,
  listLunarMonths,
  lunarToSolar,
  solarToLunar,
  type SolarDateFormat,
} from '@/utils/calendarConvert';

const todayLunar = () => {
  const now = new Date();
  const solar = `${now.getFullYear()}-${now.getMonth() + 1}-${now.getDate()}`;
  return solarToLunar(solar) ?? { year: now.getFullYear(), month: 1, day: 1 };
};

export default defineComponent({
  name: 'SheetLunarDatePicker',
  components: { BottomSheet, SheetField },
  props: {
    /** 公历 YYYY-M-D，与排盘真源一致 */
    modelValue: { type: String, default: '' },
    title: { type: String, default: '' },
    placeholder: { type: String, default: '請選擇農曆日期' },
    format: { type: String as PropType<SolarDateFormat>, default: 'loose' },
    minYear: { type: Number, default: 1900 },
    maxYear: { type: Number, default: () => new Date().getFullYear() },
    yearUnit: { type: String, default: '年' },
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
    const draft = reactive(todayLunar());
    const cleanups: Array<() => void> = [];

    const displayText = computed(() => {
      const lunar = props.modelValue ? solarToLunar(props.modelValue) : null;
      return lunar ? formatLunarText(lunar) : '';
    });

    const years = computed(() => {
      const list: number[] = [];
      for (let y = props.maxYear; y >= props.minYear; y -= 1) list.push(y);
      return list;
    });

    const monthOptions = computed(() => listLunarMonths(draft.year));
    const dayOptions = computed(() => {
      const count = monthOptions.value.find((m) => m.value === draft.month)?.dayCount ?? 30;
      return Array.from({ length: count }, (_, i) => i + 1);
    });

    watch(monthOptions, (opts) => {
      if (!opts.some((m) => m.value === draft.month)) {
        draft.month = opts[0]?.value ?? 1;
      }
    });

    watch(dayOptions, (days) => {
      if (draft.day > days.length) draft.day = days.length;
    });

    const unbindSnaps = () => {
      while (cleanups.length) cleanups.pop()?.();
    };

    const bindSnaps = () => {
      unbindSnaps();
      const pairs: Array<[HTMLElement | null, (n: number) => void]> = [
        [yearWheelRef.value, (n) => { draft.year = n; }],
        [monthWheelRef.value, (n) => { draft.month = n; }],
        [dayWheelRef.value, (n) => { draft.day = n; }],
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
      () => [draft.year, draft.month] as const,
      async () => {
        if (!open.value) return;
        await nextTick();
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
      draft.year = y;
      scrollToValue(yearWheelRef.value, y);
    };
    const pickMonth = (m: number) => {
      draft.month = m;
      scrollToValue(monthWheelRef.value, m);
    };
    const pickDay = (d: number) => {
      draft.day = d;
      scrollToValue(dayWheelRef.value, d);
    };

    const handleOpen = () => {
      const lunar = props.modelValue ? solarToLunar(props.modelValue) : null;
      const base = lunar ?? todayLunar();
      draft.year = Math.min(Math.max(base.year, props.minYear), props.maxYear);
      const months = listLunarMonths(draft.year);
      draft.month = months.some((m) => m.value === base.month) ? base.month : (months[0]?.value ?? 1);
      draft.day = clampLunarDay(draft.year, draft.month, base.day);
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
      applySnap(yearWheelRef.value, (n) => { draft.year = n; });
      applySnap(monthWheelRef.value, (n) => { draft.month = n; });
      applySnap(dayWheelRef.value, (n) => { draft.day = n; });
      draft.day = clampLunarDay(draft.year, draft.month, draft.day);
      const solar = lunarToSolar(
        { year: draft.year, month: draft.month, day: draft.day },
        props.format,
      );
      if (!solar) return;
      emit('update:modelValue', solar);
      emit('change', solar);
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
      monthOptions,
      dayOptions,
      displayText,
      dayLabel,
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
.sheet-lunar-date {
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
  padding: 0 2px;
  font-family: inherit;
  font-size: 15px;
  letter-spacing: 0.04em;
  color: var(--zw-muted);
  text-align: center;
  line-height: 44px;
  overflow: hidden;
  white-space: nowrap;
  text-overflow: ellipsis;
  scroll-snap-align: center;
  scroll-snap-stop: always;
}
.item.active {
  color: var(--zw-primary);
  font-weight: 700;
}
</style>
