<template>
  <div class="sheet-cascader">
    <SheetField :text="displayText" :placeholder="placeholder" @click="handleOpen" />
    <BottomSheet
      v-model="open"
      :title="title"
      show-toolbar
      :cancel-text="cancelText"
      :confirm-text="confirmText"
      @cancel="handleCancel"
      @confirm="handleConfirm"
    >
      <div class="cols">
        <div
          v-for="(col, colIdx) in columns"
          :key="colIdx"
          class="col"
        >
          <button
            v-for="node in col"
            :key="String(node.value)"
            type="button"
            class="cell"
            :class="{ active: draft[colIdx] === node.value }"
            @click="handleColPick(colIdx, node)"
          >
            {{ node.label }}
          </button>
        </div>
      </div>
    </BottomSheet>
  </div>
</template>

<script lang="ts">
import { computed, defineComponent, ref, type PropType } from 'vue';
import BottomSheet from './BottomSheet.vue';
import SheetField from './SheetField.vue';

export interface SheetCascaderOption {
  value: string;
  label: string;
  children?: SheetCascaderOption[];
}

export default defineComponent({
  name: 'SheetCascader',
  components: { BottomSheet, SheetField },
  props: {
    modelValue: { type: Array as PropType<string[]>, default: () => [] },
    options: { type: Array as PropType<SheetCascaderOption[]>, required: true },
    title: { type: String, default: '' },
    placeholder: { type: String, default: '請選擇' },
    separator: { type: String, default: ' / ' },
    cancelText: { type: String, default: '取消' },
    confirmText: { type: String, default: '確定' },
  },
  emits: {
    'update:modelValue': (_v: string[]) => true,
    change: (_v: string[]) => true,
  },
  setup(props, { emit }) {
    const open = ref(false);
    const draft = ref<string[]>([]);

    const findNode = (nodes: SheetCascaderOption[], value: string) =>
      nodes.find((n) => n.value === value);

    const columns = computed(() => {
      const cols: SheetCascaderOption[][] = [props.options];
      let level = props.options;
      for (let i = 0; i < draft.value.length; i += 1) {
        const node = findNode(level, draft.value[i]);
        if (!node?.children?.length) break;
        cols.push(node.children);
        level = node.children;
      }
      return cols;
    });

    const labelsOf = (path: string[]) => {
      const labels: string[] = [];
      let level = props.options;
      for (const val of path) {
        const node = findNode(level, val);
        if (!node) break;
        labels.push(node.label);
        level = node.children ?? [];
      }
      return labels;
    };

    const displayText = computed(() => labelsOf(props.modelValue).join(props.separator));

    const handleOpen = () => {
      draft.value = props.modelValue.length ? [...props.modelValue] : [];
      if (!draft.value.length && props.options[0]) {
        draft.value = [props.options[0].value];
      }
      open.value = true;
    };

    const handleColPick = (colIdx: number, node: SheetCascaderOption) => {
      const next = draft.value.slice(0, colIdx);
      next.push(node.value);
      if (node.children?.length) {
        next.push(node.children[0].value);
        let cur = node.children[0];
        while (cur.children?.length) {
          next.push(cur.children[0].value);
          cur = cur.children[0];
        }
      }
      draft.value = next;
    };

    const handleCancel = () => {
      open.value = false;
    };

    const handleConfirm = () => {
      const path = [...draft.value];
      if (!path.length) {
        open.value = false;
        return;
      }
      // trim to deepest selected complete chain
      let level = props.options;
      const valid: string[] = [];
      for (const val of path) {
        const node = findNode(level, val);
        if (!node) break;
        valid.push(val);
        if (!node.children?.length) break;
        level = node.children;
      }
      emit('update:modelValue', valid);
      emit('change', valid);
      open.value = false;
    };

    return {
      open,
      draft,
      columns,
      displayText,
      handleOpen,
      handleColPick,
      handleCancel,
      handleConfirm,
    };
  },
});
</script>

<style scoped>
.sheet-cascader {
  width: 100%;
}
.cols {
  display: flex;
  min-height: 240px;
  max-height: min(50vh, 360px);
  flex: 1;
}
.col {
  flex: 1;
  min-width: 0;
  overflow-y: auto;
  -webkit-overflow-scrolling: touch;
  border-right: 1px solid var(--zw-line);
  scrollbar-width: none;
  -ms-overflow-style: none;
}
.col::-webkit-scrollbar {
  display: none;
  width: 0;
  height: 0;
}
.col:last-child {
  border-right: 0;
}
.cell {
  display: block;
  width: 100%;
  border: 0;
  background: transparent;
  text-align: left;
  padding: 12px 10px;
  font-family: inherit;
  font-size: 13px;
  letter-spacing: 0.04em;
  color: var(--zw-ink);
  line-height: 1.35;
}
.cell.active {
  color: var(--zw-primary);
  font-weight: 600;
  background: color-mix(in srgb, var(--zw-gold) 14%, transparent);
}
</style>
