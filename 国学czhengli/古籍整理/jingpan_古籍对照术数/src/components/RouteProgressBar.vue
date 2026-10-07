<template>
  <div
    class="route-progress"
    :class="{ visible: show }"
    aria-hidden="true"
  >
    <div class="route-progress__bar" :style="{ width: `${progress}%` }" />
  </div>
</template>

<script lang="ts">
import { computed, defineComponent } from 'vue';
import { useRouteLoading } from '@/composables/useRouteLoading';

export default defineComponent({
  name: 'RouteProgressBar',
  setup() {
    const { isLoading, progress } = useRouteLoading();
    const show = computed(() => isLoading.value || progress.value > 0);
    return { show, progress };
  },
});
</script>

<style scoped>
.route-progress {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  height: 2px;
  z-index: 10000;
  pointer-events: none;
  opacity: 0;
  transition: opacity 0.2s ease;
}

.route-progress.visible {
  opacity: 1;
}

.route-progress__bar {
  height: 100%;
  /* 朱砂线：不用 --zw-primary（宣纸下是深紫，看起来发黑） */
  background: #b42318;
  transition: width 0.16s ease-out;
}
</style>
