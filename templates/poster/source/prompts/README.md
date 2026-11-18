# 海报提示词库

供 Imagegen 生图用的提示词库：商品摄影、场景头图、背景纹理、图标拼板、空态插画、对象标识池、海报主视觉、头像与其他，共 60 条（`PP-001` 至 `PP-060`），其中 7 条是真实生成并被用户认可的已验证提示词，原文保留。

双击 `index.html` 查看：分类标签、搜索、主题色切换、折叠的完整提示词、复制按钮、复核要点与成品图缩略。

## 文件

| 文件 | 作用 |
|---|---|
| `prompts.json` | 提示词数据，唯一的手写数据源 |
| `styles.json` | 主题色表、风格块 `ST-NNN`、负面约束组 `NG-NNN` |
| `prompts.js` | 由脚本生成，查看页用它加载数据（本地文件打不开 fetch），不手改 |
| `index.html` | 查看页，引用 `../../../../kit/` 的令牌与样式 |
| `source/` | 7 条已验证提示词的原文，一条一个 txt |
| `scripts/build_prompts_js.py` | 检查数据并生成 `prompts.js`，位于技能的 `scripts/` 目录 |

## 编号规则

- 提示词 `PP-NNN`：三位数字，从 001 连续，不跳号。分类按编号段排列：商品摄影 001–012、场景主视觉 013–020、背景与纹理 021–030、图标拼板 031–036、空态与结果插画 037–042、对象标识池 043–045、海报主视觉 046–055、人物与头像 056–058、其他 059–060。
- 风格块 `ST-NNN`、负面约束 `NG-NNN`：各自从 001 连续。
- 编号发出后不改、不复用、不重排。删除或弃用一条时保留编号，在 `notes` 写明弃用原因；新增一律取下一个空号，分类可以跨段。
- 按编号查看：`py -X utf8 scripts/template_registry.py show PP-012`。

## 字段

| 字段 | 内容 |
|---|---|
| `id` | `PP-NNN` |
| `name` | 4–12 个汉字，不与别的条目重名 |
| `category` | 分类，取 `categories` 里的名称 |
| `use` | 用途一句话，写清用在哪 |
| `role` | `background`、`icon-sheet`、`illustration` 对应生成器的 `--role`；另有 `photo`（摄影）与 `poster`（海报） |
| `ratio` | 生成器接受的比例：`1:1` `3:4` `4:3` `9:16` `16:9` `2:3` `3:2` |
| `resolution` | `1k` `2k` `4k`；屏幕按显示尺寸的 2 倍，印刷按成品宽度算 300ppi 以上 |
| `background` | `opaque` 或 `transparent`；透明只给拼板与单物体插画 |
| `format` | 生成器固定出 `png` 原图，再另存 webp 派生文件 |
| `prompt` | 英文提示词，按八槽位写，负面约束在最后；用 `{{primary}}` 与 `{{secondary}}` 表示主题色 |
| `negative` | 负面约束全文，等于 `prompt` 末尾那一段 |
| `style_ref` | 引用的风格块编号，数组 |
| `negative_ref` | 引用的负面约束组编号 |
| `checks` | 复核要点，数组，至少 2 条，写成可以看图回答的判断 |
| `verified` | 只有真实生成并被用户认可的才写 `true` |
| `result` | 成品图相对路径，如 `../../../../kit/assets/photo/bouquet-rose.webp`；没有写空字符串 |
| `source` | 已验证条目的原文文件，如 `source/florist-rose.txt`；其余写空字符串 |
| `notes` | 失败时怎么调，一句话，只改变量，不重写风格行 |

## 八槽位

未验证条目的 `prompt` 固定为八行，顺序不变，每行以槽位名开头：

| 行首 | 槽位 | 写什么 |
|---|---|---|
| `Purpose:` | 用途与位置 | 放在哪、给谁看 |
| `Subject:` | 主体 | 一个主体，写具体属性；拼板按 (1) 到 (16) 列物件 |
| `Composition:` | 构图与镜头 | 画幅、占比、边距、机位；海报写明文案留白区 |
| `Lighting:` | 光线 | 先原文复用风格块的光线，再追加本条特有的一句 |
| `Material:` | 材质 | 同上，复用风格块的材质 |
| `Color:` | 色彩 | 先写本条的主题色分配，再接风格块的色彩规则 |
| `Background and output:` | 背景与输出 | 背景，末尾写 `Output: 比例, 分辨率, PNG` |
| `Avoid:` | 负面约束 | 负面约束组原文，再追加本条特有的几项 |

写属性不写评价，用材质、光线、镜头这类可观察的词；不写品牌名与在世艺术家名；图里不放任何文字，海报的标题与信息在版面里另加。已验证的 7 条沿用生成时的格式（`Use case`、`Primary request` 等），原文不改。

## 怎么用

1. 打开 `index.html`，选主题色，找到条目，点“复制提示词”。复制出来的已经是换好主题色的文本。
2. 在会话里存成 `raw/02-visual/prompts/NN-名称.txt`，UTF-8。
3. 先 dry-run，一个请求一条记录：

   ```
   py -X utf8 scripts/generate_ui_assets.py generate --session <会话> --prompt-file <会话>/raw/02-visual/prompts/01-名称.txt --id <英文id> --role <角色> --ratio <比例> --resolution <分辨率> --background <背景> --dry-run
   ```

   `--role` 取条目的 `role`；`photo` 与 `poster` 在生成器里没有同名角色，登记时用 `illustration`。比例、分辨率、背景照抄条目字段。
4. dry-run 通过后去掉 `--dry-run` 正式生成。全程串行，一次只发一个请求；超时先查回执，不自动重试，不重复计费。
5. 打开成品图逐条对照 `checks`，再用 `generate_ui_assets.py review` 记录结论。拼板用 `scripts/cut_element_sheet.py` 切图，切完逐个排除邻格碎片。
6. 失败时看条目的 `notes`，只改变量，风格行与约束行原样复用，不逐张改写。

## 主题色

页面顶部的 8 个色点来自 `tokens.css` 的主题，主色取 `--action`。提示词里的占位符按下表替换成“英文色名 加 hex”，英文提示词里直接写这一串：

| 主题 | `{{primary}}` | `{{secondary}}` |
|---|---|---|
| 雾粉 | dusty rose #A85D79 | sage green #8FA68E |
| 珊瑚 | muted coral #A76352 | warm sand #D6BE9B |
| 暖橙 | caramel amber #9A6A3C | olive green #8B9462 |
| 草绿 | fresh sage green #50804E | warm cream #EADFC4 |
| 青碧 | muted teal #457D81 | soft peach #E8B49A |
| 天蓝 | dusty blue #5577A4 | oat sand #D9C7A6 |
| 紫藤 | wisteria purple #7D6CA5 | butter yellow #E5D48F |
| 石墨 | graphite grey #4B515A | warm champagne #CDB894 |

同一套产品的所有图使用同一主题色与同一段风格块，不逐张改写。已验证的 7 条是原文，没有占位符，不随主题变化。主题表在 `styles.json` 的 `themes`，新增主题在那里追加。

## 新增一条

1. 在 `styles.json` 里选一个风格块（`lighting`、`material`、`color_rule` 三段）和一组负面约束。没有合适的风格块就先追加一个 `ST-NNN`，不要在提示词里临时改写。
2. 在 `prompts.json` 的 `prompts` 末尾追加一条，编号取下一个空号，字段按上表填齐。`Lighting:`、`Material:`、`Color:` 三行必须原文包含所引风格块的对应段落，`Avoid:` 一行必须以所引负面约束组原文开头。
3. `negative` 填 `Avoid:` 之后的全文，`style_ref` 与 `negative_ref` 填引用的编号。
4. 条目只有真实生成并被用户认可后才能写 `verified: true`，同时要有 `source`（把当时的提示词原文存进 `source/`）与 `result`（成品图路径）。
5. 运行 `py -X utf8 scripts/build_prompts_js.py`。通过才会写出 `prompts.js`；`--check` 只检查不写文件，`prompts.js` 过期也会失败。
6. 打开 `index.html` 确认新条目的分类、主题色替换与折叠都正常。

## 脚本检查什么

编号连续不重复；字段齐全且类型对；名称 4–12 个汉字；分类、角色、比例、分辨率、背景、格式都在允许的范围内；八个槽位齐全且顺序对；`Avoid:` 是最后一行并与 `negative` 一致；风格块与负面约束组原文被引用；拼板恰好列 16 个物件、1:1 透明底；占位符只有 `{{primary}}` 与 `{{secondary}}`；提示词是英文，不含“好看、精美”一类空泛词，不含品牌名与艺术家风格；成品图与原文文件存在；已验证条目与 `source` 原文逐字一致。工具只检查结构，内容是否合适仍要看成品图。

## 已验证条目

| 编号 | 原文 | 成品图 |
|---|---|---|
| PP-001 | `source/florist-rose.txt` | `bouquet-rose.webp` |
| PP-002 | `source/florist-tulip.txt` | `bouquet-tulip.webp` |
| PP-003 | `source/florist-white.txt` | `bouquet-white.webp` |
| PP-013 | `source/florist-hero.txt` | `scene-hero-pink.webp` |
| PP-021 | `source/pattern-leaves.txt` | `pattern-leaves.webp` |
| PP-022 | `source/pattern-petals.txt` | `pattern-petals.webp` |
| PP-023 | `source/pattern-waves.txt` | `pattern-waves.webp` |

成品图都在 `../../../../kit/assets/photo/`。其余 53 条是按同样写法与风格块新写的，还没有生成过，生成并看图通过后再补 `result` 与 `verified`。
