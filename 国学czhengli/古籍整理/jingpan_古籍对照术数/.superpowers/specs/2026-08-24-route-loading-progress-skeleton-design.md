# 路由跳转：顶部进度条 + 分型骨架屏

日期：2026-08-24  
状态：已批准（对话确认）

## 背景

站点路由均为懒加载（`() => import(...)`）。点击导航后，异步 chunk 下载完成前主内容区可能长时间空白或停留旧页，体感「半天才跳过去」。需要在点击瞬间给出明确加载反馈。

## 目标

1. 点击未缓存路由后，约 100ms 内出现顶部进度条，且 `main` 区显示对应类型骨架屏。
2. 异步路由组件就绪后，进度条收尾淡出，骨架替换为真实页面，无残留叠加。
3. 进度条为极细（约 2px）朱砂色假进度；骨架分 `list` / `detail` / `tool` 三型。
4. Header、Footer 保持不动；宣纸 / 夜空两套主题下均可辨识。

## 非目标

- 不覆盖页面内部接口请求的 loading（仍由各页自行处理）。
- 不做真实网络下载百分比。
- 不为每个业务页单独画骨架（不做 per-page）。
- 不引入 nprogress 等第三方进度库。

## 方案选定

自研顶栏进度 + Vue `<Suspense>` 骨架兜底（方案 1）：

- `router.beforeEach` 立刻 `start`
- `App.vue` 用 Suspense，fallback 渲染分型骨架
- `afterEach` / 导航错误时 `done` / `fail`

## 触发时机

| 时机 | 行为 |
|------|------|
| 点击瞬间（beforeEach） | 进度条开始；目标页非 keep-alive 命中时，主区换对应骨架 |
| 异步组件就绪（Suspense resolve + afterEach） | 进度条冲到 100% 后淡出；显示真实页面 |
| keep-alive 缓存命中 | 不显示骨架；进度条极短闪过或跳过，避免闪烁 |
| 同路由仅 hash / query 变化 | 不触发加载态 |
| 导航取消或出错 | 立刻关闭进度条与骨架状态 |

当前 keep-alive 页面（`ChartPage`、`NamingPage`、`YijingPage`、`YaoguaPage`）：从缓存返回时按上表「命中」处理。

## 骨架类型与路由映射

在 `RouteMeta` 增加：

```ts
skeleton?: 'list' | 'detail' | 'tool'
```

| 类型 | 轮廓 | 路由 |
|------|------|------|
| `list` | 标题条 + 卡片栅格 | `/`、`/book`、`/yijing`、`/star-dict`、`/pattern-dict`、`/about` |
| `detail` | 标题 + 大块 + 多行正文 | `/yijing/:id`、`/star-dict/:name` |
| `tool` | 标题 + 表单行 + 结果区 | `/chart`、`/luopan`、`/almanac`、`/naming`、`/liuren`、`/yaogua` |

每条路由在 `router/index.ts` 的 `meta.skeleton` 中显式标注；缺省时 fallback 用 `list`。

## 组件与文件

```
src/
  composables/useRouteLoading.ts
  components/RouteProgressBar.vue
  components/RouteSkeleton.vue
  App.vue                          # 挂进度条 + Suspense
  router/index.ts                  # meta.skeleton + 钩子
```

### `useRouteLoading`

- 状态：`isLoading`、`skeletonType`、进度百分比（或阶段：idle / running / finishing）
- API：`start(type)`、`done()`、`fail()`
- 连点多次导航：只保留最后一次；被取消的导航调用 `fail`，避免进度条卡住
- 模块级单例（composable 内共享 ref），供 router 钩子与组件共用

### `RouteProgressBar`

- 固定在视口最顶（`position: fixed; top: 0; z-index` 高于 header）
- 高度约 2px，朱砂系实色；假进度动画先到约 80%，`done` 时冲到 100% 再淡出
- `aria-hidden="true"`（装饰性；不抢焦点）

### `RouteSkeleton`

- props：`type: 'list' | 'detail' | 'tool'`
- 宣纸主题：浅灰占位块；夜空主题：半透明浅色块
- 使用 Element Plus `el-skeleton` 或等价 Tailwind 占位均可，风格与站点留白一致
- 不抢焦点、不作为可交互区域

### `App.vue` 结构（概念）

```
RouteProgressBar
AppHeader
main
  router-view + Suspense
    default: keep-alive → Component
    fallback: RouteSkeleton(:type="skeletonType")
AppFooter
BackToTop
```

## 进度条动画规则

1. `start`：从 0 显示，CSS/定时器缓动爬升至约 80%，不封顶到 100%。
2. `done`：快速到 100%，短延迟后透明度淡出并重置。
3. `fail`：立即淡出并重置，不冲到 100%。
4. 极短导航（如缓存命中若仍 start）：`done` 时最短展示时长约 120–200ms，或直接跳过 start（实现时二选一，优先「缓存命中跳过 start」）。

## 主题

- 进度条颜色：使用现有主题强调色（朱砂/品牌红），两主题共用，保证对比度。
- 骨架块：随 `isDark` 切换深浅；不引入新色板体系。

## 边界情况

- 连点导航：后一次覆盖前一次 loading 状态。
- keep-alive / hash·query：见「触发时机」。
- 暗色主题下骨架与进度条均须可见。
- 不处理页内数据请求 loading。

## 验收标准

1. 冷启动后首次进入任意未访问过的懒加载路由：点击后很快看到进度条 + 对应类型骨架。
2. 页面出现后进度条消失，骨架不叠在真内容上。
3. 在 keep-alive 页之间往返：无明显骨架闪烁。
4. 宣纸 / 夜空主题切换后，进度条与骨架仍清晰。
5. 快速连续点击多个导航：最终停在目标页，进度条不永久卡住。

## 实现备注

- 不新增 npm 依赖。
- 遵循项目现有 `defineComponent` + Options-style setup 习惯。
- TypeScript：扩展 `vue-router` 的 `RouteMeta`，禁止 `any`。
