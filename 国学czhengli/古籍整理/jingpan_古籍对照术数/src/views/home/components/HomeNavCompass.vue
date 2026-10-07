<template>
  <nav class="compass" :aria-label="display('站點導航', false)">
    <div class="compass-ring">
      <svg class="sky" viewBox="0 0 200 200" aria-hidden="true">
        <line
          class="polar"
          :x1="pointer.outer.x"
          :y1="pointer.outer.y"
          :x2="100"
          :y2="100"
        />
        <polyline class="dipper" :points="dipperPoints" fill="none" />
        <g v-for="star in skyStars" :key="star.name">
          <circle class="glow" :cx="star.x" :cy="star.y" r="4.2" />
          <circle class="core" :cx="star.x" :cy="star.y" r="1.7" />
        </g>
        <text class="caption" :x="caption.x" :y="caption.y" text-anchor="middle">
          {{ display('北斗', false) }}
        </text>
      </svg>

      <router-link
        v-for="item in gates"
        :key="item.path"
        :to="item.path"
        class="gate"
        :class="[`gate-${item.dir}`, { 'is-minor': item.minor }]"
      >
        <span class="dir">{{ display(item.dirLabel, false) }}</span>
        <strong>{{ display(item.title, false) }}</strong>
        <em>{{ display(item.hint, false) }}</em>
      </router-link>
      <span class="hub" aria-hidden="true">
        <i></i>
        <i></i>
      </span>
    </div>
  </nav>
</template>

<script lang="ts">
import { computed, defineComponent } from 'vue';
import { useDisplayText } from '@/composables/useDisplayText';
import { navDesc } from '@/data/siteNav';

/** 南上。角从正南顺时针。北斗落在西北空档，斗口朝圆心。 */
const SKY: { name: string; deg: number; r: number }[] = [
  { name: '搖光', deg: 304, r: 91 },
  { name: '開陽', deg: 286, r: 90 },
  { name: '玉衡', deg: 268, r: 88 },
  { name: '天權', deg: 248, r: 80 },
  { name: '天璣', deg: 248, r: 92 },
  { name: '天璇', deg: 218, r: 92 },
  { name: '天樞', deg: 218, r: 80 },
];

function toXY(deg: number, r: number) {
  const t = (deg * Math.PI) / 180;
  return { x: 100 + r * Math.sin(t), y: 100 - r * Math.cos(t) };
}

export default defineComponent({
  name: 'HomeNavCompass',
  setup() {
    const { display } = useDisplayText();
    const gates = [
      { path: '/chart', title: '排盤', hint: navDesc('/chart'), dir: 'south', dirLabel: '南', minor: false },
      { path: '/luopan', title: '羅盤', hint: navDesc('/luopan'), dir: 'se', dirLabel: '東南', minor: true },
      { path: '/book', title: '古籍', hint: navDesc('/book'), dir: 'east', dirLabel: '東', minor: false },
      { path: '/star-dict', title: '星曜', hint: navDesc('/star-dict'), dir: 'north', dirLabel: '北', minor: false },
      { path: '/almanac', title: '黃曆', hint: navDesc('/almanac'), dir: 'sw', dirLabel: '西南', minor: true },
      { path: '/pattern-dict', title: '格局', hint: navDesc('/pattern-dict'), dir: 'west', dirLabel: '西', minor: false },
    ];
    const skyStars = SKY.map((s) => ({ ...s, ...toXY(s.deg, s.r) }));
    const dipperPoints = computed(() => {
      const at = (name: string) => {
        const s = skyStars.find((x) => x.name === name);
        return s ? `${s.x},${s.y}` : '';
      };
      return [at('天樞'), at('天璇'), at('天璣'), at('天權'), at('玉衡'), at('開陽'), at('搖光')].join(' ');
    });
    const pointer = {
      outer: toXY(218, 92),
      inner: toXY(218, 80),
    };
    const caption = toXY(312, 96);
    return { display, gates, skyStars, dipperPoints, pointer, caption };
  },
});
</script>

<style scoped>
.compass {
  max-width: 640px;
  margin: 0 auto;
  padding: 28px 0 8px;
}
.compass-ring {
  position: relative;
  width: min(520px, 84%);
  aspect-ratio: 1;
  margin: 0 auto;
  border: 1px solid var(--zw-gold);
  border-radius: 50%;
  overflow: visible;
}
.compass-ring::before {
  content: '';
  position: absolute;
  inset: 18%;
  border: 1px dashed color-mix(in srgb, var(--zw-gold) 55%, transparent);
  border-radius: 50%;
}
.sky {
  position: absolute;
  inset: -18%;
  width: 136%;
  height: 136%;
  pointer-events: none;
  overflow: visible;
}
.dipper {
  stroke: var(--zw-gold);
  stroke-width: 1.15;
  stroke-linejoin: round;
  stroke-linecap: round;
  opacity: 0.88;
}
.polar {
  stroke: var(--zw-gold);
  stroke-width: 0.9;
  stroke-dasharray: 2.5 3.5;
  opacity: 0.55;
}
.glow {
  fill: var(--zw-gold);
  opacity: 0.22;
}
.core {
  fill: var(--zw-gold);
  stroke: var(--zw-ink);
  stroke-width: 0.35;
}
.caption {
  fill: var(--zw-gold);
  font-size: 8px;
  letter-spacing: 0.22em;
  font-family: 'Songti SC', 'STSong', serif;
}
.hub {
  position: absolute;
  left: 50%;
  top: 50%;
  width: 72px;
  height: 72px;
  margin: -36px 0 0 -36px;
  border-radius: 50%;
  overflow: hidden;
  border: 1px solid var(--zw-gold);
  z-index: 1;
}
.hub i:first-child,
.hub i:last-child {
  display: block;
  width: 36px;
  height: 72px;
}
.hub i:first-child {
  float: left;
  background: var(--zw-ink);
}
.hub i:last-child {
  float: right;
  background: var(--zw-paper);
}
.gate {
  position: absolute;
  z-index: 2;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 2px;
  min-width: 88px;
  color: var(--zw-ink);
  text-decoration: none;
  letter-spacing: 0.12em;
  transition: color 0.25s ease, transform 0.25s ease;
}
.gate:hover,
.gate:focus-visible {
  color: var(--zw-primary);
  transform: scale(1.06);
}
.dir {
  font-size: 12px;
  color: var(--zw-gold);
}
.gate strong {
  font-size: 22px;
  font-weight: 600;
}
.gate em {
  font-style: normal;
  font-size: 12px;
  letter-spacing: 0.08em;
  color: var(--zw-muted);
}
.gate.is-minor strong {
  font-size: 16px;
}
.gate.is-minor em {
  font-size: 11px;
}
.gate-south {
  left: 50%;
  top: 8%;
  transform: translateX(-50%);
}
.gate-south:hover,
.gate-south:focus-visible {
  transform: translateX(-50%) scale(1.06);
}
.gate-north {
  left: 50%;
  bottom: 8%;
  transform: translateX(-50%);
}
.gate-north:hover,
.gate-north:focus-visible {
  transform: translateX(-50%) scale(1.06);
}
.gate-east {
  top: 50%;
  right: 6%;
  transform: translateY(-50%);
}
.gate-east:hover,
.gate-east:focus-visible {
  transform: translateY(-50%) scale(1.06);
}
.gate-west {
  top: 50%;
  left: 6%;
  transform: translateY(-50%);
}
.gate-west:hover,
.gate-west:focus-visible {
  transform: translateY(-50%) scale(1.06);
}
.gate-se {
  top: 22%;
  right: 12%;
}
.gate-sw {
  top: 22%;
  left: 12%;
}
@media (max-width: 640px) {
  .compass-ring {
    aspect-ratio: auto;
    height: auto;
    border: 0;
    border-radius: 0;
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 20px 12px;
    padding: 8px 0 4px;
  }
  .compass-ring::before,
  .hub,
  .sky {
    display: none;
  }
  .gate,
  .gate-south,
  .gate-north,
  .gate-east,
  .gate-west,
  .gate-se,
  .gate-sw {
    position: static;
    transform: none;
  }
  .gate:hover,
  .gate:focus-visible,
  .gate-south:hover,
  .gate-north:hover,
  .gate-east:hover,
  .gate-west:hover {
    transform: none;
  }
}
</style>
