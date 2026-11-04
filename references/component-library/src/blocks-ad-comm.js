;(() => {
/* ===== 后台 · 沟通与消息 AD-COMM-001 … 010 =====
 * 001 会话列表 · 002 单聊窗口 · 003 客服会话工作台 · 004 收件箱与阅读面板 · 005 通知中心页
 * 006 评论线程 · 007 系统公告条 · 008 用户名片悬浮卡 · 009 提及与表情面板 · 010 顶栏通知下拉
 * 全文件包在一个函数里，局部工具不污染全局；块里的 js 钩子只用本文件的小工具（$ $$ esc ic av T 等）。 */
Object.assign(LINE, {
  cmsend: '<path d="M21 3 10.500 13.500M21 3l-6.500 18-4-7.500L3 9.500z"/>',
  cmsmile: '<circle cx="12" cy="12" r="8.500"/><path d="M8.500 14a4 4 0 0 0 7 0M9 9.800h.01M15 9.800h.01"/>',
  cmat: '<circle cx="12" cy="12" r="3.500"/><path d="M15.500 8.500v5a2.500 2.500 0 0 0 5 0V12a8.500 8.500 0 1 0-3.400 6.800"/>',
  cmclip: '<path d="m20 11-8.500 8.500a5.500 5.500 0 0 1-7.800-7.800L13 2.500a3.700 3.700 0 0 1 5.200 5.200l-8.700 8.700a1.900 1.900 0 0 1-2.700-2.700l7.700-7.700"/>',
  cmhorn: '<path d="M3.500 10v4h3.500l7.500 4.500v-13L7 10z"/><path d="M18 9.500a4 4 0 0 1 0 5"/>',
  cmreply: '<path d="M10 7 4.500 12l5.500 5"/><path d="M4.500 12H14a6 6 0 0 1 6 6v1"/>',
  cmarchive: '<rect x="3.500" y="4.500" width="17" height="4" rx="1.500"/><path d="M5 8.500v10a1 1 0 0 0 1 1h12a1 1 0 0 0 1-1v-10M10 13h4"/>',
  cmpush: '<path d="M9 4h6l-1 5 3 3v1.500H7V12l3-3z"/><path d="M12 13.500V20"/>',
  cmmute: '<path d="M6 16V11a6 6 0 0 1 9-5.200M18 11v5l1.500 2H5M10 20a2 2 0 0 0 4 0M3.500 3.500l17 17"/>',
  cmthumb: '<path d="M7 11v9H4.500a1 1 0 0 1-1-1v-7a1 1 0 0 1 1-1zM7 11l3.500-6.500a1.800 1.800 0 0 1 2.500 1.600V10h5.500a1.500 1.500 0 0 1 1.500 1.800l-1.300 6.500a2 2 0 0 1-2 1.700H7"/>',
  cmchecks: '<path d="m2.500 12.500 4.500 4.500L14 8M10.500 16.500l.5.5L20.500 7.500"/>',
  cmforward: '<path d="M14 7l5.500 5-5.500 5"/><path d="M19.500 12H10a6 6 0 0 0-6 6v1"/>',
})

/* ---------- 小工具 ---------- */
const $ = (r, s) => r.querySelector(s)
const $$ = (r, s) => [...r.querySelectorAll(s)]
const esc = (s) => String(s).replace(/[&<>"]/g, (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]))
const T = (r, m) => IX.toast(r, m)
const ic = (n, s = 18) => `<span class="ic" style="width:${s}px;height:${s}px">${sv(n)}</span>`
const av = (i, s = 40, dot) => `<span class="avw">${critter(i, s)}${dot ? `<i class="dot ${dot}"></i>` : ''}</span>`
const fit = (ta, max = 98) => { ta.style.height = 'auto'; ta.style.height = Math.min(ta.scrollHeight + 2, max) + 'px' }
const insertAt = (ta, s) => {
  const a = ta.selectionStart == null ? ta.value.length : ta.selectionStart, b = ta.selectionEnd == null ? a : ta.selectionEnd
  ta.value = ta.value.slice(0, a) + s + ta.value.slice(b); const c = a + s.length
  ta.focus(); ta.setSelectionRange(c, c); ta.dispatchEvent(new Event('input', { bubbles: true }))
}
/* 点块外关闭浮层：监听挂在 document 上，块被重渲染（DOM 脱离）后自己摘掉 */
const outside = (r, fn) => { const h = (e) => { if (!r.isConnected) { document.removeEventListener('click', h); return } fn(e) }; document.addEventListener('click', h) }
const fmt = (n) => '¥' + Number(n).toLocaleString('en-US')

/* ---------- 共用样式（每块用自己的前缀） ---------- */
const K = (p, clip = true) => `
.${p},.${p} *{box-sizing:border-box}
.${p}{position:relative;container-type:inline-size;background:var(--card);border:1px solid var(--line2);border-radius:12px;box-shadow:0 1px 2px var(--sh04),0 6px 20px var(--sh05);font-size:14px;line-height:1.5;color:var(--ink)${clip ? ';overflow:hidden' : ''}}
.${p} :is(h2,h3,h4,p,ul,ol,dl,dd){margin:0;padding:0}
.${p} :is(ul,ol){list-style:none}
.${p} button{font:inherit;color:inherit}
.${p} button:focus:not(:focus-visible){outline:none}
.${p} :focus-visible{outline:2px solid var(--ink2);outline-offset:1px}
.${p} :is(input,textarea):focus-visible{outline:none}
.${p} .ic{display:inline-flex;width:18px;height:18px;flex:none;align-items:center;justify-content:center}
.${p} .sp{flex:1}
.${p} .scr{scrollbar-width:thin;scrollbar-color:var(--n8) transparent}
.${p} .ib{position:relative;width:32px;height:32px;border-radius:8px;display:inline-flex;align-items:center;justify-content:center;color:var(--ink2);flex:none;transition:background .15s,color .15s}
.${p} .ib:hover{background:var(--soft);color:var(--ink)}
.${p} .ib.on{color:var(--p-text);background:var(--pt)}
.${p} .cbt{height:32px;padding:0 14px;border-radius:8px;border:1px solid var(--n7);background:var(--card);font-size:14px;font-weight:600;display:inline-flex;align-items:center;justify-content:center;gap:6px;white-space:nowrap;color:var(--ink);flex:none;transition:background .15s,border-color .15s,transform .15s cubic-bezier(.2,0,0,1)}
.${p} .cbt:hover{background:var(--n2)}
.${p} .cbt:active{transform:scale(.97)}
.${p} .cbt.pri{background:var(--p);border-color:var(--p);color:#fff}
.${p} .cbt.pri:hover{background:var(--pd);border-color:var(--pd)}
.${p} .cbt.dg{background:var(--danger-fill);border-color:var(--danger);color:#fff}
.${p} .cbt.dg:hover{background:color-mix(in srgb,var(--danger-fill) 85%,#000);border-color:color-mix(in srgb,var(--danger-fill) 85%,#000)}
.${p} .cbt.lg{height:40px;padding:0 18px}
.${p} .cbt:disabled,.${p} .cbt.dis{background:var(--soft);border-color:var(--soft);color:var(--ink4);cursor:not-allowed;transform:none}
.${p} .tag{display:inline-flex;align-items:center;height:20px;padding:0 6px;border-radius:4px;font-size:12px;font-weight:600;line-height:1;white-space:nowrap;background:var(--soft);color:var(--ink2);flex:none}
.${p} .tag.pri{background:var(--pt);color:var(--p-text)}
.${p} .tag.ok{background:var(--ok-bg);color:var(--ok)}
.${p} .tag.warn{background:var(--warn-bg);color:var(--warn)}
.${p} .tag.red{background:var(--danger-bg);color:var(--danger)}
.${p} .ub{min-width:18px;height:18px;padding:0 5px;border-radius:16px;background:var(--danger-fill);color:#fff;font-size:12px;font-weight:600;line-height:18px;text-align:center;flex:none;font-variant-numeric:tabular-nums}
.${p} .ub.mu{background:var(--n4);color:var(--ink2)}
.${p} .tot{height:20px;min-width:20px;padding:0 6px;border-radius:16px;background:var(--danger-bg);color:var(--danger);font-size:12px;font-weight:600;line-height:20px;text-align:center;font-variant-numeric:tabular-nums}
.${p} .avw{position:relative;display:inline-flex;flex:none}
.${p} .avw .dot{position:absolute;right:0;bottom:0;width:10px;height:10px;border-radius:50%;background:var(--ok-fill);border:2px solid var(--card)}
.${p} .avw .dot.busy{background:#B8862F}
.${p} .avw .dot.off{background:color-mix(in srgb,var(--n11) 44%,var(--n12))}
.${p} .gav{width:40px;height:40px;border-radius:50%;background:var(--pm);color:var(--p-text);display:inline-flex;align-items:center;justify-content:center;flex:none}
.${p} .emp{display:flex;flex-direction:column;align-items:center;justify-content:center;gap:4px;padding:40px 16px;color:var(--ink3);text-align:center;font-size:14px}
.${p} .emp b{color:var(--ink2);font-weight:600}
.${p} .emp .ic{color:var(--ink6);margin-bottom:6px}
.${p} .sch{position:relative}
.${p} .sch>.ic{position:absolute;left:10px;top:9px;color:var(--ink4);pointer-events:none}
.${p} .in{width:100%;height:36px;border:1px solid transparent;background:var(--n3);border-radius:8px;padding:0 32px 0 34px;font:inherit;font-size:14px;color:var(--ink);outline:none;transition:border-color .15s,background .15s}
.${p} .in::placeholder{color:var(--ink4)}
.${p} .in:focus{border-color:var(--ink2);background:var(--card)}
.${p} .in::-webkit-search-cancel-button{display:none}
.${p} .sch .clr{position:absolute;right:4px;top:4px;width:28px;height:28px;border-radius:4px;display:inline-flex;align-items:center;justify-content:center;color:var(--ink4)}
.${p} .sch .clr:hover{background:var(--n4);color:var(--ink)}
.${p} .tb{position:relative;display:flex;gap:2px;padding:0 12px;border-bottom:1px solid var(--line)}
.${p} .tb [data-t]{height:40px;padding:0 10px;font-size:14px;color:var(--ink2);display:inline-flex;align-items:center;gap:6px;white-space:nowrap;transition:color .15s}
.${p} .tb [data-t]:hover{color:var(--ink)}
.${p} .tb [data-t].on{color:var(--ink);font-weight:600}
.${p} .tb .ink{position:absolute;bottom:-1px;left:0;width:0;height:2px;border-radius:1px;background:var(--p);transition:left .22s cubic-bezier(.2,0,0,1),width .22s cubic-bezier(.2,0,0,1)}
.${p} .tb .nbd{min-width:18px;height:18px;padding:0 5px;border-radius:16px;background:var(--danger-fill);color:#fff;font-size:12px;font-weight:600;line-height:18px;text-align:center}
.${p} .tb .nbd.gy{background:var(--n4);color:var(--ink2)}
.${p} .tgl{position:relative;width:36px;height:20px;border-radius:16px;background:var(--n9);flex:none;cursor:pointer;transition:background .2s cubic-bezier(.2,0,0,1)}
.${p} .tgl::after{content:"";position:absolute;left:2px;top:2px;width:16px;height:16px;border-radius:50%;background:var(--card);box-shadow:0 1px 3px var(--sh25);transition:transform .2s cubic-bezier(.2,0,0,1)}
.${p} .tgl.on{background:var(--p)}
.${p} .tgl.on::after{transform:translateX(16px)}
.${p} .ix-ov{align-items:center;justify-content:center}
.${p} .ix-ov .dlg{position:relative;width:min(380px,calc(100% - 32px));max-height:calc(100% - 32px);overflow:auto;background:var(--card2);border-radius:12px;padding:24px;box-shadow:0 20px 50px var(--sh25);animation:adcmpop .2s cubic-bezier(.2,0,0,1)}
.${p} .dlg h4{font-size:18px;font-weight:600;line-height:26px}
.${p} .dlg p{margin-top:8px;color:var(--ink2)}
.${p} .dlg .df{display:flex;justify-content:flex-end;gap:10px;margin-top:20px}
@keyframes adcmpop{from{opacity:0;transform:translateY(8px) scale(.98)}to{opacity:1;transform:none}}
@media(prefers-reduced-motion:reduce){.${p} *{animation:none!important}}
`

/* 会话条目（001 与 003 共用） */
const LIST = (p) => `
.${p} .it{display:flex;gap:12px;align-items:center;padding:12px 16px;cursor:pointer;position:relative;transition:background .15s}
.${p} .it:hover{background:var(--n2)}
.${p} .it.on{background:var(--pt)}
.${p} .it.on::before{content:"";position:absolute;left:0;top:12px;bottom:12px;width:3px;border-radius:0 2px 2px 0;background:var(--p)}
.${p} .it:focus-visible{outline-offset:-2px}
.${p} .it .bd{flex:1;min-width:0;display:flex;flex-direction:column;gap:2px}
.${p} .it .r1,.${p} .it .r2{display:flex;align-items:center;gap:6px;min-width:0}
.${p} .it .nm{flex:1;min-width:0;font-size:14px;font-weight:600;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.${p} .it .tm{font-size:12px;color:var(--ink3);flex:none}
.${p} .it .pn{color:var(--ink3);display:inline-flex}
.${p} .it .ls{flex:1;min-width:0;font-size:12px;color:var(--ink2);white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.${p} .it .ls .hl{color:var(--danger)}
.${p} .it .mi{color:var(--ink4);display:inline-flex}
`

/* 聊天气泡区与输入区（002 与 003 共用） */
const CHAT = (p) => `
.${p} .chh{display:flex;align-items:center;gap:12px;padding:0 16px;height:64px;border-bottom:1px solid var(--line);flex:none;position:relative}
.${p} .who{flex:1;min-width:0;display:flex;flex-direction:column}
.${p} .who b{font-size:16px;font-weight:600;line-height:24px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.${p} .who span{font-size:12px;color:var(--ink3);line-height:18px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.${p} .who span.ty{color:var(--p-text)}
.${p} .bx{position:relative;flex:1;min-height:0;background:var(--n1)}
.${p} .ml{height:100%;overflow-y:auto;padding:16px 20px 8px;display:flex;flex-direction:column;gap:10px;scrollbar-width:thin;scrollbar-color:var(--n8) transparent}
.${p} .ml .emp{margin:auto}
.${p} .dy{text-align:center;margin:6px 0 2px}
.${p} .dy span{display:inline-block;font-size:12px;color:var(--ink3);background:var(--n4);border-radius:16px;padding:0 10px;line-height:20px}
.${p} .mg{display:flex;gap:10px;align-items:flex-end}
.${p} .mg.me{flex-direction:row-reverse}
.${p} .ma{flex:none;width:32px;height:32px}
.${p} .ma.gh{visibility:hidden}
.${p} .mc{display:flex;flex-direction:column;align-items:flex-start;max-width:72%;min-width:0}
.${p} .mg.me .mc{align-items:flex-end}
.${p} .bb{padding:8px 12px;border-radius:12px 12px 12px 4px;background:var(--card);border:1px solid var(--n5);font-size:14px;line-height:22px;word-break:break-word;white-space:pre-wrap;animation:adcmin .22s cubic-bezier(.2,0,0,1)}
.${p} .mg.me .bb{border-radius:12px 12px 4px 12px;background:var(--p);border-color:var(--p);color:#fff}
.${p} .bb.fl{display:flex;gap:10px;align-items:center;min-width:220px;white-space:normal}
.${p} .bb.fl .fi{width:36px;height:36px;border-radius:8px;background:var(--pt);color:var(--p-text);display:inline-flex;align-items:center;justify-content:center;flex:none}
.${p} .bb.fl .fn{display:flex;flex-direction:column;min-width:0}
.${p} .bb.fl b{font-weight:600;font-size:14px;line-height:20px;word-break:break-all}
.${p} .bb.fl em{font-size:12px;color:var(--ink3);line-height:18px}
.${p} .bb.od{min-width:230px;white-space:normal;line-height:20px}
.${p} .bb.od .oa{display:flex;align-items:center;justify-content:space-between;gap:10px}
.${p} .bb.od .oa b{font-weight:600;font-variant-numeric:tabular-nums}
.${p} .bb.od .ob{color:var(--ink2);margin-top:4px}
.${p} .bb.od .oc{margin-top:4px;font-size:12px;color:var(--ink3)}
.${p} .bb.od .oc b{font-size:14px;color:var(--ink);font-weight:600}
.${p} .ms{font-size:12px;color:var(--ink3);line-height:18px;margin-top:2px}
.${p} .tp .bb{display:flex;gap:4px;align-items:center;height:38px;padding:0 14px}
.${p} .tp i{width:6px;height:6px;border-radius:50%;background:color-mix(in srgb,var(--n11) 44%,var(--n12));animation:adcmdot 1s infinite}
.${p} .tp i:nth-child(2){animation-delay:.15s}.${p} .tp i:nth-child(3){animation-delay:.3s}
@keyframes adcmdot{0%,60%,100%{opacity:.35;transform:none}30%{opacity:1;transform:translateY(-3px)}}
@keyframes adcmin{from{opacity:0;transform:translateY(6px)}to{opacity:1;transform:none}}
.${p} .newp{position:absolute;left:50%;bottom:12px;transform:translateX(-50%);height:32px;padding:0 14px 0 10px;border-radius:16px;background:var(--card);border:1px solid var(--n7);box-shadow:0 4px 14px var(--sh12);color:var(--p-text);font-size:14px;font-weight:600;display:inline-flex;gap:4px;align-items:center;white-space:nowrap}
.${p} .cp{position:relative;border-top:1px solid var(--line);padding:6px 16px 14px;background:var(--card);flex:none}
.${p} .cp .til{display:flex;gap:2px;margin-bottom:4px}
.${p} .cp .rw{display:flex;gap:10px;align-items:flex-end}
.${p} .cp textarea{flex:1;min-width:0;resize:none;height:40px;max-height:98px;border:1px solid var(--n7);border-radius:8px;padding:8px 12px;font:inherit;font-size:14px;line-height:22px;color:var(--ink);background:var(--card);outline:none;transition:border-color .15s}
.${p} .cp textarea::placeholder{color:var(--ink4)}
.${p} .cp textarea:focus{border-color:var(--ink2)}
.${p} .cp .snd{height:40px;padding:0 16px}
.${p} .emo{position:absolute;left:12px;bottom:calc(100% - 4px);width:272px;padding:8px;background:var(--card);border:1px solid var(--line2);border-radius:12px;box-shadow:0 10px 30px var(--sh14);display:grid;grid-template-columns:repeat(8,1fr);gap:2px;z-index:5}
.${p} .emo button{height:30px;border-radius:4px;font-size:18px;line-height:30px}
.${p} .emo button:hover{background:var(--soft)}
`
const EMO_QUICK = ['😀', '😊', '😂', '🙏', '👍', '👌', '🎉', '❤️', '🤝', '💪', '😅', '🤔', '👀', '✅', '🔥', '😭']
const EMO_HTML = EMO_QUICK.map((e) => `<button type="button" data-e="${e}" aria-label="插入表情">${e}</button>`).join('')

/* 聊天核心：气泡渲染、发送、输入中、对方自动回复、滚到底、新消息提示 */
const bubble = (m, conv, showAv) => {
  const me = m.from === 'me'
  let body
  if (m.file) body = `<div class="bb fl"><span class="fi">${ic('file', 20)}</span><span class="fn"><b>${esc(m.file)}</b><em>${m.size}</em></span></div>`
  else if (m.order) body = `<div class="bb od"><div class="oa"><b>订单 ${m.order.no}</b><span class="tag ${m.order.tone}">${m.order.st}</span></div><div class="ob">${m.order.sku} × ${m.order.q}</div><div class="oc">实付 <b>${fmt(m.order.amt)}</b></div></div>`
  else body = `<div class="bb">${esc(m.text)}</div>`
  return `<div class="mg${me ? ' me' : ''}" data-from="${m.from}"><span class="ma${showAv ? '' : ' gh'}">${me ? critter(3, 32) : critter(conv.av, 32)}</span><div class="mc">${body}${m.status ? `<span class="ms">${m.status}</span>` : ''}</div></div>`
}
const bubbles = (conv) => !conv.msgs.length
  ? `<div class="emp">${ic('chat', 28)}<b>暂无消息</b><span>发送第一条消息开始沟通</span></div>`
  : conv.msgs.map((m, i) => { const n = conv.msgs[i + 1]; return m.day ? `<div class="dy"><span>${m.day}</span></div>` : bubble(m, conv, !(n && !n.day && n.from === m.from)) }).join('')
const hhmm = (m) => String(Math.floor(m / 60)).padStart(2, '0') + ':' + String(m % 60).padStart(2, '0')

function chatCore(r, cfg) {
  const box = $(r, '.ml'), ta = $(r, '.cp textarea'), snd = $(r, '.snd'), nw = $(r, '.newp'), emo = $(r, '.emo'), emoBtn = $(r, '[data-emo]')
  const S = { cur: null, min: cfg.min }
  const near = () => box.scrollHeight - box.scrollTop - box.clientHeight < 80
  const down = (smooth) => box.scrollTo({ top: box.scrollHeight, behavior: smooth ? 'smooth' : 'auto' })
  const typing = (conv, on) => { conv.typing = on; if (cfg.typing) cfg.typing(conv, on) }
  const showTyping = (conv) => {
    typing(conv, true)
    if (S.cur !== conv || $(box, '.tp')) return
    const was = near()
    box.insertAdjacentHTML('beforeend', `<div class="mg tp" data-from="peer"><span class="ma">${critter(conv.av, 32)}</span><div class="mc"><div class="bb"><i></i><i></i><i></i></div></div></div>`)
    if (was) down(true)
  }
  const draw = (conv) => {
    S.cur = conv; box.innerHTML = bubbles(conv); nw.hidden = true
    if (conv.typing) showTyping(conv)
    down(false); if (cfg.typing) cfg.typing(conv, !!conv.typing)
  }
  const add = (conv, m) => {
    const last = conv.msgs[conv.msgs.length - 1], pre = []
    if (last && last.at != null && m.at != null && m.at - last.at >= 5) pre.push({ day: hhmm(m.at) })
    if (m.from === 'me') conv.msgs.forEach((x) => { delete x.status })
    conv.msgs.push(...pre, m)
    if (S.cur !== conv) return
    const e = $(box, '.emp'); if (e) e.remove()
    if (m.from === 'me') $$(box, '.ms').forEach((x) => x.remove())
    const tp = $(box, '.tp'); if (tp) tp.remove()
    const prev = box.lastElementChild
    if (prev && prev.classList.contains('mg') && prev.dataset.from === m.from && !pre.length) $(prev, '.ma').classList.add('gh')
    box.insertAdjacentHTML('beforeend', pre.map((d) => `<div class="dy"><span>${d.day}</span></div>`).join('') + bubble(m, conv, true))
  }
  const reply = (conv) => {
    typing(conv, false)
    const text = conv.replies[(conv.ri || 0) % conv.replies.length]; conv.ri = (conv.ri || 0) + 1
    const live = S.cur === conv, was = live && near()
    conv.msgs.forEach((x) => { if (x.status) x.status = '已读' })
    if (live) { const tp = $(box, '.tp'); if (tp) tp.remove(); $$(box, '.ms').forEach((x) => (x.textContent = '已读')) }
    add(conv, { from: 'peer', text, at: S.min })
    if (live) { if (was) down(true); else { nw.hidden = false } }
    if (cfg.onReply) cfg.onReply(conv, text, live)
  }
  const sync = () => { const ok = !!ta.value.trim(); snd.disabled = !ok; snd.title = ok ? '发送（Enter）' : '请先输入消息内容' }
  const send = () => {
    const text = ta.value.trim(); const conv = S.cur
    if (!text || !conv) return
    S.min += 1
    add(conv, { from: 'me', text, at: S.min, status: '已送达' })
    ta.value = ''; fit(ta); sync(); down(true); if (emo) emo.hidden = true
    if (cfg.onSend) cfg.onSend(conv, text, hhmm(S.min))
    clearTimeout(conv.t1); clearTimeout(conv.t2)
    conv.t1 = setTimeout(() => { if (r.isConnected) showTyping(conv) }, 700)
    conv.t2 = setTimeout(() => { if (r.isConnected) reply(conv) }, 2100)
  }
  ta.addEventListener('input', () => { fit(ta); sync() })
  ta.addEventListener('keydown', (e) => { if (e.key === 'Enter' && !e.shiftKey && !e.isComposing) { e.preventDefault(); send() } })
  snd.addEventListener('click', send)
  nw.addEventListener('click', () => { down(true); nw.hidden = true })
  box.addEventListener('scroll', () => { if (near()) nw.hidden = true })
  if (emo && emoBtn) {
    emoBtn.addEventListener('click', (e) => { e.stopPropagation(); emo.hidden = !emo.hidden; emoBtn.classList.toggle('on', !emo.hidden) })
    emo.addEventListener('click', (e) => { const b = e.target.closest('[data-e]'); if (b) insertAt(ta, b.dataset.e) })
    outside(r, (e) => { if (!emo.hidden && !e.target.closest('.emo')) { emo.hidden = true; emoBtn.classList.remove('on') } })
  }
  sync()
  return { S, draw, add, send, ta, down, box }
}

/* 会话列表控制：搜索 + 标签过滤 + 未读数（001 与 003 共用） */
function listCtl(r, onSel) {
  const lst = $(r, '.lst'), q = $(r, '.lp-q'), clr = $(r, '.lp .clr') || $(r, '.clr'), tot = $(r, '.tot'), emp = $(r, '.lst-emp')
  let tab = 'all'
  const its = () => $$(lst, '.it')
  const counts = () => {
    const u = its().filter((x) => x.dataset.mu !== '1').reduce((s, x) => s + (+x.dataset.un || 0), 0)
    tot.textContent = u; tot.hidden = !u
    const cn = $(r, '[data-t=un] .nbd'); if (cn) { const n = its().filter((x) => +x.dataset.un > 0).length; cn.textContent = n; cn.hidden = !n }
  }
  const apply = () => {
    const k = q.value.trim().toLowerCase(); let n = 0
    its().forEach((it) => {
      const ok = (tab === 'all' || (tab === 'un' && +it.dataset.un > 0) || (tab === 'at' && it.dataset.at === '1')) && (!k || it.textContent.toLowerCase().includes(k))
      it.hidden = !ok; if (ok) n++
    })
    emp.hidden = n > 0; clr.hidden = !q.value
    const eb = $(emp, 'b'); if (eb) eb.textContent = k ? '没有找到相关会话' : tab === 'un' ? '没有未读会话' : '没有提到你的会话'
  }
  const setUn = (it, n) => { it.dataset.un = n; const b = $(it, '.ub'); b.textContent = n; b.hidden = !n; counts() }
  const select = (it) => { its().forEach((x) => x.classList.toggle('on', x === it)); setUn(it, 0); if (onSel) onSel(it) }
  $$(r, '.tb [data-t]').forEach((b) => b.addEventListener('click', () => { tab = b.dataset.t; apply() }))
  q.addEventListener('input', apply)
  clr.addEventListener('click', () => { q.value = ''; apply(); q.focus() })
  lst.addEventListener('click', (e) => { const it = e.target.closest('.it'); if (it) select(it) })
  lst.addEventListener('keydown', (e) => { if (e.key === 'Enter' || e.key === ' ') { const it = e.target.closest('.it'); if (it) { e.preventDefault(); select(it) } } })
  counts(); apply()
  return { apply, counts, setUn, select, its }
}
const itemHTML = (c) => `<li class="it${c.sel ? ' on' : ''}" data-id="${c.id}" data-un="${c.un || 0}" data-at="${c.at ? 1 : 0}" data-mu="${c.mute ? 1 : 0}" tabindex="0" role="option">${c.g ? `<span class="gav">${ic('users', 20)}</span>` : av(c.i != null ? c.i : c.av, 40, c.on)}<div class="bd"><div class="r1"><b class="nm">${esc(c.n)}</b>${c.pin ? `<span class="pn" title="已置顶">${ic('cmpush', 14)}</span>` : ''}<span class="tm">${c.t}</span></div><div class="r2"><span class="ls">${c.at ? '<em class="hl">[有人@我] </em>' : ''}${c.draft ? '<em class="hl">[草稿] </em>' : ''}${esc(c.ls)}</span>${c.mute ? `<span class="mi" title="消息免打扰">${ic('cmmute', 14)}</span>` : ''}<span class="ub${c.mute ? ' mu' : ''}"${c.un ? '' : ' hidden'}>${c.un || 0}</span></div></div></li>`
const SEARCH_BOX = (ph) => `<div class="sch">${ic('search')}<input class="in lp-q" type="search" placeholder="${ph}" autocomplete="off" aria-label="搜索会话"><button class="clr" type="button" hidden aria-label="清空搜索">${ic('close', 16)}</button></div>`
const TABS3 = `<div class="tb" data-ix="tabs"><button type="button" data-t="all" class="on">全部</button><button type="button" data-t="un">未读<span class="nbd gy">0</span></button><button type="button" data-t="at">@我</button><i class="ink"></i></div>`

/* ================= AD-COMM-001 会话列表 ================= */
const CV1 = () => [
  { id: 'a1', n: '林小满', i: 0, ls: '好的，我下午三点前把对账单发给你', t: '10:32', un: 2, pin: 1, on: '' },
  { id: 'a2', n: '双十一大促备战群（运营 · 客服 · 仓储）', g: 1, ls: '陈晓雨：库存已同步到全部 12 家门店，大家再核对一遍', t: '10:18', un: 5, at: 1 },
  { id: 'a3', n: '陈晓雨', i: 1, ls: '这笔退款需要你确认一下', t: '09:47', un: 1, on: 'busy' },
  { id: 'a4', n: '财务部', g: 1, ls: '李安然：本月发票已全部开具完成', t: '昨天', un: 3, mute: 1 },
  { id: 'a5', n: '王子豪', i: 2, ls: '[图片]', t: '昨天', un: 0, on: 'off', sel: 1 },
  { id: 'a6', n: '周一帆', i: 0, ls: '下周的排班表我已经更新到共享表格里，你看看有没有冲突', t: '周二', un: 0, draft: 1, on: 'off' },
  { id: 'a7', n: '赵可心', i: 1, ls: '好的，谢谢！', t: '周一', un: 0, on: '' },
  { id: 'a8', n: '吴梓轩', i: 2, ls: '货已经到仓了，明天上午可以上架', t: '11-01', un: 0, on: 'off' },
]
def({
  id: 'AD-COMM-001', name: '会话列表', style: '未读+搜索', fit: '消息中心、客服工台、协作后台左侧的会话入口；要一眼看出谁有新消息、谁@了我',
  avoid: '会话超过几百条又不做分页或虚拟滚动；只有通知没有对话的页面请用通知中心页',
  kw: 'conversation 会话列表 未读 红点 搜索 置顶 免打扰 联系人 消息 inbox',
  css: K('adcomm001') + LIST('adcomm001') + `
.adcomm001{width:400px;max-width:100%;height:600px;display:flex;flex-direction:column}
.adcomm001 .hd{display:flex;align-items:center;gap:8px;padding:16px 16px 8px}
.adcomm001 .hd h3{font-size:18px;font-weight:600;line-height:28px}
.adcomm001 .sb{padding:4px 16px 12px}
.adcomm001 .lst{flex:1;min-height:0;overflow-y:auto;scrollbar-width:thin;scrollbar-color:var(--n8) transparent}
.adcomm001 .lst-emp{flex:1}`,
  html: () => `<div class="adcomm001"><div class="hd"><h3>消息</h3><span class="tot" title="未读消息总数">8</span><span class="sp"></span><button class="ib" type="button" data-toast="选择联系人后发起会话" aria-label="发起会话">${ic('edit')}</button></div><div class="sb">${SEARCH_BOX('搜索会话或联系人')}</div>${TABS3}<ul class="lst" role="listbox" aria-label="会话列表">${CV1().map(itemHTML).join('')}</ul><div class="emp lst-emp" hidden>${ic('search', 28)}<b>没有找到相关会话</b><span>换个关键词试试，或清空搜索</span></div></div>`,
  js: (r) => { listCtl(r) },
})

/* ================= AD-COMM-002 单聊窗口 ================= */
const D002 = () => ({
  n: '林小满', av: 0, replies: ['收到，我马上处理～', '好的，稍后给你回复', '这个我再和财务确认一下', '没问题，已经记下了', '可以的，我先看一下情况再同步你'],
  msgs: [
    { day: '今天 09:41' },
    { from: 'peer', text: '早，11 月的对账单我这边整理好了，你有空看一下' },
    { from: 'peer', file: '对账单-2026-11.xlsx', size: '126 KB' },
    { from: 'me', text: '收到，我先核对差异的那几笔' },
    { day: '10:24' },
    { from: 'peer', text: '有三笔和系统里对不上，订单号我标黄了' },
    { from: 'peer', text: '主要是退款在途的订单，应该不是真的差异。但这个月退货比较多，财务那边也问了两次，所以想请你再确认一遍。', at: 624 },
    { from: 'me', text: '好的，我下午三点前把核对结果发给你', status: '已读', at: 631 },
  ],
})
def({
  id: 'AD-COMM-002', name: '单聊窗口', style: '气泡+自动回复', fit: '后台内嵌的一对一沟通：客服、同事私聊、订单咨询；发送后追加气泡并滚到底，能看到对方正在输入',
  avoid: '需要成员管理、@全体的群聊场景；聊天记录很长时要配合“加载更早消息”',
  kw: 'chat 聊天 单聊 气泡 发送 输入中 已读 客服 消息窗口 滚动到底',
  css: K('adcomm002') + CHAT('adcomm002') + `
.adcomm002{width:600px;max-width:100%;height:600px;display:flex;flex-direction:column}
.adcomm002 .mn{position:absolute;right:12px;top:56px;width:176px;padding:4px;background:var(--card);border:1px solid var(--line2);border-radius:8px;box-shadow:0 10px 30px var(--sh14);z-index:6}
.adcomm002 .mn button{width:100%;height:36px;padding:0 10px;border-radius:4px;display:flex;align-items:center;gap:8px;font-size:14px;text-align:left}
.adcomm002 .mn button:hover{background:var(--n3)}
.adcomm002 .mn button.dgr{color:var(--danger)}
.adcomm002 .mn hr{border:0;border-top:1px solid var(--line);margin:4px 0}`,
  html: () => `<div class="adcomm002"><div class="chh">${av(0, 40, 'on')}<div class="who"><b>林小满</b><span>在线 · 运营部</span></div><button class="ib" type="button" data-toast="在聊天记录中查找" aria-label="查找聊天记录">${ic('search')}</button><button class="ib" type="button" data-toast="正在发起语音通话…" aria-label="语音通话">${ic('phone')}</button><button class="ib" type="button" data-mnb aria-label="更多操作">${ic('more')}</button><div class="mn" hidden><button type="button" data-pin>${ic('cmpush')}<span>置顶会话</span></button><button type="button" data-mute>${ic('cmmute')}<span>消息免打扰</span></button><hr><button type="button" class="dgr" data-open="clr">${ic('trash')}<span>清空聊天记录</span></button></div></div><div class="bx"><div class="ml">${bubbles(D002())}</div><button class="newp" type="button" hidden>${ic('arrowdown', 16)}有新消息</button></div><div class="cp"><div class="til"><button class="ib" type="button" data-emo aria-label="插入表情">${ic('cmsmile')}</button><button class="ib" type="button" data-toast="选择文件后发送" aria-label="发送文件">${ic('cmclip')}</button><button class="ib" type="button" data-toast="选择图片后发送" aria-label="发送图片">${ic('image')}</button></div><div class="rw"><textarea rows="1" placeholder="输入消息，Enter 发送" title="Enter 发送，Shift + Enter 换行" aria-label="消息内容"></textarea><button class="cbt pri snd" type="button" disabled>${ic('cmsend', 16)}发送</button></div><div class="emo" hidden>${EMO_HTML}</div></div><div class="ix-ov" data-ov="clr"><div class="ix-mask"></div><div class="dlg" role="dialog" aria-modal="true"><h4>清空与林小满的聊天记录？</h4><p>清空后所有消息无法恢复，对方的记录不受影响。</p><div class="df"><button class="cbt" type="button" data-close>取消</button><button class="cbt dg" type="button" data-clr>清空记录</button></div></div></div></div>`,
  js: (r) => {
    const conv = D002(); const sub = $(r, '.who span'), mn = $(r, '.mn'), mb = $(r, '[data-mnb]')
    const core = chatCore(r, { min: 632, typing: (c, on) => { sub.textContent = on ? '对方正在输入…' : '在线 · 运营部'; sub.classList.toggle('ty', on) } })
    core.draw(conv)
    mb.addEventListener('click', (e) => { e.stopPropagation(); mn.hidden = !mn.hidden; mb.classList.toggle('on', !mn.hidden) })
    outside(r, (e) => { if (!mn.hidden && !e.target.closest('.mn')) { mn.hidden = true; mb.classList.remove('on') } })
    let pinned = false, muted = false
    $(r, '[data-pin]').addEventListener('click', (e) => { pinned = !pinned; $(e.currentTarget, 'span:last-child').textContent = pinned ? '取消置顶' : '置顶会话'; mn.hidden = true; mb.classList.remove('on'); T(r, pinned ? '已置顶会话' : '已取消置顶') })
    $(r, '[data-mute]').addEventListener('click', (e) => { muted = !muted; $(e.currentTarget, 'span:last-child').textContent = muted ? '取消免打扰' : '消息免打扰'; mn.hidden = true; mb.classList.remove('on'); T(r, muted ? '已开启消息免打扰' : '已关闭消息免打扰') })
    $(r, '[data-open=clr]').addEventListener('click', () => { mn.hidden = true; mb.classList.remove('on') })
    $(r, '[data-clr]').addEventListener('click', () => { conv.msgs.length = 0; core.draw(conv); $(r, '[data-ov=clr]').classList.remove('show'); T(r, '已清空聊天记录') })
  },
})

/* ================= AD-COMM-003 客服会话工作台（三栏） ================= */
const ORD = (i, st, tone) => { const o = ORDER_ROWS[i]; return { no: o.no, sku: o.sku, q: o.q, amt: o.amt, st: st || o.st, tone: tone || ({ warn: 'warn', info: 'pri', ok: 'ok', mute: '', danger: 'red' }[o.tone] || '') } }
const D003 = () => [
  { id: 'w1', n: '林小满', av: 0, ls: '好的，那大概什么时候能到？', t: '10:32', un: 2, pin: 1, on: 'on', tag: '金卡会员', sel: 1, sub: '在线 · 来自小程序咨询',
    info: { lv: '金卡会员', ph: '138****2046', store: '静安旗舰店', since: '2024-03-18', spent: 12860, ords: [ORD(0, '待发货', 'warn'), ORD(7, '已完成', 'ok')] },
    replies: ['好的，谢谢你～', '那我再等一等，麻烦尽快哦', '收到，我晚点再看一下物流'],
    msgs: [{ day: '今天 09:58' }, { from: 'peer', text: '你好，我昨天买的耳机到现在还没发货，订单号发你了' }, { from: 'peer', order: ORD(0, '待发货', 'warn') }, { from: 'me', text: '您好，我帮您查一下，请稍等～', at: 600 }, { from: 'me', text: '已查到，仓库今天上午会发出，快递单号生成后会第一时间通知您。', at: 601 }, { from: 'peer', text: '好的，那大概什么时候能到？', at: 632 }] },
  { id: 'w2', n: '赵可心', av: 1, ls: '已经填好了，麻烦尽快开具', t: '10:05', un: 1, on: 'on', tag: '普通会员', sub: '在线 · 来自公众号', at: 0,
    info: { lv: '普通会员', ph: '139****8821', store: '线上商城', since: '2025-06-02', spent: 2380, ords: [ORD(5, '已完成', 'ok')] },
    replies: ['好的，谢谢！', '收到～'],
    msgs: [{ day: '今天 10:01' }, { from: 'peer', text: '请问发票可以开成公司抬头吗？' }, { from: 'me', text: '可以的，请在订单详情里填写抬头和税号。', at: 602 }, { from: 'peer', text: '已经填好了，麻烦尽快开具', at: 605 }] },
  { id: 'w3', n: '吴梓轩', av: 2, ls: '收到的杯子杯口有个小缺口，能换货吗', t: '昨天', un: 0, on: 'busy', tag: '新客', sub: '忙碌 · 来自小程序咨询',
    info: { lv: '新客', ph: '136****0417', store: '徐汇体验店', since: '2026-10-29', spent: 69, ords: [ORD(2, '已完成', 'ok')] },
    replies: ['好的，我这就拍照上传', '谢谢，等你们消息'],
    msgs: [{ day: '昨天 16:20' }, { from: 'peer', text: '收到的杯子杯口有个小缺口，能换货吗' }, { from: 'me', text: '非常抱歉给您带来不便！请您拍照上传，我们马上为您安排换货。', at: 981 }] },
  { id: 'w4', n: '郑佳怡', av: 3, ls: '谢谢，已经收到了', t: '昨天', un: 0, on: 'off', tag: '金卡会员', sub: '离线 · 最后在线 昨天 21:40',
    info: { lv: '金卡会员', ph: '137****5306', store: '静安旗舰店', since: '2023-11-11', spent: 8920, ords: [ORD(3, '已完成', 'ok'), ORD(9, '退款中', 'red')] },
    replies: ['好的～', '收到，谢谢'],
    msgs: [{ day: '昨天 14:12' }, { from: 'me', text: '您的订单已经签收了，如有问题随时联系我们。', at: 852 }, { from: 'peer', text: '谢谢，已经收到了', at: 860 }] },
  { id: 'w5', n: '孙明哲', av: 0, ls: '这个活动的券可以和满减一起用吗？', t: '周二', un: 0, on: 'off', tag: '普通会员', sub: '离线 · 最后在线 周二 18:03',
    info: { lv: '普通会员', ph: '135****7794', store: '线上商城', since: '2025-01-20', spent: 1420, ords: [ORD(4, '已取消', '')] },
    replies: ['明白了，谢谢', '好的，我再看看'],
    msgs: [{ day: '周二 17:46' }, { from: 'peer', text: '这个活动的券可以和满减一起用吗？' }, { from: 'me', text: '同一订单优惠券与满减可叠加，但不能与秒杀价同时使用哦。', at: 1068 }] },
]
const info003 = (c) => `<div class="itop">${av(c.av, 56, c.on)}<b>${esc(c.n)}</b><span class="tag pri">${c.info.lv}</span></div><dl class="kv"><div><dt>手机</dt><dd>${c.info.ph}</dd></div><div><dt>常用门店</dt><dd>${c.info.store}</dd></div><div><dt>注册时间</dt><dd>${c.info.since}</dd></div><div><dt>累计消费</dt><dd class="am">${fmt(c.info.spent)}</dd></div></dl><h4>最近订单</h4><ul class="ords">${c.info.ords.map((o) => `<li><div class="oa"><b>${o.no}</b><span class="tag ${o.tone}">${o.st}</span></div><div class="ob"><span>${o.sku} × ${o.q}</span><span class="am">${fmt(o.amt)}</span></div></li>`).join('')}</ul>`
const QR3 = ['稍等，我马上帮您查询', '已为您登记，24 小时内回复', '抱歉给您带来不便', '感谢您的反馈']
def({
  id: 'AD-COMM-003', name: '客服会话工作台', style: '三栏+快捷回复', wide: true,
  fit: '客服、运营每天要处理大量咨询的工作台：左选会话，中间沟通，右边看客户资料和订单，快捷回复减少重复打字',
  avoid: '只偶尔收几条消息的后台（用单聊窗口就够）；窄屏下资料栏会收起，不要把关键操作只放在资料栏',
  kw: '客服工作台 会话 聊天 三栏 快捷回复 客户资料 订单卡片 customer-service im workbench',
  css: K('adcomm003') + LIST('adcomm003') + CHAT('adcomm003') + `
.adcomm003{width:1400px;max-width:100%;height:660px}
.adcomm003 .g{display:grid;grid-template-columns:320px minmax(0,1fr) 288px;height:100%}
.adcomm003.noif .g{grid-template-columns:320px minmax(0,1fr)}
.adcomm003.noif .if{display:none}
.adcomm003 .lp{display:flex;flex-direction:column;min-height:0;min-width:0;border-right:1px solid var(--line)}
.adcomm003 .lp .hd{display:flex;align-items:center;gap:8px;padding:16px 16px 8px}
.adcomm003 .lp .hd h3{font-size:18px;font-weight:600;line-height:28px}
.adcomm003 .lp .sb{padding:4px 16px 12px}
.adcomm003 .lst{flex:1;min-height:0;overflow-y:auto;scrollbar-width:thin;scrollbar-color:var(--n8) transparent}
.adcomm003 .lst-emp{flex:1}
.adcomm003 .ch{display:flex;flex-direction:column;min-width:0;min-height:0}
.adcomm003 .bk{display:none}
.adcomm003 .qr{display:flex;gap:8px;padding:8px 16px 0;overflow-x:auto;scrollbar-width:none;background:var(--card);border-top:1px solid var(--line)}
.adcomm003 .qr::-webkit-scrollbar{display:none}
.adcomm003 .qr button{flex:none;height:28px;padding:0 10px;border-radius:16px;background:var(--soft);color:var(--ink2);font-size:12px;transition:background .15s,color .15s}
.adcomm003 .qr button:hover{background:var(--pt);color:var(--p-text)}
.adcomm003 .cp{border-top:0;padding-top:4px}
.adcomm003 .if{border-left:1px solid var(--line);overflow-y:auto;padding:20px 16px;min-height:0;scrollbar-width:thin;scrollbar-color:var(--n8) transparent}
.adcomm003 .itop{display:flex;flex-direction:column;align-items:center;gap:6px;padding-bottom:16px;border-bottom:1px solid var(--line)}
.adcomm003 .itop b{font-size:16px;font-weight:600}
.adcomm003 .kv{margin:12px 0 16px;display:flex;flex-direction:column;gap:10px}
.adcomm003 .kv div{display:flex;justify-content:space-between;gap:12px}
.adcomm003 .kv dt{color:var(--ink3)}
.adcomm003 .kv dd{text-align:right;font-variant-numeric:tabular-nums}
.adcomm003 .am{font-weight:600;font-variant-numeric:tabular-nums;text-align:right}
.adcomm003 .if h4{font-size:14px;font-weight:600;margin-bottom:8px}
.adcomm003 .ords{display:flex;flex-direction:column;gap:8px}
.adcomm003 .ords li{padding:10px 12px;border:1px solid var(--line);border-radius:8px;background:var(--n1)}
.adcomm003 .ords .oa{display:flex;justify-content:space-between;align-items:center;gap:8px}
.adcomm003 .ords .oa b{font-size:12px;font-weight:600;color:var(--ink2);font-variant-numeric:tabular-nums}
.adcomm003 .ords .ob{display:flex;justify-content:space-between;gap:8px;margin-top:4px}
.adcomm003 .ords .ob span:first-child{min-width:0;overflow:hidden;text-overflow:ellipsis;white-space:nowrap}
@container (max-width:1100px){.adcomm003 .g{grid-template-columns:300px minmax(0,1fr)}.adcomm003 .if,.adcomm003 .tgi{display:none}}
@container (max-width:760px){.adcomm003 .g{grid-template-columns:minmax(0,1fr)}.adcomm003 .lp{border-right:0}.adcomm003 .ch{display:none}.adcomm003[data-view=chat] .lp{display:none}.adcomm003[data-view=chat] .ch{display:flex}.adcomm003 .bk{display:inline-flex}.adcomm003 .mc{max-width:82%}}`,
  html: () => { const d = D003(), c = d[0]; return `<div class="adcomm003" data-view="list"><div class="g"><aside class="lp"><div class="hd"><h3>咨询</h3><span class="tot" title="未读消息总数">3</span></div><div class="sb">${SEARCH_BOX('搜索客户或消息')}</div>${TABS3}<ul class="lst" role="listbox" aria-label="咨询会话">${d.map(itemHTML).join('')}</ul><div class="emp lst-emp" hidden>${ic('search', 28)}<b>没有找到相关会话</b><span>换个关键词试试，或清空搜索</span></div></aside><section class="ch"><div class="chh"><button class="ib bk" type="button" aria-label="返回会话列表">${ic('left')}</button>${av(c.av, 40, c.on)}<div class="who"><b>${esc(c.n)}</b><span>${c.sub}</span></div><button class="ib" type="button" data-toast="正在发起语音通话…" aria-label="语音通话">${ic('phone')}</button><button class="ib tgi on" type="button" data-tgi aria-label="显示或隐藏客户资料" title="客户资料">${ic('user')}</button></div><div class="bx"><div class="ml">${bubbles(c)}</div><button class="newp" type="button" hidden>${ic('arrowdown', 16)}有新消息</button></div><div class="qr" data-ix="drag">${QR3.map((q) => `<button type="button" data-q="${q}">${q}</button>`).join('')}</div><div class="cp"><div class="til"><button class="ib" type="button" data-emo aria-label="插入表情">${ic('cmsmile')}</button><button class="ib" type="button" data-toast="选择文件后发送" aria-label="发送文件">${ic('cmclip')}</button><button class="ib" type="button" data-toast="选择图片后发送" aria-label="发送图片">${ic('image')}</button></div><div class="rw"><textarea rows="1" placeholder="输入回复，Enter 发送" title="Enter 发送，Shift + Enter 换行" aria-label="回复内容"></textarea><button class="cbt pri snd" type="button" disabled>${ic('cmsend', 16)}发送</button></div><div class="emo" hidden>${EMO_HTML}</div></div></section><aside class="if scr">${info003(c)}</aside></div></div>` },
  js: (r) => {
    const root = $(r, '.adcomm003'), data = D003(); const by = (id) => data.find((x) => x.id === id)
    const head = $(r, '.chh'), ifp = $(r, '.if'), lst = $(r, '.lst')
    const core = chatCore(r, {
      min: 633,
      typing: (c, on) => { if (core.S.cur !== c) return; const s = $(head, '.who span'); s.textContent = on ? '对方正在输入…' : c.sub; s.classList.toggle('ty', on) },
      onSend: (c, text, tm) => { const it = $(lst, `[data-id=${c.id}]`); $(it, '.ls').textContent = text; $(it, '.tm').textContent = tm; const firstFree = $$(lst, '.it').find((x) => !by(x.dataset.id).pin); if (firstFree && firstFree !== it && !c.pin) lst.insertBefore(it, firstFree) },
      onReply: (c, text, live) => { const it = $(lst, `[data-id=${c.id}]`); $(it, '.ls').textContent = text; $(it, '.tm').textContent = hhmm(core.S.min); if (!live) ctl.setUn(it, (+it.dataset.un || 0) + 1) },
    })
    const open = (it) => {
      const c = by(it.dataset.id); core.draw(c)
      $(head, '.avw').outerHTML = av(c.av, 40, c.on); $(head, '.who b').textContent = c.n
      const s = $(head, '.who span'); s.textContent = c.typing ? '对方正在输入…' : c.sub; s.classList.toggle('ty', !!c.typing)
      ifp.innerHTML = info003(c); root.dataset.view = 'chat'
    }
    const ctl = listCtl(r, open)
    core.draw(by('w1')); ctl.counts()
    $(r, '.bk').addEventListener('click', () => { root.dataset.view = 'list' })
    $(r, '[data-tgi]').addEventListener('click', (e) => { const off = root.classList.toggle('noif'); e.currentTarget.classList.toggle('on', !off) })
    $$(r, '.qr [data-q]').forEach((b) => b.addEventListener('click', () => { const ta = core.ta; ta.value = ta.value ? ta.value + b.dataset.q : b.dataset.q; ta.focus(); ta.dispatchEvent(new Event('input', { bubbles: true })) }))
  },
})

/* ================= AD-COMM-004 收件箱与阅读面板 ================= */
const MAILS = () => [
  { id: 'm1', n: '李安然', d: '财务部', em: 'anran.li@example.com', av: 3, subj: '11 月供应商对账单已发出，请于本周五前确认', pre: '您好，附件为 11 月 1 日至 11 月 30 日的对账单，请核对金额与单据是否一致……', t: '10:12', full: '今天 10:12', un: 1, star: 0, tag: '财务', tone: 'pri', att: [['对账单-2026-11.xlsx', '126 KB']],
    body: ['您好，', '附件为 11 月 1 日至 11 月 30 日的供应商对账单，共 86 笔，合计应付 ¥128,640.00。请重点核对第 12、37、58 笔的退款冲减金额，这三笔与系统记录有出入。', '麻烦在本周五（11-06）下班前回复确认；如有疑问，可以直接在邮件里批注，我会在当天处理。', '谢谢！'] },
  { id: 'm2', n: '订单中心', d: '系统通知', em: 'noreply@example.com', av: 1, subj: '【提醒】3 笔订单超过 24 小时未发货', pre: '以下订单已超过承诺发货时间，请尽快处理，避免触发超时赔付规则……', t: '09:30', full: '今天 09:30', un: 1, star: 1, tag: '订单', tone: 'warn', att: [],
    body: ['以下订单已超过承诺发货时间，请尽快处理：', 'SO2026110400128 · 无线降噪耳机 × 1 · 已超时 26 小时', 'SO2026110400121 · 轻量跑鞋 × 2 · 已超时 25 小时', 'SO2026110400114 · 保温水杯 × 1 · 已超时 24 小时', '如因缺货无法发货，请在订单中标记并联系客户，系统将暂停超时计算。'] },
  { id: 'm3', n: '陈晓雨', d: '客服部', em: 'xiaoyu.chen@example.com', av: 1, subj: '退款申请待你审批：SO2026110400121', pre: '客户申请退款 ¥329.00，原因是尺码不合适，已超过 7 天无理由期限，需要你确认是否特批。', t: '昨天', full: '昨天 18:20', un: 1, star: 0, tag: '审批', tone: 'warn', att: [['沟通记录截图.png', '842 KB']],
    body: ['你好，', '客户申请退款 ¥329.00，原因是尺码不合适。订单签收已满 9 天，超过 7 天无理由期限，但客户是金卡会员，且鞋子未拆封。', '我的建议是特批退款，运费由客户承担。请你确认后在审批单里点同意或驳回，我这边再通知客户。'] },
  { id: 'm4', n: '王子豪', d: '技术部', em: 'zihao.wang@example.com', av: 2, subj: '本周六凌晨 01:00–03:00 数据库升级维护', pre: '升级期间后台可正常浏览，但订单导出、批量发货和会话消息会暂时不可用。', t: '昨天', full: '昨天 15:46', un: 0, star: 1, tag: '系统', tone: '', att: [],
    body: ['各位好，', '本周六（11-07）凌晨 01:00–03:00 将进行数据库版本升级。升级期间后台可正常浏览，但订单导出、批量发货和会话消息会暂时不可用。', '请提前把需要导出的数据导出，大促期间的紧急发货请在周五 24:00 前完成。如有特殊情况请直接联系我。'] },
  { id: 'm5', n: '周一帆', d: '市场部', em: 'yifan.zhou@example.com', av: 0, subj: '双十一主视觉海报终稿，请确认后我今晚上线', pre: '终稿已按上次评审意见调整：主标题放大、价格区拉开层级，附件为全部尺寸的源文件……', t: '11-02', full: '11-02 17:05', un: 0, star: 0, tag: '市场', tone: 'pri', att: [['双十一海报终稿.zip', '12.4 MB'], ['配色与字体说明.pdf', '1.2 MB']],
    body: ['大家好，', '终稿已按上次评审意见调整：主标题放大、价格区拉开层级，底部权益条改成单行。附件是全部尺寸的源文件和导出图。', '如无修改意见，我今晚 20:00 统一上线，请在 19:30 前回复。'] },
  { id: 'm6', n: '赵可心', d: '运营部', em: 'kexin.zhao@example.com', av: 1, subj: '回复：关于满减叠加优惠券规则的几个疑问，想和财务、客服一起对齐后再定稿', pre: '我整理了三种叠加场景，想请财务确认毛利，也请客服评估一下用户理解成本……', t: '11-02', full: '11-02 11:38', un: 0, star: 0, tag: '运营', tone: '', att: [],
    body: ['各位，', '我整理了三种叠加场景：满减 + 单张券、满减 + 两张券、秒杀价不参与满减。想请财务确认毛利，也请客服评估用户理解成本。', '建议周四上午 10:00 开 20 分钟短会对齐，会前我把测算表发给大家。'] },
  { id: 'm7', n: '吴梓轩', d: '仓储部', em: 'zixuan.wu@example.com', av: 2, subj: '昨日出库日报：共出库 1,286 单', pre: '出库 1,286 单，较前日增长 18%；缺货拦截 14 单，主要集中在保温水杯和耳机。', t: '11-01', full: '11-01 08:30', un: 0, star: 0, tag: '仓储', tone: '', att: [['出库日报-1031.xlsx', '88 KB']],
    body: ['出库 1,286 单，较前日增长 18%；缺货拦截 14 单，主要集中在保温水杯和无线降噪耳机，已通知采购补货，预计周二到仓。'] },
  { id: 'm8', n: '郑佳怡', d: '行政部', em: 'jiayi.zheng@example.com', av: 3, subj: '11 月部门团建报名开始啦', pre: '本月团建定在 11-14（周六），可选城市骑行或手作工坊，请于 11-08 前在表格里登记。', t: '10-30', full: '10-30 14:00', un: 0, star: 0, tag: '行政', tone: '', att: [],
    body: ['大家好，', '本月团建定在 11-14（周六），可选城市骑行或手作工坊两个方案，请于 11-08 前在共享表格里登记，名额有限，先到先得。'] },
]
const mailRow = (m) => `<li class="mr${m.un ? ' un' : ''}" data-id="${m.id}" data-un="${m.un}" data-star="${m.star}" tabindex="0" role="option"><i class="ud" aria-hidden="true"></i><div class="bd"><div class="r1"><b class="nm">${esc(m.n)}<em>${m.d}</em></b><span class="tm">${m.t}</span></div><div class="sj">${esc(m.subj)}</div><div class="r3"><span class="ls">${esc(m.pre)}</span>${m.att.length ? `<span class="cl" title="含附件">${ic('cmclip', 14)}</span>` : ''}<button class="stb${m.star ? ' on' : ''}" type="button" data-star-btn title="${m.star ? '取消星标' : '加星标'}" aria-label="星标">${ic(m.star ? 'starf' : 'star', 16)}</button></div></div></li>`
const readMail = (m) => `<div class="rtb"><button class="ib bk" type="button" aria-label="返回邮件列表">${ic('left')}</button><button class="ib" type="button" data-act="archive" title="归档" aria-label="归档">${ic('cmarchive')}</button><button class="ib" type="button" data-act="del" title="删除" aria-label="删除">${ic('trash')}</button><button class="ib" type="button" data-act="unread" title="标为未读" aria-label="标为未读">${ic('mail')}</button><span class="sp"></span><button class="ib stt${m.star ? ' on' : ''}" type="button" data-act="star" title="${m.star ? '取消星标' : '加星标'}" aria-label="星标">${ic(m.star ? 'starf' : 'star')}</button></div><div class="rbd scr"><h2 class="sj2">${esc(m.subj)}</h2><div class="mh">${av(m.av, 40)}<div class="mm"><div class="hm1"><b>${esc(m.n)}</b><span class="tag ${m.tone}">${m.tag}</span><span>&lt;${m.em}&gt;</span></div><div class="hm2">发给 我 · ${m.full}</div></div></div><div class="txt">${m.body.map((p) => `<p>${esc(p)}</p>`).join('')}</div>${m.att.length ? `<div class="atts">${m.att.map((a) => `<button class="att" type="button" data-att="${a[0]}"><span class="fi">${ic('file', 18)}</span><span class="fn"><b>${a[0]}</b><em>${a[1]}</em></span>${ic('download', 16)}</button>`).join('')}</div>` : ''}<div class="thr">${(m.thread || []).map((x) => `<div class="th">${av(3, 32)}<div><div class="hm1"><b>我</b><span>刚刚</span></div><p>${esc(x)}</p></div></div>`).join('')}</div><div class="act"><button class="cbt" type="button" data-reply>${ic('cmreply', 16)}回复</button><button class="cbt" type="button" data-toast="选择收件人后转发">${ic('cmforward', 16)}转发</button></div><div class="rbox" hidden><textarea rows="4" placeholder="回复给 ${esc(m.n)}…" aria-label="回复内容"></textarea><div class="er" hidden>请输入回复内容</div><div class="rf"><button class="cbt" type="button" data-rc>取消</button><button class="cbt pri" type="button" data-rs>${ic('cmsend', 16)}发送</button></div></div></div>`
def({
  id: 'AD-COMM-004', name: '收件箱与阅读面板', style: '列表+阅读', wide: true,
  fit: '站内信、客户来信、审批邮件的处理页：左侧列表扫读，右侧阅读并就地回复；已读/未读、星标、归档、删除都不用跳页',
  avoid: '只需要看一条提醒的场景（用通知中心）；邮件正文含复杂排版时阅读区要换成富文本渲染',
  kw: 'email 邮件 收件箱 阅读面板 星标 已读未读 归档 回复 写邮件 站内信',
  css: K('adcomm004') + `
.adcomm004{width:1400px;max-width:100%;height:640px}
.adcomm004 .g{display:grid;grid-template-columns:400px minmax(0,1fr);height:100%}
.adcomm004 .lp{display:flex;flex-direction:column;min-height:0;min-width:0;border-right:1px solid var(--line)}
.adcomm004 .hd{display:flex;align-items:center;gap:8px;padding:16px 16px 8px}
.adcomm004 .hd h3{font-size:18px;font-weight:600;line-height:28px}
.adcomm004 .hd .cbt{height:32px}
.adcomm004 .lst{flex:1;min-height:0;overflow-y:auto;scrollbar-width:thin;scrollbar-color:var(--n8) transparent}
.adcomm004 .lst-emp{flex:1}
.adcomm004 .mr{display:flex;gap:8px;padding:12px 16px 12px 10px;cursor:pointer;position:relative;transition:background .15s}
.adcomm004 .mr+.mr{border-top:1px solid var(--line)}
.adcomm004 .mr:hover{background:var(--n2)}
.adcomm004 .mr.on{background:var(--pt)}
.adcomm004 .mr:focus-visible{outline-offset:-2px}
.adcomm004 .ud{flex:none;width:8px;height:8px;border-radius:50%;background:var(--p);margin-top:7px;visibility:hidden}
.adcomm004 .mr.un .ud{visibility:visible}
.adcomm004 .mr .bd{flex:1;min-width:0;display:flex;flex-direction:column;gap:2px}
.adcomm004 .mr .r1,.adcomm004 .mr .r3{display:flex;align-items:center;gap:6px;min-width:0}
.adcomm004 .mr .nm{flex:1;min-width:0;font-weight:400;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.adcomm004 .mr .nm em{margin-left:8px;font-size:12px;color:var(--ink3);font-weight:400}
.adcomm004 .mr.un .nm{font-weight:600}
.adcomm004 .mr .tm{font-size:12px;color:var(--ink3);flex:none}
.adcomm004 .mr .sj{white-space:nowrap;overflow:hidden;text-overflow:ellipsis;color:var(--ink2)}
.adcomm004 .mr.un .sj{color:var(--ink);font-weight:600}
.adcomm004 .mr .ls{flex:1;min-width:0;font-size:12px;color:var(--ink3);white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.adcomm004 .mr .cl{color:var(--ink3);display:inline-flex}
.adcomm004 .stb{width:24px;height:24px;border-radius:4px;display:inline-flex;align-items:center;justify-content:center;color:color-mix(in srgb,var(--ink6) 31%,var(--ink5));flex:none;transition:color .15s,background .15s}
.adcomm004 .stb:hover{background:var(--n4);color:var(--ink2)}
.adcomm004 .stb.on,.adcomm004 .stt.on{color:#B98A2E}
.adcomm004 .stt.on:hover{color:#B98A2E}
.adcomm004 .rd{display:flex;flex-direction:column;min-width:0;min-height:0}
.adcomm004 .rtb{display:flex;align-items:center;gap:2px;padding:0 12px;height:56px;border-bottom:1px solid var(--line);flex:none}
.adcomm004 .bk{display:none}
.adcomm004 .rbd{flex:1;min-height:0;overflow-y:auto;padding:24px 32px 32px;animation:adcmin .22s cubic-bezier(.2,0,0,1)}
.adcomm004 .sj2{font-size:20px;font-weight:600;line-height:28px;max-width:760px}
.adcomm004 .mh{display:flex;align-items:center;gap:12px;margin:16px 0 20px;max-width:760px}
.adcomm004 .mm{flex:1;min-width:0}
.adcomm004 .hm1{display:flex;gap:8px;align-items:baseline;flex-wrap:wrap}
.adcomm004 .hm1 b{font-weight:600}
.adcomm004 .hm1 span,.adcomm004 .hm2{font-size:12px;color:var(--ink3)}
.adcomm004 .txt{max-width:760px;display:flex;flex-direction:column;gap:12px;line-height:24px;color:color-mix(in srgb,var(--ink1) 44%,var(--ink))}
.adcomm004 .atts{display:flex;flex-wrap:wrap;gap:10px;margin-top:20px;max-width:760px}
.adcomm004 .att{display:inline-flex;gap:10px;align-items:center;padding:8px 12px;border:1px solid var(--line2);border-radius:8px;background:var(--n1);text-align:left;color:var(--ink2);transition:background .15s,border-color .15s}
.adcomm004 .att:hover{background:var(--card);border-color:var(--n9)}
.adcomm004 .att .fi{width:32px;height:32px;border-radius:8px;background:var(--pt);color:var(--p-text);display:inline-flex;align-items:center;justify-content:center;flex:none}
.adcomm004 .att .fn{display:flex;flex-direction:column;min-width:0}
.adcomm004 .att b{font-weight:600;font-size:14px;line-height:20px;color:var(--ink)}
.adcomm004 .att em{font-size:12px;line-height:18px;color:var(--ink3)}
.adcomm004 .thr{max-width:760px;margin-top:20px;display:flex;flex-direction:column;gap:14px}
.adcomm004 .th{display:flex;gap:10px;padding-top:14px;border-top:1px solid var(--line);animation:adcmin .22s cubic-bezier(.2,0,0,1)}
.adcomm004 .th p{margin-top:2px;line-height:22px}
.adcomm004 .act{display:flex;gap:10px;margin-top:24px}
.adcomm004 .rbox{max-width:760px;margin-top:14px;animation:adcmin .22s cubic-bezier(.2,0,0,1)}
.adcomm004 textarea,.adcomm004 .fi2{width:100%;border:1px solid var(--n7);border-radius:8px;padding:8px 12px;font:inherit;font-size:14px;line-height:22px;color:var(--ink);background:var(--card);outline:none;transition:border-color .15s}
.adcomm004 textarea{resize:vertical;min-height:96px}
.adcomm004 .fi2{height:36px;padding:0 12px}
.adcomm004 textarea:focus,.adcomm004 .fi2:focus{border-color:var(--ink2)}
.adcomm004 .bad{border-color:var(--danger)!important}
.adcomm004 .er{margin-top:4px;font-size:12px;color:var(--danger)}
.adcomm004 .rf{display:flex;justify-content:flex-end;gap:10px;margin-top:10px}
.adcomm004 .ix-ov .dlg.cm{width:min(520px,calc(100% - 32px))}
.adcomm004 .fld{margin-top:12px}
.adcomm004 .fld label{display:block;font-size:12px;color:var(--ink3);margin-bottom:4px}
@container (max-width:760px){.adcomm004 .g{grid-template-columns:minmax(0,1fr)}.adcomm004 .lp{border-right:0}.adcomm004 .rd{display:none}.adcomm004[data-view=read] .lp{display:none}.adcomm004[data-view=read] .rd{display:flex}.adcomm004 .bk{display:inline-flex}.adcomm004 .rbd{padding:16px}}`,
  html: () => { const ms = MAILS(); return `<div class="adcomm004" data-view="list"><div class="g"><aside class="lp"><div class="hd"><h3>收件箱</h3><span class="tot" title="未读邮件">3</span><span class="sp"></span><button class="cbt pri" type="button" data-open="cmp">${ic('edit', 16)}写邮件</button></div><div class="tb" data-ix="tabs"><button type="button" data-t="all" class="on">全部</button><button type="button" data-t="un">未读<span class="nbd">3</span></button><button type="button" data-t="star">星标<span class="nbd gy">2</span></button><i class="ink"></i></div><ul class="lst" role="listbox" aria-label="邮件列表">${ms.map((m, i) => mailRow(i === 0 ? Object.assign(m, { un: 1 }) : m)).join('')}</ul><div class="emp lst-emp" hidden>${ic('mail', 28)}<b>这个分类下没有邮件</b><span>切换到“全部”查看所有邮件</span></div></aside><section class="rd">${readMail(ms[0])}</section></div><div class="ix-ov" data-ov="cmp"><div class="ix-mask"></div><div class="dlg cm" role="dialog" aria-modal="true"><h4>写邮件</h4><div class="fld"><label for="cm4a">收件人</label><input class="fi2" id="cm4a" type="text" placeholder="输入姓名或邮箱，多个用逗号分隔" autocomplete="off"><div class="er" hidden></div></div><div class="fld"><label for="cm4b">主题</label><input class="fi2" id="cm4b" type="text" placeholder="邮件主题" autocomplete="off"><div class="er" hidden></div></div><div class="fld"><label for="cm4c">正文</label><textarea id="cm4c" rows="5" placeholder="输入邮件内容"></textarea></div><div class="df"><button class="cbt" type="button" data-close>取消</button><button class="cbt pri" type="button" data-send>${ic('cmsend', 16)}发送</button></div></div></div></div>` },
  js: (r) => {
    const root = $(r, '.adcomm004'), data = MAILS(), by = (id) => data.find((x) => x.id === id)
    const lst = $(r, '.lst'), rd = $(r, '.rd'), tot = $(r, '.tot'), emp = $(r, '.lst-emp')
    let tab = 'all', cur = null
    const rows = () => $$(lst, '.mr')
    const counts = () => {
      tot.textContent = data.filter((x) => x.un).length; tot.hidden = !data.some((x) => x.un)
      const u = $(r, '[data-t=un] .nbd'), s = $(r, '[data-t=star] .nbd'); const nu = data.filter((x) => x.un).length, ns = data.filter((x) => x.star).length
      u.textContent = nu; u.hidden = !nu; s.textContent = ns; s.hidden = !ns
    }
    const sync = (m) => {
      const it = $(lst, `[data-id=${m.id}]`); if (!it) return
      it.classList.toggle('un', !!m.un); it.dataset.un = m.un; it.dataset.star = m.star
      const b = $(it, '[data-star-btn]'); b.classList.toggle('on', !!m.star); $(b, '.ic').innerHTML = sv(m.star ? 'starf' : 'star'); b.title = m.star ? '取消星标' : '加星标'
      if (cur === m) { const t = $(rd, '.stt'); if (t) { t.classList.toggle('on', !!m.star); $(t, '.ic').innerHTML = sv(m.star ? 'starf' : 'star'); t.title = m.star ? '取消星标' : '加星标' } const u = $(rd, '[data-act=unread]'); if (u) u.title = m.un ? '标为已读' : '标为未读' }
      counts()
    }
    const apply = () => {
      let n = 0
      rows().forEach((it) => { const ok = tab === 'all' || (tab === 'un' && it.dataset.un === '1') || (tab === 'star' && it.dataset.star === '1'); it.hidden = !ok; if (ok) n++ })
      emp.hidden = n > 0
    }
    const show = (id, keep) => {
      const m = by(id); if (!m) return
      cur = m; m.un = 0; rows().forEach((x) => x.classList.toggle('on', x.dataset.id === id))
      rd.innerHTML = readMail(m); if (!keep) root.dataset.view = 'read'; sync(m)
    }
    const empty = () => { cur = null; rd.innerHTML = `<div class="emp" style="flex:1">${ic('mail', 32)}<b>选择一封邮件阅读</b><span>点击左侧列表中的邮件查看内容</span></div>` }
    const drop = (m, msg) => {
      const it = $(lst, `[data-id=${m.id}]`); const vis = rows().filter((x) => !x.hidden); const k = vis.indexOf(it); const nx = vis[k + 1] || vis[k - 1]
      data.splice(data.indexOf(m), 1); it.remove(); counts(); root.dataset.view = 'list'
      if (nx && nx !== it) show(nx.dataset.id); else empty()
      if (!rows().filter((x) => !x.hidden).length) emp.hidden = false
      T(r, msg)
    }
    lst.addEventListener('click', (e) => {
      const it = e.target.closest('.mr'); if (!it) return
      if (e.target.closest('[data-star-btn]')) { const m = by(it.dataset.id); m.star = m.star ? 0 : 1; sync(m); return }
      show(it.dataset.id)
    })
    lst.addEventListener('keydown', (e) => { if (e.key === 'Enter') { const it = e.target.closest('.mr'); if (it && !e.target.closest('button')) show(it.dataset.id) } })
    $$(r, '.tb [data-t]').forEach((b) => b.addEventListener('click', () => { tab = b.dataset.t; apply() }))
    rd.addEventListener('click', (e) => {
      const a = e.target.closest('[data-act]'), m = cur
      if (e.target.closest('.bk')) { root.dataset.view = 'list'; return }
      if (a && m) {
        const k = a.dataset.act
        if (k === 'star') { m.star = m.star ? 0 : 1; sync(m) }
        else if (k === 'unread') { m.un = m.un ? 0 : 1; sync(m); T(r, m.un ? '已标为未读' : '已标为已读') }
        else if (k === 'archive') drop(m, '已归档')
        else if (k === 'del') drop(m, '已移入已删除')
        return
      }
      const at = e.target.closest('[data-att]'); if (at) { T(r, '开始下载 ' + at.dataset.att); return }
      if (e.target.closest('[data-reply]')) { const b = $(rd, '.rbox'); b.hidden = false; $(b, 'textarea').focus(); b.scrollIntoView({ block: 'nearest', behavior: 'smooth' }); return }
      if (e.target.closest('[data-rc]')) { $(rd, '.rbox').hidden = true; return }
      if (e.target.closest('[data-rs]') && m) {
        const ta = $(rd, '.rbox textarea'), er = $(rd, '.rbox .er'), v = ta.value.trim()
        if (!v) { er.hidden = false; ta.classList.add('bad'); ta.focus(); return }
        (m.thread = m.thread || []).push(v); const th = $(rd, '.thr')
        th.insertAdjacentHTML('beforeend', `<div class="th">${av(3, 32)}<div><div class="hm1"><b>我</b><span>刚刚</span></div><p>${esc(v)}</p></div></div>`)
        ta.value = ''; ta.classList.remove('bad'); er.hidden = true; $(rd, '.rbox').hidden = true; T(r, '回复已发送')
      }
    })
    rd.addEventListener('input', (e) => { if (e.target.matches('.rbox textarea')) { e.target.classList.remove('bad'); $(rd, '.rbox .er').hidden = true } })
    /* 写邮件：缺收件人或主题时就地提示，不关闭面板 */
    const to = $(r, '#cm4a'), sj = $(r, '#cm4b'), bd = $(r, '#cm4c')
    const fail = (el, msg) => { el.classList.add('bad'); const er = el.parentNode.querySelector('.er'); er.textContent = msg; er.hidden = false; el.focus() }
    ;[to, sj].forEach((el) => el.addEventListener('input', () => { el.classList.remove('bad'); el.parentNode.querySelector('.er').hidden = true }))
    $(r, '.dlg.cm [data-send]').addEventListener('click', () => {
      if (!to.value.trim()) return fail(to, '请填写收件人')
      if (!sj.value.trim()) return fail(sj, '请填写邮件主题')
      $(r, '[data-ov=cmp]').classList.remove('show'); to.value = sj.value = bd.value = ''; T(r, '邮件已发送')
    })
    counts(); show('m1', true)
  },
})

/* ================= AD-COMM-005 通知中心页 ================= */
const NOTI = [
  { k: 'order', i: 'box', t: '订单 SO2026110400128 已支付', d: '林小满 支付了 ¥599.00，请在 24 小时内完成发货。', tm: '今天 10:24', un: 1 },
  { k: 'appr', i: 'clipboard', t: '陈晓雨 提交了「退款申请」待你审批', d: '订单 SO2026110400121 申请退款 ¥329.00，原因：尺码不合适，已超过 7 天无理由期限。', tm: '今天 09:58', un: 1, st: ['待审批', 'warn'] },
  { k: 'sys', i: 'gear', t: '系统维护通知', d: '今晚 23:00–23:30 将进行数据库维护，期间订单导出功能暂不可用，请提前安排。', tm: '今天 09:30', un: 1 },
  { k: 'order', i: 'receipt', t: '3 笔订单超过 24 小时未发货', d: '其中最早一笔下单于 11-03 08:12，建议优先处理，避免触发超时赔付。', tm: '今天 08:50', un: 1 },
  { k: 'appr', i: 'flag', t: '你提交的「双十一满减活动」已通过', d: '审批人 王子豪：同意上线，生效时间 11-10 00:00。', tm: '昨天 18:02', st: ['已通过', 'ok'] },
  { k: 'sys', i: 'shield', t: '账号安全提醒', d: '你的账号于昨天 14:31 在新设备（上海 · Chrome）登录，如非本人操作请立即修改密码。', tm: '昨天 14:31' },
  { k: 'order', i: 'truck', t: '订单 SO2026110300098 已签收', d: '客户已确认收货，订单状态更新为已完成，可申请结算。', tm: '昨天 11:20' },
  { k: 'appr', i: 'clipboard', t: '李安然 邀请你审批「11 月发票开具」', d: '共 86 张发票，合计 ¥128,640.00，请在本周五前处理。', tm: '昨天 09:15', un: 1, st: ['待审批', 'warn'] },
  { k: 'sys', i: 'cloud', t: '存储空间使用已达 85%', d: '图片与附件存储空间剩余 1.5 GB，建议清理过期素材或申请扩容。', tm: '周二 16:40', later: 1 },
  { k: 'order', i: 'receipt', t: '退款 RF20261102006 已到账', d: '¥159.00 已原路退回至客户账户。', tm: '周二 10:05', later: 1 },
  { k: 'appr', i: 'flag', t: '你提交的「新增门店权限」被驳回', d: '审批人 陈晓雨：请补充门店负责人信息后重新提交。', tm: '11-02 17:48', later: 1, st: ['已驳回', 'red'] },
  { k: 'sys', i: 'gear', t: '新版本 v2.8 已上线', d: '新增批量发货与会话快捷回复，详见更新日志。', tm: '11-01 09:00', later: 1 },
  { k: 'order', i: 'box', t: '库存预警：保温水杯仅剩 12 件', d: '已低于安全库存 20 件，建议及时补货。', tm: '10-31 15:12', later: 1 },
  { k: 'appr', i: 'clipboard', t: '周一帆 撤回了「排班调整」申请', d: '该申请已自动关闭，无需再处理。', tm: '10-30 11:26', later: 1, st: ['已撤回', ''] },
]
const KIND = { sys: '系统', order: '订单', appr: '审批' }
const notiRow = (n) => `<li class="nt k-${n.k}${n.un ? ' unread' : ''}" data-k="${n.k}"${n.later ? ' data-later="1" hidden' : ''} tabindex="0"><span class="til">${ic(n.i, 20)}</span><div class="bd"><div class="r1"><b>${esc(n.t)}</b>${n.st ? `<span class="tag ${n.st[1]}">${n.st[0]}</span>` : ''}</div><p>${esc(n.d)}</p><div class="r3"><span>${n.tm}</span><i></i><span>${KIND[n.k]}</span></div></div><div class="rt"><i class="rd" aria-label="未读"></i><button class="ib del" type="button" title="删除通知" aria-label="删除通知">${ic('trash', 16)}</button></div></li>`
def({
  id: 'AD-COMM-005', name: '通知中心页', style: '分类+已读', fit: '后台独立的消息通知页：系统、订单、审批提醒集中查看，按分类看未读数，点单条标已读、一键全部已读',
  avoid: '需要对话式沟通的场景（用会话列表）；通知量很大时要配合时间分组和后端分页，别一次全部渲染',
  kw: 'notification 通知中心 消息 全部已读 未读 红点 系统通知 订单提醒 审批 待办',
  css: K('adcomm005') + `
.adcomm005{width:680px;max-width:100%}
.adcomm005 .hd{display:flex;align-items:center;gap:10px;padding:16px 16px 6px;flex-wrap:wrap}
.adcomm005 .hd h3{font-size:18px;font-weight:600;line-height:28px}
.adcomm005 .ov{display:inline-flex;align-items:center;gap:8px;color:var(--ink2);cursor:pointer;user-select:none}
.adcomm005 .tls{display:flex;align-items:center;justify-content:space-between;gap:12px}
.adcomm005 .tb{padding-right:16px;align-items:center}
.adcomm005 .tb .tls{margin-left:auto;display:flex;align-items:center;gap:14px;padding:0}
.adcomm005 .nt{display:flex;gap:12px;padding:14px 16px;cursor:pointer;position:relative;transition:background .15s;animation:adcmin .22s cubic-bezier(.2,0,0,1)}
.adcomm005 .nt+.nt{border-top:1px solid var(--line)}
.adcomm005 .nt:hover{background:var(--n2)}
.adcomm005 .nt:focus-visible{outline-offset:-2px}
.adcomm005 .nt .til{width:36px;height:36px;border-radius:8px;display:inline-flex;align-items:center;justify-content:center;flex:none;background:var(--soft);color:var(--ink2)}
.adcomm005 .nt.k-order .til{background:var(--pt);color:var(--p-text)}
.adcomm005 .nt.k-appr .til{background:var(--warn-bg);color:var(--warn)}
.adcomm005 .nt .bd{flex:1;min-width:0}
.adcomm005 .nt .r1{display:flex;align-items:center;gap:8px;min-width:0}
.adcomm005 .nt .r1 b{min-width:0;font-weight:400;color:var(--ink2);white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.adcomm005 .nt.unread .r1 b{font-weight:600;color:var(--ink)}
.adcomm005 .nt p{margin-top:2px;color:var(--ink2);display:-webkit-box;-webkit-line-clamp:2;-webkit-box-orient:vertical;overflow:hidden}
.adcomm005 .nt:not(.unread) p{color:var(--ink3)}
.adcomm005 .nt .r3{display:flex;align-items:center;gap:6px;margin-top:4px;font-size:12px;color:var(--ink3)}
.adcomm005 .nt .r3 i{width:3px;height:3px;border-radius:50%;background:var(--n10)}
.adcomm005 .nt .rt{display:flex;flex-direction:column;align-items:center;justify-content:space-between;flex:none;width:32px}
.adcomm005 .nt .rd{width:8px;height:8px;border-radius:50%;background:var(--danger-fill);margin-top:6px;visibility:hidden}
.adcomm005 .nt.unread .rd{visibility:visible}
.adcomm005 .nt .del{opacity:0;transition:opacity .15s,background .15s,color .15s}
.adcomm005 .nt:hover .del,.adcomm005 .nt:focus-within .del{opacity:1}
.adcomm005 .nt .del:hover{color:var(--danger);background:var(--danger-bg)}
@media(hover:none){.adcomm005 .nt .del{opacity:1}}
.adcomm005 .ft{display:flex;justify-content:center;align-items:center;padding:12px 16px 16px;border-top:1px solid var(--line);color:var(--ink3);font-size:12px}
.adcomm005 .ft .cbt{height:32px}
@container (max-width:520px){.adcomm005 .tb{flex-wrap:wrap;padding-bottom:8px}.adcomm005 .tb .tls{margin-left:0;width:100%;justify-content:space-between;padding:4px 0}.adcomm005 .tb .ink{display:none}.adcomm005 .tb [data-t].on{background:var(--pt);border-radius:4px}}`,
  html: () => { const un = (k) => NOTI.filter((n) => !n.later && n.un && (!k || n.k === k)).length; const cn = (k) => (un(k) ? `<span class="nbd">${un(k)}</span>` : ''); return `<div class="adcomm005"><div class="hd"><h3>通知</h3><span class="tot" title="未读通知">${un()}</span></div><div class="tb" data-ix="tabs"><button type="button" data-t="all" class="on">全部<span class="nbd" data-cn="all">${un()}</span></button><button type="button" data-t="sys">系统${cn('sys')}</button><button type="button" data-t="order">订单${cn('order')}</button><button type="button" data-t="appr">审批${cn('appr')}</button><i class="ink"></i><div class="tls"><label class="ov"><span>仅看未读</span><i class="tgl" role="switch" aria-checked="false" tabindex="0"></i></label><button class="cbt" type="button" data-all>${ic('cmchecks', 16)}全部已读</button></div></div><ul class="lst" role="list">${NOTI.map(notiRow).join('')}</ul><div class="emp lst-emp" hidden>${ic('checkc', 32)}<b>暂无未读通知</b><span>所有提醒都已处理完毕</span></div><div class="ft"><button class="cbt" type="button" data-more>加载更多</button></div></div>` },
  js: (r) => {
    const lst = $(r, '.lst'), emp = $(r, '.lst-emp'), tot = $(r, '.tot'), tg = $(r, '.tgl'), all = $(r, '[data-all]'), ft = $(r, '.ft')
    let tab = 'all', only = false
    const rows = () => $$(lst, '.nt')
    const loaded = () => rows().filter((x) => !x.dataset.later)
    const inTab = (x) => tab === 'all' || x.dataset.k === tab
    const counts = () => {
      const u = (k) => loaded().filter((x) => x.classList.contains('unread') && (!k || x.dataset.k === k)).length
      tot.textContent = u(); tot.hidden = !u()
      $$(r, '.tb [data-t]').forEach((b) => { let c = $(b, '.nbd'); const n = u(b.dataset.t === 'all' ? '' : b.dataset.t); if (!c) { c = document.createElement('span'); c.className = 'nbd'; b.appendChild(c) } c.textContent = n; c.hidden = !n })
      const cur = loaded().filter((x) => inTab(x) && x.classList.contains('unread')).length
      all.disabled = !cur; all.title = cur ? '' : '当前分类没有未读通知'
    }
    const apply = () => {
      let n = 0
      rows().forEach((x) => { const ok = !x.dataset.later && inTab(x) && (!only || x.classList.contains('unread')); x.hidden = !ok; if (ok) n++ })
      emp.hidden = n > 0; $(emp, 'b').textContent = only ? '暂无未读通知' : '暂无通知'; emp.lastElementChild.textContent = only ? '所有提醒都已处理完毕' : '有新的提醒时会显示在这里'
    }
    const read = (x) => { if (x.classList.contains('unread')) { x.classList.remove('unread'); counts() } }
    $$(r, '.tb [data-t]').forEach((b) => b.addEventListener('click', () => { tab = b.dataset.t; apply(); counts() }))
    const flip = () => { only = !only; tg.classList.toggle('on', only); tg.setAttribute('aria-checked', only); apply() }
    $(r, '.ov').addEventListener('click', (e) => { e.preventDefault(); flip() })
    tg.addEventListener('keydown', (e) => { if (e.key === ' ' || e.key === 'Enter') { e.preventDefault(); flip() } })
    all.addEventListener('click', () => { const t = loaded().filter((x) => inTab(x) && x.classList.contains('unread')); t.forEach((x) => x.classList.remove('unread')); counts(); apply(); if (t.length) T(r, `已将 ${t.length} 条通知标为已读`) })
    lst.addEventListener('click', (e) => {
      const x = e.target.closest('.nt'); if (!x) return
      if (e.target.closest('.del')) { x.style.transition = 'opacity .2s'; x.style.opacity = '0'; setTimeout(() => { x.remove(); counts(); apply() }, 200); return }
      read(x); if (only) { /* 仅看未读时保留当前条，切换后再收起 */ }
    })
    lst.addEventListener('keydown', (e) => { if (e.key === 'Enter') { const x = e.target.closest('.nt'); if (x) read(x) } })
    $(r, '[data-more]').addEventListener('click', (e) => {
      const b = e.currentTarget; b.disabled = true; b.textContent = '加载中…'
      setTimeout(() => { if (!r.isConnected) return; $$(lst, '[data-later]').forEach((x) => { delete x.dataset.later }); apply(); counts(); ft.innerHTML = '没有更多通知了' }, 600)
    })
    counts(); apply()
  },
})

/* ================= AD-COMM-006 评论线程 ================= */
const CMT = () => [
  { id: 'c1', who: 0, name: '林小满', role: '作者', pri: 1, t: '2 小时前', ts: 120, likes: 8, text: '满减门槛先定 299 减 40，预计能把客单价拉高约 12%。大家看下有没有问题？', rs: [
    { who: 1, name: '陈晓雨', t: '1 小时前', likes: 3, text: '@林小满 门槛是不是偏低？去年 399 减 60 的转化更好。' },
    { who: 0, name: '林小满', role: '作者', pri: 1, t: '1 小时前', likes: 1, text: '去年的数据我拉一下，下午同步结论。' },
    { who: 2, name: '王子豪', role: '技术', t: '40 分钟前', likes: 2, text: '技术侧已留好阈值配置入口，调整门槛不需要发版。' },
  ] },
  { id: 'c2', who: 3, name: '李安然', role: '财务', t: '昨天 18:20', ts: 1000, likes: 5, top: 1, text: '财务提醒：满减成本要计入毛利，建议先测算爆款商品的毛利空间，避免活动做成亏本买卖。测算表我周四之前发出来。', rs: [
    { who: 0, name: '林小满', role: '作者', pri: 1, t: '昨天 18:42', likes: 1, text: '好的，辛苦！我这边先按保守口径准备方案。' },
  ] },
  { id: 'c3', who: 1, name: '赵可心', t: '昨天 11:05', ts: 1300, likes: 9, text: '优惠券叠加规则需要明确，避免用户同时使用两张。', rs: [] },
  { id: 'c4', who: 2, name: '王子豪', role: '技术', t: '11-02', ts: 3000, likes: 0, text: '上线前建议灰度 10% 的流量观察两小时，没有异常再全量。', rs: [] },
]
const cmtReply = (x, mine) => `<li class="r${mine ? ' mine' : ''}">${av(x.who, 28)}<div class="cb"><div class="ch"><b>${esc(x.name)}</b>${x.role ? `<span class="tag ${x.pri ? 'pri' : ''}">${x.role}</span>` : ''}<span class="tm">${x.t}</span></div><p class="tx">${esc(x.text).replace(/(@[^\s，。：]+)/g, '<span class="mnt">$1</span>')}</p><div class="ac"><button class="lkb" type="button" data-ix="like" aria-label="点赞"><span class="ic">${sv('cmthumb')}</span><b data-n>${x.likes}</b></button>${mine ? '<button class="rp del" type="button">删除</button>' : ''}</div></div></li>`
const cmtItem = (c, mine) => `<li class="c${mine ? ' mine' : ''}" data-id="${c.id}" data-ts="${c.ts}" data-top="${c.top ? 1 : 0}">${av(c.who, 36)}<div class="cb"><div class="ch"><b>${esc(c.name)}</b>${c.role ? `<span class="tag ${c.pri ? 'pri' : ''}">${c.role}</span>` : ''}${c.top ? '<span class="tag warn">置顶</span>' : ''}<span class="tm">${c.t}</span></div><p class="tx">${esc(c.text)}</p><div class="ac"><button class="lkb" type="button" data-ix="like" aria-label="点赞"><span class="ic">${sv('cmthumb')}</span><b data-n>${c.likes}</b></button><button class="rp" type="button" data-rp>回复</button>${mine ? '<button class="rp del" type="button">删除</button>' : ''}</div><div class="rbx"></div><ul class="rl${c.rs.length > 2 ? ' fold' : ''}">${c.rs.map((x) => cmtReply(x)).join('')}</ul><button class="mo" type="button" data-mo${c.rs.length > 2 ? '' : ' hidden'}>展开其余 ${Math.max(0, c.rs.length - 2)} 条回复</button></div></li>`
def({
  id: 'AD-COMM-006', name: '评论线程', style: '回复+点赞', fit: '审批单、工单、活动方案、商品审核下的讨论区：有楼中楼回复、点赞、最热/最新排序，保留决策过程',
  avoid: '实时沟通（用聊天窗口）；超过两层嵌套会很难读，第二层以后的回复请平铺并用 @ 指向对象',
  kw: 'comment 评论 回复 楼中楼 点赞 讨论 留言 thread 最热 最新',
  css: K('adcomm006') + `
.adcomm006{width:680px;max-width:100%}
.adcomm006 .hd{display:flex;align-items:center;gap:10px;padding:16px 20px 12px}
.adcomm006 .hd h3{font-size:18px;font-weight:600;line-height:28px}
.adcomm006 .hd h3 em{margin-left:6px;font-size:14px;color:var(--ink3);font-weight:400}
.adcomm006 .sg{display:inline-flex;background:var(--soft);border-radius:8px;padding:2px}
.adcomm006 .sg button{height:28px;padding:0 12px;border-radius:4px;font-size:14px;color:var(--ink2);transition:background .15s,color .15s}
.adcomm006 .sg button.on{background:var(--lift);color:var(--ink);font-weight:600;box-shadow:0 1px 3px var(--sh12)}
.adcomm006 .cmp{display:flex;gap:12px;padding:4px 20px 16px;border-bottom:1px solid var(--line)}
.adcomm006 .cmp .bx{flex:1;min-width:0}
.adcomm006 textarea{width:100%;display:block;border:1px solid var(--n7);border-radius:8px;padding:8px 12px;font:inherit;font-size:14px;line-height:22px;color:var(--ink);background:var(--card);outline:none;resize:none;height:60px;transition:border-color .15s}
.adcomm006 textarea::placeholder{color:var(--ink4)}
.adcomm006 textarea:focus{border-color:var(--ink2)}
.adcomm006 .fbar{display:flex;align-items:center;justify-content:flex-end;gap:12px;margin-top:8px}
.adcomm006 .fbar .cnt{font-size:12px;color:var(--ink3);font-variant-numeric:tabular-nums}
.adcomm006 .fbar .cnt.over{color:var(--danger)}
.adcomm006 .cl{padding:4px 20px 12px}
.adcomm006 .c{display:flex;gap:12px;padding:16px 0;animation:adcmin .22s cubic-bezier(.2,0,0,1)}
.adcomm006 .c+.c{border-top:1px solid var(--line)}
.adcomm006 .cb{flex:1;min-width:0}
.adcomm006 .ch{display:flex;align-items:center;gap:8px;flex-wrap:wrap;line-height:22px}
.adcomm006 .ch b{font-weight:600}
.adcomm006 .ch .tm{font-size:12px;color:var(--ink3)}
.adcomm006 .tx{margin-top:4px;line-height:22px;word-break:break-word}
.adcomm006 .tx .mnt{color:var(--p-text);font-weight:600}
.adcomm006 .ac{display:flex;align-items:center;gap:4px;margin-top:6px;margin-left:-8px}
.adcomm006 .lkb,.adcomm006 .rp{height:28px;padding:0 8px;border-radius:4px;display:inline-flex;align-items:center;gap:4px;font-size:12px;color:var(--ink3);transition:background .15s,color .15s}
.adcomm006 .lkb .ic{width:16px;height:16px}
.adcomm006 .lkb b{font-weight:400;min-width:8px;font-variant-numeric:tabular-nums}
.adcomm006 .lkb:hover,.adcomm006 .rp:hover{background:var(--soft);color:var(--ink)}
.adcomm006 .lkb.on{color:var(--p-text)}
.adcomm006 .lkb.on svg path{fill:var(--pm)}
.adcomm006 .rp.del:hover{background:var(--danger-bg);color:var(--danger)}
.adcomm006 .rl{margin-top:8px;padding:4px 14px;border-radius:8px;background:var(--n2)}
.adcomm006 .rl:empty{display:none}
.adcomm006 .r{display:flex;gap:10px;padding:10px 0;animation:adcmin .22s cubic-bezier(.2,0,0,1)}
.adcomm006 .r+.r{border-top:1px solid var(--line)}
.adcomm006 .rl.fold .r:nth-child(n+3){display:none}
.adcomm006 .mo{margin-top:8px;height:28px;padding:0 4px;font-size:14px;font-weight:600;color:var(--p-text);display:inline-flex;align-items:center;gap:4px}
.adcomm006 .mo:hover{text-decoration:underline}
.adcomm006 .rbx:empty{display:none}
.adcomm006 .rb{display:flex;gap:10px;margin-top:10px;animation:adcmin .22s cubic-bezier(.2,0,0,1)}
.adcomm006 .rb .bx{flex:1;min-width:0}
.adcomm006 .rb textarea{height:44px}
.adcomm006 .rb .fbar{margin-top:8px}
.adcomm006 .cbt.sm{height:28px;padding:0 10px}`,
  html: () => { const cs = CMT(); const n = cs.length + cs.reduce((s, c) => s + c.rs.length, 0); return `<div class="adcomm006"><div class="hd"><h3>评论<em data-cn>${n}</em></h3><span class="sp"></span><div class="sg" role="group" aria-label="排序"><button type="button" class="on" data-sort="hot">最热</button><button type="button" data-sort="new">最新</button></div></div><div class="cmp">${av(3, 36)}<div class="bx"><textarea placeholder="写下你的评论，@ 可以提到同事" aria-label="评论内容"></textarea><div class="fbar"><span class="cnt">0 / 500</span><button class="cbt pri" type="button" disabled title="请先输入评论内容">发表评论</button></div></div></div><ul class="cl">${cs.map((c) => cmtItem(c)).join('')}</ul></div>` },
  js: (r) => {
    const cl = $(r, '.cl'), ta = $(r, '.cmp textarea'), pub = $(r, '.cmp .cbt'), cnt = $(r, '.cmp .cnt'), cn = $(r, '[data-cn]')
    let mode = 'hot', seq = 0
    const total = () => { cn.textContent = $$(r, '.c').length + $$(r, '.r').length }
    const likes = (c) => +$(c, '.ac [data-n]').textContent || 0
    const order = () => {
      const cs = $$(cl, ':scope > .c').sort((a, b) => (b.dataset.top - a.dataset.top) || (mode === 'hot' ? likes(b) - likes(a) : a.dataset.ts - b.dataset.ts))
      cs.forEach((c) => cl.appendChild(c))
    }
    $$(r, '.sg [data-sort]').forEach((b) => b.addEventListener('click', () => { mode = b.dataset.sort; $$(r, '.sg button').forEach((x) => x.classList.toggle('on', x === b)); order() }))
    const lim = (el, c, btn) => { const n = el.value.length, ok = el.value.trim() && n <= 500; c.textContent = `${n} / 500`; c.classList.toggle('over', n > 500); btn.disabled = !ok; btn.title = ok ? '' : (n > 500 ? '内容超过 500 字' : '请先输入评论内容') }
    ta.addEventListener('input', () => lim(ta, cnt, pub))
    pub.addEventListener('click', () => {
      const v = ta.value.trim(); if (!v) return
      cl.insertAdjacentHTML('afterbegin', cmtItem({ id: 'n' + (++seq), who: 3, name: '我', t: '刚刚', ts: 0, likes: 0, text: v, rs: [] }, true))
      ta.value = ''; lim(ta, cnt, pub); total(); mode = 'new'; $$(r, '.sg button').forEach((x) => x.classList.toggle('on', x.dataset.sort === 'new')); order(); cl.querySelector('.c.mine').scrollIntoView({ block: 'nearest', behavior: 'smooth' })
    })
    cl.addEventListener('click', (e) => {
      const c = e.target.closest('.c'); if (!c) return
      if (e.target.closest('.del')) { const t = e.target.closest('.r') || c; t.style.transition = 'opacity .2s'; t.style.opacity = '0'; setTimeout(() => { t.remove(); total() }, 200); return }
      const mo = e.target.closest('[data-mo]')
      if (mo) { const rl = $(c, '.rl'), f = rl.classList.toggle('fold'), n = $$(rl, '.r').length - 2; mo.textContent = f ? `展开其余 ${n} 条回复` : '收起回复'; return }
      const rp = e.target.closest('[data-rp]')
      if (rp) {
        const slot = $(c, '.rbx'); const open = slot.firstElementChild; $$(cl, '.rbx').forEach((s) => { s.innerHTML = '' })
        if (open) return
        const name = $(c, '.ch b').textContent
        slot.innerHTML = `<div class="rb">${av(3, 28)}<div class="bx"><textarea placeholder="回复 @${esc(name)}" aria-label="回复内容"></textarea><div class="fbar"><span class="cnt">0 / 500</span><button class="cbt sm" type="button" data-rc>取消</button><button class="cbt pri sm" type="button" data-ok disabled title="请先输入回复内容">回复</button></div></div></div>`
        const rt = $(slot, 'textarea'), ok = $(slot, '[data-ok]'), rc = $(slot, '.cnt'); rt.focus()
        rt.addEventListener('input', () => lim(rt, rc, ok))
        return
      }
      if (e.target.closest('[data-rc]')) { $(c, '.rbx').innerHTML = ''; return }
      const ok = e.target.closest('[data-ok]')
      if (ok) {
        const rt = $(c, '.rbx textarea'), v = rt.value.trim(); if (!v) return
        const rl = $(c, '.rl'); rl.classList.remove('fold'); const mo2 = $(c, '[data-mo]'); mo2.hidden = true
        rl.insertAdjacentHTML('beforeend', cmtReply({ who: 3, name: '我', t: '刚刚', likes: 0, text: `@${$(c, '.ch b').textContent} ${v}` }, true))
        $(c, '.rbx').innerHTML = ''; total(); T(r, '回复已发布')
      }
    })
    order()
  },
})

/* ================= AD-COMM-007 系统公告条 ================= */
const ANNS = [
  { t: '双十一备战安排', d: '2026-11-04 发布 · 运营部', short: '【双十一备战】11-10 00:00 满减活动正式生效，请各门店在 11-09 24:00 前完成库存盘点与价签更换；活动期间客服排班已调整。', ps: ['满减活动将于 11 月 10 日 00:00 正式生效，持续至 11 月 12 日 24:00。', '请各门店在 11 月 9 日 24:00 前完成库存盘点与价签更换，缺货商品请在后台标记“暂不参与”。', '活动期间客服实行三班倒，排班表已更新到共享表格，如需调班请提前一天在群里说明。'] },
  { t: '11 月绩效考核表开放填写', d: '2026-11-03 发布 · 人事部', short: '11 月绩效考核表已开放填写，请于 11-15 前提交。', ps: ['本月考核表已在人事系统开放，请于 11 月 15 日 18:00 前完成自评并提交主管。', '逾期未提交的，按当月未参加考核处理。'] },
  { t: '后台新增批量发货功能', d: '2026-11-02 发布 · 产品部', short: '订单列表新增“批量发货”，一次最多处理 200 单。', ps: ['订单列表现已支持批量发货：勾选订单后点击“批量发货”，填写物流公司即可。', '单次最多处理 200 单；含缺货商品的订单会被自动跳过，并在结果里说明原因。'] },
  { t: '仓库盘点期间收货时间调整', d: '2026-11-01 发布 · 仓储部', short: '11-06 起仓库盘点，每日收货时间调整为 14:00–17:00。', ps: ['11 月 6 日至 11 月 8 日仓库盘点，期间收货时间调整为每日 14:00–17:00。', '供应商送货请提前预约，未预约的到货将顺延至盘点结束后入库。'] },
]
def({
  id: 'AD-COMM-007', name: '系统公告条', style: '滚动+可关', fit: '后台顶部的全员公告、维护通知、故障提醒：滚动单条、轮播多条、固定警示三种形态，都能就地查看详情或关闭',
  avoid: '同一页同时叠放超过两条；需要用户必须处理的事项请用待办或弹层，不要靠一条可关闭的横幅',
  kw: 'announcement 公告 通知条 跑马灯 滚动 轮播 横幅 维护 提醒 banner',
  css: K('adcomm007') + `
.adcomm007{width:680px;max-width:100%;min-height:380px;padding:16px}
.adcomm007 .bars{display:flex;flex-direction:column;gap:10px}
.adcomm007 .anb{display:flex;align-items:center;gap:10px;min-height:40px;padding:0 6px 0 12px;border-radius:8px;border:1px solid var(--line2);background:var(--card);color:var(--ink);box-sizing:border-box;overflow:hidden}
.adcomm007 .anb .bi{display:inline-flex;flex:none}
.adcomm007 .anb .x{width:28px;height:28px;margin-left:2px}
.adcomm007 .anb .lk2{flex:none;font-size:14px;font-weight:600;white-space:nowrap;display:inline-flex;align-items:center;gap:2px;padding:0 4px;height:28px;border-radius:4px}
.adcomm007 .anb .lk2:hover{text-decoration:underline}
.adcomm007 .b-info{background:var(--pt);border-color:var(--pm);color:var(--p-text)}
.adcomm007 .b-info .ib{color:var(--p-text)}.adcomm007 .b-info .ib:hover{background:rgba(var(--p-rgb),.12)}
.adcomm007 .mq{flex:1;min-width:0;overflow:hidden;white-space:nowrap;-webkit-mask-image:linear-gradient(90deg,transparent,#000 16px,#000 calc(100% - 16px),transparent);mask-image:linear-gradient(90deg,transparent,#000 16px,#000 calc(100% - 16px),transparent)}
.adcomm007 .mqt{display:inline-flex;animation:adcm7 26s linear 3s infinite}
.adcomm007 .mq:hover .mqt{animation-play-state:paused}
.adcomm007 .mqt span{padding-right:56px}
@keyframes adcm7{to{transform:translateX(-50%)}}
.adcomm007 .b-roll{padding-left:10px}
.adcomm007 .rl{position:relative;flex:1;min-width:0;height:24px}
.adcomm007 .rl li{position:absolute;inset:0;display:flex;align-items:center;opacity:0;transform:translateY(10px);transition:opacity .25s,transform .25s cubic-bezier(.2,0,0,1);pointer-events:none}
.adcomm007 .rl li.out{transform:translateY(-10px)}
.adcomm007 .rl li.on{opacity:1;transform:none;pointer-events:auto}
.adcomm007 .rl li button{max-width:100%;text-align:left;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.adcomm007 .rl li button:hover{text-decoration:underline}
.adcomm007 .b-roll .cnt{font-size:12px;color:var(--ink3);font-variant-numeric:tabular-nums;flex:none}
.adcomm007 .b-roll .ib{width:28px;height:28px}
.adcomm007 .b-warn{background:var(--warn-bg);border-color:var(--warn-line);color:var(--warn)}
.adcomm007 .b-warn .ib{color:var(--warn)}.adcomm007 .b-warn .ib:hover{background:rgba(138,90,0,.1)}
.adcomm007 .b-red{background:var(--danger-bg);border-color:#EBCFCB;color:var(--danger)}
.adcomm007 .b-red .ib{color:var(--danger)}.adcomm007 .b-red .ib:hover{background:rgba(168,67,59,.1)}
.adcomm007 .anb .tx{flex:1;min-width:0;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.adcomm007 .sk{margin-top:16px;display:grid;grid-template-columns:repeat(3,1fr);gap:12px}
.adcomm007 .sk i{height:64px;border-radius:8px;background:var(--n3)}
.adcomm007 .sk i:nth-child(n+4){height:96px;grid-column:span 3}
.adcomm007 .emp{padding:28px 16px}
.adcomm007 .dlg .dt{margin-top:2px;font-size:12px;color:var(--ink3)}
.adcomm007 .dlg .ps{display:flex;flex-direction:column;gap:8px;margin-top:12px;line-height:24px;color:var(--ink2)}
.adcomm007 .dlg .ps p{margin:0}
@container (max-width:520px){.adcomm007 .b-roll .cnt{display:none}.adcomm007 .anb .lk2{display:none}}`,
  html: () => `<div class="adcomm007"><div class="bars"><div class="anb b-info" data-bar><span class="bi">${ic('cmhorn')}</span><div class="mq"><div class="mqt"><span>${ANNS[0].short}</span><span aria-hidden="true">${ANNS[0].short}</span></div></div><button class="lk2" type="button" data-ann="0">查看详情</button><button class="ib x" type="button" data-x aria-label="关闭公告">${ic('close', 16)}</button></div><div class="anb b-roll" data-bar><span class="tag pri">公告</span><div class="rl"><ul>${ANNS.slice(1).map((a, i) => `<li class="${i === 0 ? 'on' : ''}"><button type="button" data-ann="${i + 1}">${a.short}</button></li>`).join('')}</ul></div><span class="cnt">1 / 3</span><button class="ib" type="button" data-prev aria-label="上一条">${ic('up', 16)}</button><button class="ib" type="button" data-next aria-label="下一条">${ic('down', 16)}</button><button class="ib x" type="button" data-x aria-label="关闭公告">${ic('close', 16)}</button></div><div class="anb b-warn" data-bar><span class="bi">${ic('alert')}</span><span class="tx">支付通道将于 11-06 02:00–04:00 维护，期间无法发起退款，请提前安排。</span><button class="lk2" type="button" data-toast="已打开维护计划">维护计划 ›</button><button class="ib x" type="button" data-x aria-label="关闭提醒">${ic('close', 16)}</button></div><div class="anb b-red" data-bar><span class="bi">${ic('closec')}</span><span class="tx">短信服务异常：验证码发送延迟，技术团队正在恢复，预计 30 分钟内完成。</span><button class="lk2" type="button" data-toast="已打开服务状态页">服务状态 ›</button><button class="ib x" type="button" data-x aria-label="关闭提醒">${ic('close', 16)}</button></div></div><div class="sk" aria-hidden="true"><i></i><i></i><i></i><i></i></div><div class="emp" hidden>${ic('checkc', 32)}<b>公告已全部关闭</b><button class="cbt" type="button" data-reset>重新显示</button></div><div class="ix-ov" data-ov="ann"><div class="ix-mask"></div><div class="dlg" role="dialog" aria-modal="true"><h4></h4><div class="dt"></div><div class="ps"></div><div class="df"><button class="cbt pri" type="button" data-close>知道了</button></div></div></div></div>`,
  js: (r) => {
    const bars = $$(r, '[data-bar]'), emp = $(r, '.emp'), sk = $(r, '.sk'), dlg = $(r, '.dlg'), ov = $(r, '[data-ov=ann]')
    const open = (i) => { const a = ANNS[i]; $(dlg, 'h4').textContent = a.t; $(dlg, '.dt').textContent = a.d; $(dlg, '.ps').innerHTML = a.ps.map((p) => `<p>${p}</p>`).join(''); ov.classList.add('show') }
    $$(r, '[data-ann]').forEach((b) => b.addEventListener('click', () => open(+b.dataset.ann)))
    const sync = () => { const left = bars.some((b) => !b.hidden); emp.hidden = left; sk.hidden = !left }
    $$(r, '[data-x]').forEach((x) => x.addEventListener('click', () => {
      const b = x.closest('[data-bar]'); b.style.height = b.offsetHeight + 'px'
      b.style.transition = 'height .22s cubic-bezier(.2,0,0,1),opacity .2s,margin-bottom .22s cubic-bezier(.2,0,0,1),border-width .22s'
      requestAnimationFrame(() => { b.style.height = '0'; b.style.opacity = '0'; b.style.marginBottom = '-10px'; b.style.borderWidth = '0' })
      setTimeout(() => { b.hidden = true; sync() }, 240)
    }))
    $(r, '[data-reset]').addEventListener('click', () => { bars.forEach((b) => { b.hidden = false; b.removeAttribute('style') }); sync() })
    /* 多条轮播：自动切换，鼠标停留时暂停，可手动上一条/下一条 */
    const li = $$(r, '.rl li'), cnt = $(r, '.b-roll .cnt'), roll = $(r, '.b-roll'); let k = 0, hold = false
    const go = (n) => { k = (n + li.length) % li.length; li.forEach((x, i) => { x.classList.toggle('on', i === k); x.classList.toggle('out', i === (k - 1 + li.length) % li.length) }); cnt.textContent = `${k + 1} / ${li.length}` }
    $(r, '[data-prev]').addEventListener('click', () => go(k - 1)); $(r, '[data-next]').addEventListener('click', () => go(k + 1))
    roll.addEventListener('mouseenter', () => { hold = true }); roll.addEventListener('mouseleave', () => { hold = false })
    const t = setInterval(() => { if (!r.isConnected) { clearInterval(t); return } if (!hold && !roll.hidden) go(k + 1) }, 3500)
  },
})

/* ================= AD-COMM-008 用户名片悬浮卡 ================= */
const PPL = [
  { n: '林小满', av: 0, role: '运营主管', d: '运营部', ext: '8021', em: 'xiaoman.lin@example.com', st: '在线', tone: 'ok', tags: ['大促负责人', '会员运营'], hrs: '09:00–18:00' },
  { n: '王子豪', av: 2, role: '后端工程师', d: '技术部', ext: '8136', em: 'zihao.wang@example.com', st: '忙碌', tone: 'warn', tags: ['订单系统', '今日值班'], hrs: '10:00–19:00' },
  { n: '陈晓雨', av: 1, role: '客服组长', d: '客服部', ext: '8052', em: 'xiaoyu.chen@example.com', st: '在线', tone: 'ok', tags: ['售后审批', '金卡专线'], hrs: '08:30–17:30' },
  { n: '李安然', av: 3, role: '财务专员', d: '财务部', ext: '8210', em: 'anran.li@example.com', st: '离线', tone: '', tags: ['对账', '发票'], hrs: '09:00–18:00' },
]
const cardHTML008 = (p) => `<div class="pc"><div class="top"></div><div class="id">${av(p.av, 56)}<div class="nm"><b>${p.n}</b><span class="tag ${p.tone}">${p.st}</span></div><div class="rl">${p.role} · ${p.d}</div></div><dl class="kv"><div><dt title="分机">${ic('phone', 16)}</dt><dd>${p.ext}<small>分机</small></dd><button class="ib cp" type="button" data-copy="${p.ext}" data-what="分机号" title="复制分机号" aria-label="复制分机号">${ic('copy', 16)}</button></div><div><dt title="邮箱">${ic('mail', 16)}</dt><dd>${p.em}</dd><button class="ib cp" type="button" data-copy="${p.em}" data-what="邮箱" title="复制邮箱" aria-label="复制邮箱">${ic('copy', 16)}</button></div><div><dt title="工作时间">${ic('clock', 16)}</dt><dd>${p.hrs}<small>工作时间</small></dd></div></dl><div class="tags">${p.tags.map((t) => `<span class="tag pri">${t}</span>`).join('')}</div><div class="bn"><button class="cbt pri" type="button" data-msg>${ic('chat', 16)}发消息</button><button class="ib bd" type="button" data-call title="语音通话" aria-label="语音通话">${ic('phone')}</button><button class="ib bd" type="button" data-mail title="发邮件" aria-label="发邮件">${ic('mail')}</button></div></div>`
def({
  id: 'AD-COMM-008', name: '用户名片悬浮卡', style: '悬停名片', fit: '审批单、工单、订单详情里出现人名的地方：悬停或点击看头像、部门、联系方式，并能直接发消息，不用跳到通讯录',
  avoid: '手机端没有悬停，要改成点击打开（本组件已兼容）；联系方式涉及隐私时按权限脱敏，不要默认全部展示',
  kw: 'profile-card 名片 用户卡片 悬浮卡 头像 联系人 通讯录 发消息 hovercard 部门',
  css: K('adcomm008', false) + `
.adcomm008{width:560px;max-width:100%;min-height:520px;padding:20px}
.adcomm008 .phd{display:flex;align-items:center;gap:10px}
.adcomm008 .phd h3{font-size:18px;font-weight:600;line-height:28px}
.adcomm008 .rows{margin-top:16px;display:flex;flex-direction:column}
.adcomm008 .rows>div{display:flex;gap:16px;align-items:center;min-height:48px;padding:8px 0;border-top:1px solid var(--line)}
.adcomm008 .rows dt{width:80px;flex:none;color:var(--ink3)}
.adcomm008 .rows dd{flex:1;min-width:0;display:flex;flex-wrap:wrap;gap:6px 8px;align-items:center}
.adcomm008 .who{display:inline-flex;align-items:center;gap:6px;height:32px;padding:0 10px 0 4px;border-radius:16px;background:var(--n3);font-size:14px;transition:background .15s}
.adcomm008 .who:hover,.adcomm008 .who.on{background:var(--pt);color:var(--p-text)}
.adcomm008 .who.tx{height:auto;padding:0 2px;border-radius:4px;background:none;color:var(--p-text);font-weight:600}
.adcomm008 .who.tx:hover,.adcomm008 .who.tx.on{background:var(--pt)}
.adcomm008 .note{line-height:24px}
.adcomm008 .pop{position:absolute;z-index:8;width:320px;max-width:calc(100% - 24px);background:var(--card2);border:1px solid var(--line2);border-radius:12px;box-shadow:0 12px 36px var(--sh16);overflow:hidden;animation:adcmpop .18s cubic-bezier(.2,0,0,1)}
.adcomm008 .pc .top{height:56px;background:linear-gradient(135deg,var(--pm),var(--pt))}
.adcomm008 .pc .id{display:flex;flex-direction:column;align-items:flex-start;padding:0 16px;margin-top:-28px}
.adcomm008 .pc .id .avw svg{border:3px solid var(--card);border-radius:50%;box-sizing:content-box}
.adcomm008 .pc .nm{display:flex;align-items:center;gap:8px;margin-top:8px}
.adcomm008 .pc .nm b{font-size:16px;font-weight:600;line-height:24px}
.adcomm008 .pc .rl{font-size:12px;color:var(--ink3)}
.adcomm008 .pc .kv{padding:10px 16px 4px;display:flex;flex-direction:column;gap:2px}
.adcomm008 .pc .kv>div{display:flex;align-items:center;gap:6px;min-height:32px}
.adcomm008 .pc .kv dt{display:inline-flex;align-items:center;width:20px;flex:none;color:var(--ink3)}
.adcomm008 .pc .kv dd{flex:1;min-width:0;word-break:break-all;font-size:14px}
.adcomm008 .pc .kv dd small{margin-left:6px;font-size:12px;color:var(--ink3)}
.adcomm008 .pc .kv .cp{width:28px;height:28px}
.adcomm008 .pc .tags{display:flex;flex-wrap:wrap;gap:6px;padding:6px 16px 0}
.adcomm008 .pc .bn{display:flex;gap:8px;padding:14px 16px 16px}
.adcomm008 .pc .bn .cbt{flex:1;height:36px}
.adcomm008 .pc .bn .bd{width:36px;height:36px;border:1px solid var(--n7)}`,
  html: () => `<div class="adcomm008"><div class="phd"><h3>退款申请 RF20261104008</h3><span class="tag warn">待审批</span></div><dl class="rows"><div><dt>发起人</dt><dd><button class="who" type="button" data-i="0" aria-haspopup="dialog">${critter(0, 24)}林小满</button></dd></div><div><dt>当前审批人</dt><dd><button class="who" type="button" data-i="1" aria-haspopup="dialog">${critter(2, 24)}王子豪</button><button class="who" type="button" data-i="2" aria-haspopup="dialog">${critter(1, 24)}陈晓雨</button></dd></div><div><dt>抄送</dt><dd><button class="who" type="button" data-i="3" aria-haspopup="dialog">${critter(3, 24)}李安然</button></dd></div><div><dt>审批备注</dt><dd class="note">客户为金卡会员且商品未拆封，建议特批；请 <button class="who tx" type="button" data-i="2" aria-haspopup="dialog">@陈晓雨</button> 补充沟通记录后再提交。</dd></div></dl><div class="pop" hidden></div></div>`,
  js: (r) => {
    const root = $(r, '.adcomm008'), pop = $(r, '.pop'); let cur = null, tOpen, tClose
    const hide = () => { clearTimeout(tOpen); clearTimeout(tClose); pop.hidden = true; if (cur) cur.classList.remove('on'); cur = null }
    const show = (b) => {
      if (cur === b && !pop.hidden) return
      if (cur) cur.classList.remove('on')
      cur = b; b.classList.add('on'); pop.innerHTML = cardHTML008(PPL[+b.dataset.i]); pop.hidden = false
      /* 位置：优先放在名字右侧（不遮住左边的字段），放不下依次试下方、左侧，并把卡片限制在块内 */
      const rb = root.getBoundingClientRect(), bb = b.getBoundingClientRect(), pw = pop.offsetWidth, ph = pop.offsetHeight
      const bl = bb.left - rb.left, bt = bb.top - rb.top, bBottom = bb.bottom - rb.top, br = bb.right - rb.left
      const sideTop = Math.max(12, Math.min(bt - 8, rb.height - ph - 12)); let left, top
      if (br + 8 + pw <= rb.width - 12) { left = br + 8; top = sideTop }
      else if (bBottom + 8 + ph <= rb.height - 8) { left = Math.max(12, Math.min(bl, rb.width - pw - 12)); top = bBottom + 8 }
      else if (bl - 8 - pw >= 12) { left = bl - 8 - pw; top = sideTop }
      else { left = Math.max(12, Math.min(bl, rb.width - pw - 12)); top = Math.max(12, rb.height - ph - 12) }
      pop.style.left = left + 'px'; pop.style.top = Math.max(12, top) + 'px'
    }
    $$(r, '.who').forEach((b) => {
      b.addEventListener('mouseenter', () => { clearTimeout(tClose); clearTimeout(tOpen); tOpen = setTimeout(() => show(b), 150) })
      b.addEventListener('mouseleave', () => { clearTimeout(tOpen); tClose = setTimeout(hide, 250) })
      b.addEventListener('click', (e) => { e.stopPropagation(); if (cur === b && !pop.hidden) hide(); else show(b) })
    })
    pop.addEventListener('mouseenter', () => clearTimeout(tClose)); pop.addEventListener('mouseleave', () => { tClose = setTimeout(hide, 250) })
    pop.addEventListener('click', (e) => {
      e.stopPropagation(); const p = PPL[+cur.dataset.i]
      const cp = e.target.closest('[data-copy]')
      if (cp) { try { navigator.clipboard && navigator.clipboard.writeText(cp.dataset.copy) } catch (x) { /* 忽略 */ } T(r, '已复制' + cp.dataset.what); return }
      if (e.target.closest('[data-msg]')) { T(r, `已向${p.n}发起会话`); hide(); return }
      if (e.target.closest('[data-call]')) { T(r, p.st === '离线' ? `${p.n}当前离线，无法接听` : `正在呼叫${p.n}…`); return }
      if (e.target.closest('[data-mail]')) { T(r, `已打开写给${p.n}的邮件`); hide() }
    })
    outside(r, (e) => { if (!pop.hidden && !e.target.closest('.pop') && !e.target.closest('.who')) hide() })
    root.addEventListener('keydown', (e) => { if (e.key === 'Escape') hide() })
    show($(r, '.who'))
  },
})

/* ================= AD-COMM-009 提及与表情面板 ================= */
const MEN = [['林小满', 0, '运营部'], ['陈晓雨', 1, '客服部'], ['王子豪', 2, '技术部'], ['李安然', 3, '财务部'], ['周一帆', 0, '市场部'], ['赵可心', 1, '运营部']]
const EMO9 = {
  face: ['😀', '😃', '😄', '😁', '😆', '😅', '😂', '🙂', '😉', '😊', '😍', '🤔', '😎', '😴', '😭', '😡', '🥲', '😬', '🙄', '😌', '🤗', '😇', '🤝', '🙏'],
  hand: ['👍', '👎', '👌', '✌️', '🤞', '👏', '🙌', '💪', '🤙', '👋', '🫡', '🤷', '🙆', '🙅', '🙇', '🫶', '☝️', '👀', '🧠', '🫣', '✍️', '🤲', '🖐️', '🤌'],
  obj: ['🎉', '🔥', '✅', '❌', '⭐', '💡', '📌', '📎', '📦', '🚚', '💰', '🧾', '📈', '📉', '🎁', '⏰', '📞', '📧', '🛒', '🏷️', '🔔', '🔒', '❤️', '💯'],
}
const mentionHTML = (t) => esc(t).replace(new RegExp('@(' + MEN.map((m) => m[0]).join('|') + ')', 'g'), '<span class="mnt">@$1</span>')
def({
  id: 'AD-COMM-009', name: '提及与表情面板', style: '@+表情', fit: '评论框、会话输入框、审批意见框：输入 @ 弹出同事列表（可搜索、键盘选择），表情面板分类点选，插入到光标处',
  avoid: '被提及的人需要收到通知，前端只负责插入，通知要后端配合；输入很长的富文本请换编辑器',
  kw: 'mention 提及 @ emoji 表情 选择器 输入框 同事 艾特 评论框',
  css: K('adcomm009', false) + `
.adcomm009{width:560px;max-width:100%;min-height:470px;padding:16px}
.adcomm009 .hist{display:flex;flex-direction:column;gap:14px;margin-top:20px;padding-top:16px;border-top:1px solid var(--line)}
.adcomm009 .sent{display:flex;gap:10px;animation:adcmin .22s cubic-bezier(.2,0,0,1)}
.adcomm009 .sent .cb{flex:1;min-width:0}
.adcomm009 .sent .ch{display:flex;gap:8px;align-items:baseline;line-height:22px}
.adcomm009 .sent .ch b{font-weight:600}
.adcomm009 .sent .ch span{font-size:12px;color:var(--ink3)}
.adcomm009 .sent .tx{margin-top:2px;line-height:24px;word-break:break-word;white-space:pre-wrap}
.adcomm009 .mnt{display:inline-block;padding:0 6px;border-radius:4px;background:var(--pt);color:var(--p-text);font-weight:600;line-height:22px}
.adcomm009 .cmp{position:relative;border:1px solid var(--n7);border-radius:12px;background:var(--card);transition:border-color .15s}
.adcomm009 .cmp:focus-within{border-color:var(--ink2)}
.adcomm009 textarea{display:block;width:100%;height:92px;border:0;background:none;outline:none;resize:none;padding:12px 14px 4px;font:inherit;font-size:14px;line-height:24px;color:var(--ink)}
.adcomm009 textarea::placeholder{color:var(--ink4)}
.adcomm009 .tbr{display:flex;align-items:center;gap:2px;padding:4px 8px 8px}
.adcomm009 .cnt{font-size:12px;color:var(--ink3);font-variant-numeric:tabular-nums;margin-right:10px}
.adcomm009 .cnt.over{color:var(--danger)}
.adcomm009 .pp{position:absolute;left:8px;top:calc(100% + 8px);background:var(--card2);border:1px solid var(--line2);border-radius:12px;box-shadow:0 12px 32px var(--sh16);z-index:6;animation:adcmpop .16s cubic-bezier(.2,0,0,1)}
.adcomm009 .mpop{width:264px;padding:6px}
.adcomm009 .mpop .hnt{padding:4px 8px 6px;font-size:12px;color:var(--ink3)}
.adcomm009 .mpop ul{max-height:228px;overflow-y:auto;scrollbar-width:thin;scrollbar-color:var(--n8) transparent}
.adcomm009 .mpop li{display:flex;align-items:center;gap:10px;height:44px;padding:0 8px;border-radius:8px;cursor:pointer}
.adcomm009 .mpop li.on{background:var(--pt)}
.adcomm009 .mpop li b{font-weight:600}
.adcomm009 .mpop li span{margin-left:auto;font-size:12px;color:var(--ink3)}
.adcomm009 .mpop .none{padding:14px 8px;text-align:center;color:var(--ink3)}
.adcomm009 .epop{width:312px;padding:8px}
.adcomm009 .epop .tb{padding:0 4px;margin-bottom:6px}
.adcomm009 .epop .tb [data-t]{height:34px}
.adcomm009 .epop .g{display:grid;grid-template-columns:repeat(8,1fr);gap:2px;max-height:150px;overflow-y:auto}
.adcomm009 .epop .g button{height:34px;border-radius:4px;font-size:20px;line-height:34px;transition:background .12s,transform .12s cubic-bezier(.2,0,0,1)}
.adcomm009 .epop .g button:hover{background:var(--soft);transform:scale(1.12)}`,
  html: () => `<div class="adcomm009"><div class="cmp"><textarea placeholder="写点什么，输入 @ 提到同事" aria-label="消息内容"></textarea><div class="tbr"><button class="ib" type="button" data-at title="提到同事" aria-label="提到同事">${ic('cmat')}</button><button class="ib" type="button" data-emo title="表情" aria-label="表情">${ic('cmsmile')}</button><span class="sp"></span><span class="cnt">0 / 500</span><button class="cbt pri" type="button" data-send disabled title="请先输入内容">发送</button></div><div class="pp mpop" hidden></div><div class="pp epop" hidden><div class="tb" data-ix="tabs" data-g="e9"><button type="button" data-t="face" class="on">笑脸</button><button type="button" data-t="hand">手势</button><button type="button" data-t="obj">物品</button></div>${Object.keys(EMO9).map((k, i) => `<div class="g" data-p="${k}" data-g="e9"${i ? ' hidden' : ''}>${EMO9[k].map((e) => `<button type="button" data-e="${e}" aria-label="插入表情">${e}</button>`).join('')}</div>`).join('')}</div></div><div class="hist">${[[1, '陈晓雨', '09:58', '@王子豪 今晚的库存同步任务请再确认一下，大促前不能出差错 🙏'], [2, '王子豪', '10:06', '收到 👍 @李安然 对账数据同步完我通知你']].map((x) => `<div class="sent">${av(x[0], 32)}<div class="cb"><div class="ch"><b>${x[1]}</b><span>${x[2]}</span></div><p class="tx">${mentionHTML(x[3])}</p></div></div>`).join('')}</div></div>`,
  js: (r) => {
    const ta = $(r, 'textarea'), mp = $(r, '.mpop'), ep = $(r, '.epop'), snd = $(r, '[data-send]'), cnt = $(r, '.cnt'), hist = $(r, '.hist'), eb = $(r, '[data-emo]'), ab = $(r, '[data-at]')
    let act = 0, list = []
    const shut = () => { mp.hidden = true; ep.hidden = true; eb.classList.remove('on'); ab.classList.remove('on') }
    const stat = () => { const n = ta.value.length, ok = ta.value.trim() && n <= 500; cnt.textContent = n + ' / 500'; cnt.classList.toggle('over', n > 500); snd.disabled = !ok; snd.title = ok ? '发送（Ctrl + Enter）' : n > 500 ? '内容超过 500 字' : '请先输入内容' }
    const token = () => { const c = ta.selectionStart == null ? ta.value.length : ta.selectionStart; const m = /(^|[^A-Za-z0-9])@([^\s@]{0,6})$/.exec(ta.value.slice(0, c)); return m ? { q: m[2], at: c - m[2].length - 1, c } : null }
    const drawM = () => {
      mp.innerHTML = `<div class="hnt">提到同事，他会收到通知</div>` + (list.length ? `<ul>${list.map((m, i) => `<li data-i="${i}" class="${i === act ? 'on' : ''}">${critter(m[1], 28)}<b>${m[0]}</b><span>${m[2]}</span></li>`).join('')}</ul>` : '<div class="none">没有匹配的同事</div>')
    }
    const pick = (m) => { const t = token(); if (!t) return; ta.value = ta.value.slice(0, t.at) + '@' + m[0] + ' ' + ta.value.slice(t.c); const c = t.at + m[0].length + 2; ta.focus(); ta.setSelectionRange(c, c); shut(); stat() }
    ta.addEventListener('input', () => {
      stat(); const t = token()
      if (t) { list = MEN.filter((m) => !t.q || m[0].includes(t.q) || m[2].includes(t.q)); act = 0; ep.hidden = true; mp.hidden = false; ab.classList.add('on'); drawM() } else { mp.hidden = true; ab.classList.remove('on') }
    })
    ta.addEventListener('keydown', (e) => {
      if (!mp.hidden && list.length) {
        if (e.key === 'ArrowDown') { e.preventDefault(); act = (act + 1) % list.length; drawM(); return }
        if (e.key === 'ArrowUp') { e.preventDefault(); act = (act - 1 + list.length) % list.length; drawM(); return }
        if ((e.key === 'Enter' || e.key === 'Tab') && !e.isComposing) { e.preventDefault(); pick(list[act]); return }
      }
      if (e.key === 'Escape') shut()
      if (e.key === 'Enter' && (e.ctrlKey || e.metaKey) && !e.isComposing) { e.preventDefault(); send() }
    })
    mp.addEventListener('mousedown', (e) => e.preventDefault())
    mp.addEventListener('click', (e) => { const li = e.target.closest('li'); if (li) pick(list[+li.dataset.i]) })
    ab.addEventListener('click', () => { ep.hidden = true; eb.classList.remove('on'); const c = ta.selectionStart == null ? ta.value.length : ta.selectionStart; const pre = ta.value.slice(0, c); insertAt(ta, (pre && !/\s$/.test(pre) ? ' ' : '') + '@') })
    eb.addEventListener('click', () => { mp.hidden = true; ep.hidden = !ep.hidden; eb.classList.toggle('on', !ep.hidden) })
    ep.addEventListener('click', (e) => { const b = e.target.closest('[data-e]'); if (b) insertAt(ta, b.dataset.e) })
    outside(r, (e) => { if (!e.target.closest('.pp') && !e.target.closest('.tbr .ib')) shut() })
    const send = () => {
      const v = ta.value.trim(); if (!v || ta.value.length > 500) return
      hist.insertAdjacentHTML('afterbegin', `<div class="sent">${av(3, 32)}<div class="cb"><div class="ch"><b>我</b><span>刚刚</span></div><p class="tx">${mentionHTML(v)}</p></div></div>`)
      ta.value = ''; shut(); stat()
      if (/@/.test(v)) T(r, '已通知被提到的同事')
    }
    snd.addEventListener('click', send); stat()
  },
})

/* ================= AD-COMM-010 顶栏通知下拉 ================= */
const BELL = {
  notice: [{ i: 'box', t: '订单 SO2026110400128 已支付', s: '林小满 支付了 ¥599.00，请尽快发货', tm: '10:24', un: 1 }, { i: 'gear', t: '系统维护通知', s: '今晚 23:00–23:30 数据库维护，订单导出暂不可用', tm: '09:30', un: 1 }, { i: 'receipt', t: '3 笔订单超过 24 小时未发货', s: '最早一笔下单于 11-03 08:12', tm: '08:50', un: 0 }, { i: 'shield', t: '账号安全提醒', s: '你的账号在新设备登录，如非本人请修改密码', tm: '昨天', un: 0 }],
  msg: [{ a: 0, t: '林小满', s: '好的，我下午三点前把对账单发给你', tm: '10:32', un: 1 }, { a: 1, t: '陈晓雨', s: '这笔退款需要你确认一下，客户是金卡会员', tm: '09:47', un: 1 }, { a: 3, t: '李安然', s: '本月发票已全部开具完成', tm: '昨天', un: 0 }],
  todo: [{ t: '审批：陈晓雨 的退款申请', s: '订单 SO2026110400121 · ¥329.00', tag: ['今日截止', 'warn'], un: 1 }, { t: '确认 11 月供应商对账单', s: '李安然 发起 · 本周五前', tag: ['本周', 'pri'], un: 1 }, { t: '补充双十一活动预算说明', s: '运营部 · 11-06', tag: ['', ''], un: 1 }],
}
const bellRow = (k, x) => k === 'todo'
  ? `<li class="${x.un ? 'un' : ''}"><button class="ck" type="button" aria-label="标为完成" title="标为完成">${ic('check', 14)}</button><div class="bd"><b>${esc(x.t)}</b><span>${esc(x.s)}</span></div>${x.tag[0] ? `<span class="tag ${x.tag[1]}">${x.tag[0]}</span>` : ''}</li>`
  : `<li class="${x.un ? 'un' : ''}">${k === 'msg' ? av(x.a, 36) : `<span class="til">${ic(x.i, 18)}</span>`}<div class="bd"><b>${esc(x.t)}</b><span>${esc(x.s)}</span></div><div class="rt"><em>${x.tm}</em><i class="rd"></i></div></li>`
def({
  id: 'AD-COMM-010', name: '顶栏通知下拉', style: '铃铛弹层', fit: '后台顶栏的铃铛：不离开当前页就扫一眼最近的通知、消息和待办，三类分开计数，可全部已读，要细看再进通知中心',
  avoid: '弹层里只放最近 5 条左右，别当完整列表用；完整的分类、筛选和历史记录交给通知中心页',
  kw: 'bell 铃铛 顶栏 通知下拉 消息 待办 未读 角标 dropdown 通知',
  css: K('adcomm010', false) + `
.adcomm010{width:600px;max-width:100%;height:490px;overflow:hidden}
.adcomm010 .top{display:flex;align-items:center;gap:8px;height:56px;padding:0 16px;border-bottom:1px solid var(--line);background:var(--card)}
.adcomm010 .top .lg{width:28px;height:28px;border-radius:8px;background:var(--pt);color:var(--p-text);display:inline-flex;align-items:center;justify-content:center;flex:none}
.adcomm010 .top .sch{width:220px;max-width:40%}
.adcomm010 .bell .bg{position:absolute;right:-6px;top:-6px;min-width:16px;height:16px;padding:0 4px;border-radius:8px;background:var(--danger-fill);color:#fff;font-size:12px;font-weight:600;line-height:16px;text-align:center;border:2px solid var(--card);box-sizing:content-box}
.adcomm010 .sk{padding:20px 16px;display:grid;grid-template-columns:repeat(3,1fr);gap:12px}
.adcomm010 .sk i{height:80px;border-radius:8px;background:var(--n3)}
.adcomm010 .sk i:nth-child(n+4){height:160px;grid-column:span 3}
.adcomm010 .panel{position:absolute;right:12px;top:62px;width:380px;max-width:calc(100% - 24px);background:var(--card2);border:1px solid var(--line2);border-radius:12px;box-shadow:0 14px 40px var(--sh18);z-index:8;animation:adcmpop .18s cubic-bezier(.2,0,0,1)}
.adcomm010 .panel::before{content:"";position:absolute;right:58px;top:-7px;width:12px;height:12px;background:var(--card2);border-left:1px solid var(--line2);border-top:1px solid var(--line2);transform:rotate(45deg)}
.adcomm010 .panel .tb{padding:0 8px;border-radius:12px 12px 0 0;position:relative;background:var(--card2)}
.adcomm010 .pl{max-height:300px;overflow-y:auto;scrollbar-width:thin;scrollbar-color:var(--n8) transparent}
.adcomm010 .pl li{display:flex;gap:12px;align-items:center;padding:12px 16px;cursor:pointer;transition:background .15s}
.adcomm010 .pl li+li{border-top:1px solid var(--line)}
.adcomm010 .pl li:hover{background:var(--n2)}
.adcomm010 .pl .til{width:36px;height:36px;border-radius:8px;background:var(--pt);color:var(--p-text);display:inline-flex;align-items:center;justify-content:center;flex:none}
.adcomm010 .pl .bd{flex:1;min-width:0;display:flex;flex-direction:column}
.adcomm010 .pl .bd b{font-weight:400;color:var(--ink2);white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.adcomm010 .pl li.un .bd b{font-weight:600;color:var(--ink)}
.adcomm010 .pl .bd span{font-size:12px;color:var(--ink3);white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.adcomm010 .pl .rt{display:flex;flex-direction:column;align-items:flex-end;gap:6px;flex:none}
.adcomm010 .pl .rt em{font-size:12px;color:var(--ink3)}
.adcomm010 .pl .rd{width:8px;height:8px;border-radius:50%;background:var(--danger-fill);visibility:hidden}
.adcomm010 .pl li.un .rd{visibility:visible}
.adcomm010 .pl .ck{width:20px;height:20px;border-radius:50%;border:1.5px solid var(--n10);display:inline-flex;align-items:center;justify-content:center;color:transparent;flex:none;transition:background .15s,border-color .15s,color .15s}
.adcomm010 .pl .ck:hover{border-color:var(--p);color:var(--p-fg)}
.adcomm010 .pl li:not(.un) .ck{background:var(--p);border-color:var(--p);color:#fff}
.adcomm010 .pl.td li:not(.un) .bd b{text-decoration:line-through;color:var(--ink3)}
.adcomm010 .pl .emp{padding:32px 16px}
.adcomm010 .pf{display:flex;align-items:center;justify-content:space-between;height:44px;padding:0 8px;border-top:1px solid var(--line)}
.adcomm010 .pf button{height:32px;padding:0 10px;border-radius:4px;font-size:14px;font-weight:600;color:var(--p-text);display:inline-flex;align-items:center;gap:4px}
.adcomm010 .pf button:hover{background:var(--pt)}
.adcomm010 .pf button:disabled{color:var(--ink4);background:none;cursor:not-allowed}`,
  html: () => { const sum = Object.values(BELL).reduce((s, a) => s + a.filter((x) => x.un).length, 0); const cn = (k) => { const n = BELL[k].filter((x) => x.un).length; return n ? `<span class="nbd">${n}</span>` : '' }; return `<div class="adcomm010"><div class="top"><span class="lg">${ic('dashboard', 16)}</span><div class="sch">${ic('search')}<input class="in" type="search" placeholder="搜索订单、客户、商品" aria-label="全局搜索"></div><span class="sp"></span><button class="ib bell on" type="button" data-bell aria-label="通知" aria-expanded="true">${ic('bell', 20)}<span class="bg">${sum}</span></button>${av(3, 32)}</div><div class="sk" aria-hidden="true"><i></i><i></i><i></i><i></i></div><div class="panel" role="dialog" aria-label="通知"><div class="tb" data-ix="tabs"><button type="button" data-t="notice" class="on">通知${cn('notice')}</button><button type="button" data-t="msg">消息${cn('msg')}</button><button type="button" data-t="todo">待办${cn('todo')}</button><i class="ink"></i></div>${Object.keys(BELL).map((k, i) => `<div class="pl${k === 'todo' ? ' td' : ''}" data-p="${k}"${i ? ' hidden' : ''}><ul>${BELL[k].map((x) => bellRow(k, x)).join('')}</ul></div>`).join('')}<div class="pf"><button type="button" data-allread>${ic('cmchecks', 16)}全部已读</button><button type="button" data-toast="已进入通知中心">进入通知中心 ${ic('right', 14)}</button></div></div></div>` },
  js: (r) => {
    const bell = $(r, '[data-bell]'), bg = $(r, '.bell .bg'), panel = $(r, '.panel'), allr = $(r, '[data-allread]'); let tab = 'notice'
    $$(r, '.tb [data-t]').forEach((b) => b.addEventListener('click', () => { tab = b.dataset.t; counts() }))
    const lis = (k) => $$(r, `[data-p=${k}] li`)
    const counts = () => {
      let sum = 0
      $$(r, '.tb [data-t]').forEach((b) => { const n = lis(b.dataset.t).filter((x) => x.classList.contains('un')).length; sum += n; let c = $(b, '.nbd'); if (!c) { c = document.createElement('span'); c.className = 'nbd'; b.appendChild(c) } c.textContent = n; c.hidden = !n })
      bg.textContent = sum; bg.hidden = !sum
      const cur = lis(tab).filter((x) => x.classList.contains('un')).length
      allr.disabled = !cur; allr.title = cur ? '' : '当前分类没有未读项'
      allr.lastChild.textContent = tab === 'todo' ? '全部完成' : '全部已读'
      $$(r, '.pl').forEach((p) => { let e = $(p, '.emp'); const ul = $(p, 'ul'); const all = $$(ul, 'li').length === 0; if (all && !e) { p.insertAdjacentHTML('beforeend', `<div class="emp">${ic('checkc', 28)}<b>暂无内容</b></div>`) } })
    }
    $$(r, '.pl').forEach((p) => p.addEventListener('click', (e) => {
      const li = e.target.closest('li'); if (!li) return
      if (p.dataset.p === 'todo') { if (e.target.closest('.ck')) { li.classList.toggle('un'); counts() } return }
      li.classList.remove('un'); counts()
    }))
    allr.addEventListener('click', () => { const t = lis(tab).filter((x) => x.classList.contains('un')); t.forEach((x) => x.classList.remove('un')); counts(); T(r, tab === 'todo' ? `已完成 ${t.length} 项待办` : `已将 ${t.length} 条标为已读`) })
    const setOpen = (o) => { panel.hidden = !o; bell.classList.toggle('on', o); bell.setAttribute('aria-expanded', o) }
    bell.addEventListener('click', () => setOpen(panel.hidden))
    outside(r, (e) => { if (!panel.hidden && !e.target.closest('.panel') && !e.target.closest('[data-bell]')) setOpen(false) })
    r.addEventListener('keydown', (e) => { if (e.key === 'Escape') setOpen(false) })
    counts()
  },
})

guide('ad', 'COMM', [
  ['在后台里快速切换、查找会话，一眼看出谁有新消息', '会话列表', '未读红点、@我标记、置顶与免打扰、搜索过滤都在一列里，宽度 400 左右最舒服'],
  ['一对一沟通：同事私聊、订单咨询', '单聊窗口', '时间分隔、已读状态、对方输入中提示，发送后自动滚到底，重要操作（清空记录）用居中面板确认'],
  ['客服、运营每天处理大量咨询', '客服会话工作台', '会话、聊天、客户资料三栏联动，快捷回复减少重复打字；窄屏自动收成单栏'],
  ['处理站内信、客户来信、审批邮件', '收件箱与阅读面板', '左边扫读列表，右边阅读并就地回复，已读/未读、星标、归档、删除都不用跳页'],
  ['集中查看系统、订单、审批提醒', '通知中心页', '分类标签带未读数，一键全部已读，点单条标已读；顶栏只放入口，详情都进这里'],
  ['不离开当前页，扫一眼最近的提醒和待办', '顶栏通知下拉', '铃铛弹层分通知、消息、待办三类计数，要细看再进通知中心页'],
  ['单据、方案、工单下的讨论，需要楼中楼回复', '评论线程', '回复展开、点赞、最热/最新排序，保留决策过程；全员提醒用系统公告条，输入框里要 @ 同事用提及与表情面板'],
])
/*__END__*/
})();
