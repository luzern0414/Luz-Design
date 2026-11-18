# 幻灯片模板

六个 16:9 基础模板各有描述文件（`specs/`）和生成样例（`samples/`），另有 16 个可复用块（`specs/parts/`）。已有样例采用花卉业务、雾粉主题和浅色底。按任务选择版式与品牌色，演示建议见 [演示设计](../../../references/design/slides.md)。更多风格和许可条件见 [商用演示模板](commercial-sources.md)。

## 编号与命名

| 对象 | 编号 | 文件名 |
|---|---|---|
| 模板 | `DC-SL-001` 起，三位序号 | `samples/DC-SL-001-工作汇报.pptx`，描述文件 `specs/DC-SL-001-工作汇报.json` |
| 可复用块 | `DC-SL-P01` 起 | `specs/parts/DC-SL-P01-封面.json` |

编号、中文名、用途、命令登记在 `manifest.json`，文件模板库目录页读它。

## 目录

```
slides/
  README.md
  manifest.json            登记表：items（模板）与 parts（可复用块）
  build_slides.py          生成器：读描述文件，写 pptx
  specs/DC-SL-NNN-名称.json   模板的描述文件
  specs/parts/DC-SL-PNN-名称.json   可复用块，一个版式一份内容
  samples/DC-SL-NNN-名称.pptx   用生成器做出的样例，8 至 12 页
  samples/previews/DC-SL-NNN-名称.jpg   目录页用的四页预览图，由样例导出的 PDF 拼成
```

## 模板

| 编号 | 名称 | 页数 | 用在哪 |
|---|---|---|---|
| DC-SL-001 | 工作汇报 | 9 | 周度或月度工作汇报 |
| DC-SL-002 | 方案提案 | 10 | 服务或产品方案提案 |
| DC-SL-003 | 培训课件 | 11 | 员工培训，含两个章节页 |
| DC-SL-004 | 产品介绍 | 10 | 商品系列与价格介绍 |
| DC-SL-005 | 门店路演 | 10 | 品牌与门店宣讲 |
| DC-SL-006 | 季度复盘 | 10 | 目标、构成与经验复盘 |

样例内容是虚拟店铺“花间集”的数字和文字，不对应真实公司和日期，使用时整页替换。

## 版式与字段

描述文件是 JSON：`{"id", "name", "theme", "title", "slides": [ {"layout": "...", ...} ]}`。`theme` 取 `rose`（默认）`coral` `orange` `green` `teal` `blue` `purple` `graphite`，色值读 `../../../kit/tokens.css`，不在脚本里另存一份。图片名写 `kit/assets/photo/` 里不带扩展名的文件名（如 `bouquet-rose`），带斜杠时按 `assets/` 下的路径取（如 `marks/mark-003`）；三维图标写 `icon`（如 `bag`）。

| 版式 | 名称 | 字段 | 约束 |
|---|---|---|---|
| `cover` | 封面 | `title` `image` `alt` `focus` | 默认左方主标题、右方配图。较长标题按实际文本框空间处理 |
| `section` | 章节页 | `title` `number` `image` `line` | 标题写成结论，不写“第一部分”这类板块名 |
| `bullets` | 要点页 | `title` `points` `image` 或 `stat` `numbered` | 要点 1 至 6 条；有先后顺序时 `numbered: true` |
| `two-column` | 双栏对比 | `title` `left` `right`（各含 `head` `points`） | 每栏 1 至 5 条 |
| `image-text` | 图文页 | `title` `image` `side` `head` `points` `badge` | 要点 1 至 4 条；`side` 取 `left` 或 `right` |
| `table` | 表格页 | `title` `columns`（`text` `width` `align`） `rows` | 2 至 5 列，1 至 6 行；金额列写 `"align": "right"` |
| `chart` | 图表页 | `title` `chart` `stat` | `chart.type` 取 `column` `bar` `line` `doughnut` `pie`；原生图表，可在软件里改数据 |
| `quote` | 引言页 | `title` `quote` `who` `role` `mark` `image` | 引言最多 3 行 |
| `end` | 结束页 | `title` `points` `image` | 写成结论，要点最多 3 条 |
| `steps` | 流程页 | `title` `steps`（`head` `text`） | 3 至 5 步 |
| `stats` | 数据页 | `title` `items`（`icon` `label` `value` `unit` `delta` `tone`） | 2 至 4 项；`tone` 取 `up` `down` `flat` |

`stat` 是旁边的重点数据卡：`{"icon", "label", "value", "unit"}`。图表页的 `chart` 含 `caption`（图表标注，写对象和单位）`categories` `series`（`name` `values`）`number_format` `min` `max`。

## 怎么换内容

1. 复制一份 `specs/DC-SL-NNN-名称.json`，改 `id` 和 `name`（按新编号命名），或直接改标题、要点、数字、图片名。
2. 想换版式，从 `specs/parts/` 里复制对应块的内容，放进 `slides` 数组。
3. 换主题色：改 `theme`，或生成时加 `--theme green`。
4. 重新生成并检查（见下）。

## 生成

命令从仓库根目录运行：

```
py -X utf8 templates/documents/slides/build_slides.py templates/documents/slides/specs/DC-SL-001-工作汇报.json templates/documents/slides/samples/DC-SL-001-工作汇报.pptx
py -X utf8 templates/documents/slides/build_slides.py --all
```

`--all` 把 `specs/` 里每个模板生成到 `samples/`。生成器会提示标题折行、正文超高或表格超宽。放映时检查实际边界，按需扩大文本框或换版式。使用 `--strict` 可将提醒作为本次构建失败条件。可复用块也能直接生成一页预览。

## 检查

```
py -X utf8 scripts/check_document.py templates/documents/slides/samples/DC-SL-001-工作汇报.pptx
```

六个样例都是零错误零提醒。正式交付走 `scripts/deliver.py` 和汇总页，不直接拷贝样例。块的单页预览会被检查脚本当成封面，不单独过检；块装进整份文件后再检查。放映时逐页目检：每页一个结论，没有溢出和重叠。

## 落实的规则

- 画面 13.333 × 7.5，所有页面浅色底；页边距 0.75 英寸，不少于画面宽度 5%。
- 基础样例的字阶是 40、28、20、18 磅，字体用微软雅黑。成稿使用项目语言和适合内容与观看条件的字阶。
- 每页使用一个主标题占位符。页码占位符随页序更新。
- 按当页主题选择内容密度，图表、数字、正文和来源分清主次。
- 图片带替代文字，表格设表头行，图表框带数据摘要；阅读顺序与视觉顺序一致。
- 没有目录页、议程页、“谢谢”页、日期页脚和演讲提示；结束页写结论。需要这些页时用户明确提出，检查时加 `--allow accessory`。
- 现有样例用浅色画布及主色变体。设计成稿可用 [商用模板](commercial-sources.md) 的多色母版，按照品牌安排承托色和强调色。

## 已知限制

- 本机没有 PowerPoint 和 LibreOffice，看图用的是 WPS 演示导出的 PDF；在 PowerPoint 里的排版、圆角和图表图例位置可能有细微差别，换机器后请再放映一遍。
- 行数靠微软雅黑字体文件量字估算；没有该字体的机器上按字宽估算，误差更大。
- 图表是原生图表，圆环图例位置由软件自行排布；不做三维、不做动画、不带演讲备注。
- 表格最多 6 行 5 列，更多内容拆页或改用表格文件。
- 图片先裁切成目标比例再嵌入，webp 会转成 jpeg 或 png；来源是 `../../../kit/assets/`，换成自己的图片时放进同一目录并在描述文件里写名称。
