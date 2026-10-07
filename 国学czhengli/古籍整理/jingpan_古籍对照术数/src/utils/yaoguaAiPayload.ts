import type { DivinationAiPayload } from '@/api/divinationAi';
import type { CastResult } from '@/utils/yaogua';

const POS_LABEL = ['初', '二', '三', '四', '五', '上'];

export function buildYaoguaAiPayload(input: {
  result: CastResult;
  primaryName: string;
  relatingName?: string;
  primaryOverview?: string | null;
  relatingOverview?: string | null;
  question?: string;
}): DivinationAiPayload {
  const q = (input.question || '').trim();
  const { result } = input;
  return {
    kind: 'yaogua',
    question: q || undefined,
    cast: {
      primary: {
        index: result.primaryIndex,
        name: input.primaryName,
        overview: input.primaryOverview || undefined,
      },
      relating: result.relatingIndex
        ? {
            index: result.relatingIndex,
            name: input.relatingName || '',
            overview: input.relatingOverview || undefined,
          }
        : null,
      // 1–6 爻位，便于模型阅读
      changingPositions: result.changingPositions.map((p) => p + 1),
      lines: result.lines.map((l) => ({
        position: l.position + 1,
        label: l.label || POS_LABEL[l.position] || '',
        changing: l.changing,
      })),
    },
  };
}
