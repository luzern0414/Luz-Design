/* ===== 页面：域、类别、搜索、编号索引、复制编号 ===== */
const TABS_ALL = { mp: [['COMBO', '整页组合'], ...CATS.mp], ad: CATS.ad }
let S = { dom: 'mp', cat: 'COMBO', theme: 'rose', icon: '3d', q: '', hl: '', combo: { head: '渐变头图 + 商品图', entry: '3 × 2 金刚区', card: '标准商品卡', btn: '渐变实心', nav: '标准', price: '标准红价 + 渐变标签' } }
const el = (id) => document.getElementById(id)
const COPY_SVG = '<svg viewBox="0 0 24 24"><rect x="8" y="8" width="12" height="12" rx="2.5"/><path d="M16 8V6a2 2 0 0 0-2-2H6a2 2 0 0 0-2 2v8a2 2 0 0 0 2 2h2"/></svg>'
const catName = (dom, cat) => (CATS[dom].find((c) => c[0] === cat) || [0, cat])[1]
const inCat = (dom, cat) => BLOCKS.filter((b) => b.dom === dom && b.cat === cat)
const sortById = (a, b) => a.id.localeCompare(b.id)
function copyText(text, msg) {
  const done = () => { const t = el('toast'); t.textContent = msg; t.classList.add('on'); setTimeout(() => t.classList.remove('on'), 1600) }
  if (navigator.clipboard && navigator.clipboard.writeText) navigator.clipboard.writeText(text).then(done, () => fb(text, done)); else fb(text, done)
}
function fb(text, done) { const a = document.createElement('textarea'); a.value = text; a.style.cssText = 'position:fixed;opacity:0'; document.body.appendChild(a); a.select(); try { document.execCommand('copy') } catch (e) {} a.remove(); done() }
function guideRows(dom, cat) {
  if (GUIDES[dom + '|' + cat]) return GUIDES[dom + '|' + cat]
  const tab = Object.entries(LEGACY_TAB).find(([, c]) => c === cat)
  if (dom === 'mp' && cat === 'FB') return GUIDES['表单弹层']
  return dom === 'mp' && tab ? GUIDES[tab[0]] : null
}
function cardHTML(b) {
  const bgs = b.bg ? `style="background-image:url(${ASSETS.bg[b.bg]})"` : ''
  return `<article class="tc ${b.wide ? 'wide' : ''}" id="${b.id}" data-dom="${b.dom}"><div class="st ${stageClass(b.stage)} ${ICS()}" ${bgs}><div class="ixr" data-id="${b.id}" data-cid="${b.id}">${b.html()}</div></div><div class="mt"><div class="ttl"><b>${b.name}</b><span class="sty">${b.style}</span></div><p class="fit"><em>适合</em><span>${b.fit}</span></p><p class="avd"><em>避免</em><span>${b.avoid}</span></p><button class="idc" type="button" data-id="${b.id}" aria-label="复制编号 ${b.id}"><b>${b.id}</b>${COPY_SVG}<span>复制编号</span></button></div></article>`
}
function gridHTML(list, dom) { return `<div class="grid" style="column-width:${DOMS[dom].col}px">${list.map(cardHTML).join('')}</div>` }
function guideHTML(dom, cat) {
  const g = guideRows(dom, cat)
  return g ? `<section class="guide"><h2>${catName(dom, cat)}：怎么选</h2><table><thead><tr><th>场景</th><th>推荐</th><th>原因</th></tr></thead><tbody>${g.map(([a, b, c]) => `<tr><td data-l="场景">${a}</td><td data-l="推荐">${b}</td><td data-l="原因">${c}</td></tr>`).join('')}</tbody></table></section>` : ''
}
function indexHTML() {
  const rows = (d) => CATS[d].map(([c, n]) => inCat(d, c).sort(sortById).map((b) => `<tr data-k="${(b.id + ' ' + b.name + ' ' + b.style + ' ' + b.kw).toLowerCase()}"><td data-l="编号"><button class="idc sm" type="button" data-id="${b.id}"><b>${b.id}</b>${COPY_SVG}</button></td><td data-l="名称"><button class="lk" type="button" data-goto="${b.id}">${b.name}</button></td><td data-l="类别">${DOMS[d].name} · ${n}</td><td data-l="风格">${b.style}</td><td data-l="适合">${b.fit}</td></tr>`).join('')).join('')
  const n = (d) => BLOCKS.filter((b) => b.dom === d).length
  return `<section class="guide"><h2>编号索引（共 ${BLOCKS.length} 个：小程序 ${n('mp')}，后台管理 ${n('ad')}）</h2><p class="hint">以后要用哪个组件，复制编号告诉我就行。点编号复制，点名称跳到那个组件。</p><input class="qin" id="idxq" type="search" placeholder="筛选编号、名称、风格或关键词" value=""><div class="tscroll"><table class="idx"><thead><tr><th>编号</th><th>名称</th><th>类别</th><th>风格</th><th>适合</th></tr></thead><tbody id="idxb">${rows('mp')}${rows('ad')}</tbody></table></div></section>`
}
function searchHTML() {
  const q = S.q.trim().toLowerCase()
  const list = BLOCKS.filter((b) => (b.id + ' ' + b.name + ' ' + b.style + ' ' + b.fit + ' ' + b.kw + ' ' + catName(b.dom, b.cat)).toLowerCase().includes(q)).sort(sortById)
  return `<section class="guide"><h2>搜索“${S.q.replace(/</g, '&lt;')}”：${list.length} 个结果</h2></section>` + (list.length ? gridHTML(list, 'mp') : '')
}
function renderTools() {
  const tabs = TABS_ALL[S.dom].filter(([c]) => c === 'COMBO' || inCat(S.dom, c).length)
  el('doms').innerHTML = [['mp', '小程序'], ['ad', '后台管理'], ['idx', '编号索引']].map(([k, t]) => `<button type="button" data-dom="${k}" aria-pressed="${S.dom === k || (k === 'idx' && S.cat === 'INDEX')}">${t}<em>${k === 'idx' ? BLOCKS.length : BLOCKS.filter((b) => b.dom === k).length}</em></button>`).join('')
  el('sws').innerHTML = THEMES.map((t) => `<button type="button" class="sw" data-theme="${t.id}" title="${t.name}" aria-label="${t.name}" aria-pressed="${S.theme === t.id}" style="background:linear-gradient(145deg,${mixc(t.p, '#FFFFFF', 0.8)},${t.p})"></button>`).join('')
  el('icseg').innerHTML = ICON_STYLES.map(([id, t]) => `<button type="button" data-icon="${id}" aria-pressed="${S.icon === id}">${t}</button>`).join('')
  el('apseg').innerHTML = APPEARANCES.map(([id, t]) => `<button type="button" data-ap="${id}" aria-pressed="${getAppearance() === id}">${t}</button>`).join('')
  el('tabs').innerHTML = S.cat === 'INDEX' || S.cat === 'SEARCH' ? '' : tabs.map(([c, n]) => `<button class="tab" role="tab" data-cat="${c}" aria-selected="${S.cat === c}">${n}${c === 'COMBO' ? '' : `<em>${inCat(S.dom, c).length}</em>`}</button>`).join('')
}
function renderContent() {
  ICON_STYLE = S.icon; applyTheme(el('root'), S.theme)
  const c = el('content')
  if (S.cat === 'SEARCH') c.innerHTML = searchHTML()
  else if (S.cat === 'INDEX') c.innerHTML = indexHTML()
  else if (S.cat === 'COMBO') c.innerHTML = comboPage()
  else c.innerHTML = guideHTML(S.dom, S.cat) + gridHTML(inCat(S.dom, S.cat).sort(sortById), S.dom)
  IX.init(c)
  c.querySelectorAll('.ixr[data-id]').forEach((r) => { const b = BLOCKS.find((x) => x.id === r.dataset.id); if (b && b.js) { try { b.js(r) } catch (e) { console.error(b.id, e) } } })
  if (S.hl) { const t = document.getElementById(S.hl); if (t) { t.scrollIntoView({ block: 'center' }); t.classList.add('flash'); setTimeout(() => t.classList.remove('flash'), 1800) } S.hl = '' }
}
function renderAll() { renderTools(); renderContent() }
function gotoId(id) {
  const b = BLOCKS.find((x) => x.id === id); if (!b) return false
  S.dom = b.dom; S.cat = b.cat; S.q = ''; S.hl = id; renderAll(); return true
}
document.addEventListener('click', (e) => {
  const b = e.target.closest('button'); if (!b || b.closest('.ixr')) return
  const d = b.dataset
  if (d.id !== undefined && b.classList.contains('idc')) { copyText(d.id, '已复制编号 ' + d.id); return }
  if (d.goto) { gotoId(d.goto); history.replaceState(null, '', '#' + d.goto); return }
  if (d.combocopy !== undefined) return copyCombo()
  if (d.slot) { S.combo[d.slot] = d.opt; renderContent(); return }
  if (d.dom) { if (d.dom === 'idx') { S.cat = 'INDEX' } else { S.dom = d.dom; S.cat = d.dom === 'mp' ? 'COMBO' : (CATS.ad.find((c) => inCat('ad', c[0]).length) || ['TBL'])[0] } S.q = ''; el('q').value = ''; renderAll(); scrollTo({ top: 0 }); return }
  if (d.cat) { S.cat = d.cat; scrollTo({ top: 0 }); renderAll(); return }
  if (d.ap) { setAppearance(d.ap); renderTools(); return }
  if (d.theme) S.theme = d.theme; else if (d.icon) S.icon = d.icon; else return
  renderAll()
})
document.addEventListener('input', (e) => {
  if (e.target.id === 'q') { S.q = e.target.value; if (S.q.trim()) { S.cat = 'SEARCH' } else { S.cat = S.dom === 'mp' ? 'COMBO' : 'TBL' } renderAll() }
  if (e.target.id === 'idxq') { const q = e.target.value.trim().toLowerCase(); document.querySelectorAll('#idxb tr').forEach((r) => { r.hidden = q !== '' && !r.dataset.k.includes(q) }) }
})
const bs = document.createElement('style'); bs.textContent = BLOCKS.map((b) => b.css).join('\n') + '\n' + COMBO_CSS; document.head.appendChild(bs)
window.__REGISTRY__ = () => BLOCKS.map((b) => { ICON_STYLE = '3d'; return { id: b.id, dom: b.dom, cat: b.cat, catName: catName(b.dom, b.cat), name: b.name, style: b.style, fit: b.fit, avoid: b.avoid, kw: b.kw, stage: b.stage, wide: b.wide, bg: b.bg, css: b.css, html: b.html().replace(/data:image\/[a-z]+;base64,[A-Za-z0-9+/=]+/g, 'your-image.webp'), js: b.js ? String(b.js) : '' } })
renderTools()
if (location.hash && gotoId(decodeURIComponent(location.hash.slice(1)))) { /* 编号直达 */ } else renderContent()
addEventListener('hashchange', () => { if (location.hash) gotoId(decodeURIComponent(location.hash.slice(1))) })
