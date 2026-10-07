<template>
  <div class="page-container liuren-page">
    <h1>{{ display(content.title, false) }}</h1>
    <p class="lead">
      {{ display(content.note, false) }}
      <a :href="content.sourceUrl" target="_blank" rel="noopener">{{ display('來源頁', false) }}</a>
    </p>

    <section class="panel" :style="cardStyle">
      <h2>{{ display('起課', false) }}</h2>
      <p class="hint">
        {{ display('請以心血來潮當下之農曆月、日、時為準。勿用國曆；勿重複起第二次。', false) }}
      </p>

      <div class="fields">
        <label>
          <span>{{ display('農曆月', false) }}</span>
          <SheetSelect
            v-if="isMobile"
            v-model="month"
            :options="monthOptions"
            :title="display('農曆月', false)"
            :cancel-text="display('取消', false)"
          />
          <el-select v-else v-model="month" class="w-full">
            <el-option v-for="n in 12" :key="n" :label="display(`${n}月`, false)" :value="n" />
          </el-select>
        </label>
        <label>
          <span>{{ display('農曆日', false) }}</span>
          <SheetSelect
            v-if="isMobile"
            v-model="day"
            :options="dayOptions"
            :title="display('農曆日', false)"
            :cancel-text="display('取消', false)"
          />
          <el-select v-else v-model="day" class="w-full">
            <el-option v-for="n in 30" :key="n" :label="display(`${n}日`, false)" :value="n" />
          </el-select>
        </label>
        <label>
          <span>{{ display('時辰', false) }}</span>
          <SheetSelect
            v-if="isMobile"
            v-model="hour"
            :options="hourOptions"
            :title="display('時辰', false)"
            :cancel-text="display('取消', false)"
          />
          <el-select v-else v-model="hour" class="w-full">
            <el-option
              v-for="item in LIUREN_HOURS"
              :key="item.value"
              :label="display(item.label, false)"
              :value="item.value"
            />
          </el-select>
        </label>
      </div>

      <div class="actions">
        <el-button type="primary" @click="handleCast">{{ display('起課', false) }}</el-button>
        <el-button @click="handleFillNow">{{ display('填入此刻農曆', false) }}</el-button>
        <el-button @click="handleReset">{{ display('重置', false) }}</el-button>
      </div>

      <div class="cast-visual">
        <LiurenHand :active-index="handActive" @select="previewIndex = $event" />
        <div class="palm" aria-label="六宫">
          <button
            v-for="(p, idx) in LIUREN_PALACES"
            :key="p.key"
            type="button"
            class="cell"
            :class="{
              selected: handActive === idx,
              result: result && result.index === idx,
              ji: p.luck === '吉',
              xiong: p.luck === '凶',
            }"
            @click="previewIndex = idx"
          >
            <em>{{ idx + 1 }}</em>
            <b>{{ display(p.name, false) }}</b>
            <span>{{ display(p.luck, false) }}</span>
            <i v-if="result && result.index === idx" class="mark">{{ display('落宮', false) }}</i>
          </button>
        </div>
      </div>

      <article v-if="result" class="outcome" :class="result.palace.luck === '吉' ? 'is-ji' : 'is-xiong'">
        <p class="badge">
          {{ display(result.palace.name, false) }}
          ·
          {{ display(result.palace.luck, false) }}
        </p>
        <p class="summary">{{ display(result.palace.summary, false) }}</p>
        <p class="trace">
          {{
            display(
              `月落${LIUREN_PALACES[result.monthIndex].name} → 日落${LIUREN_PALACES[result.dayIndex].name} → 時落${result.palace.name}`,
              false,
            )
          }}
        </p>
      </article>
      <article v-else-if="previewPalace" class="outcome muted">
        <p class="badge">
          {{ display(previewPalace.name, false) }}
          ·
          {{ display(previewPalace.luck, false) }}
        </p>
        <p class="summary">{{ display(previewPalace.summary, false) }}</p>
        <p class="trace">{{ display('點「起課」後，落宮會高亮顯示。', false) }}</p>
      </article>

      <div v-if="result" class="ai-panel">
        <h3>{{ display('AI 解讀', false) }}</h3>
        <p class="ai-hint">
          {{ display('請先填寫所問事項；AI 給傾向說明，僅供參考，不作唯一決策依據。', false) }}
        </p>
        <el-input
          v-model="aiQuestion"
          type="textarea"
          :rows="2"
          maxlength="120"
          show-word-limit
          :placeholder="display('請輸入所問事項', false)"
          :class="{ 'is-empty-hint': aiQuestionNeedHint }"
        />
        <p v-if="aiQuestionNeedHint" class="ai-field-hint">
          {{ display('請先填寫所問事項再生成。', false) }}
        </p>
        <div class="ai-actions">
          <el-button
            type="primary"
            :loading="aiLoading"
            :disabled="!aiConfigured || aiLoading"
            @click="handleAiGenerate"
          >
            {{ display('生成解讀', false) }}
          </el-button>
          <span class="ai-wait-hint">
            {{ display('生成較耗時（約一至兩分鐘），請稍候，勿切換或離開本頁。', false) }}
          </span>
        </div>
        <p v-if="aiLoading" class="ai-wait-hint is-loading">
          {{ display('正在生成中，請耐心等待，勿關閉或切換頁面…', false) }}
        </p>
        <p v-if="!aiConfigured" class="ai-hint">{{ display('AI 解讀服務尚未配置。', false) }}</p>
        <p v-if="aiError" class="ai-error">{{ aiError }}</p>
        <pre v-if="aiContent" class="ai-body">{{ display(aiContent, false) }}</pre>
      </div>
    </section>

    <section class="panel guide" :style="cardStyle">
      <h2>{{ display('何時用', false) }}</h2>
      <ul>
        <li v-for="(line, i) in content.when" :key="i">{{ display(line, false) }}</li>
      </ul>

      <h2>{{ display('注意', false) }}</h2>
      <p>{{ display(content.caution, false) }}</p>

      <h2>{{ display('算法要點', false) }}</h2>
      <ol>
        <li v-for="(line, i) in content.algorithm" :key="i">{{ display(line, false) }}</li>
      </ol>

      <h2>{{ display('案例', false) }}</h2>
      <div v-for="ex in content.examples" :key="ex.title" class="example">
        <strong>{{ display(ex.title, false) }}</strong>
        <p>{{ display(ex.text, false) }}</p>
      </div>
    </section>
  </div>
</template>

<script lang="ts">
import { computed, defineComponent, ref, watch } from 'vue';
import { Solar } from 'lunar-typescript';
import { ElMessage } from 'element-plus';
import contentJson from '@/data/liurenContent.json';
import { useDisplayText } from '@/composables/useDisplayText';
import { useDevice } from '@/composables/useDevice';
import { fetchDivinationAi, isDivinationAiConfigured } from '@/api/divinationAi';
import { buildLiurenAiPayload } from '@/utils/liurenAiPayload';
import SheetSelect from '@/components/sheet/SheetSelect.vue';
import LiurenHand from './components/LiurenHand.vue';
import {
  LIUREN_HOURS,
  LIUREN_PALACES,
  castLiuren,
  clockToLiurenHour,
  type LiurenResult,
} from '@/utils/liuren';

export default defineComponent({
  name: 'LiurenPage',
  components: { LiurenHand, SheetSelect },
  setup() {
    const { display } = useDisplayText();
    const { isMobile } = useDevice();
    const content = contentJson;
    const month = ref(1);
    const day = ref(1);
    const hour = ref(1);
    const result = ref<LiurenResult | null>(null);
    const previewIndex = ref(0);
    const aiConfigured = isDivinationAiConfigured();
    const aiQuestion = ref('');
    const aiQuestionNeedHint = ref(false);
    const aiLoading = ref(false);
    const aiError = ref('');
    const aiContent = ref('');

    watch(aiQuestion, (v) => {
      if (v.trim()) aiQuestionNeedHint.value = false;
    });

    const monthOptions = computed(() =>
      Array.from({ length: 12 }, (_, i) => ({
        label: display(`${i + 1}月`, false),
        value: i + 1,
      })),
    );
    const dayOptions = computed(() =>
      Array.from({ length: 30 }, (_, i) => ({
        label: display(`${i + 1}日`, false),
        value: i + 1,
      })),
    );
    const hourOptions = computed(() =>
      LIUREN_HOURS.map((item) => ({
        label: display(item.label, false),
        value: item.value,
      })),
    );

    const previewPalace = computed(() => LIUREN_PALACES[previewIndex.value]);
    const handActive = computed(() => (result.value ? result.value.index : previewIndex.value));

    const cardStyle = {
      background: 'var(--zw-paper)',
      borderColor: 'var(--zw-line)',
    };

    const clearAi = () => {
      aiError.value = '';
      aiContent.value = '';
    };

    const handleCast = () => {
      result.value = castLiuren({
        month: month.value,
        day: day.value,
        hour: hour.value,
      });
      previewIndex.value = result.value.index;
      clearAi();
    };

    const handleFillNow = () => {
      const now = new Date();
      const lunar = Solar.fromYmdHms(
        now.getFullYear(),
        now.getMonth() + 1,
        now.getDate(),
        now.getHours(),
        now.getMinutes(),
        0,
      ).getLunar();
      month.value = Math.abs(lunar.getMonth()) || 1;
      day.value = lunar.getDay();
      hour.value = clockToLiurenHour(now.getHours(), now.getMinutes());
      result.value = null;
      clearAi();
      ElMessage.success(
        display(
          `已填入農曆${month.value}月${day.value}日 · ${LIUREN_HOURS[hour.value - 1].label.split(' ')[0]}`,
          false,
        ),
      );
    };

    const handleReset = () => {
      month.value = 1;
      day.value = 1;
      hour.value = 1;
      result.value = null;
      previewIndex.value = 0;
      aiQuestion.value = '';
      aiQuestionNeedHint.value = false;
      clearAi();
      ElMessage.info(display('已重置', false));
    };

    const handleAiGenerate = async () => {
      if (!result.value || aiLoading.value) return;
      if (!aiConfigured) {
        ElMessage.warning(display('AI 解讀服務尚未配置', false));
        return;
      }
      if (!aiQuestion.value.trim()) {
        aiQuestionNeedHint.value = true;
        ElMessage.warning({
          message: display('請先填寫所問事項', false),
          duration: 500,
        });
        return;
      }
      aiQuestionNeedHint.value = false;
      aiLoading.value = true;
      aiError.value = '';
      try {
        aiContent.value = await fetchDivinationAi(
          buildLiurenAiPayload({
            result: result.value,
            month: month.value,
            day: day.value,
            hour: hour.value,
            question: aiQuestion.value,
          }),
        );
      } catch (err) {
        aiError.value = err instanceof Error ? err.message : display('生成失敗，請稍後重試', false);
      } finally {
        aiLoading.value = false;
      }
    };

    return {
      display,
      isMobile,
      content,
      cardStyle,
      month,
      day,
      hour,
      monthOptions,
      dayOptions,
      hourOptions,
      result,
      previewIndex,
      previewPalace,
      LIUREN_PALACES,
      LIUREN_HOURS,
      handActive,
      aiConfigured,
      aiQuestion,
      aiQuestionNeedHint,
      aiLoading,
      aiError,
      aiContent,
      handleCast,
      handleFillNow,
      handleReset,
      handleAiGenerate,
    };
  },
});
</script>

<style scoped>
.liuren-page {
  padding-bottom: 2.5rem;
}
.title,
h1 {
  margin: 0 0 0.35rem;
  font-size: 1.55rem;
}
.lead {
  margin: 0 0 1.25rem;
  max-width: 42rem;
  line-height: 1.7;
  font-size: 0.9rem;
  color: var(--zw-muted);
}
.lead a {
  color: var(--zw-primary);
  margin-left: 0.35rem;
}
.panel {
  padding: 1.1rem 1.15rem;
  margin-bottom: 1.25rem;
  border: 1px solid var(--zw-line);
  border-radius: 12px;
}
.panel h2 {
  margin: 0 0 0.65rem;
  font-size: 1rem;
  letter-spacing: 0.16em;
  color: var(--zw-primary);
}
.guide h2 {
  margin-top: 1.15rem;
}
.guide h2:first-child {
  margin-top: 0;
}
.hint {
  margin: 0 0 1rem;
  font-size: 0.82rem;
  line-height: 1.6;
  color: var(--zw-muted);
}
.fields {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 0.75rem;
  margin-bottom: 0.9rem;
}
.fields label {
  display: flex;
  flex-direction: column;
  gap: 0.35rem;
  font-size: 0.85rem;
  color: var(--zw-muted);
  letter-spacing: 0.08em;
}
.actions {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
  margin-bottom: 1.1rem;
}
.cast-visual {
  display: grid;
  grid-template-columns: minmax(0, 280px) minmax(0, 1fr);
  gap: 1rem 1.25rem;
  align-items: start;
  margin-bottom: 1rem;
}
.palm {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 0.55rem;
  margin-bottom: 0;
}
.cell {
  position: relative;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.2rem;
  padding: 0.85rem 0.5rem 1rem;
  border: 1.5px solid var(--zw-line);
  border-radius: 12px;
  background: color-mix(in srgb, var(--zw-bg) 40%, var(--zw-paper));
  color: var(--zw-ink);
  font-family: inherit;
  cursor: pointer;
  transition: border-color 0.15s ease, background 0.15s ease, box-shadow 0.15s ease, transform 0.15s ease;
}
.cell em {
  font-style: normal;
  font-size: 0.72rem;
  color: var(--zw-muted);
}
.cell b {
  font-size: 1.05rem;
  letter-spacing: 0.14em;
}
.cell span {
  font-size: 0.75rem;
  letter-spacing: 0.12em;
}
.cell.ji span {
  color: #2d6a4f;
}
.cell.xiong span {
  color: #8a2f2f;
}
.cell.selected {
  border-color: var(--zw-gold);
  background: color-mix(in srgb, var(--zw-paper) 78%, var(--zw-gold));
  box-shadow:
    0 0 0 2px color-mix(in srgb, var(--zw-gold) 45%, transparent),
    0 4px 14px rgba(44, 36, 22, 0.1);
  transform: translateY(-1px);
}
.cell.selected b {
  color: var(--zw-primary);
}
.cell.result {
  border-width: 2px;
  border-color: var(--zw-primary);
  box-shadow:
    0 0 0 2px color-mix(in srgb, var(--zw-gold) 55%, transparent),
    0 6px 16px rgba(44, 36, 22, 0.14);
}
.cell .mark {
  position: absolute;
  top: 6px;
  right: 6px;
  font-style: normal;
  font-size: 0.65rem;
  letter-spacing: 0.08em;
  padding: 1px 5px;
  border-radius: 999px;
  color: var(--zw-ink);
  background: var(--zw-gold);
  line-height: 1.4;
}
.outcome {
  padding: 0.95rem 1rem;
  border-radius: 10px;
  border: 1px solid var(--zw-line);
}
.outcome.is-ji {
  border-color: color-mix(in srgb, #2d6a4f 45%, var(--zw-line));
  background: color-mix(in srgb, #2d6a4f 8%, var(--zw-paper));
}
.outcome.is-xiong {
  border-color: color-mix(in srgb, #8a2f2f 40%, var(--zw-line));
  background: color-mix(in srgb, #8a2f2f 7%, var(--zw-paper));
}
.outcome.muted {
  opacity: 0.88;
}
.badge {
  margin: 0 0 0.35rem;
  font-size: 1.1rem;
  letter-spacing: 0.16em;
  color: var(--zw-primary);
  font-weight: 600;
}
.summary {
  margin: 0;
  line-height: 1.7;
  font-size: 0.95rem;
}
.trace {
  margin: 0.55rem 0 0;
  font-size: 0.8rem;
  color: var(--zw-muted);
  letter-spacing: 0.04em;
}
.ai-panel {
  margin-top: 1rem;
  padding-top: 1rem;
  border-top: 1px dashed var(--zw-line);
}
.ai-panel h3 {
  margin: 0 0 0.45rem;
  font-size: 0.95rem;
  letter-spacing: 0.14em;
  color: var(--zw-primary);
}
.ai-hint {
  margin: 0 0 0.65rem;
  font-size: 0.78rem;
  line-height: 1.55;
  color: var(--zw-muted);
}
.ai-field-hint {
  margin: 0.35rem 0 0;
  font-size: 0.68rem;
  line-height: 1.45;
  color: #8a2f2f;
  letter-spacing: 0.02em;
}
.ai-panel :deep(.is-empty-hint .el-textarea__inner) {
  border-color: color-mix(in srgb, #8a2f2f 55%, var(--zw-line));
}
.ai-actions {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 0.5rem 0.75rem;
  margin: 0.65rem 0 0.35rem;
}
.ai-wait-hint {
  margin: 0;
  flex: 1 1 10rem;
  font-size: 0.68rem;
  line-height: 1.55;
  color: color-mix(in srgb, var(--zw-muted) 78%, transparent);
  letter-spacing: 0.02em;
  opacity: 0.92;
}
.ai-wait-hint.is-loading {
  margin-top: 0.35rem;
  font-size: 0.72rem;
  color: color-mix(in srgb, var(--zw-primary) 70%, var(--zw-muted));
  opacity: 1;
}
.ai-error {
  margin: 0.5rem 0 0;
  font-size: 0.85rem;
  color: #8a2f2f;
  line-height: 1.5;
}
.ai-body {
  margin: 0.75rem 0 0;
  padding: 0.85rem 0.95rem;
  border-radius: 8px;
  border: 1px solid var(--zw-line);
  background: color-mix(in srgb, var(--zw-bg) 35%, var(--zw-paper));
  white-space: pre-wrap;
  word-break: break-word;
  font-family: inherit;
  font-size: 0.88rem;
  line-height: 1.75;
  color: var(--zw-ink);
}
.guide ul,
.guide ol {
  margin: 0 0 0.35rem;
  padding-left: 1.2rem;
  line-height: 1.75;
}
.example {
  margin-top: 0.65rem;
  padding-top: 0.55rem;
  border-top: 1px dashed var(--zw-line);
}
.example strong {
  display: block;
  margin-bottom: 0.25rem;
  color: var(--zw-gold);
  letter-spacing: 0.12em;
}
.example p {
  margin: 0;
  line-height: 1.7;
  font-size: 0.92rem;
}
@media (max-width: 720px) {
  .fields {
    grid-template-columns: 1fr;
  }
  .cast-visual {
    grid-template-columns: 1fr;
  }
  .palm {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }
}
</style>
