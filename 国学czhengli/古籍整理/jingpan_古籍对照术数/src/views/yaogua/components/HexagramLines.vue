<template>
  <div class="lines" :aria-label="display('卦象', false)">
    <div
      v-for="row in rows"
      :key="row.position"
      class="line"
      :class="{ changing: row.changing, yang: row.yang === 1, yin: row.yang === 0 }"
    >
      <span class="pos">{{ display(row.posLabel, false) }}</span>
      <div class="bars" aria-hidden="true">
        <template v-if="row.yang === 1">
          <i class="bar solid" />
        </template>
        <template v-else>
          <i class="bar half" />
          <i class="gap" />
          <i class="bar half" />
        </template>
      </div>
      <span class="tag">{{ display(row.label, false) }}</span>
    </div>
  </div>
</template>

<script lang="ts">
import { computed, defineComponent, type PropType } from 'vue';
import { useDisplayText } from '@/composables/useDisplayText';
import type { YaoLine } from '@/utils/yaogua';

const POS = ['初', '二', '三', '四', '五', '上'];

export default defineComponent({
  name: 'HexagramLines',
  props: {
    lines: { type: Array as PropType<YaoLine[]>, required: true },
  },
  setup(props) {
    const { display } = useDisplayText();
    const rows = computed(() =>
      [...props.lines]
        .slice()
        .reverse()
        .map((l) => ({
          ...l,
          posLabel: `${POS[l.position] ?? ''}${l.yang ? '九' : '六'}`,
        })),
    );
    return { display, rows };
  },
});
</script>

<style scoped>
.lines {
  display: flex;
  flex-direction: column;
  gap: 0.45rem;
  width: 100%;
  max-width: 280px;
}
.line {
  display: grid;
  grid-template-columns: 2.4rem 1fr 2.6rem;
  align-items: center;
  gap: 0.45rem;
}
.pos,
.tag {
  font-size: 0.72rem;
  color: var(--zw-muted);
  letter-spacing: 0.06em;
}
.tag {
  text-align: right;
}
.bars {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.35rem;
  min-height: 12px;
}
.bar {
  display: block;
  height: 8px;
  border-radius: 2px;
  background: var(--zw-primary);
}
.bar.solid {
  width: 100%;
}
.bar.half {
  flex: 1;
}
.gap {
  width: 0.55rem;
  flex: none;
}
.line.changing .bar {
  background: var(--zw-gold);
}
.line.changing .tag {
  color: var(--zw-gold);
  font-weight: 600;
}
</style>
