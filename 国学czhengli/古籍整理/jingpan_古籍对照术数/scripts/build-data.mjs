/**
 * 星曜词典、格局词典仍从 source-juan1.txt 结构化切条。
 * 古籍阅读页卷一正文以国学典籍网 bookJuan1.json 为准。
 */
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const root = path.resolve(__dirname, '..');
const sourcePath = path.join(root, 'src/data/source-juan1.txt');
const outDir = path.join(root, 'src/data');

const raw = fs.readFileSync(sourcePath, 'utf8').replace(/\r\n/g, '\n');

function cleanWiki(text) {
  const start = text.indexOf('### 太微賦');
  const endMark = text.search(/取自「|检索自|檢索自/);
  let body = text.slice(start, endMark === -1 ? undefined : endMark);
  body = body.replace(/^\|.*\|$/gm, '');
  return body.trim();
}

const body = cleanWiki(raw);

const TOC = [
  { id: 'taiwei-fu', title: '太微賦', match: '太微賦' },
  { id: 'xingxing-fu', title: '形性賦', match: '形性賦' },
  { id: 'xingyuan-lun', title: '星垣論', match: '星垣論' },
  { id: 'dou-shu-zhun-sheng', title: '斗數準繩', match: '斗數準繩' },
  { id: 'dou-shu-fawei-lun', title: '斗數發微論', match: '斗數發微論' },
  { id: 'chongbu-goulv', title: '重補斗數彀率', match: '重補斗數彀率' },
  { id: 'zengbu-taiwei-fu', title: '增補太微賦', match: '增補太微賦' },
  { id: 'zhuxing-wenda', title: '諸星問答論', match: '諸星問答論' },
  { id: 'gumu-fu', title: '斗數骨髓賦', match: '斗數骨髓賦' },
  { id: 'nvming-gumu-fu', title: '女命骨髓賦', match: '女命骨髓賦' },
  { id: 'geju-shijue', title: '論各類格局詩訣', match: null },
  { id: 'shi-deng-lun', title: '定富貴貧賤十等論', match: '定富貴貧賤十等論' },
  { id: 'shiergong-dedi', title: '十二宮諸星得地合格訣', match: '十二宮諸星得地合格訣' },
  { id: 'shiergong-shixian', title: '十二宮諸星失陷破格訣', match: '十二宮諸星失陷破格訣' },
  { id: 'dedi-fugui', title: '十二宮諸星得地富貴論', match: '十二宮諸星得地富貴論' },
  { id: 'shixian-pinjian', title: '十二宮諸星失陷貧賤論', match: '十二宮諸星失陷貧賤論' },
  { id: 'ding-fu-ju', title: '定富局', match: '定富局' },
  { id: 'ding-gui-ju', title: '定貴局', match: '定貴局' },
  { id: 'ding-pinjian-ju', title: '定貧賤局', match: '定貧賤局' },
  { id: 'ding-za-ju', title: '定雜局', match: '定雜局' },
];

function sectionByHeader(src, header) {
  const re = new RegExp(`###\\s*${header}\\s*\\n`);
  const m = re.exec(src);
  if (!m) return '';
  const from = m.index + m[0].length;
  const next = src.slice(from).search(/\n###\s+/);
  return (next === -1 ? src.slice(from) : src.slice(from, from + next)).trim();
}

function toBlocks(text, chapterId) {
  const lines = text.split('\n').map((l) => l.trim()).filter(Boolean);
  const blocks = [];
  for (const line of lines) {
    if (line.startsWith('#### ')) {
      blocks.push({
        type: 'heading',
        id: `${chapterId}-${blocks.length}`,
        text: line.replace(/^####\s*/, ''),
      });
      continue;
    }
    if (/^(希夷先生曰|希夷先生答曰|玉蟾先生曰|白玉蟾先生曰)/.test(line)) {
      blocks.push({ type: 'quote', speaker: line.slice(0, line.indexOf('：') + 1) || line.slice(0, 6), text: line });
      continue;
    }
    if (line === '歌曰' || line.startsWith('歌曰：') || line.startsWith('歌曰 ')) {
      blocks.push({ type: 'song-label', text: '歌曰：' });
      if (line.length > 2 && line !== '歌曰') {
        blocks.push({ type: 'song', text: line.replace(/^歌曰[：:\s]*/, '') });
      }
      continue;
    }
    if (line === '詩曰' || line.startsWith('詩曰')) {
      const rest = line.replace(/^詩曰\s*/, '');
      if (rest) blocks.push({ type: 'song', text: rest });
      else blocks.push({ type: 'song-label', text: '詩曰：' });
      continue;
    }
    if (line === '又曰' || line.startsWith('又曰')) {
      const rest = line.replace(/^又曰\s*/, '');
      if (rest) blocks.push({ type: 'song', text: rest });
      else blocks.push({ type: 'song-label', text: '又曰：' });
      continue;
    }
    if (line === '例曰') {
      blocks.push({ type: 'label', text: '例曰' });
      continue;
    }
    if (line.startsWith('答曰')) {
      blocks.push({ type: 'answer', text: line });
      continue;
    }
    blocks.push({ type: 'prose', text: line });
  }
  return blocks;
}

const chapters = [];
let nvmingText = sectionByHeader(body, '女命骨髓賦');
const splitMark = '已前論賦俱系看命要訣';
let gejuText = '';
if (nvmingText.includes(splitMark)) {
  const idx = nvmingText.indexOf(splitMark);
  gejuText = nvmingText.slice(idx).trim();
  nvmingText = nvmingText.slice(0, idx).trim();
}

for (const item of TOC) {
  let text = '';
  if (item.id === 'geju-shijue') {
    text = gejuText;
  } else if (item.id === 'nvming-gumu-fu') {
    text = nvmingText;
  } else {
    text = sectionByHeader(body, item.match);
  }
  chapters.push({
    id: item.id,
    title: item.title,
    volume: 1,
    blocks: toBlocks(text, item.id),
    raw: text,
  });
}

function parseQa(name, question, text) {
  const full = text.trim();
  const pick = (re) => {
    const m = full.match(re);
    return m ? m[1].trim() : '';
  };
  const answer = pick(/((?:答曰|希夷先生答曰)[\s\S]*?)(?=希夷先生曰|玉蟾先生曰|歌曰|$)/);
  const xiYiSaid = pick(/((?:希夷先生曰|希夷先生答曰|希夷先生歌曰)[\s\S]*?)(?=玉蟾先生曰|歌曰|$)/);
  const yuChanSaid = pick(/(玉蟾先生曰[\s\S]*?)(?=歌曰|$)/);
  const songIdx = full.search(/歌曰/);
  let song = '';
  if (songIdx >= 0) {
    song = full.slice(songIdx).replace(/^歌曰\s*/, '歌曰：').trim();
    const cut = song.search(/玉蟾先生曰/);
    if (cut > 0) song = song.slice(0, cut).trim();
  }
  return {
    name,
    question,
    answer,
    xiYiSaid,
    yuChanSaid,
    song,
    fullText: full,
  };
}

const STAR_NAME_MAP = [
  ['紫微', '紫微'],
  ['天機', '天機'],
  ['太陽', '太陽'],
  ['武曲', '武曲'],
  ['天同', '天同'],
  ['廉貞', '廉貞'],
  ['天府', '天府'],
  ['太陰', '太陰'],
  ['貪狼', '貪狼'],
  ['巨門', '巨門'],
  ['天相', '天相'],
  ['天梁', '天梁'],
  ['七殺', '七殺'],
  ['破軍', '破軍'],
  ['文昌', '文昌'],
  ['文曲', '文曲'],
  ['流年昌曲', '流年昌曲'],
  ['左輔', '左輔'],
  ['右弼', '右弼'],
  ['天魁天鉞', '天魁天鉞'],
  ['祿存', '祿存'],
  ['天馬', '天馬'],
  ['化祿', '化祿'],
  ['化權', '化權'],
  ['化科', '化科'],
  ['化忌', '化忌'],
  ['擎羊', '擎羊'],
  ['陀羅', '陀羅'],
  ['羊陀二星總論', '羊陀二星總論'],
  ['火星', '火星'],
  ['鈴星', '鈴星'],
  ['羊陀火鈴四星總論', '羊陀火鈴四星總論'],
  ['天空地劫', '天空地劫'],
  ['天傷天使', '天傷天使'],
  ['天刑', '天刑'],
  ['天姚', '天姚'],
  ['天哭天虛', '天哭天虛'],
];

const qaChapter = chapters.find((c) => c.id === 'zhuxing-wenda');
const qaRaw = qaChapter?.raw || '';
const qaParts = qaRaw.split(/\n(?=####\s)/);
const starDict = {};
const starList = [];

for (const part of qaParts) {
  const hm = part.match(/^####\s*(.+)\s*$/m);
  if (!hm) continue;
  const question = hm[1].trim();
  const content = part.replace(/^####.+\n/, '');
  const mapped = STAR_NAME_MAP.find(([key]) => question.includes(key));
  const name = mapped ? mapped[1] : question.replace(/問|所主|若何|如何|為何|？|\?/g, '').trim();
  const rec = parseQa(name, question, content);
  starDict[name] = rec;
  starList.push(name);
}

/** 点击星曜别名映射到诸星问答条目 */
const starAlias = {
  紫微: '紫微',
  天機: '天機',
  太陽: '太陽',
  武曲: '武曲',
  天同: '天同',
  廉貞: '廉貞',
  天府: '天府',
  太陰: '太陰',
  貪狼: '貪狼',
  巨門: '巨門',
  天相: '天相',
  天梁: '天梁',
  七殺: '七殺',
  破軍: '破軍',
  文昌: '文昌',
  文曲: '文曲',
  左輔: '左輔',
  右弼: '右弼',
  天魁: '天魁天鉞',
  天鉞: '天魁天鉞',
  祿存: '祿存',
  天馬: '天馬',
  化祿: '化祿',
  化權: '化權',
  化科: '化科',
  化忌: '化忌',
  擎羊: '擎羊',
  陀羅: '陀羅',
  火星: '火星',
  鈴星: '鈴星',
  天空: '天空地劫',
  地劫: '天空地劫',
  天刑: '天刑',
  天姚: '天姚',
  天哭: '天哭天虛',
  天虛: '天哭天虛',
  天傷: '天傷天使',
  天使: '天傷天使',
};

function extractSongAfter(label, src) {
  const re = new RegExp(`${label}[\\s\\S]*?詩曰\\s*([^\\n]+)`);
  const m = src.match(re);
  return m ? m[1].trim() : '';
}

const geju = gejuText;
const patternDict = {
  對面朝斗格: {
    condition: '子午宮逢祿存是也',
    originalText: extractSongAfter('論對面朝斗格', geju) || '祿有對面在遷移，子午逢之利祿宜，德合吉壤人敬重，雙全富貴福稀奇。',
    category: '定貴局',
    key: 'duiMianChaoDou',
  },
  科權祿主格: {
    condition: '祿權周勃命中逢',
    originalText: extractSongAfter('論科權祿主格', geju) || '祿權周勃命中逢，入相王朝贊聖功，迎合權星兼吉曜，巍巍富貴列三公。',
    category: '定貴局',
    key: 'keQuanLu',
  },
  左右朝垣格: {
    condition: '天星左右若在三方祿位',
    originalText: extractSongAfter('論左右朝垣格', geju) || '天星左右最高明，若在三方祿位興，武職高登應顯佐，文人名譽列公卿。',
    category: '定貴局',
    key: 'zuoYouChaoYuan',
  },
  文武格: {
    condition: '文曲武曲在身命是也',
    originalText: extractSongAfter('論兼文武格', geju) || '格名文武少人知，遇此須教百事通，更值命宮無殺破，滔滔榮顯是英雄。',
    category: '定貴局',
    key: 'wenWu',
  },
  文星朝命格: {
    condition: '文昌文曲值命',
    originalText: extractSongAfter('論文星朝命格', geju) || '文昌文曲最榮華，值此鬚生富貴家，更得三方祥曜拱，卻如錦上又添花。',
    category: '定貴局',
    key: 'wenXingChaoMing',
  },
  石中隱玉格: {
    condition: '命在子午逢巨門是也',
    originalText: extractSongAfter('論石中隱玉格', geju) || '巨門子午二宮逢，身命逢之必貴榮，更得三方科祿照，石中隱玉是豐隆。',
    category: '定貴局',
    key: 'shiZhongYinYu',
  },
  火貴格: {
    condition: '貪狼遇火名為火貴格，三合照身命是也',
    originalText: extractSongAfter('論貪狼遇火名為火貴格', geju) || '火遇貪狼照命宮，封侯食祿是英雄，三方倘若無兇殺，到老應知福壽隆。',
    category: '定貴局',
    key: 'huoGui',
  },
  七殺朝斗格: {
    condition: '七殺居寅申子午宮，逢魁鉞左右文昌會照',
    originalText: '七殺寅申子午宮，四夷拱手服英雄，魁鉞左右文昌會，權祿名高食萬鍾。',
    category: '定貴局',
    key: 'qiShaChaoDou',
  },
  日月夾財格: {
    condition: '武守命日月來夾是也，財帛宮亦然',
    originalText: '日月夾財，不權則富。',
    category: '定富局',
    key: 'riYueJiaCai',
  },
  財蔭夾印: {
    condition: '相守命武梁來夾是也，田宅宮亦然。',
    originalText: '財蔭夾印 相守命武梁來夾是也，田宅宮亦然。',
    category: '定富局',
    key: 'caiYinJiaYin',
  },
  財祿夾馬: {
    condition: '馬守命武祿來夾是也，逢生旺尤妙。',
    originalText: '財祿夾馬 馬守命武祿來夾是也，逢生旺尤妙。',
    category: '定富局',
    key: 'caiLuJiaMa',
  },
  蔭印拱身: {
    condition: '身臨田宅梁相拱沖是也，勿坐空亡。',
    originalText: '蔭印拱身 身臨田宅梁相拱沖是也，勿坐空亡。',
    category: '定富局',
    key: 'yinYinGongShen',
  },
  日月照璧: {
    condition: '日月臨田宅宮是也，喜居墓庫。',
    originalText: '日月照璧 日月臨田宅宮是也，喜居墓庫。',
    category: '定富局',
    key: 'riYueZhaoBi',
  },
  金燦光輝: {
    condition: '太陽單守，命在午宮是也。',
    originalText: '金燦光輝 太陽單守，命在午宮是也。',
    category: '定富局',
    key: 'jinCanGuangHui',
  },
  日月夾命: {
    condition: '不坐空亡遇逢本宮有吉星是也。',
    originalText: '日月夾命 不坐空亡遇逢本宮有吉星是也。',
    category: '定貴局',
    key: 'riYueJiaMing',
  },
  日出扶桑: {
    condition: '日在卯守命是也，守官祿宮亦然。',
    originalText: '日出扶桑 日在卯守命是也，守官祿宮亦然。',
    category: '定貴局',
    key: 'riChuFuSang',
  },
  月落亥宮: {
    condition: '月在亥守命是也，又名月朗天門。',
    originalText: '月落亥宮 月在亥守命是也，又名月朗天門。',
    category: '定貴局',
    key: 'yueLuoHai',
  },
  月生滄海: {
    condition: '月在子宮守田宅是也。',
    originalText: '月生滄海 月在子宮守田宅是也。',
    category: '定貴局',
    key: 'yueShengCangHai',
  },
  輔弼拱主: {
    condition: '紫微守命二星來拱是也，夾之亦然。',
    originalText: '輔弼拱主 紫微守命二星來拱是也，夾之亦然。',
    category: '定貴局',
    key: 'fuBiGongZhu',
  },
  君臣慶會: {
    condition: '紫微左右同守命是也，更會相武陰妙上。',
    originalText: '君臣慶會 紫微左右同守命是也，更會相武陰妙上。',
    category: '定貴局',
    key: 'junChenQingHui',
  },
  財印夾祿: {
    condition: '祿守命梁相來夾是也，入財亦然。',
    originalText: '財印夾祿 祿守命梁相來夾是也，入財亦然。',
    category: '定貴局',
    key: 'caiYinJiaLu',
  },
  祿馬佩印: {
    condition: '馬前有祿印星同宮是也。',
    originalText: '祿馬佩印 馬前有祿印星同宮是也。',
    category: '定貴局',
    key: 'luMaPeiYin',
  },
  坐貴向貴: {
    condition: '謂魁鉞在命迭相坐拱是也。',
    originalText: '坐貴向貴 謂魁鉞在命迭相坐拱是也。',
    category: '定貴局',
    key: 'zuoGuiXiangGui',
  },
  馬頭帶劍: {
    condition: '謂馬有刃是也不是居午格。',
    originalText: '馬頭帶劍 謂馬有刃是也不是居午格。',
    category: '定貴局',
    key: 'maTouDaiJian',
  },
  刑囚夾印: {
    condition: '天刑廉貞同臨身命主武勇之人。',
    originalText: '刑囚夾印 天刑廉貞同臨身命主武勇之人。',
    category: '定貴局',
    key: 'xingQiuJiaYin',
  },
  貪火相逢: {
    condition: '謂二星守命同居廟旺是也。',
    originalText: '貪火相逢 謂二星守命同居廟旺是也。',
    category: '定貴局',
    key: 'tanHuoXiangFeng',
  },
  武曲守垣: {
    condition: '武守命卯宮是也，余不是。',
    originalText: '武曲守垣 武守命卯宮是也，余不是。',
    category: '定貴局',
    key: 'wuQuShouYuan',
  },
  權祿生逢: {
    condition: '二星守命廟旺是也，陷不是。',
    originalText: '權祿生逢 二星守命廟旺是也，陷不是。',
    category: '定貴局',
    key: 'quanLuShengFeng',
  },
  羊刃入廟: {
    condition: '辰戍丑未守命遇吉是也。',
    originalText: '羊刃入廟 辰戍丑未守命遇吉是也。',
    category: '定貴局',
    key: 'yangRenRuMiao',
  },
  金輿扶駕: {
    condition: '紫微守命前後有日月來夾是也。',
    originalText: '金輿扶駕 紫微守命前後有日月來夾是也。',
    category: '定貴局',
    key: 'jinYuFuJia',
  },
  生不逢時: {
    condition: '命坐空亡逢廉貞是也。',
    originalText: '生不逢時 命坐空亡逢廉貞是也。',
    category: '定貧賤局',
    key: 'shengBuFengShi',
  },
  祿逢兩殺: {
    condition: '祿坐空亡又逢空劫殺星是也。',
    originalText: '祿逢兩殺 祿坐空亡又逢空劫殺星是也。',
    category: '定貧賤局',
    key: 'luFengLiangSha',
  },
  馬落空亡: {
    condition: '馬既落亡雖祿沖會無用主奔波。',
    originalText: '馬落空亡 馬既落亡雖祿沖會無用主奔波。',
    category: '定貧賤局',
    key: 'maLuoKongWang',
  },
  日月藏輝: {
    condition: '日月反背又逢巨暗是也。',
    originalText: '日月藏輝 日月反背又逢巨暗是也。',
    category: '定貧賤局',
    key: 'riYueCangHui',
  },
  財與囚仇: {
    condition: '武貞同守身命是也。',
    originalText: '財與囚仇 武貞同守身命是也。',
    category: '定貧賤局',
    key: 'caiYuQiuChou',
  },
  一生孤貧: {
    condition: '謂破守命星陷地是也。',
    originalText: '一生孤貧 謂破守命星陷地是也。',
    category: '定貧賤局',
    key: 'yiShengGuPin',
  },
  君子在野: {
    condition: '謂四殺守身命而言臨陷地是也。',
    originalText: '君子在野 謂四殺守身命而言臨陷地是也。',
    category: '定貧賤局',
    key: 'junZiZaiYe',
  },
  兩重華蓋: {
    condition: '謂祿存化祿坐命遇空劫是也。',
    originalText: '兩重華蓋 謂祿存化祿坐命遇空劫是也。',
    category: '定貧賤局',
    key: 'liangChongHuaGai',
  },
  風雲際會: {
    condition: '身命雖弱二限逢祿馬是也。',
    originalText: '風雲際會 身命雖弱二限逢祿馬是也。',
    category: '定雜局',
    key: 'fengYunJiHui',
  },
  錦上添花: {
    condition: '謂限破惡星而行吉地是也。',
    originalText: '錦上添花 謂限破惡星而行吉地是也。',
    category: '定雜局',
    key: 'jinShangTianHua',
  },
  祿衰馬困: {
    condition: '限逢七殺祿馬空亡是也。',
    originalText: '祿衰馬困 限逢七殺祿馬空亡是也。',
    category: '定雜局',
    key: 'luShuaiMaKun',
  },
  衣錦還鄉: {
    condition: '少年不遂四十後行墓運是也。',
    originalText: '衣錦還鄉 少年不遂四十後行墓運是也。',
    category: '定雜局',
    key: 'yiJinHuanXiang',
  },
  步數無依: {
    condition: '前限接後限連綿不分是也。',
    originalText: '步數無依 前限接後限連綿不分是也。',
    category: '定雜局',
    key: 'buShuWuYi',
  },
  水上駕星: {
    condition: '一年好一年不好是也。',
    originalText: '水上駕星 一年好一年不好是也。',
    category: '定雜局',
    key: 'shuiShangJiaXing',
  },
  吉凶相伴: {
    condition: '命有主星限前則發限衰不發是也。',
    originalText: '吉兇相伴 命有主星限前則發限衰不發是也。',
    category: '定雜局',
    key: 'jiXiongXiangBan',
  },
  枯木逢春: {
    condition: '謂命衰限好是也。',
    originalText: '枯木逢春 謂命衰限好是也。',
    category: '定雜局',
    key: 'kuMuFengChun',
  },
};

const juan1Path = path.join(outDir, 'bookJuan1.json');
const juan2Path = path.join(outDir, 'bookJuan2.json');
const juan3Path = path.join(outDir, 'bookJuan3.json');
const juan1Book = fs.existsSync(juan1Path) ? JSON.parse(fs.readFileSync(juan1Path, 'utf8')) : chapters;
const juan2 = fs.existsSync(juan2Path) ? JSON.parse(fs.readFileSync(juan2Path, 'utf8')) : [];
const juan3 = fs.existsSync(juan3Path) ? JSON.parse(fs.readFileSync(juan3Path, 'utf8')) : [];

const allChapters = [...juan1Book, ...juan2, ...juan3];
const bookToc = allChapters.map(({ id, title, volume }) => ({
  id,
  title,
  volume: volume ?? 1,
}));

fs.writeFileSync(path.join(outDir, 'bookToc.json'), JSON.stringify(bookToc, null, 2));
fs.writeFileSync(path.join(outDir, 'bookChapters.json'), JSON.stringify(allChapters, null, 2));
fs.writeFileSync(
  path.join(outDir, 'starDict.json'),
  JSON.stringify({ stars: starList, dict: starDict, alias: starAlias }, null, 2),
);
fs.writeFileSync(path.join(outDir, 'patternDict.json'), JSON.stringify(patternDict, null, 2));

console.log(
  'chapters',
  allChapters.length,
  `v1=${juan1Book.length} v2=${juan2.length} v3=${juan3.length}`,
);
console.log('stars', starList.join(', '));
console.log('patterns', Object.keys(patternDict).length);
