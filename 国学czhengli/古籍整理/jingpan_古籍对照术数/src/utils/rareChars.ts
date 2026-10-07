/** 生僻字括注音，例：同躔（chán）。只注音，不改原文用字。 */
const RARE_PINYIN: Record<string, string> = {
  躔: 'chán',
  彀: 'gòu',
  尪: 'wāng',
  杻: 'chǒu',
  轝: 'yú',
  櫛: 'zhì',
  漚: 'ōu',
  羸: 'léi',
  窔: 'yǎo',
  齟: 'jǔ',
  齬: 'yǔ',
  纍: 'léi',
  紲: 'xiè',
  騭: 'zhì',
  縻: 'mí',
  廩: 'lǐn',
  殀: 'yāo',
  髡: 'kūn',
};

export function annotateRareChars(text: string): string {
  return text.replace(/[\u4e00-\u9fff]/g, (ch, offset, full) => {
    const py = RARE_PINYIN[ch];
    if (!py) return ch;
    const next = full.slice(offset + 1, offset + 2);
    if (next === '（' || next === '(') return ch;
    return `${ch}（${py}）`;
  });
}
