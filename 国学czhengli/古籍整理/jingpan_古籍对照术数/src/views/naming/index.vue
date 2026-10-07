<template>
  <div class="page-container naming-page">
    <header class="head">
      <h1>{{ display('納音起名', false) }}</h1>
      <p class="lead">
        {{
          display(
            '依出生年月日時（可選公曆或農曆），取日柱納音為本氣，按生扶定喜用五行，自精選字庫推薦用字。可跳轉卷二納音歌原文核對；不作吉凶斷語。',
            false,
          )
        }}
      </p>
    </header>

    <NamingForm @submit="handleSubmit" />
    <p v-if="trueSolarNote" class="true-solar-note">{{ trueSolarNote }}</p>

    <template v-if="analysis">
      <NamingSummary :analysis="analysis" />

      <div class="modes">
        <button
          type="button"
          :class="{ on: mode === 'recommend' }"
          @click="mode = 'recommend'"
        >
          {{ display('推薦名字', false) }}
        </button>
        <button type="button" :class="{ on: mode === 'pick' }" @click="mode = 'pick'">
          {{ display('自選組名', false) }}
        </button>
      </div>

      <NamingRecommend
        v-if="mode === 'recommend'"
        :analysis="analysis"
        :surname="surname"
      />
      <NamingPick v-else :analysis="analysis" :surname="surname" />
    </template>

    <p class="foot-note">
      {{
        display(
          '用字表為站內研習輔助（字義參康熙字典等公開字書），非《紫微斗數全書》篇章。僅供對照研習，不構成命名或命理諮詢。',
          false,
        )
      }}
    </p>
  </div>
</template>

<script lang="ts">
import { defineComponent, reactive, toRefs } from 'vue';
import { ElMessage } from 'element-plus';
import { useDisplayText } from '@/composables/useDisplayText';
import { analyzeBirth, type NamingAnalysis } from '@/utils/naming';
import NamingForm from './components/NamingForm.vue';
import NamingSummary from './components/NamingSummary.vue';
import NamingRecommend from './components/NamingRecommend.vue';
import NamingPick from './components/NamingPick.vue';

export default defineComponent({
  name: 'NamingPage',
  components: {
    NamingForm,
    NamingSummary,
    NamingRecommend,
    NamingPick,
  },
  setup() {
    const { display } = useDisplayText();
    const _data = reactive({
      analysis: null as NamingAnalysis | null,
      surname: '',
      mode: 'recommend' as 'recommend' | 'pick',
      trueSolarNote: '',
    });

    const handleSubmit = (payload: {
      iso: string;
      timeIndex: number;
      surname: string;
      gender: string;
      trueSolarNote: string;
    }) => {
      const result = analyzeBirth({
        iso: payload.iso,
        timeIndex: payload.timeIndex,
        surname: payload.surname,
      });
      if (!result) {
        ElMessage.warning(display('未能推得日柱納音，請檢查日期與時辰。', false));
        _data.analysis = null;
        _data.trueSolarNote = '';
        return;
      }
      _data.analysis = result;
      _data.surname = payload.surname;
      _data.trueSolarNote = payload.trueSolarNote || '';
      void payload.gender;
    };

    return {
      display,
      ...toRefs(_data),
      handleSubmit,
    };
  },
});
</script>

<style scoped>
.naming-page {
  padding-bottom: 2.5rem;
}
.head {
  margin-bottom: 1rem;
}
.head h1 {
  margin: 0 0 0.4rem;
  font-size: 1.55rem;
}
.lead {
  margin: 0;
  max-width: 42rem;
  line-height: 1.7;
  color: var(--zw-ink-muted);
  font-size: 0.92rem;
}
.true-solar-note {
  margin: 0.65rem 0 0;
  font-size: 0.82rem;
  line-height: 1.55;
  color: var(--zw-muted);
  letter-spacing: 0.04em;
}
.modes {
  display: flex;
  gap: 0.5rem;
  margin: 1rem 0 0.75rem;
}
.modes button {
  padding: 0.4rem 0.9rem;
  border: 1px solid var(--zw-line);
  border-radius: 999px;
  background: var(--zw-paper);
  color: var(--zw-ink);
  cursor: pointer;
}
.modes button.on {
  border-color: var(--zw-primary);
  background: var(--zw-primary);
  color: #fff;
}
.foot-note {
  margin-top: 1.75rem;
  font-size: 0.8rem;
  line-height: 1.65;
  color: var(--zw-ink-muted);
}
</style>
