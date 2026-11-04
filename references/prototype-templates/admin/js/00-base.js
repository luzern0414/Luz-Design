/* ===== 后台 kind 运行时（由生成器按文件名顺序拼接，包进 (function (K, LIB) { … })(K, LIB)）=====
 * 00 基础工具  10 外壳（侧栏 顶栏 多标签页 面包屑 弹出层）  20 列表  30 表单  40 设置  50 仪表盘  60 详情与动作  70 页面与状态  90 注册与事件
 * 机制与内容分开：这里没有任何行业内容；菜单、页面、字段、数据、文案都来自规格与内容模块。 */
const { sv } = LIB
const esc = K.esc, $ = K.$, $$ = K.$$, clone = K.clone
const AD = (K.ad = { version: 1 })
const ic = (n, c = '') => `<i class="ad-ic ${c}" aria-hidden="true">${sv(n)}</i>`
const num = (v) => (typeof v === 'number' ? v : parseFloat(String(v == null ? '' : v).replace(/,/g, '')) || 0)
const money = (n) => num(n).toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })
const int = (n) => Math.round(num(n)).toLocaleString('en-US')
const shell = () => K.data.shell || {}
const todayStr = () => shell().today || '2026-11-04'
const dayShift = (base, n) => { const d = new Date(base + 'T00:00:00Z'); d.setUTCDate(d.getUTCDate() + n); return d.toISOString().slice(0, 10) }
const nowStr = () => todayStr() + ' ' + (shell().now || '10:30')
const rec = (s, row) => String(s == null ? '' : s).replace(/\{(\w+)\}/g, (m, k) => (row && row[k] != null ? row[k] : ''))
const tagH = (text, tone) => `<span class="ad-tag ${tone || 'mu'} dot">${esc(text)}</span>`
const mapOf = (name) => (typeof name === 'object' && name ? name : K.get('maps.' + name) || {})
const optsOf = (o) => (typeof o === 'string' ? K.get('options.' + o) || [] : o || [])
const readonly = () => !!(K.roles.find((r) => r.id === K.S.role) || {}).readonly
const roleName = () => (K.roles.find((r) => r.id === K.S.role) || {}).name || ''
const readReason = () => `当前角色「${roleName()}」只读，不能修改`
const hash = (s) => { let h = 0; String(s).split('').forEach((c) => { h = (h * 31 + c.charCodeAt(0)) >>> 0 }); return h }
const avatar = (row, key, size = 28) => LIB.critter(row && row.av != null ? row.av : hash(row ? row[key] : '') % 12, size)
const rowsOf = (path) => K.get(path) || []
const findRow = (path, id, key = 'id') => rowsOf(path).find((r) => String(r[key]) === String(id))
const sceneLabel = (id, v) => { const s = (K.spec.scenes || []).find((x) => x.id === id); const o = s && s.options.find((x) => x.v === v); return o ? o.label.replace(/^失败[:：]\s*/, '') : v }
const tabOf = (id) => K.tabs.find((t) => t.id === id) || {}
const rootPageOf = (tabId) => K.pages[tabOf(tabId).page] || {}
const pageTab = (p) => (p.type === 'tab' ? (K.tabs.find((t) => t.page === p.id) || {}).id : p.tab)
const stamp = () => '@now'
const resolveVal = (v) => (v === '@now' ? nowStr() : v === '@today' ? todayStr() : v)
const matches = (row, when) => !when || Object.entries(when).every(([k, v]) => (v && typeof v === 'object' && !Array.isArray(v) ? ('not' in v ? String(row[k]) !== String(v.not) : true) : Array.isArray(v) ? v.map(String).includes(String(row[k])) : String(row[k]) === String(v)))
const sheetPageOf = (id) => K.pages[id]
/* 动作描述 → 引擎属性（go 压栈 / sheet 打开居中面板 / tab 切侧栏标签 / act 调动作 / toast 提示 / back 返回） */
function navAttrs(a) {
  if (a.go) return `data-pt-go="${esc(a.go)}"`
  if (a.sheet) return `data-pt-sheet="${esc(a.sheet)}"`
  if (a.tab) return `data-ad-nav="${esc(a.tab)}"${a.preset ? ` data-ad-preset='${esc(JSON.stringify(a.preset))}'` : ''}`
  if (a.act) return `data-pt-act="${esc(a.act)}"`
  if (a.toast) return `data-pt-say="${esc(a.toast)}"`
  if (a.back) return 'data-pt-back'
  if (a.export) return `data-ad-export="${esc(a.export)}"`
  return ''
}
const btnH = (a, extra = '') => {
  const write = a.write === true
  const cls = ['ad-btn', a.kind === 'primary' ? 'primary' : '', a.danger ? 'danger' : ''].filter(Boolean).join(' ')
  return `<button type="button" class="${cls}" ${navAttrs(a)}${write ? ' data-write' : ''}${a.id ? ` data-aid="${esc(a.id)}"` : ''} ${extra}>${a.icon ? ic(a.icon) : ''}${esc(a.label)}</button>`
}
AD.fmt = { money, int }
AD.rows = rowsOf
