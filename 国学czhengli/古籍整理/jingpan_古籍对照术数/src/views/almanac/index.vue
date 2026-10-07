<template>
  <div class="page-container almanac-page">
    <header class="head">
      <h1>{{ display('老黃曆', false) }}</h1>
      <div class="nav">
        <button type="button" class="nav-btn" @click="handleShift(-1)">
          <span class="nav-chevron prev" aria-hidden="true" />
          {{ display('前一日', false) }}
        </button>
        <SheetDatePicker
          v-if="isMobile"
          v-model="iso"
          class="date-sheet"
          :title="display('選擇日期', false)"
          :placeholder="display('選擇公曆日期', false)"
          :cancel-text="display('取消', false)"
          :confirm-text="display('確定', false)"
          :year-unit="display('年', false)"
          :month-unit="display('月', false)"
          :day-unit="display('日', false)"
          format="padded"
          :max-year="maxYear"
          @change="handlePick"
        />
        <input v-else v-model="iso" class="date" type="date" @change="handlePick" />
        <button type="button" class="nav-btn" @click="handleShift(1)">
          {{ display('後一日', false) }}
          <span class="nav-chevron next" aria-hidden="true" />
        </button>
      </div>
    </header>

    <section v-if="day" class="sheet">
      <div class="date-block">
        <p class="solar">{{ display(day.solarText, false) }}　{{ display(day.week, false) }}</p>
        <p class="lunar">
          <span class="lunar-label">{{ display('農曆', false) }}</span>
          <span class="lunar-body">{{ display(day.lunarText.replace(/^農曆/, ''), false) }}</span>
          <span class="lunar-year">{{ display(day.shengxiao, false) }}年</span>
        </p>
        <p v-if="day.festivals.length" class="fest">{{ display(day.festivals.join(' · '), false) }}</p>
        <p v-if="day.jieQi" class="fest">{{ display(`節氣 ${day.jieQi}`, false) }}</p>
      </div>

      <dl class="pillars">
        <div>
          <dt>{{ display('年柱', false) }}</dt>
          <dd>{{ display(day.yearGanZhi, false) }}</dd>
        </div>
        <div>
          <dt>{{ display('月柱', false) }}</dt>
          <dd>{{ display(day.monthGanZhi, false) }}</dd>
        </div>
        <div>
          <dt>{{ display('日柱', false) }}</dt>
          <dd>{{ display(day.dayGanZhi, false) }}</dd>
        </div>
        <div>
          <dt>{{ display(day.isToday ? '時柱' : '午時', false) }}</dt>
          <dd>{{ display(day.timeGanZhi, false) }}</dd>
        </div>
      </dl>

      <div class="split">
        <article>
          <h2>{{ display('宜', false) }}</h2>
          <p>{{ display(day.yi.join('、') || '—', false) }}</p>
        </article>
        <article>
          <h2 class="ji">{{ display('忌', false) }}</h2>
          <p>{{ display(day.ji.join('、') || '—', false) }}</p>
        </article>
      </div>

      <dl class="meta">
        <div>
          <dt>{{ display('沖煞', false) }}</dt>
          <dd>{{ display(`${day.chong}　煞${day.sha}`, false) }}</dd>
        </div>
        <div>
          <dt>{{ display('納音', false) }}</dt>
          <dd>{{ display(day.nayin, false) }}</dd>
        </div>
        <div>
          <dt>{{ display('值神', false) }}</dt>
          <dd>{{ display(day.tianShen, false) }}</dd>
        </div>
        <div>
          <dt>{{ display('星宿', false) }}</dt>
          <dd>{{ display(day.xiu, false) }}</dd>
        </div>
        <div>
          <dt>{{ display('胎神', false) }}</dt>
          <dd>{{ display(day.taiShen, false) }}</dd>
        </div>
        <div>
          <dt>{{ display('彭祖百忌', false) }}</dt>
          <dd>{{ display(day.pengZu, false) }}</dd>
        </div>
      </dl>
    </section>

    <p class="hint">
      {{
        display(
          '曆注取自公開農曆庫 lunar-typescript（壽星天文曆），只作文獻曆法對照，不構成行事或吉凶裁決。',
          false,
        )
      }}
    </p>
  </div>
</template>

<script lang="ts">
import { computed, defineComponent, reactive, toRefs } from 'vue';
import { useDisplayText } from '@/composables/useDisplayText';
import { useDevice } from '@/composables/useDevice';
import { loadAlmanacDay, shiftIsoDate, toIsoDate } from '@/utils/almanac';
import SheetDatePicker from '@/components/sheet/SheetDatePicker.vue';

export default defineComponent({
  name: 'AlmanacPage',
  components: { SheetDatePicker },
  setup() {
    const { display } = useDisplayText();
    const { isMobile } = useDevice();
    const _data = reactive({
      iso: toIsoDate(new Date()),
    });
    const day = computed(() => loadAlmanacDay(_data.iso));
    const maxYear = new Date().getFullYear() + 2;
    const _methods = {
      handleShift(days: number) {
        _data.iso = shiftIsoDate(_data.iso, days);
      },
      handlePick() {
        if (!_data.iso) _data.iso = toIsoDate(new Date());
      },
    };
    return { display, isMobile, day, maxYear, ...toRefs(_data), ..._methods };
  },
});
</script>

<style scoped>
.almanac-page {
  max-width: 720px;
}

.head {
  margin-bottom: 18px;
  text-align: center;
}

.head h1 {
  margin: 0 0 14px;
  letter-spacing: 0.32em;
  font-size: 22px;
  font-weight: 600;
  color: var(--zw-ink);
}

.nav {
  display: grid;
  grid-template-columns: auto minmax(0, 1fr) auto;
  gap: 8px;
  align-items: center;
}

.nav-btn {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  margin: 0;
  padding: 8px 10px;
  border: 1px solid color-mix(in srgb, var(--zw-gold) 55%, var(--zw-line));
  border-radius: 999px;
  background: color-mix(in srgb, var(--zw-paper) 88%, var(--zw-gold));
  color: var(--zw-muted);
  font-family: inherit;
  font-size: 13px;
  letter-spacing: 0.1em;
  white-space: nowrap;
  transition: color 0.15s ease, border-color 0.15s ease, background 0.15s ease;
}

.nav-btn:active {
  color: var(--zw-primary);
  border-color: var(--zw-gold);
  background: color-mix(in srgb, var(--zw-gold) 18%, var(--zw-paper));
}

.nav-chevron {
  width: 6px;
  height: 6px;
  border-top: 1.5px solid currentColor;
  border-right: 1.5px solid currentColor;
  opacity: 0.75;
}

.nav-chevron.prev {
  transform: rotate(-135deg);
}

.nav-chevron.next {
  transform: rotate(45deg);
}

.date,
.date-sheet {
  width: 100%;
  min-width: 0;
}

.date {
  display: block;
  margin: 0;
  padding: 9px 12px;
  border: 1px solid color-mix(in srgb, var(--zw-gold) 70%, var(--zw-line));
  border-radius: 10px;
  background: var(--zw-paper);
  color: var(--zw-ink);
  font-family: inherit;
  font-size: 14px;
  letter-spacing: 0.08em;
  text-align: center;
  box-sizing: border-box;
}

.date-sheet :deep(.sheet-field) {
  min-height: 40px;
  padding: 9px 14px;
  border: 1px solid color-mix(in srgb, var(--zw-gold) 70%, var(--zw-line));
  border-radius: 10px;
  background: var(--zw-paper);
  box-shadow: inset 0 0 0 1px color-mix(in srgb, var(--zw-gold) 12%, transparent);
}

.date-sheet :deep(.text) {
  text-align: center;
  font-size: 15px;
  letter-spacing: 0.1em;
  font-weight: 500;
}

.date-sheet :deep(.arrow) {
  border-color: var(--zw-gold);
  opacity: 0.9;
}

.sheet {
  border: 1px solid color-mix(in srgb, var(--zw-gold) 75%, var(--zw-line));
  background:
    linear-gradient(
      180deg,
      color-mix(in srgb, var(--zw-gold) 8%, var(--zw-paper)) 0%,
      var(--zw-paper) 48px
    );
  border-radius: 14px;
  padding: 22px 18px 14px;
}

.date-block {
  text-align: center;
  padding-bottom: 16px;
  border-bottom: 1px solid color-mix(in srgb, var(--zw-gold) 35%, var(--zw-line));
}

.solar {
  margin: 0;
  font-size: 14px;
  letter-spacing: 0.14em;
  color: var(--zw-muted);
}

.lunar {
  display: flex;
  flex-wrap: wrap;
  justify-content: center;
  align-items: baseline;
  gap: 0.35em 0.55em;
  margin: 10px 0 0;
  color: var(--zw-primary);
}

.lunar-label {
  font-size: 12px;
  letter-spacing: 0.28em;
  opacity: 0.72;
}

.lunar-body {
  font-size: 22px;
  font-weight: 600;
  letter-spacing: 0.18em;
  line-height: 1.35;
}

.lunar-year {
  font-size: 14px;
  letter-spacing: 0.16em;
  padding: 2px 8px;
  border-radius: 999px;
  border: 1px solid color-mix(in srgb, var(--zw-primary) 28%, var(--zw-line));
  background: color-mix(in srgb, var(--zw-primary) 8%, var(--zw-paper));
}

.fest {
  margin: 10px 0 0;
  color: #b42318;
  letter-spacing: 0.1em;
  font-size: 13px;
}

.pillars {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 8px;
  margin: 16px 0;
}

.pillars div {
  text-align: center;
  padding: 10px 6px;
  border-radius: 10px;
  border: 1px solid var(--zw-line);
  background: color-mix(in srgb, var(--zw-paper) 82%, var(--zw-bg));
}

.pillars dt,
.meta dt {
  color: var(--zw-muted);
  font-size: 12px;
  letter-spacing: 0.16em;
}

.pillars dd {
  margin: 6px 0 0;
  font-size: 20px;
  letter-spacing: 0.12em;
}

.split {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 10px;
}

.split article {
  border: 1px solid var(--zw-line);
  border-radius: 10px;
  padding: 10px 12px;
  background: color-mix(in srgb, var(--zw-paper) 90%, var(--zw-bg));
}

.split h2 {
  margin: 0 0 8px;
  font-size: 14px;
  letter-spacing: 0.24em;
  color: var(--zw-primary);
}

.split .ji {
  color: #b42318;
}

.split p {
  margin: 0;
  line-height: 1.7;
  font-size: 14px;
}

.meta {
  margin: 16px 0 8px;
  display: grid;
  gap: 10px;
}

.meta div {
  text-align: center;
}

.meta dd {
  margin: 4px 0 0;
  letter-spacing: 0.06em;
}

.hint {
  margin-top: 16px;
  font-size: 12px;
  color: var(--zw-muted);
  line-height: 1.7;
}

@media (max-width: 767.98px) {
  .nav-btn {
    padding: 8px 8px;
    font-size: 12px;
    letter-spacing: 0.06em;
  }

  .lunar-body {
    font-size: 20px;
  }

  .pillars {
    grid-template-columns: repeat(2, 1fr);
  }

  .split {
    grid-template-columns: 1fr;
  }
}
</style>
