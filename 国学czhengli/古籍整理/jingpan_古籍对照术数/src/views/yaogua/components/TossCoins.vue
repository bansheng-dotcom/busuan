<template>
  <div
    class="arena"
    :class="{ tossing, 'is-six': isSix, pouring: isSix }"
    aria-hidden="true"
  >
    <!-- 六錢模式：左側錢筒 -->
    <div v-if="isSix" class="bucket" :class="{ shaking: tossing }">
      <div class="bucket-inner">
        <div class="bucket-lid" />
        <div class="bucket-rim" />
        <div class="bucket-body">
          <i class="band band-1" />
          <i class="band band-2" />
          <i class="band band-3" />
          <i class="grain" />
          <span class="bucket-label">{{ display('錢筒', false) }}</span>
        </div>
        <div class="bucket-spout" />
        <div class="bucket-base" />
        <!-- 搖筒雙手：搖完淡出 -->
        <div class="hands" aria-hidden="true">
          <svg class="hand hand-left" viewBox="0 0 64 80" fill="none">
            <path
              class="palm"
              d="M18 28c-4 2-8 10-7 22 1 10 6 18 16 20h14c8-1 14-8 15-18 1-12-2-22-8-26-2-8-8-14-14-14-7 0-12 5-14 12-1-3-3-5-6-5-4 0-7 4-6 9z"
            />
            <path class="finger" d="M22 10c-1-6 3-10 7-9 3 1 4 5 4 10v18c0 3-2 5-5 5s-5-2-5-5V10z" />
            <path class="finger" d="M32 6c0-6 4-9 7-8 3 1 4 5 4 11v20c0 3-2 5-5 5s-5-2-5-5V6z" />
            <path class="finger" d="M42 10c0-5 3-8 6-7 3 1 4 4 4 9v18c0 3-2 5-4 5s-5-2-5-5V10z" />
            <path class="thumb" d="M12 34c-6 2-10 8-9 14 1 5 5 8 10 7 3-1 5-4 6-8l2-12c1-3-1-5-4-5-2 0-4 1-5 4z" />
          </svg>
          <svg class="hand hand-right" viewBox="0 0 64 80" fill="none">
            <path
              class="palm"
              d="M18 28c-4 2-8 10-7 22 1 10 6 18 16 20h14c8-1 14-8 15-18 1-12-2-22-8-26-2-8-8-14-14-14-7 0-12 5-14 12-1-3-3-5-6-5-4 0-7 4-6 9z"
            />
            <path class="finger" d="M22 10c-1-6 3-10 7-9 3 1 4 5 4 10v18c0 3-2 5-5 5s-5-2-5-5V10z" />
            <path class="finger" d="M32 6c0-6 4-9 7-8 3 1 4 5 4 11v20c0 3-2 5-5 5s-5-2-5-5V6z" />
            <path class="finger" d="M42 10c0-5 3-8 6-7 3 1 4 4 4 9v18c0 3-2 5-4 5s-5-2-5-5V10z" />
            <path class="thumb" d="M12 34c-6 2-10 8-9 14 1 5 5 8 10 7 3-1 5-4 6-8l2-12c1-3-1-5-4-5-2 0-4 1-5 4z" />
          </svg>
        </div>
      </div>
      <div class="bucket-shadow" />
    </div>

    <div class="floor" />
    <div
      v-for="(face, i) in faces"
      v-show="showCoins"
      :key="`${tossKey}-${i}`"
      class="coin-wrap"
      :class="[
        isSix ? `stack-${i}` : `coin-${i}`,
        { tossing, pour: isSix },
      ]"
      :style="wrapStyle(i, face)"
    >
      <div class="coin-3d">
        <div class="face front">
          <i class="ring" />
          <i class="hole" />
          <span class="glyph">{{ display('陽', false) }}</span>
          <em>3</em>
        </div>
        <div class="face back">
          <i class="ring" />
          <i class="hole" />
          <span class="glyph">{{ display('陰', false) }}</span>
          <em>2</em>
        </div>
      </div>
      <div class="shadow" />
    </div>
  </div>
</template>

<script lang="ts">
import { computed, defineComponent, type PropType } from 'vue';
import { useDisplayText } from '@/composables/useDisplayText';
import type { CoinFace, SixPourSchedule } from '@/utils/yaogua';

/** 三錢橫排靜止位移 */
const HOME_3 = [-92, 0, 92];
/** 六錢豎排：0=初爻在最下，5=上爻在最上（translateY 負為上） */
const STACK_GAP = 54;

export default defineComponent({
  name: 'TossCoins',
  props: {
    faces: {
      type: Array as PropType<CoinFace[]>,
      required: true,
    },
    tossing: { type: Boolean, default: false },
    tossKey: { type: Number, default: 0 },
    /** 六錢模式：默認隱藏，灑出/成卦後才顯示 */
    revealed: { type: Boolean, default: true },
    /** 一次成卦隨機出幣節奏 */
    pourSchedule: {
      type: Object as PropType<SixPourSchedule | null>,
      default: null,
    },
  },
  setup(props) {
    const { display } = useDisplayText();
    const isSix = computed(() => props.faces.length === 6);
    const showCoins = computed(() => !isSix.value || props.revealed || props.tossing);

    const wrapStyle = (i: number, face: CoinFace) => {
      const spins = 3 + (i % 4);
      const endY = face === 3 ? 360 * spins : 360 * spins + 180;
      if (isSix.value) {
        const delay = props.pourSchedule?.delaysSec[i] ?? 0.35 + i * 0.32;
        const pourSec = props.pourSchedule?.pourSec ?? 0.85;
        return {
          '--delay': `${delay}s`,
          '--pour-coin': `${pourSec}s`,
          '--end-y': `${endY}deg`,
          '--end-z': `${(i % 2 === 0 ? -1 : 1) * (12 + i * 3)}deg`,
          '--rest-y': face === 3 ? '0deg' : '180deg',
          '--home-x': '0px',
          '--home-y': `${-i * STACK_GAP}px`,
          '--mouth-x': `${-138 - (i % 3) * 4}px`,
          '--mouth-y': `${-188 + i * 6}px`,
          '--arc-x': `${-52 + (i % 2 === 0 ? -8 : 10)}px`,
          '--wobble': `${(i % 2 === 0 ? -1 : 1) * (8 + i)}px`,
        } as Record<string, string>;
      }
      return {
        '--delay': `${i * 0.08}s`,
        '--end-y': `${endY}deg`,
        '--end-z': `${(i - 1) * 18}deg`,
        '--lift': `${110 + i * 12}px`,
        '--drift': `${(i - 1) * 28}px`,
        '--rest-y': face === 3 ? '0deg' : '180deg',
        '--home-x': `${HOME_3[i] ?? 0}px`,
        '--home-y': '0px',
      } as Record<string, string>;
    };

    return { display, isSix, showCoins, wrapStyle };
  },
});
</script>

<style scoped>
.arena {
  position: relative;
  height: 200px;
  margin: 0 auto 1rem;
  max-width: 360px;
  perspective: 900px;
  overflow: hidden;
}
.arena.is-six {
  height: 440px;
  max-width: 440px;
}
.bucket {
  position: absolute;
  left: 4px;
  top: 50%;
  z-index: 4;
  width: 148px;
  margin-top: -122px;
  pointer-events: none;
  transform-origin: 30% 85%;
}
.bucket-inner {
  position: relative;
  filter: drop-shadow(2px 6px 8px rgba(44, 36, 22, 0.28));
}
.bucket-lid {
  position: absolute;
  left: 22px;
  top: -18px;
  width: 92px;
  height: 28px;
  border-radius: 50% 50% 40% 40%;
  background: linear-gradient(160deg, #f0d48a 0%, #c49a3c 45%, #8a6420 100%);
  border: 1.5px solid #6e5018;
  box-shadow: inset 0 2px 4px rgba(255, 255, 255, 0.35);
  transform: rotate(-8deg);
  z-index: 3;
}
.bucket-lid::after {
  content: '';
  position: absolute;
  left: 50%;
  top: -8px;
  width: 18px;
  height: 12px;
  margin-left: -9px;
  border-radius: 3px;
  background: linear-gradient(180deg, #e8c878, #a67c2e);
  border: 1px solid #6e5018;
}
.bucket-rim {
  position: relative;
  z-index: 2;
  height: 20px;
  margin: 0 10px;
  border-radius: 12px 12px 4px 4px;
  background: linear-gradient(180deg, #f3dfa0 0%, #d4a84a 40%, #a67c2e 100%);
  border: 1.5px solid #8a6420;
  box-shadow: inset 0 2px 3px rgba(255, 255, 255, 0.4);
}
.bucket-body {
  position: relative;
  margin: -2px 16px 0;
  height: 200px;
  border-radius: 10px 10px 26px 26px / 8px 8px 34px 34px;
  background:
    linear-gradient(90deg, rgba(0, 0, 0, 0.18) 0%, transparent 18%, transparent 82%, rgba(0, 0, 0, 0.22) 100%),
    linear-gradient(180deg, #c8923a 0%, #a67c2e 28%, #8f6a28 62%, #5c4214 100%);
  border: 1.5px solid #6e5018;
  border-top: 0;
  overflow: hidden;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: inset 0 10px 16px rgba(255, 255, 255, 0.12);
}
.bucket-body .grain {
  position: absolute;
  inset: 0;
  background: repeating-linear-gradient(
    95deg,
    transparent 0 7px,
    rgba(255, 255, 255, 0.04) 7px 8px,
    transparent 8px 15px,
    rgba(0, 0, 0, 0.05) 15px 16px
  );
  pointer-events: none;
}
.bucket-body .band {
  position: absolute;
  left: -2px;
  right: -2px;
  height: 7px;
  border-radius: 2px;
  background: linear-gradient(180deg, #e8c878, #8a6420 55%, #5c4214);
  border: 1px solid #5c4214;
  box-shadow: 0 1px 2px rgba(0, 0, 0, 0.25);
}
.band-1 { top: 22%; }
.band-2 { top: 48%; }
.band-3 { top: 74%; }
.bucket-label {
  position: relative;
  z-index: 1;
  font-size: 1.05rem;
  font-weight: 700;
  letter-spacing: 0.32em;
  writing-mode: vertical-rl;
  color: #f7ecd2;
  text-shadow: 0 1px 2px rgba(40, 28, 10, 0.55);
}
.bucket-spout {
  position: absolute;
  right: -8px;
  top: 40%;
  width: 28px;
  height: 46px;
  border-radius: 0 12px 16px 0;
  background: linear-gradient(90deg, #8f6a28, #c49a3c 60%, #e8c878);
  border: 1.5px solid #6e5018;
  border-left: 0;
  box-shadow: inset -2px 0 4px rgba(255, 255, 255, 0.25);
  z-index: 1;
}
.bucket-spout::after {
  content: '';
  position: absolute;
  right: 4px;
  top: 10px;
  bottom: 10px;
  width: 10px;
  border-radius: 4px;
  background: rgba(40, 28, 10, 0.45);
}
.bucket-base {
  margin: -4px 12px 0;
  height: 18px;
  border-radius: 0 0 18px 18px;
  background: linear-gradient(180deg, #6e5018, #3a2a10);
  border: 1.5px solid #3a2a10;
  border-top: 0;
}
.bucket-shadow {
  position: absolute;
  left: 18%;
  right: 8%;
  bottom: -10px;
  height: 14px;
  border-radius: 50%;
  background: rgba(44, 36, 22, 0.28);
  filter: blur(4px);
}
.hands {
  position: absolute;
  inset: 0;
  z-index: 6;
  opacity: 0;
  pointer-events: none;
  transition: opacity 0.5s ease 0.08s;
}
.hand {
  position: absolute;
  width: 84px;
  height: 104px;
  overflow: visible;
  filter: drop-shadow(1px 3px 3px rgba(44, 36, 22, 0.28));
}
.hand .palm,
.hand .finger,
.hand .thumb {
  fill: #e8b896;
  stroke: #b07858;
  stroke-width: 1.4;
  stroke-linejoin: round;
}
.hand .finger {
  fill: #eab898;
}
.hand .thumb {
  fill: #dfa888;
}
.hand-left {
  left: -38px;
  top: 42%;
  transform: rotate(-18deg);
}
.hand-right {
  right: -40px;
  top: 38%;
  transform: rotate(16deg) scaleX(-1);
}
.bucket.shaking .hands {
  opacity: 1;
  transition: opacity 0.18s ease;
}
.bucket.shaking .hand-left {
  animation: hand-grip-l 0.85s ease-in-out infinite;
}
.bucket.shaking .hand-right {
  animation: hand-grip-r 0.85s ease-in-out infinite;
}
@keyframes hand-grip-l {
  0%,
  100% {
    transform: rotate(-18deg) translate(0, 0);
  }
  25% {
    transform: rotate(-28deg) translate(-3px, 4px);
  }
  50% {
    transform: rotate(-10deg) translate(3px, -2px);
  }
  75% {
    transform: rotate(-24deg) translate(-2px, 3px);
  }
}
@keyframes hand-grip-r {
  0%,
  100% {
    transform: rotate(16deg) scaleX(-1) translate(0, 0);
  }
  25% {
    transform: rotate(28deg) scaleX(-1) translate(-3px, 4px);
  }
  50% {
    transform: rotate(8deg) scaleX(-1) translate(3px, -2px);
  }
  75% {
    transform: rotate(22deg) scaleX(-1) translate(-2px, 3px);
  }
}
.bucket.shaking .bucket-inner {
  /* 整段出幣過程持續晃動，不中途靜止 */
  animation: bucket-rattle 0.95s ease-in-out infinite;
}
@keyframes bucket-rattle {
  0% {
    transform: rotate(10deg) translate(2px, 2px);
  }
  12% {
    transform: rotate(24deg) translate(6px, 5px);
  }
  25% {
    transform: rotate(6deg) translate(1px, 1px);
  }
  37% {
    transform: rotate(28deg) translate(7px, 6px);
  }
  50% {
    transform: rotate(8deg) translate(2px, 3px);
  }
  62% {
    transform: rotate(22deg) translate(5px, 4px);
  }
  75% {
    transform: rotate(4deg) translate(0, 2px);
  }
  87% {
    transform: rotate(26deg) translate(6px, 5px);
  }
  100% {
    transform: rotate(10deg) translate(2px, 2px);
  }
}
.arena.is-six .floor {
  left: 48%;
  right: 18%;
}
.floor {
  position: absolute;
  left: 28%;
  right: 28%;
  bottom: 18px;
  height: 14px;
  border-radius: 50%;
  background: radial-gradient(ellipse, rgba(44, 36, 22, 0.16), transparent 70%);
  filter: blur(2px);
}
.coin-wrap {
  position: absolute;
  left: 50%;
  bottom: 36px;
  width: 72px;
  height: 72px;
  margin-left: -36px;
  transform: translate(var(--home-x, 0), var(--home-y, 0));
  transform-style: preserve-3d;
  z-index: 1;
}
.arena.is-six .coin-wrap {
  left: 68%;
  width: 56px;
  height: 56px;
  margin-left: -28px;
  bottom: 28px;
}
.coin-3d {
  position: relative;
  width: 100%;
  height: 100%;
  transform-style: preserve-3d;
}
.coin-wrap:not(.tossing) .coin-3d {
  transform: rotateY(var(--rest-y, 0deg)) rotateX(12deg);
}
.face {
  position: absolute;
  inset: 0;
  border-radius: 50%;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  backface-visibility: hidden;
  box-shadow:
    inset 0 2px 6px rgba(255, 255, 255, 0.35),
    inset 0 -4px 10px rgba(0, 0, 0, 0.28),
    0 4px 10px rgba(44, 36, 22, 0.22);
}
.face.front {
  background: radial-gradient(circle at 32% 28%, #ffe9b0 0%, #e0b45a 38%, #a67c2e 72%, #6e4f18 100%);
  color: #3a2a10;
  border: 2px solid #c49a3c;
}
.face.back {
  background: radial-gradient(circle at 32% 28%, #cfc7b8 0%, #8f8778 40%, #554e42 75%, #2e2a24 100%);
  color: #f2ebe0;
  border: 2px solid #6a6358;
  transform: rotateY(180deg);
}
.ring {
  position: absolute;
  inset: 6px;
  border-radius: 50%;
  border: 1.5px solid color-mix(in srgb, currentColor 35%, transparent);
  pointer-events: none;
}
.hole {
  position: absolute;
  width: 12px;
  height: 12px;
  border-radius: 2px;
  background: var(--zw-paper);
  box-shadow: inset 0 0 0 1.5px color-mix(in srgb, currentColor 40%, transparent);
  opacity: 0.92;
}
.glyph {
  position: relative;
  z-index: 1;
  margin-top: 14px;
  font-size: 0.8rem;
  font-weight: 700;
  letter-spacing: 0.1em;
}
.face em {
  position: relative;
  z-index: 1;
  font-style: normal;
  font-size: 0.6rem;
  opacity: 0.75;
}
.shadow {
  position: absolute;
  left: 12%;
  right: 12%;
  bottom: -8px;
  height: 8px;
  border-radius: 50%;
  background: rgba(44, 36, 22, 0.22);
  filter: blur(3px);
  opacity: 0.55;
}

/* —— 三錢拋擲 —— */
.coin-wrap.tossing:not(.pour) {
  animation: toss-flight 1.2s cubic-bezier(0.22, 0.7, 0.25, 1) var(--delay, 0s) both;
}
.coin-wrap.tossing:not(.pour) .coin-3d {
  animation: toss-spin 1.2s cubic-bezier(0.2, 0.55, 0.25, 1) var(--delay, 0s) both;
}
.coin-wrap.tossing:not(.pour) .shadow {
  animation: toss-shadow 1.2s cubic-bezier(0.22, 0.7, 0.25, 1) var(--delay, 0s) both;
}

/* —— 六錢：自筒口灑出，先出落底 —— */
.coin-wrap.pour.tossing {
  animation: pour-fall var(--pour-coin, 0.85s) cubic-bezier(0.22, 0.82, 0.28, 1) var(--delay, 0s)
    both;
  z-index: calc(10 + var(--z, 0));
}
.coin-wrap.pour.tossing .coin-3d {
  animation: pour-spin var(--pour-coin, 0.85s) cubic-bezier(0.2, 0.55, 0.25, 1) var(--delay, 0s)
    both;
}
.coin-wrap.pour.tossing .shadow {
  animation: pour-shadow var(--pour-coin, 0.85s) ease var(--delay, 0s) both;
}
.stack-0.pour.tossing { --z: 0; }
.stack-1.pour.tossing { --z: 1; }
.stack-2.pour.tossing { --z: 2; }
.stack-3.pour.tossing { --z: 3; }
.stack-4.pour.tossing { --z: 4; }
.stack-5.pour.tossing { --z: 5; }

@keyframes pour-fall {
  0% {
    opacity: 0;
    transform: translate(var(--mouth-x), var(--mouth-y)) scale(0.65);
  }
  10% {
    opacity: 1;
  }
  42% {
    transform: translate(var(--arc-x), calc(var(--home-y) - 36px)) scale(1.06);
  }
  72% {
    transform: translate(calc(var(--wobble) * 0.35), calc(var(--home-y) + 6px)) scale(0.98);
  }
  88% {
    transform: translate(0, calc(var(--home-y) - 4px)) scale(1.02);
  }
  100% {
    opacity: 1;
    transform: translate(var(--home-x), var(--home-y)) scale(1);
  }
}
@keyframes pour-spin {
  0% {
    transform: rotateX(70deg) rotateY(0deg) rotateZ(-30deg);
  }
  100% {
    transform: rotateX(14deg) rotateY(var(--end-y)) rotateZ(var(--end-z));
  }
}
@keyframes pour-shadow {
  0%,
  20% {
    opacity: 0;
  }
  100% {
    opacity: 0.5;
  }
}

@keyframes toss-flight {
  0% {
    transform: translate(var(--home-x), var(--home-y)) scale(1);
  }
  35% {
    transform: translate(
        calc(var(--home-x) + var(--drift)),
        calc(var(--home-y) - var(--lift))
      )
      scale(1.06);
  }
  70% {
    transform: translate(
        calc(var(--home-x) + var(--drift) * 0.35),
        calc(var(--home-y) - 28px)
      )
      scale(1);
  }
  82% {
    transform: translate(var(--home-x), calc(var(--home-y) + 6px)) scale(0.98);
  }
  92% {
    transform: translate(var(--home-x), calc(var(--home-y) - 3px)) scale(1.01);
  }
  100% {
    transform: translate(var(--home-x), var(--home-y)) scale(1);
  }
}
@keyframes toss-spin {
  0% {
    transform: rotateX(12deg) rotateY(0deg) rotateZ(0deg);
  }
  100% {
    transform: rotateX(18deg) rotateY(var(--end-y)) rotateZ(var(--end-z));
  }
}
@keyframes toss-shadow {
  0%,
  100% {
    opacity: 0.5;
    transform: scaleX(1);
  }
  35% {
    opacity: 0.18;
    transform: scaleX(0.55) translateY(8px);
  }
  82% {
    opacity: 0.65;
    transform: scaleX(1.15);
  }
}
</style>
