# Luz Design 经验库

每次调用开始先读本页并运行 `py -X utf8 scripts/experience.py search <关键词>`：偏好与教训直接照做，能复用的配色、字阶与视觉、文件规则直接沿用，只为缺口做新的调研。结束前用 `note` 按主题键写入新的偏好、教训与有效信息（`experience/notes.json`），同一个键覆盖旧条目。本页由 `scripts/experience.py` 生成，修改请用命令或改 JSON。

## 偏好（13/60）

- **excel-layout**：Excel 最小 12 磅、标题 18 磅；不加序号列；同列重复的分组名纵向合并；一格只写一个事实；用浅色底区分层次。用 make_xlsx.py 生成。　确认 1 次，最近 2026-10-28
- **export-cleaned-chinese**：系统导出的表格是清洗后的中文数据：中文表头、枚举译成中文、日期年-月-日 时:分、金额两位小数单位在表头、去掉内部编号技术字段与空列、范围等于当前筛选、中文文件名带范围，用表格生成脚本出版式（用户要求导出给人看的数据，不是数据库原表）　确认 1 次，最近 2026-10-28
- **fitness-palette**：健身行业主色用火山橙，营销用金色，二者是邻近色、和谐不冲突。　确认 1 次，最近 2026-10-28
- **flat-line-style**：界面一律扁平线性：纯色或白底深灰线稿，不用立体、渐变、纹理、玻璃与发光；海报与宣传图可以用摄影照片。（用户多次纠正立体图标与渐变按钮）　确认 1 次，最近 2026-10-28
- **html-tab-icon-required**：每个交付的网页都要有浏览器标签页图标：内联 SVG，32 栅格、圆角 8 浅底、主色线稿、最多 3 个形状、无文字、16 像素可辨认，同一系统各页同一图案；后台与网站页头放同一图案的图形品牌标识；模板与生成脚本内置图标参数，check_document 缺失即报错（用户要求（2026-10-28））　确认 1 次，最近 2026-10-28
- **interface-density-14px**：界面密度：后台正文与表格 14 像素、行高 22，辅助 12 像素只给时间、单位、角标；字号 3–5 种；8 像素网格，卡片内边距 16–20、间距 16；表格行高 44–48，紧凑 36–40；1440×900 首屏至少 10 行，统计卡不超过 112 像素，不留大块空白（用户反馈后台字太小、留白太多、密度低；依据蚂蚁、腾讯字体规范与碳设计体系数据表格）　确认 1 次，最近 2026-10-28
- **list-pagination-default-20**：后台与网站里可能超过一页的列表都要分页：默认每页 20 条，可选 10/20/50/100 条/页；分页条在表格下方靠右，14 像素文字、32 像素控件、当前页主色；页码与条数写进地址并记住用户选择；小程序与移动端滚动加载，每批 20 条（用户要求（2026-10-28）；依据 Element Plus、Ant Design、TDesign 分页组件与 NN/g 分页偏好研究）　确认 1 次，最近 2026-10-28
- **no-italics**：中文产出禁用斜体，强调用字重或颜色，不用倾斜与旋转文字。　确认 1 次，最近 2026-10-28
- **one-font-stack**：每个文件只用一条字体栈（苹方、微软雅黑、思源黑体、系统无衬线），网页任何文字不小于 12 像素，网站与阅读页正文不小于 14 像素。　确认 1 次，最近 2026-10-28
- **one-object-one-icon**：一物一图：不同对象不共用同一个图标，同一对象在各处用同一个图标。　确认 1 次，最近 2026-10-28
- **palette-by-industry**：配色按行业气质从官方 10 阶色板取阶，不凭感觉调深调浅；中性色、主色、强调色按 60-30-10 分配，文字对比度达到 4.5:1。　确认 1 次，最近 2026-10-28
- **table-centred**：表格对齐：表头居中；数据不顶格，左右内边距不小于 16 像素；长文本左对齐并收紧列宽，使文字块落在表头下方；状态、日期、负责人、操作等短值居中；需比较大小的金额右对齐、等宽数字、单位写在表头；分组标题加粗（用户纠正：宽列表头居中而文字贴左边显得错位，取代原“表头与数据都居中”）　确认 2 次，最近 2026-10-28
- **word-by-type**：Word 文档先定类型（合同、方案、报告、会议纪要、公文），按该类型的结构与格式排版，用 make_docx.py 生成。　确认 1 次，最近 2026-10-28

## 组件

### PAT-149 一套线性图标：线宽统一、强调靠浅底块
- 适用：小程序、后台；行业：通用；使用 1 次，最近 2026-10-28
- 要点：全站只用一套 24 栅格描边图标，线宽 1.5 像素并设为不随尺寸缩放（矢量描边不缩放），圆角端点与连接，颜色跟旁边文字；入口、设施、权益、指标卡用主色浅底阶圆角块承托图标、图标用按下阶；底部标签当前项主色、未选中灰色，不用灰度滤镜。尺寸：按钮内 16，菜单 20，底部标签 22–24，图标块 32–40。
- 反例：菜单 1.7 像素、返回键 2.2 像素、放大到 30 像素的图标线条变粗；彩色面性图标与线性图标混排
- 依据：蚂蚁设计体系图标（统一线宽是体系统一的关键）、琉西德设计语言（不混用线宽）、碳设计体系图标尺寸
- 依据：[蚂蚁设计体系 图标](https://ant.design/docs/spec/icon)；[琉西德图标设计语言](https://lucide.dev/contribute/icon-design-guide)；[碳设计体系 图标用法](https://carbondesignsystem.com/elements/icons/usage)

### PAT-155 单表验收清单：功能验收与甲方配合同表
- 适用：表格；行业：企业服务、财务；使用 1 次，最近 2026-10-28
- 要点：一个工作表按 类别（功能验收 / 甲方配合）区分两类行，不拆分段；列为 类别、模块、事项、验收标准与配合要求、甲方岗位、完成节点、结果、确认人（不加序号列，类别与模块纵向合并）；结果列按行段各用一套下拉（通过 / 有条件通过 / 不通过；按时完成 / 延迟完成 / 未完成）；末尾两行公式合计“功能验收通过率”“甲方配合按时完成率”，让配合度可量化，延期时有事实依据
- 行高：按长文本列每行约 29 个汉字估算行数，32 会在实际导出中裁切
- 验证：WPS/Excel COM 重新打开并导出 PDF，pypdfium2 渲染逐页检查

## 色彩

### PAT-017 健身房·健身房小程序和后台系统配色
- 适用：小程序、后台；行业：健身房；使用 1 次，最近 2026-10-27
- 要点：canvas #f7f5f4
- 令牌：canvas #f7f5f4；surface #fff；soft #f6f4f3；ink #241e1b；ink2 #5b544f；ink3 #68625d；line #ebe7e5；line2 #dcd7d3；brand #c2410c；brand-press #9a3412；brand-2 #f97316；brand-3 #fdba8c；brand-tint #fff1e6；brand-mid #dd6224；gold #a14a07；gold-2 #f59e0b；gold-tint #fff3e0；gold-line #f6d7a8；success #146c36；success-tint #e6f4ea；danger #be123c；danger-tint #ffe9ee；promo #6d28d9；promo-2 #8b5cf6；promo-tint #f3eeff；promo-line #ddd3fb
- 对比度：ink 于 canvas 15.1；ink2 于 surface 7.4；success 于 success-tint 5.7；danger 于 danger-tint 5.4

### PAT-084 健身·健身房小程序和后台系统配色
- 适用：小程序、后台；行业：健身；使用 1 次，最近 2026-10-28
- 要点：canvas #f5f5f5
- 令牌：canvas #f5f5f5；surface #fff；soft #fafafa；ink #1f1f1f；ink2 #595959；ink3 #666666；line #f0f0f0；line2 #d9d9d9；brand #d4380d；brand-press #ad2102；brand-hover #fa541c；brand-2 #fa541c；brand-3 #ffbb96；brand-tint #fff2e8；brand-mid #d4380d；mk #874d00；mk-tint #fffbe6；mk-fill #fff1b8；mk-line #ffe58f；gold #a14a07；gold-2 #faad14；gold-tint #fff3e0；gold-line #f6d7a8；success #146c36；success-tint #e6f4ea；danger #cf1322；danger-tint #fff1f0；promo #874d00；promo-2 #d48806；promo-tint #fffbe6；promo-line #ffe58f
- 对比度：ink 于 canvas 15.1；ink2 于 surface 7.0；success 于 success-tint 5.7；danger 于 danger-tint 5.1

### PAT-098 健身房配色：活力橙核心 + 金色营销
- 适用：小程序、后台；行业：健身；使用 1 次，最近 2026-10-27
- 要点：按 Ant Design 官方色板取阶：主色火山 volcano，主按钮、开关、勾选用 volcano-6 #D4380D 实色白字（4.8:1），悬停 volcano-5 #FA541C，按下 volcano-7 #AD2102，浅底 volcano-0 #FFF2E8，浅底上的橙字用 #AD2102；营销取邻近色金盏花 gold，领取、抽奖用 gold-1 #FFF1B8 容器底配 gold-8 #874D00 文字（色调按钮），券面 gold-0 #FFFBE6；危险红 red-6 #CF1322；星级 gold-7 #AD6800；图表主系列火山 #FA541C，其余取金 #FFC53D、浅橙 #FFBB96、浅蓝 #69B1FF，“其他”用灰 #BFBFBF；中性暖白 #FAF8F6。
- 反例：自造深橙渐变配深紫实色按钮（显重）；随后改成半浅粉橙粉紫配深字（发飘，开关对白底不足 3:1）；饱和橙配饱和紫（彩度相近、既不邻近也不互补，用户评价“黄色和紫色不搭”）
- 依据：SRC-046～SRC-054
- 依据：[健身应用配色](https://octet.design/colors/palette/fitness-app-color-palette-1731930882)；[Ant Design 色彩](https://ant.design/docs/spec/colors-cn)；[TDesign 色彩](https://tdesign.tencent.com/design/color)；[Material 3 颜色角色](https://m3.material.io/styles/color/roles)；[NN/g 用色增强设计](https://www.nngroup.com/articles/color-enhance-design)；[Datawrapper 数据可视化配色指南](https://blog.datawrapper.de/colors-for-data-vis-style-guides)；[WCAG 2.1 理解 1.4.11 非文本对比](https://www.w3.org/WAI/WCAG21/Understanding/non-text-contrast.html)；[Material 3 高级颜色定制](https://m3.material.io/styles/color/advanced/adjust-existing-colors)；[Canva 色轮与配色类型](https://www.canva.com/colors/color-wheel)；[维基百科 色彩和谐](https://en.wikipedia.org/wiki/Harmony_(color))；[Figma 100 组配色](https://www.figma.com/resource-library/color-combinations)；[Smashing Magazine 色彩理论第二部分](https://www.smashingmagazine.com/2010/02/color-theory-for-designers-part-2-understanding-concepts-and-terminology)

## 字阶

### PAT-018 小程序字阶
- 适用：小程序；行业：通用；使用 1 次，最近 2026-10-26
- 要点：11 / 12 / 13 / 14 / 16 / 18，价格与大数字 22；正文 14（设计稿 28）
- 用途：11 注释与角标；12 辅助信息与标签；13 次要正文；14 正文、列表标题、按钮；16 卡片与模块标题；18 页面标题；22 价格与大数字
- 调整原因：用户反馈以 17 为正文的小程序字体过大；商用小程序正文多为 14，微信指南的 17 只适合页面标题级
- 依据：[微信小程序设计指南](https://developers.weixin.qq.com/miniprogram/design/)；[苹果界面规范字体](https://developer.apple.com/design/human-interface-guidelines/typography)

### PAT-019 桌面后台字阶
- 适用：后台；行业：通用；使用 1 次，最近 2026-10-26
- 要点：12 / 14 / 16 / 20 / 28；正文与表格 14，行高 22
- 用途：12 时间戳、表单提示；14 正文、表格、表单、按钮、菜单；16 卡片、抽屉、弹窗标题；20 页面标题；28 指标数字
- 行高：12/20、14/22、16/24、20/28、28/36
- 依据：[中后台字体规范](https://ant.design/docs/spec/font-cn)；[饿了么桌面组件库字号令牌](https://github.com/element-plus/element-plus/blob/dev/packages/theme-chalk/src/common/var.scss)；[腾讯设计体系字号令牌](https://github.com/Tencent/tdesign-common/blob/develop/style/web/theme/_font.less)；[字节跳动设计体系字号令牌](https://github.com/arco-design/arco-design/blob/main/components/style/theme/global.less)

### PAT-020 阅读型网页字阶
- 适用：网页；行业：通用；使用 1 次，最近 2026-10-26
- 要点：14 / 16 / 20 / 24 / 32；正文 16，按 1.25 倍递进，最小 14
- 用途：14 辅助与数字表格；16 正文与整句表格；20 三级标题；24 二级标题；32 主标题

### PAT-090 产品交付网页三部分共用一套字体与字阶
- 适用：小程序、后台、网页；行业：通用；使用 1 次，最近 2026-10-27
- 要点：功能列表、小程序、后台放在一个网页里时：同一字体族（苹方、微软雅黑、思源黑体回退），字阶 12/14/16/18/22/28，网页主标题 32；每个字号只配一个行高 12/18、14/22、16/24、18/26、22/30、28/36；正文 14；不用 11、13、15、20、24 等中间值
- 来源：用户反馈：后台、小程序、功能列表字体不统一
- 检查：原型测试统计所有可见文字的字体族与字号；check_document --allow interface 拦截字阶外字号
- 依据：[中后台字体规范](https://ant.design/docs/spec/font-cn)；[字体与数字字体规范](https://tdesign.tencent.com/design/fonts)

## 前端规则

### PAT-031 禁用态的对比度
- 适用：通用；行业：通用；使用 1 次，最近 2026-10-26
- 要点：禁用按钮用浅灰底配灰字，文字对比度至少 4.5:1；禁用图形至少 3:1；不要用灰底白字
- 推荐：背景 #e9eeee，文字 #5f6874
- 旁注：禁用必须就地写明原因，例如“勾选同意后才能拍摄或上传”

### PAT-032 圆角三档与胶囊
- 适用：通用；行业：通用；使用 1 次，最近 2026-10-26
- 要点：界面只用 4（标签与小部件）、8（控件）、12（卡片、弹层、页面框）三档；胶囊与圆形统一 999

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
- 适用：小程序、后台；行业：通用；使用 1 次，最近 2026-10-28
- 要点：所有产品界面用扁平风格：图形只用简单纯色，或白底深灰线条的镂空线稿；不用立体图标、图像生成的图标拼板、彩色面性渐变图标、装饰渐变、纹理、半透明玻璃、有机斑点、斜面内凹按钮与发光阴影。只有照片上的黑色透明度遮罩和加载骨架流光可以用渐变。页面底浅白或极浅灰，卡片白底配最轻一级中性阴影形成轻微悬浮，浮层高一级；卡片圆角 12，输入框与按钮 8。
- 反例：九宫格立体图标切图、橙色渐变头部、抽奖格子底部内凹的立体按钮、中奖格外发光、个人中心半透明玻璃卡、背景白色斑点、插画下的椭圆投影
- 依据：尼尔森诺曼集团与维基百科扁平设计；谷歌材料设计第三版、亚特拉斯、蚂蚁设计体系的层级与阴影
- 检查：check_document.py interface 模式拦截装饰渐变、斜面与发光阴影、卡片厚阴影、背景模糊、斑点圆角、矢量渐变与位图图标
- 依据：[尼尔森诺曼集团 扁平设计的起源、问题与扁平 2.0](https://www.nngroup.com/articles/flat-design)；[维基百科 扁平设计](https://en.wikipedia.org/wiki/Flat_design)；[谷歌材料设计第三版 层级](https://m3.material.io/styles/elevation/overview)；[亚特拉斯设计体系 层级](https://atlassian.design/foundations/elevation)；[蚂蚁设计体系 阴影](https://ant.design/docs/spec/shadow)

### PAT-158 表格文件：12 磅、无序号、分组名纵向合并、浅色层次
- 适用：通用；行业：通用；使用 2 次，最近 2026-10-28
- 要点：用 scripts/make_xlsx.py 从描述文件生成表格：微软雅黑，标题 18 磅，其余一律 12 磅；不加序号列；同一列连续重复的分组名（类别、子系统、区域、门店、月份）上下合并成一格，多级分组上级在左、下级只在上级组内合并；数据区不做横向合并；一格一个事实，复合内容拆列或拆行；表头拂晓蓝第 1 阶浅底，第一级分组格按组轮换官方色板第 1 阶，相邻分组交替白与极浅灰，合计浅灰；细浅灰边框、关闭网格线、冻结表头与分组列、设置打印。要筛选、导入或读屏使用的表不合并。生成后跑 check_document.py。一条标准含多个要点时按分号拆成多行；合并按源数据计算，不按读回的单元格值（已合并格读回为空会拆错）；长表按分组插入分页符，跨页的大合并格只在一页显示文字。
- 反例：其他智能体生成的表：11 磅、1/2/3 序号列、同一类别名在 2–10 行重复、纯白无层次
- 检查：check_document.py 拦截低于 12 磅、序号列、未合并的重复分组名、数据区横向合并，并提示表头无浅底
- 依据：[微软 合并与取消合并单元格](https://support.microsoft.com/en-us/office/merge-and-unmerge-cells-5cbd15d5-9375-4540-907f-c673a93fcedf)；[微软 表格无障碍最佳实践](https://support.microsoft.com/en-us/office/make-your-excel-documents-accessible-to-people-with-disabilities-6cc05fc5-1314-48b5-8eb3-683e49b3e593)；[尼尔森诺曼集团 数据表格的四类任务](https://www.nngroup.com/articles/data-tables)；[蚂蚁设计体系 色彩](https://ant.design/docs/spec/colors)

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

### PAT-161 文字文档按类型排版：合同、方案、报告、纪要、公文
- 适用：通用；行业：通用；使用 1 次，最近 2026-10-28
- 要点：用 scripts/make_docx.py 生成：微软雅黑，标题 22、一二三级 16/14/12、正文 12 磅 1.5 倍、表格 10.5 磅浅底表头重复，不低于 10.5 磅。合同：标题、编号、各方信息、鉴于条款、第一条/1.1/1.1.1 条款覆盖民法典第四百七十条一般条款、金额小写加大写、（以下无正文）、两列签署栏、页脚第 X 页共 Y 页、附件另起页、不留【请填写】×× 占位。方案：一、（一）1.（1），计划、分工、报价、验收用表格，金额处处一致。报告结论在前；纪要以决定事项表收尾；公文只在用户要求时按 GB/T 9704。check_document.py 拦截合同缺项与占位文字。
- 注意：民法典第四百七十条原文三个来源都没抓取成功，条款清单按法条通行文本写入
- 依据：[国务院 党政机关公文处理工作条例](https://www.gov.cn/zwgk/2013-02/22/content_2337704.htm)；[党政机关公文格式（国家标准 GB/T 9704-2012）](https://baike.baidu.com/item/%E5%85%9A%E6%94%BF%E6%9C%BA%E5%85%B3%E5%85%AC%E6%96%87%E6%A0%BC%E5%BC%8F)；[合同示范文本（市场监管总局合同示范文本库）](https://baike.baidu.com/item/%E5%90%88%E5%90%8C%E7%A4%BA%E8%8C%83%E6%96%87%E6%9C%AC)

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

## 来源

| 编号 | 类别 | 来源 | 可借鉴 | 采集日期 | 复用 |
|---|---|---|---|---|---|
| SRC-001 | 交互流程 | [微信小程序设计指南](https://developers.weixin.qq.com/miniprogram/design/) | 标签独立、二级页返回、异常状态必须给出下一步 | 2026-10-26 | 可复用快照 |
| SRC-013 | 页面结构 | [中后台字体规范](https://ant.design/docs/spec/font-cn) | 一个字体家族、3–5 级字号、两种字重、数字等宽 | 2026-10-27 | 可复用快照 |
| SRC-014 | 前端规则 | [饿了么桌面组件库字号令牌](https://github.com/element-plus/element-plus/blob/dev/packages/theme-chalk/src/common/var.scss) | 后台辅助 12、正文 14、标题 16 与 20 | 2026-10-26 | 知识，无快照 |
| SRC-015 | 前端规则 | [腾讯设计体系字号令牌](https://github.com/Tencent/tdesign-common/blob/develop/style/web/theme/_font.less) | 后台字阶与对应行高 | 2026-10-26 | 知识，无快照 |
| SRC-016 | 前端规则 | [字节跳动设计体系字号令牌](https://github.com/arco-design/arco-design/blob/main/components/style/theme/global.less) | 后台正文 14，标题 16/20/24 | 2026-10-26 | 知识，无快照 |
| SRC-017 | 前端规则 | [苹果界面规范字体](https://developer.apple.com/design/human-interface-guidelines/typography) | 移动端正文 17、最小字号不低于 11 | 2026-10-26 | 知识，无快照 |
| SRC-020 | 页面结构 | [宫格组件](https://vant-ui.github.io/vant/#/zh-CN/grid) | 4 或 5 列图标宫格 | 2026-10-26 | 可复用快照 |
| SRC-021 | 组件状态 | [通知栏组件](https://vant-ui.github.io/vant/#/zh-CN/notice-bar) | 单行滚动 + 左侧图标 + 主题浅底 | 2026-10-26 | 可复用快照 |
| SRC-022 | 交互流程 | [底部动作栏组件](https://vant-ui.github.io/vant/#/zh-CN/action-bar) | 左侧客服与门店图标，右侧立即购买 | 2026-10-26 | 可复用快照 |
| SRC-031 | 页面结构 | [字体与数字字体规范](https://tdesign.tencent.com/design/fonts) | 显式声明字体族并覆盖所有元素，包括图表文字与输入框 | 2026-10-27 | 可复用快照 |
| SRC-032 | 页面结构 | [中文排版需求](https://www.w3.org/TR/clreq) | 中文界面不用斜体表达强调 | 2026-10-27 | 可复用快照 |
| SRC-039 | 页面结构 | [健身应用配色](https://octet.design/colors/palette/fitness-app-color-palette-1731930882) | 浅底加橙紫双强调色，核心与营销分色 | 2026-10-27 | 可复用快照 |
| SRC-046 | 前端规则 | [Ant Design 色彩](https://ant.design/docs/spec/colors-cn) | 火山色板作主色、金盏花色板作营销辅色、取阶规则与克制原则 | 2026-10-27 | 可复用快照 |
| SRC-047 | 前端规则 | [TDesign 色彩](https://tdesign.tencent.com/design/color) | 主按钮白字达标的色阶、悬停与按下各移一阶、暖白中性底 | 2026-10-27 | 可复用快照 |
| SRC-048 | 前端规则 | [Material 3 颜色角色](https://m3.material.io/styles/color/roles) | 一个实心主按钮，其余强调用浅底容器加同色深字 | 2026-10-27 | 可复用快照 |
| SRC-049 | 前端规则 | [Carbon 色彩概览](https://carbondesignsystem.com/elements/color/overview) | 中性色主导、彩色只给操作与状态 | 2026-10-27 | 可复用快照 |
| SRC-050 | 前端规则 | [Apple 人机界面指南 颜色](https://developer.apple.com/design/human-interface-guidelines/color) | 一色一义、节制用色 | 2026-10-27 | 可复用快照 |
| SRC-051 | 前端规则 | [NN/g 用色增强设计](https://www.nngroup.com/articles/color-enhance-design) | 中性色占大面积，强调色约一成 | 2026-10-27 | 可复用快照 |
| SRC-052 | 前端规则 | [Datawrapper 数据可视化配色指南](https://blog.datawrapper.de/colors-for-data-vis-style-guides) | 图表用官方色板中饱和度适中的一阶，“其他”用灰 | 2026-10-27 | 可复用快照 |
| SRC-053 | 前端规则 | [WCAG 2.1 理解 1.4.11 非文本对比](https://www.w3.org/WAI/WCAG21/Understanding/non-text-contrast.html) | 激活态控件与图表色对白底至少 3:1 | 2026-10-27 | 可复用快照 |
| SRC-054 | 前端规则 | [Atlassian 色彩概览](https://atlassian.design/foundations/color-new) | 按角色和强调层级取色，不按感觉取色 | 2026-10-27 | 可复用快照 |
| SRC-055 | 前端规则 | [Material 3 高级颜色定制](https://m3.material.io/styles/color/advanced/adjust-existing-colors) | 辅色与主色同色相降彩度，第三色才换色相 | 2026-10-27 | 可复用快照 |
| SRC-056 | 前端规则 | [Canva 色轮与配色类型](https://www.canva.com/colors/color-wheel) | 单色或邻近色为基础，一个主导色 | 2026-10-27 | 可复用快照 |
| SRC-057 | 前端规则 | [维基百科 色彩和谐](https://en.wikipedia.org/wiki/Harmony_(color)) | 营销取主色邻近色，互补色只作小面积对比 | 2026-10-27 | 可复用快照 |
| SRC-058 | 前端规则 | [Figma 100 组配色](https://www.figma.com/resource-library/color-combinations) | 橙配金琥珀表达活力，紫只能柔化后少量使用 | 2026-10-27 | 可复用快照 |
| SRC-059 | 前端规则 | [Smashing Magazine 色彩理论第二部分](https://www.smashingmagazine.com/2010/02/color-theory-for-designers-part-2-understanding-concepts-and-terminology) | 营销色用浅底容器拉开彩度，不与主色实色同彩度并置 | 2026-10-27 | 可复用快照 |
| SRC-060 | 前端规则 | [尼尔森诺曼集团 扁平设计的起源、问题与扁平 2.0](https://www.nngroup.com/articles/flat-design) | 图形扁平，仅用最轻的阴影提示卡片与可点击层 | 2026-10-28 | 可复用快照 |
| SRC-061 | 前端规则 | [维基百科 扁平设计](https://en.wikipedia.org/wiki/Flat_design) | 纯色、简单几何、线性图形 | 2026-10-28 | 可复用快照 |
| SRC-062 | 前端规则 | [维基百科 图表垃圾](https://en.wikipedia.org/wiki/Chartjunk) | 网格用最浅的线色，去掉渐变填充与立体 | 2026-10-28 | 可复用快照 |
| SRC-063 | 前端规则 | [谷歌材料设计第三版 层级](https://m3.material.io/styles/elevation/overview) | 卡片最低一级，浮层中级 | 2026-10-28 | 可复用快照 |
| SRC-064 | 前端规则 | [尼尔森诺曼集团 图标可用性](https://www.nngroup.com/articles/icon-usability) | 每个菜单项和功能按钮图标加文字 | 2026-10-28 | 可复用快照 |
| SRC-065 | 前端规则 | [亚特拉斯设计体系 层级](https://atlassian.design/foundations/elevation) | 卡片轻阴影或细边框二选一 | 2026-10-28 | 可复用快照 |
| SRC-066 | 前端规则 | [蚂蚁设计体系 阴影](https://ant.design/docs/spec/shadow) | 卡片用低级，下拉与对话框用中高级，颜色为中性黑低透明度 | 2026-10-28 | 可复用快照 |
| SRC-067 | 前端规则 | [蚂蚁设计体系 图标](https://ant.design/docs/spec/icon) | 一套描边图标、统一线宽与圆角 | 2026-10-28 | 可复用快照 |
| SRC-068 | 前端规则 | [琉西德图标设计语言](https://lucide.dev/contribute/icon-design-guide) | 24 栅格、统一线宽、圆角端点 | 2026-10-28 | 可复用快照 |
| SRC-069 | 前端规则 | [碳设计体系 图标用法](https://carbondesignsystem.com/elements/icons/usage) | 按钮内 16 像素，菜单 20 像素，单色 | 2026-10-28 | 可复用快照 |
| SRC-070 | 前端规则 | [苹果人机界面指南 图表数据](https://developer.apple.com/design/human-interface-guidelines/charting-data) | 一张图一个问题，去掉装饰 | 2026-10-28 | 可复用快照 |
| SRC-080 | 前端规则 | [网页内容无障碍指南 概览](https://www.w3.org/WAI/standards-guidelines/wcag/glance) | 对比度、键盘可操作、替代文本 | 2026-10-28 | 可复用快照 |
| SRC-081 | 前端规则 | [微软 合并与取消合并单元格](https://support.microsoft.com/en-us/office/merge-and-unmerge-cells-5cbd15d5-9375-4540-907f-c673a93fcedf) | 先确认合并范围内的值相同再合并 | 2026-10-28 | 可复用快照 |
| SRC-082 | 前端规则 | [微软 表格无障碍最佳实践](https://support.microsoft.com/en-us/office/make-your-excel-documents-accessible-to-people-with-disabilities-6cc05fc5-1314-48b5-8eb3-683e49b3e593) | 要筛选、导入或读屏使用的表不合并；文字与底色对比达标 | 2026-10-28 | 可复用快照 |
| SRC-083 | 前端规则 | [尼尔森诺曼集团 数据表格的四类任务](https://www.nngroup.com/articles/data-tables) | 分组与名称放左侧，便于扫读与比较 | 2026-10-28 | 可复用快照 |
| SRC-084 | 前端规则 | [蚂蚁设计体系 色彩](https://ant.design/docs/spec/colors) | 浅色底取各色第 1 阶，文字用深灰 | 2026-10-28 | 可复用快照 |
| SRC-085 | 前端规则 | [国务院 党政机关公文处理工作条例](https://www.gov.cn/zwgk/2013-02/22/content_2337704.htm) | 公文要素顺序 | 2026-10-28 | 可复用快照 |
| SRC-086 | 前端规则 | [党政机关公文格式（国家标准 GB/T 9704-2012）](https://baike.baidu.com/item/%E5%85%9A%E6%94%BF%E6%9C%BA%E5%85%B3%E5%85%AC%E6%96%87%E6%A0%BC%E5%BC%8F) | 用户要求公文格式时按此排版 | 2026-10-28 | 可复用快照 |
| SRC-087 | 前端规则 | [合同示范文本（市场监管总局合同示范文本库）](https://baike.baidu.com/item/%E5%90%88%E5%90%8C%E7%A4%BA%E8%8C%83%E6%96%87%E6%9C%AC) | 按同类示范文本确定条款 | 2026-10-28 | 可复用快照 |
