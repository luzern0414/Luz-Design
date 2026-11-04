;(() => {
/* ==========================================================================
 * 后台管理 · 数据展示（AD-DATA）与图表（AD-CHART）
 * 全部原生 SVG / CSS，不引外部库。整个文件包在一个函数里，内部名字不会和别的文件冲突。
 * 图表按真实像素宽度绘制（ResizeObserver 重绘），文字不会随窄屏缩到看不清。
 * ========================================================================== */

/* ---------- 色板：低饱和分类色（OKLCH 色度约 0.075–0.09），顺序固定、不循环 ----------
 * 灰蓝 杏橘 青碧 豆沙粉 苔绿 薰紫 古铜；相邻两色在红绿色盲模拟下 ΔE≥8.7，正常视觉 ΔE≥20。
 * 色度刻意低于校验器的 0.10 下限（用户要求低饱和），所以颜色之外一定有图例、直接标注或提示框。
 * 散点/气泡这类“任意两点都可能相邻”的图只用 3 类：杏橘、青碧、薰紫（两两 ΔE≥15）。
 * 单指标图（折线、面积）用主题色 var(--p)，“本期 vs 上期”是强调形式：主题色 + 中性灰。 */
const VZ = ['#5C7CA6', '#D99A78', '#3C8888', '#CC8FB0', '#678557', '#9E9DD6', '#947446']
const VZ_OTHER = '#9AA1AB'
const VZ_PREV = '#B9BFC8'
const OKC = 'var(--ok)', OKB = 'var(--ok-bg)', WARNC = 'var(--warn)', WARNB = 'var(--warn-bg)', BADC = 'var(--danger)', BADB = 'var(--danger-bg)'

/* ---------- 小工具 ---------- */
const NS = 'http://www.w3.org/2000/svg'
const SV = (tag, a, kids) => { const e = document.createElementNS(NS, tag); if (a) for (const k in a) if (a[k] != null) e.setAttribute(k, a[k]); if (kids != null) [].concat(kids).forEach((c) => e.append(c)); return e }
const $ = (r, s) => r.querySelector(s)
const $$ = (r, s) => [...r.querySelectorAll(s)]
const clamp = (v, a, b) => Math.max(a, Math.min(b, v))
const int = (v) => Math.round(v).toLocaleString('en-US')
const dec = (v, d = 1) => v.toLocaleString('en-US', { minimumFractionDigits: d, maximumFractionDigits: d })
const wan = (v) => (Math.abs(v) >= 1e4 ? dec(v / 1e4, Math.abs(v) >= 1e5 ? 0 : 1).replace(/\.0$/, '') + ' 万' : int(v))
const pad2 = (n) => String(n).padStart(2, '0')
const rng = (s) => () => ((s = (s * 1664525 + 1013904223) >>> 0) / 4294967296)
const WKN = ['日', '一', '二', '三', '四', '五', '六']
const dayOf = (i, n) => new Date(2026, 10, 4 - (n - 1 - i))
const md = (d) => `${pad2(d.getMonth() + 1)}-${pad2(d.getDate())}`
const wk = (d) => '周' + WKN[d.getDay()]
const WKF = [0.92, 0.94, 0.97, 1, 1.06, 1.16, 1.1] /* 周一到周日的零售节奏 */
function gen(seed, n, base, vol, drift, season = 1) {
  const r = rng(seed); const out = []
  for (let i = 0; i < n; i++) { const wd = (dayOf(i, n).getDay() + 6) % 7; out.push(base * (1 + (drift * i) / n) * (1 + (WKF[wd] - 1) * season) * (1 + vol * (r() * 2 - 1))) }
  return out
}
function nice(max, n = 4) {
  if (!(max > 0)) return { max: 4, ticks: [0, 1, 2, 3, 4] }
  const raw = max / n, mag = 10 ** Math.floor(Math.log10(raw)), f = raw / mag
  const step = (f <= 1 ? 1 : f <= 2 ? 2 : f <= 5 ? 5 : 10) * mag
  const top = Math.ceil(max / step - 1e-9) * step, ticks = []
  for (let v = 0; v <= top + step / 2; v += step) ticks.push(+v.toFixed(6))
  return { max: top, ticks }
}
function tween(ms, fn, done) {
  const t0 = performance.now(); let raf = 0
  const step = (now) => { const p = Math.min(1, (now - t0) / ms); fn(1 - (1 - p) ** 3); if (p < 1) raf = requestAnimationFrame(step); else if (done) done() }
  raf = requestAnimationFrame(step); return () => cancelAnimationFrame(raf)
}
/* 单调三次曲线（折线不过冲，不会画出数据里没有的起伏） */
const sgn = (x) => (x < 0 ? -1 : 1)
function slope3(x0, y0, x1, y1, x2, y2) { const h0 = x1 - x0, h1 = x2 - x1, s0 = (y1 - y0) / (h0 || 1e-9), s1 = (y2 - y1) / (h1 || 1e-9), p = (s0 * h1 + s1 * h0) / (h0 + h1 || 1e-9); return (sgn(s0) + sgn(s1)) * Math.min(Math.abs(s0), Math.abs(s1), 0.5 * Math.abs(p)) || 0 }
function slope2(x0, y0, x1, y1, t) { const h = x1 - x0; return h ? (3 * (y1 - y0) / h - t) / 2 : t }
function curve(P) {
  const n = P.length; if (n < 2) return ''
  if (n === 2) return `M${P[0][0]},${P[0][1]}L${P[1][0]},${P[1][1]}`
  const t = new Array(n)
  for (let i = 1; i < n - 1; i++) t[i] = slope3(P[i - 1][0], P[i - 1][1], P[i][0], P[i][1], P[i + 1][0], P[i + 1][1])
  t[0] = slope2(P[0][0], P[0][1], P[1][0], P[1][1], t[1]); t[n - 1] = slope2(P[n - 2][0], P[n - 2][1], P[n - 1][0], P[n - 1][1], t[n - 2])
  let d = `M${P[0][0]},${P[0][1]}`
  for (let i = 0; i < n - 1; i++) { const dx = (P[i + 1][0] - P[i][0]) / 3; d += `C${(P[i][0] + dx).toFixed(2)},${(P[i][1] + dx * t[i]).toFixed(2)},${(P[i + 1][0] - dx).toFixed(2)},${(P[i + 1][1] - dx * t[i + 1]).toFixed(2)},${P[i + 1][0]},${P[i + 1][1]}` }
  return d
}
/* 只圆顶部两个角的柱（底边贴基线是方的） */
function colPath(x, y, w, h, r) { r = Math.max(0, Math.min(r, w / 2, h)); return `M${x},${y + h}V${y + r}Q${x},${y} ${x + r},${y}H${x + w - r}Q${x + w},${y} ${x + w},${y + r}V${y + h}Z` }
/* 画布宽度变化时重绘：draw(宽度) 在宽度为 0（被隐藏）时不调用 */
function watch(el, draw) {
  let w0 = 0
  const run = () => { const w = Math.floor(el.clientWidth); if (w > 0 && w !== w0) { w0 = w; draw(w) } }
  if (window.ResizeObserver) new ResizeObserver(() => requestAnimationFrame(run)).observe(el)
  run(); return { w: () => w0 }
}
/* 提示框：所有文字都用 textContent，名称来自数据时也安全 */
function mkTip(host) {
  const t = document.createElement('div'); t.className = 'tip'; t.hidden = true; host.appendChild(t)
  return {
    show(x, y, title, rows, foot) {
      t.replaceChildren()
      if (title) { const b = document.createElement('b'); b.className = 't'; b.textContent = title; t.append(b) }
      ;(rows || []).forEach((r) => {
        const d = document.createElement('div'); d.className = 'r'
        const i = document.createElement('i'); if (r.c) i.style.setProperty('--c', r.c); if (r.k) i.className = r.k
        const s = document.createElement('span'); s.textContent = r.n
        const v = document.createElement('b'); v.textContent = r.v
        d.append(i, s, v); t.append(d)
      })
      if (foot) { const f = document.createElement('div'); f.className = 'ft'; f.textContent = foot; t.append(f) }
      t.hidden = false
      const w = t.offsetWidth, h = t.offsetHeight, pw = host.clientWidth, ph = host.clientHeight
      let left = x + 16; if (left + w > pw) left = x - 16 - w; left = clamp(left, 0, Math.max(0, pw - w))
      t.style.left = left + 'px'; t.style.top = clamp(y - h / 2, 0, Math.max(0, ph - h)) + 'px'
    },
    hide() { t.hidden = true },
  }
}
const lgHTML = (items, shape = 'sq') => `<div class="lgd" role="group" aria-label="图例，点击显示或隐藏">${items.map((it, i) => `<button type="button" class="lg ${shape}" data-i="${i}" aria-pressed="true"><i style="--c:${it.c}"></i>${it.n}</button>`).join('')}</div>`
function bindLegend(root, cb, hover) {
  const hid = new Set(), bs = $$(root, '.lg')
  bs.forEach((b) => {
    b.addEventListener('click', () => { const i = +b.dataset.i; if (!hid.has(i) && hid.size >= bs.length - 1) return; hid.has(i) ? hid.delete(i) : hid.add(i); b.classList.toggle('off', hid.has(i)); b.setAttribute('aria-pressed', !hid.has(i)); cb(hid) })
    if (hover) { b.addEventListener('pointerenter', () => !hid.has(+b.dataset.i) && hover(+b.dataset.i)); b.addEventListener('pointerleave', () => hover(-1)) }
  })
  return hid
}
function bindSeg(seg, cb) {
  seg.addEventListener('click', (e) => { const b = e.target.closest('button'); if (!b || b.classList.contains('on')) return; $$(seg, 'button').forEach((x) => { x.classList.toggle('on', x === b); x.setAttribute('aria-pressed', x === b) }); cb(b.dataset.v) })
}
const segHTML = (items, on = 0) => `<div class="sg" role="group">${items.map(([v, t], i) => `<button type="button" data-v="${v}" class="${i === on ? 'on' : ''}" aria-pressed="${i === on}">${t}</button>`).join('')}</div>`
const deltaHTML = (v, good = 1, unit = '%') => { const up = v >= 0, flat = Math.abs(v) < 0.05, tone = flat ? 'z' : up === good > 0 ? 'g' : 'b'; return `<span class="dl ${tone}"><i class="ar">${sv(up ? 'arrowup' : 'arrowdown')}</i>${dec(Math.abs(v), 1)}${unit}</span>` }

/* ---------- 共用样式（每个块带自己的前缀，选择器不会串） ---------- */
const DL_CSS = (p) => `.${p} .dl{display:inline-flex;align-items:center;gap:2px;height:20px;padding:0 6px 0 4px;border-radius:4px;font-size:12px;line-height:20px;font-weight:600;white-space:nowrap}.${p} .dl.g{color:${OKC};background:${OKB}}.${p} .dl.b{color:${BADC};background:${BADB}}.${p} .dl.z{color:var(--ink2);background:var(--soft)}.${p} .dl .ar{display:block;width:12px;height:12px}`
const CARD = 'background:var(--card);border-radius:12px;box-shadow:0 1px 2px var(--sh04),0 4px 16px var(--sh06)'
const SEG_CSS = (p) => `.${p} .sg{display:inline-flex;margin-left:auto;padding:2px;border-radius:8px;background:var(--soft);flex:none}.${p} .sg button{height:28px;padding:0 12px;border-radius:8px;font-size:12px;line-height:28px;font-weight:600;color:var(--ink2);transition:background .15s,color .15s,box-shadow .15s}.${p} .sg button:hover{color:var(--ink)}.${p} .sg button.on{background:var(--lift);color:var(--ink);box-shadow:0 1px 3px var(--sh14)}`
/* 图表块的公共外观：白卡 + 标题（写结论）+ 图例 + 画布 + 提示框 */
const VZ_CSS = (p) => `.${p}{width:1400px;max-width:100%;box-sizing:border-box;${CARD};padding:20px 24px 18px;color:var(--ink);font-size:14px;line-height:22px;position:relative}.${p} *{box-sizing:border-box}
.${p} .hd{display:flex;align-items:flex-start;justify-content:space-between;gap:8px 16px;flex-wrap:wrap}.${p} .hd h4{margin:0;font-size:16px;line-height:24px;font-weight:600}.${p} .hd p{margin:0;font-size:12px;line-height:20px;color:var(--ink3)}
${SEG_CSS(p)}
.${p} .lgd{display:flex;flex-wrap:wrap;gap:2px 10px;margin-top:8px}.${p} .lg{display:inline-flex;align-items:center;gap:6px;height:28px;padding:0 8px 0 6px;border-radius:8px;font-size:12px;color:var(--ink2);transition:color .15s,background .15s}.${p} .lg:hover{background:var(--n3)}.${p} .lg i{display:block;width:10px;height:10px;border-radius:2px;background:var(--c)}.${p} .lg.ln i{width:14px;height:3px;border-radius:2px}.${p} .lg.off{color:var(--ink3)}.${p} .lg.off i{background:var(--card);box-shadow:inset 0 0 0 1.5px var(--n9)}
.${p} .plot{position:relative;margin-top:8px}.${p} .plot svg{display:block;width:100%;overflow:visible;outline:none}
.${p} .tip{position:absolute;z-index:5;pointer-events:none;min-width:136px;padding:8px 12px;border-radius:8px;background:var(--card2);box-shadow:0 0 0 1px var(--n6),0 8px 24px var(--sh14);font-size:12px;line-height:20px;white-space:nowrap}.${p} .tip .t{display:block;font-weight:400;color:var(--ink3);margin-bottom:2px}.${p} .tip .r{display:flex;align-items:center;gap:8px}.${p} .tip .r i{display:block;flex:none;width:10px;height:10px;border-radius:2px;background:var(--c)}.${p} .tip .r i.ln{width:14px;height:3px}.${p} .tip .r span{flex:1;color:var(--ink2)}.${p} .tip .r b{margin-left:14px;font-weight:600;color:var(--ink);font-variant-numeric:tabular-nums}.${p} .tip .ft{margin-top:4px;padding-top:4px;border-top:1px solid var(--line);color:var(--ink3)}
.${p} .ax{font-size:12px;fill:var(--ink3)}.${p} .ax.b{fill:var(--ink)}.${p} .gl{stroke:var(--n4);stroke-width:1;shape-rendering:crispEdges}.${p} .bl{stroke:var(--n7);stroke-width:1;shape-rendering:crispEdges}
@media(max-width:520px){.${p}{padding:16px 14px 14px}}@media(prefers-reduced-motion:reduce){.${p} *{animation:none!important}}`

/* ---------- 示例数据：销售、订单、访客等指标，60 天，所有统计卡与图表共用 ---------- */
const MET = {
  sales: { n: '销售额', agg: 'sum', d: gen(11, 60, 4300, 0.16, 0.22).map(Math.round), good: 1, show: (v) => `<small>¥</small>${int(v)}`, txt: (v) => '¥' + int(v) },
  orders: { n: '订单数', agg: 'sum', d: gen(12, 60, 118, 0.14, 0.18).map(Math.round), good: 1, show: (v) => int(v), txt: (v) => int(v) + ' 单' },
  uv: { n: '访客数', agg: 'sum', d: gen(13, 60, 3350, 0.12, 0.1).map(Math.round), good: 1, show: (v) => int(v), txt: (v) => int(v) + ' 人' },
  conv: { n: '支付转化率', agg: 'avg', d: gen(14, 60, 4.5, 0.07, 0.07, 0.4).map((v) => +v.toFixed(2)), good: 1, pt: true, show: (v) => `${dec(v, 2)}<small>%</small>`, txt: (v) => dec(v, 2) + '%' },
  aov: { n: '客单价', agg: 'avg', d: gen(15, 60, 36.5, 0.05, 0.04, 0.3).map((v) => +v.toFixed(1)), good: 1, show: (v) => `<small>¥</small>${dec(v, 1)}`, txt: (v) => '¥' + dec(v, 1) },
  refund: { n: '退款率', agg: 'avg', d: gen(16, 60, 2.1, 0.1, 0.16, 0.2).map((v) => +v.toFixed(2)), good: -1, pt: true, show: (v) => `${dec(v, 2)}<small>%</small>`, txt: (v) => dec(v, 2) + '%' },
}
function calc(k, days) {
  const m = MET[k], N = m.d.length, cur = m.d.slice(N - days), prev = m.d.slice(N - 2 * days, N - days)
  const agg = (a) => (m.agg === 'sum' ? a.reduce((s, v) => s + v, 0) : a.reduce((s, v) => s + v, 0) / a.length)
  const value = agg(cur), pv = agg(prev)
  return { pts: cur, prev: pv, value, delta: m.pt ? value - pv : (value / pv - 1) * 100, dunit: m.pt ? 'pt' : '%' }
}
/* 迷你趋势线：单调曲线 + 淡色面积 + 末点；悬停时末点跟着指针走并回调 onHover(下标 / -1) */
function spark(host, pts, o = {}) {
  host.replaceChildren()
  const w = o.w || host.clientWidth || 96, h = o.h || host.clientHeight || 40, pad = 5
  const lo = Math.min(...pts), hi = Math.max(...pts), span = hi - lo || 1
  const P = pts.map((v, i) => [pad + (i * (w - 2 * pad)) / (pts.length - 1), h - pad - ((v - lo) / span) * (h - 2 * pad)])
  const svg = SV('svg', { width: w, height: h, viewBox: `0 0 ${w} ${h}`, role: 'img', 'aria-label': o.label || '趋势' })
  svg.style.cssText = 'display:block;overflow:visible;touch-action:pan-y'
  const line = curve(P)
  svg.append(SV('path', { d: `${line}L${P[P.length - 1][0]},${h}L${P[0][0]},${h}Z`, style: 'fill:var(--p);opacity:.1' }))
  svg.append(SV('path', { d: line, fill: 'none', style: 'stroke:var(--p)', 'stroke-width': 2, 'stroke-linejoin': 'round', 'stroke-linecap': 'round' }))
  const dot = SV('circle', { r: 4, cx: P[P.length - 1][0], cy: P[P.length - 1][1], style: 'fill:var(--p)', stroke: 'var(--card)', 'stroke-width': 2 })
  svg.append(dot)
  const hit = SV('rect', { x: 0, y: 0, width: w, height: h, fill: 'transparent' }); svg.append(hit)
  const at = (e) => { const r = svg.getBoundingClientRect(); return clamp(Math.round((((e.clientX - r.left) / r.width) * w - pad) / ((w - 2 * pad) / (pts.length - 1))), 0, pts.length - 1) }
  const move = (e) => { const i = at(e); dot.setAttribute('cx', P[i][0]); dot.setAttribute('cy', P[i][1]); if (o.onHover) o.onHover(i, e) }
  const leave = () => { dot.setAttribute('cx', P[P.length - 1][0]); dot.setAttribute('cy', P[P.length - 1][1]); if (o.onHover) o.onHover(-1) }
  hit.addEventListener('pointermove', move); hit.addEventListener('pointerleave', leave); hit.addEventListener('pointerdown', move)
  host.append(svg); return svg
}

/* ==========================================================================
 * 折线 / 面积引擎：CHART-001、CHART-002、DATA-003 共用
 * cfg = { xs:[标签], title(i), series:[{n,c,pts,area}], hidden:Set, avg, mark:{i,text}, yfmt, vfmt, foot(i) }
 * ========================================================================== */
function mkLine(plot, o = {}) {
  const tip = mkTip(plot); let cfg = null, W = 0, st = null
  const draw = (anim) => {
    if (!cfg || !W) return
    const vis = cfg.series.filter((_, i) => !(cfg.hidden && cfg.hidden.has(i)))
    const max = Math.max(...vis.flatMap((s) => s.pts))
    const yf = cfg.yfmt || wan, sc = nice(max * (cfg.headroom || 1.04), 4)
    const lw = Math.max(...sc.ticks.map((t) => yf(t).length)) * 7 + 10
    const H = o.h || (W < 460 ? 220 : 260), m = { l: lw, r: 16, t: 14, b: 28 }, iw = W - m.l - m.r, ih = H - m.t - m.b
    const n = cfg.xs.length, X = (i) => m.l + (i * iw) / (n - 1), Y = (v) => m.t + ih - (v / sc.max) * ih
    const svg = SV('svg', { width: W, height: H, viewBox: `0 0 ${W} ${H}`, role: 'img', 'aria-label': cfg.label || '折线图', tabindex: 0 })
    svg.style.touchAction = 'pan-y'
    const defs = SV('defs'); svg.append(defs)
    sc.ticks.forEach((t) => { svg.append(SV('line', { class: t === 0 ? 'bl' : 'gl', x1: m.l, x2: W - m.r, y1: Y(t), y2: Y(t) })); svg.append(SV('text', { class: 'ax', x: m.l - 8, y: Y(t) + 4, 'text-anchor': 'end' }, yf(t))) })
    const step = Math.max(1, Math.ceil(58 / (iw / (n - 1))))
    for (let i = n - 1; i >= 0; i -= step) svg.append(SV('text', { class: 'ax', x: X(i), y: H - 6, 'text-anchor': i === 0 ? 'start' : i === n - 1 ? 'end' : 'middle' }, cfg.xs[i]))
    if (cfg.avg != null) {
      svg.append(SV('line', { x1: m.l, x2: W - m.r, y1: Y(cfg.avg), y2: Y(cfg.avg), stroke: 'var(--ink4)', 'stroke-width': 1, 'shape-rendering': 'crispEdges' }))
      svg.append(SV('text', { class: 'ax', x: W - m.r - 4, y: Y(cfg.avg) - 6, 'text-anchor': 'end' }, `均值 ${(cfg.vfmt || wan)(cfg.avg)}`))
    }
    const paths = []
    cfg.series.forEach((s, si) => {
      if (cfg.hidden && cfg.hidden.has(si)) return
      const P = s.pts.map((v, i) => [X(i), Y(v)]), d = curve(P)
      if (s.area) {
        const gid = 'g' + Math.random().toString(36).slice(2, 7)
        defs.append(SV('linearGradient', { id: gid, x1: 0, x2: 0, y1: 0, y2: 1 }, [SV('stop', { offset: '0%', style: `stop-color:${s.c};stop-opacity:.22` }), SV('stop', { offset: '100%', style: `stop-color:${s.c};stop-opacity:0` })]))
        const a = SV('path', { d: `${d}L${X(n - 1)},${Y(0)}L${X(0)},${Y(0)}Z`, fill: `url(#${gid})`, class: 'area' }); svg.append(a); paths.push(a)
      }
      const p = SV('path', { d, fill: 'none', style: `stroke:${s.c}`, 'stroke-width': 2, 'stroke-linejoin': 'round', 'stroke-linecap': 'round', class: 'ln' }); svg.append(p); paths.push(p)
    })
    const top = vis[0]
    if (top) { const li = top.pts.length - 1; svg.append(SV('circle', { cx: X(li), cy: Y(top.pts[li]), r: 4, style: `fill:${top.c}`, stroke: 'var(--card)', 'stroke-width': 2, class: 'end' })) }
    const marks = cfg.marks || (cfg.mark ? [cfg.mark] : [])
    if (top) marks.forEach((mk) => {
      const i = mk.i, px = X(i), py = Y(top.pts[i]), tw = mk.text.length * 7 + 14, below = mk.pos === 'below'
      const g = SV('g', { class: 'mk' })
      g.append(SV('circle', { cx: px, cy: py, r: 4, style: `fill:${top.c}`, stroke: 'var(--card)', 'stroke-width': 2 }))
      const bx = clamp(px - tw / 2, m.l, W - m.r - tw), by = below ? Math.min(H - 6 - 22, py + 12) : Math.max(0, py - 32)
      g.append(SV('rect', { x: bx, y: by, width: tw, height: 22, rx: 4, fill: 'var(--inv)' }))
      g.append(SV('text', { x: bx + tw / 2, y: by + 15, 'text-anchor': 'middle', style: 'font-size:12px;fill:#fff' }, mk.text))
      svg.append(g)
    })
    const cross = SV('line', { y1: m.t, y2: m.t + ih, stroke: 'var(--n9)', 'stroke-width': 1, visibility: 'hidden', 'shape-rendering': 'crispEdges' }); svg.append(cross)
    const dots = vis.map((s) => { const c = SV('circle', { r: 4, style: `fill:${s.c}`, stroke: 'var(--card)', 'stroke-width': 2, visibility: 'hidden' }); svg.append(c); return c })
    const hit = SV('rect', { x: m.l - 8, y: 0, width: iw + 16, height: H, fill: 'transparent' }); svg.append(hit)
    const show = (i) => {
      i = clamp(i, 0, n - 1); cross.setAttribute('x1', X(i)); cross.setAttribute('x2', X(i)); cross.setAttribute('visibility', 'visible')
      vis.forEach((s, k) => { dots[k].setAttribute('cx', X(i)); dots[k].setAttribute('cy', Y(s.pts[i])); dots[k].setAttribute('visibility', 'visible') })
      const vf = cfg.vfmt || wan
      tip.show(X(i), Y(vis[0].pts[i]), cfg.title(i), vis.map((s) => ({ c: s.c, k: 'ln', n: s.n, v: vf(s.pts[i]) })), cfg.foot ? cfg.foot(i) : '')
      st = i
    }
    const out = () => { cross.setAttribute('visibility', 'hidden'); dots.forEach((d) => d.setAttribute('visibility', 'hidden')); tip.hide(); st = null }
    const idx = (e) => { const r = svg.getBoundingClientRect(); return Math.round(((e.clientX - r.left) * (W / r.width) - m.l) / (iw / (n - 1))) }
    hit.addEventListener('pointermove', (e) => show(idx(e))); hit.addEventListener('pointerdown', (e) => show(idx(e))); hit.addEventListener('pointerleave', out)
    svg.addEventListener('keydown', (e) => { if (e.key === 'ArrowRight' || e.key === 'ArrowLeft') { e.preventDefault(); show((st == null ? (e.key === 'ArrowRight' ? -1 : n) : st) + (e.key === 'ArrowRight' ? 1 : -1)) } if (e.key === 'Escape') out() })
    svg.addEventListener('blur', out)
    const old = $(plot, 'svg'); if (old) old.remove(); plot.prepend(svg); tip.hide()
    if (anim && !matchMedia('(prefers-reduced-motion:reduce)').matches) {
      paths.forEach((p) => {
        if (p.classList.contains('ln')) { const L = p.getTotalLength(); p.style.strokeDasharray = L; p.style.strokeDashoffset = L; p.getBoundingClientRect(); p.style.transition = 'stroke-dashoffset .8s cubic-bezier(.2,0,0,1)'; p.style.strokeDashoffset = 0; setTimeout(() => { p.style.strokeDasharray = ''; p.style.transition = '' }, 850) }
        else { p.style.opacity = 0; p.getBoundingClientRect(); p.style.transition = 'opacity .8s'; p.style.opacity = 1 }
      })
    }
  }
  watch(plot, (w) => { W = w; draw(false) })
  return { set(c, anim = true) { cfg = c; draw(anim) } }
}

/* ==========================================================================
 * AD-DATA 数据展示
 * ========================================================================== */
/* ---- AD-DATA-001 基础统计卡 ---- */
def({
  id: 'AD-DATA-001', name: '基础统计卡', style: '趋势线',
  fit: '数据驾驶舱第一行：4 个核心指标，主数字 + 环比涨跌 + 迷你趋势线，页面级时间范围统一控制所有卡',
  avoid: '指标超过 6 个会挤；长期为 0 或几乎不变的指标别占卡位，合并成一行“暂无异常”；卡上不要再写与页面不一致的时间范围',
  kw: 'stat card 统计卡 指标卡 KPI 环比 涨跌 趋势线 sparkline 驾驶舱', stage: '', wide: true,
  css: `.addata001{width:1400px;max-width:100%}.addata001 *{box-sizing:border-box}.addata001 .tb{display:flex;align-items:center;justify-content:space-between;gap:12px;margin-bottom:12px}.addata001 .cap{font-size:12px;color:var(--ink3)}
${SEG_CSS('addata001')}${DL_CSS('addata001')}
.addata001 .row{display:grid;grid-template-columns:repeat(auto-fit,minmax(260px,1fr));gap:16px}
.addata001 .c{position:relative;height:110px;padding:14px 16px;${CARD};overflow:hidden}.addata001 .l{font-size:14px;line-height:20px;color:var(--ink2)}.addata001 .v{margin-top:2px;font-size:28px;line-height:36px;font-weight:700;white-space:nowrap}.addata001 .v small{font-size:16px;font-weight:600;margin:0 2px}.addata001 .d{display:flex;align-items:center;gap:6px;margin-top:4px;font-size:12px;line-height:20px;color:var(--ink3)}
.addata001 .sp{position:absolute;right:16px;bottom:14px;width:88px;height:40px}.addata001 .hv{position:absolute;right:14px;top:12px;padding:0 6px;border-radius:4px;background:var(--card);box-shadow:0 0 0 1px var(--n6);font-size:12px;line-height:20px;color:var(--ink2);font-variant-numeric:tabular-nums;pointer-events:none}`,
  html: () => `<div class="addata001"><div class="tb"><span class="cap">涨跌对比上一个等长周期</span>${segHTML([[7, '近 7 天'], [30, '近 30 天']])}</div><div class="row">${['sales', 'orders', 'conv', 'refund'].map((k) => `<div class="c" data-k="${k}"><div class="l">${MET[k].n}</div><div class="v"></div><div class="d"></div><div class="sp"></div><div class="hv" hidden></div></div>`).join('')}</div></div>`,
  js: (root) => {
    let days = 7
    const render = () => $$(root, '.c').forEach((c) => {
      const k = c.dataset.k, m = MET[k], r = calc(k, days), mt = $(c, '.hv')
      $(c, '.v').innerHTML = m.show(r.value); $(c, '.d').innerHTML = deltaHTML(r.delta, m.good, r.dunit) + '<span>环比</span>'
      spark($(c, '.sp'), r.pts, { label: m.n + '趋势', onHover: (i) => { mt.hidden = i < 0; if (i >= 0) mt.textContent = `${md(dayOf(i, days))} ${m.txt(r.pts[i])}` } })
    })
    bindSeg($(root, '.sg'), (v) => { days = +v; render() }); render()
  },
})

/* 环形进度：圆环 SVG 字符串 + 设置百分比（stroke-dashoffset 过渡） */
const ringHTML = (s, w, pct, tone = 'var(--p)', track = 'var(--pm)') => { const r = (s - w) / 2, c = 2 * Math.PI * r; return `<svg class="rg" width="${s}" height="${s}" viewBox="0 0 ${s} ${s}" role="img" aria-label="${pct}%"><circle cx="${s / 2}" cy="${s / 2}" r="${r}" fill="none" stroke-width="${w}" style="stroke:${track}"/><circle class="fg" cx="${s / 2}" cy="${s / 2}" r="${r}" fill="none" stroke-width="${w}" stroke-linecap="round" style="stroke:${tone}" stroke-dasharray="${c}" stroke-dashoffset="${c}" data-c="${c}" data-p="${pct}" transform="rotate(-90 ${s / 2} ${s / 2})"/></svg>` }
const ringTo = (fg, pct) => { fg.dataset.p = pct; fg.style.strokeDashoffset = +fg.dataset.c * (1 - clamp(pct, 0, 100) / 100) }
const RING_CSS = (p) => `.${p} .rg{display:block}.${p} .rg .fg{transition:stroke-dashoffset .8s cubic-bezier(.2,0,0,1),stroke .3s}`

/* ---- AD-DATA-002 统计卡样式集 ---- */
const YOY = { sales: 18.6, orders: 11.2 }
def({
  id: 'AD-DATA-002', name: '统计卡样式集', style: '六种形态',
  fit: '不同类型的指标选不同形态：带图标的结果指标、迷你柱、目标达成、待处理告警、双口径对比、环形达成率',
  avoid: '同一排混用超过 3 种形态会显乱；每张卡只放一个主数字，卡高不超过 112；不要把同一个事实在卡内说两遍',
  kw: 'stat card 统计卡 样式 目标达成 进度 告警 待处理 同比 环比', stage: '', wide: true,
  css: `.addata002{width:1400px;max-width:100%}.addata002 *{box-sizing:border-box}.addata002 .tb{display:flex;align-items:center;justify-content:space-between;gap:12px;margin-bottom:12px}.addata002 .cap{font-size:12px;color:var(--ink3)}
${SEG_CSS('addata002')}${DL_CSS('addata002')}${RING_CSS('addata002')}
.addata002 .gd{display:grid;grid-template-columns:repeat(auto-fit,minmax(340px,1fr));gap:16px}
.addata002 .c{position:relative;height:104px;padding:12px 16px;${CARD};display:flex;align-items:center;gap:12px;text-align:left;overflow:hidden;width:100%}.addata002 .bd{flex:1;min-width:0}
.addata002 .l{font-size:14px;line-height:20px;color:var(--ink2)}.addata002 .v{font-size:28px;line-height:36px;font-weight:700;white-space:nowrap}.addata002 .v small{font-size:16px;font-weight:600;margin:0 2px}.addata002 .d{display:flex;align-items:center;gap:6px;font-size:12px;line-height:20px;color:var(--ink3)}
.addata002 .ic{flex:none;width:44px;height:44px;border-radius:8px;background:var(--pt);color:var(--p-text);padding:10px}
.addata002 .mb{flex:none;display:flex;align-items:flex-end;gap:3px;height:44px}.addata002 .mb i{display:block;width:5px;border-radius:2px 2px 0 0;background:var(--pm);transition:background .15s,height .4s cubic-bezier(.2,0,0,1)}.addata002 .mb i:hover{background:var(--pd)}.addata002 .mb i.on{background:var(--p)}
.addata002 .c.g{flex-direction:column;align-items:stretch;justify-content:center;gap:0}.addata002 .g .r1{display:flex;justify-content:space-between;align-items:baseline;gap:8px}.addata002 .g .r1 span:last-child{font-size:12px;color:var(--ink3)}.addata002 .pb{height:6px;margin-top:6px;border-radius:3px;background:var(--pm);overflow:hidden}.addata002 .pb i{display:block;height:100%;width:0;border-radius:3px;background:var(--p);transition:width .8s cubic-bezier(.2,0,0,1)}
.addata002 .c.w{cursor:pointer;border-left:0;transition:box-shadow .15s,transform .15s}.addata002 .c.w::before{content:"";position:absolute;left:0;top:12px;bottom:12px;width:3px;border-radius:0 3px 3px 0;background:#C9A15B}.addata002 .c.w:hover{box-shadow:0 1px 2px var(--sh04),0 8px 24px var(--sh10)}.addata002 .c.w:active{transform:scale(.99)}
.addata002 .wt{display:inline-flex;align-items:center;gap:4px;height:20px;padding:0 6px;border-radius:4px;background:${WARNB};color:${WARNC};font-size:12px;font-weight:600}.addata002 .wt i{display:block;width:12px;height:12px}
.addata002 .two{flex:none;display:flex;flex-direction:column;gap:4px;align-items:flex-end}.addata002 .two div{display:flex;align-items:center;gap:6px;font-size:12px;color:var(--ink3);line-height:20px}
.addata002 .rgw{position:relative;flex:none;width:56px;height:56px}.addata002 .rgw b{position:absolute;inset:0;display:flex;align-items:center;justify-content:center;font-size:12px;font-weight:600}`,
  html: () => `<div class="addata002"><div class="tb"><span class="cap">涨跌对比口径可切换，其余指标按各自规则计算</span>${segHTML([['mom', '环比'], ['yoy', '同比']])}</div><div class="gd">
<div class="c a" data-k="sales"><span class="ic">${sv('wallet2')}</span><div class="bd"><div class="l">销售额</div><div class="v"></div><div class="d"></div></div></div>
<div class="c b" data-k="orders"><div class="bd"><div class="l">订单数</div><div class="v"></div><div class="d"></div></div><div class="mb" aria-label="近 12 天订单趋势"></div></div>
<div class="c g"><div class="r1"><span class="l">销售目标达成</span><span class="goal"></span></div><div class="r1"><span class="v"></span><span class="gap"></span></div><div class="pb"><i></i></div></div>
<button type="button" class="c w" data-toast="已筛选：超时未处理工单"><div class="bd"><div class="l">超时未处理工单</div><div class="v">18</div><div class="d"><span class="wt"><i>${sv('alert')}</i>需处理</span><span>较昨日 +4，最久已等 6 小时</span></div></div></button>
<div class="c e" data-k="aov"><div class="bd"><div class="l">客单价</div><div class="v"></div></div><div class="two"><div>同比 ${deltaHTML(6.8)}</div><div>环比 ${deltaHTML(-1.0)}</div></div></div>
<div class="c f" data-k="conv"><div class="bd"><div class="l">支付转化率</div><div class="v"></div><div class="d"></div></div><div class="rgw">${ringHTML(56, 6, 0)}<b></b></div></div>
</div></div>`,
  js: (root) => {
    let basis = 'mom'
    const dl = (k) => { const m = MET[k], r = calc(k, 30); return basis === 'yoy' ? deltaHTML(YOY[k], m.good) + '<span>同比</span>' : deltaHTML(r.delta, m.good, r.dunit) + '<span>环比</span>' }
    const fill = () => {
      ;['sales', 'orders'].forEach((k) => { const c = $(root, `.c[data-k="${k}"]`); $(c, '.v').innerHTML = MET[k].show(calc(k, 30).value); $(c, '.d').innerHTML = dl(k) })
      const mb = $(root, '.mb'), pts = MET.orders.d.slice(-12), mx = Math.max(...pts), mn = Math.min(...pts) * 0.8
      mb.innerHTML = pts.map((v, i) => `<i class="${i === 11 ? 'on' : ''}" style="height:0" data-h="${Math.round(((v - mn) / (mx - mn)) * 40 + 4)}" title="${md(dayOf(i, 12))}：${int(v)} 单"></i>`).join('')
      requestAnimationFrame(() => $$(mb, 'i').forEach((i) => (i.style.height = i.dataset.h + 'px')))
    }
    fill()
    const sales = calc('sales', 30).value, goal = Math.ceil(sales / 0.86 / 5000) * 5000, rate = (sales / goal) * 100
    $(root, '.goal').textContent = `目标 ¥${int(goal)}`; $(root, '.g .v').innerHTML = `${dec(rate, 1)}<small>%</small>`; $(root, '.gap').textContent = `还差 ¥${int(goal - sales)}`
    requestAnimationFrame(() => ($(root, '.pb i').style.width = rate + '%'))
    const aov = $(root, '.c.e'); $(aov, '.v').innerHTML = MET.aov.show(calc('aov', 30).value)
    const cv = $(root, '.c.f'), v = calc('conv', 30).value, target = 5.8
    $(cv, '.v').innerHTML = MET.conv.show(v); $(cv, '.d').textContent = `目标 ${dec(target, 1)}%，还差 ${dec(target - v, 2)} 个百分点`
    $(cv, '.rgw b').textContent = Math.round((v / target) * 100) + '%'; requestAnimationFrame(() => ringTo($(cv, '.fg'), (v / target) * 100))
    bindSeg($(root, '.sg'), (b) => { basis = b; ;['sales', 'orders'].forEach((k) => { $(root, `.c[data-k="${k}"] .d`).innerHTML = dl(k) }) })
  },
})

/* ---- AD-DATA-003 指标切换统计行 ---- */
def({
  id: 'AD-DATA-003', name: '指标切换统计行', style: '点选看趋势',
  fit: '分析型驾驶舱：5 个核心指标并排，点哪个下面的趋势图就换成哪个，本期与上期叠在一起看',
  avoid: '指标超过 6 个；每个指标的口径不同（金额与比率）时别叠在同一个坐标里；需要同屏对比多个指标时改用多张图',
  kw: '指标切换 统计行 tab 指标 趋势 折线 面积 分析 驾驶舱 对比上期', stage: '', wide: true,
  css: `.addata003{width:1400px;max-width:100%;${CARD};overflow:hidden;position:relative}.addata003 *{box-sizing:border-box}
${SEG_CSS('addata003')}${DL_CSS('addata003')}
.addata003 .its{display:grid;grid-template-columns:repeat(auto-fit,minmax(150px,1fr));border-bottom:1px solid var(--line)}.addata003 .it{position:relative;text-align:left;padding:16px 20px 14px;border-right:1px solid var(--line);border-bottom:2px solid transparent;margin-bottom:-1px;transition:background .15s}.addata003 .it:last-child{border-right:0}.addata003 .it:hover{background:var(--n1)}.addata003 .it.on{background:var(--lift);border-bottom-color:var(--p)}
.addata003 .it .l{display:block;font-size:14px;line-height:20px;color:var(--ink2)}.addata003 .it.on .l{color:var(--ink);font-weight:600}.addata003 .it .v{display:block;font-size:24px;line-height:34px;font-weight:700;white-space:nowrap}.addata003 .it .v small{font-size:14px;font-weight:600;margin:0 2px}.addata003 .it .d{display:flex;align-items:center;gap:6px;margin-top:2px;font-size:12px;line-height:20px;color:var(--ink3)}
.addata003 .bd{padding:18px 24px 14px}.addata003 .hd{display:flex;align-items:flex-start;justify-content:space-between;gap:8px 16px;flex-wrap:wrap}.addata003 .hd h4{margin:0;font-size:16px;line-height:24px;font-weight:600}.addata003 .hd p{margin:0;font-size:12px;line-height:20px;color:var(--ink3)}
.addata003 .lgd{display:flex;gap:2px 10px;margin-top:6px}.addata003 .lg{display:inline-flex;align-items:center;gap:6px;height:28px;padding:0 8px 0 6px;border-radius:8px;font-size:12px;color:var(--ink2)}.addata003 .lg:hover{background:var(--n3)}.addata003 .lg i{display:block;width:14px;height:3px;border-radius:2px;background:var(--c)}.addata003 .lg.off{color:var(--ink3)}.addata003 .lg.off i{background:var(--card);box-shadow:inset 0 0 0 1.5px var(--n9)}
.addata003 .plot{position:relative;margin-top:6px}.addata003 .plot svg{display:block;width:100%;overflow:visible;outline:none}
.addata003 .tip{position:absolute;z-index:5;pointer-events:none;min-width:136px;padding:8px 12px;border-radius:8px;background:var(--card2);box-shadow:0 0 0 1px var(--n6),0 8px 24px var(--sh14);font-size:12px;line-height:20px;white-space:nowrap}.addata003 .tip .t{display:block;font-weight:400;color:var(--ink3);margin-bottom:2px}.addata003 .tip .r{display:flex;align-items:center;gap:8px}.addata003 .tip .r i{display:block;flex:none;width:14px;height:3px;border-radius:2px;background:var(--c)}.addata003 .tip .r span{flex:1;color:var(--ink2)}.addata003 .tip .r b{margin-left:14px;font-weight:600;color:var(--ink);font-variant-numeric:tabular-nums}.addata003 .tip .ft{margin-top:4px;padding-top:4px;border-top:1px solid var(--line);color:var(--ink3)}
.addata003 .ax{font-size:12px;fill:var(--ink3)}.addata003 .gl{stroke:var(--n4);stroke-width:1;shape-rendering:crispEdges}.addata003 .bl{stroke:var(--n7);stroke-width:1;shape-rendering:crispEdges}
@media(max-width:520px){.addata003 .it{padding:12px 14px}.addata003 .bd{padding:14px 14px 10px}}@media(prefers-reduced-motion:reduce){.addata003 *{animation:none!important}}`,
  html: () => `<div class="addata003"><div class="its" role="tablist" aria-label="切换指标">${['sales', 'orders', 'uv', 'conv', 'aov'].map((k, i) => `<button type="button" class="it ${i === 0 ? 'on' : ''}" role="tab" aria-selected="${i === 0}" data-k="${k}"><span class="l">${MET[k].n}</span><span class="v"></span><span class="d"></span></button>`).join('')}</div>
<div class="bd"><div class="hd"><div><h4 class="ttl2"></h4><p class="sub2"></p></div>${segHTML([[7, '近 7 天'], [30, '近 30 天']])}</div>${lgHTML([{ n: '本期', c: 'var(--p)' }, { n: '上期', c: VZ_PREV }], 'ln')}<div class="plot"></div></div></div>`,
  js: (root) => {
    let k = 'sales', days = 7
    const line = mkLine($(root, '.plot'), { h: 240 }); let hid = new Set()
    const yfs = { sales: wan, orders: int, uv: wan, conv: (v) => dec(v, 1) + '%', aov: (v) => '¥' + int(v) }
    const tiles = () => $$(root, '.it').forEach((t) => { const r = calc(t.dataset.k, days), m = MET[t.dataset.k]; $(t, '.v').innerHTML = m.show(r.value); $(t, '.d').innerHTML = deltaHTML(r.delta, m.good, r.dunit) + '<span>环比</span>' })
    const chart = (anim) => {
      const m = MET[k], r = calc(k, days), N = m.d.length, prev = m.d.slice(N - 2 * days, N - days), top = r.pts.indexOf(Math.max(...r.pts))
      $(root, '.ttl2').textContent = `${m.n}近 ${days} 天${m.agg === 'sum' ? '累计 ' : '平均 '}${m.txt(r.value)}，较上期${r.delta >= 0 ? '上升' : '下降'} ${dec(Math.abs(r.delta), 1)}${r.dunit}`
      $(root, '.sub2').textContent = `${m.n}按日统计，灰线为上一个等长周期`
      line.set({ label: `${m.n}近 ${days} 天趋势`, xs: r.pts.map((_, i) => md(dayOf(i, days))), title: (i) => `${md(dayOf(i, days))} ${wk(dayOf(i, days))}`, hidden: hid, yfmt: yfs[k], vfmt: m.txt,
        series: [{ n: '本期', c: 'var(--p)', pts: r.pts, area: true }, { n: '上期', c: VZ_PREV, pts: prev }], mark: { i: top, text: `最高 ${m.txt(r.pts[top])}` },
        foot: (i) => `较上期 ${((r.pts[i] / prev[i] - 1) * 100 >= 0 ? '+' : '') + dec((r.pts[i] / prev[i] - 1) * 100, 1)}%` }, anim)
    }
    hid = bindLegend(root, () => chart(false))
    $$(root, '.it').forEach((t) => t.addEventListener('click', () => { k = t.dataset.k; $$(root, '.it').forEach((x) => { x.classList.toggle('on', x === t); x.setAttribute('aria-selected', x === t) }); chart(true) }))
    bindSeg($(root, '.sg'), (v) => { days = +v; tiles(); chart(true) }); tiles(); chart(false)
  },
})

const STT = (p) => `.${p} .stt{display:inline-flex;align-items:center;gap:4px;height:22px;padding:0 8px;border-radius:4px;font-size:12px;line-height:22px;font-weight:600;white-space:nowrap}.${p} .stt.ok{color:${OKC};background:${OKB}}.${p} .stt.warn{color:${WARNC};background:${WARNB}}.${p} .stt.bad{color:${BADC};background:${BADB}}.${p} .stt.info{color:var(--p-text);background:var(--pt)}.${p} .stt.mute{color:var(--ink2);background:var(--soft)}`
const copyTxt = (t) => { try { navigator.clipboard && navigator.clipboard.writeText(t).catch(() => {}) } catch (e) { /* 复制失败也给反馈，不阻塞 */ } }
const ICB = (p) => `.${p} .icb{display:inline-flex;align-items:center;justify-content:center;width:24px;height:24px;padding:4px;border-radius:8px;color:var(--ink3);vertical-align:middle;transition:background .15s,color .15s}.${p} .icb:hover{background:var(--soft);color:var(--ink)}.${p} .icb.done{color:${OKC}}`

/* ---- AD-DATA-004 描述列表 ---- */
def({
  id: 'AD-DATA-004', name: '描述列表', style: '两列三列',
  fit: '订单、客户、工单等详情页的“字段名 + 值”展示；两列和三列可切，长地址与备注占满一行，手机自动单列',
  avoid: '字段少于 4 个（直接写一句话）；需要编辑时改用表单；值是长文章时别塞进来，用单独的内容区',
  kw: 'descriptions 描述列表 详情 键值 key value 订单详情 字段 两列 三列', stage: '', wide: true,
  css: `.addata004{width:1400px;max-width:100%;${CARD};padding:20px 24px 8px}.addata004 *{box-sizing:border-box}
${SEG_CSS('addata004')}${STT('addata004')}${ICB('addata004')}
.addata004 .hd{display:flex;align-items:center;justify-content:space-between;gap:10px 16px;flex-wrap:wrap}.addata004 .hd h4{display:flex;align-items:center;gap:10px;margin:0;font-size:16px;line-height:24px;font-weight:600}.addata004 .ops{display:flex;align-items:center;gap:12px}.addata004 .lk2{height:32px;padding:0 4px;font-size:14px;color:var(--p-text);font-weight:600}.addata004 .lk2:hover{text-decoration:underline}
.addata004 .gd{--n:3;display:grid;grid-template-columns:repeat(var(--n),minmax(0,1fr));gap:0 40px;margin-top:8px}.addata004 .it{min-width:0;padding:12px 0;border-bottom:1px solid var(--line)}.addata004 .it.full{grid-column:1/-1}.addata004 .k{font-size:12px;line-height:20px;color:var(--ink3)}.addata004 .v{display:flex;align-items:center;gap:4px;font-size:14px;line-height:24px;color:var(--ink);word-break:break-all}.addata004 .v.t{display:block}.addata004 .v b{font-weight:600}.addata004 .v em{color:var(--ink3)}
@media(max-width:760px){.addata004 .gd{grid-template-columns:minmax(0,1fr)!important}.addata004 .sg{display:none}}`,
  html: () => `<div class="addata004"><div class="hd"><h4>订单信息<span class="stt info">配送中</span></h4><div class="ops">${segHTML([[2, '两列'], [3, '三列']], 1)}<button type="button" class="lk2" data-more aria-expanded="false">展开更多</button></div></div>
<div class="gd">
<div class="it"><div class="k">订单编号</div><div class="v"><span>SO2026110400128</span><button type="button" class="icb" data-copy="SO2026110400128" aria-label="复制订单编号">${sv('copy')}</button></div></div>
<div class="it"><div class="k">下单时间</div><div class="v">2026-11-04 09:17:32</div></div>
<div class="it"><div class="k">收货人</div><div class="v">林小满</div></div>
<div class="it"><div class="k">联系电话</div><div class="v"><span data-phone="13800005026">138****5026</span><button type="button" class="icb" data-eye aria-label="显示完整号码" aria-pressed="false">${sv('eye')}</button></div></div>
<div class="it"><div class="k">会员</div><div class="v">金卡会员<em>· 积分 2,860</em></div></div>
<div class="it"><div class="k">支付方式</div><div class="v">微信支付</div></div>
<div class="it"><div class="k">商品金额</div><div class="v">¥358.00</div></div>
<div class="it"><div class="k">优惠券</div><div class="v">满 300 减 30，已使用</div></div>
<div class="it"><div class="k">实付金额</div><div class="v"><b>¥328.00</b></div></div>
<div class="it full"><div class="k">收货地址</div><div class="v t">上海市浦东新区世纪大道 1001 号汇金中心 B 座 2208 室（请电话联系，放前台即可，不要放快递柜，谢谢）</div></div>
<div class="it full"><div class="k">订单备注</div><div class="v t">少放辣，发票请随货寄出；如果配送超时请先联系门店，不要直接取消订单。</div></div>
<div class="it ex" hidden><div class="k">发票</div><div class="v"><em>未开票</em></div></div>
<div class="it ex" hidden><div class="k">来源渠道</div><div class="v">小程序 · 首页横幅</div></div>
<div class="it ex" hidden><div class="k">履约门店</div><div class="v">徐汇旗舰店</div></div>
<div class="it ex" hidden><div class="k">配送方式</div><div class="v">门店配送，预计 12:30 前送达</div></div>
<div class="it ex" hidden><div class="k">客服备注</div><div class="v t">客户为第 3 次复购，已回访。</div></div>
<div class="it ex" hidden><div class="k">最近更新</div><div class="v">2026-11-04 10:48，客服 李安然</div></div>
</div></div>`,
  js: (root) => {
    const gd = $(root, '.gd')
    bindSeg($(root, '.sg'), (v) => gd.style.setProperty('--n', v))
    root.addEventListener('click', (e) => {
      const cp = e.target.closest('[data-copy]'), ey = e.target.closest('[data-eye]'), mo = e.target.closest('[data-more]')
      if (cp) { copyTxt(cp.dataset.copy); cp.innerHTML = sv('check'); cp.classList.add('done'); IX.toast(root, '已复制订单编号'); setTimeout(() => { cp.innerHTML = sv('copy'); cp.classList.remove('done') }, 1400) }
      if (ey) { const sp = $(root, '[data-phone]'), on = ey.getAttribute('aria-pressed') !== 'true'; ey.setAttribute('aria-pressed', on); ey.innerHTML = sv(on ? 'eyeoff' : 'eye'); ey.setAttribute('aria-label', on ? '隐藏号码' : '显示完整号码'); const p = sp.dataset.phone; sp.textContent = on ? p : p.slice(0, 3) + '****' + p.slice(7) }
      if (mo) { const open = mo.getAttribute('aria-expanded') !== 'true'; mo.setAttribute('aria-expanded', open); mo.textContent = open ? '收起' : '展开更多'; $$(root, '.ex').forEach((x) => (x.hidden = !open)) }
    })
  },
})

/* ---- AD-DATA-005 操作时间线 ---- */
const EVS = [
  { k: 'appr', who: 0, t: '李安然', a: '提交了退款申请', tm: '11-04 10:32', rows: [['退款金额', '¥328.00'], ['退款原因', '商品与描述不符：外壳有划痕，已拍照上传'], ['附件', '图片 2 张']] },
  { k: 'sys', ic: 'lock', t: '系统', a: '已冻结订单金额，暂停自动确认收货', tm: '11-04 10:32', rows: [['冻结金额', '¥328.00'], ['影响', '该订单的积分与成长值待退款结果确定后再发放']] },
  { k: 'appr', who: 1, t: '王子豪', a: '客服主管审批通过', tm: '11-04 10:45', rows: [['审批意见', '同意退款，按原路退回；请安排顾客寄回商品，运费由平台承担']] },
  { k: 'man', who: 2, t: '赵可心', a: '登记了退货物流', tm: '11-04 11:02', rows: [['物流公司', '顺丰速运'], ['运单号', 'SF1348820091'], ['当前状态', '快递员已揽收']] },
  { k: 'sys', ic: 'box', t: '系统', a: '仓库签收，质检通过', tm: '11-04 11:40', rows: [['质检结论', '商品完好，可二次销售'], ['入库仓', '上海徐汇仓']] },
  { k: 'sys', ic: 'checkc', t: '系统', a: '退款已原路退回微信支付', tm: '11-04 11:41', rows: [['到账金额', '¥328.00'], ['预计到账', '1–3 个工作日内，以支付渠道为准']] },
]
def({
  id: 'AD-DATA-005', name: '操作时间线', style: '可展开',
  fit: '订单、工单、审批的处理记录：谁在什么时间做了什么，点开看明细；按人工、系统、审批筛选',
  avoid: '记录超过 50 条时别全部渲染（分页或“加载更早”）；只有两三条状态的流程改用步骤条',
  kw: 'timeline 时间线 操作记录 日志 审批 流程 订单日志 展开 筛选 动态', stage: '', wide: false,
  css: `.addata005{width:1400px;max-width:100%;${CARD};padding:20px 24px 8px}.addata005 *{box-sizing:border-box}${STT('addata005')}
.addata005 .hd{display:flex;align-items:center;justify-content:space-between;gap:8px 16px;flex-wrap:wrap}.addata005 .hd h4{margin:0;font-size:16px;line-height:24px;font-weight:600}.addata005 .lk2{height:32px;padding:0 4px;font-size:14px;color:var(--p-text);font-weight:600}.addata005 .lk2:hover{text-decoration:underline}
.addata005 .tbs{display:flex;gap:4px;margin-top:8px;border-bottom:1px solid var(--line);overflow-x:auto;scrollbar-width:none}.addata005 .tbs button{flex:none;height:40px;padding:0 12px;font-size:14px;color:var(--ink2);border-bottom:2px solid transparent;margin-bottom:-1px;transition:color .15s}.addata005 .tbs button:hover{color:var(--ink)}.addata005 .tbs button.on{color:var(--ink);font-weight:600;border-bottom-color:var(--p)}.addata005 .tbs em{margin-left:4px;font-size:12px;color:var(--ink3);font-weight:400}
.addata005 .lst{list-style:none;margin:18px 0 0;padding:0}.addata005 .ev{position:relative;padding-left:44px}.addata005 .ev:not(:last-child)::before{content:"";position:absolute;left:13.5px;top:32px;bottom:-4px;width:1px;background:var(--n6)}
.addata005 .dt{position:absolute;left:0;top:0;width:28px;height:28px;border-radius:50%;display:flex;align-items:center;justify-content:center;background:var(--soft);color:var(--ink2)}.addata005 .dt i{display:block;width:16px;height:16px}.addata005 .ev.new .dt{background:var(--pt);color:var(--p-text)}
.addata005 .ev [data-h]{display:flex;align-items:flex-start;gap:12px;width:100%;min-height:28px;padding:3px 0 14px;text-align:left}.addata005 .ti{flex:1;min-width:0;font-size:14px;line-height:22px;color:var(--ink2)}.addata005 .ti b{color:var(--ink);font-weight:600;margin-right:6px}.addata005 .tm{flex:none;font-size:12px;line-height:22px;color:var(--ink3);font-variant-numeric:tabular-nums}.addata005 .chv{flex:none;display:block;width:16px;height:16px;margin-top:3px;color:var(--ink3);transition:transform .2s cubic-bezier(.2,0,0,1)}.addata005 .ev.open .chv{transform:rotate(180deg)}
.addata005 .dtl{margin:0 0 16px;padding:10px 14px;border-radius:8px;background:var(--n2)}.addata005 .dtl div{display:flex;gap:12px;padding:3px 0;font-size:14px;line-height:22px}.addata005 .dtl span{flex:none;width:72px;color:var(--ink3)}.addata005 .dtl p{margin:0;flex:1;min-width:0;color:var(--ink)}
@media(max-width:520px){.addata005{padding:16px 14px 4px}.addata005 .tm{display:none}}`,
  html: () => `<div class="addata005"><div class="hd"><h4>处理记录</h4><button type="button" class="lk2" data-all>全部展开</button></div>
<div class="tbs" data-ix="tabs" data-list=".addata005 .lst" role="tablist"><button type="button" class="on" role="tab" data-t="all">全部<em>${EVS.length}</em></button><button type="button" role="tab" data-t="man">人工<em>${EVS.filter((x) => x.k === 'man').length}</em></button><button type="button" role="tab" data-t="appr">审批<em>${EVS.filter((x) => x.k === 'appr').length}</em></button><button type="button" role="tab" data-t="sys">系统<em>${EVS.filter((x) => x.k === 'sys').length}</em></button></div>
<ol class="lst" data-ix="acc">${EVS.map((v, i) => `<li class="ev ix-ai ${i === 0 ? 'new' : ''}" data-k="${v.k}"><span class="dt">${v.who !== undefined ? critter(v.who, 28) : `<i>${sv(v.ic)}</i>`}</span><button type="button" data-h aria-label="展开明细"><span class="ti"><b>${v.t}</b>${v.a}</span><span class="tm">${v.tm}</span><i class="chv">${sv('down')}</i></button><div class="ix-ab"><div><div class="dtl">${v.rows.map(([a, b]) => `<div><span>${a}</span><p>${b}</p></div>`).join('')}</div></div></div></li>`).join('')}</ol></div>`,
  js: (root) => {
    const lst = $(root, '.lst'), btn = $(root, '[data-all]')
    /* 展开类名：ix 只切 .open 在 .ix-ai 上，这里同步按钮文案；全部展开/收起只作用于当前可见项 */
    const sync = () => { const vis = $$(lst, '.ev').filter((x) => !x.hidden); btn.textContent = vis.length && vis.every((x) => x.classList.contains('open')) ? '全部收起' : '全部展开' }
    btn.addEventListener('click', () => { const vis = $$(lst, '.ev').filter((x) => !x.hidden), all = vis.every((x) => x.classList.contains('open')); vis.forEach((x) => x.classList.toggle('open', !all)); sync() })
    root.addEventListener('click', () => setTimeout(sync, 0))
  },
})

/* ---- AD-DATA-006 状态标签与徽标集 ---- */
const TONES = [['ok', '已完成'], ['warn', '待付款'], ['bad', '退款中'], ['info', '配送中'], ['mute', '已取消']]
const TCOL = { ok: OKC, warn: WARNC, bad: BADC, info: 'var(--p-text)', mute: 'var(--ink3)' }
const COND = ['门店：徐汇旗舰店', '状态：待发货', '下单时间：近 7 天', '渠道：小程序', '金额：200 元以上']
def({
  id: 'AD-DATA-006', name: '状态标签与徽标集', style: '低饱和',
  fit: '订单、工单、门店等对象的状态展示；顶栏消息数字徽标；已选筛选条件可关闭；多选标签',
  avoid: '一页出现超过 5 种状态色；不要只靠颜色区分状态，必须带文字；红点和数字徽标不要同时出现在一个入口上',
  kw: 'tag 状态标签 徽标 badge 红点 数字角标 标签 chip 可关闭 筛选条件', stage: '', wide: false,
  css: `.addata006{width:1400px;max-width:100%;${CARD};padding:12px 24px}.addata006 *{box-sizing:border-box}${STT('addata006')}
.addata006 .rw{display:grid;grid-template-columns:136px minmax(0,1fr);gap:8px 12px;align-items:center;padding:14px 0;border-bottom:1px solid var(--line)}.addata006 .rw:last-child{border-bottom:0}.addata006 .k{font-size:12px;line-height:20px;color:var(--ink3)}.addata006 .vs{display:flex;flex-wrap:wrap;align-items:center;gap:8px 10px;min-width:0}
.addata006 .dot{display:inline-flex;align-items:center;gap:6px;font-size:14px;line-height:22px;color:var(--ink)}.addata006 .dot::before{content:"";width:8px;height:8px;border-radius:50%;background:var(--c)}
.addata006 .ol{display:inline-flex;align-items:center;height:22px;padding:0 8px;border-radius:4px;font-size:12px;line-height:20px;font-weight:600;color:var(--c);box-shadow:inset 0 0 0 1px currentColor;background:var(--card)}
.addata006 .bd{position:relative;display:inline-flex;align-items:center;justify-content:center;width:40px;height:40px;padding:8px;border-radius:8px;color:var(--ink2);transition:background .15s}.addata006 .bd:hover{background:var(--soft);color:var(--ink)}.addata006 .bd svg{display:block}.addata006 .bd .n{position:absolute;right:0;top:0;min-width:18px;height:18px;padding:0 5px;border-radius:9px;background:#B8584E;color:#fff;font-size:12px;line-height:18px;font-weight:600;text-align:center;box-shadow:0 0 0 2px var(--card);transition:transform .2s cubic-bezier(.2,0,0,1)}.addata006 .bd .n.pop{transform:scale(1.2)}.addata006 .bd .p{position:absolute;right:6px;top:6px;width:10px;height:10px;border-radius:50%;background:#B8584E;box-shadow:0 0 0 2px var(--card)}
.addata006 .btn2{height:32px;padding:0 12px;border-radius:8px;font-size:14px;color:var(--ink2);background:var(--soft);transition:background .15s}.addata006 .btn2:hover{background:var(--n5)}
.addata006 .cd{display:inline-flex;align-items:center;gap:4px;height:28px;padding:0 4px 0 10px;border-radius:8px;background:var(--soft);font-size:14px;color:var(--ink);transition:opacity .2s,transform .2s}.addata006 .cd.out{opacity:0;transform:scale(.9)}.addata006 .cd button{width:20px;height:20px;padding:3px;border-radius:4px;color:var(--ink3)}.addata006 .cd button:hover{background:var(--n6);color:var(--ink)}
.addata006 .cp{height:32px;padding:0 12px;border-radius:8px;font-size:14px;color:var(--ink2);box-shadow:inset 0 0 0 1px var(--n7);background:var(--card);transition:background .15s,color .15s,box-shadow .15s}.addata006 .cp:hover{background:var(--n2)}.addata006 .cp.on{background:var(--pt);color:var(--p-text);box-shadow:inset 0 0 0 1px var(--p);font-weight:600}
.addata006 .hint2{font-size:12px;color:var(--ink3)}.addata006 .lk2{height:28px;padding:0 4px;font-size:14px;color:var(--p-text);font-weight:600}.addata006 .lk2:hover{text-decoration:underline}
@media(max-width:560px){.addata006{padding:8px 14px}.addata006 .rw{grid-template-columns:1fr}}`,
  html: () => `<div class="addata006">
<div class="rw"><div class="k">状态标签 · 浅底</div><div class="vs">${TONES.map(([t, n]) => `<span class="stt ${t}">${n}</span>`).join('')}</div></div>
<div class="rw"><div class="k">状态标签 · 圆点</div><div class="vs">${TONES.map(([t, n]) => `<span class="dot" style="--c:${TCOL[t]}">${n}</span>`).join('')}</div></div>
<div class="rw"><div class="k">状态标签 · 描边</div><div class="vs">${TONES.map(([t, n]) => `<span class="ol" style="--c:${TCOL[t]}">${n}</span>`).join('')}</div></div>
<div class="rw"><div class="k">数字徽标 · 点击已读</div><div class="vs"><button type="button" class="bd" data-bd="8" aria-label="通知">${sv('bell')}<span class="n">8</span></button><button type="button" class="bd" data-bd="126" aria-label="购物车">${sv('cart')}<span class="n">99+</span></button><button type="button" class="bd" data-bd="1" aria-label="私信">${sv('chat')}<span class="p"></span></button><button type="button" class="btn2" data-newmsg>模拟一条新通知</button></div></div>
<div class="rw"><div class="k">可关闭标签</div><div class="vs" data-conds>${COND.slice(0, 3).map((c) => `<span class="cd">${c}<button type="button" aria-label="移除条件" data-rm>${sv('close')}</button></span>`).join('')}<button type="button" class="lk2" data-addc>+ 添加条件</button><button type="button" class="lk2" data-clr>清除全部</button></div></div>
<div class="rw"><div class="k">可选标签（多选）</div><div class="vs" data-sel>${['新客', '老客', '高价值', '沉睡', '储值会员', '企业客户'].map((c, i) => `<button type="button" class="cp ${i === 0 || i === 2 ? 'on' : ''}" aria-pressed="${i === 0 || i === 2}">${c}</button>`).join('')}<span class="hint2" data-selc></span></div></div>
</div>`,
  js: (root) => {
    const conds = $(root, '[data-conds]'), addB = $(root, '[data-addc]'), clrB = $(root, '[data-clr]'), selc = $(root, '[data-selc]'), sel = $(root, '[data-sel]')
    const cnt = () => $$(conds, '.cd').length
    const refresh = () => { addB.hidden = cnt() >= COND.length; clrB.hidden = cnt() === 0; $$(root, '[data-empty]').forEach((x) => x.remove()); if (!cnt()) { const s = document.createElement('span'); s.className = 'hint2'; s.dataset.empty = ''; s.textContent = '未设置筛选条件'; conds.prepend(s) } }
    const selSync = () => { const n = $$(sel, '.cp.on').length; selc.textContent = n ? `已选 ${n} 项` : '未选择，显示全部' }
    refresh(); selSync()
    root.addEventListener('click', (e) => {
      const rm = e.target.closest('[data-rm]'), cp = e.target.closest('.cp'), bd = e.target.closest('[data-bd]')
      if (rm) { const c = rm.closest('.cd'); c.classList.add('out'); setTimeout(() => { c.remove(); refresh() }, 180) }
      if (e.target.closest('[data-addc]')) { const have = $$(conds, '.cd').map((x) => x.firstChild.textContent), next = COND.find((c) => !have.includes(c)); if (next) { const s = document.createElement('span'); s.className = 'cd'; s.innerHTML = `<span></span><button type="button" aria-label="移除条件" data-rm>${sv('close')}</button>`; s.firstChild.textContent = next; conds.insertBefore(s, addB); refresh() } }
      if (e.target.closest('[data-clr]')) { $$(conds, '.cd').forEach((c) => c.remove()); refresh(); IX.toast(root, '已清除全部筛选条件') }
      if (cp) { cp.classList.toggle('on'); cp.setAttribute('aria-pressed', cp.classList.contains('on')); selSync() }
      if (bd) { const n = $(bd, '.n'), p = $(bd, '.p'); if (n) { n.remove() } if (p) p.remove(); bd.dataset.bd = 0; IX.toast(root, '已全部标为已读') }
      if (e.target.closest('[data-newmsg]')) { const b = $$(root, '[data-bd]')[0]; let n = $(b, '.n'); if (!n) { n = document.createElement('span'); n.className = 'n'; n.textContent = '0'; b.append(n) } const v = +n.textContent + 1; n.textContent = v > 99 ? '99+' : v; n.classList.add('pop'); setTimeout(() => n.classList.remove('pop'), 200) }
    })
  },
})

/* ---- AD-DATA-007 排行榜 ---- */
const RK = {
  store: [['徐汇旗舰店', 286400, 7820, 2], ['静安嘉里店', 241800, 6340, 0], ['浦东陆家嘴店', 233500, 6910, -1], ['虹桥万科店', 187200, 4880, 1], ['杨浦五角场店', 164900, 4420, -2], ['闵行七宝店', 142300, 3760, 0], ['长宁中山公园店', 118600, 3190, 1], ['普陀长风大悦城购物中心旗舰体验店', 96700, 2540, -1]],
  goods: [['无线降噪耳机', 198500, 331, 1], ['轻量跑鞋', 164800, 501, 0], ['机械腕表', 152100, 169, 3], ['双肩背包', 118400, 297, -1], ['保湿精华', 96700, 373, 0], ['护眼台灯', 81200, 371, -2], ['保温水杯', 64300, 722, 1], ['陶瓷马克杯', 38600, 654, 0]],
}
def({
  id: 'AD-DATA-007', name: '排行榜', style: '条形占比',
  fit: '门店、商品、渠道的排名：名次、名称、数值与占比一眼看清；可按销售额或订单数重排，前 5 名之外折叠',
  avoid: '类别少于 3 个（直接写数字）；名次相差极小且需要精确比较时改用带坐标轴的条形图；榜单超过 20 条改用表格',
  kw: 'rank 排行榜 排名 TOP 条形图 占比 门店排行 商品排行 销售排行 榜单', stage: '', wide: false,
  css: `.addata007{width:1400px;max-width:100%;${CARD};padding:20px 24px 12px}.addata007 *{box-sizing:border-box}${SEG_CSS('addata007')}
.addata007 .hd{display:flex;align-items:center;justify-content:space-between;gap:8px 16px;flex-wrap:wrap}.addata007 .hd h4{margin:0;font-size:16px;line-height:24px;font-weight:600}.addata007 .hd p{margin:0;font-size:12px;line-height:20px;color:var(--ink3)}.addata007 .ctl{display:flex;gap:10px;flex-wrap:wrap}
.addata007 .rk{position:relative;margin-top:12px;overflow:hidden;transition:height .35s cubic-bezier(.2,0,0,1)}.addata007 .ro{position:absolute;left:0;right:0;top:0;height:52px;padding:6px 8px;border-radius:8px;cursor:pointer;transition:transform .4s cubic-bezier(.2,0,0,1),background .15s,opacity .25s}.addata007 .ro:hover{background:var(--n2)}.addata007 .ro[hidden]{display:block!important;opacity:0;pointer-events:none;visibility:hidden}
.addata007 .l1{display:flex;align-items:center;gap:10px;height:24px}.addata007 .nb{flex:none;width:22px;height:22px;border-radius:4px;font-size:12px;line-height:22px;font-weight:600;text-align:center;color:var(--ink3);font-variant-numeric:tabular-nums}.addata007 .ro.top1 .nb{background:var(--p);color:#fff}.addata007 .ro.top2 .nb{background:var(--pm);color:var(--p-text)}.addata007 .ro.top3 .nb{background:var(--pt);color:var(--p-text)}
.addata007 .nm{flex:1;min-width:0;font-size:14px;color:var(--ink);overflow:hidden;text-overflow:ellipsis;white-space:nowrap}.addata007 .mv{flex:none;display:inline-flex;align-items:center;font-size:12px;color:var(--ink3)}.addata007 .mv i{display:block;width:12px;height:12px}.addata007 .mv.up{color:${OKC}}.addata007 .mv.dn{color:${BADC}}
.addata007 .vl{flex:none;font-size:14px;font-weight:600;font-variant-numeric:tabular-nums}.addata007 .sh{flex:none;width:44px;text-align:right;font-size:12px;color:var(--ink3);font-variant-numeric:tabular-nums}
.addata007 .tr{margin:4px 0 0 32px;height:6px;border-radius:3px;background:var(--soft);overflow:hidden}.addata007 .tr i{display:block;height:100%;width:0;border-radius:3px;background:var(--p);transition:width .6s cubic-bezier(.2,0,0,1)}
.addata007 .ft2{display:flex;justify-content:center;margin-top:4px}.addata007 .lk2{height:32px;padding:0 12px;font-size:14px;color:var(--p-text);font-weight:600;border-radius:8px}.addata007 .lk2:hover{background:var(--n2)}
@media(max-width:520px){.addata007{padding:16px 14px 8px}.addata007 .sh{display:none}}`,
  html: () => `<div class="addata007"><div class="hd"><div><h4>销售额集中在前三家门店</h4><p class="sub">按销售额排序，占比为占全部的比例</p></div><div class="ctl">${segHTML([['store', '门店'], ['goods', '商品']])}${segHTML([['s', '销售额'], ['o', '订单数']])}</div></div><div class="rk" role="list"></div><div class="ft2"><button type="button" class="lk2" data-fold aria-expanded="false">展开全部 8 项</button></div></div>`,
  js: (root) => {
    let dim = 'store', met = 's', open = false
    const rk = $(root, '.rk'), H = 52, segs = $$(root, '.sg')
    const val = (r) => (met === 's' ? r[1] : r[2]), fmt = (v) => (met === 's' ? '¥' + int(v) : int(v) + (dim === 'store' ? ' 单' : ' 件'))
    const build = () => {
      rk.innerHTML = RK[dim].map((r, i) => `<div class="ro" role="listitem" data-n="${r[0]}"><div class="l1"><span class="nb"></span><span class="nm" title="${r[0]}">${r[0]}</span><span class="mv"></span><span class="vl"></span><span class="sh"></span></div><div class="tr"><i></i></div></div>`).join('')
      $$(rk, '.ro').forEach((el, i) => { el.__d = RK[dim][i]; el.dataset.toast = `已打开「${RK[dim][i][0]}」经营明细` })
    }
    const place = () => {
      const rows = $$(rk, '.ro').sort((a, b) => val(b.__d) - val(a.__d)), tot = RK[dim].reduce((s, r) => s + val(r), 0), mx = val(rows[0].__d), lim = open ? rows.length : 5
      rows.forEach((el, i) => {
        const d = el.__d, mv = d[3]
        el.style.transform = `translateY(${i * H}px)`; el.hidden = i >= lim; el.className = `ro ${i < 3 ? 'top' + (i + 1) : ''}`
        $(el, '.nb').textContent = i + 1; $(el, '.vl').textContent = fmt(val(d)); $(el, '.sh').textContent = dec((val(d) / tot) * 100, 1) + '%'
        $(el, '.mv').className = 'mv ' + (mv > 0 ? 'up' : mv < 0 ? 'dn' : ''); $(el, '.mv').innerHTML = mv ? `<i>${sv(mv > 0 ? 'arrowup' : 'arrowdown')}</i>${Math.abs(mv)}` : ''
        $(el, '.tr i').style.width = (val(d) / mx) * 100 + '%'
      })
      rk.style.height = lim * H + 'px'
      const top3 = rows.slice(0, 3).reduce((s, r) => s + val(r.__d), 0) / tot * 100, nm = dim === 'store' ? '门店' : '商品'
      $(root, 'h4').textContent = `前三${dim === 'store' ? '家' : '款'}${nm}贡献了 ${dec(top3, 0)}% 的${met === 's' ? '销售额' : '订单数'}`
      $(root, '.sub').textContent = `按${met === 's' ? '销售额' : '订单数'}排序，名次旁的箭头为与上期相比的名次变化`
      $(root, '[data-fold]').textContent = open ? '收起' : `展开全部 ${rows.length} 项`
    }
    build(); place(); requestAnimationFrame(() => requestAnimationFrame(place))
    bindSeg(segs[0], (v) => { dim = v; build(); place(); requestAnimationFrame(() => requestAnimationFrame(place)) })
    bindSeg(segs[1], (v) => { met = v; place() })
    $(root, '[data-fold]').addEventListener('click', (e) => { open = !open; e.currentTarget.setAttribute('aria-expanded', open); place() })
  },
})
/* 相对容器的指针位置（滚动或缩放时都准） */
const relPos = (host, e) => { const r = host.getBoundingClientRect(); return [e.clientX - r.left, e.clientY - r.top] }

/* ---- AD-DATA-008 环形进度与进度条 ---- */
const SEV = { ok: ['var(--p)', 'var(--pm)'], warn: ['#C9A15B', 'var(--tint-f3e9d2)'], bad: ['#C0675E', 'var(--tint-f2dad7)'] }
const sevOf = (p) => (p >= 90 ? 'bad' : p >= 70 ? 'warn' : 'ok')
const SEVT = { ok: ['checkc', '正常'], warn: ['alert', '偏高'], bad: ['alert', '告急'] }
const METERS = [['存储空间', 500, 362, 'GB'], ['接口调用配额', 200, 76, '万次'], ['带宽峰值', 100, 91, 'Mbps'], ['短信套餐', 5000, 4200, '条']]
const GOALS = [['销售目标达成', 84.4, '目标 100%'], ['订单履约率', 96.2, '目标 98%'], ['会员复购率', 38.5, '目标 40%']]
def({
  id: 'AD-DATA-008', name: '环形进度与进度条', style: '点击演示',
  fit: '目标达成用环形（一个主数字）；资源用量用线性进度条（按阈值变色并写状态文字）；多步流程用分段条',
  avoid: '用量类指标不要用绿色代表“满”；只靠颜色表达状态（要有文字和图标）；一页超过 6 个环',
  kw: 'progress 进度条 环形进度 圆环 用量 配额 阈值 达成率 分段进度 meter', stage: '', wide: false,
  css: `.addata008{width:1400px;max-width:100%;${CARD};padding:20px 24px 18px}.addata008 *{box-sizing:border-box}${STT('addata008')}${RING_CSS('addata008')}
.addata008 .hd{display:flex;align-items:center;justify-content:space-between;gap:8px 16px;flex-wrap:wrap}.addata008 .hd h4{margin:0;font-size:16px;line-height:24px;font-weight:600}.addata008 .hd p{margin:0;font-size:12px;line-height:20px;color:var(--ink3)}.addata008 .btn2{height:32px;padding:0 14px;border-radius:8px;font-size:14px;font-weight:600;color:var(--p-text);background:var(--pt);transition:background .15s}.addata008 .btn2:hover{background:var(--pm)}
.addata008 .rgs{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:12px;margin-top:16px;padding:16px 0 18px;border-bottom:1px solid var(--line)}.addata008 .rgi{display:flex;flex-direction:column;align-items:center;gap:8px;text-align:center}.addata008 .rgw{position:relative;width:96px;height:96px}.addata008 .rgw svg{width:100%;height:100%}.addata008 .rgw b{position:absolute;inset:0;display:flex;align-items:center;justify-content:center;font-size:22px;font-weight:700}.addata008 .rgw b small{font-size:12px;font-weight:600;margin-left:1px}.addata008 .rgi .n{font-size:14px;line-height:20px;color:var(--ink)}.addata008 .rgi .t{font-size:12px;line-height:18px;color:var(--ink3)}
.addata008 .ms{padding-top:6px}.addata008 .mr{padding:12px 0}.addata008 .l1{display:flex;align-items:center;gap:10px;min-height:22px}.addata008 .nm{flex:1;min-width:0;font-size:14px;color:var(--ink)}.addata008 .us{flex:none;font-size:12px;color:var(--ink3);font-variant-numeric:tabular-nums}.addata008 .pc{flex:none;width:40px;text-align:right;font-size:14px;font-weight:600;font-variant-numeric:tabular-nums}.addata008 .stt i{display:block;width:12px;height:12px}
.addata008 .trk{height:8px;margin-top:8px;border-radius:4px;overflow:hidden;transition:background .3s}.addata008 .trk i{display:block;height:100%;width:0;border-radius:4px;transition:width .8s cubic-bezier(.2,0,0,1),background .3s}
.addata008 .sgs{display:flex;gap:4px;margin-top:8px}.addata008 .sgs i{flex:1;height:8px;border-radius:4px;background:var(--pm);transition:background .3s}.addata008 .sgs i.on{background:var(--p)}
@media(max-width:520px){.addata008{padding:16px 14px}.addata008 .rgw{width:76px;height:76px}.addata008 .rgw b{font-size:18px;font-weight:600}.addata008 .mr:not(.stp) .us{display:none}}`,
  html: () => `<div class="addata008"><div class="hd"><div><h4>资源用量与目标达成</h4><p class="sub">点“模拟变化”看数值、颜色与状态怎样随阈值切换</p></div><button type="button" class="btn2" data-sim>模拟数据变化</button></div>
<div class="rgs">${GOALS.map(([n, v, t], i) => `<div class="rgi" data-i="${i}"><div class="rgw">${ringHTML(96, 10, 0)}<b><span class="num">0</span><small>%</small></b></div><div class="n">${n}</div><div class="t">${t}</div></div>`).join('')}</div>
<div class="ms">${METERS.map(([n, tot, v, u], i) => `<div class="mr ok" data-i="${i}"><div class="l1"><span class="nm">${n}</span><span class="us"></span><b class="pc"></b><span class="stt ok"></span></div><div class="trk"><i></i></div></div>`).join('')}
<div class="mr stp"><div class="l1"><span class="nm">审批进度</span><span class="us step-t"></span></div><div class="sgs">${[0, 1, 2, 3, 4].map(() => '<i></i>').join('')}</div></div></div></div>`,
  js: (root) => {
    const rings = $$(root, '.rgi'), mrs = $$(root, '.ms .mr:not(.stp)'), STEPS = ['提交申请', '部门审批', '财务复核', '总经理审批', '已完成']
    const cur = { g: GOALS.map((g) => g[1]), m: METERS.map((m) => m[2]), s: 2 }, num = (el, to) => { const from = +el.textContent || 0; tween(800, (p) => { el.textContent = dec(from + (to - from) * p, 1).replace(/\.0$/, '') }) }
    const paint = () => {
      rings.forEach((r, i) => { num($(r, '.num'), cur.g[i]); requestAnimationFrame(() => ringTo($(r, '.fg'), cur.g[i])) })
      mrs.forEach((r, i) => {
        const [n, tot, , u] = METERS[i], v = cur.m[i], p = (v / tot) * 100, k = sevOf(p), [ic, tx] = SEVT[k]
        r.className = 'mr ' + k; $(r, '.us').textContent = `已用 ${int(v)} / ${int(tot)} ${u}`; $(r, '.pc').textContent = Math.round(p) + '%'
        const t = $(r, '.stt'); t.className = 'stt ' + k; t.innerHTML = `<i>${sv(ic)}</i>${tx}`
        const trk = $(r, '.trk'); trk.style.background = SEV[k][1]; const f = $(trk, 'i'); f.style.background = SEV[k][0]; requestAnimationFrame(() => (f.style.width = p + '%'))
      })
      $$(root, '.sgs i').forEach((x, i) => x.classList.toggle('on', i <= cur.s)); $(root, '.step-t').textContent = `${cur.s + 1} / 5 · ${STEPS[cur.s]}`
    }
    paint()
    $(root, '[data-sim]').addEventListener('click', () => {
      cur.g = GOALS.map(() => Math.round((20 + Math.random() * 78) * 10) / 10); cur.m = METERS.map((m) => Math.round(m[1] * (0.2 + Math.random() * 0.78))); cur.s = Math.floor(Math.random() * 5); paint()
    })
  },
})

/* ---- AD-DATA-009 评论动态流 ---- */
const CMS = [
  { who: 1, n: '陈晓雨', r: '客服', tm: '10 分钟前', tx: '这单客户反馈包装有破损，已经拍照留证，建议走售后极速退款。@林小满 麻烦确认一下库存是否还够补发。', k: 'all me', un: 1, likes: 4, rp: [] },
  { who: 2, n: '王子豪', r: '运营', tm: '32 分钟前', tx: '双十一预热券已经配置好了，满 200 减 20，预计明早 9 点自动发放，大家看看文案有没有要改的。', k: 'all', un: 1, likes: 9, img: [0, 6], rp: [] },
  { who: 3, n: '李安然', r: '仓储', tm: '1 小时前', tx: '补发的耳机已出库，物流单号 SF1348820091，预计今天傍晚送达。', k: 'all', likes: 2, rp: [['陈晓雨', '收到，我通知客户。'], ['林小满', '辛苦了，到货后记得回访。']] },
  { who: 0, n: '赵可心', r: '财务', tm: '昨天 18:20', tx: '本月储值账户对账已完成，发现 3 笔退款金额与支付渠道流水存在差异（合计 ¥86.50），已整理成清单发到群里，请各门店店长在周五前核对后回复，逾期将按系统数据自动入账。', k: 'all', likes: 1, rp: [] },
]
const cmHTML = (c) => `<li class="cm ${c.un ? 'un' : ''}" data-k="${c.k}">${critter(c.who, 36)}<div class="mn"><div class="who"><b>${c.n}</b><span class="role">${c.r}</span><span class="tm">${c.tm}</span><i class="udot" title="未读"></i></div><p class="tx"></p>${c.img ? `<div class="ims">${c.img.map((p) => `<img src="${P(p)}" alt="">`).join('')}</div>` : ''}<div class="act"><button type="button" class="ab" data-ix="like" aria-label="点赞"><i class="ico2">${sv('heart')}</i><span data-n>${c.likes}</span></button><button type="button" class="ab" data-reply><i class="ico2">${sv('chat')}</i>回复</button>${c.rp.length ? `<button type="button" class="ab" data-fold aria-expanded="false">查看 ${c.rp.length} 条回复</button>` : ''}</div><div class="rps" hidden>${c.rp.map(([a]) => `<div class="rpi"><b>${a}</b><span class="rpt"></span></div>`).join('')}</div><form class="rpf" hidden><input type="text" maxlength="100" placeholder="回复 ${c.n}" aria-label="回复内容"><button type="submit" class="send" disabled>发送</button></form></div></li>`
def({
  id: 'AD-DATA-009', name: '评论动态流', style: '可回复',
  fit: '工单协作、订单备注、审批讨论：按时间倒序的评论流，支持点赞、折叠回复、@我与未读筛选',
  avoid: '需要强审计的操作记录（用操作时间线，评论可以删改而日志不能）；超过 100 条要分页或“加载更早”',
  kw: 'comment 评论 动态 feed 回复 点赞 协作 工单备注 未读 提及', stage: '', wide: false,
  css: `.addata009{width:1400px;max-width:100%;${CARD};padding:20px 24px 8px}.addata009 *{box-sizing:border-box}
.addata009 .cmp{display:flex;gap:12px;align-items:flex-start}.addata009 .cmp .box{flex:1;min-width:0}.addata009 textarea{display:block;width:100%;height:68px;padding:8px 12px;border:1px solid var(--n7);border-radius:8px;font:inherit;font-size:14px;line-height:22px;color:var(--ink);resize:none;outline:none;background:var(--card);transition:border-color .15s}.addata009 textarea:focus{border-color:var(--ink2);outline:none;box-shadow:none}.addata009 .bt{display:flex;align-items:center;justify-content:space-between;margin-top:8px;gap:8px}.addata009 .hn{font-size:12px;color:var(--ink3)}.addata009 .send{height:32px;padding:0 16px;border-radius:8px;background:var(--p);color:#fff;font-size:14px;font-weight:600;transition:opacity .15s,background .15s}.addata009 .send:disabled{background:var(--n6);color:var(--ink5);cursor:not-allowed}
.addata009 .tbs{display:flex;gap:4px;margin-top:14px;border-bottom:1px solid var(--line)}.addata009 .tbs button{flex:none;height:40px;padding:0 12px;font-size:14px;color:var(--ink2);border-bottom:2px solid transparent;margin-bottom:-1px}.addata009 .tbs button:hover{color:var(--ink)}.addata009 .tbs button.on{color:var(--ink);font-weight:600;border-bottom-color:var(--p)}.addata009 .tbs em{margin-left:4px;font-size:12px;color:var(--ink3);font-weight:400}
.addata009 .lst{list-style:none;margin:0;padding:0}.addata009 .cm{display:flex;gap:12px;padding:16px 0;border-bottom:1px solid var(--line);cursor:default}.addata009 .cm:last-child{border-bottom:0}.addata009 .cm .mn{flex:1;min-width:0}
.addata009 .who{display:flex;align-items:center;gap:8px;min-height:22px}.addata009 .who b{font-size:14px;font-weight:600}.addata009 .role{height:20px;padding:0 6px;border-radius:4px;background:var(--pt);color:var(--p-text);font-size:12px;line-height:20px;font-weight:600}.addata009 .tm{margin-left:auto;font-size:12px;color:var(--ink3)}.addata009 .udot{display:none;width:8px;height:8px;border-radius:50%;background:#B8584E}.addata009 .cm.un .udot{display:block}
.addata009 .tx{margin:4px 0 0;font-size:14px;line-height:22px;color:var(--ink);word-break:break-all}.addata009 .tx .at{color:var(--p-text);font-weight:600}.addata009 .ims{display:flex;gap:8px;margin-top:8px}.addata009 .ims img{width:72px;height:72px;border-radius:8px;object-fit:cover}
.addata009 .act{display:flex;align-items:center;gap:4px;margin-top:8px;margin-left:-8px}.addata009 .ab{display:inline-flex;align-items:center;gap:4px;height:28px;padding:0 8px;border-radius:8px;font-size:12px;color:var(--ink3);transition:background .15s,color .15s}.addata009 .ab:hover{background:var(--soft);color:var(--ink)}.addata009 .ab .ico2{display:block;width:16px;height:16px}.addata009 .ab.on{color:${BADC}}.addata009 .ab.on .ico2 svg{fill:currentColor}
.addata009 .rps{margin-top:8px;padding:8px 12px;border-radius:8px;background:var(--n2)}.addata009 .rpi{padding:4px 0;font-size:14px;line-height:22px}.addata009 .rpi b{margin-right:6px;font-weight:600}.addata009 .rpi .rpt{color:var(--ink2)}
.addata009 .rpf{display:flex;gap:8px;margin-top:8px}.addata009 .rpf input{flex:1;min-width:0;height:32px;padding:0 12px;border:1px solid var(--n7);border-radius:8px;font:inherit;font-size:14px;outline:none}.addata009 .rpf input:focus{border-color:var(--ink2)}
@media(max-width:520px){.addata009{padding:16px 14px 4px}.addata009 .tm{display:none}}`,
  html: () => `<div class="addata009"><div class="cmp">${critter(0, 36)}<div class="box"><textarea maxlength="200" placeholder="写点什么，输入 @ 可以提醒同事" aria-label="评论内容"></textarea><div class="bt"><span class="hn">还可输入 200 字</span><button type="button" class="send" disabled>发送</button></div></div></div>
<div class="tbs" data-ix="tabs" data-list=".addata009 .lst" role="tablist"><button type="button" class="on" role="tab" data-t="all">全部<em data-c="all">4</em></button><button type="button" role="tab" data-t="me">@我<em data-c="me">1</em></button><button type="button" role="tab" data-t="un">未读<em data-c="un">2</em></button></div>
<ul class="lst">${CMS.map(cmHTML).join('')}</ul></div>`,
  js: (root) => {
    const lst = $(root, '.lst'), ta = $(root, 'textarea'), send = $(root, '.cmp .send'), hn = $(root, '.hn')
    const fillText = (li, c) => { const p = $(li, '.tx'); p.textContent = c.tx; p.innerHTML = p.innerHTML.replace(/@[一-龥]{2,4}/g, (m) => `<span class="at">${m}</span>`); $$(li, '.rpt').forEach((s, i) => (s.textContent = c.rp[i][1])) }
    $$(lst, '.cm').forEach((li, i) => { fillText(li, CMS[i]); if (CMS[i].un) li.dataset.k += ' un' })
    const counts = () => { $$(root, '[data-c]').forEach((e) => { const k = e.dataset.c; e.textContent = $$(lst, '.cm').filter((li) => (li.dataset.k || '').split(' ').includes(k)).length }) }
    counts()
    ta.addEventListener('input', () => { send.disabled = ta.value.trim().length === 0; hn.textContent = `还可输入 ${200 - ta.value.length} 字` })
    send.addEventListener('click', () => {
      const t = ta.value.trim(); if (!t) return
      const c = { who: 0, n: '林小满', r: '我', tm: '刚刚', tx: t, k: 'all', likes: 0, rp: [] }, h = document.createElement('template'); h.innerHTML = cmHTML(c)
      const li = h.content.firstElementChild; fillText(li, c); lst.prepend(li); ta.value = ''; send.disabled = true; hn.textContent = '还可输入 200 字'; counts(); IX.toast(root, '已发送')
    })
    root.addEventListener('click', (e) => {
      const li = e.target.closest('.cm'); if (!li) return
      if (li.classList.contains('un') && !e.target.closest('input,form')) { li.classList.remove('un'); li.dataset.k = li.dataset.k.replace(' un', ''); counts() }
      const f = e.target.closest('[data-fold]'), r = e.target.closest('[data-reply]')
      if (f) { const box = $(li, '.rps'), open = box.hidden; box.hidden = !open; f.setAttribute('aria-expanded', open); f.textContent = open ? '收起回复' : `查看 ${$$(box, '.rpi').length} 条回复` }
      if (r) { const fm = $(li, '.rpf'); fm.hidden = !fm.hidden; if (!fm.hidden) $(fm, 'input').focus() }
    })
    root.addEventListener('input', (e) => { if (e.target.matches('.rpf input')) $(e.target.closest('.rpf'), '.send').disabled = !e.target.value.trim() })
    root.addEventListener('submit', (e) => {
      e.preventDefault(); const fm = e.target, inp = $(fm, 'input'), v = inp.value.trim(); if (!v) return
      const li = fm.closest('.cm'), box = $(li, '.rps'), d = document.createElement('div'); d.className = 'rpi'; d.innerHTML = '<b>林小满</b><span class="rpt"></span>'; $(d, '.rpt').textContent = v; box.append(d); box.hidden = false
      let fb = $(li, '[data-fold]'); if (!fb) { fb = document.createElement('button'); fb.type = 'button'; fb.className = 'ab'; fb.dataset.fold = ''; $(li, '.act').append(fb) } fb.textContent = '收起回复'; fb.setAttribute('aria-expanded', 'true')
      inp.value = ''; $(fm, '.send').disabled = true; fm.hidden = true; IX.toast(root, '回复已发送')
    })
  },
})

/* ---- AD-DATA-010 日历热力图 ---- */
const CAL = (() => {
  const r = rng(7), weeks = 52, end = new Date(2026, 10, 4), dow = (end.getDay() + 6) % 7, start = new Date(2026, 10, 4 - dow - (weeks - 1) * 7)
  const mk = (base, amp) => Array.from({ length: weeks * 7 }, (_, i) => {
    const d = new Date(start.getFullYear(), start.getMonth(), start.getDate() + i); if (d > end) return null
    const hol = d.getMonth() === 9 && d.getDate() <= 7 ? 1.6 : d.getMonth() === 5 && d.getDate() >= 12 && d.getDate() <= 18 ? 1.5 : 1, wkend = i % 7 >= 5 ? 1.18 : 1
    return Math.max(0, Math.round(base * hol * wkend * (1 + (0.35 * i) / (weeks * 7)) * (1 + amp * (r() * 2 - 1))))
  })
  return { start, weeks, o: mk(80, 0.35), a: mk(9, 0.55) }
})()
def({
  id: 'AD-DATA-010', name: '日历热力图', style: '贡献图样式',
  fit: '看长周期里哪些天活跃、哪些天冷清：订单、访客、工单按天一格，悬停看数，点选一天看与日均的对比',
  avoid: '数据少于 3 周；需要精确读数时（热力只表达高低，精确值放表格）；颜色不要超过 5 档',
  kw: 'calendar heatmap 日历热力图 贡献图 github 活跃度 按天 热度 日历 订单分布', stage: '', wide: true,
  css: `.addata010{width:1400px;max-width:100%;${CARD};padding:20px 24px 16px;position:relative}.addata010 *{box-sizing:border-box}${SEG_CSS('addata010')}
.addata010 .hd{display:flex;align-items:flex-start;justify-content:space-between;gap:8px 16px;flex-wrap:wrap}.addata010 .hd h4{margin:0;font-size:16px;line-height:24px;font-weight:600}.addata010 .hd p{margin:0;font-size:12px;line-height:20px;color:var(--ink3)}
.addata010 .plw{position:relative;margin-top:12px}.addata010 .scr{overflow-x:auto;scrollbar-width:thin}.addata010 .scr svg{display:block}.addata010 .ax{font-size:12px;fill:var(--ink3)}.addata010 .cell{cursor:pointer}
.addata010 .tip{position:absolute;z-index:5;pointer-events:none;min-width:136px;padding:8px 12px;border-radius:8px;background:var(--card2);box-shadow:0 0 0 1px var(--n6),0 8px 24px var(--sh14);font-size:12px;line-height:20px;white-space:nowrap}.addata010 .tip .t{display:block;font-weight:400;color:var(--ink3);margin-bottom:2px}.addata010 .tip .r{display:flex;align-items:center;gap:8px}.addata010 .tip .r span{flex:1;color:var(--ink2)}.addata010 .tip .r b{margin-left:14px;font-weight:600;color:var(--ink)}.addata010 .tip .ft{margin-top:4px;padding-top:4px;border-top:1px solid var(--line);color:var(--ink3)}
.addata010 .ft2{display:flex;align-items:center;justify-content:space-between;gap:12px 20px;flex-wrap:wrap;margin-top:12px;padding-top:12px;border-top:1px solid var(--line)}.addata010 .pick{font-size:14px;line-height:22px;color:var(--ink2)}.addata010 .pick b{color:var(--ink);font-weight:600}.addata010 .lgn{display:flex;align-items:center;gap:4px;font-size:12px;color:var(--ink3)}.addata010 .lgn i{display:block;width:12px;height:12px;border-radius:4px}
@media(max-width:520px){.addata010{padding:16px 14px 12px}}`,
  html: () => `<div class="addata010"><div class="hd"><div><h4 class="ttl2"></h4><p class="sub2">近 52 周，每格一天；颜色越深当天越多，点一格看详情</p></div>${segHTML([['o', '订单量'], ['a', '售后工单']])}</div><div class="plw"><div class="scr"></div></div><div class="ft2"><div class="pick"></div><div class="lgn">少<i style="background:var(--n4)"></i><i style="background:rgba(var(--p-rgb),.22)"></i><i style="background:rgba(var(--p-rgb),.42)"></i><i style="background:rgba(var(--p-rgb),.66)"></i><i style="background:rgba(var(--p-rgb),.9)"></i>多</div></div></div>`,
  js: (root) => {
    let met = 'o', sel = -1, W = 0
    const scr = $(root, '.scr'), plw = $(root, '.plw'), tip = mkTip(plw), unit = () => (met === 'o' ? '单' : '件'), nm = () => (met === 'o' ? '订单' : '售后工单')
    const FILL = ['#EEF0F3', 'rgba(var(--p-rgb),.22)', 'rgba(var(--p-rgb),.42)', 'rgba(var(--p-rgb),.66)', 'rgba(var(--p-rgb),.9)']
    const dateOf = (i) => new Date(CAL.start.getFullYear(), CAL.start.getMonth(), CAL.start.getDate() + i), ds = (d) => `${d.getFullYear()}-${md(d)}`
    const draw = () => {
      const data = CAL[met], vals = data.filter((v) => v != null), sorted = [...vals].sort((a, b) => a - b), q = (p) => sorted[Math.floor(p * (sorted.length - 1))]
      const cuts = [q(0.2), q(0.45), q(0.7), q(0.9)], lv = (v) => (v <= cuts[0] ? 0 : v <= cuts[1] ? 1 : v <= cuts[2] ? 2 : v <= cuts[3] ? 3 : 4), avg = vals.reduce((s, v) => s + v, 0) / vals.length
      const lw = 28, gp = 3, cs = clamp(Math.floor((W - lw) / CAL.weeks) - gp, 11, 26), w = lw + CAL.weeks * (cs + gp), h = 22 + 7 * (cs + gp)
      const svg = SV('svg', { width: w, height: h, viewBox: `0 0 ${w} ${h}`, role: 'img', 'aria-label': '日历热力图' })
      ;['一', '三', '五'].forEach((t, i) => svg.append(SV('text', { class: 'ax', x: 0, y: 22 + i * 2 * (cs + gp) + cs - 2 }, t)))
      for (let k = 0; k < CAL.weeks; k++) { const d = dateOf(k * 7); if ((k === 0 || d.getDate() <= 7) && lw + k * (cs + gp) < w - 40) svg.append(SV('text', { class: 'ax', x: lw + k * (cs + gp), y: 12 }, `${d.getMonth() + 1} 月`)) }
      const cells = []
      data.forEach((v, i) => {
        if (v == null) return
        const r = SV('rect', { x: lw + Math.floor(i / 7) * (cs + gp), y: 22 + (i % 7) * (cs + gp), width: cs, height: cs, rx: 4, class: 'cell', style: `fill:${FILL[lv(v)]}`, 'stroke-width': 1.5, stroke: 'none' }); r.dataset.i = i; svg.append(r); cells.push(r)
      })
      const pickEl = $(root, '.pick')
      const pick = (i) => {
        const v = data[i], d = dateOf(i), rank = sorted.length - sorted.lastIndexOf(v), diff = (v / avg - 1) * 100
        pickEl.innerHTML = '<b></b>'; $(pickEl, 'b').textContent = `${ds(d)} ${wk(d)}`; pickEl.append(` ${nm()} ${v} ${unit()}，${diff >= 0 ? '高于' : '低于'}日均 ${dec(Math.abs(diff), 0)}%，近一年第 ${rank} 高`)
        cells.forEach((c) => c.setAttribute('stroke', +c.dataset.i === i ? '#1F2329' : 'none')); sel = i
      }
      const top = data.indexOf(Math.max(...vals)); if (sel < 0 || data[sel] == null) sel = top
      pick(sel)
      svg.addEventListener('pointermove', (e) => { const c = e.target.closest('.cell'); if (!c) { tip.hide(); return } const i = +c.dataset.i, v = data[i], d = dateOf(i), [x, y] = relPos(plw, e); tip.show(x, y, `${ds(d)} ${wk(d)}`, [{ n: nm(), v: v + ' ' + unit() }], `${v >= avg ? '高于' : '低于'}日均 ${dec(Math.abs((v / avg - 1) * 100), 0)}%`) })
      svg.addEventListener('pointerleave', () => tip.hide()); svg.addEventListener('click', (e) => { const c = e.target.closest('.cell'); if (c) pick(+c.dataset.i) })
      scr.replaceChildren(svg); if (scr.scrollWidth > scr.clientWidth) scr.scrollLeft = scr.scrollWidth
      $(root, '.ttl2').textContent = `近一年${nm()}累计 ${int(vals.reduce((s, v) => s + v, 0))} ${unit()}，峰值在 ${ds(dateOf(top))}（${wk(dateOf(top))}）`
    }
    watch(scr, (w) => { W = w; draw() })
    bindSeg($(root, '.sg'), (v) => { met = v; sel = -1; draw() })
  },
})

/* ---- AD-DATA-011 键值信息面板 ---- */
const TGL = (p) => `.${p} .tgl{position:relative;flex:none;width:40px;height:22px;border-radius:11px;background:var(--n8);transition:background .2s}.${p} .tgl::after{content:"";position:absolute;left:2px;top:2px;width:18px;height:18px;border-radius:50%;background:var(--card);box-shadow:0 1px 3px var(--sh25);transition:transform .2s cubic-bezier(.2,0,0,1)}.${p} .tgl.on{background:var(--p)}.${p} .tgl.on::after{transform:translateX(18px)}.${p} .tgl.ld{opacity:.55;pointer-events:none}`
def({
  id: 'AD-DATA-011', name: '键值信息面板', style: '复制脱敏',
  fit: '应用凭证、实例配置、账户资料这类“字段 + 值 + 一两个动作”的信息：一键复制、密钥脱敏、行内开关即时生效',
  avoid: '字段超过 12 行（分组或改用描述列表）；密钥默认不要明文；开关失败时必须回滚并在原位写原因',
  kw: 'key value 键值 面板 凭证 密钥 复制 脱敏 开关 应用详情', stage: '', wide: false,
  css: `.addata011{width:1400px;max-width:100%;${CARD};padding:16px 24px 8px}.addata011 *{box-sizing:border-box}${STT('addata011')}${ICB('addata011')}${TGL('addata011')}
.addata011 .hd{display:flex;align-items:center;justify-content:space-between;gap:8px 16px;padding-bottom:12px;border-bottom:1px solid var(--line)}.addata011 .hd h4{display:flex;align-items:center;gap:10px;margin:0;font-size:16px;line-height:24px;font-weight:600}.addata011 .up{display:flex;align-items:center;gap:6px;font-size:12px;color:var(--ink3)}.addata011 .up .icb svg{transition:transform .6s cubic-bezier(.2,0,0,1)}.addata011 .up .icb.spin svg{transform:rotate(360deg)}
.addata011 .kr{display:grid;grid-template-columns:104px minmax(0,1fr) auto;align-items:center;gap:0 12px;min-height:48px;padding:6px 0;border-bottom:1px solid var(--line)}.addata011 .kr:last-child{border-bottom:0}.addata011 .k{font-size:14px;color:var(--ink3)}.addata011 .v{min-width:0;font-size:14px;line-height:22px;color:var(--ink);overflow:hidden;text-overflow:ellipsis;white-space:nowrap}.addata011 .v.mono{font-variant-numeric:tabular-nums}.addata011 .ac{display:flex;align-items:center;gap:2px}
.addata011 .why{margin:0;padding:0 0 8px 116px;font-size:12px;line-height:20px;color:${BADC}}
@media(max-width:520px){.addata011{padding:12px 14px 4px}.addata011 .kr{grid-template-columns:76px minmax(0,1fr) auto}.addata011 .why{padding-left:88px}}`,
  html: () => `<div class="addata011"><div class="hd"><h4>门店订单同步<span class="stt ok">已启用</span></h4><div class="up"><span class="ut">更新于 刚刚</span><button type="button" class="icb" data-refresh aria-label="刷新">${sv('refresh')}</button></div></div>
<div class="kr"><div class="k">应用编号</div><div class="v mono">ap_7f3a91c2e8</div><div class="ac"><button type="button" class="icb" data-copy="ap_7f3a91c2e8" aria-label="复制应用编号">${sv('copy')}</button></div></div>
<div class="kr"><div class="k">应用密钥</div><div class="v mono" data-secret="demo_secret_placeholder_0001">••••••••••••••••0001</div><div class="ac"><button type="button" class="icb" data-eye aria-pressed="false" aria-label="显示密钥">${sv('eye')}</button><button type="button" class="icb" data-copy="demo_secret_placeholder_0001" aria-label="复制密钥">${sv('copy')}</button></div></div>
<div class="kr"><div class="k">回调地址</div><div class="v" title="https://api.example.com/hooks/orders/v2/receive?store=all&amp;format=json">https://api.example.com/hooks/orders/v2/receive?store=all&amp;format=json</div><div class="ac"><button type="button" class="icb" data-copy="https://api.example.com/hooks/orders/v2/receive?store=all&amp;format=json" aria-label="复制回调地址">${sv('copy')}</button></div></div>
<div class="kr"><div class="k">创建时间</div><div class="v">2026-03-18 14:20</div><div class="ac"></div></div>
<div class="kr"><div class="k">到期时间</div><div class="v">2026-11-16</div><div class="ac"><span class="stt warn">剩余 12 天</span></div></div>
<div class="kr"><div class="k">自动续期</div><div class="v">到期前 7 天按套餐价自动续费</div><div class="ac"><button type="button" class="tgl on" role="switch" aria-checked="true" aria-label="自动续期" data-sw="renew"></button></div></div>
<div class="kr"><div class="k">限流保护</div><div class="v">单应用每秒最多 50 次调用</div><div class="ac"><button type="button" class="tgl" role="switch" aria-checked="false" aria-label="限流保护" data-sw="limit"></button></div></div>
<div class="kr"><div class="k">标签</div><div class="v"><span class="stt mute">订单</span> <span class="stt mute">门店</span> <span class="stt mute">同步</span></div><div class="ac"></div></div></div>`,
  js: (root) => {
    root.addEventListener('click', (e) => {
      const cp = e.target.closest('[data-copy]'), ey = e.target.closest('[data-eye]'), rf = e.target.closest('[data-refresh]'), sw = e.target.closest('[data-sw]')
      if (cp) { copyTxt(cp.dataset.copy); cp.innerHTML = sv('check'); cp.classList.add('done'); IX.toast(root, '已复制'); setTimeout(() => { cp.innerHTML = sv('copy'); cp.classList.remove('done') }, 1400) }
      if (ey) { const s = $(root, '[data-secret]'), on = ey.getAttribute('aria-pressed') !== 'true'; ey.setAttribute('aria-pressed', on); ey.innerHTML = sv(on ? 'eyeoff' : 'eye'); ey.setAttribute('aria-label', on ? '隐藏密钥' : '显示密钥'); s.textContent = on ? s.dataset.secret : '••••••••••••••••' + s.dataset.secret.slice(-4) }
      if (rf) { rf.classList.add('spin'); $(root, '.ut').textContent = '正在更新…'; setTimeout(() => { rf.classList.remove('spin'); $(root, '.ut').textContent = '更新于 刚刚' }, 700) }
      if (sw) {
        const row = sw.closest('.kr'), old = $(root, `.why[data-for="${sw.dataset.sw}"]`); if (old) old.remove()
        const to = !sw.classList.contains('on'); sw.classList.add('ld'); sw.classList.toggle('on', to); sw.setAttribute('aria-checked', to)
        setTimeout(() => {
          sw.classList.remove('ld')
          if (sw.dataset.sw === 'limit' && to) { sw.classList.remove('on'); sw.setAttribute('aria-checked', false); const p = document.createElement('p'); p.className = 'why'; p.dataset.for = 'limit'; p.textContent = '当前套餐不支持限流保护，请先升级套餐后再开启'; row.after(p) }
          else IX.toast(root, to ? '已开启，立即生效' : '已关闭，立即生效')
        }, 600)
      }
    })
  },
})

/* ---- AD-DATA-012 数据卡片集 ---- */
const STORES = [
  ['徐汇旗舰店', 'open', 0, '李安然', '徐汇区漕溪北路 331 号中金国际广场一层', 12860, 342, 4.8], ['静安嘉里店', 'open', 1, '陈晓雨', '静安区南京西路 1515 号嘉里中心负一层', 10420, 288, 4.7], ['浦东陆家嘴店', 'open', 2, '王子豪', '浦东新区陆家嘴环路 1000 号恒生银行大厦', 9980, 301, 4.6],
  ['虹桥万科店', 'rest', 3, '周一帆', '闵行区申虹路 666 弄虹桥万科中心', 0, 0, 4.5], ['杨浦五角场店', 'open', 0, '赵可心', '杨浦区国定路 335 号创智天地', 7650, 214, 4.7], ['闵行七宝店', 'prep', 1, '吴梓轩', '闵行区七莘路 3655 号七宝万科广场', 0, 0, 0],
  ['长宁中山公园店', 'open', 2, '郑佳怡', '长宁区长宁路 1018 号龙之梦购物中心', 6310, 176, 4.4], ['普陀长风大悦城购物中心旗舰体验店', 'open', 3, '孙明哲', '普陀区大渡河路 196 号长风大悦城五层 5F-18 号铺', 5870, 164, 4.3],
]
const ST = { open: ['ok', '营业中'], rest: ['mute', '休息中'], prep: ['info', '筹备中'] }
def({
  id: 'AD-DATA-012', name: '数据卡片集', style: '卡片列表切换',
  fit: '门店、客户、应用这类“一个对象一张卡”的总览：卡片看全貌，列表看对比，搜索与状态筛选同时生效',
  avoid: '对象超过 50 个（改用表格加分页）；需要逐列排序与批量操作时用表格；卡片内不要再放与整卡同目的地的按钮',
  kw: 'card list 数据卡片 卡片列表 视图切换 门店卡片 网格 搜索 筛选 总览', stage: '', wide: true,
  css: `.addata012{width:1400px;max-width:100%}.addata012 *{box-sizing:border-box}${STT('addata012')}${SEG_CSS('addata012')}
.addata012 .tb{display:flex;align-items:center;gap:12px 16px;flex-wrap:wrap;margin-bottom:12px}.addata012 .srch{display:flex;align-items:center;gap:8px;width:260px;max-width:100%;height:36px;padding:0 12px;border:1px solid var(--n7);border-radius:8px;background:var(--card);color:var(--ink3);transition:border-color .15s}.addata012 .srch:focus-within{border-color:var(--ink2)}.addata012 .srch svg{width:16px;height:16px;flex:none}.addata012 .srch input{flex:1;min-width:0;height:100%;border:0;outline:none;background:none;font:inherit;font-size:14px;color:var(--ink)}
.addata012 .chs{display:flex;gap:8px;flex-wrap:wrap}.addata012 .ch{height:32px;padding:0 12px;border-radius:8px;font-size:14px;color:var(--ink2);background:var(--card);box-shadow:inset 0 0 0 1px var(--n7);transition:background .15s}.addata012 .ch:hover{background:var(--n2)}.addata012 .ch.on{color:var(--p-text);background:var(--pt);box-shadow:inset 0 0 0 1px var(--p);font-weight:600}.addata012 .ch em{margin-left:4px;font-size:12px;font-weight:400;color:var(--ink3)}.addata012 .sp2{flex:1}.addata012 .cnt{font-size:12px;color:var(--ink3)}
.addata012 .gv{display:grid;gap:16px}.addata012 .gv.card{grid-template-columns:repeat(auto-fill,minmax(300px,1fr))}.addata012 .gv.list{gap:0;${CARD};overflow:hidden}
.addata012 .sc{position:relative;text-align:left;cursor:pointer;transition:box-shadow .15s,transform .15s}.addata012 .card .sc{${CARD};padding:16px;display:flex;flex-direction:column;gap:10px}.addata012 .card .sc:hover{box-shadow:0 1px 2px var(--sh04),0 10px 28px var(--sh12)}.addata012 .card .sc:active{transform:scale(.995)}
.addata012 .list .sc{display:grid;grid-template-columns:minmax(220px,1.6fr) minmax(120px,.8fr) minmax(280px,2fr) 104px;align-items:center;gap:16px;padding:10px 20px;border-bottom:1px solid var(--line)}.addata012 .list .sc:last-child{border-bottom:0}.addata012 .list .sc:hover{background:var(--n1)}.addata012 .list .ad{display:none}
.addata012 .nm{display:flex;align-items:center;gap:8px;min-width:0}.addata012 .nm b{min-width:0;font-size:16px;line-height:24px;font-weight:600;overflow:hidden;text-overflow:ellipsis;white-space:nowrap}.addata012 .nm .stt{flex:none}.addata012 .mg{display:flex;align-items:center;gap:8px;font-size:14px;color:var(--ink2)}.addata012 .ad{font-size:12px;line-height:20px;color:var(--ink3);overflow:hidden;text-overflow:ellipsis;white-space:nowrap}
.addata012 .ms{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:8px}.addata012 .ms div{min-width:0}.addata012 .ms span{display:block;font-size:12px;line-height:20px;color:var(--ink3)}.addata012 .ms b{display:block;font-size:16px;line-height:24px;font-weight:600;white-space:nowrap}.addata012 .ms b.z{color:var(--ink3);font-weight:400}
.addata012 .spk{height:32px}.addata012 .card .spk{width:100%}.addata012 .list .spk{width:104px}
.addata012 .em3{padding:48px 0;text-align:center;font-size:14px;color:var(--ink3)}.addata012 .em3 button{margin-top:8px;height:32px;padding:0 14px;border-radius:8px;font-size:14px;font-weight:600;color:var(--p-text);background:var(--pt)}
@media(max-width:900px){.addata012 .list .sc{grid-template-columns:minmax(0,1fr) auto;gap:8px 12px}.addata012 .list .ms,.addata012 .list .spk{grid-column:1/-1}.addata012 .list .spk{width:100%}}`,
  html: () => `<div class="addata012"><div class="tb"><label class="srch">${sv('search')}<input type="search" placeholder="搜索门店或店长" aria-label="搜索门店或店长"></label><div class="chs" role="group" aria-label="按状态筛选"><button type="button" class="ch on" data-s="all" aria-pressed="true">全部<em></em></button><button type="button" class="ch" data-s="open" aria-pressed="false">营业中<em></em></button><button type="button" class="ch" data-s="rest" aria-pressed="false">休息中<em></em></button><button type="button" class="ch" data-s="prep" aria-pressed="false">筹备中<em></em></button></div><span class="sp2"></span><span class="cnt"></span>${segHTML([['card', '卡片'], ['list', '列表']])}</div>
<div class="gv card">${STORES.map((s, i) => `<article class="sc" data-s="${s[1]}" data-q="${s[0]} ${s[3]}" data-i="${i}" role="button" tabindex="0" data-toast="进入「${s[0]}」概览"><div class="nm"><b title="${s[0]}">${s[0]}</b><span class="stt ${ST[s[1]][0]}">${ST[s[1]][1]}</span></div><div class="mg">${critter(s[2], 24)}<span>店长 ${s[3]}</span></div><div class="ms"><div><span>今日销售额</span><b class="${s[5] ? '' : 'z'}">${s[5] ? '¥' + int(s[5]) : '暂无'}</b></div><div><span>订单数</span><b class="${s[6] ? '' : 'z'}">${s[6] ? int(s[6]) : '暂无'}</b></div><div><span>评分</span><b class="${s[7] ? '' : 'z'}">${s[7] ? dec(s[7], 1) : '暂无'}</b></div></div><div class="spk"></div><div class="ad" title="${s[4]}">${s[4]}</div></article>`).join('')}</div></div>`,
  js: (root) => {
    const gv = $(root, '.gv'), inp = $(root, 'input'), cards = $$(gv, '.sc'); let st = 'all'
    $$(root, '.ch').forEach((c) => { const k = c.dataset.s; $(c, 'em').textContent = k === 'all' ? cards.length : cards.filter((x) => x.dataset.s === k).length })
    const sparks = () => cards.forEach((c) => { const i = +c.dataset.i, host = $(c, '.spk'); if (c.hidden) return; if (!STORES[i][5]) { host.innerHTML = ''; return } const r = rng(30 + i), base = STORES[i][5]; spark(host, Array.from({ length: 7 }, (_, d) => Math.round(base * (0.8 + 0.3 * r()) * (d === 6 ? 1 : 0.9 + d * 0.015))), { w: host.clientWidth, label: '近 7 天销售额趋势' }) })
    const apply = () => {
      const q = inp.value.trim().toLowerCase(); let n = 0
      cards.forEach((c) => { const ok = (st === 'all' || c.dataset.s === st) && (!q || c.dataset.q.toLowerCase().includes(q)); c.hidden = !ok; if (ok) n++ })
      $(root, '.cnt').textContent = `共 ${cards.length} 家，显示 ${n} 家`
      let em = $(gv, '.em3'); if (!n) { if (!em) { em = document.createElement('div'); em.className = 'em3'; em.style.gridColumn = '1/-1'; em.innerHTML = '没有符合条件的门店<br><button type="button" data-clear>清除筛选</button>'; gv.append(em) } } else if (em) em.remove()
      sparks()
    }
    apply(); watch(gv, () => sparks())
    inp.addEventListener('input', apply)
    $$(root, '.ch').forEach((c) => c.addEventListener('click', () => { st = c.dataset.s; $$(root, '.ch').forEach((x) => { x.classList.toggle('on', x === c); x.setAttribute('aria-pressed', x === c) }); apply() }))
    bindSeg($(root, '.sg'), (v) => { gv.className = 'gv ' + v; requestAnimationFrame(sparks) })
    root.addEventListener('click', (e) => { if (e.target.closest('[data-clear]')) { inp.value = ''; st = 'all'; $$(root, '.ch').forEach((x, i) => { x.classList.toggle('on', i === 0); x.setAttribute('aria-pressed', i === 0) }); apply() } })
    root.addEventListener('keydown', (e) => { if ((e.key === 'Enter' || e.key === ' ') && e.target.classList && e.target.classList.contains('sc')) { e.preventDefault(); e.target.click() } })
  },
})
guide('ad', 'DATA', [
  ['驾驶舱顶部放 4–5 个核心指标', '基础统计卡', '主数字、环比涨跌和迷你趋势线一张卡讲完；指标类型各异（目标、告警、双口径）改用“统计卡样式集”'],
  ['分析型页面，点指标看对应趋势', '指标切换统计行', '一排指标加一张趋势图，本期与上期叠在一起比，比 5 张小图省空间'],
  ['订单、客户、工单详情页的字段展示', '描述列表', '两列三列可切，长文本占满一行；要复制、脱敏、行内开关时改用“键值信息面板”'],
  ['记录谁在什么时候做了什么', '操作时间线', '最新在上，点开看明细；协作讨论用“评论动态流”，日志不可改、评论可改，别混用'],
  ['订单、工单、门店的状态与消息提醒', '状态标签与徽标集', '低饱和五种状态色加文字，红点和数字徽标点击即已读'],
  ['门店、商品的排名；目标达成与资源用量', '排行榜', '名次、数值、占比一行看完；达成与用量改用“环形进度与进度条”，按阈值变色并配文字状态'],
  ['长周期里的冷热；一个对象一张卡的总览', '日历热力图', '按天一格，悬停看数；对象总览改用“数据卡片集”，卡片与列表一键切换'],
])

/* ==========================================================================
 * AD-CHART 图表
 * 一张图只回答一个问题，标题写结论（随数据与范围实时计算）；分类色固定顺序；轴与网格极淡；
 * 悬停有提示框，图例可点击显隐；数据标签只标极值，其余交给提示框。
 * ========================================================================== */
const shell = (right, legend, extra = '') => `<div class="hd"><div><h4 class="ttl2"></h4><p class="sub2"></p></div>${right || ''}</div>${legend || ''}<div class="plot"></div>${extra}`
const DT_CSS = (p) => `.${p} .dt2{margin-top:10px;padding:8px 12px;border-radius:8px;background:var(--n2);font-size:14px;line-height:22px;color:var(--ink2);min-height:40px}.${p} .dt2 b{color:var(--ink);font-weight:600}`
const BAR_CSS = (p) => `.${p} .bx{transform-box:fill-box;transform-origin:50% 100%;transition:opacity .15s}.${p} .bx.g{animation:advzgrow .5s cubic-bezier(.2,0,0,1) both}.${p} svg.fx .bx{opacity:.28}.${p} svg.fx .bx.on{opacity:1}.${p} .bgh{fill:rgba(var(--p-rgb),.06)}.${p} .bgs{fill:rgba(var(--p-rgb),.12)}@keyframes advzgrow{from{transform:scaleY(0)}}`
const CHN = [{ n: '小程序', c: VZ[0], s: 0.44 }, { n: '官网', c: VZ[1], s: 0.21 }, { n: '门店', c: VZ[2], s: 0.35 }]
CHN.forEach((c, k) => { const r = rng(40 + k); c.d = MET.orders.d.map((o) => Math.round(o * c.s * (1 + 0.14 * (r() * 2 - 1)))) })
const sumOf = (a) => a.reduce((s, v) => s + v, 0)

/* ---- 柱状引擎：CHART-003（分组）与 CHART-004（堆叠 / 占比）共用 ----
 * cfg = { cats:[标签], series:[{n,c,vals}], mode:'group'|'stack'|'pct', hidden:Set, title(i), vfmt, yfmt, onSelect(i) } */
function mkBars(plot, o = {}) {
  const tip = mkTip(plot); let cfg = null, W = 0, sel = -1, fx = -1, svgEl = null
  const focus = (i) => { fx = i; if (!svgEl) return; svgEl.classList.toggle('fx', i >= 0); $$(svgEl, '.bx').forEach((b) => b.classList.toggle('on', i >= 0 && b.classList.contains('s' + i))) }
  const draw = (anim) => {
    if (!cfg || !W) return
    const { cats, series, mode = 'group' } = cfg, hid = cfg.hidden || new Set(), n = cats.length
    const vis = series.map((s, i) => ({ ...s, i })).filter((s) => !hid.has(s.i)), vf = cfg.vfmt || int
    const tot = cats.map((_, c) => vis.reduce((a, s) => a + s.vals[c], 0))
    const sc = mode === 'pct' ? { max: 100, ticks: [0, 25, 50, 75, 100] } : nice((mode === 'stack' ? Math.max(...tot) : Math.max(...vis.flatMap((s) => s.vals))) * 1.08, 4)
    const yf = mode === 'pct' ? (v) => v + '%' : cfg.yfmt || wan, lw = Math.max(...sc.ticks.map((t) => yf(t).length)) * 7 + 10
    const H = o.h || (W < 460 ? 220 : 260), m = { l: lw, r: 8, t: 20, b: 28 }, iw = W - m.l - m.r, ih = H - m.t - m.b, band = iw / n, Y = (v) => m.t + ih - (v / sc.max) * ih
    const svg = SV('svg', { width: W, height: H, viewBox: `0 0 ${W} ${H}`, role: 'img', 'aria-label': cfg.label || '柱状图' }); svg.style.touchAction = 'pan-y'
    const bgs = SV('rect', { class: 'bgs', rx: 6, y: m.t - 6, height: ih + 6, width: band, visibility: 'hidden' }), bgh = SV('rect', { class: 'bgh', rx: 6, y: m.t - 6, height: ih + 6, width: band, visibility: 'hidden' })
    svg.append(bgs, bgh)
    sc.ticks.forEach((t) => { svg.append(SV('line', { class: t === 0 ? 'bl' : 'gl', x1: m.l, x2: W - m.r, y1: Y(t), y2: Y(t) })); svg.append(SV('text', { class: 'ax', x: m.l - 8, y: Y(t) + 4, 'text-anchor': 'end' }, yf(t))) })
    const sl = Math.max(1, Math.ceil(36 / band))
    cats.forEach((c, i) => { if ((n - 1 - i) % sl === 0) svg.append(SV('text', { class: 'ax', x: m.l + i * band + band / 2, y: H - 6, 'text-anchor': 'middle' }, c)) })
    let best = { v: -1 }
    cats.forEach((c, ci) => {
      const cx = m.l + ci * band, gcls = anim ? ' g' : '', del = ci * 25 + 'ms'
      if (mode === 'group') {
        const k = vis.length, bw = clamp(Math.floor((band * 0.68) / k) - 2, 5, 20), total = k * bw + (k - 1) * 2, x0 = cx + (band - total) / 2
        vis.forEach((s, j) => { const v = s.vals[ci], y = Y(v), x = x0 + j * (bw + 2); const p = SV('path', { d: colPath(x, y, bw, Y(0) - y, 4), class: `bx${gcls} s${s.i}`, style: `fill:${s.c};animation-delay:${del}` }); svg.append(p); if (v > best.v) best = { v, x: x + bw / 2, y } })
      } else {
        const bw = clamp(band * 0.5, 8, 30), x0 = cx + (band - bw) / 2, live = vis.filter((s) => s.vals[ci] > 0); let cum = 0
        live.forEach((s, j) => {
          const v = mode === 'pct' ? (s.vals[ci] / tot[ci]) * 100 : s.vals[ci], isTop = j === live.length - 1, yT = Y(cum + v) + (isTop ? 0 : 1), yB = Y(cum) - (j === 0 ? 0 : 1)
          svg.append(SV('path', { d: colPath(x0, yT, bw, Math.max(1, yB - yT), isTop ? 4 : 0), class: `bx${gcls} s${s.i}`, style: `fill:${s.c};animation-delay:${del}` })); cum += v
        })
        if (mode === 'stack' && tot[ci] > best.v) best = { v: tot[ci], x: x0 + bw / 2, y: Y(tot[ci]) }
      }
    })
    if (best.v > 0 && mode !== 'pct') svg.append(SV('text', { class: 'ax b', x: best.x, y: best.y - 6, 'text-anchor': 'middle' }, vf(best.v)))
    const place = (r, c) => { r.setAttribute('x', m.l + c * band); r.setAttribute('visibility', 'visible') }
    cats.forEach((c, ci) => {
      const hit = SV('rect', { x: m.l + ci * band, y: 0, width: band, height: H, fill: 'transparent', style: 'cursor:pointer' })
      const show = (e) => {
        place(bgh, ci); const [x, y] = relPos(plot, e), rows = vis.map((s) => ({ c: s.c, n: s.n, v: mode === 'pct' ? `${dec((s.vals[ci] / tot[ci]) * 100, 1)}%（${vf(s.vals[ci])}）` : vf(s.vals[ci]) }))
        tip.show(x, y, cfg.title(ci), mode === 'group' ? rows : rows.reverse(), mode === 'group' ? '' : `合计 ${vf(tot[ci])}`)
      }
      hit.addEventListener('pointermove', show); hit.addEventListener('pointerdown', show); hit.addEventListener('pointerleave', () => { bgh.setAttribute('visibility', 'hidden'); tip.hide() })
      hit.addEventListener('click', () => { sel = sel === ci ? -1 : ci; if (sel >= 0) place(bgs, sel); else bgs.setAttribute('visibility', 'hidden'); if (cfg.onSelect) cfg.onSelect(sel) })
      svg.append(hit)
    })
    if (sel >= 0 && sel < n) place(bgs, sel)
    const old = $(plot, 'svg'); if (old) old.remove(); plot.prepend(svg); svgEl = svg; tip.hide(); if (fx >= 0) focus(fx)
  }
  watch(plot, (w) => { W = w; draw(false) })
  return { set(c, anim = true) { cfg = c; if (c.sel !== undefined) sel = c.sel; draw(anim); if (c.onSelect) c.onSelect(sel) }, focus }
}

/* ---- AD-CHART-001 趋势折线图 ---- */
def({
  id: 'AD-CHART-001', name: '趋势折线图', style: '多系列',
  fit: '看 2–4 个渠道随时间的走势和交叉：悬停十字线一次读出每条线的值，点图例显隐，7 天与 30 天一键切换',
  avoid: '系列超过 4 条（改小图并排）；少于 3 个时间点（改数字加变化）；两个量纲不同的指标不要画在同一坐标里，也不用双 Y 轴',
  kw: 'line chart 折线图 趋势 多系列 十字线 提示框 图例 渠道 走势', stage: '', wide: false,
  css: `${VZ_CSS('adchart001')}${DT_CSS('adchart001')}`,
  html: () => `<div class="adchart001">${shell(segHTML([[7, '近 7 天'], [30, '近 30 天']]), lgHTML(CHN, 'ln'))}</div>`,
  js: (root) => {
    let days = 7; const line = mkLine($(root, '.plot')); let hid = new Set()
    const draw = (anim) => {
      const sl = CHN.map((c) => ({ n: c.n, c: c.c, pts: c.d.slice(60 - days) })), sums = sl.map((s) => sumOf(s.pts)), all = sumOf(sums), top = sums.indexOf(Math.max(...sums))
      $(root, '.ttl2').textContent = `近 ${days} 天共 ${int(all)} 单，${sl[top].n}贡献 ${dec((sums[top] / all) * 100, 0)}%`; $(root, '.sub2').textContent = '各渠道按日订单数，悬停十字线读出同一天每条线的值'
      line.set({ label: '分渠道订单趋势', xs: sl[0].pts.map((_, i) => md(dayOf(i, days))), title: (i) => `${md(dayOf(i, days))} ${wk(dayOf(i, days))}`, series: sl, hidden: hid, yfmt: int, vfmt: (v) => int(v) + ' 单' }, anim)
    }
    hid = bindLegend(root, () => draw(false)); bindSeg($(root, '.sg'), (v) => { days = +v; draw(true) }); draw(false)
  },
})

/* ---- AD-CHART-002 均值面积图 ---- */
const HPROF = [3, 2, 1, 1, 1, 2, 4, 8, 14, 20, 26, 34, 40, 36, 28, 24, 26, 30, 38, 46, 44, 34, 20, 10]
const HRS = (() => { const r = rng(21); return HPROF.map((v) => Math.round(v * 58 * (1 + 0.1 * (r() * 2 - 1)))) })()
def({
  id: 'AD-CHART-002', name: '均值面积图', style: '单指标',
  fit: '单个指标的走势与高低点：面积只用淡色渐变，自动标出最高与最低，可叠加均值线，24 小时、7 天、30 天切换',
  avoid: '要比较多条线（用趋势折线图）；数据全是 0 或几乎不变；面积图的纵轴必须从 0 开始，不要截断',
  kw: 'area chart 面积图 均值线 峰值 最高 最低 趋势 时段 小时', stage: '', wide: false,
  css: `${VZ_CSS('adchart002')}${DT_CSS('adchart002')}.adchart002 .tls{display:flex;align-items:center;gap:10px;flex-wrap:wrap}.adchart002 .chk{display:inline-flex;align-items:center;gap:6px;height:32px;padding:0 10px;border-radius:8px;font-size:12px;color:var(--ink2);box-shadow:inset 0 0 0 1px var(--n7);background:var(--card);transition:background .15s,color .15s}.adchart002 .chk:hover{background:var(--n2)}.adchart002 .chk i{display:block;width:14px;height:14px;border-radius:4px;box-shadow:inset 0 0 0 1.5px var(--n10);color:#fff;padding:1px}.adchart002 .chk i svg{display:none}.adchart002 .chk.on{color:var(--ink)}.adchart002 .chk.on i{background:var(--p);box-shadow:none}.adchart002 .chk.on i svg{display:block;stroke-width:3}`,
  html: () => `<div class="adchart002">${shell(`<div class="tls"><button type="button" class="chk" aria-pressed="false"><i>${sv('check')}</i>均值线</button>${segHTML([['24', '24 小时'], ['7', '近 7 天'], ['30', '近 30 天']], 1)}</div>`, '')}</div>`,
  js: (root) => {
    let rg = '7', avgOn = false; const line = mkLine($(root, '.plot'), { h: 250 })
    const draw = (anim) => {
      const pts = rg === '24' ? HRS : MET.sales.d.slice(60 - +rg), n = pts.length, mx = Math.max(...pts), mn = Math.min(...pts), avg = sumOf(pts) / n, xs = pts.map((_, i) => (rg === '24' ? `${pad2(i)}:00` : md(dayOf(i, n))))
      const ttl = (i) => (rg === '24' ? `今日 ${pad2(i)}:00–${pad2(i + 1)}:00` : `${md(dayOf(i, n))} ${wk(dayOf(i, n))}`), im = pts.indexOf(mx), il = pts.indexOf(mn)
      $(root, '.ttl2').textContent = rg === '24' ? `今日销售额在 ${xs[im]} 达到峰值，是全天均值的 ${dec(mx / avg, 1)} 倍` : `近 ${rg} 天日均销售额 ¥${int(avg)}，峰值出现在 ${xs[im]}（${wk(dayOf(im, n))}）`
      $(root, '.sub2').textContent = rg === '24' ? '按小时统计，单位：元' : '按日统计，单位：元'
      line.set({ label: '销售额面积图', xs, title: ttl, headroom: 1.14, yfmt: wan, vfmt: (v) => '¥' + int(v), series: [{ n: '销售额', c: 'var(--p)', pts, area: true }], avg: avgOn ? avg : null,
        marks: [{ i: im, text: `最高 ¥${int(mx)}` }, ...(il !== im ? [{ i: il, text: `最低 ¥${int(mn)}`, pos: 'below' }] : [])], foot: (i) => `较均值 ${pts[i] >= avg ? '+' : ''}${dec((pts[i] / avg - 1) * 100, 1)}%` }, anim)
    }
    bindSeg($(root, '.sg'), (v) => { rg = v; draw(true) })
    $(root, '.chk').addEventListener('click', (e) => { avgOn = !avgOn; e.currentTarget.classList.toggle('on', avgOn); e.currentTarget.setAttribute('aria-pressed', avgOn); draw(false) }); draw(false)
  },
})

/* ---- AD-CHART-003 分组柱状图 ---- */
const MONTHS6 = ['5 月', '6 月', '7 月', '8 月', '9 月', '10 月']
def({
  id: 'AD-CHART-003', name: '分组柱状图', style: '悬停高亮',
  fit: '比较同一类别下 2–3 个系列的大小：线上线下、本月上月；悬停整列高亮并读数，点列可固定，点图例显隐系列',
  avoid: '类别超过 12 个（改横向条形或排行榜）；系列超过 3 个（改堆叠）；柱子不能带三维或渐变；纵轴必须从 0 开始',
  kw: 'bar chart column 柱状图 分组 对比 线上 门店 悬停 高亮', stage: '', wide: false,
  css: `${VZ_CSS('adchart003')}${BAR_CSS('adchart003')}${DT_CSS('adchart003')}`,
  html: () => `<div class="adchart003">${shell(segHTML([['d', '近 7 天'], ['m', '近 6 个月']]), lgHTML([{ n: '线上订单', c: VZ[0] }, { n: '门店订单', c: VZ[1] }]), '<div class="dt2" aria-live="polite"></div>')}</div>`,
  js: (root) => {
    let mode = 'd'; const bars = mkBars($(root, '.plot')); let hid = new Set()
    const dataOf = () => {
      if (mode === 'd') { const o = MET.orders.d.slice(-7); return { cats: o.map((_, i) => md(dayOf(i, 7))), titles: o.map((_, i) => `${md(dayOf(i, 7))} ${wk(dayOf(i, 7))}`), on: o.map((v) => Math.round(v * 0.64)), off: o.map((v) => Math.round(v * 0.36)), span: '本周' } }
      return { cats: MONTHS6, titles: MONTHS6, on: [2310, 2480, 2650, 2890, 3120, 3380], off: [1520, 1490, 1570, 1610, 1590, 1640], span: '半年' }
    }
    const draw = (anim, keep) => {
      const d = dataOf(), all = d.on.map((v, i) => v + d.off[i]), pk = all.indexOf(Math.max(...all)), share = (sumOf(d.on) / sumOf(all)) * 100
      $(root, '.ttl2').textContent = `线上订单占 ${dec(share, 0)}%，${d.cats[pk]} 订单最多`; $(root, '.sub2').textContent = '每组两根柱：线上与门店，单位：单'
      const detail = (i) => { const el = $(root, '.dt2'); if (i < 0) { el.textContent = '点一列可固定并查看明细'; return } el.innerHTML = ''; const b = document.createElement('b'); b.textContent = d.titles[i]; el.append(b, `：线上 ${int(d.on[i])} 单，门店 ${int(d.off[i])} 单，合计 ${int(all[i])} 单，占${d.span}的 ${dec((all[i] / sumOf(all)) * 100, 1)}%`) }
      bars.set({ label: '分渠道订单柱状图', cats: d.cats, mode: 'group', hidden: hid, series: [{ n: '线上订单', c: VZ[0], vals: d.on }, { n: '门店订单', c: VZ[1], vals: d.off }], title: (i) => d.titles[i], vfmt: (v) => int(v) + ' 单', yfmt: int, onSelect: detail, sel: keep ? undefined : pk }, anim)
    }
    hid = bindLegend(root, () => draw(false, true), (i) => bars.focus(i)); bindSeg($(root, '.sg'), (v) => { mode = v; draw(true) }); draw(true)
  },
})

/* ---- AD-CHART-004 堆叠柱状图 ---- */
const CH4 = [{ n: '小程序', c: VZ[0], v: [41200, 46800, 52600, 59800, 64200, 70500] }, { n: '官网', c: VZ[1], v: [28800, 29600, 31200, 30400, 32100, 33600] }, { n: '门店', c: VZ[2], v: [24500, 25200, 24100, 26800, 27300, 27900] }, { n: '第三方平台', c: VZ[3], v: [9800, 11200, 12600, 13900, 14100, 14800] }]
def({
  id: 'AD-CHART-004', name: '堆叠柱状图', style: '绝对值与占比',
  fit: '看总量的同时看构成变化：每月销售额按渠道堆叠，可切成 100% 占比看结构，隐藏某个渠道后自动重排',
  avoid: '分段超过 5 个（尾部并入“其他”）；需要精确比较中间段的大小时（基线不齐，改分组柱）；负值不能堆叠',
  kw: 'stacked bar 堆叠柱状图 占比 构成 渠道 销售额 100% 结构 图例', stage: '', wide: false,
  css: `${VZ_CSS('adchart004')}${BAR_CSS('adchart004')}${DT_CSS('adchart004')}`,
  html: () => `<div class="adchart004">${shell(segHTML([['stack', '销售额'], ['pct', '占比']]), lgHTML(CH4.map((c) => ({ n: c.n, c: c.c }))), '<div class="dt2" aria-live="polite"></div>')}</div>`,
  js: (root) => {
    let mode = 'stack'; const bars = mkBars($(root, '.plot')); let hid = new Set()
    const draw = (anim) => {
      const vis = CH4.filter((_, i) => !hid.has(i)), tot = MONTHS6.map((_, m) => vis.reduce((a, c) => a + c.v[m], 0)), s0 = CH4[0].v
      const a = (s0[0] / CH4.reduce((x, c) => x + c.v[0], 0)) * 100, b = (s0[5] / CH4.reduce((x, c) => x + c.v[5], 0)) * 100
      $(root, '.ttl2').textContent = `小程序销售额占比由 ${dec(a, 0)}% 升至 ${dec(b, 0)}%，已是第一大渠道`; $(root, '.sub2').textContent = mode === 'stack' ? '每月销售额按渠道堆叠，单位：元' : '每月各渠道占当月销售额的比例'
      bars.set({ label: '分渠道销售额堆叠柱状图', cats: MONTHS6, mode, hidden: hid, series: CH4.map((c) => ({ n: c.n, c: c.c, vals: c.v })), title: (i) => `2026 年 ${MONTHS6[i]}`, vfmt: (v) => '¥' + int(v), yfmt: wan,
        onSelect: (i) => { const el = $(root, '.dt2'); if (i < 0) { el.textContent = '点一列可固定并查看各渠道明细'; return } el.innerHTML = ''; const bb = document.createElement('b'); bb.textContent = MONTHS6[i]; el.append(bb, `：${vis.map((c) => `${c.n} ¥${int(c.v[i])}（${dec((c.v[i] / tot[i]) * 100, 1)}%）`).join('，')}`) } }, anim)
    }
    hid = bindLegend(root, () => draw(false), (i) => bars.focus(i)); bindSeg($(root, '.sg'), (v) => { mode = v; draw(true) }); draw(true)
  },
})

/* ---- AD-CHART-005 环形占比图 ---- */
const SHARE = [{ n: '小程序', c: VZ[0], v: 68400 }, { n: '官网', c: VZ[1], v: 32600 }, { n: '门店', c: VZ[2], v: 26100 }, { n: '第三方平台', c: VZ[3], v: 13500 }, { n: '其他', c: VZ_OTHER, v: 7400 }]
const arcPath = (cx, cy, r0, r1, a0, a1) => {
  if (a1 - a0 > Math.PI * 2 - 0.01) return `M${cx - r1},${cy}a${r1},${r1} 0 1,0 ${2 * r1},0a${r1},${r1} 0 1,0 ${-2 * r1},0ZM${cx - r0},${cy}a${r0},${r0} 0 1,0 ${2 * r0},0a${r0},${r0} 0 1,0 ${-2 * r0},0Z`
  const L = a1 - a0 > Math.PI ? 1 : 0, p = (r, a) => `${(cx + r * Math.cos(a)).toFixed(2)},${(cy + r * Math.sin(a)).toFixed(2)}`
  return `M${p(r1, a0)}A${r1},${r1} 0 ${L} 1 ${p(r1, a1)}L${p(r0, a1)}A${r0},${r0} 0 ${L} 0 ${p(r0, a0)}Z`
}
def({
  id: 'AD-CHART-005', name: '环形占比图', style: '悬停弹出',
  fit: '看一个整体由哪几块构成（5 类以内）：悬停分块弹出并在中心读数，点图例或右侧列表隐藏分块，合计随之重算',
  avoid: '分类只有 1 类（改用进度条）；超过 5 类（小类并入“其他”）；需要精确比较相近的占比时改用排行榜或条形图',
  kw: 'donut pie 环形图 饼图 占比 构成 渠道占比 分块 悬停 中心合计', stage: '', wide: false,
  css: `${VZ_CSS('adchart005')}.adchart005 .dw{display:flex;align-items:center;gap:20px 32px;flex-wrap:wrap;margin-top:8px}.adchart005 .dn{position:relative;flex:none;width:220px;height:220px;margin:0 auto}.adchart005 .dn svg{width:220px;height:220px}.adchart005 .sl{cursor:pointer;transition:transform .18s cubic-bezier(.2,0,0,1),opacity .15s}
.adchart005 .ctr{position:absolute;inset:0;display:flex;flex-direction:column;align-items:center;justify-content:center;gap:0;pointer-events:none;text-align:center;padding:0 52px}.adchart005 .c1{font-size:12px;line-height:20px;color:var(--ink3);max-width:100%;overflow:hidden;text-overflow:ellipsis;white-space:nowrap}.adchart005 .c2{font-size:22px;line-height:30px;font-weight:700;white-space:nowrap}.adchart005 .c3{font-size:12px;line-height:20px;color:var(--ink2)}
.adchart005 .ls{flex:1;min-width:240px}.adchart005 .lw{display:flex;align-items:center;gap:10px;width:100%;height:44px;padding:0 10px;border-radius:8px;text-align:left;transition:background .15s}.adchart005 .lw:hover,.adchart005 .lw.hv{background:var(--n3)}.adchart005 .lw i{flex:none;width:10px;height:10px;border-radius:2px;background:var(--c)}.adchart005 .lw .nm{flex:1;min-width:0;font-size:14px;color:var(--ink);overflow:hidden;text-overflow:ellipsis;white-space:nowrap}.adchart005 .lw .vl{flex:none;font-size:14px;font-weight:600;font-variant-numeric:tabular-nums}.adchart005 .lw .pc{flex:none;width:52px;text-align:right;font-size:12px;color:var(--ink3);font-variant-numeric:tabular-nums}.adchart005 .lw.off .nm,.adchart005 .lw.off .vl{color:var(--ink3);font-weight:400}.adchart005 .lw.off i{background:var(--card);box-shadow:inset 0 0 0 1.5px var(--n9)}.adchart005 .lw.off .nm{text-decoration:line-through}
.adchart005 .ht{margin:8px 10px 0;font-size:12px;color:var(--ink3)}`,
  html: () => `<div class="adchart005">${shell('', '', `<div class="dw"><div class="dn"><div class="ctr"><span class="c1"></span><b class="c2"></b><span class="c3"></span></div></div><div class="ls" role="group" aria-label="渠道，点击显示或隐藏">${SHARE.map((s, i) => `<button type="button" class="lw" data-i="${i}" aria-pressed="true"><i style="--c:${s.c}"></i><span class="nm">${s.n}</span><b class="vl"></b><span class="pc"></span></button>`).join('')}<p class="ht">点击渠道可隐藏，合计与占比随之重算</p></div></div>`).replace('<div class="plot"></div>', '')}</div>`,
  js: (root) => {
    const dn = $(root, '.dn'), cx = 110, cy = 110, R = 104, r0 = 68, hid = new Set(); let cur = SHARE.map(() => ({ a0: -Math.PI / 2, a1: -Math.PI / 2 })), stop = null, hv = -1, tgt = null
    const svg = SV('svg', { width: 220, height: 220, viewBox: '0 0 220 220', role: 'img', 'aria-label': '渠道销售额占比环形图' }); dn.prepend(svg)
    const paths = SHARE.map((s, i) => { const p = SV('path', { class: 'sl', style: `fill:${s.c}`, 'data-i': i }); svg.append(p); return p })
    const target = () => { const v = SHARE.map((s, i) => (hid.has(i) ? 0 : s.v)), t = sumOf(v); let a = -Math.PI / 2; return v.map((x) => { const sp = t ? (x / t) * Math.PI * 2 : 0, o = { a0: a, a1: a + sp }; a += sp; return o }) }
    const mid = (i) => (tgt[i].a0 + tgt[i].a1) / 2
    const paint = (A) => A.forEach((a, i) => { const sp = a.a1 - a.a0, g = sp > 0.2 && sp < Math.PI * 2 - 0.05 ? 1.2 / ((R + r0) / 2) : 0; paths[i].setAttribute('d', sp < 0.002 ? '' : arcPath(cx, cy, r0, R, a.a0 + g, a.a1 - g)); paths[i].style.visibility = sp < 0.002 ? 'hidden' : 'visible' })
    const center = (i) => { const vis = SHARE.filter((_, k) => !hid.has(k)), t = sumOf(vis.map((s) => s.v)); const c1 = $(root, '.c1'), c2 = $(root, '.c2'), c3 = $(root, '.c3'); if (i < 0 || hid.has(i)) { c1.textContent = '销售额合计'; c2.textContent = '¥' + int(t); c3.textContent = `${vis.length} 个渠道` } else { c1.textContent = SHARE[i].n; c2.textContent = '¥' + int(SHARE[i].v); c3.textContent = `占 ${dec((SHARE[i].v / t) * 100, 1)}%` } }
    const rows = () => { const t = sumOf(SHARE.filter((_, k) => !hid.has(k)).map((s) => s.v)); $$(root, '.lw').forEach((b, i) => { b.classList.toggle('off', hid.has(i)); b.setAttribute('aria-pressed', !hid.has(i)); $(b, '.vl').textContent = '¥' + int(SHARE[i].v); $(b, '.pc').textContent = hid.has(i) ? '已隐藏' : dec((SHARE[i].v / t) * 100, 1) + '%' })
      const vis = SHARE.map((s, i) => [s, i]).filter(([, i]) => !hid.has(i)).sort((a, b) => b[0].v - a[0].v), top2 = (vis[0][0].v + (vis[1] ? vis[1][0].v : 0)) / t * 100
      $(root, '.ttl2').textContent = vis.length > 1 ? `${vis[0][0].n}占销售额 ${dec((vis[0][0].v / t) * 100, 0)}%，前两大渠道合计 ${dec(top2, 0)}%` : `仅剩${vis[0][0].n}，占全部可见渠道 100%`
      $(root, '.sub2').textContent = '本月各渠道销售额占比，单位：元' }
    const pop = (i) => { hv = i; paths.forEach((p, k) => { const m = mid(k), on = k === i && !hid.has(k); p.style.transform = on ? `translate(${(Math.cos(m) * 6).toFixed(1)}px,${(Math.sin(m) * 6).toFixed(1)}px)` : ''; p.style.opacity = i >= 0 && !on && !hid.has(k) ? '.45' : '' }); $$(root, '.lw').forEach((b, k) => b.classList.toggle('hv', k === i)); center(i) }
    const go = (first) => { tgt = target(); if (stop) stop(); const from = cur.map((c) => ({ ...c })); stop = tween(first ? 900 : 600, (p) => { cur = from.map((f, i) => ({ a0: f.a0 + (tgt[i].a0 - f.a0) * p, a1: f.a1 + (tgt[i].a1 - f.a1) * p })); paint(cur) }, () => { cur = tgt }); rows(); pop(-1) }
    paths.forEach((p, i) => { p.addEventListener('pointerenter', () => pop(i)); p.addEventListener('pointerleave', () => pop(-1)); p.addEventListener('click', () => toggle(i)) })
    const toggle = (i) => { if (!hid.has(i) && hid.size >= SHARE.length - 1) return; hid.has(i) ? hid.delete(i) : hid.add(i); go(false) }
    $$(root, '.lw').forEach((b, i) => { b.addEventListener('click', () => toggle(i)); b.addEventListener('pointerenter', () => pop(i)); b.addEventListener('pointerleave', () => pop(-1)) })
    go(true)
  },
})

/* ---- AD-CHART-006 转化漏斗图 ---- */
const FUN = { all: [12860, 8420, 3150, 1860, 1320], mp: [7420, 5230, 2210, 1380, 1040], web: [3980, 2410, 690, 360, 220] }
const FSTG = ['访问', '浏览商品', '加入购物车', '提交订单', '支付成功']
const FALPHA = [0.5, 0.62, 0.74, 0.87, 1]
def({
  id: 'AD-CHART-006', name: '转化漏斗图', style: '逐级转化',
  fit: '看用户在“访问→浏览→加购→下单→支付”哪一步流失最多：条宽代表人数，侧边直接标转化率，最弱一步自动标出',
  avoid: '步骤不是严格先后的（改用柱状图）；步骤少于 3 步；每一步口径（人数或订单数）必须一致',
  kw: 'funnel 漏斗图 转化率 流失 转化漏斗 下单 支付 步骤 渠道 对比', stage: '', wide: false,
  css: `${VZ_CSS('adchart006')}${DT_CSS('adchart006')}.adchart006 .fn{cursor:pointer;transition:opacity .15s}.adchart006 svg.fx .fn{opacity:.5}.adchart006 svg.fx .fn.on{opacity:1}.adchart006 .nm{font-size:14px;fill:var(--ink)}.adchart006 .nm2{font-size:12px;fill:var(--ink3)}`,
  html: () => `<div class="adchart006">${shell(segHTML([['all', '全部渠道'], ['mp', '小程序'], ['web', '官网']]), '', '<div class="dt2" aria-live="polite"></div>')}</div>`,
  js: (root) => {
    const plot = $(root, '.plot'), tip = mkTip(plot); let ch = 'all', W = 0, vals = FUN.all.slice(), sel = -1, stop = null
    const draw = () => {
      if (!W) return
      const v = vals, n = v.length, narrow = W < 460, labW = narrow ? 92 : 128, rightW = narrow ? 0 : 124, rowH = 52, H = n * rowH + 4, fw = W - labW - rightW - 8, cx = labW + fw / 2
      const wd = v.map((x) => Math.max(18, (fw * x) / v[0])), conv = v.map((x, i) => (i ? (x / v[i - 1]) * 100 : 100)), worst = conv.indexOf(Math.min(...conv.slice(1)))
      const svg = SV('svg', { width: W, height: H, viewBox: `0 0 ${W} ${H}`, role: 'img', 'aria-label': '转化漏斗图' }); svg.style.touchAction = 'pan-y'; if (sel >= 0) svg.classList.add('fx')
      v.forEach((x, i) => {
        const y0 = i * rowH + 2, y1 = y0 + rowH - 4, wt = wd[i], wb = i < n - 1 ? wd[i + 1] : wt * 0.82
        const g = SV('g', { class: 'fn' + (i === sel ? ' on' : '') }), poly = SV('path', { d: `M${cx - wt / 2},${y0}L${cx + wt / 2},${y0}L${cx + wb / 2},${y1}L${cx - wb / 2},${y1}Z`, style: `fill:rgba(var(--p-rgb),${FALPHA[i]})`, 'stroke-linejoin': 'round' })
        const hit = SV('rect', { x: 0, y: y0 - 2, width: W, height: rowH, fill: 'transparent' })
        g.append(poly)
        g.append(SV('text', { class: 'nm', x: 0, y: y0 + 22 }, FSTG[i])); g.append(SV('text', { class: 'nm2', x: 0, y: y0 + 40 }, `${int(x)} 人`))
        if (!narrow && i > 0) { const ry = y0 - 2, bad = i === worst; if (bad) g.append(SV('rect', { x: W - rightW + 4, y: ry - 11, width: 112, height: 22, rx: 4, fill: WARNB })); g.append(SV('text', { x: W - rightW + (bad ? 10 : 6), y: ry + 4, style: `font-size:12px;font-weight:${bad ? 600 : 400};fill:${bad ? WARNC : 'var(--ink2)'}` }, `转化 ${dec(conv[i], 1)}%${bad ? ' · 最弱' : ''}`)) }
        const over = (e) => { svg.classList.add('fx'); $$(svg, '.fn').forEach((f, k) => f.classList.toggle('on', k === i)); const [px, py] = relPos(plot, e); tip.show(px, py, FSTG[i], [{ n: '人数', v: int(x) }, { n: '占访问', v: dec((x / v[0]) * 100, 1) + '%' }, ...(i ? [{ n: '较上一步', v: dec(conv[i], 1) + '%' }, { n: '流失', v: int(v[i - 1] - x) + ' 人' }] : [])]) }
        const out = () => { tip.hide(); svg.classList.toggle('fx', sel >= 0); $$(svg, '.fn').forEach((f, k) => f.classList.toggle('on', k === sel)) }
        hit.addEventListener('pointermove', over); hit.addEventListener('pointerdown', over); hit.addEventListener('pointerleave', out)
        hit.addEventListener('click', () => { sel = sel === i ? -1 : i; out(); detail() }); hit.style.cursor = 'pointer'; g.append(hit); svg.append(g)
      })
      const old = $(plot, 'svg'); if (old) old.remove(); plot.prepend(svg)
      $(root, '.ttl2').textContent = `${FSTG[worst - 1]}到${FSTG[worst]}转化最低（${dec(conv[worst], 1)}%），整体转化 ${dec((v[n - 1] / v[0]) * 100, 1)}%`; $(root, '.sub2').textContent = '条宽代表人数，侧边为较上一步的转化率'
    }
    const detail = () => { const el = $(root, '.dt2'), v = FUN[ch]; if (sel < 0) { el.textContent = '点一个阶段可固定并查看流失明细'; return } el.innerHTML = ''; const b = document.createElement('b'); b.textContent = sel ? `${FSTG[sel - 1]} → ${FSTG[sel]}` : FSTG[0]; el.append(b, sel ? `：${int(v[sel - 1])} 人中有 ${int(v[sel - 1] - v[sel])} 人（${dec(((v[sel - 1] - v[sel]) / v[sel - 1]) * 100, 1)}%）没有继续` : `：共 ${int(v[0])} 人进入，是后续各阶段的基数`) }
    watch(plot, (w) => { W = w; draw() })
    bindSeg($(root, '.sg'), (k) => { ch = k; const from = vals.slice(), to = FUN[k]; if (stop) stop(); stop = tween(700, (p) => { vals = from.map((f, i) => f + (to[i] - f) * p); draw() }); detail() }); detail()
  },
})

/* ---- AD-CHART-007 指针仪表盘 ---- */
def({
  id: 'AD-CHART-007', name: '指针仪表盘', style: '点击刷新',
  fit: '单个比率对照目标和分档：订单履约率、服务评分、可用率；点击仪表盘或按钮，指针摆向新值，读数与状态同步变化',
  avoid: '驾驶舱规范不建议用指针仪表盘（占地大、读数不如数字准）——只在“有明确分档阈值”的单指标上用，其余用进度条；同屏不超过 1 个',
  kw: 'gauge 仪表盘 指针 刻度 履约率 评分 阈值 分档 刷新 动画', stage: '', wide: false,
  css: `${VZ_CSS('adchart007')}${STT('adchart007')}.adchart007 .btn3{height:32px;padding:0 14px;border-radius:8px;font-size:14px;font-weight:600;color:var(--p-text);background:var(--pt);transition:background .15s}.adchart007 .btn3:hover{background:var(--pm)}.adchart007 .gsv{display:flex;justify-content:center;margin-top:12px;cursor:pointer}.adchart007 .gsv svg{width:auto;max-width:100%;height:auto}.adchart007 .nd{transition:transform 1s cubic-bezier(.2,0,0,1)}
.adchart007 .rd{display:flex;flex-direction:column;align-items:center;gap:4px;margin-top:-6px}.adchart007 .gv{font-size:32px;line-height:40px;font-weight:700}.adchart007 .gv small{font-size:16px;font-weight:600;margin-left:2px}.adchart007 .stt i{display:block;width:12px;height:12px}.adchart007 .fc{display:flex;flex-wrap:wrap;justify-content:center;gap:4px 20px;margin-top:8px;font-size:12px;color:var(--ink3)}.adchart007 .fc b{color:var(--ink);font-weight:600;margin-left:4px}`,
  html: () => `<div class="adchart007">${shell('<button type="button" class="btn3" data-r>刷新数据</button>', '').replace('<div class="plot"></div>', '<div class="gsv" role="img" aria-label="订单履约率仪表盘，点击刷新"></div><div class="rd" aria-live="polite"><div class="gv"><span class="num">0</span><small>%</small></div><span class="stt"></span></div><div class="fc"><span>目标<b>90%</b></span><span>上期<b>88.1%</b></span><span class="df"></span></div>')}</div>`,
  js: (root) => {
    const host = $(root, '.gsv'), TARGET = 90, PREV = 88.1, GB = ['#E4B9B3', '#EBD7A8', '#A9CDB8'], ZONES = [[0, 60], [60, 85], [85, 100]]
    const W = 340, R = 128, cx = W / 2, cy = R + 30, H = cy + 20, ang = (v) => Math.PI + (v / 100) * Math.PI, pt = (r, v) => [cx + r * Math.cos(ang(v)), cy + r * Math.sin(ang(v))]
    const svg = SV('svg', { width: W, height: H, viewBox: `0 0 ${W} ${H}` })
    ZONES.forEach(([a, b], i) => { const g = 1.6 / R, a0 = ang(a) + (i ? g : 0), a1 = ang(b) - (i < 2 ? g : 0); svg.append(SV('path', { d: arcPath(cx, cy, R - 16, R, a0, a1), fill: GB[i] })) })
    for (let v = 0; v <= 100; v += 10) { const [x0, y0] = pt(R - 22, v), [x1, y1] = pt(R - 28, v); svg.append(SV('line', { x1: x0, y1: y0, x2: x1, y2: y1, stroke: 'var(--n9)', 'stroke-width': 1 })) }
    ;[0, 60, 85, 100].forEach((v) => { const [x, y] = pt(R + 14, v); svg.append(SV('text', { x, y: y + 4, 'text-anchor': v === 0 ? 'end' : v === 100 ? 'start' : 'middle', style: 'font-size:12px;fill:var(--ink3)' }, v)) })
    const nd = SV('g', { class: 'nd' }); nd.style.transformOrigin = `${cx}px ${cy}px`; nd.style.transform = 'rotate(-90deg)'
    nd.append(SV('path', { d: `M${cx - 4},${cy}L${cx},${cy - R + 24}L${cx + 4},${cy}Z`, fill: 'var(--ink1)' })); svg.append(nd)
    svg.append(SV('circle', { cx, cy, r: 9, fill: 'var(--ink1)' }), SV('circle', { cx, cy, r: 3.5, fill: 'var(--card)' })); host.append(svg)
    let cur = 0, stop = null
    const state = (v) => (v >= 85 ? ['ok', 'checkc', '良好'] : v >= 60 ? ['warn', 'alert', '需关注'] : ['bad', 'alert', '异常'])
    const set = (v) => {
      const [k, ic, tx] = state(v), st = $(root, '.stt'); st.className = 'stt ' + k; st.innerHTML = `<i>${sv(ic)}</i>${tx}`
      nd.style.transform = `rotate(${((v - 50) / 100) * 180}deg)`; if (stop) stop(); const from = cur; stop = tween(1000, (p) => { cur = from + (v - from) * p; $(root, '.num').textContent = dec(cur, 1) })
      $(root, '.ttl2').textContent = `订单履约率 ${dec(v, 1)}%，${v >= TARGET ? '达到' : '低于'}目标 ${TARGET}%`; $(root, '.sub2').textContent = '点击仪表盘或“刷新数据”，指针会摆向新的数值'
      const d = v - TARGET; $(root, '.df').innerHTML = `与目标相差<b>${d >= 0 ? '+' : ''}${dec(d, 1)} 个百分点</b>`
    }
    requestAnimationFrame(() => requestAnimationFrame(() => set(92.4)))
    const next = () => { let v; do v = Math.round((38 + Math.random() * 61.6) * 10) / 10; while (Math.abs(v - cur) < 8); set(v) }
    host.addEventListener('click', next); $(root, '[data-r]').addEventListener('click', next)
  },
})

/* ---- AD-CHART-008 时段热力图 ---- */
const HM = (() => {
  const r = rng(5), out = { o: [], u: [] }, prof = (h, we) => Math.exp(-((h - (we ? 12.6 : 12.1)) ** 2) / 3.2) * 0.9 + Math.exp(-((h - (we ? 19.6 : 18.9)) ** 2) / 4.5) + 0.25 * Math.exp(-((h - 9) ** 2) / 6) + 0.18 * Math.exp(-((h - 22) ** 2) / 5) + 0.03
  for (let d = 0; d < 7; d++) { const we = d >= 5; out.o.push(Array.from({ length: 24 }, (_, h) => Math.round(prof(h, we) * (we ? 74 : 62) * (1 + 0.12 * (r() * 2 - 1))))); out.u.push(Array.from({ length: 24 }, (_, h) => Math.round(prof(h - 1.2, we) * (we ? 540 : 440) * (1 + 0.12 * (r() * 2 - 1))))) }
  return out
})()
const WKM = ['周一', '周二', '周三', '周四', '周五', '周六', '周日']
def({
  id: 'AD-CHART-008', name: '时段热力图', style: '星期×小时',
  fit: '看订单、访客在“星期 × 小时”两个维度上的分布，找高峰排班：悬停读数并高亮所在行列，点一格固定并看占比',
  avoid: '只有一个维度（改柱状图）；颜色档位超过 5 档；精确值要放进表格，热力格只表达高低',
  kw: 'heatmap 热力图 时段 星期 小时 高峰 排班 订单分布 矩阵 悬停', stage: '', wide: false,
  css: `${VZ_CSS('adchart008')}${DT_CSS('adchart008')}.adchart008 .scr{overflow-x:auto;scrollbar-width:thin}.adchart008 .cell{cursor:pointer}.adchart008 .ax.hl{fill:var(--ink);font-weight:600}.adchart008 .lgn{display:flex;align-items:center;justify-content:flex-end;gap:4px;margin-top:8px;font-size:12px;color:var(--ink3)}.adchart008 .lgn i{display:block;width:12px;height:12px;border-radius:3px}`,
  html: () => `<div class="adchart008">${shell(segHTML([['o', '订单量'], ['u', '访客数']]), '', '<div class="lgn">少<i style="background:var(--n4)"></i><i style="background:rgba(var(--p-rgb),.22)"></i><i style="background:rgba(var(--p-rgb),.42)"></i><i style="background:rgba(var(--p-rgb),.66)"></i><i style="background:rgba(var(--p-rgb),.9)"></i>多</div><div class="dt2" aria-live="polite"></div>').replace('<div class="plot"></div>', '<div class="plot"><div class="scr"></div></div>')}</div>`,
  js: (root) => {
    const plot = $(root, '.plot'), scr = $(root, '.scr'), tip = mkTip(plot); let met = 'o', W = 0, sel = null
    const nm = () => (met === 'o' ? '订单' : '访客'), un = () => (met === 'o' ? '单' : '人')
    const FILL = ['#EEF0F3', 'rgba(var(--p-rgb),.22)', 'rgba(var(--p-rgb),.42)', 'rgba(var(--p-rgb),.66)', 'rgba(var(--p-rgb),.9)']
    const draw = () => {
      if (!W) return
      const M = HM[met], flat = M.flat(), sorted = [...flat].sort((a, b) => a - b), q = (p) => sorted[Math.floor(p * (sorted.length - 1))], cuts = [q(0.25), q(0.5), q(0.75), q(0.92)], lv = (v) => (v <= cuts[0] ? 0 : v <= cuts[1] ? 1 : v <= cuts[2] ? 2 : v <= cuts[3] ? 3 : 4)
      const total = sumOf(flat), lw = 40, gp = W < 460 ? 2 : 3, cw = Math.max(10, Math.floor((W - lw) / 24) - gp), ch = clamp(cw + 2, 16, 28), w = lw + 24 * (cw + gp), h = 22 + 7 * (ch + gp)
      const svg = SV('svg', { width: w, height: h, viewBox: `0 0 ${w} ${h}`, role: 'img', 'aria-label': '星期与小时热力图' }), rl = [], cl = [], cells = []
      WKM.forEach((t, d) => { const e = SV('text', { class: 'ax', x: 0, y: 22 + d * (ch + gp) + ch / 2 + 4 }, t); svg.append(e); rl.push(e) })
      for (let hh = 0; hh < 24; hh++) { const e = SV('text', { class: 'ax', x: lw + hh * (cw + gp) + cw / 2, y: 12, 'text-anchor': 'middle', visibility: hh % (W < 460 ? 4 : 2) === 0 ? 'visible' : 'hidden' }, hh); svg.append(e); cl.push(e) }
      M.forEach((row, d) => row.forEach((v, hh) => { const r = SV('rect', { x: lw + hh * (cw + gp), y: 22 + d * (ch + gp), width: cw, height: ch, rx: 4, class: 'cell', style: `fill:${FILL[lv(v)]}`, 'stroke-width': 1.5, stroke: 'none' }); r.dataset.d = d; r.dataset.h = hh; svg.append(r); cells.push(r) }))
      const mark = () => cells.forEach((c) => c.setAttribute('stroke', sel && +c.dataset.d === sel[0] && +c.dataset.h === sel[1] ? '#1F2329' : 'none'))
      const detail = () => { const [d, hh] = sel, v = M[d][hh], dayT = sumOf(M[d]), el = $(root, '.dt2'); el.innerHTML = ''; const b = document.createElement('b'); b.textContent = `${WKM[d]} ${pad2(hh)}:00–${pad2(hh + 1)}:00`; el.append(b, `：${nm()} ${v} ${un()}，占全周 ${dec((v / total) * 100, 1)}%，占当天 ${dec((v / dayT) * 100, 1)}%`) }
      const hl = (d, hh) => { rl.forEach((e, k) => e.classList.toggle('hl', k === d)); cl.forEach((e, k) => { e.classList.toggle('hl', k === hh); if (hh >= 0 && k === hh) e.setAttribute('visibility', 'visible') }) }
      const pk = flat.indexOf(Math.max(...flat)), pd = Math.floor(pk / 24), ph = pk % 24; if (!sel) sel = [pd, ph]; mark(); detail()
      const eve = sumOf(M.map((r) => sumOf(r.slice(18, 21)))) / total * 100
      $(root, '.ttl2').textContent = `${nm()}高峰出现在 ${WKM[pd]} ${pad2(ph)}:00–${pad2(ph + 1)}:00，晚间 18–21 点占全周 ${dec(eve, 0)}%`; $(root, '.sub2').textContent = `每格为某星期某小时的${nm()}数（${un()}），颜色越深越多`
      svg.addEventListener('pointermove', (e) => { const c = e.target.closest('.cell'); if (!c) { tip.hide(); hl(-1, -1); return } const d = +c.dataset.d, hh = +c.dataset.h, [x, y] = relPos(plot, e); hl(d, hh); tip.show(x, y, `${WKM[d]} ${pad2(hh)}:00–${pad2(hh + 1)}:00`, [{ n: nm(), v: M[d][hh] + ' ' + un() }], `占全周 ${dec((M[d][hh] / total) * 100, 1)}%`) })
      svg.addEventListener('pointerleave', () => { tip.hide(); hl(-1, -1); cl.forEach((e, k) => e.setAttribute('visibility', k % (W < 460 ? 4 : 2) === 0 ? 'visible' : 'hidden')) })
      svg.addEventListener('click', (e) => { const c = e.target.closest('.cell'); if (c) { sel = [+c.dataset.d, +c.dataset.h]; mark(); detail() } })
      scr.replaceChildren(svg)
    }
    watch(scr, (w) => { W = w; draw() }); bindSeg($(root, '.sg'), (v) => { met = v; sel = null; draw() })
  },
})

/* ---- AD-CHART-009 能力雷达图 ---- */
const RDN = ['商品质量', '物流时效', '服务态度', '价格优势', '售后处理', '复购口碑'], RDA = [92, 88, 90, 72, 68, 85], RDB = [84, 86, 82, 78, 74, 80]
const pill = (d) => `<span class="dl ${d >= 0 ? 'g' : 'b'}"><i class="ar">${sv(d >= 0 ? 'arrowup' : 'arrowdown')}</i>${Math.abs(d)}</span>`
def({
  id: 'AD-CHART-009', name: '能力雷达图', style: '对比同行',
  fit: '店铺、员工、供应商的多维度评分对比同行或目标：一眼看出短板，悬停或点选维度读数，右侧列表与图联动',
  avoid: '维度少于 4 个或多于 8 个；维度之间量纲不同；只想比较两三个数（改条形图）；读形状，不要读面积',
  kw: 'radar 雷达图 能力 评分 维度 短板 同行均值 对比 店铺评分 蜘蛛图', stage: '', wide: false,
  css: `${VZ_CSS('adchart009')}${DL_CSS('adchart009')}.adchart009 .rw{display:flex;align-items:center;gap:12px 28px;flex-wrap:wrap;margin-top:4px}.adchart009 .rdp{flex:0 1 320px;min-width:240px;margin:8px auto 0}.adchart009 .axl{stroke:var(--n4);stroke-width:1}.adchart009 .axl.hl{stroke:var(--ink5)}.adchart009 .ax.hl{fill:var(--ink);font-weight:600}
.adchart009 .tb2{flex:1;min-width:250px}.adchart009 .th2,.adchart009 .rr{display:grid;grid-template-columns:minmax(0,1fr) 52px 60px 72px;align-items:center;gap:4px;width:100%}.adchart009 .th2{height:32px;font-size:12px;color:var(--ink3);text-align:center}.adchart009 .th2 span:first-child{text-align:left;padding-left:10px}.adchart009 .rr{height:44px;border-radius:8px;text-align:center;font-size:14px;transition:background .15s}.adchart009 .rr:hover{background:var(--n3)}.adchart009 .rr.on{background:var(--pt)}.adchart009 .rr .nm{text-align:left;padding-left:10px;color:var(--ink)}.adchart009 .rr b{font-weight:600;font-variant-numeric:tabular-nums}.adchart009 .rr span.p{color:var(--ink2);font-variant-numeric:tabular-nums}.adchart009 .rr .dl{justify-self:center}`,
  html: () => `<div class="adchart009">${shell('', lgHTML([{ n: '本店', c: 'var(--p)' }, { n: '同行均值', c: VZ_PREV }]), `<div class="rw"><div class="tb2" role="group" aria-label="各维度得分"><div class="th2"><span>维度</span><span>本店</span><span>同行</span><span>差距</span></div>${RDN.map((n, i) => `<button type="button" class="rr" data-i="${i}" aria-pressed="false"><span class="nm">${n}</span><b>${RDA[i]}</b><span class="p">${RDB[i]}</span>${pill(RDA[i] - RDB[i])}</button>`).join('')}</div></div>`).replace('<div class="plot"></div>', '')}</div>`,
  js: (root) => {
    const rw = $(root, '.rw'), host = document.createElement('div'); host.className = 'plot rdp'; rw.prepend(host); const tip = mkTip(host); let sel = -1, hidd = new Set(), W = 0, hiF = () => {}
    const n = RDN.length
    const draw = () => {
      if (!W) return
      const S = clamp(W, 240, 340), cx = S / 2, cy = S / 2, R = S / 2 - 48, ang = (i) => -Math.PI / 2 + (i * 2 * Math.PI) / n, P = (i, v) => [cx + ((R * (v - 40)) / 60) * Math.cos(ang(i)), cy + ((R * (v - 40)) / 60) * Math.sin(ang(i))]
      const svg = SV('svg', { width: S, height: S, viewBox: `0 0 ${S} ${S}`, role: 'img', 'aria-label': '能力雷达图' }); svg.style.touchAction = 'pan-y'
      ;[60, 80, 100].forEach((lv) => svg.append(SV('polygon', { points: RDN.map((_, i) => P(i, lv).join(',')).join(' '), fill: 'none', stroke: 'var(--n4)', 'stroke-width': 1 })))
      const axes = RDN.map((_, i) => { const [x, y] = P(i, 100), l = SV('line', { class: 'axl', x1: cx, y1: cy, x2: x, y2: y }); svg.append(l); return l })
      svg.append(SV('text', { class: 'ax', x: cx + 4, y: cy - R / 3 + 12 }, '60'), SV('text', { class: 'ax', x: cx + 4, y: cy - (2 * R) / 3 + 12 }, '80'), SV('text', { class: 'ax', x: cx + 4, y: cy - R + 12 }, '100'))
      const labels = RDN.map((t, i) => { const [x, y] = P(i, 100), c = Math.cos(ang(i)), s = Math.sin(ang(i)), e = SV('text', { class: 'ax', x: x + c * 14, y: y + s * 14 + (s > 0.5 ? 10 : s < -0.5 ? -2 : 4), 'text-anchor': c > 0.3 ? 'start' : c < -0.3 ? 'end' : 'middle' }, t); svg.append(e); return e })
      ;[[RDB, VZ_PREV, 'peer', 1], [RDA, 'var(--p)', 'me', 0]].forEach(([d, c, k, si]) => {
        if (hidd.has(si)) return
        svg.append(SV('polygon', { points: d.map((v, i) => P(i, v).join(',')).join(' '), style: `stroke:${c};fill:${k === 'me' ? 'var(--p)' : c};fill-opacity:${k === 'me' ? 0.16 : 0.1}`, 'stroke-width': 2, 'stroke-linejoin': 'round' }))
        d.forEach((v, i) => { const [x, y] = P(i, v); svg.append(SV('circle', { cx: x, cy: y, r: 4, style: `fill:${c}`, stroke: 'var(--card)', 'stroke-width': 2 })) })
      })
      const hit = SV('circle', { cx, cy, r: R + 36, fill: 'transparent' }); svg.append(hit)
      hiF = (i) => { axes.forEach((l, k) => l.classList.toggle('hl', k === i)); labels.forEach((l, k) => l.classList.toggle('hl', k === i)); $$(root, '.rr').forEach((b, k) => { b.classList.toggle('on', k === i); b.setAttribute('aria-pressed', k === i) }) }
      const idxAt = (e) => { const r = svg.getBoundingClientRect(), dx = e.clientX - r.left - cx, dy = e.clientY - r.top - cy; if (Math.hypot(dx, dy) < 12) return -1; let a = Math.atan2(dy, dx) + Math.PI / 2; a = ((a % (2 * Math.PI)) + 2 * Math.PI) % (2 * Math.PI); return Math.round(a / ((2 * Math.PI) / n)) % n }
      const over = (e) => { const i = idxAt(e); if (i < 0) { tip.hide(); hiF(sel); return } hiF(i); const [x, y] = relPos(host, e); tip.show(x, y, RDN[i], [{ c: 'var(--p)', n: '本店', v: RDA[i] + ' 分' }, { c: VZ_PREV, n: '同行均值', v: RDB[i] + ' 分' }], `差距 ${RDA[i] - RDB[i] >= 0 ? '+' : ''}${RDA[i] - RDB[i]} 分`) }
      hit.addEventListener('pointermove', over); hit.addEventListener('pointerdown', over); hit.addEventListener('pointerleave', () => { tip.hide(); hiF(sel) })
      hit.addEventListener('click', (e) => { const i = idxAt(e); sel = i === sel ? -1 : i; hiF(sel) })
      const old = $(host, 'svg'); if (old) old.remove(); host.prepend(svg); hiF(sel)
    }
    const low = RDN.filter((_, i) => RDA[i] < RDB[i])
    $(root, '.ttl2').textContent = low.length ? `${low.join('、')}低于同行均值，其余维度领先` : '各维度均不低于同行均值'; $(root, '.sub2').textContent = '各维度满分 100，圆心为 40 分；灰色为同行均值，点右侧维度可在图中高亮'
    hidd = bindLegend(root, draw)
    $$(root, '.rr').forEach((b, i) => { b.addEventListener('click', () => { sel = sel === i ? -1 : i; hiF(sel) }); b.addEventListener('pointerenter', () => hiF(i)); b.addEventListener('pointerleave', () => hiF(sel)) })
    watch(host, (w) => { W = Math.min(w, 340); draw() })
  },
})

/* ---- AD-CHART-010 迷你趋势图集 ---- */
const UPT = (() => { const r = rng(3), a = Array.from({ length: 30 }, () => 0), m = Array.from({ length: 30 }, () => 0); a[17] = 1; m[17] = 18; a[25] = 2; m[25] = 6; return { a, m, r } })()
def({
  id: 'AD-CHART-010', name: '迷你趋势图集', style: '五种迷你图',
  fit: '指标列表里的行内小图：趋势线、迷你柱、涨跌盈亏、目标子弹条、可用性状态条；悬停每个小图读当天的值',
  avoid: '小图没有坐标轴，只表达走势，不用于精确比较；同一列只用同一种；少于 7 个点的趋势不画',
  kw: 'sparkline 迷你图 趋势线 迷你柱 盈亏 win loss 子弹图 bullet 状态条', stage: '', wide: false,
  css: `${VZ_CSS('adchart010')}${DL_CSS('adchart010')}.adchart010 .lst2{position:relative;margin-top:8px}.adchart010 .mh,.adchart010 .mrw{display:grid;grid-template-columns:minmax(96px,1.1fr) 184px 92px 100px;align-items:center;gap:8px}.adchart010 .mh{height:32px;font-size:12px;color:var(--ink3);text-align:center;border-bottom:1px solid var(--line)}.adchart010 .mh span:first-child{text-align:left;padding-left:8px}
.adchart010 .mrw{min-height:56px;padding:6px 0;border-bottom:1px solid var(--line);border-radius:0;cursor:pointer;transition:background .15s}.adchart010 .mrw:last-child{border-bottom:0}.adchart010 .mrw:hover{background:var(--n1)}.adchart010 .nm{padding-left:8px;font-size:14px;color:var(--ink)}.adchart010 .mn{display:flex;justify-content:center}.adchart010 .cur{text-align:center;font-size:14px;font-weight:600;font-variant-numeric:tabular-nums}.adchart010 .chg{display:flex;justify-content:center;font-size:12px;color:var(--ink3);text-align:center}
.adchart010 .mn svg{display:block;overflow:visible}.adchart010 .mb2{transition:opacity .12s}
@media(max-width:620px){.adchart010 .mh{display:none}.adchart010 .mrw{grid-template-columns:minmax(0,1fr) auto;gap:4px 12px}.adchart010 .mn{grid-column:1/-1;order:3;justify-content:flex-start;padding-left:8px}.adchart010 .nm{order:1}.adchart010 .cur{order:2;text-align:right}.adchart010 .chg{display:none}}`,
  html: () => `<div class="adchart010">${shell(segHTML([[7, '近 7 天'], [14, '近 14 天'], [30, '近 30 天']], 1), '').replace('<div class="plot"></div>', `<div class="lst2"><div class="mh"><span>指标</span><span>趋势</span><span>当前</span><span>变化</span></div>${[['line', '日销售额'], ['bar', '订单数'], ['wl', '日环比涨跌'], ['bullet', '销售目标'], ['up', '服务可用性']].map(([k, n]) => `<div class="mrw" data-k="${k}" data-toast="已打开「${n}」趋势详情"><div class="nm">${n}</div><div class="mn"></div><div class="cur"></div><div class="chg"></div></div>`).join('')}</div>`)}</div>`,
  js: (root) => {
    const list = $(root, '.lst2'), tip = mkTip(list), SW = 176, SH = 36, ACC = 'var(--p)', SOFT = 'rgba(var(--p-rgb),.34)'
    let days = 14
    const row = (k) => $(root, `.mrw[data-k="${k}"]`)
    /* 通用：一组可悬停的矩形，tipOf(i) 返回 [标题, 行] */
    const strip = (host, rects, tipOf, hoverFill) => {
      host.replaceChildren(); const svg = SV('svg', { width: SW, height: SH, viewBox: `0 0 ${SW} ${SH}`, role: 'img' }); svg.style.touchAction = 'pan-y'
      rects.forEach((r, i) => { const e = SV('rect', { x: r.x, y: r.y, width: r.w, height: r.h, rx: r.rx || 2, style: `fill:${r.fill}`, class: 'mb2' }); svg.append(e)
        const hit = SV('rect', { x: r.x - 1, y: 0, width: r.w + 2, height: SH, fill: 'transparent' }); svg.append(hit)
        const over = (ev) => { svg.querySelectorAll('.mb2').forEach((q, k) => (q.style.opacity = k === i ? 1 : 0.55)); const [x, y] = relPos(list, ev), [t, rows] = tipOf(i); tip.show(x, y, t, rows) }
        hit.addEventListener('pointermove', over); hit.addEventListener('pointerdown', over); hit.addEventListener('pointerleave', () => { svg.querySelectorAll('.mb2').forEach((q) => (q.style.opacity = '')); tip.hide() }) })
      host.append(svg)
    }
    const bw = (n, mx, mnw) => clamp(Math.floor((SW - (n - 1) * 2) / n), mnw, mx)
    const render = () => {
      /* 1 趋势线 */
      const s = calc('sales', days), r1 = row('line'); spark($(r1, '.mn'), s.pts, { w: SW, h: SH, label: '日销售额趋势', onHover: (i, e) => { if (i < 0) { tip.hide(); return } const [x, y] = relPos(list, e); tip.show(x, y, `${md(dayOf(i, days))} ${wk(dayOf(i, days))}`, [{ c: 'var(--p)', k: 'ln', n: '销售额', v: MET.sales.txt(s.pts[i]) }]) } })
      $(r1, '.cur').textContent = MET.sales.txt(s.pts[days - 1]); $(r1, '.chg').innerHTML = deltaHTML(s.delta, 1, '%')
      /* 2 迷你柱（基线从 0 起，末根用主题色） */
      const o = calc('orders', days), mx = Math.max(...o.pts), w2 = bw(days, 12, 3), r2 = row('bar')
      strip($(r2, '.mn'), o.pts.map((v, i) => { const h = Math.max(2, (v / mx) * (SH - 4)); return { x: i * (w2 + 2) + (SW - (days * w2 + (days - 1) * 2)) / 2, y: SH - h, w: w2, h, rx: 2, fill: i === days - 1 ? ACC : SOFT } }), (i) => [`${md(dayOf(i, days))} ${wk(dayOf(i, days))}`, [{ c: 'var(--p)', n: '订单', v: int(o.pts[i]) + ' 单' }]])
      $(r2, '.cur').textContent = int(o.pts[days - 1]) + ' 单'; $(r2, '.chg').innerHTML = deltaHTML(o.delta, 1, '%')
      /* 3 涨跌盈亏柱：中线以上涨、以下跌，方向本身就是编码，不靠颜色 */
      const base = MET.sales.d.slice(-days - 1), ch = base.slice(1).map((v, i) => (v / base[i] - 1) * 100), amax = Math.max(...ch.map(Math.abs)), r3 = row('wl'), ups = ch.filter((v) => v >= 0).length
      strip($(r3, '.mn'), ch.map((v, i) => { const h = Math.max(2, (Math.abs(v) / amax) * (SH / 2 - 3)); return { x: i * (w2 + 2) + (SW - (days * w2 + (days - 1) * 2)) / 2, y: v >= 0 ? SH / 2 - h : SH / 2, w: w2, h, rx: 1, fill: v >= 0 ? ACC : '#B9BFC8' } }), (i) => [`${md(dayOf(i, days))} ${wk(dayOf(i, days))}`, [{ c: ch[i] >= 0 ? 'var(--p)' : '#B9BFC8', n: '较前一日', v: `${ch[i] >= 0 ? '+' : ''}${dec(ch[i], 1)}%` }]])
      $(r3, '.cur').textContent = `${ch[days - 1] >= 0 ? '+' : ''}${dec(ch[days - 1], 1)}%`; $(r3, '.chg').textContent = `${ups} 涨 ${days - ups} 跌`
      /* 4 子弹条：轴 0–120%，竖线是目标 */
      const r4 = row('bullet'), rate = 86.4, host4 = $(r4, '.mn'); host4.replaceChildren()
      const sv4 = SV('svg', { width: SW, height: SH, viewBox: `0 0 ${SW} ${SH}`, role: 'img', 'aria-label': `销售目标达成 ${rate}%` }); const tx = (v) => (v / 120) * SW
      sv4.append(SV('rect', { x: 0, y: 11, width: SW, height: 14, rx: 4, style: 'fill:var(--pm)' }), SV('rect', { x: 0, y: 11, width: tx(rate), height: 14, rx: 4, style: 'fill:var(--p)' }), SV('rect', { x: tx(100) - 1, y: 6, width: 2, height: 24, rx: 1, fill: 'var(--ink1)' }))
      const hit4 = SV('rect', { x: 0, y: 0, width: SW, height: SH, fill: 'transparent' }); sv4.append(hit4)
      hit4.addEventListener('pointermove', (ev) => { const [x, y] = relPos(list, ev); tip.show(x, y, '销售目标', [{ c: 'var(--p)', n: '已达成', v: dec(rate, 1) + '%' }, { c: '#3B424C', n: '目标', v: '100%' }]) }); hit4.addEventListener('pointerleave', () => tip.hide()); host4.append(sv4)
      $(r4, '.cur').textContent = dec(rate, 1) + '%'; $(r4, '.chg').textContent = '目标 100%'
      /* 5 可用性状态条：每天一格，颜色之外用提示框与右侧文字说明 */
      const r5 = row('up'), a = UPT.a.slice(-days), mm = UPT.m.slice(-days), w5 = bw(days, 8, 3), STC = ['#8FBFA3', '#E0C27A', '#D98F87'], STN = ['正常运行', '服务降级', '服务中断']
      strip($(r5, '.mn'), a.map((v, i) => ({ x: i * (w5 + 2) + (SW - (days * w5 + (days - 1) * 2)) / 2, y: 6, w: w5, h: 24, rx: 2, fill: STC[v] })), (i) => [`${md(dayOf(i, days))} ${wk(dayOf(i, days))}`, [{ c: STC[a[i]], n: STN[a[i]], v: a[i] ? mm[i] + ' 分钟' : '全天' }]])
      const bad = a.filter((v) => v).length, down = sumOf(mm); $(r5, '.cur').textContent = dec(100 - (down / (days * 1440)) * 100, 2) + '%'; $(r5, '.chg').textContent = bad ? `${bad} 天有异常` : '无异常'
    }
    bindSeg($(root, '.sg'), (v) => { days = +v; render() }); render()
    $(root, '.ttl2').textContent = '销售额与订单稳步上升，服务可用性保持在 99.9% 以上'; $(root, '.sub2').textContent = '悬停任意小图读取当天的值；点一行可进入该指标详情'
  },
})

/* ---- AD-CHART-011 气泡散点图 ---- */
const BUBC = [{ n: '数码', c: VZ[1] }, { n: '家居', c: VZ[2] }, { n: '美妆', c: VZ[5] }]
const BUB = [['无线降噪耳机', 0, 599, 22, 2386], ['机械腕表', 0, 899, 12, 645], ['护眼台灯', 0, 219, 31, 1533], ['智能手环', 0, 329, 27, 1820], ['蓝牙音箱', 0, 259, 29, 1180], ['陶瓷马克杯', 1, 59, 42, 3112], ['保温水杯', 1, 89, 46, 4208], ['帆布托特包', 1, 159, 24, 987], ['香薰蜡烛', 1, 99, 38, 1250], ['记忆棉枕', 1, 189, 34, 760], ['保湿精华', 2, 258, 36, 502], ['洁面乳', 2, 79, 48, 2650], ['气垫粉底', 2, 199, 33, 980], ['唇釉', 2, 119, 41, 1410], ['防晒霜', 2, 149, 52, 2980]]
def({
  id: 'AD-CHART-011', name: '气泡散点图', style: '三维度',
  fit: '同时比较三个维度（客单价、复购率、销量）：商品、门店、客户分层；悬停取最近的点，点选固定并看与同类均值的差距',
  avoid: '类别超过 3 类（任意两点都可能相邻，颜色难区分，改分面小图）；点少于 8 个；气泡大小只表达量级，不用于精确读数',
  kw: 'scatter bubble 气泡图 散点图 象限 客单价 复购率 销量 商品分析 四象限', stage: '', wide: false,
  css: `${VZ_CSS('adchart011')}${DT_CSS('adchart011')}.adchart011 .bb{transition:opacity .15s}.adchart011 svg.fx .bb{opacity:.3}.adchart011 svg.fx .bb.on{opacity:1}.adchart011 .lb{font-size:12px;fill:var(--ink1);paint-order:stroke;stroke:var(--card);stroke-width:3px;stroke-linejoin:round;pointer-events:none}.adchart011 .qn{font-size:12px;fill:var(--ink3)}`,
  html: () => `<div class="adchart011">${shell('', lgHTML(BUBC.map((c) => ({ n: c.n, c: c.c }))), '<div class="dt2" aria-live="polite"></div>')}</div>`,
  js: (root) => {
    const plot = $(root, '.plot'), tip = mkTip(plot); let W = 0, sel = -1, hid = new Set(), fxc = -1
    const draw = () => {
      if (!W) return
      const H = W < 460 ? 280 : 320, m = { l: 48, r: 16, t: 22, b: 36 }, iw = W - m.l - m.r, ih = H - m.t - m.b
      const sx = { ticks: [50, 100, 200, 500, 1000] }, sy = nice(60, 3), lg = Math.log, X = (v) => m.l + ((lg(v) - lg(40)) / (lg(1000) - lg(40))) * iw, Y = (v) => m.t + ih - (v / sy.max) * ih
      const vis = BUB.map((b, i) => ({ b, i })).filter(({ b }) => !hid.has(b[1])), mxS = Math.max(...BUB.map((b) => b[4])), Rf = (s) => 5 + Math.sqrt(s / mxS) * 14
      const ax = vis.length ? sumOf(vis.map(({ b }) => b[2])) / vis.length : 0, ay = vis.length ? sumOf(vis.map(({ b }) => b[3])) / vis.length : 0
      const svg = SV('svg', { width: W, height: H, viewBox: `0 0 ${W} ${H}`, role: 'img', 'aria-label': '商品气泡散点图' }); svg.style.touchAction = 'pan-y'
      sy.ticks.forEach((t) => { svg.append(SV('line', { class: t === 0 ? 'bl' : 'gl', x1: m.l, x2: W - m.r, y1: Y(t), y2: Y(t) })); svg.append(SV('text', { class: 'ax', x: m.l - 8, y: Y(t) + 4, 'text-anchor': 'end' }, t + '%')) })
      sx.ticks.forEach((t) => { svg.append(SV('line', { class: 'gl', x1: X(t), x2: X(t), y1: m.t, y2: m.t + ih })); svg.append(SV('text', { class: 'ax', x: X(t), y: H - 16, 'text-anchor': 'middle' }, '¥' + t)) })
      svg.append(SV('text', { class: 'ax', x: W - m.r, y: H - 2, 'text-anchor': 'end' }, '客单价（元，对数刻度）'), SV('text', { class: 'ax', x: m.l - 40, y: 11 }, '复购率'))
      if (vis.length) { svg.append(SV('line', { x1: X(ax), x2: X(ax), y1: m.t, y2: m.t + ih, stroke: 'var(--n10)', 'stroke-width': 1 }), SV('line', { x1: m.l, x2: W - m.r, y1: Y(ay), y2: Y(ay), stroke: 'var(--n10)', 'stroke-width': 1 }), SV('text', { class: 'qn', x: m.l + 6, y: m.t + 14 }, '低价高复购'), SV('text', { class: 'qn', x: W - m.r - 6, y: m.t + ih - 8, 'text-anchor': 'end' }, '高价低复购')) }
      const order = [...vis].sort((a, b) => b.b[4] - a.b[4]), top3 = order.slice(0, 3).map((o) => o.i), pts = []
      order.forEach(({ b, i }) => { const cx = X(b[2]), cy = Y(b[3]), r = Rf(b[4]), c = BUBC[b[1]].c; const e = SV('circle', { cx, cy, r, style: `fill:${c};fill-opacity:.8`, stroke: i === sel ? '#1F2329' : '#fff', 'stroke-width': i === sel ? 2.5 : 2, class: 'bb' + (b[1] === fxc ? ' on' : '') }); e.dataset.c = b[1]; svg.append(e); pts.push({ i, cx, cy, r, e }) })
      order.forEach(({ b, i }) => { if (top3.includes(i)) { const cx = X(b[2]), cy = Y(b[3]), r = Rf(b[4]), right = cx + r + 6 + b[0].length * 12 < W; svg.append(SV('text', { class: 'lb', x: right ? cx + r + 5 : cx - r - 5, y: cy + 4, 'text-anchor': right ? 'start' : 'end' }, b[0])) } })
      const hit = SV('rect', { x: 0, y: 0, width: W, height: H, fill: 'transparent' }); svg.append(hit)
      const near = (e) => { const r = svg.getBoundingClientRect(), px = (e.clientX - r.left) * (W / r.width), py = (e.clientY - r.top) * (W / r.width); let best = null, bd = 1e9; pts.forEach((p) => { const d = Math.hypot(px - p.cx, py - p.cy) - p.r; if (d < bd) { bd = d; best = p } }); return bd < 34 ? best : null }
      const ring = (p) => pts.forEach((q) => q.e.setAttribute('stroke', q === p || q.i === sel ? '#1F2329' : '#fff'))
      const over = (e) => { const p = near(e); if (!p) { tip.hide(); ring(null); return } ring(p); const b = BUB[p.i], [x, y] = relPos(plot, e); tip.show(x, y, b[0], [{ c: BUBC[b[1]].c, n: '品类', v: BUBC[b[1]].n }, { n: '客单价', v: '¥' + b[2] }, { n: '复购率', v: b[3] + '%' }, { n: '月销量', v: int(b[4]) + ' 件' }]) }
      hit.addEventListener('pointermove', over); hit.addEventListener('pointerdown', over); hit.addEventListener('pointerleave', () => { tip.hide(); ring(null) })
      hit.addEventListener('click', (e) => { const p = near(e); sel = p ? (p.i === sel ? -1 : p.i) : -1; draw() })
      const old = $(plot, 'svg'); if (old) old.remove(); plot.prepend(svg); tip.hide()
      const el = $(root, '.dt2')
      if (sel >= 0 && !hid.has(BUB[sel][1])) { const b = BUB[sel], same = BUB.filter((x) => x[1] === b[1]), avgP = sumOf(same.map((x) => x[3])) / same.length; el.innerHTML = ''; const bb = document.createElement('b'); bb.textContent = b[0]; el.append(bb, `（${BUBC[b[1]].n}）：客单价 ¥${b[2]}，复购率 ${b[3]}%，月销 ${int(b[4])} 件；复购率${b[3] >= avgP ? '高于' : '低于'}同类均值 ${dec(Math.abs(b[3] - avgP), 1)} 个百分点`) } else el.textContent = '点一个气泡可固定并查看与同类均值的差距'
    }
    const avg = (c, k) => { const a = BUB.filter((b) => b[1] === c); return sumOf(a.map((b) => b[k])) / a.length }, cats = [0, 1, 2]
    const rep = cats.reduce((a, c) => (avg(c, 3) > avg(a, 3) ? c : a), 0), prc = cats.reduce((a, c) => (avg(c, 2) > avg(a, 2) ? c : a), 0)
    $(root, '.ttl2').textContent = `${BUBC[rep].n}类复购率最高（均值 ${dec(avg(rep, 3), 0)}%），${BUBC[prc].n}类客单价最高（均值 ¥${dec(avg(prc, 2), 0)}）`; $(root, '.sub2').textContent = '气泡大小 = 月销量；灰色十字线为当前可见商品的均值'
    bindLegend(root, (h) => { hid = h; if (sel >= 0 && hid.has(BUB[sel][1])) sel = -1; draw() }, (i) => { fxc = i; const sv2 = $(plot, 'svg'); if (sv2) { sv2.classList.toggle('fx', i >= 0); $$(sv2, '.bb').forEach((e) => e.classList.toggle('on', i >= 0 && +e.dataset.c === i)) } })
    watch(plot, (w) => { W = w; draw() })
  },
})
guide('ad', 'CHART', [
  ['多个渠道随时间的走势与交叉', '趋势折线图', '十字线一次读出每条线的值，系列不超过 4 条；单指标的高低点与均值改用“均值面积图”'],
  ['比较类别大小；总量与构成一起看', '分组柱状图', '悬停整列高亮，点列固定看明细；构成变化改用“堆叠柱状图”，可切 100% 占比'],
  ['整体由哪几块构成', '环形占比图', '5 类以内，悬停分块弹出、中心读数；只有 1 类不画环，改用进度条'],
  ['看流失发生在哪一步', '转化漏斗图', '条宽是人数，侧边直接标转化率并标出最弱一步；步骤必须是严格的先后'],
  ['星期 × 小时的高峰与排班', '时段热力图', '悬停高亮所在行列，点一格固定并看占全周、占当天的比例'],
  ['多维度评分对比同行；三个维度同时比较', '能力雷达图', '4–8 个维度，右侧列表与图联动；价格、复购、销量这类三维度改用“气泡散点图”'],
  ['指标列表里的行内小图；单个比率对照目标', '迷你趋势图集', '五种迷你图一列一种；比率有明确分档阈值时才用“指针仪表盘”，同屏不超过 1 个'],
])

})();
