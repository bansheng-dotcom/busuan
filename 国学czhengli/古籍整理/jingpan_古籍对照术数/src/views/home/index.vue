<template>
  <div class="home" :class="deviceClass">
    <!-- ===== PC：完整保留八卦 + 四象罗盘 ===== -->
    <template v-if="isPc">
      <section class="hero hero-pc">
        <div class="hero-copy">
          <p class="brand">{{ display('經盤', false) }}</p>
          <h1>{{ display('古籍對照 · 不編吉凶', false) }}</h1>
          <p class="lead">{{ display('斗數排盤、全書原文、羅盤與黃曆。', false) }}</p>
          <div class="cta">
            <router-link class="cta-main" to="/chart">{{ display('開始排盤', false) }}</router-link>
            <router-link class="cta-ghost" to="/book">{{ display('閱讀全書', false) }}</router-link>
          </div>
        </div>
        <div class="hero-figure" aria-hidden="true">
          <BaguaWheel />
        </div>
      </section>

      <section class="section nav-section">
        <h2>{{ display('研習門徑', false) }}</h2>
        <p>{{ display('南離排盤，東震讀經，北坎問星，西兌觀格。', false) }}</p>
        <div class="compass-stage">
          <HomeNavCompass />
        </div>
      </section>

      <section class="section gallery-section">
        <div class="gallery-card star-card">
          <div class="star-visual">
            <StarMap />
          </div>
          <div>
            <h3>{{ display('星象示意', false) }}</h3>
            <p>{{ display('紫微垣意象圖，僅作視覺襯景；斷語仍以卷一原文為準。', false) }}</p>
          </div>
        </div>
      </section>

      <section class="section wuxing-section">
        <div class="wuxing-copy">
          <h2>{{ display('五行局圖', false) }}</h2>
          <p>
            {{
              display(
                '木火土金水循環相生。排盤所得五行局，只作盤面標記，解讀仍歸卷一原文。',
                false,
              )
            }}
          </p>
          <router-link class="text-link" to="/about">{{ display('來源與聲明', false) }}</router-link>
        </div>
        <WuXingDiagram />
      </section>
    </template>

    <!-- ===== H5：八卦半透明衬景 + 抽屉入口 ===== -->
    <template v-else>
      <section class="hero hero-h5">
        <div class="h5-bagua" aria-hidden="true">
          <BaguaWheel />
        </div>
        <div class="hero-copy">
          <p class="brand">{{ display('經盤', false) }}</p>
          <h1>{{ display('古籍對照 · 不編吉凶', false) }}</h1>
          <p class="lead">{{ display('排盤 · 讀經 · 羅盤 · 黃曆', false) }}</p>
          <div class="cta">
            <router-link class="cta-main" to="/chart">{{ display('開始排盤', false) }}</router-link>
            <button type="button" class="cta-ghost" @click="openDrawer">
              {{ display('更多入口', false) }}
            </button>
          </div>
        </div>
      </section>

      <section class="h5-quick">
        <router-link to="/chart" class="q">
          <span class="q-icon" aria-hidden="true">
            <svg viewBox="0 0 24 24" fill="none">
              <rect x="3.5" y="3.5" width="17" height="17" rx="2" stroke="currentColor" stroke-width="1.4" />
              <path d="M12 3.5v17M3.5 12h17" stroke="currentColor" stroke-width="1.2" />
            </svg>
          </span>
          <span class="q-label">{{ display('排盤', false) }}</span>
        </router-link>
        <router-link to="/book" class="q">
          <span class="q-icon" aria-hidden="true">
            <svg viewBox="0 0 24 24" fill="none">
              <path
                d="M5 5.5c1.6-.9 3.4-1.3 5.2-.7V19c-1.8-.6-3.6-.2-5.2.7V5.5Z"
                stroke="currentColor"
                stroke-width="1.4"
                stroke-linejoin="round"
              />
              <path
                d="M19 5.5c-1.6-.9-3.4-1.3-5.2-.7V19c1.8-.6 3.6-.2 5.2.7V5.5Z"
                stroke="currentColor"
                stroke-width="1.4"
                stroke-linejoin="round"
              />
            </svg>
          </span>
          <span class="q-label">{{ display('古籍', false) }}</span>
        </router-link>
        <router-link to="/star-dict" class="q">
          <span class="q-icon" aria-hidden="true">
            <svg viewBox="0 0 24 24" fill="none">
              <path
                d="M12 3.5l1.7 5.2h5.5l-4.4 3.2 1.7 5.3L12 14.2l-4.5 3 1.7-5.3-4.4-3.2h5.5L12 3.5Z"
                stroke="currentColor"
                stroke-width="1.3"
                stroke-linejoin="round"
              />
            </svg>
          </span>
          <span class="q-label">{{ display('星曜', false) }}</span>
        </router-link>
        <router-link to="/pattern-dict" class="q">
          <span class="q-icon" aria-hidden="true">
            <svg viewBox="0 0 24 24" fill="none">
              <path d="M12 3.5 20.5 12 12 20.5 3.5 12 12 3.5Z" stroke="currentColor" stroke-width="1.4" />
              <circle cx="12" cy="12" r="2.2" stroke="currentColor" stroke-width="1.3" />
            </svg>
          </span>
          <span class="q-label">{{ display('格局', false) }}</span>
        </router-link>
        <router-link to="/luopan" class="q">
          <span class="q-icon" aria-hidden="true">
            <svg viewBox="0 0 24 24" fill="none">
              <circle cx="12" cy="12" r="8.2" stroke="currentColor" stroke-width="1.4" />
              <circle cx="12" cy="12" r="3.2" stroke="currentColor" stroke-width="1.2" />
              <path d="M12 4.2v2.2M12 17.6v2.2M4.2 12h2.2M17.6 12h2.2" stroke="currentColor" stroke-width="1.3" />
            </svg>
          </span>
          <span class="q-label">{{ display('羅盤', false) }}</span>
        </router-link>
        <router-link to="/almanac" class="q">
          <span class="q-icon" aria-hidden="true">
            <svg viewBox="0 0 24 24" fill="none">
              <rect x="4" y="5" width="16" height="15" rx="2" stroke="currentColor" stroke-width="1.4" />
              <path d="M8 3.5v3M16 3.5v3M4 10h16" stroke="currentColor" stroke-width="1.3" />
              <path d="M8 13.5h2.5M13.5 13.5H16M8 17h2.5" stroke="currentColor" stroke-width="1.3" />
            </svg>
          </span>
          <span class="q-label">{{ display('黃曆', false) }}</span>
        </router-link>
      </section>

      <section class="h5-card star-h5">
        <div class="star-visual">
          <StarMap />
        </div>
        <div class="star-h5-copy">
          <h3>{{ display('星象示意', false) }}</h3>
          <p>{{ display('紫微垣意象，僅作研習襯景。', false) }}</p>
        </div>
      </section>

      <section class="h5-card wuxing-h5">
        <WuXingDiagram />
        <div class="wuxing-h5-copy">
          <h3>{{ display('五行相生', false) }}</h3>
          <p>{{ display('盤面五行局僅作標記，解讀歸卷一原文。', false) }}</p>
          <ol class="wuxing-cycle">
            <li v-for="(item, idx) in shengCycle" :key="item.name">
              <span class="dot" :style="{ backgroundColor: item.color }" />
              {{ display(item.name, false) }}
              <span v-if="idx < shengCycle.length - 1" class="arrow" aria-hidden="true">→</span>
            </li>
          </ol>
          <router-link class="text-link" to="/about">{{ display('關於', false) }}</router-link>
        </div>
      </section>

      <MobileDrawer v-model="drawerOpen" />
    </template>
  </div>
</template>

<script lang="ts">
import { defineComponent, ref } from 'vue';
import { useDisplayText } from '@/composables/useDisplayText';
import { useDevice } from '@/composables/useDevice';
import BaguaWheel from './components/BaguaWheel.vue';
import HomeNavCompass from './components/HomeNavCompass.vue';
import StarMap from './components/StarMap.vue';
import WuXingDiagram from './components/WuXingDiagram.vue';
import MobileDrawer from '@/components/MobileDrawer.vue';

interface ShengCycleItem {
  name: string;
  color: string;
}

const SHENG_CYCLE: ShengCycleItem[] = [
  { name: '木', color: '#2f5d3a' },
  { name: '火', color: '#8b3a2a' },
  { name: '土', color: '#8a6a32' },
  { name: '金', color: '#c8a967' },
  { name: '水', color: '#2c4a6e' },
];

export default defineComponent({
  name: 'HomePage',
  components: { BaguaWheel, HomeNavCompass, StarMap, WuXingDiagram, MobileDrawer },
  setup() {
    const { display } = useDisplayText();
    const { isPc, deviceClass } = useDevice();
    const drawerOpen = ref(false);
    const openDrawer = () => {
      drawerOpen.value = true;
    };
    return { display, isPc, deviceClass, drawerOpen, openDrawer, shengCycle: SHENG_CYCLE };
  },
});
</script>

<style scoped>
.home {
  overflow-x: hidden;
}
.hero {
  position: relative;
  background:
    url('/assets/decor/paper-noise.svg'),
    radial-gradient(ellipse at 18% 22%, rgba(200, 169, 103, 0.16), transparent 42%),
    linear-gradient(
      120deg,
      color-mix(in srgb, var(--zw-paper) 82%, var(--zw-primary)) 0%,
      var(--zw-bg) 55%,
      color-mix(in srgb, var(--zw-bg) 70%, #1a1430) 100%
    );
  background-blend-mode: multiply, normal, normal;
}
html.theme-nightsky .hero {
  background-blend-mode: soft-light, normal, normal;
}
.hero-pc {
  position: relative;
  overflow: hidden;
  min-height: calc(100vh - 64px);
  display: grid;
  grid-template-columns: minmax(0, 1fr) minmax(280px, 48%);
  align-items: center;
  padding: 8vh 6vw 10vh;
}
.hero-copy {
  position: relative;
  z-index: 1;
  max-width: 520px;
}
.brand {
  margin: 0 0 12px;
  font-size: clamp(40px, 7vw, 84px);
  line-height: 1.05;
  letter-spacing: 0.28em;
  color: var(--zw-primary);
  font-weight: 700;
}
h1 {
  margin: 0 0 16px;
  font-size: clamp(20px, 3vw, 34px);
  font-weight: 500;
  letter-spacing: 0.28em;
}
.lead {
  margin: 0 0 28px;
  max-width: 28em;
  font-size: 17px;
  line-height: 1.8;
  color: var(--zw-muted);
  letter-spacing: 0.08em;
}
.cta {
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
}
.cta-main,
.cta-ghost {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  min-width: 132px;
  padding: 12px 20px;
  text-decoration: none;
  letter-spacing: 0.18em;
  border: 1px solid transparent;
  font-family: inherit;
  cursor: pointer;
}
.cta-main {
  background: var(--zw-primary);
  color: #f7f0de;
}
.cta-ghost {
  border-color: var(--zw-gold);
  color: var(--zw-ink);
  background: transparent;
}
.hero-figure {
  position: relative;
  z-index: 1;
  justify-self: end;
  width: min(72vh, 100%);
  color: var(--zw-ink);
}
.section {
  padding: 72px 6vw;
  text-align: center;
}
.section h2 {
  margin: 0 0 10px;
  font-size: 28px;
  letter-spacing: 0.36em;
}
.section > p {
  margin: 0 auto 36px;
  max-width: 28em;
  color: var(--zw-muted);
  letter-spacing: 0.1em;
  line-height: 1.8;
}
.nav-section {
  overflow: visible;
  padding-bottom: 96px;
  background: var(--zw-paper);
  border-top: 1px solid var(--zw-line);
  border-bottom: 1px solid var(--zw-line);
}
.compass-stage {
  position: relative;
  max-width: 720px;
  margin: 0 auto;
}
.gallery-section {
  padding-top: 56px;
  padding-bottom: 24px;
}
.gallery-card {
  max-width: 1080px;
  margin: 0 auto;
  display: grid;
  grid-template-columns: 1.4fr 0.8fr;
  gap: 24px;
  align-items: center;
  text-align: left;
  border: 1px solid var(--zw-line);
  background: var(--zw-paper);
  padding: 16px;
}
.gallery-card img {
  width: 100%;
  border: 1px solid color-mix(in srgb, var(--zw-gold) 45%, transparent);
}
.star-visual {
  width: 100%;
  min-height: 220px;
  border: 1px solid color-mix(in srgb, var(--zw-gold) 45%, transparent);
  overflow: hidden;
  background: #0b1020;
}
.star-visual :deep(.star-map) {
  min-height: 220px;
}
.gallery-card h3 {
  margin: 0 0 10px;
  letter-spacing: 0.24em;
}
.gallery-card p {
  margin: 0;
  color: var(--zw-muted);
  line-height: 1.8;
  letter-spacing: 0.06em;
}
.wuxing-section {
  display: grid;
  grid-template-columns: minmax(0, 360px) minmax(0, 1fr);
  gap: 40px;
  align-items: center;
  text-align: left;
  max-width: 1080px;
  margin: 0 auto;
}
.wuxing-copy h2,
.wuxing-copy p {
  text-align: left;
}
.wuxing-copy p {
  margin-bottom: 18px;
  color: var(--zw-muted);
  line-height: 1.8;
}
.text-link {
  color: var(--zw-gold);
  letter-spacing: 0.16em;
  text-decoration: none;
  border-bottom: 1px solid var(--zw-gold);
}

/* ===== H5 ===== */
.hero-h5 {
  min-height: auto;
  padding: 108px 18px 36px;
  overflow: hidden;
}
.h5-bagua {
  position: absolute;
  right: -18%;
  top: -4%;
  width: min(88vw, 380px);
  opacity: 0.28;
  pointer-events: none;
  color: var(--zw-ink);
}
.hero-h5 .brand {
  font-size: 40px;
  letter-spacing: 0.16em;
}
.hero-h5 h1 {
  letter-spacing: 0.14em;
  font-size: 20px;
}
.hero-h5 .lead {
  font-size: 14px;
  margin-bottom: 20px;
}
.hero-h5 .cta-main,
.hero-h5 .cta-ghost {
  min-width: 0;
  flex: 1;
  padding: 12px 10px;
  letter-spacing: 0.12em;
  font-size: 14px;
}
.h5-quick {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 8px;
  margin-top: 8px;
  padding: 16px 14px 18px;
}
.h5-quick .q {
  position: relative;
  display: flex;
  align-items: center;
  justify-content: center;
  overflow: hidden;
  text-align: center;
  text-decoration: none;
  color: var(--zw-ink);
  border: 1px solid var(--zw-line);
  background: var(--zw-paper);
  padding: 16px 0;
  letter-spacing: 0.16em;
  border-radius: 10px;
  font-size: 14px;
}
.h5-quick .q-label {
  position: relative;
  z-index: 1;
  line-height: 1.2;
}
.h5-quick .q-icon {
  position: absolute;
  left: 50%;
  top: 50%;
  z-index: 0;
  color: var(--zw-primary);
  opacity: 0.1;
  pointer-events: none;
  transform: translate(-50%, -50%);
}
.h5-quick .q-icon svg {
  width: 52px;
  height: 52px;
  display: block;
}
.h5-quick .q:active .q-icon {
  opacity: 0.16;
}
.h5-card {
  margin: 0 14px 12px;
  padding: 12px;
  border: 1px solid var(--zw-line);
  background: var(--zw-paper);
  border-radius: 12px;
}
.star-h5 {
  position: relative;
  padding: 0;
  overflow: hidden;
}
.star-h5 .star-visual {
  min-height: 168px;
  height: 168px;
  border: 0;
}
.star-h5 .star-visual :deep(.star-map) {
  min-height: 168px;
  height: 168px;
}
.star-h5-copy {
  position: absolute;
  left: 0;
  right: 0;
  bottom: 0;
  z-index: 1;
  padding: 32px 14px 12px;
  background: linear-gradient(transparent, rgba(11, 16, 32, 0.84));
  text-align: left;
}
.star-h5-copy h3 {
  margin: 0 0 4px;
  color: #f3ebd8;
  font-size: 15px;
  font-weight: 500;
  letter-spacing: 0.28em;
}
.star-h5-copy p {
  margin: 0;
  color: rgba(243, 235, 216, 0.78);
  font-size: 12px;
  letter-spacing: 0.1em;
  line-height: 1.6;
}
.wuxing-h5 {
  display: grid;
  grid-template-columns: minmax(132px, 40%) minmax(0, 1fr);
  gap: 10px 14px;
  align-items: center;
  padding: 14px 12px;
  margin-bottom: 28px;
}
.wuxing-h5 :deep(.wuxing) {
  width: 100%;
  max-width: 176px;
  justify-self: center;
}
.wuxing-h5-copy {
  min-width: 0;
}
.wuxing-h5 h3 {
  margin: 0 0 6px;
  letter-spacing: 0.2em;
  font-size: 16px;
}
.wuxing-h5 p {
  margin: 0 0 10px;
  color: var(--zw-muted);
  line-height: 1.7;
  font-size: 13px;
}
.wuxing-cycle {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 6px 0;
  margin: 0 0 12px;
  padding: 0;
  list-style: none;
  font-size: 13px;
  letter-spacing: 0.08em;
}
.wuxing-cycle li {
  display: inline-flex;
  align-items: center;
  gap: 4px;
}
.wuxing-cycle .dot {
  width: 7px;
  height: 7px;
  border-radius: 50%;
  flex-shrink: 0;
}
.wuxing-cycle .arrow {
  margin: 0 6px 0 4px;
  color: var(--zw-gold);
  opacity: 0.75;
}
@media (max-width: 380px) {
  .wuxing-h5 {
    grid-template-columns: 1fr;
    justify-items: center;
    text-align: center;
  }
  .wuxing-h5 :deep(.wuxing) {
    max-width: 200px;
  }
  .wuxing-h5-copy {
    text-align: center;
  }
  .wuxing-cycle {
    justify-content: center;
  }
}
</style>
