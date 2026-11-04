#!/usr/bin/env python3
"""主题配色纪律审计：补 check_contrast.py 没覆盖的“配色是否有纪律”，并给“主题 + 图标 + 圆角 + 层级 + 字阶 + 动效”的搭配做兼容性检查。

    py -X utf8 scripts/audit_theme_discipline.py                                  # themes.json 全部主题跑 A–F，打印矩阵、汇总与明细
    py -X utf8 scripts/audit_theme_discipline.py --theme xiangcai --theme coffee  # 只跑指定主题
    py -X utf8 scripts/audit_theme_discipline.py --json out.json --md out.md      # 同时写 JSON 与 Markdown 报告
    py -X utf8 scripts/audit_theme_discipline.py --combo ai-agent duotone standard soft compact calm
    py -X utf8 scripts/audit_theme_discipline.py --combo ai-agent clay3d round glass bold friendly --icon-roles controls,entry --glass-roles navigation

不重复 check_contrast.py 已查的项（关键对比度、深色映射键与对比度、层级阴影、色阶第 1/6/7 阶与第 2–3、9 阶、模块点缀色色相差）；
这里补的是：色阶质量（A）、同一色相家族（B）、色相预算与区分度（C）、色觉差异（D）、面积与层级纪律（E）、深色配套纪律（F）、搭配兼容（G）。

严重度三级：FAIL 硬规则（用词为“要求”“不能”的）、WARN 纪律偏差、INFO 描述性事实。退出码：有 FAIL 返回 1，否则 0。
本脚本只报告，不修改 themes.json。

颜色换算统一用 OKLab / OKLCH（Ottosson 2020，直接复用 make_dark.py 的 hex_to_oklch）；对比度用 WCAG 2.2 相对亮度（阈值 0.04045，复用 check_contrast.py），不用 APCA。
库用法：audit_theme(theme_id, theme, shared) -> list[Finding]；check_combo(theme_id, icons, shape, depth, type_pack, motion, ...) -> dict。
"""
from __future__ import annotations

import argparse
import json
import math
import sys
from dataclasses import asdict, dataclass, field
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import check_contrast as cc  # noqa: E402
import make_dark as md  # noqa: E402

THEMES = Path(__file__).resolve().parents[1] / "references" / "themes.json"

# ---- 阈值常量（每条一行：值 + 依据；“经验值”可由用户裁定）-------------------------------------------------------------------------------

CHROMATIC_C = 0.04            # OKLCH 彩度 C >= 0.04 才算“有彩色”参与色相统计；经验值，可由用户裁定（与 audit_palette 的有彩判断同量级）
HUE_RELIABLE_C = 0.02         # C < 0.02 时 OKLCH 色相不稳定（8 位取整的 ±0.002 在 C = 0.02 时已约 ±6 度），色相比较时跳过；经验值，可由用户裁定

A1_MAX_STEP_RATIO = 2.2       # 色阶相邻阶 OKLCH 亮度差的最大/最小比 <= 2.2，避免两阶几乎一样、另两阶跳变（用户指定）；经验值，可由用户裁定
A2_MAX_HUE_DRIFT = 12.0       # 10 阶色相相对第 6 阶的最大偏差 <= 12 度（与 check_contrast 深色色相漂移 MAX_DARK_HUE_DRIFT 同标准）
A3_PEAK_INDEXES = range(3, 8)  # 彩度峰值落在第 4–8 阶（索引 3–7）才算“中间阶最高”；经验值，可由用户裁定
A3_CHROMA_NOISE = 0.004       # 彩度曲线允许的取整噪声（8 位 sRGB 取整在 OKLCH 彩度上约 0.002–0.004），在此内的起伏算平台
A3_END_DROP = 0.01            # 两端阶（第 1、10 阶）彩度至少比峰值低 0.01 才算“两端降低”；经验值，可由用户裁定

B1_MAX_HUE_GAP = 12.0         # action / actionPress / actionTint / 第 6 阶 色相两两 <= 12 度（与 check_contrast 的 canvas 同色相标准 12 度一致）
B2_NEUTRAL_C = 0.02           # canvas / surface / navBg 中性：OKLCH C < 0.02（用户指定）
B2_TINT_MAX_C = 0.03          # 或与主色同色相时 C <= 0.03（极浅底，用户指定）
B2_TINT_HUE_GAP = 15.0        # “同色相”指与主色相差 <= 15 度（用户指定）
B3_INK_MAX_C = 0.03           # ink / ink2 / ink3 的 C <= 0.03，正文字色不染色（用户指定）

C1_CLUSTER_WIDTH = 20.0       # 色相簇宽 20 度：同簇内的颜色算同一个色相（用户指定）
C1_MAX_CLUSTERS = 7           # 主色、点缀色、四个状态色、价格色合计 <= 7 个色相簇（用户指定）；模块点缀色等额外有彩色相同样计入
C2_MIN_GAP = 20.0             # 主色与 danger、price 的色相距离 >= 20 度，避免“品牌红 = 危险红”混淆（用户指定）
C2_NEAR_OVERLAP = 8.0         # 小于 20 度记 family-overlap 提示；小于 8 度（几乎同一个红）升为 WARN；经验值，可由用户裁定
C3_MIN_GAP = 25.0             # 主色与 accent 色相距离 >= 25 度，否则点缀失去作用（用户指定）
C3_HARMONY_MAX = 60.0         # 25–60 度为邻近色和谐，算通过（visual-design.html 配色：辅色优先邻近色）
C3_CLASH_MAX = 150.0          # 60–150 度记“撞色提示”，大于 150 度记“强对比提示”（互补）；两者是描述，不是错误
C4_MIN_GAP = 25.0             # 四个状态色色相两两 >= 25 度（与 check_contrast 的 MIN_STATUS_GAP / MIN_MODULE_GAP 同标准）

D_KINDS = ("protan", "deut", "tritan")
D1_KINDS = ("protan", "deut")  # 红绿色盲两种：success 与 danger 在这两种下要拉开
D1_MIN_DE = 8.0               # success 与 danger 在 protan / deut 下 OKLab ΔE×100 >= 8（用户指定）；不足提示“状态不能只靠颜色”
D2_MIN_DE = 6.0               # 主色与 accent 在三种模拟下 ΔE×100 >= 6（用户指定）

E1_RANGE = (1.02, 1.20)       # canvas 与 surface 的 WCAG 亮度比：卡片能从底上立起来但不过度（用户指定）
E2_RANGE = (1.1, 1.6)         # line 在 surface 上的对比度：发丝线可见但不抢戏（用户指定）
E3_MIN_RATIO = 1.0            # actionTint 与 canvas 的 WCAG 亮度比 >= 1.0（按 (高+0.05)/(低+0.05) 定义恒成立，仅作记录）
E3_MIN_DE = 3.0               # actionTint 与 canvas 的 OKLab ΔE×100 >= 3，浅底阶能被看见（用户指定）；3 约为并排可辨的下限，经验值

F1_RANGE = (0.12, 0.30)       # 深色 canvas / surface 的 OKLCH L（用户指定；make_dark 派生值为 0.175 / 0.23）
F2_RANGE = (0.0, 0.15)        # 深色 action 比浅色 action 的 OKLCH L 差（深 - 浅）（用户指定）：品牌色在深色里不要变成另一个颜色
F2_LOW_SLACK = 0.01           # F2 下限的取整容差：make_dark 要求白字 4.6:1，比浅色 4.5:1 多一点余量，亮度可能低 0.01 内；经验值
F3_MAX_HUE_GAP = 12.0         # 深色 actionText 与浅色 action 的色相差 <= 12 度（用户指定）

# ---- 搭配（G）常量 ------------------------------------------------------------------------------------------------------------------------

GLASS_MIN_CONTRAST = 4.5      # 文字落在玻璃上的最差对比度 >= 4.5:1（WCAG 2.2 1.4.3 AA，用户指定“要求”）
GLASS_ALPHA_LIGHT = 0.72      # 浅色玻璃：surface 白色 72% 不透明（常见毛玻璃 60–80%）；经验值，可由用户裁定，可用 glass_alpha 覆盖
GLASS_ALPHA_DARK = 0.60       # 深色玻璃：dark.surface 60% 不透明；经验值，可由用户裁定
GLASS_ALLOWED_ROLES = ("hero", "entry-icon")  # visual-design.html 风格矩阵：frosted-glass 只用于 heroDecorations / entryIcons，不用于控制器表面
GLASS_RULING = "需裁定（现规则禁止控制器表面使用毛玻璃）"
CLAY_RULING = "需用户裁定（黏土质感入口图标不在现行风格矩阵允许范围内，现行只允许空状态与主视觉装饰）"

ICON_STYLES = ("line", "duotone", "clay3d")
ICON_ROLES = ("controls", "entry", "empty", "result", "hero")  # 控件、入口、空状态、结果页、主视觉装饰
ICON_ROLES_ALLOWED = {         # visual-design.html 风格矩阵：控件图标始终是统一线性矢量；duotone 只用于入口与空状态；clay3d 只用于入口、空状态、结果页
    "line": ICON_ROLES,
    "duotone": ("entry", "empty"),
    "clay3d": ("entry", "empty", "result"),
}
ICON_ROLES_DEFAULT = {         # 不传 icon_roles 时各风格的典型用法（用户指定：line 用于控件与入口）
    "line": ("controls", "entry"),
    "duotone": ("entry", "empty"),
    "clay3d": ("entry", "empty", "result"),
}
CLAY_RULING_ROLES = ("entry", "result")  # 矩阵里 clay 只允许 empty-state / hero-decoration，用在入口或结果页需用户裁定

# 圆角：标签 / 控件（输入框、按钮、下拉、图标底块）/ 卡片与图片 / 对话框与底部弹层（visual-design.html 层级与立体感 › 圆角：4 / 8 / 12 / 16）
SHAPES = {
    "tight": {"tag": 2, "control": 4, "card": 8, "dialog": 12, "ruling": "圆角 2/4/8/12 不在现行令牌 4/8/12/16 内，需裁定"},
    "standard": {"tag": 4, "control": 8, "card": 12, "dialog": 16, "ruling": ""},
    "round": {"tag": 6, "control": 10, "card": 16, "dialog": 20, "ruling": "圆角 6/10/16/20 不在现行令牌 4/8/12/16 内，需裁定"},
}
DEPTHS = ("hairline", "soft", "glass")

# 字阶：standard 为小程序字阶，compact 为产品交付网页（后台）字阶，bold 沿用小程序字阶只改字重（visual-design.html 字阶 › 产品交付网页与小程序字阶）
MINIAPP_SCALE = (12, 14, 16, 18, 22, 28)
ADMIN_SCALE = (12, 14, 16, 18, 22, 28, 32)
TYPE_PACKS = {
    "standard": {"sizes": MINIAPP_SCALE, "body": "16/24", "note": "小程序字阶 12/14/16/18/22/28，正文 16/24，次要 14/22，标题 600、页面主标题与大号数字 700（仅 >= 22）"},
    "compact": {"sizes": ADMIN_SCALE, "body": "14/22", "note": "后台字阶 12/14/16/18/22/28/32，正文 14/22，辅助 12/18"},
    "bold": {"sizes": MINIAPP_SCALE, "body": "16/24", "note": "沿用小程序字阶，只加大字重对比：标题 700 仅 >= 22，其余标题 600，正文 400"},
}
FONT_WEIGHTS = (400, 600, 700)   # visual-design.html 字重三档，不出现 300、500、800、900
MIN_BOLD_SIZE = 22               # 700 只给不小于 22 像素的页面主标题、详情页价格与大号数字
MOTIONS = {                      # 只描述时长偏好，不改令牌（时长档见 visual-design.html 动效细则：即时 100、快 150、标准 200、中 250–300、页面 280–320）
    "calm": "安静：偏标准档 200 与中档 250–300，退出取进入的 70%–80%，不加回弹，高频交互仍用即时 100 / 快 150",
    "snappy": "利落：偏即时 100 与快档 150，面板与弹层取 200–240，高频交互不加位移，页面转场取 280 下限",
    "friendly": "亲和：以标准档 200 为主，对话框与面板 240 带 0.96 到 1 的缩放淡入，点击回弹用快档 150；小控件不超过 300，面板与页面不超过 320",
}

# 本脚本的局限（写进 Markdown 报告末尾，读报告的人需要知道）
LIMITS = (
    "A 组只覆盖有 scale 的主题（themes.json 里目前只有 ai-agent），其余主题记“不适用”；报告不会替它们推导色阶。",
    "色相统一用 OKLCH，度数与 check_contrast 用的 HSV 色相不同，同一对颜色的“相差多少度”两边不会相等。",
    "C1 的色相簇除主色、点缀色、四个状态色、价格色外，还计入模块点缀色（非品牌）以及彩度 >= 0.04 的 canvas / navBg / actionTint / accentTint；只有这 7 个来源时总数不会超过 7。",
    "E3 的“亮度比 >= 1.0”按 WCAG 比值定义恒成立，真正起作用的是 ΔE >= 3；比 canvas 更暗或更亮只作记录。",
    "色觉模拟（Machado 2009，严重度 1.0）模拟的是二色视，8 位取整使 ΔE 约有 ±0.1 的误差；它不代表异常三色视，也不替代真人测试。",
    "玻璃对比度用的是假设的 tint 与不透明度（浅色 surface 72%、深色 dark.surface 60%），实际 backdrop-filter 的模糊与背景内容变化没有建模。",
    "严重度分级（哪些记 FAIL、哪些记 WARN）是本脚本的判断：只有色阶不单调、正文字色染色、状态色色相过近记 FAIL；其余是 WARN 或 INFO，可由用户裁定。",
    "只报告，不修改 themes.json；“怎么改”是方向，不是已验证的取值。",
)

SEVERITIES = ("FAIL", "WARN", "INFO", "PASS", "NA")   # 由重到轻；NA 表示该主题没有这项的前提（如无 scale、主色为中性色）
CHECK_IDS = ("A1", "A2", "A3", "B1", "B2", "B3", "C1", "C2", "C3", "C4", "D1", "D2", "E1", "E2", "E3", "F1", "F2", "F3")

# 每项的名称、阈值文字、怎么改；scope 为 shared 表示只取决于 shared 令牌（所有主题相同）
CHECKS: dict[str, dict] = {
    "A1": {"title": "色阶亮度单调且步长均匀", "threshold": f"OKLCH L 逐阶下降（FAIL）；相邻阶亮度差最大/最小 <= {A1_MAX_STEP_RATIO}（WARN）",
           "fix": "用 OKLCH 按近似等 L 步长重取色阶（make_dark.oklch_hex），把过密的两阶拉开、跳变处补中间阶；第 1/6/7 阶仍须等于 actionTint / action / actionPress。"},
    "A2": {"title": "色阶色相不漂移", "threshold": f"10 阶色相相对第 6 阶偏差 <= {A2_MAX_HUE_DRIFT:g} 度（C < {HUE_RELIABLE_C} 的阶不计）",
           "fix": "保持第 6 阶的 OKLCH 色相，只调 L 与 C 重取偏离的阶；漂移通常来自在 sRGB / HSL 里直接调深浅。"},
    "A3": {"title": "色阶彩度曲线单峰", "threshold": f"彩度峰值在第 4–8 阶，升段不降、降段不升（噪声 {A3_CHROMA_NOISE}，可有平台），两端比峰值低 >= {A3_END_DROP}",
           "fix": "把彩度峰值放到中间阶，浅端与深端逐步降彩度；中间不要出现凹谷或第二个峰。"},
    "B1": {"title": "主色家族同色相", "threshold": f"action / actionPress / actionTint / scale 第 6 阶色相两两 <= {B1_MAX_HUE_GAP:g} 度（actionTint 彩度过低不计）",
           "fix": "让按压档、浅底阶与主色保持同一 OKLCH 色相，只调 L 与 C。"},
    "B2": {"title": "底色中性或同色相低彩度", "threshold": f"canvas / surface / navBg：C < {B2_NEUTRAL_C}，或与主色同色相（<= {B2_TINT_HUE_GAP:g} 度）且 C <= {B2_TINT_MAX_C}",
           "fix": "把偏色的底色改成中性浅灰，或改成主色色相的极浅底（降彩度到 0.03 以内）。"},
    "B3": {"title": "正文字色不染色", "threshold": f"ink / ink2 / ink3 的 OKLCH C <= {B3_INK_MAX_C}", "scope": "shared",
           "fix": "把染色的正文字色改回中性或近中性深灰（降彩度）；ink 是 shared 令牌，改动影响全部主题。"},
    "C1": {"title": "色相预算", "threshold": f"有彩色（C >= {CHROMATIC_C}）互不相同的色相簇（簇宽 {C1_CLUSTER_WIDTH:g} 度）<= {C1_MAX_CLUSTERS}",
           "fix": "合并或删除装饰色相：模块点缀色并入主色 / 点缀色家族，或把近似色相收到同一簇；状态色与价格色不另加。"},
    "C2": {"title": "主色与 danger / price 区分", "threshold": f"色相距离 >= {C2_MIN_GAP:g} 度；不足记 family-overlap（<{C2_NEAR_OVERLAP:g} 度升 WARN）",
           "fix": "品牌色避开 danger / price 的红色色相；做不到时危险操作与价格必须带图标或文字，危险按钮用 danger 色列实色阶，不用主色。"},
    "C3": {"title": "主色与点缀色关系", "threshold": f"色相距离 >= {C3_MIN_GAP:g} 度；{C3_MIN_GAP:g}–{C3_HARMONY_MAX:g} 邻近色通过，{C3_HARMONY_MAX:g}–{C3_CLASH_MAX:g} 撞色提示，> {C3_CLASH_MAX:g} 强对比提示",
           "fix": "距离不足 25 度时把点缀色换到邻近色（25–60 度）或明确的对比色；撞色与强对比只是描述，点缀面积要小并经用户确认。"},
    "C4": {"title": "状态色之间区分", "threshold": f"success / warning / danger / info 色相两两 >= {C4_MIN_GAP:g} 度", "scope": "shared",
           "fix": "拉开相邻状态色的色相；这些是 shared 令牌，改动影响全部主题，且需同步 shared.dark。"},
    "D1": {"title": "红绿色觉差异", "threshold": f"success 与 danger 在 protan、deut 模拟下 ΔE×100 >= {D1_MIN_DE:g}", "scope": "shared",
           "fix": "状态不能只靠颜色，必须带图标或文字；也可拉开 success 与 danger 的明度（OKLCH L）。"},
    "D2": {"title": "主色与点缀色的色觉差异", "threshold": f"主色与 accent 在 protan / deut / tritan 模拟下 ΔE×100 >= {D2_MIN_DE:g}",
           "fix": "把点缀色与主色的明度（OKLCH L）拉开 0.1 以上，不只靠色相区分；必要时点缀信息带图标或文字。"},
    "E1": {"title": "canvas 与 surface 立体差", "threshold": f"WCAG 亮度比在 {E1_RANGE[0]}–{E1_RANGE[1]} 之间",
           "fix": "比值过小则把 canvas 略调暗，过大则调亮；卡片靠这点差加发丝线从底上立起来。"},
    "E2": {"title": "line 发丝线可见度", "threshold": f"line 在 surface 上对比度 {E2_RANGE[0]}–{E2_RANGE[1]}", "scope": "shared",
           "fix": "过淡则加深 line，过重则变浅；line 是 shared 令牌，改动影响全部主题。"},
    "E3": {"title": "actionTint 能被看见", "threshold": f"与 canvas 亮度比 >= {E3_MIN_RATIO:g} 且 ΔE×100 >= {E3_MIN_DE:g}",
           "fix": "把 actionTint 取得比 canvas 更有色相（提高 C）或略拉开明度，让选中态浅底在页面底上可辨。"},
    "F1": {"title": "深色底亮度", "threshold": f"dark.canvas 与 dark.surface 的 OKLCH L 在 {F1_RANGE[0]}–{F1_RANGE[1]} 之间",
           "fix": "用 make_dark 的 canvas L 0.175、surface L 0.23 作基准重取；过黑则抬亮，过灰则压暗。"},
    "F2": {"title": "深色主色明度一致", "threshold": f"dark.action 比 action 的 OKLCH L 差在 {F2_RANGE[0]}–{F2_RANGE[1]} 之间（容差 {F2_LOW_SLACK}）",
           "fix": "深色 action 取同色相、略亮（L 差 <= 0.15）且白字仍 >= 4.5:1；整体换成另一种明度的按钮（如浅色按钮配深字）需用户裁定。"},
    "F3": {"title": "深色品牌文字色相", "threshold": f"dark.actionText 与 action 的色相差 <= {F3_MAX_HUE_GAP:g} 度",
           "fix": "按浅色 action 的 OKLCH 色相重新求解 dark.actionText（make_dark.derive_theme）。"},
}

# ---- 色觉模拟：Machado, Oliveira & Fernandes 2009，严重度 1.0，在线性 sRGB 上乘 ---------------------------------------------------------------

CVD_MATRICES = {
    "protan": ((0.152286, 1.052583, -0.204868), (0.114503, 0.786281, 0.099216), (-0.003882, -0.048116, 1.051998)),
    "deut": ((0.367322, 0.860646, -0.227968), (0.280085, 0.672501, 0.047413), (-0.011820, 0.042940, 0.968881)),
    "tritan": ((1.255528, -0.076749, -0.178779), (-0.078411, 0.930809, 0.147602), (0.004733, 0.691367, 0.303900)),
}


# ---- 颜色小工具（OKLab / OKLCH，复用 make_dark / check_contrast）-----------------------------------------------------------------------

def oklch(color: str) -> tuple[float, float, float]:
    """(L, C, H 度)，H 在 0–360。"""
    return md.hex_to_oklch(cc.normalize_hex(color))


def oklab(color: str) -> tuple[float, float, float]:
    lightness, chroma, hue = oklch(color)
    return lightness, chroma * math.cos(math.radians(hue)), chroma * math.sin(math.radians(hue))


def delta_e(a: str, b: str) -> float:
    """OKLab 距离 × 100。"""
    la, aa, ba = oklab(a)
    lb, ab, bb = oklab(b)
    return 100 * math.sqrt((la - lb) ** 2 + (aa - ab) ** 2 + (ba - bb) ** 2)


def hue_diff(a: float, b: float) -> float:
    d = abs(a - b) % 360
    return min(d, 360 - d)


def hue_of(color: str) -> float:
    return oklch(color)[2]


def chroma_of(color: str) -> float:
    return oklch(color)[1]


def simulate(color: str, kind: str) -> str:
    """色觉缺陷模拟（Machado 2009，严重度 1.0）：线性 sRGB 乘矩阵，越界截断，回到 8 位 sRGB。"""
    matrix = CVD_MATRICES[kind]
    linear = [md._to_linear(v) for v in cc.rgb(cc.normalize_hex(color))]
    out = [max(0.0, min(1.0, sum(row[j] * linear[j] for j in range(3)))) for row in matrix]
    return "#%02X%02X%02X" % tuple(round(md._to_srgb(v) * 255) for v in out)


def cvd_delta_e(a: str, b: str, kind: str) -> float:
    return delta_e(simulate(a, kind), simulate(b, kind))


def composite(top: str, alpha: float, bottom: str) -> str:
    """CSS 的半透明叠加（在 sRGB 值上）：top 以 alpha 不透明度叠在 bottom 上。"""
    return "#%02X%02X%02X" % tuple(round(t * alpha + b * (1 - alpha)) for t, b in zip(cc.rgb(top), cc.rgb(bottom)))


def hue_clusters(items: dict[str, float], width: float) -> list[list[str]]:
    """把 {名称: 色相} 按簇宽归簇：环形排序，从最大空隙之后开始，簇内最大色相跨度 <= width。"""
    if not items:
        return []
    ordered = sorted(items.items(), key=lambda kv: kv[1])
    n = len(ordered)
    gaps = [(ordered[i + 1][1] - ordered[i][1], i) for i in range(n - 1)] + [(ordered[0][1] + 360 - ordered[-1][1], n - 1)]
    start = (max(gaps)[1] + 1) % n
    rotated = [ordered[(start + i) % n] for i in range(n)]
    base = rotated[0][1]
    unwrapped = [(name, (h - base) % 360) for name, h in rotated]
    clusters: list[list[str]] = []
    cluster_start = None
    for name, h in unwrapped:
        if cluster_start is None or h - cluster_start > width:
            clusters.append([])
            cluster_start = h
        clusters[-1].append(name)
    return clusters


# ---- 结果结构 -----------------------------------------------------------------------------------------------------------------------------

@dataclass
class Finding:
    id: str
    status: str            # FAIL / WARN / INFO / PASS / NA
    value: str             # 当前值
    metric: str = ""       # 指标名
    threshold: str = ""    # 阈值
    fix: str = ""          # 怎么改（只在非 PASS / NA 时给）
    scope: str = "theme"   # shared：所有主题相同
    tags: list[str] = field(default_factory=list)
    data: dict = field(default_factory=dict)

    def to_dict(self) -> dict:
        return asdict(self)


def finding(check_id: str, status: str, value: str, tags: list[str] | None = None, **data) -> Finding:
    info = CHECKS[check_id]
    fix = info["fix"] if status in ("FAIL", "WARN") or (status == "INFO" and check_id in ("C2", "C3")) else ""
    return Finding(id=check_id, status=status, value=value, metric=info["title"], threshold=info["threshold"], fix=fix,
                   scope=info.get("scope", "theme"), tags=tags or [], data=data)


def na(check_id: str, reason: str) -> Finding:
    return finding(check_id, "NA", reason)


def deg(value: float) -> str:
    return f"{value:.0f}°"


# ---- A 色阶质量 ---------------------------------------------------------------------------------------------------------------------------

def check_scale(theme: dict) -> list[Finding]:
    scale = theme.get("scale")
    if not scale:
        return [na(i, "无 scale") for i in ("A1", "A2", "A3")]
    if len(scale) != 10:
        return [na(i, f"scale 有 {len(scale)} 阶，不是 10 阶（check_contrast 会报）") for i in ("A1", "A2", "A3")]
    lch = [oklch(c) for c in scale]
    lights, chromas, hues = [x[0] for x in lch], [x[1] for x in lch], [x[2] for x in lch]
    out = []

    diffs = [a - b for a, b in zip(lights, lights[1:])]
    if min(diffs) <= 0:
        bad = [i + 1 for i, d in enumerate(diffs) if d <= 0]
        out.append(finding("A1", "FAIL", "第 " + "、".join(f"{i}→{i + 1}" for i in bad) + f" 阶亮度没有下降（L {' '.join(f'{x:.2f}' for x in lights)}）", lights=lights))
    else:
        ratio = max(diffs) / min(diffs)
        hi, lo = diffs.index(max(diffs)) + 1, diffs.index(min(diffs)) + 1
        text = f"差 max/min = {ratio:.2f}（最大 {max(diffs):.3f} 在第 {hi}→{hi + 1} 阶，最小 {min(diffs):.3f} 在第 {lo}→{lo + 1} 阶；L {lights[0]:.2f}→{lights[-1]:.2f}）"
        out.append(finding("A1", "PASS" if ratio <= A1_MAX_STEP_RATIO else "WARN", text, ratio=round(ratio, 3), lights=[round(x, 4) for x in lights]))

    if chromas[5] < HUE_RELIABLE_C:
        out.append(na("A2", "第 6 阶近中性，色相不稳定"))
    else:
        drift = [(hue_diff(hues[i], hues[5]), i + 1) for i in range(10) if i != 5 and chromas[i] >= HUE_RELIABLE_C]
        worst, step = max(drift) if drift else (0.0, 6)
        out.append(finding("A2", "PASS" if worst <= A2_MAX_HUE_DRIFT else "WARN",
                           f"最大偏差 {deg(worst)}（第 {step} 阶；第 6 阶 {deg(hues[5])}；色相 {' '.join(deg(h) for h in hues)}）", worst=round(worst, 2)))

    peak = max(range(10), key=chromas.__getitem__)
    if chromas[peak] < CHROMATIC_C:
        out.append(na("A3", f"色阶近中性（峰值 C {chromas[peak]:.3f}）"))
    else:
        problems = []
        if peak not in A3_PEAK_INDEXES:
            problems.append(f"峰值在第 {peak + 1} 阶")
        problems += [f"升段第 {i + 1}→{i + 2} 阶下降 {chromas[i] - chromas[i + 1]:.3f}" for i in range(peak) if chromas[i + 1] < chromas[i] - A3_CHROMA_NOISE]
        problems += [f"降段第 {i + 1}→{i + 2} 阶回升 {chromas[i + 1] - chromas[i]:.3f}" for i in range(peak, 9) if chromas[i + 1] > chromas[i] + A3_CHROMA_NOISE]
        if chromas[peak] - chromas[0] < A3_END_DROP or chromas[peak] - chromas[9] < A3_END_DROP:
            problems.append("两端没有比峰值低 %g" % A3_END_DROP)
        curve = " ".join(f"{c:.3f}" for c in chromas)
        out.append(finding("A3", "WARN" if problems else "PASS", f"峰值第 {peak + 1} 阶 C {chromas[peak]:.3f}；" + ("；".join(problems) + "；" if problems else "") + f"曲线 {curve}"))
    return out


# ---- B 同一色相家族 -----------------------------------------------------------------------------------------------------------------------

def check_family(theme: dict, shared: dict) -> list[Finding]:
    out = []
    action = theme.get("action")
    action_chromatic = bool(action) and chroma_of(action) >= CHROMATIC_C
    if not action_chromatic:
        out.append(na("B1", "主色为中性色，无色相可比" if action else "无 action"))
    else:
        named = {"action": theme.get("action"), "actionPress": theme.get("actionPress"), "actionTint": theme.get("actionTint")}
        scale = theme.get("scale")
        if scale and len(scale) == 10:
            named["scale 第 6 阶"] = scale[5]
        named = {k: v for k, v in named.items() if v}
        used = {k: hue_of(v) for k, v in named.items() if chroma_of(v) >= HUE_RELIABLE_C}
        skipped = [k for k in named if k not in used]
        names = list(used)
        gaps = [(hue_diff(used[a], used[b]), a, b) for i, a in enumerate(names) for b in names[i + 1:]]
        worst = max(gaps) if gaps else (0.0, "", "")
        hue_text = " ".join(f"{k} {deg(h)}" for k, h in used.items())
        text = f"最大两两色相差 {deg(worst[0])}（{worst[1]} 与 {worst[2]}）；{hue_text}" + (f"；不计（彩度过低）：{'、'.join(skipped)}" if skipped else "")
        out.append(finding("B1", "PASS" if worst[0] <= B1_MAX_HUE_GAP else "WARN", text, worst=round(worst[0], 2)))

    offenders, listed = [], []
    ground = {"canvas": theme.get("canvas"), "surface": shared.get("surface", "#FFFFFF"), "navBg": theme.get("navBg")}
    for name, color in ground.items():
        if not color:
            continue
        lightness, chroma, hue = oklch(color)
        neutral = chroma < B2_NEUTRAL_C
        same_hue = action_chromatic and hue_diff(hue, hue_of(action)) <= B2_TINT_HUE_GAP and chroma <= B2_TINT_MAX_C
        listed.append(f"{name} C {chroma:.3f}" + ("" if neutral else f" 色相 {deg(hue)}"))
        if not (neutral or same_hue):
            gap = f"，与主色相差 {deg(hue_diff(hue, hue_of(action)))}" if action_chromatic else ""
            offenders.append(f"{name}（{color}）C {chroma:.3f} 色相 {deg(hue)}{gap}")
    out.append(finding("B2", "WARN" if offenders else "PASS", ("偏色：" + "；".join(offenders)) if offenders else "；".join(listed)))

    ink_chroma = {k: chroma_of(shared[k]) for k in ("ink", "ink2", "ink3") if k in shared}
    tinted = [f"{k} C {c:.3f}" for k, c in ink_chroma.items() if c > B3_INK_MAX_C]
    out.append(finding("B3", "FAIL" if tinted else "PASS", ("染色：" + "、".join(tinted)) if tinted else "、".join(f"{k} C {c:.3f}" for k, c in ink_chroma.items()),
                       chroma={k: round(c, 4) for k, c in ink_chroma.items()}))
    return out


# ---- C 色相预算与区分度 -------------------------------------------------------------------------------------------------------------------

def check_budget(theme: dict, shared: dict) -> list[Finding]:
    out = []
    core = {"主色": theme.get("action"), "点缀色": theme.get("accent")}
    for key in ("success", "warning", "danger", "info", "price"):
        core[key] = shared.get(key)
    extras = {}
    for key, m in (theme.get("modules") or {}).items():
        if not m.get("brand") and m.get("solid"):
            extras[f"module:{key}"] = m["solid"]
    for key in ("canvas", "navBg", "actionTint", "accentTint"):
        if theme.get(key):
            extras[key] = theme[key]
    hues = {k: hue_of(v) for k, v in core.items() if v and chroma_of(v) >= CHROMATIC_C}
    extra_hues = {k: hue_of(v) for k, v in extras.items() if chroma_of(v) >= CHROMATIC_C}
    clusters = hue_clusters({**hues, **extra_hues}, C1_CLUSTER_WIDTH)
    core_clusters = hue_clusters(hues, C1_CLUSTER_WIDTH)
    allh = {**hues, **extra_hues}
    desc = "；".join("+".join(f"{n} {deg(allh[n])}" for n in c) for c in clusters)
    ignored = [k for k, v in core.items() if v and k not in hues]
    text = f"{len(clusters)} 个色相簇（核心 {len(core_clusters)}，额外有彩色 {len(extra_hues)} 个）：{desc}" + (f"；中性不计：{'、'.join(ignored)}" if ignored else "")
    out.append(finding("C1", "PASS" if len(clusters) <= C1_MAX_CLUSTERS else "WARN", text, clusters=len(clusters), extra=sorted(extra_hues)))

    action, accent = theme.get("action"), theme.get("accent")
    if not action or chroma_of(action) < CHROMATIC_C:
        out.append(na("C2", "主色为中性色，不会与 danger / price 的红混淆"))
        out.append(na("C3", "主色为中性色，无色相可比"))
    else:
        h = hue_of(action)
        gaps = {k: hue_diff(h, hue_of(shared[k])) for k in ("danger", "price") if k in shared}
        text = "；".join(f"与 {k} 相差 {deg(g)}" for k, g in gaps.items()) + f"（主色 {deg(h)}）"
        near = min(gaps.values()) if gaps else 360
        if near >= C2_MIN_GAP:
            out.append(finding("C2", "PASS", text))
        else:
            out.append(finding("C2", "WARN" if near < C2_NEAR_OVERLAP else "INFO", text + "；family-overlap", tags=["family-overlap"], gaps={k: round(g, 2) for k, g in gaps.items()}))
        if not accent or chroma_of(accent) < CHROMATIC_C:
            out.append(na("C3", "点缀色为中性色"))
        else:
            gap = hue_diff(h, hue_of(accent))
            text = f"主色 {deg(h)} 与点缀色 {deg(hue_of(accent))} 相差 {deg(gap)}"
            if gap < C3_MIN_GAP:
                out.append(finding("C3", "WARN", text + "：点缀失去作用"))
            elif gap <= C3_HARMONY_MAX:
                out.append(finding("C3", "PASS", text + "：邻近色和谐", tags=["analogous"]))
            elif gap <= C3_CLASH_MAX:
                out.append(finding("C3", "INFO", text + "：撞色提示", tags=["clash"]))
            else:
                out.append(finding("C3", "INFO", text + "：强对比提示（互补）", tags=["complementary"]))

    status = {k: shared[k] for k in ("success", "warning", "danger", "info") if k in shared}
    names = list(status)
    gaps = sorted((hue_diff(hue_of(status[a]), hue_of(status[b])), a, b) for i, a in enumerate(names) for b in names[i + 1:])
    low = [g for g in gaps if g[0] < C4_MIN_GAP]
    text = ("过近：" + "；".join(f"{a} 与 {b} 相差 {deg(g)}" for g, a, b in low)) if low else "最近一对 %s 与 %s 相差 %s" % (gaps[0][1], gaps[0][2], deg(gaps[0][0])) if gaps else "无状态色"
    out.append(finding("C4", "FAIL" if low else "PASS", text))
    return out


# ---- D 色觉差异 ---------------------------------------------------------------------------------------------------------------------------

def check_cvd(theme: dict, shared: dict) -> list[Finding]:
    out = []
    if shared.get("success") and shared.get("danger"):
        des = {k: cvd_delta_e(shared["success"], shared["danger"], k) for k in D1_KINDS}
        low = [k for k, v in des.items() if v < D1_MIN_DE]
        text = "success 与 danger：" + "，".join(f"{k} ΔE {v:.1f}" for k, v in des.items())
        if low:
            text += "；状态不能只靠颜色，必须带图标或文字"
        out.append(finding("D1", "WARN" if low else "PASS", text, de={k: round(v, 2) for k, v in des.items()}))
    else:
        out.append(na("D1", "无 success / danger"))
    if theme.get("action") and theme.get("accent"):
        des = {k: cvd_delta_e(theme["action"], theme["accent"], k) for k in D_KINDS}
        low = [k for k, v in des.items() if v < D2_MIN_DE]
        text = "主色与点缀色：" + "，".join(f"{k} ΔE {v:.1f}" for k, v in des.items())
        out.append(finding("D2", "WARN" if low else "PASS", text, de={k: round(v, 2) for k, v in des.items()}))
    else:
        out.append(na("D2", "无 action / accent"))
    return out


# ---- E 面积与层级纪律 ---------------------------------------------------------------------------------------------------------------------

def check_area(theme: dict, shared: dict) -> list[Finding]:
    out = []
    surface = shared.get("surface", "#FFFFFF")
    if theme.get("canvas"):
        ratio = cc.contrast(theme["canvas"], surface)
        ok = E1_RANGE[0] <= ratio <= E1_RANGE[1]
        out.append(finding("E1", "PASS" if ok else "WARN", f"canvas {theme['canvas']} 与 surface {surface} 亮度比 {ratio:.3f}", ratio=round(ratio, 4)))
    else:
        out.append(na("E1", "无 canvas"))
    line = theme.get("line") or shared.get("line")
    if line:
        ratio = cc.contrast(line, surface)
        ok = E2_RANGE[0] <= ratio <= E2_RANGE[1]
        out.append(finding("E2", "PASS" if ok else "WARN", f"line {line} 在 surface 上 {ratio:.3f}:1", ratio=round(ratio, 4)))
        if theme.get("line"):
            out[-1].scope = "theme"
    else:
        out.append(na("E2", "无 line"))
    if theme.get("actionTint") and theme.get("canvas"):
        ratio = cc.contrast(theme["actionTint"], theme["canvas"])
        de = delta_e(theme["actionTint"], theme["canvas"])
        lighter = cc.luminance(theme["actionTint"]) >= cc.luminance(theme["canvas"])
        ok = ratio >= E3_MIN_RATIO and de >= E3_MIN_DE
        out.append(finding("E3", "PASS" if ok else "WARN",
                           f"actionTint {theme['actionTint']} 与 canvas {theme['canvas']}：亮度比 {ratio:.3f}，ΔE {de:.1f}（actionTint {'比 canvas 亮' if lighter else '比 canvas 暗'}）",
                           ratio=round(ratio, 4), de=round(de, 2)))
    else:
        out.append(na("E3", "无 actionTint / canvas"))
    return out


# ---- F 深色配套纪律 -----------------------------------------------------------------------------------------------------------------------

def check_dark(theme: dict) -> list[Finding]:
    dark = theme.get("dark")
    if not dark:
        return [na(i, "无 dark 映射（check_contrast 会报）") for i in ("F1", "F2", "F3")]
    out = []
    if dark.get("canvas") and dark.get("surface"):
        lights = {k: oklch(dark[k])[0] for k in ("canvas", "surface")}
        bad = [k for k, v in lights.items() if not F1_RANGE[0] <= v <= F1_RANGE[1]]
        out.append(finding("F1", "WARN" if bad else "PASS", "，".join(f"dark.{k} L {v:.3f}" for k, v in lights.items()) + (f"；超出：{'、'.join(bad)}" if bad else ""),
                           lights={k: round(v, 4) for k, v in lights.items()}))
    else:
        out.append(na("F1", "dark 缺 canvas / surface"))
    if dark.get("action") and theme.get("action"):
        diff = oklch(dark["action"])[0] - oklch(theme["action"])[0]
        ok = F2_RANGE[0] - F2_LOW_SLACK <= diff <= F2_RANGE[1]
        out.append(finding("F2", "PASS" if ok else "WARN", f"dark.action {dark['action']} 比 action {theme['action']} 的 L 差 {diff:+.3f}", diff=round(diff, 4)))
    else:
        out.append(na("F2", "缺 dark.action / action"))
    if dark.get("actionText") and theme.get("action") and chroma_of(theme["action"]) >= HUE_RELIABLE_C:
        gap = hue_diff(hue_of(dark["actionText"]), hue_of(theme["action"]))
        out.append(finding("F3", "PASS" if gap <= F3_MAX_HUE_GAP else "WARN",
                           f"dark.actionText {deg(hue_of(dark['actionText']))} 与 action {deg(hue_of(theme['action']))} 相差 {deg(gap)}", gap=round(gap, 2)))
    else:
        out.append(na("F3", "主色近中性或缺 dark.actionText，色相不可比"))
    return out


# ---- 审计入口 -----------------------------------------------------------------------------------------------------------------------------

def audit_theme(theme_id: str, theme: dict, shared: dict) -> list[Finding]:
    """一套主题的 A–F 共 18 项结果，顺序同 CHECK_IDS。"""
    results = check_scale(theme) + check_family(theme, shared) + check_budget(theme, shared) + check_cvd(theme, shared) + check_area(theme, shared) + check_dark(theme)
    order = {cid: i for i, cid in enumerate(CHECK_IDS)}
    return sorted(results, key=lambda f: order[f.id])


def load_data(path: Path = THEMES) -> dict:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def audit_all(data: dict, only: list[str] | None = None) -> dict[str, list[Finding]]:
    themes = data["themes"]
    ids = only or list(themes)
    unknown = [i for i in ids if i not in themes]
    if unknown:
        raise KeyError("unknown theme: " + ", ".join(unknown))
    return {tid: audit_theme(tid, themes[tid], data["shared"]) for tid in ids}


def summarize(results: dict[str, list[Finding]]) -> dict[str, dict[str, int]]:
    summary = {cid: {s: 0 for s in SEVERITIES} for cid in CHECK_IDS}
    for findings in results.values():
        for f in findings:
            summary[f.id][f.status] += 1
    return summary


# ---- G 搭配兼容 ---------------------------------------------------------------------------------------------------------------------------

def glass_contrast(theme: dict, shared: dict, alpha_light: float | None = None, alpha_dark: float | None = None) -> dict:
    """文字落在玻璃上的最差对比度：把玻璃 tint 以其不透明度叠在“最差背景”上，再算 ink 对叠加色的对比度。
    浅色：tint = surface，背景取 #FFFFFF 与主色阶 4（无 scale 时用 action 混入 60% 白近似）；深色：tint = dark.surface，背景取 dark.canvas 与 dark.action。"""
    alpha_light = GLASS_ALPHA_LIGHT if alpha_light is None else alpha_light
    alpha_dark = GLASS_ALPHA_DARK if alpha_dark is None else alpha_dark
    scale = theme.get("scale")
    step4 = scale[3] if scale and len(scale) >= 4 else md.mix_white(theme["action"], 60)
    out: dict = {}
    light_bg = {"#FFFFFF": "#FFFFFF", "主色阶 4": step4}
    light = {name: cc.contrast(shared["ink"], composite(shared.get("surface", "#FFFFFF"), alpha_light, bg)) for name, bg in light_bg.items()}
    worst = min(light, key=light.get)
    out["light"] = {"alpha": alpha_light, "worst_background": worst, "worst": light[worst], "by_background": light,
                    "approximated_step4": not (scale and len(scale) >= 4)}
    dark, sdark = theme.get("dark"), (shared.get("dark") or {})
    if dark and sdark.get("ink"):
        dark_bg = {"dark canvas": dark["canvas"], "dark action": dark["action"]}
        values = {name: cc.contrast(sdark["ink"], composite(dark["surface"], alpha_dark, bg)) for name, bg in dark_bg.items()}
        worst = min(values, key=values.get)
        out["dark"] = {"alpha": alpha_dark, "worst_background": worst, "worst": values[worst], "by_background": values}
    return out


def check_combo(theme_id: str, icons: str, shape: str, depth: str, type_pack: str, motion: str, *, icon_roles=None, glass_roles=None,
                type_uses=None, glass_alpha: float | None = None, data: dict | None = None) -> dict:
    """主题 + 图标 + 圆角 + 层级 + 字阶方案 + 动效个性 的搭配兼容性。

    icons ∈ line / duotone / clay3d；shape ∈ tight / standard / round；depth ∈ hairline / soft / glass；type_pack ∈ standard / compact / bold；motion ∈ calm / snappy / friendly。
    可选：icon_roles 该图标风格用在哪些位置（controls、entry、empty、result、hero，默认见 ICON_ROLES_DEFAULT）；
    glass_roles 玻璃用在哪些表面（hero、entry-icon 合规；navigation、tabbar、sheet、dialog、popover 等控制器表面需裁定，默认 hero 与 entry-icon）；
    type_uses 实际用到的 [(字号, 字重), ...]，逐个核对字阶与字重；glass_alpha 覆盖浅色玻璃不透明度；data 为 themes.json 结构（默认读取文件）。
    返回 {"ok", "errors", "needs_ruling", "notes", "contrast", "resolved"}：ok = 没有 errors（needs_ruling 不影响 ok，但要交给用户裁定）。"""
    data = data if data is not None else load_data()
    errors: list[str] = []
    ruling: list[str] = []
    notes: list[str] = []
    contrast: dict[str, float] = {}
    resolved: dict = {}
    shared = data["shared"]
    theme = data["themes"].get(theme_id)
    if theme is None:
        return {"ok": False, "errors": [f"未知主题 {theme_id!r}"], "needs_ruling": [], "notes": [], "contrast": {}, "resolved": {}}
    for label, value, allowed in (("icons", icons, ICON_STYLES), ("shape", shape, tuple(SHAPES)), ("depth", depth, DEPTHS),
                                  ("type_pack", type_pack, tuple(TYPE_PACKS)), ("motion", motion, tuple(MOTIONS))):
        if value not in allowed:
            errors.append(f"{label} 取值 {value!r} 不在 {'/'.join(allowed)} 内")
    if errors:
        return {"ok": False, "errors": errors, "needs_ruling": [], "notes": [], "contrast": {}, "resolved": {}}

    surface = shared.get("surface", "#FFFFFF")
    contrast.update({
        "white_on_action": cc.contrast(surface, theme["action"]),
        "white_on_actionPress": cc.contrast(surface, theme["actionPress"]),
        "actionPress_on_actionTint": cc.contrast(theme["actionPress"], theme["actionTint"]),
        "ink_on_canvas": cc.contrast(shared["ink"], theme["canvas"]),
        "ink2_on_canvas": cc.contrast(shared["ink2"], theme["canvas"]),
        "ink3_on_surface": cc.contrast(shared["ink3"], surface),
        "canvas_vs_surface": cc.contrast(theme["canvas"], surface),
        "line_on_surface": cc.contrast(theme.get("line") or shared["line"], surface),
    })
    dark, sdark = theme.get("dark"), shared.get("dark") or {}
    if dark and sdark.get("ink"):
        contrast["dark_ink_on_dark_canvas"] = cc.contrast(sdark["ink"], dark["canvas"])
        contrast["dark_action_on_dark_surface"] = cc.contrast(dark["action"], dark["surface"])

    # 图标
    roles = tuple(icon_roles) if icon_roles is not None else ICON_ROLES_DEFAULT[icons]
    for role in roles:
        if role not in ICON_ROLES:
            errors.append(f"图标位置 {role!r} 未知（可用 {'/'.join(ICON_ROLES)}）")
        elif role not in ICON_ROLES_ALLOWED[icons]:
            if role == "controls":
                errors.append(f"{icons} 图标不能用在控件上：控件图标始终是统一线性矢量（line，线宽 2）")
            else:
                errors.append(f"{icons} 图标不能用在 {role}：只用于 {'、'.join(ICON_ROLES_ALLOWED[icons])}")
    if icons == "line":
        notes.append("line：统一线性矢量，用于控件与入口，线宽 2，颜色取 ink / actionText，不用 accent")
    elif icons == "duotone":
        contrast["accent_on_actionTint"] = cc.contrast(theme["accent"], theme["actionTint"])
        notes.append(f"duotone：只用于入口与空状态，浅底用 actionTint {theme['actionTint']}，细节用 accent {theme['accent']}；控件图标仍用 line")
        if contrast["accent_on_actionTint"] < 3.0:
            notes.append(f"duotone 细节线（accent）在浅底（actionTint）上只有 {contrast['accent_on_actionTint']:.2f}:1，低于非文本 3:1，小尺寸时线条会糊；细节用 actionPress 或给轮廓线加深")
    else:
        notes.append("clay3d：只用于入口、空状态、结果页；控件图标仍必须是 line")
        if any(r in CLAY_RULING_ROLES for r in roles):
            ruling.append(CLAY_RULING)

    # 圆角
    spec = SHAPES[shape]
    resolved["radii"] = {k: spec[k] for k in ("tag", "control", "card", "dialog")}
    notes.append(f"圆角 {shape}：标签 {spec['tag']} / 控件 {spec['control']} / 卡片 {spec['card']} / 对话框与弹层 {spec['dialog']}")
    if spec["ruling"]:
        ruling.append(spec["ruling"])
    own = (theme.get("radiusCard"), theme.get("radiusButton"))
    if own != (spec["card"], spec["control"]) and own != (None, None):
        notes.append(f"主题自带圆角 卡片 {own[0]} / 按钮 {own[1]}，与所选 {shape} 的 {spec['card']} / {spec['control']} 不一致；导出令牌时以谁为准需确认")

    # 层级
    elevation = shared.get("elevation") or {}
    if depth == "hairline":
        notes.append(f"hairline：靠 1 像素发丝线分层（{elevation.get('hairline', 'shared.elevation.hairline')}），不加投影；line 在 surface 上 {contrast['line_on_surface']:.2f}:1")
    elif depth == "soft":
        notes.append("soft：两层向下柔和阴影 level1–level4（shared.elevation），hairline 作边")
    else:
        roles_g = tuple(glass_roles) if glass_roles is not None else GLASS_ALLOWED_ROLES
        bad = [r for r in roles_g if r not in GLASS_ALLOWED_ROLES]
        if bad:
            ruling.append(f"{GLASS_RULING}：{'、'.join(bad)}")
        notes.append("glass：只用于主视觉装饰与入口图标块，不作默认页面底色、正文与表格底")
        measured = glass_contrast(theme, shared, glass_alpha)
        resolved["glass"] = measured
        for mode, key in (("light", "glass_light_ink_worst"), ("dark", "glass_dark_ink_worst")):
            if mode not in measured:
                continue
            item = measured[mode]
            contrast[key] = item["worst"]
            notes.append(f"glass {mode}：ink 落在玻璃上最差 {item['worst']:.2f}:1（背景 {item['worst_background']}，不透明度 {item['alpha']:g}）")
            if item["worst"] < GLASS_MIN_CONTRAST:
                errors.append(f"glass {mode} 文字对比度 {item['worst']:.2f}:1 低于 {GLASS_MIN_CONTRAST:g}:1（最差背景 {item['worst_background']}）：提高玻璃不透明度或改用实色面")
        if "dark" not in measured:
            notes.append("该主题没有 dark 映射，未算深色玻璃对比度")

    # 字阶
    pack = TYPE_PACKS[type_pack]
    resolved["type"] = {"sizes": list(pack["sizes"]), "body": pack["body"]}
    notes.append(f"字阶 {type_pack}：{pack['note']}")
    for use in (type_uses or []):
        size, weight = use
        if size not in pack["sizes"]:
            errors.append(f"字号 {size} 不在 {type_pack} 字阶 {'/'.join(map(str, pack['sizes']))} 内")
        if weight not in FONT_WEIGHTS:
            errors.append(f"字重 {weight} 不在 400/600/700 三档内")
        elif weight == 700 and size < MIN_BOLD_SIZE:
            errors.append(f"字重 700 只给不小于 {MIN_BOLD_SIZE} 像素的字号，字号 {size} 请用 600")

    # 动效
    resolved["motion"] = MOTIONS[motion]
    notes.append(MOTIONS[motion])

    return {"ok": not errors, "errors": errors, "needs_ruling": ruling, "notes": notes,
            "contrast": {k: round(v, 3) for k, v in contrast.items()}, "resolved": resolved}


# ---- 报告 ---------------------------------------------------------------------------------------------------------------------------------

CELL = {"PASS": "ok", "INFO": "info", "WARN": "WARN", "FAIL": "FAIL", "NA": "-"}


def matrix_rows(results: dict[str, list[Finding]]) -> list[list[str]]:
    head = ["主题", *CHECK_IDS]
    rows = [head]
    for tid, findings in results.items():
        by_id = {f.id: f for f in findings}
        rows.append([tid, *(CELL[by_id[cid].status] for cid in CHECK_IDS)])
    return rows


def summary_rows(summary: dict[str, dict[str, int]]) -> list[list[str]]:
    rows = [["检查项", "名称", "FAIL", "WARN", "INFO", "通过", "不适用"]]
    for cid in CHECK_IDS:
        s = summary[cid]
        rows.append([cid, CHECKS[cid]["title"], str(s["FAIL"]), str(s["WARN"]), str(s["INFO"]), str(s["PASS"]), str(s["NA"])])
    return rows


def md_table(rows: list[list[str]]) -> str:
    lines = ["| " + " | ".join(rows[0]) + " |", "| " + " | ".join("---" for _ in rows[0]) + " |"]
    lines += ["| " + " | ".join(r) + " |" for r in rows[1:]]
    return "\n".join(lines)


def detail_line(f: Finding) -> str:
    text = f"- **{f.status} {f.id} {f.metric}**：当前 {f.value}；阈值 {f.threshold}"
    if f.fix:
        text += f"；怎么改：{f.fix}"
    return text


def render_markdown(results: dict[str, list[Finding]], summary: dict[str, dict[str, int]]) -> str:
    n = len(results)
    totals = {s: sum(summary[c][s] for c in CHECK_IDS) for s in SEVERITIES}
    out = ["# 主题配色纪律审计", "",
           f"范围：{n} 套主题 × {len(CHECK_IDS)} 项（A–F）。颜色换算用 OKLab / OKLCH，对比度用 WCAG 2.2 相对亮度；只报告，不修改 themes.json。",
           f"合计：FAIL {totals['FAIL']}，WARN {totals['WARN']}，INFO {totals['INFO']}，通过 {totals['PASS']}，不适用 {totals['NA']}。", "",
           "严重度：FAIL = 硬规则（用词为“要求”“不能”）；WARN = 纪律偏差；INFO = 描述性事实（family-overlap 的轻度重叠、撞色提示、强对比提示）。矩阵格子：ok 通过，info 提示，WARN 偏差，FAIL 失败，- 该主题没有这项的前提（无 scale、主色为中性色、无 dark）。", "",
           "## 一、矩阵（行 = 主题，列 = 检查项）", "", md_table(matrix_rows(results)), "",
           "## 二、各检查项汇总", "", md_table(summary_rows(summary)), ""]
    shared_seen: set[str] = set()
    shared_lines = []
    for findings in results.values():
        for f in findings:
            if f.scope == "shared" and f.id not in shared_seen:
                shared_seen.add(f.id)
                shared_lines.append(detail_line(f))
    out += ["## 三、共享令牌（只取决于 shared，所有主题相同，只列一次）", ""] + (shared_lines or ["- 无"]) + [""]
    out += ["## 四、逐主题明细（只列 FAIL / WARN / INFO；不适用与通过的合并成一行）", ""]
    for tid, findings in results.items():
        out.append(f"### {tid}")
        out.append("")
        shown = [f for f in findings if f.status in ("FAIL", "WARN", "INFO") and f.scope == "theme"]
        out += [detail_line(f) for f in shown] or ["- 无主题自有的提示或偏差"]
        passed = [f.id for f in findings if f.status == "PASS"]
        skipped = [f"{f.id}（{f.value}）" for f in findings if f.status == "NA"]
        out.append(f"- 通过：{'、'.join(passed) if passed else '无'}")
        if skipped:
            out.append(f"- 不适用：{'；'.join(skipped)}")
        out.append("")
    out += ["## 五、阈值与依据", "", md_table([["检查项", "阈值"], *[[cid, CHECKS[cid]["threshold"].replace("|", "/")] for cid in CHECK_IDS]]), ""]
    out += ["## 六、局限", ""] + [f"- {item}" for item in LIMITS] + [""]
    return "\n".join(out)


def render_console(results: dict[str, list[Finding]], summary: dict[str, dict[str, int]]) -> str:
    rows = matrix_rows(results)
    widths = [max(len(r[i]) for r in rows) for i in range(len(rows[0]))]
    lines = ["  ".join(c.ljust(widths[i]) if i == 0 else c.center(widths[i]) for i, c in enumerate(r)) for r in rows]
    lines.append("")
    for r in summary_rows(summary):
        lines.append("  ".join([r[0].ljust(4), r[2].rjust(5), r[3].rjust(5), r[4].rjust(5), r[5].rjust(5), r[6].rjust(6), r[1]]))
    lines.append("")
    shared_seen: set[str] = set()
    for tid, findings in results.items():
        for f in findings:
            if f.status not in ("FAIL", "WARN", "INFO"):
                continue
            if f.scope == "shared":      # 共享令牌的结果所有主题相同，只打印一次
                if f.id in shared_seen:
                    continue
                shared_seen.add(f.id)
                lines.append(f"{f.status:4} (全部主题) {f.id} {f.metric}：{f.value}")
            else:
                lines.append(f"{f.status:4} {tid} {f.id} {f.metric}：{f.value}")
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--theme", action="append", default=[], metavar="ID", help="只审计这个主题（可重复）")
    parser.add_argument("--themes-file", type=Path, default=THEMES, help="themes.json 路径")
    parser.add_argument("--json", type=Path, metavar="OUT", help="写 JSON 报告")
    parser.add_argument("--md", type=Path, metavar="OUT", help="写 Markdown 报告")
    parser.add_argument("--combo", nargs=6, metavar=("THEME", "ICONS", "SHAPE", "DEPTH", "TYPE", "MOTION"), help="检查一个搭配并以 JSON 输出")
    parser.add_argument("--icon-roles", help="--combo 的图标位置，逗号分隔（controls,entry,empty,result,hero）")
    parser.add_argument("--glass-roles", help="--combo 的玻璃表面，逗号分隔（hero,entry-icon,navigation,tabbar,sheet,dialog,popover）")
    parser.add_argument("--quiet", action="store_true", help="不打印矩阵与明细，只写文件并以退出码表示")
    args = parser.parse_args(argv)
    data = load_data(args.themes_file)
    split = lambda s: [x.strip() for x in s.split(",") if x.strip()] if s else None  # noqa: E731
    if args.combo:
        result = check_combo(*args.combo, icon_roles=split(args.icon_roles), glass_roles=split(args.glass_roles), data=data)
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 0 if result["ok"] else 1
    try:
        results = audit_all(data, args.theme or None)
    except KeyError as exc:
        print(f"ERROR {exc.args[0]}", file=sys.stderr)
        return 2
    summary = summarize(results)
    if not args.quiet:
        print(render_console(results, summary))
    if args.json:
        payload = {"themes": {tid: [f.to_dict() for f in findings] for tid, findings in results.items()}, "summary": summary,
                   "thresholds": {cid: CHECKS[cid]["threshold"] for cid in CHECK_IDS}}
        args.json.parent.mkdir(parents=True, exist_ok=True)
        args.json.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    if args.md:
        args.md.parent.mkdir(parents=True, exist_ok=True)
        args.md.write_text(render_markdown(results, summary), encoding="utf-8")
    failed = any(f.status == "FAIL" for findings in results.values() for f in findings)
    return 1 if failed else 0


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    raise SystemExit(main())
