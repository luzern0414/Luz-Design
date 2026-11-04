/* ===== 后台管理 · 导航与页头 / 弹层与反馈 / 状态与结果页（AD-NAV 001-013 · AD-FB 001-010 · AD-STATE 001-006）=====
 * 整份包在一个函数里，避免和别的文件重名；每个块自带完整 CSS（base 公共段 + 自己的段），可单独取用。 */
;(() => {
const $ = (r, s) => r.querySelector(s)
const $$ = (r, s) => [...r.querySelectorAll(s)]
Object.assign(LINE, {
  adshFold: '<rect x="3.5" y="4.5" width="17" height="15" rx="2.5"/><path d="M9.5 4.5v15M16 9.5 13.5 12l2.5 2.5"/>',
  adshUnfold: '<rect x="3.5" y="4.5" width="17" height="15" rx="2.5"/><path d="M9.5 4.5v15M13 9.5l2.5 2.5-2.5 2.5"/>',
  adshHelp: '<circle cx="12" cy="12" r="8.5"/><path d="M9.5 9.5a2.5 2.5 0 1 1 3.5 2.3c-.7.4-1 1-1 1.7M12 16.5v.01"/>',
  adshStore: '<path d="M4 9.5 5.5 4.5h13L20 9.5M4 9.5a2.5 2.5 0 0 0 4 1.8 2.5 2.5 0 0 0 4 0 2.5 2.5 0 0 0 4 0 2.5 2.5 0 0 0 4-1.8M5.5 12v8h13v-8M10 20v-4.5h4V20"/>',
  adshInbox: '<path d="M4 13.5 6.5 5h11l2.5 8.5V19H4zM4 13.5h4.5a3.5 3.5 0 0 0 7 0H20"/>',
  adshWifiOff: '<path d="M3 3l18 18M8.5 16a5 5 0 0 1 7 0M5 12.5a10 10 0 0 1 3-2M19 12.5a10 10 0 0 0-5.5-2.8M2 9a15 15 0 0 1 4-2.5M22 9a15 15 0 0 0-8.5-3.8M12 20v.01"/>',
  adshExt: '<path d="M14 4.5h5.5V10M19.5 4.5 11 13M17 14v4.5a1.5 1.5 0 0 1-1.5 1.5h-9A1.5 1.5 0 0 1 5 18.5v-9A1.5 1.5 0 0 1 6.5 8H11"/>',
  adshBan: '<circle cx="12" cy="12" r="8.5"/><path d="m6 6 12 12"/>',
  adshDesk: '<rect x="3.5" y="4.5" width="17" height="12" rx="2"/><path d="M9 20h6M12 16.5V20"/>',
  adshSwap: '<path d="M7 7h12l-3-3M17 17H5l3 3"/>',
  adshSearchOff: '<circle cx="11" cy="11" r="6.5"/><path d="m20.5 20.5-4.7-4.7M8.5 8.5l5 5M13.5 8.5l-5 5"/>',
  adshServer: '<rect x="4" y="4" width="16" height="6.5" rx="2"/><rect x="4" y="13.5" width="16" height="6.5" rx="2"/><path d="M8 7.2h.01M8 16.8h.01M14 7.2h3M14 16.8h3"/>',
  adshUp2: '<path d="M12 19V6M6 11l6-6 6 6M5 20h14"/>',
  adshBook: '<path d="M5 4.5h10a3 3 0 0 1 3 3V20H8a3 3 0 0 1-3-3zM8 17h10"/>',
  adshTarget: '<circle cx="12" cy="12" r="8.5"/><circle cx="12" cy="12" r="4.5"/><circle cx="12" cy="12" r="1"/>',
})
const I = (n, c = '') => `<span class="ic ${c}">${sv(n)}</span>`
const TONE_IC = { ok: 'checkc', wn: 'alert', dg: 'closec', in: 'info' }

/* ---------- 公共 CSS：按钮、标签、输入、旋转、轻提示。§ 代表本块根类名 ---------- */
const base = (p) => `
.${p}{--bd:var(--n7);--bd2:var(--n5);--okb:var(--ok-bg);--wn:var(--warn);--wnb:var(--warn-bg);--dg:var(--danger);--dgb:var(--danger-bg);--mu:var(--neutral);--mub:var(--neutral-bg);--e:cubic-bezier(.2,0,0,1);--sh:0 1px 2px var(--sh05),0 4px 14px var(--sh06);--sh2:0 2px 6px var(--sh06),0 12px 32px var(--sh16);position:relative;width:100%;font-size:14px;line-height:1.5;color:var(--ink);text-align:left}
.ixr:has(>.${p}){width:100%}
.${p} *{box-sizing:border-box}
.${p} button{font:inherit;color:inherit;cursor:pointer;border:0;background:none;padding:0;text-align:inherit}
.${p} button:focus{outline:none}
.${p} button:focus-visible{outline:1px solid var(--ink2);outline-offset:2px}
.${p} .pn:focus{outline:none}
.${p} .ic{display:inline-flex;width:16px;height:16px;flex:none}
.${p} .bt{display:inline-flex;align-items:center;justify-content:center;gap:6px;height:32px;padding:0 14px;border:1px solid var(--bd);border-radius:8px;background:var(--card);color:var(--ink);white-space:nowrap;transition:background-color .15s var(--e),border-color .15s var(--e),color .15s var(--e)}
.${p} .bt:hover{background:var(--bg)}
.${p} .bt.lg{height:36px;padding:0 16px}
.${p} .bt.pri{background:var(--p);border-color:var(--p);color:#fff}
.${p} .bt.pri:hover{background:var(--pd);border-color:var(--pd)}
.${p} .bt.dng{background:var(--danger-fill);border-color:var(--dg);color:#fff}
.${p} .bt.dng:hover{background:color-mix(in srgb,var(--danger-fill) 85%,#000);border-color:color-mix(in srgb,var(--danger-fill) 85%,#000)}
.${p} .bt.txt{border-color:transparent;background:none;padding:0 8px;color:var(--p-text)}
.${p} .bt.txt:hover{background:var(--pt)}
.${p} .bt.txt.dg{color:var(--dg)}.${p} .bt.txt.dg:hover{background:var(--dgb)}
.${p} .bt.ib{width:32px;padding:0;color:var(--ink2)}
.${p} .bt:disabled,.${p} .bt.dis,.${p} .bt:disabled:hover,.${p} .bt.dis:hover{background:var(--mub);border-color:var(--mub);color:var(--ink4);cursor:not-allowed}
.${p} .tg2{display:inline-flex;align-items:center;gap:4px;height:22px;padding:0 8px;border-radius:4px;font-size:12px;line-height:1;white-space:nowrap;background:var(--mub);color:var(--mu)}
.${p} .tg2.ok{background:var(--okb);color:var(--ok)}.${p} .tg2.wn{background:var(--wnb);color:var(--wn)}.${p} .tg2.dg{background:var(--dgb);color:var(--dg)}.${p} .tg2.in{background:var(--pt);color:var(--p-text)}
.${p} .ip{display:block;width:100%;height:36px;padding:0 12px;border:1px solid var(--bd);border-radius:8px;background:var(--card);font:inherit;color:var(--ink);outline:none;transition:border-color .15s var(--e)}
.${p} .ip::placeholder{color:var(--ink3)}
.${p} .ip:focus{border-color:var(--ink2)}
.${p} textarea.ip{height:auto;padding:8px 12px;resize:none;line-height:1.5}
.${p} .kb{display:inline-flex;align-items:center;height:20px;padding:0 6px;border-radius:4px;border:1px solid var(--bd);background:var(--card);font-size:12px;line-height:1;color:var(--ink3)}
.${p} .spn{display:inline-block;width:16px;height:16px;border:2px solid currentColor;border-right-color:transparent;border-radius:50%;animation:${p}-spin .7s linear infinite;flex:none}
.${p} .sk{display:block;height:10px;border-radius:4px;background:var(--n5)}
.${p} .pop{position:absolute;display:none;z-index:25}
.${p} .pop.open{display:block;animation:${p}-in .16s var(--e)}
.${p} .sayw{position:absolute;left:0;right:0;top:12px;z-index:80;display:flex;flex-direction:column;align-items:center;gap:8px;pointer-events:none}
.${p} .say{display:flex;align-items:center;gap:8px;max-width:calc(100% - 32px);padding:9px 14px;border-radius:8px;background:var(--card);border:1px solid var(--bd2);box-shadow:var(--sh2);animation:${p}-in .2s var(--e)}
.${p} .say.ok .ic{color:var(--ok)}.${p} .say.wn .ic{color:var(--wn)}.${p} .say.dg .ic{color:var(--dg)}.${p} .say.in .ic{color:var(--p-text)}
.${p} .ix-ov{align-items:center;justify-content:center;padding:16px}
.${p} .ix-ov.show .pn{animation:${p}-pop .2s var(--e)}
@keyframes ${p}-spin{to{transform:rotate(360deg)}}
@keyframes ${p}-in{from{opacity:0;transform:translateY(-6px)}}
@keyframes ${p}-pop{from{opacity:0;transform:translateY(10px) scale(.98)}}
@media(prefers-reduced-motion:reduce){.${p} *{animation-duration:1ms!important;transition-duration:1ms!important}}
`
const C = (p, s) => base(p) + s.replace(/§/g, '.' + p)

/* ---------- 公共脚本 ---------- */
const say = (root, text, kind = 'ok', ms = 2400) => {
  const host = $(root, '[data-sh]') || root
  let w = $(host, ':scope > .sayw'); if (!w) { w = document.createElement('div'); w.className = 'sayw'; host.appendChild(w) }
  const d = document.createElement('div'); d.className = 'say ' + kind; d.setAttribute('role', kind === 'dg' ? 'alert' : 'status')
  d.innerHTML = `${I(TONE_IC[kind])}<span>${text}</span>`; w.appendChild(d); setTimeout(() => d.remove(), ms); return d
}
/* 气泡：[data-pop="名"] 触发，.pop[data-pn="名"] 面板；点外面、Esc 关闭 */
const pops = (root) => {
  const closeAll = (except) => $$(root, '.pop.open').forEach((p) => { if (p !== except) { p.classList.remove('open'); const t = $(root, `[data-pop="${p.dataset.pn}"]`); if (t) t.setAttribute('aria-expanded', 'false') } })
  root.addEventListener('click', (e) => {
    const t = e.target.closest('[data-pop]')
    if (t) { const p = $(root, `.pop[data-pn="${t.dataset.pop}"]`); if (!p) return; const open = !p.classList.contains('open'); closeAll(p); p.classList.toggle('open', open); t.setAttribute('aria-expanded', open); return }
    if (!e.target.closest('.pop, [data-keep]')) closeAll()
  })
  const off = (e) => { if (!root.isConnected) { document.removeEventListener('pointerdown', off, true); return } if (!root.contains(e.target)) closeAll() }
  document.addEventListener('pointerdown', off, true)
  root.addEventListener('keydown', (e) => { if (e.key === 'Escape') closeAll() })
  return closeAll
}
/* 居中弹层：打开后聚焦、Esc 关闭并还焦点、Tab 在弹层内循环 */
const FOCUSABLE = 'button:not(:disabled),input:not(:disabled),textarea:not(:disabled),[tabindex]:not([tabindex="-1"]),a[href]'
const overlays = (root) => {
  root.addEventListener('click', (e) => {
    const o = e.target.closest('[data-open]'); if (!o) return
    const ov = $(root, `[data-ov="${o.dataset.open}"]`); if (!ov) return
    ov.__from = o; setTimeout(() => { const f = $(ov, '[data-autofocus]') || $(ov, '.pn'); if (f) f.focus({ preventScroll: true }) }, 30)
  })
  root.addEventListener('keydown', (e) => {
    const ov = $(root, '.ix-ov.show'); if (!ov) return
    if (e.key === 'Escape') { if (ov.__esc && ov.__esc(e) === false) return; ov.classList.remove('show'); if (ov.__from) ov.__from.focus({ preventScroll: true }); e.stopPropagation(); return }
    if (e.key === 'Tab') {
      const fs = $$(ov, FOCUSABLE).filter((x) => x.offsetParent !== null); if (!fs.length) return
      const a = document.activeElement
      if (e.shiftKey && (a === fs[0] || a === $(ov, '.pn'))) { e.preventDefault(); fs[fs.length - 1].focus() }
      else if (!e.shiftKey && a === fs[fs.length - 1]) { e.preventDefault(); fs[0].focus() }
    }
  })
}
const closeOv = (ov) => { ov.classList.remove('show'); if (ov.__from) ov.__from.focus({ preventScroll: true }) }

/* ======================================================================
   一、导航与页头 AD-NAV
   ====================================================================== */
/* 侧栏菜单（浅色 001 / 深色 002 共用结构）。分组只在组内两项及以上时才有标题；页面标题不重复菜单名 */
const MENU = [
  { k: 'dash', t: '数据概览', i: 'dashboard' },
  { g: '交易', items: [
    { t: '订单管理', i: 'receipt', open: 1, cur: 1, sub: [['ord-list', '订单列表', 1], ['ord-ship', '发货管理'], ['ord-ref', '售后处理']] },
    { t: '商品管理', i: 'box', sub: [['g-list', '商品列表'], ['g-cat', '分类管理'], ['g-stock', '库存预警']] }] },
  { g: '会员营销', items: [
    { k: 'mem', t: '会员管理', i: 'users' }, { k: 'cpn', t: '优惠券', i: 'coupon' }, { k: 'act', t: '活动配置', i: 'fire' }] },
  { g: '系统', items: [
    { k: 'store', t: '门店设置', i: 'adshStore' },
    { t: '员工权限', i: 'shield', sub: [['st-acc', '员工账号'], ['st-role', '角色权限']] },
    { k: 'log', t: '操作日志', i: 'file' }] },
]
const menuItem = (m) => m.sub
  ? `<div class="ix-ai${m.open ? ' open' : ''}"><button type="button" class="it${m.cur ? ' cur' : ''}" data-h aria-expanded="${!!m.open}"><span class="ic">${sv(m.i)}</span><span class="tx">${m.t}</span><span class="ic chev">${sv('down')}</span></button><div class="ix-ab"><div><div class="sub"><div class="fh">${m.t}</div>${m.sub.map(([k, t, on]) => `<button type="button" class="si${on ? ' on' : ''}" data-k="${k}">${t}</button>`).join('')}</div></div></div></div>`
  : `<button type="button" class="it${m.on ? ' on' : ''}" data-k="${m.k}" data-tip="${m.t}"><span class="ic">${sv(m.i)}</span><span class="tx">${m.t}</span></button>`
const sideHTML = (p) => `<div class="${p}" data-sh><div class="sh">
  <aside class="side" aria-label="主菜单"><div class="br"><span class="logo">${sv('grid2')}</span><b class="tx">云店管理</b></div>
    <nav class="nv" data-ix="acc" data-single>${MENU.map((m) => m.g ? `<div class="gt">${m.g}</div>${m.items.map(menuItem).join('')}` : menuItem({ ...m, on: 0 })).join('')}</nav>
    <div class="ft"><button type="button" class="fold" aria-label="收起菜单" aria-expanded="true" data-tip="展开菜单"><span class="ic">${sv('adshFold')}</span><span class="tx">收起菜单</span></button>
      <div class="vw"><button type="button" class="ver version-btn" data-pop="ver" aria-expanded="false"><span class="tx">前端 2.4.1 · 后端 2.4.0</span><span class="vs">2.4</span></button>
        <div class="pop vp version-pop" data-pn="ver"><b>当前版本</b><dl><dt>前端</dt><dd>2.4.1</dd><dt>后端</dt><dd>2.4.0</dd><dt>上线日期</dt><dd>2026-11-02</dd><dt>运行环境</dt><dd>生产环境</dd></dl><div class="nt"><em>本次更新</em><span>订单列表支持按门店筛选</span><span>修复导出文件日期格式错误</span></div></div></div></div>
  </aside>
  <div class="cnt"><div class="tbr"><span class="fakein">${I('search')}搜索名称或编号</span><span class="sp"></span><span class="bt pri">新建</span></div>
    <div class="card">${[0, 1, 2, 3, 4].map((i) => `<div class="row">${critter(i, 28)}<div class="ln"><i class="sk" style="width:${[46, 38, 52, 34, 44][i]}%"></i><i class="sk s" style="width:${[28, 22, 30, 18, 26][i]}%"></i></div><i class="sk t"></i></div>`).join('')}</div></div>
</div></div>`
const sideCSS = (p, dark) => C(p, `
§ .sh{display:flex;min-height:470px;min-width:500px;border:1px solid var(--bd2);border-radius:12px;background:var(--bg)}
§ .side{--sb:${dark ? '#1E2329' : 'var(--card)'};--sf:${dark ? '#B9C0CA' : 'var(--ink2)'};--sh1:${dark ? 'rgba(255,255,255,.06)' : 'var(--n3)'};--sob:${dark ? 'rgba(255,255,255,.10)' : 'var(--pt)'};--sof:${dark ? '#fff' : 'var(--p-text)'};--sgt:${dark ? '#8A919C' : 'var(--ink3)'};--sfl:${dark ? '#2A3038' : 'var(--card)'};--sln:${dark ? 'rgba(255,255,255,.12)' : 'var(--line)'};position:relative;width:220px;flex:none;display:flex;flex-direction:column;padding:12px;background:var(--sb);border-radius:11px 0 0 11px;border-right:1px solid var(--sln);transition:width .2s var(--e)}
§ .side.col{width:64px}
§ .br{display:flex;align-items:center;gap:10px;height:40px;padding:0 6px;margin-bottom:6px;color:${dark ? '#fff' : 'var(--ink)'}}
§ .br b{font-size:16px;font-weight:600;white-space:nowrap}
§ .logo{display:flex;align-items:center;justify-content:center;width:28px;height:28px;border-radius:8px;background:var(--p);color:#fff;flex:none}
§ .logo svg{width:16px;height:16px}
§ .nv{flex:1}
§ .it,§ .fold{position:relative;display:flex;align-items:center;gap:10px;width:100%;height:40px;padding:0 12px;border-radius:8px;color:var(--sf);transition:background-color .15s var(--e),color .15s var(--e)}
§ .it .ic,§ .fold .ic{width:18px;height:18px}
§ .it .tx{flex:1;white-space:nowrap}
§ .it:hover,§ .fold:hover,§ .si:hover{background:var(--sh1)}
§ .it.on{background:var(--sob);color:var(--sof);font-weight:600${dark ? ';box-shadow:inset 3px 0 0 var(--pm)' : ''}}
§ .it.cur{color:var(--sof);font-weight:600}
§ .chev{width:16px!important;height:16px!important;transition:transform .2s var(--e)}
§ .ix-ai.open>.it .chev{transform:rotate(180deg)}
§ .gt{padding:16px 12px 6px;font-size:12px;color:var(--sgt)}
§ .sub{position:relative;margin:2px 0 4px 21px;padding-left:12px}
§ .sub::before{content:"";position:absolute;left:0;top:4px;bottom:4px;width:1px;background:var(--sln)}
§ .fh{display:none}
§ .si{display:block;width:100%;height:36px;padding:0 12px;border-radius:8px;color:var(--sf);white-space:nowrap;transition:background-color .15s var(--e)}
§ .si.on{background:var(--sob);color:var(--sof);font-weight:600${dark ? ';box-shadow:inset 3px 0 0 var(--pm)' : ''}}
§ .ft{margin-top:8px;padding-top:8px;border-top:1px solid var(--sln)}
§ .fold .tx{white-space:nowrap}
§ .vw{position:relative}
§ .ver{display:flex;align-items:center;width:100%;height:32px;padding:0 12px;border-radius:8px;font-size:12px;color:var(--sgt);white-space:nowrap}
§ .ver:hover{background:var(--sh1)}
§ .vs{display:none}
§ .vp{left:0;bottom:calc(100% + 8px);width:268px;padding:14px 16px;border-radius:12px;background:var(--card);color:var(--ink);border:1px solid var(--bd2);box-shadow:var(--sh2);z-index:40}
§ .vp b{font-weight:600}
§ .vp dl{display:grid;grid-template-columns:auto 1fr;gap:4px 14px;margin:8px 0 10px;font-size:13px}
§ .vp dt{color:var(--ink3)}§ .vp dd{margin:0;text-align:right}
§ .vp .nt{display:flex;flex-direction:column;gap:2px;padding-top:10px;border-top:1px solid var(--line);font-size:12px;color:var(--ink2)}
§ .vp .nt em{font-size:12px;color:var(--ink3)}
§ .col .br{justify-content:center;padding:0}
§ .col .tx,§ .col .chev{display:none}
§ .col .it,§ .col .fold{justify-content:center;padding:0}
§ .col .gt{height:1px;margin:10px 14px;padding:0;font-size:0;background:var(--sln)}
§ .col .ver{justify-content:center;padding:0}
§ .col .vs{display:inline}
§ .col .vp{left:0}
§ .col .ix-ai{position:relative}
§ .col .ix-ai>.ix-ab{display:none;position:absolute;left:100%;top:0;z-index:30;min-width:184px;padding-left:12px}
§ .col .ix-ai:hover>.ix-ab,§ .col .ix-ai:focus-within>.ix-ab{display:block}
§ .col .ix-ab>div{overflow:visible}
§ .col .sub{margin:0;padding:6px;border-radius:8px;background:var(--sfl);border:1px solid var(--sln);box-shadow:var(--sh2)}
§ .col .sub::before{display:none}
§ .col .fh{display:block;padding:6px 12px 4px;font-size:12px;color:var(--sgt)}
§ .col .it[data-tip]:not([data-h]):hover::after{content:attr(data-tip);position:absolute;left:calc(100% + 10px);top:50%;transform:translateY(-50%);z-index:35;padding:5px 10px;border-radius:4px;background:var(--inv);color:#fff;font-size:12px;line-height:1.4;white-space:nowrap;pointer-events:none}
§ .col .fold::after{content:attr(data-tip);position:absolute;left:calc(100% + 10px);top:50%;transform:translateY(-50%);z-index:35;padding:5px 10px;border-radius:4px;background:var(--inv);color:#fff;font-size:12px;line-height:1.4;white-space:nowrap;pointer-events:none;display:none}
§ .col .fold:hover::after{display:block}
§ .cnt{flex:1;min-width:0;padding:16px}
§ .tbr{display:flex;align-items:center;gap:10px;margin-bottom:12px}
§ .sp{flex:1}
§ .fakein{display:flex;align-items:center;gap:8px;width:200px;max-width:100%;height:36px;padding:0 12px;border:1px solid var(--bd);border-radius:8px;background:var(--card);color:var(--ink3);white-space:nowrap}
§ .tbr .bt{height:36px;cursor:default}
§ .card{background:var(--card);border:1px solid var(--bd2);border-radius:12px;padding:4px 16px}
§ .row{display:flex;align-items:center;gap:12px;height:52px;border-bottom:1px solid var(--line)}
§ .row:last-child{border-bottom:0}
§ .ln{flex:1;display:flex;flex-direction:column;gap:6px}
§ .ln .sk.s{height:8px;background:var(--n4)}
§ .sk.t{width:44px;height:20px}
`)
const sideJs = (root) => {
  const side = $(root, '.side'); const closeP = pops(root)
  root.addEventListener('click', (e) => {
    const k = e.target.closest('.it[data-k], .si')
    if (k) {
      $$(root, '.it.on,.si.on').forEach((x) => x.classList.remove('on')); k.classList.add('on')
      $$(root, '.it.cur').forEach((x) => x.classList.remove('cur')); const g = k.closest('.ix-ai'); if (g) $(g, '.it[data-h]').classList.add('cur')
      return
    }
    const f = e.target.closest('.fold')
    if (f) { const c = side.classList.toggle('col'); f.setAttribute('aria-expanded', !c); f.setAttribute('aria-label', c ? '展开菜单' : '收起菜单'); const ic = $(f, '.ic'); ic.innerHTML = sv(c ? 'adshUnfold' : 'adshFold'); closeP() }
  })
}
def({
  id: 'AD-NAV-001', name: '侧栏菜单·浅色', style: '可收起', stage: '', wide: false,
  fit: '后台默认主导航：一级菜单带线性图标、二级可展开、当前页高亮，收起后只剩图标栏，悬停出二级飞出菜单；底部写前后端版本，点开看上线日期与更新说明。',
  avoid: '菜单超过 8 个一级项时先按业务域分组；分组内只有一项时不要给分组标题；顶部不要再放与高亮菜单同名的大标题。',
  kw: 'sidebar menu 侧栏 侧边栏 菜单 导航 收起 折叠 二级菜单 浅色 版本信息 admin nav',
  css: sideCSS('adnav001', false), html: () => sideHTML('adnav001'), js: sideJs,
})
def({
  id: 'AD-NAV-002', name: '侧栏菜单·深色', style: '深底可收起', stage: '', wide: false,
  fit: '数据密集的运营后台、带品牌色顶栏的系统，深色侧栏让内容区更突出；交互与浅色版一致，高亮项用主题浅色做左侧标记。',
  avoid: '给浅色为基准的系统硬配深色侧栏会割裂；强调色只用主题浅阶，别另加鲜艳色；深色模式整页主题另走深色令牌。',
  kw: 'sidebar dark 深色侧栏 暗色 菜单 导航 收起 二级菜单 运营后台',
  css: sideCSS('adnav002', true), html: () => sideHTML('adnav002'), js: sideJs,
})

/* ---- 共用片段：下拉菜单、消息列表、用户菜单、假页面 ---- */
const MENU_CSS = `
§ .pw{position:relative;display:inline-flex}
§ .mn{min-width:160px;padding:6px;border-radius:12px;background:var(--card);border:1px solid var(--bd2);box-shadow:var(--sh2)}
§ .mn .mi2,§ .mi2{display:flex;align-items:center;gap:10px;width:100%;height:36px;padding:0 10px;border-radius:8px;color:var(--ink);white-space:nowrap;transition:background-color .15s var(--e)}
§ .mi2 .ic{color:var(--ink2)}
§ .mi2:hover{background:var(--bg)}
§ .mi2.on{color:var(--p-text);font-weight:600}
§ .mi2 .val{margin-left:auto;font-size:12px;color:var(--ink3)}
§ .mi2 .ck{margin-left:auto;color:var(--p-text);opacity:0}
§ .mi2.on .ck{opacity:1}
§ .mi2.dg,§ .mi2.dg .ic{color:var(--dg)}
§ .mi2.dg:hover{background:var(--dgb)}
§ .hr{height:1px;margin:6px 4px;background:var(--line)}
`
const FP_CSS = `
§ .fp{display:flex;flex-direction:column;gap:12px;padding:16px;background:var(--bg)}
§ .fp .cd{background:var(--card);border:1px solid var(--bd2);border-radius:12px;padding:14px 16px}
§ .fp .g3{display:grid;grid-template-columns:repeat(3,1fr);gap:12px}
§ .fp .st3{display:flex;flex-direction:column;gap:8px}
§ .fp .st3 .sk:first-child{height:8px;width:40%;background:var(--n4)}
§ .fp .st3 .sk:last-child{height:20px;width:60%}
`
const fauxPage = (rows = 4) => `<div class="fp"><div class="g3">${[0, 1, 2].map(() => '<div class="cd st3"><i class="sk"></i><i class="sk"></i></div>').join('')}</div><div class="cd">${Array.from({ length: rows }, (_, i) => `<div class="frow"><i class="sk" style="width:${[22, 30, 18, 26, 20][i % 5]}%"></i><i class="sk" style="width:${[38, 30, 44, 34, 40][i % 5]}%"></i><i class="sk" style="width:48px"></i></div>`).join('')}</div></div>`
const FROW_CSS = `§ .frow{display:flex;align-items:center;justify-content:space-between;gap:16px;height:40px;border-bottom:1px solid var(--line)}§ .frow:last-child{border-bottom:0}`

const MSGS = [
  { k: 'n', t: '库存预警', d: '保温水杯（鼠尾草绿 500ml）库存仅剩 12 件，低于预警值 20 件', ago: '10 分钟前', tone: 'wn', i: 'alert', u: 1 },
  { k: 'n', t: '客户申请退款', d: '订单 SO2026110528 申请退款 ¥599.00，原因：商品与描述不符', ago: '32 分钟前', tone: 'dg', i: 'receipt', u: 1 },
  { k: 'n', t: '系统维护通知', d: '系统将于 11-06 02:00–03:00 进行例行维护，期间订单与支付功能暂不可用，请提前调整门店营业安排', ago: '昨天 18:20', tone: 'in', i: 'server', u: 0 },
  { k: 'n', t: '导出完成', d: '「10 月订单明细」已生成，可在导出记录中下载，文件 7 天后自动清理', ago: '昨天 09:41', tone: 'ok', i: 'download', u: 0 },
  { k: 't', t: '3 张优惠券待审核', d: '春季焕新满减券等 3 张券已提交审核，请在 24 小时内处理', ago: '今天 09:05', tone: 'in', i: 'coupon', u: 1 },
  { k: 't', t: '排班调整申请', d: '周一帆申请将 11-08（周六）的早班调换为晚班', ago: '今天 08:30', tone: 'wn', i: 'calendar', u: 1 },
  { k: 't', t: '本周盘点单待确认', d: '仓储部已提交 11-03 盘点单，差异 2 项', ago: '昨天 17:00', tone: 'in', i: 'clipboard', u: 0 },
]
const MSG_CSS = `
§ .mp{width:380px;max-width:calc(100vw - 32px);padding:0;overflow:hidden}
§ .mh{display:flex;align-items:center;gap:10px;height:48px;padding:0 8px 0 16px;border-bottom:1px solid var(--line)}
§ .mh b{flex:1;font-weight:600;font-size:16px}
§ .mtabs{display:flex;gap:4px;padding:8px 12px 0;border-bottom:1px solid var(--line)}
§ .mtabs button{position:relative;display:inline-flex;align-items:center;gap:6px;height:36px;padding:0 10px;color:var(--ink2)}
§ .mtabs button span{display:inline-flex;flex-direction:column}
§ .mtabs button span::after{content:attr(data-w);height:0;overflow:hidden;visibility:hidden;font-weight:600}
§ .mtabs button em{min-width:20px;height:18px;padding:0 5px;border-radius:9px;background:var(--mub);color:var(--ink2);font-size:12px;line-height:18px;text-align:center}
§ .mtabs button.on{color:var(--p-text);font-weight:600}
§ .mtabs button.on em{background:var(--pt);color:var(--p-text)}
§ .mtabs button.on::after{content:"";position:absolute;left:10px;right:10px;bottom:-1px;height:2px;background:var(--p)}
§ .ml{list-style:none;margin:0;padding:0;max-height:300px;overflow:auto}
§ .mi{position:relative;display:flex;gap:12px;padding:12px 16px;cursor:pointer;border-bottom:1px solid var(--line);transition:background-color .15s var(--e)}
§ .mi:last-child{border-bottom:0}
§ .mi:hover{background:var(--bg)}
§ .mi:focus-visible{outline:1px solid var(--ink2);outline-offset:-2px}
§ .mti{display:flex;align-items:center;justify-content:center;width:32px;height:32px;border-radius:8px;flex:none;background:var(--pt);color:var(--p-text)}
§ .mti.wn{background:var(--wnb);color:var(--wn)}§ .mti.dg{background:var(--dgb);color:var(--dg)}§ .mti.ok{background:var(--okb);color:var(--ok)}
§ .mb{flex:1;min-width:0}
§ .mb b{display:block;font-weight:400;color:var(--ink2)}
§ .mi.un .mb b{font-weight:600;color:var(--ink)}
§ .mb p{margin:2px 0 4px;font-size:13px;line-height:1.5;color:var(--ink2);display:-webkit-box;-webkit-line-clamp:2;-webkit-box-orient:vertical;overflow:hidden}
§ .mb time{font-size:12px;color:var(--ink3)}
§ .ud{position:absolute;right:16px;top:18px;width:8px;height:8px;border-radius:50%;background:var(--danger-fill);opacity:0;transition:opacity .2s var(--e)}
§ .mi.un .ud{opacity:1}
§ .mi.un .mb b{padding-right:16px}
§ .em{display:flex;flex-direction:column;align-items:center;gap:6px;padding:36px 16px;color:var(--ink3);text-align:center}
§ .em .ic{width:36px;height:36px;color:var(--ink6)}
§ .mf{display:flex;border-top:1px solid var(--line)}
§ .mf button{flex:1;height:44px;color:var(--p-text);text-align:center}
§ .mf button:hover{background:var(--pt)}
§ .dot{position:absolute;right:-4px;top:-4px;min-width:16px;height:16px;padding:0 4px;border-radius:8px;background:var(--danger-fill);color:#fff;font-size:12px;line-height:16px;text-align:center;font-style:normal}
§ .bell{position:relative}
`
const msgItems = (tabs) => MSGS.filter((m) => tabs || m.k === 'n').map((m) => `<li class="mi${m.u ? ' un' : ''}" data-k="${m.k}" tabindex="0" role="button"><span class="mti ${m.tone}">${I(m.i)}</span><div class="mb"><b>${m.t}</b><p>${m.d}</p><time>${m.ago}</time></div><i class="ud"></i></li>`).join('')
const msgPanel = (tabs) => `<div class="mh"><b>消息</b><button type="button" class="bt txt" data-readall>全部已读</button></div>
  ${tabs ? `<div class="mtabs" role="tablist">${[['n', '通知'], ['t', '待办'], ['m', '私信']].map(([k, t], i) => `<button type="button" role="tab" data-t="${k}" class="${i ? '' : 'on'}"><span data-w="${t}">${t}</span><em data-n="${k}">0</em></button>`).join('')}</div>` : ''}
  <ul class="ml">${msgItems(tabs)}</ul>
  <div class="em" hidden>${I('adshInbox')}<span data-emt>暂无消息</span></div>
  <div class="mf"><button type="button" data-toast="已打开：全部消息">查看全部消息</button></div>`
/* 消息中心逻辑：tab 过滤、点条目标已读、全部已读、红点数量联动 */
const msgHook = (root, badge) => {
  let tab = $(root, '.mtabs') ? 'n' : null
  const render = () => {
    const items = $$(root, '.mi')
    items.forEach((it) => { it.hidden = tab ? it.dataset.k !== tab : false })
    const vis = items.filter((it) => !it.hidden)
    const unread = items.filter((it) => it.classList.contains('un')).length
    $$(root, '.mtabs [data-n]').forEach((n) => { const c = items.filter((it) => it.dataset.k === n.dataset.n && it.classList.contains('un')).length; n.textContent = c })
    if (badge) { const b = $(root, '.dot'); if (b) { b.textContent = unread; b.hidden = unread === 0 } }
    const ra = $(root, '[data-readall]'); if (ra) ra.disabled = unread === 0
    const em = $(root, '.em'), ul = $(root, '.ml')
    if (em) { em.hidden = vis.length > 0; ul.hidden = vis.length === 0; const t = $(em, '[data-emt]'); if (t) t.textContent = tab === 'm' ? '暂无私信' : '暂无消息' }
  }
  root.addEventListener('click', (e) => {
    const t = e.target.closest('.mtabs [data-t]'); if (t) { tab = t.dataset.t; $$(root, '.mtabs [data-t]').forEach((x) => { x.classList.toggle('on', x === t); x.setAttribute('aria-selected', x === t) }); render(); return }
    const it = e.target.closest('.mi'); if (it) { it.classList.remove('un'); render(); return }
    if (e.target.closest('[data-readall]')) { $$(root, '.mi.un').forEach((x) => x.classList.remove('un')); render(); say(root, '已全部标为已读', 'ok') }
  })
  root.addEventListener('keydown', (e) => { if ((e.key === 'Enter' || e.key === ' ') && e.target.classList && e.target.classList.contains('mi')) { e.preventDefault(); e.target.click() } })
  render()
}
const userPanel = (o = {}) => `<div class="um">
  <div class="uh">${critter(0, 44)}<div class="ui"><div class="unm"><b>林小满</b><span class="tg2 in">店长</span></div><p>旗舰店 · 138****2086</p></div></div>
  <div class="ul">
    <button type="button" class="mi2" data-toast="打开：个人资料">${I('user')}个人资料</button>
    <button type="button" class="mi2" data-toast="打开：修改密码">${I('key')}修改密码</button>
    ${o.store ? `<button type="button" class="mi2" data-sw aria-expanded="false">${I('adshSwap')}切换门店<span class="val" data-cur>旗舰店</span>${I('down')}</button><div class="sl" hidden>${['旗舰店', '中心城店', '星湖街店'].map((s, i) => `<button type="button" class="mi2${i ? '' : ' on'}" data-st="${s}">${s}<span class="ic ck">${sv('check')}</span></button>`).join('')}</div>` : ''}
    <div class="ap"><span class="al">${I('sun')}外观</span><div class="sgm" data-ix="radio" role="radiogroup">${['跟随系统', '浅色', '深色'].map((t, i) => `<button type="button" data-o="${t}" class="${i ? '' : 'on'}" role="radio">${t}</button>`).join('')}</div></div>
    <button type="button" class="mi2" data-toast="已在新窗口打开帮助中心">${I('adshHelp')}帮助中心<span class="ic val">${sv('adshExt')}</span></button>
  </div>
  <div class="uf"><button type="button" class="mi2 dg" data-out>${I('logout')}退出登录</button></div>
  <div class="lg">上次登录 今天 09:12 · 192.168.1.8</div>
  <div class="bye" hidden>${I('checkc')}<b>已安全退出</b><span>未提交的表单草稿已保留在本机</span><button type="button" class="bt pri" data-back>重新登录</button></div>
</div>`
const USER_CSS = `
§ .um{width:288px;position:relative}
§ .uh{display:flex;align-items:center;gap:12px;padding:12px 10px 12px}
§ .ui{min-width:0}
§ .unm{display:flex;align-items:center;gap:8px}
§ .unm b{font-weight:600;font-size:16px}
§ .ui p{margin:2px 0 0;font-size:13px;color:var(--ink3)}
§ .ul{padding:6px 0;border-top:1px solid var(--line)}
§ .sl{margin:2px 0 4px 26px;padding-left:8px;border-left:1px solid var(--line)}
§ .ap{display:flex;align-items:center;gap:10px;min-height:44px;padding:4px 10px;color:var(--ink)}
§ .al{display:flex;align-items:center;gap:10px;flex:none;color:var(--ink)}
§ .al .ic{color:var(--ink2)}
§ .sgm{display:flex;margin-left:auto;padding:2px;border-radius:8px;background:var(--mub)}
§ .sgm button{height:28px;padding:0 8px;border-radius:4px;font-size:12px;color:var(--ink2);transition:background-color .15s var(--e)}
§ .sgm button.on{background:var(--lift);color:var(--ink);box-shadow:0 1px 3px var(--sh12)}
§ .uf{padding-top:6px;border-top:1px solid var(--line)}
§ .lg{padding:6px 10px 4px;font-size:12px;color:var(--ink3)}
§ .cf{padding:8px 10px;border-radius:8px;background:var(--dgb);font-size:13px;color:var(--ink)}
§ .cf p{margin:0 0 8px}
§ .cf .bt{height:32px}
§ .cf div{display:flex;gap:8px;justify-content:flex-end}
§ .bye{position:absolute;inset:0;display:flex;flex-direction:column;align-items:center;justify-content:center;gap:6px;padding:20px;background:var(--card);text-align:center;border-radius:12px;color:var(--ink2);font-size:13px}
§ .bye[hidden]{display:none}
§ .bye .ic{width:36px;height:36px;color:var(--ok)}
§ .bye b{font-size:16px;font-weight:600;color:var(--ink)}
§ .bye .bt{margin-top:10px}
`
const userHook = (root) => {
  root.addEventListener('click', (e) => {
    const sw = e.target.closest('[data-sw]'); if (sw) { const l = $(root, '.sl'); l.hidden = !l.hidden; sw.setAttribute('aria-expanded', !l.hidden); return }
    const st = e.target.closest('[data-st]'); if (st) { $$(root, '[data-st]').forEach((x) => x.classList.toggle('on', x === st)); $(root, '[data-cur]').textContent = st.dataset.st; say(root, `已切换到「${st.dataset.st}」`, 'ok'); return }
    const ap = e.target.closest('.sgm [data-o]'); if (ap) { say(root, `外观：${ap.dataset.o}（示例，不改变本页）`, 'in'); return }
    const out = e.target.closest('[data-out]'); if (out) { out.closest('.uf').innerHTML = `<div class="cf"><p>确定退出登录？未提交的草稿会保留在本机。</p><div><button type="button" class="bt" data-no>取消</button><button type="button" class="bt dng" data-yes>退出</button></div></div>`; const y = $(root, '[data-yes]'); if (y) y.focus(); return }
    if (e.target.closest('[data-no]')) { $(root, '.uf').innerHTML = `<button type="button" class="mi2 dg" data-out>${I('logout')}退出登录</button>`; return }
    if (e.target.closest('[data-yes]')) { $(root, '.bye').hidden = false; const b = $(root, '[data-back]'); if (b) b.focus(); return }
    if (e.target.closest('[data-back]')) { $(root, '.bye').hidden = true; $(root, '.uf').innerHTML = `<button type="button" class="mi2 dg" data-out>${I('logout')}退出登录</button>`; say(root, '欢迎回来，林小满', 'ok') }
  })
}

/* ---- AD-NAV-003 顶栏 ---- */
const SUGG = [['订单', 'SO2026110528 · 林小满 · ¥1,196.00', 'receipt'], ['订单', 'SO2026110521 · 陈晓雨 · ¥329.00', 'receipt'], ['客户', '林小满 · 138****2086 · 金卡会员', 'user'], ['客户', '林子豪 · 139****7741 · 普通会员', 'user'], ['商品', '无线降噪耳机 · 石墨灰', 'box'], ['页面', '库存预警', 'alert']]
def({
  id: 'AD-NAV-003', name: '后台顶栏', style: '搜索+消息+账号', stage: '', wide: true,
  fit: '后台主框架顶部：折叠键、面包屑（两级以上页面）、全局搜索、测试环境标识、门店切换、帮助、消息红点与账号菜单，下拉各自独立开合。',
  avoid: '一级菜单页别在顶栏放面包屑；门店切换只在顶栏放一处，账号菜单里不再重复；不要把页面操作按钮（新建、导出）塞进顶栏。',
  kw: 'header topbar 顶栏 头部 搜索 消息 通知 用户菜单 门店切换 面包屑 测试环境 admin header',
  css: C('adnav003', `${MENU_CSS}${MSG_CSS}${USER_CSS}${FP_CSS}${FROW_CSS}
§ .frm{min-width:820px;border:1px solid var(--bd2);border-radius:12px;background:var(--bg)}
§ .hbar{display:flex;align-items:center;gap:12px;height:56px;padding:0 16px;background:var(--card);border-bottom:1px solid var(--bd2);border-radius:11px 11px 0 0}
§ .crumb{display:flex;align-items:center;gap:6px;white-space:nowrap;color:var(--ink3)}
§ .crumb button{color:var(--ink3)}§ .crumb button:hover{color:var(--p-text)}
§ .crumb .ic{width:14px;height:14px}
§ .crumb b{font-weight:400;color:var(--ink)}
§ .srch{position:relative;display:block;width:320px;margin-left:12px}
§ .srch>.ic{position:absolute;left:12px;top:10px;color:var(--ink3);pointer-events:none}
§ .srch .ip{height:36px;padding:0 64px 0 36px;background:var(--bg);border-color:transparent}
§ .srch .ip:focus{background:var(--card);border-color:var(--ink2)}
§ .srch .kb{position:absolute;right:8px;top:8px}
§ .sg{left:0;top:calc(100% + 6px);width:420px;padding:6px 0}
§ .sg h4{margin:0;padding:8px 14px 4px;font-size:12px;font-weight:400;color:var(--ink3)}
§ .sgi{display:flex;align-items:center;gap:10px;width:100%;height:40px;padding:0 14px;cursor:pointer;transition:background-color .15s var(--e)}
§ .sgi:hover{background:var(--bg)}
§ .sgi .tg2{flex:none}
§ .sgi span:last-child{min-width:0;overflow:hidden;text-overflow:ellipsis;white-space:nowrap}
§ .sg .none{padding:18px 14px;text-align:center;color:var(--ink3)}
§ .vr{width:1px;height:24px;background:var(--bd2)}
§ .pop.rt{right:0;top:calc(100% + 8px)}
§ .usr{display:flex;align-items:center;gap:10px;height:40px;padding:0 8px;border-radius:8px}
§ .usr:hover{background:var(--bg)}
§ .usr .ts{display:flex;flex-direction:column;line-height:1.25}
§ .usr .ts em{font-size:12px;color:var(--ink3)}
§ .env{height:24px}
§ .pg{min-height:316px}
`),
  html: () => `<div class="adnav003" data-sh><div class="frm">
  <header class="hbar"><button type="button" class="bt ib" data-fold aria-label="折叠菜单">${I('adshFold')}</button>
    <nav class="crumb" aria-label="面包屑"><button type="button">订单管理</button>${I('right')}<b aria-current="page">订单详情</b></nav>
    <div class="srch" data-keep>${I('search')}<input class="ip" type="search" placeholder="搜索订单号、客户、商品" autocomplete="off" aria-label="全局搜索"><span class="kb">Ctrl K</span>
      <div class="pop mn sg" data-pn="sg"></div></div>
    <span style="flex:1"></span>
    <span class="tg2 wn env">测试环境</span>
    <div class="pw"><button type="button" class="bt" data-pop="store" aria-expanded="false">${I('adshStore')}<span data-cur>旗舰店</span>${I('down')}</button>
      <div class="pop mn rt" data-pn="store">${['旗舰店', '中心城店', '星湖街店'].map((s, i) => `<button type="button" class="mi2${i ? '' : ' on'}" data-st="${s}">${s}<span class="ic ck">${sv('check')}</span></button>`).join('')}</div></div>
    <button type="button" class="bt ib" data-toast="已在新窗口打开帮助中心" aria-label="帮助中心">${I('adshHelp')}</button>
    <div class="pw"><button type="button" class="bt ib bell" data-pop="msg" aria-expanded="false" aria-label="消息">${I('bell')}<i class="dot">3</i></button>
      <div class="pop mn rt mp" data-pn="msg">${msgPanel(false)}</div></div>
    <i class="vr"></i>
    <div class="pw"><button type="button" class="usr" data-pop="usr" aria-expanded="false">${critter(0, 32)}<span class="ts"><b style="font-weight:600">林小满</b><em>店长</em></span>${I('down')}</button>
      <div class="pop mn rt" data-pn="usr" style="padding:6px">${userPanel({ store: false })}</div></div>
  </header>
  <div class="pg">${fauxPage(6)}</div></div></div>`,
  js: (root) => {
    const closeAll = pops(root); msgHook(root, true); userHook(root)
    const f = $(root, '[data-fold]'); let c = false
    f.addEventListener('click', () => { c = !c; $(f, '.ic').innerHTML = sv(c ? 'adshUnfold' : 'adshFold') })
    root.addEventListener('click', (e) => { const st = e.target.closest('.pop[data-pn=store] [data-st]'); if (st) { $$(root, '.pop[data-pn=store] [data-st]').forEach((x) => x.classList.toggle('on', x === st)); $(root, '.pw [data-pop=store] [data-cur]').textContent = st.dataset.st; closeAll(); say(root, `已切换到「${st.dataset.st}」`, 'ok') } })
    const inp = $(root, '.srch .ip'), sg = $(root, '.sg')
    const draw = () => {
      const q = inp.value.trim().toLowerCase()
      const list = q ? SUGG.filter((s) => (s[0] + s[1]).toLowerCase().includes(q)) : SUGG.slice(0, 4)
      sg.innerHTML = list.length ? `<h4>${q ? `找到 ${list.length} 条结果` : '最近搜索'}</h4>${list.map((s) => `<div class="sgi" data-v="${s[1].split(' · ')[0]}">${I(s[2])}<span class="tg2 in">${s[0]}</span><span>${s[1]}</span></div>`).join('')}` : `<div class="none">没有找到「${inp.value.trim().replace(/</g, '&lt;')}」相关内容，试试订单号或客户手机号</div>`
    }
    inp.addEventListener('focus', () => { closeAll(); draw(); sg.classList.add('open') })
    inp.addEventListener('input', () => { draw(); sg.classList.add('open') })
    sg.addEventListener('pointerdown', (e) => e.preventDefault())
    sg.addEventListener('click', (e) => { const it = e.target.closest('.sgi'); if (!it) return; inp.value = it.dataset.v; sg.classList.remove('open'); say(root, `已打开：${it.dataset.v}`, 'in') })
    inp.addEventListener('blur', () => sg.classList.remove('open'))
    inp.addEventListener('keydown', (e) => { if (e.key === 'Escape') { sg.classList.remove('open'); inp.blur() } })
  },
})

/* ---- AD-NAV-004 面包屑 ---- */
const CP = ['订单管理', '订单列表', '订单详情', '售后记录', '退款处理', '退款详情']
def({
  id: 'AD-NAV-004', name: '面包屑', style: '折叠+同级切换', stage: '', wide: false,
  fit: '两级以上的详情页、子页告诉用户“我在哪、怎么回上级”：层级过深时自动折叠中间层，同级页面可在面包屑里直接切换。',
  avoid: '一级菜单页不放面包屑；最后一级是当前页，不做成链接；别把它当页面标题（标题写对象名，如订单号）。',
  kw: 'breadcrumb 面包屑 路径 层级 导航 折叠 同级切换 返回上级',
  css: C('adnav004', `${MENU_CSS}
§ .cd{padding:16px 18px;border:1px solid var(--bd2);border-radius:12px;background:var(--card);box-shadow:var(--sh)}
§ .cd+.cd{margin-top:12px}
§ .cap{margin:0 0 10px;font-size:12px;color:var(--ink3)}
§ .bc{display:flex;align-items:center;flex-wrap:wrap;gap:6px;min-height:32px}
§ .bc .bl{display:inline-flex;align-items:center;gap:4px;height:28px;padding:0 6px;border-radius:4px;color:var(--ink3);white-space:nowrap;transition:color .15s var(--e),background-color .15s var(--e)}
§ .bc .bl:hover{color:var(--p-text);background:var(--pt)}
§ .bc .sep{color:var(--ink6);display:inline-flex}
§ .bc .sep .ic{width:14px;height:14px}
§ .bc .cur{padding:0 6px;color:var(--ink);white-space:nowrap}
§ .bc .ic{width:16px;height:16px}
§ .bc .more{letter-spacing:0}
§ .nonebc{color:var(--ink3);font-size:13px}
§ .ctl{display:flex;align-items:center;gap:8px;margin-top:12px;padding-top:12px;border-top:1px solid var(--line)}
§ .ctl .sp{flex:1;font-size:12px;color:var(--ink3);text-align:right}
§ .pop.dn{left:0;top:calc(100% + 6px)}
`),
  html: () => `<div class="adnav004" data-sh>
  <div class="cd"><p class="cap">路径随层级增长，超过 4 级折叠中间层（点“…”展开）</p><div class="bc" data-bc></div>
    <div class="ctl"><button type="button" class="bt" data-d="-1">返回上一级</button><button type="button" class="bt pri" data-d="1">进入下一级</button><span class="sp" data-lv></span></div></div>
  <div class="cd"><p class="cap">同级页面可以在面包屑里直接切换</p>
    <div class="bc"><button type="button" class="bl" data-toast="回到首页">${I('home')}</button><span class="sep">${I('right')}</span><button type="button" class="bl">商品管理</button><span class="sep">${I('right')}</span>
      <div class="pw"><button type="button" class="bl" data-pop="sib" aria-expanded="false"><span data-cur>商品列表</span>${I('down')}</button>
        <div class="pop mn dn" data-pn="sib">${['商品列表', '分类管理', '库存预警'].map((s, i) => `<button type="button" class="mi2${i ? '' : ' on'}" data-sb="${s}">${s}<span class="ic ck">${sv('check')}</span></button>`).join('')}</div></div>
      <span class="sep">${I('right')}</span><span class="cur" aria-current="page">陶瓷马克杯 350ml 手作釉面款</span></div></div></div>`,
  js: (root) => {
    pops(root)
    const bc = $(root, '[data-bc]'); let n = 5
    const link = (t, i) => `<button type="button" class="bl" data-i="${i}">${t}</button>`
    const sep = `<span class="sep">${I('right')}</span>`
    const draw = () => {
      if (n < 2) { bc.innerHTML = `<span class="nonebc">一级菜单页不放面包屑，页面顶部留给筛选与操作</span>` }
      else {
        const home = `<button type="button" class="bl" data-home aria-label="首页">${I('home')}</button>`
        let items
        if (n > 4) { const hid = CP.slice(1, n - 2); items = [link(CP[0], 0), `<div class="pw"><button type="button" class="bl more" data-pop="hid" aria-expanded="false" aria-label="展开隐藏的层级">${I('more')}</button><div class="pop mn dn" data-pn="hid">${hid.map((t, k) => `<button type="button" class="mi2" data-i="${k + 1}">${t}</button>`).join('')}</div></div>`, link(CP[n - 2], n - 2), `<span class="cur" aria-current="page">${CP[n - 1]}</span>`] }
        else items = CP.slice(0, n).map((t, i) => i === n - 1 ? `<span class="cur" aria-current="page">${t}</span>` : link(t, i))
        bc.innerHTML = home + items.map((x) => sep + x).join('')
      }
      $(root, '[data-lv]').textContent = n < 2 ? '当前：一级页' : `当前层级 ${n} / ${CP.length}`
      $$(root, '[data-d="-1"]')[0].disabled = n <= 1; $$(root, '[data-d="1"]')[0].disabled = n >= CP.length
    }
    draw()
    root.addEventListener('click', (e) => {
      const d = e.target.closest('[data-d]'); if (d) { n = Math.max(1, Math.min(CP.length, n + +d.dataset.d)); draw(); return }
      const l = e.target.closest('[data-bc] [data-i]'); if (l) { n = +l.dataset.i + 1; draw(); say(root, `已回到：${CP[+l.dataset.i]}`, 'in'); return }
      if (e.target.closest('[data-home]')) { say(root, '回到首页（示例）', 'in'); return }
      const s = e.target.closest('[data-sb]'); if (s) { $$(root, '[data-sb]').forEach((x) => x.classList.toggle('on', x === s)); $(root, '.pw [data-pop=sib] [data-cur]').textContent = s.dataset.sb; $(root, '.pop[data-pn=sib]').classList.remove('open'); say(root, `已切换到：${s.dataset.sb}`, 'ok') }
    })
  },
})

/* ---- AD-NAV-005 页面标签栏 ---- */
const TABS5 = [['home', '首页', 1], ['ord', '订单列表'], ['ship', '发货管理'], ['goods', '商品列表'], ['mem', '会员详情 · 林小满'], ['cpn', '优惠券活动配置'], ['staff', '员工账号'], ['stock', '库存预警'], ['ref', '售后处理'], ['store', '门店设置'], ['log', '操作日志'], ['cat', '分类管理']]
const tabItem = ([k, t, pin], on) => `<div class="tb${on ? ' on' : ''}${pin ? ' pin' : ''}" role="tab" aria-selected="${!!on}" data-k="${k}"><button type="button" class="ti">${pin ? I('home') : ''}<span data-w="${t}">${t}</span></button>${pin ? '' : `<button type="button" class="x" aria-label="关闭 ${t}">${sv('close')}</button>`}</div>`
def({
  id: 'AD-NAV-005', name: '页面标签栏', style: '多标签可关闭', stage: '', wide: true,
  fit: '业务员要在订单、商品、会员之间来回切换的后台：打开过的页面留成标签，可切换、可关闭、可批量关闭，超出宽度横向滚动。',
  avoid: '页面很少或以向导为主的系统不需要；标签上限别超过 15 个，并让首页标签不可关闭；别用它代替菜单。',
  kw: 'tabs 标签栏 多标签 页签 tab bar 关闭其他 关闭全部 历史页面 visited tags',
  css: C('adnav005', `${MENU_CSS}${FP_CSS}${FROW_CSS}
§ .tw{display:flex;align-items:flex-end;gap:4px;padding:8px 8px 0;background:var(--bg);border:1px solid var(--bd2);border-bottom:0;border-radius:12px 12px 0 0}
§ .tw>.bt{margin-bottom:3px}
§ .trk{position:relative;flex:1;min-width:0;display:flex;gap:2px;overflow-x:auto;scrollbar-width:none;cursor:default}
§ .trk::-webkit-scrollbar{display:none}
§ .tb{position:relative;flex:none;display:flex;align-items:center;gap:2px;height:38px;padding:0 6px 0 14px;border-radius:8px 8px 0 0;color:var(--ink2);transition:background-color .15s var(--e)}
§ .tb:hover{background:color-mix(in srgb,var(--card) 65%,transparent)}
§ .tb.on{background:var(--lift);color:var(--p-text);box-shadow:inset 0 2px 0 var(--p)}
§ .tb.pin{padding-right:14px}
§ .ti{display:inline-flex;align-items:center;gap:6px;height:100%;white-space:nowrap}
§ .ti span{display:inline-flex;flex-direction:column}
§ .ti span::after{content:attr(data-w);height:0;overflow:hidden;visibility:hidden;font-weight:600}
§ .tb.on .ti{font-weight:600}
§ .x{display:flex;align-items:center;justify-content:center;width:22px;height:22px;border-radius:50%;color:var(--ink3);opacity:0;transition:opacity .15s var(--e),background-color .15s var(--e)}
§ .tb:hover .x,§ .tb.on .x,§ .x:focus-visible{opacity:1}
§ .x:hover{background:var(--veil08);color:var(--ink)}
§ .x svg{width:12px;height:12px}
§ .pop.rt{right:0;top:calc(100% + 6px)}
§ .pgx{border:1px solid var(--bd2);border-radius:0 0 12px 12px;background:var(--card);padding:16px 20px 12px;min-height:250px}
§ .stt{display:flex;align-items:center;gap:8px;margin-bottom:10px;font-size:13px;color:var(--ink3)}
§ .stt b{font-weight:600;color:var(--ink)}
§ .pgx .frow{height:46px}
§ .pgx.ld .frow .sk{background:linear-gradient(90deg,var(--n5),var(--n3),var(--n5));background-size:200% 100%;animation:adnav005-sh 1s linear infinite}
@keyframes adnav005-sh{to{background-position:-200% 0}}
`),
  html: () => `<div class="adnav005" data-sh><div class="tw"><button type="button" class="bt ib" data-sc="-1" aria-label="向左滚动标签">${I('left')}</button>
    <div class="trk" role="tablist" data-ix="drag">${TABS5.map((t, i) => tabItem(t, i === 1)).join('')}</div>
    <button type="button" class="bt ib" data-sc="1" aria-label="向右滚动标签">${I('right')}</button>
    <div class="pw"><button type="button" class="bt ib" data-pop="act" aria-expanded="false" aria-label="标签操作">${I('more')}</button>
      <div class="pop mn rt" data-pn="act"><button type="button" class="mi2" data-a="refresh">${I('refresh')}刷新当前页</button><button type="button" class="mi2" data-a="others">${I('adshBan')}关闭其他</button><button type="button" class="mi2" data-a="right">${I('arrowright')}关闭右侧</button><div class="hr"></div><button type="button" class="mi2 dg" data-a="all">${I('trash')}关闭全部</button></div></div></div>
    <div class="pgx"><div class="stt" data-st></div>${Array.from({ length: 5 }, (_, i) => `<div class="frow"><i class="sk" style="width:${[18, 26, 14, 22, 16][i]}%"></i><i class="sk" style="width:${[36, 28, 42, 30, 38][i]}%"></i><i class="sk" style="width:56px"></i></div>`).join('')}</div></div>`,
  js: (root) => {
    pops(root)
    const trk = $(root, '.trk'), tabs = () => $$(trk, '.tb')
    const arrows = () => { const l = $(root, '[data-sc="-1"]'), r = $(root, '[data-sc="1"]'); l.disabled = trk.scrollLeft <= 1; r.disabled = trk.scrollLeft + trk.clientWidth >= trk.scrollWidth - 1 }
    const stat = () => { const a = $(trk, '.tb.on'); $(root, '[data-st]').innerHTML = `<b>当前标签：${a ? $(a, '.ti span').textContent : '无'}</b><span>已打开 ${tabs().length} 个页面，第 ${a ? tabs().indexOf(a) + 1 : 0} 个</span>` }
    const reveal = (tb) => { const l = tb.offsetLeft, r = l + tb.offsetWidth; if (l < trk.scrollLeft) trk.scrollTo({ left: l - 8, behavior: 'smooth' }); else if (r > trk.scrollLeft + trk.clientWidth) trk.scrollTo({ left: r - trk.clientWidth + 8, behavior: 'smooth' }) }
    const activate = (tb) => { tabs().forEach((t) => { t.classList.toggle('on', t === tb); t.setAttribute('aria-selected', t === tb) }); reveal(tb); stat(); arrows() }
    const close = (tb) => { if (tb.classList.contains('pin')) return; const was = tb.classList.contains('on'), nx = tb.nextElementSibling || tb.previousElementSibling; tb.remove(); if (was && nx) activate(nx); else { stat(); arrows() } }
    root.addEventListener('click', (e) => {
      if (e.target.__drag) return
      const x = e.target.closest('.x'); if (x) { close(x.closest('.tb')); return }
      const tb = e.target.closest('.tb'); if (tb) { activate(tb); return }
      const sc = e.target.closest('[data-sc]'); if (sc) { trk.scrollBy({ left: +sc.dataset.sc * 240, behavior: 'smooth' }); setTimeout(arrows, 320); return }
      const a = e.target.closest('[data-a]'); if (!a) return
      $(root, '.pop[data-pn=act]').classList.remove('open')
      const cur = $(trk, '.tb.on'), all = tabs()
      if (a.dataset.a === 'refresh') { const pg = $(root, '.pgx'); pg.classList.add('ld'); setTimeout(() => { pg.classList.remove('ld'); say(root, `已刷新：${$(cur, '.ti span').textContent}`, 'ok') }, 700) }
      if (a.dataset.a === 'others') { all.filter((t) => t !== cur && !t.classList.contains('pin')).forEach((t) => t.remove()); stat(); arrows(); say(root, '已关闭其他标签', 'ok') }
      if (a.dataset.a === 'right') { all.slice(all.indexOf(cur) + 1).forEach((t) => t.remove()); stat(); arrows(); say(root, '已关闭右侧标签', 'ok') }
      if (a.dataset.a === 'all') { all.filter((t) => !t.classList.contains('pin')).forEach((t) => t.remove()); activate($(trk, '.tb')); say(root, '已关闭全部，回到首页', 'ok') }
    })
    trk.addEventListener('auxclick', (e) => { const tb = e.target.closest('.tb'); if (tb && e.button === 1) { e.preventDefault(); close(tb) } })
    trk.addEventListener('scroll', arrows, { passive: true })
    stat(); requestAnimationFrame(arrows)
  },
})

/* ---- AD-NAV-006 详情页页头 ---- */
const DESC6 = [['客户', '林小满'], ['手机号', '138****2086'], ['下单时间', '2026-11-04 09:12'], ['实付金额', '¥1,196.00']]
def({
  id: 'AD-NAV-006', name: '详情页页头', style: '标题+状态+操作', stage: '', wide: true,
  fit: '订单、会员、工单这类详情页：面包屑 + 对象名（订单号）作标题 + 状态标签 + 主次操作 + 关键信息一行 + 内容标签页；操作后状态当场更新。',
  avoid: '一级列表页不用（那里顶部是筛选和按钮，不放同名标题）；主按钮最多一个，危险操作收进“更多”；标题写对象名，别重复菜单名。',
  kw: 'page header 页头 详情页 标题 状态 操作按钮 面包屑 标签页 订单详情 descriptions PageHeader',
  css: C('adnav006', `${MENU_CSS}
§ .hd{padding:14px 24px 0;border:1px solid var(--bd2);border-bottom:0;border-radius:12px 12px 0 0;background:var(--card)}
§ .bcm{display:flex;align-items:center;gap:4px;font-size:13px;color:var(--ink3)}
§ .bcm .ic{width:14px;height:14px;color:var(--ink6)}
§ .bcm button{color:var(--ink3)}§ .bcm button:hover{color:var(--p-text)}
§ .hdl{display:flex;align-items:center;flex-wrap:wrap;gap:10px;margin-top:10px}
§ .hdl h3{margin:0;font-size:20px;line-height:32px;font-weight:600;font-variant-numeric:tabular-nums}
§ .cp{display:inline-flex;width:28px;height:28px;align-items:center;justify-content:center;border-radius:4px;color:var(--ink3)}
§ .cp:hover{background:var(--bg);color:var(--ink)}
§ .hdl .sp{flex:1}
§ .acts{display:flex;align-items:center;gap:8px;flex-wrap:wrap}
§ .pop.rt{right:0;top:calc(100% + 6px)}
§ .ds{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:12px 24px;margin:14px 0 4px;padding:12px 16px;border-radius:8px;background:var(--bg)}
§ .ds div{min-width:0}
§ .ds dt{font-size:12px;color:var(--ink3)}
§ .ds dd{margin:2px 0 0;overflow:hidden;text-overflow:ellipsis;white-space:nowrap}
§ .ds .amt{font-weight:600;font-variant-numeric:tabular-nums}
§ .tbs{position:relative;display:flex;gap:28px;margin-top:6px;overflow-x:auto;scrollbar-width:none}
§ .tbs::-webkit-scrollbar{display:none}
§ .tbs>button{display:inline-flex;align-items:center;flex:none;gap:6px;height:44px;color:var(--ink2);white-space:nowrap}
§ .tbs>button span{display:inline-flex;flex-direction:column}
§ .tbs>button span::after{content:attr(data-w);height:0;overflow:hidden;visibility:hidden;font-weight:600}
§ .tbs>button.on{color:var(--p-text);font-weight:600}
§ .tbs>button em{min-width:18px;height:18px;padding:0 5px;border-radius:9px;background:var(--mub);font-size:12px;line-height:18px;text-align:center;color:var(--ink2)}
§ .tbs .ink{position:absolute;bottom:0;height:2px;background:var(--p);transition:left .25s var(--e),width .25s var(--e)}
§ .pnl{min-height:210px;padding:18px 24px;border:1px solid var(--bd2);border-radius:0 0 12px 12px;background:var(--card);border-top:1px solid var(--line)}
§ .kv{display:grid;grid-template-columns:96px 1fr;gap:10px 16px;margin:0}
§ .kv dt{color:var(--ink3)}§ .kv dd{margin:0}
§ .gl{display:flex;align-items:center;gap:12px;padding:10px 0;border-bottom:1px solid var(--line)}
§ .gl:last-child{border-bottom:0}
§ .gl img{width:44px;height:44px;border-radius:8px;object-fit:cover;flex:none}
§ .gl .nm{flex:1;min-width:0}
§ .gl .nm small{display:block;font-size:12px;color:var(--ink3)}
§ .gl .am{width:96px;text-align:right;font-variant-numeric:tabular-nums}
§ .tln{list-style:none;margin:0;padding:0}
§ .tln li{position:relative;padding:0 0 14px 20px;color:var(--ink2)}
§ .tln li::before{content:"";position:absolute;left:3px;top:7px;width:8px;height:8px;border-radius:50%;background:var(--pm)}
§ .tln li::after{content:"";position:absolute;left:6.5px;top:17px;bottom:-2px;width:1px;background:var(--line)}
§ .tln li:last-child::after{display:none}
§ .tln li.now::before{background:var(--p)}
§ .tln b{font-weight:600;color:var(--ink)}
§ .tln time{display:block;font-size:12px;color:var(--ink3)}
@media(max-width:640px){§ .ds{grid-template-columns:repeat(2,minmax(0,1fr))}§ .ds dd{white-space:normal}§ .pnl{padding:16px}§ .kv{grid-template-columns:72px 1fr}}
`),
  html: () => `<div class="adnav006" data-sh><section class="hd">
    <nav class="bcm" aria-label="面包屑"><button type="button">订单管理</button>${I('right')}<button type="button">订单列表</button>${I('right')}<span aria-current="page">订单详情</span></nav>
    <div class="hdl"><button type="button" class="bt ib" aria-label="返回订单列表" data-toast="返回订单列表">${I('left')}</button><h3>SO2026110528</h3><button type="button" class="cp" data-cp aria-label="复制订单号">${I('copy')}</button><span class="tg2 in" data-state>待发货</span><span class="sp"></span>
      <div class="acts"><button type="button" class="bt" data-toast="已发送到打印机：面单 1 张">${I('file')}打印面单</button><button type="button" class="bt" data-toast="打开：修改收货地址">修改地址</button><button type="button" class="bt pri" data-ship>发货</button>
        <div class="pw"><button type="button" class="bt ib" data-pop="mo" aria-expanded="false" aria-label="更多操作">${I('more')}</button><div class="pop mn rt" data-pn="mo"><button type="button" class="mi2" data-toast="已导出订单明细">${I('download')}导出明细</button><div class="hr"></div><button type="button" class="mi2 dg" data-toast="关闭订单需二次确认（示例）">${I('adshBan')}关闭订单</button></div></div></div></div>
    <dl class="ds">${DESC6.map(([k, v]) => `<div><dt>${k}</dt><dd${k === '实付金额' ? ' class="amt"' : ''}>${v}</dd></div>`).join('')}</dl>
    <div class="tbs" data-ix="tabs" role="tablist">${[['a', '订单概览'], ['b', '商品明细', 3], ['c', '物流信息'], ['d', '操作日志']].map(([k, t, n], i) => `<button type="button" role="tab" data-t="${k}" class="${i ? '' : 'on'}"><span data-w="${t}">${t}</span>${n ? `<em>${n}</em>` : ''}</button>`).join('')}<i class="ink"></i></div></section>
  <div class="pnl">
    <div data-p="a"><dl class="kv"><dt>收货信息</dt><dd>林小满，138****2086，江苏省苏州市工业园区星湖街 328 号创意产业园 5 栋 1203 室</dd><dt>配送方式</dt><dd>顺丰快递 · 预计 11-06 送达</dd><dt>支付方式</dt><dd>微信支付 · 已支付 11-04 09:13</dd><dt>买家留言</dt><dd>工作日白天无人，请放前台代收，谢谢</dd></dl></div>
    <div data-p="b" hidden>${[[0, '无线降噪耳机', '石墨灰 · 主动降噪', 599], [1, '轻量跑鞋', '云白 · 42 码', 329], [7, '保湿精华', '玻尿酸 · 30ml', 258]].map(([i, n, d, a]) => `<div class="gl"><img src="${P(i)}" alt=""><div class="nm">${n}<small>${d} × 1</small></div><div class="am">¥${a}.00</div></div>`).join('')}<div class="gl"><div class="nm" style="text-align:right;color:var(--ink3)">运费 ¥10.00，合计</div><div class="am" style="font-weight:600">¥1,196.00</div></div></div>
    <div data-p="c" hidden><ul class="tln" data-logi><li class="now"><b>等待发货</b><time>仓库正在拣货，预计今天 16:00 前发出</time></li></ul></div>
    <div data-p="d" hidden><ul class="tln" data-log><li class="now"><b>审核通过</b>周一帆<time>11-04 09:20</time></li><li><b>支付成功</b>系统<time>11-04 09:13</time></li><li><b>顾客下单</b>林小满<time>11-04 09:12</time></li></ul></div>
  </div></div>`,
  js: (root) => {
    pops(root)
    root.addEventListener('click', (e) => {
      if (e.target.closest('[data-cp]')) { try { navigator.clipboard.writeText('SO2026110528') } catch (x) {} say(root, '已复制订单号 SO2026110528', 'ok'); return }
      const b = e.target.closest('[data-ship]'); if (!b || b.disabled) return
      b.disabled = true; b.innerHTML = '<span class="spn"></span>发货中'
      setTimeout(() => {
        b.innerHTML = '已发货'; const s = $(root, '[data-state]'); s.className = 'tg2 ok'; s.textContent = '已发货'
        $(root, '[data-logi]').innerHTML = `<li class="now"><b>顺丰速运 已揽收</b>运单号 SF1403387920265<time>11-04 15:20</time></li><li><b>仓库已出库</b><time>11-04 15:05</time></li>`
        $(root, '[data-log]').insertAdjacentHTML('afterbegin', `<li class="now"><b>订单发货</b>林小满（店长）<time>11-04 15:05</time></li>`)
        $$(root, '[data-log] li.now')[1] && $$(root, '[data-log] li.now')[1].classList.remove('now')
        say(root, '已发货，运单号 SF1403387920265', 'ok')
      }, 800)
    })
  },
})

/* ---- AD-NAV-007 一级页操作栏 ---- */
const ddm = (key, label, opts, def) => `<div class="dd" data-ix="dd" data-f="${key}"><button type="button" class="bt" data-tg aria-haspopup="listbox"><span class="kl">${label}</span><span data-label>${def}</span>${I('down')}</button><div class="menu mn">${opts.map(([v, n]) => `<button type="button" class="mi2${v === def ? ' on' : ''}" data-o data-v="${v}">${v}${n === undefined ? '' : `<em class="${n === 0 ? 'z' : ''}">${n}</em>`}<span class="ic ck">${sv('check')}</span></button>`).join('')}</div></div>`
const BASE7 = { 待发货: 12, 配送中: 8, 已完成: 41, 退款中: 0, 已取消: 5, 全部: 66 }
const RF7 = { 今天: 0.3, '近 7 天': 1, '近 30 天': 2.6, 本季度: 6.2, 全部时间: 11 }
const CH7 = { 全部: 1, 小程序: 0.62, 门店收银: 0.3, 第三方平台: 0.08 }
const PAY7 = { 全部: 1, 微信支付: 0.7, 储值余额: 0.2, 支付宝: 0.1 }
def({
  id: 'AD-NAV-007', name: '一级页操作栏', style: '筛选左·按钮右', stage: '', wide: true,
  fit: '侧栏已高亮的一级列表页顶部：左侧搜索 + 2 个常用筛选 + “更多筛选”，右侧最多 1 个主按钮 + 1–2 个次按钮；生效的筛选以可移除标签显示，默认只看最该处理的子集。',
  avoid: '不要在这一行放与菜单同名的大标题或解释段；外露筛选别超过 4 个；状态数量已写在下拉里，就不再另放同组数字的统计卡。',
  kw: 'toolbar 操作栏 页面顶部 筛选 搜索 新建 导出 更多筛选 筛选标签 默认视图 列表页顶部',
  css: C('adnav007', `${MENU_CSS}
§ .wrap7{min-height:330px;padding:18px 20px;border:1px solid var(--bd2);border-radius:12px;background:var(--card)}
§ .tb7{display:flex;align-items:center;gap:10px;flex-wrap:wrap}
§ .lf{display:flex;align-items:center;gap:10px;flex-wrap:wrap;flex:1 1 440px;min-width:0}
§ .rt{display:flex;gap:8px}
§ .srch{position:relative;width:260px;max-width:100%}
§ .srch>.ic{position:absolute;left:12px;top:10px;color:var(--ink3);pointer-events:none}
§ .srch .ip{padding-left:36px}
§ .dd .bt{height:36px}
§ .kl{color:var(--ink3)}
§ .kl::after{content:"："}
§ .rt .bt{height:36px}
§ .menu{min-width:176px}
§ .mi2 em{margin-left:auto;font-style:normal;font-size:12px;color:var(--ink3)}
§ .mi2 em.z{color:var(--ink5)}
§ .mi2 .ck{margin-left:8px}
§ .badge{min-width:18px;height:18px;padding:0 5px;border-radius:9px;background:var(--pm);color:var(--p-text);font-size:12px;line-height:18px;text-align:center;font-style:normal}
§ .more7{display:flex;gap:10px;flex-wrap:wrap;margin-top:12px;padding:12px;border-radius:8px;background:var(--bg)}
§ .chips{display:flex;align-items:center;flex-wrap:wrap;gap:8px;margin-top:14px;min-height:28px}
§ .chips .lb{font-size:13px;color:var(--ink3)}
§ .chip{display:inline-flex;align-items:center;gap:2px;height:28px;padding:0 4px 0 10px;border-radius:14px;background:var(--pt);color:var(--p-text);font-size:13px}
§ .chip button{display:inline-flex;width:20px;height:20px;align-items:center;justify-content:center;border-radius:50%}
§ .chip button:hover{background:var(--pm)}
§ .chip svg{width:12px;height:12px}
§ .sum{margin-left:auto;font-size:13px;color:var(--ink3)}
§ .sum b{font-weight:600;color:var(--ink);font-variant-numeric:tabular-nums}
§ .nores{margin-top:12px;padding:10px 14px;border-radius:8px;background:var(--wnb);color:var(--wn);font-size:13px}
@media(max-width:640px){§ .srch{width:100%}§ .rt{width:100%;justify-content:flex-end}}
§ .phd{margin-top:16px;display:flex;flex-direction:column;gap:10px}
§ .phd .sk{height:36px;background:var(--soft);border-radius:8px}
`),
  html: () => `<div class="adnav007" data-sh><div class="wrap7">
    <div class="tb7"><div class="lf"><label class="srch">${I('search')}<input class="ip" data-q type="search" placeholder="搜索订单号、客户、手机号" autocomplete="off" aria-label="搜索订单"></label>
      ${ddm('status', '状态', [['待发货', 12], ['配送中', 8], ['已完成', 41], ['退款中', 0], ['已取消', 5], ['全部', 66]], '待发货')}
      ${ddm('range', '时间', [['今天'], ['近 7 天'], ['近 30 天'], ['本季度'], ['全部时间']], '近 7 天')}
      <button type="button" class="bt" data-more aria-expanded="false">${I('filter')}更多筛选<i class="badge" data-mb hidden>0</i></button></div>
      <div class="rt"><button type="button" class="bt" data-exp>${I('download')}导出</button><button type="button" class="bt pri" data-new>${I('plus')}新建订单</button></div></div>
    <div class="more7" data-mp hidden>${ddm('channel', '下单渠道', [['全部'], ['小程序'], ['门店收银'], ['第三方平台']], '全部')}${ddm('pay', '支付方式', [['全部'], ['微信支付'], ['储值余额'], ['支付宝']], '全部')}</div>
    <div class="chips" data-chips></div>
    <div class="phd"><i class="sk"></i><i class="sk"></i><i class="sk"></i></div></div></div>`,
  js: (root) => {
    const DEF = { status: '待发货', range: '近 7 天', channel: '全部', pay: '全部' }, ALL = { status: '全部', range: '全部时间', channel: '全部', pay: '全部' }
    const LB = { status: '状态', range: '时间', channel: '渠道', pay: '支付' }
    const st = { ...DEF, q: '' }, inp = $(root, '[data-q]')
    const count = () => { let n = BASE7[st.status] * RF7[st.range] * CH7[st.channel] * PAY7[st.pay]; if (st.q) n *= Math.max(0.05, 1 - st.q.length * 0.18); return n < 0.5 ? 0 : Math.max(1, Math.round(n)) }
    const setDd = (k, v) => { const d = $(root, `.dd[data-f="${k}"]`); $$(d, '[data-o]').forEach((o) => o.classList.toggle('on', o.dataset.v === v)); $(d, '[data-label]').textContent = v }
    const draw = () => {
      const act = Object.keys(DEF).filter((k) => st[k] !== ALL[k]); const n = count()
      const chips = act.map((k) => `<span class="chip">${LB[k]}：${st[k]}<button type="button" data-rm="${k}" aria-label="移除 ${LB[k]}">${sv('close')}</button></span>`)
      if (st.q) chips.push(`<span class="chip">关键词：${st.q.replace(/</g, '&lt;')}<button type="button" data-rm="q" aria-label="移除关键词">${sv('close')}</button></span>`)
      $(root, '[data-chips]').innerHTML = `${chips.length ? `<span class="lb">已筛选</span>${chips.join('')}<button type="button" class="bt txt" data-clear>清空</button>` : '<span class="lb">未设置筛选，显示全部订单</span>'}<span class="sum">共 <b>${n}</b> 条</span>`
      const ex = ['channel', 'pay'].filter((k) => st[k] !== ALL[k]).length; const mb = $(root, '[data-mb]'); mb.hidden = !ex; mb.textContent = ex
      let w = $(root, '.nores'); if (n === 0 && !w) $(root, '[data-chips]').insertAdjacentHTML('afterend', '<div class="nores">没有符合条件的订单，试试放宽时间范围或清空筛选。</div>'); if (n > 0 && w) w.remove()
    }
    root.addEventListener('click', (e) => {
      const o = e.target.closest('.dd [data-o]'); if (o) { st[o.closest('.dd').dataset.f] = o.dataset.v; draw(); return }
      const rm = e.target.closest('[data-rm]'); if (rm) { const k = rm.dataset.rm; if (k === 'q') { st.q = ''; inp.value = '' } else { st[k] = ALL[k]; setDd(k, ALL[k]) } draw(); return }
      if (e.target.closest('[data-clear]')) { Object.assign(st, ALL, { q: '' }); inp.value = ''; Object.keys(ALL).forEach((k) => setDd(k, ALL[k])); draw(); return }
      const m = e.target.closest('[data-more]'); if (m) { const p = $(root, '[data-mp]'); p.hidden = !p.hidden; m.setAttribute('aria-expanded', !p.hidden); return }
      if (e.target.closest('[data-exp]')) { const n = count(); n ? say(root, `已开始导出：当前筛选的 ${n} 条订单`, 'ok') : say(root, '没有可导出的订单，请先调整筛选', 'wn'); return }
      if (e.target.closest('[data-new]')) say(root, '打开：新建订单', 'in')
    })
    inp.addEventListener('input', () => { st.q = inp.value.trim(); draw() })
    draw()
  },
})

/* ---- AD-NAV-008 分页导航 ---- */
const ST_TONE = { warn: 'wn', info: 'in', ok: 'ok', mute: '', danger: 'dg' }
def({
  id: 'AD-NAV-008', name: '分页导航', style: '页码+条数+跳转', stage: '', wide: true,
  fit: '后台列表底部、靠右：共 N 条、每页条数（默认 20，可选 10/20/50/100）、上一页、页码（超过 7 页折叠，点省略号一次跳 5 页）、下一页、跳至某页；改条数时保持当前位置。',
  avoid: '小程序与移动端不用页码，改滚动加载；数据不足一页时不显示；别把“每页条数”藏起来，也别把默认值改成 10 或 50。',
  kw: 'pagination pager 分页 页码 每页条数 跳转 上一页 下一页 共几条 列表底部 page size',
  css: C('adnav008', `${MENU_CSS}
§ .box{border:1px solid var(--bd2);border-radius:12px;background:var(--card);overflow:visible}
§ table{width:100%;border-collapse:collapse}
§ th{height:44px;padding:0 16px;background:var(--bg);color:var(--ink2);font-weight:600;text-align:center;white-space:nowrap}
§ th:first-child{border-radius:11px 0 0 0}§ th:last-child{border-radius:0 11px 0 0}
§ td{height:48px;padding:0 16px;border-bottom:1px solid var(--line);text-align:center;white-space:nowrap}
§ td.l{text-align:left;padding-left:24px}
§ td.r{text-align:right;font-variant-numeric:tabular-nums;padding-right:28px}
§ td.id{font-variant-numeric:tabular-nums;color:var(--ink2)}
§ .pgn{display:flex;align-items:center;justify-content:flex-end;flex-wrap:wrap;gap:12px;padding:14px 16px}
§ .tot{color:var(--ink2)}
§ .tot b{font-weight:600;color:var(--ink);font-variant-numeric:tabular-nums}
§ .pgs{display:flex;align-items:center;gap:4px}
§ .pgs .bt{min-width:32px;padding:0 8px;font-variant-numeric:tabular-nums}
§ .pgs .bt.ib{width:32px}
§ .pgs .bt.on{background:var(--p);border-color:var(--p);color:#fff;cursor:default}
§ .pgs .bt.gap{border-color:transparent;background:none;color:var(--ink3)}
§ .pgs .bt.gap:hover{background:var(--bg);color:var(--p-text)}
§ .pop.up{left:0;bottom:calc(100% + 6px);min-width:132px}
§ .jmp{display:flex;align-items:center;gap:8px;color:var(--ink2)}
§ .jmp .ip{width:56px;height:32px;padding:0 8px;text-align:center}
§ .jmp .ip.bad{border-color:var(--dg)}
`),
  html: () => `<div class="adnav008" data-sh><div class="box"><table><thead><tr><th>订单号</th><th>客户</th><th>商品</th><th>金额</th><th>状态</th></tr></thead><tbody data-tb></tbody></table>
    <div class="pgn"><span class="tot">共 <b data-tot>268</b> 条</span>
      <div class="pw"><button type="button" class="bt" data-pop="sz" aria-expanded="false"><span data-sz>20 条/页</span>${I('down')}</button><div class="pop mn up" data-pn="sz">${[10, 20, 50, 100].map((n) => `<button type="button" class="mi2${n === 20 ? ' on' : ''}" data-size="${n}">${n} 条/页<span class="ic ck">${sv('check')}</span></button>`).join('')}</div></div>
      <nav class="pgs" aria-label="分页" data-pgs></nav>
      <label class="jmp">跳至<input class="ip" data-jump inputmode="numeric" aria-label="跳转页码">页</label></div></div></div>`,
  js: (root) => {
    pops(root)
    const TOTAL = 268; let size = 20, cur = 1
    const pages = () => Math.ceil(TOTAL / size)
    const pl = (c, t) => { const r = (a, b) => Array.from({ length: b - a + 1 }, (_, i) => a + i); if (t <= 7) return r(1, t); if (c <= 4) return [...r(1, 5), '…n', t]; if (c >= t - 3) return [1, '…p', ...r(t - 4, t)]; return [1, '…p', c - 1, c, c + 1, '…n', t] }
    const draw = () => {
      const t = pages()
      $(root, '[data-pgs]').innerHTML = `<button type="button" class="bt ib" data-go="${cur - 1}" aria-label="上一页"${cur <= 1 ? ' disabled' : ''}>${I('left')}</button>` + pl(cur, t).map((p) => typeof p === 'string' ? `<button type="button" class="bt gap" data-go="${p === '…n' ? Math.min(t, cur + 5) : Math.max(1, cur - 5)}" aria-label="${p === '…n' ? '向后 5 页' : '向前 5 页'}">•••</button>` : `<button type="button" class="bt${p === cur ? ' on' : ''}" data-go="${p}"${p === cur ? ' aria-current="page"' : ''}>${p}</button>`).join('') + `<button type="button" class="bt ib" data-go="${cur + 1}" aria-label="下一页"${cur >= t ? ' disabled' : ''}>${I('right')}</button>`
      $(root, '[data-tb]').innerHTML = Array.from({ length: 5 }, (_, k) => { const o = ORDER_ROWS[((cur - 1) * 5 + k) % 24]; return `<tr><td class="id">${o.no}</td><td>${o.who}</td><td class="l">${o.sku}</td><td class="r">¥${o.amt.toLocaleString('zh-CN')}.00</td><td><span class="tg2 ${ST_TONE[o.tone]}">${o.st}</span></td></tr>` }).join('')
      $(root, '[data-sz]').textContent = size + ' 条/页'
      $$(root, '[data-size]').forEach((b) => b.classList.toggle('on', +b.dataset.size === size))
    }
    const go = (n) => { const t = pages(); if (!(n >= 1 && n <= t)) return false; cur = n; draw(); return true }
    root.addEventListener('click', (e) => {
      const g = e.target.closest('[data-go]'); if (g && !g.disabled) { go(+g.dataset.go); return }
      const s = e.target.closest('[data-size]'); if (s) { const first = (cur - 1) * size; size = +s.dataset.size; cur = Math.floor(first / size) + 1; draw(); $(root, '.pop[data-pn=sz]').classList.remove('open'); say(root, `已改为每页 ${size} 条，共 ${pages()} 页`, 'in') }
    })
    const j = $(root, '[data-jump]')
    j.addEventListener('input', () => j.classList.remove('bad'))
    j.addEventListener('keydown', (e) => { if (e.key !== 'Enter') return; const n = parseInt(j.value, 10); if (go(n)) { j.value = '' } else { j.classList.add('bad'); say(root, `请输入 1–${pages()} 之间的页码`, 'wn') } })
    draw()
  },
})

/* ---- AD-NAV-009 步骤条 ---- */
def({
  id: 'AD-NAV-009', name: '步骤条', style: '横向分步表单', stage: '', wide: false,
  fit: '新建活动、开通店铺、导入向导这类 3–5 步的连续流程：已完成打勾、当前高亮、未开始置灰，失败时停在该步并写原因，可回退修改。',
  avoid: '步骤之间互相独立时改用标签页；超过 6 步先拆流程；别把“完成”当成要用户操作的一步，它是终点。',
  kw: 'steps stepper 步骤条 向导 分步 流程 进度 提交审核 wizard 新建活动 失败重试',
  css: C('adnav009', `${MENU_CSS}
§ .cd{padding:22px 24px 18px;border:1px solid var(--bd2);border-radius:12px;background:var(--card);box-shadow:var(--sh)}
§ .stp{display:flex;align-items:center;list-style:none;margin:0;padding:0;min-width:440px}
§ .stp li{position:relative;flex:none;display:flex;align-items:center;gap:10px;min-width:0}
§ .stp li.ln{flex:1;min-width:20px;height:2px;margin:0 12px;border-radius:1px;background:var(--n6);transition:background-color .25s var(--e)}
§ .stp li.ln.done{background:var(--p)}
§ .no{display:flex;align-items:center;justify-content:center;width:32px;height:32px;border-radius:50%;flex:none;border:2px solid var(--n7);background:var(--card);color:var(--ink3);transition:background-color .2s var(--e),border-color .2s var(--e),color .2s var(--e)}
§ .no .ic{width:16px;height:16px}
§ .stp li.on .no{border-color:var(--p);background:var(--pt);color:var(--p-text);font-weight:600}
§ .stp li.done .no{border-color:var(--p);background:var(--p);color:#fff}
§ .stp li.err .no{border-color:var(--dg);background:var(--dgb);color:var(--dg)}
§ .tx{min-width:0;padding-top:0;white-space:nowrap;line-height:1.35}
§ .tx b{display:block;font-weight:400;color:var(--ink3)}
§ .stp li.on .tx b,§ .stp li.done .tx b{color:var(--ink);font-weight:600}
§ .stp li.err .tx b{color:var(--dg);font-weight:600}
§ .tx small{display:block;font-size:12px;color:var(--ink3)}
§ .bd{padding:18px 20px;border-radius:8px;background:var(--bg);min-height:154px}
§ .bd label{display:block;margin-bottom:6px;font-size:13px;color:var(--ink2)}
§ .fld+.fld{margin-top:12px}
§ .er{margin:4px 0 0;font-size:12px;color:var(--dg)}
§ .ip.bad{border-color:var(--dg)}
§ .chs{display:flex;gap:8px;flex-wrap:wrap}
§ .chs button{height:36px;padding:0 14px;border:1px solid var(--bd);border-radius:8px;background:var(--card);transition:border-color .15s var(--e),background-color .15s var(--e)}
§ .chs button.on{border-color:var(--p);background:var(--pt);color:var(--p-text);font-weight:600}
§ .kv{display:grid;grid-template-columns:88px 1fr;gap:8px 12px;margin:0}
§ .kv dt{color:var(--ink3)}§ .kv dd{margin:0}
§ .fail{display:flex;gap:8px;margin-top:12px;padding:10px 12px;border-radius:8px;background:var(--dgb);color:var(--dg);font-size:13px}
§ .okp{display:flex;flex-direction:column;align-items:center;gap:6px;text-align:center;padding:6px 0}
§ .okp .ic{width:36px;height:36px;color:var(--ok)}
§ .okp b{font-size:16px;font-weight:600}
§ .okp span{color:var(--ink2)}
§ .ft9{display:flex;justify-content:flex-end;gap:8px;margin-top:16px}
`),
  html: () => `<div class="adnav009" data-sh><div class="cd" style="overflow-x:auto"><ol class="stp" aria-label="新建满减活动的步骤">${[['基本信息', '名称与时间'], ['优惠规则', '门槛与额度'], ['核对提交', '确认后送审'], ['完成', '等待审核']].map(([t, d], i) => `${i ? '<li class="ln" aria-hidden="true"></li>' : ''}<li class="sp${i === 0 ? ' on' : ''}"${i === 0 ? ' aria-current="step"' : ''}><span class="no">${i + 1}</span><span class="tx"><b>${t}</b><small>${d}</small></span></li>`).join('')}</ol></div>
    <div class="cd" style="margin-top:12px;padding-top:18px"><div class="bd" data-bd></div><div class="ft9"><button type="button" class="bt" data-prev>上一步</button><button type="button" class="bt pri" data-next>下一步</button></div></div></div>`,
  js: (root) => {
    const items = $$(root, '.stp li.sp'), lines = $$(root, '.stp li.ln'); let i = 0, tries = 0
    const D = { name: '双十一满减活动', rule: '满 200 减 30' }
    const body = [
      () => `<div class="fld"><label for="s9n">活动名称</label><input class="ip" id="s9n" data-name value="${D.name}" maxlength="20" placeholder="如：双十一满减活动"><p class="er" data-er hidden>请填写活动名称</p></div><div class="fld"><label>活动时间</label><div class="ip" style="display:flex;align-items:center;height:auto;min-height:36px;padding:6px 12px;color:var(--ink2)">2026-11-08 00:00 至 2026-11-12 23:59</div></div>`,
      () => `<label>优惠规则</label><div class="chs" data-ch>${['满 200 减 30', '满 300 减 50', '满 500 减 100'].map((t) => `<button type="button" class="${t === D.rule ? 'on' : ''}" data-r="${t}">${t}</button>`).join('')}</div><p style="margin:12px 0 0;color:var(--ink3);font-size:13px">优惠券与满减可叠加，叠加后最低实付不低于商品成本价。</p>`,
      () => `<dl class="kv"><dt>活动名称</dt><dd>${D.name}</dd><dt>优惠规则</dt><dd>${D.rule}</dd><dt>活动时间</dt><dd>2026-11-08 至 2026-11-12，共 5 天</dd><dt>适用门店</dt><dd>全部门店（旗舰店、中心城店、星湖街店）</dd></dl>${tries === 1 ? `<div class="fail">${I('closec')}<span>提交失败：网络超时，请检查网络后重试。草稿已自动保存，不会丢失。</span></div>` : ''}`,
      () => `<div class="okp">${I('checkc')}<b>已提交审核</b><span>“${D.name}”预计 1 个工作日内审核完成，结果会发到消息中心。</span></div>`,
    ]
    const draw = () => {
      const failed = tries === 1 && i === 2
      items.forEach((li, k) => {
        const done = k < i || (i === 3 && k === 3), err = failed && k === 2
        li.classList.toggle('done', done); li.classList.toggle('err', err); li.classList.toggle('on', k === i && !err)
        if (k === i) li.setAttribute('aria-current', 'step'); else li.removeAttribute('aria-current')
        $(li, '.no').innerHTML = done ? I('check') : err ? I('close') : k + 1
      })
      lines.forEach((l, k) => l.classList.toggle('done', k < i))
      $(root, '[data-bd]').innerHTML = body[i]()
      const p = $(root, '[data-prev]'), n = $(root, '[data-next]')
      p.hidden = i === 0; n.disabled = false
      n.textContent = i === 2 ? (tries === 1 ? '重试提交' : '提交审核') : i === 3 ? '再建一个' : '下一步'
      p.textContent = i === 3 ? '返回活动列表' : '上一步'
    }
    root.addEventListener('click', (e) => {
      const r = e.target.closest('[data-r]'); if (r) { D.rule = r.dataset.r; $$(root, '[data-r]').forEach((x) => x.classList.toggle('on', x === r)); return }
      if (e.target.closest('[data-prev]')) { if (i === 3) { say(root, '返回活动列表（示例）', 'in'); return } i = Math.max(0, i - 1); draw(); return }
      const n = e.target.closest('[data-next]'); if (!n) return
      if (i === 0) { const v = $(root, '[data-name]').value.trim(); if (!v) { $(root, '[data-name]').classList.add('bad'); $(root, '[data-er]').hidden = false; $(root, '[data-name]').focus(); return } D.name = v }
      if (i === 2) {
        n.disabled = true; n.innerHTML = '<span class="spn"></span>提交中'
        setTimeout(() => { if (tries === 0) { tries = 1; draw() } else { tries = 0; i = 3; draw(); say(root, '已提交审核', 'ok') } }, 800); return
      }
      if (i === 3) { i = 0; tries = 0; D.name = '双十一满减活动'; draw(); return }
      i++; draw()
    })
    root.addEventListener('input', (e) => { if (e.target.matches('[data-name]')) { e.target.classList.remove('bad'); $(root, '[data-er]').hidden = true } })
    draw()
  },
})

/* ---- AD-NAV-010 回到顶部 ---- */
def({
  id: 'AD-NAV-010', name: '回到顶部', style: '进度环按钮', stage: '', wide: false,
  fit: '内容很长的页面（长列表、长表单、日志）：滚过一屏后右下角出现“回到顶部”，圆环显示阅读进度，旁边可放帮助等常驻浮动按钮。',
  avoid: '短页面不需要；别和吸顶表头、底部批量栏抢位置；不用 position:fixed 压住主操作，距离页面底部至少 24px。',
  kw: 'back to top 回到顶部 返回顶部 浮动按钮 float button 滚动进度 长列表 backtop',
  css: C('adnav010', `
§ .wr{position:relative;border:1px solid var(--bd2);border-radius:12px;background:var(--card);overflow:hidden}
§ .hh{display:flex;align-items:center;justify-content:space-between;padding:12px 18px;border-bottom:1px solid var(--line);font-size:13px;color:var(--ink3)}
§ .hh b{font-weight:600;color:var(--ink);font-variant-numeric:tabular-nums}
§ .scr{height:320px;overflow-y:auto;padding:0 68px 0 18px}
§ .scr:focus-visible{outline:1px solid var(--ink2);outline-offset:-2px}
§ .li{display:flex;align-items:center;gap:12px;height:52px;border-bottom:1px solid var(--line)}
§ .li .nm{flex:1;min-width:0;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
§ .li .no{color:var(--ink3);font-variant-numeric:tabular-nums;width:116px;flex:none}
§ .li .am{width:80px;text-align:right;font-variant-numeric:tabular-nums}
§ .fl{position:absolute;right:20px;bottom:20px;display:flex;flex-direction:column;gap:10px;align-items:center}
§ .fb{position:relative;display:flex;align-items:center;justify-content:center;width:40px;height:40px;border-radius:50%;background:var(--card);color:var(--ink2);box-shadow:0 2px 6px var(--sh12),0 0 0 1px var(--bd2);transition:opacity .2s var(--e),transform .2s var(--e),background-color .15s var(--e)}
§ .fb:hover{background:var(--pt);color:var(--p-text)}
§ .fb .ic{width:18px;height:18px}
§ .fb.top.hid{opacity:0;transform:translateY(10px);pointer-events:none}
§ .fb svg.rg{position:absolute;inset:0;width:40px;height:40px;transform:rotate(-90deg);pointer-events:none}
§ .fb .rg circle{fill:none;stroke-width:2}
§ .fb .rg .bg{stroke:transparent}
§ .fb .rg .fg{stroke:var(--p);stroke-linecap:round;transition:stroke-dashoffset .1s linear}
§ .fb::after{content:attr(data-tip);position:absolute;right:calc(100% + 10px);top:50%;transform:translateY(-50%);padding:5px 10px;border-radius:4px;background:var(--inv);color:#fff;font-size:12px;line-height:1.4;white-space:nowrap;opacity:0;pointer-events:none;transition:opacity .15s var(--e)}
§ .fb:hover::after,§ .fb:focus-visible::after{opacity:1}
`),
  html: () => `<div class="adnav010" data-sh><div class="wr"><div class="hh"><span>示例页面：向下滚动试试</span><span>已阅读 <b data-pc>0</b>%</span></div>
    <div class="scr" tabindex="0" aria-label="示例长列表，可滚动">${Array.from({ length: 30 }, (_, i) => { const o = ORDER_ROWS[i % 24]; return `<div class="li"><span class="no">SO${2026110400 + 128 - i * 5}</span><span class="nm">${o.who} · ${o.sku}</span><span class="am">¥${o.amt}.00</span></div>` }).join('')}</div>
    <div class="fl"><button type="button" class="fb" data-tip="帮助中心" data-toast="已在新窗口打开帮助中心" aria-label="帮助中心">${I('adshHelp')}</button>
      <button type="button" class="fb top hid" data-tip="回到顶部" aria-label="回到顶部"><svg class="rg" viewBox="0 0 40 40" aria-hidden="true"><circle class="bg" cx="20" cy="20" r="19"/><circle class="fg" cx="20" cy="20" r="19" stroke-dasharray="119.4" stroke-dashoffset="119.4"/></svg>${I('arrowup')}</button></div></div></div>`,
  js: (root) => {
    const scr = $(root, '.scr'), top = $(root, '.fb.top'), fg = $(root, '.fg')
    const upd = () => { const max = scr.scrollHeight - scr.clientHeight, p = max > 0 ? scr.scrollTop / max : 0; fg.style.strokeDashoffset = 119.4 * (1 - p); $(root, '[data-pc]').textContent = Math.round(p * 100); top.classList.toggle('hid', scr.scrollTop < 120) }
    scr.addEventListener('scroll', upd, { passive: true }); upd()
    top.addEventListener('click', () => { const rm = matchMedia('(prefers-reduced-motion:reduce)').matches; scr.scrollTo({ top: 0, behavior: rm ? 'auto' : 'smooth' }); scr.focus({ preventScroll: true }) })
  },
})

/* ---- AD-NAV-011 用户菜单 ---- */
const miniBar = (inner) => `<div class="mbar"><span class="logo">${sv('grid2')}</span><b>云店管理</b><span style="flex:1"></span>${inner}</div>`
const MBAR_CSS = `
§ .mfr{min-height:440px;border:1px solid var(--bd2);border-radius:12px;background:var(--bg)}
§ .mbar{display:flex;align-items:center;gap:10px;height:56px;padding:0 16px;background:var(--card);border-bottom:1px solid var(--bd2);border-radius:11px 11px 0 0}
§ .mbar b{font-size:16px;font-weight:600}
§ .logo{display:flex;align-items:center;justify-content:center;width:28px;height:28px;border-radius:8px;background:var(--p);color:#fff}
§ .logo svg{width:16px;height:16px}
§ .pop.rt{right:0;top:calc(100% + 8px)}
`
def({
  id: 'AD-NAV-011', name: '用户菜单', style: '头像+角色+退出', stage: '', wide: false,
  fit: '顶栏右上角账号下拉：动物头像、姓名与角色、门店、个人资料、改密码、切换门店、外观（跟随系统/浅色/深色）、帮助，退出登录单独成区并先确认、草稿保留。',
  avoid: '顶栏已有门店切换时，这里不再放“切换门店”；别放与账号无关的业务入口；退出不要一步到位，防误触。',
  kw: 'user menu 用户菜单 头像 账号 角色 退出登录 切换门店 外观 深色 个人资料 修改密码 下拉',
  css: C('adnav011', `${MENU_CSS}${USER_CSS}${MBAR_CSS}
§ .mfr{min-height:470px}${FP_CSS}${FROW_CSS}`),
  html: () => `<div class="adnav011" data-sh><div class="mfr">${miniBar(`<div class="pw"><button type="button" class="usr" data-pop="usr" aria-expanded="true" style="display:flex;align-items:center;gap:10px;height:40px;padding:0 8px;border-radius:8px">${critter(0, 32)}<span style="font-weight:600">林小满</span>${I('down')}</button><div class="pop mn rt open" data-pn="usr">${userPanel({ store: true })}</div></div>`)}${fauxPage(3)}</div></div>`,
  js: (root) => { pops(root); userHook(root) },
})

/* ---- AD-NAV-012 全局命令面板 ---- */
const CMDS = [
  { g: '页面', t: '订单列表', k: 'order dingdan', i: 'receipt', h: '订单管理' }, { g: '页面', t: '发货管理', k: 'fahuo shipping', i: 'truck', h: '订单管理' },
  { g: '页面', t: '商品列表', k: 'goods shangpin', i: 'box', h: '商品管理' }, { g: '页面', t: '库存预警', k: 'stock kucun', i: 'alert', h: '商品管理' },
  { g: '页面', t: '会员管理', k: 'member huiyuan', i: 'users', h: '会员营销' }, { g: '页面', t: '优惠券', k: 'coupon youhuiquan', i: 'coupon', h: '会员营销' },
  { g: '页面', t: '操作日志', k: 'log rizhi', i: 'file', h: '系统' },
  { g: '操作', t: '新建订单', k: 'new create', i: 'plus', kb: 'N' }, { g: '操作', t: '导出本月订单', k: 'export daochu', i: 'download', kb: 'E' },
  { g: '操作', t: '切换门店', k: 'switch store mendian', i: 'adshSwap' }, { g: '操作', t: '退出登录', k: 'logout tuichu', i: 'logout', dg: 1 },
]
def({
  id: 'AD-NAV-012', name: '全局命令面板', style: '输入即搜', stage: '', wide: false,
  fit: '页面和操作很多的后台：Ctrl K 呼出，输入关键词即时过滤页面与操作，↑↓ 选择、Enter 执行、Esc 关闭；无输入时显示最近访问和常用操作。',
  avoid: '菜单很少的小系统不需要；结果要分组（页面、操作）并写所属菜单；没有结果时写出搜索词并给下一步，不要留空白。',
  kw: 'command palette 命令面板 全局搜索 快捷键 Ctrl K 跳转 spotlight cmdk 键盘导航 快速操作',
  css: C('adnav012', `${MENU_CSS}${FP_CSS}${FROW_CSS}
§ .wrp{position:relative;min-height:510px;border:1px solid var(--bd2);border-radius:12px;background:var(--bg);overflow:hidden}
§ .top{display:flex;align-items:center;gap:12px;height:56px;padding:0 16px;background:var(--card);border-bottom:1px solid var(--bd2)}
§ .trg{display:flex;align-items:center;gap:8px;width:300px;max-width:100%;height:36px;padding:0 10px 0 12px;border:1px solid var(--bd);border-radius:8px;background:var(--card);color:var(--ink3);transition:border-color .15s var(--e)}
§ .trg:hover{border-color:var(--ink3)}
§ .trg .kb{margin-left:auto}
§ .ix-ov{align-items:flex-start;padding-top:56px}
§ .pal{position:relative;z-index:1;width:560px;max-width:100%;border-radius:12px;background:var(--card);box-shadow:var(--sh2);overflow:hidden}
§ .ih{display:flex;align-items:center;gap:10px;height:52px;padding:0 16px;border-bottom:1px solid var(--line);color:var(--ink3)}
§ .ih .ic{width:18px;height:18px}
§ .cin{flex:1;min-width:0;height:100%;border:0;outline:none;background:none;font:inherit;font-size:16px;color:var(--ink)}
§ .cin::placeholder{color:var(--ink3)}
§ .res{max-height:290px;overflow:auto;padding:6px 8px 8px}
§ .gh{padding:10px 10px 4px;font-size:12px;color:var(--ink3)}
§ .ci{display:flex;align-items:center;gap:12px;height:44px;padding:0 10px;border-radius:8px;cursor:pointer}
§ .ci .ic{color:var(--ink2)}
§ .ci .hh{margin-left:auto;font-size:12px;color:var(--ink3);white-space:nowrap}
§ .ci.act{background:var(--pt)}
§ .ci.act .ic{color:var(--p-text)}
§ .ci.dg,§ .ci.dg .ic{color:var(--dg)}
§ .ci .hl{color:var(--p-text);font-weight:600}
§ .ci .kb{margin-left:auto}
§ .none{display:flex;flex-direction:column;align-items:center;gap:4px;padding:32px 16px;text-align:center;color:var(--ink3)}
§ .none b{font-weight:600;color:var(--ink)}
§ .ph2{display:flex;align-items:center;gap:16px;height:40px;padding:0 16px;border-top:1px solid var(--line);background:var(--bg);font-size:12px;color:var(--ink3)}
§ .ph2 span{display:inline-flex;align-items:center;gap:6px}
`),
  html: () => `<div class="adnav012" data-sh><div class="wrp"><div class="top"><button type="button" class="trg" data-open="pal" aria-keyshortcuts="Control+K">${I('search')}搜索页面或操作<span class="kb">Ctrl K</span></button></div>${fauxPage(4)}
    <div class="ix-ov show" data-ov="pal"><div class="ix-mask"></div><div class="pal pn" role="dialog" aria-label="全局命令面板" tabindex="-1">
      <div class="ih">${I('search')}<input class="cin" data-autofocus role="combobox" aria-expanded="true" aria-controls="adnav012-res" placeholder="输入页面或操作，如：订单、导出" autocomplete="off" aria-label="搜索命令"><span class="kb">Esc</span></div>
      <div class="res" id="adnav012-res" role="listbox"></div>
      <div class="ph2"><span><i class="kb">↑</i><i class="kb">↓</i>选择</span><span><i class="kb">Enter</i>打开</span><span><i class="kb">Esc</i>关闭</span></div></div></div></div></div>`,
  js: (root) => {
    overlays(root)
    const inp = $(root, '.cin'), res = $(root, '.res'), ov = $(root, '.ix-ov'); let list = [], ai = 0
    const esc = (s) => s.replace(/[&<>]/g, (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;' }[c]))
    const hl = (t, q) => { if (!q) return t; const k = t.toLowerCase().indexOf(q); return k < 0 ? t : `${t.slice(0, k)}<span class="hl">${t.slice(k, k + q.length)}</span>${t.slice(k + q.length)}` }
    const draw = () => {
      const raw = inp.value.trim(), q = raw.toLowerCase()
      let groups
      if (!q) groups = [['最近访问', [CMDS[0], CMDS[3], CMDS[4]]], ['常用操作', [CMDS[7], CMDS[8]]]]
      else { const m = CMDS.filter((c) => (c.t + ' ' + c.k + ' ' + (c.h || '')).toLowerCase().includes(q)); groups = ['页面', '操作'].map((g) => [g, m.filter((c) => c.g === g)]).filter((x) => x[1].length) }
      list = groups.flatMap((g) => g[1]); ai = Math.min(ai, Math.max(0, list.length - 1))
      res.innerHTML = list.length ? groups.map(([g, items]) => `<div class="gh">${g}</div>${items.map((c) => `<div class="ci${c.dg ? ' dg' : ''}" role="option" id="adnav012-o${list.indexOf(c)}" data-i="${list.indexOf(c)}">${I(c.i)}<span>${hl(c.t, q)}</span>${c.kb ? `<span class="kb">${c.kb}</span>` : `<span class="hh">${c.h || ''}</span>`}</div>`).join('')}`).join('') : `<div class="none"><b>没有找到「${esc(raw)}」</b><span>试试订单号、客户名，或换一个更短的关键词</span></div>`
      mark()
    }
    const mark = () => { $$(res, '.ci').forEach((el, k) => { const on = k === ai; el.classList.toggle('act', on); el.setAttribute('aria-selected', on); if (on) { inp.setAttribute('aria-activedescendant', el.id); const t = el.offsetTop, b = t + el.offsetHeight; if (t < res.scrollTop + 28) res.scrollTop = Math.max(0, t - 36); else if (b > res.scrollTop + res.clientHeight) res.scrollTop = b - res.clientHeight + 8 } }) }
    const run = (c) => { if (!c) return; closeOv(ov); say(root, c.g === '页面' ? `已跳转：${c.t}` : `已执行：${c.t}`, c.dg ? 'wn' : 'in') }
    inp.addEventListener('input', () => { ai = 0; draw() })
    inp.addEventListener('keydown', (e) => {
      if (e.key === 'ArrowDown') { e.preventDefault(); ai = list.length ? (ai + 1) % list.length : 0; mark() }
      else if (e.key === 'ArrowUp') { e.preventDefault(); ai = list.length ? (ai - 1 + list.length) % list.length : 0; mark() }
      else if (e.key === 'Enter') { e.preventDefault(); run(list[ai]) }
    })
    res.addEventListener('pointermove', (e) => { const c = e.target.closest('.ci'); if (c && +c.dataset.i !== ai) { ai = +c.dataset.i; mark() } })
    res.addEventListener('click', (e) => { const c = e.target.closest('.ci'); if (c) run(list[+c.dataset.i]) })
    $(root, '.trg').addEventListener('click', () => { inp.value = ''; ai = 0; draw() })
    const key = (e) => { if (!root.isConnected) { document.removeEventListener('keydown', key); return } if ((e.ctrlKey || e.metaKey) && e.key.toLowerCase() === 'k' && root.matches(':hover')) { e.preventDefault(); ov.__from = $(root, '.trg'); ov.classList.add('show'); inp.value = ''; ai = 0; draw(); inp.focus() } }
    document.addEventListener('keydown', key)
    draw()
  },
})

/* ---- AD-NAV-013 消息中心 ---- */
def({
  id: 'AD-NAV-013', name: '消息中心下拉', style: '分类+未读红点', stage: '', wide: false,
  fit: '顶栏铃铛的下拉：通知、待办、私信分类带未读数，点条目即标已读、红点同步减少，“全部已读”一键清零，空分类给一句说明；长消息两行截断。',
  avoid: '不要用它承载需要长时间处理的工作（那是待办页）；红点数量要和下拉里的未读一致；重要且紧急的事用提示条或通知卡，别只靠红点。',
  kw: 'message center 消息中心 通知 待办 私信 未读 红点 全部已读 铃铛 bell notification dropdown',
  css: C('adnav013', `${MENU_CSS}${MSG_CSS}${MBAR_CSS}
§ .mfr{min-height:530px}`),
  html: () => `<div class="adnav013" data-sh><div class="mfr">${miniBar(`<div class="pw"><button type="button" class="bt ib bell" data-pop="msg" aria-expanded="true" aria-label="消息">${I('bell')}<i class="dot">4</i></button><div class="pop mn rt mp open" data-pn="msg">${msgPanel(true)}</div></div>`)}</div></div>`,
  js: (root) => { pops(root); msgHook(root, true) },
})

/* ======================================================================
   二、弹层与反馈 AD-FB（详情、编辑、确认一律居中悬浮面板，不用右侧抽屉）
   ====================================================================== */
const DLG_CSS = `${MENU_CSS}${FP_CSS}${FROW_CSS}
§ .pgw{position:relative;min-height:440px;border:1px solid var(--bd2);border-radius:12px;background:var(--bg);overflow:hidden}
§ .tbr{display:flex;align-items:center;gap:10px;padding:12px 16px;background:var(--card);border-bottom:1px solid var(--bd2)}
§ .tbr .sp{flex:1}
§ .dlg{position:relative;z-index:1;width:480px;max-width:100%;max-height:100%;display:flex;flex-direction:column;border-radius:12px;background:var(--card2);box-shadow:var(--sh2)}
§ .dh{display:flex;align-items:flex-start;gap:12px;padding:18px 20px 8px}
§ .dh h4{flex:1;min-width:0;margin:0;padding-top:4px;font-size:16px;line-height:24px;font-weight:600}
§ .dx{display:inline-flex;align-items:center;justify-content:center;width:32px;height:32px;margin:-4px -8px 0 0;border-radius:8px;color:var(--ink3);flex:none}
§ .dx:hover{background:var(--bg);color:var(--ink)}
§ .db{padding:4px 20px 16px;overflow:auto;color:var(--ink2)}
§ .df{display:flex;align-items:center;justify-content:flex-end;gap:8px;padding:12px 20px 16px}
§ .df .sp{flex:1}
§ .cbx{display:inline-flex;align-items:center;gap:8px;color:var(--ink2);cursor:pointer;text-align:left}
§ .cbx i{display:inline-flex;align-items:center;justify-content:center;width:16px;height:16px;flex:none;border:1px solid var(--bd);border-radius:4px;background:var(--card);color:transparent;transition:background-color .15s var(--e),border-color .15s var(--e)}
§ .cbx i svg{width:12px;height:12px;stroke-width:3}
§ .cbx.on i{background:var(--p);border-color:var(--p);color:#fff}
§ .wi{display:inline-flex;align-items:center;justify-content:center;width:36px;height:36px;border-radius:50%;flex:none;background:var(--pt);color:var(--p-text)}
§ .wi.dg{background:var(--dgb);color:var(--dg)}§ .wi.wn{background:var(--wnb);color:var(--wn)}§ .wi.ok{background:var(--okb);color:var(--ok)}
§ .wi .ic{width:20px;height:20px}
§ .gone{display:none}
@media(max-width:520px){§ .df{flex-wrap:wrap}}
`
const cbxHook = (root, on) => root.addEventListener('click', (e) => { const c = e.target.closest('.cbx'); if (!c) return; const v = c.classList.toggle('on'); c.setAttribute('aria-checked', v); if (on) on(c, v) })
const cbxHTML = (t, n = '') => `<button type="button" class="cbx${n ? ' ' + n : ''}" role="checkbox" aria-checked="false"><i>${sv('check')}</i>${t}</button>`
const dlgOpen = (open, name, id) => `<div class="ix-ov${open ? ' show' : ''}" data-ov="${name}"><div class="ix-mask"></div>`

/* ---- AD-FB-001 说明对话框 ---- */
def({
  id: 'AD-FB-001', name: '说明对话框', style: '居中·遮罩·Esc', stage: '', wide: true,
  fit: '规则说明、操作须知、版本公告这类“读完点我知道了”的弹层：居中、带遮罩，点遮罩、右上角 × 或按 Esc 关闭，内容多时只在对话框内部滚动，可勾选“不再提示”。',
  avoid: '要用户做选择或填写时别用它（用确认框或表单弹窗）；别叠开两层对话框；标题不超过 12 字，正文超过 6 条先做成文档页。',
  kw: 'dialog modal 对话框 弹窗 说明 须知 公告 遮罩 Esc 关闭 居中 不再提示',
  css: C('adfb001', `${DLG_CSS}
§ .db p{margin:0 0 10px;color:var(--ink)}
§ .db ol{margin:0;padding:0;list-style:none;counter-reset:n}
§ .db li{position:relative;padding:10px 0 10px 28px;border-top:1px solid var(--line);counter-increment:n;line-height:1.6}
§ .db li::before{content:counter(n);position:absolute;left:0;top:11px;width:20px;height:20px;border-radius:50%;background:var(--pt);color:var(--p-text);font-size:12px;line-height:20px;text-align:center}
§ .db li b{font-weight:600;color:var(--ink)}
§ .db{max-height:300px}
`),
  html: () => `<div class="adfb001" data-sh><div class="pgw"><div class="tbr"><button type="button" class="bt" data-open="d1">${I('adshBook')}退款规则说明</button></div>${fauxPage(5)}
    ${dlgOpen(true, 'd1')}<div class="dlg pn" role="dialog" aria-modal="true" aria-labelledby="adfb001-t" tabindex="-1">
      <div class="dh"><h4 id="adfb001-t">退款规则说明</h4><button type="button" class="dx" data-close aria-label="关闭">${I('close')}</button></div>
      <div class="db"><p>处理售后前请先了解以下规则，规则调整以「经营设置」中的配置为准。</p><ol>
        <li><b>发货前退款</b>：顾客可直接申请，系统自动通过并原路退回，无需人工审核。</li>
        <li><b>发货后退款</b>：需先寄回商品，商家收货后 24 小时内处理，超时自动同意。</li>
        <li><b>优惠分摊</b>：满减和优惠券按商品金额分摊，部分退款按分摊后的实付金额退回。</li>
        <li><b>储值支付</b>：使用储值余额支付的订单，退款退回储值账户，不转为现金。</li>
        <li><b>手续费</b>：由「经营设置」中的退款手续费规则决定，当前为 0.6%，不足 1 元按 1 元收取，因商家原因退款不收。</li></ol></div>
      <div class="df">${cbxHTML('7 天内不再提示')}<span class="sp"></span><button type="button" class="bt pri lg" data-close data-autofocus>我知道了</button></div></div></div></div></div>`,
  js: (root) => { overlays(root); cbxHook(root) },
})

/* ---- AD-FB-002 危险操作确认框 ---- */
const PROD2 = [['陶瓷马克杯 350ml 手作釉面款', '在售', 2], ['保温水杯 鼠尾草绿 500ml', '在售', 6], ['护眼台灯 无频闪三档调光', '已下架', 5]]
def({
  id: 'AD-FB-002', name: '危险操作确认框', style: '写清后果', stage: '', wide: true,
  fit: '删除、停业、清空这类不可撤销的操作：标题带对象名，正文逐条写影响范围，需勾选“我已了解”才能点危险按钮，取消在左、危险按钮在右，提交中保持窗口并显示进度，成功后列表同步。',
  avoid: '可撤销或影响很小的操作（行内开关、改名）不要弹确认，改成成功提示 + 撤销；别用“确定/取消”这种看不出后果的按钮名，按钮写动作（删除商品）。',
  kw: 'confirm 确认框 危险操作 删除 二次确认 不可恢复 后果 影响范围 destructive 危险按钮',
  css: C('adfb002', `${DLG_CSS}
§ .dlg{width:460px}
§ .dh{align-items:flex-start}
§ .dh h4{padding-top:6px}
§ .db{padding-left:68px}
§ .db p{margin:0 0 6px;color:var(--ink)}
§ .imp{margin:0 0 14px;padding:0;list-style:none}
§ .imp li{position:relative;padding:3px 0 3px 14px;line-height:1.6}
§ .imp li::before{content:"";position:absolute;left:0;top:12px;width:5px;height:5px;border-radius:50%;background:var(--danger-fill)}
§ .tbl{width:100%;border-collapse:collapse;background:var(--card)}
§ .tbl th{height:44px;padding:0 16px;background:var(--bg);color:var(--ink2);font-weight:600;text-align:center}
§ .tbl td{height:48px;padding:0 16px;border-bottom:1px solid var(--line);text-align:center}
§ .tbl td.l{text-align:left;padding-left:24px}
§ .tbl tr.out{opacity:0;transition:opacity .25s var(--e)}
§ .box2{margin:12px 16px 16px;border:1px solid var(--bd2);border-radius:12px;overflow:hidden;background:var(--card)}
§ .emp{padding:28px;text-align:center;color:var(--ink3)}
`),
  html: () => `<div class="adfb002" data-sh><div class="pgw"><div class="tbr"><span class="sp"></span><button type="button" class="bt" data-reset>重置示例</button></div>
    <div class="box2"><table class="tbl"><thead><tr><th>商品</th><th>状态</th><th>操作</th></tr></thead><tbody data-tb>${PROD2.map(([n, s], i) => `<tr data-row><td class="l">${n}</td><td><span class="tg2 ${s === '在售' ? 'ok' : ''}">${s}</span></td><td><button type="button" class="bt txt dg" data-open="d2" data-n="${n}">删除</button></td></tr>`).join('')}</tbody></table><div class="emp" hidden>商品已全部删除，点右上角“重置示例”重新体验</div></div>
    ${dlgOpen(true, 'd2')}<div class="dlg pn" role="alertdialog" aria-modal="true" aria-labelledby="adfb002-t" aria-describedby="adfb002-d" tabindex="-1">
      <div class="dh"><span class="wi dg">${I('alert')}</span><h4 id="adfb002-t" data-title>删除商品「陶瓷马克杯 350ml 手作釉面款」？</h4></div>
      <div class="db" id="adfb002-d"><p>删除后将产生以下影响：</p><ul class="imp"><li>商品将从 3 个门店同时下架，购物车里的 12 位顾客会看到“商品已下架”</li><li>进行中的 2 个订单不受影响，仍可正常发货与售后</li><li>删除后无法恢复，历史订单保留商品快照</li></ul>${cbxHTML('我已了解以上影响', 'ag')}</div>
      <div class="df"><button type="button" class="bt lg" data-close data-autofocus>取消</button><button type="button" class="bt dng lg" data-del disabled>删除商品</button></div></div></div></div></div>`,
  js: (root) => {
    overlays(root); const ov = $(root, '.ix-ov'), del = $(root, '[data-del]'), cancel = $(root, '.df [data-close]'); let busy = false, target = $(root, 'tr[data-row]')
    ov.__esc = () => !busy
    cbxHook(root, (c, v) => { del.disabled = !v })
    root.addEventListener('click', (e) => {
      const o = e.target.closest('[data-open="d2"]'); if (o) { target = o.closest('tr'); $(root, '[data-title]').textContent = `删除商品「${o.dataset.n}」？`; $(root, '.cbx').classList.remove('on'); del.disabled = true; return }
      if (e.target.closest('[data-reset]')) { $$(root, 'tr[data-row]').forEach((r) => { r.hidden = false; r.classList.remove('out') }); $(root, '.emp').hidden = true; $(root, '.tbl').hidden = false; return }
      if (e.target.closest('.ix-mask') && busy) { e.stopPropagation(); return }
      if (!e.target.closest('[data-del]') || del.disabled || busy) return
      busy = true; del.innerHTML = '<span class="spn"></span>删除中'; del.disabled = true; cancel.disabled = true
      setTimeout(() => {
        busy = false; del.textContent = '删除商品'; cancel.disabled = false; closeOv(ov)
        if (target) { const nm = $(target, 'td').textContent; target.classList.add('out'); setTimeout(() => { target.hidden = true; if (!$$(root, 'tr[data-row]').some((r) => !r.hidden)) { $(root, '.tbl').hidden = true; $(root, '.emp').hidden = false } }, 260); say(root, `已删除商品「${nm}」`, 'ok') }
      }, 900)
    })
  },
})

/* ---- AD-FB-003 居中详情面板 ---- */
const MEM = [
  { n: '林小满', lv: '金卡会员', ph: '13800002086', bd: '1994-03-18', sex: '女', st: '旗舰店', pts: 2860, spent: 12860, reg: '2024-05-12', rem: '偏好无糖饮品，周末常带孩子到店，生日当月发过一次优惠券', i: 0 },
  { n: '陈晓雨', lv: '银卡会员', ph: '13900015531', bd: '1990-11-02', sex: '女', st: '中心城店', pts: 960, spent: 4320, reg: '2025-01-20', rem: '', i: 1 },
  { n: '王子豪', lv: '普通会员', ph: '13700034417', bd: '1998-07-26', sex: '男', st: '星湖街店', pts: 180, spent: 899, reg: '2025-09-03', rem: '', i: 2 },
  { n: '李安然', lv: '金卡会员', ph: '13600048820', bd: '1987-01-09', sex: '女', st: '旗舰店', pts: 3410, spent: 15270, reg: '2023-12-30', rem: '企业采购联系人', i: 3 },
]
const maskP = (p) => p.slice(0, 3) + '****' + p.slice(7)
const LVT = { 金卡会员: 'wn', 银卡会员: 'in', 普通会员: '' }
def({
  id: 'AD-FB-003', name: '居中详情面板', style: '查看编辑合一', stage: '', wide: true,
  fit: '会员、订单、商品这类“点一行看详情、顺手改一下”的场景：居中悬浮面板（不用右侧抽屉），顶部对象信息 + 标签页，内容超出只在面板内滚动；点“编辑”原地变表单，保存后回到查看并同步列表行。',
  avoid: '内容少于 3 个字段时用表单弹窗；复杂的多步流程用独立页面；关闭面板后要回到列表原位置并保留筛选与滚动，别刷新列表。',
  kw: 'detail panel 详情面板 居中悬浮 详情 编辑 会员详情 弹窗 modal 标签页 查看编辑切换 不用抽屉 drawer',
  css: C('adfb003', `${DLG_CSS}
§ .pgw{min-height:600px}
§ .tbl{width:100%;border-collapse:collapse;background:var(--card)}
§ .tbl th{height:44px;padding:0 16px;background:var(--bg);color:var(--ink2);font-weight:600;text-align:center}
§ .tbl td{height:52px;padding:0 16px;border-bottom:1px solid var(--line);text-align:center}
§ .tbl td.l{text-align:left;padding-left:24px}
§ .tbl td.r{text-align:right;padding-right:32px;font-variant-numeric:tabular-nums}
§ .tbl tbody tr{cursor:pointer;transition:background-color .15s var(--e)}
§ .tbl tbody tr:hover{background:var(--bg)}
§ .nmc{display:inline-flex;align-items:center;gap:10px}
§ .box2{margin:12px 16px 16px;border:1px solid var(--bd2);border-radius:12px;overflow:hidden;background:var(--card)}
§ .dlg{width:720px;max-height:100%;min-height:440px}
§ .hd3{display:flex;align-items:center;gap:14px;padding:20px 24px 16px}
§ .hd3 .nm{flex:1;min-width:0}
§ .hd3 b{font-size:18px;font-weight:600}
§ .hd3 .tt{display:flex;align-items:center;gap:8px;flex-wrap:wrap}
§ .hd3 p{margin:2px 0 0;font-size:13px;color:var(--ink3)}
§ .hd3 .dx{margin:-6px -8px 0 0;align-self:flex-start}
§ .sts{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:12px;margin-bottom:18px}
§ .sts div{padding:10px 14px;border-radius:8px;background:var(--bg)}
§ .sts span{display:block;font-size:12px;color:var(--ink3)}
§ .sts b{font-size:18px;font-weight:600;font-variant-numeric:tabular-nums}
§ .tabs3{position:relative;display:flex;gap:28px;padding:0 24px;overflow-x:auto;scrollbar-width:none;box-shadow:inset 0 -1px 0 var(--line)}
§ .tabs3::-webkit-scrollbar{display:none}
§ .tabs3>button{height:44px;color:var(--ink2);display:inline-flex;align-items:center;flex:none;white-space:nowrap}
§ .tabs3>button span{display:inline-flex;flex-direction:column}
§ .tabs3>button span::after{content:attr(data-w);height:0;overflow:hidden;visibility:hidden;font-weight:600}
§ .tabs3>button.on{color:var(--p-text);font-weight:600}
§ .tabs3 .ink{position:absolute;bottom:0;height:2px;background:var(--p);transition:left .25s var(--e),width .25s var(--e)}
§ .db3{flex:1;min-height:0;padding:18px 24px;overflow:auto;color:var(--ink)}
§ .kv{display:grid;grid-template-columns:96px 1fr 96px 1fr;gap:14px 12px;margin:0}
§ .kv dt{color:var(--ink3)}
§ .kv dd{margin:0;min-width:0}
§ .kv .w{grid-column:2 / -1}
§ .lk3{margin-left:8px;color:var(--p-text)}
§ .lk3:hover{text-decoration:underline}
§ .fm{display:grid;grid-template-columns:1fr 1fr;gap:14px 20px}
§ .fm .fld{min-width:0}
§ .fm .fld.w{grid-column:1 / -1}
§ .fm label{display:block;margin-bottom:6px;font-size:13px;color:var(--ink2)}
§ .fm label i{color:var(--dg);font-style:normal}
§ .er{margin:4px 0 0;font-size:12px;color:var(--dg)}
§ .ip.bad{border-color:var(--dg)}
§ .cnt{margin-top:4px;text-align:right;font-size:12px;color:var(--ink3)}
§ .r3{display:flex;align-items:center;gap:12px;min-height:48px;border-bottom:1px solid var(--line)}
§ .r3:last-child{border-bottom:0}
§ .r3 .a{width:88px;color:var(--ink3);font-variant-numeric:tabular-nums}
§ .r3 .b{flex:1;min-width:0}
§ .r3 .c{width:96px;text-align:right;font-variant-numeric:tabular-nums}
§ .tln{list-style:none;margin:0;padding:0}
§ .tln li{position:relative;padding:0 0 14px 20px;color:var(--ink2)}
§ .tln li::before{content:"";position:absolute;left:3px;top:7px;width:8px;height:8px;border-radius:50%;background:var(--pm)}
§ .tln li::after{content:"";position:absolute;left:6.5px;top:17px;bottom:-2px;width:1px;background:var(--line)}
§ .tln li:last-child::after{display:none}
§ .tln b{font-weight:600;color:var(--ink)}
§ .tln time{display:block;font-size:12px;color:var(--ink3)}
@media(max-width:640px){§ .kv{grid-template-columns:88px 1fr}§ .kv .w{grid-column:2}§ .fm{grid-template-columns:1fr}}
`),
  html: () => `<div class="adfb003" data-sh><div class="pgw"><div class="tbr"><span class="sp"></span><span class="tg2">点击任意一行查看详情</span></div>
    <div class="box2"><table class="tbl"><thead><tr><th>会员</th><th>等级</th><th>手机号</th><th>累计消费</th></tr></thead><tbody data-tb>${MEM.map((m, k) => `<tr data-open="d3" data-k="${k}" tabindex="0"><td class="l"><span class="nmc">${critter(m.i, 32)}<span data-nm>${m.n}</span></span></td><td><span class="tg2 ${LVT[m.lv]}" data-lv>${m.lv}</span></td><td data-ph>${maskP(m.ph)}</td><td class="r" data-sp>¥${m.spent.toLocaleString('zh-CN')}.00</td></tr>`).join('')}</tbody></table></div>
    ${dlgOpen(true, 'd3')}<div class="dlg pn" role="dialog" aria-modal="true" aria-label="会员详情" tabindex="-1">
      <div class="hd3" data-hd></div>
      <div class="tabs3" data-ix="tabs" data-g="m3" role="tablist">${[['a', '基本信息'], ['b', '消费记录'], ['c', '操作日志']].map(([k, t], i) => `<button type="button" role="tab" data-t="${k}" class="${i ? '' : 'on'}"><span data-w="${t}">${t}</span></button>`).join('')}<i class="ink"></i></div>
      <div class="db3" data-b></div>
      <div class="df" data-ft></div></div></div></div></div>`,
  js: (root) => {
    overlays(root); const ov = $(root, '.ix-ov'); let k = 0, mode = 'view', phShown = false
    const rows = $$(root, 'tbody tr')
    const view = () => {
      const m = MEM[k]
      $(root, '[data-hd]').innerHTML = `${critter(m.i, 48)}<div class="nm"><div class="tt"><b>${m.n}</b><span class="tg2 ${LVT[m.lv]}">${m.lv}</span><span class="tg2 ok">正常</span></div><p>${m.st} · 注册于 ${m.reg}</p></div><button type="button" class="dx" data-close aria-label="关闭">${I('close')}</button>`
      const body = {
        a: mode === 'view'
          ? `<div class="sts"><div><span>累计订单</span><b>${m.orders || 28} 单</b></div><div><span>平均客单价</span><b>¥${Math.round(m.spent / (m.orders || 28)).toLocaleString('zh-CN')}</b></div><div><span>最近消费</span><b>11-02</b></div></div><dl class="kv"><dt>性别</dt><dd>${m.sex}</dd><dt>生日</dt><dd>${m.bd}</dd><dt>手机号</dt><dd>${phShown ? m.ph.replace(/(\d{3})(\d{4})(\d{4})/, '$1 $2 $3') : maskP(m.ph)}<button type="button" class="lk3" data-phs>${phShown ? '隐藏' : '显示'}</button></dd><dt>所属门店</dt><dd>${m.st}</dd><dt>积分余额</dt><dd>${m.pts.toLocaleString('zh-CN')}</dd><dt>累计消费</dt><dd>¥${m.spent.toLocaleString('zh-CN')}.00</dd><dt>备注</dt><dd class="w">${m.rem || '—'}</dd></dl>`
          : `<div class="fm"><div class="fld"><label for="f3n">姓名 <i>*</i></label><input class="ip" id="f3n" data-f="n" value="${m.n}" maxlength="10"><p class="er" data-er="n" hidden>请填写姓名（2–10 个字）</p></div><div class="fld"><label for="f3p">手机号 <i>*</i></label><input class="ip" id="f3p" data-f="ph" value="${m.ph}" maxlength="11" inputmode="numeric"><p class="er" data-er="ph" hidden>手机号应为 11 位数字</p></div><div class="fld"><label for="f3b">生日</label><input class="ip" id="f3b" data-f="bd" value="${m.bd}" placeholder="YYYY-MM-DD"></div><div class="fld"><label>所属门店</label><div class="ip" style="display:flex;align-items:center;background:var(--bg);color:var(--ink3)">${m.st}</div></div><div class="fld w"><label for="f3r">备注</label><textarea class="ip" id="f3r" data-f="rem" rows="3" maxlength="100">${m.rem}</textarea><div class="cnt"><span data-c>${m.rem.length}</span>/100</div></div></div>`,
        b: [['11-02', '无线降噪耳机', 599], ['10-18', '保湿精华', 258], ['09-27', '陶瓷马克杯', 69], ['09-03', '轻量跑鞋', 329]].map(([d, n, a]) => `<div class="r3"><span class="a">${d}</span><span class="b">${n}</span><span class="c">¥${a}.00</span></div>`).join(''),
        c: `<ul class="tln" data-log>${(m.log || []).concat([['发放生日优惠券 满 100 减 20', '系统', '2026-03-01 00:00'], ['升级为' + m.lv, '系统', '2025-08-16 12:30'], ['注册成为会员', m.n, m.reg + ' 10:12']]).map(([t, w, ti], j) => `<li><b>${t}</b> · ${w}<time>${ti}</time></li>`).join('')}</ul>`,
      }
      const cur = $(root, '.tabs3 .on').dataset.t
      $(root, '[data-b]').innerHTML = body[cur]
      $(root, '[data-ft]').innerHTML = mode === 'view' ? `<button type="button" class="bt lg" data-close>关闭</button><button type="button" class="bt pri lg" data-edit>${I('edit')}编辑</button>` : `<button type="button" class="bt lg" data-cancel>取消</button><button type="button" class="bt pri lg" data-save>保存</button>`
    }
    const open = (i) => { k = i; mode = 'view'; phShown = false; $$(root, '.tabs3 [data-t]').forEach((t, j) => t.classList.toggle('on', j === 0)); view(); requestAnimationFrame(() => { const t = $(root, '.tabs3'); const on = $(t, '.on'), ink = $(t, '.ink'); ink.style.left = on.offsetLeft + 'px'; ink.style.width = on.offsetWidth + 'px' }) }
    root.addEventListener('click', (e) => {
      const r = e.target.closest('tr[data-open]'); if (r) { open(+r.dataset.k); return }
      if (e.target.closest('.tabs3 [data-t]')) { setTimeout(view, 0); return }
      if (e.target.closest('[data-phs]')) { phShown = !phShown; view(); return }
      if (e.target.closest('[data-edit]')) { mode = 'edit'; $(root, '.tabs3 [data-t="a"]').click(); setTimeout(() => { view(); const f = $(root, '[data-f="n"]'); if (f) f.focus() }, 0); return }
      if (e.target.closest('[data-cancel]')) { mode = 'view'; view(); return }
      if (e.target.closest('[data-save]')) {
        const n = $(root, '[data-f="n"]'), p = $(root, '[data-f="ph"]'); let ok = true
        const nv = n.value.trim(), pv = p.value.trim()
        const bad = (el, key, f) => { el.classList.toggle('bad', f); $(root, `[data-er="${key}"]`).hidden = !f; if (f) ok = false }
        bad(n, 'n', nv.length < 2); bad(p, 'ph', !/^\d{11}$/.test(pv))
        if (!ok) { ($(root, '.ip.bad') || n).focus(); return }
        const m = MEM[k]; m.n = nv; m.ph = pv; m.bd = $(root, '[data-f="bd"]').value.trim() || m.bd; m.rem = $(root, '[data-f="rem"]').value.trim()
        m.log = [['修改会员资料', '林小满（店长）', '2026-11-04 15:30']].concat(m.log || [])
        const row = rows[k]; $(row, '[data-nm]').textContent = m.n; $(row, '[data-ph]').textContent = maskP(m.ph)
        mode = 'view'; view(); say(root, '已保存，列表已同步', 'ok'); return
      }
    })
    root.addEventListener('input', (e) => { const t = e.target; if (t.matches('[data-f]')) { t.classList.remove('bad'); const er = $(root, `[data-er="${t.dataset.f}"]`); if (er) er.hidden = true; if (t.dataset.f === 'rem') $(root, '[data-c]').textContent = t.value.length } })
    rows.forEach((r) => r.addEventListener('keydown', (e) => { if (e.key === 'Enter') r.click() }))
    open(0)
  },
})

/* ---- AD-FB-004 提示条 ---- */
const ALERTS = [
  { t: 'mu', ic: 'adshDesk', b: '当前是测试环境', d: '这里的订单、会员都是演示数据，不会影响线上经营。', fixed: 1 },
  { t: 'in', ic: 'info', b: '新版订单中心已上线', d: '旧版入口将于 12 月 1 日下线，历史数据已自动迁移，无需手动操作。', link: '了解详情' },
  { t: 'ok', ic: 'checkc', b: '导入完成', d: '共 128 条，成功 126 条，已自动跳过 2 条重复记录。', link: '查看结果' },
  { t: 'wn', ic: 'alert', b: '营业时间将在今晚 23:00 生效', d: '生效后小程序按新时间接单，在途订单不受影响。', act: '立即生效' },
  { t: 'dg', ic: 'closec', b: '支付回调连续 3 次失败', d: '影响：新订单可能一直显示“待付款”。下一步：检查商户号与回调地址，仍未恢复请联系技术支持。', acts: ['重新检测', '查看日志'], fixed: 1 },
]
def({
  id: 'AD-FB-004', name: '提示条', style: '四种语气', stage: '', wide: false,
  fit: '页面内常驻的说明与结果：信息、成功、警告、危险四种语气，标题一句话 + 说明写影响与下一步，可带 1–2 个动作，次要提示可关闭，重要错误常驻直到处理（处理后自动变成功）。',
  avoid: '一屏最多同时出现 2 条；不要拿它做瞬时反馈（用轻提示）；不要所有提示都用红色，危险色只给会造成损失的问题。',
  kw: 'alert 提示条 横幅 banner 警告 成功 信息 错误 可关闭 公告 通知条 callout',
  css: C('adfb004', `${MENU_CSS}
§ .wrp{padding:6px 0}
§ .alw{display:grid;grid-template-rows:1fr;transition:grid-template-rows .25s var(--e),opacity .2s var(--e)}
§ .alw>div{overflow:hidden;padding-bottom:10px}
§ .alw.gone{grid-template-rows:0fr;opacity:0}
§ .al{display:flex;align-items:flex-start;gap:12px;padding:12px 14px;border:1px solid;border-radius:8px}
§ .al.mu{background:var(--mub);border-color:var(--n6)}
§ .al.in{background:var(--pt);border-color:var(--pm)}
§ .al.ok{background:var(--okb);border-color:var(--ok-line)}
§ .al.wn{background:var(--wnb);border-color:#EBDCB8}
§ .al.dg{background:var(--dgb);border-color:#EACCC8}
§ .al>.ic{width:20px;height:20px;margin-top:2px}
§ .al.mu>.ic{color:var(--mu)}§ .al.in>.ic{color:var(--p-text)}§ .al.ok>.ic{color:var(--ok)}§ .al.wn>.ic{color:var(--wn)}§ .al.dg>.ic{color:var(--dg)}
§ .ab{flex:1;min-width:0}
§ .ab b{display:block;font-weight:600}
§ .ab p{margin:2px 0 0;color:var(--ink2);line-height:1.6}
§ .aa{display:flex;align-items:center;flex-wrap:wrap;gap:8px;margin-top:10px}
§ .aa .bt{height:32px}
§ .lnk{color:var(--p-text);text-decoration:underline;text-underline-offset:3px}
§ .al .cl{display:inline-flex;align-items:center;justify-content:center;width:28px;height:28px;margin:-4px -6px 0 0;border-radius:4px;color:var(--ink3);flex:none}
§ .al .cl:hover{background:color-mix(in srgb,var(--scrim) 7%,transparent);color:var(--ink)}
§ .al .cl svg{width:14px;height:14px}
§ .none{display:flex;align-items:center;justify-content:space-between;gap:12px;padding:14px 16px;border:1px dashed var(--bd);border-radius:8px;color:var(--ink3)}
`),
  html: () => `<div class="adfb004" data-sh><div class="wrp" data-list>${ALERTS.map((a, i) => `<div class="alw"><div><div class="al ${a.t}" role="${a.t === 'dg' ? 'alert' : 'status'}" ${a.t === 'dg' ? 'data-risk' : ''}>${I(a.ic)}<div class="ab"><b>${a.b}</b><p>${a.d}</p>${a.link ? `<div class="aa"><button type="button" class="lnk" data-toast="${a.link}（示例）">${a.link}</button></div>` : ''}${a.act ? `<div class="aa"><button type="button" class="bt" data-do="${a.act}">${a.act}</button></div>` : ''}${a.acts ? `<div class="aa"><button type="button" class="bt" data-recheck>${a.acts[0]}</button><button type="button" class="bt txt" data-toast="已打开：回调日志">${a.acts[1]}</button></div>` : ''}</div>${a.fixed ? '' : `<button type="button" class="cl" aria-label="关闭提示">${sv('close')}</button>`}</div></div></div>`).join('')}</div>
    <div class="none" data-none hidden><span>可关闭的提示都已关闭</span><button type="button" class="bt" data-restore>恢复示例</button></div></div>`,
  js: (root) => {
    const list = $(root, '[data-list]')
    const closeA = (w) => { w.classList.add('gone'); setTimeout(() => { w.hidden = true; if (!$$(root, '.alw:not([hidden])').some((x) => $(x, '.cl'))) $(root, '[data-none]').hidden = false }, 260) }
    root.addEventListener('click', (e) => {
      const c = e.target.closest('.cl'); if (c) { closeA(c.closest('.alw')); return }
      const d = e.target.closest('[data-do]'); if (d) { const w = d.closest('.al'); d.disabled = true; d.innerHTML = '<span class="spn"></span>生效中'; setTimeout(() => { w.className = 'al ok'; w.querySelector('.ic').innerHTML = sv('checkc'); $(w, 'b').textContent = '营业时间已生效'; $(w, 'p').textContent = '小程序已按新营业时间接单。'; $(w, '.aa').remove() }, 700); return }
      const r = e.target.closest('[data-recheck]'); if (r) {
        const w = r.closest('.al'); r.disabled = true; r.innerHTML = '<span class="spn"></span>检测中'
        setTimeout(() => { w.className = 'al ok'; w.removeAttribute('data-risk'); $(w, '.ic').innerHTML = sv('checkc'); $(w, 'b').textContent = '支付回调已恢复'; $(w, 'p').textContent = '最近一次回调成功（11-04 15:28），待付款订单会在几分钟内自动更新。'; $(w, '.aa').remove(); if (!$(w, '.cl')) { const b = document.createElement('button'); b.type = 'button'; b.className = 'cl'; b.setAttribute('aria-label', '关闭提示'); b.innerHTML = sv('close'); w.appendChild(b) } }, 900); return
      }
      if (e.target.closest('[data-restore]')) { $$(root, '.alw').forEach((x) => { x.hidden = false; x.classList.remove('gone') }); $(root, '[data-none]').hidden = true }
    })
  },
})

/* ---- AD-FB-005 通知卡 ---- */
const NOTI = {
  ord: { t: 'in', ic: 'receipt', b: '收到新订单 SO2026110533', d: '林小满 · ¥599.00 · 无线降噪耳机，已支付，等待发货', a: ['去处理'] },
  stock: { t: 'wn', ic: 'alert', b: '库存预警', d: '保温水杯（鼠尾草绿 500ml）仅剩 12 件，低于预警值 20 件', a: ['去补货'] },
  pay: { t: 'dg', ic: 'closec', b: '支付回调失败', d: '微信支付回调连续失败 3 次，新订单可能显示“待付款”，请检查商户号配置', a: ['查看详情'], stay: 1 },
  exp: { t: 'ok', ic: 'checkc', b: '导出完成', d: '「10 月订单明细」已生成，共 1,286 条，文件保留 7 天', a: ['下载文件'] },
}
def({
  id: 'AD-FB-005', name: '通知卡', style: '右上角堆叠', stage: '', wide: true,
  fit: '需要引起注意但不打断操作的系统事件（新订单、库存预警、导出完成、支付失败）：右上角向下堆叠，最多 4 条，普通通知 6 秒自动消失（悬停暂停），错误类常驻直到点关闭，可带一个动作。',
  avoid: '用户自己刚做的操作结果用轻提示，不要用通知卡；别连续刷屏，同类事件合并成一条并写数量；重要通知要同步进消息中心，防止错过。',
  kw: 'notification 通知卡 通知 右上角 堆叠 toast 新订单 预警 自动关闭 常驻 notice',
  css: C('adfb005', `${MENU_CSS}${FP_CSS}${FROW_CSS}
§ .pgw{position:relative;min-height:430px;border:1px solid var(--bd2);border-radius:12px;background:var(--bg);overflow:hidden}
§ .tbr{display:flex;align-items:center;flex-wrap:wrap;gap:8px;padding:12px 16px;background:var(--card);border-bottom:1px solid var(--bd2)}
§ .tbr .sp{flex:1}
§ .stk{position:absolute;top:70px;right:16px;z-index:30;display:flex;flex-direction:column;gap:10px;width:360px;max-width:calc(100% - 32px)}
§ .nt{position:relative;display:flex;gap:12px;padding:14px 14px 16px 14px;border-radius:12px;background:var(--card);border:1px solid var(--bd2);box-shadow:var(--sh2);overflow:hidden;animation:adfb005-in .24s var(--e)}
§ .nt.out{opacity:0;transform:translateX(24px);transition:opacity .2s var(--e),transform .2s var(--e)}
§ .ni{display:flex;align-items:center;justify-content:center;width:32px;height:32px;border-radius:8px;flex:none;background:var(--pt);color:var(--p-text)}
§ .nt.wn .ni{background:var(--wnb);color:var(--wn)}§ .nt.dg .ni{background:var(--dgb);color:var(--dg)}§ .nt.ok .ni{background:var(--okb);color:var(--ok)}
§ .nb{flex:1;min-width:0}
§ .nb b{display:block;padding-right:24px;font-weight:600}
§ .nb p{margin:2px 0 0;font-size:13px;line-height:1.55;color:var(--ink2);display:-webkit-box;-webkit-line-clamp:2;-webkit-box-orient:vertical;overflow:hidden}
§ .nb .na{display:flex;align-items:center;gap:10px;margin-top:8px;font-size:12px;color:var(--ink3)}
§ .nb .na .bt{height:28px;padding:0 10px;font-size:13px}
§ .xx{position:absolute;right:8px;top:8px;display:inline-flex;align-items:center;justify-content:center;width:28px;height:28px;border-radius:4px;color:var(--ink3)}
§ .xx:hover{background:var(--bg);color:var(--ink)}
§ .xx svg{width:14px;height:14px}
§ .nt .prg{position:absolute;left:0;bottom:0;height:3px;width:100%;background:var(--pm);transform-origin:left;animation:adfb005-run 6s linear forwards}
§ .nt.wn .prg{background:#E6D5A8}§ .nt.ok .prg{background:#BFD9C8}
§ .nt:hover .prg{animation-play-state:paused}
§ .nt.stay .prg{display:none}
§ .cnt5{font-size:13px;color:var(--ink3)}
@media(max-width:700px){§ .stk{top:124px}}
@keyframes adfb005-in{from{opacity:0;transform:translateX(28px)}}
@keyframes adfb005-run{to{transform:scaleX(0)}}
`),
  html: () => `<div class="adfb005" data-sh><div class="pgw"><div class="tbr"><span class="cnt5">模拟事件：</span><button type="button" class="bt" data-n="ord">新订单</button><button type="button" class="bt" data-n="stock">库存预警</button><button type="button" class="bt" data-n="exp">导出完成</button><button type="button" class="bt" data-n="pay">支付失败</button><span class="sp"></span><span class="cnt5" data-cnt></span><button type="button" class="bt txt" data-clear>全部清除</button></div>${fauxPage(5)}
    <div class="stk" role="region" aria-label="通知" aria-live="polite" data-stk></div></div></div>`,
  js: (root) => {
    const stk = $(root, '[data-stk]'), MAX = 4
    const cnt = () => { const n = $$(stk, '.nt:not(.out)').length; $(root, '[data-cnt]').textContent = n ? `当前 ${n} 条` : '没有通知'; $(root, '[data-clear]').disabled = !n }
    const rm = (nt) => { if (!nt || nt.classList.contains('out')) return; nt.classList.add('out'); setTimeout(() => { nt.remove(); cnt() }, 210); cnt() }
    const push = (key, first) => {
      const o = NOTI[key]; const nt = document.createElement('div'); nt.className = `nt ${o.t}${o.stay ? ' stay' : ''}`; nt.setAttribute('role', o.t === 'dg' ? 'alert' : 'status')
      nt.innerHTML = `<span class="ni">${I(o.ic)}</span><div class="nb"><b>${o.b}</b><p>${o.d}</p><div class="na"><button type="button" class="bt" data-act>${o.a[0]}</button><span>${first ? '10 分钟前' : '刚刚'}</span></div></div><button type="button" class="xx" aria-label="关闭通知">${sv('close')}</button><i class="prg"></i>`
      stk.prepend(nt); const all = $$(stk, '.nt:not(.out)'); if (all.length > MAX) rm(all[all.length - 1])
      nt.querySelector('.prg').addEventListener('animationend', () => rm(nt)); cnt()
    }
    root.addEventListener('click', (e) => {
      const b = e.target.closest('[data-n]'); if (b) { push(b.dataset.n); return }
      if (e.target.closest('[data-clear]')) { $$(stk, '.nt').forEach(rm); return }
      const x = e.target.closest('.xx'); if (x) { rm(x.closest('.nt')); return }
      const a = e.target.closest('[data-act]'); if (a) { const nt = a.closest('.nt'); say(root, `已打开：${a.textContent}`, 'in'); rm(nt) }
    })
    push('stock', true); push('ord', true); cnt()
  },
})

/* ---- AD-FB-006 气泡确认 Popconfirm ---- */
const COUPONS = [['春季焕新满减券', '进行中', 1286], ['新客首单立减 10 元', '进行中', 3420], ['会员日 8 折券（仅限金卡会员使用）', '已停用', 214], ['端午限时赠品活动', '已结束', 902]]
def({
  id: 'AD-FB-006', name: '气泡确认', style: '就近确认', stage: '', wide: false,
  fit: '表格行内“停用、删除”这类轻量的二次确认：气泡贴着按钮弹出，写清对象和后果，取消在左、确认在右，点外面或按 Esc 关闭；位置不够时自动翻到下方。',
  avoid: '后果很重（影响资金、批量、不可恢复）用居中确认框；一次只开一个气泡；启用这类可立即恢复的操作不要确认，直接生效并轻提示。',
  kw: 'popconfirm 气泡确认 行内确认 删除确认 停用 二次确认 popover confirm 就近 轻量确认',
  css: C('adfb006', `${MENU_CSS}
§{padding-bottom:150px}
§ .box{border:1px solid var(--bd2);border-radius:12px;background:var(--card);overflow:visible}
§ table{width:100%;border-collapse:collapse;min-width:520px}
§ th{height:44px;padding:0 16px;background:var(--bg);color:var(--ink2);font-weight:600;text-align:center;white-space:nowrap}
§ th:first-child{border-radius:11px 0 0 0}§ th:last-child{border-radius:0 11px 0 0}
§ td{height:48px;padding:0 12px;border-bottom:1px solid var(--line);text-align:center;white-space:nowrap}
§ tr:last-child td{border-bottom:0}
§ td.l{text-align:left;padding-left:24px;max-width:240px;overflow:hidden;text-overflow:ellipsis}
§ td .bt.txt{height:32px}
§ tr.out{opacity:0;transition:opacity .25s var(--e)}
§ tr.off td:not(:last-child){color:var(--ink3)}
§ .pc{position:absolute;z-index:40;width:276px;padding:14px 16px 12px;border-radius:12px;background:var(--card);border:1px solid var(--bd2);box-shadow:var(--sh2);animation:adfb006-in .16s var(--e)}
§ .pc::after{content:"";position:absolute;left:var(--ax,50%);bottom:-6px;width:10px;height:10px;background:var(--card);border-right:1px solid var(--bd2);border-bottom:1px solid var(--bd2);transform:translateX(-50%) rotate(45deg)}
§ .pc.below::after{bottom:auto;top:-6px;border:0;border-left:1px solid var(--bd2);border-top:1px solid var(--bd2)}
§ .pch{display:flex;align-items:flex-start;gap:8px;font-weight:600}
§ .pch .ic{width:18px;height:18px;margin-top:3px;color:var(--wn)}
§ .pc.dg .pch .ic{color:var(--dg)}
§ .pc p{margin:4px 0 0 26px;font-size:13px;line-height:1.55;color:var(--ink2)}
§ .pcf{display:flex;justify-content:flex-end;gap:8px;margin-top:12px}
§ .emp{padding:30px;text-align:center;color:var(--ink3)}
@keyframes adfb006-in{from{opacity:0}}
`),
  html: () => `<div class="adfb006" data-sh><div class="box" style="overflow-x:auto"><table><thead><tr><th>活动名称</th><th>状态</th><th>已领取</th><th>操作</th></tr></thead><tbody>${COUPONS.map(([n, s, c]) => `<tr data-row class="${s === '进行中' ? '' : 'off'}"><td class="l" title="${n}">${n}</td><td><span class="tg2${s === '进行中' ? ' ok' : ''}" data-s>${s}</span></td><td>${c.toLocaleString('zh-CN')}</td><td><button type="button" class="bt txt" data-toast="打开：编辑「${n}」">编辑</button>${s === '已结束' ? '<button type="button" class="bt txt dis" disabled data-tip="已结束的活动不能停用">停用</button>' : `<button type="button" class="bt txt" data-pc="off" data-n="${n}">${s === '进行中' ? '停用' : '启用'}</button>`}<button type="button" class="bt txt dg" data-pc="del" data-n="${n}">删除</button></td></tr>`).join('')}</tbody></table><div class="emp" hidden>活动都已删除，刷新页面可恢复示例</div></div></div>`,
  js: (root) => {
    const host = $(root, '[data-sh]'), pc = document.createElement('div'); pc.className = 'pc'; pc.hidden = true; pc.setAttribute('role', 'alertdialog'); host.appendChild(pc)
    let cur = null
    const close = () => { pc.hidden = true; cur = null }
    const place = (btn) => {
      const R = host.getBoundingClientRect(), r = btn.getBoundingClientRect(), w = pc.offsetWidth, h = pc.offsetHeight
      const left = Math.max(8, Math.min(R.width - w - 8, r.left - R.left + r.width / 2 - w / 2)), above = r.top - R.top > h + 16
      pc.classList.toggle('below', !above); pc.style.left = left + 'px'; pc.style.top = (above ? r.top - R.top - h - 10 : r.bottom - R.top + 10) + 'px'; pc.style.setProperty('--ax', (r.left - R.left + r.width / 2 - left) + 'px')
    }
    const open = (btn) => {
      cur = btn; const del = btn.dataset.pc === 'del', n = btn.dataset.n
      pc.className = 'pc' + (del ? ' dg' : '')
      pc.innerHTML = `<div class="pch">${I('alert')}<span>${del ? `确定删除「${n}」？` : `停用「${n}」？`}</span></div><p>${del ? '删除后无法恢复，已领取的券将一并失效。' : '停用后顾客不能再领取，已领取的券仍可使用。'}</p><div class="pcf"><button type="button" class="bt" data-no>取消</button><button type="button" class="bt ${del ? 'dng' : 'pri'}" data-yes>${del ? '删除' : '停用'}</button></div>`
      pc.hidden = false; place(btn); const no = $(pc, '[data-no]'); if (no) no.focus({ preventScroll: true })
    }
    root.addEventListener('click', (e) => {
      const b = e.target.closest('[data-pc]')
      if (b) {
        const row = b.closest('tr')
        if (b.dataset.pc === 'off' && b.textContent === '启用') { $(row, '[data-s]').className = 'tg2 ok'; $(row, '[data-s]').textContent = '进行中'; row.classList.remove('off'); b.textContent = '停用'; say(root, `已启用「${b.dataset.n}」`, 'ok'); return }
        if (cur === b) close(); else open(b); return
      }
      const y = e.target.closest('[data-yes]')
      if (y && cur) {
        const row = cur.closest('tr'), n = cur.dataset.n, del = cur.dataset.pc === 'del', btn = cur; close()
        if (del) { row.classList.add('out'); setTimeout(() => { row.remove(); if (!$$(root, 'tr[data-row]').length) $(root, '.emp').hidden = false }, 260); say(root, `已删除「${n}」`, 'ok') }
        else { $(row, '[data-s]').className = 'tg2'; $(row, '[data-s]').textContent = '已停用'; row.classList.add('off'); btn.textContent = '启用'; say(root, `已停用「${n}」，顾客不能再领取`, 'ok') }
        return
      }
      if (e.target.closest('[data-no]')) { const b2 = cur; close(); if (b2) b2.focus(); return }
    })
    root.addEventListener('keydown', (e) => { if (e.key === 'Escape' && cur) { const b = cur; close(); b.focus() } })
    const off = (e) => { if (!root.isConnected) { document.removeEventListener('pointerdown', off, true); return } if (cur && !pc.contains(e.target) && !e.target.closest('[data-pc]')) close() }
    document.addEventListener('pointerdown', off, true)
  },
})

/* ---- AD-FB-007 Tooltip 与气泡卡 ---- */
def({
  id: 'AD-FB-007', name: '提示与气泡卡', style: '悬停·聚焦·键盘', stage: '', wide: false,
  fit: '图标按钮的文字提示、被截断文字的全称、字段旁的帮助说明、人名上的悬浮名片：悬停或键盘聚焦都能出现，不遮挡触发元素，Esc 可收起，名片里的按钮可以点。',
  avoid: '提示里不放必须读到的信息（用提示条）；触屏没有悬停，关键说明别只放在这里；全称没被截断时不要再弹提示，别让提示盖住相邻的可点内容。',
  kw: 'tooltip 文字提示 气泡卡 popover 悬停 hover 帮助提示 截断 全称 名片 hover card 图标按钮提示',
  css: C('adfb007', `${MENU_CSS}
§ .gr{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:12px}
§ .cd{padding:18px 20px 22px;border:1px solid var(--bd2);border-radius:12px;background:var(--card);box-shadow:var(--sh);min-width:0}
§ .cd h4{margin:0;font-size:14px;font-weight:600}
§ .cap{margin:2px 0 20px;font-size:12px;line-height:1.5;color:var(--ink3)}
§ [data-tip]{position:relative}
§ [data-tip]::after{content:attr(data-tip);position:absolute;left:50%;bottom:calc(100% + 9px);transform:translateX(-50%) translateY(3px);width:max-content;max-width:240px;padding:6px 10px;border-radius:4px;background:var(--inv);color:#fff;font-size:12px;font-weight:400;line-height:1.5;text-align:left;white-space:normal;opacity:0;pointer-events:none;z-index:50;transition:opacity .15s var(--e),transform .15s var(--e)}
§ [data-tip]::before{content:"";position:absolute;left:50%;bottom:calc(100% + 4px);width:8px;height:8px;background:var(--inv);transform:translateX(-50%) translateY(3px) rotate(45deg);opacity:0;pointer-events:none;z-index:50;transition:opacity .15s var(--e),transform .15s var(--e)}
§ [data-tip]:hover::after,§ [data-tip]:focus-visible::after{opacity:1;transform:translateX(-50%);transition-delay:.12s}
§ [data-tip]:hover::before,§ [data-tip]:focus-visible::before{opacity:1;transform:translateX(-50%) rotate(45deg);transition-delay:.12s}
§.noTip [data-tip]::after,§.noTip [data-tip]::before{opacity:0!important}
§ .ibs{display:flex;gap:10px}
§ .trl{display:flex;align-items:center;gap:10px;height:40px}
§ .trw{display:block;flex:1;min-width:0;max-width:210px}
§ .tr{display:block;overflow:hidden;text-overflow:ellipsis;white-space:nowrap}
§ .hpw,§ .hcw{position:relative;display:inline-flex;align-items:center;gap:6px}
§ .hq{display:inline-flex;width:20px;height:20px;border-radius:50%;color:var(--ink3)}
§ .hq:hover,§ .hq:focus-visible{color:var(--p-text)}
§ .hq .ic{width:18px;height:18px}
§ .hp,§ .hc{position:absolute;left:50%;bottom:calc(100% + 10px);z-index:45;width:260px;padding:12px 14px;border-radius:12px;background:var(--card);border:1px solid var(--bd2);box-shadow:var(--sh2);opacity:0;visibility:hidden;transform:translate(-50%,4px);transition:opacity .15s var(--e),transform .15s var(--e),visibility 0s .15s}
§ .hp::after,§ .hc::after{content:"";position:absolute;left:0;right:0;top:100%;height:12px}
§ .hpw:hover .hp,§ .hpw:focus-within .hp{opacity:1;visibility:visible;transform:translate(-50%,0);transition-delay:.12s,.12s,0s}
§ .hcw:hover .hc,§ .hcw:focus-within .hc{opacity:1;visibility:visible;transform:translate(-50%,0);transition-delay:.12s,.12s,0s}
§ .hp b{display:block;font-weight:600}
§ .hp p{margin:4px 0 8px;font-size:13px;line-height:1.55;color:var(--ink2)}
§ .hp .a{font-size:13px;color:var(--p-text)}
§ .hcn{text-decoration:underline dotted;text-underline-offset:4px;color:var(--ink)}
§ .hcn:hover{color:var(--p-text)}
§ .hc{left:50%;width:280px;transform:translate(-50%,4px)}
§ .hc .top{display:flex;align-items:center;gap:12px}
§ .hc .top b{display:flex;align-items:center;gap:8px;font-weight:600}
§ .hc .top span{font-size:13px;color:var(--ink3)}
§ .hc .bt{margin-top:12px;width:100%}
§ .fld{display:flex;align-items:center;gap:4px}
§ .sent{margin:0;line-height:2;color:var(--ink2)}
@media(max-width:700px){§ .gr{grid-template-columns:1fr}}
`),
  html: () => `<div class="adfb007" data-sh><div class="gr">
    <section class="cd"><h4>文字提示</h4><p class="cap">图标按钮没有文字时，悬停或聚焦显示动作名</p><div class="ibs"><button type="button" class="bt ib" data-tip="编辑" aria-label="编辑">${I('edit')}</button><button type="button" class="bt ib" data-tip="复制订单号" aria-label="复制订单号">${I('copy')}</button><button type="button" class="bt ib" data-tip="导出当前筛选结果" aria-label="导出">${I('download')}</button><button type="button" class="bt ib" data-tip="删除后无法恢复" aria-label="删除" style="color:var(--dg)">${I('trash')}</button></div></section>
    <section class="cd"><h4>被截断的文字</h4><p class="cap">只有真的被截断才显示全称，没截断不弹</p>
      <div class="trl"><span class="trw" tabindex="0"><span class="tr">无线降噪耳机（石墨灰）旗舰款 · 主动降噪 40 小时续航 · 蓝牙 5.3 双设备连接</span></span><span class="tg2 ok">在售</span></div>
      <div class="trl"><span class="trw" tabindex="0"><span class="tr">陶瓷马克杯</span></span><span class="tg2 ok">在售</span></div></section>
    <section class="cd"><h4>帮助说明</h4><p class="cap">字段旁的问号，说明写规则与去哪里改</p>
      <div class="fld"><span>退款手续费率</span><span class="hpw"><button type="button" class="hq" aria-label="退款手续费率说明" aria-describedby="adfb007-hp">${I('adshHelp')}</button><div class="hp" id="adfb007-hp" role="tooltip"><b>退款手续费率</b><p>按退款金额的 0.6% 收取，不足 1 元按 1 元；因商家原因退款不收。</p><span class="a">在「经营设置」中修改 →</span></div></span></div></section>
    <section class="cd"><h4>悬浮名片</h4><p class="cap">鼠标移到人名上看角色和联系方式，卡片里的按钮可点</p>
      <div class="sent">订单由 <span class="hcw"><button type="button" class="hcn">周一帆</button><div class="hc" role="tooltip"><div class="top">${critter(1, 40)}<div><b>周一帆<span class="tg2 in">店员</span></b><span>旗舰店 · 139****7741</span></div></div><button type="button" class="bt" data-toast="已打开与周一帆的会话">${I('chat')}发消息</button></div></span> 创建，由 <span class="hcw"><button type="button" class="hcn">林小满</button><div class="hc" role="tooltip"><div class="top">${critter(0, 40)}<div><b>林小满<span class="tg2 in">店长</span></b><span>旗舰店 · 138****2086</span></div></div><button type="button" class="bt" data-toast="已打开与林小满的会话">${I('chat')}发消息</button></div></span> 审核。</div></section></div></div>`,
  js: (root) => {
    const host = $(root, '[data-sh]')
    $$(root, '.trw').forEach((w) => { const chk = () => { const t = $(w, '.tr'); if (t.scrollWidth > t.clientWidth + 1) w.setAttribute('data-tip', t.textContent); else w.removeAttribute('data-tip') }; w.addEventListener('pointerenter', chk); w.addEventListener('focus', chk) })
    root.addEventListener('keydown', (e) => { if (e.key === 'Escape') { host.classList.add('noTip'); const h = $(root, '.hcw:focus-within,.hpw:focus-within'); if (h) document.activeElement.blur() } })
    const on = () => host.classList.remove('noTip'); root.addEventListener('pointermove', on); root.addEventListener('focusin', on)
  },
})

/* ---- AD-FB-008 轻提示与行内开关 ---- */
def({
  id: 'AD-FB-008', name: '轻提示', style: '失败写原因', stage: '', wide: false,
  fit: '操作后的即时反馈：成功只说一句（已保存），失败写清原因与下一步，保存中先显示加载再变结果；行内开关直接生效，失败时回滚并在原位写原因，可重试。',
  avoid: '需要用户必须看到并处理的信息别用轻提示（会消失，用提示条或对话框）；一次不要超过 3 条；成功提示别写成长句，失败别只写“操作失败”。',
  kw: 'message toast 轻提示 消息提示 成功 失败 加载中 保存 行内开关 回滚 原因 反馈 switch',
  css: C('adfb008', `${MENU_CSS}
§ .gr{display:grid;grid-template-columns:minmax(0,1fr) minmax(0,1.25fr);gap:12px;min-height:330px}
§ .cd{padding:18px 20px;border:1px solid var(--bd2);border-radius:12px;background:var(--card);box-shadow:var(--sh)}
§ .cd h4{margin:0 0 2px;font-size:14px;font-weight:600}
§ .cap{margin:0 0 14px;font-size:12px;color:var(--ink3)}
§ .btns{display:grid;grid-template-columns:1fr 1fr;gap:10px}
§ .btns .bt{height:36px}
§ .btns .bt .ic{color:var(--ink2)}
§ .sr{display:flex;align-items:center;gap:12px;flex-wrap:wrap;padding:12px 0;border-bottom:1px solid var(--line)}
§ .sr:last-child{border-bottom:0}
§ .sr .t{flex:1;min-width:0}
§ .sr .t b{display:block;font-weight:600}
§ .sr .t span{font-size:13px;color:var(--ink3)}
§ .swt{position:relative;flex:none;width:40px;height:22px;border-radius:11px;background:var(--n8);transition:background-color .2s var(--e)}
§ .swt::after{content:"";position:absolute;left:2px;top:2px;width:18px;height:18px;border-radius:50%;background:var(--card);box-shadow:0 1px 3px var(--sh25);transition:transform .2s var(--e)}
§ .swt.on{background:var(--p)}
§ .swt.on::after{transform:translateX(18px)}
§ .swt.pd{opacity:.6;pointer-events:none}
§ .fe{flex-basis:100%;display:flex;align-items:flex-start;gap:6px;margin:0;padding:8px 10px;border-radius:8px;background:var(--dgb);color:var(--dg);font-size:13px;line-height:1.5}
§ .fe .ic{margin-top:3px}
§ .fe button{margin-left:auto;flex:none;color:var(--p-text);text-decoration:underline;text-underline-offset:3px}
§ .say .spn{color:var(--p-text)}
§ .rul{list-style:none;margin:18px 0 0;padding:14px 0 0;border-top:1px solid var(--line);font-size:13px;color:var(--ink2)}
§ .rul li{display:flex;gap:10px;line-height:2}
§ .rul b{flex:none;width:32px;font-weight:600;color:var(--ink)}
@media(max-width:700px){§ .gr{grid-template-columns:1fr}}
`),
  html: () => `<div class="adfb008" data-sh><div class="gr">
    <section class="cd"><h4>四种提示</h4><p class="cap">点击按钮，看顶部居中的提示</p><div class="btns"><button type="button" class="bt" data-m="ok">${I('checkc')}成功</button><button type="button" class="bt" data-m="wn">${I('alert')}警告</button><button type="button" class="bt" data-m="dg">${I('closec')}失败</button><button type="button" class="bt" data-m="ld">${I('refresh')}保存中→成功</button></div>
      <ul class="rul"><li><b>成功</b>一句话，2 秒后消失</li><li><b>失败</b>写原因与下一步，5 秒或手动关闭</li><li><b>加载</b>先转圈，再变成成功或失败</li></ul></section>
    <section class="cd"><h4>行内开关</h4><p class="cap">开关直接生效；失败回滚并在原位写原因</p>
      <div class="sr"><div class="t"><b>小程序接单</b><span>关闭后顾客仍可浏览，但不能下单</span></div><button type="button" class="swt on" role="switch" aria-checked="true" aria-label="小程序接单" data-k="shop"></button></div>
      <div class="sr"><div class="t"><b>新订单语音提醒</b><span>收银台有新订单时播报</span></div><button type="button" class="swt" role="switch" aria-checked="false" aria-label="新订单语音提醒" data-k="voice"></button></div>
      <div class="sr" data-r="ali"><div class="t"><b>支付宝收款</b><span>开启后顾客可使用支付宝支付</span></div><button type="button" class="swt" role="switch" aria-checked="false" aria-label="支付宝收款" data-k="ali"></button></div></section></div></div>`,
  js: (root) => {
    let aliOk = false
    const MSG = { ok: ['ok', '保存成功', 2200], wn: ['wn', '库存低于预警值，建议尽快补货', 3000], dg: ['dg', '保存失败：库存数量不能小于已锁定的 12 件，请调大后重试', 5000] }
    const ON = { shop: ['已开启小程序接单', '已暂停接单，顾客仍可浏览'], voice: ['已开启语音提醒', '已关闭语音提醒'] }
    const toggle = (sw) => {
      if (sw.classList.contains('pd')) return
      const to = !sw.classList.contains('on'), k = sw.dataset.k; sw.classList.add('pd'); sw.classList.toggle('on', to); sw.setAttribute('aria-checked', to)
      setTimeout(() => {
        sw.classList.remove('pd')
        if (k === 'ali' && to && !aliOk) {
          sw.classList.remove('on'); sw.setAttribute('aria-checked', 'false')
          const r = $(root, '[data-r=ali]'); if (!$(r, '.fe')) r.insertAdjacentHTML('beforeend', `<p class="fe" role="alert">${I('closec')}<span>开启失败：商户号审核未通过，请到「收款设置」补充营业执照后重试。</span><button type="button" data-retry>重试</button></p>`)
          say(root, '支付宝收款开启失败', 'dg', 3200); return
        }
        const fe = $(root, `[data-r=${k}] .fe`); if (fe) fe.remove()
        say(root, k === 'ali' ? (to ? '已开启支付宝收款' : '已关闭支付宝收款') : ON[k][to ? 0 : 1], 'ok')
      }, 650)
    }
    root.addEventListener('click', (e) => {
      const m = e.target.closest('[data-m]')
      if (m) {
        if (m.dataset.m !== 'ld') { const [t, x, ms] = MSG[m.dataset.m]; say(root, x, t, ms); return }
        const d = say(root, '正在保存…', 'in', 20000); $(d, '.ic').outerHTML = '<span class="spn"></span>'
        setTimeout(() => { d.className = 'say ok'; d.innerHTML = `${I('checkc')}<span>保存成功</span>`; setTimeout(() => d.remove(), 2000) }, 1100); return
      }
      const sw = e.target.closest('.swt'); if (sw) { toggle(sw); return }
      if (e.target.closest('[data-retry]')) { aliOk = true; toggle($(root, '.swt[data-k=ali]')) }
    })
  },
})

/* ---- AD-FB-009 表单弹窗 ---- */
const STAFF = [['周一帆', '客服部', '店员', '13900007741', 1], ['吴梓轩', '仓储部', '店员', '13700023308', 2], ['何婉清', '财务部', '财务', '13600044519', 3]]
def({
  id: 'AD-FB-009', name: '表单弹窗', style: '校验·防丢草稿', stage: '', wide: true,
  fit: '新增、快速编辑 4–6 个字段的对象（员工、分类、标签）：单列表单、必填标红星、失败在字段下写原因并聚焦第一个错误，保存中按钮加载防重复，成功后关闭并在列表里高亮新行；有未保存内容时关闭会先确认。',
  avoid: '字段超过 8 个或要多步时用独立页面；不要把查看和编辑混在一个弹窗里（那是居中详情面板）；别让“取消”静默丢掉已填内容。',
  kw: 'form modal 表单弹窗 新增 新建 编辑 校验 必填 保存 防重复提交 未保存提示 草稿 dialog form',
  css: C('adfb009', `${DLG_CSS}
§ .pgw{min-height:560px}
§ .tbl{width:100%;border-collapse:collapse;background:var(--card)}
§ .tbl th{height:44px;padding:0 16px;background:var(--bg);color:var(--ink2);font-weight:600;text-align:center}
§ .tbl td{height:52px;padding:0 16px;border-bottom:1px solid var(--line);text-align:center}
§ .tbl td.l{text-align:left;padding-left:24px}
§ .tbl tr.new td{animation:adfb009-hl 2s var(--e)}
§ .nmc{display:inline-flex;align-items:center;gap:10px}
§ .box2{margin:12px 16px 16px;border:1px solid var(--bd2);border-radius:12px;overflow:hidden;background:var(--card)}
§ .dlg{width:520px}
§ .db{padding-top:8px;color:var(--ink)}
§ .db .fld,§ .db .r2{margin-top:14px}
§ .db>:first-child{margin-top:0}
§ .r2 .fld{margin-top:0}
§ .fld label,§ .fld .lb{display:block;margin-bottom:6px;font-size:13px;color:var(--ink2)}
§ .fld label i,§ .fld .lb i{color:var(--dg);font-style:normal}
§ .er{margin:4px 0 0;font-size:12px;color:var(--dg)}
§ .ip.bad,§ .ddb.bad{border-color:var(--dg)}
§ .r2{display:grid;grid-template-columns:1fr 1fr;gap:14px}
§ .ddb{display:flex;align-items:center;justify-content:space-between;width:100%;height:36px;padding:0 12px;border:1px solid var(--bd);border-radius:8px;background:var(--card);text-align:left}
§ .ddb .pl{color:var(--ink3)}
§ .menu{width:100%}
§ .dd{position:relative}
§ .chs{display:flex;gap:8px}
§ .chs button{height:36px;padding:0 16px;border:1px solid var(--bd);border-radius:8px;background:var(--card);transition:border-color .15s var(--e),background-color .15s var(--e)}
§ .chs button.on{border-color:var(--p);background:var(--pt);color:var(--p-text);font-weight:600}
§ .cnt{margin-top:4px;text-align:right;font-size:12px;color:var(--ink3)}
§ .dfc{display:flex;align-items:center;gap:10px;flex:1;padding:6px 12px;border-radius:8px;background:var(--wnb);color:var(--wn);font-size:13px}
§ .dfc>span:not(.ic){flex:1}
@keyframes adfb009-hl{from{background:var(--pt)}}
@media(max-width:560px){§ .r2{grid-template-columns:1fr}}
`),
  html: () => `<div class="adfb009" data-sh><div class="pgw"><div class="tbr"><span class="sp"></span><button type="button" class="bt pri" data-open="d9">${I('plus')}新增员工</button></div>
    <div class="box2"><table class="tbl"><thead><tr><th>员工</th><th>部门</th><th>角色</th><th>手机号</th></tr></thead><tbody data-tb>${STAFF.map(([n, d, r, p, i]) => `<tr><td class="l"><span class="nmc">${critter(i, 32)}${n}</span></td><td>${d}</td><td><span class="tg2 in">${r}</span></td><td>${maskP(p)}</td></tr>`).join('')}</tbody></table></div>
    ${dlgOpen(true, 'd9')}<form class="dlg pn" role="dialog" aria-modal="true" aria-labelledby="adfb009-t" tabindex="-1" novalidate>
      <div class="dh"><h4 id="adfb009-t">新增员工</h4><button type="button" class="dx" data-x aria-label="关闭">${I('close')}</button></div>
      <div class="db">
        <div class="fld"><label for="f9n">姓名 <i>*</i></label><input class="ip" id="f9n" data-f="n" maxlength="10" placeholder="2–10 个字" autocomplete="off" data-autofocus><p class="er" data-er="n" hidden>请填写姓名（2–10 个字）</p></div>
        <div class="r2"><div class="fld"><label for="f9p">手机号 <i>*</i></label><input class="ip" id="f9p" data-f="p" inputmode="numeric" maxlength="11" placeholder="11 位手机号" autocomplete="off"><p class="er" data-er="p" hidden>手机号应为 11 位数字</p></div>
          <div class="fld"><span class="lb">所属部门 <i>*</i></span><div class="dd" data-ix="dd"><button type="button" class="ddb" data-tg aria-haspopup="listbox"><span class="pl" data-label>请选择部门</span>${I('down')}</button><div class="menu mn">${DEPTS.map((d) => `<button type="button" class="mi2" data-o data-v="${d}">${d}<span class="ic ck">${sv('check')}</span></button>`).join('')}</div></div><p class="er" data-er="d" hidden>请选择所属部门</p></div></div>
        <div class="fld"><span class="lb">角色</span><div class="chs" data-ix="radio" role="radiogroup">${['店员', '店长', '财务'].map((r, i) => `<button type="button" role="radio" data-o data-v="${r}" class="${i ? '' : 'on'}">${r}</button>`).join('')}</div></div>
        <div class="fld"><label for="f9r">备注</label><textarea class="ip" id="f9r" data-f="r" rows="3" maxlength="100" placeholder="选填，如负责的门店或班次"></textarea><div class="cnt"><span data-c>0</span>/100</div></div></div>
      <div class="df" data-df><button type="button" class="bt lg" data-x>取消</button><button type="submit" class="bt pri lg" data-save>保存</button></div></form></div></div></div>`,
  js: (root) => {
    overlays(root); const ov = $(root, '.ix-ov'), form = $(root, 'form'), df = $(root, '[data-df]'); let busy = false
    const dirty = () => !!($(root, '[data-f=n]').value.trim() || $(root, '[data-f=p]').value.trim() || $(root, '[data-f=r]').value.trim() || !$(root, '[data-label]').classList.contains('pl'))
    const showGuard = () => { if ($(root, '.dfc')) return; df.dataset.prev = df.innerHTML; df.innerHTML = `<div class="dfc">${I('alert')}<span>有未保存的内容，确定关闭？</span></div><button type="button" class="bt" data-keep>继续编辑</button><button type="button" class="bt dng" data-drop>放弃并关闭</button>`; $(root, '[data-keep]').focus() }
    const hideGuard = () => { if ($(root, '.dfc')) df.innerHTML = df.dataset.prev }
    const reset = () => { form.reset(); $$(root, '.bad').forEach((x) => x.classList.remove('bad')); $$(root, '.er').forEach((x) => (x.hidden = true)); const l = $(root, '[data-label]'); l.textContent = '请选择部门'; l.classList.add('pl'); $$(root, '.dd [data-o]').forEach((x) => x.classList.remove('on')); $$(root, '.chs [data-o]').forEach((x, i) => x.classList.toggle('on', i === 0)); $(root, '[data-c]').textContent = '0'; hideGuard() }
    const tryClose = () => { if (busy) return; if (dirty()) showGuard(); else closeOv(ov) }
    ov.__esc = () => { tryClose(); return false }
    root.addEventListener('click', (e) => {
      if (e.target.closest('[data-open="d9"]')) { reset(); return }
      if (e.target.closest('.ix-mask')) { e.stopPropagation(); tryClose(); return }
      if (e.target.closest('[data-x]')) { tryClose(); return }
      if (e.target.closest('[data-keep]')) { hideGuard(); return }
      if (e.target.closest('[data-drop]')) { closeOv(ov); setTimeout(reset, 200); return }
      const o = e.target.closest('.dd [data-o]'); if (o) { const l = $(root, '[data-label]'); l.classList.remove('pl'); $(root, '.ddb').classList.remove('bad'); $(root, '[data-er=d]').hidden = true }
    })
    root.addEventListener('input', (e) => { const t = e.target; if (t.matches('[data-f]')) { t.classList.remove('bad'); const er = $(root, `[data-er="${t.dataset.f}"]`); if (er) er.hidden = true; if (t.dataset.f === 'r') $(root, '[data-c]').textContent = t.value.length } })
    form.addEventListener('submit', (e) => {
      e.preventDefault(); if (busy) return
      const n = $(root, '[data-f=n]'), p = $(root, '[data-f=p]'), dl = $(root, '[data-label]'); const errs = []
      const bad = (el, key, f) => { el.classList.toggle('bad', f); $(root, `[data-er="${key}"]`).hidden = !f; if (f) errs.push(el) }
      bad(n, 'n', n.value.trim().length < 2); bad(p, 'p', !/^\d{11}$/.test(p.value.trim())); bad($(root, '.ddb'), 'd', dl.classList.contains('pl'))
      if (errs.length) { errs[0].focus(); return }
      busy = true; const sv9 = $(root, '[data-save]'); sv9.disabled = true; sv9.innerHTML = '<span class="spn"></span>保存中'
      setTimeout(() => {
        busy = false; const name = n.value.trim(), dept = dl.textContent, role = $(root, '.chs .on').dataset.v, ph = p.value.trim()
        $(root, '[data-tb]').insertAdjacentHTML('afterbegin', `<tr class="new"><td class="l"><span class="nmc">${critter(0, 32)}${name.replace(/</g, '&lt;')}</span></td><td>${dept}</td><td><span class="tg2 in">${role}</span></td><td>${maskP(ph)}</td></tr>`)
        sv9.disabled = false; sv9.textContent = '保存'; closeOv(ov); say(root, `已添加员工「${name}」`, 'ok'); setTimeout(reset, 250)
      }, 900)
    })
  },
})

/* ---- AD-FB-010 加载遮罩与进度 ---- */
def({
  id: 'AD-FB-010', name: '加载遮罩与进度', style: '遮罩+进度', stage: '', wide: false,
  fit: '耗时操作的反馈：区域刷新用半透明遮罩盖住原内容（不跳位）；导入、导出这类长任务用进度条 + 阶段清单 + 已用时间，可取消，完成给结果与下一步。',
  avoid: '不超过 1 秒的操作不必遮罩；别用全屏遮罩锁死整个后台（只盖受影响的区域）；进度条不知道进度时用阶段文字，不要假装精确百分比。',
  kw: 'loading mask 加载遮罩 进度条 progress 导入 导出 长任务 取消 阶段 spinner 区域刷新 全屏加载',
  css: C('adfb010', `${MENU_CSS}
§ .gr{display:grid;grid-template-columns:minmax(0,1.15fr) minmax(0,1fr);gap:12px}
§ .cd{position:relative;padding:18px 20px;border:1px solid var(--bd2);border-radius:12px;background:var(--card);box-shadow:var(--sh);min-height:300px;overflow:hidden}
§ .cd h4{margin:0 0 2px;font-size:14px;font-weight:600}
§ .cap{margin:0 0 14px;font-size:12px;color:var(--ink3)}
§ .file{display:flex;align-items:center;gap:12px;padding:12px 14px;border:1px dashed var(--bd);border-radius:8px}
§ .fi{display:inline-flex;align-items:center;justify-content:center;width:36px;height:36px;border-radius:8px;background:var(--okb);color:var(--ok)}
§ .file b{display:block;font-weight:600}
§ .file span{font-size:12px;color:var(--ink3)}
§ .ctl{margin-top:14px;display:flex;gap:8px;align-items:center}
§ .ovl{position:absolute;inset:0;z-index:5;display:flex;flex-direction:column;justify-content:center;gap:10px;padding:22px 24px;background:var(--card)}
§ .ovl h5{margin:0;display:flex;align-items:baseline;justify-content:space-between;font-size:16px;font-weight:600}
§ .ovl h5 span{font-size:14px;font-weight:400;color:var(--ink2);font-variant-numeric:tabular-nums}
§ .pb{height:8px;border-radius:4px;background:var(--n5);overflow:hidden}
§ .pb i{display:block;height:100%;border-radius:4px;background:var(--p);transition:width .12s linear}
§ .stg{list-style:none;margin:2px 0 0;padding:0;display:flex;flex-direction:column;gap:6px;color:var(--ink3)}
§ .stg li{display:flex;align-items:center;gap:8px}
§ .stg li.cur{color:var(--ink)}
§ .stg li.ok{color:var(--ink2)}
§ .stg .ic{color:var(--ink6)}§ .stg li.ok .ic{color:var(--ok)}
§ .stg .spn{width:14px;height:14px;margin:1px;color:var(--p-text)}
§ .tm{font-size:12px;color:var(--ink3)}
§ .res{display:flex;flex-direction:column;align-items:flex-start;gap:8px}
§ .res .ic.big{width:36px;height:36px;color:var(--ok)}
§ .res b{font-size:16px;font-weight:600}
§ .res p{margin:0;color:var(--ink2)}
§ .tw{position:relative;margin-top:2px;border:1px solid var(--bd2);border-radius:8px;overflow:hidden}
§ table{width:100%;border-collapse:collapse}
§ th{height:40px;padding:0 12px;background:var(--bg);color:var(--ink2);font-weight:600;text-align:center}
§ td{height:44px;padding:0 12px;border-top:1px solid var(--line);text-align:center;font-variant-numeric:tabular-nums}
§ td.l{text-align:left}
§ td.r{text-align:right}
§ .msk{position:absolute;inset:0;z-index:5;display:flex;align-items:center;justify-content:center;gap:8px;background:var(--glass0);color:var(--ink2)}
§ .msk .spn{color:var(--p-text)}
§ .upd{margin-left:auto;font-size:12px;color:var(--ink3)}
@media(max-width:700px){§ .gr{grid-template-columns:1fr}}
`),
  html: () => `<div class="adfb010" data-sh><div class="gr">
    <section class="cd" data-imp><h4>导入商品</h4><p class="cap">长任务：进度、阶段、可取消、有结果</p>
      <div class="file"><span class="fi">${I('file')}</span><div><b>商品导入模板.xlsx</b><span>1.2 MB · 共 1,286 行</span></div></div>
      <div class="ctl"><button type="button" class="bt pri lg" data-start>开始导入</button></div>
      <div class="ovl" data-ovl hidden></div></section>
    <section class="cd"><h4>今日门店数据</h4><p class="cap">区域刷新：遮罩盖住表格，原内容不跳位</p>
      <div class="tw"><table><thead><tr><th>门店</th><th>订单数</th><th>销售额</th></tr></thead><tbody data-tb>${[['旗舰店', 86, 18420], ['中心城店', 64, 12960], ['星湖街店', 41, 7385], ['火车站店', 28, 5120]].map(([n, o, a]) => `<tr><td class="l">${n}</td><td>${o}</td><td class="r">¥${a.toLocaleString('zh-CN')}</td></tr>`).join('')}</tbody></table><div class="msk" data-msk hidden><span class="spn"></span>正在刷新…</div></div>
      <div class="ctl"><button type="button" class="bt lg" data-refresh>${I('refresh')}刷新数据</button><span class="upd" data-upd>更新于 15:20</span></div></section></div></div>`,
  js: (root) => {
    const ovl = $(root, '[data-ovl]'); let t = null, pct = 0, t0 = 0
    const STG = ['校验文件格式', '写入商品数据', '更新搜索索引']
    const stage = () => (pct < 28 ? 0 : pct < 86 ? 1 : 2)
    const draw = () => {
      const s = stage(), el = Math.round((Date.now() - t0) / 1000)
      ovl.innerHTML = `<h5>正在导入商品<span>${Math.round(pct)}%</span></h5><div class="pb" role="progressbar" aria-valuenow="${Math.round(pct)}" aria-valuemin="0" aria-valuemax="100"><i style="width:${pct}%"></i></div><ul class="stg">${STG.map((x, i) => `<li class="${i < s ? 'ok' : i === s ? 'cur' : ''}">${i < s ? I('checkc') : i === s ? '<span class="spn"></span>' : I('adshTarget')}${x}</li>`).join('')}</ul><div class="tm">已用 ${el} 秒，取消不会写入任何数据</div><div class="ctl" style="margin-top:4px"><button type="button" class="bt" data-cancel>取消导入</button></div>`
    }
    const done = () => { ovl.innerHTML = `<div class="res"><span class="ic big">${sv('checkc')}</span><b>导入完成</b><p>共 1,286 行，成功 1,281 行，失败 5 行。失败行的原因已写入明细，修正后可重新导入。</p><div class="ctl" style="margin-top:4px"><button type="button" class="bt" data-toast="已下载：失败明细.xlsx">下载失败明细</button><button type="button" class="bt pri" data-fin>完成</button></div></div>` }
    root.addEventListener('click', (e) => {
      if (e.target.closest('[data-start]')) { pct = 0; t0 = Date.now(); ovl.hidden = false; draw(); t = setInterval(() => { if (!root.isConnected) { clearInterval(t); return } pct = Math.min(100, pct + 2.5); if (pct >= 100) { clearInterval(t); done() } else draw() }, 110); return }
      if (e.target.closest('[data-cancel]')) { clearInterval(t); ovl.hidden = true; say(root, '已取消导入，未写入任何数据', 'wn'); return }
      if (e.target.closest('[data-fin]')) { ovl.hidden = true; say(root, '商品列表已刷新', 'ok'); return }
      const r = e.target.closest('[data-refresh]'); if (r) {
        r.disabled = true; $(root, '[data-msk]').hidden = false
        setTimeout(() => {
          $(root, '[data-msk]').hidden = true; r.disabled = false; $(root, '[data-upd]').textContent = '更新于 15:32'
          $$(root, '[data-tb] tr').forEach((tr, i) => { const c = tr.cells; c[1].textContent = +c[1].textContent + 1 + i; c[2].textContent = '¥' + (+c[2].textContent.replace(/[^\d]/g, '') + 120 * (i + 1)).toLocaleString('zh-CN') })
          say(root, '数据已更新', 'ok')
        }, 1300)
      }
    })
  },
})

/* ======================================================================
   三、状态与结果页 AD-STATE
   ====================================================================== */
const ART_STROKE = '#C3C8D0'
const ART = {
  empty: `<ellipse cx="80" cy="106" rx="50" ry="7" fill="var(--pt)"/><rect x="52" y="20" width="56" height="54" rx="6" fill="var(--card)" stroke="${ART_STROKE}" stroke-width="2"/><path d="M62 36h36M62 46h36M62 56h22" stroke="var(--pm)" stroke-width="3" stroke-linecap="round"/><path d="M30 70h28l6 10h32l6-10h28v24a8 8 0 0 1-8 8H38a8 8 0 0 1-8-8z" fill="var(--pt)" stroke="${ART_STROKE}" stroke-width="2" stroke-linejoin="round"/>`,
  search: `<ellipse cx="80" cy="106" rx="50" ry="7" fill="var(--pt)"/><circle cx="72" cy="52" r="28" fill="var(--card)" stroke="${ART_STROKE}" stroke-width="2"/><path d="m92 72 22 22" stroke="var(--p)" stroke-width="6" stroke-linecap="round"/><path d="m62 42 20 20M82 42 62 62" stroke="var(--pm)" stroke-width="4" stroke-linecap="round"/>`,
  flag: `<ellipse cx="80" cy="106" rx="54" ry="7" fill="var(--pt)"/><rect x="36" y="82" width="28" height="20" rx="3" fill="var(--pt)" stroke="${ART_STROKE}" stroke-width="2"/><rect x="64" y="64" width="28" height="38" rx="3" fill="var(--card)" stroke="${ART_STROKE}" stroke-width="2"/><rect x="92" y="46" width="28" height="56" rx="3" fill="var(--pt)" stroke="${ART_STROKE}" stroke-width="2"/><path d="M106 46V20" stroke="${ART_STROKE}" stroke-width="2" stroke-linecap="round"/><path d="M106 20h20l-5 7 5 7h-20z" fill="var(--p)"/>`,
  cloud: `<ellipse cx="80" cy="106" rx="50" ry="7" fill="var(--pt)"/><path d="M46 86a18 18 0 0 1 2-36 26 26 0 0 1 50-4 20 20 0 0 1 4 40z" fill="var(--card)" stroke="${ART_STROKE}" stroke-width="2" stroke-linejoin="round"/><circle cx="106" cy="84" r="14" fill="var(--dgb)" stroke="#D9A9A3" stroke-width="2"/><path d="m100 78 12 12M112 78l-12 12" stroke="var(--dg)" stroke-width="3" stroke-linecap="round"/>`,
}
const art = (k) => `<svg class="art" viewBox="0 0 160 120" width="160" height="120" aria-hidden="true">${ART[k]}</svg>`
const SHIM = (p) => `
§ .sk.sh{background:linear-gradient(90deg,var(--n4) 25%,var(--n2) 40%,var(--n4) 60%);background-size:300% 100%;animation:${p}-sh 1.4s ease infinite}
@keyframes ${p}-sh{from{background-position:100% 50%}to{background-position:0 50%}}
`
const TABS_CSS = `
§ .tbs{position:relative;display:flex;gap:28px;padding:0 24px;overflow-x:auto;scrollbar-width:none;box-shadow:inset 0 -1px 0 var(--line)}
§ .tbs::-webkit-scrollbar{display:none}
§ .tbs>button{display:inline-flex;align-items:center;flex:none;gap:6px;height:48px;color:var(--ink2);white-space:nowrap}
§ .tbs>button span{display:inline-flex;flex-direction:column}
§ .tbs>button span::after{content:attr(data-w);height:0;overflow:hidden;visibility:hidden;font-weight:600}
§ .tbs>button.on{color:var(--p-text);font-weight:600}
§ .tbs .ink{position:absolute;bottom:0;height:2px;background:var(--p);transition:left .25s var(--e),width .25s var(--e)}
`
const tabsHTML = (list) => `<div class="tbs" data-ix="tabs" role="tablist">${list.map(([k, t], i) => `<button type="button" role="tab" data-t="${k}" class="${i ? '' : 'on'}"><span data-w="${t}">${t}</span></button>`).join('')}<i class="ink"></i></div>`

/* ---- AD-STATE-001 空状态 ---- */
def({
  id: 'AD-STATE-001', name: '空状态', style: '四种场景', stage: '', wide: false,
  fit: '列表或区域没有内容时：暂无数据（引导新建）、搜索无结果（可一键清除筛选）、首次使用（分步引导并显示进度）、加载失败（写原因，重试会真的重新请求）；每种都带一个明确的下一步。',
  avoid: '不要只放一张图加“暂无数据”；有筛选条件时不要说“还没有任何数据”（要说没找到并给清除入口）；一个空状态最多一个主按钮。',
  kw: 'empty state 空状态 暂无数据 无结果 搜索无结果 首次使用 引导 加载失败 重试 缺省页 空白页',
  css: C('adstate001', `${MENU_CSS}${TABS_CSS}
§ .cd{border:1px solid var(--bd2);border-radius:12px;background:var(--card);box-shadow:var(--sh);overflow:hidden}
§ .pa{display:flex;flex-direction:column;align-items:center;min-height:330px;padding:28px 24px 30px;text-align:center}
§ .pa[hidden]{display:none}
§ .pa h4{margin:8px 0 0;font-size:16px;font-weight:600}
§ .pa p{margin:6px 0 0;max-width:380px;color:var(--ink2);line-height:1.6}
§ .act{display:flex;gap:10px;flex-wrap:wrap;justify-content:center;margin-top:18px}
§ .chips{display:flex;gap:8px;flex-wrap:wrap;justify-content:center;margin-top:14px}
§ .chip{display:inline-flex;align-items:center;gap:2px;height:28px;padding:0 4px 0 10px;border-radius:14px;background:var(--pt);color:var(--p-text);font-size:13px}
§ .chip button{display:inline-flex;width:20px;height:20px;align-items:center;justify-content:center;border-radius:50%}
§ .chip button:hover{background:var(--pm)}
§ .chip svg{width:12px;height:12px}
§ .gs{width:100%;max-width:420px;margin-top:14px;text-align:left}
§ .gp{display:flex;align-items:center;gap:10px;margin-bottom:10px;font-size:13px;color:var(--ink3)}
§ .gp .pb{flex:1;height:6px;border-radius:3px;background:var(--n5);overflow:hidden}
§ .gp .pb i{display:block;height:100%;border-radius:3px;background:var(--p);transition:width .3s var(--e)}
§ .gi{display:flex;align-items:center;gap:12px;min-height:48px;padding:0 14px;border:1px solid var(--bd2);border-radius:8px}
§ .gi+.gi{margin-top:8px}
§ .gi .no{display:flex;align-items:center;justify-content:center;width:24px;height:24px;border-radius:50%;border:2px solid var(--n7);color:var(--ink3);font-size:12px;flex:none}
§ .gi.done .no{border-color:var(--p);background:var(--p);color:#fff}
§ .gi .no svg{width:12px;height:12px;stroke-width:3}
§ .gi span.t{flex:1;color:var(--ink)}
§ .gi.done span.t{color:var(--ink3);text-decoration:line-through}
§ .gi .bt{height:32px}
§ .ok2{display:flex;flex-direction:column;align-items:center;gap:6px}
§ .ok2 .ic{width:40px;height:40px;color:var(--ok)}
`),
  html: () => `<div class="adstate001" data-sh><div class="cd">${tabsHTML([['a', '暂无数据'], ['b', '搜索无结果'], ['c', '首次使用'], ['d', '加载失败']])}
    <div class="pa" data-p="a">${art('empty')}<h4>还没有优惠券</h4><p>创建第一张券，发给会员或放进活动页，顾客领取后会显示在这里。</p><div class="act"><button type="button" class="bt pri lg" data-toast="打开：新建优惠券">${I('plus')}新建优惠券</button><button type="button" class="bt lg" data-toast="打开：导入优惠券">导入</button></div></div>
    <div class="pa" data-p="b" hidden>${art('search')}<h4>没有找到「保温杯 绿色」</h4><p data-bt>试试更短的关键词，或去掉一些筛选条件。</p><div class="chips" data-chips><span class="chip">状态：进行中<button type="button" data-rm aria-label="移除">${sv('close')}</button></span><span class="chip">类型：满减<button type="button" data-rm aria-label="移除">${sv('close')}</button></span></div><div class="act"><button type="button" class="bt pri lg" data-clear>清除全部筛选</button></div></div>
    <div class="pa" data-p="c" hidden>${art('flag')}<h4 data-gt>开店前还差 2 步</h4><div class="gs"><div class="gp"><span data-gn>已完成 1 / 3</span><div class="pb"><i style="width:33%"></i></div></div>
      ${['添加第一个商品', '设置营业时间', '开通微信支付'].map((t, i) => `<div class="gi${i === 0 ? ' done' : ''}"><span class="no">${i === 0 ? sv('check') : i + 1}</span><span class="t">${t}</span>${i === 0 ? '<span class="tg2 ok">已完成</span>' : '<button type="button" class="bt" data-go>去设置</button>'}</div>`).join('')}</div>
      <div class="act" data-fin hidden><button type="button" class="bt pri lg" data-toast="已开业，小程序开始接单">一键开业</button></div></div>
    <div class="pa" data-p="d" hidden>${art('cloud')}<h4 data-ft>订单列表加载失败</h4><p data-fd>网络连接中断，请检查网络后重试（错误码 NET-408）。</p><div class="act" data-fa><button type="button" class="bt pri lg" data-retry>${I('refresh')}重试</button></div></div></div></div>`,
  js: (root) => {
    root.addEventListener('click', (e) => {
      const rm = e.target.closest('[data-rm]'); if (rm) { rm.closest('.chip').remove(); if (!$$(root, '[data-chips] .chip').length) $(root, '[data-bt]').textContent = '已清除全部筛选，请重新搜索或返回完整列表。'; return }
      if (e.target.closest('[data-clear]')) { $(root, '[data-chips]').innerHTML = ''; $(root, '[data-bt]').textContent = '已清除全部筛选，正在显示全部 12 张优惠券。'; say(root, '已清除筛选，共 12 张优惠券', 'ok'); return }
      const g = e.target.closest('[data-go]'); if (g) {
        const it = g.closest('.gi'); it.classList.add('done'); $(it, '.no').innerHTML = sv('check'); g.replaceWith(Object.assign(document.createElement('span'), { className: 'tg2 ok', textContent: '已完成' }))
        const n = $$(root, '.gi.done').length; $(root, '[data-gn]').textContent = `已完成 ${n} / 3`; $(root, '.gp .pb i').style.width = (n / 3 * 100) + '%'
        $(root, '[data-gt]').textContent = n === 3 ? '全部就绪，可以开店了' : `开店前还差 ${3 - n} 步`; $(root, '[data-fin]').hidden = n < 3; say(root, `已完成：${$(it, '.t').textContent}`, 'ok'); return
      }
      const r = e.target.closest('[data-retry]'); if (r) {
        r.disabled = true; r.innerHTML = '<span class="spn"></span>重试中'; const n = (r.__n = (r.__n || 0) + 1)
        setTimeout(() => {
          if (n < 2) { r.disabled = false; r.innerHTML = `${I('refresh')}再试一次`; $(root, '[data-fd]').textContent = '仍然无法连接服务器，已重试 1 次。请确认网络正常，或稍后再试。'; say(root, '重试失败：仍无法连接', 'dg') }
          else { $(root, '[data-ft]').textContent = '已恢复'; $(root, '[data-fd]').textContent = '订单列表已重新加载，共 24 条订单。'; $(root, '[data-fa]').innerHTML = '<button type="button" class="bt lg" data-reload>重新演示</button>'; $(root, '.pa[data-p=d] .art').outerHTML = `<span class="ic" style="width:64px;height:64px;color:var(--ok);margin-bottom:4px">${sv('checkc')}</span>`; say(root, '已恢复，列表已刷新', 'ok') }
        }, 900); return
      }
    })
  },
})

/* ---- AD-STATE-002 异常结果页 403/404/500 ---- */
const ERRS = {
  403: { ic: 'lock', t: '没有访问权限', d: '你当前的角色是「店员」，不能查看「财务报表」。', why: ['该页面仅限「店长」和「财务」角色', '你的权限最近被管理员调整过'], a: [['申请权限', 'pri', 'ask'], ['返回首页', '', 'home']] },
  404: { ic: 'adshSearchOff', t: '页面不存在', d: '你访问的页面可能已被移动、改名或删除。', why: ['链接来自旧版本，菜单已调整', '地址输入有误，或页面已下线'], a: [['返回上一页', 'pri', 'back'], ['回到首页', '', 'home']] },
  500: { ic: 'adshServer', t: '服务暂时不可用', d: '服务器处理请求时出了问题，不是你的操作有误。我们已记录，通常几分钟内恢复。', why: ['请求编号 REQ-20261104-7F3A，联系技术支持时请提供'], a: [['重试', 'pri', 'retry'], ['联系技术支持', '', 'help']] },
}
def({
  id: 'AD-STATE-002', name: '异常结果页', style: '状态码+下一步', stage: '', wide: false,
  fit: '整页打不开时：大号状态码 + 图标、一句话讲清发生了什么、列出可能原因、给下一步（403 申请权限、404 返回、500 重试并带请求编号）；动作真的会有反馈。',
  avoid: '不要只写“出错了”；500 不要把堆栈、服务器地址展示给用户；区块内的小错误用空状态的“加载失败”，别整页替换；别让用户只能关浏览器。',
  kw: 'error page 403 404 500 异常页 无权限 页面不存在 服务器错误 结果页 result 请求编号 重试 申请权限',
  css: C('adstate002', `${MENU_CSS}${TABS_CSS}
§ .cd{border:1px solid var(--bd2);border-radius:12px;background:var(--card);box-shadow:var(--sh);overflow:hidden}
§ .rp{display:flex;flex-direction:column;align-items:center;min-height:430px;padding:30px 24px 32px;text-align:center}
§ .rp[hidden]{display:none}
§ .code{position:relative;display:flex;align-items:center;justify-content:center;height:112px;margin-bottom:6px}
§ .code b{font-size:100px;line-height:1;font-weight:700;color:var(--pm);font-variant-numeric:tabular-nums}
§ .code .tile{position:absolute;right:-30px;bottom:-4px;display:flex;align-items:center;justify-content:center;width:52px;height:52px;border-radius:50%;background:var(--card);color:var(--p-text);box-shadow:0 0 0 1px var(--bd2),var(--sh)}
§ .code .tile .ic{width:26px;height:26px}
§ .rp h4{margin:10px 0 0;font-size:20px;line-height:1.4;font-weight:600}
§ .rp>p{margin:6px 0 0;max-width:420px;line-height:1.65;color:var(--ink2)}
§ .why{margin:16px 0 0;padding:12px 16px 12px 16px;max-width:420px;border-radius:8px;background:var(--bg);text-align:left;list-style:none;color:var(--ink2);font-size:13px}
§ .why li{position:relative;padding-left:14px;line-height:1.7}
§ .why li::before{content:"";position:absolute;left:0;top:10px;width:5px;height:5px;border-radius:50%;background:var(--n11)}
§ .why .cp{margin-left:6px;color:var(--p-text)}
§ .why .cp:hover{text-decoration:underline}
§ .act{display:flex;gap:10px;flex-wrap:wrap;justify-content:center;margin-top:22px}
§ .note{margin-top:12px;min-height:22px;font-size:13px;color:var(--ink3)}
§ .note.ok{color:var(--ok)}
`),
  html: () => `<div class="adstate002" data-sh><div class="cd">${tabsHTML([['403', '403 无权限'], ['404', '404 不存在'], ['500', '500 服务异常']])}
    ${Object.entries(ERRS).map(([c, o], i) => `<div class="rp" data-p="${c}"${i ? ' hidden' : ''}><div class="code"><b>${c}</b><span class="tile">${I(o.ic)}</span></div><h4>${o.t}</h4><p data-d>${o.d}</p><ul class="why"><li>${o.why[0]}${c === '500' ? '<button type="button" class="cp" data-cp>复制</button>' : ''}</li>${o.why[1] ? `<li>${o.why[1]}</li>` : ''}</ul><div class="act">${o.a.map(([t, k, a]) => `<button type="button" class="bt ${k} lg" data-a="${a}">${t}</button>`).join('')}</div><div class="note" data-note></div></div>`).join('')}</div></div>`,
  js: (root) => {
    let tries = 0
    root.addEventListener('click', (e) => {
      if (e.target.closest('[data-cp]')) { try { navigator.clipboard.writeText('REQ-20261104-7F3A') } catch (x) {} say(root, '已复制请求编号', 'ok'); return }
      const a = e.target.closest('[data-a]'); if (!a) return
      const pn = a.closest('.rp'), note = $(pn, '[data-note]'), k = a.dataset.a
      if (k === 'ask') { a.disabled = true; a.innerHTML = '<span class="spn"></span>提交中'; setTimeout(() => { a.innerHTML = '已提交申请'; note.className = 'note ok'; note.textContent = '审批人：林小满（店长），通常 1 个工作日内处理，结果会发到消息中心。'; say(root, '权限申请已提交', 'ok') }, 800); return }
      if (k === 'retry') {
        a.disabled = true; a.innerHTML = '<span class="spn"></span>重试中'; tries++
        setTimeout(() => {
          if (tries < 2) { a.disabled = false; a.textContent = '再试一次'; note.className = 'note'; note.textContent = '服务仍未恢复，已自动重试 1 次，请稍后再试。'; say(root, '重试失败：服务仍未恢复', 'dg') }
          else { a.textContent = '已恢复'; note.className = 'note ok'; note.textContent = '服务已恢复，正在带你回到刚才的页面（示例）。'; say(root, '服务已恢复', 'ok') }
        }, 900); return
      }
      if (k === 'help') { note.className = 'note'; note.textContent = '技术支持：400-000-0000（工作日 9:00–18:00），请提供请求编号。'; return }
      say(root, k === 'back' ? '返回上一页（示例）' : '回到首页（示例）', 'in')
    })
  },
})

/* ---- AD-STATE-003 骨架屏 ---- */
def({
  id: 'AD-STATE-003', name: '骨架屏', style: '列表·看板·微光', stage: '', wide: false,
  fit: '页面或区域首次加载超过 300 毫秒时：用与真实内容同样布局的灰块占位，加载完成后原位替换，页面不跳位；列表页与数据看板各有一套骨架，微光动画只给“正在加载”传达进度感。',
  avoid: '不到 300 毫秒的加载别闪骨架；骨架布局要和真实内容一致，不然替换时会跳；整页只放一套微光，减少动态偏好的用户要关闭动画；不要同时又放转圈。',
  kw: 'skeleton 骨架屏 加载中 占位 shimmer 微光 首次加载 列表骨架 看板骨架 loading placeholder',
  css: C('adstate003', `${MENU_CSS}${SHIM('adstate003')}
§ .cd{border:1px solid var(--bd2);border-radius:12px;background:var(--card);box-shadow:var(--sh);overflow:hidden}
§ .ctl{display:flex;align-items:center;gap:10px;flex-wrap:wrap;padding:12px 16px;border-bottom:1px solid var(--line)}
§ .ctl .sp{flex:1}
§ .sgm{display:inline-flex;padding:2px;border-radius:8px;background:var(--mub)}
§ .sgm button{height:28px;padding:0 12px;border-radius:4px;font-size:13px;color:var(--ink2);transition:background-color .15s var(--e)}
§ .sgm button.on{background:var(--lift);color:var(--ink);box-shadow:0 1px 3px var(--sh12)}
§ .body{position:relative;min-height:392px;padding:16px}
§ .tb3{display:flex;align-items:center;gap:10px;margin-bottom:12px}
§ .tb3 .sk{height:36px;border-radius:8px}
§ .rw{display:flex;align-items:center;gap:14px;height:56px;border-bottom:1px solid var(--line)}
§ .rw:last-child{border-bottom:0}
§ .rw .av{width:32px;height:32px;border-radius:50%;flex:none}
§ .rw .ls{flex:1;display:flex;flex-direction:column;gap:7px}
§ .rw .ls .sk:last-child{height:8px}
§ .hd{display:flex;gap:14px;height:40px;align-items:center;margin-bottom:4px;padding:0 4px}
§ .g3{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:12px}
§ .st3{padding:14px 16px;border:1px solid var(--bd2);border-radius:12px;display:flex;flex-direction:column;gap:10px}
§ .st3 b{font-size:22px;font-weight:700;font-variant-numeric:tabular-nums}
§ .st3 span{font-size:13px;color:var(--ink3)}
§ .ch{margin-top:12px;height:150px;border:1px solid var(--bd2);border-radius:12px;padding:16px;display:flex;align-items:flex-end;gap:12px}
§ .ch i{flex:1;border-radius:4px 4px 0 0;background:var(--pm)}
§ .ch .sk{height:auto}
§ .tg2.mini{height:20px}
§ .rl{display:flex;align-items:center;gap:14px;height:56px;border-bottom:1px solid var(--line)}
§ .rl:last-child{border-bottom:0}
§ .rl .nm{flex:1;min-width:0}
§ .rl .nm small{display:block;font-size:12px;color:var(--ink3)}
§ .rl .am{width:88px;text-align:right;font-variant-numeric:tabular-nums}
@media(prefers-reduced-motion:reduce){§ .sk.sh{animation:none}}
`),
  html: () => `<div class="adstate003" data-sh><div class="cd"><div class="ctl"><div class="sgm" role="group" aria-label="骨架类型"><button type="button" class="on" data-lay="list">列表页</button><button type="button" data-lay="card">数据看板</button></div><span class="sp"></span><button type="button" class="bt" data-reload>${I('refresh')}重新加载</button></div><div class="body" data-body></div></div></div>`,
  js: (root) => {
    let lay = 'list', loading = true, timer = null
    const skList = () => `<div class="tb3"><i class="sk sh" style="width:200px"></i><i class="sk sh" style="width:96px"></i><span style="flex:1"></span><i class="sk sh" style="width:88px"></i></div>${Array.from({ length: 6 }, (_, i) => `<div class="rw"><i class="sk sh av"></i><div class="ls"><i class="sk sh" style="width:${[42, 36, 48, 32, 40, 38][i]}%"></i><i class="sk sh" style="width:${[24, 20, 28, 18, 22, 26][i]}%"></i></div><i class="sk sh" style="width:56px;height:22px"></i><i class="sk sh" style="width:72px"></i></div>`).join('')}`
    const skCard = () => `<div class="g3">${[0, 1, 2].map(() => '<div class="st3"><i class="sk sh" style="width:44%;height:8px"></i><i class="sk sh" style="width:62%;height:22px"></i><i class="sk sh" style="width:38%;height:8px"></i></div>').join('')}</div><div class="ch">${[60, 90, 50, 110, 80, 100, 70].map((h) => `<i class="sk sh" style="height:${h}px"></i>`).join('')}</div>`
    const rList = () => `<div class="tb3"><div class="ip" style="width:200px;display:flex;align-items:center;gap:8px;color:var(--ink3)">${I('search')}搜索订单号</div><div class="ip" style="width:96px;display:flex;align-items:center;color:var(--ink2)">待发货</div><span style="flex:1"></span><span class="bt pri lg" style="cursor:default">新建订单</span></div>${ORDER_ROWS.slice(0, 6).map((o, i) => `<div class="rl">${critter(i, 32)}<div class="nm">${o.who}<small>${o.no} · ${o.sku}</small></div><span class="tg2 ${ST_TONE[o.tone]}">${o.st}</span><span class="am">¥${o.amt.toLocaleString('zh-CN')}.00</span></div>`).join('')}`
    const rCard = () => `<div class="g3">${[['今日订单', '218', '较昨日 +12'], ['销售额', '¥38,640', '较昨日 +8.5%'], ['待处理', '12', '含 3 条超时']].map(([a, b, c]) => `<div class="st3"><span>${a}</span><b>${b}</b><span>${c}</span></div>`).join('')}</div><div class="ch">${[60, 90, 50, 110, 80, 100, 70].map((h) => `<i style="height:${h}px"></i>`).join('')}</div>`
    const draw = () => { $(root, '[data-body]').innerHTML = loading ? (lay === 'list' ? skList() : skCard()) : (lay === 'list' ? rList() : rCard()); $(root, '[data-body]').setAttribute('aria-busy', loading) }
    const load = () => { clearTimeout(timer); loading = true; draw(); timer = setTimeout(() => { loading = false; draw(); say(root, '已加载完成', 'ok') }, 1800) }
    root.addEventListener('click', (e) => {
      const l = e.target.closest('[data-lay]'); if (l) { lay = l.dataset.lay; $$(root, '[data-lay]').forEach((x) => x.classList.toggle('on', x === l)); load(); return }
      if (e.target.closest('[data-reload]')) load()
    })
    draw(); timer = setTimeout(() => { if (root.isConnected && loading && !root.__touched) { /* 首屏停在骨架，便于查看 */ } }, 0)
  },
})

/* ---- AD-STATE-004 操作结果页 ---- */
const FAILS = [['第 18 行', '手机号格式不正确（应为 11 位数字）'], ['第 87 行', '会员等级「铂金」不存在，可选：普通、银卡、金卡']]
def({
  id: 'AD-STATE-004', name: '操作结果页', style: '成功·部分失败', stage: '', wide: false,
  fit: '提交审核、发货、批量导入这类有明确终点的操作：成功页写清做了什么、关键信息、可继续的下一步（继续新建、返回列表、查看详情），可倒计时自动返回；部分失败页列出每条失败的原因并支持只重试失败项。',
  avoid: '简单操作用轻提示即可；别让用户无路可走（至少给“返回列表”）；自动返回要能取消；失败原因别写“系统错误”，要写到行和字段。',
  kw: 'result page 操作结果 操作成功 成功页 部分失败 批量结果 继续新建 返回列表 重试失败项 倒计时返回 success',
  css: C('adstate004', `${MENU_CSS}${TABS_CSS}
§ .cd{border:1px solid var(--bd2);border-radius:12px;background:var(--card);box-shadow:var(--sh);overflow:hidden}
§ .rp{display:flex;flex-direction:column;align-items:center;min-height:440px;padding:30px 24px 26px;text-align:center}
§ .rp[hidden]{display:none}
§ .big{position:relative;display:flex;align-items:center;justify-content:center;width:72px;height:72px;border-radius:50%;background:var(--okb);color:var(--ok)}
§ .big .ic{width:36px;height:36px}
§ .big.wn{background:var(--wnb);color:var(--wn)}
§ .big:not(.wn) svg path{stroke-dasharray:30;stroke-dashoffset:30;animation:adstate004-draw .5s .1s var(--e) forwards}
@keyframes adstate004-draw{to{stroke-dashoffset:0}}
§ .rp h4{margin:14px 0 0;font-size:20px;line-height:1.4;font-weight:600}
§ .rp>p{margin:6px 0 0;max-width:440px;line-height:1.65;color:var(--ink2)}
§ .sum{width:100%;max-width:440px;margin-top:18px;padding:14px 18px;border-radius:8px;background:var(--bg);text-align:left}
§ .sum div{display:flex;gap:12px;line-height:2}
§ .sum span{width:72px;color:var(--ink3);flex:none}
§ .sum b{font-weight:400;min-width:0}
§ .sum .cp{margin-left:8px;color:var(--p-text)}
§ .act{display:flex;gap:10px;flex-wrap:wrap;justify-content:center;margin-top:20px}
§ .cdw{margin-top:14px;min-height:22px;font-size:13px;color:var(--ink3)}
§ .cdw button{margin-left:6px;color:var(--p-text);text-decoration:underline;text-underline-offset:3px}
§ .stat{display:flex;gap:10px;width:100%;max-width:440px;margin-top:16px}
§ .stat div{flex:1;padding:10px 12px;border-radius:8px;background:var(--bg)}
§ .stat span{display:block;font-size:12px;color:var(--ink3)}
§ .stat b{font-size:18px;font-weight:600;font-variant-numeric:tabular-nums}
§ .stat .f b{color:var(--dg)}
§ .fl{width:100%;max-width:440px;margin:12px 0 0;padding:0;list-style:none;border:1px solid var(--bd2);border-radius:8px;text-align:left}
§ .fl li{display:flex;align-items:flex-start;gap:10px;padding:10px 14px;border-bottom:1px solid var(--line);line-height:1.55}
§ .fl li:last-child{border-bottom:0}
§ .fl .ln{flex:none;width:56px;color:var(--ink3)}
§ .fl .rs{flex:1;min-width:0;color:var(--ink2)}
§ .fl li.fixed .rs{color:var(--ok)}
§ .fl li .ic{margin-top:3px;color:var(--ok)}
`),
  html: () => `<div class="adstate004" data-sh><div class="cd">${tabsHTML([['ok', '全部成功'], ['part', '部分失败']])}
    <div class="rp" data-p="ok"><span class="big">${I('check')}</span><h4>订单已发货</h4><p>运单号已同步给顾客，顾客将收到发货通知，可在小程序里查看物流。</p>
      <div class="sum"><div><span>订单号</span><b>SO2026110528</b></div><div><span>收货人</span><b>林小满 · 138****2086</b></div><div><span>运单号</span><b>SF1403387920265<button type="button" class="cp" data-cp>复制</button></b></div><div><span>发货时间</span><b>2026-11-04 15:20</b></div></div>
      <div class="act"><button type="button" class="bt pri lg" data-next>继续发货下一单</button><button type="button" class="bt lg" data-back>返回订单列表</button><button type="button" class="bt txt lg" data-toast="打开：订单详情">查看订单详情</button></div>
      <div class="cdw" data-cdw></div></div>
    <div class="rp" data-p="part" hidden><span class="big wn">${I('alert')}</span><h4 data-pt>批量导入完成，2 条失败</h4><p data-pd>共 128 条，成功 126 条。失败的 2 条未写入，修正后可只重试这些行。</p>
      <div class="stat"><div><span>总数</span><b>128</b></div><div><span>成功</span><b data-so>126</b></div><div class="f"><span>失败</span><b data-sf>2</b></div></div>
      <ul class="fl" data-fl>${FAILS.map(([l, r]) => `<li><span class="ln">${l}</span><span class="rs">${r}</span></li>`).join('')}</ul>
      <div class="act"><button type="button" class="bt pri lg" data-retry>重试失败项</button><button type="button" class="bt lg" data-toast="已下载：失败明细.xlsx">${I('download')}下载失败明细</button><button type="button" class="bt txt lg" data-back>返回列表</button></div></div></div></div>`,
  js: (root) => {
    let n = 8, tm = null
    const cd = $(root, '[data-cdw]')
    const tick = () => { if (!root.isConnected) { clearInterval(tm); return } n--; if (n <= 0) { clearInterval(tm); cd.textContent = '已返回订单列表（示例）'; const b = document.createElement('button'); b.type = 'button'; b.dataset.replay = ''; b.textContent = '重新演示'; cd.appendChild(b) } else paint() }
    const paint = () => { cd.innerHTML = `${n} 秒后自动返回订单列表<button type="button" data-stop>取消</button>` }
    const start = () => { clearInterval(tm); n = 8; paint(); tm = setInterval(tick, 1000) }
    root.addEventListener('click', (e) => {
      if (e.target.closest('.tbs [data-t]')) { if (e.target.closest('[data-t="ok"]')) setTimeout(start, 0); else clearInterval(tm); return }
      if (e.target.closest('[data-stop]')) { clearInterval(tm); cd.textContent = '已取消自动返回'; return }
      if (e.target.closest('[data-replay]')) { start(); return }
      if (e.target.closest('[data-cp]')) { try { navigator.clipboard.writeText('SF1403387920265') } catch (x) {} say(root, '已复制运单号', 'ok'); return }
      if (e.target.closest('[data-next]')) { clearInterval(tm); cd.textContent = ''; say(root, '已进入：下一张待发货订单 SO2026110521', 'in'); return }
      if (e.target.closest('[data-back]')) { clearInterval(tm); say(root, '返回订单列表（示例）', 'in'); return }
      const r = e.target.closest('[data-retry]'); if (r) {
        r.disabled = true; r.innerHTML = '<span class="spn"></span>重试中'
        setTimeout(() => {
          $$(root, '[data-fl] li').forEach((li) => { li.classList.add('fixed'); $(li, '.rs').textContent = '已重试成功，已写入'; li.insertAdjacentHTML('afterbegin', I('checkc')) })
          const big = $(root, '.big.wn'); big.className = 'big'; big.innerHTML = I('check'); $(root, '[data-pt]').textContent = '批量导入全部完成'; $(root, '[data-pd]').textContent = '128 条数据已全部写入。'; $(root, '[data-so]').textContent = '128'; $(root, '[data-sf]').textContent = '0'
          r.textContent = '已全部成功'; say(root, '失败项已重试成功', 'ok')
        }, 1000)
      }
    })
    start()
  },
})

/* ---- AD-STATE-005 加载中状态集 ---- */
def({
  id: 'AD-STATE-005', name: '加载中状态集', style: '四种等待形态', stage: '', wide: false,
  fit: '按场景选加载形态：按钮点击后原位变“保存中”并禁用防重复；区块用转圈加说明；跨页跳转用顶部细进度条；统计等不确定耗时的文字用加载点。每种点一下都能看到完整过程。',
  avoid: '不要所有地方都用全屏转圈；加载中必须保持按钮宽度不跳；超过 5 秒要提示可以继续其他操作或取消；减少动态偏好的用户要关掉旋转动画。',
  kw: 'loading 加载中 spinner 转圈 按钮加载 区块加载 顶部进度条 加载点 防重复提交 保存中 等待',
  css: C('adstate005', `${MENU_CSS}
§ .gr{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:12px}
§ .cd{position:relative;display:flex;flex-direction:column;padding:18px 20px;border:1px solid var(--bd2);border-radius:12px;background:var(--card);box-shadow:var(--sh);min-height:208px;overflow:hidden}
§ .cd h4{margin:0 0 2px;font-size:14px;font-weight:600}
§ .cap{margin:0 0 14px;font-size:12px;color:var(--ink3)}
§ .cs{flex:1;display:flex;align-items:center;justify-content:center;flex-direction:column;gap:10px}
§ .bt.w{min-width:112px}
§ .bt.ok{background:var(--ok-fill);border-color:var(--ok);color:#fff}
§ .zone{position:relative;width:100%;min-height:96px;border:1px solid var(--bd2);border-radius:8px;display:flex;flex-direction:column;align-items:center;justify-content:center;gap:8px;color:var(--ink2)}
§ .zone .spn{width:24px;height:24px;border-width:3px;color:var(--p-text)}
§ .zone ul{list-style:none;margin:0;padding:0 14px;width:100%}
§ .zone li{display:flex;justify-content:space-between;height:32px;align-items:center;border-bottom:1px solid var(--line)}
§ .zone li:last-child{border-bottom:0}
§ .zone li span:last-child{font-variant-numeric:tabular-nums}
§ .mp5{position:relative;width:100%;height:96px;border:1px solid var(--bd2);border-radius:8px;overflow:hidden;background:var(--bg)}
§ .mp5 .tp{position:absolute;left:0;top:0;height:3px;width:0;background:var(--p)}
§ .mp5 .tp.run{animation:adstate005-tp 1.4s var(--e) forwards}
§ .mp5 .pg{padding:16px;display:flex;flex-direction:column;gap:10px}
§ .mp5 .sk{background:var(--n6)}
§ .mp5 .lb{position:absolute;right:10px;bottom:8px;font-size:12px;color:var(--ink3)}
@keyframes adstate005-tp{0%{width:0;opacity:1}70%{width:82%}100%{width:100%;opacity:0}}
§ .dots{display:inline-flex;gap:4px;margin-left:4px;vertical-align:middle}
§ .dots i{width:5px;height:5px;border-radius:50%;background:var(--pd);animation:adstate005-dt 1s ease-in-out infinite}
§ .dots i:nth-child(2){animation-delay:.15s}§ .dots i:nth-child(3){animation-delay:.3s}
@keyframes adstate005-dt{0%,60%,100%{opacity:.25;transform:translateY(0)}30%{opacity:1;transform:translateY(-3px)}}
§ .stt{display:flex;align-items:baseline;gap:10px;font-size:14px;color:var(--ink2)}
§ .stt b{font-size:22px;font-weight:700;color:var(--ink);font-variant-numeric:tabular-nums}
@media(max-width:700px){§ .gr{grid-template-columns:1fr}}
`),
  html: () => `<div class="adstate005" data-sh><div class="gr">
    <section class="cd"><h4>按钮加载</h4><p class="cap">点击后原位变“保存中”，宽度不变、不可重复点</p><div class="cs"><button type="button" class="bt pri lg w" data-save>保存设置</button></div></section>
    <section class="cd"><h4>区块加载</h4><p class="cap">转圈加一句说明，区域大小保持稳定</p><div class="cs"><div class="zone" data-zone><ul><li><span>旗舰店</span><span>86 单</span></li><li><span>中心城店</span><span>64 单</span></li></ul></div><button type="button" class="bt" data-zr>${I('refresh')}刷新</button></div></section>
    <section class="cd"><h4>页面顶部进度条</h4><p class="cap">跨页跳转时，顶部细条先走到 80%，完成后补满淡出</p><div class="cs"><div class="mp5"><i class="tp" data-tp></i><div class="pg"><i class="sk" style="width:40%"></i><i class="sk" style="width:72%"></i><i class="sk" style="width:56%"></i></div></div><button type="button" class="bt" data-go>切换页面</button></div></section>
    <section class="cd"><h4>文字加载点</h4><p class="cap">统计类不确定耗时的数字，先显示加载点</p><div class="cs"><div class="stt"><span>本月销售额</span><b data-num>¥386,420</b></div><button type="button" class="bt" data-cnt>${I('refresh')}重新统计</button></div></section></div></div>`,
  js: (root) => {
    root.addEventListener('click', (e) => {
      const s = e.target.closest('[data-save]'); if (s) { if (s.disabled) return; s.disabled = true; s.innerHTML = '<span class="spn"></span>保存中'; setTimeout(() => { s.disabled = false; s.classList.add('ok'); s.innerHTML = `${I('check')}已保存`; setTimeout(() => { s.classList.remove('ok'); s.textContent = '保存设置' }, 1400) }, 1300); return }
      const z = e.target.closest('[data-zr]'); if (z) { const zone = $(root, '[data-zone]'); if (z.disabled) return; z.disabled = true; const keep = zone.innerHTML; zone.style.height = zone.offsetHeight + 'px'; zone.innerHTML = '<span class="spn"></span><span>正在加载门店数据…</span>'; setTimeout(() => { zone.innerHTML = '<ul><li><span>旗舰店</span><span>87 单</span></li><li><span>中心城店</span><span>65 单</span></li></ul>'; zone.style.height = ''; z.disabled = false; say(root, '门店数据已更新', 'ok') }, 1300); return }
      const g = e.target.closest('[data-go]'); if (g) { const tp = $(root, '[data-tp]'); tp.classList.remove('run'); void tp.offsetWidth; tp.classList.add('run'); return }
      const c = e.target.closest('[data-cnt]'); if (c) { const n = $(root, '[data-num]'); if (c.disabled) return; c.disabled = true; n.innerHTML = '<span class="dots"><i></i><i></i><i></i></span>'; setTimeout(() => { n.textContent = '¥387,150'; c.disabled = false }, 1200) }
    })
  },
})

/* ---- AD-STATE-006 无权限提示 ---- */
def({
  id: 'AD-STATE-006', name: '无权限提示', style: '锁定+申请', stage: '', wide: false,
  fit: '页面里某个模块或按钮用户没有权限：模块用半透明锁定层盖住并写清所需角色，提供“申请权限”并真实走完（填原因、提交、显示审批人、可撤回）；按钮则置灰并旁注原因，不直接消失。',
  avoid: '整页没权限用 403 结果页；不要悄悄隐藏用户本该知道存在的功能；不要只写“无权限”，要写缺哪个权限、谁能开通；申请提交后必须有状态可看。',
  kw: 'no permission 无权限 权限不足 申请权限 锁定 禁用原因 审批 角色 受限模块 forbidden permission denied',
  css: C('adstate006', `${MENU_CSS}
§ .cd{padding:18px 20px;border:1px solid var(--bd2);border-radius:12px;background:var(--card);box-shadow:var(--sh)}
§ .cd+.cd{margin-top:12px}
§ .cd h4{margin:0 0 2px;font-size:14px;font-weight:600}
§ .cap{margin:0 0 14px;font-size:12px;color:var(--ink3)}
§ .lk6{position:relative;border:1px solid var(--bd2);border-radius:12px;overflow:hidden;min-height:390px}
§ .bgm{filter:blur(3px);opacity:.75;padding:16px;pointer-events:none;user-select:none;display:flex;flex-direction:column;gap:12px;min-height:390px}
§ .bgm .g3{display:grid;grid-template-columns:repeat(3,1fr);gap:10px}
§ .bgm .stc{padding:12px 14px;border-radius:8px;background:var(--bg)}
§ .bgm .stc b{font-size:22px;font-weight:700}
§ .bgm .ch{display:flex;align-items:flex-end;gap:8px;height:90px}
§ .bgm .ch i{flex:1;border-radius:4px 4px 0 0;background:var(--pm)}
§ .ovl{position:absolute;inset:0;display:flex;align-items:center;justify-content:center;padding:16px;background:color-mix(in srgb,var(--card) 55%,transparent)}
§ .pb6{width:100%;max-width:400px;padding:20px 22px;border-radius:12px;background:var(--card);border:1px solid var(--bd2);box-shadow:var(--sh2);text-align:center}
§ .pb6 .lkc{display:flex;align-items:center;justify-content:center;width:44px;height:44px;margin:0 auto 10px;border-radius:50%;background:var(--pt);color:var(--p-text)}
§ .pb6 .lkc .ic{width:22px;height:22px}
§ .pb6 h5{margin:0;font-size:16px;font-weight:600}
§ .pb6 p{margin:6px 0 0;line-height:1.6;color:var(--ink2);font-size:13px}
§ .pb6 .act{display:flex;justify-content:center;gap:8px;margin-top:14px}
§ .frm{text-align:left;margin-top:12px}
§ .frm label{display:block;margin-bottom:6px;font-size:13px;color:var(--ink2)}
§ .chs{display:flex;gap:8px;margin-bottom:12px}
§ .chs button{height:32px;padding:0 12px;border:1px solid var(--bd);border-radius:8px;background:var(--card);transition:border-color .15s var(--e),background-color .15s var(--e)}
§ .chs button.on{border-color:var(--p);background:var(--pt);color:var(--p-text);font-weight:600}
§ .er{margin:4px 0 0;font-size:12px;color:var(--dg)}
§ .ip.bad{border-color:var(--dg)}
§ .sent{display:flex;flex-direction:column;align-items:center;gap:4px}
§ .sent .ic{width:30px;height:30px;color:var(--ok)}
§ .btns{display:flex;align-items:center;gap:10px;flex-wrap:wrap}
§ .why{display:inline-flex;align-items:center;gap:8px;font-size:13px;color:var(--ink3)}
§ .why button{color:var(--p-text);text-decoration:underline;text-underline-offset:3px}
`),
  html: () => `<div class="adstate006" data-sh>
    <div class="cd"><h4>受限模块</h4><p class="cap">模块锁定并写清缺什么权限、谁能开通</p>
      <div class="lk6"><div class="bgm" aria-hidden="true"><div class="g3">${[['本月收入', '¥386,420'], ['本月支出', '¥241,880'], ['净利润', '¥144,540']].map(([a, b]) => `<div class="stc"><span style="font-size:12px">${a}</span><br><b>${b}</b></div>`).join('')}</div><div class="ch">${[50, 80, 60, 90, 70, 85, 55, 75].map((h) => `<i style="height:${h}%"></i>`).join('')}</div></div>
        <div class="ovl"><div class="pb6" data-pb><div class="lkc">${I('lock')}</div><h5>没有查看「财务报表」的权限</h5><p>该模块仅限「店长」和「财务」角色查看，你当前的角色是「店员」。</p><div class="act"><button type="button" class="bt pri lg" data-ask>申请权限</button><button type="button" class="bt txt lg" data-toast="已通知管理员：林小满">联系管理员</button></div></div></div></div></div>
    <div class="cd"><h4>受限按钮</h4><p class="cap">置灰并在旁边写原因，不要直接消失</p>
      <div class="btns"><button type="button" class="bt lg" data-toast="已开始导出">${I('download')}导出订单</button><button type="button" class="bt dng lg dis" disabled aria-disabled="true">${I('trash')}删除订单</button><span class="why">需要「订单删除」权限<button type="button" data-toast="已提交申请：订单删除权限">申请</button></span></div></div></div>`,
  js: (root) => {
    const pb = $(root, '[data-pb]'); const home = pb.innerHTML; let dur = '7 天'
    root.addEventListener('click', (e) => {
      if (e.target.closest('[data-ask]')) { pb.innerHTML = `<div class="lkc">${I('key')}</div><h5>申请「财务报表」查看权限</h5><div class="frm"><label>使用时长</label><div class="chs">${['7 天', '30 天', '长期'].map((d) => `<button type="button" class="${d === dur ? 'on' : ''}" data-d="${d}">${d}</button>`).join('')}</div><label for="adstate006-r">申请原因 <span style="color:var(--dg)">*</span></label><textarea class="ip" id="adstate006-r" rows="3" maxlength="100" placeholder="如：月底对账需要核对本店收入"></textarea><p class="er" data-er hidden>请写明申请原因，方便审批人判断</p></div><div class="act"><button type="button" class="bt lg" data-cancel>取消</button><button type="button" class="bt pri lg" data-send>提交申请</button></div>`; $(pb, 'textarea').focus(); return }
      const d = e.target.closest('[data-d]'); if (d) { dur = d.dataset.d; $$(pb, '[data-d]').forEach((x) => x.classList.toggle('on', x === d)); return }
      if (e.target.closest('[data-cancel]')) { pb.innerHTML = home; return }
      if (e.target.closest('[data-send]')) {
        const t = $(pb, 'textarea'); if (t.value.trim().length < 4) { t.classList.add('bad'); $(pb, '[data-er]').hidden = false; t.focus(); return }
        const b = $(pb, '[data-send]'); b.disabled = true; b.innerHTML = '<span class="spn"></span>提交中'
        setTimeout(() => { pb.innerHTML = `<div class="sent">${I('checkc')}<h5>申请已提交</h5><p>权限：财务报表（查看）· ${dur}<br>审批人：林小满（店长），通常 1 个工作日内处理，结果会发到消息中心。</p></div><div class="act"><button type="button" class="bt lg" data-withdraw>撤回申请</button></div>`; say(root, '权限申请已提交', 'ok') }, 800); return
      }
      if (e.target.closest('[data-withdraw]')) { pb.innerHTML = home; say(root, '已撤回申请', 'in'); return }
    })
    root.addEventListener('input', (e) => { if (e.target.matches('textarea')) { e.target.classList.remove('bad'); const r = $(pb, '[data-er]'); if (r) r.hidden = true } })
  },
})

/* ---- 各类别“怎么选” ---- */
guide('ad', 'NAV', [
  ['后台主导航，菜单一二级分明', '侧栏菜单·浅色', '浅色是基准，二级展开、收起图标栏都齐；数据密集、要突出内容区时才换深色版'],
  ['要品牌感、内容区更突出的运营后台', '侧栏菜单·深色', '交互与浅色一致，高亮用主题浅色标记，别另加鲜艳色'],
  ['框架顶部：搜索、消息、账号、测试环境标识', '后台顶栏', '门店切换只放这一处；两级以上页面才放面包屑'],
  ['页面很多、要来回切换', '页面标签栏', '打开过的页面留成标签，首页固定、可批量关闭'],
  ['订单、会员这类详情页的页头', '详情页页头', '对象名作标题，不重复菜单名；主按钮只一个，危险操作收进“更多”'],
  ['一级列表页顶部：筛选和新建、导出', '一级页操作栏', '左筛选右按钮，默认视图是最该处理的子集，已生效筛选可移除'],
  ['列表底部翻页', '分页导航', '默认每页 20 条，可选 10/20/50/100，超过 7 页折叠'],
  ['几十个页面或操作想一键直达', '全局命令面板', 'Ctrl K 呼出，输入即过滤，上下键选择；菜单少的系统不需要'],
])
guide('ad', 'FB', [
  ['读完点“我知道了”的规则、公告', '说明对话框', '居中遮罩，点遮罩、× 或 Esc 关闭；长内容只在框内滚动'],
  ['删除、停业这类不可撤销的操作', '危险操作确认框', '写清后果并勾选“已了解”，按钮写动作名，取消在左、危险按钮在右'],
  ['点一行看详情、顺手改几项', '居中详情面板', '不用右侧抽屉；查看和编辑在同一面板里切换，保存后同步列表'],
  ['新增或快速编辑 4–6 个字段', '表单弹窗', '必填标星、字段下写错误原因，保存中防重复，未保存关闭先确认'],
  ['表格行里的停用、删除', '气泡确认', '贴着按钮弹，轻量；后果重的用居中确认框'],
  ['页面里常驻的说明与结果', '提示条', '四种语气，重要错误常驻直到处理，次要的可关闭'],
  ['系统事件（新订单、预警、导出完成）', '通知卡', '右上角堆叠最多 4 条，错误常驻；用户自己操作的结果用轻提示'],
  ['操作后的即时反馈、行内开关', '轻提示', '成功一句话，失败写原因；开关失败要回滚并在原位说明'],
  ['图标按钮、截断文字、字段帮助', '提示与气泡卡', '悬停和聚焦都能出现；触屏没有悬停，关键信息别只放这里'],
  ['导入导出等耗时任务、区域刷新', '加载遮罩与进度', '区域用遮罩盖住不跳位，长任务给阶段和取消'],
])
guide('ad', 'STATE', [
  ['列表没数据、搜索没结果、首次使用、加载失败', '空状态', '每种都带一个明确下一步；有筛选时要说“没找到”并给清除入口'],
  ['整页打不开（无权限、不存在、服务异常）', '异常结果页', '写发生了什么、可能原因、下一步；500 带请求编号'],
  ['首次加载超过 300 毫秒', '骨架屏', '布局与真实内容一致，原位替换不跳位'],
  ['发货、提交、批量导入做完了', '操作结果页', '成功页给继续与返回；部分失败列出每条原因并支持只重试失败项'],
  ['按钮、区块、跨页、统计数字的等待', '加载中状态集', '按场景选形态，按钮保持宽度并禁用防重复'],
  ['某个模块或按钮用户没有权限', '无权限提示', '锁定并写缺什么权限、谁能开通，申请要能走完、可撤回'],
])
})()
