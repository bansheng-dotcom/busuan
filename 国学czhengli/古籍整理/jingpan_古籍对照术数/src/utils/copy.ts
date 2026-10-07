import { ElMessage } from 'element-plus';

/**
 * 手机端触碰易触发 ElMessage hover 暂停计时，导致提示永不关闭。
 * duration=0 + 定时强制 close，与 store/app 字号提示同一策略。
 */
const TOAST_MS = 800;
let toastOpen = false;
let toastTimer: ReturnType<typeof setTimeout> | null = null;

function showCopyToast(type: 'success' | 'warning', message: string) {
  if (toastOpen) return;
  toastOpen = true;
  const instance = ElMessage({
    type,
    message,
    duration: 0,
    onClose: () => {
      toastOpen = false;
      if (toastTimer != null) {
        clearTimeout(toastTimer);
        toastTimer = null;
      }
    },
  });
  toastTimer = setTimeout(() => {
    instance.close();
  }, TOAST_MS);
}

export async function copyText(text: string): Promise<void> {
  const value = text.trim();
  if (!value) {
    showCopyToast('warning', '沒有可複製的文本');
    return;
  }
  try {
    await navigator.clipboard.writeText(value);
    showCopyToast('success', '已複製原文');
  } catch {
    const ta = document.createElement('textarea');
    ta.value = value;
    document.body.appendChild(ta);
    ta.select();
    document.execCommand('copy');
    document.body.removeChild(ta);
    showCopyToast('success', '已複製原文');
  }
}

export function copySelection(): void {
  const sel = window.getSelection()?.toString() ?? '';
  void copyText(sel);
}
