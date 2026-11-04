"""One set of 24-grid linear icons for showcase documents (own drawings, no third-party icon data).

Every icon is ``(face, lines)``: ``lines`` are stroked with the one line width of the set (2 px on the 24 grid, round caps
and joins); ``face`` is the single main shape that the two-tone icon block fills with the theme's second step
(visual-design.html 双色图标块: only one face is filled, never a second one). One object, one icon; names are concepts,
not drawings, so every document refers to the same name for the same object.
"""
from __future__ import annotations

ICONS: dict[str, tuple[str, str]] = {
    "user": ('<circle cx="12" cy="8" r="4"/>', '<circle cx="12" cy="8" r="4"/><path d="M4 21c0-4 3.6-7 8-7s8 3 8 7"/>'),
    "users": ('<circle cx="9" cy="8" r="3.5"/>', '<circle cx="9" cy="8" r="3.5"/><path d="M2.5 20c0-3.5 2.9-6 6.5-6s6.5 2.5 6.5 6"/><circle cx="17.5" cy="9" r="2.5"/><path d="M17 14.2c2.7.3 4.5 2.3 4.5 5"/>'),
    "building": ('<rect x="5" y="3" width="14" height="18" rx="2"/>', '<rect x="5" y="3" width="14" height="18" rx="2"/><path d="M9 8h2M13 8h2M9 12h2M13 12h2M10 21v-4h4v4"/>'),
    "store": ('<rect x="5" y="12" width="14" height="8"/>', '<path d="M3 9l1.5-5h15L21 9"/><path d="M3 9c0 1.7 1.3 3 3 3s3-1.3 3-3c0 1.7 1.3 3 3 3s3-1.3 3-3c0 1.7 1.3 3 3 3s3-1.3 3-3"/><path d="M5 12v8h14v-8"/>'),
    "calendar": ('<rect x="3" y="5" width="18" height="16" rx="2"/>', '<rect x="3" y="5" width="18" height="16" rx="2"/><path d="M3 10h18M8 3v4M16 3v4"/>'),
    "clock": ('<circle cx="12" cy="12" r="9"/>', '<circle cx="12" cy="12" r="9"/><path d="M12 7v5l3 2"/>'),
    "check": ('<circle cx="12" cy="12" r="9"/>', '<circle cx="12" cy="12" r="9"/><path d="M8 12.5l3 3 5-6"/>'),
    "close": ('<circle cx="12" cy="12" r="9"/>', '<circle cx="12" cy="12" r="9"/><path d="M9 9l6 6M15 9l-6 6"/>'),
    "shield": ('<path d="M12 3l8 3v6c0 4.5-3.2 8.2-8 9-4.8-.8-8-4.5-8-9V6z"/>', '<path d="M12 3l8 3v6c0 4.5-3.2 8.2-8 9-4.8-.8-8-4.5-8-9V6z"/><path d="M9 12l2 2 4-4"/>'),
    "lock": ('<rect x="5" y="11" width="14" height="10" rx="2"/>', '<rect x="5" y="11" width="14" height="10" rx="2"/><path d="M8 11V8a4 4 0 0 1 8 0v3"/>'),
    "key": ('<circle cx="8" cy="15" r="4"/>', '<circle cx="8" cy="15" r="4"/><path d="M11 12l9-9M16 7l3 3"/>'),
    "database": ('<ellipse cx="12" cy="6" rx="8" ry="3"/>', '<ellipse cx="12" cy="6" rx="8" ry="3"/><path d="M4 6v6c0 1.7 3.6 3 8 3s8-1.3 8-3V6"/><path d="M4 12v6c0 1.7 3.6 3 8 3s8-1.3 8-3v-6"/>'),
    "server": ('<rect x="3" y="4" width="18" height="7" rx="2"/>', '<rect x="3" y="4" width="18" height="7" rx="2"/><rect x="3" y="13" width="18" height="7" rx="2"/><path d="M7 7.5h.01M7 16.5h.01"/>'),
    "cloud": ('<path d="M7 18a4 4 0 0 1-.5-8A5.5 5.5 0 0 1 17 8.5 4.5 4.5 0 0 1 17.5 18z"/>', '<path d="M7 18a4 4 0 0 1-.5-8A5.5 5.5 0 0 1 17 8.5 4.5 4.5 0 0 1 17.5 18z"/>'),
    "phone": ('<rect x="7" y="2" width="10" height="20" rx="2.5"/>', '<rect x="7" y="2" width="10" height="20" rx="2.5"/><path d="M11 18h2"/>'),
    "monitor": ('<rect x="3" y="4" width="18" height="12" rx="2"/>', '<rect x="3" y="4" width="18" height="12" rx="2"/><path d="M8 20h8M12 16v4"/>'),
    "scan": ('', '<path d="M4 8V6a2 2 0 0 1 2-2h2M16 4h2a2 2 0 0 1 2 2v2M20 16v2a2 2 0 0 1-2 2h-2M8 20H6a2 2 0 0 1-2-2v-2"/><path d="M7 12h10"/>'),
    "qr": ('<rect x="4" y="4" width="6" height="6" rx="1"/>', '<rect x="4" y="4" width="6" height="6" rx="1"/><rect x="14" y="4" width="6" height="6" rx="1"/><rect x="4" y="14" width="6" height="6" rx="1"/><path d="M14 14h3v3M20 14v.01M14 20h.01M17 20h3v-3"/>'),
    "list": ('<rect x="5" y="4" width="14" height="17" rx="2"/>', '<rect x="5" y="4" width="14" height="17" rx="2"/><path d="M9 9h6M9 13h6M9 17h3"/>'),
    "file": ('<path d="M6 3h8l5 5v13H6z"/>', '<path d="M6 3h8l5 5v13H6z"/><path d="M14 3v5h5M9 13h6M9 17h4"/>'),
    "book": ('<path d="M4 5a2 2 0 0 1 2-2h13v16H6a2 2 0 0 0-2 2z"/>', '<path d="M4 5a2 2 0 0 1 2-2h13v16H6a2 2 0 0 0-2 2z"/><path d="M4 21V5M8 7h8"/>'),
    "folder": ('<path d="M3 7a2 2 0 0 1 2-2h4l2 2h8a2 2 0 0 1 2 2v9a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"/>', '<path d="M3 7a2 2 0 0 1 2-2h4l2 2h8a2 2 0 0 1 2 2v9a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"/>'),
    "chart-bar": ('<rect x="11" y="6" width="3" height="12"/>', '<path d="M4 20h16"/><rect x="6" y="11" width="3" height="7"/><rect x="11" y="6" width="3" height="12"/><rect x="16" y="9" width="3" height="9"/>'),
    "chart-line": ('', '<path d="M3 3v18h18"/><path d="M7 15l4-4 3 3 5-6"/>'),
    "money": ('<circle cx="12" cy="12" r="9"/>', '<circle cx="12" cy="12" r="9"/><path d="M9 8l3 4 3-4M12 12v5M9.5 12.5h5M9.5 15h5"/>'),
    "tag": ('<path d="M3 12V4h8l10 10-8 8z"/>', '<path d="M3 12V4h8l10 10-8 8z"/><circle cx="7.5" cy="8.5" r="1.2"/>'),
    "package": ('<path d="M12 3l8 4v10l-8 4-8-4V7z"/>', '<path d="M12 3l8 4v10l-8 4-8-4V7z"/><path d="M4 7l8 4 8-4M12 11v10"/>'),
    "truck": ('<rect x="2" y="6" width="12" height="10" rx="1"/>', '<rect x="2" y="6" width="12" height="10" rx="1"/><path d="M14 10h4l4 3v3h-8"/><circle cx="6.5" cy="18.5" r="2"/><circle cx="17.5" cy="18.5" r="2"/>'),
    "settings": ('', '<path d="M4 7h10M18 7h2M4 17h2M10 17h10"/><circle cx="16" cy="7" r="2"/><circle cx="8" cy="17" r="2"/>'),
    "bell": ('<path d="M6 17V11a6 6 0 0 1 12 0v6l2 2H4z"/>', '<path d="M6 17V11a6 6 0 0 1 12 0v6l2 2H4z"/><path d="M10 21h4"/>'),
    "mail": ('<rect x="3" y="5" width="18" height="14" rx="2"/>', '<rect x="3" y="5" width="18" height="14" rx="2"/><path d="M3 7l9 6 9-6"/>'),
    "link": ('', '<path d="M10 14a4 4 0 0 0 5.7 0l3-3a4 4 0 0 0-5.7-5.7l-1 1M14 10a4 4 0 0 0-5.7 0l-3 3a4 4 0 0 0 5.7 5.7l1-1"/>'),
    "flow": ('<rect x="9" y="15" width="6" height="5" rx="1"/>', '<rect x="3" y="4" width="6" height="5" rx="1"/><rect x="15" y="4" width="6" height="5" rx="1"/><rect x="9" y="15" width="6" height="5" rx="1"/><path d="M6 9v2.5a1 1 0 0 0 1 1h10a1 1 0 0 0 1-1V9M12 12.5V15"/>'),
    "layers": ('<path d="M12 2.5l9 5-9 5-9-5z"/>', '<path d="M12 2.5l9 5-9 5-9-5z"/><path d="M3 12l9 5 9-5M3 16.5l9 5 9-5"/>'),
    "target": ('<circle cx="12" cy="12" r="5"/>', '<circle cx="12" cy="12" r="9"/><circle cx="12" cy="12" r="5"/><path d="M12 12h.01"/>'),
    "flag": ('<path d="M5 4h11l-2 4 2 4H5z"/>', '<path d="M5 21V4"/><path d="M5 4h11l-2 4 2 4H5"/>'),
    "warning": ('<path d="M12 3l10 18H2z"/>', '<path d="M12 3l10 18H2z"/><path d="M12 10v5M12 18v.01"/>'),
    "info": ('<circle cx="12" cy="12" r="9"/>', '<circle cx="12" cy="12" r="9"/><path d="M12 11v6M12 7.5v.01"/>'),
    "search": ('<circle cx="11" cy="11" r="7"/>', '<circle cx="11" cy="11" r="7"/><path d="M16 16l5 5"/>'),
    "download": ('', '<path d="M12 3v12M7 11l5 5 5-5M4 20h16"/>'),
    "upload": ('', '<path d="M12 17V5M7 9l5-5 5 5M4 20h16"/>'),
    "refresh": ('', '<path d="M20 11a8 8 0 0 0-14-4L4 9M4 4v5h5M4 13a8 8 0 0 0 14 4l2-2M20 20v-5h-5"/>'),
    "edit": ('<path d="M4 20l1-4L16 5l3 3L8 19z"/>', '<path d="M4 20l1-4L16 5l3 3L8 19z"/><path d="M14 7l3 3"/>'),
    "trash": ('', '<path d="M4 7h16M10 11v6M14 11v6M6 7l1 13h10l1-13M9 7V4h6v3"/>'),
    "star": ('<path d="M12 3l2.7 5.6 6.1.9-4.4 4.3 1 6.1L12 17l-5.4 2.9 1-6.1L3.2 9.5l6.1-.9z"/>', '<path d="M12 3l2.7 5.6 6.1.9-4.4 4.3 1 6.1L12 17l-5.4 2.9 1-6.1L3.2 9.5l6.1-.9z"/>'),
    "home": ('<path d="M4 11l8-7 8 7v9H4z"/>', '<path d="M4 11l8-7 8 7v9H4z"/><path d="M10 20v-5h4v5"/>'),
    "pin": ('<path d="M12 21s7-6 7-12a7 7 0 0 0-14 0c0 6 7 12 7 12z"/>', '<path d="M12 21s7-6 7-12a7 7 0 0 0-14 0c0 6 7 12 7 12z"/><circle cx="12" cy="9" r="2.5"/>'),
    "camera": ('<rect x="3" y="7" width="18" height="13" rx="2"/>', '<rect x="3" y="7" width="18" height="13" rx="2"/><path d="M8 7l1.5-3h5L16 7"/><circle cx="12" cy="13.5" r="3.5"/>'),
    "image": ('<rect x="3" y="4" width="18" height="16" rx="2"/>', '<rect x="3" y="4" width="18" height="16" rx="2"/><circle cx="9" cy="10" r="1.5"/><path d="M21 16l-5-5-8 8"/>'),
    "printer": ('<rect x="4" y="8" width="16" height="9" rx="2"/>', '<rect x="7" y="3" width="10" height="5"/><rect x="4" y="8" width="16" height="9" rx="2"/><rect x="7" y="14" width="10" height="7"/>'),
    "wifi": ('', '<path d="M2 9a15 15 0 0 1 20 0M5 12.5a10 10 0 0 1 14 0M8.5 16a5 5 0 0 1 7 0M12 20v.01"/>'),
    "globe": ('<circle cx="12" cy="12" r="9"/>', '<circle cx="12" cy="12" r="9"/><path d="M3 12h18M12 3c3 3 3 15 0 18M12 3c-3 3-3 15 0 18"/>'),
    "utensils": ('', '<path d="M6 3v8M9 3v8M6 7h3M7.5 11v10"/><path d="M17 21V3c-2 1-3 4-3 8h3"/>'),
    "ticket": ('<path d="M3 7h18v4a2 2 0 0 0 0 4v4H3v-4a2 2 0 0 0 0-4z"/>', '<path d="M3 7h18v4a2 2 0 0 0 0 4v4H3v-4a2 2 0 0 0 0-4z"/><path d="M14 9v1M14 12v.01M14 14v1"/>'),
    "briefcase": ('<rect x="3" y="7" width="18" height="13" rx="2"/>', '<rect x="3" y="7" width="18" height="13" rx="2"/><path d="M8 7V5a1 1 0 0 1 1-1h6a1 1 0 0 1 1 1v2M3 13h18"/>'),
    "bolt": ('<path d="M13 2L4 14h7l-1 8 9-12h-7z"/>', '<path d="M13 2L4 14h7l-1 8 9-12h-7z"/>'),
    "route": ('', '<circle cx="6" cy="18" r="2"/><circle cx="18" cy="6" r="2"/><path d="M8 18h6a3 3 0 0 0 0-6h-4a3 3 0 0 1 0-6h6"/>'),
    "inbox": ('<path d="M3 13l3-8h12l3 8v6H3z"/>', '<path d="M3 13l3-8h12l3 8v6H3z"/><path d="M3 13h5l1 3h6l1-3h5"/>'),
    "pen": ('', '<path d="M3 21l3-1 13-13a2.1 2.1 0 0 0-3-3L3 17z"/><path d="M14 6l3 3"/>'),
    "sliders": ('', '<path d="M5 4v16M12 4v16M19 4v16"/><circle cx="5" cy="9" r="2"/><circle cx="12" cy="15" r="2"/><circle cx="19" cy="8" r="2"/>'),
    "grid": ('<rect x="3" y="3" width="8" height="8" rx="1.5"/>', '<rect x="3" y="3" width="8" height="8" rx="1.5"/><rect x="13" y="3" width="8" height="8" rx="1.5"/><rect x="3" y="13" width="8" height="8" rx="1.5"/><rect x="13" y="13" width="8" height="8" rx="1.5"/>'),
    "handshake": ('', '<path d="M2 11l4-3 5 1 3-2 6 4"/><path d="M6 8v8l4 3 3-2 3 2 5-4v-4"/><path d="M11 14l2 2"/>'),
}

# Keywords that choose an icon for a module or card when the author did not name one.
KEYWORDS: list[tuple[str, str]] = [
    ("登录", "key"), ("绑定", "link"), ("菜单", "utensils"), ("餐", "utensils"), ("订单", "list"), ("取餐码", "qr"), ("核销", "scan"), ("扫码", "scan"),
    ("员工", "users"), ("会员", "users"), ("角色", "users"), ("企业", "building"), ("门店", "store"), ("套餐", "package"), ("商品", "package"),
    ("支付", "money"), ("金额", "money"), ("积分", "star"), ("优惠", "tag"), ("预约", "calendar"), ("日程", "calendar"), ("时间", "clock"),
    ("统计", "chart-bar"), ("报表", "chart-bar"), ("看板", "chart-bar"), ("数据", "database"), ("备份", "database"), ("导出", "download"), ("导入", "upload"),
    ("权限", "shield"), ("隔离", "shield"), ("安全", "shield"), ("通知", "bell"), ("消息", "mail"), ("配置", "settings"), ("规则", "sliders"),
    ("个人", "user"), ("账号", "user"), ("部署", "server"), ("服务器", "server"), ("小程序", "phone"), ("后台", "monitor"), ("网站", "globe"),
    ("验收", "check"), ("交付", "package"), ("变更", "refresh"), ("风险", "warning"), ("流程", "flow"), ("架构", "layers"), ("计划", "calendar"), ("目标", "target"),
]


def pick(text: str, default: str = "grid") -> str:
    for word, name in KEYWORDS:
        if word in text:
            return name
    return default


def svg(name: str, *, size: int = 24, color: str = "currentColor", fill: str | None = None, width: float = 2.0, cls: str = "") -> str:
    """Inline SVG. ``fill`` colours the icon's one face (two-tone icon block); without it the icon is plain line art."""
    if name not in ICONS:
        raise KeyError(f"unknown icon {name!r}; choose from {', '.join(sorted(ICONS))}")
    face, lines = ICONS[name]
    stroke = f'fill="none" stroke="{color}" stroke-width="{width}" stroke-linecap="round" stroke-linejoin="round"'
    back = f'<g fill="{fill}" stroke="none">{face}</g>' if (fill and face) else ""
    klass = f' class="{cls}"' if cls else ""
    return f'<svg{klass} xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" width="{size}" height="{size}" aria-hidden="true" focusable="false">{back}<g {stroke}>{lines}</g></svg>'


def inner(name: str, x: float, y: float, size: float, *, color: str, fill: str | None = None, width: float = 2.0) -> str:
    """Icon placed inside another SVG at (x, y) with the given size (scaled from the 24 grid, stroke kept at ``width`` px)."""
    face, lines = ICONS[name]
    k = size / 24
    back = f'<g fill="{fill}" stroke="none">{face}</g>' if (fill and face) else ""
    return (f'<g transform="translate({x:.1f} {y:.1f}) scale({k:.4f})"><g {back and ""}>{back}</g>'
            f'<g fill="none" stroke="{color}" stroke-width="{width / k:.2f}" stroke-linecap="round" stroke-linejoin="round">{lines}</g></g>')
