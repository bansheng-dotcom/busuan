<template>
  <div class="page-container yijing-page">
    <h1 class="title">{{ display(intro.title, false) }}</h1>
    <p class="lead">
      {{ display(intro.note, false) }}
      <a :href="intro.sourceIndex" target="_blank" rel="noopener">{{ display('來源索引', false) }}</a>
    </p>

    <section class="intro card" :style="cardStyle">
      <h2>{{ display('總論', false) }}</h2>
      <YijingText :blocks="intro.blocks" />
    </section>

    <section class="gua-list">
      <div class="list-head">
        <div>
          <h2>{{ display('六十四卦先後順序', false) }}</h2>
          <p class="list-lead">
            {{ display('按《周易》上下經文王卦序排列；可用八卦篩選上卦或下卦。', false) }}
          </p>
        </div>
        <label class="filter">
          <span>{{ display('八卦', false) }}</span>
          <SheetSelect
            v-if="isMobile"
            v-model="trigramFilter"
            :options="trigramOptions"
            :title="display('八卦', false)"
            :cancel-text="display('取消', false)"
          />
          <el-select v-else v-model="trigramFilter" size="small" style="width: 7.5rem">
            <el-option :label="display('全部', false)" value="" />
            <el-option
              v-for="g in TRIGRAM_OPTIONS"
              :key="g"
              :label="display(g, false)"
              :value="g"
            />
          </el-select>
        </label>
      </div>

      <template v-if="!trigramFilter">
        <h3 class="sec-title">{{ display('上經 · 1–30', false) }}</h3>
        <div class="grid">
          <router-link
            v-for="item in upperJing"
            :key="item.id"
            :to="`/yijing/${item.id}`"
            class="cell"
            :style="cardStyle"
          >
            <span class="no">{{ item.index }}</span>
            <span class="body">
              <b>{{ display(item.name, false) }}</b>
              <em>{{ display(trigramLabel(item.index), false) }}</em>
            </span>
          </router-link>
        </div>
        <h3 class="sec-title">{{ display('下經 · 31–64', false) }}</h3>
        <div class="grid">
          <router-link
            v-for="item in lowerJing"
            :key="item.id"
            :to="`/yijing/${item.id}`"
            class="cell"
            :style="cardStyle"
          >
            <span class="no">{{ item.index }}</span>
            <span class="body">
              <b>{{ display(item.name, false) }}</b>
              <em>{{ display(trigramLabel(item.index), false) }}</em>
            </span>
          </router-link>
        </div>
      </template>

      <template v-else>
        <h3 class="sec-title">
          {{ display(`含「${trigramFilter}」· 共 ${filteredList.length} 卦`, false) }}
        </h3>
        <div v-if="filteredList.length" class="grid">
          <router-link
            v-for="item in filteredList"
            :key="item.id"
            :to="`/yijing/${item.id}`"
            class="cell"
            :style="cardStyle"
          >
            <span class="no">{{ item.index }}</span>
            <span class="body">
              <b>{{ display(item.name, false) }}</b>
              <em>{{ display(trigramLabel(item.index), false) }}</em>
            </span>
          </router-link>
        </div>
        <p v-else class="empty">{{ display('無符合條件之卦。', false) }}</p>
      </template>
    </section>
  </div>
</template>

<script lang="ts">
import { computed, defineComponent, nextTick, onActivated, onMounted, ref } from 'vue';
import { onBeforeRouteLeave } from 'vue-router';
import introData from '@/data/yijingIntro.json';
import hexData from '@/data/yijingHexagrams.json';
import YijingText, { type YijingBlock } from '@/components/YijingText.vue';
import SheetSelect from '@/components/sheet/SheetSelect.vue';
import { useDisplayText } from '@/composables/useDisplayText';
import { useDevice } from '@/composables/useDevice';
import { trigramsOf } from '@/utils/yijingTrigrams';
import { WEN_HEXAGRAM_ORDER } from '@/data/yijingWenOrder';

const TRIGRAM_OPTIONS = ['天', '澤', '火', '雷', '風', '水', '山', '地'] as const;

interface HexItem {
  id: string;
  index: number;
  name: string;
}

let listScrollY = 0;

function saveListScroll() {
  listScrollY = window.scrollY;
}

function restoreListScroll() {
  const y = listScrollY;
  if (!y) return;
  void nextTick(() => {
    window.scrollTo({ top: y, left: 0, behavior: 'auto' });
    requestAnimationFrame(() => window.scrollTo({ top: y, left: 0, behavior: 'auto' }));
  });
}

export default defineComponent({
  name: 'YijingPage',
  components: { YijingText, SheetSelect },
  setup() {
    const { display } = useDisplayText();
    const { isMobile } = useDevice();
    const intro = introData as {
      title: string;
      note: string;
      sourceIndex: string;
      blocks: YijingBlock[];
    };
    const trigramFilter = ref('');

    const trigramOptions = computed(() => [
      { label: display('全部', false), value: '' },
      ...TRIGRAM_OPTIONS.map((g) => ({ label: display(g, false), value: g })),
    ]);

    const byIndex = new Map(
      (hexData as { hexagrams: HexItem[] }).hexagrams.map((h) => [h.index, h]),
    );

    /** 文王序完整列表（帶站內全名） */
    const wenList = computed(() =>
      WEN_HEXAGRAM_ORDER.map((_, i) => {
        const index = i + 1;
        const hit = byIndex.get(index);
        return {
          id: hit?.id ?? `gua-${index}`,
          index,
          name: hit?.name ?? WEN_HEXAGRAM_ORDER[i],
        };
      }),
    );

    const upperJing = computed(() => wenList.value.slice(0, 30));
    const lowerJing = computed(() => wenList.value.slice(30));

    const filteredList = computed(() => {
      const g = trigramFilter.value;
      if (!g) return wenList.value;
      return wenList.value.filter((item) => {
        const { upper, lower } = trigramsOf(item.index);
        return upper === g || lower === g;
      });
    });

    const trigramLabel = (index: number) => {
      const { upper, lower } = trigramsOf(index);
      return `上${upper} · 下${lower}`;
    };

    const cardStyle = {
      background: 'var(--zw-paper)',
      borderColor: 'var(--zw-line)',
    };

    onMounted(restoreListScroll);
    onActivated(restoreListScroll);
    onBeforeRouteLeave(() => {
      saveListScroll();
    });

    return {
      display,
      isMobile,
      intro,
      TRIGRAM_OPTIONS,
      trigramFilter,
      trigramOptions,
      upperJing,
      lowerJing,
      filteredList,
      trigramLabel,
      cardStyle,
    };
  },
});
</script>

<style scoped>
.yijing-page {
  padding-bottom: 2.5rem;
}
.title {
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
.card {
  padding: 1rem 1.15rem;
  margin-bottom: 1.75rem;
  border: 1px solid var(--zw-line);
  border-radius: 12px;
}
.card h2,
.gua-list h2 {
  margin: 0 0 0.35rem;
  font-size: 1rem;
  letter-spacing: 0.18em;
  color: var(--zw-primary);
}
.gua-list {
  margin-bottom: 1.5rem;
}
.list-head {
  display: flex;
  flex-wrap: wrap;
  align-items: flex-end;
  justify-content: space-between;
  gap: 0.75rem 1.25rem;
  margin-bottom: 0.85rem;
}
.list-lead {
  margin: 0;
  max-width: 28rem;
  font-size: 0.78rem;
  line-height: 1.5;
  color: var(--zw-muted);
}
.filter {
  display: inline-flex;
  align-items: center;
  gap: 0.45rem;
  font-size: 0.82rem;
  letter-spacing: 0.1em;
  color: var(--zw-ink);
}
.filter :deep(.sheet-select) {
  min-width: 7.5rem;
}
.sec-title {
  margin: 1rem 0 0.55rem;
  font-size: 0.82rem;
  letter-spacing: 0.14em;
  color: var(--zw-muted);
  font-weight: 600;
}
.grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(132px, 1fr));
  gap: 0.55rem;
}
.cell {
  display: flex;
  align-items: flex-start;
  gap: 0.55rem;
  padding: 0.65rem 0.75rem;
  border: 1px solid var(--zw-line);
  border-radius: 10px;
  text-decoration: none;
  color: var(--zw-ink);
}
.cell .body {
  display: flex;
  flex-direction: column;
  gap: 0.15rem;
  min-width: 0;
}
.cell em {
  font-style: normal;
  font-size: 0.72rem;
  color: var(--zw-muted);
  letter-spacing: 0.06em;
}
.cell:hover {
  border-color: var(--zw-gold);
  color: var(--zw-primary);
}
.no {
  flex: none;
  width: 1.6rem;
  text-align: center;
  font-size: 0.8rem;
  color: var(--zw-muted);
}
.cell b {
  font-size: 0.95rem;
  letter-spacing: 0.1em;
}
.empty {
  margin: 0.5rem 0 0;
  font-size: 0.88rem;
  color: var(--zw-muted);
}
</style>
