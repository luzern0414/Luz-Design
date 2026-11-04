# 动效配方

规则卡 `interface-motion`（视觉设计规范 › 一、视觉基础 › 动效、动效细则、层级与立体感、稳定显示）只给了令牌和场景表。本文补“怎么做出高级质感”：转场怎么编排、共享元素怎么做、骨架怎么过渡、数字怎么滚、加购怎么飞。

## 先读这里

- 配方服从规则卡，不放宽任何一条：时长只用 100、150、200、300 四档，缓动只用标准、进入、退出三条，位移缩放出现消失只动 `transform` 与 `opacity`，逐项延迟最多 8 项、总延迟不超过 240 毫秒，动画可打断，必须有减少动态效果分支，不用带过冲的弹簧、无意义循环、长于 1.2 秒的界面转场。
- 超出现有规范的建议一律放在文末“待用户裁定的事项”，配方正文里凡是用到它们的地方都标了“提议”。没有裁定之前，按正文默认写法做，不要自己加档位。
- 阅读型文档不用动效；产品界面（后台、小程序、手机网页、智能体界面、原型）按本文做。
- 能在浏览器里演示的配方都做成了可点的演示卡（13 张，带“减少动态效果”开关与“时长个性”三选一），本文的代码来自这些演示，并在 Edge 的 Chromium 内核里点过（见“验收方法”末尾的实测记录）。

### 令牌速查

| 名称 | 值 | 用在 |
| --- | --- | --- |
| `--dur-instant` | 100 毫秒 | 按下、焦点、悬停的颜色变化 |
| `--dur-fast` | 150 毫秒 | 图标交叉淡化、提示出现、卡片悬停与回弹 |
| `--dur-base` | 200 毫秒 | 标签页下划线、列表项进入、遮罩 |
| `--dur-slow` | 300 毫秒 | 面板、二级页（规范 280–320）、模块显隐 |
| `--ease-standard` | `cubic-bezier(0.2, 0, 0, 1)` | 屏幕内的移动、尺寸变化、`FLIP` 位移 |
| `--ease-enter` | `cubic-bezier(0, 0, 0, 1)` | 出现、展开、淡入（减速） |
| `--ease-exit` | `cubic-bezier(0.3, 0, 1, 1)` | 离开、收起、淡出（加速） |
| `linear` | 线性 | 只给转圈、骨架流光、进度、滚动联动 |

场景表里还有几个数值没有进令牌表，本文原样使用并称为“场景值”，不当成新档位：对话框 240、底部弹层 280、关闭 160（`references/ui-kit/ui.css` 用 `--dur-dialog`、`--dur-sheet`、`--dur-close` 命名）、二级页 280–320、骨架流光 1.2 秒、数字计数 800–1000 毫秒、关键成功不超过 2.4 秒。

### 通用底座

所有配方共用这一段。位移与缩放乘以 `--mv`，进入页的起始不透明度用 `--fc`；减少动态效果时 `--mv` 变 0，位移缩放消失，淡入淡出的时长收到不超过 150 毫秒。系统偏好与手动开关写同一套，写在原规则之后（同优先级后写的生效）。

```css
:root {
  --dur-instant: 100ms; --dur-fast: 150ms; --dur-base: 200ms; --dur-slow: 300ms;
  --dur-dialog: 240ms; --dur-sheet: 280ms; --dur-close: 160ms;   /* 场景表已有的数值 */
  --ease-standard: cubic-bezier(0.2, 0, 0, 1);
  --ease-enter: cubic-bezier(0, 0, 0, 1);
  --ease-exit: cubic-bezier(0.3, 0, 1, 1);
  --mv: 1;   /* 位移与缩放的开关 */
  --fc: 1;   /* 进入页的起始不透明度，减少动态效果时为 0 */
}
@media (prefers-reduced-motion: reduce) {
  :root { --mv: 0; --fc: 0; --dur-base: var(--dur-fast); --dur-slow: var(--dur-fast); --dur-dialog: var(--dur-fast); --dur-sheet: var(--dur-fast); --dur-close: var(--dur-fast); }
}
html[data-rm] {   /* 手动开关或产品自己的“减少动态效果”设置，同一套 */
  --mv: 0; --fc: 0; --dur-base: var(--dur-fast); --dur-slow: var(--dur-fast); --dur-dialog: var(--dur-fast); --dur-sheet: var(--dur-fast); --dur-close: var(--dur-fast);
}
```

```js
const mq = matchMedia('(prefers-reduced-motion: reduce)');
let manual = false;                                  // 页面自己的开关
const rm = () => manual || mq.matches;               // 脚本动画先问它
mq.addEventListener('change', () => document.documentElement.toggleAttribute('data-rm', rm()));
const css = (n) => getComputedStyle(document.documentElement).getPropertyValue(n).trim();
const ms = (n) => parseFloat(css(n)) || 0;           // ms('--dur-slow') 得 300，减少动态效果时得 150
const ease = (n) => css(n);

/* 可打断的 WAAPI：新动画从“当前画面”出发，旧动画取消。进入只写起点，终点是元素现在的样式。 */
const live = new WeakMap();
const snap = (e) => { const cs = getComputedStyle(e); return { opacity: cs.opacity, transform: cs.transform }; };
function enter(e, from, opt) {
  const prev = live.get(e);
  const start = prev ? snap(e) : from;
  if (prev) prev.cancel();
  const a = e.animate([start], { fill: 'none', ...opt });
  live.set(e, a);
  a.finished.then(() => { if (live.get(e) === a) live.delete(e); }, () => {});
  return a;
}
function leave(e, to, opt) {
  const prev = live.get(e);
  const start = snap(e);
  if (prev) prev.cancel();
  const a = e.animate([start, to], { fill: 'forwards', ...opt });
  live.set(e, a);
  return a;                      // 调用方在 a.finished 之后收尾，并 cancel() 掉 forwards 的填充
}
```

### 配方索引

| 配方 | 主要令牌 | 动的属性 | 同时在动的元素 |
| --- | --- | --- | --- |
| 1 按压反馈 | `--dur-instant` 或 `--dur-fast`，标准 | `transform`、`box-shadow`、`background-color` | 1 |
| 2 二级页推入与返回 | `--dur-slow`，进入、退出、标准 | `transform`、`opacity` | 3 |
| 3 标签切换 | `--dur-base`，标准、进入 | `transform`、`opacity` | 2 |
| 4 底部弹层与对话框 | 遮罩 `--dur-base`，场景值 240、280、160 | `transform`、`opacity` | 2 |
| 5 共享元素转场 | `--dur-slow`，标准 | 快照组，或 `transform` | 1 个命名元素加整页淡入 |
| 6 骨架屏到内容 | 流光 1.2 秒，`--dur-base`，进入 | `transform`、`opacity` | 骨架块数 |
| 7 列表逐项进入 | `--dur-base`，进入 | `transform`、`opacity` | 不超过 8 |
| 8 数字滚动 | 场景值 800–1000，进入 | 文本，或 `transform` | 1 个指标 |
| 9 加入购物车飞入 | `--dur-slow`，标准与退出 | `transform` | 不超过 3 |
| 10 成功反馈 | `--dur-base`，`--dur-slow`，进入 | `stroke-dashoffset`、`transform`、`opacity` | 圆、对勾、彩屑不超过 14 |
| 11 滚动联动 | 线性（跟随滚动） | `transform`、`opacity` | 4 |
| 12 手势跟手 | 跟手无时长；松手 `--dur-base`，标准 | `transform` | 1 |
| 13 轻提示与按钮加载态 | `--dur-fast`，`--dur-instant`，线性 | `transform`、`opacity` | 2 |

---

## 配方 1：按压反馈

**用在哪**：可点击卡片、按钮、列表行、宫格入口。

**感受目标**：手指一落下就“被接住”，松手干脆回位，不拖泥带水。

**编排**：

| 谁 | 做什么 | 时长 | 曲线 |
| --- | --- | --- | --- |
| 可点卡片 | 缩放到 0.98，阴影回到第 1 级 | `--dur-instant` 或 `--dur-fast` | 标准 |
| 主按钮 | 下沉 1 像素，去掉底部 1 像素边，换按下阶底色 | 同上 | 标准 |
| 列表行、宫格入口 | 底色加深一阶 | 同上 | 标准 |
| 悬停（只在有鼠标的设备） | 卡片升到第 2 级，发丝线加深 | `--dur-fast` | 进入 |

按下与松手同一时长，松手不另起一套。个性只在 100 与 150 之间选。

**代码**：

```css
.press-card {
  background: #fff; border: 1px solid var(--line); border-radius: 12px; box-shadow: var(--e1);
  transition: transform var(--p-press) var(--ease-standard),
              box-shadow var(--dur-fast) var(--ease-enter),
              border-color var(--dur-fast) var(--ease-enter);
}
@media (hover: hover) { .press-card:hover { box-shadow: var(--e2); border-color: var(--line-strong); } }
.press-card:active { transform: scale(calc(1 - 0.02 * var(--mv))); box-shadow: var(--e1); }

.btn-p {   /* 主按钮：底边与内顶部高光走 box-shadow，下沉走 transform */
  box-shadow: inset 0 1px 0 rgb(255 255 255 / 20%), 0 1px 0 var(--primary-d);
  transition: transform var(--p-press) var(--ease-standard), box-shadow var(--p-press) var(--ease-standard), background-color var(--p-press) var(--ease-standard);
}
.btn-p:active { transform: translateY(calc(1px * var(--mv))); box-shadow: inset 0 1px 0 rgb(255 255 255 / 20%); background: var(--primary-d); }

.press-row { transition: background-color var(--p-press) var(--ease-standard); }
.press-row:active { background: var(--press); }
button { -webkit-tap-highlight-color: transparent; touch-action: manipulation; }
```

`--p-press` 是个性变量，默认 `var(--dur-fast)`，见“动效个性”。

**降级**：`--mv` 为 0，缩放与下沉消失；底色与层级变化保留（颜色与层级变化不是运动）。

**性能与可访问性**：`transform` 走合成层；`box-shadow`、`background-color` 只在小面积上过渡。触屏没有悬停，悬停样式一律包在 `@media (hover: hover)` 里，否则点一下之后悬停态会粘住。去掉浏览器默认的点按高亮之后，必须靠 `:active` 给出反馈。点击目标不小于 44 像素；键盘 Tab 到达才出现 2 像素深色轮廓。

**常见翻车**：缩放写成 0.95 以下显得夸张；按压时长超过 150；悬停与按下同时改 `transform` 造成抖动；写成 `transition: all`；整屏宽的大卡片缩放会让边缘发虚，这类卡只换阴影层级；在可滚动列表里用 `pointerdown` 触发，用户只是想滚动却被打断。

---

## 配方 2：二级页推入与返回

**用在哪**：小程序与手机网页进入详情、订单等二级页，以及返回。

**感受目标**：新页从右边来覆盖旧页，旧页退让但不消失；返回是同一个动作倒放，手指可以带着它走。

**编排**：

| 谁 | 做什么 | 时长 | 曲线 |
| --- | --- | --- | --- |
| 新页 B 推入 | `translateX(100%)` 到 0 | `--dur-slow`（规范 280–320） | 进入 |
| 底页 A | 左移 30%，同时被一层 12% 的深色轻微变暗 | 同上 | 标准（仍在屏幕内） |
| B 返回 | 0 到 `translateX(100%)` | 同上 | 退出 |
| A 返回 | 回到原位，变暗退去，恢复原滚动位置 | 同上 | 标准 |

三者同时开始，不排队。A 不销毁，保留它的 DOM 与 `scrollTop`，返回时才能恢复滚动位置而不闪白。

**返回手势跟手的做法**：只接管左边缘约 28 像素；手指怎么动，B 就 `translateX(dx)`、A 就 `translateX(-30% * (1 - 进度))`，跟手阶段关掉过渡。松手时按“位置或速度”决定：进度超过 30%，或最近 80 毫秒内的速度超过 0.5 像素每毫秒就返回，否则回弹。松手后不再手写动画：同一帧里去掉内联样式和跟手标记，让 CSS 过渡从当前位置走到终点，时长与曲线同上，不过冲。

**代码**：

```css
.pg { position: absolute; inset: 0; background: #fff; }
.pg-a { transition: transform var(--dur-slow) var(--ease-standard); }
.pushed .pg-a { transform: translateX(calc(-30% * var(--mv))); }
.pg-b {
  transform: translateX(calc(100% * var(--mv))); opacity: var(--fc);          /* 减少动态效果时：不位移，改淡入 */
  transition: transform var(--dur-slow) var(--ease-exit), opacity var(--dur-slow) var(--ease-exit);
}
.pushed .pg-b { transform: none; opacity: 1; transition-timing-function: var(--ease-enter); }
.dim { position: absolute; inset: 0; background: rgb(24 24 27 / 0%); pointer-events: none; transition: background-color var(--dur-slow) var(--ease-standard); }
.pushed .dim { background: rgb(24 24 27 / 12%); }
.dragging .pg, .dragging .dim { transition: none; }      /* 跟手阶段没有过渡 */
.edge { position: absolute; left: 0; top: 0; bottom: 0; width: 28px; touch-action: pan-y; }
```

```js
const stage = document.querySelector('#push'), A = stage.querySelector('.pg-a'), B = stage.querySelector('.pg-b');
const dim = stage.querySelector('.dim'), edge = B.querySelector('.edge');
const set = (on) => { stage.classList.toggle('pushed', on); A.toggleAttribute('inert', on); B.toggleAttribute('inert', !on); };
let d = null;
edge.addEventListener('pointerdown', (e) => {
  if (!stage.classList.contains('pushed')) return;
  edge.setPointerCapture(e.pointerId);
  d = { x0: e.clientX, w: stage.clientWidth, x: 0, last: e.clientX, lt: performance.now(), v: 0 };
  stage.classList.add('dragging');
});
edge.addEventListener('pointermove', (e) => {
  if (!d) return;
  const now = performance.now();
  d.x = Math.max(0, e.clientX - d.x0);
  d.v = (e.clientX - d.last) / ((now - d.lt) || 1); d.last = e.clientX; d.lt = now;
  const p = Math.min(1, d.x / d.w);
  B.style.transform = `translateX(${d.x}px)`; B.style.opacity = '1';
  A.style.transform = `translateX(${-30 * (1 - p) * (rm() ? 0 : 1)}%)`;
  dim.style.backgroundColor = `rgb(24 24 27 / ${(12 * (1 - p)).toFixed(1)}%)`;
});
const end = () => {
  if (!d) return;
  const v = performance.now() - d.lt > 80 ? 0 : d.v;          // 停住再松手，速度算 0
  const back = d.x / d.w > 0.3 || v > 0.5;
  d = null;
  stage.classList.remove('dragging');
  B.style.transform = ''; B.style.opacity = ''; A.style.transform = ''; dim.style.backgroundColor = '';
  set(!back);                                                  // 过渡从当前位置接着走
};
edge.addEventListener('pointerup', end);
edge.addEventListener('pointercancel', end);
```

**降级**：B 不位移，只在 `--dur-fast` 内淡入（`--fc` 为 0）；A 不位移；变暗保留。跟手拖动是手指在动，不是自动动画，可以保留；松手后的回位走降级后的时长。

**性能与可访问性**：同时动的是 A、B 两个整页层和一个遮罩；页面很重时，B 里的图片先给固定尺寸，避免推入中途撑开布局（稳定显示）。看不见的那一页加 `inert`，键盘与读屏都进不去。必须有“返回”按钮，边缘手势只是加速。

**常见翻车**：用 `left` 或 `margin` 做动画；返回时重新渲染 A，滚动位置丢失并闪白；只动 B 不动 A，层次感没了；时长超过 320；页面里 `position: fixed` 的底部栏放在带 `transform` 的页层里，固定定位会失效，改把底部栏放进页层内，或过渡结束后清掉页层的 `transform`；边缘手势与系统自带的边缘返回冲突，微信与 iOS 浏览器里要在真机实测；松手后另写一段 JS 补间，会与 CSS 过渡打架。

---

## 配方 3：标签切换淡入与选中下划线滑动

**用在哪**：底部标签、顶部标签页、分段控件、后台菜单切换。

**感受目标**：内容“换了”而不是“飞过去”；下划线像一根被拉动的线。

**编排**：

| 谁 | 做什么 | 时长 | 曲线 |
| --- | --- | --- | --- |
| 内容区 | 不透明度 0 到 1，不位移 | `--dur-fast` 或 `--dur-base`（150–200） | 进入 |
| 选中下划线 | 平移，并用缩放改变宽度 | `--dur-base` | 标准 |

两者同时开始。后台内容区可以在淡入的同时上移不超过 8 像素并按区块错开，规则见配方 7。

**代码**：

```css
.tabs { position: relative; display: flex; border-bottom: 1px solid var(--line-strong); }
.ul {                       /* 固定宽度 100px 的 2px 条，宽度只用 scaleX 改，不 transition width */
  position: absolute; left: 0; bottom: -1px; width: 100px; height: 2px; background: var(--primary);
  transform-origin: 0 0;
  transform: translateX(var(--ux, 0px)) scaleX(var(--uw, 0.3));
  transition: transform calc(var(--dur-base) * var(--mv)) var(--ease-standard);   /* 减少动态效果：乘 0，直接到位 */
}
```

```js
const list = document.querySelector('#tabs'), tabs = [...list.querySelectorAll('[role="tab"]')], panel = document.querySelector('#tabpanel');
const DATA = ['为你推荐的内容', '全部分类的内容', '我的订单的内容'];
const place = () => {
  const t = tabs.find((x) => x.getAttribute('aria-selected') === 'true');
  list.style.setProperty('--ux', (t.offsetLeft + 16) + 'px');            // 16 是标签的左右内边距
  list.style.setProperty('--uw', ((t.offsetWidth - 32) / 100).toFixed(4));
};
function pick(i) {
  tabs.forEach((t, j) => { t.setAttribute('aria-selected', String(i === j)); t.tabIndex = i === j ? 0 : -1; });
  place();
  panel.textContent = DATA[i];                                           // 先换内容再淡入，不先清空
  enter(panel, { opacity: 0 }, { duration: ms('--p-fade'), easing: ease('--ease-enter') });   // 连点时从当前不透明度继续
}
addEventListener('resize', place);                                       // 字体或窗口变化后重新量
```

**降级**：下划线直接到位；内容仍用不超过 150 毫秒的淡入（淡入淡出是允许的降级）。

**性能与可访问性**：只缩放纯色条，条不失真；文字本身不缩放。`role="tablist"`、`role="tab"`、`role="tabpanel"`，方向键切换，`aria-selected` 与漫游 `tabindex` 要写全。

**常见翻车**：用 `transition: width` 或 `left` 做下划线；内容区高度随内容变化引起整页抖动，给面板固定最小高度；切换时先清空旧内容再渲染，闪白；连点时淡入每次从 0 重来，用上面的 `enter` 从当前值接着走；底部标签切换做横向滑动（规范明确不做）。

---

## 配方 4：底部弹层与对话框

**用在哪**：选择、确认、详情面板。

**感受目标**：面板“被推出来”，遮罩同时变暗；关闭干脆利落，随时可以反悔。

**编排**：

| 谁 | 做什么 | 时长 | 曲线 |
| --- | --- | --- | --- |
| 遮罩（45%） | 淡入 | `--dur-base`（200） | 进入 |
| 对话框与居中面板 | 从 0.96 放大并淡入，不从右侧滑入 | 240（场景值） | 进入 |
| 底部弹层 | 从底部上滑，只圆顶部两角 | 280（场景值） | 进入 |
| 任意关闭 | 遮罩与面板同时反向 | 160（场景值） | 退出 |

只在打开时播放；面板内容更新时不重播。动画中按 Esc、点遮罩或点关闭，立刻从当前画面反向，不等播完。

**代码**：原生 `<dialog>` 当全屏容器，遮罩是里面自己的元素，不去动 `::backdrop`（没有用它，也没有实测它的动画支持）。

```css
dialog.ov { border: 0; padding: 0; margin: 0; max-width: none; max-height: none; width: 100%; height: 100%; background: transparent; overflow: hidden; }
dialog.ov::backdrop { background: transparent; }
.scrim { position: absolute; inset: 0; background: rgb(24 24 27 / 45%); }
.panel { position: absolute; background: #fff; box-shadow: var(--e4); padding: 16px; }
.panel-dialog { inset: 0; margin: auto; width: min(480px, calc(100% - 32px)); height: fit-content; border-radius: 16px; }
.panel-sheet  { left: 0; right: 0; bottom: 0; border-radius: 16px 16px 0 0; }
```

```js
function open(d, kind) {
  const panel = d.querySelector('.panel'), scrim = d.querySelector('.scrim');
  d._closing = false;
  if (!d.open) d.showModal();
  enter(scrim, { opacity: 0 }, { duration: ms('--dur-base'), easing: ease('--ease-enter') });
  const from = rm() ? { opacity: 0 } : kind === 'sheet' ? { transform: 'translateY(100%)' } : { opacity: 0, transform: 'scale(0.96)' };
  enter(panel, from, { duration: ms(kind === 'sheet' ? '--dur-sheet' : '--dur-dialog'), easing: ease('--ease-enter') });
}
async function close(d, kind) {
  if (!d.open || d._closing) return;
  d._closing = true;
  const panel = d.querySelector('.panel'), scrim = d.querySelector('.scrim');
  const o = { duration: ms('--dur-close'), easing: ease('--ease-exit') };
  leave(scrim, { opacity: 0 }, o);
  const to = rm() ? { opacity: 0 } : kind === 'sheet' ? { transform: 'translateY(100%)' } : { opacity: 0, transform: 'scale(0.96)' };
  const a = leave(panel, to, o);
  try { await a.finished; } catch (e) { return; }          // 被重新打开打断
  d.close();
  live.get(panel)?.cancel(); live.get(scrim)?.cancel(); live.delete(panel); live.delete(scrim);
  d._closing = false;
}
d.addEventListener('cancel', (e) => { e.preventDefault(); close(d, kind); });     // Esc 走自己的关闭动画
d.addEventListener('click', (e) => { if (e.target.classList.contains('scrim')) close(d, kind); });
```

**降级**：去掉位移与缩放，面板与遮罩只做不超过 150 毫秒的淡入淡出。

**性能与可访问性**：同时动的只有遮罩与面板两个元素。`showModal()` 自带焦点陷阱与背景 `inert`，关闭后焦点回到触发按钮。主滚动区写 `scrollbar-gutter: stable`，弹层锁定滚动时页面不左右跳。

**常见翻车**：关闭用进入曲线，显得拖沓；动画结束才响应下一次点击；遮罩与面板错开播放；用 `display: none` 到 `block` 直接做过渡，什么都不会动（要么用 WAAPI，要么用 `@starting-style` 加 `allow-discrete`，后者要在目标 WebView 实测）；对话框从右侧滑入（规范明确不做）；面板里数据一更新就重播入场。

---

## 配方 5：共享元素转场（列表商品图到详情大图）

**用在哪**：列表里的商品图点进详情，变成详情大图；返回时缩回原位。

**感受目标**：同一件东西从小长大，眼睛不用重新找它。

**编排**：

| 谁 | 做什么 | 时长 | 曲线 |
| --- | --- | --- | --- |
| 被命名的那张图 | 从缩略图的位置与大小变到大图的位置与大小 | `--dur-slow` | 标准（屏幕内的移动与尺寸变化） |
| 其余整页 | 新页在旧页上方淡入，旧页不淡出 | `--dur-base` | 进入 |
| 详情里的文字区（降级路径） | 淡入，不位移 | `--dur-base` | 进入 |

操作后 100 毫秒内开始。整页转场不超过 1.2 秒，本配方只有 300 毫秒。

**代码**（优先：View Transitions API）：

命名唯一性是这个配方最容易翻车的地方：

1. 同一时刻、同一个文档里，每个 `view-transition-name` 只能出现一次，旧状态拍快照时一次，新状态拍快照时一次。重名会让转场被跳过：实测 `ready` 以 `InvalidStateError` 拒绝，更新回调照常执行。
2. 列表里有很多张卡时，不要在样式表里给所有缩略图写固定名字。点击时只给被点击的那一张设置名字，更新回调里把名字从缩略图交给详情大图，`finished` 之后清掉。
3. 更新回调里只做同步的 DOM 切换。数据先取好再调 `startViewTransition`，不要在回调里 `await` 请求，期间页面是冻结的。
4. 用 `transition.finished` 清理名字，不用 `setTimeout`；连点时用自增的令牌防止旧过渡的清理把新过渡的名字清掉。
5. 转场进行时页面不接收指针事件（实测：这时 `pointerdown` 的目标是 `html`，不是被点的卡片），所以“动画可打断”要自己补：监听一次 `pointerdown`，调 `transition.skipTransition()`，点一下就直接到终态（实测在 100 毫秒处点一下，转场约 114 毫秒就结束）。

```css
::view-transition-group(hero) { animation-duration: var(--dur-slow); animation-timing-function: var(--ease-standard); }
/* 整页：旧页保持不透明垫在下面，新页淡入。默认的“旧淡出、新淡入加 plus-lighter 混合”靠两者透明度之和为 1 才不闪，时长或曲线一改就不成立（理论推断，没有单独复现） */
::view-transition-old(root) { animation: none; mix-blend-mode: normal; }
::view-transition-new(root) { animation: vt-in var(--dur-base) var(--ease-enter) both; mix-blend-mode: normal; }
@keyframes vt-in { from { opacity: 0; } }
html[data-rm]::view-transition-group(*), html[data-rm]::view-transition-old(*), html[data-rm]::view-transition-new(*) { animation-duration: 1ms !important; }
.thumb, .hero { aspect-ratio: 4 / 3; }          /* 缩略图与大图同比例，快照与 FLIP 都不会拉伸内容 */
```

```js
let token = 0;
/* go(旧状态里的命名元素, 同步更新函数, 取新状态里的命名元素, 不支持时的降级函数) */
function go(oldEl, update, getNewEl, fallback) {
  if (rm()) { update(); return; }                                  // 减少动态效果：直接切换，不调 View Transitions
  if (!document.startViewTransition) { fallback(); return; }       // 不支持：走 FLIP
  const id = ++token;
  oldEl.style.viewTransitionName = 'hero';                         // 只给被点击的这一张命名
  const t = document.startViewTransition(() => {
    oldEl.style.viewTransitionName = '';                           // 旧状态已拍完，名字交给新元素
    update();
    getNewEl().style.viewTransitionName = 'hero';
  });
  const skip = () => t.skipTransition();
  document.addEventListener('pointerdown', skip, { once: true });
  t.finished.finally(() => {
    document.removeEventListener('pointerdown', skip);
    if (id === token) clearNames();                                // 把 hero 与所有缩略图上的名字清空
  });
}
openBtn.onclick = () => go(thumb, () => showDetail(i), () => hero, () => {
  const first = thumb.getBoundingClientRect();                     // FLIP 的 First
  showDetail(i);
  flip(hero, first, ms('--dur-slow'));
});
```

**代码**（不支持时：FLIP）：先量首末位置，再用 `transform` 反推回起点，从起点播放到原位（规范：`FLIP` 位移用标准曲线）。

```js
function flip(node, first, dur) {
  const last = node.getBoundingClientRect();                       // Last
  const dx = first.left - last.left, dy = first.top - last.top;     // Invert
  const sx = first.width / last.width, sy = first.height / last.height;
  node.style.transformOrigin = '0 0';
  const a = node.animate(                                          // Play
    [{ transform: `translate(${dx}px, ${dy}px) scale(${sx}, ${sy})` }, { transform: 'none' }],
    { duration: dur, easing: 'cubic-bezier(0.2, 0, 0, 1)' });
  a.finished.finally(() => { node.style.transformOrigin = ''; });
}
```

返回时对称：首位置是大图，更新后缩略图出现，对缩略图做同样的 `flip`。

**支持情况**：View Transitions 在各引擎里的支持时间不同，微信里取决于所用的内核。本文不写任何版本号：先用 `if (!document.startViewTransition)` 做特性检测，上线前在目标 WebView（至少 iOS 微信与 Android 微信各一台）实测，必须包括“有这个函数但表现不对”的情形。小程序原生页面不是浏览器的文档，没有这个 API，要另走原生方案（待用户裁定第 15 条）。在 Edge 的 Chromium 内核里实测：转场跑通，`ready` 兑现，快照组里有 `hero`；把 `startViewTransition` 删掉后，FLIP 分支也走通。

**降级**（减少动态效果）：不调用 View Transitions，直接切换；样式里再把转场伪元素的时长压到 1 毫秒兜底。

**性能与可访问性**：快照是位图，只命名一个元素，不要给整张卡命名；同比例缩略图与大图让 FLIP 的缩放不拉伸内容；FLIP 期间给被动画的节点临时抬高层级，避免被相邻卡片盖住。读屏用户靠详情页的标题与“返回”按钮，动画不承载信息。视图过渡期间新旧内容会同时存在于文档里，可能带来阅读位置丢失、焦点混乱和实时区域重复播报（MDN 视图过渡 API 概述列出的无障碍风险）：转场开始前把旧内容设为 `inert`，结束后把焦点移到详情页标题，并在 `finished` 里再检查一次。

**常见翻车**：重名；在样式表里给所有缩略图写同一个名字；回调里异步请求；更新回调之后新旧状态的滚动位置不一致，图飞到屏外；父级 `overflow: hidden` 的圆角裁剪裁不住快照（快照在最上层）；缩略图与大图比例不同，`scale` 把内容拉变形；旧页新页同时用默认的 `plus-lighter` 混合却改了其中一边的时长，透明度之和偏离 1，理论上会中途发白或发暗（没有单独复现）。另外：快照组的尺寸变化由浏览器内部动画，不是 `transform`，见待用户裁定第 7 条。

---

## 配方 6：骨架屏到内容的过渡

**用在哪**：列表、详情、卡片的首次加载。

**感受目标**：先有轮廓，再有内容；内容出现时原地亮起来，不推开任何东西。

**编排**：

| 谁 | 做什么 | 时长 | 曲线 |
| --- | --- | --- | --- |
| 骨架块 | 出现后至少停留 500 毫秒 | — | — |
| 流光 | 横向扫过，只在加载态 | 1.2 秒循环（场景值） | 线性 |
| 内容 | 原位淡入，不位移 | `--dur-base` 或 `--dur-fast` | 进入 |
| 骨架 | 淡出 | `--dur-fast` | 退出 |

骨架与内容放在同一个网格单元里（`grid-area: 1 / 1`），尺寸一致，内容进来时不会有任何块移动，累计布局偏移为 0。骨架出现的时机以规范“骨架屏”一节为准，请求很快回来时宁可保留旧内容也不要让骨架一闪。

**代码**：

```css
.sk-wrap { display: grid; height: 132px; }                 /* 固定高度，两层叠在一起 */
.sk-layer { grid-area: 1 / 1; }
.sk-sk { transition: opacity var(--dur-fast) var(--ease-exit); }
.ct { transition: opacity var(--dur-base) var(--ease-enter); }
[data-state="loading"] .ct { opacity: 0; }
[data-state="ready"] .sk-sk { opacity: 0; }
.sk-bone { position: relative; overflow: hidden; background: #E4E4E7; border-radius: 8px; }
.sk-bone::after {            /* 骨架流光是规范里“界面不用渐变”的唯一例外 */
  content: ""; position: absolute; inset: 0; transform: translateX(-100%);
  background: linear-gradient(90deg, rgb(255 255 255 / 0%), rgb(255 255 255 / 60%), rgb(255 255 255 / 0%));
}
[data-state="loading"] .sk-bone::after { animation: shine 1.2s linear infinite; }   /* 只在加载态 */
@keyframes shine { to { transform: translateX(100%); } }
@media (prefers-reduced-motion: reduce) { .sk-bone::after { animation: none !important; } }
html[data-rm] .sk-bone::after { animation: none !important; }
```

```js
const box = document.querySelector('#sk');
function load() {
  box.dataset.state = 'loading'; box.setAttribute('aria-busy', 'true');
  const shown = performance.now();
  fetchData().then(render).then(() => {
    const wait = Math.max(0, 500 - (performance.now() - shown));       // 骨架至少停留 500 毫秒
    setTimeout(() => { box.dataset.state = 'ready'; box.setAttribute('aria-busy', 'false'); }, wait);
  });
}
```

**降级**：流光停止，骨架显示静态浅灰块；内容淡入保留（不超过 150 毫秒）。

**性能与可访问性**：流光是 `::after` 的 `translateX`，在 `overflow: hidden` 的父级里，不动 `background-position`（那会重绘）。离开加载态时必须让动画真的停掉：状态选择器不再匹配，动画自然消失，不要只是 `display: none` 一层。同屏骨架块不要几十个都跑流光。`aria-busy` 告诉读屏内容在加载。

**常见翻车**：数据 80 毫秒回来，骨架一闪而过；骨架与内容尺寸不一致，落地时跳一下；内容进入带 `translateY`；流光一直循环到页面销毁；用 `background-position` 做流光。

---

## 配方 7：列表逐项进入

**用在哪**：列表、卡片网格首次出现，后台内容区按区块错开。

**感受目标**：像一页纸被“翻开”，不是一个个排队。

**编排**：

| 规则 | 数值 |
| --- | --- |
| 参与错开的项数 | 最多 8 项，其余项与第 8 项同时出现 |
| 相邻两项间隔 | 20–40 毫秒 |
| 总延迟 | 不超过 240 毫秒 |
| 单项动画 | `opacity` 0 到 1，加上移 8 像素以内，`--dur-base`，进入曲线 |
| 播放时机 | 只在首次进入；筛选、排序、刷新不重播；只用于进入，退出不错开 |

规范的两条界线在 8 项且间隔 40 时冲突（7 乘 40 是 280，超过 240），取更严的：`间隔 = min(个性间隔, floor(240 ÷ (参与项数 - 1)))`，8 项时最多 34 毫秒（待用户裁定第 17 条）。加载更多追加的新项只淡入 150 毫秒，不位移，见规范场景细则。

**代码**：

```js
const box = document.querySelector('#lst'), rows = [...box.querySelectorAll('.lrow')];
function play() {
  box.classList.remove('armed');
  const n = Math.min(rows.length, 8);
  const step = Math.min(ms('--p-step'), Math.floor(240 / (n - 1)));       // --p-step 是 20–40 的个性值
  rows.forEach((r, i) => {
    r.getAnimations().forEach((a) => a.cancel());
    const quiet = rm();
    r.animate(quiet ? [{ opacity: 0 }] : [{ opacity: 0, transform: 'translateY(8px)' }], {
      duration: quiet ? ms('--dur-fast') : ms('--dur-base'),
      delay: quiet ? 0 : Math.min(i, 7) * step,                           // 第 9 项起与第 8 项同时
      easing: ease('--ease-enter'), fill: 'backwards'                     // 等待期间保持透明
    });
  });
}
box.classList.add('armed');                                               // 先由脚本藏起来：脚本失败时内容仍可见
const io = new IntersectionObserver(([e]) => { if (e.isIntersecting) { io.disconnect(); play(); } }, { threshold: 0.6 });
io.observe(box);
```

```css
.armed .lrow { opacity: 0; }       /* 由脚本加这个类，不写成默认样式 */
```

**降级**：一起淡入，不错开，不位移。

**性能与可访问性**：同时动的元素不超过 8 个；长列表不动画（见“性能预算”）；用 `fill: 'backwards'` 而不是在样式里先写 `opacity: 0`，避免脚本失败时内容永远不出现。

**常见翻车**：用样式表里的 `animation-delay` 给 `nth-child(1…20)` 各写一个延迟，总延迟变成 800 毫秒；用 `setTimeout` 串联，等前一项播完才开始下一项；每次重渲染都重播；首屏以外的项也错开；对退出也做错开。

---

## 配方 8：数字滚动与计数

**用在哪**：指标卡、金额、统计页的核心数字。

**感受目标**：数字“落定”，先快后慢，不抖。

**编排**：规范“数据变化”：指标数字从 0（或上一个值）计数到目标值，800–1000 毫秒（场景值，不是令牌）；曲线用进入（减速）。只在数据首次到达或用户主动触发时播，之后的更新直接换值。

**两种做法的取舍**：

| | JS 计数 | `transform` 滚动数位 |
| --- | --- | --- |
| 原理 | `requestAnimationFrame` 里每帧改文本 | 每一位一条 0–9 的竖条，`translateY` 平移 |
| 属性 | 文本（小面积重排重绘） | `transform`（合成） |
| 优点 | 任意格式：千分位、小数、百分比、单位；读屏读到最终值；代码短 | 质感像机械翻牌；没有每帧 JS |
| 缺点 | 每帧一次 JS 与文本重绘；要防宽度抖动 | 位数变化要重建；DOM 变多（位数乘 10）；格式复杂就很难做 |
| 建议 | 默认用它（规范的写法就是“从 0 计数到目标值”） | 一个核心指标、位数固定时作为质感增强，需用户裁定（第 12 条） |

两种都要：`font-variant-numeric: tabular-nums`，容器固定宽度（`width: 9ch` 或最小宽度）且左对齐，否则数字变宽会推挤邻居，产生布局偏移。

**代码**：

```js
function bezier(str) {                            // 读 --ease-enter 这样的令牌，保证和 CSS 曲线一致
  const [x1, y1, x2, y2] = (str.match(/-?\d*\.?\d+/g) || [0, 0, 1, 1]).map(Number);
  const cx = 3 * x1, bx = 3 * (x2 - x1) - cx, ax = 1 - cx - bx, cy = 3 * y1, by = 3 * (y2 - y1) - cy, ay = 1 - cy - by;
  const X = (t) => ((ax * t + bx) * t + cx) * t, Y = (t) => ((ay * t + by) * t + cy) * t;
  return (x) => { let lo = 0, hi = 1, t = x; for (let i = 0; i < 28; i++) { const d = X(t) - x; if (Math.abs(d) < 1e-5) break; if (d > 0) hi = t; else lo = t; t = (lo + hi) / 2; } return Y(t); };
}
function countTo(node, from, to) {
  if (rm()) { node.textContent = fmt(to); return; }                       // 直接显示终值
  const dur = ms('--p-count'), f = bezier(ease('--ease-enter')), t0 = performance.now();
  cancelAnimationFrame(node._raf);
  const tick = (now) => {
    const p = Math.min(1, (now - t0) / dur);
    node.textContent = fmt(from + (to - from) * f(p));
    if (p < 1) node._raf = requestAnimationFrame(tick);
  };
  node._raf = requestAnimationFrame(tick);
}
```

```css
.num { display: inline-flex; width: 9ch; font-variant-numeric: tabular-nums; }
.dg { display: inline-block; height: 36px; overflow: hidden; }      /* 滚动数位：每位一个窗口 */
.strip span { display: block; height: 36px; text-align: center; }  /* 0–9 竖排 */
```

```js
strips[i].style.transform = `translateY(${-digit * 36}px)`;         // 终态直接写好
strips[i].animate([{ transform: `translateY(${-prev * 36}px)` }, { transform: `translateY(${-digit * 36}px)` }],
  { duration: ms('--p-count'), easing: ease('--ease-enter') });
```

滚动数位的容器写 `role="img"` 与 `aria-label="12,846"`，竖条里的数字对读屏无意义。

**降级**：直接显示终值与完整数字。

**性能与可访问性**：每帧只改一个文本节点，不用 `innerHTML`；页面隐藏时 `requestAnimationFrame` 自己会停，回来时直接显示终值；动画中不让读屏反复朗读（`aria-live="off"`，最终值再告知）。

**常见翻车**：没有 `tabular-nums`，整行数字抖；容器宽度随数字变，推挤邻居；超过 1 秒；每次重渲染都从 0 重播；计数中途读屏一遍遍朗读。

---

## 配方 9：加入购物车的“飞入”

**用在哪**：商品图沿曲线飞向购物车图标。

**感受目标**：东西被“收”进购物车，路径是一条顺滑的弧线，到达时角标轻轻“点”一下。

**编排**：

| 谁 | 做什么 | 时长 | 曲线 |
| --- | --- | --- | --- |
| 外层（只动 X） | 水平平移到购物车 | `--dur-slow`（距离大，取 250–300） | 标准 |
| 内层（只动 Y） | 垂直平移到购物车，同时缩小到 0.4 | 同上 | 退出（先慢后快，像被吸进去） |
| 到达后 | 角标数字加一，角标缩放 1 到 1.2 再回 1 | `--dur-base` | 标准 |

**为什么两层嵌套**：同一个元素同一时刻只能有一条 `transform` 动画，两条同时写会互相覆盖。外层只负责 X、内层只负责 Y，各用各的缓动，合起来就是曲线。用独立的 `translate`、`scale` 属性在旧内核里不一定支持，所以不推荐。

**代码**：

```js
let flying = 0;
function fly(thumb, cart, stage, onLand) {
  if (rm() || flying >= 3) { onLand(); return; }                   // 减少动态效果，或同时飞的已有 3 个：直接计数
  flying++;
  const sr = stage.getBoundingClientRect(), pr = thumb.getBoundingClientRect(), cr = cart.getBoundingClientRect();
  const size = 36;
  const dx = (cr.left + cr.width / 2) - (pr.left + pr.width / 2);
  const dy = (cr.top + cr.height / 2) - (pr.top + pr.height / 2);
  const outer = Object.assign(document.createElement('div'), { className: 'fly' });     // 绝对定位 36×36
  const inner = Object.assign(document.createElement('div'), { className: 'fly-i' });   // 缩略图
  outer.style.left = (pr.left - sr.left + (pr.width - size) / 2) + 'px';
  outer.style.top = (pr.top - sr.top + (pr.height - size) / 2) + 'px';
  outer.append(inner); stage.append(outer);
  const dur = ms('--p-fly');
  const ax = outer.animate([{ transform: 'translateX(0)' }, { transform: `translateX(${dx}px)` }],
    { duration: dur, easing: ease('--ease-standard'), fill: 'forwards' });
  inner.animate([{ transform: 'translateY(0) scale(1)' }, { transform: `translateY(${dy}px) scale(0.4)` }],
    { duration: dur, easing: ease('--ease-exit'), fill: 'forwards' });
  ax.finished.then(() => { outer.remove(); flying--; onLand(); });
}
function pulse(badge) {
  badge.getAnimations().forEach((a) => a.cancel());
  badge.animate([{ transform: 'scale(1)' }, { transform: 'scale(1.2)', offset: 0.5 }, { transform: 'scale(1)' }],
    { duration: ms('--dur-base'), easing: ease('--ease-standard') });
}
```

```css
.fly { position: absolute; width: 36px; height: 36px; pointer-events: none; z-index: 3; }
.fly-i { width: 100%; height: 100%; border-radius: 8px; background: #DBEAFE; box-shadow: var(--e2); }
```

商品在滚动列表里、购物车固定在底部标签栏时，飞行层改用 `position: fixed`，起终点都用视口坐标，并在这 300 毫秒里不要让页面滚动。

**降级**：不飞；只更新角标数字，不脉冲。

**性能与可访问性**：飞的是 36 像素的缩略图，不是整张大图的克隆；同时飞行不超过 3 个（连点时多出来的直接计数）；飞行元素 `pointer-events: none`，结束必须移除节点。角标是 `aria-live="polite"`，读屏听到“购物车 1”。脉冲是“去而复返”的缩放，不是弹簧，曲线没有过冲。

**常见翻车**：一个元素上写两条 `transform` 动画；用 `left`、`top` 做动画；飞行层被父级 `overflow: hidden` 裁掉；到达后没有任何反馈；飞行超过 400 毫秒；连点产生几十个飞行元素；用弹簧或回弹曲线让图标在购物车上“弹”。

---

## 配方 10：成功反馈

**用在哪**：支付成功、中奖、人脸通过。普通保存只用轻提示（配方 13），不用本配方。

**感受目标**：确定、克制，像“盖章”，不是烟花。

**编排**：

| 谁 | 做什么 | 时长 | 曲线 |
| --- | --- | --- | --- |
| 成功层 | 淡入 | `--dur-base` | 进入 |
| 圆底 | 0.8 放大到 1 并淡入 | `--dur-base` | 进入 |
| 对勾 | 描边，`stroke-dashoffset` 从满到 0，晚 120 毫秒开始 | `--dur-slow` | 进入 |
| 彩屑（可选） | 少量纯色小方块向外飘散并淡出，数量不超过 14，不用发光与光芒 | 约 1.2 秒（场景值，规范上限 2.4 秒） | 进入 |

文字（“支付成功 ¥128.00”）与动画同时出现，结果不靠动画传达；整个反馈不挡下一步操作，彩屑 `pointer-events: none`。

**代码**：

```html
<svg viewBox="0 0 64 64" aria-hidden="true">
  <circle class="ok-c" cx="32" cy="32" r="28"/>
  <path class="ok-p" d="M20 33l8 8 16-17" pathLength="40"/>   <!-- pathLength 让描边长度恒为 40，不用手量 -->
</svg>
```

```css
.ok-c { fill: var(--primary-soft); transform-box: fill-box; transform-origin: center; }
.ok-p { fill: none; stroke: var(--primary); stroke-width: 4; stroke-linecap: round; stroke-linejoin: round; stroke-dasharray: 40; }
```

```js
function success(layer) {
  layer.hidden = false;
  if (rm()) return;                                               // 静态对勾，结果同时有文字，不放彩屑
  enter(layer, { opacity: 0 }, { duration: ms('--dur-base'), easing: ease('--ease-enter') });
  layer.querySelector('.ok-c').animate([{ transform: 'scale(0.8)', opacity: 0 }, { transform: 'scale(1)', opacity: 1 }], { duration: ms('--dur-base'), easing: ease('--ease-enter') });
  layer.querySelector('.ok-p').animate([{ strokeDashoffset: 40 }, { strokeDashoffset: 0 }],
    { duration: ms('--dur-slow'), delay: 120, easing: ease('--ease-enter'), fill: 'backwards' });
  const COLORS = ['#2563EB', '#27272A', '#93B4F5', '#A1A1AA'];          // 纯色，取自主题阶与中性色
  for (let i = 0; i < 14; i++) {
    const c = Object.assign(document.createElement('span'), { className: 'cf' });
    c.style.background = COLORS[i % COLORS.length]; layer.append(c);
    const dx = (Math.random() - 0.5) * 220, dy = -30 + Math.random() * 150, rot = (Math.random() - 0.5) * 540;
    c.animate([{ transform: 'translate(0,0) rotate(0deg)', opacity: 1 }, { transform: `translate(${dx}px, ${dy}px) rotate(${rot}deg)`, opacity: 0 }],
      { duration: 900 + Math.random() * 300, easing: ease('--ease-enter'), fill: 'forwards' }).finished.then(() => c.remove(), () => {});
  }
}
```

**降级**：显示静态对勾，不放彩屑，文字照旧。

**性能与可访问性**：`stroke-dashoffset` 不是合成属性，但只有一条很短的路径，可以接受；彩屑只动 `transform` 与 `opacity`，结束就移除，数量不超过 14；彩屑旋转属于运动，降级时必须去掉。每秒闪烁不超过 3 次。

**常见翻车**：加发光或光芒；彩屑盖住“完成”按钮；把普通保存也做成大动画；动画长于 2.4 秒；只有动画没有文字；每次进入页面都重放。

---

## 配方 11：滚动联动

**用在哪**：顶栏随滚动变实、变阴影，头图折叠。

**感受目标**：内容滚上来时，栏“自然地”从透明变成有质感的一层，头图安静地退后。

**编排**：

| 谁 | 做什么 | 范围 | 曲线 |
| --- | --- | --- | --- |
| 栏的白底层、阴影层、标题 | `opacity` 0 到 1 | 滚动 0–96 像素 | 线性（进度就是手指） |
| 头图内容 | 上移 16 像素、缩到 0.9、淡到 0.3 | 滚动 0–160 像素 | 线性 |

静止时栏贴在底面，只有 1 像素分隔线或完全透明地叠在头图上；内容滚到它下面之后才升到第 3 级阴影（规范）。阴影用伪元素的 `opacity` 去显隐，不去动画 `box-shadow`（后者每帧重绘）。

**毛玻璃顶栏**：默认不用。风格矩阵里毛玻璃的“避免”项包含控制器表面，已确认的作用范围只有头图装饰与入口图标；视觉规范对半透明玻璃与背景模糊的表述是界面里一律不用，减少动态效果的降级表还要求去掉背景模糊的变化。所以本配方的顶栏用实色白底加第 3 级阴影。只有用户在视觉审批里选定了毛玻璃风格、并且作用范围含头图装饰时，才能把它用在头图上的装饰块上，且 `backdrop-filter` 本身不做动画，只动那一层的 `opacity`。想把毛玻璃扩到吸顶栏要用户单独裁定（第 8 条）。

**代码**（优先：CSS 滚动驱动动画）：

```css
.scroller { position: absolute; inset: 0; overflow-y: auto; scroll-timeline: --page block; }   /* 具名时间线，见下面的翻车 */
.bar { position: sticky; top: 0; z-index: 2; height: 56px; margin-bottom: -56px; display: flex; align-items: center; }
.bar::before, .bar::after { content: ""; position: absolute; inset: 0; opacity: 0; z-index: -1; pointer-events: none; }
.bar::before { background: #fff; border-bottom: 1px solid var(--line); }
.bar::after { box-shadow: var(--e3); z-index: -2; }
.bar-title { opacity: 0; }
@keyframes bar-in { from { opacity: 0; } to { opacity: 1; } }
@keyframes hero-fold { to { transform: translateY(-16px) scale(0.9); opacity: 0.3; } }
.sda .bar::before, .sda .bar::after, .sda .bar-title { animation: bar-in linear both; animation-timeline: --page; animation-range: 0 96px; }
.sda .hero-in { animation: hero-fold linear both; animation-timeline: --page; animation-range: 0 160px; transform-origin: 50% 100%; }
@media (prefers-reduced-motion: reduce) { .sda .hero-in { animation: none; } }   /* 栏变实保留，头图位移缩放去掉 */
html[data-rm] .sda .hero-in { animation: none; }
```

**代码**（不支持时：IntersectionObserver）：

```js
const sda = CSS.supports('animation-timeline: scroll()');
scroller.classList.add(sda ? 'sda' : 'no-sda');
if (!sda) {
  const io = new IntersectionObserver(([e]) => bar.classList.toggle('stuck', !e.isIntersecting), { root: scroller, threshold: 0 });
  io.observe(sentinel);        // 滚动内容顶部一个 1px 的绝对定位哨兵，不占布局
}
```

```css
.no-sda .bar::before, .no-sda .bar::after, .no-sda .bar-title { transition: opacity var(--dur-fast) var(--ease-standard); }
.no-sda .bar.stuck::before, .no-sda .bar.stuck::after, .no-sda .bar.stuck .bar-title { opacity: 1; }
```

回退路径是“一步到位”的状态切换，不是随滚动连续变化，这是它与滚动驱动版本的区别。

**降级**（减少动态效果）：头图折叠的位移与缩放去掉；栏变实、阴影出现保留（不透明度的变化不是运动）。

**性能与可访问性**：滚动驱动动画只动 `transform`、`opacity` 时可以跑在合成器上，不需要监听 `scroll` 事件，主线程再忙也不会卡栏。回退里只用 IntersectionObserver，不在 `scroll` 事件里读布局再写样式。

**常见翻车**：`scroll()` 找的是最近的“滚动容器”，祖先里只要有 `overflow: hidden`（哪怕它不滚）就命中它，动画永远停在进度 0。做演示时就踩到了：头图外层写了 `overflow: hidden`。解决：用 `scroll-timeline: --page block` 加 `animation-timeline: --page` 具名绑定，或把头图的 `overflow: hidden` 改成 `overflow: clip`（实测：改成 `clip` 后 `scroll()` 就能找到外层滚动容器，`hidden` 不行）；`animation-timeline` 写在 `animation` 简写之前会被简写重置；对 `box-shadow` 做滚动联动；哨兵用 `height` 撑开布局；在 `scroll` 事件里读 `getBoundingClientRect` 再写样式。

---

## 配方 12：手势跟手（侧滑删除与下拉刷新）

**用在哪**：列表行侧滑出删除、下拉刷新。

**感受目标**：手指怎么动，东西怎么动，没有一点延迟；松手后平稳落到位，不弹。

**编排**（基本模型）：

| 阶段 | 做什么 |
| --- | --- |
| 按下 | `setPointerCapture`，记起点；加“跟手中”标记（关掉过渡） |
| 移动 | 位置等于手指，没有缓动、没有时长；越过边界时加阻力（拖多少走 30%） |
| 松手 | 按位置或最近 80 毫秒内的速度决定终点；去掉“跟手中”，让 CSS 过渡从当前位置走到终点 |
| 终点动画 | `--dur-base`，标准曲线，不过冲 |
| 中断 | `pointercancel` 与松手同样处理，不能卡在中间态 |

**代码**（侧滑删除）：

```css
.srow { position: relative; height: 56px; overflow: hidden; border-radius: 8px; background: var(--press); }
.srow-act { position: absolute; inset: 0; display: flex; justify-content: flex-end; visibility: hidden; transition: visibility 0s linear var(--dur-base); }
.srow.reveal .srow-act { visibility: visible; transition-delay: 0s; }
.srow-main {
  position: relative; height: 100%; background: #fff; touch-action: pan-y; user-select: none;       /* 竖向留给浏览器滚动 */
  transform: translateX(var(--sx, 0px));
  transition: transform var(--dur-base) var(--ease-standard), opacity var(--dur-base) var(--ease-exit);
}
.srow-main.dragging { transition: none; }
```

```js
const W = 88;                                                       // 操作区宽度
let d = null;
const setState = (s) => {
  row.dataset.state = s; row.classList.toggle('reveal', s !== 'closed');
  main.style.setProperty('--sx', s === 'open' ? -W + 'px' : s === 'deleted' ? '-100%' : '0px');
};
main.addEventListener('pointerdown', (e) => {
  main.setPointerCapture(e.pointerId);
  d = { x0: e.clientX, base: row.dataset.state === 'open' ? -W : 0, x: 0, last: e.clientX, lt: performance.now(), v: 0 };
  main.classList.add('dragging'); row.classList.add('reveal');
});
main.addEventListener('pointermove', (e) => {
  if (!d) return;
  const now = performance.now();
  d.v = (e.clientX - d.last) / ((now - d.lt) || 1); d.last = e.clientX; d.lt = now;
  let x = d.base + (e.clientX - d.x0);
  if (x > 0) x *= 0.3; if (x < -W) x = -W + (x + W) * 0.3;          // 越界有阻力
  d.x = x; main.style.setProperty('--sx', x + 'px');
});
const end = () => {
  if (!d) return;
  const v = performance.now() - d.lt > 80 ? 0 : d.v;                // 停住再松手，速度算 0
  const open = v < -0.4 ? true : v > 0.4 ? false : d.x < -W / 2;
  d = null; main.classList.remove('dragging');
  setState(open ? 'open' : 'closed');                              // 设 --sx 为 -88px 或 0，CSS 过渡接着走
};
main.addEventListener('pointerup', end); main.addEventListener('pointercancel', end);
main.addEventListener('keydown', (e) => {                          // 等价的键盘操作（规范要求）
  if (e.key === 'ArrowLeft') setState('open'); else if (e.key === 'ArrowRight') setState('closed'); else if (e.key === 'Delete') setState('deleted');
});
```

删除后原位显示“已删除，撤销”（高度不变），不要把行收起来：行高一收，下面所有行都在动，既产生布局偏移，也不给反悔的机会。

**下拉刷新的模型**（没有做过演示，没有实测）：只在 `scrollTop` 为 0 且手指向下拖时接管；指示器位置取手指位移的约一半（阻尼），拖过阈值（如 64 像素）松手就停在加载位（如 48 像素）显示转圈，数据回来后用 `--dur-base` 加标准曲线回到 0；没拖过阈值直接回到 0。垂直拖动与浏览器自己的滚动与原生下拉刷新会抢手势，需要 `overscroll-behavior-y: contain`，并且要处理触摸事件的取消（用 `touchmove` 非被动监听加 `preventDefault`，或让浏览器滚动与自管滚动二选一）。这一段动手前先在目标 WebView 里做原型实测。

**降级**：跟手保留，因为它是手指在动；松手后的回位改为直接切换或不超过 150 毫秒的淡入；等价操作（按钮、键盘）必须有。

**性能与可访问性**：`pointermove` 里只写一个 CSS 变量，不读布局；`touch-action` 要声明，否则浏览器会抢走手势并发来 `pointercancel`；等价操作缺失会让键盘与读屏用户无法删除。

**常见翻车**：松手后用弹簧或回弹曲线过冲（规范禁止）；跟手阶段还带着 `transition`，手指与元素之间有粘滞感；速度取整个拖动的平均值，停住再松手还被判成快甩；漏掉 `pointercancel`；删除后把行高收起；没有等价的键盘操作。

---

## 配方 13：轻提示与按钮加载态

**用在哪**：保存、提交、复制等普通操作的反馈。

**感受目标**：点了就知道“在处理”，处理完轻轻告诉一声，不打扰。

**编排**：

| 谁 | 做什么 | 时长 | 曲线 |
| --- | --- | --- | --- |
| 按钮 | 进入加载态：内部转圈，禁用防重复提交，宽度不变 | 转圈用线性 | 线性 |
| 提示出现 | `opacity` 0 到 1，上移不超过 8 像素 | `--dur-fast`（100–150） | 进入 |
| 提示停留 | 示例值 2.4 秒，不挡下一步 | — | — |
| 提示退出 | 淡出 | `--dur-instant` | 退出 |

提示是第 3 级阴影的浮层，绝对定位或固定定位，不推开任何内容。

**代码**：

```js
let toast = null, timer = 0;
btn.addEventListener('click', () => {
  if (btn.getAttribute('aria-busy') === 'true') return;           // 防重复提交
  btn.setAttribute('aria-busy', 'true');                          // 不用 disabled：焦点不会丢
  const sp = Object.assign(document.createElement('span'), { className: 'spin' }); sp.setAttribute('aria-hidden', 'true');
  btn.prepend(sp); label.textContent = '保存中';
  save().then(() => { sp.remove(); btn.removeAttribute('aria-busy'); label.textContent = '保存'; show('已保存'); });
});
function hide() {
  if (!toast) return;
  const t = toast; toast = null; clearTimeout(timer);
  leave(t, rm() ? { opacity: 0 } : { opacity: 0, transform: 'translateY(-8px)' }, { duration: ms('--dur-instant'), easing: ease('--ease-exit') })
    .finished.then(() => t.remove(), () => t.remove());
}
function show(text) {
  hide();                                                         // 同时只留一条，替换而不是堆叠
  const t = Object.assign(document.createElement('div'), { className: 'toast', textContent: text }); t.setAttribute('role', 'status');
  stage.append(t); toast = t;
  enter(t, rm() ? { opacity: 0 } : { opacity: 0, transform: 'translateY(-8px)' }, { duration: ms('--p-toast'), easing: ease('--ease-enter') });
  timer = setTimeout(hide, 2400);
}
```

```css
.save { min-width: 132px; }                                       /* 文字变化时宽度不变 */
.spin { width: 16px; height: 16px; border-radius: 50%; border: 2px solid rgb(255 255 255 / 40%); border-top-color: #fff; animation: spin 800ms linear infinite; }
@keyframes spin { to { transform: rotate(360deg); } }
.toast { position: absolute; left: 12px; right: 12px; top: 12px; margin: 0 auto; width: max-content; background: #fff; border: 1px solid var(--line); border-radius: 12px; box-shadow: var(--e3); padding: 10px 16px; }
```

**降级**：转圈保留，它是进度信息，只是不加弹跳；提示去掉位移，只淡入淡出。

**性能与可访问性**：转圈只动 `transform`；`role="status"` 让读屏播报“已保存”，文字本身就是信息；提示不抢焦点；同时只留一条。转速 800 毫秒一圈是示例值，规范只规定曲线是线性。

**常见翻车**：把按钮文字换成“保存中…”后宽度变了，整行跳；用 `disabled` 属性让焦点丢失；提示用 `top` 做动画；提示遮住下一步操作，或消失太快读不完；多条提示堆叠把页面推开；转圈用了缓动曲线。

---

## 动效个性

个性是在令牌之内的取值偏好，不是新的动效系统。三种个性只在规范给了区间的位置挪动；规范写死的值（二级页 280–320、对话框 240、底部弹层 280、关闭 160、标签下划线 200、骨架流光 1.2 秒）不随个性变，也不允许任何个性突破规范的区间。

| 槽位 | 规范区间 | 沉稳 | 利落 | 亲和 |
| --- | --- | --- | --- | --- |
| 按压反馈 | 100–150 | `--dur-fast` | `--dur-instant` | `--dur-fast` |
| 标签内容淡入 | 150–200 | `--dur-base` | `--dur-fast` | `--dur-fast` |
| 轻提示出现 | 100–150 | `--dur-fast` | `--dur-instant` | `--dur-fast` |
| 加购飞行 | 不超过 300 | `--dur-slow` | `--dur-base` | `--dur-slow` |
| 逐项间隔 | 20–40 毫秒 | 40（8 项时收到 34） | 20 | 30 |
| 数字计数 | 800–1000 毫秒 | 1000 | 800 | 900 |
| 进入曲线 | 进入令牌 | `--ease-enter` | `--ease-enter` | `--ease-soft`（提议令牌） |
| 移动曲线 | 标准令牌 | `--ease-standard` | `--ease-standard` | `--ease-standard` |

- 沉稳：偏用 200 与 300、标准曲线。适合金融、医疗、后台、B2B 工具。
- 利落：偏用 100 与 150。适合工具、效率类、高频操作的产品。
- 亲和：偏用 150 与 200，进入曲线更长的减速。适合消费、健身、母婴、生活服务。

**提议的新令牌（需用户裁定，第 1 条）**：`--ease-soft: cubic-bezier(0.22, 1, 0.36, 1)`，一条不过冲的缓出（两个控制点的纵坐标都是 1，曲线从不越过终点），比 `--ease-enter` 的减速尾巴更长。没有裁定之前只在“亲和”个性里使用，并且只用于进入。

```css
:root { --ease-soft: cubic-bezier(0.22, 1, 0.36, 1);   /* 提议令牌 */
  --p-press: var(--dur-fast); --p-fade: var(--dur-base); --p-toast: var(--dur-fast); --p-fly: var(--dur-slow); --p-step: 40; --p-count: 1000; --ease-in-p: var(--ease-enter); }
html[data-feel="sharp"] { --p-press: var(--dur-instant); --p-fade: var(--dur-fast); --p-toast: var(--dur-instant); --p-fly: var(--dur-base); --p-step: 20; --p-count: 800; }
html[data-feel="warm"]  { --p-press: var(--dur-fast); --p-fade: var(--dur-fast); --p-toast: var(--dur-fast); --p-fly: var(--dur-slow); --p-step: 30; --p-count: 900; --ease-in-p: var(--ease-soft); }
```

个性变量只在使用处出现（`var(--p-press)` 等），配方代码里不散落数值；减少动态效果时个性被令牌的降级值盖掉，因为 `--p-*` 引用的是令牌本身。同一个产品只选一种个性，不在页面之间切换。

---

## 性能预算

**只动合成属性**。位移、缩放、出现消失只用 `transform` 与 `opacity`。状态层级的切换可以动 `box-shadow`、`border-color`、`background-color`，限于小面积；不对 `width`、`height`、`left`、`top`、`margin`、`padding` 做过渡，折叠展开用网格行高或高度；`filter` 与 `backdrop-filter` 不做动画。仅有的例外是配方 10 的对勾描边（一条很短的路径），以及 View Transitions 的快照组（浏览器内部动画，待用户裁定第 7 条）。

**同时在动的元素数（建议上限，非规范，待用户裁定第 10 条）**：

| 场景 | 建议上限 |
| --- | --- |
| 一屏里同时在动的元素 | 8 个，其中整屏大面积的层不超过 2 个（二级页的 A、B） |
| 列表逐项进入 | 8（规范） |
| 加购飞行 | 3 |
| 彩屑 | 14 |
| 同屏骨架流光块 | 12 |
| 无限循环动画 | 只有转圈与骨架流光，且只在加载态 |

**`will-change`**：规范的立场是“最后手段，只在已出现性能问题的元素上临时设置”，稳定显示一节还写了“不写 `will-change`”；`audit_rendered.py` 对样式表里出现的任何 `will-change` 都报错（它只读样式表，不读脚本临时写的内联值）。

- 可以临时加的情形：已经用性能记录证实某个元素的首帧掉帧（动画第一帧才提升合成层），并且只给这一个元素；在动画开始前一帧由脚本设置，动画 `finished` 后立刻清掉。
- 不能保留的情形：写在样式表里常驻；给列表的每一项、给多个元素加；给 `all` 或布局属性加；加了没有记录证明它有效。
- 为什么这样：它会让元素提前占用合成层内存，创建层叠上下文，并成为 `position: fixed` 子元素的包含块，副作用大于收益。大多数时候用 `transform` 或 `opacity` 做的 WAAPI 与过渡，浏览器在动画开始时就会自己提升合成层，用不着它。
- 临时设置绕不绕得过检查不是重点；规则是“出现问题才用、用完就撤”，不要为了过检查去绕。是否接受脚本临时设置见待用户裁定第 11 条。

**长列表不动画**：超过一两屏的列表、虚拟滚动的列表，滚动时进入视口的项不播入场动画；入场逐项进入只给首屏的前 8 项。长页面的屏外分段用 `content-visibility: auto` 加 `contain-intrinsic-size`，给占位尺寸，避免滚动条跳。

**其他预算**：每帧约 16.7 毫秒；动画期间不得有超过 50 毫秒的长任务；累计布局偏移不超过 0.05（规范，`audit_stability.py` 量）；不在动画回调里交替读写布局；动画开始前图片先解码并写好宽高。

---

## 验收方法

三层，从便宜到贵。

**第一层：静态与渲染检查**（规则卡“交付前必须通过”）：

```text
py -X utf8 scripts/check_document.py <页面.html> --allow interface
py -X utf8 scripts/audit_rendered.py <页面.html> --width 390 --min-font 12
py -X utf8 scripts/audit_rendered.py <页面.html> --width 390 --min-font 12 --reduced-motion
py -X utf8 scripts/audit_stability.py <页面.html> --width 390
```

`audit_rendered.py` 只量打开那一刻的页面；弹层、详情页、提示这些点了才出现的状态，用它的 `--walk` 选项写一个 `walk(page, scan)` 点一遍再量。

**第二层：运行时测量**。用 Playwright 点每个动效，在页面里用 `PerformanceObserver` 记长任务与布局偏移，再用 `requestAnimationFrame` 的间隔算丢帧。下面的脚本可以直接复制。

```python
# motion_probe.py   py -X utf8 motion_probe.py <页面> [宽度]
import json, sys
from playwright.sync_api import sync_playwright

INIT = r"""
(() => {
  const P = window.__probe = { long: [], shifts: [], loaf: [] };
  const watch = (type, fn) => { try { new PerformanceObserver((l) => l.getEntries().forEach(fn)).observe({ type, buffered: true }); } catch (e) { P[type] = 'unsupported'; } };
  watch('longtask', (e) => P.long.push({ at: Math.round(e.startTime), ms: Math.round(e.duration) }));
  watch('layout-shift', (e) => { if (!e.hadRecentInput) P.shifts.push({ at: Math.round(e.startTime), value: e.value }); });
  watch('long-animation-frame', (e) => P.loaf.push({ at: Math.round(e.startTime), ms: Math.round(e.duration) }));   // 不支持时忽略
  window.__frames = () => {                       // 返回“停止并取结果”的函数
    const gaps = []; let last = performance.now(), on = true;
    const f = (t) => { gaps.push(t - last); last = t; if (on) requestAnimationFrame(f); };
    requestAnimationFrame(f);
    return () => { on = false; return gaps.slice(2); };    // 头两个间隔含采样器启动，丢掉
  };
})();
"""

def probe(url, steps, width=390, reduced=False):
    """steps: [(名称, 动作函数(page))]；返回每步的长任务、布局偏移与丢帧数。"""
    out = []
    with sync_playwright() as pw:
        browser = pw.chromium.launch(channel="msedge")            # 没有 Edge 就用 pw.chromium.launch()
        ctx = browser.new_context(viewport={"width": width, "height": 844}, locale="zh-CN",
                                  reduced_motion="reduce" if reduced else "no-preference")
        ctx.add_init_script(INIT)
        page = ctx.new_page()
        page.goto(url); page.wait_for_timeout(1000)
        for name, act in steps:
            l0 = page.evaluate("__probe.long.length"); s0 = page.evaluate("__probe.shifts.length")
            # 注意：evaluate 的表达式如果“返回一个函数”，Playwright 会去调用它。这里用括号包一层，不返回函数。
            page.evaluate("(() => { window.__stop = __frames(); })()")
            act(page)
            gaps = page.evaluate("window.__stop()")
            out.append({
                "step": name, "frames": len(gaps), "max_gap_ms": round(max(gaps), 1) if gaps else 0,
                "dropped_33ms": sum(1 for g in gaps if g > 33.4), "dropped_50ms": sum(1 for g in gaps if g > 50),
                "long_tasks": page.evaluate(f"__probe.long.slice({l0})"),
                "layout_shifts": page.evaluate(f"__probe.shifts.slice({s0})"),
            })
        ctx.close(); browser.close()
    return out

if __name__ == "__main__":
    url = sys.argv[1]
    steps = [("点按钮", lambda p: (p.locator("#open").click(), p.wait_for_timeout(600)))]   # 换成你的动作
    print(json.dumps(probe(url, steps, int(sys.argv[2]) if len(sys.argv) > 2 else 390), ensure_ascii=False, indent=1))
```

通过线（建议，写进验收记录）：交互期间长任务 0 个，布局偏移合计 0（规范上限 0.05），每个动画丢帧（间隔超过 33.4 毫秒）不超过 2 帧，超过 50 毫秒的间隔 0 次。无头浏览器是软件渲染，数字偏保守，只能证明没有明显的主线程问题，真机的合成与掉帧要在目标 WebView 里另测（Chrome 远程调试看 Android，Safari 网页检查器看 iOS，微信用它自己的真机调试面板）。

**第三层：录性能记录**（需要看是哪一帧、哪段脚本慢时）：

```python
browser = pw.chromium.launch(channel="msedge")
page = browser.new_page()
browser.start_tracing(page=page, path="trace.json", screenshots=True)    # 只在 Chromium 内核可用，参数必须写成关键字
page.goto(url); page.locator("#open").click(); page.wait_for_timeout(800)
browser.stop_tracing()                                              # 用 DevTools 的 Performance 面板或 Perfetto 打开 trace.json
```

Playwright 的 `context.tracing` 与 trace 查看器记的是操作与截图，不含帧耗时，不能替代上面这条。

**减少动态效果的复测**：Playwright 用 `reduced_motion="reduce"` 开新环境（或 `page.emulate_media(reduced_motion="reduce")`），再点一遍：位移与缩放的元素 `getComputedStyle(el).transform` 应为 `none`，`el.getAnimations()` 里不应有位移与缩放的动画，彩屑与描线不出现，流光停止，转圈保留。

**可打断的复测**：在动画进行到一半（约 100 毫秒）时再次操作（返回、关闭、连点），元素应从当前位置反向，最终位置准确，没有跳变，没有残留的 `forwards` 填充。

**实测记录（2026-11-04，Windows 11，Edge 156 的 Chromium 内核，Playwright）**：13 个配方演示在 390 与 1280 两个宽度、沉稳/利落/亲和三种个性、系统与手动减少动态效果、以及“没有 View Transitions 与滚动驱动动画”的降级路径下各点一遍：交互期间长任务 0 个，布局偏移 0；12 轮共约 21500 帧，间隔超过 33.4 毫秒的 1 帧（33.4 毫秒），超过 50 毫秒的 0 帧；`audit_rendered.py` 在 390 与 1280、浅色、有无减少动态效果、以及点开各状态的 `--walk` 下都是 `audit: ok`；View Transitions 在 Chromium 内核里跑通（`ready` 兑现，快照组含 `hero`），删掉 `document.startViewTransition` 后 FLIP 分支同样通过。页面首次加载有一个约 85–115 毫秒的长任务，把页面里的汉字替换成同一个字之后它消失，是该机器上首次排版大量不同汉字的字体回退开销，与动效无关。没有测的：微信 WebView（任何版本）、iOS Safari、真机帧率、下拉刷新、小程序原生页面。

---

## 待用户裁定的事项

凡是超出现有规范的建议都在这里。裁定之前，本文按“默认”一列写。

| 序号 | 事项 | 本文的默认做法 |
| --- | --- | --- |
| 1 | 提议的新令牌 `--ease-soft: cubic-bezier(0.22, 1, 0.36, 1)` 是否并入缓动令牌 | 只在“亲和”个性里用，只用于进入 |
| 2 | 场景表里的 240（对话框）、280（底部弹层）、160（关闭）是否正式列为令牌，或并入 200 与 300；另外关闭 160 相对 240、280 只有 57%–67%，低于“退出取进入 70%–80%” | 用场景表数值；退出配对以场景表为准 |
| 3 | 二级页返回的时长：场景表写“与进入相同”，细则写“退出取进入的 70%–80%” | 按场景表，返回与推入同为 `--dur-slow` |
| 4 | 轻提示退出 100 对进入 150 是 67%，低于 70%，令牌里没有 105–120 | 用 `--dur-instant` |
| 5 | “时长个性”是否成为产品级设置（写进主题库）或只是设计师选型；任何个性都不得突破规范区间 | 只是选型，一个产品选一种 |
| 6 | 减少动态效果下，是令牌“接近 0”（直接切换）还是“不超过 150 毫秒的淡入” | 推荐淡入（令牌收到 150，位移缩放归零）；直接切换是最小降级 |
| 7 | View Transitions 的快照组由浏览器内部动画 width 与 height（不是 `transform`、`opacity`），是否视为合规；转场期间页面不接收指针事件，用“点一下就 skip”补打断；View Transitions 是否作首选、FLIP 作降级；微信 WebView 不支持或表现不对时是否一律走 FLIP | 首选 View Transitions，特性检测不过走 FLIP，点击即跳到终态 |
| 8 | 毛玻璃是否可以用在吸顶栏（现状：风格矩阵避免控制器表面，视觉规范禁玻璃与背景模糊，降级表要求去掉背景模糊变化） | 不用，顶栏用实色加第 3 级阴影 |
| 9 | 头图折叠（滚动联动的缩放、位移、淡出）属于“视差”，规范降级表有这一行，意味着非降级时允许；幅度是否需要限定 | 允许，位移不超过 16 像素、缩放不低于 0.9，降级时去掉 |
| 10 | “同时在动的元素数”建议上限（8、2、3、14、12）是否写进规范与检查脚本 | 只作建议 |
| 11 | `will-change`：脚本临时设置、结束清除是否允许；是否让 `audit_rendered.py` 检查运行时残留 | 允许临时设置，必须有性能记录证明，结束必须清除 |
| 12 | 数字的 `transform` 滚动数位是否作为规范外的新写法允许（规范只写“从 0 计数到目标值”） | JS 计数为默认，滚动数位限于一个核心指标 |
| 13 | 彩屑数量（14）、时长（约 1.2 秒）、轻提示停留（2.4 秒）、转圈转速（800 毫秒一圈）都是示例值，规范只给了上限或曲线 | 按示例值，实际以规范与 Luz-System“浮层与反馈”为准 |
| 14 | 手势常数：松手阈值 30%、速度阈值 0.5 与 0.4 像素每毫秒、速度过期 80 毫秒、越界阻力 0.3、下拉阻尼 0.5 | 实现常数，不是规范 |
| 15 | 小程序原生页面（非 WebView）的动效实现不在本文范围；是否另写一版原生配方（页面栈转场、共享元素组件、`wx.createAnimation` 与动画 API、WXS 响应事件做手势；这些名称凭印象写出，动手前先核对微信官方文档与基础库版本） | 本文只覆盖浏览器与 WebView 里的页面 |
| 16 | 骨架屏出现的时机（请求多快回来就不出骨架）以规范“骨架屏”一节为准；本文只写了“至少停留 500 毫秒” | 按规范原文 |
| 17 | 逐项延迟的两条界线在 8 项且间隔 40 毫秒时冲突（7 乘 40 超过 240） | 取更严的：间隔收到 `floor(240 ÷ 6)` 不超过 34 毫秒 |
| 18 | 个性变量 `--p-*` 与 `data-feel` 属性是否作为 ui-kit 的正式接口 | 只在本文的演示与配方里使用，不改 ui-kit |
