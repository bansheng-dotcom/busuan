import type { ChartAiPayload, ChartAiTimelineEvent } from '@/utils/chartAiPayload';

const API_URL =
  (import.meta.env.VITE_CHART_AI_HOLOGRAPHIC_API as string | undefined)?.trim() ||
  (import.meta.env.VITE_CHART_AI_API as string | undefined)?.trim() ||
  '/api/chart-ai-holographic';

export function isChartAiConfigured(): boolean {
  return Boolean(API_URL);
}

export function fetchChartAiHolographic(
  payload: ChartAiPayload & {
    timeline?: ChartAiTimelineEvent[];
    anchorYear?: number;
  },
): Promise<string> {
  if (!API_URL) {
    return Promise.reject(new Error('全息診斷服務未配置，請聯繫站點管理員。'));
  }

  return postChartAi(API_URL, payload);
}

async function postChartAi(url: string, payload: unknown): Promise<string> {
  let res: Response;
  try {
    res = await fetch(url, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
      signal: AbortSignal.timeout(200_000),
    });
  } catch (err) {
    if (err instanceof DOMException && err.name === 'TimeoutError') {
      throw new Error('請求逾時，模型仍在整理材料，請稍後重試。');
    }
    throw err;
  }

  const data = (await res.json().catch(() => ({}))) as { content?: string; error?: string };

  if (!res.ok) {
    const msg = data.error || `請求失敗（${res.status}）`;
    if (/timed out/i.test(msg)) {
      throw new Error('模型回應逾時，請稍後重試。');
    }
    throw new Error(msg);
  }

  if (!data.content?.trim()) {
    throw new Error('AI 返回內容為空，請稍後重試。');
  }

  return data.content.trim();
}
