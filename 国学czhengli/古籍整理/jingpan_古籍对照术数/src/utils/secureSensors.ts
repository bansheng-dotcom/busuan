/** 運動／方向感應在瀏覽器中的可用性（與 HTTPS 安全上下文有關） */
export type SensorAccess = 'ok' | 'need-https' | 'unsupported';

export function deviceMotionAccess(): SensorAccess {
  if (typeof window === 'undefined') return 'unsupported';
  if (!window.isSecureContext) return 'need-https';
  if (typeof DeviceMotionEvent === 'undefined') return 'unsupported';
  return 'ok';
}

export function deviceOrientationAccess(): SensorAccess {
  if (typeof window === 'undefined') return 'unsupported';
  if (!window.isSecureContext) return 'need-https';
  if (typeof DeviceOrientationEvent === 'undefined') return 'unsupported';
  return 'ok';
}
