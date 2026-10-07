import * as OpenCC from 'opencc-js';
import type { ScriptMode } from '@/types';

const toHans = OpenCC.Converter({ from: 'tw', to: 'cn' });
const toHant = OpenCC.Converter({ from: 'cn', to: 'tw' });

/** 阅读底本为国学典籍网。简体仅作显示转换，不改底层原文。 */
export function convertScript(text: string, mode: ScriptMode): string {
  if (!text) return '';
  if (mode === 'hans') return toHans(text);
  return toHant(text).replaceAll('鬥', '斗').replaceAll('醜', '丑');
}
