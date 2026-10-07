<template>
  <div class="sheet-select">
    <SheetField :text="displayText" :placeholder="placeholder" @click="open = true" />
    <BottomSheet
      v-model="open"
      :title="title"
      show-cancel-footer
      :cancel-text="cancelText"
      @cancel="open = false"
    >
      <ul class="option-list">
        <li
          v-for="opt in options"
          :key="String(opt.value)"
          class="option"
          :class="{ active: opt.value === modelValue }"
          @click="handlePick(opt.value)"
        >
          <span>{{ opt.label }}</span>
          <i v-if="opt.value === modelValue" class="check" aria-hidden="true" />
        </li>
      </ul>
    </BottomSheet>
  </div>
</template>

<script lang="ts">
import { computed, defineComponent, nextTick, ref, type PropType } from 'vue';
import BottomSheet from './BottomSheet.vue';
import SheetField from './SheetField.vue';

export interface SheetSelectOption {
  label: string;
  value: string | number;
}

export default defineComponent({
  name: 'SheetSelect',
  components: { BottomSheet, SheetField },
  props: {
    modelValue: { type: [String, Number] as PropType<string | number | null>, default: null },
    options: { type: Array as PropType<SheetSelectOption[]>, required: true },
    title: { type: String, default: '' },
    placeholder: { type: String, default: '請選擇' },
    cancelText: { type: String, default: '取消' },
  },
  emits: {
    'update:modelValue': (_v: string | number) => true,
    change: (_v: string | number) => true,
  },
  setup(props, { emit }) {
    const open = ref(false);
    const displayText = computed(() => {
      const hit = props.options.find((o) => o.value === props.modelValue);
      return hit?.label ?? '';
    });

    /** 先关弹层解锁 body，再通知父级，避免 scrollIntoView 在 position:fixed 锁页时算错位置 */
    const handlePick = async (val: string | number) => {
      open.value = false;
      await nextTick();
      emit('update:modelValue', val);
      emit('change', val);
    };

    return { open, displayText, handlePick };
  },
});
</script>

<style scoped>
.sheet-select {
  width: 100%;
}
.option-list {
  list-style: none;
  margin: 0;
  padding: 4px 0 8px;
  max-height: min(50vh, 360px);
  overflow-y: auto;
  -webkit-overflow-scrolling: touch;
  scrollbar-width: none;
}
.option-list::-webkit-scrollbar {
  display: none;
}
.option {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  padding: 14px 18px;
  font-size: 15px;
  letter-spacing: 0.06em;
  color: var(--zw-ink);
  border-bottom: 1px solid var(--zw-line);
}
.option:last-child {
  border-bottom: 0;
}
.option.active {
  color: var(--zw-primary);
  font-weight: 600;
}
.check {
  width: 8px;
  height: 14px;
  border-right: 2px solid var(--zw-primary);
  border-bottom: 2px solid var(--zw-primary);
  transform: rotate(45deg);
  margin-top: -4px;
}
</style>
