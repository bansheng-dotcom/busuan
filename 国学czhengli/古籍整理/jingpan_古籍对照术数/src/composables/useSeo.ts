import type { RouteLocationNormalizedLoaded } from 'vue-router';
import {
  SITE_DESCRIPTION,
  SITE_NAME,
  SITE_OG_IMAGE,
  SITE_TAGLINE,
  absoluteUrl,
} from '@/config/site';

export interface SeoPayload {
  title?: string;
  description?: string;
  path?: string;
  image?: string;
  noindex?: boolean;
  jsonLd?: Record<string, unknown> | Record<string, unknown>[];
}

function ensureMeta(attr: 'name' | 'property', key: string, content: string) {
  const selector = `meta[${attr}="${key}"]`;
  let el = document.head.querySelector(selector) as HTMLMetaElement | null;
  if (!el) {
    el = document.createElement('meta');
    el.setAttribute(attr, key);
    document.head.appendChild(el);
  }
  el.setAttribute('content', content);
}

function ensureLink(rel: string, href: string) {
  let el = document.head.querySelector(`link[rel="${rel}"]`) as HTMLLinkElement | null;
  if (!el) {
    el = document.createElement('link');
    el.rel = rel;
    document.head.appendChild(el);
  }
  el.href = href;
}

function setJsonLd(data?: Record<string, unknown> | Record<string, unknown>[]) {
  const id = 'jingpan-jsonld';
  let el = document.getElementById(id) as HTMLScriptElement | null;
  if (!data) {
    el?.remove();
    return;
  }
  if (!el) {
    el = document.createElement('script');
    el.type = 'application/ld+json';
    el.id = id;
    document.head.appendChild(el);
  }
  el.textContent = JSON.stringify(data);
}

/** 寫入 document head（SPA 客戶端 SEO / 分享預覽） */
export function applySeo(payload: SeoPayload = {}) {
  const titleCore = payload.title?.trim() || SITE_NAME;
  const fullTitle =
    titleCore === SITE_NAME ? `${SITE_NAME} · ${SITE_TAGLINE}` : `${titleCore} · ${SITE_NAME}`;
  const description = payload.description?.trim() || SITE_DESCRIPTION;
  const url = absoluteUrl(payload.path || '/');
  const image = payload.image || SITE_OG_IMAGE;

  document.title = fullTitle;
  document.documentElement.lang = document.documentElement.lang || 'zh-Hant';

  ensureMeta('name', 'description', description);
  ensureMeta('name', 'keywords', '經盤,紫微斗數,易經,六十四卦,搖卦,六壬,納音起名,羅盤,黃曆,古籍對照');
  ensureMeta('name', 'author', SITE_NAME);
  ensureMeta(
    'name',
    'robots',
    payload.noindex ? 'noindex,nofollow' : 'index,follow,max-image-preview:large',
  );

  ensureMeta('property', 'og:type', 'website');
  ensureMeta('property', 'og:site_name', SITE_NAME);
  ensureMeta('property', 'og:title', fullTitle);
  ensureMeta('property', 'og:description', description);
  ensureMeta('property', 'og:url', url);
  ensureMeta('property', 'og:image', image);
  ensureMeta('property', 'og:locale', 'zh_TW');

  ensureMeta('name', 'twitter:card', 'summary');
  ensureMeta('name', 'twitter:title', fullTitle);
  ensureMeta('name', 'twitter:description', description);
  ensureMeta('name', 'twitter:image', image);

  ensureLink('canonical', url);
  setJsonLd(payload.jsonLd);
}

export function seoFromRoute(route: RouteLocationNormalizedLoaded): SeoPayload {
  const meta = route.meta as {
    title?: string;
    description?: string;
    noindex?: boolean;
  };
  return {
    title: typeof meta.title === 'string' ? meta.title : undefined,
    description: typeof meta.description === 'string' ? meta.description : undefined,
    noindex: Boolean(meta.noindex),
    path: route.path,
  };
}
