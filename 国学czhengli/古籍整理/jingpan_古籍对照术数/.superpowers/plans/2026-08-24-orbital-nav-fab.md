# 环绕导航浮球实现计划

> **For agent:** 按步骤执行。规格：`.superpowers/specs/2026-08-24-orbital-nav-fab-design.md`

**目标：** 右下角新增可拖动「盤」浮球；点击后全站导航子项单圈环绕甩出；与「頂」独立。

---

## 任务清单

- [ ] Step 1：展平导航工具函数（可选，放 `siteNav.ts`）
- [ ] Step 2：实现 `OrbitalNavFab.vue`（拖动 + 展开/动画 + 跳转）
- [ ] Step 3：`App.vue` 挂载
- [ ] Step 4：本地验收（拖、展开、跳转、双主题）

---

## Step 1：展平导航

**文件：** `src/data/siteNav.ts`

新增：

```ts
export interface OrbitalNavItem {
  path: string;
  label: string;
  tag: string;
}

export function flattenOrbitalNav(): OrbitalNavItem[]
```

规则：遍历 `SITE_NAV`；有 `path` 则加入（tag 缺省用 label 首字）；有 `children` 则展开。顺序与规格表一致。

**验证：** 导出长度约为 12，含 `/` 与 `/about`。

---

## Step 2：`OrbitalNavFab.vue`

**文件：** 新建 `src/components/OrbitalNavFab.vue`

**结构要点：**

- `teleport` → `body`
- 遮罩 `v-show="open"`：fixed 全屏，半透明，点击 `close`
- 容器 fixed，位置由 `left/top`（与 BackToTop 同模式）
- 主球 button「盤」：pointerdown/move/up + click（moved 则忽略）
- 子项：`v-for`，绝对定位；展开时用 CSS 变量或 `:style` 设 `--tx/--ty` 与 `transition-delay`

**常量建议：**

- `SIZE = 44`，子球 `CHILD = 36`
- `RADIUS = 78`
- `POS_KEY = 'zw-orbital-nav-pos'`
- 默认：`clamp(innerWidth - 16 - SIZE, innerHeight - 24 - SIZE - 56)`（在「頂」默认上方约 56px）

**展开动画：**

- 关闭：`transform: translate(0,0) scale(0.4) rotate(-90deg); opacity:0`
- 打开：`translate(tx,ty) scale(1) rotate(0); opacity:1`，`tx = cos(θ)*R`，`ty = sin(θ)*R`
- `θ = startAngle + i * (2π/n)`，`startAngle` 约 `-Math.PI/2 - π/n`（略偏）
- delay：`i * 30ms`
- 拖动开始：`open = false`

**路由：**

- `useRouter().push(path)`；当前项 `isNavChildActive(path, route.path)` 加 class
- 跳转前 `open = false`

**样式：** 对齐 BackToTop 金边/宣纸；当前项朱砂或 primary 描边；`z-index` 遮罩 80、球 90。

**验证：** 单独挂到 App 能拖、能开合。

---

## Step 3：挂载

**文件：** `src/App.vue`

- import + components 注册
- template 在 `BackToTop` 旁加 `<OrbitalNavFab />`

**验证：** 两球同时出现，互不影响。

---

## Step 4：验收

1. 拖主球，刷新同会话位置还在  
2. 点击环绕甩出；遮罩/再点收起  
3. 点子项路由正确  
4. 拖动不误跳转  
5. 宣纸/夜空都清晰  

---

## 完成定义

- 规格验收 1–5 满足  
- 无新依赖；未改 `BackToTop.vue`  
- `vue-tsc` 无本功能相关新增错误  
