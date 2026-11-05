/* ===== 小程序 kind 运行时：手机框里一页怎么画 =====
 * 由生成器包进 (function (K, LIB) { … })(K, LIB)。机制与内容分开：这里没有任何行业内容。
 * 一页 = 状态栏 + （导航栏）+ 头部区 + 滚动区（blocks / custom）+ 底部区 + （标签栏）。 */
const { sv } = LIB
const esc = K.esc
const SB_ICONS = '<svg viewBox="0 0 18 12"><path d="M1 9h2v2H1zM5 6h2v5H5zM9 3.5h2V11H9zM13 1h2v10h-2z"/></svg><svg viewBox="0 0 17 12"><path d="M8.5 2.5c2 0 3.8.8 5.1 2l1-1.1A8.8 8.8 0 0 0 8.5 1 8.8 8.8 0 0 0 2.4 3.4l1 1.1c1.3-1.2 3.1-2 5.1-2zM8.5 6c1 0 2 .4 2.7 1l1-1.1a5.5 5.5 0 0 0-7.4 0l1 1.1c.7-.6 1.7-1 2.7-1zM8.5 9.5l1.6-1.7a2.3 2.3 0 0 0-3.2 0z"/></svg><svg viewBox="0 0 27 12"><rect x=".5" y=".5" width="22" height="11" rx="3.5" fill="none" stroke="currentColor" opacity=".5"/><rect x="2" y="2" width="19" height="8" rx="2"/><path d="M24 4v4c.8-.3 1.5-1.1 1.5-2S24.8 4.3 24 4z" opacity=".5"/></svg>'
const LABELS = { silk: '织物', interior: '室内' }
const bgLabel = (k) => ((K.spec.assets && K.spec.assets.labels) || {})[k] || LABELS[k] || k
const device = () => Object.assign({ width: 390, height: 800, time: '9:41', capsule: true }, K.spec.device || {})
const themeOf = (cfg) => LIB.THEMES.find((t) => t.id === cfg.theme) || LIB.THEMES[0]

/* ---------- 积木：blocks 与 custom ---------- */
function custom(name, args, frame, ctx) {
  const f = K.contentDef && K.contentDef.pages && K.contentDef.pages[name]
  if (!f) return `<div class="pt-miss">内容模块里没有「${esc(name)}」</div>`
  return `<div class="pt-custom" data-custom="${esc(name)}">${f(frame, ctx, args || {})}</div>`
}
/* 模块显示：每个 blocks / header / footer 项是一个模块，键 = 区域:序号；场景面板的“模块显示”开关关掉它就不画 */
const hidden = (frame, area, i) => K.moduleHidden(frame.page.id, `${area}:${i}`)
function modules(p) {
  const out = []
  if (p.custom) out.push({ key: 'custom', label: '页面内容：' + p.custom })
  ;[['header', '头部区'], ['blocks', '正文'], ['footer', '底部区']].forEach(([area, zone]) => {
    ;(p[area] || []).forEach((it, i) => {
      if (it.gap !== undefined) return
      const info = it.cid ? K.cidInfo(it.cid) : null
      const label = it.name || it.id || (it.cid ? it.cid + (info ? ' ' + info.name : '') : it.custom ? '自定义：' + it.custom : it.heading ? '标题：' + it.heading : '')
      out.push({ key: `${area}:${i}`, label: `${zone} · ${label}` })
    })
  })
  return out
}
function items(list, frame, ctx, area = 'blocks') {
  return (list || []).map((it, i) => {
    if (hidden(frame, area, i)) return ''
    if (it.custom) return custom(it.custom, it.args, frame, ctx)
    if (it.gap !== undefined) return `<div class="pt-gap" style="height:${+it.gap || 12}px"></div>`
    if (it.heading) return `<h3 class="pt-heading">${esc(it.heading)}</h3>`
    if (it.cid) return K.block(it.cid, K.ovOf(it))
    return ''
  }).join('')
}

/* ---------- 状态页 ---------- */
const FAILS = {
  'fail-network': ['网络不可用', '请检查网络连接后重试'], 'fail-timeout': ['请求超时', '服务器响应较慢，请稍后重试'],
  'fail-server': ['服务繁忙', '当前访问人数较多，请稍后重试'], 'fail-expired': ['数据已失效', '内容已发生变化，请刷新后再看'],
}
const stateTile = (name) => LIB.tileHTML(name, 'ci')
function actionBtn(go, label, primary = true) {
  if (!go) return ''
  const p = K.pages[go]
  const attr = p && p.type === 'tab' ? `data-pt-tab="${esc(K.tabs.find((t) => t.page === go).id)}"` : `data-pt-go="${esc(go)}"`
  return `<button type="button" class="btn ${primary ? 'btn-p' : 'btn-s'}" ${attr}>${esc(label)}</button>`
}
function stateView(view, p, frame, ctx) {
  if (view === 'loading') return `<div class="pt-sk" data-cid="MP-STATE-002" role="status" aria-label="加载中"><i class="b"></i><i class="l"></i><i class="l s"></i><i class="c"></i><i class="c"></i></div>`
  if (view === 'empty') {
    const e = p.empty || {}
    return `<div class="pt-state" data-cid="MP-STATE-001">${stateTile(e.icon || 'bag')}<h3>${esc(e.title || '这里还没有内容')}</h3><p>${esc(e.text || '先去逛逛，有了新内容会出现在这里')}</p>${actionBtn(e.go || (K.tabs[0] && K.tabs[0].page), e.button || '去逛逛')}</div>`
  }
  if (view.startsWith('fail')) {
    const [t, d] = FAILS[view] || FAILS['fail-server']
    return `<div class="pt-state" data-cid="MP-STATE-003">${stateTile('cart')}<h3>${t}</h3><p>${d}</p><div class="row"><button type="button" class="btn btn-p" data-pt-act="retry">重试</button>${frame.depth ? '<button type="button" class="btn btn-s" data-pt-back>返回</button>' : ''}</div></div>`
  }
  if (view === 'denied') {
    const r = ctx.roleDef || {}
    return `<div class="pt-state" data-cid="MP-STATE-001">${stateTile('wallet')}<h3>暂无权限</h3><p>当前身份：${esc(r.name || '未知')}。${esc(r.note || '登录后才能使用这个功能')}</p>${actionBtn(r.deniedGo, r.deniedLabel || '去登录')}</div>`
  }
  return ''
}

/* ---------- 一页 ---------- */
function render(frame, ctx) {
  const p = frame.page, cfg = ctx.cfg, d = device()
  const nav = p.nav || (p.type === 'tab' ? 'none' : 'bar')
  const hb = !!p.headerBg
  const light = p.light !== undefined ? !!p.light : hb && cfg.header !== 'light'
  const showTab = p.type === 'tab' && frame.depth === 0 && p.tabbar !== false
  const view = ctx.view
  let body = ''
  if (view === 'ok' || view === 'disabled') {
    if (view === 'disabled') body += `<div class="pt-banner" data-cid="MP-FB-008" role="status">${sv('info')}<span>${esc(((p.logic && p.logic.states) || []).find((s) => /禁用|不可|不能/.test(s)) || '条件未满足，本页的主操作已禁用')}</span></div>`
    if (p.custom && !K.moduleHidden(p.id, 'custom')) body += custom(p.custom, p.args, frame, ctx)
    body += items(p.blocks, frame, ctx, 'blocks')
  } else body = stateView(view, p, frame, ctx)
  const bg = cfg.header === 'image' ? ` style="background-image:url(${LIB.ASSETS.bg[cfg.bgImage] || ''})"` : ''
  const sb = `<div class="pt-sb" data-shell aria-hidden="true"><span>${esc(d.time)}</span><span class="r">${SB_ICONS}</span></div>`
  const cap = d.capsule ? `<div class="pt-cap" data-shell aria-hidden="true"><i></i><i></i><i></i><b></b><u></u></div>` : ''
  const back = frame.depth && !p.noBack ? `<button class="rb" type="button" data-pt-back aria-label="返回">${sv('back')}</button>` : ''
  const navbar = nav === 'none' || nav === 'space' ? '' : `<div class="pt-nav" data-cid="MP-NAV-001">${back}<h2>${esc(K.tpl(String(p.title || p.name).replace(/\{\{\s*arg\s*\}\}/g, frame.a || '')))}</h2></div>`
  const head = p.header && (view === 'ok' || view === 'disabled') ? `<div class="pt-head">${items(p.header, frame, ctx, 'header')}</div>` : ''
  const foot = p.footer ? `<div class="pt-foot">${items(p.footer, frame, ctx, 'footer')}</div>` : ''
  const tab = showTab ? `<nav class="pt-tabbar" data-cid="MP-NAV-002" aria-label="标签栏">${K.tabs.map((t) => {
    const n = t.badge ? +K.get(t.badge) || 0 : 0
    return `<button type="button" data-pt-tab="${esc(t.id)}"${K.S.tab === t.id ? ' class="on" aria-current="page"' : ''}>${sv(t.icon)}<span>${esc(t.name)}</span>${n > 0 ? `<b class="bdg" aria-label="${n} 件">${n > 99 ? '99+' : n}</b>` : ''}</button>`
  }).join('')}</nav><div class="pt-hind" data-shell aria-hidden="true"></div>` : ''
  return `<div class="pt-page" data-nav="${nav}" data-hb="${hb ? 1 : 0}" data-light="${light ? 1 : 0}">${sb}${cap}${navbar}${head}<div class="pt-scroll${p.scroll === false ? ' pt-fixed' : ''}">${hb ? `<div class="pt-hbg" data-bg="${esc(cfg.header)}"${bg}></div>` : ''}<div class="pt-body">${body}</div></div>${foot}${tab}</div>`
}

function mounted(root, frame, ctx) {
  const nav = root.querySelector('.pt-nav'), sc = root.querySelector('.pt-scroll')
  if (nav && sc && frame.page.nav === 'overlay') {
    const upd = () => nav.classList.toggle('solid', sc.scrollTop > 120)
    sc.addEventListener('scroll', upd, { passive: true }); upd()
  }
  if (ctx.view === 'disabled') {
    const reason = ((frame.page.logic && frame.page.logic.states) || []).find((s) => /禁用|不可|不能/.test(s)) || '条件未满足'
    root.querySelectorAll('[data-pt-primary], .pt-foot button, .btn-p').forEach((b) => {
      b.classList.add('pt-dis'); b.setAttribute('aria-disabled', 'true'); b.dataset.ptReason = reason
      if (b.tagName === 'BUTTON') b.disabled = true
    })
  }
}

function sheet(p, a, ctx) {
  const frame = { id: p.id, a, page: p, tab: K.S.tab, depth: K.cur().depth }
  const layout = p.layout === 'center' ? 'center' : 'bottom'
  let body = ''
  if (p.custom && !K.moduleHidden(p.id, 'custom')) body += custom(p.custom, p.args, frame, ctx)
  body += items(p.blocks, frame, ctx, 'blocks')
  return { title: p.title || p.name, body, foot: items(p.footer, frame, ctx, 'footer'), layout, cid: layout === 'center' ? 'MP-FB-002' : 'MP-FB-003' }
}

/* ---------- 配置组：头部背景 ---------- */
const headerGroup = {
  id: 'header', title: '头部背景', type: 'cards', cols: 3, default: 'gradient', note: '只作用于声明了头部背景的页面（首页、我的这类带头部区的一级页）。',
  options: (cfg) => {
    const v = LIB.themeVars(themeOf(cfg).id, document.documentElement.dataset.theme === 'dark' ? 'dark' : 'light') // 深浅两套主题色，缩略图跟着外观
    return [
      { v: 'gradient', label: '渐变', swatch: `linear-gradient(150deg,${LIB.mixc(v['--p'], '#FFFFFF', 0.85)},${v['--p']})` },
      { v: 'light', label: '浅色', swatch: `linear-gradient(180deg,${v['--pm']},${v['--pt']})` },
      { v: 'image', label: '图片', bg: LIB.ASSETS.bg[cfg.bgImage] },
    ]
  },
}
const bgKeys = Object.keys(LIB.ASSETS.bg)
const bgImageGroup = {
  id: 'bgImage', title: '背景图', type: 'cards', cols: 2, default: bgKeys[0], when: (cfg) => cfg.header === 'image',
  options: () => bgKeys.map((k) => ({ v: k, label: bgLabel(k), bg: LIB.ASSETS.bg[k] })),
}

K.kind({
  id: 'mini', tabsKey: 'tabbar', screen: '#ptScreen', clip: '#ptPhone', toasts: '#ptToasts', darkMode: 'tokens', confirmCid: 'MP-FB-002',
  size: () => { const d = device(); return { w: d.width, h: d.height } },
  stageMin: () => device().width + 16, /* 舞台至少一个设备框宽加两侧各 8：外壳放不下三栏时把左右栏改成抽屉，手机框不压到面板上 */
  defaultGroups: ['appearance', 'theme', 'header', 'bgImage', 'iconStyle', 'iconTile'],
  typeLabel: { tab: '一级页', sub: '二级页', sheet: '弹层', result: '结果页' },
  config: [headerGroup, bgImageGroup],
  render, mounted, sheet, modules,
})
