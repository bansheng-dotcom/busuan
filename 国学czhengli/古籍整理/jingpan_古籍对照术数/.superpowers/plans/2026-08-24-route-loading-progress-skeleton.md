# 路由加载反馈实现计划

> **For agent:** 按步骤顺序执行；每步完成后打勾。规格见 `.superpowers/specs/2026-08-24-route-loading-progress-skeleton-design.md`。

**目标：** 点击懒加载路由时立刻显示 2px 朱砂顶栏进度条 + 分型骨架（list/detail/tool），组件就绪后收起；keep-alive 命中与仅 hash/query 变化不闪骨架。

**技术要点：** 不新增依赖；`defineComponent` Options-style；`RouteMeta.skeleton`；模块级 `useRouteLoading`；`App.vue` 内 `Suspense` + 现有 `keep-alive`。

---

## 任务清单

- [ ] Step 1：`useRouteLoading` 单例 composable
- [ ] Step 2：`RouteProgressBar.vue`
- [ ] Step 3：`RouteSkeleton.vue`（三型）
- [ ] Step 4：路由 `meta.skeleton` + before/afterEach / onError
- [ ] Step 5：改 `App.vue` 挂载进度条与 Suspense
- [ ] Step 6：本地验收（冷路由 / keep-alive / 连点 / 双主题）

---

## Step 1：`useRouteLoading`

**文件：** 新建 `src/composables/useRouteLoading.ts`

**内容要求：**

```ts
export type SkeletonType = 'list' | 'detail' | 'tool';

// 模块级共享状态（单例）
const isLoading = ref(false);
const skeletonType = ref<SkeletonType>('list');
const progress = ref(0); // 0–100
// 可选：phase 'idle' | 'running' | 'finishing' 便于进度条收尾

function start(type: SkeletonType = 'list'): void
function done(): void
function fail(): void
```

**行为：**

- `start`：设 `isLoading=true`、写入 `skeletonType`、`progress` 从 0 起；若已有爬升 timer 先清再开。用 `requestAnimationFrame` 或 `setInterval` 缓动爬到约 80（勿到 100）。
- `done`：进度冲到 100 → 约 150–200ms 后 `isLoading=false`、`progress=0`、清 timer。可用递增 `token`/`generation`，避免旧 `done` 关掉新导航的 loading。
- `fail`：立刻清 timer，`isLoading=false`、`progress=0`（不冲到 100）。
- `useRouteLoading()` 返回上述 refs（只读或 toRefs）与三个方法。

**验证：** `npx vue-tsc --noEmit` 无该文件相关报错（可与后续步骤一起跑）。

---

## Step 2：`RouteProgressBar`

**文件：** 新建 `src/components/RouteProgressBar.vue`

**结构：**

- `defineComponent` + `name: 'RouteProgressBar'`
- `setup` 中 `useRouteLoading()`，取 `isLoading`、`progress`
- template：`v-show`/`v-if` 在加载或收尾时显示；一根 `div`，`width: progress%`，`height: 2px`，`background: var(--zw-primary)`，`position: fixed; top: 0; left: 0; z-index` 高于 header（查现有 `.site-header` z-index，取更大值，如 9999）
- `aria-hidden="true"`
- `transition`：opacity 淡出；width 可用 CSS transition 让视觉更顺

**验证：** 临时在 App 里挂上，控制台改 `start('list')` / `done()` 能看见条（或等 Step 5 一起验）。

---

## Step 3：`RouteSkeleton`

**文件：** 新建 `src/components/RouteSkeleton.vue`

**props：** `type: { type: String as PropType<SkeletonType>, default: 'list' }`

**三型布局（可用 Tailwind 或 scoped + CSS 变量）：**

| type | 占位 |
|------|------|
| `list` | 短标题条 + 2×2（或更多）卡片块 |
| `detail` | 标题条 + 大块 + 3～4 行横条 |
| `tool` | 标题 + 3 条表单高横条 + 下方大结果区 |

**样式：**

- 块背景：宣纸用半透明深色/灰（如 `color-mix` 或 `var(--zw-line)` 低透明）；夜空用浅色半透明。优先跟现有 `--zw-*` 变量，勿新造色板。
- 根节点 `aria-hidden="true"`，`pointer-events: none`
- 外层加与页面类似的水平 padding（对齐 `main` 内容宽）

**验证：** 三型切换视觉符合规格 mock。

---

## Step 4：路由 meta 与钩子

**文件：** 修改 `src/router/index.ts`

### 4.1 扩展 Meta

```ts
skeleton?: 'list' | 'detail' | 'tool';
```

### 4.2 每条路由写死 meta.skeleton

按规格表：

- list：`home`、`book`、`yijing`、`star-dict`、`pattern-dict`、`about`
- detail：`yijing-detail`、`star-dict-detail`
- tool：`chart`、`luopan`、`almanac`、`naming`、`liuren`、`yaogua`

### 4.3 keep-alive 跳过逻辑

与 `App.vue` 的 `include` 保持一致：

```ts
const KEEP_ALIVE_NAMES = new Set(['ChartPage', 'NamingPage', 'YijingPage', 'YaoguaPage']);
```

注意：`include` 用的是**组件 name**，不是 route name。路由 name → 组件 name 映射：

| route name | component name（需与页面 `name` 一致） |
|------------|----------------------------------------|
| chart | ChartPage |
| naming | NamingPage |
| yijing | YijingPage |
| yaogua | YaoguaPage |

维护 `visitedKeepAlive = new Set<string>()`（存组件 name）。`afterEach` 若目标在 KEEP_ALIVE 则 `add`。

`beforeEach`：

1. 若 `to.path === from.path` → 不 `start`（仅 query/hash）
2. 若目标组件名在 `KEEP_ALIVE_NAMES` 且已在 `visitedKeepAlive` → 不 `start`
3. 否则 `start(to.meta.skeleton ?? 'list')`

`afterEach`：若本次曾 start（可用模块 flag 或 `isLoading`）则 `done()`；并更新 visited。

更稳妥：`beforeEach` 返回前设 `shouldTrack = true/false`；`afterEach` 仅当 `shouldTrack` 时 `done()`，否则不动。

`router.onError(() => fail())`。

**验证：** 读路由表，每条都有 `skeleton`；钩子无类型错误。

---

## Step 5：改 `App.vue`

**文件：** 修改 `src/App.vue`

**目标结构：**

```vue
<template>
  <div class="app-shell ...">
    <RouteProgressBar />
    <AppHeader />
    <main class="flex-1">
      <router-view v-slot="{ Component }">
        <Suspense>
          <keep-alive include="ChartPage,NamingPage,YijingPage,YaoguaPage">
            <component :is="Component" />
          </keep-alive>
          <template #fallback>
            <RouteSkeleton :type="skeletonType" />
          </template>
        </Suspense>
      </router-view>
    </main>
    <AppFooter />
    <BackToTop />
  </div>
</template>
```

**注意：**

- `Suspense` 包住异步路由组件；fallback 在懒加载未完成时显示。
- `skeletonType` 来自 `useRouteLoading()`。
- 注册 `RouteProgressBar`、`RouteSkeleton`。
- 若 keep-alive 在 Suspense 外导致缓存行为异常，按 Vue 文档微调顺序，以「懒加载时能出 fallback、缓存页不闪」为准。

**验证：** `npm run dev` 点击未访问过的「关于」等页，应先见进度条+骨架再出内容。

---

## Step 6：验收清单

在浏览器手动过一遍：

1. **冷路由：** 硬刷新后点「关于」→ 立刻进度条 + list 骨架 → 真页面 → 条消失。
2. **detail：** 从易经列表进某卦 → detail 骨架。
3. **tool：** 首次进「罗盘」→ tool 骨架。
4. **keep-alive：** 进排盘一次后再离开再回来 → 无骨架闪烁（可有极短进度条或无）。
5. **连点：** 快速点多个导航 → 最终页正确，进度条不卡住。
6. **主题：** 宣纸 / 夜空切换后重复 1，条与骨架都清晰。
7. **类型检查：** `npx vue-tsc --noEmit` 通过。

---

## 风险与回退

| 风险 | 处理 |
|------|------|
| Suspense + keep-alive 顺序导致 fallback 不出现 | 调换包裹顺序；必要时用 `v-if="isLoading"` 在 main 上强制盖一层骨架（与 Suspense 双保险，优先 Suspense） |
| 假进度 timer 泄漏 | `done`/`fail`/`onUnmounted`（若组件内有）清 timer；generation token |
| 组件 name 与 include 不一致 | 打开各页确认 `name` 字段 |

---

## 完成定义

- 规格中验收标准 1–5 全部满足
- 无新增 npm 依赖
- `vue-tsc` 无新增错误
- 未改无关文件
