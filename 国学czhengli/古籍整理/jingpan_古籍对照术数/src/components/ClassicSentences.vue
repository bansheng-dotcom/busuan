<template>
  <div class="classic-sentences" :class="{ multiline }">
    <template v-for="(seg, idx) in segments" :key="idx">
      <p class="classic-line" :class="{ 'is-block': multiline }">{{ display(seg.text) }}</p>
      <p v-if="showVernacular && seg.vernacular" class="vernacular-line">
        {{ display(seg.vernacular, false) }}
      </p>
    </template>
  </div>
</template>

<script lang="ts">
import { computed, defineComponent } from 'vue';
import { useDisplayText } from '@/composables/useDisplayText';
import { annotateClassicText, chapterHasVernacular } from '@/utils/bookVernacular';

export default defineComponent({
  name: 'ClassicSentences',
  props: {
    text: { type: String, default: '' },
    chapterId: { type: String, default: '' },
    showVernacular: { type: Boolean, default: false },
    multiline: { type: Boolean, default: false },
  },
  setup(props) {
    const { display } = useDisplayText();
    const segments = computed(() => {
      if (!props.text.trim()) return [];
      // 關閉白話時不做拆句匹配，避免整卷正文反覆掃描索引
      if (
        !props.showVernacular ||
        !props.chapterId ||
        !chapterHasVernacular(props.chapterId)
      ) {
        return [{ text: props.text.trim() }];
      }
      return annotateClassicText(props.text, props.chapterId);
    });
    return { display, segments };
  },
});
</script>

<style scoped>
.classic-sentences.multiline .classic-line.is-block {
  white-space: pre-wrap;
}
.classic-line {
  margin: 0 0 0.25rem;
  line-height: 1.75;
  font-size: 1em;
  color: var(--zw-ink);
}
.vernacular-line {
  display: block;
  margin: 0 0 0.85rem;
  padding: 0.45rem 0.65rem;
  border-radius: 6px;
  background: color-mix(in srgb, var(--zw-primary) 10%, var(--zw-paper));
  box-shadow: inset 0 0 0 1px color-mix(in srgb, var(--zw-primary) 14%, transparent);
  font-size: 0.7em;
  line-height: 1.65;
  color: var(--zw-muted);
  font-weight: 400;
}
</style>
