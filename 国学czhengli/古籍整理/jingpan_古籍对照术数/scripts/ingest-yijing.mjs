/**
 * 抓取 nihaixiahope.com 易经64卦（断易天机）索引与各卦正文，生成 JSON。
 * 来源：https://www.nihaixiahope.com/yijing.html
 */
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const root = path.resolve(__dirname, '..');
const rawDir = path.join(root, 'scripts/raw');
const outDir = path.join(root, 'src/data');

const INDEX_URL = 'https://www.nihaixiahope.com/yijing.html';
const SOURCE_SITE = 'https://www.nihaixiahope.com';

const TRIGRAM_GROUPS = [
  { key: 'tian', label: '天', tabId: 'travis2' },
  { key: 'ze', label: '澤', tabId: 'travis3' },
  { key: 'huo', label: '火', tabId: 'travis4' },
  { key: 'lei', label: '雷', tabId: 'travis5' },
  { key: 'feng', label: '風', tabId: 'travis6' },
  { key: 'shui', label: '水', tabId: 'travis7' },
  { key: 'shan', label: '山', tabId: 'travis8' },
  { key: 'di', label: '地', tabId: 'travis9' },
];

function sleep(ms) {
  return new Promise((r) => setTimeout(r, ms));
}

function decodeHtml(s) {
  return s
    .replace(/&nbsp;/g, ' ')
    .replace(/&amp;/g, '&')
    .replace(/&lt;/g, '<')
    .replace(/&gt;/g, '>')
    .replace(/&quot;/g, '"')
    .replace(/&#39;/g, "'");
}

function stripTags(html) {
  return decodeHtml(html.replace(/<br\s*\/?>/gi, '\n').replace(/<[^>]+>/g, ''))
    .replace(/\uFEFF/g, '')
    .replace(/\s+\n/g, '\n')
    .replace(/\n{3,}/g, '\n\n')
    .trim();
}

function parseIntro(html) {
  const introMatch = html.match(/id="travis1"[\s\S]*?<\/div>\s*<div class="tab-pane" id="travis2"/);
  if (!introMatch) return [];
  const chunk = introMatch[0];
  const blocks = [];
  const re = /<(h3|p)([^>]*)>([\s\S]*?)<\/\1>/gi;
  let m;
  while ((m = re.exec(chunk))) {
    const tag = m[1].toLowerCase();
    const text = stripTags(m[3]);
    if (!text) continue;
    blocks.push({ type: tag === 'h3' ? 'heading' : 'prose', text });
  }
  return blocks;
}

function parseHexLinks(html) {
  const items = [];
  for (const group of TRIGRAM_GROUPS) {
    const re = new RegExp(`id="${group.tabId}"[\\s\\S]*?(?=id="travis\\d+"|<\\/div>\\s*<\\/div>\\s*<\\/span>)`, 'i');
    const chunk = html.match(re)?.[0] ?? '';
    const linkRe = /<a[^>]+href="\/blog\/(\d+)\.html"[^>]*>([\d.]+)\.([^<]+)<\/a>/gi;
    let m;
    while ((m = linkRe.exec(chunk))) {
      const index = Number(m[2]);
      const name = stripTags(m[3]);
      items.push({
        id: `gua-${index}`,
        index,
        name,
        upperTrigram: group.label,
        groupKey: group.key,
        blogId: Number(m[1]),
        sourceUrl: `${SOURCE_SITE}/blog/${m[1]}.html`,
      });
    }
  }
  items.sort((a, b) => a.index - b.index);
  return items;
}

function resolveImgSrc(src) {
  if (!src) return '';
  if (/^https?:\/\//i.test(src)) return src;
  if (src.startsWith('//')) return `https:${src}`;
  if (src.startsWith('/')) return `${SOURCE_SITE}${src}`;
  return `${SOURCE_SITE}/${src}`;
}

/** 正文卦象圖（排除站標、備案等） */
function isContentImage(src) {
  return /\/blog\/image\//i.test(src);
}

function pushImageBlock(blocks, attrs) {
  const srcRaw = attrs.match(/src=["']([^"']+)["']/i)?.[1];
  const alt = attrs.match(/alt=["']([^"']*)["']/i)?.[1] ?? '';
  const src = resolveImgSrc(srcRaw ?? '');
  if (!src || !isContentImage(src)) return;
  if (blocks.some((b) => b.type === 'image' && b.src === src)) return;
  blocks.push({ type: 'image', src, alt: stripTags(alt) });
}

function parseArticle(html) {
  const titleMatch = html.match(/class="postHeaderTitle">([^<]+)/);
  const title = titleMatch ? stripTags(titleMatch[1]) : '';
  const artMatch = html.match(/<header class="postHeader">[\s\S]*?<article>([\s\S]*?)<\/article>/);
  if (!artMatch) return { title, blocks: [] };
  const body = artMatch[1];
  const blocks = [];
  // 圖常嵌在 <p> 內；須先抽出 img，再取文字，否則 stripTags 會丟掉圖
  const tokenRe = /<(h[1-6]|p)(\s[^>]*)?>([\s\S]*?)<\/\1>|<img\b([^>]*)\/?>/gi;
  let m;
  while ((m = tokenRe.exec(body))) {
    if (m[0].toLowerCase().startsWith('<img')) {
      pushImageBlock(blocks, m[4] ?? '');
      continue;
    }
    const tag = m[1].toLowerCase();
    const inner = m[3] ?? '';
    const imgRe = /<img\b([^>]*)\/?>/gi;
    let im;
    const imgs = [];
    while ((im = imgRe.exec(inner))) imgs.push(im[1] ?? '');
    const text = stripTags(inner);
    if (text) {
      const isHeading =
        /^h/.test(tag) || (tag === 'p' && /<strong[^>]*>/.test(inner) && text.length < 40);
      blocks.push({ type: isHeading ? 'heading' : 'prose', text });
    }
    for (const attrs of imgs) pushImageBlock(blocks, attrs);
  }
  return { title, blocks };
}

async function fetchText(url) {
  const res = await fetch(url, {
    headers: { 'User-Agent': 'jingpan-ingest/1.0 (study mirror)' },
  });
  if (!res.ok) throw new Error(`${url} ${res.status}`);
  return res.text();
}

async function downloadImage(url, destPath) {
  if (fs.existsSync(destPath)) return true;
  const res = await fetch(url, {
    headers: { 'User-Agent': 'jingpan-ingest/1.0 (study mirror)' },
  });
  if (!res.ok) {
    console.warn(`skip image ${url} ${res.status}`);
    return false;
  }
  const buf = Buffer.from(await res.arrayBuffer());
  fs.mkdirSync(path.dirname(destPath), { recursive: true });
  fs.writeFileSync(destPath, buf);
  return true;
}

/** 遠程圖下載到 public，JSON 改寫為站內路徑 */
async function localizeImages(hexagrams) {
  const imgDir = path.join(root, 'public/yijing/images');
  fs.mkdirSync(imgDir, { recursive: true });
  let ok = 0;
  let fail = 0;
  for (const h of hexagrams) {
    for (const b of h.blocks) {
      if (b.type !== 'image' || !b.src) continue;
      if (b.src.startsWith('/yijing/images/')) continue;
      const name = path.basename(new URL(b.src).pathname);
      if (!name) continue;
      const dest = path.join(imgDir, name);
      const saved = await downloadImage(b.src, dest);
      if (saved) {
        b.src = `/yijing/images/${name}`;
        ok += 1;
      } else {
        fail += 1;
      }
      await sleep(80);
    }
  }
  console.log(`images localized: ${ok} ok, ${fail} fail → public/yijing/images`);
}

async function main() {
  fs.mkdirSync(rawDir, { recursive: true });
  fs.mkdirSync(outDir, { recursive: true });

  let indexHtml = fs.existsSync(path.join(rawDir, 'yijing.html'))
    ? fs.readFileSync(path.join(rawDir, 'yijing.html'), 'utf8')
    : null;
  if (!indexHtml) {
    indexHtml = await fetchText(INDEX_URL);
    fs.writeFileSync(path.join(rawDir, 'yijing.html'), indexHtml);
  }

  const intro = parseIntro(indexHtml);
  const links = parseHexLinks(indexHtml);
  if (links.length < 60) {
    console.warn(`warn: only parsed ${links.length} hexagram links`);
  }

  const hexagrams = [];
  for (let i = 0; i < links.length; i += 1) {
    const link = links[i];
    const rawPath = path.join(rawDir, `yijing-${link.blogId}.html`);
    let html;
    if (fs.existsSync(rawPath)) {
      html = fs.readFileSync(rawPath, 'utf8');
    } else {
      process.stdout.write(`fetch ${link.index}. ${link.name} …\n`);
      html = await fetchText(link.sourceUrl);
      fs.writeFileSync(rawPath, html);
      await sleep(400);
    }
    const { title, blocks } = parseArticle(html);
    hexagrams.push({ ...link, title, blocks });
  }

  await localizeImages(hexagrams);

  const meta = {
    title: '斷易天機 · 易經六十四卦',
    sourceSite: SOURCE_SITE,
    sourceIndex: INDEX_URL,
    note: '正文取自倪海廈天紀《斷易天機》公開網頁整理，非《紫微斗數全書》原文。僅供研習對照。',
  };

  fs.writeFileSync(
    path.join(outDir, 'yijingIntro.json'),
    JSON.stringify({ ...meta, blocks: intro }, null, 2),
    'utf8',
  );
  fs.writeFileSync(
    path.join(outDir, 'yijingHexagrams.json'),
    JSON.stringify({ ...meta, hexagrams }, null, 2),
    'utf8',
  );
  fs.writeFileSync(
    path.join(outDir, 'yijingToc.json'),
    JSON.stringify(
      {
        groups: TRIGRAM_GROUPS.map((g) => ({
          ...g,
          items: hexagrams.filter((h) => h.groupKey === g.key).map((h) => ({ id: h.id, index: h.index, name: h.name })),
        })),
      },
      null,
      2,
    ),
    'utf8',
  );

  console.log(
    `done: intro ${intro.length} blocks, hexagrams ${hexagrams.length}, images ${hexagrams.reduce((n, h) => n + h.blocks.filter((b) => b.type === 'image').length, 0)}`,
  );
}

main().catch((e) => {
  console.error(e);
  process.exit(1);
});
