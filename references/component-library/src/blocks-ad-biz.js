/* ===== 后台管理 · 流程与协作(FLOW) / 系统管理(MGMT) / 整页布局(PAGE) =====
 * 整份文件包在一个函数里，所有 const 都是私有的，不会和其他 blocks-*.js 冲突。
 * 每个组件的 CSS = 共用零件 K(前缀, '零件名...') + 自己的样式；共用零件按块前缀展开，所以每个块的 CSS 自成一体，可单独复制。
 * 通用类名一律带 z- 前缀（z-btn z-tag z-in z-ck z-sw z-tbl z-tabs z-seg z-dd z-modal），避免和库里的 .btn .tg .sw .tab 串。 */
;(() => {
Object.assign(LINE, {
  bz_branch: '<circle cx="6" cy="5.5" r="2.2"/><circle cx="6" cy="18.5" r="2.2"/><circle cx="18" cy="8.5" r="2.2"/><path d="M6 7.7v8.6M18 10.7v.8a3.5 3.5 0 0 1-3.5 3.5h-5A3.5 3.5 0 0 0 6 18"/>',
  bz_panel: '<rect x="3.5" y="4.5" width="17" height="15" rx="2.5"/><path d="M9.5 4.5v15"/>',
  bz_shop: '<path d="M4 9.5 5.5 4.5h13L20 9.5"/><path d="M4 9.5a2.7 2.7 0 0 0 5.3 0 2.7 2.7 0 0 0 5.4 0 2.7 2.7 0 0 0 5.3 0M5.5 12.5V20h13v-7.5"/>',
  bz_desktop: '<rect x="3" y="4.5" width="18" height="12" rx="2"/><path d="M8.5 20h7M12 16.5V20"/>',
  bz_mobile: '<rect x="7" y="3" width="10" height="18" rx="2.5"/><path d="M11 17.5h2"/>',
  bz_send: '<path d="M20.5 3.5 10 14M20.5 3.5 14 20.5l-4-6.5-6.5-4z"/>',
  bz_timer: '<circle cx="12" cy="13.5" r="7.5"/><path d="M12 9.5v4l2.5 1.5M9.5 3.5h5"/>',
  bz_ban: '<circle cx="12" cy="12" r="8.5"/><path d="m6 6 12 12"/>',
  bz_undo: '<path d="M9 14 4 9l5-5"/><path d="M4 9h10a6 6 0 0 1 0 12h-3"/>',
  bz_note: '<path d="M5 4.5h14v11l-4 4H5z"/><path d="M15 19.5v-4h4M8.5 9h7M8.5 12.5h4"/>',
  bz_user_check: '<circle cx="9.5" cy="8" r="3.5"/><path d="M3 20c0-3.6 2.9-6 6.500-6 1.600 0 3 .4 4.200 1.200M15 18l2 2 4-4.500"/>',
  bz_pulse: '<path d="M3 12h4l2.500-6 4 12 2.500-6H21"/>',
  bz_zoom: '<circle cx="11" cy="11" r="6.500"/><path d="m20.500 20.500-4.700-4.700M8.500 11h5M11 8.500v5"/>',
  bz_stack: '<path d="M4 7h16M4 12h16M4 17h10"/>',
})

/* ---------- 小工具 ---------- */
const $ = (r, s) => r.querySelector(s)
const $$ = (r, s) => [...r.querySelectorAll(s)]
const esc = (s) => String(s).replace(/[&<>"]/g, (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' })[c])
const ic = (n, c = '') => `<i class="z-ic ${c}">${sv(n)}</i>`
const toast = (root, msg) => IX.toast(root, msg)
const openOv = (root, n) => { const o = $(root, `[data-ov="${n}"]`); if (!o) return; o.classList.add('show'); const f = $(o, 'textarea,input,.z-btn.p'); if (f) setTimeout(() => f.focus({ preventScroll: true }), 30) }
const closeOv = (el) => { const o = el.closest ? el.closest('[data-ov]') : el; if (o) o.classList.remove('show') }
/* Esc 关闭块内所有弹层；Enter 不处理 */
const wireEsc = (root) => root.addEventListener('keydown', (e) => { if (e.key === 'Escape') $$(root, '.ix-ov.show').forEach((o) => o.classList.remove('show')) })
const pad = (n) => String(n).padStart(2, '0')
const modal = (name, title, body, foot, w = 440) => `<div class="ix-ov" data-ov="${name}"><div class="ix-mask"></div><div class="z-modal" style="width:min(${w}px,calc(100% - 32px))" role="dialog" aria-modal="true" aria-label="${title}"><div class="mh"><b>${title}</b><button class="z-x" type="button" data-close aria-label="关闭">${ic('close')}</button></div><div class="mb">${body}</div>${foot ? `<div class="mf">${foot}</div>` : ''}</div></div>`
/* 下拉：items 为字符串或 [值, 文案]；用 ix 的 dd，选中后 [data-label] 自动更新 */
const dd = (items, cur, o = {}) => `<div class="z-dd${o.up ? ' up' : ''}${o.cls ? ' ' + o.cls : ''}" data-ix="dd" ${o.attr || ''}><button type="button" data-tg aria-haspopup="listbox"><span data-label>${(items.map((x) => (Array.isArray(x) ? x : [x, x])).find((x) => x[0] === cur) || [0, cur])[1]}</span>${ic('down', 's')}</button><div class="menu" role="listbox">${items.map((x) => { const [v, t] = Array.isArray(x) ? x : [x, x]; return `<div data-o data-v="${t}" data-val="${v}" class="${v === cur ? 'on' : ''}" role="option">${t}</div>` }).join('')}</div></div>`
/* 带下划线的标签页（ix tabs）：data-l 用来按粗体预留宽度，切换时不抖 */
const tabs = (items, cur, attrs = '') => `<div class="z-tabs" data-ix="tabs" role="tablist" ${attrs}>${items.map(([k, t, n]) => `<button type="button" role="tab" data-t="${k}" class="${k === cur ? 'on' : ''}"><span class="lb" data-l="${t}${n != null ? ' ' + n : ''}">${t}${n != null ? `<em class="z-n">${n}</em>` : ''}</span></button>`).join('')}<i class="ink"></i></div>`
const seg = (items, cur, attrs = '') => `<div class="z-seg" data-ix="tabs" role="tablist" ${attrs}>${items.map(([k, t]) => `<button type="button" role="tab" data-t="${k}" class="${k === cur ? 'on' : ''}">${t}</button>`).join('')}</div>`
const ck = (on, attr = '') => `<span class="z-ck${on === 1 ? ' on' : on === 2 ? ' part' : ''}" role="checkbox" tabindex="0" aria-checked="${on === 1 ? 'true' : on === 2 ? 'mixed' : 'false'}" ${attr}></span>`
const sw = (on, attr = '') => `<span class="z-sw${on ? ' on' : ''}" role="switch" tabindex="0" aria-checked="${!!on}" ${attr}></span>`
const tag = (t, tone = '') => `<span class="z-tag ${tone}">${t}</span>`
const person = (i, size = 28) => `${critter(i, size)}<span>${NAMES[i % 12]}</span>`

/* ---------- 共用样式零件（§ 会替换成块的根选择器） ---------- */
const PARTS = {
  root: `§{font-size:14px;line-height:1.5;color:var(--ink);width:100%;--bd:var(--n8);--sf:var(--n2);--okb:var(--ok-bg);--wn:var(--warn);--wnb:var(--warn-bg);--dg:var(--danger);--dgb:var(--danger-bg);--mu:var(--neutral);--mub:var(--neutral-bg);text-align:left}§ *{box-sizing:border-box}§ button,§ input,§ textarea{font:inherit;color:inherit}§ button{cursor:pointer;border:0;background:none;padding:0;text-align:inherit}§ button:focus{outline:none}§ button:focus-visible{outline:1px solid var(--ink2);outline-offset:1px}§ svg{flex:none}§ p,§ h3,§ h4,§ dl,§ dd,§ ul,§ ol{margin:0;padding:0}§ ul,§ ol{list-style:none}§ .z-ic{display:inline-flex;width:16px;height:16px;flex:none}§ .z-ic.l{width:20px;height:20px}§ .z-ic.s{width:14px;height:14px}§ .z-ic.xl{width:24px;height:24px}§ .z-n{margin-left:6px;font-size:12px;font-weight:600;color:var(--ink3)}§ .z-card{background:var(--card);border:1px solid var(--line2);border-radius:12px}§ .z-who{display:inline-flex;align-items:center;gap:8px;text-align:left}@keyframes zbin{from{opacity:0;transform:translateY(8px)}to{opacity:1;transform:none}}@keyframes zspin{to{transform:rotate(360deg)}}`,
  btn: `§ .z-btn{display:inline-flex;align-items:center;justify-content:center;gap:6px;height:32px;padding:0 14px;border-radius:8px;border:1px solid var(--bd);background:var(--card);white-space:nowrap;transition:background-color .15s,border-color .15s,color .15s}§ .z-btn:hover:not(:disabled){border-color:var(--ink3);background:var(--n1)}§ .z-btn.p{background:var(--p);border-color:var(--p);color:#fff}§ .z-btn.p:hover:not(:disabled){background:var(--pd);border-color:var(--pd)}§ .z-btn.t{border-color:transparent;background:none;color:var(--p-text);padding:0 8px}§ .z-btn.t:hover:not(:disabled){background:var(--pt);border-color:transparent}§ .z-btn.d{color:var(--dg)}§ .z-btn.d:hover:not(:disabled){background:var(--dgb);border-color:var(--danger-line)}§ .z-btn.l{height:36px;padding:0 18px}§ .z-btn:disabled{opacity:.45;cursor:not-allowed}§ .z-x{display:inline-flex;align-items:center;justify-content:center;width:32px;height:32px;border-radius:8px;color:var(--ink2);flex:none}§ .z-x:hover{background:var(--mub)}§ .z-spin{width:14px;height:14px;border-radius:50%;border:2px solid currentColor;border-right-color:transparent;animation:zspin .7s linear infinite;display:inline-block;flex:none}`,
  tag: `§ .z-tag{display:inline-flex;align-items:center;gap:5px;height:22px;padding:0 8px;border-radius:4px;font-size:12px;font-weight:600;line-height:1;white-space:nowrap;background:var(--mub);color:var(--mu)}§ .z-tag.ok{background:var(--okb);color:var(--ok)}§ .z-tag.wn{background:var(--wnb);color:var(--wn)}§ .z-tag.dg{background:var(--dgb);color:var(--dg)}§ .z-tag.in{background:var(--pt);color:var(--p-text)}§ .z-tag.dot::before{content:"";width:6px;height:6px;border-radius:50%;background:currentColor}`,
  in: `§ .z-in{display:block;width:100%;height:36px;padding:0 12px;border:1px solid var(--bd);border-radius:8px;background:var(--card);outline:none;transition:border-color .15s}§ .z-in:focus{border-color:var(--ink2)}§ .z-in::placeholder{color:var(--ink3)}§ .z-in.er{border-color:var(--dg)}§ textarea.z-in{height:auto;padding:8px 12px;line-height:1.55;resize:none}§ select.z-in{appearance:none;-webkit-appearance:none;padding-right:32px;background:var(--card) url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='none' stroke='%235B6470' stroke-width='2' stroke-linecap='round' stroke-linejoin='round'%3E%3Cpath d='m6 9 6 6 6-6'/%3E%3C/svg%3E") right 10px center/14px no-repeat}§ .z-in.sm{height:32px}§ .z-er{color:var(--dg);font-size:12px;margin-top:4px}§ .z-lb{font-size:14px;color:var(--ink2)}§ .z-req::before{content:"*";color:var(--dg);margin-right:4px}`,
  ck: `§ .z-ck{display:inline-flex;width:16px;height:16px;border:1px solid var(--n11);border-radius:4px;background:var(--card) center/12px no-repeat;cursor:pointer;flex:none;vertical-align:middle;transition:background-color .15s,border-color .15s}§ .z-ck:hover{border-color:var(--ink3)}§ .z-ck.on,§ .z-ck.part{background-color:var(--p);border-color:var(--p)}§ .z-ck.on{background-image:url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='none' stroke='%23fff' stroke-width='3.2' stroke-linecap='round' stroke-linejoin='round'%3E%3Cpath d='m5 12.500 4.500 4.500L19 7.500'/%3E%3C/svg%3E")}§ .z-ck.part{background-image:url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='none' stroke='%23fff' stroke-width='3.2' stroke-linecap='round'%3E%3Cpath d='M6 12h12'/%3E%3C/svg%3E")}§ .z-ck.dis{opacity:.4;cursor:not-allowed}`,
  sw: `§ .z-sw{position:relative;display:inline-block;width:36px;height:20px;border-radius:10px;background:var(--n11);cursor:pointer;flex:none;transition:background-color .2s}§ .z-sw::after{content:"";position:absolute;left:2px;top:2px;width:16px;height:16px;border-radius:50%;background:var(--card);box-shadow:0 1px 2px var(--sh25);transition:transform .2s cubic-bezier(.2,0,0,1)}§ .z-sw.on{background:var(--p)}§ .z-sw.on::after{transform:translateX(16px)}§ .z-sw.busy{opacity:.55;pointer-events:none}`,
  tbl: `§ .z-tbl{width:100%;border-collapse:collapse}§ .z-tbl th{height:44px;padding:0 12px;text-align:center;font-weight:600;color:var(--ink2);background:var(--n2);border-bottom:1px solid var(--line);white-space:nowrap}§ .z-tbl td{height:48px;padding:0 12px;text-align:center;border-bottom:1px solid var(--line)}§ .z-tbl td.l{text-align:left;padding-left:16px}§ .z-tbl td.r{text-align:right;padding-right:24px;font-variant-numeric:tabular-nums}§ .z-tbl tbody tr:hover td{background:var(--n1)}§ .z-tbl tr.sel td{background:var(--pt)}`,
  tabs: `§ .z-tabs{position:relative;display:flex;gap:28px;border-bottom:1px solid var(--line)}§ .z-tabs button{height:44px;color:var(--ink2);transition:color .15s}§ .z-tabs button:hover{color:var(--ink)}§ .z-tabs button.on{color:var(--ink)}§ .z-tabs button.on .lb{font-weight:600}§ .z-tabs .lb{display:inline-block}§ .z-tabs .lb::after{content:attr(data-l);display:block;height:0;overflow:hidden;visibility:hidden;font-weight:600}§ .z-tabs .ink{position:absolute;bottom:-1px;left:0;width:0;height:2px;background:var(--p);transition:left .25s cubic-bezier(.2,0,0,1),width .25s cubic-bezier(.2,0,0,1)}`,
  seg: `§ .z-seg{display:inline-flex;gap:2px;padding:2px;border-radius:8px;background:var(--n4)}§ .z-seg button{height:28px;padding:0 12px;border-radius:4px;color:var(--ink2);white-space:nowrap;transition:background-color .15s,color .15s}§ .z-seg button:hover{color:var(--ink)}§ .z-seg button.on{background:var(--lift);color:var(--ink);box-shadow:0 1px 2px var(--sh12)}`,
  modal: `§ .z-modal{position:relative;margin:auto;max-height:calc(100% - 32px);overflow:auto;background:var(--card2);border-radius:12px;box-shadow:0 16px 48px var(--sh22);animation:zbin .2s cubic-bezier(.2,0,0,1)}§ .z-modal .mh{display:flex;align-items:center;justify-content:space-between;padding:10px 12px 10px 20px;border-bottom:1px solid var(--line);font-size:16px}§ .z-modal .mh b{font-weight:600}§ .z-modal .mb{padding:20px}§ .z-modal .mf{display:flex;justify-content:flex-end;gap:8px;padding:0 20px 20px}`,
  dd: `§ .z-dd [data-tg]{display:inline-flex;align-items:center;justify-content:space-between;gap:8px;height:32px;min-width:96px;padding:0 10px 0 12px;border:1px solid var(--bd);border-radius:8px;background:var(--card);white-space:nowrap}§ .z-dd [data-tg]:hover{border-color:var(--ink3)}§ .z-dd.open [data-tg]{border-color:var(--ink2)}§ .z-dd .menu{background:var(--card2);border:1px solid var(--n6);border-radius:8px;padding:4px;box-shadow:0 8px 24px var(--sh12);min-width:100%}§ .z-dd .menu [data-o]{display:flex;align-items:center;height:32px;padding:0 10px;border-radius:4px;cursor:pointer;white-space:nowrap}§ .z-dd .menu [data-o]:hover{background:var(--sf)}§ .z-dd .menu [data-o].on{background:var(--pt);color:var(--p-text)}§ .z-dd.up .menu{top:auto;bottom:calc(100% + 6px)}§ .z-dd.r .menu{left:auto;right:0}`,
}
const K = (p, want = '') => ['root', ...want.split(' ').filter(Boolean)].map((k) => PARTS[k]).join('').replace(/§/g, '.' + p)

/* ================= FLOW 流程与协作 ================= */
/* ---- AD-FLOW-001 审批流程图 ---- */
const APV = () => [
  { k: 'a', t: '发起申请', i: 0, dept: '运营部', st: 'done', at: '11-03 09:12', note: '采购 20 台门店收银终端，预算 ¥48,000，用于华东 6 家门店更新。' },
  { k: 'b', t: '部门主管', i: 1, dept: '运营部', st: 'done', at: '11-03 10:40', note: '同意。现有设备已使用超过 5 年，故障率偏高，确需更新。' },
  { k: 'c', t: '财务复核', i: 4, dept: '财务部', st: 'doing', at: '11-03 14:05', note: '', waited: 5, limit: 24 },
  { k: 'd', t: '总经理审批', i: 2, dept: '管理层', st: 'wait', at: '', note: '' },
  { k: 'e', t: '采购下单', i: 8, dept: '仓储部', st: 'wait', at: '', note: '' },
]
const APV_ST = { done: ['已通过', 'ok'], doing: ['审批中', 'in'], wait: ['待审批', ''], rej: ['已驳回', 'dg'] }
const apvFlow = (ns, sel) => ns.map((n, i) => {
  const l = i === 0 ? 'no' : ns[i - 1].st === 'done' ? 'ok' : ''
  const r = i === ns.length - 1 ? 'no' : n.st === 'done' ? 'ok' : ''
  const icon = { done: 'check', doing: 'clock', wait: 'clock', rej: 'close' }[n.st]
  const tm = n.st === 'wait' ? '等待上一节点' : n.st === 'doing' ? `已等待 ${n.waited} 小时` : n.at
  return `<button type="button" class="nd${n.k === sel ? ' on' : ''}" data-k="${n.k}" aria-label="${n.t}，${APV_ST[n.st][0]}"><span class="rw"><i class="${l}"></i><span class="cir ${n.st}">${ic(icon)}</span><i class="${r}"></i></span><span class="cd"><b>${n.t}</b><span class="pp">${critter(n.i, 20)}${NAMES[n.i]}</span><span class="tm">${tm}</span></span></button>`
}).join('')
const apvDetail = (ns, sel) => {
  const n = ns.find((x) => x.k === sel), [lab, tone] = APV_ST[n.st]
  const dl = (k, v) => `<div><dt>${k}</dt><dd>${v}</dd></div>`
  let rows = dl('审批人', `<span class="z-who">${critter(n.i, 24)}${NAMES[n.i]} · ${n.dept}</span>`)
  if (n.st === 'doing') rows += dl('到达时间', n.at) + dl('处理时限', `<span class="sla"><i style="width:${Math.round((n.waited / n.limit) * 100)}%"></i></span><em class="z-n">已 ${n.waited} / ${n.limit} 小时</em>`)
  else if (n.st === 'wait') rows += dl('预计到达', '上一节点通过后自动流转')
  else rows += dl(n.st === 'rej' ? '驳回时间' : '处理时间', n.at)
  if (n.note) rows += dl(n.st === 'rej' ? '驳回原因' : '审批意见', esc(n.note))
  const acts = n.st === 'doing' ? '<button class="z-btn d" type="button" data-act="rej">驳回</button><button class="z-btn p" type="button" data-act="pass">通过</button>' : n.st === 'rej' ? '<button class="z-btn" type="button" data-act="reset">重新发起</button>' : ''
  return `<div class="th"><div class="tt"><b>${n.t}</b>${tag(lab, tone + ' dot')}</div><dl>${rows}</dl></div><div class="ac">${acts}</div>`
}
def({
  id: 'AD-FLOW-001', name: '审批流程图', style: '节点状态', wide: true,
  fit: '报销、采购、请假等多级审批的进度展示：点节点看审批人、意见与时限，当前节点可直接通过或驳回',
  avoid: '带并行会签、条件分支的流程（改用工作流编排）；节点超过 7 个时横向太长，应改成竖向时间线',
  kw: '审批 流程图 节点 通过 驳回 会签 approval 进度 采购申请 stepper',
  css: K('adflow001', 'btn tag modal in') + `.adflow001{width:1000px;max-width:100%;background:var(--card);border:1px solid var(--line2);border-radius:12px}.adflow001 .hd{display:flex;align-items:center;justify-content:space-between;gap:12px;padding:16px 20px;border-bottom:1px solid var(--line)}.adflow001 .hd h4{font-size:16px;font-weight:600}.adflow001 .hd p{font-size:12px;color:var(--ink3);margin-top:2px}.adflow001 .flow{display:flex;padding:24px 14px 6px;overflow-x:auto}.adflow001 .nd{flex:1 0 152px;display:flex;flex-direction:column;gap:12px;padding:0 6px;text-align:center}.adflow001 .rw{display:flex;align-items:center}.adflow001 .rw>i{flex:1;height:2px;background:var(--n8)}.adflow001 .rw>i.ok{background:var(--ok-fill)}.adflow001 .rw>i.no{background:none}.adflow001 .cir{display:flex;align-items:center;justify-content:center;width:32px;height:32px;border-radius:50%;border:2px solid var(--n8);background:var(--mub);color:var(--mu);flex:none}.adflow001 .cir.done{background:var(--okb);border-color:var(--ok);color:var(--ok)}.adflow001 .cir.doing{background:var(--pt);border-color:var(--p);color:var(--p-text)}.adflow001 .cir.rej{background:var(--dgb);border-color:var(--dg);color:var(--dg)}.adflow001 .cd{display:flex;flex-direction:column;align-items:center;gap:6px;padding:10px 8px;border:1px solid var(--line2);border-radius:8px;background:var(--card);transition:border-color .15s,box-shadow .15s}.adflow001 .nd:hover .cd{border-color:var(--n10)}.adflow001 .nd.on .cd{border-color:var(--p);box-shadow:0 0 0 1px var(--p)}.adflow001 .cd b{font-weight:600}.adflow001 .pp{display:inline-flex;align-items:center;gap:6px;color:var(--ink2)}.adflow001 .tm{font-size:12px;color:var(--ink3)}.adflow001 .dtl{display:flex;flex-wrap:wrap;align-items:flex-end;justify-content:space-between;gap:16px;margin:16px 20px 20px;padding:16px 20px;border-radius:8px;background:var(--sf)}.adflow001 .th{flex:1 1 420px;min-width:0}.adflow001 .tt{display:flex;align-items:center;gap:10px;margin-bottom:10px}.adflow001 .tt b{font-size:16px;font-weight:600}.adflow001 dl{display:grid;grid-template-columns:repeat(auto-fit,minmax(200px,1fr));gap:10px 24px}.adflow001 dt{font-size:12px;color:var(--ink3)}.adflow001 dd{margin-top:2px;overflow-wrap:anywhere}.adflow001 .sla{display:inline-block;vertical-align:middle;width:120px;height:6px;border-radius:3px;background:var(--n7);overflow:hidden}.adflow001 .sla i{display:block;height:100%;background:var(--p)}.adflow001 dd .z-n{margin-left:8px}.adflow001 .ac{display:flex;gap:8px}`,
  html: () => `<div class="adflow001"><div class="hd"><div><h4>采购申请 · 门店收银终端更新</h4><p>AP-20261103-017 · 林小满 发起于 11-03 09:12 · 预算 ¥48,000</p></div>${tag('审批中', 'in dot')}</div><div class="flow">${apvFlow(APV(), 'c')}</div><div class="dtl">${apvDetail(APV(), 'c')}</div>${modal('rj', '驳回申请', '<label class="z-lb z-req" for="adflow001-rs">驳回原因</label><textarea id="adflow001-rs" class="z-in rjtxt" rows="3" maxlength="100" placeholder="说明驳回的原因，申请人会收到通知" style="margin-top:8px"></textarea><p style="font-size:12px;color:var(--ink3);margin-top:6px">必填，至少 2 个字</p>', '<button class="z-btn" type="button" data-close>取消</button><button class="z-btn p" type="button" data-act="rjok" disabled>确认驳回</button>')}</div>`,
  js: (root) => {
    const el = $(root, '.adflow001'); let ns = APV(), sel = 'c'
    const draw = () => {
      $(el, '.flow').innerHTML = apvFlow(ns, sel); $(el, '.dtl').innerHTML = apvDetail(ns, sel)
      const rej = ns.some((n) => n.st === 'rej'), all = ns.every((n) => n.st === 'done'), t = $(el, '.hd .z-tag')
      t.className = 'z-tag dot ' + (rej ? 'dg' : all ? 'ok' : 'in'); t.textContent = rej ? '已驳回' : all ? '已通过' : '审批中'
    }
    root.addEventListener('click', (e) => {
      const nd = e.target.closest('.nd'); if (nd) { sel = nd.dataset.k; draw(); return }
      const a = e.target.closest('[data-act]'); if (!a) return
      const i = ns.findIndex((n) => n.k === sel), n = ns[i], act = a.dataset.act
      if (act === 'pass') {
        n.st = 'done'; n.at = '刚刚'; n.note = '同意'; const nx = ns[i + 1]
        if (nx) { nx.st = 'doing'; nx.at = '刚刚'; nx.waited = 0; nx.limit = 24; sel = nx.k; toast(root, `已通过，流转到「${nx.t}」`) } else toast(root, '审批全部完成')
        draw()
      } else if (act === 'rej') { $(root, '.rjtxt').value = ''; $(root, '[data-act=rjok]').disabled = true; openOv(root, 'rj') }
      else if (act === 'rjok') { n.st = 'rej'; n.at = '刚刚'; n.note = $(root, '.rjtxt').value.trim(); closeOv(a); draw(); toast(root, '已驳回，申请人会收到通知') }
      else if (act === 'reset') { ns = APV(); sel = 'c'; draw(); toast(root, '已重新发起') }
    })
    root.addEventListener('input', (e) => { if (e.target.matches('.rjtxt')) $(root, '[data-act=rjok]').disabled = e.target.value.trim().length < 2 })
    wireEsc(root)
  },
})

/* ---- AD-FLOW-002 任务看板 ---- */
const KB_TAG = { 运营: 'wn', 功能: 'in', 缺陷: 'dg', 优化: 'ok' }
const KB_PRI = { 高: 'var(--danger)', 中: 'var(--warn)', 低: 'var(--ink3)' }
const KB = [
  { k: 'todo', t: '待处理', cs: [['梳理双十一活动规则与优惠叠加说明', '运营', '高', '11-06', 0], ['会员等级权益页改版', '功能', '中', '11-12', 3], ['库存预警阈值支持按仓库单独设置，低于阈值时通知仓储负责人与采购专员', '优化', '中', '11-15', 5], ['订单报表导出时间范围超过 31 天时报错', '缺陷', '高', '11-05', 2]] },
  { k: 'doing', t: '进行中', wip: 4, cs: [['优惠券核销接口联调', '功能', '高', '11-05', 1], ['退款审核流程支持多级审批', '功能', '中', '11-08', 4], ['小程序首页加载速度优化', '优化', '低', '11-10', 6]] },
  { k: 'review', t: '待验收', cs: [['客服工单自动分配规则', '功能', '中', '11-04', 7], ['修复积分过期提醒重复推送', '缺陷', '高', '11-04', 9]] },
  { k: 'done', t: '已完成', cs: [['门店营业状态一键切换', '功能', '中', '11-02', 10], ['支付回调幂等校验', '缺陷', '高', '11-01', 11]] },
]
const kbCard = (c) => `<div class="kc" data-t="${esc(c[0])}"><span class="grip" aria-label="拖动排序">${ic('drag', 's')}</span><p class="tt">${esc(c[0])}</p><div class="mm"><span class="z-tag ${KB_TAG[c[1]]}">${c[1]}</span><span class="pr" style="color:${KB_PRI[c[2]]}" title="优先级${c[2]}">${ic('flag', 's')}${c[2]}</span>${c[3] ? `<span class="du">${ic('calendar', 's')}${c[3]}</span>` : ''}<span class="as">${critter(c[4], 22)}</span></div></div>`
const kbCol = (col) => `<section class="col" data-k="${col.k}"${col.wip ? ` data-wip="${col.wip}"` : ''}><header><b>${col.t}</b><span class="cnt z-tag">${col.cs.length}${col.wip ? '/' + col.wip : ''}</span><button type="button" class="z-x plus" aria-label="在「${col.t}」添加卡片" title="添加卡片">${ic('plus')}</button></header><div class="lst">${col.cs.map(kbCard).join('')}</div></section>`
def({
  id: 'AD-FLOW-002', name: '任务看板', style: '拖拽换列', wide: true,
  fit: '工单、需求、售后、线索等按阶段流转的事务：鼠标拖卡片到别的列即换状态，列头 + 号直接加卡片，进行中有在制上限',
  avoid: '阶段超过 6 列或卡片上百张（改用带状态标签的列表）；需要严格审批留痕的流程（改用审批流程图）',
  kw: '看板 kanban 拖拽 卡片 任务 工单 阶段 泳道 在制上限 drag',
  css: K('adflow002', 'btn tag in') + `.adflow002{width:1400px;max-width:100%;position:relative;background:var(--card);border:1px solid var(--line2);border-radius:12px}.adflow002 .tb{display:flex;align-items:center;justify-content:space-between;flex-wrap:wrap;gap:10px 16px;padding:14px 16px;border-bottom:1px solid var(--line)}.adflow002 .sq{position:relative;width:260px;max-width:100%}.adflow002 .sq .z-ic{position:absolute;left:10px;top:9px;color:var(--ink3)}.adflow002 .sq input{padding-left:32px;height:32px}.adflow002 .tb span.tip{font-size:12px;color:var(--ink3)}.adflow002 .board{display:grid;grid-template-columns:repeat(4,minmax(236px,1fr));gap:12px;padding:16px;overflow-x:auto;align-items:start}.adflow002 .col{display:flex;flex-direction:column;gap:10px;padding:10px;border-radius:12px;background:var(--soft);min-height:360px;transition:background-color .15s,box-shadow .15s}.adflow002 .col.hot{background:var(--pt);box-shadow:inset 0 0 0 1.5px var(--p)}.adflow002 .col header{display:flex;align-items:center;gap:8px;padding:2px 2px 0}.adflow002 .col header b{font-weight:600}.adflow002 .col .cnt{background:var(--card)}.adflow002 .col .cnt.full{background:var(--wnb);color:var(--wn)}.adflow002 .col .plus{margin-left:auto;width:32px;height:32px}.adflow002 .lst{display:flex;flex-direction:column;gap:8px;flex:1;min-height:60px}.adflow002 .lst:not(:has(.kc,.slot,.nw))::before{content:"暂无卡片，可拖到这里";display:flex;align-items:center;justify-content:center;height:72px;border:1px dashed var(--n9);border-radius:8px;color:var(--ink3);font-size:12px}.adflow002 .kc{position:relative;padding:10px 12px 10px 28px;border:1px solid var(--line2);border-radius:8px;background:var(--card);box-shadow:0 1px 2px var(--sh04);cursor:grab;user-select:none;-webkit-user-select:none;transition:border-color .15s,box-shadow .15s}.adflow002 .kc:hover{border-color:var(--n10);box-shadow:0 2px 6px var(--sh08)}.adflow002 .kc .grip{position:absolute;left:6px;top:11px;display:flex;color:var(--ink5);touch-action:none;cursor:grab}.adflow002 .kc .tt{line-height:1.5;overflow-wrap:anywhere}.adflow002 .kc .mm{display:flex;align-items:center;gap:10px;margin-top:8px;font-size:12px;color:var(--ink3)}.adflow002 .kc .pr,.adflow002 .kc .du{display:inline-flex;align-items:center;gap:3px}.adflow002 .kc .as{margin-left:auto;display:flex}.adflow002 .kc.ghost{position:absolute;z-index:50;pointer-events:none;cursor:grabbing;box-shadow:0 14px 30px var(--sh24);border-color:var(--p);opacity:.96}.adflow002 .kc.flash{animation:zbin .3s cubic-bezier(.2,0,0,1)}.adflow002 .slot{border:1.5px dashed var(--p);border-radius:8px;background:var(--pt)}.adflow002 .nw{padding:0}.adflow002 .nw input{height:36px}.adflow002 .kc.mutedby{display:none}`,
  html: () => `<div class="adflow002"><div class="tb"><label class="sq">${ic('search')}<input class="z-in" type="search" placeholder="搜索卡片标题" aria-label="搜索卡片"></label><span class="tip">拖动卡片即可换列；「进行中」最多同时 4 张</span></div><div class="board">${KB.map(kbCol).join('')}</div></div>`,
  js: (root) => {
    const el = $(root, '.adflow002'), board = $(el, '.board'); let d = null
    const refresh = () => $$(el, '.col').forEach((c) => {
      const n = $$(c, '.lst > .kc:not(.ghost)').filter((x) => x.style.display !== 'none').length, w = +c.dataset.wip || 0, t = $(c, '.cnt')
      t.textContent = w ? `${n}/${w}` : n; t.classList.toggle('full', !!w && n >= w)
    })
    const colAt = (x, y) => {
      const cols = $$(el, '.col'); let best = null, bd = 1e9
      cols.forEach((c) => { const r = c.getBoundingClientRect(); const dx = x < r.left ? r.left - x : x > r.right ? x - r.right : 0; if (dx < bd) { bd = dx; best = c } })
      return best
    }
    board.addEventListener('pointerdown', (e) => {
      const card = e.target.closest('.kc'); if (!card || card.classList.contains('ghost') || e.button > 0) return
      if (e.pointerType !== 'mouse' && !e.target.closest('.grip')) return
      const r = card.getBoundingClientRect()
      d = { card, id: e.pointerId, sx: e.clientX, sy: e.clientY, ox: e.clientX - r.left, oy: e.clientY - r.top, w: r.width, h: r.height, on: false, from: card.closest('.col') }
      try { card.setPointerCapture(e.pointerId) } catch (x) { /* 忽略 */ }
    })
    board.addEventListener('pointermove', (e) => {
      if (!d || e.pointerId !== d.id) return
      if (!d.on) {
        if (Math.hypot(e.clientX - d.sx, e.clientY - d.sy) < 5) return
        d.on = true; const g = d.card.cloneNode(true); g.classList.add('ghost'); g.style.width = d.w + 'px'; el.appendChild(g); d.ghost = g
        const s = document.createElement('div'); s.className = 'slot'; s.style.height = d.h + 'px'; d.card.after(s); d.slot = s; d.card.style.display = 'none'
      }
      const rr = el.getBoundingClientRect(); d.ghost.style.left = e.clientX - d.ox - rr.left + 'px'; d.ghost.style.top = e.clientY - d.oy - rr.top + 'px'
      const br = board.getBoundingClientRect(); if (e.clientX < br.left + 40) board.scrollLeft -= 14; else if (e.clientX > br.right - 40) board.scrollLeft += 14
      const col = colAt(e.clientX, e.clientY); $$(el, '.col').forEach((c) => c.classList.toggle('hot', c === col))
      const lst = $(col, '.lst'), others = $$(lst, ':scope > .kc').filter((c) => c.style.display !== 'none' && !c.classList.contains('ghost'))
      const before = others.find((c) => { const q = c.getBoundingClientRect(); return e.clientY < q.top + q.height / 2 })
      if (before) { if (d.slot.nextSibling !== before) lst.insertBefore(d.slot, before) } else if (lst.lastElementChild !== d.slot) lst.appendChild(d.slot)
    })
    const end = (e, cancel) => {
      if (!d || e.pointerId !== d.id) return
      const { card, slot, ghost, from } = d; d = null
      if (!slot) return
      ghost.remove(); $$(el, '.col').forEach((c) => c.classList.remove('hot'))
      const to = slot.closest('.col'), w = +to.dataset.wip || 0, moving = to !== from
      const n = $$(to, '.lst > .kc').filter((c) => c.style.display !== 'none').length
      if (cancel || (w && moving && n >= w)) { slot.remove(); card.style.display = ''; if (!cancel) toast(root, `「${$(to, 'b').textContent}」已达在制上限 ${w} 张，先完成一些再拖入`) }
      else { slot.replaceWith(card); card.style.display = ''; card.classList.remove('flash'); void card.offsetWidth; card.classList.add('flash'); if (moving) toast(root, `已移到「${$(to, 'b').textContent}」`) }
      refresh()
    }
    board.addEventListener('pointerup', (e) => end(e, false))
    board.addEventListener('pointercancel', (e) => end(e, true))
    /* 添加卡片：列头 + 号，回车确认，Esc 取消 */
    el.addEventListener('click', (e) => {
      const add = e.target.closest('.plus'); if (!add) return
      const lst = $(add.closest('.col'), '.lst'); if ($(lst, '.nw')) { $(lst, '.nw input').focus(); return }
      const w = document.createElement('div'); w.className = 'nw'; w.innerHTML = '<input class="z-in" placeholder="输入标题，回车添加" maxlength="60" aria-label="新卡片标题">'; lst.prepend(w)
      const inp = $(w, 'input'); inp.focus()
      let closed = false
      const done = (ok) => {
        if (closed) return; closed = true
        const v = inp.value.trim(); w.remove()
        if (ok && v) { lst.insertAdjacentHTML('afterbegin', kbCard([v, '功能', '中', '', $$(el, '.kc').length % 12])); const c = $(lst, '.kc'); c.classList.add('flash'); refresh(); toast(root, '已添加') }
      }
      inp.addEventListener('keydown', (k) => { if (k.key === 'Enter') done(true); else if (k.key === 'Escape') done(false) })
      inp.addEventListener('blur', () => done(true))
    })
    $(el, '.sq input').addEventListener('input', (e) => {
      const q = e.target.value.trim().toLowerCase()
      $$(el, '.kc:not(.ghost)').forEach((c) => { c.classList.toggle('mutedby', q !== '' && !c.dataset.t.toLowerCase().includes(q)) })
    })
  },
})

/* ---- AD-FLOW-003 状态流转图（订单 / 工单状态机）---- */
const SM_N = { A: ['待付款', 12, 40], B: ['待发货', 192, 40], C: ['配送中', 372, 40], D: ['已完成', 552, 40], E: ['已取消', 12, 170], F: ['退款中', 372, 170], G: ['已退款', 552, 170] }
const SM_END = { D: 'fin', E: 'neg', G: 'neg' }
const SM_DESC = { A: '买家已下单，30 分钟内未付款会自动关闭。', B: '已收款，等待仓库打包发货。', C: '快递已揽收，运输途中。', D: '买家已确认收货，订单结束。', E: '订单已关闭，库存已释放。', F: '买家申请了退款，等待客服审核。', G: '款项已原路退回，订单结束。' }
const SM_E = [
  ['A', 'B', '确认收款', 'M112 62H190', 151, 52, 'm'],
  ['B', 'C', '发货', 'M292 62H370', 331, 52, 'm'],
  ['C', 'D', '确认送达', 'M472 62H550', 511, 52, 'm'],
  ['A', 'E', '取消订单', 'M62 84V166', 72, 130, 's', '取消后库存会释放，买家会收到通知，此操作不能撤销。'],
  ['B', 'F', '申请退款', 'M242 84V192H370', 306, 184, 'm', '订单将进入退款流程，需要客服审核后才能退款。'],
  ['C', 'F', '拒收退款', 'M422 84V166', 432, 130, 's', '按拒收处理，退款成功后商品将退回仓库。'],
  ['F', 'G', '同意退款', 'M472 192H550', 511, 184, 'm', '款项将原路退回买家，涉及资金，确认后不能撤销。'],
]
const smSvg = (cur, vis, taken) => {
  const mk = (id, c) => `<marker id="adflow003-${id}" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="7" markerHeight="7" orient="auto"><path d="M1.5 1.5 8 5 1.5 8.5" style="fill:none;stroke:${c};stroke-width:1.6;stroke-linecap:round;stroke-linejoin:round"/></marker>`
  const edges = SM_E.map((e) => {
    const next = e[0] === cur, cls = taken.has(e[0] + e[1]) ? 'taken' : next ? 'next' : ''
    return `<g class="ed ${cls}${e[7] ? ' neg' : ''}"${next ? ` data-to="${e[1]}" role="button" tabindex="0" aria-label="${e[2]}"` : ''}><path class="hit" d="${e[3]}"/><path class="ln" d="${e[3]}"/><text x="${e[4]}" y="${e[5]}" ${e[6] === 's' ? 'text-anchor="start"' : ''}>${e[2]}</text></g>`
  }).join('')
  const nodes = Object.entries(SM_N).map(([k, [t, x, y]]) => `<g class="sn${k === cur ? ' cur ' + (SM_END[k] || '') : vis.has(k) ? ' vis' : ''}"><rect x="${x}" y="${y}" width="100" height="44" rx="8"/><text x="${x + 50}" y="${y + 22}">${t}</text></g>`).join('')
  return `<svg viewBox="0 0 664 236" width="664" height="236" role="img" aria-label="订单状态流转图，当前状态${SM_N[cur][0]}"><defs>${mk('g', '#9AA1AB')}${mk('o', 'var(--ok)')}${mk('p', 'var(--p)')}</defs>${edges}${nodes}</svg>`
}
const smSide = (cur, log) => {
  const outs = SM_E.filter((e) => e[0] === cur), end = !outs.length
  return `<div class="now"><span class="k">当前状态</span><div class="nb"><b>${SM_N[cur][0]}</b>${tag(end ? '终态' : '进行中', (end ? (SM_END[cur] === 'fin' ? 'ok' : 'dg') : 'in') + ' dot')}</div><p>${SM_DESC[cur]}</p></div><div class="ops"><span class="k">可执行的流转</span>${end ? '<p class="none">已是终态，不能再流转。</p><button class="z-btn" type="button" data-act="reset">' + ic('bz_undo') + '重置演示</button>' : `<div class="bs">${outs.map((e) => `<button type="button" class="z-btn${e[7] ? ' d' : ' p'}" data-to="${e[1]}">${e[2]}<span class="to">→ ${SM_N[e[1]][0]}</span></button>`).join('')}</div>`}</div><div class="lg"><span class="k">流转记录</span><ol>${log.map((l) => `<li><span class="tm">${l[0]}</span><span>${l[1]}</span></li>`).join('')}</ol></div>`
}
def({
  id: 'AD-FLOW-003', name: '状态流转图', style: '当前高亮', wide: true,
  fit: '订单、工单、售后等有明确状态机的对象：图上高亮当前状态，只给合法的下一步，危险流转先确认，并记录流转日志',
  avoid: '状态只有 2–3 个的简单开关（用状态标签即可）；需要多人会签的流程（用审批流程图）',
  kw: '状态机 流转 订单状态 工单状态 state-machine 下一步 日志 退款 取消 确认',
  css: K('adflow003', 'btn tag modal') + `.adflow003{width:1100px;max-width:100%;background:var(--card);border:1px solid var(--line2);border-radius:12px}.adflow003 .hd{display:flex;align-items:center;justify-content:space-between;gap:12px;padding:16px 20px;border-bottom:1px solid var(--line)}.adflow003 .hd h4{font-size:16px;font-weight:600}.adflow003 .hd p{font-size:12px;color:var(--ink3);margin-top:2px}.adflow003 .body{display:grid;grid-template-columns:minmax(0,1fr) 296px;gap:20px;padding:20px}.adflow003 .map{overflow-x:auto;border-radius:8px;background:var(--sf);padding:12px 8px}.adflow003 .map svg{display:block;margin:0 auto}.adflow003 .sn rect{fill:var(--card);stroke:var(--n8);stroke-width:1.5}.adflow003 .sn text{font-size:14px;fill:var(--ink2);text-anchor:middle;dominant-baseline:central}.adflow003 .sn.vis rect{fill:var(--okb);stroke:var(--ok)}.adflow003 .sn.vis text{fill:var(--ok)}.adflow003 .sn.cur rect{fill:var(--pt);stroke:var(--p);stroke-width:2}.adflow003 .sn.cur text{fill:var(--p-text);font-weight:600}.adflow003 .sn.cur.neg rect{fill:var(--dgb);stroke:var(--dg)}.adflow003 .sn.cur.neg text{fill:var(--dg)}.adflow003 .sn.cur.fin rect{fill:var(--ok);stroke:var(--ok)}.adflow003 .sn.cur.fin text{fill:var(--card)}.adflow003 .ed .ln{fill:none;stroke:var(--n11);stroke-width:1.5;marker-end:url(#adflow003-g)}.adflow003 .ed .hit{fill:none;stroke:transparent;stroke-width:16}.adflow003 .ed text{font-size:12px;fill:var(--ink3);text-anchor:middle}.adflow003 .ed.taken .ln{stroke:var(--ok);marker-end:url(#adflow003-o)}.adflow003 .ed.taken text{fill:var(--ok)}.adflow003 .ed.next{cursor:pointer}.adflow003 .ed.next .ln{stroke:var(--p);stroke-dasharray:5 4;marker-end:url(#adflow003-p)}.adflow003 .ed.next text{fill:var(--p-text);font-weight:600}.adflow003 .ed.next.neg .ln{stroke:var(--dg);marker-end:url(#adflow003-g)}.adflow003 .ed.next.neg text{fill:var(--dg)}.adflow003 .ed:focus{outline:none}.adflow003 .side{display:flex;flex-direction:column;gap:16px;min-width:0}.adflow003 .k{display:block;font-size:12px;color:var(--ink3);margin-bottom:6px}.adflow003 .nb{display:flex;align-items:center;gap:8px}.adflow003 .nb b{font-size:16px;font-weight:600}.adflow003 .now p{margin-top:4px;color:var(--ink2)}.adflow003 .bs{display:flex;flex-direction:column;gap:8px}.adflow003 .bs .z-btn{justify-content:space-between}.adflow003 .bs .to{font-size:12px;opacity:var(--dim80)}.adflow003 .none{color:var(--ink2);margin-bottom:8px}.adflow003 .lg ol{display:flex;flex-direction:column;gap:6px;max-height:132px;overflow-y:auto;padding-right:4px}.adflow003 .lg li{display:flex;gap:10px;font-size:12px;color:var(--ink2);line-height:1.5}.adflow003 .lg .tm{flex:none;width:56px;color:var(--ink3)}@media(max-width:820px){.adflow003 .body{grid-template-columns:minmax(0,1fr)}}`,
  html: () => `<div class="adflow003"><div class="hd"><div><h4>订单 SO2026110400128 · 状态流转</h4><p>点击虚线标出的流转，或在右侧选择下一步；红色流转需要确认</p></div></div><div class="body"><div class="map">${smSvg('A', new Set(['A']), new Set())}</div><div class="side">${smSide('A', [['09:30', '创建订单，进入「待付款」']])}</div></div>${modal('cf', '确认流转', '<p class="cfm" style="line-height:1.6"></p>', '<button class="z-btn" type="button" data-close>取消</button><button class="z-btn p" type="button" data-act="cfok">确认</button>', 400)}</div>`,
  js: (root) => {
    const el = $(root, '.adflow003'); let cur = 'A', vis = new Set(['A']), taken = new Set(), log = [['09:30', '创建订单，进入「待付款」']], pend = null
    const draw = () => { $(el, '.map').innerHTML = smSvg(cur, vis, taken); $(el, '.side').innerHTML = smSide(cur, log) }
    const go = (e) => { taken.add(e[0] + e[1]); vis.add(e[1]); log.unshift(['刚刚', `${SM_N[e[0]][0]} → ${SM_N[e[1]][0]}（${e[2]}）`]); cur = e[1]; draw(); toast(root, `已流转到「${SM_N[cur][0]}」`) }
    const pick = (to) => { const e = SM_E.find((x) => x[0] === cur && x[1] === to); if (!e) return; if (e[7]) { pend = e; $(root, '.cfm').textContent = `「${e[2]}」：${e[7]}`; openOv(root, 'cf') } else go(e) }
    root.addEventListener('click', (e) => {
      const t = e.target.closest('[data-to]'); if (t) { pick(t.dataset.to); return }
      const a = e.target.closest('[data-act]'); if (!a) return
      if (a.dataset.act === 'cfok' && pend) { closeOv(a); go(pend); pend = null }
      if (a.dataset.act === 'reset') { cur = 'A'; vis = new Set(['A']); taken = new Set(); log = [['09:30', '创建订单，进入「待付款」']]; draw(); toast(root, '已重置') }
    })
    root.addEventListener('keydown', (e) => { const g = e.target.closest && e.target.closest('.ed.next'); if (g && (e.key === 'Enter' || e.key === ' ')) { e.preventDefault(); pick(g.dataset.to) } })
    wireEsc(root)
  },
})

/* ---- AD-FLOW-004 工单时间线 ---- */
const TK_TONE = { 处理中: 'in', 待客户回复: 'wn', 已解决: 'ok', 已关闭: '' }
const TK_ICON = { cust: 'user', reply: 'chat', note: 'bz_note', sys: 'bolt', status: 'refresh' }
const TK_EV = () => [
  { ty: 'cust', i: 0, who: '林小满', role: '客户', at: '11-03 09:20', tx: '订单 SO2026110400128 无法开具发票，页面提示“金额超出单张发票上限”，请帮忙处理。' },
  { ty: 'sys', at: '11-03 09:21', tx: '系统自动分配给 陈晓雨（客服二组）' },
  { ty: 'reply', i: 1, who: '陈晓雨', role: '客服', at: '11-03 10:15', tx: '您好，这笔订单金额超过了单张发票的上限，我们可以拆分成两张开具，预计今天内完成，请问是否同意？' },
  { ty: 'note', i: 1, who: '陈晓雨', role: '内部备注', at: '11-03 10:30', tx: '已和财务确认可以拆分，拆成 ¥9,800 与 ¥2,350 两张，需要财务在系统里手动开具。' },
  { ty: 'cust', i: 0, who: '林小满', role: '客户', at: '11-04 08:50', tx: '同意拆分，今天下午要用，麻烦尽快。' },
  { ty: 'status', at: '11-04 08:52', tx: '状态由「待客户回复」变更为「处理中」' },
]
const tkEv = (v) => v.ty === 'sys' || v.ty === 'status'
  ? `<li class="ev line"><span class="dc">${ic(TK_ICON[v.ty], 's')}</span><p><span>${v.tx}</span><time>${v.at}</time></p></li>`
  : `<li class="ev ${v.ty}"><span class="dc">${ic(TK_ICON[v.ty], 's')}</span><div class="bx"><div class="mh">${critter(v.i, 24)}<b>${v.who}</b>${tag(v.role, v.ty === 'reply' ? 'in' : v.ty === 'note' ? 'wn' : '')}<time>${v.at}</time></div><p>${esc(v.tx).replace(/\n/g, '<br>')}</p></div></li>`
def({
  id: 'AD-FLOW-004', name: '工单时间线', style: '评论追加', wide: true,
  fit: '客服工单、售后单、线索跟进：按时间展示客户来信、客服回复、内部备注与状态变更，底部直接回复并可同时改状态',
  avoid: '需要结构化审批节点的流程（用审批流程图）；对话上千条的即时聊天（用专门的会话组件）',
  kw: '工单 时间线 timeline 评论 回复 内部备注 客服 售后 跟进记录 状态变更',
  css: K('adflow004', 'btn tag modal in dd seg') + `.adflow004{width:1100px;max-width:100%;background:var(--card);border:1px solid var(--line2);border-radius:12px}.adflow004 .hd{display:flex;align-items:center;justify-content:space-between;flex-wrap:wrap;gap:10px 16px;padding:16px 20px;border-bottom:1px solid var(--line)}.adflow004 .hd .l{display:flex;align-items:center;flex-wrap:wrap;gap:10px}.adflow004 .hd h4{font-size:16px;font-weight:600}.adflow004 .hd .no{font-size:12px;color:var(--ink3)}.adflow004 .body{display:grid;grid-template-columns:minmax(0,1fr) 264px}.adflow004 .main{min-width:0;display:flex;flex-direction:column}.adflow004 .evs{padding:20px 20px 4px;max-height:440px;overflow-y:auto}.adflow004 .ev{position:relative;display:flex;gap:12px;padding-bottom:16px}.adflow004 .ev:not(:last-child)::before{content:"";position:absolute;left:11px;top:26px;bottom:2px;width:2px;background:var(--n5)}.adflow004 .dc{flex:none;display:flex;align-items:center;justify-content:center;width:24px;height:24px;border-radius:50%;background:var(--mub);color:var(--ink2)}.adflow004 .ev.cust .dc{background:var(--n4)}.adflow004 .ev.reply .dc{background:var(--pt);color:var(--p-text)}.adflow004 .ev.note .dc{background:var(--wnb);color:var(--wn)}.adflow004 .bx{flex:1;min-width:0;padding:10px 14px;border:1px solid var(--line2);border-radius:8px;background:var(--card)}.adflow004 .ev.reply .bx{background:var(--pt);border-color:var(--pm)}.adflow004 .ev.note .bx{background:var(--wnb);border:1px dashed #D9BE86}.adflow004 .bx .mh{display:flex;align-items:center;gap:8px;margin-bottom:6px}.adflow004 .bx .mh b{font-weight:600}.adflow004 time{font-size:12px;color:var(--ink3);margin-left:auto}.adflow004 .bx p{line-height:1.6;overflow-wrap:anywhere}.adflow004 .ev.line{align-items:center}.adflow004 .ev.line p{display:flex;flex:1;gap:12px;color:var(--ink2);font-size:12px}.adflow004 .ev.new{animation:zbin .3s cubic-bezier(.2,0,0,1)}.adflow004 .cmp{margin:0 20px 20px;padding:12px;border:1px solid var(--bd);border-radius:12px;background:var(--card);transition:border-color .15s}.adflow004 .cmp:focus-within{border-color:var(--ink2)}.adflow004 .cmp.note{background:var(--wnb);border-color:#D9BE86}.adflow004 .cmp .top{display:flex;align-items:center;justify-content:space-between;gap:8px;margin-bottom:8px}.adflow004 .cmp .top span{font-size:12px;color:var(--ink3)}.adflow004 .cmp textarea{border:0;padding:4px 2px;background:none;border-radius:0}.adflow004 .cmp .cbar{display:flex;align-items:center;justify-content:space-between;flex-wrap:wrap;gap:8px;margin-top:8px}.adflow004 .cmp .cbar .r{display:flex;align-items:center;gap:12px}.adflow004 .cmp .cbar .sb{display:flex;align-items:center;gap:8px;font-size:12px;color:var(--ink3)}.adflow004 .cmp .cnt{font-size:12px;color:var(--ink3);font-variant-numeric:tabular-nums}.adflow004 .shut{margin:0 20px 20px;padding:14px 16px;border-radius:8px;background:var(--sf);display:flex;align-items:center;justify-content:space-between;gap:12px;color:var(--ink2)}.adflow004 .side{padding:20px;border-left:1px solid var(--line);background:var(--sf);border-radius:0 0 12px 0}.adflow004 .side h4{font-size:14px;font-weight:600;margin-bottom:12px}.adflow004 .side dl{display:flex;flex-direction:column;gap:12px}.adflow004 .side dt{font-size:12px;color:var(--ink3)}.adflow004 .side dd{margin-top:2px;display:flex;align-items:center;gap:8px;flex-wrap:wrap}@media(max-width:820px){.adflow004 .body{grid-template-columns:minmax(0,1fr)}.adflow004 .side{border-left:0;border-top:1px solid var(--line);border-radius:0 0 12px 12px}}`,
  html: () => `<div class="adflow004"><div class="hd"><div class="l"><h4>发票开具异常</h4>${tag('处理中', 'in dot')}${tag('高优先级', 'wn')}<span class="no">TK-20261103-088</span></div><button type="button" class="z-btn d" data-open="cl">关闭工单</button></div><div class="body"><div class="main"><ol class="evs">${TK_EV().map(tkEv).join('')}</ol><div class="cmp"><div class="top">${seg([['reply', '回复客户'], ['note', '内部备注']], 'reply')}<span class="nt">客户会收到短信与站内通知</span></div><textarea class="z-in" rows="3" maxlength="500" placeholder="输入回复内容，Ctrl + Enter 发送" aria-label="回复内容"></textarea><div class="cbar"><div class="sb"><span>发送后设为</span>${dd(['处理中', '待客户回复', '已解决'], '处理中', { up: true })}</div><div class="r"><span class="cnt">0/500</span><button type="button" class="z-btn p l" data-act="send" disabled title="先输入内容">${ic('bz_send')}发送</button></div></div></div></div><aside class="side"><h4>工单信息</h4><dl><div><dt>客户</dt><dd>${critter(0, 24)}林小满${tag('金卡会员', 'in')}</dd></div><div><dt>关联订单</dt><dd>SO2026110400128 · ¥12,150</dd></div><div><dt>来源渠道</dt><dd>小程序 · 在线客服</dd></div><div><dt>处理人</dt><dd>${critter(1, 24)}陈晓雨 · 客服二组</dd></div><div><dt>响应时限</dt><dd>剩余 3 小时 12 分</dd></div></dl></aside></div>${modal('cl', '关闭工单', '<p style="line-height:1.6">关闭后客户将无法继续回复，可随时重新打开。确认关闭这张工单？</p>', '<button class="z-btn" type="button" data-close>取消</button><button class="z-btn p" type="button" data-act="clok">确认关闭</button>', 400)}</div>`,
  js: (root) => {
    const el = $(root, '.adflow004'), list = $(el, '.evs'), ta = $(el, 'textarea'), send = $(el, '[data-act=send]'), cmp = $(el, '.cmp'); let status = '处理中', mode = 'reply'
    const setStatus = (s) => { const t = $(el, '.hd .z-tag'); t.className = 'z-tag dot ' + TK_TONE[s]; t.textContent = s; status = s }
    const push = (v) => { list.insertAdjacentHTML('beforeend', tkEv(v).replace('class="ev ', 'class="ev new ')); list.scrollTop = list.scrollHeight }
    const sync = () => { send.disabled = !ta.value.trim(); send.title = send.disabled ? '先输入内容' : ''; $(el, '.cnt').textContent = ta.value.length + '/500' }
    list.scrollTop = list.scrollHeight
    ta.addEventListener('input', sync)
    ta.addEventListener('keydown', (e) => { if (e.key === 'Enter' && (e.ctrlKey || e.metaKey) && !send.disabled) send.click() })
    root.addEventListener('click', (e) => {
      const t = e.target.closest('[data-t]')
      if (t && t.closest('.z-seg')) {
        mode = t.dataset.t; cmp.classList.toggle('note', mode === 'note'); $(el, '.nt').textContent = mode === 'note' ? '仅客服可见，客户看不到' : '客户会收到短信与站内通知'
        ta.placeholder = mode === 'note' ? '写给同事看的备注，客户看不到' : '输入回复内容，Ctrl + Enter 发送'; $(el, '.cmp .sb').style.visibility = mode === 'note' ? 'hidden' : ''; return
      }
      const a = e.target.closest('[data-act]'); if (!a) return
      if (a.dataset.act === 'send') {
        const txt = ta.value.trim(); if (!txt) return
        push({ ty: mode, i: 1, who: '陈晓雨', role: mode === 'note' ? '内部备注' : '客服', at: '刚刚', tx: txt })
        const want = $(el, '.cmp [data-label]').textContent
        if (mode === 'reply' && want !== status) { push({ ty: 'status', at: '刚刚', tx: `状态由「${status}」变更为「${want}」` }); setStatus(want) }
        ta.value = ''; sync(); toast(root, mode === 'note' ? '备注已保存' : '回复已发送')
      }
      if (a.dataset.act === 'clok') {
        closeOv(a); push({ ty: 'status', at: '刚刚', tx: `状态由「${status}」变更为「已关闭」` }); setStatus('已关闭'); cmp.hidden = true; $(el, '[data-open=cl]').hidden = true
        const s = document.createElement('div'); s.className = 'shut'; s.innerHTML = '<span>工单已关闭，客户不能再回复。</span><button type="button" class="z-btn" data-act="reopen">重新打开</button>'; cmp.after(s)
      }
      if (a.dataset.act === 'reopen') { $(el, '.shut').remove(); cmp.hidden = false; $(el, '[data-open=cl]').hidden = false; push({ ty: 'status', at: '刚刚', tx: '状态由「已关闭」变更为「处理中」' }); setStatus('处理中'); toast(root, '已重新打开') }
    })
    wireEsc(root)
  },
})

/* ---- AD-FLOW-005 日程周视图 ---- */
const CAL_TY = { 会议: 'in', 拜访: 'ok', 培训: 'wn', 其他: '' }
const CAL_H0 = 8, CAL_H1 = 20, CAL_RH = 44
const WK = ['周一', '周二', '周三', '周四', '周五', '周六', '周日']
const ymd = (d) => `${d.getFullYear()}-${pad(d.getMonth() + 1)}-${pad(d.getDate())}`
const hhmm = (m) => `${pad(Math.floor(m / 60))}:${pad(m % 60)}`
const CAL_EV = () => [
  { id: 1, d: '2026-11-02', s: 540, m: 60, t: '运营周会', ty: '会议', who: [0, 1, 3] },
  { id: 2, d: '2026-11-02', s: 840, m: 90, t: '供应商拜访 · 华东仓', ty: '拜访', who: [4, 8] },
  { id: 3, d: '2026-11-03', s: 600, m: 90, t: '新品评审', ty: '会议', who: [2, 5, 7] },
  { id: 4, d: '2026-11-03', s: 630, m: 30, t: '面试 · 客服岗', ty: '其他', who: [6] },
  { id: 5, d: '2026-11-04', s: 570, m: 60, t: '门店店长培训', ty: '培训', who: [1, 9, 10] },
  { id: 6, d: '2026-11-04', s: 840, m: 60, t: '活动复盘', ty: '会议', who: [0, 2, 4] },
  { id: 7, d: '2026-11-05', s: 660, m: 60, t: '财务月结对账', ty: '其他', who: [3, 4] },
  { id: 8, d: '2026-11-05', s: 900, m: 120, t: '双十一预热方案讨论（含渠道与客服排期）', ty: '会议', who: [0, 5, 7, 11] },
  { id: 9, d: '2026-11-06', s: 600, m: 60, t: '客户回访', ty: '拜访', who: [8] },
  { id: 10, d: '2026-11-07', s: 600, m: 120, t: '门店盘点', ty: '其他', who: [9, 10, 11] },
]
const lanes = (evs) => {
  const out = []; let cl = [], end = 0
  const flush = () => { const n = Math.max(...cl.map((e) => e.lane)) + 1; cl.forEach((e) => out.push({ ...e, n })); cl = [] }
  ;[...evs].sort((a, b) => a.s - b.s).forEach((e) => {
    if (cl.length && e.s >= end) { flush(); end = 0 }
    const used = cl.filter((x) => x.s + x.m > e.s).map((x) => x.lane); let l = 0; while (used.includes(l)) l++
    cl.push({ ...e, lane: l }); end = Math.max(end, e.s + e.m)
  })
  if (cl.length) flush()
  return out
}
const NOW = { d: '2026-11-04', m: 14 * 60 + 20 }
const calRange = (ws) => { const e = new Date(ws); e.setDate(e.getDate() + 6); return ws.getMonth() === e.getMonth() ? `${ws.getFullYear()} 年 ${ws.getMonth() + 1} 月 ${ws.getDate()} 日 – ${e.getDate()} 日` : `${ws.getFullYear()} 年 ${ws.getMonth() + 1} 月 ${ws.getDate()} 日 – ${e.getMonth() + 1} 月 ${e.getDate()} 日` }
const calGrid = (ws, evs) => {
  const days = Array.from({ length: 7 }, (_, i) => { const d = new Date(ws); d.setDate(d.getDate() + i); return d })
  const head = '<div class="gh t"></div>' + days.map((d, i) => `<div class="gh${ymd(d) === NOW.d ? ' today' : ''}"><span>${WK[i]}</span><b>${d.getDate()}</b></div>`).join('')
  const times = `<div class="tcol">${Array.from({ length: CAL_H1 - CAL_H0 }, (_, i) => `<span>${pad(CAL_H0 + i)}:00</span>`).join('')}</div>`
  const cols = days.map((d) => {
    const k = ymd(d), list = lanes(evs.filter((e) => e.d === k))
    return `<div class="dc${k === NOW.d ? ' today' : ''}" data-d="${k}">${list.map((e) => `<button type="button" class="evb${e.m <= 30 ? ' sh' : ''} ${CAL_TY[e.ty] || 'mu'}" data-id="${e.id}" style="top:${((e.s - CAL_H0 * 60) / 60) * CAL_RH + 1}px;height:${(e.m / 60) * CAL_RH - 2}px;left:calc(${(e.lane / e.n) * 100}% + 2px);width:calc(${100 / e.n}% - 4px)" title="${esc(e.t)} ${hhmm(e.s)}–${hhmm(e.s + e.m)}"><b>${esc(e.t)}</b><span>${hhmm(e.s)}–${hhmm(e.s + e.m)}</span></button>`).join('')}${k === NOW.d ? `<i class="now" style="top:${((NOW.m - CAL_H0 * 60) / 60) * CAL_RH}px"></i>` : ''}<i class="hv" hidden>${ic('plus', 's')}新建日程</i></div>`
  }).join('')
  return { head, body: times + cols }
}
const selTime = (cur) => `<select class="z-in stt" aria-label="开始时间">${Array.from({ length: (CAL_H1 - CAL_H0) * 2 }, (_, i) => { const m = CAL_H0 * 60 + i * 30; return `<option value="${m}"${m === cur ? ' selected' : ''}>${hhmm(m)}</option>` }).join('')}</select>`
const selDur = `<select class="z-in dur" aria-label="时长">${[[30, '30 分钟'], [60, '1 小时'], [90, '1.5 小时'], [120, '2 小时'], [180, '3 小时']].map(([v, t]) => `<option value="${v}"${v === 60 ? ' selected' : ''}>${t}</option>`).join('')}</select>`
def({
  id: 'AD-FLOW-005', name: '日程周视图', style: '点格新增', wide: true,
  fit: '会议室、拜访、培训、排期类的周日程：点空白格直接新建，点日程块看详情与删除，同一时段的日程自动并排',
  avoid: '按人 × 天排班（用员工排班表）；只看月度总览时（改用月历 + 角标）',
  kw: '日程 日历 周视图 calendar week 会议 排期 点格新增 时间轴 schedule',
  css: K('adflow005', 'btn tag modal in') + `.adflow005{width:1100px;max-width:100%;background:var(--card);border:1px solid var(--line2);border-radius:12px}.adflow005 .tb{display:flex;align-items:center;justify-content:space-between;flex-wrap:wrap;gap:10px 16px;padding:12px 16px;border-bottom:1px solid var(--line)}.adflow005 .tb .l{display:flex;align-items:center;gap:8px}.adflow005 .tb .rng{min-width:176px;text-align:center;font-weight:600}.adflow005 .tb .lg{display:flex;align-items:center;gap:14px;font-size:12px;color:var(--ink2)}.adflow005 .lg span{display:inline-flex;align-items:center;gap:6px}.adflow005 .lg i{width:10px;height:10px;border-radius:3px}.adflow005 .lg i.in{background:var(--p)}.adflow005 .lg i.ok{background:var(--ok-fill)}.adflow005 .lg i.wn{background:#B58A2E}.adflow005 .lg i.mu{background:var(--n12)}.adflow005 .wrapc{overflow-x:auto}.adflow005 .cal{min-width:860px}.adflow005 .gr{display:grid;grid-template-columns:56px repeat(7,minmax(0,1fr))}.adflow005 .gh{display:flex;flex-direction:column;align-items:center;gap:2px;padding:8px 0;border-bottom:1px solid var(--line);border-left:1px solid var(--line);color:var(--ink2);font-size:12px}.adflow005 .gh.t{border-left:0}.adflow005 .gh b{display:flex;align-items:center;justify-content:center;min-width:28px;height:28px;border-radius:14px;font-size:16px;font-weight:600;color:var(--ink)}.adflow005 .gh.today b{background:var(--p);color:#fff}.adflow005 .gh.today span{color:var(--p-text);font-weight:600}.adflow005 .gb{display:grid;grid-template-columns:56px repeat(7,minmax(0,1fr))}.adflow005 .tcol{display:flex;flex-direction:column}.adflow005 .tcol span{height:${CAL_RH}px;padding-right:8px;text-align:right;font-size:12px;color:var(--ink3);transform:translateY(-8px)}.adflow005 .dc{position:relative;height:${(CAL_H1 - CAL_H0) * CAL_RH}px;border-left:1px solid var(--line);background:repeating-linear-gradient(to bottom,transparent 0,transparent ${CAL_RH - 1}px,var(--n4) ${CAL_RH - 1}px,var(--n4) ${CAL_RH}px);cursor:cell}.adflow005 .dc.today{background-color:var(--n1)}.adflow005 .evb{position:absolute;z-index:2;display:flex;flex-direction:column;align-items:flex-start;gap:1px;overflow:hidden;padding:4px 8px;border-radius:4px;border-left:3px solid var(--p);background:var(--pt);color:var(--p-text);text-align:left;font-size:12px;line-height:1.4;cursor:pointer;transition:box-shadow .15s}.adflow005 .evb:hover{box-shadow:0 2px 8px var(--sh16)}.adflow005 .evb b{font-weight:600;max-width:100%;overflow:hidden;text-overflow:ellipsis;white-space:nowrap}.adflow005 .evb span{opacity:.85;white-space:nowrap}.adflow005 .evb.sh{flex-direction:row;align-items:center;gap:6px;padding:0 6px}.adflow005 .evb.ok{border-color:var(--ok);background:var(--okb);color:var(--ok)}.adflow005 .evb.wn{border-color:#B58A2E;background:var(--wnb);color:var(--wn)}.adflow005 .evb.mu{border-color:var(--n12);background:var(--mub);color:color-mix(in srgb,var(--ink2) 43%,var(--ink1))}.adflow005 .now{position:absolute;z-index:3;left:0;right:0;height:0;border-top:2px solid var(--dg);pointer-events:none}.adflow005 .now::before{content:"";position:absolute;left:-5px;top:-6px;width:8px;height:8px;border-radius:50%;background:var(--danger-fill)}.adflow005 .hv{position:absolute;z-index:1;left:2px;right:2px;height:${CAL_RH / 2 - 2}px;display:flex;align-items:center;justify-content:center;gap:4px;border-radius:4px;background:var(--pt);color:var(--p-text);font-size:12px;pointer-events:none}.adflow005 .fm{display:flex;flex-direction:column;gap:14px}.adflow005 .fm .z-lb{display:block;margin-bottom:6px}.adflow005 .fm .r2{display:grid;grid-template-columns:1fr 1fr;gap:12px}.adflow005 .chips{display:flex;flex-wrap:wrap;gap:8px}.adflow005 .chips [data-o]{display:inline-flex;align-items:center;height:32px;padding:0 14px;border:1px solid var(--bd);border-radius:8px;cursor:pointer;transition:border-color .15s,background-color .15s}.adflow005 .chips [data-o]:hover{border-color:var(--ink3)}.adflow005 .chips [data-o].on{border-color:var(--p);background:var(--pt);color:var(--p-text)}.adflow005 .fm .dtp{color:var(--ink2);font-size:12px}.adflow005 .vw{display:flex;flex-direction:column;gap:12px}.adflow005 .vw h4{font-size:16px;font-weight:600;overflow-wrap:anywhere}.adflow005 .vw .row{display:flex;align-items:center;gap:10px;color:var(--ink2)}.adflow005 .vw .avs{display:flex}.adflow005 .vw .avs .av{margin-right:-6px;box-shadow:0 0 0 2px var(--card)}`,
  html: () => { const ws = new Date(2026, 10, 2), g = calGrid(ws, CAL_EV()); return `<div class="adflow005"><div class="tb"><div class="l"><button type="button" class="z-btn" data-act="today">今天</button><button type="button" class="z-x" data-act="prev" aria-label="上一周">${ic('left')}</button><button type="button" class="z-x" data-act="next" aria-label="下一周">${ic('right')}</button><span class="rng">${calRange(ws)}</span></div><div class="lg"><span><i class="in"></i>会议</span><span><i class="ok"></i>拜访</span><span><i class="wn"></i>培训</span><span><i class="mu"></i>其他</span></div></div><div class="wrapc"><div class="cal"><div class="gr">${g.head}</div><div class="gb">${g.body}</div></div></div>${modal('nw', '新建日程', `<div class="fm"><div><label class="z-lb z-req">日程标题</label><input class="z-in tt1" maxlength="30" placeholder="例如：新品评审会"><p class="z-er" hidden>请输入日程标题</p></div><div class="r2"><div><label class="z-lb">开始时间</label>${selTime(600)}</div><div><label class="z-lb">时长</label>${selDur}</div></div><div><label class="z-lb">类型</label><div class="chips" data-ix="radio"><span data-o class="on" role="radio">会议</span><span data-o role="radio">拜访</span><span data-o role="radio">培训</span><span data-o role="radio">其他</span></div></div><p class="dtp"></p></div>`, '<button class="z-btn" type="button" data-close>取消</button><button class="z-btn p" type="button" data-act="save">保存</button>', 420)}${modal('vw', '日程详情', '<div class="vw"></div>', '<button class="z-btn d" type="button" data-act="del">删除日程</button><button class="z-btn" type="button" data-close>关闭</button>', 400)}</div>` },
  js: (root) => {
    const el = $(root, '.adflow005'); let ws = new Date(2026, 10, 2), evs = CAL_EV(), uid = 100, slot = null, cur = null
    const draw = () => { const g = calGrid(ws, evs); $(el, '.gr').innerHTML = g.head; $(el, '.gb').innerHTML = g.body; $(el, '.rng').textContent = calRange(ws) }
    const hover = (e) => {
      const dc = e.target.closest('.dc'); $$(el, '.hv').forEach((h) => (h.hidden = true)); if (!dc || e.target.closest('.evb')) return
      const y = e.clientY - dc.getBoundingClientRect().top, i = Math.floor(y / (CAL_RH / 2)), h = $(dc, '.hv'); h.style.top = i * (CAL_RH / 2) + 1 + 'px'; h.hidden = false
    }
    el.addEventListener('mousemove', hover); el.addEventListener('mouseleave', () => $$(el, '.hv').forEach((h) => (h.hidden = true)))
    root.addEventListener('click', (e) => {
      const ev = e.target.closest('.evb')
      if (ev) {
        cur = evs.find((x) => x.id === +ev.dataset.id); const d = new Date(cur.d.replace(/-/g, '/'))
        $(root, '.vw').innerHTML = `<h4>${esc(cur.t)}</h4><div class="row">${ic('calendar')}${d.getMonth() + 1} 月 ${d.getDate()} 日 ${WK[(d.getDay() + 6) % 7]} · ${hhmm(cur.s)}–${hhmm(cur.s + cur.m)}</div><div class="row">${ic('tag')}${tag(cur.ty, CAL_TY[cur.ty])}</div><div class="row">${ic('users')}<span class="avs">${cur.who.map((i) => critter(i, 26)).join('')}</span>共 ${cur.who.length} 人</div>`
        openOv(root, 'vw'); return
      }
      const dc = e.target.closest('.dc')
      if (dc) {
        const y = e.clientY - dc.getBoundingClientRect().top, m = CAL_H0 * 60 + Math.floor(y / (CAL_RH / 2)) * 30, d = new Date(dc.dataset.d.replace(/-/g, '/'))
        slot = { d: dc.dataset.d }; $(root, '.stt').value = Math.min(m, (CAL_H1 - 1) * 60 + 30); $(root, '.tt1').value = ''; $(root, '.tt1').classList.remove('er'); $(root, '.z-er').hidden = true
        $(root, '.dtp').textContent = `日期：${d.getMonth() + 1} 月 ${d.getDate()} 日 ${WK[(d.getDay() + 6) % 7]}`; openOv(root, 'nw'); return
      }
      const a = e.target.closest('[data-act]'); if (!a) return
      const act = a.dataset.act
      if (act === 'prev' || act === 'next') { ws.setDate(ws.getDate() + (act === 'next' ? 7 : -7)); draw() }
      else if (act === 'today') { ws = new Date(2026, 10, 2); draw() }
      else if (act === 'save') {
        const t = $(root, '.tt1').value.trim(); if (!t) { $(root, '.tt1').classList.add('er'); $(root, '.z-er').hidden = false; $(root, '.tt1').focus(); return }
        const on = $(root, '.chips [data-o].on'); evs.push({ id: ++uid, d: slot.d, s: +$(root, '.stt').value, m: +$(root, '.dur').value, t, ty: on ? on.textContent : '会议', who: [0] }); closeOv(a); draw(); toast(root, '已添加日程')
      } else if (act === 'del' && cur) { evs = evs.filter((x) => x.id !== cur.id); closeOv(a); draw(); toast(root, `已删除「${cur.t.length > 10 ? cur.t.slice(0, 10) + '…' : cur.t}」`) }
    })
    root.addEventListener('keydown', (e) => { if (e.key === 'Enter' && e.target.matches('.tt1')) $(root, '[data-act=save]').click() })
    root.addEventListener('input', (e) => { if (e.target.matches('.tt1') && e.target.value.trim()) { e.target.classList.remove('er'); $(root, '.z-er').hidden = true } })
    wireEsc(root)
  },
})

/* ---- AD-FLOW-006 员工排班表 ---- */
const SH = { 早: ['早班', '08:00–16:00', 'in'], 晚: ['晚班', '14:00–22:00', 'wn'], 休: ['休息', '', ''] }
const ROSTER = () => [
  [0, '店长', '早早早休早早休'], [1, '收银', '晚晚休晚晚晚早'], [2, '导购', '早休早早休早早'], [3, '导购', '休早晚休晚休晚'],
  [4, '仓管', '早早休早早休休'], [5, '收银', '晚休晚休晚晚晚'], [6, '导购', '休晚晚早休早早'], [7, '导购', '早晚早休早休晚'],
].map(([i, r, s]) => ({ i, r, s: [...s] }))
const rosterBody = (rs, ws) => {
  const hrs = (r) => r.s.filter((x) => x === '早' || x === '晚').length * 8
  const cnt = (c, k) => rs.filter((r) => r.s[c] === k).length
  const rows = rs.map((r, ri) => { const h = hrs(r); return `<tr><td class="l"><span class="z-who">${critter(r.i, 28)}<span class="nm"><b>${NAMES[r.i]}</b><em>${r.r}</em></span></span></td>${r.s.map((x, c) => `<td><button type="button" class="cell${x === '' ? ' empty' : ''}" data-r="${ri}" data-c="${c}" aria-label="${NAMES[r.i]} ${WK[c]} ${x ? SH[x][0] : '未排'}">${x ? `<span class="z-tag ${SH[x][2]}">${SH[x][0]}</span>${SH[x][1] ? `<small>${SH[x][1]}</small>` : ''}` : ic('plus', 's')}</button></td>`).join('')}<td class="hr${h > 44 ? ' over' : ''}">${h} h${h > 44 ? '<em>超时</em>' : ''}</td></tr>` }).join('')
  const foot = `<tr class="ft"><td class="l">在岗人数</td>${WK.map((_, c) => { const a = cnt(c, '早'), b = cnt(c, '晚'), lack = a < 2 || b < 2; return `<td class="${lack ? 'lack' : ''}"><span>早 ${a} · 晚 ${b}</span>${lack ? `<em>${a < 2 ? '早班' : '晚班'}缺 ${2 - Math.min(a, b)} 人</em>` : ''}</td>` }).join('')}<td></td></tr>`
  return rows + foot
}
def({
  id: 'AD-FLOW-006', name: '员工排班表', style: '点格选班次', wide: true,
  fit: '门店、客服、仓库的周排班：点格子选早班 / 晚班 / 休息，底部实时统计每天在岗人数，右侧统计工时并标出超时',
  avoid: '按小时精确排的会议或预约（用日程周视图）；班次种类很多、需要拖拽批量排班时（改用专业排班系统）',
  kw: '排班 班次 排班表 roster shift 员工 工时 在岗人数 门店 schedule',
  css: K('adflow006', 'btn tag') + `.adflow006{position:relative;width:1100px;max-width:100%;background:var(--card);border:1px solid var(--line2);border-radius:12px}.adflow006 .tb{display:flex;align-items:center;justify-content:space-between;flex-wrap:wrap;gap:10px 16px;padding:12px 16px;border-bottom:1px solid var(--line)}.adflow006 .tb .l{display:flex;align-items:center;gap:8px}.adflow006 .tb .rng{min-width:176px;text-align:center;font-weight:600}.adflow006 .tb .r{display:flex;align-items:center;gap:12px}.adflow006 .tb .hnt{font-size:12px;color:var(--ink3)}.adflow006 .tw{position:relative;overflow-x:auto}.adflow006 table{width:100%;min-width:900px;border-collapse:collapse}.adflow006 th{height:56px;padding:0 6px;text-align:center;font-weight:600;color:var(--ink2);background:var(--n2);border-bottom:1px solid var(--line)}.adflow006 th small{display:block;font-size:12px;font-weight:400;color:var(--ink3)}.adflow006 th.today{color:var(--p-text);background:var(--pt)}.adflow006 td{height:56px;padding:0 6px;text-align:center;border-bottom:1px solid var(--line)}.adflow006 td.l{padding-left:16px;text-align:left}.adflow006 .nm{display:flex;flex-direction:column;line-height:1.35}.adflow006 .nm em{font-size:12px;color:var(--ink3)}.adflow006 .nm b{font-weight:600}.adflow006 .cell{display:flex;flex-direction:column;align-items:center;justify-content:center;gap:2px;width:100%;min-height:46px;border-radius:8px;border:1px solid transparent;transition:background-color .15s,border-color .15s}.adflow006 .cell:hover{background:var(--sf);border-color:var(--bd)}.adflow006 .cell small{font-size:12px;color:var(--ink3)}.adflow006 .cell.empty{color:var(--ink3);border:1px dashed var(--n8)}.adflow006 td.hr{font-variant-numeric:tabular-nums;width:92px}.adflow006 td.hr.over{color:var(--wn);font-weight:600}.adflow006 td.hr em{display:block;font-size:12px;font-weight:400}.adflow006 tr.ft td{height:52px;background:var(--n2);border-bottom:0;font-size:12px;color:var(--ink2)}.adflow006 tr.ft td.l{font-size:14px;font-weight:600}.adflow006 tr.ft td.lack{background:var(--wnb);color:var(--wn);font-weight:600}.adflow006 tr.ft td span,.adflow006 tr.ft td em{display:block}.adflow006 tr.ft td em{font-weight:400}.adflow006 .pop{position:absolute;z-index:20;width:148px;padding:4px;border:1px solid var(--n6);border-radius:8px;background:var(--card2);box-shadow:0 8px 24px var(--sh14);animation:zbin .15s cubic-bezier(.2,0,0,1)}.adflow006 .pop button{display:flex;align-items:center;gap:8px;width:100%;height:32px;padding:0 10px;border-radius:4px}.adflow006 .pop button:hover{background:var(--sf)}.adflow006 .pop button.on{background:var(--pt);color:var(--p-text)}.adflow006 .pop button.clr{color:var(--ink3)}.adflow006 .pop .z-tag{pointer-events:none}`,
  html: () => { const ws = new Date(2026, 10, 2), rs = ROSTER(); return `<div class="adflow006"><div class="tb"><div class="l"><span class="rng">${calRange(ws)}</span>${tag('已发布', 'ok dot')}</div><div class="r"><span class="hnt">点格子切换班次；早班、晚班每天各需 2 人以上</span><button type="button" class="z-btn" data-act="reset">${ic('bz_undo')}还原</button><button type="button" class="z-btn p" data-act="pub" disabled title="排班没有修改">发布排班</button></div></div><div class="tw"><table><thead><tr><th style="width:176px">员工</th>${WK.map((w, i) => { const d = new Date(ws); d.setDate(d.getDate() + i); return `<th class="${ymd(d) === NOW.d ? 'today' : ''}">${w}<small>${d.getMonth() + 1}/${pad(d.getDate())}</small></th>` }).join('')}<th>本周工时</th></tr></thead><tbody>${rosterBody(rs, ws)}</tbody></table></div></div>` },
  js: (root) => {
    const el = $(root, '.adflow006'), body = $(el, 'tbody'); let rs = ROSTER(); const ws = new Date(2026, 10, 2); let dirty = false
    const draw = () => { body.innerHTML = rosterBody(rs, ws) }
    const mark = (d) => { dirty = d; const p = $(el, '[data-act=pub]'); p.disabled = !d; p.title = d ? '' : '排班没有修改'; const t = $(el, '.tb .z-tag'); t.className = 'z-tag dot ' + (d ? 'wn' : 'ok'); t.textContent = d ? '有未发布的修改' : '已发布' }
    const closePop = () => { const p = $(el, '.pop'); if (p) p.remove() }
    root.addEventListener('click', (e) => {
      const pk = e.target.closest('.pop [data-k]')
      if (pk) { const p = pk.closest('.pop'), r = +p.dataset.r, c = +p.dataset.c; rs[r].s[c] = pk.dataset.k === '-' ? '' : pk.dataset.k; closePop(); draw(); mark(true); return }
      const cell = e.target.closest('.cell')
      if (cell) {
        const had = $(el, '.pop') && $(el, '.pop').dataset.r === cell.dataset.r && $(el, '.pop').dataset.c === cell.dataset.c; closePop(); if (had) return
        const r = +cell.dataset.r, c = +cell.dataset.c, cur = rs[r].s[c], tw = $(el, '.tw'), cb = cell.getBoundingClientRect(), tb = tw.getBoundingClientRect()
        const pop = document.createElement('div'); pop.className = 'pop'; pop.dataset.r = r; pop.dataset.c = c; pop.setAttribute('role', 'menu')
        pop.innerHTML = ['早', '晚', '休'].map((k) => `<button type="button" role="menuitem" data-k="${k}" class="${cur === k ? 'on' : ''}">${tag(SH[k][0], SH[k][2])}<small>${SH[k][1]}</small></button>`).join('') + '<button type="button" role="menuitem" class="clr" data-k="-">清空</button>'
        tw.appendChild(pop); const ph = pop.offsetHeight
        let top = cb.bottom - tb.top + tw.scrollTop + 4; if (cb.bottom + ph > tb.bottom + 40 && cb.top - tb.top - ph - 4 > 0) top = cb.top - tb.top + tw.scrollTop - ph - 4
        pop.style.top = top + 'px'; pop.style.left = Math.min(Math.max(8, cb.left - tb.left + tw.scrollLeft + cb.width / 2 - 74), tw.scrollWidth - 156) + 'px'; return
      }
      if (!e.target.closest('.pop')) closePop()
      const a = e.target.closest('[data-act]'); if (!a) return
      if (a.dataset.act === 'pub') { mark(false); toast(root, '已发布，员工会收到排班通知') }
      if (a.dataset.act === 'reset') { rs = ROSTER(); draw(); mark(false); toast(root, '已还原为已发布的排班') }
    })
    root.addEventListener('keydown', (e) => { if (e.key === 'Escape') closePop() })
  },
})

/* ---- AD-FLOW-007 任务清单 ---- */
const TD_TODAY = '11-04'
const TD = () => [
  { g: '证照与资质', open: true, ts: [['办理营业执照', 4, '11-02', 1], ['申请食品经营许可证', 2, '11-08', 0], ['消防验收备案', 4, '11-12', 0]] },
  { g: '设备与物料', open: true, ts: [['收银终端与打印机安装调试', 5, '11-03', 0], ['首批商品入库与上架', 6, '11-06', 1], ['门头与店内标识制作', 1, '11-10', 0]] },
  { g: '人员与培训', open: true, ts: [['店员招聘到岗 6 人', 0, '11-05', 0], ['岗前培训与考核', 9, '11-09', 0], ['排班与薪资规则确认', 3, '11-04', 1]] },
].map((g) => ({ ...g, ts: g.ts.map(([t, i, due, done]) => ({ t, i, due, done: !!done })) }))
const tdDue = (t) => (t.done || !t.due ? `<span class="du">${t.due || ''}</span>` : t.due < TD_TODAY ? '<span class="z-tag dg">已逾期</span><span class="du">' + t.due + '</span>' : t.due === TD_TODAY ? '<span class="z-tag wn">今天到期</span>' : `<span class="du">${t.due}</span>`)
const tdList = (gs, f) => {
  const html = gs.map((g, gi) => {
    const vis = g.ts.map((t, ti) => [t, ti]).filter(([t]) => f === 'all' || (f === 'todo' ? !t.done : t.done)), n = g.ts.filter((t) => t.done).length, st = n === g.ts.length && n ? 1 : n ? 2 : 0
    if (!vis.length) return ''
    return `<section class="gp${g.open ? ' open' : ''}" data-g="${gi}"><header>${ck(st, `data-gall="${gi}" aria-label="全选「${g.g}」"`)}<b>${g.g}</b><span class="gn">${n}/${g.ts.length}</span><button type="button" class="z-x fold" data-fold="${gi}" aria-label="${g.open ? '收起' : '展开'}">${ic('down', 's')}</button></header>${g.open ? `<ul>${vis.map(([t, ti]) => `<li class="${t.done ? 'done' : ''}" data-g="${gi}" data-t="${ti}">${ck(t.done ? 1 : 0, `data-ck aria-label="完成「${esc(t.t)}」"`)}<span class="tt">${esc(t.t)}</span>${tdDue(t)}<span class="as">${critter(t.i, 22)}</span><button type="button" class="z-x del" data-del aria-label="删除任务" title="删除">${ic('trash', 's')}</button></li>`).join('')}</ul>` : ''}<div class="addr"><button type="button" class="z-btn t" data-add="${gi}">${ic('plus', 's')}添加任务</button></div></section>`
  }).join('')
  return html || '<p class="none">没有符合条件的任务</p>'
}
def({
  id: 'AD-FLOW-007', name: '任务清单', style: '进度联动', wide: false,
  fit: '开业筹备、上线检查、交接清单等分组待办：勾选即完成，分组与整体进度实时联动，逾期与今天到期自动标出',
  avoid: '需要指派、评论、依赖关系的复杂任务（用任务看板）；上百条的清单（要加搜索和分页）',
  kw: '任务清单 待办 checklist todo 勾选 进度 分组 逾期 筹备 检查表',
  css: K('adflow007', 'btn tag ck seg') + `.adflow007{width:640px;max-width:100%;background:var(--card);border:1px solid var(--line2);border-radius:12px;overflow:hidden}.adflow007 .top{display:flex;align-items:center;gap:16px;flex-wrap:wrap;padding:16px 20px;border-bottom:1px solid var(--line)}.adflow007 .ring{position:relative;width:56px;height:56px;flex:none}.adflow007 .ring svg{width:56px;height:56px;transform:rotate(-90deg)}.adflow007 .ring circle{fill:none;stroke-width:6}.adflow007 .ring .bg{stroke:var(--n4)}.adflow007 .ring .fg{stroke:var(--p);stroke-linecap:round;transition:stroke-dashoffset .3s cubic-bezier(.2,0,0,1),stroke .2s}.adflow007 .ring.all .fg{stroke:var(--ok)}.adflow007 .ring b{position:absolute;inset:0;display:flex;align-items:center;justify-content:center;font-size:14px;font-weight:600}.adflow007 .sum{flex:1;min-width:160px}.adflow007 .sum h4{font-size:16px;font-weight:600;display:flex;align-items:center;gap:8px}.adflow007 .sum p{margin-top:2px;font-size:12px;color:var(--ink2)}.adflow007 .sum p em{font-weight:600;color:var(--ink)}.adflow007 .sum p em.dg{color:var(--dg)}.adflow007 .groups{display:flex;flex-direction:column;gap:12px;padding:16px 20px 20px}.adflow007 .gp{border:1px solid var(--line2);border-radius:8px}.adflow007 .gp>header{display:flex;align-items:center;gap:10px;height:44px;padding:0 8px 0 14px;background:var(--n2);border-radius:8px 8px 0 0}.adflow007 .gp>header b{font-weight:600}.adflow007 .gn{font-size:12px;color:var(--ink3);font-variant-numeric:tabular-nums}.adflow007 .fold{margin-left:auto;width:32px;height:32px}.adflow007 .fold .z-ic{transition:transform .2s cubic-bezier(.2,0,0,1)}.adflow007 .gp:not(.open) .fold .z-ic{transform:rotate(-90deg)}.adflow007 .gp:not(.open)>header{border-radius:8px}.adflow007 ul{display:flex;flex-direction:column}.adflow007 li{display:flex;align-items:center;gap:10px;min-height:44px;padding:6px 8px 6px 14px;border-top:1px solid var(--line)}.adflow007 li .tt{flex:1;min-width:0;overflow-wrap:anywhere}.adflow007 li.done .tt{color:var(--ink3);text-decoration:line-through}.adflow007 li .du{font-size:12px;color:var(--ink3);font-variant-numeric:tabular-nums}.adflow007 li .as{display:flex}.adflow007 li.done .as{opacity:.5}.adflow007 .del{width:32px;height:32px;opacity:0;transition:opacity .15s}.adflow007 li:hover .del,.adflow007 li:focus-within .del{opacity:1}@media(hover:none){.adflow007 .del{opacity:1}}.adflow007 .addr{border-top:1px solid var(--line);padding:4px 6px}.adflow007 .addr .z-in{height:32px}.adflow007 .addr form{display:flex;gap:8px;padding:4px 8px}.adflow007 .none{padding:24px;text-align:center;color:var(--ink3)}.adflow007 .gp.flash{animation:zbin .25s cubic-bezier(.2,0,0,1)}`,
  html: () => { const gs = TD(), all = gs.flatMap((g) => g.ts), n = all.filter((t) => t.done).length, p = Math.round((n / all.length) * 100); return `<div class="adflow007"><div class="top"><div class="ring"><svg viewBox="0 0 56 56" aria-hidden="true"><circle class="bg" cx="28" cy="28" r="24"/><circle class="fg" cx="28" cy="28" r="24" stroke-dasharray="150.8" stroke-dashoffset="${150.8 * (1 - p / 100)}"/></svg><b>${p}%</b></div><div class="sum"><h4>门店开业筹备</h4><p>已完成 <em>${n}</em> / ${all.length} 项 · 逾期 <em class="dg">1</em> 项</p></div>${seg([['all', '全部'], ['todo', '未完成'], ['done', '已完成']], 'all')}</div><div class="groups">${tdList(gs, 'all')}</div></div>` },
  js: (root) => {
    const el = $(root, '.adflow007'); let gs = TD(), f = 'all'
    const draw = () => {
      const all = gs.flatMap((g) => g.ts), n = all.filter((t) => t.done).length, p = all.length ? Math.round((n / all.length) * 100) : 0, late = all.filter((t) => !t.done && t.due && t.due < TD_TODAY).length
      $(el, '.ring .fg').style.strokeDashoffset = 150.8 * (1 - p / 100); $(el, '.ring').classList.toggle('all', p === 100 && all.length > 0); $(el, '.ring b').textContent = p + '%'
      $(el, '.sum p').innerHTML = p === 100 && all.length ? '全部任务已完成' : `已完成 <em>${n}</em> / ${all.length} 项${late ? ` · 逾期 <em class="dg">${late}</em> 项` : ''}`
      $(el, '.sum h4').innerHTML = '门店开业筹备' + (p === 100 && all.length ? tag('可以开业', 'ok dot') : '')
      $(el, '.groups').innerHTML = tdList(gs, f)
    }
    root.addEventListener('click', (e) => {
      const sg = e.target.closest('.z-seg [data-t]'); if (sg) { f = sg.dataset.t; draw(); return }
      const li = e.target.closest('li[data-t]')
      const c = e.target.closest('[data-ck]'); if (c && li) { const t = gs[+li.dataset.g].ts[+li.dataset.t]; t.done = !t.done; draw(); return }
      const ga = e.target.closest('[data-gall]'); if (ga) { const g = gs[+ga.dataset.gall], on = !g.ts.every((t) => t.done); g.ts.forEach((t) => (t.done = on)); draw(); return }
      const fo = e.target.closest('[data-fold]'); if (fo) { gs[+fo.dataset.fold].open = !gs[+fo.dataset.fold].open; draw(); return }
      const d = e.target.closest('[data-del]'); if (d && li) { const t = gs[+li.dataset.g].ts.splice(+li.dataset.t, 1)[0]; draw(); toast(root, `已删除「${t.t.length > 10 ? t.t.slice(0, 10) + '…' : t.t}」`); return }
      const ad = e.target.closest('[data-add]')
      if (ad) {
        const box = ad.closest('.addr'); box.innerHTML = '<form><input class="z-in" maxlength="40" placeholder="任务名称，回车添加" aria-label="任务名称"><button type="button" class="z-btn" data-cancel>取消</button></form>'; const inp = $(box, 'input'); inp.focus()
        const gi = +ad.dataset.add
        box.querySelector('form').addEventListener('submit', (x) => x.preventDefault())
        inp.addEventListener('keydown', (k) => { if (k.key === 'Enter') { const v = inp.value.trim(); if (v) { gs[gi].ts.push({ t: v, i: 0, due: '', done: false }); gs[gi].open = true; draw(); toast(root, '已添加') } } else if (k.key === 'Escape') draw() })
        return
      }
      if (e.target.closest('[data-cancel]')) draw()
    })
    root.addEventListener('keydown', (e) => { if ((e.key === ' ' || e.key === 'Enter') && e.target.matches('.z-ck')) { e.preventDefault(); e.target.click() } })
  },
})

/* ---- AD-FLOW-008 工作流编排 ---- */
const WF_T = { trig: ['触发器', 'bolt', 'in'], cond: ['条件判断', 'bz_branch', 'wn'], act: ['执行动作', 'play', 'ok'], delay: ['延时等待', 'bz_timer', ''] }
const WF_W = 184, WF_H = 60
const WF_NODES = () => [
  { id: 'n1', ty: 'trig', x: 16, y: 152, name: '订单支付成功', cfg: { event: '订单支付成功' } },
  { id: 'n2', ty: 'cond', x: 236, y: 152, name: '订单金额判断', cfg: { field: '订单金额', op: '≥', val: '500' } },
  { id: 'n3', ty: 'act', x: 456, y: 64, name: '发放优惠券', cfg: { kind: '发放优惠券', val: '20 元券' } },
  { id: 'n4', ty: 'delay', x: 676, y: 64, name: '等待', cfg: { n: 3, unit: '天' } },
  { id: 'n5', ty: 'act', x: 896, y: 64, name: '发送回访短信', cfg: { kind: '发送短信', val: '回访问卷' } },
  { id: 'n6', ty: 'act', x: 456, y: 240, name: '打标签', cfg: { kind: '打标签', val: '普通客户' } },
]
const WF_E = () => [['n1', 'out', 'n2'], ['n2', 'yes', 'n3'], ['n3', 'out', 'n4'], ['n4', 'out', 'n5'], ['n2', 'no', 'n6']]
const wfSub = (n) => ({ trig: () => n.cfg.event, cond: () => `${n.cfg.field} ${n.cfg.op} ${n.cfg.val || '…'}`, act: () => `${n.cfg.kind}：${n.cfg.val || '未填写'}`, delay: () => `等待 ${n.cfg.n} ${n.cfg.unit}` })[n.ty]()
const wfPort = (n, p) => ({ x: n.x + (p === 'in' ? 0 : WF_W), y: n.y + WF_H * (p === 'yes' ? 0.3 : p === 'no' ? 0.7 : 0.5) })
const wfNode = (n) => { const [lb, icn, tone] = WF_T[n.ty]; return `<div class="nod ${n.ty}" data-id="${n.id}" style="left:${n.x}px;top:${n.y}px"><span class="ic2 ${tone}">${ic(icn)}</span><span class="tx"><b>${esc(n.name)}</b><small>${esc(wfSub(n))}</small></span>${n.ty !== 'trig' ? '<i class="pt in" data-in></i>' : ''}${n.ty === 'cond' ? '<i class="pt out" data-port="yes" style="top:30%" title="拖到下一节点"></i><i class="plb" style="top:30%">是</i><i class="pt out" data-port="no" style="top:70%"></i><i class="plb" style="top:70%">否</i>' : '<i class="pt out" data-port="out" title="拖到下一节点"></i>'}</div>` }
const wfEdges = (ns, es) => es.map(([a, p, b], i) => {
  const A = ns.find((n) => n.id === a), B = ns.find((n) => n.id === b); if (!A || !B) return ''
  const s = wfPort(A, p), t = wfPort(B, 'in'), d = `M${s.x} ${s.y}C${s.x + 56} ${s.y} ${t.x - 56} ${t.y} ${t.x - 3} ${t.y}`, mx = (s.x + t.x) / 2, my = (s.y + t.y) / 2
  return `<g class="eg" data-i="${i}"><path class="hit" d="${d}"/><path class="ln" d="${d}"/><g class="cut" data-cut="${i}" transform="translate(${mx} ${my})"><circle r="9"/><path d="M-3 -3 3 3M3 -3-3 3"/></g></g>`
}).join('')
const wfProps = (n) => {
  if (!n) return '<div class="emp">' + ic('bz_branch', 'xl') + '<p>点击画布里的节点编辑属性</p><p class="sm">拖动节点调整位置；从节点右侧圆点拖出一条线到另一个节点即可连接；鼠标移到连线上可删除。</p></div>'
  const f = (l, c) => `<div class="fd"><label class="z-lb">${l}</label>${c}</div>`, sel = (k, arr) => `<select class="z-in sm" data-cfg="${k}">${arr.map((x) => `<option${x === n.cfg[k] ? ' selected' : ''}>${x}</option>`).join('')}</select>`
  let b = f('节点名称', `<input class="z-in sm" data-nm value="${esc(n.name)}" maxlength="16">`)
  if (n.ty === 'trig') b += f('触发事件', sel('event', ['订单支付成功', '会员注册成功', '库存低于预警值', '订单申请退款']))
  if (n.ty === 'cond') b += f('判断字段', sel('field', ['订单金额', '会员等级', '本月下单次数'])) + f('比较方式', sel('op', ['≥', '＜', '＝'])) + f('比较值', `<input class="z-in sm" data-cfg="val" value="${esc(n.cfg.val)}" maxlength="10">`)
  if (n.ty === 'act') b += f('动作类型', sel('kind', ['发放优惠券', '发送短信', '打标签', '发送站内信'])) + f('内容', `<input class="z-in sm" data-cfg="val" value="${esc(n.cfg.val)}" maxlength="20">`)
  if (n.ty === 'delay') b += f('等待时长', `<div class="two"><input class="z-in sm" type="number" min="1" max="999" data-cfg="n" value="${n.cfg.n}">${sel('unit', ['分钟', '小时', '天'])}</div>`)
  return `<div class="phd"><span class="ic2 ${WF_T[n.ty][2]}">${ic(WF_T[n.ty][1])}</span><b>${WF_T[n.ty][0]}</b></div>${b}<button type="button" class="z-btn d del" data-rm>${ic('trash')}删除节点</button>`
}
def({
  id: 'AD-FLOW-008', name: '工作流编排', style: '拖拽连线', wide: true,
  fit: '营销自动化、审批规则、通知流程的可视化编排：拖动节点、从圆点拖线连接、右侧改属性、点试运行看执行路径',
  avoid: '线性、不超过 5 步的简单流程（用审批流程图）；节点上百的大型流程（要加缩放、小地图与分组）',
  kw: '工作流 编排 节点 连线 流程设计器 条件分支 workflow 自动化 拖拽 试运行',
  css: K('adflow008', 'btn tag in') + `.adflow008{width:1400px;max-width:100%;background:var(--card);border:1px solid var(--line2);border-radius:12px;overflow:hidden}.adflow008 .tb{display:flex;align-items:center;justify-content:space-between;flex-wrap:wrap;gap:10px 16px;padding:12px 16px;border-bottom:1px solid var(--line)}.adflow008 .tb .l{display:flex;align-items:center;gap:10px}.adflow008 .tb h4{font-size:16px;font-weight:600}.adflow008 .tb .r{display:flex;align-items:center;gap:8px}.adflow008 .bd{display:grid;grid-template-columns:minmax(0,1fr) 272px;min-height:500px}.adflow008 .mid{min-width:0;display:flex;flex-direction:column}.adflow008 .pal{display:flex;align-items:center;flex-wrap:wrap;gap:8px 8px;padding:10px 16px;border-bottom:1px solid var(--line);background:var(--n2)}.adflow008 .pal h5{margin:0 4px 0 0;font-size:12px;font-weight:400;color:var(--ink3)}.adflow008 .pal button{display:flex;align-items:center;gap:8px;height:36px;padding:0 12px 0 8px;border:1px solid var(--bd);border-radius:8px;background:var(--card);transition:border-color .15s}.adflow008 .pal button:hover{border-color:var(--ink3)}.adflow008 .ic2{display:inline-flex;align-items:center;justify-content:center;width:28px;height:28px;border-radius:8px;flex:none;background:var(--mub);color:var(--mu)}.adflow008 .ic2.in{background:var(--pt);color:var(--p-text)}.adflow008 .ic2.wn{background:var(--wnb);color:var(--wn)}.adflow008 .ic2.ok{background:var(--okb);color:var(--ok)}.adflow008 .pal .tip{margin-left:auto;font-size:12px;color:var(--ink3)}.adflow008 .cv{position:relative;flex:1;overflow:auto;background:var(--n1) radial-gradient(circle,var(--n8) 1px,transparent 1.2px) 0 0/20px 20px}.adflow008 .pl{position:relative;min-width:1000px;height:100%;min-height:440px}.adflow008 svg.es{position:absolute;inset:0;width:100%;height:100%;overflow:visible;pointer-events:none}.adflow008 .eg .ln{fill:none;stroke:var(--ink5);stroke-width:1.5;marker-end:url(#adflow008-ar)}.adflow008 .eg .hit{fill:none;stroke:transparent;stroke-width:16;pointer-events:stroke}.adflow008 .eg .cut{opacity:0;pointer-events:all;cursor:pointer;transition:opacity .15s}.adflow008 .eg:hover .cut{opacity:1}.adflow008 .eg .cut circle{fill:var(--card);stroke:var(--dg);stroke-width:1.5}.adflow008 .eg .cut path{stroke:var(--dg);stroke-width:1.5;stroke-linecap:round;fill:none}.adflow008 .tmp{fill:none;stroke:var(--p);stroke-width:1.5;stroke-dasharray:5 4}.adflow008 .nod{position:absolute;z-index:2;display:flex;align-items:center;gap:10px;width:${WF_W}px;height:${WF_H}px;padding:0 12px;border:1px solid var(--n8);border-radius:12px;background:var(--card);box-shadow:0 1px 3px var(--sh06);cursor:grab;user-select:none;-webkit-user-select:none;touch-action:none;transition:box-shadow .15s,border-color .15s}.adflow008 .nod:hover{box-shadow:0 4px 12px var(--sh10)}.adflow008 .nod.on{border-color:var(--p);box-shadow:0 0 0 1px var(--p),0 4px 12px var(--sh10)}.adflow008 .nod.drag{cursor:grabbing;z-index:5;box-shadow:0 10px 24px var(--sh18)}.adflow008 .nod.run{border-color:var(--p);background:var(--pt)}.adflow008 .nod.fin{border-color:var(--ok)}.adflow008 .nod.fin::after{content:"";position:absolute;right:-6px;top:-6px;width:16px;height:16px;border-radius:50%;background:var(--ok-fill) url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='none' stroke='%23fff' stroke-width='3.500' stroke-linecap='round' stroke-linejoin='round'%3E%3Cpath d='m5 12.500 4.500 4.500L19 7.500'/%3E%3C/svg%3E") center/10px no-repeat}.adflow008 .nod.cond{padding-right:30px}.adflow008 .nod .tx{min-width:0;display:flex;flex-direction:column}.adflow008 .nod b{font-weight:600;overflow:hidden;text-overflow:ellipsis;white-space:nowrap}.adflow008 .nod small{font-size:12px;color:var(--ink3);overflow:hidden;text-overflow:ellipsis;white-space:nowrap}.adflow008 .pt{position:absolute;width:12px;height:12px;border-radius:50%;background:var(--card);border:2px solid var(--n12);transform:translate(-50%,-50%);cursor:crosshair}.adflow008 .pt.in{left:0;top:50%}.adflow008 .pt.out{left:100%;top:50%}.adflow008 .pt.out:hover,.adflow008 .pt.in.hot{border-color:var(--p);background:var(--pt);transform:translate(-50%,-50%) scale(1.25)}.adflow008 i.plb{position:absolute;right:8px;transform:translateY(-50%);font-size:12px;color:var(--ink3);pointer-events:none}.adflow008 .pn{padding:16px;border-left:1px solid var(--line);display:flex;flex-direction:column;gap:12px}.adflow008 .pn .phd{display:flex;align-items:center;gap:10px}.adflow008 .pn .phd b{font-weight:600}.adflow008 .pn .fd .z-lb{display:block;margin-bottom:6px}.adflow008 .pn .two{display:grid;grid-template-columns:1fr 1fr;gap:8px}.adflow008 .pn .del{margin-top:auto;align-self:flex-start}.adflow008 .emp{display:flex;flex-direction:column;align-items:center;gap:8px;margin:auto 0;color:var(--ink3);text-align:center}.adflow008 .emp p{color:var(--ink2)}.adflow008 .emp p.sm{font-size:12px;color:var(--ink3);line-height:1.6}@media(max-width:900px){.adflow008 .bd{grid-template-columns:minmax(0,1fr)}.adflow008 .pal .tip{display:none}.adflow008 .pn{border-left:0;border-top:1px solid var(--line)}}`,
  html: () => { const ns = WF_NODES(); return `<div class="adflow008"><div class="tb"><div class="l"><h4>订单支付后回访</h4>${tag('草稿', 'dot')}</div><div class="r"><button type="button" class="z-btn" data-act="run">${ic('play')}试运行</button><button type="button" class="z-btn p" data-act="pub">发布</button></div></div><div class="bd"><div class="mid"><div class="pal"><h5>添加节点</h5>${Object.entries(WF_T).map(([k, [t, i, c]]) => `<button type="button" data-add="${k}"><span class="ic2 ${c}">${ic(i)}</span>${t}</button>`).join('')}<p class="tip">先选中一个节点再添加，新节点会接在它后面</p></div><div class="cv"><div class="pl"><svg class="es" aria-hidden="true"><defs><marker id="adflow008-ar" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="7" markerHeight="7" orient="auto"><path d="M1.5 1.5 8 5 1.5 8.5" style="fill:none;stroke:var(--ink5);stroke-width:1.6;stroke-linecap:round;stroke-linejoin:round"/></marker></defs><g class="egs">${wfEdges(ns, WF_E())}</g><path class="tmp" d="" hidden/></svg>${ns.map(wfNode).join('')}</div></div></div><div class="pn">${wfProps(null)}</div></div></div>` },
  js: (root) => {
    const el = $(root, '.adflow008'), pl = $(el, '.pl'), pn = $(el, '.pn'); let ns = WF_NODES(), es = WF_E(), sel = null, uid = 10, d = null, run = false
    const dirty = () => { const t = $(el, '.tb .z-tag'); t.className = 'z-tag dot wn'; t.textContent = '有未发布的修改' }
    const byId = (id) => ns.find((n) => n.id === id)
    const drawE = () => { $(el, '.egs').innerHTML = wfEdges(ns, es) }
    const drawN = (n) => { const o = $(pl, `.nod[data-id="${n.id}"]`); $(o, '.tx b').textContent = n.name; $(o, '.tx small').textContent = wfSub(n) }
    const fit = () => { pl.style.minWidth = Math.max(1000, ...ns.map((n) => n.x + WF_W + 40)) + 'px'; pl.style.minHeight = Math.max(440, ...ns.map((n) => n.y + WF_H + 40)) + 'px' }
    const pick = (id) => { sel = id; $$(pl, '.nod').forEach((o) => o.classList.toggle('on', o.dataset.id === id)); pn.innerHTML = wfProps(id ? byId(id) : null) }
    const pt = (e) => { const r = pl.getBoundingClientRect(); return { x: e.clientX - r.left, y: e.clientY - r.top } }
    pl.addEventListener('pointerdown', (e) => {
      if (run) return
      const port = e.target.closest('.pt.out')
      if (port) { const n = byId(port.closest('.nod').dataset.id); d = { k: 'link', from: n.id, p: port.dataset.port, id: e.pointerId }; pl.setPointerCapture(e.pointerId); return }
      const nd = e.target.closest('.nod'); if (!nd) { if (!e.target.closest('.eg')) pick(null); return }
      const n = byId(nd.dataset.id); pick(n.id); d = { k: 'move', n, o: nd, sx: e.clientX, sy: e.clientY, x0: n.x, y0: n.y, id: e.pointerId, on: false }; pl.setPointerCapture(e.pointerId)
    })
    pl.addEventListener('pointermove', (e) => {
      if (!d || e.pointerId !== d.id) return
      if (d.k === 'move') {
        if (!d.on && Math.hypot(e.clientX - d.sx, e.clientY - d.sy) < 4) return
        d.on = true; d.o.classList.add('drag'); d.n.x = Math.max(0, Math.round((d.x0 + e.clientX - d.sx) / 8) * 8); d.n.y = Math.max(0, Math.round((d.y0 + e.clientY - d.sy) / 8) * 8)
        d.o.style.left = d.n.x + 'px'; d.o.style.top = d.n.y + 'px'; drawE(); fit()
      } else {
        const s = wfPort(byId(d.from), d.p), p = pt(e), t = $(el, '.tmp'); t.removeAttribute('hidden'); t.setAttribute('d', `M${s.x} ${s.y}C${s.x + 56} ${s.y} ${p.x - 56} ${p.y} ${p.x} ${p.y}`)
        const over = document.elementFromPoint(e.clientX, e.clientY), hn = over && over.closest('.nod'); $$(pl, '.pt.in').forEach((x) => x.classList.remove('hot')); if (hn && hn.dataset.id !== d.from && hn.classList.contains('trig') === false) $(hn, '.pt.in').classList.add('hot')
      }
    })
    const up = (e) => {
      if (!d || e.pointerId !== d.id) return
      const m = d; d = null
      if (m.k === 'move') { m.o.classList.remove('drag'); if (m.on) dirty() }
      else {
        $(el, '.tmp').setAttribute('hidden', ''); $$(pl, '.pt.in').forEach((x) => x.classList.remove('hot'))
        const over = document.elementFromPoint(e.clientX, e.clientY), hn = over && over.closest('.nod')
        if (hn && hn.dataset.id !== m.from && !hn.classList.contains('trig')) { es = es.filter((x) => !(x[0] === m.from && x[1] === m.p)); es.push([m.from, m.p, hn.dataset.id]); drawE(); dirty(); toast(root, '已连接') }
      }
    }
    pl.addEventListener('pointerup', up); pl.addEventListener('pointercancel', up)
    pl.addEventListener('click', (e) => { const c = e.target.closest('[data-cut]'); if (c) { es.splice(+c.dataset.cut, 1); drawE(); dirty(); toast(root, '已断开连线') } })
    root.addEventListener('click', (e) => {
      const ad = e.target.closest('[data-add]')
      if (ad) {
        if (run) return; const ty = ad.dataset.add
        if (ty === 'trig' && ns.some((n) => n.ty === 'trig')) { toast(root, '一个流程只能有一个触发器'); return }
        const base = sel ? byId(sel) : null, x = base ? base.x + 220 : 16; let y = base ? base.y : 40
        const clash = (yy) => ns.some((n) => Math.abs(n.x - x) < 190 && Math.abs(n.y - yy) < 72)
        for (const dy of [0, 96, -96, 192, -192, 288]) { if (!clash(y + dy) && y + dy >= 0) { y += dy; break } }
        const dft = { trig: { event: '会员注册成功' }, cond: { field: '订单金额', op: '≥', val: '100' }, act: { kind: '发送站内信', val: '活动通知' }, delay: { n: 1, unit: '小时' } }[ty]
        const n = { id: 'n' + ++uid, ty, x, y, name: WF_T[ty][0], cfg: dft }; ns.push(n); pl.insertAdjacentHTML('beforeend', wfNode(n))
        if (base) { const free = base.ty === 'cond' ? ['yes', 'no'].find((p) => !es.some((x2) => x2[0] === base.id && x2[1] === p)) : es.some((x2) => x2[0] === base.id && x2[1] === 'out') ? null : 'out'; if (free) es.push([base.id, free, n.id]) }
        drawE(); fit(); pick(n.id); dirty(); return
      }
      const a = e.target.closest('[data-act]')
      if (a && a.dataset.act === 'pub') { const t = $(el, '.tb .z-tag'); t.className = 'z-tag dot ok'; t.textContent = '已发布'; toast(root, '已发布，新订单支付后会按此流程执行'); return }
      if (a && a.dataset.act === 'run' && !run) {
        const trig = ns.find((n) => n.ty === 'trig'); if (!trig) { toast(root, '先添加一个触发器'); return }
        run = true; a.disabled = true; $$(pl, '.nod').forEach((o) => o.classList.remove('run', 'fin'))
        const path = []; let cur = trig, guard = 0
        while (cur && guard++ < 20) { path.push(cur); const out = es.filter((x) => x[0] === cur.id); if (!out.length) break; let pick2 = out[0]; if (cur.ty === 'cond') { const v = cur.cfg.field === '订单金额' ? 680 : 3, th = +cur.cfg.val || 0, ok = cur.cfg.op === '≥' ? v >= th : cur.cfg.op === '＜' ? v < th : v === th; pick2 = out.find((x) => x[1] === (ok ? 'yes' : 'no')) || null } cur = pick2 ? byId(pick2[2]) : null }
        path.forEach((n, i) => { setTimeout(() => { const o = $(pl, `.nod[data-id="${n.id}"]`); if (o) o.classList.add('run') }, i * 520); setTimeout(() => { const o = $(pl, `.nod[data-id="${n.id}"]`); if (o) { o.classList.remove('run'); o.classList.add('fin') } }, i * 520 + 420) })
        setTimeout(() => { run = false; a.disabled = false; toast(root, `试运行完成：走过 ${path.length} 个节点（示例订单 ¥680）`) }, path.length * 520 + 200); return
      }
      if (e.target.closest('[data-rm]') && sel) { ns = ns.filter((n) => n.id !== sel); es = es.filter((x) => x[0] !== sel && x[2] !== sel); const o = $(pl, `.nod[data-id="${sel}"]`); if (o) o.remove(); drawE(); pick(null); dirty(); toast(root, '已删除节点') }
    })
    pn.addEventListener('input', (e) => {
      const n = byId(sel); if (!n) return
      if (e.target.matches('[data-nm]')) n.name = e.target.value
      else if (e.target.dataset.cfg) n.cfg[e.target.dataset.cfg] = e.target.dataset.cfg === 'n' ? Math.max(1, +e.target.value || 1) : e.target.value
      else return
      drawN(n); dirty()
    })
    pn.addEventListener('change', (e) => { const n = byId(sel); if (n && e.target.dataset.cfg) { n.cfg[e.target.dataset.cfg] = e.target.value; drawN(n); dirty() } })
  },
})

/* ---- AD-FLOW-009 待办面板 ---- */
const IB_ICON = { 采购申请: 'cart', 费用报销: 'receipt', 请假: 'calendar', 合同审批: 'file', 退款特批: 'wallet', 加班: 'clock', 补卡: 'edit', 物资领用: 'box' }
const IB = () => ({
  todo: [
    { id: 1, ty: '采购申请', t: '门店收银终端更新（20 台）', who: 0, dept: '运营部', at: '2 小时前', h: 2, amt: '¥48,000', urgent: true, d: '华东 6 家门店现有终端已使用 5 年以上，故障率偏高。' },
    { id: 2, ty: '退款特批', t: '订单 SO2026110300086 超期退款', who: 6, dept: '客服部', at: '昨天 09:30', h: 29, amt: '¥599', urgent: true, d: '客户收货后第 9 天反馈商品质量问题，已超出 7 天无理由，申请特批。' },
    { id: 3, ty: '费用报销', t: '双十一活动物料费 · 11 月第 1 周', who: 4, dept: '市场部', at: '5 小时前', h: 5, amt: '¥6,820', d: '含海报、展架与现场布置，发票 4 张已上传。' },
    { id: 4, ty: '合同审批', t: '华东仓储服务合同续签（含 2026–2027 年度价格条款与违约责任修订）', who: 2, dept: '仓储部', at: '昨天 11:05', h: 27, amt: '¥320,000', d: '年度价格上调 3%，违约金条款改为按日计收，法务已审。' },
    { id: 5, ty: '请假', t: '年假 3 天（11-10 至 11-12）', who: 7, dept: '客服部', at: '2 天前', h: 50, amt: '', d: '已与同组同事协调好排班。' },
  ],
  mine: [
    { id: 11, ty: '物资领用', t: '门店打印纸与标签纸（各 20 卷）', st: '审批中', node: '部门主管', at: '今天 09:12' },
    { id: 12, ty: '加班', t: '11-02 周末盘点加班 4 小时', st: '已通过', node: '', at: '11-03 17:40' },
    { id: 13, ty: '补卡', t: '10-31 上班补卡', st: '已驳回', node: '考勤专员', at: '11-02 10:05' },
  ],
  cc: [
    { id: 21, ty: '费用报销', t: '华东仓 10 月运输费结算', who: 4, dept: '财务部', at: '今天 10:20', unread: true },
    { id: 22, ty: '合同审批', t: '收银系统年度维保合同', who: 2, dept: '运营部', at: '昨天 15:00', unread: true },
    { id: 23, ty: '采购申请', t: '包装纸箱补货（5000 个）', who: 8, dept: '仓储部', at: '11-02 16:30' },
  ],
})
const ibRow = (k, r) => {
  const head = `<span class="tic">${ic(IB_ICON[r.ty] || 'file', 'l')}</span><div class="mn"><div class="l1"><b>${esc(r.t)}</b>${r.urgent ? tag('紧急', 'dg') : ''}${r.unread ? '<i class="ud" title="未读"></i>' : ''}</div>`
  if (k === 'mine') return `<li class="rw" data-id="${r.id}" data-k="mine">${head}<div class="l2">${tag(r.ty)}<span>${r.at} 提交</span>${r.st === '审批中' ? `<span>· 当前在「${r.node}」</span>` : r.st === '已驳回' ? `<span>· 被「${r.node}」驳回</span>` : ''}</div></div><div class="rt">${tag(r.st, (r.st === '已通过' ? 'ok' : r.st === '已驳回' ? 'dg' : 'in') + ' dot')}${r.st === '审批中' ? `<button type="button" class="z-btn t" data-act="urge">催办</button>` : ''}</div></li>`
  return `<li class="rw" data-id="${r.id}" data-k="${k}">${head}<div class="l2">${tag(r.ty)}<span class="z-who">${critter(r.who, 18)}${NAMES[r.who]} · ${r.dept}</span><span>${r.at}</span></div></div><div class="rt">${r.amt ? `<span class="am">${r.amt}</span>` : ''}${k === 'todo' ? '<div class="bs"><button type="button" class="z-btn t d" data-act="rej">驳回</button><button type="button" class="z-btn p" data-act="ok">通过</button></div>' : `<button type="button" class="z-btn t" data-act="read">${r.unread ? '标为已读' : '查看'}</button>`}</div></li>`
}
def({
  id: 'AD-FLOW-009', name: '待办面板', style: '就地审批', wide: false,
  fit: '首页或侧栏的待办入口：待我审批、我发起的、抄送我三类；列表里直接通过，驳回需填原因，处理完即时从列表消失并更新数量',
  avoid: '需要看完整表单和附件才能决定的审批（点进详情页）；条数很多的审批中心（用带筛选分页的列表页）',
  kw: '待办 审批 inbox 待我审批 抄送 催办 就地处理 通知 工作台 todo',
  css: K('adflow009', 'btn tag modal in tabs') + `.adflow009{position:relative;width:640px;max-width:100%;background:var(--card);border:1px solid var(--line2);border-radius:12px;overflow:hidden}.adflow009 .z-tabs{padding:0 20px}.adflow009 .lst{min-height:120px}.adflow009 .rw{display:flex;align-items:center;gap:12px;padding:14px 20px;border-bottom:1px solid var(--line);transition:opacity .2s,background-color .15s}.adflow009 .rw:hover{background:var(--n1)}.adflow009 .rw.out{opacity:0;transform:translateX(12px);transition:opacity .2s,transform .2s cubic-bezier(.2,0,0,1)}.adflow009 .tic{display:flex;align-items:center;justify-content:center;width:36px;height:36px;border-radius:8px;background:var(--pt);color:var(--p-text);flex:none;align-self:flex-start}.adflow009 .mn{flex:1;min-width:0;cursor:pointer}.adflow009 .l1{display:flex;align-items:center;gap:8px}.adflow009 .l1 b{font-weight:600;overflow:hidden;text-overflow:ellipsis;display:-webkit-box;-webkit-line-clamp:2;-webkit-box-orient:vertical}.adflow009 .l1 .z-tag{flex:none}.adflow009 .l2{display:flex;align-items:center;flex-wrap:wrap;gap:4px 10px;margin-top:6px;font-size:12px;color:var(--ink3)}.adflow009 .l2 .z-who{gap:6px;color:var(--ink2)}.adflow009 .rt{display:flex;flex-direction:column;align-items:flex-end;gap:6px;flex:none}.adflow009 .am{font-variant-numeric:tabular-nums;font-weight:600}.adflow009 .bs{display:flex;gap:4px}.adflow009 .ud{width:8px;height:8px;border-radius:50%;background:var(--danger-fill);flex:none}.adflow009 .ft{display:flex;align-items:center;justify-content:space-between;gap:12px;padding:12px 20px;font-size:12px;color:var(--ink3);background:var(--n2)}.adflow009 .emp{display:flex;flex-direction:column;align-items:center;gap:6px;padding:40px 20px;color:var(--ink3)}.adflow009 .emp .z-ic{width:36px;height:36px;color:var(--ok)}.adflow009 .emp b{color:var(--ink);font-weight:600;margin-top:4px}.adflow009 .dtl{display:flex;flex-direction:column;gap:12px}.adflow009 .dtl h4{font-size:16px;font-weight:600;line-height:1.5}.adflow009 .dtl dl{display:grid;grid-template-columns:72px 1fr;gap:8px 12px}.adflow009 .dtl dt{color:var(--ink3)}.adflow009 .fe{margin-top:8px}.adflow009 .z-tabs .z-n{background:var(--mub);padding:0 6px;border-radius:9px;line-height:18px;display:inline-block}`,
  html: () => { const d = IB(); return `<div class="adflow009">${tabs([['todo', '待我审批', d.todo.length], ['mine', '我发起的', d.mine.length], ['cc', '抄送我', d.cc.length]], 'todo', 'data-g="ib"')}<ul class="lst">${d.todo.map((r) => ibRow('todo', r)).join('')}</ul><div class="ft"><span class="fs">${d.todo.length} 项待处理 · 最久已等 ${Math.floor(Math.max(...d.todo.map((r) => r.h)) / 24)} 天</span><span>紧急的排在前面</span></div>${modal('rj', '驳回申请', '<p class="rjt" style="margin-bottom:10px;color:var(--ink2)"></p><label class="z-lb z-req">驳回原因</label><textarea class="z-in rjx" rows="3" maxlength="100" placeholder="说明原因，申请人会收到通知" style="margin-top:6px"></textarea>', '<button class="z-btn" type="button" data-close>取消</button><button class="z-btn p" type="button" data-act="rjok" disabled>确认驳回</button>')}${modal('dt', '审批详情', '<div class="dtl"></div>', '<button class="z-btn d" type="button" data-act="rej2">驳回</button><button class="z-btn p" type="button" data-act="ok2">通过</button>', 460)}</div>` },
  js: (root) => {
    const el = $(root, '.adflow009'), lst = $(el, '.lst'); let data = IB(), k = 'todo', cur = null
    const bump = () => { ['todo', 'mine', 'cc'].forEach((t) => { const n = $(el, `.z-tabs [data-t="${t}"] .z-n`); if (n) n.textContent = data[t].length; const lb = $(el, `.z-tabs [data-t="${t}"] .lb`); if (lb) lb.dataset.l = (t === 'todo' ? '待我审批' : t === 'mine' ? '我发起的' : '抄送我') + ' ' + data[t].length }) }
    const foot = () => { const f = $(el, '.ft'); const t = data.todo; $(f, '.fs').textContent = k === 'todo' ? (t.length ? `${t.length} 项待处理 · 最久已等 ${Math.max(...t.map((r) => r.h)) >= 24 ? Math.floor(Math.max(...t.map((r) => r.h)) / 24) + ' 天' : Math.max(...t.map((r) => r.h)) + ' 小时'}` : '没有待处理的审批') : k === 'mine' ? `共 ${data.mine.length} 条` : `${data.cc.filter((r) => r.unread).length} 条未读`; f.lastElementChild.textContent = k === 'todo' ? '紧急的排在前面' : k === 'cc' ? '抄送只读，不需要审批' : '' }
    const draw = () => {
      const rows = data[k]; lst.innerHTML = rows.length ? rows.map((r) => ibRow(k, r)).join('') : `<li class="emp">${ic('checkc')}<b>${k === 'todo' ? '待办已清空' : '这里没有内容'}</b><span>${k === 'todo' ? '新的审批会出现在这里' : '暂时没有记录'}</span></li>`; bump(); foot()
    }
    const done = (id, msg) => { const row = $(lst, `[data-id="${id}"]`); const fin = () => { data[k] = data[k].filter((r) => r.id !== id); draw(); toast(root, msg) }; if (row) { row.classList.add('out'); setTimeout(fin, 200) } else fin() }
    root.addEventListener('click', (e) => {
      const t = e.target.closest('.z-tabs [data-t]'); if (t) { k = t.dataset.t; draw(); return }
      const row = e.target.closest('.rw'), a = e.target.closest('[data-act]')
      if (a && a.dataset.act === 'ok' && row) { done(+row.dataset.id, '已通过'); return }
      if (a && a.dataset.act === 'rej' && row) { cur = data.todo.find((r) => r.id === +row.dataset.id); $(root, '.rjt').textContent = `驳回「${cur.t.length > 20 ? cur.t.slice(0, 20) + '…' : cur.t}」`; $(root, '.rjx').value = ''; $(root, '[data-act=rjok]').disabled = true; openOv(root, 'rj'); return }
      if (a && a.dataset.act === 'rjok') { closeOv(a); closeOv($(root, '[data-ov=dt]')); done(cur.id, '已驳回，申请人会收到通知'); return }
      if (a && a.dataset.act === 'urge') { a.textContent = '已催办'; a.disabled = true; toast(root, '已提醒当前审批人'); return }
      if (a && a.dataset.act === 'read' && row) { const r = data.cc.find((x) => x.id === +row.dataset.id); r.unread = false; draw(); toast(root, '已标为已读'); return }
      if (a && a.dataset.act === 'ok2' && cur) { closeOv(a); done(cur.id, '已通过'); return }
      if (a && a.dataset.act === 'rej2' && cur) { closeOv(a); $(root, '.rjt').textContent = `驳回「${cur.t.length > 20 ? cur.t.slice(0, 20) + '…' : cur.t}」`; $(root, '.rjx').value = ''; $(root, '[data-act=rjok]').disabled = true; openOv(root, 'rj'); return }
      const mn = e.target.closest('.mn')
      if (mn && row && row.dataset.k === 'todo') { cur = data.todo.find((r) => r.id === +row.dataset.id); $(root, '.dtl').innerHTML = `<h4>${esc(cur.t)}</h4><dl><dt>类型</dt><dd>${tag(cur.ty)}${cur.urgent ? ' ' + tag('紧急', 'dg') : ''}</dd><dt>申请人</dt><dd class="z-who">${critter(cur.who, 22)}${NAMES[cur.who]} · ${cur.dept}</dd><dt>提交时间</dt><dd>${cur.at}</dd>${cur.amt ? `<dt>金额</dt><dd>${cur.amt}</dd>` : ''}<dt>事由</dt><dd>${esc(cur.d)}</dd></dl>`; openOv(root, 'dt') }
      if (mn && row && row.dataset.k === 'cc') { const r = data.cc.find((x) => x.id === +row.dataset.id); if (r.unread) { r.unread = false; draw() } }
    })
    root.addEventListener('input', (e) => { if (e.target.matches('.rjx')) $(root, '[data-act=rjok]').disabled = e.target.value.trim().length < 2 })
    wireEsc(root)
  },
})

guide('ad', 'FLOW', [
  ['多级审批的进度展示', '审批流程图', '节点状态一眼看清，点节点看审批人、意见和时限，当前节点可直接通过或驳回'],
  ['需求、工单、线索按阶段推进', '任务看板', '拖卡片即换状态，列头显示数量，进行中有在制上限防止堆积'],
  ['订单、售后这类有固定状态机的对象', '状态流转图', '图上只给合法的下一步，危险流转先确认，每次流转都有记录'],
  ['客服工单、跟进记录', '工单时间线', '客户来信、客服回复、内部备注与状态变更按时间排好，底部直接回复'],
  ['会议、拜访排期；门店、客服按人排班', '日程周视图', '点空白格新建日程；按人排班时改用员工排班表，点格子选班次并统计在岗与工时'],
  ['首页待办、筹备清单', '待办面板', '待我审批 / 我发起 / 抄送我就地处理；分组清单勾选看进度时用任务清单'],
  ['营销自动化、规则流程的可视化搭建', '工作流编排', '拖节点、拉线、右侧改属性，试运行能看到执行路径'],
])

/* ================= MGMT 系统管理 ================= */
/* ---- AD-MGMT-001 角色权限矩阵 ---- */
const RB_MOD = [['订单管理', ['订单列表', '退款审核', '发货管理']], ['商品管理', ['商品列表', '库存盘点']], ['会员营销', ['会员列表', '优惠券', '积分规则']], ['数据与财务', ['经营报表', '对账结算']]]
const RB_ACT = [['v', '查看'], ['a', '新增'], ['e', '编辑'], ['d', '删除']]
const RB_F = RB_MOD.flatMap(([, fs], gi) => fs.map((n) => ({ g: gi, n })))
const rbp = (o) => new Set(Object.entries(o).flatMap(([fi, acts]) => [...acts].map((a) => `${fi}.${a}`)))
const RB_ROLES = () => [
  { id: 'owner', n: '店长', cnt: 1, lock: true, saved: new Set(RB_F.flatMap((_, i) => RB_ACT.map(([a]) => `${i}.${a}`))) },
  { id: 'ops', n: '运营专员', cnt: 12, saved: rbp({ 0: 've', 1: 'v', 2: 'v', 3: 'vaed', 4: 'v', 5: 'vae', 6: 'vaed', 7: 've', 8: 'v' }) },
  { id: 'cs', n: '客服', cnt: 18, saved: rbp({ 0: 've', 1: 've', 2: 'v', 5: 'v' }) },
  { id: 'fin', n: '财务', cnt: 4, saved: rbp({ 0: 'v', 1: 've', 8: 'v', 9: 'vae' }) },
  { id: 'wh', n: '仓管', cnt: 6, saved: rbp({ 2: 've', 3: 'v', 4: 'vaed' }) },
].map((r) => ({ ...r, cur: new Set(r.saved) }))
const rbKeys = (fis, acts = RB_ACT.map((a) => a[0])) => fis.flatMap((i) => acts.map((a) => `${i}.${a}`))
const rbSt = (set, keys) => (keys.every((k) => set.has(k)) ? 1 : keys.some((k) => set.has(k)) ? 2 : 0)
const rbTable = (r, fold) => {
  const lk = r.lock ? ' dis' : '', all = RB_F.map((_, i) => i)
  const head = `<thead><tr><th class="l">功能</th>${RB_ACT.map(([a, t]) => `<th><span class="ch" data-col="${a}">${ck(rbSt(r.cur, rbKeys(all, [a]))).replace('class="z-ck', 'class="z-ck' + lk)}${t}</span></th>`).join('')}<th>全选</th></tr></thead>`
  let body = ''
  RB_MOD.forEach(([g, fs], gi) => {
    const idx = RB_F.map((f, i) => (f.g === gi ? i : -1)).filter((i) => i >= 0)
    body += `<tr class="gr"><td class="l" colspan="6"><span class="gh"><button type="button" class="fold${fold.has(gi) ? '' : ' open'}" data-fold="${gi}" aria-label="${fold.has(gi) ? '展开' : '收起'}${g}">${ic('down', 's')}</button><span class="ch" data-grp="${gi}">${ck(rbSt(r.cur, rbKeys(idx))).replace('class="z-ck', 'class="z-ck' + lk)}<b>${g}</b></span><em>${fs.length} 项</em></span></td></tr>`
    if (!fold.has(gi)) idx.forEach((i) => { body += `<tr><td class="l fn">${RB_F[i].n}</td>${RB_ACT.map(([a]) => `<td><span class="ch" data-k="${i}.${a}">${ck(r.cur.has(`${i}.${a}`) ? 1 : 0).replace('class="z-ck', 'class="z-ck' + lk)}</span></td>`).join('')}<td><span class="ch" data-row="${i}">${ck(rbSt(r.cur, rbKeys([i]))).replace('class="z-ck', 'class="z-ck' + lk)}</span></td></tr>` })
  })
  return head + `<tbody>${body}</tbody>`
}
const rbDiff = (r) => [...r.cur].filter((k) => !r.saved.has(k)).length + [...r.saved].filter((k) => !r.cur.has(k)).length
def({
  id: 'AD-MGMT-001', name: '角色权限矩阵', style: '联动勾选', wide: true,
  fit: '给角色分配功能权限：行是功能、列是查看 / 新增 / 编辑 / 删除，行、列、分组都能一键全选并显示半选，内置角色只读',
  avoid: '按数据范围（只能看本店、本人）授权的场景（需另做数据权限）；功能上百个时（改成菜单树 + 按钮级权限）',
  kw: '角色 权限 矩阵 授权 查看 新增 编辑 删除 半选 rbac',
  css: K('admgmt001', 'btn tag ck modal tbl') + `.admgmt001{width:1100px;max-width:100%;display:grid;grid-template-columns:216px minmax(0,1fr);background:var(--card);border:1px solid var(--line2);border-radius:12px}.admgmt001 .rl{padding:12px;border-right:1px solid var(--line);background:var(--n2);border-radius:12px 0 0 12px;display:flex;flex-direction:column;gap:4px}.admgmt001 .rl h5{margin:4px 8px 8px;font-size:12px;font-weight:400;color:var(--ink3)}.admgmt001 .rl button{display:flex;align-items:center;gap:8px;min-height:44px;padding:0 10px;border-radius:8px;text-align:left;transition:background-color .15s}.admgmt001 .rl button:hover{background:var(--n4)}.admgmt001 .rl button.on{background:var(--lift);box-shadow:0 1px 2px var(--sh10);color:var(--p-text)}.admgmt001 .rl .nm{flex:1;font-weight:600}.admgmt001 .rl .n{font-size:12px;color:var(--ink3)}.admgmt001 .rl .dt{width:6px;height:6px;border-radius:50%;background:var(--warn-fill)}.admgmt001 .mx{min-width:0;display:flex;flex-direction:column}.admgmt001 .mh2{display:flex;align-items:center;justify-content:space-between;flex-wrap:wrap;gap:10px 16px;padding:14px 20px;border-bottom:1px solid var(--line)}.admgmt001 .mh2 h4{font-size:16px;font-weight:600;display:flex;align-items:center;gap:8px}.admgmt001 .mh2 p{font-size:12px;color:var(--ink3);margin-top:2px}.admgmt001 .mh2 .r{display:flex;gap:8px}.admgmt001 .tw{max-height:424px;overflow:auto}.admgmt001 .z-tbl{min-width:600px}.admgmt001 .z-tbl thead th{position:sticky;top:0;z-index:2}.admgmt001 .fn{white-space:nowrap}.admgmt001 .z-tbl td{height:44px}.admgmt001 .ch{display:inline-flex;align-items:center;gap:8px;cursor:pointer;user-select:none;-webkit-user-select:none}.admgmt001 .dis .ch,.admgmt001 .ch:has(.dis){cursor:not-allowed}.admgmt001 tr.gr td{background:var(--n1);height:40px}.admgmt001 .gh{display:inline-flex;align-items:center;gap:8px}.admgmt001 .gh b{font-weight:600}.admgmt001 .gh em{font-size:12px;color:var(--ink3);margin-left:4px}.admgmt001 .fold{display:flex;align-items:center;justify-content:center;width:24px;height:24px;border-radius:4px;color:var(--ink2)}.admgmt001 .fold:hover{background:var(--mub)}.admgmt001 .fold .z-ic{transition:transform .2s cubic-bezier(.2,0,0,1)}.admgmt001 .fold:not(.open) .z-ic{transform:rotate(-90deg)}.admgmt001 .fn{padding-left:56px!important}.admgmt001 .ft{display:flex;align-items:center;justify-content:space-between;flex-wrap:wrap;gap:10px 16px;padding:12px 20px;border-top:1px solid var(--line)}.admgmt001 .ft .l{display:flex;align-items:center;gap:12px;color:var(--ink2)}.admgmt001 .ft .l b{font-weight:600;color:var(--ink)}.admgmt001 .ft .r{display:flex;gap:8px}.admgmt001 .lkt{display:flex;align-items:center;gap:6px;font-size:12px;color:var(--ink3)}@media(max-width:820px){.admgmt001{grid-template-columns:minmax(0,1fr)}.admgmt001 .rl{flex-direction:row;overflow-x:auto;border-right:0;border-bottom:1px solid var(--line);border-radius:12px 12px 0 0}.admgmt001 .rl h5{display:none}.admgmt001 .rl button{flex:none}}`,
  html: () => { const rs = RB_ROLES(), r = rs[1]; return `<div class="admgmt001"><div class="rl"><h5>角色</h5>${rs.map((x) => `<button type="button" data-role="${x.id}" class="${x.id === r.id ? 'on' : ''}"><span class="nm">${x.n}</span>${x.lock ? ic('lock', 's') : ''}<span class="n">${x.cnt} 人</span></button>`).join('')}</div><div class="mx"><div class="mh2"><div><h4><span class="rn">${r.n}</span></h4><p>新增、编辑、删除需要同时有查看权限，取消查看会清空该功能的其他权限</p></div><div class="r"><button type="button" class="z-btn" data-act="all">全部授权</button><button type="button" class="z-btn" data-act="none">清空</button></div></div><div class="tw"><table class="z-tbl">${rbTable(r, new Set())}</table></div><div class="ft"><div class="l"><span>已授权 <b class="nn">${r.cur.size}</b> / ${RB_F.length * 4} 项</span><span class="df"></span></div><div class="r"><button type="button" class="z-btn" data-act="reset" disabled>撤销修改</button><button type="button" class="z-btn p" data-act="save" disabled>保存权限</button></div></div></div></div>` },
  js: (root) => {
    const el = $(root, '.admgmt001'), rs = RB_ROLES(); let cur = 'ops'; const fold = new Set()
    const role = () => rs.find((r) => r.id === cur)
    const all = RB_F.map((_, i) => i)
    const draw = () => {
      const r = role(), d = rbDiff(r)
      $(el, '.rl').innerHTML = '<h5>角色</h5>' + rs.map((x) => `<button type="button" data-role="${x.id}" class="${x.id === cur ? 'on' : ''}"><span class="nm">${x.n}</span>${x.lock ? ic('lock', 's') : rbDiff(x) ? '<i class="dt" title="有未保存的修改"></i>' : ''}<span class="n">${x.cnt} 人</span></button>`).join('')
      $(el, '.rn').innerHTML = r.n + (r.lock ? tag('系统内置 · 只读', '') : ''); $(el, '.z-tbl').innerHTML = rbTable(r, fold)
      $(el, '.nn').textContent = r.cur.size; $(el, '.df').innerHTML = d ? tag(`有 ${d} 处未保存修改`, 'wn dot') : ''
      $(el, '[data-act=save]').disabled = !d; $(el, '[data-act=reset]').disabled = !d; $$(el, '.mh2 .r .z-btn').forEach((b) => (b.disabled = !!r.lock))
    }
    const setKeys = (keys, on) => {
      const r = role(); if (r.lock) return
      keys.forEach((k) => { const [fi, a] = k.split('.'); if (on) { r.cur.add(k); r.cur.add(`${fi}.v`) } else { r.cur.delete(k); if (a === 'v') RB_ACT.forEach(([x]) => r.cur.delete(`${fi}.${x}`)) } })
      draw()
    }
    root.addEventListener('click', (e) => {
      const r = role()
      const b = e.target.closest('[data-role]'); if (b) { cur = b.dataset.role; draw(); return }
      const f = e.target.closest('[data-fold]'); if (f) { const g = +f.dataset.fold; fold.has(g) ? fold.delete(g) : fold.add(g); draw(); return }
      const c = e.target.closest('.ch'); if (c) {
        if (r.lock) { toast(root, '系统内置角色的权限不能修改'); return }
        let keys; if (c.dataset.k) keys = [c.dataset.k]; else if (c.dataset.row) keys = rbKeys([+c.dataset.row]); else if (c.dataset.col) keys = rbKeys(all, [c.dataset.col]); else if (c.dataset.grp) keys = rbKeys(all.filter((i) => RB_F[i].g === +c.dataset.grp))
        setKeys(keys, rbSt(r.cur, keys) !== 1); return
      }
      const a = e.target.closest('[data-act]'); if (!a) return
      if (a.dataset.act === 'all') setKeys(rbKeys(all), true)
      if (a.dataset.act === 'none') setKeys(rbKeys(all), false)
      if (a.dataset.act === 'reset') { r.cur = new Set(r.saved); draw(); toast(root, '已撤销修改') }
      if (a.dataset.act === 'save') { r.saved = new Set(r.cur); draw(); toast(root, `已保存「${r.n}」的权限，${r.cnt} 位成员下次刷新后生效`) }
    })
    root.addEventListener('keydown', (e) => { if ((e.key === ' ' || e.key === 'Enter') && e.target.matches('.z-ck')) { e.preventDefault(); e.target.closest('.ch').click() } })
  },
})

/* ---- AD-MGMT-002 菜单树配置 ---- */
const MT_TY = { dir: ['目录', ''], menu: ['菜单', 'in'], btn: ['按钮', 'ok'] }
const MT = () => [
  { id: 'm1', t: '工作台', ty: 'menu', icon: 'dashboard', path: '/workbench', show: true, c: 1, ch: [] },
  { id: 'm2', t: '交易管理', ty: 'dir', icon: 'receipt', show: true, open: true, ch: [
    { id: 'm21', t: '订单管理', ty: 'menu', icon: 'file', path: '/trade/orders', show: true, open: true, ch: [{ id: 'm211', t: '查看订单', ty: 'btn', show: true, c: 1, ch: [] }, { id: 'm212', t: '发货', ty: 'btn', show: true, c: 1, ch: [] }, { id: 'm213', t: '导出订单', ty: 'btn', show: true, c: 0, ch: [] }] },
    { id: 'm22', t: '售后管理', ty: 'menu', icon: 'refresh', path: '/trade/after-sales', show: true, c: 1, ch: [] },
  ] },
  { id: 'm3', t: '商品管理', ty: 'dir', icon: 'box', show: true, ch: [
    { id: 'm31', t: '商品列表', ty: 'menu', icon: 'list', path: '/goods/list', show: true, c: 1, ch: [] },
    { id: 'm32', t: '分类管理', ty: 'menu', icon: 'tag', path: '/goods/category', show: true, c: 1, ch: [] },
    { id: 'm33', t: '库存盘点', ty: 'menu', icon: 'clipboard', path: '/goods/stock', show: false, c: 0, ch: [] },
  ] },
  { id: 'm4', t: '会员营销', ty: 'dir', icon: 'users', show: true, ch: [
    { id: 'm41', t: '会员列表', ty: 'menu', icon: 'user', path: '/member/list', show: true, c: 1, ch: [] },
    { id: 'm42', t: '优惠券', ty: 'menu', icon: 'coupon', path: '/member/coupons', show: true, c: 0, ch: [] },
  ] },
  { id: 'm5', t: '系统管理', ty: 'dir', icon: 'gear', show: true, ch: [
    { id: 'm51', t: '员工账号', ty: 'menu', icon: 'users', path: '/system/staff', show: true, c: 1, ch: [] },
    { id: 'm52', t: '角色权限', ty: 'menu', icon: 'shield', path: '/system/roles', show: true, c: 1, ch: [] },
    { id: 'm53', t: '操作日志', ty: 'menu', icon: 'clock', path: '/system/logs', show: true, c: 0, ch: [] },
  ] },
]
const mtLeaves = (n) => (n.ch.length ? n.ch.flatMap(mtLeaves) : [n])
const mtFind = (ns, id, par = null) => { for (const n of ns) { if (n.id === id) return { n, par, list: ns }; const r = mtFind(n.ch, id, n); if (r) return r } return null }
const mtMatch = (n, q) => n.t.toLowerCase().includes(q) || n.ch.some((c) => mtMatch(c, q))
const mtRow = (ns, sel, q) => `<ul>${ns.filter((n) => !q || mtMatch(n, q)).map((n) => {
  const lv = mtLeaves(n), st = rbSt(new Set(lv.filter((x) => x.c).map((x) => x.id)), lv.map((x) => x.id)), open = q ? true : n.open
  const label = q && n.t.toLowerCase().includes(q) ? esc(n.t).replace(new RegExp('(' + q.replace(/[.*+?^${}()|[\]\\]/g, '\\$&') + ')', 'i'), '<mark>$1</mark>') : esc(n.t)
  return `<li class="${n.ch.length && open ? 'open' : ''}" data-id="${n.id}"><div class="rw${sel === n.id ? ' on' : ''}${n.show ? '' : ' off'}" data-sel>${n.ch.length ? `<button type="button" class="exb" data-ex aria-label="展开或收起${esc(n.t)}">${ic('right', 's')}</button>` : '<span class="exb"></span>'}${ck(st, `data-ck aria-label="勾选${esc(n.t)}"`)}${n.icon ? `<i class="ni">${ic(n.icon)}</i>` : ''}<span class="nm">${label}</span>${tag(MT_TY[n.ty][0], MT_TY[n.ty][1])}${n.show ? '' : `<span class="hid" title="已在侧栏隐藏">${ic('eyeoff', 's')}</span>`}</div>${n.ch.length ? mtRow(n.ch, sel, q) : ''}</li>`
}).join('')}</ul>`
const mtPanel = (d) => {
  if (!d) return `<div class="emp">${ic('list', 'xl')}<p>点击左侧的节点查看和修改配置</p></div>`
  const { n, list } = d, i = list.indexOf(n)
  return `<div class="ph2"><i class="ni big">${ic(n.icon || 'bz_stack', 'l')}</i><div><b>${esc(n.t)}</b><br>${tag(MT_TY[n.ty][0], MT_TY[n.ty][1])}</div></div><div class="fd"><label class="z-lb">显示名称</label><input class="z-in" data-nm value="${esc(n.t)}" maxlength="12"></div>${n.path ? `<div class="fd"><label class="z-lb">访问路径</label><input class="z-in" value="${esc(n.path)}" readonly aria-readonly="true"></div>` : ''}<div class="fd row2"><div><label class="z-lb">${n.ty === 'btn' ? '启用' : '在侧栏显示'}</label><p class="sm">${n.ty === 'btn' ? '关闭后该按钮对所有角色隐藏' : '关闭后侧栏不再出现，已有权限不受影响'}</p></div>${sw(n.show, 'data-show')}</div><div class="fd row2"><div><label class="z-lb">同级排序</label><p class="sm">第 ${i + 1} 位，共 ${list.length} 个</p></div><div class="mv"><button type="button" class="z-x" data-mv="-1" ${i === 0 ? 'disabled' : ''} aria-label="上移">${ic('arrowup')}</button><button type="button" class="z-x" data-mv="1" ${i === list.length - 1 ? 'disabled' : ''} aria-label="下移">${ic('arrowdown')}</button></div></div>`
}
def({
  id: 'AD-MGMT-002', name: '菜单树配置', style: '勾选与排序', wide: true,
  fit: '配置侧栏菜单与按钮权限的层级：展开收起、搜索定位、三态勾选，点节点在右侧改名称、显隐与排序，开关直接生效',
  avoid: '节点上千的超大树（要做懒加载）；只需要纯展示的目录结构（用简单的树形列表）',
  kw: '菜单 树 配置 目录 按钮 勾选 展开 排序 tree 权限',
  css: K('admgmt002', 'btn tag ck sw in') + `.admgmt002{width:1100px;max-width:100%;display:grid;grid-template-columns:minmax(0,1fr) 320px;background:var(--card);border:1px solid var(--line2);border-radius:12px}.admgmt002 .tr{min-width:0;display:flex;flex-direction:column}.admgmt002 .tb{display:flex;align-items:center;flex-wrap:wrap;gap:10px;padding:12px 16px;border-bottom:1px solid var(--line)}.admgmt002 .sq{position:relative;flex:1;min-width:180px;max-width:280px}.admgmt002 .sq .z-ic{position:absolute;left:10px;top:9px;color:var(--ink3)}.admgmt002 .sq input{padding-left:32px;height:32px}.admgmt002 .tb .nn{margin-left:auto;font-size:12px;color:var(--ink3)}.admgmt002 .tree{padding:8px 12px 12px;max-height:440px;overflow:auto}.admgmt002 .tree ul{display:flex;flex-direction:column}.admgmt002 .tree ul ul{margin-left:22px;display:none;border-left:1px solid var(--line);padding-left:4px}.admgmt002 .tree li.open>ul{display:flex}.admgmt002 .rw{display:flex;align-items:center;gap:8px;height:40px;padding:0 10px 0 4px;border-radius:8px;cursor:pointer;transition:background-color .15s}.admgmt002 .rw:hover{background:var(--sf)}.admgmt002 .rw.on{background:var(--pt)}.admgmt002 .rw.off .nm{color:var(--ink3)}.admgmt002 .exb{display:flex;align-items:center;justify-content:center;width:28px;height:32px;border-radius:4px;color:var(--ink2);flex:none}.admgmt002 button.exb:hover{background:var(--mub)}.admgmt002 .exb .z-ic{transition:transform .2s cubic-bezier(.2,0,0,1)}.admgmt002 li.open>.rw .exb .z-ic{transform:rotate(90deg)}.admgmt002 .ni{display:inline-flex;align-items:center;justify-content:center;width:24px;height:24px;color:var(--ink2);flex:none}.admgmt002 .ni.big{width:40px;height:40px;border-radius:8px;background:var(--pt);color:var(--p-text)}.admgmt002 .nm{flex:1;min-width:0;overflow:hidden;text-overflow:ellipsis;white-space:nowrap}.admgmt002 mark{background:var(--wnb);color:var(--wn);border-radius:2px}.admgmt002 .hid{display:flex;color:var(--ink3)}.admgmt002 .pn{padding:20px;border-left:1px solid var(--line);background:var(--n2);border-radius:0 12px 12px 0;display:flex;flex-direction:column;gap:16px}.admgmt002 .ph2{display:flex;align-items:center;gap:12px}.admgmt002 .ph2 b{font-weight:600;font-size:16px}.admgmt002 .fd .z-lb{display:block;margin-bottom:6px}.admgmt002 .fd.row2{display:flex;align-items:center;justify-content:space-between;gap:12px}.admgmt002 .fd.row2 .z-lb{margin:0}.admgmt002 .sm{font-size:12px;color:var(--ink3);margin-top:2px}.admgmt002 .mv{display:flex;gap:4px}.admgmt002 .mv .z-x{border:1px solid var(--bd);background:var(--card)}.admgmt002 .mv .z-x:disabled{opacity:.4;cursor:not-allowed}.admgmt002 .emp{display:flex;flex-direction:column;align-items:center;gap:8px;margin:auto 0;color:var(--ink3)}.admgmt002 .auto{margin-top:auto;font-size:12px;color:var(--ink3);display:flex;align-items:center;gap:6px}@media(max-width:820px){.admgmt002{grid-template-columns:minmax(0,1fr)}.admgmt002 .pn{border-left:0;border-top:1px solid var(--line);border-radius:0 0 12px 12px}}`,
  html: () => { const ns = MT(); return `<div class="admgmt002"><div class="tr"><div class="tb"><label class="sq">${ic('search')}<input class="z-in" type="search" placeholder="搜索菜单名称" aria-label="搜索菜单"></label><button type="button" class="z-btn" data-act="open">展开全部</button><button type="button" class="z-btn" data-act="shut">收起全部</button><span class="nn">已勾选 <b>${ns.flatMap(mtLeaves).filter((x) => x.c).length}</b> 项</span></div><div class="tree">${mtRow(ns, 'm21', '')}</div></div><div class="pn">${mtPanel(mtFind(ns, 'm21'))}</div></div>` },
  js: (root) => {
    const el = $(root, '.admgmt002'), tree = $(el, '.tree'), pn = $(el, '.pn'); const ns = MT(); let sel = 'm21', q = ''
    const walk = (list, f) => list.forEach((n) => { f(n); walk(n.ch, f) })
    const draw = () => { tree.innerHTML = mtRow(ns, sel, q); $(el, '.tb .nn b').textContent = ns.flatMap(mtLeaves).filter((x) => x.c).length }
    const panel = () => { pn.innerHTML = mtPanel(sel ? mtFind(ns, sel) : null) + '<p class="auto">' + ic('checkc', 's') + '修改后自动保存</p>' }
    panel()
    root.addEventListener('click', (e) => {
      const li = e.target.closest('li[data-id]'), a = e.target.closest('[data-act]')
      if (a) { walk(ns, (n) => { if (n.ch.length) n.open = a.dataset.act === 'open' }); q = ''; $(el, '.sq input').value = ''; draw(); return }
      if (e.target.closest('[data-ex]') && li) { const d = mtFind(ns, li.dataset.id); d.n.open = !d.n.open; draw(); return }
      if (e.target.closest('[data-ck]') && li) { const n = mtFind(ns, li.dataset.id).n, lv = mtLeaves(n), on = !lv.every((x) => x.c); lv.forEach((x) => (x.c = on ? 1 : 0)); draw(); return }
      if (e.target.closest('[data-sel]') && li) { sel = li.dataset.id; draw(); panel(); return }
      const s = e.target.closest('[data-show]'); if (s && sel) { const n = mtFind(ns, sel).n; n.show = !n.show; panel(); draw(); toast(root, n.show ? `「${n.t}」已显示` : `「${n.t}」已隐藏，侧栏不再出现`); return }
      const m = e.target.closest('[data-mv]'); if (m && sel) { const d = mtFind(ns, sel), i = d.list.indexOf(d.n), j = i + +m.dataset.mv; if (j < 0 || j >= d.list.length) return; d.list.splice(j, 0, d.list.splice(i, 1)[0]); draw(); panel(); toast(root, `已移到第 ${j + 1} 位`) }
    })
    pn.addEventListener('input', (e) => { if (e.target.matches('[data-nm]') && sel) { const n = mtFind(ns, sel).n; n.t = e.target.value.trim() || n.t; draw(); $(pn, '.ph2 b').textContent = n.t } })
    $(el, '.sq input').addEventListener('input', (e) => { q = e.target.value.trim().toLowerCase(); draw() })
    root.addEventListener('keydown', (e) => { if ((e.key === ' ' || e.key === 'Enter') && e.target.matches('.z-ck, .z-sw')) { e.preventDefault(); e.target.click() } })
  },
})

/* ---- AD-MGMT-003 操作日志列表 ---- */
const LG_T = [
  ['订单管理', '修改订单 SO2026110400128 的收货地址', '信息'], ['订单管理', '审核通过退款申请 RF20261103021（¥599）', '信息'], ['订单管理', '导出订单报表（10-01 至 10-31）', '信息'],
  ['订单管理', '导出订单报表失败：时间范围超过 31 天', '错误'], ['商品管理', '调整「轻量跑鞋」售价 ¥329 → ¥299', '警告'], ['商品管理', '下架商品「无线降噪耳机」', '信息'],
  ['优惠券', '删除优惠券「新人 20 元券」', '警告'], ['会员管理', '手动调整会员 林小满 的积分 +200', '警告'], ['系统设置', '修改「订单自动关闭时间」30 → 45 分钟', '警告'],
  ['角色权限', '为角色「客服」新增「退款审核」的编辑权限', '警告'], ['登录', '账号登录成功', '信息'], ['登录', '密码连续错误 3 次，账号已锁定 15 分钟', '错误'],
  ['短信服务', '验证码短信发送失败（通道超时）', '错误'], ['商品管理', '批量上架 12 个商品', '信息'], ['会员管理', '导出会员名单（共 2,386 人）', '信息'],
]
const LG = Array.from({ length: 46 }, (_, i) => { const t = LG_T[(i * 7 + (i % 3)) % LG_T.length], m = 1244 - i * 11, w = i % 8; return { id: i, at: `11-04 ${pad(Math.floor(m / 60))}:${pad(m % 60)}`, who: w, mod: t[0], act: t[1], lv: t[2], ok: !(t[2] === '错误'), ip: `192.168.${i % 5}.${20 + i}`, ms: 40 + ((i * 53) % 420), dev: ['Chrome 126 · Windows 11', 'Edge 126 · Windows 10', 'Safari 17 · macOS'][i % 3] } })
const LG_LV = { 信息: 'mu', 警告: 'wn', 错误: 'dg' }
const pgBtns = (p, n) => { if (n <= 7) return Array.from({ length: n }, (_, i) => i + 1); const s = new Set([1, 2, n - 1, n, p - 1, p, p + 1]); const a = [...s].filter((x) => x >= 1 && x <= n).sort((x, y) => x - y), o = []; a.forEach((x, i) => { if (i && x - a[i - 1] > 1) o.push('…'); o.push(x) }); return o }
const lgFilter = (k, q) => LG.filter((r) => (k === 'all' || (k === 'care' ? r.lv !== '信息' : r.lv === k)) && (!q || (NAMES[r.who] + r.act + r.mod).toLowerCase().includes(q)))
def({
  id: 'AD-MGMT-003', name: '操作日志列表', style: '级别与展开', wide: true,
  fit: '审计员工操作：默认只看需要关注的警告与错误，级别带数量，即输即查，点行展开 IP、设备与耗时，分页默认每页 20 条',
  avoid: '需要精确到字段对比的审计（要另做变更详情页）；日志量级过大时（改用服务端检索与导出）',
  kw: '操作日志 审计 日志 级别 警告 错误 展开 分页 audit 追溯',
  css: K('admgmt003', 'btn tag in seg tbl dd') + `.admgmt003{width:1100px;max-width:100%;background:var(--card);border:1px solid var(--line2);border-radius:12px}.admgmt003 .tb{display:flex;align-items:center;justify-content:space-between;flex-wrap:wrap;gap:10px 16px;padding:12px 16px;border-bottom:1px solid var(--line)}.admgmt003 .tb .l{display:flex;align-items:center;flex-wrap:wrap;gap:10px 12px}.admgmt003 .sq{position:relative;width:240px;max-width:100%}.admgmt003 .sq .z-ic{position:absolute;left:10px;top:9px;color:var(--ink3)}.admgmt003 .sq input{padding-left:32px;height:32px}.admgmt003 .tb .l{min-width:0;max-width:100%}.admgmt003 .z-seg{max-width:100%;overflow-x:auto;scrollbar-width:none}.admgmt003 .z-seg::-webkit-scrollbar{display:none}.admgmt003 .z-seg button{flex:none}.admgmt003 .z-seg button em{margin-left:4px;font-style:normal;font-size:12px;color:var(--ink3)}.admgmt003 .z-seg button em.z0{opacity:.5}.admgmt003 .z-seg button.on em{color:var(--p-text)}.admgmt003 .tw{max-height:480px;overflow:auto}.admgmt003 .z-tbl{min-width:800px}.admgmt003 .z-tbl thead th{position:sticky;top:0;z-index:2}.admgmt003 .z-tbl td{height:46px}.admgmt003 td.l{overflow-wrap:anywhere}.admgmt003 .xp{display:inline-flex;align-items:center;justify-content:center;width:32px;height:32px;border-radius:4px;color:var(--ink2)}.admgmt003 .xp:hover{background:var(--mub)}.admgmt003 .xp .z-ic{transition:transform .2s cubic-bezier(.2,0,0,1)}.admgmt003 tr.open .xp .z-ic{transform:rotate(180deg)}.admgmt003 tr.dtr td{height:auto;padding:12px 16px 14px;background:var(--n2);text-align:left}.admgmt003 tr.dtr dl{display:grid;grid-template-columns:repeat(auto-fit,minmax(160px,1fr));gap:8px 24px}.admgmt003 tr.dtr dt{font-size:12px;color:var(--ink3)}.admgmt003 tr.dtr dd{margin-top:2px}.admgmt003 .res{display:inline-flex;align-items:center;gap:6px}.admgmt003 .res i{width:6px;height:6px;border-radius:50%;background:var(--ok-fill)}.admgmt003 .res.bad{color:var(--dg)}.admgmt003 .res.bad i{background:var(--danger-fill)}.admgmt003 .emp{padding:40px;text-align:center;color:var(--ink3)}.admgmt003 .pg{display:flex;align-items:center;justify-content:flex-end;flex-wrap:wrap;gap:8px 12px;padding:12px 16px;border-top:1px solid var(--line);color:var(--ink2)}.admgmt003 .pg .pb{display:flex;align-items:center;gap:4px}.admgmt003 .pg .pb button{min-width:32px;height:32px;padding:0 6px;border-radius:8px;border:1px solid transparent}.admgmt003 .pg .pb button:hover:not(:disabled){border-color:var(--bd)}.admgmt003 .pg .pb button.on{border-color:var(--p);color:var(--p-text);background:var(--pt);font-weight:600}.admgmt003 .pg .pb button:disabled{opacity:.4;cursor:not-allowed}.admgmt003 .pg .pb span{padding:0 4px;color:var(--ink3)}`,
  html: () => { const q = lgFilter('care', ''); return `<div class="admgmt003"><div class="tb"><div class="l">${seg([['care', '需关注'], ['错误', '错误'], ['警告', '警告'], ['信息', '信息'], ['all', '全部']].map(([k, t]) => [k, `${t}<em>${lgFilter(k, '').length}</em>`]), 'care')}<label class="sq">${ic('search')}<input class="z-in" type="search" placeholder="搜索操作人或内容" aria-label="搜索日志"></label></div><button type="button" class="z-btn" data-toast="已按当前筛选导出 ${q.length} 条">${ic('download')}导出</button></div><div class="tw"><table class="z-tbl"><thead><tr><th style="width:116px">时间</th><th style="width:132px">操作人</th><th style="width:104px">模块</th><th>操作内容</th><th style="width:84px">级别</th><th style="width:84px">结果</th><th style="width:56px"></th></tr></thead><tbody></tbody></table></div><div class="pg"></div></div>` },
  js: (root) => {
    const el = $(root, '.admgmt003'), body = $(el, 'tbody'), pg = $(el, '.pg'); let k = 'care', q = '', page = 1, size = 20; const open = new Set()
    const draw = () => {
      const rows = lgFilter(k, q), n = rows.length, pages = Math.max(1, Math.ceil(n / size)); page = Math.min(page, pages)
      const cur = rows.slice((page - 1) * size, page * size)
      body.innerHTML = cur.length ? cur.map((r) => `<tr class="${open.has(r.id) ? 'open' : ''}" data-id="${r.id}"><td>${r.at}</td><td><span class="z-who">${critter(r.who, 24)}${NAMES[r.who]}</span></td><td>${r.mod}</td><td class="l">${esc(r.act)}</td><td>${tag(r.lv, LG_LV[r.lv])}</td><td><span class="res${r.ok ? '' : ' bad'}"><i></i>${r.ok ? '成功' : '失败'}</span></td><td><button type="button" class="xp" data-xp aria-label="展开详情" aria-expanded="${open.has(r.id)}">${ic('down')}</button></td></tr>${open.has(r.id) ? `<tr class="dtr"><td colspan="7"><dl><div><dt>来源地址</dt><dd>${r.ip}</dd></div><div><dt>使用设备</dt><dd>${r.dev}</dd></div><div><dt>处理耗时</dt><dd>${r.ms} 毫秒</dd></div><div><dt>所属角色</dt><dd>${['店长', '运营专员', '客服', '财务'][r.who % 4]}</dd></div></dl></td></tr>` : ''}`).join('') : `<tr><td colspan="7" class="emp">没有符合条件的日志${q ? '，试试换个关键词' : ''}</td></tr>`
      $$(el, '.z-seg button').forEach((b) => { const kk = b.dataset.t, c = lgFilter(kk, q).length, em = $(b, 'em'); em.textContent = c; em.classList.toggle('z0', c === 0) })
      const bt = pgBtns(page, pages)
      pg.innerHTML = `<span>共 ${n} 条</span>${dd([10, 20, 50, 100].map((x) => [x, x + ' 条/页']), size, { up: true, attr: 'data-sz' })}<div class="pb"><button type="button" data-pn="${page - 1}" ${page <= 1 ? 'disabled' : ''} aria-label="上一页">${ic('left', 's')}</button>${bt.map((x) => (x === '…' ? '<span>…</span>' : `<button type="button" data-pn="${x}" class="${x === page ? 'on' : ''}">${x}</button>`)).join('')}<button type="button" data-pn="${page + 1}" ${page >= pages ? 'disabled' : ''} aria-label="下一页">${ic('right', 's')}</button></div>`
    }
    draw()
    root.addEventListener('click', (e) => {
      const t = e.target.closest('.z-seg [data-t]'); if (t) { k = t.dataset.t; page = 1; draw(); return }
      const x = e.target.closest('[data-xp]'); if (x) { const id = +x.closest('tr').dataset.id; open.has(id) ? open.delete(id) : open.add(id); draw(); return }
      const p = e.target.closest('[data-pn]'); if (p && !p.disabled) { page = +p.dataset.pn; draw(); return }
      const o = e.target.closest('[data-sz] [data-o]'); if (o) { size = +o.dataset.val; page = 1; setTimeout(draw, 0) }
    })
    $(el, '.sq input').addEventListener('input', (e) => { q = e.target.value.trim().toLowerCase(); page = 1; draw() })
  },
})

/* ---- AD-MGMT-004 字典配置表 ---- */
const DC = () => [
  { n: '订单状态', it: [['待付款', '1', 1, 1280], ['待发货', '2', 1, 860], ['配送中', '3', 1, 432], ['已完成', '4', 1, 18204], ['已取消', '5', 1, 2310], ['退款中', '6', 1, 96]] },
  { n: '支付方式', it: [['微信支付', '1', 1, 15820], ['储值余额', '2', 1, 6234], ['到店付款', '3', 0, 0]] },
  { n: '退款原因', it: [['拍错了', '1', 1, 322], ['商品质量问题', '2', 1, 87], ['配送太慢', '3', 1, 41], ['不想要了', '4', 1, 512], ['与描述不符', '5', 1, 63], ['其他', '6', 1, 120]] },
  { n: '会员等级', it: [['普通会员', '1', 1, 9420], ['银卡会员', '2', 1, 2310], ['金卡会员', '3', 1, 586], ['钻石会员', '4', 1, 74]] },
  { n: '配送方式', it: [['骑手配送', '1', 1, 12400], ['快递', '2', 1, 3320], ['到店自提', '3', 1, 1280]] },
].map((d) => ({ ...d, it: d.it.map(([l, v, on, ref]) => ({ l, v, on: !!on, ref })) }))
const dcRows = (d, ed) => d.it.map((x, i) => ed === i ? `<tr class="ed" data-i="${i}"><td>${i + 1}</td><td class="l"><input class="z-in sm" data-f="l" value="${esc(x.l)}" maxlength="12" placeholder="例如：待付款" aria-label="字典标签"><p class="z-er" hidden></p></td><td><input class="z-in sm" data-f="v" value="${esc(x.v)}" maxlength="4" inputmode="numeric" aria-label="字典值" style="width:80px;margin:0 auto"><p class="z-er" hidden></p></td><td>${x.ref ? x.ref.toLocaleString() : '—'}</td><td>${sw(x.on, 'data-sw')}</td><td><button type="button" class="z-btn t" data-act="sv">保存</button><button type="button" class="z-btn t" data-act="cn">取消</button></td></tr>` : `<tr data-i="${i}"><td>${i + 1}</td><td class="l${x.on ? '' : ' off'}">${esc(x.l)}</td><td>${x.v}</td><td>${x.ref ? x.ref.toLocaleString() : '—'}</td><td>${sw(x.on, `data-sw aria-label="启用${esc(x.l)}"`)}</td><td><span class="mvb"><button type="button" class="z-x" data-mv="-1" ${i === 0 ? 'disabled' : ''} aria-label="上移">${ic('arrowup', 's')}</button><button type="button" class="z-x" data-mv="1" ${i === d.it.length - 1 ? 'disabled' : ''} aria-label="下移">${ic('arrowdown', 's')}</button></span><button type="button" class="z-btn t" data-act="ed">编辑</button><button type="button" class="z-btn t d" data-act="del">删除</button></td></tr>`).join('')
def({
  id: 'AD-MGMT-004', name: '字典配置表', style: '行内增删改', wide: true,
  fit: '维护订单状态、退款原因、会员等级等下拉选项：行内编辑、行内新增，启用开关直接生效，被引用的项不能删除只能停用',
  avoid: '字典项上千的大表（要加搜索分页）；有层级的数据（用菜单树配置那类树形组件）',
  kw: '字典 数据字典 行内编辑 新增 删除 启用 停用 下拉选项 枚举 dictionary',
  css: K('admgmt004', 'btn tag in sw modal tbl') + `.admgmt004{width:1100px;max-width:100%;display:grid;grid-template-columns:220px minmax(0,1fr);background:var(--card);border:1px solid var(--line2);border-radius:12px}.admgmt004 .ls{padding:12px;border-right:1px solid var(--line);background:var(--n2);border-radius:12px 0 0 12px;display:flex;flex-direction:column;gap:4px}.admgmt004 .ls h5{margin:4px 8px 8px;font-size:12px;font-weight:400;color:var(--ink3)}.admgmt004 .ls button{display:flex;align-items:center;justify-content:space-between;min-height:44px;padding:0 12px;border-radius:8px;text-align:left}.admgmt004 .ls button:hover{background:var(--n4)}.admgmt004 .ls button.on{background:var(--lift);box-shadow:0 1px 2px var(--sh10);color:var(--p-text);font-weight:600}.admgmt004 .ls .n{font-size:12px;font-weight:400;color:var(--ink3)}.admgmt004 .mn{min-width:0}.admgmt004 .tb{display:flex;align-items:center;justify-content:space-between;gap:12px;padding:14px 20px;border-bottom:1px solid var(--line)}.admgmt004 .tb h4{font-size:16px;font-weight:600}.admgmt004 .tb p{font-size:12px;color:var(--ink3);margin-top:2px}.admgmt004 .z-tbl td{height:52px}.admgmt004 .z-tbl td.off{color:var(--ink3)}.admgmt004 tr.ed td{background:var(--pt)}.admgmt004 tr.ed .z-in{max-width:220px}.admgmt004 tr.ed td.l .z-in{margin:0}.admgmt004 tr.ed .z-er{text-align:left}.admgmt004 .mvb{display:inline-flex;opacity:0;transition:opacity .15s}.admgmt004 tr:hover .mvb,.admgmt004 tr:focus-within .mvb{opacity:1}.admgmt004 .mvb .z-x{width:32px;height:32px}.admgmt004 .mvb .z-x:disabled{opacity:.3;cursor:not-allowed}.admgmt004 tr.out td{opacity:0;transition:opacity .2s}.admgmt004 .rf{color:var(--ink2);line-height:1.6}.admgmt004 .rf b{color:var(--ink)}@media(max-width:820px){.admgmt004{grid-template-columns:minmax(0,1fr)}.admgmt004 .ls{flex-direction:row;overflow-x:auto;border-right:0;border-bottom:1px solid var(--line);border-radius:12px 12px 0 0}.admgmt004 .ls h5{display:none}.admgmt004 .ls button{flex:none;gap:8px}.admgmt004 .mvb{opacity:1}.admgmt004 .z-tbl{min-width:560px}.admgmt004 .tw{overflow-x:auto}}`,
  html: () => { const ds = DC(), d = ds[0]; return `<div class="admgmt004"><div class="ls"><h5>字典</h5>${ds.map((x, i) => `<button type="button" data-d="${i}" class="${i === 0 ? 'on' : ''}"><span>${x.n}</span><span class="n">${x.it.length}</span></button>`).join('')}</div><div class="mn"><div class="tb"><div><h4>${d.n}</h4><p>启用开关直接生效；被业务单据引用的项不能删除，只能停用</p></div><button type="button" class="z-btn p" data-act="add">${ic('plus')}新增一项</button></div><div class="tw"><table class="z-tbl"><thead><tr><th style="width:64px">排序</th><th>字典标签</th><th style="width:120px">字典值</th><th style="width:120px">被引用次数</th><th style="width:88px">启用</th><th style="width:260px">操作</th></tr></thead><tbody>${dcRows(d, -1)}</tbody></table></div></div>${modal('dl', '删除字典项', '<p class="rf"></p>', '<button class="z-btn" type="button" data-close>取消</button><button class="z-btn p" type="button" data-act="dlok">确认删除</button><button class="z-btn p" type="button" data-act="off" hidden>改为停用</button>', 420)}</div>` },
  js: (root) => {
    const el = $(root, '.admgmt004'), body = $(el, 'tbody'), ds = DC(); let di = 0, ed = -1, isNew = false, pend = -1
    const D = () => ds[di]
    const draw = () => { body.innerHTML = dcRows(D(), ed); $$(el, '.ls button').forEach((b, i) => { b.classList.toggle('on', i === di); $(b, '.n').textContent = ds[i].it.length }); $(el, '.tb h4').textContent = D().n; $(el, '[data-act=add]').disabled = ed >= 0 }
    const err = (tr, f, msg) => { const inp = $(tr, `[data-f=${f}]`), p = inp.parentNode.querySelector('.z-er'); inp.classList.toggle('er', !!msg); p.hidden = !msg; p.textContent = msg || ''; return !msg }
    root.addEventListener('click', (e) => {
      const db = e.target.closest('[data-d]'); if (db) { di = +db.dataset.d; ed = -1; draw(); return }
      const sg = e.target.closest('[data-sw]'); if (sg && ed < 0) { const i = +sg.closest('tr').dataset.i, x = D().it[i]; x.on = !x.on; draw(); toast(root, x.on ? `已启用「${x.l}」` : `已停用「${x.l}」，新单据不再出现该选项`); return }
      const mv = e.target.closest('[data-mv]'); if (mv && !mv.disabled) { const i = +mv.closest('tr').dataset.i, j = i + +mv.dataset.mv; D().it.splice(j, 0, D().it.splice(i, 1)[0]); draw(); return }
      const a = e.target.closest('[data-act]'); if (!a) return
      const act = a.dataset.act, tr = a.closest('tr')
      if (act === 'add') { const it = D().it; it.push({ l: '', v: String(Math.max(0, ...it.map((x) => +x.v || 0)) + 1), on: true, ref: 0 }); ed = it.length - 1; isNew = true; draw(); $(body, '[data-f=l]').focus() }
      if (act === 'ed') { ed = +tr.dataset.i; isNew = false; draw(); $(body, '[data-f=l]').focus() }
      if (act === 'cn') { if (isNew) D().it.pop(); ed = -1; isNew = false; draw() }
      if (act === 'sv') {
        const l = $(tr, '[data-f=l]').value.trim(), v = $(tr, '[data-f=v]').value.trim(), i = +tr.dataset.i
        const ok1 = err(tr, 'l', l ? (D().it.some((x, k) => k !== i && x.l === l) ? '标签已存在' : '') : '请填写标签'), ok2 = err(tr, 'v', v ? (D().it.some((x, k) => k !== i && x.v === v) ? '值已被使用' : '') : '请填写值')
        if (ok1 && ok2) { Object.assign(D().it[i], { l, v }); ed = -1; isNew = false; draw(); toast(root, '已保存') }
      }
      if (act === 'del') { pend = +tr.dataset.i; const x = D().it[pend], bad = x.ref > 0; $(el, '.rf').innerHTML = bad ? `「<b>${esc(x.l)}</b>」已被 <b>${x.ref.toLocaleString()}</b> 条记录引用，删除会导致这些记录显示异常，所以不能删除。<br>可以改为停用：已有记录不受影响，新单据不再出现这个选项。` : `确认删除「<b>${esc(x.l)}</b>」？暂无记录引用它，删除后不能恢复。`; $(el, '[data-act=dlok]').hidden = bad; $(el, '[data-act=off]').hidden = !bad; openOv(root, 'dl') }
      if (act === 'dlok') { closeOv(a); const x = D().it.splice(pend, 1)[0]; draw(); toast(root, `已删除「${x.l}」`) }
      if (act === 'off') { closeOv(a); const x = D().it[pend]; x.on = false; draw(); toast(root, `已停用「${x.l}」`) }
    })
    root.addEventListener('keydown', (e) => { if (e.key === 'Enter' && e.target.matches('tr.ed input')) $(e.target.closest('tr'), '[data-act=sv]').click(); if (e.key === 'Escape' && ed >= 0) $(body, '[data-act=cn]').click(); if ((e.key === ' ' || e.key === 'Enter') && e.target.matches('.z-sw')) { e.preventDefault(); e.target.click() } })
    wireEsc(root)
  },
})

/* ---- AD-MGMT-005 通知设置 ---- */
const NT = [
  ['订单', [['new', '新订单提醒', '有人下单并付款后通知', [1, 0, 1]], ['rf', '退款申请', '买家提交退款申请时通知', [1, 1, 1]], ['late', '订单超时未发货', '超过承诺发货时间仍未发货时通知', [1, 1, 0]]]],
  ['库存与商品', [['stk', '库存低于预警值', '商品库存低于预警线时通知仓管', [1, 0, 1]], ['audit', '商品审核结果', '上架审核通过或驳回时通知', [1, 0, 0]]]],
  ['资金', [['rc', '储值充值到账', '会员储值充值成功后通知财务', [1, 0, 0]], ['wd', '提现与结算', '提现申请与结算单生成时通知', [1, 0, 0]]]],
]
const NT_CH = ['站内信', '短信', '企业微信']
const NT_FAIL = { 'wd.1': '短信签名正在审核，预计 1 个工作日内通过，暂时无法开启', 'wd.2': '尚未绑定企业微信，绑定后才能开启' }
const ntRows = (st, errs) => NT.map(([g, rows]) => `<tr class="gr"><td colspan="4">${g}</td></tr>` + rows.map(([k, t, d]) => `<tr class="${errs[k] ? 'er' : ''}"><td class="l"><b>${t}</b><span>${d}</span>${errs[k] ? `<em class="ern">${ic('info', 's')}${errs[k]}</em>` : ''}</td>${NT_CH.map((c, i) => `<td>${sw(st[k][i], `data-n="${k}.${i}" aria-label="${t}·${c}"`)}</td>`).join('')}</tr>`).join('')).join('')
def({
  id: 'AD-MGMT-005', name: '通知设置', style: '开关即生效', wide: false,
  fit: '员工消息订阅：按事项与渠道的开关矩阵，点开关立即保存并轻提示；失败时回滚并在该行写清原因，另有免打扰时段',
  avoid: '需要填写大量内容的复杂配置（用系统参数的保存模式）；只有一个总开关时（直接用单个开关）',
  kw: '通知 设置 开关 订阅 短信 站内信 企业微信 免打扰 即时保存 失败回滚',
  css: K('admgmt005', 'btn tag sw in') + `.admgmt005{width:640px;max-width:100%;background:var(--card);border:1px solid var(--line2);border-radius:12px;overflow:hidden}.admgmt005 .hd{display:flex;align-items:center;justify-content:space-between;gap:12px;padding:16px 20px;border-bottom:1px solid var(--line)}.admgmt005 .hd h4{font-size:16px;font-weight:600}.admgmt005 .hd p{font-size:12px;color:var(--ink3);margin-top:2px}.admgmt005 .sv{display:inline-flex;align-items:center;gap:6px;font-size:12px;color:var(--ink3);white-space:nowrap}.admgmt005 .sv.ok{color:var(--ok)}.admgmt005 .sv.bad{color:var(--dg)}.admgmt005 table{width:100%;border-collapse:collapse}.admgmt005 th{height:40px;padding:0 8px;text-align:center;font-weight:600;color:var(--ink2);background:var(--n2);border-bottom:1px solid var(--line);white-space:nowrap}.admgmt005 th:first-child{width:auto}.admgmt005 tr.gr td{height:36px;padding:0 20px;background:var(--n1);font-size:12px;color:var(--ink3);border-bottom:1px solid var(--line)}.admgmt005 td{padding:12px 8px;text-align:center;border-bottom:1px solid var(--line);vertical-align:middle}.admgmt005 td.l{text-align:left;padding-left:20px}.admgmt005 td.l b{display:block;font-weight:600}.admgmt005 td.l span{display:block;font-size:12px;color:var(--ink3);margin-top:2px}.admgmt005 td.l .ern{display:flex;align-items:flex-start;gap:6px;margin-top:6px;font-style:normal;font-size:12px;color:var(--dg);line-height:1.5;animation:zbin .2s cubic-bezier(.2,0,0,1)}.admgmt005 td.l .ern .z-ic{margin-top:1px}.admgmt005 tr.er td.l b{color:var(--dg)}.admgmt005 .dnd{display:flex;align-items:center;justify-content:space-between;flex-wrap:wrap;gap:10px 16px;padding:14px 20px}.admgmt005 .dnd b{display:block;font-weight:600}.admgmt005 .dnd span.s{display:block;font-size:12px;color:var(--ink3);margin-top:2px}.admgmt005 .dnd .tm{display:flex;align-items:center;gap:8px;color:var(--ink2)}.admgmt005 .dnd select{width:92px;height:32px}.admgmt005 .dnd.off .tm{opacity:.45;pointer-events:none}@media(max-width:520px){.admgmt005 th:not(:first-child){width:62px!important;padding:0 2px;font-size:12px}.admgmt005 td{padding:12px 2px}.admgmt005 td.l{padding-left:14px}}`,
  html: () => { const st = Object.fromEntries(NT.flatMap(([, rs]) => rs.map(([k, , , v]) => [k, v]))); const time = (id, cur) => `<select class="z-in" data-t="${id}" aria-label="${id === 's' ? '开始时间' : '结束时间'}">${['20:00', '21:00', '22:00', '23:00', '06:00', '07:00', '08:00', '09:00'].map((t) => `<option${t === cur ? ' selected' : ''}>${t}</option>`).join('')}</select>`; return `<div class="admgmt005"><div class="hd"><div><h4>消息通知</h4><p>点开关立即保存，不需要再点保存</p></div><span class="sv ok">${ic('checkc', 's')}已是最新</span></div><table><thead><tr><th>通知事项</th>${NT_CH.map((c) => `<th style="width:84px">${c}</th>`).join('')}</tr></thead><tbody>${ntRows(st, {})}</tbody></table><div class="dnd"><div><b>免打扰时段</b><span class="s">时段内只发站内信，短信和企业微信暂缓到时段结束</span></div><div class="tm">${sw(true, 'data-dnd aria-label="免打扰"')}${time('s', '22:00')}<span>至</span>${time('e', '08:00')}</div></div></div>` },
  js: (root) => {
    const el = $(root, '.admgmt005'), body = $(el, 'tbody'), tip = $(el, '.sv'); let st = Object.fromEntries(NT.flatMap(([, rs]) => rs.map(([k, , , v]) => [k, [...v]]))), errs = {}; const busy = new Set()
    const mark = (cls, html) => { tip.className = 'sv ' + cls; tip.innerHTML = html }
    const save = (done) => { mark('', '<i class="z-spin"></i>保存中…'); setTimeout(() => { mark('ok', ic('checkc', 's') + '已保存 · 刚刚'); done && done() }, 520) }
    root.addEventListener('click', (e) => {
      const s = e.target.closest('[data-n]'); if (s) {
        const [k, i] = s.dataset.n.split('.'), key = s.dataset.n; if (busy.has(key)) return
        const next = !st[k][+i]
        if (next && NT_FAIL[key]) { busy.add(key); s.classList.add('busy', 'on'); mark('', '<i class="z-spin"></i>保存中…'); setTimeout(() => { busy.delete(key); errs = {}; errs[k] = NT_FAIL[key]; body.innerHTML = ntRows(st, errs); mark('bad', ic('alert', 's') + '有 1 项没有保存成功') }, 520); return }
        busy.add(key); s.classList.add('busy'); s.classList.toggle('on', next); st[k][+i] = next ? 1 : 0; errs = {}; $$(el, '.ern').forEach((x) => x.remove()); $$(el, 'tr.er').forEach((x) => x.classList.remove('er'))
        mark('', '<i class="z-spin"></i>保存中…'); setTimeout(() => { busy.delete(key); s.classList.remove('busy'); s.setAttribute('aria-checked', next); mark('ok', ic('checkc', 's') + '已保存 · 刚刚'); toast(root, next ? '已开启' : '已关闭') }, 520); return
      }
      const d = e.target.closest('[data-dnd]'); if (d) { const on = d.classList.toggle('on'); d.setAttribute('aria-checked', on); d.closest('.dnd').classList.toggle('off', !on); save(() => toast(root, on ? '免打扰已开启' : '免打扰已关闭')) }
    })
    root.addEventListener('change', (e) => { if (e.target.matches('[data-t]')) save(() => toast(root, '免打扰时段已更新')) })
    root.addEventListener('keydown', (e) => { if ((e.key === ' ' || e.key === 'Enter') && e.target.matches('.z-sw')) { e.preventDefault(); e.target.click() } })
  },
})

/* ---- AD-MGMT-006 个人资料 ---- */
const PF = { nick: '林小满', av: 0, mail: 'linxiaoman@example.com', sign: '把每一单都当成第一单。', phone: '138****5678' }
def({
  id: 'AD-MGMT-006', name: '个人资料', style: '头像与昵称', wide: false,
  fit: '账号中心里改头像、昵称、邮箱与签名：默认动物头像可选，昵称实时校验，顶部预览即时变化，改完才允许保存',
  avoid: '需要上传真人照片并裁剪的场景（另做上传组件）；实名、证件等敏感信息（要独立流程与二次验证）',
  kw: '个人资料 账号 头像 昵称 邮箱 签名 校验 保存 profile 动物头像',
  css: K('admgmt006', 'btn tag in') + `.admgmt006{width:640px;max-width:100%;background:var(--card);border:1px solid var(--line2);border-radius:12px;overflow:hidden}.admgmt006 .pv{display:flex;align-items:center;gap:16px;padding:20px;background:linear-gradient(180deg,var(--pt),var(--card))}.admgmt006 .pv .big{border-radius:50%;box-shadow:0 0 0 3px var(--card),0 2px 8px var(--sh12)}.admgmt006 .pv b{display:block;font-size:18px;font-weight:600;line-height:1.4;overflow-wrap:anywhere}.admgmt006 .pv span.s{display:block;font-size:12px;color:var(--ink2);margin-top:2px}.admgmt006 .fm{display:flex;flex-direction:column;gap:18px;padding:20px}.admgmt006 .fd .z-lb{display:block;margin-bottom:8px}.admgmt006 .avs{display:flex;gap:12px;flex-wrap:wrap}.admgmt006 .avs button{position:relative;width:56px;height:56px;border-radius:50%;padding:0;transition:box-shadow .15s,transform .15s cubic-bezier(.2,0,0,1)}.admgmt006 .avs button:hover{transform:translateY(-1px)}.admgmt006 .avs button.on{box-shadow:0 0 0 2px var(--card),0 0 0 4px var(--p)}.admgmt006 .avs button.on::after{content:"";position:absolute;right:-2px;bottom:-2px;width:18px;height:18px;border-radius:50%;background:var(--p) url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='none' stroke='%23fff' stroke-width='3.500' stroke-linecap='round' stroke-linejoin='round'%3E%3Cpath d='m5 12.500 4.500 4.500L19 7.500'/%3E%3C/svg%3E") center/11px no-repeat;border:2px solid var(--card)}.admgmt006 .sm{font-size:12px;color:var(--ink3);margin-top:6px}.admgmt006 .wr{position:relative}.admgmt006 .wr .cnt{position:absolute;right:10px;top:9px;font-size:12px;color:var(--ink3);font-variant-numeric:tabular-nums}.admgmt006 .wr textarea+.cnt{top:auto;bottom:8px}.admgmt006 .wr .z-in{padding-right:56px}.admgmt006 .ln{display:flex;align-items:center;justify-content:space-between;gap:12px;height:36px}.admgmt006 .ln .z-in{flex:1}.admgmt006 .ft{display:flex;align-items:center;justify-content:space-between;gap:12px;padding:14px 20px;border-top:1px solid var(--line);background:var(--n2)}.admgmt006 .ft .l{font-size:12px;color:var(--ink3)}.admgmt006 .ft .r{display:flex;gap:8px}.admgmt006 .tgs{display:flex;gap:8px;align-items:center;flex-wrap:wrap}`,
  html: () => `<div class="admgmt006"><div class="pv"><span class="pav">${critter(0, 72).replace('class="av"', 'class="av big"')}</span><div><b class="pn">${PF.nick}</b><span class="s">运营部 · 运营专员</span><span class="s">上次登录：今天 09:12</span></div></div><div class="fm"><div class="fd"><label class="z-lb">头像</label><div class="avs" role="radiogroup" aria-label="选择头像">${[0, 1, 2, 3].map((i) => `<button type="button" role="radio" aria-checked="${i === PF.av}" data-av="${i}" class="${i === PF.av ? 'on' : ''}" aria-label="动物头像 ${i + 1}">${critter(i, 56)}</button>`).join('')}</div><p class="sm">没有上传照片时使用卡通动物头像，选一个喜欢的</p></div><div class="fd"><label class="z-lb z-req" for="admgmt006-n">昵称</label><div class="wr"><input id="admgmt006-n" class="z-in" data-f="nick" maxlength="12" value="${PF.nick}" autocomplete="off"><span class="cnt">${PF.nick.length}/12</span></div><p class="z-er" hidden></p></div><div class="fd"><label class="z-lb">手机号</label><div class="ln"><span>${PF.phone}</span><button type="button" class="z-btn t" data-act="phone">更换</button></div></div><div class="fd"><label class="z-lb" for="admgmt006-m">邮箱</label><input id="admgmt006-m" class="z-in" data-f="mail" value="${PF.mail}" autocomplete="off"><p class="z-er" hidden></p></div><div class="fd"><label class="z-lb">所属部门与角色</label><div class="tgs">${tag('运营部')}${tag('运营专员', 'in')}</div><p class="sm">由管理员分配，不能自己修改</p></div><div class="fd"><label class="z-lb" for="admgmt006-s">个性签名</label><div class="wr"><textarea id="admgmt006-s" class="z-in" data-f="sign" rows="2" maxlength="40">${PF.sign}</textarea><span class="cnt">${PF.sign.length}/40</span></div></div></div><div class="ft"><span class="l">修改后点保存才会生效</span><div class="r"><button type="button" class="z-btn" data-act="undo" disabled>撤销修改</button><button type="button" class="z-btn p" data-act="save" disabled>保存</button></div></div></div>`,
  js: (root) => {
    const el = $(root, '.admgmt006'); let base = { ...PF }, v = { ...PF }
    const fields = { nick: $(el, '[data-f=nick]'), mail: $(el, '[data-f=mail]'), sign: $(el, '[data-f=sign]') }
    const bad = { nick: (x) => (!x.trim() ? '请输入昵称' : x.trim().length < 2 ? '昵称至少 2 个字' : /管理员|admin/i.test(x) ? '昵称不能使用「管理员」' : ''), mail: (x) => (x && !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(x) ? '邮箱格式不正确' : '') }
    const showErr = (f, m) => { const p = fields[f].closest('.fd').querySelector('.z-er'); fields[f].classList.toggle('er', !!m); if (p) { p.hidden = !m; p.textContent = m } }
    const sync = () => {
      const dirty = ['nick', 'mail', 'sign', 'av'].some((k) => v[k] !== base[k]), ok = !bad.nick(v.nick) && !bad.mail(v.mail)
      $(el, '[data-act=save]').disabled = !(dirty && ok); $(el, '[data-act=undo]').disabled = !dirty; $(el, '.ft .l').textContent = dirty ? (ok ? '有未保存的修改' : '请先修正标红的内容') : '修改后点保存才会生效'
    }
    el.addEventListener('input', (e) => {
      const f = e.target.dataset.f; if (!f) return; v[f] = e.target.value
      const c = e.target.parentNode.querySelector('.cnt'); if (c) c.textContent = e.target.value.length + '/' + e.target.maxLength
      if (bad[f]) showErr(f, bad[f](e.target.value))
      if (f === 'nick') $(el, '.pn').textContent = v.nick.trim() || '未命名'
      sync()
    })
    el.addEventListener('click', (e) => {
      const a = e.target.closest('[data-av]'); if (a) { v.av = +a.dataset.av; $$(el, '[data-av]').forEach((b) => { b.classList.toggle('on', b === a); b.setAttribute('aria-checked', b === a) }); $(el, '.pav').innerHTML = critter(v.av, 72).replace('class="av"', 'class="av big"'); sync(); return }
      const b = e.target.closest('[data-act]'); if (!b) return
      if (b.dataset.act === 'save') { base = { ...v }; sync(); toast(root, '资料已保存') }
      if (b.dataset.act === 'undo') { v = { ...base }; fields.nick.value = v.nick; fields.mail.value = v.mail; fields.sign.value = v.sign; ['nick', 'mail', 'sign'].forEach((f) => { showErr(f, ''); const c = fields[f].parentNode.querySelector('.cnt'); if (c) c.textContent = v[f].length + '/' + fields[f].maxLength }); $$(el, '[data-av]').forEach((x) => { x.classList.toggle('on', +x.dataset.av === v.av); x.setAttribute('aria-checked', +x.dataset.av === v.av) }); $(el, '.pav').innerHTML = critter(v.av, 72).replace('class="av"', 'class="av big"'); $(el, '.pn').textContent = v.nick; sync(); toast(root, '已撤销修改') }
      if (b.dataset.act === 'phone') toast(root, '更换手机号需要短信验证，示例中不演示')
    })
    sync()
  },
})

/* ---- AD-MGMT-007 系统参数 ---- */
const SP_TABS = [['base', '基础'], ['trade', '交易'], ['sec', '安全']]
const SP = () => ({
  base: [
    { k: 'name', t: '系统名称', d: '显示在登录页和浏览器标签上', ty: 'text', v: '示例商城后台', def: '示例商城后台', max: 16 },
    { k: 'ps', t: '列表默认每页条数', d: '新打开的列表按这个数量分页', ty: 'sel', v: '20 条', def: '20 条', opts: ['10 条', '20 条', '50 条', '100 条'] },
    { k: 'keep', t: '操作日志保留时间', d: '超过期限的日志会自动归档', ty: 'sel', v: '180 天', def: '180 天', opts: ['90 天', '180 天', '365 天'] },
  ],
  trade: [
    { k: 'close', t: '订单自动关闭', d: '下单后超过该时间仍未付款，订单自动关闭并释放库存', ty: 'num', v: 30, def: 30, min: 5, max: 120, step: 5, unit: '分钟' },
    { k: 'recv', t: '自动确认收货', d: '发货后超过该天数买家仍未操作，系统自动确认收货', ty: 'num', v: 10, def: 10, min: 3, max: 30, step: 1, unit: '天', money: '影响订单进入「可结算」的时间' },
    { k: 'aft', t: '售后申请期限', d: '确认收货后买家可申请售后的天数', ty: 'num', v: 7, def: 7, min: 0, max: 30, step: 1, unit: '天', money: '影响买家可申请退款的范围' },
    { k: 'lim', t: '单笔订单最多购买件数', d: '超过时提示并拦截下单', ty: 'num', v: 99, def: 99, min: 1, max: 999, step: 1, unit: '件' },
  ],
  sec: [
    { k: 'lock', t: '登录失败锁定次数', d: '连续输错密码达到次数后锁定账号 15 分钟', ty: 'num', v: 5, def: 5, min: 3, max: 10, step: 1, unit: '次' },
    { k: 'sess', t: '会话超时', d: '无操作超过该时间需要重新登录', ty: 'num', v: 30, def: 30, min: 10, max: 240, step: 10, unit: '分钟' },
    { k: 'pw', t: '密码最小长度', d: '新设置的密码不能短于该位数', ty: 'num', v: 8, def: 8, min: 6, max: 20, step: 1, unit: '位' },
    { k: 'chg', t: '首次登录强制改密', d: '新建账号首次登录必须修改初始密码', ty: 'sw', v: true, def: true },
    { k: 'mfa', t: '登录二次验证', d: '开启后登录需要再输入短信验证码', ty: 'sw', v: false, def: false },
  ],
})
const spCtl = (p) => p.ty === 'num' ? `<div class="nm"><button type="button" class="z-x" data-d="-1" aria-label="减少">${ic('minus', 's')}</button><input class="z-in sm" inputmode="numeric" value="${p.v}" aria-label="${p.t}"><button type="button" class="z-x" data-d="1" aria-label="增加">${ic('plus', 's')}</button><em>${p.unit}</em></div>` : p.ty === 'sw' ? sw(p.v, `data-sw aria-label="${p.t}"`) : p.ty === 'sel' ? `<select class="z-in sm" aria-label="${p.t}">${p.opts.map((o) => `<option${o === p.v ? ' selected' : ''}>${o}</option>`).join('')}</select>` : `<input class="z-in sm" value="${esc(p.v)}" maxlength="${p.max}" aria-label="${p.t}">`
const spRow = (p) => `<div class="rw" data-k="${p.k}"><div class="lb"><b>${p.t}${p.money ? tag('影响资金', 'wn') : ''}<i class="chg" hidden title="已修改，未保存"></i></b><span>${p.d}</span><p class="z-er" hidden></p></div><div class="ct">${spCtl(p)}<button type="button" class="z-btn t rs" data-act="rs" hidden>恢复默认</button></div></div>`
def({
  id: 'AD-MGMT-007', name: '系统参数', style: '分组保存重置', wide: false,
  fit: '运行规则与阈值的集中设置：按基础 / 交易 / 安全分组，改过的行打小点，可单项恢复默认；影响资金的项保存前弹出改前改后确认',
  avoid: '会频繁变动的运营内容（营业时间、公告、优惠券放业务页）；需要审批发布的配置（要带版本与审批流）',
  kw: '系统参数 设置 配置 阈值 保存 重置 恢复默认 步进 分组 改前改后',
  css: K('admgmt007', 'btn tag sw in tabs modal') + `.admgmt007{position:relative;width:640px;max-width:100%;background:var(--card);border:1px solid var(--line2);border-radius:12px;overflow:hidden}.admgmt007 .z-tabs{padding:0 20px}.admgmt007 .pl{min-height:340px}.admgmt007 .rw{display:flex;align-items:center;justify-content:space-between;gap:20px;padding:16px 20px;border-bottom:1px solid var(--line)}.admgmt007 .lb{flex:1;min-width:0}.admgmt007 .lb b{display:flex;align-items:center;gap:8px;font-weight:600}.admgmt007 .lb span{display:block;font-size:12px;color:var(--ink3);margin-top:2px;line-height:1.5}.admgmt007 .chg{width:6px;height:6px;border-radius:50%;background:var(--warn-fill)}.admgmt007 .ct{display:flex;align-items:center;gap:8px;flex:none}.admgmt007 .ct .z-in{width:156px}.admgmt007 .nm{display:flex;align-items:center;gap:4px}.admgmt007 .nm .z-in{width:64px;text-align:center;padding:0 4px}.admgmt007 .nm .z-x{width:32px;height:32px;border:1px solid var(--bd)}.admgmt007 .nm .z-x:hover{border-color:var(--ink3)}.admgmt007 .nm .z-x:disabled{opacity:.4;cursor:not-allowed}.admgmt007 .nm em{font-style:normal;color:var(--ink2);margin-left:4px;min-width:28px}.admgmt007 .ft{display:flex;align-items:center;justify-content:space-between;gap:12px;padding:14px 20px;background:var(--n2)}.admgmt007 .ft .l{font-size:12px;color:var(--ink3)}.admgmt007 .ft .r{display:flex;gap:8px}.admgmt007 .cmp{display:flex;flex-direction:column;gap:10px}.admgmt007 .cmp .it{padding:12px 14px;border-radius:8px;background:var(--n2);line-height:1.6}.admgmt007 .cmp .it b{font-weight:600}.admgmt007 .cmp .ar{color:var(--ink3);margin:0 6px}.admgmt007 .cmp .im{display:block;font-size:12px;color:var(--wn)}@media(max-width:520px){.admgmt007 .rw{flex-direction:column;align-items:stretch;gap:10px}.admgmt007 .ct{justify-content:space-between}}`,
  html: () => { const d = SP(); return `<div class="admgmt007">${tabs(SP_TABS, 'base', 'data-g="sp"')}${SP_TABS.map(([k]) => `<div class="pl" data-p="${k}" data-g="sp" ${k === 'base' ? '' : 'hidden'}>${d[k].map(spRow).join('')}</div>`).join('')}<div class="ft"><span class="l">没有未保存的修改</span><div class="r"><button type="button" class="z-btn" data-act="reset" disabled>撤销修改</button><button type="button" class="z-btn p" data-act="save" disabled>保存</button></div></div>${modal('cf', '确认修改影响资金的参数', '<div class="cmp"></div>', '<button class="z-btn" type="button" data-close>再想想</button><button class="z-btn p" type="button" data-act="cfok">确认保存</button>', 460)}</div>` },
  js: (root) => {
    const el = $(root, '.admgmt007'); const d = SP(); const all = Object.values(d).flat(), saved = Object.fromEntries(all.map((p) => [p.k, p.v]))
    const P = (k) => all.find((p) => p.k === k)
    const row = (k) => $(el, `.rw[data-k="${k}"]`)
    const paint = (k) => {
      const p = P(k), r = row(k), ch = p.v !== saved[k]
      $(r, '.chg').hidden = !ch; $(r, '.rs').hidden = p.v === p.def
      if (p.ty === 'num') { $(r, 'input').value = p.v; $$(r, '.z-x').forEach((b) => (b.disabled = (+b.dataset.d < 0 && p.v <= p.min) || (+b.dataset.d > 0 && p.v >= p.max))) } else if (p.ty === 'sw') { $(r, '.z-sw').classList.toggle('on', p.v); $(r, '.z-sw').setAttribute('aria-checked', p.v) } else $(r, '.z-in').value = p.v
      const n = all.filter((x) => x.v !== saved[x.k]).length; $(el, '.ft .l').textContent = n ? `已修改 ${n} 项，还没有保存` : '没有未保存的修改'; $(el, '[data-act=save]').disabled = !n; $(el, '[data-act=reset]').disabled = !n
    }
    all.forEach((p) => paint(p.k))
    const set = (k, v) => { const p = P(k); if (p.ty === 'num') { const c = Math.max(p.min, Math.min(p.max, +v || p.min)); const e = $(row(k), '.z-er'); e.hidden = !(+v < p.min || +v > p.max); e.textContent = `可设置范围 ${p.min}–${p.max} ${p.unit}，已自动调整`; p.v = c } else p.v = v; paint(k) }
    root.addEventListener('click', (e) => {
      const r = e.target.closest('.rw'), k = r && r.dataset.k
      const b = e.target.closest('[data-d]'); if (b && r && !b.disabled) { const p = P(k); $(r, '.z-er').hidden = true; set(k, p.v + +b.dataset.d * p.step); return }
      const s = e.target.closest('[data-sw]'); if (s && r) { set(k, !P(k).v); return }
      const a = e.target.closest('[data-act]'); if (!a) return
      if (a.dataset.act === 'rs' && r) { $(r, '.z-er').hidden = true; set(k, P(k).def); toast(root, `已恢复「${P(k).t}」的默认值`) }
      if (a.dataset.act === 'reset') { all.forEach((p) => { p.v = saved[p.k]; $(row(p.k), '.z-er').hidden = true; paint(p.k) }); toast(root, '已撤销修改') }
      if (a.dataset.act === 'save') {
        const ch = all.filter((p) => p.v !== saved[p.k]), mo = ch.filter((p) => p.money)
        if (mo.length) { $(el, '.cmp').innerHTML = mo.map((p) => `<div class="it"><b>${p.t}</b><br>${saved[p.k]} ${p.unit}<span class="ar">→</span>${p.v} ${p.unit}<span class="im">${p.money}，只对之后的订单生效</span></div>`).join('') + (ch.length > mo.length ? `<p style="color:var(--ink3);font-size:12px">另有 ${ch.length - mo.length} 项普通参数一并保存</p>` : ''); openOv(root, 'cf'); return }
        ch.forEach((p) => (saved[p.k] = p.v)); all.forEach((p) => paint(p.k)); toast(root, `已保存 ${ch.length} 项`)
      }
      if (a.dataset.act === 'cfok') { const ch = all.filter((p) => p.v !== saved[p.k]); closeOv(a); ch.forEach((p) => (saved[p.k] = p.v)); all.forEach((p) => paint(p.k)); toast(root, `已保存 ${ch.length} 项`) }
    })
    root.addEventListener('change', (e) => { const r = e.target.closest('.rw'); if (!r || !e.target.matches('input,select')) return; const p = P(r.dataset.k); set(p.k, p.ty === 'num' ? e.target.value : e.target.value) })
    root.addEventListener('input', (e) => { const r = e.target.closest('.rw'); if (r && P(r.dataset.k).ty === 'text') { P(r.dataset.k).v = e.target.value; const k = r.dataset.k, ch = P(k).v !== saved[k]; $(r, '.chg').hidden = !ch; $(r, '.rs').hidden = P(k).v === P(k).def; const n = all.filter((x) => x.v !== saved[x.k]).length; $(el, '.ft .l').textContent = n ? `已修改 ${n} 项，还没有保存` : '没有未保存的修改'; $(el, '[data-act=save]').disabled = !n; $(el, '[data-act=reset]').disabled = !n } })
    root.addEventListener('keydown', (e) => { if ((e.key === ' ' || e.key === 'Enter') && e.target.matches('.z-sw')) { e.preventDefault(); e.target.click() } })
    wireEsc(root)
  },
})

/* ---- AD-MGMT-008 会话与登录日志 ---- */
const SS = () => [
  { id: 1, who: 4, role: '仓管', dev: 'bz_mobile', env: 'Chrome · Android', ip: '36.110.5.14', city: '北京', at: '前天 20:40', act: '闲置 1 天', st: '闲置', abn: true },
  { id: 2, who: 3, role: '财务', dev: 'bz_desktop', env: 'Chrome 125 · Windows 10', ip: '180.157.33.92', city: '苏州', at: '今天 09:02', act: '闲置 47 分钟', st: '闲置' },
  { id: 3, who: 1, role: '运营专员', dev: 'bz_mobile', env: 'Safari · iPhone', ip: '117.136.40.7', city: '上海', at: '昨天 18:12', act: '3 小时前', st: '在线' },
  { id: 4, who: 1, role: '运营专员', dev: 'bz_desktop', env: 'Edge 126 · Windows 10', ip: '61.172.8.19', city: '上海', at: '今天 09:30', act: '2 分钟前', st: '在线' },
  { id: 5, who: 2, role: '客服', dev: 'bz_desktop', env: 'Chrome 126 · macOS', ip: '114.80.67.201', city: '杭州', at: '今天 08:05', act: '8 分钟前', st: '在线' },
  { id: 6, who: 0, role: '店长', dev: 'bz_desktop', env: 'Chrome 126 · Windows 11', ip: '218.4.21.36', city: '上海', at: '今天 08:52', act: '刚刚', st: '当前会话', cur: true },
]
const LGI = [
  ['今天 09:30', 1, '成功', '上海', 'Edge 126 · Windows 10', ''], ['今天 09:02', 3, '成功', '苏州', 'Chrome 125 · Windows 10', ''], ['今天 08:41', 7, '失败', '上海', 'Chrome 126 · Windows 11', '密码错误，连续 3 次，账号已锁定 15 分钟'],
  ['今天 08:40', 7, '失败', '上海', 'Chrome 126 · Windows 11', '密码错误'], ['今天 08:05', 2, '成功', '杭州', 'Chrome 126 · macOS', ''], ['前天 20:40', 4, '成功', '北京', 'Chrome · Android', '常用地为上海，本次为异地登录'],
  ['昨天 18:12', 1, '成功', '上海', 'Safari · iPhone', ''], ['昨天 09:10', 0, '成功', '上海', 'Chrome 126 · Windows 11', ''], ['昨天 08:58', 5, '失败', '无锡', 'Firefox 127 · Windows 10', '验证码错误'], ['11-02 17:46', 6, '成功', '上海', 'Chrome 126 · Windows 11', ''],
]
def({
  id: 'AD-MGMT-008', name: '会话与登录日志', style: '强制下线', wide: true,
  fit: '安全管理：在线会话列表可单个或批量强制下线（当前会话不能下线），登录记录默认只看失败与异地等异常',
  avoid: '没有会话概念的纯 Token 接口系统；需要风控规则与自动封禁时（要另做安全策略页）',
  kw: '会话 登录日志 强制下线 在线 设备 异地登录 失败 session login 踢下线',
  css: K('admgmt008', 'btn tag ck tabs seg tbl modal') + `.admgmt008{position:relative;width:1100px;max-width:100%;background:var(--card);border:1px solid var(--line2);border-radius:12px}.admgmt008 .z-tabs{padding:0 20px}.admgmt008 .tb{display:flex;align-items:center;justify-content:space-between;flex-wrap:wrap;gap:10px 16px;padding:12px 16px;border-bottom:1px solid var(--line);min-height:57px}.admgmt008 .tb .hnt{font-size:12px;color:var(--ink3)}.admgmt008 .bbar{display:flex;align-items:center;gap:12px;color:var(--ink2)}.admgmt008 .bbar b{color:var(--ink)}.admgmt008 .tw{overflow-x:auto}.admgmt008 .z-tbl{min-width:860px}.admgmt008 .z-tbl td{height:56px}.admgmt008 .z-tbl td.l{overflow-wrap:anywhere}.admgmt008 .who{display:inline-flex;align-items:center;gap:10px;text-align:left}.admgmt008 .who span{display:flex;flex-direction:column;line-height:1.35}.admgmt008 .who em{font-style:normal;font-size:12px;color:var(--ink3)}.admgmt008 .dv{display:inline-flex;align-items:center;gap:8px;color:var(--ink2)}.admgmt008 .ip{display:inline-flex;flex-direction:column;align-items:center;line-height:1.4}.admgmt008 .ip em{font-style:normal;font-size:12px;color:var(--ink3)}.admgmt008 tr.out td{opacity:0;transition:opacity .22s}.admgmt008 .emp{padding:40px;text-align:center;color:var(--ink3)}.admgmt008 .z-seg button em{margin-left:4px;font-style:normal;font-size:12px;color:var(--ink3)}.admgmt008 .z-seg button.on em{color:var(--p-text)}.admgmt008 .kl{display:flex;flex-direction:column;gap:8px;line-height:1.6;color:var(--ink2)}.admgmt008 .kl b{color:var(--ink);font-weight:600}.admgmt008 .kl ul{display:flex;flex-direction:column;gap:6px;margin-top:4px}.admgmt008 .kl li{display:flex;align-items:center;gap:8px;color:var(--ink)}`,
  html: () => { const s = SS(); return `<div class="admgmt008">${tabs([['ss', '在线会话', s.length], ['lg', '登录记录']], 'ss', 'data-g="ss"')}<div data-p="ss" data-g="ss"><div class="tb"><div class="bbar" data-bar hidden>已选 <b data-count>0</b> 个会话<button type="button" class="z-btn d" data-act="kmany">强制下线</button></div><span class="hnt" data-hint>异地登录和长时间闲置的会话排在前面</span></div><div class="tw"><table class="z-tbl" data-ix="checks"><thead><tr><th style="width:48px">${ck(0, 'data-all aria-label="全选"')}</th><th style="width:200px">账号</th><th style="width:220px">设备</th><th style="width:140px">登录地点</th><th style="width:120px">登录时间</th><th style="width:120px">最近活跃</th><th style="width:100px">状态</th><th style="width:110px">操作</th></tr></thead><tbody>${s.map((x) => ssRow(x)).join('')}</tbody></table></div></div><div data-p="lg" data-g="ss" hidden><div class="tb">${seg([['bad', '异常 ' + LGI.filter((r) => r[2] === '失败' || r[5]).length], ['all', '全部 ' + LGI.length]], 'bad', 'data-g="lgf"')}<span class="hnt">默认只看登录失败和异地登录</span></div><div class="tw"><table class="z-tbl"><thead><tr><th style="width:120px">时间</th><th style="width:150px">账号</th><th style="width:90px">结果</th><th style="width:100px">地点</th><th style="width:210px">设备</th><th>备注</th></tr></thead><tbody></tbody></table></div></div>${modal('ko', '强制下线', '<div class="kl"></div>', '<button class="z-btn" type="button" data-close>取消</button><button class="z-btn p" type="button" data-act="kok">确认下线</button>', 420)}</div>` },
  js: (root) => {
    const el = $(root, '.admgmt008'); let ss = SS(), kill = []
    const lgDraw = (f) => { $(el, '[data-p=lg] tbody').innerHTML = LGI.filter((r) => f === 'all' || r[2] === '失败' || r[5]).map((r) => `<tr><td>${r[0]}</td><td><span class="z-who">${critter(r[1], 24)}${NAMES[r[1]]}</span></td><td>${tag(r[2], r[2] === '成功' ? 'ok' : 'dg')}</td><td>${r[3]}</td><td>${r[4]}</td><td class="l">${r[5] ? esc(r[5]) : '—'}</td></tr>`).join('') }
    lgDraw('bad')
    const upd = () => { const n = $(el, '.z-tabs [data-t=ss] .z-n'); if (n) n.textContent = ss.length; const lb = $(el, '.z-tabs [data-t=ss] .lb'); if (lb) lb.dataset.l = '在线会话 ' + ss.length; if (!ss.length) $(el, '[data-p=ss] tbody').innerHTML = '<tr><td colspan="8" class="emp">没有在线会话</td></tr>' }
    root.addEventListener('click', (e) => {
      const seg2 = e.target.closest('.z-seg [data-t]'); if (seg2) { lgDraw(seg2.dataset.t); return }
      const one = e.target.closest('[data-act=kone]'); if (one) { kill = [+one.closest('tr').dataset.id]; kmodal(); return }
      const many = e.target.closest('[data-act=kmany]'); if (many) { kill = $$(el, 'tbody tr.sel').map((r) => +r.dataset.id); if (kill.length) kmodal(); return }
      const ok = e.target.closest('[data-act=kok]'); if (ok) {
        closeOv(ok); const ids = kill.slice(); kill = []; ids.forEach((id) => { const r = $(el, `tbody tr[data-id="${id}"]`); if (r) r.classList.add('out') })
        setTimeout(() => { ss = ss.filter((x) => !ids.includes(x.id)); ids.forEach((id) => { const r = $(el, `tbody tr[data-id="${id}"]`); if (r) r.remove() }); upd(); const a = $(el, '[data-all]'); a.classList.remove('on', 'part'); $(el, '[data-bar]').hidden = true; toast(root, `已强制下线 ${ids.length} 个会话`) }, 230)
      }
    })
    const kmodal = () => { const rows = kill.map((id) => ss.find((x) => x.id === id)); $(el, '.kl').innerHTML = `<p>${rows.length === 1 ? '下面这个会话会立即退出登录：' : `下面 <b>${rows.length}</b> 个会话会立即退出登录：`}</p><ul>${rows.map((x) => `<li>${critter(x.who, 22)}<b>${NAMES[x.who]}</b><span>${x.env}</span></li>`).join('')}</ul><p>对方未保存的内容会丢失，需要重新登录。</p>`; openOv(root, 'ko') }
    wireEsc(root)
  },
})
const ssRow = (x) => `<tr data-id="${x.id}"><td>${x.cur ? '<span class="z-ck dis" role="checkbox" aria-disabled="true" title="当前会话不能下线"></span>' : ck(0, 'data-c aria-label="选择会话"')}</td><td class="l"><span class="who">${critter(x.who, 32)}<span><b>${NAMES[x.who]}</b><em>${x.role}</em></span></span></td><td><span class="dv">${ic(x.dev)}${x.env}</span></td><td><span class="ip">${x.ip}<em>${x.city}${x.abn ? ' ' : ''}</em>${x.abn ? tag('异地', 'wn') : ''}</span></td><td>${x.at}</td><td>${x.act}</td><td>${tag(x.st, x.cur ? 'in dot' : x.st === '在线' ? 'ok dot' : 'dot')}</td><td><button type="button" class="z-btn t d" data-act="kone" ${x.cur ? 'disabled title="不能下线当前会话"' : ''}>强制下线</button></td></tr>`

guide('ad', 'MGMT', [
  ['按角色分配功能权限', '角色权限矩阵', '行是功能、列是操作，行 / 列 / 分组都能全选并显示半选，内置角色只读'],
  ['配置侧栏菜单与按钮', '菜单树配置', '展开收起、搜索、三态勾选，点节点在右侧改名称、显隐与排序'],
  ['审计谁在什么时候做了什么', '操作日志列表', '默认只看警告与错误，级别带数量，点行展开 IP、设备与耗时'],
  ['维护下拉选项与状态枚举', '字典配置表', '行内增删改，启用开关直接生效，被引用的项只能停用'],
  ['员工自己订阅消息、改资料', '通知设置', '开关点一下即保存，失败回滚并在该行写原因；改头像和昵称用个人资料'],
  ['运行规则与阈值集中设置', '系统参数', '分组 + 恢复默认，影响资金的项保存前弹出改前改后确认'],
  ['在线会话管理与登录异常排查', '会话与登录日志', '可单个或批量强制下线，登录记录默认只看失败与异地登录'],
])

/* ================= PAGE 整页布局 ================= */
/* 共用：数据生成、折线图、页面外壳。每个整页块的 CSS 里都带一份外壳样式，可单独复制。 */
const rnd = (i, s) => { const x = Math.sin(i * 12.9898 + s * 78.233) * 43758.5453; return x - Math.floor(x) }
const dLabel = (back) => { const d = new Date(2026, 10, 4); d.setDate(d.getDate() - back); return `${pad(d.getMonth() + 1)}-${pad(d.getDate())}` }
const SALES60 = Array.from({ length: 60 }, (_, i) => Math.round(18000 + i * 55 + Math.sin((i / 7) * Math.PI * 2) * 2800 + (rnd(i, 1) - 0.5) * 3600 - (i === 57 ? 9200 : 0)))
const ORD60 = SALES60.map((v, i) => Math.round(v / (112 + rnd(i, 2) * 22)))
const VIS60 = ORD60.map((o, i) => Math.round(o / (0.034 + rnd(i, 3) * 0.011)))
const HOUR_T = [320, 180, 90, 60, 50, 140, 420, 980, 1650, 2100, 2350, 2100, 2640, 2480, 2300]
const HOUR_Y = HOUR_T.map((v, i) => Math.round(v * (0.9 + rnd(i, 4) * 0.2)))
const hLab = (i) => `${pad(i)}:00`
const range = (r) => {
  if (r === 'd1') { const o = (a) => a.map((v) => Math.round(v / 118)); return { cur: HOUR_T, prev: HOUR_Y, ord: o(HOUR_T), ordP: o(HOUR_Y), vis: o(HOUR_T).map((x) => Math.round(x / 0.038)), visP: o(HOUR_Y).map((x) => Math.round(x / 0.036)), labels: HOUR_T.map((_, i) => hLab(i)) } }
  const n = r === 'd7' ? 7 : r === 'd30' ? 30 : 90, m = Math.min(n, 30)
  const idx = (a, from, len) => a.slice(from, from + len)
  const k = n > 30 ? 3 : 1  // 90 天：按 3 天合并，点数不变
  const merge = (a) => (k === 1 ? a : Array.from({ length: m }, (_, i) => a.slice(i * k, i * k + k).reduce((x, y) => x + y, 0)))
  const full = (a) => { const big = Array.from({ length: 200 }, (_, i) => Math.round(a[i % 60] * (0.94 + rnd(i, 7) * 0.08))); return big }
  const S = n > 30 ? full(SALES60) : SALES60, O = n > 30 ? full(ORD60) : ORD60, V = n > 30 ? full(VIS60) : VIS60, L = S.length
  return { cur: merge(idx(S, L - n, n)), prev: merge(idx(S, L - 2 * n, n)), ord: merge(idx(O, L - n, n)), ordP: merge(idx(O, L - 2 * n, n)), vis: merge(idx(V, L - n, n)), visP: merge(idx(V, L - 2 * n, n)), labels: Array.from({ length: m }, (_, i) => dLabel((m - 1 - i) * k)) }
}
const sum = (a) => a.reduce((x, y) => x + y, 0)
const money = (v) => '¥' + Math.round(v).toLocaleString()
const nice = (v) => { const raw = v / 4, p = Math.pow(10, Math.floor(Math.log10(raw))), f = raw / p; return 4 * p * ([1, 1.5, 2, 2.5, 3, 4, 5, 6, 8, 10].find((x) => x >= f - 1e-9) || 10) }
const axis = (v) => (v >= 10000 ? `${+(v / 10000).toFixed(1)} 万` : v.toLocaleString())
const delta = (c, p) => (p ? ((c - p) / p) * 100 : 0)
const dTag = (d, unit = '%', fix = 1) => `<span class="dl ${d >= 0 ? 'up' : 'dn'}">${ic(d >= 0 ? 'arrowup' : 'arrowdown', 's')}${Math.abs(d).toFixed(fix)}${unit}</span>`
const spark = (a) => { const mx = Math.max(...a), mn = Math.min(...a), n = a.length; const d = a.map((v, i) => `${i ? 'L' : 'M'}${((i / (n - 1)) * 100).toFixed(1)} ${(26 - ((v - mn) / (mx - mn || 1)) * 22).toFixed(1)}`).join(''); return `<svg class="spk" viewBox="0 0 100 28" preserveAspectRatio="none" aria-hidden="true"><path d="${d}"/></svg>` }
/* 折线图：线与面积用 SVG（非等比拉伸），坐标轴文字与提示用 HTML，字号不会被缩放 */
const chartHTML = (uid) => `<div class="cht" data-uid="${uid}"><div class="yax"></div><div class="plot"><svg viewBox="0 0 100 100" preserveAspectRatio="none" aria-hidden="true"><defs><linearGradient id="${uid}-g" x1="0" y1="0" x2="0" y2="1"><stop offset="0" style="stop-color:var(--p);stop-opacity:.2"/><stop offset="1" style="stop-color:var(--p);stop-opacity:0"/></linearGradient></defs><g class="gl"></g><path class="pv"/><path class="ar" fill="url(#${uid}-g)"/><path class="ln"/></svg><i class="gd" hidden></i><i class="d1" hidden></i><i class="d2" hidden></i><div class="cti" hidden></div></div><div class="xax"></div></div>`
const chartDraw = (box, o) => {
  const n = o.cur.length, all = [...o.cur, ...(o.showPrev ? o.prev : [])], max = nice(Math.max(...all) * 1.08)
  const X = (i) => (n === 1 ? 50 : (i / (n - 1)) * 100), Y = (v) => 96 - (v / max) * 90
  const path = (a) => a.map((v, i) => `${i ? 'L' : 'M'}${X(i).toFixed(2)} ${Y(v).toFixed(2)}`).join('')
  $(box, '.ln').setAttribute('d', o.hideCur ? '' : path(o.cur)); $(box, '.ar').setAttribute('d', o.hideCur ? '' : `${path(o.cur)}L${X(n - 1)} 96L${X(0)} 96Z`); $(box, '.pv').setAttribute('d', o.showPrev ? path(o.prev) : '')
  $(box, '.gl').innerHTML = [0, 1, 2, 3, 4].map((k) => `<line x1="0" x2="100" y1="${96 - k * 22.5}" y2="${96 - k * 22.5}"/>`).join('')
  $(box, '.yax').innerHTML = [0, 1, 2, 3, 4].map((k) => `<span style="top:${96 - k * 22.5}%">${axis((max / 4) * k)}</span>`).join('')
  const step = Math.max(1, Math.ceil(n / 7)); $(box, '.xax').innerHTML = o.labels.map((t, i) => (i % step === 0 || i === n - 1 ? `<span style="left:${X(i)}%"${i === 0 ? ' class="f"' : i === n - 1 ? ' class="e"' : ''}>${t}</span>` : '')).join('')
  box.__o = { ...o, X, Y, n }
}
const chartBind = (box) => {
  const plot = $(box, '.plot'), hide = () => ['.gd', '.d1', '.d2', '.cti'].forEach((s) => ($(plot, s).hidden = true))
  plot.addEventListener('pointermove', (e) => {
    const o = box.__o; if (!o) return; const r = plot.getBoundingClientRect(), i = Math.max(0, Math.min(o.n - 1, Math.round(((e.clientX - r.left) / r.width) * (o.n - 1)))), x = o.X(i)
    const g = $(plot, '.gd'), d1 = $(plot, '.d1'), d2 = $(plot, '.d2'), t = $(plot, '.cti'); g.hidden = false; g.style.left = x + '%'
    d1.hidden = !!o.hideCur; d1.style.left = x + '%'; d1.style.top = o.Y(o.cur[i]) + '%'; d2.hidden = !o.showPrev; d2.style.left = x + '%'; d2.style.top = o.Y(o.prev[i]) + '%'
    const d = delta(o.cur[i], o.prev[i]); t.hidden = false; t.innerHTML = `<b>${o.labels[i]}</b>${o.hideCur ? '' : `<div><i class="s1"></i>${o.name || '本期'}<em>${o.fmt(o.cur[i])}</em></div>`}${o.showPrev ? `<div><i class="s2"></i>上期<em>${o.fmt(o.prev[i])}</em></div>` : ''}${o.showPrev && !o.hideCur ? `<div class="df">${dTag(d)}</div>` : ''}`
    const w = t.offsetWidth; t.style.left = (x > 60 ? 'auto' : 'calc(' + x + '% + 12px)'); t.style.right = (x > 60 ? `calc(${100 - x}% + 12px)` : 'auto'); t.style.top = '8px'
  })
  plot.addEventListener('pointerleave', hide)
}
const CHART_CSS = `§ .cht{position:relative;padding:4px 0 24px 52px}§ .yax{position:absolute;left:0;top:4px;bottom:24px;width:46px}§ .yax span{position:absolute;right:0;transform:translateY(-50%);font-size:12px;color:var(--ink3);font-variant-numeric:tabular-nums}§ .plot{position:relative;height:var(--ch,220px);touch-action:pan-y}§ .plot svg{position:absolute;inset:0;width:100%;height:100%;overflow:visible}§ .plot line{stroke:var(--n4);stroke-width:1;vector-effect:non-scaling-stroke}§ .plot .ln{fill:none;stroke:var(--p);stroke-width:2;stroke-linejoin:round;stroke-linecap:round;vector-effect:non-scaling-stroke}§ .plot .pv{fill:none;stroke:var(--ink5);stroke-width:1.5;stroke-dasharray:5 4;vector-effect:non-scaling-stroke}§ .plot .gd{position:absolute;top:0;bottom:0;width:0;border-left:1px dashed var(--n11);pointer-events:none}§ .plot .d1,§ .plot .d2{position:absolute;width:10px;height:10px;margin:-5px 0 0 -5px;border-radius:50%;background:var(--card);border:2px solid var(--p);pointer-events:none}§ .plot .d2{border-color:var(--n12)}§ .cti{position:absolute;z-index:5;min-width:148px;padding:8px 12px;border-radius:8px;background:var(--card);box-shadow:0 6px 20px var(--sh16),0 0 0 1px var(--sh06);font-size:12px;line-height:1.7;pointer-events:none}§ .cti b{display:block;font-weight:600;margin-bottom:2px}§ .cti div{display:flex;align-items:center;gap:6px;color:var(--ink2)}§ .cti em{margin-left:auto;padding-left:12px;font-style:normal;font-weight:600;color:var(--ink);font-variant-numeric:tabular-nums}§ .cti .s1,§ .cti .s2{width:8px;height:8px;border-radius:50%;background:var(--p)}§ .cti .s2{background:var(--n12)}§ .cti .df{justify-content:flex-end}§ .xax{position:absolute;left:52px;right:0;bottom:0;height:20px}§ .xax span{position:absolute;transform:translateX(-50%);font-size:12px;color:var(--ink3);white-space:nowrap}§ .xax span.f{transform:none}§ .xax span.e{transform:translateX(-100%)}§ .dl{display:inline-flex;align-items:center;gap:2px;font-size:12px;font-weight:600;font-variant-numeric:tabular-nums}§ .dl.up{color:var(--ok)}§ .dl.dn{color:var(--dg)}§ .spk{display:block;width:100%;height:28px}§ .spk path{fill:none;stroke:var(--p);stroke-width:1.5;stroke-linejoin:round;stroke-linecap:round;vector-effect:non-scaling-stroke}`

/* ---- 页面外壳 ---- */
const PG_NAV = [
  [null, [['dash', '工作台', 'dashboard']]],
  ['交易', [['order', '订单管理', 'receipt'], ['after', '售后管理', 'refresh'], ['goods', '商品管理', 'box']]],
  ['运营', [['member', '会员管理', 'users'], ['mkt', '营销活动', 'coupon'], ['stat', '数据分析', 'barchart']]],
  ['系统', [['role', '员工与角色', 'shield'], ['set', '系统设置', 'gear']]],
]
const PG_NOTE = [['库存预警：保温水杯仅剩 6 件', '10 分钟前', 1], ['退款申请：RF20261104007 等待审核', '35 分钟前', 1], ['11 月 4 日 02:00 系统已完成自动备份', '今天 02:00', 0]]
const pgItems = () => PG_NAV.flatMap(([, it]) => it)
const shell = (active, body, o = {}) => `<aside class="sd"><div class="br"><i class="lg">${ic('bz_shop', 'l')}</i><b>示例商城</b></div><nav aria-label="主导航">${PG_NAV.map(([g, it]) => `${g ? `<div class="gt">${g}</div>` : ''}${it.map(([k, t, i]) => `<button type="button" class="mi${k === active ? ' on' : ''}" data-nav="${k}" title="${t}"${k === active ? ' aria-current="page"' : ''}>${ic(i, 'l')}<span>${t}</span></button>`).join('')}`).join('<div class="sp"></div>')}</nav><div class="vr"><button type="button" class="vb" data-pp="ver" title="版本信息">${ic('info')}<span>前端 v2.4.1 · 后端 v2.4.0</span></button><div class="pop ver" data-pop="ver"><b>版本信息</b><dl><dt>上线日期</dt><dd>2026-10-28</dd><dt>运行环境</dt><dd>生产环境</dd></dl><p>本次更新：订单列表新增批量发货；优化导出速度；修复积分过期提醒重复推送。</p></div></div></aside><div class="mn"><header class="tp"><button type="button" class="z-x" data-col aria-label="收起或展开侧栏" title="收起 / 展开侧栏">${ic('bz_panel')}</button>${o.crumb ? `<div class="crumb">${o.crumb}</div>` : `<label class="sr">${ic('search')}<input class="z-in" type="search" placeholder="搜索订单号、会员、商品" aria-label="全局搜索"></label>`}<div class="rt">${dd(['示例旗舰店', '静安分店', '浦东分店'], '示例旗舰店', { cls: 'r' })}<span class="bw"><button type="button" class="z-x" data-pp="bell" aria-label="消息通知" title="消息通知">${ic('bell')}<i class="bdg">2</i></button><div class="pop bell" data-pop="bell"><div class="phd"><b>消息</b><button type="button" class="z-btn t" data-readall>全部已读</button></div>${PG_NOTE.map(([t, tm, u]) => `<button type="button" class="nt${u ? ' un' : ''}" data-nt><i></i><span>${t}<em>${tm}</em></span></button>`).join('')}</div></span><span class="uw"><button type="button" class="us" data-pp="user" aria-label="账号菜单">${critter(0, 28)}<span>林小满</span>${ic('down', 's')}</button><div class="pop user" data-pop="user"><button type="button" data-toast="个人资料为示例入口">个人资料</button><button type="button" data-toast="已切换为浅色外观">外观：浅色</button><button type="button" data-toast="已退出登录（示例）">退出登录</button></div></span></div></header><main class="ct">${body}</main></div>`
const SHELL_CSS = `§{position:relative;display:flex;width:1400px;max-width:100%;height:620px;background:var(--n3);border:1px solid var(--n7);border-radius:12px;overflow:hidden}.ixr:has(>§){min-width:1040px}§ .sd{position:relative;z-index:6;display:flex;flex-direction:column;flex:none;width:216px;background:var(--card);border-right:1px solid var(--line);transition:width .2s cubic-bezier(.2,0,0,1)}§.mini .sd{width:64px}§ .br{display:flex;align-items:center;gap:10px;height:52px;padding:0 18px;border-bottom:1px solid var(--line);overflow:hidden;white-space:nowrap}§ .br .lg{display:flex;align-items:center;justify-content:center;width:28px;height:28px;border-radius:8px;background:var(--pt);color:var(--p-text);flex:none}§ .br b{font-size:16px;font-weight:600}§ nav{flex:1;min-height:0;overflow:auto;padding:8px 10px}§ .gt{padding:12px 10px 4px;font-size:12px;color:var(--ink3);white-space:nowrap;overflow:hidden}§ .sp{height:4px}§.mini .gt{height:0;padding:0;opacity:0}§.mini .sp{height:8px;margin:4px 12px;border-top:1px solid var(--line)}§ .mi{display:flex;align-items:center;gap:12px;width:100%;height:40px;padding:0 10px;border-radius:8px;color:var(--ink2);white-space:nowrap;overflow:hidden;transition:background-color .15s,color .15s}§ .mi:hover{background:var(--soft);color:var(--ink)}§ .mi.on{background:var(--pt);color:var(--p-text);font-weight:600}§ .mi .z-ic{flex:none}§.mini .mi span{opacity:0}§ .vr{position:relative;padding:8px 10px 12px;border-top:1px solid var(--line)}§ .vb{display:flex;align-items:center;gap:10px;width:100%;height:32px;padding:0 10px;border-radius:8px;font-size:12px;color:var(--ink3);white-space:nowrap;overflow:hidden}§ .vb:hover{background:var(--soft)}§.mini .vb span{opacity:0}§ .pop{position:absolute;z-index:30;display:none;padding:6px;border:1px solid var(--n6);border-radius:8px;background:var(--card2);box-shadow:0 8px 24px var(--sh14)}§ .pop.open{display:block;animation:zbin .15s cubic-bezier(.2,0,0,1)}§ .pop.ver{left:10px;bottom:calc(100% - 6px);width:248px;padding:12px 14px;line-height:1.6}§ .pop.ver b{font-weight:600}§ .pop.ver dl{display:grid;grid-template-columns:64px 1fr;gap:2px 8px;margin:6px 0;font-size:12px}§ .pop.ver dt{color:var(--ink3)}§ .pop.ver p{font-size:12px;color:var(--ink2)}§ .mn{flex:1;min-width:0;display:flex;flex-direction:column}§ .tp{position:relative;z-index:5;display:flex;align-items:center;gap:12px;height:52px;flex:none;padding:0 16px;background:var(--card);border-bottom:1px solid var(--line)}§ .sr{position:relative;width:280px;max-width:40%}§ .sr .z-ic{position:absolute;left:10px;top:8px;color:var(--ink3)}§ .sr input{height:32px;padding-left:32px}§ .crumb{display:flex;align-items:center;gap:8px;color:var(--ink2);white-space:nowrap;overflow:hidden}§ .crumb button{color:var(--ink2)}§ .crumb button:hover{color:var(--p-text)}§ .crumb b{font-weight:600;color:var(--ink)}§ .crumb .z-ic{color:var(--ink3)}§ .rt{display:flex;align-items:center;gap:8px;margin-left:auto}§ .bw,§ .uw{position:relative;display:flex}§ .bdg{position:absolute;right:2px;top:2px;min-width:16px;height:16px;padding:0 4px;border-radius:8px;background:var(--danger-fill);color:#fff;font-size:12px;font-style:normal;line-height:16px;text-align:center}§ .pop.bell{right:0;top:calc(100% + 8px);width:320px;padding:0}§ .pop.bell .phd{display:flex;align-items:center;justify-content:space-between;padding:8px 8px 8px 14px;border-bottom:1px solid var(--line)}§ .pop.bell .phd b{font-weight:600}§ .nt{display:flex;align-items:flex-start;gap:10px;width:100%;padding:10px 14px;border-radius:0;text-align:left;line-height:1.5}§ .nt:hover{background:var(--n2)}§ .nt i{flex:none;width:8px;height:8px;margin-top:6px;border-radius:50%;background:transparent}§ .nt.un i{background:var(--danger-fill)}§ .nt span{display:flex;flex-direction:column}§ .nt em{font-style:normal;font-size:12px;color:var(--ink3)}§ .nt:not(.un){color:var(--ink2)}§ .us{display:flex;align-items:center;gap:8px;height:36px;padding:0 8px;border-radius:8px}§ .us:hover{background:var(--soft)}§ .pop.user{right:0;top:calc(100% + 8px);width:160px}§ .pop.user button{display:flex;align-items:center;width:100%;height:36px;padding:0 10px;border-radius:4px}§ .pop.user button:hover{background:var(--sf)}§ .ct{position:relative;flex:1;min-height:0;overflow:auto;padding:20px}`
const wireShell = (root, el, active) => {
  const closeAll = () => $$(el, '.pop.open').forEach((p) => p.classList.remove('open'))
  root.addEventListener('click', (e) => {
    const pp = e.target.closest('[data-pp]')
    if (pp) { const p = $(el, `[data-pop="${pp.dataset.pp}"]`), was = p.classList.contains('open'); closeAll(); p.classList.toggle('open', !was); return }
    if (e.target.closest('[data-col]')) { closeAll(); el.classList.toggle('mini'); return }
    const nt = e.target.closest('[data-nt]'); if (nt) { nt.classList.remove('un'); const n = $$(el, '.nt.un').length; const b = $(el, '.bdg'); b.textContent = n; b.hidden = !n; return }
    if (e.target.closest('[data-readall]')) { $$(el, '.nt.un').forEach((x) => x.classList.remove('un')); $(el, '.bdg').hidden = true; toast(root, '已全部标为已读'); return }
    const mi = e.target.closest('.mi'); if (mi && mi.dataset.nav !== active) { toast(root, `这是布局示例，只演示「${pgItems().find((x) => x[0] === active)[1]}」`); return }
    if (!e.target.closest('.pop')) closeAll()
  })
  root.addEventListener('keydown', (e) => { if (e.key === 'Escape') closeAll() })
}

/* ---- AD-PAGE-001 驾驶舱首页 ---- */
const TODOS = [['待发货订单', 12, 'receipt'], ['待审核退款', 3, 'refresh'], ['库存预警商品', 5, 'box'], ['待回复评价', 8, 'chat']]
const TOP5 = [['无线降噪耳机', 1286], ['轻量跑鞋', 1048], ['保温水杯', 912], ['护眼台灯', 764], ['陶瓷马克杯', 633]]
const dashBody = (r, showPrev) => {
  const d = range(r), S = sum(d.cur), SP = sum(d.prev), O = sum(d.ord), OP = sum(d.ordP), A = S / O, AP = SP / OP, V = sum(d.vis), VP = sum(d.visP), C = (O / V) * 100, CP = (OP / VP) * 100
  const kp = [['销售额', money(S), dTag(delta(S, SP)), d.cur], ['订单数', O.toLocaleString(), dTag(delta(O, OP)), d.ord], ['客单价', money(A), dTag(delta(A, AP)), d.cur.map((v, i) => v / (d.ord[i] || 1))], ['支付转化率', C.toFixed(1) + '%', dTag(C - CP, ' 个百分点', 1), d.ord.map((o, i) => (o / (d.vis[i] || 1)) * 100)]]
  const mean = S / d.cur.length, mi = d.cur.indexOf(Math.min(...d.cur)), low = r !== 'd1' && d.cur[mi] < mean * 0.8
  return { d, html: `${low ? `<div class="warn">${ic('alert', 'l')}<span><b>${d.labels[mi]}</b> 销售额 ${money(d.cur[mi])}，比区间日均低 ${Math.round((1 - d.cur[mi] / mean) * 100)}%，建议检查当天的商品与活动</span><button type="button" class="z-btn t" data-toast="已定位到 ${d.labels[mi]} 的订单">查看当天</button></div>` : ''}<div class="kpis">${kp.map(([t, v, dl, a]) => `<div class="z-card kp"><span class="k">${t}</span><b class="v">${v}</b><div class="dd2">${dl}<em>较上期</em></div>${spark(a)}</div>`).join('')}</div>` }
}
def({
  id: 'AD-PAGE-001', name: '驾驶舱首页', style: '计算后的指标', wide: true,
  fit: '运营型首页：先给计算后的结果（销售额、订单、客单价、转化率及较上期变化），再看趋势、待办与排名；时间范围由页面统一控制，异常自动提示',
  avoid: '分析型的深度下钻（用数据分析页）；指标长期为 0 或数据点少于 3 个时（合并为一行状态、不画折线）',
  kw: '首页 驾驶舱 dashboard 工作台 概览 指标 趋势 待办 排名 异常',
  css: K('adpage001', 'btn tag seg in dd') + SHELL_CSS.replace(/§/g, '.adpage001') + CHART_CSS.replace(/§/g, '.adpage001') + `.adpage001 .hd{display:flex;align-items:center;justify-content:space-between;gap:12px;margin-bottom:12px}.adpage001 .hd .l{display:flex;align-items:center;gap:12px}.adpage001 .hd .u{font-size:12px;color:var(--ink3)}.adpage001 .warn{display:flex;align-items:center;gap:10px;margin-bottom:12px;padding:6px 8px 6px 12px;border:1px solid #EBD9AE;border-radius:8px;background:var(--wnb);color:var(--wn)}.adpage001 .warn span{flex:1;color:var(--gold-ink);line-height:1.5}.adpage001 .kpis{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:16px}.adpage001 .cd .cht{padding-top:0}.adpage001 .kp{padding:14px 16px 10px;display:flex;flex-direction:column}.adpage001 .kp .k{color:var(--ink2)}.adpage001 .kp .v{margin-top:6px;font-size:22px;font-weight:700;line-height:1.2;font-variant-numeric:tabular-nums}.adpage001 .kp .dd2{display:flex;align-items:center;gap:8px;margin:4px 0 8px}.adpage001 .kp .spk{height:22px}.adpage001 .kp .dd2 em{font-style:normal;font-size:12px;color:var(--ink3)}.adpage001{--ch:150px}.adpage001 .grid2{display:grid;grid-template-columns:minmax(0,1.7fr) minmax(0,1fr) minmax(0,1fr);gap:16px;margin-top:16px}.adpage001 .cd{padding:16px 18px}.adpage001 .cd .ch{display:flex;align-items:center;justify-content:space-between;gap:12px;margin-bottom:12px}.adpage001 .cd h4{font-size:14px;font-weight:600}.adpage001 .lgd{display:flex;align-items:center;gap:14px;font-size:12px;color:var(--ink2)}.adpage001 .lgd i{display:inline-block;width:14px;height:0;border-top:2px solid var(--p);vertical-align:middle;margin-right:6px}.adpage001 .lgd i.pv{border-top:2px dashed var(--n12)}.adpage001 .td{display:flex;flex-direction:column}.adpage001 .td button{display:flex;align-items:center;gap:10px;height:44px;padding:0 8px;margin:0 -8px;border-radius:8px;text-align:left}.adpage001 .td button:hover{background:var(--sf)}.adpage001 .td .ti{display:flex;align-items:center;justify-content:center;width:28px;height:28px;border-radius:8px;background:var(--pt);color:var(--p-text)}.adpage001 .td .n{margin-left:auto;font-weight:600;font-variant-numeric:tabular-nums}.adpage001 .td .n.z{color:var(--ink3);font-weight:400}.adpage001 .td .z-ic.c{color:var(--ink3)}.adpage001 .rk{display:flex;flex-direction:column;gap:12px}.adpage001 .rk li{display:grid;grid-template-columns:20px 1fr auto;align-items:center;gap:6px 10px}.adpage001 .rk .no{font-size:12px;color:var(--ink3);font-variant-numeric:tabular-nums}.adpage001 .rk .trk{grid-column:2/4;height:6px;border-radius:3px;background:var(--n4);overflow:hidden}.adpage001 .rk .trk i{display:block;height:100%;border-radius:3px;background:var(--p);transition:width .3s cubic-bezier(.2,0,0,1)}.adpage001 .rk .v{font-variant-numeric:tabular-nums;color:var(--ink2)}`,
  html: () => { const b = dashBody('d7'); return `<div class="adpage001">${shell('dash', `<div class="hd"><div class="l">${seg([['d1', '今日'], ['d7', '近 7 天'], ['d30', '近 30 天']], 'd7')}<span class="u">更新于 14:20</span></div><button type="button" class="z-btn" data-act="re">${ic('refresh')}刷新</button></div><div class="dash">${b.html}</div><div class="grid2"><div class="z-card cd"><div class="ch"><h4>销售额趋势</h4><span class="lgd"><span><i></i>本期</span><span><i class="pv"></i>上期</span></span></div>${chartHTML('adpage001c')}</div><div class="z-card cd"><div class="ch"><h4>待办事项</h4></div><div class="td">${TODOS.map(([t, n, i]) => `<button type="button" data-toast="前往「${t}」"><span class="ti">${ic(i)}</span>${t}<span class="n${n ? '' : ' z'}">${n}</span>${ic('right', 's c')}</button>`).join('')}</div></div><div class="z-card cd"><div class="ch"><h4>商品销量排行</h4></div><ol class="rk">${TOP5.map(([n, v], i) => `<li><span class="no">${i + 1}</span><span>${n}</span><span class="v">${v.toLocaleString()} 件</span><span class="trk"><i style="width:${(v / TOP5[0][1]) * 100}%"></i></span></li>`).join('')}</ol></div></div>`)}</div>` },
  js: (root) => {
    const el = $(root, '.adpage001'); let r = 'd7'; const box = $(el, '.cht'); chartBind(box)
    const mult = { d1: 0.12, d7: 1, d30: 4.2 }
    const draw = () => {
      const b = dashBody(r); $(el, '.dash').innerHTML = b.html
      chartDraw(box, { cur: b.d.cur, prev: b.d.prev, labels: b.d.labels, showPrev: true, fmt: money, name: '本期' })
      $$(el, '.rk li').forEach((li, i) => { const v = Math.round(TOP5[i][1] * mult[r]); $(li, '.v').textContent = v.toLocaleString() + ' 件'; $(li, '.trk i').style.width = (TOP5[i][1] / TOP5[0][1]) * 100 + '%' })
    }
    draw(); wireShell(root, el, 'dash')
    root.addEventListener('click', (e) => {
      const t = e.target.closest('.z-seg [data-t]'); if (t) { r = t.dataset.t; draw(); return }
      if (e.target.closest('[data-act=re]')) { $(el, '.u').textContent = '更新于 刚刚'; toast(root, '数据已刷新') }
    })
  },
})

/* ---- AD-PAGE-002 列表页 ---- */
const OD_ST = [['待发货', 'in'], ['待付款', 'wn'], ['配送中', 'in'], ['已完成', 'ok'], ['已取消', ''], ['已退款', 'dg']]
const ODL = [...Array(14).fill(0), ...Array(9).fill(1), ...Array(12).fill(2), ...Array(18).fill(3), ...Array(4).fill(4), ...Array(3).fill(5)]
const STORES = ['示例旗舰店', '静安分店', '浦东分店']
const OD = Array.from({ length: 60 }, (_, i) => {
  const a = SKUS[(i * 4) % 9], b = SKUS[(i * 2 + 1) % 9], q = (i % 3) + 1, two = i % 4 === 0, t = new Date(2026, 10, 4, 14, 20 - i * 91)
  return { no: 'SO' + (20261104200 - i * 3), who: i % 12, goods: two ? `${a[0]} × ${q}；${b[0]} × 1` : `${a[0]} × ${q}`, n: two ? q + 1 : q, amt: a[1] * q + (two ? b[1] : 0), st: ODL[(i * 17) % 60], at: t.getTime(), store: STORES[i % 3], ship: i % 5 === 0 ? '快递' : '骑手配送', addr: ['上海市静安区南京西路 1266 号 12 楼', '上海市浦东新区世纪大道 88 号 3 单元 502', '上海市徐汇区漕溪北路 331 号 A 座 8 层'][i % 3] }
})
const fmtT = (ms) => { const d = new Date(ms); return `${pad(d.getMonth() + 1)}-${pad(d.getDate())} ${pad(d.getHours())}:${pad(d.getMinutes())}` }
const ODRANGE = { today: '今天', d7: '近 7 天', all: '全部时间' }
def({
  id: 'AD-PAGE-002', name: '列表页', style: '筛选表格分页', wide: true,
  fit: '订单、会员、工单等业务列表：默认先看待处理，筛选只露最常用的几项、其余收进更多筛选，状态标签带数量，批量栏、排序与分页齐全',
  avoid: '少于 10 条的小列表（直接用卡片或简单表格）；需要对比多个维度的分析场景（用数据分析页）',
  kw: '列表页 订单列表 筛选 表格 分页 批量 状态标签 更多筛选 排序 导出',
  css: K('adpage002', 'btn tag in dd ck tbl modal') + SHELL_CSS.replace(/§/g, '.adpage002') + `.adpage002 .ct{display:flex;flex-direction:column;padding:16px 20px 0}.adpage002 .fl{display:flex;align-items:center;justify-content:space-between;flex-wrap:wrap;gap:10px 12px}.adpage002 .fl .l,.adpage002 .fl .r{display:flex;align-items:center;gap:8px;flex-wrap:wrap}.adpage002 .sq{position:relative;width:240px}.adpage002 .sq .z-ic{position:absolute;left:10px;top:9px;color:var(--ink3)}.adpage002 .sq input{height:32px;padding-left:32px}.adpage002 .more{display:flex;align-items:center;gap:8px;flex-wrap:wrap;margin-top:10px;padding:10px 12px;border-radius:8px;background:var(--card);border:1px dashed var(--bd)}.adpage002 .more .lb{font-size:12px;color:var(--ink3)}.adpage002 .chips{display:flex;align-items:center;gap:8px;flex-wrap:wrap;margin-top:10px;font-size:12px;color:var(--ink3)}.adpage002 .chips .c{display:inline-flex;align-items:center;gap:4px;height:24px;padding:0 4px 0 8px;border-radius:4px;background:var(--pt);color:var(--p-text)}.adpage002 .chips .c button{display:flex;width:16px;height:16px;border-radius:4px;align-items:center;justify-content:center}.adpage002 .chips .c button:hover{background:var(--pm)}.adpage002 .sts{display:flex;align-items:center;gap:4px;margin-top:12px;padding:4px;border-radius:8px;background:var(--n4);align-self:flex-start;max-width:100%;overflow-x:auto}.adpage002 .sts button{display:inline-flex;align-items:center;gap:6px;height:32px;padding:0 12px;border-radius:4px;color:var(--ink2);white-space:nowrap}.adpage002 .sts button:hover{color:var(--ink)}.adpage002 .sts button.on{background:var(--lift);color:var(--ink);font-weight:600;box-shadow:0 1px 2px var(--sh12)}.adpage002 .sts em{font-style:normal;font-size:12px;color:var(--ink3);font-variant-numeric:tabular-nums}.adpage002 .sts em.z0{opacity:.5}.adpage002 .sts .z-dd [data-tg]{border:0;background:none;height:32px;min-width:0;padding:0 8px 0 12px}.adpage002 .bat{display:flex;align-items:center;gap:12px;margin-top:12px;padding:8px 12px;border-radius:8px;background:var(--pt);color:var(--p-text)}.adpage002 .bat b{font-weight:600}.adpage002 .card{margin-top:12px;display:flex;flex-direction:column;flex:1;min-height:0;background:var(--card);border:1px solid var(--line2);border-radius:12px 12px 0 0;border-bottom:0}.adpage002 .tw{flex:1;min-height:0;overflow:auto}.adpage002 .z-tbl{min-width:900px}.adpage002 .z-tbl thead th{position:sticky;top:0;z-index:2}.adpage002 .z-tbl td{height:46px}.adpage002 .z-tbl td.l{overflow-wrap:anywhere}.adpage002 .z-tbl .no{font-variant-numeric:tabular-nums;white-space:nowrap}.adpage002 th.so{cursor:pointer;user-select:none;-webkit-user-select:none}.adpage002 th.so:hover{color:var(--ink)}.adpage002 th.so .z-ic{color:color-mix(in srgb,var(--ink6) 74%,var(--ink5));margin-left:2px;vertical-align:-3px}.adpage002 th.so.on .z-ic{color:var(--p-fg)}.adpage002 .emp{padding:48px 0;text-align:center;color:var(--ink3)}.adpage002 .pgf{display:flex;align-items:center;justify-content:flex-end;gap:8px 12px;flex-wrap:wrap;padding:10px 16px;border-top:1px solid var(--line);color:var(--ink2);background:var(--card);border-radius:0}.adpage002 .pgf .pb{display:flex;align-items:center;gap:4px}.adpage002 .pgf .pb button{min-width:32px;height:32px;padding:0 6px;border-radius:8px;border:1px solid transparent}.adpage002 .pgf .pb button:hover:not(:disabled){border-color:var(--bd)}.adpage002 .pgf .pb button.on{border-color:var(--p);color:var(--p-text);background:var(--pt);font-weight:600}.adpage002 .pgf .pb button:disabled{opacity:.4;cursor:not-allowed}.adpage002 .pgf .pb span{padding:0 4px;color:var(--ink3)}.adpage002 .dtl{display:grid;grid-template-columns:72px 1fr;gap:10px 12px}.adpage002 .dtl dt{color:var(--ink3)}.adpage002 .dtl dd{overflow-wrap:anywhere}.adpage002 tr.out td{opacity:0;transition:opacity .2s}`,
  html: () => `<div class="adpage002">${shell('order', `<div class="fl"><div class="l"><label class="sq">${ic('search')}<input class="z-in" type="search" placeholder="订单号、客户、商品" aria-label="搜索订单"></label>${dd(Object.entries(ODRANGE), 'd7', { attr: 'data-f="rg"' })}${dd(['全部门店', ...STORES], '全部门店', { attr: 'data-f="st"' })}<button type="button" class="z-btn" data-act="more" aria-expanded="false">${ic('filter')}更多筛选</button></div><div class="r"><button type="button" class="z-btn" data-toast="已按当前筛选结果导出">${ic('download')}导出</button><button type="button" class="z-btn p" data-toast="新建订单为示例入口">${ic('plus')}新建订单</button></div></div><div class="more" hidden><span class="lb">金额</span>${dd(['不限', '≥ ¥200', '≥ ¥500', '≥ ¥1,000'], '不限', { attr: 'data-f="am"' })}<span class="lb">配送方式</span>${dd(['不限', '骑手配送', '快递'], '不限', { attr: 'data-f="sh"' })}</div><div class="chips" hidden></div><div class="sts"></div><div class="bat" hidden>已选 <b class="bn">0</b> 项<button type="button" class="z-btn" data-act="ship">批量发货</button><button type="button" class="z-btn t" data-act="clr">取消选择</button></div><div class="card"><div class="tw"><table class="z-tbl"><thead><tr><th style="width:44px">${ck(0, 'data-all aria-label="全选本页"')}</th><th style="width:168px">订单号</th><th style="width:140px">客户</th><th>商品</th><th class="so" data-sort="amt" style="width:120px">金额${ic('sort', 's')}</th><th style="width:96px">状态</th><th class="so" data-sort="at" style="width:130px">下单时间${ic('sort', 's')}</th><th style="width:120px">操作</th></tr></thead><tbody></tbody></table></div><div class="pgf"></div></div>`)}${modal('od', '订单详情', '<dl class="dtl"></dl>', '<button class="z-btn" type="button" data-close>关闭</button><button class="z-btn p" type="button" data-act="shipone" hidden>发货</button>', 460)}</div>`,
  js: (root) => {
    const el = $(root, '.adpage002'), body = $(el, 'tbody'), rows = OD.map((x) => ({ ...x })); wireShell(root, el, 'order')
    const S = { tab: 0, q: '', rg: 'd7', st: '全部门店', am: '不限', sh: '不限', page: 1, size: 20, sort: 'at', dir: 1, sel: new Set(), cur: null }
    const amMin = { '不限': 0, '≥ ¥200': 200, '≥ ¥500': 500, '≥ ¥1,000': 1000 }
    const base = () => rows.filter((r) => (!S.q || (r.no + NAMES[r.who] + r.goods).toLowerCase().includes(S.q)) && (S.rg !== 'today' || new Date(r.at).getDate() === 4) && (S.st === '全部门店' || r.store === S.st) && r.amt >= amMin[S.am] && (S.sh === '不限' || r.ship === S.sh))
    const TABS = [[0, '待发货'], [1, '待付款'], [2, '配送中'], [3, '已完成'], ['all', '全部']]
    const MORE = [[4, '已取消'], [5, '已退款']]
    const drawTabs = () => {
      const b = base(), c = (k) => (k === 'all' ? b.length : b.filter((r) => r.st === k).length), inMore = MORE.some(([k]) => k === S.tab)
      $(el, '.sts').innerHTML = TABS.map(([k, t]) => `<button type="button" data-tab="${k}" class="${S.tab === k ? 'on' : ''}">${t}<em class="${c(k) ? '' : 'z0'}">${c(k)}</em></button>`).join('') + `<span class="z-dd" data-ix="dd"><button type="button" data-tg class="${inMore ? 'on' : ''}" style="${inMore ? 'background:var(--card);border-radius:4px;font-weight:600;box-shadow:0 1px 2px var(--sh12)' : ''}"><span>${inMore ? MORE.find(([k]) => k === S.tab)[1] : '更多'}</span>${ic('down', 's')}</button><div class="menu">${MORE.map(([k, t]) => `<div data-o data-tab="${k}" class="${S.tab === k ? 'on' : ''}">${t}<em style="margin-left:8px;font-style:normal;font-size:12px;color:var(--ink3)">${c(k)}</em></div>`).join('')}</div></span>`
    }
    const drawChips = () => {
      const cs = []; if (S.rg !== 'd7') cs.push(['rg', ODRANGE[S.rg]]); if (S.st !== '全部门店') cs.push(['st', S.st]); if (S.am !== '不限') cs.push(['am', '金额 ' + S.am]); if (S.sh !== '不限') cs.push(['sh', S.sh])
      const c = $(el, '.chips'); c.hidden = !cs.length; c.innerHTML = cs.length ? '已生效：' + cs.map(([k, t]) => `<span class="c">${t}<button type="button" data-rm="${k}" aria-label="移除${t}">${ic('close', 's')}</button></span>`).join('') + '<button type="button" class="z-btn t" data-act="clrf">清空</button>' : ''
    }
    const draw = () => {
      drawTabs(); drawChips()
      let list = base().filter((r) => S.tab === 'all' || r.st === S.tab).sort((a, b) => (S.sort === 'at' ? a.at - b.at : a.amt - b.amt) * S.dir)
      if (S.tab === 0 && S.sort === 'at' && S.dir === 1) list = list /* 待发货：等得最久的在前 */
      const n = list.length, pages = Math.max(1, Math.ceil(n / S.size)); S.page = Math.min(S.page, pages); const cur = list.slice((S.page - 1) * S.size, S.page * S.size)
      body.innerHTML = cur.length ? cur.map((r) => { const idx = rows.indexOf(r); return `<tr data-i="${idx}" class="${S.sel.has(idx) ? 'sel' : ''}"><td>${ck(S.sel.has(idx) ? 1 : 0, `data-c aria-label="选择订单"`)}</td><td class="no">${r.no}</td><td><span class="z-who">${critter(r.who, 24)}${NAMES[r.who]}</span></td><td class="l">${esc(r.goods)}</td><td class="r">${money(r.amt)}</td><td>${tag(OD_ST[r.st][0], OD_ST[r.st][1])}</td><td>${fmtT(r.at)}</td><td><button type="button" class="z-btn t" data-act="view">查看</button>${r.st === 0 ? '<button type="button" class="z-btn t" data-act="ship1">发货</button>' : ''}</td></tr>` }).join('') : `<tr><td colspan="8" class="emp">${S.q || S.st !== '全部门店' || S.am !== '不限' || S.sh !== '不限' ? '没有符合条件的订单，试试清空筛选' : '这个状态下暂时没有订单'}</td></tr>`
      $$(el, 'th.so').forEach((th) => { th.classList.toggle('on', th.dataset.sort === S.sort); $(th, '.z-ic').innerHTML = sv(th.dataset.sort === S.sort ? (S.dir === 1 ? 'arrowup' : 'arrowdown') : 'sort') })
      const sel = cur.filter((r) => S.sel.has(rows.indexOf(r))).length, all = $(el, '[data-all]'); all.classList.toggle('on', cur.length > 0 && sel === cur.length); all.classList.toggle('part', sel > 0 && sel < cur.length)
      const bar = $(el, '.bat'); bar.hidden = !S.sel.size; $(bar, '.bn').textContent = S.sel.size; const can = [...S.sel].every((i) => rows[i].st === 0); const sb = $(bar, '[data-act=ship]'); sb.disabled = !can; sb.title = can ? '' : '只能批量发货「待发货」的订单'
      const bt = pgBtns(S.page, pages)
      $(el, '.pgf').innerHTML = `<span>共 ${n} 条</span>${dd([10, 20, 50, 100].map((x) => [x, x + ' 条/页']), S.size, { up: true, attr: 'data-sz' })}<div class="pb"><button type="button" data-pn="${S.page - 1}" ${S.page <= 1 ? 'disabled' : ''} aria-label="上一页">${ic('left', 's')}</button>${bt.map((x) => (x === '…' ? '<span>…</span>' : `<button type="button" data-pn="${x}" class="${x === S.page ? 'on' : ''}">${x}</button>`)).join('')}<button type="button" data-pn="${S.page + 1}" ${S.page >= pages ? 'disabled' : ''} aria-label="下一页">${ic('right', 's')}</button></div>`
    }
    draw()
    const setSt = (idx, st) => { rows[idx].st = st }
    root.addEventListener('click', (e) => {
      const tb = e.target.closest('[data-tab]'); if (tb) { S.tab = tb.dataset.tab === 'all' ? 'all' : +tb.dataset.tab; S.page = 1; S.sel.clear(); setTimeout(draw, 0); return }
      const th = e.target.closest('th.so'); if (th) { if (S.sort === th.dataset.sort) S.dir = -S.dir; else { S.sort = th.dataset.sort; S.dir = 1 } draw(); return }
      const pn = e.target.closest('[data-pn]'); if (pn && !pn.disabled) { S.page = +pn.dataset.pn; draw(); return }
      const sz = e.target.closest('[data-sz] [data-o]'); if (sz) { S.size = +sz.dataset.val; S.page = 1; setTimeout(draw, 0); return }
      const f = e.target.closest('[data-f] [data-o]'); if (f) { S[f.closest('[data-f]').dataset.f] = f.dataset.val; S.page = 1; setTimeout(draw, 0); return }
      const rm = e.target.closest('[data-rm]'); if (rm) { S[rm.dataset.rm] = rm.dataset.rm === 'rg' ? 'd7' : rm.dataset.rm === 'st' ? '全部门店' : '不限'; $$(el, `[data-f="${rm.dataset.rm}"] [data-label]`).forEach((l) => (l.textContent = rm.dataset.rm === 'rg' ? '近 7 天' : rm.dataset.rm === 'st' ? '全部门店' : '不限')); S.page = 1; draw(); return }
      const tr = e.target.closest('tbody tr'), i = tr ? +tr.dataset.i : -1
      if (e.target.closest('[data-c]') && tr) { S.sel.has(i) ? S.sel.delete(i) : S.sel.add(i); draw(); return }
      if (e.target.closest('[data-all]')) { const cur = $$(el, 'tbody tr[data-i]').map((t) => +t.dataset.i), on = !cur.every((x) => S.sel.has(x)); cur.forEach((x) => (on ? S.sel.add(x) : S.sel.delete(x))); draw(); return }
      const a = e.target.closest('[data-act]'); if (!a) return
      const act = a.dataset.act
      if (act === 'more') { const m = $(el, '.more'); m.hidden = !m.hidden; a.setAttribute('aria-expanded', !m.hidden); a.classList.toggle('on', !m.hidden) }
      if (act === 'clrf') { Object.assign(S, { rg: 'd7', st: '全部门店', am: '不限', sh: '不限', page: 1 }); $$(el, '.fl [data-label], .more [data-label]').forEach((l, k) => { const t = ['近 7 天', '全部门店', '不限', '不限'][k]; if (t) l.textContent = t }); draw() }
      if (act === 'clr') { S.sel.clear(); draw() }
      if (act === 'view' || act === 'ship1') {
        const r = rows[i]; if (act === 'ship1') { tr.classList.add('out'); setTimeout(() => { setSt(i, 2); draw(); toast(root, `订单 ${r.no.slice(-6)} 已发货`) }, 200); return }
        S.cur = i; $(el, '.dtl').innerHTML = `<dt>订单号</dt><dd>${r.no}</dd><dt>状态</dt><dd>${tag(OD_ST[r.st][0], OD_ST[r.st][1])}</dd><dt>客户</dt><dd class="z-who">${critter(r.who, 22)}${NAMES[r.who]}</dd><dt>商品</dt><dd>${esc(r.goods)}（共 ${r.n} 件）</dd><dt>金额</dt><dd>${money(r.amt)}</dd><dt>门店</dt><dd>${r.store} · ${r.ship}</dd><dt>下单时间</dt><dd>${fmtT(r.at)}</dd><dt>收货地址</dt><dd>${r.addr}</dd>`; $(el, '[data-act=shipone]').hidden = r.st !== 0; openOv(root, 'od')
      }
      if (act === 'shipone') { closeOv(a); const r = rows[S.cur]; setSt(S.cur, 2); draw(); toast(root, `订单 ${r.no.slice(-6)} 已发货`) }
      if (act === 'ship') { const n = S.sel.size; S.sel.forEach((x) => setSt(x, 2)); S.sel.clear(); draw(); toast(root, `已发货 ${n} 单`) }
    })
    $(el, '.sq input').addEventListener('input', (e) => { S.q = e.target.value.trim().toLowerCase(); S.page = 1; draw() })
    wireEsc(root)
  },
})

const crumb = (up, cur) => `${up.map((t) => `<button type="button" data-toast="返回「${t}」">${t}</button>${ic('right', 's')}`).join('')}<b>${cur}</b>`

/* ---- AD-PAGE-003 详情页 ---- */
const DT_STEPS = [['待付款', '09:12'], ['待发货', '09:13'], ['配送中', ''], ['已完成', '']]
const DT_ITEMS = [['无线降噪耳机', '石墨灰', 599, 1, 0], ['轻量跑鞋', '云白 · 42 码', 329, 2, 1], ['护眼台灯', '三档调光', 219, 1, 5]]
const dtSteps = (cur, times) => DT_STEPS.map(([t], i) => `<li class="${i < cur ? 'done' : i === cur ? 'now' : ''}"><span class="cr">${i < cur ? ic('check', 's') : i + 1}</span><b>${t}</b><em>${times[i] || '—'}</em></li>`).join('')
const dtLog = (rows) => `<ol class="tl2">${rows.map(([a, b, c]) => `<li><i></i><div><b>${a}</b><p>${b}</p></div><em>${c}</em></li>`).join('')}</ol>`
def({
  id: 'AD-PAGE-003', name: '详情页', style: '页头与标签页', wide: true,
  fit: '订单、会员、工单等对象的详情：面包屑加对象名做页头，关键信息与进度在上，明细、物流、记录放标签页，主操作随状态变化',
  avoid: '只想快速看几个字段时（用居中悬浮的详情面板）；字段极多的档案类对象（改成分组描述列表 + 锚点导航）',
  kw: '详情页 订单详情 页头 描述列表 标签页 时间线 步骤 面包屑 发货 detail',
  css: K('adpage003', 'btn tag in tabs modal tbl dd') + SHELL_CSS.replace(/§/g, '.adpage003') + `.adpage003 .hdc{padding:16px 20px}.adpage003 .hdc .t{display:flex;align-items:center;justify-content:space-between;gap:12px;flex-wrap:wrap}.adpage003 .hdc .t .l{display:flex;align-items:center;gap:10px}.adpage003 .hdc h4{font-size:18px;font-weight:600;font-variant-numeric:tabular-nums}.adpage003 .hdc .r{display:flex;gap:8px}.adpage003 .kv{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:12px 24px;margin-top:14px;padding-top:14px;border-top:1px solid var(--line)}.adpage003 .kv dt{font-size:12px;color:var(--ink3)}.adpage003 .kv dd{margin-top:2px}.adpage003 .kv dd.big{font-size:22px;font-weight:700;line-height:1.3;font-variant-numeric:tabular-nums}.adpage003 .stp{display:flex;margin-top:16px;padding-top:16px;border-top:1px solid var(--line)}.adpage003 .stp li{position:relative;flex:1;display:flex;flex-direction:column;align-items:center;gap:2px;text-align:center}.adpage003 .stp li:not(:last-child)::after{content:"";position:absolute;left:calc(50% + 20px);right:calc(-50% + 20px);top:13px;height:2px;background:var(--n7)}.adpage003 .stp li.done:not(:last-child)::after{background:var(--ok-fill)}.adpage003 .stp .cr{position:relative;z-index:1;display:flex;align-items:center;justify-content:center;width:28px;height:28px;margin-bottom:4px;border-radius:50%;border:2px solid var(--n8);background:var(--card);font-size:12px;font-weight:600;color:var(--ink3)}.adpage003 .stp li.done .cr{border-color:var(--ok);background:var(--okb);color:var(--ok)}.adpage003 .stp li.now .cr{border-color:var(--p);background:var(--p);color:#fff}.adpage003 .stp b{font-weight:600}.adpage003 .stp li:not(.done):not(.now) b{color:var(--ink3);font-weight:400}.adpage003 .stp em{font-style:normal;font-size:12px;color:var(--ink3)}.adpage003 .two{display:grid;grid-template-columns:minmax(0,1fr) 300px;gap:16px;margin-top:16px}.adpage003 .mainc{min-width:0}.adpage003 .z-tabs{padding:0 20px}.adpage003 .pnl{padding:16px 20px 20px}.adpage003 .pr{display:flex;align-items:center;gap:12px;text-align:left}.adpage003 .pr img{width:44px;height:44px;border-radius:8px;object-fit:cover;flex:none}.adpage003 .pr span{display:flex;flex-direction:column;line-height:1.4}.adpage003 .pr em{font-style:normal;font-size:12px;color:var(--ink3)}.adpage003 .tot{display:flex;flex-direction:column;align-items:flex-end;gap:6px;margin-top:14px;color:var(--ink2)}.adpage003 .tot div{display:flex;gap:24px;min-width:220px;justify-content:space-between;font-variant-numeric:tabular-nums}.adpage003 .tot .pay{margin-top:4px;padding-top:10px;border-top:1px solid var(--line);color:var(--ink);font-weight:600}.adpage003 .tot .pay b{font-size:22px;font-weight:700;color:var(--price)}.adpage003 .tl2{display:flex;flex-direction:column}.adpage003 .tl2 li{position:relative;display:flex;gap:12px;padding:0 0 16px}.adpage003 .tl2 li:not(:last-child)::before{content:"";position:absolute;left:4px;top:14px;bottom:-2px;width:2px;background:var(--n5)}.adpage003 .tl2 li>i{flex:none;width:10px;height:10px;margin-top:6px;border-radius:50%;background:var(--n9)}.adpage003 .tl2 li:first-child>i{background:var(--p)}.adpage003 .tl2 li>div{flex:1}.adpage003 .tl2 b{font-weight:400}.adpage003 .tl2 li:first-child b{font-weight:600}.adpage003 .tl2 p{font-size:12px;color:var(--ink3);margin-top:2px}.adpage003 .tl2 em{font-style:normal;font-size:12px;color:var(--ink3);white-space:nowrap}.adpage003 .tl2 li.nw{animation:zbin .25s cubic-bezier(.2,0,0,1)}.adpage003 .none{padding:32px 0;text-align:center;color:var(--ink3)}.adpage003 .sd2{padding:16px 20px;align-self:start}.adpage003 .sd2 h4{font-size:14px;font-weight:600;margin-bottom:12px}.adpage003 .sd2 .by{display:flex;align-items:center;gap:10px}.adpage003 .sd2 .by span{display:flex;flex-direction:column;line-height:1.4}.adpage003 .sd2 dl{display:flex;flex-direction:column;gap:10px;margin-top:14px;padding-top:14px;border-top:1px solid var(--line)}.adpage003 .sd2 dt{font-size:12px;color:var(--ink3)}.adpage003 .sd2 dd{margin-top:2px;overflow-wrap:anywhere}.adpage003 .fm{display:flex;flex-direction:column;gap:14px}.adpage003 .fm .z-lb{display:block;margin-bottom:6px}`,
  html: () => `<div class="adpage003">${shell('order', `<div class="z-card hdc"><div class="t"><div class="l"><h4>SO20261104128</h4>${tag('待发货', 'in dot')}</div><div class="r"><button type="button" class="z-btn" data-toast="已发送到打印机">${ic('file')}打印</button><button type="button" class="z-btn p" data-act="main">发货</button></div></div><dl class="kv"><div><dt>订单金额</dt><dd class="big">¥1,258.00</dd></div><div><dt>支付方式</dt><dd>微信支付</dd></div><div><dt>下单时间</dt><dd>11-04 09:12</dd></div><div><dt>所属门店</dt><dd>示例旗舰店</dd></div></dl><ol class="stp">${dtSteps(1, ['09:12', '09:13'])}</ol></div><div class="two"><div class="z-card mainc">${tabs([['it', '商品明细', 3], ['lg', '物流进度'], ['op', '操作记录']], 'it', 'data-g="dt"')}<div class="pnl" data-p="it" data-g="dt"><table class="z-tbl"><thead><tr><th>商品</th><th style="width:110px">单价</th><th style="width:70px">数量</th><th style="width:110px">小计</th></tr></thead><tbody>${DT_ITEMS.map(([n, s, p, q, im]) => `<tr><td class="l"><span class="pr"><img src="${P(im)}" alt=""><span><b>${n}</b><em>${s}</em></span></span></td><td class="r">${money(p)}</td><td>${q}</td><td class="r">${money(p * q)}</td></tr>`).join('')}</tbody></table><div class="tot"><div><span>商品总额</span><span>¥1,476.00</span></div><div><span>运费</span><span>¥0.00</span></div><div><span>满 1,000 减 218</span><span>-¥218.00</span></div><div class="pay"><span>实付金额</span><b>¥1,258.00</b></div></div></div><div class="pnl" data-p="lg" data-g="dt" hidden><div class="lgb"><p class="none">订单尚未发货，发货后会在这里显示物流进度</p></div></div><div class="pnl" data-p="op" data-g="dt" hidden><div class="opb">${dtLog([['买家提交订单', '林小满', '11-04 09:12'], ['微信支付成功', '实付 ¥1,258.00', '11-04 09:13'], ['系统自动审核通过', '无风险订单', '11-04 09:13']].reverse())}</div></div></div><aside class="z-card sd2"><h4>买家信息</h4><div class="by">${critter(0, 40)}<span><b>林小满</b><em style="font-style:normal;font-size:12px;color:var(--ink3)">138****5678</em></span>${tag('金卡会员', 'in')}</div><dl><div><dt>收货信息</dt><dd>林小满，138****5678<br>上海市静安区南京西路 1266 号 12 楼</dd></div><div><dt>配送方式</dt><dd>骑手配送</dd></div><div><dt>买家留言</dt><dd>请尽量工作日送达，放前台即可。</dd></div></dl></aside></div>`, { crumb: crumb(['订单管理'], '订单详情') })}${modal('sp', '确认发货', '<div class="fm"><div><label class="z-lb">配送方式</label><select class="z-in" data-f="co"><option>骑手配送（同城）</option><option>顺丰速运</option><option>中通快递</option></select></div><div class="nof" hidden><label class="z-lb z-req">快递单号</label><input class="z-in" data-f="no" maxlength="20" placeholder="请输入快递单号"><p class="z-er" hidden>请填写快递单号</p></div></div>', '<button class="z-btn" type="button" data-close>取消</button><button class="z-btn p" type="button" data-act="shipok">确认发货</button>', 420)}</div>`,
  js: (root) => {
    const el = $(root, '.adpage003'); wireShell(root, el, 'order'); let cur = 1; const times = ['09:12', '09:13', '', ''], log = [['买家提交订单', '林小满', '11-04 09:12'], ['微信支付成功', '实付 ¥1,258.00', '11-04 09:13'], ['系统自动审核通过', '无风险订单', '11-04 09:13']].reverse(), lg = []
    const sync = () => {
      $(el, '.stp').innerHTML = dtSteps(cur, times); const t = $(el, '.hdc .z-tag'); t.className = 'z-tag dot ' + (cur === 3 ? 'ok' : 'in'); t.textContent = DT_STEPS[cur][0]
      const b = $(el, '[data-act=main]'); b.hidden = cur === 3; b.textContent = cur === 1 ? '发货' : '确认送达'
      $(el, '.opb').innerHTML = dtLog(log); $(el, '.lgb').innerHTML = lg.length ? dtLog(lg) : '<p class="none">订单尚未发货，发货后会在这里显示物流进度</p>'
    }
    const co = $(el, '[data-f=co]'), nof = $(el, '.nof')
    co.addEventListener('change', () => { nof.hidden = co.selectedIndex === 0 })
    root.addEventListener('click', (e) => {
      const a = e.target.closest('[data-act]'); if (!a) return
      if (a.dataset.act === 'main') {
        if (cur === 1) { co.selectedIndex = 0; nof.hidden = true; $(el, '[data-f=no]').value = ''; openOv(root, 'sp') }
        else { cur = 3; times[3] = '刚刚'; log.unshift(['确认送达', '林小满 · 买家已签收', '刚刚']); lg.unshift(['已签收', '买家已确认收货', '刚刚']); sync(); toast(root, '订单已完成') }
      }
      if (a.dataset.act === 'shipok') {
        const way = co.value, no = $(el, '[data-f=no]'); if (co.selectedIndex > 0 && !no.value.trim()) { no.classList.add('er'); no.nextElementSibling.hidden = false; no.focus(); return }
        closeOv(a); cur = 2; times[2] = '刚刚'; log.unshift(['商家发货', `${way}${co.selectedIndex > 0 ? '，单号 ' + no.value.trim() : ''}`, '刚刚']); lg.unshift([co.selectedIndex ? '快递已揽收' : '骑手已取货', way, '刚刚']); sync(); toast(root, '已发货，买家会收到通知')
      }
    })
    root.addEventListener('input', (e) => { if (e.target.matches('[data-f=no]')) { e.target.classList.remove('er'); e.target.nextElementSibling.hidden = true } })
    wireEsc(root)
  },
})

/* ---- AD-PAGE-004 表单页 ---- */
const FM_REQ = [['name', '商品名称'], ['cat', '商品分类'], ['price', '售价'], ['stock', '库存'], ['img', '封面图']]
def({
  id: 'AD-PAGE-004', name: '表单页', style: '分组+保存栏', wide: true,
  fit: '新建、编辑较长的对象（商品、活动、合同）：单列分组表单，右侧填写进度可点击定位，底部保存栏固定，提交时统一校验并跳到第一个错误',
  avoid: '三四个字段的小表单（用居中悬浮的编辑面板）；需要分步引导的复杂流程（改用分步表单）',
  kw: '表单页 新建商品 分组表单 固定保存栏 校验 必填 进度 草稿 提交 form',
  css: K('adpage004', 'btn tag in dd sw') + SHELL_CSS.replace(/§/g, '.adpage004') + `.adpage004 .lay{display:grid;grid-template-columns:minmax(0,1fr) 248px;gap:16px;align-items:start}.adpage004 .sec{padding:18px 22px 22px;margin-bottom:16px}.adpage004 .sec h4{font-size:16px;font-weight:600;margin-bottom:16px}.adpage004 .fm{display:flex;flex-direction:column;gap:16px;max-width:560px}.adpage004 .fd .z-lb{display:flex;align-items:baseline;margin-bottom:6px}.adpage004 .fd .z-lb small{margin-left:auto;font-size:12px;color:var(--ink3);font-variant-numeric:tabular-nums}.adpage004 .px{position:relative}.adpage004 .px .pre{position:absolute;left:12px;top:0;height:36px;display:flex;align-items:center;color:var(--ink2)}.adpage004 .px .z-in{padding-left:28px}.adpage004 .row2{display:grid;grid-template-columns:1fr 1fr;gap:12px}.adpage004 .stp{display:flex;align-items:center;gap:6px;width:max-content}.adpage004 .stp .z-in{width:96px;text-align:center}.adpage004 .stp .z-x{width:36px;height:36px;border:1px solid var(--bd)}.adpage004 .stp .z-x:disabled{opacity:.4;cursor:not-allowed}.adpage004 .stp em{font-style:normal;color:var(--ink2);margin-left:4px}.adpage004 .chips{display:flex;flex-wrap:wrap;gap:8px}.adpage004 .chips [data-o]{display:inline-flex;align-items:center;height:32px;padding:0 14px;border:1px solid var(--bd);border-radius:8px;cursor:pointer;transition:border-color .15s,background-color .15s}.adpage004 .chips [data-o]:hover{border-color:var(--ink3)}.adpage004 .chips [data-o].on{border-color:var(--p);background:var(--pt);color:var(--p-text)}.adpage004 .ups{display:flex;flex-wrap:wrap;gap:10px}.adpage004 .ups .ui{position:relative;width:76px;height:76px;border-radius:8px;overflow:hidden;border:1px solid var(--line2)}.adpage004 .ups .ui img{width:100%;height:100%;object-fit:cover}.adpage004 .ups .ui b{position:absolute;left:0;bottom:0;right:0;padding:1px 0;background:color-mix(in srgb,var(--scrim) 62%,transparent);color:#fff;font-size:12px;font-weight:400;text-align:center}.adpage004 .ups .ui button{position:absolute;right:3px;top:3px;display:flex;align-items:center;justify-content:center;width:20px;height:20px;border-radius:50%;background:color-mix(in srgb,var(--scrim) 70%,transparent);color:#fff}.adpage004 .ups .addb{display:flex;flex-direction:column;align-items:center;justify-content:center;gap:2px;width:76px;height:76px;border:1px dashed var(--n11);border-radius:8px;color:var(--ink2);font-size:12px;transition:border-color .15s,color .15s}.adpage004 .ups .addb:hover{border-color:var(--p);color:var(--p-text)}.adpage004 .ups.er .addb{border-color:var(--dg)}.adpage004 .swr{display:flex;align-items:center;justify-content:space-between;gap:12px;padding:12px 14px;border-radius:8px;background:var(--sf)}.adpage004 .swr span small{display:block;font-size:12px;color:var(--ink3)}.adpage004 .pgs{position:sticky;top:0;padding:16px 18px}.adpage004 .pgs h4{font-size:14px;font-weight:600;display:flex;align-items:center;justify-content:space-between}.adpage004 .pgs .bar2{height:6px;margin:10px 0 12px;border-radius:3px;background:var(--n4);overflow:hidden}.adpage004 .pgs .bar2 i{display:block;height:100%;border-radius:3px;background:var(--p);transition:width .25s cubic-bezier(.2,0,0,1)}.adpage004 .pgs li button{display:flex;align-items:center;gap:8px;width:100%;height:36px;padding:0 6px;margin:0 -6px;border-radius:8px;text-align:left;color:var(--ink2)}.adpage004 .pgs li button:hover{background:var(--sf)}.adpage004 .pgs .ck2{display:flex;align-items:center;justify-content:center;width:16px;height:16px;border-radius:50%;border:1.5px solid var(--n11);flex:none;color:#fff}.adpage004 .pgs li.ok .ck2{background:var(--ok-fill);border-color:var(--ok)}.adpage004 .pgs li.ok button{color:var(--ink)}.adpage004 .fbar{position:sticky;bottom:-20px;z-index:4;display:flex;align-items:center;justify-content:space-between;gap:12px;margin:0 -20px -20px;padding:12px 20px;background:var(--card);border-top:1px solid var(--line);box-shadow:0 -4px 12px var(--sh05)}.adpage004 .fbar .l{display:flex;align-items:center;gap:10px;color:var(--ink2)}.adpage004 .fbar .r{display:flex;gap:8px}.adpage004 .done{display:flex;align-items:center;gap:10px;padding:10px 14px;margin-bottom:16px;border-radius:8px;background:var(--okb);color:var(--ok)}.adpage004 .done span{color:var(--ok-ink);flex:1}`,
  html: () => `<div class="adpage004">${shell('goods', `<div class="lay"><div class="fmain"><section class="z-card sec" data-sec="base"><h4>基础信息</h4><div class="fm"><div class="fd" data-fd="name"><label class="z-lb z-req" for="adpage004-nm"><span>商品名称</span><small>0/40</small></label><input id="adpage004-nm" class="z-in" data-f="name" maxlength="40" placeholder="例如：无线降噪耳机" autocomplete="off"><p class="z-er" hidden>请填写商品名称</p></div><div class="fd" data-fd="cat"><label class="z-lb z-req"><span>商品分类</span></label>${dd(['请选择分类', '数码配件', '家居生活', '服饰鞋包', '美妆个护'], '请选择分类', { attr: 'data-f="cat"' })}<p class="z-er" hidden>请选择商品分类</p></div><div class="fd"><label class="z-lb"><span>商品卖点</span><small>0/60</small></label><textarea class="z-in" data-f="sell" rows="2" maxlength="60" placeholder="一句话说明商品最吸引人的地方"></textarea></div></div></section><section class="z-card sec" data-sec="price"><h4>价格与库存</h4><div class="fm"><div class="row2"><div class="fd" data-fd="price"><label class="z-lb z-req"><span>售价</span></label><div class="px"><span class="pre">¥</span><input class="z-in" data-f="price" inputmode="decimal" placeholder="0.00"></div><p class="z-er" hidden>请填写大于 0 的售价</p></div><div class="fd" data-fd="orig"><label class="z-lb"><span>划线价</span></label><div class="px"><span class="pre">¥</span><input class="z-in" data-f="orig" inputmode="decimal" placeholder="选填"></div><p class="z-er" hidden>划线价不能低于售价</p></div></div><div class="fd" data-fd="stock"><label class="z-lb z-req"><span>库存</span></label><div class="stp"><button type="button" class="z-x" data-d="-1" aria-label="减少库存" disabled>${ic('minus')}</button><input class="z-in" data-f="stock" inputmode="numeric" value="0"><button type="button" class="z-x" data-d="1" aria-label="增加库存">${ic('plus')}</button><em>件</em></div><p class="z-er" hidden>库存需大于 0</p></div><div class="fd"><label class="z-lb"><span>规格</span></label><div class="chips" data-ix="multi">${['石墨灰', '云白', '鼠尾草绿', '原木色'].map((t) => `<span data-o role="checkbox">${t}</span>`).join('')}</div></div></div></section><section class="z-card sec" data-sec="show"><h4>展示设置</h4><div class="fm"><div class="fd" data-fd="img"><label class="z-lb z-req"><span>商品图片</span><small class="ic">0/5</small></label><div class="ups"><button type="button" class="addb" data-add>${ic('plus')}添加</button></div><p class="z-er" hidden>请至少上传 1 张封面图</p></div><div class="swr"><span>上架方式<small>开启后审核通过即上架，关闭则保存为下架商品</small></span>${sw(true, 'data-f="on" aria-label="审核通过后立即上架"')}</div></div></section></div><aside class="z-card pgs"><h4>填写进度<span class="pc">0/5</span></h4><div class="bar2"><i style="width:0"></i></div><ul>${FM_REQ.map(([k, t]) => `<li data-k="${k}"><button type="button" data-go="${k}"><span class="ck2"></span>${t}</button></li>`).join('')}</ul></aside></div><div class="fbar"><div class="l"><span class="fs">还有 5 项必填没有完成</span></div><div class="r"><button type="button" class="z-btn" data-toast="已取消，返回商品列表">取消</button><button type="button" class="z-btn" data-act="draft">保存草稿</button><button type="button" class="z-btn p" data-act="submit">提交审核</button></div></div>`, { crumb: crumb(['商品管理'], '新建商品') })}</div>`,
  js: (root) => {
    const el = $(root, '.adpage004'); wireShell(root, el, 'goods'); const ct = $(el, '.ct'); let imgs = 0, submitted = false
    const val = (k) => { const q = (s) => $(el, `[data-f="${k}"]`); if (k === 'cat') return $(q('cat'), '[data-label]').textContent.trim(); if (k === 'img') return imgs; return (q(k) ? q(k).value : '').trim() }
    const rule = { name: () => (val('name') ? '' : '请填写商品名称'), cat: () => (val('cat') === '请选择分类' ? '请选择商品分类' : ''), price: () => (+val('price') > 0 ? '' : '请填写大于 0 的售价'), stock: () => (+val('stock') > 0 ? '' : '库存需大于 0'), img: () => (imgs ? '' : '请至少上传 1 张封面图'), orig: () => (val('orig') && +val('orig') < +val('price') ? '划线价不能低于售价' : '') }
    const show = (k, msg) => { const fd = $(el, `[data-fd="${k}"]`), p = $(fd, '.z-er'); p.hidden = !msg; p.textContent = msg || p.textContent; const inp = $(fd, 'input.z-in'); if (inp) inp.classList.toggle('er', !!msg); if (k === 'img') $(fd, '.ups').classList.toggle('er', !!msg) }
    const prog = () => {
      const okc = FM_REQ.filter(([k]) => !rule[k]()).length
      FM_REQ.forEach(([k]) => { const ok = !rule[k](), li = $(el, `.pgs li[data-k="${k}"]`); li.classList.toggle('ok', ok); $(li, '.ck2').innerHTML = ok ? sv('check') : '' })
      $(el, '.pc').textContent = `${okc}/5`; $(el, '.bar2 i').style.width = (okc / 5) * 100 + '%'; $(el, '.fs').textContent = okc === 5 ? '必填项已全部完成，可以提交审核' : `还有 ${5 - okc} 项必填没有完成`
    }
    const touched = new Set()
    const check = (k) => { if (touched.has(k)) show(k, rule[k]()); prog() }
    el.addEventListener('input', (e) => {
      const k = e.target.dataset.f; if (!k) return
      if (k === 'name' || k === 'sell') { const s = e.target.closest('.fd').querySelector('small'); s.textContent = e.target.value.length + '/' + e.target.maxLength }
      if (k === 'price' || k === 'orig') { e.target.value = e.target.value.replace(/[^0-9.]/g, ''); if (k === 'price') check('orig') }
      if (k === 'stock') { e.target.value = e.target.value.replace(/\D/g, ''); $$(el, '.stp .z-x').forEach((b) => (b.disabled = +b.dataset.d < 0 && !+e.target.value)) }
      check(k)
    })
    el.addEventListener('focusout', (e) => { const k = e.target.dataset && e.target.dataset.f; if (k && rule[k]) { touched.add(k); show(k, rule[k]()) } })
    root.addEventListener('click', (e) => {
      const d = e.target.closest('.stp [data-d]'); if (d) { const i = $(el, '[data-f=stock]'); i.value = Math.max(0, (+i.value || 0) + +d.dataset.d); $$(el, '.stp .z-x').forEach((b) => (b.disabled = +b.dataset.d < 0 && !+i.value)); touched.add('stock'); check('stock'); return }
      const swt = e.target.closest('.z-sw'); if (swt) { const on = swt.classList.toggle('on'); swt.setAttribute('aria-checked', on); toast(root, on ? '审核通过后立即上架' : '审核通过后保持下架'); return }
      const o = e.target.closest('[data-f=cat] [data-o]'); if (o) { setTimeout(() => { touched.add('cat'); check('cat') }, 0); return }
      const add = e.target.closest('[data-add]'); if (add) { if (imgs >= 5) { toast(root, '最多上传 5 张'); return } const u = document.createElement('div'); u.className = 'ui'; u.innerHTML = `<img src="${P(imgs % 9)}" alt=""><button type="button" data-rm aria-label="删除图片">${ic('close', 's')}</button>${imgs === 0 ? '<b>封面</b>' : ''}`; add.before(u); imgs++; $(el, '.ic').textContent = imgs + '/5'; add.hidden = imgs >= 5; touched.add('img'); check('img'); return }
      const rm = e.target.closest('[data-rm]'); if (rm) { rm.closest('.ui').remove(); imgs--; $(el, '.ic').textContent = imgs + '/5'; $(el, '[data-add]').hidden = false; const f = $(el, '.ups .ui b'); if (!f && $(el, '.ups .ui')) $(el, '.ups .ui').insertAdjacentHTML('beforeend', '<b>封面</b>'); touched.add('img'); check('img'); return }
      const go = e.target.closest('[data-go]'); if (go) { const fd = $(el, `[data-fd="${go.dataset.go}"]`); ct.scrollTo({ top: fd.offsetTop - 80, behavior: 'smooth' }); const i = $(fd, 'input,textarea'); if (i) setTimeout(() => i.focus({ preventScroll: true }), 250); return }
      const a = e.target.closest('[data-act]'); if (!a) return
      if (a.dataset.act === 'draft') toast(root, '草稿已保存，可以稍后继续')
      if (a.dataset.act === 'submit') {
        if (submitted) { submitted = false; $$(el, '[data-f]').forEach((i) => { if (i.matches('input,textarea')) i.value = i.dataset.f === 'stock' ? '0' : '' }); $$(el, '.ups .ui').forEach((u) => u.remove()); imgs = 0; $(el, '[data-add]').hidden = false; $(el, '.ic').textContent = '0/5'; $(el, '[data-f=cat] [data-label]').textContent = '请选择分类'; touched.clear(); FM_REQ.forEach(([k]) => show(k, '')); const dn = $(el, '.done'); if (dn) dn.remove(); a.textContent = '提交审核'; prog(); ct.scrollTo({ top: 0, behavior: 'smooth' }); return }
        let first = null; FM_REQ.concat([['orig', '']]).forEach(([k]) => { touched.add(k); const m = rule[k](); show(k, m); if (m && !first) first = k }); prog()
        if (first) { const fd = $(el, `[data-fd="${first}"]`); ct.scrollTo({ top: fd.offsetTop - 80, behavior: 'smooth' }); const i = $(fd, 'input'); if (i) setTimeout(() => i.focus({ preventScroll: true }), 250); toast(root, '有内容没有填好，已定位到第一处'); return }
        submitted = true; a.textContent = '再新建一个'; ct.insertAdjacentHTML('afterbegin', `<div class="done">${ic('checkc', 'l')}<span>已提交审核，通常 1 个工作日内完成，结果会通过站内信通知你。</span></div>`); ct.scrollTo({ top: 0, behavior: 'smooth' }); toast(root, '已提交审核')
      }
    })
    prog()
  },
})

/* ---- AD-PAGE-005 设置页 ---- */
const ST_NAV = [['store', '门店信息', 'bz_shop'], ['biz', '营业设置', 'clock'], ['ntf', '通知偏好', 'bell'], ['sec', '账号安全', 'shield']]
const ST_STORE = { name: '示例旗舰店', intro: '都市通勤与居家好物，次日达', tel: '021-5566 7788', addr: '上海市静安区示例路 100 号 示例广场 3 层', note: '11 月 11 日起 10:00–22:00 延长营业，订单满 99 元包邮。' }
const stPanel = (k, d = ST_STORE) => {
  if (k === 'store') return `<div class="ph2"><h4>门店信息</h4><p>展示在小程序首页和订单小票上</p></div><div class="fm"><div class="fd"><label class="z-lb z-req">门店名称</label><input class="z-in" data-f="name" maxlength="20" value="${d.name}"><p class="z-er" hidden></p></div><div class="fd"><label class="z-lb z-req">联系电话</label><input class="z-in" data-f="tel" maxlength="16" value="${d.tel}"><p class="z-er" hidden></p></div><div class="fd"><label class="z-lb z-req">门店地址</label><input class="z-in" data-f="addr" maxlength="50" value="${d.addr}"><p class="z-er" hidden></p></div><div class="fd"><label class="z-lb">门店公告<small class="cnt">${d.note.length}/100</small></label><textarea class="z-in" data-f="note" rows="2" maxlength="100">${d.note}</textarea></div></div><div class="sf"><span class="hnt">没有未保存的修改</span><div class="r"><button type="button" class="z-btn" data-act="undo" disabled>撤销</button><button type="button" class="z-btn p" data-act="save" disabled>保存</button></div></div>`
  if (k === 'biz') return `<div class="ph2"><h4>营业设置</h4><p>营业状态只有一份，停业后小程序可浏览、不可下单</p></div><div class="opn"><span class="dot2"></span><div><b class="os">营业中</b><p class="od">今天 08:00 已开业，距打烊还有 7 小时</p></div><button type="button" class="z-btn" data-act="toggle">一键停业</button></div><div class="fm" style="margin-top:20px"><div class="hrs"><span>周一至周五</span>${sw(true, 'data-hr aria-label="周一至周五营业"')}<select class="z-in sm"><option>08:00</option><option>09:00</option><option>10:00</option></select><em>至</em><select class="z-in sm"><option>21:00</option><option>22:00</option><option>23:00</option></select></div><div class="hrs"><span>周六、周日</span>${sw(true, 'data-hr aria-label="周末营业"')}<select class="z-in sm"><option>09:00</option><option>10:00</option></select><em>至</em><select class="z-in sm"><option>22:00</option><option>23:00</option></select></div></div><div class="sf"><span class="hnt">营业时间修改后自动保存</span></div>`
  if (k === 'ntf') return `<div class="ph2"><h4>通知偏好</h4><p>开关点一下立即生效</p></div><div class="rows">${[['新订单提醒', '有新订单时在右上角弹出提醒并响铃', 1], ['库存预警', '商品库存低于预警线时通知', 1], ['每日经营日报', '每天 08:00 发送昨日经营数据到邮箱', 0]].map(([t, d, on]) => `<div class="row"><div><b>${t}</b><p>${d}</p></div>${sw(on, `data-nf aria-label="${t}"`)}</div>`).join('')}</div>`
  return `<div class="ph2"><h4>账号安全</h4><p>保护账号与门店资金安全</p></div><div class="rows"><div class="row"><div><b>登录密码</b><p>上次修改在 45 天前，建议定期更换</p></div><button type="button" class="z-btn" data-open="pw">修改</button></div><div class="row"><div><b>绑定手机</b><p>138****5678，用于登录验证和找回密码</p></div><button type="button" class="z-btn" data-toast="更换手机号需要短信验证，示例中不演示">更换</button></div><div class="row"><div><b>登录二次验证</b><p>开启后登录需再输入短信验证码</p></div>${sw(0, 'data-nf aria-label="登录二次验证"')}</div><div class="row"><div><b>已登录的设备</b><p>当前共 3 台设备在线</p></div><button type="button" class="z-btn" data-toast="设备管理为示例入口">管理</button></div></div>`
}
def({
  id: 'AD-PAGE-005', name: '设置页', style: '分类+表单', wide: true,
  fit: '系统设置、门店设置、账号设置：左侧分类、右侧表单，保存按钮在修改后才可用，切换分类时有未保存修改会先询问；开关类即时生效',
  avoid: '设置项只有一两个（直接放在对应业务页）；会频繁变动的运营内容（放进业务模块，不进设置页）',
  kw: '设置页 系统设置 门店信息 营业设置 账号安全 一键停业 修改密码 保存 settings 分类导航',
  css: K('adpage005', 'btn tag in sw modal dd') + SHELL_CSS.replace(/§/g, '.adpage005') + `.adpage005 .ct{display:grid;grid-template-columns:200px minmax(0,1fr);gap:16px;align-items:start}.adpage005 .nv{padding:8px;position:sticky;top:0}.adpage005 .nv button{display:flex;align-items:center;gap:10px;width:100%;height:40px;padding:0 12px;border-radius:8px;color:var(--ink2);transition:background-color .15s}.adpage005 .nv button:hover{background:var(--sf)}.adpage005 .nv button.on{background:var(--pt);color:var(--p-text);font-weight:600}.adpage005 .pn{padding:22px 26px 0;min-height:100%}.adpage005 .ph2{margin-bottom:20px}.adpage005 .ph2 h4{font-size:16px;font-weight:600}.adpage005 .ph2 p{font-size:12px;color:var(--ink3);margin-top:2px}.adpage005 .fm{display:flex;flex-direction:column;gap:16px;max-width:520px}.adpage005 .fd .z-lb{display:flex;align-items:baseline;margin-bottom:6px}.adpage005 .fd .z-lb small{margin-left:auto;font-size:12px;color:var(--ink3);font-variant-numeric:tabular-nums}.adpage005 .sf{display:flex;align-items:center;justify-content:space-between;gap:12px;margin:24px -26px 0;padding:14px 26px;border-top:1px solid var(--line)}.adpage005 .sf .hnt{font-size:12px;color:var(--ink3)}.adpage005 .sf .r{display:flex;gap:8px}.adpage005 .rows{max-width:640px}.adpage005 .row{display:flex;align-items:center;justify-content:space-between;gap:20px;padding:16px 0;border-bottom:1px solid var(--line)}.adpage005 .row b{font-weight:600}.adpage005 .row p{font-size:12px;color:var(--ink3);margin-top:2px}.adpage005 .opn{display:flex;align-items:center;gap:14px;max-width:640px;padding:16px 18px;border-radius:12px;background:var(--okb)}.adpage005 .opn.off{background:var(--mub)}.adpage005 .opn .dot2{width:10px;height:10px;border-radius:50%;background:var(--ok-fill);flex:none}.adpage005 .opn.off .dot2{background:var(--n12)}.adpage005 .opn b{font-size:16px;font-weight:600}.adpage005 .opn p{font-size:12px;color:var(--ink2);margin-top:2px}.adpage005 .opn .z-btn{margin-left:auto}.adpage005 .hrs{display:flex;align-items:center;gap:12px}.adpage005 .hrs span{width:88px;color:var(--ink2)}.adpage005 .hrs .z-in{width:96px}.adpage005 .hrs em{font-style:normal;color:var(--ink3)}.adpage005 .hrs .z-sw:not(.on)~select,.adpage005 .hrs .z-sw:not(.on)~em{opacity:.4;pointer-events:none}.adpage005 .ckl{display:flex;flex-direction:column;gap:10px;line-height:1.5}.adpage005 .ckl li{display:flex;align-items:flex-start;gap:8px}.adpage005 .ckl .z-ic{color:var(--ok);margin-top:2px}.adpage005 .ckl .no .z-ic{color:var(--wn)}.adpage005 .stre{display:flex;gap:4px;margin-top:8px}.adpage005 .stre i{flex:1;height:4px;border-radius:2px;background:var(--n6)}.adpage005 .stre i.on{background:var(--warn-fill)}.adpage005 .stre.s3 i.on{background:var(--ok-fill)}.adpage005 .stl{font-size:12px;color:var(--ink3);margin-top:4px}.adpage005 .fm2{display:flex;flex-direction:column;gap:14px}.adpage005 .fm2 .z-lb{display:block;margin-bottom:6px}@media(max-width:1100px){.adpage005 .ct{grid-template-columns:minmax(0,1fr)}}`,
  html: () => `<div class="adpage005">${shell('set', `<nav class="z-card nv" aria-label="设置分类">${ST_NAV.map(([k, t, i], n) => `<button type="button" data-cat="${k}" class="${n === 0 ? 'on' : ''}">${ic(i)}${t}</button>`).join('')}</nav><section class="z-card pn">${stPanel('store')}</section>`)}${modal('dc', '有未保存的修改', '<p style="line-height:1.6">「门店信息」里的修改还没有保存，离开后会丢失。</p>', '<button class="z-btn" type="button" data-close>继续编辑</button><button class="z-btn" type="button" data-act="drop">放弃修改</button><button class="z-btn p" type="button" data-act="keep">保存并离开</button>', 440)}${modal('sc', '确认停业', '<div class="ckl"><p style="margin-bottom:6px">停业后会立即生效：</p><ul class="ckl"><li>' + ic('checkc') + '<span>小程序仍可浏览，但不能下单；顶部显示停业公告</span></li><li>' + ic('checkc') + '<span>已支付的在途订单继续处理，不受影响</span></li><li>' + ic('checkc') + '<span>已登记的设备按停业动作统一下发（关闭点餐屏、灯箱等）</span></li></ul></div>', '<button class="z-btn" type="button" data-close>再想想</button><button class="z-btn p" type="button" data-act="scok">确认停业</button>', 440)}${modal('oc', '开业检查', '<ul class="ckl"><li>' + ic('checkc') + '<span>设备在线：收银终端、打印机均在线</span></li><li>' + ic('checkc') + '<span>商品库存：无售罄的主推商品</span></li><li class="no">' + ic('alert') + '<span>公告：停业公告仍在展示，开业后会自动撤下</span></li></ul>', '<button class="z-btn" type="button" data-close>取消</button><button class="z-btn p" type="button" data-act="ocok">确认开业</button>', 440)}${modal('pw', '修改登录密码', '<div class="fm2"><div><label class="z-lb z-req">当前密码</label><input class="z-in" type="password" data-pw="old" autocomplete="off"></div><div><label class="z-lb z-req">新密码</label><input class="z-in" type="password" data-pw="new" autocomplete="off" placeholder="至少 8 位，含字母和数字"><div class="stre"><i></i><i></i><i></i></div><p class="stl">强度：未填写</p></div><div><label class="z-lb z-req">确认新密码</label><input class="z-in" type="password" data-pw="cf" autocomplete="off"><p class="z-er" hidden>两次输入的密码不一致</p></div></div>', '<button class="z-btn" type="button" data-close>取消</button><button class="z-btn p" type="button" data-act="pwok" disabled>确认修改</button>', 420)}</div>`,
  js: (root) => {
    const el = $(root, '.adpage005'), pn = $(el, '.pn'); wireShell(root, el, 'set'); let cat = 'store', to = null; const st = { ...ST_STORE }; let saved = { ...ST_STORE }
    const bad = { name: (v) => (v.trim() ? '' : '请填写门店名称'), tel: (v) => (/^[0-9\-\s]{7,16}$/.test(v.trim()) ? '' : '请填写正确的电话，例如 021-5566 7788'), addr: (v) => (v.trim() ? '' : '请填写门店地址') }
    const dirty = () => Object.keys(st).some((k) => st[k] !== saved[k]), valid = () => !bad.name(st.name) && !bad.tel(st.tel) && !bad.addr(st.addr)
    const sync = () => { if (cat !== 'store') return; $(pn, '[data-act=save]').disabled = !(dirty() && valid()); $(pn, '[data-act=undo]').disabled = !dirty(); $(pn, '.hnt').textContent = dirty() ? (valid() ? '有未保存的修改' : '请先修正标红的内容') : '没有未保存的修改' }
    const goto = (k) => { cat = k; pn.innerHTML = stPanel(k, saved); $$(el, '.nv button').forEach((b) => b.classList.toggle('on', b.dataset.cat === k)); if (k === 'store') { Object.assign(st, saved); sync() } if (k === 'biz') opn(isOpen) }
    const opn = (isOpen) => { const o = $(pn, '.opn'); if (!o) return; o.classList.toggle('off', !isOpen); $(o, '.os').textContent = isOpen ? '营业中' : '已停业'; $(o, '.od').textContent = isOpen ? '今天 08:00 已开业，距打烊还有 7 小时' : '小程序可浏览、不可下单，在途订单继续处理'; $(o, '.z-btn').textContent = isOpen ? '一键停业' : '一键开业' }
    let isOpen = true
    root.addEventListener('click', (e) => {
      const c = e.target.closest('[data-cat]'); if (c) { const k = c.dataset.cat; if (k === cat) return; if (cat === 'store' && dirty()) { to = k; openOv(root, 'dc'); return } goto(k); return }
      const nf = e.target.closest('[data-nf]'); if (nf) { const on = nf.classList.toggle('on'); nf.setAttribute('aria-checked', on); toast(root, on ? '已开启' : '已关闭'); return }
      const hr = e.target.closest('[data-hr]'); if (hr) { const on = hr.classList.toggle('on'); hr.setAttribute('aria-checked', on); toast(root, '营业时间已更新'); return }
      const a = e.target.closest('[data-act]'); if (!a) return
      const act = a.dataset.act
      if (act === 'save') { saved = { ...st }; sync(); toast(root, '门店信息已保存') }
      if (act === 'undo') { Object.assign(st, saved); goto('store'); toast(root, '已撤销修改') }
      if (act === 'drop') { closeOv(a); const k = to; goto(k) }
      if (act === 'keep') { if (!valid()) { closeOv(a); toast(root, '请先修正标红的内容'); return } saved = { ...st }; closeOv(a); goto(to); toast(root, '已保存') }
      if (act === 'toggle') openOv(root, isOpen ? 'sc' : 'oc')
      if (act === 'scok') { closeOv(a); isOpen = false; opn(false); toast(root, '已停业，小程序暂停下单') }
      if (act === 'ocok') { closeOv(a); isOpen = true; opn(true); toast(root, '已开业，小程序恢复下单') }
      if (act === 'pwok') { closeOv(a); toast(root, '密码已修改，下次登录生效') }
    })
    pn.addEventListener('input', (e) => {
      const f = e.target.dataset.f; if (!f) return; st[f] = e.target.value
      if (f === 'note') $(pn, '.cnt').textContent = e.target.value.length + '/100'
      if (bad[f]) { const m = bad[f](e.target.value), p = e.target.parentNode.querySelector('.z-er'); e.target.classList.toggle('er', !!m); p.hidden = !m; p.textContent = m }
      sync()
    })
    root.addEventListener('input', (e) => {
      const k = e.target.dataset.pw; if (!k) return
      const g = (x) => $(root, `[data-pw=${x}]`).value, n = g('new'); let s = 0; if (n.length >= 8) s++; if (/[a-zA-Z]/.test(n) && /\d/.test(n)) s++; if (n.length >= 12 && /[^a-zA-Z0-9]/.test(n)) s++
      const bar = $(root, '.stre'); bar.className = 'stre s' + s; $$(bar, 'i').forEach((i, x) => i.classList.toggle('on', x < s)); $(root, '.stl').textContent = '强度：' + (!n ? '未填写' : ['弱', '一般', '较强', '很强'][s])
      const mis = g('cf') && g('cf') !== n; const er = $(root, '[data-pw=cf]').nextElementSibling; er.hidden = !mis; $(root, '[data-pw=cf]').classList.toggle('er', !!mis)
      $(root, '[data-act=pwok]').disabled = !(g('old') && s >= 2 && g('cf') === n)
    })
    wireEsc(root)
  },
})

/* ---- 登录表单（AD-PAGE-006、007 共用）---- */
const LG_CSS = `§ .lgf{width:100%;max-width:380px}§ .lgf .lh{display:flex;align-items:center;gap:10px;margin-bottom:28px}§ .lgf .lg2{display:flex;align-items:center;justify-content:center;width:36px;height:36px;border-radius:8px;background:var(--pt);color:var(--p-text)}§ .lgf .lh b{font-size:16px;font-weight:600}§ .lgf .lt{font-size:22px;font-weight:700;line-height:1.3}§ .lgf .ls{margin:6px 0 20px;color:var(--ink2)}§ .lgf .z-tabs{gap:24px;margin-bottom:20px}§ .lgf .z-tabs button{height:40px}§ .lgf .fi{position:relative;margin-bottom:14px}§ .lgf .fi>.z-ic{position:absolute;left:12px;top:12px;color:var(--ink3);pointer-events:none}§ .lgf .fi .z-in{height:40px;padding-left:38px}§ .lgf .fi .eye{position:absolute;right:4px;top:4px;width:32px;height:32px;display:flex;align-items:center;justify-content:center;border-radius:8px;color:var(--ink3)}§ .lgf .fi .eye:hover{background:var(--mub);color:var(--ink)}§ .lgf .fi .z-in.pr{padding-right:44px}§ .lgf .fi .gc{position:absolute;right:4px;top:4px;height:32px;padding:0 12px;border-radius:8px;color:var(--p-text);white-space:nowrap}§ .lgf .fi .gc:hover:not(:disabled){background:var(--pt)}§ .lgf .fi .gc:disabled{color:var(--ink3);cursor:not-allowed}§ .lgf .opt{display:flex;align-items:center;justify-content:space-between;margin:2px 0 16px}§ .lgf .opt label{display:inline-flex;align-items:center;gap:8px;cursor:pointer;color:var(--ink2)}§ .lgf .msg{display:flex;align-items:flex-start;gap:8px;margin-bottom:12px;padding:8px 12px;border-radius:8px;background:var(--dgb);color:var(--dg);line-height:1.5}§ .lgf .msg .z-ic{margin-top:2px}§ .lgf .full{width:100%;height:40px;font-weight:600}§ .lgf .full.ok{background:var(--ok-fill);border-color:var(--ok)}§ .lgf .demo{margin-top:12px;font-size:12px;color:var(--ink3);text-align:center}§ .lgf .fine{margin-top:20px;font-size:12px;color:var(--ink3);line-height:1.6;text-align:center}§ .lgf .fine button{color:var(--p-text);font-size:12px}§ .lgf .qr{display:flex;flex-direction:column;align-items:center;gap:12px;padding:4px 0 8px}§ .lgf .qrb{position:relative;width:168px;height:168px;padding:10px;border:1px solid var(--line2);border-radius:12px;background:var(--paper)}§ .lgf .qrb svg{display:block;width:100%;height:100%}§ .lgf .qrb .ex{position:absolute;inset:0;display:none;flex-direction:column;align-items:center;justify-content:center;gap:8px;border-radius:12px;background:var(--glass2);color:var(--ink2)}§ .lgf .qrb.exp .ex{display:flex}§ .lgf .qr p{color:var(--ink2)}§ .lgf .qr small{font-size:12px;color:var(--ink3)}`
const lgPw = (tabsHtml, second) => `${tabsHtml}<div data-p="pw" data-g="lg"><div class="fi">${ic('user')}<input class="z-in" data-in="acc" placeholder="员工账号或手机号" autocomplete="off" aria-label="账号"><p class="z-er" hidden>请输入账号</p></div><div class="fi">${ic('lock')}<input class="z-in pr" data-in="pw" type="password" placeholder="登录密码" autocomplete="off" aria-label="密码"><button type="button" class="eye" data-eye aria-label="显示密码" title="显示 / 隐藏密码">${ic('eye')}</button><p class="z-er" hidden>请输入密码</p></div></div>${second}`
const lgSms = `<div data-p="sms" data-g="lg" hidden><div class="fi">${ic('phone')}<input class="z-in" data-in="tel" inputmode="numeric" maxlength="11" placeholder="手机号" autocomplete="off" aria-label="手机号"><p class="z-er" hidden>请输入 11 位手机号</p></div><div class="fi">${ic('shield')}<input class="z-in pr" data-in="code" inputmode="numeric" maxlength="6" placeholder="6 位验证码" autocomplete="off" aria-label="验证码"><button type="button" class="gc" data-act="code">获取验证码</button><p class="z-er" hidden>请输入 6 位验证码</p></div></div>`
const qrSvg = () => {
  const n = 21, fin = [[0, 0], [n - 7, 0], [0, n - 7]]; let r = ''
  for (let y = 0; y < n; y++) for (let x = 0; x < n; x++) {
    let on, inF = false
    fin.forEach(([ox, oy]) => { if (x >= ox && x < ox + 7 && y >= oy && y < oy + 7) { inF = true; const lx = x - ox, ly = y - oy; on = lx === 0 || lx === 6 || ly === 0 || ly === 6 || (lx >= 2 && lx <= 4 && ly >= 2 && ly <= 4) } })
    if (!inF) on = rnd(x * 31 + y, 9) > 0.52
    if (on) r += `<rect x="${x}" y="${y}" width="1" height="1"/>`
  }
  return `<svg viewBox="0 0 ${n} ${n}" shape-rendering="crispEdges" role="img" aria-label="登录二维码"><g fill="#1F2329">${r}</g></svg>`
}
const lgForm = (kind) => {
  const t = kind === 'a' ? tabs([['pw', '密码登录'], ['sms', '验证码登录']], 'pw', 'data-g="lg"') : tabs([['pw', '账号登录'], ['qr', '扫码登录']], 'pw', 'data-g="lg"')
  const extra = kind === 'a' ? lgSms : `<div data-p="qr" data-g="lg" hidden><div class="qr"><div class="qrb">${qrSvg()}<div class="ex"><b>二维码已过期</b><button type="button" class="z-btn" data-act="qrre">${ic('refresh')}点击刷新</button></div></div><p>打开手机端「扫一扫」登录</p><small class="qt">二维码 60 秒后过期</small></div></div>`
  return `<div class="lgf"><div class="lh"><i class="lg2">${ic('bz_shop', 'l')}</i><b>示例商城后台</b></div><h4 class="lt">登录</h4><p class="ls">使用员工账号登录管理后台</p>${lgPw(t, extra)}<div class="msg" role="alert" hidden></div><div class="opt" data-main>${'<label>' + ck(1, 'data-rem aria-label="记住我"') + '记住我，7 天内免登录</label>'}<button type="button" class="z-btn t" data-toast="请联系管理员重置密码">忘记密码</button></div><button type="button" class="z-btn p full" data-act="login" data-main>登录</button><p class="demo" data-main>演示：任意账号 + 密码 123456 可登录</p><p class="fine">登录即表示同意 <button type="button" data-toast="用户协议为示例">用户协议</button> 和 <button type="button" data-toast="隐私政策为示例">隐私政策</button></p></div>`
}
const lgBind = (root, el) => {
  let tries = 5, tab = 'pw', cd = 0, timer = null, qrT = null
  const $in = (k) => $(el, `[data-in=${k}]`), main = () => $$(el, '[data-main]')
  const err = (k, msg) => { const i = $in(k), p = i.parentNode.querySelector('.z-er'); i.classList.toggle('er', !!msg); p.hidden = !msg }
  const say = (m) => { const b = $(el, '.msg'); b.hidden = !m; b.innerHTML = m ? ic('alert') + `<span>${m}</span>` : '' }
  const tick = () => { if (!el.isConnected) { clearInterval(timer); return } cd--; const b = $(el, '[data-act=code]'); if (b) { b.textContent = cd > 0 ? `重新获取 (${cd})` : '获取验证码'; b.disabled = cd > 0 } if (cd <= 0) clearInterval(timer) }
  const qrStart = () => { clearInterval(qrT); let s = 60; const b = $(el, '.qrb'), t = $(el, '.qt'); if (!b) return; b.classList.remove('exp'); t.textContent = `二维码 ${s} 秒后过期`; qrT = setInterval(() => { if (!el.isConnected) { clearInterval(qrT); return } s--; t.textContent = s > 0 ? `二维码 ${s} 秒后过期` : '二维码已过期'; if (s <= 0) { b.classList.add('exp'); clearInterval(qrT) } }, 1000) }
  root.addEventListener('click', (e) => {
    const t = e.target.closest('.z-tabs [data-t]'); if (t) { tab = t.dataset.t; say(''); $$(el, '.z-er').forEach((p) => (p.hidden = true)); $$(el, '.z-in').forEach((i) => i.classList.remove('er')); main().forEach((m) => (m.hidden = tab === 'qr')); if (tab === 'qr') qrStart(); return }
    if (e.target.closest('[data-eye]')) { const b = e.target.closest('[data-eye]'), i = $in('pw'), show = i.type === 'password'; i.type = show ? 'text' : 'password'; b.innerHTML = sv(show ? 'eyeoff' : 'eye'); b.setAttribute('aria-label', show ? '隐藏密码' : '显示密码'); return }
    if (e.target.closest('[data-rem]')) { const c = e.target.closest('[data-rem]'); c.classList.toggle('on'); c.setAttribute('aria-checked', c.classList.contains('on')); return }
    const a = e.target.closest('[data-act]'); if (!a) return
    if (a.dataset.act === 'qrre') { qrStart(); toast(root, '二维码已刷新'); return }
    if (a.dataset.act === 'code') { const v = $in('tel').value.trim(); if (!/^1\d{10}$/.test(v)) { err('tel', 1); $in('tel').focus(); return } err('tel', 0); cd = 60; a.disabled = true; a.textContent = '重新获取 (60)'; clearInterval(timer); timer = setInterval(tick, 1000); toast(root, `验证码已发送到 ${v.slice(0, 3)}****${v.slice(-4)}`); return }
    if (a.dataset.act === 'login') {
      if (a.disabled) return; say('')
      let ok = true
      if (tab === 'pw') { const u = $in('acc').value.trim(), p = $in('pw').value; err('acc', !u); err('pw', !p); ok = !!(u && p) } else { const tel = $in('tel').value.trim(), c = $in('code').value.trim(); err('tel', !/^1\d{10}$/.test(tel)); err('code', !/^\d{6}$/.test(c)); ok = /^1\d{10}$/.test(tel) && /^\d{6}$/.test(c) }
      if (!ok) return
      a.disabled = true; a.innerHTML = '<i class="z-spin"></i>登录中…'
      setTimeout(() => {
        const good = tab === 'pw' ? $in('pw').value === '123456' : $in('code').value === '123456'
        if (good) { a.classList.add('ok'); a.innerHTML = ic('check') + '登录成功，正在进入…'; toast(root, '登录成功（示例）'); setTimeout(() => { a.disabled = false; a.classList.remove('ok'); a.textContent = '登录' }, 2200); return }
        tries--; a.disabled = tries <= 0; a.textContent = tries <= 0 ? '账号已锁定' : '登录'
        say(tab === 'pw' ? (tries > 0 ? `账号或密码错误，还可以尝试 ${tries} 次` : '连续输错 5 次，账号已锁定 15 分钟，可联系管理员解锁') : '验证码错误或已过期，请重新获取')
        if (tab === 'sms') tries++
      }, 900)
    }
  })
  root.addEventListener('keydown', (e) => { if (e.key === 'Enter' && e.target.matches('input')) $(el, '[data-act=login]').click(); if ((e.key === ' ' || e.key === 'Enter') && e.target.matches('.z-ck')) { e.preventDefault(); e.target.click() } })
  root.addEventListener('input', (e) => { if (e.target.matches('[data-in]')) { e.target.classList.remove('er'); const p = e.target.parentNode.querySelector('.z-er'); if (p) p.hidden = true; say('') } })
}

/* ---- AD-PAGE-006 登录页·左图右表单 ---- */
def({
  id: 'AD-PAGE-006', name: '登录页·左图右表单', style: '品牌图双登录', wide: true,
  fit: '面向员工的后台登录：左侧品牌与产品价值，右侧表单；密码与验证码两种方式，输错有剩余次数、验证码有倒计时、登录有加载与成功状态',
  avoid: '要极简、嵌在别的系统里的登录（用居中卡片）；需要第三方扫码、单点登录入口时（加到表单下方，别再堆在左侧）',
  kw: '登录页 登录 左图右表单 密码 验证码 倒计时 锁定 剩余次数 login 后台登录',
  css: K('adpage006', 'btn tag ck tabs in') + LG_CSS.replace(/§/g, '.adpage006') + `.adpage006{display:flex;width:1400px;max-width:100%;height:620px;background:var(--card);border:1px solid var(--n7);border-radius:12px;overflow:hidden}.ixr:has(>.adpage006){min-width:1040px}.adpage006 .art{position:relative;flex:1 1 56%;display:flex;flex-direction:column;justify-content:space-between;padding:36px 44px;background:linear-gradient(155deg,var(--pt) 0%,var(--pm) 100%);overflow:hidden}.adpage006 .art::before{content:"";position:absolute;right:-120px;top:-120px;width:420px;height:420px;border-radius:50%;background:color-mix(in srgb,var(--card) 45%,transparent)}.adpage006 .art::after{content:"";position:absolute;left:-80px;bottom:-140px;width:360px;height:360px;border-radius:50%;background:color-mix(in srgb,var(--card) 30%,transparent)}.adpage006 .art>*{position:relative;z-index:1}.adpage006 .ab{display:flex;align-items:center;gap:10px}.adpage006 .ab i{display:flex;align-items:center;justify-content:center;width:32px;height:32px;border-radius:8px;background:var(--card);color:var(--p-text)}.adpage006 .ab b{font-size:16px;font-weight:600;color:var(--p-text)}.adpage006 .art h3{font-size:28px;line-height:1.35;font-weight:700;color:var(--p-text);max-width:420px}.adpage006 .art .sub{margin-top:12px;color:var(--ink2);max-width:420px;line-height:1.7}.adpage006 .mock{position:relative;height:236px;margin:8px 0}.adpage006 .mk{position:absolute;padding:14px 16px;border-radius:12px;background:var(--card);box-shadow:0 8px 24px var(--sh10)}.adpage006 .mk small{display:block;font-size:12px;color:var(--ink3)}.adpage006 .mk b{display:block;margin-top:2px;font-size:22px;font-weight:700;font-variant-numeric:tabular-nums}.adpage006 .mk .dl{display:inline-flex;align-items:center;gap:2px;margin-top:2px;font-size:12px;font-weight:600;color:var(--ok)}.adpage006 .mk.a{left:0;top:0;width:250px}.adpage006 .mk.a .bars{display:flex;align-items:flex-end;gap:6px;height:48px;margin-top:10px}.adpage006 .mk.a .bars i{flex:1;border-radius:3px 3px 0 0;background:var(--pm)}.adpage006 .mk.a .bars i:last-child{background:var(--p)}.adpage006 .mk.b{left:262px;top:44px;width:170px}.adpage006 .mk.c{left:70px;top:176px;width:210px;display:flex;align-items:center;gap:12px}.adpage006 .mk.c i{display:flex;align-items:center;justify-content:center;width:32px;height:32px;border-radius:8px;background:var(--wnb);color:var(--wn)}.adpage006 .mk.c b{font-size:14px;font-weight:600;margin:0}.adpage006 .art .cp{font-size:12px;color:var(--ink2)}.adpage006 .pnl{flex:1 1 44%;min-width:0;display:flex;align-items:center;justify-content:center;padding:32px 40px;background:var(--card)}`,
  html: () => `<div class="adpage006"><div class="art"><div class="ab"><i>${ic('bz_shop', 'l')}</i><b>示例商城</b></div><div><h3>订单、会员与库存，一个后台管好</h3><p class="sub">从下单到售后的全流程数据实时汇总，异常自动提醒，团队按角色各取所需。</p></div><div class="mock" aria-hidden="true"><div class="mk a"><small>今日销售额</small><b>¥18,640</b><span class="dl">${ic('arrowup', 's')}8.2%</span><div class="bars">${[38, 52, 44, 60, 48, 72, 100].map((h) => `<i style="height:${h}%"></i>`).join('')}</div></div><div class="mk b"><small>待发货订单</small><b>12</b></div><div class="mk c"><i>${ic('alert')}</i><div><small>库存预警</small><b>5 件商品</b></div></div></div><div class="cp">© 2026 示例商城 · 前端 v2.4.1</div></div><div class="pnl">${lgForm('a')}</div></div>`,
  js: (root) => { const el = $(root, '.adpage006'); lgBind(root, el) },
})

/* ---- AD-PAGE-007 登录页·居中卡片 ---- */
def({
  id: 'AD-PAGE-007', name: '登录页·居中卡片', style: '极简+扫码', wide: true,
  fit: '极简或嵌入式的后台登录：浅色背景上一张居中卡片，账号密码与扫码两种方式，二维码有倒计时与过期刷新',
  avoid: '需要大篇幅介绍产品价值、品牌展示的场景（用左图右表单）；没有移动端 App 时不要放扫码',
  kw: '登录页 居中卡片 极简 扫码登录 二维码 过期刷新 login card 后台登录',
  css: K('adpage007', 'btn tag ck tabs in') + LG_CSS.replace(/§/g, '.adpage007') + `.adpage007{position:relative;display:flex;flex-direction:column;align-items:center;justify-content:center;gap:16px;width:1400px;max-width:100%;height:620px;background:var(--pt);border:1px solid var(--n7);border-radius:12px;overflow:hidden}.ixr:has(>.adpage007){min-width:1040px}.adpage007::before{content:"";position:absolute;inset:0;background-image:linear-gradient(var(--glass0) 1px,transparent 1px),linear-gradient(90deg,var(--glass0) 1px,transparent 1px);background-size:36px 36px;-webkit-mask-image:radial-gradient(ellipse at center,#000 20%,transparent 75%);mask-image:radial-gradient(ellipse at center,#000 20%,transparent 75%)}.adpage007 .cd{position:relative;width:420px;max-width:calc(100% - 32px);padding:32px 34px 28px;border-radius:16px;background:var(--card);box-shadow:0 12px 40px var(--sh10),0 0 0 1px var(--sh04)}.adpage007 .lgf{max-width:none}.adpage007 .lgf .lh{justify-content:center;margin-bottom:20px}.adpage007 .lgf .lt{text-align:center}.adpage007 .lgf .ls{text-align:center}.adpage007 .lgf .z-tabs{justify-content:center}.adpage007 .ft2{position:relative;display:flex;gap:16px;font-size:12px;color:var(--ink2)}.adpage007 .ft2 button{color:var(--ink2);font-size:12px}.adpage007 .ft2 button:hover{color:var(--p-text)}`,
  html: () => `<div class="adpage007"><div class="cd">${lgForm('b')}</div><div class="ft2"><button type="button" data-toast="帮助中心为示例">帮助中心</button><span>·</span><button type="button" data-toast="已切换为英文（示例）">简体中文</button><span>·</span><span>© 2026 示例商城</span></div></div>`,
  js: (root) => { const el = $(root, '.adpage007'); lgBind(root, el) },
})

/* ---- AD-PAGE-008 数据分析页 ---- */
const CH_COL = ['var(--p)', '#7F8B9B', '#C2A98B', '#9DB3A3']
const CHS = [['小程序商城', 0.46, 12.4], ['到店收银', 0.27, 3.1], ['外卖平台', 0.17, -5.2], ['社群团购', 0.1, 21.6]]
const MET = { s: ['销售额', money, (d) => d.cur, (d) => d.prev], o: ['订单数', (v) => Math.round(v).toLocaleString(), (d) => d.ord, (d) => d.ordP], v: ['访客数', (v) => Math.round(v).toLocaleString(), (d) => d.vis, (d) => d.visP] }
const donut = (data, hi) => { const R = 44, C = 2 * Math.PI * R; let off = 0; return `<svg viewBox="0 0 120 120" aria-hidden="true"><circle cx="60" cy="60" r="${R}" fill="none" stroke="var(--n4)" stroke-width="16"/>${data.map((x, i) => { const len = C * x.share, seg = `<circle class="sg${hi === i ? ' hot' : hi >= 0 ? ' dim' : ''}" data-i="${i}" cx="60" cy="60" r="${R}" fill="none" stroke="${CH_COL[i]}" stroke-width="16" stroke-dasharray="${Math.max(0, len - 1.5)} ${C - Math.max(0, len - 1.5)}" stroke-dashoffset="${-off}" transform="rotate(-90 60 60)"/>`; off += len; return seg }).join('')}</svg>` }
def({
  id: 'AD-PAGE-008', name: '数据分析页', style: '切范围联动', wide: true,
  fit: '分析型页面：页面统一控制时间范围与对比开关，主图可切指标、点图例显隐线条，下方渠道构成与明细表联动高亮',
  avoid: '给管理层看一眼的首页（用驾驶舱首页）；数据点少于 3 个时不画折线，1 类数据不画环图',
  kw: '数据分析 分析页 图表 趋势 对比上期 渠道 环图 占比 明细 analytics',
  css: K('adpage008', 'btn tag seg in sw dd') + SHELL_CSS.replace(/§/g, '.adpage008') + CHART_CSS.replace(/§/g, '.adpage008') + `.adpage008{--ch:132px}.adpage008 .hd{display:flex;align-items:center;justify-content:space-between;gap:12px;margin-bottom:12px}.adpage008 .hd .l{display:flex;align-items:center;gap:16px}.adpage008 .cmp{display:inline-flex;align-items:center;gap:8px;color:var(--ink2)}.adpage008 .mc{padding:14px 18px 6px}.adpage008 .mh{display:flex;align-items:flex-start;justify-content:space-between;flex-wrap:wrap;gap:8px 16px}.adpage008 .mh .big{display:flex;align-items:baseline;gap:10px;margin-top:6px}.adpage008 .mh .big b{font-size:22px;font-weight:700;font-variant-numeric:tabular-nums;line-height:1.2}.adpage008 .mh .big em{font-style:normal;font-size:12px;color:var(--ink3)}.adpage008 .lgd{display:flex;align-items:center;gap:8px}.adpage008 .lgd button{display:inline-flex;align-items:center;gap:6px;height:32px;padding:0 10px;border-radius:8px;border:1px solid var(--bd);font-size:12px;color:var(--ink2);transition:border-color .15s,opacity .15s}.adpage008 .lgd button:hover:not(:disabled){border-color:var(--ink3)}.adpage008 .lgd button i{display:inline-block;width:14px;height:0;border-top:2px solid var(--p)}.adpage008 .lgd button.pv i{border-top:2px dashed var(--n12)}.adpage008 .lgd button.off{opacity:.5}.adpage008 .lgd button.off i{border-top-color:var(--n9)}.adpage008 .lgd button:disabled{opacity:.4;cursor:not-allowed}.adpage008 .row2{display:grid;grid-template-columns:minmax(0,5fr) minmax(0,7fr);gap:16px;margin-top:16px}.adpage008 .cd{padding:14px 18px 16px}.adpage008 .cd h4{font-size:14px;font-weight:600;margin-bottom:10px}.adpage008 .dnt{display:flex;align-items:center;gap:18px}.adpage008 .dnt .ring{position:relative;flex:none;width:130px;height:130px}.adpage008 .dnt .ring svg{width:100%;height:100%}.adpage008 .dnt .sg{transition:opacity .15s,stroke-width .15s}.adpage008 .dnt .sg.dim{opacity:.3}.adpage008 .dnt .sg.hot{stroke-width:19}.adpage008 .dnt .ctr{position:absolute;inset:0;display:flex;flex-direction:column;align-items:center;justify-content:center;text-align:center;line-height:1.3}.adpage008 .dnt .ctr b{font-size:16px;font-weight:600;font-variant-numeric:tabular-nums}.adpage008 .dnt .ctr small{font-size:12px;color:var(--ink3)}.adpage008 .dnt ul{flex:1;display:flex;flex-direction:column;gap:2px}.adpage008 .dnt li{display:flex;align-items:center;gap:8px;height:30px;padding:0 6px;margin:0 -6px;border-radius:4px}.adpage008 .dnt li.hot{background:var(--sf)}.adpage008 .dnt li i{width:8px;height:8px;border-radius:2px;flex:none}.adpage008 .dnt li span{flex:1}.adpage008 .dnt li em{font-style:normal;font-variant-numeric:tabular-nums;color:var(--ink2)}.adpage008 .tb2{width:100%;border-collapse:collapse}.adpage008 .tb2 th{height:36px;padding:0 10px;text-align:center;font-weight:600;color:var(--ink2);background:var(--n2);border-bottom:1px solid var(--line);white-space:nowrap;user-select:none;-webkit-user-select:none}.adpage008 .tb2 th.so{cursor:pointer}.adpage008 .tb2 th.so:hover{color:var(--ink)}.adpage008 .tb2 th.so .z-ic{color:color-mix(in srgb,var(--ink6) 74%,var(--ink5));margin-left:2px;vertical-align:-3px}.adpage008 .tb2 th.so.on .z-ic{color:var(--p-fg)}.adpage008 .tb2 td{height:38px;padding:0 10px;text-align:center;border-bottom:1px solid var(--line)}.adpage008 .tb2 tr:last-child td{border-bottom:0}.adpage008 .tb2 td.l{text-align:left;padding-left:16px}.adpage008 .tb2 td.r{text-align:right;padding-right:24px;font-variant-numeric:tabular-nums}.adpage008 .tb2 tr.hot td{background:var(--sf)}.adpage008 .tb2 .nm{display:inline-flex;align-items:center;gap:8px}.adpage008 .tb2 .nm i{width:8px;height:8px;border-radius:2px}.adpage008 .tb2 .pc{display:inline-flex;align-items:center;gap:8px;width:120px}.adpage008 .tb2 .pc span{flex:1;height:6px;border-radius:3px;background:var(--n4);overflow:hidden}.adpage008 .tb2 .pc span i{display:block;height:100%;border-radius:3px}.adpage008 .tb2 .pc b{font-weight:400;font-variant-numeric:tabular-nums;width:40px;text-align:right}`,
  html: () => `<div class="adpage008">${shell('stat', `<div class="hd"><div class="l">${seg([['d7', '近 7 天'], ['d30', '近 30 天'], ['d90', '近 90 天']], 'd30', 'data-g="rg"')}<label class="cmp">${sw(true, 'data-cmp aria-label="对比上期"')}对比上期</label></div><button type="button" class="z-btn" data-toast="已按当前范围导出报表">${ic('download')}导出</button></div><div class="z-card mc"><div class="mh"><div>${seg([['s', '销售额'], ['o', '订单数'], ['v', '访客数']], 's', 'data-g="mt"')}<div class="big"><b class="bv">—</b><span class="bd"></span><em>较上期</em></div></div><div class="lgd"><button type="button" data-lg="cur"><i></i>本期</button><button type="button" class="pv" data-lg="prev"><i></i>上期</button></div></div>${chartHTML('adpage008c')}</div><div class="row2"><div class="z-card cd"><h4>渠道构成</h4><div class="dnt"><div class="ring"></div><ul></ul></div></div><div class="z-card cd" style="padding:0 0 4px"><h4 style="padding:14px 18px 0">渠道明细</h4><table class="tb2"><thead><tr><th>渠道</th><th class="so on" data-s="sales">销售额${ic('arrowdown', 's')}</th><th class="so" data-s="share">占比${ic('sort', 's')}</th><th class="so" data-s="mom">环比${ic('sort', 's')}</th></tr></thead><tbody></tbody></table></div></div>`)}</div>`,
  js: (root) => {
    const el = $(root, '.adpage008'), box = $(el, '.cht'); wireShell(root, el, 'stat'); chartBind(box)
    let r = 'd30', m = 's', cmp = true, showCur = true, showPrev = true, sk = 'sales', dir = -1, hi = -1
    const rows = () => { const S = sum(range(r).cur), f = r === 'd7' ? 0.6 : r === 'd90' ? 1.3 : 1; return CHS.map(([n, sh, mom], i) => ({ n, i, share: sh, sales: S * sh, mom: mom * f * (i % 2 ? 1 : 0.9) })).sort((a, b) => (a[sk] - b[sk]) * dir) }
    const drawChart = () => { const d = range(r), [, fmt, cur, prev] = MET[m]; const c = cur(d), p = prev(d); chartDraw(box, { cur: c, prev: p, labels: d.labels, showPrev: cmp && showPrev, hideCur: !showCur, fmt, name: MET[m][0] }); const S = sum(c), SP = sum(p); $(el, '.bv').textContent = fmt(S); $(el, '.bd').innerHTML = dTag(delta(S, SP)) }
    const drawLg = () => { const a = $(el, '[data-lg=cur]'), b = $(el, '[data-lg=prev]'); a.classList.toggle('off', !showCur); b.classList.toggle('off', !(cmp && showPrev)); b.disabled = !cmp; b.title = cmp ? '' : '已关闭「对比上期」' }
    const drawCh = () => {
      const rs = rows(), tot = sum(rs.map((x) => x.sales)); $(el, '.ring').innerHTML = donut(rs, hi) + `<div class="ctr">${hi >= 0 ? `<b>${(rs.find((x) => x.i === hi).share * 100).toFixed(0)}%</b><small>${rs.find((x) => x.i === hi).n}</small>` : `<b>${money(tot)}</b><small>销售额合计</small>`}</div>`
      $(el, '.dnt ul').innerHTML = rs.map((x) => `<li data-i="${x.i}" class="${hi === x.i ? 'hot' : ''}"><i style="background:${CH_COL[x.i]}"></i><span>${x.n}</span><em>${(x.share * 100).toFixed(0)}%</em></li>`).join('')
      $(el, '.tb2 tbody').innerHTML = rs.map((x) => `<tr data-i="${x.i}" class="${hi === x.i ? 'hot' : ''}"><td class="l"><span class="nm"><i style="background:${CH_COL[x.i]}"></i>${x.n}</span></td><td class="r">${money(x.sales)}</td><td><span class="pc"><span><i style="width:${x.share * 100 * 2}%;background:${CH_COL[x.i]}"></i></span><b>${(x.share * 100).toFixed(0)}%</b></span></td><td>${dTag(x.mom)}</td></tr>`).join('')
      $$(el, '.tb2 th.so').forEach((th) => { const on = th.dataset.s === sk; th.classList.toggle('on', on); $(th, '.z-ic').innerHTML = sv(on ? (dir === 1 ? 'arrowup' : 'arrowdown') : 'sort') })
    }
    const all = () => { drawChart(); drawLg(); drawCh() }
    all()
    root.addEventListener('click', (e) => {
      const t = e.target.closest('.z-seg [data-t]'); if (t) { const g = t.closest('.z-seg').dataset.g; if (g === 'rg') r = t.dataset.t; else m = t.dataset.t; all(); return }
      const c = e.target.closest('[data-cmp]'); if (c) { cmp = c.classList.toggle('on'); c.setAttribute('aria-checked', cmp); all(); return }
      const lg = e.target.closest('[data-lg]'); if (lg && !lg.disabled) { const k = lg.dataset.lg; if (k === 'cur') { if (showCur && !(cmp && showPrev)) { toast(root, '至少保留一条线'); return } showCur = !showCur } else { if (showPrev && !showCur) { toast(root, '至少保留一条线'); return } showPrev = !showPrev } all(); return }
      const th = e.target.closest('th.so'); if (th) { if (sk === th.dataset.s) dir = -dir; else { sk = th.dataset.s; dir = -1 } drawCh(); return }
    })
    root.addEventListener('pointerover', (e) => { const x = e.target.closest('.dnt li, .tb2 tbody tr, .dnt .sg'); const i = x ? +x.dataset.i : -1; if (i !== hi) { hi = i; drawCh() } })
    el.addEventListener('pointerleave', () => { if (hi >= 0) { hi = -1; drawCh() } })
    root.addEventListener('keydown', (e) => { if ((e.key === ' ' || e.key === 'Enter') && e.target.matches('.z-sw')) { e.preventDefault(); e.target.click() } })
  },
})

/* ---- AD-PAGE-009 空白壳 ---- */
def({
  id: 'AD-PAGE-009', name: '空白壳', style: '侧栏+顶栏', wide: true,
  fit: '新页面的起点：侧栏分组导航（可收起）、顶栏（搜索、门店、消息、账号）、页头区与内容区都已就位，只填内容；内容区会实时显示当前尺寸',
  avoid: '已经确定整页结构时（直接用列表页、详情页、表单页）；登录页、全屏大屏这类不需要侧栏的页面',
  kw: '空白壳 页面框架 layout 侧栏 顶栏 面包屑 内容区 模板 骨架 shell',
  css: K('adpage009', 'btn tag dd') + SHELL_CSS.replace(/§/g, '.adpage009') + `.adpage009 .z-in{background:var(--card);color:var(--ink)}.adpage009 .z-in::placeholder{color:var(--ink3)}.adpage009 .slot{border:1px dashed var(--n10);border-radius:12px;background:color-mix(in srgb,var(--card) 60%,transparent);color:var(--ink3)}.adpage009 .hd2{display:flex;align-items:center;justify-content:space-between;gap:12px;padding:14px 18px;margin-bottom:16px}.adpage009 .hd2 .l{display:flex;flex-direction:column;gap:8px}.adpage009 .hd2 .l span{display:block;height:10px;border-radius:5px;background:var(--n6)}.adpage009 .hd2 .l span.t{width:180px;height:16px}.adpage009 .hd2 .l span.c{width:260px}.adpage009 .hd2 .r{display:flex;gap:8px}.adpage009 .hd2 .r i{display:block;width:84px;height:32px;border-radius:8px;background:var(--n6)}.adpage009 .hd2 .r i.p{background:var(--pm)}.adpage009 .hd2 em{position:absolute;right:20px;top:-1px;transform:translateY(-100%);font-style:normal;font-size:12px;color:var(--ink3)}.adpage009 .area{position:relative;display:flex;align-items:center;justify-content:center;height:calc(100% - 82px);min-height:260px;text-align:center}.adpage009 .area .in{display:flex;flex-direction:column;align-items:center;gap:8px}.adpage009 .area b{font-size:16px;font-weight:600;color:var(--ink2)}.adpage009 .area .sz{display:inline-flex;gap:8px;flex-wrap:wrap;justify-content:center}.adpage009 .area .sz span{display:inline-flex;align-items:center;height:24px;padding:0 10px;border-radius:12px;background:var(--card);border:1px solid var(--line2);font-size:12px;color:var(--ink2);font-variant-numeric:tabular-nums}.adpage009 .area p{font-size:12px}`,
  html: () => `<div class="adpage009">${shell('dash', `<div class="slot hd2"><div class="l"><span class="c"></span><span class="t"></span></div><div class="r"><i></i><i class="p"></i></div></div><div class="slot area"><div class="in"><b>内容区</b><div class="sz"><span class="a1">内容区 1144 × 424</span><span class="a2">侧栏 216</span><span class="a3">顶栏 52</span><span class="a4">内边距 20</span></div><p>页头区放面包屑、对象名与主操作；点左上角的按钮试试收起侧栏</p></div></div>`)}</div>`,
  js: (root) => {
    const el = $(root, '.adpage009'); wireShell(root, el, 'dash'); const area = $(el, '.area')
    const upd = () => { const r = area.getBoundingClientRect(), s = $(el, '.sd').getBoundingClientRect(), t = $(el, '.tp').getBoundingClientRect(); $(el, '.a1').textContent = `内容区 ${Math.round(r.width)} × ${Math.round(r.height)}`; $(el, '.a2').textContent = `侧栏 ${Math.round(s.width)}`; $(el, '.a3').textContent = `顶栏 ${Math.round(t.height)}` }
    if (window.ResizeObserver) { const ro = new ResizeObserver(upd); ro.observe(area); ro.observe($(el, '.sd')) } else { setInterval(upd, 500) }
    setTimeout(upd, 0)
  },
})

guide('ad', 'PAGE', [
  ['运营者每天打开的第一屏', '驾驶舱首页', '先给计算后的指标和异常，再看趋势、待办、排行；时间范围统一控制'],
  ['订单、会员、工单等业务列表', '列表页', '默认先看待处理，筛选只露最常用的，状态标签带数量，批量栏与分页齐全'],
  ['查看一个对象的完整信息', '详情页', '面包屑 + 对象名做页头，进度在上，明细、物流、记录放标签页'],
  ['新建或编辑较长的对象', '表单页', '分组单列表单，右侧进度可定位，底部保存栏固定，提交统一校验'],
  ['系统、门店、账号设置', '设置页', '左分类右表单，修改后才能保存，切换分类先询问；开关类即时生效'],
  ['员工登录后台', '登录页·左图右表单', '品牌与价值在左、表单在右，密码与验证码两种方式；要极简时用登录页·居中卡片'],
  ['深入分析趋势与构成', '数据分析页', '可切范围与指标，图例显隐，渠道构成与明细联动；新页面从空白壳起步'],
])
/*__MORE__*/
})()
