<template>
  <article class="yijing-prose">
    <template v-for="(block, idx) in blocks" :key="idx">
      <h3 v-if="block.type === 'heading'" class="y-heading">{{ display(block.text ?? '', false) }}</h3>
      <figure v-else-if="block.type === 'image'" class="y-figure">
        <img :src="block.src" :alt="display(block.alt ?? '卦象圖', false)" loading="lazy" />
      </figure>
      <p v-else class="y-prose">{{ display(block.text ?? '', false) }}</p>
    </template>
  </article>
</template>

<script lang="ts">
import { defineComponent, type PropType } from 'vue';
import { useDisplayText } from '@/composables/useDisplayText';

export interface YijingBlock {
  type: 'heading' | 'prose' | 'image';
  text?: string;
  src?: string;
  alt?: string;
}

export default defineComponent({
  name: 'YijingText',
  props: {
    blocks: {
      type: Array as PropType<YijingBlock[]>,
      required: true,
    },
  },
  setup() {
    const { display } = useDisplayText();
    return { display };
  },
});
</script>

<style scoped>
.yijing-prose {
  line-height: 1.85;
  letter-spacing: 0.04em;
}
.y-heading {
  margin: 1.25rem 0 0.5rem;
  font-size: 1.05rem;
  font-weight: 600;
  color: var(--zw-gold);
}
.y-prose {
  margin: 0 0 0.85rem;
  white-space: pre-wrap;
}
.y-figure {
  margin: 1rem 0;
  text-align: center;
}
.y-figure img {
  max-width: 100%;
  border-radius: 8px;
  border: 1px solid var(--zw-line);
}
</style>
