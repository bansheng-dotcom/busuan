import { defineStore } from 'pinia';

/** 搖卦 → 易經往返：標記來源，配合 keep-alive 保留爻象；硬刷新清空 */
export const useYaoguaSessionStore = defineStore('yaoguaSession', () => {
  let fromYaogua = false;

  function markFromYaogua() {
    fromYaogua = true;
  }

  function clearFromYaogua() {
    fromYaogua = false;
  }

  function isFromYaogua() {
    return fromYaogua;
  }

  return {
    markFromYaogua,
    clearFromYaogua,
    isFromYaogua,
  };
});
