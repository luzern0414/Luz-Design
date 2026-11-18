<!doctype html>
<html lang="zh-CN" data-ic-base="../../kit/assets/icons" data-icons="mono" data-bg="glow">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>@TITLE@</title>
<link rel="icon" href="../../kit/assets/icons/flat/bouquet.webp">
<link rel="stylesheet" href="../../kit/tokens.css">
<link rel="stylesheet" href="../../kit/ui.css">
<link rel="stylesheet" href="../../kit/kit.css">
<style>
  /* 打包外壳：顶部 tab 与外观控制，下面一个满屏面板；不属于任何一端的产品界面 */
  html, body { height: 100%; }
  body { margin: 0; display: grid; grid-template-rows: 60px minmax(0, 1fr); overflow: hidden; background: var(--bg); color: var(--ink); font-family: var(--font); }
  .hd { display: flex; align-items: center; gap: var(--s-5); padding: 0 var(--s-6); background: var(--surface); border-bottom: 1px solid var(--line); z-index: 20; }
  .hd__brand { display: flex; align-items: center; gap: var(--s-3); flex: none; }
  .hd__brand img { width: 32px; height: 32px; object-fit: contain; }
  .hd__brand h1 { font-size: var(--fs-lg); font-weight: 700; line-height: 1; white-space: nowrap; }
  .tabs[hidden] { display: none; }
  .tabs { display: inline-flex; gap: 2px; padding: 3px; border-radius: var(--r-full); background: var(--zone); flex: none; }
  .tabs__item { min-height: 34px; padding: 0 var(--s-5); border-radius: var(--r-full); font-size: var(--fs-md); font-weight: 500; color: var(--ink-2); transition: background var(--dur-quick) var(--ease-out), color var(--dur-quick) var(--ease-out); }
  .tabs__item[aria-selected="true"] { background: var(--action); color: var(--surface); font-weight: 600; }
  [data-ui-workbench] .tabs { border-radius: 12px; }
  [data-ui-workbench] :is(.tabs__item, .tool, .iconseg, .iconseg button) { border-radius: 8px; }
  .tools { display: flex; align-items: center; gap: var(--s-2); margin-left: auto; flex-wrap: nowrap; }
  .tool { display: inline-flex; align-items: center; gap: var(--s-2); min-height: 36px; padding: 0 var(--s-3); border-radius: var(--r-full); background: var(--zone); font-size: var(--fs-sm); font-weight: 500; color: var(--ink-2); white-space: nowrap; }
  .tool:hover, .pop[data-open="true"] > .tool { background: var(--action-edge); }
  .tool .dot { width: 14px; height: 14px; border-radius: 50%; background: var(--action); box-shadow: 0 0 0 2px var(--surface), 0 0 0 3px var(--line-strong); }
  .tool .fx { width: 18px; height: 14px; border-radius: 4px; background: var(--action-edge); }
  .pop { position: relative; }
  .pop__panel { position: absolute; top: calc(100% + 8px); right: 0; display: none; padding: var(--s-4); background: var(--surface); border-radius: var(--r-lg); box-shadow: var(--elev-3); border: 1px solid var(--line); z-index: 30; }
  .pop[data-open="true"] > .pop__panel { display: block; }
  .pop__title { font-size: var(--fs-sm); font-weight: 600; color: var(--ink-2); margin-bottom: var(--s-3); }
  .swatches { display: grid; grid-template-columns: repeat(8, 28px); gap: var(--s-2); }
  .swatch { width: 28px; height: 28px; border-radius: 50%; background: var(--c); box-shadow: inset 0 0 0 2px var(--surface), 0 0 0 1px var(--line-strong); transition: transform var(--dur-quick) var(--ease-out); }
  .swatch:hover { transform: scale(1.12); }
  .swatch[aria-pressed="true"] { box-shadow: inset 0 0 0 3px var(--surface), 0 0 0 2px var(--c); transform: scale(1.1); }
  .custom { display: flex; align-items: center; gap: var(--s-3); margin-top: var(--s-4); padding-top: var(--s-3); border-top: 1px solid var(--line); font-size: var(--fs-sm); color: var(--ink-2); }
  .custom input[type="color"] { width: 40px; height: 28px; padding: 0; border: 0; border-radius: var(--r-sm); background: none; cursor: pointer; }
  .custom code { font-size: var(--fs-xs); color: var(--ink-3); }
  .fxlist { display: grid; grid-template-columns: repeat(3, 92px); gap: var(--s-2); }
  .fxitem { display: grid; gap: var(--s-1); padding: var(--s-1); border-radius: var(--r-md); font-size: var(--fs-xs); color: var(--ink-2); text-align: center; }
  .fxitem__tile { height: 44px; border-radius: var(--r-sm); background-color: var(--action-tint); box-shadow: inset 0 0 0 1px var(--line); }
  .fxitem[aria-pressed="true"] { background: var(--action-tint); box-shadow: inset 0 0 0 1.5px var(--action); color: var(--action-press); font-weight: 600; }
  .iconseg { display: inline-flex; padding: 3px; gap: 2px; border-radius: var(--r-full); background: var(--zone); }
  .iconseg button { min-height: 30px; padding: 0 var(--s-3); border-radius: var(--r-full); font-size: var(--fs-sm); color: var(--ink-2); }
  .iconseg button[aria-pressed="true"] { background: var(--surface); color: var(--action-press); font-weight: 600; box-shadow: var(--elev-1); }
  .home { font-size: var(--fs-sm); color: var(--ink-2); padding: 0 var(--s-2); white-space: nowrap; }

  main { position: relative; min-height: 0; }
  .panel { position: absolute; inset: 0; visibility: hidden; pointer-events: none; }
  .panel[data-on="true"] { visibility: visible; pointer-events: auto; }
  .host { position: absolute; inset: 0; }
  .host iframe { display: block; width: 100%; height: 100%; border: 0; background: var(--bg); }

  /* 整页模板：页面列表 | 预览 | 本页逻辑 */
  .wb { display: grid; grid-template-columns: 208px minmax(0, 1fr) 328px; height: 100%; }
  .wb__side { overflow-y: auto; padding: var(--s-4) var(--s-2) var(--s-4) var(--s-4); }
  .wb__side h2 { margin: 0 var(--s-2) var(--s-2); font-size: var(--fs-xs); font-weight: 600; color: var(--ink-3); }
  .nav { display: grid; gap: 2px; }
  .nav__item { display: flex; align-items: center; justify-content: space-between; gap: var(--s-2); min-height: 40px; padding: 0 var(--s-3); border-radius: var(--r-md); text-align: left; font-size: var(--fs-md); color: var(--ink-2); }
  .nav__item:hover { background: var(--zone); }
  .nav__item[aria-current="true"] { background: var(--action-tint); color: var(--action-press); font-weight: 600; box-shadow: inset 0 0 0 1px var(--action-edge); }
  .nav__item small { font-size: var(--fs-xs); color: var(--ink-3); font-weight: 400; }
  .wb__stage { position: relative; display: grid; grid-template: minmax(0, 1fr) / minmax(0, 1fr); place-items: center; margin: var(--s-3) 0; border-radius: var(--r-xl); overflow: hidden; background: color-mix(in srgb, var(--action) 4%, var(--bg)); box-shadow: inset 0 0 0 1px var(--line); }
  .frame { position: relative; flex: none; overflow: hidden; background: var(--surface); box-shadow: var(--elev-3); }
  .frame iframe { display: block; width: 100%; height: 100%; border: 0; background: var(--bg); }
  .frame--phone { width: 410px; height: 864px; border-radius: 42px; border: 10px solid var(--ink); }
  .frame--desktop { width: 1440px; height: 900px; border-radius: var(--r-lg); border: 1px solid var(--line-strong); }
  .wb__info { overflow-y: auto; padding: var(--s-4) var(--s-5) var(--s-5) var(--s-3); }
  .wb__info h2 { margin: 0 0 var(--s-3); font-size: var(--fs-xl); font-weight: 700; line-height: var(--lh-tight); }
  .wb__info h3 { margin: var(--s-5) 0 var(--s-2); font-size: var(--fs-sm); font-weight: 600; color: var(--ink-2); }
  .kv { display: grid; gap: var(--s-3); padding: var(--s-4); margin: 0; background: var(--surface); border-radius: var(--r-lg); box-shadow: inset 0 0 0 1px var(--line); }
  .kv > div { display: grid; grid-template-columns: 52px minmax(0, 1fr); gap: var(--s-3); align-items: baseline; }
  .kv dt { font-size: var(--fs-sm); color: var(--ink-3); }
  .kv dd { margin: 0; font-size: var(--fs-md); line-height: 1.55; }
  .ids { display: grid; padding: var(--s-1); background: var(--surface); border-radius: var(--r-lg); box-shadow: inset 0 0 0 1px var(--line); }
  .ids button { display: flex; align-items: center; justify-content: space-between; gap: var(--s-2); min-height: 38px; padding: 0 var(--s-3); border-radius: var(--r-sm); text-align: left; font-size: var(--fs-md); }
  .ids button:hover { background: var(--zone); }
  .ids code { font-size: var(--fs-xs); font-weight: 600; font-variant-numeric: tabular-nums; color: var(--action-press); background: var(--zone); padding: 2px 8px; border-radius: var(--r-sm); }
  @media (max-width: 1180px) { .wb { grid-template-columns: 188px minmax(0, 1fr); } .wb__info { display: none; } }
  @media (max-width: 860px) { .hd { gap: var(--s-3); padding: 0 var(--s-3); } .hd__brand h1, .home, .tool span { display: none; } .wb { grid-template-columns: minmax(0, 1fr); } .wb__side { display: none; } }
</style>
</head>
<body>
<header class="hd bgfx">
  <div class="hd__brand"><img data-ic="bouquet" src="../../kit/assets/icons/flat/bouquet.webp" alt=""><h1>@TITLE@</h1></div>
  <nav class="tabs" id="tabs" aria-label="模板分类">@TABS@</nav>
  <div class="tools">
    <div class="pop" id="pop-theme"><button class="tool" aria-haspopup="true" aria-expanded="false"><i class="dot"></i><span>主题色</span></button>
      <div class="pop__panel"><p class="pop__title">主题色 24 种，或自选</p><div class="swatches" id="swatches"></div>
        <label class="custom"><span>自选</span><input type="color" id="custom" value="#a75f6d" aria-label="自选主题色"><code id="customhex">#A75F6D</code></label></div></div>
    <div class="pop" id="pop-bg"><button class="tool" aria-haspopup="true" aria-expanded="false"><i class="fx"></i><span>背景</span></button>
      <div class="pop__panel"><p class="pop__title">背景效果</p><div class="fxlist" id="fxlist"></div></div></div>
    <div class="iconseg" id="iconseg" role="group" aria-label="图标形态"><button data-icons="mono" aria-pressed="true">单色</button><button data-icons="flat" aria-pressed="false">彩色</button><button data-icons="3d" aria-pressed="false">立体</button><button data-icons="real" aria-pressed="false">真实</button></div>
    <a class="home" href="../../index.html">模板库首页</a>
  </div>
</header>
<main>
@PANELS@
</main>
@SOURCES@
<script src="../../kit/ui.js"></script>
<script>
(function () {
  const CFG = @CONFIG@;
  const $ = (s, r = document) => r.querySelector(s), $$ = (s, r = document) => [...r.querySelectorAll(s)];
  const state = { theme: CFG.theme, color: null, bg: CFG.background || 'glow', icons: 'mono' };
  const frames = new Set();
  const store = { get(k) { try { return localStorage.getItem('lz-bundle-' + k); } catch (e) { return null; } }, set(k, v) { try { localStorage.setItem('lz-bundle-' + k, v); } catch (e) { /* 浏览器不让存时只是不记住 */ } } };
  const q = new URLSearchParams(location.search);
  const skinKeys = ['theme', 'bg', 'icons', 'color'];
  const skinKey = k => CFG.workbench ? 'frontend-' + k : k;
  const oldDefaults = { theme: 'rose', bg: 'glow', icons: 'mono', color: '' };
  skinKeys.forEach(k => {
    const legacy = store.get(k);
    const saved = store.get(skinKey(k)) ?? (legacy === oldDefaults[k] ? null : legacy);
    const value = q.get(k) || saved;
    if (value) state[k] = value;
  });
  if (state.color) state.theme = null;

  function send(win) { try { win.postMessage({ lz: 'skin', theme: state.theme || undefined, color: state.color || undefined, bg: state.bg, icons: state.icons }, '*'); } catch (e) { /* 框还没准备好 */ } }
  function apply() {
    Lz.skin({ theme: state.theme || undefined, color: state.color || undefined, bg: state.bg, icons: state.icons });
    frames.forEach(f => f.contentWindow && send(f.contentWindow));
    $$('#swatches .swatch').forEach(b => b.setAttribute('aria-pressed', String(!state.color && b.dataset.theme === state.theme)));
    $$('#fxlist .fxitem').forEach(b => b.setAttribute('aria-pressed', String(b.dataset.bg === state.bg)));
    $$('#iconseg button').forEach(b => b.setAttribute('aria-pressed', String(b.dataset.icons === state.icons)));
    skinKeys.forEach(k => store.set(skinKey(k), state[k] || ''));
  }
  function mount(host, html, cls) {
    const f = document.createElement('iframe'); f.setAttribute('aria-label', host.dataset.label || '预览');
    f.addEventListener('load', () => { frames.add(f); send(f.contentWindow); });
    f.srcdoc = html; host.appendChild(f); return f;
  }
  const source = id => ($('#src-' + id).textContent || '').replace(/<\\\/script/g, '</script');

  // 外观控制
  $('#swatches').innerHTML = CFG.presets.map(p => `<button class="swatch" style="--c:${p.action}" data-theme="${p.id}" aria-pressed="false" aria-label="${p.name}" data-tip="${p.name}"></button>`).join('');
  $('#fxlist').innerHTML = CFG.effects.map(e => `<button class="fxitem" data-bg="${e.id}" aria-pressed="false"><span class="fxitem__tile bgfx bgfx--${e.id}" ${e.id === 'none' ? '' : ''}></span>${e.name}</button>`).join('');
  $('#swatches').addEventListener('click', e => { const b = e.target.closest('.swatch'); if (!b) return; state.theme = b.dataset.theme; state.color = null; apply(); });
  $('#custom').addEventListener('input', e => { state.color = e.target.value; state.theme = null; $('#customhex').textContent = e.target.value.toUpperCase(); apply(); });
  $('#fxlist').addEventListener('click', e => { const b = e.target.closest('.fxitem'); if (!b) return; state.bg = b.dataset.bg; apply(); });
  $('#iconseg').addEventListener('click', e => { const b = e.target.closest('button'); if (!b) return; state.icons = b.dataset.icons; apply(); });
  $$('.pop').forEach(p => p.firstElementChild.addEventListener('click', e => { e.stopPropagation(); const open = p.dataset.open !== 'true'; $$('.pop').forEach(x => { x.dataset.open = 'false'; x.firstElementChild.setAttribute('aria-expanded', 'false'); }); p.dataset.open = String(open); p.firstElementChild.setAttribute('aria-expanded', String(open)); }));
  document.addEventListener('click', e => { if (!e.target.closest('.pop__panel')) $$('.pop').forEach(x => { x.dataset.open = 'false'; x.firstElementChild.setAttribute('aria-expanded', 'false'); }); });
  document.addEventListener('keydown', e => { if (e.key === 'Escape') $$('.pop').forEach(x => { x.dataset.open = 'false'; }); });

  // tab
  const mounted = {};
  function openTab(id) {
    $$('#tabs .tabs__item').forEach(b => b.setAttribute('aria-selected', String(b.dataset.tab === id)));
    $$('.panel').forEach(p => { p.dataset.on = String(p.id === 'panel-' + id); });
    if (!mounted[id]) { mounted[id] = true; const host = $('#panel-' + id + ' .host'); if (host) mount(host, source(host.dataset.src)); else if (id === CFG.workbench) openPage(page); }
    store.set('tab-' + CFG.key, id); fit();
  }
  $('#tabs').addEventListener('click', e => { const b = e.target.closest('.tabs__item'); if (b) openTab(b.dataset.tab); });

  // 整页模板工作台
  let page = CFG.pages && CFG.pages[0] ? CFG.pages[0].id : null, pageFrame = null;
  const frame = $('#frame');
  function fit() {
    const stage = $('.wb__stage'); if (!stage || !frame || !stage.clientWidth) return;
    if (CFG.device === 'phone') {
      const k = Math.min(1, (stage.clientHeight - 28) / 864, (stage.clientWidth - 28) / 410);
      frame.style.transform = 'scale(' + k + ')';
    } else { // 桌面：宽按 1440 缩放，高度随舞台补满，页面按真实窗口比例显示
      const k = Math.min(1, (stage.clientWidth - 28) / 1440);
      frame.style.height = Math.floor((stage.clientHeight - 28) / k) + 'px'; frame.style.transform = 'scale(' + k + ')';
    }
    frame.style.transformOrigin = 'center center';
  }
  function esc(s) { return String(s).replace(/[&<>"]/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c])); }
  function openPage(id) {
    page = id; const p = CFG.pages.find(x => x.id === id);
    $$('#nav .nav__item').forEach(b => b.setAttribute('aria-current', String(b.dataset.page === id)));
    if (pageFrame) { frames.delete(pageFrame); pageFrame.remove(); }
    pageFrame = mount(frame, source('page-' + id));
    $('#info').innerHTML = `<h2>${esc(p.name)}</h2><h3>本页逻辑</h3><dl class="kv">${p.logic.map(([k, v]) => `<div><dt>${k}</dt><dd>${esc(v)}</dd></div>`).join('')}</dl><h3>本页组件编号</h3><div class="ids">${p.ids.map(c => `<button data-copy="${c.id}"><span>${esc(c.name)}</span><code>${c.id}</code></button>`).join('')}</div>`;
    fit();
  }
  if (frame) {
    $('#nav').innerHTML = '<h2>完整页面</h2>' + CFG.pages.map(p => `<button class="nav__item" data-page="${p.id}" aria-current="false"><span>${esc(p.name)}</span><small>${p.ids.length} 块</small></button>`).join('');
    $('#nav').addEventListener('click', e => { const b = e.target.closest('[data-page]'); if (b) openPage(b.dataset.page); });
    $('#info').addEventListener('click', async e => { const b = e.target.closest('[data-copy]'); if (!b) return; try { await navigator.clipboard.writeText(b.dataset.copy); Lz.toast('已复制 ' + b.dataset.copy, 'success'); } catch (err) { Lz.toast('复制失败', 'danger'); } });
    addEventListener('message', e => { if (e.data && e.data.lz === 'goto' && CFG.pages.some(p => p.id === e.data.page)) { openTab(CFG.workbench); openPage(e.data.page); } });
    addEventListener('resize', fit);
  }
  // 海报墙：缩放预览，点击在新页打开原文件
  $$('.wall').forEach(w => { const f = $('iframe', w); });

  apply();
  openTab(store.get('tab-' + CFG.key) && CFG.tabs.includes(store.get('tab-' + CFG.key)) ? store.get('tab-' + CFG.key) : CFG.tabs[0]);
})();
</script>
</body>
</html>
