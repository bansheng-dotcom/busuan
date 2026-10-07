<template>
  <div class="pick">
    <p class="hint">
      {{ display('點選 1～2 個喜用字組名；再點可取消。', false) }}
      <button type="button" class="text-link" @click="handleGotoBook">
        {{ display('納音出處', false) }}
      </button>
    </p>

    <div class="preview">
      <span class="label">{{ display('預覽', false) }}</span>
      <strong>{{ display(preview, false) || display('（請選字）', false) }}</strong>
      <button v-if="picked.length" type="button" class="clear" @click="handleClear">
        {{ display('清空', false) }}
      </button>
    </div>

    <section v-for="group in groups" :key="group.key" class="group">
      <h3>{{ display(group.title, false) }}</h3>
      <div class="chars">
        <button
          v-for="ch in group.chars"
          :key="ch.char"
          type="button"
          class="char-btn"
          :class="{ on: isPicked(ch.char) }"
          :title="display(`${ch.note}｜${ch.source}`, false)"
          @click="handleToggle(ch)"
        >
          <b>{{ display(ch.char, false) }}</b>
          <small>{{ display(ch.note, false) }}</small>
        </button>
      </div>
    </section>
  </div>
</template>

<script lang="ts">
import { computed, defineComponent, ref, watch, type PropType } from 'vue';
import { useRouter } from 'vue-router';
import { useDisplayText } from '@/composables/useDisplayText';
import { useNamingSessionStore } from '@/store/namingSession';
import {
  NAME_CHARS,
  type NameChar,
  type NamingAnalysis,
} from '@/utils/naming';

export default defineComponent({
  name: 'NamingPick',
  props: {
    analysis: {
      type: Object as PropType<NamingAnalysis>,
      required: true,
    },
    surname: {
      type: String,
      default: '',
    },
  },
  setup(props) {
    const { display } = useDisplayText();
    const router = useRouter();
    const session = useNamingSessionStore();
    const picked = ref<NameChar[]>([]);

    const groups = computed(() => {
      const { primary, secondary } = props.analysis.preferred;
      const primaryChars = NAME_CHARS.filter((c) => c.wuxing === primary);
      const secondaryChars =
        secondary === primary
          ? []
          : NAME_CHARS.filter((c) => c.wuxing === secondary);
      const list = [
        {
          key: 'primary',
          title: `主喜用 · ${primary}`,
          chars: primaryChars,
        },
      ];
      if (secondaryChars.length) {
        list.push({
          key: 'secondary',
          title: `次喜用 · ${secondary}`,
          chars: secondaryChars,
        });
      }
      return list;
    });

    const preview = computed(() => {
      const given = picked.value.map((c) => c.char).join('');
      if (!given) return '';
      return `${(props.surname || '').trim()}${given}`;
    });

    watch(
      () => props.analysis.dayNayin.ganZhi,
      () => {
        picked.value = [];
      },
    );

    const isPicked = (char: string) => picked.value.some((c) => c.char === char);

    const handleToggle = (ch: NameChar) => {
      const idx = picked.value.findIndex((c) => c.char === ch.char);
      if (idx >= 0) {
        picked.value = picked.value.filter((_, i) => i !== idx);
        return;
      }
      if (picked.value.length >= 2) {
        picked.value = [picked.value[1], ch];
        return;
      }
      picked.value = [...picked.value, ch];
    };

    const handleClear = () => {
      picked.value = [];
    };

    const handleGotoBook = () => {
      session.markFromNaming();
      void router.push({ path: '/book', query: { from: 'naming' }, hash: '#huajia-nayin' });
    };

    return {
      display,
      picked,
      groups,
      preview,
      isPicked,
      handleToggle,
      handleClear,
      handleGotoBook,
    };
  },
});
</script>

<style scoped>
.pick {
  margin-top: 0.5rem;
}
.hint {
  font-size: 0.85rem;
  color: var(--zw-ink-muted);
  margin: 0 0 0.75rem;
}
.hint .text-link {
  margin-left: 0.5rem;
  padding: 0;
  border: none;
  background: none;
  color: var(--zw-primary);
  text-decoration: underline;
  font: inherit;
  cursor: pointer;
}
.preview {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  flex-wrap: wrap;
  padding: 0.75rem 0.9rem;
  margin-bottom: 1rem;
  border-radius: 10px;
  border: 1px solid var(--zw-gold);
  background: color-mix(in srgb, var(--zw-gold) 10%, var(--zw-paper));
}
.preview .label {
  font-size: 0.8rem;
  color: var(--zw-ink-muted);
}
.preview strong {
  font-size: 1.35rem;
  letter-spacing: 0.15em;
  color: var(--zw-gold);
}
.clear {
  margin-left: auto;
  padding: 0.25rem 0.6rem;
  border: 1px solid var(--zw-line);
  border-radius: 6px;
  background: transparent;
  cursor: pointer;
  color: var(--zw-ink);
}
.group h3 {
  margin: 0.5rem 0 0.45rem;
  font-size: 0.95rem;
}
.chars {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(92px, 1fr));
  gap: 0.45rem;
}
.char-btn {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.2rem;
  padding: 0.5rem 0.35rem;
  border: 1px solid var(--zw-line);
  border-radius: 8px;
  background: var(--zw-paper);
  color: var(--zw-ink);
  cursor: pointer;
  text-align: center;
}
.char-btn b {
  font-size: 1.25rem;
}
.char-btn small {
  font-size: 0.65rem;
  color: var(--zw-ink-muted);
  line-height: 1.3;
  max-height: 2.6em;
  overflow: hidden;
}
.char-btn.on {
  border-color: var(--zw-gold);
  background: color-mix(in srgb, var(--zw-gold) 18%, transparent);
  box-shadow: 0 0 0 1px var(--zw-gold);
}
</style>
