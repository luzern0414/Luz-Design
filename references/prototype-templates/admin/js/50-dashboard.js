/* ===== 工作台 / 驾驶舱：指标卡（计算后的变化）、趋势、占比、排行、待办、动态、日程；页面级时间范围统一控制所有卡片 ===== */
const DST = { range: {}, metric: {}, off: {}, alert: new Set() }
const FMT = {
  money: (v) => money(v), int: (v) => int(v), pct: (v) => (num(v) * 100).toFixed(1) + '%', dec1: (v) => num(v).toFixed(1),
}
const fmtBy = (f, v) => (FMT[f] || FMT.int)(v)
const rangeOf = (p) => DST.range[p.id] || (p.dashboard.range && p.dashboard.range.default) || 7
function series(k, n, off) {
  const arr = rowsOf(k.calc.src), end = arr.length - off, part = arr.slice(Math.max(0, end - n), end), c = k.calc
  const val = (r) => (c.op === 'ratio' ? (num(r[c.den]) ? num(r[c.num]) / num(r[c.den]) : 0) : num(r[c.field]))
  return { vals: part.map(val), rows: part }
}
function calcKpi(k, n) {
  const c = k.calc, a = series(k, n, 0), b = series(k, n, n)
  const agg = (s) => {
    if (!s.rows.length) return null
    if (c.op === 'sum') return s.vals.reduce((x, y) => x + y, 0)
    if (c.op === 'avg') return s.vals.reduce((x, y) => x + y, 0) / s.vals.length
    if (c.op === 'last') return s.vals[s.vals.length - 1]
    if (c.op === 'ratio') { const nu = s.rows.reduce((x, r) => x + num(r[c.num]), 0), de = s.rows.reduce((x, r) => x + num(r[c.den]), 0); return de ? nu / de : 0 }
    return 0
  }
  const cur = agg(a), prev = b.rows.length >= Math.max(3, n / 2) ? agg(b) : null
  return { cur, prev, delta: prev ? (cur - prev) / prev : null, spark: a.vals }
}
function sparkH(vals) {
  if (vals.length < 7) return ''
  const w = 72, h = 24, mx = Math.max(...vals), mn = Math.min(...vals), sp = mx - mn || 1
  return `<svg class="sp" viewBox="0 0 ${w} ${h}" aria-hidden="true"><path d="${vals.map((v, i) => `${i ? 'L' : 'M'}${((i / (vals.length - 1)) * w).toFixed(1)} ${(h - 3 - ((v - mn) / sp) * (h - 6)).toFixed(1)}`).join('')}"/></svg>`
}
function kpiH(k, n) {
  const r = calcKpi(k, n), up = r.delta != null && r.delta > 0.0005, dn = r.delta != null && r.delta < -0.0005
  const good = k.bad ? dn : up, bad = k.bad ? up : dn
  const tile = k.tile ? LIB.tileHTML(k.tile, 'sq') : `<span class="ti">${ic(k.icon || 'chart')}</span>`
  return `<div class="ad-card ad-kpi" data-cid="AD-DATA-001" data-kpi="${esc(k.id)}"><div class="hd"><span>${esc(k.label)}</span>${tile}</div><div class="vl">${r.cur == null ? '—' : esc(fmtBy(k.format, r.cur))}${k.unit ? `<small>${esc(k.unit)}</small>` : ''}</div><div class="dl">${r.delta == null ? '<span>暂无对比</span>' : `<span>较上期</span><b class="${good ? 'up' : bad ? 'dn' : 'fl'}">${up ? '↑' : dn ? '↓' : '–'} ${Math.abs(r.delta * 100).toFixed(1)}%</b>`}${sparkH(r.spark)}</div></div>`
}
/* 折线图：悬停（或聚焦）出十字线与数值；点少于 3 个不画折线 */
function lineH(vals, labels, f, unit, id) {
  if (vals.length < 3) return `<div class="ad-empty" style="padding:24px">数据点不足 3 个，先看数字：${vals.length ? esc(fmtBy(f, vals[vals.length - 1])) + esc(unit || '') : '暂无数据'}</div>`
  const W = 640, H = 220, L = 52, R = 12, T = 12, B = 28, mx = Math.max(...vals) * 1.08 || 1, x = (i) => L + (i / (vals.length - 1)) * (W - L - R), y = (v) => T + (1 - v / mx) * (H - T - B)
  const pts = vals.map((v, i) => [x(i), y(v)])
  const grid = [0, 1, 2, 3, 4].map((g) => { const v = (mx / 4) * g, yy = y(v); return `<g class="grid"><line x1="${L}" x2="${W - R}" y1="${yy}" y2="${yy}"/></g><text x="${L - 8}" y="${yy + 4}" text-anchor="end">${esc(mx >= 10000 ? (v / 1000).toFixed(0) + 'k' : v >= 100 ? Math.round(v) : v.toFixed(1))}</text>` }).join('')
  const step = Math.max(1, Math.round(vals.length / 6))
  const xl = labels.map((l, i) => (i % step === 0 || i === labels.length - 1 ? `<text x="${x(i)}" y="${H - 8}" text-anchor="middle">${esc(l)}</text>` : '')).join('')
  const d = pts.map((p, i) => `${i ? 'L' : 'M'}${p[0].toFixed(1)} ${p[1].toFixed(1)}`).join('')
  return `<div class="ad-chart" data-line="${esc(id)}" data-vals="${esc(JSON.stringify(vals))}" data-labels="${esc(JSON.stringify(labels))}" data-fmt="${esc(f)}" data-unit="${esc(unit || '')}"><svg viewBox="0 0 ${W} ${H}" role="img" aria-label="趋势折线图，共 ${vals.length} 个点，最近一天 ${esc(fmtBy(f, vals[vals.length - 1]))}${esc(unit || '')}">${grid}${xl}<path class="ar" d="${d}L${x(vals.length - 1)} ${y(0)}L${L} ${y(0)}Z"/><path class="ln" d="${d}"/><g class="hvg" hidden><line class="hv" y1="${T}" y2="${H - B}"/><circle class="pt" r="4"/></g><rect class="hit" x="${L}" y="${T}" width="${W - L - R}" height="${H - T - B}" fill="transparent" tabindex="0" aria-label="趋势图，可用左右方向键查看每一天"/></svg><div class="ad-tip" hidden></div></div>`
}
const TONES = ['var(--p, #A85D79)', '#6E8BA8', '#8AA27A', '#C0A06A', '#9A8DB5', '#B58A82']
function donutH(items, hidden, unit, secId) {
  const vis = items.filter((it) => !hidden.includes(it.name)), tot = vis.reduce((a, b) => a + num(b.value), 0)
  const R = 56, C = 2 * Math.PI * R; let off = 0
  const segs = vis.map((it) => { const i = items.indexOf(it), len = tot ? (num(it.value) / tot) * C : 0; const s = `<circle cx="75" cy="75" r="${R}" fill="none" stroke="${TONES[i % TONES.length]}" stroke-width="22" stroke-dasharray="${len.toFixed(2)} ${(C - len).toFixed(2)}" stroke-dashoffset="${(-off).toFixed(2)}" transform="rotate(-90 75 75)"><title>${esc(it.name)}：${esc(int(it.value))}${esc(unit || '')}（${tot ? ((num(it.value) / tot) * 100).toFixed(1) : 0}%）</title></circle>`; off += len; return s }).join('')
  return `<div class="ad-donut"><svg viewBox="0 0 150 150" role="img" aria-label="占比环形图">${segs}<text class="ctr" x="75" y="77">${esc(int(tot))}</text><text class="ctr2" x="75" y="95">合计${esc(unit || '')}</text></svg><div class="ad-legend">${items.map((it, i) => `<button type="button" data-ad-dl="${esc(secId)}" data-n="${esc(it.name)}" data-fk="dl-${esc(secId)}-${i}" aria-pressed="${!hidden.includes(it.name)}"><i style="background:${TONES[i % TONES.length]}"></i><span class="n">${esc(it.name)}</span><span class="v">${esc(int(it.value))}${tot && !hidden.includes(it.name) ? ' · ' + ((num(it.value) / tot) * 100).toFixed(0) + '%' : ''}</span></button>`).join('')}</div></div>`
}
function rankH(items, top, unit) {
  const list = items.slice().sort((a, b) => num(b.value) - num(a.value)).slice(0, top || 5), mx = num(list[0] && list[0].value) || 1
  return `<div class="ad-rank">${list.map((it, i) => `<div class="rw"><span class="no${i < 3 ? ' t' : ''}">${i + 1}</span><span class="nm" title="${esc(it.name)}">${esc(it.name)}</span><span class="vv">${esc(int(it.value))}${esc(unit || '')}</span><span class="bar"><i style="width:${((num(it.value) / mx) * 100).toFixed(1)}%"></i></span></div>`).join('')}</div>`
}
function todoH(items) {
  return `<div class="ad-todo" data-cid="AD-FLOW-009">${items.map((t) => {
    const n = t.count ? rowsOf(t.count.data).filter((r) => matches(r, t.count.where)).length : 0
    const a = navAttrs(t.tab ? { tab: t.tab, preset: t.preset } : t.sheet ? { sheet: t.sheet } : t.go ? { go: t.go } : {})
    return `<button type="button" class="rw" ${a}>${t.icon ? ic(t.icon) : ''}<span>${esc(t.label)}</span><span class="n${n ? '' : ' z'}">${n}</span></button>`
  }).join('')}</div>`
}
function feedH(S, rows) {
  return `<ul class="ad-feed" data-cid="AD-DATA-005">${rows.slice(0, S.limit || 6).map((r) => `<li><span class="tm">${esc(r.time)}</span><span class="tx" title="${esc(r.text)}">${esc(r.text)}</span>${r.sheet ? `<button type="button" class="bt" data-pt-sheet="${esc(r.sheet)}">查看</button>` : r.go ? `<button type="button" class="bt" data-pt-go="${esc(r.go)}">查看</button>` : '<span></span>'}</li>`).join('')}</ul>`
}
function agendaH(S) {
  const where = JSON.parse(JSON.stringify(S.where || {}).replace(/"@today"/g, JSON.stringify(todayStr())))
  const rows = rowsOf(S.src).filter((r) => matches(r, where)).sort((a, b) => String(a[S.time]).localeCompare(String(b[S.time]))).slice(0, S.limit || 8), mp = mapOf(S.map || S.status)
  if (!rows.length) return '<div class="ad-empty" style="padding:24px">今天没有安排</div>'
  return `<ul class="ad-feed" data-cid="AD-FLOW-005">${rows.map((r) => `<li><span class="tm">${esc(r[S.time])}</span><span class="tx"><b>${esc(rec(S.row, r))}</b>${S.sub ? `<small style="display:block;color:var(--ad-ink3)">${esc(rec(S.sub, r))}</small>` : ''}</span>${S.status ? tagH((mp[r[S.status]] || {}).label || r[S.status], (mp[r[S.status]] || {}).tone) : ''}</li>`).join('')}</ul>`
}
function sectionH(p, S, i, n) {
  const w = S.w ? ' w' + S.w : '', id = p.id + i
  let body = '', head = `<h3>${esc(S.title)}</h3>`
  if (S.kind === 'trend') {
    const ms = S.metrics, mi = Math.min(DST.metric[id] || 0, ms.length - 1), m = ms[mi], arr = rowsOf(S.src).slice(-n)
    head = `<div class="hd"><h3>${esc(S.title)}</h3>${ms.length > 1 ? `<div class="ad-seg" role="group" aria-label="指标">${ms.map((x, j) => `<button type="button" data-ad-dm="${id}:${j}" data-fk="dm-${id}-${j}" aria-pressed="${j === mi}">${esc(x.label)}</button>`).join('')}</div>` : ''}</div>`
    body = lineH(arr.map((r) => num(r[m.field])), arr.map((r) => String(r.date).slice(5)), m.format, m.unit, id)
  } else if (S.kind === 'donut') {
    const items = rowsOf(S.src); body = items.filter((x) => num(x.value) > 0).length < 2 ? '<div class="ad-empty" style="padding:24px">只有 1 类数据，不画环形图</div>' : donutH(items, DST.off[id] || [], S.unit, id)
  } else if (S.kind === 'rank') body = rankH(rowsOf(S.src), S.top, S.unit)
  else if (S.kind === 'todo') body = todoH(S.items)
  else if (S.kind === 'feed') body = feedH(S, rowsOf(S.src))
  else if (S.kind === 'agenda') body = agendaH(S)
  return `<section class="ad-card ad-dc${w}" data-module="${esc(S.id || 'sec' + i)}" data-cid="${S.kind === 'trend' ? 'AD-CHART-001' : S.kind === 'donut' ? 'AD-CHART-005' : S.kind === 'rank' ? 'AD-DATA-007' : S.kind === 'todo' ? 'AD-FLOW-009' : S.kind === 'agenda' ? 'AD-FLOW-005' : 'AD-DATA-005'}" data-sec="${id}">${head}${body}</section>`
}
function dashH(p) {
  const D = p.dashboard, n = rangeOf(p), ks = D.kpis || []
  const calc = ks.map((k) => [k, calcKpi(k, n)]), quiet = calc.filter(([k, r]) => k.quiet && r.cur === 0), shown = calc.filter(([k, r]) => !(k.quiet && r.cur === 0)).map(([k]) => k)
  const alerts = (D.alerts || []).filter((a) => !DST.alert.has(a.id)).map((a) => { const k = ks.find((x) => x.id === a.kpi), r = k && calcKpi(k, n); if (!r || r.delta == null || (a.deltaGt != null && r.delta * 100 < a.deltaGt)) return ''; return `<div class="ad-banner" role="status" data-cid="AD-FB-004">${ic('alert')}<span class="tx">${esc(rec(a.text, { label: k.label, delta: (r.delta * 100).toFixed(1), value: fmtBy(k.format, r.cur) }))}${a.tab ? ` <button type="button" class="ad-btn text" ${navAttrs({ tab: a.tab, preset: a.preset })}>去处理</button>` : ''}</span><button type="button" class="x" data-ad-dx="${esc(a.id)}" aria-label="关闭提醒">${ic('close', 's')}</button></div>` }).join('')
  const head = `<div class="ad-ph" data-cid="AD-NAV-007"><div class="l">${D.range ? `<div class="ad-seg" role="group" aria-label="时间范围" data-cid="AD-CTRL-006">${D.range.options.map((o) => `<button type="button" data-ad-dr="${o.v}" data-fk="dr-${o.v}" aria-pressed="${n === o.v}">${esc(o.label)}</button>`).join('')}</div>` : ''}</div><div class="r">${(p.actions || []).map((a) => btnH(a)).join('')}</div></div>`
  const hideK = K.moduleHidden(p.id, 'kpis')
  return `<div class="ad-dashroot" data-dash="${esc(p.id)}">${head}${hideK ? '' : alerts}${hideK ? '' : `<div class="ad-kpis">${shown.map((k) => kpiH(k, n)).join('')}</div>${quiet.length ? `<p class="ad-sub" style="color:var(--ad-ink2)">${ic('check', 's')}暂无异常：${quiet.map((q) => esc(q[0].label)).join('、')} 当前都是 0</p>` : ''}`}<div class="ad-dash">${(D.sections || []).map((S, i) => (K.moduleHidden(p.id, S.id || 'sec' + i) ? '' : sectionH(p, S, i, n))).join('')}</div></div>`
}
function repaintDash() { const w = $('[data-dash]'); if (!w) return null; const p = K.pages[w.dataset.dash]; const h = document.createElement('div'); h.innerHTML = LW(dashH(p)); const n = h.firstElementChild; w.replaceWith(n); return n }
function dashClick(e) {
  const el = e.target.closest('[data-ad-dr],[data-ad-dm],[data-ad-dl],[data-ad-dx]'); if (!el) return false
  const w = el.closest('[data-dash]'); if (!w) return false
  const p = K.pages[w.dataset.dash]
  if (el.dataset.adDr) DST.range[p.id] = +el.dataset.adDr
  else if (el.dataset.adDm) { const [id, j] = el.dataset.adDm.split(':'); DST.metric[id] = +j }
  else if (el.dataset.adDl) { const id = el.dataset.adDl, off = DST.off[id] || (DST.off[id] = []), nm = el.dataset.n, i = off.indexOf(nm); if (i >= 0) off.splice(i, 1); else off.push(nm) }
  else if (el.dataset.adDx) DST.alert.add(el.dataset.adDx)
  K.render({ part: 'dash' }); return true
}
/* 图表悬停与键盘：找最近的点，画十字线并弹出数值 */
function chartMove(e) {
  const box = e.target.closest && e.target.closest('[data-line]'); if (!box) return
  const svg = $('svg', box), vals = JSON.parse(box.dataset.vals), labels = JSON.parse(box.dataset.labels), r = svg.getBoundingClientRect(), vb = svg.viewBox.baseVal
  let i
  if (e.type === 'keydown') { const cur = +box.dataset.i; i = Math.max(0, Math.min(vals.length - 1, (isNaN(cur) ? vals.length - 1 : cur) + (e.key === 'ArrowRight' ? 1 : e.key === 'ArrowLeft' ? -1 : 0))) }
  else { const px = ((e.clientX - r.left) / r.width) * vb.width; i = Math.max(0, Math.min(vals.length - 1, Math.round(((px - 52) / (vb.width - 64)) * (vals.length - 1)))) }
  box.dataset.i = i
  const x = 52 + (i / (vals.length - 1)) * (vb.width - 64), mx = Math.max(...vals) * 1.08 || 1, y = 12 + (1 - vals[i] / mx) * (vb.height - 40)
  const g = $('.hvg', box); g.hidden = false; $('.hv', g).setAttribute('x1', x); $('.hv', g).setAttribute('x2', x); $('.pt', g).setAttribute('cx', x); $('.pt', g).setAttribute('cy', y)
  const tip = $('.ad-tip', box); tip.hidden = false; tip.innerHTML = `<b>${esc(labels[i])}</b>　${esc(fmtBy(box.dataset.fmt, vals[i]))}${esc(box.dataset.unit)}`
  tip.style.left = Math.max(60, Math.min(r.width - 60, (x / vb.width) * r.width)) + 'px'; tip.style.top = Math.max(24, (y / vb.height) * r.height - 8) + 'px'
}
function chartLeave(e) { const box = e.target.closest && e.target.closest('[data-line]'); if (!box) return; $('.hvg', box).hidden = true; $('.ad-tip', box).hidden = true }
