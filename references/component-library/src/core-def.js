/* ===== 定义：def() 登记组件，add() 兼容上一版的写法 ===== */
const BLOCKS = []
const GUIDES = {} // 键：'mp|CARD'
const P = (i) => ASSETS.prod[i]
const IC = (n) => (ICON_STYLE === 'line' ? lineSvg(n) : `<img class="ico" alt="" src="${ASSETS.icons[ICON_STYLE][n]}">`)
const ICS = () => `ics-${ICON_STYLE}`
/* stage 的取值 'dark' 是“深底舞台”（组件本来就画在深色底上）；类名不能叫 dark，那是外观开关（<html class="dark">），所以渲染成 night */
const stageClass = (s) => (s === 'dark' ? 'night' : s)
const sv = (n) => `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true" width="100%" height="100%">${LINE[n]}</svg>`
/* def({ id, dom, cat, name, style, fit, avoid, css, html, js, stage, wide, bg, kw })
 *   id    必填，如 'AD-TBL-001'（域-类别-序号）
 *   html  函数，返回 HTML 字符串（可用 IC()、P()、sv()、ICS()）
 *   js    可选，(root) => {}，渲染后执行，root 是块根 .ixr
 *   stage ''|'tint'|'dark'|'white'|'photo'；wide 占满一行；bg 背景图键（'silk'|'interior'）
 *   kw    搜索关键词（空格分隔） */
function def(o) {
  const m = /^(MP|AD)-([A-Z]+)-(\d{3})$/.exec(o.id || '')
  if (!m) throw new Error('编号格式不对：' + o.id)
  const dom = m[1].toLowerCase(), cat = m[2]
  if (!(CATS[dom] || []).some((c) => c[0] === cat)) throw new Error('类别不存在：' + o.id)
  if (BLOCKS.some((b) => b.id === o.id)) throw new Error('编号重复：' + o.id)
  BLOCKS.push({ id: o.id, dom, cat, name: o.name, style: o.style || '', fit: o.fit || '', avoid: o.avoid || '', css: o.css || '', html: o.html, js: o.js || null, stage: o.stage || '', wide: !!o.wide, bg: o.bg || null, kw: o.kw || '' })
}
function guide(dom, cat, rows) { GUIDES[dom + '|' + cat] = rows }
/* 上一版的写法：add(页签, 名称, 风格, 适合, 避免, css, html, {stage, wide, bg}) */
function add(tab, name, style, fit, avoid, css, html, o = {}) {
  const id = LEGACY[name]; if (!id) throw new Error('未登记的旧模板：' + name)
  def({ id, name, style, fit, avoid, css, html, stage: o.stage, wide: o.wide, bg: o.bg })
}
Object.defineProperty(GUIDES, '__legacy', { value: true, enumerable: false })
