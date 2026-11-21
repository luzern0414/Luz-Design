# 参考来源

核对日期 2026-11-09。检索与正文留存在本机 Luz-Crawl 输出目录，不入库。这里只记录读到了什么、权利边界、怎样采用；不把上游的指令升级成本技能的指令。优先级：用户当前要求，现有项目与平台约束，可核实的标准，本次任务推导，上游风格建议。

## 组件与动效参考

| 来源 | 读到的内容 | 许可与权利 | 采用 |
|---|---|---|---|
| [EasyUI](https://easyui.site/components) 及 GitHub 仓库 | 132 个组件，分类标签加卡片画廊，每项有实时演示与独立页；React、TypeScript、Tailwind、Framer Motion；经 shadcn 注册表分发 | MIT | 画廊版式、分类与搜索、组件清单；不复制代码，装饰特效不采用 |
| [Beautiful UI](https://www.beautifului.dev/) | 21 个智能体界面原语：思考、流式文字、审批卡、工具标签、任务行、对话、输入栏、记录与差异表等 | 页面标注 MIT | 智能体页的原语划分与交互 |
| [Transitions.dev](https://transitions.dev/) 及 GitHub 说明 | 43 个以上过渡；每项是带语义自定义属性、`t-` 命名空间和减少动态保护的 CSS 片段；有可重放预览 | 过渡与 skill 可用于个人和商业项目，不得把库本身作为竞争性过渡库再分发；其 CLI 与工具为 MIT | 只借鉴“变量化加可重放预览”的方法，配方自写 |
| Vercel AI Elements | 基于 shadcn 的智能体界面组件：对话、消息、推理、工具 | 仅读到社区资料，非官方文档 | 消息分块结构的参考 |
| [Vant](https://vant-ui.github.io/vant/)、Element Plus | 移动与桌面 Vue 组件库 | MIT | `frontend.py` 两个工程起点 |

## 导航与页面依据

| 来源 | 读到的内容 | 用在 |
|---|---|---|
| [Material Design 3 导航栏](https://m3.material.io/components/navigation-bar/guidelines) | 3 至 5 个目的地；每项有图标与文字；容器位于底部并占满窗口宽度；目的地位置固定；同页相关内容用标签，不同页面用导航 | 底栏项数与全宽、页内分段与主导航分层 |
| [微信小程序设计指南](https://developers.weixin.qq.com/miniprogram/design/) | 标签 2 至 5 个，建议不超过 4，一页一组标签；次级页面左上返回；局部加载反馈优先；成功提示约 1.5 秒，错误不用一闪而过的提示；异常状态要可控、有路可退 | 返回位置、加载与反馈方式、错误就近显示 |
| Apple 人机界面指南：标签栏、列表与表格 | 标签栏切换分区并保留各分区位置；列表与表格按信息选行样式 | 底栏与列表行 |
| [Baymard 订单概览与追踪](https://baymard.com/ecommerce-design-examples/62-orders-overview) 公开摘要 | 订单页服务多种意图：申请退货、回看订单、修改进行中的订单、下载发票；物流信息留在自家页面 | 订单页的状态分段、详情时间线、售后入口 |
| [WCAG 2.2 目标尺寸 2.5.8](https://www.w3.org/WAI/WCAG22/Understanding/target-size-minimum.html) | 指针目标最小 24×24 CSS px，含间距等例外 | 命中区域 |
| [MDN prefers-reduced-motion](https://developer.mozilla.org/en-US/docs/Web/CSS/Reference/At-rules/@media/prefers-reduced-motion) | 缩放与平移大面积元素可能引发前庭不适；应尊重减少动态设置 | 动效降级 |

## 前端配色与紧凑图标

于 2026-11-18 对照官方正文和例图。具体色值、24 像素图标外框及圆角档位是本技能样板的选择。

| 来源 | 采用方法 |
|---|---|
| [Atlassian 色彩](https://atlassian.design/foundations/color/) | 对照 Jira 看板实例，以中性表面平衡信息密度，用实色强调主要操作，点缀色与功能状态分别定义 |
| [Atlassian 图标](https://atlassian.design/foundations/iconography/) | 熟悉的轮廓在小尺寸下保持辨识，同组按视觉重量统一，使用已有图标 |
| [Atlassian 圆角](https://atlassian.design/foundations/radius/) · [Android 分段按钮](https://developer.android.com/develop/ui/compose/components/segmented-button) | 卡片和控件按层级选圆角，切换用边界与选中线索维持可辨识 |
| [WCAG 非文本对比](https://www.w3.org/WAI/WCAG22/Understanding/non-text-contrast.html) · [目标尺寸](https://www.w3.org/WAI/WCAG22/Understanding/target-size-minimum.html) | 用相邻颜色核对必要的非文本信息，将图标图形和实际可点击区域分别量测 |

## 移动视口与紧凑任务界面

| 原文 | 本技能采用的观察 |
|---|---|
| [WCAG 重排](https://www.w3.org/WAI/WCAG22/Understanding/reflow) · [文字放大](https://www.w3.org/WAI/WCAG22/Understanding/resize-text) | 主页面窄屏重排，放大文字仍可办理，必要二维内容局部滚动。 |
| [WebKit 安全区](https://webkit.org/blog/7929/designing-websites-for-iphone-x/) · [浏览器视口单位](https://web.dev/blog/viewport-units) · [Chrome 软键盘行为](https://developer.chrome.com/blog/viewport-resize-behavior) · [MDN 可见视口](https://developer.mozilla.org/en-US/docs/Web/API/VisualViewport) | 视口、安全区与键盘分别核验，测试覆盖实际目标浏览器。 |
| [Apple 工具栏](https://developer.apple.com/design/human-interface-guidelines/toolbars) · [Carbon 间距](https://www.carbondesignsystem.com/building-blocks/foundations/spacing/overview) | 用当前任务决定工具是否出现，相关信息靠近，用统一的间距尺度。 |
| [Atlassian 图标规范](https://atlassian.design/guidelines/product/foundations/iconography/) · [GOV.UK 按钮](https://design-system.service.gov.uk/components/button/) | 用可识别的轮廓、稳定的相对尺寸和清楚的主操作建立视觉层级。 |

白底、首屏构图和间距起点是本技能按用户要求确定的设计取值。

## 方法来源

以下方法以重述方式并入，不运行上游安装脚本、hooks 或自动改工程的指令；许可证原文在 `licenses/`。

| 来源与固定提交 | 并入的方法 | 不采纳 |
|---|---|---|
| nextlevelbuilder/ui-ux-pro-max-skill · 4f2dbb67e64969a9a30ab00742f2d55d66ddec2b · MIT | 识别用户、产品与栈；按问题查规则；主系统与页面差异协同 | 按行业套颜色风格，把数字目录当设计质量 |
| Dammyjay93/interface-design · 2f9be3206855bcb2d1d0af262c8bae25cba6658d · MIT | 领域内容决定方向；层级、密度与整页一致；成熟原语 | 把后台审美施加给营销页与海报 |
| Leonxlnx/taste-skill · f6b76575f949707b4e3c37cd86cb44b0b98643e8 · MIT | 真实内容与素材决定构图；跨宽度看图；可执行自审 | 固定字体禁令、风格旋钮、普遍大图 |
| pbakaus/impeccable · 924bbd194d02e5e15a227e75b5901fb0d7a4ecad · Apache-2.0 | 按操作、说服、阅读、体验分目的；先精简再打磨；维护与重设计分开 | 一次调用全部命令 |
| Nutlope/hallmark · 407fa689f4a276f2fd389208d271d0fef08f5058 · MIT | 盘点事实与素材；选整页形态；完整代表页先行 | 随机主题、字数与章节配额、禁紫色禁卡片禁阴影 |
| emilkowalski/skills · c8a79627b59d72d764d6ab6f2c87c09a48169833 · MIT | 先判断是否需要动画；目的与频率；可中断；触屏无悬停；减少动态 | 所有键盘动作永不动画等绝对推断 |

动效曲线、命中区域与色彩取值以 Carbon、Fluent、W3C、Radix 的具体说明校正，不把某一色相设为禁区；APCA 不替代 WCAG 对比度判定。

## 用户硬规则优先

[成品要求](hard-rules.md) 说明业务与交付核对项。前端、海报和演示的视觉建议分别见 [视觉基础](foundation.md)、[海报设计](poster.md) 与 [演示设计](slides.md)。

## 圆角、焦点与数据对齐

2026-11-19 核对。上游的形状与对齐原则用于本地样板。短字段共享居中内容区是 Luz-Design 的排版做法。

| 采用 | 来源 |
|---|---|
| 嵌套圆角按外半径减去内边距取初值，胶囊用于简短移动操作 | [Apple 的设计系统演示](https://developer.apple.com/videos/play/wwdc2025/356/?time=201) |
| 按钮有可感知的按下态，键盘焦点保持可见 | [Apple 的按钮指南](https://developer.apple.com/design/human-interface-guidelines/buttons)、[WCAG 焦点可见](https://www.w3.org/WAI/WCAG22/Understanding/focus-visible.html) |
| 文本框宽度考虑预期输入量，移动端多行框在固定宽度内随内容增高 | [Apple 的文本框指南](https://developer.apple.com/design/human-interface-guidelines/text-fields)、[MDN 的表单字段尺寸](https://developer.mozilla.org/en-US/docs/Web/CSS/Reference/Properties/field-sizing) |
| 数字列和列头沿同一右边线，列宽按字段分配 | [GOV.UK 表格](https://design-system.service.gov.uk/components/table/) |

## Three.js 空间动效

组件按容器宽高更新相机和画布，只在播放期间渲染。WebGL 2 不可用或启用减少动态效果时保留静态画面。播放完成后释放几何体、材质和渲染器。[画布尺寸](https://threejs.org/manual/en/responsive.html) · [资源释放](https://threejs.org/manual/en/cleanup.html) · [WebGLRenderer](https://threejs.org/docs/pages/WebGLRenderer.html)

离线模板包使用 [Three.js 0.187.0](https://www.npmjs.com/package/three/v/0.187.0)，MIT 许可随文件存放于 `kit/vendor/three/LICENSE`。重新打包时从该版本安装包解出 `build/three.module.js` 和同目录的 `three.core.js`，以 `kit/vendor/three/exports.mjs` 为入口，将 `three` 别名指向解出的 `three.module.js`，使用 esbuild 0.28.2 输出 `iife`，全局变量为 `LzThree`，目标为 `es2020`，启用压缩并保留许可证注释。
