import { computed, onMounted, onUnmounted, ref } from 'vue';
import { lerpHeading, normalizeDeg, signedDeg } from '@/utils/luopan';
import { deviceOrientationAccess } from '@/utils/secureSensors';

type DeviceOrientationCtor = typeof DeviceOrientationEvent & {
  requestPermission?: () => Promise<PermissionState>;
};

interface CompassOrientationEvent extends DeviceOrientationEvent {
  webkitCompassHeading?: number;
}

function readHeading(event: CompassOrientationEvent): number | null {
  if (typeof event.webkitCompassHeading === 'number' && !Number.isNaN(event.webkitCompassHeading)) {
    return normalizeDeg(event.webkitCompassHeading);
  }
  if (event.absolute && typeof event.alpha === 'number') {
    return normalizeDeg(360 - event.alpha);
  }
  if (typeof event.alpha === 'number') {
    return normalizeDeg(360 - event.alpha);
  }
  return null;
}

export function useCompassHeading() {
  const heading = ref(0);
  const live = ref(false);
  const paused = ref(false);
  const needsPermission = ref(false);
  const denied = ref(false);
  const supported = ref(false);
  /** HTTP 等非安全上下文：瀏覽器禁止方向感應 */
  const needHttps = ref(false);
  /** 天池偏差：顯示角 = normalize(傳感器 − offset) */
  const offsetDeg = ref(0);

  let sensorRaw = 0;
  let raf = 0;

  const calibrated = computed(() => Math.abs(signedDeg(offsetDeg.value)) >= 0.5);
  const offsetSigned = computed(() => signedDeg(offsetDeg.value));

  const correctedTarget = () => normalizeDeg(sensorRaw - offsetDeg.value);

  const onOrient = (event: Event) => {
    const next = readHeading(event as CompassOrientationEvent);
    if (next === null) return;
    sensorRaw = next;
    live.value = true;
  };

  const tick = () => {
    if (!paused.value && live.value) {
      heading.value = lerpHeading(heading.value, correctedTarget(), 0.18);
    }
    raf = window.requestAnimationFrame(tick);
  };

  const pause = () => {
    paused.value = true;
  };

  const resume = () => {
    paused.value = false;
  };

  /** 撥盤：直接設顯示角，不改傳感器與偏差 */
  const setHeading = (deg: number) => {
    heading.value = normalizeDeg(deg);
  };

  /** 當前「等效傳感器」角（撥盤時由顯示角反推） */
  const apparentSensor = () => {
    if (paused.value || !live.value) {
      return normalizeDeg(heading.value + offsetDeg.value);
    }
    return sensorRaw;
  };

  /** 對準目標山：使當前朝向讀成 targetDeg */
  const calibrateTo = (targetDeg: number) => {
    const target = normalizeDeg(targetDeg);
    offsetDeg.value = normalizeDeg(apparentSensor() - target);
    heading.value = target;
  };

  const nudgeOffset = (delta: number) => {
    const sensor = apparentSensor();
    offsetDeg.value = normalizeDeg(offsetDeg.value + delta);
    if (paused.value || !live.value) {
      heading.value = normalizeDeg(sensor - offsetDeg.value);
    }
  };

  const setOffsetSigned = (signed: number) => {
    const sensor = apparentSensor();
    offsetDeg.value = normalizeDeg(signed);
    if (paused.value || !live.value) {
      heading.value = normalizeDeg(sensor - offsetDeg.value);
    }
  };

  const resetOffset = () => {
    const sensor = apparentSensor();
    offsetDeg.value = 0;
    if (paused.value || !live.value) {
      heading.value = normalizeDeg(sensor);
    }
  };

  const bind = () => {
    window.addEventListener('deviceorientationabsolute', onOrient, true);
    window.addEventListener('deviceorientation', onOrient, true);
  };

  const unbind = () => {
    window.removeEventListener('deviceorientationabsolute', onOrient, true);
    window.removeEventListener('deviceorientation', onOrient, true);
  };

  const requestStart = async () => {
    denied.value = false;
    const access = deviceOrientationAccess();
    if (access === 'need-https') {
      needHttps.value = true;
      supported.value = false;
      return;
    }
    needHttps.value = false;
    const Ctor = window.DeviceOrientationEvent as DeviceOrientationCtor | undefined;
    if (!Ctor) {
      supported.value = false;
      return;
    }
    supported.value = true;
    if (typeof Ctor.requestPermission === 'function') {
      try {
        const state = await Ctor.requestPermission();
        if (state !== 'granted') {
          denied.value = true;
          needsPermission.value = true;
          return;
        }
        needsPermission.value = false;
      } catch {
        denied.value = true;
        needsPermission.value = true;
        return;
      }
    }
    bind();
  };

  onMounted(() => {
    const access = deviceOrientationAccess();
    if (access === 'need-https') {
      needHttps.value = true;
      supported.value = false;
      needsPermission.value = false;
    } else {
      needHttps.value = false;
      const Ctor = window.DeviceOrientationEvent as DeviceOrientationCtor | undefined;
      supported.value = Boolean(Ctor);
      needsPermission.value = Boolean(Ctor && typeof Ctor.requestPermission === 'function');
      if (Ctor && typeof Ctor.requestPermission !== 'function') {
        bind();
      }
    }
    raf = window.requestAnimationFrame(tick);
  });

  onUnmounted(() => {
    unbind();
    window.cancelAnimationFrame(raf);
  });

  return {
    heading,
    live,
    paused,
    needsPermission,
    denied,
    supported,
    needHttps,
    offsetDeg,
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
  };
}
