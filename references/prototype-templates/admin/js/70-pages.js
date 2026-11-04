/* ===== 页面：一页 = 页面顶部区 + 原生视图（列表 / 工作台 / 设置 / 表单 / 结果）+ blocks / custom；状态页 ===== */
function customH(name, args, frame, ctx) {
  const f = K.contentDef && K.contentDef.pages && K.contentDef.pages[name]
  if (!f) return `<div class="pt-miss">内容模块里没有「${esc(name)}」</div>`
  return `<div class="ad-custom" data-custom="${esc(name)}">${f(frame, ctx, args || {})}</div>`
}
function itemsH(list, frame, ctx) {
  return (list || []).map((it, i) => {
    if (it.id !== undefined || it.cid || it.custom) { if (K.moduleHidden(frame.page.id, it.id || 'b' + i)) return '' }
    if (it.custom) return customH(it.custom, it.args, frame, ctx)
    if (it.gap !== undefined) return `<div class="ad-gap" style="height:${+it.gap || 12}px"></div>`
    if (it.heading) return `<h3 class="ad-hd3">${esc(it.heading)}</h3>`
    if (it.cid) return K.block(it.cid, K.ovOf(it)).replace('class="pt-blk"', 'class="pt-blk ad-blk"')
    return ''
  }).join('')
}
const FAILS = {
  'fail-network': ['网络不可用', '请检查网络连接后重试'], 'fail-timeout': ['请求超时', '服务器响应较慢，请稍后重试'],
  'fail-server': ['服务繁忙', '当前访问人数较多，请稍后重试'], 'fail-expired': ['数据已失效', '内容已发生变化，请刷新后再看'],
}
function stateView(view, p, frame, ctx) {
  if (view === 'loading') return `<div class="ad-sk" data-cid="AD-STATE-003" role="status" aria-label="加载中"><i class="h"></i><i class="m"></i><i></i><i></i><i class="s"></i><i></i><i class="m"></i></div>`
  if (view === 'empty') {
    const e = p.empty || {}
    return `<div class="ad-empty" data-cid="AD-STATE-001">${LIB.tileHTML(e.tile || 'bag', 'ci')}<h3>${esc(e.title || '这里还没有内容')}</h3><p>${esc(e.text || '有了新内容会出现在这里')}</p>${e.go ? `<div class="row">${btnH({ label: e.button || '去看看', go: K.pages[e.go] && K.pages[e.go].type === 'tab' ? undefined : e.go, tab: K.pages[e.go] && K.pages[e.go].type === 'tab' ? pageTab(K.pages[e.go]) : undefined, kind: 'primary' })}</div>` : ''}</div>`
  }
  if (view.indexOf('fail') === 0) {
    const [t, d] = FAILS[view] || FAILS['fail-server']
    return `<div class="ad-empty" data-cid="AD-STATE-002">${LIB.tileHTML('cart', 'ci')}<h3>${t}</h3><p>${d}。请求编号 RQ-${String(hash(p.id + view)).slice(0, 6)}</p><div class="row"><button type="button" class="ad-btn primary" data-pt-act="retry">${ic('refresh')}重试</button>${frame.depth ? '<button type="button" class="ad-btn" data-pt-back>返回</button>' : ''}</div></div>`
  }
  if (view === 'denied') {
    const r = ctx.roleDef || {}, g = r.deniedGo && K.pages[r.deniedGo]
    const need = (p.roles || []).map((id) => (K.roles.find((x) => x.id === id) || {}).name || id).join('、')
    return `<div class="ad-empty" data-cid="AD-STATE-006">${LIB.tileHTML('wallet', 'ci')}<h3>暂无权限</h3><p>当前身份：${esc(r.name || '未知')}。${need ? `这个页面需要「${esc(need)}」。` : ''}${esc(r.note || '')}</p>${g ? `<div class="row">${btnH({ label: r.deniedLabel || '去申请权限', kind: 'primary', go: g.type === 'tab' ? undefined : g.id, tab: g.type === 'tab' ? pageTab(g) : undefined })}</div>` : ''}</div>`
  }
  return ''
}
function resultH(p) {
  const R = p.result, tone = R.tone || 'ok', icon = { ok: 'checkc', dg: 'closec', wn: 'alert', empty: 'box', denied: 'lock' }[tone] || 'info', cid = { ok: 'AD-STATE-004', dg: 'AD-STATE-002', wn: 'AD-STATE-004', empty: 'AD-STATE-001', denied: 'AD-STATE-002' }[tone]
  const facts = (R.facts || []).map(([k, v]) => `<dt>${esc(k)}</dt><dd>${esc(rec(v, {}))}</dd>`).join('')
  return `<div class="ad-card ad-result" data-cid="${cid}" style="padding:36px 20px;text-align:center"><span class="ad-tag ${tone === 'ok' ? 'ok' : tone === 'dg' ? 'dg' : tone === 'wn' ? 'wn' : 'mu'}" style="width:56px;height:56px;border-radius:50%;justify-content:center"><i class="ad-ic l" style="width:30px;height:30px">${sv(icon)}</i></span><h2 class="ad-h2" style="margin:12px 0 4px">${esc(R.title)}</h2><p style="color:var(--ad-ink2);margin:0 auto;max-width:480px">${esc(R.text || '')}</p>${facts ? `<dl class="ad-dl" style="max-width:420px;margin:16px auto 0;text-align:left;grid-template-columns:96px 1fr">${facts}</dl>` : ''}<div class="row" style="display:flex;gap:8px;justify-content:center;margin-top:20px;flex-wrap:wrap">${(R.actions || []).map((a) => btnH(a)).join('')}</div></div>`
}
function headerZone(p) {
  const acts = (p.actions || []).map((a) => btnH(a)).join('')
  return acts ? `<div class="ad-ph" data-cid="AD-NAV-007"><div class="l"></div><div class="r">${acts}</div></div>` : ''
}
function subHeader(p, frame) {
  const row = findRowOfPage(p, frame.a), title = row ? rec(p.title || p.name, row) : p.titleNew || p.name
  return `<div class="ad-sub" data-cid="AD-NAV-006"><h2 class="ad-h2">${esc(title)}</h2><span class="sp"></span>${(p.actions || []).map((a) => btnH(a)).join('')}</div>`
}
function pageBody(p, frame, ctx) {
  let h = ''
  if (p.type === 'sub' || p.type === 'result') h += subHeader(p, frame)
  if (p.dashboard) h += dashH(p)
  else if (p.list) h += listH(p)
  else if (!p.form && !p.settings) h += p.type === 'tab' ? headerZone(p) : ''
  if (p.settings) h += (p.type === 'tab' ? headerZone(p) : '') + settingsH(p)
  if (p.form) h += `<div class="ad-formwrap"><div class="ad-card" style="padding:0 0 0">${formBodyH(p, frame.a, false)}${formBarH(p, frame.a, false)}</div></div>`
  if (p.result) h += resultH(p)
  if (p.custom && !K.moduleHidden(p.id, 'custom')) h += customH(p.custom, p.args, frame, ctx)
  h += itemsH(p.blocks, frame, ctx)
  return h
}
/* 场景面板的“模块显示”：工作台的指标卡与各模块、blocks 的每一项、custom 内容各一个开关；名字取 name，再取 id，再取组件编号加名称 */
function modules(p) {
  const out = []
  if (p.dashboard) {
    if ((p.dashboard.kpis || []).length) out.push({ key: 'kpis', label: '指标卡' })
    ;(p.dashboard.sections || []).forEach((s, i) => out.push({ key: s.id || 'sec' + i, label: s.name || s.title || s.id }))
  }
  ;(p.blocks || []).forEach((it, i) => {
    if (it.gap !== undefined || (!it.cid && !it.custom && it.id === undefined)) return
    const info = it.cid ? K.cidInfo(it.cid) : null
    out.push({ key: it.id || 'b' + i, label: it.name || it.id || (info ? `${info.id} ${info.name}` : it.custom || it.cid) })
  })
  if (p.custom) out.push({ key: 'custom', label: '自定义内容' })
  return out
}
/* 局部重画：K.render({part: 'list:页面 id' | 'settings' | 'dash'})，返回被替换的元素，引擎按 data-fk 恢复焦点 */
function renderPart(part) {
  const i = part.indexOf(':'), kind = i < 0 ? part : part.slice(0, i), id = i < 0 ? '' : part.slice(i + 1)
  if (kind === 'list') { const w = $(`.ad-list[data-list="${CSS.escape(id)}"]`); if (w) paintList(w); return w }
  if (kind === 'settings') return repaintSettings()
  if (kind === 'dash') return repaintDash()
  return null
}
function render(frame, ctx) {
  const p = frame.page, view = ctx.view
  let h = ''
  if (readonly()) h += `<div class="ad-banner info" role="status" data-cid="AD-FB-004">${ic('lock')}<span class="tx">当前角色「${esc(roleName())}」是只读：所有页面都能看，写操作已禁用，悬停按钮可看原因。</span></div>`
  if (view === 'disabled') h += `<div class="ad-banner" role="status" data-cid="AD-FB-004">${ic('info')}<span class="tx">${esc(disabledReason())}</span></div>`
  h += view === 'ok' || view === 'disabled' ? pageBody(p, frame, ctx) : stateView(view, p, frame, ctx)
  return `<div class="pt-scroll ad-scroll" tabindex="-1">${LW(h)}</div>`
}
function mounted(root, frame, ctx) {
  syncOpen(); drawShell(); applyMode()
  const app = $('#adApp'); if (app && !app.hasAttribute('data-ready')) requestAnimationFrame(() => app.setAttribute('data-ready', '1'))
  root.querySelectorAll('.ad-tbl input[type="checkbox"][data-ad-l="selall"]').forEach((cb) => { const w = cb.closest('.ad-list'); if (w) paintListIndeterminate(w) })
  if (frame.page.list) lstate(frame.page).flash = null
}
function paintListIndeterminate(w) { const p = K.pages[w.dataset.list], s = lstate(p), all = $('[data-ad-l="selall"]', w); if (all) all.indeterminate = !all.checked && visibleRows(p.list, s).slice((s.page - 1) * s.size, s.page * s.size).some((r) => s.sel.has(String(r.id))) }

/* ---------- 配置组：侧栏深浅、密度（外观、主题色、图标风格由引擎内置）---------- */
const sidebarGroup = { id: 'sidebar', title: '侧栏深浅', type: 'seg', default: 'light', options: [{ v: 'light', label: '浅色' }, { v: 'dark', label: '深色' }], render: false, apply: () => { drawSide() }, note: '只改侧栏的底色；顶栏、内容区不变。' }
const densityGroup = { id: 'density', title: '密度', type: 'seg', default: 'standard', options: [{ v: 'compact', label: '紧凑 44' }, { v: 'standard', label: '标准 48' }], render: false, note: '表格行高：紧凑 44、标准 48，字号不变。' }
