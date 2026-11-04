/* ===== 组件交互运行时：事件委托，块的 HTML 只写 data-ix 属性 =====
 * 每个块被包在 <div class="ixr">（position:relative）里，这个元素就是块根（rootEl）。
 * 词汇表见 SPEC.md。需要特殊交互的块再写自己的 js(root) 钩子。 */
const IX = (() => {
  const $ = (r, s) => r.querySelector(s)
  const $$ = (r, s) => [...r.querySelectorAll(s)]
  const rootOf = (e) => e.closest('.ixr') || document.body
  const num = (v, d = 0) => (v === undefined || v === '' || isNaN(+v) ? d : +v)
  function toast(root, msg) {
    const t = document.createElement('div'); t.className = 'ix-toast'; t.textContent = msg
    root.appendChild(t); setTimeout(() => t.remove(), 1600)
  }
  function ink(c) {
    const i = $(c, '.ink'), on = $(c, '[data-t].on'); if (!i || !on) return
    i.style.left = on.offsetLeft + 'px'; i.style.width = on.offsetWidth + 'px'
  }
  function setBind(c, root, text) { if (c.dataset.bind) { const t = $(root, c.dataset.bind); if (t) t.textContent = text } }
  function dots(c) {
    const tr = $(c, '.ix-track'), ds = $$(c, '.dots > i'); if (!tr || !ds.length) return
    const kids = [...tr.children]; const mid = tr.scrollLeft + tr.clientWidth / 2
    let best = 0, bd = 1e9
    kids.forEach((k, i) => { const d = Math.abs(k.offsetLeft + k.offsetWidth / 2 - mid); if (d < bd) { bd = d; best = i } })
    ds.forEach((d, i) => d.classList.toggle('on', i === best))
  }
  function scrollToIdx(c, i) {
    const tr = $(c, '.ix-track'); const k = tr.children[Math.max(0, Math.min(tr.children.length - 1, i))]
    tr.scrollTo({ left: k.offsetLeft - (tr.clientWidth - k.offsetWidth) / 2, behavior: 'smooth' })
  }
  function curIdx(c) { const ds = $$(c, '.dots > i'); const i = ds.findIndex((d) => d.classList.contains('on')); return i < 0 ? 0 : i }
  function count(c) {
    let s = num(c.dataset.sec, 0)
    const draw = () => {
      const h = String(Math.floor(s / 3600)).padStart(2, '0'), m = String(Math.floor(s % 3600 / 60)).padStart(2, '0'), x = String(s % 60).padStart(2, '0')
      const H = $(c, '[data-h]'), M = $(c, '[data-m]'), S = $(c, '[data-s]')
      if (H) { H.textContent = h; M.textContent = m; S.textContent = x } else c.textContent = `${h}:${m}:${x}`
    }
    draw(); c.__t && clearInterval(c.__t)
    c.__t = setInterval(() => { if (!c.isConnected) { clearInterval(c.__t); return } s = s > 0 ? s - 1 : num(c.dataset.sec, 0); draw() }, 1000)
  }
  function sortTable(th) {
    const table = th.closest('table'), idx = [...th.parentNode.children].indexOf(th), asc = !th.classList.contains('asc')
    $$(table, 'th').forEach((h) => { h.classList.remove('asc', 'desc'); h.removeAttribute('aria-sort') })
    th.classList.add(asc ? 'asc' : 'desc'); th.setAttribute('aria-sort', asc ? 'ascending' : 'descending')
    const tb = table.tBodies[0], rows = [...tb.rows], isNum = th.dataset.sort === 'n'
    const val = (r) => { const c = r.cells[idx]; const v = c.dataset.v !== undefined ? c.dataset.v : c.textContent.trim(); return isNum ? parseFloat(String(v).replace(/[^0-9.\-]/g, '')) || 0 : v }
    rows.sort((a, b) => { const x = val(a), y = val(b); const r = isNum ? x - y : String(x).localeCompare(String(y), 'zh'); return asc ? r : -r })
    rows.forEach((r) => tb.appendChild(r))
  }
  function checks(c) {
    const all = $(c, '[data-all]'), items = $$(c, '[data-c]'), n = items.filter((x) => x.classList.contains('on')).length
    if (all) { all.classList.toggle('on', n === items.length && n > 0); all.classList.toggle('part', n > 0 && n < items.length) }
    const root = rootOf(c)
    $$(root, '[data-count]').forEach((t) => { t.textContent = n })
    $$(root, '[data-bar]').forEach((b) => { b.hidden = n === 0 })
    items.forEach((x) => { const r = x.closest('tr,li,[data-row]'); if (r) r.classList.toggle('sel', x.classList.contains('on')) })
  }
  function pager(c, to) {
    const btns = $$(c, '[data-pg]'); let i = btns.findIndex((b) => b.classList.contains('on')); if (i < 0) i = 0
    const ni = typeof to === 'number' ? Math.max(0, Math.min(btns.length - 1, to)) : i
    btns.forEach((b, k) => b.classList.toggle('on', k === ni))
    const info = $(rootOf(c), '[data-info]'); if (info) info.textContent = btns[ni].dataset.pg
    return ni
  }
  function steps(c, d) {
    const sp = $$(c, '.sp'), pn = $$(rootOf(c), '[data-s]'); let i = sp.findIndex((s) => s.classList.contains('on')); if (i < 0) i = 0
    i = Math.max(0, Math.min(sp.length - 1, i + d))
    sp.forEach((s, k) => { s.classList.toggle('on', k === i); s.classList.toggle('done', k < i) })
    pn.forEach((p, k) => { p.hidden = k !== i })
    $$(c, '[data-d="-1"]').forEach((b) => (b.disabled = i === 0)); $$(c, '[data-d="1"]').forEach((b) => (b.disabled = i === sp.length - 1))
  }
  function filterList(c, key) {
    const list = $(rootOf(c), c.dataset.list); if (!list) return
    [...list.children].forEach((it) => { it.hidden = !(key === 'all' || key === '' || (it.dataset.k || '').split(' ').includes(key)) })
  }

  document.addEventListener('click', (e) => { if (window.__ixSup && Date.now() - window.__ixSup < 120) { window.__ixSup = 0; e.stopPropagation(); e.preventDefault() } }, true)
  document.addEventListener('click', (e) => {
    const t = e.target
    if (t.closest('[data-ix=dd]') === null) $$(document, '[data-ix=dd].open').forEach((d) => d.classList.remove('open'))
    if (e.target.__drag) { e.target.__drag = false; return }
    let m
    if ((m = t.closest('[data-ix=tabs] [data-t]'))) {
      const c = m.closest('[data-ix=tabs]'), root = rootOf(c)
      $$(c, '[data-t]').forEach((x) => { x.classList.toggle('on', x === m); x.setAttribute('aria-selected', x === m) })
      ink(c)
      const g = c.dataset.g || ''
      $$(root, '[data-p]').filter((p) => (p.dataset.g || '') === g).forEach((p) => { p.hidden = p.dataset.p !== m.dataset.t })
      if (c.dataset.list) filterList(c, m.dataset.t)
      return
    }
    if ((m = t.closest('[data-ix=radio] [data-o]'))) {
      const c = m.closest('[data-ix=radio]'); $$(c, '[data-o]').forEach((x) => x.classList.toggle('on', x === m))
      setBind(c, rootOf(c), m.dataset.v || m.textContent.trim()); return
    }
    if ((m = t.closest('[data-ix=multi] [data-o]'))) {
      const c = m.closest('[data-ix=multi]'), mx = num(c.dataset.max, 99)
      if (!m.classList.contains('on') && $$(c, '[data-o].on').length >= mx) return
      m.classList.toggle('on'); return
    }
    if ((m = t.closest('[data-ix=toggle]'))) { const on = m.classList.toggle('on'); m.setAttribute('aria-checked', on); return }
    if ((m = t.closest('[data-ix=stepper] [data-d]'))) {
      const c = m.closest('[data-ix=stepper]'), v = $(c, '[data-val]'), mn = num(c.dataset.min, 0), mx = num(c.dataset.max, 99), st = num(c.dataset.step, 1)
      const nv = Math.max(mn, Math.min(mx, num(v.textContent, 0) + num(m.dataset.d) * st)); v.textContent = nv
      if (c.dataset.sum) { const s = $(rootOf(c), c.dataset.sum); if (s) s.textContent = nv * num(c.dataset.price) }
      $$(c, '[data-d]').forEach((b) => b.classList.toggle('dis', (num(b.dataset.d) < 0 && nv <= mn) || (num(b.dataset.d) > 0 && nv >= mx))); return
    }
    if ((m = t.closest('[data-ix=carousel] [data-d]'))) { const c = m.closest('[data-ix=carousel]'); scrollToIdx(c, curIdx(c) + num(m.dataset.d)); return }
    if ((m = t.closest('[data-ix=carousel] .dots > i'))) { const c = m.closest('[data-ix=carousel]'); scrollToIdx(c, [...m.parentNode.children].indexOf(m)); return }
    if ((m = t.closest('[data-ix=acc] [data-h]'))) {
      const c = m.closest('[data-ix=acc]'), it = m.closest('.ix-ai'), open = !it.classList.contains('open')
      if (c.dataset.single !== undefined) $$(c, '.ix-ai').forEach((x) => x.classList.remove('open'))
      it.classList.toggle('open', open); return
    }
    if ((m = t.closest('[data-open]'))) { const ov = $(rootOf(m), `[data-ov="${m.dataset.open}"]`); if (ov) ov.classList.add('show'); return }
    if ((m = t.closest('[data-ov] [data-close], [data-ov] .ix-mask'))) { m.closest('[data-ov]').classList.remove('show'); return }
    if ((m = t.closest('[data-ix=dd] [data-tg]'))) { const c = m.closest('[data-ix=dd]'), o = !c.classList.contains('open'); $$(document, '[data-ix=dd].open').forEach((d) => d.classList.remove('open')); c.classList.toggle('open', o); return }
    if ((m = t.closest('[data-ix=dd] [data-o]'))) {
      const c = m.closest('[data-ix=dd]'); $$(c, '[data-o]').forEach((x) => x.classList.toggle('on', x === m))
      const l = $(c, '[data-label]'); if (l) l.textContent = m.dataset.v || m.textContent.trim(); c.classList.remove('open'); return
    }
    if ((m = t.closest('[data-toast]'))) { toast(rootOf(m), m.dataset.toast); }
    if ((m = t.closest('[data-ix=rate] [data-n]'))) {
      const c = m.closest('[data-ix=rate]'), n = num(m.dataset.n); $$(c, '[data-n]').forEach((x) => x.classList.toggle('on', num(x.dataset.n) <= n)); setBind(c, rootOf(c), n + ' 分'); return
    }
    if ((m = t.closest('[data-ix=like]'))) {
      const on = m.classList.toggle('on'), n = $(m, '[data-n]'); if (n) n.textContent = Math.max(0, num(n.textContent) + (on ? 1 : -1)); return
    }
    if ((m = t.closest('[data-ix=sort] th[data-sort]'))) { sortTable(m); return }
    if ((m = t.closest('[data-ix=checks] [data-all]'))) {
      const c = m.closest('[data-ix=checks]'), on = !m.classList.contains('on'); $$(c, '[data-c]').forEach((x) => x.classList.toggle('on', on)); checks(c); return
    }
    if ((m = t.closest('[data-ix=checks] [data-c]'))) { m.classList.toggle('on'); checks(m.closest('[data-ix=checks]')); return }
    if ((m = t.closest('[data-ix=pager] [data-pg]'))) { const c = m.closest('[data-ix=pager]'); pager(c, $$(c, '[data-pg]').indexOf(m)); return }
    if ((m = t.closest('[data-ix=pager] [data-d]'))) { const c = m.closest('[data-ix=pager]'); const i = $$(c, '[data-pg]').findIndex((b) => b.classList.contains('on')); pager(c, i + num(m.dataset.d)); return }
    if ((m = t.closest('[data-ix=tree] [data-x]'))) { m.closest('li').classList.toggle('open'); return }
    if ((m = t.closest('[data-ix=steps] [data-d]'))) { steps(m.closest('[data-ix=steps]'), num(m.dataset.d)); return }
    if ((m = t.closest('[data-ix=cal] [data-day]'))) {
      const c = m.closest('[data-ix=cal]'), ds = $$(c, '[data-day]')
      if (c.dataset.range === undefined) { ds.forEach((x) => x.classList.toggle('on', x === m)); return }
      const st = c.__st
      if (st === undefined || c.__en !== undefined) { c.__st = ds.indexOf(m); c.__en = undefined; ds.forEach((x) => x.classList.remove('on', 'in')); m.classList.add('on'); return }
      const a = Math.min(c.__st, ds.indexOf(m)), b = Math.max(c.__st, ds.indexOf(m)); c.__en = b
      ds.forEach((x, i) => { x.classList.toggle('on', i === a || i === b); x.classList.toggle('in', i > a && i < b) }); return
    }
    if ((m = t.closest('[data-ix=upload] [data-add]'))) {
      const c = m.closest('[data-ix=upload]'), mx = num(c.dataset.max, 6), n = $$(c, '.up-i').length
      if (n >= mx) { toast(rootOf(c), `最多上传 ${mx} 张`); return }
      const s = document.createElement('span'); s.className = 'up-i'; s.innerHTML = `<img src="${ASSETS.prod[n % ASSETS.prod.length]}" alt=""><b data-rm role="button" aria-label="删除">×</b>`
      m.parentNode.insertBefore(s, m); if (n + 1 >= mx) m.hidden = true; return
    }
    if ((m = t.closest('[data-ix=upload] [data-rm]'))) { const c = m.closest('[data-ix=upload]'); m.closest('.up-i').remove(); const a = $(c, '[data-add]'); if (a) a.hidden = false; return }
    if ((m = t.closest('[data-ix=swipe].open .sf')) && !t.closest('button,a,input')) { m.closest('[data-ix=swipe]').classList.remove('open'); m.style.transition = 'transform .2s'; m.style.transform = 'translateX(0)'; return }
    if ((m = t.closest('[data-ix=swipe] [data-del]'))) {
      const r = m.closest('[data-ix=swipe]'); r.style.transition = 'height .25s,opacity .25s'; r.style.height = r.offsetHeight + 'px'; requestAnimationFrame(() => { r.style.height = '0'; r.style.opacity = '0' }); setTimeout(() => r.remove(), 260); return
    }
    if ((m = t.closest('[data-ix=remove]'))) { const r = m.closest('[data-row]') || m.parentElement; r.style.transition = 'opacity .2s'; r.style.opacity = '0'; setTimeout(() => r.remove(), 200); return }
  })
  document.addEventListener('input', (e) => {
    const t = e.target
    if (t.matches && t.matches('[data-ix=search]')) {
      const list = $(rootOf(t), t.dataset.list); if (!list) return
      const q = t.value.trim().toLowerCase(); [...list.children].forEach((it) => { it.hidden = q !== '' && !it.textContent.toLowerCase().includes(q) })
    }
    if (t.matches && t.matches('[data-ix=range]')) { const o = $(rootOf(t), t.dataset.bind); if (o) o.textContent = t.value }
  })
  /* 滑动：鼠标拖动横向滚动（触屏本来就能滑）、轮播同步圆点、行左滑出操作、滑块拖动 */
  let drag = null
  document.addEventListener('pointerdown', (e) => {
    let m
    if (e.pointerType === 'mouse' && (m = e.target.closest('.ix-track, [data-ix=drag]')) && !e.target.closest('input,textarea,select')) {
      drag = { k: 'scroll', el: m, x: e.clientX, l: m.scrollLeft, moved: false }; return
    }
    if ((m = e.target.closest('[data-ix=swipe] .sf'))) {
      const r = m.closest('[data-ix=swipe]'); drag = { k: 'swipe', el: m, r, x: e.clientX, w: num(r.dataset.w, 80), s: r.classList.contains('open') ? -num(r.dataset.w, 80) : 0, moved: false }; m.style.transition = 'none'; return
    }
    if ((m = e.target.closest('[data-ix=slider] .rt'))) { drag = { k: 'range', el: m }; rangeTo(m, e.clientX) }
  })
  function rangeTo(rt, x) {
    const c = rt.closest('[data-ix=slider]'), b = rt.getBoundingClientRect(), mn = num(c.dataset.min, 0), mx = num(c.dataset.max, 100)
    const p = Math.max(0, Math.min(1, (x - b.left) / b.width)), v = Math.round(mn + p * (mx - mn))
    c.style.setProperty('--v', (p * 100) + '%'); const o = $(rootOf(c), c.dataset.bind); if (o) o.textContent = v
  }
  document.addEventListener('pointermove', (e) => {
    if (!drag) return
    if (drag.k === 'scroll') { const dx = e.clientX - drag.x; if (Math.abs(dx) > 4) { drag.moved = true; drag.el.classList.add('drag') } drag.el.scrollLeft = drag.l - dx }
    else if (drag.k === 'swipe') { const dx = Math.max(-drag.w, Math.min(0, drag.s + e.clientX - drag.x)); if (Math.abs(e.clientX - drag.x) > 4) drag.moved = true; drag.el.style.transform = `translateX(${dx}px)`; drag.dx = dx }
    else if (drag.k === 'range') rangeTo(drag.el, e.clientX)
  })
  document.addEventListener('pointerup', (e) => {
    if (!drag) return
    if (drag.k === 'scroll') {
      drag.el.classList.remove('drag')
      if (drag.moved) { const c = drag.el.closest('[data-ix=carousel]'); if (c) { const mid = drag.el.scrollLeft + drag.el.clientWidth / 2; let b = 0, bd = 1e9;[...drag.el.children].forEach((k, i) => { const d = Math.abs(k.offsetLeft + k.offsetWidth / 2 - mid); if (d < bd) { bd = d; b = i } }); scrollToIdx(c, b) } window.__ixSup = Date.now() }
    } else if (drag.k === 'swipe') {
      const open = (drag.dx !== undefined ? drag.dx : drag.s) < -drag.w / 2; drag.r.classList.toggle('open', open)
      drag.el.style.transition = 'transform .2s'; drag.el.style.transform = `translateX(${open ? -drag.w : 0}px)`
    }
    drag = null
  })
  document.addEventListener('scroll', (e) => { const c = e.target.closest && e.target.closest('[data-ix=carousel]'); if (c) dots(c) }, true)
  function init(root) {
    $$(root, '[data-ix=tabs]').forEach(ink)
    $$(root, '[data-ix=carousel]').forEach((c) => { dots(c); if (c.dataset.auto && !c.__a) { const tr = $(c, '.ix-track'); let paused = false; tr.addEventListener('pointerenter', () => (paused = true)); tr.addEventListener('pointerleave', () => (paused = false)); tr.addEventListener('touchstart', () => (paused = true), { passive: true }); c.__a = setInterval(() => { if (!c.isConnected) { clearInterval(c.__a); return } if (!paused) { const i = curIdx(c); scrollToIdx(c, i + 1 >= tr.children.length ? 0 : i + 1) } }, num(c.dataset.auto, 3000)) } })
    $$(root, '[data-ix=count]').forEach(count)
    $$(root, '[data-ix=steps]').forEach((c) => steps(c, 0))
    $$(root, '[data-ix=checks]').forEach(checks)
    $$(root, '[data-ix=slider]').forEach((c) => { const v = num(c.dataset.value, 50), mn = num(c.dataset.min, 0), mx = num(c.dataset.max, 100); c.style.setProperty('--v', ((v - mn) / (mx - mn) * 100) + '%'); const o = $(root, c.dataset.bind); if (o) o.textContent = v })
    $$(root, '[data-ix=pager]').forEach((c) => pager(c, undefined))
  }
  return { init, toast, $, $$ }
})()
