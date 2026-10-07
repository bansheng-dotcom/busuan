<template>
  <button type="button" class="sheet-field" :class="{ placeholder: !text }" @click="$emit('click')">
    <span class="text">{{ text || placeholder }}</span>
    <span class="arrow" aria-hidden="true" />
  </button>
</template>

<script lang="ts">
import { defineComponent } from 'vue';

export default defineComponent({
  name: 'SheetField',
  props: {
    text: { type: String, default: '' },
    placeholder: { type: String, default: '請選擇' },
  },
  emits: {
    click: () => true,
  },
});
</script>

<style scoped>
.sheet-field {
  display: flex;
  align-items: center;
  width: 100%;
  min-height: 36px;
  padding: 8px 12px;
  border: 1px solid var(--el-border-color, var(--zw-line));
  border-radius: 4px;
  background: var(--el-fill-color-blank, #fff);
  color: var(--zw-ink);
  font-family: inherit;
  font-size: 14px;
  text-align: left;
  box-sizing: border-box;
}
html.theme-nightsky .sheet-field,
html.dark .sheet-field {
  background: var(--zw-paper);
}
.sheet-field.placeholder .text {
  color: var(--zw-muted);
}
.text {
  flex: 1;
  min-width: 0;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  letter-spacing: 0.04em;
}
.arrow {
  flex-shrink: 0;
  width: 7px;
  height: 7px;
  margin-left: 8px;
  border-right: 1.5px solid var(--zw-muted);
  border-bottom: 1.5px solid var(--zw-muted);
  transform: rotate(45deg);
  opacity: 0.7;
}
</style>
