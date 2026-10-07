<template>
  <form class="naming-form" @submit.prevent="handleSubmit">
    <label class="date-label">
      {{ display('出生日期', false) }}
      <BirthDateField v-model="iso" format="padded" />
    </label>

    <label class="span-full">
      <span class="row-label">
        {{ display('真太陽時', false) }}
        <el-switch v-model="useTrueSolar" />
      </span>
      <p class="hint">
        {{
          display(
            '關閉時按所選時辰起名。開啟後用鐘錶時刻與出生地經度校正均時差，再換算時辰與日柱；須填具體出生時間與出生地。',
            false,
          )
        }}
      </p>
    </label>

    <template v-if="useTrueSolar">
      <label class="span-full">
        {{ display('鐘錶時刻', false) }}
        <SheetTimePicker
          v-if="isMobile"
          v-model="clock"
          :title="display('鐘錶時刻', false)"
          :placeholder="display('具體出生時間', false)"
          :cancel-text="display('取消', false)"
          :confirm-text="display('確定', false)"
          :hour-unit="display('時', false)"
          :minute-unit="display('分', false)"
        />
        <input v-else v-model="clock" type="time" required />
        <p v-if="clockShichenHint" class="hint">{{ clockShichenHint }}</p>
        <p v-if="trueShichenHint" class="hint">{{ trueShichenHint }}</p>
      </label>
      <label class="span-full">
        {{ display('出生地', false) }}
        <SheetCascader
          v-if="isMobile"
          v-model="areaPath"
          :options="placeOptions"
          :title="display('出生地', false)"
          :placeholder="display('省 / 市 / 區', false)"
          :cancel-text="display('取消', false)"
          :confirm-text="display('確定', false)"
          @change="handlePlace"
        />
        <el-cascader
          v-else
          v-model="areaPath"
          class="place-cascader"
          filterable
          clearable
          :options="placeOptions"
          :props="cascaderProps"
          separator=" / "
          :placeholder="display('省 / 市 / 區', false)"
          @change="handlePlace"
        />
        <p v-if="coordHint" class="hint">{{ coordHint }}</p>
      </label>
    </template>

    <label v-else class="span-full">
      {{ display('出生時辰', false) }}
      <SheetSelect
        v-if="isMobile"
        v-model="timeIndex"
        :options="timeOptions"
        :title="display('出生時辰', false)"
        :cancel-text="display('取消', false)"
      />
      <select v-else v-model.number="timeIndex">
        <option v-for="(label, idx) in timeLabels" :key="idx" :value="idx">
          {{ display(label, false) }}
        </option>
      </select>
    </label>
    <label class="span-full">
      {{ display('姓氏（可選）', false) }}
      <input v-model="surname" type="text" maxlength="8" :placeholder="display('如：陳', false)" />
    </label>
    <label class="span-full">
      {{ display('性別（僅展示，不參與用字）', false) }}
      <SheetSelect
        v-if="isMobile"
        v-model="gender"
        :options="genderOptions"
        :title="display('性別', false)"
        :cancel-text="display('取消', false)"
      />
      <select v-else v-model="gender">
        <option value="">{{ display('未填', false) }}</option>
        <option value="男">{{ display('男', false) }}</option>
        <option value="女">{{ display('女', false) }}</option>
      </select>
    </label>
    <button type="submit" class="submit">{{ display('起名', false) }}</button>
  </form>
</template>

<script lang="ts">
import { computed, defineComponent, reactive, toRefs, watch } from 'vue';
import { ElMessage, type CascaderProps } from 'element-plus';
import { useDisplayText } from '@/composables/useDisplayText';
import { useDevice } from '@/composables/useDevice';
import {
  clockToTimeIndex,
  computeTrueSolar,
  TIME_INDEX_LABELS,
  timeIndexToClock,
} from '@/utils/trueSolar';
import { toIsoDate } from '@/utils/almanac';
import {
  BIRTHPLACE_TREE,
  findPlaceByPath,
  type BirthplaceNode,
} from '@/data/birthplaces';
import SheetSelect from '@/components/sheet/SheetSelect.vue';
import SheetTimePicker from '@/components/sheet/SheetTimePicker.vue';
import SheetCascader, { type SheetCascaderOption } from '@/components/sheet/SheetCascader.vue';
import BirthDateField from '@/components/BirthDateField.vue';

export default defineComponent({
  name: 'NamingForm',
  components: { SheetSelect, SheetTimePicker, SheetCascader, BirthDateField },
  emits: {
    submit: (_payload: {
      iso: string;
      timeIndex: number;
      surname: string;
      gender: string;
      trueSolarNote: string;
    }) => true,
  },
  setup(_props, { emit }) {
    const { display } = useDisplayText();
    const { isMobile } = useDevice();
    const now = new Date();
    const h = now.getHours();
    const m = now.getMinutes();
    const _data = reactive({
      iso: toIsoDate(now),
      timeIndex: clockToTimeIndex(h, m),
      clock: `${String(h).padStart(2, '0')}:${String(m).padStart(2, '0')}`,
      useTrueSolar: false,
      areaPath: [] as string[],
      lng: 0,
      lat: 0,
      surname: '',
      gender: '',
    });

    const mapPlaceTree = (nodes: BirthplaceNode[]): SheetCascaderOption[] =>
      nodes.map((n) => ({
        value: n.name,
        label: display(n.name, false),
        children: n.children ? mapPlaceTree(n.children) : undefined,
      }));

    const placeOptions = computed(() => mapPlaceTree(BIRTHPLACE_TREE));
    const cascaderProps: CascaderProps = { expandTrigger: 'click' };
    const timeOptions = computed(() =>
      TIME_INDEX_LABELS.map((label, idx) => ({
        label: display(label, false),
        value: idx,
      })),
    );
    const genderOptions = computed(() => [
      { label: display('未填', false), value: '' },
      { label: display('男', false), value: '男' },
      { label: display('女', false), value: '女' },
    ]);
    const coordHint = computed(() => {
      if (!_data.lng || !_data.lat) return '';
      return display(`東經 ${_data.lng.toFixed(2)}°　北緯 ${_data.lat.toFixed(2)}°`, false);
    });

    const clockShichenHint = computed(() => {
      if (!_data.clock) return '';
      const [hh, mm] = _data.clock.split(':').map(Number);
      const idx = clockToTimeIndex(hh, mm);
      return display(`對應時辰：${TIME_INDEX_LABELS[idx]}`, false);
    });

    const trueShichenHint = computed(() => {
      if (!_data.clock || !_data.lng || !_data.iso) return '';
      const [hh, mm] = _data.clock.split(':').map(Number);
      const ts = computeTrueSolar(_data.iso, hh, mm, _data.lng);
      const clockIdx = clockToTimeIndex(hh, mm);
      if (ts.timeIndex === clockIdx) {
        return display(`校正後仍為：${TIME_INDEX_LABELS[ts.timeIndex]}`, false);
      }
      return display(`校正後時辰：${TIME_INDEX_LABELS[ts.timeIndex]}（真太陽時 ${ts.trueClock}）`, false);
    });

    watch(
      () => _data.clock,
      (val) => {
        if (!val) return;
        const [hh, mm] = val.split(':').map(Number);
        const next = clockToTimeIndex(hh, mm);
        if (_data.timeIndex !== next) _data.timeIndex = next;
      },
    );

    watch(
      () => _data.timeIndex,
      (idx) => {
        if (_data.clock) {
          const [hh, mm] = _data.clock.split(':').map(Number);
          if (clockToTimeIndex(hh, mm) === idx) return;
        }
        _data.clock = timeIndexToClock(idx);
      },
    );

    const handlePlace = (path: string[] | null) => {
      if (!path?.length) {
        _data.areaPath = [];
        _data.lng = 0;
        _data.lat = 0;
        return;
      }
      const hit = findPlaceByPath(path);
      if (!hit) return;
      _data.areaPath = [...hit.path];
      _data.lng = hit.lng;
      _data.lat = hit.lat;
    };

    const toPaddedIso = (y: number, mo: number, d: number) =>
      `${y}-${String(mo).padStart(2, '0')}-${String(d).padStart(2, '0')}`;

    const handleSubmit = () => {
      if (!_data.iso) {
        ElMessage.warning(display('請選擇出生日期', false));
        return;
      }
      let iso = _data.iso;
      let timeIndex = _data.timeIndex;
      let trueSolarNote = '';

      if (_data.useTrueSolar) {
        if (!_data.clock) {
          ElMessage.warning(display('請填寫鐘錶時刻', false));
          return;
        }
        if (!_data.areaPath.length || !_data.lng) {
          ElMessage.warning(display('請選擇出生地', false));
          return;
        }
        const [hh, mm] = _data.clock.split(':').map(Number);
        const ts = computeTrueSolar(iso, hh, mm, _data.lng);
        const [y, mo, d] = ts.dateStr.split('-').map(Number);
        iso = toPaddedIso(y, mo, d);
        timeIndex = ts.timeIndex;
        trueSolarNote = display(`真太陽時 ${ts.trueClock}，時差 ${ts.offsetMinutes} 分`, false);
      }

      emit('submit', {
        iso,
        timeIndex,
        surname: _data.surname.trim(),
        gender: _data.gender,
        trueSolarNote,
      });
    };

    return {
      display,
      isMobile,
      timeLabels: TIME_INDEX_LABELS,
      timeOptions,
      genderOptions,
      placeOptions,
      cascaderProps,
      coordHint,
      clockShichenHint,
      trueShichenHint,
      handlePlace,
      ...toRefs(_data),
      handleSubmit,
    };
  },
});
</script>

<style scoped>
.naming-form {
  display: grid;
  grid-template-columns: 1fr;
  gap: 0.85rem;
  padding: 1rem 1.1rem;
  border: 1px solid var(--zw-line);
  border-radius: 12px;
  background: var(--zw-paper);
}
.date-label,
.span-full {
  grid-column: 1 / -1;
  min-width: 0;
}
.row-label {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
}
label {
  display: flex;
  flex-direction: column;
  gap: 0.35rem;
  font-size: 0.85rem;
  color: var(--zw-ink-muted);
  min-width: 0;
}
.hint {
  margin: 0;
  font-size: 12px;
  line-height: 1.55;
  letter-spacing: 0.04em;
  color: var(--zw-muted);
}
input,
select {
  width: 100%;
  box-sizing: border-box;
  min-height: 38px;
  padding: 0.45rem 0.55rem;
  border: 1px solid var(--zw-line);
  border-radius: 8px;
  background: var(--zw-bg);
  color: var(--zw-ink);
  font: inherit;
}
.naming-form :deep(.sheet-select),
.naming-form :deep(.sheet-field),
.naming-form :deep(.sheet-time),
.naming-form :deep(.sheet-cascader),
.naming-form :deep(.birth-date-field) {
  width: 100%;
}
.place-cascader {
  width: 100%;
}
.place-cascader :deep(.el-input),
.place-cascader :deep(.el-input__wrapper) {
  width: 100%;
}
.submit {
  width: 100%;
  min-height: 42px;
  margin-top: 0.15rem;
  padding: 0.6rem 1rem;
  border: none;
  border-radius: 8px;
  background: var(--zw-primary);
  color: #fff;
  font-weight: 600;
  cursor: pointer;
}
.submit:hover {
  filter: brightness(1.05);
}
</style>
