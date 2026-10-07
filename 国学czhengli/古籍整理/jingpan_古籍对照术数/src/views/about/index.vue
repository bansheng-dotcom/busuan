<template>
  <div class="page-container">
    <article class="classic-prose max-w-3xl rounded-lg border p-6" :style="cardStyle">
      <h1 class="mb-4 text-2xl font-semibold">{{ display('關於', false) }}</h1>
      <h2 class="mb-2 font-semibold">{{ display('資料來源說明', false) }}</h2>
      <p class="mb-4">
        {{
          display(
            '經盤是古籍對照的術數研習站。斗數所據《紫微斗數全書》卷一至卷三正文，統一取國學典籍網公開頁，僅做切章與簡轉繁，不校改、不補寫、不附現代白話斷語。',
            false,
          )
        }}
      </p>
      <ul class="mb-4 source-list">
        <li>
          <a href="http://ab.newdu.com/book/ms261794.html" target="_blank" rel="noopener">卷一 · 國學典籍網</a>
        </li>
        <li>
          <a href="http://ab.newdu.com/book/ms261795.html" target="_blank" rel="noopener">卷二 · 國學典籍網</a>
        </li>
        <li>
          <a href="http://ab.newdu.com/book/ms261796.html" target="_blank" rel="noopener">卷三 · 國學典籍網</a>
        </li>
        <li>
          <a href="https://www.nihaixiahope.com/yijing.html" target="_blank" rel="noopener">易經64卦 · 斷易天機（倪海廈天紀公開頁）</a>
        </li>
        <li>
          <a href="https://www.nihaixiahope.com/liurenfa/" target="_blank" rel="noopener">六壬法 · 倪海廈天紀公開頁</a>
        </li>
      </ul>
      <h2 class="mb-2 font-semibold">{{ display('技術說明', false) }}</h2>
      <p class="mb-4">
        {{
          display(
            '排盤使用公開曆法安星算法（iztro）。真太陽時依出生地經度與均時差校正鐘錶時刻後再入盤。廟旺落陷標記隨安星結果展示，格局與命盤摘句只輸出卷一對應原始歌訣或定義原文。卷二、卷三供站內閱讀。易經六十四卦取自倪海廈天紀《斷易天機》公開網頁整理（非全書原文）。六壬法依倪海廈天紀公開頁算法作農曆月日時六宮推算（本地計算，無 AI 解卦）。搖卦頁採三錢法本地隨機起六爻，成卦後自站內易經條目節選卦體講解原文並鏈接全文，不另行編寫吉凶斷語。羅盤為研習地盤（廿四山、先後天、洛書），手機可讀方向感應器，不作風水斷事；老黃曆曆注取自 lunar-typescript。起名頁依日柱納音生扶取喜用，用字為站內精選研習表（非全書原文），可跳轉卷二納音歌核對。網站不生成 AI 解讀。',
            false,
          )
        }}
      </p>
      <h2 class="mb-2 font-semibold">{{ display('聯繫', false) }}</h2>
      <p class="mb-2">
        {{ display('網站內容若有錯漏，歡迎斧正。', false) }}
      </p>
      <p class="mb-4 contact-wechat">
        {{ display('微信', false) }}
        <span class="wechat-id">2653586693</span>
      </p>
      <h2 class="mb-2 font-semibold">{{ display('免責聲明', false) }}</h2>
      <p>{{ display(DISCLAIMER_TEXT, false) }}</p>
    </article>
  </div>
</template>

<script lang="ts">
import { defineComponent } from 'vue';
import { DISCLAIMER_TEXT } from '@/utils/disclaimer';
import { useDisplayText } from '@/composables/useDisplayText';

export default defineComponent({
  name: 'AboutPage',
  setup() {
    const { display } = useDisplayText();
    const cardStyle = {
      background: 'var(--zw-paper)',
      borderColor: 'var(--zw-line)',
    };
    return { display, DISCLAIMER_TEXT, cardStyle };
  },
});
</script>

<style scoped>
.source-list {
  padding-left: 1.25rem;
  margin-bottom: 1rem;
  line-height: 1.8;
}
.source-list a {
  color: var(--zw-primary);
  text-decoration: underline;
  word-break: break-all;
}
.contact-wechat {
  letter-spacing: 0.08em;
}
.wechat-id {
  margin-left: 0.5em;
  color: var(--zw-primary);
  font-variant-numeric: tabular-nums;
  letter-spacing: 0.06em;
}
</style>
