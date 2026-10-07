<template>
  <div class="star-map-stage">
    <svg
      class="star-map"
      viewBox="0 0 800 480"
      role="img"
      :aria-label="display('紫微垣星象示意', false)"
      preserveAspectRatio="xMidYMid slice"
    >
      <defs>
        <radialGradient :id="skyId" cx="50%" cy="40%" r="70%">
          <stop offset="0%" stop-color="#2a2148" />
          <stop offset="100%" stop-color="#0b1020" />
        </radialGradient>
        <filter :id="glowId" x="-80%" y="-80%" width="260%" height="260%">
          <feGaussianBlur stdDeviation="2.4" result="b" />
          <feMerge>
            <feMergeNode in="b" />
            <feMergeNode in="b" />
            <feMergeNode in="SourceGraphic" />
          </feMerge>
        </filter>
        <linearGradient :id="lineGlowId" x1="0%" y1="0%" x2="100%" y2="0%">
          <stop offset="0%" stop-color="#C8A967" stop-opacity="0.15" />
          <stop offset="45%" stop-color="#C8A967" stop-opacity="0.35" />
          <stop offset="50%" stop-color="#f3e2b0" stop-opacity="0.95" />
          <stop offset="55%" stop-color="#C8A967" stop-opacity="0.35" />
          <stop offset="100%" stop-color="#C8A967" stop-opacity="0.15" />
          <animate attributeName="x1" values="-100%;100%" dur="4.5s" repeatCount="indefinite" />
          <animate attributeName="x2" values="0%;200%" dur="4.5s" repeatCount="indefinite" />
        </linearGradient>
      </defs>

      <rect width="800" height="480" :fill="`url(#${skyId})`" />
      <rect
        x="12"
        y="12"
        width="776"
        height="456"
        fill="none"
        stroke="#C8A967"
        stroke-opacity="0.35"
      />
      <text
        x="40"
        y="48"
        fill="#C8A967"
        font-family="Noto Serif SC, Songti SC, serif"
        font-size="18"
        letter-spacing="6"
      >
        {{ display('紫微垣 · 星象示意', false) }}
      </text>

      <g class="stars" fill="#f3ebd8" :filter="`url(#${glowId})`">
        <circle
          v-for="(s, i) in stars"
          :key="i"
          class="star"
          :cx="s[0]"
          :cy="s[1]"
          :r="s[2]"
          :style="starAnim(i)"
        />
      </g>

      <g class="constellation" fill="none" stroke-width="1.15">
        <path
          class="line-base"
          d="M280 250 L340 210 L400 240 L460 200 L520 260 L460 300 L400 280 L340 300 Z"
        />
        <path
          class="line-flow"
          :stroke="`url(#${lineGlowId})`"
          d="M280 250 L340 210 L400 240 L460 200 L520 260 L460 300 L400 280 L340 300 Z"
        />
        <path class="line-base line-arc" d="M180 70 L240 110 L300 80 L360 130 L420 95" />
        <path
          class="line-flow line-arc"
          :stroke="`url(#${lineGlowId})`"
          d="M180 70 L240 110 L300 80 L360 130 L420 95"
        />
        <circle class="ziwei-ring" cx="400" cy="250" r="38" />
      </g>

      <text
        x="400"
        y="256"
        text-anchor="middle"
        fill="#C8A967"
        font-family="Noto Serif SC, Songti SC, serif"
        font-size="14"
      >
        {{ display('紫微', false) }}
      </text>
    </svg>
  </div>
</template>

<script lang="ts">
import { defineComponent } from 'vue';
import { useDisplayText } from '@/composables/useDisplayText';

/** [cx, cy, r] — 略放大半径，H5 上闪烁更易辨认 */
const STARS: Array<[number, number, number]> = [
  [120, 90, 2.1],
  [180, 70, 1.5],
  [240, 110, 2.4],
  [300, 80, 1.8],
  [360, 130, 1.5],
  [420, 95, 2.6],
  [480, 70, 1.9],
  [540, 120, 1.5],
  [600, 85, 2.2],
  [660, 140, 1.7],
  [720, 100, 2],
  [100, 200, 1.5],
  [160, 230, 2.1],
  [220, 190, 1.8],
  [280, 250, 2.6],
  [340, 210, 1.5],
  [400, 240, 2.3],
  [460, 200, 1.9],
  [520, 260, 1.5],
  [580, 220, 2.4],
  [640, 270, 1.8],
  [700, 230, 2.1],
  [140, 320, 2],
  [200, 360, 1.5],
  [260, 330, 2.2],
  [320, 380, 1.8],
  [380, 340, 2.6],
  [440, 370, 1.5],
  [500, 330, 2.1],
  [560, 390, 1.7],
  [620, 350, 2.3],
  [680, 400, 1.5],
  [740, 360, 1.9],
];

export default defineComponent({
  name: 'StarMap',
  setup() {
    const { display } = useDisplayText();
    const uid = Math.random().toString(36).slice(2, 8);

    const starAnim = (i: number) => {
      const variant = i % 3;
      return {
        animationDelay: `${(i % 9) * 0.22}s`,
        animationDuration: `${1.35 + (i % 6) * 0.28}s`,
        animationName: variant === 0 ? 'twinkle-bright' : variant === 1 ? 'twinkle' : 'twinkle-soft',
      };
    };

    return {
      display,
      stars: STARS,
      starAnim,
      skyId: `starSky-${uid}`,
      glowId: `starGlow-${uid}`,
      lineGlowId: `starLineGlow-${uid}`,
    };
  },
});
</script>

<style scoped>
.star-map-stage {
  width: 100%;
  height: 100%;
}

.star-map {
  width: 100%;
  height: 100%;
  display: block;
}

.line-base {
  stroke: #c8a967;
  stroke-opacity: 0.4;
}

.line-flow {
  stroke-opacity: 1;
  stroke-linecap: round;
  stroke-linejoin: round;
  stroke-dasharray: 28 220;
  animation: line-dash 5.5s linear infinite;
}

.line-flow.line-arc {
  animation-duration: 4.2s;
  animation-direction: reverse;
  stroke-dasharray: 18 160;
}

.ziwei-ring {
  stroke: #c8a967;
  stroke-opacity: 0.65;
  stroke-dasharray: 4 6;
}

.star {
  opacity: 0.55;
  transform-box: fill-box;
  transform-origin: center;
  animation-timing-function: ease-in-out;
  animation-iteration-count: infinite;
  will-change: opacity, transform;
}

@keyframes line-dash {
  to {
    stroke-dashoffset: -248;
  }
}

/* 强闪：几乎熄灭 → 爆亮 + 放大 */
@keyframes twinkle-bright {
  0%,
  100% {
    opacity: 0.12;
    transform: scale(0.55);
  }
  45% {
    opacity: 1;
    transform: scale(1.55);
  }
  55% {
    opacity: 1;
    transform: scale(1.35);
  }
}

/* 中闪 */
@keyframes twinkle {
  0%,
  100% {
    opacity: 0.18;
    transform: scale(0.7);
  }
  50% {
    opacity: 1;
    transform: scale(1.4);
  }
}

/* 柔闪：节奏错开，避免整片同闪 */
@keyframes twinkle-soft {
  0%,
  100% {
    opacity: 0.28;
    transform: scale(0.8);
  }
  40% {
    opacity: 0.95;
    transform: scale(1.25);
  }
  70% {
    opacity: 0.4;
    transform: scale(0.85);
  }
}

@media (prefers-reduced-motion: reduce) {
  .line-flow,
  .star {
    animation: none;
  }
  .star {
    opacity: 0.85;
    transform: none;
  }
}
</style>
