# Luz Design 经验库

每次调用开始先读本页并运行 `py -X utf8 scripts/experience.py search <关键词>`：偏好与教训直接照做，能复用的配色、字阶与视觉、文件规则直接沿用，只为缺口做新的调研。结束前用 `note` 按主题键写入新的偏好、教训与有效信息（`experience/notes.json`），同一个键覆盖旧条目。本页由 `scripts/experience.py` 生成，修改请用命令或改 JSON。

## 偏好（27/60）

- **ai-service-brochure**：企业 AI 服务介绍类 PDF：横版、不超过 20 页、清晰简洁，只放一个大标题加表格（通用决策系统一张、行业定制方向一张），每个行业列出具体方向（智能体名称加一句判断），不放导语、示例、流程图、上线步骤等其他内容；只适用于 AI 服务介绍类产出（用户 2026-10-30：119 页太多了，把具体的行业和具体的方向列表就行，清晰简洁，不要超过20页，不要任何多余的内容，一个大标题，然后列出表格即可）　确认 2 次，最近 2026-10-30
- **b2b-tool-graphite**：B2B 数据与获客类工具后台用 themes.json 的 b2b-graphite 石墨主题：锌灰中性色占绝大部分，主按钮近黑，彩色只给链接与焦点，状态用小圆点加文字，头像与智能体用线性图形，不用卡通、立体或生成的装饰图案，静止卡片只用发丝线；其他行业与产出不适用（用户 2026-10-29 否定一个获客系统的极客蓝方案（颜色太重、图案幼稚、3D 不够高级），在石墨、雾蓝、青石三个方向中选了石墨）　确认 2 次，最近 2026-10-29
- **catalog-table-look**：目录式表格（行业、产品、方向清单）要好看：表头用主色第 2 阶、分组行第 1 阶、对象名列页面极浅底，行间 1 像素横线，表头上角统一圆角；单元格写“要点 + 一句说明”，要点主色按下阶 600、说明正文深色；中文只在词间换行、行长均衡；横版 PDF 用 make_table_pdf.py 生成（用户 2026-10-30：表格设计有点丑，字体要自适应居中或者对齐，表格颜色、底色可以优化，提升视觉效果）　确认 1 次，最近 2026-10-30
- **commercial-miniprogram-density**：小程序用紧凑字阶：页面主标题 18/600，商品名与列表名 14 加粗，主对象大卡片 16，描述、规格、“状态 · 时间”第二行与标签、划线价 12，列表与卡片价格 16–18/600、详情页价格 22/700，货币符号与小数 12，智能体消息 14/22，每屏只留一个大数字；营销区（首页、活动页、会员与积分商城推荐位）可以错落、一大两小、出框与图形化标题字（手写风格用图片或图形字，不另加字体族），功能区（菜单列表、表单、订单、设置、后台）对齐等高（用户 2026-10-29 看过商用小程序录屏后确认紧凑字阶，并决定只在营销区放开不规则排版；同日审计统一页面主标题与价格数值）　确认 3 次，最近 2026-10-29
- **commercial-miniprogram-look**：产品界面做成成熟商用小程序的样子：居中导航栏与胶囊位、分组单元格、首屏一张品牌主卡、底部固定操作栏，令牌仍按主题与层级规则（用户 2026-10-29 要求视觉尽量做成小程序的视觉效果，商用的，成熟的）　确认 1 次，最近 2026-10-29
- **concise-logic-table-doc**：业务逻辑说明按主题拆成若干张两到四列的表格，有状态的表把状态放首列，每行一条规则，不写解释段落、建议与阅读指引（用户要求状态放前列并补全规则）　确认 2 次，最近 2026-10-29
- **deliver-to-requested-dir**：用户指定保存位置并说只要一个文件时，只把最终成品复制到该位置，规则卡、BRIEF、spec 等过程文件留在会话 raw。（用户要求保存到当前目录且只需一个 Word 文件）　确认 2 次，最近 2026-10-30
- **elevation-and-canvas**：界面要有立体感：卡片、悬浮卡片、下拉与吸顶、对话框按 themes.json shared.elevation 的五级双层阴影取值，静止卡片 1 像素发丝边加第 1 级，可点击卡片悬停升第 2 级，对话框第 4 级加 45% 遮罩；阴影只向下（贴底的栏向上镜像），用中性深色或主题第 10 阶暗调；页面底可用主色同色相的极浅底（色相差不超过 12 度、亮度不低于 0.85，例如智能体主题 #F0F2FC），不必一律中性灰；阅读型页面只用细线不用卡片阴影（用户 2026-10-29 要求补对话框、卡片与整体立体感，参照 Material 3 高度、Apple HIG 材质、Fluent 2 高度、Ant Design 阴影、Carbon 分层、Atlassian 高度与 Polaris 阴影令牌，并批准页面底用主题极浅底 #F0F2FC）　确认 1 次，最近 2026-10-29
- **excel-layout**：Excel 最小 12 磅、标题 18 磅；不加序号列；同列重复的分组名纵向合并；一格只写一个事实；用浅色底区分层次。用 make_xlsx.py 生成。　确认 1 次，最近 2026-10-28
- **export-cleaned-chinese**：系统导出的表格是清洗后的中文数据：中文表头、枚举译成中文、日期年-月-日 时:分、金额两位小数单位在表头、去掉内部编号技术字段与空列、范围等于当前筛选、中文文件名带范围，用表格生成脚本出版式（用户要求导出给人看的数据，不是数据库原表）　确认 1 次，最近 2026-10-28
- **fitness-palette**：健身行业主色用火山橙，营销用金色，二者是邻近色、和谐不冲突。　确认 1 次，最近 2026-10-28
- **flat-line-style**：界面扁平为主：控件图标、头像与图表是平面矢量（纯色面加统一 2 像素描边）；入口图标、插画与装饰元素可用用户选定风格的生成图（imagegen-decorative-elements）；立体感属于表面，按五级层级令牌（双层中性阴影、发丝线、遮罩）、主按钮 1 像素按下阶底边与实色面 16%–24% 内顶部高光建立；界面不用渐变（照片遮罩与骨架流光除外）、玻璃、发光、主色投影、斜面与拟物纹理（用户多次纠正立体图标与渐变按钮，2026-10-29 要求补层级系统；同日又确认入口图标、插画与装饰元素可以生成，风格按行业和场景定）　确认 3 次，最近 2026-10-29
- **html-tab-icon-required**：每个交付的网页都要有浏览器标签页图标：内联 SVG，32 栅格、圆角 8 浅底、主色线稿、最多 3 个形状、无文字、16 像素可辨认，同一系统各页同一图案；后台与网站页头放同一图案的图形品牌标识；模板与生成脚本内置图标参数，check_document 缺失即报错（用户要求（2026-10-28））　确认 1 次，最近 2026-10-28
- **imagegen-decorative-elements**：入口图标、插画与装饰元素（品牌主卡主视觉、横幅、空状态、完成页、引导页、能力清单、宫格入口）可用 Imagegen 生成：风格按行业和场景在视觉稿给 2–3 种候选，用户在视觉审批时选定，一个产品一种风格；透明底、无文字、一物一图；优先一次生成 4×4 拼板再切图；导航、标签栏、菜单、按钮内、工具栏、表格与表单里的控件图标仍用 2 像素线性矢量（用户 2026-10-29：装饰性的元素图案可以做，尽量生成 4*4 的提高效率；再次确认插画和图标都可生成，风格按行业和场景定）　确认 2 次，最近 2026-10-29
- **interface-density-14px**：界面密度：后台正文与表格 14 像素、行高 22，辅助 12 像素只给时间、单位、角标；字号 3–5 种；8 像素网格，卡片内边距 16–20、间距 16；表格行高 44–48，紧凑 36–40；1440×900 首屏至少 10 行，统计卡不超过 112 像素，不留大块空白（用户反馈后台字太小、留白太多、密度低；依据蚂蚁、腾讯字体规范与碳设计体系数据表格）　确认 1 次，最近 2026-10-28
- **list-pagination-default-20**：分页条的样子：放在表格下方靠右、右缘与表格对齐，文字 14 像素与表格正文同档，页码、翻页、条数选择与跳页框高 32 像素，当前页用主色；默认条数、可选条数、记住选择与小程序滚动加载等行为按 Luz-System admin-design.html 的分页规则（用户要求（2026-10-28）；2026-10-29 审计后本技能只留视觉部分，行为规则归 Luz-System）　确认 2 次，最近 2026-10-29
- **luz-skill-order**：产品工作按固定顺序调用：Luz-System 从需求、系统设计做到界面视觉稿、原型与发布（视觉数值读 Luz-Design 的 visual-design.html 与规则卡）→ Luz-Dev 实现 → Luz-Writing 写文档与文案；Luz-Design 只做视觉标准、海报与品牌视觉、文件排版；每个技能开始检索经验、结束沉淀，不得跳过（用户 2026-10-28 要求规定调用顺序；2026-10-29 审计按五个技能分工改写：界面视觉稿与原型归 Luz-System）　确认 2 次，最近 2026-10-29
- **no-italics**：中文产出禁用斜体，强调用字重或颜色，不用倾斜与旋转文字。　确认 1 次，最近 2026-10-28
- **no-template-reuse**：每次产出前重读规范相关小节与 themes.json，模板只给结构骨架；配色、字体角色、层级、图标与插画按本次内容完整设计，不保留模板默认色板与样式，不沿用上一个项目的样式；交付前逐条自检并把记录写在会话 raw（BRIEF 的采用的规则），不进成品（用户 2026-10-29 要求不允许只套用模板；check_document 对保留模板默认样式的页面给出警告）　确认 1 次，最近 2026-10-29
- **one-font-stack**：每个文件只用一条字体栈（苹方、微软雅黑、思源黑体、系统无衬线），网页任何文字不小于 12 像素，网站与阅读页正文不小于 14 像素；字重三档：400 正文，600 标题、表头与强调，700 只给 22 像素以上的页面主标题与大号数字，不用 500 与细字重，标题与表头不用浏览器默认粗体；产品界面按七级字体角色取字号、字重与颜色，大段正文用正文深色（用户 2026-10-29 反馈字体没有完整层级且太细，取代原“只用 400 与 600 两种字重”）　确认 2 次，最近 2026-10-29
- **one-object-one-icon**：一物一图：不同对象不共用同一个图标，同一对象在各处用同一个图标。　确认 1 次，最近 2026-10-28
- **palette-by-industry**：配色按行业气质从官方 10 阶色板取阶，不凭感觉调深调浅；中性色、主色、强调色按 60-30-10 分配，文字对比度达到 4.5:1。　确认 1 次，最近 2026-10-28
- **rich-solid-visual**：界面要图案丰富、字体层级完整且不细、颜色丰富浑厚、图标不单薄：七级字体角色与 400/600/700，控件图标 2 像素，入口、指标与空状态用双色图标块或选定风格的生成图标，空状态、结果、问候与封面用多层扁平插画或生成插画，主色按整列多阶使用并给一级模块固定点缀色，每屏至多一张品牌主卡（用户 2026-10-29 反馈图案太简单、字太细、颜色不够浑厚、图标单薄；同日确认图标与插画可以生成）　确认 2 次，最近 2026-10-29
- **store-open-close-one-click**：停业的视觉：营业状态用状态色加文字（营业中成功色、暂停与休息警示色加恢复时间、闭店中性灰），不用红色；页面不整页灰化，商品与价格可浏览，加购按钮换成中性灰“暂停营业”，线上公告与门店张贴的停业海报同一文案与时间（用户 2026-10-29 要求后台补一键开业与停业，完善停业后的小程序显示、支付暂停与设备配置）　确认 1 次，最近 2026-10-29
- **table-centred**：表格对齐：整张表视觉居中——列宽随内容自适应、对象名列按最长名称收紧，所有单元格垂直居中，表头、分组名与对象名居中；数据不顶格，左右内边距不小于 16 像素；长文本左对齐，列宽偏宽或等宽时作为一个文字块在列内居中；状态、日期、负责人、操作等短值居中；需比较大小的金额右对齐、等宽数字、单位写在表头；界面、阅读页、Excel、Word 与 PDF 表格同一规则（用户 2026-10-30：表格对齐尽量自适应，表格内容与标题尽可能居中对齐，表格数据可以左对齐，但是整体视觉要居中；此前纠正过宽列表头居中而文字贴左边的错位）　确认 4 次，最近 2026-10-30
- **word-by-type**：Word 文档先定类型（合同、方案、报告、会议纪要、公文），按该类型的结构与格式排版，用 make_docx.py 生成。　确认 2 次，最近 2026-10-29
- **word-paper-style**：正式申请、报告、方案类 Word 按学术论文的文字规范排（make_docx.py 的 style paper）：标题黑体小二居中；一级标题用 Word 自动编号生成序号（用户首选 1、，也接受 1.），不手打数字和空格，黑体四号顶左；标题与各级标题都不加粗；正文宋体小四、西文 Times New Roman、首行空两字、1.5 倍行距；不用公文的 3 号仿宋；表格用普通浅色网格加浅底表头，不用三线表（用户确认论文版式后要求补充进技能；2026-10-29 审计把键名从 official-doc-fonts-gbt9704 改为论文版式（内容与 GB/T 9704 公文格式无关））　确认 9 次，最近 2026-10-29

## 教训（28/120）

- **catalog-content-as-table**：几十个对象的目录式内容（行业、产品、方向清单）不要按演示文稿一页一结论展开，会膨胀到上百页；做成一个标题加分组表格的横版网页导出 PDF，对象一行、属性分列，先估算页数再排版（85 个行业按演示文稿规则做成 119 页被用户否决，改成标题加两张表后 16 页）　确认 1 次，最近 2026-10-30
- **check-document-paper-official-fonts**：用户明确要求论文版式或公文格式时，check_document.py 要带对应参数：论文版式 --allow paper（宋体、黑体、Times New Roman），公文格式 --allow official；不带参数时多字体仍报 more than one font family，参数只在用户要求时使用（2026-10-29 审计把键名从 check-document-gbt9704-fonts 改为同时覆盖论文版式与公文格式）　确认 4 次，最近 2026-10-29
- **cjk-cell-word-break**：窄列中文单元格只用 text-wrap: balance 会把词拆到两行（提/醒、速/度）；先在生成时用浏览器 Intl.Segmenter 分词，标点并入前一个词，词间放 <wbr>，再配 word-break: keep-all 与 text-wrap: balance，成品不带脚本（目录表格首版用 pretty 与 balance 都出现拆词，按词折行后断行自然）　确认 1 次，最近 2026-10-30
- **control-fill-by-element**：实色底是否允许按元素认定：button、按钮类 input、带控件角色的元素和类名含 btn 的链接都算控件，类名随意；同一组选择器还命中卡片、横幅等容器时按容器报错（check_document 与会话校验原先只认选择器里的 button 字样，.ok、.btn-primary 这类按钮被误判为大面积深色）　确认 1 次，最近 2026-10-29
- **docx-check-cue-brackets**：Word 成品里的舞台提示不用【】（check_document 把 12 字内的【…】判为占位符），改用（停顿）（计时 10 分钟）；正文避开“数据来源”“我们来看”“以下是”“如有问题”等会被判为元信息或套话的说法（讲稿类 Word 用 make_docx 生成时被检查拦下）　确认 1 次，最近 2026-10-30
- **docx-latin-width**：make_docx 估算列宽时西文字母与数字按 0.6 个汉字宽（汉字记 2、西文记 1.2），设备地址、编号等无空格长串才不会在格内断开（IEEE 地址在表格里被截成两行）　确认 1 次，最近 2026-10-29
- **docx-single-face-bold**：黑体、宋体、楷体等系统中文字体没有真粗体，Word 加粗只是模拟描粗，黑体标题加粗会发糊；黑体标题一律不加粗，靠字号与字体区分层级，即使规范写了加粗也先按不加粗出并说明。（用户看过黑体加粗标题后说有点丑）　确认 2 次，最近 2026-10-29
- **docx-split-long-cell**：Word 表格里地址加通道等组合值会在格内折行，拆成独立列；同一主题拆成两张表会因长短不同出现两种对齐，能放进一页时合成一张（门禁开关与入场资格两表逐页检查发现）　确认 1 次，最近 2026-10-29
- **docx-table-column-align**：一列只用一种对齐：make_docx 按整列判断，任一数据格超过 22 字或会在本列宽内折行则整列左对齐，否则整列居中；不要再按单元格各自判断导致同列混排（业务逻辑关系表交付时同列出现居中与左对齐混排）　确认 2 次，最近 2026-10-29
- **docx-table-keep-together**：make_docx 只让不超过 8 行的短表整表不跨页；接近页底的表格超过 8 行会把最后一两行挤到下一页，可合并同类行压到 8 行以内或精简长文本（业务逻辑关系表注销表 9 行跨页）　确认 4 次，最近 2026-10-29
- **export-from-current-file**：导出或转换格式前从用户手里的当前文件导出，不从会话里的旧源重新生成，以保留用户在 Word 里做的手工修改，并把修改后的版本同步回会话。（用户交付后在 Word 中改过文字）　确认 2 次，最近 2026-10-29
- **icon-label-consistency**：图标目录里每个图标的说明文字要与页面上同一图标旁的对象名一致或互相包含；确属不同对象就另画一个图标（例如项目问答用问号气泡，与对话分开），否则 check_document --allow interface 判为一图多义（Luz-System 会话的智能体视觉板：图标目录写的说明与页面对象名不一致被判一图多义（同 key 也记在 Luz-System））　确认 1 次，最近 2026-10-29
- **interface-rich-but-flat**：用户要更多动画与图形时：动效挂在状态变化上（按钮下沉 1 像素、卡片悬停升级、对话框放大弹入、计数、描线），循环只留进行中状态；线条承担结构（调用链、时间线、阶段轨道、横向网格、内缩分隔）；插画用多层扁平进空状态、结果、登录与问候；阴影按五级令牌，点缀色不借用状态色（多动效多图形的诉求与扁平、动效只说明来去的规范冲突时，按此取舍能同时满足用户意图与规范（2026-10-29 随层级系统更新））　确认 2 次，最近 2026-10-29
- **interface-version-not-metadata**：界面里的版本信息是产品内容：check_document 在界面模式下不检查类名或编号带 version 的元素里的“版本号”“发布时间”等元数据词；交付文档里仍然拦（用户 2026-10-29：后台要显示版本信息，把这个规范加上）　确认 1 次，最近 2026-10-29
- **interface-visual-graphics**：产品界面视觉稿先读规范与 themes.json：按行业取主题与页面底色，头部浅底，入口、指标、列表项配双色图标块（主色或模块点缀色），一物一图，空状态、问候与封面用多层扁平插画，卡片发丝边加第 1 级阴影，首页与工作台各一张品牌主卡；只有灰底白卡与细线图标会被判为没有设计感（用户 2026-10-28 反馈视觉板丑、没有图案，2026-10-29 又反馈图案简单、图标单薄、缺立体感；取代原“线稿插画、浅底图标块”的做法）　确认 2 次，最近 2026-10-29
- **layered-rule-consistency**：改上层视觉规范时同步核对同页的平台矩阵、分端规范（Luz-System 各端页面）与检查脚本：上层不能比分端更宽松或互相矛盾，例如七级字体角色把小程序正文写成 16 而平台矩阵与小程序规范是 14，应以分端的 14 为准；实色面与浅底面的高光透明度、点击反馈也要在动效表与按钮规则里取同一值（2026-10-29 视觉规范修订复核时发现小程序正文、按钮按下反馈与实色面高光三处前后不一致）　确认 1 次，最近 2026-10-29
- **long-content-bullets**：表格中的长采购内容用最多三条短列点表达，使用浅色主题色小圆点，悬停提示保留完整原文。（短列点提升扫读效率，同时不丢失可追溯信息。）　确认 1 次，最近 2026-10-30
- **pdf-outline-label-headings**：导出 PDF 书签按 h1–h3 生成，卡片里的“常见问题”“看哪些指标”这类小标签不要用 h3，改成同样式的段落，书签只留章节、系统和对象名（首版 149 条书签里混入大量小标签，改后 129 条且三级只剩行业与系统名）　确认 1 次，最近 2026-10-30
- **pptx-legend-dots-as-shapes**：演示文稿里的矩阵圆点和图例用椭圆形状画，不用 ●○ 字符；check_document 把这些字符判为装饰符号报错（八套系统矩阵页用 ● 字符被判 emoji or decorative symbol）　确认 1 次，最近 2026-10-30
- **publish-docx-manual-copy**：publish.py 的 document 阶段只发布 HTML（会把模板 document.html 当成品）；Word 或 Excel 成品直接放到会话根目录，命名为文件夹名加扩展名，不跑 publish.py。　确认 1 次，最近 2026-10-29
- **reading-page-for-design-docs**：系统架构与系统设计页是阅读型网页：按 file-design.html 用 32/24/20/16/14 字阶、整句表格 16、只有横线、不给每节套卡片，check_document 不加 --allow interface；用户要求时每节配独立线性图标块并用内嵌线性矢量画页面关系图（用户 2026-10-29 指出系统设计页文字过小、缺图标、未用 Luz-Design 排版）　确认 1 次，最近 2026-10-29
- **small-fill-selector-naming**：check_document 按尺寸与类名认定小元素：规则里声明高度不超过 20 像素（或宽高都不超过 24 像素）的实色块、类名末段是 dot、badge、mark、progress、avatar 等小对象词的元素、伪元素与图标算小元素；顶栏、卡片等容器即使叫 -bar、-box 也按大面积检查。12 号辅助字放在类名含 meta、hint、time、unit、badge、tag、caption、aux 整词或连字符段的元素里，community、timeline 这类包含字母的词不算（2026-10-29 审计实测 .top-bar、.box-card 深色底与 .community 12 号正文都曾漏检，改为按尺寸与整词认定）　确认 2 次，最近 2026-10-29
- **small-mark-class-noun**：文档里的小圆点、图例点等深色小标记，类名的最后一个词要是 dot、mark、tag 这类小物件词（如 core-dot），写成 dotm 或 dot-core 会被 check_document 当成深色大块填充报错（矩阵页图例圆点用 dotm、dot-core 均报 dark fill，改成 core-dot 后通过）　确认 1 次，最近 2026-10-30
- **spec-json-utf8-no-bom**：make_docx 与 make_xlsx 的 spec.json 用无 BOM 的 UTF-8 写；PowerShell Set-Content -Encoding utf8 会带 BOM 导致 JSON 读取失败，用文件写入工具或去掉 BOM。　确认 1 次，最近 2026-10-29
- **status-label-surface-only**：状态组件用文字底色和整体浅背景表达语义，外框用中性线；步骤列表显示状态文案并直接绑定事件状态以实时换色。（图标颜色不足以表达长步骤列表的状态，彩色边框会破坏浅色层级。）　确认 1 次，最近 2026-10-30
- **table-date-no-truncation**：日期、时间等短值列保持居中，并按最完整格式预留宽度；不能只按当前年份的短格式估算列宽。（研究报告日期列的跨年值被单元格内边距挤压。）　确认 1 次，最近 2026-10-30
- **topic-words-in-prose**：提示词、官方页面、版本号、SHA-256、哈希这些词在标题与成句的正文里是内容：check_document 只在“标签：值”、页脚与元信息行、不成句的短块里把它们判为产出信息；写这些主题的文章不用改词，元信息行仍要删（Luz-Writing 审计 2026-10-29：一篇讲提示词模板的文章被整篇误报）　确认 1 次，最近 2026-10-29
- **xlsx-group-level-values**：明细拆成多行的表格里，属于上级分组的数值（次数、问题数、整改数及其派生公式）随该分组纵向合并、公式只写在组首行；make_xlsx 默认只冻结开头的分组名称列（合并的数值列随数据滚动），需要别的冻结范围在描述文件写 freeze；长文本列自带一级缩进，列宽和折行已把缩进算进去；仍要用 Excel 导出 PDF 目检折行是否被行高截断（门店巡检汇总表评测：旧版 builder 冻结到最后一个合并列、公式列按公式文字估宽、缩进后折行被截断；已改 make_xlsx 默认值）　确认 2 次，最近 2026-10-29

## 有效信息（11/120）

- **b2b-status-tints**：在石墨主题中，进行中使用蓝色浅底，等待使用琥珀浅底，完成使用绿色浅底，部分完成使用橙色浅底，失败使用红色浅底，并配同色细边与左侧状态轨。（基于 b2b-graphite 主题与 Element Plus Tag/Card 官方规范实测。）　确认 1 次，最近 2026-10-30
- **docx-heading-auto-numbering**：make_docx.py 的 style paper 已内置标题自动编号：多级列表接在 Heading 1–3 样式上，一级按 number_format 取 1、（序号后无空白）或 1.（后接空格），二级 1.1、三级 1.1.1，附件重新从 1 开始；改现成文件时仍可按同法给 numbering.xml 加 abstractNum 并删去手打序号，用 Word COM 的 ListParagraphs 与 ListString 核对。　确认 2 次，最近 2026-10-29
- **docx-pdf-pagination-check**：Word 交付前用 Word COM 导出 PDF 并逐页渲染查看；短文档避免末页只剩一小节、段落末行只剩一两个字，优先删去重复句把内容收进整页。　确认 3 次，最近 2026-10-29
- **docx-slide-script-structure**：逐页讲稿类 Word：一级标题按 PPT 的部分（一、二…），二级标题写“第 X 页 标题”，生成后去掉 make_docx 加在二级标题前的（一）；超过 10 页时在标题后插 TOC 域，用 Word COM 更新，目录 1/2 样式固定行距 16 磅、段后 0 可把 33 条收进一页（make_docx general 类型对二级标题自动加（一），与“第 X 页”重复；目录按 1.5 倍行距会溢出到第二页并留空白页）　确认 1 次，最近 2026-10-30
- **docx-to-pdf-export**：Word 转 PDF 用 Word COM ExportAsFixedFormat：格式 17、CreateBookmarks=1（按标题建书签）、DocStructureTags 与 BitmapMissingFonts 为真；check_document 不支持 PDF，改用 PyMuPDF 核对页面尺寸、书签层级、字体嵌入与文字层，再逐页渲染目检。　确认 2 次，最近 2026-10-29
- **elevation-research-sources**：层级与阴影的依据用 Luz-Crawl 采集有效：流畅设计二代 elevation 页（双层阴影与 2–64 六档）、材料设计第三版 applying-elevation 与 tokens 页（0–5 级、遮罩 32%）、蚂蚁设计体系阴影页与 genColorMapToken.ts 源码（遮罩 45%）、亚特拉斯 elevation、碳设计体系 color/usage 分层、苹果材质页、约什·科莫阴影文章；北极星文档站的 depth 与 tokens/shadow 页已跳转到通用页，阴影令牌要从 GitHub 的 polaris-tokens/src/themes/base/shadow.ts 读取（2026-10-29 视觉规范补层级依据时的实测，采集目录 Luz-Crawl raw 016 与 019；来源已写入 sources.json SRC-088 至 SRC-102）　确认 1 次，最近 2026-10-29
- **gbt9704-docx-params**：python-docx 实现 GB/T 9704 版面：页边上 37、下 35、左 28、右 26 毫米，docGrid linesAndChars linePitch=579（28.95 磅）charSpace=-849（每行 28 字），正文与标题固定行距 28.95 磅，页脚距边界 2.5 厘米使页码一字线约在版心下 7 毫米；表格国标未规定，用小四仿宋、黑体表头、按毫米定列宽并关闭对齐网格；pPr 子元素须按架构顺序插入，否则 Word 打不开。　确认 1 次，最近 2026-10-29
- **imagegen-element-sheet**：Imagegen 透明底 4×4 元素拼板：请求 2880 实际返回 1254×1254，每格约 313 像素，界面 120 像素内够用；按网格切图后只保留面积不小于主体 1% 的连通部分，去掉背景碎点，再裁边存 WebP（每个约 15 KB）嵌入页面（008 视觉板修订 4 实测）　确认 1 次，最近 2026-10-29
- **landscape-brochure-pdf**：横版表格类 PDF 用 scripts/make_table_pdf.py spec.json out.pdf：一个 h1、每张表一个 h2，阅读型字阶 32/24/16/14 像素，A4 横版 @page，Edge 打印带书签、标签与页码；脚本先跑 check_document，再用 PyMuPDF 核对页数上限、字体嵌入和文字层，并输出每 6 页一张总览图（企业 AI 定制服务 85 个行业 372 个格子，17 页，检查 0 错误）　确认 3 次，最近 2026-10-30
- **premium-flat-palette-sources**：高级平面界面的取色与层次参考：Vercel Geist 灰阶 10 阶分工（1–3 组件底、4–6 边框、7–8 高对比底、9–10 文字）、Radix 12 阶用途表、Linear 改版减少品牌色用量、Stripe 感知均匀色板与浅底徽标上移一阶；Tailwind zinc/slate/stone 作中性色，zinc-500 对白 4.83:1 可作次要文字，但在 zinc-100 上只有 4.40:1，浅底上的文字用 zinc-600（Luz-Crawl 任务 027 实测采集 17 页（2026-10-29））　确认 1 次，最近 2026-10-29
- **thesis-text-spec**：论文文字规范可依《中国科学院大学研究生学位论文撰写规范指导意见》：A4，上下 2.54 厘米、左右 3.17 厘米，页眉页脚 1.5 厘米；章标题黑体四号、节标题黑体小四顶左、段前 24 段后 6 磅（原文写加粗，交付按 file-design.html 论文版式不加粗，系统中文字体没有真粗体）；正文宋体小四、英文 Times New Roman、首行缩进两字、段前段后 0、1.5 倍行距；标题编号 1、1.1、1.1.1 用 Word 自动编号；页码 Times New Roman 小五（交付用五号以守 10.5 磅下限）。GB/T 7713.1-2006 与 GB/T 7713.2-2022 只定结构与编号，不定字体字号。　确认 2 次，最近 2026-10-29

## 色彩

### PAT-098 健身房配色：活力橙核心 + 金色营销
- 适用：小程序、后台；行业：健身；使用 1 次，最近 2026-10-27
- 要点：按 Ant Design 官方色板取阶：主色火山 volcano，主按钮、开关、勾选用 volcano-6 #D4380D 实色白字（4.8:1），悬停 volcano-5 #FA541C，按下 volcano-7 #AD2102，浅底 volcano-0 #FFF2E8，浅底上的橙字用 #AD2102；营销取邻近色金盏花 gold，领取、抽奖用 gold-1 #FFF1B8 容器底配 gold-8 #874D00 文字（色调按钮），券面 gold-0 #FFFBE6；危险红 red-6 #CF1322；星级 gold-7 #AD6800；图表主系列火山 #FA541C，其余取金 #FFC53D、浅橙 #FFBB96、浅蓝 #69B1FF，“其他”用灰 #BFBFBF；中性暖白 #FAF8F6。
- 反例：自造深橙渐变配深紫实色按钮（显重）；随后改成半浅粉橙粉紫配深字（发飘，开关对白底不足 3:1）；饱和橙配饱和紫（彩度相近、既不邻近也不互补，用户评价“黄色和紫色不搭”）
- 依据：SRC-046～SRC-054
- 依据：[健身应用配色](https://octet.design/colors/palette/fitness-app-color-palette-1731930882)；[Ant Design 色彩](https://ant.design/docs/spec/colors-cn)；[TDesign 色彩](https://tdesign.tencent.com/design/color)；[Material 3 颜色角色](https://m3.material.io/styles/color/roles)；[NN/g 用色增强设计](https://www.nngroup.com/articles/color-enhance-design)；[Datawrapper 数据可视化配色指南](https://blog.datawrapper.de/colors-for-data-vis-style-guides)；[WCAG 2.1 理解 1.4.11 非文本对比](https://www.w3.org/WAI/WCAG21/Understanding/non-text-contrast.html)；[Material 3 高级颜色定制](https://m3.material.io/styles/color/advanced/adjust-existing-colors)；[Canva 色轮与配色类型](https://www.canva.com/colors/color-wheel)；[维基百科 色彩和谐](https://en.wikipedia.org/wiki/Harmony_(color))；[Figma 100 组配色](https://www.figma.com/resource-library/color-combinations)；[Smashing Magazine 色彩理论第二部分](https://www.smashingmagazine.com/2010/02/color-theory-for-designers-part-2-understanding-concepts-and-terminology)

## 字阶

### PAT-020 阅读型网页字阶
- 适用：网页；行业：通用；使用 1 次，最近 2026-10-26
- 要点：14 / 16 / 20 / 24 / 32；正文 16，按 1.25 倍递进，最小 14
- 用途：14 辅助与数字表格；16 正文与整句表格；20 三级标题；24 二级标题；32 主标题

### PAT-090 产品交付网页三部分共用一套字体与字阶
- 适用：小程序、后台、网页；行业：通用；使用 2 次，最近 2026-10-29
- 要点：功能列表、小程序、后台放在一个网页里时：同一字体族（苹方、微软雅黑、思源黑体回退），字阶 12/14/16/18/22/28/32，每个字号一个行高 12/18、14/22、16/24、18/26、22/30、28/36、32/40；按七级字体角色取用：大号数字 32/700、页面主标题 22/700、区块标题 18/600、卡片标题 16/600、正文 14/400（智能体消息 16）、次要 14/400、辅助 12/400；字重只有 400、600 与 22 像素以上的 700，不用 500
- 来源：用户反馈后台、小程序、功能列表字体不统一；2026-10-29 反馈字体层级不全且太细
- 检查：check_document --allow interface 拦截字阶外字号、22 像素以下的 700 与 500
- 依据：[中后台字体规范](https://ant.design/docs/spec/font-cn)；[字体与数字字体规范](https://tdesign.tencent.com/design/fonts)；[尼尔森诺曼集团 视觉层级](https://www.nngroup.com/articles/visual-hierarchy-ux-definition)；[碳设计体系 字体字阶](https://carbondesignsystem.com/elements/typography/type-sets)；[谷歌材料设计第三版 字阶令牌](https://m3.material.io/styles/typography/type-scale-tokens)

## 视觉规则

### PAT-031 禁用态的对比度
- 适用：通用；行业：通用；使用 1 次，最近 2026-10-26
- 要点：禁用按钮用浅灰底配灰字，文字对比度至少 4.5:1；禁用图形至少 3:1；不要用灰底白字
- 推荐：背景 #e9eeee，文字 #5f6874
- 旁注：禁用必须就地写明原因，例如“勾选同意后才能拍摄或上传”

### PAT-032 圆角三档与胶囊
- 适用：通用；行业：通用；使用 2 次，最近 2026-10-29
- 要点：产品界面圆角四档：标签 4，输入框、按钮、下拉与图标底块 8，卡片与图片 12，品牌主卡、横幅、对话框与底部弹层 16；头像、开关、胶囊全圆；阅读型产出全篇一个值（4–12）
- 更新：2026-10-29 增加 16 一档给大卡片与对话框

### PAT-091 中文界面禁用斜体
- 适用：小程序、后台、网页；行业：通用；使用 1 次，最近 2026-10-27
- 要点：中文没有真正的斜体，浏览器硬拉斜会让笔画变形；全局把 font-style 设为常规，斜体与强调标签重置为常规；强调用字重、颜色、位置
- 检查：check_document 拦截 font-style: italic 以及未重置的默认斜体标签
- 依据：[中文排版需求](https://www.w3.org/TR/clreq)

### PAT-092 图表文字反向缩放保持 12 像素
- 适用：后台；行业：通用；使用 1 次，最近 2026-10-27
- 要点：矢量图表按 viewBox 缩放时文字跟着放大缩小，导致不同图表坐标字号不同；渲染后计算 k = 实际宽度 / viewBox 宽度，文字字号写成 calc(12px / k)
- 实现：fitCharts() 在每次渲染后为 svg.chart 设置 --k；窗口尺寸变化时重算

### PAT-148 扁平线性风格：纯色与线稿，不用立体和渐变
- 适用：小程序、后台、智能体、网站；行业：通用；使用 2 次，最近 2026-10-29
- 要点：“扁平”管图形，“立体感”只属于表面：控件图标、头像与图表始终是平面矢量（纯色面加统一 2 像素描边，不画体积、透视、光泽、投影与渐变）；入口图标、插画与装饰元素可按用户在视觉审批时选定的风格用 Imagegen 生成（一个产品一种风格、透明底、无文字）；卡片、浮层与按钮按五级层级令牌表达前后关系（双层中性阴影、1 像素发丝边、遮罩、主按钮 1 像素按下阶底边与实色面 16%–24% 内顶部高光）。仍禁止装饰渐变（照片遮罩与骨架流光除外）、半透明玻璃与背景模糊、发光与主色投影、斜面与内凹、拟物纹理、有机斑点。判断：去掉阴影与细线后仍是一张完整的扁平稿。
- 反例：九宫格立体图标切图、橙色渐变头部、内凹立体按钮、外发光、半透明玻璃卡、插画椭圆投影；以及另一极端：灰底白块没有边线与阴影、对话框与卡片同一阴影、主按钮像平贴色块
- 依据：尼尔森诺曼集团扁平 2.0；谷歌材料设计第三版、流畅设计二代、蚂蚁设计体系、亚特拉斯、北极星的层级与阴影
- 检查：check_document.py interface 模式拦截渐变、斜面、发光、彩色投影、玻璃、斑点；check_contrast.py 核对层级令牌形状
- 依据：[尼尔森诺曼集团 扁平设计的起源、问题与扁平 2.0](https://www.nngroup.com/articles/flat-design)；[维基百科 扁平设计](https://en.wikipedia.org/wiki/Flat_design)；[谷歌材料设计第三版 层级](https://m3.material.io/styles/elevation/overview)；[亚特拉斯设计体系 层级](https://atlassian.design/foundations/elevation)；[蚂蚁设计体系 阴影](https://ant.design/docs/spec/shadow)；[流畅设计二代 高度](https://fluent2.microsoft.design/elevation)；[谷歌材料设计第三版 应用高度](https://m3.material.io/styles/elevation/applying-elevation)；[肖普菲北极星设计体系 阴影令牌源码](https://github.com/Shopify/polaris/blob/main/polaris-tokens/src/themes/base/shadow.ts)

### PAT-149 一套线性图标：线宽统一、强调靠浅底块
- 适用：小程序、后台、智能体、网站；行业：通用；使用 2 次，最近 2026-10-29
- 要点：全站一套 24 栅格描边图标，线宽 2 像素并设为不随尺寸缩放（16 像素按钮内图标可 1.75，任何尺寸不细于 1.75），圆角端点与连接；导航、底部标签、按钮内与工具操作用单色描边、颜色跟旁边文字；入口、指标、设施与空状态用双色图标块：第 1 阶浅底圆角 8 的方块，描边取按下阶或模块点缀色实色阶，主体内一个面填第 2 阶。尺寸：按钮内 16，菜单 20，底部标签 22–24，图标块 32–40。
- 反例：1.5 像素灰线图标显得单薄；菜单 1.7 像素、返回键 2.2 像素混用；彩色面性图标与线性图标混排；导航图标用双色
- 依据：琉西德图标设计指南（2 像素、不混用线宽）、蚂蚁设计体系图标、磷光图标双色字重、碳设计体系图标尺寸
- 依据：[蚂蚁设计体系 图标](https://ant.design/docs/spec/icon)；[琉西德图标设计语言](https://lucide.dev/contribute/icon-design-guide)；[碳设计体系 图标用法](https://carbondesignsystem.com/elements/icons/usage)；[磷光图标 双色字重](https://phosphoricons.com/)

### PAT-159 一物一图：不同对象不共用图标
- 适用：小程序、后台、智能体、网站；行业：通用；使用 1 次，最近 2026-10-28
- 要点：不同对象不共用同一个图形，同一对象各处同一个图形：每日抽奖用转盘、新人礼券用礼盒、优惠券用券面、中奖记录用奖杯、月卡用日历、次卡用计次卡、可购套餐用购物袋、会员权益用皇冠、面积用面积框、设施服务用宫格、协议用签字文档、最近入场用历史时钟、可转赠用双向箭头。通用控件（返回、箭头、关闭、勾选）不受限。不把同一个通用图标（设置、文件）挂在多个不同标题前，没有合适图形宁可不放。验收：浏览器逐页列出图标与相邻文字，同一图形对应两个不同对象即退回；check_document.py 对静态网页做同样检查。
- 反例：健身房原型里礼盒同时代表新人礼券、每日抽奖、可转赠和后台抽奖菜单；皇冠同时代表月卡、可购套餐、会员权益；配置面板每组标题都是设置图标
- 依据：[尼尔森诺曼集团 图标可用性](https://www.nngroup.com/articles/icon-usability)；[维基百科 扁平设计](https://en.wikipedia.org/wiki/Flat_design)

### PAT-160 网页字体：一条字体栈、不小于 12 像素
- 适用：小程序、后台、智能体、网站；行业：通用；使用 1 次，最近 2026-10-28
- 要点：所有网页、原型、规范页、模板写同一条字体栈、同一顺序：苹方、微软雅黑、思源黑体、系统无衬线；不另加西文、宋体、楷体、圆体。任何网页文字不小于 12 像素（网站与阅读页 14），矢量图坐标、内联样式、脚本生成的文字同样适用；发布脚本与会话校验的原型下限从 11 提到 12。check_document.py 检查样式表外的字号、非通用字体与矢量图字体。
- 反例：规范页样式表、模板、原型三处字体栈顺序各不相同；发布脚本允许原型 11 像素注释
- 依据：[网页内容无障碍指南 概览](https://www.w3.org/WAI/standards-guidelines/wcag/glance)

### PAT-162 五级层级：双层阴影、发丝线与遮罩
- 适用：小程序、后台、智能体、网站；行业：通用；使用 1 次，最近 2026-10-29
- 要点：0 底面（页面底、输入框）无阴影；1 静止卡片：1 像素发丝线加 0 1px 2px 6% + 0 2px 6px 4%；2 悬停与拖动：0 2px 4px 6% + 0 8px 16px 8%；3 下拉、气泡、滚过后的吸顶栏：0 4px 8px 6% + 0 12px 24px 10%；4 对话框与底部弹层：0 8px 16px 8% + 0 24px 48px 14% 加 45% 遮罩。阴影色 rgba(16,24,40) 或主题第 10 阶暗调；只向下（贴底的栏向上镜像）；远处一层逐级更大更柔、单位面积浓度逐级降低；状态整级切换，静止时同屏不超过三级；阅读型页面只用第 0 级与细线。令牌在 themes.json shared.elevation。
- 检查：check_contrast.py 核对每级两层、只向下、近锐远柔、逐级变大变淡、透明度 ≤ 0.2；check_document.py 对令牌外阴影、向上阴影与阅读页卡片阴影给出警告
- 依据：[蚂蚁设计体系 阴影](https://ant.design/docs/spec/shadow)；[流畅设计二代 高度](https://fluent2.microsoft.design/elevation)；[谷歌材料设计第三版 应用高度](https://m3.material.io/styles/elevation/applying-elevation)；[谷歌材料设计第三版 高度令牌](https://m3.material.io/styles/elevation/tokens)；[蚂蚁设计体系 颜色映射令牌源码（遮罩）](https://github.com/ant-design/ant-design/blob/master/components/theme/themes/shared/genColorMapToken.ts)；[碳设计体系 颜色用法（分层）](https://carbondesignsystem.com/elements/color/usage)；[苹果人机界面指南 材质](https://developer.apple.com/design/human-interface-guidelines/materials)；[约什·科莫 设计阴影](https://www.joshwcomeau.com/css/designing-shadows)；[尼尔森诺曼集团 卡片](https://www.nngroup.com/articles/cards-component)

## 文件规则

### PAT-155 单表验收清单：功能验收与甲方配合同表
- 适用：表格；行业：企业服务、财务；使用 1 次，最近 2026-10-28
- 要点：一个工作表按 类别（功能验收 / 甲方配合）区分两类行，不拆分段；列为 类别、模块、事项、验收标准与配合要求、甲方岗位、完成节点、结果、确认人（不加序号列，类别与模块纵向合并）；结果列按行段各用一套下拉（通过 / 有条件通过 / 不通过；按时完成 / 延迟完成 / 未完成）；末尾两行公式合计“功能验收通过率”“甲方配合按时完成率”，让配合度可量化，延期时有事实依据
- 行高：按长文本列每行约 29 个汉字估算行数，32 会在实际导出中裁切
- 验证：WPS/Excel COM 重新打开并导出 PDF，pypdfium2 渲染逐页检查

### PAT-158 表格文件：12 磅、无序号、分组名纵向合并、浅色层次
- 适用：通用；行业：通用；使用 2 次，最近 2026-10-28
- 要点：用 scripts/make_xlsx.py 从描述文件生成表格：微软雅黑，标题 18 磅，其余一律 12 磅；不加序号列；同一列连续重复的分组名（类别、子系统、区域、门店、月份）上下合并成一格，多级分组上级在左、下级只在上级组内合并；数据区不做横向合并；一格一个事实，复合内容拆列或拆行；表头拂晓蓝第 1 阶浅底，第一级分组格按组轮换官方色板第 1 阶，相邻分组交替白与极浅灰，合计浅灰；细浅灰边框、关闭网格线、冻结表头与分组列、设置打印。要筛选、导入或读屏使用的表不合并。生成后跑 check_document.py。一条标准含多个要点时按分号拆成多行；合并按源数据计算，不按读回的单元格值（已合并格读回为空会拆错）；长表按分组插入分页符，跨页的大合并格只在一页显示文字。
- 反例：其他智能体生成的表：11 磅、1/2/3 序号列、同一类别名在 2–10 行重复、纯白无层次
- 检查：check_document.py 拦截低于 12 磅、序号列、未合并的重复分组名、数据区横向合并，并提示表头无浅底
- 依据：[微软 合并与取消合并单元格](https://support.microsoft.com/en-us/office/merge-and-unmerge-cells-5cbd15d5-9375-4540-907f-c673a93fcedf)；[微软 表格无障碍最佳实践](https://support.microsoft.com/en-us/office/make-your-excel-documents-accessible-to-people-with-disabilities-6cc05fc5-1314-48b5-8eb3-683e49b3e593)；[尼尔森诺曼集团 数据表格的四类任务](https://www.nngroup.com/articles/data-tables)；[蚂蚁设计体系 色彩](https://ant.design/docs/spec/colors)

### PAT-161 文字文档按类型排版：合同、方案、报告、纪要、公文
- 适用：通用；行业：通用；使用 1 次，最近 2026-10-28
- 要点：用 scripts/make_docx.py 生成：微软雅黑，标题 22、一二三级 16/14/12、正文 12 磅 1.5 倍、表格 10.5 磅浅底表头重复，不低于 10.5 磅。合同：标题、编号、各方信息、鉴于条款、第一条/1.1/1.1.1 条款覆盖民法典第四百七十条一般条款、金额小写加大写、（以下无正文）、两列签署栏、页脚第 X 页共 Y 页、附件另起页、不留【请填写】×× 占位。方案：一、（一）1.（1），计划、分工、报价、验收用表格，金额处处一致。报告结论在前；纪要以决定事项表收尾；公文只在用户要求时按 GB/T 9704。check_document.py 拦截合同缺项与占位文字。
- 注意：民法典第四百七十条原文三个来源都没抓取成功，条款清单按法条通行文本写入
- 依据：[国务院 党政机关公文处理工作条例](https://www.gov.cn/zwgk/2013-02/22/content_2337704.htm)；[党政机关公文格式（国家标准 GB/T 9704-2012）](https://baike.baidu.com/item/%E5%85%9A%E6%94%BF%E6%9C%BA%E5%85%B3%E5%85%AC%E6%96%87%E6%A0%BC%E5%BC%8F)；[合同示范文本（市场监管总局合同示范文本库）](https://baike.baidu.com/item/%E5%90%88%E5%90%8C%E7%A4%BA%E8%8C%83%E6%96%87%E6%9C%AC)

### PAT-164 文字文档论文版式：宋体正文、黑体标题不加粗、自动编号
- 适用：通用；行业：通用；使用 1 次，最近 2026-10-29
- 要点：用户要求按论文的文字标准排申请、报告、方案时，make_docx.py 描述文件写 "style": "paper"：A4，上下 2.54、左右 3.17 厘米，页眉页脚 1.5 厘米；标题黑体小二居中、一级标题黑体四号顶左段前 24 段后 6、二三级黑体小四，标题都不加粗（黑体无真粗体，模拟加粗发糊）；标题序号用 Word 多级列表自动编号，一级 1、（或 1.），二级 1.1、三级 1.1.1，不手打数字和空格；正文宋体小四、西文 Times New Roman、首行缩进 2 字符、1.5 倍行距、两端对齐；表格按普通浅色网格浅底表头，宋体五号，不用三线表；页码 Times New Roman 五号居中；文字全黑。检查用 check_document.py --allow paper。
- 取舍：规范原文标题加粗、序号后空一个汉字、页码小五；用户嫌加粗发糊、全角空格像占位，页码按 10.5 磅下限取五号
- 被否定的方案：GB/T 9704 公文格式（3 号仿宋正文太大）、全文单一黑体或楷体
- 依据：[中国科学院大学研究生学位论文撰写规范指导意见](http://www.las.cas.cn/yjsjy2021/pyyxw/xwglgd2021/202112/t20211229_6329144.html)；[国家标准 GB/T 7713.2-2022 学术论文编写规则](https://openstd.samr.gov.cn/bzgk/std/newGbInfo?hcno=0B963916637B8F34B295FCF4A51A1BE5)

## 设计理念

### PAT-099 主色按行业气质选，不沿用上一个项目
- 适用：小程序、后台、网页；行业：通用；使用 1 次，最近 2026-10-27
- 要点：先写产品要让人感到什么（活力、信赖、食欲、安心、精致），再按气质选色相；营销辅色与主色相差 90 度以上；主色深一档给按钮、亮一档给图形；旧素材颜色冲突时重新生成
- 依据：[健身应用配色](https://octet.design/colors/palette/fitness-app-color-palette-1731930882)

### PAT-146 配色按标准取阶，不凭感觉调深调浅
- 适用：小程序、后台、通用；行业：通用；使用 1 次，最近 2026-10-27
- 要点：60-30-10：中性色占大面积，强调色约一成留给主行动；主色与辅色从官方 10 阶色板取：品牌阶取白字达 4.5:1 的一阶，悬停浅一阶、按下深一阶、浅底取最浅一阶；一屏一个实色主按钮，次要与营销用浅底容器配同色深字；激活态控件和图表色对白底至少 3:1，不用介于浅底与实色之间的半浅色；按钮不用渐变；图表取同一阶，“其他”用灰。 主色与辅色按配色和谐选：优先邻近色，互补色只作小面积对比，不并置彩度相近的两个饱和色相。
- 触发：用户先后反馈“配色太重”“不要有过亮的颜色，要找标准、多找参考”
- 检查：check_document.py interface 模式拦截主按钮渐变与对白底不足 3:1 的激活态控件填充；check_contrast.py 校验白字与浅底文字对比
- 依据：[Ant Design 色彩](https://ant.design/docs/spec/colors-cn)；[TDesign 色彩](https://tdesign.tencent.com/design/color)；[Material 3 颜色角色](https://m3.material.io/styles/color/roles)；[Carbon 色彩概览](https://carbondesignsystem.com/elements/color/overview)；[Apple 人机界面指南 颜色](https://developer.apple.com/design/human-interface-guidelines/color)；[NN/g 用色增强设计](https://www.nngroup.com/articles/color-enhance-design)；[Datawrapper 数据可视化配色指南](https://blog.datawrapper.de/colors-for-data-vis-style-guides)；[WCAG 2.1 理解 1.4.11 非文本对比](https://www.w3.org/WAI/WCAG21/Understanding/non-text-contrast.html)；[Atlassian 色彩概览](https://atlassian.design/foundations/color-new)；[Material 3 高级颜色定制](https://m3.material.io/styles/color/advanced/adjust-existing-colors)；[Canva 色轮与配色类型](https://www.canva.com/colors/color-wheel)；[维基百科 色彩和谐](https://en.wikipedia.org/wiki/Harmony_(color))；[Figma 100 组配色](https://www.figma.com/resource-library/color-combinations)；[Smashing Magazine 色彩理论第二部分](https://www.smashingmagazine.com/2010/02/color-theory-for-designers-part-2-understanding-concepts-and-terminology)

### PAT-163 多层扁平插画
- 适用：小程序、后台、智能体、网站；行业：通用；使用 1 次，最近 2026-10-29
- 要点：空状态、结果页、登录引导、首页问候与产品封面用多层扁平插画：深色 2 像素描边（主色第 9 阶或正文深色），2–4 个主题纯色面（主色第 1、2–3 阶，模块点缀色第 1–2 阶，中性浅灰），至多 1 个实色强调（面积不超过一成）；主体、配件、地面三层，每张 12–30 个形状；不加阴影、渐变、高光、透视与发光；品牌主卡里改用白色 2 像素线稿或 10%–16% 白色纯色形。
- 取代：白底深灰线稿、最多一处主色的旧画法（用户 2026-10-29 反馈图案太简单）
- 检查：check_document.py 对不在主题阶与中性浅灰里的填色给出警告
- 依据：[昂德劳 开源插画库](https://undraw.co/)；[故事集插画库](https://storyset.com/)

## 来源

| 编号 | 类别 | 来源 | 可借鉴 | 采集日期 | 复用 |
| :---: | :---: | :--- | :--- | :---: | :---: |
| SRC-001 | 视觉规范 | [微信小程序设计指南](https://developers.weixin.qq.com/miniprogram/design/) | 标签独立、二级页返回、异常状态必须给出下一步 | 2026-10-26 | 可复用快照 |
| SRC-013 | 视觉规范 | [中后台字体规范](https://ant.design/docs/spec/font-cn) | 一个字体家族、3–5 级字号、两种字重、数字等宽 | 2026-10-27 | 可复用快照 |
| SRC-014 | 视觉规范 | [饿了么桌面组件库字号令牌](https://github.com/element-plus/element-plus/blob/dev/packages/theme-chalk/src/common/var.scss) | 后台辅助 12、正文 14、标题 16 与 20 | 2026-10-26 | 知识，无快照 |
| SRC-015 | 视觉规范 | [腾讯设计体系字号令牌](https://github.com/Tencent/tdesign-common/blob/develop/style/web/theme/_font.less) | 后台字阶与对应行高 | 2026-10-26 | 知识，无快照 |
| SRC-016 | 视觉规范 | [字节跳动设计体系字号令牌](https://github.com/arco-design/arco-design/blob/main/components/style/theme/global.less) | 后台正文 14，标题 16/20/24 | 2026-10-26 | 知识，无快照 |
| SRC-017 | 视觉规范 | [苹果界面规范字体](https://developer.apple.com/design/human-interface-guidelines/typography) | 移动端正文 17、最小字号不低于 11 | 2026-10-26 | 知识，无快照 |
| SRC-020 | 组件库 | [宫格组件](https://vant-ui.github.io/vant/#/zh-CN/grid) | 4 或 5 列图标宫格 | 2026-10-26 | 可复用快照 |
| SRC-021 | 组件库 | [通知栏组件](https://vant-ui.github.io/vant/#/zh-CN/notice-bar) | 单行滚动 + 左侧图标 + 主题浅底 | 2026-10-26 | 可复用快照 |
| SRC-022 | 组件库 | [底部动作栏组件](https://vant-ui.github.io/vant/#/zh-CN/action-bar) | 左侧客服与门店图标，右侧立即购买 | 2026-10-26 | 可复用快照 |
| SRC-031 | 视觉规范 | [字体与数字字体规范](https://tdesign.tencent.com/design/fonts) | 显式声明字体族并覆盖所有元素，包括图表文字与输入框 | 2026-10-27 | 可复用快照 |
| SRC-032 | 视觉规范 | [中文排版需求](https://www.w3.org/TR/clreq) | 中文界面不用斜体表达强调 | 2026-10-27 | 可复用快照 |
| SRC-039 | 视觉规范 | [健身应用配色](https://octet.design/colors/palette/fitness-app-color-palette-1731930882) | 浅底加橙紫双强调色，核心与营销分色 | 2026-10-27 | 可复用快照 |
| SRC-046 | 视觉规范 | [Ant Design 色彩](https://ant.design/docs/spec/colors-cn) | 火山色板作主色、金盏花色板作营销辅色、取阶规则与克制原则 | 2026-10-27 | 可复用快照 |
| SRC-047 | 视觉规范 | [TDesign 色彩](https://tdesign.tencent.com/design/color) | 主按钮白字达标的色阶、悬停与按下各移一阶、暖白中性底 | 2026-10-27 | 可复用快照 |
| SRC-048 | 视觉规范 | [Material 3 颜色角色](https://m3.material.io/styles/color/roles) | 一个实心主按钮，其余强调用浅底容器加同色深字 | 2026-10-27 | 可复用快照 |
| SRC-049 | 视觉规范 | [Carbon 色彩概览](https://carbondesignsystem.com/elements/color/overview) | 中性色主导、彩色只给操作与状态 | 2026-10-27 | 可复用快照 |
| SRC-050 | 视觉规范 | [Apple 人机界面指南 颜色](https://developer.apple.com/design/human-interface-guidelines/color) | 一色一义、节制用色 | 2026-10-27 | 可复用快照 |
| SRC-051 | 视觉规范 | [NN/g 用色增强设计](https://www.nngroup.com/articles/color-enhance-design) | 中性色占大面积，强调色约一成 | 2026-10-27 | 可复用快照 |
| SRC-052 | 视觉规范 | [Datawrapper 数据可视化配色指南](https://blog.datawrapper.de/colors-for-data-vis-style-guides) | 图表用官方色板中饱和度适中的一阶，“其他”用灰 | 2026-10-27 | 可复用快照 |
| SRC-053 | 视觉规范 | [WCAG 2.1 理解 1.4.11 非文本对比](https://www.w3.org/WAI/WCAG21/Understanding/non-text-contrast.html) | 激活态控件与图表色对白底至少 3:1 | 2026-10-27 | 可复用快照 |
| SRC-054 | 视觉规范 | [Atlassian 色彩概览](https://atlassian.design/foundations/color-new) | 按角色和强调层级取色，不按感觉取色 | 2026-10-27 | 可复用快照 |
| SRC-055 | 视觉规范 | [Material 3 高级颜色定制](https://m3.material.io/styles/color/advanced/adjust-existing-colors) | 辅色与主色同色相降彩度，第三色才换色相 | 2026-10-27 | 可复用快照 |
| SRC-056 | 视觉规范 | [Canva 色轮与配色类型](https://www.canva.com/colors/color-wheel) | 单色或邻近色为基础，一个主导色 | 2026-10-27 | 可复用快照 |
| SRC-057 | 视觉规范 | [维基百科 色彩和谐](https://en.wikipedia.org/wiki/Harmony_(color)) | 营销取主色邻近色，互补色只作小面积对比 | 2026-10-27 | 可复用快照 |
| SRC-058 | 视觉规范 | [Figma 100 组配色](https://www.figma.com/resource-library/color-combinations) | 橙配金琥珀表达活力，紫只能柔化后少量使用 | 2026-10-27 | 可复用快照 |
| SRC-059 | 视觉规范 | [Smashing Magazine 色彩理论第二部分](https://www.smashingmagazine.com/2010/02/color-theory-for-designers-part-2-understanding-concepts-and-terminology) | 营销色用浅底容器拉开彩度，不与主色实色同彩度并置 | 2026-10-27 | 可复用快照 |
| SRC-060 | 视觉规范 | [尼尔森诺曼集团 扁平设计的起源、问题与扁平 2.0](https://www.nngroup.com/articles/flat-design) | 图形扁平，仅用最轻的阴影提示卡片与可点击层 | 2026-10-28 | 可复用快照 |
| SRC-061 | 视觉规范 | [维基百科 扁平设计](https://en.wikipedia.org/wiki/Flat_design) | 纯色、简单几何、线性图形 | 2026-10-28 | 可复用快照 |
| SRC-062 | 视觉规范 | [维基百科 图表垃圾](https://en.wikipedia.org/wiki/Chartjunk) | 网格用最浅的线色，去掉渐变填充与立体 | 2026-10-28 | 可复用快照 |
| SRC-063 | 视觉规范 | [谷歌材料设计第三版 层级](https://m3.material.io/styles/elevation/overview) | 卡片最低一级，浮层中级 | 2026-10-28 | 可复用快照 |
| SRC-064 | 视觉规范 | [尼尔森诺曼集团 图标可用性](https://www.nngroup.com/articles/icon-usability) | 每个菜单项和功能按钮图标加文字 | 2026-10-28 | 可复用快照 |
| SRC-065 | 视觉规范 | [亚特拉斯设计体系 层级](https://atlassian.design/foundations/elevation) | 卡片轻阴影或细边框二选一 | 2026-10-28 | 可复用快照 |
| SRC-066 | 视觉规范 | [蚂蚁设计体系 阴影](https://ant.design/docs/spec/shadow) | 卡片用低级，下拉与对话框用中高级，颜色为中性黑低透明度 | 2026-10-28 | 可复用快照 |
| SRC-067 | 视觉规范 | [蚂蚁设计体系 图标](https://ant.design/docs/spec/icon) | 一套描边图标、统一线宽与圆角 | 2026-10-28 | 可复用快照 |
| SRC-068 | 视觉规范 | [琉西德图标设计语言](https://lucide.dev/contribute/icon-design-guide) | 24 栅格、统一线宽、圆角端点 | 2026-10-28 | 可复用快照 |
| SRC-069 | 视觉规范 | [碳设计体系 图标用法](https://carbondesignsystem.com/elements/icons/usage) | 按钮内 16 像素，菜单 20 像素，单色 | 2026-10-28 | 可复用快照 |
| SRC-070 | 视觉规范 | [苹果人机界面指南 图表数据](https://developer.apple.com/design/human-interface-guidelines/charting-data) | 一张图一个问题，去掉装饰 | 2026-10-28 | 可复用快照 |
| SRC-080 | 视觉规范 | [网页内容无障碍指南 概览](https://www.w3.org/WAI/standards-guidelines/wcag/glance) | 对比度、键盘可操作、替代文本 | 2026-10-28 | 可复用快照 |
| SRC-081 | 文件规范 | [微软 合并与取消合并单元格](https://support.microsoft.com/en-us/office/merge-and-unmerge-cells-5cbd15d5-9375-4540-907f-c673a93fcedf) | 先确认合并范围内的值相同再合并 | 2026-10-28 | 可复用快照 |
| SRC-082 | 文件规范 | [微软 表格无障碍最佳实践](https://support.microsoft.com/en-us/office/make-your-excel-documents-accessible-to-people-with-disabilities-6cc05fc5-1314-48b5-8eb3-683e49b3e593) | 要筛选、导入或读屏使用的表不合并；文字与底色对比达标 | 2026-10-28 | 可复用快照 |
| SRC-083 | 文件规范 | [尼尔森诺曼集团 数据表格的四类任务](https://www.nngroup.com/articles/data-tables) | 分组与名称放左侧，便于扫读与比较 | 2026-10-28 | 可复用快照 |
| SRC-084 | 文件规范 | [蚂蚁设计体系 色彩](https://ant.design/docs/spec/colors) | 浅色底取各色第 1 阶，文字用深灰 | 2026-10-28 | 可复用快照 |
| SRC-085 | 文件规范 | [国务院 党政机关公文处理工作条例](https://www.gov.cn/zwgk/2013-02/22/content_2337704.htm) | 公文要素顺序 | 2026-10-28 | 可复用快照 |
| SRC-086 | 文件规范 | [党政机关公文格式（国家标准 GB/T 9704-2012）](https://baike.baidu.com/item/%E5%85%9A%E6%94%BF%E6%9C%BA%E5%85%B3%E5%85%AC%E6%96%87%E6%A0%BC%E5%BC%8F) | 用户要求公文格式时按此排版 | 2026-10-28 | 可复用快照 |
| SRC-087 | 文件规范 | [合同示范文本（市场监管总局合同示范文本库）](https://baike.baidu.com/item/%E5%90%88%E5%90%8C%E7%A4%BA%E8%8C%83%E6%96%87%E6%9C%AC) | 按同类示范文本确定条款 | 2026-10-28 | 可复用快照 |
| SRC-088 | 视觉规范 | [流畅设计二代 高度](https://fluent2.microsoft.design/elevation) | 每级双层阴影、模糊逐级增大、卡片用描边定边缘 | 2026-10-29 | 可复用快照 |
| SRC-089 | 视觉规范 | [谷歌材料设计第三版 应用高度](https://m3.material.io/styles/elevation/applying-elevation) | 少数几级层级、交互升一级、遮罩 | 2026-10-29 | 可复用快照 |
| SRC-090 | 视觉规范 | [谷歌材料设计第三版 高度令牌](https://m3.material.io/styles/elevation/tokens) | 组件静止层级与交互升级 | 2026-10-29 | 可复用快照 |
| SRC-091 | 视觉规范 | [蚂蚁设计体系 颜色映射令牌源码（遮罩）](https://github.com/ant-design/ant-design/blob/master/components/theme/themes/shared/genColorMapToken.ts) | 遮罩 45% | 2026-10-29 | 可复用快照 |
| SRC-092 | 视觉规范 | [肖普菲北极星设计体系 阴影令牌源码](https://github.com/Shopify/polaris/blob/main/polaris-tokens/src/themes/base/shadow.ts) | 主按钮底边与实色面内顶部高光 | 2026-10-29 | 可复用快照 |
| SRC-093 | 视觉规范 | [碳设计体系 颜色用法（分层）](https://carbondesignsystem.com/elements/color/usage) | 页面底与卡片交替分层，卡片内用浅灰分区 | 2026-10-29 | 可复用快照 |
| SRC-094 | 视觉规范 | [苹果人机界面指南 材质](https://developer.apple.com/design/human-interface-guidelines/materials) | 深度来自分层而非装饰 | 2026-10-29 | 可复用快照 |
| SRC-095 | 视觉规范 | [约什·科莫 设计阴影](https://www.joshwcomeau.com/css/designing-shadows) | 阴影只向下、双层令牌、主题暗调阴影 | 2026-10-29 | 可复用快照 |
| SRC-096 | 视觉规范 | [尼尔森诺曼集团 卡片](https://www.nngroup.com/articles/cards-component) | 白卡、发丝边、最轻一级阴影、内缩分隔 | 2026-10-29 | 可复用快照 |
| SRC-097 | 视觉规范 | [尼尔森诺曼集团 视觉层级](https://www.nngroup.com/articles/visual-hierarchy-ux-definition) | 标题与数字三级拉开，其余靠字重与颜色 | 2026-10-29 | 可复用快照 |
| SRC-098 | 视觉规范 | [碳设计体系 字体字阶](https://carbondesignsystem.com/elements/typography/type-sets) | 小标题 600、层级靠字号 | 2026-10-29 | 可复用快照 |
| SRC-099 | 视觉规范 | [谷歌材料设计第三版 字阶令牌](https://m3.material.io/styles/typography/type-scale-tokens) | 600 与 700 只给标题、数字与强调 | 2026-10-29 | 可复用快照 |
| SRC-100 | 视觉规范 | [磷光图标 双色字重](https://phosphoricons.com/) | 双色图标块：描边加一个浅色面 | 2026-10-29 | 可复用快照 |
| SRC-101 | 视觉规范 | [昂德劳 开源插画库](https://undraw.co/) | 多层扁平插画、颜色全部取主题阶 | 2026-10-29 | 可复用快照 |
| SRC-102 | 视觉规范 | [故事集插画库](https://storyset.com/) | 主体、配件、地面三层 | 2026-10-29 | 可复用快照 |
| SRC-103 | 文件规范 | [中国科学院大学研究生学位论文撰写规范指导意见](http://www.las.cas.cn/yjsjy2021/pyyxw/xwglgd2021/202112/t20211229_6329144.html) | 论文版式的字体字号、页边距与编号方式 | 2026-10-29 | 可复用快照 |
| SRC-104 | 文件规范 | [国家标准 GB/T 7713.2-2022 学术论文编写规则](https://openstd.samr.gov.cn/bzgk/std/newGbInfo?hcno=0B963916637B8F34B295FCF4A51A1BE5) | 论文版式的标准依据与现行状态 | 2026-10-29 | 可复用快照 |
