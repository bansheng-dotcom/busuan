<template>
  <div class="page-container luopan-page">
    <h1>{{ display('羅盤', false) }}</h1>
    <p class="lead">
      {{
        display(
          '研習地盤·廿四山陰陽、後天先天對照、洛書九數。紅標為當前朝向，N 隨子山指向磁北。天池可對準校準與微調。',
          false,
        )
      }}
    </p>
    <div class="dial-bar">
      <button
        type="button"
        class="start"
        :class="{ on: dialOn }"
        @click="dialOn = !dialOn"
      >
        {{ display(dialOn ? '撥盤中 · 點此結束' : '開啟撥盤', false) }}
      </button>
      <p class="gesture-hint">
        {{
          display(
            dialOn
              ? '已開啟：在盤上拖動可調方位。要滾動頁面請先點「結束」。'
              : '默認可直接滑動頁面。需要手動擰盤時，點「開啟撥盤」。',
            false,
          )
        }}
      </p>
    </div>
    <LuopanDisk
      :heading="heading"
      :interactive="dialOn"
      @dragstart="handleDragStart"
      @drag="handleDrag"
    />
    <div class="readout">
      <strong>{{ headingText }}°</strong>
      <span>{{ display(current.dir, false) }}</span>
      <span>{{ display(mainLine, false) }}</span>
      <span class="sub">{{ display(guaLine, false) }}</span>
      <span v-if="calibrated" class="calib-tag">
        {{ display(`已校準 · 偏差 ${offsetLabel}`, false) }}
      </span>
    </div>

    <section class="tianchi" aria-label="天池校準">
      <h2>{{ display('天池校準', false) }}</h2>
      <p class="tianchi-lead">
        {{
          display(
            '對準已知方位後點校準；再用 ± 或滑條微調。偏差僅修手機磁偏／干擾，刷新後清空，不能替代實物羅盤。',
            false,
          )
        }}
      </p>
      <div class="tianchi-row">
        <label class="lab" for="calib-mountain">{{ display('對準目標', false) }}</label>
        <SheetSelect
          v-if="isMobile"
          id="calib-mountain"
          v-model="targetDeg"
          class="mountain-select"
          :options="mountainOptions"
          :title="display('對準目標', false)"
          :cancel-text="display('取消', false)"
        />
        <select v-else id="calib-mountain" v-model="targetDeg" class="mountain-select">
          <option v-for="m in mountains" :key="m.name" :value="m.deg">
            {{ display(`${m.name}山 · ${m.dir} · ${String(m.deg).padStart(3, '0')}°`, false) }}
          </option>
        </select>
      </div>
      <div class="tianchi-actions">
        <button type="button" class="start" @click="handleCalibrate">
          {{ display('校準天池', false) }}
        </button>
        <button type="button" class="ghost" :disabled="!calibrated" @click="handleResetOffset">
          {{ display('重置校準', false) }}
        </button>
      </div>
      <div class="fine">
        <span class="lab">{{ display('微調偏差', false) }}</span>
        <div class="fine-btns">
          <button type="button" class="ghost sm" @click="handleNudge(-5)">−5°</button>
          <button type="button" class="ghost sm" @click="handleNudge(-1)">−1°</button>
          <button type="button" class="ghost sm" @click="handleNudge(1)">+1°</button>
          <button type="button" class="ghost sm" @click="handleNudge(5)">+5°</button>
        </div>
        <input
          class="slider"
          type="range"
          min="-30"
          max="30"
          step="1"
          :value="fineSlider"
          @input="handleFineSlider"
        />
        <span class="slider-hint">{{ display(`微調滑條 ±30° · 當前偏差 ${offsetLabel}`, false) }}</span>
      </div>
    </section>

    <div class="actions">
      <button
        v-if="!needHttps && (needsPermission || (isMobile && !live))"
        type="button"
        class="start"
        @click="handleStart"
      >
        {{ display(live ? '指南針已開啟' : '開啟指南針', false) }}
      </button>
      <button v-if="paused && supported" type="button" class="start" @click="handleFollow">
        {{ display('跟隨指南針', false) }}
      </button>
    </div>
    <p v-if="denied" class="warn">{{ display('未獲得方向感應權限，可在系統設定中允許，亦可撥盤對照。', false) }}</p>
    <p v-else-if="needHttps" class="warn">
      {{
        display(
          '指南針需 HTTPS 安全連線；當前為 HTTP，瀏覽器會攔截方向感應。可撥盤子山對照，或為站點配置 HTTPS。',
          false,
        )
      }}
    </p>
    <p v-else-if="!supported" class="hint">{{ display('此裝置沒有方向感應器，可撥盤子山對照。', false) }}</p>
    <p v-else-if="!live && !paused" class="hint">
      {{ display('手機請開啟指南針；電腦無磁感應，可撥盤作廿四山對照。', false) }}
    </p>
    <p class="hint">
      {{
        display(
          '電子羅盤受磁場干擾，不能替代實物羅盤實測。陰陽取三合地盤常例，先天後天僅方位對照。本頁不作風水斷事。',
          false,
        )
      }}
    </p>
  </div>
</template>

<script lang="ts">
import { computed, defineComponent, ref } from 'vue';
import { ElMessage } from 'element-plus';
import LuopanDisk from './components/LuopanDisk.vue';
import SheetSelect from '@/components/sheet/SheetSelect.vue';
import { useCompassHeading } from '@/composables/useCompassHeading';
import { useDisplayText } from '@/composables/useDisplayText';
import { useDevice } from '@/composables/useDevice';
import { houTianAt, LUOSHU_HAN, MOUNTAINS, mountainAt, xianTianAt } from '@/utils/luopan';

export default defineComponent({
  name: 'LuopanPage',
  components: { LuopanDisk, SheetSelect },
  setup() {
    const { display } = useDisplayText();
    const { isMobile } = useDevice();
    const {
      heading,
      live,
      paused,
      needsPermission,
      denied,
      supported,
      needHttps,
      offsetSigned,
      calibrated,
      requestStart,
      pause,
      resume,
      setHeading,
      calibrateTo,
      nudgeOffset,
      setOffsetSigned,
      resetOffset,
    } = useCompassHeading();

    const targetDeg = ref(0);
    const dialOn = ref(false);
    /** 滑條為相對「對準校準後基準」的 ±30 微調；基準用對準時寫入 */
    const fineBase = ref(0);
    const fineSlider = computed(() => {
      const d = offsetSigned.value - fineBase.value;
      return Math.max(-30, Math.min(30, Math.round(d)));
    });

    const mountainOptions = computed(() =>
      MOUNTAINS.map((m) => ({
        label: display(`${m.name}山 · ${m.dir} · ${String(m.deg).padStart(3, '0')}°`, false),
        value: m.deg,
      })),
    );

    const current = computed(() => mountainAt(heading.value));
    const hou = computed(() => houTianAt(heading.value));
    const xian = computed(() => xianTianAt(heading.value));
    const headingText = computed(() => heading.value.toFixed(0).padStart(3, '0'));
    const mainLine = computed(() => {
      const m = current.value;
      const yinYang = m.yinYang === 'yang' ? '陽山' : '陰山';
      return `${m.name}山 · ${yinYang} · ${hou.value.name}卦 · 洛書${LUOSHU_HAN[hou.value.luoshu]}`;
    });
    const guaLine = computed(() => `後天${hou.value.name} · 先天${xian.value.name}`);
    const offsetLabel = computed(() => {
      const s = offsetSigned.value;
      if (Math.abs(s) < 0.5) return '0°';
      return `${s > 0 ? '+' : ''}${s.toFixed(0)}°`;
    });

    const _methods = {
      handleStart() {
        resume();
        void requestStart();
      },
      handleDragStart() {
        pause();
      },
      handleDrag(deg: number) {
        if (!dialOn.value) return;
        setHeading(deg);
      },
      handleFollow() {
        resume();
        void requestStart();
      },
      handleCalibrate() {
        calibrateTo(targetDeg.value);
        fineBase.value = offsetSigned.value;
        const m = MOUNTAINS.find((x) => x.deg === targetDeg.value);
        ElMessage.success(
          display(
            m
              ? `天池已對準「${m.name}山 · ${m.dir}」`
              : `天池已對準 ${String(targetDeg.value).padStart(3, '0')}°`,
            false,
          ),
        );
      },
      handleResetOffset() {
        resetOffset();
        fineBase.value = 0;
        ElMessage.info(display('已重置天池校準', false));
      },
      handleFineSlider(e: Event) {
        const v = Number((e.target as HTMLInputElement).value);
        setOffsetSigned(fineBase.value + v);
      },
      handleNudge(delta: number) {
        nudgeOffset(delta);
        const d = offsetSigned.value - fineBase.value;
        if (d > 30) fineBase.value = offsetSigned.value - 30;
        if (d < -30) fineBase.value = offsetSigned.value + 30;
      },
    };
    return {
      display,
      heading,
      live,
      paused,
      needsPermission,
      denied,
      supported,
      needHttps,
      isMobile,
      current,
      headingText,
      mainLine,
      guaLine,
      mountains: MOUNTAINS,
      mountainOptions,
      targetDeg,
      dialOn,
      calibrated,
      offsetLabel,
      fineSlider,
      ..._methods,
    };
  },
});
</script>

<style scoped>
.luopan-page {
  text-align: center;
  max-width: 720px;
  width: 100%;
  overflow-x: hidden;
  box-sizing: border-box;
}
h1 {
  margin: 0 0 8px;
  letter-spacing: 0.28em;
  font-size: 28px;
}
.lead,
.hint,
.warn,
.tianchi-lead {
  color: var(--zw-muted);
  font-size: 13px;
  line-height: 1.7;
  letter-spacing: 0.06em;
  overflow-wrap: anywhere;
}
.warn {
  color: #b42318;
}
.readout {
  display: flex;
  flex-direction: column;
  gap: 4px;
  margin: 18px 0 12px;
  letter-spacing: 0.12em;
  padding: 0 4px;
  overflow-wrap: anywhere;
}
.readout strong {
  font-size: 40px;
  color: var(--zw-primary);
  letter-spacing: 0.08em;
  font-variant-numeric: tabular-nums;
}
.readout .sub {
  font-size: 13px;
  color: var(--zw-gold);
  letter-spacing: 0.12em;
}
.calib-tag {
  margin-top: 6px;
  font-size: 12px;
  color: var(--zw-primary);
  letter-spacing: 0.14em;
}
.gesture-hint {
  margin: 8px 0 0;
  font-size: 12px;
  color: var(--zw-muted);
  letter-spacing: 0.08em;
  line-height: 1.5;
}
.dial-bar {
  margin: 0 auto 12px;
  max-width: 420px;
}
.dial-bar .start.on {
  background: color-mix(in srgb, var(--zw-primary) 18%, var(--zw-paper));
  border-color: var(--zw-primary);
  color: var(--zw-primary);
}
.tianchi {
  margin: 8px auto 18px;
  padding: 14px 14px 16px;
  max-width: 420px;
  text-align: left;
  border: 1px solid var(--zw-line);
  border-radius: 14px;
  background: color-mix(in srgb, var(--zw-paper) 88%, var(--zw-gold));
  box-sizing: border-box;
}
.tianchi h2 {
  margin: 0 0 6px;
  font-size: 15px;
  letter-spacing: 0.22em;
  text-align: center;
  color: var(--zw-primary);
}
.tianchi-lead {
  margin: 0 0 12px;
  text-align: center;
}
.tianchi-row {
  display: flex;
  flex-direction: column;
  gap: 6px;
  margin-bottom: 10px;
}
.lab {
  font-size: 12px;
  letter-spacing: 0.14em;
  color: var(--zw-muted);
}
.mountain-select {
  width: 100%;
  padding: 8px 10px;
  border: 1px solid var(--zw-line);
  border-radius: 10px;
  background: var(--zw-paper);
  color: var(--zw-ink);
  font-family: inherit;
  font-size: 14px;
  letter-spacing: 0.06em;
}
.tianchi-actions {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  justify-content: center;
  margin-bottom: 12px;
}
.fine {
  display: flex;
  flex-direction: column;
  gap: 8px;
  align-items: stretch;
}
.fine-btns {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
  justify-content: center;
}
.slider {
  width: 100%;
  accent-color: var(--zw-primary);
}
.slider-hint {
  text-align: center;
  font-size: 11px;
  color: var(--zw-muted);
  letter-spacing: 0.08em;
}
.start,
.ghost {
  border: 1px solid var(--zw-gold);
  background: color-mix(in srgb, var(--zw-paper) 70%, var(--zw-gold));
  color: var(--zw-ink);
  padding: 10px 22px;
  border-radius: 999px;
  font-family: inherit;
  letter-spacing: 0.16em;
  cursor: pointer;
}
.ghost {
  background: transparent;
  border-color: var(--zw-line);
}
.ghost:disabled {
  opacity: 0.45;
  cursor: not-allowed;
}
.ghost.sm {
  padding: 6px 12px;
  letter-spacing: 0.08em;
  font-size: 13px;
  min-width: 3.2rem;
}
.actions {
  display: flex;
  justify-content: center;
  gap: 10px;
  flex-wrap: wrap;
  margin-bottom: 12px;
}
</style>
