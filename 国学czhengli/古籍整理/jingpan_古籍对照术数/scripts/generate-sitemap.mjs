#!/usr/bin/env node
/**
 * 生成 public/sitemap.xml（靜態路由 + 易經64卦 + 星曜詞典）
 * 源站：VITE_SITE_ORIGIN 或默認 VPS 地址
 */
import { readFileSync, writeFileSync } from 'node:fs';
import { dirname, join } from 'node:path';
import { fileURLToPath } from 'node:url';

const __dirname = dirname(fileURLToPath(import.meta.url));
const root = join(__dirname, '..');
const hexData = JSON.parse(readFileSync(join(root, 'src/data/yijingHexagrams.json'), 'utf8'));
const starData = JSON.parse(readFileSync(join(root, 'src/data/starDict.json'), 'utf8'));

const origin = (process.env.VITE_SITE_ORIGIN || 'http://38.55.194.234').replace(/\/$/, '');
const today = new Date().toISOString().slice(0, 10);

const staticPaths = [
  { path: '/', priority: '1.0', changefreq: 'weekly' },
  { path: '/chart', priority: '0.9', changefreq: 'monthly' },
  { path: '/book', priority: '0.9', changefreq: 'monthly' },
  { path: '/yijing', priority: '0.9', changefreq: 'monthly' },
  { path: '/star-dict', priority: '0.8', changefreq: 'monthly' },
  { path: '/pattern-dict', priority: '0.8', changefreq: 'monthly' },
  { path: '/luopan', priority: '0.7', changefreq: 'monthly' },
  { path: '/almanac', priority: '0.7', changefreq: 'monthly' },
  { path: '/naming', priority: '0.7', changefreq: 'monthly' },
  { path: '/liuren', priority: '0.7', changefreq: 'monthly' },
  { path: '/yaogua', priority: '0.8', changefreq: 'monthly' },
  { path: '/about', priority: '0.5', changefreq: 'yearly' },
];

/** @type {{ loc: string; priority: string; changefreq: string }[]} */
const urls = [
  ...staticPaths.map((p) => ({
    loc: p.path === '/' ? `${origin}/` : `${origin}${p.path}`,
    priority: p.priority,
    changefreq: p.changefreq,
  })),
  ...hexData.hexagrams.map((h) => ({
    loc: `${origin}/yijing/${h.id}`,
    priority: '0.7',
    changefreq: 'monthly',
  })),
  ...Object.keys(starData.dict).map((name) => ({
    loc: `${origin}/star-dict/${encodeURIComponent(name)}`,
    priority: '0.6',
    changefreq: 'monthly',
  })),
];

const body = urls
  .map(
    (u) => `  <url>
    <loc>${u.loc}</loc>
    <lastmod>${today}</lastmod>
    <changefreq>${u.changefreq}</changefreq>
    <priority>${u.priority}</priority>
  </url>`,
  )
  .join('\n');

const xml = `<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
${body}
</urlset>
`;

const out = join(root, 'public/sitemap.xml');
writeFileSync(out, xml, 'utf8');
console.log(`Wrote ${urls.length} URLs → ${out} (origin=${origin})`);
