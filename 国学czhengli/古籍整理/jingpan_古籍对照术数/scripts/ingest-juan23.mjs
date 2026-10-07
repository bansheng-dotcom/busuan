/**
 * 从国学典籍网卷一至卷三公开文本切章入库。
 * 只切章、简转繁，不校改、不补写。
 *
 * 底本：
 * - 卷一 http://ab.newdu.com/book/ms261794.html
 * - 卷二 http://ab.newdu.com/book/ms261795.html
 * - 卷三 http://ab.newdu.com/book/ms261796.html
 */
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import * as OpenCC from 'opencc-js';
import { findAsciiChartStart, toBlocksWithCharts } from './parse-ascii-charts.mjs';

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const root = path.resolve(__dirname, '..');
const outDir = path.join(root, 'src/data');
const toHantRaw = OpenCC.Converter({ from: 'cn', to: 'tw' });

/** OpenCC 会把「斗」转成「鬥」、「丑」转成「醜」；本书用地支与北斗，转回。 */
function toHant(text) {
  return toHantRaw(text).replaceAll('鬥', '斗').replaceAll('醜', '丑');
}

const rawDir = path.join(__dirname, 'raw');
const JUAN1_RAW = path.join(rawDir, 'ms261794.html');
const JUAN2_RAW = path.join(rawDir, 'ms261795.html');
const JUAN3_RAW = path.join(rawDir, 'ms261796.txt');

function stripNav(text) {
  return text
    .replace(/^[\s\S]*?(紫微斗数全书卷[二三])/, '$1')
    .replace(/上一篇[\s\S]*$/, '')
    .replace(/电脑版手机版[\s\S]*$/, '')
    .replace(/\[ 新都首页 \][\s\S]*$/, '')
    .replace(/更新时间：.*$/gm, '')
    .trim();
}

function extractJuan(raw, marker) {
  const start = raw.indexOf(marker);
  const end = raw.search(/上一篇|电脑版手机版|\[ 新都首页 \]/);
  if (start < 0) throw new Error(`${marker} start not found`);
  return raw.slice(start, end < 0 ? undefined : end).trim();
}

function extractJuan2(raw) {
  return extractJuan(raw, '紫微斗数全书卷二');
}

function extractJuan3(raw) {
  const start = raw.indexOf('紫微斗数全书卷三');
  const end = raw.search(/电脑版手机版|上一篇|\[ 新都首页 \]/);
  if (start < 0) throw new Error('juan3 start not found');
  return raw.slice(start, end < 0 ? undefined : end).trim();
}

/** 按原文标题切；标题以底本出现为准。卷一章 id 与站内锚点对齐。 */
const JUAN1_HEADS = [
  { id: 'taiwei-fu', title: '太微赋', match: '太微赋' },
  { id: 'xingxing-fu', title: '形性赋', match: '形性赋' },
  { id: 'xingyuan-lun', title: '星垣论', match: '星垣论' },
  { id: 'dou-shu-zhun-sheng', title: '斗数准绳', match: '斗数准绳' },
  { id: 'dou-shu-fawei-lun', title: '斗数发微论', match: '斗数发微论' },
  { id: 'chongbu-goulv', title: '重补斗数彀率', match: '重补斗数彀率' },
  { id: 'zengbu-taiwei-fu', title: '增补太微赋', match: '增补太微赋' },
  { id: 'zhuxing-wenda', title: '诸星问答论', match: '诸星问答论' },
  { id: 'gumu-fu', title: '斗数骨随赋', match: '斗数骨随赋' },
  { id: 'nvming-gumu-fu', title: '女命骨髓赋', match: '女命骨髓赋' },
  { id: 'shi-deng-lun', title: '定富贵贫贱十等论', match: '定富贵贫贱十等论' },
  { id: 'shiergong-dedi', title: '十二宫诸星得地合格诀', match: '十二宫诸星得地合格诀' },
  { id: 'shiergong-shixian', title: '十二宫诸星失陷破格诀', match: '十二宫诸星失陷破格诀' },
  { id: 'dedi-fugui', title: '十二宫诸星得地富贵论', match: '十二宫诸星得地富贵论' },
  { id: 'shixian-pinjian', title: '十二宫诸星失陷贫贱论', match: '十二宫诸星失陷贫贱论' },
  { id: 'ding-fu-ju', title: '定富局', match: '定富局' },
  { id: 'ding-gui-ju', title: '定贵局', match: '定贵局' },
  { id: 'ding-pinjian-ju', title: '定贫贱局', match: '定贫贱局' },
  { id: 'ding-za-ju', title: '定杂局', match: '定杂局' },
];

const JUAN2_HEADS = [
  { id: 'an-shenming-li', title: '安身命例', match: '安身命例' },
  { id: 'an-shiergong-li', title: '安十二宫例', match: '安十二宫例' },
  { id: 'qi-wuxing-yin', title: '起五行寅例', match: '起五行寅例' },
  { id: 'huajia-nayin', title: '六十花甲子纳音歌', match: '六十花甲子纳音歌' },
  { id: 'an-nanbeidou', title: '安南北斗诸星诀', match: '安南北斗诸星诀' },
  { id: 'an-changqu', title: '安文昌文曲星诀', match: '安文昌文曲星诀' },
  { id: 'an-fuxing', title: '安左辅右弼星诀', match: '安左辅右弼星诀' },
  { id: 'an-kuiyue', title: '安天魁天钺诀', match: '安天魁天钺诀' },
  { id: 'an-tianma', title: '安天马星诀', match: '安天马星诀' },
  { id: 'an-lucun', title: '安禄存星诀', match: '安禄存星诀' },
  { id: 'an-yangtuo', title: '安擎羊陀罗二星诀', match: '安擎羊陀罗二星诀' },
  { id: 'an-huoling', title: '安火铃二星诀', match: '安火铃二星诀' },
  { id: 'an-sihua-bianhua', title: '安禄权科忌四星变化诀', match: '安禄权科忌四星变化诀' },
  { id: 'kongjie-jue', title: '天空地劫诀', match: '天空地劫诀' },
  { id: 'an-shangshi', title: '安天伤天使诀', match: '安天伤天使诀' },
  { id: 'an-suisha-lu', title: '安十二宫太岁杀禄诀', match: '安十二宫太岁杀禄诀' },
  { id: 'an-xingyao', title: '安天刑天姚星诀', match: '安天刑天姚星诀' },
  { id: 'an-santai', title: '安三台八座二星诀', match: '安三台八座二星诀' },
  { id: 'an-kuxu', title: '安天哭天虚星诀', match: '安天哭天虚星诀' },
  { id: 'an-longfeng', title: '安龙池凤阁诀', match: '安龙池凤阁诀' },
  { id: 'an-taifu', title: '安台辅封诀', match: '安台辅封诀' },
  { id: 'an-fenggao', title: '安封诰诀', match: '安封诰诀' },
  { id: 'an-changsheng', title: '安长生沐浴十二宫', match: '安长生、沐浴' },
  { id: 'an-hongluan', title: '安红鸾天喜诀', match: '安红鸾天喜诀' },
  { id: 'an-sangmen', title: '安丧门白虎吊客官府四飞星诀', match: '安丧门白虎吊客官府四飞星诀' },
  { id: 'an-doujun', title: '安斗君诀', match: '安斗君诀' },
  { id: 'an-tiande', title: '安天德月德解神诀', match: '安天德月德解神诀' },
  { id: 'an-feisha', title: '安飞天三杀诀', match: '安飞天三杀诀' },
  { id: 'an-jielu', title: '安截路空亡诀', match: '安截路空亡诀' },
  { id: 'an-xunzhong', title: '安旬中空亡诀', match: '安旬中空亡诀' },
  { id: 'an-daxian', title: '安大限诀', match: '安大限诀' },
  { id: 'an-xiaoxian', title: '安小限诀', match: '安小限诀' },
  { id: 'an-tongxian', title: '安童限诀', match: '安童限诀' },
  { id: 'an-mingzhu', title: '安命主', match: '安命主' },
  { id: 'an-shenzhu', title: '安身主', match: '安身主' },
  { id: 'jinsuo-tieshe', title: '论安命金锁铁蛇关', match: '论安命金锁铁蛇关' },
  { id: 'zhuluo-sanxian', title: '定男女竹萝三限', match: '定男女竹萝三限' },
  { id: 'shiergong-ruoqiang', title: '定十二宫弱强', match: '定十二宫弱强' },
  { id: 'xingchen-luoxian', title: '定十二宫星辰落闲', match: '定十二宫星辰落闲' },
  { id: 'an-liulu', title: '安流禄流羊流陀诀', match: '安流禄流羊流陀诀' },
  { id: 'shengke-zhihua', title: '论星辰生克制化', match: '论星辰生克制化' },
  { id: 'nanbeidou-wuxing', title: '论诸星分属南北斗化吉凶并分属五行', match: '论诸星分属南北斗化吉凶并分属五行' },
  { id: 'antu-tianfu', title: '安紫微天府图', match: '安天府图', backToChart: true },
  { id: 'shangshi-tu', title: '殇使祸福紧慢图', match: '殇使祸福紧慢图', backToChart: true },
  { id: 'luquan-tu', title: '禄权科忌图', match: '禄权科忌图', backToChart: true },
  { id: 'miaowang-tu', title: '十二宫庙旺落陷图', match: '庙 |旺 |得地', backToChart: true },
  // 须整行标题；勿命中「安十二宫例」中「一 命宫、二兄弟…」列表
  { id: 'lun-minggong', title: '一 命宫', match: '一 命宫', lineExact: true },
  { id: 'lun-xiongdi', title: '二 兄弟', match: '二 兄弟', lineExact: true },
  { id: 'lun-qieqie', title: '三 妻妾', match: '三 妻妾', lineExact: true },
  { id: 'lun-zinv', title: '四 子女', match: '四 子女', lineExact: true },
  { id: 'lun-caibo', title: '五 财帛', match: '五 财帛', lineExact: true },
  { id: 'lun-jie', title: '六 疾厄', match: '六 疾厄', lineExact: true },
  { id: 'lun-qianyi', title: '七 迁移', match: '七 迁移', lineExact: true },
  { id: 'lun-nupu', title: '八 奴仆', match: '八 奴仆', lineExact: true },
  { id: 'lun-guanlu', title: '九 官禄', match: '九 官禄', lineExact: true },
  { id: 'lun-tianzhai', title: '十 田宅', match: '十 田宅', lineExact: true },
  { id: 'lun-fude', title: '十一 福德', match: '十一 福德', lineExact: true },
  { id: 'lun-fumu', title: '十二 父母', match: '十二 父母', lineExact: true },
];

const JUAN3_HEADS = [
  { id: 'tanxing-yaolun', title: '谈星要论', match: '谈星要论' },
  { id: 'lun-ruming-ruge', title: '论人命入格', match: '论人命入格' },
  { id: 'lun-geshu-gaoxia', title: '论格星数高下', match: '论格星数高下' },
  { id: 'lun-nannu-tongyi', title: '论男女命同异', match: '论男女命同异' },
  { id: 'lun-xiaoer-ming', title: '论小儿命', match: '论小儿命' },
  { id: 'ding-xiaoer-shengshi', title: '定小儿生时诀', match: '定小儿生时诀' },
  { id: 'lun-shengshi-anming', title: '论人生时安命吉凶', match: '论人生时安命吉凶' },
  { id: 'lun-shengshi-diqie', title: '论人生时要审的确', match: '论人生时要审的确' },
  { id: 'lun-xiaoer-keqin', title: '论小儿克亲', match: '论小儿克亲' },
  { id: 'lun-xianpin-houfu', title: '论命先贫后富', match: '论命先贫后富' },
  { id: 'lun-daxian-shinian', title: '论大限十年祸福何如', match: '论大限十年祸福何如' },
  { id: 'lun-erxian-taisui', title: '论二限太岁吉凶', match: '论二限太岁吉凶' },
  { id: 'lun-xingxian-nanbei', title: '论行限分南北斗', match: '论行限分南北斗' },
  { id: 'lun-liunian-xingsha', title: '论流年太岁吉凶星杀', match: '论流年太岁吉凶星杀' },
  { id: 'lun-yinzhi-yanshou', title: '论阴骘延寿', match: '论阴骘延寿' },
  { id: 'lun-yangtuo-diebing', title: '论羊陀迭并', match: '论羊陀迭并' },
  { id: 'lun-qisha-chongfeng', title: '论七杀重逢', match: '论七杀重逢' },
  { id: 'lun-xianchen-suoji', title: '论大小限星辰过十二宫遇十二支所忌诀', match: '论大小限星辰过十二宫遇十二支所忌诀' },
  { id: 'lun-liming-xingxian-ge', title: '论立命行限宫歌', match: '论立命行限宫歌' },
  { id: 'lun-taisui-xiaoxian-miaoxian', title: '论太岁小限星辰庙陷遇十二宫中吉凶', match: '论太岁小限星辰庙陷遇十二宫中吉凶' },
  { id: 'lun-tongyuan-suoyi', title: '论诸星同垣各司所宜分别富贵贫贱夭寿', match: '论诸星同垣各司所宜分别富贵贫贱夭寿' },
];

function escapeRe(s) {
  return s.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
}

/** lineExact：整行恰好为标题（避开列表中的「一 命宫、…」）。 */
function findHeadIndex(src, match, lineExact = false, backToChart = false) {
  let idx = -1;
  if (!lineExact) idx = src.indexOf(match);
  else {
    const re = new RegExp(`(?:^|\\n)([ \\t]*${escapeRe(match)})[ \\t]*(?=\\n|$)`);
    const m = re.exec(src);
    if (!m) return -1;
    idx = m.index + (m[0].startsWith('\n') ? 1 : 0) + (m[1].length - match.length);
  }
  if (backToChart && idx >= 0) {
    idx = findAsciiChartStart(src, idx);
  }
  return idx;
}

function splitByHeads(src, heads, volume) {
  const hits = heads
    .map((h) => ({
      ...h,
      index: findHeadIndex(src, h.match, Boolean(h.lineExact), Boolean(h.backToChart)),
    }))
    .filter((h) => h.index >= 0)
    .sort((a, b) => a.index - b.index);

  const chapters = [];
  for (let i = 0; i < hits.length; i++) {
    const cur = hits[i];
    const from = cur.index;
    const to = i + 1 < hits.length ? hits[i + 1].index : src.length;
    const raw = src.slice(from, to).trim();
    chapters.push({
      id: cur.id,
      title: toHant(cur.title),
      volume,
      blocks: toBlocks(raw, cur.id),
      raw: toHant(raw),
    });
  }
  return chapters;
}

function toBlocks(text, chapterId) {
  return toBlocksWithCharts(text, toHant, (line, blocks) => {
    const t = line.trim();
    if (t.startsWith('诗曰') || t.startsWith('詩曰')) {
      blocks.push({ type: 'song-label', text: '詩曰：' });
      const rest = t.replace(/^[诗詩]曰\s*/, '');
      if (rest) blocks.push({ type: 'song', text: toHant(rest) });
      return;
    }
    if (t.startsWith('歌曰')) {
      blocks.push({ type: 'song-label', text: '歌曰：' });
      const rest = t.replace(/^歌曰[：:\s]*/, '');
      if (rest) blocks.push({ type: 'song', text: toHant(rest) });
      return;
    }
    if (t === '又' || t.startsWith('又曰')) {
      blocks.push({ type: 'song-label', text: toHant(t) });
      return;
    }
    blocks.push({ type: 'prose', text: toHant(line) });
  }).concat([]);
}

function wrapJuan3Lines(src) {
  if (src.includes('\n谈星要论') || src.split('\n').length > 20) return src;
  let out = src;
  for (const h of JUAN3_HEADS) {
    out = out.replaceAll(h.match, `\n${h.match}\n`);
  }
  const extra = [
    '诗曰',
    '子年太岁',
    '丑年太岁',
    '寅年太岁',
    '卯年太岁',
    '辰年太岁',
    '巳年太岁',
    '午年太岁',
    '未年太岁',
    '申年太岁',
    '酉年太岁',
    '戌年太岁',
    '亥年太岁',
    '紫微 庙',
    '天府 庙',
    '天相 庙',
    '天梁 庙',
    '天同 庙',
    '天机 庙',
    '太阳 庙',
    '太阴 庙',
    '文昌 庙',
    '文曲 庙',
    '武曲 庙',
    '贪狠 庙',
    '贪狼 庙',
    '廉贞 庙',
    '巨门 庙',
    '七杀 庙',
    '破军 庙',
    '擎羊 庙',
    '陀罗 庙',
    '火星 庙',
    '铃星 庙',
    '魁钺',
    '左辅右弼',
    '禄存 十二',
    '天马',
    '科权禄',
    '劫空',
    '伤使',
    '命宫',
    '身宫',
    '纳音',
    '财帛',
    '财宅',
    '财福',
  ];
  for (const k of extra) {
    out = out.replaceAll(k, `\n${k}`);
  }
  return out.replace(/\n{3,}/g, '\n\n').trim();
}

const juan1Raw = extractJuan(fs.readFileSync(JUAN1_RAW, 'utf8'), '紫微斗数全书卷一');
const juan2Raw = extractJuan2(fs.readFileSync(JUAN2_RAW, 'utf8'));
const juan3Raw = wrapJuan3Lines(extractJuan3(fs.readFileSync(JUAN3_RAW, 'utf8')));

fs.writeFileSync(path.join(outDir, 'source-juan1-newdu.txt'), `${juan1Raw}\n`);
fs.writeFileSync(path.join(outDir, 'source-juan2.txt'), `${juan2Raw}\n`);
fs.writeFileSync(path.join(outDir, 'source-juan3.txt'), `${juan3Raw}\n`);

const juan1 = splitByHeads(juan1Raw, JUAN1_HEADS, 1);
const juan2 = splitByHeads(juan2Raw, JUAN2_HEADS, 2);
const juan3 = splitByHeads(juan3Raw, JUAN3_HEADS, 3);

const NOTE = '国学典籍网公开正文，按原文标题切章后简转繁，不校改。';
const sources = {
  juan1: {
    title: '卷一',
    note: NOTE,
    url: 'http://ab.newdu.com/book/ms261794.html',
  },
  juan2: {
    title: '卷二',
    note: NOTE,
    url: 'http://ab.newdu.com/book/ms261795.html',
  },
  juan3: {
    title: '卷三',
    note: NOTE,
    url: 'http://ab.newdu.com/book/ms261796.html',
  },
};

fs.writeFileSync(path.join(outDir, 'bookJuan1.json'), JSON.stringify(juan1, null, 2));
fs.writeFileSync(path.join(outDir, 'bookJuan2.json'), JSON.stringify(juan2, null, 2));
fs.writeFileSync(path.join(outDir, 'bookJuan3.json'), JSON.stringify(juan3, null, 2));
fs.writeFileSync(path.join(outDir, 'bookSources.json'), JSON.stringify(sources, null, 2));

console.log(
  'juan1',
  juan1.length,
  juan1.map((c) => `${c.id}:${c.raw.length}`).join(' | '),
);
console.log(
  'juan2',
  juan2.length,
  juan2.map((c) => `${c.id}:${c.raw.length}`).join(' | '),
);
console.log(
  'juan3',
  juan3.length,
  juan3.map((c) => `${c.id}:${c.raw.length}`).join(' | '),
);
