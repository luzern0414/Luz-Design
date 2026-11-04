/* ===== 后台 · 表单与输入（AD-FORM-001…）、基础控件（AD-CTRL-001…）=====
 * 整个文件包在一个函数里，函数名不会和别的组件文件重名。
 * 共用样式由 K(类名) 生成，每个组件的 css 里都带完整一份，复制编号取用时不依赖别的组件。 */
;(() => {
const Q = (r, s) => r.querySelector(s)
const QA = (r, s) => [...r.querySelectorAll(s)]
const wait = (ms) => new Promise((r) => setTimeout(r, ms))
let UID = 0
const uid = (p) => `${p}-${++UID}`
const ic = (n, s) => `<i class="ic"${s ? ` style="width:${s}px;height:${s}px"` : ''}>${sv(n)}</i>`
Object.assign(LINE, {
  adf_store: '<path d="M4 9.5 5.5 4h13L20 9.5M4 9.5a2.7 2.7 0 0 0 5.3 0 2.7 2.7 0 0 0 5.4 0 2.7 2.7 0 0 0 5.3 0M5.5 12.5V20h13v-7.5M10 20v-4.5h4V20"/>',
  adf_ll: '<path d="m11 6-6 6 6 6M18 6l-6 6 6 6"/>', adf_rr: '<path d="m13 6 6 6-6 6M6 6l6 6-6 6"/>',
  adf_undo: '<path d="M9 7 4.500 11.500 9 16M5 11.500h9.500a5 5 0 0 1 0 10H11"/>',
})
/* 今天固定为 2026-11-04（和示例数据一致，截图不随日期变） */
const TODAY = '2026-11-04'
const pad = (n) => String(n).padStart(2, '0')
const ymd = (d) => `${d.getFullYear()}-${pad(d.getMonth() + 1)}-${pad(d.getDate())}`
const parseD = (s) => { const m = /^(\d{4})-(\d{2})-(\d{2})$/.exec(s || ''); if (!m) return null; const d = new Date(+m[1], +m[2] - 1, +m[3]); return ymd(d) === s ? d : null }
const addDays = (s, n) => { const d = parseD(s); d.setDate(d.getDate() + n); return ymd(d) }

/* 轻提示：落在块内顶部居中，2.4 秒消失 */
const tst = (B, msg, tone) => {
  QA(B, ':scope > .tst').forEach((x) => x.remove())
  const t = document.createElement('div'); t.className = 'tst' + (tone ? ' ' + tone : ''); t.setAttribute('role', 'status')
  t.innerHTML = `<span class="ti">${sv(tone === 'bad' ? 'alert' : 'checkc')}</span>${msg}`
  B.appendChild(t); setTimeout(() => t.remove(), 2400)
}
/* 单选/多选/开关的 aria-checked 跟着 .on 走 */
const a11y = (root) => root.addEventListener('click', () => setTimeout(() => QA(root, '[role=checkbox],[role=radio],[role=switch]').forEach((e) => e.setAttribute('aria-checked', e.classList.contains('part') ? 'mixed' : e.classList.contains('on') ? 'true' : 'false')), 0))
const H = (fn) => (root) => { a11y(root); root.addEventListener('click', (e) => { if (e.target.closest('.dis,[aria-disabled=true]')) e.stopPropagation() }, true); const B = root.firstElementChild; if (fn) fn(root, B) }

/* 校验：失焦时校验，出错后每次输入都重新校验；提交时汇总。字段包装 [data-f="键"]，错误写在 .er */
const mkV = (B, rules, o = {}) => {
  const run = (f) => {
    const inp = Q(f, '.in'); if (!inp) return ''
    const v = inp.value.trim(), fn = rules[f.dataset.f], m = fn ? fn(v, B, f) || '' : ''
    f.classList.toggle('bad', !!m); f.classList.toggle('good', !m && v !== '' && !!o.good)
    const er = Q(f, '.er'); if (er) er.textContent = m
    return m
  }
  B.addEventListener('focusout', (e) => { const f = e.target.closest && e.target.closest('[data-f]'); if (f && e.target.matches('.in')) { run(f); o.onChange && o.onChange() } })
  B.addEventListener('input', (e) => { const f = e.target.closest && e.target.closest('[data-f]'); if (f && (f.classList.contains('bad') || o.live)) { run(f); o.onChange && o.onChange() } })
  return { run, all: () => QA(B, '[data-f]').map((f) => ({ f, m: run(f) })).filter((x) => x.m) }
}
/* 字段：标签永远可见，必填星号，错误位置固定在字段下方 */
const fld = (key, label, inner, o = {}) => {
  const fn = typeof inner === 'function', id = uid('f')
  return `<div class="f${o.cls ? ' ' + o.cls : ''}"${key ? ` data-f="${key}"` : ''}><${fn ? `label class="lb" for="${id}"` : 'div class="lb"'}>${o.req ? '<i class="rq">*</i>' : ''}${label}</${fn ? 'label' : 'div'}><div class="ctl">${fn ? inner(id) : inner}<span class="er" role="alert"></span></div></div>`
}
const inp = (id, v = '', ph = '', extra = '') => `<input class="in" id="${id}" value="${v}" placeholder="${ph}" ${extra}>`
const ddHTML = (opts, cur, extra = '') => `<div class="dd" data-ix="dd"><button type="button" class="in sel" data-tg aria-haspopup="listbox" ${extra}><span data-label>${cur}</span>${ic('down')}</button><div class="menu" role="listbox">${opts.map((x) => `<div class="op${x === cur ? ' on' : ''}" data-o role="option">${x}</div>`).join('')}</div></div>`
const swHTML = (on, label, extra = '', txt = true) => `<span class="swr"><button type="button" class="tgl${on ? ' on' : ''}" role="switch" aria-checked="${!!on}" aria-label="${label}" ${extra}><i></i></button>${txt ? '<span class="swt"></span>' : ''}</span>`

/* 共用样式。prefix = 块的类名，bare = true 则根元素不画卡片 */
const K = (c, o = {}) => {
  const q = '.' + c, bare = o.bare
  const id = c.replace(/^ad([a-z]+)(\d{3})$/, (m, a, b) => `AD-${a.toUpperCase()}-${b}`)
  return `
.ixr[data-id="${id}"]{width:100%}
${q}{--bd:var(--n7);--bd2:var(--n10);--bd0:var(--n6);--okb:var(--ok-bg);--wn:var(--warn);--wnb:var(--warn-bg);--dg:var(--danger);--dgb:var(--danger-bg);--mu:var(--neutral);--mub:var(--neutral-bg);--sh1:0 1px 2px var(--sh05);--sh3:0 8px 24px var(--sh12),0 2px 6px var(--sh06);position:relative;width:100%;${o.w ? `max-width:${o.w}px;margin:0 auto;` : ''}font-size:14px;line-height:22px;color:var(--ink)${bare ? '' : ';background:var(--card);border:1px solid var(--bd0);border-radius:12px;box-shadow:var(--sh1)'}}
${q} *{box-sizing:border-box}
${q} .ic{display:inline-flex;width:16px;height:16px;flex:none}
${q} .ic svg{display:block}
${q} .mut{font-size:12px;line-height:18px;color:var(--ink3)}
${q} .f{display:block;margin-bottom:6px}
${q} .lb{display:block;margin-bottom:6px;font-size:14px;line-height:22px;color:var(--ink)}
${q} .rq{color:var(--dg);margin-right:4px;font-style:normal}
${q} .er{display:flex;align-items:flex-start;gap:4px;min-height:18px;margin-top:2px;font-size:12px;line-height:18px;color:var(--dg)}
${q} .er:empty{visibility:hidden}
${q} .in{display:block;width:100%;height:32px;padding:0 12px;border:1px solid var(--bd);border-radius:8px;background:var(--card);font:inherit;font-size:14px;line-height:30px;color:var(--ink);outline:0;transition:border-color .15s}
${q} .in::placeholder{color:var(--ink3)}
${q} .in:hover{border-color:var(--bd2)}
${q} .in:focus{border-color:var(--ink2)}
${q} .in:disabled,${q} .in.dis{background:var(--mub);border-color:var(--bd0);color:var(--ink3);cursor:not-allowed}
${q} .in.ta{height:auto;min-height:72px;padding:5px 12px;line-height:22px;resize:vertical}
${q} .f.bad .in,${q} .f.bad .in:hover,${q} .f.bad .in:focus,${q} .f.bad .ig,${q} .f.bad .ig:focus-within{border-color:var(--dg)}
${q} .ig{display:flex;align-items:center;height:32px;border:1px solid var(--bd);border-radius:8px;background:var(--card);overflow:hidden;transition:border-color .15s}
${q} .ig:hover{border-color:var(--bd2)}
${q} .ig:focus-within{border-color:var(--ink2)}
${q} .ig .in{border:0;border-radius:0;height:30px;background:none;flex:1;min-width:0}
${q} .ig .ad{display:flex;align-items:center;align-self:stretch;padding:0 10px;background:var(--n2);color:var(--ink2);white-space:nowrap}
${q} .ig .ad:first-child{border-right:1px solid var(--bd)}
${q} .ig .ad:last-child{border-left:1px solid var(--bd)}
${q} .ig .sx{padding:0 10px;color:var(--ink3);white-space:nowrap}
${q} .ig .pf{display:inline-flex;width:16px;height:16px;margin-left:10px;color:var(--ink3);flex:none}
${q} .ib{display:inline-flex;align-items:center;justify-content:center;width:24px;height:24px;margin-right:3px;border-radius:4px;color:var(--ink3);flex:none;position:relative}
${q} .ib:hover{background:var(--mub);color:var(--ink)}
${q} .ib:focus{outline:0}
${q} .ib:focus-visible,${q} .tgl:focus-visible,${q} .bt:focus-visible,${q} .cb:focus-visible,${q} .rd:focus-visible,${q} .lnk:focus-visible{outline:2px solid var(--ink2);outline-offset:2px}
${q} .dd{position:relative}
${q} .sel{display:flex;align-items:center;justify-content:space-between;gap:8px;padding:0 8px 0 12px;text-align:left;cursor:pointer}
${q} .sel [data-label]{overflow:hidden;text-overflow:ellipsis;white-space:nowrap}
${q} .sel .ic{color:var(--ink3);transition:transform .2s cubic-bezier(.2,0,0,1)}
${q} .dd.open .sel .ic{transform:rotate(180deg)}
${q} .dd.open .sel{border-color:var(--ink2)}
${q} .menu{background:var(--card2);border:1px solid var(--bd0);border-radius:8px;padding:4px;box-shadow:var(--sh3);max-height:236px;overflow:auto}
${q} .op{display:flex;align-items:center;justify-content:space-between;gap:8px;min-height:32px;padding:5px 10px;border-radius:4px;cursor:pointer}
${q} .op:hover{background:var(--mub)}
${q} .op.on{background:var(--pt);color:var(--p-text);font-weight:600}
${q} .bt{position:relative;display:inline-flex;align-items:center;justify-content:center;gap:6px;height:32px;padding:0 16px;border:1px solid transparent;border-radius:8px;font-size:14px;font-weight:600;line-height:1;white-space:nowrap;cursor:pointer;transition:background-color .15s,border-color .15s,box-shadow .15s,transform .15s cubic-bezier(.2,0,0,1)}
${q} .bt:active{transform:translateY(1px)}
${q} .bt:focus:not(:focus-visible){outline:0}
${q} .bt-p{background:var(--p);color:#fff}
${q} .bt-p:hover{box-shadow:inset 0 0 0 99px rgba(255,255,255,.12)}
${q} .bt-p:active{background:var(--pd);box-shadow:none}
${q} .bt-s{background:var(--card);border-color:var(--bd);color:var(--ink)}
${q} .bt-s:hover{border-color:var(--bd2);background:var(--n1)}
${q} .bt-s:active{background:var(--mub)}
${q} .bt-t{background:none;color:var(--p-text);padding:0 10px}
${q} .bt-t:hover{background:var(--pt)}
${q} .bt-t:active{background:var(--pm)}
${q} .bt-d{background:var(--danger-fill);color:#fff}
${q} .bt-d:hover{box-shadow:inset 0 0 0 99px rgba(255,255,255,.12)}
${q} .bt-d:active{background:color-mix(in srgb,var(--danger-fill) 84%,#000);box-shadow:none}
${q} .bt-dt{background:var(--card);border-color:#E2C3BF;color:var(--dg)}
${q} .bt-dt:hover{background:var(--dgb)}
${q} .bt[disabled],${q} .bt.dis{background:var(--n4);border-color:var(--line);color:color-mix(in srgb,var(--ink4) 43%,var(--ink3));cursor:not-allowed;box-shadow:none;transform:none}
${q} .bt.ld{pointer-events:none;color:transparent}
${q} .bt.ld .ic{opacity:0}
${q} .bt.ld::after{content:"";position:absolute;left:50%;top:50%;width:14px;height:14px;margin:-7px 0 0 -7px;border-radius:50%;border:2px solid rgba(255,255,255,.4);border-top-color:var(--card);animation:adspin .7s linear infinite}
${q} .bt-s.ld::after,${q} .bt-t.ld::after,${q} .bt-dt.ld::after{border-color:var(--bd);border-top-color:var(--ink2)}
${q} .bt-lg{height:40px;padding:0 20px}
${q} .cb,${q} .rd{display:inline-flex;align-items:center;gap:8px;min-height:24px;text-align:left;cursor:pointer;-webkit-user-select:none;user-select:none}
${q} .cb>i,${q} .rd>i{position:relative;width:16px;height:16px;flex:none;border:1px solid var(--bd2);background:var(--card);transition:background-color .15s,border-color .15s}
${q} .cb>i{border-radius:4px}
${q} .rd>i{border-radius:50%}
${q} .cb:hover>i,${q} .rd:hover>i{border-color:var(--ink3)}
${q} .cb.on>i,${q} .cb.part>i{background:var(--p);border-color:var(--p)}
${q} .cb.on>i::after{content:"";position:absolute;left:4.5px;top:1.500px;width:4px;height:8px;border:solid var(--card);border-width:0 2px 2px 0;transform:rotate(45deg)}
${q} .cb.part>i::after{content:"";position:absolute;left:3px;top:6.5px;width:8px;height:2px;border-radius:0;background:var(--card)}
${q} .rd.on>i{border-color:var(--p)}
${q} .rd.on>i::after{content:"";position:absolute;left:3px;top:3px;width:8px;height:8px;border-radius:50%;background:var(--p)}
${q} .cb.dis,${q} .rd.dis{color:var(--ink3);cursor:not-allowed}
${q} .cb.dis>i,${q} .rd.dis>i{background:var(--mub);border-color:var(--bd0)}
${q} .swr{display:inline-flex;align-items:center;gap:8px}
${q} .tgl{position:relative;width:36px;height:20px;flex:none;border-radius:999px;background:var(--n9);cursor:pointer;transition:background-color .2s}
${q} .tgl i{position:absolute;left:2px;top:2px;width:16px;height:16px;border-radius:50%;background:var(--card);box-shadow:0 1px 2px var(--sh28);transition:transform .2s cubic-bezier(.2,0,0,1)}
${q} .tgl.on{background:var(--p)}
${q} .tgl.on i{transform:translateX(16px)}
${q} .tgl:focus:not(:focus-visible){outline:0}
${q} .tgl.ld{pointer-events:none}
${q} .tgl.ld i::after{content:"";position:absolute;inset:3px;border-radius:50%;border:2px solid var(--n8);border-top-color:var(--ink3);animation:adspin .7s linear infinite}
${q} .tgl.on.ld i::after{border-color:var(--pm);border-top-color:var(--p)}
${q} .tgl.dis{background:var(--n6);cursor:not-allowed}
${q} .tgl.dis.on{background:var(--n10)}
${q} .swt{min-width:14px;font-size:12px;line-height:18px;color:var(--ink3)}
${q} .swt::after{content:"关"}
${q} .tgl.on~.swt::after{content:"开"}
${q} .tag{display:inline-flex;align-items:center;gap:4px;height:22px;padding:0 8px;border-radius:4px;font-size:12px;line-height:1;white-space:nowrap;background:var(--mub);color:var(--ink2)}
${q} .tag.pri{background:var(--pt);color:var(--p-text)}
${q} .tag.ok{background:var(--okb);color:var(--ok)}
${q} .tag.wn{background:var(--wnb);color:var(--wn)}
${q} .tag.dg{background:var(--dgb);color:var(--dg)}
${q} .tst{position:absolute;left:50%;top:12px;z-index:60;display:flex;align-items:center;gap:8px;max-width:calc(100% - 24px);padding:8px 16px;border-radius:8px;background:color-mix(in srgb,var(--inv) 92%,transparent);color:#fff;font-size:14px;line-height:22px;box-shadow:var(--sh3);pointer-events:none;transform:translateX(-50%);animation:adtst .2s cubic-bezier(.2,0,0,1)}
${q} .tst .ti{display:inline-flex;width:16px;height:16px;flex:none;color:#9FD0B0}
${q} .tst.bad .ti{color:#F0B3AC}
${q} .mdl{position:relative;z-index:1;margin:auto;display:flex;flex-direction:column;width:min(520px,calc(100% - 32px));max-height:calc(100% - 32px);background:var(--card);border-radius:16px;box-shadow:0 24px 56px var(--sh20),0 6px 16px var(--sh08);animation:admdl .2s cubic-bezier(.2,0,0,1)}
${q} .mdl:focus{outline:0}
${q} .mdl-h{display:flex;align-items:center;gap:8px;padding:16px 16px 12px 20px}
${q} .mdl-h h3{flex:1;margin:0;font-size:18px;line-height:26px;font-weight:600}
${q} .mdl-h .ib{width:32px;height:32px;margin:0}
${q} .mdl-b{flex:1;min-height:0;padding:4px 20px 12px;overflow:auto}
${q} .mdl-f{display:flex;justify-content:flex-end;gap:8px;padding:12px 20px 16px;border-top:1px solid var(--line)}
${q} .ix-mask{background:color-mix(in srgb,var(--scrim) 45%,transparent)}
@keyframes adspin{to{transform:rotate(360deg)}}
@keyframes admdl{from{opacity:0;transform:translateY(8px)}to{opacity:1;transform:none}}
@keyframes adtst{from{opacity:0;transform:translate(-50%,-6px)}to{opacity:1;transform:translateX(-50%)}}
`
}

/* ================= AD-FORM 表单与输入 ================= */
const STORES = ['静安旗舰店', '徐汇中心店', '浦东新区店', '杭州西湖体验店（含周末夜场）']
const rgHTML = (opts, cur, label) => `<div class="rg" data-ix="radio" role="radiogroup" aria-label="${label}">${opts.map((x) => `<button type="button" class="rd${x === cur ? ' on' : ''}" data-o role="radio" aria-checked="${x === cur}"><i></i>${x}</button>`).join('')}</div>`

/* ---------- AD-FORM-001 水平表单 ---------- */
def({
  id: 'AD-FORM-001', name: '水平表单', style: '标签居左',
  fit: '会员、商品、门店这类 5–8 个字段的新建与编辑；标签短、一行一个字段，扫读最快',
  avoid: '字段超过 10 个（改用分组卡片表单）；手机宽度下标签会转到输入框上方，不要靠标签宽度去对齐别的内容',
  kw: 'form horizontal 表单 水平 标签居左 必填 校验 字数 前缀 后缀',
  css: K('adform001', { w: 560 }) + `
.adform001 .hd{padding:16px 24px;border-bottom:1px solid var(--line);font-size:16px;font-weight:600;line-height:24px}
.adform001 .bd{padding:20px 24px 6px}
.adform001 .f{display:grid;grid-template-columns:88px minmax(0,1fr);column-gap:16px}
.adform001 .f>.lb{margin:0;padding-top:5px}
.adform001 .ctl{max-width:392px}
.adform001 .rg{display:flex;flex-wrap:wrap;align-items:center;gap:4px 20px;min-height:32px}
.adform001 .tw{position:relative}
.adform001 .tw .in{padding-bottom:24px}
.adform001 .cnt{position:absolute;right:10px;bottom:5px;font-size:12px;line-height:18px;color:var(--ink3);pointer-events:none}
.adform001 .sf{display:flex;align-items:center;min-height:32px}
.adform001 .ft{display:flex;justify-content:flex-end;gap:8px;padding:12px 24px;border-top:1px solid var(--line)}
@media(max-width:520px){.adform001 .hd,.adform001 .bd,.adform001 .ft{padding-left:16px;padding-right:16px}.adform001 .f{display:block}.adform001 .f>.lb{padding:0;margin-bottom:6px}}`,
  html: () => `<form class="adform001" novalidate>
<div class="hd">新增会员</div>
<div class="bd">
${fld('name', '会员姓名', (id) => inp(id, '林小满', '请输入姓名', 'maxlength="30" autocomplete="off"'), { req: 1 })}
${fld('phone', '手机号', (id) => `<div class="ig"><span class="ad">+86</span>${inp(id, '13800138000', '请输入 11 位手机号', 'inputmode="numeric" maxlength="11" autocomplete="off"')}</div>`, { req: 1 })}
${fld('', '所属门店', ddHTML(STORES, STORES[0]))}
${fld('', '会员等级', rgHTML(['普通', '银卡', '金卡'], '银卡', '会员等级'))}
${fld('money', '初始储值', (id) => `<div class="ig"><span class="ad">¥</span>${inp(id, '0.00', '0.00', 'inputmode="decimal" autocomplete="off"')}<span class="sx">元</span></div>`)}
${fld('', '备注', (id) => `<div class="tw"><textarea class="in ta" id="${id}" maxlength="100" placeholder="例如：偏好周末到店，对花粉过敏"></textarea><span class="cnt">0/100</span></div>`)}
${fld('', '到期提醒', `<div class="sf">${swHTML(true, '到期短信提醒', 'data-ix="toggle"')}</div>`)}
</div>
<div class="ft"><button type="button" class="bt bt-s" data-cancel>取消</button><button type="submit" class="bt bt-p">保存</button></div>
</form>`,
  js: H((root, B) => {
    const rules = {
      name: (v) => (!v ? '请输入会员姓名' : v.length > 20 ? '姓名最多 20 个字' : ''),
      phone: (v) => (!v ? '请输入手机号' : /^1[3-9]\d{9}$/.test(v) ? '' : '请输入 11 位手机号'),
      money: (v) => (v === '' || /^\d+(\.\d{1,2})?$/.test(v) ? '' : '金额需为数字，最多两位小数'),
    }
    const V = mkV(B, rules), bd = Q(B, '.bd'), init = bd.innerHTML
    B.addEventListener('input', (e) => { if (e.target.matches('textarea')) Q(B, '.cnt').textContent = `${e.target.value.length}/100` })
    B.addEventListener('focusout', (e) => { const m = e.target.closest('[data-f=money]'); if (m && e.target.matches('.in') && /^\d+(\.\d{1,2})?$/.test(e.target.value.trim())) e.target.value = (+e.target.value).toFixed(2) })
    B.addEventListener('click', (e) => { if (e.target.closest('[data-cancel]')) { bd.innerHTML = init; tst(B, '已还原为打开时的内容') } })
    B.addEventListener('submit', async (e) => {
      e.preventDefault()
      const btn = Q(B, '[type=submit]'); if (btn.classList.contains('ld')) return
      const bad = V.all()
      if (bad.length) { tst(B, `有 ${bad.length} 项需要修改`, 'bad'); Q(bad[0].f, '.in').focus(); return }
      btn.classList.add('ld'); await wait(700); btn.classList.remove('ld'); tst(B, '会员已保存')
    })
  }),
})

/* ---------- AD-FORM-002 分组卡片表单 ---------- */
const sec2 = (title, body, open = true) => `<div class="ix-ai${open ? ' open' : ''} sec"><button type="button" class="sh" data-h aria-expanded="${open}"><b>${title}</b><span class="prog mut" data-prog></span>${ic('down')}</button><div class="ix-ab"><div><div class="sg">${body}</div></div></div></div>`
def({
  id: 'AD-FORM-002', name: '分组卡片表单', style: '分节折叠',
  fit: '字段多（10–20 个）的商品、活动、门店编辑页；按主题分节，节可折叠，改了哪里一眼看到',
  avoid: '只有 5–6 个字段的小表单（分节反而啰嗦，用水平表单）；节之间有强先后顺序时改用分步表单',
  kw: 'form group section 分组 分节 卡片 折叠 未保存 商品编辑 字段多',
  css: K('adform002', { bare: true, w: 720 }) + `
.adform002 .sec{background:var(--card);border:1px solid var(--bd0);border-radius:12px;box-shadow:var(--sh1);margin-bottom:12px}
.adform002 .ix-ai:not(.open)>.ix-ab{visibility:hidden;transition:grid-template-rows .25s cubic-bezier(.2,0,0,1),visibility 0s .25s}
.adform002 .sh{display:flex;align-items:center;gap:12px;width:100%;height:52px;padding:0 20px;text-align:left}
.adform002 .sh b{font-size:16px;font-weight:600}
.adform002 .sh .prog{margin-left:auto}
.adform002 .sh .ic{color:var(--ink3);transition:transform .25s cubic-bezier(.2,0,0,1)}
.adform002 .sec:not(.open) .sh .ic{transform:rotate(-90deg)}
.adform002 .sg{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:0 24px;padding:4px 20px 12px;border-top:1px solid var(--line);padding-top:16px}
.adform002 .sg .f.w2{grid-column:1/-1}
.adform002 .rg{display:flex;flex-wrap:wrap;gap:4px 20px;min-height:32px;align-items:center}
.adform002 .sf{display:flex;align-items:center;min-height:32px}
.adform002 .act{display:flex;align-items:center;gap:8px;padding:12px 20px;background:var(--lift);border:1px solid var(--bd0);border-radius:12px;box-shadow:var(--sh1)}
.adform002 .dirty{display:inline-flex;align-items:center;gap:6px;margin-right:auto;font-size:14px;color:var(--wn)}
.adform002 .dirty::before{content:"";width:6px;height:6px;border-radius:50%;background:var(--warn-fill)}
@media(max-width:700px){.adform002 .sg{grid-template-columns:minmax(0,1fr)}.adform002 .sh{padding:0 16px}.adform002 .sg{padding-left:16px;padding-right:16px}}`,
  html: () => `<form class="adform002" novalidate><div data-ix="acc">
${sec2('基本信息', `
${fld('name', '商品名称', (id) => inp(id, '无线降噪耳机 Pro（石墨灰，赠收纳盒与替换耳塞三套）', '请输入商品名称', 'maxlength="60"'), { req: 1, cls: 'w2' })}
${fld('cat', '商品分类', ddHTML(['数码配件', '家居日用', '服饰鞋包', '食品饮料'], '数码配件'))}
${fld('brand', '品牌', (id) => inp(id, '示例品牌', '请输入品牌'))}
${fld('sku', '货号', (id) => inp(id, 'HP-2026-GR', '请输入货号'))}
${fld('', '上架状态', `<div class="sf">${swHTML(true, '上架状态', 'data-ix="toggle"')}</div>`)}`)}
${sec2('价格与库存', `
${fld('price', '售价', (id) => `<div class="ig"><span class="ad">¥</span>${inp(id, '599.00', '0.00', 'inputmode="decimal"')}</div>`, { req: 1 })}
${fld('mkt', '划线价', (id) => `<div class="ig"><span class="ad">¥</span>${inp(id, '799.00', '0.00', 'inputmode="decimal"')}</div>`)}
${fld('stock', '库存', (id) => `<div class="ig">${inp(id, '1280', '0', 'inputmode="numeric"')}<span class="sx">件</span></div>`, { req: 1 })}
${fld('limit', '每人限购', (id) => `<div class="ig">${inp(id, '2', '不限', 'inputmode="numeric"')}<span class="sx">件</span></div>`)}`)}
${sec2('配送与售后', `
${fld('', '配送方式', rgHTML(['快递', '同城配送', '到店自提'], '快递', '配送方式'))}
${fld('ship', '发货时效', ddHTML(['24 小时内', '48 小时内', '3 天内', '预售（下单后 7 天）'], '48 小时内'))}
${fld('', '7 天无理由退货', `<div class="sf">${swHTML(true, '7 天无理由退货', 'data-ix="toggle"')}</div>`)}`, false)}
</div>
<div class="act"><span class="dirty" data-dirty hidden><span data-dn>0</span> 项未保存</span><button type="button" class="bt bt-s dis" data-cancel aria-disabled="true">还原</button><button type="submit" class="bt bt-p dis" aria-disabled="true">保存</button></div>
</form>`,
  js: H((root, B) => {
    const req = (m) => (v) => (!v ? m : '')
    const num = (m, int) => (v) => (v === '' ? '' : (int ? /^\d+$/ : /^\d+(\.\d{1,2})?$/).test(v) ? '' : m)
    const rules = {
      name: req('请输入商品名称'), price: (v) => (!v ? '请输入售价' : /^\d+(\.\d{1,2})?$/.test(v) && +v > 0 ? '' : '售价需大于 0，最多两位小数'),
      mkt: num('划线价需为数字，最多两位小数'), stock: (v) => (!v ? '请输入库存' : /^\d+$/.test(v) ? '' : '库存需为不小于 0 的整数'), limit: num('限购数量需为整数', 1),
    }
    const V = mkV(B, rules), wrap = Q(B, '[data-ix=acc]')
    const valOf = (f) => {
      const i = Q(f, '.in:not(.sel)'); if (i) return i.value.trim()
      const l = Q(f, '[data-label]'); if (l) return l.textContent.trim()
      const r = Q(f, '.rd.on'); if (r) return r.textContent.trim()
      const s = Q(f, '.tgl'); return s ? String(s.classList.contains('on')) : ''
    }
    let base = new Map(QA(B, '[data-f],.f').map((f) => [f, valOf(f)]))
    const refresh = () => {
      QA(B, '.f').forEach((f) => { if (!base.has(f)) base.set(f, valOf(f)) })
      const n = [...base].filter(([f, v]) => valOf(f) !== v).length
      Q(B, '[data-dirty]').hidden = n === 0; Q(B, '[data-dn]').textContent = n
      QA(B, '[type=submit],[data-cancel]').forEach((b) => { b.classList.toggle('dis', n === 0); b.setAttribute('aria-disabled', n === 0) })
      QA(B, '.sec').forEach((s) => { const fs = QA(s, '.f'); const filled = fs.filter((f) => valOf(f) !== '').length; Q(s, '[data-prog]').textContent = `已填 ${filled}/${fs.length}` })
    }
    refresh()
    B.addEventListener('input', refresh)
    B.addEventListener('click', () => setTimeout(refresh, 0))
    let snap = wrap.innerHTML
    B.addEventListener('click', (e) => {
      const c = e.target.closest('[data-cancel]'); if (!c || c.classList.contains('dis')) return
      wrap.innerHTML = snap; base = new Map(QA(B, '.f').map((f) => [f, valOf(f)])); refresh(); tst(B, '已还原')
    })
    B.addEventListener('submit', async (e) => {
      e.preventDefault()
      const btn = Q(B, '[type=submit]'); if (btn.classList.contains('dis') || btn.classList.contains('ld')) return
      const bad = V.all()
      if (bad.length) { bad.forEach((x) => x.f.closest('.sec').classList.add('open')); tst(B, `还有 ${bad.length} 项必填内容需要处理`, 'bad'); Q(bad[0].f, '.in').focus(); return }
      btn.classList.add('ld'); await wait(700); btn.classList.remove('ld')
      QA(B, '.in:not(.sel)').forEach((i) => { if (i.tagName === 'INPUT') i.setAttribute('value', i.value) })
      snap = wrap.innerHTML; base = new Map(QA(B, '.f').map((f) => [f, valOf(f)])); refresh(); tst(B, '商品已保存')
    })
  }),
})

/* ---------- AD-FORM-003 分步表单 ---------- */
def({
  id: 'AD-FORM-003', name: '分步表单', style: '步骤条',
  fit: '有先后顺序、需要核对后提交的流程：创建优惠券、开通门店、发起审批；每步字段不超过 5 个',
  avoid: '字段少于 8 个（一页放得下就别拆步）；需要来回对照多节内容时改用分组卡片表单',
  kw: 'steps wizard 分步 步骤条 上一步 下一步 确认提交 优惠券 创建流程 stepper',
  css: K('adform003', { w: 600 }) + `
.adform003 .hd{padding:16px 24px;border-bottom:1px solid var(--line);font-size:16px;font-weight:600;line-height:24px}
.adform003 .stp{display:flex;align-items:center;padding:20px 24px 4px}
.adform003 .sp{display:flex;align-items:center;gap:8px;flex:none;color:var(--ink3)}
.adform003 .sp+.sp{flex:1}
.adform003 .sp+.sp::before{content:"";flex:1;min-width:24px;height:1px;margin-right:8px;background:var(--bd);transition:background-color .2s}
.adform003 .sp.done+.sp::before,.adform003 .sp.on::before{background:var(--p)}
.adform003 .sp .n{position:relative;display:inline-flex;align-items:center;justify-content:center;width:24px;height:24px;border-radius:50%;border:1px solid var(--bd2);font-size:12px;line-height:1;font-style:normal;background:var(--card);color:var(--ink2);flex:none}
.adform003 .sp b{font-weight:400;white-space:nowrap}
.adform003 .sp.on{color:var(--ink)}
.adform003 .sp.on b{font-weight:600}
.adform003 .sp.on .n{background:var(--p);border-color:var(--p);color:#fff}
.adform003 .sp.done{color:var(--ink);cursor:pointer}
.adform003 .sp.done .n{background:var(--pt);border-color:var(--pm);color:transparent}
.adform003 .sp.done .n::after{content:"";position:absolute;left:8px;top:4.5px;width:5px;height:9px;border:solid var(--pd);border-width:0 2px 2px 0;transform:rotate(45deg)}
.adform003 .pn{padding:20px 24px 8px;min-height:292px}
.adform003 .pn .f{max-width:420px}
.adform003 .rg{display:flex;flex-wrap:wrap;gap:4px 20px;min-height:32px;align-items:center}
.adform003 .lim{display:inline-flex;align-items:center;height:32px;border:1px solid var(--bd);border-radius:8px;overflow:hidden}
.adform003 .lim button{display:inline-flex;align-items:center;justify-content:center;width:32px;height:30px;color:var(--ink2)}
.adform003 .lim button:hover{background:var(--mub)}
.adform003 .lim button.dis{color:color-mix(in srgb,var(--ink6) 56%,var(--ink5));cursor:not-allowed;background:none}
.adform003 .lim b{min-width:40px;text-align:center;font-weight:600;font-variant-numeric:tabular-nums}
.adform003 .dl{display:grid;grid-template-columns:96px minmax(0,1fr) auto;gap:0 16px;max-width:520px;margin:0}
.adform003 .dl dt,.adform003 .dl dd,.adform003 .dl .jp{padding:10px 0;border-bottom:1px solid var(--line);margin:0}
.adform003 .dl dt{color:var(--ink3)}
.adform003 .dl dd{font-weight:600;overflow-wrap:anywhere}
.adform003 .dl .jp{color:var(--p-text);text-align:right;cursor:pointer;font-size:14px}
.adform003 .dl .jp:hover{text-decoration:underline}
.adform003 .ft{display:flex;justify-content:flex-end;gap:8px;padding:12px 24px;border-top:1px solid var(--line)}
.adform003 [data-d="-1"][disabled]{visibility:hidden}
.adform003 .rs{display:flex;flex-direction:column;align-items:center;gap:6px;padding:48px 24px 40px;text-align:center}
.adform003 .rs .ok{display:flex;align-items:center;justify-content:center;width:56px;height:56px;border-radius:50%;background:var(--okb);color:var(--ok);margin-bottom:8px}
.adform003 .rs .ok .ic{width:28px;height:28px}
.adform003 .rs h3{margin:0;font-size:18px;line-height:26px;font-weight:600}
.adform003 .rs p{margin:0;color:var(--ink2)}
.adform003 .rs .bt{margin-top:16px}
@media(max-width:520px){.adform003 .stp{padding:16px 16px 4px;overflow-x:auto}.adform003 .sp b{display:none}.adform003 .sp.on b{display:inline}.adform003 .pn,.adform003 .hd,.adform003 .ft{padding-left:16px;padding-right:16px}.adform003 .dl{grid-template-columns:80px minmax(0,1fr) auto}}`,
  html: () => `<div class="adform003"><div class="wz" data-ix="steps">
<div class="hd">创建优惠券</div>
<div class="stp"><div class="sp on"><i class="n">1</i><b>券信息</b></div><div class="sp"><i class="n">2</i><b>发放规则</b></div><div class="sp"><i class="n">3</i><b>确认提交</b></div></div>
<div class="pn" data-s>
${fld('cname', '券名称', (id) => inp(id, '新客立减券', '最多 20 个字', 'maxlength="20"'), { req: 1 })}
${fld('', '券类型', rgHTML(['满减券', '无门槛券'], '满减券', '券类型'))}
${fld('amt', '优惠金额', (id) => `<div class="ig"><span class="ad">¥</span>${inp(id, '20', '0', 'inputmode="decimal"')}</div>`, { req: 1 })}
${fld('thr', '使用门槛', (id) => `<div class="ig"><span class="ad">满</span>${inp(id, '99', '0', 'inputmode="decimal"')}<span class="sx">元可用</span></div>`)}
</div>
<div class="pn" data-s>
${fld('total', '发放总量', (id) => `<div class="ig">${inp(id, '500', '请输入数量', 'inputmode="numeric"')}<span class="sx">张</span></div>`, { req: 1 })}
${fld('', '每人限领', '<div class="lim"><button type="button" class="dis" data-dec aria-label="减少">' + ic('minus') + '</button><b data-lim>1</b><button type="button" data-inc aria-label="增加">' + ic('plus') + '</button></div>')}
${fld('days', '有效期', (id) => `<div class="ig"><span class="ad">领取后</span>${inp(id, '7', '1–365', 'inputmode="numeric"')}<span class="sx">天内有效</span></div>`, { req: 1 })}
</div>
<div class="pn" data-s><dl class="dl" data-sum></dl></div>
<div class="ft"><button type="button" class="bt bt-s" data-d="-1">上一步</button><button type="button" class="bt bt-p" data-d="1">下一步</button><button type="button" class="bt bt-p" data-submit hidden>提交审核</button></div>
</div>
<div class="rs" data-done hidden><span class="ok">${ic('check')}</span><h3>已提交审核</h3><p data-donep></p><button type="button" class="bt bt-s" data-again>再建一张</button></div></div>`,
  js: H((root, B) => {
    const wz = Q(B, '.wz'), snap = wz.innerHTML
    const V = mkV(B, {
      cname: (v) => (!v ? '请输入券名称' : ''),
      amt: (v) => (/^\d+(\.\d{1,2})?$/.test(v) && +v > 0 ? '' : '请输入大于 0 的金额'),
      thr: (v) => { if (v !== '' && !/^\d+(\.\d{1,2})?$/.test(v)) return '请输入金额'; const a = +Q(B, '[data-f=amt] .in').value; return v !== '' && +v < a ? '使用门槛不能低于优惠金额' : '' },
      total: (v) => (/^\d+$/.test(v) && +v >= 1 && +v <= 100000 ? '' : '请输入 1–100000 的整数'),
      days: (v) => (/^\d+$/.test(v) && +v >= 1 && +v <= 365 ? '' : '请输入 1–365 的整数'),
    })
    const idx = () => QA(B, '.sp').findIndex((s) => s.classList.contains('on'))
    const val = (k) => Q(B, `[data-f=${k}] .in`).value.trim()
    const sync = () => {
      const i = idx(), last = i === 2
      Q(B, '[data-d="1"]').hidden = last; Q(B, '[data-submit]').hidden = !last
      if (last) {
        const type = Q(B, '.rd.on').textContent.trim(), lim = Q(B, '[data-lim]').textContent
        const rows = [['券名称', val('cname'), 0], ['优惠内容', type === '满减券' ? `满 ${val('thr') || 0} 元减 ${val('amt')} 元` : `立减 ${val('amt')} 元`, 0], ['发放总量', `${val('total')} 张`, 1], ['每人限领', `${lim} 张`, 1], ['有效期', `领取后 ${val('days')} 天内`, 1]]
        Q(B, '[data-sum]').innerHTML = rows.map(([a, b, j]) => `<dt>${a}</dt><dd>${b}</dd><span class="jp" data-jump="${j}" role="button" tabindex="0">修改</span>`).join('')
      }
    }
    B.addEventListener('click', (e) => {
      const nx = e.target.closest('[data-d="1"]')
      if (nx) {
        const panel = QA(B, '[data-s]')[idx()], bad = QA(panel, '[data-f]').map((f) => ({ f, m: V.run(f) })).filter((x) => x.m)
        if (bad.length) { e.stopPropagation(); Q(bad[0].f, '.in').focus(); return }
      }
      const dn = e.target.closest('.sp.done')
      if (dn) { const n = idx() - QA(B, '.sp').indexOf(dn); for (let k = 0; k < n; k++) Q(B, '[data-d="-1"]').click(); return }
      const jp = e.target.closest('[data-jump]')
      if (jp) { const n = idx() - +jp.dataset.jump; for (let k = 0; k < n; k++) Q(B, '[data-d="-1"]').click(); return }
      setTimeout(sync, 0)
    }, true)
    B.addEventListener('click', (e) => {
      const lim = Q(B, '[data-lim]'), dec = Q(B, '[data-dec]'), inc = Q(B, '[data-inc]')
      if (e.target.closest('[data-dec],[data-inc]')) {
        const v = Math.max(1, Math.min(5, +lim.textContent + (e.target.closest('[data-inc]') ? 1 : -1))); lim.textContent = v
        dec.classList.toggle('dis', v <= 1); inc.classList.toggle('dis', v >= 5)
      }
    })
    B.addEventListener('click', async (e) => {
      const sb = e.target.closest('[data-submit]')
      if (sb && !sb.classList.contains('ld')) {
        sb.classList.add('ld'); await wait(800); sb.classList.remove('ld')
        Q(B, '[data-donep]').textContent = `${val('cname')}，共 ${val('total')} 张，审核通过后自动发放`
        wz.hidden = true; Q(B, '[data-done]').hidden = false
      }
      if (e.target.closest('[data-again]')) { wz.innerHTML = snap; IX.init(root); wz.hidden = false; Q(B, '[data-done]').hidden = true; sync() }
    })
    sync()
  }),
})

/* ---------- AD-FORM-004 失焦校验表单 ---------- */
def({
  id: 'AD-FORM-004', name: '失焦校验表单', style: '汇总定位',
  fit: '企业认证、注册、开户这类格式要求多的表单：失焦才校验，错误写在字段下方，提交时汇总并定位第一个错误',
  avoid: '字段很少的搜索或筛选（不需要校验）；不要在用户还没输完时就报错，也不要只在顶部写一句“请检查”',
  kw: 'validate validation 校验 失焦 汇总 错误 密码强度 邮箱 企业认证 提交',
  css: K('adform004', { w: 520 }) + `
.adform004 .hd{padding:16px 24px;border-bottom:1px solid var(--line);font-size:16px;font-weight:600;line-height:24px}
.adform004 .bd{padding:20px 24px 4px}
.adform004 .ctl{position:relative;max-width:420px}
.adform004 .f.good:not(.nog) .ctl::after{content:"";position:absolute;right:10px;top:8px;width:16px;height:16px;background:url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='none' stroke='%233F7D58' stroke-width='2.4' stroke-linecap='round' stroke-linejoin='round'%3E%3Cpath d='m4.5 12.5 5 5L19.5 7'/%3E%3C/svg%3E") center/16px no-repeat}
.adform004 .f.good:not(.nog) .in{padding-right:34px}
.adform004 .er::before{content:"";width:12px;height:12px;margin-top:3px;flex:none;background:url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='none' stroke='%23A8433B' stroke-width='2.4' stroke-linecap='round'%3E%3Ccircle cx='12' cy='12' r='9'/%3E%3Cpath d='M12 7.500v5.500M12 16.500v.5'/%3E%3C/svg%3E") center/12px no-repeat}
.adform004 .er:empty::before{display:none}
.adform004 .sumb{display:flex;gap:10px;margin:16px 24px 0;padding:12px 14px;border-radius:8px;background:var(--dgb);color:var(--dg)}
.adform004 .sumb .ic{margin-top:3px}
.adform004 .sumb b{display:block;font-weight:600}
.adform004 .sumb ul{margin:4px 0 0;padding:0;list-style:none}
.adform004 .sumb li{line-height:24px}
.adform004 .sumb button{color:var(--dg);text-align:left;text-decoration:underline;text-underline-offset:3px}
.adform004 .str{display:flex;align-items:center;gap:8px;margin-top:6px}
.adform004 .str span{display:flex;gap:3px;flex:1;max-width:200px}
.adform004 .str i{flex:1;height:4px;border-radius:999px;background:var(--bd0);transition:background-color .2s}
.adform004 .str.s1 i:nth-child(1){background:var(--danger-fill)}
.adform004 .str.s2 i:nth-child(-n+2){background:#B08A3A}
.adform004 .str.s3 i{background:var(--ok-fill)}
.adform004 .str em{font-style:normal;font-size:12px;line-height:18px;color:var(--ink3);min-width:16px}
.adform004 .ft{display:flex;justify-content:flex-end;gap:8px;padding:12px 24px;border-top:1px solid var(--line)}
@media(max-width:520px){.adform004 .hd,.adform004 .bd,.adform004 .ft{padding-left:16px;padding-right:16px}.adform004 .sumb{margin:16px 16px 0}}`,
  html: () => `<form class="adform004" novalidate>
<div class="hd">企业认证</div>
<div class="sumb" data-sum role="alert" hidden>${ic('alert')}<div><b></b><ul></ul></div></div>
<div class="bd">
${fld('company', '企业名称', (id) => inp(id, '示例家居有限公司', '请输入营业执照上的全称', 'maxlength="50" autocomplete="off"'), { req: 1 })}
${fld('code', '统一社会信用代码', (id) => inp(id, '9100000000EXAMPLE', '18 位数字或大写字母', 'maxlength="18" autocomplete="off"'), { req: 1 })}
${fld('email', '联系人邮箱', (id) => inp(id, '', '例如：chen.wei@example.com', 'type="email" autocomplete="off"'), { req: 1 })}
${fld('pwd', '登录密码', (id) => `<div class="ig">${inp(id, '', '至少 8 位，含字母和数字', 'type="password" autocomplete="new-password"')}<button type="button" class="ib" data-eye aria-label="显示密码" title="显示密码">${ic('eye')}</button></div><div class="str" data-str hidden><span><i></i><i></i><i></i></span><em></em></div>`, { req: 1, cls: 'nog' })}
${fld('pwd2', '确认密码', (id) => inp(id, '', '再输入一次密码', 'type="password" autocomplete="new-password"'), { req: 1 })}
</div>
<div class="ft"><button type="submit" class="bt bt-p">提交审核</button></div>
</form>`,
  js: H((root, B) => {
    const val = (k) => Q(B, `[data-f=${k}] .in`).value.trim()
    const rules = {
      company: (v) => (!v ? '请输入企业全称' : v.length < 4 ? '企业全称至少 4 个字' : ''),
      code: (v) => (!v ? '请输入统一社会信用代码' : /^[0-9A-Z]{18}$/.test(v) ? '' : `统一社会信用代码为 18 位，当前 ${v.length} 位，请核对`),
      email: (v) => (!v ? '请输入联系人邮箱' : /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(v) ? '' : '邮箱格式不对，例如 name@example.com'),
      pwd: (v) => (!v ? '请设置登录密码' : v.length >= 8 && /[A-Za-z]/.test(v) && /\d/.test(v) ? '' : '密码至少 8 位，需同时包含字母和数字'),
      pwd2: (v) => (!v ? '请再输入一次密码' : v === val('pwd') ? '' : '两次输入的密码不一致'),
    }
    const labelOf = (f) => Q(f, '.lb').textContent.replace('*', '').trim()
    const sum = Q(B, '[data-sum]')
    const upd = () => {
      if (sum.hidden) return
      const bads = QA(B, '.f.bad')
      if (!bads.length) { sum.hidden = true; return }
      Q(sum, 'b').textContent = `有 ${bads.length} 项需要修改`
      const html = bads.map((f) => `<li><button type="button" data-goto="${f.dataset.f}">${labelOf(f)}：${Q(f, '.er').textContent}</button></li>`).join('')
      if (Q(sum, 'ul').innerHTML !== html) Q(sum, 'ul').innerHTML = html
    }
    const V = mkV(B, rules, { good: true, onChange: upd })
    QA(B, '[data-f]').forEach((f) => { const i = Q(f, '.in'); if (i && i.value.trim()) { V.run(f); if (f.classList.contains('bad')) { f.classList.remove('bad'); Q(f, '.er').textContent = '' } } })
    B.addEventListener('input', (e) => {
      const f = e.target.closest('[data-f]'); if (!f) return
      if (f.dataset.f === 'code') { e.target.value = e.target.value.toUpperCase(); if (f.classList.contains('bad')) { V.run(f); upd() } }
      if (f.dataset.f === 'pwd') {
        const v = e.target.value, s = Q(B, '[data-str]'); s.hidden = !v
        const sc = (v.length >= 8) + (/[A-Za-z]/.test(v) && /\d/.test(v)) + (v.length >= 12 || /[^A-Za-z0-9]/.test(v))
        s.className = 'str s' + Math.max(1, sc); Q(s, 'em').textContent = ['', '弱', '中', '强'][Math.max(1, sc)]
        const p2 = Q(B, '[data-f=pwd2]'); if (p2.classList.contains('bad')) V.run(p2)
      }
    })
    B.addEventListener('click', (e) => {
      const eye = e.target.closest('[data-eye]')
      if (eye) { const i = Q(eye.closest('.ig'), '.in'), show = i.type === 'password'; i.type = show ? 'text' : 'password'; eye.innerHTML = ic(show ? 'eyeoff' : 'eye'); eye.setAttribute('aria-label', show ? '隐藏密码' : '显示密码'); eye.title = show ? '隐藏密码' : '显示密码' }
      const g = e.target.closest('[data-goto]'); if (g) Q(B, `[data-f=${g.dataset.goto}] .in`).focus()
    })
    B.addEventListener('submit', async (e) => {
      e.preventDefault()
      const btn = Q(B, '[type=submit]'); if (btn.classList.contains('ld')) return
      const bad = V.all()
      if (bad.length) { sum.hidden = false; upd(); Q(bad[0].f, '.in').focus(); return }
      sum.hidden = true; btn.classList.add('ld'); await wait(800); btn.classList.remove('ld'); tst(B, '已提交，预计 1 个工作日内审核')
    })
  }),
})

/* ---------- AD-FORM-005 动态增减行 ---------- */
const specRow = (n = '', p = '', s = '') => `<div class="rw" data-row><div class="ri">
<div class="f c" data-f="spec" data-l="规格名称"><input class="in" aria-label="规格名称" value="${n}" placeholder="例如：标准款" maxlength="30"><span class="er" role="alert"></span></div>
<div class="f c" data-f="price" data-l="售价"><div class="ig"><span class="ad">¥</span><input class="in" aria-label="售价" value="${p}" placeholder="0.00" inputmode="decimal"></div><span class="er" role="alert"></span></div>
<div class="f c" data-f="stock" data-l="库存"><div class="ig"><input class="in" aria-label="库存" value="${s}" placeholder="0" inputmode="numeric"><span class="sx">件</span></div><span class="er" role="alert"></span></div>
<button type="button" class="ib del" data-del aria-label="删除规格" title="删除">${ic('trash')}</button></div></div>`
def({
  id: 'AD-FORM-005', name: '动态增减行', style: '添加删除',
  fit: '规格、阶梯价、联系人、收货地址这类条数不固定的子表单；每行字段 2–4 个，有数量上下限',
  avoid: '每行字段超过 5 个（行会很挤，改用弹层逐条编辑）；条数上百时改用表格加分页',
  kw: 'dynamic rows add remove 动态 增减行 添加一行 删除 规格 sku',
  css: K('adform005', { w: 640 }) + `
.adform005 .hd{display:flex;align-items:center;justify-content:space-between;gap:12px;padding:16px 24px;border-bottom:1px solid var(--line)}
.adform005 .hd b{font-size:16px;font-weight:600}
.adform005 .bd{padding:16px 24px 12px}
.adform005 .rh,.adform005 .ri{display:grid;grid-template-columns:minmax(0,1.5fr) minmax(0,1fr) minmax(0,1fr) 32px;gap:0 12px;align-items:start}
.adform005 .rh{padding-bottom:6px;color:var(--ink2)}
.adform005 .rw{display:grid;grid-template-rows:1fr;transition:grid-template-rows .2s cubic-bezier(.2,0,0,1),opacity .2s}
.adform005 .rw>.ri{min-height:0;overflow:hidden}
.adform005 .rw.out{grid-template-rows:0fr;opacity:0}
.adform005 .del{width:32px;height:32px;margin:0;border-radius:8px}
.adform005 .del.dis{color:var(--ink6);cursor:not-allowed}
.adform005 .del.dis:hover{background:none}
.adform005 .c::before{display:none}
.adform005 .adb{display:flex;align-items:center;justify-content:center;gap:6px;width:100%;height:32px;margin-top:2px;border:1px dashed var(--bd2);border-radius:8px;color:var(--p-text);font-weight:600;transition:border-color .15s,background-color .15s}
.adform005 .adb:hover{border-color:var(--p);background:var(--pt)}
.adform005 .adb.dis{border-color:var(--bd0);color:var(--ink3);background:none;cursor:not-allowed}
.adform005 .ft{display:flex;justify-content:flex-end;gap:8px;padding:12px 24px;border-top:1px solid var(--line)}
@media(max-width:520px){.adform005 .hd,.adform005 .bd,.adform005 .ft{padding-left:16px;padding-right:16px}.adform005 .rh{display:none}.adform005 .ri{grid-template-columns:minmax(0,1fr) minmax(0,1fr) 32px}.adform005 .c:first-child{grid-column:1/3}.adform005 .del{grid-column:3;grid-row:1}.adform005 .c::before{display:block;content:attr(data-l);font-size:12px;line-height:18px;color:var(--ink3);margin-bottom:2px}.adform005 .c:nth-child(3){grid-column:2}}`,
  html: () => `<div class="adform005">
<div class="hd"><b>商品规格</b><span class="mut" data-meta></span></div>
<div class="bd">
<div class="rh"><span>规格名称</span><span>售价</span><span>库存</span><span></span></div>
<div data-rows>${specRow('标准款 · 石墨灰', '599.00', '80')}${specRow('加大款 · 雾蓝（含无线充电盒与三套耳塞）', '659.00', '46')}${specRow('礼盒款', '699.00', '30')}</div>
<button type="button" class="adb" data-add>${ic('plus')}添加规格</button>
</div>
<div class="ft"><button type="button" class="bt bt-s" data-cancel>取消</button><button type="button" class="bt bt-p" data-save>保存规格</button></div>
</div>`,
  js: H((root, B) => {
    const MAX = 8, MIN = 1, rowsEl = Q(B, '[data-rows]'), init = rowsEl.innerHTML
    const V = mkV(B, {
      spec: (v, B, f) => (!v ? '请输入规格名称' : QA(B, '[data-row]:not([data-gone]) [data-f=spec] .in').some((i) => i !== Q(f, '.in') && i.value.trim() === v) ? '规格名称重复' : ''),
      price: (v) => (/^\d+(\.\d{1,2})?$/.test(v) && +v > 0 ? '' : '请输入大于 0 的售价'),
      stock: (v) => (/^\d+$/.test(v) ? '' : '请输入整数库存'),
    })
    const live = () => QA(B, '[data-row]:not([data-gone])')
    const meta = () => {
      const rows = live(), total = rows.reduce((s, r) => s + (parseInt(Q(r, '[data-f=stock] .in').value, 10) || 0), 0)
      Q(B, '[data-meta]').textContent = `${rows.length}/${MAX} 项 · 总库存 ${total} 件`
      const add = Q(B, '[data-add]'), full = rows.length >= MAX
      add.classList.toggle('dis', full); add.setAttribute('aria-disabled', full); add.innerHTML = full ? `最多 ${MAX} 项` : `${ic('plus')}添加规格`
      QA(B, '[data-del]').forEach((d) => { const lock = rows.length <= MIN; d.classList.toggle('dis', lock); d.setAttribute('aria-disabled', lock); d.title = lock ? '至少保留 1 项' : '删除' })
    }
    meta()
    B.addEventListener('input', (e) => { if (e.target.closest('[data-f=stock]')) meta() })
    B.addEventListener('click', (e) => {
      if (e.target.closest('[data-add]')) {
        if (live().length >= MAX) return
        const r = document.createElement('div'); r.innerHTML = specRow(); const row = r.firstElementChild
        row.classList.add('out'); rowsEl.appendChild(row); meta()
        requestAnimationFrame(() => requestAnimationFrame(() => { row.classList.remove('out'); Q(row, '.in').focus() }))
      }
      const d = e.target.closest('[data-del]')
      if (d && !d.classList.contains('dis')) { const row = d.closest('[data-row]'); row.setAttribute('data-gone', ''); row.classList.add('out'); meta(); setTimeout(() => row.remove(), 220) }
      if (e.target.closest('[data-cancel]')) { rowsEl.innerHTML = init; meta(); tst(B, '已还原') }
    })
    B.addEventListener('click', async (e) => {
      const s = e.target.closest('[data-save]'); if (!s || s.classList.contains('ld')) return
      const bad = V.all()
      if (bad.length) { tst(B, `有 ${bad.length} 项需要修改`, 'bad'); Q(bad[0].f, '.in').focus(); return }
      s.classList.add('ld'); await wait(700); s.classList.remove('ld'); tst(B, `已保存 ${live().length} 个规格`)
    })
  }),
})

/* ---------- AD-FORM-006 键值对编辑器 ---------- */
const kvRow = (k = '', v = '') => `<div class="rw" data-row><div class="ri">
<div class="f c" data-f="k"><input class="in" aria-label="参数名" value="${k}" placeholder="例如：材质" maxlength="20"><span class="er" role="alert"></span></div>
<div class="f c" data-f="v"><input class="in" aria-label="参数值" value="${v}" placeholder="例如：纯棉" maxlength="60"><span class="er" role="alert"></span></div>
<button type="button" class="ib del" data-del aria-label="删除参数" title="删除">${ic('trash')}</button></div></div>`
const KV0 = [['材质', '纯棉（40 支精梳，机洗不易变形）'], ['产地', '浙江杭州'], ['保质期', '12 个月'], ['净含量', '500 克'], ['颜色分类', '雾粉 / 石墨灰 / 燕麦色']]
def({
  id: 'AD-FORM-006', name: '键值对编辑器', style: '表格或文本',
  fit: '商品参数、扩展属性、标签对照这类“名称 + 值”成对的配置；新手用表格逐行填，熟手切到文本批量粘贴',
  avoid: '值需要富文本或多选时；条目固定且不多时，用普通表单更直观',
  kw: 'key value 键值对 参数 属性 配置 编辑器 批量 粘贴 文本模式',
  css: K('adform006', { w: 640 }) + `
.adform006 .hd{display:flex;align-items:center;justify-content:space-between;gap:12px;padding:12px 24px;border-bottom:1px solid var(--line)}
.adform006 .hd b{font-size:16px;font-weight:600}
.adform006 .sgc{display:inline-flex;padding:2px;border-radius:8px;background:var(--soft)}
.adform006 .sgc button{height:28px;padding:0 14px;border-radius:8px;color:var(--ink2);transition:background-color .15s,color .15s}
.adform006 .sgc button.on{background:var(--lift);color:var(--ink);font-weight:600;box-shadow:0 1px 2px var(--sh14)}
.adform006 .sgc button:focus:not(:focus-visible){outline:0}
.adform006 .bd{padding:16px 24px 12px}
.adform006 .rh,.adform006 .ri{display:grid;grid-template-columns:minmax(0,180px) minmax(0,1fr) 32px;gap:0 12px;align-items:start}
.adform006 .rh{padding-bottom:6px;color:var(--ink2)}
.adform006 .rw{display:grid;grid-template-rows:1fr;transition:grid-template-rows .2s cubic-bezier(.2,0,0,1),opacity .2s}
.adform006 .rw>.ri{min-height:0;overflow:hidden}
.adform006 .rw.out{grid-template-rows:0fr;opacity:0}
.adform006 .del{width:32px;height:32px;margin:0;border-radius:8px}
.adform006 .adb{display:flex;align-items:center;justify-content:center;gap:6px;width:100%;height:32px;margin-top:2px;border:1px dashed var(--bd2);border-radius:8px;color:var(--p-text);font-weight:600;transition:border-color .15s,background-color .15s}
.adform006 .adb:hover{border-color:var(--p);background:var(--pt)}
.adform006 .emp{display:none;padding:20px 0 14px;text-align:center;color:var(--ink3)}
.adform006 .emp:only-child{display:block}
.adform006 .ta.big{min-height:196px;font-size:14px;line-height:24px}
.adform006 .ft{display:flex;align-items:center;gap:8px;padding:12px 24px;border-top:1px solid var(--line)}
.adform006 .ft .mut{margin-right:auto}
@media(max-width:520px){.adform006 .hd,.adform006 .bd,.adform006 .ft{padding-left:16px;padding-right:16px}.adform006 .rh,.adform006 .ri{grid-template-columns:minmax(0,110px) minmax(0,1fr) 32px;gap:0 8px}}`,
  html: () => `<div class="adform006">
<div class="hd"><b>商品参数</b><div class="sgc" data-ix="tabs" role="tablist"><button type="button" class="on" data-t="table" role="tab" aria-selected="true">表格</button><button type="button" data-t="text" role="tab" aria-selected="false">文本</button></div></div>
<div class="bd">
<div data-p="table"><div class="rh"><span>参数名</span><span>参数值</span><span></span></div>
<div data-rows>${KV0.map(([k, v]) => kvRow(k, v)).join('')}<div class="emp">还没有参数，点下面的按钮添加</div></div>
<button type="button" class="adb" data-add>${ic('plus')}添加参数</button></div>
<div data-p="text" hidden><div class="f" data-fx><textarea class="in ta big" aria-label="参数文本" spellcheck="false" placeholder="一行一项，格式：参数名：参数值"></textarea><span class="er" role="alert"></span></div></div>
</div>
<div class="ft"><span class="mut" data-meta></span><button type="button" class="bt bt-s" data-cancel>取消</button><button type="button" class="bt bt-p" data-save>保存</button></div>
</div>`,
  js: H((root, B) => {
    const rowsEl = Q(B, '[data-rows]'), ta = Q(B, 'textarea'), init = rowsEl.innerHTML
    const live = () => QA(B, '[data-row]:not([data-gone])')
    const V = mkV(B, {
      k: (v, B, f) => { const row = f.closest('[data-row]'), val = Q(row, '[data-f=v] .in').value.trim(); if (!v && !val) return ''; if (!v) return '请输入参数名'; return live().some((r) => r !== row && Q(r, '[data-f=k] .in').value.trim() === v) ? '参数名重复' : '' },
      v: (v, B, f) => { const row = f.closest('[data-row]'), k = Q(row, '[data-f=k] .in').value.trim(); return k && !v ? '请输入参数值' : '' },
    })
    const meta = () => { Q(B, '[data-meta]').textContent = `共 ${live().filter((r) => Q(r, '[data-f=k] .in').value.trim() || Q(r, '[data-f=v] .in').value.trim()).length} 项` }
    meta()
    const toText = () => (ta.value = live().map((r) => [Q(r, '[data-f=k] .in').value.trim(), Q(r, '[data-f=v] .in').value.trim()]).filter(([k, v]) => k || v).map(([k, v]) => `${k}：${v}`).join('\n'))
    const parse = () => {
      const out = [], lines = ta.value.split('\n'); let bad = ''
      lines.forEach((l, i) => { if (!l.trim() || bad) return; const m = /^\s*([^:：]+?)\s*[:：]\s*(.*)$/.exec(l); if (!m) bad = `第 ${i + 1} 行缺少“：”，格式为 参数名：参数值`; else out.push([m[1], m[2].trim()]) })
      return { out, bad }
    }
    const setErr = (m) => { const f = Q(B, '[data-fx]'); f.classList.toggle('bad', !!m); Q(f, '.er').textContent = m }
    const rebuild = (arr) => { rowsEl.innerHTML = arr.map(([k, v]) => kvRow(k, v)).join('') + '<div class="emp">还没有参数，点下面的按钮添加</div>'; meta() }
    B.addEventListener('click', (e) => {
      const t = e.target.closest('[data-t]')
      if (t) {
        if (t.dataset.t === 'text') { toText(); setErr('') }
        else { const p = parse(); if (p.bad) { e.stopPropagation(); setErr(p.bad); ta.focus(); return } setErr(''); rebuild(p.out) }
      }
      if (e.target.closest('[data-add]')) {
        const r = document.createElement('div'); r.innerHTML = kvRow(); const row = r.firstElementChild
        row.classList.add('out'); rowsEl.insertBefore(row, Q(rowsEl, '.emp')); requestAnimationFrame(() => requestAnimationFrame(() => { row.classList.remove('out'); Q(row, '.in').focus() }))
      }
      const d = e.target.closest('[data-del]')
      if (d) { const row = d.closest('[data-row]'); row.setAttribute('data-gone', ''); row.classList.add('out'); meta(); setTimeout(() => row.remove(), 220) }
      if (e.target.closest('[data-cancel]')) { rowsEl.innerHTML = init; ta.value = ''; setErr(''); meta(); tst(B, '已还原') }
    })
    B.addEventListener('input', (e) => { if (e.target === ta) { if (Q(B, '[data-fx]').classList.contains('bad')) setErr(parse().bad); Q(B, '[data-meta]').textContent = `共 ${parse().out.length} 项` } else meta() })
    B.addEventListener('click', async (e) => {
      const s = e.target.closest('[data-save]'); if (!s || s.classList.contains('ld')) return
      if (!Q(B, '[data-p=text]').hidden) { const p = parse(); if (p.bad) { setErr(p.bad); ta.focus(); return } Q(B, '[data-t=table]').click(); await wait(0) }
      const bad = V.all()
      if (bad.length) { tst(B, `有 ${bad.length} 项需要修改`, 'bad'); Q(bad[0].f, '.in').focus(); return }
      s.classList.add('ld'); await wait(600); s.classList.remove('ld'); tst(B, `已保存 ${live().filter((r) => Q(r, '[data-f=k] .in').value.trim()).length} 项参数`)
    })
  }),
})

/* ---------- AD-FORM-007 登录表单 ---------- */
def({
  id: 'AD-FORM-007', name: '登录表单', style: '居中卡片',
  fit: '后台账号密码登录；失败统一提示“账号或密码错误”，密码框内有显示/隐藏，提交时按钮加载并防重复点击',
  avoid: '不要提示是账号错还是密码错；不要把显示密码做成框外的勾选项；不要在登录页放功能介绍',
  kw: 'login 登录 账号 密码 记住我 显示密码 眼睛 忘记密码 sign in',
  css: K('adform007', { w: 400 }) + `
.adform007{padding:32px 32px 28px;box-shadow:0 1px 2px var(--sh05),0 12px 32px var(--sh08)}
.adform007 .lg{display:flex;flex-direction:column;align-items:center;gap:12px;margin-bottom:20px}
.adform007 .lgt{display:flex;align-items:center;justify-content:center;width:44px;height:44px;border-radius:12px;background:var(--p);color:#fff}
.adform007 .lgt .ic{width:24px;height:24px}
.adform007 h3{margin:0;font-size:20px;line-height:28px;font-weight:600}
.adform007 .alw{display:grid;grid-template-rows:0fr;transition:grid-template-rows .2s cubic-bezier(.2,0,0,1)}
.adform007 .alw.show{grid-template-rows:1fr}
.adform007 .alw>div{min-height:0;overflow:hidden}
.adform007 .al{display:flex;align-items:center;gap:8px;margin-bottom:12px;padding:8px 12px;border-radius:8px;background:var(--dgb);color:var(--dg)}
.adform007 .ig .pf+.in{padding-left:8px}
.adform007 .row{display:flex;align-items:center;justify-content:space-between;margin:2px 0 16px}
.adform007 .lnk{color:var(--p-text);border-radius:4px}
.adform007 .lnk:hover{text-decoration:underline;text-underline-offset:3px}
.adform007 .bt{width:100%}
.adform007 .bt .ic{width:16px;height:16px}
@media(max-width:520px){.adform007{padding:24px 20px 20px}}`,
  html: () => `<form class="adform007" novalidate>
<div class="lg"><span class="lgt">${ic('layers')}</span><h3>登录运营后台</h3></div>
<div class="alw" data-al role="alert"><div><div class="al">${ic('alert')}<span>账号或密码错误</span></div></div></div>
${fld('acc', '账号', (id) => `<div class="ig"><span class="pf">${sv('user')}</span>${inp(id, '', '手机号或工号', 'autocomplete="username"')}</div>`)}
${fld('pwd', '密码', (id) => `<div class="ig"><span class="pf">${sv('lock')}</span>${inp(id, '', '请输入密码', 'type="password" autocomplete="current-password"')}<button type="button" class="ib" data-eye aria-label="显示密码" title="显示密码">${ic('eye')}</button></div>`)}
<div class="row"><button type="button" class="cb" role="checkbox" aria-checked="false" data-ix="toggle"><i></i>记住我</button><button type="button" class="lnk" data-forgot>忘记密码</button></div>
<button type="submit" class="bt bt-p bt-lg">登录</button>
</form>`,
  js: H((root, B) => {
    const al = Q(B, '[data-al]'), btn = Q(B, '[type=submit]')
    const V = mkV(B, { acc: (v) => (v ? '' : '请输入账号'), pwd: (v) => (v ? '' : '请输入密码') })
    B.addEventListener('input', () => al.classList.remove('show'))
    B.addEventListener('click', (e) => {
      const eye = e.target.closest('[data-eye]')
      if (eye) { const i = Q(eye.closest('.ig'), '.in'), show = i.type === 'password'; i.type = show ? 'text' : 'password'; eye.innerHTML = ic(show ? 'eyeoff' : 'eye'); eye.setAttribute('aria-label', show ? '隐藏密码' : '显示密码'); eye.title = show ? '隐藏密码' : '显示密码' }
      if (e.target.closest('[data-forgot]')) tst(B, '请联系系统管理员重置密码')
    })
    B.addEventListener('submit', async (e) => {
      e.preventDefault(); if (btn.classList.contains('ld') || btn.classList.contains('dis')) return
      al.classList.remove('show')
      const bad = V.all(); if (bad.length) { Q(bad[0].f, '.in').focus(); return }
      btn.classList.add('ld'); await wait(800); btn.classList.remove('ld')
      if (Q(B, '[data-f=pwd] .in').value.length < 6) { al.classList.add('show'); return }
      btn.classList.add('dis'); btn.innerHTML = `${ic('check')}已登录`; tst(B, '登录成功，正在进入后台')
      await wait(1800); btn.classList.remove('dis'); btn.textContent = '登录'
    })
  }),
})

/* ---------- AD-FORM-008 搜索新建弹层表单 ---------- */
const CUST0 = [['林小满', '13800138000', '静安旗舰店'], ['陈晓雨', '13900002468', '徐汇中心店'], ['王子豪', '13600009876', '浦东新区店'], ['李安然', '15000006543', '静安旗舰店'], ['周一帆', '13700000011', '杭州西湖体验店'], ['赵可心', '18500003322', '徐汇中心店'], ['吴梓轩', '13200007788', '浦东新区店'], ['郑佳怡', '15800004455', '静安旗舰店']]
const maskP = (p) => p.slice(0, 3) + '****' + p.slice(7)
def({
  id: 'AD-FORM-008', name: '搜索新建弹层表单', style: '居中对话框',
  fit: '选择关联对象（客户、商品、门店）时：先搜，搜不到就在同一个对话框里新建并自动选中，不跳页、不丢当前表单',
  avoid: '候选项不到 5 个（直接用下拉）；表单对话框点遮罩不关闭，不要为了方便改成点遮罩关闭，会丢已填内容',
  kw: 'modal dialog 弹层 对话框 居中 搜索 新建 选择客户 关联 popup',
  css: K('adform008', { w: 640 }) + `
.adform008{min-height:540px;overflow:hidden}
.adform008 .hd{padding:16px 24px;border-bottom:1px solid var(--line);font-size:16px;font-weight:600;line-height:24px}
.adform008 .bd{padding:20px 24px 4px;max-width:520px}
.adform008 .rg{display:flex;flex-wrap:wrap;gap:4px 20px;min-height:32px;align-items:center}
.adform008 .pick{height:40px;padding:0 8px 0 10px}
.adform008 .pick .pl{color:var(--ink3)}
.adform008 .pick .who{display:flex;align-items:center;gap:8px;min-width:0;overflow:hidden;white-space:nowrap}
.adform008 .pick .who .av{width:24px;height:24px}
.adform008 .pick .who small{color:var(--ink3);font-size:12px}
.adform008 .ft{display:flex;justify-content:flex-end;gap:8px;padding:12px 24px;border-top:1px solid var(--line)}
.adform008 .ix-ov{border-radius:inherit;overflow:hidden}
.adform008 .mk{position:absolute;inset:0;background:color-mix(in srgb,var(--scrim) 45%,transparent)}
.adform008 .mdl.nudge{animation:adnudge .18s cubic-bezier(.2,0,0,1)}
@keyframes adnudge{50%{transform:scale(1.012)}}
.adform008 .srch{margin-bottom:8px}
.adform008 .lst{display:flex;flex-direction:column;gap:2px;max-height:272px;overflow:auto}
.adform008 .cu{display:grid;grid-template-columns:32px minmax(0,1fr) auto 16px;align-items:center;gap:12px;min-height:56px;padding:6px 10px;border-radius:8px;text-align:left}
.adform008 .cu:hover{background:var(--mub)}
.adform008 .cu.on{background:var(--pt)}
.adform008 .cu .av{width:32px;height:32px}
.adform008 .cu b{display:block;font-weight:600;overflow:hidden;text-overflow:ellipsis;white-space:nowrap}
.adform008 .cu small{display:block;font-size:12px;line-height:18px;color:var(--ink3)}
.adform008 .cu .tag{max-width:120px;overflow:hidden;text-overflow:ellipsis}
.adform008 .cu i{width:16px;height:16px;border:1px solid var(--bd2);border-radius:50%;position:relative;background:var(--card)}
.adform008 .cu.on i{border-color:var(--p)}
.adform008 .cu.on i::after{content:"";position:absolute;left:3px;top:3px;width:8px;height:8px;border-radius:50%;background:var(--p)}
.adform008 .emp{display:flex;flex-direction:column;align-items:center;gap:12px;padding:28px 0 20px;color:var(--ink2);text-align:center}
.adform008 .mdl-f .lft{margin-right:auto}
.adform008 .mdl-b .f{margin-top:12px}
@media(max-width:520px){.adform008 .hd,.adform008 .bd,.adform008 .ft{padding-left:16px;padding-right:16px}.adform008 .cu{grid-template-columns:32px minmax(0,1fr) 16px}.adform008 .cu .tag{display:none}}`,
  html: () => `<div class="adform008">
<div class="hd">新建工单</div>
<div class="bd">
${fld('title', '工单标题', (id) => inp(id, '', '例如：耳塞尺寸不合适，申请换货', 'maxlength="40" autocomplete="off"'), { req: 1 })}
${fld('cust', '关联客户', `<button type="button" class="in sel pick" data-open="pick" data-pick aria-haspopup="dialog"><span class="pl" data-show>请选择客户</span>${ic('search')}</button>`, { req: 1 })}
${fld('', '优先级', rgHTML(['普通', '加急'], '普通', '优先级'))}
${fld('', '来源渠道', ddHTML(['电话', '在线客服', '到店反馈', '社群'], '在线客服'))}
${fld('', '问题描述', (id) => `<textarea class="in ta" id="${id}" placeholder="补充订单号、商品和希望的处理方式"></textarea>`)}
</div>
<div class="ft"><button type="button" class="bt bt-s" data-cancelp>取消</button><button type="button" class="bt bt-p" data-create>创建工单</button></div>
<div class="ix-ov" data-ov="pick"><div class="mk" data-mk></div>
<div class="mdl" tabindex="-1" role="dialog" aria-modal="true" aria-label="选择客户">
<div data-view="a">
<div class="mdl-h"><h3>选择客户</h3><button type="button" class="ib" data-close aria-label="关闭" title="关闭">${ic('close')}</button></div>
<div class="mdl-b"><div class="ig srch"><span class="pf">${sv('search')}</span><input class="in" data-q placeholder="搜索姓名或手机号" aria-label="搜索客户"><button type="button" class="ib" data-clear aria-label="清除" title="清除" hidden>${ic('close', 14)}</button></div>
<div class="lst" data-list role="radiogroup" aria-label="客户"></div>
<div class="emp" data-empty hidden><span>没有找到“<b data-qs></b>”</span><button type="button" class="bt bt-s" data-new>${ic('plus')}新建客户</button></div></div>
<div class="mdl-f"><button type="button" class="bt bt-t lft" data-new>${ic('plus')}新建客户</button><button type="button" class="bt bt-s" data-close>取消</button><button type="button" class="bt bt-p dis" data-ok aria-disabled="true">确定</button></div>
</div>
<div data-view="b" hidden>
<div class="mdl-h"><button type="button" class="ib" data-back aria-label="返回选择" title="返回">${ic('left')}</button><h3>新建客户</h3><button type="button" class="ib" data-close aria-label="关闭" title="关闭">${ic('close')}</button></div>
<div class="mdl-b">
${fld('nn', '姓名', (id) => inp(id, '', '请输入客户姓名', 'maxlength="20" autocomplete="off"'), { req: 1 })}
${fld('np', '手机号', (id) => `<div class="ig"><span class="ad">+86</span>${inp(id, '', '请输入 11 位手机号', 'inputmode="numeric" maxlength="11" autocomplete="off"')}</div>`, { req: 1 })}
${fld('', '所属门店', ddHTML(STORES, STORES[0]))}
</div>
<div class="mdl-f"><button type="button" class="bt bt-s" data-back>返回</button><button type="button" class="bt bt-p" data-save>保存并选中</button></div>
</div>
</div></div>
</div>`,
  js: H((root, B) => {
    const ov = Q(B, '.ix-ov'), mdl = Q(B, '.mdl'), list = Q(B, '[data-list]'), q = Q(B, '[data-q]'), ok = Q(B, '[data-ok]')
    const custs = CUST0.map(([n, p, s], i) => ({ n, p, s, i })); let sel = -1, chosen = null, nextI = custs.length
    const V = mkV(B, {
      title: (v) => (v ? '' : '请输入工单标题'),
      nn: (v) => (v ? '' : '请输入客户姓名'),
      np: (v) => { if (!v) return '请输入手机号'; if (!/^1[3-9]\d{9}$/.test(v)) return '请输入 11 位手机号'; const d = custs.find((c) => c.p === v); return d ? `该手机号已有客户“${d.n}”` : '' },
    })
    const view = (k) => QA(B, '[data-view]').forEach((v) => (v.hidden = v.dataset.view !== k))
    const render = () => {
      const s = q.value.trim().toLowerCase(), rows = custs.filter((c) => !s || c.n.toLowerCase().includes(s) || c.p.includes(s))
      list.innerHTML = rows.map((c) => `<button type="button" class="cu${c.i === sel ? ' on' : ''}" role="radio" aria-checked="${c.i === sel}" data-i="${c.i}">${critter(c.i, 32)}<span><b>${c.n}</b><small>${maskP(c.p)}</small></span><span class="tag">${c.s}</span><i></i></button>`).join('')
      Q(B, '[data-empty]').hidden = rows.length > 0; list.hidden = rows.length === 0; Q(B, '[data-qs]').textContent = q.value.trim()
      Q(B, '[data-clear]').hidden = !q.value; ok.classList.toggle('dis', sel < 0); ok.setAttribute('aria-disabled', sel < 0)
    }
    const open = () => { view('a'); q.value = ''; sel = chosen ? chosen.i : -1; render(); setTimeout(() => q.focus(), 30) }
    const close = (back) => { ov.classList.remove('show'); if (back) Q(B, '[data-pick]').focus() }
    const choose = (c) => {
      chosen = c; sel = c.i
      Q(B, '[data-show]').outerHTML = `<span class="who" data-show>${critter(c.i, 24)}<b>${c.n}</b><small>${maskP(c.p)}</small></span>`
      const f = Q(B, '[data-f=cust]'); f.classList.remove('bad'); Q(f, '.er').textContent = ''
    }
    B.addEventListener('click', (e) => {
      if (e.target.closest('[data-pick]')) open()
      if (e.target.closest('[data-cancelp]')) tst(B, '已取消')
      const cu = e.target.closest('.cu'); if (cu) { sel = +cu.dataset.i; QA(list, '.cu').forEach((x) => { const on = +x.dataset.i === sel; x.classList.toggle('on', on); x.setAttribute('aria-checked', on) }); ok.classList.remove('dis'); ok.setAttribute('aria-disabled', 'false') }
      if (e.target.closest('[data-ok]') && sel >= 0) { choose(custs.find((c) => c.i === sel)); close(true); tst(B, `已选择 ${chosen.n}`) }
      if (e.target.closest('[data-clear]')) { q.value = ''; render(); q.focus() }
      if (e.target.closest('[data-new]')) { const nm = Q(B, '[data-f=nn] .in'); view('b'); nm.value = /^[^\d]+$/.test(q.value.trim()) ? q.value.trim() : ''; QA(B, '[data-view=b] [data-f]').forEach((f) => { f.classList.remove('bad'); Q(f, '.er').textContent = '' }); setTimeout(() => nm.focus(), 30) }
      if (e.target.closest('[data-back]')) { view('a'); setTimeout(() => q.focus(), 30) }
      if (e.target.closest('[data-close]')) setTimeout(() => Q(B, '[data-pick]').focus(), 0)
      if (e.target.closest('[data-mk]')) { mdl.classList.remove('nudge'); void mdl.offsetWidth; mdl.classList.add('nudge') }
      if (e.target.closest('[data-save]')) {
        const bad = QA(B, '[data-view=b] [data-f]').map((f) => ({ f, m: V.run(f) })).filter((x) => x.m)
        if (bad.length) { Q(bad[0].f, '.in').focus(); return }
        const c = { n: Q(B, '[data-f=nn] .in').value.trim(), p: Q(B, '[data-f=np] .in').value.trim(), s: Q(B, '[data-view=b] [data-label]').textContent.trim(), i: nextI++ }
        custs.unshift(c); choose(c); close(true); tst(B, `已新建并选中 ${c.n}`)
      }
      if (e.target.closest('[data-create]')) {
        const tf = Q(B, '[data-f=title]'), tm = V.run(tf); let cm = false
        if (!chosen) { const f = Q(B, '[data-f=cust]'); f.classList.add('bad'); Q(f, '.er').textContent = '请选择关联客户'; cm = true }
        if (tm) Q(tf, '.in').focus(); else if (cm) Q(B, '[data-pick]').focus()
        if (tm || cm) return
        tst(B, '工单已创建')
      }
    })
    B.addEventListener('dblclick', (e) => { const cu = e.target.closest('.cu'); if (cu) { sel = +cu.dataset.i; Q(B, '[data-ok]').click() } })
    q.addEventListener('input', () => { if (sel >= 0 && !custs.some((c) => c.i === sel && (c.n.includes(q.value.trim()) || c.p.includes(q.value.trim())))) sel = -1; render() })
    ov.addEventListener('keydown', (e) => {
      if (e.key === 'Escape') { e.stopPropagation(); close(true); return }
      if (e.key === 'Tab') {
        const f = QA(mdl, 'button,input,[tabindex]:not([tabindex="-1"])').filter((x) => x.offsetParent && !x.disabled); if (!f.length) return
        const a = document.activeElement, first = f[0], last = f[f.length - 1]
        if (e.shiftKey && (a === first || a === mdl)) { e.preventDefault(); last.focus() } else if (!e.shiftKey && a === last) { e.preventDefault(); first.focus() }
      }
      if (e.key === 'Enter' && e.target === q) { e.preventDefault(); const f = list.querySelector('.cu'); if (f) { sel = +f.dataset.i; render() } }
    })
    render()
  }),
})

/* ---------- 共用：标签输入（AD-FORM-011、AD-CTRL-013 都用）---------- */
const TAGI_CSS = (q) => `
${q} .tgi{display:flex;flex-wrap:wrap;align-items:center;gap:4px 6px;min-height:32px;padding:3px 8px;border:1px solid var(--bd);border-radius:8px;background:var(--card);cursor:text;transition:border-color .15s}
${q} .tgi:hover{border-color:var(--bd2)}
${q} .tgi:focus-within{border-color:var(--ink2)}
${q} .tgi .tag{height:24px;padding:0 3px 0 8px;font-size:12px}
${q} .tgi .tag .x{display:inline-flex;align-items:center;justify-content:center;width:18px;height:18px;border-radius:4px;color:inherit}
${q} .tgi .tag .x:hover{background:var(--veil08)}
${q} .tgi .tag .x .ic{width:12px;height:12px}
${q} .tgi .tag.shake{animation:adshake .28s cubic-bezier(.2,0,0,1)}
${q} .tgi .tin{flex:1;min-width:96px;height:24px;padding:0;border:0;outline:0;background:none;font:inherit;font-size:14px;color:var(--ink)}
${q} .tgi .tin::placeholder{color:var(--ink3)}
${q} .tgi.full{background:var(--n2)}
@keyframes adshake{25%{transform:translateX(-3px)}75%{transform:translateX(3px)}}
`
const tagHTML = (t, cls = 'pri') => `<span class="tag ${cls}" data-tag="${t}">${t}<button type="button" class="x" data-x aria-label="删除标签 ${t}">${ic('close')}</button></span>`
/* 标签输入逻辑：回车或逗号添加，退格删最后一个，× 删除，重复提示，到上限禁用 */
const mkTags = (wrap, o = {}) => {
  const max = o.max || 99, inpEl = Q(wrap, '.tin'), er = o.er
  const tags = () => QA(wrap, '[data-tag]').map((x) => x.dataset.tag)
  const msg = (m) => { if (er) er.textContent = m }
  const sync = () => { const full = tags().length >= max; wrap.classList.toggle('full', full); inpEl.disabled = full; inpEl.placeholder = full ? `最多 ${max} 个标签` : (o.ph || '输入后回车添加'); o.onChange && o.onChange(tags()) }
  const add = (raw) => {
    const t = raw.trim().replace(/[，,]+$/, '').trim(); if (!t) return false
    if (t.length > (o.len || 12)) { msg(`标签最多 ${o.len || 12} 个字`); return false }
    const ex = QA(wrap, '[data-tag]').find((x) => x.dataset.tag === t)
    if (ex) { msg(`“${t}”已存在`); ex.classList.remove('shake'); void ex.offsetWidth; ex.classList.add('shake'); return false }
    if (tags().length >= max) return false
    inpEl.insertAdjacentHTML('beforebegin', tagHTML(t, typeof o.cls === 'function' ? o.cls(t) : o.cls)); msg(''); sync(); return true
  }
  wrap.addEventListener('click', (e) => { const x = e.target.closest('[data-x]'); if (x) { x.closest('[data-tag]').remove(); msg(''); sync(); inpEl.focus() } else inpEl.focus() })
  inpEl.addEventListener('keydown', (e) => {
    if (e.isComposing) return
    if (e.key === 'Enter' || e.key === ',' || e.key === '，') { e.preventDefault(); if (add(inpEl.value)) inpEl.value = '' }
    else if (e.key === 'Backspace' && !inpEl.value) { const l = QA(wrap, '[data-tag]').pop(); if (l) { l.remove(); msg(''); sync() } }
  })
  inpEl.addEventListener('paste', (e) => { const t = (e.clipboardData || window.clipboardData).getData('text'); if (/[,，;；\s]/.test(t.trim())) { e.preventDefault(); t.split(/[,，;；\s]+/).forEach(add) } })
  inpEl.addEventListener('input', () => { if (er && er.textContent) msg('') })
  inpEl.addEventListener('blur', () => { if (inpEl.value.trim() && add(inpEl.value)) inpEl.value = '' })
  sync()
  return { add, tags, sync }
}

/* ---------- AD-FORM-009 行内小表单 ---------- */
const catRow = (n, cnt, on = true, flash = false) => `<li class="rw${flash ? ' flash' : ''}" data-row data-cnt="${cnt}"><div class="rn"><button type="button" class="nm${on ? '' : ' off'}" data-edit title="点击改名">${n}</button><span class="tag">${cnt} 件商品</span>${swHTML(on, `启用 ${n}`, 'data-sw', true)}<button type="button" class="ib del${cnt ? ' dis' : ''}" data-del aria-label="删除分类" title="${cnt ? `分类下还有 ${cnt} 件商品，不能删除` : '删除分类'}">${ic('trash')}</button></div><div class="cf" hidden><span>删除“<b data-cn>${n}</b>”？删除后无法恢复</span><button type="button" class="bt bt-s" data-ccan>保留</button><button type="button" class="bt bt-dt" data-cdel>删除分类</button></div></li>`
def({
  id: 'AD-FORM-009', name: '行内小表单', style: '行内改名',
  fit: '分类、标签、字典这类一两个字段的小对象：顶部行内添加，列表里点名字直接改，回车保存，开关立即生效',
  avoid: '字段超过 3 个或需要校验多条规则（改用弹层表单）；影响金额或数据的修改不要用失焦自动保存',
  kw: 'inline form 行内 内联编辑 快速添加 分类 标签 点击改名 回车保存 inline',
  css: K('adform009', { w: 640 }) + `
.adform009 .hd{display:flex;align-items:center;justify-content:space-between;padding:16px 24px;border-bottom:1px solid var(--line)}
.adform009 .hd b{font-size:16px;font-weight:600}
.adform009 .qa{padding:16px 24px 0}
.adform009 .qr{display:flex;align-items:flex-start;gap:8px}
.adform009 .qr .f{flex:1;min-width:0}
.adform009 .qr .f.sm{flex:none;width:132px}
.adform009 .qr .er{margin-top:2px}
.adform009 .ls{list-style:none;margin:0;padding:0 0 8px;min-height:60px}
.adform009 .rw{position:relative;display:block;padding:0 24px;border-bottom:1px solid var(--line)}
.adform009 .rw:last-child{border-bottom:0}
.adform009 .rn,.adform009 .cf{display:flex;align-items:center;gap:12px;min-height:52px}
.adform009 .nm{flex:1;min-width:0;height:32px;padding:0 8px;margin-left:-8px;border-radius:4px;text-align:left;font-weight:600;overflow:hidden;text-overflow:ellipsis;white-space:nowrap}
.adform009 .nm:hover{background:var(--mub)}
.adform009 .nm.off{color:var(--ink3);font-weight:400}
.adform009 .ed{flex:1;min-width:0;width:auto;height:32px;margin-left:-8px}
.adform009 .del{margin:0;width:32px;height:32px}
.adform009 .del.dis{color:var(--ink6);cursor:not-allowed}
.adform009 .del.dis:hover{background:none}
.adform009 .cf{justify-content:flex-end;color:var(--dg)}
.adform009 .cf span{margin-right:auto}
.adform009 .cf b{font-weight:600}
.adform009 .rw.flash{animation:adfl 1.4s cubic-bezier(.2,0,0,1)}
.adform009 .rw.out{opacity:0;transition:opacity .2s}
@keyframes adfl{0%,40%{background:var(--pt)}100%{background:transparent}}
.adform009 .nom{padding:20px 24px;text-align:center;color:var(--ink3)}
@media(max-width:520px){.adform009 .hd,.adform009 .qa,.adform009 .rw{padding-left:16px;padding-right:16px}.adform009 .qr{flex-wrap:wrap}.adform009 .qr .f{flex:1 1 100%}.adform009 .qr .f.sm{flex:1}.adform009 .rn .tag{display:none}.adform009 .cf{flex-wrap:wrap}.adform009 .cf span{flex:1 1 100%}}`,
  html: () => `<div class="adform009">
<div class="hd"><b>商品分类</b><span class="mut" data-meta></span></div>
<form class="qa" data-qa novalidate><div class="qr">
<div class="f" data-f="nm"><div class="ctl"><div class="ig"><span class="ad">名称</span><input class="in" aria-label="分类名称" placeholder="例如：运动户外" maxlength="12" autocomplete="off"></div><span class="er" role="alert"></span></div></div>
<div class="f sm"><div class="ctl"><div class="ig"><span class="ad">排序</span><input class="in" aria-label="排序" value="5" inputmode="numeric" maxlength="3"></div><span class="er"></span></div></div>
<button type="submit" class="bt bt-p dis" aria-disabled="true">${ic('plus')}添加</button></div></form>
<ul class="ls" data-ls>${catRow('数码配件', 48)}${catRow('家居日用', 126)}${catRow('服饰鞋包', 87)}${catRow('食品饮料', 0, false)}</ul>
</div>`,
  js: H((root, B) => {
    const ls = Q(B, '[data-ls]'), qa = Q(B, '[data-qa]'), nm = Q(qa, '[data-f=nm] .in'), er = Q(qa, '[data-f=nm] .er'), add = Q(qa, '[type=submit]')
    const rows = () => QA(ls, '[data-row]:not(.out)')
    const nameOf = (r) => (Q(r, '.nm') ? Q(r, '.nm').textContent.trim() : '')
    const meta = () => { Q(B, '[data-meta]').textContent = `共 ${rows().length} 项`; if (!ls.children.length) ls.innerHTML = '<li class="nom">还没有分类，在上方输入名称添加</li>' }
    meta()
    nm.addEventListener('input', () => { const has = !!nm.value.trim(); add.classList.toggle('dis', !has); add.setAttribute('aria-disabled', !has); er.textContent = ''; nm.closest('.f').classList.remove('bad') })
    qa.addEventListener('submit', (e) => {
      e.preventDefault(); const v = nm.value.trim(); if (!v) return
      if (rows().some((r) => nameOf(r) === v)) { nm.closest('.f').classList.add('bad'); er.textContent = '分类名称已存在'; return }
      const nom = Q(ls, '.nom'); if (nom) nom.remove()
      ls.insertAdjacentHTML('beforeend', catRow(v, 0, true, true)); nm.value = ''; add.classList.add('dis'); nm.focus()
      const so = Q(qa, '.f.sm .in'); so.value = String((parseInt(so.value, 10) || 0) + 1); meta(); tst(B, `已添加“${v}”`)
    })
    B.addEventListener('click', (e) => {
      const ed = e.target.closest('[data-edit]')
      if (ed) {
        const row = ed.closest('[data-row]'), old = ed.textContent.trim(), i = document.createElement('input')
        i.className = 'in ed'; i.value = old; i.maxLength = 12; i.setAttribute('aria-label', '分类名称'); ed.replaceWith(i); i.focus(); i.select()
        let done = false
        const finish = (save) => {
          if (done) return; const v = i.value.trim()
          if (save && v && v !== old && rows().some((r) => r !== row && nameOf(r) === v)) { if (document.activeElement === i) { tst(B, '分类名称已存在', 'bad'); return } save = false; tst(B, '分类名称已存在，未修改', 'bad') }
          done = true; const b = document.createElement('button'); b.type = 'button'; b.className = 'nm' + (Q(row, '.tgl').classList.contains('on') ? '' : ' off'); b.dataset.edit = ''; b.title = '点击改名'
          const nv = save && v ? v : old; b.textContent = nv; i.replaceWith(b)
          if (save && v && v !== old) { Q(row, '[data-cn]').textContent = nv; tst(B, '已保存'); b.focus() }
        }
        i.addEventListener('keydown', (k) => { if (k.key === 'Enter') { k.preventDefault(); finish(true) } else if (k.key === 'Escape') { k.preventDefault(); finish(false) } })
        i.addEventListener('blur', () => finish(true))
      }
      const sw = e.target.closest('[data-sw]')
      if (sw) { setTimeout(() => { const on = sw.classList.contains('on'), row = sw.closest('[data-row]'); Q(row, '.nm') && Q(row, '.nm').classList.toggle('off', !on); tst(B, `“${nameOf(row)}”已${on ? '启用' : '停用'}`) }, 0) }
      const d = e.target.closest('[data-del]')
      if (d && !d.classList.contains('dis')) { const row = d.closest('[data-row]'); Q(row, '.rn').hidden = true; Q(row, '.cf').hidden = false; Q(row, '[data-ccan]').focus() }
      const cc = e.target.closest('[data-ccan]'); if (cc) { const row = cc.closest('[data-row]'); Q(row, '.cf').hidden = true; Q(row, '.rn').hidden = false }
      const cd = e.target.closest('[data-cdel]')
      if (cd) { const row = cd.closest('[data-row]'), n = Q(row, '[data-cn]').textContent; row.classList.add('out'); setTimeout(() => { row.remove(); meta(); tst(B, `已删除“${n}”`) }, 200) }
    })
    /* 行内的开关：点一下立即切换 */
    B.addEventListener('click', (e) => { const sw = e.target.closest('.tgl[data-sw]'); if (sw) { sw.classList.toggle('on'); sw.setAttribute('aria-checked', sw.classList.contains('on')) } }, true)
  }),
})

/* ---------- AD-FORM-010 开关设置表单 ---------- */
const stRow = (title, desc, ctrl, attrs = '') => `<div class="rw" data-row ${attrs}><div class="tx"><b>${title}</b><span class="ds">${desc}</span><em class="rs" data-reason role="alert"></em></div><div class="ct">${ctrl}</div></div>`
def({
  id: 'AD-FORM-010', name: '开关设置表单', style: '开关加说明',
  fit: '经营设置、通知设置、功能开关：左边标题加一句影响说明，右边放控件；开关点了就生效，数值改了出现保存，影响资金的先确认',
  avoid: '说明写成长段文字（一句话说清影响即可）；开关后面再放“保存”按钮；多个设置之间有依赖时要先理顺再放开关',
  kw: 'settings switch 设置 开关 说明 经营设置 即时生效 回滚 确认框 手续费',
  css: K('adform010', { w: 640 }) + `
.adform010{min-height:540px;overflow:hidden}
.adform010 .stt{margin:0;padding:20px 24px 4px;font-size:16px;line-height:24px;font-weight:600}
.adform010 .rw{display:flex;align-items:center;gap:16px;padding:14px 24px;border-bottom:1px solid var(--line)}
.adform010 .rw:last-child{border-bottom:0}
.adform010 .sec+.sec{border-top:8px solid var(--bg)}
.adform010 .tx{flex:1;min-width:0}
.adform010 .tx b{display:block;font-weight:600}
.adform010 .ds{display:block;font-size:12px;line-height:18px;color:var(--ink3)}
.adform010 .rs{display:none;margin-top:4px;font-style:normal;font-size:12px;line-height:18px;color:var(--dg)}
.adform010 .rw.err .rs{display:block}
.adform010 .ct{display:flex;align-items:center;justify-content:flex-end;gap:8px;flex:none}
.adform010 .ct .ig{width:120px}
.adform010 .ct .dd{width:152px}
.adform010 .pa{display:none;align-items:center;gap:8px}
.adform010 .rw.pend .pa{display:flex}
.adform010 .rw.bad .ig,.adform010 .rw.bad .ig:focus-within{border-color:var(--dg)}
.adform010 .ix-ov{border-radius:inherit;overflow:hidden}
.adform010 .mk{position:absolute;inset:0;background:color-mix(in srgb,var(--scrim) 45%,transparent)}
.adform010 .mdl{width:min(440px,calc(100% - 32px))}
.adform010 .chg{display:grid;grid-template-columns:1fr auto 1fr;align-items:center;gap:12px;margin:4px 0 12px;padding:12px 16px;border-radius:8px;background:var(--n2);text-align:center}
.adform010 .chg small{display:block;font-size:12px;line-height:18px;color:var(--ink3)}
.adform010 .chg b{font-size:18px;line-height:26px;font-weight:600}
.adform010 .chg .ic{color:var(--ink3)}
.adform010 .imp{margin:0 0 8px;color:var(--ink2)}
.adform010 .mdl-b .f{margin-top:12px}
@media(max-width:520px){.adform010 .rw{flex-wrap:wrap;padding-left:16px;padding-right:16px}.adform010 .stt{padding-left:16px}.adform010 .tx{flex:1 1 60%}.adform010 .ct{flex:1 1 100%;justify-content:flex-start}}`,
  html: () => `<div class="adform010">
<div class="sec"><h4 class="stt">订单与通知</h4>
${stRow('自动接单', '新订单自动确认，无需店员手动点击', swHTML(true, '自动接单', 'data-sw="ok"'))}
${stRow('短信通知', '订单状态变化时短信通知顾客', swHTML(false, '短信通知', 'data-sw="fail"'))}
${stRow('超时关闭', '未支付订单超过设定时间自动关闭', `<span class="pa"><button type="button" class="bt bt-s" data-cancelv>取消</button><button type="button" class="bt bt-p" data-savev>保存</button></span><div class="ig"><input class="in" aria-label="超时关闭分钟数" value="30" inputmode="numeric" maxlength="3" data-v><span class="sx">分钟</span></div>`, 'data-val data-saved="30" data-kind="num"')}
</div>
<div class="sec"><h4 class="stt">资金规则</h4>
${stRow('退款手续费', '按退款金额收取，只影响之后的退款', `<span class="pa"><button type="button" class="bt bt-s" data-cancelv>取消</button><button type="button" class="bt bt-p" data-savev>保存</button></span><div class="ig"><input class="in" aria-label="退款手续费比例" value="2" inputmode="decimal" maxlength="4" data-v><span class="sx">%</span></div>`, 'data-val data-saved="2" data-kind="fee" data-money="1" data-name="退款手续费" data-unit="%"')}
${stRow('储值扣减顺序', '消费时先扣哪部分余额，只影响之后的订单', `<span class="pa"><button type="button" class="bt bt-s" data-cancelv>取消</button><button type="button" class="bt bt-p" data-savev>保存</button></span>${ddHTML(['先本金后赠送', '先赠送后本金'], '先本金后赠送')}`, 'data-val data-saved="先本金后赠送" data-kind="dd" data-money="1" data-name="储值扣减顺序" data-unit=""')}
</div>
<div class="ix-ov" data-ov="cf"><div class="mk" data-mk></div>
<div class="mdl" tabindex="-1" role="dialog" aria-modal="true" aria-label="确认修改">
<div class="mdl-h"><h3 data-ct>确认修改</h3><button type="button" class="ib" data-close aria-label="关闭" title="关闭">${ic('close')}</button></div>
<div class="mdl-b"><div class="chg"><div><small>改前</small><b data-old></b></div>${ic('arrowright')}<div><small>改后</small><b data-new></b></div></div>
<p class="imp" data-imp></p>
${fld('why', '修改原因', (id) => inp(id, '', '例如：与新的合作协议保持一致', 'maxlength="50" autocomplete="off"'), { req: 1 })}</div>
<div class="mdl-f"><button type="button" class="bt bt-s" data-close>取消</button><button type="button" class="bt bt-p" data-confirm>确认修改</button></div>
</div></div>
</div>`,
  js: H((root, B) => {
    const ov = Q(B, '.ix-ov'), mdl = Q(B, '.mdl'); let cur = null
    const V = mkV(B, { why: (v) => (v ? '' : '请填写修改原因') })
    const valOf = (row) => (row.dataset.kind === 'dd' ? Q(row, '[data-label]').textContent.trim() : Q(row, '[data-v]').value.trim())
    const check = (row) => {
      const v = valOf(row); let bad = ''
      if (row.dataset.kind === 'fee' && !(/^\d+(\.\d)?$/.test(v) && +v <= 20)) bad = '请输入 0–20 的数字，最多一位小数'
      if (row.dataset.kind === 'num' && !(/^\d+$/.test(v) && +v >= 5 && +v <= 720)) bad = '请输入 5–720 的整数'
      row.classList.toggle('bad', !!bad); row.classList.toggle('err', !!bad); Q(row, '[data-reason]').textContent = bad
      return bad
    }
    const pend = (row) => { const p = valOf(row) !== row.dataset.saved; row.classList.toggle('pend', p); if (!p) { row.classList.remove('bad', 'err'); Q(row, '[data-reason]').textContent = '' } }
    B.addEventListener('input', (e) => { const row = e.target.closest('[data-val]'); if (row) { pend(row); if (row.classList.contains('pend') && row.classList.contains('bad')) check(row) } })
    B.addEventListener('click', () => setTimeout(() => QA(B, '[data-val]').forEach(pend), 0))
    /* 开关：先切换再请求，失败回滚并在原位写原因 */
    B.addEventListener('click', async (e) => {
      const sw = e.target.closest('.tgl[data-sw]'); if (!sw || sw.classList.contains('ld')) return
      const row = sw.closest('[data-row]'), rs = Q(row, '[data-reason]'); row.classList.remove('err'); rs.textContent = ''
      const name = Q(row, '.tx b').textContent, was = sw.classList.contains('on'); sw.classList.toggle('on', !was); sw.classList.add('ld')
      await wait(700); sw.classList.remove('ld')
      if (sw.dataset.sw === 'fail' && !sw.dataset.tried) { sw.dataset.tried = '1'; sw.classList.toggle('on', was); row.classList.add('err'); rs.textContent = `保存失败：网络连接中断，已恢复为${was ? '开启' : '关闭'}，请重试`; return }
      tst(B, `${name}已${was ? '关闭' : '开启'}`)
    }, true)
    const done = (row, v) => { row.dataset.saved = v; pend(row); tst(B, row.dataset.money ? '已生效，只影响之后的业务' : '已保存') }
    B.addEventListener('click', async (e) => {
      const c = e.target.closest('[data-cancelv]')
      if (c) { const row = c.closest('[data-val]'); if (row.dataset.kind === 'dd') { const s = row.dataset.saved; QA(row, '[data-o]').forEach((o) => o.classList.toggle('on', o.textContent.trim() === s)); Q(row, '[data-label]').textContent = s } else Q(row, '[data-v]').value = row.dataset.saved; pend(row); return }
      const s = e.target.closest('[data-savev]')
      if (s && !s.classList.contains('ld')) {
        const row = s.closest('[data-val]'); if (check(row)) return
        if (row.dataset.money) {
          cur = row; const u = row.dataset.unit
          Q(B, '[data-ct]').textContent = `确认修改${row.dataset.name}`; Q(B, '[data-old]').textContent = row.dataset.saved + u; Q(B, '[data-new]').textContent = valOf(row) + u
          Q(B, '[data-imp]').textContent = row.dataset.kind === 'fee' ? '只影响之后发起的退款，已完成的退款不变。' : '只影响之后的订单，已发生的扣款不变。'
          const w = Q(B, '[data-f=why]'); Q(w, '.in').value = ''; w.classList.remove('bad'); Q(w, '.er').textContent = ''
          ov.classList.add('show'); setTimeout(() => Q(w, '.in').focus(), 30); return
        }
        s.classList.add('ld'); await wait(600); s.classList.remove('ld'); done(row, valOf(row))
      }
      if (e.target.closest('[data-confirm]')) {
        const w = Q(B, '[data-f=why]'); if (V.run(w)) { Q(w, '.in').focus(); return }
        const b = e.target.closest('[data-confirm]'); b.classList.add('ld'); await wait(700); b.classList.remove('ld'); ov.classList.remove('show'); done(cur, valOf(cur))
      }
      if (e.target.closest('[data-mk]')) { mdl.classList.remove('nudge'); void mdl.offsetWidth; mdl.classList.add('nudge') }
    })
    ov.addEventListener('keydown', (e) => {
      if (e.key === 'Escape') { e.stopPropagation(); ov.classList.remove('show'); return }
      if (e.key === 'Enter' && e.target.matches('.in')) { e.preventDefault(); Q(B, '[data-confirm]').click() }
      if (e.key === 'Tab') { const f = QA(mdl, 'button,input').filter((x) => x.offsetParent && !x.disabled), a = document.activeElement; if (e.shiftKey && a === f[0]) { e.preventDefault(); f[f.length - 1].focus() } else if (!e.shiftKey && a === f[f.length - 1]) { e.preventDefault(); f[0].focus() } }
    })
    B.addEventListener('keydown', (e) => { if (e.key === 'Enter' && e.target.matches('[data-v]')) { e.preventDefault(); Q(e.target.closest('[data-val]'), '[data-savev]').click() } })
  }),
})

/* ---------- AD-FORM-011 带预览编辑表单 ---------- */
const PV_IMG = [0, 1, 2, 5]
def({
  id: 'AD-FORM-011', name: '带预览编辑表单', style: '左填右看',
  fit: '商品、活动、横幅这类要在前台展示的内容：左边填，右边实时预览前台的样子，填完不用保存了才发现排版不对',
  avoid: '没有前台展示的纯配置；预览和真实展示不一致时（预览会误导人），先对齐再用',
  kw: 'preview 预览 实时预览 商品编辑 标签 封面 字数 前缀 后缀 上架',
  wide: true,
  css: K('adform011', { w: 960 }) + TAGI_CSS('.adform011') + `
.adform011 .hd{padding:16px 24px;border-bottom:1px solid var(--line);font-size:16px;font-weight:600;line-height:24px}
.adform011 .bd{display:grid;grid-template-columns:minmax(0,1fr) 300px;gap:0 32px;padding:20px 24px 8px}
.adform011 .pr2{display:grid;grid-template-columns:minmax(0,1fr) minmax(0,1fr);gap:0 12px}
.adform011 .cnt{padding-right:10px;font-size:12px;color:var(--ink3);white-space:nowrap}
.adform011 .cv{display:flex;gap:8px}
.adform011 .cv button{position:relative;width:56px;height:56px;border-radius:8px;overflow:hidden;border:2px solid transparent;transition:border-color .15s}
.adform011 .cv button img{width:100%;height:100%;object-fit:cover}
.adform011 .cv button:hover{border-color:var(--bd)}
.adform011 .cv button.on{border-color:var(--p)}
.adform011 .cv button.on::after{content:"";position:absolute;right:3px;top:3px;width:16px;height:16px;border-radius:50%;background:var(--p) url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='none' stroke='white' stroke-width='3.2' stroke-linecap='round' stroke-linejoin='round'%3E%3Cpath d='m5 12.500 5 5L19.500 7'/%3E%3C/svg%3E") center/11px no-repeat}
.adform011 .sf{display:flex;align-items:center;min-height:32px}
.adform011 .pvw{position:sticky;top:12px;align-self:start;padding:16px;border-radius:12px;background:var(--n3)}
.adform011 .pvh{display:flex;align-items:center;justify-content:space-between;margin-bottom:10px;font-weight:600}
.adform011 .pv{border-radius:12px;background:var(--card);overflow:hidden;box-shadow:0 2px 10px var(--sh08)}
.adform011 .pv .im{position:relative;aspect-ratio:1/1;background:var(--ph)}
.adform011 .pv .im img{width:100%;height:100%;object-fit:cover}
.adform011 .pv .off{position:absolute;inset:0;display:none;align-items:center;justify-content:center;background:color-mix(in srgb,var(--scrim) 50%,transparent);color:#fff;font-weight:600}
.adform011 .pv.down .off{display:flex}
.adform011 .pv .tx{padding:10px 12px 12px}
.adform011 .pv h4{margin:0;font-size:14px;line-height:20px;font-weight:600;display:-webkit-box;-webkit-line-clamp:2;-webkit-box-orient:vertical;overflow:hidden}
.adform011 .pv p{margin:2px 0 0;font-size:12px;line-height:18px;color:var(--ink3);white-space:nowrap;overflow:hidden;text-overflow:ellipsis;min-height:18px}
.adform011 .pv .tgs{display:flex;gap:4px;margin-top:6px;min-height:20px;overflow:hidden}
.adform011 .pv .tgs .tag{height:18px;padding:0 6px}
.adform011 .pv .pc{display:flex;align-items:baseline;gap:6px;margin-top:6px;color:var(--price);font-variant-numeric:tabular-nums}
.adform011 .pv .pc small{font-size:12px;font-weight:600}
.adform011 .pv .pc b{font-size:22px;line-height:28px;font-weight:600}
.adform011 .pv .pc s{font-size:12px;color:var(--ink3)}
.adform011 .ft{display:flex;justify-content:flex-end;gap:8px;padding:12px 24px;border-top:1px solid var(--line)}
@media(max-width:760px){.adform011 .bd{grid-template-columns:minmax(0,1fr);padding-left:16px;padding-right:16px}.adform011 .pvw{position:static;margin-bottom:16px;order:-1}.adform011 .hd,.adform011 .ft{padding-left:16px;padding-right:16px}}`,
  html: () => `<div class="adform011">
<div class="hd">编辑商品</div>
<div class="bd">
<div>
${fld('name', '商品名称', (id) => `<div class="ig">${inp(id, '无线降噪耳机 Pro', '最多 30 个字', 'maxlength="30" autocomplete="off"')}<span class="cnt" data-cnt>8/30</span></div>`, { req: 1 })}
${fld('', '副标题', (id) => inp(id, '石墨灰 · 主动降噪', '一句话卖点', 'maxlength="20" data-sub'))}
<div class="pr2">
${fld('price', '售价', (id) => `<div class="ig"><span class="ad">¥</span>${inp(id, '599', '0.00', 'inputmode="decimal" data-price')}</div>`, { req: 1 })}
${fld('', '划线价', (id) => `<div class="ig"><span class="ad">¥</span>${inp(id, '799', '不填则不显示', 'inputmode="decimal" data-mkt')}</div>`)}
</div>
${fld('', '商品标签', `<div class="tgi" data-tags>${tagHTML('热卖')}${tagHTML('包邮')}<input class="tin" aria-label="添加标签" placeholder="输入后回车添加"></div>`)}
${fld('', '封面图', `<div class="cv" data-cv role="radiogroup" aria-label="封面图">${PV_IMG.map((i, k) => `<button type="button" class="${k === 0 ? 'on' : ''}" role="radio" aria-checked="${k === 0}" data-i="${i}" aria-label="封面 ${k + 1}"><img src="${P(i)}" alt=""></button>`).join('')}</div>`)}
${fld('', '上架状态', `<div class="sf">${swHTML(true, '上架状态', 'data-sw')}</div>`)}
</div>
<aside class="pvw"><div class="pvh"><span>前台预览</span><span class="mut">商品卡</span></div>
<div class="pv" data-pv><div class="im"><img src="${P(PV_IMG[0])}" alt="" data-pimg><span class="off">已下架</span></div><div class="tx"><h4 data-pn></h4><p data-ps></p><div class="tgs" data-pt></div><div class="pc"><small>¥</small><b data-pp></b><s data-pm></s></div></div></div></aside>
</div>
<div class="ft"><button type="button" class="bt bt-s" data-cancel>取消</button><button type="button" class="bt bt-p" data-save>保存</button></div>
</div>`,
  js: H((root, B) => {
    const V = mkV(B, { name: (v) => (v ? '' : '请输入商品名称'), price: (v) => (/^\d+(\.\d{1,2})?$/.test(v) && +v > 0 ? '' : '请输入大于 0 的售价') })
    let tg = null
    const draw = () => {
      if (!tg) return
      const v = (s) => Q(B, s).value.trim(), pv = Q(B, '[data-pv]')
      Q(B, '[data-pn]').textContent = v('[data-f=name] .in') || '商品名称'
      Q(B, '[data-ps]').textContent = v('[data-sub]')
      const p = v('[data-price]'), m = v('[data-mkt]')
      Q(B, '[data-pp]').textContent = /^\d+(\.\d{1,2})?$/.test(p) ? p : '0'
      Q(B, '[data-pm]').textContent = /^\d+(\.\d{1,2})?$/.test(m) && +m > +p ? '¥' + m : ''
      Q(B, '[data-pt]').innerHTML = tg.tags().map((t) => `<span class="tag pri">${t}</span>`).join('')
      pv.classList.toggle('down', !Q(B, '.tgl').classList.contains('on'))
      Q(B, '[data-cnt]').textContent = `${v('[data-f=name] .in').length}/30`
    }
    tg = mkTags(Q(B, '[data-tags]'), { max: 3, len: 6, onChange: () => draw() })
    draw()
    B.addEventListener('input', draw)
    B.addEventListener('click', (e) => {
      const c = e.target.closest('[data-cv] button')
      if (c) { QA(B, '[data-cv] button').forEach((x) => { x.classList.toggle('on', x === c); x.setAttribute('aria-checked', x === c) }); Q(B, '[data-pimg]').src = P(+c.dataset.i) }
      const sw = e.target.closest('.tgl[data-sw]'); if (sw) { sw.classList.toggle('on'); sw.setAttribute('aria-checked', sw.classList.contains('on')); draw() }
      if (e.target.closest('[data-cancel]')) tst(B, '已取消，内容未保存')
    })
    B.addEventListener('click', async (e) => {
      const s = e.target.closest('[data-save]'); if (!s || s.classList.contains('ld')) return
      const bad = V.all(); if (bad.length) { tst(B, `有 ${bad.length} 项需要修改`, 'bad'); Q(bad[0].f, '.in').focus(); return }
      s.classList.add('ld'); await wait(700); s.classList.remove('ld'); tst(B, '商品已保存，前台已更新')
    })
  }),
})

guide('ad', 'FORM', [
  ['新建或编辑 5–8 个字段，或字段多到 10 个以上', '水平表单 / 分组卡片表单', '字段少用标签居左的水平表单；多了按主题分节可折叠，改了几项一眼可见'],
  ['有先后顺序、提交前要核对（创建优惠券、开通门店）', '分步表单', '一步只填一件事，最后一页汇总核对再提交，可回到某一步修改'],
  ['格式要求多、容易填错（企业认证、注册）', '失焦校验表单', '失焦才报错、改对即消，提交时汇总并定位第一个错误，不在输入中途报错'],
  ['条数不固定的子项，或名称加值成对的配置', '动态增减行 / 键值对编辑器', '一行一条，有上下限且删到下限写明原因；成对配置可切文本批量粘贴'],
  ['选一个关联对象还要现场新建，或只有一两个字段的小对象', '搜索新建弹层表单 / 行内小表单', '同一个居中对话框里搜与建，不跳页；小对象直接行内添加，点名字改名'],
  ['经营与通知设置，或要在前台展示的内容', '开关设置表单 / 带预览编辑表单', '开关即时生效且失败回滚，影响资金的先确认；展示类内容左填右看'],
  ['后台账号登录', '登录表单', '失败统一写“账号或密码错误”，密码框内有显示隐藏，提交即加载防重复'],
])

/* ================= AD-CTRL 基础控件 ================= */
/* 控件页共用：分区行（左侧小标题 + 右侧控件）和浮在上面的提示 */
const TIP_CSS = (q) => `
${q} .tp{position:relative;display:inline-flex}
${q} .tp::after{content:attr(data-tip);position:absolute;left:50%;bottom:calc(100% + 6px);z-index:40;padding:4px 8px;border-radius:4px;background:color-mix(in srgb,var(--inv) 92%,transparent);color:#fff;font-size:12px;line-height:18px;font-weight:400;white-space:nowrap;opacity:0;pointer-events:none;transform:translate(-50%,2px);transition:opacity .15s,transform .15s}
${q} .tp:hover::after,${q} .tp:focus-within::after{opacity:1;transform:translate(-50%,0)}
`
const SC_CSS = (q) => `
${q}{padding:4px 24px}
${q} .sc{display:grid;grid-template-columns:104px minmax(0,1fr);gap:0 16px;padding:16px 0;border-bottom:1px solid var(--line)}
${q} .sc:last-child{border-bottom:0}
${q} .sc>h4{margin:0;padding-top:5px;font-size:14px;line-height:22px;font-weight:600;color:var(--ink2)}
${q} .rw2{display:flex;flex-wrap:wrap;align-items:center;gap:12px 16px}
${q} .cap{display:flex;flex-direction:column;align-items:center;gap:6px}
${q} .cap small{font-size:12px;line-height:18px;color:var(--ink3)}
${TIP_CSS(q)}
@media(max-width:520px){${q}{padding:4px 16px}${q} .sc{grid-template-columns:minmax(0,1fr);gap:8px}${q} .sc>h4{padding-top:0}}
`

/* ---------- AD-CTRL-001 按钮体系 ---------- */
def({
  id: 'AD-CTRL-001', name: '按钮体系', style: '主次文字危险',
  fit: '定下后台所有按钮的层级、尺寸与状态：一屏一个主按钮，次按钮做可逆动作，文字按钮放表格行内，危险按钮先确认',
  avoid: '一屏出现两个主按钮；用“确定”做危险按钮的文案；禁用按钮不写原因；危险按钮放在操作组第一个',
  kw: 'button 按钮 主按钮 次按钮 文字按钮 危险按钮 加载 禁用 尺寸 32',
  css: K('adctrl001', { w: 680 }) + SC_CSS('.adctrl001') + `
.adctrl001 .bt-s36{height:36px;padding:0 18px}
.adctrl001 .bt-i{width:32px;padding:0}
.adctrl001 .bt.hv.bt-p{box-shadow:inset 0 0 0 99px rgba(255,255,255,.12)}
.adctrl001 .bt.pr.bt-p{background:var(--pd);transform:translateY(1px)}
.adctrl001 .grp{display:flex;flex-wrap:wrap;gap:12px 24px}
.adctrl001 .grp>div{display:flex;gap:8px}
.adctrl001 .grp .bt{min-width:84px}
.adctrl001 .pcw{position:relative;display:inline-flex}
.adctrl001 .pc{position:absolute;right:0;bottom:calc(100% + 8px);z-index:30;width:272px;padding:12px 14px 12px;border:1px solid var(--bd0);border-radius:12px;background:var(--card);box-shadow:var(--sh3);animation:admdl .18s cubic-bezier(.2,0,0,1)}
.adctrl001 .pc p{margin:0 0 10px;color:var(--ink)}
.adctrl001 .pc p b{font-weight:600}
.adctrl001 .pc .a{display:flex;justify-content:flex-end;gap:8px}
.adctrl001 .pc .bt{height:28px;padding:0 12px}`,
  html: () => `<div class="adctrl001">
<div class="sc"><h4>类型</h4><div class="rw2"><button type="button" class="bt bt-p">主按钮</button><button type="button" class="bt bt-s">次按钮</button><button type="button" class="bt bt-t">文字按钮</button><button type="button" class="bt bt-d">危险按钮</button><button type="button" class="bt bt-dt">危险（次要）</button></div></div>
<div class="sc"><h4>尺寸</h4><div class="rw2"><div class="cap"><button type="button" class="bt bt-p">保存</button><small>32 · 表格与工具栏</small></div><div class="cap"><button type="button" class="bt bt-p bt-s36">保存</button><small>36 · 表单</small></div><div class="cap"><button type="button" class="bt bt-p bt-lg">保存</button><small>40 · 登录与大屏</small></div></div></div>
<div class="sc"><h4>带图标</h4><div class="rw2"><button type="button" class="bt bt-p">${ic('plus')}新增会员</button><button type="button" class="bt bt-s">${ic('download')}导出</button><button type="button" class="bt bt-s">${ic('refresh')}刷新</button><span class="tp" data-tip="编辑"><button type="button" class="bt bt-s bt-i" aria-label="编辑">${ic('edit')}</button></span><span class="tp" data-tip="复制"><button type="button" class="bt bt-s bt-i" aria-label="复制">${ic('copy')}</button></span><span class="tp" data-tip="更多"><button type="button" class="bt bt-s bt-i" aria-label="更多">${ic('more')}</button></span></div></div>
<div class="sc"><h4>状态</h4><div class="rw2"><div class="cap"><button type="button" class="bt bt-p">提交</button><small>默认</small></div><div class="cap"><button type="button" class="bt bt-p hv">提交</button><small>悬停</small></div><div class="cap"><button type="button" class="bt bt-p pr">提交</button><small>按下</small></div><div class="cap"><button type="button" class="bt bt-p ld" aria-busy="true">提交</button><small>加载中</small></div><div class="cap"><span class="tp" data-tip="仅店长可导出订单"><button type="button" class="bt bt-p dis" aria-disabled="true">提交</button></span><small>禁用</small></div></div></div>
<div class="sc"><h4>点击试试</h4><div class="rw2"><button type="button" class="bt bt-p" data-demo="ok">保存</button><button type="button" class="bt bt-s" data-demo="fail">提交审核</button></div></div>
<div class="sc"><h4>按钮组</h4><div class="grp"><div><button type="button" class="bt bt-s">取消</button><button type="button" class="bt bt-p">保存</button></div><div><button type="button" class="bt bt-s">保留</button><span class="pcw"><button type="button" class="bt bt-d" data-pc aria-haspopup="dialog">删除订单</button><div class="pc" role="alertdialog" aria-label="确认删除" hidden><p>删除订单 <b>SO2026110512</b> 后无法恢复，已付款项将原路退回。</p><div class="a"><button type="button" class="bt bt-s" data-pcx>保留</button><button type="button" class="bt bt-d" data-pcok>删除订单</button></div></div></span></div></div></div>
</div>`,
  js: H((root, B) => {
    B.addEventListener('click', async (e) => {
      const d = e.target.closest('[data-demo]')
      if (d && !d.classList.contains('ld')) {
        d.classList.add('ld'); d.setAttribute('aria-busy', 'true'); await wait(d.dataset.demo === 'fail' ? 1000 : 900); d.classList.remove('ld'); d.removeAttribute('aria-busy')
        if (d.dataset.demo === 'fail') tst(B, '提交失败：库存不足，已保留填写内容', 'bad'); else tst(B, '已保存')
      }
      const pc = e.target.closest('[data-pc]')
      if (pc) { const p = Q(pc.parentNode, '.pc'); p.hidden = !p.hidden; if (!p.hidden) Q(p, '[data-pcx]').focus() }
      if (e.target.closest('[data-pcx]')) { const p = e.target.closest('.pc'); p.hidden = true; Q(p.parentNode, '[data-pc]').focus() }
      if (e.target.closest('[data-pcok]')) { const p = e.target.closest('.pc'); p.hidden = true; tst(B, '订单已删除') }
    })
    B.addEventListener('focusout', (e) => { const w = e.target.closest('.pcw'); if (w && !w.contains(e.relatedTarget)) Q(w, '.pc').hidden = true })
    B.addEventListener('keydown', (e) => { if (e.key === 'Escape') { const p = e.target.closest('.pc'); if (p) { p.hidden = true; Q(p.parentNode, '[data-pc]').focus() } } })
  }),
})

/* ---------- AD-CTRL-002 开关 ---------- */
def({
  id: 'AD-CTRL-002', name: '开关', style: '即时生效',
  fit: '只用于“立即生效”的二元设置：自动接单、上下架、通知；点一下先切换，请求中显示加载，失败自动回滚并在原位写原因',
  avoid: '开关后面再放“保存”按钮；需要二次确认的重要改动（用确认框）；多选一或选项超过两个的场景',
  kw: 'switch toggle 开关 即时生效 加载 回滚 禁用 开 关 自动接单',
  css: K('adctrl002', { w: 640 }) + SC_CSS('.adctrl002') + `
.adctrl002 .tgl.sm{width:28px;height:16px;border-radius:999px}
.adctrl002 .tgl.sm i{width:12px;height:12px}
.adctrl002 .tgl.sm.on i{transform:translateX(12px)}
.adctrl002 .tgl.sm.ld i::after{inset:2px;border-width:1.5px}
.adctrl002 .lines{display:flex;flex-direction:column;gap:0;width:100%}
.adctrl002 .ln{display:flex;align-items:center;gap:16px;padding:12px 0;border-bottom:1px solid var(--line)}
.adctrl002 .ln:first-child{padding-top:0}
.adctrl002 .ln:last-child{border-bottom:0;padding-bottom:0}
.adctrl002 .ln .tx{flex:1;min-width:0}
.adctrl002 .ln b{display:block;font-weight:600}
.adctrl002 .ln .ds{display:block;font-size:12px;line-height:18px;color:var(--ink3)}
.adctrl002 .ln .rs{display:none;margin-top:4px;font-style:normal;font-size:12px;line-height:18px;color:var(--dg)}
.adctrl002 .ln.err .rs{display:block}`,
  html: () => `<div class="adctrl002">
<div class="sc"><h4>状态</h4><div class="rw2"><div class="cap">${swHTML(false, '关闭', 'data-sw="plain"', false)}<small>关</small></div><div class="cap">${swHTML(true, '开启', 'data-sw="plain"', false)}<small>开</small></div><div class="cap">${swHTML(true, '带文字', 'data-sw="plain"')}<small>附文字</small></div></div></div>
<div class="sc"><h4>尺寸</h4><div class="rw2"><div class="cap"><button type="button" class="tgl on" role="switch" aria-checked="true" aria-label="默认" data-sw="plain"><i></i></button><small>默认 36×20</small></div><div class="cap"><button type="button" class="tgl sm on" role="switch" aria-checked="true" aria-label="小号" data-sw="plain"><i></i></button><small>小 28×16</small></div></div></div>
<div class="sc"><h4>加载与禁用</h4><div class="rw2"><div class="cap"><button type="button" class="tgl on ld" role="switch" aria-checked="true" aria-label="加载中" aria-busy="true"><i></i></button><small>加载中</small></div><div class="cap"><span class="tp" data-tip="仅店长可修改"><button type="button" class="tgl dis" role="switch" aria-checked="false" aria-disabled="true" aria-label="禁用关闭"><i></i></button></span><small>禁用·关</small></div><div class="cap"><span class="tp" data-tip="仅店长可修改"><button type="button" class="tgl dis on" role="switch" aria-checked="true" aria-disabled="true" aria-label="禁用开启"><i></i></button></span><small>禁用·开</small></div></div></div>
<div class="sc"><h4>设置行</h4><div class="lines">
<div class="ln" data-row><div class="tx"><b>自动接单</b><span class="ds">新订单自动确认，无需店员手动点击</span><em class="rs" data-reason role="alert"></em></div>${swHTML(true, '自动接单', 'data-sw="async"')}</div>
<div class="ln" data-row><div class="tx"><b>短信通知</b><span class="ds">订单状态变化时短信通知顾客</span><em class="rs" data-reason role="alert"></em></div>${swHTML(false, '短信通知', 'data-sw="fail"')}</div>
</div></div>
</div>`,
  js: H((root, B) => {
    B.addEventListener('click', async (e) => {
      const sw = e.target.closest('.tgl[data-sw]'); if (!sw || sw.classList.contains('ld')) return
      const mode = sw.dataset.sw, was = sw.classList.contains('on'), row = sw.closest('[data-row]'), rs = row && Q(row, '[data-reason]')
      if (row) { row.classList.remove('err'); rs.textContent = '' }
      sw.classList.toggle('on', !was); sw.setAttribute('aria-checked', !was)
      if (mode === 'plain') return
      sw.classList.add('ld'); sw.setAttribute('aria-busy', 'true'); await wait(700); sw.classList.remove('ld'); sw.removeAttribute('aria-busy')
      if (mode === 'fail' && !sw.dataset.tried) { sw.dataset.tried = '1'; sw.classList.toggle('on', was); sw.setAttribute('aria-checked', was); row.classList.add('err'); rs.textContent = `保存失败：网络连接中断，已恢复为${was ? '开启' : '关闭'}，请重试`; return }
      tst(B, `${Q(row, '.tx b').textContent}已${was ? '关闭' : '开启'}`)
    })
  }),
})

/* ---------- AD-CTRL-003 单选与多选 ---------- */
def({
  id: 'AD-CTRL-003', name: '单选与多选', style: '选项组卡片',
  fit: '选项不到 5 个时用单选或分段；多选要全选与已选数量；套餐、方案这类要比较说明的选项用卡片式',
  avoid: '选项超过 5 个（改用下拉）；开关能表达的二元设置不要用单选；卡片式选项不要塞长段说明',
  kw: 'radio checkbox 单选 多选 全选 半选 分段控件 卡片选项 选项组 segmented',
  css: K('adctrl003', { w: 680 }) + SC_CSS('.adctrl003') + `
.adctrl003 .rg{display:flex;flex-wrap:wrap;align-items:center;gap:8px 24px;min-height:32px}
.adctrl003 .sgm{position:relative;display:inline-flex;padding:2px;border-radius:8px;background:var(--soft)}
.adctrl003 .sgm .th{position:absolute;left:0;top:2px;bottom:2px;width:0;border-radius:8px;background:var(--card);box-shadow:0 1px 2px var(--sh14);transition:transform .2s cubic-bezier(.2,0,0,1),width .2s cubic-bezier(.2,0,0,1)}
.adctrl003 .sgm button{position:relative;z-index:1;height:28px;padding:0 16px;border-radius:8px;font-weight:600;color:var(--ink2);transition:color .15s}
.adctrl003 .sgm button.on{color:var(--ink)}
.adctrl003 .sgm button:focus:not(:focus-visible){outline:0}
.adctrl003 .sgm button:focus-visible{outline:2px solid var(--ink2);outline-offset:1px}
.adctrl003 .cnt2{margin-left:4px;color:var(--ink3);font-size:12px}
.adctrl003 .cds{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:12px;width:100%}
.adctrl003 .oc{position:relative;display:flex;flex-direction:column;align-items:flex-start;gap:2px;padding:12px 14px;border-radius:12px;background:var(--card);box-shadow:inset 0 0 0 1px var(--bd);text-align:left;transition:box-shadow .15s,background-color .15s}
.adctrl003 .oc:hover{box-shadow:inset 0 0 0 1px var(--bd2)}
.adctrl003 .oc b{font-weight:600}
.adctrl003 .oc em{font-style:normal;font-size:16px;line-height:24px;font-weight:600;color:var(--ink);font-variant-numeric:tabular-nums}
.adctrl003 .oc .ds{font-size:12px;line-height:18px;color:var(--ink3)}
.adctrl003 .oc.on{background:var(--pt);box-shadow:inset 0 0 0 2px var(--p)}
.adctrl003 .oc.on::after{content:"";position:absolute;right:10px;top:10px;width:16px;height:16px;border-radius:50%;background:var(--p) url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='none' stroke='white' stroke-width='3.2' stroke-linecap='round' stroke-linejoin='round'%3E%3Cpath d='m5 12.5 5 5L19.5 7'/%3E%3C/svg%3E") center/11px no-repeat}
.adctrl003 .oc:focus:not(:focus-visible){outline:0}
.adctrl003 .oc:focus-visible{outline:2px solid var(--ink2);outline-offset:2px}
@media(max-width:560px){.adctrl003 .cds{grid-template-columns:minmax(0,1fr)}}`,
  html: () => `<div class="adctrl003">
<div class="sc"><h4>单选组</h4><div class="rg" data-ix="radio" role="radiogroup" aria-label="配送方式"><button type="button" class="rd on" data-o role="radio" aria-checked="true"><i></i>快递</button><button type="button" class="rd" data-o role="radio" aria-checked="false"><i></i>同城配送</button><button type="button" class="rd" data-o role="radio" aria-checked="false"><i></i>到店自提</button><button type="button" class="rd dis" data-o role="radio" aria-checked="false" aria-disabled="true" title="该门店未开通"><i></i>跨境直邮</button></div></div>
<div class="sc"><h4>分段控件</h4><div class="sgm" data-seg role="radiogroup" aria-label="统计周期"><i class="th"></i><button type="button" class="on" role="radio" aria-checked="true">日</button><button type="button" role="radio" aria-checked="false">周</button><button type="button" role="radio" aria-checked="false">月</button><button type="button" role="radio" aria-checked="false">年</button></div></div>
<div class="sc"><h4>多选与全选</h4><div data-ix="checks"><div class="rg"><button type="button" class="cb" data-all role="checkbox" aria-checked="false"><i></i>全选<span class="cnt2">已选 <span data-count>0</span>/4</span></button></div><div class="rg" style="margin-top:8px"><button type="button" class="cb on" data-c role="checkbox" aria-checked="true"><i></i>订单提醒</button><button type="button" class="cb on" data-c role="checkbox" aria-checked="true"><i></i>库存预警</button><button type="button" class="cb" data-c role="checkbox" aria-checked="false"><i></i>售后申请</button><button type="button" class="cb" data-c role="checkbox" aria-checked="false"><i></i>评价提醒</button></div></div></div>
<div class="sc"><h4>限选数量</h4><div class="rg" data-max="2"><button type="button" class="cb on" role="checkbox" aria-checked="true" data-m><i></i>短信</button><button type="button" class="cb on" role="checkbox" aria-checked="true" data-m><i></i>邮件</button><button type="button" class="cb" role="checkbox" aria-checked="false" data-m><i></i>站内信</button><button type="button" class="cb" role="checkbox" aria-checked="false" data-m><i></i>企业微信</button><span class="mut">最多选 2 项</span></div></div>
<div class="sc"><h4>卡片选项</h4><div class="cds" data-ix="radio" role="radiogroup" aria-label="套餐"><button type="button" class="oc" data-o role="radio" aria-checked="false"><b>基础版</b><em>¥99 / 月</em><span class="ds">1 家门店</span></button><button type="button" class="oc on" data-o role="radio" aria-checked="true"><b>专业版</b><em>¥299 / 月</em><span class="ds">最多 5 家门店</span></button><button type="button" class="oc" data-o role="radio" aria-checked="false"><b>旗舰版</b><em>¥699 / 月</em><span class="ds">不限门店，含数据分析</span></button></div></div>
</div>`,
  js: H((root, B) => {
    const seg = Q(B, '[data-seg]'), th = Q(seg, '.th')
    const place = () => { const on = Q(seg, '.on'); if (on) { th.style.width = on.offsetWidth + 'px'; th.style.transform = `translateX(${on.offsetLeft}px)` } }
    requestAnimationFrame(place); setTimeout(place, 120)
    seg.addEventListener('click', (e) => { const b = e.target.closest('button'); if (!b) return; QA(seg, 'button').forEach((x) => { x.classList.toggle('on', x === b); x.setAttribute('aria-checked', x === b) }); place() })
    seg.addEventListener('keydown', (e) => { if (e.key === 'ArrowRight' || e.key === 'ArrowLeft') { const bs = QA(seg, 'button'), i = bs.findIndex((x) => x.classList.contains('on')), n = bs[(i + (e.key === 'ArrowRight' ? 1 : bs.length - 1)) % bs.length]; n.click(); n.focus() } })
    const mx = Q(B, '[data-max]')
    mx.addEventListener('click', (e) => {
      const c = e.target.closest('[data-m]'); if (!c) return
      if (!c.classList.contains('on') && QA(mx, '.cb.on').length >= 2) { tst(B, '最多选 2 项', 'bad'); return }
      c.classList.toggle('on')
    })
  }),
})

/* ---------- AD-CTRL-004 下拉选择器 ---------- */
const SEL_STORES = ['静安旗舰店', '徐汇中心店', '浦东新区店', '杭州西湖体验店（含周末夜场）', '苏州观前街店', ['南京路店', '已停业，不可选']]
const SEL_CATS = ['数码配件', '家居日用', '服饰鞋包', '食品饮料', '美妆个护', '母婴玩具', '运动户外', '宠物用品', '图书文娱', '汽车用品', '办公文具', '厨房小电', '床上用品', '箱包皮具']
const selOpts = (arr) => arr.map((x) => (Array.isArray(x) ? `<div class="op dis" role="option" aria-disabled="true" data-v="${x[0]}" title="${x[1]}"><span class="ot">${x[0]}</span></div>` : `<div class="op" role="option" data-v="${x}"><span class="ot">${x}</span></div>`)).join('')
/* 下拉：单选（可清除）/ 可搜索 / 多选标签。键盘：上下选、回车确认、Esc 关闭 */
const mkSelect = (el, o = {}) => {
  const mode = el.dataset.sel, tr = Q(el, '.sel'), menu = Q(el, '.menu'), list = Q(el, '.opl'), search = Q(el, '.srq')
  const ph = o.ph || '请选择'; let vals = (o.init || []).slice(), hv = -1
  const opts = () => QA(list, '.op').filter((x) => !x.hidden)
  const drawTr = () => {
    const html = mode === 'multi'
      ? (vals.length ? vals.slice(0, 2).map((v) => `<span class="tag pri" data-tv="${v}">${v}<button type="button" class="x" data-rm="${v}" aria-label="移除 ${v}">${ic('close')}</button></span>`).join('') + (vals.length > 2 ? `<span class="tag">+${vals.length - 2}</span>` : '') : `<span class="pl2">${ph}</span>`)
      : (vals.length ? `<span class="v">${vals[0]}</span>` : `<span class="pl2">${ph}</span>`)
    Q(tr, '.vs').innerHTML = html
    const clr = Q(tr, '[data-clear]'); if (clr) clr.hidden = mode === 'multi' || !vals.length
    QA(list, '.op').forEach((x) => { const on = vals.includes(x.dataset.v); x.classList.toggle('on', on); x.setAttribute('aria-selected', on) })
    const ft = Q(menu, '.mf'); if (ft) { Q(ft, '[data-n]').textContent = vals.length }
    tr.classList.toggle('has', vals.length > 0)
  }
  const hl = (i) => { const os = opts(); QA(list, '.op.hv').forEach((x) => x.classList.remove('hv')); hv = Math.max(0, Math.min(os.length - 1, i)); if (os[hv]) { os[hv].classList.add('hv'); os[hv].scrollIntoView({ block: 'nearest' }) } }
  const open = () => { el.classList.add('open'); menu.hidden = false; tr.setAttribute('aria-expanded', 'true'); if (search) { search.value = ''; filter(); setTimeout(() => search.focus(), 0) } const on = Q(list, '.op.on:not([hidden])'); hl(on ? opts().indexOf(on) : 0) }
  const close = () => { el.classList.remove('open'); menu.hidden = true; tr.setAttribute('aria-expanded', 'false') }
  const filter = () => {
    const s = search ? search.value.trim() : ''; let n = 0
    QA(list, '.op').forEach((x) => { const v = x.dataset.v, hit = !s || v.includes(s); x.hidden = !hit; if (hit) { n++; Q(x, '.ot').innerHTML = s ? v.replace(s, `<mark>${s}</mark>`) : v } })
    Q(menu, '.nom2').hidden = n > 0; hl(0)
  }
  const pick = (x) => {
    if (!x || x.classList.contains('dis')) return
    const v = x.dataset.v
    if (mode === 'multi') { vals = vals.includes(v) ? vals.filter((y) => y !== v) : [...vals, v] } else { vals = [v]; close(); tr.focus() }
    drawTr(); o.onChange && o.onChange(vals)
  }
  tr.addEventListener('click', (e) => {
    const rm = e.target.closest('[data-rm]'); if (rm) { vals = vals.filter((y) => y !== rm.dataset.rm); drawTr(); o.onChange && o.onChange(vals); e.stopPropagation(); return }
    if (e.target.closest('[data-clear]')) { vals = []; drawTr(); o.onChange && o.onChange(vals); e.stopPropagation(); return }
    el.classList.contains('open') ? close() : open()
  })
  menu.addEventListener('mousedown', (e) => { if (!e.target.closest('input')) e.preventDefault() })
  tr.addEventListener('mousedown', (e) => { if (e.target.closest('[data-rm],[data-clear]')) e.preventDefault() })
  list.addEventListener('click', (e) => pick(e.target.closest('.op')))
  list.addEventListener('mousemove', (e) => { const x = e.target.closest('.op'); if (x && !x.classList.contains('hv')) { QA(list, '.op.hv').forEach((y) => y.classList.remove('hv')); x.classList.add('hv'); hv = opts().indexOf(x) } })
  if (search) search.addEventListener('input', filter)
  const ft = Q(menu, '.mf'); if (ft) ft.addEventListener('click', (e) => { if (e.target.closest('[data-all0]')) { vals = []; drawTr(); o.onChange && o.onChange(vals) } })
  el.addEventListener('keydown', (e) => {
    const isOpen = el.classList.contains('open')
    if (e.key === 'ArrowDown' || e.key === 'ArrowUp') { e.preventDefault(); if (!isOpen) open(); else hl(hv + (e.key === 'ArrowDown' ? 1 : -1)) }
    else if (e.key === 'Enter' && isOpen) { e.preventDefault(); pick(opts()[hv]) }
    else if ((e.key === 'Enter' || e.key === ' ') && !isOpen && e.target === tr) { e.preventDefault(); open() }
    else if (e.key === 'Escape' && isOpen) { e.stopPropagation(); close(); tr.focus() }
  })
  el.addEventListener('focusout', (e) => { if (!el.contains(e.relatedTarget)) close() })
  drawTr()
  return { get: () => vals.slice(), set: (v) => { vals = v; drawTr() } }
}
const selHTML = (mode, id, opts, label, o = {}) => `<div class="f"><label class="lb" id="${id}-l">${label}</label><div class="sx2" data-sel="${mode}"><div class="in sel${mode === 'multi' ? ' mtg' : ''}" role="combobox" tabindex="0" aria-haspopup="listbox" aria-expanded="false" aria-labelledby="${id}-l"><span class="vs"></span>${mode === 'multi' ? '' : `<button type="button" class="ib clr" data-clear aria-label="清除" title="清除" hidden>${ic('closec')}</button>`}${ic('down')}</div>
<div class="menu" hidden>${mode === 'search' ? `<div class="sq"><div class="ig"><span class="pf">${sv('search')}</span><input class="in srq" aria-label="搜索${label}" placeholder="搜索${label}"></div></div>` : ''}<div class="opl" role="listbox" ${mode === 'multi' ? 'aria-multiselectable="true"' : ''}>${selOpts(opts)}</div>${mode === 'search' ? '<div class="nom2" hidden>没有匹配的分类，换个关键词试试</div>' : ''}${mode === 'multi' ? `<div class="mf"><span>已选 <b data-n>0</b> 项</span><button type="button" class="lnk" data-all0>清空</button></div>` : ''}</div></div></div>`
def({
  id: 'AD-CTRL-004', name: '下拉选择器', style: '单选搜索多选',
  fit: '选项 5 个以上用下拉：少量单选直接点；超过 10 个带搜索；可见范围、标签这类多选用标签展示并折叠',
  avoid: '选项少于 5 个（改用单选或分段，少点一次）；长列表不带搜索；多选标签不限显示个数会撑破表单',
  kw: 'select dropdown 下拉 选择器 单选 多选 标签 搜索 可搜索 清除',
  wide: true,
  css: K('adctrl004', { w: 1000 }) + TAGI_CSS('.adctrl004') + `
.adctrl004{padding:20px 24px 24px;min-height:420px}
.adctrl004 .g3{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:0 24px}
.adctrl004 .sx2{position:relative}
.adctrl004 .sel .vs{display:flex;align-items:center;flex:1;gap:4px;min-width:0;overflow:hidden}
.adctrl004 .sel .v{overflow:hidden;text-overflow:ellipsis;white-space:nowrap}
.adctrl004 .sel .pl2{color:var(--ink3)}
.adctrl004 .sel.mtg{height:auto;min-height:32px;padding:3px 8px 3px 6px;line-height:24px}
.adctrl004 .sel .tag{height:24px;padding:0 3px 0 8px;font-size:12px;max-width:100%}
.adctrl004 .sel .tag .x{display:inline-flex;align-items:center;justify-content:center;width:18px;height:18px;border-radius:4px;color:inherit}
.adctrl004 .sel .tag .x:hover{background:var(--veil08)}
.adctrl004 .sel .tag .x .ic{width:12px;height:12px}
.adctrl004 .sel .clr{width:20px;height:20px;margin:0 2px 0 0;color:var(--ink3)}
.adctrl004 .sel .clr .ic{width:14px;height:14px;transition:none;transform:none}
.adctrl004 .sel:focus{outline:0}
.adctrl004 .sel:focus-visible{outline:2px solid var(--ink2);outline-offset:2px}
.adctrl004 .sx2.open .sel{border-color:var(--ink2)}
.adctrl004 .sx2.open .sel>.ic{transform:rotate(180deg)}
.adctrl004 .menu{position:absolute;left:0;right:0;top:calc(100% + 6px);z-index:25;padding:4px}
.adctrl004 .menu[hidden]{display:none}
.adctrl004 .opl{max-height:204px;overflow:auto}
.adctrl004 .sq{padding:4px 4px 6px}
.adctrl004 .op.hv{background:var(--mub)}
.adctrl004 .op.on{background:var(--pt);color:var(--p-text);font-weight:600}
.adctrl004 .op.on::after{content:"";width:5px;height:9px;margin:0 3px 3px 0;border:solid var(--pd);border-width:0 2px 2px 0;transform:rotate(45deg);flex:none}
.adctrl004 .op.dis{color:var(--ink4);cursor:not-allowed;background:none}
.adctrl004 .op .ot{min-width:0;overflow:hidden;text-overflow:ellipsis;white-space:nowrap}
.adctrl004 .op mark{background:none;color:var(--p-text);font-weight:600}
.adctrl004 .nom2{padding:16px 10px;text-align:center;color:var(--ink3)}
.adctrl004 .mf{display:flex;align-items:center;justify-content:space-between;margin-top:4px;padding:6px 10px 2px;border-top:1px solid var(--line);color:var(--ink2)}
.adctrl004 .mf .lnk{color:var(--p-text);font-size:14px}
.adctrl004 .mf .lnk:hover{text-decoration:underline}
@media(max-width:860px){.adctrl004 .g3{grid-template-columns:minmax(0,1fr)}.adctrl004 .f{margin-bottom:14px}.adctrl004{min-height:560px}}`,
  html: () => `<div class="adctrl004"><div class="g3">
${selHTML('single', 'sa', SEL_STORES, '所属门店')}
${selHTML('search', 'sb', SEL_CATS, '商品分类')}
${selHTML('multi', 'sc', SEL_STORES.slice(0, 5), '可见门店')}
</div></div>`,
  js: H((root, B) => {
    const g = (m) => Q(B, `[data-sel=${m}]`)
    mkSelect(g('single'), { ph: '请选择门店', init: ['徐汇中心店'] })
    mkSelect(g('search'), { ph: '请选择分类' })
    mkSelect(g('multi'), { ph: '请选择可见门店', init: ['静安旗舰店', '徐汇中心店', '浦东新区店'] })
  }),
})

/* ---------- 日历共用：样式、月份格子、状态涂色 ---------- */
const WK = ['一', '二', '三', '四', '五', '六', '日']
const CAL_CSS = (q) => `
${q} .dtw{position:relative}
${q} .dtw .ig .in{cursor:pointer}
${q} .dtw .clr{width:20px;height:20px;margin-right:6px;color:var(--ink3)}
${q} .dtw .clr .ic{width:14px;height:14px}
${q} .dtw.open .ig{border-color:var(--ink2)}
${q} .pop{position:absolute;left:0;top:calc(100% + 6px);z-index:25;width:max-content;max-width:calc(100vw - 32px);padding:12px;border:1px solid var(--bd0);border-radius:12px;background:var(--card2);box-shadow:var(--sh3);animation:admdl .18s cubic-bezier(.2,0,0,1)}
${q} .pop[hidden]{display:none}
${q} .ch{display:flex;align-items:center;justify-content:space-between;height:32px;margin-bottom:4px}
${q} .ch b{font-weight:600;font-variant-numeric:tabular-nums}
${q} .ch button{display:inline-flex;align-items:center;justify-content:center;width:28px;height:28px;border-radius:4px;color:var(--ink2)}
${q} .ch button:hover{background:var(--mub)}
${q} .ch button .ic{width:16px;height:16px}
${q} .ch button:focus:not(:focus-visible){outline:0}
${q} .ch button:focus-visible{outline:2px solid var(--ink2);outline-offset:1px}
${q} .cal{width:252px}
${q} .cw,${q} .cg{display:grid;grid-template-columns:repeat(7,1fr)}
${q} .cw span{display:flex;align-items:center;justify-content:center;height:28px;font-size:12px;color:var(--ink3)}
${q} .cg{row-gap:2px}
${q} .d{position:relative;display:flex;align-items:center;justify-content:center;height:32px;font-variant-numeric:tabular-nums}
${q} .d::before{content:"";position:absolute;left:0;right:0;top:2px;bottom:2px}
${q} .d i{position:relative;z-index:1;display:flex;align-items:center;justify-content:center;width:28px;height:28px;border-radius:8px;font-style:normal;transition:background-color .12s}
${q} .d:hover i{background:var(--mub)}
${q} .d.out i{color:var(--ink4)}
${q} .d.today i{box-shadow:inset 0 0 0 1px var(--p)}
${q} .d.rn::before{background:var(--pt)}
${q} .d.rs::before{left:50%;background:var(--pt)}
${q} .d.re::before{right:50%;background:var(--pt)}
${q} .d.rs.re::before{background:none}
${q} .d.sel i,${q} .d.sel:hover i{background:var(--p);color:#fff;font-weight:600;box-shadow:none}
${q} .d.dis{cursor:not-allowed}
${q} .d.dis i,${q} .d.dis:hover i{background:none;color:var(--ink6);box-shadow:none}
${q} .d.hid{visibility:hidden}
${q} .d:focus{outline:0}
${q} .d:focus-visible i{outline:2px solid var(--ink2);outline-offset:1px}
${q} .cf2{display:flex;align-items:center;justify-content:space-between;gap:8px;margin-top:8px;padding-top:8px;border-top:1px solid var(--line)}
${q} .cf2 .lnk{color:var(--p-text);font-size:14px;border-radius:4px}
${q} .cf2 .lnk:hover{text-decoration:underline;text-underline-offset:3px}
${q} .cf2 .lnk.dis{color:color-mix(in srgb,var(--ink6) 56%,var(--ink5));cursor:not-allowed;text-decoration:none}
${q} .cf2 .bt{height:28px;padding:0 12px}
`
const calMonthHTML = (y, m, hideOut) => {
  const off = (new Date(y, m, 1).getDay() + 6) % 7
  let cells = ''
  for (let i = 0; i < 42; i++) {
    const d = new Date(y, m, 1 - off + i), s = ymd(d), out = d.getMonth() !== m
    cells += `<button type="button" class="d${out ? (hideOut ? ' out hid' : ' out') : ''}${s === TODAY ? ' today' : ''}" data-date="${s}" tabindex="-1" aria-label="${s}"><i>${d.getDate()}</i></button>`
  }
  return `<div class="cal"><div class="cw">${WK.map((w) => `<span>${w}</span>`).join('')}</div><div class="cg">${cells}</div></div>`
}
const paintCal = (scope, st) => QA(scope, '.d').forEach((x) => {
  const s = x.dataset.date; let lo = '', hi = ''
  if (st.a) { const b = st.b || (st.hover && st.hover !== st.a ? st.hover : st.a); lo = st.a < b ? st.a : b; hi = st.a < b ? b : st.a }
  const dis = (st.min && s < st.min) || (st.max && s > st.max)
  const hid = x.classList.contains('hid')
  x.classList.toggle('sel', st.a ? !hid && (s === lo || s === hi) : s === st.v)
  x.classList.toggle('rn', !hid && !!lo && s > lo && s < hi)
  x.classList.toggle('rs', !hid && !!lo && s === lo && lo !== hi)
  x.classList.toggle('re', !hid && !!lo && s === hi && lo !== hi)
  x.classList.toggle('dis', !!dis); x.setAttribute('aria-disabled', !!dis)
})
const monthTitle = (y, m) => `${y} 年 ${m + 1} 月`
const navHTML = (title, dbl = true) => `<div class="ch">${dbl ? `<button type="button" data-nav="-12" aria-label="上一年">${ic('adf_ll')}</button>` : ''}<button type="button" data-nav="-1" aria-label="上个月">${ic('left')}</button><b>${title}</b><button type="button" data-nav="1" aria-label="下个月">${ic('right')}</button>${dbl ? `<button type="button" data-nav="12" aria-label="下一年">${ic('adf_rr')}</button>` : ''}</div>`
const dateFieldHTML = (key, label, ph, value, extra = '') => `<div class="f" data-f="${key}"><label class="lb" for="${key}-i">${label}</label><div class="ctl"><div class="dtw" data-dt="${key}" ${extra}><div class="ig"><span class="pf">${sv('calendar')}</span><input class="in" id="${key}-i" placeholder="${ph}" value="${value}" autocomplete="off" inputmode="numeric"><button type="button" class="ib clr" data-clear aria-label="清除" title="清除" ${value ? '' : 'hidden'}>${ic('closec')}</button></div><div class="pop" hidden></div></div><span class="er" role="alert"></span></div></div>`

/* 单个日期（可带时间）：点选、手输、今天、最小日期 */
const mkDate = (w, o = {}) => {
  const f = w.closest('[data-f]'), inp = Q(w, '.in'), pop = Q(w, '.pop'), er = Q(f, '.er'), clr = Q(w, '[data-clear]')
  const fmt = o.time ? /^(\d{4}-\d{2}-\d{2}) (\d{2}):(\d{2})$/ : /^\d{4}-\d{2}-\d{2}$/
  let val = '', y = 2026, m = 10, pend = '', hh = '09', mm = '00'
  const setErr = (t) => { f.classList.toggle('bad', !!t); er.textContent = t }
  const split = (s) => { const t = o.time ? fmt.exec(s) : null; return o.time ? (t ? [t[1], t[2], t[3]] : null) : (parseD(s) ? [s] : null) }
  const set = (s) => { val = s; inp.value = s; clr.hidden = !s; setErr(''); o.onChange && o.onChange(s) }
  const draw = () => {
    const d = pend || (split(val) ? split(val)[0] : '')
    pop.innerHTML = `<div class="dpw"><div class="dpc">${navHTML(monthTitle(y, m))}${calMonthHTML(y, m)}<div class="cf2"><button type="button" class="lnk${o.min && o.min > TODAY ? ' dis' : ''}" data-today>今天</button>${o.time ? '<button type="button" class="bt bt-p" data-ok>确定</button>' : ''}</div></div>${o.time ? `<div class="tm"><div class="tcol" data-col="h" role="listbox" aria-label="小时">${Array.from({ length: 24 }, (_, i) => `<button type="button" class="${pad(i) === hh ? 'on' : ''}" data-h="${pad(i)}">${pad(i)}</button>`).join('')}</div><div class="tcol" data-col="m" role="listbox" aria-label="分钟">${Array.from({ length: 12 }, (_, i) => `<button type="button" class="${pad(i * 5) === mm ? 'on' : ''}" data-m="${pad(i * 5)}">${pad(i * 5)}</button>`).join('')}</div></div>` : ''}</div>`
    paintCal(pop, { v: d, min: o.min })
  }
  const scrollTimes = () => { if (o.time) QA(pop, '.tcol .on').forEach((b) => { b.parentNode.scrollTop = b.offsetTop - 100 }) }
  const open = () => { const s = split(val); if (s) { const d = parseD(s[0]); y = d.getFullYear(); m = d.getMonth(); if (o.time) { hh = s[1]; mm = s[2] } } pend = ''; draw(); pop.hidden = false; w.classList.add('open'); scrollTimes() }
  const close = () => { pop.hidden = true; w.classList.remove('open') }
  const commit = (s) => { if (o.min && s < o.min) return setErr(`不能选择 ${o.min} 以前的日期`); set(o.time ? `${s} ${hh}:${mm}` : s); close() }
  const parseInput = () => {
    const t = inp.value.trim(); if (!t) return set('')
    const s = split(t)
    if (!s) return setErr(`格式应为 ${o.time ? '2026-11-04 14:30' : '2026-11-04'}`)
    if (o.min && s[0] < o.min) return setErr(`不能选择 ${o.min} 以前的日期`)
    if (o.time && (+s[1] > 23 || +s[2] > 59)) return setErr('时间不存在')
    set(t)
  }
  w.addEventListener('click', (e) => {
    if (e.target.closest('[data-clear]')) { set(''); inp.focus(); return }
    const nv = e.target.closest('[data-nav]'); if (nv) { const d = new Date(y, m + +nv.dataset.nav, 1); y = d.getFullYear(); m = d.getMonth(); draw(); return }
    const dd = e.target.closest('.d')
    if (dd) { if (dd.classList.contains('dis')) return; const s = dd.dataset.date; const d = parseD(s); if (d.getMonth() !== m) { y = d.getFullYear(); m = d.getMonth() } if (o.time) { pend = s; draw() } else commit(s); return }
    if (e.target.closest('[data-today]')) { if (!(o.min && o.min > TODAY)) { if (o.time) { pend = TODAY; y = 2026; m = 10; draw() } else commit(TODAY) } return }
    const h = e.target.closest('[data-h]'); if (h) { hh = h.dataset.h; QA(pop, '[data-h]').forEach((x) => x.classList.toggle('on', x === h)); return }
    const mi = e.target.closest('[data-m]'); if (mi) { mm = mi.dataset.m; QA(pop, '[data-m]').forEach((x) => x.classList.toggle('on', x === mi)); return }
    if (e.target.closest('[data-ok]')) { const s = pend || (split(val) ? split(val)[0] : ''); if (!s) { setErr('请先选择日期'); return } commit(s); return }
    if (e.target.closest('.ig') && pop.hidden) open()
  })
  inp.addEventListener('focus', () => { if (pop.hidden) open() })
  inp.addEventListener('keydown', (e) => { if (e.key === 'Enter') { e.preventDefault(); parseInput(); if (!f.classList.contains('bad')) close() } else if (e.key === 'Escape' && !pop.hidden) { e.stopPropagation(); close() } })
  inp.addEventListener('input', () => { if (f.classList.contains('bad')) setErr('') })
  w.addEventListener('focusout', (e) => { if (!w.contains(e.relatedTarget)) { close(); if (document.hasFocus()) parseInput() } })
  w.addEventListener('mousedown', (e) => { if (!e.target.closest('input')) e.preventDefault() })
  w.addEventListener('keydown', (e) => { if (e.key === 'Escape' && !pop.hidden) { close(); inp.focus() } })
  val = inp.value.trim(); clr.hidden = !val
  return { get: () => val }
}

/* ---------- AD-CTRL-005 日期选择 ---------- */
def({
  id: 'AD-CTRL-005', name: '日期选择', style: '日历面板',
  fit: '单个日期或日期加时间：下单日期、预约时间、有效期截止；可点选也可手输 YYYY-MM-DD，可限定最早日期',
  avoid: '要选一段时间（用日期范围选择，别放两个日期框）；只需要选年月时不要用整张日历',
  kw: 'date picker 日期 日历 时间 预约 选日期 YYYY-MM-DD 今天 最小日期',
  wide: true,
  css: K('adctrl005', { w: 1000 }) + CAL_CSS('.adctrl005') + `
.adctrl005{min-height:470px;padding:20px 24px 24px}
.adctrl005 .g3{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:0 24px}
.adctrl005 .dpw{display:flex;gap:12px}
.adctrl005 .tm{display:flex;gap:4px;padding-left:12px;border-left:1px solid var(--line)}
.adctrl005 .tcol{position:relative;width:48px;height:276px;overflow:auto;scrollbar-width:thin;padding:0 2px}
.adctrl005 .tcol button{display:flex;align-items:center;justify-content:center;width:100%;height:28px;margin-bottom:2px;border-radius:4px;font-variant-numeric:tabular-nums;color:var(--ink)}
.adctrl005 .tcol button:hover{background:var(--mub)}
.adctrl005 .tcol button.on{background:var(--pt);color:var(--p-text);font-weight:600}
.adctrl005 .tcol button:focus:not(:focus-visible){outline:0}
.adctrl005 .g3 .f:last-child .pop{left:auto;right:0}
@media(max-width:900px){.adctrl005 .g3{grid-template-columns:minmax(0,1fr)}.adctrl005{min-height:780px}.adctrl005 .g3 .f{margin-bottom:12px}.adctrl005 .g3 .f:last-child .pop{left:0;right:auto}.adctrl005 .dpw{flex-direction:column}.adctrl005 .tm{padding:8px 0 0;border-left:0;border-top:1px solid var(--line)}.adctrl005 .tcol{height:84px;width:auto;flex:1}}`,
  html: () => `<div class="adctrl005"><div class="g3">
${dateFieldHTML('da', '下单日期', 'YYYY-MM-DD', '2026-11-04')}
${dateFieldHTML('db', '预约日期', 'YYYY-MM-DD', '')}
${dateFieldHTML('dc', '提醒时间', 'YYYY-MM-DD HH:mm', '2026-11-06 14:30')}
</div></div>`,
  js: H((root, B) => {
    mkDate(Q(B, '[data-dt=da]'))
    mkDate(Q(B, '[data-dt=db]'), { min: TODAY })
    mkDate(Q(B, '[data-dt=dc]'), { time: true })
  }),
})

/* ---------- AD-CTRL-006 日期范围选择 ---------- */
const RANGE_PRESETS = [['今日', () => [TODAY, TODAY]], ['近 7 天', () => [addDays(TODAY, -6), TODAY]], ['近 30 天', () => [addDays(TODAY, -29), TODAY]], ['本月', () => ['2026-11-01', TODAY]], ['全部', () => ['', '']]]
const dayCount = (a, b) => Math.round((parseD(b) - parseD(a)) / 86400000) + 1
def({
  id: 'AD-CTRL-006', name: '日期范围选择', style: '快捷项双月',
  fit: '订单、报表按时间筛选：快捷项（今日、近 7 天、近 30 天、本月、全部）和自定义起止日期放在同一个弹层里，选完结束日期即生效',
  avoid: '不要在旁边再摆一排快捷按钮（同一目的地两个入口）；要限定最长跨度时在选到上限后禁用更远的日期',
  kw: 'date range 日期范围 区间 快捷项 近7天 近30天 双月 起止日期 筛选',
  wide: true,
  css: K('adctrl006', { w: 1000 }) + CAL_CSS('.adctrl006') + `
.adctrl006{min-height:480px;padding:20px 24px 24px}
.adctrl006 .box{max-width:360px}
.adctrl006 .rpw{display:flex;gap:0}
.adctrl006 .pre{display:flex;flex-direction:column;gap:2px;width:96px;margin:0 12px 0 -4px;padding:0 12px 0 0;border-right:1px solid var(--line);list-style:none}
.adctrl006 .pre button{display:flex;align-items:center;height:32px;padding:0 10px;border-radius:4px;color:var(--ink);text-align:left;width:100%}
.adctrl006 .pre button:hover{background:var(--mub)}
.adctrl006 .pre button.on{background:var(--pt);color:var(--p-text);font-weight:600}
.adctrl006 .pre button:focus:not(:focus-visible){outline:0}
.adctrl006 .ms{display:flex;gap:16px}
.adctrl006 .ms .mh{display:flex;align-items:center;justify-content:space-between;height:32px;margin-bottom:4px}
.adctrl006 .ms .mh b{flex:1;text-align:center;font-weight:600;font-variant-numeric:tabular-nums}
.adctrl006 .ms .mh button{display:inline-flex;align-items:center;justify-content:center;width:28px;height:28px;border-radius:4px;color:var(--ink2)}
.adctrl006 .ms .mh button:hover{background:var(--mub)}
.adctrl006 .ms .mh button .ic{width:16px;height:16px}
.adctrl006 .ms .mh button.hd0{visibility:hidden}
.adctrl006 .sum{color:var(--ink2);font-variant-numeric:tabular-nums}
.adctrl006 .sum b{font-weight:600;color:var(--ink)}
@media(max-width:600px){.adctrl006{padding:16px}.adctrl006 .rpw{flex-direction:column}.adctrl006 .pre{flex-direction:row;flex-wrap:wrap;width:auto;margin:0 0 8px;padding:0 0 8px;border-right:0;border-bottom:1px solid var(--line)}.adctrl006 .pre button{width:auto}.adctrl006 .ms .mo2{display:none}.adctrl006 .ms .mo1 .mh button.hd0{visibility:visible}.adctrl006 .ms .mo1 .mh button.nx{visibility:visible}}`,
  html: () => `<div class="adctrl006"><div class="box"><div class="f" data-f="r"><label class="lb" for="rg-i">统计日期</label><div class="ctl"><div class="dtw" data-rg><div class="ig"><span class="pf">${sv('calendar')}</span><input class="in" id="rg-i" readonly aria-haspopup="dialog" value=""><button type="button" class="ib clr" data-clear aria-label="清除" title="清除">${ic('closec')}</button></div><div class="pop" hidden></div></div><span class="er"></span></div></div></div></div>`,
  js: H((root, B) => {
    const w = Q(B, '[data-rg]'), inp = Q(w, '.in'), pop = Q(w, '.pop'), clr = Q(w, '[data-clear]')
    let a = addDays(TODAY, -6), b = TODAY, pa = '', pb = '', hover = '', y = 2026, m = 9
    const text = () => (a ? `${a} ~ ${b}` : '全部')
    const sync = () => { inp.value = text(); clr.hidden = !a }
    const activePre = () => RANGE_PRESETS.findIndex(([, f]) => { const [x, z] = f(); return x === a && z === b })
    const draw = () => {
      const y2 = m === 11 ? y + 1 : y, m2 = (m + 1) % 12, ap = activePre()
      pop.innerHTML = `<div class="rpw"><ul class="pre" role="listbox" aria-label="快捷范围">${RANGE_PRESETS.map(([t], i) => `<li><button type="button" class="${i === ap && !pa ? 'on' : ''}" data-pre="${i}" role="option">${t}</button></li>`).join('')}</ul><div><div class="ms"><div class="mo1"><div class="mh"><button type="button" data-nav="-1" aria-label="上个月">${ic('left')}</button><b>${monthTitle(y, m)}</b><button type="button" class="hd0 nx" data-nav="1" aria-label="下个月">${ic('right')}</button></div>${calMonthHTML(y, m, true)}</div><div class="mo2"><div class="mh"><button type="button" class="hd0" aria-hidden="true" tabindex="-1">${ic('left')}</button><b>${monthTitle(y2, m2)}</b><button type="button" data-nav="1" aria-label="下个月">${ic('right')}</button></div>${calMonthHTML(y2, m2, true)}</div></div><div class="cf2"><span class="sum" data-sum></span></div></div></div>`
      paint()
    }
    const paint = () => {
      const st = pa ? { a: pa, b: pb, hover } : { a, b: a ? b : '' }
      paintCal(pop, st)
      const sm = Q(pop, '[data-sum]'); if (!sm) return
      if (pa && !pb) sm.innerHTML = `<b>${pa}</b> ~ 选择结束日期`
      else if (a) sm.innerHTML = `<b>${a}</b> ~ <b>${b}</b> · 共 ${dayCount(a, b)} 天`
      else sm.textContent = '不限日期'
    }
    const open = () => { const d = parseD(a || addDays(TODAY, -30)); y = d.getFullYear(); m = d.getMonth(); pa = ''; pb = ''; hover = ''; draw(); pop.hidden = false; w.classList.add('open') }
    const close = () => { pop.hidden = true; w.classList.remove('open'); pa = ''; pb = '' }
    const commit = (x, z) => { a = x; b = z; sync(); close() }
    w.addEventListener('click', (e) => {
      if (e.target.closest('[data-clear]')) { commit('', ''); return }
      const nv = e.target.closest('[data-nav]'); if (nv) { const d = new Date(y, m + +nv.dataset.nav, 1); y = d.getFullYear(); m = d.getMonth(); draw(); return }
      const pre = e.target.closest('[data-pre]'); if (pre) { const [x, z] = RANGE_PRESETS[+pre.dataset.pre][1](); commit(x, z); inp.focus(); return }
      const dd = e.target.closest('.d')
      if (dd && !dd.classList.contains('hid')) {
        const s = dd.dataset.date
        if (!pa || pb) { pa = s; pb = ''; hover = ''; paint(); QA(pop, '[data-pre]').forEach((x) => x.classList.remove('on')) }
        else { const lo = s < pa ? s : pa, hi = s < pa ? pa : s; commit(lo, hi); inp.focus() }
        return
      }
      if (e.target.closest('.ig') && pop.hidden) open()
    })
    w.addEventListener('mouseover', (e) => { const dd = e.target.closest('.d'); if (dd && pa && !pb && !dd.classList.contains('hid') && hover !== dd.dataset.date) { hover = dd.dataset.date; paint() } })
    inp.addEventListener('focus', () => { if (pop.hidden) open() })
    inp.addEventListener('keydown', (e) => { if (e.key === 'Enter' || e.key === ' ' || e.key === 'ArrowDown') { e.preventDefault(); if (pop.hidden) open() } else if (e.key === 'Escape' && !pop.hidden) { e.stopPropagation(); close() } })
    w.addEventListener('focusout', (e) => { if (!w.contains(e.relatedTarget)) close() })
    w.addEventListener('mousedown', (e) => { if (!e.target.closest('input')) e.preventDefault() })
    sync()
  }),
})

/* ---------- AD-CTRL-007 级联选择 ---------- */
const CAS = [
  ['数码', [['手机', ['智能手机', '老人机', '手机配件']], ['耳机', ['头戴式耳机', '入耳式耳机', '骨传导耳机']], ['智能穿戴', ['智能手表', '运动手环']]]],
  ['家居', [['厨房', ['锅具', '刀具餐具', '收纳整理']], ['卧室', ['床品套件', '睡眠枕芯']], ['清洁', ['拖把扫帚', '清洁用品']]]],
  ['服饰', [['男装', ['夹克', 'T 恤', '牛仔裤']], ['女装', ['连衣裙', '针织衫', '半身裙']], ['鞋靴', ['运动鞋', '休闲鞋']]]],
  ['食品', [['零食', ['坚果炒货', '糖果巧克力']], ['饮品', ['咖啡', '茶叶', '气泡水']]]],
]
def({
  id: 'AD-CTRL-007', name: '级联选择', style: '三级联动',
  fit: '商品分类、地区、组织架构这类有层级的单选：点一级展开二级，再展开三级，选到叶子即完成；带搜索可直接定位',
  avoid: '层级只有两级且选项不多（用两个联动下拉更简单）；选项超过 200 个一级节点时先分页或搜索',
  kw: 'cascader 级联 三级联动 商品分类 地区 省市区 层级选择 树选择 搜索 路径',
  css: K('adctrl007', { w: 640 }) + `
.adctrl007{min-height:420px;padding:20px 24px 24px}
.adctrl007 .box{max-width:360px}
.adctrl007 .cx{position:relative}
.adctrl007 .sel .vs{flex:1;min-width:0;overflow:hidden;text-overflow:ellipsis;white-space:nowrap}
.adctrl007 .sel .pl2{color:var(--ink3)}
.adctrl007 .sel .clr{width:20px;height:20px;margin:0 2px 0 0;color:var(--ink3)}
.adctrl007 .sel .clr .ic{width:14px;height:14px;transform:none}
.adctrl007 .sel:focus{outline:0}
.adctrl007 .sel:focus-visible{outline:2px solid var(--ink2);outline-offset:2px}
.adctrl007 .cx.open .sel{border-color:var(--ink2)}
.adctrl007 .cx.open .sel>.ic{transform:rotate(180deg)}
.adctrl007 .cpn{position:absolute;left:0;top:calc(100% + 6px);z-index:25;width:min(540px,calc(100vw - 48px));padding:8px;border:1px solid var(--bd0);border-radius:12px;background:var(--card);box-shadow:var(--sh3);animation:admdl .18s cubic-bezier(.2,0,0,1)}
.adctrl007 .cpn[hidden]{display:none}
.adctrl007 .cq{margin-bottom:8px}
.adctrl007 .cols{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:0;height:224px}
.adctrl007 .col{overflow:auto;padding:0 4px;border-right:1px solid var(--line)}
.adctrl007 .col:last-child{border-right:0}
.adctrl007 .ci{display:flex;align-items:center;justify-content:space-between;gap:6px;width:100%;min-height:32px;padding:5px 8px;border-radius:4px;text-align:left;margin-bottom:2px}
.adctrl007 .ci:hover{background:var(--mub)}
.adctrl007 .ci .ic{color:var(--ink3);width:14px;height:14px}
.adctrl007 .ci.on{background:var(--pt);color:var(--p-text);font-weight:600}
.adctrl007 .ci.on .ic{color:var(--p-text)}
.adctrl007 .ci.pick::after{content:"";width:5px;height:9px;margin:0 3px 3px 0;border:solid var(--pd);border-width:0 2px 2px 0;transform:rotate(45deg);flex:none}
.adctrl007 .ci:focus:not(:focus-visible){outline:0}
.adctrl007 .ci:focus-visible{outline:2px solid var(--ink2);outline-offset:-2px}
.adctrl007 .col .em{padding:12px 8px;color:var(--ink3)}
.adctrl007 .rs2{height:224px;overflow:auto}
.adctrl007 .rs2 .ci{padding:5px 10px}
.adctrl007 mark{background:none;color:var(--p-text);font-weight:600}
.adctrl007 .nom2{padding:56px 10px;text-align:center;color:var(--ink3)}
@media(max-width:520px){.adctrl007{padding:16px}.adctrl007 .cpn{width:calc(100vw - 72px)}.adctrl007 .cols{height:200px}.adctrl007 .ci{padding:5px 6px}}`,
  html: () => `<div class="adctrl007"><div class="box"><div class="f"><label class="lb" id="cs-l">商品分类</label><div class="cx" data-cas><div class="in sel" role="combobox" tabindex="0" aria-haspopup="tree" aria-expanded="false" aria-labelledby="cs-l"><span class="vs"></span><button type="button" class="ib clr" data-clear aria-label="清除" title="清除" hidden>${ic('closec')}</button>${ic('down')}</div><div class="cpn" hidden><div class="ig cq"><span class="pf">${sv('search')}</span><input class="in" data-q aria-label="搜索分类" placeholder="搜索分类"></div><div data-body></div></div></div></div></div></div>`,
  js: H((root, B) => {
    const el = Q(B, '[data-cas]'), tr = Q(el, '.sel'), pn = Q(el, '.cpn'), body = Q(el, '[data-body]'), q = Q(el, '[data-q]'), clr = Q(el, '[data-clear]')
    let act = [0, 1], sel = null
    const label = () => { Q(tr, '.vs').innerHTML = sel ? sel.map((x, i) => [CAS[sel[0]][0], CAS[sel[0]][1][sel[1]][0], CAS[sel[0]][1][sel[1]][1][sel[2]]][i]).join(' / ') : '<span class="pl2">请选择分类</span>'; clr.hidden = !sel }
    const cols = () => {
      const c1 = CAS.map((n, i) => `<button type="button" class="ci${act[0] === i ? ' on' : ''}" data-l="0" data-i="${i}">${n[0]}${ic('right')}</button>`).join('')
      const l2 = act[0] != null ? CAS[act[0]][1] : []
      const c2 = l2.map((n, j) => `<button type="button" class="ci${act[1] === j ? ' on' : ''}" data-l="1" data-i="${j}">${n[0]}${ic('right')}</button>`).join('') || '<div class="em">先选左侧分类</div>'
      const l3 = act[0] != null && act[1] != null && l2[act[1]] ? l2[act[1]][1] : []
      const c3 = l3.map((n, k) => `<button type="button" class="ci${sel && sel[0] === act[0] && sel[1] === act[1] && sel[2] === k ? ' on pick' : ''}" data-l="2" data-i="${k}">${n}</button>`).join('')
      body.innerHTML = `<div class="cols"><div class="col">${c1}</div><div class="col">${c2}</div><div class="col">${c3}</div></div>`
    }
    const flat = () => CAS.flatMap((n, i) => n[1].flatMap((c, j) => c[1].map((l, k) => ({ i, j, k, t: `${n[0]} / ${c[0]} / ${l}` }))))
    const draw = () => {
      const s = q.value.trim()
      if (!s) { cols(); return }
      const rs = flat().filter((x) => x.t.includes(s))
      body.innerHTML = rs.length ? `<div class="rs2">${rs.map((x) => `<button type="button" class="ci" data-p="${x.i},${x.j},${x.k}">${x.t.replace(s, `<mark>${s}</mark>`)}</button>`).join('')}</div>` : `<div class="nom2">没有包含“${s.replace(/</g, '&lt;')}”的分类</div>`
    }
    const open = () => { if (sel) act = [sel[0], sel[1]]; q.value = ''; draw(); pn.hidden = false; el.classList.add('open'); tr.setAttribute('aria-expanded', 'true') }
    const close = () => { pn.hidden = true; el.classList.remove('open'); tr.setAttribute('aria-expanded', 'false') }
    const choose = (a) => { sel = a; label(); close(); tr.focus() }
    tr.addEventListener('click', (e) => { if (e.target.closest('[data-clear]')) { sel = null; label(); e.stopPropagation(); return } el.classList.contains('open') ? close() : open() })
    pn.addEventListener('mousedown', (e) => { if (!e.target.closest('input')) e.preventDefault() })
    pn.addEventListener('click', (e) => {
      const c = e.target.closest('.ci'); if (!c) return
      if (c.dataset.p) { choose(c.dataset.p.split(',').map(Number)); return }
      const l = +c.dataset.l, i = +c.dataset.i
      if (l === 0) { act = [i, 0]; cols() } else if (l === 1) { act = [act[0], i]; cols() } else choose([act[0], act[1], i])
    })
    q.addEventListener('input', draw)
    el.addEventListener('keydown', (e) => { if (e.key === 'Escape' && el.classList.contains('open')) { e.stopPropagation(); close(); tr.focus() } else if ((e.key === 'Enter' || e.key === ' ' || e.key === 'ArrowDown') && e.target === tr) { e.preventDefault(); open() } })
    el.addEventListener('focusout', (e) => { if (!el.contains(e.relatedTarget)) close() })
    label()
  }),
})

/* ---------- AD-CTRL-008 穿梭框 ---------- */
const TR_PEOPLE = NAMES.slice(0, 10).map((n, i) => ({ id: i, n, d: DEPTS[i % 6], dis: i === 9 }))
def({
  id: 'AD-CTRL-008', name: '穿梭框', style: '左右移动',
  fit: '给角色分配成员、给活动选适用商品这类“从一大堆里挑一部分”的多选：左边待选、右边已选，两边都能搜索与全选',
  avoid: '选项少于 8 个（直接用多选组）；要选的对象有层级时改用树形选择；右侧要排序时需额外加拖动',
  kw: 'transfer 穿梭框 左右移动 分配成员 待选 已选 全选 搜索 双列表 角色授权',
  wide: true,
  css: K('adctrl008', { w: 760 }) + TIP_CSS('.adctrl008') + `
.adctrl008{padding:20px 24px 24px}
.adctrl008 .tw{display:grid;grid-template-columns:minmax(0,1fr) auto minmax(0,1fr);align-items:center;gap:0 12px}
.adctrl008 .pn{display:flex;flex-direction:column;height:320px;border:1px solid var(--bd);border-radius:12px;background:var(--card2);overflow:hidden}
.adctrl008 .ph2{display:flex;align-items:center;justify-content:space-between;gap:8px;padding:10px 14px;border-bottom:1px solid var(--line);background:var(--n1)}
.adctrl008 .ph2 .cb{font-weight:600}
.adctrl008 .ph2 .n{font-size:12px;color:var(--ink3);font-variant-numeric:tabular-nums}
.adctrl008 .sq{padding:8px 10px 4px}
.adctrl008 .ls{flex:1;min-height:0;overflow:auto;padding:4px 6px 6px}
.adctrl008 .ti{display:flex;align-items:center;gap:10px;width:100%;min-height:36px;padding:4px 8px;border-radius:4px;text-align:left}
.adctrl008 .ti:hover{background:var(--mub)}
.adctrl008 .ti.on{background:var(--pt)}
.adctrl008 .ti>i{position:relative;width:16px;height:16px;flex:none;border:1px solid var(--bd2);border-radius:4px;background:var(--card)}
.adctrl008 .ti.on>i{background:var(--p);border-color:var(--p)}
.adctrl008 .ti.on>i::after{content:"";position:absolute;left:4.5px;top:1.5px;width:4px;height:8px;border:solid var(--card);border-width:0 2px 2px 0;transform:rotate(45deg)}
.adctrl008 .ti .av{width:24px;height:24px;flex:none}
.adctrl008 .ti span{flex:1;min-width:0;overflow:hidden;text-overflow:ellipsis;white-space:nowrap}
.adctrl008 .ti small{font-size:12px;color:var(--ink3);white-space:nowrap}
.adctrl008 .ti.dis{color:var(--ink4);cursor:not-allowed}
.adctrl008 .ti.dis:hover{background:none}
.adctrl008 .ti.dis>i{background:var(--mub);border-color:var(--bd0)}
.adctrl008 .ti:focus:not(:focus-visible){outline:0}
.adctrl008 .ti:focus-visible{outline:2px solid var(--ink2);outline-offset:-2px}
.adctrl008 .em{padding:56px 12px;text-align:center;color:var(--ink3)}
.adctrl008 .mid{display:flex;flex-direction:column;gap:8px}
.adctrl008 .bt-i{width:32px;padding:0}
@media(max-width:640px){.adctrl008{padding:16px}.adctrl008 .tw{grid-template-columns:minmax(0,1fr);gap:12px 0}.adctrl008 .mid{flex-direction:row;justify-content:center}.adctrl008 .mid .ic{transform:rotate(90deg)}.adctrl008 .pn{height:260px}}`,
  html: () => `<div class="adctrl008"><div class="tw">
<div class="pn" data-side="l"><div class="ph2"><button type="button" class="cb" data-all role="checkbox" aria-checked="false"><i></i>待选员工</button><span class="n" data-n></span></div><div class="sq"><div class="ig"><span class="pf">${sv('search')}</span><input class="in" data-q aria-label="搜索待选员工" placeholder="搜索姓名或部门"></div></div><div class="ls" role="group" aria-label="待选员工"></div></div>
<div class="mid"><span class="tp" data-tip="移到已选"><button type="button" class="bt bt-s bt-i dis" data-to="r" aria-label="移到已选" aria-disabled="true">${ic('right')}</button></span><span class="tp" data-tip="移回待选"><button type="button" class="bt bt-s bt-i dis" data-to="l" aria-label="移回待选" aria-disabled="true">${ic('left')}</button></span></div>
<div class="pn" data-side="r"><div class="ph2"><button type="button" class="cb" data-all role="checkbox" aria-checked="false"><i></i>已选员工</button><span class="n" data-n></span></div><div class="sq"><div class="ig"><span class="pf">${sv('search')}</span><input class="in" data-q aria-label="搜索已选员工" placeholder="搜索姓名或部门"></div></div><div class="ls" role="group" aria-label="已选员工"></div></div>
</div></div>`,
  js: H((root, B) => {
    const right = new Set([1, 4]), pick = { l: new Set(), r: new Set() }
    const side = (s) => Q(B, `[data-side=${s}]`)
    const items = (s) => TR_PEOPLE.filter((p) => (s === 'r') === right.has(p.id))
    const vis = (s) => { const k = Q(side(s), '[data-q]').value.trim(); return items(s).filter((p) => !k || p.n.includes(k) || p.d.includes(k)) }
    const render = () => {
      ;['l', 'r'].forEach((s) => {
        const pn = side(s), v = vis(s)
        Q(pn, '.ls').innerHTML = v.length ? v.map((p) => `<button type="button" class="ti${p.dis ? ' dis' : ''}" role="checkbox" aria-checked="false" ${p.dis ? 'aria-disabled="true" title="已离职，不可选"' : ''} data-id="${p.id}"><i></i>${critter(p.id, 24)}<span>${p.n}${p.dis ? '（已离职）' : ''}</span><small>${p.d}</small></button>`).join('') : `<div class="em">${Q(pn, '[data-q]').value.trim() ? '没有符合的员工' : s === 'l' ? '员工已全部选完' : '从左侧选择员工'}</div>`
      })
    }
    /* 勾选只改样式、不重建列表，这样双击才能被浏览器识别 */
    const paint = () => {
      ;['l', 'r'].forEach((s) => {
        const pn = side(s), v = vis(s), all = items(s)
        QA(pn, '.ti').forEach((t) => { const on = pick[s].has(+t.dataset.id); t.classList.toggle('on', on); t.setAttribute('aria-checked', on) })
        const sel = all.filter((p) => pick[s].has(p.id)).length, can = v.filter((p) => !p.dis)
        Q(pn, '[data-n]').textContent = `${sel}/${all.length} 项`
        const a = Q(pn, '[data-all]'), full = can.length > 0 && can.every((p) => pick[s].has(p.id)), part = can.some((p) => pick[s].has(p.id)) && !full
        a.classList.toggle('on', full); a.classList.toggle('part', part); a.setAttribute('aria-checked', part ? 'mixed' : full)
      })
      ;[['r', 'l'], ['l', 'r']].forEach(([to, from]) => { const b = Q(B, `[data-to=${to}]`), off = pick[from].size === 0; b.classList.toggle('dis', off); b.setAttribute('aria-disabled', off) })
    }
    const draw = () => { render(); paint() }
    const move = (ids, to) => { ids.forEach((i) => (to === 'r' ? right.add(i) : right.delete(i))); pick.l.clear(); pick.r.clear(); draw() }
    B.addEventListener('click', (e) => {
      const it = e.target.closest('.ti'); if (it && !it.classList.contains('dis')) { const s = it.closest('[data-side]').dataset.side, id = +it.dataset.id; pick[s].has(id) ? pick[s].delete(id) : pick[s].add(id); paint(); return }
      const al = e.target.closest('[data-all]'); if (al) { const s = al.closest('[data-side]').dataset.side, can = vis(s).filter((p) => !p.dis); const full = can.every((p) => pick[s].has(p.id)); can.forEach((p) => (full ? pick[s].delete(p.id) : pick[s].add(p.id))); paint(); return }
      const to = e.target.closest('[data-to]'); if (to) { const from = to.dataset.to === 'r' ? 'l' : 'r'; const ids = [...pick[from]]; move(ids, to.dataset.to); tst(B, `已${to.dataset.to === 'r' ? '加入' : '移出'} ${ids.length} 人`) }
    })
    B.addEventListener('dblclick', (e) => { const it = e.target.closest('.ti'); if (it && !it.classList.contains('dis')) { const s = it.closest('[data-side]').dataset.side; move([+it.dataset.id], s === 'l' ? 'r' : 'l') } })
    B.addEventListener('input', (e) => { if (e.target.matches('[data-q]')) draw() })
    draw()
  }),
})

/* ---------- AD-CTRL-009 图片上传区 ---------- */
const upThumb = (src, st = 'done', n = 0) => `<div class="th ${st}" data-th data-st="${st}" tabindex="0" draggable="true" aria-label="图片 ${n}，方向键调整顺序"><img src="${src}" alt="" draggable="false"><span class="cvb">封面</span><div class="ov"><button type="button" class="ib" data-cover aria-label="设为封面" title="设为封面">${ic('star')}</button><button type="button" class="ib" data-del aria-label="删除" title="删除">${ic('trash')}</button></div><div class="pg"><i></i></div><div class="fl2"><span>上传失败</span><button type="button" class="lnk" data-retry>重试</button></div></div>`
def({
  id: 'AD-CTRL-009', name: '图片上传区', style: '拖拽封面排序',
  fit: '商品图、门店照片、横幅这类要传多张图的场景：拖进来或点击添加，有进度与失败重试，第一张是封面，可拖动或用方向键排序',
  avoid: '用户自己无法改小的原图不要限制大小或提示“过大”，由后台压缩；合同、文档这类能换文件的才写大小上限',
  kw: 'upload 上传 图片 拖拽 缩略图 封面 排序 删除 进度 重试',
  wide: true,
  css: K('adctrl009', { w: 760 }) + `
.adctrl009 .hd2{display:flex;align-items:center;justify-content:space-between;padding:16px 24px;border-bottom:1px solid var(--line)}
.adctrl009 .hd2 b{font-size:16px;font-weight:600}
.adctrl009 .bd{padding:20px 24px 24px}
.adctrl009 .dz{display:flex;flex-direction:column;align-items:center;justify-content:center;gap:2px;height:112px;border:1px dashed var(--bd2);border-radius:12px;background:var(--n1);text-align:center;cursor:pointer;transition:border-color .15s,background-color .15s}
.adctrl009 .dz:hover{border-color:var(--p);background:var(--pt)}
.adctrl009 .dz.over{border-color:var(--p);border-style:solid;background:var(--pm)}
.adctrl009 .dz .ic{width:24px;height:24px;margin-bottom:4px;color:var(--ink2)}
.adctrl009 .dz b{font-weight:600}
.adctrl009 .dz:focus{outline:0}
.adctrl009 .dz:focus-visible{outline:2px solid var(--ink2);outline-offset:2px}
.adctrl009 .dz.full{cursor:not-allowed;background:var(--soft);border-color:var(--bd0)}
.adctrl009 .dz.full:hover{border-color:var(--bd0);background:var(--soft)}
.adctrl009 .gr{display:grid;grid-template-columns:repeat(auto-fill,96px);gap:12px;margin-top:16px}
.adctrl009 .gr:empty{display:none}
.adctrl009 .th{position:relative;width:96px;height:96px;border:1px solid var(--bd0);border-radius:8px;overflow:hidden;background:var(--ph);cursor:grab;transition:transform .2s cubic-bezier(.2,0,0,1),opacity .15s}
.adctrl009 .th img{display:block;width:100%;height:100%;object-fit:cover;pointer-events:none}
.adctrl009 .th.drg{opacity:.4}
.adctrl009 .th:focus{outline:0}
.adctrl009 .th:focus-visible{outline:2px solid var(--ink2);outline-offset:2px}
.adctrl009 .cvb{position:absolute;left:6px;top:6px;display:none;height:20px;padding:0 6px;border-radius:4px;background:var(--p);color:#fff;font-size:12px;line-height:20px;font-weight:600}
.adctrl009 .th.first .cvb{display:block}
.adctrl009 .ov{position:absolute;inset:0;display:flex;align-items:center;justify-content:center;gap:6px;background:color-mix(in srgb,var(--scrim) 50%,transparent);opacity:0;transition:opacity .15s}
.adctrl009 .th:hover .ov,.adctrl009 .th:focus-within .ov{opacity:1}
.adctrl009 .ov .ib{margin:0;width:28px;height:28px;color:#fff}
.adctrl009 .ov .ib:hover{background:color-mix(in srgb,var(--card) 20%,transparent);color:#fff}
.adctrl009 .th.first [data-cover]{display:none}
.adctrl009 .pg{position:absolute;left:8px;right:8px;bottom:8px;height:4px;border-radius:999px;background:var(--glass0);display:none}
.adctrl009 .pg i{display:block;height:100%;width:0;border-radius:999px;background:var(--p);transition:width .1s linear}
.adctrl009 .th.up .pg{display:block}
.adctrl009 .th.up img{opacity:.55}
.adctrl009 .th.up .ov,.adctrl009 .th.err .cvb{display:none}
.adctrl009 .fl2{position:absolute;inset:0;display:none;flex-direction:column;align-items:center;justify-content:center;gap:2px;background:rgba(248,236,234,.94);color:var(--dg);font-size:12px;line-height:18px}
.adctrl009 .fl2 .lnk{color:var(--dg);font-size:12px;text-decoration:underline;text-underline-offset:2px}
.adctrl009 .th.err .fl2{display:flex}
.adctrl009 .th.err .ov{display:none}
@media(hover:none){.adctrl009 .ov{opacity:1;inset:auto 0 0 0;height:32px;background:color-mix(in srgb,var(--scrim) 55%,transparent)}}
@media(max-width:520px){.adctrl009 .hd2,.adctrl009 .bd{padding-left:16px;padding-right:16px}.adctrl009 .gr{grid-template-columns:repeat(3,minmax(0,1fr))}.adctrl009 .th{width:auto;aspect-ratio:1/1;height:auto}}`,
  html: () => `<div class="adctrl009"><div class="hd2"><b>商品图片</b><span class="mut" data-cnt></span></div><div class="bd">
<div class="dz" data-dz tabindex="0" role="button" aria-label="添加图片">${ic('upload')}<b data-dzt>拖拽图片到这里，或点击添加</b><span class="mut" data-dzs>支持 JPG、PNG，最多 9 张，第一张为封面</span></div>
<div class="gr" data-gr>${[0, 1, 2].map((i) => upThumb(P(i), 'done', i + 1)).join('')}</div>
</div></div>`,
  js: H((root, B) => {
    const MAX = 9, gr = Q(B, '[data-gr]'), dz = Q(B, '[data-dz]'); let nAdd = 0, drag = null
    const items = () => QA(gr, '[data-th]')
    const refresh = () => {
      const it = items(); it.forEach((t, i) => { t.classList.toggle('first', i === 0); t.setAttribute('aria-label', `图片 ${i + 1}，方向键调整顺序`) })
      Q(B, '[data-cnt]').textContent = `${it.length}/${MAX}`
      const full = it.length >= MAX; dz.classList.toggle('full', full); dz.setAttribute('aria-disabled', full)
      Q(B, '[data-dzt]').textContent = full ? '已达到 9 张上限' : '拖拽图片到这里，或点击添加'
    }
    const run = (t, failAt) => {
      t.classList.add('up'); t.classList.remove('done', 'err'); const bar = Q(t, '.pg i'); let p = 0
      const iv = setInterval(() => {
        if (!t.isConnected) { clearInterval(iv); return }
        p += 12; bar.style.width = Math.min(p, 100) + '%'
        if (failAt && p >= failAt) { clearInterval(iv); t.classList.remove('up'); t.classList.add('err'); t.dataset.failed = '1'; return }
        if (p >= 100) { clearInterval(iv); t.classList.remove('up'); t.classList.add('done') }
      }, 90)
    }
    const add = (src) => {
      if (items().length >= MAX) { tst(B, '最多 9 张', 'bad'); return }
      nAdd++; const w = document.createElement('div'); w.innerHTML = upThumb(src, 'up', items().length + 1); const t = w.firstElementChild
      gr.appendChild(t); refresh(); run(t, nAdd % 4 === 0 ? 60 : 0)
    }
    refresh()
    dz.addEventListener('click', () => { if (!dz.classList.contains('full')) add(P((items().length + nAdd) % 9)) })
    dz.addEventListener('keydown', (e) => { if (e.key === 'Enter' || e.key === ' ') { e.preventDefault(); dz.click() } })
    B.addEventListener('click', (e) => {
      const d = e.target.closest('[data-del]'); if (d) { d.closest('[data-th]').remove(); refresh(); tst(B, '已删除') ; return }
      const c = e.target.closest('[data-cover]'); if (c) { const t = c.closest('[data-th]'); gr.insertBefore(t, gr.firstElementChild); refresh(); tst(B, '已设为封面'); return }
      const r = e.target.closest('[data-retry]'); if (r) { const t = r.closest('[data-th]'); delete t.dataset.failed; run(t, 0) }
    })
    /* 拖动：本地文件拖入添加，缩略图之间拖动排序 */
    const hasFiles = (e) => e.dataTransfer && [...(e.dataTransfer.types || [])].includes('Files')
    const readFiles = (files) => { [...files].filter((f) => f.type.startsWith('image/')).slice(0, MAX - items().length).forEach((f) => { const rd = new FileReader(); rd.onload = () => add(rd.result); rd.readAsDataURL(f) }) }
    B.addEventListener('dragover', (e) => { if (hasFiles(e)) { e.preventDefault(); dz.classList.add('over') } else if (drag) { e.preventDefault(); const t = e.target.closest('[data-th]'); if (t && t !== drag) { const r = t.getBoundingClientRect(); gr.insertBefore(drag, e.clientX < r.left + r.width / 2 ? t : t.nextSibling) } } })
    B.addEventListener('dragleave', (e) => { if (!B.contains(e.relatedTarget)) dz.classList.remove('over') })
    B.addEventListener('drop', (e) => { dz.classList.remove('over'); if (hasFiles(e)) { e.preventDefault(); readFiles(e.dataTransfer.files) } else if (drag) { e.preventDefault(); refresh() } })
    B.addEventListener('dragstart', (e) => { const t = e.target.closest && e.target.closest('[data-th]'); if (t) { drag = t; t.classList.add('drg'); e.dataTransfer.effectAllowed = 'move'; e.dataTransfer.setData('text/plain', 'th') } })
    B.addEventListener('dragend', () => { if (drag) { drag.classList.remove('drg'); drag = null; refresh() } })
    B.addEventListener('keydown', (e) => {
      const t = e.target.closest && e.target.closest('[data-th]'); if (!t || e.target !== t) return
      if (e.key === 'ArrowLeft' && t.previousElementSibling) { e.preventDefault(); gr.insertBefore(t, t.previousElementSibling); refresh(); t.focus() }
      else if (e.key === 'ArrowRight' && t.nextElementSibling) { e.preventDefault(); gr.insertBefore(t.nextElementSibling, t); refresh(); t.focus() }
      else if (e.key === 'Delete' || e.key === 'Backspace') { e.preventDefault(); const n = t.nextElementSibling || t.previousElementSibling; t.remove(); refresh(); if (n) n.focus(); tst(B, '已删除') }
    })
  }),
})

/* ---------- AD-CTRL-010 评分 ---------- */
const STAR_TXT = ['未评分', '很差', '较差', '一般', '满意', '很棒']
const starsHTML = (cls = '') => [1, 2, 3, 4, 5].map((n) => `<button type="button" class="sta${cls}" data-n="${n}" role="radio" aria-checked="false" aria-label="${n} 星">${sv('star')}</button>`).join('')
def({
  id: 'AD-CTRL-010', name: '评分', style: '星级量表',
  fit: '评价管理里的评分筛选与回复、客服质检打分；星级用于 1–5 分，0–10 分的推荐意愿用数字量表',
  avoid: '只需要“好评/差评”二选一时用单选；展示平均分时用只读小数评分，别用可点的星',
  kw: 'rate rating 评分 星级 评价 打分 量表 NPS 数字量表 只读',
  css: K('adctrl010', { w: 640 }) + SC_CSS('.adctrl010') + `
.adctrl010{--gold:#B8862F;--gold0:color-mix(in srgb,var(--off) 40%,var(--n10))}
.adctrl010 .stars{display:inline-flex;gap:2px}
.adctrl010 .sta{width:32px;height:32px;padding:5px;color:var(--gold0);transition:color .12s,transform .12s cubic-bezier(.2,0,0,1)}
.adctrl010 .sta svg{display:block}
.adctrl010 .sta.on,.adctrl010 .stars.hv .sta.hl{color:var(--gold)}
.adctrl010 .sta.on svg,.adctrl010 .stars.hv .sta.hl svg{fill:currentColor}
.adctrl010 .stars.hv .sta:not(.hl){color:var(--gold0)}
.adctrl010 .stars.hv .sta:not(.hl) svg{fill:none}
.adctrl010 .sta:hover{transform:scale(1.08)}
.adctrl010 .sta:focus:not(:focus-visible){outline:0}
.adctrl010 .sta:focus-visible{outline:2px solid var(--ink2);outline-offset:1px;border-radius:4px}
.adctrl010 .rt2{display:flex;align-items:center;gap:12px}
.adctrl010 .rtx{min-width:56px;color:var(--ink2);font-variant-numeric:tabular-nums}
.adctrl010 .ro{position:relative;display:inline-flex;height:20px}
.adctrl010 .ro .row{display:flex;gap:2px;color:var(--gold0)}
.adctrl010 .ro .row svg{width:20px;height:20px;display:block}
.adctrl010 .ro .row.f{position:absolute;left:0;top:0;overflow:hidden;color:var(--gold);white-space:nowrap}
.adctrl010 .ro .row.f svg{fill:currentColor;flex:none}
.adctrl010 .sc4{display:inline-flex;align-items:baseline;gap:8px}
.adctrl010 .sc4 b{font-size:22px;line-height:28px;font-weight:700;font-variant-numeric:tabular-nums}
.adctrl010 .scl{display:grid;grid-template-columns:repeat(11,minmax(0,1fr));gap:4px;width:100%;max-width:440px}
.adctrl010 .scl button{height:32px;border-radius:8px;border:1px solid var(--bd);background:var(--card);font-variant-numeric:tabular-nums;transition:background-color .12s,border-color .12s,color .12s}
.adctrl010 .scl button:hover{border-color:var(--bd2);background:var(--n1)}
.adctrl010 .scl button.on{background:var(--p);border-color:var(--p);color:#fff;font-weight:600}
.adctrl010 .scl button.rg2{background:var(--pt);border-color:var(--pm);color:var(--p-text)}
.adctrl010 .scl button:focus:not(:focus-visible){outline:0}
.adctrl010 .scl button:focus-visible{outline:2px solid var(--ink2);outline-offset:1px}
.adctrl010 .ends{display:flex;justify-content:space-between;width:100%;max-width:440px;margin-top:6px;font-size:12px;line-height:18px;color:var(--ink3)}
@media(max-width:520px){.adctrl010 .scl{grid-template-columns:repeat(6,minmax(0,1fr))}.adctrl010 .rt2{flex-wrap:wrap;gap:4px 12px}}`,
  html: () => `<div class="adctrl010">
<div class="sc"><h4>服务评分</h4><div class="rt2"><div class="stars" data-stars role="radiogroup" aria-label="服务评分">${starsHTML()}</div><span class="rtx" data-rtx>未评分</span></div></div>
<div class="sc"><h4>只读评分</h4><div class="rt2"><div class="ro" role="img" aria-label="平均 4.6 分"><div class="row">${sv('star').repeat(5)}</div><div class="row f" style="width:92%">${sv('star').repeat(5)}</div></div><span class="sc4"><b>4.6</b><span class="mut">1,286 条评价</span></span></div></div>
<div class="sc"><h4>推荐意愿</h4><div><div class="scl" data-scl role="radiogroup" aria-label="推荐意愿 0 到 10 分">${Array.from({ length: 11 }, (_, i) => `<button type="button" data-n="${i}" role="radio" aria-checked="false">${i}</button>`).join('')}</div><div class="ends"><span>不愿意</span><span>非常愿意</span></div></div></div>
</div>`,
  js: H((root, B) => {
    const bx = Q(B, '[data-stars]'), sts = QA(bx, '.sta'); let v = 0
    const draw = (n) => { sts.forEach((s) => { s.classList.toggle('on', +s.dataset.n <= v); s.classList.toggle('hl', +s.dataset.n <= n); s.setAttribute('aria-checked', +s.dataset.n === v); s.tabIndex = +s.dataset.n === (v || 1) ? 0 : -1 }); Q(B, '[data-rtx]').textContent = n ? `${n} 分 · ${STAR_TXT[n]}` : '未评分' }
    draw(0)
    bx.addEventListener('mouseover', (e) => { const s = e.target.closest('.sta'); if (s) { bx.classList.add('hv'); draw(+s.dataset.n) } })
    bx.addEventListener('mouseleave', () => { bx.classList.remove('hv'); draw(v) })
    bx.addEventListener('click', (e) => { const s = e.target.closest('.sta'); if (!s) return; const n = +s.dataset.n; v = n === v ? 0 : n; bx.classList.remove('hv'); draw(v) })
    bx.addEventListener('keydown', (e) => { if (e.key === 'ArrowRight' || e.key === 'ArrowUp') { e.preventDefault(); v = Math.min(5, v + 1); draw(v); sts[Math.max(0, v - 1)].focus() } else if (e.key === 'ArrowLeft' || e.key === 'ArrowDown') { e.preventDefault(); v = Math.max(0, v - 1); draw(v); sts[Math.max(0, v - 1)].focus() } })
    const sc = Q(B, '[data-scl]'), bs = QA(sc, 'button'); let nv = -1
    const drawN = (hov) => bs.forEach((b) => { const n = +b.dataset.n; b.classList.toggle('on', n === nv); b.classList.toggle('rg2', hov >= 0 && n <= hov && n !== nv); b.setAttribute('aria-checked', n === nv); b.tabIndex = n === (nv < 0 ? 0 : nv) ? 0 : -1 })
    drawN(-1)
    sc.addEventListener('mouseover', (e) => { const b = e.target.closest('button'); if (b) drawN(+b.dataset.n) })
    sc.addEventListener('mouseleave', () => drawN(-1))
    sc.addEventListener('click', (e) => { const b = e.target.closest('button'); if (b) { nv = +b.dataset.n; drawN(-1) } })
    sc.addEventListener('keydown', (e) => { if (e.key === 'ArrowRight' || e.key === 'ArrowLeft') { e.preventDefault(); nv = Math.max(0, Math.min(10, (nv < 0 ? 0 : nv) + (e.key === 'ArrowRight' ? 1 : -1))); drawN(-1); bs[nv].focus() } })
  }),
})

/* ---------- 滑块共用 ---------- */
const SLIDER_CSS = (q) => `
${q} .sl{position:relative;height:24px;margin:0 10px;touch-action:none;cursor:pointer}
${q} .sl .tk{position:absolute;left:0;right:0;top:10px;height:4px;border-radius:999px;background:var(--n6)}
${q} .sl .fl{position:absolute;top:10px;height:4px;border-radius:999px;background:var(--p)}
${q} .sl .tb{position:absolute;top:3px;width:18px;height:18px;margin-left:-9px;border-radius:50%;background:var(--card);box-shadow:inset 0 0 0 2px var(--p),0 1px 3px var(--sh22);cursor:grab;outline:0;transition:box-shadow .15s}
${q} .sl .tb:hover,${q} .sl .tb.dr{box-shadow:inset 0 0 0 2px var(--p),0 0 0 4px var(--pt),0 1px 3px var(--sh22)}
${q} .sl .tb.dr{cursor:grabbing}
${q} .sl .tb:focus-visible{outline:2px solid var(--ink2);outline-offset:3px}
${q} .sl .tip{position:absolute;left:50%;bottom:calc(100% + 8px);padding:1px 8px;border-radius:4px;background:color-mix(in srgb,var(--inv) 92%,transparent);color:#fff;font-size:12px;line-height:20px;white-space:nowrap;font-variant-numeric:tabular-nums;opacity:0;pointer-events:none;transform:translateX(-50%);transition:opacity .12s}
${q} .sl .tb:hover .tip,${q} .sl .tb.dr .tip,${q} .sl .tb:focus-visible .tip{opacity:1}
${q} .sl.dis{cursor:not-allowed}
${q} .sl.dis .fl{background:var(--n10)}
${q} .sl.dis .tb{cursor:not-allowed;box-shadow:inset 0 0 0 2px var(--n10)}
${q} .mks{position:relative;height:20px;margin:0 10px}
${q} .mks span{position:absolute;top:2px;transform:translateX(-50%);font-size:12px;line-height:18px;color:var(--ink3);font-variant-numeric:tabular-nums;white-space:nowrap}
`
const slHTML = (n, label) => `<div class="sl" data-sl>${'<i class="tk"></i><i class="fl"></i>'}${Array.from({ length: n }, (_, i) => `<span class="tb" tabindex="0" role="slider" aria-label="${label}${n > 1 ? (i ? '上限' : '下限') : ''}"><i class="tip"></i></span>`).join('')}</div>`
const mkSlider = (el, o) => {
  const { min, max, step = 1 } = o, vals = o.vals.slice(), th = QA(el, '.tb'), fl = Q(el, '.fl'), tk = Q(el, '.tk')
  const pct = (v) => ((v - min) / (max - min)) * 100
  const snap = (v) => Math.max(min, Math.min(max, Math.round((v - min) / step) * step + min))
  const draw = () => {
    th.forEach((t, i) => { t.style.left = pct(vals[i]) + '%'; t.setAttribute('aria-valuenow', vals[i]); t.setAttribute('aria-valuemin', min); t.setAttribute('aria-valuemax', max); Q(t, '.tip').textContent = (o.fmt || ((x) => x))(vals[i]) })
    fl.style.left = (vals.length > 1 ? pct(vals[0]) : 0) + '%'; fl.style.width = (vals.length > 1 ? pct(vals[1]) - pct(vals[0]) : pct(vals[0])) + '%'
  }
  const set = (i, v, user) => {
    v = snap(v); if (vals.length > 1) v = i === 0 ? Math.min(v, vals[1]) : Math.max(v, vals[0])
    if (o.clamp) v = o.clamp(i, v, vals)
    if (v === vals[i]) return false
    vals[i] = v; draw(); o.onChange && o.onChange(vals.slice(), i, user); return true
  }
  const valAt = (x) => { const r = tk.getBoundingClientRect(); return min + Math.max(0, Math.min(1, (x - r.left) / r.width)) * (max - min) }
  let cur = -1
  el.addEventListener('pointerdown', (e) => {
    if (el.classList.contains('dis')) return
    const t = e.target.closest('.tb'), v = valAt(e.clientX)
    cur = t ? th.indexOf(t) : vals.length > 1 ? (Math.abs(v - vals[0]) < Math.abs(v - vals[1]) ? 0 : Math.abs(v - vals[0]) > Math.abs(v - vals[1]) ? 1 : v > vals[1] ? 1 : 0) : 0
    el.setPointerCapture && el.setPointerCapture(e.pointerId); th[cur].classList.add('dr'); th[cur].focus(); set(cur, v, true); e.preventDefault()
  })
  el.addEventListener('pointermove', (e) => { if (cur >= 0) set(cur, valAt(e.clientX), true) })
  const up = () => { if (cur >= 0) { th[cur].classList.remove('dr'); cur = -1 } }
  el.addEventListener('pointerup', up); el.addEventListener('pointercancel', up)
  th.forEach((t, i) => t.addEventListener('keydown', (e) => {
    if (el.classList.contains('dis')) return
    const k = { ArrowRight: step, ArrowUp: step, ArrowLeft: -step, ArrowDown: -step, PageUp: step * 10, PageDown: -step * 10 }[e.key]
    if (k) { e.preventDefault(); set(i, vals[i] + k, true) } else if (e.key === 'Home') { e.preventDefault(); set(i, min, true) } else if (e.key === 'End') { e.preventDefault(); set(i, max, true) }
  }))
  draw()
  return { get: () => vals.slice(), set: (i, v) => { vals[i] = snap(v); draw() } }
}
const marksHTML = (min, max, n, fmt) => `<div class="mks" aria-hidden="true">${Array.from({ length: n }, (_, i) => { const v = min + ((max - min) * i) / (n - 1); return `<span style="left:${(i / (n - 1)) * 100}%">${fmt(v)}</span>` }).join('')}</div>`

/* ---------- AD-CTRL-011 滑块 ---------- */
def({
  id: 'AD-CTRL-011', name: '滑块', style: '单滑块范围',
  fit: '起送价、折扣、价格区间这类有上下界的数值：拖动看大致、旁边输入框精确填，两边实时同步；范围用双滑块',
  avoid: '要精确到个位且范围很大（直接用数字输入）；离散的几个档位（用分段控件）；不要只有滑块没有数值显示',
  kw: 'slider range 滑块 范围 价格区间 起送价 拖动 双滑块 刻度 数值同步',
  css: K('adctrl011', { w: 680 }) + SC_CSS('.adctrl011') + SLIDER_CSS('.adctrl011') + `
.adctrl011 .line{display:flex;align-items:center;gap:20px;width:100%}
.adctrl011 .line .box{flex:1;min-width:0}
.adctrl011 .line .ig{width:112px;flex:none}
.adctrl011 .line .ig.r2{width:auto;display:flex;align-items:center;gap:6px;border:0;background:none;overflow:visible}
.adctrl011 .line .ig.r2 .ig{width:104px}
.adctrl011 .line .ig.r2 .dsh{color:var(--ink3)}
.adctrl011 .sc>div{min-width:0}
@media(max-width:520px){.adctrl011 .line{flex-direction:column;align-items:stretch;gap:8px}.adctrl011 .line .ig{width:100%}}`,
  html: () => `<div class="adctrl011">
<div class="sc"><h4>起送价</h4><div class="line"><div class="box">${slHTML(1, '起送价')}${marksHTML(0, 200, 5, (v) => '¥' + v)}</div><div class="ig"><span class="ad">¥</span><input class="in" aria-label="起送价金额" data-one inputmode="numeric" value="50"></div></div></div>
<div class="sc"><h4>价格区间</h4><div class="line"><div class="box">${slHTML(2, '价格')}${marksHTML(0, 1000, 5, (v) => '¥' + v)}</div><div class="ig r2"><div class="ig"><span class="ad">¥</span><input class="in" aria-label="最低价" data-lo inputmode="numeric" value="100"></div><span class="dsh">至</span><div class="ig"><span class="ad">¥</span><input class="in" aria-label="最高价" data-hi inputmode="numeric" value="800"></div></div></div></div>
<div class="sc"><h4>禁用</h4><div class="line"><div class="box"><div class="sl dis" data-sl><i class="tk"></i><i class="fl" style="left:0;width:40%"></i><span class="tb" role="slider" aria-disabled="true" aria-label="禁用示例" style="left:40%"><i class="tip">80</i></span></div></div><span class="mut" style="width:112px">仅店长可调整</span></div></div>
</div>`,
  js: H((root, B) => {
    const sls = QA(B, '[data-sl]'), one = Q(B, '[data-one]'), lo = Q(B, '[data-lo]'), hi = Q(B, '[data-hi]')
    const a = mkSlider(sls[0], { min: 0, max: 200, step: 10, vals: [50], fmt: (v) => '¥' + v, onChange: (v) => (one.value = v[0]) })
    const r = mkSlider(sls[1], { min: 0, max: 1000, step: 50, vals: [100, 800], fmt: (v) => '¥' + v, onChange: (v) => { lo.value = v[0]; hi.value = v[1] } })
    const fix = (inp, f) => inp.addEventListener('change', () => { const n = parseInt(inp.value, 10); f(isNaN(n) ? NaN : n) })
    fix(one, (n) => { if (!isNaN(n)) a.set(0, n); one.value = a.get()[0] })
    fix(lo, (n) => { if (!isNaN(n)) r.set(0, Math.min(n, r.get()[1])); lo.value = r.get()[0] })
    fix(hi, (n) => { if (!isNaN(n)) r.set(1, Math.max(n, r.get()[0])); hi.value = r.get()[1] })
  }),
})

/* ---------- AD-CTRL-012 比例分配滑块 ---------- */
const PRIZES = [['一等奖', 1, 'p1'], ['二等奖', 5, 'p2'], ['三等奖', 20, 'p3']]
def({
  id: 'AD-CTRL-012', name: '比例分配滑块', style: '总和约束',
  fit: '中奖概率、分成比例、库存配比这类“几项之和必须等于 100%”的参数：拖动其中几项，剩下一项自动补齐，不让人手算',
  avoid: '各项互相独立的数值（用单滑块）；总和不是固定值时不用补齐；超过 5 项时拖动会互相牵制，改成表格逐行填',
  kw: 'ratio 比例 概率 分配 总和 100% 自动补齐 中奖概率 分成 占比',
  css: K('adctrl012', { w: 680 }) + SLIDER_CSS('.adctrl012') + `
.adctrl012{padding:20px 24px 16px}
.adctrl012 .stk{display:flex;height:12px;border-radius:999px;overflow:hidden;background:var(--n6);gap:2px}
.adctrl012 .stk i{display:block;height:100%;min-width:0;transition:width .12s linear}
.adctrl012 .stk .p1{background:var(--pd)}
.adctrl012 .stk .p2{background:var(--p)}
.adctrl012 .stk .p3{background:var(--pm)}
.adctrl012 .stk .p4{background:var(--n9)}
.adctrl012 .lg2{display:flex;flex-wrap:wrap;gap:4px 16px;margin:8px 0 12px;font-size:12px;line-height:18px;color:var(--ink2)}
.adctrl012 .lg2 span{display:inline-flex;align-items:center;gap:6px}
.adctrl012 .lg2 span::before{content:"";width:8px;height:8px;border-radius:999px;background:currentColor}
.adctrl012 .lg2 .p1{color:var(--p-text)}.adctrl012 .lg2 .p2{color:var(--p-fg)}.adctrl012 .lg2 .p3{color:var(--pm)}.adctrl012 .lg2 .p4{color:var(--n9)}
.adctrl012 .lg2 span b{font-weight:400;color:var(--ink2)}
.adctrl012 .pr{display:grid;grid-template-columns:72px minmax(0,1fr) 64px;align-items:center;gap:0 16px;min-height:44px}
.adctrl012 .pr>b{font-weight:600}
.adctrl012 .pr .v{text-align:right;font-weight:600;font-variant-numeric:tabular-nums}
.adctrl012 .pr.auto .tk,.adctrl012 .pr.auto .fl{background:var(--n9)}
.adctrl012 .pr.auto .sl{cursor:default;pointer-events:none}
.adctrl012 .pr.auto .v{color:var(--ink2)}
.adctrl012 .pr.auto .nt{color:var(--ink3)}
.adctrl012 .pr .nt{grid-column:2/4;margin-top:-6px;font-size:12px;line-height:18px;color:var(--wn);min-height:18px}
.adctrl012 .sum2{display:flex;align-items:center;justify-content:space-between;margin-top:8px;padding-top:12px;border-top:1px solid var(--line);color:var(--ink2)}
.adctrl012 .sum2 b{color:var(--ok);font-weight:600;font-variant-numeric:tabular-nums}
@media(max-width:520px){.adctrl012{padding:16px}.adctrl012 .pr{grid-template-columns:56px minmax(0,1fr) 48px;gap:0 10px}}`,
  html: () => `<div class="adctrl012"><div class="stk" data-stk>${PRIZES.map(([, , c]) => `<i class="${c}"></i>`).join('')}<i class="p4"></i></div>
<div class="lg2">${PRIZES.map(([n, , c]) => `<span class="${c}"><b>${n}</b></span>`).join('')}<span class="p4"><b>谢谢参与</b></span></div>
${PRIZES.map(([n]) => `<div class="pr" data-pr><b>${n}</b>${slHTML(1, n)}<span class="v" data-v></span><span class="nt" data-nt role="status"></span></div>`).join('')}
<div class="pr auto"><b>谢谢参与</b><div class="sl dis" data-auto aria-hidden="true"><i class="tk"></i><i class="fl"></i></div><span class="v" data-v></span><span class="nt">自动补齐，不可拖动</span></div>
<div class="sum2"><span>四项合计</span><b>100%</b></div></div>`,
  js: H((root, B) => {
    const prs = QA(B, '[data-pr]'), auto = Q(B, '[data-auto]').parentNode, ss = []
    const rest = () => 100 - ss.reduce((s, x) => s + x.get()[0], 0)
    const paint = () => {
      const vs = ss.map((x) => x.get()[0]), ap = 100 - vs.reduce((a, b) => a + b, 0)
      QA(B, '.stk i').forEach((i, k) => (i.style.width = (k < 3 ? vs[k] : ap) + '%'))
      prs.forEach((p, i) => (Q(p, '[data-v]').textContent = vs[i] + '%'))
      Q(auto, '[data-v]').textContent = ap + '%'; Q(auto, '.fl').style.width = ap + '%'
      QA(B, '.lg2 span b').forEach((b, k) => (b.textContent = `${[...PRIZES.map((p) => p[0]), '谢谢参与'][k]} ${k < 3 ? vs[k] : ap}%`))
    }
    prs.forEach((p, i) => {
      ss[i] = mkSlider(Q(p, '[data-sl]'), {
        min: 0, max: 100, step: 1, vals: [PRIZES[i][1]], fmt: (v) => v + '%',
        clamp: (k, v) => { const others = ss.reduce((s, x, j) => s + (j === i || !x ? 0 : x.get()[0]), 0), mx = 100 - others; if (v > mx) { const nt = Q(p, '[data-nt]'); nt.textContent = '已达上限，其余项合计 ' + others + '%'; clearTimeout(nt.__t); nt.__t = setTimeout(() => (nt.textContent = ''), 1800); return mx } Q(p, '[data-nt]').textContent = ''; return v },
        onChange: paint,
      })
    })
    paint()
  }),
})

/* ---------- AD-CTRL-013 标签输入 ---------- */
const EMAIL_RE = /^[^\s@，,;；]+@[^\s@，,;；]+\.[^\s@，,;；]+$/
def({
  id: 'AD-CTRL-013', name: '标签输入', style: '回车添加',
  fit: '商品标签、关键词、收件邮箱这类条数不固定的短文本：回车或逗号添加，点 × 或退格删除，重复会提示，到上限自动停手',
  avoid: '每项文字很长（改用动态增减行）；选项是固定可选的几个（用多选下拉）；上限很大时要显示已添加数量',
  kw: 'tag input 标签输入 回车添加 删除 关键词 邮箱 收件人 重复提示 上限',
  css: K('adctrl013', { w: 680 }) + SC_CSS('.adctrl013') + TAGI_CSS('.adctrl013') + `
.adctrl013 .box{width:100%;max-width:460px}
.adctrl013 .meta{display:flex;align-items:flex-start;justify-content:space-between;gap:12px}
.adctrl013 .meta .er{flex:1;margin-top:4px}
.adctrl013 .meta .n{margin-top:4px;font-size:12px;line-height:18px;color:var(--ink3);font-variant-numeric:tabular-nums}
.adctrl013 .sug{display:flex;flex-wrap:wrap;align-items:center;gap:6px;margin-top:6px}
.adctrl013 .sug>span{font-size:12px;color:var(--ink3)}
.adctrl013 .sug button{height:24px;padding:0 8px;border:1px dashed var(--bd2);border-radius:4px;font-size:12px;color:var(--ink2);transition:border-color .15s,color .15s,background-color .15s}
.adctrl013 .sug button:hover{border-color:var(--p);color:var(--p-text);background:var(--pt)}
.adctrl013 .sug button.dis{border-style:solid;border-color:var(--bd0);background:var(--mub);color:var(--ink4);cursor:not-allowed}
.adctrl013 .sug button:focus:not(:focus-visible){outline:0}
.adctrl013 .sug button:focus-visible{outline:2px solid var(--ink2);outline-offset:1px}
.adctrl013 .f.bad .tgi{border-color:var(--dg)}`,
  html: () => `<div class="adctrl013">
<div class="sc"><h4>商品标签</h4><div class="box"><div class="tgi" data-tags="a">${['新品', '热卖', '包邮'].map((t) => tagHTML(t)).join('')}<input class="tin" aria-label="添加商品标签" placeholder="输入后回车添加"></div>
<div class="meta"><span class="er" data-er="a" role="alert"></span><span class="n" data-n="a"></span></div>
<div class="sug" data-sug="a"><span>常用</span>${['限时', '现货', '买一送一', '会员专享', '新客首单'].map((t) => `<button type="button" data-s="${t}">${ic('plus', 12)}${t}</button>`).join('')}</div></div></div>
<div class="sc"><h4>收件邮箱</h4><div class="box f" data-f="mail"><div class="tgi" data-tags="b">${tagHTML('zhou.yifan@example.com')}${tagHTML('finance@example', 'dg')}<input class="tin" aria-label="添加收件邮箱" placeholder="输入或粘贴，多个用逗号分隔"></div>
<div class="meta"><span class="er" data-er="b" role="alert"></span></div></div></div>
</div>`,
  js: H((root, B) => {
    const A = Q(B, '[data-tags=a]'), erA = Q(B, '[data-er=a]'), sug = Q(B, '[data-sug=a]')
    const ta = mkTags(A, { max: 8, er: erA, onChange: (t) => { Q(B, '[data-n=a]').textContent = `${t.length}/8`; QA(sug, '[data-s]').forEach((b) => { const has = t.includes(b.dataset.s) || t.length >= 8; b.classList.toggle('dis', has); b.setAttribute('aria-disabled', has) }) } })
    sug.addEventListener('click', (e) => { const b = e.target.closest('[data-s]'); if (b && !b.classList.contains('dis')) ta.add(b.dataset.s) })
    const Bt = Q(B, '[data-tags=b]'), erB = Q(B, '[data-er=b]'), fB = Q(B, '[data-f=mail]')
    const chk = () => { const bad = QA(Bt, '[data-tag]').filter((x) => x.classList.contains('dg')).length; fB.classList.toggle('bad', bad > 0); erB.textContent = bad ? `${bad} 个邮箱格式不对，已标红，请修改后重新添加` : '' }
    mkTags(Bt, { max: 20, len: 40, ph: '输入或粘贴，多个用逗号分隔', cls: (t) => (EMAIL_RE.test(t) ? 'pri' : 'dg'), er: null, onChange: chk })
  }),
})

/* ---------- AD-CTRL-014 颜色选择 ---------- */
const hexOk = (h) => /^#?([0-9a-f]{3}|[0-9a-f]{6})$/i.test(h.trim())
const hexNorm = (h) => { let x = h.trim().replace('#', '').toUpperCase(); if (x.length === 3) x = x.split('').map((c) => c + c).join(''); return '#' + x }
const lumOf = (h) => { const c = hex2(h).map((v) => { v /= 255; return v <= 0.03928 ? v / 12.92 : Math.pow((v + 0.055) / 1.055, 2.4) }); return 0.2126 * c[0] + 0.7152 * c[1] + 0.0722 * c[2] }
const COLORS = [...THEMES.map((t) => [t.p, t.name]), ...THEMES.slice(0, 4).map((t) => [t.pm, t.name + '浅'])]
def({
  id: 'AD-CTRL-014', name: '颜色选择', style: '色板与色值',
  fit: '标签颜色、分类色、主题色设置：先给一套低饱和的预设色板，点选即用；需要品牌色时再手填色值，并保留最近使用',
  avoid: '给用户整张任意取色盘（容易选出刺眼的颜色）；颜色单独表达含义（要配文字）；色板超过 16 个会难以挑选',
  kw: 'color picker 颜色 色板 取色 标签颜色 十六进制 hex 最近使用 主题色',
  css: K('adctrl014', { w: 640 }) + `
.adctrl014{min-height:400px;padding:20px 24px 24px}
.adctrl014 .box{max-width:360px}
.adctrl014 .cw{position:relative}
.adctrl014 .cb2{display:flex;align-items:center;gap:10px;width:100%;height:32px;padding:0 8px 0 6px;border:1px solid var(--bd);border-radius:8px;background:var(--card);text-align:left;transition:border-color .15s}
.adctrl014 .cb2:hover{border-color:var(--bd2)}
.adctrl014 .cw.open .cb2{border-color:var(--ink2)}
.adctrl014 .cb2:focus:not(:focus-visible){outline:0}
.adctrl014 .cb2:focus-visible{outline:2px solid var(--ink2);outline-offset:2px}
.adctrl014 .sw3{width:20px;height:20px;flex:none;border-radius:4px;box-shadow:inset 0 0 0 1px var(--sh12)}
.adctrl014 .cb2 .hx{flex:1;font-variant-numeric:tabular-nums}
.adctrl014 .cb2 .ic{color:var(--ink3);transition:transform .2s cubic-bezier(.2,0,0,1)}
.adctrl014 .cw.open .cb2 .ic{transform:rotate(180deg)}
.adctrl014 .pn{position:absolute;left:0;top:calc(100% + 6px);z-index:25;width:288px;padding:12px;border:1px solid var(--bd0);border-radius:12px;background:var(--card2);box-shadow:var(--sh3);animation:admdl .18s cubic-bezier(.2,0,0,1)}
.adctrl014 .pn[hidden]{display:none}
.adctrl014 .pn h5{margin:0 0 8px;font-size:12px;line-height:18px;font-weight:600;color:var(--ink3)}
.adctrl014 .pal{display:grid;grid-template-columns:repeat(6,1fr);gap:8px}
.adctrl014 .pal button,.adctrl014 .rec button{position:relative;width:100%;aspect-ratio:1/1;border-radius:8px;box-shadow:inset 0 0 0 1px var(--sh12);transition:transform .12s cubic-bezier(.2,0,0,1)}
.adctrl014 .pal button:hover,.adctrl014 .rec button:hover{transform:scale(1.06)}
.adctrl014 .pal button.on::after,.adctrl014 .rec button.on::after{content:"";position:absolute;left:50%;top:50%;width:6px;height:11px;margin:-7px 0 0 -3px;border:solid var(--ck,var(--card));border-width:0 2px 2px 0;transform:rotate(45deg)}
.adctrl014 .pal button.on,.adctrl014 .rec button.on{box-shadow:inset 0 0 0 1px var(--sh12),0 0 0 2px var(--card),0 0 0 4px var(--ink2)}
.adctrl014 .pal button:focus:not(:focus-visible),.adctrl014 .rec button:focus:not(:focus-visible){outline:0}
.adctrl014 .pal button:focus-visible,.adctrl014 .rec button:focus-visible{outline:2px solid var(--ink2);outline-offset:2px}
.adctrl014 .rec{display:grid;grid-template-columns:repeat(6,1fr);gap:8px;margin-top:0}
.adctrl014 .sec2{margin-top:12px}
.adctrl014 .hxr{display:flex;align-items:flex-start;gap:8px;margin-top:12px;padding-top:12px;border-top:1px solid var(--line)}
.adctrl014 .hxr .f{flex:1;min-width:0}
.adctrl014 .hxr .er{min-height:18px}
.adctrl014 .prv{display:flex;align-items:center;gap:8px;margin-top:4px}
.adctrl014 .prv .tag{height:24px;font-size:12px}
.adctrl014 .prv .chip{display:inline-flex;align-items:center;height:24px;padding:0 10px;border-radius:4px;font-size:12px;font-weight:600}
@media(max-width:520px){.adctrl014{padding:16px}.adctrl014 .pn{width:min(288px,calc(100vw - 48px))}}`,
  html: () => `<div class="adctrl014"><div class="box"><div class="f"><label class="lb" id="clr-l">标签颜色</label><div class="cw" data-cw><button type="button" class="cb2" aria-haspopup="dialog" aria-expanded="false" aria-labelledby="clr-l"><span class="sw3" data-sw></span><span class="hx" data-hx></span>${ic('down')}</button>
<div class="pn" hidden role="dialog" aria-label="选择颜色"><h5>预设色板</h5><div class="pal" role="radiogroup" aria-label="预设色板">${COLORS.map(([c, n]) => `<button type="button" data-c="${c}" style="background:${c};--ck:${lumOf(c) > 0.45 ? '#1F2329' : '#fff'}" role="radio" aria-checked="false" aria-label="${n} ${c}" title="${n}"></button>`).join('')}</div>
<div class="sec2" data-recw hidden><h5>最近使用</h5><div class="rec" data-rec></div></div>
<div class="hxr"><div class="f" data-f="hex"><div class="ig"><span class="ad">#</span><input class="in" data-hexin aria-label="色值" maxlength="7" placeholder="A85D79" autocomplete="off"></div><span class="er" role="alert"></span></div><div class="prv" data-prv></div></div></div></div></div></div></div>`,
  js: H((root, B) => {
    const cw = Q(B, '[data-cw]'), tr = Q(cw, '.cb2'), pn = Q(cw, '.pn'), hexIn = Q(B, '[data-hexin]'), f = Q(B, '[data-f=hex]'); let cur = '#A85D79', recent = []
    const tint = (c) => mixc(c, '#FFFFFF', 0.14)
    const ink = (c) => (lumOf(c) > 0.45 ? '#1F2329' : '#FFFFFF')
    const darkText = (c) => { let t = c; while (lumOf(t) > 0.18) t = mixc(t, '#000000', 0.85); return t }
    const draw = () => {
      Q(B, '[data-sw]').style.background = cur; Q(B, '[data-hx]').textContent = cur
      QA(pn, '.pal button,.rec button').forEach((b) => { const on = b.dataset.c.toUpperCase() === cur; b.classList.toggle('on', on); b.setAttribute('aria-checked', on) })
      hexIn.value = cur.slice(1)
      Q(B, '[data-prv]').innerHTML = `<span class="chip" style="background:${cur};color:${ink(cur)}">进行中</span><span class="tag" style="background:${tint(cur)};color:${darkText(cur)}">进行中</span>`
      const rw = Q(B, '[data-recw]'); rw.hidden = !recent.length
      Q(B, '[data-rec]').innerHTML = recent.map((c) => `<button type="button" data-c="${c}" style="background:${c};--ck:${ink(c)}" role="radio" aria-checked="false" aria-label="最近使用 ${c}"></button>`).join('')
      QA(pn, '.rec button').forEach((b) => b.classList.toggle('on', b.dataset.c === cur))
    }
    const pick = (c, remember) => { cur = hexNorm(c); if (remember) { recent = [cur, ...recent.filter((x) => x !== cur)].slice(0, 6) } f.classList.remove('bad'); Q(f, '.er').textContent = ''; draw() }
    const open = () => { pn.hidden = false; cw.classList.add('open'); tr.setAttribute('aria-expanded', 'true') }
    const close = () => { pn.hidden = true; cw.classList.remove('open'); tr.setAttribute('aria-expanded', 'false') }
    tr.addEventListener('click', () => (cw.classList.contains('open') ? close() : open()))
    pn.addEventListener('click', (e) => { const b = e.target.closest('[data-c]'); if (b) pick(b.dataset.c, true) })
    const commit = () => { const v = hexIn.value.trim(); if (!v) return; if (!hexOk(v)) { f.classList.add('bad'); Q(f, '.er').textContent = '请输入 3 或 6 位色值，如 A85D79'; return } pick(v, true) }
    hexIn.addEventListener('keydown', (e) => { if (e.key === 'Enter') { e.preventDefault(); commit() } })
    hexIn.addEventListener('blur', commit)
    hexIn.addEventListener('input', () => { if (f.classList.contains('bad')) { f.classList.remove('bad'); Q(f, '.er').textContent = '' } })
    cw.addEventListener('keydown', (e) => { if (e.key === 'Escape' && cw.classList.contains('open')) { e.stopPropagation(); close(); tr.focus() } })
    cw.addEventListener('focusout', (e) => { if (!cw.contains(e.relatedTarget)) close() })
    pn.addEventListener('mousedown', (e) => { if (!e.target.closest('input')) e.preventDefault() })
    draw()
  }),
})

/* ---------- AD-CTRL-015 头像组与进度条 ---------- */
const PEOPLE7 = NAMES.slice(0, 7).map((n, i) => ({ n, d: DEPTS[i % 6] }))
const ring = (pct, cls = '') => { const r = 22, c = 2 * Math.PI * r; return `<svg class="rg3 ${cls}" width="56" height="56" viewBox="0 0 56 56" role="img" aria-label="完成 ${pct}%"><circle cx="28" cy="28" r="${r}" fill="none" stroke="var(--n6)" stroke-width="5"/><circle cx="28" cy="28" r="${r}" fill="none" stroke="currentColor" stroke-width="5" stroke-linecap="round" stroke-dasharray="${(c * pct) / 100} ${c}" transform="rotate(-90 28 28)"/><text x="28" y="33" text-anchor="middle" font-size="14" font-weight="600" fill="var(--ink)">${pct}%</text></svg>` }
def({
  id: 'AD-CTRL-015', name: '头像组与进度条', style: '叠放与状态',
  fit: '负责人、协作成员的叠放头像（悬停看姓名、点“+N”展开）；导入导出、批量处理、审批进度的进度条，要有成功与失败两种结果',
  avoid: '头像用姓氏或首字母代替（只用默认卡通动物或照片）；进度条没有数值或失败后没有“重试”；超过 10 秒的任务要显示已用时',
  kw: 'avatar group 头像组 叠放 进度条 progress 环形 分段 上传进度 失败重试',
  css: K('adctrl015', { w: 680 }) + SC_CSS('.adctrl015') + `
.adctrl015{color-scheme:light}
.adctrl015 .stk2{display:flex;align-items:center;flex-wrap:wrap}
.adctrl015 .stk2 .m{position:relative;display:inline-flex;margin-left:-8px;border-radius:50%;box-shadow:0 0 0 2px var(--card);transition:transform .15s cubic-bezier(.2,0,0,1)}
.adctrl015 .stk2 .m:first-child{margin-left:0}
.adctrl015 .stk2 .m:hover{transform:translateY(-2px);z-index:2}
.adctrl015 .stk2 .m[data-tip]::after{content:attr(data-tip);position:absolute;left:50%;bottom:calc(100% + 6px);z-index:5;padding:3px 8px;border-radius:4px;background:color-mix(in srgb,var(--inv) 92%,transparent);color:#fff;font-size:12px;line-height:18px;white-space:nowrap;opacity:0;pointer-events:none;transform:translate(-50%,2px);transition:opacity .15s,transform .15s}
.adctrl015 .stk2 .m[data-tip]:hover::after,.adctrl015 .stk2 .m[data-tip]:focus-visible::after{opacity:1;transform:translate(-50%,0)}
.adctrl015 .stk2 .m:focus:not(:focus-visible){outline:0}
.adctrl015 .stk2 .m:focus-visible{outline:2px solid var(--ink2);outline-offset:2px}
.adctrl015 .stk2 .more{display:inline-flex;align-items:center;justify-content:center;width:32px;height:32px;margin-left:-8px;border-radius:50%;background:var(--soft);box-shadow:0 0 0 2px var(--card);font-size:12px;font-weight:600;color:var(--ink2);transition:background-color .15s}
.adctrl015 .stk2 .more:hover{background:var(--n5)}
.adctrl015 .stk2.open .m{margin-left:6px}
.adctrl015 .stk2.open .m:first-child{margin-left:0}
.adctrl015 .stk2.open .more{margin-left:6px}
.adctrl015 .szs{display:flex;align-items:flex-end;gap:20px}
.adctrl015 .szs .cap .stk2 .m{margin-left:-6px}
.adctrl015 .szs .cap .stk2 .m:first-child{margin-left:0}
.adctrl015 .pg3{display:grid;grid-template-columns:96px minmax(0,1fr) 96px;align-items:center;gap:0 12px;min-height:32px}
.adctrl015 .pg3>span:first-child{color:var(--ink2)}
.adctrl015 .pg3 .v{text-align:right;font-variant-numeric:tabular-nums;color:var(--ink2)}
.adctrl015 .pb{height:6px;border-radius:999px;background:var(--n6);overflow:hidden}
.adctrl015 .pb i{display:block;height:100%;border-radius:999px;background:var(--p);transition:width .2s linear}
.adctrl015 .pg3.ok .pb i{background:var(--ok-fill)}
.adctrl015 .pg3.ok .v{color:var(--ok);display:inline-flex;align-items:center;justify-content:flex-end;gap:4px}
.adctrl015 .pg3.bad .pb i{background:var(--danger-fill)}
.adctrl015 .pg3.bad .v{color:var(--dg)}
.adctrl015 .pg3 .v .ic{width:14px;height:14px}
.adctrl015 .pg3 .lnk{color:var(--p-text);text-decoration:underline;text-underline-offset:3px;margin-left:6px}
.adctrl015 .seg5{display:flex;gap:3px}
.adctrl015 .seg5 i{flex:1;height:6px;border-radius:999px;background:var(--n6)}
.adctrl015 .seg5 i.on{background:var(--p)}
.adctrl015 .rgs{display:flex;gap:24px;align-items:center}
.adctrl015 .rg3{color:var(--p-fg)}
.adctrl015 .rg3.ok{color:var(--ok)}
.adctrl015 .demo{display:flex;flex-direction:column;gap:12px;width:100%}
@media(max-width:520px){.adctrl015 .pg3{grid-template-columns:72px minmax(0,1fr) 72px;gap:0 8px}}`,
  html: () => `<div class="adctrl015">
<div class="sc"><h4>头像组</h4><div class="stk2" data-stk role="group" aria-label="协作成员">${PEOPLE7.slice(0, 4).map((p, i) => `<span class="m" tabindex="0" data-tip="${p.n} · ${p.d}">${critter(i, 32)}</span>`).join('')}<button type="button" class="more" data-more aria-expanded="false" aria-label="展开其余 3 人">+3</button></div></div>
<div class="sc"><h4>尺寸</h4><div class="szs"><div class="cap"><div class="stk2">${[0, 1, 2].map((i) => `<span class="m">${critter(i, 24)}</span>`).join('')}</div><small>24 · 表格行</small></div><div class="cap"><div class="stk2">${[0, 1, 2].map((i) => `<span class="m">${critter(i, 32)}</span>`).join('')}</div><small>32 · 列表与卡片</small></div><div class="cap"><div class="stk2">${[0, 1, 2].map((i) => `<span class="m">${critter(i, 40)}</span>`).join('')}</div><small>40 · 详情页头</small></div></div></div>
<div class="sc"><h4>线形进度</h4><div class="demo">
<div class="pg3"><span>库存周转</span><div class="pb" role="progressbar" aria-valuenow="62" aria-valuemin="0" aria-valuemax="100"><i style="width:62%"></i></div><span class="v">62%</span></div>
<div class="pg3 ok"><span>订单导出</span><div class="pb" role="progressbar" aria-valuenow="100"><i style="width:100%"></i></div><span class="v">${ic('check')}已完成</span></div>
<div class="pg3 bad"><span>会员导入</span><div class="pb" role="progressbar" aria-valuenow="45"><i style="width:45%"></i></div><span class="v">失败</span></div>
<div class="pg3" data-demo><span>上传报表</span><div class="pb" role="progressbar" aria-valuenow="0"><i style="width:0"></i></div><span class="v" data-dv>未开始</span></div>
<div><button type="button" class="bt bt-s" data-go>${ic('upload')}开始上传</button></div></div></div>
<div class="sc"><h4>分段与环形</h4><div class="rgs"><div class="cap"><div style="width:160px"><div class="seg5" role="progressbar" aria-valuenow="3" aria-valuemax="5"><i class="on"></i><i class="on"></i><i class="on"></i><i></i><i></i></div></div><small>审批 3/5</small></div><div class="cap">${ring(72)}<small>目标完成率</small></div><div class="cap">${ring(100, 'ok')}<small>已达成</small></div></div></div>
</div>`,
  js: H((root, B) => {
    const stk = Q(B, '[data-stk]'), more = Q(B, '[data-more]'); let open = false
    const draw = () => {
      QA(stk, '.m.x').forEach((x) => x.remove())
      if (open) { more.insertAdjacentHTML('beforebegin', PEOPLE7.slice(4).map((p, i) => `<span class="m x" tabindex="0" data-tip="${p.n} · ${p.d}">${critter(i + 4, 32)}</span>`).join('')) }
      stk.classList.toggle('open', open); more.textContent = open ? '收起' : '+3'; more.setAttribute('aria-expanded', open); more.setAttribute('aria-label', open ? '收起成员' : '展开其余 3 人')
      more.style.width = open ? 'auto' : ''; more.style.padding = open ? '0 10px' : ''; more.style.borderRadius = open ? '16px' : ''
    }
    more.addEventListener('click', () => { open = !open; draw() })
    const row = Q(B, '[data-demo]'), bar = Q(row, '.pb i'), pb = Q(row, '.pb'), dv = Q(row, '[data-dv]'), go = Q(B, '[data-go]'); let runs = 0, iv = null
    const setP = (p) => { bar.style.width = p + '%'; pb.setAttribute('aria-valuenow', p) }
    const status = (cls, html) => { row.classList.remove('ok', 'bad'); if (cls) row.classList.add(cls); dv.innerHTML = html }
    const start = (from, failAt) => {
      clearInterval(iv); let p = from; go.classList.add('dis'); status('', `${p}%`)
      iv = setInterval(() => {
        if (!row.isConnected) { clearInterval(iv); return }
        p += 5; setP(Math.min(p, 100)); status('', `${Math.min(p, 100)}%`)
        if (failAt && p >= failAt) { clearInterval(iv); status('bad', `失败<button type="button" class="lnk" data-retry>重试</button>`); go.classList.remove('dis'); go.lastChild.textContent = '重新上传' }
        else if (p >= 100) { clearInterval(iv); status('ok', `${ic('check')}已完成`); go.classList.remove('dis'); go.lastChild.textContent = '再传一次'; tst(B, '报表已上传') }
      }, 110)
    }
    go.addEventListener('click', () => { if (go.classList.contains('dis')) return; runs++; setP(0); start(0, runs % 2 === 0 ? 60 : 0) })
    row.addEventListener('click', (e) => { if (e.target.closest('[data-retry]')) start(Math.round(+pb.getAttribute('aria-valuenow') / 5) * 5, 0) })
  }),
})

/* ---------- AD-CTRL-016 数字输入 ---------- */
const stpHTML = (o) => `<div class="stp${o.dis ? ' dis' : ''}" data-stp data-min="${o.min}" data-max="${o.max}" data-step="${o.step}" data-dec2="${o.dec || 0}"><button type="button" data-dec aria-label="减少" ${o.dis ? 'tabindex="-1"' : ''}>${ic('minus')}</button><input class="nin" inputmode="${o.dec ? 'decimal' : 'numeric'}" aria-label="${o.label}" value="${o.v}" ${o.dis ? 'disabled' : ''}>${o.unit ? `<span class="un">${o.unit}</span>` : ''}<button type="button" data-inc aria-label="增加" ${o.dis ? 'tabindex="-1"' : ''}>${ic('plus')}</button></div>`
def({
  id: 'AD-CTRL-016', name: '数字输入', style: '步进与金额',
  fit: '数量、天数、百分比用步进输入（点 ± 或方向键，到边界按钮置灰）；金额用自由输入：前缀 ¥、两位小数，失焦补零',
  avoid: '金额给预设档位代替输入；范围很大的数值（用滑块加输入框）；超出范围时直接清空，应夹回边界并说明范围',
  kw: 'number input 数字输入 步进 数量 金额 小数 百分比 加减 边界',
  css: K('adctrl016', { w: 680 }) + SC_CSS('.adctrl016') + `
.adctrl016 .stp{display:inline-flex;align-items:center;height:32px;border:1px solid var(--bd);border-radius:8px;overflow:hidden;background:var(--card);transition:border-color .15s}
.adctrl016 .stp:hover{border-color:var(--bd2)}
.adctrl016 .stp:focus-within{border-color:var(--ink2)}
.adctrl016 .stp button{display:inline-flex;align-items:center;justify-content:center;width:32px;height:30px;color:var(--ink2);transition:background-color .12s}
.adctrl016 .stp button:hover{background:var(--mub)}
.adctrl016 .stp button:active{background:var(--n5)}
.adctrl016 .stp button.dis{color:color-mix(in srgb,var(--ink6) 56%,var(--ink5));cursor:not-allowed;background:none}
.adctrl016 .stp button:focus:not(:focus-visible){outline:0}
.adctrl016 .stp button:focus-visible{outline:2px solid var(--ink2);outline-offset:-2px}
.adctrl016 .stp .nin{width:64px;height:30px;padding:0 4px;border:0;border-left:1px solid var(--line);border-right:1px solid var(--line);border-radius:0;outline:0;background:none;text-align:center;font:inherit;font-variant-numeric:tabular-nums;color:var(--ink)}
.adctrl016 .stp .un{align-self:stretch;display:flex;align-items:center;padding:0 8px 0 0;margin-left:-2px;color:var(--ink3);border-right:1px solid var(--line)}
.adctrl016 .stp.un2 .nin{border-right:0;width:52px}
.adctrl016 .stp.dis{background:var(--mub);border-color:var(--bd0);cursor:not-allowed}
.adctrl016 .stp.dis .nin{color:var(--ink3)}
.adctrl016 .stp.dis button{color:color-mix(in srgb,var(--ink6) 56%,var(--ink5));cursor:not-allowed}
.adctrl016 .stp.dis button:hover{background:none}
.adctrl016 .bx{width:100%;max-width:300px}
.adctrl016 .bx .f.bad .ig,.adctrl016 .bx .f.bad .ig:focus-within{border-color:var(--dg)}
.adctrl016 .rw3{display:flex;align-items:center;gap:12px}
.adctrl016 .rn{font-size:12px;line-height:18px;color:var(--ink3)}
.adctrl016 .stp.bad{border-color:var(--dg)}`,
  html: () => `<div class="adctrl016">
<div class="sc"><h4>数量步进</h4><div class="f"><div class="rw3">${stpHTML({ min: 1, max: 99, step: 1, v: 1, label: '购买数量' })}<span class="rn">范围 1–99</span></div><span class="er" role="alert"></span></div></div>
<div class="sc"><h4>金额</h4><div class="bx"><div class="f" data-f="money"><div class="ig"><span class="ad">¥</span><input class="in" aria-label="金额" data-money inputmode="decimal" value="128.00"><span class="sx">元</span></div><span class="er" role="alert"></span></div></div></div>
<div class="sc"><h4>百分比</h4><div class="f"><div class="rw3">${stpHTML({ min: 0, max: 100, step: 5, v: 15, label: '折扣比例', unit: '%' }).replace('class="stp"', 'class="stp un2"')}<span class="rn">范围 0–100，每次 5</span></div><span class="er" role="alert"></span></div></div>
<div class="sc"><h4>禁用</h4><div>${stpHTML({ min: 1, max: 99, step: 1, v: 3, label: '禁用示例', dis: 1 })}</div></div>
</div>`,
  js: H((root, B) => {
    QA(B, '[data-stp]:not(.dis)').forEach((el) => {
      const inp = Q(el, '.nin'), mn = +el.dataset.min, mx = +el.dataset.max, st = +el.dataset.step, f = el.closest('.f'), er = Q(f, '.er')
      const clamp = (n) => Math.max(mn, Math.min(mx, n))
      const sync = () => { const v = +inp.value; Q(el, '[data-dec]').classList.toggle('dis', v <= mn); Q(el, '[data-inc]').classList.toggle('dis', v >= mx); Q(el, '[data-dec]').setAttribute('aria-disabled', v <= mn); Q(el, '[data-inc]').setAttribute('aria-disabled', v >= mx) }
      const msg = (t) => { er.textContent = t; el.classList.toggle('bad', !!t) }
      const set = (n, note) => { const c = clamp(n); inp.value = c; sync(); msg(note && c !== n ? `已调整为${c === mn ? '最小' : '最大'}值 ${c}` : '') }
      el.addEventListener('click', (e) => { const b = e.target.closest('button'); if (!b || b.classList.contains('dis')) return; set(+inp.value + (b.hasAttribute('data-inc') ? st : -st)) })
      inp.addEventListener('input', () => { inp.value = inp.value.replace(/[^\d]/g, ''); msg('') })
      inp.addEventListener('blur', () => set(inp.value === '' ? mn : parseInt(inp.value, 10), true))
      inp.addEventListener('keydown', (e) => { if (e.key === 'ArrowUp') { e.preventDefault(); set((parseInt(inp.value, 10) || mn) + st) } else if (e.key === 'ArrowDown') { e.preventDefault(); set((parseInt(inp.value, 10) || mn) - st) } else if (e.key === 'Enter') { e.preventDefault(); set(inp.value === '' ? mn : parseInt(inp.value, 10), true) } })
      sync()
    })
    const mi = Q(B, '[data-money]'), mf = mi.closest('.f'), me = Q(mf, '.er')
    const money = () => {
      const v = mi.value.trim().replace(/,/g, ''); let t = ''
      if (v === '') t = '请输入金额'
      else if (!/^\d+(\.\d{1,2})?$/.test(v)) t = '金额需为数字，最多两位小数'
      else if (+v > 99999.99) t = '金额不能超过 99,999.99'
      mf.classList.toggle('bad', !!t); me.textContent = t
      if (!t) mi.value = (+v).toFixed(2)
    }
    mi.addEventListener('blur', money); mi.addEventListener('keydown', (e) => { if (e.key === 'Enter') { e.preventDefault(); money() } })
    mi.addEventListener('input', () => { if (mf.classList.contains('bad')) { mf.classList.remove('bad'); me.textContent = '' } })
  }),
})

guide('ad', 'CTRL', [
  ['定下整个后台的按钮层级', '按钮体系', '主次文字危险各司其职，一屏一个主按钮；危险操作先确认，禁用要写原因'],
  ['立即生效的二元设置，或选项不到 5 个', '开关 / 单选与多选', '开关点了就生效且失败回滚；少量选项直接平铺，套餐类用卡片式'],
  ['选项 5 个以上，或要从大量对象里挑一部分', '下拉选择器 / 穿梭框', '超过 10 个带搜索；多选用标签折叠；成员分配用左右穿梭，两边都能搜'],
  ['选日期，或按时间段筛选', '日期选择 / 日期范围选择', '单日点选可手输；范围的快捷项与自定义在同一弹层里，选完结束日期即生效'],
  ['有层级的分类或地区', '级联选择', '三级联动加搜索，选到叶子即完成，输入框里显示完整路径'],
  ['传图、加标签、挑颜色', '图片上传区 / 标签输入 / 颜色选择', '图片有进度与失败重试、首张为封面；标签回车添加防重复；颜色先给低饱和色板'],
  ['填数值、打分、看进度与协作人', '数字输入 / 滑块 / 评分 / 头像组与进度条', '数量步进、金额自由输入；区间用滑块并同步数值，总和约束用比例分配滑块'],
])

})()
