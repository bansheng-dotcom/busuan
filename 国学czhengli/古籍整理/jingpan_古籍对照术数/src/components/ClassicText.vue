<template>
  <article class="classic-prose">
    <template v-for="(block, idx) in blocks" :key="idx">
      <h3 v-if="block.type === 'heading'" :id="block.id" class="mt-6 mb-2 text-lg font-semibold">
        {{ display(block.text ?? '') }}
      </h3>
      <p v-else-if="block.type === 'label'" class="my-2 font-semibold">{{ display(block.text ?? '') }}</p>
      <blockquote v-else-if="block.type === 'quote'" class="quote-block">
        <ClassicSentences
          :text="block.text ?? ''"
          :chapter-id="chapterId"
          :show-vernacular="showVernacular"
        />
      </blockquote>
      <p v-else-if="block.type === 'song-label'" class="mt-3 font-semibold text-gold">
        {{ display(block.text ?? '') }}
      </p>
      <div v-else-if="block.type === 'song'" class="song-card">
        <ClassicSentences
          :text="formatSong(block.text ?? '')"
          :chapter-id="chapterId"
          :show-vernacular="showVernacular"
          multiline
        />
      </div>
      <div v-else-if="block.type === 'answer'" class="my-3">
        <ClassicSentences
          :text="block.text ?? ''"
          :chapter-id="chapterId"
          :show-vernacular="showVernacular"
          multiline
        />
      </div>
      <figure v-else-if="block.type === 'palace-chart'" class="palace-wrap">
        <figcaption v-if="block.title" class="palace-title">{{ display(block.title) }}</figcaption>
        <div class="palace-board" role="img" :aria-label="display(block.title ?? '十二宮圖', false)">
          <div
            v-for="item in palaceCells(block.palaces ?? {})"
            :key="item.branch"
            class="palace-cell"
            :class="`pos-${item.branch}`"
          >
            <span class="palace-text">{{ display(item.text) }}</span>
            <b>{{ item.branch }}</b>
          </div>
          <div class="palace-center">
            <strong>{{ display(block.title ?? '') }}</strong>
            <p v-if="block.note">{{ display(block.note) }}</p>
          </div>
        </div>
        <p class="palace-hint">{{ display(palaceHint(block.title), false) }}</p>
      </figure>
      <figure v-else-if="block.type === 'table'" class="table-wrap">
        <figcaption v-if="block.title" class="palace-title">{{ display(block.title) }}</figcaption>
        <div class="table-scroll">
          <table>
            <thead>
              <tr>
                <th v-for="h in block.headers ?? []" :key="h">{{ display(h) }}</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="(row, ri) in block.rows ?? []" :key="ri">
                <td v-for="(cell, ci) in row" :key="ci">{{ display(cell) }}</td>
              </tr>
            </tbody>
          </table>
        </div>
      </figure>
      <div v-else class="my-3">
        <ClassicSentences
          :text="block.text ?? ''"
          :chapter-id="chapterId"
          :show-vernacular="showVernacular"
          multiline
        />
      </div>
    </template>
  </article>
</template>

<script lang="ts">
import { defineComponent, type PropType } from 'vue';
import type { BookBlock } from '@/types';
import ClassicSentences from '@/components/ClassicSentences.vue';
import { useDisplayText } from '@/composables/useDisplayText';

const PALACE_POS = ['巳', '午', '未', '申', '酉', '戌', '亥', '子', '丑', '寅', '卯', '辰'];

export default defineComponent({
  name: 'ClassicText',
  components: { ClassicSentences },
  props: {
    blocks: {
      type: Array as PropType<BookBlock[]>,
      required: true,
    },
    chapterId: {
      type: String,
      default: '',
    },
    showVernacular: {
      type: Boolean,
      default: false,
    },
  },
  setup() {
    const { display } = useDisplayText();
    const formatSong = (text: string) =>
      text
        .replace(/歌曰：?/g, '')
        .split(/[，,]/)
        .map((s) => s.trim())
        .filter(Boolean)
        .join('\n');
    const palaceCells = (palaces: Record<string, string>) =>
      PALACE_POS.map((branch) => ({ branch, text: palaces[branch] ?? '' }));
    const WUXING = new Set(['水二局', '木三局', '金四局', '土五局', '火六局']);
    const palaceHint = (title?: string) => {
      if (title && WUXING.has(title)) {
        return '十二宮按原圖排位。日期由原圖上下兩行逐字對讀，不另補字。';
      }
      return '十二宮按原圖排位。盤中細字照錄底本，不另補寫。';
    };
    return { display, formatSong, palaceCells, palaceHint };
  },
});
</script>

<style scoped>
.palace-wrap,
.table-wrap {
  margin: 1.25rem 0 1.75rem;
}
.palace-title {
  text-align: center;
  font-weight: 600;
  color: var(--zw-primary);
  margin-bottom: 8px;
  letter-spacing: 0.12em;
}
.palace-hint {
  margin: 0.35rem 0 0;
  font-size: 12px;
  color: var(--zw-muted);
  text-align: center;
}
.palace-board {
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  grid-template-areas:
    'si wu wei shen'
    'chen center center you'
    'mao center center xu'
    'yin chou zi hai';
  border: 1px solid var(--zw-gold);
  background: var(--zw-paper);
  max-width: 640px;
  margin: 0 auto;
}
.palace-cell,
.palace-center {
  border: 1px solid var(--zw-line);
  padding: 8px 6px;
  min-height: 72px;
}
.palace-cell {
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  gap: 6px;
}
.palace-cell b {
  align-self: flex-end;
  color: var(--zw-primary);
  font-size: 13px;
}
.palace-text {
  font-size: 13px;
  line-height: 1.45;
  word-break: break-all;
  white-space: pre-wrap;
}
.palace-center {
  grid-area: center;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  text-align: center;
  gap: 8px;
  background: color-mix(in srgb, var(--zw-paper) 82%, var(--zw-gold));
}
.palace-center p {
  margin: 0;
  font-size: 12px;
  line-height: 1.55;
  white-space: pre-wrap;
}
.pos-巳 { grid-area: si; }
.pos-午 { grid-area: wu; }
.pos-未 { grid-area: wei; }
.pos-申 { grid-area: shen; }
.pos-酉 { grid-area: you; }
.pos-戌 { grid-area: xu; }
.pos-亥 { grid-area: hai; }
.pos-子 { grid-area: zi; }
.pos-丑 { grid-area: chou; }
.pos-寅 { grid-area: yin; }
.pos-卯 { grid-area: mao; }
.pos-辰 { grid-area: chen; }
.table-scroll {
  overflow-x: auto;
}
.table-wrap table {
  width: 100%;
  border-collapse: collapse;
  font-size: 13px;
  min-width: 640px;
}
.table-wrap th,
.table-wrap td {
  border: 1px solid var(--zw-line);
  padding: 6px 8px;
  vertical-align: top;
  line-height: 1.45;
}
.table-wrap th {
  background: color-mix(in srgb, var(--zw-paper) 80%, var(--zw-gold));
  color: var(--zw-primary);
  font-weight: 600;
  white-space: nowrap;
}
.table-wrap td:first-child {
  font-weight: 600;
  color: var(--zw-primary);
  white-space: nowrap;
}
@media (max-width: 768px) {
  .palace-cell,
  .palace-center {
    min-height: 64px;
    padding: 6px 4px;
  }
  .palace-text {
    font-size: 12px;
  }
}
</style>
