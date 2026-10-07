<template>
  <div class="page-container chart-page">
    <el-tabs v-model="pageTab" class="chart-tabs">
      <el-tab-pane :label="display('生辰排盤', false)" name="chart">
    <div class="layout">
      <section class="form-col rounded-lg border" :style="cardStyle">
        <h2 class="form-title font-semibold">{{ display('生辰排盤', false) }}</h2>
        <ChartForm :loading="loading" :seed="formSeed" @submit="handleGenerate" @reset="handleReset" />
        <p v-if="trueSolarNote" class="true-solar-note" style="color: var(--zw-muted)">{{ trueSolarNote }}</p>
        <div v-if="chart" class="horoscope-block">
          <div class="horoscope-field">
            <div class="horoscope-label">{{ display('大限／流年', false) }}</div>
            <SheetDatePicker
              v-if="isMobile"
              v-model="targetDate"
              :title="display('大限／流年', false)"
              :placeholder="display('選擇推運日期', false)"
              :cancel-text="display('取消', false)"
              :confirm-text="display('確定', false)"
              :year-unit="display('年', false)"
              :month-unit="display('月', false)"
              :day-unit="display('日', false)"
              format="loose"
              :max-year="horoscopeMaxYear"
              @change="handleHoroscope"
            />
            <el-date-picker
              v-else
              v-model="targetDate"
              type="date"
              value-format="YYYY-M-D"
              class="horoscope-picker"
              :placeholder="display('選擇推運日期', false)"
              @change="handleHoroscope"
            />
            <p class="horoscope-hint">
              {{
                display(
                  '選一個公曆日期，查看該日所在大限（約十年一段）與流年；盤面會高亮對應大限宫、流年宫，並疊加流曜。預設為出生當天。',
                  false,
                )
              }}
            </p>
          </div>
          <p v-if="horoscope" class="horoscope-summary">
            <span class="tag decadal-tag">{{ display('大限', false) }}</span>
            {{ horoscope.decadalRange }}
            <span class="tag yearly-tag">{{ display('流年', false) }}</span>
            {{ horoscope.yearly }}
          </p>
          <el-button class="export-btn" :loading="exporting" :disabled="exporting" @click="handleExport">
            {{ display('導出命盤圖片', false) }}
          </el-button>
        </div>
      </section>

      <section class="board-col">
        <div v-if="chart" ref="captureRef">
          <ChartBoard
            :palaces="displayPalaces"
            :five-elements-class="chart.fiveElementsClass"
            :soul="chart.soul"
            :body="chart.body"
            :lunar-date="chart.lunarDate"
            :chinese-date="chart.chineseDate"
            @star-click="handleStarClick"
          />
        </div>
        <p v-else class="rounded-lg border p-8 text-center" :style="cardStyle">
          {{ display('請輸入出生日期後生成命盤。點擊星曜只彈出《諸星問答論》原文。解讀頁籤中的白話是卷一原句今譯，並附出處。', false) }}
        </p>
        <ChartResultTabs
          v-if="chart"
          :readings="readings"
          :patterns="patterns"
          :excerpts="excerpts"
          :five-elements-class="chart.fiveElementsClass"
          :soul="chart.soul"
          :body="chart.body"
          :gender="chart.gender"
          :lunar-date="chart.lunarDate"
          :chinese-date="chart.chineseDate"
          :horoscope="horoscope"
          :ai-loading="aiLoading"
          :ai-error="aiError"
          :ai-content="aiContent"
          :ai-configured="aiConfigured"
          @goto="handleGoto"
          @generate-ai="handleAiGenerate"
        />
      </section>
    </div>

    <StarDialog v-model="dialogVisible" :star-name="activeStar" />
      </el-tab-pane>
      <el-tab-pane :label="display('六十納音', false)" name="nayin">
        <div class="nayin-wrap">
          <NayinPanel />
        </div>
      </el-tab-pane>
    </el-tabs>
  </div>
</template>

<script lang="ts">
import { computed, defineComponent, nextTick, onActivated, onMounted, reactive, ref, toRefs } from 'vue';
import { onBeforeRouteLeave, useRouter } from 'vue-router';
import { captureElement } from '@/utils/captureHtml';
import ChartForm, { type ChartFormValue } from './components/ChartForm.vue';
import ChartBoard from './components/ChartBoard.vue';
import ChartResultTabs from './components/ChartResultTabs.vue';
import NayinPanel from './components/NayinPanel.vue';
import StarDialog from '@/components/StarDialog.vue';
import SheetDatePicker from '@/components/sheet/SheetDatePicker.vue';
import { buildChart, getHoroscope, palacesWithHoroscope, type BuiltChart, type HoroscopeView } from '@/utils/chart';
import { computeTrueSolar } from '@/utils/trueSolar';
import { matchPatterns } from '@/utils/patternMatch';
import { extractExcerpts } from '@/utils/excerpt';
import { buildPalaceReadings } from '@/utils/palaceReading';
import { upgradeQuoteVernacular } from '@/utils/bookVernacular';
import { fetchChartAiHolographic, isChartAiConfigured } from '@/api/chartAi';
import { buildChartAiPayload, hasChartAiMaterial } from '@/utils/chartAiPayload';
import { useAppStore } from '@/store/app';
import { useChartSessionStore } from '@/store/chartSession';
import { useDisplayText } from '@/composables/useDisplayText';
import { useDevice } from '@/composables/useDevice';
import type { ExcerptItem, MatchedPattern } from '@/types';
import { ElMessage } from 'element-plus';

export default defineComponent({
  name: 'ChartPage',
  components: {
    ChartForm,
    ChartBoard,
    ChartResultTabs,
    NayinPanel,
    StarDialog,
    SheetDatePicker,
  },
  setup() {
    const router = useRouter();
    const store = useAppStore();
    const session = useChartSessionStore();
    const { display } = useDisplayText();
    const { isMobile } = useDevice();
    const captureRef = ref<HTMLElement>();
    const formSeed = session.getSnapshot()?.form ?? null;
    const restoredOnce = ref(false);
    const horoscopeMaxYear = new Date().getFullYear() + 80;
    const _data = reactive({
      pageTab: 'chart',
      loading: false,
      exporting: false,
      chart: null as BuiltChart | null,
      patterns: [] as MatchedPattern[],
      excerpts: [] as ExcerptItem[],
      dialogVisible: false,
      activeStar: '',
      targetDate: '',
      horoscope: null as HoroscopeView | null,
      trueSolarNote: '',
      aiLoading: false,
      aiError: '',
      aiContent: '',
    });

    const aiConfigured = isChartAiConfigured();

    const displayPalaces = computed(() => {
      if (!_data.chart) return [];
      if (!_data.targetDate) return _data.chart.palaces;
      return palacesWithHoroscope(_data.chart.astrolabe, _data.chart.palaces, _data.targetDate);
    });

    const readings = computed(() =>
      buildPalaceReadings(displayPalaces.value).map((reading) => ({
        ...reading,
        quotes: reading.quotes.map((q) => upgradeQuoteVernacular(q)),
      })),
    );

    const cardStyle = {
      background: 'var(--zw-paper)',
      borderColor: 'var(--zw-line)',
    };

    const _inner = {
      clearAiState() {
        _data.aiLoading = false;
        _data.aiError = '';
        _data.aiContent = '';
      },
      refreshDerived() {
        if (!_data.chart) return;
        _data.patterns = matchPatterns(_data.chart);
        _data.excerpts = extractExcerpts(_data.chart);
      },
    };

    const _methods = {
      /** 生成命盘 */
      handleGenerate(form: ChartFormValue) {
        if (!form.solarDate || form.timeIndex === null || (form.gender !== '男' && form.gender !== '女')) {
          ElMessage.warning(display('請完善未填寫的內容', false));
          return;
        }
        const gender = form.gender;
        const birthTimeIndex = form.timeIndex;
        _inner.clearAiState();
        _data.loading = true;
        try {
          let solarDate = form.solarDate;
          let timeIndex = birthTimeIndex;
          _data.trueSolarNote = '';
          if (form.useTrueSolar && form.clock) {
            const [h, m] = form.clock.split(':').map(Number);
            const ts = computeTrueSolar(form.solarDate, h, m, form.lng);
            solarDate = ts.dateStr;
            timeIndex = ts.timeIndex;
            _data.trueSolarNote = `真太陽時 ${ts.trueClock}，時差 ${ts.offsetMinutes} 分`;
          }
          _data.chart = buildChart({
            solarDate,
            timeIndex,
            gender,
            language: store.iztroLang,
          });
          _data.targetDate = solarDate;
          _inner.refreshDerived();
          _methods.handleHoroscope(solarDate);
          session.saveSnapshot({
            form,
            targetDate: _data.targetDate,
            trueSolarNote: _data.trueSolarNote,
          });
        } catch (err) {
          ElMessage.error(err instanceof Error ? err.message : '排盤失敗');
        } finally {
          _data.loading = false;
        }
      },
      handleStarClick(name: string) {
        _data.activeStar = name;
        _data.dialogVisible = true;
      },
      handleHoroscope(date: string) {
        if (!_data.chart || !date) return;
        _data.horoscope = getHoroscope(_data.chart.astrolabe, date);
        const snap = session.getSnapshot();
        if (snap) {
          session.saveSnapshot({ ...snap, targetDate: date });
        }
      },
      async handleExport() {
        if (!captureRef.value || _data.exporting) return;
        const scrollX = window.scrollX;
        const scrollY = window.scrollY;
        _data.exporting = true;
        try {
          const canvas = await captureElement(captureRef.value);
          const a = document.createElement('a');
          a.href = canvas.toDataURL('image/png');
          a.download = 'ziwei-chart.png';
          a.click();
        } catch (err) {
          ElMessage.error(err instanceof Error ? err.message : '導出失敗');
        } finally {
          _data.exporting = false;
          window.scrollTo(scrollX, scrollY);
        }
      },
      handleGoto(id: string) {
        session.markFromChart();
        void router.push({ path: '/book', query: { from: 'chart' }, hash: `#${id}` });
      },
      handleReset() {
        _data.chart = null;
        _data.patterns = [];
        _data.excerpts = [];
        _data.horoscope = null;
        _data.targetDate = '';
        _data.trueSolarNote = '';
        _data.dialogVisible = false;
        _data.activeStar = '';
        _inner.clearAiState();
        session.clearSnapshot();
        ElMessage.success(display('已重置表單與命盤', false));
      },
      async handleAiGenerate(opts?: { timeline?: Array<{ year: number; event: string }> }) {
        if (!_data.chart || _data.aiLoading) return;
        if (!aiConfigured) {
          ElMessage.warning(display('全息診斷服務尚未配置', false));
          return;
        }
        const payload = buildChartAiPayload({
          chart: _data.chart,
          palaces: displayPalaces.value,
          patterns: _data.patterns,
          excerpts: _data.excerpts,
          readings: readings.value,
        });
        if (!hasChartAiMaterial(payload)) {
          ElMessage.warning(display('本盤材料不足，無法生成全息診斷', false));
          return;
        }
        _data.aiLoading = true;
        _data.aiError = '';
        try {
          const timeline = (opts?.timeline || []).slice(0, 2);
          _data.aiContent = await fetchChartAiHolographic({
            ...payload,
            timeline: timeline.length ? timeline : undefined,
          });
        } catch (err) {
          _data.aiError = err instanceof Error ? err.message : display('生成失敗，請稍後重試', false);
        } finally {
          _data.aiLoading = false;
        }
      },
    };

    const restoreSession = () => {
      if (_data.chart || restoredOnce.value) return;
      const snap = session.getSnapshot();
      if (!snap) return;
      restoredOnce.value = true;
      _methods.handleGenerate(snap.form);
      if (snap.targetDate) {
        _data.targetDate = snap.targetDate;
        _methods.handleHoroscope(snap.targetDate);
      }
      _data.trueSolarNote = snap.trueSolarNote;
    };

    const restoreScroll = () => {
      const y = session.getScrollY();
      if (!y) return;
      void nextTick(() => {
        window.scrollTo({ top: y, left: 0, behavior: 'auto' });
        requestAnimationFrame(() => window.scrollTo({ top: y, left: 0, behavior: 'auto' }));
      });
    };

    onMounted(() => {
      restoreSession();
      restoreScroll();
    });

    onActivated(() => {
      restoreScroll();
    });

    onBeforeRouteLeave(() => {
      session.saveScroll();
    });

    return {
      display,
      isMobile,
      horoscopeMaxYear,
      captureRef,
      cardStyle,
      displayPalaces,
      readings,
      formSeed,
      aiConfigured,
      ...toRefs(_data),
      ..._methods,
    };
  },
});
</script>

<style scoped>
.chart-tabs :deep(.el-tabs__item) {
  color: var(--zw-muted);
  letter-spacing: 0.16em;
}
.chart-tabs :deep(.el-tabs__item.is-active) {
  color: var(--zw-primary);
}
.chart-tabs :deep(.el-tabs__active-bar) {
  background: var(--zw-gold);
}
.chart-tabs :deep(.el-tabs__nav-wrap::after) {
  background: var(--zw-line);
}
.nayin-wrap {
  max-width: 720px;
  margin: 0 auto;
}
.layout {
  display: grid;
  grid-template-columns: 280px minmax(0, 1fr);
  gap: 16px;
  align-items: start;
}
.form-col {
  padding: 16px;
}
.form-title {
  margin-bottom: 12px;
}
.true-solar-note {
  margin-top: 12px;
  font-size: 0.75em;
  line-height: 1.55;
}
.horoscope-block {
  margin-top: 20px;
  padding-top: 16px;
  border-top: 1px solid var(--zw-line);
  display: flex;
  flex-direction: column;
  gap: 12px;
}
.horoscope-field {
  min-width: 0;
}
.horoscope-label {
  margin-bottom: 6px;
  font-size: 14px;
  line-height: 1.4;
  color: var(--zw-ink);
}
.horoscope-picker {
  width: 100%;
  max-width: 100%;
}
.horoscope-picker :deep(.el-input__wrapper) {
  width: 100%;
}
.layout,
.board-col,
.form-col {
  min-width: 0;
}
.horoscope-hint {
  margin: 6px 0 0;
  font-size: 0.75em;
  line-height: 1.55;
  letter-spacing: 0.04em;
  color: var(--zw-muted);
}
.horoscope-summary {
  font-size: 0.95em;
  line-height: 1.7;
  padding: 10px 12px;
  border-radius: 8px;
  border: 1px solid var(--zw-line);
  background: color-mix(in srgb, var(--zw-gold) 10%, var(--zw-paper));
}
.horoscope-summary .tag {
  display: inline-block;
  margin-right: 4px;
  padding: 1px 6px;
  border-radius: 4px;
  font-size: 0.85em;
  letter-spacing: 0.08em;
}
.horoscope-summary .decadal-tag {
  color: #fff;
  background: var(--zw-primary);
}
.horoscope-summary .yearly-tag {
  margin-left: 8px;
  color: var(--zw-ink);
  background: color-mix(in srgb, var(--zw-gold) 70%, #fff);
}
.export-btn {
  align-self: flex-start;
}
@media (max-width: 1100px) {
  .layout {
    grid-template-columns: 1fr;
  }
}
@media (max-width: 767.98px) {
  .layout {
    gap: 14px;
  }
  .board-col {
    width: 100%;
    max-width: 100%;
    overflow-x: hidden;
  }
  .form-col {
    padding: 14px 14px 16px;
    overflow-x: hidden;
  }
  .form-title {
    margin-bottom: 10px;
    font-size: 1em;
    letter-spacing: 0.1em;
  }
  .true-solar-note {
    margin-top: 10px;
    font-size: 0.75em;
    line-height: 1.5;
  }
  .horoscope-block {
    margin-top: 14px;
    padding-top: 14px;
    gap: 10px;
  }
  .horoscope-label {
    margin-bottom: 4px;
    font-size: 0.92em;
    letter-spacing: 0.06em;
    color: var(--zw-muted);
  }
  .horoscope-hint {
    margin-top: 6px;
    font-size: 0.75em;
    line-height: 1.5;
  }
  .export-btn {
    width: 100%;
    min-height: 38px;
  }
}
</style>
