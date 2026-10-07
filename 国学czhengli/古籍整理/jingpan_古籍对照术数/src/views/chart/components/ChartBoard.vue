<template>
  <div class="chart-board-wrap">
    <div class="chart-board">
      <div
        v-for="palace in palaces"
        :key="palace.earthlyBranch"
        class="palace"
        :style="palaceStyle(palace.earthlyBranch)"
        :class="{
          'is-ming': palace.name === '命宫' || palace.name === '命宮',
          'is-shen': palace.isBodyPalace,
          'is-decadal': palace.isDecadalLimit,
          'is-yearly': palace.isYearlyLimit,
        }"
      >
        <div class="palace-head">
          <span>{{ display(palace.aliasName || palace.name, false) }}</span>
          <span>{{ palace.heavenlyStem }}{{ palace.earthlyBranch }}</span>
        </div>
        <div v-if="palace.isDecadalLimit || palace.isYearlyLimit" class="limit-tags">
          <em v-if="palace.isDecadalLimit">{{ display('大限', false) }}</em>
          <em v-if="palace.isYearlyLimit" class="yearly">{{ display('流年', false) }}</em>
        </div>
        <p v-if="palace.decadal" class="decadal">
          {{ palace.decadal.range[0] }}–{{ palace.decadal.range[1] }}
        </p>
        <div class="stars">
          <button
            v-for="star in palace.majorStars"
            :key="star.name + star.scope"
            class="star major"
            :class="[brightnessClass(star.brightness), mutagenClass(star.mutagen)]"
            :title="previewOf(star.name)"
            @click="$emit('star-click', star.name)"
          >
            {{ display(star.name, false) }}
            <small v-if="star.brightness">{{ display(star.brightness, false) }}</small>
            <i v-if="star.mutagen">{{ display(star.mutagen, false) }}</i>
          </button>
          <button
            v-for="star in palace.minorStars"
            :key="star.name + 'm'"
            class="star minor"
            :title="previewOf(star.name)"
            @click="$emit('star-click', star.name)"
          >
            {{ display(star.name, false) }}
            <i v-if="star.mutagen">{{ display(star.mutagen, false) }}</i>
          </button>
          <button
            v-for="star in palace.adjectiveStars"
            :key="star.name + 'a'"
            class="star adj"
            :class="shaClass(star)"
            :title="previewOf(star.name)"
            @click="$emit('star-click', star.name)"
          >
            {{ display(star.name, false) }}
          </button>
        </div>
      </div>
      <div class="center-panel">
        <p>{{ display('五行局', false) }}　{{ display(fiveElementsClass, false) }}</p>
        <p>{{ display('命宮', false) }}　{{ display(soul, false) }}</p>
        <p>{{ display('身宮', false) }}　{{ display(body, false) }}</p>
        <p>{{ lunarDate }}</p>
        <p>{{ chineseDate }}</p>
      </div>
    </div>
  </div>
</template>

<script lang="ts">
import { defineComponent, type PropType } from 'vue';
import type { ChartPalace } from '@/types';
import { BRANCH_GRID, BRIGHTNESS_CLASS, MUTAGEN_CLASS } from '@/utils/chart';
import { useDisplayText } from '@/composables/useDisplayText';
import starData from '@/data/starDict.json';
import type { StarEntry } from '@/types';

export default defineComponent({
  name: 'ChartBoard',
  props: {
    palaces: { type: Array as PropType<ChartPalace[]>, required: true },
    fiveElementsClass: { type: String, default: '' },
    soul: { type: String, default: '' },
    body: { type: String, default: '' },
    lunarDate: { type: String, default: '' },
    chineseDate: { type: String, default: '' },
  },
  emits: {
    'star-click': (_name: string) => true,
  },
  setup() {
    const { display } = useDisplayText();
    const dict = starData as { dict: Record<string, StarEntry>; alias: Record<string, string> };

    const palaceStyle = (branch: string) => {
      const pos = BRANCH_GRID[branch];
      if (!pos) return {};
      return { gridColumn: String(pos.col), gridRow: String(pos.row) };
    };

    const brightnessClass = (b: string) => BRIGHTNESS_CLASS[b] || '';
    const mutagenClass = (m: string) => MUTAGEN_CLASS[m] || '';
    const shaClass = (star: { name: string; type: string }) =>
      ['擎羊', '陀羅', '陀罗', '火星', '鈴星', '铃星', '地劫', '天空'].some((n) => star.name.includes(n))
        ? 'sha'
        : '';

    const previewOf = (name: string) => {
      const key = dict.alias[name] || name;
      const entry = dict.dict[key];
      if (!entry) return name;
      return (entry.answer || entry.xiYiSaid || entry.fullText).slice(0, 48);
    };

    return {
      display,
      palaceStyle,
      brightnessClass,
      mutagenClass,
      shaClass,
      previewOf,
    };
  },
});
</script>

<style scoped>
.chart-board-wrap {
  overflow: visible;
  touch-action: pan-y;
  padding: 8px;
  width: 100%;
  max-width: 100%;
  box-sizing: border-box;
}
.chart-board {
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  grid-template-rows: repeat(4, minmax(0, 1fr));
  gap: 4px;
  width: 100%;
  aspect-ratio: 1;
  min-width: 0;
  min-height: 0;
  box-sizing: border-box;
}
.palace {
  border: 1px solid var(--zw-line);
  background: var(--zw-paper);
  padding: 6px;
  font-size: 12px;
  min-height: 0;
  min-width: 0;
  overflow: hidden;
  box-sizing: border-box;
}
.palace.is-ming {
  border: 2px solid var(--zw-gold);
  padding: 5px;
}
.palace.is-shen {
  background: var(--zw-paper-gold);
}
.palace.is-decadal {
  border: 2px solid var(--zw-primary);
  padding: 5px;
  background: color-mix(in srgb, var(--zw-primary) 8%, var(--zw-paper));
}
.palace.is-yearly:not(.is-decadal) {
  border: 2px solid var(--zw-gold);
  padding: 5px;
  background: color-mix(in srgb, var(--zw-gold) 14%, var(--zw-paper));
}
.palace.is-decadal.is-yearly {
  background: color-mix(in srgb, var(--zw-primary) 6%, color-mix(in srgb, var(--zw-gold) 12%, var(--zw-paper)));
}
.limit-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 4px;
  margin: 2px 0 4px;
}
.limit-tags em {
  font-style: normal;
  font-size: 10px;
  letter-spacing: 0.08em;
  padding: 1px 5px;
  border-radius: 4px;
  color: #fff;
  background: var(--zw-primary);
}
.limit-tags em.yearly {
  background: color-mix(in srgb, var(--zw-gold) 85%, #7a5b12);
  color: var(--zw-ink);
}
.palace-head {
  display: flex;
  justify-content: space-between;
  gap: 2px;
  font-weight: 600;
  color: var(--zw-primary);
}
.palace-head span {
  min-width: 0;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}
.decadal {
  color: var(--zw-muted);
  font-size: 11px;
}
.stars {
  display: flex;
  flex-wrap: wrap;
  gap: 4px;
  margin-top: 4px;
}
.star {
  border: 0;
  background: transparent;
  cursor: pointer;
  padding: 0 2px;
  font-family: inherit;
  color: var(--zw-ink);
}
.star.major {
  font-weight: 700;
  color: var(--zw-primary);
}
.star.minor {
  color: var(--zw-gold);
}
.star.sha {
  color: #8a2f2f;
}
html.theme-nightsky .star.sha {
  color: #e07a7a;
}
.star small,
.star i {
  font-style: normal;
  font-size: 10px;
  margin-left: 2px;
  color: var(--zw-muted);
}
.star.is-miao small,
.star.is-wang small {
  color: #7a5b12;
}
.star.is-xian small,
.star.is-bu small {
  color: #8a2f2f;
  opacity: 0.85;
}
.star.muta-lu i { color: #2d6a4f; }
.star.muta-quan i { color: #3a2e5c; }
.star.muta-ke i { color: #1d4e89; }
.star.muta-ji i { color: #8a2f2f; }
.center-panel {
  grid-column: 2 / 4;
  grid-row: 2 / 4;
  border: 1px solid var(--zw-gold);
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  text-align: center;
  background: var(--zw-paper);
  padding: 8px;
  line-height: 1.8;
  min-width: 0;
  overflow: hidden;
  box-sizing: border-box;
}
.center-panel p {
  margin: 0;
  max-width: 100%;
  word-break: break-word;
}
@media (max-width: 767.98px) {
  .chart-board-wrap {
    padding: 0;
    overflow: visible;
    touch-action: pan-y;
  }
  .chart-board {
    width: 100%;
    min-width: 0;
    min-height: 0;
    /* 不再压成正方形：行高随内容长高，避免宫位挤成一团 */
    aspect-ratio: auto;
    gap: 5px;
    grid-template-columns: repeat(4, minmax(0, 1fr));
    grid-template-rows: repeat(4, minmax(126px, auto));
  }
  .palace {
    display: flex;
    flex-direction: column;
    padding: 7px 6px 8px;
    font-size: 11px;
    min-height: 126px;
    line-height: 1.4;
    overflow: visible;
  }
  .palace.is-ming {
    padding: 6px 5px 7px;
  }
  .palace-head {
    font-size: 11px;
    letter-spacing: 0.04em;
    margin-bottom: 2px;
    gap: 4px;
  }
  .palace-head span:last-child {
    flex-shrink: 0;
    color: var(--zw-muted);
    font-weight: 500;
    font-size: 10px;
  }
  .decadal {
    margin: 0 0 6px;
    font-size: 10px;
    line-height: 1.3;
    letter-spacing: 0.02em;
  }
  .stars {
    gap: 4px 0;
    margin-top: 0;
    flex: 1;
    align-content: flex-start;
  }
  /* 主星单独成行，辅星/杂曜换行排布，减轻横向挤兑 */
  .star.major {
    flex: 0 0 100%;
    padding: 0;
    font-size: 12px;
    line-height: 1.45;
    letter-spacing: 0.02em;
  }
  .star.minor,
  .star.adj {
    flex: 0 0 auto;
    margin-right: 6px;
    padding: 0;
    font-size: 10.5px;
    line-height: 1.4;
  }
  .star small,
  .star i {
    font-size: 10px;
    margin-left: 2px;
  }
  .center-panel {
    padding: 12px 10px;
    line-height: 1.75;
    font-size: 12px;
    letter-spacing: 0.04em;
    gap: 4px;
  }
  .center-panel p + p {
    margin-top: 2px;
  }
}
</style>
