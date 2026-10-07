/** PC / H5 共用逻辑宽度，保证导出图尺寸与疏密一致 */
const EXPORT_BOARD_WIDTH = 760;

function waitTwoFrames(): Promise<void> {
  return new Promise((resolve) => {
    requestAnimationFrame(() => {
      requestAnimationFrame(() => resolve());
    });
  });
}

/**
 * 截取命盘节点为 PNG canvas。
 * 使用离屏固定宽度克隆，避免改动页面布局，并让 PC/H5 导出一致。
 * modern-screenshot 动态导入，避免进排盘页时被过期 Vite 预构建卡住。
 */
export async function captureElement(source: HTMLElement): Promise<HTMLCanvasElement> {
  const scrollX = window.scrollX;
  const scrollY = window.scrollY;
  const paper =
    getComputedStyle(document.documentElement).getPropertyValue('--zw-paper').trim() || '#fbf4e4';

  const boardWrap = source.querySelector('.chart-board-wrap');
  const target = boardWrap instanceof HTMLElement ? boardWrap : source;

  const wrapper = document.createElement('div');
  wrapper.setAttribute('aria-hidden', 'true');
  wrapper.style.cssText = [
    'position:fixed',
    'left:-10000px',
    'top:0',
    'pointer-events:none',
    'z-index:-1',
  ].join(';');

  const clone = target.cloneNode(true) as HTMLElement;
  clone.style.width = `${EXPORT_BOARD_WIDTH}px`;
  clone.style.maxWidth = `${EXPORT_BOARD_WIDTH}px`;
  clone.style.boxSizing = 'border-box';

  const board =
    clone.classList.contains('chart-board')
      ? clone
      : clone.querySelector('.chart-board');
  if (board instanceof HTMLElement) {
    board.style.width = '100%';
    board.style.aspectRatio = '1';
  }

  wrapper.appendChild(clone);
  document.body.appendChild(wrapper);

  try {
    const { domToCanvas } = await import('modern-screenshot');
    await waitTwoFrames();
    return await domToCanvas(clone, {
      scale: 2,
      backgroundColor: paper,
    });
  } finally {
    wrapper.remove();
    window.scrollTo(scrollX, scrollY);
  }
}
