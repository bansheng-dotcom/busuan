import { nextTick, watch, type Ref } from 'vue';

/** Element Plus 横向 tabs：中间项点击后滚到可视区中央，首尾仍贴边 */
export function useCenterScrollTabs(
  rootRef: Ref<HTMLElement | undefined>,
  activeTab: Ref<string>,
  tabNames: readonly string[],
) {
  const centerActiveTab = () => {
    const root = rootRef.value;
    if (!root) return;

    const nav = root.querySelector('.el-tabs__nav') as HTMLElement | null;
    const navScroll = root.querySelector('.el-tabs__nav-scroll') as HTMLElement | null;
    if (!nav || !navScroll) return;

    const items = Array.from(root.querySelectorAll('.el-tabs__item'));
    const index = tabNames.indexOf(activeTab.value);
    if (index < 0 || !items[index]) return;

    const containerSize = navScroll.clientWidth;
    const navSize = nav.scrollWidth;
    if (navSize <= containerSize) return;

    const activeItem = items[index] as HTMLElement;
    let offset: number;

    if (index === 0) {
      offset = 0;
    } else if (index === items.length - 1) {
      offset = navSize - containerSize;
    } else {
      const tabLeft = activeItem.offsetLeft;
      const tabWidth = activeItem.offsetWidth;
      offset = tabLeft - (containerSize - tabWidth) / 2;
      offset = Math.max(0, Math.min(offset, navSize - containerSize));
    }

    nav.style.transition = 'transform 0.28s ease';
    nav.style.transform = `translateX(-${offset}px)`;
  };

  const scheduleCenter = () => {
    void nextTick(() => {
      window.setTimeout(centerActiveTab, 60);
    });
  };

  watch(activeTab, scheduleCenter);

  return { centerActiveTab, scheduleCenter };
}
