<template>
  <div
    ref="rootRef"
    class="disk"
    :class="{ interactive }"
    role="img"
    :aria-label="display('研習地盤羅盤', false)"
    @pointerdown="onPointerDown"
    @pointermove="onPointerMove"
    @pointerup="onPointerUp"
    @pointercancel="onPointerUp"
  >
    <svg class="plate" viewBox="0 0 480 480" :style="{ transform: `rotate(${-heading}deg)` }">
      <circle cx="240" cy="240" r="238" fill="var(--zw-paper)" stroke="var(--zw-gold)" />
      <circle cx="240" cy="240" r="192" fill="none" stroke="var(--zw-line)" />
      <circle cx="240" cy="240" r="168" fill="none" stroke="var(--zw-gold)" />
      <circle cx="240" cy="240" r="124" fill="none" stroke="var(--zw-line)" />
      <circle cx="240" cy="240" r="70" fill="none" stroke="var(--zw-gold)" />
      <g v-for="tick in 72" :key="tick">
        <line
          :x1="240"
          :y1="tickLen(tick).y1"
          :x2="240"
          :y2="tickLen(tick).y2"
          stroke="var(--zw-ink)"
          :stroke-width="tick % 18 === 0 ? 1.5 : tick % 3 === 0 ? 1.1 : 0.6"
          :transform="`rotate(${tick * 5} 240 240)`"
        />
      </g>
      <text
        v-for="deg in [0, 90, 180, 270]"
        :key="`d-${deg}`"
        x="240"
        y="38"
        text-anchor="middle"
        fill="var(--zw-muted)"
        font-size="11"
        :transform="`rotate(${deg} 240 240)`"
      >
        {{ deg }}
      </text>
      <text
        v-for="item in mountains"
        :key="item.name"
        x="240"
        y="58"
        text-anchor="middle"
        :fill="item.yinYang === 'yang' ? '#b42318' : 'var(--zw-ink)'"
        :font-size="item.deg % 90 === 0 ? 16 : 13"
        :font-weight="item.deg % 90 === 0 ? 700 : 600"
        :transform="`rotate(${item.deg} 240 240)`"
      >
        {{ display(item.name, false) }}
      </text>
      <g v-for="item in houTian" :key="`h-${item.name}`" :transform="`rotate(${item.deg} 240 240)`">
        <text x="240" y="86" text-anchor="middle" fill="var(--zw-primary)" font-size="12" font-weight="600">
          {{ display(item.name, false) }}
        </text>
        <g v-for="(yao, idx) in yaoDrawn(item.yaos)" :key="idx">
          <rect v-if="yao === 1" x="229" :y="94 + idx * 8" width="22" height="5" fill="var(--zw-primary)" />
          <template v-else>
            <rect x="229" :y="94 + idx * 8" width="9" height="5" fill="var(--zw-primary)" />
            <rect x="242" :y="94 + idx * 8" width="9" height="5" fill="var(--zw-primary)" />
          </template>
        </g>
      </g>
      <g v-for="item in xianTian" :key="`x-${item.name}`" :transform="`rotate(${item.deg} 240 240)`">
        <text x="240" y="140" text-anchor="middle" fill="var(--zw-gold)" font-size="11" font-weight="600">
          {{ display(item.name, false) }}
        </text>
        <g v-for="(yao, idx) in yaoDrawn(item.yaos)" :key="idx">
          <rect v-if="yao === 1" x="230" :y="147 + idx * 7" width="20" height="4" fill="var(--zw-gold)" />
          <template v-else>
            <rect x="230" :y="147 + idx * 7" width="8" height="4" fill="var(--zw-gold)" />
            <rect x="242" :y="147 + idx * 7" width="8" height="4" fill="var(--zw-gold)" />
          </template>
        </g>
      </g>
      <text
        v-for="item in houTian"
        :key="`l-${item.name}`"
        x="240"
        y="186"
        text-anchor="middle"
        fill="var(--zw-ink)"
        font-size="13"
        font-weight="600"
        :transform="`rotate(${item.deg} 240 240)`"
      >
        {{ display(LUOSHU_HAN[item.luoshu], false) }}
      </text>
      <text x="240" y="20" text-anchor="middle" fill="#b42318" font-size="11" font-weight="700">N</text>
      <circle
        cx="240"
        cy="240"
        r="46"
        fill="color-mix(in srgb, var(--zw-paper) 70%, var(--zw-gold))"
        stroke="var(--zw-gold)"
      />
    </svg>
    <span class="cross" aria-hidden="true" />
    <span class="needle" aria-hidden="true" />
  </div>
</template>

<script lang="ts">
import { defineComponent, ref, watch } from 'vue';
import { HOU_TIAN, LUOSHU_HAN, MOUNTAINS, XIAN_TIAN, normalizeDeg, yaoDrawn } from '@/utils/luopan';
import { useDisplayText } from '@/composables/useDisplayText';

export default defineComponent({
  name: 'LuopanDisk',
  props: {
    heading: { type: Number, required: true },
    /** 為 true 時才攔截手勢撥盤；關閉時頁面可正常滾動 */
    interactive: { type: Boolean, default: false },
  },
  emits: {
    dragstart: () => true,
    drag: (_deg: number) => true,
  },
  setup(props, { emit }) {
    const { display } = useDisplayText();
    const rootRef = ref<HTMLElement | null>(null);
    let dragging = false;
    let pointerId: number | null = null;
    let originAngle = 0;
    let originHeading = 0;

    const endDrag = () => {
      const el = rootRef.value;
      if (dragging && el && pointerId !== null) {
        try {
          el.releasePointerCapture(pointerId);
        } catch {
          /* ignore */
        }
      }
      dragging = false;
      pointerId = null;
    };

    watch(
      () => props.interactive,
      (on) => {
        if (!on) endDrag();
      },
    );

    const _inner = {
      tickLen(tick: number) {
        if (tick % 18 === 0) return { y1: 8, y2: 26 };
        if (tick % 3 === 0) return { y1: 12, y2: 24 };
        return { y1: 16, y2: 22 };
      },
      insideDisk(event: PointerEvent) {
        const el = rootRef.value;
        if (!el) return false;
        const box = el.getBoundingClientRect();
        const cx = box.left + box.width / 2;
        const cy = box.top + box.height / 2;
        const r = Math.min(box.width, box.height) / 2;
        return Math.hypot(event.clientX - cx, event.clientY - cy) <= r;
      },
      pointerAngle(event: PointerEvent) {
        const el = rootRef.value;
        if (!el) return 0;
        const box = el.getBoundingClientRect();
        const dx = event.clientX - (box.left + box.width / 2);
        const dy = event.clientY - (box.top + box.height / 2);
        return normalizeDeg((Math.atan2(dx, -dy) * 180) / Math.PI);
      },
      onPointerDown(event: PointerEvent) {
        if (!props.interactive) return;
        if (event.pointerType === 'mouse' && event.button !== 0) return;
        if (!_inner.insideDisk(event)) return;
        const el = rootRef.value;
        if (!el) return;
        dragging = true;
        pointerId = event.pointerId;
        try {
          el.setPointerCapture(event.pointerId);
        } catch {
          /* ignore */
        }
        originAngle = _inner.pointerAngle(event);
        originHeading = props.heading;
        emit('dragstart');
      },
      onPointerMove(event: PointerEvent) {
        if (!props.interactive || !dragging) return;
        if (pointerId !== null && event.pointerId !== pointerId) return;
        event.preventDefault();
        const delta = _inner.pointerAngle(event) - originAngle;
        emit('drag', normalizeDeg(originHeading - delta));
      },
      onPointerUp(event: PointerEvent) {
        if (pointerId !== null && event.pointerId !== pointerId) return;
        endDrag();
      },
    };

    return {
      display,
      rootRef,
      mountains: MOUNTAINS,
      houTian: HOU_TIAN,
      xianTian: XIAN_TIAN,
      LUOSHU_HAN,
      yaoDrawn,
      ..._inner,
    };
  },
});
</script>

<style scoped>
.disk {
  position: relative;
  width: 100%;
  max-width: 460px;
  aspect-ratio: 1;
  margin: 0 auto;
  border-radius: 50%;
  /* 默認不攔截：手指從盤上滑過也能滾頁 */
  touch-action: auto;
  pointer-events: none;
  user-select: none;
  box-sizing: border-box;
  filter: drop-shadow(0 8px 18px rgba(44, 36, 22, 0.12));
}
.disk.interactive {
  pointer-events: auto;
  touch-action: none;
  cursor: grab;
}
.disk.interactive:active {
  cursor: grabbing;
}
.plate {
  width: 100%;
  height: 100%;
  transform-origin: 50% 50%;
  will-change: transform;
}
.cross,
.needle {
  position: absolute;
  left: 50%;
  top: 50%;
  pointer-events: none;
}
.cross {
  width: 20%;
  height: 20%;
  margin: -10% 0 0 -10%;
  border: 1px solid rgba(180, 35, 24, 0.55);
  border-radius: 50%;
}
.cross::before,
.cross::after {
  content: '';
  position: absolute;
  background: rgba(180, 35, 24, 0.7);
}
.cross::before {
  left: 50%;
  top: 8%;
  bottom: 8%;
  width: 1px;
  margin-left: -0.5px;
}
.cross::after {
  top: 50%;
  left: 8%;
  right: 8%;
  height: 1px;
  margin-top: -0.5px;
}
.needle {
  width: 0;
  height: 0;
  margin: -48% 0 0 -7px;
  border-left: 7px solid transparent;
  border-right: 7px solid transparent;
  border-bottom: 16px solid #b42318;
}
</style>
