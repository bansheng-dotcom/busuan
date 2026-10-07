<template>
  <div
    class="site-header-spacer"
    aria-hidden="true"
    :style="{ height: `${headerH}px` }"
  />
  <teleport to="body">
    <header ref="headerRef" class="site-header" :class="deviceClass">
      <div class="bar">
        <router-link to="/" class="logo">
          <img src="/assets/decor/yin-yang.svg" alt="" class="mark" width="22" height="22" />
          <span>{{ display('經盤', false) }}</span>
        </router-link>

        <nav v-if="isPc" class="nav" :aria-label="display('主導航', false)">
          <template v-for="item in navs" :key="item.key">
            <router-link
              v-if="item.path && !item.children"
              :to="item.path"
              class="nav-link"
              :class="{ 'is-active': isActive(item) }"
              :active-class="item.path === '/' ? undefined : 'is-active'"
              exact-active-class="is-active"
            >
              {{ display(item.label, false) }}
            </router-link>

            <div
              v-else
              class="nav-drop"
              :class="{ open: openKey === item.key, 'is-active': isActive(item) }"
              @mouseenter="openKey = item.key"
              @mouseleave="openKey = ''"
            >
              <button
                type="button"
                class="nav-link nav-trigger"
                :aria-expanded="openKey === item.key"
                @click="toggleDrop(item.key)"
              >
                {{ display(item.label, false) }}
                <span class="caret" aria-hidden="true">▾</span>
              </button>
              <div v-show="openKey === item.key" class="drop-panel" role="menu">
                <router-link
                  v-for="child in item.children"
                  :key="child.path"
                  :to="child.path"
                  class="drop-link"
                  role="menuitem"
                  :class="{ 'is-active': isChildActive(child.path) }"
                  @click="openKey = ''"
                >
                  <b>{{ display(child.label, false) }}</b>
                  <em v-if="child.desc">{{ display(child.desc, false) }}</em>
                </router-link>
              </div>
            </div>
          </template>
        </nav>

        <div v-if="isPc" class="tools">
          <button type="button" class="tool tool-script" @click="store.toggleScript">
            {{ display('繁/簡', false) }}
          </button>
          <button type="button" class="tool" @click="store.toggleTheme">
            {{ display(store.isDark ? '宣紙' : '夜空', false) }}
          </button>
          <button v-if="showFontTools" type="button" class="tool" @click="store.bumpFont(-1)">A-</button>
          <button v-if="showFontTools" type="button" class="tool" @click="store.bumpFont(1)">A+</button>
          <button v-if="showFontTools" type="button" class="tool" @click="handleCopy">{{ display('複製', false) }}</button>
        </div>

        <div v-else class="tools tools-h5">
          <button type="button" class="tool tool-script" @click="store.toggleScript">
            {{ display('繁/簡', false) }}
          </button>
          <button type="button" class="tool" @click="store.toggleTheme">
            {{ display(store.isDark ? '宣紙' : '夜空', false) }}
          </button>
          <button v-if="showFontTools" type="button" class="tool" @click="store.bumpFont(-1)">A-</button>
          <button v-if="showFontTools" type="button" class="tool" @click="store.bumpFont(1)">A+</button>
          <button v-if="showFontTools" type="button" class="tool" @click="handleCopy">{{ display('複製', false) }}</button>
          <button
            type="button"
            class="burger"
            :aria-label="display('打開菜單', false)"
            @click="drawerOpen = true"
          >
            <i /><i /><i />
          </button>
        </div>
      </div>
      <MobileDrawer v-model="drawerOpen" />
    </header>
  </teleport>
</template>

<script lang="ts">
import { defineComponent, onBeforeUnmount, onMounted, ref, watch } from 'vue';
import { useRoute } from 'vue-router';
import { useAppStore } from '@/store/app';
import { useDisplayText } from '@/composables/useDisplayText';
import { useDevice } from '@/composables/useDevice';
import { useFontTools } from '@/composables/useFontTools';
import { copySelection } from '@/utils/copy';
import {
  SITE_NAV,
  isNavChildActive,
  isNavGroupActive,
  type NavItem,
} from '@/data/siteNav';
import MobileDrawer from '@/components/MobileDrawer.vue';

export default defineComponent({
  name: 'AppHeader',
  components: { MobileDrawer },
  setup() {
    const store = useAppStore();
    const route = useRoute();
    const { display } = useDisplayText();
    const { isPc, deviceClass } = useDevice();
    const { showFontTools } = useFontTools();
    const drawerOpen = ref(false);
    const openKey = ref('');
    const navs = SITE_NAV;
    const headerRef = ref<HTMLElement | null>(null);
    const headerH = ref(58);
    let ro: ResizeObserver | null = null;

    const syncHeaderH = () => {
      const el = headerRef.value;
      if (!el) return;
      const h = Math.ceil(el.getBoundingClientRect().height);
      if (h > 0) {
        headerH.value = h;
        document.documentElement.style.setProperty('--zw-header-h', `${h}px`);
      }
    };

    const handleCopy = () => copySelection();

    const isActive = (item: NavItem) => isNavGroupActive(item, route.path);
    const isChildActive = (path: string) => isNavChildActive(path, route.path);
    const toggleDrop = (key: string) => {
      openKey.value = openKey.value === key ? '' : key;
    };

    watch(
      () => route.fullPath,
      () => {
        openKey.value = '';
      },
    );

    watch(isPc, () => {
      requestAnimationFrame(syncHeaderH);
    });

    onMounted(() => {
      syncHeaderH();
      if (typeof ResizeObserver !== 'undefined' && headerRef.value) {
        ro = new ResizeObserver(() => syncHeaderH());
        ro.observe(headerRef.value);
      }
      window.addEventListener('resize', syncHeaderH);
    });

    onBeforeUnmount(() => {
      ro?.disconnect();
      ro = null;
      window.removeEventListener('resize', syncHeaderH);
    });

    return {
      store,
      display,
      navs,
      handleCopy,
      showFontTools,
      isPc,
      deviceClass,
      drawerOpen,
      openKey,
      isActive,
      isChildActive,
      toggleDrop,
      headerRef,
      headerH,
    };
  },
});
</script>

<style scoped>
.site-header {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  z-index: 1000;
  width: 100%;
  border-bottom: 1px solid var(--zw-line);
  background: color-mix(in srgb, var(--zw-paper) 94%, transparent);
  backdrop-filter: blur(12px);
  -webkit-backdrop-filter: blur(12px);
}
.site-header-spacer {
  flex: none;
  width: 100%;
}
.bar {
  display: flex;
  align-items: center;
  gap: 10px 16px;
  max-width: 1280px;
  margin: 0 auto;
  padding: 12px 24px;
}
.logo {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  color: var(--zw-primary);
  text-decoration: none;
  font-weight: 700;
  letter-spacing: 0.18em;
  font-size: 15px;
}
.mark {
  border-radius: 50%;
  flex: none;
}
.nav {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 4px 2px;
}
.nav-link {
  position: relative;
  display: inline-flex;
  align-items: center;
  gap: 2px;
  padding: 6px 10px;
  color: var(--zw-ink);
  text-decoration: none;
  letter-spacing: 0.16em;
  font-size: 14px;
  border: none;
  background: transparent;
  font-family: inherit;
  cursor: pointer;
}
.nav-link.is-active::after,
.nav-link:hover::after,
.nav-drop.is-active > .nav-trigger::after,
.nav-drop.open > .nav-trigger::after {
  content: '';
  position: absolute;
  left: 10px;
  right: 10px;
  bottom: 2px;
  height: 1px;
  background: var(--zw-gold);
}
.caret {
  font-size: 10px;
  opacity: 0.7;
  transform: translateY(-1px);
}
.nav-drop {
  position: relative;
}
.drop-panel {
  position: absolute;
  top: calc(100% - 2px);
  left: 0;
  min-width: 148px;
  padding: 8px;
  border: 1px solid var(--zw-line);
  border-radius: 12px;
  background: var(--zw-paper);
  box-shadow: 0 12px 28px rgba(44, 36, 22, 0.14);
  z-index: 50;
}
.drop-link {
  display: flex;
  flex-direction: column;
  gap: 2px;
  padding: 8px 10px;
  border-radius: 8px;
  text-decoration: none;
  color: var(--zw-ink);
}
.drop-link b {
  font-size: 14px;
  font-weight: 600;
  letter-spacing: 0.14em;
}
.drop-link em {
  font-style: normal;
  font-size: 11px;
  color: var(--zw-muted);
  letter-spacing: 0.06em;
}
.drop-link:hover,
.drop-link.is-active {
  background: color-mix(in srgb, var(--zw-gold) 16%, transparent);
  color: var(--zw-primary);
}
.tools {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
  margin-left: auto;
}
.tool {
  border: 1px solid var(--zw-line);
  background: transparent;
  color: var(--zw-ink);
  padding: 4px 10px;
  font-family: inherit;
  font-size: 12px;
  letter-spacing: 0.08em;
  cursor: pointer;
}
.tool:hover {
  border-color: var(--zw-gold);
  color: var(--zw-primary);
}
.tool-script {
  min-width: 3.6em;
  text-align: center;
  letter-spacing: 0.02em;
  font-variant-numeric: tabular-nums;
}
.burger {
  width: 42px;
  height: 42px;
  border: 1px solid var(--zw-line);
  border-radius: 10px;
  background: transparent;
  display: inline-flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  gap: 5px;
  padding: 0;
}
.burger i {
  display: block;
  width: 18px;
  height: 1.5px;
  background: var(--zw-ink);
}
.is-h5 .bar {
  padding: 8px 12px;
  gap: 8px;
}
.is-h5 .logo {
  flex: none;
}
.is-h5 .logo span {
  letter-spacing: 0.14em;
}
.is-h5 .tools-h5 {
  flex: 1;
  flex-wrap: nowrap;
  justify-content: flex-end;
  align-items: center;
  gap: 4px;
  min-width: 0;
}
.is-h5 .tools-h5 .tool {
  flex: none;
  padding: 5px 6px;
  font-size: 11px;
  letter-spacing: 0.02em;
  border-radius: 8px;
  white-space: nowrap;
}
.is-h5 .tools-h5 .burger {
  flex: none;
  width: 38px;
  height: 38px;
  margin-left: 2px;
}
</style>
