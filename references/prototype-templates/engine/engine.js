/* ===== 共用引擎：页面栈、配置面板（K.panel）、场景、逻辑面板、弹层（dialog + showModal）、外观、减少动态 =====
 * 接口说明见 engine/ENGINE.md。这里只依赖 LIB（组件库封装）和浏览器；产品区的画法由 K.kind 注册的 kind 提供。 */
const K = (() => {
  const K = { LIB, version: 1 }
  const $ = (s, r = document) => r.querySelector(s)
  const $$ = (s, r = document) => [...r.querySelectorAll(s)]
  const esc = (s) => String(s ?? '').replace(/[&<>"']/g, (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' })[c])
  const clone = (o) => (o === undefined ? undefined : JSON.parse(JSON.stringify(o)))
  const root = () => document.getElementById('root')
  const html = document.documentElement
  const svg = (n, cls = '') => `<svg class="${cls}" viewBox="0 0 24 24" aria-hidden="true">${LIB.LINE[n] || ''}</svg>`
  const SH = ' data-shell'
  K.esc = esc; K.$ = $; K.$$ = $$; K.clone = clone; K.svg = svg

  /* ---------- 事件 ---------- */
  const handlers = {}
  K.on = (e, f) => { (handlers[e] = handlers[e] || []).push(f) }
  K.emit = (e, p) => (handlers[e] || []).forEach((f) => { try { f(p) } catch (err) { console.error(err) } })

  /* ---------- 状态 ---------- */
  const S = (K.S = { cfg: {}, tab: '', stacks: {}, sheet: null, scene: {}, role: '', net: 'online', view: 'ok', auto: false, flowOrigin: {}, sc: {}, hidden: {}, reduce: false, lt: 'pages', rt: 'logic' })
  K.cfg = S.cfg
  K.data = {}
  K.pages = {}
  K.tabs = []
  K.roles = []
  K.groups = []
  const blockMap = new Map(LIB.BLOCKS.map((b) => [b.id, b]))

  /* ---------- 演示数据：路径读写与模板 ---------- */
  const parts = (p) => String(p).split('.')
  K.get = (p, base = K.data) => parts(p).reduce((o, k) => (o == null ? undefined : o[k]), base)
  K.set = (p, v) => { const ks = parts(p), last = ks.pop(); const o = ks.reduce((a, k) => (a[k] == null ? (a[k] = {}) : a[k]), K.data); o[last] = v; K.render() }
  K.inc = (p, by = 1, o = {}) => K.set(p, Math.max(o.min ?? -Infinity, Math.min(o.max ?? Infinity, (+K.get(p) || 0) + by)))
  K.tpl = (s) => String(s).replace(/\{\{\s*([\w.]+)\s*\}\}/g, (m, p) => { const v = K.get(p); return v == null ? '' : v })

  /* ---------- 批处理：一次动作里多次 render 只画一次，提示等画完再弹 ---------- */
  let depth = 0, need = null // need = {fresh, restore, full, parts[]}
  const toastQ = []
  K.batch = (fn) => {
    depth++
    try { return fn() } finally {
      depth--
      if (!depth) { const o = need; need = null; if (o) { if (o.full) K.render(o); else o.parts.forEach((x) => K.render({ part: x })) } toastQ.splice(0).forEach(([m, t]) => K.toast(m, t)) }
    }
  }

  /* ---------- 页面与标签 ---------- */
  const typeLabel = (t) => (K.kindDef.typeLabel || { tab: '一级页', sub: '二级页', sheet: '弹层', result: '结果页' })[t] || t
  /* 标签/菜单：只有带 page 的节点是标签（K.tabs）；没有 page 的是分组节点，只管展开收起，可以有多级 children */
  const flatTabs = (list, out = []) => { (list || []).forEach((t) => { if (t.page) out.push(t); if (t.children) flatTabs(t.children, out) }); return out }
  const tabOfPage = (id) => { const p = K.pages[id]; if (!p) return K.tabs[0]?.id; if (p.type === 'tab') return (K.tabs.find((t) => t.page === id) || K.tabs[0] || {}).id; return p.tab || K.tabs[0]?.id }
  const tabRoot = (tab) => (K.tabs.find((t) => t.id === tab) || {}).page
  const stack = () => S.stacks[S.tab] || (S.stacks[S.tab] = [])
  K.cur = () => { const st = stack(), f = st.length ? st[st.length - 1] : { id: tabRoot(S.tab), a: '' }; return { id: f.id, a: f.a || '', page: K.pages[f.id] || {}, tab: S.tab, depth: st.length } }
  K.canBack = () => stack().length > 0
  const frontPage = () => (S.sheet ? K.pages[S.sheet.id] : K.cur().page) || {}

  /* ---------- 导航 ---------- */
  const navigated = (o) => { S.view = 'ok'; S.auto = false; if (S.net === 'slow' && o.fresh) { S.view = 'loading'; S.auto = true; const k = ++navSeq; setTimeout(() => { if (k === navSeq && S.auto && S.view === 'loading') { S.view = 'ok'; S.auto = false; K.render() } }, 900) } K.emit('nav', K.cur()); K.render(o) }
  let navSeq = 0
  /* 路由语义对应微信小程序的页面路由（官方文档“页面路由”）：
   *   go = navigateTo（压栈，目标必须是非标签栏页面）、replace = redirectTo（替换栈顶，同样不能是标签栏页面）、
   *   back = navigateBack（弹出若干层，栈里只有根页时失败）、toTab = switchTab（目标必须是标签栏页面，弹掉所有二级页）、
   *   jump = reLaunch（销毁所有页面并载入任意页面）。标签栏页面出现在栈里时必为栈底，所以这里栈里只放二级页和结果页。
   *   页面栈上限 MAX_DEPTH 是本技能的取值，不是微信的规定。 */
  const MAX_DEPTH = 10
  const clearStacks = () => K.tabs.forEach((t) => (S.stacks[t.id] = []))
  K.go = (id, a = '') => {
    const p = K.pages[id]; if (!p) { console.error('go: 页面不存在', id); return false }
    if (p.type === 'tab') { console.error('go 不能去标签栏页面，请改用 toTab：', id); K.toast('跳转方式不对：标签栏页面要用标签切换', 'warn'); return false }
    if (p.type === 'sheet') return K.openSheet(id, a)
    const st = stack()
    ;(K.spec.flows || []).forEach((f) => { if (f.start === id) S.flowOrigin[f.id] = st.length })
    if (st.length >= MAX_DEPTH) st.pop()
    st.push({ id, a: String(a || '') }); S.sheet = null; closeAdhoc(); navigated({ fresh: true })
    return true
  }
  K.back = (delta = 1) => {
    const st = stack(); if (!st.length) { K.emit('back-denied', K.cur()); return false }
    st.splice(Math.max(0, st.length - Math.max(1, delta))); S.sheet = null; closeAdhoc(); navigated({ fresh: true, restore: true })
    return true
  }
  K.replace = (id, a = '') => {
    const p = K.pages[id]; if (!p || p.type === 'tab') { console.error('replace 不能去标签栏页面：', id); return false }
    const st = stack(); if (st.length) st.pop()
    st.push({ id, a: String(a || '') }); S.sheet = null; closeAdhoc(); navigated({ fresh: true })
    return true
  }
  K.popTo = (n) => { S.stacks[S.tab] = stack().slice(0, Math.max(0, n)); S.sheet = null; closeAdhoc(); navigated({ fresh: true, restore: true }) }
  /* toTab 的栈语义：默认是微信 switchTab——弹掉所有二级页，各标签回到根页；这对应小程序（标签栏只有一级页，二级页隐藏标签栏）。
   * 侧栏菜单式的后台不是 switchTab：切换保持各菜单自己停在的二级页。kind 声明 keepTabStacks: true，或调用时传 {keep: true} 即可；
   * 保留模式下再点当前标签（栈里有二级页）回到该标签的根页，其他标签的栈不动。 */
  K.toTab = (t, o = {}) => {
    if (!K.tabs.some((x) => x.id === t)) { console.error('toTab: 标签不存在', t); return false }
    const keep = o.keep !== undefined ? !!o.keep : !!K.kindDef.keepTabStacks
    if (t === S.tab && !stack().length) { const sc = $('.pt-scroll'); if (sc) sc.scrollTo({ top: 0, behavior: 'smooth' }); return true }
    if (keep) { if (t === S.tab) S.stacks[t] = [] } else clearStacks()
    S.tab = t; S.sheet = null; closeAdhoc(); navigated({ fresh: true, restore: true })
    return true
  }
  K.jump = (id, a = '') => {
    const p = K.pages[id]; if (!p) return false
    if (p.type === 'sheet') { const base = p.base || tabRoot(tabOfPage(id)); K.jump(base, p.baseArg || ''); K.openSheet(id, a); return true }
    clearStacks(); S.flowOrigin = {}
    S.tab = tabOfPage(id); S.stacks[S.tab] = p.type === 'tab' ? [] : [{ id, a: String(a || '') }]
    ;(K.spec.flows || []).forEach((f) => { if (f.start === id) S.flowOrigin[f.id] = 0 })
    S.sheet = null; closeAdhoc(); navigated({ fresh: true })
    return true
  }
  K.done = (flowId) => {
    const f = (K.spec.flows || []).find((x) => x.id === flowId) || (K.spec.flows || []).find((x) => (x.steps || []).includes(K.cur().id))
    const origin = f && S.flowOrigin[f.id] != null ? S.flowOrigin[f.id] : 0
    if (f && f.done && f.done !== 'origin' && K.pages[f.done]) {
      S.sheet = null; closeAdhoc()
      return K.pages[f.done].type === 'tab' ? K.toTab(tabOfPage(f.done)) : K.go(f.done)
    }
    K.popTo(origin)
  }
  K.openSheet = (id, a = '') => { if (!K.pages[id]) return; S.sheet = { id, a: String(a || '') }; closeAdhoc(); K.emit('sheet', S.sheet); K.render() }
  K.closeSheet = () => { if (S.sheet) { S.sheet = null; K.emit('sheet', null); K.render() } else K.sheet.close() }

  /* ---------- 场景、角色、网络、减少动态、外观 ---------- */
  K.scene = (id) => S.scene[id]
  K.setScene = (id, v) => {
    if (id === 'view') { S.view = v; S.auto = false } else S.scene[id] = v
    K.emit('scene', { id, value: v }); K.render()
  }
  K.setRole = (r) => { S.role = r; K.emit('role', r); K.render({ fresh: true }) }
  K.setNet = (n) => { S.net = n; K.emit('net', n); S.view = 'ok'; K.render({ fresh: true }) }
  /* 三栏宽度与折叠（R6）：kind 可声明 layout: {left, right}（像素），外壳按它排；页头右侧有“左栏”“右栏”两个折叠按钮，折叠后舞台变宽 */
  K.setFold = (side, on) => { html.dataset['fold' + (side === 'left' ? 'Left' : 'Right')] = on ? '1' : '0'; $$('[data-fold]').forEach((b) => b.setAttribute('aria-pressed', html.dataset['fold' + (b.dataset.fold === 'left' ? 'Left' : 'Right')] === '1')); if (K.kindDef && K.kindDef.size) fit(); else if (dlg.open) placeClip() }
  K.setReduce = (on) => { S.reduce = !!on; html.dataset.reduce = on ? '1' : '0'; K.emit('reduce', S.reduce); renderLeft() }
  const mq = matchMedia('(prefers-color-scheme: dark)')
  /* 外观：先交给组件库的 setAppearance（给 <html> 设类与 data-theme；不记 localStorage），再把“跟随系统”算成具体的深或浅写回 data-theme，
   * 这样外壳和产品区用同一个开关：组件库的颜色令牌与外壳的 --sh-* 都跟着 html 上的 data-theme 换。 */
  function applyAppearance(mode) {
    const dark = mode === 'dark' || (mode === 'auto' && mq.matches)
    LIB.setAppearance(mode === 'auto' ? 'system' : mode, false)
    html.dataset.appearance = mode; html.dataset.theme = dark ? 'dark' : 'light'
  }
  mq.addEventListener('change', () => { if ((S.cfg.appearance || 'auto') === 'auto') applyAppearance('auto') })
  K.setAppearance = (m) => K.setCfg('appearance', m)

  K.reset = () => {
    Object.keys(K.data).forEach((k) => delete K.data[k]); Object.assign(K.data, clone(K.spec.data || {}))
    if (K.contentDef && K.contentDef.init) K.contentDef.init(K.data)
    S.stacks = {}; K.tabs.forEach((t) => (S.stacks[t.id] = [])); S.tab = (K.tabs[0] || {}).id; S.sheet = null; S.view = 'ok'; S.auto = false; S.flowOrigin = {}; S.sc = {}; S.hidden = {}
    S.scene = {}; (K.spec.scenes || []).forEach((s) => (S.scene[s.id] = s.default !== undefined ? s.default : s.options[0].v))
    S.role = (K.roles[0] || {}).id || ''
    closeAdhoc(); K.emit('reset'); K.render({ fresh: true })
  }

  /* ---------- 模块显示：按页面把正文里的模块（blocks 的一项）开关显隐，kind 的 render 读 K.moduleHidden ---------- */
  K.moduleHidden = (pageId, key) => !!(S.hidden[pageId] && S.hidden[pageId][key])
  K.setModule = (pageId, key, hidden) => {
    const m = (S.hidden[pageId] = S.hidden[pageId] || {})
    if (hidden) m[key] = true; else delete m[key]
    K.emit('module', { page: pageId, key, hidden: !!hidden }); K.render()
  }
  K.modules = (page) => (K.kindDef && K.kindDef.modules ? K.kindDef.modules(page || frontPage()) : [])

  /* ---------- 组件库：K.block 与覆盖 ---------- */
  const cssDone = new Set()
  const useCss = (b) => { if (cssDone.has(b.id) || !b.css) return; cssDone.add(b.id); const s = document.createElement('style'); s.dataset.cidCss = b.id; s.textContent = b.css; document.head.appendChild(s) }
  K.cidInfo = (cid) => { const b = blockMap.get(cid); return b ? { id: b.id, name: b.name, style: b.style, cat: b.cat } : null }
  const OV_KEYS = ['text', 'img', 'go', 'back', 'tab', 'sheet', 'act', 'toast', 'attrs', 'hide', 'class']
  K.ovOf = (it) => { const ov = {}; OV_KEYS.forEach((k) => { if (it[k] !== undefined) ov[k] = it[k] }); return Object.keys(ov).length ? ov : null }
  K.block = (cid, ov) => {
    const b = blockMap.get(cid)
    if (!b) return `<div class="pt-miss" data-cid="${esc(cid)}">缺少组件 ${esc(cid)}</div>`
    useCss(b); LIB.setIconStyle(S.cfg.iconStyle || LIB.iconStyle)
    const bg = b.bg && LIB.ASSETS.bg[b.bg] ? ` style="background-image:url(${LIB.ASSETS.bg[b.bg]})"` : ''
    return `<section class="pt-blk"${b.stage ? ` data-stage="${b.stage === 'dark' ? 'night' : b.stage}"` : ''}${bg}><div class="ixr" data-cid="${b.id}" data-id="${b.id}"${ov ? ` data-ov="${esc(JSON.stringify(ov))}"` : ''}>${b.html()}</div></section>`
  }
  const setText = (el, v) => {
    if (!el.children.length) { el.textContent = v; return }
    const w = document.createTreeWalker(el, NodeFilter.SHOW_TEXT)
    for (let n = w.nextNode(); n; n = w.nextNode()) if (n.nodeValue.trim()) { n.nodeValue = v; return }
    el.prepend(v)
  }
  const setImg = (el, v) => {
    let src = v
    if (typeof v === 'number') src = LIB.P(v)
    else if (typeof v === 'string' && v.startsWith('bg:')) src = LIB.ASSETS.bg[v.slice(3)] || v
    if (el.tagName === 'IMG') el.src = src; else { el.style.backgroundImage = `url(${src})`; el.style.backgroundSize = 'cover'; el.style.backgroundPosition = 'center' }
  }
  function applyOv(r) {
    if (!r.dataset.ov) return
    let ov; try { ov = JSON.parse(r.dataset.ov) } catch (e) { return }
    /* 选择器：CSS 选择器；@n 取第 n 个匹配（从 0 起），@* 取全部；@n 后面还可以接后代选择器，如 ".row@2 .name" = 第 3 个 .row 里的 .name */
    const pickIn = (scope, sel) => {
      const m = /^(.*?)@(\d+|\*)(?:\s+(.+))?$/.exec(sel)
      if (!m) return $$(sel, scope).slice(0, 1)
      const all = $$(m[1], scope), bases = m[2] === '*' ? all : all.slice(+m[2], +m[2] + 1)
      return m[3] ? bases.flatMap((x) => pickIn(x, m[3])) : bases
    }
    const pick = (sel) => pickIn(r, sel)
    const each = (key, fn) => { if (ov[key]) Object.entries(ov[key]).forEach(([sel, v]) => pick(sel).forEach((el) => fn(el, v))) }
    if (ov.text) Object.entries(ov.text).forEach(([sel, v]) => { const whole = sel.endsWith('!'); pick(whole ? sel.slice(0, -1) : sel).forEach((el) => (whole ? (el.textContent = K.tpl(v)) : setText(el, K.tpl(v)))) })
    each('img', setImg)
    const attr = (k) => (el, v) => { el.setAttribute(k, v); if (!/^(BUTTON|A|INPUT)$/.test(el.tagName) && !el.getAttribute('role')) { el.setAttribute('role', 'button'); if (!el.hasAttribute('tabindex')) el.tabIndex = 0 } }
    each('go', attr('data-pt-go')); each('back', attr('data-pt-back')); each('tab', attr('data-pt-tab')); each('sheet', attr('data-pt-sheet')); each('act', attr('data-pt-act')); each('toast', attr('data-pt-say'))
    each('attrs', (el, v) => Object.entries(v).forEach(([k, x]) => (x === null ? el.removeAttribute(k) : el.setAttribute(k, x))))
    each('class', (el, v) => el.classList.add(...String(v).split(/\s+/).filter(Boolean)))
    ;(ov.hide || []).forEach((sel) => pick(sel).forEach((el) => (el.hidden = true)))
  }
  /* 写入 DOM 之后统一做的事：组件交互、组件自带 js、覆盖、给跳转补 data-route */
  /* 整个文档只有一个 h1（外壳里的产品名）：运行时塞进来的 h1 元素（组件的 js 钩子、内容模块动态拼的 HTML）降成带 data-h1 属性的 h2，
   * 子节点原样搬过去，外观由 engine.css 的 h2[data-h1] 保持。生成器已经在源码里降过一遍，这里是兜底。 */
  function demoteH1(scope) {
    $$('h1', scope).forEach((h) => { const n = document.createElement('h2'); n.setAttribute('data-h1', ''); [...h.attributes].forEach((a) => n.setAttribute(a.name, a.value)); while (h.firstChild) n.appendChild(h.firstChild); h.replaceWith(n) })
  }
  function mountIn(scope) {
    demoteH1(scope)
    LIB.IX.init(scope)
    $$('.ixr[data-cid]', scope).forEach((r) => {
      const b = blockMap.get(r.dataset.cid)
      if (b && b.js) { try { b.js(r) } catch (e) { console.error(b.id, e) } }
      applyOv(r)
    })
    $$('[data-pt-go],[data-pt-tab]', scope).forEach((el) => { const v = el.dataset.ptGo || el.dataset.ptTab; if (v) el.setAttribute('data-route', '#/' + (el.dataset.ptTab ? tabRoot(el.dataset.ptTab) || v : v.replace(':', '/'))) })
  }
  K.mount = mountIn

  /* ---------- 渲染 ---------- */
  function viewCtx(c) {
    const p = c.page; let view = S.view
    if (view === 'ok') {
      if (S.net === 'offline' && !p.offline) view = 'fail-network'
      else if (p.roles && p.roles.length && !p.roles.includes(S.role)) view = 'denied'
    }
    return { view, cfg: S.cfg, scene: S.scene, role: S.role, roleDef: K.roles.find((r) => r.id === S.role) || null, net: S.net }
  }
  K.viewCtx = () => viewCtx(K.cur())
  /* 只重画一部分（R9）：kind 的 renderPart(part, frame, ctx) 自己替换那一块 DOM 并返回被替换的元素；引擎对它做 mountIn，
   * 并按 data-fk 属性恢复焦点与光标（列表的搜索框即输即查、表单输入这类不能丢焦点的场合）。 */
  const focusKey = () => { const a = document.activeElement; return a && a.dataset && a.dataset.fk ? { key: a.dataset.fk, s: a.selectionStart, e: a.selectionEnd } : null }
  const restoreFocus = (f) => { if (!f) return; const n = $(`[data-fk="${f.key}"]`); if (!n) return; n.focus({ preventScroll: true }); try { if (f.s != null) n.setSelectionRange(f.s, f.e) } catch (e) { /* 不是文本框 */ } }
  K.keepFocus = (fn) => { const f = focusKey(); fn(); restoreFocus(f) }
  function renderPart(part) {
    const c = K.cur(), ctx = viewCtx(c), f = focusKey()
    let els = K.kindDef.renderPart(part, c, ctx)
    els = els ? [].concat(els) : []
    els.forEach(mountIn)
    restoreFocus(f); renderRight(); K.emit('render', c)
  }
  K.render = (o = {}) => {
    if (!K.kindDef) return
    if (depth) {
      need = need || { fresh: false, restore: false, full: false, parts: [] }
      if (o.part && K.kindDef.renderPart) { if (!need.parts.includes(o.part)) need.parts.push(o.part) } else { need.full = true; need.fresh = need.fresh || !!o.fresh; need.restore = need.restore || !!o.restore }
      return
    }
    if (o.part && K.kindDef.renderPart) return renderPart(o.part)
    const kd = K.kindDef, scr = $(kd.screen)
    const sc = $('.pt-scroll', scr)
    if (sc && scr.dataset.key) S.sc[scr.dataset.key] = sc.scrollTop
    const c = K.cur(), key = `${S.tab}|${c.id}|${c.a}`, ctx = viewCtx(c)
    scr.dataset.key = key; scr.dataset.page = c.id
    ;['3d', 'real', 'flat', 'line'].forEach((s) => scr.classList.toggle('ics-' + s, s === LIB.iconStyle))
    try { scr.innerHTML = kd.render(c, ctx) } catch (e) { console.error('渲染失败', c.id, e); scr.innerHTML = `<div class="pt-miss">页面「${esc(c.id)}」渲染出错：${esc(e.message)}</div>` }
    mountIn(scr)
    try { if (kd.mounted) kd.mounted(scr, c, ctx) } catch (e) { console.error(e) }
    const sc2 = $('.pt-scroll', scr)
    if (sc2) sc2.scrollTop = o.fresh && !o.restore ? 0 : S.sc[key] || 0
    syncSheet()
    renderLeft(); renderRight(); syncHash()
    K.emit('render', c)
  }

  /* ---------- 弹层：原生 dialog + showModal，焦点陷阱 ---------- */
  const mkDialog = (id) => {
    const d = document.createElement('dialog')
    d.id = id; d.className = 'pt-dlg kit'; d.setAttribute('role', 'dialog'); d.setAttribute('aria-modal', 'true'); d.setAttribute('aria-labelledby', id + 'T')
    return d
  }
  const dlg = mkDialog('ptDlg')
  let dlg2 = null // 弹层之上再叠的确认框（嵌套），只在已有弹层时才建
  let adhoc = null, opener = null, fitScale = 1, shown = null
  const FOCUSABLE = 'a[href],button:not([disabled]),input:not([disabled]),select:not([disabled]),textarea:not([disabled]),[tabindex]:not([tabindex="-1"])'
  const focusablesIn = (d) => $$(FOCUSABLE, d).filter((e) => !e.closest('[hidden]') && e.offsetParent !== null)
  const focusables = () => focusablesIn(dlg)
  /* 对话框外壳。maskClose === false：遮罩不带 data-pt-close，点遮罩或面板外都不关闭（表单与确认面板用，免得丢已填内容） */
  function sheetShell(c, id = 'ptDlg') {
    const center = c.layout === 'center', nest = id !== 'ptDlg'
    const cid = c.cid ? ` data-cid="${esc(c.cid)}"` : ''
    const mask = c.maskClose === false || nest ? '<div class="pt-mask"></div>' : '<div class="pt-mask" data-pt-close></div>'
    const x = nest ? 'data-confirm-cancel' : 'data-pt-close'
    return `<div class="pt-clip kit"${nest ? '' : ' id="ptClip"'}>${mask}<section class="pt-sheet pt-surface${center ? ' center' : ''}"${cid}><header><h3 id="${id}T">${esc(c.title || '')}</h3><button type="button" class="x" ${x} aria-label="关闭">${svg('close')}</button></header><div class="pt-sbody"></div><div class="pt-sfoot"></div></section><div class="pt-toasts"></div></div>`
  }
  function placeClip(d = dlg) {
    const clip = $('.pt-clip', d); if (!clip) return
    const el = $(K.kindDef.clip); const r = el.getBoundingClientRect(), k = fitScale
    Object.assign(clip.style, { left: r.left + 'px', top: r.top + 'px', width: r.width / k + 'px', height: r.height / k + 'px', transform: k === 1 ? '' : `scale(${k})`, borderRadius: getComputedStyle(el).borderRadius })
  }
  /* R12：dialog 元素自己也带 data-cid（审计把 dialog 当控件，要求它落在带编号的组件里） */
  const tagCid = (d, cid) => { if (cid) d.setAttribute('data-cid', cid); else d.removeAttribute('data-cid') }
  function fillSheet(c) {
    const body = $('.pt-sbody', dlg), foot = $('.pt-sfoot', dlg), st = body.scrollTop
    $('#ptDlgT', dlg).textContent = c.title || ''
    body.innerHTML = c.body || ''; foot.innerHTML = c.foot || ''
    mountIn(dlg); body.scrollTop = st
  }
  function openDialog(c) {
    const lay = c.layout === 'center' ? 'center' : 'bottom'
    const sig = lay + (c.cid || '') + (c.maskClose === false ? 'stay' : '')
    closingSeq++; dlg.classList.remove('closing') // 正在退出时又要打开：取消退出
    if (dlg.open && dlg.dataset.layout !== sig) { dlg.close() }
    shown = c
    if (!dlg.open) {
      if (!opener || !document.contains(opener)) opener = document.activeElement
      dlg.dataset.layout = sig; dlg.innerHTML = sheetShell(c); tagCid(dlg, c.cid); placeClip(); dlg.showModal(); fillSheet(c)
      const f = focusables().filter((e) => !e.classList.contains('x'))[0] || focusables()[0]; if (f) f.focus()
    } else {
      const active = document.activeElement, idx = focusables().indexOf(active)
      tagCid(dlg, c.cid); fillSheet(c)
      if (idx >= 0 && (!document.activeElement || !dlg.contains(document.activeElement))) { const fs = focusables(); (fs[Math.min(idx, fs.length - 1)] || fs[0]).focus() }
    }
  }
  function sheetContent() {
    if (adhoc) return adhoc
    if (!S.sheet) return null
    const p = K.pages[S.sheet.id]; if (!p) return null
    const cd = K.contentDef
    const c = cd && cd.sheets && cd.sheets[S.sheet.id] ? cd.sheets[S.sheet.id](S.sheet.a, viewCtx(K.cur())) : K.kindDef.sheet(p, S.sheet.a, viewCtx(K.cur()))
    return c && Object.assign({ title: p.title || p.name, maskClose: p.maskClose }, c)
  }
  /* 关闭：先加 .closing 放 150ms 的退出动画（进入 200ms 的 75%），再真正 close；减少动态时直接关 */
  let closingSeq = 0
  function closeDialog() {
    if (!dlg.open) return
    if (S.reduce) { dlg.close(); return }
    dlg.classList.add('closing')
    const k = ++closingSeq
    setTimeout(() => { if (k === closingSeq) { dlg.classList.remove('closing'); if (dlg.open) dlg.close() } }, 150)
  }
  function syncSheet() {
    const c = sheetContent()
    if (c) openDialog(c); else closeDialog()
  }
  function closeAdhoc() { if (adhoc) { const a = adhoc; adhoc = null; if (a.onClose) a.onClose() } }
  K.sheet = {
    open(o) { adhoc = o; S.sheet = null; openDialog(o) },
    close() { adhoc = null; closeDialog() },
    get isOpen() { return dlg.open && !dlg.classList.contains('closing') },
  }
  /* R4：用户发起的关闭（Esc、右上角 ×、点遮罩、点面板外、内容里的 data-pt-close 按钮）先问 onBeforeClose(reason)；返回 false 就不关。
   * reason 取 esc / click / outside。程序里的 K.closeSheet() 与导航（go、back、toTab……）不问，直接关。 */
  K.requestClose = (reason = 'click') => {
    if (shown && shown.onBeforeClose && shown.onBeforeClose(reason) === false) return false
    K.closeSheet(); return true
  }

  /* ---------- 确认框：K.confirm；R8 带字段；R4 已有弹层时叠一层（第二个 <dialog>） ---------- */
  const fieldsHTML = (fields) => `<div class="pt-fields">${fields.map((f) => {
    const id = 'ptf-' + f.name, req = f.required ? '<i aria-hidden="true">*</i>' : ''
    let ctl
    if (f.type === 'textarea') ctl = `<textarea id="${id}" name="${esc(f.name)}" rows="${f.rows || 3}" placeholder="${esc(f.placeholder || '')}" data-fk="${id}"></textarea>`
    else if (f.type === 'select') ctl = `<select id="${id}" name="${esc(f.name)}">${(f.options || []).map((o) => `<option value="${esc(o.v !== undefined ? o.v : o)}">${esc(o.label || o.v || o)}</option>`).join('')}</select>`
    else ctl = `<input id="${id}" name="${esc(f.name)}" type="${f.type === 'password' ? 'password' : 'text'}" placeholder="${esc(f.placeholder || '')}" autocomplete="off" data-fk="${id}">`
    return `<label class="pt-field" for="${id}"><span>${esc(f.label || f.name)}${req}</span>${ctl}<em class="pt-ferr" role="alert"></em>${f.hint ? `<small>${esc(f.hint)}</small>` : ''}</label>`
  }).join('')}</div>`
  function checkFields(root, fields) {
    const values = {}; let first = null
    fields.forEach((f) => {
      const el = $(`[name="${f.name}"]`, root), v = el ? String(el.value).trim() : '', err = el.closest('.pt-field').querySelector('.pt-ferr')
      const bad = (f.required && !v) || (v && f.pattern && !new RegExp(f.pattern).test(v)) || (v && f.min != null && v.length < f.min)
      el.setAttribute('aria-invalid', bad ? 'true' : 'false'); err.textContent = bad ? (f.msg || (f.required && !v ? '请填写' + (f.label || '') : '格式不对')) : ''
      if (bad && !first) first = el
      values[f.name] = v
    })
    if (first) first.focus()
    return { ok: !first, values }
  }
  const confirmBody = (o) => `${o.text ? `<p class="pt-confirm">${esc(o.text)}</p>` : ''}${o.fields ? fieldsHTML(o.fields) : ''}`
  const confirmFoot = (o) => `<div class="pt-confirm-row"><button type="button" ${o.nested ? 'data-confirm-cancel' : 'data-pt-close'}>${esc(o.cancel || '取消')}</button><button type="button" class="ok${o.danger ? ' danger' : ''}" data-confirm-ok>${esc(o.ok || '确定')}</button></div>`
  /* K.confirm({title, text, ok, cancel, danger, stack, fields: [{name, label, type: text|password|textarea|select, required, placeholder, hint, pattern, min, msg, options}], onOk(values)})
   * 带 fields 时，必填或格式不通过不关闭，错误写在字段下面；通过后先关闭再回调 onOk(values) */
  K.confirm = (o) => {
    if (o.stack && dlg.open && !dlg.classList.contains('closing')) return confirmNested(o) // stack: true 且已有弹层：叠在它上面；不写就替换当前弹层（旧行为）
    K.sheet.open({ layout: 'center', title: o.title, cid: (K.kindDef.confirmCid || ''), body: confirmBody(o), foot: confirmFoot(o), maskClose: o.maskClose, onOk: o.onOk, fields: o.fields })
  }
  const trap = (d) => (e) => {
    if (e.key !== 'Tab') return
    const fs = focusablesIn(d); if (!fs.length) { e.preventDefault(); return }
    const first = fs[0], last = fs[fs.length - 1], a = document.activeElement
    if (e.shiftKey && (a === first || !d.contains(a))) { e.preventDefault(); last.focus() }
    else if (!e.shiftKey && (a === last || !d.contains(a))) { e.preventDefault(); first.focus() }
  }
  let nested = null, nestedOpener = null
  function closeNested() {
    if (!dlg2 || !dlg2.open) return
    if (S.reduce) { dlg2.close(); return }
    dlg2.classList.add('closing')
    setTimeout(() => { dlg2.classList.remove('closing'); if (dlg2.open) dlg2.close() }, 150)
  }
  function confirmNested(o) {
    if (!dlg2) {
      dlg2 = mkDialog('ptDlg2'); document.body.appendChild(dlg2)
      dlg2.addEventListener('cancel', (e) => { e.preventDefault(); closeNested() })
      dlg2.addEventListener('close', () => { if (nestedOpener && document.contains(nestedOpener)) { try { nestedOpener.focus() } catch (e) { /* 忽略 */ } } nested = null })
      dlg2.addEventListener('keydown', trap(dlg2))
      dlg2.addEventListener('click', (e) => {
        const stay = nested && nested.maskClose === false
        if (e.target === dlg2) { if (!stay) closeNested(); return }
        if (e.target.closest('[data-confirm-ok]')) {
          let values
          if (nested && nested.fields) { const r = checkFields(dlg2, nested.fields); if (!r.ok) return; values = r.values }
          const a = nested; closeNested(); if (a && a.onOk) a.onOk(values)
          return
        }
        if (e.target.closest('[data-confirm-cancel]')) { closeNested(); return }
        if (e.target.closest('.pt-mask') && !stay) closeNested()
      })
    }
    nested = o; nestedOpener = document.activeElement
    LIB.applyTheme(dlg2, S.cfg.theme || 'rose'); tagCid(dlg2, K.kindDef.confirmCid || '')
    dlg2.classList.remove('closing')
    const c = { layout: 'center', title: o.title, cid: K.kindDef.confirmCid || '', maskClose: o.maskClose }
    if (dlg2.open) dlg2.close()
    dlg2.innerHTML = sheetShell(c, 'ptDlg2'); placeClip(dlg2)
    $('.pt-sbody', dlg2).innerHTML = confirmBody(o); $('.pt-sfoot', dlg2).innerHTML = confirmFoot(Object.assign({}, o, { nested: true }))
    dlg2.showModal()
    const f = focusablesIn(dlg2).filter((e) => !e.classList.contains('x'))[0] || focusablesIn(dlg2)[0]; if (f) f.focus()
  }
  dlg.addEventListener('cancel', (e) => { e.preventDefault(); K.requestClose('esc') })
  dlg.addEventListener('close', () => {
    if (dlg.open) return // 关了又马上重新打开（换了一层内容）：不动状态
    if (S.sheet) { S.sheet = null; K.emit('sheet', null) }
    adhoc = null; shown = null
    if (opener && document.contains(opener)) { try { opener.focus() } catch (e) { /* 忽略 */ } }
    opener = null
    K.render()
  })
  dlg.addEventListener('click', (e) => {
    if (e.target === dlg) { if (!(shown && shown.maskClose === false)) K.requestClose('outside'); return }
    const ok = e.target.closest('[data-confirm-ok]')
    if (ok) {
      const a = adhoc; let values
      if (a && a.fields) { const r = checkFields(dlg, a.fields); if (!r.ok) return; values = r.values }
      K.sheet.close(); if (a && a.onOk) a.onOk(values)
    }
  })
  dlg.addEventListener('keydown', trap(dlg))

  /* ---------- 轻提示 ---------- */
  K.toast = (msg, tone = 'ok') => {
    if (depth) { toastQ.push([msg, tone]); return }
    const top = dlg2 && dlg2.open ? dlg2 : dlg.open ? dlg : null
    const box = top ? $('.pt-clip .pt-toasts', top) : $(K.kindDef.toasts || '#ptToasts')
    if (!box) return
    const t = document.createElement('div'); t.className = 'pt-toast'; t.dataset.tone = tone; t.setAttribute('role', 'status')
    t.innerHTML = `${svg(tone === 'ok' ? 'check' : tone === 'danger' ? 'closec' : 'info')}<span></span>`; $('span', t).textContent = msg
    box.appendChild(t); setTimeout(() => t.remove(), 1800)
  }

  /* ---------- 动作：命名动作与声明式步骤 ---------- */
  const splitArg = (v) => { const s = String(v); const i = s.indexOf(':'); return i < 0 ? [s, ''] : [s.slice(0, i), s.slice(i + 1)] }
  function validate(rules) {
    const scope = dlg.open ? dlg : $(K.kindDef.clip) // 嵌套确认框的校验由 K.confirm 的 fields 自己做
    for (const r of rules) {
      for (const el of $$(r.sel, scope)) {
        const val = String(el.value !== undefined ? el.value : el.textContent).trim()
        const bad = (r.required && !val) || (val && r.pattern && !new RegExp(r.pattern).test(val)) || (r.min != null && val.length < r.min)
        el.setAttribute('aria-invalid', bad ? 'true' : 'false')
        if (bad) { K.toast(r.msg || '请检查填写内容', 'warn'); if (el.focus) el.focus(); return false }
      }
    }
    return true
  }
  const STEP = {
    go: (v) => K.go(...splitArg(v)), replace: (v) => K.replace(...splitArg(v)), tab: (v) => K.toTab(v), sheet: (v) => K.openSheet(...splitArg(v)),
    back: (v) => K.back(v === true ? 1 : +v || 1), popTo: (v) => K.popTo(+v), close: () => K.closeSheet(), done: (v) => K.done(v === true ? undefined : v),
    toast: (v) => (typeof v === 'string' ? K.toast(K.tpl(v)) : K.toast(K.tpl(v.text), v.tone || 'ok')),
    set: (v) => K.set(v.path, v.value), inc: (v) => K.inc(v.path, v.by === undefined ? 1 : v.by, v),
    push: (v) => { const a = K.get(v.path) || []; a.unshift(clone(v.value)); K.set(v.path, a) },
    role: (v) => K.setRole(v), scene: (v) => K.setScene(v.id, v.value),
    branch: (v, ctx) => { const key = v.scene != null ? K.scene(v.scene) : String(K.get(v.path)); const arm = (v.cases || {})[key] || v.default; return arm ? K.run(arm, ctx) : true },
    validate: (v) => validate(v), net: () => { if (S.net === 'offline') { K.toast('网络不可用，请检查网络后重试', 'warn'); return false } return true },
    act: (v) => K.act(v), stop: () => false,
  }
  K.run = (steps, ctx = {}) => {
    let ok = true
    K.batch(() => { for (const st of steps || []) { const k = Object.keys(st)[0]; if (!STEP[k]) { console.warn('未知步骤', k); continue } if (STEP[k](st[k], ctx) === false) { ok = false; break } } })
    return ok
  }
  const builtin = {
    retry() { if (S.net === 'offline') { K.toast('网络仍不可用', 'warn'); return } S.view = 'ok'; S.auto = false; K.render() },
  }
  K.act = (name, ...args) => {
    const cd = K.contentDef
    return K.batch(() => {
      if (cd && cd.acts && cd.acts[name]) return cd.acts[name](...args)
      const steps = (K.spec.actions || {})[name]
      if (steps) return K.run(steps, { args })
      if (builtin[name]) return builtin[name](...args)
      console.warn('未定义的动作', name)
    })
  }

  /* ---------- 配置：组、K.panel、应用 ---------- */
  const mixc = LIB.mixc
  const BUILTIN = {
    appearance: () => ({ id: 'appearance', title: '外观', type: 'seg', options: [{ v: 'auto', label: '跟随系统' }, { v: 'light', label: '浅色' }, { v: 'dark', label: '深色' }], default: 'auto', render: false, apply: applyAppearance }),
    theme: () => ({ id: 'theme', title: '主题色', type: 'swatch', options: LIB.THEMES.filter((t) => !(K.spec.theme && K.spec.theme.themes) || K.spec.theme.themes.includes(t.id)).map((t) => ({ v: t.id, label: t.name, swatch: `linear-gradient(145deg,${mixc(t.p, '#FFFFFF', 0.8)},${t.p})` })), default: 'rose', apply: (v) => { LIB.applyTheme(root(), v); LIB.applyTheme(dlg, v); if (dlg2) LIB.applyTheme(dlg2, v) } }),
    iconStyle: () => ({ id: 'iconStyle', title: '图标风格', type: 'cards', cols: 2, default: '3d', options: LIB.ICON_STYLES.map(([v, label]) => ({ v, label, thumb: ['giftbox', 'coupon', 'cart'].map((n) => (v === 'line' ? LIB.lineSvg(n, '', '') : `<img alt="" src="${LIB.ASSETS.icons[v][n]}">`)).join('') })), apply: (v) => LIB.setIconStyle(v) }),
    iconTile: () => ({ id: 'iconTile', title: '图标底', type: 'seg', default: 'sq', options: [{ v: 'sq', label: '圆角方块' }, { v: 'ci', label: '圆形' }, { v: 'no', label: '无底' }], note: '图标自己的颜色不变，底色取主题色的浅色。' }),
  }
  function buildGroups(spec, kd) {
    const own = Object.fromEntries((kd.config || []).map((g) => [g.id, g]))
    const extra = ((spec.config && spec.config.extra) || []).map((g) => Object.assign({}, g))
    const ids = (spec.config && spec.config.groups) || kd.defaultGroups || ['appearance', 'theme']
    return ids.map((id) => own[id] || BUILTIN[id]?.() || extra.find((g) => g.id === id)).filter(Boolean).concat(extra.filter((g) => !ids.includes(g.id)))
  }
  const reflect = (g, v) => {
    root().setAttribute('data-cfg-' + g.id, v)
    if (g.var) { const o = (typeof g.options === 'function' ? g.options(S.cfg) : g.options || []).find((x) => x.v === v); root().style.setProperty(g.var, o && o.css ? o.css : v) }
  }
  K.setCfg = (id, v) => {
    const g = K.groups.find((x) => x.id === id); if (!g) return
    S.cfg[id] = v; reflect(g, v); if (g.apply) g.apply(v, S.cfg)
    if (K.kindDef.onConfig) K.kindDef.onConfig(id, v)
    K.emit('config', { id, value: v })
    if (g.render !== false) K.render(); else renderLeft()
  }
  const groupHTML = (g, cfg) => {
    const opts = typeof g.options === 'function' ? g.options(cfg) : g.options || [], cur = cfg[g.id]
    const btn = (cls, o, inner) => `<button type="button" class="${cls}" data-shell data-g="${esc(g.id)}" data-v="${esc(o.v)}" aria-pressed="${cur === o.v}">${inner}</button>`
    let body = ''
    if (g.type === 'swatch') body = `<div class="pt-sw">${opts.map((o) => btn('pt-swb', o, `<i style="background:${o.swatch}"></i>${esc(o.label)}`)).join('')}</div>`
    else if (g.type === 'seg') body = `<div class="pt-segb">${opts.map((o) => btn('', o, esc(o.label))).join('')}</div>`
    else if (g.type === 'cards') body = `<div class="pt-opts c${g.cols || 2}">${opts.map((o) => btn('pt-opt', o, `<span class="th"${o.bg ? ` style="background-image:url(${o.bg})"` : o.swatch ? ` style="background:${o.swatch}"` : ''}>${o.thumb || ''}</span>${esc(o.label)}`)).join('')}</div>`
    else if (g.type === 'switch') body = `<button type="button" class="pt-switch" data-shell data-g="${esc(g.id)}" data-v="toggle" role="switch" aria-checked="${!!cur}"><span>${esc(g.label || g.title)}</span><i class="tg"></i></button>`
    else if (g.type === 'select') body = `<select class="pt-select" data-shell data-g="${esc(g.id)}" aria-label="${esc(g.title)}">${opts.map((o) => `<option value="${esc(o.v)}"${cur === o.v ? ' selected' : ''}>${esc(o.label)}</option>`).join('')}</select>`
    return `<h3>${esc(g.title)}</h3>${body}${g.note ? `<p class="pt-note">${esc(g.note)}</p>` : ''}`
  }
  /* K.panel：配置面板的构造函数。groups 是组声明，cfg 是值对象（会被直接改写），onChange(id, value, cfg) 在值变化后调用 */
  K.panel = function panel(opts) {
    const { mount, groups, cfg } = opts
    const draw = () => { mount.innerHTML = groups.filter((g) => !g.when || g.when(cfg)).map((g) => groupHTML(g, cfg)).join('') }
    mount.addEventListener('click', (e) => {
      const b = e.target.closest('[data-g][data-v]'); if (!b) return
      const g = groups.find((x) => x.id === b.dataset.g); if (!g) return
      const v = b.dataset.v === 'toggle' ? !cfg[g.id] : b.dataset.v
      if (opts.onChange) opts.onChange(g.id, v, cfg)
    })
    mount.addEventListener('change', (e) => { const s = e.target.closest('select[data-g]'); if (s && opts.onChange) opts.onChange(s.dataset.g, s.value, cfg) })
    draw()
    return { update: draw }
  }

  /* ---------- 左栏：页面 / 外观 / 场景 ---------- */
  const VIEWS = [['ok', '正常', 'ok'], ['loading', '加载中', 'loading'], ['empty', '空', 'empty'], ['fail-network', '失败：网络不可用', 'fail'], ['fail-timeout', '失败：请求超时', 'fail'], ['fail-server', '失败：服务繁忙', 'fail'], ['fail-expired', '失败：数据已失效', 'fail'], ['denied', '无权限', 'denied'], ['disabled', '禁用', 'disabled']]
  const NETS = [['online', '正常'], ['slow', '弱网'], ['offline', '断网']]
  const chip = (attr, val, label, on, kind = '') => `<button type="button" class="pt-chip" data-shell ${attr}="${esc(val)}" data-kind="${kind}" aria-pressed="${on}">${esc(label)}</button>`
  function dirGroups() {
    if (K.spec.directory) return K.spec.directory.map((g) => [g.group, g.pages])
    const order = { tab: 0, sub: 1, result: 2, sheet: 3 }, by = {}
    K.spec.pages.forEach((p) => { const k = p.tab || (p.type === 'tab' ? tabOfPage(p.id) : '_'); (by[k] = by[k] || []).push(p) })
    const out = K.tabs.filter((t) => by[t.id]).map((t) => [t.name, by[t.id].sort((a, b) => (order[a.type] ?? 9) - (order[b.type] ?? 9)).map((p) => p.id)])
    if (by._) out.push(['其他', by._.map((p) => p.id)])
    return out
  }
  function scenesHTML() {
    const fp = frontPage(), spec = K.spec
    const rel = (s) => (s.pages || []).includes(fp.id) || (fp.scenes || []).includes(s.id)
    const sc = (spec.scenes || []).slice().sort((a, b) => rel(b) - rel(a))
    let out = `<h3>本页状态<small>作用于当前页，换页复位</small></h3><div class="pt-chips">${VIEWS.map(([v, l, k]) => chip('data-scn', 'view:' + v, l, S.view === v, k)).join('')}</div>`
    if (sc.length) out += `<h3>业务场景</h3>` + sc.map((s) => `<div class="pt-scn"><b>${esc(s.label)}${rel(s) ? '<em>本页</em>' : ''}</b><div class="pt-chips">${s.options.map((o) => chip('data-scn', s.id + ':' + o.v, o.label, S.scene[s.id] === o.v, o.kind || 'ok')).join('')}</div></div>`).join('')
    const mods = K.modules(fp)
    if (mods.length) out += `<h3>模块显示<small>${esc(fp.name || fp.id)}：关掉就不画这个模块</small></h3><div class="pt-mods">${mods.map((m) => `<button type="button" class="pt-switch" data-shell data-mod="${esc(m.key)}" role="switch" aria-checked="${!K.moduleHidden(fp.id, m.key)}"><span>${esc(m.label)}</span><i class="tg"></i></button>`).join('')}</div>`
    const flows = spec.flows || []
    if (flows.length) out += `<h3>流程直达</h3><div class="pt-flows">${flows.map((f) => `<button type="button" data-shell data-flow="${esc(f.id)}">${esc(f.name)}<span>${esc((f.steps || []).map((x) => (K.pages[x] || {}).name || x).join(' › '))}</span></button>`).join('')}</div>`
    out += `<h3>全局</h3><div class="pt-scn"><b>网络</b><div class="pt-chips">${NETS.map(([v, l]) => chip('data-net', v, l, S.net === v)).join('')}</div></div>`
    out += `<button type="button" class="pt-switch" data-shell data-reduce role="switch" aria-checked="${S.reduce}"><span>减少动态</span><i class="tg"></i></button>`
    if (K.roles.length) out += `<div class="pt-scn"><b>角色</b><div class="pt-chips">${K.roles.map((r) => chip('data-role', r.id, r.name, S.role === r.id)).join('')}</div></div>`
    out += `<button type="button" class="pt-btn" data-shell data-reset>重置演示数据</button><p class="pt-note">重置会还原演示数据、页面栈、场景和角色，配置面板里的选择不变。</p>`
    return out
  }
  const keyOf = (el) => Object.entries(el.dataset).map(([k, v]) => k + '=' + v).join('|')
  function keepFocus(panel, fn) {
    const a = document.activeElement, k = a && panel.contains(a) ? keyOf(a) : null, top = panel.scrollTop
    fn()
    panel.scrollTop = top
    if (k) { const n = $$('[data-shell]', panel).find((e) => keyOf(e) === k && e.matches('button,select')); if (n) n.focus({ preventScroll: true }) }
  }
  function renderLeft() {
    const el = $('#ptLeft'); if (!el) return
    keepFocus(el, () => {
      const tabs = [['pages', '页面'], ['look', '外观'], ['scene', '场景']]
      const c = frontPage()
      let body = ''
      if (S.lt === 'pages') {
        const item = (ref) => { const [id, a] = splitArg(ref), pg = K.pages[id]; if (!pg) return ''; const on = c.id === id && (!a || (S.sheet ? S.sheet.a : K.cur().a) === a); return `<button type="button" data-shell data-jump="${esc(ref)}"${on ? ' aria-current="page"' : ''}><span>${esc(pg.name + (a ? ' · ' + a : ''))}</span><em>${esc(typeLabel(pg.type))}</em></button>` }
        body = dirGroups().map(([g, ids]) => `<h3>${esc(g)}</h3><div class="pt-dir">${ids.map(item).join('')}</div>`).join('')
      } else if (S.lt === 'look') body = '<div id="ptCfg"></div>'
      else body = scenesHTML()
      el.innerHTML = `<div class="pt-seg" role="tablist">${tabs.map(([k, n]) => `<button type="button" role="tab" data-shell data-lt="${k}" aria-selected="${S.lt === k}">${n}</button>`).join('')}</div>${body}`
      if (S.lt === 'look') K.panel({ mount: $('#ptCfg', el), groups: K.groups, cfg: S.cfg, onChange: (id, v) => K.setCfg(id, v) })
    })
  }

  /* ---------- 右栏：本页逻辑 / 业务规则 / 状态流转 ---------- */
  const ul = (arr) => (arr && arr.length ? `<ul class="pt-list">${arr.map((x) => `<li>${esc(x)}</li>`).join('')}</ul>` : '')
  const refRow = (label, v) => {
    if (v == null || v === '' || (Array.isArray(v) && !v.length)) return ''
    const o = typeof v === 'object' && !Array.isArray(v) ? v : { text: v }
    const to = o.to && K.pages[o.to] ? ` <button type="button" class="pt-link" data-shell data-jump="${esc(o.to)}">${esc(K.pages[o.to].name)}</button>` : ''
    return `<div class="pt-kv"><b>${label}</b><span>${esc(o.text || '')}${to}</span></div>`
  }
  function logicHTML() {
    const c = K.cur(), p = frontPage(), L = p.logic || {}, spec = K.spec
    const flows = (spec.flows || []).filter((f) => (f.steps || []).includes(p.id))
    const flowbar = flows.map((f) => `<div class="pt-flowbar" title="${esc(f.name)}">${(f.steps || []).map((s) => `<span${s === p.id ? ' class="on"' : ''}>${esc((K.pages[s] || {}).name || s)}</span>`).join('<i>›</i>')}</div>`).join('')
    const tabName = (K.tabs.find((t) => t.id === (p.tab || c.tab)) || {}).name
    const cids = [...new Set($$('[data-cid]', $(K.kindDef.clip)).concat($$('[data-cid]', dlg)).map((e) => e.dataset.cid))]
    const acts = (L.actions || []).length ? `<h3>动作</h3><table class="pt-tbl"><thead><tr><th>编号</th><th>按钮</th><th>触发或禁用条件</th><th>结果</th></tr></thead><tbody>${L.actions.map((a) => `<tr><td>${esc(a.id || '')}</td><td>${esc(a.label || '')}</td><td class="l">${esc(a.when || '')}</td><td class="l">${esc(a.result || '')}</td></tr>`).join('')}</tbody></table>` : ''
    return `${flowbar}<h2 class="pt-title">${esc(p.name || p.id)}<em>${esc(typeLabel(p.type))}</em></h2>
      ${tabName ? refRow('所属', tabName) : ''}${refRow('来源', L.from)}${refRow('返回', L.back)}${refRow('完成后', L.done)}${refRow('主操作', L.primary)}
      ${(L.rules || []).length ? '<h3>业务规则</h3>' + ul(L.rules) : ''}${(L.states || []).length ? '<h3>状态</h3>' + ul(L.states) : ''}${(L.backend || []).length ? '<h3>后台维护</h3>' + ul(L.backend) : ''}${acts}${(L.data || []).length ? '<h3>数据</h3>' + ul(L.data) : ''}
      ${cids.length ? `<h3>本页组件</h3><div class="pt-cids">${cids.map((id) => { const i = K.cidInfo(id); return `<span title="${esc(i ? i.style : '')}">${esc(id)}${i ? ' ' + esc(i.name) : ''}</span>` }).join('')}</div>` : ''}`
  }
  function renderRight() {
    const el = $('#ptRight'); if (!el) return
    keepFocus(el, () => {
      const tabs = [['logic', '本页逻辑'], ['rules', '业务规则'], ['status', '状态流转']]
      let body
      if (S.rt === 'logic') body = logicHTML()
      else if (S.rt === 'rules') body = (K.spec.rules || []).map((g) => `<h3>${esc(g.title)}</h3>${ul(g.items)}`).join('') || '<p class="pt-note">规格里没有写业务规则。</p>'
      else body = (K.spec.statuses || []).length ? `<h3>状态机</h3><div class="pt-sm">${K.spec.statuses.map((s) => `<div class="pt-smr"><b data-tone="${esc(s.tone || 'mute')}">${esc(s.name)}</b><div>${s.trigger ? `<p><u>触发</u>${esc(s.trigger)}</p>` : ''}${s.ops ? `<p><u>可做</u>${esc(s.ops)}</p>` : ''}${s.to ? `<p><u>去向</u>${esc(s.to)}</p>` : ''}</div></div>`).join('')}</div>` : '<p class="pt-note">规格里没有写状态机。</p>'
      el.innerHTML = `<div class="pt-seg" role="tablist">${tabs.map(([k, n]) => `<button type="button" role="tab" data-shell data-rt="${k}" aria-selected="${S.rt === k}">${n}</button>`).join('')}</div>${body}`
    })
  }

  /* ---------- 路由 ---------- */
  function syncHash() {
    const c = K.cur(), f = S.sheet ? S.sheet : c
    const h = '#/' + f.id + (f.a ? ':' + f.a : '')
    if (location.hash !== h) { try { history.replaceState(null, '', h) } catch (e) { /* file:// 下个别环境不允许 */ } }
  }
  function routeFromHash() {
    const m = /^#\/([\w-]+)(?::(.*))?$/.exec(decodeURIComponent(location.hash)); if (!m || !K.pages[m[1]]) return false
    const f = S.sheet ? S.sheet : K.cur()
    if (f.id === m[1] && (f.a || '') === (m[2] || '')) return true
    K.jump(m[1], m[2] || ''); return true
  }
  addEventListener('hashchange', routeFromHash)

  /* ---------- 事件 ---------- */
  document.addEventListener('click', (e) => {
    const t = e.target.closest('[data-pt-say],[data-pt-act],[data-pt-close],[data-pt-back],[data-pt-done],[data-pt-go],[data-pt-tab],[data-pt-sheet],[data-pt-scene]')
    if (!t || t.closest('[data-shell]') || !K.kindDef) return
    if (!(t.closest(K.kindDef.clip) || t.closest('.pt-dlg'))) return
    // 只拦引擎自己置灰的（“禁用”状态写了 data-pt-reason）和原生 disabled；组件库自己的 aria-disabled 交给组件处理
    if (t.disabled || t.dataset.ptReason !== undefined) { K.toast(t.dataset.ptReason || '当前不可操作', 'warn'); return }
    const d = t.dataset
    K.batch(() => {
      if (d.ptSay !== undefined) K.toast(K.tpl(d.ptSay))
      if (d.ptAct !== undefined) { const [n, ...a] = d.ptAct.split(':'); K.act(n, ...a) }
      if (d.ptClose !== undefined) K.requestClose('click')
      if (d.ptBack !== undefined) K.back(+d.ptBack || 1)
      if (d.ptDone !== undefined) K.done(d.ptDone || undefined)
      if (d.ptGo !== undefined) { const [id, a] = splitArg(d.ptGo); K.go(id, a) }
      if (d.ptTab !== undefined) K.toTab(d.ptTab)
      if (d.ptSheet !== undefined) { const [id, a] = splitArg(d.ptSheet); opener = t; K.openSheet(id, a) }
      if (d.ptScene !== undefined) { const [id, v] = splitArg(d.ptScene); K.setScene(id, v) }
    })
  }, true) // 捕获阶段：先于组件自己的 js 钩子运行，读到的是点击前的状态（钩子会把按钮置为 disabled）
  document.addEventListener('keydown', (e) => {
    if ((e.key === 'Enter' || e.key === ' ') && e.target.matches && e.target.matches('[role=button][data-pt-go],[role=button][data-pt-act],[role=button][data-pt-tab],[role=button][data-pt-sheet],[role=button][data-pt-back],[role=button][data-pt-say]')) { e.preventDefault(); e.target.click() }
    if (e.key === 'Enter' && e.target.dataset && e.target.dataset.ptEnter) { const [n, ...a] = e.target.dataset.ptEnter.split(':'); K.act(n, ...a, e.target.value) }
  })
  document.addEventListener('input', (e) => { const t = e.target; if (t.dataset && t.dataset.ptInp) { const [n, ...a] = t.dataset.ptInp.split(':'); K.act(n, ...a, t.value) } })
  const panelClick = (e) => {
    const b = e.target.closest('button[data-shell]'); if (!b) return
    const d = b.dataset
    if (d.lt) { S.lt = d.lt; renderLeft() }
    else if (d.rt) { S.rt = d.rt; renderRight() }
    else if (d.jump !== undefined) { const [id, a] = splitArg(d.jump); K.jump(id, a) }
    else if (d.flow) { const f = K.spec.flows.find((x) => x.id === d.flow); if (f) { K.jump(f.start); S.flowOrigin[f.id] = 0 } }
    else if (d.scn) { const [id, v] = splitArg(d.scn); K.setScene(id, v) }
    else if (d.net) K.setNet(d.net)
    else if (d.role) K.setRole(d.role)
    else if (d.reduce !== undefined) K.setReduce(!S.reduce)
    else if (d.mod !== undefined) K.setModule(frontPage().id, d.mod, !K.moduleHidden(frontPage().id, d.mod))
    else if (d.reset !== undefined) K.reset()
  }
  $('#ptLeft').addEventListener('click', panelClick); $('#ptRight').addEventListener('click', panelClick)

  /* ---------- 舞台缩放 ---------- */
  let fitEl = null, fitIn = null, fitSize = null
  function fit() {
    if (!fitSize) return
    const narrow = innerWidth < 910
    let k = narrow ? Math.min(1, innerWidth / fitSize.w) : Math.min(1, (innerHeight - 76) / (fitSize.h + 12))
    k = Math.max(0.5, k); fitScale = k
    fitEl.style.width = fitSize.w * k + 'px'; fitEl.style.height = fitSize.h * k + 'px'
    fitIn.style.width = fitSize.w + 'px'; fitIn.style.height = fitSize.h + 'px'; fitIn.style.transform = k === 1 ? '' : `scale(${k})`
    if (dlg.open) placeClip()
    if (dlg2 && dlg2.open) placeClip(dlg2)
    if (K.kindDef.fit) K.kindDef.fit(k)
  }
  addEventListener('resize', fit)

  /* ---------- 注册与启动 ---------- */
  K.kind = (def) => { K.kindDef = def }
  K.content = (def) => {
    K.contentDef = def
    if (def.css) { const s = document.createElement('style'); s.textContent = def.css; document.head.appendChild(s) }
  }
  K.boot = (spec) => {
    const kd = K.kindDef
    if (!kd) throw new Error('没有注册 kind 运行时')
    K.spec = Object.freeze(spec)
    K.pages = Object.fromEntries(spec.pages.map((p) => [p.id, p]))
    K.tabs = flatTabs(spec[kd.tabsKey || 'tabbar']).map((t) => Object.assign({}, t))
    K.roles = spec.roles || []
    html.dataset.darkMode = 'tokens' // 深色一律用令牌（组件库的深色层 + 外壳 --sh-*），不再有滤镜近似
    document.body.appendChild(dlg)
    if (kd.layout) { const L = kd.layout(spec) || {}; const app = $('.pt-app'); if (L.left) app.style.setProperty('--sh-left', L.left + 'px'); if (L.right) app.style.setProperty('--sh-right', L.right + 'px') }
    $$('[data-fold]').forEach((b) => b.addEventListener('click', () => K.setFold(b.dataset.fold, html.dataset['fold' + (b.dataset.fold === 'left' ? 'Left' : 'Right')] !== '1')))
    K.groups = buildGroups(spec, kd)
    K.groups.forEach((g) => {
      const t = spec.theme || {}
      S.cfg[g.id] = g.id === 'theme' && t.id ? t.id : t[g.id] !== undefined ? t[g.id] : g.default
    })
    K.groups.forEach((g) => { reflect(g, S.cfg[g.id]); if (g.apply) g.apply(S.cfg[g.id], S.cfg) })
    applyAppearance(S.cfg.appearance || 'auto')
    S.reduce = matchMedia('(prefers-reduced-motion: reduce)').matches; html.dataset.reduce = S.reduce ? '1' : '0'
    document.title = spec.meta.title
    const size = kd.size ? kd.size(spec) : null
    if (size) {
      const stage = $('#ptStage'); fitSize = size
      fitEl = document.createElement('div'); fitEl.className = 'pt-fit'; fitIn = document.createElement('div'); fitIn.className = 'pt-stage-in'
      while (stage.firstChild) fitIn.appendChild(stage.firstChild)
      fitEl.appendChild(fitIn); stage.appendChild(fitEl); fit()
    }
    S.sc = {}
    Object.keys(K.data).forEach((k) => delete K.data[k]); Object.assign(K.data, clone(spec.data || {}))
    if (K.contentDef && K.contentDef.init) K.contentDef.init(K.data)
    S.stacks = {}; K.tabs.forEach((t) => (S.stacks[t.id] = [])); S.tab = (K.tabs[0] || {}).id
    S.scene = {}; (spec.scenes || []).forEach((s) => (S.scene[s.id] = s.default !== undefined ? s.default : s.options[0].v))
    S.role = (K.roles[0] || {}).id || ''
    if (!routeFromHash()) K.render({ fresh: true })
    window.__PT__ = K
  }
  return K
})()
