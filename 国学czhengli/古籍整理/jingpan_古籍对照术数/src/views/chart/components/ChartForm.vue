<template>
  <el-form
    ref="formRef"
    :model="form"
    :rules="rules"
    :label-width="isMobile ? 'auto' : '92px'"
    :label-position="isMobile ? 'top' : 'right'"
    class="chart-form"
    :class="{ 'is-h5-form': isMobile }"
    @submit.prevent
  >
    <el-form-item :label="display('出生日期', false)" prop="solarDate" required>
      <div class="cal-switch" role="group" :aria-label="display('曆法', false)">
        <button
          type="button"
          class="cal-btn"
          :class="{ active: form.calendarType === 'solar' }"
          @click="setCalendarType('solar')"
        >
          {{ display('公曆', false) }}
        </button>
        <button
          type="button"
          class="cal-btn"
          :class="{ active: form.calendarType === 'lunar' }"
          @click="setCalendarType('lunar')"
        >
          {{ display('農曆', false) }}
        </button>
      </div>

      <template v-if="form.calendarType === 'solar'">
        <SheetDatePicker
          v-if="isMobile"
          v-model="form.solarDate"
          :title="display('公曆生辰', false)"
          :placeholder="display('選擇公曆日期', false)"
          :cancel-text="display('取消', false)"
          :confirm-text="display('確定', false)"
          :year-unit="display('年', false)"
          :month-unit="display('月', false)"
          :day-unit="display('日', false)"
          format="loose"
        />
        <el-date-picker
          v-else
          :model-value="form.solarDate || undefined"
          type="date"
          value-format="YYYY-M-D"
          clearable
          :placeholder="display('選擇公曆日期', false)"
          style="width: 100%"
          @update:model-value="onSolarDate"
        />
      </template>

      <template v-else>
        <SheetLunarDatePicker
          v-if="isMobile"
          v-model="form.solarDate"
          :title="display('農曆生辰', false)"
          :placeholder="display('選擇農曆日期', false)"
          :cancel-text="display('取消', false)"
          :confirm-text="display('確定', false)"
          :year-unit="display('年', false)"
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

      <p v-if="counterpartHint" class="coord-hint">{{ counterpartHint }}</p>
    </el-form-item>

    <el-form-item :label="display('真太陽時', false)">
      <el-switch v-model="form.useTrueSolar" />
      <p class="coord-hint">
        {{
          display(
            '關閉時按所選時辰排盤。開啟後用鐘錶時刻與出生地經度校正均時差，再換成時辰；須填具體出生時間與出生地。',
            false,
          )
        }}
      </p>
    </el-form-item>

    <el-form-item v-if="form.useTrueSolar" :label="display('鐘錶時刻', false)" prop="clock" required>
      <SheetTimePicker
        v-if="isMobile"
        v-model="form.clock"
        :title="display('鐘錶時刻', false)"
        :placeholder="display('具體出生時間', false)"
        :cancel-text="display('取消', false)"
        :confirm-text="display('確定', false)"
        :hour-unit="display('時', false)"
        :minute-unit="display('分', false)"
      />
      <el-time-picker
        v-else
        :model-value="form.clock || undefined"
        format="HH:mm"
        value-format="HH:mm"
        clearable
        :placeholder="display('具體出生時間', false)"
        style="width: 100%"
        @update:model-value="onClock"
      />
      <p v-if="clockShichenHint" class="coord-hint">{{ clockShichenHint }}</p>
      <p v-if="trueShichenHint" class="coord-hint">{{ trueShichenHint }}</p>
    </el-form-item>

    <el-form-item v-if="form.useTrueSolar" :label="display('出生地', false)" prop="areaPath" required>
      <SheetCascader
        v-if="isMobile"
        v-model="form.areaPath"
        :options="placeOptions"
        :title="display('出生地', false)"
        :placeholder="display('省 / 市 / 區', false)"
        :cancel-text="display('取消', false)"
        :confirm-text="display('確定', false)"
        @change="handlePlace"
      />
      <el-cascader
        v-else
        v-model="form.areaPath"
        class="w-full"
        filterable
        clearable
        :options="placeOptions"
        :props="cascaderProps"
        separator=" / "
        :placeholder="display('省 / 市 / 區', false)"
        @change="handlePlace"
      />
      <p v-if="coordHint" class="coord-hint">{{ coordHint }}</p>
    </el-form-item>

    <el-form-item
      v-if="!form.useTrueSolar"
      :label="display('出生時辰', false)"
      prop="timeIndex"
      required
    >
      <SheetSelect
        v-if="isMobile"
        v-model="form.timeIndex"
        :options="timeOptions"
        :title="display('出生時辰', false)"
        :placeholder="display('請選擇時辰', false)"
        :cancel-text="display('取消', false)"
      />
      <el-select
        v-else
        v-model="form.timeIndex"
        clearable
        class="w-full"
        :placeholder="display('請選擇時辰', false)"
      >
        <el-option
          v-for="(label, idx) in TIME_INDEX_LABELS"
          :key="idx"
          :label="display(label, false)"
          :value="idx"
        />
      </el-select>
    </el-form-item>

    <el-form-item :label="display('性別', false)" prop="gender" required>
      <el-radio-group v-model="form.gender">
        <el-radio value="男">{{ display('男', false) }}</el-radio>
        <el-radio value="女">{{ display('女', false) }}</el-radio>
      </el-radio-group>
    </el-form-item>
    <div class="form-actions">
      <el-button type="primary" :loading="loading" @click="handleSubmit">{{ display('生成命盤', false) }}</el-button>
      <el-button @click="handleReset">{{ display('重置表單', false) }}</el-button>
    </div>
  </el-form>
</template>

<script lang="ts">
import { computed, defineComponent, nextTick, onMounted, reactive, ref, watch, type PropType } from 'vue';
import { ElMessage, type CascaderProps, type FormInstance, type FormRules } from 'element-plus';
import { TIME_INDEX_LABELS, clockToTimeIndex, computeTrueSolar, timeIndexToClock } from '@/utils/trueSolar';
import {
  type CalendarType,
  clampLunarDay,
  dayLabel,
  formatLunarTextFromSolar,
  listLunarMonths,
  lunarToSolar,
  solarToLunar,
} from '@/utils/calendarConvert';
import {
  BIRTHPLACE_TREE,
  DEFAULT_BIRTHPLACE_PATH,
  findPlaceByPath,
  getDefaultBirthplace,
  type BirthplaceNode,
} from '@/data/birthplaces';
import { useDisplayText } from '@/composables/useDisplayText';
import { useDevice } from '@/composables/useDevice';
import SheetSelect from '@/components/sheet/SheetSelect.vue';
import SheetCascader, { type SheetCascaderOption } from '@/components/sheet/SheetCascader.vue';
import SheetDatePicker from '@/components/sheet/SheetDatePicker.vue';
import SheetLunarDatePicker from '@/components/sheet/SheetLunarDatePicker.vue';
import SheetTimePicker from '@/components/sheet/SheetTimePicker.vue';

export interface ChartFormValue {
  solarDate: string;
  calendarType: CalendarType;
  clock: string;
  timeIndex: number | null;
  gender: '男' | '女' | '';
  city: string;
  areaPath: string[];
  lng: number;
  lat: number;
  useTrueSolar: boolean;
}

export default defineComponent({
  name: 'ChartForm',
  components: {
    SheetSelect,
    SheetCascader,
    SheetDatePicker,
    SheetLunarDatePicker,
    SheetTimePicker,
  },
  props: {
    loading: { type: Boolean, default: false },
    seed: { type: Object as PropType<ChartFormValue | null>, default: null },
  },
  emits: {
    submit: (_val: ChartFormValue) => true,
    reset: () => true,
  },
  setup(props, { emit }) {
    const { display } = useDisplayText();
    const { isMobile } = useDevice();
    const formRef = ref<FormInstance>();
    const maxLunarYear = new Date().getFullYear();
    const minLunarYear = 1900;
    let syncingLunar = false;

    const defaults = (): ChartFormValue => {
      const place = getDefaultBirthplace();
      const now = new Date();
      const h = now.getHours();
      const m = now.getMinutes();
      const clock = `${String(h).padStart(2, '0')}:${String(m).padStart(2, '0')}`;
      return {
        solarDate: `${now.getFullYear()}-${now.getMonth() + 1}-${now.getDate()}`,
        calendarType: 'solar',
        clock,
        timeIndex: clockToTimeIndex(h, m),
        gender: '男',
        city: place.label,
        areaPath: [...DEFAULT_BIRTHPLACE_PATH],
        lng: place.lng,
        lat: place.lat,
        useTrueSolar: false,
      };
    };

    const empty = (): ChartFormValue => ({
      solarDate: '',
      calendarType: 'solar',
      clock: '',
      timeIndex: null,
      gender: '男',
      city: '',
      areaPath: [],
      lng: 0,
      lat: 0,
      useTrueSolar: false,
    });

    const form = reactive<ChartFormValue>(defaults());
    const lunarDraft = reactive({ year: maxLunarYear, month: 1, day: 1 });

    const syncLunarDraftFromSolar = () => {
      const lunar = form.solarDate ? solarToLunar(form.solarDate) : null;
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

    syncLunarDraftFromSolar();

    const mapPlaceTree = (nodes: BirthplaceNode[]): SheetCascaderOption[] =>
      nodes.map((n) => ({
        value: n.name,
        label: display(n.name, false),
        children: n.children ? mapPlaceTree(n.children) : undefined,
      }));

    const placeOptions = computed(() => mapPlaceTree(BIRTHPLACE_TREE));
    const timeOptions = computed(() =>
      TIME_INDEX_LABELS.map((label, idx) => ({
        label: display(label, false),
        value: idx,
      })),
    );
    const cascaderProps: CascaderProps = {
      expandTrigger: 'click',
    };

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
      if (!form.solarDate) return '';
      if (form.calendarType === 'solar') {
        const text = formatLunarTextFromSolar(form.solarDate);
        return text ? display(`對應農曆：${text}`, false) : '';
      }
      return display(`對應公曆：${form.solarDate}`, false);
    });

    const rules = computed<FormRules>(() => {
      const next: FormRules = {
        solarDate: [
          { required: true, message: display('請選擇出生日期', false), trigger: 'change' },
        ],
        gender: [{ required: true, message: display('請選擇性別', false), trigger: 'change' }],
      };
      if (form.useTrueSolar) {
        next.clock = [
          { required: true, message: display('請填寫鐘錶時刻', false), trigger: 'change' },
        ];
        next.areaPath = [
          {
            validator: (_rule, value, callback) => {
              if (!Array.isArray(value) || !value.length) {
                callback(new Error(display('請選擇出生地', false)));
              } else {
                callback();
              }
            },
            trigger: 'change',
          },
        ];
      } else {
        next.timeIndex = [
          {
            validator: (_rule, value, callback) => {
              if (value === null || value === undefined || value === '') {
                callback(new Error(display('請選擇出生時辰', false)));
              } else {
                callback();
              }
            },
            trigger: 'change',
          },
        ];
      }
      return next;
    });

    const coordHint = computed(() => {
      if (!form.lng || !form.lat) return '';
      return display(`東經 ${form.lng.toFixed(2)}°　北緯 ${form.lat.toFixed(2)}°`, false);
    });

    const clockShichenHint = computed(() => {
      if (!form.useTrueSolar || !form.clock) return '';
      const [h, m] = form.clock.split(':').map(Number);
      const idx = clockToTimeIndex(h, m);
      return display(`對應時辰：${TIME_INDEX_LABELS[idx]}`, false);
    });

    const trueShichenHint = computed(() => {
      if (!form.useTrueSolar || !form.clock || !form.lng || !form.solarDate) return '';
      const [h, m] = form.clock.split(':').map(Number);
      const ts = computeTrueSolar(form.solarDate, h, m, form.lng);
      const clockIdx = clockToTimeIndex(h, m);
      if (ts.timeIndex === clockIdx) {
        return display(`校正後仍為：${TIME_INDEX_LABELS[ts.timeIndex]}`, false);
      }
      return display(`校正後時辰：${TIME_INDEX_LABELS[ts.timeIndex]}（真太陽時 ${ts.trueClock}）`, false);
    });

    watch(
      () => form.clock,
      (val) => {
        if (!val) return;
        const [h, m] = val.split(':').map(Number);
        const next = clockToTimeIndex(h, m);
        if (form.timeIndex !== next) form.timeIndex = next;
      },
    );

    watch(
      () => form.timeIndex,
      (idx) => {
        if (idx === null) return;
        if (form.clock) {
          const [h, m] = form.clock.split(':').map(Number);
          if (clockToTimeIndex(h, m) === idx) return;
        }
        form.clock = timeIndexToClock(idx);
      },
    );

    watch(
      () => form.useTrueSolar,
      () => {
        void nextTick(() => {
          formRef.value?.clearValidate(['clock', 'timeIndex', 'areaPath']);
        });
      },
    );

    watch(
      () => form.solarDate,
      () => {
        if (form.calendarType === 'lunar') syncLunarDraftFromSolar();
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

    const setCalendarType = (type: CalendarType) => {
      if (form.calendarType === type) return;
      form.calendarType = type;
      if (type === 'lunar' && form.solarDate) {
        const lunar = solarToLunar(form.solarDate);
        if (!lunar) {
          ElMessage.warning(display('無法換算農曆，請重新選擇日期', false));
          form.solarDate = '';
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
      const solar = lunarToSolar({
        year: lunarDraft.year,
        month: lunarDraft.month,
        day: lunarDraft.day,
      });
      if (!solar) {
        ElMessage.warning(display('農曆日期無效，請重新選擇', false));
        return;
      }
      form.solarDate = solar;
    };

    const applyPlace = (path: string[]) => {
      const hit = findPlaceByPath(path);
      if (!hit) return;
      form.areaPath = [...hit.path];
      form.city = hit.label;
      form.lng = hit.lng;
      form.lat = hit.lat;
    };

    const clearPlace = () => {
      form.areaPath = [];
      form.city = '';
      form.lng = 0;
      form.lat = 0;
    };

    const handlePlace = (path: string[] | null) => {
      if (path?.length) applyPlace(path);
      else clearPlace();
    };

    const onSolarDate = (val: string | null) => {
      form.solarDate = val || '';
    };

    const onClock = (val: string | null) => {
      form.clock = val || '';
    };

    const handleSubmit = async () => {
      if (!formRef.value) return;
      try {
        await formRef.value.validate();
      } catch {
        ElMessage.warning(display('請完善未填寫的內容', false));
        return;
      }
      if (form.timeIndex === null || !form.gender) return;
      emit('submit', { ...form, areaPath: [...form.areaPath] });
    };

    const handleReset = () => {
      Object.assign(form, empty());
      form.areaPath = [];
      void nextTick(() => {
        formRef.value?.clearValidate();
      });
      emit('reset');
    };

    const applySeed = (seed: ChartFormValue) => {
      form.solarDate = seed.solarDate;
      form.calendarType = seed.calendarType === 'lunar' ? 'lunar' : 'solar';
      form.clock = seed.clock;
      form.timeIndex = seed.timeIndex;
      form.gender = seed.gender;
      form.city = seed.city;
      form.areaPath = [...seed.areaPath];
      form.lng = seed.lng;
      form.lat = seed.lat;
      form.useTrueSolar = seed.useTrueSolar;
      if (form.calendarType === 'lunar') syncLunarDraftFromSolar();
    };

    onMounted(() => {
      if (props.seed) applySeed(props.seed);
    });

    return {
      formRef,
      form,
      rules,
      display,
      isMobile,
      TIME_INDEX_LABELS,
      timeOptions,
      placeOptions,
      cascaderProps,
      coordHint,
      counterpartHint,
      clockShichenHint,
      trueShichenHint,
      lunarDraft,
      lunarYears,
      lunarMonthOptions,
      lunarDayOptions,
      dayLabel,
      setCalendarType,
      onLunarDraftChange,
      handlePlace,
      onSolarDate,
      onClock,
      handleSubmit,
      handleReset,
    };
  },
});
</script>

<style scoped>
.chart-form :deep(.el-cascader),
.chart-form :deep(.el-select),
.chart-form :deep(.el-date-editor) {
  width: 100%;
  max-width: 100%;
}
.cal-switch {
  display: inline-flex;
  margin-bottom: 8px;
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
.lunar-pc {
  display: grid;
  grid-template-columns: 1.1fr 1fr 1fr;
  gap: 8px;
  width: 100%;
}
.form-actions {
  display: flex;
  gap: 8px;
}
.coord-hint {
  margin: 6px 0 0;
  font-size: 12px;
  line-height: 1.55;
  letter-spacing: 0.06em;
  color: var(--zw-muted);
}
.chart-form.is-h5-form :deep(.el-form-item) {
  margin-bottom: 12px;
}
.chart-form.is-h5-form :deep(.el-form-item__label) {
  margin-bottom: 0;
  padding: 0 0 4px;
  line-height: 1.3;
  height: auto;
  font-size: 0.92em;
  letter-spacing: 0.06em;
  color: var(--zw-muted);
  justify-content: flex-start;
}
.chart-form.is-h5-form :deep(.el-form-item__content) {
  line-height: 1.4;
  min-width: 0;
}
.chart-form.is-h5-form .coord-hint {
  margin-top: 6px;
  font-size: 12px;
  line-height: 1.5;
}
.chart-form.is-h5-form .form-actions {
  gap: 10px;
  margin-top: 2px;
}
.chart-form.is-h5-form .form-actions .el-button {
  flex: 1;
  min-height: 38px;
}
.chart-form.is-h5-form .cal-switch {
  display: flex;
  width: 100%;
}
.chart-form.is-h5-form .cal-btn {
  flex: 1;
  min-height: 34px;
}
</style>
