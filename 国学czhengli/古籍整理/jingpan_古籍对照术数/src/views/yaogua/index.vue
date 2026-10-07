<template>
  <div class="page-container yaogua-page">
    <h1>{{ display('搖卦', false) }}</h1>
    <p class="lead">
      {{
        display(
          '三錢起卦：自下而上共六爻。每次擲三錢得一爻；老陽、老陰為變爻。成卦後節選站內易經條目原文作大體講解，並可選用 AI 傾向解讀（不作絕對斷語）。',
          false,
        )
      }}
    </p>

    <section class="panel stage" :style="cardStyle">
      <div class="mode-row">
        <span>{{ display('一次成卦', false) }}</span>
        <el-switch v-model="quickMode" :disabled="shaking" @change="handleModeChange" />
        <em>{{
          display(
            quickMode ? '自錢筒逐枚灑下：先出為初爻（最下），依次向上成卦' : '傳統三錢，逐爻搖六次',
            false,
          )
        }}</em>
      </div>

      <p class="step">
        <template v-if="done">{{ display('六爻已成', false) }}</template>
        <template v-else-if="quickMode">{{ display('準備一次搖出六爻', false) }}</template>
        <template v-else>
          {{ display(`第 ${lines.length + 1} 爻 · 共六爻（初→上）`, false) }}
        </template>
      </p>

      <TossCoins
        :faces="displayCoins"
        :tossing="shaking"
        :toss-key="tossKey"
        :revealed="!quickMode || done || shaking"
        :pour-schedule="pourSchedule"
      />
      <p class="coin-legend">
        {{ display('陽面計 3、陰面計 2；三錢相加：6老陰 · 7少陽 · 8少陰 · 9老陽。', false) }}
      </p>

      <div class="actions">
        <el-button type="primary" :disabled="shaking || done" @click="handleShake">
          {{
            display(
              done ? '已成卦' : shaking ? '搖動中…' : quickMode ? '從筒中灑出成卦' : '搖一搖',
              false,
            )
          }}
        </el-button>
        <el-button :disabled="shaking" @click="handleReset">{{ display('重來', false) }}</el-button>
        <!-- HTTP 下運動感應不可用，暫隱藏手機搖動入口
        <el-button
          v-if="isMobile"
          :disabled="shaking || done || motionBlocked"
          @click="handleEnableMotion"
        >
          {{ display(motionOn ? '已啟用手機搖動' : '啟用手機搖動', false) }}
        </el-button>
        -->
      </div>
      <!--
      <p v-if="isMobile" class="hint" :class="{ warn: motionBlocked }">
        {{ display(motionHint, false) }}
      </p>
      -->
    </section>

    <section v-if="lines.length" class="panel" :style="cardStyle">
      <h2>{{ display('當前爻象', false) }}</h2>
      <HexagramLines :lines="lines" />
    </section>

    <section v-if="result" class="panel result" :style="cardStyle">
      <div class="gua-block">
        <div>
          <p class="eyebrow">{{ display('本卦', false) }}</p>
          <h2>{{ display(primaryName, false) }}</h2>
          <p class="meta">
            {{ display(`第 ${result.primaryIndex} 卦 · 上${primaryTrigrams.upper} · 下${primaryTrigrams.lower}`, false) }}
          </p>
          <HexagramLines :lines="result.lines" />
          <p v-if="primaryOverview" class="overview">{{ display(primaryOverview, false) }}</p>
          <p v-else class="overview muted">
            {{ display('本卦條目暫無可節選之卦體講解，請閱原文。', false) }}
          </p>
          <router-link
            class="link"
            :to="{ path: `/yijing/gua-${result.primaryIndex}`, query: { from: 'yaogua' } }"
            @click="markGotoYijing"
          >
            {{ display('查看易經原文', false) }}
          </router-link>
        </div>
        <div v-if="result.relatingIndex">
          <p class="eyebrow">{{ display('之卦', false) }}</p>
          <h2>{{ display(relatingName, false) }}</h2>
          <p class="meta">
            {{
              display(
                `第 ${result.relatingIndex} 卦 · 變爻：${changingLabels}`,
                false,
              )
            }}
          </p>
          <HexagramLines :lines="relatingLines" />
          <p v-if="relatingOverview" class="overview">{{ display(relatingOverview, false) }}</p>
          <p v-else class="overview muted">
            {{ display('之卦條目暫無可節選之卦體講解，請閱原文。', false) }}
          </p>
          <router-link
            class="link"
            :to="{ path: `/yijing/gua-${result.relatingIndex}`, query: { from: 'yaogua' } }"
            @click="markGotoYijing"
          >
            {{ display('查看易經原文', false) }}
          </router-link>
        </div>
        <p v-else class="note">{{ display('無變爻，僅得本卦。', false) }}</p>
      </div>
      <p class="overview-note">
        {{
          display(
            '以上講解摘自站內易經條目（倪海廈天紀《斷易天機》公開頁整理）原文節選，非臨時編寫；完整圖象與爻辭請點「查看易經原文」。',
            false,
          )
        }}
      </p>

      <div class="ai-panel">
        <h3>{{ display('AI 解讀', false) }}</h3>
        <p class="ai-hint">
          {{ display('請先填寫所問事項；AI 依本卦／之卦給傾向說明，僅供參考，不作唯一決策依據。', false) }}
        </p>
        <el-input
          v-model="aiQuestion"
          type="textarea"
          :rows="2"
          maxlength="120"
          show-word-limit
          :placeholder="display('請輸入所問事項', false)"
          :class="{ 'is-empty-hint': aiQuestionNeedHint }"
        />
        <p v-if="aiQuestionNeedHint" class="ai-field-hint">
          {{ display('請先填寫所問事項再生成。', false) }}
        </p>
        <div class="ai-actions">
          <el-button
            type="primary"
            :loading="aiLoading"
            :disabled="!aiConfigured || aiLoading"
            @click="handleAiGenerate"
          >
            {{ display('生成解讀', false) }}
          </el-button>
          <span class="ai-wait-hint">
            {{ display('生成較耗時（約一至兩分鐘），請稍候，勿切換或離開本頁。', false) }}
          </span>
        </div>
        <p v-if="aiLoading" class="ai-wait-hint is-loading">
          {{ display('正在生成中，請耐心等待，勿關閉或切換頁面…', false) }}
        </p>
        <p v-if="!aiConfigured" class="ai-hint">{{ display('AI 解讀服務尚未配置。', false) }}</p>
        <p v-if="aiError" class="ai-error">{{ aiError }}</p>
        <pre v-if="aiContent" class="ai-body">{{ display(aiContent, false) }}</pre>
      </div>
    </section>
  </div>
</template>

<script lang="ts">
import { computed, defineComponent, onUnmounted, ref, watch } from 'vue';
import { ElMessage } from 'element-plus';
import tocData from '@/data/yijingToc.json';
import hexData from '@/data/yijingHexagrams.json';
import { useDisplayText } from '@/composables/useDisplayText';
import { useDevice } from '@/composables/useDevice';
import { useYaoguaSessionStore } from '@/store/yaoguaSession';
import { fetchDivinationAi, isDivinationAiConfigured } from '@/api/divinationAi';
import { buildYaoguaAiPayload } from '@/utils/yaoguaAiPayload';
import { trigramsOf } from '@/utils/yijingTrigrams';
import { excerptHexagramOverview } from '@/utils/yijingExcerpt';
import {
  castFullHexagram,
  coinsToYao,
  createSixPourSchedule,
  finishCast,
  linesToDisplayFaces,
  tossThreeCoins,
  type CastResult,
  type CoinFace,
  type SixPourSchedule,
  type YaoLine,
} from '@/utils/yaogua';
import { deviceMotionAccess } from '@/utils/secureSensors';
import HexagramLines from './components/HexagramLines.vue';
import TossCoins from './components/TossCoins.vue';

const POS_LABEL = ['初', '二', '三', '四', '五', '上'];
const DEFAULT_THREE: CoinFace[] = [3, 2, 3];
const DEFAULT_SIX: CoinFace[] = [3, 2, 3, 3, 2, 3];

interface YijingHexEntry {
  id: string;
  index: number;
  name: string;
  blocks: { type: 'heading' | 'prose' | 'image'; text?: string }[];
}

export default defineComponent({
  name: 'YaoguaPage',
  components: { HexagramLines, TossCoins },
  setup() {
    const { display } = useDisplayText();
    const { isMobile } = useDevice();
    const yaoguaSession = useYaoguaSessionStore();
    const hexList = (hexData as { hexagrams: YijingHexEntry[] }).hexagrams;
    const hexByIndex = new Map(hexList.map((h) => [h.index, h]));
    const quickMode = ref(false);
    const lines = ref<YaoLine[]>([]);
    const shaking = ref(false);
    const tossKey = ref(0);
    const displayCoins = ref<CoinFace[]>([...DEFAULT_THREE]);
    const pourSchedule = ref<SixPourSchedule | null>(null);
    const result = ref<CastResult | null>(null);
    const motionOn = ref(false);
    const motionAccess = deviceMotionAccess();
    const motionBlocked = motionAccess !== 'ok';
    const aiConfigured = isDivinationAiConfigured();
    const aiQuestion = ref('');
    const aiQuestionNeedHint = ref(false);
    const aiLoading = ref(false);
    const aiError = ref('');
    const aiContent = ref('');
    watch(aiQuestion, (v) => {
      if (v.trim()) aiQuestionNeedHint.value = false;
    });
    const motionHint =
      motionAccess === 'need-https'
        ? '手機搖動需 HTTPS 安全連線；當前為 HTTP，瀏覽器會攔截運動感應。請用上方「搖一搖」按鈕起爻。'
        : motionAccess === 'unsupported'
          ? '此裝置或瀏覽器不提供運動感應，請用「搖一搖」按鈕起爻。'
          : '亦可真的晃動手機起爻（需授權運動感應）。';
    let lastShakeAt = 0;
    let lastMag = 9.8;

    const nameByIndex = (() => {
      const map = new Map<number, string>();
      for (const g of tocData.groups) {
        for (const item of g.items) map.set(item.index, item.name);
      }
      return map;
    })();

    const done = computed(() => lines.value.length >= 6);
    const primaryName = computed(() =>
      result.value ? nameByIndex.get(result.value.primaryIndex) ?? '' : '',
    );
    const relatingName = computed(() =>
      result.value?.relatingIndex ? nameByIndex.get(result.value.relatingIndex) ?? '' : '',
    );
    const primaryTrigrams = computed(() => trigramsOf(result.value?.primaryIndex ?? 0));
    const primaryOverview = computed(() => {
      if (!result.value) return null;
      const entry = hexByIndex.get(result.value.primaryIndex);
      return excerptHexagramOverview(entry?.blocks, entry?.name ?? primaryName.value);
    });
    const relatingOverview = computed(() => {
      if (!result.value?.relatingIndex) return null;
      const entry = hexByIndex.get(result.value.relatingIndex);
      return excerptHexagramOverview(entry?.blocks, entry?.name ?? relatingName.value);
    });
    const changingLabels = computed(() => {
      if (!result.value) return '';
      return result.value.changingPositions.map((p) => POS_LABEL[p]).join('、');
    });
    const relatingLines = computed((): YaoLine[] => {
      if (!result.value?.relatingIndex) return [];
      return result.value.lines.map((l) => {
        if (!l.changing) return { ...l, label: l.yang ? '少陽' : '少陰', changing: false };
        const yang = (l.yang ? 0 : 1) as 0 | 1;
        return {
          ...l,
          yang,
          changing: false,
          kind: yang ? 'youngYang' : 'youngYin',
          label: yang ? '少陽' : '少陰',
          sum: yang ? 7 : 8,
        };
      });
    });

    const cardStyle = {
      background: 'var(--zw-paper)',
      borderColor: 'var(--zw-line)',
    };

    const runToss = async () => {
      if (shaking.value || done.value) return;

      if (quickMode.value) {
        const full = castFullHexagram();
        displayCoins.value = linesToDisplayFaces(full);
        tossKey.value += 1;
        const schedule = createSixPourSchedule(tossKey.value + Date.now());
        pourSchedule.value = schedule;
        shaking.value = true;
        await new Promise((r) => setTimeout(r, schedule.totalMs));
        lines.value = full;
        result.value = finishCast(full);
        aiError.value = '';
        aiContent.value = '';
        shaking.value = false;
        ElMessage.success(display('六爻已成', false));
        return;
      }

      const coins = tossThreeCoins();
      displayCoins.value = coins;
      tossKey.value += 1;
      shaking.value = true;
      await new Promise((r) => setTimeout(r, 1350));

      const yao = coinsToYao(coins, lines.value.length);
      lines.value = [...lines.value, yao];
      shaking.value = false;

      if (lines.value.length >= 6) {
        result.value = finishCast(lines.value);
        aiError.value = '';
        aiContent.value = '';
        ElMessage.success(display('六爻已成', false));
      }
    };

    const markGotoYijing = () => {
      yaoguaSession.markFromYaogua();
    };

    const handleShake = () => {
      void runToss();
    };

    const handleReset = () => {
      lines.value = [];
      result.value = null;
      displayCoins.value = quickMode.value ? [...DEFAULT_SIX] : [...DEFAULT_THREE];
      pourSchedule.value = null;
      shaking.value = false;
      aiQuestion.value = '';
      aiQuestionNeedHint.value = false;
      aiError.value = '';
      aiContent.value = '';
    };

    const handleModeChange = () => {
      handleReset();
    };

    const handleAiGenerate = async () => {
      if (!result.value || aiLoading.value) return;
      if (!aiConfigured) {
        ElMessage.warning(display('AI 解讀服務尚未配置', false));
        return;
      }
      if (!aiQuestion.value.trim()) {
        aiQuestionNeedHint.value = true;
        ElMessage.warning({
          message: display('請先填寫所問事項', false),
          duration: 500,
        });
        return;
      }
      aiQuestionNeedHint.value = false;
      aiLoading.value = true;
      aiError.value = '';
      try {
        aiContent.value = await fetchDivinationAi(
          buildYaoguaAiPayload({
            result: result.value,
            primaryName: primaryName.value,
            relatingName: relatingName.value || undefined,
            primaryOverview: primaryOverview.value,
            relatingOverview: relatingOverview.value,
            question: aiQuestion.value,
          }),
        );
      } catch (err) {
        aiError.value = err instanceof Error ? err.message : display('生成失敗，請稍後重試', false);
      } finally {
        aiLoading.value = false;
      }
    };

    const onDeviceMotion = (e: DeviceMotionEvent) => {
      const a = e.accelerationIncludingGravity;
      if (!a || a.x == null || a.y == null || a.z == null) return;
      const now = Date.now();
      if (now - lastShakeAt < 1400) return;
      const mag = Math.hypot(a.x, a.y, a.z);
      const delta = Math.abs(mag - lastMag);
      lastMag = mag;
      if (delta < 12) return;
      lastShakeAt = now;
      void runToss();
    };

    const handleEnableMotion = async () => {
      const access = deviceMotionAccess();
      if (access === 'need-https') {
        ElMessage.warning(
          display(
            '手機搖動需在 HTTPS 下使用。當前為 HTTP（如用 IP 訪問），瀏覽器會禁止運動感應。請用「搖一搖」按鈕，或為站點配置 HTTPS。',
            false,
          ),
        );
        return;
      }
      if (access === 'unsupported') {
        ElMessage.warning(display('此裝置或瀏覽器不支持運動感應，請用「搖一搖」按鈕。', false));
        return;
      }
      try {
        const req = (
          DeviceMotionEvent as unknown as { requestPermission?: () => Promise<PermissionState> }
        ).requestPermission;
        if (typeof req === 'function') {
          const state = await req.call(DeviceMotionEvent);
          if (state !== 'granted') {
            ElMessage.warning(display('未獲得運動感應權限，請在系統／瀏覽器設定中允許。', false));
            return;
          }
        }
        if (!motionOn.value) {
          window.addEventListener('devicemotion', onDeviceMotion, { passive: true });
          motionOn.value = true;
          ElMessage.success(display('已啟用：晃動手機即可起爻', false));
        }
      } catch {
        ElMessage.warning(
          display('無法啟用運動感應（權限被拒或瀏覽器限制），請用「搖一搖」按鈕。', false),
        );
      }
    };

    onUnmounted(() => {
      window.removeEventListener('devicemotion', onDeviceMotion);
    });

    return {
      display,
      isMobile,
      cardStyle,
      lines,
      shaking,
      tossKey,
      displayCoins,
      pourSchedule,
      result,
      done,
      quickMode,
      motionOn,
      motionBlocked,
      motionHint,
      primaryName,
      relatingName,
      primaryTrigrams,
      primaryOverview,
      relatingOverview,
      changingLabels,
      relatingLines,
      aiConfigured,
      aiQuestion,
      aiQuestionNeedHint,
      aiLoading,
      aiError,
      aiContent,
      handleShake,
      handleReset,
      handleModeChange,
      handleAiGenerate,
      handleEnableMotion,
      markGotoYijing,
    };
  },
});
</script>

<style scoped>
.yaogua-page {
  padding-bottom: 2.5rem;
}
h1 {
  margin: 0 0 0.35rem;
  font-size: 1.55rem;
}
.lead {
  margin: 0 0 1.25rem;
  max-width: 40rem;
  line-height: 1.7;
  font-size: 0.9rem;
  color: var(--zw-muted);
}
.panel {
  padding: 1.1rem 1.15rem;
  margin-bottom: 1.15rem;
  border: 1px solid var(--zw-line);
  border-radius: 12px;
}
.panel h2 {
  margin: 0 0 0.75rem;
  font-size: 1rem;
  letter-spacing: 0.16em;
  color: var(--zw-primary);
}
.step {
  margin: 0 0 1rem;
  text-align: center;
  letter-spacing: 0.14em;
  color: var(--zw-muted);
  font-size: 0.9rem;
}
.mode-row {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 0.55rem 0.75rem;
  margin-bottom: 0.85rem;
  font-size: 0.88rem;
  letter-spacing: 0.08em;
  color: var(--zw-ink);
}
.mode-row em {
  flex: 1 1 12rem;
  font-style: normal;
  font-size: 0.78rem;
  color: var(--zw-muted);
  letter-spacing: 0.04em;
  line-height: 1.45;
}
.coin-legend {
  margin: -0.35rem 0 1rem;
  text-align: center;
  font-size: 0.78rem;
  line-height: 1.55;
  color: var(--zw-muted);
  letter-spacing: 0.04em;
}
.actions {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
  justify-content: center;
}
.hint {
  margin: 0.75rem 0 0;
  text-align: center;
  font-size: 0.78rem;
  color: var(--zw-muted);
  line-height: 1.55;
}
.hint.warn {
  color: #9a3412;
}
.gua-block {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
  gap: 1.25rem;
}
.eyebrow {
  margin: 0 0 0.25rem;
  font-size: 0.75rem;
  letter-spacing: 0.18em;
  color: var(--zw-gold);
}
.gua-block h2 {
  margin: 0 0 0.35rem;
  font-size: 1.35rem;
  letter-spacing: 0.12em;
}
.meta {
  margin: 0 0 0.85rem;
  font-size: 0.82rem;
  color: var(--zw-muted);
}
.overview {
  margin: 0.85rem 0 0.65rem;
  padding: 0.75rem 0.85rem;
  border-left: 3px solid color-mix(in srgb, var(--zw-gold) 70%, transparent);
  background: color-mix(in srgb, var(--zw-gold) 8%, transparent);
  font-size: 0.88rem;
  line-height: 1.75;
  letter-spacing: 0.04em;
  color: var(--zw-ink);
}
.overview.muted {
  border-left-color: var(--zw-line);
  background: transparent;
  color: var(--zw-muted);
}
.overview-note {
  margin: 1.1rem 0 0;
  font-size: 0.75rem;
  line-height: 1.55;
  color: var(--zw-muted);
  letter-spacing: 0.03em;
}
.ai-panel {
  margin-top: 1.15rem;
  padding-top: 1rem;
  border-top: 1px dashed var(--zw-line);
}
.ai-panel h3 {
  margin: 0 0 0.45rem;
  font-size: 0.95rem;
  letter-spacing: 0.14em;
  color: var(--zw-primary);
}
.ai-hint {
  margin: 0 0 0.65rem;
  font-size: 0.78rem;
  line-height: 1.55;
  color: var(--zw-muted);
}
.ai-field-hint {
  margin: 0.35rem 0 0;
  font-size: 0.68rem;
  line-height: 1.45;
  color: #8a2f2f;
  letter-spacing: 0.02em;
}
.ai-panel :deep(.is-empty-hint .el-textarea__inner) {
  border-color: color-mix(in srgb, #8a2f2f 55%, var(--zw-line));
}
.ai-actions {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 0.5rem 0.75rem;
  margin: 0.65rem 0 0.35rem;
}
.ai-wait-hint {
  margin: 0;
  flex: 1 1 10rem;
  font-size: 0.68rem;
  line-height: 1.55;
  color: color-mix(in srgb, var(--zw-muted) 78%, transparent);
  letter-spacing: 0.02em;
  opacity: 0.92;
}
.ai-wait-hint.is-loading {
  margin-top: 0.35rem;
  font-size: 0.72rem;
  color: color-mix(in srgb, var(--zw-primary) 70%, var(--zw-muted));
  opacity: 1;
}
.ai-error {
  margin: 0.5rem 0 0;
  font-size: 0.85rem;
  color: #8a2f2f;
  line-height: 1.5;
}
.ai-body {
  margin: 0.75rem 0 0;
  padding: 0.85rem 0.95rem;
  border-radius: 8px;
  border: 1px solid var(--zw-line);
  background: color-mix(in srgb, var(--zw-bg) 35%, var(--zw-paper));
  white-space: pre-wrap;
  word-break: break-word;
  font-family: inherit;
  font-size: 0.88rem;
  line-height: 1.75;
  color: var(--zw-ink);
}
.link {
  display: inline-block;
  margin-top: 0.85rem;
  color: var(--zw-primary);
  text-decoration: underline;
  letter-spacing: 0.08em;
  font-size: 0.88rem;
}
.note {
  margin: 0;
  color: var(--zw-muted);
  font-size: 0.88rem;
}
</style>
