/* Luz UI kit 的行为层：原生 JS，无依赖。对话框、弹出菜单、提示用浏览器原生的 <dialog>、popover、view transition；图表是手写 SVG；看板与泳道是两个渲染器。
   不支持的浏览器降级：没有 view transition 就直接切换，没有 popover 就用 hidden 切换，没有 anchor 定位就由 UI.menu 按触发器位置放。 */
(function () {
  'use strict';
  const UI = (window.UI = {});
  const $ = (s, r) => (r || document).querySelector(s);
  const $$ = (s, r) => Array.from((r || document).querySelectorAll(s));
  UI.$ = $; UI.$$ = $$;

  /** h('div.a.b', {class, style, on:{click}, text, html, 其余写属性}, ...子节点) */
  UI.h = function (tag, props, ...kids) {
    const m = /^([a-z0-9-]+)((?:[.#][\w-]+)*)$/i.exec(tag), el = document.createElement(m ? m[1] : tag);
    if (m && m[2]) m[2].replace(/([.#])([\w-]+)/g, (_, k, v) => (k === '.' ? el.classList.add(v) : (el.id = v)));
    for (const [k, v] of Object.entries(props || {})) {
      if (v == null || v === false) continue;
      if (k === 'class') v.split(/\s+/).filter(Boolean).forEach((c) => el.classList.add(c));
      else if (k === 'style') { if (typeof v === 'string') el.style.cssText += v; else for (const [a, b] of Object.entries(v)) a.startsWith('--') ? el.style.setProperty(a, b) : (el.style[a] = b); }
      else if (k === 'on') for (const [ev, fn] of Object.entries(v)) el.addEventListener(ev, fn);
      else if (k === 'text') el.textContent = v;
      else if (k === 'html') el.innerHTML = v;
      else if (['value', 'checked', 'disabled', 'selected', 'open'].includes(k)) el[k] = v;
      else el.setAttribute(k, v === true ? '' : v);
    }
    const add = (c) => { if (c == null || c === false) return; if (Array.isArray(c)) c.forEach(add); else el.append(c.nodeType ? c : document.createTextNode(String(c))); };
    kids.forEach(add);
    return el;
  };
  const h = UI.h;

  /* ---------- 减少动态效果：系统偏好与页面开关任一开启即生效 ---------- */
  const mq = matchMedia('(prefers-reduced-motion: reduce)');
  UI.rmUser = false; UI.rm = mq.matches;
  const syncRM = () => { UI.rm = mq.matches || UI.rmUser; document.documentElement.classList.toggle('rm', UI.rm); };
  mq.addEventListener && mq.addEventListener('change', syncRM);
  UI.setReduced = (on) => { UI.rmUser = !!on; syncRM(); };
  syncRM();
  /* ---------- 外观：跟随系统 / 浅色 / 深色。选择记在本机（localStorage 的 luz-theme，没有即跟随系统），落到 <html data-theme>；
     页面 <head> 里先于样式执行的内联脚本做同一件事（references/ui-kit/README.md），减少加载闪烁 ---------- */
  const THEME_KEY = 'luz-theme', THEMES = [['system', '跟随系统'], ['light', '浅色'], ['dark', '深色']];
  const themeNow = () => { try { const v = localStorage.getItem(THEME_KEY); return v === 'light' || v === 'dark' ? v : 'system'; } catch (e) { return 'system'; } };
  const themeApply = (m) => { const r = document.documentElement; if (m === 'light' || m === 'dark') r.setAttribute('data-theme', m); else r.removeAttribute('data-theme'); };
  UI.theme = {
    get: themeNow,
    set(m) { try { if (m === 'light' || m === 'dark') localStorage.setItem(THEME_KEY, m); else localStorage.removeItem(THEME_KEY); } catch (e) { /* 读写失败时只在本次页面生效 */ } themeApply(m); document.dispatchEvent(new CustomEvent('luz-theme', { detail: m })); },
    /** 当前实际生效的是 'light' 还是 'dark'（跟随系统时看系统外观） */
    resolved() { const m = themeNow(); return m === 'system' ? (matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light') : m; },
  };
  themeApply(themeNow());
  /** 三选一的外观控件（分段控件，radiogroup，方向键切换）；root 给了就放进去 */
  UI.appearance = function (root) {
    const box = h('div.seg', { role: 'radiogroup', 'aria-label': '外观' });
    const paint = () => box.querySelectorAll('button').forEach((b) => { const on = b.dataset.mode === themeNow(); b.setAttribute('aria-checked', String(on)); b.tabIndex = on ? 0 : -1; });
    THEMES.forEach(([m, label]) => box.append(h('button', { type: 'button', role: 'radio', 'data-mode': m, text: label, on: { click: () => { UI.theme.set(m); paint(); } } })));
    box.addEventListener('keydown', (e) => {
      const step = { ArrowRight: 1, ArrowDown: 1, ArrowLeft: -1, ArrowUp: -1 }[e.key]; if (!step) return;
      e.preventDefault(); const i = THEMES.findIndex(([m]) => m === themeNow()); UI.theme.set(THEMES[(i + step + THEMES.length) % THEMES.length][0]); paint(); box.querySelector('[aria-checked="true"]').focus();
    });
    document.addEventListener('luz-theme', paint); paint();
    if (root) root.append(box);
    return box;
  };
  /** 主色：只改色相与彩度，亮度台阶不变（对比度因此不会被改坏） */
  UI.brand = (hue, chroma) => { const s = document.documentElement.style; s.setProperty('--brand-h', hue); if (chroma != null) s.setProperty('--brand-c', chroma); };
  /** 视图过渡：支持就交叉淡化，不支持或减少动态时直接切换 */
  UI.go = (fn) => { if (document.startViewTransition && !UI.rm) return document.startViewTransition(fn).updateCallbackDone; fn(); return Promise.resolve(); };
  UI.sleep = (ms) => new Promise((r) => setTimeout(r, UI.rm ? Math.min(ms, 40) : ms));
  UI.play = (el, frames, o) => { const opt = Object.assign({ duration: 200, easing: 'cubic-bezier(0.2,0,0,1)', fill: 'backwards' }, o); if (UI.rm) { frames = frames.map((f) => { const g = { ...f }; delete g.transform; delete g.translate; delete g.scale; return g; }).filter((f) => 'opacity' in f); if (frames.length < 2) frames = [{ opacity: 1 }, { opacity: 1 }]; opt.duration = Math.min(opt.duration, 120); opt.delay = 0; } return el.animate(frames, opt); };
  /** 列表项依次进入：淡入加上移，相隔 30 毫秒，最多 8 项 */
  UI.stagger = (els) => els.forEach((el, i) => UI.play(el, [{ opacity: 0, transform: 'translateY(8px)' }, { opacity: 1, transform: 'none' }], { delay: Math.min(i, 8) * 30, easing: 'cubic-bezier(0,0,0,1)' }));

  /* ---------- 图标：24 栅格、描边 1.75 ---------- */
  const I = {
    home: 'M3 11l9-8 9 8M5 10v10h14V10', chart: 'M4 20V10M10 20V4M16 20v-7M22 20H2', bag: 'M6 7h12l1 13H5zM9 7a3 3 0 0 1 6 0', cart: 'M3 4h3l2.5 11h9L20 7H7M10 20h.01M17 20h.01', list: 'M8 6h13M8 12h13M8 18h13M3 6h.01M3 12h.01M3 18h.01',
    user: 'M12 12a4 4 0 1 0 0-8 4 4 0 0 0 0 8zM4 21c1-4 4-6 8-6s7 2 8 6', users: 'M9 11a3.5 3.5 0 1 0 0-7 3.5 3.5 0 0 0 0 7zM2 20c1-3.5 3.5-5 7-5s6 1.5 7 5M16 4a3.5 3.5 0 0 1 0 7M18 15c2 .5 3.5 2 4 5', card: 'M3 6h18v12H3zM3 10h18M7 15h4', wallet: 'M3 7h16a2 2 0 0 1 2 2v9H5a2 2 0 0 1-2-2zM3 7l12-3v3M16 13h2', tag: 'M3 12V4h8l10 10-8 8zM7.5 8h.01', bell: 'M6 9a6 6 0 1 1 12 0c0 6 2 7 2 7H4s2-1 2-7M10 20a2 2 0 0 0 4 0',
    shop: 'M4 9l1-5h14l1 5M4 9a3 3 0 0 0 5 2 3 3 0 0 0 6 0 3 3 0 0 0 5-2M5 12v8h14v-8', file: 'M7 3h8l4 4v14H7zM14 3v5h5', image: 'M4 5h16v14H4zM8 10a1.5 1.5 0 1 0 0-3 1.5 1.5 0 0 0 0 3zM20 16l-5-5-9 8', upload: 'M12 16V4M7 9l5-5 5 5M4 20h16', download: 'M12 4v12M7 11l5 5 5-5M4 20h16',
    search: 'M11 18a7 7 0 1 0 0-14 7 7 0 0 0 0 14zM20 20l-4-4', plus: 'M12 5v14M5 12h14', minus: 'M5 12h14', x: 'M6 6l12 12M18 6L6 18', check: 'M5 12.5l4.5 4.5L19 7', down: 'M6 9l6 6 6-6', up: 'M6 15l6-6 6 6', left: 'M15 6l-6 6 6 6', right: 'M9 6l6 6-6 6', more: 'M5 12h.01M12 12h.01M19 12h.01',
    edit: 'M4 20h4L19 9l-4-4L4 16zM13 7l4 4', trash: 'M5 7h14M10 7V4h4v3M7 7l1 13h8l1-13', copy: 'M9 9h11v11H9zM5 15V4h11', filter: 'M4 5h16l-6 8v6l-4-2v-4z', calendar: 'M4 6h16v14H4zM4 10h16M8 3v4M16 3v4', clock: 'M12 21a9 9 0 1 0 0-18 9 9 0 0 0 0 18zM12 7v5l3 2', map: 'M9 4l-6 2v14l6-2 6 2 6-2V4l-6 2zM9 4v14M15 6v14', pin: 'M12 21s-7-6-7-11a7 7 0 1 1 14 0c0 5-7 11-7 11zM12 12a2.5 2.5 0 1 0 0-5 2.5 2.5 0 0 0 0 5z',
    gear: 'M12 15a3 3 0 1 0 0-6 3 3 0 0 0 0 6zM19 12a7 7 0 0 0-.1-1.2l2-1.5-2-3.5-2.3 1a7 7 0 0 0-2-1.2L14 3h-4l-.6 2.6a7 7 0 0 0-2 1.2l-2.3-1-2 3.5 2 1.5A7 7 0 0 0 5 12c0 .4 0 .8.1 1.2l-2 1.5 2 3.5 2.3-1a7 7 0 0 0 2 1.2L10 21h4l.6-2.6a7 7 0 0 0 2-1.2l2.3 1 2-3.5-2-1.5c.1-.4.1-.8.1-1.2z', shield: 'M12 3l8 3v6c0 5-3.5 8-8 9-4.5-1-8-4-8-9V6z', lock: 'M6 11h12v9H6zM8 11V8a4 4 0 0 1 8 0v3', star: 'M12 3l2.7 5.6 6.1.9-4.4 4.3 1 6.1L12 17l-5.4 2.9 1-6.1L3.2 9.5l6.1-.9z', heart: 'M12 20s-8-5-8-11a4.5 4.5 0 0 1 8-2.5A4.5 4.5 0 0 1 20 9c0 6-8 11-8 11z',
    refresh: 'M20 12a8 8 0 1 1-2.3-5.7M20 4v5h-5', undo: 'M9 14L4 9l5-5M4 9h10a6 6 0 0 1 0 12h-3', send: 'M21 3L3 11l7 3 3 7zM10 14l11-11', scan: 'M4 8V5a1 1 0 0 1 1-1h3M16 4h3a1 1 0 0 1 1 1v3M20 16v3a1 1 0 0 1-1 1h-3M8 20H5a1 1 0 0 1-1-1v-3M4 12h16', gift: 'M4 11h16v9H4zM3 7h18v4H3zM12 7v13M12 7c-2 0-4-1-4-3s3-2 4 1c1-3 4-3 4-1s-2 3-4 3z', phone: 'M7 3h10v18H7zM11 18h2', menu: 'M4 7h16M4 12h16M4 17h16', info: 'M12 21a9 9 0 1 0 0-18 9 9 0 0 0 0 18zM12 11v6M12 7.5h.01', warn: 'M12 4l9 16H3zM12 10v4M12 17.5h.01', grid: 'M4 4h7v7H4zM13 4h7v7h-7zM4 13h7v7H4zM13 13h7v7h-7z', kanban: 'M4 4h5v16H4zM10 4h5v10h-5zM16 4h4v13h-4z', lanes: 'M3 6h10M3 12h18M3 18h13M8 4v16',
  };
  UI.icons = I;
  UI.icon = (name, cls) => { const s = document.createElementNS('http://www.w3.org/2000/svg', 'svg'); s.setAttribute('viewBox', '0 0 24 24'); s.setAttribute('class', 'icon' + (cls ? ' ' + cls : '')); s.setAttribute('aria-hidden', 'true'); const p = document.createElementNS('http://www.w3.org/2000/svg', 'path'); p.setAttribute('d', I[name] || I.info); s.append(p); return s; };

  /* ---------- 对话框：原生 <dialog>。UI.dialog 返回 Promise，点按钮得到按钮的 value，点遮罩、Esc、关闭键得到 null ---------- */
  let dlgN = 0;
  UI.dialog = function (o) {
    const tid = 'dlg-t' + ++dlgN;
    const dlg = h('dialog.dlg' + (o.size ? '.dlg--' + o.size : '') + (o.sheet ? '.sheet' : ''), { 'aria-labelledby': tid, closedby: o.dismiss === false ? 'none' : 'any' });
    const title = h('h2', { id: tid, text: o.title || '' });
    const close = o.dismiss === false ? null : h('button.btn.btn--ghost.btn--icon', { type: 'button', 'aria-label': '关闭', on: { click: () => dlg.close('') } }, UI.icon('x'));
    const body = h('div.dlg-body', {}, typeof o.body === 'string' ? h('p', { text: o.body }) : o.body);
    const foot = h('div.dlg-foot');
    (o.actions || []).forEach((a) => {
      const b = h('button.btn' + (a.kind ? '.btn--' + a.kind.split(' ').join('.btn--') : ''), { type: 'button', text: a.label, on: { click: async () => {
        if (b.disabled) return;
        if (a.on) { b.disabled = true; const t = b.textContent; b.replaceChildren(h('span.spin'), ' ' + t); let r; try { r = await a.on(body, dlg); } finally { b.disabled = false; b.textContent = t; } if (r === false) return; }
        dlg.close(a.value === undefined ? 'ok' : a.value);
      } } });
      foot.append(b);
    });
    dlg.append(h('div.dlg-head', {}, title, close), body, (o.actions || []).length ? foot : null);
    document.body.append(dlg);
    return new Promise((resolve) => {
      dlg.addEventListener('close', () => { const v = dlg.returnValue; setTimeout(() => dlg.remove(), 220); resolve(v === '' ? null : v); });
      if (o.dismiss === false) dlg.addEventListener('cancel', (e) => e.preventDefault());
      else dlg.addEventListener('click', (e) => { if (e.target === dlg) dlg.close(''); });   // 点遮罩关闭（closedby 不支持时的降级）
      dlg.showModal();
      const first = $('[autofocus],input,textarea,select', body) || $('.btn--primary', foot); first && first.focus({ preventScroll: true });
    });
  };
  UI.confirm = (text, o) => { o = o || {}; return UI.dialog({ title: o.title || '请确认', size: 'sm', body: text, actions: [{ label: '取消', value: null }, { label: o.ok || '确定', kind: o.danger ? 'danger.solid' : 'primary', value: 'ok' }] }).then((v) => v === 'ok'); };
  UI.sheet = (o) => UI.dialog(Object.assign({ sheet: true }, o));

  /* ---------- 提示：popover 顶层容器，1.5 秒消失，错误 3 秒 ---------- */
  UI.toast = function (text, o) {
    let box = $('#toasts');
    if (!box) { box = h('div.toasts#toasts', { popover: 'manual', role: 'status', 'aria-live': 'polite' }); document.body.append(box); }
    if (box.showPopover && !box.matches(':popover-open')) box.showPopover();
    const bad = o && o.kind === 'bad', t = h('div.toast' + (bad ? '.bad' : ''), {}, UI.icon(bad ? 'warn' : 'check', 'icon--sm'), h('span', { text }));
    box.append(t);
    setTimeout(() => { t.classList.add('out'); setTimeout(() => { t.remove(); if (!box.children.length && box.hidePopover) box.hidePopover(); }, 180); }, bad ? 3000 : 1500);
  };

  /* ---------- 弹出菜单：items = [{label, icon, danger, disabled, on}] 或 'hr'；disabled 为 true 或一句原因（显示在右侧并读出） ---------- */
  let popN = 0;
  UI.menu = function (trigger, items, o) {
    const id = 'menu-' + ++popN, name = '--anchor-' + popN;
    $$('[popover].menu').forEach((x) => { if (x._for && (x._for === trigger || !x._for.isConnected)) x.remove(); });   // 同一触发器重建、或触发器已被移出页面：旧菜单不留在 body 里
    const item = (it) => {
      if (it === 'hr') return h('hr');
      const off = !!it.disabled, why = typeof it.disabled === 'string' ? it.disabled : '';
      return h('button' + (it.danger ? '.danger' : ''), { type: 'button', role: 'menuitem', 'aria-disabled': off ? 'true' : null, on: { click: () => { if (off) return; m.hidePopover && m.hidePopover(); it.on && it.on(); } } }, it.icon ? UI.icon(it.icon, 'icon--sm') : null, it.label, why ? h('small', { text: why }) : null);
    };
    const m = h('div.menu', { popover: 'auto', id, role: 'menu' }, items.map(item));
    m._for = trigger;
    document.body.append(m);
    trigger.setAttribute('popovertarget', id); trigger.setAttribute('aria-haspopup', 'menu');
    if (CSS.supports && CSS.supports('position-anchor', '--a')) { trigger.style.setProperty('anchor-name', name); m.style.setProperty('position-anchor', name); m.dataset.anchored = ''; }
    else m.addEventListener('beforetoggle', (e) => { if (e.newState !== 'open') return; const r = trigger.getBoundingClientRect(); m.style.position = 'fixed'; m.style.top = Math.min(r.bottom + 4, innerHeight - 24) + 'px'; m.style.left = Math.max(8, Math.min(r.left, innerWidth - 220)) + 'px'; });
    return m;
  };

  /* ---------- 标签页：ARIA 角色，方向键，hidden 切换面板 ---------- */
  UI.tabs = function (list, onChange) {
    const tabs = $$('[role=tab]', list), panel = (t) => document.getElementById(t.getAttribute('aria-controls'));
    const show = (i, focus) => UI.go(() => { tabs.forEach((t, k) => { const on = k === i; t.setAttribute('aria-selected', String(on)); t.tabIndex = on ? 0 : -1; const p = panel(t); if (p) p.hidden = !on; }); if (focus) tabs[i].focus(); onChange && onChange(i, tabs[i]); });
    tabs.forEach((t, i) => t.addEventListener('click', () => show(i)));
    list.addEventListener('keydown', (e) => { const i = tabs.indexOf(document.activeElement); if (i < 0) return; const n = { ArrowRight: (i + 1) % tabs.length, ArrowLeft: (i - 1 + tabs.length) % tabs.length, Home: 0, End: tabs.length - 1 }[e.key]; if (n != null) { e.preventDefault(); show(n, true); } });
    return { show };
  };

  /** 数字从当前值数到目标值（800–900 毫秒）；减少动态时直接显示终值 */
  UI.count = function (el, to, o) {
    o = Object.assign({ dur: 900, dec: 0, prefix: '', suffix: '' }, o);
    const fmt = (v) => o.prefix + v.toLocaleString('zh-CN', { minimumFractionDigits: o.dec, maximumFractionDigits: o.dec }) + o.suffix;
    const from = Number(el.dataset.v || 0); el.dataset.v = String(to);
    if (UI.rm) { el.textContent = fmt(to); return; }
    const t0 = performance.now();
    const step = (t) => { const p = Math.min(1, (t - t0) / o.dur); el.textContent = fmt(from + (to - from) * (1 - Math.pow(1 - p, 3))); if (p < 1) requestAnimationFrame(step); };
    requestAnimationFrame(step);
  };
  UI.money = (cents, dec) => '¥' + (cents / 100).toLocaleString('zh-CN', { minimumFractionDigits: dec == null ? 2 : dec, maximumFractionDigits: dec == null ? 2 : dec });
  UI.skeleton = (rows, o) => h('div', { 'aria-busy': 'true', 'aria-label': '加载中', class: 'stack' }, Array.from({ length: rows || 3 }, (_, i) => h('div.skel', { style: { height: (o && o.h) || '18px', width: i % 3 === 2 ? '62%' : '100%' } })));

  /* ---------- 图表：手写 SVG。UI.spark / UI.line / UI.bars / UI.donut。每张图都带文字描述（aria-label），动画不超过 1.2 秒 ---------- */
  const NS = 'http://www.w3.org/2000/svg';
  const sv = (tag, a, ...k) => { const e = document.createElementNS(NS, tag); for (const [x, y] of Object.entries(a || {})) if (y != null) e.setAttribute(x, y); k.forEach((c) => c && e.append(c)); return e; };
  const niceStep = (x) => { const p = Math.pow(10, Math.floor(Math.log10(x || 1))), f = x / p; return (f <= 1 ? 1 : f <= 2 ? 2 : f <= 5 ? 5 : 10) * p; };
  const CH = ['var(--ch-1)', 'var(--ch-2)', 'var(--ch-3)', 'var(--ch-4)', 'var(--ch-5)', 'var(--ch-6)'];
  UI.chartColors = CH;
  function tip(el) { const t = h('div.chart-tip'); t.hidden = true; el.append(t); return { show(html, x, y) { t.innerHTML = html; t.hidden = false; t.style.left = Math.min(Math.max(0, x + 12), el.clientWidth - t.offsetWidth - 4) + 'px'; t.style.top = Math.max(0, y - 48) + 'px'; }, hide() { t.hidden = true; } }; }
  const rel = (e, el) => { const r = el.getBoundingClientRect(); return [e.clientX - r.left, e.clientY - r.top]; };
  UI.spark = (el, values, o) => {
    o = o || {}; el.replaceChildren(); const W = 160, H = 44, mx = Math.max(...values, 1), mn = Math.min(...values, 0), sp = mx - mn || 1;
    const pts = values.map((v, i) => [(i / Math.max(1, values.length - 1)) * W, H - 4 - ((v - mn) / sp) * (H - 10)]), d = pts.map((p, i) => (i ? 'L' : 'M') + p[0].toFixed(1) + ' ' + p[1].toFixed(1)).join('');
    const line = sv('path', { d, fill: 'none', stroke: o.color || 'var(--brand)', 'stroke-width': 2, 'stroke-linejoin': 'round', 'stroke-linecap': 'round', 'vector-effect': 'non-scaling-stroke' });
    const area = sv('path', { d: d + `L${W} ${H}L0 ${H}Z`, fill: o.color || 'var(--brand)', opacity: 0.1 });
    const s = sv('svg', { viewBox: `0 0 ${W} ${H}`, preserveAspectRatio: 'none', role: 'img', 'aria-label': o.label || '近期走势，最近一项 ' + values[values.length - 1] }, area, line); s.style.height = (o.height || 44) + 'px'; s.style.width = '100%'; el.append(s);
    const len = line.getTotalLength ? line.getTotalLength() : 0; if (len && !UI.rm) line.animate([{ strokeDasharray: len, strokeDashoffset: len }, { strokeDasharray: len, strokeDashoffset: 0 }], { duration: 800, easing: 'cubic-bezier(0,0,0,1)' });
  };
  /** UI.line(el, {labels, series:[{name, data, color}], height, unit, area, aria}) */
  UI.line = (el, o) => {
    const draw = () => {
      el.replaceChildren(); el.classList.add('chart');
      const W = Math.max(320, el.clientWidth), H = o.height || 260, pad = { l: 44, r: 12, t: 12, b: 28 }, n = o.labels.length, all = o.series.flatMap((s) => s.data), mx0 = Math.max(...all, 1), step = niceStep(mx0 / 4), mx = Math.ceil(mx0 / step) * step, iw = W - pad.l - pad.r, ih = H - pad.t - pad.b;
      const x = (i) => pad.l + (n === 1 ? iw / 2 : (i / (n - 1)) * iw), y = (v) => pad.t + ih - (v / mx) * ih;
      const svg = sv('svg', { viewBox: `0 0 ${W} ${H}`, role: 'img', 'aria-label': o.aria || '折线图', height: H }), g = sv('g', { class: 'grid' });
      for (let v = 0; v <= mx; v += step) { g.append(sv('line', { x1: pad.l, x2: W - pad.r, y1: y(v), y2: y(v) }), sv('text', { x: pad.l - 8, y: y(v) + 5, 'text-anchor': 'end' }, document.createTextNode(v.toLocaleString('zh-CN')))); }
      svg.append(g);
      const every = Math.max(1, Math.ceil(n / Math.floor(iw / 72))); o.labels.forEach((l, i) => { if (i % every === 0) svg.append(sv('text', { x: x(i), y: H - 6, 'text-anchor': 'middle' }, document.createTextNode(l))); });
      const lines = [];
      o.series.forEach((s, k) => { const c = s.color || CH[k % 6], d = s.data.map((v, i) => (i ? 'L' : 'M') + x(i).toFixed(1) + ' ' + y(v).toFixed(1)).join(''); if (o.area !== false && k === 0) svg.append(sv('path', { d: d + `L${x(n - 1)} ${pad.t + ih}L${x(0)} ${pad.t + ih}Z`, fill: c, opacity: 0.1 })); const p = sv('path', { d, fill: 'none', stroke: c, 'stroke-width': 2.5, 'stroke-linejoin': 'round', 'stroke-linecap': 'round' }); svg.append(p); lines.push(p); });
      const cur = sv('line', { y1: pad.t, y2: pad.t + ih, stroke: 'var(--line-strong)', opacity: 0 }); svg.append(cur);
      const t = tip(el), hit = sv('rect', { x: pad.l, y: pad.t, width: iw, height: ih, fill: 'transparent' });
      hit.addEventListener('pointermove', (e) => { const [px, py] = rel(e, el), i = Math.max(0, Math.min(n - 1, Math.round(((px - pad.l) / iw) * (n - 1)))); cur.setAttribute('x1', x(i)); cur.setAttribute('x2', x(i)); cur.setAttribute('opacity', 1); t.show('<b>' + o.labels[i] + '</b>' + o.series.map((s, k) => `<div><i style="display:inline-block;width:8px;height:8px;border-radius:2px;margin-right:6px;background:${s.color || CH[k % 6]}"></i>${s.name} ${s.data[i].toLocaleString('zh-CN')}${o.unit || ''}</div>`).join(''), px, py); });
      hit.addEventListener('pointerleave', () => { t.hide(); cur.setAttribute('opacity', 0); }); svg.append(hit);
      el.prepend(svg);
      if (!UI.rm) lines.forEach((p) => { const len = p.getTotalLength(); p.animate([{ strokeDasharray: len, strokeDashoffset: len }, { strokeDasharray: len, strokeDashoffset: 0 }], { duration: 900, easing: 'cubic-bezier(0,0,0,1)' }); });
    };
    draw(); let w = el.clientWidth; new ResizeObserver(() => { if (Math.abs(el.clientWidth - w) > 24) { w = el.clientWidth; draw(); } }).observe(el);
  };
  /** UI.bars(el, {labels, series:[{name, data, color}], stacked, height, unit, aria})——纵向柱；横向条用 .progress 或表格里的条形 */
  UI.bars = (el, o) => {
    const draw = () => {
      el.replaceChildren(); el.classList.add('chart');
      const W = Math.max(320, el.clientWidth), H = o.height || 260, pad = { l: 44, r: 8, t: 12, b: 28 }, n = o.labels.length, tot = o.labels.map((_, i) => o.series.reduce((a, s) => a + s.data[i], 0));
      const raw = Math.max(...(o.stacked ? tot : o.series.flatMap((s) => s.data)), 1), step = niceStep(raw / 4), mx = Math.ceil(raw / step) * step, iw = W - pad.l - pad.r, ih = H - pad.t - pad.b, bw = Math.max(4, Math.min(32, (iw / n) * 0.6));
      const svg = sv('svg', { viewBox: `0 0 ${W} ${H}`, role: 'img', 'aria-label': o.aria || '柱图', height: H }), g = sv('g', { class: 'grid' });
      for (let v = 0; v <= mx; v += step) g.append(sv('line', { x1: pad.l, x2: W - pad.r, y1: pad.t + ih - (v / mx) * ih, y2: pad.t + ih - (v / mx) * ih }), sv('text', { x: pad.l - 8, y: pad.t + ih - (v / mx) * ih + 5, 'text-anchor': 'end' }, document.createTextNode(v.toLocaleString('zh-CN'))));
      svg.append(g); const t = tip(el), rects = [], every = Math.max(1, Math.ceil(n / Math.floor(iw / 56)));
      o.labels.forEach((lab, i) => {
        const cx = pad.l + (iw / n) * (i + 0.5); let acc = 0;
        o.series.forEach((s, k) => { const v = s.data[i], hh = (v / mx) * ih, w = o.stacked ? bw : bw / o.series.length, xx = o.stacked ? cx - bw / 2 : cx - bw / 2 + k * w, yy = o.stacked ? pad.t + ih - acc - hh : pad.t + ih - hh; acc += hh; const r = sv('rect', { x: xx, y: yy, width: w, height: Math.max(0, hh), rx: 3, fill: s.color || CH[k % 6] }); rects.push(r); svg.append(r); });
        const hit = sv('rect', { x: cx - iw / n / 2, y: pad.t, width: iw / n, height: ih, fill: 'transparent' });
        hit.addEventListener('pointermove', (e) => { const [px, py] = rel(e, el); t.show('<b>' + lab + '</b>' + o.series.map((s, k) => `<div><i style="display:inline-block;width:8px;height:8px;border-radius:2px;margin-right:6px;background:${s.color || CH[k % 6]}"></i>${s.name} ${s.data[i].toLocaleString('zh-CN')}${o.unit || ''}</div>`).join(''), px, py); });
        hit.addEventListener('pointerleave', () => t.hide()); svg.append(hit);
        if (i % every === 0) svg.append(sv('text', { x: cx, y: H - 6, 'text-anchor': 'middle' }, document.createTextNode(lab)));
      });
      el.prepend(svg);
      if (!UI.rm) rects.forEach((r, i) => { r.style.transformBox = 'fill-box'; r.style.transformOrigin = '50% 100%'; r.animate([{ transform: 'scaleY(0)' }, { transform: 'scaleY(1)' }], { duration: 600, delay: Math.min(i, 30) * 12, easing: 'cubic-bezier(0,0,0,1)', fill: 'backwards' }); });
    };
    draw(); let w = el.clientWidth; new ResizeObserver(() => { if (Math.abs(el.clientWidth - w) > 24) { w = el.clientWidth; draw(); } }).observe(el);
  };
  /** UI.donut(el, [{name, value, color}], {size, center:{value, label}, aria}) */
  UI.donut = (el, items, o) => {
    o = o || {}; el.replaceChildren(); const size = o.size || 168, r = size / 2 - 14, c = 2 * Math.PI * r, tot = items.reduce((a, b) => a + b.value, 0) || 1;
    const svg = sv('svg', { width: size, height: size, viewBox: `0 0 ${size} ${size}`, role: 'img', 'aria-label': o.aria || '占比：' + items.map((x) => x.name + ' ' + Math.round((x.value / tot) * 1000) / 10 + '%').join('，') });
    svg.append(sv('circle', { cx: size / 2, cy: size / 2, r, fill: 'none', stroke: 'var(--surface-3)', 'stroke-width': 20 })); let off = 0; const arcs = [];
    items.forEach((it, i) => { const len = (it.value / tot) * c, a = sv('circle', { cx: size / 2, cy: size / 2, r, fill: 'none', stroke: it.color || CH[i % 6], 'stroke-width': 20, 'stroke-dasharray': `${Math.max(0, len - 2)} ${c}`, transform: `rotate(${-90 + (off / c) * 360} ${size / 2} ${size / 2})` }); off += len; svg.append(a); arcs.push([a, len - 2]); });
    const mid = h('div', { style: { position: 'absolute', inset: 0, display: 'grid', placeContent: 'center', textAlign: 'center' } }, h('b.num', { style: { fontSize: '22px' }, text: o.center ? o.center.value : '' }), h('span.muted', { text: o.center ? o.center.label : '' }));
    el.append(h('div', { style: { position: 'relative', width: size + 'px', height: size + 'px', margin: '0 auto' } }, svg, mid));
    if (!UI.rm) arcs.forEach(([a, len], i) => a.animate([{ strokeDasharray: `0 ${c}` }, { strokeDasharray: `${Math.max(0, len)} ${c}` }], { duration: 700, delay: i * 120, easing: 'cubic-bezier(0,0,0,1)' }));
  };


  /* ---------- 后台外壳：UI.app({root, brand, brandMark, nav:[{title, items:[{id, label, icon, badge, roles}]}], pages:{id: {title, render(ctx)}}, home, topRight}) ----------
     哈希路由（#/页面id），页面切换用视图过渡；ctx = {id, scene, role, net, go(id), refresh()}；render 返回节点或 Promise；场景 forbidden 由外壳统一处理，其余由页面处理 ---------- */
  UI.state = { net: 'ok', role: null, scene: {} };
  /** 模拟一次请求：正常稍等、弱网多等 1.1 秒、断网抛错；页面用它包住取数，演示三种网络 */
  UI.request = async (fn, ms) => { if (UI.state.net === 'off') { await UI.sleep(300); const e = new Error('offline'); e.offline = true; throw e; } await UI.sleep((ms || 220) + (UI.state.net === 'weak' ? 1100 : 0)); return fn ? fn() : undefined; };
  UI.app = function (o) {
    const root = o.root; root.replaceChildren();
    const nav = h('nav.app-nav', { 'aria-label': '主菜单' }), items = {};
    const paintNav = () => {
      nav.replaceChildren(h('div.app-brand', {}, o.brandMark || UI.icon('shop'), h('span', { text: o.brand }))); Object.keys(items).forEach((k) => delete items[k]);
      o.nav.map((g) => ({ ...g, items: g.items.filter((it) => !it.roles || !UI.state.role || it.roles.includes(UI.state.role)) })).filter((g) => g.items.length).forEach((g) => {
        if (g.title) nav.append(h('div.nav-title', { text: g.title }));
        g.items.forEach((it) => { const a = h('a.nav-item', { href: '#/' + it.id, 'data-id': it.id }, UI.icon(it.icon || 'grid'), h('span', { text: it.label }), it.badge ? h('span.badge-dot', { text: it.badge }) : null); items[it.id] = a; nav.append(a); });
      });
    };
    const crumb = h('div.crumb');
    const burger = h('button.btn.btn--ghost.btn--icon.app-burger', { type: 'button', 'aria-label': '打开菜单', on: { click: () => { app.dataset.nav = app.dataset.nav === 'open' ? '' : 'open'; } } }, UI.icon('menu'));
    const top = h('header.app-top', {}, burger, crumb, h('span.grow'), o.topRight || null);
    const view = h('div.app-view', { id: 'view', tabindex: '-1' }), main = h('div.app-main', {}, top, view);
    const scrim = h('div.app-scrim', { on: { click: () => { app.dataset.nav = ''; } } }), app = h('div.app', {}, nav, scrim, main);
    root.append(app); paintNav();
    let token = 0;
    const errorView = (route) => h('div.empty', { role: 'alert' }, UI.icon('warn', 'icon--lg'), h('h2', { text: '网络不太稳定，请稍后再试' }), h('button.btn', { type: 'button', text: '重试', on: { click: () => route() } }));
    const route = async () => {
      const id = (location.hash.replace(/^#\//, '') || o.home).split('?')[0], real = o.pages[id] ? id : o.home, page = o.pages[real], tok = ++token;
      const allowed = Object.keys(items).includes(real) || !Object.values(o.nav).length;
      app.dataset.nav = '';
      const ctx = { id: real, scene: UI.state.scene[real] || 'normal', role: UI.state.role, net: UI.state.net, go: (x) => { location.hash = '#/' + x; }, refresh: () => route() };
      await UI.go(() => {
        Object.values(items).forEach((a) => a.setAttribute('aria-current', a.dataset.id === real ? 'page' : 'false'));
        crumb.replaceChildren(h('span', { text: o.brand }), ' / ', h('b', { text: page.title }));
        document.title = page.title + ' - ' + o.brand;
        if (ctx.scene === 'forbidden' || !allowed) { view.replaceChildren(h('div.empty', { role: 'alert' }, UI.icon('lock', 'icon--lg'), h('h2', { text: '没有权限查看此内容' }), h('button.btn', { type: 'button', text: '回到首页', on: { click: () => ctx.go(o.home) } }))); return; }
        let node; try { node = page.render(ctx); } catch (e) { node = errorView(route); }
        const put = (n) => { view.replaceChildren(n); UI.stagger(UI.$$('.card, .band, .kcol, .table-wrap', view).slice(0, 8)); };
        if (node && node.then) { view.replaceChildren(h('div.page', {}, UI.skeleton(6))); node.then((n) => { if (tok === token) put(n); }).catch(() => { if (tok === token) view.replaceChildren(errorView(route)); }); }
        else put(node);
      });
      window.scrollTo(0, 0);
    };
    window.addEventListener('hashchange', route);
    route();
    return { route, repaintNav: paintNav, go: (id) => { location.hash = '#/' + id; } };
  };

  /* ---------- 演示控制（原型用）：UI.demo({home, pages:[{id,label,group}], scenes:(pageId)=>[{id,label}], roles:[{id,label}], onRole, onReset, layoutOf(pageId)→{layout, reason}, app}) ---------- */
  UI.demo = function (o) {
    const pop = h('div.demo', { popover: 'auto', id: 'demo-pop', 'aria-label': '演示控制' }), body = h('div.demo-body'), uid = 'dm' + Math.random().toString(36).slice(2, 6);
    const opt = (type, name, label, checked, on) => h('label.demo-opt', {}, h('input', { type, name, checked, on: { change: on } }), h('span', { text: label }));
    const group = (title, ...nodes) => h('div.demo-group', {}, h('h3', { text: title }), h('div.demo-opts', {}, nodes));
    const pageId = () => (location.hash.replace(/^#\//, '') || o.home).split('?')[0];
    const paint = () => {
      body.replaceChildren(); const pid = pageId(), meta = o.layoutOf && o.layoutOf(pid);
      if (meta) body.append(h('div.demo-group', {}, h('h3', { text: '当前页面的布局' }), h('p', {}, h('b', { text: meta.layout }), '：' + meta.reason)));
      const scenes = (o.scenes ? o.scenes(pid) : []).concat([{ id: 'normal', label: '正常' }, { id: 'loading', label: '加载中' }, { id: 'empty', label: '空' }, { id: 'error', label: '加载失败' }, { id: 'forbidden', label: '无权限' }]);
      const seen = new Set(), uniq = scenes.filter((s) => !seen.has(s.id) && seen.add(s.id));
      body.append(group('场景', ...uniq.map((s) => opt('radio', uid + 'sc', s.label, (UI.state.scene[pid] || 'normal') === s.id, () => { UI.state.scene[pid] = s.id; o.app.route(); }))));
      const byGroup = {}; o.pages.forEach((p) => (byGroup[p.group || '页面'] = byGroup[p.group || '页面'] || []).push(p));
      Object.entries(byGroup).forEach(([g, ps]) => body.append(group('页面直达：' + g, ...ps.map((p) => opt('radio', uid + 'pg', p.label, p.id === pid, () => o.app.go(p.id))))));
      body.append(group('网络', ...[['ok', '正常'], ['weak', '弱网'], ['off', '断网']].map(([v, l]) => opt('radio', uid + 'net', l, UI.state.net === v, () => { UI.state.net = v; o.app.route(); }))));
      body.append(group('外观', ...THEMES.map(([v, l]) => opt('radio', uid + 'th', l, UI.theme.get() === v, () => UI.theme.set(v)))));
      body.append(group('动效', opt('checkbox', uid + 'rm', '减少动态效果', UI.rmUser, (e) => UI.setReduced(e.target.checked))));
      if (o.roles) body.append(group('角色', ...o.roles.map((r) => opt('radio', uid + 'role', r.label, (UI.state.role || o.roles[0].id) === r.id, () => { UI.state.role = r.id; o.onRole && o.onRole(r.id); o.app.repaintNav(); o.app.route(); }))));
      body.append(group('演示数据', h('button.btn.btn--sm', { type: 'button', text: '重置演示数据', on: { click: () => { o.onReset && o.onReset(); o.app.route(); UI.toast('已重置演示数据'); } } })));
    };
    pop.append(h('div.dlg-head', {}, h('h2', { text: '演示控制' })), body); document.body.append(pop);
    pop.addEventListener('beforetoggle', (e) => { if (e.newState === 'open') paint(); });
    window.addEventListener('hashchange', () => pop.matches(':popover-open') && paint());
    document.body.append(h('button.btn.btn--primary.demo-fab', { type: 'button', popovertarget: 'demo-pop', 'aria-label': '演示控制' }, UI.icon('gear', 'icon--sm'), '演示'));
    return { paint };
  };

  /* ---------- 看板：UI.kanban(root, {columns:[{id, title, cards:[{id, title, meta, badge}]}], card(c)→节点, onMove(cardId, from, to)——返回 false 就把卡片放回原处，不能转的状态用它拒绝}) —— 拖放，也提供“移到…”菜单（键盘和触屏可用） ---------- */
  UI.kanban = function (root, o) {
    root.replaceChildren(); root.classList.add('l-kanban');
    const cols = {};
    const count = (id) => $('.count', cols[id].head).textContent = cols[id].body.children.length;
    const move = (cardEl, to, silent) => { const from = cardEl.closest('.kcol').dataset.id; if (from === to) return; const before = cardEl.nextElementSibling; const first = cardEl.getBoundingClientRect(); cols[to].body.append(cardEl); count(from); count(to); const last = cardEl.getBoundingClientRect(); if (!UI.rm) cardEl.animate([{ transform: `translate(${first.left - last.left}px, ${first.top - last.top}px)` }, { transform: 'none' }], { duration: 200, easing: 'cubic-bezier(0.2,0,0,1)' }); if (!silent && o.onMove) Promise.resolve(o.onMove(cardEl.dataset.id, from, to)).then((ok) => { if (ok === false) { cols[from].body.insertBefore(cardEl, before); count(from); count(to); } }); };
    o.columns.forEach((c) => {
      const head = h('div.kcol-head', {}, h('strong', { text: c.title }), h('span.count', { text: c.cards.length })), body = h('div', { class: 'stack', style: { gap: 'var(--s-3)' } });
      const col = h('section.kcol', { 'data-id': c.id, 'aria-label': c.title }, head, body); cols[c.id] = { head, body, col };
      col.addEventListener('dragover', (e) => { e.preventDefault(); col.classList.add('drop'); }); col.addEventListener('dragleave', (e) => { if (!col.contains(e.relatedTarget)) col.classList.remove('drop'); });
      col.addEventListener('drop', (e) => { e.preventDefault(); col.classList.remove('drop'); const el = $('.kcard.dragging'); if (el) move(el, c.id); });
      c.cards.forEach((cd) => {
        const el = h('article.kcard', { draggable: 'true', 'data-id': cd.id, tabindex: 0 }, o.card ? o.card(cd) : h('div', { text: cd.title }));
        const mv = h('button.btn.btn--ghost.btn--sm.btn--icon', { type: 'button', 'aria-label': '移到其他列' }, UI.icon('more', 'icon--sm')); el.append(mv);
        UI.menu(mv, o.columns.filter((x) => x.id !== c.id).map((x) => ({ label: '移到 ' + x.title, on: () => move(el, x.id) })).concat([]));
        el.addEventListener('dragstart', (e) => { el.classList.add('dragging'); e.dataTransfer.effectAllowed = 'move'; e.dataTransfer.setData('text/plain', cd.id); }); el.addEventListener('dragend', () => { el.classList.remove('dragging'); $$('.kcol.drop', root).forEach((x) => x.classList.remove('drop')); });
        body.append(el);
      });
      root.append(col);
    });
    return { move: (id, to) => { const el = $(`.kcard[data-id="${id}"]`, root); if (el) move(el, to, true); } };
  };

  /* ---------- 泳道：UI.lanes(root, {from:8, to:22, step:1, lanes:[{id, label, sub, events:[{id, from, to, title, kind}]}], now:10.5, free:true, onEvent(ev, lane)}) ——
     顶部时间刻度；事项横条按起止时间铺在格子里；时间重叠的事项自动分行并标冲突；空档用虚线块标出空闲；竖线是当前时间 ---------- */
  UI.lanes = function (root, o) {
    root.replaceChildren(); root.classList.add('l-lanes');
    const slots = Math.round((o.to - o.from) / (o.step || 1)), st = o.step || 1; root.style.setProperty('--slots', slots);
    const col = (t) => Math.round((t - o.from) / st) + 1, fmt = (t) => String(Math.floor(t)).padStart(2, '0') + ':' + (t % 1 ? '30' : '00');
    root.append(h('div.lanes-ruler', {}, h('div.corner'), h('div.ticks', {}, Array.from({ length: slots }, (_, i) => h('span', { text: fmt(o.from + i * st) })))));
    o.lanes.forEach((ln) => {
      const evs = ln.events.slice().sort((a, b) => a.from - b.from), rows = [];
      evs.forEach((e) => { let r = rows.findIndex((end) => end <= e.from); if (r < 0) { r = rows.length; rows.push(0); } rows[r] = e.to; e._row = r + 1; });
      evs.forEach((e) => { e._conflict = evs.some((x) => x !== e && x.from < e.to && x.to > e.from); });
      const track = h('div.lane-track', { style: { gridAutoRows: '40px' } });
      evs.forEach((e) => track.append(h('div.lane-event' + (e._conflict ? '.conflict' : e.kind === 'warn' ? '.warn' : ''), { style: { '--from': col(e.from), '--to': col(e.to), '--row': e._row }, title: `${e.title} ${fmt(e.from)}–${fmt(e.to)}${e._conflict ? '（时间冲突）' : ''}`, tabindex: 0, role: 'button', on: { click: () => o.onEvent && o.onEvent(e, ln) } }, e.title)));
      if (o.free !== false && rows.length) { const covered = []; evs.forEach((e) => covered.push([e.from, e.to])); covered.sort((a, b) => a[0] - b[0]); let t = o.from; const gaps = []; covered.forEach(([f, to]) => { if (f - t >= 2 * st) gaps.push([t, f]); t = Math.max(t, to); }); if (o.to - t >= 2 * st) gaps.push([t, o.to]); gaps.forEach(([f, to]) => track.append(h('div.lane-free', { style: { '--from': col(f), '--to': col(to), '--row': 1 }, text: '空闲 ' + (to - f) + ' 小时' }))); }
      else if (o.free !== false) track.append(h('div.lane-free', { style: { '--from': 1, '--to': slots + 1, '--row': 1 }, text: '全天空闲' }));
      track.style.minHeight = 40 * Math.max(1, rows.length) + 24 + 'px';
      root.append(h('div.lane-label', {}, ln.avatar || null, h('div', {}, h('strong', { text: ln.label }), ln.sub ? h('div.muted', { text: ln.sub }) : null)), track);
    });
    if (o.now != null && o.now >= o.from && o.now <= o.to) { const now = h('div.lanes-now', { 'data-label': '现在 ' + fmt(o.now), 'aria-hidden': 'true' }); root.append(now); const place = () => { const first = $('.lane-track', root) || $('.ticks', root); if (!first) return; const tr = $('.ticks', root).getBoundingClientRect(), rr = root.getBoundingClientRect(); now.style.left = (tr.left - rr.left + root.scrollLeft + ((o.now - o.from) / (o.to - o.from)) * tr.width) + 'px'; now.style.height = root.scrollHeight + 'px'; }; requestAnimationFrame(place); new ResizeObserver(place).observe(root); }
  };
})();
