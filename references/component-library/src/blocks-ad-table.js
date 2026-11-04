/* ================================================================
 * 后台 · 表格与列表（AD-TBL）· 筛选与搜索（AD-FLT）
 * 整个文件包在一个函数里。最上面几段（B、cg、tag、ROWS、BIG、dd……）是各组件共用的小工具，
 * 按编号取用某个组件时，连同这几段一起拿。组件内部类名一律 a- 开头，避免和页面样式重名。
 * 规则出处：Luz-System admin-list 规则卡（即输即查、行内开关失败回滚、批量栏不推表格、
 * 分页默认 20 条、分页条靠右、冻结列与吸顶表头、列设置/密度、已选条件标签 + 清空、详情编辑确认用居中面板）。
 * ================================================================ */
;(() => {
Object.assign(LINE, {
  adt_cols: '<rect x="3.5" y="4.5" width="17" height="15" rx="2.5"/><path d="M9.5 4.5v15M15 4.5v15"/>',
  adt_inbox: '<path d="M4 13.500 6.500 5.500h11l2.500 8"/><path d="M4 13.500V19h16v-5.500h-4.500l-1 2.500h-5l-1-2.500z"/>',
  adt_bookmark: '<path d="M7 4.500h10v15l-5-3.500-5 3.500z"/>',
  adt_grip: '<path d="M5 9h14M5 15h14"/>',
})

/* ---------- 共用：数据 ---------- */
const T0 = new Date(2026, 10, 4) /* 演示用“今天” */
const pad = (n) => String(n).padStart(2, '0')
const ymd = (d) => `${d.getFullYear()}-${pad(d.getMonth() + 1)}-${pad(d.getDate())}`
const money = (n) => Number(n).toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })
const AGO = [0, 0, 1, 1, 2, 3, 3, 5, 6, 6, 8, 9, 10, 12, 13, 15, 17, 19, 21, 23, 25, 27, 29, 32]
const ADDR = ['上海市浦东新区张江高科技园区祖冲之路 887 弄 3 号楼 1202 室（工作日白天无人，请放驿站）', '杭州市西湖区文三路 398 号东部软件园 5 幢', '成都市锦江区春熙路 26 号', '深圳市南山区科技园南区 R2-B 栋 7 层', '北京市朝阳区望京街 9 号 B 座 1503', '广州市天河区体育西路 103 号维多利广场 B 塔 22 层']
const CITIES = ['上海', '杭州', '成都', '深圳', '北京', '广州']
const PAY = ['微信支付', '支付宝', '余额支付', '微信支付', '银行卡', '支付宝']
const TN = { ok: 'ok', warn: 'warn', info: 'info', mute: 'mu', danger: 'bad' }
/* BIG(n)：在示例订单基础上扩出 n 条，订单号唯一、日期往前推 */
const BIG = (n) => Array.from({ length: n }, (_, i) => {
  const b = ORDER_ROWS[i % 24], ago = AGO[i % 24] + 33 * Math.floor(i / 24)
  const d = new Date(T0); d.setDate(d.getDate() - ago); d.setHours(9 + (i % 12), (i * 17) % 60, 0, 0)
  return Object.assign({}, b, {
    i, ago, d, ts: d.getTime(), date: `${ymd(d)} ${pad(d.getHours())}:${pad(d.getMinutes())}`,
    no: 'SO' + String(2026110528 - i * 7).padStart(10, '0'), who: NAMES[(i + 5 * Math.floor(i / 24)) % 12],
    item: b.sku + ' · ' + PRODUCTS[i % 9].d, addr: ADDR[i % 6], city: CITIES[i % 6], pay: PAY[i % 6],
    phone: '13' + (i % 10) + '****' + String(1000 + (i * 379) % 9000),
  })
})
const ROWS = BIG(24)
const GOODS = [
  { n: '无线降噪耳机', sp: '石墨灰 · 主动降噪', p: 599, k: 128, s: 2386, on: 1, i: 0, tags: ['数码'] },
  { n: '轻量跑鞋', sp: '云白 · 男女同款', p: 329, k: 46, s: 1204, on: 1, i: 1, tags: ['运动'] },
  { n: '陶瓷马克杯', sp: '手作釉面 · 350ml', p: 69, k: 312, s: 3112, on: 1, i: 2, tags: ['家居'] },
  { n: '帆布托特包', sp: '原色 · 可放 14 寸', p: 159, k: 0, s: 987, on: 0, i: 3, tags: ['箱包'] },
  { n: '机械腕表', sp: '钢壳皮带 · 40mm', p: 899, k: 23, s: 645, on: 1, i: 4, tags: ['配饰'] },
  { n: '护眼台灯', sp: '无频闪 · 三档调光', p: 219, k: 76, s: 1533, on: 0, i: 5, tags: ['数码', '家居'] },
  { n: '保温水杯', sp: '鼠尾草绿 · 500ml', p: 89, k: 540, s: 4208, on: 1, i: 6, tags: ['家居', '运动'] },
  { n: '保湿精华', sp: '玻尿酸 · 30ml', p: 258, k: 64, s: 502, on: 0, i: 7, tags: ['美妆'], lock: 1 },
  { n: '通勤双肩包', sp: '米色 · 防泼水', p: 369, k: 91, s: 860, on: 1, i: 8, tags: ['箱包', '运动'] },
]

/* ---------- 共用：小部件 HTML ---------- */
const ID = (p) => p.slice(0, 2).toUpperCase() + '-' + p.slice(2, 5).toUpperCase() + '-' + p.slice(5)
const tag = (tone, t) => `<span class="a-tg ${tone}"><i></i>${t}</span>`
const stTag = (r) => tag(TN[r.tone], r.st)
const ck = (a = '', label = '选择', on = false) => `<span class="a-ck${on ? ' on' : ''}" role="checkbox" tabindex="0" aria-label="${label}" ${a}></span>`
const SO = '<svg class="a-so" viewBox="0 0 8 12" aria-hidden="true"><path class="u" d="M4 0l4 5H0z"/><path class="d" d="M4 12 0 7h8z"/></svg>'
const cg = (ws) => `<colgroup>${ws.map((w) => (w ? `<col style="width:${w}px">` : '<col>')).join('')}</colgroup>`
const sumw = (ws, flex = 220) => ws.reduce((a, w) => a + (w || flex), 0)
const nm = (r) => `<div class="a-nm"><b>${r.who}</b><small>${r.no}</small></div>`
const svb = (n, c = 'a-i16') => `<span class="${c}" aria-hidden="true">${sv(n)}</span>`
const pnHTML = (page, P) => {
  const pl = P <= 7 ? Array.from({ length: P }, (_, i) => i + 1) : page <= 4 ? [1, 2, 3, 4, 5, '…', P] : page >= P - 3 ? [1, '…', P - 4, P - 3, P - 2, P - 1, P] : [1, '…', page - 1, page, page + 1, '…', P]
  return `<button class="a-pb" data-go="${page - 1}" ${page === 1 ? 'disabled' : ''} aria-label="上一页">${svb('left')}</button>` +
    pl.map((x) => (x === '…' ? '<span class="a-el">…</span>' : `<button class="a-pb${x === page ? ' on' : ''}" data-go="${x}" ${x === page ? 'aria-current="page"' : ''}>${x}</button>`)).join('') +
    `<button class="a-pb" data-go="${page + 1}" ${page === P ? 'disabled' : ''} aria-label="下一页">${svb('right')}</button>`
}
/* 下拉：key 是筛选键；opts 是 [值, 菜单文字, 数量?, 触发器文字?]；cur 是当前值。选中后触发器显示 data-v（缺省为菜单文字），值放 data-val */
const ddMenu = (opts, cur) => opts.map(([v, t, c, lb]) => `<div data-o role="option" data-v="${lb === undefined ? t : lb}" data-val="${v}" class="${v === cur ? 'on' : ''}">${t}${c !== undefined ? `<small class="a-cn${c === 0 ? ' z' : ''}">${c}</small>` : ''}</div>`).join('')
const fillDD = (root, key, opts, cur) => { const d = root.querySelector(`.a-dd[data-key="${key}"]`), hit = opts.find((x) => x[0] === cur) || opts[0]; d.querySelector('.menu').innerHTML = ddMenu(opts, cur); d.querySelector('[data-label]').textContent = hit[3] === undefined ? hit[1] : hit[3] }
const dd = (key, opts, cur, o = {}) => {
  const hit = opts.find((x) => x[0] === cur) || opts[0]
  return `<div class="a-dd${o.cls ? ' ' + o.cls : ''}" data-ix="dd" data-key="${key}"><button class="a-sel" data-tg type="button" aria-haspopup="listbox"><span data-label>${hit[3] === undefined ? hit[1] : hit[3]}</span>${svb('down', 'a-i14')}</button><div class="menu" role="listbox">${ddMenu(opts, cur)}</div></div>`
}

/* ---------- 共用：基础样式（每个组件各取一份，选择器全部带自己的前缀）---------- */
const B = (p, mw = 0, extra = '') => {
  const s = '.' + p
  return `.ixr[data-id="${ID(p)}"]{width:100%;min-width:0}
${s}{width:100%;${mw ? `min-width:${mw}px;` : ''}font-size:14px;line-height:22px;color:var(--ink)}
${s} .a-card{position:relative;background:var(--card);border:1px solid var(--line);border-radius:12px;box-shadow:0 1px 2px var(--sh04),0 8px 20px var(--sh04);overflow:hidden}
${s} .a-card.ov{overflow:visible}
${s} .a-tw{overflow-x:auto;border-radius:11px 11px 0 0}
${s} .a-card th:first-child{border-top-left-radius:11px}${s} .a-card th:last-child{border-top-right-radius:11px}
${s} table{width:100%;border-collapse:separate;border-spacing:0;table-layout:fixed;font-size:14px;line-height:22px}
${s} th{height:44px;padding:0 12px;background:var(--n2);color:var(--ink2);font-weight:600;text-align:center;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;border-bottom:1px solid var(--line)}
${s} td{height:48px;padding:0 12px;background:var(--card);border-bottom:1px solid var(--line);text-align:center;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;transition:background-color .15s}
${s} td.l{text-align:left;padding-left:20px}
${s} td.r{text-align:right;padding-right:28px}
${s} td.n,${s} td.r{font-variant-numeric:tabular-nums}
${s} td.k,${s} th.k{padding:0;text-align:center}
${s} td.ac{overflow:visible}
${s} tbody tr:last-child>td{border-bottom:0}
${s} tbody tr:hover>td{background:var(--n1)}
${s} tbody tr.sel>td{background:var(--pt)}
${s} tr.sel .a-tg.info,${s} tr.cur .a-tg.info{background:var(--lift)}
${s} th[data-sort]{cursor:pointer;transition:color .15s}
${s} th[data-sort]:hover{color:var(--ink)}
${s} .a-so{width:8px;height:12px;margin-left:6px;vertical-align:-2px}
${s} .a-so path{fill:var(--n9);transition:fill .15s}
${s} th.asc .u,${s} th.desc .d{fill:var(--p-text)}
${s} .a-i16{display:inline-flex;width:16px;height:16px;flex:none}
${s} .a-i14{display:inline-flex;width:14px;height:14px;flex:none}
${s} .a-i20{display:inline-flex;width:20px;height:20px;flex:none}
${s} .a-ck{position:relative;display:inline-block;width:16px;height:16px;border:1.5px solid color-mix(in srgb,var(--n9) 44%,var(--n10));border-radius:4px;background:var(--card);vertical-align:middle;cursor:pointer;transition:background-color .15s,border-color .15s}
${s} .a-ck::before{content:"";position:absolute;inset:-14px}
${s} .a-ck:hover{border-color:var(--p)}
${s} .a-ck.on,${s} .a-ck.part{background:var(--p);border-color:var(--p)}
${s} .a-ck.on::after{content:"";position:absolute;left:3.5px;top:.5px;width:4px;height:8px;border:solid var(--card);border-width:0 2px 2px 0;transform:rotate(45deg)}
${s} .a-ck.part::after{content:"";position:absolute;left:2px;top:4.5px;width:8px;height:2px;border-radius:1px;background:var(--card)}
${s} .a-tg{display:inline-flex;align-items:center;gap:6px;height:24px;padding:0 8px;border-radius:4px;font-size:12px;font-weight:600;line-height:1;white-space:nowrap;background:var(--soft);color:var(--ink3)}
${s} .a-tg i{width:6px;height:6px;border-radius:50%;background:currentColor;opacity:.7}
${s} .a-tg.ok{background:var(--ok-bg);color:var(--ok)}${s} .a-tg.warn{background:var(--warn-bg);color:var(--warn)}${s} .a-tg.bad{background:var(--danger-bg);color:var(--danger)}${s} .a-tg.info{background:var(--pt);color:var(--p-text)}${s} .a-tg.mu{background:var(--soft);color:var(--ink3)}
${s} .a-b{display:inline-flex;align-items:center;justify-content:center;gap:6px;height:32px;padding:0 14px;border-radius:8px;border:1px solid var(--n7);background:var(--card);color:var(--ink);white-space:nowrap;transition:background-color .15s,border-color .15s,color .15s}
${s} .a-b:hover{background:var(--n2);border-color:var(--n9)}
${s} .a-b.p{background:var(--p);border-color:var(--p);color:#fff}
${s} .a-b.p:hover{background:var(--pd);border-color:var(--pd)}
${s} .a-b.g{border-color:transparent;background:none;color:var(--ink2)}
${s} .a-b.g:hover{background:var(--soft)}
${s} .a-b.d{color:var(--danger)}
${s} .a-b:disabled{opacity:.45;pointer-events:none}
${s} .a-ib{display:inline-flex;align-items:center;justify-content:center;width:32px;height:32px;border-radius:8px;color:var(--ink2);transition:background-color .15s,color .15s}
${s} .a-ib:hover{background:var(--soft);color:var(--ink)}
${s} .a-ib.on{background:var(--pt);color:var(--p-text)}
${s} .a-lk{display:inline-flex;align-items:center;gap:2px;height:28px;padding:0 8px;border-radius:4px;color:var(--p-text);white-space:nowrap;transition:background-color .15s}
${s} .a-lk:hover{background:var(--pt)}
${s} .a-lk.d{color:var(--danger)}${s} .a-lk.d:hover{background:var(--danger-bg)}
${s} .a-lk:disabled{color:var(--ink6);pointer-events:none}
${s} .a-in{height:32px;padding:0 10px;border:1px solid var(--n7);border-radius:8px;background:var(--card);outline:none;min-width:0;font:inherit;transition:border-color .15s}
${s} .a-in:focus,${s} .a-sb:focus-within{border-color:var(--ink2)}
${s} .a-in::placeholder,${s} .a-sb input::placeholder{color:var(--ink3)}
${s} .a-in.err{border-color:var(--danger)}
${s} textarea.a-in{height:auto;padding:6px 10px;resize:none;line-height:22px}
${s} .a-sb{display:inline-flex;align-items:center;gap:8px;height:32px;padding:0 10px;border:1px solid var(--n7);border-radius:8px;background:var(--card);color:var(--ink3);transition:border-color .15s}
${s} .a-sb input{flex:1;min-width:0;border:0;outline:0;background:none;font:inherit;color:var(--ink)}
${s} .a-sb input::-webkit-search-cancel-button{-webkit-appearance:none;display:none}
${s} .a-sw{position:relative;display:inline-block;width:36px;height:20px;border-radius:10px;background:var(--n8);vertical-align:middle;cursor:pointer;flex:none;transition:background-color .2s}
${s} .a-sw::before{content:"";position:absolute;inset:-8px -4px}
${s} .a-sw::after{content:"";position:absolute;left:2px;top:2px;width:16px;height:16px;border-radius:50%;background:var(--card);box-shadow:0 1px 3px var(--sh25);transition:transform .2s cubic-bezier(.2,0,0,1)}
${s} .a-sw.on{background:var(--p)}${s} .a-sw.on::after{transform:translateX(16px)}
${s} .a-sw.ld{opacity:.6;pointer-events:none}
${s} .a-sw.dis{opacity:.45;cursor:not-allowed}
${s} .a-tb{position:relative;display:flex;flex-wrap:wrap;align-items:center;gap:10px;min-height:56px;padding:10px 16px;border-bottom:1px solid var(--line)}
${s} .a-tb .sp{flex:1}
${s} .a-ht{font-size:12px;line-height:18px;color:var(--ink3)}
${s} .a-pg{display:flex;align-items:center;justify-content:flex-end;flex-wrap:wrap;gap:8px 16px;padding:12px 16px;border-top:1px solid var(--line);color:var(--ink2)}
${s} .a-pn{display:flex;align-items:center;gap:4px}
${s} .a-pb{display:inline-flex;align-items:center;justify-content:center;min-width:32px;height:32px;padding:0 8px;border-radius:8px;border:1px solid transparent;color:var(--ink);font-variant-numeric:tabular-nums;transition:background-color .15s}
${s} .a-pb:hover{background:var(--soft)}
${s} .a-pb.on{border-color:var(--p);background:var(--pt);color:var(--p-text)}
${s} .a-pb:disabled{color:var(--ink6);pointer-events:none}
${s} .a-el{width:28px;text-align:center;color:var(--ink3)}
${s} .a-dd{position:relative;display:inline-block}
${s} .a-sel{display:inline-flex;align-items:center;gap:8px;height:32px;padding:0 10px 0 12px;border:1px solid var(--n7);border-radius:8px;background:var(--card);white-space:nowrap;transition:border-color .15s,background-color .15s}
${s} .a-sel:hover{border-color:var(--n9)}
${s} .a-dd.open .a-sel{border-color:var(--ink2)}
${s} .a-sel svg{color:var(--ink3);transition:transform .2s cubic-bezier(.2,0,0,1)}
${s} .a-dd.open .a-sel svg{transform:rotate(180deg)}
${s} .a-sel.has{border-color:var(--pm);background:var(--pt);color:var(--p-text)}
${s} .a-sel.has svg{color:var(--p-text)}
${s} .menu{padding:4px;background:var(--card2);border:1px solid var(--line);border-radius:8px;box-shadow:0 8px 24px var(--sh12);min-width:128px;text-align:left}
${s} .menu>*{display:flex;align-items:center;gap:8px;width:100%;height:32px;padding:0 10px;border-radius:4px;white-space:nowrap;cursor:pointer}
${s} .menu>*:hover{background:var(--n3)}
${s} .menu>.on{background:var(--pt);color:var(--p-text)}
${s} .menu>.d{color:var(--danger)}
${s} .menu>button:disabled{color:var(--ink6);pointer-events:none}
${s} .menu>hr{height:1px;padding:0;margin:4px 0;border:0;background:var(--line)}
${s} .menu small,${s} .a-cn{margin-left:auto;padding-left:16px;font-size:12px;color:var(--ink3);font-variant-numeric:tabular-nums}
${s} .a-cn.z{opacity:.55}
${s} .a-chip{display:inline-flex;align-items:center;gap:6px;height:32px;padding:0 12px;border:1px solid var(--n7);border-radius:8px;background:var(--card);white-space:nowrap;cursor:pointer;transition:background-color .15s,border-color .15s,color .15s}
${s} .a-chip:hover{border-color:var(--n9);background:var(--n2)}
${s} .a-chip.on{border-color:var(--pm);background:var(--pt);color:var(--p-text)}
${s} .a-seg{display:inline-flex;gap:2px;padding:2px;border-radius:8px;background:var(--soft)}
${s} .a-seg button{height:28px;padding:0 12px;border-radius:6px;color:var(--ink2);white-space:nowrap;transition:background-color .15s,color .15s}
${s} .a-seg button.on{background:var(--lift);color:var(--ink);box-shadow:0 1px 3px var(--sh12)}
${s} .a-nm{min-width:0;overflow:hidden}
${s} .a-nm b{display:block;font-weight:600;line-height:20px;overflow:hidden;text-overflow:ellipsis}
${s} .a-nm small{display:block;font-size:12px;line-height:16px;color:var(--ink3);overflow:hidden;text-overflow:ellipsis;font-variant-numeric:tabular-nums}
${s} .a-av{display:flex;align-items:center;gap:10px;min-width:0}
${s} .a-av .a-nm{flex:1}
${s} .a-th{width:36px;height:36px;border-radius:8px;object-fit:cover;flex:none;background:var(--ph)}
${s} .ix-ov{align-items:center;justify-content:center;padding:16px}
${s} .a-dlg{position:relative;z-index:1;width:min(440px,100%);max-height:100%;overflow:auto;padding:22px 24px 0;border-radius:16px;background:var(--card);box-shadow:0 20px 50px var(--sh22)}
${s} .ix-ov.show .a-dlg{animation:adtIn .22s cubic-bezier(.2,0,0,1)}
${s} .a-dlg h4{display:flex;align-items:center;justify-content:space-between;margin:0 0 12px;font-size:16px;line-height:24px;font-weight:600}
${s} .a-dlg p{margin:0 0 16px;color:var(--ink2)}
${s} .a-dlg .ft{position:sticky;bottom:0;display:flex;justify-content:flex-end;gap:10px;margin:0 -24px;padding:16px 24px 18px;background:var(--card)}
${s} .a-sk{display:block;height:12px;border-radius:6px;background:linear-gradient(90deg,var(--n4) 25%,var(--n2) 50%,var(--n4) 75%);background-size:200% 100%;animation:adtSk 1.4s linear infinite}
@keyframes adtIn{from{opacity:0;transform:translateY(8px) scale(.98)}to{opacity:1;transform:none}}
@keyframes adtSk{from{background-position:200% 0}to{background-position:-200% 0}}
@keyframes adtFade{from{opacity:0}to{opacity:1}}
@keyframes adtSpin{to{transform:rotate(360deg)}}
@media(prefers-reduced-motion:reduce){${s} .a-sk{animation:none}${s} *{animation-duration:1ms!important}}
${extra}`
}

/* ================================================================
 * TBL 表格与列表
 * ================================================================ */

/* AD-TBL-001 基础数据表 */
{
  const W = [200, 0, 88, 128, 112, 160, 120]
  def({
    id: 'AD-TBL-001', name: '基础数据表', style: '排序状态',
    fit: '订单、会员、商品这类最常见的列表：第一列放人能看懂的标识，点表头排序，状态用低饱和标签。',
    avoid: '数据不止一页时要接分页（AD-TBL-003）；整列都是同一个值的列不要单独占列。',
    kw: 'table 表格 数据表 排序 列表 订单列表 基础表格 状态标签 sort',
    wide: true,
    css: B('adtbl001', 0),
    html: () => `<div class="adtbl001"><div class="a-card"><div class="a-tw"><table data-ix="sort" data-pagination="none" style="min-width:${sumw(W)}px">${cg(W)}
<thead><tr><th>客户</th><th>商品</th><th data-sort="n">数量${SO}</th><th data-sort="n">金额（元）${SO}</th><th data-sort="s">状态${SO}</th><th data-sort="n" class="desc" aria-sort="descending">下单时间${SO}</th><th>操作</th></tr></thead>
<tbody>${ROWS.slice(0, 8).map((r) => `<tr><td class="l">${nm(r)}</td><td class="l" title="${r.item}">${r.item}</td><td class="n">${r.q}</td><td class="r" data-v="${r.amt}">${money(r.amt)}</td><td>${stTag(r)}</td><td class="n" data-v="${r.ts}">${r.date}</td><td><button class="a-lk" type="button">详情</button><button class="a-lk" type="button">编辑</button></td></tr>`).join('')}</tbody></table></div>
<div class="a-pg"><span>共 8 条</span></div></div></div>`,
  })
}

/* AD-TBL-002 勾选与批量操作 */
{
  const W = [44, 200, 0, 128, 112, 160]
  def({
    id: 'AD-TBL-002', name: '勾选与批量操作', style: '批量栏',
    fit: '要对多行一起处理（发货、导出、删除）：勾选后批量栏替换工具栏同一位置，表格不被推开。',
    avoid: '只有单行操作的列表不要放勾选列；批量删除这类不可撤销动作必须二次确认（居中面板）。',
    kw: 'checkbox 勾选 批量 多选 全选 半选 批量操作 批量删除 已选',
    wide: true,
    css: B('adtbl002', 0, `
.adtbl002 .bar2{position:absolute;inset:0;z-index:2;display:flex;align-items:center;gap:10px;padding:0 16px;background:var(--pt);animation:adtFade .15s}
.adtbl002 .bar2 b{font-weight:600;color:var(--p-text);font-variant-numeric:tabular-nums}
.adtbl002 .bar2 .sp{flex:1}
.adtbl002 .a-card{min-height:0}
@media(max-width:520px){.adtbl002 .bar2 .opt{display:none}}`),
    html: () => `<div class="adtbl002"><div class="a-card" data-ix="checks"><div class="a-tb"><label class="a-sb" style="width:240px">${svb('search')}<input type="search" placeholder="搜索客户、订单号" aria-label="搜索订单"></label><span class="sp"></span><span class="a-ht">共 8 条</span><button class="a-b" type="button" data-toast="已开始导出，完成后在消息中心通知">${svb('download')}导出</button>
<div class="bar2" data-bar hidden><span>已选 <b data-count>0</b> 项</span><button class="a-b p" type="button" data-toast="已提交批量发货">批量发货</button><button class="a-b opt" type="button" data-toast="已开始导出所选订单">导出所选</button><button class="a-b d" type="button" data-open="del">删除</button><span class="sp"></span><button class="a-b g" type="button" data-act="clear">取消选择</button></div></div>
<div class="a-tw"><table style="min-width:${sumw(W)}px">${cg(W)}
<thead><tr><th class="k">${ck('data-all', '全选')}</th><th>客户</th><th>商品</th><th>金额（元）</th><th>状态</th><th>下单时间</th></tr></thead>
<tbody>${ROWS.slice(0, 8).map((r, k) => `<tr><td class="k">${ck('data-c', '选择 ' + r.who)}</td><td class="l">${nm(r)}</td><td class="l" title="${r.item}">${r.item}</td><td class="r">${money(r.amt)}</td><td>${stTag(r)}</td><td class="n">${r.date}</td></tr>`).join('')}</tbody></table></div></div>
<div class="ix-ov" data-ov="del"><div class="ix-mask"></div><div class="a-dlg" role="alertdialog" aria-modal="true"><h4>删除所选订单</h4><p>将删除已选的 <b data-n>0</b> 条订单，删除后不能恢复。</p><div class="ft"><button class="a-b" type="button" data-close>取消</button><button class="a-b p" type="button" data-act="do-del" data-close>确认删除</button></div></div></div></div>`,
    js: (root) => {
      const $$ = (s) => [...root.querySelectorAll(s)]
      const sel = () => $$('tbody [data-c].on')
      root.addEventListener('click', (e) => {
        if (e.target.closest('[data-open=del]')) root.querySelector('[data-n]').textContent = sel().length
        if (e.target.closest('[data-act=clear]')) { $$('[data-c]').forEach((x) => x.classList.remove('on')); IX.init(root) }
        if (e.target.closest('[data-act=do-del]')) {
          const rows = sel().map((x) => x.closest('tr')); rows.forEach((r) => r.remove()); IX.init(root); IX.toast(root, `已删除 ${rows.length} 条订单`)
          root.querySelector('.a-ht').textContent = `共 ${root.querySelectorAll('tbody tr').length} 条`
        }
      })
    },
  })
}

/* AD-TBL-003 分页器 */
{
  const W = [200, 0, 128, 112, 160]
  const rowH = (r) => `<tr style="--h:46px"><td class="l">${nm(r)}</td><td class="l" title="${r.item}">${r.item}</td><td class="r">${money(r.amt)}</td><td>${stTag(r)}</td><td class="n">${r.date}</td></tr>`
  const pgBar = (page, P, total, size) => `<span class="a-tot">共 ${total} 条</span>${dd('size', [['10', '10 条/页'], ['20', '20 条/页'], ['50', '50 条/页'], ['100', '100 条/页']], String(size), { cls: 'up' })}<div class="a-pn">${pnHTML(page, P)}</div><label class="a-jump" ${P <= 5 ? 'hidden' : ''}>跳至 <input class="a-in" type="number" min="1" max="${P}" value="" aria-label="跳至第几页" style="width:56px;height:32px;text-align:center"> 页</label>`
  def({
    id: 'AD-TBL-003', name: '分页器', style: '页码条数',
    fit: '数据可能超过一页的任何列表：共 N 条、每页条数（默认 20，可选 10/20/50/100）、上一页、页码（超过 7 页折叠）、下一页，超过 5 页加“跳至”。',
    avoid: '确定永远不超过一页的列表（如 5 个会员等级）不放分页；改每页条数或筛选后要回到第 1 页；小程序和手机不用页码，改滚动加载。',
    kw: 'pagination 分页 页码 翻页 每页条数 跳转 pager 上一页 下一页',
    wide: true,
    css: B('adtbl003', 0, `
.adtbl003 .a-tw{max-height:520px;overflow:auto}
.adtbl003 thead th{position:sticky;top:0;z-index:2}
.adtbl003 td{height:var(--h,46px)}
.adtbl003 tbody.ld{opacity:.5;transition:opacity .15s}
.adtbl003 .a-jump{display:inline-flex;align-items:center;gap:6px}
.adtbl003 .a-pg .menu{top:auto;bottom:calc(100% + 6px)}`),
    html: () => `<div class="adtbl003"><div class="a-card ov"><div class="a-tw"><table data-pagination="20" style="min-width:${sumw(W)}px">${cg(W)}
<thead><tr><th>客户</th><th>商品</th><th>金额（元）</th><th>状态</th><th>下单时间</th></tr></thead>
<tbody>${BIG(126).slice(0, 20).map(rowH).join('')}</tbody></table></div>
<div class="a-pg">${pgBar(1, 7, 126, 20)}</div></div></div>`,
    js: (root) => {
      const $ = (s) => root.querySelector(s)
      const DATA = BIG(126); let size = 20, page = 1
      const render = (soft) => {
        const P = Math.ceil(DATA.length / size); page = Math.max(1, Math.min(page, P))
        const tb = $('tbody'), draw = () => {
          tb.innerHTML = DATA.slice((page - 1) * size, page * size).map(rowH).join(''); tb.classList.remove('ld'); $('.a-tw').scrollTop = 0
        }
        $('.a-pn').innerHTML = pnHTML(page, P); $('.a-jump').hidden = P <= 5; $('.a-jump input').max = P
        $('table').dataset.pagination = size
        if (soft) { tb.classList.add('ld'); setTimeout(draw, 160) } else draw()
      }
      root.addEventListener('click', (e) => {
        const g = e.target.closest('[data-go]'); if (g && !g.disabled) { page = +g.dataset.go; render(true) }
        const o = e.target.closest('.menu [data-o]'); if (o) { size = +o.dataset.val; page = 1; render(true) }
      })
      root.addEventListener('keydown', (e) => { if (e.key === 'Enter' && e.target.matches('.a-jump input') && e.target.value) { page = +e.target.value; e.target.value = ''; render(true) } })
      render()
    },
  })
}

/* AD-TBL-004 行内操作与更多菜单 */
{
  const W = [200, 0, 128, 112, 160, 210]
  const R4 = ROWS.slice(0, 8)
  const can = (r) => r.st === '待付款' || r.st === '待发货'
  const act = (r, k) => `<td class="ac"><button class="a-lk" type="button" data-act="detail" data-open="dt">详情</button><button class="a-lk" type="button" data-act="edit" data-open="ed">编辑</button><span class="a-dd${k >= 5 ? ' up' : ''}" data-ix="dd"><button class="a-lk" type="button" data-tg aria-label="更多操作" aria-haspopup="menu">更多${svb('down', 'a-i14')}</button><div class="menu" role="menu" style="min-width:156px"><button type="button" role="menuitem" data-m="copy">复制订单号</button><button type="button" role="menuitem" data-m="print">打印面单</button><hr><button type="button" role="menuitem" class="d" data-m="cancel" data-open="cf" ${can(r) ? '' : 'disabled'}>取消订单${can(r) ? '' : `<small>${r.st}</small>`}</button></div></span></td>`
  def({
    id: 'AD-TBL-004', name: '行内操作与更多', style: '文字操作',
    fit: '行操作放最后一列：最常用的两个文字操作（详情、编辑）外露，其余收进“更多”；详情、编辑、取消订单一律用居中悬浮面板，危险操作不放第一个。',
    avoid: '行内文字操作不加图标；操作超过 3 个别全摊开；“更多”按钮要有无障碍名称；已完成的订单把“取消”置灰并写原因。',
    kw: '行操作 操作列 更多 下拉菜单 详情 编辑 删除 取消订单 row action dropdown 居中面板',
    wide: true,
    css: B('adtbl004', sumw(W), `
.adtbl004 .a-dd.up .menu{top:auto;bottom:calc(100% + 6px)}
.adtbl004 .a-dd .menu{left:auto;right:0}
.adtbl004 .a-card.ov th:first-child{border-top-left-radius:11px}.adtbl004 .a-card.ov th:last-child{border-top-right-radius:11px}
.adtbl004 .kv{display:flex;gap:12px;padding:6px 0;border-bottom:1px solid var(--line)}
.adtbl004 .kv span{flex:none;width:76px;color:var(--ink3)}
.adtbl004 .kv b{flex:1;min-width:0;font-weight:400;overflow-wrap:anywhere}
.adtbl004 .fld{display:block;margin-bottom:12px}
.adtbl004 .fld span{display:block;margin-bottom:4px;color:var(--ink2)}
.adtbl004 .fld .a-in{width:100%}
.adtbl004 .rs{display:flex;flex-wrap:wrap;gap:8px}`),
    html: () => `<div class="adtbl004"><div class="a-card ov"><table style="min-width:${sumw(W)}px">${cg(W)}
<thead><tr><th>客户</th><th>商品</th><th>金额（元）</th><th>状态</th><th>下单时间</th><th>操作</th></tr></thead>
<tbody>${R4.map((r, k) => `<tr data-i="${r.i}"><td class="l">${nm(r)}</td><td class="l" title="${r.item}">${r.item}</td><td class="r">${money(r.amt)}</td><td>${stTag(r)}</td><td class="n">${r.date}</td>${act(r, k)}</tr>`).join('')}</tbody></table>
<div class="a-pg"><span>共 8 条</span></div></div>
<div class="ix-ov" data-ov="dt"><div class="ix-mask"></div><div class="a-dlg" role="dialog" aria-modal="true"><h4><span>订单详情</span><button class="a-ib" type="button" data-close aria-label="关闭">${svb('close')}</button></h4><div class="bd"></div><div class="ft"><button class="a-b" type="button" data-close>关闭</button><button class="a-b p" type="button" data-act="detail-edit">编辑订单</button></div></div></div>
<div class="ix-ov" data-ov="ed"><div class="ix-mask"></div><div class="a-dlg" role="dialog" aria-modal="true"><h4><span>编辑订单</span><button class="a-ib" type="button" data-close aria-label="关闭">${svb('close')}</button></h4>
<label class="fld"><span>收货人</span><input class="a-in" data-f="who"></label><label class="fld"><span>联系电话</span><input class="a-in" data-f="phone"></label><label class="fld"><span>收货地址</span><textarea class="a-in" rows="2" data-f="addr"></textarea></label>
<div class="ft"><button class="a-b" type="button" data-close>取消</button><button class="a-b p" type="button" data-act="save" data-close>保存</button></div></div></div>
<div class="ix-ov" data-ov="cf"><div class="ix-mask"></div><div class="a-dlg" role="alertdialog" aria-modal="true"><h4><span>取消订单</span></h4><p>将取消订单 <b data-no></b>，已支付金额原路退回。请选择取消原因。</p><div class="rs" data-ix="radio"><span class="a-chip" data-o>客户申请</span><span class="a-chip" data-o>商品缺货</span><span class="a-chip" data-o>地址有误</span><span class="a-chip" data-o>其他</span></div>
<div class="ft"><button class="a-b" type="button" data-close>先不取消</button><button class="a-b p" type="button" data-act="do-cancel" data-close disabled>确认取消</button></div></div></div></div>`,
    js: (root) => {
      const $ = (s) => root.querySelector(s), $$ = (s) => [...root.querySelectorAll(s)]
      let tr = null, r = null
      const fill = () => {
        $('[data-ov=dt] .bd').innerHTML = [['订单号', r.no], ['客户', r.who], ['商品', r.item + ' × ' + r.q], ['金额（元）', money(r.amt)], ['状态', stTag(r)], ['支付方式', r.pay], ['下单时间', r.date], ['收货地址', r.addr]].map(([k, v]) => `<div class="kv"><span>${k}</span><b>${v}</b></div>`).join('')
      }
      root.addEventListener('click', (e) => {
        const a = e.target.closest('[data-act],[data-m]'); const t = e.target.closest('tbody tr')
        if (t && a) { tr = t; r = ROWS[+t.dataset.i] }
        if (!a || !r) return
        const act = a.dataset.act, m = a.dataset.m
        if (act === 'detail') fill()
        if (act === 'detail-edit') { $('[data-ov=dt]').classList.remove('show'); a.dataset.open = 'ed'; $('[data-ov=ed]').classList.add('show') }
        if (act === 'edit' || act === 'detail-edit') { $$('[data-ov=ed] [data-f]').forEach((i) => (i.value = r[i.dataset.f])) }
        if (act === 'save') { r.who = $('[data-f=who]').value || r.who; r.phone = $('[data-f=phone]').value; r.addr = $('[data-f=addr]').value; tr.querySelector('.a-nm b').textContent = r.who; IX.toast(root, '订单信息已保存') }
        if (m === 'copy') { try { navigator.clipboard.writeText(r.no) } catch (x) {} IX.toast(root, '已复制订单号 ' + r.no) }
        if (m === 'print') IX.toast(root, '面单已加入打印队列')
        if (m === 'cancel') { $('[data-no]').textContent = r.no; $$('[data-ov=cf] [data-o]').forEach((x) => x.classList.remove('on')); $('[data-act=do-cancel]').disabled = true }
        if (act === 'do-cancel') { r.st = '已取消'; r.tone = 'mute'; tr.children[3].innerHTML = stTag(r); tr.querySelector('[data-m=cancel]').disabled = true; IX.toast(root, '订单 ' + r.no + ' 已取消') }
        if (m) a.closest('.a-dd').classList.remove('open')
      })
      root.addEventListener('click', (e) => { if (e.target.closest('[data-ov=cf] [data-o]')) setTimeout(() => ($('[data-act=do-cancel]').disabled = false), 0) })
    },
  })
}

/* AD-TBL-005 行内开关 */
{
  const W = [0, 120, 96, 128, 220]
  const G = GOODS.slice(0, 8)
  const stText = (g) => (g.lock ? '审核中' : g.on ? '已上架' : '已下架')
  def({
    id: 'AD-TBL-005', name: '行内开关', style: '直接生效',
    fit: '上架/下架、启用/停用这类可逆的状态：点开关立即生效并轻提示，失败时回滚并在原位写原因。',
    avoid: '影响用户资金或不可撤销的操作不能用开关直接生效（要二次确认）；开关旁一定写状态文字，不只靠颜色。',
    kw: 'switch 开关 上架 下架 启用 停用 直接生效 回滚 失败原因 toggle 轻提示',
    wide: true,
    css: B('adtbl005', 0, `
.adtbl005 .a-sc{display:flex;align-items:center;justify-content:center;gap:8px}
.adtbl005 .a-sl{width:48px;text-align:left;font-size:12px;color:var(--ink2)}
.adtbl005 .a-why{display:block;height:0;font-size:12px;line-height:16px;color:var(--danger);overflow:hidden;opacity:0;transition:height .2s cubic-bezier(.2,0,0,1),opacity .2s}
.adtbl005 .a-why.show{height:16px;opacity:1}
.adtbl005 td.sc{padding-top:6px;padding-bottom:6px}
.adtbl005 .z{color:var(--danger)}`),
    html: () => `<div class="adtbl005"><div class="a-card"><div class="a-tw"><table style="min-width:${sumw(W)}px">${cg(W)}
<thead><tr><th>商品</th><th>价格（元）</th><th>库存</th><th>近 30 天销量</th><th>上架状态</th></tr></thead>
<tbody>${G.map((g) => `<tr data-k="${g.k}" data-n="${g.n}"><td class="l"><div class="a-av"><img class="a-th" src="${P(g.i)}" alt=""><div class="a-nm"><b>${g.n}</b><small>${g.sp}</small></div></div></td><td class="r">${money(g.p)}</td><td class="n${g.k === 0 ? ' z' : ''}">${g.k === 0 ? '0（缺货）' : g.k}</td><td class="n">${g.s.toLocaleString('en-US')}</td><td class="sc"><div class="a-sc"><span class="a-sw${g.on ? ' on' : ''}${g.lock ? ' dis' : ''}" role="switch" tabindex="0" aria-checked="${!!g.on}" aria-label="${g.n}上架开关"${g.lock ? ' title="审核通过后才能上架"' : ''}></span><span class="a-sl">${stText(g)}</span></div><span class="a-why" role="alert"></span></td></tr>`).join('')}</tbody></table></div>
<div class="a-pg"><span>共 8 条</span></div></div></div>`,
    js: (root) => {
      root.addEventListener('click', (e) => {
        const sw = e.target.closest('.a-sw'); if (!sw || sw.classList.contains('dis') || sw.classList.contains('ld')) return
        const tr = sw.closest('tr'), lab = tr.querySelector('.a-sl'), why = tr.querySelector('.a-why'), to = !sw.classList.contains('on')
        const set = (on) => { sw.classList.toggle('on', on); sw.setAttribute('aria-checked', on); lab.textContent = on ? '已上架' : '已下架' }
        why.classList.remove('show'); set(to); sw.classList.add('ld') /* 先生效、带加载态 */
        setTimeout(() => {
          sw.classList.remove('ld')
          if (to && +tr.dataset.k === 0) { set(!to); why.textContent = '库存为 0，无法上架'; why.classList.add('show'); setTimeout(() => why.classList.remove('show'), 3200) } /* 失败：回滚并写原因 */
          else IX.toast(root, `${tr.dataset.n} ${to ? '已上架' : '已下架'}`)
        }, 480)
      })
    },
  })
}

/* AD-TBL-006 行内编辑 */
{
  const W = [64, 0, 130, 110, 320]
  const G = GOODS.slice(0, 7), RM = ['主推款，活动期间不要改价', '', '供应商 7 天内补货，缺货期间在前台显示“预计 11-12 到货”，不要提前下架', '', '腕表类仅限实体店自提', '', '']
  const cell = (f, v, c = '') => `<td class="ed ${c}" data-f="${f}"><span class="a-v" title="${v}">${v}</span><button class="a-pe" type="button" aria-label="编辑">${svb('edit', 'a-i14')}</button></td>`
  def({
    id: 'AD-TBL-006', name: '行内编辑', style: '双击改值',
    fit: '改价、改库存、改备注这类高频小改动：双击单元格变输入框，回车保存、Esc 取消；格式不对原位提示，不用进编辑页。',
    avoid: '字段之间有联动校验、或需要填很多项时用居中编辑面板；触屏没有双击，所以悬停/点按时要有铅笔入口。',
    kw: '行内编辑 内联编辑 双击 inline edit 改价 改库存 单元格编辑 回车保存',
    wide: true,
    css: B('adtbl006', sumw(W), `
.adtbl006 td.ed{position:relative;cursor:text}
.adtbl006 td.ed:hover{box-shadow:inset 0 0 0 1px var(--pm)}
.adtbl006 td.ed.editing{box-shadow:none;overflow:visible}
.adtbl006 .a-v{display:block;overflow:hidden;text-overflow:ellipsis}
.adtbl006 .a-v:empty::before{content:"双击添加";color:var(--ink6)}
.adtbl006 .a-pe{position:absolute;right:4px;top:50%;margin-top:-14px;display:none;align-items:center;justify-content:center;width:28px;height:28px;border-radius:4px;color:var(--ink3);background:var(--card)}
.adtbl006 td.ed:hover .a-pe{display:inline-flex}
.adtbl006 .a-pe:hover{color:var(--p-text);background:var(--pt)}
@media(hover:none){.adtbl006 .a-pe{display:inline-flex}}
.adtbl006 td.ed .a-in{width:100%;height:34px}
.adtbl006 td.r .a-in{text-align:right}.adtbl006 td.n .a-in{text-align:center}
.adtbl006 .a-er{position:absolute;left:12px;top:100%;z-index:3;margin-top:-6px;padding:2px 8px;border-radius:4px;background:var(--danger-fill);color:#fff;font-size:12px;line-height:18px;white-space:nowrap}
.adtbl006 td.hit{animation:adtHit 1.2s cubic-bezier(.2,0,0,1)}
@keyframes adtHit{from{background:var(--pm)}to{background:var(--card)}}
.adtbl006 .a-card{overflow:visible}`),
    html: () => `<div class="adtbl006"><div class="a-card"><div class="a-tw" style="overflow:visible"><table style="min-width:${sumw(W)}px">${cg(W)}
<thead><tr><th>图片</th><th>商品名称</th><th>价格（元）</th><th>库存</th><th>备注</th></tr></thead>
<tbody>${G.map((g, k) => `<tr><td class="k"><img class="a-th" src="${P(g.i)}" alt="" style="margin:0 auto"></td>${cell('n', g.n, 'l')}${cell('p', money(g.p), 'r')}${cell('k', g.k, 'n')}${cell('m', RM[k], 'l')}</tr>`).join('')}</tbody></table></div>
<div class="a-pg"><span>共 7 条</span></div></div></div>`,
    js: (root) => {
      const NUM = { p: /^\d{1,6}(\.\d{1,2})?$/, k: /^\d{1,6}$/ }
      const LBL = { n: '名称', p: '价格', k: '库存', m: '备注' }
      const begin = (td) => {
        if (td.classList.contains('editing')) return
        const old = td.querySelector('.a-v').textContent.replace(/,/g, ''); td.dataset.old = old; td.classList.add('editing')
        td.innerHTML = `<input class="a-in" value="${old.replace(/"/g, '&quot;')}" aria-label="编辑${LBL[td.dataset.f]}">`
        const inp = td.querySelector('input'); inp.focus(); inp.select()
        let done = false
        const end = (save) => {
          if (done) return
          const v = inp.value.trim(), f = td.dataset.f
          let bad = ''
          if (save) { if (f === 'n' && !v) bad = '名称不能为空'; else if (NUM[f] && !NUM[f].test(v)) bad = f === 'p' ? '请输入价格，最多两位小数' : '库存须是整数' }
          if (save && bad) { inp.classList.add('err'); let er = td.querySelector('.a-er'); if (!er) { er = document.createElement('em'); er.className = 'a-er'; td.appendChild(er) } er.textContent = bad; return }
          done = true
          const val = save ? (f === 'p' ? money(v) : v) : td.dataset.old
          td.classList.remove('editing'); td.innerHTML = `<span class="a-v" title="${val}">${val}</span><button class="a-pe" type="button" aria-label="编辑">${svb('edit', 'a-i14')}</button>`
          if (save && v !== td.dataset.old.replace(/,/g, '')) { td.classList.remove('hit'); void td.offsetWidth; td.classList.add('hit'); IX.toast(root, `已保存：${LBL[f]}改为 ${val || '空'}`) }
        }
        inp.addEventListener('keydown', (e) => { if (e.key === 'Enter') end(true); if (e.key === 'Escape') end(false) })
        inp.addEventListener('blur', () => { if (!done) { const f = td.dataset.f, v = inp.value.trim(); const ok = !(f === 'n' && !v) && !(NUM[f] && !NUM[f].test(v)); if (ok) end(true); else { end(false); IX.toast(root, '输入无效，已还原') } } })
      }
      root.addEventListener('dblclick', (e) => { const td = e.target.closest('td.ed'); if (td) begin(td) })
      root.addEventListener('click', (e) => { const b = e.target.closest('.a-pe'); if (b) begin(b.closest('td')) })
    },
  })
}

/* AD-TBL-007 可展开行 */
{
  const W = [48, 200, 0, 128, 112, 160, 120]
  const R7 = ROWS.slice(0, 6)
  const sub = (r) => { const s = SKUS[r.i % 9]; return `<div class="a-in2"><table class="a-st">${cg([0, 150, 110, 80, 120])}<thead><tr><th>商品</th><th>规格</th><th>单价（元）</th><th>数量</th><th>小计（元）</th></tr></thead><tbody><tr><td class="l"><div class="a-av"><img class="a-th" src="${P(s[2])}" alt=""><span>${s[0]}</span></div></td><td class="l">${PRODUCTS[r.i % 9].d.split(' · ')[0]}</td><td class="r">${money(s[1])}</td><td class="n">${r.q}</td><td class="r">${money(r.amt)}</td></tr><tr><td class="l"><div class="a-av"><img class="a-th" src="${P(2)}" alt=""><span>赠品 · 陶瓷马克杯</span></div></td><td class="l">手作釉面</td><td class="r">0.00</td><td class="n">1</td><td class="r">0.00</td></tr></tbody></table><div class="a-lg"><span>支付方式 ${r.pay}</span><span>运费 0.00 元</span><span>收货地址 ${r.addr}</span></div></div>` }
  def({
    id: 'AD-TBL-007', name: '可展开行', style: '子表明细',
    fit: '一行下面还有明细（订单的商品、批次的出入库、方案的步骤）：点箭头在行下展开子表，不用跳页；表头箭头可全部展开。',
    avoid: '明细很多或要编辑时用详情面板；展开内容别比主行信息还重；同时展开太多行页面会很长。',
    kw: 'expand 展开行 子表 明细 嵌套表格 折叠 订单明细 展开收起 expandable',
    wide: true,
    css: B('adtbl007', 0, `
.adtbl007 .a-xb{display:inline-flex;align-items:center;justify-content:center;width:32px;height:32px;border-radius:8px;color:var(--ink2);transition:background-color .15s}
.adtbl007 .a-xb:hover{background:var(--soft)}
.adtbl007 .a-xb span{display:inline-flex;width:16px;height:16px;transition:transform .2s cubic-bezier(.2,0,0,1)}
.adtbl007 tr.open .a-xb span,.adtbl007 th .a-xb.all span{transform:rotate(90deg)}
.adtbl007 th .a-xb{background:none}
.adtbl007 tr.sub>td,.adtbl007 tbody tr.sub:hover>td{height:auto;padding:0;background:var(--n1);border-bottom:0}
.adtbl007 tr.open+tr.sub>td{border-bottom:1px solid var(--line)}
.adtbl007 .a-sp{display:grid;grid-template-rows:0fr;transition:grid-template-rows .25s cubic-bezier(.2,0,0,1)}
.adtbl007 tr.open+tr.sub .a-sp{grid-template-rows:1fr}
.adtbl007 .a-sp>div{overflow:hidden}
.adtbl007 .a-in2{padding:4px 28px 16px 60px;white-space:normal;text-align:left}
.adtbl007 .a-st th{height:40px;background:none;border-bottom:1px solid var(--line)}
.adtbl007 .a-st td{height:44px;background:none;border-bottom:1px solid var(--line)}
.adtbl007 .a-st tbody tr:last-child>td{border-bottom:1px solid var(--line)}
.adtbl007 .a-st tbody tr:hover>td{background:none}
.adtbl007 .a-lg{display:flex;flex-wrap:wrap;gap:4px 24px;padding-top:10px;font-size:12px;line-height:18px;color:var(--ink3)}
.adtbl007 .a-lg span:last-child{flex:1 1 280px;min-width:0}`),
    html: () => `<div class="adtbl007"><div class="a-card"><div class="a-tw"><table style="min-width:${sumw(W)}px">${cg(W)}
<thead><tr><th class="k"><button class="a-xb" type="button" data-all-x aria-label="展开全部">${svb('right')}</button></th><th>客户</th><th>商品</th><th>金额（元）</th><th>状态</th><th>下单时间</th><th>操作</th></tr></thead>
<tbody>${R7.map((r, k) => `<tr class="${k === 0 ? 'open' : ''}"><td class="k"><button class="a-xb" type="button" data-x aria-expanded="${k === 0}" aria-label="展开订单明细">${svb('right')}</button></td><td class="l">${nm(r)}</td><td class="l" title="${r.item}">${r.item}</td><td class="r">${money(r.amt)}</td><td>${stTag(r)}</td><td class="n">${r.date}</td><td><button class="a-lk" type="button">详情</button></td></tr><tr class="sub"><td colspan="7"><div class="a-sp"><div>${sub(r)}</div></div></td></tr>`).join('')}</tbody></table></div>
<div class="a-pg"><span>共 6 条</span></div></div></div>`,
    js: (root) => {
      const tb = root.querySelector('.a-tw > table > tbody'), rows = () => [...tb.children].filter((r) => !r.classList.contains('sub'))
      const sync = () => { const all = rows().every((r) => r.classList.contains('open')); root.querySelector('[data-all-x]').classList.toggle('all', all); root.querySelector('[data-all-x]').setAttribute('aria-label', all ? '收起全部' : '展开全部') }
      root.addEventListener('click', (e) => {
        const b = e.target.closest('[data-x]'); if (b) { const tr = b.closest('tr'); b.setAttribute('aria-expanded', tr.classList.toggle('open')); sync(); return }
        const a = e.target.closest('[data-all-x]'); if (a) { const to = !a.classList.contains('all'); rows().forEach((r) => { r.classList.toggle('open', to); r.querySelector('[data-x]').setAttribute('aria-expanded', to) }); sync() }
      })
      sync()
    },
  })
}

/* AD-TBL-008 树形表格 */
{
  const W = [0, 120, 168, 112, 200]
  const T = [
    ['服饰鞋包', [['鞋靴', [['跑步鞋', 38], ['休闲板鞋', 36]]], ['箱包', [['托特包', 31], ['双肩背包', 31]]], ['配饰', 50]]],
    ['数码配件', [['耳机音响', [['降噪耳机', 52], ['运动耳机', 36]]], ['智能穿戴', 54]]],
    ['家居生活', [['杯具水具', [['保温水杯', 64], ['陶瓷杯', 56]]], ['灯具', 95]]],
    ['美妆个护', [['护肤', 61], ['彩妆', 32]]],
  ]
  const OWN = ['林小满', '陈晓雨', '王子豪', '李安然', '周一帆', '赵可心']
  const flat = []
  const walk = (nodes, lv, pid) => nodes.map((n, k) => {
    const id = (pid ? pid + '_' : 'c') + (k + 1), kids = Array.isArray(n[1]) ? n[1] : null
    const me = { id, pid, lv, name: n[0], n: 0, kids: !!kids, st: (k + lv) % 7 === 5 ? '停用' : '启用' }
    flat.push(me); me.n = kids ? walk(kids, lv + 1, id).reduce((a, b) => a + b, 0) : n[1]; return me.n
  })
  walk(T, 0, '')
  flat.forEach((x, i) => (x.own = OWN[i % 6], x.oi = i % 6))
  def({
    id: 'AD-TBL-008', name: '树形表格', style: '层级缩进',
    fit: '商品分类、部门组织、菜单权限这类有层级的数据：名称列按层级缩进，点箭头展开收起，可一键全部展开；数量向上汇总。',
    avoid: '层级超过 4 层或节点上千时用左树右表的布局；只有两层且每层很少时直接用分组表（AD-TBL-013）。',
    kw: 'tree 树形 层级 分类 缩进 展开 收起 组织架构 部门 树表格 tree table',
    wide: true,
    css: B('adtbl008', 0, `
.adtbl008 .tn{display:flex;align-items:center;gap:6px;min-width:0;padding-left:calc(var(--lv)*28px)}
.adtbl008 .tn b{font-weight:400;overflow:hidden;text-overflow:ellipsis}
.adtbl008 tr.lv0 .tn b{font-weight:600}
.adtbl008 .tn em{flex:none;padding:0 6px;border-radius:4px;background:var(--soft);color:var(--ink3);font-size:12px;line-height:18px;font-variant-numeric:tabular-nums}
.adtbl008 .tx{display:inline-flex;align-items:center;justify-content:center;flex:none;width:24px;height:24px;border-radius:4px;color:var(--ink2);transition:background-color .15s}
.adtbl008 .tx:hover{background:var(--soft)}
.adtbl008 .tx span{display:inline-flex;width:14px;height:14px;transition:transform .2s cubic-bezier(.2,0,0,1)}
.adtbl008 tr.open .tx span{transform:rotate(90deg)}
.adtbl008 .tx.nil{pointer-events:none;visibility:hidden}
.adtbl008 .own{display:flex;align-items:center;justify-content:center;gap:8px}`),
    html: () => `<div class="adtbl008"><div class="a-card"><div class="a-tb"><button class="a-b" type="button" data-act="all">${svb('layers')}全部展开</button><button class="a-b g" type="button" data-act="none">全部收起</button><span class="sp"></span><button class="a-b p" type="button" data-toast="已新增一级分类">${svb('plus')}新增分类</button></div>
<div class="a-tw"><table style="min-width:${sumw(W)}px">${cg(W)}
<thead><tr><th>分类名称</th><th>商品数</th><th>负责人</th><th>状态</th><th>操作</th></tr></thead>
<tbody>${flat.map((x) => `<tr class="lv${x.lv}${x.id === 'c1' || x.id === 'c1_1' ? ' open' : ''}" data-id="${x.id}" data-pid="${x.pid}" data-lv="${x.lv}" ${x.lv > 0 && x.pid !== 'c1' && x.pid !== 'c1_1' ? 'hidden' : ''}><td class="l"><div class="tn" style="--lv:${x.lv}"><button class="tx${x.kids ? '' : ' nil'}" type="button" data-t aria-label="展开或收起">${svb('right', 'a-i14')}</button><b>${x.name}</b></div></td><td class="n">${x.n}</td><td><div class="own">${critter(x.oi, 24)}<span>${x.own}</span></div></td><td>${tag(x.st === '启用' ? 'ok' : 'mu', x.st)}</td><td><button class="a-lk" type="button" data-toast="已在“${x.name}”下新增子分类">新增子类</button><button class="a-lk" type="button" data-toast="打开“${x.name}”的编辑面板">编辑</button></td></tr>`).join('')}</tbody></table></div>
<div class="a-pg"><span>共 ${flat.length} 个分类</span></div></div></div>`,
    js: (root) => {
      const rows = () => [...root.querySelectorAll('tbody tr')]
      const apply = () => { const m = {}; rows().forEach((r) => { const p = m[r.dataset.pid]; r.hidden = !!r.dataset.pid && (p.hidden || !p.classList.contains('open')); m[r.dataset.id] = r }) }
      root.addEventListener('click', (e) => {
        const t = e.target.closest('[data-t]'); if (t) { t.closest('tr').classList.toggle('open'); apply(); return }
        const a = e.target.closest('[data-act]'); if (!a) return
        const to = a.dataset.act === 'all'; rows().forEach((r) => { if (r.querySelector('.tx:not(.nil)')) r.classList.toggle('open', to) }); apply()
      })
      apply()
    },
  })
}

/* AD-TBL-009 固定表头与固定列 */
{
  const W = [44, 190, 130, 240, 80, 110, 120, 110, 120, 110, 110, 100, 160, 0, 120]
  const D9 = BIG(36).map((r) => { const disc = r.i % 4 === 1 ? 20 : r.i % 5 === 2 ? 10 : 0; return Object.assign(r, { unit: r.amt / r.q, disc, paid: r.amt - disc }) })
  def({
    id: 'AD-TBL-009', name: '固定表头与固定列', style: '大表滚动',
    fit: '列很多、行很多的大表（订单明细、对账表）：表头吸顶，勾选列和对象名列冻结在左，操作列冻结在右；容器内横向滚动，鼠标可按住拖动，滚动方向的冻结列显示层级提示。',
    avoid: '冻结列合计不超过容器宽的 40%；列少于 6 列不用冻结；手机上冻结列要少，操作列始终可见。',
    kw: 'sticky 固定表头 冻结列 固定列 大表格 横向滚动 吸顶 fixed header frozen column 虚拟滚动',
    wide: true,
    css: B('adtbl009', 0, `
.adtbl009 .a-tw{height:440px;overflow:auto;position:relative;cursor:grab;border-radius:11px 11px 0 0}
.adtbl009 .a-tw.drag{cursor:grabbing;user-select:none}
.adtbl009 .a-tw:focus-visible{outline:2px solid var(--ink2);outline-offset:-2px}
.adtbl009 table{min-width:${sumw(W)}px}
.adtbl009 thead th{position:sticky;top:0;z-index:2}
.adtbl009 .fl{position:sticky;left:0;z-index:1}
.adtbl009 .fl2{position:sticky;left:44px;z-index:1;box-shadow:inset -1px 0 0 var(--line)}
.adtbl009 .fr{position:sticky;right:0;z-index:1;box-shadow:inset 1px 0 0 var(--line)}
.adtbl009 thead .fl,.adtbl009 thead .fl2,.adtbl009 thead .fr{top:0;z-index:4}
.adtbl009 .a-tw.sx-l .fl2{box-shadow:inset -1px 0 0 var(--line),8px 0 10px -6px var(--sh14)}
.adtbl009 .a-tw.sx-r .fr{box-shadow:inset 1px 0 0 var(--line),-8px 0 10px -6px var(--sh14)}
.adtbl009 .a-pg{justify-content:space-between}
.adtbl009 .a-pg b{font-weight:600;color:var(--p-text);font-variant-numeric:tabular-nums}`),
    html: () => `<div class="adtbl009"><div class="a-card" data-ix="checks"><div class="a-tw" data-ix="drag" tabindex="0" role="region" aria-label="订单明细表，可横向和纵向滚动" data-pagination="none"><table>${cg(W)}
<thead><tr><th class="k fl">${ck('data-all', '全选')}</th><th class="fl2">客户</th><th>手机号</th><th>商品</th><th>数量</th><th>单价（元）</th><th>金额（元）</th><th>优惠（元）</th><th>实付（元）</th><th>状态</th><th>支付方式</th><th>收货城市</th><th>下单时间</th><th>收货地址</th><th class="fr">操作</th></tr></thead>
<tbody>${D9.map((r) => `<tr><td class="k fl">${ck('data-c', '选择 ' + r.who)}</td><td class="l fl2">${nm(r)}</td><td class="n">${r.phone}</td><td class="l" title="${r.item}">${r.item}</td><td class="n">${r.q}</td><td class="r">${money(r.unit)}</td><td class="r">${money(r.amt)}</td><td class="r">${money(r.disc)}</td><td class="r">${money(r.paid)}</td><td>${stTag(r)}</td><td>${r.pay}</td><td>${r.city}</td><td class="n">${r.date}</td><td class="l" title="${r.addr}">${r.addr}</td><td class="fr"><button class="a-lk" type="button">详情</button><button class="a-lk" type="button">编辑</button></td></tr>`).join('')}</tbody></table></div>
<div class="a-pg"><span>共 ${D9.length} 条，已选 <b data-count>0</b> 条</span></div></div></div>`,
    js: (root) => {
      const tw = root.querySelector('.a-tw')
      const upd = () => { tw.classList.toggle('sx-l', tw.scrollLeft > 2); tw.classList.toggle('sx-r', tw.scrollLeft + tw.clientWidth < tw.scrollWidth - 2) }
      tw.addEventListener('scroll', upd, { passive: true }); upd(); setTimeout(upd, 60)
      tw.addEventListener('keydown', (e) => { if (e.key === 'ArrowRight') tw.scrollLeft += 80; if (e.key === 'ArrowLeft') tw.scrollLeft -= 80 })
    },
  })
}

/* AD-TBL-010 汇总行 */
{
  const W = [44, 0, 120, 80, 130, 120, 130]
  const R10 = ROWS.slice(0, 7).map((r) => { const disc = r.i % 3 === 1 ? 20 : r.i % 4 === 2 ? 10 : 0; return Object.assign({}, r, { unit: r.amt / r.q, disc, paid: r.amt - disc }) })
  const ALL = BIG(126).map((r) => ({ q: r.q, amt: r.amt, disc: r.i % 3 === 1 ? 20 : r.i % 4 === 2 ? 10 : 0 }))
  const tot = (a) => ({ q: a.reduce((s, x) => s + x.q, 0), amt: a.reduce((s, x) => s + x.amt, 0), disc: a.reduce((s, x) => s + x.disc, 0) })
  const A = tot(ALL)
  def({
    id: 'AD-TBL-010', name: '汇总行', style: '合计已选',
    fit: '对账、报表、订单明细等需要看合计的表：表尾固定一行“本页合计”，勾选行后同一行变成“已选 N 项合计”，不新增行、不推动表格；再用一行淡色写全部筛选结果的合计。',
    avoid: '单价、日期这类不能相加的列留空，不要硬凑平均值；合计行的精度和格式与明细列保持一致。',
    kw: 'summary 汇总 合计 总计 统计行 tfoot 求和 已选合计 对账 表尾',
    wide: true,
    css: B('adtbl010', 0, `
.adtbl010 tfoot td{height:48px;background:var(--n2);border-top:1px solid var(--line);border-bottom:0;font-weight:600}
.adtbl010 tfoot tr.all td{height:44px;background:var(--card);font-weight:400;color:var(--ink2);border-top:1px dashed var(--line)}
.adtbl010 tfoot tr:hover>td{background:var(--n2)}.adtbl010 tfoot tr.all:hover>td{background:var(--card)}
.adtbl010 tfoot b{font-weight:600}
.adtbl010 tfoot .pick{color:var(--p-text)}
.adtbl010 tbody tr:last-child>td{border-bottom:0}`),
    html: () => `<div class="adtbl010"><div class="a-card" data-ix="checks"><div class="a-tw"><table style="min-width:${sumw(W)}px">${cg(W)}
<thead><tr><th class="k">${ck('data-all', '全选')}</th><th>商品</th><th>单价（元）</th><th>数量</th><th>金额（元）</th><th>优惠（元）</th><th>实收（元）</th></tr></thead>
<tbody>${R10.map((r) => `<tr data-q="${r.q}" data-amt="${r.amt}" data-disc="${r.disc}"><td class="k">${ck('data-c', '选择 ' + r.sku)}</td><td class="l"><div class="a-av"><img class="a-th" src="${P(r.img)}" alt=""><div class="a-nm"><b>${r.sku}</b><small>${r.who} · ${r.no}</small></div></div></td><td class="r">${money(r.unit)}</td><td class="n">${r.q}</td><td class="r">${money(r.amt)}</td><td class="r">${money(r.disc)}</td><td class="r">${money(r.paid)}</td></tr>`).join('')}</tbody>
<tfoot><tr class="cur"><td></td><td class="l"><span data-lab>本页合计</span></td><td></td><td class="n" data-s="q"></td><td class="r" data-s="amt"></td><td class="r" data-s="disc"></td><td class="r" data-s="paid"></td></tr>
<tr class="all"><td></td><td class="l">全部筛选结果合计（共 126 条）</td><td></td><td class="n">${A.q}</td><td class="r">${money(A.amt)}</td><td class="r">${money(A.disc)}</td><td class="r">${money(A.amt - A.disc)}</td></tr></tfoot></table></div></div></div>`,
    js: (root) => {
      const $$ = (s) => [...root.querySelectorAll(s)]
      const calc = () => {
        const sel = $$('tbody tr.sel'), use = sel.length ? sel : $$('tbody tr')
        const sum = (k) => use.reduce((a, r) => a + (+r.dataset[k]), 0)
        const q = sum('q'), amt = sum('amt'), disc = sum('disc')
        const f = { q, amt: money(amt), disc: money(disc), paid: money(amt - disc) }
        $$('[data-s]').forEach((c) => (c.textContent = f[c.dataset.s]))
        const lab = root.querySelector('[data-lab]'); lab.textContent = sel.length ? `已选 ${sel.length} 项合计` : '本页合计'; lab.classList.toggle('pick', !!sel.length)
      }
      root.addEventListener('click', () => setTimeout(calc, 0)); calc()
    },
  })
}

/* AD-TBL-011 状态列与表头筛选 */
{
  const W = [200, 0, 128, 150, 160]
  const R11 = ROWS.slice(0, 10)
  const ORDER = ['待发货', '退款中', '待付款', '配送中', '已完成', '已取消']
  const cnt = (s) => R11.filter((r) => r.st === s).length
  const opts = () => ORDER.map((s) => [s, cnt(s)]).sort((a, b) => (a[1] === 0) - (b[1] === 0))
  def({
    id: 'AD-TBL-011', name: '状态列与表头筛选', style: '低饱和标签',
    fit: '枚举列（状态、类型、渠道）：状态用“圆点 + 文字”的低饱和标签，同一状态全系统同名同外观；表头漏斗点开选项（带数量，可多选），选中即生效。',
    avoid: '状态别只靠颜色区分（要有文字）；标签里不放营销口号；选项按处理顺序排，数量为 0 的弱化并排最后。',
    kw: '状态 标签 tag 表头筛选 列筛选 枚举 漏斗 filter 多选 数量 状态列',
    wide: true,
    css: B('adtbl011', sumw(W), `
.adtbl011{min-height:370px}
.adtbl011 .a-card{overflow:visible}
.adtbl011 th.f{position:relative}
.adtbl011 .a-fb{position:relative;display:inline-flex;align-items:center;justify-content:center;width:28px;height:28px;margin-left:4px;border-radius:4px;color:var(--ink3);vertical-align:middle;transition:background-color .15s,color .15s}
.adtbl011 .a-fb:hover{background:var(--n4);color:var(--ink)}
.adtbl011 .a-fb.on{background:var(--pt);color:var(--p-text)}
.adtbl011 .a-fb em{position:absolute;right:-2px;top:-2px;min-width:16px;height:16px;padding:0 4px;border-radius:8px;background:var(--p);color:#fff;font-size:12px;line-height:16px;font-weight:600}
.adtbl011 .a-pop{position:absolute;z-index:20;width:208px;padding:6px;border:1px solid var(--line);border-radius:12px;background:var(--card);box-shadow:0 8px 24px var(--sh14);animation:adtIn .18s cubic-bezier(.2,0,0,1)}
.adtbl011 .a-opt{display:flex;align-items:center;gap:10px;height:36px;padding:0 10px;border-radius:8px;cursor:pointer;text-align:left}
.adtbl011 .a-opt:hover{background:var(--n3)}
.adtbl011 .a-opt .a-cn{margin-left:auto;padding-left:0}
.adtbl011 .a-opt.z{color:var(--ink3)}
.adtbl011 .a-pop .ft{display:flex;justify-content:space-between;align-items:center;margin-top:4px;padding:6px 6px 2px;border-top:1px solid var(--line)}`),
    html: () => `<div class="adtbl011"><div class="a-card"><table style="min-width:${sumw(W)}px">${cg(W)}
<thead><tr><th>客户</th><th>商品</th><th>金额（元）</th><th class="f"><span>状态</span><button class="a-fb" type="button" aria-label="筛选状态" aria-haspopup="true">${svb('filter')}</button></th><th>下单时间</th></tr></thead>
<tbody>${R11.map((r) => `<tr data-st="${r.st}"><td class="l">${nm(r)}</td><td class="l" title="${r.item}">${r.item}</td><td class="r">${money(r.amt)}</td><td>${stTag(r)}</td><td class="n">${r.date}</td></tr>`).join('')}</tbody></table>
<div class="a-pop" hidden role="dialog" aria-label="状态筛选">${opts().map(([s, n]) => `<div class="a-opt${n === 0 ? ' z' : ''}" data-s="${s}" role="checkbox" aria-checked="false">${ck('', s)}<span>${s}</span><small class="a-cn${n === 0 ? ' z' : ''}">${n}</small></div>`).join('')}<div class="ft"><button class="a-lk" type="button" data-clear>清除筛选</button><span class="a-ht" data-ft></span></div></div>
<div class="a-pg"><span data-total>共 ${R11.length} 条</span></div></div></div>`,
    js: (root) => {
      const $ = (s) => root.querySelector(s), $$ = (s) => [...root.querySelectorAll(s)]
      const card = $('.a-card'), pop = $('.a-pop'), btn = $('.a-fb'), th = btn.closest('th'), set = new Set()
      const apply = () => {
        let n = 0
        $$('tbody tr').forEach((r) => { const ok = !set.size || set.has(r.dataset.st); r.hidden = !ok; if (ok) n++ })
        $$('.a-opt').forEach((o) => { const on = set.has(o.dataset.s); o.querySelector('.a-ck').classList.toggle('on', on); o.setAttribute('aria-checked', on) })
        btn.classList.toggle('on', set.size > 0); btn.querySelector('em') && btn.querySelector('em').remove()
        if (set.size) btn.insertAdjacentHTML('beforeend', `<em>${set.size}</em>`)
        $('[data-total]').textContent = set.size ? `已筛选 ${n} 条（全部 ${$$('tbody tr').length} 条）` : `共 ${n} 条`
      }
      const place = () => { const c = card.getBoundingClientRect(), t = th.getBoundingClientRect(); pop.style.top = (t.bottom - c.top + 4) + 'px'; pop.style.left = Math.max(8, Math.min(c.width - 216, t.left - c.left + t.width / 2 - 104)) + 'px' }
      const close = () => { pop.hidden = true }
      btn.addEventListener('click', (e) => { e.stopPropagation(); pop.hidden = !pop.hidden; if (!pop.hidden) place() })
      pop.addEventListener('click', (e) => {
        e.stopPropagation()
        const o = e.target.closest('.a-opt'); if (o) { const s = o.dataset.s; set.has(s) ? set.delete(s) : set.add(s); apply() }
        if (e.target.closest('[data-clear]')) { set.clear(); apply() }
      })
      const off = (e) => { if (!root.isConnected) return document.removeEventListener('click', off); if (!pop.hidden && !pop.contains(e.target)) close() }
      document.addEventListener('click', off)
      apply()
    },
  })
}

/* AD-TBL-012 人员表 */
{
  const W = [0, 120, 150, 140, 110, 150]
  const ROLE = ['管理员', '运营', '客服', '财务', '仓管', '运营', '客服', '技术', '运营', '客服']
  const LAST = ['刚刚', '12 分钟前', '昨天 18:20', '2 小时前', '2026-10-28', '今天 09:12', '3 小时前', '2026-11-01', '昨天 11:05', '5 分钟前']
  const STS = ['在职', '在职', '休假', '在职', '停用', '在职', '在职', '休假', '在职', '在职']
  const TNE = { 在职: 'ok', 休假: 'warn', 停用: 'mu' }
  const M = NAMES.slice(0, 10).map((n, i) => ({ n, d: DEPTS[i % 6], role: ROLE[i], phone: '13' + (i % 10) + '****' + String(2046 + i * 311).slice(-4), last: LAST[i], st: STS[i], i }))
  const row = (m) => `<tr><td class="l"><div class="a-av">${critter(m.i, 36)}<div class="a-nm"><b>${m.n}</b><small>${m.d}</small></div></div></td><td><span class="a-tg info" style="gap:0">${m.role}</span></td><td class="n">${m.phone}</td><td class="n">${m.last}</td><td>${tag(TNE[m.st], m.st)}</td><td><button class="a-lk" type="button" data-toast="打开“${m.n}”的编辑面板">编辑</button><button class="a-lk" type="button" data-toast="打开“${m.n}”的权限设置">权限</button></td></tr>`
  def({
    id: 'AD-TBL-012', name: '人员表', style: '头像姓名',
    fit: '成员、客户、联系人名单：第一列“默认动物头像 + 姓名 + 部门”，角色用浅色标签，手机号脱敏，状态带文字；搜索即输即查，无结果给一句话和清除入口。',
    avoid: '没有照片时用按人固定的卡通动物头像，严禁首字母或文字头像；手机号、证件号默认脱敏，点开详情再看全。',
    kw: '人员 成员 用户 员工 头像 avatar 部门 角色 联系人 通讯录 用户列表 搜索',
    wide: true,
    css: B('adtbl012', 0, `
.adtbl012 .a-av svg{flex:none}
.adtbl012 tr.empty td{height:200px;background:var(--card);color:var(--ink2);white-space:normal}
.adtbl012 .em{display:flex;flex-direction:column;align-items:center;gap:6px}
.adtbl012 .em span.i{width:40px;height:40px;color:var(--ink6)}`),
    html: () => `<div class="adtbl012"><div class="a-card"><div class="a-tb"><label class="a-sb" style="width:260px">${svb('search')}<input type="search" placeholder="搜索姓名、部门、角色" aria-label="搜索成员"></label><span class="sp"></span><button class="a-b p" type="button" data-toast="打开新增成员面板">${svb('plus')}新增成员</button></div>
<div class="a-tw"><table style="min-width:${sumw(W)}px">${cg(W)}
<thead><tr><th>成员</th><th>角色</th><th>手机号</th><th>最近活跃</th><th>状态</th><th>操作</th></tr></thead>
<tbody>${M.map(row).join('')}<tr class="empty" hidden><td colspan="6"><div class="em"><span class="i">${sv('users')}</span><b>没有找到匹配的成员</b><span>换个关键词试试，或</span><button class="a-lk" type="button" data-clear>清除搜索</button></div></td></tr></tbody></table></div>
<div class="a-pg"><span data-total>共 ${M.length} 人</span></div></div></div>`,
    js: (root) => {
      const $ = (s) => root.querySelector(s), inp = $('input')
      const apply = () => {
        const q = inp.value.trim().toLowerCase(); let n = 0
        ;[...root.querySelectorAll('tbody tr:not(.empty)')].forEach((r) => { const ok = !q || r.textContent.toLowerCase().includes(q); r.hidden = !ok; if (ok) n++ })
        $('tr.empty').hidden = n > 0; $('[data-total]').textContent = q ? `找到 ${n} 人（共 ${M.length} 人）` : `共 ${M.length} 人`
      }
      inp.addEventListener('input', apply)
      root.addEventListener('click', (e) => { if (e.target.closest('[data-clear]')) { inp.value = ''; apply(); inp.focus() } })
    },
  })
}

/* AD-TBL-013 分组表 */
{
  const W = [0, 130, 150, 100, 130]
  const GR = [['上海徐汇店', [0, 1, 4]], ['杭州西湖店', [2, 6, 5]], ['成都春熙店', [3, 7, 8]]]
  const rowsOf = (ids, gi) => ids.map((id, k) => { const g = GOODS[id], sales = 40 + ((g.s * (gi + 2)) % 360) + k * 17, stock = g.k === 0 ? 0 : Math.max(6, Math.round(g.k / (gi + 1))); return { g, sales, amt: sales * g.p, stock } })
  const stOf = (x) => (x.stock === 0 ? tag('bad', '缺货') : x.stock < 30 ? tag('warn', '库存预警') : tag('ok', '在售'))
  def({
    id: 'AD-TBL-013', name: '分组表', style: '可折叠分组',
    fit: '按门店、部门、日期归类的列表：分组头显示名称、条数和分组小计，点分组头折叠或展开，适合“先看每组总量，再看明细”。',
    avoid: '分组超过十几个、每组只有一两行时，分组头比数据还多，改用筛选；分组头里别放操作按钮，免得和整行点击冲突。',
    kw: '分组 group 折叠 分组头 小计 门店 归类 collapse 分类汇总 展开收起',
    wide: true,
    css: B('adtbl013', 0, `
.adtbl013 tr.g>td{height:44px;padding:0;background:var(--n2);cursor:pointer;border-bottom:1px solid var(--line)}
.adtbl013 tr.g:hover>td{background:var(--soft)}
.adtbl013 .gh{display:flex;align-items:center;gap:10px;height:44px;padding:0 20px 0 12px;text-align:left}
.adtbl013 .gx{display:inline-flex;width:20px;height:20px;align-items:center;justify-content:center;color:var(--ink2)}
.adtbl013 .gx span{display:inline-flex;width:14px;height:14px;transition:transform .2s cubic-bezier(.2,0,0,1)}
.adtbl013 tr.g.open .gx span{transform:rotate(90deg)}
.adtbl013 .gh b{font-weight:600}
.adtbl013 .gh em{padding:0 8px;border-radius:4px;background:var(--card);color:var(--ink3);font-size:12px;line-height:20px;border:1px solid var(--line)}
.adtbl013 .gh .sp{flex:1}
.adtbl013 .gh .m{color:var(--ink2);font-variant-numeric:tabular-nums}
.adtbl013 .gh .m b{color:var(--ink)}`),
    html: () => `<div class="adtbl013"><div class="a-card"><div class="a-tw"><table style="min-width:${sumw(W)}px">${cg(W)}
<thead><tr><th>商品</th><th>本月销量</th><th>销售额（元）</th><th>库存</th><th>状态</th></tr></thead>
<tbody>${GR.map(([name, ids], gi) => { const rs = rowsOf(ids, gi), sq = rs.reduce((a, x) => a + x.sales, 0), sa = rs.reduce((a, x) => a + x.amt, 0)
  return `<tr class="g open" data-gk="${gi}" tabindex="0" role="button" aria-expanded="true"><td colspan="5"><div class="gh"><span class="gx">${svb('right', 'a-i14')}</span><b>${name}</b><em>${rs.length} 个商品</em><span class="sp"></span><span class="m">销量 <b>${sq.toLocaleString('en-US')}</b></span><span class="m">销售额 <b>${money(sa)}</b> 元</span></div></td></tr>` +
  rs.map((x) => `<tr data-gk="${gi}"><td class="l"><div class="a-av"><img class="a-th" src="${P(x.g.i)}" alt=""><div class="a-nm"><b>${x.g.n}</b><small>${x.g.sp}</small></div></div></td><td class="n">${x.sales}</td><td class="r">${money(x.amt)}</td><td class="n">${x.stock}</td><td>${stOf(x)}</td></tr>`).join('') }).join('')}</tbody></table></div>
<div class="a-pg"><span>共 ${GR.length} 家门店，${GR.reduce((a, g) => a + g[1].length, 0)} 条记录</span></div></div></div>`,
    js: (root) => {
      const tog = (g) => { const open = !g.classList.contains('open'); g.classList.toggle('open', open); g.setAttribute('aria-expanded', open); root.querySelectorAll(`tr[data-gk="${g.dataset.gk}"]:not(.g)`).forEach((r) => (r.hidden = !open)) }
      root.addEventListener('click', (e) => { const g = e.target.closest('tr.g'); if (g) tog(g) })
      root.addEventListener('keydown', (e) => { const g = e.target.closest && e.target.closest('tr.g'); if (g && (e.key === 'Enter' || e.key === ' ')) { e.preventDefault(); tog(g) } })
    },
  })
}

/* AD-TBL-014 密度切换 */
{
  const W = [200, 0, 128, 112, 160]
  const KEY = 'adt-density'
  def({
    id: 'AD-TBL-014', name: '密度切换', style: '三档行高',
    fit: '数据量大、用户差异大的表：右上角三档切换，紧凑 40、默认 48、宽松 56，字号不变；选择按用户保存，下次进来还是这档。',
    avoid: '默认档必须是标准（48）；含日期时间两行的行不低于宽松档；切换时表头和列宽不能跳。',
    kw: '密度 紧凑 宽松 行高 density compact 间距 表格大小 row height 切换',
    wide: true,
    css: B('adtbl014', 0, `
.adtbl014 .a-card{--rh:48px}
.adtbl014 .a-card.s{--rh:40px}.adtbl014 .a-card.l{--rh:56px}
.adtbl014 td{height:var(--rh);transition:height .2s cubic-bezier(.2,0,0,1)}
.adtbl014 .a-card.s th{height:40px}.adtbl014 .a-card.l th{height:48px}
.adtbl014 .a-card.s .a-nm b{line-height:18px}.adtbl014 .a-card.s .a-nm small{display:none}`),
    html: () => `<div class="adtbl014"><div class="a-card"><div class="a-tb"><span class="a-ht">共 8 条</span><span class="sp"></span><div class="a-seg" role="group" aria-label="行高密度"><button type="button" data-d="s">紧凑</button><button type="button" data-d="m" class="on">默认</button><button type="button" data-d="l">宽松</button></div></div>
<div class="a-tw"><table style="min-width:${sumw(W)}px">${cg(W)}
<thead><tr><th>客户</th><th>商品</th><th>金额（元）</th><th>状态</th><th>下单时间</th></tr></thead>
<tbody>${ROWS.slice(0, 8).map((r) => `<tr><td class="l">${nm(r)}</td><td class="l" title="${r.item}">${r.item}</td><td class="r">${money(r.amt)}</td><td>${stTag(r)}</td><td class="n">${r.date}</td></tr>`).join('')}</tbody></table></div></div></div>`,
    js: (root) => {
      const card = root.querySelector('.a-card')
      const set = (d, save) => { card.classList.toggle('s', d === 's'); card.classList.toggle('l', d === 'l'); root.querySelectorAll('[data-d]').forEach((b) => b.classList.toggle('on', b.dataset.d === d)); if (save) try { localStorage.setItem(KEY, d) } catch (e) {} }
      root.addEventListener('click', (e) => { const b = e.target.closest('[data-d]'); if (b) set(b.dataset.d, true) })
      let d = 'm'; try { d = localStorage.getItem(KEY) || 'm' } catch (e) {} set(['s', 'm', 'l'].includes(d) ? d : 'm')
    },
  })
}

/* AD-TBL-015 表格工具栏 */
{
  const COLS = [['who', '客户', 200], ['item', '商品', 0], ['q', '数量', 80], ['amt', '金额（元）', 128], ['st', '状态', 112], ['pay', '支付方式', 120], ['city', '收货城市', 100], ['at', '下单时间', 160]]
  const DEF = ['who', 'item', 'q', 'amt', 'st', 'at']
  const R15 = ROWS.slice(0, 8)
  const cellOf = (k, r) => ({ who: `<td class="l" data-c="who">${nm(r)}</td>`, item: `<td class="l" data-c="item" title="${r.item}">${r.item}</td>`, q: `<td class="n" data-c="q">${r.q}</td>`, amt: `<td class="r" data-c="amt">${money(r.amt)}</td>`, st: `<td data-c="st">${stTag(r)}</td>`, pay: `<td data-c="pay">${r.pay}</td>`, city: `<td data-c="city">${r.city}</td>`, at: `<td class="n" data-c="at">${r.date}</td>` })[k]
  def({
    id: 'AD-TBL-015', name: '表格工具栏', style: '刷新·列设置',
    fit: '表格右上角的一组工具：搜索即输即查、刷新（带加载与更新时间）、行高密度、列设置（显示/隐藏列、恢复默认）、导出（范围等于当前筛选）。',
    avoid: '勾选列、对象名列、操作列不可隐藏；导出按钮写清范围和条数，不再让用户重选条件；工具别超过 5 个，多了收进“更多”。',
    kw: '工具栏 toolbar 列设置 列显隐 刷新 导出 密度 搜索 表格设置 columns refresh export',
    wide: true,
    css: B('adtbl015', 0, `
.adtbl015 .a-card{overflow:visible}
.adtbl015 .a-tb{gap:8px}
.adtbl015 .a-tb .ud{margin-right:4px}
.adtbl015 .spin svg{animation:adtSpin .8s linear infinite}
.adtbl015 .a-pop{position:absolute;right:16px;top:calc(100% - 6px);z-index:20;width:220px;padding:6px;border:1px solid var(--line);border-radius:12px;background:var(--card);box-shadow:0 8px 24px var(--sh14);animation:adtIn .18s cubic-bezier(.2,0,0,1)}
.adtbl015 .a-opt{display:flex;align-items:center;gap:10px;height:36px;padding:0 10px;border-radius:8px;cursor:pointer;text-align:left}
.adtbl015 .a-opt:hover{background:var(--n3)}
.adtbl015 .a-opt.lock{cursor:not-allowed;color:var(--ink3)}
.adtbl015 .a-opt.lock .a-ck{opacity:.5}
.adtbl015 .a-opt small{margin-left:auto;font-size:12px;color:var(--ink3)}
.adtbl015 .a-pop .ft{display:flex;justify-content:space-between;align-items:center;margin-top:4px;padding:6px 6px 2px;border-top:1px solid var(--line)}
.adtbl015 .a-sl{position:absolute;left:0;right:0;top:44px;bottom:0;z-index:5;display:none;background:var(--glass0)}
.adtbl015 .a-card.ld .a-sl{display:block}
.adtbl015 .a-card.ld tbody{opacity:.5}
.adtbl015 .a-dd .menu{left:auto;right:0}
.adtbl015 .a-card.s td{height:40px}.adtbl015 .a-card.l td{height:56px}
.adtbl015 .a-card th:first-child{border-top-left-radius:11px}.adtbl015 .a-card th:last-child{border-top-right-radius:11px}`),
    html: () => `<div class="adtbl015"><div class="a-card"><div class="a-tb"><label class="a-sb" style="width:240px">${svb('search')}<input type="search" placeholder="搜索客户、订单号、商品" aria-label="搜索订单"></label><span class="sp"></span><span class="a-ht ud" data-upd>更新于 刚刚</span>
<button class="a-ib" type="button" data-act="reload" aria-label="刷新" title="刷新">${svb('refresh')}</button>
<div class="a-dd" data-ix="dd" data-key="den"><button class="a-ib" data-tg type="button" aria-label="行高密度" title="行高密度" aria-haspopup="listbox">${svb('menu')}</button><div class="menu" role="listbox"><div data-o data-v="紧凑" data-val="s">紧凑</div><div data-o data-v="默认" data-val="m" class="on">默认</div><div data-o data-v="宽松" data-val="l">宽松</div></div></div>
<button class="a-ib" type="button" data-act="cols" aria-label="列设置" title="列设置" aria-haspopup="true">${svb('adt_cols')}</button>
<button class="a-b" type="button" data-act="exp">${svb('download')}<span>导出（共 8 条）</span></button>
<div class="a-pop" hidden role="dialog" aria-label="列设置"><div class="a-opt lock">${ck('', '客户', true)}<span>客户</span><small>不可隐藏</small></div>${COLS.slice(1).map(([k, t]) => `<div class="a-opt" data-k="${k}">${ck('', t, DEF.includes(k))}<span>${t.replace('（元）', '')}</span></div>`).join('')}<div class="ft"><button class="a-lk" type="button" data-act="reset">恢复默认</button><span class="a-ht">按用户保存</span></div></div></div>
<div class="a-tw" style="position:relative"><table style="min-width:${sumw(COLS.map((c) => c[2]))}px" data-pagination="none">${cg(COLS.map((c) => c[2]))}
<thead><tr>${COLS.map(([k, t]) => `<th data-c="${k}"${DEF.includes(k) ? '' : ' hidden'}>${t}</th>`).join('')}</tr></thead>
<tbody>${R15.map((r) => `<tr>${COLS.map(([k]) => cellOf(k, r).replace('<td', `<td${DEF.includes(k) ? '' : ' hidden'}`)).join('')}</tr>`).join('')}</tbody></table></div>
<div class="a-sl"></div>
<div class="a-pg"><span data-total>共 8 条</span></div></div></div>`,
    js: (root) => {
      const $ = (s) => root.querySelector(s), $$ = (s) => [...root.querySelectorAll(s)]
      const card = $('.a-card'), pop = $('.a-pop'), cols = $('table colgroup')
      const vis = new Set(DEF)
      const sync = () => {
        $$('[data-c]').forEach((c) => { c.hidden = !vis.has(c.dataset.c) })
        ;[...cols.children].forEach((c, i) => { c.hidden = !vis.has(COLS[i][0]) })
        $$('.a-opt[data-k]').forEach((o) => o.querySelector('.a-ck').classList.toggle('on', vis.has(o.dataset.k)))
        const w = COLS.filter((c) => vis.has(c[0])).map((c) => c[2]); $('table').style.minWidth = w.reduce((a, x) => a + (x || 220), 0) + 'px'
      }
      const count = () => {
        const q = $('input').value.trim().toLowerCase(); let n = 0
        $$('tbody tr').forEach((r) => { const ok = !q || r.textContent.toLowerCase().includes(q); r.hidden = !ok; if (ok) n++ })
        $('[data-total]').textContent = `共 ${n} 条`; $('[data-act=exp] span').textContent = `导出（共 ${n} 条）`
      }
      $('input').addEventListener('input', count)
      root.addEventListener('click', (e) => {
        const a = e.target.closest('[data-act]'), o = e.target.closest('.a-opt[data-k]'), d = e.target.closest('.menu [data-o]')
        if (d) { card.classList.toggle('s', d.dataset.val === 's'); card.classList.toggle('l', d.dataset.val === 'l') }
        if (o) { const k = o.dataset.k; vis.has(k) ? vis.delete(k) : vis.add(k); sync() }
        if (!a) return
        const act = a.dataset.act
        if (act === 'cols') pop.hidden = !pop.hidden
        if (act === 'reset') { vis.clear(); DEF.forEach((k) => vis.add(k)); sync() }
        if (act === 'exp') IX.toast(root, `已开始导出当前筛选的 ${$$('tbody tr:not([hidden])').length} 条，完成后在消息中心通知`)
        if (act === 'reload') { a.classList.add('spin'); card.classList.add('ld'); setTimeout(() => { a.classList.remove('spin'); card.classList.remove('ld'); $('[data-upd]').textContent = '更新于 刚刚'; IX.toast(root, '已刷新') }, 800) }
      })
      const off = (e) => { if (!root.isConnected) return document.removeEventListener('click', off); if (!pop.hidden && !e.target.closest('.a-pop,[data-act=cols]')) pop.hidden = true }
      document.addEventListener('click', off); sync()
    },
  })
}

/* AD-TBL-016 空表与加载骨架 */
{
  const W = [200, 0, 128, 112, 160]
  const SK = [[120, 70], [160, 54], [140, 80], [150, 60], [110, 90], [170, 50]]
  const body = (st) => {
    if (st === 'ok') return ROWS.slice(0, 6).map((r) => `<tr><td class="l">${nm(r)}</td><td class="l" title="${r.item}">${r.item}</td><td class="r">${money(r.amt)}</td><td>${stTag(r)}</td><td class="n">${r.date}</td></tr>`).join('')
    if (st === 'load') return SK.map(([a, b]) => `<tr><td class="l"><span class="a-sk" style="width:${a * 0.8}px;margin-bottom:6px"></span><span class="a-sk" style="width:${a * 0.55}px;height:10px"></span></td><td class="l"><span class="a-sk" style="width:${a}px"></span></td><td class="r"><span class="a-sk" style="width:64px;margin-left:auto"></span></td><td><span class="a-sk" style="width:60px;margin:0 auto;height:22px;border-radius:4px"></span></td><td><span class="a-sk" style="width:${b + 30}px;margin:0 auto"></span></td></tr>`).join('')
    const M = { empty: ['adt_inbox', '还没有订单', '有新订单时会第一时间出现在这里', '新建订单', 'go'], none: ['search', '没有符合条件的订单', '试试放宽筛选条件，或清除后重新查看', '清除筛选', 'ok'], fail: ['alert', '订单加载失败', '网络连接超时，请检查网络后重试（请求编号 a3f9c2）', '重试', 'retry'] }[st]
    return `<tr class="stt"><td colspan="5"><div class="em"><span class="i">${sv(M[0])}</span><b>${M[1]}</b><span>${M[2]}</span><button class="a-b${st === 'fail' ? ' p' : ''}" type="button" data-to="${M[4]}">${M[3]}</button></div></td></tr>`
  }
  def({
    id: 'AD-TBL-016', name: '空表与加载骨架', style: '四种状态',
    fit: '表格的四种非正常状态一次定好：加载用骨架（保留表头与列宽）、没有数据给一句话加一个行动、筛选无结果给“清除筛选”、加载失败写原因并给“重试”。',
    avoid: '加载时不要整页转圈把表头也盖住；失败态要写原因和请求编号；空态别只放一张图，没有行动入口。',
    kw: '空状态 empty 骨架屏 skeleton 加载 loading 失败 重试 无数据 无结果 error 状态',
    wide: true,
    css: B('adtbl016', 0, `
.adtbl016 tr.stt td{height:300px;background:var(--card);white-space:normal}
.adtbl016 tr.stt:hover>td{background:var(--card)}
.adtbl016 .em{display:flex;flex-direction:column;align-items:center;gap:6px;color:var(--ink2)}
.adtbl016 .em b{font-size:16px;line-height:24px;font-weight:600;color:var(--ink)}
.adtbl016 .em .i{display:flex;align-items:center;justify-content:center;width:64px;height:64px;margin-bottom:6px;border-radius:50%;background:var(--soft);color:var(--ink4)}
.adtbl016 .em .i svg{width:28px;height:28px}
.adtbl016 .em .a-b{margin-top:10px}
.adtbl016 .a-card.fail .em .i{background:var(--danger-bg);color:var(--danger)}
.adtbl016 .a-tb{justify-content:space-between}`),
    html: () => `<div class="adtbl016"><div class="a-card"><div class="a-tb"><div class="a-seg" role="group" aria-label="切换演示状态"><button type="button" data-s="ok" class="on">正常</button><button type="button" data-s="load">加载中</button><button type="button" data-s="empty">暂无数据</button><button type="button" data-s="none">无匹配结果</button><button type="button" data-s="fail">加载失败</button></div><span class="a-ht" data-ht>共 6 条</span></div>
<div class="a-tw"><table style="min-width:${sumw(W)}px" aria-live="polite">${cg(W)}<thead><tr><th>客户</th><th>商品</th><th>金额（元）</th><th>状态</th><th>下单时间</th></tr></thead><tbody>${body('ok')}</tbody></table></div></div></div>`,
    js: (root) => {
      const card = root.querySelector('.a-card'), tb = root.querySelector('tbody'); let t
      const show = (st) => {
        clearTimeout(t); tb.innerHTML = body(st); card.classList.toggle('fail', st === 'fail')
        root.querySelectorAll('[data-s]').forEach((b) => b.classList.toggle('on', b.dataset.s === st))
        root.querySelector('[data-ht]').textContent = { ok: '共 6 条', load: '加载中…', empty: '共 0 条', none: '共 0 条', fail: '加载失败' }[st]
      }
      root.addEventListener('click', (e) => {
        const b = e.target.closest('[data-s]'); if (b) return show(b.dataset.s)
        const x = e.target.closest('[data-to]'); if (!x) return
        if (x.dataset.to === 'retry') { show('load'); t = setTimeout(() => show('ok'), 1000) }
        if (x.dataset.to === 'ok') show('ok')
        if (x.dataset.to === 'go') IX.toast(root, '打开新建订单面板')
      })
    },
  })
}

/* AD-TBL-017 主从表 */
{
  const W = [200, 0, 128, 112]
  const R17 = ROWS.slice(0, 7)
  const STEP = ['已下单', '已支付', '已发货', '已签收']
  const reach = (r) => ({ 待付款: 1, 待发货: 2, 配送中: 3, 已完成: 4, 已取消: 1, 退款中: 3 })[r.st]
  const when = (r, k) => { const d = new Date(r.ts + k * 5.5 * 3600000); return `${pad(d.getMonth() + 1)}-${pad(d.getDate())} ${pad(d.getHours())}:${pad(d.getMinutes())}` }
  const detail = (r) => { const s = SKUS[r.i % 9], n = reach(r); return `<div class="dh"><b>${r.who}</b><span class="no">${r.no}</span>${stTag(r)}<span class="sp"></span><span class="a-ht">${r.date}</span></div>
<div class="dg"><div class="c"><h5>收货信息</h5><p>${r.who} · ${r.phone}</p><p class="ad" title="${r.addr}">${r.addr}</p><p>${r.pay}</p></div>
<div class="c"><h5>商品明细</h5><div class="it"><img class="a-th" src="${P(s[2])}" alt=""><div class="a-nm"><b>${s[0]}</b><small>${money(s[1])} × ${r.q}</small></div><b class="am">${money(r.amt)}</b></div><p class="a-ht" style="margin-top:8px">运费 0.00 元，优惠 0.00 元</p></div>
<div class="c"><h5>物流进度</h5><ol class="a-tl">${STEP.map((t, k) => `<li class="${k < n ? 'done' : ''}${k === n - 1 ? ' cur' : ''}"><i></i><span>${t}</span><small>${k < n ? when(r, k) : '—'}</small></li>`).join('')}${r.st === '已取消' ? '<li class="done bad cur"><i></i><span>已取消</span><small>' + when(r, 1) + '</small></li>' : r.st === '退款中' ? '<li class="done bad cur"><i></i><span>退款处理中</span><small>' + when(r, 3) + '</small></li>' : ''}</ol></div></div>` }
  def({
    id: 'AD-TBL-017', name: '主从表', style: '点行看详情',
    fit: '需要一边浏览列表、一边看单条详情的场景（客服查订单、仓库对单）：点一行，下方同步显示收货、商品、物流；不跳页、不遮住列表。',
    avoid: '详情内容很多或要编辑时用居中悬浮面板（AD-TBL-004）；手机上主从上下排，别左右并排；当前行要有明确的高亮。',
    kw: '主从 master detail 详情 联动 点行 预览 行选中 订单详情 split 上下联动',
    wide: true,
    css: B('adtbl017', 0, `
.adtbl017 tbody tr{cursor:pointer}
.adtbl017 tbody tr.cur>td{background:var(--pt)}
.adtbl017 tbody tr.cur>td:first-child{box-shadow:inset 3px 0 0 var(--p)}
.adtbl017 .pane{padding:18px 20px 22px;border-top:1px solid var(--line);background:var(--n1);animation:adtFade .2s}
.adtbl017 .dh{display:flex;align-items:center;gap:12px;flex-wrap:wrap;margin-bottom:14px}
.adtbl017 .dh b{font-size:16px;font-weight:600}
.adtbl017 .dh .no{color:var(--ink3);font-variant-numeric:tabular-nums}
.adtbl017 .dh .sp{flex:1}
.adtbl017 .dg{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:16px}
.adtbl017 .c{padding:14px 16px;border:1px solid var(--line);border-radius:12px;background:var(--card);min-width:0}
.adtbl017 .c h5{margin:0 0 8px;font-size:14px;font-weight:600;color:var(--ink2)}
.adtbl017 .c p{margin:0 0 4px;overflow:hidden;text-overflow:ellipsis;display:-webkit-box;-webkit-line-clamp:2;-webkit-box-orient:vertical}
.adtbl017 .it{display:flex;align-items:center;gap:10px}
.adtbl017 .it .a-nm{flex:1}
.adtbl017 .it .am{font-weight:600;font-variant-numeric:tabular-nums}
.adtbl017 .a-tl{margin:0;padding:0;list-style:none}
.adtbl017 .a-tl li{position:relative;display:flex;align-items:baseline;gap:8px;padding:0 0 10px 20px;color:var(--ink3)}
.adtbl017 .a-tl li::before{content:"";position:absolute;left:4px;top:12px;bottom:-2px;width:1px;background:var(--line)}
.adtbl017 .a-tl li:last-child{padding-bottom:0}.adtbl017 .a-tl li:last-child::before{display:none}
.adtbl017 .a-tl li i{position:absolute;left:0;top:7px;width:9px;height:9px;border-radius:50%;background:var(--n8)}
.adtbl017 .a-tl li.done{color:var(--ink)}.adtbl017 .a-tl li.done i{background:var(--p)}.adtbl017 .a-tl li.bad i{background:var(--danger-fill)}.adtbl017 .a-tl li.bad span{color:var(--danger)}
.adtbl017 .a-tl small{margin-left:auto;font-size:12px;color:var(--ink3)}
@media(max-width:900px){.adtbl017 .dg{grid-template-columns:1fr}}`),
    html: () => `<div class="adtbl017"><div class="a-card"><div class="a-tw"><table style="min-width:${sumw(W)}px" data-pagination="none">${cg(W)}<thead><tr><th>客户</th><th>商品</th><th>金额（元）</th><th>状态</th></tr></thead>
<tbody>${R17.map((r, k) => `<tr data-i="${r.i}" tabindex="0" class="${k === 0 ? 'cur' : ''}"><td class="l">${nm(r)}</td><td class="l" title="${r.item}">${r.item}</td><td class="r">${money(r.amt)}</td><td>${stTag(r)}</td></tr>`).join('')}</tbody></table></div>
<div class="pane" aria-live="polite">${detail(R17[0])}</div></div></div>`,
    js: (root) => {
      const pick = (tr) => { root.querySelectorAll('tbody tr').forEach((x) => x.classList.toggle('cur', x === tr)); const p = root.querySelector('.pane'); p.innerHTML = detail(ROWS[+tr.dataset.i]); p.style.animation = 'none'; void p.offsetWidth; p.style.animation = '' }
      root.addEventListener('click', (e) => { const tr = e.target.closest('tbody tr'); if (tr) pick(tr) })
      root.addEventListener('keydown', (e) => {
        const tr = e.target.closest && e.target.closest('tbody tr'); if (!tr) return
        if (e.key === 'Enter' || e.key === ' ') { e.preventDefault(); pick(tr) }
        if (e.key === 'ArrowDown' && tr.nextElementSibling) { e.preventDefault(); tr.nextElementSibling.focus(); pick(tr.nextElementSibling) }
        if (e.key === 'ArrowUp' && tr.previousElementSibling) { e.preventDefault(); tr.previousElementSibling.focus(); pick(tr.previousElementSibling) }
      })
    },
  })
}

/* AD-TBL-018 拖拽排序行 */
{
  const W = [48, 64, 0, 130, 150, 110]
  const BN = [['春季上新 · 全场 8 折', 1, '首页顶部', '11-01 至 11-30', 'ok'], ['会员日 · 积分翻倍', 4, '首页顶部', '每月 8 日', 'ok'], ['新人礼包 · 首单立减 20 元', 0, '首页中部', '长期有效', 'ok'], ['满 199 减 30', 2, '首页中部', '11-04 至 11-11', 'ok'], ['品牌故事 · 手作的温度', 3, '内容页', '长期有效', 'ok'], ['周年庆预热（较长的文案用来测试省略效果，仅作演示请勿用于正式环境）', 6, '首页顶部', '11-20 至 12-05', 'warn'], ['清仓专区', 8, '分类页', '11-04 至 11-15', 'mu']]
  const ST = { ok: '展示中', warn: '未开始', mu: '已暂停' }
  def({
    id: 'AD-TBL-018', name: '拖拽排序行', style: '手柄拖动',
    fit: '运营内容的展示顺序（横幅、分类、套餐、菜单）：左侧手柄按住拖动换位，序号实时重排，松手即生效并轻提示；手柄聚焦时可用上下方向键调整。',
    avoid: '行数很多（超过 30 行）时拖不动，要提供“置顶/移到第 N 位”；排序影响前台展示，要在提示里写清；不要整行都可拖，会和点击冲突。',
    kw: '拖拽 排序 drag sort 手柄 调整顺序 横幅排序 运营位 reorder sortable 拖动',
    wide: true,
    css: B('adtbl018', 0, `
.adtbl018 .a-gp{display:inline-flex;align-items:center;justify-content:center;width:32px;height:32px;border-radius:8px;color:var(--ink3);cursor:grab;touch-action:none;transition:background-color .15s,color .15s}
.adtbl018 .a-gp:hover,.adtbl018 .a-gp:focus-visible{background:var(--soft);color:var(--ink)}
.adtbl018 .a-gp span{display:inline-flex;width:18px;height:18px}
.adtbl018 .a-card.dragging{user-select:none}.adtbl018 .a-card.dragging .a-gp{cursor:grabbing}
.adtbl018 tr.dg>td{background:var(--pt);box-shadow:0 8px 16px -8px var(--sh25);position:relative;z-index:1}
.adtbl018 .no{font-variant-numeric:tabular-nums;color:var(--ink2)}
.adtbl018 .a-pg{justify-content:space-between}`),
    html: () => `<div class="adtbl018"><div class="a-card"><div class="a-tw"><table style="min-width:${sumw(W)}px" data-pagination="none">${cg(W)}<thead><tr><th></th><th>排序</th><th>横幅</th><th>展示位置</th><th>有效期</th><th>状态</th></tr></thead>
<tbody>${BN.map((b, k) => `<tr data-t="${b[0].split('（')[0]}"><td class="k"><button class="a-gp" type="button" aria-label="拖动调整顺序，或按上下方向键">${svb('drag', 'a-i20')}</button></td><td class="no n">${k + 1}</td><td class="l"><div class="a-av"><img class="a-th" src="${P(b[1])}" alt="" style="width:56px;height:32px"><span title="${b[0]}" style="min-width:0;overflow:hidden;text-overflow:ellipsis">${b[0]}</span></div></td><td>${b[2]}</td><td class="n">${b[3]}</td><td>${tag(b[4], ST[b[4]])}</td></tr>`).join('')}</tbody></table></div>
<div class="a-pg"><span>共 ${BN.length} 张，顺序实时同步到小程序首页</span></div></div></div>`,
    js: (root) => {
      const tb = root.querySelector('tbody'), card = root.querySelector('.a-card')
      const rows = () => [...tb.rows], renum = () => rows().forEach((r, i) => (r.querySelector('.no').textContent = i + 1))
      const flip = (fn) => {
        const was = new Map(rows().map((r) => [r, r.getBoundingClientRect().top])); fn()
        rows().forEach((r) => { const d = was.get(r) - r.getBoundingClientRect().top; if (d && !r.classList.contains('dg')) { r.style.transition = 'none'; r.style.transform = `translateY(${d}px)`; requestAnimationFrame(() => { r.style.transition = 'transform .18s cubic-bezier(.2,0,0,1)'; r.style.transform = '' }) } })
      }
      const done = (row, from) => { renum(); const to = rows().indexOf(row); if (to !== from) IX.toast(root, `“${row.dataset.t}”已移到第 ${to + 1} 位`) }
      let drag = null
      root.addEventListener('pointerdown', (e) => {
        const h = e.target.closest('.a-gp'); if (!h || (e.pointerType === 'mouse' && e.button !== 0)) return
        e.preventDefault(); const row = h.closest('tr'); drag = { row, from: rows().indexOf(row) }; row.classList.add('dg'); card.classList.add('dragging')
        const move = (ev) => {
          const y = ev.clientY
          for (const r of rows()) {
            if (r === row) continue
            const b = r.getBoundingClientRect()
            if (y >= b.top && y <= b.bottom) { const ref = y < b.top + b.height / 2 ? r : r.nextSibling; if (ref !== row && ref !== row.nextSibling) flip(() => tb.insertBefore(row, ref)); break }
          }
        }
        const up = () => { document.removeEventListener('pointermove', move); document.removeEventListener('pointerup', up); document.removeEventListener('pointercancel', up); row.classList.remove('dg'); card.classList.remove('dragging'); done(row, drag.from); drag = null }
        document.addEventListener('pointermove', move); document.addEventListener('pointerup', up); document.addEventListener('pointercancel', up)
      })
      root.addEventListener('keydown', (e) => {
        const h = e.target.closest && e.target.closest('.a-gp'); if (!h || (e.key !== 'ArrowUp' && e.key !== 'ArrowDown')) return
        e.preventDefault(); const row = h.closest('tr'), from = rows().indexOf(row)
        const ref = e.key === 'ArrowUp' ? row.previousElementSibling : row.nextElementSibling && row.nextElementSibling.nextSibling
        if (e.key === 'ArrowUp' ? !row.previousElementSibling : !row.nextElementSibling) return
        flip(() => tb.insertBefore(row, ref)); h.focus(); done(row, from)
      })
    },
  })
}

guide('ad', 'TBL', [
  ['普通数据列表（订单、会员、商品）', '基础数据表 / 分页器 / 状态列与表头筛选', '第一列放人能看懂的标识，点表头排序；超过一页就接分页（默认 20 条）；枚举列用表头漏斗筛选'],
  ['要对多行一起处理（发货、导出、删除）', '勾选与批量操作', '批量栏替换工具栏同一位置，不推开表格；删除类动作用居中面板二次确认'],
  ['行上的操作和小改动', '行内操作与更多 / 行内开关 / 行内编辑', '常用两个外露、其余进“更多”；可逆状态用开关直接生效；改价改库存双击就改，复杂改动才开面板'],
  ['一行下面有明细，或数据有层级要归类', '可展开行 / 树形表格 / 分组表', '明细用展开行，分类和部门用树形表格，按门店日期归类用分组表，别互相替代'],
  ['列多行多的大表，还要看合计', '固定表头与固定列 / 汇总行', '表头吸顶、勾选与名称列冻结左侧、操作列冻结右侧，容器内滚动；合计行与已选合计共用一行'],
  ['让用户自己调表格', '表格工具栏 / 密度切换', '搜索、刷新、密度、列设置、导出放右上角；设置按用户保存，勾选、名称、操作列不可隐藏'],
  ['名单、边看边查、调顺序、空与失败', '人员表 / 主从表 / 拖拽排序行 / 空表与加载骨架', '成员用动物头像；详情不跳页；运营顺序手柄拖动；加载用骨架，空态一句话加一个行动，失败写原因与重试'],
])

/* ================================================================
 * FLT 筛选与搜索
 * 共用：FD（60 条示例订单）、STS6（状态的处理顺序）、fmtRow/emptyTr/emptyCss（结果表）、bindF（输入与下拉绑定）
 * 原则（规则卡）：即输即查，不放“查询”按钮；外露最多 4 个，其余收进“更多筛选”；已生效条件以可移除标签显示并可清空；
 * 下拉选项带数量，数量为 0 的弱化并排最后；时间的快捷范围与自定义日期合并为一个控件。
 * ================================================================ */
const FD = BIG(60)
const STS6 = ['待发货', '退款中', '待付款', '配送中', '已完成', '已取消']
const fmtRow = (r) => `<tr><td class="l">${nm(r)}</td><td class="l" title="${r.item}">${r.item}</td><td class="r">${money(r.amt)}</td><td>${stTag(r)}</td><td class="n">${r.date}</td></tr>`
const fmtRowS = (r) => `<tr><td class="l">${nm(r)}</td><td class="l" title="${r.item}">${r.item}</td><td class="r">${money(r.amt)}</td><td>${stTag(r)}</td></tr>`
const emptyTr = (n, msg = '没有符合条件的订单', btn = '清除筛选') => `<tr class="empty"><td colspan="${n}"><div class="em"><span class="i">${sv('search')}</span><b>${msg}</b><button class="a-lk" type="button" data-clear>${btn}</button></div></td></tr>`
const emptyCss = (p) => `.${p} tr.empty td{height:176px;background:var(--card);white-space:normal}.${p} tr.empty:hover>td{background:var(--card)}.${p} .em{display:flex;flex-direction:column;align-items:center;gap:4px;color:var(--ink2)}.${p} .em b{font-weight:600;color:var(--ink)}.${p} .em .i{display:flex;width:36px;height:36px;margin-bottom:4px;color:var(--ink6)}`
const FBAR = (p) => `.${p} .a-fbar{display:flex;flex-wrap:wrap;align-items:center;gap:8px;padding:12px 16px}.${p} .a-fbar .sp{flex:1}`
const bindF = (root, s, render) => {
  root.addEventListener('input', (e) => { if (e.target.matches('[data-q]')) { s.q = e.target.value; render() } })
  root.addEventListener('click', (e) => { const o = e.target.closest('.menu [data-o]'); if (o) { s[o.closest('.a-dd').dataset.key] = o.dataset.val; render() } })
}
const markHas = (root, s) => root.querySelectorAll('.a-dd[data-key]').forEach((d) => d.querySelector('.a-sel').classList.toggle('has', s[d.dataset.key] !== 'all' && s[d.dataset.key] !== undefined))
const matchQ = (r, q) => !q || (r.who + r.no + r.item).toLowerCase().includes(q.trim().toLowerCase())
const DAYS = [['all', '全部时间', undefined, '下单时间'], ['1', '今天'], ['7', '近 7 天'], ['30', '近 30 天']]
const inDays = (r, d) => d === 'all' || r.ago < +d
const CITY_O = [['all', '全部', undefined, '收货城市'], ...CITIES.map((c) => [c, c])]
const PAY_O = [['all', '全部', undefined, '支付方式'], ...['微信支付', '支付宝', '余额支付', '银行卡'].map((c) => [c, c])]
const searchBox = (ph, w = 240) => `<label class="a-sb" style="width:${w}px;max-width:100%">${svb('search')}<input type="search" data-q placeholder="${ph}" aria-label="${ph}"></label>`
const stOptions = (rowsFn, s, key = 'st', allLabel = '状态') => [['all', '全部', rowsFn({ ...s, [key]: 'all' }).length, allLabel], ...STS6.map((x) => [x, x, rowsFn({ ...s, [key]: x }).length])].sort((a, b) => (a[2] === 0) - (b[2] === 0) || 0)

/* AD-FLT-001 行内筛选栏 */
{
  const W = [200, 0, 128, 112, 160]
  const DEF = { q: '', st: '待发货', days: '30', city: 'all' }
  const run = (s) => FD.filter((r) => matchQ(r, s.q) && (s.st === 'all' || r.st === s.st) && inDays(r, s.days) && (s.city === 'all' || r.city === s.city))
  const bar = (s) => `<div class="a-fbar">${searchBox('搜索客户、订单号、商品', 260)}${dd('st', stOptions(run, s), s.st)}${dd('days', DAYS, s.days)}${dd('city', CITY_O, s.city)}<button class="a-b g" type="button" data-reset hidden>重置</button></div>`
  def({
    id: 'AD-FLT-001', name: '行内筛选栏', style: '即输即查',
    fit: '列表页顶部的常用筛选：搜索框加 2–3 个最常用条件（状态、时间、城市），输入或选择即刻刷新结果，不放“查询”按钮；默认值是“待发货”这类最需要处理的子集。',
    avoid: '外露超过 4 个就把低频的收进“更多筛选”（AD-FLT-002）；搜索、筛选旁不放说明文字和字段标签；状态选项要带数量，数量为 0 的弱化排后。',
    kw: '筛选 筛选栏 搜索 即输即查 状态筛选 日期筛选 重置 filter bar 条件 查询',
    wide: true,
    css: B('adflt001', 0, FBAR('adflt001') + emptyCss('adflt001') + '.adflt001 .a-card{overflow:visible}'),
    html: () => `<div class="adflt001"><div class="a-card ov"><div data-bar>${bar(DEF)}</div><div class="a-tw"><table style="min-width:${sumw(W)}px" data-pagination="none">${cg(W)}<thead><tr><th>客户</th><th>商品</th><th>金额（元）</th><th>状态</th><th>下单时间</th></tr></thead><tbody>${run(DEF).slice(0, 8).map(fmtRow).join('')}</tbody></table></div><div class="a-pg"><span data-total>共 ${run(DEF).length} 条</span></div></div></div>`,
    js: (root) => {
      const $ = (s) => root.querySelector(s); const s = { ...DEF }
      const render = () => {
        const rs = run(s)
        $('tbody').innerHTML = rs.length ? rs.slice(0, 8).map(fmtRow).join('') : emptyTr(5)
        $('[data-total]').textContent = `共 ${rs.length} 条` + (rs.length > 8 ? '，显示前 8 条' : '')
        fillDD(root, 'st', stOptions(run, s), s.st)
        markHas(root, s); $('[data-reset]').hidden = JSON.stringify(s) === JSON.stringify(DEF)
      }
      bindF(root, s, render)
      root.addEventListener('click', (e) => {
        if (e.target.closest('[data-reset],[data-clear]')) {
          Object.assign(s, DEF); $('[data-q]').value = ''
          const set = (k, t) => { const d = $(`.a-dd[data-key=${k}]`); d.querySelector('[data-label]').textContent = t; d.querySelectorAll('[data-o]').forEach((o) => o.classList.toggle('on', o.dataset.val === s[k])) }
          set('st', '待发货'); set('days', '近 30 天'); set('city', '收货城市'); render()
        }
      })
      render()
    },
  })
}

/* AD-FLT-002 高级筛选（更多筛选） */
{
  const W = [200, 0, 128, 112, 160]
  const DEF = { q: '', st: 'all', days: '30', pay: 'all', city: 'all', sku: 'all', min: '', max: '' }
  const SKU_O = [['all', '全部', undefined, '商品'], ...SKUS.slice(0, 6).map((x) => [x[0], x[0]])]
  const run = (s) => FD.filter((r) => matchQ(r, s.q) && (s.st === 'all' || r.st === s.st) && inDays(r, s.days) && (s.pay === 'all' || r.pay === s.pay) && (s.city === 'all' || r.city === s.city) && (s.sku === 'all' || r.sku === s.sku) && (!s.min || r.amt >= +s.min) && (!s.max || r.amt <= +s.max))
  def({
    id: 'AD-FLT-002', name: '高级筛选', style: '更多筛选',
    fit: '筛选条件超过 4 个时：顶部只露搜索、状态、时间三项，其余（支付方式、城市、商品、金额区间）收进“更多筛选”，展开后即选即查；按钮上的角标告诉用户收起的条件里已生效几项。',
    avoid: '不要把所有条件平铺成一排下拉；收起时有生效条件必须有提示（角标），否则用户不知道结果为什么少；展开和收起不能推动页面其他内容乱跳。',
    kw: '高级筛选 更多筛选 展开 收起 多条件 筛选面板 金额区间 条件角标 advanced filter',
    wide: true,
    css: B('adflt002', 0, FBAR('adflt002') + emptyCss('adflt002') + `
.adflt002 .a-b em{min-width:18px;height:18px;padding:0 5px;border-radius:9px;background:var(--p);color:#fff;font-size:12px;line-height:18px;font-weight:600;text-align:center}
.adflt002 .a-b.on{border-color:var(--pm);background:var(--pt);color:var(--p-text)}
.adflt002 .a-b svg{transition:transform .2s cubic-bezier(.2,0,0,1)}.adflt002 .a-b.on svg{transform:rotate(180deg)}
.adflt002 .a-more{display:grid;grid-template-rows:0fr;transition:grid-template-rows .25s cubic-bezier(.2,0,0,1);background:var(--n1)}
.adflt002 .a-more>div{overflow:hidden}
.adflt002 .a-more.open{grid-template-rows:1fr}.adflt002 .a-more.open.done>div{overflow:visible}
.adflt002 .a-mg{display:flex;flex-wrap:wrap;align-items:center;gap:8px;padding:12px 16px;border-top:1px solid var(--line)}
.adflt002 .a-rg{display:inline-flex;align-items:center;gap:6px}.adflt002 .a-rg .a-in{width:104px}.adflt002 .a-rg i{color:var(--ink3)}`),
    html: () => `<div class="adflt002"><div class="a-card ov"><div class="a-fbar">${searchBox('搜索客户、订单号、商品', 260)}${dd('st', stOptions(run, DEF), DEF.st)}${dd('days', DAYS, DEF.days)}<button class="a-b" type="button" data-more aria-expanded="false">更多筛选<em hidden>0</em>${svb('down', 'a-i14')}</button><button class="a-b g" type="button" data-reset hidden>重置</button></div>
<div class="a-more"><div><div class="a-mg">${dd('pay', PAY_O, 'all')}${dd('city', CITY_O, 'all')}${dd('sku', SKU_O, 'all')}<span class="a-rg"><input class="a-in" data-n="min" inputmode="numeric" placeholder="金额下限" aria-label="金额下限"><i>—</i><input class="a-in" data-n="max" inputmode="numeric" placeholder="金额上限" aria-label="金额上限"></span></div></div></div>
<div class="a-tw"><table style="min-width:${sumw(W)}px" data-pagination="none">${cg(W)}<thead><tr><th>客户</th><th>商品</th><th>金额（元）</th><th>状态</th><th>下单时间</th></tr></thead><tbody>${run(DEF).slice(0, 6).map(fmtRow).join('')}</tbody></table></div><div class="a-pg"><span data-total>共 ${run(DEF).length} 条</span></div></div></div>`,
    js: (root) => {
      const $ = (s) => root.querySelector(s), $$ = (s) => [...root.querySelectorAll(s)]; const s = { ...DEF }
      const more = $('.a-more'), mb = $('[data-more]')
      const extra = () => ['pay', 'city', 'sku'].filter((k) => s[k] !== 'all').length + (s.min || s.max ? 1 : 0)
      const render = () => {
        const rs = run(s)
        $('tbody').innerHTML = rs.length ? rs.slice(0, 6).map(fmtRow).join('') : emptyTr(5)
        $('[data-total]').textContent = `共 ${rs.length} 条` + (rs.length > 6 ? '，显示前 6 条' : '')
        fillDD(root, 'st', stOptions(run, s), s.st)
        markHas(root, s)
        const n = extra(), em = mb.querySelector('em'); em.hidden = !n; em.textContent = n
        $('[data-reset]').hidden = JSON.stringify(s) === JSON.stringify(DEF)
      }
      bindF(root, s, render)
      root.addEventListener('input', (e) => { const k = e.target.dataset && e.target.dataset.n; if (k) { e.target.value = e.target.value.replace(/\D/g, ''); s[k] = e.target.value; render() } })
      root.addEventListener('click', (e) => {
        if (e.target.closest('[data-more]')) { const o = !more.classList.contains('open'); more.classList.toggle('open', o); mb.classList.toggle('on', o); mb.setAttribute('aria-expanded', o); if (!o) more.classList.remove('done') }
        if (e.target.closest('[data-reset],[data-clear]')) {
          Object.assign(s, DEF); $$('[data-q],[data-n]').forEach((i) => (i.value = ''))
          const lab = { st: '状态', days: '近 30 天', pay: '支付方式', city: '收货城市', sku: '商品' }
          Object.entries(lab).forEach(([k, t]) => { const d = $(`.a-dd[data-key=${k}]`); d.querySelector('[data-label]').textContent = t; d.querySelectorAll('[data-o]').forEach((o) => o.classList.toggle('on', o.dataset.val === s[k])) }); render()
        }
      })
      more.addEventListener('transitionend', (e) => { if (e.target === more && more.classList.contains('open')) more.classList.add('done') })
      render()
    },
  })
}

/* AD-FLT-003 搜索框与联想 */
{
  const W = [190, 0, 110, 100]
  const REC0 = ['林小满', '无线降噪耳机', 'SO20261105']
  const hl = (t, q) => { if (!q) return t; const i = t.toLowerCase().indexOf(q.toLowerCase()); return i < 0 ? t : `${t.slice(0, i)}<mark>${t.slice(i, i + q.length)}</mark>${t.slice(i + q.length)}` }
  const sug = (q) => {
    const k = q.trim().toLowerCase(); if (!k) return []
    const o = FD.filter((r) => (r.who + r.no).toLowerCase().includes(k)).slice(0, 3).map((r) => ({ g: '订单', v: r.who, a: hl(r.who, q.trim()), s: `${hl(r.no, q.trim())} · ${r.st}` }))
    const g = [...new Set(FD.map((r) => r.sku))].filter((x) => x.toLowerCase().includes(k)).slice(0, 3).map((x) => ({ g: '商品', v: x, a: hl(x, q.trim()) }))
    return [...o, ...g]
  }
  def({
    id: 'AD-FLT-003', name: '搜索框与联想', style: '联想下拉',
    fit: '大数据量里按关键词找订单、商品、客户：输入时下拉联想（命中处高亮、分组、键盘上下选择、回车确认），空输入聚焦时显示最近搜索，结果表同时即输即查。',
    avoid: '联想最多每组 3–5 条，别铺满屏；没有结果要给一句话和清除入口；最近搜索可单个删除、可清空；不要用“查询”按钮。',
    kw: '搜索 联想 自动补全 suggest autocomplete 最近搜索 关键词 高亮 键盘 search',
    css: B('adflt003', 0, emptyCss('adflt003') + `
.adflt003 .top{position:relative;padding:16px 16px 12px}
.adflt003 .a-sb{width:100%;height:40px;border-radius:8px}
.adflt003 .a-sb input{font-size:14px}
.adflt003 .a-sb .x{display:none;width:24px;height:24px;border-radius:4px;color:var(--ink3);align-items:center;justify-content:center}
.adflt003 .a-sb.has .x{display:inline-flex}.adflt003 .a-sb .x:hover{background:var(--soft);color:var(--ink)}
.adflt003 .a-sb.open{border-color:var(--ink2)}
.adflt003 .pn{position:absolute;left:16px;right:16px;top:calc(100% - 8px);z-index:20;max-height:320px;overflow:auto;padding:6px;border:1px solid var(--line);border-radius:12px;background:var(--card2);box-shadow:0 8px 24px var(--sh14);animation:adtIn .16s cubic-bezier(.2,0,0,1)}
.adflt003 .pn h6{display:flex;align-items:center;justify-content:space-between;margin:0;padding:6px 10px 4px;font-size:12px;line-height:18px;font-weight:600;color:var(--ink3)}
.adflt003 .it{display:flex;align-items:center;gap:10px;min-height:36px;padding:4px 10px;border-radius:8px;cursor:pointer}
.adflt003 .it small{margin-left:auto;font-size:12px;color:var(--ink3)}
.adflt003 .it.on{background:var(--pt)}
.adflt003 .it mark{background:none;color:var(--p-text);font-weight:600}
.adflt003 .it .a-i16{color:var(--ink3)}
.adflt003 .rc{display:flex;flex-wrap:wrap;gap:8px;padding:2px 10px 8px}
.adflt003 .rc .a-chip{height:28px;padding:0 4px 0 10px}
.adflt003 .rc .a-chip b{display:inline-flex;align-items:center;justify-content:center;width:20px;height:20px;border-radius:4px;color:var(--ink3);font-weight:400}
.adflt003 .rc .a-chip b:hover{background:var(--n5);color:var(--ink)}
.adflt003 .pn h6 button{font-size:12px;color:var(--p-text)}
.adflt003 .a-card{overflow:visible}`),
    html: () => `<div class="adflt003"><div class="a-card ov"><div class="top"><label class="a-sb">${svb('search')}<input type="search" data-q placeholder="搜索客户、订单号、商品" autocomplete="off" aria-label="搜索" role="combobox" aria-expanded="false"><button class="x" type="button" data-x aria-label="清空">${svb('close', 'a-i14')}</button></label><div class="pn" hidden></div></div>
<div class="a-tw"><table style="min-width:560px" data-pagination="none">${cg(W)}<thead><tr><th>客户</th><th>商品</th><th>金额（元）</th><th>状态</th></tr></thead><tbody>${FD.slice(0, 5).map(fmtRowS).join('')}</tbody></table></div><div class="a-pg"><span data-total>共 ${FD.length} 条，显示前 5 条</span></div></div></div>`,
    js: (root) => {
      const $ = (s) => root.querySelector(s), inp = $('[data-q]'), pn = $('.pn'), box = $('.a-sb'); let rec = [...REC0], act = -1, list = []
      const draw = () => {
        const q = inp.value.trim(); box.classList.toggle('has', !!inp.value)
        const rs = FD.filter((r) => matchQ(r, q))
        $('tbody').innerHTML = rs.length ? rs.slice(0, 5).map(fmtRowS).join('') : emptyTr(4, `没有找到“${q}”相关的订单`, '清除搜索')
        $('[data-total]').textContent = `共 ${rs.length} 条` + (rs.length > 5 ? '，显示前 5 条' : '')
      }
      const panel = () => {
        const q = inp.value.trim(); list = sug(q); act = -1
        if (!q) pn.innerHTML = rec.length ? `<h6><span>最近搜索</span><button type="button" data-rc-clear>清空</button></h6><div class="rc">${rec.map((x, i) => `<span class="a-chip" data-rec="${x}">${x}<b data-rm="${i}" role="button" aria-label="删除">${svb('close', 'a-i14')}</b></span>`).join('')}</div>` : '<h6><span>输入客户、订单号或商品名</span></h6>'
        else if (!list.length) pn.innerHTML = '<h6><span>没有匹配的联想，按回车查看全部结果</span></h6>'
        else { let last = ''; pn.innerHTML = list.map((x, i) => { const h = x.g !== last ? `<h6><span>${x.g}</span></h6>` : ''; last = x.g; return `${h}<div class="it" data-i="${i}" role="option">${svb(x.g === '订单' ? 'receipt' : 'box')}<span>${x.a}</span>${x.s ? `<small>${x.s}</small>` : ''}</div>` }).join('') }
        pn.hidden = false; box.classList.add('open'); inp.setAttribute('aria-expanded', 'true')
      }
      const close = () => { pn.hidden = true; box.classList.remove('open'); inp.setAttribute('aria-expanded', 'false') }
      const pick = (v) => { inp.value = v; rec = [v, ...rec.filter((x) => x !== v)].slice(0, 5); draw(); close() }
      const mark = () => { [...pn.querySelectorAll('.it')].forEach((e, i) => e.classList.toggle('on', i === act)) }
      inp.addEventListener('focus', panel); inp.addEventListener('input', () => { draw(); panel() })
      inp.addEventListener('keydown', (e) => {
        if (e.key === 'ArrowDown' || e.key === 'ArrowUp') { if (pn.hidden) panel(); if (!list.length) return; e.preventDefault(); act = (act + (e.key === 'ArrowDown' ? 1 : -1) + list.length) % list.length; mark() }
        if (e.key === 'Enter') { e.preventDefault(); if (act >= 0 && list[act]) pick(list[act].v); else if (inp.value.trim()) pick(inp.value.trim()) }
        if (e.key === 'Escape') close()
      })
      root.addEventListener('click', (e) => {
        const it = e.target.closest('.it'); if (it) { pick(list[+it.dataset.i].v); return }
        const rm = e.target.closest('[data-rm]'); if (rm) { rec.splice(+rm.dataset.rm, 1); panel(); return }
        if (e.target.closest('[data-rc-clear]')) { rec = []; panel(); return }
        const rc = e.target.closest('[data-rec]'); if (rc) { pick(rc.dataset.rec); return }
        if (e.target.closest('[data-x],[data-clear]')) { inp.value = ''; draw(); inp.focus(); panel() }
      })
      const off = (e) => { if (!root.isConnected) return document.removeEventListener('click', off); if (!e.composedPath().includes($('.top'))) close() }
      document.addEventListener('click', off)
    },
  })
}

/* AD-FLT-004 标签筛选 */
{
  const stOf = (g) => (g.k === 0 ? '缺货' : g.on ? '在售' : '已下架')
  const TAGS = ['数码', '家居', '运动', '箱包', '配饰', '美妆']
  const run = (s) => GOODS.filter((g) => (s.st === 'all' || stOf(g) === s.st) && (!s.tags.length || s.tags.some((t) => g.tags.includes(t))))
  const card = (g) => `<div class="gc"><img class="a-th" src="${P(g.i)}" alt=""><div class="a-nm"><b>${g.n}</b><small>${g.tags.join(' · ')}</small></div><span class="pr">${money(g.p)}</span>${tag({ 在售: 'ok', 已下架: 'mu', 缺货: 'bad' }[stOf(g)], stOf(g))}</div>`
  const segs = (s) => ['all', '在售', '已下架', '缺货'].map((x) => `<button type="button" data-st="${x}" class="${s.st === x ? 'on' : ''}">${x === 'all' ? '全部' : x}<small>${x === 'all' ? GOODS.length : GOODS.filter((g) => stOf(g) === x).length}</small></button>`).join('')
  const chips = (s) => TAGS.map((t) => { const n = GOODS.filter((g) => (s.st === 'all' || stOf(g) === s.st) && g.tags.includes(t)).length; return `<button type="button" class="a-chip${s.tags.includes(t) ? ' on' : ''}${n === 0 ? ' z' : ''}" data-tag="${t}" aria-pressed="${s.tags.includes(t)}">${t}<small>${n}</small></button>` }).join('')
  const D = { st: 'all', tags: [] }
  def({
    id: 'AD-FLT-004', name: '标签筛选', style: '单选多选',
    fit: '商品、内容、客户这类有“标签/分类”的列表：互斥维度（状态）用分段单选，可叠加的维度（标签）用胶囊多选，每项带数量，已选数量在旁边写清并可一键清除。',
    avoid: '互斥的别用多选胶囊；标签超过十几个时要收起或搜索；选中后要立刻看到结果数量变化，不能没反应；数量为 0 的弱化。',
    kw: '标签 chips 胶囊 单选 多选 分类筛选 状态分段 筛选标签 tag filter 商品标签',
    css: B('adflt004', 0, `
.adflt004 .a-card{padding:16px}
.adflt004 .row{display:flex;align-items:center;gap:12px;flex-wrap:wrap}
.adflt004 .row+.row{margin-top:12px}
.adflt004 .a-seg button small,.adflt004 .a-chip small{margin-left:6px;font-size:12px;color:var(--ink3);font-variant-numeric:tabular-nums}
.adflt004 .a-seg button.on small,.adflt004 .a-chip.on small{color:var(--p-text)}
.adflt004 .a-chip.z{color:var(--ink3)}.adflt004 .a-chip.z small{opacity:.6}
.adflt004 .row .a-lk{margin-left:auto}
.adflt004 .sum{display:flex;align-items:center;gap:8px;margin:16px 0 8px;font-size:12px;line-height:18px;color:var(--ink3)}
.adflt004 .gl{display:grid;grid-template-columns:repeat(auto-fill,minmax(250px,1fr));gap:10px}
.adflt004 .gc{display:flex;align-items:center;gap:10px;min-width:0;padding:10px 12px;border:1px solid var(--line);border-radius:12px;animation:adtFade .2s}
.adflt004 .gc .a-nm{flex:1}
.adflt004 .gc .pr{font-variant-numeric:tabular-nums;color:var(--ink)}
.adflt004 .none{grid-column:1/-1;padding:28px 0;text-align:center;color:var(--ink2)}`),
    html: () => `<div class="adflt004"><div class="a-card"><div class="row"><div class="a-seg" data-seg role="radiogroup" aria-label="状态">${segs(D)}</div></div><div class="row" data-chips>${chips(D)}<button class="a-lk" type="button" data-clear hidden>清除标签</button></div><div class="sum" data-sum>找到 ${GOODS.length} 件商品</div><div class="gl" data-list>${GOODS.map(card).join('')}</div></div></div>`,
    js: (root) => {
      const $ = (s) => root.querySelector(s); const s = { st: 'all', tags: [] }
      const render = () => {
        const rs = run(s)
        $('[data-seg]').innerHTML = segs(s); $('[data-chips]').querySelectorAll('.a-chip').forEach((e) => e.remove()); $('[data-clear]').insertAdjacentHTML('beforebegin', chips(s))
        $('[data-clear]').hidden = !s.tags.length
        $('[data-sum]').textContent = `找到 ${rs.length} 件商品` + (s.tags.length ? `，已选 ${s.tags.length} 个标签（满足任一即可）` : '')
        $('[data-list]').innerHTML = rs.length ? rs.map(card).join('') : '<div class="none">没有符合条件的商品，试试清除标签</div>'
      }
      root.addEventListener('click', (e) => {
        const a = e.target.closest('[data-st]'); if (a) { s.st = a.dataset.st; render() }
        const t = e.target.closest('[data-tag]'); if (t) { const k = t.dataset.tag; s.tags = s.tags.includes(k) ? s.tags.filter((x) => x !== k) : [...s.tags, k]; render() }
        if (e.target.closest('[data-clear]')) { s.tags = []; render() }
      })
    },
  })
}

/* AD-FLT-005 日期范围快捷选 */
{
  const A = (d, n) => { const x = new Date(d); x.setDate(x.getDate() + n); return x }
  const PRE = [['today', '今天', () => [T0, T0]], ['yest', '昨天', () => [A(T0, -1), A(T0, -1)]], ['d7', '近 7 天', () => [A(T0, -6), T0]], ['d30', '近 30 天', () => [A(T0, -29), T0]], ['mon', '本月', () => [new Date(2026, 10, 1), T0]], ['last', '上月', () => [new Date(2026, 9, 1), new Date(2026, 9, 31)]]]
  const run = (a, b) => FD.filter((r) => { const k = ymd(r.d); return k >= ymd(a) && k <= ymd(b) })
  const WD = ['一', '二', '三', '四', '五', '六', '日']
  def({
    id: 'AD-FLT-005', name: '日期范围快捷选', style: '快捷自定义',
    fit: '时间范围只放一个控件：左侧快捷项（今天、近 7 天、近 30 天、本月……），右侧日历选自定义区间，点快捷项立即生效，自定义选完两端点确定；结果区同步更新。',
    avoid: '快捷范围与自定义日期别摆成两套控件；未来日期要禁用；选中的范围要在按钮上写成完整日期，不要只写“自定义”；跨年要显示年份。',
    kw: '日期范围 日期选择 快捷 今天 近7天 近30天 自定义 日历 date range picker 时间筛选',
    css: B('adflt005', 0, `
.adflt005{min-height:440px}
.adflt005 .a-card{overflow:visible;padding:16px}
.adflt005 .tr{position:relative;display:flex;align-items:center;gap:12px;flex-wrap:wrap}
.adflt005 .a-sel{height:36px;min-width:292px;justify-content:space-between}
.adflt005 .a-sel b{font-weight:600;color:var(--p-text)}.adflt005 .a-sel span{color:var(--ink2)}
.adflt005 .a-sel .l{display:inline-flex;align-items:center;gap:8px;white-space:nowrap}
.adflt005 .pop{position:absolute;left:0;top:calc(100% + 6px);z-index:20;display:flex;width:488px;max-width:calc(100vw - 48px);border:1px solid var(--line);border-radius:12px;background:var(--card2);box-shadow:0 12px 32px var(--sh16);animation:adtIn .18s cubic-bezier(.2,0,0,1)}
.adflt005 .ps{flex:none;display:flex;flex-direction:column;gap:2px;width:112px;padding:8px;border-right:1px solid var(--line)}
.adflt005 .ps button{height:32px;padding:0 10px;border-radius:8px;text-align:left;color:var(--ink);white-space:nowrap}
.adflt005 .ps button:hover{background:var(--n3)}.adflt005 .ps button.on{background:var(--pt);color:var(--p-text)}
.adflt005 .ps hr{margin:4px 8px;border:0;height:1px;background:var(--line)}
.adflt005 .cl{flex:1;min-width:0;padding:12px 14px 12px}
.adflt005 .ch{display:flex;align-items:center;justify-content:space-between;margin-bottom:6px;font-weight:600}
.adflt005 .ch button{display:inline-flex;align-items:center;justify-content:center;width:28px;height:28px;border-radius:8px;color:var(--ink2)}
.adflt005 .ch button:hover{background:var(--soft)}.adflt005 .ch button:disabled{color:var(--ink7);pointer-events:none}
.adflt005 .gr{display:grid;grid-template-columns:repeat(7,1fr);row-gap:2px}
.adflt005 .gr .w{height:28px;text-align:center;font-size:12px;line-height:28px;color:var(--ink3)}
.adflt005 .gr .d{position:relative;height:32px;font-variant-numeric:tabular-nums;border-radius:0;transition:background-color .12s}
.adflt005 .gr .d:hover{background:var(--soft);border-radius:8px}
.adflt005 .gr .d.td::after{content:"";position:absolute;left:50%;bottom:3px;width:4px;height:4px;margin-left:-2px;border-radius:50%;background:var(--p)}
.adflt005 .gr .d.in{background:var(--pt);color:var(--p-text)}
.adflt005 .gr .d.on{background:var(--p);color:#fff;border-radius:8px}
.adflt005 .gr .d.in.s{border-radius:8px 0 0 8px}.adflt005 .gr .d.in.e{border-radius:0 8px 8px 0}
.adflt005 .gr .d.on.s.e{border-radius:8px}
.adflt005 .gr .d.on.s:not(.e){border-radius:8px 0 0 8px}.adflt005 .gr .d.on.e:not(.s){border-radius:0 8px 8px 0}
.adflt005 .gr .d:disabled{color:var(--ink7);pointer-events:none}
.adflt005 .gr .d.on.td::after{background:var(--lift)}
.adflt005 .cf{display:flex;align-items:center;justify-content:space-between;gap:8px;margin-top:10px;padding-top:10px;border-top:1px solid var(--line)}
.adflt005 .cf .a-ht{flex:1}
.adflt005 .kp{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:10px;margin-top:16px}
.adflt005 .kp div{padding:12px 14px;border:1px solid var(--line);border-radius:12px}
.adflt005 .kp small{display:block;font-size:12px;line-height:18px;color:var(--ink3)}
.adflt005 .kp b{display:block;font-size:20px;line-height:28px;font-weight:600;font-variant-numeric:tabular-nums}
.adflt005 .rt{margin-top:12px;border:1px solid var(--line);border-radius:12px;overflow-x:auto}
@media(max-width:520px){.adflt005 .pop{flex-direction:column;width:min(340px,calc(100vw - 48px))}.adflt005 .ps{flex-direction:row;flex-wrap:wrap;width:auto;border-right:0;border-bottom:1px solid var(--line)}.adflt005 .ps hr{display:none}.adflt005 .a-sel{min-width:0;width:100%}.adflt005 .kp{grid-template-columns:1fr}}
.adflt005 .rt th{height:40px}.adflt005 .rt td{height:44px}`),
    html: () => `<div class="adflt005"><div class="a-card"><div class="tr"><button class="a-sel" type="button" data-tg2 aria-haspopup="dialog"><span class="l">${svb('calendar')}<b data-name>近 7 天</b><span data-range>2026-10-29 ~ 2026-11-04</span></span>${svb('down', 'a-i14')}</button>
<div class="pop" hidden role="dialog" aria-label="选择日期范围"><div class="ps">${PRE.map(([k, t]) => `<button type="button" data-p="${k}" class="${k === 'd7' ? 'on' : ''}">${t}</button>`).join('')}<hr><button type="button" data-p="custom">自定义</button></div>
<div class="cl"><div class="ch"><button type="button" data-m="-1" aria-label="上个月">${svb('left')}</button><span data-mon></span><button type="button" data-m="1" aria-label="下个月">${svb('right')}</button></div><div class="gr" data-gr></div><div class="cf"><span class="a-ht" data-hint>选择开始日期</span><button class="a-b" type="button" data-cancel>取消</button><button class="a-b p" type="button" data-ok disabled>确定</button></div></div></div></div>
<div class="kp"><div><small>订单数</small><b data-k="n">0</b></div><div><small>成交金额（元）</small><b data-k="a">0</b></div><div><small>客单价（元）</small><b data-k="u">0</b></div></div>
<div class="rt"><table style="min-width:520px" data-pagination="none">${cg([190, 0, 120, 100])}<thead><tr><th>客户</th><th>商品</th><th>金额（元）</th><th>状态</th></tr></thead><tbody></tbody></table></div></div></div>`,
    js: (root) => {
      const $ = (s) => root.querySelector(s), $$ = (s) => [...root.querySelectorAll(s)]; const pop = $('.pop')
      let rng = PRE[2][2](), name = '近 7 天', view = new Date(2026, 10, 1), a = null, b = null, custom = false
      const fmt = (d) => ymd(d)
      const apply = () => {
        const rs = run(rng[0], rng[1]), sum = rs.reduce((x, r) => x + r.amt, 0)
        $('[data-name]').textContent = name; $('[data-range]').textContent = rng[0].getTime() === rng[1].getTime() ? fmt(rng[0]) : `${fmt(rng[0])} ~ ${fmt(rng[1])}`
        $('[data-k=n]').textContent = rs.length; $('[data-k=a]').textContent = money(sum); $('[data-k=u]').textContent = rs.length ? money(sum / rs.length) : '—'
        $('tbody').innerHTML = rs.length ? rs.slice(0, 4).map(fmtRowS).join('') : emptyTr(4, '这段时间没有订单', '近 30 天').replace('data-clear', 'data-clear')
        $$('[data-p]').forEach((x) => x.classList.toggle('on', x.dataset.p === (custom ? 'custom' : PRE.find((p) => p[1] === name) && PRE.find((p) => p[1] === name)[0])))
      }
      const grid = () => {
        const y = view.getFullYear(), m = view.getMonth(), first = (new Date(y, m, 1).getDay() + 6) % 7, days = new Date(y, m + 1, 0).getDate()
        $('[data-mon]').textContent = `${y} 年 ${m + 1} 月`; $('[data-m="1"]').disabled = y === 2026 && m >= 10
        const lo = a && b ? (a < b ? a : b) : a, hi = a && b ? (a < b ? b : a) : a
        $('[data-gr]').innerHTML = WD.map((w) => `<span class="w">${w}</span>`).join('') + '<span></span>'.repeat(first) + Array.from({ length: days }, (_, i) => {
          const d = new Date(y, m, i + 1), k = fmt(d), fut = d > T0
          const on = (lo && k === fmt(lo)) || (hi && k === fmt(hi)), inr = lo && hi && k > fmt(lo) && k < fmt(hi)
          return `<button type="button" class="d${on ? ' on' : ''}${inr ? ' in' : ''}${lo && k === fmt(lo) ? ' s' : ''}${hi && k === fmt(hi) ? ' e' : ''}${k === fmt(T0) ? ' td' : ''}" data-d="${k}" ${fut ? 'disabled' : ''}>${i + 1}</button>`
        }).join('')
        $('[data-ok]').disabled = !(a && b)
        $('[data-hint]').textContent = !a ? '选择开始日期' : !b ? '再选择结束日期' : `${fmt(a < b ? a : b)} ~ ${fmt(a < b ? b : a)}`
      }
      const open = () => { pop.hidden = false; a = b = null; view = new Date(rng[1].getFullYear(), rng[1].getMonth(), 1); grid() }
      root.addEventListener('click', (e) => {
        if (e.target.closest('[data-tg2]')) { pop.hidden ? open() : (pop.hidden = true); return }
        const p = e.target.closest('[data-p]')
        if (p) {
          if (p.dataset.p === 'custom') { custom = true; a = b = null; grid(); apply(); return }
          const pr = PRE.find((x) => x[0] === p.dataset.p); rng = pr[2](); name = pr[1]; custom = false; pop.hidden = true; apply(); return
        }
        const m = e.target.closest('[data-m]'); if (m) { view = new Date(view.getFullYear(), view.getMonth() + +m.dataset.m, 1); grid(); return }
        const d = e.target.closest('[data-d]')
        if (d) { const [y, mo, da] = d.dataset.d.split('-').map(Number), dt = new Date(y, mo - 1, da); custom = true; if (!a || (a && b)) { a = dt; b = null } else b = dt; grid(); $$('[data-p]').forEach((x) => x.classList.toggle('on', x.dataset.p === 'custom')); return }
        if (e.target.closest('[data-cancel]')) { pop.hidden = true; custom = false; apply(); return }
        if (e.target.closest('[data-ok]')) { const lo = a < b ? a : b, hi = a < b ? b : a; rng = [lo, hi]; name = '自定义'; custom = true; pop.hidden = true; apply(); return }
        if (e.target.closest('[data-clear]')) { const pr = PRE[3]; rng = pr[2](); name = pr[1]; custom = false; apply() }
      })
      const off = (e) => { if (!root.isConnected) return document.removeEventListener('click', off); if (!pop.hidden && !e.composedPath().includes($('.tr'))) pop.hidden = true }
      document.addEventListener('click', off); apply()
    },
  })
}

/* AD-FLT-006 已选条件条 */
{
  const W = [200, 0, 128, 112, 160]
  const DEF = { q: '', st: '待发货', pay: 'all', city: 'all' }
  const LB = { st: '状态', pay: '支付方式', city: '城市' }
  const run = (s) => FD.filter((r) => matchQ(r, s.q) && (s.st === 'all' || r.st === s.st) && (s.pay === 'all' || r.pay === s.pay) && (s.city === 'all' || r.city === s.city))
  const chips = (s) => { const c = []; if (s.q.trim()) c.push(['q', '关键词', s.q.trim()]); ['st', 'pay', 'city'].forEach((k) => { if (s[k] !== 'all') c.push([k, LB[k], s[k]]) }); return c.length ? c.map(([k, a, v]) => `<span class="a-chip on" data-chip="${k}">${a}：${v}<button type="button" data-x="${k}" aria-label="移除${a}条件">${svb('close', 'a-i14')}</button></span>`).join('') + '<button class="a-lk" type="button" data-all>清空</button>' : '<span class="a-ht">暂无筛选条件</span>' }
  def({
    id: 'AD-FLT-006', name: '已选条件条', style: '可移除标签',
    fit: '筛选一多就让用户看清“现在结果是被什么限制的”：已生效条件以标签排在表格上方，每个可单独移除，末尾一个“清空”；标签条高度固定，增删条件时表格不跳。',
    avoid: '状态标签页（如“待发货 / 已完成”）的切换不算筛选条件，别重复显示；没有条件时保留一行占位，不要让表格上下跳；标签文字写“字段：值”。',
    kw: '已选条件 筛选标签 条件标签 清空 移除 chips filter tags 条件条 面包屑筛选',
    wide: true,
    css: B('adflt006', 0, FBAR('adflt006') + emptyCss('adflt006') + `
.adflt006 .a-card{overflow:visible}
.adflt006 .cb{display:flex;align-items:center;flex-wrap:wrap;gap:8px;min-height:48px;padding:8px 16px;border-top:1px solid var(--line);background:var(--n1)}
.adflt006 .cb .a-chip{height:28px;padding:0 4px 0 10px}
.adflt006 .cb .a-chip button{display:inline-flex;align-items:center;justify-content:center;width:20px;height:20px;border-radius:4px;color:var(--p-text)}
.adflt006 .cb .a-chip button:hover{background:rgba(var(--p-rgb),.14)}`),
    html: () => `<div class="adflt006"><div class="a-card ov"><div class="a-fbar">${searchBox('搜索客户、订单号、商品', 260)}${dd('st', stOptions(run, DEF), DEF.st)}${dd('pay', PAY_O, 'all')}${dd('city', CITY_O, 'all')}</div><div class="cb" data-cb>${chips(DEF)}</div>
<div class="a-tw"><table style="min-width:${sumw(W)}px" data-pagination="none">${cg(W)}<thead><tr><th>客户</th><th>商品</th><th>金额（元）</th><th>状态</th><th>下单时间</th></tr></thead><tbody>${run(DEF).slice(0, 5).map(fmtRow).join('')}</tbody></table></div><div class="a-pg"><span data-total>共 ${run(DEF).length} 条</span></div></div></div>`,
    js: (root) => {
      const $ = (s) => root.querySelector(s); const s = { ...DEF }
      const reset = (k) => { s[k] = k === 'q' ? '' : 'all'; if (k === 'q') $('[data-q]').value = ''; else { const d = $(`.a-dd[data-key=${k}]`); d.querySelector('[data-label]').textContent = { st: '状态', pay: '支付方式', city: '收货城市' }[k]; d.querySelectorAll('[data-o]').forEach((o) => o.classList.toggle('on', o.dataset.val === 'all')) } }
      const render = () => {
        const rs = run(s)
        $('tbody').innerHTML = rs.length ? rs.slice(0, 5).map(fmtRow).join('') : emptyTr(5)
        $('[data-total]').textContent = `共 ${rs.length} 条` + (rs.length > 5 ? '，显示前 5 条' : '')
        fillDD(root, 'st', stOptions(run, s), s.st); markHas(root, s); $('[data-cb]').innerHTML = chips(s)
      }
      bindF(root, s, render)
      root.addEventListener('click', (e) => {
        const x = e.target.closest('[data-x]'); if (x) { reset(x.dataset.x); render() }
        if (e.target.closest('[data-all],[data-clear]')) { ['q', 'st', 'pay', 'city'].forEach(reset); render() }
      })
      render()
    },
  })
}

/* AD-FLT-007 保存的筛选方案 */
{
  const W = [200, 0, 128, 112, 160]
  const AMT = [['all', '全部', undefined, '金额'], ['500', '≥ 500 元'], ['1000', '≥ 1,000 元']]
  const SCH0 = [{ id: 's0', n: '默认视图', st: '待发货', days: '30', min: 'all', sys: 1 }, { id: 's1', n: '大额待发货', st: '待发货', days: 'all', min: '500' }, { id: 's2', n: '本周退款', st: '退款中', days: '7', min: 'all' }]
  const run = (s) => FD.filter((r) => (s.st === 'all' || r.st === s.st) && inDays(r, s.days) && (s.min === 'all' || r.amt >= +s.min))
  const tabs = (sch, cur, dirty) => sch.map((x) => `<button type="button" class="vt${x.id === cur ? ' on' : ''}" data-sch="${x.id}" role="tab" aria-selected="${x.id === cur}">${x.sys ? svb('adt_bookmark', 'a-i14') : ''}${x.n}${x.id === cur && dirty ? '<i class="dot" title="已修改"></i>' : ''}${x.sys ? '' : `<span class="rm" data-rm="${x.id}" role="button" aria-label="删除方案${x.n}">${svb('close', 'a-i14')}</span>`}</button>`).join('')
  def({
    id: 'AD-FLT-007', name: '保存的筛选方案', style: '视图标签',
    fit: '同一个人反复用同几组条件（“大额待发货”“本周退款”）：把条件存成方案，顶部点方案名一键套用；改动条件后方案旁出现“已修改”，可另存为新方案。',
    avoid: '系统默认方案不能删除或覆盖；方案名不能重复、不能为空；删除方案要有轻提示；别把方案存成 20 个，超过 8 个要收进“更多”。',
    kw: '保存筛选 筛选方案 视图 常用筛选 保存条件 方案 view saved filter 我的视图 另存为',
    wide: true,
    css: B('adflt007', 0, FBAR('adflt007') + emptyCss('adflt007') + `
.adflt007 .a-card{overflow:visible}
.adflt007 .vs{display:flex;align-items:center;gap:4px;padding:0 12px;border-bottom:1px solid var(--line);overflow-x:auto}
.adflt007 .vt{position:relative;display:inline-flex;align-items:center;gap:6px;height:44px;padding:0 12px;color:var(--ink2);white-space:nowrap;transition:color .15s}
.adflt007 .vt:hover{color:var(--ink)}
.adflt007 .vt.on{color:var(--p-text)}
.adflt007 .vt.on::after{content:"";position:absolute;left:12px;right:12px;bottom:-1px;height:2px;border-radius:1px;background:var(--p)}
.adflt007 .vt .dot{width:6px;height:6px;border-radius:50%;background:var(--warn-fill)}
.adflt007 .vt .rm{display:none;align-items:center;justify-content:center;width:20px;height:20px;margin-right:-6px;border-radius:4px;color:var(--ink3)}
.adflt007 .vt:hover .rm,.adflt007 .vt.on .rm{display:inline-flex}.adflt007 .vt .rm:hover{background:var(--n4);color:var(--ink)}
.adflt007 .vs .a-add{margin-left:4px;color:var(--p-text)}
.adflt007 .a-fbar .sp+.a-lk{visibility:hidden}.adflt007 .a-fbar.dirty .sp+.a-lk{visibility:visible}
.adflt007 .fld{display:block}.adflt007 .fld .a-in{width:100%}
.adflt007 .a-dlg .a-ht{margin-top:6px}.adflt007 .a-dlg .a-ht.bad{color:var(--danger)}`),
    html: () => `<div class="adflt007"><div class="a-card ov"><div class="vs" role="tablist" data-vs>${tabs(SCH0, 's0', false)}<button class="a-lk a-add" type="button" data-open="sv" data-new>${svb('plus', 'a-i14')}保存当前筛选</button></div>
<div class="a-fbar" data-fb>${dd('st', stOptions(run, SCH0[0]), '待发货')}${dd('days', DAYS, '30')}${dd('min', AMT, 'all')}<span class="sp"></span><button class="a-lk" type="button" data-back>还原为方案设置</button></div>
<div class="a-tw"><table style="min-width:${sumw(W)}px" data-pagination="none">${cg(W)}<thead><tr><th>客户</th><th>商品</th><th>金额（元）</th><th>状态</th><th>下单时间</th></tr></thead><tbody>${run(SCH0[0]).slice(0, 5).map(fmtRow).join('')}</tbody></table></div><div class="a-pg"><span data-total>共 ${run(SCH0[0]).length} 条</span></div></div>
<div class="ix-ov" data-ov="sv"><div class="ix-mask"></div><div class="a-dlg" role="dialog" aria-modal="true"><h4><span>保存为筛选方案</span></h4><label class="fld"><input class="a-in" data-name placeholder="给方案起个名字，例如“华东待发货”" maxlength="12" aria-label="方案名称"></label><div class="a-ht" data-msg>将保存当前的状态、时间、金额条件，最多 12 个字。</div><div class="ft"><button class="a-b" type="button" data-close>取消</button><button class="a-b p" type="button" data-save data-close disabled>保存</button></div></div></div></div>`,
    js: (root) => {
      const $ = (s) => root.querySelector(s), $$ = (s) => [...root.querySelectorAll(s)]
      const sch = SCH0.map((x) => ({ ...x })); let cur = 's0'; const s = { st: '待发货', days: '30', min: 'all' }
      const base = () => sch.find((x) => x.id === cur)
      const dirty = () => ['st', 'days', 'min'].some((k) => s[k] !== base()[k])
      const setDD = () => { const lab = { st: '状态', days: '下单时间', min: '金额' }; ;['st', 'days', 'min'].forEach((k) => { const d = $(`.a-dd[data-key=${k}]`), o = [...d.querySelectorAll('[data-o]')]; o.forEach((x) => x.classList.toggle('on', x.dataset.val === s[k])); const on = o.find((x) => x.dataset.val === s[k]); d.querySelector('[data-label]').textContent = s[k] === 'all' ? lab[k] : on ? on.dataset.v : s[k] }) }
      const render = () => {
        const rs = run(s)
        $('tbody').innerHTML = rs.length ? rs.slice(0, 5).map(fmtRow).join('') : emptyTr(5, '没有符合条件的订单', '还原为方案设置')
        $('[data-total]').textContent = `共 ${rs.length} 条` + (rs.length > 5 ? '，显示前 5 条' : '')
        fillDD(root, 'st', stOptions(run, s), s.st); setDD(); markHas(root, s)
        $('[data-vs]').querySelectorAll('.vt').forEach((e) => e.remove()); $('[data-vs]').insertAdjacentHTML('afterbegin', tabs(sch, cur, dirty()))
        $('[data-fb]').classList.toggle('dirty', dirty())
      }
      const apply = (id) => { cur = id; const b = base(); s.st = b.st; s.days = b.days; s.min = b.min; render() }
      bindF(root, s, render)
      root.addEventListener('click', (e) => {
        const rm = e.target.closest('[data-rm]'); if (rm) { e.stopPropagation(); const x = sch.find((v) => v.id === rm.dataset.rm); sch.splice(sch.indexOf(x), 1); IX.toast(root, `已删除方案“${x.n}”`); if (cur === x.id) apply('s0'); else render(); return }
        const v = e.target.closest('[data-sch]'); if (v) { apply(v.dataset.sch); return }
        if (e.target.closest('[data-back],[data-clear]')) { apply(cur); return }
        if (e.target.closest('[data-new]')) { $('[data-name]').value = ''; $('[data-save]').disabled = true; $('[data-msg]').textContent = '将保存当前的状态、时间、金额条件，最多 12 个字。'; $('[data-msg]').classList.remove('bad') }
        if (e.target.closest('[data-save]')) { const n = $('[data-name]').value.trim(); sch.push({ id: 's' + Date.now(), n, st: s.st, days: s.days, min: s.min }); cur = sch[sch.length - 1].id; render(); IX.toast(root, `已保存方案“${n}”`) }
      })
      root.addEventListener('input', (e) => {
        if (!e.target.matches('[data-name]')) return
        const n = e.target.value.trim(), dup = sch.some((x) => x.n === n), m = $('[data-msg]')
        $('[data-save]').disabled = !n || dup; m.textContent = dup ? '已有同名方案，换一个名字' : '将保存当前的状态、时间、金额条件，最多 12 个字。'; m.classList.toggle('bad', dup)
      })
      render()
    },
  })
}

/* AD-FLT-008 排序控件 */
{
  const COLS = [['def', '默认排序'], ['ts', '下单时间'], ['amt', '金额'], ['q', '数量']]
  const NAT = { ts: ['最新在前', '最早在前'], amt: ['从高到低', '从低到高'], q: ['从多到少', '从少到多'] }
  const rows = FD.slice(0, 7)
  const ord = (k, dir) => { const a = [...rows]; if (k === 'def') return a.sort((x, y) => STS6.indexOf(x.st) - STS6.indexOf(y.st) || y.ts - x.ts); return a.sort((x, y) => (dir === 'desc' ? 1 : -1) * (y[k] - x[k])) }
  const line = (r) => `<tr><td class="l">${nm(r)}</td><td class="r">${money(r.amt)}</td><td class="n">${r.q}</td><td class="n">${r.date.slice(5)}</td><td>${stTag(r)}</td></tr>`
  def({
    id: 'AD-FLT-008', name: '排序控件', style: '三态切换',
    fit: '列表没有表头排序（卡片列表、移动端）或要提供“默认排序”时：一排排序项，点一下降序、再点升序、第三下回到默认；当前排序写成人话（“按金额从高到低”）。',
    avoid: '默认排序要有意义（待处理按紧急程度），别默认按创建时间；表格已有表头排序就不要再放一套；一次只允许一个排序字段，除非业务确实需要多级。',
    kw: '排序 sort 升序 降序 排序条 排序方式 默认排序 三态 order by 时间排序 金额排序',
    css: B('adflt008', 0, `
.adflt008 .a-card{padding:0}
.adflt008 .sb{display:flex;align-items:center;gap:6px;flex-wrap:wrap;padding:12px 16px;border-bottom:1px solid var(--line)}
.adflt008 .so2{display:inline-flex;align-items:center;gap:6px;height:32px;padding:0 12px;border-radius:8px;color:var(--ink2);white-space:nowrap;transition:background-color .15s,color .15s}
.adflt008 .so2:hover{background:var(--soft);color:var(--ink)}
.adflt008 .so2.on{background:var(--pt);color:var(--p-text)}
.adflt008 .so2 .ar{display:inline-flex;width:14px;height:14px;transition:transform .2s cubic-bezier(.2,0,0,1)}
.adflt008 .so2.asc .ar{transform:rotate(180deg)}
.adflt008 .so2:not(.on) .ar{display:none}
.adflt008 .tx{margin-left:auto;font-size:12px;color:var(--ink3);white-space:nowrap}
.adflt008 tbody.a-fx{animation:adtFade .2s}`),
    html: () => `<div class="adflt008"><div class="a-card"><div class="sb" role="group" aria-label="排序方式">${COLS.map(([k, t], i) => `<button type="button" class="so2${i === 0 ? ' on' : ''}" data-k="${k}" aria-pressed="${i === 0}">${t}<span class="ar">${sv('arrowdown')}</span></button>`).join('')}<span class="tx" data-tx>待处理优先，同状态按时间从新到旧</span></div>
<div class="a-tw"><table style="min-width:560px" data-pagination="none">${cg([190, 120, 80, 100, 110])}<thead><tr><th>客户</th><th>金额（元）</th><th>数量</th><th>下单时间</th><th>状态</th></tr></thead><tbody>${ord('def').map(line).join('')}</tbody></table></div></div></div>`,
    js: (root) => {
      const $ = (s) => root.querySelector(s); let k = 'def', dir = 'desc'
      const render = () => {
        const tb = $('tbody'); tb.innerHTML = ord(k, dir).map(line).join(''); tb.classList.remove('a-fx'); void tb.offsetWidth; tb.classList.add('a-fx')
        root.querySelectorAll('.so2').forEach((b) => { const on = b.dataset.k === k; b.classList.toggle('on', on); b.classList.toggle('asc', on && dir === 'asc'); b.setAttribute('aria-pressed', on) })
        $('[data-tx]').textContent = k === 'def' ? '待处理优先，同状态按时间从新到旧' : `按${COLS.find((c) => c[0] === k)[1]}${NAT[k][dir === 'desc' ? 0 : 1]}`
      }
      root.addEventListener('click', (e) => {
        const b = e.target.closest('.so2'); if (!b) return
        const n = b.dataset.k
        if (n === 'def') { k = 'def'; dir = 'desc' }
        else if (k !== n) { k = n; dir = 'desc' }
        else if (dir === 'desc') dir = 'asc'
        else { k = 'def'; dir = 'desc' }
        render()
      })
    },
  })
}

/* AD-FLT-009 级联筛选 */
{
  const REG = { 浙江省: { 杭州市: ['西湖区', '余杭区', '滨江区'], 宁波市: ['海曙区', '鄞州区'] }, 广东省: { 广州市: ['天河区', '越秀区'], 深圳市: ['南山区', '福田区', '宝安区'] }, 四川省: { 成都市: ['锦江区', '武侯区', '高新区'] }, 江苏省: { 南京市: ['鼓楼区', '玄武区'], 苏州市: ['姑苏区', '工业园区'] } }
  const ST = []
  Object.entries(REG).forEach(([p, cs]) => Object.entries(cs).forEach(([c, ds]) => ds.forEach((d, i) => ST.push({ n: c.replace('市', '') + d.replace('区', '') + '店', p, c, d, on: (ST.length * 3 + i) % 5 !== 4, tel: '0' + (571 + ST.length) + '-8' + String(2000 + ST.length * 137).slice(-4) + '66' }))))
  const run = (s) => ST.filter((x) => (!s.p || x.p === s.p) && (!s.c || x.c === s.c) && (!s.d || x.d === s.d))
  const menu = (list, cur, all) => `<div data-o data-v="${all}" data-val="" class="${cur ? '' : 'on'}">全部</div>` + list.map((v) => `<div data-o data-v="${v}" data-val="${v}" class="${v === cur ? 'on' : ''}">${v}</div>`).join('')
  const dds = (k, ph, list, cur, dis) => `<div class="a-dd${dis ? ' dis' : ''}" data-ix="dd" data-key="${k}"><button class="a-sel${cur ? ' has' : ''}" data-tg type="button" aria-haspopup="listbox" ${dis ? 'tabindex="-1" aria-disabled="true"' : ''}><span data-label>${cur || ph}</span>${svb('down', 'a-i14')}</button><div class="menu" role="listbox">${menu(list, cur, ph)}</div></div>`
  const card = (x) => `<div class="sc"><div class="a-nm"><b>${x.n}</b><small>${x.p} ${x.c} ${x.d} · ${x.tel}</small></div>${tag(x.on ? 'ok' : 'mu', x.on ? '营业中' : '休息中')}</div>`
  def({
    id: 'AD-FLT-009', name: '级联筛选', style: '省市区联动',
    fit: '有上下级关系的条件（省 → 市 → 区县、分类 → 子类、品牌 → 型号）：上级选了下级才可选，上级一改下级自动清空；已选路径写成一条，可一键清除。',
    avoid: '下级未解锁时要写明原因（“请先选择省份”），不要只置灰；上级改变后下级要回到“全部”，不能残留旧值；层级不超过 3 层，更深的用搜索选择。',
    kw: '级联 省市区 联动 级联选择 地区筛选 cascader 三级 分类联动 门店区域',
    css: B('adflt009', 0, `
.adflt009 .a-card{overflow:visible;padding:16px}
.adflt009 .rw{display:flex;align-items:center;flex-wrap:wrap;gap:8px}
.adflt009 .a-dd.dis{pointer-events:none}
.adflt009 .a-dd.dis .a-sel{background:var(--n2);color:var(--ink3)}
.adflt009 .path{display:flex;align-items:center;gap:8px;min-height:28px;margin:12px 0 10px;font-size:12px;line-height:18px;color:var(--ink3)}
.adflt009 .path b{font-weight:600;color:var(--ink)}
.adflt009 .path .a-lk{margin-left:auto}
.adflt009 .sl{display:grid;grid-template-columns:repeat(auto-fill,minmax(250px,1fr));gap:10px}
.adflt009 .sc{display:flex;align-items:center;gap:10px;min-width:0;padding:10px 12px;border:1px solid var(--line);border-radius:12px;animation:adtFade .2s}
.adflt009 .sc .a-nm{flex:1}`),
    html: () => `<div class="adflt009"><div class="a-card ov"><div class="rw" data-rw>${dds('p', '省份', Object.keys(REG), '', false)}${dds('c', '请先选择省份', [], '', true)}${dds('d', '请先选择城市', [], '', true)}</div><div class="path" data-path><span>共 ${ST.length} 家门店</span></div><div class="sl" data-list>${ST.slice(0, 6).map(card).join('')}</div></div></div>`,
    js: (root) => {
      const $ = (s) => root.querySelector(s); const s = { p: '', c: '', d: '' }
      const render = () => {
        const rs = run(s), cs = s.p ? Object.keys(REG[s.p]) : [], ds = s.c ? REG[s.p][s.c] : []
        $('[data-rw]').innerHTML = dds('p', '省份', Object.keys(REG), s.p, false) + dds('c', s.p ? '城市' : '请先选择省份', cs, s.c, !s.p) + dds('d', s.c ? '区县' : '请先选择城市', ds, s.d, !s.c)
        const path = [s.p, s.c, s.d].filter(Boolean)
        $('[data-path]').innerHTML = path.length ? `<span>已选</span><b>${path.join(' / ')}</b><span>· 共 ${rs.length} 家门店</span><button class="a-lk" type="button" data-clear>清除地区</button>` : `<span>共 ${ST.length} 家门店</span>`
        $('[data-list]').innerHTML = rs.slice(0, 6).map(card).join('') + (rs.length > 6 ? `<div class="a-ht" style="grid-column:1/-1">仅显示前 6 家，选择更细的地区可缩小范围</div>` : '')
      }
      root.addEventListener('click', (e) => {
        const o = e.target.closest('.menu [data-o]')
        if (o) { const k = o.closest('.a-dd').dataset.key, v = o.dataset.val; if (k === 'p') { s.p = v; s.c = ''; s.d = '' } else if (k === 'c') { s.c = v; s.d = '' } else s.d = v; setTimeout(render, 0); return }
        if (e.target.closest('[data-clear]')) { s.p = s.c = s.d = ''; render() }
      })
      render()
    },
  })
}

/* AD-FLT-010 状态分段筛选 */
{
  const W = [200, 0, 128, 112, 160]
  const PAT = '待发货,待付款,配送中,已完成,待发货,已完成,待发货,配送中,待付款,已完成,已取消,待发货,配送中,已完成,待付款,待发货,退款中,已完成,配送中,待发货,待付款,已完成,配送中,已取消,待发货,已完成,待付款,配送中,退款中,已完成,已取消'.split(',')
  const TONE = Object.fromEntries(ORDER_STATUS)
  const D10 = BIG(31).map((r, i) => Object.assign(r, { st: PAT[i], tone: TONE[PAT[i]] }))
  const ORDER = ['待发货', '退款中', '待付款', '配送中', '已完成', '已取消', '已关闭']
  const cnt = (s) => D10.filter((r) => r.st === s).length
  def({
    id: 'AD-FLT-010', name: '状态分段筛选', style: '带数量角标',
    fit: '订单、工单、线索按状态分流：标签按处理顺序排（待处理 → 进行中 → 完成 → 关闭），每个标签带数量，默认选中最需要处理的“待发货”，“全部”放在末尾；数量为 0 的弱化。',
    avoid: '页面上不要再放同一组数字的统计卡（二选一）；状态超过 7 个把终态收进“更多”；标签数字要和表格实际条数一致；切换后保持滚动与排序。',
    kw: '状态标签 分段 tabs 数量角标 状态筛选 待处理 订单状态 badge 标签页 默认视图',
    wide: true,
    css: B('adflt010', 0, emptyCss('adflt010') + `
.adflt010 .a-tw{max-height:408px;overflow:auto}
.adflt010 thead th{position:sticky;top:0;z-index:2}
.adflt010 .a-tabs{position:relative;display:flex;gap:4px;padding:0 12px;border-bottom:1px solid var(--line);overflow-x:auto}
.adflt010 .a-tabs button{display:inline-flex;align-items:center;gap:8px;height:48px;padding:0 12px;color:var(--ink2);white-space:nowrap;transition:color .15s}
.adflt010 .a-tabs button:hover{color:var(--ink)}
.adflt010 .a-tabs button.on{color:var(--p-text)}
.adflt010 .a-tabs button small{min-width:20px;height:20px;padding:0 6px;border-radius:10px;background:var(--soft);color:var(--ink2);font-size:12px;line-height:20px;text-align:center;font-variant-numeric:tabular-nums}
.adflt010 .a-tabs button.on small{background:var(--pt);color:var(--p-text)}
.adflt010 .a-tabs button.z{color:var(--ink3)}.adflt010 .a-tabs button.z small{background:none;opacity:.6}
.adflt010 .a-tabs .sepv{flex:none;width:1px;height:20px;margin:14px 6px;background:var(--line)}
.adflt010 .ink{position:absolute;left:0;bottom:-1px;height:2px;width:0;border-radius:1px;background:var(--p);transition:left .25s cubic-bezier(.2,0,0,1),width .25s cubic-bezier(.2,0,0,1)}`),
    html: () => `<div class="adflt010"><div class="a-card"><div class="a-tabs" data-ix="tabs" data-list=".adflt010 tbody" role="tablist">${ORDER.map((s) => `<button type="button" data-t="${s}" role="tab" class="${s === '待发货' ? 'on' : ''}${cnt(s) === 0 ? ' z' : ''}" aria-selected="${s === '待发货'}">${s}<small>${cnt(s)}</small></button>`).join('')}<span class="sepv"></span><button type="button" data-t="all" role="tab" aria-selected="false">全部<small>${D10.length}</small></button><i class="ink"></i></div>
<div class="a-tw"><table style="min-width:${sumw(W)}px" data-pagination="none">${cg(W)}<thead><tr><th>客户</th><th>商品</th><th>金额（元）</th><th>状态</th><th>下单时间</th></tr></thead><tbody>${D10.map((r) => `<tr data-k="${r.st}"${r.st === '待发货' ? '' : ' hidden'}><td class="l">${nm(r)}</td><td class="l" title="${r.item}">${r.item}</td><td class="r">${money(r.amt)}</td><td>${stTag(r)}</td><td class="n">${r.date}</td></tr>`).join('')}<tr class="empty" hidden><td colspan="5"><div class="em"><span class="i">${sv('adt_inbox')}</span><b>这个状态下暂时没有订单</b></div></td></tr></tbody></table></div><div class="a-pg"><span data-total>共 ${cnt('待发货')} 条</span></div></div></div>`,
    js: (root) => {
      const upd = () => {
        const rows = [...root.querySelectorAll('tbody tr:not(.empty)')], n = rows.filter((r) => !r.hidden).length
        root.querySelector('tr.empty').hidden = n > 0; root.querySelector('[data-total]').textContent = `共 ${n} 条`
      }
      root.addEventListener('click', (e) => { if (e.target.closest('.a-tabs [data-t]')) setTimeout(upd, 0) })
      upd()
    },
  })
}

guide('ad', 'FLT', [
  ['列表页顶部常用筛选', '行内筛选栏', '搜索框 + 2–3 个最常用条件，输入即查、不放“查询”按钮，只放一个“重置”；默认选中最需要处理的子集'],
  ['条件超过 4 个', '高级筛选', '低频条件收进“更多筛选”，按钮角标提示收起的条件里生效了几项，展开不推动页面'],
  ['按时间看数据', '日期范围快捷选', '快捷项（今天、近 7 天、近 30 天、本月）和自定义日历放进同一个弹层，选中的范围写成完整日期'],
  ['按关键词找东西', '搜索框与联想', '输入联想 + 最近搜索，键盘上下选；结果同时即输即查，没结果给清除入口'],
  ['按状态、标签、分类分流', '状态分段筛选 / 标签筛选', '状态按处理顺序排并带数量角标；互斥维度用分段，可叠加的维度用胶囊多选'],
  ['条件多、要看清结果被谁限制', '已选条件条 / 保存的筛选方案', '已生效条件做成可移除标签并可清空；常用组合存成方案一键套用'],
  ['地区、分类这类上下级条件；调顺序', '级联筛选 / 排序控件', '上级选了下级才可选，改上级就清空下级；排序点一下降序、再点升序、第三下回默认'],
])

})()
