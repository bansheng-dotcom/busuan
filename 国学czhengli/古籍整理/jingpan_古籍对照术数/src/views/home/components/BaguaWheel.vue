<template>
  <svg
    class="bagua-wheel"
    viewBox="0 0 400 400"
    role="img"
    :aria-label="display('後天八卦太極圖', false)"
  >
    <defs>
      <radialGradient id="baguaGlow" cx="50%" cy="50%" r="50%">
        <stop offset="0%" stop-color="var(--zw-gold)" stop-opacity="0.18" />
        <stop offset="70%" stop-color="var(--zw-gold)" stop-opacity="0.04" />
        <stop offset="100%" stop-color="var(--zw-gold)" stop-opacity="0" />
      </radialGradient>
    </defs>
    <circle cx="200" cy="200" r="198" fill="url(#baguaGlow)" />
    <circle cx="200" cy="200" r="188" fill="none" stroke="currentColor" stroke-opacity="0.22" />
    <circle cx="200" cy="200" r="132" fill="none" stroke="var(--zw-gold)" stroke-opacity="0.45" stroke-width="1.2" />
    <g v-for="item in placed" :key="item.name" :transform="`translate(${item.x}, ${item.y})`">
      <text
        x="0"
        y="-22"
        text-anchor="middle"
        fill="var(--zw-gold)"
        font-size="13"
        font-family="Noto Serif SC, Songti SC, serif"
      >
        {{ display(item.name, false) }}
      </text>
      <g v-for="(yao, idx) in item.drawn" :key="idx" :transform="`translate(0, ${idx * 11})`">
        <rect v-if="yao === 1" x="-18" y="0" width="36" height="6" fill="currentColor" />
        <template v-else>
          <rect x="-18" y="0" width="14" height="6" fill="currentColor" />
          <rect x="4" y="0" width="14" height="6" fill="currentColor" />
        </template>
      </g>
    </g>
    <g transform="translate(200, 200)">
      <g class="taiji-spin">
        <circle r="54" fill="currentColor" />
        <path d="M0,-54 A54,54 0 0 1 0,54 A27,27 0 0 1 0,0 A27,27 0 0 0 0,-54 Z" fill="var(--zw-paper)" />
        <circle cy="-27" r="9" fill="var(--zw-paper)" />
        <circle cy="27" r="9" fill="currentColor" />
      </g>
    </g>
  </svg>
</template>

<script lang="ts">
import { defineComponent } from 'vue';
import { useDisplayText } from '@/composables/useDisplayText';

/** 后天八卦，南离居上。爻序自下而上：1 阳，0 阴。 */
const TRIGRAMS = [
  { name: '離', yaos: [1, 0, 1], angle: 0 },
  { name: '坤', yaos: [0, 0, 0], angle: 45 },
  { name: '兌', yaos: [1, 1, 0], angle: 90 },
  { name: '乾', yaos: [1, 1, 1], angle: 135 },
  { name: '坎', yaos: [0, 1, 0], angle: 180 },
  { name: '艮', yaos: [0, 0, 1], angle: 225 },
  { name: '震', yaos: [1, 0, 0], angle: 270 },
  { name: '巽', yaos: [0, 1, 1], angle: 315 },
];

export default defineComponent({
  name: 'BaguaWheel',
  setup() {
    const { display } = useDisplayText();
    const radius = 142;
    const placed = TRIGRAMS.map((item) => {
      const rad = ((item.angle - 90) * Math.PI) / 180;
      return {
        name: item.name,
        drawn: [...item.yaos].reverse(),
        x: 200 + radius * Math.cos(rad),
        y: 200 + radius * Math.sin(rad),
      };
    });
    return { display, placed };
  },
});
</script>

<style scoped>
.bagua-wheel {
  width: 100%;
  height: auto;
  color: var(--zw-ink);
  overflow: visible;
}
.taiji-spin {
  transform-origin: 0 0;
  animation: taiji-turn 48s linear infinite;
}
@keyframes taiji-turn {
  to {
    transform: rotate(360deg);
  }
}
@media (prefers-reduced-motion: reduce) {
  .taiji-spin {
    animation: none;
  }
}
</style>
