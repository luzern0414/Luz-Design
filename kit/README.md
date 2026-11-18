# kit

`frontend/app-task` 和 `frontend/web-workspace` 是组包源目录。用 `scripts/frontend.py init` 组装相应起点，命令见 [组件复用合同](../references/component-reuse.md)。共享脚本、图库和运行时位于 `frontend` 的同级子目录，由组包脚本放到成品入口旁。

四个模板文件夹共用的样式、脚本、素材，以及可运行工程起点。页面通过 `../../kit/` 引用，换文件夹位置时只改这一层相对路径。

| 路径 | 内容 |
|---|---|
| `tokens.css` | 令牌：颜色、字阶、间距、圆角、阴影、动效，由 `scripts/sync_template_tokens.py` 生成，不手改；八个主题色用 `data-theme` 切换 |
| `ui.css` | 基础组件样式：卡片、列表行、按钮、表单、标签、反馈、图表、智能体等 |
| `kit.css` | 变体：按钮、背景、卡片、标签、分段的细分类 |
| `app.css` `web.css` `agent.css` | 移动端壳、网页后台壳、智能体对话 |
| `ui.js` | `Lz`：分段、展开、独立页面、下拉、开关、滚轮、轻提示、确认框、折线图、流式文字、换主题与图标风格 |
| `assets/` | 线性图标、立体 / 真实 / 扁平三套入口图标、彩色实心业务图标、花卉商品实拍、背景图案、对象标识；清单与哈希见 `assets/manifest.json` |
| `registry.js` | 全部编号，由 `scripts/template_registry.py write` 生成 |
| `frontend/` | `scripts/frontend.py init` 使用的两个可运行工程起点（Vue），含运行时依赖与许可 |
