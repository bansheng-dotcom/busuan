export const PICKER_ITEM_H = 44;
export const PICKER_WHEEL_H = 264;
export const PICKER_PAD = (PICKER_WHEEL_H - PICKER_ITEM_H) / 2;

/** 把指定项滚到可视中心 */
export function scrollPickerItemToCenter(wheel: HTMLElement, item: HTMLElement) {
  const itemCenter = item.offsetTop + item.offsetHeight / 2;
  const target = itemCenter - wheel.clientHeight / 2;
  wheel.scrollTop = Math.max(0, target);
}

/** 吸附到距中心最近的一格，并返回该项 */
export function snapWheelToNearest(wheel: HTMLElement): HTMLElement | null {
  const items = Array.from(wheel.querySelectorAll<HTMLElement>('.item'));
  if (!items.length) return null;
  const center = wheel.scrollTop + wheel.clientHeight / 2;
  let best: HTMLElement | null = null;
  let bestDist = Infinity;
  for (const item of items) {
    const c = item.offsetTop + item.offsetHeight / 2;
    const d = Math.abs(c - center);
    if (d < bestDist) {
      bestDist = d;
      best = item;
    }
  }
  if (best) scrollPickerItemToCenter(wheel, best);
  return best;
}

export function scrollAllPickerWheels(root: HTMLElement | null) {
  if (!root) return;
  root.querySelectorAll('.wheel').forEach((node) => {
    const wheel = node as HTMLElement;
    const active = wheel.querySelector('.item.active') as HTMLElement | null;
    if (active) scrollPickerItemToCenter(wheel, active);
  });
}

/** 滚动停止后吸附；返回清理函数 */
export function bindWheelSnap(
  wheel: HTMLElement,
  onSnap: (item: HTMLElement) => void,
): () => void {
  let timer: number | null = null;
  const finish = () => {
    timer = null;
    const item = snapWheelToNearest(wheel);
    if (item) onSnap(item);
  };
  const schedule = () => {
    if (timer != null) window.clearTimeout(timer);
    timer = window.setTimeout(finish, 90);
  };
  const onScroll = () => schedule();
  const onTouchEnd = () => schedule();
  wheel.addEventListener('scroll', onScroll, { passive: true });
  wheel.addEventListener('touchend', onTouchEnd, { passive: true });
  wheel.addEventListener('pointerup', onTouchEnd, { passive: true });
  return () => {
    if (timer != null) window.clearTimeout(timer);
    wheel.removeEventListener('scroll', onScroll);
    wheel.removeEventListener('touchend', onTouchEnd);
    wheel.removeEventListener('pointerup', onTouchEnd);
  };
}
