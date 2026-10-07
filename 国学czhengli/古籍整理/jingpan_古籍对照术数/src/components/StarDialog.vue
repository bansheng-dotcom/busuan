<template>
  <el-dialog
    v-model="visible"
    :title="display(entry?.question || starName, false)"
    width="720px"
    class="star-dialog"
    append-to-body
    destroy-on-close
  >
    <div v-if="entry" class="classic-prose max-h-[60vh] overflow-y-auto pr-2">
      <p class="font-semibold">{{ display(entry.question) }}</p>
      <p v-if="entry.answer" class="my-3 whitespace-pre-wrap">{{ display(entry.answer) }}</p>
      <blockquote v-if="entry.xiYiSaid" class="quote-block">{{ display(entry.xiYiSaid) }}</blockquote>
      <blockquote v-if="entry.yuChanSaid" class="quote-block">{{ display(entry.yuChanSaid) }}</blockquote>
      <div v-if="entry.song" class="song-card">{{ formatSong(display(entry.song)) }}</div>
      <p v-if="!entry.answer && !entry.xiYiSaid" class="whitespace-pre-wrap">{{ display(entry.fullText) }}</p>
    </div>
    <p v-else class="text-sm" style="color: var(--zw-muted)">
      {{ display('卷一《諸星問答論》未單列此曜專條，請至古籍文庫檢閱相關賦文。', false) }}
    </p>
    <template #footer>
      <el-button @click="handleCopy">{{ display('複製原文', false) }}</el-button>
      <el-button type="primary" @click="handleGoto">{{ display('跳轉古籍文庫', false) }}</el-button>
    </template>
  </el-dialog>
</template>

<script lang="ts">
import { computed, defineComponent } from 'vue';
import { useRouter } from 'vue-router';
import starData from '@/data/starDict.json';
import type { StarEntry } from '@/types';
import { useDisplayText } from '@/composables/useDisplayText';
import { copyText } from '@/utils/copy';

export default defineComponent({
  name: 'StarDialog',
  props: {
    modelValue: { type: Boolean, default: false },
    starName: { type: String, default: '' },
  },
  emits: {
    'update:modelValue': (_val: boolean) => true,
  },
  setup(props, { emit }) {
    const router = useRouter();
    const { display } = useDisplayText();
    const data = starData as {
      dict: Record<string, StarEntry>;
      alias: Record<string, string>;
    };

    const visible = computed({
      get: () => props.modelValue,
      set: (val: boolean) => emit('update:modelValue', val),
    });

    const entry = computed(() => {
      const key = data.alias[props.starName] || props.starName;
      return data.dict[key] ?? data.dict[key.replace(/星$/, '')];
    });

    const formatSong = (text: string) =>
      text
        .replace(/歌曰：?/g, '歌曰：\n')
        .split(/[，,]/)
        .map((s) => s.trim())
        .filter(Boolean)
        .join('\n');

    const handleCopy = () => {
      const e = entry.value;
      if (!e) return;
      const chunks = [e.question, e.answer, e.xiYiSaid, e.yuChanSaid, e.song].filter(Boolean);
      void copyText(chunks.join('\n'));
    };

    const handleGoto = () => {
      visible.value = false;
      void router.push({ path: '/book', hash: '#zhuxing-wenda' });
    };

    return { visible, entry, display, formatSong, handleCopy, handleGoto };
  },
});
</script>
