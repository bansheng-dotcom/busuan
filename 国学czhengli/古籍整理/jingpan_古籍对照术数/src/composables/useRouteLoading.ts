import { ref, readonly } from 'vue';

/** 与路由 name 对齐的页面轮廓骨架 */
export type SkeletonType =
  | 'home'
  | 'chart'
  | 'book'
  | 'yijing'
  | 'yijing-detail'
  | 'star-dict'
  | 'star-dict-detail'
  | 'pattern-dict'
  | 'luopan'
  | 'almanac'
  | 'naming'
  | 'liuren'
  | 'yaogua'
  | 'about';

/** 首屏默认 true，避免硬刷新时懒加载 chunk 未到出现白屏 */
const isLoading = ref(true);
const skeletonType = ref<SkeletonType>('home');
const progress = ref(0);

let generation = 0;
let climbTimer: ReturnType<typeof setInterval> | null = null;
let finishTimer: ReturnType<typeof setTimeout> | null = null;

function clearTimers() {
  if (climbTimer != null) {
    clearInterval(climbTimer);
    climbTimer = null;
  }
  if (finishTimer != null) {
    clearTimeout(finishTimer);
    finishTimer = null;
  }
}

function startClimb(gen: number) {
  clearTimers();
  progress.value = 0;
  climbTimer = setInterval(() => {
    if (gen !== generation) return;
    if (progress.value >= 80) return;
    const step = progress.value < 40 ? 8 : progress.value < 65 ? 4 : 1.5;
    progress.value = Math.min(80, progress.value + step);
  }, 120);
}

function start(type: SkeletonType = 'home') {
  generation += 1;
  const gen = generation;
  clearTimers();
  skeletonType.value = type;
  isLoading.value = true;
  startClimb(gen);
}

function done() {
  const gen = generation;
  clearTimers();
  // 骨架立刻收起，进度条再冲到 100% 后淡出
  isLoading.value = false;
  progress.value = 100;
  finishTimer = setTimeout(() => {
    if (gen !== generation) return;
    progress.value = 0;
    finishTimer = null;
  }, 180);
}

function fail() {
  generation += 1;
  clearTimers();
  isLoading.value = false;
  progress.value = 0;
}

/** 路由加载态（模块单例，供 router 钩子与组件共用） */
export function useRouteLoading() {
  return {
    isLoading: readonly(isLoading),
    skeletonType: readonly(skeletonType),
    progress: readonly(progress),
    start,
    done,
    fail,
  };
}
