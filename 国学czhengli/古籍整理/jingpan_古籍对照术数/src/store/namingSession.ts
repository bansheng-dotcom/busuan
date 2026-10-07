import { defineStore } from 'pinia';

/** 起名 → 古籍往返：标记来源，配合 keep-alive 保留结果；硬刷新清空 */
export const useNamingSessionStore = defineStore('namingSession', () => {
  let fromNaming = false;

  function markFromNaming() {
    fromNaming = true;
  }

  function clearFromNaming() {
    fromNaming = false;
  }

  function isFromNaming() {
    return fromNaming;
  }

  return {
    markFromNaming,
    clearFromNaming,
    isFromNaming,
  };
});
