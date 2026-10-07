<template>
  <div class="chart-legend rounded-lg border p-3" :style="panelStyle">
    <h3 class="mb-2 text-sm font-semibold">{{ display('盤面標註', false) }}</h3>
    <ul class="legend-grid">
      <li>
        <span class="swatch major">{{ display('紫微', false) }}</span>
        <em>{{ display('十四主星，字色深紫加粗', false) }}</em>
      </li>
      <li>
        <span class="swatch minor">{{ display('左輔', false) }}</span>
        <em>{{ display('輔佐吉曜，字色金褐', false) }}</em>
      </li>
      <li>
        <span class="swatch sha">{{ display('擎羊', false) }}</span>
        <em>{{ display('羊陀火鈴空劫等煞，字色暗紅', false) }}</em>
      </li>
      <li>
        <span class="swatch">{{ display('天梁', false) }}<small class="miao">{{ display('廟', false) }}</small></span>
        <em>{{ display('廟旺得地，標註為褐金小字', false) }}</em>
      </li>
      <li>
        <span class="swatch">{{ display('太陽', false) }}<small class="xian">{{ display('陷', false) }}</small></span>
        <em>{{ display('落陷失地，標註為紅色小字', false) }}</em>
      </li>
      <li>
        <span class="swatch">{{ display('武曲', false) }}<i class="lu">{{ display('祿', false) }}</i></span>
        <em>{{ display('化祿，綠色角標', false) }}</em>
      </li>
      <li>
        <span class="swatch">{{ display('貪狼', false) }}<i class="quan">{{ display('權', false) }}</i></span>
        <em>{{ display('化權，紫色角標', false) }}</em>
      </li>
      <li>
        <span class="swatch">{{ display('天梁', false) }}<i class="ke">{{ display('科', false) }}</i></span>
        <em>{{ display('化科，藍色角標', false) }}</em>
      </li>
      <li>
        <span class="swatch">{{ display('文曲', false) }}<i class="ji">{{ display('忌', false) }}</i></span>
        <em>{{ display('化忌，紅色角標', false) }}</em>
      </li>
      <li>
        <span class="swatch ming">{{ display('命宮', false) }}</span>
        <em>{{ display('命宮金框內描', false) }}</em>
      </li>
      <li>
        <span class="swatch shen">{{ display('身宮', false) }}</span>
        <em>{{ display('身宮底色微染金', false) }}</em>
      </li>
      <li>
        <span class="swatch muted">5–14</span>
        <em>{{ display('宮內數字為大限起迄歲', false) }}</em>
      </li>
    </ul>
  </div>
</template>

<script lang="ts">
import { defineComponent } from 'vue';
import { useDisplayText } from '@/composables/useDisplayText';

export default defineComponent({
  name: 'ChartLegend',
  setup() {
    const { display } = useDisplayText();
    const panelStyle = {
      background: 'var(--zw-paper)',
      borderColor: 'var(--zw-line)',
    };
    return { display, panelStyle };
  },
});
</script>

<style scoped>
.legend-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(220px, 1fr));
  gap: 8px 16px;
  margin: 0;
  padding: 0;
  list-style: none;
}
.legend-grid li {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 12px;
}
.swatch {
  min-width: 64px;
  text-align: center;
  font-weight: 600;
}
.swatch.major { color: var(--zw-primary); font-weight: 700; }
.swatch.minor { color: var(--zw-gold); }
.swatch.sha { color: #8a2f2f; }
html.theme-nightsky .swatch.sha { color: #e07a7a; }
.swatch.ming {
  box-shadow: inset 0 0 0 2px var(--zw-gold);
  padding: 2px 6px;
  color: var(--zw-primary);
}
.swatch.shen {
  background: color-mix(in srgb, var(--zw-paper) 80%, var(--zw-gold));
  padding: 2px 6px;
  color: var(--zw-primary);
}
.swatch.muted { color: var(--zw-muted); font-weight: 400; }
.legend-grid em {
  font-style: normal;
  color: var(--zw-muted);
}
.miao { color: #7a5b12; font-size: 10px; margin-left: 2px; }
.xian { color: #8a2f2f; font-size: 10px; margin-left: 2px; }
i {
  font-style: normal;
  font-size: 10px;
  margin-left: 2px;
}
.lu { color: #2d6a4f; }
.quan { color: #3a2e5c; }
.ke { color: #1d4e89; }
.ji { color: #8a2f2f; }
</style>
