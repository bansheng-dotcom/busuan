<template>
  <div class="page-container yijing-detail">
    <button v-if="!fromYaogua" type="button" class="back" @click="$router.push('/yijing')">
      {{ display('返回列表', false) }}
    </button>

    <article v-if="entry" ref="cardRef" class="card classic-prose" :style="cardStyle">
      <header class="head">
        <p class="meta">
          {{
            display(
              `第 ${entry.index} 卦 · 上卦${trigrams.upper} · 下卦${trigrams.lower}`,
              false,
            )
          }}
        </p>
        <h1>{{ display(entry.name, false) }}</h1>
        <p v-if="entry.title" class="sub">{{ display(entry.title, false) }}</p>
      </header>
      <YijingText :blocks="entry.blocks" />
      <div class="foot-nav">
        <router-link
          v-if="prevEntry"
          class="nav-gua prev"
          :to="prevLink"
        >
          <span aria-hidden="true">‹</span>
          {{ display(`上一卦 · ${prevWenName}`, false) }}
        </router-link>
        <p v-else class="nav-gua done prev">{{ display('已是第一卦 · 乾', false) }}</p>
        <p class="nav-hint">{{ display(wenHint, false) }}</p>
        <router-link
          v-if="nextEntry"
          class="nav-gua next"
          :to="nextLink"
        >
          {{ display(`下一卦 · ${nextWenName}`, false) }}
          <span aria-hidden="true">›</span>
        </router-link>
        <p v-else class="nav-gua done next">{{ display('已至末卦 · 未濟', false) }}</p>
      </div>
      <p class="source">
        {{ display('底本', false) }}：
        <a :href="entry.sourceUrl" target="_blank" rel="noopener">{{ entry.sourceUrl }}</a>
      </p>
    </article>
    <p v-else>{{ display('未見此卦條目。', false) }}</p>

    <button
      v-if="fromYaogua"
      type="button"
      class="float-back"
      :class="{ dragging: floatDragging }"
      :style="floatStyle"
      @pointerdown="handleFloatDown"
      @click="handleFloatClick"
    >
      <span class="float-ico" aria-hidden="true">‹</span>
      <span class="float-txt">{{ display('返回搖卦', false) }}</span>
    </button>
  </div>
</template>

<script lang="ts">
import { computed, defineComponent, nextTick, onMounted, onUnmounted, ref, watch } from 'vue';
import { onBeforeRouteLeave, useRoute, useRouter } from 'vue-router';
import hexData from '@/data/yijingHexagrams.json';
import YijingText, { type YijingBlock } from '@/components/YijingText.vue';
import { applySeo } from '@/composables/useSeo';
import { useDisplayText } from '@/composables/useDisplayText';
import { useYaoguaSessionStore } from '@/store/yaoguaSession';
import { trigramsOf } from '@/utils/yijingTrigrams';
import {
  wenNameOf,
  wenNextIndex,
  wenPrevIndex,
  wenSectionOf,
} from '@/data/yijingWenOrder';

function excerptFromBlocks(blocks: YijingBlock[], max = 120): string {
  const parts: string[] = [];
  for (const b of blocks) {
    if ((b.type === 'prose' || b.type === 'heading') && b.text?.trim()) {
      parts.push(b.text.trim().replace(/\s+/g, ' '));
      if (parts.join('').length >= max) break;
    }
  }
  const raw = parts.join(' ').trim();
  if (!raw) return '';
  return raw.length > max ? `${raw.slice(0, max - 1)}…` : raw;
}

interface YijingHexagram {
  id: string;
  index: number;
  name: string;
  upperTrigram: string;
  title: string;
  sourceUrl: string;
  blocks: YijingBlock[];
}

export default defineComponent({
  name: 'YijingDetailPage',
  components: { YijingText },
  setup() {
    const route = useRoute();
    const router = useRouter();
    const session = useYaoguaSessionStore();
    const { display } = useDisplayText();
    const list = (hexData as { hexagrams: YijingHexagram[] }).hexagrams;
    const byIndex = new Map(list.map((h) => [h.index, h]));
    const entry = computed(() => list.find((h) => h.id === route.params.id));
    const trigrams = computed(() => trigramsOf(entry.value?.index ?? 0));
    /** 嚴格按《周易》上下經文王卦序前後跳轉 */
    const prevEntry = computed(() => {
      const prev = wenPrevIndex(entry.value?.index ?? 0);
      return prev ? byIndex.get(prev) ?? null : null;
    });
    const nextEntry = computed(() => {
      const next = wenNextIndex(entry.value?.index ?? 0);
      return next ? byIndex.get(next) ?? null : null;
    });
    const prevWenName = computed(() => wenNameOf(prevEntry.value?.index ?? 0));
    const nextWenName = computed(() => wenNameOf(nextEntry.value?.index ?? 0));
    const wenHint = computed(() => {
      const i = entry.value?.index ?? 0;
      const sec = wenSectionOf(i);
      if (!sec) return '周易上下經卦序';
      return `${sec} · 第 ${i} 卦 · ${wenNameOf(i)}`;
    });
    const guaLink = (gua: YijingHexagram | null) => {
      if (!gua) return { path: '/yijing' };
      const q = route.query.from ? { from: route.query.from } : undefined;
      return { path: `/yijing/${gua.id}`, query: q };
    };
    const prevLink = computed(() => guaLink(prevEntry.value));
    const nextLink = computed(() => guaLink(nextEntry.value));
    const fromYaogua = computed(
      () => route.query.from === 'yaogua' || session.isFromYaogua(),
    );

    watch(
      entry,
      (h) => {
        if (!h) {
          applySeo({
            title: '未見此卦',
            description: '易經單卦詳解頁面未找到對應條目。',
            path: route.path,
            noindex: true,
          });
          return;
        }
        const tri = trigramsOf(h.index);
        const excerpt = excerptFromBlocks(h.blocks);
        const desc =
          excerpt ||
          `易經第 ${h.index} 卦「${h.name}」：上卦${tri.upper}、下卦${tri.lower}。站內原文對照，不編吉凶斷語。`;
        applySeo({
          title: `${h.name} · 第 ${h.index} 卦`,
          description: desc,
          path: `/yijing/${h.id}`,
          jsonLd: {
            '@context': 'https://schema.org',
            '@type': 'Article',
            headline: h.name,
            description: desc,
            inLanguage: 'zh-Hant',
            isPartOf: { '@type': 'WebSite', name: '經盤' },
          },
        });
      },
      { immediate: true },
    );

    const floatLeft = ref(0);
    const floatTop = ref(0);
    const floatDragging = ref(false);
    const floatMoved = ref(false);
    const cardRef = ref<HTMLElement | null>(null);
    let floatOrigin = { x: 0, y: 0, left: 0, top: 0 };

    const floatStyle = computed(() => ({
      left: `${floatLeft.value}px`,
      top: `${floatTop.value}px`,
    }));

    const clampFloat = (left: number, top: number) => {
      const w = 132;
      const h = 44;
      const maxL = Math.max(8, window.innerWidth - w - 8);
      const maxT = Math.max(8, window.innerHeight - h - 8);
      return {
        left: Math.min(maxL, Math.max(8, left)),
        top: Math.min(maxT, Math.max(72, top)),
      };
    };

    /** 默認貼在正文卡片右緣中部 */
    const placeFloatDefault = () => {
      const w = 132;
      const h = 44;
      const rect = cardRef.value?.getBoundingClientRect();
      let left: number;
      let top: number;
      if (rect && rect.width > 40) {
        left = rect.right - w - 8;
        top = Math.min(
          Math.max(72, rect.top + Math.max(80, rect.height * 0.22) - h / 2),
          window.innerHeight - h - 16,
        );
      } else {
        left = window.innerWidth - w - 20;
        top = Math.round(window.innerHeight * 0.4);
      }
      const next = clampFloat(left, top);
      floatLeft.value = next.left;
      floatTop.value = next.top;
    };

    const handleFloatMove = (e: PointerEvent) => {
      const dx = e.clientX - floatOrigin.x;
      const dy = e.clientY - floatOrigin.y;
      if (Math.abs(dx) > 4 || Math.abs(dy) > 4) floatMoved.value = true;
      const next = clampFloat(floatOrigin.left + dx, floatOrigin.top + dy);
      floatLeft.value = next.left;
      floatTop.value = next.top;
    };

    const handleFloatUp = (e: PointerEvent) => {
      floatDragging.value = false;
      window.removeEventListener('pointermove', handleFloatMove);
      window.removeEventListener('pointerup', handleFloatUp);
      try {
        (e.target as HTMLElement)?.releasePointerCapture?.(e.pointerId);
      } catch {
        /* ignore */
      }
    };

    const handleFloatDown = (e: PointerEvent) => {
      if (e.button !== 0) return;
      floatDragging.value = true;
      floatMoved.value = false;
      floatOrigin = {
        x: e.clientX,
        y: e.clientY,
        left: floatLeft.value,
        top: floatTop.value,
      };
      (e.currentTarget as HTMLElement).setPointerCapture?.(e.pointerId);
      window.addEventListener('pointermove', handleFloatMove);
      window.addEventListener('pointerup', handleFloatUp);
    };

    const handleBack = () => {
      if (window.history.length > 1) {
        router.back();
        return;
      }
      void router.push('/yaogua');
    };

    const handleFloatClick = () => {
      if (floatMoved.value) return;
      handleBack();
    };

    const keepFloatInView = () => {
      const next = clampFloat(floatLeft.value, floatTop.value);
      floatLeft.value = next.left;
      floatTop.value = next.top;
    };

    const cardStyle = {
      background: 'var(--zw-paper)',
      borderColor: 'var(--zw-line)',
    };

    const onResize = () => {
      if (fromYaogua.value) placeFloatDefault();
      else keepFloatInView();
    };

    onMounted(() => {
      window.addEventListener('resize', onResize, { passive: true });
      void nextTick(() => {
        if (fromYaogua.value) placeFloatDefault();
      });
    });

    watch(fromYaogua, (on) => {
      if (on) void nextTick(placeFloatDefault);
    });

    watch(entry, () => {
      if (fromYaogua.value) void nextTick(placeFloatDefault);
    });

    onUnmounted(() => {
      window.removeEventListener('resize', onResize);
      window.removeEventListener('pointermove', handleFloatMove);
      window.removeEventListener('pointerup', handleFloatUp);
    });

    onBeforeRouteLeave((to) => {
      if (to.name !== 'yaogua') session.clearFromYaogua();
    });

    return {
      display,
      entry,
      trigrams,
      nextEntry,
      nextLink,
      nextWenName,
      prevEntry,
      prevLink,
      prevWenName,
      wenHint,
      cardStyle,
      cardRef,
      fromYaogua,
      floatStyle,
      floatDragging,
      handleFloatDown,
      handleFloatClick,
    };
  },
});
</script>

<style scoped>
.back {
  margin-bottom: 0.85rem;
  padding: 0.35rem 0.75rem;
  border: 1px solid var(--zw-line);
  border-radius: 8px;
  background: transparent;
  color: var(--zw-ink);
  font-family: inherit;
  cursor: pointer;
}
.card {
  padding: 1.1rem 1.2rem;
  border: 1px solid var(--zw-line);
  border-radius: 12px;
}
.head {
  margin-bottom: 1rem;
  padding-bottom: 0.75rem;
  border-bottom: 1px solid var(--zw-line);
}
.meta {
  margin: 0 0 0.25rem;
  font-size: 0.8rem;
  color: var(--zw-muted);
  letter-spacing: 0.12em;
}
.head h1 {
  margin: 0;
  font-size: 1.45rem;
  color: var(--zw-gold);
  letter-spacing: 0.14em;
}
.sub {
  margin: 0.35rem 0 0;
  font-size: 0.88rem;
  color: var(--zw-muted);
}
.source {
  margin: 0.85rem 0 0;
  font-size: 0.78rem;
  color: var(--zw-muted);
  word-break: break-all;
}
.source a {
  color: var(--zw-primary);
}
.foot-nav {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  justify-content: space-between;
  gap: 0.75rem 1rem;
  margin-top: 1.25rem;
  padding-top: 0.85rem;
  border-top: 1px solid var(--zw-line);
}
.nav-hint {
  flex: 1 1 100%;
  order: -1;
  margin: 0;
  text-align: center;
  font-size: 0.75rem;
  letter-spacing: 0.12em;
  color: var(--zw-muted);
}
@media (min-width: 640px) {
  .nav-hint {
    flex: 1 1 auto;
    order: 0;
  }
}
.nav-gua {
  display: inline-flex;
  align-items: center;
  gap: 0.35rem;
  padding: 0.45rem 0.9rem;
  border: 1px solid color-mix(in srgb, var(--zw-gold) 65%, var(--zw-line));
  border-radius: 8px;
  background: color-mix(in srgb, var(--zw-paper) 88%, var(--zw-gold));
  color: var(--zw-primary);
  font-size: 0.88rem;
  letter-spacing: 0.1em;
  text-decoration: none;
  line-height: 1.3;
  transition: background 0.15s ease, border-color 0.15s ease;
}
.nav-gua.prev {
  border-color: color-mix(in srgb, var(--zw-primary) 35%, var(--zw-line));
}
.nav-gua.next {
  margin-left: auto;
  background: color-mix(in srgb, var(--zw-gold) 18%, var(--zw-paper));
}
.nav-gua:hover,
.nav-gua:focus-visible {
  background: color-mix(in srgb, var(--zw-gold) 22%, var(--zw-paper));
  border-color: var(--zw-gold);
  outline: none;
}
.nav-gua.done {
  border-style: dashed;
  color: var(--zw-muted);
  background: transparent;
  cursor: default;
}
.nav-gua span {
  font-size: 1.05rem;
  line-height: 1;
}
.float-back {
  position: fixed;
  z-index: 65;
  display: inline-flex;
  align-items: center;
  gap: 4px;
  min-height: 40px;
  padding: 8px 14px 8px 10px;
  border: 1px solid color-mix(in srgb, var(--zw-gold) 70%, var(--zw-line));
  border-radius: 999px;
  background: color-mix(in srgb, var(--zw-paper) 92%, var(--zw-gold));
  color: var(--zw-primary);
  font-family: inherit;
  font-size: 13px;
  letter-spacing: 0.14em;
  line-height: 1.2;
  cursor: grab;
  touch-action: none;
  user-select: none;
  box-shadow:
    0 1px 0 color-mix(in srgb, #fff 55%, transparent) inset,
    0 8px 22px rgba(44, 36, 22, 0.14);
  backdrop-filter: blur(8px);
}
.float-back .float-ico {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 1.35rem;
  height: 1.35rem;
  border-radius: 50%;
  background: color-mix(in srgb, var(--zw-gold) 28%, transparent);
  color: var(--zw-primary);
  font-size: 1.05rem;
  font-weight: 600;
  line-height: 1;
}
.float-back .float-txt {
  white-space: nowrap;
}
.float-back.dragging {
  cursor: grabbing;
  transform: scale(1.03);
}
</style>
