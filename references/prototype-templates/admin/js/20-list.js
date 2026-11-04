/* ===== 列表页：状态标签带数量、即输即查的筛选、更多筛选、已选条件、排序、批量栏（原位替换工具栏）、行内开关、分页（默认 20）、转卡片 ===== */
const LS = new Map()
const SIZES = [10, 20, 50, 100]
let PAGE_SIZE = null
const SWBUSY = new Set(), SWERR = new Map()
const lstate = (p) => {
  let s = LS.get(p.id)
  if (!s) { const L = p.list; s = { tab: (L.tabs && L.tabs.default) || '__all', q: '', f: {}, sort: null, page: 1, size: PAGE_SIZE || L.pageSize || 20, sel: new Set(), more: false, flash: null }; LS.set(p.id, s) }
  return s
}
AD.lstate = (p) => lstate(typeof p === 'string' ? K.pages[p] : p)
const filtersOf = (L) => ((L.filters && L.filters.primary) || []).concat((L.filters && L.filters.more) || [])
const defaultSort = (L, s) => (L.defaultSort && (L.defaultSort.key ? L.defaultSort : L.defaultSort[s.tab] || L.defaultSort.__all)) || null
const sortOf = (L, s) => s.sort || defaultSort(L, s)
const cutoff = (n) => dayShift(todayStr(), -(Math.max(1, n) - 1))
function baseRows(L, s, skipTab) {
  let rows = rowsOf(L.data)
  if (s.q && L.filters && L.filters.search) { const q = s.q.toLowerCase(), ks = L.filters.search.keys; rows = rows.filter((r) => ks.some((k) => String(r[k] == null ? '' : r[k]).toLowerCase().includes(q))) }
  filtersOf(L).forEach((f) => {
    if (f.type === 'num') {
      const lo = s.f[f.key + '.min'], hi = s.f[f.key + '.max']
      if (lo !== undefined && lo !== '') rows = rows.filter((r) => num(r[f.key]) >= num(lo))
      if (hi !== undefined && hi !== '') rows = rows.filter((r) => num(r[f.key]) <= num(hi))
    } else if (f.type === 'date') {
      const a = s.f[f.key + '.from'], b = s.f[f.key + '.to']
      if (a) rows = rows.filter((r) => String(r[f.key]).slice(0, 10) >= a)
      if (b) rows = rows.filter((r) => String(r[f.key]).slice(0, 10) <= b)
    } else {
      const v = s.f[f.key]; if (v === undefined || v === '') return
      if (f.type === 'range') rows = rows.filter((r) => (+v === 0 ? String(r[f.key]).slice(0, 10) === todayStr() : String(r[f.key]).slice(0, 10) >= cutoff(+v)))
      else rows = rows.filter((r) => String(r[f.key]) === String(v))
    }
  })
  if (!skipTab && L.tabs && s.tab !== '__all') rows = rows.filter((r) => String(r[L.tabs.key]) === String(s.tab))
  return rows
}
function visibleRows(L, s) {
  const rows = baseRows(L, s).slice(), so = sortOf(L, s)
  if (so) { const d = so.dir === 'desc' ? -1 : 1; rows.sort((a, b) => { const x = a[so.key], y = b[so.key]; return (typeof x === 'number' && typeof y === 'number' ? x - y : String(x == null ? '' : x).localeCompare(String(y == null ? '' : y), 'zh')) * d }) }
  return rows
}
const filterActive = (L, s) => !!(s.q || Object.entries(s.f).some(([, v]) => v !== '' && v != null))
const colAlign = (c) => c.align || (c.type === 'long' || c.type === 'person' || c.type === 'thumb' ? 'l' : c.type === 'money' ? 'r' : 'c')
function cellH(L, c, row, pid) {
  const v = row[c.key], t = c.type || 'text', e = v == null || v === '' ? '—' : esc(v)
  if (t === 'money') return v == null || v === '' ? '—' : num(v) < 0 ? `<span class="neg">${money(v)}</span>` : money(v)
  if (t === 'num') return v == null || v === '' ? '—' : int(v) + (c.unit ? `<small> ${esc(c.unit)}</small>` : '')
  if (t === 'status' || t === 'tag') { const m = (t === 'status' ? mapOf(c.map || c.key)[v] : null) || { label: v, tone: c.tone || 'mu' }; return v == null || v === '' ? '—' : tagH(m.label, m.tone) }
  if (t === 'date') return esc(String(v || '').slice(0, 10)) || '—'
  if (t === 'datetime') return v ? `<span class="two">${esc(String(v).slice(0, 10))}<small>${esc(String(v).slice(11, 16))}</small></span>` : '—'
  if (t === 'person') return `<span class="who">${avatar(row, c.key, 28)}<span>${esc(v)}${c.sub ? `<small>${esc(rec(c.sub, row))}</small>` : ''}</span></span>`
  if (t === 'thumb') return `<span class="thumb"><img alt="" src="${LIB.P(num(Array.isArray(row[c.img || 'img']) ? row[c.img || 'img'][0] : row[c.img || 'img']) % 9)}"><span>${esc(v)}${c.sub ? `<small>${esc(rec(c.sub, row))}</small>` : ''}</span></span>`
  if (t === 'long') return `<span class="cut" title="${esc(v)}">${e}</span>`
  if (t === 'two') return `<span class="two">${e}${c.sub ? `<small>${esc(rec(c.sub, row))}</small>` : ''}</span>`
  if (t === 'switch') return switchH(L, c, row, pid)
  if (t === 'rating') return v == null ? '—' : `${esc(v)} 分`
  return c.tpl ? esc(rec(c.tpl, row)) : e
}
function switchH(L, c, row, pid) {
  const on = !!row[c.key], bk = `${pid}|${row.id}|${c.key}`, busy = SWBUSY.has(bk), err = SWERR.get(bk)
  return `<button type="button" class="ad-sw" role="switch" aria-checked="${on}" data-ad-sw="${esc(row.id)}" data-k="${esc(c.key)}" data-fk="sw-${esc(row.id)}-${esc(c.key)}" data-write${busy ? ' data-busy="1" aria-busy="true"' : ''} aria-label="${esc(c.label)}：${esc(rec(c.name || '{name}', row))}"><span class="tg"></span><span class="st">${busy ? '处理中' : esc(on ? c.on || '开' : c.off || '关')}</span></button>${err ? `<span class="ad-swerr" role="alert">${esc(err)}</span>` : ''}`
}
function actBtn(a, row, cls = 'ad-btn text') {
  const bad = a.when && !matches(row, a.when), ro = readonly() && a.write !== false
  const reason = bad ? a.whyNot || '当前状态不能操作' : ro ? readReason() : ''
  return `<button type="button" class="${cls}${a.danger ? ' danger' : ''}" data-ad-ra="${esc(a.id)}" data-id="${esc(row.id)}"${a.write !== false ? ' data-write' : ''}${reason ? ` aria-disabled="true" data-reason="${esc(reason)}" title="${esc(reason)}"` : ''}>${esc(a.label)}</button>`
}
function rowActsH(L, row) {
  const acts = L.rowActions || [], rest = acts.slice(2).concat(L.moreActions || [])
  let h = acts.slice(0, 2).map((a) => actBtn(a, row)).join('')
  if (rest.length) h += `<button type="button" class="ad-btn text" data-ad-l="rowmenu" data-id="${esc(row.id)}" aria-label="更多操作：${esc(rec(L.nameTpl || '{name}', row))}" aria-haspopup="menu">更多</button>`
  return h
}
const cols = (L) => L.columns.filter((c) => !c.hide)
const colW = (c) => (c.width ? ` style="width:${c.width}px;min-width:${c.width}px"` : '')
function tableH(L, s, rows, p) {
  const so = sortOf(L, s), cs = cols(L), hasAct = (L.rowActions || []).length || (L.moreActions || []).length, sel = L.select !== false
  const frozen = cs.length >= 6
  const pageRows = rows.slice((s.page - 1) * s.size, s.page * s.size)
  const allOn = pageRows.length && pageRows.every((r) => s.sel.has(String(r.id)))
  const minW = (sel ? 44 : 0) + cs.reduce((a, c) => a + (c.width || (c.type === 'date' || c.type === 'datetime' ? 112 : 96)), 0) + (hasAct ? L.actWidth || 140 : 0)
  let h = `<table class="ad-tbl" data-cid="AD-TBL-001" data-pagination="${rows.length > s.size ? 'on' : 'single'}" style="min-width:${minW}px"><thead><tr>`
  if (sel) h += `<th class="ck${frozen ? ' fz-l' : ''}" style="${frozen ? 'left:0' : ''}"><label><input type="checkbox" data-ad-l="selall" data-fk="selall" aria-label="选择本页全部"${allOn ? ' checked' : ''}></label></th>`
  cs.forEach((c, i) => {
    const a = colAlign(c), on = so && so.key === c.key
    const lab = c.sort ? `<button type="button" data-ad-l="sort" data-k="${esc(c.key)}" data-fk="sort-${esc(c.key)}" aria-label="按${esc(c.label)}排序">${esc(c.label)}${ic(on ? (so.dir === 'desc' ? 'arrowdown' : 'arrowup') : 'sort', 's')}</button>` : esc(c.label)
    const sty = [frozen && i === 0 ? `left:${sel ? 44 : 0}px` : '', c.width ? `width:${c.width}px;min-width:${c.width}px` : ''].filter(Boolean).join(';')
    h += `<th class="${a === 'l' ? 'l' : a === 'r' ? 'r' : ''}${frozen && i === 0 ? ' fz-l' : ''}"${on ? ` aria-sort="${so.dir === 'desc' ? 'descending' : 'ascending'}"` : ''}${sty ? ` style="${sty}"` : ''}>${lab}</th>`
  })
  if (hasAct) h += `<th class="${frozen ? 'fz-r' : ''}" style="min-width:${L.actWidth || 140}px">操作</th>`
  h += '</tr></thead><tbody>'
  pageRows.forEach((r) => {
    const on = s.sel.has(String(r.id)), fl = s.flash === String(r.id)
    h += `<tr data-id="${esc(r.id)}"${on ? ' class="sel"' : ''}${fl ? ' data-flash="1"' : ''}>`
    if (sel) h += `<td class="ck${frozen ? ' fz-l' : ''}" style="${frozen ? 'left:0' : ''}"><label><input type="checkbox" data-ad-l="sel" data-id="${esc(r.id)}" data-fk="sel-${esc(r.id)}" aria-label="选择${esc(rec(L.nameTpl || '{name}', r))}"${on ? ' checked' : ''}></label></td>`
    cs.forEach((c, i) => {
      const a = colAlign(c)
      h += `<td data-label="${esc(c.label)}" class="${a === 'l' ? 'l' : a === 'r' ? 'r' : ''}${c.type === 'num' || c.type === 'money' ? ' n' : ''}${frozen && i === 0 ? ' fz-l' : ''}"${frozen && i === 0 ? ` style="left:${sel ? 44 : 0}px"` : ''}>${cellH(L, c, r, p.id)}</td>`
    })
    if (hasAct) h += `<td class="act${frozen ? ' fz-r' : ''}">${rowActsH(L, r)}</td>`
    h += '</tr>'
  })
  if (L.sum && pageRows.length) {
    const pick = s.sel.size ? rows.filter((r) => s.sel.has(String(r.id))) : pageRows
    const tot = (list) => (c) => (L.sum.includes(c.key) ? money(list.reduce((a, r) => a + num(r[c.key]), 0)) : '')
    const row = (cls, label, list) => `<tr class="sumrow ${cls}">${sel ? '<td class="ck"></td>' : ''}${cs.map((c, i) => `<td data-label="${esc(c.label)}" class="${colAlign(c) === 'r' ? 'r n' : 'l'}">${i === 0 ? esc(label) : tot(list)(c)}</td>`).join('')}${hasAct ? '<td class="act"></td>' : ''}</tr>`
    h += row('', s.sel.size ? `已选 ${s.sel.size} 项合计` : '本页合计', pick) + row('sub', '全部筛选结果合计', rows)
  }
  return h + '</tbody></table>'
}
function pageList(cur, total) {
  if (total <= 7) return Array.from({ length: total }, (_, i) => i + 1)
  const set = new Set([1, total, cur, cur - 1, cur + 1]); if (cur <= 3) [2, 3, 4].forEach((x) => set.add(x)); if (cur >= total - 2) [total - 1, total - 2, total - 3].forEach((x) => set.add(x))
  const arr = [...set].filter((x) => x >= 1 && x <= total).sort((a, b) => a - b), out = []
  arr.forEach((x, i) => { if (i && x - arr[i - 1] > 1) out.push('…'); out.push(x) })
  return out
}
function pagerH(s, n) {
  const total = Math.max(1, Math.ceil(n / s.size))
  if (!n) return ''
  let h = `<span>共 ${n} 条</span>`
  if (n <= Math.min(...SIZES) && total === 1) return `<div class="ad-pg" data-cid="AD-TBL-003">${h}</div>`
  h += `<select class="ad-sel" data-ad-l="size" data-fk="size" aria-label="每页条数">${SIZES.map((x) => `<option value="${x}"${x === s.size ? ' selected' : ''}>${x} 条/页</option>`).join('')}</select>`
  if (total > 1) {
    h += `<span class="pb"><button type="button" data-ad-l="page" data-fk="pg-prev" data-v="${s.page - 1}" aria-label="上一页"${s.page <= 1 ? ' disabled' : ''}>${ic('left', 's')}</button>${pageList(s.page, total).map((x) => (x === '…' ? '<span class="el">…</span>' : `<button type="button" data-ad-l="page" data-fk="pg-${x}" data-v="${x}"${x === s.page ? ' aria-current="page"' : ''} aria-label="第 ${x} 页">${x}</button>`)).join('')}<button type="button" data-ad-l="page" data-fk="pg-next" data-v="${s.page + 1}" aria-label="下一页"${s.page >= total ? ' disabled' : ''}>${ic('right', 's')}</button></span>`
    if (total > 5) h += `<span class="jump">跳至<input class="ad-in" type="number" min="1" max="${total}" data-ad-l="jump" data-fk="jump" aria-label="跳至第几页">页</span>`
  }
  return `<div class="ad-pg" data-cid="AD-TBL-003">${h}</div>`
}
function filterCtl(f, s) {
  const v = s.f[f.key] == null ? '' : s.f[f.key]
  if (f.type === 'num') return `<span class="rg"><span>${esc(f.label)}</span><input class="ad-in" type="number" data-ad-f="${esc(f.key)}.min" data-fk="f-${esc(f.key)}.min" value="${esc(s.f[f.key + '.min'] || '')}" placeholder="最小" aria-label="${esc(f.label)}最小值"><span>–</span><input class="ad-in" type="number" data-ad-f="${esc(f.key)}.max" data-fk="f-${esc(f.key)}.max" value="${esc(s.f[f.key + '.max'] || '')}" placeholder="最大" aria-label="${esc(f.label)}最大值">${f.unit ? `<span>${esc(f.unit)}</span>` : ''}</span>`
  if (f.type === 'date') return `<span class="rg"><span>${esc(f.label)}</span><input class="ad-in" type="date" data-ad-f="${esc(f.key)}.from" data-fk="f-${esc(f.key)}.from" value="${esc(s.f[f.key + '.from'] || '')}" aria-label="${esc(f.label)}起" style="width:150px"><span>–</span><input class="ad-in" type="date" data-ad-f="${esc(f.key)}.to" data-fk="f-${esc(f.key)}.to" value="${esc(s.f[f.key + '.to'] || '')}" aria-label="${esc(f.label)}止" style="width:150px"></span>`
  const opts = f.type === 'range' ? (f.options || [{ v: 0, label: '今天' }, { v: 7, label: '近 7 天' }, { v: 30, label: '近 30 天' }]) : optsOf(f.options)
  return `<select class="ad-sel" data-ad-f="${esc(f.key)}" data-fk="f-${esc(f.key)}" aria-label="${esc(f.label)}"><option value="">${esc(f.all || '全部' + f.label)}</option>${opts.map((o) => `<option value="${esc(o.v)}"${String(o.v) === String(v) ? ' selected' : ''}>${esc(o.label)}</option>`).join('')}</select>`
}
function filterText(f, s) {
  if (f.type === 'num') { const lo = s.f[f.key + '.min'], hi = s.f[f.key + '.max']; return lo || hi ? `${f.label}：${lo || '不限'} – ${hi || '不限'}${f.unit || ''}` : '' }
  if (f.type === 'date') { const a = s.f[f.key + '.from'], b = s.f[f.key + '.to']; return a || b ? `${f.label}：${a || '不限'} 至 ${b || '不限'}` : '' }
  const v = s.f[f.key]; if (v === undefined || v === '') return ''
  const opts = f.type === 'range' ? f.options || [{ v: 0, label: '今天' }, { v: 7, label: '近 7 天' }, { v: 30, label: '近 30 天' }] : optsOf(f.options), o = opts.find((x) => String(x.v) === String(v))
  return `${f.label}：${o ? o.label : v}`
}
const chipKeys = (f) => (f.type === 'num' ? [f.key + '.min', f.key + '.max'] : f.type === 'date' ? [f.key + '.from', f.key + '.to'] : [f.key])
function barH(p, L, s, rows) {
  const acts = (p.actions || []).map((a) => btnH(Object.assign({ write: a.write }, a))).join('')
  if (s.sel.size) {
    const sr = rowsOf(L.data).filter((r) => s.sel.has(String(r.id)))
    const bulk = (L.bulk || []).map((a) => {
      const bad = a.when && !sr.every((r) => matches(r, a.when)), ro = readonly(), reason = bad ? a.whyNot || '所选项里有不能执行的项' : ro ? readReason() : ''
      return `<button type="button" class="ad-btn${a.danger ? ' danger' : ''}" data-ad-ba="${esc(a.id)}" data-write${reason ? ` aria-disabled="true" data-reason="${esc(reason)}" title="${esc(reason)}"` : ''}>${a.icon ? ic(a.icon) : ''}${esc(a.label)}</button>`
    }).join('')
    return `<div class="ad-lbar bulk" data-cid="AD-TBL-002" role="region" aria-label="批量操作" style="min-height:${s.barH || 40}px"><div class="l"><span>已选 <b>${s.sel.size}</b> 项</span>${bulk}</div><div class="r"><button type="button" class="ad-btn text" data-ad-l="unsel">取消选择</button></div></div>`
  }
  const F = L.filters || {}, mf = F.more || []
  const active = mf.reduce((a, f) => a + (filterText(f, s) ? 1 : 0), 0)
  let l = ''
  if (F.search) l += `<label class="ad-search">${ic('search')}<input class="ad-in" type="search" data-ad-f="__q" data-fk="q" value="${esc(s.q)}" placeholder="${esc(F.search.placeholder || '搜索')}" aria-label="${esc(F.search.placeholder || '搜索')}"></label>`
  ;(F.primary || []).forEach((f) => { l += filterCtl(f, s) })
  if (mf.length) l += `<button type="button" class="ad-btn" data-ad-l="more" data-fk="more" aria-expanded="${s.more}">${ic('filter')}更多筛选${active ? `<span class="ad-tag in">${active}</span>` : ''}</button>`
  const exp = L.export ? `<button type="button" class="ad-btn" data-ad-export="${esc(p.id)}">${ic('download')}导出筛选结果（共 ${rows.length} 条）</button>` : ''
  return `<div class="ad-lbar" data-cid="AD-NAV-007"><div class="l">${l}</div><div class="r">${exp}${acts}</div></div>`
}
function tabsH(L, s) {
  const T = L.tabs; if (!T) return ''
  const base = baseRows(L, s, true), cnt = (v) => (v === '__all' ? base.length : base.filter((r) => String(r[T.key]) === String(v)).length), mp = mapOf(T.map || T.key)
  const one = (v, label) => `<button type="button" role="tab" data-ad-l="tab" data-fk="tab-${esc(v)}" data-v="${esc(v)}" aria-selected="${s.tab === String(v)}">${esc(label)}<em class="${cnt(v) ? '' : 'z'}">${cnt(v)}</em></button>`
  const more = T.more || [], inMore = more.map(String).includes(s.tab)
  return `<div class="ad-stabs" role="tablist" aria-label="状态" data-cid="AD-FLT-010">${T.order.map((v) => one(v, (mp[v] || {}).label || v)).join('')}${one('__all', T.all || '全部')}${more.length ? `<span class="mw"><button type="button" role="tab" data-ad-l="tabmore" aria-haspopup="menu" aria-selected="${inMore}">${inMore ? esc((mp[s.tab] || {}).label || s.tab) : '更多'}${ic('down', 's')}</button></span>` : ''}</div>`
}
function moreH(L, s) {
  const mf = (L.filters && L.filters.more) || []
  return `<div class="ad-more" data-cid="AD-FLT-002"${s.more ? '' : ' hidden'}>${mf.map((f) => filterCtl(f, s)).join('')}</div>`
}
function chipsH(L, s) {
  const chips = filtersOf(L).map((f) => [f, filterText(f, s)]).filter(([, t]) => t)
  if (!chips.length) return ''
  return `<div class="ad-chips" data-cid="AD-FLT-006"><span>已生效：</span>${chips.map(([f, t]) => `<span class="ad-chip">${esc(t)}<button type="button" data-ad-l="rmf" data-k="${esc(f.key)}" aria-label="移除${esc(t)}">${ic('close', 's')}</button></span>`).join('')}<button type="button" class="ad-btn text" data-ad-l="clear">清空</button></div>`
}
function bodyH(p, L, s, rows) {
  if (!rows.length) {
    const act = filterActive(L, s) || (L.tabs && s.tab !== '__all')
    const e = L.empty || {}
    return `<div class="ad-empty" data-cid="AD-STATE-001">${LIB.tileHTML(e.tile || 'bag', 'ci')}<h3>${act ? `没有找到符合条件的${esc(L.noun || '数据')}` : esc(e.title || `还没有${L.noun || '数据'}`)}</h3><p>${act ? '换个条件试试，或清除筛选查看全部' : esc(e.text || '')}</p><div class="row">${act ? '<button type="button" class="ad-btn" data-ad-l="clear">清除筛选</button>' : e.action ? btnH(e.action) : ''}</div></div>`
  }
  return `<div class="ad-tw" tabindex="0" role="region" aria-label="${esc(L.noun || '数据')}列表（可横向滚动）">${tableH(L, s, rows, p)}</div>`
}
function listH(p) {
  const L = p.list, s = lstate(p), rows = visibleRows(L, s)
  const total = Math.max(1, Math.ceil(rows.length / s.size)); s.page = Math.min(s.page, total)
  return `<div class="ad-list" data-list="${esc(p.id)}"><div data-r="bar">${barH(p, L, s, rows)}</div><div data-r="more">${moreH(L, s)}</div><div data-r="chips">${chipsH(L, s)}</div><div data-r="tabs">${tabsH(L, s)}</div><div data-r="table">${bodyH(p, L, s, rows)}</div><div data-r="pager">${pagerH(s, rows.length)}</div></div>`
}
/* 重画列表各区。由引擎的 K.render({part: 'list:页面 id'}) 经 renderPart 调进来：引擎按 data-fk 恢复焦点与光标，所以这里不管焦点 */
function paintList(wrap) {
  if (!wrap) return
  const p = K.pages[wrap.dataset.list], L = p.list, s = lstate(p), rows = visibleRows(L, s)
  const total = Math.max(1, Math.ceil(rows.length / s.size)); s.page = Math.min(s.page, total)
  const bar0 = $('.ad-lbar:not(.bulk)', wrap); if (bar0) s.barH = bar0.offsetHeight
  const set = (r, h) => { h = LW(h); const el = $(`[data-r="${r}"]`, wrap); if (el.innerHTML !== h) el.innerHTML = h }
  const sc = $('.ad-tw', wrap), left = sc ? sc.scrollLeft : 0
  set('bar', barH(p, L, s, rows)); set('more', moreH(L, s)); set('chips', chipsH(L, s)); set('tabs', tabsH(L, s)); set('table', bodyH(p, L, s, rows)); set('pager', pagerH(s, rows.length))
  const sc2 = $('.ad-tw', wrap); if (sc2) sc2.scrollLeft = left
  const all = $('[data-ad-l="selall"]', wrap); if (all) all.indeterminate = !all.checked && rows.slice((s.page - 1) * s.size, s.page * s.size).some((r) => s.sel.has(String(r.id)))
  s.flash = null
}
const repaint = (w) => K.render({ part: 'list:' + w.dataset.list })
const listWrapOf = (el) => el.closest('.ad-list')
/* 点击与输入：命令表 */
const LCMD = {
  tab: (w, s, el) => { s.tab = el.dataset.v; s.page = 1; s.sel.clear(); s.sort = null },
  sort: (w, s, el) => { const L = K.pages[w.dataset.list].list, cur = sortOf(L, s), k = el.dataset.k; s.sort = cur && cur.key === k ? (cur.dir === 'asc' ? { key: k, dir: 'desc' } : null) : { key: k, dir: 'asc' }; s.page = 1 },
  page: (w, s, el) => { s.page = Math.max(1, +el.dataset.v || 1); s.sel.clear() },
  more: (w, s) => { s.more = !s.more },
  rmf: (w, s, el) => { const f = filtersOf(K.pages[w.dataset.list].list).find((x) => x.key === el.dataset.k); chipKeys(f).forEach((k) => delete s.f[k]); s.page = 1; s.sel.clear() },
  clear: (w, s) => { s.f = {}; s.q = ''; const T = K.pages[w.dataset.list].list.tabs; if (T) s.tab = '__all'; s.page = 1; s.sel.clear() },
  sel: (w, s, el) => { el.checked ? s.sel.add(el.dataset.id) : s.sel.delete(el.dataset.id) },
  selall: (w, s, el) => { const L = K.pages[w.dataset.list].list, pr = visibleRows(L, s).slice((s.page - 1) * s.size, s.page * s.size); pr.forEach((r) => (el.checked ? s.sel.add(String(r.id)) : s.sel.delete(String(r.id)))) },
  unsel: (w, s) => s.sel.clear(),
}
function onListClick(e) {
  const el = e.target.closest('[data-ad-l]'); if (!el) return false
  const w = listWrapOf(el); if (!w) return false
  const c = el.dataset.adL, s = lstate(K.pages[w.dataset.list])
  if (c === 'rowmenu') { openRowMenu(el, w); return true }
  if (c === 'tabmore') { openTabMenu(el, w); return true }
  if (c === 'size' || c === 'jump') return false
  if (el.matches('input[type="checkbox"]') && e.type === 'click') { /* 复选框交给 change 事件 */ return false }
  if (LCMD[c]) { LCMD[c](w, s, el); repaint(w); return true }
  return false
}
function onListChange(e) {
  const el = e.target; const w = listWrapOf(el); if (!w) return false
  const s = lstate(K.pages[w.dataset.list])
  if (el.dataset.adL === 'sel' || el.dataset.adL === 'selall') { LCMD[el.dataset.adL](w, s, el); repaint(w); return true }
  if (el.dataset.adL === 'size') { s.size = +el.value; PAGE_SIZE = s.size; s.page = 1; s.sel.clear(); repaint(w); return true }
  if (el.dataset.adL === 'jump') { const total = Math.max(1, Math.ceil(visibleRows(K.pages[w.dataset.list].list, s).length / s.size)); s.page = Math.min(total, Math.max(1, +el.value || 1)); repaint(w); return true }
  const k = el.getAttribute('data-ad-f'); if (k == null || k === '__q') return false
  s.f[k] = el.value; s.page = 1; s.sel.clear(); repaint(w); return true
}
function onListInput(e) {
  const el = e.target; const w = el.closest && listWrapOf(el); if (!w) return false
  const k = el.getAttribute && el.getAttribute('data-ad-f'); if (k == null) return false
  const s = lstate(K.pages[w.dataset.list])
  if (k === '__q') s.q = el.value.trim(); else if (el.matches('input[type="number"], input[type="date"]')) s.f[k] = el.value; else return false
  s.page = 1; s.sel.clear(); repaint(w); return true
}
/* 行内开关：悲观更新——点击后进入处理中，成功才切换；失败保持原状并在原位写原因 */
function toggleSwitch(w, rowId, key) {
  const p = K.pages[w.dataset.list], L = p.list, c = L.columns.find((x) => x.key === key), row = findRow(L.data, rowId), bk = `${p.id}|${rowId}|${key}`
  if (!row || SWBUSY.has(bk)) return
  if (readonly()) { K.toast(readReason(), 'warn'); return }
  const sid = c.scene || 'switch', sc = K.scene(sid) || 'ok', to = !row[key]
  SWERR.delete(bk); SWBUSY.add(bk); repaint(w)
  setTimeout(() => {
    SWBUSY.delete(bk)
    let why = null
    if (K.S.net === 'offline') why = '网络不可用，请检查网络后重试'
    else if (sc.indexOf('fail') === 0) why = (c.reasons && c.reasons[sc]) || sceneLabel(sid, sc)
    else { const g = (c.guard || []).find((x) => x.to === to && matches(row, x.when)); if (g) why = g.reason }
    if (why) { SWERR.set(bk, why); setTimeout(() => { SWERR.delete(bk); K.render({ part: 'list:' + p.id }) }, 5000) }
    else { row[key] = to; auditLog(`${c.label}：${rec(c.name || '{name}', row)} 已${to ? c.on || '开启' : c.off || '关闭'}`); K.toast(rec(to ? c.onToast : c.offToast, row) || `${rec(c.name || '{name}', row)}已${to ? c.on || '开启' : c.off || '关闭'}`) }
    if (!why) lstate(p).flash = String(rowId)
    K.render({ part: 'list:' + p.id })
    drawSide()
  }, sc === 'processing' ? 2200 : 450)
}
