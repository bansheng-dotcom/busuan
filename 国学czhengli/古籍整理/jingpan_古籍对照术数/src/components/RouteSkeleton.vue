<template>
  <div class="route-skeleton-shell" :class="`sk-${type}`" aria-hidden="true">
    <!-- 首页：H5 英雄+快捷格；PC 英雄全宽 -->
    <template v-if="type === 'home'">
      <div class="sk-home-hero">
        <div class="sk-block sk-brand" />
        <div class="sk-block sk-title sk-title--wide" />
        <div class="sk-block sk-line sk-line--60" />
        <div class="sk-cta-row">
          <div class="sk-block sk-cta" />
          <div class="sk-block sk-cta sk-cta--ghost" />
        </div>
      </div>
      <div class="sk-home-quick">
        <div v-for="i in 6" :key="i" class="sk-block sk-quick" />
      </div>
    </template>

    <!-- 排盘首屏：双 Tab + 生辰表单卡 + 提示卡（未排盘时无盘面） -->
    <template v-else-if="type === 'chart'">
      <div class="sk-tabs">
        <div class="sk-block sk-tab sk-tab--on" />
        <div class="sk-block sk-tab" />
      </div>
      <div class="sk-chart-layout">
        <div class="sk-form-card sk-form-card--chart">
          <div class="sk-block sk-title sk-title--md" />
          <div class="sk-block sk-label" />
          <div class="sk-seg">
            <div class="sk-block sk-seg-item" />
            <div class="sk-block sk-seg-item" />
          </div>
          <div class="sk-block sk-field" />
          <div class="sk-block sk-line sk-line--55" />
          <div class="sk-row-between">
            <div class="sk-block sk-label" />
            <div class="sk-block sk-switch" />
          </div>
          <div class="sk-block sk-line sk-line--90" />
          <div class="sk-block sk-line sk-line--80" />
          <div class="sk-block sk-label" />
          <div class="sk-block sk-field" />
          <div class="sk-block sk-label" />
          <div class="sk-radio-row">
            <div class="sk-block sk-radio" />
            <div class="sk-block sk-radio" />
          </div>
          <div class="sk-btn-row">
            <div class="sk-block sk-btn sk-btn--primary" />
            <div class="sk-block sk-btn sk-btn--ghost" />
          </div>
        </div>
        <div class="sk-hint-card">
          <div class="sk-block sk-line sk-line--92" />
          <div class="sk-block sk-line sk-line--88" />
          <div class="sk-block sk-line sk-line--85" />
          <div class="sk-block sk-line sk-line--72" />
        </div>
      </div>
    </template>

    <!-- 古籍：工具条 + 正文 -->
    <template v-else-if="type === 'book'">
      <div class="sk-toolbar">
        <div class="sk-block sk-chip" />
        <div class="sk-block sk-chip" />
        <div class="sk-block sk-chip" />
      </div>
      <div class="sk-book-body">
        <div class="sk-block sk-toc sk-toc--pc" />
        <div class="sk-block sk-reader">
          <div class="sk-block sk-title sk-title--md" />
          <div class="sk-block sk-line" />
          <div class="sk-block sk-line sk-line--90" />
          <div class="sk-block sk-line sk-line--80" />
          <div class="sk-block sk-line sk-line--95" />
          <div class="sk-block sk-line sk-line--70" />
          <div class="sk-block sk-line sk-line--85" />
        </div>
      </div>
    </template>

    <!-- 易经列表 -->
    <template v-else-if="type === 'yijing'">
      <header class="sk-page-head">
        <div class="sk-block sk-title sk-title--page" />
        <div class="sk-block sk-lead" />
      </header>
      <div class="sk-panel sk-intro-card">
        <div class="sk-block sk-title sk-title--section" />
        <div class="sk-block sk-line" />
        <div class="sk-block sk-line sk-line--90" />
        <div class="sk-block sk-line sk-line--75" />
      </div>
      <div class="sk-list-head">
        <div>
          <div class="sk-block sk-title sk-title--section" />
          <div class="sk-block sk-line sk-line--55" />
        </div>
        <div class="sk-block sk-field sk-field--sm" />
      </div>
      <div class="sk-block sk-sec-label" />
      <div class="sk-gua-grid">
        <div v-for="i in 6" :key="`u-${i}`" class="sk-block sk-gua" />
      </div>
      <div class="sk-block sk-sec-label" />
      <div class="sk-gua-grid sk-gua-grid--tail">
        <div v-for="i in 6" :key="`l-${i}`" class="sk-block sk-gua" />
      </div>
    </template>

    <!-- 易经详 / 星曜详：返回 + 单篇 -->
    <template v-else-if="type === 'yijing-detail' || type === 'star-dict-detail'">
      <div class="sk-block sk-back" />
      <div class="sk-block sk-prose-card">
        <div class="sk-block sk-title sk-title--md" />
        <div class="sk-block sk-hero sk-hero--sm" />
        <div class="sk-block sk-line" />
        <div class="sk-block sk-line sk-line--90" />
        <div class="sk-block sk-line sk-line--80" />
        <div class="sk-block sk-line sk-line--70" />
      </div>
    </template>

    <!-- 星曜词典 / 格局词典 -->
    <template v-else-if="type === 'star-dict' || type === 'pattern-dict'">
      <div class="sk-block sk-title" />
      <div class="sk-block sk-line sk-line--65" />
      <div class="sk-section-label" />
      <div class="sk-dict-grid" :class="{ 'sk-dict-grid--pattern': type === 'pattern-dict' }">
        <div v-for="i in cardCount" :key="i" class="sk-block sk-dict-card" />
      </div>
    </template>

    <!-- 罗盘 -->
    <template v-else-if="type === 'luopan'">
      <div class="sk-block sk-title" />
      <div class="sk-block sk-line sk-line--60" />
      <div class="sk-luopan-wrap">
        <div class="sk-block sk-disk" />
      </div>
      <div class="sk-block sk-readout" />
      <div class="sk-block sk-panel" />
    </template>

    <!-- 黄历 -->
    <template v-else-if="type === 'almanac'">
      <div class="sk-block sk-title sk-title--center" />
      <div class="sk-date-nav">
        <div class="sk-block sk-nav-btn" />
        <div class="sk-block sk-date" />
        <div class="sk-block sk-nav-btn" />
      </div>
      <div class="sk-block sk-day-sheet">
        <div class="sk-block sk-line sk-line--50" />
        <div class="sk-pillars">
          <div v-for="i in 4" :key="i" class="sk-block sk-pillar" />
        </div>
        <div class="sk-yi-ji">
          <div class="sk-block sk-half" />
          <div class="sk-block sk-half" />
        </div>
      </div>
    </template>

    <!-- 起名：标题 + 表单 + 脚注（首屏无结果区） -->
    <template v-else-if="type === 'naming'">
      <header class="sk-page-head">
        <div class="sk-block sk-title sk-title--page" />
        <div class="sk-block sk-lead" />
      </header>
      <div class="sk-form-card sk-form-card--naming">
        <div class="sk-block sk-label" />
        <div class="sk-block sk-field" />
        <div class="sk-row-between">
          <div class="sk-block sk-label" />
          <div class="sk-block sk-switch" />
        </div>
        <div class="sk-block sk-hint-lines" />
        <div class="sk-block sk-label" />
        <div class="sk-block sk-field" />
        <div class="sk-block sk-label" />
        <div class="sk-block sk-field" />
        <div class="sk-block sk-label" />
        <div class="sk-block sk-field" />
        <div class="sk-block sk-btn sk-btn--full" />
      </div>
      <div class="sk-block sk-foot-note" />
    </template>

    <!-- 六壬：起课 panel + 说明 panel -->
    <template v-else-if="type === 'liuren'">
      <header class="sk-page-head">
        <div class="sk-block sk-title sk-title--page" />
        <div class="sk-block sk-lead" />
      </header>
      <div class="sk-panel sk-liuren-cast">
        <div class="sk-block sk-title sk-title--section" />
        <div class="sk-block sk-line sk-line--85" />
        <div class="sk-fields-row">
          <div class="sk-block sk-field" />
          <div class="sk-block sk-field" />
          <div class="sk-block sk-field" />
        </div>
        <div class="sk-btn-row sk-btn-row--left">
          <div class="sk-block sk-btn sk-btn--sm" />
          <div class="sk-block sk-btn sk-btn--sm sk-btn--ghost" />
          <div class="sk-block sk-btn sk-btn--sm sk-btn--ghost" />
        </div>
        <div class="sk-cast-visual">
          <div class="sk-block sk-hand" />
          <div class="sk-palm-grid">
            <div v-for="i in 6" :key="i" class="sk-block sk-palm-cell" />
          </div>
        </div>
        <div class="sk-outcome">
          <div class="sk-block sk-line sk-line--35" />
          <div class="sk-block sk-line sk-line--90" />
          <div class="sk-block sk-line sk-line--55" />
        </div>
      </div>
      <div class="sk-panel sk-liuren-guide">
        <div class="sk-block sk-title sk-title--section" />
        <div class="sk-block sk-line" />
        <div class="sk-block sk-line sk-line--85" />
        <div class="sk-block sk-line sk-line--70" />
        <div class="sk-block sk-title sk-title--section sk-title--spaced" />
        <div class="sk-block sk-line sk-line--80" />
        <div class="sk-block sk-title sk-title--section sk-title--spaced" />
        <div class="sk-block sk-line sk-line--90" />
        <div class="sk-block sk-line sk-line--75" />
      </div>
    </template>

    <!-- 摇卦：stage panel（首屏无爻象/结果） -->
    <template v-else-if="type === 'yaogua'">
      <header class="sk-page-head">
        <div class="sk-block sk-title sk-title--page" />
        <div class="sk-block sk-lead" />
      </header>
      <div class="sk-panel sk-yaogua-stage">
        <div class="sk-mode-row">
          <div class="sk-block sk-line sk-line--30" />
          <div class="sk-block sk-switch" />
          <div class="sk-block sk-line sk-line--55" />
        </div>
        <div class="sk-block sk-step" />
        <div class="sk-block sk-coin-arena" />
        <div class="sk-block sk-coin-legend" />
        <div class="sk-btn-row sk-btn-row--center">
          <div class="sk-block sk-btn sk-btn--sm" />
          <div class="sk-block sk-btn sk-btn--sm sk-btn--ghost" />
        </div>
      </div>
    </template>

    <!-- 关于 -->
    <template v-else>
      <div class="sk-block sk-prose-card sk-prose-card--about">
        <div class="sk-block sk-title sk-title--md" />
        <div class="sk-block sk-line" />
        <div class="sk-block sk-line sk-line--90" />
        <div class="sk-block sk-line sk-line--80" />
        <div class="sk-block sk-line sk-line--95" />
        <div class="sk-block sk-line sk-line--70" />
        <div class="sk-block sk-line sk-line--85" />
        <div class="sk-block sk-line sk-line--60" />
      </div>
    </template>
  </div>
</template>

<script lang="ts">
import { computed, defineComponent, type PropType } from 'vue';
import type { SkeletonType } from '@/composables/useRouteLoading';

export default defineComponent({
  name: 'RouteSkeleton',
  props: {
    type: {
      type: String as PropType<SkeletonType>,
      default: 'home',
    },
  },
  setup(props) {
    const cardCount = computed(() => (props.type === 'pattern-dict' ? 4 : 6));
    return { cardCount };
  },
});
</script>

<style scoped>
/* 外壳 padding / min-height 见 src/styles/skeleton.css */

.sk-block {
  border-radius: 6px;
  background: color-mix(in srgb, var(--zw-ink, #2a2620) 8%, transparent);
}

/* —— 通用页头（h1 + lead） —— */
.sk-page-head {
  margin-bottom: 1.25rem;
}
.sk-title--page {
  height: 1.55rem;
  width: 34%;
  margin: 0 0 0.4rem;
}
.sk-lead {
  height: 4.85rem;
  width: min(100%, 42rem);
  margin: 0;
  border-radius: 6px;
}
.sk-title {
  height: 1.35rem;
  width: 30%;
  margin-bottom: 0.85rem;
}
.sk-title--section {
  width: 38%;
  height: 1rem;
  margin: 0 0 0.65rem;
}
.sk-title--section.sk-title--spaced {
  margin-top: 1.15rem;
}
.sk-title--md {
  width: 42%;
  height: 1.2rem;
  margin-bottom: 1rem;
}
.sk-title--wide {
  width: 72%;
  height: 1.6rem;
  margin-bottom: 0.65rem;
}
.sk-title--center {
  width: 36%;
  margin-left: auto;
  margin-right: auto;
}

.sk-line {
  height: 0.65rem;
  width: 95%;
  margin-bottom: 0.5rem;
  border-radius: 4px;
}
.sk-line--95 { width: 95%; }
.sk-line--92 { width: 92%; }
.sk-line--90 { width: 90%; }
.sk-line--88 { width: 88%; }
.sk-line--85 { width: 85%; }
.sk-line--80 { width: 80%; }
.sk-line--75 { width: 75%; }
.sk-line--72 { width: 72%; }
.sk-line--70 { width: 70%; }
.sk-line--65 { width: 65%; }
.sk-line--60 { width: 60%; }
.sk-line--55 { width: 55%; }
.sk-line--50 { width: 50%; }
.sk-line--35 { width: 35%; height: 1.1rem; margin-bottom: 0.35rem; }
.sk-line--30 { width: 30%; }

.sk-field {
  height: 2.375rem;
  margin-bottom: 0;
  border-radius: 8px;
}
.sk-field--sm {
  width: 7.5rem;
  flex: none;
}
.sk-btn {
  height: 2.375rem;
  width: 42%;
  border-radius: 8px;
}
.sk-btn--full {
  width: 100%;
  height: 2.625rem;
  margin-top: 0.15rem;
}
.sk-btn--sm {
  width: 5.5rem;
  height: 2.375rem;
}
.sk-back {
  height: 1.1rem;
  width: 4.5rem;
  margin-bottom: 1rem;
}
.sk-panel {
  padding: 1.1rem 1.15rem;
  margin-bottom: 1.15rem;
  border-radius: 12px;
  box-sizing: border-box;
  background: color-mix(in srgb, var(--zw-ink, #2a2620) 4%, transparent);
  border: 1px solid color-mix(in srgb, var(--zw-ink, #2a2620) 8%, transparent);
}
.sk-panel .sk-block {
  background: color-mix(in srgb, var(--zw-ink, #2a2620) 10%, transparent);
}

/* —— 首页 —— */
.sk-home-hero {
  padding: 108px 18px 36px;
}
.sk-brand {
  height: 0.85rem;
  width: 3rem;
  margin-bottom: 0.75rem;
}
.sk-cta-row {
  display: flex;
  gap: 0.65rem;
  margin-top: 1rem;
}
.sk-cta {
  height: 2.75rem;
  width: 7.5rem;
  border-radius: 8px;
}
.sk-cta--ghost {
  opacity: 0.65;
}
.sk-home-quick {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 8px;
  margin-top: 8px;
  padding: 16px 14px 18px;
}
.sk-quick {
  height: 3.4rem;
  border-radius: 8px;
}

@media (min-width: 768px) {
  .sk-home-hero {
    min-height: calc(100vh - 64px);
    padding: 8vh 6vw 10vh;
    display: flex;
    flex-direction: column;
    justify-content: center;
  }
  .sk-home-quick {
    display: none;
  }
}

/* —— 排盘：表单卡高度贴近真实 H5 表单 —— */
.sk-tabs {
  display: flex;
  gap: 1.25rem;
  margin-bottom: 14px;
  padding-bottom: 10px;
  border-bottom: 1px solid color-mix(in srgb, var(--zw-ink, #2a2620) 10%, transparent);
  min-height: 2.2rem;
}
.sk-tab {
  height: 1.15rem;
  width: 4.2rem;
  border-radius: 3px;
}
.sk-tab--on {
  width: 4.6rem;
  background: color-mix(in srgb, var(--zw-ink, #2a2620) 16%, transparent);
}
.sk-chart-layout {
  display: grid;
  gap: 14px;
}
.sk-form-card {
  padding: 14px 14px 16px;
  border-radius: 10px;
  background: color-mix(in srgb, var(--zw-ink, #2a2620) 4%, transparent);
  border: 1px solid color-mix(in srgb, var(--zw-ink, #2a2620) 8%, transparent);
  box-sizing: border-box;
}
.sk-form-card--chart {
  display: flex;
  flex-direction: column;
  gap: 0;
}
.sk-form-card--chart .sk-field,
.sk-form-card--chart .sk-btn,
.sk-form-card--chart .sk-label,
.sk-form-card--chart .sk-seg-item,
.sk-form-card--chart .sk-switch,
.sk-form-card--chart .sk-radio,
.sk-form-card--chart .sk-line,
.sk-form-card--chart .sk-title {
  background: color-mix(in srgb, var(--zw-ink, #2a2620) 10%, transparent);
}
.sk-form-card--naming {
  display: flex;
  flex-direction: column;
  gap: 0.85rem;
  padding: 1rem 1.1rem;
  border-radius: 12px;
}
.sk-form-card--naming .sk-block {
  background: color-mix(in srgb, var(--zw-ink, #2a2620) 10%, transparent);
}
.sk-hint-lines {
  height: 2.35rem;
  width: 100%;
  border-radius: 4px;
}
.sk-foot-note {
  height: 2.65rem;
  width: 100%;
  margin-top: 1.75rem;
  border-radius: 6px;
}
.sk-label {
  height: 0.75rem;
  width: 4rem;
  margin: 0.85rem 0 0.45rem;
  border-radius: 3px;
}
.sk-seg {
  display: flex;
  gap: 0;
  margin-bottom: 0.55rem;
  border-radius: 8px;
  overflow: hidden;
  width: 100%;
  max-width: 220px;
}
.sk-seg-item {
  height: 2.125rem;
  flex: 1;
  border-radius: 0;
}
.sk-row-between {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-top: 0.55rem;
  min-height: 1.6rem;
}
.sk-row-between .sk-label {
  margin: 0;
}
.sk-switch {
  height: 1.35rem;
  width: 2.6rem;
  border-radius: 999px;
}
.sk-radio-row {
  display: flex;
  gap: 1.25rem;
  margin: 0.45rem 0 1rem;
  min-height: 1.4rem;
}
.sk-radio {
  height: 1.15rem;
  width: 3.2rem;
  border-radius: 999px;
}
.sk-btn-row {
  display: flex;
  gap: 0.65rem;
  padding-top: 0.35rem;
}
.sk-btn-row--left {
  flex-wrap: wrap;
  margin: 0.9rem 0 1rem;
  padding-top: 0;
}
.sk-btn-row--center {
  justify-content: center;
  flex-wrap: wrap;
  margin-top: 0;
  padding-top: 0;
}
.sk-btn-row .sk-btn {
  flex: none;
  width: auto;
  margin-top: 0;
}
.sk-btn-row:not(.sk-btn-row--left):not(.sk-btn-row--center) .sk-btn {
  flex: 1;
  height: 2.375rem;
}
.sk-btn--primary {
  background: color-mix(in srgb, var(--zw-ink, #2a2620) 18%, transparent) !important;
}
.sk-btn--ghost {
  background: color-mix(in srgb, var(--zw-ink, #2a2620) 7%, transparent) !important;
}
.sk-hint-card {
  padding: 2rem 1.25rem;
  border-radius: 10px;
  box-sizing: border-box;
  display: flex;
  flex-direction: column;
  justify-content: center;
  gap: 0.55rem;
  background: color-mix(in srgb, var(--zw-ink, #2a2620) 4%, transparent);
  border: 1px solid color-mix(in srgb, var(--zw-ink, #2a2620) 8%, transparent);
}
.sk-hint-card .sk-line {
  height: 0.72rem;
  background: color-mix(in srgb, var(--zw-ink, #2a2620) 10%, transparent);
  margin-left: auto;
  margin-right: auto;
  margin-bottom: 0;
}

@media (min-width: 1100px) {
  .sk-chart-layout {
    grid-template-columns: minmax(280px, 360px) 1fr;
    align-items: start;
  }
  .sk-form-card--chart {
    padding: 16px;
  }
}

/* —— 古籍：阅读区撑满可视高度 —— */
.sk-toolbar {
  display: flex;
  gap: 0.5rem;
  margin-bottom: 1rem;
  min-height: 1.7rem;
}
.sk-chip {
  height: 1.7rem;
  width: 3.8rem;
  border-radius: 999px;
}
.sk-book-body {
  display: grid;
  gap: 0.85rem;
}
.sk-toc {
  display: none;
  height: 16rem;
}
.sk-reader {
  padding: 1rem;
  min-height: 18rem;
  background: color-mix(in srgb, var(--zw-ink, #2a2620) 4%, transparent);
  border: 1px solid color-mix(in srgb, var(--zw-ink, #2a2620) 8%, transparent);
  border-radius: 8px;
  box-sizing: border-box;
}
.sk-reader .sk-line,
.sk-reader .sk-title {
  background: color-mix(in srgb, var(--zw-ink, #2a2620) 10%, transparent);
}

@media (min-width: 768px) {
  .sk-book-body {
    grid-template-columns: 180px 1fr;
  }
  .sk-toc--pc {
    display: block;
    min-height: 18rem;
  }
}

/* —— 易经列表 —— */
.sk-intro-card {
  margin-bottom: 1.75rem;
}
.sk-list-head {
  display: flex;
  flex-wrap: wrap;
  align-items: flex-end;
  justify-content: space-between;
  gap: 0.75rem 1.25rem;
  margin-bottom: 0.85rem;
}
.sk-sec-label {
  height: 0.82rem;
  width: 28%;
  margin: 1rem 0 0.55rem;
  border-radius: 4px;
}
.sk-gua-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 0.55rem;
}
.sk-gua-grid--tail {
  min-height: 42rem;
}
.sk-gua {
  height: 3.35rem;
  border-radius: 10px;
}
.sk-section-label {
  height: 0.75rem;
  width: 22%;
  margin: 1rem 0 0.65rem;
  border-radius: 4px;
  background: color-mix(in srgb, var(--zw-ink, #2a2620) 10%, transparent);
}
.sk-dict-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 0.65rem;
}
.sk-dict-grid--pattern {
  grid-template-columns: 1fr;
}
.sk-dict-card {
  height: 5rem;
  border-radius: 8px;
}

@media (min-width: 768px) {
  .sk-gua-grid {
    grid-template-columns: repeat(4, 1fr);
  }
  .sk-gua-grid--tail {
    min-height: 28rem;
  }
  .sk-dict-grid {
    grid-template-columns: repeat(3, 1fr);
  }
  .sk-dict-grid--pattern {
    grid-template-columns: repeat(2, 1fr);
  }
}

/* —— 详情正文 —— */
.sk-prose-card {
  padding: 1.25rem 1rem;
  border-radius: 8px;
  box-sizing: border-box;
  background: color-mix(in srgb, var(--zw-ink, #2a2620) 4%, transparent);
  border: 1px solid color-mix(in srgb, var(--zw-ink, #2a2620) 8%, transparent);
}
.sk-prose-card .sk-line,
.sk-prose-card .sk-title,
.sk-prose-card .sk-hero {
  background: color-mix(in srgb, var(--zw-ink, #2a2620) 10%, transparent);
}
.sk-prose-card--about {
  max-width: 42rem;
  min-height: 22rem;
}
.sk-hero {
  height: 6rem;
  margin-bottom: 0.85rem;
  border-radius: 8px;
}
.sk-hero--sm {
  height: 4.5rem;
}

/* —— 罗盘 —— */
.sk-luopan-wrap {
  display: flex;
  justify-content: center;
  margin: 1.25rem 0 1rem;
}
.sk-disk {
  width: min(72vw, 280px);
  height: min(72vw, 280px);
  border-radius: 50%;
}
.sk-readout {
  height: 1.5rem;
  width: 40%;
  margin: 0 auto 0.85rem;
}
.sk-panel {
  height: 5.5rem;
  border-radius: 8px;
}

/* —— 黄历 —— */
.sk-date-nav {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.65rem;
  margin: 1rem 0;
  min-height: 2.4rem;
}
.sk-nav-btn {
  height: 2.2rem;
  width: 4.5rem;
  border-radius: 999px;
}
.sk-date {
  height: 2.2rem;
  width: 8rem;
  border-radius: 8px;
}
.sk-day-sheet {
  padding: 1rem;
  border-radius: 10px;
  min-height: 16rem;
  box-sizing: border-box;
  background: color-mix(in srgb, var(--zw-ink, #2a2620) 4%, transparent);
  border: 1px solid color-mix(in srgb, var(--zw-ink, #2a2620) 8%, transparent);
}
.sk-day-sheet .sk-line,
.sk-day-sheet .sk-pillar,
.sk-day-sheet .sk-half {
  background: color-mix(in srgb, var(--zw-ink, #2a2620) 10%, transparent);
}
.sk-pillars {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 0.5rem;
  margin: 0.85rem 0;
}
.sk-pillar {
  height: 3.2rem;
  border-radius: 6px;
}
.sk-yi-ji {
  display: grid;
  gap: 0.5rem;
}
.sk-half {
  height: 3.5rem;
  border-radius: 6px;
}

@media (min-width: 768px) {
  .sk-pillars {
    grid-template-columns: repeat(4, 1fr);
  }
  .sk-yi-ji {
    grid-template-columns: 1fr 1fr;
  }
}

/* —— 六壬 —— */
.sk-fields-row {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 0.75rem;
  margin: 0.85rem 0 0;
}
.sk-cast-visual {
  display: grid;
  grid-template-columns: minmax(0, 280px) minmax(0, 1fr);
  gap: 1rem 1.25rem;
  align-items: start;
  margin: 1rem 0;
}
.sk-hand {
  width: min(100%, 280px);
  aspect-ratio: 320 / 380;
  margin: 0 auto;
  border-radius: 8px;
}
.sk-palm-grid {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 0.55rem;
}
.sk-palm-cell {
  height: 4.75rem;
  border-radius: 12px;
}
.sk-outcome {
  padding: 0.95rem 1rem;
  border-radius: 10px;
  border: 1px solid color-mix(in srgb, var(--zw-ink, #2a2620) 10%, transparent);
  display: flex;
  flex-direction: column;
  gap: 0.45rem;
}
.sk-outcome .sk-line {
  margin-bottom: 0;
}
.sk-liuren-guide .sk-line:last-child {
  margin-bottom: 0;
}

@media (max-width: 767.98px) {
  .sk-cast-visual {
    grid-template-columns: 1fr;
  }
  .sk-fields-row {
    grid-template-columns: 1fr;
  }
}

/* —— 摇卦 —— */
.sk-mode-row {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 0.55rem 0.75rem;
  margin-bottom: 0.85rem;
}
.sk-step {
  height: 0.9rem;
  width: 42%;
  margin: 0 auto 1rem;
  border-radius: 4px;
}
.sk-coin-arena {
  height: 200px;
  margin-bottom: 0.65rem;
  border-radius: 12px;
}
.sk-coin-legend {
  height: 2.45rem;
  width: 88%;
  margin: -0.35rem auto 1rem;
  border-radius: 4px;
}
</style>
