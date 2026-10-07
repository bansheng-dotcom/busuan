<template>
  <svg
    class="wuxing"
    viewBox="0 0 420 400"
    role="img"
    :aria-label="display('五行相生圖', false)"
  >
    <defs>
      <marker id="wuxingArrow" markerWidth="8" markerHeight="8" refX="6" refY="4" orient="auto">
        <path d="M0,0 L8,4 L0,8 Z" fill="var(--zw-gold)" />
      </marker>
    </defs>
    <polygon
      :points="pentagonPoints"
      fill="none"
      stroke="var(--zw-gold)"
      stroke-opacity="0.35"
      stroke-width="1"
    />
    <line
      v-for="(line, idx) in generateLines"
      :key="idx"
      :x1="line.x1"
      :y1="line.y1"
      :x2="line.x2"
      :y2="line.y2"
      class="sheng-line"
      stroke="var(--zw-gold)"
      stroke-width="1.4"
      marker-end="url(#wuxingArrow)"
    />
    <g v-for="el in elements" :key="el.name">
      <circle
        :cx="el.x"
        :cy="el.y"
        r="34"
        fill="var(--zw-paper)"
        :stroke="el.color"
        stroke-width="2"
      />
      <text
        :x="el.x"
        :y="el.y + 8"
        text-anchor="middle"
        :fill="el.color"
        font-size="26"
        font-family="Noto Serif SC, Songti SC, serif"
      >
        {{ display(el.name, false) }}
      </text>
    </g>
  </svg>
</template>

<script lang="ts">
import { computed, defineComponent } from 'vue';
import { useDisplayText } from '@/composables/useDisplayText';

interface WuXingNode {
  name: string;
  color: string;
  x: number;
  y: number;
}

export default defineComponent({
  name: 'WuXingDiagram',
  setup() {
    const { display } = useDisplayText();
    const cx = 210;
    const cy = 200;
    const r = 132;
    const names = ['火', '土', '金', '水', '木'] as const;
    const colors = ['#8b3a2a', '#8a6a32', '#c8a967', '#2c4a6e', '#2f5d3a'];

    const elements = computed<WuXingNode[]>(() =>
      names.map((name, i) => {
        const angle = ((-90 + i * 72) * Math.PI) / 180;
        return {
          name,
          color: colors[i],
          x: cx + r * Math.cos(angle),
          y: cy + r * Math.sin(angle),
        };
      }),
    );

    const pentagonPoints = computed(() =>
      elements.value.map((el: WuXingNode) => `${el.x},${el.y}`).join(' '),
    );

    const generateLines = computed(() => {
      const nodes = elements.value;
      return nodes.map((from: WuXingNode, i: number) => {
        const to = nodes[(i + 1) % nodes.length];
        const dx = to.x - from.x;
        const dy = to.y - from.y;
        const len = Math.hypot(dx, dy) || 1;
        const shrink = 40;
        return {
          x1: from.x + (dx / len) * shrink,
          y1: from.y + (dy / len) * shrink,
          x2: to.x - (dx / len) * shrink,
          y2: to.y - (dy / len) * shrink,
        };
      });
    });

    return { display, elements, pentagonPoints, generateLines };
  },
});
</script>

<style scoped>
.wuxing {
  width: min(420px, 100%);
  height: auto;
}
.sheng-line {
  stroke-dasharray: 6 8;
  animation: dash-flow 8s linear infinite;
}
@keyframes dash-flow {
  to {
    stroke-dashoffset: -56;
  }
}
@media (prefers-reduced-motion: reduce) {
  .sheng-line {
    animation: none;
  }
}
</style>
