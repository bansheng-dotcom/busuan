<template>
  <section class="summary">
    <div class="day">
      <span class="label">{{ display('日柱納音（本氣）', false) }}</span>
      <strong>
        {{ display(analysis.dayNayin.ganZhi, false) }}
        ·
        {{ display(analysis.dayNayin.name, false) }}
        ·
        {{ display(analysis.dayNayin.wuxing, false) }}
      </strong>
    </div>
    <dl class="pillars">
      <div v-for="item in analysis.pillars" :key="item.label" :class="{ focus: item.label === '日柱' }">
        <dt>{{ display(item.label, false) }}</dt>
        <dd>{{ display(item.ganZhi, false) }}</dd>
        <dd class="sub">{{ display(`${item.name} · ${item.wuxing}`, false) }}</dd>
      </div>
    </dl>
    <div class="prefer">
      <span>{{ display('主喜用', false) }}：<b>{{ display(analysis.preferred.primary, false) }}</b></span>
      <span>{{ display('次喜用', false) }}：<b>{{ display(analysis.preferred.secondary, false) }}</b></span>
      <span class="avoid">{{ display('忌用', false) }}：{{ display(analysis.preferred.avoid, false) }}</span>
    </div>
    <p class="rule">{{ display(analysis.ruleText, false) }}</p>
    <p class="link-row">
      <button type="button" class="text-link" @click="handleGotoBook">
        {{ display('查看卷二《六十花甲子納音歌》原文', false) }}
      </button>
    </p>
  </section>
</template>

<script lang="ts">
import { defineComponent, type PropType } from 'vue';
import { useRouter } from 'vue-router';
import { useDisplayText } from '@/composables/useDisplayText';
import { useNamingSessionStore } from '@/store/namingSession';
import type { NamingAnalysis } from '@/utils/naming';

export default defineComponent({
  name: 'NamingSummary',
  props: {
    analysis: {
      type: Object as PropType<NamingAnalysis>,
      required: true,
    },
  },
  setup() {
    const { display } = useDisplayText();
    const router = useRouter();
    const session = useNamingSessionStore();
    const handleGotoBook = () => {
      session.markFromNaming();
      void router.push({ path: '/book', query: { from: 'naming' }, hash: '#huajia-nayin' });
    };
    return { display, handleGotoBook };
  },
});
</script>

<style scoped>
.summary {
  margin-top: 1rem;
  padding: 1rem 1.1rem;
  border: 1px solid var(--zw-line);
  border-radius: 12px;
  background: var(--zw-paper);
}
.day {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
  margin-bottom: 0.85rem;
}
.day .label {
  font-size: 0.8rem;
  color: var(--zw-ink-muted);
}
.day strong {
  font-size: 1.15rem;
  color: var(--zw-gold);
}
.pillars {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(110px, 1fr));
  gap: 0.65rem;
  margin: 0 0 0.85rem;
}
.pillars > div {
  padding: 0.5rem 0.6rem;
  border-radius: 8px;
  border: 1px solid var(--zw-line);
}
.pillars > div.focus {
  border-color: var(--zw-gold);
  background: color-mix(in srgb, var(--zw-gold) 12%, transparent);
}
dt {
  font-size: 0.75rem;
  color: var(--zw-ink-muted);
}
dd {
  margin: 0.15rem 0 0;
  font-weight: 600;
}
dd.sub {
  font-weight: 400;
  font-size: 0.8rem;
  color: var(--zw-ink-muted);
}
.prefer {
  display: flex;
  flex-wrap: wrap;
  gap: 0.75rem 1.25rem;
  margin-bottom: 0.65rem;
  font-size: 0.92rem;
}
.prefer .avoid {
  color: var(--zw-ink-muted);
}
.rule {
  margin: 0 0 0.5rem;
  font-size: 0.85rem;
  line-height: 1.65;
  color: var(--zw-ink-muted);
}
.link-row .text-link {
  padding: 0;
  border: none;
  background: none;
  color: var(--zw-primary);
  text-decoration: underline;
  font: inherit;
  font-size: 0.9rem;
  cursor: pointer;
}
</style>
