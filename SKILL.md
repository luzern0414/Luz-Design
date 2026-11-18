---
name: luz-design
description: 设计、实现或改进 App、Web 前端界面，制作海报和 PowerPoint 演示文稿，也处理 Word、Excel、PDF 与阅读网页的排版。提供整页与组件模板、图标排布建议和可商用演示模板来源。已有产品优先延续现有设计系统。
---

# Luz Design

把真实内容做成可用的界面、海报或文档。App 和 Web 默认交付可运行的界面及源码。已有产品沿用其设计系统。

## 调用协议

独立任务用 [会话与交付](references/session-delivery.md)。有项目上下文时接入[项目流程](../Luz-Project/references/skill-architecture.md)。

1. 运行 `python -X utf8 scripts/context.py list`，读所选规则卡和[成品要求](references/design/hard-rules.md)。`new_session.py` 按所选类别开会话，海报使用 `--standalone-poster`。在简报写使用者、主任务、内容和要检查的状态。
2. 按原始请求选择[阶段依据](../Luz-Crawl/references/evidence-policy.md)。项目或生成器需要记录时依[前置检索](../Luz-Crawl/references/preflight.md)完成 `run` 与 `check`，联网先核对实际正文或图像再 `conclude`。
3. `template_library.py list/select` 将模板绑定到实际路径。按所选类别的生成器制作，登记最终哈希，`deliver.py` 或 `publish.py` 复核。正式文档按[内容依据与成品验收](references/document-evidence.md)。
4. 用真实内容和目标尺寸检查成品。前端走主要用户流程、状态和无障碍检查，项目的 UX、AX 和 DX 规则用 `quality_rules.py list/plan` 选取并 `check`。
5. BRIEF 写“采用的规则”和“本次沉淀”，用 `experience.py note` 更新同键经验。只适用于项目、技能维护或已写入规范的经验分别用 `--scope project`、`--scope maintenance`、`--codified`。

## 按产出选规则

- **App** 读 [移动端](references/design/app.md)，**Web** 读 [网页](references/design/web.md)。按[界面分工](references/ui-ownership.md)承接 System 的页面与动作。先看 `index.html` 和页面示例，再按[组件复用](references/component-reuse.md)和[交互合同](references/design/interaction-contract.md)做到代表任务可操作。素材许可见[图像与素材](references/image-assets.md)。新工程可用 `frontend.py init app-task|web-workspace`，已有工程沿用原构建链。用[审阅](references/design/review.md)记录实际成品。
- **海报** 读[构图与传播尺寸](references/design/poster.md)。
- **Word、Excel、PDF、阅读页** 读[文件排版](references/design/documents.md)。**PPT** 读[演示设计](references/design/slides.md)与[可商用模板目录](templates/documents/slides/commercial-sources.md)。

修改技能后运行 `validate_skill.py --package-only`。
