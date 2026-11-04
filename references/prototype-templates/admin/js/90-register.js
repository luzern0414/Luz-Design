/* ===== 注册 kind、事件委托、重置 ===== */
K.kind({
  id: 'admin', tabsKey: 'nav', screen: '#adScreen', clip: '#adApp', toasts: '#ptToasts', darkMode: 'tokens', confirmCid: 'AD-FB-002',
  size: () => null,
  defaultGroups: ['appearance', 'theme', 'sidebar', 'density', 'iconStyle'],
  typeLabel: { tab: '一级页', sub: '二级页', sheet: '居中面板', result: '结果页' },
  config: [sidebarGroup, densityGroup],
  keepTabStacks: true,
  layout: () => ({ left: 264, right: 320 }),
  render, mounted, sheet: sheetContent, modules, renderPart,
})
sidebarGroup.apply = () => { if (K.S.tab) drawSide() }

const curForm = (el) => {
  if (el.closest('#ptDlg') && K.S.sheet) return { p: K.pages[K.S.sheet.id], a: K.S.sheet.a }
  const c = K.cur(); return { p: c.page, a: c.a }
}
const goPage = (id, a) => {
  const pg = K.pages[id]; if (!pg) return
  if (pg.type === 'tab') activate(pageTab(pg)); else if (pg.type === 'sheet') K.openSheet(id, a || ''); else K.go(id, a || '')
}
function onClick(e) {
  const t = e.target, q = (s) => t.closest(s)
  let el
  if ((el = q('[data-ad-nav]'))) { if (el.closest('[data-shell]')) return; activate(el.dataset.adNav, el.dataset.adPreset ? JSON.parse(el.dataset.adPreset) : null); return }
  if ((el = q('[data-ad-grp]'))) { toggleGroup(el); return }
  if ((el = q('[data-ad-close]'))) { closeTab(el.dataset.adClose); return }
  if ((el = q('[data-ad-side]'))) {
    const app = $('#adApp')
    if (el.dataset.adSide === 'close') app.dataset.side = 'closed'
    else if (mode() === 'narrow') app.dataset.side = app.dataset.side === 'open' ? 'closed' : 'open'
    else { ST.collapsed = !ST.collapsed; applyMode() }
    return
  }
  if ((el = q('[data-ad-pop]'))) { const v = el.dataset.adPop; if (v === 'close') closePopOnly(); else openPop(v); return }
  if ((el = q('[data-ad-notice]'))) {
    const id = el.dataset.adNotice, list = noticesOf()
    if (id === 'all') { list.forEach((n) => { n.read = true }); drawTop(); drawPop(); return }
    const n = list.find((x) => x.id === id); if (n) { n.read = true; closePopOnly(); drawTop(); if (n.go) goPage(n.go, n.arg) }
    return
  }
  if ((el = q('[data-ad-appear]'))) { K.setCfg('appearance', el.dataset.adAppear); drawPop(); return }
  if (q('[data-ad-logout]')) { closePopOnly(); K.confirm({ title: '退出登录', text: '未保存的草稿会保留在本机，下次登录继续。演示环境不会真的退出。', ok: '退出登录', onOk: () => K.toast('演示环境：已模拟退出，仍停留在当前页', 'info'), maskClose: false }); return }
  if ((el = q('[data-ad-tabsop]'))) { const v = el.dataset.adTabsop; closePopOnly(); if (v === 'home') activate(homeId()); else closeOthers(v === 'all'); return }
  if ((el = q('[data-ad-palgo]'))) { closePopOnly(); activate(el.dataset.adPalgo); return }
  if (q('[data-ad-ver]')) {
    const info = shell().versionInfo || [['前端版本', shell().version || '1.0.0']]
    K.sheet.open({ layout: 'center', title: '版本信息', cid: 'AD-FB-001', body: `<dl class="ad-dl" style="grid-template-columns:96px 1fr">${info.map(([k, v]) => `<dt>${esc(k)}</dt><dd>${esc(v)}</dd>`).join('')}</dl>`, foot: '<button type="button" class="ad-btn primary" data-pt-close>知道了</button>' })
    return
  }
  if ((el = q('[data-ad-mtab]'))) { const [pid, v] = el.dataset.adMtab.split(':'), s = lstate(K.pages[pid]); s.tab = v; s.page = 1; s.sel.clear(); closePopOnly(); K.render({ part: 'list:' + pid }); return }
  if ((el = q('[data-ad-export]'))) { if (el.matches('[aria-disabled="true"]')) return; exportOpen(el.dataset.adExport); return }
  if ((el = q('[data-ad-expok]'))) { exportDo(el.dataset.adExpok); return }
  if ((el = q('[data-ad-fsubmit]'))) { if (el.matches('[aria-disabled="true"]')) return; const c = curForm(el); submitForm(c.p, c.a); return }
  if ((el = q('[data-ad-fcancel]'))) { const c = curForm(el); cancelForm(c.p, c.a); return }
  if ((el = q('[data-ad-sw]'))) { if (el.matches('[aria-disabled="true"]')) return; toggleSwitch(el.closest('.ad-list'), el.dataset.adSw, el.dataset.k); return }
  if (onListClick(e) || settingsClick(e) || dashClick(e) || actionClick(e) || formClick(e)) return
  if (!q('#adPop .panel, #adPop .ad-menu') && ST.pop && ST.pop !== 'pal' && q('#adApp') && !q('[data-ad-pop]')) { /* 点击别处由遮罩关闭 */ }
}
document.addEventListener('click', onClick)
/* 捕获阶段：带原因的禁用项点了只说明原因 */
document.addEventListener('click', (e) => {
  const d = e.target.closest && e.target.closest('[aria-disabled="true"][data-reason]')
  if (d && !d.closest('[data-shell]')) { e.preventDefault(); e.stopPropagation(); K.toast(d.dataset.reason, 'warn'); return }
}, true)
document.addEventListener('input', (e) => {
  if (e.target.id === 'adPalIn') { ST.palQ = e.target.value; ST.palI = 0; $('#adPalList').innerHTML = palListH(); return }
  if (formInput(e) || settingsInput(e)) return
  onListInput(e)
})
document.addEventListener('change', (e) => { onListChange(e) })
document.addEventListener('focusout', formBlur)
document.addEventListener('pointermove', chartMove)
document.addEventListener('pointerout', (e) => { const b = e.target.closest && e.target.closest('[data-line]'); if (b && !(e.relatedTarget && b.contains(e.relatedTarget))) chartLeave(e) })
document.addEventListener('keydown', (e) => {
  if ((e.ctrlKey || e.metaKey) && (e.key === 'k' || e.key === 'K') && $('#adApp')) { e.preventDefault(); if (!document.getElementById('ptDlg').open) { ST.pop = null; openPop('pal') } return }
  if (e.key === 'Escape' && ST.pop) { e.stopPropagation(); closePopOnly(); return }
  if (e.target.id === 'adPalIn') {
    const n = palItems().length
    if (e.key === 'ArrowDown') { e.preventDefault(); ST.palI = (ST.palI + 1) % Math.max(1, n); $('#adPalList').innerHTML = palListH() }
    else if (e.key === 'ArrowUp') { e.preventDefault(); ST.palI = (ST.palI - 1 + n) % Math.max(1, n); $('#adPalList').innerHTML = palListH() }
    else if (e.key === 'Enter') { const it = palItems()[ST.palI]; if (it) { closePopOnly(); activate(it.t.id) } }
    return
  }
  if (e.target.closest && e.target.closest('[data-line]') && /^Arrow(Left|Right)$/.test(e.key)) { e.preventDefault(); chartMove(e); return }
  formKey2(e)
})
document.addEventListener('focusin', (e) => { const b = e.target.closest && e.target.closest('[data-line]'); if (b && e.target.matches('rect.hit') && b.dataset.i === undefined) chartMove({ type: 'keydown', key: 'x', target: e.target }) })
/* 预览宽度：舞台里的外壳工具，不是产品界面 */
document.addEventListener('click', (e) => {
  const b = e.target.closest && e.target.closest('[data-ad-w]'); if (!b) return
  const app = $('#adApp'); app.dataset.w = b.dataset.adW; $$('[data-ad-w]').forEach((x) => x.setAttribute('aria-pressed', String(x === b))); applyMode()
})
if (typeof ResizeObserver !== 'undefined') new ResizeObserver(() => applyMode()).observe($('#adApp'))
addEventListener('resize', applyMode)
applyMode()

K.on('reset', () => { ST.open = []; ST.grp = new Set(); ST.pop = null; ST.collapsed = false; LS.clear(); DRAFTS.clear(); SWBUSY.clear(); SWERR.clear(); SETST.edit = null; SETST.cat = {}; DST.range = {}; DST.metric = {}; DST.off = {}; DST.alert = new Set(); PAGE_SIZE = null; SUBMITTING.clear() })
AD.activate = activate
