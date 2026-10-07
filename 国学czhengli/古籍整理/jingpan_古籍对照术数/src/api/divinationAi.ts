export type DivinationKind = 'liuren' | 'yaogua';

export interface DivinationAiPayload {
  kind: DivinationKind;
  question?: string;
  cast: Record<string, unknown>;
}

const API_URL =
  (import.meta.env.VITE_DIVINATION_AI_API as string | undefined)?.trim() ||
  '/api/divination-ai';

export function isDivinationAiConfigured(): boolean {
  return Boolean(API_URL);
}

export async function fetchDivinationAi(payload: DivinationAiPayload): Promise<string> {
  if (!API_URL) {
    throw new Error('AI 解讀服務未配置，請聯繫站點管理員。');
  }

  let res: Response;
  try {
    res = await fetch(API_URL, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
      signal: AbortSignal.timeout(200_000),
    });
  } catch (err) {
    if (err instanceof DOMException && err.name === 'TimeoutError') {
      throw new Error('請求逾時，模型仍在整理，請稍後重試。');
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
