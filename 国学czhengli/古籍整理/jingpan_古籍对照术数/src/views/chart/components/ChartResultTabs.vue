<template>
  <section ref="tabsRootRef" class="result-tabs rounded-lg border mt-4" :style="panelStyle">
    <el-tabs v-model="activeTab">
      <el-tab-pane :label="display('命盤解讀', false)" name="reading">
        <p class="note">
          {{
            display(
              '古文摘自國學典籍網《紫微斗數全書》卷一；其下白話只譯該句，不另造斷語。每宮先列三方四正，再對本宮星曜、四化選句。點出處核對原文。',
              false,
            )
          }}
        </p>
        <div class="method-box">
          <p class="classic">{{ display(sanFangDef.classic) }}</p>
          <p class="vernacular">{{ display(sanFangDef.vernacular, false) }}</p>
          <p class="cites">
            <a :href="sanFangDef.cite.url" target="_blank" rel="noopener noreferrer">{{ display(sanFangDef.cite.title, false) }}</a>
            <button v-if="sanFangDef.cite.bookId" type="button" @click="$emit('goto', sanFangDef.cite.bookId)">
              {{ display('站內原文', false) }}
            </button>
          </p>
          <p class="classic">{{ display(sanFangBaike.classic) }}</p>
          <p class="vernacular">{{ display(sanFangBaike.vernacular, false) }}</p>
          <p class="cites">
            <a :href="sanFangBaike.cite.url" target="_blank" rel="noopener noreferrer">{{ display(sanFangBaike.cite.title, false) }}</a>
          </p>
        </div>
        <ChartLegend class="mb-4" />
        <article v-for="item in readings" :key="item.name + item.earthlyBranch" class="palace-card">
          <header class="palace-head">
            <h3>
              {{ display(item.aliasName, false) }}
              <small>{{ item.heavenlyStem }}{{ item.earthlyBranch }}</small>
              <span v-if="item.isBodyPalace" class="tag">{{ display('身宮', false) }}</span>
            </h3>
            <p class="meta">{{ display('本宮星曜', false) }}　{{ display(item.starLine, false) }}</p>
            <p v-if="item.mutagenLine" class="meta">{{ display('本宮四化', false) }}　{{ display(item.mutagenLine, false) }}</p>
            <p class="meta sanfang">
              {{ display('三方四正', false) }}　
              {{ display('本宮', false) }} {{ display(item.sanFang.self, false) }}　
              {{ display('對宮', false) }} {{ display(item.sanFang.opposite, false) }}　
              {{ display('三合', false) }} {{ display(item.sanFang.triA, false) }}　
              {{ display(item.sanFang.triB, false) }}
            </p>
          </header>
          <ol v-if="item.quotes.length" class="quotes">
            <li v-for="(q, idx) in item.quotes" :key="idx">
              <p class="classic">{{ display(q.classic) }}</p>
              <p class="vernacular">{{ display(q.vernacular, false) }}</p>
              <p class="cites">
                <a :href="q.cite.url" target="_blank" rel="noopener noreferrer">{{ display(q.cite.title, false) }}</a>
                <button v-if="q.cite.bookId" type="button" @click="$emit('goto', q.cite.bookId)">
                  {{ display('站內原文', false) }}
                </button>
              </p>
            </li>
          </ol>
          <p v-else class="note">
            {{ display('本宮暫無對應卷一選句。請點盤上星曜，查看《諸星問答論》原文。', false) }}
          </p>
        </article>
      </el-tab-pane>

      <el-tab-pane :label="display('AI 解讀', false)" name="ai">
        <p class="note ai-disclaimer">
          {{
            display(
              '以下为盘面逻辑推演（全息诊断），语气偏硬，仅供参考，不作唯一决策依据。请点「命盘解读」「古籍原文」核对站内出处。',
              false,
            )
          }}
        </p>
        <p v-if="!aiConfigured" class="note">
          {{ display('AI 解讀服務尚未配置，暫不可用。', false) }}
        </p>
        <template v-else>
          <div class="ai-timeline">
            <p class="note ai-timeline-hint">
              {{ display('選填：過往 1～2 件大事（年份 + 事件），用於驗盤；不填則跳過驗盤段。', false) }}
            </p>
            <div v-for="(row, idx) in timelineRows" :key="idx" class="ai-timeline-row">
              <el-input-number
                v-model="row.year"
                :min="1900"
                :max="2100"
                :controls="false"
                :disabled="aiLoading"
                class="ai-year"
                placeholder="年份"
              />
              <el-input
                v-model="row.event"
                :disabled="aiLoading"
                maxlength="80"
                clearable
                class="ai-event"
                :placeholder="display('事件简述，如结婚/升迁/破财', false)"
              />
            </div>
          </div>

          <div v-if="!aiContent && !aiLoading" class="ai-actions">
            <el-button type="primary" :disabled="aiLoading" @click="emitGenerate">
              {{ display('生成全息診斷', false) }}
            </el-button>
            <span class="ai-wait-hint">
              {{ display('生成較耗時（約一至兩分鐘），請稍候，勿切換或離開本頁。', false) }}
            </span>
          </div>
          <div v-if="aiLoading && !aiContent" class="ai-loading">
            <el-icon class="is-loading"><Loading /></el-icon>
            <span>{{ display('正在整理本盤材料，請耐心等待，勿關閉或切換頁面…', false) }}</span>
          </div>
          <p v-if="aiError" class="ai-error">{{ aiError }}</p>
          <div v-if="aiError && !aiLoading" class="ai-actions">
            <el-button type="primary" plain @click="emitGenerate">
              {{ display('重試', false) }}
            </el-button>
            <span class="ai-wait-hint">
              {{ display('生成較耗時（約一至兩分鐘），請稍候，勿切換或離開本頁。', false) }}
            </span>
          </div>
          <article v-if="aiContent" class="ai-result">
            <div class="ai-toolbar">
              <span class="ai-mode-tag">{{ display('全息診斷', false) }}</span>
              <el-button size="small" plain @click="copyAi">{{ display('複製全文', false) }}</el-button>
              <el-button size="small" plain :disabled="aiLoading" @click="emitGenerate">
                {{ display('重新生成', false) }}
              </el-button>
              <span v-if="!aiLoading" class="ai-wait-hint">
                {{ display('重新生成約需一至兩分鐘，請勿切換頁面。', false) }}
              </span>
            </div>
            <div v-if="aiLoading" class="ai-loading compact">
              <el-icon class="is-loading"><Loading /></el-icon>
              <span>{{ display('正在重新生成，請稍候，勿離開本頁…', false) }}</span>
            </div>
            <div class="ai-body ai-md" v-html="aiHtml" />
          </article>
        </template>
      </el-tab-pane>

      <el-tab-pane :label="display('命盤格局', false)" name="pattern">
        <p v-if="!patterns.length" class="note">
          {{ display('本盤未匹配到卷一格局歌訣。格局只錄古本原句，不另作白話。', false) }}
        </p>
        <article v-for="p in patterns" :key="p.name" class="mb-4">
          <h4 style="color: var(--zw-gold)">{{ display(p.name, false) }}</h4>
          <p class="text-sm" style="color: var(--zw-muted)">{{ display(p.condition) }}</p>
          <div class="song-card">{{ formatSong(display(p.originalText)) }}</div>
        </article>
      </el-tab-pane>

      <el-tab-pane :label="display('古籍原文', false)" name="excerpt">
        <ExcerptPanel :items="excerpts" @goto="$emit('goto', $event)" />
      </el-tab-pane>
    </el-tabs>
  </section>
</template>

<script lang="ts">
import { computed, defineComponent, reactive, ref, type PropType } from 'vue';
import { Loading } from '@element-plus/icons-vue';
import type { ExcerptItem, MatchedPattern, PalaceReading } from '@/types';
import { useDisplayText } from '@/composables/useDisplayText';
import { useCenterScrollTabs } from '@/composables/useCenterScrollTabs';
import { copyText } from '@/utils/copy';
import { renderSimpleMarkdown } from '@/utils/simpleMarkdown';
import ChartLegend from './ChartLegend.vue';
import ExcerptPanel from './ExcerptPanel.vue';
import { SANFANG_BAIKE, SANFANG_DEF, toReadingQuote } from '@/data/readingQuotes';

export default defineComponent({
  name: 'ChartResultTabs',
  components: { ChartLegend, ExcerptPanel, Loading },
  props: {
    readings: { type: Array as PropType<PalaceReading[]>, default: () => [] },
    patterns: { type: Array as PropType<MatchedPattern[]>, default: () => [] },
    excerpts: { type: Array as PropType<ExcerptItem[]>, default: () => [] },
    aiLoading: { type: Boolean, default: false },
    aiError: { type: String, default: '' },
    aiContent: { type: String, default: '' },
    aiConfigured: { type: Boolean, default: false },
  },
  emits: {
    goto: (_id: string) => true,
    'generate-ai': (_payload: { timeline: Array<{ year: number; event: string }> }) => true,
  },
  setup(props, { emit }) {
    const { display } = useDisplayText();
    const activeTab = ref('reading');
    const tabsRootRef = ref<HTMLElement>();
    const tabNames = ['reading', 'ai', 'pattern', 'excerpt'] as const;
    useCenterScrollTabs(tabsRootRef, activeTab, tabNames);

    const timelineRows = reactive([
      { year: undefined as number | undefined, event: '' },
      { year: undefined as number | undefined, event: '' },
    ]);

    const aiHtml = computed(() => renderSimpleMarkdown(display(props.aiContent, false)));

    const panelStyle = {
      background: 'var(--zw-paper)',
      borderColor: 'var(--zw-line)',
      padding: '12px 16px 16px',
    };
    const formatSong = (text: string) =>
      text
        .split(/[，,]/)
        .map((s) => s.trim())
        .filter(Boolean)
        .join('\n');
    const copyAi = () => {
      void copyText(props.aiContent);
    };
    const emitGenerate = () => {
      const timeline = timelineRows
        .filter((r) => typeof r.year === 'number' && r.event.trim())
        .slice(0, 2)
        .map((r) => ({ year: r.year as number, event: r.event.trim() }));
      emit('generate-ai', { timeline });
    };
    return {
      display,
      activeTab,
      tabsRootRef,
      panelStyle,
      formatSong,
      copyAi,
      timelineRows,
      emitGenerate,
      aiHtml,
      sanFangDef: toReadingQuote(SANFANG_DEF),
      sanFangBaike: toReadingQuote(SANFANG_BAIKE),
    };
  },
});
</script>

<style scoped>
.note {
  font-size: 0.75em;
  color: var(--zw-muted);
  line-height: 1.7;
  margin-bottom: 12px;
}
.method-box {
  border: 1px solid var(--zw-line);
  background: var(--zw-quote);
  padding: 12px 14px;
  margin-bottom: 14px;
}
.palace-card {
  border-top: 1px solid var(--zw-line);
  padding: 16px 0;
}
.palace-head h3 {
  font-size: 1em;
  margin-bottom: 6px;
}
.palace-head small {
  margin-left: 8px;
  color: var(--zw-muted);
  font-weight: 400;
}
.tag {
  margin-left: 8px;
  font-size: 0.7em;
  color: var(--zw-gold);
}
.meta {
  font-size: 0.75em;
  color: var(--zw-muted);
  line-height: 1.7;
}
.sanfang {
  color: var(--zw-primary);
}
.quotes {
  margin: 10px 0 0;
  padding: 0;
  list-style: none;
}
.quotes li {
  margin-bottom: 12px;
}
.classic {
  font-size: 0.9em;
  line-height: 1.8;
}
.vernacular {
  margin-top: 4px;
  font-size: 0.85em;
  color: var(--zw-muted);
  line-height: 1.7;
}
.cites {
  margin-top: 4px;
  font-size: 0.75em;
  display: flex;
  gap: 12px;
  flex-wrap: wrap;
}
.cites a,
.cites button {
  color: var(--zw-gold);
  background: none;
  border: 0;
  padding: 0;
  cursor: pointer;
  font-family: inherit;
  font-size: inherit;
  text-decoration: underline;
}
.result-tabs :deep(.excerpt-panel) {
  border: 0;
  padding: 0;
}
.result-tabs :deep(.el-tabs__item) {
  color: var(--zw-muted);
}
.result-tabs :deep(.el-tabs__item.is-active) {
  color: var(--zw-primary);
}
.result-tabs :deep(.el-tabs__active-bar) {
  background: var(--zw-gold);
}
.ai-disclaimer {
  border-left: 3px solid var(--zw-gold);
  padding-left: 10px;
}
.ai-timeline {
  margin-bottom: 14px;
  padding: 10px 12px;
  border: 1px solid var(--zw-line);
  background: var(--zw-quote);
}
.ai-timeline-hint {
  margin-bottom: 8px;
}
.ai-timeline-row {
  display: flex;
  gap: 8px;
  margin-bottom: 8px;
}
.ai-timeline-row:last-child {
  margin-bottom: 0;
}
.ai-year {
  width: 6.5rem;
  flex: 0 0 auto;
}
.ai-event {
  flex: 1 1 auto;
}
.ai-mode-tag {
  font-size: 0.75em;
  color: var(--zw-gold);
  border: 1px solid var(--zw-gold);
  padding: 2px 8px;
  margin-right: 4px;
}
.ai-actions {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 8px 12px;
  margin-bottom: 12px;
}
.ai-wait-hint {
  flex: 1 1 10rem;
  font-size: 0.68em;
  line-height: 1.55;
  color: color-mix(in srgb, var(--zw-muted) 78%, transparent);
  letter-spacing: 0.02em;
  opacity: 0.92;
}
.ai-loading {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 0.85em;
  color: var(--zw-muted);
  margin-bottom: 12px;
}
.ai-loading.compact {
  margin-top: 0;
  margin-bottom: 10px;
}
.ai-error {
  font-size: 0.85em;
  color: #b42318;
  margin-bottom: 12px;
  line-height: 1.7;
}
.ai-result {
  margin-top: 8px;
}
.ai-toolbar {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
  align-items: center;
  margin-bottom: 12px;
}
.ai-body {
  margin: 0;
  white-space: pre-wrap;
  word-break: break-word;
  font-family: inherit;
  font-size: 0.9em;
  line-height: 1.85;
  color: var(--zw-primary);
  background: var(--zw-quote);
  border: 1px solid var(--zw-line);
  padding: 14px 16px;
}
.ai-md {
  white-space: normal;
}
.ai-md :deep(h2) {
  font-size: 1.05em;
  margin: 1.1em 0 0.45em;
  color: var(--zw-gold);
  font-weight: 600;
}
.ai-md :deep(h2:first-child) {
  margin-top: 0;
}
.ai-md :deep(h3) {
  font-size: 0.98em;
  margin: 0.85em 0 0.35em;
  font-weight: 600;
}
.ai-md :deep(p) {
  margin: 0.35em 0;
}
.ai-md :deep(ul),
.ai-md :deep(ol) {
  margin: 0.35em 0 0.55em;
  padding-left: 1.35em;
}
.ai-md :deep(li) {
  margin: 0.2em 0;
}
.ai-md :deep(strong) {
  font-weight: 600;
  color: var(--zw-primary);
}
.ai-md :deep(em) {
  font-style: normal;
  color: var(--zw-muted);
}
.ai-md :deep(code) {
  font-size: 0.92em;
  background: color-mix(in srgb, var(--zw-line) 55%, transparent);
  padding: 0.05em 0.3em;
}
</style>
