<template>
  <div class="page-container">
    <h1 class="mb-2 text-2xl font-semibold">{{ display('格局詞典', false) }}</h1>
    <p class="mb-6 text-sm" style="color: var(--zw-muted)">
      {{ display('分組取自卷一定富局、定貴局、定貧賤局、定雜局及格局詩訣，只列古籍原文，不附白話。', false) }}
    </p>
    <section v-for="group in groups" :key="group" class="mb-8">
      <h2 class="mb-3 text-xl font-semibold" style="color: var(--zw-primary)">{{ display(group, false) }}</h2>
      <div class="grid gap-3 md:grid-cols-2">
        <article
          v-for="item in grouped[group]"
          :key="item.name"
          class="rounded-lg border p-4"
          :style="cardStyle"
        >
          <h3 class="mb-1 font-semibold">{{ display(item.name, false) }}</h3>
          <p class="mb-2 text-sm" style="color: var(--zw-muted)">{{ display(item.condition) }}</p>
          <div class="song-card">{{ formatSong(display(item.originalText)) }}</div>
        </article>
      </div>
    </section>
  </div>
</template>

<script lang="ts">
import { computed, defineComponent } from 'vue';
import patternDict from '@/data/patternDict.json';
import type { PatternEntry } from '@/types';
import { useDisplayText } from '@/composables/useDisplayText';

export default defineComponent({
  name: 'PatternDictPage',
  setup() {
    const { display } = useDisplayText();
    const dict = patternDict as Record<string, PatternEntry>;
    const groups = ['定富局', '定貴局', '定貧賤局', '定雜局'];
    const grouped = computed(() => {
      const map: Record<string, Array<PatternEntry & { name: string }>> = {
        定富局: [],
        定貴局: [],
        定貧賤局: [],
        定雜局: [],
      };
      for (const [name, item] of Object.entries(dict)) {
        (map[item.category] ?? map['定貴局']).push({ ...item, name });
      }
      return map;
    });
    const formatSong = (text: string) =>
      text
        .split(/[，,]/)
        .map((s) => s.trim())
        .filter(Boolean)
        .join('\n');
    const cardStyle = {
      background: 'var(--zw-paper)',
      borderColor: 'var(--zw-line)',
    };
    return { display, groups, grouped, formatSong, cardStyle };
  },
});
</script>
