<div align="center">

# Luz Design

为中文产出定视觉标准，做海报与品牌视觉，排报告、Excel、Word 等文件的版式。

![许可：PolyForm Noncommercial 1.0.0](https://img.shields.io/badge/%E8%AE%B8%E5%8F%AF-PolyForm%20Noncommercial%201.0.0-c2410c)
![类型：Agent Skill](https://img.shields.io/badge/%E7%B1%BB%E5%9E%8B-Agent%20Skill-475569)

</div>

## 能做什么

- **视觉标准**：配色从官方色板按行业气质取阶，附 18 个行业主题（含面向企业工具后台的石墨主题）；一条统一的中文字体栈、各类产出的字阶与七级字体角色（字重 400/600/700）；扁平图形（2 像素线性与双色图标、多层扁平插画）与五级层级的立体感（双层阴影、发丝线、按钮底边、遮罩）、圆角、间距与动效。其他 Luz 技能的界面都以此为准。
- **海报与品牌视觉**：活动海报、品牌主视觉、宣传图，规定安全区、文字层级、缩略图辨识与版权边界；照片可交给本机图像生成服务。
- **Excel 与 Word**：Excel 单工作表、12 磅起、无序号、分组名纵向合并、一格一事实；Word 按合同、方案、报告、会议纪要、公文分类排版。两者都由脚本直接生成。
- **其他文件**：阅读型网页、演示文稿、PDF、Markdown 的标题、字号、表格与图表规则。
- **自动检查**：拦截小字号、多字体、大面积深色、装饰渐变与立体效果、图标混用、文字头像、表格合并错误、合同缺项与占位文字；PDF 用 PyMuPDF 与逐页渲染核对。其他 Luz 技能也用它检查自己的页面。
- **经验沉淀**：记住用户偏好、有效的配色与字阶、踩过的坑，下次调用先查再做。

## 适合与不适合

| 适合交给本技能 | 改用 |
|---|---|
| 配色、字体、图标、间距等视觉标准 | — |
| 海报、品牌主视觉、宣传图 | — |
| 报告、Excel、Word、演示文稿、PDF 的版式 | — |
| 系统方案、后台与小程序界面、可交互原型、硬件选型 | [Luz-System](https://github.com/luzern0414/Luz-System) |
| 后端、接口、数据库、部署上线 | [Luz-Dev](https://github.com/luzern0414/Luz-Dev) |
| 文章、文案、协议条款等文字本身 | [Luz-Writing](https://github.com/luzern0414/Luz-Writing) |
| 网页检索与采集 | [Luz-Crawl](https://github.com/luzern0414/Luz-Crawl) |

## 快速开始

1. 把整个目录放进 Agent 的技能目录（例如 `~/.claude/skills/luz-design`）。
2. 安装 Python 3.11 及以上，以及生成与检查文件用的库（表格、Word、演示文稿、元素拼板切图）：

   ```bash
   pip install openpyxl python-docx python-pptx pillow numpy
   ```

   核对 PDF 时另装 `pymupdf`；校验脚本读技能说明的头部信息时用到 `pyyaml`（可选）。

3. 需要调研配色或规范时，另装 [Luz-Crawl](https://github.com/luzern0414/Luz-Crawl)；图片生成是可选能力，需要本机的图像生成服务。

然后直接提需求，例如：

- “做一张健身房周年庆的活动海报。”
- “把这份调研结果整理成一个单工作表的 Excel，类别合并、加浅色底。”
- “按这些条款排一份设备采购合同的 Word。”
- “这份方案的配色和字号按规范调整一下。”

## 工作方式

1. **先读规则卡**：`context.py <任务类型>` 一次给出这类任务的你的偏好、相关教训、规范原文、该用的工具和必须通过的检查；模板和生成脚本只是骨架，内容以规则卡为准。
2. **收集事实**：只记录用户给出的目的、对象、渠道、精确文案、尺寸与格式；缺文案或格式就先停下来问。
3. **建会话**：每个任务一个编号目录，工作文件放在 `raw/`，最终只交付一个文件。
4. **调研**：配色、字体或文件格式需要依据时，按 Luz-Crawl 的调用协议查官方色板、设计体系和标准，并写明依据。
5. **出稿**：视觉稿汇总在一个总览页里，**等用户批准**后才算定稿；文件先定类型，再按类型排版并导出。
6. **检查与交付**：在 BRIEF 里写明采用了哪些规则；表格和 Word 生成后自动检查，网页用检查脚本复核，零错误才交付；没写“采用的规则”的会话不能发布；改动过的产出需要重新批准。
7. **沉淀**：结束前把新的偏好、有效信息和教训写回经验库。

## 经验沉淀

Luz-System、Luz-Design、Luz-Dev、Luz-Writing 四个技能用同一套经验沉淀：经验库是 `experience/notes.json`，分偏好、教训、有效信息三类，按主题键更新而不是堆积；开始时用 `scripts/experience.py search` 查，结束前用 `note` 写。字段、上限与清理规则见 SKILL.md“每次调用后沉淀”。仓库公开，手机号、邮箱、微信号、个人目录路径、密钥与客户名称都不写进去。

本仓库另有整理好的配色、字阶、视觉与文件规则库 `patterns.json`（最多 200 条，用 `add` 批量写入）和来源库 `sources.json`。

## 目录结构

```text
SKILL.md        技能入口：分工、路由、规则摘要、每次调用后沉淀
WORKFLOW.md     各阶段的进入条件与停止条件
references/     视觉设计规范、文件设计规范、行业主题库、生图提示词与会话模板
experience/     经验库：用户偏好、教训、配色与字阶等模式、来源，以及生成的目录页
scripts/        文件与对比度检查、Excel 与 Word 生成、会话、发布、经验库、校验与测试
agents/         Agent 平台配置
```

## 五个技能的分工

| 技能 | 负责 |
|---|---|
| [Luz-System](https://github.com/luzern0414/Luz-System) | 系统设计：软件方案、界面与原型、硬件选型 |
| **Luz-Design**（本仓库） | 视觉标准、海报与品牌视觉、文件排版 |
| [Luz-Dev](https://github.com/luzern0414/Luz-Dev) | 后端、接口、数据库、部署与上线 |
| [Luz-Writing](https://github.com/luzern0414/Luz-Writing) | 文章、文案、协议等文字内容 |
| [Luz-Crawl](https://github.com/luzern0414/Luz-Crawl) | 真实浏览器检索与采集 |

## 许可

本仓库采用 [PolyForm Noncommercial 1.0.0](LICENSE)：个人学习、研究、教学、公益组织与政府机构等**非商业用途**可以自由使用、复制、修改和分发；**禁止任何商业用途**。如需商用，请先联系作者取得授权。分发时请保留 LICENSE 与 [NOTICE](NOTICE) 中以 “Required Notice:” 开头的版权声明。引用的公开设计体系与标准只用于提炼规则，版权归原作者。
