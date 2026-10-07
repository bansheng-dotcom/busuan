import { createRouter, createWebHistory, type RouteRecordRaw } from 'vue-router';
import { applySeo, seoFromRoute } from '@/composables/useSeo';
import { SITE_DESCRIPTION, SITE_NAME, absoluteUrl } from '@/config/site';
import { useRouteLoading, type SkeletonType } from '@/composables/useRouteLoading';

declare module 'vue-router' {
  interface RouteMeta {
    title?: string;
    description?: string;
    noindex?: boolean;
    /** 頁面自行寫 SEO（詳情頁），afterEach 不覆蓋 */
    seoDynamic?: boolean;
    /** 路由懶加載時的骨架類型 */
    skeleton?: SkeletonType;
    /** 顶栏显示字号 ± 与复制（仅正文可读页） */
    fontTools?: boolean;
  }
}

/** 与 App.vue keep-alive include 的组件 name 对齐 */
const KEEP_ALIVE_BY_ROUTE: Record<string, string> = {
  chart: 'ChartPage',
  naming: 'NamingPage',
  yijing: 'YijingPage',
  yaogua: 'YaoguaPage',
};

const visitedKeepAlive = new Set<string>();
let loadingStarted = false;

const { start, done, fail, isLoading } = useRouteLoading();

const routes: RouteRecordRaw[] = [
  {
    path: '/',
    name: 'home',
    component: () => import('@/views/home/index.vue'),
    meta: {
      title: '首頁',
      description: SITE_DESCRIPTION,
      skeleton: 'home',
    },
  },
  {
    path: '/chart',
    name: 'chart',
    component: () => import('@/views/chart/index.vue'),
    meta: {
      title: '紫微排盤',
      description: '本地紫微斗數排盤：公曆生辰、真太陽時、十二宮命盤與古籍原文對照，不編吉凶斷語。',
      skeleton: 'chart',
    },
  },
  {
    path: '/book',
    name: 'book',
    component: () => import('@/views/book/index.vue'),
    meta: {
      title: '古籍原文',
      description: '《紫微斗數全書》卷一至卷三站內閱讀，星曜、格局、納音等原文可對照查閱。',
      skeleton: 'book',
      fontTools: true,
    },
  },
  {
    path: '/yijing',
    name: 'yijing',
    component: () => import('@/views/yijing/index.vue'),
    meta: {
      title: '易經六十四卦',
      description: '斷易天機六十四卦按文王卦序整理，含卦象圖與講解原文，可按八卦篩選。',
      skeleton: 'yijing',
      fontTools: true,
    },
  },
  {
    path: '/yijing/:id',
    name: 'yijing-detail',
    component: () => import('@/views/yijing/detail/index.vue'),
    meta: {
      title: '易經卦詳',
      description: '易經單卦詳解：卦象、圖說與原文節選，支持上下卦跳轉。',
      seoDynamic: true,
      skeleton: 'yijing-detail',
      fontTools: true,
    },
  },
  {
    path: '/star-dict',
    name: 'star-dict',
    component: () => import('@/views/star-dict/index.vue'),
    meta: {
      title: '星曜詞典',
      description: '紫微斗數諸星問答與廟旺落陷等卷一原文詞典。',
      skeleton: 'star-dict',
      fontTools: true,
    },
  },
  {
    path: '/star-dict/:name',
    name: 'star-dict-detail',
    component: () => import('@/views/star-dict/detail/index.vue'),
    meta: {
      title: '星曜詳解',
      description: '單顆星曜的古籍原文與性質說明。',
      seoDynamic: true,
      skeleton: 'star-dict-detail',
      fontTools: true,
    },
  },
  {
    path: '/pattern-dict',
    name: 'pattern-dict',
    component: () => import('@/views/pattern-dict/index.vue'),
    meta: {
      title: '格局詞典',
      description: '紫微斗數格局歌訣原文對照，便於研習查閱。',
      skeleton: 'pattern-dict',
      fontTools: true,
    },
  },
  {
    path: '/luopan',
    name: 'luopan',
    component: () => import('@/views/luopan/index.vue'),
    meta: {
      title: '羅盤',
      description: '研習用地盤羅盤：廿四山、先後天八卦與洛書，不作風水斷事。',
      skeleton: 'luopan',
    },
  },
  {
    path: '/almanac',
    name: 'almanac',
    component: () => import('@/views/almanac/index.vue'),
    meta: {
      title: '老黃曆',
      description: '農曆黃曆宜忌查閱（曆注來源公開庫），僅供研習參考。',
      skeleton: 'almanac',
    },
  },
  {
    path: '/naming',
    name: 'naming',
    component: () => import('@/views/naming/index.vue'),
    meta: {
      title: '納音起名',
      description: '依日柱納音生扶取喜用字，站內精選字庫，可跳轉卷二納音歌核對。',
      skeleton: 'naming',
    },
  },
  {
    path: '/liuren',
    name: 'liuren',
    component: () => import('@/views/liuren/index.vue'),
    meta: {
      title: '六壬法',
      description: '依農曆月日時推六宮，本地計算，可選用 AI 傾向解讀。',
      skeleton: 'liuren',
    },
  },
  {
    path: '/yaogua',
    name: 'yaogua',
    component: () => import('@/views/yaogua/index.vue'),
    meta: {
      title: '三錢搖卦',
      description: '三錢法本地起六爻，出本卦／之卦並鏈接站內易經原文，可選用 AI 傾向解讀。',
      skeleton: 'yaogua',
    },
  },
  {
    path: '/about',
    name: 'about',
    component: () => import('@/views/about/index.vue'),
    meta: {
      title: '關於與聲明',
      description: '經盤資料來源、算法說明與免責聲明：僅供傳統文化與古籍研習。',
      skeleton: 'about',
      fontTools: true,
    },
  },
];

const router = createRouter({
  history: createWebHistory(),
  scrollBehavior(to, from, savedPosition) {
    // 硬刷新 / 首次进入：强制回顶，不沿用浏览器滚动恢复
    if (!from.matched.length) {
      return { top: 0, left: 0 };
    }
    if (savedPosition) return savedPosition;
    if (to.hash) {
      return { el: to.hash, behavior: 'smooth', top: 80 };
    }
    if (to.name === 'chart' || to.name === 'yijing' || to.name === 'yaogua') {
      return false;
    }
    return { top: 0 };
  },
  routes,
});

router.beforeEach((to, from) => {
  loadingStarted = false;

  // 仅 hash/query 变化：不闪骨架
  if (from.matched.length && to.path === from.path) {
    return true;
  }

  const keepName =
    typeof to.name === 'string' ? KEEP_ALIVE_BY_ROUTE[to.name] : undefined;
  // keep-alive 命中：组件已在内存，数据保留，不闪骨架
  if (from.matched.length && keepName && visitedKeepAlive.has(keepName)) {
    return true;
  }

  // 含首次进入 / 硬刷新：懒加载 chunk 未到前必须出骨架
  start(to.meta.skeleton ?? 'home');
  loadingStarted = true;
  return true;
});

router.afterEach((to) => {
  if (loadingStarted) {
    done();
    loadingStarted = false;
  } else if (isLoading.value) {
    // 兜底：首屏默认 loading，避免异常路径卡死骨架
    done();
  }

  const keepName =
    typeof to.name === 'string' ? KEEP_ALIVE_BY_ROUTE[to.name] : undefined;
  if (keepName) visitedKeepAlive.add(keepName);

  if (to.meta.seoDynamic) return;
  const base = seoFromRoute(to);
  if (to.name === 'home') {
    applySeo({
      ...base,
      title: SITE_NAME,
      jsonLd: {
        '@context': 'https://schema.org',
        '@type': 'WebSite',
        name: SITE_NAME,
        url: absoluteUrl('/'),
        description: SITE_DESCRIPTION,
        inLanguage: ['zh-Hant', 'zh-Hans'],
      },
    });
    return;
  }
  applySeo(base);
});

router.onError(() => {
  fail();
  loadingStarted = false;
});

export default router;
