<template>
  <div class="page-container">
    <h1 class="mb-2 text-2xl font-semibold">{{ display('星曜詞典', false) }}</h1>
    <p class="lead">
      {{ display('條目全部取自卷一《諸星問答論》，點入只見問答原文。斗序據卷一，五行化氣據卷二', false) }}
      <router-link :to="{ path: '/book', hash: '#nanbeidou-wuxing' }">{{
        display('《論諸星分屬南北斗化吉凶并分屬五行》', false)
      }}</router-link>
      {{ display('。', false) }}
    </p>

    <section v-for="sec in sections" :key="sec.id" class="block">
      <h2>{{ display(sec.title, false) }}</h2>
      <p class="hint">{{ display(sec.hint, false) }}</p>
      <div v-for="g in sec.groups" :key="g.title" class="sub">
        <h3>{{ display(g.title, false) }}</h3>
        <p v-if="g.hint" class="subhint">{{ display(g.hint, false) }}</p>
        <div class="grid grid-cols-2 gap-3 sm:grid-cols-3 md:grid-cols-4">
          <router-link
            v-for="name in g.names"
            :key="name"
            :to="`/star-dict/${encodeURIComponent(name)}`"
            class="card"
            :style="cardStyle"
          >
            <span v-if="starTag(name)" class="tag">{{ display(starTag(name), false) }}</span>
            <b>{{ display(name, false) }}</b>
            <span v-if="starLine(name)" class="line">{{ display(starLine(name), false) }}</span>
          </router-link>
        </div>
      </div>
    </section>
  </div>
</template>

<script lang="ts">
import { defineComponent } from 'vue';
import starData from '@/data/starDict.json';
import { buildStarSections, starLine, starTag } from '@/data/starGroups';
import { useDisplayText } from '@/composables/useDisplayText';

export default defineComponent({
  name: 'StarDictPage',
  setup() {
    const { display } = useDisplayText();
    const stars = (starData as { stars: string[] }).stars;
    const sections = buildStarSections(stars);
    const cardStyle = {
      background: 'var(--zw-paper)',
      borderColor: 'var(--zw-line)',
      color: 'var(--zw-ink)',
    };
    return { display, sections, starTag, starLine, cardStyle };
  },
});
</script>

<style scoped>
.lead,
.hint,
.subhint {
  margin: 0 0 14px;
  font-size: 13px;
  line-height: 1.7;
  color: var(--zw-muted);
  letter-spacing: 0.04em;
}
.lead a {
  color: var(--zw-gold);
  text-decoration: underline;
  text-underline-offset: 3px;
}
.block {
  margin-bottom: 32px;
}
.block h2 {
  margin: 0 0 8px;
  font-size: 18px;
  letter-spacing: 0.2em;
  color: var(--zw-primary);
}
.sub {
  margin-bottom: 20px;
}
.sub h3 {
  margin: 0 0 6px;
  font-size: 14px;
  letter-spacing: 0.16em;
  color: var(--zw-gold);
}
.card {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 4px;
  border: 1px solid var(--zw-line);
  border-radius: 10px;
  padding: 14px 10px;
  text-align: center;
  text-decoration: none;
}
.card:hover {
  border-color: var(--zw-gold);
}
.tag {
  font-size: 11px;
  letter-spacing: 0.12em;
  color: var(--zw-gold);
}
.card b {
  font-weight: 600;
  letter-spacing: 0.12em;
}
.line {
  font-size: 11px;
  line-height: 1.5;
  color: var(--zw-muted);
  letter-spacing: 0.04em;
}
</style>
