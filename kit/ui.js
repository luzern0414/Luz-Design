/* 模板库共用交互：分段筛选、独立页面、就近展开、下拉、开关、悬浮说明、轻提示、确认框、纵向滚轮、图表与流式文字。
   无依赖；每个函数只做一件事，页面按 data- 属性接入。 */
const Lz = (() => {
  const $ = (s, r = document) => r.querySelector(s);
  const $$ = (s, r = document) => [...r.querySelectorAll(s)];
  const reduce = matchMedia('(prefers-reduced-motion: reduce)').matches;
  const css = (name, el = document.documentElement) => getComputedStyle(el).getPropertyValue(name).trim();

  /* 分段筛选：.seg[data-seg] 内 .seg__item[data-key]；[data-panel] 面板或 data-seg-for 指向的列表项 data-cat 同时受控，只影响下方内容 */
  function initSeg(root = document) {
    $$('[data-seg]', root).forEach(seg => {
      const group = seg.dataset.seg, items = $$('.seg__item', seg);
      seg.setAttribute('role', 'tablist');
      const select = key => {
        items.forEach(b => b.setAttribute('aria-selected', String(b.dataset.key === key)));
        $$(`[data-panel="${group}"]`).forEach(p => { p.hidden = p.dataset.key !== key; });
        const target = seg.dataset.segFor && $(seg.dataset.segFor);
        if (target) {
          let shown = 0;
          $$('[data-cat]', target).forEach(el => {
            const on = key === 'all' || el.dataset.cat.split(' ').includes(key);
            el.hidden = !on || el.dataset.filterOff === '1'; if (!el.hidden) shown++;
          });
          const empty = $('[data-empty]', target.parentElement); if (empty) empty.hidden = shown > 0;
        }
        seg.dispatchEvent(new CustomEvent('lz:seg', { bubbles: true, detail: { group, key } }));
      };
      items.forEach((b, i) => {
        b.setAttribute('role', 'tab'); b.tabIndex = b.getAttribute('aria-selected') === 'true' ? 0 : -1;
        b.addEventListener('click', () => { select(b.dataset.key); items.forEach(x => (x.tabIndex = x === b ? 0 : -1)); });
        b.addEventListener('keydown', e => {
          const d = { ArrowRight: 1, ArrowLeft: -1 }[e.key]; if (!d) return;
          const n = items[(i + d + items.length) % items.length]; n.focus(); n.click(); e.preventDefault();
        });
      });
      const cur = items.find(b => b.getAttribute('aria-selected') === 'true') || items[0]; if (cur) select(cur.dataset.key);
    });
  }

  /* 就近展开：[data-expand="id"] 控制 #id.expand，配对 aria-expanded 与 aria-controls */
  function initExpand(root = document) {
    $$('[data-expand]', root).forEach(btn => {
      const panel = document.getElementById(btn.dataset.expand); if (!panel) return;
      btn.setAttribute('aria-controls', panel.id);
      btn.setAttribute('aria-expanded', String(panel.dataset.open === 'true'));
      panel.inert = panel.dataset.open !== 'true';
      btn.addEventListener('click', () => {
        const open = panel.dataset.open !== 'true';
        panel.dataset.open = String(open); btn.setAttribute('aria-expanded', String(open)); panel.inert = !open;
      });
    });
  }

  /* 独立页面：[data-open="视图"] 打开 [data-view="视图"]；[data-back] 返回，恢复滚动位置与触发焦点 */
  const stack = [];
  function view(id, opener) {
    const views = $$('[data-view]'); const next = views.find(v => v.dataset.view === id); if (!next) return;
    const cur = views.find(v => !v.hidden);
    if (cur && opener !== null) stack.push({ id: cur.dataset.view, y: scrollY, key: opener && (opener.dataset.open + '|' + (opener.dataset.key || '')) });
    views.forEach(v => { v.hidden = v !== next; });
    if (cur && opener !== null) history.pushState({ lz: id }, '');
    scrollTo(0, 0);
    const h = $('h1, h2', next); if (h) { h.tabIndex = -1; h.focus({ preventScroll: true }); }
    document.dispatchEvent(new CustomEvent('lz:view', { detail: { id } }));
  }
  function popView() {
    const prev = stack.pop(); if (!prev) return;
    $$('[data-view]').forEach(v => { v.hidden = v.dataset.view !== prev.id; });
    scrollTo(0, prev.y);
    if (prev.key) {
      const [open, key] = prev.key.split('|');
      const el = $$(`[data-open="${open}"]`).find(e => (e.dataset.key || '') === key); if (el) el.focus({ preventScroll: true });
    }
    document.dispatchEvent(new CustomEvent('lz:view', { detail: { id: prev.id } }));
  }
  /* 按钮返回走浏览器历史，由 popstate 统一出栈，避免历史堆积 */
  function back() { if (history.state && history.state.lz) history.back(); else popView(); }
  function initViews() {
    document.addEventListener('click', e => {
      let o = e.target.closest('[data-open]');
      // data-open 也被展开面板与下拉用作开合状态：只认指向真实视图的那一个
      while (o && !$(`[data-view="${CSS.escape(o.dataset.open)}"]`)) o = o.parentElement && o.parentElement.closest('[data-open]');
      if (o) { view(o.dataset.open, o); return; }
      if (e.target.closest('[data-back]')) back();
    });
    addEventListener('popstate', () => popView());
    document.addEventListener('lz:view', () => $$('.wheel').forEach(w => w._lzSync && w._lzSync()));
  }

  /* 下拉：就近弹出的选项层，选中条件常显 */
  function initDrop(root = document) {
    $$('.drop', root).forEach(drop => {
      const btn = $('.drop__btn', drop), opts = $$('.drop__opt', drop), label = $('b', btn);
      const set = o => { opts.forEach(x => x.setAttribute('aria-selected', String(x === o))); if (label) label.textContent = o.textContent; drop.dataset.value = 'value' in o.dataset ? o.dataset.value : o.textContent; drop.dispatchEvent(new CustomEvent('lz:drop', { bubbles: true, detail: { value: drop.dataset.value } })); };
      btn.setAttribute('aria-haspopup', 'listbox'); btn.setAttribute('aria-expanded', 'false');
      const toggle = open => { drop.dataset.open = String(open); btn.setAttribute('aria-expanded', String(open)); };
      btn.addEventListener('click', e => { e.stopPropagation(); $$('.drop[data-open="true"]').forEach(d => { if (d !== drop) d.dataset.open = 'false'; }); toggle(drop.dataset.open !== 'true'); });
      opts.forEach(o => o.addEventListener('click', () => { set(o); toggle(false); btn.focus(); }));
      drop.addEventListener('keydown', e => { if (e.key === 'Escape') { toggle(false); btn.focus(); } });
      document.addEventListener('click', () => toggle(false));
      const first = opts.find(o => o.getAttribute('aria-selected') === 'true') || (drop.hasAttribute('data-placeholder') ? null : opts[0]); if (first) set(first);
    });
  }

  /* 开关与勾选 */
  function initToggles(root = document) {
    $$('[role="switch"],[role="checkbox"]', root).forEach(el => {
      el.tabIndex = 0;
      const flip = () => { el.setAttribute('aria-checked', String(el.getAttribute('aria-checked') !== 'true')); el.dispatchEvent(new CustomEvent('lz:toggle', { bubbles: true })); };
      el.addEventListener('click', flip);
      el.addEventListener('keydown', e => { if (e.key === ' ' || e.key === 'Enter') { e.preventDefault(); flip(); } });
    });
  }

  /* 悬浮说明：无可见文字的图标在悬浮和键盘焦点时显示中文名；Escape 关闭，鼠标可移入阅读 */
  let tip = null, tipOwner = null;
  function hideTip() { if (tip) { tip.remove(); tip = null; tipOwner = null; } }
  function showTip(el) {
    hideTip(); tipOwner = el;
    tip = document.createElement('div'); tip.className = 'tip'; tip.setAttribute('role', 'tooltip'); tip.textContent = el.dataset.tip;
    (el.closest('dialog[open]') || document.body).appendChild(tip);
    tip.style.left = '0px'; tip.style.top = '0px';
    const o = tip.getBoundingClientRect(); /* 弹层带动画时会成为固定定位的参照框，量出偏移再扣掉 */
    const r = el.getBoundingClientRect(), t = tip.getBoundingClientRect();
    const x = Math.min(Math.max(8, r.left + r.width / 2 - t.width / 2), innerWidth - t.width - 8);
    const below = r.top < t.height + 12;
    tip.style.left = (x - o.left) + 'px'; tip.style.top = ((below ? r.bottom + 6 : r.top - t.height - 6) - o.top) + 'px';
    tip.addEventListener('pointerleave', e => { if (!tipOwner || !tipOwner.contains(e.relatedTarget)) hideTip(); });
  }
  function initTips() {
    document.addEventListener('pointerover', e => { const el = e.target.closest('[data-tip]'); if (el && el !== tipOwner) showTip(el); });
    document.addEventListener('click', e => { const el = e.target.closest('[data-tip]'); if (el && el === tipOwner && tip) tip.textContent = el.dataset.tip; });
    document.addEventListener('pointerout', e => { const el = e.target.closest('[data-tip]'); if (el && !(tip && tip.contains(e.relatedTarget)) && !el.contains(e.relatedTarget)) hideTip(); });
    document.addEventListener('focusin', e => { const el = e.target.closest('[data-tip]'); if (el && el.matches(':focus-visible')) showTip(el); });
    document.addEventListener('focusout', hideTip);
    document.addEventListener('keydown', e => { if (e.key === 'Escape') hideTip(); });
  }

  /* 轻提示：不抢焦点，不挡主要操作 */
  function toast(text, tone = 'neutral') {
    let host = $('.toast-host'); if (!host) { host = document.createElement('div'); host.className = 'toast-host'; host.setAttribute('role', 'status'); host.setAttribute('aria-live', 'polite'); host.setAttribute('popover', 'manual'); document.body.appendChild(host); }
    const t = document.createElement('div'); t.className = 'toast'; t.dataset.tone = tone; t.textContent = text; host.appendChild(t);
    /* 顶层浮层：每次重新提到最上，不被之后打开的居中弹层盖住 */
    try { if (host.matches(':popover-open')) host.hidePopover(); host.showPopover(); } catch (e) { /* 不支持浮层的浏览器沿用普通固定定位 */ }
    setTimeout(() => { t.dataset.leave = ''; setTimeout(() => t.remove(), 160); }, 2400);
  }

  /* 确认框：居中、无方向滑动，只含标题与相邻的确认取消，不含任何输入 */
  function confirm({ title, body = '', ok = '确认', cancel = '取消', tone = 'primary' }) {
    return new Promise(resolve => {
      const d = document.createElement('dialog'); d.className = 'dialog'; d.setAttribute('role', 'alertdialog');
      const id = 'dlg' + Date.now(); d.setAttribute('aria-labelledby', id + 't'); if (body) d.setAttribute('aria-describedby', id + 'b');
      d.innerHTML = `<h2 class="dialog__title" id="${id}t"></h2>${body ? `<p class="dialog__body" id="${id}b"></p>` : ''}<div class="dialog__acts"><button class="btn btn--ghost" value="no">${cancel}</button><button class="btn btn--${tone}" value="yes">${ok}</button></div>`;
      $('.dialog__title', d).textContent = title; if (body) $('.dialog__body', d).textContent = body;
      d.addEventListener('click', e => { const b = e.target.closest('button'); if (b) d.close(b.value); });
      d.addEventListener('close', () => { resolve(d.returnValue === 'yes'); d.remove(); });
      document.body.appendChild(d); d.showModal(); $('[value="yes"]', d).focus();
    });
  }

  /* 纵向滚轮：滚动与手输共用一个值；快捷范围不是业务上限 */
  function initWheels(root = document) {
    $$('.wheel', root).forEach(w => {
      const min = +w.dataset.min || 0, max = +w.dataset.max || 99, step = +w.dataset.step || 1, unit = w.dataset.unit || '';
      let value = +w.dataset.value || min;
      const wrap = document.createElement('div'); wrap.className = 'wheel__wrap';
      const col = document.createElement('div'); col.className = 'wheel__col'; col.tabIndex = -1; col.setAttribute('aria-hidden', 'true');
      let html = '<div class="wheel__pad"></div>'; for (let v = min; v <= max; v += step) html += `<div class="wheel__item" data-v="${v}">${v}</div>`; html += '<div class="wheel__pad"></div>';
      col.innerHTML = html; wrap.append(col, Object.assign(document.createElement('div'), { className: 'wheel__band' }));
      const input = document.createElement('input'); input.className = 'input'; input.inputMode = 'numeric'; input.value = value; input.name = w.dataset.name || ''; input.setAttribute('aria-label', w.dataset.label || '数值');
      const u = document.createElement('span'); u.className = 't-sub'; u.textContent = unit;
      w.replaceChildren(wrap, input, u);
      const items = $$('.wheel__item', col); let timer;
      const mark = v => items.forEach(i => i.setAttribute('aria-selected', String(+i.dataset.v === v)));
      const to = (v, smooth) => { const idx = Math.round((Math.min(Math.max(v, min), max) - min) / step); col.scrollTo({ top: idx * 44, behavior: smooth && !reduce ? 'smooth' : 'auto' }); mark(min + idx * step); };
      col.addEventListener('scroll', () => { clearTimeout(timer); timer = setTimeout(() => { const v = min + Math.round(col.scrollTop / 44) * step; value = v; input.value = v; mark(v); w.dispatchEvent(new CustomEvent('lz:wheel', { bubbles: true, detail: { value: v } })); }, 70); });
      input.addEventListener('input', () => { const n = parseInt(input.value, 10); if (!Number.isNaN(n)) { value = n; to(n, true); } });
      input.addEventListener('keydown', e => { const d = { ArrowUp: step, ArrowDown: -step }[e.key]; if (!d) return; e.preventDefault(); value = Math.max(min, (parseInt(input.value, 10) || min) + d); input.value = value; to(value, true); });
      w._lzSync = () => to(parseInt(input.value, 10) || min, false);
      requestAnimationFrame(() => to(value, false));
    });
  }

  /* 数字入场与进入视野的错峰出现 */
  function count(el, to = +el.dataset.to, ms = 700) {
    const dec = (String(to).split('.')[1] || '').length;
    const fmt = n => (dec ? n.toFixed(dec) : Math.round(n).toLocaleString('zh-CN'));
    if (reduce) { el.textContent = fmt(to); return; }
    const t0 = performance.now(); const tick = t => { const p = Math.min(1, (t - t0) / ms), e = 1 - Math.pow(1 - p, 3); el.textContent = fmt(to * e); if (p < 1) requestAnimationFrame(tick); }; requestAnimationFrame(tick);
  }
  function initReveal(root = document) {
    const io = new IntersectionObserver(es => es.forEach(e => { if (e.isIntersecting) { e.target.dataset.in = ''; const n = $('[data-to]', e.target); if (n) count(n); io.unobserve(e.target); } }), { threshold: .12 });
    $$('[data-reveal]', root).forEach((el, i) => { el.classList.add('reveal'); el.style.setProperty('--i', i % 8); io.observe(el); });
    $$('[data-count]', root).forEach(n => { const o = new IntersectionObserver(es => { if (es[0].isIntersecting) { count(n); o.disconnect(); } }); o.observe(n); });
  }

  /* 折线图：保留真实顺序与缺口（null 断开），不平滑；指针、触屏点选与方向键都更新同区明细 */
  function line(canvas, { labels, values, unit = '', read, readLabels }) {
    const rl = readLabels || labels;
    const ctx = canvas.getContext('2d'); let active = values.length - 1;
    const draw = () => {
      const dpr = devicePixelRatio || 1, w = canvas.clientWidth, h = canvas.clientHeight; canvas.width = w * dpr; canvas.height = h * dpr; ctx.setTransform(dpr, 0, 0, dpr, 0, 0); ctx.clearRect(0, 0, w, h);
      const nums = values.filter(v => v != null), top = Math.max(...nums), bot = Math.min(...nums), span = (top - bot) || top || 1, lo = Math.max(0, bot - span * .3), hi = top + span * .15, pad = { l: 8, r: 8, t: 12, b: 24 };
      const x = i => pad.l + (w - pad.l - pad.r) * (values.length === 1 ? .5 : i / (values.length - 1)), y = v => pad.t + (h - pad.t - pad.b) * (1 - (v - lo) / (hi - lo));
      ctx.strokeStyle = css('--line'); ctx.lineWidth = 1; for (let g = 0; g <= 3; g++) { const gy = pad.t + (h - pad.t - pad.b) * g / 3; ctx.beginPath(); ctx.moveTo(pad.l, gy); ctx.lineTo(w - pad.r, gy); ctx.stroke(); }
      ctx.fillStyle = css('--ink-3'); ctx.font = `12px ${css('--font')}`; labels.forEach((l, i) => { ctx.textAlign = i === 0 ? 'left' : i === labels.length - 1 ? 'right' : 'center'; ctx.fillText(l, x(i), h - 6); });
      ctx.strokeStyle = css('--action'); ctx.lineWidth = 2; ctx.lineJoin = 'round'; ctx.beginPath(); let pen = false;
      values.forEach((v, i) => { if (v == null) { pen = false; return; } pen ? ctx.lineTo(x(i), y(v)) : ctx.moveTo(x(i), y(v)); pen = true; }); ctx.stroke();
      values.forEach((v, i) => { if (v == null) return; ctx.beginPath(); ctx.arc(x(i), y(v), i === active ? 5 : 3, 0, 7); ctx.fillStyle = i === active ? css('--action') : css('--surface'); ctx.fill(); ctx.lineWidth = 2; ctx.stroke(); });
      if (read) read.textContent = values[active] == null ? `${rl[active]} 暂无数据` : `${rl[active]} ${Number(values[active]).toLocaleString('zh-CN')}${unit}`;
    };
    const pick = clientX => { const r = canvas.getBoundingClientRect(); const i = Math.round(((clientX - r.left - 8) / (r.width - 16)) * (values.length - 1)); active = Math.min(values.length - 1, Math.max(0, i)); draw(); };
    canvas.tabIndex = 0;
    canvas.addEventListener('pointermove', e => pick(e.clientX)); canvas.addEventListener('pointerdown', e => pick(e.clientX));
    canvas.addEventListener('keydown', e => { const d = { ArrowRight: 1, ArrowLeft: -1 }[e.key]; if (!d) return; e.preventDefault(); active = Math.min(values.length - 1, Math.max(0, active + d)); draw(); });
    new ResizeObserver(draw).observe(canvas); draw();
  }

  /* 流式文字：追加到当前文本节点，稳定步骤保持原 DOM */
  function stream(el, text, cps = 36) {
    let stopped = false;
    const promise = new Promise(resolve => {
      const node = document.createTextNode(''); el.appendChild(node); el.classList.add('is-streaming');
      if (reduce) { node.data = text; el.classList.remove('is-streaming'); return resolve(); }
      let i = 0; const step = () => { if (stopped) { el.classList.remove('is-streaming'); return resolve(); } i = Math.min(text.length, i + Math.max(1, Math.round(cps / 30))); node.data = text.slice(0, i); if (i < text.length) setTimeout(step, 1000 / 30); else { el.classList.remove('is-streaming'); resolve(); } }; step();
    });
    promise.cancel = () => { stopped = true; };
    return promise;
  }

  /* 提交前同步：停止滚轮惯性并读取仍在编辑的输入 */
  function syncWheels(form) { $$('.wheel .input', form).forEach(i => i.dispatchEvent(new Event('input'))); return Object.fromEntries(new FormData(form)); }

  /* 外观：<html> 的 data-theme（24 个预设）、data-icons（mono 单色 flat 彩色扁平 3d 立体 real 真实）、data-bg（背景效果），
     以及自选主色 color。img[data-ic] 的地址随图标集换成同名图标，mono 与 flat 共用扁平图标集，mono 另靠 kit.css 的滤镜单色化。
     预览框里的页面通过 postMessage({ lz: 'skin', ... }) 或地址参数 ?theme=&icons=&bg=&color= 同步 */
  const ICON_SET = { mono: 'flat', flat: 'flat', '3d': '3d', real: 'real' };
  const iconSet = () => ICON_SET[document.documentElement.dataset.icons] || 'flat';
  const CUSTOM_VARS = ['--action', '--accent', '--hue', '--ic-sat'];
  const srgbToLin = c => (c <= 0.04045 ? c / 12.92 : ((c + 0.055) / 1.055) ** 2.4);
  const linToSrgb = c => (c <= 0.0031308 ? 12.92 * c : 1.055 * Math.abs(c) ** (1 / 2.4) - 0.055);
  function hexToRgb(hex) { const v = hex.replace('#', ''); return [0, 2, 4].map(i => parseInt(v.slice(i, i + 2), 16) / 255); }
  function lum(rgb) { const [r, g, b] = rgb.map(srgbToLin); return 0.2126 * r + 0.7152 * g + 0.0722 * b; }
  function contrastWhite(rgb) { return 1.05 / (lum(rgb) + 0.05); }
  function rgbToOklch([r, g, b]) {
    const [lr, lg, lb] = [r, g, b].map(srgbToLin);
    const l = Math.cbrt(0.4122214708 * lr + 0.5363325363 * lg + 0.0514459929 * lb), m = Math.cbrt(0.2119034982 * lr + 0.6806995451 * lg + 0.1073969566 * lb), s = Math.cbrt(0.0883024619 * lr + 0.2817188376 * lg + 0.6299787005 * lb);
    const L = 0.2104542553 * l + 0.793617785 * m - 0.0040720468 * s, a = 1.9779984951 * l - 2.428592205 * m + 0.4505937099 * s, bb = 0.0259040371 * l + 0.7827717662 * m - 0.808675766 * s;
    return [L, Math.hypot(a, bb), (Math.atan2(bb, a) * 180 / Math.PI + 360) % 360];
  }
  function oklchToRgb(L, C, H) {
    const a = C * Math.cos(H * Math.PI / 180), b = C * Math.sin(H * Math.PI / 180);
    const l = (L + 0.3963377774 * a + 0.2158037573 * b) ** 3, m = (L - 0.1055613458 * a - 0.0638541728 * b) ** 3, s = (L - 0.0894841775 * a - 1.291485548 * b) ** 3;
    return [4.0767416621 * l - 3.3077115913 * m + 0.2309699292 * s, -1.2684380046 * l + 2.6097574011 * m - 0.3413193965 * s, -0.0041960863 * l - 0.7034186147 * m + 1.707614701 * s].map(linToSrgb);
  }
  const inGamut = rgb => rgb.every(c => c >= -0.0005 && c <= 1.0005);
  const toHex = rgb => '#' + rgb.map(c => Math.round(Math.min(1, Math.max(0, c)) * 255).toString(16).padStart(2, '0')).join('');
  /* 同一色相与彩度下，白字仍有 4.6:1 的最浅主色；彩度超出色域就收小 */
  function fitColour(C, H, cap) {
    for (let L = cap; L > 0.15; L -= 0.004) {
      let c = C; while (c > 0 && !inGamut(oklchToRgb(L, c, H))) c -= 0.002;
      const rgb = oklchToRgb(L, Math.max(c, 0), H);
      if (contrastWhite(rgb.map(x => Math.min(1, Math.max(0, x)))) >= 4.6) return toHex(rgb);
    }
    return '#222222';
  }
  function hslHue([r, g, b]) {
    const mx = Math.max(r, g, b), mn = Math.min(r, g, b), d = mx - mn; if (!d) return 0;
    const h = mx === r ? ((g - b) / d) % 6 : mx === g ? (b - r) / d + 2 : (r - g) / d + 4;
    return Math.round((h * 60 + 360) % 360);
  }
  /* 自选主色：保留色相与彩度，亮度压到白字可读；同时派生辅色、图标色相与单色饱和度 */
  function customColour(hex) {
    const h = document.documentElement, [, C, H] = rgbToOklch(hexToRgb(hex));
    const action = fitColour(Math.min(C, 0.14), H, 0.66), accent = fitColour(Math.min(C + 0.01, 0.1), (H + 38) % 360, 0.6);
    h.style.setProperty('--action', action); h.style.setProperty('--accent', accent);
    h.style.setProperty('--hue', hslHue(hexToRgb(action))); h.style.setProperty('--ic-sat', String(Math.min(C / 0.1 * 1.5, 1.9).toFixed(2)));
    custom = (custom + 1) % 2; h.dataset.theme = 'custom' + custom; // 属性变化让画布图表重绘
    return action;
  }
  let custom = 0;
  function skin({ theme, icons, bg, color } = {}) {
    const h = document.documentElement;
    if (theme) { h.dataset.theme = theme; CUSTOM_VARS.forEach(k => h.style.removeProperty(k)); }
    if (color) customColour(color);
    if (bg) h.dataset.bg = bg;
    if (icons) {
      h.dataset.icons = icons;
      const base = h.dataset.icBase || '../../kit/assets/icons';
      $$('img[data-ic]').forEach(i => { i.src = `${base}/${ICON_SET[icons] || 'flat'}/${i.dataset.ic}.webp`; });
    }
    document.dispatchEvent(new CustomEvent('lz:skin', { detail: { theme, icons, bg, color } }));
  }
  function initSkin() {
    const q = new URLSearchParams(location.search);
    if (['theme', 'icons', 'bg', 'color'].some(k => q.get(k))) skin({ theme: q.get('theme'), icons: q.get('icons'), bg: q.get('bg'), color: q.get('color') });
    addEventListener('message', e => { if (e.data && e.data.lz === 'skin') skin(e.data); });
  }

  function init(root = document) { initSeg(root); initExpand(root); initDrop(root); initToggles(root); initWheels(root); initReveal(root); }
  document.addEventListener('DOMContentLoaded', () => { init(); initViews(); initTips(); initSkin(); });
  return { $, $$, init, skin, iconSet, view, back, toast, confirm, line, stream, count, syncWheels, initSeg, initExpand, initDrop, initToggles, initWheels, initReveal, reduce };
})();
