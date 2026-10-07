/** 主导航：一级 + 可选二级。PC 下拉 / H5 分组共用。 */
export interface NavChild {
  path: string;
  label: string;
  tag?: string;
  desc?: string;
}

export interface NavItem {
  key: string;
  label: string;
  path?: string;
  tag?: string;
  desc?: string;
  children?: NavChild[];
}

export const SITE_NAV: NavItem[] = [
  { key: 'home', path: '/', label: '首頁', tag: '首', desc: '紫微斗數研習總覽' },
  { key: 'chart', path: '/chart', label: '排盤', tag: '盤', desc: '時辰安星·十二宮命盤' },
  {
    key: 'classics',
    label: '典籍',
    children: [
      { path: '/book', label: '古籍', tag: '卷', desc: '紫微斗數全書·卷一至三' },
      { path: '/yijing', label: '易經', tag: '易', desc: '斷易天機64卦' },
      { path: '/star-dict', label: '星曜', tag: '星', desc: '卷一諸星性質·廟旺問答' },
      { path: '/pattern-dict', label: '格局', tag: '格', desc: '卷一定格歌訣·原文對照' },
    ],
  },
  {
    key: 'tools',
    label: '工具',
    children: [
      { path: '/luopan', label: '羅盤', tag: '針', desc: '八卦廿四山' },
      { path: '/almanac', label: '黃曆', tag: '曆', desc: '農曆宜忌' },
      { path: '/naming', label: '起名', tag: '名', desc: '日柱納音·喜用取字' },
      { path: '/liuren', label: '六壬', tag: '壬', desc: '農曆月日時·六宮' },
      { path: '/yaogua', label: '搖卦', tag: '卦', desc: '三錢起卦·六爻' },
    ],
  },
  { key: 'about', path: '/about', label: '關於', tag: '註', desc: '資料來源·免責聲明' },
];

export function navDesc(path: string): string {
  for (const item of SITE_NAV) {
    if (item.path === path && item.desc) return item.desc;
    for (const child of item.children ?? []) {
      if (child.path === path && child.desc) return child.desc;
    }
  }
  return '';
}

export function isNavChildActive(path: string, routePath: string): boolean {
  if (path === '/') return routePath === '/';
  return routePath === path || routePath.startsWith(`${path}/`);
}

export function isNavGroupActive(item: NavItem, routePath: string): boolean {
  if (item.path) return isNavChildActive(item.path, routePath);
  return (item.children ?? []).some((c) => isNavChildActive(c.path, routePath));
}

/** 环绕浮球菜单：展平后的叶子项 */
export interface OrbitalNavItem {
  path: string;
  label: string;
  tag: string;
}

/** 将 SITE_NAV 展平为环绕菜单项（单字 tag） */
export function flattenOrbitalNav(): OrbitalNavItem[] {
  const items: OrbitalNavItem[] = [];
  for (const nav of SITE_NAV) {
    if (nav.path) {
      items.push({
        path: nav.path,
        label: nav.label,
        tag: nav.tag || nav.label.slice(0, 1),
      });
      continue;
    }
    for (const child of nav.children ?? []) {
      items.push({
        path: child.path,
        label: child.label,
        tag: child.tag || child.label.slice(0, 1),
      });
    }
  }
  return items;
}
