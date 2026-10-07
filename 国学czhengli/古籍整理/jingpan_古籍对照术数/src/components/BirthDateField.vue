<template>
  <div class="birth-date-field">
    <div class="cal-switch" role="group" :aria-label="display('曆法', false)">
      <button
        type="button"
        class="cal-btn"
        :class="{ active: calendarType === 'solar' }"
        @click="setCalendarType('solar')"
      >
        {{ display('公曆', false) }}
      </button>
      <button
        type="button"
        class="cal-btn"
        :class="{ active: calendarType === 'lunar' }"
        @click="setCalendarType('lunar')"
      >
        {{ display('農曆', false) }}
      </button>
    </div>

    <template v-if="calendarType === 'solar'">
      <SheetDatePicker
        v-if="isMobile"
        :model-value="modelValue"
        :title="display('公曆日期', false)"
        :placeholder="display('選擇公曆日期', false)"
        :cancel-text="display('取消', false)"
        :confirm-text="display('確定', false)"
        :year-unit="display('年', false)"
        :month-unit="display('月', false)"
        :day-unit="display('日', false)"
        :format="format"
        @update:model-value="emitValue"
        @change="emitChange"
      />
      <input
        v-else-if="format === 'padded'"
        class="native-date"
        type="date"
        :value="modelValue"
        @input="onNativeDate"
      />
      <el-date-picker
        v-else
        :model-value="modelValue || undefined"
        type="date"
        value-format="YYYY-M-D"
        clearable
        :placeholder="display('選擇公曆日期', false)"
        style="width: 100%"
        @update:model-value="onElDate"
      />
    </template>

    <template v-else>
      <SheetLunarDatePicker
        v-if="isMobile"
        :model-value="modelValue"
        :title="display('農曆日期', false)"
        :placeholder="display('選擇農曆日期', false)"
        :cancel-text="display('取消', false)"
        :confirm-text="display('確定', false)"
        :year-unit="display('年', false)"
        :format="format"
        @update:model-value="emitValue"
        @change="emitChange"
      />
      <div v-else class="lunar-pc">
        <el-select
          v-model="lunarDraft.year"
          class="lunar-pc__year"
          :placeholder="display('年', false)"
          @change="onLunarDraftChange"
        >
          <el-option v-for="y in lunarYears" :key="y" :label="`${y}${display('年', false)}`" :value="y" />
        </el-select>
        <el-select
          v-model="lunarDraft.month"
          class="lunar-pc__month"
          :placeholder="display('月', false)"
          @change="onLunarDraftChange"
        >
          <el-option
            v-for="m in lunarMonthOptions"
            :key="m.value"
            :label="display(m.label, false)"
            :value="m.value"
          />
        </el-select>
        <el-select
          v-model="lunarDraft.day"
          class="lunar-pc__day"
          :placeholder="display('日', false)"
          @change="onLunarDraftChange"
        >
          <el-option
            v-for="d in lunarDayOptions"
            :key="d"
            :label="display(dayLabel(d), false)"
            :value="d"
          />
        </el-select>
      </div>
    </template>

    <p v-if="counterpartHint" class="counterpart">{{ counterpartHint }}</p>
  </div>
</template>

<script lang="ts">
import { computed, defineComponent, nextTick, reactive, ref, watch, type PropType } from 'vue';
import { ElMessage } from 'element-plus';
import { useDisplayText } from '@/composables/useDisplayText';
import { useDevice } from '@/composables/useDevice';
import SheetDatePicker from '@/components/sheet/SheetDatePicker.vue';
import SheetLunarDatePicker from '@/components/sheet/SheetLunarDatePicker.vue';
import {
  type CalendarType,
  type SolarDateFormat,
  clampLunarDay,
  dayLabel,
  formatLunarTextFromSolar,
  listLunarMonths,
  lunarToSolar,
  solarToLunar,
} from '@/utils/calendarConvert';

export default defineComponent({
  name: 'BirthDateField',
  components: { SheetDatePicker, SheetLunarDatePicker },
  props: {
    modelValue: { type: String, default: '' },
    format: { type: String as PropType<SolarDateFormat>, default: 'padded' },
  },
  emits: {
    'update:modelValue': (_v: string) => true,
    change: (_v: string) => true,
  },
  setup(props, { emit }) {
    const { display } = useDisplayText();
    const { isMobile } = useDevice();
    const maxLunarYear = new Date().getFullYear();
    const minLunarYear = 1900;
    const calendarType = ref<CalendarType>('solar');
    const lunarDraft = reactive({ year: maxLunarYear, month: 1, day: 1 });
    let syncingLunar = false;

    const syncLunarDraftFromSolar = () => {
      const lunar = props.modelValue ? solarToLunar(props.modelValue) : null;
      if (!lunar) return;
      syncingLunar = true;
      lunarDraft.year = Math.min(Math.max(lunar.year, minLunarYear), maxLunarYear);
      const months = listLunarMonths(lunarDraft.year);
      lunarDraft.month = months.some((m) => m.value === lunar.month)
        ? lunar.month
        : (months[0]?.value ?? 1);
      lunarDraft.day = clampLunarDay(lunarDraft.year, lunarDraft.month, lunar.day);
      void nextTick(() => {
        syncingLunar = false;
      });
    };

    if (props.modelValue) syncLunarDraftFromSolar();

    const lunarYears = computed(() => {
      const list: number[] = [];
      for (let y = maxLunarYear; y >= minLunarYear; y -= 1) list.push(y);
      return list;
    });
    const lunarMonthOptions = computed(() => listLunarMonths(lunarDraft.year));
    const lunarDayOptions = computed(() => {
      const count =
        lunarMonthOptions.value.find((m) => m.value === lunarDraft.month)?.dayCount ?? 30;
      return Array.from({ length: count }, (_, i) => i + 1);
    });

    const counterpartHint = computed(() => {
      if (!props.modelValue) return '';
      if (calendarType.value === 'solar') {
        const text = formatLunarTextFromSolar(props.modelValue);
        return text ? display(`對應農曆：${text}`, false) : '';
      }
      return display(`對應公曆：${props.modelValue}`, false);
    });

    watch(
      () => props.modelValue,
      () => {
        if (calendarType.value === 'lunar') syncLunarDraftFromSolar();
      },
    );

    watch(lunarMonthOptions, (opts) => {
      if (!opts.some((m) => m.value === lunarDraft.month)) {
        lunarDraft.month = opts[0]?.value ?? 1;
      }
    });

    watch(lunarDayOptions, (days) => {
      if (lunarDraft.day > days.length) lunarDraft.day = days.length;
    });

    const emitValue = (val: string) => {
      emit('update:modelValue', val);
    };
    const emitChange = (val: string) => {
      emit('change', val);
    };

    const setCalendarType = (type: CalendarType) => {
      if (calendarType.value === type) return;
      calendarType.value = type;
      if (type === 'lunar' && props.modelValue) {
        const lunar = solarToLunar(props.modelValue);
        if (!lunar) {
          ElMessage.warning(display('無法換算農曆，請重新選擇日期', false));
          emitValue('');
          emitChange('');
        } else {
          syncLunarDraftFromSolar();
        }
      }
    };

    const onLunarDraftChange = () => {
      if (syncingLunar) return;
      const months = listLunarMonths(lunarDraft.year);
      if (!months.some((m) => m.value === lunarDraft.month)) {
        lunarDraft.month = months[0]?.value ?? 1;
      }
      lunarDraft.day = clampLunarDay(lunarDraft.year, lunarDraft.month, lunarDraft.day);
      const solar = lunarToSolar(
        { year: lunarDraft.year, month: lunarDraft.month, day: lunarDraft.day },
        props.format,
      );
      if (!solar) {
        ElMessage.warning(display('農曆日期無效，請重新選擇', false));
        return;
      }
      emitValue(solar);
      emitChange(solar);
    };

    const onNativeDate = (e: Event) => {
      const val = (e.target as HTMLInputElement).value || '';
      emitValue(val);
      emitChange(val);
    };

    const onElDate = (val: string | null) => {
      const next = val || '';
      emitValue(next);
      emitChange(next);
    };

    return {
      display,
      isMobile,
      calendarType,
      lunarDraft,
      lunarYears,
      lunarMonthOptions,
      lunarDayOptions,
      counterpartHint,
      dayLabel,
      setCalendarType,
      onLunarDraftChange,
      onNativeDate,
      onElDate,
      emitValue,
      emitChange,
    };
  },
});
</script>

<style scoped>
.birth-date-field {
  display: flex;
  flex-direction: column;
  gap: 6px;
  width: 100%;
  min-width: 0;
}
.cal-switch {
  display: inline-flex;
  align-self: flex-start;
  border: 1px solid var(--zw-line);
  border-radius: 8px;
  overflow: hidden;
  background: color-mix(in srgb, var(--zw-paper) 88%, var(--zw-gold));
}
.cal-btn {
  margin: 0;
  border: 0;
  padding: 6px 14px;
  background: transparent;
  color: var(--zw-muted);
  font-family: inherit;
  font-size: 13px;
  letter-spacing: 0.12em;
  cursor: pointer;
  line-height: 1.3;
}
.cal-btn.active {
  background: var(--zw-primary);
  color: var(--zw-paper);
}
.native-date {
  width: 100%;
  box-sizing: border-box;
  border: 1px solid var(--zw-line);
  background: var(--zw-paper);
  color: var(--zw-ink);
  padding: 8px 10px;
  border-radius: 8px;
  font-family: inherit;
}
.lunar-pc {
  display: grid;
  grid-template-columns: 1.1fr 1fr 1fr;
  gap: 8px;
  width: 100%;
}
.lunar-pc :deep(.el-select) {
  width: 100%;
}
.counterpart {
  margin: 0;
  font-size: 12px;
  line-height: 1.55;
  letter-spacing: 0.06em;
  color: var(--zw-muted);
}
@media (max-width: 767.98px) {
  .cal-switch {
    display: flex;
    width: 100%;
    align-self: stretch;
  }
  .cal-btn {
    flex: 1;
    min-height: 34px;
  }
}
</style>
