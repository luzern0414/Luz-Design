/* ===== 设置页：分类 + 行内修改；开关直接生效；影响资金的项先验证身份、写清改前改后、必填原因；修改记录进审计 ===== */
const SETST = { cat: {}, edit: null }
const SRC = { default: ['默认', 'mu'], global: ['全局', 'in'], store: ['本店', 'ok'] }
function auditLog(what, level) {
  const a = K.get('audit'); if (!Array.isArray(a)) return
  a.unshift({ id: 'L' + (Date.now() % 1e8) + a.length, time: nowStr(), who: (shell().account || {}).name || '管理员', role: roleName(), level: level || 'info', what, result: '成功' })
}
const sdata = (S) => K.get(S.data) || {}
const ssrc = (S) => K.get(S.data + '_src') || {}
const itemsOf = (S) => S.groups.flatMap((g) => g.sections.flatMap((x) => x.items))
function showVal(it, v) {
  if (it.type === 'switch') return v ? it.on || '开' : it.off || '关'
  if (it.type === 'radio') { const o = optsOf(it.options).find((x) => String(x.v) === String(v)); return o ? o.label : String(v) }
  return `${v}${it.unit || ''}`
}
function rangeText(it) { return it.type === 'number' ? `可填 ${it.min != null ? it.min : '不限'} – ${it.max != null ? it.max : '不限'}${it.unit || ''}` : '' }
function itemH(it, S) {
  const v = sdata(S)[it.key], src = ssrc(S)[it.key] || 'default', sr = SRC[src] || SRC.default, ed = SETST.edit === it.key
  let cv = ''
  if (it.type === 'switch') cv = `<button type="button" class="ad-sw" role="switch" aria-checked="${!!v}" data-ad-sset="${esc(it.key)}" data-write aria-label="${esc(it.label)}"><span class="tg"></span><span class="st">${v ? esc(it.on || '开') : esc(it.off || '关')}</span></button>`
  else cv = `<span class="v">${esc(showVal(it, v))}</span>${tagH(sr[0], sr[1])}<button type="button" class="ad-btn text" data-ad-sedit="${esc(it.key)}" data-fk="se-${esc(it.key)}" data-write aria-label="修改${esc(it.label)}">修改</button>${src !== 'default' ? `<button type="button" class="ad-btn text" data-ad-sreset="${esc(it.key)}" data-write aria-label="恢复${esc(it.label)}为默认值">恢复默认</button>` : ''}`
  let edit = ''
  if (ed) {
    const ctl = it.type === 'radio' ? `<div class="ad-radios" role="radiogroup" aria-label="${esc(it.label)}">${optsOf(it.options).map((o) => `<button type="button" role="radio" aria-checked="${String(o.v) === String(SETST.val)}" data-ad-sradio="${esc(o.v)}" data-fk="sr-${esc(o.v)}">${esc(o.label)}</button>`).join('')}</div>` : `<input class="ad-in" type="number" data-ad-sin data-fk="sin" value="${esc(SETST.val)}" min="${it.min == null ? '' : it.min}" max="${it.max == null ? '' : it.max}" step="${it.step || 1}" aria-label="${esc(it.label)}新值">${it.unit ? `<span>${esc(it.unit)}</span>` : ''}<span class="ad-sub" style="margin:0;color:var(--ad-ink3)">${esc(rangeText(it))}</span>`
    edit = `<div class="ed">${ctl}<button type="button" class="ad-btn primary" data-ad-sok="${esc(it.key)}">确定</button><button type="button" class="ad-btn" data-ad-scancel>取消</button></div>`
    if (SETST.err) edit += `<div class="why" role="alert">${esc(SETST.err)}</div>`
  }
  return `<div class="ad-sit" data-skey="${esc(it.key)}"><div><div class="nm">${esc(it.label)}${it.money ? ` ${tagH('影响资金', 'wn')}` : ''}</div><div class="im">${esc(it.impact || '')}${it.type === 'number' ? ' · ' + esc(rangeText(it)) : ''}</div></div><div class="cv">${cv}</div>${edit}</div>`
}
function settingsH(p) {
  const S = p.settings, cur = SETST.cat[p.id] || S.groups[0].id, g = S.groups.find((x) => x.id === cur) || S.groups[0]
  return `<div class="ad-set" data-sets="${esc(p.id)}" data-cid="AD-PAGE-005"><div class="ad-card ad-setnav" role="group" aria-label="设置分类">${S.groups.map((x) => `<button type="button" data-ad-scat="${esc(x.id)}"${x.id === g.id ? ' aria-current="true"' : ''}>${esc(x.label)}</button>`).join('')}</div><div class="ad-setbody" data-cid="AD-MGMT-007">${g.sections.map((sec) => `<section class="ad-card ad-setgrp"><h3>${esc(sec.title)}</h3>${sec.items.map((it) => itemH(it, S)).join('')}${sec.note ? `<p class="ad-sub" style="padding:8px 20px;margin:0;color:var(--ad-ink3)">${esc(sec.note)}</p>` : ''}</section>`).join('')}</div></div>`
}
/* 引擎的 K.render({part: 'settings'}) 经 renderPart 调进来：换掉设置区并返回新元素，焦点按 data-fk 恢复 */
function repaintSettings() { const w = $('[data-sets]'); if (!w) return null; const p = K.pages[w.dataset.sets]; const h = document.createElement('div'); h.innerHTML = LW(settingsH(p)); const n = h.firstElementChild; w.replaceWith(n); return n }
function applySetting(S, it, to, reason) {
  const d = sdata(S), src = ssrc(S), before = d[it.key]
  outcome('submit', () => {
    d[it.key] = to; src[it.key] = it.scope === 'global' ? 'global' : 'store'
    auditLog(`修改经营设置「${it.label}」：${showVal(it, before)} → ${showVal(it, to)}${reason ? '（原因：' + reason + '）' : ''}`, it.money ? 'warn' : 'info')
    SETST.edit = null; SETST.err = ''; K.toast('已生效，只影响之后的业务'); K.render({ part: 'settings' }); drawSide()
  }, '保存')
}
/* 影响资金的修改：引擎的 K.confirm 带必填字段（原因、验证身份），不通过时不关闭；写清改前改后与影响范围；点遮罩不关闭 */
function confirmReason(o) {
  K.confirm({
    title: o.title, text: `${o.label}：${o.before} → ${o.after}。影响范围：${o.scope || '只影响之后的业务'}。`, ok: '确认修改', cancel: '取消', maskClose: false, stack: true,
    fields: [
      { name: 'reason', label: '修改原因', type: 'textarea', required: true, min: 2, placeholder: '写清为什么改，会进入操作日志', msg: '请写清修改原因（至少 2 个字）' },
      { name: 'password', label: '验证身份', type: 'password', required: true, placeholder: '输入登录密码（演示环境任意非空）', msg: '请输入登录密码验证身份' },
    ],
    onOk: (v) => o.cb(String(v.reason).trim()),
  })
}
function settingsClick(e) {
  const t = e.target, el = t.closest('[data-ad-scat],[data-ad-sedit],[data-ad-sok],[data-ad-scancel],[data-ad-sreset],[data-ad-sset],[data-ad-sradio]'); if (!el) return false
  const w = el.closest('[data-sets]'); if (!w) return false
  const p = K.pages[w.dataset.sets], S = p.settings, find = (k) => itemsOf(S).find((x) => x.key === k)
  if (el.dataset.adScat) { SETST.cat[p.id] = el.dataset.adScat; SETST.edit = null; K.render({ part: 'settings' }); return true }
  if (el.dataset.adSedit) { const it = find(el.dataset.adSedit); SETST.edit = it.key; SETST.val = sdata(S)[it.key]; SETST.err = ''; K.render({ part: 'settings' }); const i = $('[data-ad-sin]') || $('[data-ad-sradio]'); if (i) i.focus(); return true }
  if (el.hasAttribute('data-ad-scancel')) { SETST.edit = null; SETST.err = ''; K.render({ part: 'settings' }); return true }
  if (el.dataset.adSradio !== undefined) { SETST.val = el.dataset.adSradio; K.render({ part: 'settings' }); return true }
  if (el.dataset.adSreset) {
    const it = find(el.dataset.adSreset), def = it.default, before = sdata(S)[it.key]
    const run = () => outcome('submit', () => { sdata(S)[it.key] = def; ssrc(S)[it.key] = 'default'; auditLog(`恢复经营设置「${it.label}」为默认值：${showVal(it, before)} → ${showVal(it, def)}`); K.toast('已恢复默认，只影响之后的业务'); K.render({ part: 'settings' }) }, '恢复')
    if (it.money) confirmReason({ title: `恢复「${it.label}」为默认值`, label: it.label, before: showVal(it, before), after: showVal(it, def), scope: it.scope, cb: () => run() }); else run()
    return true
  }
  if (el.dataset.adSset) {
    const it = find(el.dataset.adSset), to = !sdata(S)[it.key], run = (reason) => applySetting(S, it, to, reason)
    if (it.money) confirmReason({ title: `${to ? '开启' : '关闭'}「${it.label}」`, label: it.label, before: sdata(S)[it.key] ? '开' : '关', after: to ? '开' : '关', scope: it.scope, cb: run }); else run()
    return true
  }
  if (el.dataset.adSok) {
    const it = find(el.dataset.adSok); let to = SETST.val
    if (it.type === 'number') {
      const n = Number(to)
      if (to === '' || Number.isNaN(n)) { SETST.err = `请填写${it.label}`; K.render({ part: 'settings' }); return true }
      if ((it.min != null && n < it.min) || (it.max != null && n > it.max)) { SETST.err = `${it.label}${rangeText(it)}，当前填的 ${n}${it.unit || ''} 超出范围`; K.render({ part: 'settings' }); return true }
      to = n
    }
    if (String(to) === String(sdata(S)[it.key])) { SETST.edit = null; K.render({ part: 'settings' }); K.toast('没有变化', 'info'); return true }
    if (it.money) confirmReason({ title: `修改「${it.label}」`, label: it.label, before: showVal(it, sdata(S)[it.key]), after: showVal(it, to), scope: it.scope, cb: (reason) => applySetting(S, it, to, reason) }); else applySetting(S, it, to)
    return true
  }
  return false
}
function settingsInput(e) { const el = e.target; if (el.matches && el.matches('[data-ad-sin]')) { SETST.val = el.value; return true } return false }
