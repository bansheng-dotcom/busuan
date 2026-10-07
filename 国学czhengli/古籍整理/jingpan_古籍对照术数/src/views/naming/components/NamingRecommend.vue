<template>
  <div class="recommend">
    <div class="toolbar">
      <button type="button" @click="handleRefresh">{{ display('換一批', false) }}</button>
      <button type="button" class="text-link" @click="handleGotoBook">
        {{ display('納音出處', false) }}
      </button>
    </div>

    <h3>{{ display('單字名', false) }}</h3>
    <ul v-if="single.length" class="list">
      <li v-for="item in single" :key="item.full">
        <div class="name">{{ display(item.full, false) }}</div>
        <div class="meta">
          <span v-for="ch in item.chars" :key="ch.char">
            {{ display(ch.char, false) }}（{{ display(ch.wuxing, false) }}）·
            {{ display(ch.note, false) }}
            <em>{{ display(ch.source, false) }}</em>
          </span>
        </div>
      </li>
    </ul>
    <p v-else class="empty">{{ display('該喜用五行精選字不足，請換一批或改用自選。', false) }}</p>

    <h3>{{ display('雙字名', false) }}</h3>
    <ul v-if="double.length" class="list">
      <li v-for="item in double" :key="item.full">
        <div class="name">{{ display(item.full, false) }}</div>
        <div class="meta">
          <span v-for="ch in item.chars" :key="ch.char + item.full">
            {{ display(ch.char, false) }}（{{ display(ch.wuxing, false) }}）·
            {{ display(ch.note, false) }}
            <em>{{ display(ch.source, false) }}</em>
          </span>
        </div>
      </li>
    </ul>
    <p v-else class="empty">{{ display('暫無雙字組合。', false) }}</p>
  </div>
</template>

<script lang="ts">
import { computed, defineComponent, ref, watch, type PropType } from 'vue';
import { useRouter } from 'vue-router';
import { useDisplayText } from '@/composables/useDisplayText';
import { useNamingSessionStore } from '@/store/namingSession';
import {
  buildRecommendations,
  type NamingAnalysis,
} from '@/utils/naming';

export default defineComponent({
  name: 'NamingRecommend',
  props: {
    analysis: {
      type: Object as PropType<NamingAnalysis>,
      required: true,
    },
    surname: {
      type: String,
      default: '',
    },
  },
  setup(props) {
    const { display } = useDisplayText();
    const router = useRouter();
    const session = useNamingSessionStore();
    const seed = ref(1);
    const packs = computed(() =>
      buildRecommendations({
        surname: props.surname,
        primary: props.analysis.preferred.primary,
        secondary: props.analysis.preferred.secondary,
        seed: seed.value,
      }),
    );
    const single = computed(() => packs.value.single);
    const double = computed(() => packs.value.double);
    watch(
      () => [props.analysis.dayNayin.ganZhi, props.surname],
      () => {
        seed.value = 1;
      },
    );
    const handleRefresh = () => {
      seed.value += 1;
    };
    const handleGotoBook = () => {
      session.markFromNaming();
      void router.push({ path: '/book', query: { from: 'naming' }, hash: '#huajia-nayin' });
    };
    return { display, single, double, handleRefresh, handleGotoBook };
  },
});
</script>

<style scoped>
.recommend {
  margin-top: 0.5rem;
}
.toolbar {
  display: flex;
  align-items: center;
  gap: 1rem;
  margin-bottom: 0.75rem;
}
.toolbar button {
  padding: 0.35rem 0.75rem;
  border: 1px solid var(--zw-line);
  border-radius: 8px;
  background: var(--zw-bg);
  color: var(--zw-ink);
  cursor: pointer;
}
.toolbar .text-link {
  padding: 0;
  border: none;
  background: none;
  color: var(--zw-primary);
  text-decoration: underline;
  font: inherit;
  font-size: 0.9rem;
  cursor: pointer;
}
h3 {
  margin: 0.85rem 0 0.45rem;
  font-size: 1rem;
}
.list {
  list-style: none;
  margin: 0;
  padding: 0;
  display: grid;
  gap: 0.55rem;
}
.list li {
  padding: 0.65rem 0.75rem;
  border: 1px solid var(--zw-line);
  border-radius: 10px;
  background: var(--zw-paper);
}
.name {
  font-size: 1.15rem;
  font-weight: 700;
  letter-spacing: 0.12em;
  color: var(--zw-gold);
}
.meta {
  margin-top: 0.35rem;
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
  font-size: 0.8rem;
  color: var(--zw-ink-muted);
  line-height: 1.5;
}
.meta em {
  font-style: normal;
  opacity: 0.85;
}
.empty {
  font-size: 0.85rem;
  color: var(--zw-ink-muted);
}
</style>
