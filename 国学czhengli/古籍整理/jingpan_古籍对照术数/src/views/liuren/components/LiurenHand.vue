<template>
  <figure class="hand-fig" :aria-label="display('左手掌訣示意', false)">
    <svg class="hand" viewBox="0 0 320 380" role="img">
      <title>{{ display('左手六壬掌訣', false) }}</title>
      <defs>
        <marker id="arr" markerWidth="7" markerHeight="7" refX="6" refY="3.5" orient="auto">
          <path d="M0,0 L7,3.5 L0,7 Z" class="arrow-head" />
        </marker>
      </defs>

      <!--
        左手：俯視掌心朝上，拇指在左。
        四指自左向右：食、中、無名、小。
      -->

      <!-- 掌心 -->
      <path
        class="skin"
        d="M108 190
           C96 236 104 296 132 326
           C154 348 198 350 228 330
           C254 312 264 264 258 220
           C254 192 238 172 210 164
           L168 156
           C140 152 118 164 108 190 Z"
      />

      <!-- 拇指（左側） -->
      <path
        class="skin"
        d="M118 186
           C96 168 64 172 52 196
           C42 216 52 242 76 250
           C98 258 116 240 122 218 Z"
      />

      <!-- 食指 -->
      <path
        class="skin"
        d="M128 162
           C122 122 116 78 122 44
           C126 22 144 18 152 40
           C158 58 158 112 156 158 Z"
      />
      <!-- 中指 -->
      <path
        class="skin"
        d="M158 158
           C156 116 156 70 164 36
           C170 14 188 14 194 36
           C200 54 198 112 196 156 Z"
      />
      <!-- 無名指 -->
      <path
        class="skin"
        d="M196 158
           C196 122 198 78 206 48
           C212 28 230 28 236 48
           C242 64 240 118 238 156 Z"
      />
      <!-- 小指 -->
      <path
        class="skin"
        d="M238 164
           C240 134 246 100 254 76
           C260 56 276 58 280 78
           C284 94 278 130 274 162 Z"
      />

      <!-- 關節 -->
      <g class="joint" fill="none">
        <path d="M128 86 H150" />
        <path d="M130 122 H152" />
        <path d="M164 76 H190" />
        <path d="M164 118 H190" />
        <path d="M206 86 H232" />
        <path d="M208 124 H232" />
      </g>

      <!-- 順時針：①↑②→③→④↓⑤←⑥←① -->
      <g class="arrows" fill="none">
        <path d="M140 118 L140 78" marker-end="url(#arr)" />
        <path d="M158 52 L170 46" marker-end="url(#arr)" />
        <path d="M198 42 L210 46" marker-end="url(#arr)" />
        <path d="M222 72 L222 112" marker-end="url(#arr)" />
        <path d="M208 136 L190 136" marker-end="url(#arr)" />
        <path d="M168 136 L152 136" marker-end="url(#arr)" />
      </g>

      <g
        v-for="spot in spots"
        :key="spot.index"
        class="spot"
        :class="{ hit: activeIndex === spot.index }"
        @click="$emit('select', spot.index)"
      >
        <circle :cx="spot.x" :cy="spot.y" r="15" class="dot" />
        <text :x="spot.x" :y="spot.y + 1" text-anchor="middle" dominant-baseline="middle" class="num">
          {{ spot.index + 1 }}
        </text>
        <text :x="spot.lx" :y="spot.ly" text-anchor="middle" class="label">
          {{ display(`${spot.index + 1}${spot.name}`, false) }}
        </text>
      </g>

      <text x="160" y="366" text-anchor="middle" class="caption">
        {{ display('左手 · 掌心朝上 · 順時針掐指', false) }}
      </text>
    </svg>
    <figcaption>
      {{
        display(
          '①食指根大安 → ②食指尖留連 → ③中指尖速喜 → ④無名指尖赤口 → ⑤無名指根小吉 → ⑥中指根空亡。',
          false,
        )
      }}
    </figcaption>
  </figure>
</template>

<script lang="ts">
import { defineComponent } from 'vue';
import { useDisplayText } from '@/composables/useDisplayText';
import { LIUREN_PALACES } from '@/utils/liuren';

/** 左手掌心朝上（拇指在左），對照常見掌訣圖 */
const SPOTS = [
  { index: 0, x: 140, y: 132, lx: 92, ly: 136, name: LIUREN_PALACES[0].name }, // ①大安 食指根
  { index: 1, x: 140, y: 52, lx: 92, ly: 40, name: LIUREN_PALACES[1].name }, // ②留連 食指尖
  { index: 2, x: 180, y: 42, lx: 180, ly: 16, name: LIUREN_PALACES[2].name }, // ③速喜 中指尖
  { index: 3, x: 222, y: 52, lx: 268, ly: 40, name: LIUREN_PALACES[3].name }, // ④赤口 無名指尖
  { index: 4, x: 222, y: 132, lx: 268, ly: 136, name: LIUREN_PALACES[4].name }, // ⑤小吉 無名指根
  { index: 5, x: 180, y: 132, lx: 180, ly: 164, name: LIUREN_PALACES[5].name }, // ⑥空亡 中指根
];

export default defineComponent({
  name: 'LiurenHand',
  props: {
    activeIndex: { type: Number, default: -1 },
  },
  emits: {
    select: (_index: number) => true,
  },
  setup() {
    const { display } = useDisplayText();
    return { display, spots: SPOTS };
  },
});
</script>

<style scoped>
.hand-fig {
  margin: 0 0 1rem;
  text-align: center;
}
.hand {
  width: min(100%, 340px);
  height: auto;
  display: block;
  margin: 0 auto;
}
.skin {
  fill: color-mix(in srgb, var(--zw-paper) 70%, #e8c9a0);
  stroke: var(--zw-gold);
  stroke-width: 1.5;
}
.joint {
  stroke: color-mix(in srgb, var(--zw-gold) 50%, transparent);
  stroke-width: 1;
}
.arrows {
  stroke: #c45c26;
  stroke-width: 1.8;
  opacity: 0.85;
}
.arrow-head {
  fill: #c45c26;
}
.spot {
  cursor: pointer;
}
.dot {
  fill: var(--zw-paper);
  stroke: var(--zw-primary);
  stroke-width: 1.6;
  transition: fill 0.15s ease, stroke 0.15s ease;
}
.num {
  fill: var(--zw-primary);
  font-size: 11px;
  font-weight: 700;
  pointer-events: none;
}
.label {
  fill: var(--zw-ink);
  font-size: 12px;
  letter-spacing: 0.06em;
  pointer-events: none;
}
.spot.hit .dot {
  fill: var(--zw-gold);
  stroke: var(--zw-primary);
}
.spot.hit .num {
  fill: var(--zw-ink);
}
.spot.hit .label {
  fill: var(--zw-primary);
  font-weight: 700;
}
.caption {
  fill: var(--zw-muted);
  font-size: 11px;
  letter-spacing: 0.14em;
}
figcaption {
  margin-top: 0.35rem;
  font-size: 0.78rem;
  line-height: 1.55;
  color: var(--zw-muted);
  letter-spacing: 0.04em;
}
</style>
