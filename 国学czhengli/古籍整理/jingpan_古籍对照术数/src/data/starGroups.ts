/** 斗属、化气、五行据卷二《论诸星分属南北斗化吉凶并分属五行》；斗序据卷一《诸星问答论》。不另拟。 */

export type DouKind = 'bei' | 'nan' | 'zhong' | '';

export interface StarMeta {
  dou: DouKind;
  /** 如「北斗第一」「南斗第三」「中天」 */
  tag: string;
  /** 卷二摘句：五行 · 化气 · 所主 */
  line: string;
}

export const STAR_META: Record<string, StarMeta> = {
  紫微: { dou: 'zhong', tag: '中天之尊星', line: '屬土 · 化帝座 · 官祿主' },
  天機: { dou: 'nan', tag: '南斗第三', line: '屬木 · 化善 · 兄弟主' },
  太陽: { dou: 'zhong', tag: '南北斗', line: '屬火 · 化貴 · 官祿主' },
  武曲: { dou: 'bei', tag: '北斗第六', line: '屬金 · 化財 · 財帛主' },
  天同: { dou: 'nan', tag: '南斗第四', line: '屬水金 · 化福 · 福德主' },
  廉貞: { dou: 'bei', tag: '北斗第五', line: '屬火 · 化殺囚 · 官祿主' },
  天府: { dou: 'nan', tag: '南斗第一', line: '屬土 · 化令星 · 財帛田宅主' },
  太陰: { dou: 'zhong', tag: '南北斗', line: '屬水 · 化富 · 財帛田宅主' },
  貪狼: { dou: 'bei', tag: '北斗第一', line: '屬水木 · 化桃花殺 · 主禍福' },
  巨門: { dou: 'bei', tag: '北斗第二', line: '屬水 · 化暗 · 主是非' },
  天相: { dou: 'nan', tag: '南斗第五', line: '屬水 · 化印 · 官祿主' },
  天梁: { dou: 'nan', tag: '南斗第二', line: '屬土 · 化蔭 · 壽星' },
  七殺: { dou: 'nan', tag: '南斗第六', line: '屬火金 · 降星 · 遇帝為權' },
  破軍: { dou: 'bei', tag: '北斗第七', line: '屬水 · 化耗 · 夫妻子女奴僕' },
  祿存: { dou: 'bei', tag: '北斗第三', line: '屬土 · 司爵貴壽' },
  文昌: { dou: 'zhong', tag: '南北斗', line: '屬金 · 司科甲' },
  文曲: { dou: 'bei', tag: '北斗第四', line: '屬水 · 主科甲' },
  左輔: { dou: 'bei', tag: '北斗', line: '令星' },
  右弼: { dou: 'bei', tag: '北斗', line: '令星' },
  天魁天鉞: { dou: '', tag: '不入正曜', line: '屬火' },
  天馬: { dou: '', tag: '不入正曜', line: '屬火' },
  擎羊: { dou: 'bei', tag: '北斗浮星', line: '屬金 · 化刑' },
  陀羅: { dou: 'bei', tag: '北斗助星', line: '屬金 · 化忌' },
  火星: { dou: 'nan', tag: '南斗助星', line: '屬火' },
  鈴星: { dou: 'nan', tag: '南斗助星', line: '屬火' },
  化祿: { dou: '', tag: '四化', line: '屬土 · 喜見祿存' },
  化權: { dou: '', tag: '四化', line: '屬木 · 喜會巨門武曲' },
  化科: { dou: '', tag: '四化', line: '屬水 · 喜會魁鉞' },
  化忌: { dou: '', tag: '四化', line: '屬水 · 即計都星' },
};

/** 十四主星：中天 / 南斗斗序 / 北斗斗序（缺第三祿存、第四文曲）。 */
const MAJOR_ZHONG = ['紫微', '太陽', '太陰'] as const;
const MAJOR_NAN = ['天府', '天梁', '天機', '天同', '天相', '七殺'] as const;
const MAJOR_BEI = ['貪狼', '巨門', '廉貞', '武曲', '破軍'] as const;

const ZHENG_ZHONG = ['文昌'] as const;
const ZHENG_BEI = ['祿存', '文曲', '左輔', '右弼'] as const;

const OTHER_GROUPS: { title: string; hint: string; names: string[] }[] = [
  { title: '吉星不入正曜', hint: '卷二：魁鉞天馬亦是吉星，俱不入正曜。', names: ['天魁天鉞', '天馬'] },
  { title: '北斗浮星助星', hint: '卷二：擎羊北斗浮星化刑，陀羅北斗助星化忌。', names: ['擎羊', '陀羅', '羊陀二星總論'] },
  { title: '南斗助星', hint: '卷二：火星、鈴星南斗助星。', names: ['火星', '鈴星'] },
  { title: '羊陀火鈴', hint: '卷一總論條目。', names: ['羊陀火鈴四星總論'] },
  { title: '四化', hint: '卷二：化祿屬土，化權屬木，化科化忌屬水。', names: ['化祿', '化權', '化科', '化忌'] },
];

export interface StarSubGroup {
  title: string;
  hint: string;
  names: string[];
}

export interface StarSection {
  id: string;
  title: string;
  hint: string;
  groups: StarSubGroup[];
}

function pick(all: string[], names: readonly string[]): string[] {
  return names.filter((n) => all.includes(n));
}

export function starTag(name: string): string {
  return STAR_META[name]?.tag ?? '';
}

export function starLine(name: string): string {
  return STAR_META[name]?.line ?? '';
}

export function buildStarSections(allNames: string[]): StarSection[] {
  const majorZhong = pick(allNames, MAJOR_ZHONG);
  const majorNan = pick(allNames, MAJOR_NAN);
  const majorBei = pick(allNames, MAJOR_BEI);
  const zhengZhong = pick(allNames, ZHENG_ZHONG);
  const zhengBei = pick(allNames, ZHENG_BEI);
  const used = new Set<string>([...majorZhong, ...majorNan, ...majorBei, ...zhengZhong, ...zhengBei]);
  const otherGroups = OTHER_GROUPS.map((g) => ({
    ...g,
    names: pick(allNames, g.names),
  })).filter((g) => g.names.length > 0);
  otherGroups.forEach((g) => g.names.forEach((n) => used.add(n)));
  const leftover = allNames.filter((n) => !used.has(n));
  if (leftover.length) {
    otherGroups.push({ title: '雜曜', hint: '卷一其餘條目。', names: leftover });
  }
  return [
    {
      id: 'major14',
      title: '十四主星',
      hint: '盤面十四正曜。中天日月據卷二「南北斗」；南斗六星、北斗五星據卷一斗序排列。北斗第三祿存、第四文曲見下節。',
      groups: [
        { title: '中天南北斗', hint: '紫微中天之尊星；太陽、太陰卷二謂南北斗。', names: majorZhong },
        { title: '南斗六星', hint: '天府一、天梁二、天機三、天同四、天相五、七殺六。', names: majorNan },
        { title: '北斗五星', hint: '貪狼一、巨門二、廉貞五、武曲六、破軍七。', names: majorBei },
      ].filter((g) => g.names.length > 0),
    },
    {
      id: 'zhengyao',
      title: '其餘正曜',
      hint: '卷二：自紫微至輔弼一十八星俱南北斗正曜。此處補齊十四以外的五星。',
      groups: [
        { title: '南北斗', hint: '文昌屬金，司科甲。', names: zhengZhong },
        { title: '北斗', hint: '祿存第三、文曲第四；輔弼二星北斗令星。', names: zhengBei },
      ].filter((g) => g.names.length > 0),
    },
    {
      id: 'others',
      title: '輔佐與雜曜',
      hint: '浮星、助星、四化、雜曜分列，標注仍依卷二。',
      groups: otherGroups,
    },
  ];
}
