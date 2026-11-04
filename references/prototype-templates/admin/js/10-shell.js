/* ===== 外壳：侧栏、顶栏、多标签页、面包屑、通知与账号菜单、命令面板 ===== */
const DEFAULT_MARK = "<rect x='5' y='6' width='22' height='20' rx='4'/><path d='M5 12h22M12 12v14'/>"
const ST = (AD.state = { open: [], collapsed: false, pop: null, palQ: '', palI: 0, grp: new Set() })
const homeId = () => (K.tabs[0] || {}).id
/* 侧栏菜单树：带 page 的是标签，不带 page、带 children 的是分组节点（引擎的 K.tabs 只含标签）。没有图标的分组节点是分组标题，有图标的是手风琴父项 */
const navPathOf = (id, nodes = K.spec.nav, path = []) => {
  for (const n of nodes || []) {
    if (n.id === id) return path
    if (n.children) { const r = navPathOf(id, n.children, path.concat(n)); if (r) return r }
  }
  return null
}
const groupHas = (n, tabId) => (n.children || []).some((k) => k.id === tabId || (k.children && groupHas(k, tabId)))
const badgeOf = (t) => {
  const b = t.badge; if (!b) return 0
  return typeof b === 'string' ? num(K.get(b)) : rowsOf(b.count).filter((r) => matches(r, b.where)).length
}
const noticesOf = () => (shell().notices || [])
const unread = () => noticesOf().filter((n) => !n.read).length
const mode = () => { const w = $('#adApp') ? $('#adApp').clientWidth : 1200; return w < 640 ? 'narrow' : w < 960 ? 'mid' : 'wide' }

/* ---------- 打开的标签页：页面栈由引擎保留（keepTabStacks），这里只记“打开了哪些标签”；列表状态、表单草稿、滚动位置各标签自己留着 ---------- */
function syncOpen() {
  const t = K.S.tab; if (!t) return
  if (!ST.open.some((x) => x.id === t)) { ST.open.push({ id: t }); trimTabs(t) }
}
function trimTabs(keep) {
  while (ST.open.length > 15) { const i = ST.open.findIndex((x) => x.id !== homeId() && x.id !== keep); if (i < 0) break; dropState(ST.open[i].id); ST.open.splice(i, 1) }
}
function dropState(tabId) {
  K.S.stacks[tabId] = []
  K.spec.pages.filter((p) => pageTab(p) === tabId).forEach((p) => { LS.delete(p.id); [...DRAFTS.keys()].filter((k) => k.startsWith(p.id + '|')).forEach((k) => DRAFTS.delete(k)) })
  Object.keys(K.S.sc).filter((k) => k.startsWith(tabId + '|')).forEach((k) => delete K.S.sc[k])
}
/* 切到某个标签：K.toTab 在 keepTabStacks 下保留各标签的页面栈；再点当前标签回到它的根页。preset 是从待办、预警直达时带的筛选 */
function activate(id, preset) {
  if (!K.tabs.some((t) => t.id === id)) return
  if (!ST.open.some((x) => x.id === id)) { ST.open.push({ id }); trimTabs(id) }
  if (preset) { applyPreset(id, preset); K.S.stacks[id] = [] }
  K.batch(() => { K.toTab(id); if (preset) K.render({ fresh: true }) })
  closeChrome()
}
function applyPreset(tabId, preset) {
  const p = rootPageOf(tabId); if (!p.list) return
  LS.delete(p.id); const s = lstate(p)
  if (preset.tab != null) s.tab = preset.tab
  if (preset.q) s.q = preset.q
  Object.assign(s.f, preset.filters || {})
  if (preset.sort) s.sort = preset.sort
}
function closeTab(id) {
  if (id === homeId()) return
  const i = ST.open.findIndex((x) => x.id === id); if (i < 0) return
  const wasActive = K.S.tab === id
  ST.open.splice(i, 1); dropState(id)
  if (wasActive) activate((ST.open[i - 1] || ST.open[0]).id); else drawTabs()
}
function closeOthers(keepAll) {
  const keep = keepAll ? [homeId()] : [homeId(), K.S.tab]
  ST.open.filter((o) => !keep.includes(o.id)).forEach((o) => dropState(o.id))
  ST.open = ST.open.filter((o) => keep.includes(o.id))
  if (!ST.open.some((o) => o.id === K.S.tab)) activate(homeId()); else drawTabs()
  closeChrome()
}

/* ---------- 绘制：侧栏 ---------- */
function navH(n, level, ctx) {
  if (n.hidden) return ''
  if (n.children && !n.page) {
    const kids = n.children.filter((k) => !k.hidden)
    if (!n.icon) return `<div class="ad-ngt-sep" aria-hidden="true"></div><div class="ad-ngt">${esc(n.name)}</div>` + kids.map((k) => navH(k, level, ctx)).join('')
    const open = groupHas(n, K.S.tab) || ST.grp.has(n.id)
    return `<div class="ad-npar" data-open="${open ? 1 : 0}"><button type="button" class="ad-ni parent" data-ad-grp="${esc(n.id)}" aria-expanded="${open}" title="${esc(n.name)}" aria-label="${esc(n.name)}"${groupHas(n, K.S.tab) ? ' data-anc="1"' : ''}>${ic(n.icon)}<span class="lb">${esc(n.name)}</span>${ic('chev', 's chev')}</button><div class="ad-nkids"${open ? '' : ' hidden'}>${kids.map((k) => navH(k, level + 1, ctx)).join('')}</div></div>`
  }
  const b = badgeOf(n)
  return `<button type="button" class="ad-ni${level > 1 ? ' sub' : ''}" data-ad-nav="${esc(n.id)}" data-route="#/${esc(n.page)}" title="${esc(n.name)}" aria-label="${esc(n.name)}"${K.S.tab === n.id ? ' aria-current="page"' : ''}>${level > 1 ? '' : ic(n.icon || 'list')}<span class="lb">${esc(n.name)}</span>${b > 0 ? `<span class="bdg" aria-label="${b} 条待处理">${b > 99 ? '99+' : b}</span>` : ''}</button>`
}
function drawSide() {
  const el = $('#adSide'); if (!el) return
  let h = '<nav class="ad-nav" aria-label="主菜单">', prevSection = false
  ;(K.spec.nav || []).filter((n) => !n.hidden).forEach((n) => {
    const section = !!(n.children && !n.page && !n.icon)
    if (!section && prevSection) h += '<div class="ad-ngt-sep" aria-hidden="true"></div>'
    h += navH(n, 1); prevSection = section
  })
  h += `</nav><div class="ad-sidefoot"><button type="button" class="app-version" data-ad-ver aria-label="版本信息">${ic('info', 's')}<span class="vt">版本 ${esc(shell().version || '1.0.0')}</span></button></div>`
  el.innerHTML = h
  el.setAttribute('data-cid', K.cfg.sidebar === 'dark' ? 'AD-NAV-002' : 'AD-NAV-001')
}
/* 手风琴父项：宽屏同一时刻只展开一个；图标栏与窄屏抽屉里点父项出悬浮菜单 */
function toggleGroup(btn) {
  const id = btn.dataset.adGrp, node = (function f(ns) { for (const n of ns || []) { if (n.id === id) return n; const r = n.children && f(n.children); if (r) return r } })(K.spec.nav)
  const app = $('#adApp')
  if (app.dataset.mode !== 'wide' || app.dataset.collapsed === '1') {
    if (app.dataset.mode === 'narrow') { ST.grp = ST.grp.has(id) ? new Set() : new Set([id]); drawSide(); return }
    openMenu(btn, (node.children || []).filter((k) => !k.hidden).map((k) => ({ label: k.name, attr: `data-ad-nav="${esc(k.id)}"` }))); return
  }
  ST.grp = ST.grp.has(id) ? new Set() : new Set([id])
  drawSide()
}

/* ---------- 绘制：顶栏 ---------- */
function drawTop() {
  const el = $('#adTop'); if (!el) return
  const m = K.spec.meta, sh = shell(), acc = sh.account || { name: '管理员', av: 0 }
  const n = unread()
  el.setAttribute('data-cid', 'AD-NAV-003')
  el.innerHTML = `<button type="button" class="ad-ib menu-btn" data-ad-side="toggle" aria-label="展开或收起侧栏">${ic('menu')}</button>
    <div class="tbrand"><span class="mk" aria-hidden="true"><svg viewBox="0 0 32 32" fill="none" stroke="currentColor" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round">${m.mark || DEFAULT_MARK}</svg></span><b>${esc(m.brand || m.title)}</b></div>
    <span class="sp"></span>
    <button type="button" class="ad-searchbtn" data-ad-pop="pal" aria-label="搜索页面和功能（Ctrl K）">${ic('search')}<span>搜索页面和功能</span><kbd>Ctrl K</kbd></button>
    ${sh.env ? `<span class="ad-env">${esc(sh.env)}</span>` : ''}
    <button type="button" class="ad-ib" data-ad-pop="bell" aria-label="通知，${n} 条未读" aria-haspopup="dialog">${ic('bell')}${n ? `<span class="dot">${n}</span>` : ''}</button>
    <button type="button" class="ad-acct" data-ad-pop="acct" aria-label="账号菜单" aria-haspopup="menu">${LIB.critter(acc.av != null ? acc.av : 0, 28)}<span class="nm">${esc(acc.name)}</span>${ic('chev', 's')}</button>`
}

/* ---------- 绘制：多标签页 ---------- */
function drawTabs() {
  const el = $('#adTabs'); if (!el) return
  el.setAttribute('data-cid', 'AD-NAV-005')
  el.innerHTML = ST.open.map((o) => {
    const t = tabOf(o.id), on = o.id === K.S.tab, pinned = o.id === homeId()
    return `<div class="ad-tab" data-on="${on ? 1 : 0}" data-tabid="${esc(o.id)}"><button type="button" class="tb" role="tab" aria-selected="${on}" data-ad-nav="${esc(o.id)}" title="${esc(t.name)}">${pinned ? `<span class="pin" aria-hidden="true">${ic('pin2', 's')}</span>` : ''}<span>${esc(t.name)}</span></button>${pinned ? '' : `<button type="button" class="tx" data-ad-close="${esc(o.id)}" aria-label="关闭 ${esc(t.name)}">${ic('close', 's')}</button>`}</div>`
  }).join('') + `<button type="button" class="ad-ib more" data-ad-pop="tabs" aria-label="标签页操作" aria-haspopup="menu">${ic('more')}</button>`
}

/* ---------- 绘制：面包屑（只在二级页、子页、结果页出现；一级菜单页不放） ---------- */
function drawCrumb() {
  const el = $('#adCrumb'); if (!el) return
  const st = K.S.stacks[K.S.tab] || []
  if (!st.length) { el.hidden = true; el.innerHTML = ''; return }
  const parts = [`<button type="button" data-pt-back="${st.length}">${esc(tabOf(K.S.tab).name)}</button>`]
  st.forEach((f, i) => {
    const p = K.pages[f.id] || {}
    const label = rec(p.crumb || p.name, findRowOfPage(p, f.a))
    parts.push(i < st.length - 1 ? `<button type="button" data-pt-back="${st.length - 1 - i}">${esc(label)}</button>` : `<b aria-current="page">${esc(label)}</b>`)
  })
  el.setAttribute('data-cid', 'AD-NAV-004')
  el.innerHTML = parts.join(ic('chev', 's')); el.hidden = false
}

/* ---------- 弹出层：通知、账号、标签页菜单、命令面板（都在 .ad-app 里，不是 position: fixed） ---------- */
function palItems() {
  const q = ST.palQ.trim().toLowerCase()
  return K.tabs.map((t) => ({ t, path: (navPathOf(t.id) || []).map((n) => n.name).join(' › ') })).filter(({ t, path }) => !q || (t.name + path).toLowerCase().includes(q))
}
function drawPop() {
  const el = $('#adPop'); if (!el) return
  if (!ST.pop) { el.hidden = true; el.innerHTML = ''; return }
  const sh = shell(), acc = sh.account || { name: '管理员', av: 0 }
  let h = '<div class="ov" data-ad-pop="close"></div>'
  if (ST.pop === 'bell') {
    const list = noticesOf().slice(0, 6)
    h += `<div class="panel bell" role="dialog" aria-label="通知" data-cid="AD-NAV-013"><h4>通知<button type="button" class="ad-btn text" data-ad-notice="all">全部已读</button></h4><ul class="nl">${list.length ? list.map((n) => `<li><button type="button" data-ad-notice="${esc(n.id)}"><i class="u${n.read ? ' r' : ''}"></i><span><b>${esc(n.title)}</b><small>${esc(n.time || '')}</small></span></button></li>`).join('') : '<li class="ad-empty" style="border:0">暂无通知</li>'}</ul>${sh.noticePage ? `<div style="padding:4px 8px"><button type="button" class="ad-btn text" data-ad-nav="${esc(pageTab(K.pages[sh.noticePage] || {}) || sh.noticePage)}">查看全部通知</button></div>` : ''}</div>`
  } else if (ST.pop === 'acct') {
    const ap = K.cfg.appearance || 'auto'
    h += `<div class="panel acct" role="menu" aria-label="账号菜单" data-cid="AD-NAV-011"><div class="acc-h">${LIB.critter(acc.av != null ? acc.av : 0, 40)}<div><b>${esc(acc.name)}</b><small>${esc(roleName())}${acc.store ? ' · ' + esc(acc.store) : ''}</small></div></div><hr>
      ${sh.profilePage ? `<button type="button" class="it" role="menuitem" data-ad-nav="${esc(pageTab(K.pages[sh.profilePage] || {}) || sh.profilePage)}">${ic('user')}个人资料</button>` : ''}
      <div class="acc-r"><span>外观</span><div class="ad-seg" role="group" aria-label="外观">${[['auto', '跟随系统'], ['light', '浅色'], ['dark', '深色']].map(([v, l]) => `<button type="button" data-ad-appear="${v}" aria-pressed="${ap === v}">${l}</button>`).join('')}</div></div><hr>
      <button type="button" class="it" role="menuitem" data-ad-logout>${ic('logout')}退出登录</button></div>`
  } else if (ST.pop === 'tabs') {
    h += `<div class="panel acct" role="menu" aria-label="标签页操作" style="top:96px;width:200px;padding:4px"><button type="button" class="it" role="menuitem" data-ad-tabsop="others">关闭其他标签页</button><button type="button" class="it" role="menuitem" data-ad-tabsop="all">关闭全部（保留首页）</button><button type="button" class="it" role="menuitem" data-ad-tabsop="home">回到首页</button></div>`
  } else if (ST.pop === 'menu') {
    h += menuH()
  } else if (ST.pop === 'pal') {
    h += `<div class="panel pal" role="dialog" aria-label="搜索页面和功能" data-cid="AD-NAV-012"><input class="ad-in" id="adPalIn" type="search" placeholder="输入页面名称，Enter 打开，Esc 关闭" aria-label="搜索页面和功能" value="${esc(ST.palQ)}" style="width:100%"><ul class="pl" id="adPalList">${palListH()}</ul></div>`
  }
  el.innerHTML = h; el.hidden = false
  const inp = $('#adPalIn', el); if (inp) { inp.focus(); inp.setSelectionRange(inp.value.length, inp.value.length) }
}
function palListH() {
  const items = palItems(); ST.palI = Math.min(ST.palI, Math.max(0, items.length - 1))
  return items.length ? items.map(({ t, path }, i) => `<li><button type="button" data-ad-palgo="${esc(t.id)}" aria-selected="${i === ST.palI}">${ic(t.icon || 'list')}<span>${esc(t.name)}</span><small>${esc(path || '菜单')}</small></button></li>`).join('') : `<li class="ad-empty" style="border:0">没有找到「${esc(ST.palQ)}」，换个词试试</li>`
}
function closeChrome() { ST.pop = null; drawPop(); const app = $('#adApp'); if (app) app.dataset.side = 'closed' }
function openPop(name) { ST.pop = ST.pop === name ? null : name; if (name === 'pal') { ST.palQ = ''; ST.palI = 0 } drawPop() }

/* ---------- 外壳整体刷新（每次渲染后调用）---------- */
function drawShell() { drawSide(); drawTop(); drawTabs(); drawCrumb() }
function applyMode() {
  const app = $('#adApp'); if (!app) return
  const m = mode(); app.dataset.mode = m
  app.dataset.collapsed = ST.collapsed && m !== 'narrow' ? '1' : '0'
  const n = $('#adWidthNow'); if (n) n.textContent = `舞台宽度 ${app.clientWidth} px`
}
AD.activate = activate
AD.closeTab = closeTab
