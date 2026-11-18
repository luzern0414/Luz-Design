<!doctype html>
<html lang="zh-CN" data-ic-base="../../kit/assets/icons" data-icons="mono" data-bg="glow">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>海报模板</title>
<link rel="stylesheet" href="../../kit/tokens.css">
<link rel="stylesheet" href="../../kit/ui.css">
<link rel="stylesheet" href="../../kit/kit.css">
<style>
  /* 海报墙：按用途分类，缩放预览紧挨着排成瀑布流，点开在新页打开原文件 */
  body { margin: 0; background: var(--bg); color: var(--ink); font-family: var(--font); }
  .lib { padding: 0 var(--s-5) var(--s-8); }
  .bar { position: sticky; top: 0; z-index: 5; display: flex; align-items: center; gap: var(--s-3); margin: 0 calc(var(--s-5) * -1); padding: var(--s-3) var(--s-5); background: color-mix(in srgb, var(--bg) 94%, transparent); backdrop-filter: blur(8px); border-bottom: 1px solid var(--line); }
  .pills { display: flex; flex: 1; gap: var(--s-2); overflow-x: auto; scrollbar-width: none; }
  .pills::-webkit-scrollbar { display: none; }
  .pill { flex: none; display: inline-flex; align-items: center; gap: var(--s-2); min-height: 34px; padding: 0 var(--s-3); border-radius: var(--r-full); background: var(--surface); box-shadow: inset 0 0 0 1px var(--line); font-size: var(--fs-sm); font-weight: 500; color: var(--ink-2); }
  .pill small { font-size: var(--fs-xs); font-weight: 600; color: var(--ink-3); }
  .pill:hover { background: var(--zone); }
  .pill[aria-pressed="true"] { background: var(--ink); color: var(--surface); box-shadow: none; }
  .pill[aria-pressed="true"] small { color: color-mix(in srgb, var(--surface) 70%, transparent); }
  .bar .search { flex: none; width: 240px; max-width: 34%; }
  .wall { column-width: 300px; column-gap: var(--s-3); margin-top: var(--s-4); }
  .item { display: grid; gap: var(--s-2); break-inside: avoid; margin: 0 0 var(--s-3); padding: var(--s-2); background: var(--surface); border-radius: var(--r-lg); box-shadow: inset 0 0 0 1px var(--line); }
  .item[hidden] { display: none; }
  .pv { position: relative; display: block; overflow: hidden; border-radius: var(--r-md); background: var(--zone); }
  .pv iframe { position: absolute; left: 0; top: 0; border: 0; transform-origin: top left; pointer-events: none; background: var(--bg); }
  .meta { display: flex; align-items: center; justify-content: space-between; gap: var(--s-2); padding: 0 var(--s-1) var(--s-1); }
  .meta h2 { margin: 0; font-size: var(--fs-md); font-weight: 600; line-height: var(--lh-tight); }
  .meta p { margin: 2px 0 0; font-size: var(--fs-xs); color: var(--ink-3); }
  .copy { flex: none; min-height: 26px; padding: 0 var(--s-2); border-radius: var(--r-sm); background: var(--zone); color: var(--action-press); font-size: var(--fs-xs); font-weight: 600; font-variant-numeric: tabular-nums; }
  .copy:hover { background: var(--action-edge); }
  .none { display: none; margin-top: var(--s-8); }
  .none.on { display: grid; }
</style>
</head>
<body>
<div class="lib">
  <div class="bar"><nav class="pills" id="pills" aria-label="按用途筛选"></nav><label class="search"><img src="../../kit/assets/line/search.webp" alt=""><input id="q" type="search" placeholder="搜索编号或名称" aria-label="搜索编号或名称"></label></div>
  <main class="wall" id="wall"></main>
  <div class="empty none" id="none"><img data-ic="vase" src="../../kit/assets/icons/flat/vase.webp" alt=""><span>没有匹配的海报</span></div>
</div>
<script src="../../kit/ui.js"></script>
<script>
  (function () {
    const ITEMS = @ITEMS@;
    const $ = (s, r = document) => r.querySelector(s), $$ = (s, r = document) => [...r.querySelectorAll(s)];
    const state = { use: 'all', q: '' };
    const uses = [...new Set(ITEMS.map(i => i.use))];
    $('#pills').innerHTML = `<button class="pill" data-use="all" aria-pressed="true">全部 <small>${ITEMS.length}</small></button>` + uses.map(u => `<button class="pill" data-use="${u}" aria-pressed="false">${u} <small>${ITEMS.filter(i => i.use === u).length}</small></button>`).join('');
    $('#wall').innerHTML = ITEMS.map(i => `<article class="item" data-id="${i.id}" data-use="${i.use}" data-text="${(i.id + i.name + i.use).toLowerCase()}">
      <a class="pv" href="${i.file}" target="_blank" rel="noopener" aria-label="打开${i.name}" style="aspect-ratio:${i.w} / ${i.h}" data-w="${i.w}"><iframe src="${i.file}?export=1" width="${i.w}" height="${i.h}" loading="lazy" tabindex="-1" aria-hidden="true"></iframe></a>
      <div class="meta"><div><h2>${i.name}</h2><p>${i.size}</p></div><button class="copy" data-copy="${i.id}" aria-label="复制编号 ${i.id}">${i.id}</button></div></article>`).join('');
    function scale() { $$('.pv').forEach(p => { const k = p.clientWidth / +p.dataset.w; $('iframe', p).style.transform = 'scale(' + k + ')'; }); }
    function draw() {
      const q = state.q.trim().toLowerCase(); let n = 0;
      $$('.item').forEach(el => { const on = (state.use === 'all' || el.dataset.use === state.use) && (!q || el.dataset.text.includes(q)); el.hidden = !on; if (on) n++; });
      $('#none').classList.toggle('on', n === 0); scale();
    }
    $('#pills').addEventListener('click', e => { const b = e.target.closest('.pill'); if (!b) return; $$('.pill').forEach(x => x.setAttribute('aria-pressed', String(x === b))); state.use = b.dataset.use; draw(); });
    $('#q').addEventListener('input', e => { state.q = e.target.value; draw(); });
    document.addEventListener('click', async e => { const b = e.target.closest('[data-copy]'); if (!b) return; try { await navigator.clipboard.writeText(b.dataset.copy); Lz.toast('已复制 ' + b.dataset.copy, 'success'); } catch (err) { Lz.toast('复制失败', 'danger'); } });
    // 主题、背景、图标由外壳统一控制：把消息转给每张海报
    addEventListener('message', e => { if (e.data && e.data.lz === 'skin') $$('.pv iframe').forEach(f => { try { f.contentWindow.postMessage(e.data, '*'); } catch (err) { /* 还在加载 */ } }); });
    $$('.pv iframe').forEach(f => f.addEventListener('load', () => { try { f.contentWindow.postMessage({ lz: 'skin', theme: document.documentElement.dataset.theme, bg: document.documentElement.dataset.bg, icons: document.documentElement.dataset.icons, color: document.documentElement.style.getPropertyValue('--action') && /^custom/.test(document.documentElement.dataset.theme || '') ? document.documentElement.style.getPropertyValue('--action') : undefined }, '*'); } catch (err) { /* 同上 */ } }));
    addEventListener('resize', scale); draw();
  })();
</script>
</body>
</html>
