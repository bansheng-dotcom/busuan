/**
 * 《周易》上下經 · 文王卦序（第 1–64 卦）
 * 上經 1–30，下經 31–64。前後卦跳轉嚴格依此序，不用八卦宮位重排。
 */
export const WEN_HEXAGRAM_ORDER = [
  // 上經
  '乾',
  '坤',
  '屯',
  '蒙',
  '需',
  '訟',
  '師',
  '比',
  '小畜',
  '履',
  '泰',
  '否',
  '同人',
  '大有',
  '謙',
  '豫',
  '隨',
  '蠱',
  '臨',
  '觀',
  '噬嗑',
  '賁',
  '剝',
  '復',
  '無妄',
  '大畜',
  '頤',
  '大過',
  '坎',
  '離',
  // 下經
  '咸',
  '恆',
  '遁',
  '大壯',
  '晉',
  '明夷',
  '家人',
  '睽',
  '蹇',
  '解',
  '損',
  '益',
  '夬',
  '姤',
  '萃',
  '升',
  '困',
  '井',
  '革',
  '鼎',
  '震',
  '艮',
  '漸',
  '歸妹',
  '豐',
  '旅',
  '巽',
  '兌',
  '渙',
  '節',
  '中孚',
  '小過',
  '既濟',
  '未濟',
] as const;

export type WenHexagramName = (typeof WEN_HEXAGRAM_ORDER)[number];

/** 卦序號 1–64 → 短名；非法則空字串 */
export function wenNameOf(index: number): string {
  if (index < 1 || index > 64) return '';
  return WEN_HEXAGRAM_ORDER[index - 1] ?? '';
}

/** 上一卦序號；已是第一卦則 null */
export function wenPrevIndex(index: number): number | null {
  if (index <= 1 || index > 64) return null;
  return index - 1;
}

/** 下一卦序號；已是第六十四卦則 null */
export function wenNextIndex(index: number): number | null {
  if (index < 1 || index >= 64) return null;
  return index + 1;
}

export function wenSectionOf(index: number): '上經' | '下經' | '' {
  if (index >= 1 && index <= 30) return '上經';
  if (index >= 31 && index <= 64) return '下經';
  return '';
}
