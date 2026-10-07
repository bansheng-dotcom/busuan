<template>
  <footer class="site-footer">
    <p>{{ display(DISCLAIMER_TEXT, false) }}</p>
  </footer>
</template>

<script lang="ts">
import { defineComponent } from 'vue';
import { DISCLAIMER_TEXT } from '@/utils/disclaimer';
import { useDisplayText } from '@/composables/useDisplayText';

export default defineComponent({
  name: 'AppFooter',
  setup() {
    const { display } = useDisplayText();
    return { DISCLAIMER_TEXT, display };
  },
});
</script>
