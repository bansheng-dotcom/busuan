export type ScriptMode = 'hans' | 'hant';
export type ThemeMode = 'xuanpaper' | 'nightsky';

export type BookVolume = 1 | 2 | 3;

export interface BookTocItem {
  id: string;
  title: string;
  volume?: BookVolume;
}

export type BookBlock = {
  type: 'heading' | 'quote' | 'song' | 'song-label' | 'answer' | 'prose' | 'label' | 'palace-chart' | 'table';
  id?: string;
  speaker?: string;
  text?: string;
  title?: string;
  note?: string;
  palaces?: Record<string, string>;
  headers?: string[];
  rows?: string[][];
};

export interface BookChapter {
  id: string;
  title: string;
  volume?: BookVolume;
  blocks: BookBlock[];
  raw: string;
}

export interface StarEntry {
  name: string;
  question: string;
  answer: string;
  xiYiSaid: string;
  yuChanSaid: string;
  song: string;
  fullText: string;
}

export interface PatternEntry {
  condition: string;
  originalText: string;
  category: string;
  key: string;
}

export interface ChartStar {
  name: string;
  type: string;
  brightness: string;
  mutagen: string;
  scope: string;
}

export interface ChartPalace {
  name: string;
  aliasName: string;
  heavenlyStem: string;
  earthlyBranch: string;
  isBodyPalace: boolean;
  isOriginalPalace: boolean;
  majorStars: ChartStar[];
  minorStars: ChartStar[];
  adjectiveStars: ChartStar[];
  decadal?: { range: [number, number]; heavenlyStem: string; earthlyBranch: string };
  /** 当前推运日期所落之大限宫 */
  isDecadalLimit?: boolean;
  /** 当前推运日期所落之流年宫 */
  isYearlyLimit?: boolean;
}

export interface MatchedPattern {
  name: string;
  condition: string;
  originalText: string;
  category: string;
}

export interface ExcerptItem {
  chapterId: string;
  chapterTitle: string;
  text: string;
}

export interface ReadingCite {
  title: string;
  url: string;
  bookId?: string;
}

export interface ReadingQuote {
  classic: string;
  vernacular: string;
  cite: ReadingCite;
}

export interface PalaceSanFang {
  self: string;
  opposite: string;
  triA: string;
  triB: string;
}

export interface PalaceReading {
  name: string;
  aliasName: string;
  heavenlyStem: string;
  earthlyBranch: string;
  isBodyPalace: boolean;
  starLine: string;
  mutagenLine: string;
  sanFang: PalaceSanFang;
  quotes: ReadingQuote[];
}
