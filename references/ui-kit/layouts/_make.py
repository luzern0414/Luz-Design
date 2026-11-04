"""Writes the six runnable layout examples (layouts/*.html) of the Luz UI kit. Each is plain HTML + ui.css + ui.js, no build step."""
from pathlib import Path

HERE = Path(__file__).resolve().parent
ICON = ("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 32 32'%3E%3Crect width='32' height='32' rx='8' fill='%232f6b4f'/%3E"
        "%3Crect x='8' y='8' width='7' height='7' rx='1.5' fill='none' stroke='%23fff' stroke-width='2'/%3E%3Crect x='17' y='8' width='7' height='7' rx='1.5' fill='none' stroke='%23fff' stroke-width='2'/%3E"
        "%3Crect x='8' y='17' width='16' height='7' rx='1.5' fill='none' stroke='%23fff' stroke-width='2'/%3E%3C/svg%3E")


def page(title: str, css: str, body: str, js: str) -> str:
    import re

    h1 = re.search(r"<h1>(.*?)</h1>", body)
    heading = f'<h1 class="page-title">{h1.group(1)}</h1>' + chr(10) if h1 else ""
    body = re.sub(r"<h1>.*?</h1>", "", body, count=1)
    return ("<!doctype html>\n<html lang=\"zh-CN\">\n<head>\n<meta charset=\"utf-8\">\n<meta name=\"viewport\" content=\"width=device-width, initial-scale=1\">\n"
            f"<title>{title}</title>\n<link rel=\"icon\" href=\"{ICON}\">\n" + THEME_HEAD + "<link rel=\"stylesheet\" href=\"../ui.css\">\n"
            + (f"<style>\n@layer project {{\n{css.strip()}\n}}\n</style>\n" if css.strip() else "")
            + f"</head>\n<body>\n{heading}<section class=\"page\">\n<h2 class=\"sr-only\">页面内容</h2>\n{body.strip()}\n<div class=\"appearance-row\"><span>外观</span><span id=\"appearance\"></span></div>\n</section>\n<script src=\"../ui.js\"></script>\n<script>\nUI.appearance(document.getElementById('appearance'));\n{js.strip()}\n</script>\n</body>\n</html>\n")


THEME_HEAD = ("<script>(function(){var K='luz-theme',r=document.documentElement;function g(){try{var v=localStorage.getItem(K);return v==='light'||v==='dark'?v:'system'}catch(e){return'system'}}"
              "function a(m){if(m==='light'||m==='dark')r.setAttribute('data-theme',m);else r.removeAttribute('data-theme')}"
              "window.luzTheme={get:g,set:function(m){try{if(m==='light'||m==='dark')localStorage.setItem(K,m);else localStorage.removeItem(K)}catch(e){}a(m)}};a(g())})();</script>\n")


PAGES = {}

# 1 主次布局 ------------------------------------------------------------------------------------------------
PAGES["1-主次布局"] = ("主次布局：经营看板", """
.hero-card { display: grid; grid-template-rows: auto 1fr; gap: var(--s-4); height: 100%; }
.hero-num { display: flex; align-items: baseline; gap: var(--s-3); flex-wrap: wrap; }
""", """
<header class="page-head"><div><h1>经营看板</h1><p class="muted">主角是营业额趋势，占首屏一半以上；其余指标缩成小块贴右侧和下方</p></div>
<div class="actions"><div class="seg" role="group" aria-label="时间范围"><button aria-pressed="false">今天</button><button aria-pressed="false">近 7 天</button><button aria-pressed="true">近 30 天</button></div><button class="btn btn--primary" id="export">导出</button></div></header>
<section class="l-hero" aria-label="经营概览">
  <article class="card hero"><div class="hero-card"><div class="stat"><span class="stat-label">营业额</span><div class="hero-num"><span class="stat-value num" id="rev">0</span><span class="delta up">▲ 12.4%</span></div><span class="stat-sub">较上一个 30 天</span></div><div id="hero-chart" style="min-height:240px"></div></div></article>
  <article class="card card--tight aside stat stat--sm"><span class="stat-label">订单数</span><span class="stat-value num" id="ord">0</span><span class="stat-sub"><span class="delta up">▲ 8.1%</span> 日均 86 单</span><div id="s1"></div></article>
  <article class="card card--tight aside stat stat--sm"><span class="stat-label">客单价</span><span class="stat-value num" id="avg">0</span><span class="stat-sub"><span class="delta">持平</span></span><div id="s2"></div></article>
  <article class="card card--tight below stat stat--sm"><span class="stat-label">新增会员</span><span class="stat-value num" id="mem">0</span><span class="stat-sub"><span class="delta up">▲ 3.2%</span></span></article>
  <article class="card card--tight below stat stat--sm"><span class="stat-label">待处理售后</span><span class="stat-value num" id="ref">0</span><span class="stat-sub"><span class="badge badge--warn">2 条超时</span></span></article>
  <article class="card card--tight below stat stat--sm"><span class="stat-label">核销率</span><span class="stat-value num" id="rate">0</span><span class="stat-sub">已核销 2,471 份</span></article>
</section>
""", """
const days = Array.from({length: 30}, (_, i) => (new Date(Date.now() - (29 - i) * 864e5)).toISOString().slice(5, 10).replace('-', '/'));
const rev = days.map((_, i) => Math.round(1800 + Math.sin(i / 3) * 420 + i * 28 + (i % 7 === 5 ? -500 : 0)));
UI.line(document.getElementById('hero-chart'), {labels: days, series: [{name: '营业额', data: rev}], unit: ' 元', height: 280, aria: '近 30 天营业额折线，从 ' + rev[0] + ' 元到 ' + rev[29] + ' 元'});
UI.count(document.getElementById('rev'), rev.reduce((a, b) => a + b, 0), {prefix: '¥'}); UI.count(document.getElementById('ord'), 2585); UI.count(document.getElementById('avg'), 17.37, {prefix: '¥', dec: 2}); UI.count(document.getElementById('mem'), 318); UI.count(document.getElementById('ref'), 7); UI.count(document.getElementById('rate'), 95.6, {dec: 1, suffix: '%'});
UI.spark(document.getElementById('s1'), rev.map((v) => v / 20)); UI.spark(document.getElementById('s2'), rev.map((v, i) => 17 + (i % 5)), {color: 'var(--ch-2)'});
document.querySelectorAll('.seg button').forEach((b) => b.addEventListener('click', () => { document.querySelectorAll('.seg button').forEach((x) => x.setAttribute('aria-pressed', String(x === b))); UI.toast('已切换到「' + b.textContent + '」'); }));
document.getElementById('export').addEventListener('click', () => UI.toast('已导出 营业额_近30天.xlsx'));
""")

# 2 横带分层 ------------------------------------------------------------------------------------------------
PAGES["2-横带分层"] = ("横带分层：订单概览", "", """
<header class="page-head"><div><h1>订单</h1><p class="muted">自上而下：概览数字，趋势，明细表格</p></div><div class="actions"><button class="btn">筛选</button><button class="btn btn--primary">导出</button></div></header>
<div class="l-bands">
  <section class="band" aria-label="概览数字"><div class="band-stats">
    <div class="stat"><span class="stat-label">今日订单</span><span class="stat-value num" id="a">0</span><span class="stat-sub"><span class="delta up">▲ 6.2%</span></span></div>
    <div class="stat"><span class="stat-label">营业额</span><span class="stat-value num" id="b">0</span><span class="stat-sub"><span class="delta up">▲ 9.8%</span></span></div>
    <div class="stat"><span class="stat-label">待履约</span><span class="stat-value num" id="c">0</span><span class="stat-sub"><span class="badge badge--warn">3 单超 15 分钟</span></span></div>
    <div class="stat"><span class="stat-label">退款中</span><span class="stat-value num" id="d">0</span><span class="stat-sub muted">待审批</span></div>
    <div class="stat"><span class="stat-label">客单价</span><span class="stat-value num" id="e">0</span><span class="stat-sub"><span class="delta">持平</span></span></div></div></section>
  <section class="band" aria-label="订单趋势"><div class="band-title"><h2>近 14 天订单趋势</h2><div class="legend"><span><i style="background:var(--ch-1)"></i>已完成</span><span><i style="background:var(--ch-2)"></i>待履约</span><span><i style="background:var(--ch-3)"></i>退款</span></div></div><div id="trend"></div></section>
  <section class="band" aria-label="订单明细"><div class="band-title"><h2>订单明细</h2><div class="row wrap"><input class="input input--search" placeholder="订单号或会员" aria-label="搜索订单" style="width:240px"><select class="select" aria-label="状态" style="width:140px"><option>全部状态</option><option>待履约</option><option>已完成</option></select></div></div>
    <div class="table-wrap"><table class="table"><thead><tr><th>订单号</th><th>会员</th><th>商品</th><th class="r">金额</th><th>状态</th><th>下单时间</th><th class="c">操作</th></tr></thead><tbody id="rows"></tbody></table></div></section>
</div>
""", """
const d = Array.from({length: 14}, (_, i) => (new Date(Date.now() - (13 - i) * 864e5)).toISOString().slice(5, 10).replace('-', '/'));
UI.bars(document.getElementById('trend'), {labels: d, stacked: true, unit: ' 单', height: 240, aria: '近 14 天订单分状态堆叠柱图', series: [{name: '已完成', data: d.map((_, i) => 70 + (i * 7) % 30)}, {name: '待履约', data: d.map((_, i) => 6 + (i * 3) % 9), color: 'var(--ch-2)'}, {name: '退款', data: d.map((_, i) => 1 + i % 4), color: 'var(--ch-3)'}]});
[['a', 108], ['b', 1876, '¥'], ['c', 9], ['d', 4], ['e', 17.4, '¥', 1]].forEach(([id, v, p, dec]) => UI.count(document.getElementById(id), v, {prefix: p || '', dec: dec || 0}));
const st = [['已完成', 'ok'], ['待履约', 'warn'], ['退款中', 'bad'], ['已完成', 'ok'], ['待支付', 'info']];
document.getElementById('rows').innerHTML = Array.from({length: 8}, (_, i) => `<tr><td data-label="订单号" class="num">26110${3000 + i * 37}</td><td data-label="会员">${['李哲', '王思远', '张雨婷', '刘子豪'][i % 4]}</td><td data-label="商品" class="ell">${['招牌牛腩饭 ×1', '红烧鸡腿饭 ×2', '轻食鸡胸沙拉 ×1'][i % 3]}</td><td data-label="金额" class="r num">¥${(18 + i * 3.5).toFixed(2)}</td><td data-label="状态"><span class="badge badge--${st[i % 5][1]}">${st[i % 5][0]}</span></td><td data-label="下单时间" class="num">11-03 ${10 - (i >> 1)}:${String(10 + i * 6).slice(-2)}</td><td data-label="操作" class="c"><button class="btn btn--ghost btn--sm">详情</button></td></tr>`).join('');
""")

# 3 主区+右侧窄栏 -------------------------------------------------------------------------------------------
PAGES["3-主区加右侧窄栏"] = ("主区加右侧窄栏：商品管理", """
.prod { display: grid; grid-template-columns: 72px 1fr auto; gap: var(--s-4); align-items: center; padding: var(--s-3); border-radius: var(--r-md); }
.prod:hover { background: var(--surface-2); }
.thumb { width: 72px; height: 54px; border-radius: var(--r-sm); background: var(--brand-soft); display: grid; place-items: center; color: var(--brand); }
""", """
<header class="page-head"><div><h1>商品</h1><p class="muted">左侧三分之二是主列表；右侧窄栏 sticky，滚动主区时库存预警、待办和动态停在原处</p></div><div class="actions"><button class="btn">批量上下架</button><button class="btn btn--primary">新增商品</button></div></header>
<div class="l-rail">
  <div class="main">
    <div class="card card--tight row wrap"><div class="tabs" role="tablist" style="border:0"><button role="tab" aria-selected="true">全部 <span class="count">32</span></button><button role="tab" aria-selected="false">在售 <span class="count">27</span></button><button role="tab" aria-selected="false">已下架 <span class="count">5</span></button></div><span class="grow"></span><input class="input input--search" placeholder="商品名称" aria-label="搜索商品" style="width:220px"></div>
    <div class="card" style="padding:var(--s-2)"><div id="list" class="stack" style="gap:2px"></div></div>
  </div>
  <aside class="rail" aria-label="提醒与动态">
    <section class="card card--tight"><div class="card-head"><h3>库存预警</h3><span class="badge badge--bad">4 项</span></div><div class="list" id="warn"></div></section>
    <section class="card card--tight"><div class="card-head"><h3>今日待办</h3></div><div class="list"><div><span class="grow">3 单超过 15 分钟未出餐</span><button class="btn btn--soft btn--sm">去处理</button></div><div><span class="grow">2 条退款待审批</span><button class="btn btn--soft btn--sm">去处理</button></div><div><span class="grow">1 张月卡即将到期</span><button class="btn btn--soft btn--sm">查看</button></div></div></section>
    <section class="card card--tight"><div class="card-head"><h3>最近动态</h3></div><div class="list" id="feed"></div></section>
  </aside>
</div>
""", """
const names = ['招牌牛腩饭', '红烧鸡腿饭', '清蒸鲈鱼套餐', '田园素食套餐', '宫保鸡丁饭', '黑椒牛柳饭', '鱼香肉丝饭', '轻食鸡胸沙拉', '中式早餐', '粥品早餐', '西式早餐', '梅菜扣肉饭', '香煎三文鱼', '照烧鸡排饭', '咖喱牛肉饭', '番茄鸡蛋面'];
document.getElementById('list').innerHTML = names.map((n, i) => `<div class="prod"><div class="thumb">${UI.icon('bag').outerHTML}</div><div><strong>${n}</strong><div class="muted">主食 · 库存 <span class="num">${[8, 42, 31, 6, 55, 20, 17, 64][i % 8]}</span></div></div><div class="row"><span class="num"><b>¥${(15 + (i * 3) % 12).toFixed(2)}</b></span><span class="badge ${i % 7 === 6 ? '' : 'badge--ok'}">${i % 7 === 6 ? '已下架' : '在售'}</span></div></div>`).join('');
document.getElementById('warn').innerHTML = [['招牌牛腩饭', 8], ['田园素食套餐', 6], ['鱼香肉丝饭', 5], ['西式早餐', 3]].map(([n, s]) => `<div><span class="grow">${n}</span><span class="badge badge--bad num">剩 ${s}</span></div>`).join('');
document.getElementById('feed').innerHTML = [['李哲 下单 招牌牛腩饭', '10:12'], ['王思远 申请退款 ¥18.00', '10:05'], ['月卡 C20260053 今日扣次', '09:48'], ['周敏 上架 轻食鸡胸沙拉', '09:30'], ['张雨婷 领取 满 30 减 3', '09:12']].map(([t, m]) => `<div><span class="grow">${t}</span><span class="muted num">${m}</span></div>`).join('');
""")

# 4 全幅画布+浮动面板 ---------------------------------------------------------------------------------------
PAGES["4-全幅画布加浮动面板"] = ("全幅画布加浮动面板：门店分布", """
.map-svg { width: 100%; height: 100%; display: block; background: oklch(0.96 0.012 165); }
.pin { cursor: pointer; } .pin circle { transition: r var(--dur-fast) var(--ease-enter); } .pin:hover circle.dot { r: 11; }
.store { min-width: 220px; padding: var(--s-3) var(--s-4); border-radius: var(--r-md); background: var(--surface-2); display: grid; gap: var(--s-1); flex: none; cursor: pointer; }
.store.on { background: var(--brand-soft); box-shadow: 0 0 0 2px var(--brand); }
""", """
<header class="page-head"><div><h1>门店分布</h1><p class="muted">地图铺满主区，数字和列表做成圆角浅色浮动面板，贴四角或底边</p></div><div class="actions"><button class="btn">导出</button></div></header>
<section class="l-canvas" aria-label="门店地图">
  <div class="canvas"><svg class="map-svg" id="map" viewBox="0 0 1200 700" preserveAspectRatio="xMidYMid slice" role="img" aria-label="示意地图，标出五家门店的位置"></svg></div>
  <div class="float tl"><div class="field"><label for="q" class="sr-only">搜索门店</label><input id="q" class="input input--search" placeholder="搜索门店或地址"></div><div class="row wrap" style="margin-top:var(--s-3)"><span class="badge badge--ok">营业中 4</span><span class="badge">休息 1</span></div></div>
  <div class="float tr"><div class="stat stat--sm"><span class="stat-label">今日营业额</span><span class="stat-value num" id="v1">0</span><span class="stat-sub"><span class="delta up">▲ 7.5%</span> 五店合计</span></div><hr style="border:0;border-top:1px solid var(--line);margin:var(--s-3) 0"><div class="stat stat--sm"><span class="stat-label">今日订单</span><span class="stat-value num" id="v2">0</span></div></div>
  <div class="float bottom"><div class="row" style="overflow-x:auto;gap:var(--s-3);padding-bottom:var(--s-1)" id="stores"></div></div>
</section>
""", """
const stores = [['云帆店', 220, 180, 86, 1620, true], ['滨江店', 520, 300, 64, 1180, true], ['西溪店', 760, 160, 102, 1950, true], ['钱江店', 430, 470, 41, 760, true], ['萧山店', 960, 480, 0, 0, false]];
const svg = document.getElementById('map'); let html = '<g stroke="oklch(0.9 0.01 165)" stroke-width="1">' + Array.from({length: 13}, (_, i) => `<line x1="${i * 100}" y1="0" x2="${i * 100}" y2="700"/>`).join('') + Array.from({length: 8}, (_, i) => `<line x1="0" y1="${i * 100}" x2="1200" y2="${i * 100}"/>`).join('') + '</g>';
html += '<path d="M0 420 C 240 360, 420 520, 700 440 S 1050 330, 1200 380" fill="none" stroke="oklch(0.86 0.04 235)" stroke-width="46" stroke-linecap="round" opacity=".7"/><path d="M180 0 L 340 700" stroke="oklch(0.9 0.01 90)" stroke-width="14"/><path d="M0 250 L 1200 210" stroke="oklch(0.9 0.01 90)" stroke-width="12"/><rect x="620" y="60" width="180" height="110" rx="18" fill="oklch(0.93 0.04 150)"/>';
stores.forEach(([n, x, y, o, r, open], i) => { html += `<g class="pin" data-i="${i}" tabindex="0" role="button" aria-label="${n}"><circle cx="${x}" cy="${y}" r="32" fill="transparent"/><circle cx="${x}" cy="${y}" r="26" fill="${open ? 'var(--brand)' : 'var(--text-4)'}" opacity=".18"/><circle class="dot" cx="${x}" cy="${y}" r="9" fill="${open ? 'var(--brand)' : 'var(--text-3)'}" stroke="#fff" stroke-width="3"/></g>`; });
svg.innerHTML = html;
const list = document.getElementById('stores'); list.innerHTML = stores.map(([n, , , o, r, open], i) => `<div class="store${i === 0 ? ' on' : ''}" data-i="${i}"><div class="row between"><strong>${n}</strong><span class="badge ${open ? 'badge--ok' : ''}">${open ? '营业中' : '休息'}</span></div><span class="muted">今日 <b class="num">${o}</b> 单 · <b class="num">¥${r.toLocaleString()}</b></span></div>`).join('');
const sel = (i) => { list.querySelectorAll('.store').forEach((s) => s.classList.toggle('on', +s.dataset.i === i)); list.children[i].scrollIntoView({inline: 'center', block: 'nearest', behavior: UI.rm ? 'auto' : 'smooth'}); };
svg.addEventListener('click', (e) => { const p = e.target.closest('.pin'); if (p) sel(+p.dataset.i); }); list.addEventListener('click', (e) => { const s = e.target.closest('.store'); if (s) sel(+s.dataset.i); });
UI.count(document.getElementById('v1'), 5510, {prefix: '¥'}); UI.count(document.getElementById('v2'), 293);
""")

# 5 看板分列 ------------------------------------------------------------------------------------------------
PAGES["5-看板分列"] = ("看板分列：订单履约", "", """
<header class="page-head"><div><h1>订单履约</h1><p class="muted">按状态分列，列头写列名与数量；拖动卡片，或用卡片右上角的菜单移到别的列</p></div><div class="actions"><button class="btn btn--primary" id="add">模拟新订单</button></div></header>
<section id="board" aria-label="订单看板"></section>
""", """
const mk = (id, n, t, items, min) => ({id, title: n, meta: items, money: t, min});
const cols = [
  {id: 'wait', title: '待支付', cards: [mk('o1', 'A31', 1800, '招牌牛腩饭 ×1', 3), mk('o2', 'A32', 3600, '红烧鸡腿饭 ×2', 1)]},
  {id: 'make', title: '待出餐', cards: [mk('o3', 'A27', 2200, '黑椒牛柳饭 ×1', 18), mk('o4', 'A28', 4400, '清蒸鲈鱼套餐 ×1，粥品早餐 ×1', 11), mk('o5', 'A29', 1900, '轻食鸡胸沙拉 ×1', 6)]},
  {id: 'ready', title: '已出餐', cards: [mk('o6', 'A24', 2600, '清蒸鲈鱼套餐 ×1', 2), mk('o7', 'A25', 1500, '田园素食套餐 ×1', 4)]},
  {id: 'done', title: '已完成', cards: [mk('o8', 'A21', 1800, '宫保鸡丁饭 ×1', 0), mk('o9', 'A22', 2200, '番茄牛腩饭 ×1', 0), mk('o10', 'A23', 1700, '鱼香肉丝饭 ×1', 0)]},
];
UI.kanban(document.getElementById('board'), {columns: cols, card: (c) => UI.h('div.stack', {style: {gap: 'var(--s-2)', paddingRight: '28px'}}, UI.h('div.row.between', {}, UI.h('strong', {text: '取餐号 ' + c.title}), UI.h('span.num', {text: UI.money(c.money)})), UI.h('span.muted', {text: c.meta}), c.min > 10 ? UI.h('span.badge.badge--warn', {text: '已等 ' + c.min + ' 分钟'}) : UI.h('span.muted.num', {text: c.min ? '已等 ' + c.min + ' 分钟' : '已取走'})), onMove: (id, from, to) => UI.toast('已移到「' + cols.find((c) => c.id === to).title + '」')});
let n = 33; document.getElementById('add').addEventListener('click', () => UI.toast('新订单 A' + n++ + ' 已进入「待支付」'));
document.querySelectorAll('.kcard').forEach((el) => { el.style.position = 'relative'; const b = el.querySelector('button'); b.style.position = 'absolute'; b.style.top = '4px'; b.style.right = '4px'; });
""")

# 6 时间轴泳道 ----------------------------------------------------------------------------------------------
PAGES["6-时间轴泳道"] = ("时间轴泳道：门店排班", "", """
<header class="page-head"><div><h1>门店排班</h1><p class="muted">顶部是时间刻度，每行一条泳道；竖线是现在；红色是冲突，虚线块是空闲</p></div><div class="actions"><div class="seg" role="group" aria-label="日期"><button aria-pressed="false">昨天</button><button aria-pressed="true">今天</button><button aria-pressed="false">明天</button></div><button class="btn btn--primary">新增班次</button></div></header>
<section aria-label="排班泳道"><div id="lanes"></div><div class="legend" style="margin-top:var(--s-3)"><span><i style="background:var(--brand)"></i>正常班次</span><span><i style="background:var(--bad)"></i>时间冲突</span><span><i style="background:var(--warn)"></i>需确认</span><span><i style="background:none;border:1px dashed var(--line-strong)"></i>空闲</span></div></section>
""", """
const L = (label, sub, events) => ({label, sub, events});
UI.lanes(document.getElementById('lanes'), {from: 7, to: 21, now: 10.5, lanes: [
  L('陈晓燕', '前台', [{from: 8, to: 12, title: '早班 前台'}, {from: 13, to: 17, title: '午班 前台'}]),
  L('刘洋', '后厨', [{from: 7, to: 11, title: '备料'}, {from: 10, to: 14, title: '出餐高峰'}, {from: 16, to: 20, title: '晚班'}]),
  L('周敏', '店长', [{from: 9, to: 12, title: '盘点'}, {from: 12, to: 13, title: '会议', kind: 'warn'}]),
  L('赵建国', '配送', []),
  L('何建平', '前台', [{from: 11, to: 15, title: '午高峰 前台'}, {from: 14, to: 18, title: '代班 前台'}]),
], onEvent: (e, l) => UI.dialog({title: e.title, size: 'sm', body: UI.h('div.stack', {}, UI.h('div.row.between', {}, UI.h('span.muted', {text: '人员'}), UI.h('strong', {text: l.label})), UI.h('div.row.between', {}, UI.h('span.muted', {text: '时间'}), UI.h('strong.num', {text: e.from + ':00 – ' + e.to + ':00'}))), actions: [{label: '关闭', value: null}, {label: '调整班次', kind: 'primary'}]})});
document.querySelectorAll('.seg button').forEach((b) => b.addEventListener('click', () => { document.querySelectorAll('.seg button').forEach((x) => x.setAttribute('aria-pressed', String(x === b))); UI.toast('已切换到「' + b.textContent + '」'); }));
""")

for name, (title, css, body, js) in PAGES.items():
    (HERE / f"{name}.html").write_text(page(title, css, body, js), encoding="utf-8")
print("written", len(PAGES))
