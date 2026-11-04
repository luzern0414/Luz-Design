/* ===== 动作与详情：行操作、批量操作、详情面板、导出预览、操作结果（成功 / 处理中 / 失败）、更多菜单 ===== */
const disabledReason = () => { const p = K.cur().page; return ((p.logic && p.logic.states) || []).find((s) => /禁用|不可|不能/.test(s)) || '当前条件不满足，写操作已禁用' }
const lockReason = () => (readonly() ? readReason() : K.S.view === 'disabled' ? disabledReason() : '')
function LW(html) {
  const r = lockReason(); if (!r) return html
  return html.replace(/<button\b[^>]*\bdata-write\b[^>]*>/g, (tag) => (/aria-disabled/.test(tag) ? tag : tag.replace('data-write', `data-write aria-disabled="true" data-reason="${esc(r)}" title="${esc(r)}"`)))
}
/* 操作结果由场景 submit（或动作自己指定的场景）决定：成功 / 处理中 / 各种失败原因；断网时失败 */
function outcome(sid, ok, label) {
  const sc = K.scene(sid) || 'ok'
  if (K.S.net === 'offline') { K.toast(`${label || '操作'}失败：网络不可用，请检查网络后重试`, 'danger'); return false }
  if (sc.indexOf('fail') === 0) { K.toast(`${label || '操作'}失败：${sceneLabel(sid, sc)}`, 'danger'); return false }
  if (sc === 'processing') { K.toast('处理中，请稍候…', 'info'); setTimeout(ok, 1500); return true }
  ok(); return true
}
function runAction(a, rows, ctx) {
  ctx = ctx || {}
  if (a.write !== false && readonly()) { K.toast(readReason(), 'warn'); return }
  if (K.S.view === 'disabled' && a.write !== false) { K.toast(disabledReason(), 'warn'); return }
  const bad = a.when && rows.find((r) => !matches(r, a.when)); if (bad) { K.toast(a.whyNot || '当前状态不能操作', 'warn'); return }
  const r0 = rows[0] || {}, go = () => execAction(a, rows, ctx)
  if (a.confirm) {
    const c = a.confirm
    /* 确认框叠在已打开的详情面板上（stack），点遮罩不关闭（maskClose: false） */
    K.confirm({ title: rec(c.title || a.label, r0), text: rec(c.text || '', r0) + (rows.length > 1 ? `（共 ${rows.length} 项）` : ''), ok: c.ok || a.label, danger: !!(c.danger || a.danger), onOk: go, stack: true, maskClose: false })
  } else go()
}
function execAction(a, rows, ctx) {
  const r0 = rows[0] || {}
  if (!a.patch && !a.append && !a.inc && !a.act) {
    if (a.sheet) { K.openSheet(a.sheet, String(r0.id)); return }
    if (a.go) { K.go(a.go, String(r0.id)); return }
    if (a.tab) { activate(a.tab, a.preset); return }
    if (a.close) { K.closeSheet(); return }
    return
  }
  if (a.act && !a.patch) { K.act(a.act, String(r0.id)); return }
  outcome(a.scene || 'submit', () => {
    K.batch(() => {
      rows.forEach((r) => {
        Object.entries(a.patch || {}).forEach(([k, v]) => { r[k] = resolveVal(v) })
        Object.entries(a.inc || {}).forEach(([k, v]) => { r[k] = num(r[k]) + v })
        if (a.append) { (r.log = r.log || []).push({ time: nowStr(), text: rec(a.append, r) }) }
      })
      if (a.log) auditLog(rec(a.log, r0) + (rows.length > 1 ? ` 等 ${rows.length} 项` : ''), a.danger ? 'warn' : 'info')
      const lp = ctx.listId && K.pages[ctx.listId]; if (lp && lp.list) { lstate(lp).flash = String(r0.id); lstate(lp).sel.clear() }
      K.toast(rec(a.toast || `${a.label}已完成`, Object.assign({}, r0, { n: rows.length })))
      if (a.close) K.closeSheet(); else if (a.sheet) K.openSheet(a.sheet, String(r0.id)); else if (a.go) K.go(a.go, String(r0.id))
      K.render()
    })
    drawSide()
  }, a.label)
}
/* 点击里的命令：行操作、批量操作、详情底部动作 */
function actionClick(e) {
  const el = e.target.closest('[data-ad-ra],[data-ad-ba],[data-ad-da]'); if (!el) return false
  if (el.matches('[aria-disabled="true"]')) return false
  closePopOnly()
  if (el.dataset.adRa) {
    const w = el.closest('.ad-list') || $('.ad-list'), pid = w ? w.dataset.list : (K.cur().page.id), p = K.pages[pid], L = p.list
    const a = (L.rowActions || []).concat(L.moreActions || []).find((x) => x.id === el.dataset.adRa), row = findRow(L.data, el.dataset.id)
    if (a && row) runAction(a, [row], { listId: pid }); return true
  }
  if (el.dataset.adBa) {
    const w = el.closest('.ad-list'), p = K.pages[w.dataset.list], L = p.list, s = lstate(p)
    const a = L.bulk.find((x) => x.id === el.dataset.adBa), rows = rowsOf(L.data).filter((r) => s.sel.has(String(r.id)))
    if (a && rows.length) runAction(a, rows, { listId: p.id }); return true
  }
  if (el.dataset.adDa) {
    const sp = K.S.sheet && K.pages[K.S.sheet.id]; if (!sp) return true
    const D = sp.detail, row = findRow(D.data, K.S.sheet.a) || rowsOf(D.data)[0], a = (D.actions || []).find((x) => x.id === el.dataset.adDa)
    if (a && row) runAction(a, [row], { listId: D.list }); return true
  }
  return false
}
/* ---------- 更多菜单（弹出层里）---------- */
function openMenu(btn, items) {
  const app = $('#adApp').getBoundingClientRect(), r = btn.getBoundingClientRect()
  ST.pop = 'menu'; ST.menu = { items, x: Math.max(8, Math.min(r.left - app.left, app.width - 196)), y: r.bottom - app.top + 4, by: r.top - app.top }
  drawPop()
  const m = $('.ad-menu', $('#adPop')); if (m && ST.menu.y + m.offsetHeight > app.height - 8) m.style.top = Math.max(8, ST.menu.by - m.offsetHeight - 4) + 'px'
  const f = $('.ad-menu button:not([aria-disabled])', $('#adPop')); if (f) f.focus()
}
function closePopOnly() { if (ST.pop) { ST.pop = null; drawPop() } }
function openRowMenu(btn, w) {
  const p = K.pages[w.dataset.list], L = p.list, row = findRow(L.data, btn.dataset.id), rest = (L.rowActions || []).slice(2).concat(L.moreActions || [])
  openMenu(btn, rest.map((a) => { const bad = a.when && !matches(row, a.when), ro = readonly() && a.write !== false, why = bad ? a.whyNot || '当前状态不能操作' : ro ? readReason() : ''; return { label: a.label, attr: `data-ad-ra="${esc(a.id)}" data-id="${esc(row.id)}"`, danger: a.danger, why } }))
}
function openTabMenu(btn, w) {
  const p = K.pages[w.dataset.list], L = p.list, T = L.tabs, s = lstate(p), base = baseRows(L, s, true), mp = mapOf(T.map || T.key)
  openMenu(btn, T.more.map((v) => ({ label: `${(mp[v] || {}).label || v}　${base.filter((r) => String(r[T.key]) === String(v)).length}`, attr: `data-ad-mtab="${esc(p.id)}:${esc(v)}"` })))
}
function menuH() {
  const m = ST.menu
  return `<div class="ad-menu" role="menu" style="left:${m.x}px;top:${m.y}px">${m.items.map((i) => `<button type="button" role="menuitem"${i.danger ? ' class="danger"' : ''} ${i.attr}${i.why ? ` aria-disabled="true" data-reason="${esc(i.why)}" title="${esc(i.why)}"` : ''}>${esc(i.label)}</button>`).join('')}</div>`
}
/* ---------- 详情面板 ---------- */
function valH(t, v, extra) {
  if (v == null || v === '') return '—'
  if (t === 'money') return `¥${money(v)}`
  if (t === 'status') { const m = mapOf(extra.map)[v] || { label: v, tone: 'mu' }; return tagH(m.label, m.tone) }
  if (t === 'person') return `<span class="who" style="display:inline-flex;align-items:center;gap:8px">${avatar(extra.row, extra.key, 24)}${esc(v)}</span>`
  if (t === 'num') return int(v)
  if (t === 'phone') return esc(String(v).replace(/^(\d{3})\d{4}(\d{4})$/, '$1 **** $2'))
  if (t === 'bool') return v ? '是' : '否'
  return esc(v)
}
function detailH(p, a, row) {
  const D = p.detail
  if (!row) return `<div class="ad-empty" style="border:0">没有找到这条记录，可能已被删除。</div>`
  const head = D.head ? `<div class="ad-dhd">${D.head.status ? valH('status', row[D.head.status], { map: D.head.map || D.head.status }) : ''}${D.head.big ? `<span class="big">${valH(D.head.big.type, row[D.head.big.key], {})}</span>` : ''}${D.head.sub ? `<span style="color:var(--ad-ink2)">${esc(rec(D.head.sub, row))}</span>` : ''}</div>` : ''
  const secs = (D.sections || []).map((s) => {
    let b = ''
    if (s.kv) b = `<dl class="ad-dl">${s.kv.map((f) => `<dt>${esc(f.label)}</dt><dd class="${f.wide ? 'wide' : ''}">${valH(f.type, row[f.key], { map: f.map || f.key, row, key: f.key })}</dd>`).join('')}</dl>`
    else if (s.table) { const rows = row[s.table.key] || []; b = rows.length ? `<table class="ad-mini"><thead><tr>${s.table.columns.map((c) => `<th class="${c.align === 'l' ? 'l' : c.type === 'money' ? 'r' : ''}">${esc(c.label)}</th>`).join('')}</tr></thead><tbody>${rows.map((r) => `<tr>${s.table.columns.map((c) => `<td class="${c.align === 'l' ? 'l' : c.type === 'money' ? 'r' : ''}">${c.type === 'money' ? money(r[c.key]) : esc(r[c.key] == null ? '—' : r[c.key])}</td>`).join('')}</tr>`).join('')}</tbody></table>` : '<p style="color:var(--ad-ink3)">没有明细</p>' }
    else if (s.timeline) { const lg = row[s.timeline] || []; b = lg.length ? `<ol class="ad-tl">${lg.slice().reverse().map((l) => `<li>${esc(l.text)}<small>${esc(l.time)}</small></li>`).join('')}</ol>` : '<p style="color:var(--ad-ink3)">还没有记录</p>' }
    return `<section class="ad-dsec"><h4>${esc(s.title)}</h4>${b}</section>`
  }).join('')
  return `<div data-cid="AD-FB-003" data-detail="${esc(row.id)}">${head}${secs}</div>`
}
function detailFoot(p, row) {
  const D = p.detail
  const acts = (D.actions || []).filter((a) => !(a.hideWhen && row && matches(row, a.hideWhen))).map((a) => {
    const bad = row && a.when && !matches(row, a.when), why = bad ? a.whyNot || '当前状态不能操作' : ''
    return `<button type="button" class="ad-btn${a.kind === 'primary' ? ' primary' : ''}${a.danger ? ' danger' : ''}" data-ad-da="${esc(a.id)}"${a.write !== false ? ' data-write' : ''}${why ? ` aria-disabled="true" data-reason="${esc(why)}" title="${esc(why)}"` : ''}>${a.icon ? ic(a.icon) : ''}${esc(a.label)}</button>`
  }).join('')
  return `<button type="button" class="ad-btn" data-pt-close>关闭</button>${acts}`
}
function sheetContent(p, a) {
  const frame = { id: p.id, a, page: p, tab: K.S.tab, depth: K.cur().depth }, ctx = K.viewCtx()
  const row = p.detail ? findRow(p.detail.data, a) || rowsOf(p.detail.data)[0] : findRowOfPage(p, a)
  const title = rec(p.title || p.name, row || {})
  let body = '', foot = '', cid = 'AD-FB-001'
  if (p.detail) { body = detailH(p, a, row); foot = detailFoot(p, row); cid = 'AD-FB-003' }
  else if (p.form) { body = formBodyH(p, a, true); foot = formBarH(p, a, true); cid = 'AD-FB-009' }
  else { if (p.custom) body += customH(p.custom, p.args, frame, ctx); body += itemsH(p.blocks, frame, ctx); foot = `<button type="button" class="ad-btn" data-pt-close>关闭</button>` }
  const out = { title, body: LW(body), foot: LW(foot), layout: 'center', cid }
  if (p.form) { out.maskClose = false; out.onBeforeClose = () => formBeforeClose(p, a) }
  return out
}
/* 表单与确认面板点遮罩不关闭（避免丢已填内容）：引擎给遮罩写了 data-pt-close，面板建好后把它摘掉（详情面板保留，点遮罩可关）*/
/* ---------- 导出预览：中文表头、枚举翻译、金额两位小数、去掉内部编号 ---------- */
function exportOpen(pid) {
  const p = K.pages[pid], L = p.list, s = lstate(p), rows = visibleRows(L, s), cs = cols(L).filter((c) => c.type !== 'switch' && !c.noExport)
  const cell = (c, r) => { const v = r[c.key]; if (v == null || v === '') return ''; if (c.type === 'status') return ((mapOf(c.map || c.key)[v]) || { label: v }).label; if (c.type === 'money') return money(v); if (c.type === 'datetime') return String(v).slice(0, 16); return String(v) }
  const scope = L.tabs && s.tab !== '__all' ? ((mapOf(L.tabs.map || L.tabs.key)[s.tab] || {}).label || s.tab) : '全部'
  const file = `${L.export.file || L.noun}_${scope}_${todayStr()}.xlsx`
  K.sheet.open({
    layout: 'center', title: '导出预览', cid: 'AD-FB-001',
    body: `<p style="margin:0 0 8px;color:var(--ad-ink2)">文件名：<b>${esc(file)}</b>，导出当前筛选结果，共 ${rows.length} 条（不只当前页）。</p><div class="ad-tw" style="max-height:260px;overflow:auto"><table class="ad-mini" data-export-preview><thead><tr>${cs.map((c) => `<th class="${colAlign(c) === 'l' ? 'l' : ''}">${esc(c.label)}</th>`).join('')}</tr></thead><tbody>${rows.slice(0, 5).map((r) => `<tr>${cs.map((c) => `<td class="${colAlign(c) === 'l' ? 'l' : colAlign(c) === 'r' ? 'r' : ''}">${esc(cell(c, r))}</td>`).join('')}</tr>`).join('')}</tbody></table></div><p style="margin:8px 0 0;font-size:12px;color:var(--ad-ink3)">只显示前 5 行预览；表头用中文，状态翻译成中文，金额两位小数，不带内部编号。</p>`,
    foot: `<button type="button" class="ad-btn" data-pt-close>取消</button><button type="button" class="ad-btn primary" data-ad-expok="${esc(pid)}">${ic('download')}导出 ${rows.length} 条</button>`,
  })
}
function exportDo(pid) {
  const p = K.pages[pid], rows = visibleRows(p.list, lstate(p))
  K.sheet.close()
  outcome(p.list.export.scene || 'submit', () => K.toast(rows.length > 200 ? '数据较多，已转为后台生成，完成后在通知里提供下载' : `已导出 ${rows.length} 条`), '导出')
}
AD.outcome = outcome
AD.run = runAction
