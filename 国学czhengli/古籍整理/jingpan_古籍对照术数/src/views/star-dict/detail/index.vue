<template>
  <div class="page-container">
    <el-button class="mb-4" @click="$router.push('/star-dict')">{{ display('返回列表', false) }}</el-button>
    <article v-if="entry" class="rounded-lg border p-6 classic-prose" :style="cardStyle">
      <h1 class="mb-4 text-2xl font-semibold">{{ display(entry.name, false) }}</h1>
      <section class="mb-6">
        <h2 class="mb-2 font-semibold" style="color: var(--zw-gold)">{{ display('問答原文', false) }}</h2>
        <p class="font-semibold">{{ display(entry.question) }}</p>
        <p class="mt-3 whitespace-pre-wrap">{{ display(entry.answer || entry.fullText) }}</p>
      </section>
      <section v-if="entry.xiYiSaid" class="mb-6">
        <h2 class="mb-2 font-semibold" style="color: var(--zw-gold)">{{ display('希夷先生曰', false) }}</h2>
        <blockquote class="quote-block">{{ display(entry.xiYiSaid) }}</blockquote>
      </section>
      <section v-if="entry.yuChanSaid" class="mb-6">
        <blockquote class="quote-block">{{ display(entry.yuChanSaid) }}</blockquote>
      </section>
      <section v-if="entry.song">
        <h2 class="mb-2 font-semibold" style="color: var(--zw-gold)">{{ display('歌曰', false) }}</h2>
        <div class="song-card">{{ formatSong(display(entry.song)) }}</div>
      </section>
    </article>
    <p v-else>{{ display('未見此星專條。', false) }}</p>
  </div>
</template>

<script lang="ts">
import { computed, defineComponent, watch } from 'vue';
import { useRoute } from 'vue-router';
import starData from '@/data/starDict.json';
import type { StarEntry } from '@/types';
import { applySeo } from '@/composables/useSeo';
import { useDisplayText } from '@/composables/useDisplayText';

function clip(text: string, max = 140): string {
  const t = text.replace(/\s+/g, ' ').trim();
  if (!t) return '';
  return t.length > max ? `${t.slice(0, max - 1)}…` : t;
}

export default defineComponent({
  name: 'StarDictDetailPage',
  setup() {
    const route = useRoute();
    const { display } = useDisplayText();
    const data = starData as { dict: Record<string, StarEntry>; alias: Record<string, string> };
    const entry = computed(() => {
      const name = decodeURIComponent(String(route.params.name || ''));
      const key = data.alias[name] || name;
      return data.dict[key];
    });
    watch(
      entry,
      (e) => {
        const name = decodeURIComponent(String(route.params.name || ''));
        if (!e) {
          applySeo({
            title: '未見此星',
            description: '星曜詞典未找到對應條目。',
            path: route.path,
            noindex: true,
          });
          return;
        }
        const body = clip(e.answer || e.fullText || e.question || '');
        applySeo({
          title: `${e.name} · 星曜詞典`,
          description:
            body ||
            `紫微斗數星曜「${e.name}」諸星問答原文對照，取自《紫微斗數全書》卷一。`,
          path: `/star-dict/${encodeURIComponent(name)}`,
        });
      },
      { immediate: true },
    );
    const formatSong = (text: string) =>
      text
        .replace(/歌曰：?/g, '歌曰：\n')
        .split(/[，,]/)
        .map((s) => s.trim())
        .filter(Boolean)
        .join('\n');
    const cardStyle = {
      background: 'var(--zw-paper)',
      borderColor: 'var(--zw-line)',
    };
    return { entry, display, formatSong, cardStyle };
  },
});
</script>
