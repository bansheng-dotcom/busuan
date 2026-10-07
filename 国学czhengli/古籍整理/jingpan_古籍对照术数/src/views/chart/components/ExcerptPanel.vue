<template>
  <aside class="excerpt-panel rounded-lg border p-3" :style="panelStyle">
    <div class="mb-2 flex items-center justify-between">
      <h3 class="font-semibold">{{ display('相關古籍原文片段', false) }}</h3>
      <el-button size="small" @click="handleCopyAll">{{ display('複製原文片段', false) }}</el-button>
    </div>
    <p v-if="!items.length" class="text-sm" style="color: var(--zw-muted)">
      {{ display('生成命盤後，將摘取卷一賦文中含當前命宮星曜之名的原句。', false) }}
    </p>
    <ul class="space-y-3">
      <li v-for="(item, idx) in items" :key="idx" class="classic-prose excerpt-item">
        <button class="excerpt-link" style="color: var(--zw-gold)" @click="$emit('goto', item.chapterId)">
          {{ display(item.chapterTitle, false) }}
        </button>
        <p>{{ display(item.text) }}</p>
      </li>
    </ul>
  </aside>
</template>

<script lang="ts">
import { defineComponent, type PropType } from 'vue';
import type { ExcerptItem } from '@/types';
import { useDisplayText } from '@/composables/useDisplayText';
import { copyText } from '@/utils/copy';

export default defineComponent({
  name: 'ExcerptPanel',
  props: {
    items: { type: Array as PropType<ExcerptItem[]>, default: () => [] },
  },
  emits: {
    goto: (_id: string) => true,
  },
  setup(props) {
    const { display } = useDisplayText();
    const panelStyle = {
      background: 'var(--zw-paper)',
      borderColor: 'var(--zw-line)',
    };
    const handleCopyAll = () => {
      void copyText(props.items.map((i) => `【${i.chapterTitle}】${i.text}`).join('\n'));
    };
    return { display, panelStyle, handleCopyAll };
  },
});
</script>

<style scoped>
.excerpt-item p {
  margin: 0.25em 0 0;
  line-height: 1.7;
}
.excerpt-link {
  background: none;
  border: 0;
  padding: 0;
  cursor: pointer;
  font-family: inherit;
  font-size: 0.85em;
  text-decoration: underline;
}
</style>
