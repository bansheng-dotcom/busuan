import type { DivinationAiPayload } from '@/api/divinationAi';
import type { LiurenResult } from '@/utils/liuren';

export function buildLiurenAiPayload(input: {
  result: LiurenResult;
  month: number;
  day: number;
  hour: number;
  question?: string;
}): DivinationAiPayload {
  const q = (input.question || '').trim();
  return {
    kind: 'liuren',
    question: q || undefined,
    cast: {
      month: input.month,
      day: input.day,
      hour: input.hour,
      palaceName: input.result.palace.name,
      luck: input.result.palace.luck,
      summary: input.result.palace.summary,
    },
  };
}
