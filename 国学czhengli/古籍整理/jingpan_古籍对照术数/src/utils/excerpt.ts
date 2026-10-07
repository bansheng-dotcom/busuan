import type { ExcerptItem } from '@/types';
import type { BuiltChart } from '@/utils/chart';
import bookChapters from '@/data/bookChapters.json';
import type { BookChapter } from '@/types';

const EXCERPT_CHAPTERS = [
  'taiwei-fu',
  'xingxing-fu',
  'xingyuan-lun',
  'gumu-fu',
  'shiergong-dedi',
  'shiergong-shixian',
  'ding-gui-ju',
  'ding-fu-ju',
];

function palaceStarNames(chart: BuiltChart): string[] {
  const ming = chart.palaces.find((p) => p.name === '命宫' || p.name === '命宮');
  if (!ming) return [];
  return [...ming.majorStars, ...ming.minorStars, ...ming.adjectiveStars].map((s) => s.name);
}

/** 从卷一赋文中摘取含当前命宫星曜之名的原句，不做改写。 */
export function extractExcerpts(chart: BuiltChart): ExcerptItem[] {
  const names = palaceStarNames(chart);
  if (!names.length) return [];
  const chapters = bookChapters as BookChapter[];
  const result: ExcerptItem[] = [];

  for (const ch of chapters) {
    if (!EXCERPT_CHAPTERS.includes(ch.id)) continue;
    const sentences = ch.raw
      .split(/[。！？\n]/)
      .map((s) => s.trim())
      .filter(Boolean);
    for (const sentence of sentences) {
      if (names.some((n) => sentence.includes(n.replace(/化/, '')))) {
        result.push({
          chapterId: ch.id,
          chapterTitle: ch.title,
          text: sentence.endsWith('。') ? sentence : `${sentence}。`,
        });
      }
      if (result.length >= 24) return result;
    }
  }
  return result;
}
