/** 站點公開源（sitemap / canonical / OG）。可用 VITE_SITE_ORIGIN 覆蓋。 */
export const SITE_NAME = '經盤';
export const SITE_TAGLINE = '古籍對照 · 不編吉凶';
export const SITE_DESCRIPTION =
  '經盤是紫微斗數與易經研習站：排盤、古籍原文、易經六十四卦、搖卦、六壬、納音起名與羅盤黃曆工具。只做原文對照與本地推算，不編吉凶斷語，不作決策依據。';

export const SITE_ORIGIN = (
  import.meta.env.VITE_SITE_ORIGIN || 'http://38.55.194.234'
).replace(/\/$/, '');

export const SITE_OG_IMAGE = `${SITE_ORIGIN}/assets/decor/yin-yang.svg`;

export function absoluteUrl(path = '/'): string {
  if (!path || path === '/') return `${SITE_ORIGIN}/`;
  return `${SITE_ORIGIN}${path.startsWith('/') ? path : `/${path}`}`;
}
