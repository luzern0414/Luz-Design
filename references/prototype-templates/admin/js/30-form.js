/* ===== 表单：字段由规格的 form.sections[].fields 声明；草稿在关闭面板后仍保留；失焦校验、提交时汇总并定位第一个错误 ===== */
const DRAFTS = new Map()
const fieldsOf = (F) => (F.sections || []).flatMap((s) => s.fields || [])
const formCfgOf = (p) => p.form || null
function findRowOfPage(p, a) {
  const F = p.form || p.detail; if (!F) return null
  const path = F.record ? F.record.data : F.data
  if (!path) return null
  return a && a !== 'new' ? findRow(path, a) : null
}
function draftOf(p, a) {
  const F = p.form, k = p.id + '|' + (a || '')
  let d = DRAFTS.get(k)
  if (!d) {
    const row = findRowOfPage(p, a), vals = {}
    fieldsOf(F).forEach((f) => { vals[f.key] = row && row[f.key] !== undefined ? clone(row[f.key]) : f.default !== undefined ? clone(f.default) : f.type === 'switch' ? false : f.type === 'tags' || f.type === 'images' ? [] : f.type === 'slider' ? f.min || 0 : '' })
    d = { vals, errs: {}, key: k, isNew: !row, id: row ? row.id : null, fail: '', init: JSON.stringify(vals) }; DRAFTS.set(k, d)
  }
  return d
}
AD.draft = draftOf
const isDirty = (d) => JSON.stringify(d.vals) !== d.init
/* 面板里的表单有未保存的内容时，Esc、×、点面板外先问一句（叠在表单上的确认框）；没改过直接关。取消按钮是程序里的关闭，直接丢弃草稿 */
function formBeforeClose(p, a) {
  const d = DRAFTS.get(p.id + '|' + (a || ''))
  if (!d || !isDirty(d)) { if (d) DRAFTS.delete(d.key); return true }
  K.confirm({ title: '放弃未保存的修改？', text: '关闭后已经填写的内容不会保留。', ok: '放弃修改', cancel: '继续编辑', danger: true, maskClose: false, stack: true, onOk: () => { DRAFTS.delete(d.key); K.closeSheet() } })
  return false
}
const fid = (d, f) => 'f' + (hash(d.key + f.key) % 100000)
function checkField(f, v) {
  const empty = v === '' || v == null || (Array.isArray(v) && !v.length)
  if (f.required && empty) return f.requiredMsg || `请填写${f.label}`
  if (empty) return ''
  const s = String(v)
  if (f.pattern && !new RegExp(f.pattern).test(s)) return f.msg || `${f.label}格式不对`
  if (f.type === 'number' || f.type === 'money' || f.type === 'slider') {
    const n = num(v); if (Number.isNaN(n)) return `${f.label}要填数字`
    if (f.min != null && n < f.min) return f.msg || `${f.label}不能小于 ${f.min}`
    if (f.max != null && n > f.max) return f.msg || `${f.label}不能大于 ${f.max}`
  }
  if (f.minLen && s.length < f.minLen) return f.msg || `${f.label}至少 ${f.minLen} 个字`
  if (f.max && (f.type === 'text' || f.type === 'textarea') && s.length > f.max) return `${f.label}最多 ${f.max} 个字`
  return ''
}
function fieldH(f, d) {
  const id = fid(d, f), v = d.vals[f.key], err = d.errs[f.key] || '', bad = err ? ' aria-invalid="true"' : '', dby = `aria-describedby="e${id}${f.hint ? ' h' + id : ''}"`
  let ctl = ''
  const t = f.type || 'text'
  if (t === 'text' || t === 'date') ctl = `<input class="ad-in" id="${id}" type="${t === 'date' ? 'date' : 'text'}" data-ad-in="${esc(f.key)}" data-fk="fi-${esc(f.key)}" value="${esc(v)}"${f.max ? ` maxlength="${f.max}"` : ''}${f.placeholder ? ` placeholder="${esc(f.placeholder)}"` : ''}${f.ro ? ' readonly' : ''}${bad} ${dby}>${f.max && t === 'text' ? `<div class="cnt" data-cnt="${esc(f.key)}">${String(v).length} / ${f.max}</div>` : ''}`
  else if (t === 'number') ctl = `<div class="ad-pre"><input class="ad-in${f.unit ? ' pl' : ''}" id="${id}" type="number" data-ad-in="${esc(f.key)}" data-fk="fi-${esc(f.key)}" value="${esc(v)}"${f.min != null ? ` min="${f.min}"` : ''}${f.max != null ? ` max="${f.max}"` : ''}${f.step ? ` step="${f.step}"` : ''}${bad} ${dby} style="max-width:200px">${f.unit ? `<span class="p s">${esc(f.unit)}</span>` : ''}</div>`
  else if (t === 'money') ctl = `<div class="ad-pre"><span class="p">¥</span><input class="ad-in" id="${id}" type="text" inputmode="decimal" data-ad-in="${esc(f.key)}" data-fk="fi-${esc(f.key)}" data-fmt="money" value="${esc(v === '' ? '' : money(v))}"${bad} ${dby} style="max-width:200px"></div>`
  else if (t === 'select') ctl = `<select class="ad-sel" id="${id}" data-ad-in="${esc(f.key)}"${bad} ${dby}><option value="">${esc(f.placeholder || '请选择')}</option>${optsOf(f.options).map((o) => `<option value="${esc(o.v)}"${String(o.v) === String(v) ? ' selected' : ''}>${esc(o.label)}</option>`).join('')}</select>`
  else if (t === 'radio') ctl = `<div class="ad-radios" role="radiogroup" aria-labelledby="l${id}">${optsOf(f.options).map((o) => `<button type="button" role="radio" aria-checked="${String(o.v) === String(v)}" data-ad-radio="${esc(f.key)}" data-v="${esc(o.v)}">${esc(o.label)}</button>`).join('')}</div>`
  else if (t === 'switch') ctl = `<div class="row"><button type="button" class="ad-sw" role="switch" aria-checked="${!!v}" data-ad-fsw="${esc(f.key)}" aria-labelledby="l${id}"><span class="tg"></span><span class="st">${v ? esc(f.on || '开') : esc(f.off || '关')}</span></button></div>`
  else if (t === 'textarea') ctl = `<textarea class="ad-ta" id="${id}" data-ad-in="${esc(f.key)}" data-fk="fi-${esc(f.key)}" rows="${f.rows || 3}"${f.max ? ` maxlength="${f.max}"` : ''}${f.placeholder ? ` placeholder="${esc(f.placeholder)}"` : ''}${bad} ${dby}>${esc(v)}</textarea>${f.max ? `<div class="cnt" data-cnt="${esc(f.key)}">${String(v).length} / ${f.max}</div>` : ''}`
  else if (t === 'tags') ctl = `<div class="ad-tags">${(v || []).map((x, i) => `<span class="ad-tag in">${esc(x)}<button type="button" data-ad-tagx="${esc(f.key)}" data-i="${i}" aria-label="删除标签${esc(x)}" style="margin-left:2px;min-width:20px;min-height:20px">${ic('close', 's')}</button></span>`).join('')}<input class="ad-in" id="${id}" type="text" data-ad-tag="${esc(f.key)}" data-fk="ft-${esc(f.key)}" placeholder="输入后按 Enter 添加" aria-label="${esc(f.label)}"${(v || []).length >= (f.maxCount || 8) ? ' disabled' : ''}></div>`
  else if (t === 'images') ctl = `<div class="ad-imgs" role="group" aria-label="${esc(f.label)}">${Array.from({ length: Math.min(9, LIB.ASSETS.prod.length) }, (_, i) => { const at = (v || []).indexOf(i); return `<button type="button" data-ad-img="${esc(f.key)}" data-v="${i}" aria-pressed="${at >= 0}" aria-label="图片 ${i + 1}${at === 0 ? '（封面）' : ''}"><img alt="" src="${LIB.P(i)}">${at === 0 ? '<b>封面</b>' : ''}</button>` }).join('')}</div>`
  else if (t === 'slider') ctl = `<div class="ad-range"><input type="range" id="${id}" data-ad-in="${esc(f.key)}" min="${f.min || 0}" max="${f.max == null ? 100 : f.max}" step="${f.step || 1}" value="${esc(v)}" aria-label="${esc(f.label)}"><output data-out="${esc(f.key)}">${esc(v)}${esc(f.unit || '')}</output></div>`
  else if (t === 'ro') ctl = `<div style="padding-top:7px">${esc(rec(f.value || '{' + f.key + '}', d.vals))}</div>`
  return `<div class="ad-ff" data-field="${esc(f.key)}"><label class="lb" id="l${id}" for="${id}">${esc(f.label)}${f.required ? '<span class="req" aria-hidden="true">*</span>' : ''}</label><div class="ctl">${ctl}${f.hint ? `<div class="hint" id="h${id}">${esc(f.hint)}</div>` : ''}<div class="err" id="e${id}" role="alert">${esc(err)}</div></div></div>`
}
function formBodyH(p, a, panel) {
  const F = p.form, d = draftOf(p, a)
  const secs = (F.sections || []).map((s) => `<section class="${panel ? '' : 'ad-card ad-fsec'}">${s.title ? `<h3${panel ? ' class="ad-hd3" style="margin-top:0"' : ''}>${esc(s.title)}</h3>` : ''}${(s.fields || []).map((f) => fieldH(f, d)).join('')}</section>`).join('')
  return `<div class="ad-form" data-form="${esc(d.key)}" data-cid="${panel ? 'AD-FORM-008' : 'AD-FORM-002'}"><div class="ad-banner dg ad-ferr" role="alert"${d.fail ? '' : ' hidden'}>${ic('alert')}<span class="tx">${esc(d.fail)}</span></div>${secs}</div>`
}
function formBarH(p, a, panel) {
  const F = p.form, sub = F.submit || {}
  const busy = SUBMITTING.has(p.id + '|' + (a || ''))
  const btns = `<button type="button" class="ad-btn" data-ad-fcancel="1">${esc(sub.cancel || '取消')}</button><button type="button" class="ad-btn primary" data-ad-fsubmit="1" data-write${busy ? ' aria-busy="true" aria-disabled="true"' : ''}>${busy ? '<span class="ad-spin"></span>保存中' : esc(sub.label || '保存')}</button>`
  return panel ? btns : `<div class="ad-fbar" data-cid="AD-FORM-002">${btns}</div>`
}
const SUBMITTING = new Set()
let CURFORM = null /* 当前打开的表单：{p, a, panel} */
function showFormErrors(p, a) {
  const d = draftOf(p, a), root = $(`[data-form="${CSS.escape(d.key)}"]`) || document.querySelector(`[data-form="${d.key}"]`); if (!root) return
  fieldsOf(p.form).forEach((f) => {
    const box = $(`[data-field="${f.key}"]`, root); if (!box) return
    const err = d.errs[f.key] || '', e = $('.err', box), c = $('[data-ad-in],[data-ad-tag]', box)
    e.textContent = err; if (c) c.setAttribute('aria-invalid', err ? 'true' : 'false')
  })
  const fe = $('.ad-ferr', root); if (fe) { fe.hidden = !d.fail; $('.tx', fe).textContent = d.fail }
}
function validateForm(p, a) {
  const d = draftOf(p, a); d.errs = {}; let first = null
  fieldsOf(p.form).forEach((f) => { const m = checkField(f, d.vals[f.key]); if (m) { d.errs[f.key] = m; if (!first) first = f } })
  const n = Object.keys(d.errs).length
  d.fail = n ? `还有 ${n} 项没有填对，已定位到第一项：${first.label}` : ''
  showFormErrors(p, a)
  if (first) { const root = document.querySelector(`[data-form="${d.key}"]`), c = root && $(`[data-field="${first.key}"] [data-ad-in],[data-field="${first.key}"] [data-ad-radio],[data-field="${first.key}"] [data-ad-tag]`, root); if (c) { c.focus(); if (c.scrollIntoView) c.scrollIntoView({ block: 'nearest' }) } }
  return !n
}
function coerce(F, vals) {
  const out = clone(vals)
  fieldsOf(F).forEach((f) => { if ((f.type === 'number' || f.type === 'money' || f.type === 'slider') && out[f.key] !== '') out[f.key] = num(out[f.key]) })
  return out
}
function submitForm(p, a) {
  if (readonly()) { K.toast(readReason(), 'warn'); return }
  const key = p.id + '|' + (a || ''), F = p.form, sub = F.submit || {}, d = draftOf(p, a)
  if (SUBMITTING.has(key)) return
  if (!validateForm(p, a)) return
  const sid = sub.scene || 'submit', sc = K.scene(sid) || 'ok'
  SUBMITTING.add(key); refreshFormBar(p, a)
  setTimeout(() => {
    SUBMITTING.delete(key)
    let why = null
    if (K.S.net === 'offline') why = '网络不可用，请检查网络后重试'
    else if (sc.indexOf('fail') === 0) why = (sub.reasons && sub.reasons[sc]) || sceneLabel(sid, sc)
    if (why) { d.fail = `保存失败：${why}。已填写的内容都还在，处理后可以再点保存。`; refreshFormBar(p, a); showFormErrors(p, a); K.toast('保存失败：' + why, 'danger'); return }
    d.fail = ''
    const vals = Object.assign(coerce(F, d.vals), F.patch || {}), row = findRowOfPage(p, a); let id
    if (F.stamp) vals[F.stamp] = nowStr()
    if (F.record) {
      if (row) { Object.assign(row, vals); id = row.id }
      else { id = (F.idPrefix || 'N') + String(Date.now()).slice(-6); (K.get(F.record.data) || []).unshift(Object.assign({ id }, F.record.defaults || {}, vals)) }
    }
    if (F.log) auditLog(rec(F.log, Object.assign({}, vals, { id })))
    if (F.record && F.record.list) { const lp = K.pages[F.record.list]; if (lp && lp.list) lstate(lp).flash = String(id) }
    DRAFTS.delete(d.key)
    K.batch(() => {
      K.toast(rec(sub.toast || '已保存', Object.assign({}, vals, { id })))
      if (d.isNew && sub.thenNew) K.replace(sub.thenNew); else if (sub.then === 'back') K.back(); else if (sub.then === 'close') K.closeSheet(); else if (sub.go) K.replace(sub.go, String(id || '')); else K.render()
    })
  }, sc === 'processing' ? 1800 : 400)
}
function refreshFormBar(p, a) {
  const panel = p.type === 'sheet'
  if (panel) { const foot = $('.pt-sfoot', document.getElementById('ptDlg')); if (foot) foot.innerHTML = formBarH(p, a, true) }
  else { const bar = $('.ad-fbar'); if (bar) bar.outerHTML = formBarH(p, a, false) }
}
function cancelForm(p, a) {
  DRAFTS.delete(p.id + '|' + (a || ''))
  if (p.type === 'sheet') K.closeSheet(); else K.back()
}
/* 字段交互：输入同步到草稿，失焦校验，单选/开关/标签/图片点选 */
function formCtx(el) {
  const root = el.closest('[data-form]'); if (!root) return null
  const d = DRAFTS.get(root.dataset.form); if (!d) return null
  const pid = d.key.split('|')[0], p = K.pages[pid]; return { d, p, a: d.key.slice(pid.length + 1), root }
}
function formInput(e) {
  const el = e.target; if (!el.matches || !el.matches('[data-ad-in]')) return false
  const c = formCtx(el); if (!c) return false
  const k = el.dataset.adIn, f = fieldsOf(c.p.form).find((x) => x.key === k)
  c.d.vals[k] = el.value
  const cnt = $(`[data-cnt="${k}"]`, c.root); if (cnt) cnt.textContent = `${el.value.length} / ${f.max}`
  const out = $(`[data-out="${k}"]`, c.root); if (out) out.textContent = el.value + (f.unit || '')
  if (c.d.errs[k]) { delete c.d.errs[k]; el.setAttribute('aria-invalid', 'false'); const eb = $('.err', el.closest('[data-field]')); if (eb) eb.textContent = '' }
  return true
}
function formBlur(e) {
  const el = e.target; if (!el.matches || !el.matches('[data-ad-in]')) return
  const c = formCtx(el); if (!c) return
  const k = el.dataset.adIn, f = fieldsOf(c.p.form).find((x) => x.key === k)
  if (el.dataset.fmt === 'money' && el.value !== '') { c.d.vals[k] = num(el.value); el.value = money(el.value) }
  const m = checkField(f, c.d.vals[k]); c.d.errs[k] = m || undefined; if (!m) delete c.d.errs[k]
  el.setAttribute('aria-invalid', m ? 'true' : 'false'); const eb = $('.err', el.closest('[data-field]')); if (eb) eb.textContent = m
}
function redrawForm(c) {
  const dlg = document.getElementById('ptDlg')
  K.keepFocus(() => {
    if (c.p.type === 'sheet' && dlg && dlg.open) { const b = $('.pt-sbody', dlg); b.innerHTML = LW(formBodyH(c.p, c.a, true)); K.mount(dlg) } else { const r = c.root; const wrap = document.createElement('div'); wrap.innerHTML = LW(formBodyH(c.p, c.a, false)); r.replaceWith(wrap.firstElementChild); K.mount(document.getElementById('adScreen')) }
  })
}
function formClick(e) {
  const t = e.target
  const rad = t.closest('[data-ad-radio]'), fsw = t.closest('[data-ad-fsw]'), img = t.closest('[data-ad-img]'), tx = t.closest('[data-ad-tagx]')
  const el = rad || fsw || img || tx; if (!el) return false
  const c = formCtx(el); if (!c) return false
  const F = c.p.form
  if (rad) { c.d.vals[rad.dataset.adRadio] = rad.dataset.v; $$('[data-ad-radio="' + rad.dataset.adRadio + '"]', c.root).forEach((b) => b.setAttribute('aria-checked', b === rad ? 'true' : 'false')) }
  else if (fsw) { const k = fsw.dataset.adFsw, f = fieldsOf(F).find((x) => x.key === k); c.d.vals[k] = !c.d.vals[k]; fsw.setAttribute('aria-checked', String(c.d.vals[k])); $('.st', fsw).textContent = c.d.vals[k] ? f.on || '开' : f.off || '关' }
  else if (img) { const k = img.dataset.adImg, i = +img.dataset.v, arr = c.d.vals[k] || (c.d.vals[k] = []), at = arr.indexOf(i); const f = fieldsOf(F).find((x) => x.key === k); if (at >= 0) arr.splice(at, 1); else if (arr.length < (f.maxCount || 5)) arr.push(i); else K.toast(`最多选 ${f.maxCount || 5} 张`, 'warn'); redrawForm(c) }
  else if (tx) { c.d.vals[tx.dataset.adTagx].splice(+tx.dataset.i, 1); redrawForm(c) }
  return true
}
function formKey2(e) {
  const el = e.target; if (e.key !== 'Enter' || !el.matches || !el.matches('[data-ad-tag]')) return false
  const c = formCtx(el); if (!c) return false
  e.preventDefault(); const v = el.value.trim().replace(/[,，]$/, ''); const k = el.dataset.adTag, arr = c.d.vals[k] || (c.d.vals[k] = [])
  if (!v) return true
  if (arr.includes(v)) { K.toast('这个标签已经添加过了', 'warn'); return true }
  arr.push(v); redrawForm(c); return true
}
