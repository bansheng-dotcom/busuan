<template>
  <div class="nayin-panel">
    <form class="query" @submit.prevent>
      <label class="date-label">
        {{ display('出生日期', false) }}
        <BirthDateField v-model="iso" format="padded" @change="handlePick" />
      </label>
      <label>
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
    </form>

    <section v-if="result" class="result">
      <div class="ju">
        <span>{{ display('五行局', false) }}</span>
        <strong>{{ display(result.fiveElementsClass, false) }}</strong>
      </div>
      <dl class="pillars">
        <div v-for="item in result.pillars" :key="item.label">
          <dt>{{ display(item.label, false) }}</dt>
          <dd>{{ display(item.ganZhi, false) }}</dd>
          <dd class="sub">{{ display(`${item.name} · ${item.wuxing}`, false) }}</dd>
        </div>
        <div v-if="result.soul">
          <dt>{{ display(result.soul.label, false) }}</dt>
          <dd>{{ display(result.soul.ganZhi, false) }}</dd>
          <dd class="sub">{{ display(`${result.soul.name} · ${result.soul.wuxing}`, false) }}</dd>
        </div>
      </dl>
    </section>

    <table class="nayin-table">
      <thead>
        <tr>
          <th>{{ display('花甲', false) }}</th>
          <th>{{ display('納音', false) }}</th>
          <th>{{ display('五行', false) }}</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="row in pairs" :key="row.first" :class="{ hit: isHit(row) }">
          <td>{{ display(`${row.first} ${row.second}`, false) }}</td>
          <td>{{ display(row.name, false) }}</td>
          <td>{{ display(row.wuxing, false) }}</td>
        </tr>
      </tbody>
    </table>

    <p class="hint">
      {{
        display(
          '歌辭據卷二《六十花甲子納音歌》。底本「甲戊」「已亥」「桑拓」按六十甲子通行寫作甲戌、己亥、桑柘，只便檢索；古籍頁仍照底本。五行局由命宮干支納音所定，與排盤算法相同，不作吉凶斷語。',
          false,
        )
      }}
      <router-link :to="{ path: '/book', hash: '#huajia-nayin' }">{{ display('卷二原文', false) }}</router-link>
    </p>
  </div>
</template>

<script lang="ts">
import { computed, defineComponent, reactive, toRefs } from 'vue';
import { useDisplayText } from '@/composables/useDisplayText';
import { useDevice } from '@/composables/useDevice';
import { clockToTimeIndex, TIME_INDEX_LABELS } from '@/utils/trueSolar';
import { toIsoDate } from '@/utils/almanac';
import { lookupBirthNayin, NAYIN_PAIRS, type NayinPair } from '@/utils/nayin';
import SheetSelect from '@/components/sheet/SheetSelect.vue';
import BirthDateField from '@/components/BirthDateField.vue';

export default defineComponent({
  name: 'NayinPanel',
  components: { SheetSelect, BirthDateField },
  setup() {
    const { display } = useDisplayText();
    const { isMobile } = useDevice();
    const now = new Date();
    const _data = reactive({
      iso: toIsoDate(now),
      timeIndex: clockToTimeIndex(now.getHours(), now.getMinutes()),
    });
    const result = computed(() => lookupBirthNayin(_data.iso, _data.timeIndex));
    const timeOptions = computed(() =>
      TIME_INDEX_LABELS.map((label, idx) => ({
        label: display(label, false),
        value: idx,
      })),
    );
    const hitKeys = computed(() => {
      const keys = result.value.pillars.map((p) => p.ganZhi);
      if (result.value.soul) keys.push(result.value.soul.ganZhi);
      return new Set(keys);
    });
    const _inner = {
      isHit(row: NayinPair) {
        return hitKeys.value.has(row.first) || hitKeys.value.has(row.second);
      },
    };
    const _methods = {
      handlePick() {
        if (!_data.iso) _data.iso = toIsoDate(new Date());
      },
      isHit: _inner.isHit,
    };
    return {
      display,
      isMobile,
      pairs: NAYIN_PAIRS,
      timeLabels: TIME_INDEX_LABELS,
      timeOptions,
      result,
      ...toRefs(_data),
      ..._methods,
    };
  },
});
</script>

<style scoped>
.query {
  display: grid;
  grid-template-columns: 1fr;
  gap: 12px;
  margin-bottom: 16px;
  align-items: start;
}
.query label {
  display: flex;
  flex-direction: column;
  gap: 6px;
  font-size: 13px;
  letter-spacing: 0.12em;
  color: var(--zw-muted);
  min-width: 0;
}
.query select {
  width: 100%;
  box-sizing: border-box;
  border: 1px solid var(--zw-line);
  background: var(--zw-paper);
  color: var(--zw-ink);
  padding: 8px 10px;
  border-radius: 8px;
  font-family: inherit;
}
.query :deep(.sheet-select),
.query :deep(.sheet-field),
.query :deep(.birth-date-field) {
  width: 100%;
}
.result {
  border: 1px solid var(--zw-gold);
  border-radius: 12px;
  padding: 14px 12px 8px;
  margin-bottom: 16px;
  background: var(--zw-paper);
}
.ju {
  display: flex;
  justify-content: center;
  align-items: baseline;
  gap: 12px;
  letter-spacing: 0.18em;
  margin-bottom: 12px;
}
.ju strong {
  font-size: 22px;
  color: var(--zw-primary);
}
.pillars {
  display: grid;
  grid-template-columns: repeat(5, 1fr);
  gap: 8px;
  text-align: center;
}
.pillars dt {
  font-size: 12px;
  color: var(--zw-muted);
  letter-spacing: 0.14em;
}
.pillars dd {
  margin: 4px 0 0;
  letter-spacing: 0.08em;
}
.pillars .sub {
  font-size: 12px;
  color: var(--zw-primary);
}
.nayin-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 14px;
}
.nayin-table th,
.nayin-table td {
  border-bottom: 1px solid var(--zw-line);
  padding: 8px 6px;
  text-align: left;
  letter-spacing: 0.08em;
}
.nayin-table th {
  color: var(--zw-primary);
  font-weight: 600;
}
.nayin-table tr.hit td {
  background: color-mix(in srgb, var(--zw-gold) 22%, transparent);
  color: var(--zw-primary);
}
.hint {
  margin-top: 14px;
  font-size: 12px;
  color: var(--zw-muted);
  line-height: 1.7;
}
.hint a {
  margin-left: 8px;
  color: var(--zw-primary);
}
@media (max-width: 767.98px) {
  .pillars {
    grid-template-columns: 1fr 1fr;
  }
}
</style>
